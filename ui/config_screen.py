from textual.screen import Screen
from textual.widgets import Select, Button, Label, Header, Footer
from textual.containers import Vertical, Horizontal, ScrollableContainer
from ui.widgets import FieldInput
import yaml
import os

class ConfigScreen(Screen):
    def compose(self):
        yield Header()
        with Horizontal():
            yield Label("Select Command: ")
            yield Select([], id="cmd_select")
        
        with Horizontal():
            yield Label("Select Preset:  ")
            yield Select([], id="preset_select")
        
        yield ScrollableContainer(id="fields_container")
        
        with Horizontal():
            yield Button("Send", variant="primary", id="send_btn")
            yield Button("Save Preset", variant="default", id="save_btn")
        yield Footer()

    def on_mount(self):
        self.update_commands()
        self.update_presets()

    def update_commands(self):
        commands = self.app.format_loader.commands
        options = [(name, name) for name in commands.keys()]
        self.query_one("#cmd_select").options = options

    def update_presets(self):
        preset_dir = "presets"
        if not os.path.exists(preset_dir):
            return
        files = [f for f in os.listdir(preset_dir) if f.endswith(".yaml")]
        options = [(f, f) for f in files]
        self.query_one("#preset_select").options = options

    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "cmd_select":
            self.render_fields(event.value)
        elif event.select.id == "preset_select":
            self.load_preset(event.value)

    def load_preset(self, preset_file):
        if not preset_file:
            return
        path = os.path.join("presets", preset_file)
        with open(path, "r") as f:
            preset_data = yaml.safe_load(f)
        
        cmd_name = preset_data.get('command')
        self.query_one("#cmd_select").value = cmd_name
        self.render_fields(cmd_name, preset_data.get('values'))

    def render_fields(self, cmd_name, preset_values=None):
        container = self.query_one("#fields_container")
        container.query("*").remove()
        
        cmd_def = self.app.format_loader.get_command(cmd_name)
        if not cmd_def:
            return
            
        for field in cmd_def.get('payload', []):
            initial = None
            if preset_values:
                initial = preset_values.get(field['name'])
            container.mount(FieldInput(field, self.app.value_mapper, initial_value=initial))

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
            mapped_val = self.app.value_mapper.unmap_value(raw_val, field_input.field_def)
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
