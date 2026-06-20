def cobs_encode(data: bytes) -> bytes:
    """
    Encode a byte string using Consistent Overhead Byte Stuffing (COBS).
    Returns the encoded byte string, ending with a 0x00 delimiter byte.
    """
    encoded = bytearray()
    block = bytearray()
    for b in data:
        if b == 0:
            encoded.append(len(block) + 1)
            encoded.extend(block)
            block.clear()
        else:
            block.append(b)
            if len(block) == 254:
                encoded.append(0xFF)
                encoded.extend(block)
                block.clear()
    encoded.append(len(block) + 1)
    encoded.extend(block)
    encoded.append(0x00) # Frame delimiter
    return bytes(encoded)

def cobs_decode(data: bytes) -> bytes:
    """
    Decode a COBS-encoded byte string.
    Expects data without the trailing 0x00 delimiter (or handles it if present).
    """
    if not data:
        return b""
    if data[-1] == 0x00:
        data = data[:-1]
    
    decoded = bytearray()
    idx = 0
    while idx < len(data):
        code = data[idx]
        if code == 0:
            raise ValueError("Zero byte found in COBS encoded data (excluding delimiter)")
        idx += 1
        block_len = code - 1
        if idx + block_len > len(data):
            raise ValueError("Truncated COBS frame")
        decoded.extend(data[idx:idx+block_len])
        idx += block_len
        if code < 0xFF and idx < len(data):
            decoded.append(0x00)
    return bytes(decoded)
