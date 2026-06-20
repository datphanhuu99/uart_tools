import struct

class Parser:
    """
    Deserializes raw binary data payloads into structured dictionaries
    containing parsed field variables.
    """
    TYPE_MAP = {
        'uint8': ('B', 1),
        'int8': ('b', 1),
        'uint16': ('H', 2),
        'int16': ('h', 2),
        'uint32': ('I', 4),
        'int32': ('i', 4),
        'float': ('f', 4),
    }

    def parse(self, msg_def: dict, payload: bytes) -> dict:
        """
        Unpack binary bytes into structured data dictionary using message templates.
        
        Args:
            msg_def: Dictionary defining template fields, types, and endianness.
            payload: Inner payload bytes to deserialize.
            
        Returns:
            Dictionary mapped by field names to parsed numeric values.
        """
        payload_def = msg_def.get('payload', [])
        results = {}
        offset = 0
        
        for field in payload_def:
            name = field['name']
            type_str = field['type']
            endian = field.get('endian', 'little')
            
            fmt, size = self.TYPE_MAP.get(type_str, ('B', 1))
            
            if offset + size > len(payload):
                break
                
            prefix = '<' if endian == 'little' else '>'
            value = struct.unpack_from(f"{prefix}{fmt}", payload, offset)[0]
            results[name] = value
            offset += size
            
        return results

