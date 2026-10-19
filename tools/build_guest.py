"""Build the guest page (invitation as guests see it) from the prototype and seal it.

usage: python3 tools/build_guest.py <prototype konvert.html> <setup token file> [--plain out.html]

The page reuses the prototype's renderer (designs, cover, blocks, real map), loads the
invitation from the server API and wires the RSVP form and the wishlist to it.
It contains all design code, so it is stored encrypted (AES-GCM) in server/app/sealed/guest.enc;
the server opens it with a key derived from the one-time setup token.
"""
import hashlib, os, sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]).read_text(encoding="utf-8")
token = Path(sys.argv[2]).read_text().strip()


def cut(a, b):
    i, j = src.index(a), src.index(b)
    return src[i:j]


# styles: Leaflet + site/design CSS (two <style> blocks in <head>)
head = src[: src.index("<script>")]
styles = []
pos = 0
while True:
    i = head.find("<style>", pos)
    if i < 0:
        break
    j = head.index("</style>", i)
    styles.append(head[i + 7 : j])
    pos = j
css = "\n".join(styles)
renderer = cut("/* constructor: base + paid blocks */", "/* hero rotation */")
mapjs = cut("/* real map: Yandex Tiles API + Leaflet", "/* point picker in the order form */")

GUEST_CSS = r"""
body{background:#1E1A1C;margin:0}
#inviteView .page{min-height:100svh}
.gmsg{min-height:100svh;display:grid;place-items:center;text-align:center;color:#F3EEEE;font:500 16px/1.5 var(--f-body);padding:24px}
.gmsg b{display:block;font-family:var(--f-disp);font-size:22px;color:#fff;margin-bottom:8px}
.gmsg a{color:#fff}
.rsvp .more{display:grid;gap:3cqi}
.rsvp .more[hidden]{display:none}
.rsvp select,.rsvp textarea{font:inherit;font-size:4cqi;padding:3cqi;border-radius:2cqi;background:transparent;color:var(--t-ink);border:1px solid color-mix(in srgb,var(--t-ink) 30%,transparent);width:100%;box-sizing:border-box}
.rsvp select option{color:#241B20;background:#fff}
.rsvp textarea{min-height:18cqi;resize:vertical}
.rsvp .rdays{display:grid;gap:2cqi;text-align:left}
.rsvp .rdays label{display:flex!important;flex-direction:row!important;justify-content:flex-start!important;text-align:left!important;align-items:center;gap:3cqi;font-size:3.8cqi;cursor:pointer;padding:2.4cqi 3cqi;border-radius:2cqi;background:color-mix(in srgb,var(--t-ink) 6%,transparent)}
.rsvp .rdays input{width:4.6cqi;height:4.6cqi;accent-color:var(--t-acc);flex:none;margin:0}
.rsvp .rdays span{display:grid;text-align:left;justify-items:start}.rsvp .rdays small{font-size:3.1cqi;opacity:.7}
.rsvp .lbl{font-size:3.4cqi;opacity:.75;text-align:left;margin-bottom:-1.5cqi}
.rsvp .err{font-size:3.4cqi;color:var(--t-acc)}
.rsvp .ok{font-size:4cqi;line-height:1.5}
.rsvp .again{background:none;border:0;color:inherit;text-decoration:underline;font:inherit;font-size:3.4cqi;cursor:pointer;opacity:.8;margin-top:2cqi}
.wish .wbtn{font:inherit;font-size:3.2cqi;font-weight:700;padding:1.6cqi 3.4cqi;border-radius:999px;border:1px solid var(--t-acc);background:transparent;color:var(--t-acc);cursor:pointer;white-space:nowrap}
.wish .wtaken{opacity:.6;font-size:3.2cqi;white-space:nowrap}
.wish .wform{display:flex;gap:2cqi;margin-top:2cqi;grid-column:1/-1;width:100%}
.wish .wform input{flex:1;min-width:0;font:inherit;font-size:3.6cqi;padding:2cqi 3cqi;border-radius:2cqi;background:transparent;color:var(--t-ink);border:1px solid color-mix(in srgb,var(--t-ink) 30%,transparent)}
.wish .wform button{font:inherit;font-size:3.4cqi;font-weight:700;padding:2cqi 3.4cqi;border-radius:999px;border:0;background:var(--t-acc);color:var(--t-bg);cursor:pointer}
.wish>div{flex-wrap:wrap}
.inv .seat .cd div{min-width:0}
/* printable version: A5 sheets, front = cover, back = date, place, program, dress code, QR */
body.print{background:#E9E4E5}
.pbar{position:sticky;top:0;z-index:50;background:#fff;color:#241B20;font:500 14px/1.5 'Manrope',system-ui,sans-serif;padding:14px 16px;box-shadow:0 2px 14px rgba(36,27,32,.08)}
.pbar .in{max-width:760px;margin:0 auto;display:grid;gap:10px}
.pbar h1{font-size:18px;margin:0;font-weight:800}
.pbar .warn{background:#F3EEEE;border-radius:12px;padding:10px 12px}
.pbar .row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.pbar select{flex:0 1 auto;font:inherit;padding:10px 12px;border-radius:12px;border:0;background:#F3EEEE;color:#241B20;max-width:100%}
.pbar button{font:inherit;font-weight:700;padding:11px 20px;border-radius:999px;border:0;background:#C62828;color:#fff;cursor:pointer}
.pbar .n{color:#6F6068;font-size:13px}
.sheets{display:grid;gap:24px;justify-content:center;padding:24px 12px 48px}
.sheet{width:148mm;height:210mm;container-type:inline-size;overflow:hidden;position:relative;background:#fff;box-shadow:0 6px 30px rgba(36,27,32,.18)}
.sheet .inv{height:100%;min-height:0;transform:none}
.sheet .cover{min-height:0!important;height:210mm;box-sizing:border-box;aspect-ratio:auto!important}
.sheet.back .inv{display:flex;flex-direction:column;justify-content:center;align-items:center}
.sheet.back .fit{container-type:inline-size;width:100%;flex:none}
.sheet.back section{padding:3.4cqi 9cqi}
.sheet.back h4{font-size:6.4cqi;margin-bottom:2.2cqi}
.sheet.back p{margin:0}
.sheet.back .prog{gap:1.6cqi}
.sheet.back .sign{padding:3cqi 0 6cqi}
.sheet .qr{display:flex;gap:5cqi;align-items:center;justify-content:center;text-align:left}
.sheet .qr svg{width:27cqi;height:27cqi;flex:none;background:#fff;padding:1.6cqi;border-radius:2cqi}
.sheet .qr div{font-size:3.3cqi;line-height:1.45;max-width:46cqi}
.sheet .qr b{display:block;font-size:3.8cqi;margin-bottom:1cqi}
.sheet.back .seat .cd{margin:0}
.sheet .t-sketch .sk-art{width:46cqi;transform:translate(-50%,-50%)}
.sheet *,.sheet *::before,.sheet *::after{animation:none!important;transition:none!important}
body.render{margin:0;background:#000;overflow:hidden}
.rn{display:flex;align-items:center;justify-content:center;background:var(--t-bg);overflow:hidden}
.rn *,.rn *::before,.rn *::after{animation:none!important;transition:none!important}
.rn-og{width:1200px;height:630px}.rn-og .rn-c{width:430px;height:881px;zoom:.7151;container-type:inline-size;box-shadow:0 0 90px rgba(0,0,0,.2)}
.rn-story{width:1080px;height:1920px}.rn-story .rn-c{width:1080px;height:1920px;container-type:inline-size}
.rn .inv{height:100%;min-height:0;transform:none}.rn .cover{min-height:0!important;height:100%;box-sizing:border-box;aspect-ratio:auto!important;width:auto}
.rn .t-sketch .sk-art{width:52cqi;transform:translate(-50%,-50%)}
@page{size:A5;margin:0}
@media print{.sheets{zoom:1!important}body.print{background:none}.pbar{display:none}.sheets{display:block;padding:0}.sheet{box-shadow:none;break-after:page;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pvbar{position:sticky;top:0;z-index:50;background:#C62828;color:#fff;text-align:center;font:600 13px/1.4 var(--f-body);padding:8px 12px}
"""

GUEST_JS = r"""
/* ===== guest page: data from the server ===== */
const V=document.getElementById('inviteView');
const parts_=location.pathname.split('/').filter(Boolean);
const PREVIEW=parts_[0]==='p',PRINT=parts_[0]==='print';
/* app.knocky.ru/i/<address>, /p/<id>, /print/<id>, or knocky.ru/<address> served by our server */
const KEY=decodeURIComponent((['i','p','print'].includes(parts_[0])?parts_[1]:parts_[0])||'');
const G=new URLSearchParams(location.search).get('g')||'';
let P=null;
function msg(t,s){V.innerHTML=`<div class="gmsg"><div><b>${t}</b>${s||''}</div></div>`;}
function draw(){
  const t=TPL.find(x=>x.id===P.tpl)||TPL[0];
  const on=new Set(P.sel||[]);
  const ord=[...(P.order||[]).filter(id=>DEF_ORDER.includes(id)),...DEF_ORDER.filter(id=>!(P.order||[]).includes(id))];
  V.innerHTML=(PREVIEW?'<div class="pvbar">Предпросмотр: так приглашение увидят гости</div>':'')+
    `<div class="page">${full(t,P.v,on,ord)}</div><p class="made">Приглашение сделано на Knocky. <a href="https://knocky.ru" target="_blank" rel="noopener">Создать своё</a></p>`;
  wireRsvp();wireWish();}
function wireRsvp(){const box=V.querySelector('[data-rsvp]');if(!box)return;
  const inp=box.querySelector('input');if(P.guest&&!inp.value)inp.value=P.guest;
  const more=document.createElement('div');more.className='more';more.hidden=true;
  const D=daysOf(P.v);
  more.innerHTML=(D.length>1?`<div class="lbl">В какие дни придете</div><div class="rdays">${D.map((d,i)=>`<label><input type="checkbox" data-rday="${i}" checked><span>${esc(dayTitle(P.v,i))}${d.date?`<small>${esc(dayMonth(d.date))}</small>`:''}</span></label>`).join('')}</div>`:'')+
    `<div class="lbl">Сколько вас будет</div><select data-people aria-label="Сколько вас будет">${[1,2,3,4,5,6,7,8].map(n=>`<option value="${n}">${n}</option>`).join('')}</select>`;
  const cm=document.createElement('textarea');cm.setAttribute('aria-label','Комментарий');cm.placeholder='Комментарий: пожелания по меню, вопросы (по желанию)';cm.maxLength=500;
  const er=document.createElement('div');er.className='err';er.setAttribute('role','alert');
  const send=box.querySelector('[data-send]');
  box.insertBefore(more,send);box.insertBefore(cm,send);box.insertBefore(er,send);}
document.addEventListener('click',async e=>{
  const o=e.target.closest('[data-rsvp] [data-o]');
  if(o){o.parentNode.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',b===o));const m=o.closest('[data-rsvp]').querySelector('.more');if(m)m.hidden=o.dataset.o!=='1';return;}
  const s=e.target.closest('[data-rsvp] [data-send]');
  if(s){const box=s.closest('[data-rsvp]'),er=box.querySelector('.err'),n=box.querySelector('input').value.trim(),ch=box.querySelector('[aria-pressed="true"]');
    er.textContent='';
    if(!ch){er.textContent='Выберите «Приду» или «Не смогу»';return;}
    if(!n){er.textContent='Укажите имя и фамилию';box.querySelector('input').focus();return;}
    if(PREVIEW){er.textContent='Это предпросмотр: ответы принимаются после публикации';return;}
    const yes=ch.dataset.o==='1';const dayBoxes=[...box.querySelectorAll('[data-rday]')];const days=dayBoxes.filter(x=>x.checked).map(x=>+x.dataset.rday);
    if(yes&&dayBoxes.length&&!days.length){er.textContent='Отметьте, в какие дни вы придете';return;}
    s.disabled=true;s.textContent='Отправляем…';
    try{const r=await fetch('/api/public/'+encodeURIComponent(KEY)+'/rsvp',{method:'POST',headers:{'content-type':'application/json'},
        body:JSON.stringify({name:n,attend:yes,people:+(box.querySelector('[data-people]')||{}).value||1,comment:(box.querySelector('textarea')||{}).value||'',g:G,days:dayBoxes.length?days:undefined})});
      const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.error||'Не получилось отправить');
      box.innerHTML=`<div class="ok">Спасибо, ${esc(n)}! ${yes?'Ждём вас на празднике.':'Жаль, что не получится. Спасибо, что ответили.'}</div><button type="button" class="again" data-again>Изменить ответ</button>`;}
    catch(x){s.disabled=false;s.textContent='Отправить ответ';er.textContent=x.message||'Нет связи. Попробуйте ещё раз';}
    return;}
  if(e.target.closest('[data-again]')){draw();V.querySelector('[data-rsvp]').scrollIntoView({block:'center'});return;}
  const wb=e.target.closest('[data-wi]');
  if(wb){const row=wb.closest('div');if(row.querySelector('.wform'))return;
    if(PREVIEW){wb.textContent='Доступно после публикации';return;}
    const f=document.createElement('form');f.className='wform';
    f.innerHTML=`<input aria-label="Ваше имя" placeholder="Ваше имя" maxlength="80" value="${esc(P.guest||'')}"><button>Подарю</button>`;
    row.appendChild(f);f.querySelector('input').focus();
    f.addEventListener('submit',async ev=>{ev.preventDefault();const nm=f.querySelector('input').value.trim();if(!nm){f.querySelector('input').focus();return;}
      const b=f.querySelector('button');b.disabled=true;
      try{const r=await fetch('/api/public/'+encodeURIComponent(KEY)+'/wish',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({idx:+wb.dataset.wi,name:nm})});
        const j=await r.json().catch(()=>({}));
        if(r.status===409){P.wishTaken.push(+wb.dataset.wi);wb.outerHTML='<span class="wtaken">Уже выбрали</span>';f.remove();return;}
        if(!r.ok)throw new Error(j.error||'Не получилось');
        P.wishTaken.push(+wb.dataset.wi);wb.outerHTML='<span class="wtaken">Вы выбрали этот подарок</span>';f.remove();}
      catch(x){b.disabled=false;b.textContent='Ещё раз';}});
  }
});
function wireWish(){const rows=V.querySelectorAll('.wish>div');if(!rows.length)return;
  const idx=(P.v.wish||[]).map((w,i)=>w.n?i:-1).filter(i=>i>=0);
  rows.forEach((row,k)=>{const b=row.querySelector('b');if(!b)return;const i=idx[k];
    b.outerHTML=(P.wishTaken||[]).includes(i)?'<span class="wtaken">Уже выбрали</span>':`<button type="button" class="wbtn" data-wi="${i}">Подарю</button>`;});}
__QRM__
function qrSvg(t){const m=QRM(t),n=m.length,q=2;let d='';m.forEach((r,y)=>r.forEach((on,x)=>{if(on)d+=`M${x+q} ${y+q}h1v1h-1z`;}));
  return `<svg viewBox="0 0 ${n+q*2} ${n+q*2}" shape-rendering="crispEdges" aria-label="QR-код"><path d="${d}" fill="#241B20"/></svg>`;}
const NOT_PRINTED={timer:'таймер',map:'карта и маршрут',rsvp:'ответ на приглашение',wishlist:'вишлист',gallery:'фото'};
function printView(D){
  document.body.classList.add('print');
  const t=TPL.find(x=>x.id===D.tpl)||TPL[0],sel=new Set(D.sel||[]);
  const ord=[...(D.order||[]).filter(id=>DEF_ORDER.includes(id)),...DEF_ORDER.filter(id=>!(D.order||[]).includes(id))];
  const on=new Set(['program','dress'].filter(x=>sel.has(x)));
  const online=Object.keys(NOT_PRINTED).filter(k=>sel.has(k)).map(k=>NOT_PRINTED[k]);
  const qrList=['map','rsvp','wishlist','gallery'].filter(k=>sel.has(k)).map(k=>NOT_PRINTED[k]);
  const sheet=(c)=>{
    const v={...D.v,guests:c.guest?[c.guest]:[],dear:[c.dear||''],tables:c.table?[{n:c.table}]:[],seat:c.table?[0]:[]},on1=new Set(on);if(c.guest)on1.add('named');if(c.table&&sel.has('seating'))on1.add('seating');
    const box=document.createElement('div');EXPAND_DAYS=true;box.innerHTML=full(t,v,on1,ord);EXPAND_DAYS=false;
    const inv=box.firstElementChild,cov=inv.querySelector('.cover');
    const front=inv.cloneNode(false);front.appendChild(cov);
    const dp=dparts(v.date),when=`${dp.dn} ${dp.mon} ${dp.y}, ${dp.wd}${v.time?', '+esc(v.time):''}`;
    /* date and place in one section instead of the map block */
    inv.querySelectorAll('section').forEach(x=>{if(x.querySelector('h4')&&x.querySelector('h4').textContent==='Место')x.remove();});
    inv.insertAdjacentHTML('afterbegin',`<section><h4>Когда и где</h4><p>${(v.events||[]).length?'<b>'+esc(dayTitle(v,0))+'</b><br>':''}${when}</p>${v.venue||v.addr?`<p style="margin-top:2cqi">${esc(v.venue||'')}${v.venue&&v.addr?'<br>':''}${esc(v.addr||'')}</p>`:''}${(v.events||[]).map((e,i)=>`<p style="margin-top:3cqi"><b>${esc(dayTitle(v,i+1))}</b>${evWhen(e)?'<br>'+esc(evWhen(e)):''}${e.venue||e.addr?'<br>'+esc([e.venue,e.addr].filter(Boolean).join(', ')):''}</p>`).join('')}</section>`);
    const seatSec=inv.querySelector('section.seat');
    const tail=`${seatSec?seatSec.outerHTML:''}
      ${c.link?`<section class="qr">${qrSvg(c.link)}<div><b>Наведите камеру телефона</b>${qrList.length?esc(qrList.join(', ').replace(/^./,x=>x.toUpperCase()))+' - по этому коду.':'Приглашение откроется на телефоне.'}</div></section>`:''}`;
    if(seatSec)seatSec.remove();
    inv.querySelector('.sign').insertAdjacentHTML('beforebegin',tail);
    const fit=document.createElement('div');fit.className='fit';while(inv.firstChild)fit.appendChild(inv.firstChild);inv.appendChild(fit);
    return `<div class="sheet front">${front.outerHTML}</div><div class="sheet back">${inv.outerHTML}</div>`;};
  const opts=D.cards.length>1?`<select id="who" aria-label="Для кого"><option value="-1">Все гости (${D.cards.length})</option>${D.cards.map((c,i)=>`<option value="${i}">${esc(c.guest)}</option>`).join('')}</select>`:'';
  V.innerHTML=`<div class="pbar"><div class="in"><h1>Печатная версия, формат A5</h1>
    <div class="warn">В печатной версии только обложка, дата, адрес${on.has('program')?', программа':''}${on.has('dress')?', дресс-код':''}.${online.length?` Здесь нет: ${esc(online.join(', '))}. Гость откроет это по QR-коду на обороте.`:''}${D.published?'':' <b>QR-коды появятся после публикации приглашения.</b>'}</div>
    <div class="row">${opts}<button type="button" id="pr">Сохранить PDF</button></div>
    <div class="n">В окне печати выберите «Сохранить как PDF». Каждое приглашение - 2 страницы: лицевая сторона и оборот. Для печати дома на A4 выберите «2 страницы на листе».</div></div></div>
    <div class="sheets" id="sh"></div>`;
  /* the back side shrinks as a whole when the program is long, so everything fits on one A5 page */
  const fitAll=()=>document.querySelectorAll('.sheet.back').forEach(sh=>{const f=sh.querySelector('.fit');f.style.width='100%';
    for(let k=0;k<3;k++){const H=sh.clientHeight*.97,h=f.scrollHeight;if(h<=H)break;f.style.width=(parseFloat(f.style.width)*H/h).toFixed(2)+'%';}});
  const fill=i=>{document.getElementById('sh').innerHTML=(i<0?D.cards:[D.cards[i]]).map(sheet).join('');fitAll();zoomIt();};
  if(document.fonts)document.fonts.ready.then(fitAll);
  /* phones: shrink the preview on screen only (print uses real A5) */
  function zoomIt(){const sh=document.getElementById('sh'),f=sh.querySelector('.sheet');if(!f)return;sh.style.zoom='';const z=Math.min(1,(innerWidth-24)/f.offsetWidth);sh.style.zoom=z<1?z.toFixed(3):'';}
  addEventListener('resize',zoomIt);
  fill(-1);
  const w=document.getElementById('who');if(w)w.onchange=()=>fill(+w.value);
  document.getElementById('pr').onclick=()=>window.print();}
/* server-side picture of the cover: link preview 1200x630 or stories 1080x1920 */
function renderView(R){
  document.body.className='render';const t=TPL.find(x=>x.id===R.tpl)||TPL[0];
  const box=document.createElement('div');box.innerHTML=full(t,R.v,new Set(R.sel||[]),DEF_ORDER);
  const inv=box.firstElementChild,cov=inv.querySelector('.cover');while(inv.firstChild)inv.removeChild(inv.firstChild);inv.appendChild(cov);
  V.innerHTML=`<div class="rn rn-${R.fmt}" style="${inv.getAttribute('style')}"><div class="rn-c">${inv.outerHTML}</div></div>`;
  const imgs=[...V.querySelectorAll('img')].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r;}));
  requestAnimationFrame(()=>requestAnimationFrame(()=>Promise.all([document.fonts?document.fonts.ready:0,...imgs]).then(()=>setTimeout(()=>{window.RENDER_DONE=true;},150))));}
(async()=>{
  if(window.RENDER){renderView(window.RENDER);return;}
  if(!KEY){msg('Приглашение не найдено');return;}
  if(PRINT){try{const r=await fetch('/api/invitations/'+encodeURIComponent(KEY)+'/print',{credentials:'same-origin'});const j=await r.json().catch(()=>({}));
      if(r.status===401){msg('Войдите в кабинет',`<p><a href="/">Перейти ко входу</a></p>`);return;}
      if(!r.ok){msg(r.status===403?'Печатная версия не подключена':'Приглашение не найдено',r.status===403?'<p>Добавьте блок «Печатная версия» в конструкторе.</p>':'');return;}
      document.title='Печатная версия - Knocky';printView(j);}
    catch(e){msg('Нет связи','<p>Проверьте интернет и обновите страницу.</p>');}
    return;}
  try{const r=await fetch(PREVIEW?'/api/invitations/'+encodeURIComponent(KEY)+'/preview':'/api/public/'+encodeURIComponent(KEY)+location.search,{credentials:'same-origin'});
    const j=await r.json().catch(()=>({}));
    if(r.status===401){msg('Войдите в кабинет',`<p><a href="/">Перейти ко входу</a></p>`);return;}
    if(!r.ok){msg('Приглашение не найдено','<p>Проверьте ссылку или спросите её у молодожёнов.</p>');return;}
    if(j.expired){msg(`${esc(j.v.a||'')} и ${esc(j.v.b||'')}`,'<p>Срок действия этого приглашения закончился.</p>');return;}
    P=j;P.wishTaken=P.wishTaken||[];draw();}
  catch(e){msg('Нет связи','<p>Проверьте интернет и обновите страницу.</p>');}
})();
"""

GUEST_JS = GUEST_JS.replace("__QRM__", (ROOT / "tools" / "qrm.js").read_text(encoding="utf-8"))

page = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Knocky</title><meta name="robots" content="noindex"><meta property="og:type" content="website"><meta property="og:site_name" content="Knocky">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/fonts.css">
<style>{css}
{GUEST_CSS}</style></head>
<body class="invite-mode"><div id="inviteView"></div>
<script>{renderer}
{GUEST_JS}
{mapjs}</script></body></html>"""

if "--plain" in sys.argv:
    Path(sys.argv[sys.argv.index("--plain") + 1]).write_text(page, encoding="utf-8")
key = hashlib.sha256(("knocky-render:" + token).encode()).digest()
nonce = os.urandom(12)
out = ROOT / "server" / "app" / "sealed" / "guest.enc"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(nonce + AESGCM(key).encrypt(nonce, page.encode("utf-8"), None))
print("sealed", out, len(page) // 1024, "KB")
