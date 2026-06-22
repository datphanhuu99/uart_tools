import logging
from typing import Callable, Dict, Any, Tuple, Optional
from uart.serial_manager import SerialManager
from uart.frame_codec import FrameCodec
from uart.rx_worker import RXWorker
from protocol.format_loader import FormatLoader
from protocol.packer import Packer
from protocol.parser import Parser
from protocol.value_mapper import ValueMapper

class UARTController:
    """
    Core controller class that coordinates all UART and protocol parsing operations.
    Acts as an intermediary/orchestrator layer between the TUI presentation (UI)
    and underlying components like SerialManager, FrameCodec, and Packer/Parser.
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, rtscts: bool = False, formats_dir: str = "formats"):
        """
        Initialize the UART controller and its constituent sub-modules.
        """
        self.serial_manager = SerialManager(port, baudrate, rtscts)
        self.frame_codec = FrameCodec()
        
        # Load protocols from YAML files
        self.format_loader = FormatLoader(formats_dir)
        self.format_loader.load_all()
        
        self.packer = Packer()
        self.parser = Parser()
        self.value_mapper = ValueMapper(self.format_loader)
        
        # Callbacks (registered by the presentation layer)
        self.on_message_received_cb: Optional[Callable[[int, Dict[str, Any], Dict[str, Any]], None]] = None
        self.on_raw_received_cb: Optional[Callable[[bytes], None]] = None
        self.on_status_changed_cb: Optional[Callable[[str, str, str], None]] = None
        
        # Spawn the rx worker thread, passing serial_manager, frame_codec, and internal callbacks
        self.rx_worker = RXWorker(
            serial_manager=self.serial_manager,
            codec=self.frame_codec,
            on_message_received=self._internal_on_message_received,
            on_raw_received=self._internal_on_raw_received
        )

    def register_callbacks(
        self,
        on_message_received: Callable[[int, Dict[str, Any], Dict[str, Any]], None],
        on_raw_received: Callable[[bytes], None],
        on_status_changed: Callable[[str, str, str], None]
    ) -> None:
        """
        Register presentation layer callbacks to handle asynchronous events.
        """
        self.on_message_received_cb = on_message_received
        self.on_raw_received_cb = on_raw_received
        self.on_status_changed_cb = on_status_changed

    def connect(self) -> Tuple[bool, str]:
        """
        Establish serial connection and start the receiver background thread.
        """
        success, msg = self.serial_manager.connect()
        if success:
            self._notify_status("STATUS", f"Connected to {self.serial_manager.port}", "green")
            # Start RXWorker thread if not already running
            if not self.rx_worker.is_alive():
                # Re-instantiate RXWorker if stopped previously
                if not self.rx_worker.running and self.rx_worker._started.is_set():
                    self.rx_worker = RXWorker(
                        serial_manager=self.serial_manager,
                        codec=self.frame_codec,
                        on_message_received=self._internal_on_message_received,
                        on_raw_received=self._internal_on_raw_received
                    )
                self.rx_worker.start()
        else:
            self._notify_status("ERROR", f"Failed to connect: {msg}", "red")
        return success, msg

    def disconnect(self) -> None:
        """
        Stop the receiver thread and close serial connection.
        """
        self.rx_worker.stop()
        self.serial_manager.disconnect()
        self._notify_status("STATUS", "Disconnected", "yellow")

    def send_text(self, text: str) -> None:
        """
        Send raw ASCII text terminated with carriage return and newline.
        """
        data = text.encode('utf-8') + b'\r\n'
        self.serial_manager.send_raw(data)
        self._notify_status("TX", text, "blue")

    def send_command(self, cmd_name: str, values: Dict[str, Any]) -> None:
        """
        Pack command arguments defined by name in YAML rules into bytes,
        frame them with FrameCodec, and transmit them via SerialManager.
        """
        cmd_def = self.format_loader.get_command(cmd_name)
        if not cmd_def:
            self._notify_status("ERROR", f"Command definition '{cmd_name}' not found", "red")
            return
            
        payload = self.packer.pack(cmd_def, values)
        frame = self.frame_codec.pack(cmd_def['msg_id'], payload)
        self.serial_manager.send_raw(frame)
        self._notify_status("TX", f"Command: {cmd_name} | Values: {values}", "blue")

    def set_protocol_config(self, mode: str, crc_type: str, endian: str) -> None:
        """
        Update FrameCodec settings dynamically.
        """
        self.frame_codec.protocol_mode = "cobs"
        self.frame_codec.cobs_crc_type = "crc16_2b"
        self.frame_codec.cobs_endian = "big"
        self._notify_status(
            "STATUS",
            "Protocol fixed to implemented MCU spec: COBS + CRC16/CCITT-FALSE + big-endian LEN/CRC",
            "cyan",
        )

    def _internal_on_message_received(self, msg_id: int, payload: bytes) -> None:
        """
        Internal event handler for incoming unpacked messages. Parses and maps the payload values.
        """
        msg_def = self.format_loader.get_rx_message(msg_id)
        if not msg_def:
            if self.on_message_received_cb:
                raw_hex = " ".join(f"{b:02X}" for b in payload)
                self.on_message_received_cb(msg_id, {}, {"raw_payload": raw_hex, "len": len(payload)})
            return

        try:
            payload_fields = msg_def.get('payload', [])
            parsed_values = self.parser.parse(msg_def, payload)
            mapped_values = {}
            
            # Safely map parsed values, preventing StopIteration if definitions don't match
            for field_name, val in parsed_values.items():
                # Find the matching field definition structure
                field_def = None
                for f in payload_fields:
                    if f.get('name') == field_name:
                        field_def = f
                        break
                
                if field_def:
                    mapped_values[field_name] = self.value_mapper.map_value(val, field_def)
                else:
                    mapped_values[field_name] = val
                    
            if self.on_message_received_cb:
                self.on_message_received_cb(msg_id, msg_def, mapped_values)
        except Exception as e:
            logging.getLogger(__name__).debug(
                "Falling back to raw payload for msg 0x%02X due to parse mismatch: %s",
                msg_id,
                e,
            )
            if self.on_message_received_cb:
                raw_hex = " ".join(f"{b:02X}" for b in payload)
                self.on_message_received_cb(msg_id, {}, {"raw_payload": raw_hex, "len": len(payload)})

    def _internal_on_raw_received(self, data: bytes) -> None:
        """
        Internal event handler for raw incoming bytes. Triggers presentation callbacks.
        """
        if self.on_raw_received_cb:
            self.on_raw_received_cb(data)

    def _notify_status(self, tag: str, message: str, color: str) -> None:
        """
        Helper method to dispatch status changes to presentation layer.
        """
        if self.on_status_changed_cb:
            self.on_status_changed_cb(tag, message, color)
