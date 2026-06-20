# Project Rules & Customizations

## 1. Session Initialization (BẮT BUỘC)
- Tại đầu mỗi phiên làm việc (Session Start), Agent PHẢI chủ động đọc và cập nhật thông tin phong cách/kinh nghiệm từ file [MEMORY.md](file:///home/datphan/job/hoa/ECU_tools/uart_tool/MEMORY.md).

## 2. Safe Execution Workflow (BẮT BUỘC)
Mọi tác vụ thay đổi mã nguồn PHẢI tuân thủ quy trình sau (xem chi tiết tại [rules/coding.md](file:///home/datphan/job/hoa/ECU_tools/uart_tool/rules/coding.md)):
1. **Lập kế hoạch (Plan):** Tạo một `<proposed_plan>` bao gồm Root cause, các file bị ảnh hưởng, các thay đổi dự kiến (Pseudocode/Logic), Kế hoạch kiểm thử (Test plan), và **Decision Points** (các lựa chọn kiến trúc/tradeoff).
2. **Xác nhận (Confirm):** Dừng lại và đợi người dùng gõ `/approve` trong Chat.
3. **Thực thi (Act):** Chỉ khi nhận được sự đồng ý mới tiến hành chỉnh sửa mã nguồn.
4. **Kiểm chứng (Verify):** Chạy các lệnh kiểm thử/linting và báo cáo kết quả.

## 3. Coding Philosophy & Review Guidelines
- **Maintainability & Simplicity:** Xem chi tiết tại [rules/coding.md](file:///home/datphan/job/hoa/ECU_tools/uart_tool/rules/coding.md).
- **Review Logic Khắt khe & Quy trình Review:** Xem chi tiết tại [rules/review.md](file:///home/datphan/job/hoa/ECU_tools/uart_tool/rules/review.md). Không tự ý sửa các đoạn mã mơ hồ (ambiguity) mà phải hỏi ý kiến người dùng trước.
