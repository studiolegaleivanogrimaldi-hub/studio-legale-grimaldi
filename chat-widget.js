import {createClient} from 'https://esm.sh/@supabase/supabase-js@2';
const db=createClient('https://abiqaqjgotdjgrjdptqg.supabase.co','sb_publishable_voDrdOQ7R-bXOF-Ylo1u0g_JZvUxVis',{auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false}});
const get=id=>document.getElementById(id), toggle=get('slg-chat-toggle'),panel=get('slg-chat-panel'),form=get('slg-chat-form'),status=get('slg-chat-status');
toggle.addEventListener('click',()=>{panel.hidden=!panel.hidden;toggle.setAttribute('aria-expanded',String(!panel.hidden))});
form.addEventListener('submit',async e=>{e.preventDefault();const content=get('slg-chat-text').value.trim();if(!content||content.length>2000||!get('slg-chat-consent').checked)return;const send=get('slg-chat-send');send.disabled=true;status.textContent='Invio in corso…';try{
// Requires server-side RLS policies allowing only safe anonymous INSERTs; never expose admin privileges.
const {data:c,error:ce}=await db.from('chat_conversations').insert({status:'open'}).select('id').single();if(ce||!c?.id)throw ce||Error('conversation');
const {error:me}=await db.from('chat_messages').insert({conversation_id:c.id,sender:'visitor',content});if(me)throw me;
form.reset();status.textContent='Messaggio inviato. Lo studio potrà leggerlo nel pannello riservato.';
}catch(err){console.warn('Chat non disponibile:',err?.code||'connection');status.textContent='Non è stato possibile inviare il messaggio. Usa i contatti indicati sul sito.'}finally{send.disabled=false}});
