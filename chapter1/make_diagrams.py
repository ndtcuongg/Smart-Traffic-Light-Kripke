"""Readable SVG and local interactive diagrams, all derived from the actual models."""
from pathlib import Path
import json,html,math
from intersection import Config,PHASES,PERIODS,initial,step,lamps,hhmmss
HERE=Path(__file__).resolve().parent

def svg_start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title)}">',
    '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10Z" fill="#55718a"/></marker></defs>',
    f'<rect width="{w}" height="{h}" fill="#f3f6fa"/>',
    '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#19344c}.title{font-size:27px;font-weight:700}.sub{font-size:15px;fill:#526b80}.box{fill:#fff;stroke:#bac9d6;stroke-width:1.4}.name{font-size:17px;font-weight:700}.mono{font-family:Consolas,monospace;font-size:12px}.link{fill:none;stroke:#55718a;stroke-width:1.6;marker-end:url(#arrow)}</style>',
    f'<text class="title" x="35" y="45">{html.escape(title)}</text>']

def figures():
    cfg=Config(HERE/'config.json');parts=svg_start(1400,980,'Kripke — giao lộ bốn hướng có thời gian')
    parts.append('<text class="sub" x="35" y="77">Mỗi cạnh = 1 giây. Hình này mô tả tham số; DOT và JSON chứa toàn bộ trạng thái và cạnh.</text>')
    positions=[(40,120),(500,120),(960,120),(960,360),(500,360),(40,360)]
    for i,(phase,(x,y)) in enumerate(zip(PHASES,positions)):
        parts.append(f'<rect class="box" x="{x}" y="{y}" width="400" height="175" rx="12"/>')
        parts.append(f'<text class="name" x="{x+16}" y="{y+30}">{phase}</text>')
        states=lamps(phase)
        for row,p in enumerate(('n','s','e','w')):
            parts.append(f'<text class="mono" x="{x+16}" y="{y+56+row*23}">{p.upper()}</text>')
            for cidx,color in enumerate(('red','yellow','green')):
                active=states[f'{p}_{color}'];cx=x+52+cidx*100;cy=y+52+row*23
                fill={'red':'#d84545','yellow':'#e7b62c','green':'#299c67'}[color] if active else '#dce4eb'
                parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{fill}"/><text class="mono" x="{cx+12}" y="{cy+4}">{color[0].upper()}:{"ON" if active else "OFF"}</text>')
        nx,ny=positions[(i+1)%6]
        if y==ny:
            sx,ex=(x+400,nx) if nx>x else (x,nx+400)
            parts.append(f'<path class="link" d="M{sx} {y+85} L{ex} {ny+85}"/>')
        else:
            parts.append(f'<path class="link" d="M{x+200} {y+175 if ny>y else y} L{nx+200} {ny if ny>y else ny+175}"/>')
    lines=[
'S = (phase, remaining, current_period, entry_period, clock, 12 lamp booleans).',
'Countdown: (phase,r,p,e) → (phase,r−1,p′,e) khi r > 1.',
'Đổi pha: (phase,1,p,e) → (next_phase,D(next_phase,p′),p′,p′).',
'Clock: 23:59:59 → 00:00:00; current_period lấy từ clock mới.',
'entry_period được chốt tại đầu pha; đổi khung giờ không cắt ngắn pha đang chạy.',
'JSON cho GUI: 1.012 trạng thái / 2.548 cạnh; giữ timer từng giây, chiếu clock xuống period.',
'JSON chính xác: 86.400 trạng thái / 86.400 cạnh; đầy đủ clock 24 giờ với cấu hình mặc định.',
'Mọi lamp ON/OFF được ghi rõ trong labeling, không chỉ dùng một biến phase.'
]
    for i,line in enumerate(lines):parts.append(f'<text class="sub" x="40" y="{590+i*29}">{html.escape(line)}</text>')
    parts.append('<text class="name" x="40" y="855">Thời lượng theo entry_period (giây)</text>')
    for i,p in enumerate(PERIODS):
        d=cfg.durations[p]
        parts.append(f'<text class="sub" x="40" y="{884+i*23}">{p}: NS_GREEN={d["NS_GREEN"]}; EW_GREEN={d["EW_GREEN"]}; YELLOW={d["NS_YELLOW"]}; ALL_RED={d["ALL_RED_NS_TO_EW"]}</text>')
    parts.append('</svg>');(HERE/'kripke_overview.svg').write_text('\n'.join(parts),encoding='utf-8')
    # A concrete second-by-second trace crossing 07:00 while NS is GREEN.
    states=[];s=initial(cfg,6*3600+59*60+55,'NS_GREEN')
    for _ in range(34):states.append(s);s=step(cfg,s)
    rows=math.ceil(len(states)/3);parts=svg_start(1410,120+rows*180,'Vết Kripke chi tiết — đổi NORMAL → MORNING_PEAK lúc 07:00')
    parts.append('<text class="sub" x="35" y="77">Ca kiểm thử khởi tạo lúc 06:59:55 trong NS_GREEN; đọc từ trái sang phải, trên xuống dưới.</text>')
    for i,s in enumerate(states):
        x=20+(i%3)*465;y=110+(i//3)*180
        color='#e7f4ee' if s.period!=s.entry_period else '#ffffff'
        parts.append(f'<rect x="{x}" y="{y}" width="440" height="155" rx="9" fill="{color}" stroke="#b7c8d6"/>')
        text=[f'{i:02d} | {hhmmss(s.clock)} | {s.phase} | timer={s.remaining}',f'now={s.period}; entry={s.entry_period}']
        lights=lamps(s.phase)
        text += [p.upper()+': '+ ' '.join(c[0].upper()+':'+('ON' if lights[f'{p}_{c}'] else 'OFF') for c in ('red','yellow','green')) for p in ('n','s','e','w')]
        for j,line in enumerate(text):parts.append(f'<text class="mono" x="{x+10}" y="{y+23+j*22}">{html.escape(line)}</text>')
        if i%3<2 and i+1<len(states):parts.append(f'<path class="link" d="M{x+440} {y+70} L{x+465} {y+70}"/>')
        elif i+1<len(states):parts.append(f'<path class="link" d="M{x+220} {y+155} L{x+220} {y+170} L240 {y+170} L240 {y+180}"/>')
    parts.append('</svg>');(HERE/'kripke_boundary.svg').write_text('\n'.join(parts),encoding='utf-8')
    (HERE/'evidence/boundary_trace.json').write_text(json.dumps([{'clock':hhmmss(s.clock),'phase':s.phase,'remaining':s.remaining,'period':s.period,'entry_period':s.entry_period,'lamps':lamps(s.phase)} for s in states],indent=2),encoding='utf-8')
    doc=json.loads((HERE/'smart_intersection.json').read_text(encoding='utf-8'));packed=json.dumps(doc,ensure_ascii=False).replace('</','<\\/')
    page=r'''<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kripke Explorer — Smart Intersection</title><style>
body{margin:0;background:#f3f6fa;color:#19344c;font:16px system-ui}main{max-width:1160px;margin:auto;padding:28px}h1{margin-bottom:8px}p{line-height:1.6}.panel{background:white;border:1px solid #c8d5e0;border-radius:14px;padding:20px;margin:16px 0}select,input,button{font:inherit;padding:10px;border-radius:7px;border:1px solid #9aafc1;max-width:100%}select{width:100%}input{width:70%}button{cursor:pointer;background:#e6eef7;margin:4px}svg{width:100%;height:auto}code{word-break:break-all}#lamps{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.pole{padding:15px;background:#17334d;color:white;border-radius:12px}.light{display:block;margin:8px 0}.bulb{display:inline-block;width:16px;height:16px;border-radius:50%;margin-right:8px;background:#526477}.on.red{background:#f05b5b}.on.yellow{background:#f3c84b}.on.green{background:#44ce92}li{margin:10px 0}.hint{color:#526b80;font-size:14px}</style><main>
<h1>Kripke Explorer · Giao lộ bốn hướng</h1><p>Đồ thị JSON tương thích Chương 1 của SecLabFramework. Mỗi cạnh là một giây. Timer được giữ đầy đủ; clock 24 giờ được chiếu xuống khung giờ, cho phép nhiều nhánh đổi khung giờ để kiểm tra an toàn trên mọi nhánh.</p>
<div class="panel"><label for="search">Lọc theo pha, timer hoặc khung giờ</label><p><input id="search" placeholder="Ví dụ: NS_GREEN__r001 hoặc NIGHT_LOW"><button id="filter">Lọc</button><button id="reset">Về S₀</button></p><label for="state">Chọn một trong <span id="count"></span> trạng thái</label><select id="state"></select></div>
<div class="panel"><h2>Trạng thái và 12 đèn ON/OFF</h2><p><code id="name"></code></p><div id="lamps"></div><p id="meta"></p></div>
<div class="panel"><h2>Các chuyển tiếp thật từ trạng thái đang chọn</h2><svg id="graph" viewBox="0 0 1080 360" aria-label="Đồ thị lân cận"></svg><ul id="next"></ul><p class="hint">Bấm trạng thái đích để đi thêm 1 giây. Tất cả cạnh hiển thị được đọc trực tiếp từ JSON, không suy diễn chỉ từ sáu pha.</p></div>
<div class="panel"><h2>Nhãn và công thức kiểm chứng</h2><p id="labels"></p><pre id="formulas"></pre><p class="hint">Đồ thị đầy đủ: kripke_full.dot (1.012 trạng thái) và kripke_exact.dot (86.400 trạng thái). Thống kê áp dụng cho config mặc định.</p></div></main>
<script id="data" type="application/json">DATA_HERE</script><script>
const d=JSON.parse(document.getElementById('data').textContent),el=id=>document.getElementById(id),out=new Map(d.states.map(s=>[s,[]]));for(const [a,b]of d.transitions)out.get(a).push(b);let current=d.initial[0];el('count').textContent=d.states.length;el('formulas').textContent=d.suggested_ctl_formulas.join('\n');
function options(filter=''){el('state').replaceChildren();for(const n of d.states)if(n.toLowerCase().includes(filter.toLowerCase())){const o=document.createElement('option');o.value=n;o.textContent=n;el('state').append(o)}el('state').value=current}
function select(n){current=n;if(![...el('state').options].some(o=>o.value===n))options();el('state').value=n;render()}
function render(){const labs=new Set(d.labeling[current]);el('name').textContent=current;el('labels').textContent=[...labs].join(', ');el('lamps').replaceChildren();for(const p of ['n','s','e','w']){const b=document.createElement('div');b.className='pole';const title=document.createElement('strong');title.textContent={n:'Bắc · North',s:'Nam · South',e:'Đông · East',w:'Tây · West'}[p];b.append(title);for(const c of ['red','yellow','green']){const row=document.createElement('span');row.className='light';const dot=document.createElement('span');const on=labs.has(p+'_'+c+'_on');dot.className='bulb '+c+(on?' on':'');row.append(dot,document.createTextNode(c.toUpperCase()+': '+(on?'ON':'OFF')));b.append(row)}el('lamps').append(b)}el('meta').textContent=[...labs].filter(x=>/^(phase_|period_|entry_|timer_)/.test(x)).join(' · ');el('next').replaceChildren();const targets=out.get(current),svg=el('graph'),NS='http://www.w3.org/2000/svg';svg.replaceChildren();svg.setAttribute('viewBox','0 0 1080 '+Math.max(240,targets.length*100));function node(x,y,title,detail,fill){const g=document.createElementNS(NS,'g');const r=document.createElementNS(NS,'rect');for(const[k,v]of Object.entries({x,y,width:430,height:76,rx:10,fill,stroke:'#9aafc1'}))r.setAttribute(k,v);g.append(r);for(const[t,dy]of [[title,28],[detail,54]]){const text=document.createElementNS(NS,'text');text.setAttribute('x',x+12);text.setAttribute('y',y+dy);text.setAttribute('font-size','12');text.textContent=t;g.append(text)}svg.append(g);return g}const cy=Math.max(40,targets.length*50-38);node(5,cy,current.split('__')[0],current.split('__').slice(1).join(' / '),'#e7f0fc');targets.forEach((n,i)=>{const y=i*100+12,line=document.createElementNS(NS,'path');line.setAttribute('d',`M435 ${cy+38} L625 ${y+38}`);line.setAttribute('stroke','#55718a');line.setAttribute('fill','none');svg.append(line);const g=node(635,y,n.split('__')[0],n.split('__').slice(1).join(' / '),'#e7f4ee');g.style.cursor='pointer';g.addEventListener('click',()=>select(n));const li=document.createElement('li'),b=document.createElement('button');b.textContent='1 giây → '+n;b.onclick=()=>select(n);li.append(b);el('next').append(li)})}
el('state').onchange=()=>select(el('state').value);el('filter').onclick=()=>options(el('search').value);el('search').onkeydown=e=>{if(e.key==='Enter')options(el('search').value)};el('reset').onclick=()=>{el('search').value='';options();select(d.initial[0])};options();render();</script></html>'''
    (HERE/'kripke_explorer.html').write_text(page.replace('DATA_HERE',packed),encoding='utf-8')
    print('Generated kripke_overview.svg, kripke_boundary.svg and kripke_explorer.html')
if __name__=='__main__':figures()
