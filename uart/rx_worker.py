import threading
import time
from uart.frame_codec import FrameCodec

class RXWorker(threading.Thread):
    """
    Worker thread that continuously reads raw bytes from the SerialManager,
    passes them to the FrameCodec to reconstruct complete messages, and
    triggers callbacks upon raw data reception and successful frame decoding.
    """
    def __init__(self, serial_manager, codec, on_message_received=None, on_raw_received=None):
        """
        Initialize the RX worker thread.
        
        Args:
            serial_manager: SerialManager instance to read bytes from.
            codec: FrameCodec instance used for packet extraction.
            on_message_received: Callback function invoked when a message is successfully unpacked.
            on_raw_received: Callback function invoked for raw bytes.
        """
        super().__init__()
        self.serial_manager = serial_manager
        self.codec = codec
        self.on_message_received = on_message_received
        self.on_raw_received = on_raw_received
        self.running = False
        self.paused = False
        self.daemon = True

    def run(self):
        """
        Main runner loop of the background thread that queries SerialManager for bytes
        and processes the received stream.
        """
        self.running = True
        while self.running:
            if self.serial_manager.is_connected and not self.paused:
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
        """
        Stop the worker thread run execution loop.
        """
        self.running = False

