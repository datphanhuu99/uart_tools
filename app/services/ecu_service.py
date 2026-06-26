import struct
import logging
import threading
from typing import Optional, Callable, Dict
from app.serial_comm.connection import SerialConnection
from app.serial_comm.protocol import PacketCodec, ECUCommand, Packet
from app.models.config_model import ECUConfig, SerialConfig

logger = logging.getLogger("ecu_app")

class ECUService:
    """
    Dịch vụ điều phối kết nối và xử lý nghiệp vụ cấu hình ECU.
    """
    def __init__(self):
        self.connection = SerialConnection()
        
        # Các callback đăng ký từ phía UI để cập nhật trạng thái
        self._on_status_updated: Optional[Callable[[Dict[str, any]], None]] = None
        self._on_connection_changed: Optional[Callable[[bool], None]] = None
        
        # Đồng bộ hóa luồng (chờ phản hồi ACK/NACK từ ECU)
        self._ack_event = threading.Event()
        self._last_received_cmd: Optional[int] = None
        self._ecu_config_received: Optional[ECUConfig] = None

    def register_callbacks(self, on_status_updated: Callable[[Dict[str, any]], None], 
                           on_connection_changed: Callable[[bool], None]) -> None:
        """Đăng ký các callback để truyền thông tin lên lớp UI."""
        self._on_status_updated = on_status_updated
        self._on_connection_changed = on_connection_changed

    def connect(self, serial_cfg: SerialConfig) -> bool:
        """Thực hiện kết nối tới thiết bị."""
        try:
            self.connection.connect(
                port=serial_cfg.port,
                baudrate=serial_cfg.baudrate,
                timeout=serial_cfg.timeout,
                parity=serial_cfg.parity,
                stopbits=serial_cfg.stopbits,
                bytesize=serial_cfg.bytesize
            )
            # Khởi động luồng đọc nền
            self.connection.start_reading(
                packet_callback=self._handle_incoming_packet,
                error_callback=self._handle_serial_error
            )
            if self._on_connection_changed:
                self._on_connection_changed(True)
            return True
        except Exception as e:
            logger.error(f"Kết nối thất bại tại cổng {serial_cfg.port}: {e}")
            return False

    def disconnect(self) -> None:
        """Ngắt kết nối thiết bị."""
        self.connection.disconnect()
        if self._on_connection_changed:
            self._on_connection_changed(False)

    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối."""
        return self.connection.is_connected

    def send_config(self, config: ECUConfig) -> bool:
        """
        Nạp cấu hình mới xuống ECU (Gửi lệnh SET_CONFIG và chờ ACK/NACK).
        """
        if not self.is_connected():
            logger.error("Không thể nạp cấu hình: Chưa kết nối cổng Serial.")
            return False

        # Chuyển đổi chế độ hoạt động sang mã số nguyên (byte)
        mode_mapping = {"normal": 0, "eco": 1, "sport": 2, "diagnostic": 3}
        mode_val = mode_mapping.get(config.mode, 0)

        # Đóng gói payload nhị phân:
        # B (Device ID - 1B) + B (Mode - 1B) + H (Update Interval - 2B) + 4x f (Temp High, Temp Low, Volt High, Volt Low - 4B mỗi biến)
        payload = struct.pack(
            "<BBHffff",
            config.device_id,
            mode_val,
            config.update_interval_ms,
            config.temp_threshold_high,
            config.temp_threshold_low,
            config.voltage_threshold_high,
            config.voltage_threshold_low
        )

        packet = PacketCodec.encode(ECUCommand.SET_CONFIG, payload)
        
        # Reset event đồng bộ trước khi gửi
        self._ack_event.clear()
        self._last_received_cmd = None

        logger.info(f"Đang gửi cấu hình xuống ECU: Device ID={config.device_id}, Mode={config.mode}")
        if not self.connection.send(packet):
            return False

        # Chờ phản hồi trong vòng 2.0 giây
        success = self._ack_event.wait(timeout=2.0)
        if not success:
            logger.warning("Quá thời gian chờ phản hồi (Timeout) từ ECU khi gửi cấu hình.")
            return False

        if self._last_received_cmd == ECUCommand.ACK:
            logger.info("ECU phản hồi ACK: Ghi cấu hình thành công.")
            return True
        elif self._last_received_cmd == ECUCommand.NACK:
            logger.error("ECU phản hồi NACK: Cấu hình bị từ chối.")
            return False

        return False

    def request_config(self) -> Optional[ECUConfig]:
        """
        Yêu cầu đọc cấu hình hiện tại từ ECU (Lệnh GET_CONFIG).
        """
        if not self.is_connected():
            return None

        packet = PacketCodec.encode(ECUCommand.GET_CONFIG)
        self._ack_event.clear()
        self._last_received_cmd = None
        self._ecu_config_received = None

        logger.info("Yêu cầu đọc cấu hình hiện tại của ECU.")
        if not self.connection.send(packet):
            return None

        success = self._ack_event.wait(timeout=2.0)
        if not success or self._ecu_config_received is None:
            logger.warning("Không nhận được phản hồi thông số cấu hình từ ECU.")
            return None

        return self._ecu_config_received

    def reboot_ecu(self) -> bool:
        """Yêu cầu ECU khởi động lại."""
        if not self.is_connected():
            return False

        packet = PacketCodec.encode(ECUCommand.REBOOT_ECU)
        self._ack_event.clear()
        self._last_received_cmd = None

        logger.info("Yêu cầu khởi động lại ECU.")
        if not self.connection.send(packet):
            return False

        success = self._ack_event.wait(timeout=2.0)
        return success and self._last_received_cmd == ECUCommand.ACK

    def _handle_incoming_packet(self, packet: Packet) -> None:
        """
        Xử lý các gói tin nhận được từ luồng đọc nền.
        """
        cmd_id = packet.command_id
        
        # 1. Nhận phản hồi ACK / NACK
        if cmd_id in (ECUCommand.ACK, ECUCommand.NACK):
            self._last_received_cmd = cmd_id
            self._ack_event.set()
            return

        # 2. Nhận cấu hình từ lệnh GET_CONFIG
        if cmd_id == ECUCommand.GET_CONFIG:
            try:
                # Giải mã payload
                if len(packet.payload) >= 20:
                    device_id, mode_val, update_interval_ms, temp_high, temp_low, volt_high, volt_low = struct.unpack(
                        "<BBHffff", packet.payload[:20]
                    )
                    
                    # Ánh xạ ngược chế độ mode
                    mode_mapping_rev = {0: "normal", 1: "eco", 2: "sport", 3: "diagnostic"}
                    mode_str = mode_mapping_rev.get(mode_val, "normal")

                    self._ecu_config_received = ECUConfig(
                        device_id=device_id,
                        mode=mode_str,
                        update_interval_ms=update_interval_ms,
                        temp_threshold_high=temp_high,
                        temp_threshold_low=temp_low,
                        voltage_threshold_high=volt_high,
                        voltage_threshold_low=volt_low
                    )
                    
                    self._last_received_cmd = cmd_id
                    self._ack_event.set()
            except Exception as e:
                logger.error(f"Lỗi phân tích payload cấu hình nhận từ ECU: {e}")
            return

        # 3. Nhận dữ liệu trạng thái thời gian thực (Lệnh READ_STATUS hoặc bản tin chu kỳ tự động từ ECU)
        if cmd_id == ECUCommand.READ_STATUS:
            try:
                # Thống nhất payload trạng thái thực:
                # f (Nhiệt độ hiện tại) + f (Điện áp hiện tại) + I (Thời gian chạy của ECU - uptime giây) + B (Mã lỗi lỗi - error_code)
                if len(packet.payload) >= 13:
                    temperature, voltage, uptime, error_code = struct.unpack("<ffIB", packet.payload[:13])
                    
                    status_data = {
                        "temperature": round(temperature, 2),
                        "voltage": round(voltage, 2),
                        "uptime_seconds": uptime,
                        "error_code": error_code
                    }
                    
                    if self._on_status_updated:
                        self._on_status_updated(status_data)
            except Exception as e:
                logger.error(f"Lỗi phân tích trạng thái thời gian thực từ ECU: {e}")
            return

    def _handle_serial_error(self, error: Exception) -> None:
        """Xử lý khi xảy ra lỗi kết nối phần cứng."""
        logger.error(f"Lỗi phần cứng Serial: {error}. Ngắt kết nối tự động.")
        self.disconnect()
