from textual.screen import Screen
from textual.widgets import Select, Button, Label, Header, Footer
from textual.containers import Vertical, Horizontal, ScrollableContainer
from ui.widgets import FieldInput
import yaml
import os

class ConfigScreen(Screen):
    def compose(self):
        yield Header()
        with Horizontal(id="protocol_settings_area"):
            yield Label("Protocol: ")
            yield Select([("Legacy (0xAA 0x55)", "legacy"), ("COBS", "cobs")], value="legacy", id="protocol_select")
            yield Label("  CRC Type: ")
            yield Select([("CRC16 1-Byte", "crc16_1b"), ("CRC16 2-Byte", "crc16_2b"), ("CRC8", "crc8"), ("Checksum", "checksum")], value="crc16_1b", id="crc_select")
            yield Label("  Endian: ")
            yield Select([("Big Endian", "big"), ("Little Endian", "little")], value="big", id="endian_select")
            
        with Horizontal(id="cmd_select_area"):
            yield Label("Select Command: ")
            yield Select([], id="cmd_select")
        
        with Horizontal(id="preset_select_area"):
            yield Label("Select Preset:  ")
            yield Select([], id="preset_select")
        
        yield ScrollableContainer(id="fields_container")
        
        with Horizontal():
            yield Button("Send", variant="primary", id="send_btn")
            yield Button("Save Preset", variant="default", id="save_btn")
        yield Footer()

    def on_mount(self):
        # Style the layout areas to look premium and aligned
        settings_area = self.query_one("#protocol_settings_area")
        settings_area.styles.height = "auto"
        settings_area.styles.align = ("left", "middle")
        settings_area.styles.margin = (0, 0, 1, 0)
        
        # Give Select dropdowns a fixed width so they don't overflow the horizontal layout
        for select in self.query("#protocol_settings_area Select"):
            select.styles.width = 22
            
        self.query_one("#cmd_select_area").styles.height = "auto"
        self.query_one("#preset_select_area").styles.height = "auto"
        
        self.update_commands()
        self.update_presets()

    def update_commands(self):
        commands = self.app.controller.format_loader.commands
        options = [(name, name) for name in commands.keys()]
        try:
            self.query_one("#cmd_select", Select).set_options(options)
        except Exception:
            pass

    def update_presets(self):
        preset_dir = "presets"
        if not os.path.exists(preset_dir):
            return
        files = [f for f in os.listdir(preset_dir) if f.endswith(".yaml")]
        options = [(f, f) for f in files]
        try:
            self.query_one("#preset_select", Select).set_options(options)
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed):
        if event.select.id in ["protocol_select", "crc_select", "endian_select"]:
            mode = self.query_one("#protocol_select").value
            crc = self.query_one("#crc_select").value
            endian = self.query_one("#endian_select").value
            self.app.controller.set_protocol_config(mode, crc, endian)
            self.app.notify(f"Protocol updated: {mode.upper()} ({crc}, {endian})")
        elif event.select.id == "cmd_select":
            self.render_fields(event.value)
        elif event.select.id == "preset_select":
            self.load_preset(event.value)

    def load_preset(self, preset_file):
        if not preset_file:
            return
        path = os.path.join("presets", preset_file)
        try:
            with open(path, "r") as f:
                preset_data = yaml.safe_load(f)
            if not preset_data or not isinstance(preset_data, dict):
                self.app.notify(f"Invalid preset data in {preset_file}", severity="error")
                return
        except Exception as e:
            self.app.notify(f"Failed to read preset: {e}", severity="error")
            return
        
        cmd_name = preset_data.get('command')
        self.query_one("#cmd_select").value = cmd_name
        self.render_fields(cmd_name, preset_data.get('values'))

    def render_fields(self, cmd_name, preset_values=None):
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
        elif event.button.id == "save_btn":
            self.save_preset()

    def send_command(self):
        cmd_name = self.query_one("#cmd_select").value
        if not cmd_name:
            return
            
        values = {}
        for field_input in self.query(FieldInput):
            raw_val = field_input.get_value()
            mapped_val = self.app.controller.value_mapper.unmap_value(raw_val, field_input.field_def)
            values[field_input.field_name] = mapped_val
            
        self.app.send_command(cmd_name, values)

    def save_preset(self):
        cmd_name = self.query_one("#cmd_select").value
        if not cmd_name:
            return
            
        values = {}
        for field_input in self.query(FieldInput):
            values[field_input.field_name] = field_input.get_value()
            
        preset_data = {
            'name': f"{cmd_name}_preset",
            'command': cmd_name,
            'values': values
        }
        
        # In a real app, we might ask for a name. For MVP, just use cmd name.
        path = os.path.join("presets", f"{cmd_name}_preset.yaml")
        with open(path, "w") as f:
            yaml.dump(preset_data, f)
        self.update_presets()
        self.app.notify(f"Preset saved to {path}")
