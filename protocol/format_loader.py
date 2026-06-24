import yaml
import os

class FormatLoader:
    """
    Loads, processes, and persists YAML format specification definitions 
    for commands, rx_messages, and values lookup tables (maps.yaml).
    """
    def __init__(self, formats_dir: str):
        """
        Initialize format files directory paths.
        
        Args:
            formats_dir: Root directory containing yaml files.
        """
        self.formats_dir = formats_dir
        self.commands = {}
        self.rx_messages = {}
        self.rx_message_variants = {}
        self.maps = {}

    def load_all(self):
        """
        Load commands, messages, and map definition dictionaries from files.
        """
        self.maps = self._load_yaml('maps.yaml')
        
        commands_list = self._load_yaml('commands.yaml')
        if isinstance(commands_list, list):
            self.commands = {cmd['name']: cmd for cmd in commands_list}
        elif isinstance(commands_list, dict):
            self.commands = commands_list
            
        rx_list = self._load_yaml('rx_messages.yaml')
        if isinstance(rx_list, list):
            self.rx_message_variants = {}
            for msg in rx_list:
                self.rx_message_variants.setdefault(msg['msg_id'], []).append(msg)
            self.rx_messages = {
                msg_id: variants[0]
                for msg_id, variants in self.rx_message_variants.items()
            }
        elif isinstance(rx_list, dict):
            # If msg_id is the key
            self.rx_messages = rx_list
            self.rx_message_variants = {
                msg_id: [msg]
                for msg_id, msg in rx_list.items()
            }

    def _load_yaml(self, filename: str):
        """
        Helper method to deserialize a single YAML file safely.
        """
        path = os.path.join(self.formats_dir, filename)
        if not os.path.exists(path):
            return {}
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}

    def get_command(self, name: str):
        """
        Get TX command definition by name.
        """
        return self.commands.get(name)

    def get_rx_message(self, msg_id: int, payload_len: int | None = None):
        """
        Get RX message definition by Msg ID.
        """
        variants = self.rx_message_variants.get(msg_id, [])
        if not variants:
            return None

        if payload_len is None or len(variants) == 1:
            return variants[0]

        for variant in variants:
            expected_len = variant.get("payload_len")
            if expected_len == payload_len:
                return variant

        return variants[0]
        
    def get_map(self, map_name: str):
        """
        Get field value mappings/lookup tables by name.
        """
        return self.maps.get(map_name, {})

    def save_all(self):
        """
        Save current commands and rx_messages definitions to YAML files.
        """
        # Save TX commands
        commands_path = os.path.join(self.formats_dir, 'commands.yaml')
        commands_list = list(self.commands.values())
        with open(commands_path, 'w') as f:
            yaml.safe_dump(commands_list, f, sort_keys=False)
            
        # Save RX messages
        rx_path = os.path.join(self.formats_dir, 'rx_messages.yaml')
        rx_list = []
        for variants in self.rx_message_variants.values():
            rx_list.extend(variants)
        with open(rx_path, 'w') as f:
            yaml.safe_dump(rx_list, f, sort_keys=False)

