import {spawn} from 'node:child_process';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {writeFile,stat} from 'node:fs/promises';
const delivery=path.resolve('chapter1/web/report_delivery'),output=path.join(delivery,'quality_checks','browser_export.pdf'),source=path.join(delivery,'quality_checks','print_record.html');
const app='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const proc=spawn(app,['--headless=new','--disable-gpu','--disable-extensions','--no-first-run','--no-default-browser-check','--allow-file-access-from-files',`--user-data-dir=${path.join(delivery,'quality_checks','edge_render_profile')}`,'--no-pdf-header-footer',`--print-to-pdf=${output}`,pathToFileURL(source).href],{windowsHide:true,stdio:['ignore','pipe','pipe']});
let log='';proc.stdout.on('data',d=>log+=d);proc.stderr.on('data',d=>log+=d);let timeout=setTimeout(()=>proc.kill(),90000);const code=await new Promise(r=>proc.on('exit',r));clearTimeout(timeout);await writeFile(path.join(delivery,'quality_checks','browser_export.log'),log);const result={application:'Microsoft Edge headless',source:'Print HTML generated directly from DOCX paragraphs/tables/embedded original images',returncode:code,output,bytes:(await stat(output)).size};await writeFile(path.join(delivery,'quality_checks','browser_export.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
