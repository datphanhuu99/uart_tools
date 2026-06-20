# Review Guidelines

## 1. Review Logic Khắt khe
Khi review code (của chính Agent hoặc người khác), Agent PHẢI tập trung vào:
- **Functional Correctness:** Kiểm tra lỗi logic, sai sót tiềm ẩn.
- **Ambiguity Detection:** Nếu phát hiện một đoạn code có vẻ giống bug nhưng có khả năng là tính năng (feature), Agent KHÔNG ĐƯỢC tự ý sửa. PHẢI hỏi bạn rõ ràng trước khi quyết định.
- **Readability:** Đảm bảo code dễ đọc, dễ hiểu.

## 2. Quy trình Review
- Agent thực hiện review dựa trên Checklist nội bộ.
- Mọi cảnh báo (Warning) hoặc nghi ngờ về tính năng cần được liệt kê trong file `.plan.md` hoặc báo cáo review gửi bạn.
