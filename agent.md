# Project: art_ecu_firmware - Agent Hub

> **Hướng dẫn:** File này là trung tâm điều phối hành vi và tư duy của Agent cho toàn dự án.
> Mọi thay đổi nội quy tại đây phải được xác nhận thông qua quy trình phê duyệt.

## 1. Interaction Protocol (Quy trình tương tác)
- **Session Start:** Mỗi khi bắt đầu phiên làm việc, Agent PHẢI:
  1. Đọc `MEMORY.md`.
  2. Tóm tắt trạng thái dự án dựa trên `docs/session_notes.md`.
  3. Kiểm tra và đề xuất các cải tiến tool/skill nếu thấy cần thiết.
- **Plan-Act-Validate:** Trước mọi hành động phức tạp, Agent phải:
  1. Phân tích ngữ cảnh hệ thống.
  2. Tạo file `.plan.md` tạm thời.
  3. Trình bày sơ bộ kế hoạch trong Chat.
  4. Chờ bạn gõ `/approve` trước khi thực thi.
- **Rule Management:** Khi cập nhật nội quy, Agent đề xuất thay đổi nội dung file cụ thể (`rules/`), bạn review trong Chat, sau đó Agent mới ghi đè.
- **Feedback Loop:** Nếu người dùng không hài lòng, Agent PHẢI chủ động hỏi: "Tôi cần cải thiện điều gì để lần sau tốt hơn?" và đề xuất cập nhật vào `MEMORY.md` hoặc `rules/`.

## 2. Documentation Standards (Chuẩn tài liệu)
- **Centralized Docs:** Mọi tài liệu phải lưu trong thư mục `docs/` theo cấu trúc: `docs/<tính_năng>/<loại_tài_liệu>.md`.
- **Auto-Documentation:** Ngay sau mỗi thay đổi code, Agent cập nhật tài liệu với cấu trúc:
  - **Functionality:** Chức năng chính.
  - **TODOs:** Các nhiệm vụ chưa hoàn thành.
  - **Attention Points:** Điểm cần chú ý khi đọc docs/code.
  - **System Notes:** (Nếu cần) để cuối file, ghi chú quan trọng cho lần quay lại làm việc.
- **Context Logging:**
  - Note cho hệ thống (chung): Lưu tại `docs/session_notes.md`.
  - Note cho source (riêng): Lưu tại file docs tương ứng của tính năng đó.

## 3. Document Index (Bản đồ tri thức)
- **Architecture:** [docs/architecture/](./docs/architecture/)
- **Coding Rules:** [rules/coding.md](./rules/coding.md)
- **Review Guidelines:** [rules/review.md](./rules/review.md)
- **Session Notes:** [docs/session_notes.md](./docs/session_notes.md)

## 4. Operational State
- **Active Task:** [Cập nhật tại đây]
- **Persona:** Kỹ thuật, chủ động, tư duy điều phối (orchestrator), tuân thủ tiêu chuẩn nhúng.
