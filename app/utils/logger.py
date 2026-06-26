import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "ecu_app", log_level: str = "INFO") -> logging.Logger:
    """
    Cấu hình hệ thống ghi log của ứng dụng, ghi ra cả console và file log xoay vòng.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Tránh thêm trùng lặp các handler nếu logger đã được cấu hình trước đó
    if logger.handlers:
        return logger

    # Định dạng log
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(threadName)s] [%(filename)s:%(lineno)d] - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Ghi log vào file với chế độ xoay vòng - tối đa 5 file, mỗi file 2MB)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "app.log")
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.error(f"Không thể tạo file ghi log tại {log_file}: {e}")

    return logger
