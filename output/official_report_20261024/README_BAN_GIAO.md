# Bàn giao báo cáo đồ án — 24/10/2026

- Báo cáo chính thức: [PDF](BAO_CAO_CHINH_THUC.pdf) · [DOCX chỉnh sửa](BAO_CAO_CHINH_THUC.docx), 20 trang PDF, đúng tám mục và độ dài gợi ý.
- Biên bản riêng: [PDF](BIEN_BAN_KIEM_CHUNG.pdf) · [DOCX](BIEN_BAN_KIEM_CHUNG.docx), 2 trang.
- [Kiểm kê trước viết](KIEM_KE_BANG_CHUNG.md) · [Checklist tiêu chí trường](CHECKLIST_TIEU_CHI.md).
- [838 dòng truy vết có liên kết log](verification_test_record.html) · [CSV](verification_test_cases.csv) · [JSON](verification_test_cases.json).
- [Mục lục trang PDF](MUC_LUC_TRANG.md) · [Kết quả kiểm tra](quality_validation.json).
- [Phụ lục nguồn và log nguyên văn](PHU_LUC_NGUON_VA_BANG_CHUNG.zip); nộp cùng báo cáo. Giữ nguyên cấu trúc kho để mở liên kết trong HTML.

Kết quả mới: 335/335 CTL v1 TRUE; BDD 86400 reachable; 26/26 CTL JSON TRUE; graph exact86400/86400, chiếu1012/2548; bốn query bổ sung v0 FALSE đúng dự kiến; ba injected-fault CTL FALSE có trace. Các LTL gốc trong hai harness v0 vẫn TRUE. Đã giữ nguyên 243 tệp dự án kiểm kê, không đổi nguồn v0 hoặc logic ứng dụng.

## Cần hoàn thiện trước nộp

1. Điền tên, MSSV, lớp, số nhóm, GitHub và phân công bằng thông tin thật; xác nhận giảng viên hướng dẫn thực tế.
2. Giảng viên xác nhận dùng mã lỗi mô hình D01–D03 thay CWE/CERT; không có căn cứ gán CWE/CERT trong kho.
3. Xác nhận quy ước tên v0/v1 hiện có thay hậu tố, phụ lục log điện tử và tài liệu quy trình năm bước/tuần học/mã đề tài.
4. V0 archive cũ thiếu timestamp/lệnh đầy đủ; không điền hồi tố. Counterexample trực tiếp mới đã bù thiếu chứng cứ timer/reset/reachability.
5. Chưa có thử nghiệm giao lộ vật lý, emergency hoặc thao tác GUI SecLab; không công bố các phần này PASS.

PDF được xuất bằng Edge từ cùng nội dung cấu trúc với DOCX. Word có thể phân trang khác; PDF là bản đã kiểm định dạng. Không có commit hoặc danh tính cá nhân được tạo giả.
