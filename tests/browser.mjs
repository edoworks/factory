// Dependency-free Chrome DevTools smoke test; only a new temporary browser profile.
import {spawn} from 'node:child_process';
import {createServer} from 'node:http';
import {readFile, writeFile, mkdtemp, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const root=path.resolve(process.argv[2]), chrome=process.env.FACTORY_CHROME;
if(!chrome) throw new Error('FACTORY_CHROME must name the installed browser executable');
const {spec}=await import(pathToFileURL(path.join(root,'spec.mjs')));
const lock=JSON.parse(await readFile(new URL('../toolchain.json',import.meta.url),'utf8'));
assert.equal(process.versions.node,lock.node);
const profile=await mkdtemp(path.join(tmpdir(),'factory-browser-'));
const allowed=new Set(['index.html','style.css','app.mjs','engine.mjs','spec.mjs']);
const server=createServer(async(req,res)=>{
  const pathname=new URL(req.url,'http://localhost').pathname;
  const name=pathname==='/'?'index.html':pathname.slice(1);
  if(!allowed.has(name)){res.writeHead(404);res.end();return;}
  try{const data=await readFile(path.join(root,name));res.setHeader('Content-Type',name.endsWith('mjs')?'text/javascript':name.endsWith('css')?'text/css':'text/html');res.end(data);}catch{res.writeHead(500);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const processHandle=spawn(chrome,['--headless=new','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-default-apps','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:['ignore','ignore','pipe']});
let stderr='';processHandle.stderr.on('data',d=>stderr+=d.toString());
let socket; const checks=[];
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn, attempts=100){for(let i=0;i<attempts;i++){const v=await fn();if(v)return v;await pause(50);}throw new Error('Browser wait timed out: '+stderr.slice(-1000));}
try {
  const port=await until(async()=>{try{return (await readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];}catch{return null;}},400);
  const version=await (await fetch('http://127.0.0.1:'+port+'/json/version')).json();
  assert.ok(version.Browser.endsWith('/'+lock.browser),'Browser differs from toolchain lock: '+version.Browser);
  const page=await (await fetch('http://127.0.0.1:'+port+'/json/new?about:blank',{method:'PUT'})).json();
  socket=new WebSocket(page.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  let sequence=0;const pending=new Map(),errors=[];
  socket.onmessage=event=>{const response=JSON.parse(event.data);if(response.id){const p=pending.get(response.id);pending.delete(response.id);if(response.error)p?.reject(new Error(JSON.stringify(response.error)));else p?.resolve(response.result);}else if(response.method==='Runtime.exceptionThrown')errors.push(response.params);};
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.delete(id))reject(new Error('CDP timeout '+method));},5000).unref();});
  const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  const exists=selector=>until(()=>evaluate(`!!document.querySelector(${JSON.stringify(selector)})`));
  const click=selector=>evaluate(`document.querySelector(${JSON.stringify(selector)}).click()`);
  const text=()=>evaluate('document.body.innerText');
  const fill=async(selector,values)=>evaluate(`(()=>{const form=document.querySelector(${JSON.stringify(selector)});for(const [key,value] of Object.entries(${JSON.stringify(values)}))form.elements.namedItem(key).value=value;form.requestSubmit();})()`);
  await call('Page.enable');await call('Runtime.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await call('Page.navigate',{url:origin});await exists('#setup');
  assert.equal(await evaluate('document.title'),spec.title);
  await evaluate("document.querySelector('#players').value='Alex\\nAlex';document.querySelector('#setup').requestSubmit()");
  assert.match(await text(),/distinct player names/);checks.push('invalid setup rejected');
  await evaluate("document.querySelector('#players').value='Alex\\nSam';document.querySelector('#setup').requestSubmit();localStorage.setItem('unrelated-test-key','keep')");
  for(const stage of spec.stages){
    if(stage.kind==='lock'){
      for(let player=0;player<2;player++){
        assert.equal(await evaluate("document.querySelector('#picks')===null"),true);
        await click('#player-'+player);await exists('#picks');
        const values=Object.fromEntries(stage.questions.map(id=>[id,spec.questions.find(q=>q.id===id).options[0].id]));
        if(stage.boost) values.boost=stage.questions[0];
        await fill('#picks',values);
        assert.equal(await evaluate("document.querySelector('#picks')===null"),true);
        if(player===0){
          const saved=await evaluate('localStorage.getItem('+JSON.stringify('factory.game.'+spec.id)+')');
          await call('Page.navigate',{url:origin+'/?reload='+stage.id});await exists('#player-1');
          assert.equal(await evaluate('localStorage.getItem('+JSON.stringify('factory.game.'+spec.id)+')'),saved);
          assert.equal(await evaluate("document.querySelector('#player-0')===null"),true);
        }
      }
      checks.push(stage.id+': private handoff, locks and reload');
    }else{
      await exists('#results');const before=await evaluate('localStorage.getItem('+JSON.stringify('factory.game.'+spec.id)+')');
      const values=Object.fromEntries(stage.questions.map(id=>[id,spec.questions.find(q=>q.id===id).options[0].id]));
      await fill('#results',values);await exists('#confirm');
      assert.equal(await evaluate('localStorage.getItem('+JSON.stringify('factory.game.'+spec.id)+')'),before);
      await click('#edit-results');await exists('#results');await fill('#results',values);await click('#confirm');
      checks.push(stage.id+': preview has no mutation, explicit confirmation');
    }
  }
  assert.match(await text(),/Final podium/);assert.equal(await evaluate("document.querySelectorAll('#recap article').length"),2);
  const expected=spec.questions.reduce((n,q)=>n+q.points,0)+spec.stages.filter(s=>s.boost).reduce((n,s)=>n+spec.questions.find(q=>q.id===s.questions[0]).points,0);
  assert.deepEqual(await evaluate("[...document.querySelectorAll('.score')].map(n=>n.textContent)"),[expected+' prediction points',expected+' prediction points']);
  assert.ok((await text()).includes(spec.questions[0].text));checks.push('final shared-rank recap and spec-driven score '+expected);
  const screenshot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
  await writeFile(path.join(path.dirname(root),'browser-'+path.basename(root)+'.png'),Buffer.from(screenshot.data,'base64'));
  await call('Emulation.setDeviceMetricsOverride',{width:320,height:844,deviceScaleFactor:1,mobile:true});
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'),true);checks.push('320px no horizontal overflow');
  await click('#reset');await click('#confirm-reset');await exists('#setup');
  assert.equal(await evaluate("localStorage.getItem('unrelated-test-key')"),'keep');checks.push('reset preserves unrelated key');
  await evaluate('localStorage.setItem('+JSON.stringify('factory.game.'+spec.id)+',"{broken")');
  await call('Page.navigate',{url:origin+'/?corrupt'});await until(async()=>/Cannot safely restore/.test(await text()));
  assert.equal(await evaluate('localStorage.getItem('+JSON.stringify('factory.game.'+spec.id)+')'),'{broken');
  assert.equal(await evaluate("document.querySelector('#setup')===null"),true);checks.push('corrupt save visibly blocked and retained');
  await click('#reset');await click('#confirm-reset');await exists('#setup');
  await evaluate("Storage.prototype.setItem=function(){throw new Error('simulated quota')};document.querySelector('#setup').requestSubmit()");
  assert.match(await text(),/in memory only/);checks.push('write failure warns without a saved claim');
  assert.deepEqual(errors,[]);console.log(JSON.stringify({status:'passed',browser:version.Browser,checks},null,2));
} finally {
  socket?.close();processHandle.kill('SIGTERM');
  await Promise.race([new Promise(r=>processHandle.once('exit',r)),pause(3000)]);
  if(processHandle.exitCode===null)processHandle.kill('SIGKILL');
  server.close();await rm(profile,{recursive:true,force:true,maxRetries:3,retryDelay:100});
}
