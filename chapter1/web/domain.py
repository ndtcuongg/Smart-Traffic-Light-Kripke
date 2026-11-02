"""Web adapter over the existing Chapter 1 controller; no frontend transition rules."""
from pathlib import Path
from dataclasses import asdict
from collections import deque
import sys,json,hashlib,re,threading
HERE=Path(__file__).resolve().parent
CHAPTER=HERE.parent
ROOT=CHAPTER.parent
sys.path.insert(0,str(CHAPTER))
from intersection import Config,State,PHASES,PERIODS,NEXT,POLES,COLORS,initial,step,lamps,label,sid,abstract,exact_graph,hhmmss,seconds
from nusmv_model import generate
PHASE_VI={'NS_GREEN':'Bắc–Nam xanh','NS_YELLOW':'Bắc–Nam vàng','ALL_RED_NS_TO_EW':'Đỏ toàn hướng · sang Đông–Tây','EW_GREEN':'Đông–Tây xanh','EW_YELLOW':'Đông–Tây vàng','ALL_RED_EW_TO_NS':'Đỏ toàn hướng · sang Bắc–Nam'}
PERIOD_VI={'MORNING_PEAK':'Cao điểm sáng','NORMAL':'Bình thường','EVENING_PEAK':'Cao điểm chiều','NIGHT_LOW':'Thấp điểm ban đêm'}
POLE_VI={'n':'Bắc','s':'Nam','e':'Đông','w':'Tây'}
COLOR_VI={'red':'Đỏ','yellow':'Vàng','green':'Xanh'}
CATEGORY_VI={'safety':'An toàn','mutex':'Loại trừ lẫn nhau','liveness':'Tính sống','deadlock':'Không bế tắc','timer':'Timer chính xác','adaptive':'Thích nghi','clock':'Đồng hồ','transition':'Chuyển pha','reachability':'Khả đạt'}

def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def normal_formula(value):return re.sub(r'[\s()]','',value)

def protected_files():
    paths=[ROOT/'test.smv',ROOT/'CHAPTER1.md']
    for base in [CHAPTER,ROOT/'Smart-Traffic-Light-Verification',ROOT/'output',ROOT/'scripts']:
        paths.extend(p for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_relative_to(HERE))
    return {p.relative_to(ROOT).as_posix():digest(p) for p in paths if p.is_file()}

def verify_preservation(expected):
    return {'status':'PASS' if all((ROOT/p).is_file() and digest(ROOT/p)==h for p,h in expected.items()) else 'FAIL',
        'checked_files':len(expected),'changed':[p for p,h in expected.items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]}

def describe_property(name,formula):
    if name=='physical_green_exclusion':return 'Không cột Bắc/Nam nào cùng xanh với cột Đông/Tây; kiểm trên các đầu ra đèn riêng biệt.'
    if name.startswith('one_hot_'):return 'Mỗi cột chỉ có đúng một đèn bật: đỏ, vàng hoặc xanh.'
    if name.startswith('synchronized_'):return 'Bắc đồng bộ với Nam; Đông đồng bộ với Tây cho màu đèn tương ứng.'
    if name.startswith('recurring_green_'):return 'Từ mọi trạng thái đạt được, hướng này cuối cùng lại nhận đèn xanh.'
    if name.startswith('yellow_'):return 'Khi một luồng đang vàng, mọi đèn của luồng vuông góc phải đỏ.'
    if name=='clearance_all_red':return 'Trong hai pha dọn giao lộ, cả bốn hướng đều bật đèn đỏ.'
    if name=='deadlock_free':return 'Mọi trạng thái đạt được đều còn ít nhất một chuyển tiếp hợp lệ.'
    if name=='timer_bounds':return 'Timer luôn dương và không vượt thời lượng chốt lúc bắt đầu pha.'
    if name.startswith('countdown_'):return 'Khi còn '+name.split('_')[-1]+' giây, bước kế tiếp giảm chính xác một giây.'
    if name.startswith('hold_'):return 'Giữ pha hiện tại khi timer còn lớn hơn một; không chuyển pha sớm.'
    if name.startswith('advance_'):return 'Khi timer bằng một, bước kế tiếp phải đến đúng pha trong chu kỳ an toàn.'
    if name.startswith('reset_'):return 'Nạp timer theo pha đích và khung giờ mới; chốt entry_period đồng thời.'
    if name.startswith('latch_'):return 'Giữ khung giờ chốt trong pha đang chạy, kể cả khi đồng hồ qua mốc đổi giờ.'
    if name.startswith('clock_second_'):return 'Giây tăng đúng một bước và quay về 0 sau giây 59.'
    if name.startswith('clock_minute_tick_'):return 'Phút chỉ tăng khi giây chuyển 59→0; quay về 0 sau phút 59.'
    if name.startswith('clock_minute_hold_'):return 'Giữ nguyên phút khi chưa đến cuối phút.'
    if name.startswith('clock_hour_tick_'):return 'Giờ tăng ở cuối phút 59, giây 59; 23:59:59 quay về 00:00:00.'
    if name.startswith('clock_hour_hold_'):return 'Giữ nguyên giờ khi chưa đến cuối giờ.'
    if name.startswith('reachable_'):return 'Tồn tại đường đi từ trạng thái khởi tạo đến pha được chỉ định.'
    if formula.startswith('EF(period'):return 'Khung giờ này thực sự đạt được trên mô hình có đồng hồ 24 giờ.'
    if formula.startswith('AF('):return 'Trên mọi nhánh, cuối cùng đạt nhãn đích; kiểm từ trạng thái khởi tạo.'
    if formula.startswith('AG('):return 'Mệnh đề bên trong đúng ở mọi trạng thái có thể đạt được.'
    if formula.startswith('EG('):return 'Tồn tại một đường đi mà mệnh đề duy trì mãi.'
    if formula.startswith('EF('):return 'Có một đường đi đến trạng thái thỏa nhãn đích.'
    return 'Công thức được kiểm trên cấu trúc Kripke và tập trạng thái khởi tạo đã khai báo.'

class Model:
    def __init__(self):
        self.config=Config(CHAPTER/'config.json')
        self.graph=read_json(CHAPTER/'smart_intersection.json')
        self.summary=read_json(CHAPTER/'evidence/build_summary.json')
        self.props=read_json(CHAPTER/'properties.json')
        self.audit=read_json(CHAPTER/'evidence/before_after_audit.json')
        self._exact=None;self._exact_lock=threading.Lock()
        self.abstract_ids=self.graph['states'];self.abstract_index={n:i for i,n in enumerate(self.abstract_ids)}
        self.successors={n:[] for n in self.abstract_ids};self.predecessors={n:[] for n in self.abstract_ids}
        for a,b in self.graph['transitions']:self.successors[a].append(b);self.predecessors[b].append(a)
        self.source_hashes={'model':digest(CHAPTER/'smart_intersection.smv'),'config':digest(CHAPTER/'config.json'),'json':digest(CHAPTER/'smart_intersection.json')}
        self.integrity=(self.source_hashes['model']==self.audit['official_after_sha256'] and self.source_hashes['config']==self.summary['config_sha256'])
        generated,_=generate(self.config)
        self.generator_matches=generated==(CHAPTER/'smart_intersection.smv').read_text(encoding='utf-8')
    def exact(self):
        with self._exact_lock:
            if self._exact is None:
                values,edges,loop=exact_graph(self.config)
                ids=[sid(s) for s in values];index={n:i for i,n in enumerate(ids)};pred=[[] for _ in values]
                for i,row in enumerate(edges):
                    for j in row:pred[j].append(i)
                self._exact=(values,edges,ids,index,pred,loop)
        return self._exact
    def serialize(self,state,estimates=True):
        nxt=step(self.config,state);light=lamps(state.phase)
        result={**asdict(state),'id':sid(state),'clock_text':hhmmss(state.clock),'phase_vi':PHASE_VI[state.phase],
            'period_vi':PERIOD_VI[state.period],'entry_period_vi':PERIOD_VI[state.entry_period],
            'phase_duration':self.config.duration(state.phase,state.entry_period),'next_phase':NEXT[state.phase],
            'next_phase_vi':PHASE_VI[NEXT[state.phase]],'next_step_phase':nxt.phase,'lamps':light,
            'labels':label(self.config,state,[nxt]),'safe':not((light['n_green'] or light['s_green']) and(light['e_green'] or light['w_green']))}
        if estimates:
            colors={p:next(c for c in COLORS if light[p+'_'+c]) for p in POLES}
            waits={p:{'color':colors[p],'color_vi':COLOR_VI[colors[p]],'until_green':0 if colors[p]=='green' else None,'color_remaining':None} for p in POLES}
            cursor=state
            for elapsed in range(1,self.config.maximum*6+2):
                cursor=step(self.config,cursor);future=lamps(cursor.phase)
                for p in POLES:
                    if waits[p]['until_green'] is None and future[p+'_green']:waits[p]['until_green']=elapsed
                    if waits[p]['color_remaining'] is None and not future[p+'_'+colors[p]]:waits[p]['color_remaining']=elapsed
                if all(w['until_green'] is not None and w['color_remaining'] is not None for w in waits.values()):break
            result['directions']=waits
        return result
    def state_from_id(self,ident):
        m=re.fullmatch(r'(?:t(\d{5})__)?([A-Z_]+)__r(\d{3})__now_([A-Z_]+)__entry_([A-Z_]+)',ident)
        if not m:raise ValueError('Mã trạng thái không hợp lệ.')
        clock,q,r,p,e=m.groups()
        if q not in PHASES or p not in PERIODS or e not in PERIODS:raise ValueError('Trạng thái không thuộc miền mô hình.')
        r=int(r);clock=None if clock is None else int(clock)
        if not 1<=r<=self.config.duration(q,e) or(clock is not None and(not 0<=clock<86400 or self.config.period(clock)!=p)):
            raise ValueError('Timer hoặc khung giờ không hợp lệ.')
        return State(q,r,p,e,clock)
    def state_item(self,ident,mode='abstract',allow_live=False):
        if mode=='abstract':
            if ident not in self.abstract_index:raise ValueError('Trạng thái không nằm trong tập S xấp xỉ.')
            outgoing=self.successors[ident];incoming=self.predecessors[ident];state=self.state_from_id(ident)
            labels=self.graph['labeling'][ident];initial_state=ident in self.graph['initial'];member=True
        else:
            values,edges,ids,index,pred,loop=self.exact();member=ident in index
            if not member and not allow_live:raise ValueError('Trạng thái không thuộc quỹ đạo khởi tạo mặc định.')
            state=self.state_from_id(ident)
            if state.clock is None:raise ValueError('Thiếu đồng hồ chính xác.')
            nxt=step(self.config,state);outgoing=[sid(nxt)];incoming=[ids[j] for j in pred[index[ident]]] if member else []
            labels=label(self.config,state,[nxt]);initial_state=member and index[ident]==0
        def brief(n):
            v=self.state_from_id(n)
            return {'id':n,**asdict(v),'phase_vi':PHASE_VI[v.phase],'period_vi':PERIOD_VI[v.period],'clock_text':hhmmss(v.clock) if v.clock is not None else None}
        return {**brief(ident),'labels':labels,'lamps':lamps(state.phase),'is_initial':initial_state,'in_default_state_set':member,
            'successors':[brief(n) for n in outgoing],'predecessors':[brief(n) for n in incoming[:8]],'predecessor_count':len(incoming),
            'kind':'exact' if mode=='exact' else 'abstract','state_count':len(self.exact()[0]) if mode=='exact' else len(self.abstract_ids),
            'edge_count':sum(len(e) for e in self.exact()[1]) if mode=='exact' else len(self.graph['transitions']),
            'initial_id':self.exact()[2][0] if mode=='exact' else self.graph['initial'][0]}
    def search(self,mode='abstract',query='',phase='',period='',offset=0,limit=20):
        ids=self.exact()[2] if mode=='exact' else self.abstract_ids
        q=query.casefold();matches=[]
        for ident in ids:
            if q and q not in ident.casefold():continue
            if phase and not re.search(r'(?:^|__)'+re.escape(phase)+r'__r',ident):continue
            if period and '__now_'+period+'__' not in ident:continue
            matches.append(ident)
        return {'total':len(ids),'matches':len(matches),'offset':offset,'limit':limit,'items':[{'id':n,**asdict(self.state_from_id(n))} for n in matches[offset:offset+limit]]}
    def comparisons(self):
        text=(CHAPTER/'BEFORE_AFTER_V0_V1.md').read_text(encoding='utf-8')
        parts=re.split(r'(?m)^### (V0-\d\d) — ',text)[1:];sections={}
        for i in range(0,len(parts),2):
            block=parts[i+1].split('\n## ',1)[0];details={}
            for m in re.finditer(r'(?m)^([1-5])\. \*\*([^*]+)\*\* (.+)$',block):details[m[1]]=re.sub(r'[`*]','',m[3])
            sections[parts[i]]=details
        result=[]
        for record in self.audit['mapping']:
            p=ROOT/record['source_file'];body=p.read_text(encoding='utf-8-sig')
            result.append({**record,'details':sections.get(record['id'],{}),'source_text':body,
                'source_hash_matches':digest(p)==record['source_sha256'],
                'v1_properties':[r for r in self.props if r['name'] in record['v1_property_names']]})
        return result
