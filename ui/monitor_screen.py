from textual.screen import Screen
from textual.widgets import Select, Button, Label, Header, Footer, DataTable
from textual.containers import Vertical, Horizontal, ScrollableContainer
from ui.widgets import FieldInput
import os

class MonitorScreen(Screen):
    """
    Monitor Screen (F4): Combines a TX command sender panel on the left 
    with a real-time RX parameter monitoring table on the right.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.latest_values = {}  # Cache of the latest received parameter values

    def compose(self):
        yield Header()
        with Horizontal():
            # Left panel - Command Sender (TX)
            with Vertical(id="left_panel"):
                yield Label("[bold cyan]Command Sender (TX)[/bold cyan]\n")
                yield Label("Select Command:")
                yield Select([], id="cmd_select", prompt="Choose Command")
                yield Label("\nPayload Fields:")
                yield ScrollableContainer(id="fields_container")
                yield Button("Send Command", id="send_btn", variant="primary")
            
            # Right panel - Real-time Parameter Monitor (RX)
            with Vertical(id="right_panel"):
                yield Label("[bold green]Parameter Monitor (RX)[/bold green]\n")
                yield DataTable(id="monitor_table")
                yield Button("Clear Monitor", id="clear_btn", variant="error")
        yield Footer()

    def on_mount(self):
        # Style panels
        left_panel = self.query_one("#left_panel")
        left_panel.styles.width = "40%"
        left_panel.styles.border_right = ("solid", "gray")
        left_panel.styles.padding = 1
        
        right_panel = self.query_one("#right_panel")
        right_panel.styles.width = "60%"
        right_panel.styles.padding = 1
        
        fields_container = self.query_one("#fields_container")
        fields_container.styles.height = "1fr"
        fields_container.styles.border = ("solid", "gray")
        fields_container.styles.margin = (0, 0, 1, 0)
        fields_container.styles.padding = 1
        
        send_btn = self.query_one("#send_btn")
        send_btn.styles.width = "1fr"
        
        clear_btn = self.query_one("#clear_btn")
        clear_btn.styles.width = "1fr"
        clear_btn.styles.margin = (1, 0, 0, 0)

        # Configure DataTable
        table = self.query_one("#monitor_table", DataTable)
        table.add_columns("Mã Lệnh", "Tên Biến", "Giá Trị", "Định Dạng")
        table.zebra_stripes = True
        table.styles.height = "1fr"

        self.update_commands()

    def update_commands(self):
        """Load TX commands from format loader into dropdown select."""
        commands = self.app.controller.format_loader.commands
        options = [(name, name) for name in commands.keys()]
        try:
            self.query_one("#cmd_select", Select).set_options(options)
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "cmd_select":
            self.render_fields(event.value)

    def render_fields(self, cmd_name, preset_values=None):
        """Render field inputs based on selected command payload structure."""
        container = self.query_one("#fields_container")
        container.query("*").remove()
        
        cmd_def = self.app.controller.format_loader.get_command(cmd_name)
        if not cmd_def:
            return
            
        for field in cmd_def.get('payload', []):
            initial = None
            if preset_values:
                initial = preset_values.get(field['name'])
            container.mount(FieldInput(field, self.app.controller.value_mapper, initial_value=initial))

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            self.send_command()
        elif event.button.id == "clear_btn":
            self.clear_monitor()

    def send_command(self):
        cmd_name = self.query_one("#cmd_select").value
        if not cmd_name:
            self.app.notify("Please select a command to send.", severity="error")
            return
            
        values = {}
        for field_input in self.query(FieldInput):
            raw_val = field_input.get_value()
            mapped_val = self.app.controller.value_mapper.unmap_value(raw_val, field_input.field_def)
            values[field_input.field_name] = mapped_val
            
        self.app.send_command(cmd_name, values)

    def update_message(self, msg_def, mapped_values):
        """
        Public method called on incoming frames to update the monitoring table.
        Receives parsed variables and updates parameter rows dynamically.
        """
        fields = msg_def.get('payload', [])
        for field in fields:
            name = field['name']
            val = mapped_values.get(name)
            if val is not None:
                self.latest_values[name] = {
                    'msg_name': msg_def['name'],
                    'value': val,
                    'details': f"{field['type']} ({field.get('endian', 'little')})"
                }
        
        # Clear and redraw the rows of the DataTable
        table = self.query_one("#monitor_table", DataTable)
        table.clear(columns=False)
        
        for name, data in self.latest_values.items():
            table.add_row(
                data['msg_name'],
                name,
                str(data['value']),
                data['details']
            )

    def clear_monitor(self):
        """Clear cached parameter values and empty the monitor table."""
        self.latest_values.clear()
        table = self.query_one("#monitor_table", DataTable)
        table.clear(columns=False)
        self.app.notify("Monitor cleared.")
