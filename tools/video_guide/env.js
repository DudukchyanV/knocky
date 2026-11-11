// shared: mobile page with knocky.ru served from the repo
const {chromium}=require('playwright');const fs=require('fs');const R='/home/claude/knocky';
async function open(url,opts={}){const b=await chromium.launch({args:['--lang=ru-RU'],env:{...process.env,LANG:'ru_RU.UTF-8',LANGUAGE:'ru'}});const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true,locale:'ru-RU'});
await ctx.addInitScript(()=>{try{localStorage.setItem('kn_cookie','all');localStorage.setItem('ck','all')}catch(e){}});
await ctx.route('https://knocky.ru/**',r=>{let u=new URL(r.request().url()).pathname;let f;
 if(u.startsWith('/assets/'))f=R+'/server/app/static'+u;else if(u==='/'||u==='/index.html')f=R+'/index.html';else f=R+u+(u.endsWith('/')?'index.html':'');
 try{r.fulfill({body:fs.readFileSync(f),contentType:f.endsWith('.html')?'text/html':f.endsWith('.webp')?'image/webp':f.endsWith('.css')?'text/css':f.endsWith('.js')?'text/javascript':undefined})}catch(e){r.fulfill({status:404,body:''})}});
await ctx.route('https://fonts.googleapis.com/**',r=>r.fulfill({contentType:'text/css',body:fs.readFileSync(R+'/server/app/static/assets/fonts.css','utf8').replaceAll("url('/assets/","url('https://knocky.ru/assets/")}));
await ctx.route(/fonts\.gstatic|mc\.yandex|yandex\.ru\/an|core-renderer-tiles|tiles\.api-maps|dadata/,r=>r.abort().catch(()=>{}));
await ctx.route('https://app.knocky.ru/**',r=>{const f=R+'/server/app/static'+new URL(r.request().url()).pathname;r.fulfill({path:f}).catch(()=>r.abort().catch(()=>{}))});
const p=await ctx.newPage();p.on('pageerror',e=>console.log('PAGEERR',e.message));await p.goto(url);await p.waitForTimeout(1500);return {b,p};}
module.exports={open};
