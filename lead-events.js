/* Misura solo i clic sui pulsanti contrassegnati, se Analytics e gia attivo con consenso. */
(function(){'use strict';document.addEventListener('click',function(ev){
 var a=ev.target.closest('a[data-lead-channel]');if(!a)return;
 if(typeof window.gtag!=='function'||!window.__grimaldiAnalyticsLoaded)return;
 window.gtag('event','lead_contact_click',{contact_channel:a.getAttribute('data-lead-channel'),legal_area:a.getAttribute('data-lead-area'),page_path:location.pathname});
});})();
