const {chromium}=require('playwright');const fs=require('fs');const {rec}=require('./rec.js');const R0='/home/claude/knocky';
(async()=>{const T=process.argv[2],D=process.argv[3];
const b=await chromium.launch({args:['--lang=ru-RU'],env:{...process.env,LANG:'ru_RU.UTF-8',LANGUAGE:'ru'}});
const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,locale:'ru-RU'});
await ctx.addCookies([{name:'kn',value:fs.readFileSync(T+'/tok','utf8'),domain:'127.0.0.1',path:'/'}]);
await ctx.route('https://fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:fs.readFileSync(R0+'/server/app/static/assets/fonts.css','utf8').replaceAll("url('/assets/","url('http://127.0.0.1:8765/assets/")}));
await ctx.route(/fonts\.gstatic|mc\.yandex|knocky\.ru/,r=>r.abort().catch(()=>{}));
const p=await ctx.newPage();p.on('pageerror',e=>console.log('PAGEERR',e.message));
await p.goto('http://127.0.0.1:8765/inv/inv1');await p.waitForTimeout(1800);
const R=rec(p,D);R.scene('s4');await R.shot(12);
const info=await p.$$eval('h2, .tabs button, button',e=>e.filter(x=>x.offsetParent).map(x=>x.tagName+':'+x.textContent.trim().slice(0,30)).slice(0,40));console.log(info.join(' | '));
const H=await p.evaluate(()=>document.documentElement.scrollHeight);console.log('H',H);
// to the link panel
const ly=await p.evaluate(()=>{const h=[...document.querySelectorAll('h2')].find(x=>/Ссылка|Публикац/.test(x.textContent));return h?h.getBoundingClientRect().top+scrollY-90:0});
await R.scroll('scrollTo(0,v)',0,ly,26);await R.hold(30);
R.scene('s6');
const ay=await p.evaluate(()=>{const t=[...document.querySelectorAll('.tabs button, [role=tab]')].find(x=>/Ответы/.test(x.textContent));return t?t.getBoundingClientRect().top+scrollY-120:document.documentElement.scrollHeight});
await R.scroll('scrollTo(0,v)',ly,ay+40,30);await R.hold(50);
R.save();await b.close()})();
