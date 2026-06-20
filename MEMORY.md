# Project Memory (Global Context)

> **Hướng dẫn:** Đây là bộ nhớ dài hạn, lưu trữ phong cách, sở thích và kinh nghiệm của người dùng.
> Agent PHẢI đọc file này vào đầu mỗi phiên làm việc (Session Start).

## 1. User Preferences (Sở thích cá nhân)
- **Coding Style:** [Cập nhật tại đây]
- **Review Style:** [Cập nhật tại đây]
- **Tools/Automation:** [Cập nhật tại đây]

## 2. Lessons Learned (Rút kinh nghiệm)
- **Mistakes:** 
  - Gọi `.mount()` trên các widget chưa được mount (trong Textual) gây ra `MountError`. Khắc phục bằng cách sử dụng Declarative UI hoặc khởi tạo widget con qua constructor.
  - Sử dụng thuộc tính cũ (`self.app.format_loader`) sau khi refactor thay vì `self.app.controller.format_loader` dẫn đến `AttributeError`. Khắc phục bằng tìm kiếm toàn cục trước khi chỉnh sửa.
- **Feedback:** Luôn kiểm tra sơ đồ thuộc tính và vòng đời thư viện trước khi viết code.

## 3. Proactive Suggestions (Đề xuất chủ động)
- **Suggested Tools:** [Tools cần tạo để tăng tốc]
- **Suggested Skills:** [Skills cần tạo/kích hoạt]
- **Rules Updates:** [Quy tắc cần cập nhật]
