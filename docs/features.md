# Danh Sách Các Tính Năng Đã Hoàn Thành (ECU Configurator Features)

Tài liệu này tổng hợp chi tiết các tính năng đã được thiết kế, lập trình và xác minh thành công trong ứng dụng **ECU Configurator Desktop App**.

---

## 1. Kiến Trúc Phân Lớp Chuẩn (Architecture)
* **Phân Tách Mối Quan Tâm (Separation of Concerns)**: Mã nguồn được chia nhỏ thành các tầng rõ rệt:
  - **Tầng Giao Diện (UI)**: [app/main.py](file:///d:/Projects/ConfigApp/app/main.py)
  - **Tầng Nghiệp Vụ (Service)**: [app/services/ecu_service.py](file:///d:/Projects/ConfigApp/app/services/ecu_service.py)
  - **Tầng Giao Tiếp UART (Serial)**: [app/serial_comm/](file:///d:/Projects/ConfigApp/app/serial_comm/)
  - **Tầng Lưu Trữ (Storage)**: [app/storage/file_manager.py](file:///d:/Projects/ConfigApp/app/storage/file_manager.py)
  - **Tầng Xác Thực Dữ Liệu (Models)**: [app/models/config_model.py](file:///d:/Projects/ConfigApp/app/models/config_model.py)
  - **Tầng Tiện Ích (Utils)**: [app/utils/logger.py](file:///d:/Projects/ConfigApp/app/utils/logger.py)
* **Khả năng Bảo Trì Cao**: Các tầng kết nối với nhau thông qua interface và cơ chế callback rõ ràng, dễ dàng thay thế giao diện hoặc giao thức truyền tin mà không làm ảnh hưởng đến các tầng khác.

---

## 2. Giao Diện Người Dùng Hiện Đại (CustomTkinter GUI)
* **Thiết Kế Dashboard Đẳng Cấp**: Sử dụng thư viện `customtkinter` tạo giao diện hiện đại với màu sắc hài hòa, hỗ trợ chế độ tự động chuyển đổi Sáng/Tối (Dark/Light mode) dựa trên cấu hình hệ thống.
* **Bảng Cấu Hình Cổng Nối Tiếp (Serial Connection Panel)**:
  - Tự động quét và liệt kê danh sách các cổng Serial/COM vật lý hoặc giả lập có sẵn trên máy.
  - Cho phép người dùng tùy chọn cổng kết nối và tốc độ Baudrate (từ 9600 đến 115200 bps).
  - Đèn LED trạng thái trực quan: Màu đỏ khi chưa kết nối, tự động chuyển sang màu xanh lá cây khi kết nối thành công.
* **Khung Nhập Thông Số Cấu Hình ECU**:
  - Nhập Device ID (giới hạn 1 - 255).
  - Chọn chế độ hoạt động: `normal`, `eco`, `sport`, `diagnostic`.
  - Nhập chu kỳ cập nhật dữ liệu (ms).
  - Các ngưỡng cảnh báo nhiệt độ cao/nhiệt độ thấp (°C) và điện áp cao/điện áp thấp (Volt).
* **Nút Điều Khiển Tối Ưu Hóa**:
  - Nút **"Nạp Cấu Hình"** và **"Khởi Động Lại ECU"** được xếp nằm song song trên cùng một hàng để giao diện gọn gàng và thẩm mỹ hơn.
  - Tự động vô hiệu hóa (disable) các nút tương tác thiết bị khi chưa mở cổng kết nối thành công để tránh lỗi hệ thống.

---

## 3. Quản Lý File Cấu Hình Linh Hoạt (YAML & JSON)
* **Cấu Hình Khởi Chạy Từ File**: Ứng dụng nạp toàn bộ cấu hình mặc định (bao gồm thông số cổng COM và cài đặt ECU) từ file [values.yml](file:///d:/Projects/ConfigApp/values.yml) nằm ở thư mục gốc.
* **Tính Năng "Lưu Cấu Hình" (Save)**: Cho phép ghi đè nhanh chóng toàn bộ thông số đang hiển thị trên form giao diện vào tệp tin đang mở hiện hành mà không cần hiển thị lại hộp thoại hỏi tên file.
* **Tính Năng "Lưu Mới..." (Save As)**: Mở hộp thoại (Save dialog) cho phép người dùng tự đặt tên file và chọn định dạng mong muốn (.yml, .yaml, hoặc .json).
* **Tính Năng "Nạp từ File..." (Import)**: Hỗ trợ người dùng mở bất kỳ tệp tin cấu hình nào để đưa thông số lên giao diện. Đặc biệt, nếu file đó chứa thông số cấu hình cổng Serial, hệ thống sẽ tự động đồng bộ cả cài đặt kết nối.
* **Tiêu Đề Động**: Tiêu đề ứng dụng tự động hiển thị tên file cấu hình hiện tại đang làm việc, ví dụ: `Hệ Thống Cấu Hình ECU - [my_config.yml]`.

---

## 4. Giao Tiếp UART Bất Đồng Bộ & Mã Lỗi CRC-16 Modbus
* **Đóng Gói Gói Tin Nhị Phân**: Mã hóa thông số thành chuỗi byte có cấu trúc rõ ràng:
  `[HEADER (0xAA)] [LENGTH] [COMMAND] [PAYLOAD] [CRC16 Modbus] [END (0x55)]`
  - Đã xử lý loại bỏ hoàn toàn đệm dữ liệu (padding) nhị phân nhờ sử dụng định dạng đóng gói không căn chỉnh `<` của struct.
* **Bảo Vệ Tính Toàn Vẹn Bằng CRC16**: Tích hợp thuật toán tính CRC-16 Modbus (đa thức `0xA001`) để đảm bảo dữ liệu không bị sai lệch trong quá trình truyền dẫn.
* **Xử Lý Bất Đồng Bộ (Non-blocking UI)**:
  - Khởi chạy một luồng chạy ngầm riêng biệt (`SerialReaderThread`) chuyên lắng nghe và ghép dòng byte nhận được từ cổng Serial thành gói tin hoàn chỉnh.
  - Sử dụng cơ chế đồng bộ `threading.Event` giúp luồng giao diện có thể gửi lệnh cấu hình xuống và chờ phản hồi ACK/NACK đồng bộ trong một khoảng thời gian chờ (timeout) định trước mà không làm đơ giao diện đồ họa.

---

## 5. Giám Sát Thời Gian Thực & Logs Hệ Thống
* **Bảng Giám Sát Thời Gian Thực (Realtime Monitor)**:
  - Hiển thị các thông số đo đạc thực tế từ ECU gửi lên bao gồm: Nhiệt độ hiện tại (°C), Điện áp hiện tại (Volt), thời gian ECU đã hoạt động liên tục (Uptime giây).
  - Tự động nhận diện và cảnh báo mã lỗi bằng màu sắc trực quan (màu xanh lá khi bình thường `0x00`, màu đỏ khi xuất hiện lỗi).
* **Tích Hợp Khung Hiển Thị Log (Console Log)**:
  - Tự động bắt và chuyển hướng toàn bộ luồng log hệ thống lên cửa sổ giao diện chính.
  - Được xử lý luồng an toàn (thread-safe) thông qua phương thức hàng đợi của Tkinter để tránh xung đột tài nguyên giữa luồng đọc Serial và luồng giao diện chính.
  - Tích hợp nút **"Xóa Log"** để xóa trắng màn hình log khi cần.
  - Log hoạt động cũng được ghi đồng thời vào file xoay vòng cục bộ `logs/app.log` để phục vụ chẩn đoán lỗi.

---

## 6. Xác Thực Chặt Chẽ & Kiểm Thử Tự Động (Validation & Tests)
* **Xác Thực Đầu Vào Bằng Pydantic**: Sử dụng Pydantic v2 để tự động kiểm tra định dạng và khoảng dữ liệu nhập vào:
  - Device ID: `1` đến `255`.
  - Baudrate: Phải thuộc tập hợp baudrate chuẩn.
  - Ngưỡng cảnh báo: Tự động chạy bộ kiểm tra chéo `@model_validator(mode="after")` để bắt lỗi nếu ngưỡng cảnh báo cao thiết lập nhỏ hơn hoặc bằng ngưỡng cảnh báo thấp.
* **Bộ Kiểm Thử Tự Động (Unit Tests)**:
  - Viết sẵn 12 ca kiểm thử tự động bằng `pytest` trong thư mục `tests/` để kiểm tra toàn diện quá trình tính toán CRC, mã hóa/giải mã luồng byte và xác thực dữ liệu của các model cấu hình.
