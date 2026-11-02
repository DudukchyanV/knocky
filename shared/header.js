/* Knocky shared header: the same file on knocky.ru and app.knocky.ru (tools/inject_header.py) */
(function(){
  var root=document.documentElement,$=function(i){return document.getElementById(i);};
  var page=/^app\./.test(location.hostname)||location.port==='8000'?'cab':'home',API=page==='cab'?'/api':'https://app.knocky.ru/api';
  document.querySelectorAll('.kh [data-k]').forEach(function(a){if(a.getAttribute('data-k')===page)a.setAttribute('aria-current','page');});
  /* theme: one setting for knocky.ru and app.knocky.ru (cookie on the whole domain) */
  function readTheme(){var c;try{c=(document.cookie.match(/(?:^|; )knocky-theme=(dark|light)/)||[])[1]||localStorage.getItem('knocky-theme');}catch(e){}return c==='dark'?'dark':'light';}
  function setTheme(t,save){root.setAttribute('data-theme',t);$('khTheme').setAttribute('aria-checked',t==='dark'?'true':'false');
    if(save)try{localStorage.setItem('knocky-theme',t);document.cookie='knocky-theme='+t+';path=/;max-age=31536000;samesite=lax'+(/knocky\.ru$/.test(location.hostname)?';domain=knocky.ru':'');}catch(e){}
    try{document.dispatchEvent(new CustomEvent('kh-theme',{detail:t}));}catch(e){}}
  setTheme(readTheme(),false);
  $('khTheme').addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark',true);});
  addEventListener('pageshow',function(){var t=readTheme();if(t!==root.getAttribute('data-theme'))setTheme(t,false);});
  /* menu */
  var btn=$('khMenuBtn'),menu=$('khMenu');
  function isOpen(){return menu.classList.contains('open');}
  function setMenu(o){menu.classList.toggle('open',o);menu.setAttribute('aria-hidden',!o);btn.setAttribute('aria-expanded',o);btn.querySelector('span').textContent=o?'Закрыть':'Меню';}
  btn.addEventListener('click',function(e){e.stopPropagation();setMenu(!isOpen());});
  menu.addEventListener('click',function(e){if(e.target.closest('a,button'))setMenu(false);});
  document.addEventListener('click',function(e){if(isOpen()&&!e.target.closest('#khMenu'))setMenu(false);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&isOpen()){setMenu(false);btn.focus();}});
  /* who is signed in */
  function setUser(email){$('khMail').hidden=$('khMe').hidden=!email;$('khMail').textContent=email||'';
    try{document.dispatchEvent(new CustomEvent('kh-user',{detail:email||null}));}catch(e){}}
  function loadUser(){fetch(API+'/me',{credentials:'include'}).then(function(r){return r.json();}).then(function(j){setUser(j&&j.user?j.user.email:null);}).catch(function(){setUser(null);});}
  $('khOut').addEventListener('click',function(){fetch(API+'/auth/logout',{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:'{}'}).catch(function(){}).then(function(){setUser(null);try{document.dispatchEvent(new CustomEvent('kh-logout'));}catch(e){}});});
  window.KH={setUser:setUser,reload:loadUser,page:page};
  loadUser();addEventListener('pageshow',function(e){if(e.persisted)loadUser();});
})();
