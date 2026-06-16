class ValueMapper:
    def __init__(self, loader):
        self.loader = loader

    def map_value(self, value, field_def):
        """
        Map a raw numeric value to a string if map or enum is defined.
        """
        # Check for enum
        if 'enum' in field_def:
            enum_map = field_def['enum']
            return enum_map.get(value, f"UNKNOWN({value})")
            
        # Check for map (from maps.yaml)
        if 'map' in field_def:
            map_name = field_def['map']
            mapping = self.loader.get_map(map_name)
            return mapping.get(value, f"UNKNOWN({value})")
            
        return value

    def unmap_value(self, value_str, field_def):
        """
        Map a string back to a numeric value for packing.
        """
        if 'enum' in field_def:
            enum_map = field_def['enum']
            # Reverse lookup
            for val, label in enum_map.items():
                if str(label) == str(value_str):
                    return val
            # Try to convert to int if it's a number string
            try:
                return int(value_str)
            except (ValueError, TypeError):
                return 0
                
        if 'map' in field_def:
            map_name = field_def['map']
            mapping = self.loader.get_map(map_name)
            for val, label in mapping.items():
                if str(label) == str(value_str):
                    return val
            try:
                return int(value_str, 0) # handles 0x prefixes
            except (ValueError, TypeError):
                return 0

        try:
            return int(value_str, 0)
        except (ValueError, TypeError):
            try:
                return float(value_str)
            except (ValueError, TypeError):
                return 0
