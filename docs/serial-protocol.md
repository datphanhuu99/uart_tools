# Giao Thức Truyền Thông Serial (UART) ECU

Tài liệu này đặc tả định dạng gói tin nhị phân truyền thông giữa Ứng dụng Desktop và ECU.

## 1. Định Dạng Khung Gói Tin (Packet Frame Format)

Mọi gói tin truyền nhận qua cổng Serial đều tuân thủ cấu trúc khung cố định dưới đây để đảm bảo khả năng đồng bộ và phát hiện lỗi đường truyền:

| Thành phần | Độ dài (Bytes) | Giá trị | Mô tả |
| :--- | :---: | :---: | :--- |
| **HEADER** | 1 | `0xAA` | Byte đánh dấu bắt đầu gói tin (Start of Frame) |
| **LENGTH** | 1 | `1 + N` | Độ dài của vùng `COMMAND` + `PAYLOAD` (tính bằng byte) |
| **COMMAND** | 1 | *Biến đổi* | Mã lệnh yêu cầu hoặc loại phản hồi (Command ID) |
| **PAYLOAD** | N | *Biến đổi* | Dữ liệu kèm theo lệnh (chứa các thông số cấu hình hoặc trạng thái) |
| **CRC16** | 2 | *Biến đổi* | Mã kiểm tra lỗi CRC-16 Modbus (Thứ tự byte: Little Endian) |
| **END** | 1 | `0x55` | Byte đánh dấu kết thúc gói tin (End of Frame) |

---

## 2. Danh Sách Lệnh và Phản Hồi (Command IDs)

| Mã Lệnh (Hex) | Tên Lệnh | Hướng Truyền | Mô tả |
| :---: | :--- | :---: | :--- |
| `0x01` | **SET_CONFIG** | App → ECU | Gửi các thông số cấu hình mới yêu cầu ECU lưu tạm. |
| `0x02` | **GET_CONFIG** | Song hướng | **App → ECU**: Yêu cầu đọc cấu hình.<br>**ECU → App**: Trả về cấu hình hiện tại trong payload. |
| `0x03` | **SAVE_CONFIG** | App → ECU | Yêu cầu ECU ghi vĩnh viễn cấu hình hiện tại vào bộ nhớ Flash/EEPROM. |
| `0x04` | **READ_STATUS** | ECU → App | Gửi dữ liệu trạng thái thời gian thực của ECU (chu kỳ hoặc theo yêu cầu). |
| `0x05` | **REBOOT_ECU** | App → ECU | Yêu cầu ECU khởi động lại thiết bị. |
| `0x06` | **ACK** | ECU → App | Phản hồi xác nhận thực thi lệnh trước đó thành công. |
| `0x15` | **NACK** | ECU → App | Phản hồi báo lỗi/từ chối thực thi lệnh (Ví dụ: sai tham số, sai CRC). |

---

## 3. Chi Tiết Payload Các Lệnh

Kiểu đóng gói nhị phân sử dụng định dạng Byte-Order: **Little Endian (kiểu dữ liệu x86/ARM tiêu chuẩn)**.

### 3.1. Lệnh SET_CONFIG (`0x01`) & Phản hồi GET_CONFIG (`0x02`)
Độ dài Payload cố định: **20 bytes**

| Vị trí (Offset) | Trường dữ liệu | Kiểu dữ liệu | Mô tả |
| :---: | :--- | :---: | :--- |
| 0 | `device_id` | `uint8` | ID của ECU (1 - 255) |
| 1 | `mode` | `uint8` | Chế độ: `0` (Normal), `1` (Eco), `2` (Sport), `3` (Diag) |
| 2 - 3 | `update_interval_ms`| `uint16` | Chu kỳ gửi bản tin trạng thái (mili giây) |
| 4 - 7 | `temp_threshold_high`| `float` | Ngưỡng nhiệt độ cao cảnh báo (°C) |
| 8 - 11 | `temp_threshold_low` | `float` | Ngưỡng nhiệt độ thấp cảnh báo (°C) |
| 12 - 15| `voltage_threshold_high`| `float`| Ngưỡng điện áp cao cảnh báo (V) |
| 16 - 19| `voltage_threshold_low` | `float`| Ngưỡng điện áp thấp cảnh báo (V) |

### 3.2. Lệnh READ_STATUS (`0x04`)
Độ dài Payload cố định: **13 bytes**

| Vị trí (Offset) | Trường dữ liệu | Kiểu dữ liệu | Mô tả |
| :---: | :--- | :---: | :--- |
| 0 - 3 | `temperature` | `float` | Nhiệt độ hiện tại của ECU (°C) |
| 4 - 7 | `voltage` | `float` | Điện áp hiện tại đo được (V) |
| 8 - 11 | `uptime_seconds` | `uint32` | Thời gian ECU hoạt động liên tục (giây) |
| 12 | `error_code` | `uint8` | Mã lỗi hiện tại: `0x00` (OK), các giá trị khác đại diện mã lỗi cụ thể |

---

## 4. Thuật Toán Tính Toán CRC-16 Modbus

Thuật toán CRC-16 sử dụng đa thức sinh `0xA001` (Modbus). Dữ liệu đầu vào để tính toán CRC bao gồm các byte từ trường **LENGTH** đến hết trường **PAYLOAD** (bỏ qua `HEADER`, `CRC16` và `END`).

### Mã giả thuật toán (Python):
```python
def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF
```
Gói tin gửi đi sẽ chứa byte thấp của CRC trước, sau đó tới byte cao (Little Endian).
