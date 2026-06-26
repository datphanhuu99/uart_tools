import pytest
from pydantic import ValidationError
from app.models.config_model import ECUConfig, SerialConfig

def test_valid_ecu_config():
    cfg = ECUConfig(
        device_id=10,
        mode="sport",
        update_interval_ms=500,
        temp_threshold_high=90.0,
        temp_threshold_low=-5.0,
        voltage_threshold_high=15.0,
        voltage_threshold_low=10.0
    )
    assert cfg.device_id == 10
    assert cfg.mode == "sport"
    assert cfg.temp_threshold_high == 90.0

def test_invalid_device_id():
    # ID của thiết bị phải trong khoảng 1-255
    with pytest.raises(ValidationError):
        ECUConfig(device_id=0)
        
    with pytest.raises(ValidationError):
        ECUConfig(device_id=256)

def test_invalid_mode():
    # Chế độ phải nằm trong các lựa chọn định sẵn
    with pytest.raises(ValidationError):
        ECUConfig(mode="invalid_mode")

def test_invalid_temp_thresholds():
    # Ngưỡng cao phải lớn hơn ngưỡng thấp
    with pytest.raises(ValidationError) as excinfo:
        ECUConfig(temp_threshold_high=20.0, temp_threshold_low=30.0)
    assert "temp_threshold_high phải lớn hơn temp_threshold_low" in str(excinfo.value)

def test_invalid_voltage_thresholds():
    # Ngưỡng điện áp cao phải lớn hơn ngưỡng điện áp thấp
    with pytest.raises(ValidationError) as excinfo:
        ECUConfig(voltage_threshold_high=9.0, voltage_threshold_low=12.0)
    assert "voltage_threshold_high phải lớn hơn voltage_threshold_low" in str(excinfo.value)

def test_valid_serial_config():
    cfg = SerialConfig(
        port="COM5",
        baudrate=115200,
        timeout=2.0
    )
    assert cfg.port == "COM5"
    assert cfg.baudrate == 115200

def test_invalid_baudrate():
    # Baudrate phải nằm trong tập hợp các baudrate chuẩn
    with pytest.raises(ValidationError):
        SerialConfig(baudrate=12345)
