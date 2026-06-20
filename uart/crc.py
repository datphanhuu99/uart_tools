def crc16_modbus(data: bytes) -> int:
    """
    Calculate CRC-16-MODBUS for the given data.
    Polynomial: 0x8005 (x^16 + x^15 + x^2 + 1), LSB first.
    Initial value: 0xFFFF.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF

def crc8_ccitt(data: bytes) -> int:
    """
    Calculate CRC-8-CCITT for the given data.
    Polynomial: 0x07 (x^8 + x^2 + x + 1).
    Initial value: 0x00.
    """
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

def checksum8(data: bytes) -> int:
    """
    Simple 8-bit checksum (sum of bytes modulo 256).
    """
    return sum(data) & 0xFF
