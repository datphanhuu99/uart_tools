from textual.app import App
from ui.terminal_screen import TerminalScreen
from ui.config_screen import ConfigScreen
from uart.serial_manager import SerialManager
from uart.rx_worker import RXWorker
from protocol.format_loader import FormatLoader
from protocol.value_mapper import ValueMapper
from protocol.packer import Packer
from protocol.parser import Parser
from uart.frame_codec import FrameCodec
import threading

class UARTToolApp(App):
    BINDINGS = [
        ("f1", "switch_screen('terminal')", "Terminal"),
        ("f2", "switch_screen('config')", "Config"),
        ("q", "quit", "Quit"),
    ]
    
    SCREENS = {
        "terminal": TerminalScreen,
        "config": ConfigScreen,
    }

    def __init__(self, port, baudrate):
        super().__init__()
        self.serial_manager = SerialManager(port, baudrate)
        self.format_loader = FormatLoader("formats")
        self.format_loader.load_all()
        self.value_mapper = ValueMapper(self.format_loader)
        self.packer = Packer()
        self.parser = Parser()
        self.rx_worker = RXWorker(self.serial_manager, 
                                  on_message_received=self.on_message_received,
                                  on_raw_received=self.on_raw_received)

    def on_mount(self):
        self.push_screen("terminal")
        success, msg = self.serial_manager.connect()
        term = self.get_screen("terminal")
        if success:
            term.append_log("STATUS", f"Connected to {self.serial_manager.port}", "green")
            self.rx_worker.start()
        else:
            term.append_log("ERROR", f"Failed to connect: {msg}", "red")

    def on_unmount(self):
        self.rx_worker.stop()
        self.serial_manager.disconnect()

    def action_switch_screen(self, screen_name):
        self.push_screen(screen_name)

    def send_text(self, text):
        data = text.encode('utf-8') + b'\r\n'
        self.serial_manager.send_raw(data)
        term = self.get_screen("terminal")
        term.append_log("TX", text, "blue")

    def send_command(self, cmd_name, values):
        cmd_def = self.format_loader.get_command(cmd_name)
        payload = self.packer.pack(cmd_def, values)
        frame = FrameCodec.pack(cmd_def['msg_id'], payload)
        self.serial_manager.send_raw(frame)
        
        term = self.get_screen("terminal")
        term.append_log("TX", f"Command: {cmd_name} | Values: {values}", "blue")
        self.notify(f"Sent {cmd_name}")

    def on_message_received(self, msg_id, payload):
        msg_def = self.format_loader.get_rx_message(msg_id)
        term = self.get_screen("terminal")
        
        if msg_def:
            parsed_values = self.parser.parse(msg_def, payload)
            mapped_values = {k: self.value_mapper.map_value(v, next(f for f in msg_def['payload'] if f['name'] == k)) 
                             for k, v in parsed_values.items()}
            
            tag = "RX"
            color = "cyan"
            if "ERROR" in msg_def['name']:
                tag = "ERROR"
                color = "red"
            
            msg_str = f"{msg_def['name']} | {mapped_values}"
            self.call_from_thread(term.append_log, tag, msg_str, color)
        else:
            self.call_from_thread(term.append_log, "RX", f"Unknown Msg ID: 0x{msg_id:02X} | Payload: {payload.hex()}", "yellow")

    def on_raw_received(self, data):
        # Optional: display raw text if it looks like ASCII
        try:
            text = data.decode('utf-8').strip()
            if text and all(32 <= ord(c) <= 126 or c in '\r\n' for c in text):
                term = self.get_screen("terminal")
                self.call_from_thread(term.append_log, "RX", text, "white")
        except:
            pass
            
    def call_from_thread(self, func, *args, **kwargs):
        # Textual is not thread-safe for direct widget updates, but call_from_thread helps
        self.call_later(func, *args, **kwargs)
