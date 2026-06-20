import struct

class Packer:
    """
    Serializes a dictionary of field values into structured raw binary payloads
    according to specified command templates.
    """
    TYPE_MAP = {
        'uint8': 'B',
        'int8': 'b',
        'uint16': 'H',
        'int16': 'h',
        'uint32': 'I',
        'int32': 'i',
        'float': 'f',
    }

    def pack(self, command_def: dict, values: dict) -> bytes:
        """
        Serialize input variables into binary byte sequences based on field rules.
        
        Args:
            command_def: Dictionary defining the template fields, types, and endianness.
            values: Key-value mapped parameters to pack.
            
        Returns:
            Packaged binary data payload.
        """
        payload_def = command_def.get('payload', [])
        packed_data = bytearray()
        
        for field in payload_def:
            name = field['name']
            type_str = field['type']
            endian = field.get('endian', 'little')
            
            value = values.get(name, 0)
            
            fmt = self.TYPE_MAP.get(type_str, 'B')
            prefix = '<' if endian == 'little' else '>'
            
            try:
                packed_data.extend(struct.pack(f"{prefix}{fmt}", value))
            except struct.error:
                # Default to 0 if packing fails
                packed_data.extend(struct.pack(f"{prefix}{fmt}", 0))
                
        return bytes(packed_data)

