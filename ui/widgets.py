from textual.widgets import Static, Input, RichLog, Button, Select, Label
from textual.containers import Vertical, Horizontal

class FieldInput(Horizontal):
    """A widget for a single payload field input."""
    def __init__(self, field_def, value_mapper, initial_value=None):
        super().__init__()
        self.field_def = field_def
        self.value_mapper = value_mapper
        self.field_name = field_def['name']
        self.initial_value = initial_value

    def compose(self):
        yield Label(f"{self.field_name}: ", classes="field-label")
        if 'enum' in self.field_def:
            options = [(str(v), str(v)) for v in self.field_def['enum'].values()]
            yield Select(options, value=str(self.initial_value) if self.initial_value else None)
        elif 'map' in self.field_def:
            map_name = self.field_def['map']
            mapping = self.value_mapper.loader.get_map(map_name)
            options = [(str(v), str(v)) for v in mapping.values()]
            yield Select(options, value=str(self.initial_value) if self.initial_value else None)
        else:
            yield Input(value=str(self.initial_value) if self.initial_value is not None else "", placeholder=f"Type: {self.field_def['type']}")

    def get_value(self):
        widget = self.query_one(Select) if self.query(Select) else self.query_one(Input)
        return widget.value
