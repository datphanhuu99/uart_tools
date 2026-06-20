from textual.screen import Screen
from textual.widgets import Select, Button, Label, Header, Footer, Input, ListView, ListItem, Static
from textual.containers import Vertical, Horizontal, ScrollableContainer
import os
import yaml

class CommandManagerScreen(Screen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_list = []  # List of all command definitions (both TX and RX)
        self.selected_cmd = None
        self.is_editing = False
        self.field_counter = 0

    def compose(self):
        yield Header()
        with Horizontal():
            # Left panel - List of Commands
            with Vertical(id="left_panel"):
                yield Label("[bold]Commands List[/bold]")
                with Horizontal(id="filter_area"):
                    yield Label("Filter: ")
                    yield Select([("All", "all"), ("TX (Commands)", "tx"), ("RX (Messages)", "rx")], value="all", id="filter_select")
                yield ListView(id="cmd_list")
                yield Button("Add New Command", variant="success", id="add_btn")
            
            # Right panel - View Details / Edit Form
            with Vertical(id="right_panel"):
                yield ScrollableContainer(id="details_container")
        yield Footer()

    async def on_mount(self):
        # Style layout
        left_panel = self.query_one("#left_panel")
        left_panel.styles.width = "40%"
        left_panel.styles.border_right = ("solid", "gray")
        left_panel.styles.padding = 1
        
        right_panel = self.query_one("#right_panel")
        right_panel.styles.width = "60%"
        right_panel.styles.padding = 1
        
        filter_area = self.query_one("#filter_area")
        filter_area.styles.height = "auto"
        filter_area.styles.align = ("left", "middle")
        filter_area.styles.margin = (0, 0, 1, 0)
        
        self.load_commands()
        await self.show_welcome_message()

    def load_commands(self):
        # Combine TX and RX commands from format_loader
        self.commands_list = []
        
        # TX
        for name, cmd in self.app.controller.format_loader.commands.items():
            cmd_copy = dict(cmd)
            cmd_copy['direction'] = 'tx'
            self.commands_list.append(cmd_copy)
            
        # RX
        for msg_id, rx in self.app.controller.format_loader.rx_messages.items():
            rx_copy = dict(rx)
            rx_copy['direction'] = 'rx'
            self.commands_list.append(rx_copy)
            
        # Sort by direction then name
        self.commands_list.sort(key=lambda x: (x['direction'], x['name']))
        self.refresh_list()

    def refresh_list(self):
        filter_val = self.query_one("#filter_select").value
        list_view = self.query_one("#cmd_list")
        list_view.clear()
        
        self.filtered_cmds = []
        for cmd in self.commands_list:
            if filter_val == "all" or cmd['direction'] == filter_val:
                self.filtered_cmds.append(cmd)
                label = f"{cmd['name']} (ID: 0x{cmd['msg_id']:02X}) [{cmd['direction'].upper()}]"
                list_view.append(ListItem(Label(label)))

    async def on_select_changed(self, event: Select.Changed):
        if event.select.id == "filter_select":
            self.refresh_list()
            await self.show_welcome_message()

    async def on_list_view_selected(self, event: ListView.Selected):
        if self.is_editing:
            self.app.notify("Please save or cancel editing current command first.", severity="warning")
            return
            
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self.filtered_cmds):
            self.selected_cmd = self.filtered_cmds[idx]
            await self.show_details()

    async def show_welcome_message(self):
        self.selected_cmd = None
        container = self.query_one("#details_container")
        await container.query("*").remove()
        await container.mount(Static("[bold cyan]ECU Command Manager[/bold cyan]\n\n"
                                     "Select a command from the list to view, edit, or delete it.\n"
                                     "Click 'Add New Command' to create a new command template.", id="welcome_msg"))

    async def show_details(self):
        if not self.selected_cmd:
            return
        container = self.query_one("#details_container")
        await container.query("*").remove()
        
        cmd = self.selected_cmd
        
        # Build child widgets for details view
        widgets_to_mount = [
            Label(f"[bold cyan]Command Details[/bold cyan]\n", classes="section-title"),
            Label(f"[bold]Name:[/bold] {cmd['name']}"),
            Label(f"[bold]Message ID:[/bold] 0x{cmd['msg_id']:02X} ({cmd['msg_id']})"),
            Label(f"[bold]Direction:[/bold] {cmd['direction'].upper()}"),
            Label("\n[bold]Payload Fields:[/bold]")
        ]
        
        fields = cmd.get('payload', [])
        if not fields:
            widgets_to_mount.append(Label("  No payload fields (0 bytes)"))
        else:
            for field in fields:
                field_str = f"  • {field['name']}: {field['type']} ({field.get('endian', 'little')} endian)"
                if 'enum' in field:
                    field_str += f" | Enum: {field['enum']}"
                if 'map' in field:
                    field_str += f" | Map: {field['map']}"
                widgets_to_mount.append(Label(field_str))
                
        # Buttons area
        btn_area = Horizontal(
            Button("Edit Command", variant="primary", id="edit_cmd_btn"),
            Button("Delete Command", variant="error", id="delete_cmd_btn"),
            id="details_btn_area"
        )
        btn_area.styles.height = "auto"
        btn_area.styles.margin = (2, 0, 0, 0)
        
        widgets_to_mount.append(btn_area)
        
        # Instantiate details with its children
        details = Vertical(*widgets_to_mount, id="details_view")
        await container.mount(details)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_btn":
            if self.is_editing:
                self.app.notify("Save or cancel current edits first.", severity="warning")
                return
            await self.show_edit_form(is_new=True)
        elif event.button.id == "edit_cmd_btn":
            await self.show_edit_form(is_new=False)
        elif event.button.id == "delete_cmd_btn":
            await self.delete_selected()
        elif event.button.id == "add_field_btn":
            await self.add_field_row()
        elif event.button.id == "save_form_btn":
            await self.save_form()
        elif event.button.id == "cancel_form_btn":
            await self.cancel_form()
        elif event.button.id.startswith("del_field_"):
            field_idx = event.button.id.replace("del_field_", "")
            await self.query_one(f"#field_row_{field_idx}").remove()

    async def show_edit_form(self, is_new=True):
        if not is_new and not self.selected_cmd:
            self.app.notify("No command selected to edit", severity="error")
            return
        self.is_editing = True
        container = self.query_one("#details_container")
        await container.query("*").remove()
        
        title = "Add New Command" if is_new else f"Edit Command: {self.selected_cmd['name']}"
        initial_name = "" if is_new else self.selected_cmd['name']
        initial_id = "" if is_new else f"0x{self.selected_cmd['msg_id']:02X}"
        initial_dir = "tx" if is_new else self.selected_cmd['direction']
        
        # Build field rows before mounting
        field_rows = []
        self.field_counter = 0
        if not is_new:
            for field in self.selected_cmd.get('payload', []):
                row = self.create_field_row(field)
                field_rows.append(row)
        else:
            row = self.create_field_row()
            field_rows.append(row)
            
        fields_scroll = ScrollableContainer(*field_rows, id="form_fields_list")
        fields_scroll.styles.max_height = "15"
        fields_scroll.styles.border = ("solid", "gray")
        fields_scroll.styles.padding = 1
        
        # Form control buttons
        ctrl_area = Horizontal(
            Button("Save", variant="primary", id="save_form_btn"),
            Button("Cancel", variant="default", id="cancel_form_btn"),
            id="form_ctrl_area"
        )
        ctrl_area.styles.height = "auto"
        ctrl_area.styles.margin = (2, 0, 0, 0)
        
        # Build entire form tree
        form = Vertical(
            Label(f"[bold green]{title}[/bold green]\n"),
            Label("Command Name (e.g. MOTOR_STOP):"),
            Input(value=initial_name, placeholder="UPPER_CASE_NAME", id="form_name"),
            Label("\nMessage ID (integer or hex, e.g. 16 or 0x10):"),
            Input(value=initial_id, placeholder="e.g. 0x10", id="form_msg_id"),
            Label("\nDirection:"),
            Select([("TX (Command to ECU)", "tx"), ("RX (Response from ECU)", "rx")], value=initial_dir, id="form_dir"),
            Label("\n[bold]Payload Fields:[/bold]"),
            fields_scroll,
            Button("Add Field", variant="default", id="add_field_btn"),
            ctrl_area,
            id="edit_form"
        )
        
        await container.mount(form)

    def create_field_row(self, field_def=None):
        field_id = self.field_counter
        self.field_counter += 1
        
        # Field Name
        initial_name = field_def['name'] if field_def else f"param_{field_id}"
        field_name_input = Input(value=initial_name, placeholder="Field Name", classes="field-name-in")
        field_name_input.styles.width = "2fr"
        
        # Type Select
        type_options = [
            ("uint8", "uint8"), ("int8", "int8"),
            ("uint16", "uint16"), ("int16", "int16"),
            ("uint32", "uint32"), ("int32", "int32"),
            ("float", "float")
        ]
        initial_type = field_def['type'] if field_def else "uint8"
        type_select = Select(type_options, value=initial_type, classes="field-type-sel")
        type_select.styles.width = "1fr"
        
        # Endian Select
        endian_options = [("Little Endian", "little"), ("Big Endian", "big")]
        initial_endian = field_def.get('endian', 'little') if field_def else 'little'
        endian_select = Select(endian_options, value=initial_endian, classes="field-endian-sel")
        endian_select.styles.width = "1fr"
        
        # Delete Button
        del_btn = Button("X", variant="error", id=f"del_field_{field_id}")
        del_btn.styles.width = "auto"
        
        row = Horizontal(
            field_name_input,
            type_select,
            endian_select,
            del_btn,
            id=f"field_row_{field_id}",
            classes="form-field-row"
        )
        row.styles.height = "auto"
        row.styles.align = ("left", "middle")
        row.styles.margin = (0, 0, 1, 0)
        
        return row

    async def add_field_row(self, field_def=None):
        container = self.query_one("#form_fields_list")
        row = self.create_field_row(field_def)
        await container.mount(row)

    async def cancel_form(self):
        self.is_editing = False
        if self.selected_cmd:
            await self.show_details()
        else:
            await self.show_welcome_message()

    async def delete_selected(self):
        if not self.selected_cmd:
            return
            
        cmd = self.selected_cmd
        name = cmd['name']
        msg_id = cmd['msg_id']
        direction = cmd['direction']
        
        if direction == 'tx':
            if name in self.app.controller.format_loader.commands:
                del self.app.controller.format_loader.commands[name]
        else:
            if msg_id in self.app.controller.format_loader.rx_messages:
                del self.app.controller.format_loader.rx_messages[msg_id]
                
        # Save back to file
        self.app.controller.format_loader.save_all()
        self.app.notify(f"Deleted {name}")
        
        # Reload
        self.load_commands()
        await self.show_welcome_message()
        
        # Update config screen
        self.update_other_screens()

    async def save_form(self):
        name_input = self.query_one("#form_name").value.strip()
        msg_id_input = self.query_one("#form_msg_id").value.strip()
        direction = self.query_one("#form_dir").value
        
        if not name_input:
            self.app.notify("Command Name cannot be empty.", severity="error")
            return
        
        # Parse MSG ID
        try:
            if msg_id_input.lower().startswith("0x"):
                msg_id = int(msg_id_input, 16)
            else:
                msg_id = int(msg_id_input)
        except ValueError:
            self.app.notify("Invalid Message ID. Must be integer or hex (e.g. 0x10).", severity="error")
            return
            
        # Parse payload fields
        payload = []
        for row in self.query(".form-field-row"):
            f_name = row.query_one(".field-name-in").value.strip()
            f_type = row.query_one(".field-type-sel").value
            f_endian = row.query_one(".field-endian-sel").value
            
            if not f_name:
                continue
                
            payload.append({
                'name': f_name,
                'type': f_type,
                'endian': f_endian
            })
            
        # If we are editing, delete the old one first in case name or ID changed
        if not self.selected_cmd:
            # Adding new
            pass
        else:
            old_name = self.selected_cmd['name']
            old_id = self.selected_cmd['msg_id']
            old_dir = self.selected_cmd['direction']
            
            if old_dir == 'tx':
                if old_name in self.app.controller.format_loader.commands:
                    del self.app.controller.format_loader.commands[old_name]
            else:
                if old_id in self.app.controller.format_loader.rx_messages:
                    del self.app.controller.format_loader.rx_messages[old_id]
                    
        # Construct command definition
        new_def = {
            'name': name_input,
            'msg_id': msg_id,
            'direction': direction,
            'payload': payload
        }
        
        # Add to correct list
        if direction == 'tx':
            self.app.controller.format_loader.commands[name_input] = new_def
        else:
            self.app.controller.format_loader.rx_messages[msg_id] = new_def
            
        # Save back to file
        self.app.controller.format_loader.save_all()
        self.app.notify(f"Saved {name_input}")
        
        # Reset editing state
        self.is_editing = False
        
        # Reload
        self.load_commands()
        
        # Find new item and show details
        self.selected_cmd = new_def
        await self.show_details()
        
        # Update config screen
        self.update_other_screens()

    def update_other_screens(self):
        try:
            config_scr = self.app.get_screen("config")
            config_scr.update_commands()
        except Exception:
            pass
