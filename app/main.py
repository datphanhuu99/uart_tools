import os
import sys
import logging
import threading
from typing import Dict, Any, Optional

import customtkinter as ctk
from tkinter import messagebox, filedialog

# Thêm thư mục gốc vào python path nếu cần thiết
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.config_model import ECUConfig, SerialConfig, AppConfig
from app.storage.file_manager import FileManager
from app.services.ecu_service import ECUService
from app.serial_comm import SerialConnection
from app.utils.logger import setup_logger

# Đường dẫn file cấu hình mặc định
VALUES_FILE = "values.yml"

# Khởi tạo logger
logger = setup_logger("ecu_app", log_level="INFO")

class TextBoxLogHandler(logging.Handler):
    """
    Handler ghi log tùy chỉnh để hiển thị log lên CTkTextbox một cách an toàn luồng.
    """
    def __init__(self, textbox: ctk.CTkTextbox):
        super().__init__()
        self.textbox = textbox
        self.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s", "%H:%M:%S"))

    def emit(self, record):
        log_entry = self.format(record) + "\n"
        # Đưa yêu cầu cập nhật giao diện vào hàng đợi chính của Tkinter để tránh xung đột luồng
        self.textbox.after(0, self._safe_append, log_entry, record.levelname)

    def _safe_append(self, message: str, levelname: str):
        try:
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message)
            self.textbox.configure(state="disabled")
            self.textbox.see("end")
            
            # Giới hạn số dòng log hiển thị tối đa để tránh tràn bộ nhớ
            lines = self.textbox.get("1.0", "end").split("\n")
            if len(lines) > 500:
                self.textbox.configure(state="normal")
                self.textbox.delete("1.0", "2.0")
                self.textbox.configure(state="disabled")
        except Exception:
            pass


class ECUConfigApp(ctk.CTk):
    """
    Lớp giao diện ứng dụng chính chạy bằng CustomTkinter.
    """
    def __init__(self):
        super().__init__()

        # 1. Nạp cấu hình từ values.yml
        self.values_path = VALUES_FILE
        if not os.path.exists(self.values_path):
            # Fallback nếu chạy từ các thư mục khác
            self.values_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), VALUES_FILE)
            
        self.serial_cfg, self.app_cfg, self.ecu_cfg = FileManager.load_app_settings(self.values_path)

        # 2. Khởi tạo dịch vụ ECU
        self.ecu_service = ECUService()

        # 3. Thiết lập giao diện tổng quan
        ctk.set_appearance_mode(self.app_cfg.theme)
        ctk.set_default_color_theme(self.app_cfg.color_theme)
        
        self._update_window_title()
        self.geometry("1100x700")
        self.minsize(950, 600)

        # Cấu hình grid hệ thống: 2 cột chính
        self.grid_columnconfigure(0, weight=1, minsize=420)
        self.grid_columnconfigure(1, weight=1, minsize=450)
        self.grid_rowconfigure(0, weight=1)

        # Khởi tạo các biến lưu trữ giao diện
        self.port_var = ctk.StringVar(value=self.serial_cfg.port)
        self.baud_var = ctk.StringVar(value=str(self.serial_cfg.baudrate))
        
        # Biến cấu hình ECU
        self.dev_id_var = ctk.StringVar(value=str(self.ecu_cfg.device_id))
        self.mode_var = ctk.StringVar(value=self.ecu_cfg.mode)
        self.interval_var = ctk.StringVar(value=str(self.ecu_cfg.update_interval_ms))
        self.temp_high_var = ctk.StringVar(value=str(self.ecu_cfg.temp_threshold_high))
        self.temp_low_var = ctk.StringVar(value=str(self.ecu_cfg.temp_threshold_low))
        self.volt_high_var = ctk.StringVar(value=str(self.ecu_cfg.voltage_threshold_high))
        self.volt_low_var = ctk.StringVar(value=str(self.ecu_cfg.voltage_threshold_low))

        self._build_ui()

        # Đăng ký callbacks dịch vụ
        self.ecu_service.register_callbacks(
            on_status_updated=self._on_ecu_status_updated,
            on_connection_changed=self._on_connection_changed
        )

        # Khởi tạo chuyển hướng log lên UI
        self.log_handler = TextBoxLogHandler(self.log_textbox)
        logger.addHandler(self.log_handler)
        
        # Quét cổng serial ban đầu
        self.refresh_ports()
        logger.info("Giao diện ứng dụng đã khởi động thành công.")

    def _build_ui(self):
        # ==========================================
        # CỘT TRÁI: Bảng Kết Nối & Cấu Hình ECU
        # ==========================================
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(1, weight=1)

        # 1. Khung Kết Nối (Connection Panel)
        conn_frame = ctk.CTkFrame(left_frame)
        conn_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        conn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        conn_title = ctk.CTkLabel(conn_frame, text="KẾT NỐI SERIAL / UART", font=ctk.CTkFont(size=14, weight="bold"))
        conn_title.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(conn_frame, text="Cổng COM:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.port_menu = ctk.CTkOptionMenu(conn_frame, variable=self.port_var, values=[self.serial_cfg.port])
        self.port_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        btn_refresh = ctk.CTkButton(conn_frame, text="Quét lại", width=80, command=self.refresh_ports)
        btn_refresh.grid(row=1, column=2, padx=10, pady=5, sticky="e")

        ctk.CTkLabel(conn_frame, text="Baudrate:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.baud_menu = ctk.CTkOptionMenu(
            conn_frame, variable=self.baud_var, 
            values=["9600", "19200", "38400", "57600", "115200"]
        )
        self.baud_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Trạng thái kết nối dạng đèn LED
        self.status_led = ctk.CTkLabel(conn_frame, text="● Chưa kết nối", text_color="#d9534f", font=ctk.CTkFont(weight="bold"))
        self.status_led.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="w")

        self.btn_connect = ctk.CTkButton(conn_frame, text="Kết Nối", fg_color="#28a745", hover_color="#218838", command=self.toggle_connection)
        self.btn_connect.grid(row=3, column=2, padx=10, pady=15, sticky="e")

        # 2. Khung Cấu Hình ECU (Configuration Panel)
        config_frame = ctk.CTkScrollableFrame(left_frame, label_text="THÔNG SỐ CẤU HÌNH ECU")
        config_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        config_frame.grid_columnconfigure(1, weight=1)

        # Device ID
        ctk.CTkLabel(config_frame, text="Device ID (1-255):").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.entry_dev_id = ctk.CTkEntry(config_frame, textvariable=self.dev_id_var)
        self.entry_dev_id.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        # Mode
        ctk.CTkLabel(config_frame, text="Chế độ hoạt động:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(
            config_frame, variable=self.mode_var,
            values=["normal", "eco", "sport", "diagnostic"]
        )
        self.mode_menu.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Update Interval
        ctk.CTkLabel(config_frame, text="Chu kỳ gửi trạng thái (ms):").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.entry_interval = ctk.CTkEntry(config_frame, textvariable=self.interval_var)
        self.entry_interval.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # Temp High
        ctk.CTkLabel(config_frame, text="Ngưỡng nhiệt độ cao (°C):").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.entry_temp_high = ctk.CTkEntry(config_frame, textvariable=self.temp_high_var)
        self.entry_temp_high.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        # Temp Low
        ctk.CTkLabel(config_frame, text="Ngưỡng nhiệt độ thấp (°C):").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.entry_temp_low = ctk.CTkEntry(config_frame, textvariable=self.temp_low_var)
        self.entry_temp_low.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        # Volt High
        ctk.CTkLabel(config_frame, text="Ngưỡng điện áp cao (V):").grid(row=5, column=0, padx=10, pady=8, sticky="w")
        self.entry_volt_high = ctk.CTkEntry(config_frame, textvariable=self.volt_high_var)
        self.entry_volt_high.grid(row=5, column=1, padx=10, pady=8, sticky="ew")

        # Volt Low
        ctk.CTkLabel(config_frame, text="Ngưỡng điện áp thấp (V):").grid(row=6, column=0, padx=10, pady=8, sticky="w")
        self.entry_volt_low = ctk.CTkEntry(config_frame, textvariable=self.volt_low_var)
        self.entry_volt_low.grid(row=6, column=1, padx=10, pady=8, sticky="ew")

        # Nút bấm hành động
        btn_action_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        btn_action_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        btn_action_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_write_config = ctk.CTkButton(
            btn_action_frame, text="Nạp Cấu Hình", 
            fg_color="#007bff", hover_color="#0069d9", 
            command=self.write_config_to_device
        )
        self.btn_write_config.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_reboot = ctk.CTkButton(
            btn_action_frame, text="Khởi Động Lại ECU", 
            fg_color="#dc3545", hover_color="#c82333", 
            command=self.reboot_ecu_device
        )
        self.btn_reboot.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Quản lý file cục bộ
        file_mgmt_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        file_mgmt_frame.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        file_mgmt_frame.grid_columnconfigure((0, 1), weight=1)

        btn_save = ctk.CTkButton(file_mgmt_frame, text="Lưu Cấu Hình", command=self.save_current_settings)
        btn_save.grid(row=0, column=0, padx=5, pady=2, sticky="ew")

        btn_save_as = ctk.CTkButton(file_mgmt_frame, text="Lưu Mới...", fg_color="#17a2b8", hover_color="#138496", command=self.save_as_settings)
        btn_save_as.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        btn_import_file = ctk.CTkButton(file_mgmt_frame, text="Nạp từ File...", fg_color="#6c757d", hover_color="#5a6268", command=self.import_config_file)
        btn_import_file.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="ew")


        # ==========================================
        # CỘT PHẢI: Trạng Thái ECU & Log Hệ Thống
        # ==========================================
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        # 1. Khung Trạng Thái Thời Gian Thực (Realtime Monitoring)
        monitor_frame = ctk.CTkFrame(right_frame)
        monitor_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        monitor_frame.grid_columnconfigure((0, 1), weight=1)

        monitor_title = ctk.CTkLabel(monitor_frame, text="GIÁM SÁT THỜI GIAN THỰC (ECU)", font=ctk.CTkFont(size=14, weight="bold"))
        monitor_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Nhiệt độ hiện tại
        temp_subframe = ctk.CTkFrame(monitor_frame, fg_color="#1f2d3d")
        temp_subframe.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(temp_subframe, text="Nhiệt độ", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=5)
        self.lbl_temp_val = ctk.CTkLabel(temp_subframe, text="-- °C", font=ctk.CTkFont(size=24, weight="bold"), text_color="#17a2b8")
        self.lbl_temp_val.pack(anchor="w", padx=10, pady=5)

        # Điện áp hiện tại
        volt_subframe = ctk.CTkFrame(monitor_frame, fg_color="#1f2d3d")
        volt_subframe.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(volt_subframe, text="Điện áp", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=5)
        self.lbl_volt_val = ctk.CTkLabel(volt_subframe, text="-- V", font=ctk.CTkFont(size=24, weight="bold"), text_color="#28a745")
        self.lbl_volt_val.pack(anchor="w", padx=10, pady=5)

        # Uptime & Mã lỗi
        ctk.CTkLabel(monitor_frame, text="Thời gian chạy (Uptime):").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.lbl_uptime = ctk.CTkLabel(monitor_frame, text="-- giây", font=ctk.CTkFont(weight="bold"))
        self.lbl_uptime.grid(row=2, column=1, padx=15, pady=5, sticky="e")

        ctk.CTkLabel(monitor_frame, text="Mã trạng thái/Lỗi:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.lbl_err_code = ctk.CTkLabel(monitor_frame, text="Không xác định", text_color="#ffc107", font=ctk.CTkFont(weight="bold"))
        self.lbl_err_code.grid(row=3, column=1, padx=15, pady=5, sticky="e")

        # 2. Khung Log Hệ Thống (Console Log Output)
        log_frame = ctk.CTkFrame(right_frame)
        log_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        log_title = ctk.CTkLabel(log_frame, text="LOG HOẠT ĐỘNG HỆ THỐNG", font=ctk.CTkFont(size=12, weight="bold"))
        log_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.log_textbox = ctk.CTkTextbox(log_frame, state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        btn_clear_log = ctk.CTkButton(log_frame, text="Xóa Log", width=80, fg_color="#6c757d", hover_color="#5a6268", command=self.clear_log_box)
        btn_clear_log.grid(row=0, column=0, padx=10, pady=5, sticky="e")

    # ==========================================
    # Logic Nghiệp Vụ và Hàm Sự Kiện
    # ==========================================

    def refresh_ports(self):
        """Quét và làm mới danh sách cổng serial."""
        ports = SerialConnection.list_available_ports()
        if ports:
            self.port_menu.configure(values=ports)
            if self.port_var.get() not in ports:
                self.port_var.set(ports[0])
            logger.info(f"Đã tìm thấy các cổng: {ports}")
        else:
            self.port_menu.configure(values=["Không tìm thấy"])
            self.port_var.set("Không tìm thấy")
            logger.warning("Không tìm thấy cổng Serial/COM nào khả dụng.")

    def toggle_connection(self):
        """Kết nối hoặc ngắt kết nối cổng serial."""
        if self.ecu_service.is_connected():
            # Ngắt kết nối
            logger.info("Đang thực hiện ngắt kết nối...")
            self.ecu_service.disconnect()
        else:
            # Thực hiện kết nối
            port = self.port_var.get()
            if port == "Không tìm thấy" or not port:
                messagebox.showerror("Lỗi cổng Serial", "Vui lòng quét lại và chọn cổng kết nối hợp lệ.")
                return

            try:
                baud = int(self.baud_var.get())
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Baudrate phải là một số nguyên.")
                return

            # Cập nhật serial config
            self.serial_cfg.port = port
            self.serial_cfg.baudrate = baud

            # Tiến hành kết nối
            success = self.ecu_service.connect(self.serial_cfg)
            if success:
                logger.info(f"Đã kết nối thành công tới cổng {port} ở tốc độ {baud}.")
            else:
                messagebox.showerror("Lỗi kết nối", f"Không thể mở cổng {port}. Hãy kiểm tra cáp hoặc cổng đang bị tiến trình khác chiếm dụng.")

    def _on_connection_changed(self, is_connected: bool):
        """Callback xử lý thay đổi trạng thái kết nối."""
        if is_connected:
            self.status_led.configure(text="● Đã kết nối", text_color="#28a745")
            self.btn_connect.configure(text="Ngắt Kết Nối", fg_color="#dc3545", hover_color="#c82333")
            # Mở khóa các nút điều khiển
            self._set_ui_controls_state("normal")
        else:
            self.status_led.configure(text="● Chưa kết nối", text_color="#d9534f")
            self.btn_connect.configure(text="Kết Nối", fg_color="#28a745", hover_color="#218838")
            # Khóa các nút điều khiển
            self._set_ui_controls_state("disabled")
            # Reset thông số giám sát
            self.lbl_temp_val.configure(text="-- °C")
            self.lbl_volt_val.configure(text="-- V")
            self.lbl_uptime.configure(text="-- giây")
            self.lbl_err_code.configure(text="Không xác định", text_color="#ffc107")

    def _set_ui_controls_state(self, state: str):
        """Bật/tắt trạng thái các nút bấm tương tác thiết bị."""
        self.btn_write_config.configure(state=state)
        self.btn_reboot.configure(state=state)

    def write_config_to_device(self):
        """Gửi cấu hình xuống ECU."""
        try:
            cfg = ECUConfig(
                device_id=int(self.dev_id_var.get()),
                mode=self.mode_var.get(),
                update_interval_ms=int(self.interval_var.get()),
                temp_threshold_high=float(self.temp_high_var.get()),
                temp_threshold_low=float(self.temp_low_var.get()),
                voltage_threshold_high=float(self.volt_high_var.get()),
                voltage_threshold_low=float(self.volt_low_var.get())
            )
        except ValueError as val_err:
            messagebox.showerror("Dữ liệu đầu vào lỗi", f"Vui lòng kiểm tra lại kiểu dữ liệu nhập vào:\n{val_err}")
            return
        except Exception as e:
            messagebox.showerror("Dữ liệu không hợp lệ", f"Dữ liệu cấu hình không đúng quy định:\n{e}")
            return

        # Chạy trong luồng riêng để tránh làm đơ UI (vì chờ phản hồi từ ECU mất tối đa 2s)
        def run_write():
            self.btn_write_config.configure(state="disabled")
            logger.info("Đang bắt đầu nạp dữ liệu xuống ECU...")
            success = self.ecu_service.send_config(cfg)
            if success:
                self.after(0, lambda: messagebox.showinfo("Thành công", "Nạp cấu hình xuống ECU thành công!"))
            else:
                self.after(0, lambda: messagebox.showerror("Thất bại", "Không thể nạp cấu hình xuống ECU. Thiết bị không phản hồi hoặc từ chối cấu hình."))
            self.after(0, lambda: self.btn_write_config.configure(state="normal"))

        threading.Thread(target=run_write, daemon=True).start()



    def _update_config_form(self, cfg: ECUConfig):
        """Cập nhật dữ liệu từ đối tượng ECUConfig vào form nhập liệu."""
        self.dev_id_var.set(str(cfg.device_id))
        self.mode_var.set(cfg.mode)
        self.interval_var.set(str(cfg.update_interval_ms))
        self.temp_high_var.set(str(cfg.temp_threshold_high))
        self.temp_low_var.set(str(cfg.temp_threshold_low))
        self.volt_high_var.set(str(cfg.voltage_threshold_high))
        self.volt_low_var.set(str(cfg.voltage_threshold_low))

    def reboot_ecu_device(self):
        """Yêu cầu ECU reboot."""
        if not messagebox.askyesno("Khởi động lại ECU", "Bạn có chắc chắn muốn phát lệnh khởi động lại ECU không?"):
            return

        def run_reboot():
            self.btn_reboot.configure(state="disabled")
            success = self.ecu_service.reboot_ecu()
            if success:
                self.after(0, lambda: messagebox.showinfo("Khởi động lại", "Lệnh khởi động lại đã được ECU thực thi và phản hồi ACK thành công."))
            else:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Không nhận được phản hồi ACK từ ECU cho lệnh khởi động lại."))
            self.after(0, lambda: self.btn_reboot.configure(state="normal"))

        threading.Thread(target=run_reboot, daemon=True).start()

    def _on_ecu_status_updated(self, status: Dict[str, Any]):
        """Callback cập nhật dữ liệu thời gian thực lên màn hình."""
        # Chạy trong luồng chính của Tkinter
        self.after(0, self._ui_update_status, status)

    def _ui_update_status(self, status: Dict[str, Any]):
        self.lbl_temp_val.configure(text=f"{status['temperature']} °C")
        self.lbl_volt_val.configure(text=f"{status['voltage']} V")
        self.lbl_uptime.configure(text=f"{status['uptime_seconds']} giây")
        
        # Xử lý hiển thị mã lỗi
        err_code = status['error_code']
        if err_code == 0:
            self.lbl_err_code.configure(text="Bình thường (0x00)", text_color="#28a745")
        else:
            self.lbl_err_code.configure(text=f"Lỗi: 0x{err_code:02X}", text_color="#dc3545")

    def _update_window_title(self):
        """Cập nhật tiêu đề cửa sổ hiển thị tên file cấu hình đang làm việc."""
        file_name = os.path.basename(self.values_path)
        self.title(f"Hệ Thống Cấu Hình ECU - [{file_name}]")

    def _save_to_file(self, file_path: str) -> bool:
        """Helper lưu cấu hình hiện tại ở giao diện ra file được chỉ định."""
        try:
            # Thu thập và tạo đối tượng
            serial_cfg = SerialConfig(
                port=self.port_var.get(),
                baudrate=int(self.baud_var.get())
            )
            app_cfg = self.app_cfg # Giữ nguyên các cấu hình theme
            ecu_cfg = ECUConfig(
                device_id=int(self.dev_id_var.get()),
                mode=self.mode_var.get(),
                update_interval_ms=int(self.interval_var.get()),
                temp_threshold_high=float(self.temp_high_var.get()),
                temp_threshold_low=float(self.temp_low_var.get()),
                voltage_threshold_high=float(self.volt_high_var.get()),
                voltage_threshold_low=float(self.volt_low_var.get())
            )
            
            if file_path.endswith((".yml", ".yaml")):
                FileManager.save_app_settings(file_path, serial_cfg, app_cfg, ecu_cfg)
            elif file_path.endswith(".json"):
                data = {
                    "serial": serial_cfg.model_dump(),
                    "app": app_cfg.model_dump(),
                    "ecu_default_config": ecu_cfg.model_dump()
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            else:
                # Mặc định lưu thành YAML
                file_path += ".yml"
                FileManager.save_app_settings(file_path, serial_cfg, app_cfg, ecu_cfg)

            self.values_path = file_path
            self._update_window_title()
            logger.info(f"Đã lưu cấu hình thành công vào file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi ghi file cấu hình {file_path}: {e}")
            messagebox.showerror("Lỗi lưu cấu hình", f"Không thể ghi cấu hình ra file:\n{e}")
            return False

    def save_current_settings(self):
        """Lưu các cấu hình hiện tại đè lên file hiện hành đang làm việc."""
        if self._save_to_file(self.values_path):
            messagebox.showinfo("Lưu thành công", f"Đã lưu cấu hình đè lên file {os.path.basename(self.values_path)} thành công!")

    def save_as_settings(self):
        """Lưu cấu hình hiện tại thành một file mới."""
        file_path = filedialog.asksaveasfilename(
            title="Lưu cấu hình thành file mới",
            initialfile=os.path.basename(self.values_path),
            filetypes=[("YAML files", "*.yml;*.yaml"), ("JSON files", "*.json"), ("Tất cả các file", "*.*")],
            defaultextension=".yml"
        )
        if not file_path:
            return
            
        if self._save_to_file(file_path):
            messagebox.showinfo("Lưu thành công", f"Đã lưu cấu hình mới vào file {os.path.basename(file_path)} thành công!")

    def import_config_file(self):
        """Nạp cấu hình từ một file bất kỳ do người dùng chọn."""
        file_path = filedialog.askopenfilename(
            title="Chọn file cấu hình",
            filetypes=[("YAML files", "*.yml;*.yaml"), ("JSON files", "*.json"), ("Tất cả các file", "*.*")]
        )
        if not file_path:
            return

        try:
            import json
            if file_path.endswith((".yml", ".yaml")):
                data = FileManager.load_yaml(file_path)
            elif file_path.endswith(".json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                raise ValueError("Định dạng file không được hỗ trợ. Vui lòng chọn file JSON hoặc YAML.")

            # Nếu file chứa full cấu hình hoặc chỉ chứa phần cấu hình ECU
            ecu_data = data.get("ecu_default_config", data)
            cfg = ECUConfig(**ecu_data)
            
            # Cập nhật cấu hình Serial nếu có trong file
            if isinstance(data, dict) and "serial" in data:
                try:
                    self.serial_cfg = SerialConfig(**data["serial"])
                    self.port_var.set(self.serial_cfg.port)
                    self.baud_var.set(str(self.serial_cfg.baudrate))
                except Exception as e:
                    logger.warning(f"Không thể nạp cấu hình Serial từ file: {e}")

            self._update_config_form(cfg)
            
            self.values_path = file_path
            self._update_window_title()
            
            logger.info(f"Đã nhập cấu hình thành công từ file: {file_path}")
            messagebox.showinfo("Thành công", f"Đã tải cấu hình từ file {os.path.basename(file_path)} lên giao diện thành công.")
        except Exception as e:
            logger.error(f"Lỗi khi nhập file cấu hình: {e}")
            messagebox.showerror("Lỗi nạp file", f"Không thể nạp dữ liệu cấu hình từ file được chọn:\n{e}")

    def clear_log_box(self):
        """Xóa trắng hộp log."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def destroy(self):
        """Xử lý dọn dẹp kết nối khi đóng ứng dụng."""
        logger.info("Đang đóng ứng dụng, ngắt kết nối phần cứng...")
        self.ecu_service.disconnect()
        super().destroy()


if __name__ == "__main__":
    app = ECUConfigApp()
    app.mainloop()
