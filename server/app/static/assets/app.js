/* Knocky cabinet: login by email code, invitations, guest answers */
const $=(s,r=document)=>r.querySelector(s);
const app=$('#app');
const SITE='https://knocky.ru';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const M=['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
const plural=(n,a,b,c)=>{const m=n%10,h=n%100;return n+' '+(m===1&&h!==11?a:m>=2&&m<=4&&(h<12||h>14)?b:c);};
const dateLong=s=>{if(!s)return'';const[y,m,d]=s.split('-').map(Number);return d&&m?`${d} ${M[m-1]} ${y}`:''};
const tsDate=t=>t?new Date(t*1000).toLocaleDateString('ru-RU',{day:'numeric',month:'long',year:'numeric'}).replace(/\s*г\.?$/,''):'';
const tsShort=t=>t?new Date(t*1000).toLocaleString('ru-RU',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}):'';
const IC={
  back:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
  copy:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2.5"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/></svg>',
  ext:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
  dl:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>',
  edit:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h4L19 9l-4-4L4 16v4Z"/></svg>'
};
let ME=null,DESIGNS={};

async function api(path,opt={}){
  const r=await fetch('/api'+path,{credentials:'same-origin',...opt,headers:{'content-type':'application/json',...(opt.headers||{})}});
  let j={};try{j=await r.json()}catch(e){}
  if(!r.ok){const e=new Error(j.error||'Нет связи с сервером. Попробуйте ещё раз');e.status=r.status;e.data=j;throw e;}
  return j;}
function toast(t){const el=$('#toast');el.textContent=t;el.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>el.hidden=true,2600);}
async function copy(t){try{await navigator.clipboard.writeText(t);toast('Ссылка скопирована');}catch(e){prompt('Скопируйте ссылку',t);}}
function go(p,replace){history[replace?'replaceState':'pushState']({},'',p);route();}
document.addEventListener('click',e=>{const a=e.target.closest('a[data-go]');if(a&&!e.metaKey&&!e.ctrlKey){e.preventDefault();go(a.getAttribute('href'));}});
window.addEventListener('popstate',route);

/* theme */
const themeBtn=$('#themeBtn');
function curTheme(){return document.documentElement.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');}
function setTheme(t){document.documentElement.dataset.theme=t;themeBtn.setAttribute('aria-checked',t==='dark');try{localStorage.setItem('knocky-theme',t)}catch(e){}}
themeBtn.setAttribute('aria-checked',curTheme()==='dark');
themeBtn.onclick=()=>setTheme(curTheme()==='dark'?'light':'dark');
$('#logoutBtn').onclick=async()=>{try{await api('/auth/logout',{method:'POST'})}catch(e){}ME=null;showWho();go('/',true);};
function showWho(){$('#who').hidden=!ME;if(ME)$('#whoMail').textContent=ME.email;}

/* ---------- login ---------- */
function loginView(){
  const claim=new URLSearchParams(location.search).get('claim')||'';
  let email=(new URLSearchParams(location.search).get('email')||'').trim().toLowerCase(),step='mail',timer=0,tick=null;
  document.title='Вход - Кабинет Knocky';
  const draw=()=>{
    if(step==='mail'){
      app.innerHTML=`<section class="auth"><form class="auth-card" id="f" novalidate>
        <h1>Вход в кабинет</h1>
        <p class="note">${claim?'Приглашение сохранено. Войдите, чтобы оно появилось в кабинете.':'Здесь ваши приглашения, ссылки для гостей и их ответы.'} Пароль не нужен: пришлём код на почту.</p>
        <label class="field"><span>Почта</span><input class="inp" id="em" type="email" inputmode="email" autocomplete="email" placeholder="anna@mail.ru" value="${esc(email)}" required></label>
        <label class="check" id="agreeRow"><input type="checkbox" id="agree"><span>Согласен(на) с <a href="${SITE}/#doc-privacy" target="_blank" rel="noopener">политикой обработки персональных данных</a> и даю <a href="${SITE}/#doc-consent" target="_blank" rel="noopener">согласие на обработку</a></span></label>
        <p class="err" id="er" role="alert" hidden></p>
        <button class="btn btn-seal btn-xl" id="sb">Получить код</button>
        <button type="button" class="lnk" id="toPw" style="justify-self:center">Вход для администратора по паролю</button>
      </form></section>`;
      $('#toPw').onclick=()=>{email=$('#em').value.trim().toLowerCase();step='pw';draw();};
      const f=$('#f'),em=$('#em'),er=$('#er');em.focus();
      f.onsubmit=async e=>{e.preventDefault();er.hidden=true;email=em.value.trim().toLowerCase();
        if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){er.hidden=false;er.textContent='Введите почту, например anna@mail.ru';em.focus();return;}
        const b=$('#sb');b.disabled=true;b.textContent='Отправляем код…';
        try{await api('/auth/request',{method:'POST',body:JSON.stringify({email,agree:$('#agree').checked})});step='code';timer=60;draw();}
        catch(x){if(x.data&&x.data.already){step='code';timer=Math.max(1,x.data.wait||50);draw();return;}b.disabled=false;b.textContent='Получить код';er.hidden=false;er.textContent=x.data&&x.data.need_agree?'Отметьте согласие на обработку персональных данных':x.message;}};
    }else if(step==='pw'){
      app.innerHTML=`<section class="auth"><form class="auth-card" id="f" novalidate>
        <h1>Вход по паролю</h1>
        <p class="note">Для администраторов. Пароль задается на странице настройки сервера.</p>
        <label class="field"><span>Почта</span><input class="inp" id="em" type="email" autocomplete="username" value="${esc(email||'me@dudukchyan.ru')}"></label>
        <label class="field"><span>Пароль</span><input class="inp" id="pw" type="password" autocomplete="current-password"></label>
        <p class="err" id="er" role="alert" hidden></p>
        <button class="btn btn-seal btn-xl" id="sb">Войти</button>
        <button type="button" class="lnk" id="toMail" style="justify-self:center">Войти по коду из письма</button>
      </form></section>`;
      const er=$('#er');$('#pw').focus();
      $('#toMail').onclick=()=>{step='mail';draw();};
      $('#f').onsubmit=async e=>{e.preventDefault();er.hidden=true;const b=$('#sb');email=$('#em').value.trim().toLowerCase();
        if(!$('#pw').value){er.hidden=false;er.textContent='Введите пароль';return;}
        b.disabled=true;b.textContent='Проверяем…';
        try{const j=await api('/auth/password',{method:'POST',body:JSON.stringify({email,password:$('#pw').value})});ME=j.user;showWho();
          if(claim){try{const c=await api('/drafts/claim',{method:'POST',body:JSON.stringify({claim})});return go('/inv/'+c.id,true);}catch(_){}}
          go('/',true);}
        catch(x){b.disabled=false;b.textContent='Войти';er.hidden=false;er.textContent=x.message;}};
    }else{
      app.innerHTML=`<section class="auth"><form class="auth-card" id="f" novalidate>
        <h1>Введите код</h1>
        <p class="note">Отправили 6 цифр на <b>${esc(email)}</b>. Письмо может прийти через минуту, проверьте папку «Спам».</p>
        <input class="inp code" id="cd" inputmode="numeric" autocomplete="one-time-code" maxlength="6" placeholder="······" aria-label="Код из письма">
        <p class="err" id="er" role="alert" hidden></p>
        <button class="btn btn-seal btn-xl" id="sb">Войти</button>
        <div class="row spread"><button type="button" class="lnk" id="chg">Другая почта</button><button type="button" class="lnk" id="again"></button></div>
      </form></section>`;
      const cd=$('#cd'),er=$('#er'),ag=$('#again');cd.focus();
      const upd=()=>{ag.disabled=timer>0;ag.textContent=timer>0?`Новый код через ${timer} с`:'Отправить код ещё раз';ag.style.opacity=timer>0?.55:1;};
      upd();clearInterval(tick);tick=setInterval(()=>{if(timer>0){timer--;upd();}},1000);
      cd.oninput=()=>{cd.value=cd.value.replace(/\D/g,'').slice(0,6);if(cd.value.length===6)$('#f').requestSubmit();};
      $('#chg').onclick=()=>{clearInterval(tick);step='mail';draw();};
      ag.onclick=async()=>{if(timer>0)return;try{await api('/auth/request',{method:'POST',body:JSON.stringify({email,agree:true})});timer=60;upd();toast('Новый код отправлен');}catch(x){er.hidden=false;er.textContent=x.message;}};
      $('#f').onsubmit=async e=>{e.preventDefault();er.hidden=true;const b=$('#sb');
        if(cd.value.length!==6){er.hidden=false;er.textContent='Введите 6 цифр из письма';return;}
        b.disabled=true;b.textContent='Проверяем…';
        try{const j=await api('/auth/verify',{method:'POST',body:JSON.stringify({email,code:cd.value,claim})});clearInterval(tick);ME=j.user;showWho();go('/',true);}
        catch(x){b.disabled=false;b.textContent='Войти';er.hidden=false;er.textContent=x.message;cd.select();}};
    }};
  draw();}

/* ---------- list ---------- */
function status(o){
  if(o.status==='published'&&o.expired)return'<span class="chip red"><i></i>Срок истёк</span>';
  if(o.status==='published')return'<span class="chip pub"><i></i>Опубликовано</span>';
  return'<span class="chip"><i></i>Черновик</span>';}
function swatch(o){const d=DESIGNS[o.tpl]||{n:'',bg:'#F3EEEE',ink:'#241B20',acc:'#C62828'};
  const [a,b]=(o.title||'').split(' и ');
  return`<div class="sw" style="background:${d.bg};color:${d.acc}" aria-hidden="true"><span style="color:${d.ink}">${esc((a||'').slice(0,1))}<span style="color:${d.acc}">&nbsp;и&nbsp;</span>${esc((b||'').slice(0,1))}</span></div>`;}
function cardOf(o,admin){const d=DESIGNS[o.tpl];
  const a=o.answers||{};const ans=o.status==='published'&&o.sel&&o.sel.includes('rsvp')?`<span class="chip">${plural(a.yes||0,'ответ «приду»','ответа «приду»','ответов «приду»')}</span>`:'';
  return`<a class="card" href="/inv/${esc(o.id)}${admin?'?from=admin':''}" data-go>${swatch(o)}<div style="min-width:0">
    <h3>${esc(o.title)}</h3><div class="meta">${o.date?esc(dateLong(o.date)):'Дата не указана'}${d?' · '+esc(d.n):''}</div>
    ${admin&&o.owner!==undefined?`<div class="owner">${esc(o.owner||'без владельца')}</div>`:''}
    <div class="chips">${status(o)}${ans}</div></div></a>`;}
async function listView(admin){
  document.title=(admin?'Все приглашения':'Мои приглашения')+' - Кабинет Knocky';
  app.innerHTML='<div class="spin" aria-label="Загрузка"></div>';
  let items=[];
  try{items=(await api('/invitations'+(admin?'?all=1':''))).items;}catch(x){app.innerHTML=`<div class="empty"><h2>Не получилось загрузить</h2><p>${esc(x.message)}</p><button class="btn btn-soft" onclick="location.reload()">Обновить</button></div>`;return;}
  const tabs=ME.admin?`<div class="tabs" role="tablist"><button role="tab" aria-selected="${!admin}" data-t="/">Мои</button><button role="tab" aria-selected="${!!admin}" data-t="/admin">Все приглашения</button></div>`:'';
  const head=`<div class="head"><div><h1>${admin?'Все приглашения':'Мои приглашения'}</h1>
    <p>${admin?plural(items.length,'приглашение','приглашения','приглашений')+' на сервисе':'Черновики, опубликованные приглашения и ответы гостей.'}</p></div>${tabs}</div>`;
  const newCard=`<a class="new" href="${SITE}/#templates"><b aria-hidden="true">+</b>Создать приглашение</a>`;
  if(!items.length&&!admin){
    app.innerHTML=head+`<div class="empty"><h2>Здесь пока пусто</h2><p>Выберите дизайн на knocky.ru, заполните данные и сохраните приглашение - оно появится здесь. Отсюда вы отправите ссылку гостям и будете видеть их ответы.</p><a class="btn btn-seal btn-xl" href="${SITE}/#templates">Выбрать дизайн</a></div>`;
  }else{
    app.innerHTML=head+(admin?`<div style="margin:-6px 0 16px"><input class="inp search" id="q" type="search" placeholder="Поиск: имена, почта, адрес ссылки" aria-label="Поиск"></div>`:'')+
      `<div class="cards" id="cards">${items.map(o=>cardOf(o,admin)).join('')}${admin?'':newCard}</div>`;
    if(admin)$('#q').oninput=e=>{const q=e.target.value.trim().toLowerCase();
      $('#cards').innerHTML=items.filter(o=>!q||[o.title,o.owner,o.slug].join(' ').toLowerCase().includes(q)).map(o=>cardOf(o,true)).join('')||'<p class="note">Ничего не нашлось</p>';};
  }
  app.querySelectorAll('[data-t]').forEach(b=>b.onclick=()=>go(b.dataset.t));}

/* ---------- one invitation ---------- */
async function invView(id){
  app.innerHTML='<div class="spin" aria-label="Загрузка"></div>';
  let o,ans;
  try{[o,ans]=await Promise.all([api('/invitations/'+encodeURIComponent(id)),api('/invitations/'+encodeURIComponent(id)+'/answers')]);}
  catch(x){app.innerHTML=`<a class="back" href="/" data-go>${IC.back}Мои приглашения</a><div class="empty"><h2>${x.status===404?'Приглашение не найдено':'Не получилось загрузить'}</h2><p>${esc(x.message)}</p></div>`;return;}
  document.title=o.title+' - Кабинет Knocky';
  const d=DESIGNS[o.tpl],pub=o.status==='published',a=o.answers,sel=new Set(o.sel||[]);
  const editUrl=`${SITE}/#edit=${encodeURIComponent(o.id)}`;
  const shareText=`${o.title}: приглашение на свадьбу`;
  const linkBlock=pub?`<div class="panel"><h2>Ссылка для гостей</h2>
      <div class="link"><a href="${esc(o.link)}" target="_blank" rel="noopener">${esc(o.link.replace('https://',''))}</a><button class="btn btn-seal btn-sm" data-copy="${esc(o.link)}">${IC.copy}Копировать</button></div>
      <div class="acts" style="margin-top:12px"><a class="btn btn-soft btn-sm" href="https://t.me/share/url?url=${encodeURIComponent(o.link)}&text=${encodeURIComponent(shareText)}" target="_blank" rel="noopener">Отправить в Telegram</a>
      <a class="btn btn-soft btn-sm" href="https://wa.me/?text=${encodeURIComponent(shareText+' '+o.link)}" target="_blank" rel="noopener">Отправить в WhatsApp</a>
      <a class="btn btn-ghost btn-sm" href="${esc(o.link)}" target="_blank" rel="noopener">${IC.ext}Открыть</a></div>
      <p class="note" style="margin-top:12px">${o.expired?'Срок действия ссылки закончился '+esc(tsDate(o.expires_at))+'.':'Ссылка работает до '+esc(tsDate(o.expires_at))+'.'} Тексты, время и адрес можно менять до праздника, ссылка у гостей не изменится.</p></div>`
    :`<div class="panel"><h2>Публикация</h2>
      <label class="field"><span>Адрес ссылки</span><div class="slug"><span>knocky.ru/</span><input class="inp" id="slug" value="${esc(o.slug||'')}" placeholder="anna-ilya" maxlength="40" autocomplete="off" spellcheck="false"></div></label>
      <p class="note" style="margin-top:8px">Латинские буквы, цифры и дефис. Если оставить пустым, адрес соберём из имён.</p>
      <p class="err" id="slugEr" hidden></p>
      <div class="acts" style="margin-top:14px">${ME.admin?`<button class="btn btn-seal" id="pubBtn">Опубликовать без оплаты</button>`:`<button class="btn btn-seal" aria-disabled="true" id="payBtn">Оплатить и получить ссылку</button>`}<button class="btn btn-soft" id="slugSave">Сохранить адрес</button></div>
      </div>`;
  const rsvpOn=sel.has('rsvp'),namedOn=sel.has('named'),wishOn=sel.has('wishlist');
  const tabs=[rsvpOn&&['ans','Ответы'],namedOn&&['gst','Именные ссылки'],wishOn&&['wish','Подарки']].filter(Boolean);
  const opened=ans.guests.filter(g=>g.opens>0).length;
  app.innerHTML=`<a class="back" href="${ME.admin&&location.search.includes('from=admin')?'/admin':'/'}" data-go>${IC.back}Мои приглашения</a>
  <div class="inv"><div class="inv-main">
    <div class="panel title"><div class="row spread"><h1>${esc(o.title)}</h1>${status(o)}</div>
      <div class="meta">${o.date?esc(dateLong(o.date)):'Дата не указана'}${d?' · дизайн «'+esc(d.n)+'»':''}${o.paid_via==='admin'?' · без оплаты (админ)':''}</div>
      <div class="acts"><a class="btn btn-soft" href="${editUrl}" target="_blank" rel="noopener">${IC.edit}Редактировать</a><a class="btn btn-ghost" href="/p/${esc(o.id)}" target="_blank" rel="noopener">${IC.ext}Предпросмотр</a>
      ${!pub||ME.admin?`<button class="btn btn-ghost" id="delBtn">Удалить</button>`:''}${ME.admin&&pub?`<button class="btn btn-ghost" id="unpubBtn">Снять с публикации</button>`:''}</div></div>
    ${linkBlock}
    ${rsvpOn||namedOn?`<div class="stats">
      <div class="stat yes"><b>${a.people||0}</b><span>${a.people===1?'гость придёт':'гостей придут'}</span></div>
      <div class="stat"><b>${a.no||0}</b><span>не смогут</span></div>
      ${namedOn?`<div class="stat"><b>${opened}<small style="font-size:15px;color:var(--muted)"> / ${ans.guests.length}</small></b><span>открыли ссылку</span></div>`:`<div class="stat"><b>${a.total||0}</b><span>всего ответов</span></div>`}</div>`:''}
    ${tabs.length?`<div class="panel"><div class="row spread" style="margin-bottom:14px"><div class="tabs" role="tablist">${tabs.map((t,i)=>`<button role="tab" aria-selected="${i===0}" data-tab="${t[0]}">${t[1]}</button>`).join('')}</div>
      <a class="btn btn-soft btn-sm" href="/api/invitations/${esc(o.id)}/export.xlsx">${IC.dl}Скачать Excel</a></div><div id="tabBody"></div></div>`:''}
  </div>
  <aside class="phone"><div class="scr"><iframe src="/p/${esc(o.id)}" title="Предпросмотр приглашения" loading="lazy"></iframe></div><a class="note" href="/p/${esc(o.id)}" target="_blank" rel="noopener">Открыть во весь экран</a></aside></div>`;

  const body=t=>{const el=$('#tabBody');if(!el)return;
    if(t==='ans')el.innerHTML=ans.answers.length?`<div class="tbl"><table><thead><tr><th>Гость</th><th>Ответ</th><th>Сколько</th><th>Комментарий</th><th>Когда</th></tr></thead><tbody>${ans.answers.map(r=>`<tr><td><b>${esc(r.name)}</b>${r.guest&&r.guest!==r.name?`<div class="note">ссылка: ${esc(r.guest)}</div>`:''}</td><td>${r.attend?'<span class="chip pub">Придёт</span>':'<span class="chip red">Не сможет</span>'}</td><td>${r.attend?r.people:'-'}</td><td class="c">${esc(r.comment)||'-'}</td><td class="c nowrap">${esc(tsShort(r.at))}</td></tr>`).join('')}</tbody></table></div>`
      :`<p class="empty-row">${pub?'Пока никто не ответил. Ответы появятся здесь сразу, как гости заполнят анкету.':'Ответы появятся после публикации.'}</p>`;
    if(t==='gst')el.innerHTML=ans.guests.length?`<div class="tbl"><table><thead><tr><th>Гость</th><th>Открыл</th><th>Ответ</th><th></th></tr></thead><tbody>${ans.guests.map(g=>`<tr><td><b>${esc(g.name)}</b></td><td class="c nowrap">${g.opens?esc(tsShort(g.first_open)):'нет'}</td><td>${g.answer===null?'<span class="note">-</span>':g.answer?'<span class="chip pub">Придёт</span>':'<span class="chip red">Не сможет</span>'}</td><td class="nowrap" style="text-align:right">${g.link?`<button class="btn btn-soft btn-sm" data-copy="${esc(g.link)}">${IC.copy}Ссылка</button>`:'<span class="note">после публикации</span>'}</td></tr>`).join('')}</tbody></table></div>`
      :'<p class="empty-row">Добавьте гостей в редакторе: блок «Именные ссылки», одна строка - одна ссылка.</p>';
    if(t==='wish')el.innerHTML=ans.wish.length?`<div class="tbl"><table><thead><tr><th>Подарок</th><th>Кто подарит</th></tr></thead><tbody>${ans.wish.map(w=>`<tr><td><b>${esc(w.n)}</b></td><td>${w.by?esc(w.by):'<span class="note">свободно</span>'}</td></tr>`).join('')}</tbody></table></div>`
      :'<p class="empty-row">В вишлисте пока нет подарков. Добавьте их в редакторе.</p>';};
  if(tabs.length){body(tabs[0][0]);app.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{app.querySelectorAll('[data-tab]').forEach(x=>x.setAttribute('aria-selected',x===b));body(b.dataset.tab);});}
  app.onclick=e=>{const c=e.target.closest('[data-copy]');if(c)copy(c.dataset.copy);};
  const slugIn=$('#slug'),slugEr=$('#slugEr');
  if(slugIn)slugIn.oninput=()=>{slugIn.value=slugIn.value.toLowerCase().replace(/[^a-z0-9-]/g,'');};
  const saveSlug=async()=>{slugEr.hidden=true;try{await api('/invitations/'+o.id,{method:'PUT',body:JSON.stringify({slug:slugIn.value})});return true;}catch(x){slugEr.hidden=false;slugEr.textContent=x.message;return false;}};
  if($('#slugSave'))$('#slugSave').onclick=async()=>{if(!slugIn.value){slugEr.hidden=false;slugEr.textContent='Впишите адрес или опубликуйте - соберём его из имён';return;}if(await saveSlug())toast('Адрес сохранён');};
  if($('#pubBtn'))$('#pubBtn').onclick=async()=>{if(slugIn.value&&slugIn.value!==(o.slug||'')&&!(await saveSlug()))return;
    try{await api('/invitations/'+o.id+'/publish',{method:'POST'});toast('Опубликовано');invView(id);}catch(x){slugEr.hidden=false;slugEr.textContent=x.message;}};
  if($('#payBtn'))$('#payBtn').onclick=()=>toast('Оплата скоро заработает');
  if($('#unpubBtn'))$('#unpubBtn').onclick=async()=>{if(!(await ask('Снять с публикации?','Гости перестанут видеть приглашение по ссылке, пока вы не опубликуете его снова.','Снять')))return;
    try{await api('/invitations/'+o.id+'/unpublish',{method:'POST'});invView(id);}catch(x){toast(x.message);}};
  if($('#delBtn'))$('#delBtn').onclick=async()=>{if(!(await ask('Удалить приглашение?',pub?'Ссылка у гостей перестанет работать, ответы удалятся. Это нельзя отменить.':'Черновик удалится насовсем.','Удалить')))return;
    try{await api('/invitations/'+o.id,{method:'DELETE'});toast('Удалено');go('/');}catch(x){toast(x.message);}};
}
function ask(title,text,ok){return new Promise(res=>{const d=document.createElement('dialog');
  d.innerHTML=`<h2>${esc(title)}</h2><p class="note" style="margin-top:8px">${esc(text)}</p><div class="acts"><button class="btn btn-soft" value="no">Отмена</button><button class="btn btn-seal" value="yes">${esc(ok)}</button></div>`;
  document.body.appendChild(d);d.addEventListener('close',()=>{res(d.returnValue==='yes');d.remove();});
  d.querySelectorAll('button').forEach(b=>b.onclick=()=>d.close(b.value));d.showModal();d.querySelector('[value=no]').focus();});}

/* ---------- router ---------- */
async function route(){
  window.scrollTo(0,0);
  if(ME===null){try{const j=await api('/me');ME=j.user||false;}catch(e){ME=false;}showWho();}
  if(!ME){loginView();return;}
  const p=location.pathname;
  const claim=new URLSearchParams(location.search).get('claim');
  if(claim){history.replaceState({},'','/');try{const j=await api('/drafts/claim',{method:'POST',body:JSON.stringify({claim})});return go('/inv/'+j.id,true);}catch(e){}}
  let m;
  if((m=p.match(/^\/inv\/([\w-]+)/)))return invView(m[1]);
  if(p==='/admin'&&ME.admin)return listView(true);
  return listView(false);}
fetch('/assets/designs.json').then(r=>r.json()).then(d=>{DESIGNS=d;}).catch(()=>{}).finally(route);
