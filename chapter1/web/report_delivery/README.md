# Biên bản kiểm thử phần mềm — Chương 1

Hai tệp nộp chính:

- BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.docx — bản Word có thể điền thông tin và ký.
- BIEN_BAN_KIEM_THU_PHAN_MEM_CHUONG_1.pdf — bản xuất bằng Microsoft Edge headless từ chính nội dung DOCX. Word đã mở thành công DOCX (26 trang, 15 bảng, 7 ảnh), nhưng hàm xuất PDF của Word bị treo; PDF dùng bộ dựng trang riêng, nên số trang có thể khác DOCX.

Ngày lập biên bản: 23/10/2026. Các kết quả sản phẩm là bằng chứng đã thực thi ngày 22/10/2026; không phải kết quả chạy lại ngày lập hồ sơ. Lượt chọn thống nhất theo browser_tests.json: 20261022T153609Z_0d111894.

Tài liệu có đủ 12 phần, bảng ca tám cột, bảng truy vết EV01… và bảy ảnh gốc. PASS* của từng ca backend dựa bản ghi tổng hợp 13/13, không có stdout riêng từng ca. Negative test mong đợi FALSE; chưa có bằng chứng LTL hoặc biên bản kiểm thử sản phẩm thủ công có người ký. Họ tên, MSSV, ngày xác nhận và chữ ký để trống.

Thư mục quality_checks lưu đối chiếu log, hash bằng chứng, mã ca, xác nhận Word mở/xuất PDF và kiểm tra PDF. Bản xem trước trang chỉ phục vụ rà soát tài liệu, không thay cho ảnh chụp sản phẩm.

Mã collect_evidence.py, case_data.py, build_record.py, export_word_pdf.ps1 và validate_documents.py phục vụ tái tạo hồ sơ. _tools chỉ là thư viện soạn/kiểm tài liệu, không cần để mở Word/PDF và không phải mã ứng dụng. Không sửa log, ảnh hay mã dự án khi tái tạo; mọi kết quả phải tiếp tục đối chiếu nguồn.

Nếu tách hai tài liệu khỏi cây dự án, các đường dẫn bằng chứng trong phụ lục vẫn là đường dẫn tương đối tính từ NuSMV_project; cần nộp kèm dự án/log theo yêu cầu giảng viên. Bảy ảnh đã được nhúng trong Word/PDF.

