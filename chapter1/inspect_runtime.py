import dis, types, marshal, pathlib, sys
root=pathlib.Path.cwd(); runtime=root/'.chapter1-tools'/'seclab'
sys.stdout.reconfigure(encoding='utf-8')
out=root/'chapter1'/'evidence'/'seclab_parser_disassembly.txt'
with out.open('w',encoding='utf-8') as f:
    for name in ['core.kripke','core.spec_pipeline']:
        p=runtime/pathlib.Path(*name.split('.')).with_suffix('.pyc')
        code=marshal.loads(p.read_bytes()[16:])
        print('MODULE',name,file=f)
        dis.dis(code,file=f)
print(out)
