# Smart Traffic Light — Kripke & NuSMV

## 1. Giới thiệu dự án

**Tên đề tài:** Mô hình hóa và kiểm chứng hình thức cho hệ thống các đèn giao thông thông minh sử dụng cấu trúc Kripke.

**Môn học:** CSE703093-1-1-26(N01) — An toàn phần mềm.

**Trường:** Đại học Phenikaa.

Dự án xây dựng mô hình hệ thống đèn giao thông thông minh tại ngã tư gồm bốn hướng Bắc, Nam, Đông và Tây.

Hệ thống sử dụng cấu trúc Kripke để biểu diễn trạng thái, logic thời gian CTL và công cụ NuSMV để kiểm chứng các thuộc tính an toàn và hoạt động.

## 2. Chức năng chính

- Mô phỏng hoạt động đèn giao thông với sáu pha điều khiển.
- Điều chỉnh thời lượng đèn theo bốn khung giờ trong ngày.
- Xây dựng và trực quan hóa cấu trúc Kripke.
- Kiểm chứng các thuộc tính CTL bằng NuSMV.
- Phân tích ba lỗi logic D01, D02 và D03 trong mô hình ban đầu.
- Thử nghiệm ba trường hợp cố ý gây lỗi N1, N2 và N3 để quan sát phản ví dụ.
- Hiển thị mô hình, cấu hình và kết quả kiểm chứng trên giao diện Web.

## 3. Công nghệ sử dụng

- **Python 3.11:** Xây dựng logic chuyển trạng thái và sinh mô hình.
- **NuSMV 2.7.1:** Kiểm chứng các thuộc tính CTL.
- **JSON:** Lưu cấu hình và dữ liệu mô hình Kripke.
- **HTML, CSS, JavaScript:** Xây dựng giao diện Web.

## 4. Cấu trúc dự án

| Thư mục / File | Chức năng |
|---|---|
| `Smart-Traffic-Light-Verification/` | Mô hình ban đầu v0 |
| `chapter1/` | Mô hình cải tiến v1 |
| `chapter1/config.json` | Cấu hình thời gian giao thông |
| `chapter1/intersection.py` | Logic điều khiển và chuyển trạng thái |
| `chapter1/build.py` | Chương trình sinh mô hình |
| `chapter1/smart_intersection.smv` | Mô hình chính thức dùng NuSMV |
| `chapter1/web/` | Giao diện Web |
| `chapter1/evidence/` | Bằng chứng và các mô hình đối chứng |
| `output/official_report_20261024/evidence/` | Log kiểm chứng phục vụ báo cáo |

## 5. Hướng dẫn chạy

**Yêu cầu:** Máy tính đã cài đặt Python và trình duyệt Web. Để kiểm chứng trực tiếp cần cài đặt NuSMV.

**Bước 1:** Mở Terminal tại thư mục gốc của dự án.

**Bước 2:** Chạy Web bằng lệnh:

`python chapter1/web/server.py`

**Bước 3:** Mở trình duyệt tại địa chỉ:

`http://127.0.0.1:8765`

**Chạy kiểm chứng bằng NuSMV:**

`NuSMV -dynamic -df -coi chapter1/smart_intersection.smv`

Lệnh trên yêu cầu NuSMV đã được cài đặt và có thể gọi từ Terminal.

## 6. Kết quả đạt được

Theo bộ bằng chứng kiểm chứng đã lưu của dự án:

| Nội dung | Kết quả |
|---|---|
| Kiểm chứng CTL bằng NuSMV | 335/335 thuộc tính TRUE |
| Kiểm chứng CTL trên dữ liệu JSON | 26/26 thuộc tính đạt |
| Số trạng thái đạt được trong mô hình NuSMV | 86.400 |
| Kiểm tra khả năng đạt tới các khung giờ | 4/4 chế độ đạt được |
| Thử nghiệm đối chứng lỗi | 3 trường hợp được phát hiện |

Các kết quả trên phản ánh những lần kiểm chứng đã lưu, không thay thế việc kiểm chứng lại sau khi thay đổi mã nguồn.

## 7. Thành viên thực hiện

| Họ và tên | MSSV | Vai trò |
|---|---|---|
| Nguyễn Đào Tuấn Cường | 23011520 | Phân tích mô hình, phát triển hệ thống, kiểm chứng và tổng hợp kết quả |
| Nguyễn Trung Hiếu | 23010603 | Hỗ trợ nghiên cứu, kiểm thử và tài liệu |

**Giảng viên hướng dẫn:** Vũ Quang Dũng

## 8. Giới hạn của dự án

Hệ thống được mô phỏng và kiểm chứng trên phần mềm, chưa triển khai trên thiết bị điều khiển đèn giao thông thực tế.

Kết quả kiểm chứng chỉ áp dụng cho các thuộc tính đã được đặc tả trên mô hình tương ứng.