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
