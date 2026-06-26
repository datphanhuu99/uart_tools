import serial
import serial.tools.list_ports
import threading
import logging
from typing import List, Callable, Optional
from app.serial_comm.protocol import PacketCodec, Packet

logger = logging.getLogger("ecu_app")

class SerialConnection:
    """
    Quản lý kết nối Serial/UART, thực hiện đọc ghi dữ liệu trên các luồng độc lập.
    """
    def __init__(self):
        self.serial_port: Optional[serial.Serial] = None
        self._read_thread: Optional[threading.Thread] = None
        self._is_reading = False
        self._packet_callback: Optional[Callable[[Packet], None]] = None
        self._error_callback: Optional[Callable[[Exception], None]] = None
        self._lock = threading.Lock()

    @staticmethod
    def list_available_ports() -> List[str]:
        """Trả về danh sách các cổng Serial/COM khả dụng trên hệ thống."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    @property
    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối."""
        with self._lock:
            return self.serial_port is not None and self.serial_port.is_open

    def connect(self, port: str, baudrate: int, timeout: float = 1.0, 
                parity: str = "N", stopbits: float = 1, bytesize: int = 8) -> None:
        """
        Kết nối tới cổng Serial được chỉ định.
        """
        with self._lock:
            if self.serial_port and self.serial_port.is_open:
                raise ConnectionError("Cổng serial đã được kết nối trước đó.")

            # Ánh xạ cấu hình stopbits của pyserial
            stopbits_map = {
                1: serial.STOPBITS_ONE,
                1.5: serial.STOPBITS_ONE_POINT_FIVE,
                2: serial.STOPBITS_TWO
            }
            # Ánh xạ cấu hình bytesize
            bytesize_map = {
                5: serial.FIVEBITS,
                6: serial.SIXBITS,
                7: serial.SEVENBITS,
                8: serial.EIGHTBITS
            }
            # Ánh xạ parity
            parity_map = {
                "N": serial.PARITY_NONE,
                "E": serial.PARITY_EVEN,
                "O": serial.PARITY_ODD
            }

            logger.info(f"Đang mở cổng kết nối {port} với baudrate={baudrate}")
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                parity=parity_map.get(parity, serial.PARITY_NONE),
                stopbits=stopbits_map.get(stopbits, serial.STOPBITS_ONE),
                bytesize=bytesize_map.get(bytesize, serial.EIGHTBITS)
            )

    def disconnect(self) -> None:
        """Đóng kết nối và dừng luồng đọc dữ liệu."""
        self.stop_reading()
        
        with self._lock:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
                logger.info("Đã đóng kết nối Serial thành công.")
            self.serial_port = None

    def send(self, data: bytes) -> bool:
        """Gửi mảng byte qua cổng Serial."""
        with self._lock:
            if not self.serial_port or not self.serial_port.is_open:
                logger.error("Không thể gửi dữ liệu: Thiết bị chưa được kết nối.")
                return False
            try:
                self.serial_port.write(data)
                self.serial_port.flush()
                return True
            except Exception as e:
                logger.error(f"Lỗi khi gửi dữ liệu qua Serial: {e}")
                self._handle_error(e)
                return False

    def start_reading(self, packet_callback: Callable[[Packet], None], 
                      error_callback: Optional[Callable[[Exception], None]] = None) -> None:
        """
        Bắt đầu luồng đọc dữ liệu nền từ cổng Serial.
        """
        with self._lock:
            if not self.serial_port or not self.serial_port.is_open:
                raise ConnectionError("Không thể đọc dữ liệu: Thiết bị chưa được kết nối.")
            
            if self._is_reading:
                return

            self._is_reading = True
            self._packet_callback = packet_callback
            self._error_callback = error_callback
            
            self._read_thread = threading.Thread(
                target=self._read_loop, 
                name="SerialReaderThread", 
                daemon=True
            )
            self._read_thread.start()
            logger.info("Đã khởi chạy luồng đọc dữ liệu serial.")

    def stop_reading(self) -> None:
        """Dừng luồng đọc dữ liệu."""
        self._is_reading = False
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=2.0)
            logger.info("Đã dừng luồng đọc dữ liệu serial.")
        self._read_thread = None

    def _read_loop(self) -> None:
        """Hàm vòng lặp chạy ngầm để liên tục nhận dữ liệu và phân tích gói tin."""
        buffer = bytearray()
        
        while self._is_reading:
            # Lấy đối tượng cổng serial cục bộ để đảm bảo an toàn luồng
            with self._lock:
                port = self.serial_port
                if not port or not port.is_open:
                    break

            try:
                # Đọc byte khả dụng từ serial port (non-blocking hoặc blocking tùy timeout)
                data = port.read(max(1, port.in_waiting))
                if data:
                    buffer.extend(data)
                    
                    # Giải mã liên tục các gói tin có trong buffer
                    while len(buffer) > 0:
                        packet, bytes_processed = PacketCodec.decode_stream(buffer)
                        if bytes_processed > 0:
                            # Cắt phần dữ liệu đã được xử lý khỏi buffer
                            del buffer[:bytes_processed]
                            
                            if packet and self._packet_callback:
                                try:
                                    self._packet_callback(packet)
                                except Exception as cb_err:
                                    logger.error(f"Lỗi xảy ra tại hàm callback xử lý gói tin: {cb_err}")
                        else:
                            # Chưa đủ dữ liệu để giải mã, thoát vòng lặp nhỏ chờ nhận thêm byte
                            break
            except Exception as e:
                logger.error(f"Lỗi xảy ra trong luồng đọc dữ liệu: {e}")
                self._handle_error(e)
                break

        self._is_reading = False

    def _handle_error(self, error: Exception) -> None:
        """Thông báo lỗi kết nối hoặc đọc ghi về tầng nghiệp vụ/giao diện."""
        if self._error_callback:
            try:
                self._error_callback(error)
            except Exception as cb_err:
                logger.error(f"Lỗi khi thực thi hàm báo lỗi callback: {cb_err}")
