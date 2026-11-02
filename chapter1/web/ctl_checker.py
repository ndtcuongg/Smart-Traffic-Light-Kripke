"""Independent Chapter 1 CTL checker for the supported JSON formulas. No EXE dependency."""
import re
from collections import deque

def check_graph(document):
    names=document['states'];nodes=set(names);initial=set(document['initial']);labels=document['labeling']
    if len(nodes)!=len(names) or not initial or not initial<=nodes or set(labels)!=nodes:raise ValueError('Cấu trúc Kripke không nhất quán.')
    succ={n:set() for n in names};pred={n:set() for n in names}
    for a,b in document['transitions']:
        if a not in nodes or b not in nodes:raise ValueError('Cạnh tham chiếu trạng thái không tồn tại.')
        succ[a].add(b);pred[b].add(a)
    dead=[n for n in names if not succ[n]]
    if dead:raise ValueError('Quan hệ chuyển tiếp không toàn phần: có trạng thái bế tắc.')
    def ef(goal):
        found=set(goal);q=deque(found)
        while q:
            for p in pred[q.popleft()]:
                if p not in found:found.add(p);q.append(p)
        return found
    def af(goal):
        found=set(goal);q=deque(found);left={n:len(succ[n]) for n in names}
        while q:
            for p in pred[q.popleft()]:
                if p in found:continue
                left[p]-=1
                if left[p]==0:found.add(p);q.append(p)
        return found
    def eg(goal):
        kept=set(goal);degree={n:len(succ[n]&kept) for n in kept};q=deque(n for n in kept if degree[n]==0)
        while q:
            n=q.popleft()
            if n not in kept:continue
            kept.remove(n)
            for p in pred[n]&kept:
                degree[p]-=1
                if degree[p]==0:q.append(p)
        return kept
    results=[]
    for formula in document['suggested_ctl_formulas']:
        m=re.fullmatch(r'(AG|AF|EF|EG|AX|EX)\((!?)([A-Za-z_]\w*)\)',formula)
        if not m:raise ValueError('Cú pháp CTL chưa được hỗ trợ: '+formula)
        op,neg,atom=m.groups();goal={n for n in names if atom in labels[n]}
        if neg:goal=nodes-goal
        if op=='EF':sat=ef(goal)
        elif op=='AF':sat=af(goal)
        elif op=='EG':sat=eg(goal)
        elif op=='AG':sat=nodes-ef(nodes-goal)
        elif op=='EX':sat={n for n in names if succ[n]&goal}
        else:sat={n for n in names if succ[n]<=goal}
        holds=initial<=sat
        results.append({'formula':formula,'result':holds,'status':'PASS' if holds else 'FAIL','satisfying_states':len(sat),'initial_not_satisfied':sorted(initial-sat)})
    reachable=set(initial);q=deque(initial)
    while q:
        for n in succ[q.popleft()]:
            if n not in reachable:reachable.add(n);q.append(n)
    bad=[n for n in reachable if 'ns_go' in labels[n] and 'ew_go' in labels[n]]
    return {'tool':'Bộ kiểm CTL độc lập bằng Python','states':len(names),'transitions':sum(map(len,succ.values())),
        'reachable_states':len(reachable),'properties':results,'mutex':{'status':'PASS' if not bad else 'FAIL','violating_states':bad},
        'deadlock_states':dead,'overall':'PASS' if all(r['result'] for r in results) and not bad else 'FAIL'}
