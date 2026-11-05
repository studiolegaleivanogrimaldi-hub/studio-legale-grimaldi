-- Studio Legale Grimaldi - aggiornamento bidirezionale.
-- Eseguire una sola volta in Supabase SQL Editor, prima di pubblicare il nuovo sito.
create extension if not exists pgcrypto;
create table if not exists public.chat_visitor_access (
 conversation_id uuid primary key references public.chat_conversations(id) on delete cascade,
 token_hash bytea not null unique,
 created_at timestamptz not null default now()
);
alter table public.chat_visitor_access enable row level security;
revoke all on public.chat_visitor_access from anon, authenticated;
-- Evita che il vecchio endpoint permetta messaggi non collegati a una sessione.
revoke execute on function public.submit_chat_message(text) from anon, authenticated;

create or replace function public.chat_visitor_start(message_text text)
returns table(conversation_id uuid, access_token text)
language plpgsql security definer set search_path = '' as $$
declare new_id uuid; new_token text;
begin
 if message_text is null or char_length(btrim(message_text)) < 1 or char_length(message_text) > 2000 then
  raise exception 'Invalid message';
 end if;
 new_token := encode(extensions.gen_random_bytes(32),'hex');
 insert into public.chat_conversations(status) values ('open') returning id into new_id;
 insert into public.chat_visitor_access(conversation_id,token_hash)
 values (new_id, extensions.digest(new_token,'sha256'));
 insert into public.chat_messages(conversation_id,sender,content)
 values (new_id,'visitor',message_text);
 return query select new_id,new_token;
end; $$;

create or replace function public.chat_visitor_send(p_conversation_id uuid, p_access_token text, message_text text)
returns void language plpgsql security definer set search_path = '' as $$
declare last_sent timestamptz; sent_recent int;
begin
 if p_access_token is null or length(p_access_token) <> 64 or p_access_token !~ '^[0-9a-f]{64}$'
 or not exists(select 1 from public.chat_visitor_access a where a.conversation_id=p_conversation_id
 and a.token_hash=extensions.digest(p_access_token,'sha256')) then
  raise exception 'Access denied';
 end if;
 if message_text is null or char_length(btrim(message_text)) < 1 or char_length(message_text)>2000 then
  raise exception 'Invalid message';
 end if;
 if not exists(select 1 from public.chat_conversations c where c.id=p_conversation_id and c.status='open') then
  raise exception 'Conversation closed';
 end if;
 select count(*) into sent_recent from public.chat_messages m
 where m.conversation_id=p_conversation_id and m.sender='visitor' and m.created_at>now()-interval '1 minute';
 if sent_recent>=5 then raise exception 'Too many messages; try later'; end if;
 insert into public.chat_messages(conversation_id,sender,content)
 values (p_conversation_id,'visitor',message_text);
end; $$;

create or replace function public.chat_visitor_read(p_conversation_id uuid, p_access_token text)
returns table(sender text, content text, created_at timestamptz)
language plpgsql security definer set search_path = '' as $$
begin
 if p_access_token is null or length(p_access_token) <> 64 or p_access_token !~ '^[0-9a-f]{64}$'
 or not exists(select 1 from public.chat_visitor_access a where a.conversation_id=p_conversation_id
 and a.token_hash=extensions.digest(p_access_token,'sha256')) then
  raise exception 'Access denied';
 end if;
 return query select m.sender,m.content,m.created_at from public.chat_messages m
 where m.conversation_id=p_conversation_id order by m.created_at asc limit 500;
end; $$;

revoke all on function public.chat_visitor_start(text) from public;
revoke all on function public.chat_visitor_send(uuid,text,text) from public;
revoke all on function public.chat_visitor_read(uuid,text) from public;
grant execute on function public.chat_visitor_start(text) to anon, authenticated;
grant execute on function public.chat_visitor_send(uuid,text,text) to anon, authenticated;
grant execute on function public.chat_visitor_read(uuid,text) to anon, authenticated;
