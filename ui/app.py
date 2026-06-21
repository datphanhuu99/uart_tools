from textual.app import App
from ui.terminal_screen import TerminalScreen
from ui.config_screen import ConfigScreen
from ui.command_manager_screen import CommandManagerScreen
from ui.monitor_screen import MonitorScreen
from uart.controller import UARTController

class UARTToolApp(App):
    """
    Main Textual TUI Application for the UART ECU tool.
    Acts as the presentation layer, delegating logic, state management,
    and serial/protocol operations to the UARTController coordinator.
    """
    BINDINGS = [
        ("f1", "switch_screen('terminal')", "Terminal"),
        ("f2", "switch_screen('config')", "Config"),
        ("f3", "switch_screen('cmd_manager')", "Commands"),
        ("f4", "switch_screen('monitor')", "Monitor"),
        ("q", "quit", "Quit"),
    ]
    
    SCREENS = {
        "terminal": TerminalScreen,
        "config": ConfigScreen,
        "cmd_manager": CommandManagerScreen,
        "monitor": MonitorScreen,
    }

    def __init__(self, port: str, baudrate: int):
        """
        Initialize the UI application and its UARTController.
        """
        super().__init__()
        self.controller = UARTController(port, baudrate)
        # Register UI callbacks with the controller
        self.controller.register_callbacks(
            on_message_received=self.on_message_received,
            on_raw_received=self.on_raw_received,
            on_status_changed=self.on_status_changed
        )

    def on_mount(self):
        """
        Lifecycle event triggered when application mounts.
        Initiates serial connection through the controller.
        """
        self.push_screen("terminal")
        self.controller.connect()

    def on_unmount(self):
        """
        Lifecycle event triggered when application unmounts.
        Ensures clean teardown of serial connections and worker threads.
        """
        self.controller.disconnect()

    def action_switch_screen(self, screen_name: str) -> None:
        """
        Action method to transition between different UI screens.
        """
        self.push_screen(screen_name)

    def send_text(self, text: str) -> None:
        """
        Send raw text through the controller.
        """
        self.controller.send_text(text)

    def send_command(self, cmd_name: str, values: dict) -> None:
        """
        Send formatted command structured payload through the controller.
        """
        self.controller.send_command(cmd_name, values)
        self.notify(f"Sent {cmd_name}")

    def on_message_received(self, msg_id: int, msg_def: dict, mapped_values: dict) -> None:
        """
        Callback handler called by controller when a valid message frame is parsed.
        """
        term = self.get_screen("terminal")
        
        if msg_def:
            if "PARSE_ERROR" in msg_def.get('name', ''):
                tag = "ERROR"
                color = "red"
                msg_str = f"Parse failed for Msg 0x{msg_id:02X}: {msg_def.get('error_msg', '')}"
                self.call_from_thread(term.append_log, tag, msg_str, color)
                return

            tag = "RX"
            color = "cyan"
            if "ERROR" in msg_def.get('name', ''):
                tag = "ERROR"
                color = "red"
            
            msg_str = f"{msg_def['name']} | {mapped_values}"
            self.call_from_thread(term.append_log, tag, msg_str, color)
            
            # Also forward to MonitorScreen if loaded
            try:
                monitor = self.get_screen("monitor")
                self.call_from_thread(monitor.update_message, msg_def, mapped_values)
            except Exception:
                pass
        else:
            self.call_from_thread(term.append_log, "RX", f"Unknown Msg ID: 0x{msg_id:02X}", "yellow")

    def on_raw_received(self, data: bytes) -> None:
        """
        Callback handler called by controller when raw serial bytes are received.
        """
        try:
            text = data.decode('utf-8').strip()
            if text and all(32 <= ord(c) <= 126 or c in '\r\n' for c in text):
                term = self.get_screen("terminal")
                self.call_from_thread(term.append_log, "RX", text, "white")
        except Exception:
            pass

    def on_status_changed(self, tag: str, message: str, color: str) -> None:
        """
        Callback handler called by controller when status changes.
        """
        try:
            term = self.get_screen("terminal")
            self.call_from_thread(term.append_log, tag, message, color)
        except Exception:
            pass
            
    def call_from_thread(self, func, *args, **kwargs):
        """
        Thread-safe helper to schedule UI operations on the main Textual event loop.
        """
        self.call_later(func, *args, **kwargs)

