import struct
from uart.crc import crc16_modbus

HEAD_1 = 0xAA
HEAD_2 = 0x55

class FrameCodec:
    @staticmethod
    def pack(msg_id: int, payload: bytes) -> bytes:
        length = len(payload)
        # Header + msg_id + length
        header = struct.pack('BBBB', HEAD_1, HEAD_2, msg_id, length)
        # Entire data for CRC (msg_id + length + payload)
        # Actually, common practice is CRC over MSG_ID, LEN, and PAYLOAD
        # The user didn't specify what CRC covers. Usually it's everything after headers or everything.
        # Let's assume CRC covers MSG_ID, LEN, and PAYLOAD.
        crc_data = struct.pack('BB', msg_id, length) + payload
        crc = crc16_modbus(crc_data)
        
        return header + payload + struct.pack('<H', crc)

    def __init__(self):
        self.buffer = bytearray()

    def unpack(self, data: bytes):
        """
        Unpack stream of bytes. Returns a list of (msg_id, payload) tuples.
        """
        self.buffer.extend(data)
        messages = []
        
        while len(self.buffer) >= 6:  # Min length: HEAD1, HEAD2, MSG_ID, LEN, CRC_L, CRC_H (6 bytes for 0 payload)
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
                
        return messages
