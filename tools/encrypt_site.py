"""Encrypt a single-page site (AES-GCM) with a random key; the key is wrapped by each password (PBKDF2-SHA256).
Usage: python3 encrypt_site.py SRC.html OUT.html PASSWORD [PASSWORD ...]
"""
import base64, json, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

src, out, passwords = sys.argv[1], sys.argv[2], sys.argv[3:]
assert passwords
ITER = 600_000
html = open(src, encoding='utf-8').read()
if '<!doctype' not in html[:200].lower():
    html = ('<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n') + html
b64 = lambda b: base64.b64encode(b).decode()
K, iv = os.urandom(32), os.urandom(12)
ct = AESGCM(K).encrypt(iv, html.encode('utf-8'), None)
wraps = []
for pw in passwords:
    s, wi = os.urandom(16), os.urandom(12)
    wk = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=s, iterations=ITER).derive(pw.encode('utf-8'))
    wraps.append({'s': b64(s), 'i': b64(wi), 'w': b64(AESGCM(wk).encrypt(wi, K, None))})
payload = json.dumps({'i': b64(iv), 'c': b64(ct), 'n': ITER, 'k': wraps})

# seal paths from the logo
_sp = json.load(open(os.path.join(os.path.dirname(__file__), 'seal_paths.json')))
OUTER, INNER = _sp['outer'], _sp['inner']
seal = (f'<svg class="seal" viewBox="0 0 100 100" aria-hidden="true"><path d="{OUTER}" fill="#C62828"/><path d="{INNER}" fill="#8E1A20"/>'
        '<text x="50" y="63" text-anchor="middle" font-family="Unbounded, Arial Black, sans-serif" font-weight="600" font-size="38" fill="#E0564E">k</text></svg>')

page = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Knocky</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M95.3 50.0 L96.4 54.1 L95.7 58.1 L93.9 61.8 L91.7 65.2 L89.6 68.5 L87.5 71.7 L85.2 74.6 L82.5 77.2 L79.7 79.7 L77.3 82.5 L75.2 86.0 L73.0 89.8 L70.0 92.9 L66.2 94.4 L61.8 93.9 L57.4 92.1 L53.5 90.5 L50.0 90.3 L46.4 91.5 L42.4 93.4 L38.1 94.4 L34.0 93.8 L30.5 91.8 L27.5 89.0 L24.7 86.1 L22.0 83.4 L19.5 80.5 L17.3 77.4 L15.5 74.2 L13.6 71.0 L11.1 68.1 L8.0 65.3 L4.9 62.1 L3.2 58.3 L3.5 54.1 L5.7 50.0 L8.4 46.4 L10.4 43.0 L10.7 39.5 L9.9 35.4 L9.2 31.0 L9.8 26.8 L11.9 23.3 L15.0 20.7 L18.5 18.5 L21.9 16.5 L25.1 14.5 L28.5 12.8 L32.1 11.5 L35.6 10.5 L39.1 9.1 L42.4 7.0 L46.0 4.6 L50.0 2.8 L54.1 2.8 L58.0 4.9 L61.2 8.3 L64.0 11.6 L67.0 13.6 L70.7 14.1 L75.1 14.2 L79.4 15.0 L83.0 17.0 L85.4 20.3 L87.0 24.1 L88.3 27.9 L89.5 31.6 L90.6 35.2 L91.3 38.9 L91.6 42.7 L91.9 46.3 Z' fill='%23C62828'/%3E%3Cpath d='M83.9 50.0 L84.0 53.0 L82.8 55.8 L81.4 58.4 L80.5 61.1 L79.5 63.7 L78.3 66.3 L77.3 69.1 L76.1 71.9 L74.0 74.0 L70.9 74.9 L68.1 75.8 L66.1 77.9 L64.3 80.6 L61.7 82.1 L58.6 82.3 L55.7 82.1 L52.8 82.3 L50.0 82.5 L47.2 82.5 L44.2 82.7 L41.2 82.9 L38.4 81.9 L36.2 79.5 L34.2 77.3 L31.6 76.3 L28.4 75.8 L25.8 74.2 L24.3 71.5 L23.3 68.7 L21.9 66.2 L20.5 63.7 L19.4 61.1 L18.0 58.6 L16.5 55.9 L16.1 53.0 L17.3 50.0 L18.6 47.2 L18.5 44.4 L17.6 41.3 L17.8 38.3 L19.6 35.8 L21.7 33.7 L23.4 31.4 L25.1 29.1 L27.0 27.0 L28.8 24.7 L30.5 22.2 L33.0 20.5 L36.1 20.2 L39.2 20.3 L41.7 19.2 L44.2 17.1 L47.0 15.9 L50.0 16.3 L52.9 17.4 L55.6 18.0 L58.4 18.6 L61.1 19.4 L63.9 20.1 L66.9 20.7 L69.6 22.0 L71.2 24.7 L72.4 27.6 L74.4 29.6 L77.2 30.9 L79.6 32.9 L80.6 35.7 L80.8 38.8 L81.3 41.6 L82.0 44.4 L82.4 47.2 Z' fill='%238E1A20'/%3E%3Ctext x='50' y='63' text-anchor='middle' font-family='Arial Black,sans-serif' font-weight='900' font-size='38' fill='%23E0564E'%3Ek%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600&family=Manrope:wght@500;700&display=swap">
<style>
:root{{--bg:#F7F4F4;--surface:#FFFFFF;--soft:#F3EEEE;--ink:#241B20;--muted:#6F6068;--seal:#C62828}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141112;--surface:#1E1A1B;--soft:#292324;--ink:#F3EEEE;--muted:#A99BA1}}}}
*{{box-sizing:border-box}}
html,body{{margin:0;height:100%}}
body{{background:var(--bg);color:var(--ink);font:500 16px/1.5 Manrope,system-ui,sans-serif;display:grid;place-items:center;padding:20px}}
.box{{width:100%;max-width:360px}}
.logo{{display:flex;align-items:center;gap:8px;font:600 26px/1 Unbounded,'Arial Black',sans-serif;letter-spacing:-1px}}
.seal{{width:32px;height:32px}}
p{{color:var(--muted);margin:18px 0 22px}}
form{{display:flex;flex-direction:column;gap:12px}}
input#pw{{font:inherit;font-size:16px;color:var(--ink);background:var(--surface);border:1px solid transparent;border-radius:12px;padding:14px 16px;width:100%}}
input#pw:focus{{outline:none;border-color:var(--seal)}}
label.rm{{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--muted)}}
label.rm input{{accent-color:var(--seal);width:16px;height:16px}}
button#go{{font:700 16px Manrope,system-ui,sans-serif;border:0;border-radius:999px;padding:14px 24px;background:var(--seal);color:#fff;cursor:pointer}}
button#go[disabled]{{opacity:.6;cursor:wait}}
.pw{{position:relative;display:block}}input#pw{{padding-right:52px}}
.eye{{position:absolute;right:6px;top:50%;transform:translateY(-50%);width:40px;height:40px;border:0;border-radius:10px;background:transparent;color:var(--muted);cursor:pointer;display:grid;place-items:center;padding:0}}
.eye:hover{{color:var(--ink);background:var(--soft)}}.eye svg{{width:22px;height:22px}}.eye[aria-pressed="true"] .sl{{display:none}}
.err{{color:var(--seal);font-size:14px;min-height:21px;margin:0}}
</style>
</head>
<body>
<main class="box">
  <div class="logo"><span>knocky</span>{seal}</div>
  <p>Сайт в разработке. Введите пароль, чтобы посмотреть.</p>
  <form id="f" autocomplete="on">
    <input type="text" name="username" value="knocky" autocomplete="username" hidden>
    <span class="pw"><input id="pw" type="password" autocomplete="current-password" placeholder="Пароль" required autofocus><button type="button" class="eye" id="eye" aria-label="Показать пароль" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="3" fill="currentColor"/><path class="sl" d="M4 4l16 16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button></span>
    <label class="rm"><input type="checkbox" id="rm" checked>Запомнить на этом устройстве</label>
    <button id="go" type="submit">Войти</button>
    <p class="err" id="err" role="alert"></p>
  </form>
</main>
<script>
(()=>{{
const P={payload};
const b=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
const KEY='knocky-key';
document.getElementById('eye').onclick=e=>{{const p=document.getElementById('pw'),on=p.type==='password';p.type=on?'text':'password';e.currentTarget.setAttribute('aria-pressed',on);e.currentTarget.setAttribute('aria-label',on?'Скрыть пароль':'Показать пароль');p.focus();}};
async function derive(pw){{const base=await crypto.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
  for(const w of P.k){{const wk=await crypto.subtle.deriveKey({{name:'PBKDF2',salt:b(w.s),iterations:P.n,hash:'SHA-256'}},base,{{name:'AES-GCM',length:256}},false,['decrypt']);
    try{{const raw=await crypto.subtle.decrypt({{name:'AES-GCM',iv:b(w.i)}},wk,b(w.w));return crypto.subtle.importKey('raw',raw,'AES-GCM',true,['decrypt']);}}catch(_){{}}}}
  throw new Error('bad');}}
async function open_(key){{const pt=await crypto.subtle.decrypt({{name:'AES-GCM',iv:b(P.i)}},key,b(P.c));
  const html=new TextDecoder().decode(pt);document.open();document.write(html);document.close();}}
(async()=>{{try{{const raw=localStorage.getItem(KEY);if(raw){{const k=await crypto.subtle.importKey('raw',b(raw),'AES-GCM',true,['decrypt']);await open_(k);}}}}catch(e){{try{{localStorage.removeItem(KEY)}}catch(_){{}}}}}})();
document.getElementById('f').addEventListener('submit',async e=>{{e.preventDefault();
  if(!window.crypto||!crypto.subtle){{if(location.protocol==='http:'){{location.replace('https://'+location.host+location.pathname+location.search+location.hash);return;}}document.getElementById('err').textContent='Браузер не поддерживает защищённый вход. Откройте сайт по https://';return;}}
  const btn=document.getElementById('go'),err=document.getElementById('err');btn.disabled=true;btn.textContent='Проверяем…';err.textContent='';
  try{{const k=await derive(document.getElementById('pw').value);
    if(document.getElementById('rm').checked){{try{{const raw=new Uint8Array(await crypto.subtle.exportKey('raw',k));localStorage.setItem(KEY,btoa(String.fromCharCode(...raw)));}}catch(_){{}}}}
    await open_(k);}}
  catch(x){{try{{localStorage.removeItem(KEY)}}catch(_){{}};err.textContent='Неверный пароль';btn.disabled=false;btn.textContent='Войти';document.getElementById('pw').select();}}}});
}})();
</script>
</body>
</html>
'''
open(out, 'w', encoding='utf-8').write(page)
print('ok', len(page))
