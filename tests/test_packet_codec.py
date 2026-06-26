import pytest
from app.serial_comm.protocol import PacketCodec, ECUCommand, Packet

def test_crc16_calculation():
    # Test tính toán CRC với một chuỗi cố định
    data = b"\x05\x01\x01\x00\x0a\x00" # length, command, payload
    crc = PacketCodec.calculate_crc16(data)
    assert isinstance(crc, int)
    assert 0 <= crc <= 0xFFFF

def test_packet_encoding():
    # Kiểm tra đóng gói lệnh đơn giản không có payload
    encoded = PacketCodec.encode(ECUCommand.GET_CONFIG)
    assert encoded[0] == PacketCodec.HEADER
    assert encoded[-1] == PacketCodec.END
    # Length byte (byte 1) phải là 1 vì chỉ có mã lệnh GET_CONFIG (1 byte) và không có payload
    assert encoded[1] == 1 
    assert encoded[2] == ECUCommand.GET_CONFIG

def test_packet_decoding_valid():
    # Đóng gói và giải mã để kiểm tra tính nhất quán
    payload = b"\x01\x02\x03\x04"
    encoded = PacketCodec.encode(ECUCommand.SET_CONFIG, payload)
    
    buffer = bytearray(encoded)
    packet, bytes_processed = PacketCodec.decode_stream(buffer)
    
    assert packet is not None
    assert packet.command_id == ECUCommand.SET_CONFIG
    assert packet.payload == payload
    assert bytes_processed == len(encoded)

def test_packet_decoding_fragmented():
    # Kiểm tra giải mã gói tin bị chia nhỏ thành nhiều phần truyền về
    payload = b"\x10\x20"
    encoded = PacketCodec.encode(ECUCommand.READ_STATUS, payload)
    
    # Gửi một nửa gói tin trước
    buffer = bytearray(encoded[:4])
    packet, bytes_processed = PacketCodec.decode_stream(buffer)
    assert packet is None
    assert bytes_processed == 0
    
    # Gửi nửa còn lại
    buffer.extend(encoded[4:])
    packet, bytes_processed = PacketCodec.decode_stream(buffer)
    assert packet is not None
    assert packet.command_id == ECUCommand.READ_STATUS
    assert packet.payload == payload
    assert bytes_processed == len(encoded)

def test_packet_decoding_corrupted_crc():
    payload = b"\x01\x02"
    encoded = bytearray(PacketCodec.encode(ECUCommand.SET_CONFIG, payload))
    
    # Làm hỏng byte CRC
    encoded[5] ^= 0xFF 
    
    buffer = bytearray(encoded)
    packet, bytes_processed = PacketCodec.decode_stream(buffer)
    
    # Do lỗi CRC, gói tin phải bị từ chối
    assert packet is None
    # Trả về bytes_processed = 1 (bỏ qua byte HEADER sai để đồng bộ tiếp)
    assert bytes_processed == 1
