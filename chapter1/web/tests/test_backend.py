"""HTTP/kernel regression tests. Writes only chapter1/web/evidence/backend_tests.json."""
from pathlib import Path
import sys,unittest,threading,urllib.request,urllib.error,http.cookiejar,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import LocalServer
from domain import HERE,ROOT,CHAPTER,Config,initial,step,lamps,sid,abstract,read_json,digest,verify_preservation
from ctl_checker import check_graph

class Client:
    def __init__(self,url):
        self.url=url;self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));self.token=None
    def call(self,path,body=None):
        req=urllib.request.Request(self.url+path,data=None if body is None else json.dumps(body).encode(),headers={} if body is None else {'X-Demo-Token':self.token or '', 'Content-Type':'application/json'})
        with self.opener.open(req,timeout=30) as r:return json.load(r)

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=LocalServer(0,HERE/'evidence/test_runs');cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url='http://127.0.0.1:'+str(cls.server.server_port);cls.cfg=Config(CHAPTER/'config.json')
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def setUp(self):self.c=Client(self.url);self.b=self.c.call('/api/bootstrap');self.c.token=self.b['token']
    def reset(self,clock=0,warmup=0):return self.c.call('/api/simulation/reset',{'clock':clock,'warmup':warmup})
    def tick(self,n=1):return self.c.call('/api/simulation/step',{'count':n})
    def test_01_all_lights_synchronization_exclusion_full_day(self):
        # Exhaustive kernel day plus representative HTTP cycle; UI tested separately.
        s=initial(self.cfg);phases=set()
        for _ in range(86400):
            v=lamps(s.phase);self.assertEqual(len(v),12)
            for p in 'nsew':self.assertEqual(sum(v[p+'_'+c] for c in ('red','yellow','green')),1)
            for c in ('red','yellow','green'):self.assertEqual(v['n_'+c],v['s_'+c]);self.assertEqual(v['e_'+c],v['w_'+c])
            self.assertFalse(v['n_green'] and v['e_green']);phases.add(s.phase);s=step(self.cfg,s)
        self.assertEqual(phases,set(self.b['phases']))
    def test_02_cycle_countdown_reload_clearance(self):
        self.reset();history=[self.b['state']]+self.tick(80)['history'];order=[]
        for a,b in zip(history,history[1:]):
            if not order or order[-1]!=a['phase']:order.append(a['phase'])
            if a['remaining']>1:self.assertEqual(b['phase'],a['phase']);self.assertEqual(b['remaining'],a['remaining']-1);self.assertEqual(b['entry_period'],a['entry_period'])
            else:
                nxt=self.b['phases'][(self.b['phases'].index(a['phase'])+1)%6];self.assertEqual(b['phase'],nxt);self.assertEqual(b['remaining'],self.cfg.duration(nxt,b['period']))
                if nxt.startswith('ALL_RED'):self.assertEqual(b['remaining'],2)
        self.assertEqual(order[:7],['ALL_RED_EW_TO_NS']+self.b['phases'][:])
    def test_03_every_boundary_latches(self):
        points=[21600,25200,32400,57600,68400,79200,86400]
        for boundary in points:
            with self.subTest(boundary=boundary):
                a=self.reset(boundary-1,12);b=self.tick();self.assertEqual(b['clock'],boundary%86400);self.assertEqual(b['period'],self.cfg.period(boundary%86400));self.assertEqual(a['phase'],b['phase']);self.assertEqual(b['remaining'],a['remaining']-1);self.assertEqual(b['entry_period'],a['entry_period']);self.assertEqual(b['phase_duration'],a['phase_duration'])
    def test_04_http_matches_authoritative_kernel(self):
        for clock,warm in [(0,0),(25199,12),(57599,12),(86399,12),(32000,0)]:
            s=initial(self.cfg,(clock-warm)%86400)
            for _ in range(warm):s=step(self.cfg,s)
            a=self.reset(clock,warm);self.assertEqual(a['id'],sid(s))
            for b in self.tick(120)['history']:
                s=step(self.cfg,s);self.assertEqual(b['id'],sid(s));self.assertEqual(b['lamps'],lamps(s.phase))
    def test_05_direction_countdowns(self):
        a=self.reset(25199,12)
        for pole,d in a['directions'].items():
            s=initial(self.cfg,25187)
            for _ in range(12):s=step(self.cfg,s)
            green=0 if lamps(s.phase)[pole+'_green'] else None;color=None
            for n in range(1,200):
                s=step(self.cfg,s);v=lamps(s.phase)
                if green is None and v[pole+'_green']:green=n
                if color is None and not v[pole+'_'+d['color']]:color=n
            self.assertEqual(green,d['until_green']);self.assertEqual(color,d['color_remaining'])
    def test_06_sessions_reset_input_validation(self):
        self.reset(30000);other=Client(self.url);self.assertEqual(other.call('/api/bootstrap')['state']['clock'],0)
        self.tick(3);self.assertEqual(self.reset(30000)['clock'],30000)
        for body in [{'count':0},{'count':121},{'count':True}]:
            with self.assertRaises(urllib.error.HTTPError):self.c.call('/api/simulation/step',body)
        self.c.token='invalid'
        with self.assertRaises(urllib.error.HTTPError):self.tick()
    def test_07_kripke_s0_labels_neighbors_filters(self):
        from urllib.parse import urlencode
        doc=read_json(CHAPTER/'smart_intersection.json');a=self.c.call('/api/kripke/state?'+urlencode({'id':doc['initial'][0]}));self.assertTrue(a['is_initial']);self.assertEqual(a['labels'],doc['labeling'][a['id']]);self.assertEqual({r['id'] for r in a['successors']},{b for x,b in doc['transitions'] if x==a['id']})
        search=self.c.call('/api/kripke/states?phase=NS_GREEN&period=MORNING_PEAK&limit=7');self.assertEqual(len(search['items']),7);self.assertTrue(all(r['phase']=='NS_GREEN' and r['period']=='MORNING_PEAK' for r in search['items']))
        e=self.c.call('/api/kripke/states?mode=exact&limit=2');self.assertEqual(e['total'],86400);self.assertEqual(len(e['items']),2)
        self.reset(25199,12);live=self.c.call('/api/kripke/current?mode=exact');self.assertEqual(live['id'],self.c.call('/api/simulation')['id']);self.assertEqual(len(live['successors']),1)
    def test_08_recorded_results_match_raw_logs(self):
        v=self.c.call('/api/verification');reports=read_json(CHAPTER/'evidence/nusmv_results.json');main=next(r for r in reports if r['name']=='nusmv_main');self.assertEqual(v['summary']['passed'],sum(r['result'] for r in main['checks']));self.assertEqual(v['summary']['passed'],335);self.assertEqual(v['summary']['ctl_passed'],26);self.assertEqual(v['summary']['reachable_states'],86400);self.assertEqual(v['kind'],'recorded');self.assertIsNone(v['started_at']);self.assertTrue(all(not r['property_result'] and r['harness_status']=='PASS' for r in v['negative']))
        log=self.c.call('/api/artifact?path=chapter1/evidence/negative_conflicting_green.log')['text'];self.assertIn('is false',log);self.assertIn('Trace',log)
    def test_09_comparison_14_originals(self):
        rows=self.c.call('/api/comparisons')['items'];self.assertEqual(len(rows),14)
        for r in rows:
            self.assertEqual(set(r['details']),set('12345'));self.assertTrue(r['source_hash_matches']);self.assertEqual(digest(ROOT/r['source_file']),r['source_sha256']);self.assertTrue((ROOT/r['historical_stdout_extraction']).is_file())
    def test_10_source_integrity(self):
        self.assertTrue(self.b['integrity']);self.assertTrue(self.b['generator_matches_model']);self.assertEqual(self.c.call('/api/preservation')['status'],'PASS')
    def test_11_path_restrictions(self):
        for path in ['../secret','chapter1/web/server.py']:
            with self.assertRaises(urllib.error.HTTPError):self.c.call('/api/artifact?path='+path)
    def test_12_ctl_checker_branching_and_reachability(self):
        d={'states':['s','good','bad','unreachable'],'initial':['s'],'transitions':[['s','good'],['s','bad'],['good','good'],['bad','bad'],['unreachable','unreachable']],'labeling':{'s':['safe'],'good':['goal','safe'],'bad':['safe'],'unreachable':[]},'suggested_ctl_formulas':['EF(goal)','AF(goal)','AG(safe)','EG(safe)','AX(goal)','EX(goal)']}
        r=check_graph(d);self.assertEqual([p['result'] for p in r['properties']],[True,False,True,True,False,True]);self.assertEqual(r['reachable_states'],3)
        d['transitions']=[['s','good']]
        with self.assertRaises(ValueError):check_graph(d)
    def test_13_json_ctl_actual_26(self):
        r=check_graph(read_json(CHAPTER/'smart_intersection.json'));self.assertEqual(r['overall'],'PASS');self.assertEqual(len(r['properties']),26);self.assertTrue(all(p['result'] for p in r['properties']))

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');suite=unittest.defaultTestLoader.loadTestsFromTestCase(WebTests);result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':[(str(t),e) for t,e in result.failures],'errors':[(str(t),e) for t,e in result.errors],'preservation':verify_preservation(read_json(HERE/'evidence/preservation_baseline.json'))}
    (HERE/'evidence/backend_tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');sys.exit(0 if result.wasSuccessful() else 1)
