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

    def _parse_scalar(self, field: dict, payload: bytes, offset: int):
        type_str = field['type']
        endian = field.get('endian', 'little')

        if type_str == 'bytes':
            size = field.get('length', 0)
            if offset + size > len(payload):
                raise ValueError(
                    f"Field '{field['name']}' requires {size} bytes at offset {offset}, "
                    f"but payload has only {len(payload) - offset} bytes remaining"
                )
            return payload[offset:offset + size], size

        fmt, size = self.TYPE_MAP.get(type_str, ('B', 1))
        if offset + size > len(payload):
            raise ValueError(
                f"Field '{field['name']}' requires {size} bytes at offset {offset}, "
                f"but payload has only {len(payload) - offset} bytes remaining"
            )

        prefix = '<' if endian == 'little' else '>'
        return struct.unpack_from(f"{prefix}{fmt}", payload, offset)[0], size

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

            if type_str == 'array':
                results[name] = []
                fields_def = field.get('fields', [])
                if not fields_def:
                    continue

                record_count = field.get('count')
                if record_count is None and 'count_field' in field:
                    record_count = results.get(field['count_field'])
                    if record_count is None:
                        raise ValueError(
                            f"Array '{name}' depends on missing count field '{field['count_field']}'"
                        )

                record_size = 0
                for f in fields_def:
                    if f['type'] == 'bytes':
                        record_size += f.get('length', 0)
                    else:
                        record_size += self.TYPE_MAP.get(f['type'], ('B', 1))[1]

                while record_count is None or len(results[name]) < record_count:
                    if offset + record_size > len(payload):
                        if record_count is None:
                            break
                        raise ValueError(
                            f"Array '{name}' expects {record_count} record(s), "
                            f"but payload ended after {len(results[name])} record(s)"
                        )

                    record = {}
                    for f in fields_def:
                        value, size = self._parse_scalar(f, payload, offset)
                        record[f['name']] = value
                        offset += size
                    results[name].append(record)
                continue

            value, size = self._parse_scalar(field, payload, offset)
            results[name] = value
            offset += size

        if offset != len(payload):
            raise ValueError(
                f"Payload length mismatch for '{msg_def.get('name', 'unknown')}' "
                f"(parsed {offset} / {len(payload)} bytes)"
            )

        return results
