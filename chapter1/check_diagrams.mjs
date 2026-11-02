import {spawn} from 'node:child_process';
import {readFile,writeFile,mkdir,rm} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd(),profile=path.join(root,'.chapter1-tools','diagram-browser');
await mkdir(profile,{recursive:true});
await rm(path.join(profile,'DevToolsActivePort'),{force:true});
const edge=spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',[
'--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
'--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',`--user-data-dir=${profile}`,
'--window-size=1400,1600',pathToFileURL(path.join(root,'chapter1','kripke_explorer.html')).href],{windowsHide:true,stdio:'ignore'});
const expected=JSON.parse(await readFile(path.join(root,'chapter1','smart_intersection.json'),'utf8')).states.length;
let ws;
try{
 let port;
 for(let i=0;i<100;i++){try{port=Number((await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0]);if(port)break}catch{}await new Promise(r=>setTimeout(r,100))}
 if(!port)throw new Error('No DevTools port');
 const tabs=await(await fetch(`http://127.0.0.1:${port}/json`)).json(),tab=tabs.find(t=>t.type==='page');
 ws=new WebSocket(tab.webSocketDebuggerUrl);await new Promise((ok,no)=>{ws.onopen=ok;ws.onerror=no});
 let sequence=0;const pending=new Map();const errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);if(m.error)p.reject(new Error(JSON.stringify(m.error)));else p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
 await send('Runtime.enable');
 const evaluate=async code=>{const r=await send('Runtime.evaluate',{expression:code,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value};
 for(let i=0;i<100;i++){if(await evaluate(`document.querySelectorAll('#state option').length===${expected}`))break;await new Promise(r=>setTimeout(r,100))}
 const checks=[];
 checks.push(['all_states_loaded',await evaluate(`document.querySelectorAll('#state option').length===${expected}`)]);
 checks.push(['initial_all_red',await evaluate("document.querySelectorAll('#lamps .bulb.red.on').length===4 && document.querySelectorAll('#lamps .bulb.on').length===4")]);
 await evaluate("select(d.states.find(n=>n.startsWith('NS_GREEN__r001__now_NIGHT_LOW')))");
 checks.push(['individual_green_lamps',await evaluate("document.querySelectorAll('#lamps .bulb.green.on').length===2 && document.querySelectorAll('#lamps .bulb.red.on').length===2")]);
 checks.push(['rendered_real_edges',await evaluate("document.querySelectorAll('#next button').length===out.get(current).length")]);
 await evaluate("document.querySelector('#next button').click()");
 checks.push(['one_second_step',await evaluate("current.startsWith('NS_YELLOW__r003')")]);
 await evaluate("el('search').value='NS_GREEN__r001';el('filter').click()");
 checks.push(['filter',await evaluate("document.querySelectorAll('#state option').length>0 && [...el('state').options].every(o=>o.value.includes('NS_GREEN__r001'))")]);
 await evaluate("el('reset').click()");checks.push(['reset',await evaluate("current===d.initial[0]")]);
 await evaluate("select(d.states.find(n=>n.startsWith('NS_GREEN__') && n.includes('__now_MORNING_PEAK')))");
 const screenshot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 await writeFile(path.join(root,'chapter1','evidence','explorer_preview.png'),Buffer.from(screenshot.data,'base64'));
 checks.push(['no_browser_exceptions',errors.length===0]);
 const result={browser:'Microsoft Edge headless',checks:Object.fromEntries(checks),status:checks.every(x=>x[1])?'PASS':'FAIL'};
 await writeFile(path.join(root,'chapter1','evidence','diagram_results.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result,null,2));if(result.status!=='PASS')process.exitCode=1;
 await send('Browser.close');
}finally{if(ws)ws.close();edge.kill()}
