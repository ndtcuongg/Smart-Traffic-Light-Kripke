# Checklist tiêu chí — report_guide.pdf

Nguồn trực tiếp: PDF tr.3 cấu trúc; tr.4 định dạng; tr.5 năm mục; tr.6–7 bảng; tr.8 trọng số; tr.8–9 checklist. Không tự chấm điểm.

| Tiêu chí | Trọng số | Bằng chứng / trạng thái |
|---|---:|---|
| Đầy đủ cấu trúc 8 phần | 10% | Đủ tám Heading1, đúng tên/thứ tự |
| Chất lượng phân tích lỗ hổng (Phần 4) | 35% | D01–D03 đủ năm mục; CWE/CERT chờ giảng viên |
| Bảng before/after (Phần 5) | 15% | D01–D03 khớp1–1, có log |
| Chất lượng bằng chứng (Phần 6) | 20% | Log đầy đủ/hash/chỉ mục; nộp phụ lục điện tử |
| Chiều sâu phản biện (Phần 7) | 10% | Ba câu hỏi; hạn chế/vacuity/abstraction cụ thể |
| Định dạng & trình bày | 10% | Times New Roman11.5pt, A4 lề2cm, trang/caption; tên phiên bản cần duyệt |

- [x] Đủ tám phần, đúng tên/thứ tự.
- [ ] CWE cụ thể: không tự gán cho lỗi logic; giảng viên xác nhận áp dụng.
- [x] D01–D03 đủ vị trí, nguyên nhân, chứng cứ trước, cách sửa, chứng cứ sau.
- [x] Bảng phần5 khớp phần4; tách giới hạn/mở rộng/fault.
- [x] Log/ảnh có caption; log đầy đủ trong phụ lục điện tử.
- [x] Baseline nguyên vẹn, hash không đổi.
- [x] Cung cấp lệnh build/kiểm; generator khớp model, không ghi đè chapter1.
- [x] data_gen/seed không áp dụng; thay config/hash, nêu state-limit.
- [x] Phản biện cụ thể về Kripke, CTL, vacuity, đồng bộ next.
- [ ] Điền tên/MSSV/lớp/nhóm/GitHub/phân công/tuần/mã đề tài thật.
- [ ] Giảng viên duyệt CWE/CERT, tên phiên bản và phụ lục điện tử.
- [ ] PDF mở/font/đủ trang: xem quality_validation.json sau kiểm kỹ thuật; nhóm kiểm lần cuối trước nộp.

Độ dài gợi ý: bìa1; tổng quan1–1.5; phương pháp1; phân tích3–6; bảng1; bằng chứng1–3; phản biện0.5–1; phụ lục không giới hạn. Đo trang thực sau render, không mặc định đạt.
