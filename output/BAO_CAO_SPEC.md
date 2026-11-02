# Đặc tả Excel theo PDF — Smart Traffic Light

File chính: **Smart_Traffic_Light_Spec.xlsx**. Đúng 10 sheet và tiêu đề theo PDF 28 trang được cung cấp. Nội dung ô và chú thích phân biệt rõ code hiện có với bài thực hành bổ sung. Không sửa bất kỳ file SMV gốc nào.

## Phạm vi và cách đọc

- Dự án chứa 14 file SMV thật; thư mục `login.smv` rỗng không phải file. `test.smv` ở gốc là ví dụ đăng nhập, được giữ thành thành phần riêng.
- Mỗi file có biến được liệt kê thành đồ thị hữu hạn các trạng thái đạt được; timer, traffic_mode, time_period, emergency và NS/EW_light đều được giữ. Các thành phần độc lập có tiền tố nhãn riêng và nhiều trạng thái khởi tạo. Không ngụ ý các mô hình này chạy đồng thời.
- Các công thức CTL được viết mới trên đồ thị Excel. Với code xác định hiện tại, thuộc tính thời gian gốc có thể đối chiếu trên đường chạy duy nhất. Không tuyên bố phép thay G/F/X bằng AG/AF/AX đúng cho mọi mô hình bất định.
- Bốn trạng thái signal_free/main_holds/log_holds/conflict là bài lab khóa bổ sung theo PDF 3.5; KHÔNG tồn tại trong code gốc. AG(!violation) và mutex dòng đầu phải thất bại để minh họa phát hiện lỗi.
- Hàm C/Python, bộ đếm cộng dồn và mục tiêu phi chức năng là thiết kế bổ sung theo PDF, chưa triển khai/chưa đo. Không quy lỗi bộ nhớ C hay tràn int32 cho timer có miền 0..60 trong SMV.
- Các ô trống KhoiTao và trường HamSinhMa không áp dụng tuân theo quy tắc riêng PDF 3.5/3.8. Không điền N/A vì có thể làm parser hiểu sai. Buffer 16 byte chứa tối đa 15 ký tự ASCII và NUL.
- Sheet LoaiTruLanNhau có nhiều cặp; theo PDF parser chỉ tự kiểm cặp đầu. Các cặp bổ sung quan trọng cũng được thể hiện bằng CTL. TestCase là kế hoạch truy vết, không tự được pipeline thực thi.

## Kết quả NuSMV gốc

| File | Số thuộc tính | True | False | Exit |
|---|---:|---:|---:|---:|
| Smart-Traffic-Light-Verification/01_basic_model/traffic_light_model.smv | 1 | 1 | 0 | 0 |
| Smart-Traffic-Light-Verification/02_time_based_model/timed_light.smv | 2 | 2 | 0 | 0 |
| Smart-Traffic-Light-Verification/03_adaptive_model/adaptive_light.smv | 10 | 10 | 0 | 0 |
| Smart-Traffic-Light-Verification/03_bmc/init_bug.smv | 1 | 0 | 1 | 0 |
| Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc.smv | 1 | 1 | 0 | 0 |
| Smart-Traffic-Light-Verification/03_bmc/traffic_light_bmc_bug.smv | 0 | 0 | 0 | 0 |
| Smart-Traffic-Light-Verification/03_bmc/transition_bug.smv | 2 | 1 | 1 | 0 |
| Smart-Traffic-Light-Verification/04_verification/safety_liveness.smv | 4 | 4 | 0 | 0 |
| Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug.smv | 1 | 0 | 1 | 0 |
| Smart-Traffic-Light-Verification/05_bug_analysis/transition_bug_fixed.smv | 1 | 1 | 0 | 0 |
| Smart-Traffic-Light-Verification/06_extension/emergency_mode.smv | 4 | 4 | 0 | 0 |
| Smart-Traffic-Light-Verification/test/traffic_light2.smv | 0 | 0 | 0 | 0 |
| Smart-Traffic-Light-Verification/test/traffic_light_basic.smv | 0 | 0 | 0 | 0 |
| test.smv | 1 | 1 | 0 | 0 |

Log đầy đủ, stderr, thời gian đo và SHA-256 từng file nằm trong **nusmv_results.json**. Các bản lỗi được kỳ vọng có false; exit code 0 không đồng nghĩa tất cả thuộc tính đúng.

## Điểm cần lưu ý trong code

1. **adaptive_light.smv:** hai nhánh time_period=NORMAL_TIME; nhánh đầu chọn MORNING_PEAK nên nhánh EVENING_PEAK không bao giờ được chọn. Chu kỳ chỉ NORMAL_TIME ↔ MORNING_PEAK; EVENING_PEAK, NIGHT_LOW và traffic_mode=LOW không đạt được. Các thuộc tính kéo theo NIGHT_LOW/LOW vì vậy có thể đúng rỗng. Workbook có hai kiểm tra khả đạt trả false để làm rõ.
2. **adaptive_light.smv:** khi pha xanh timer=0, next(state) chuyển vàng trong khi next(timer) nhận 45/30/20 theo mode cũ; khi vàng kết thúc lại nạp 5 cho pha xanh. Do đó đặc tả thời lượng xanh thích nghi chưa phản ánh đúng mục tiêu bình luận. traffic_mode cũng cập nhật theo time_period hiện tại, có độ trễ 1 bước.
3. **timed_light.smv:** timer đếm cả giá trị 0 trước khi chuyển pha. Pha xanh 30..0 có 31 trạng thái; pha vàng 5..0 có 6. Không tự suy ra 30/5 giây nếu chưa định nghĩa một bước là gì và cách đo biên.
4. **init_bug.smv:** GREEN/GREEN ở init làm safety sai ngay bước đầu. **transition_bug.smv** ở 03_bmc và 05_bug_analysis bỏ S1: S0→S2; bản fixed sửa S0→S1. Safety không đồng thời xanh vẫn có thể đúng khi quy tắc chuyển pha sai.
5. **traffic_light_bmc_bug.smv:** chỉ có MODULE main, không có biến/chuyển tiếp/thuộc tính; không được xem là một bài BMC có kết quả. Hai file trong test cũng chưa có SPEC/LTLSPEC.
6. **emergency_mode.smv:** cảm biến luân phiên FALSE/TRUE cố định; không bao phủ cảm biến giữ TRUE hay đến ngẫu nhiên. Các điều kiện cấm hai giá trị state enum đồng thời chỉ là bất biến cấu trúc.
7. **safety_liveness.smv:** có bước NS_YELLOW/EW_GREEN; mô hình không bảo đảm hướng đối diện phải đỏ khi một hướng vàng, cũng không có khoảng all-red. Các thuộc tính đang có không đủ khẳng định an toàn giao lộ thực tế.
8. Tên thư mục 03_bmc không tự biến lần chạy mặc định thành BMC. Kết quả gốc ở đây dùng NuSMV mặc định, chưa phải báo cáo SAT bounded model checking.

## Kiểm tra file Excel

| Sheet | Dòng dữ liệu |
|---|---:|
| ThongTin | 2 |
| YeuCauChucNang | 19 |
| YeuCauPhiChucNang | 6 |
| RangBuoc | 9 |
| MoHinhTrangThai | 461 |
| ThuocTinhAnToan | 29 |
| LoaiTruLanNhau | 6 |
| HamSinhMa | 7 |
| KiemTraSoHoc | 5 |
| TestCase | 27 |

- Đã mở lại workbook, kiểm tra header/ID/nhãn/chuyển tiếp, bốn loại lỗi C và hai mẫu Python. Không có deadlock trong đồ thị Excel.
- Đã đối chiếu số trạng thái đạt được của 13 mô hình với print_reachable_states của NuSMV; mọi số lượng đều khớp.
- Đã xuất đồ thị từ dữ liệu Excel sang excel_graph_check.smv và chạy NuSMV: **29 CTL, 22 true, 7 false**, khớp toàn bộ kết quả dự kiến. Log: excel_graph_check.log; tổng kiểm tra: validation.json.
- **Chưa chạy** parse_specification_excel(), run_pipeline(), Z3 hoặc fuzzing: workspace không có mã nguồn Spec Verification Lab (core/spec_excel.py, core/spec_pipeline.py...). Kiểm tra NuSMV độc lập không thay thế kiểm tra tương thích với parser/pipeline đó. Chưa thể đánh dấu phần 5.3 của PDF là hoàn tất.
- Các CWE được nêu trong TestCase là kết quả dự kiến theo hướng dẫn PDF, chưa phải lỗ hổng được phát hiện hoặc CVE của dự án.

## Cách dùng

1. Mở Smart_Traffic_Light_Spec.xlsx; xem chú thích tại cột đầu của mỗi dòng để biết nguồn.
2. Khi có bộ Spec Verification Lab đúng phiên bản PDF, chép workbook sang đó rồi chạy `python -m core.spec_excel duong_dan/Smart_Traffic_Light_Spec.xlsx`.
3. Đối chiếu kết quả với các bài lỗi cố ý và TestCase; kiểm tra đủ bốn chương trước khi nộp phần xác nhận pipeline.
4. Để tái tạo file từ code: `python scripts/generate_spec.py` (cần openpyxl trong .codex-tools hoặc môi trường Python và NuSMV trên PATH).

NOTE: EF(main_locked) is TRUE from signal_free, but FALSE over all independent initial states. The workbook intentionally retains the exact PDF formula and records this multi-component limitation. No artificial cross-model edges were added.
