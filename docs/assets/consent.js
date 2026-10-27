(function(){var K='mtm-analytics-consent',ID='G-RSKRTQEZNW',loaded=false;
function load(){if(loaded)return;loaded=true;gtag('consent','update',{analytics_storage:'granted'});var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.appendChild(s);gtag('js',new Date());gtag('config',ID,{anonymize_ip:true});}
function clearGa(){document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();if(n.indexOf('_ga')===0){['',';domain=.'+location.hostname,';domain='+location.hostname].forEach(function(d){document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/'+d;});}});}
function close(){var b=document.getElementById('mtm-consent');if(b)b.remove();}
function show(){if(document.getElementById('mtm-consent'))return;var b=document.createElement('div');b.id='mtm-consent';b.setAttribute('role','dialog');b.setAttribute('aria-live','polite');b.setAttribute('aria-label','Cookie consent');
b.innerHTML='<p>We use Google Analytics cookies to understand how readers use PhotonDispatch, only if you agree. <a href="/privacy.html">Privacy policy</a></p><div><button type="button" class="rej">Decline</button> <button type="button" class="acc">Accept</button></div>';
b.style.cssText='position:fixed;left:12px;right:12px;bottom:12px;z-index:9999;max-width:640px;margin:0 auto;background:#111827;color:#f9fafb;padding:14px 16px;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.3);font:15px/1.45 system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between';
b.querySelector('p').style.margin='0';b.querySelector('a').style.color='#93c5fd';
[].forEach.call(b.querySelectorAll('button'),function(x){x.style.cssText='font:inherit;padding:7px 14px;border-radius:6px;cursor:pointer;border:1px solid #9ca3af;background:'+(x.className==='acc'?'#2563eb;color:#fff;border-color:#2563eb':'transparent;color:#f9fafb');});
b.querySelector('.acc').onclick=function(){try{localStorage.setItem(K,'granted')}catch(e){}close();load();};
b.querySelector('.rej').onclick=function(){try{localStorage.setItem(K,'denied')}catch(e){}gtag('consent','update',{analytics_storage:'denied'});clearGa();close();};
document.body.appendChild(b);b.querySelector('.acc').focus({preventScroll:true});}
var v=null;try{v=localStorage.getItem(K)}catch(e){}
if(v==='granted')load();else if(v!=='denied')show();
document.addEventListener('click',function(e){var t=e.target.closest&&e.target.closest('[data-consent-open]');if(t){e.preventDefault();show();}});
})();
