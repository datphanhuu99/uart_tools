import yaml
import os

class FormatLoader:
    def __init__(self, formats_dir: str):
        self.formats_dir = formats_dir
        self.commands = {}
        self.rx_messages = {}
        self.maps = {}

    def load_all(self):
        self.maps = self._load_yaml('maps.yaml')
        
        commands_list = self._load_yaml('commands.yaml')
        if isinstance(commands_list, list):
            self.commands = {cmd['name']: cmd for cmd in commands_list}
        elif isinstance(commands_list, dict):
            self.commands = commands_list
            
        rx_list = self._load_yaml('rx_messages.yaml')
        if isinstance(rx_list, list):
            self.rx_messages = {msg['msg_id']: msg for msg in rx_list}
        elif isinstance(rx_list, dict):
            # If msg_id is the key
            self.rx_messages = rx_list

    def _load_yaml(self, filename: str):
        path = os.path.join(self.formats_dir, filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}

    def get_command(self, name: str):
        return self.commands.get(name)

    def get_rx_message(self, msg_id: int):
        return self.rx_messages.get(msg_id)
        
    def get_map(self, map_name: str):
        return self.maps.get(map_name, {})
