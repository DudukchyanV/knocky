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
.pvbar{position:sticky;top:0;z-index:50;background:#C62828;color:#fff;text-align:center;font:600 13px/1.4 var(--f-body);padding:8px 12px}
"""

GUEST_JS = r"""
/* ===== guest page: data from the server ===== */
const V=document.getElementById('inviteView');
const parts_=location.pathname.split('/').filter(Boolean);
const PREVIEW=parts_[0]==='p';const KEY=decodeURIComponent(parts_[1]||'');
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
  more.innerHTML=`<div class="lbl">Сколько вас будет</div><select data-people aria-label="Сколько вас будет">${[1,2,3,4,5,6,7,8].map(n=>`<option value="${n}">${n}</option>`).join('')}</select>`;
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
    const yes=ch.dataset.o==='1';s.disabled=true;s.textContent='Отправляем…';
    try{const r=await fetch('/api/public/'+encodeURIComponent(KEY)+'/rsvp',{method:'POST',headers:{'content-type':'application/json'},
        body:JSON.stringify({name:n,attend:yes,people:+(box.querySelector('[data-people]')||{}).value||1,comment:(box.querySelector('textarea')||{}).value||'',g:G})});
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
(async()=>{
  if(!KEY){msg('Приглашение не найдено');return;}
  try{const r=await fetch(PREVIEW?'/api/invitations/'+encodeURIComponent(KEY)+'/preview':'/api/public/'+encodeURIComponent(KEY)+location.search,{credentials:'same-origin'});
    const j=await r.json().catch(()=>({}));
    if(r.status===401){msg('Войдите в кабинет',`<p><a href="/">Перейти ко входу</a></p>`);return;}
    if(!r.ok){msg('Приглашение не найдено','<p>Проверьте ссылку или спросите её у молодожёнов.</p>');return;}
    if(j.expired){msg(`${esc(j.v.a||'')} и ${esc(j.v.b||'')}`,'<p>Срок действия этого приглашения закончился.</p>');return;}
    P=j;P.wishTaken=P.wishTaken||[];draw();}
  catch(e){msg('Нет связи','<p>Проверьте интернет и обновите страницу.</p>');}
})();
"""

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
