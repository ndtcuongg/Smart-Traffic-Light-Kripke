"""Rebuild and verify Chapter 1 only, using the existing local tools."""
from pathlib import Path
import sys,subprocess,shutil,hashlib,json
ROOT=Path(__file__).resolve().parent.parent

def call(args):
    print('\n> '+' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=ROOT,check=True)

def main():
    if not shutil.which('NuSMV'):raise RuntimeError('NuSMV must be on PATH')
    exe=Path(r'C:\Users\Admin\Downloads\SecLabFramework.exe')
    if not exe.is_file():raise RuntimeError('Missing target application: '+str(exe))
    record=ROOT/'chapter1/evidence/runtime_provenance.json'
    runtime=ROOT/'.chapter1-tools/seclab/python314.dll'
    expected=json.loads(record.read_text(encoding='utf-8')).get('exe_sha256') if record.exists() else None
    actual=hashlib.sha256(exe.read_bytes()).hexdigest()
    if not runtime.exists() or actual!=expected:call([sys.executable,'chapter1/bootstrap_seclab.py','--exe',exe])
    for script in ['build.py','verify_graph.py','verify_nusmv.py','count_nusmv.py']:
        call([sys.executable,'chapter1/'+script])
    call(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File','chapter1/run_seclab.ps1','-ScriptPath','chapter1/verify_target.py'])
    call([sys.executable,'chapter1/make_diagrams.py'])
    call(['node','chapter1/check_diagrams.mjs'])
    call([sys.executable,'chapter1/make_docs.py'])
    print('\nPASS: Chapter 1 verification completed. Report: chapter1/README.md',flush=True)
if __name__=='__main__':main()
