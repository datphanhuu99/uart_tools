# Coding Standards & Execution Workflow

## 1. Safe Execution Workflow (BẮT BUỘC)
Mọi tác vụ thay đổi mã nguồn PHẢI tuân thủ quy trình sau:

- **Bước 1: Lập kế hoạch (Plan):** Trước khi đụng vào code, Agent PHẢI tạo một `<proposed_plan>` bao gồm:
  - Phân tích vấn đề (Root cause).
  - Các file sẽ bị ảnh hưởng.
  - Các thay đổi dự kiến (Pseudocode/Logic).
  - Kế hoạch kiểm thử (Test plan) để xác nhận thay đổi.
  - **Decision Points:** Liệt kê các lựa chọn kiến trúc hoặc tradeoff (ví dụ: hiệu năng vs. dễ đọc) và hỏi ý kiến bạn trước khi thực thi.
- **Bước 2: Xác nhận (Confirm):** Agent PHẢI dừng lại và đợi bạn gõ `/approve` sau khi trình bày kế hoạch và sơ bộ logic trong Chat.
- **Bước 3: Thực thi (Act):** Chỉ khi nhận được sự đồng ý, Agent mới thực hiện chỉnh sửa.
- **Bước 4: Kiểm chứng (Verify):** Sau khi thực thi, Agent PHẢI chạy các lệnh kiểm thử/linting và báo cáo kết quả.

## 2. Coding Philosophy (Triết lý lập trình)
- **Maintainability First:** Ưu tiên khả năng đọc hiểu và dễ debug. Code phải được chú thích rõ ràng bằng tiếng Anh, tuân thủ chuẩn naming convention.
- **Simplicity over Complexity:** Kiến trúc Modular (tách file rõ ràng) nhưng không rườm rà. Chỉ tách khi cần thiết để kiểm soát chức năng, không làm phức tạp hóa cấu trúc không cần thiết.
- **Performance:** Ưu tiên đọc hiểu. Khi có trường hợp đặc biệt cần tối ưu hiệu năng cực đoan, Agent PHẢI note lại trong kế hoạch và hỏi bạn trước.

## 3. Framework & Refactoring Safety (An toàn khi lập trình và Refactor)
- **Framework Lifecycle Awareness:** Trước khi sử dụng bất kỳ phương thức phụ thuộc vào vòng đời của thư viện/khung làm việc (ví dụ: `mount` trong Textual), Agent phải chắc chắn đối tượng đang ở trạng thái hợp lệ. Ưu tiên khai báo cây giao diện trực tiếp (Declarative layout) bằng cách truyền đối tượng con vào constructor hơn là dựng cấu trúc động bằng mã lệnh (Imperative nesting) trên widget chưa mount.
- **Refactoring & Attribute Alignment:** Khi thực hiện tái cấu trúc, di chuyển hoặc đổi tên thuộc tính/phương thức:
  - Agent **PHẢI** thực hiện tìm kiếm toàn cục trên toàn bộ dự án đối với tên thuộc tính đó để cập nhật tất cả các vị trí tham chiếu (bao gồm cả các nhánh xử lý phụ/nhánh lỗi).
  - Khuyến khích sử dụng Static Analysis (mypy, linter) để phát hiện sớm các tham chiếu sai thuộc tính.
