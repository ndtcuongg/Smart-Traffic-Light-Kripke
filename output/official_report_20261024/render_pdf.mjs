import {spawn} from 'node:child_process';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {writeFile,stat} from 'node:fs/promises';
const dir=path.resolve('output/official_report_20261024');
const app='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const result=[];
for(const name of ['BAO_CAO_CHINH_THUC','BIEN_BAN_KIEM_CHUNG']){
 const output=path.join(dir,name+'.pdf');
 const proc=spawn(app,['--headless=new','--disable-gpu','--disable-extensions','--no-first-run','--no-default-browser-check','--allow-file-access-from-files',`--user-data-dir=${path.join(dir,'render_profile')}`,'--no-pdf-header-footer',`--print-to-pdf=${output}`,pathToFileURL(path.join(dir,name+'.html')).href],{windowsHide:true,stdio:['ignore','pipe','pipe']});
 let log='';proc.stdout.on('data',d=>log+=d);proc.stderr.on('data',d=>log+=d);
 const timeout=setTimeout(()=>proc.kill(),60000);const code=await new Promise(r=>proc.on('exit',r));clearTimeout(timeout);
 await writeFile(path.join(dir,name+'_render.log'),log);result.push({name,returncode:code,bytes:(await stat(output)).size,renderer:'Microsoft Edge headless; same structured content as DOCX'});
}
await writeFile(path.join(dir,'pdf_render.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
