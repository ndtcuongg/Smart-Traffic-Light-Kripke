from pathlib import Path
import sys,json,inspect,traceback
sys.stdout.reconfigure(encoding='utf-8')
from core.kripke import KripkeStructure,CTLChecker,find_deadlock_states,check_mutual_exclusion
report={'module':'core.kripke','runtime':sys.version,'signatures':{k:str(inspect.signature(v)) for k,v in [('from_dict',KripkeStructure.from_dict),('check',CTLChecker.check),('check_mutual_exclusion',check_mutual_exclusion)]}}
try:
    from core.spec_pipeline import parse_specification_dict
    report['spec_parser_available']=True
except Exception as e: report['spec_parser_available']=False; report['spec_parser_error']=repr(e)
print(json.dumps(report,ensure_ascii=False,indent=2))
Path('chapter1/evidence/target_runtime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
