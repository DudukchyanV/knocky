// stop-motion recorder: every shot is a JPEG + how many video frames it is held + optional tap mark
const fs=require('fs');
function rec(p,dir){fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});const man=[];let n=0,scene='';
 const R={scene(s){scene=s},
  async shot(hold=1,tap=null){const f=String(++n).padStart(5,'0')+'.jpg';await p.screenshot({path:dir+'/'+f,type:'jpeg',quality:92});man.push({f,hold,tap,scene});},
  async hold(fr){if(man.length)man[man.length-1].hold+=fr;},
  async box(sel){const b=await (typeof sel==='string'?p.$(sel):sel).then?await (typeof sel==='string'?p.$(sel):sel):sel;const bb=await b.boundingBox();return {x:bb.x+bb.width/2,y:bb.y+bb.height/2,el:b};},
  async tap(sel,after=8){const {x,y,el}=await R.box(sel);await R.shot(7,{x,y});await el.click();await p.waitForTimeout(450);await R.shot(after);},
  async scroll(js,from,to,frames){for(let i=1;i<=frames;i++){const t=i/frames,e=t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;await p.evaluate(([js,v])=>{(new Function('v',js))(v)},[js,from+(to-from)*e]);await R.shot(1);}},
  async type(sel,text,per=2){await p.fill(sel,'');for(const ch of text){await p.type(sel,ch);await R.shot(per);}},
  save(){fs.writeFileSync(dir+'/manifest.json',JSON.stringify(man));}};
 return R;}
module.exports={rec};
