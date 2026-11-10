const {chromium}=require('playwright');(async()=>{const out=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900},deviceScaleFactor:2});
await p.route('https://app.knocky.ru/assets/**',r=>{const f='/home/claude/knocky/server/app/static'+new URL(r.request().url()).pathname;try{r.fulfill({path:f})}catch(e){r.abort()}});
await p.route('https://fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:require('fs').readFileSync('/home/claude/knocky/server/app/static/assets/fonts.css','utf8').replaceAll("url('/assets/","url('https://app.knocky.ru/assets/")}));
await p.route('https://fonts.gstatic.com/**',r=>r.abort());
await p.goto('file:///home/claude/knocky/index.html');await p.waitForTimeout(1500);await p.evaluate(()=>document.fonts.ready);
await p.addStyleTag({content:'#grid{grid-auto-columns:450px !important}'});await p.waitForTimeout(800);
await p.evaluate(()=>{document.querySelectorAll('.cookie,#cookie,[class*=cookie]').forEach(e=>e.remove())});
const ids=await p.evaluate(()=>TPL.map(t=>t.id));
const meta=[];
for(const id of ids){const el=await p.$(`#grid [data-open="${id}"] .inv`);await el.scrollIntoViewIfNeeded();await p.waitForTimeout(1800);
const bb=await el.boundingBox();meta.push([id,Math.round(bb.width),Math.round(bb.height)]);
await el.screenshot({path:`${out}/${id}.png`,animations:'disabled'});}
console.log(JSON.stringify(meta.slice(0,3)),meta.length);await b.close()})();
