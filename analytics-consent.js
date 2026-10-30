(function(){
  'use strict';
  var KEY='grimaldi_analytics_consent_v1', ID='G-S1JWDLSMRC';
  function choice(){try{return localStorage.getItem(KEY);}catch(e){return null;}}
  function store(v){try{localStorage.setItem(KEY,v);}catch(e){}}
  function analytics(){
    if(window.__grimaldiAnalyticsLoaded)return;
    window.__grimaldiAnalyticsLoaded=true;
    window.dataLayer=window.dataLayer||[];
    window.gtag=function(){window.dataLayer.push(arguments);};
    window.gtag('js',new Date());window.gtag('config',ID,{anonymize_ip:true});
    var s=document.createElement('script');s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(ID);
    document.head.appendChild(s);
  }
  function apply(v){store(v);document.getElementById('grimaldi-cookie-banner').hidden=true;
    if(v==='yes')analytics();
    else if(window.__grimaldiAnalyticsLoaded){window.location.reload();}
  }
  function show(){document.getElementById('grimaldi-cookie-banner').hidden=false;}
  function init(){
    var b=document.createElement('div');b.id='grimaldi-cookie-banner';b.hidden=true;
    b.setAttribute('role','region');b.setAttribute('aria-label','Preferenze statistiche');
    b.style.cssText='position:fixed;z-index:9999;bottom:12px;left:12px;right:12px;max-width:680px;margin:auto;background:#123d32;color:#fff;border:1px solid #d6b76b;border-radius:12px;padding:17px;box-shadow:0 4px 20px #0005;font:15px/1.5 Arial,sans-serif';
    b.innerHTML='<button type="button" id="grimaldi-close" aria-label="Chiudi senza accettare" style="float:right;background:transparent;border:1px solid #fff;color:#fff;border-radius:4px;cursor:pointer;font-size:20px;line-height:1;padding:2px 8px">×</button><strong style="color:#e5c67a">Preferenze privacy</strong><p style="margin:8px 0">Utilizziamo Google Analytics solo se accetti le statistiche. Puoi rifiutare e modificare la scelta in qualsiasi momento. <a href="/privacy.html" style="color:#e5c67a;text-decoration:underline">Informativa privacy</a>.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><button type="button" id="grimaldi-reject" style="padding:9px 14px;cursor:pointer">Rifiuta</button><button type="button" id="grimaldi-accept" style="padding:9px 14px;background:#e5c67a;color:#123d32;border:0;border-radius:4px;cursor:pointer">Accetta statistiche</button></div>';
    document.body.appendChild(b);
    document.getElementById('grimaldi-close').addEventListener('click',function(){apply('no');});
    document.getElementById('grimaldi-reject').addEventListener('click',function(){apply('no');});
    document.getElementById('grimaldi-accept').addEventListener('click',function(){apply('yes');});
    var foot=document.querySelector('footer')||document.body;
    var p=document.createElement('p');p.style.cssText='margin:10px 0;font-size:13px';
    var a=document.createElement('a');a.href='#';a.textContent='Modifica preferenze statistiche';
    a.addEventListener('click',function(e){e.preventDefault();show();});p.appendChild(a);foot.appendChild(p);
    if(choice()==='yes')analytics();else if(choice()!=='no')show();
    document.querySelectorAll('[data-privacy-settings]').forEach(function(el){el.addEventListener('click',function(e){e.preventDefault();show();});});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
