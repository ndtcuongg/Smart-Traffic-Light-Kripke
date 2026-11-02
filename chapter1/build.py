"""Build Chapter 1 artifacts only. Never calls the interrupted Excel workflow."""
from pathlib import Path
import argparse,json,hashlib
from intersection import Config,exact_graph,abstract_graph,write_spec,sid,abstract,step,rule_flags,lamps,PROPERTIES
from nusmv_model import generate
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(config=None,state_limit=1000000):
    cfg=Config(config or HERE/'config.json')
    evidence=HERE/'evidence'; evidence.mkdir(exist_ok=True)
    baseline=evidence/'preserved_work.json'
    if not baseline.exists():
        paths=list((ROOT/'Smart-Traffic-Light-Verification').rglob('*'))+list((ROOT/'output').glob('*'))+[ROOT/'test.smv',ROOT/'scripts/generate_spec.py']
        baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths if p.is_file()},ensure_ascii=False,indent=2),encoding='utf-8')
    av,ae=abstract_graph(cfg); ev,ee,loop=exact_graph(cfg,state_limit)
    adoc=write_spec(HERE/'smart_intersection.json',cfg,av,ae,
        'Chuong 1: giao lo bon huong, 12 den ON/OFF, 1 buoc = 1 giay. Trang thai gom pha, timer, khung gio hien tai va khung gio chot khi vao pha. Dong ho 24 gio duoc chieu xuong khung gio; cho phep doi khung gio theo cac canh hop le (over-approximation), nen bao toan tinh an toan va song con khi kiem tren moi nhanh. Dong ho chinh xac: smart_intersection_exact.json va smart_intersection.smv. Khong co ham sinh ma, SMT hay fuzzing.')
    write_spec(HERE/'smart_intersection_exact.json',cfg,ev,ee,
        'Do thi Kripke dat duoc CHINH XAC cua smart_intersection.smv voi config mac dinh; clock giay 0..86399, timer >=1 va 12 trang thai den ON/OFF. Chi dung parser Ch1; do thi lon, uu tien JSON rut gon cho giao dien.')
    model,props=generate(cfg)
    (HERE/'smart_intersection.smv').write_text(model,encoding='utf-8')
    (HERE/'properties.json').write_text(json.dumps(props,indent=2),encoding='utf-8')
    # Verify a simulation relation: every concrete one-second transition is an abstract edge.
    aindex={s:i for i,s in enumerate(av)}
    for i,s in enumerate(ev):
        a=aindex[abstract(s)]
        for j in ee[i]:
            b=aindex[abstract(ev[j])]
            if b not in ae[a]: raise AssertionError(('Projection mismatch',sid(s)))
        if not all(rule_flags(cfg,s,[ev[j] for j in ee[i]]).values()): raise AssertionError(('Rule violation',sid(s)))
    for i,s in enumerate(av):
        if not all(rule_flags(cfg,s,[av[j] for j in ae[i]]).values()): raise AssertionError(('Abstract rule violation',sid(s)))
    # Complete DOT diagrams: these files contain every state and every transition.
    for name,values,edges in [('kripke_full',av,ae),('kripke_exact',ev,ee)]:
        with (HERE/(name+'.dot')).open('w',encoding='utf-8') as f:
            f.write('digraph Kripke {\nrankdir=LR;\nnode [shape=box,fontname="Consolas",fontsize=8];\nstart [shape=point]; start -> n0;\n')
            for i,s in enumerate(values):
                text=sid(s)+'\\n'+', '.join(k+'='+('ON' if v else 'OFF') for k,v in lamps(s.phase).items())
                f.write(f'n{i} [label="{text}"];\n')
            for i,targets in enumerate(edges):
                for j in targets: f.write(f'n{i} -> n{j} [label="1s"];\n')
            f.write('}\n')
    summary={'config_sha256':sha(config or HERE/'config.json'),'concrete_states':len(ev),'concrete_transitions':sum(map(len,ee)),
        'concrete_loop_start_index':loop,'abstract_states':len(av),'abstract_transitions':sum(map(len,ae)),
        'initial_state':sid(ev[0]),'exact_to_abstract_simulation':'PASS','all_state_and_edge_rules':'PASS',
        'exact_periods':sorted({s.period for s in ev}),'exact_phases':sorted({s.phase for s in ev}),
        'lamp_boolean_count':12,'json_ctl_properties':len(PROPERTIES),'nusmv_properties':len(props),
        'json_top_level_keys':list(adoc)}
    (evidence/'build_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return cfg,av,ae,ev,ee

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path);p.add_argument('--state-limit',type=int,default=1000000)
    args=p.parse_args();build(args.config,args.state_limit)
