"""Re-extract the trusted local application's runtime for headless Chapter 1 checks."""
from pathlib import Path
import struct,zlib,marshal,json,hashlib,argparse

def extract(executable):
    root=Path(__file__).resolve().parent.parent;out=root/'.chapter1-tools'/'seclab';out.mkdir(parents=True,exist_ok=True)
    b=Path(executable).read_bytes();pos=b.rfind(b'MEI\014\013\012\013\016')
    if pos<0:raise ValueError('Not a PyInstaller application')
    cookie=struct.unpack('!8sIIII64s',b[pos:pos+88]);base=pos+88-cookie[1]
    if cookie[4]!=314:raise ValueError('Expected the inspected Python 3.14 application')
    toc=b[base+cookie[2]:base+cookie[2]+cookie[3]];i=0;pyz=None
    for_write=[]
    while i<len(toc):
        e=struct.unpack('!IIIIBB',toc[i:i+18]);name=toc[i+18:i+e[0]].split(b'\0')[0].decode();i+=e[0]
        selected=(name=='PYZ.pyz' or name in ['python314.dll','python3.dll','base_library.zip'] or ('\\' not in name and name.lower().endswith(('.pyd','.dll'))) or name.startswith('z3\\') or name in ['dataset\\ch1_verification\\traffic_light.json','dataset\\ch6_specs\\FORMAT.md','dataset\\ch6_specs\\elevator_control_spec.json'])
        if not selected:continue
        raw=b[base+e[1]:base+e[1]+e[2]];raw=zlib.decompress(raw) if e[4] else raw
        dest=(out/Path(name)).resolve()
        if not dest.is_relative_to(out.resolve()):raise ValueError('Archive path escapes runtime directory')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        if name=='PYZ.pyz':pyz=raw
    if pyz is None:raise ValueError('Missing bundled modules')
    modules=dict(marshal.loads(pyz[struct.unpack('!i',pyz[8:12])[0]:]));count=0
    for name,(kind,offset,size) in modules.items():
        if kind not in (0,1):continue
        dest=out/Path(*name.split('.'));dest=dest/'__init__.pyc' if kind==1 else dest.with_suffix('.pyc')
        if not dest.resolve().is_relative_to(out.resolve()):raise ValueError('Invalid module path')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(pyz[4:8]+b'\0'*12+zlib.decompress(pyz[offset:offset+size]));count+=1
    report={'executable':str(executable),'exe_sha256':hashlib.sha256(b).hexdigest(),'runtime':str(out),'python':cookie[4],'pure_python_modules_extracted':count,'application_executed':False}
    (root/'chapter1/evidence/runtime_provenance.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--exe',type=Path,default=Path(r'C:\Users\Admin\Downloads\SecLabFramework.exe'));args=p.parse_args();extract(args.exe)
