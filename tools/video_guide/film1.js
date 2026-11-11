const {open}=require('./env.js');const {rec}=require('./rec.js');const fs=require('fs');
(async()=>{const {b,p}=await open('https://knocky.ru/');const D=process.argv[2];const R=rec(p,D);
await p.evaluate(()=>{document.querySelectorAll('[class*=cookie],#cookie').forEach(e=>e.remove())});
// 1. design
await p.addStyleTag({content:'.sprog{display:none!important}.grid{scroll-snap-type:none!important;scroll-behavior:auto!important}html{scroll-behavior:auto!important}'});
// load every lazy picture before filming, so nothing pops in while scrolling
await p.evaluate(async()=>{document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');const g=document.getElementById('grid');for(let x=0;x<=g.scrollWidth;x+=300){g.scrollLeft=x;await new Promise(r=>setTimeout(r,60));}g.scrollLeft=0;});
await p.evaluate(()=>{for(let i=1;i<100000;i++)clearInterval(i);});
await p.waitForTimeout(1500);
R.scene('s1');await R.shot(18);
const ty=await p.evaluate(()=>document.getElementById('templates').getBoundingClientRect().top+scrollY-10);
await R.scroll('scrollTo(0,v)',0,ty,36);await R.hold(10);
const gx=await p.evaluate(()=>{const g=document.getElementById('grid');const sc=[g,g.parentElement,g.parentElement.parentElement].find(e=>e.scrollWidth>e.clientWidth+10);window.__gs=sc;const c=g.querySelector('[data-open="glass"]').closest('.card')||g.querySelector('[data-open="glass"]');
 return {from:sc.scrollLeft,to:c.getBoundingClientRect().left-sc.getBoundingClientRect().left+sc.scrollLeft-16}});
await R.scroll('window.__gs.scrollLeft=v',gx.from,gx.to,54);await R.hold(8);
await R.tap('#grid [data-open="glass"]',4);await p.waitForTimeout(800);await R.shot(22);
// 2. colors and blocks
R.scene('s2');const DS='document.querySelector("dialog[open]").scrollTop=v';
const palY=await p.evaluate(()=>{const d=document.querySelector('dialog[open]');const el=[...d.querySelectorAll('button')].find(x=>x.textContent.trim()==='Сумерки');return el.getBoundingClientRect().top+d.scrollTop-260});
await R.scroll(DS,0,palY,24);await R.hold(6);
const champ=await p.evaluateHandle(()=>[...document.querySelectorAll('dialog[open] button')].find(x=>x.textContent.trim()==='Сумерки'));
await R.tap(champ,6);
await R.scroll(DS,palY,0,20);await R.hold(16);
const blkY=await p.evaluate(()=>{const d=document.querySelector('dialog[open]');const el=d.querySelector('#blk-rsvp');return el.getBoundingClientRect().top+d.scrollTop-420});
await R.scroll(DS,0,blkY,24);
const TS='document.querySelector("dialog[open] .tiers").scrollTop=v';
const tY=await p.evaluate(()=>{const t=document.querySelector('dialog[open] .tiers');const g=document.querySelector('#blk-gallery');return Math.max(0,g.getBoundingClientRect().top-t.getBoundingClientRect().top+t.scrollTop-t.clientHeight/2)});
await R.scroll(TS,0,tY,20);await R.hold(8);
const gal=await p.evaluateHandle(()=>document.querySelector('#blk-gallery').closest('label')||document.querySelector('#blk-gallery'));
if(!(await p.$eval('#blk-gallery',e=>e.checked)))await R.tap(gal,14);
await R.tap('#payBtn',4);await p.waitForTimeout(500);
// 3. data
R.scene('s3');
const fy=await p.evaluate(()=>{const d=document.querySelector('dialog[open]');return document.getElementById('fA').getBoundingClientRect().top+d.scrollTop-330});
await R.scroll(DS,await p.evaluate(()=>document.querySelector('dialog[open]').scrollTop),fy,18);await R.hold(4);
await R.type('#fA','Мария');await R.type('#fB','Денис');await R.hold(4);
await p.fill('#fVenue','');await R.type('#fVenue','Шато «Белый сад»',1);await R.hold(10);
await R.scroll(DS,fy,0,22);await R.hold(26);
// save payload for the cabinet scenes
fs.writeFileSync(D+'/payload.json',JSON.stringify(await p.evaluate(()=>orderPayload())));
// 5. guest view (filmed here, used after the cabinet)
R.scene('s5');
await p.evaluate(()=>{const d=document.querySelector('dialog[open]');if(d)d.close();location.hash='#invite-glass'});await p.waitForTimeout(1400);await R.shot(20);
const H=await p.evaluate(()=>document.documentElement.scrollHeight-innerHeight);
const rsvp=await p.evaluate(()=>{const b=[...document.querySelectorAll('#inviteView button')].find(x=>x.textContent.trim()==='Приду');return b?b.getBoundingClientRect().top+scrollY-500:0});
await R.scroll('scrollTo(0,v)',0,Math.min(rsvp*0.5,H),40);await R.hold(8);
await R.scroll('scrollTo(0,v)',Math.min(rsvp*0.5,H),rsvp,40);await R.hold(6);
const nm=await p.evaluateHandle(()=>[...document.querySelectorAll('#inviteView input')].find(x=>/Имя/.test(x.placeholder)));
if(nm){await nm.click();await p.waitForTimeout(150);for(const ch of 'Ольга Смирнова'){await nm.type(ch);await R.shot(1);}}
const pr=await p.evaluateHandle(()=>[...document.querySelectorAll('#inviteView button')].find(x=>x.textContent.trim()==='Приду'));await R.tap(pr,10);
const sb=await p.evaluateHandle(()=>[...document.querySelectorAll('#inviteView button')].find(x=>x.textContent.trim()==='Отправить ответ'));await R.tap(sb,24);
R.save();console.log('frames',fs.readdirSync(D).length);await b.close()})();
