import serial
import logging
import os
from datetime import datetime

class SerialManager:
    """
    Manages serial port operations and communications.
    Handles establishing connections, disconnection, transmission,
    reception, and logging of hexadecimal and ASCII operations to log files.
    """
    def __init__(self, port=None, baudrate=115200, log_dir="logs"):
        """
        Initialize SerialManager settings.
        
        Args:
            port: String name of the serial port (e.g. /dev/ttyUSB0).
            baudrate: Port baudrate speed (default 115200).
            log_dir: Directory to save connection log output.
        """
        self.ser = None
        self.port = port
        self.baudrate = baudrate
        self.log_dir = log_dir
        self.is_connected = False
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_file = os.path.join(log_dir, f"uart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    def connect(self):
        """
        Open the configured serial interface and verify connectivity.
        
        Returns:
            A tuple of (success_boolean, status_message_string).
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.is_connected = True
            self.log(f"[STATUS] Connected to {self.port} at {self.baudrate} baud")
            return True, "Connected"
        except Exception as e:
            self.is_connected = False
            return False, str(e)

    def disconnect(self):
        """
        Safely disconnect from the active serial interface.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
        self.log("[STATUS] Disconnected")

    def send_raw(self, data: bytes):
        """
        Transmit raw byte strings over the open serial port.
        
        Args:
            data: Raw byte content to transmit.
        """
        if self.is_connected and self.ser:
            self.ser.write(data)
            self.log_hex("[TX]", data)

    def read(self, size=1024):
        """
        Read up to 'size' bytes from the serial buffer.
        
        Args:
            size: Maximum quantity of bytes to extract.
            
        Returns:
            Raw bytes extracted from the device buffer.
        """
        if self.is_connected and self.ser:
            return self.ser.read(size)
        return b""

    def log(self, message):
        """
        Write timestamped text logs to the log file.
        
        Args:
            message: Text trace string.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def log_hex(self, tag, data: bytes):
        """
        Log hex representations of transmitted/received bytes.
        
        Args:
            tag: Logging tag prefix (e.g. '[RX]', '[TX]').
            data: Target byte sequence.
        """
        hex_str = ' '.join([f'{b:02X}' for b in data])
        self.log(f"{tag} {hex_str}")

