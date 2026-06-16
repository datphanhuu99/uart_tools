import threading
import time
from uart.frame_codec import FrameCodec

class RXWorker(threading.Thread):
    def __init__(self, serial_manager, on_message_received=None, on_raw_received=None):
        super().__init__()
        self.serial_manager = serial_manager
        self.codec = FrameCodec()
        self.on_message_received = on_message_received
        self.on_raw_received = on_raw_received
        self.running = False
        self.daemon = True

    def run(self):
        self.running = True
        while self.running:
            if self.serial_manager.is_connected:
                try:
                    data = self.serial_manager.read(128)
                    if data:
                        # Log raw RX
                        self.serial_manager.log_hex("[RX]", data)
                        
                        # Try to unpack frames
                        messages = self.codec.unpack(data)
                        for msg_id, payload in messages:
                            if self.on_message_received:
                                self.on_message_received(msg_id, payload)
                        
                        # Also pass raw data for terminal display if needed
                        if self.on_raw_received:
                            self.on_raw_received(data)
                    else:
                        time.sleep(0.01)
                except Exception as e:
                    self.serial_manager.log(f"[ERROR] RX Worker error: {e}")
                    time.sleep(1)
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False
