class ValueMapper:
    """
    Translates raw numeric packet values to meaningful string labels,
    and vice-versa, using the lookup maps loaded from YAML configs.
    """
    def __init__(self, loader):
        """
        Initialize the ValueMapper with a FormatLoader.
        """
        self.loader = loader

    def map_value(self, value, field_def):
        """
        Translate a raw numeric value to a string description if a map or enum is defined.
        
        Args:
            value: Raw numeric data value.
            field_def: Dictionary defining the field specification.
            
        Returns:
            Mapped string description, or the raw value itself if no mapping is found.
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
        Translate a user-provided string back to its corresponding numeric value for packing.
        
        Args:
            value_str: The input string or custom number string to convert.
            field_def: Dictionary defining the field specification.
            
        Returns:
            Mapped numeric representation.
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

