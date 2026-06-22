import struct
import logging
from uart.crc import crc16_modbus, crc8_ccitt, checksum8, crc16_ccitt
from uart.cobs import cobs_encode, cobs_decode

HEAD_1 = 0xAA
HEAD_2 = 0x55

logger = logging.getLogger("FrameCodec")

class FrameCodec:
    """
    Codec class responsible for packaging and unpackaging binary data frames.
    Supports both legacy custom framing (HEAD1, HEAD2, MSG_ID, LEN, Payload, CRC16)
    and COBS-encoded framing with configurable checksum/CRC algorithm.
    """
    def __init__(self):
        """
        Initialize the FrameCodec with default protocol modes and configurations.
        """
        self.buffer = bytearray()
        self.protocol_mode = "cobs"  # "legacy" or "cobs"
        self.cobs_crc_type = "crc16_2b"  # "crc16_1b", "crc16_2b", "crc8", "checksum"
        self.cobs_endian = "big"       # "big" or "little"

    def pack(self, msg_id: int, payload: bytes) -> bytes:
        """
        Pack message ID and payload into a complete frame based on the active protocol mode.
        
        Args:
            msg_id: 1-byte command or message ID identifier.
            payload: Inner payload bytes of the message.
            
        Returns:
            The complete framed byte string ready to be transmitted over serial.
        """
        if self.protocol_mode == "legacy":
            length = len(payload)
            header = struct.pack('BBBB', HEAD_1, HEAD_2, msg_id, length)
            crc_data = struct.pack('BB', msg_id, length) + payload
            crc = crc16_modbus(crc_data)
            return header + payload + struct.pack('<H', crc)

        # Implemented MCU protocol is fixed to:
        # 0x00 + COBS(CMD + LEN_BE + PAYLOAD + CRC16_CCITT_FALSE_BE) + 0x00
        header = struct.pack(">BH", msg_id, len(payload))
        packet_to_crc = header + payload
        crc_bytes = struct.pack(">H", crc16_ccitt(packet_to_crc))
        raw_packet = packet_to_crc + crc_bytes
        return b"\x00" + cobs_encode(raw_packet)

    def unpack(self, data: bytes):
        """
        Ingest stream of raw bytes and unpack complete messages.
        
        Args:
            data: Raw input bytes received from transport.
            
        Returns:
            A list of tuples (msg_id, payload_bytes) representing decoded valid packets.
        """
        self.buffer.extend(data)
        messages = []
        
        if self.protocol_mode == "legacy":
            while len(self.buffer) >= 6:  # Min length: HEAD1, HEAD2, MSG_ID, LEN, CRC_L, CRC_H
                # Find HEAD_1
                try:
                    idx = self.buffer.index(HEAD_1)
                except ValueError:
                    self.buffer.clear()
                    break
                
                if idx > 0:
                    del self.buffer[:idx]
                
                if len(self.buffer) < 2:
                    break
                
                if self.buffer[1] != HEAD_2:
                    del self.buffer[0:1]
                    continue
                
                if len(self.buffer) < 4:
                    break
                
                msg_id = self.buffer[2]
                length = self.buffer[3]
                
                total_len = 4 + length + 2 # HEAD1, HEAD2, MSG_ID, LEN + PAYLOAD + CRC16
                
                if len(self.buffer) < total_len:
                    break
                
                payload = bytes(self.buffer[4:4+length])
                received_crc = struct.unpack('<H', self.buffer[4+length:total_len])[0]
                
                # Calculate CRC over msg_id, length, payload
                crc_data = struct.pack('BB', msg_id, length) + payload
                calculated_crc = crc16_modbus(crc_data)
                
                if received_crc == calculated_crc:
                    messages.append((msg_id, payload))
                    del self.buffer[:total_len]
                else:
                    # Invalid CRC, skip HEAD1 and search again
                    del self.buffer[0:1]
        else:
            while 0x00 in self.buffer:
                idx = self.buffer.index(0x00)
                frame = bytes(self.buffer[:idx])
                del self.buffer[:idx + 1]

                if not frame:
                    continue

                try:
                    decoded = cobs_decode(frame)
                    min_len = 1 + 2 + 2
                    if len(decoded) < min_len:
                        continue

                    cmd = decoded[0]
                    payload_len = struct.unpack(">H", decoded[1:3])[0]
                    expected_len = 1 + 2 + payload_len + 2
                    if len(decoded) != expected_len:
                        continue

                    payload = decoded[3:3 + payload_len]
                    received_crc = decoded[3 + payload_len:expected_len]
                    packet_to_crc = decoded[:3 + payload_len]
                    expected_crc = struct.pack(">H", crc16_ccitt(packet_to_crc))

                    if received_crc == expected_crc:
                        messages.append((cmd, payload))
                except Exception as e:
                    logger.debug("Failed to decode COBS packet: %s", e)

        return messages
