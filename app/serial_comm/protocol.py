import struct
from enum import IntEnum
from typing import NamedTuple, Optional, Tuple

class ECUCommand(IntEnum):
    SET_CONFIG = 0x01
    GET_CONFIG = 0x02
    SAVE_CONFIG = 0x03
    READ_STATUS = 0x04
    REBOOT_ECU = 0x05
    ACK = 0x06
    NACK = 0x15

class Packet(NamedTuple):
    command_id: int
    payload: bytes

class PacketCodec:
    """
    Mã hóa và giải mã các gói tin giao tiếp với ECU.
    Định dạng gói tin: [HEADER (1B)][LENGTH (1B)][COMMAND (1B)][PAYLOAD (N B)][CRC16 (2B)][END (1B)]
    HEADER = 0xAA
    END = 0x55
    LENGTH = Độ dài của [COMMAND] + [PAYLOAD]
    """
    HEADER = 0xAA
    END = 0x55

    @staticmethod
    def calculate_crc16(data: bytes) -> int:
        """
        Tính toán CRC-16 Modbus (Đa thức: 0xA001, Giá trị khởi tạo: 0xFFFF).
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

    @classmethod
    def encode(cls, command: int, payload: bytes = b"") -> bytes:
        """
        Mã hóa lệnh và dữ liệu thành gói tin nhị phân.
        """
        length = 1 + len(payload) # COMMAND + PAYLOAD
        # Dữ liệu dùng để tính toán CRC gồm: LENGTH + COMMAND + PAYLOAD
        crc_data = bytes([length, command]) + payload
        crc = cls.calculate_crc16(crc_data)
        
        # Đóng gói gói tin
        # format: B (Header) + B (Length) + B (Command) + payload + H (CRC16 - Little Endian) + B (End)
        packet = struct.pack(f"<BBB{len(payload)}sHB", cls.HEADER, length, command, payload, crc, cls.END)
        return packet

    @classmethod
    def decode_stream(cls, buffer: bytearray) -> Tuple[Optional[Packet], int]:
        """
        Phân tích dòng byte nhận được trong buffer để tìm gói tin hợp lệ.
        Trả về: (Packet, bytes_to_discard)
        - Nếu tìm thấy gói tin hợp lệ: trả về (Packet, số_byte_đã_tiêu_thụ)
        - Nếu chưa đủ dữ liệu: trả về (None, 0)
        - Nếu phát hiện gói tin lỗi/không hợp lệ: trả về (None, số_byte_cần_bỏ_qua_để_đồng_bộ)
        """
        if len(buffer) < 6: # Tối thiểu: HEADER(1) + LENGTH(1) + CMD(1) + CRC(2) + END(1) = 6 bytes
            return None, 0

        # Tìm kiếm byte HEADER
        try:
            header_idx = buffer.index(cls.HEADER)
        except ValueError:
            # Không tìm thấy HEADER, loại bỏ toàn bộ dữ liệu trong buffer
            return None, len(buffer)

        # Nếu HEADER không nằm ở đầu buffer, loại bỏ phần dữ liệu thừa phía trước
        if header_idx > 0:
            return None, header_idx

        # Đã tìm thấy HEADER ở đầu buffer, kiểm tra trường LENGTH
        length = buffer[1]
        expected_packet_len = 1 + 1 + length + 2 + 1 # HEADER + LENGTH + (CMD + PAYLOAD) + CRC16 + END

        # Chưa nhận đủ độ dài của toàn bộ gói tin dự kiến
        if len(buffer) < expected_packet_len:
            return None, 0

        # Kiểm tra byte END
        if buffer[expected_packet_len - 1] != cls.END:
            # Gói tin không kết thúc bằng byte END hợp lệ, loại bỏ byte HEADER hiện tại để tìm kiếm tiếp
            return None, 1

        # Trích xuất các trường dữ liệu để kiểm tra CRC
        cmd = buffer[2]
        payload = bytes(buffer[3 : 2 + length])
        crc_received = struct.unpack("<H", buffer[2 + length : 2 + length + 2])[0]

        # Kiểm tra tính toàn vẹn bằng CRC
        crc_data = bytes([length, cmd]) + payload
        crc_calculated = cls.calculate_crc16(crc_data)

        if crc_calculated != crc_received:
            # Lỗi CRC, bỏ qua byte HEADER này để đồng bộ lại ở byte tiếp theo
            return None, 1

        # Gói tin hoàn toàn hợp lệ
        packet = Packet(command_id=cmd, payload=payload)
        return packet, expected_packet_len
