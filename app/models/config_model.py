from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal

class SerialConfig(BaseModel):
    port: str = Field(default="COM3", description="Cổng kết nối COM/Serial")
    baudrate: int = Field(default=115200, description="Tốc độ truyền (baud rate)")
    timeout: float = Field(default=1.0, ge=0.1, le=10.0, description="Thời gian chờ nhận phản hồi (giây)")
    parity: Literal["N", "E", "O"] = Field(default="N", description="Phương thức kiểm tra chẵn lẻ (None, Even, Odd)")
    stopbits: Literal[1, 1.5, 2] = Field(default=1, description="Stop bits")
    bytesize: Literal[5, 6, 7, 8] = Field(default=8, description="Độ dài bit dữ liệu")

    @field_validator("baudrate")
    @classmethod
    def validate_baudrate(cls, v: int) -> int:
        valid_baudrates = [9600, 19200, 38400, 57600, 115200]
        if v not in valid_baudrates:
            raise ValueError(f"Baudrate không hợp lệ. Phải thuộc: {valid_baudrates}")
        return v

class AppConfig(BaseModel):
    theme: Literal["dark", "light", "system"] = Field(default="dark", description="Giao diện sáng/tối")
    color_theme: str = Field(default="blue", description="Chủ đề màu sắc hiển thị")
    language: Literal["vi", "en"] = Field(default="vi", description="Ngôn ngữ sử dụng")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO", description="Mức độ log hệ thống")

class ECUConfig(BaseModel):
    device_id: int = Field(default=1, ge=1, le=255, description="ID định danh thiết bị ECU (1-255)")
    mode: Literal["normal", "eco", "sport", "diagnostic"] = Field(default="normal", description="Chế độ hoạt động")
    update_interval_ms: int = Field(default=100, ge=10, le=5000, description="Chu kỳ gửi dữ liệu (ms)")
    temp_threshold_high: float = Field(default=85.0, ge=-40.0, le=150.0, description="Ngưỡng nhiệt độ cao cảnh báo (°C)")
    temp_threshold_low: float = Field(default=-10.0, ge=-40.0, le=150.0, description="Ngưỡng nhiệt độ thấp cảnh báo (°C)")
    voltage_threshold_high: float = Field(default=16.0, ge=5.0, le=30.0, description="Ngưỡng điện áp cao cảnh báo (Volt)")
    voltage_threshold_low: float = Field(default=9.0, ge=5.0, le=30.0, description="Ngưỡng điện áp thấp cảnh báo (Volt)")

    @model_validator(mode="after")
    def validate_thresholds(self) -> 'ECUConfig':
        if self.temp_threshold_high <= self.temp_threshold_low:
            raise ValueError("temp_threshold_high phải lớn hơn temp_threshold_low")
        if self.voltage_threshold_high <= self.voltage_threshold_low:
            raise ValueError("voltage_threshold_high phải lớn hơn voltage_threshold_low")
        return self
