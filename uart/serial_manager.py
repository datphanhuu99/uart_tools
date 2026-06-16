import serial
import logging
import os
from datetime import datetime

class SerialManager:
    def __init__(self, port=None, baudrate=115200, log_dir="logs"):
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        self.log_dir = log_dir
        self.is_connected = False
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_file = os.path.join(log_dir, f"uart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.is_connected = True
            self.log(f"[STATUS] Connected to {self.port} at {self.baudrate} baud")
            return True, "Connected"
        except Exception as e:
            self.is_connected = False
            return False, str(e)

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
        self.log("[STATUS] Disconnected")

    def send_raw(self, data: bytes):
        if self.is_connected and self.ser:
            self.ser.write(data)
            self.log_hex("[TX]", data)

    def read(self, size=1024):
        if self.is_connected and self.ser:
            return self.ser.read(size)
        return b""

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def log_hex(self, tag, data: bytes):
        hex_str = ' '.join([f'{b:02X}' for b in data])
        self.log(f"{tag} {hex_str}")
