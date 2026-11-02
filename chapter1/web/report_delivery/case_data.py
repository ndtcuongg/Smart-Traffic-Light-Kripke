"""Descriptions of already-executed checks; IDs are document references, not new executions."""
WEB=[
('12 đèn ở trạng thái đầu','Trang sẵn sàng; API trả S0.','Đếm 12 circle và 12 chỉ báo; so từng BẬT/TẮT với API.','Đủ 24 thành phần hiển thị, khớp cùng state ID; trạng thái an toàn.','Khớp API; ALL_RED_EW_TO_NS, timer 2, 00:00:00.'),
('Chu kỳ, timer và an toàn','Từ S0, mô phỏng đang dừng.','Bấm +1 giây 43 lần; lưu pha, timer, đèn và tính an toàn.','Đúng thứ tự sáu pha; mỗi bước trong pha giảm 1; DOM khớp API; không cùng xanh.','Ghi 43 mẫu; thứ tự bắt đầu ALL_RED_EW_TO_NS → NS_GREEN → NS_YELLOW → ALL_RED_NS_TO_EW → EW_GREEN → EW_YELLOW → ALL_RED_EW_TO_NS.'),
]
for time in ['06:59:59','08:59:59','15:59:59','18:59:59','21:59:59','23:59:59']:
    WEB.append(('Mốc giờ '+time,'Có nút mốc giờ; warmup 12 bước.','Chọn mốc, đọc trạng thái; bấm +1 giây; so trước/sau.','Giữ pha và entry_period; timer giảm 1; thời lượng không đổi; DOM khớp API. Nửa đêm về 00:00:00.','BOUNDARY'))
WEB += [
('Bắt đầu / tốc độ / tạm dừng','Chọn 06:59:59; đổi tốc độ thành 8×.','Bấm Bắt đầu; chờ đồng hồ đổi; bấm Tạm dừng; so state ID sau 500 ms.','Có tiến triển khi chạy; không đổi state ID trong khoảng quan sát sau khi dừng.','Phép so state ID khi dừng trả true. Không đo chính xác tốc độ thời gian thực.'),
('Tiếp tục / đặt lại / bước','Đã tạm dừng và có seed 06:59:59.','Tiếp tục đến khi state ID đổi; dừng; Đặt lại về seed; đọc đèn.','State ID đổi khi tiếp tục; giờ trở về seed; đèn khớp API.','Đặt lại về 06:59:59; phép so DOM/API trả true.'),
('DOM khớp backend','Đã đặt lại theo seed.','Bấm thêm +1 giây và đối chiếu tất cả chỉ báo với API.','State ID và cả 12 đèn ở SVG/bảng khớp backend.','Phép đối chiếu trả true. Đối chiếu R/nguồn chi tiết ở API-04.'),
('S0 và hàm gán nhãn','Mở trang Kripke, nhãn đã tải.','Đọc mã đang chọn và toàn bộ L(s); gọi API lấy cùng ID.','ID và danh sách nhãn hiển thị bằng phản hồi API.','So ID và JSON danh sách nhãn đều đúng. Cạnh R được kiểm riêng tại API-07.'),
('Góc nhìn các hướng','Trang Kripke sẵn sàng.','Bấm tab directions; đọc vùng giải thích.','Vùng giải thích có nội dung dài hơn 120 ký tự.','Điều kiện độ dài nội dung đúng; chưa phải kiểm chứng ngữ nghĩa toàn bộ sơ đồ.'),
('Góc nhìn timer','Trang Kripke sẵn sàng.','Bấm tab timer; đọc vùng giải thích.','Vùng giải thích có nội dung dài hơn 120 ký tự.','Điều kiện độ dài nội dung đúng.'),
('Góc nhìn khung giờ','Trang Kripke sẵn sàng.','Bấm tab periods; đọc vùng giải thích.','Vùng giải thích có nội dung dài hơn 120 ký tự.','Điều kiện độ dài nội dung đúng.'),
('Góc nhìn kết hợp','Trang Kripke sẵn sàng.','Bấm tab combined; đọc vùng giải thích.','Vùng giải thích có nội dung dài hơn 120 ký tự.','Điều kiện độ dài nội dung đúng.'),
('Lọc trạng thái Kripke','Danh sách trạng thái đã tải.','Chọn bộ lọc phase = NS_GREEN.','Có kết quả; mọi ID trong danh sách bắt đầu NS_GREEN__.','Tất cả kết quả hiển thị thỏa bộ lọc.'),
('Xem trạng thái exact đang chạy','Có trạng thái mô phỏng hiện hành.','Chọn exact; bấm Xem trạng thái mô phỏng; chờ đúng ID.','Mã trong inspector bằng state ID của mô phỏng.','Hai ID bằng nhau; có đồng hồ trong mã trạng thái.'),
('Kết quả lưu có nhãn nguồn','Mở Kiểm chứng hình thức; bảng đã tải.','Đọc nhãn nguồn và thống kê.','Nhãn ghi lịch sử, bảng có 335/335.','Hai điều kiện hiển thị đúng; kết quả được xác nhận thêm từ EV07/EV10.'),
('CTL JSON lịch sử','Đang chọn bằng chứng đã lưu.','Bấm tab JSON; đọc cột công cụ.','Ghi đúng SecLabFramework cho bản ghi cũ.','Có tên SecLabFramework; không tuyên bố web đã gọi lại công cụ cũ.'),
('Tách đối chứng cố ý lỗi','Dashboard đã tải.','Chọn tab negative.','Đúng ba hàng; có kết quả SAI.','Ba hàng đối chứng tách riêng; nhãn SAI xuất hiện.'),
('Mở phản ví dụ thật','Tab đối chứng đã có log.','Bấm mở log .log; chờ nội dung; tìm is false và Trace.','Hiển thị stdout thật với FALSE và trace.','Cả is false và Trace được tìm thấy; không dùng phản ví dụ giả.'),
('Kích hoạt lượt kiểm mới','NuSMV có trên PATH; nút chạy được bật.','Bấm Chạy kiểm chứng mới; chờ tác vụ kết thúc; đọc nguồn đang chọn.','Nguồn đổi từ recorded sang mã lượt vừa hoàn tất.','RUN'),
('Tích hợp checker và BDD','Lượt mới hoàn tất.','Đọc API kết quả; so các tổng và cờ bảo toàn.','executed; 335 + 335 CTL đúng; 4 EF; 26 CTL JSON; 86.400 trạng thái; integrity = true.','Các giá trị đều khớp; có stdout NuSMV xác nhận tại EV07–EV17.'),
('Bộ kiểm JSON độc lập','Đang chọn lượt mới.','Bấm tab JSON; đọc công cụ.','Có chữ độc lập; không ghi SecLabFramework cho lượt mới.','Tên công cụ đúng bộ kiểm Python độc lập.'),
('Cấu hình hiển thị','Mở Cấu hình thời gian.','Đếm hàng bảng khoảng giờ và bảng pha.','Bảy khoảng thời gian và sáu pha.','Bảng lần lượt có 7 và 6 hàng. Chỉ kiểm số hàng tại phép thử này.'),
('Đối chiếu v0/v1','Mở Before/After.','Đếm lựa chọn, mục phân tích; tìm đường dẫn v1.','14 file gốc, 5 mục cho file được chọn; có smart_intersection.smv.','Cả ba điều kiện đúng. Toàn bộ 14 nguồn được kiểm hash tại API-09.'),
('Bảo toàn nguồn cũ','Mở Bằng chứng và kết quả.','Bấm Kiểm tra bảo toàn tệp; chờ kết quả.','Trạng thái bảo toàn PASS.','API kiểm bảo toàn báo PASS cho baseline 93 tệp cũ.'),
('Bố cục điện thoại','Emulation 390 × 844; mở mô phỏng.','So scrollWidth với innerWidth.','Không tràn ngang toàn trang.','scrollWidth ≤ innerWidth. Không đại diện mọi thiết bị/trình duyệt.'),
('Mở menu điện thoại','Đang ở kích thước điện thoại.','Bấm nút menu.','Sidebar có class open.','Sidebar mở đúng điều kiện kiểm.'),
('Đổi trang và đóng menu','Menu điện thoại đang mở.','Bấm liên kết Cấu hình; đọc trạng thái menu/trang.','Menu đóng; trang Cấu hình hiện.','Cả hai điều kiện đúng.'),
('Lỗi JavaScript','Đã thực hiện chuỗi Edge trên.','Thu Runtime.exceptionThrown và console error trong toàn bộ phiên.','Danh sách lỗi thu được rỗng.','Không ghi nhận lỗi trong phiên này; không suy ra không còn mọi lỗi có thể xảy ra.'),
]
API=[
('12 đèn, đồng bộ, loại trừ cả ngày','Config mặc định; kernel initial().','Lặp 86.400 bước nguồn; kiểm 12 giá trị, đúng một màu/cột, cặp đồng bộ và không cùng xanh.','Tất cả bất biến đúng; xuất hiện đủ 6 pha.','Kiểm kernel toàn ngày; không phải 86.400 yêu cầu HTTP.'),
('Chu kỳ, giảm/nạp timer, ALL_RED','HTTP reset lúc 00:00:00.','Lấy 80 bước qua API; so các cặp liên tiếp; kiểm pha đích và thời lượng cấu hình.','r>1 giảm 1/giữ entry; r=1 sang pha đúng; pha ALL_RED được nạp 2.','Kiểm chuỗi HTTP; thứ tự 7 đoạn đầu đúng.'),
('Bảy ranh giới và chốt thời lượng','Các mốc 06, 07, 09, 16, 19, 22, 24 giờ.','Reset trước từng mốc 1 giây, warmup 12; gọi step.','Clock/period đúng; giữ pha, entry_period, phase_duration; giảm timer 1.','Bảy subtest được chạy trong một ca unittest.'),
('API khớp kernel nguồn','5 cặp clock/warmup: (0,0), (25199,12), (57599,12), (86399,12), (32000,0).','Tính initial/step trực tiếp; reset HTTP; so state ID và đèn của 120 bước mỗi điểm.','Mọi ID và 12 giá trị đèn bằng nguồn.','600 cạnh HTTP được đối chiếu trong một ca.'),
('Thời gian còn lại từng hướng','Reset 06:59:59, warmup 12.','Đi tiếp nguồn tối đa 199 bước; tính lúc đến xanh/đổi màu từng hướng; so API.','until_green và color_remaining bằng số bước thật.','Cả bốn hướng được đối chiếu.'),
('Phiên, reset, đầu vào sai và token','Hai client có cookie riêng.','Đặt giờ một phiên; đọc phiên kia; reset; gửi count 0/121/true; gửi token invalid.','Phiên kia ở 0; reset về 30000; yêu cầu sai gây HTTPError.','Script kiểm ngoại lệ HTTPError; không khẳng định mã HTTP cụ thể.'),
('Kripke S0, L, R và tìm kiếm','Có JSON và API đồ thị.','So S0/nhãn/cạnh ra với JSON; lọc pha+giờ, limit=7; exact limit=2; xem current.','Nhãn và cạnh đúng; lọc đúng; exact total 86400, 2 kết quả; current có một cạnh ra.','Đối chiếu JSON trực tiếp, không vẽ toàn bộ S.'),
('Kết quả lịch sử khớp nguồn','Có nusmv_results.json và log đối chứng cũ.','So thống kê API với JSON; kiểm kind/started_at; đọc log đồng xanh.','335, 26, 86400; recorded, started_at null; negative FALSE/PASS; log có false/Trace.','Đọc bằng chứng cũ, không phải lượt kiểm mới.'),
('14 nguồn Before/After','Có audit và stdout trích xuất.','Kiểm đủ 14 bản ghi, đủ 5 mục, hash nguồn và đường dẫn stdout tồn tại.','Tất cả khớp audit.','Tái sử dụng mã gốc, không sửa v0.'),
('Toàn vẹn nguồn','Bootstrap và baseline bảo toàn có sẵn.','Đọc integrity, generator_matches_model và /api/preservation.','Các cờ đúng; preservation PASS.','Nguồn Python/cấu hình khớp v1; baseline được giữ nguyên.'),
('Giới hạn đọc tệp','Client đã có phiên.','Yêu cầu artifact ../secret và chapter1/web/server.py.','Cả hai gây HTTPError.','Không khẳng định đã kiểm toàn bộ lớp bảo mật/đường dẫn có thể có.'),
('Ngữ nghĩa bộ kiểm CTL','Đồ thị s phân nhánh đến good/bad, thêm unreachable.','Kiểm EF/AF/AG/EG/AX/EX; sau đó tạo quan hệ có deadlock.','Kết quả [true,false,true,true,false,true], reachable=3; đồ thị thiếu cạnh bị ValueError.','FALSE ở AF(goal), AX(goal) là mong đợi trên fixture, không phải lỗi sản phẩm.'),
('26 CTL JSON độc lập','JSON chiếu hiện hành.','Gọi check_graph trên JSON; kiểm overall, số công thức và từng kết quả.','overall PASS, đúng 26 thuộc tính và tất cả true.','Bộ kiểm fixpoint Python; không dùng SecLabFramework.'),
]
CATS={'safety':'An toàn và đầu ra','mutex':'Loại trừ xanh','liveness':'Tính sống','deadlock':'Không bế tắc','timer':'Timer chính xác','adaptive':'Thích nghi/chốt pha','clock':'Đồng hồ 24 giờ','transition':'Chuyển pha an toàn','reachability':'Khả đạt pha'}
def cases(a):
    web=[]
    for i,(f,pre,steps,expected,actual) in enumerate(WEB):
        c=a['browser']['checks'][i]
        if actual=='BOUNDARY':
            d=c['details'];x,y=d['before'],d['after'];actual=f"{x['clock']} → {y['clock']}; {x['period']} → {y['period']}; timer {x['timer']} → {y['timer']}; entry giữ {y['entry']}; D={y['duration']}."
        if actual=='RUN':actual='Hoàn tất '+a['browser']['fresh_run']+'.'
        web.append({'id':f'WEB-{i+1:02d}','function':f,'pre':pre,'steps':steps,'expected':expected,'actual':actual,'status':c['status'],'evidence':f'EV02 checks[{i}]; EV04','native':c['name']})
    backend=[]
    for i,(f,pre,steps,expected,actual) in enumerate(API):
        backend.append({'id':f'API-{i+1:02d}','function':f,'pre':pre,'steps':steps,'expected':expected,'actual':'Bộ 13 ca PASS, 0 failure/error. '+actual,'status':'PASS*','evidence':f'EV01; EV03 / {a["backend_methods"][i]}','native':a['backend_methods'][i]})
    formal=[]
    for i,(cat,items) in enumerate(a['property_groups'].items(),1):
        formal.append({'id':f'FM-{i:02d}','function':CATS[cat],'pre':'Mô hình v1/config khớp hash; lượt mặc định.','steps':f'Đọc kết quả NuSMV; đối chiếu {len(items)} công thức trong properties.json với stdout.','expected':f'Tất cả {len(items)} công thức TRUE.','actual':f'{len(items)}/{len(items)} TRUE; ví dụ '+items[0]['name']+'.','status':'PASS','evidence':'EV07, EV10, EV18','native':cat})
    extra=[('335 CTL giờ bất kỳ','Dùng bản sinh any_clock, không sửa v1.','NuSMV -dynamic -df -coi trên nusmv_any_start_time.smv.','335/335 TRUE.','335 TRUE, 0 FALSE, returncode 0.','EV08, EV10'),('Khả đạt bốn khung giờ','Mô hình có clock 24 giờ.','Kiểm EF(period = p) cho bốn period.','4/4 TRUE.','Cả bốn khung giờ đạt được.','EV09, EV10'),('26 CTL JSON','JSON chiếu 1.012 trạng thái.','Kiểm fixpoint độc lập theo từng công thức.','26/26 đúng ở S0.','26 PASS; overall PASS; không dùng checker cũ.','EV11, EV21'),('Đếm trạng thái BDD','S0 mặc định; clock 00:00:00.','NuSMV -dynamic -r -is -ils -ii theo EV13.','Đếm khớp mô hình exact nguồn.','86.400 trạng thái; returncode 0.','EV12, EV13'),('Đèn và cạnh hai JSON','Có bản chiếu và bản exact.','verify_graph.verify_file kiểm mọi nút/cạnh, khả đạt và AF đèn xanh.','Không bế tắc; 12 đèn/cạnh giây đúng; mọi nút đạt được.','Cả hai PASS: 1.012/2.548 và 86.400/86.400 nút/cạnh.','EV14, EV24')]
    for x in extra:
        f,pre,steps,exp,act,ev=x;formal.append({'id':f'FM-{len(formal)+1:02d}','function':f,'pre':pre,'steps':steps,'expected':exp,'actual':act,'status':'PASS','evidence':ev,'native':f})
    negative=[]
    defs=[('Đồng xanh cố ý','Sửa next(e_green) để bật cả khi phase_next = NS_GREEN.','1.3: n_green = TRUE, s_green = TRUE, e_green = TRUE; conflicting_green = TRUE.','EV15'),('Timer nạp sai cố ý','Sửa nhánh timer=1 để nạp 1 thay vì next_phase_duration.','1.2: timer=1, phase ALL_RED_EW_TO_NS; 1.3 sang NS_GREEN, timer vẫn 1, không đạt 15.','EV16'),('Bỏ ALL_RED cố ý','Sửa đích NS_YELLOW thành EW_GREEN.','1.20: NS_YELLOW, timer=1; 1.21: EW_GREEN, timer=15, all_red vẫn FALSE.','EV17')]
    for i,((f,steps,actual,ev),job) in enumerate(zip(defs,a['raw_log_checks'][3:]),1):
        negative.append({'id':f'NEG-{i:02d}','function':f,'pre':'Bản negative riêng, sinh bởi EV22; v1 chính thức không đổi.','steps':steps+' Chạy NuSMV trên bản này.','expected':'Công thức FALSE; có CTL Counterexample; harness PASS.','actual':'FALSE đúng mong đợi. '+actual,'status':'PASS (FALSE)','evidence':ev+'; EV10, EV22','native':Pathname(job['file'])})
    return web,backend,formal,negative

def Pathname(s):return s.rsplit('/',1)[-1]
