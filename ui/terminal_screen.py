from textual.screen import Screen
from textual.widgets import RichLog, Input, Header, Footer, Button
from textual.containers import Horizontal
from datetime import datetime
import subprocess

class TerminalScreen(Screen):
    BINDINGS = [
        ("ctrl+y", "copy_log", "Copy Log"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_history = []

    def compose(self):
        yield Header()
        yield RichLog(highlight=True, markup=True, max_lines=10000, id="rx_log")
        with Horizontal(id="input_area"):
            yield Input(placeholder="Type text and press Enter to send...", id="tx_input")
            yield Button("Send", id="send_btn", variant="primary")
            yield Button("Pause RX", id="rx_toggle_btn", variant="warning")
            yield Button("Copy Log", id="copy_btn", variant="default")
        yield Footer()

    def on_mount(self):
        self.query_one("#tx_input").focus()
        
        # Style the horizontal input layout
        input_area = self.query_one("#input_area")
        input_area.styles.height = "auto"
        input_area.styles.align = ("left", "middle")
        
        tx_input = self.query_one("#tx_input")
        tx_input.styles.width = "1fr"
        
        send_btn = self.query_one("#send_btn")
        send_btn.styles.width = "auto"
        
        rx_toggle_btn = self.query_one("#rx_toggle_btn")
        rx_toggle_btn.styles.width = "auto"
        
        copy_btn = self.query_one("#copy_btn")
        copy_btn.styles.width = "auto"

    def append_log(self, tag, message, color="white"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_widget = self.query_one("#rx_log")
        
        # Keep a plain text version in history
        plain_text_message = f"[{timestamp}] [{tag}] {message}"
        self.log_history.append(plain_text_message)
        if len(self.log_history) > 10000:
            self.log_history.pop(0)

        # Check if the user is at the bottom of the log to decide if we should auto-scroll
        is_at_bottom = log_widget.scroll_y >= log_widget.max_scroll_y
        log_widget.write(f"[{timestamp}] [{color}]{tag}[/{color}] {message}", scroll_end=is_at_bottom)

    def send_terminal_input(self):
        tx_input = self.query_one("#tx_input")
        text = tx_input.value
        if text:
            self.app.send_text(text)
            tx_input.value = ""

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "tx_input":
            self.send_terminal_input()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "copy_btn":
            self.action_copy_log()
        elif event.button.id == "send_btn":
            self.send_terminal_input()
        elif event.button.id == "rx_toggle_btn":
            self.toggle_rx()

    def toggle_rx(self):
        worker = self.app.controller.rx_worker
        worker.paused = not worker.paused
        
        btn = self.query_one("#rx_toggle_btn")
        if worker.paused:
            btn.label = "Resume RX"
            btn.variant = "success"
            self.append_log("STATUS", "RX Listening Paused", "yellow")
            self.app.notify("RX Listening Paused")
        else:
            btn.label = "Pause RX"
            btn.variant = "warning"
            self.append_log("STATUS", "RX Listening Resumed", "green")
            self.app.notify("RX Listening Resumed")

    def action_copy_log(self):
        log_text = "\n".join(self.log_history)
        if log_text:
            self.copy_text_to_system_clipboard(log_text)
            self.app.notify("Copied all logs to clipboard!", severity="information")
        else:
            self.app.notify("Log is empty!", severity="warning")

    def copy_text_to_system_clipboard(self, text):
        # 1. Try Textual's built-in OSC 52 method
        self.app.copy_to_clipboard(text)
        
        # 2. Also try system fallback using xclip/xsel since they are available on the user's Linux system
        try:
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE, close_fds=True)
            process.communicate(input=text.encode('utf-8'))
        except Exception:
            try:
                process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE, close_fds=True)
                process.communicate(input=text.encode('utf-8'))
            except Exception:
                pass
