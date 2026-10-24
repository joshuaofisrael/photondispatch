(function(){var p=document.querySelector('.progress');if(!p||matchMedia('(prefers-reduced-motion:reduce)').matches)return;
function u(){var h=document.documentElement,m=h.scrollHeight-h.clientHeight;p.style.width=(m>0?h.scrollTop/m*100:0)+'%'}
addEventListener('scroll',u,{passive:true});u()})();

(function(){var f=document.getElementById('cf'),t=document.getElementById('thanks');if(!f)return;
function ok(){f.hidden=true;t.hidden=false;t.focus()}
if(/[?&]sent=1/.test(location.search))ok();
f.addEventListener('submit',function(e){if(!window.fetch)return;e.preventDefault();var b=f.querySelector('button'),er=document.getElementById('cf-err');er.hidden=true;b.disabled=true;
fetch(f.dataset.ajax,{method:'POST',headers:{Accept:'application/json'},body:new FormData(f)}).then(function(r){return r.json()}).then(function(d){if(d&&(d.success===true||d.success==='true'))ok();else throw 0}).catch(function(){er.hidden=false;b.disabled=false})})})();
