const {chromium}=require('playwright');const fs=require('fs');const R0='/home/claude/knocky';
(async()=>{const T=process.argv[2],out=process.argv[3];
const b=await chromium.launch({args:['--lang=ru-RU'],env:{...process.env,LANG:'ru_RU.UTF-8',LANGUAGE:'ru'}});
const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:+(process.env.DSF||2),isMobile:true,hasTouch:true,locale:'ru-RU'});
await ctx.addCookies([{name:'kn',value:fs.readFileSync(T+'/tok','utf8'),domain:'127.0.0.1',path:'/'}]);
await ctx.route('https://fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:fs.readFileSync(R0+'/server/app/static/assets/fonts.css','utf8').replaceAll("url('/assets/","url('http://127.0.0.1:8765/assets/")}));
await ctx.route(/fonts\.gstatic|mc\.yandex|knocky\.ru/,r=>r.abort().catch(()=>{}));
const p=await ctx.newPage();await p.goto('http://127.0.0.1:8765/inv/inv1');await p.waitForTimeout(1800);
// hide the preview phone below the answers
await p.addStyleTag({content:'aside.phone{display:none!important}'});
const ay=await p.evaluate(()=>{const t=[...document.querySelectorAll('.tabs button, [role=tab], button')].find(x=>/^Ответы/.test(x.textContent.trim()));return t.getBoundingClientRect().top+scrollY-210});
await p.evaluate(y=>scrollTo(0,y),ay);await p.waitForTimeout(300);await p.screenshot({path:out,type:out.endsWith('.png')?'png':'jpeg',...(out.endsWith('.png')?{}:{quality:92})});await b.close()})();
