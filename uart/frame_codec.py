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
        else:
            # COBS packaging format: cmd(1B) + len(2B) + data(nB) + crc(1B or 2B)
            prefix = '>' if self.cobs_endian == 'big' else '<'
            header = struct.pack(f'{prefix}BH', msg_id, len(payload))
            packet_to_crc = header + payload
            
            # Calculate CRC
            if self.cobs_crc_type == "crc16_1b":
                crc_val = crc16_ccitt(packet_to_crc) & 0xFF
                crc_bytes = bytes([crc_val])
            elif self.cobs_crc_type == "crc16_2b":
                crc_val = crc16_ccitt(packet_to_crc)
                crc_bytes = struct.pack(f'{prefix}H', crc_val)
            elif self.cobs_crc_type == "crc8":
                crc_val = crc8_ccitt(packet_to_crc)
                crc_bytes = bytes([crc_val])
            elif self.cobs_crc_type == "checksum":
                crc_val = checksum8(packet_to_crc)
                crc_bytes = bytes([crc_val])
            else:
                crc_bytes = b""
                
            raw_packet = packet_to_crc + crc_bytes
            return cobs_encode(raw_packet)

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
            # COBS mode: packages end with 0x00
            while 0x00 in self.buffer:
                idx = self.buffer.index(0x00)
                frame = bytes(self.buffer[:idx + 1])
                del self.buffer[:idx + 1]
                
                if len(frame) <= 1:
                    continue  # consecutive 0x00 or empty frame
                
                try:
                    decoded = cobs_decode(frame)
                    crc_size = 2 if self.cobs_crc_type == "crc16_2b" else (0 if self.cobs_crc_type == "none" else 1)
                    min_len = 1 + 2 + crc_size
                    if len(decoded) < min_len:
                        continue
                    
                    cmd = decoded[0]
                    len_fmt = '>H' if self.cobs_endian == 'big' else '<H'
                    payload_len = struct.unpack(len_fmt, decoded[1:3])[0]
                    
                    if len(decoded) != 1 + 2 + payload_len + crc_size:
                        continue  # Length mismatch
                    
                    payload = decoded[3:3+payload_len]
                    received_crc = decoded[3+payload_len:3+payload_len+crc_size]
                    
                    # Verify CRC
                    packet_to_crc = decoded[0:3+payload_len]
                    if crc_size == 1:
                        if self.cobs_crc_type == "crc16_1b":
                            expected_crc = bytes([crc16_ccitt(packet_to_crc) & 0xFF])
                        elif self.cobs_crc_type == "crc8":
                            expected_crc = bytes([crc8_ccitt(packet_to_crc)])
                        else: # checksum
                            expected_crc = bytes([checksum8(packet_to_crc)])
                    elif crc_size == 2:
                        expected_crc = struct.pack(len_fmt, crc16_ccitt(packet_to_crc))
                    else:
                        expected_crc = b""
                        
                    if received_crc == expected_crc:
                        messages.append((cmd, payload))
                except Exception as e:
                    logger.debug("Failed to decode COBS packet: %s", e)
                    
        return messages

