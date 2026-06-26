import yaml
import json
import os
import logging
from typing import Dict, Any, Tuple
from app.models.config_model import SerialConfig, AppConfig, ECUConfig

logger = logging.getLogger("ecu_app")

class FileManager:
    """
    Lớp quản lý đọc ghi cấu hình cục bộ từ file YAML hoặc JSON.
    """

    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """Đọc và phân tích file YAML."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data or {}
        except Exception as e:
            logger.error(f"Lỗi khi đọc file YAML {file_path}: {e}")
            raise

    @staticmethod
    def save_yaml(file_path: str, data: Dict[str, Any]) -> None:
        """Ghi dữ liệu vào file YAML."""
        try:
            # Tạo thư mục cha nếu chưa tồn tại
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Đã lưu cấu hình vào file YAML: {file_path}")
        except Exception as e:
            logger.error(f"Lỗi khi ghi file YAML {file_path}: {e}")
            raise

    @classmethod
    def load_app_settings(cls, values_path: str) -> Tuple[SerialConfig, AppConfig, ECUConfig]:
        """
        Nạp cấu hình ứng dụng từ file values.yml và khởi tạo các đối tượng Pydantic models.
        """
        logger.info(f"Đang nạp cấu hình hệ thống từ: {values_path}")
        try:
            data = cls.load_yaml(values_path)
            
            serial_data = data.get("serial", {})
            app_data = data.get("app", {})
            ecu_data = data.get("ecu_default_config", {})

            # Khởi tạo mô hình dữ liệu Pydantic (sẽ tự động validate)
            serial_cfg = SerialConfig(**serial_data)
            app_cfg = AppConfig(**app_data)
            ecu_cfg = ECUConfig(**ecu_data)

            return serial_cfg, app_cfg, ecu_cfg
        except Exception as e:
            logger.warning(f"Lỗi phân tích {values_path}, sử dụng cấu hình mặc định: {e}")
            # Trả về các cấu hình mặc định của hệ thống nếu xảy ra lỗi
            return SerialConfig(), AppConfig(), ECUConfig()

    @classmethod
    def save_app_settings(
        cls, values_path: str, serial_cfg: SerialConfig, app_cfg: AppConfig, ecu_cfg: ECUConfig
    ) -> None:
        """
        Lưu cấu hình hiện tại của ứng dụng về file values.yml.
        """
        data = {
            "serial": serial_cfg.model_dump(),
            "app": app_cfg.model_dump(),
            "ecu_default_config": ecu_cfg.model_dump()
        }
        cls.save_yaml(values_path, data)
