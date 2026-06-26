# ECU Configurator Desktop App

Ứng dụng desktop viết bằng Python (sử dụng thư viện CustomTkinter) dùng để cấu hình thông số và giao tiếp dữ liệu thời gian thực với ECU qua cổng Serial/UART.

## 🚀 Tính năng chính

- Kết nối và cấu hình cổng Serial/UART (COM Port, Baudrate, Timeout...).
- Đọc và ghi các thông số cấu hình xuống ECU sử dụng định dạng gói tin chuẩn có kiểm tra lỗi CRC.
- Hiển thị dữ liệu thời gian thực (Realtime monitoring) từ ECU gửi lên thông qua luồng chạy nền (Background Thread) tránh treo giao diện.
- Lưu trữ cấu hình mặc định trong file `values.yml` và xuất nhập cấu hình ra file JSON/YAML cục bộ.
- Hệ thống log ghi nhận hoạt động và cảnh báo chi tiết.

## 📁 Cấu trúc thư mục dự án

```text
ConfigApp/
├── app/
│   ├── models/             # Định nghĩa cấu trúc dữ liệu cấu hình (Pydantic models)
│   ├── serial_comm/        # Logic giao tiếp Serial/UART và đóng gói giao thức
│   ├── services/           # Logic nghiệp vụ điều phối kết nối và nạp cấu hình
│   ├── storage/            # Xử lý đọc ghi file cấu hình cục bộ (JSON, YAML)
│   ├── utils/              # Các hàm tiện ích dùng chung (Logger, helper...)
│   └── main.py             # Điểm khởi chạy ứng dụng chính và giao diện GUI
├── config/                 # Thư mục cấu hình phụ (JSON defaults)
├── docs/                   # Tài liệu chi tiết dự án (Kiến trúc, Giao thức...)
├── tests/                  # Kiểm thử tự động (Unit and Integration tests)
├── requirements.txt        # Các thư viện phụ thuộc của dự án
├── values.yml              # File cấu hình mặc định của ứng dụng và ECU
├── AGENTS.md               # Hướng dẫn phát triển dành cho AI Agent
└── README.md               # Tài liệu này
```

## 🛠️ Hướng dẫn cài đặt và chạy thử

### Yêu cầu hệ thống
- Python 3.8 trở lên.
- Cáp kết nối USB-to-UART hoặc phần mềm mô phỏng cổng COM ảo (như VSPD) để test.

### Các bước thiết lập

1. **Tạo môi trường ảo Python (Virtual Environment):**
   ```bash
   python -m venv venv
   ```

2. **Kích hoạt môi trường ảo:**
   - Trên **Windows (Git Bash)**:
     ```bash
     source venv/Scripts/activate
     ```
   - Trên **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Trên **Linux/macOS**:
     ```bash
     source venv/bin/activate
     ```

3. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi chạy ứng dụng:**
   ```bash
   python app/main.py
   ```

## 🧪 Chạy Kiểm Thử (Testing)

Sử dụng `pytest` để chạy toàn bộ các bài viết kiểm thử có sẵn:
```bash
pytest
```

## 📖 Tài Liệu Tham Khảo Chi Tiết (Documentation)

Các tài liệu hướng dẫn kỹ thuật chi tiết của dự án (viết bằng Tiếng Việt):
- [Danh sách các tính năng đã làm](file:///d:/Projects/ConfigApp/docs/features.md): Báo cáo chi tiết toàn bộ các tính năng đã được thiết kế và kiểm thử thành công.
- [Kiến trúc ứng dụng](file:///d:/Projects/ConfigApp/docs/architecture.md): Giải thích sơ đồ luồng dữ liệu và thiết kế phân tách mối quan tâm.
- [Đặc tả giao thức Serial](file:///d:/Projects/ConfigApp/docs/serial-protocol.md): Chi tiết khung byte truyền nhận nhị phân, mã lệnh và thuật toán tính CRC-16.

