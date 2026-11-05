-- Studio Legale Grimaldi: chat con invio pubblico tramite RPC e lettura riservata.
create extension if not exists pgcrypto;
create table if not exists public.chat_conversations (
 id uuid primary key default gen_random_uuid(),
 created_at timestamptz not null default now(),
 status text not null default 'open' check (status in ('open','closed'))
);
create table if not exists public.chat_messages (
 id uuid primary key default gen_random_uuid(),
 conversation_id uuid not null references public.chat_conversations(id) on delete cascade,
 sender text not null check (sender in ('visitor','studio')),
 content text not null check (char_length(trim(content)) between 1 and 2000),
 created_at timestamptz not null default now()
);
create index if not exists chat_messages_conversation_time_idx on public.chat_messages(conversation_id,created_at);
create table if not exists public.chat_admins (user_id uuid primary key references auth.users(id) on delete cascade);
alter table public.chat_conversations enable row level security;
alter table public.chat_messages enable row level security;
alter table public.chat_admins enable row level security;
revoke all on public.chat_conversations,public.chat_messages,public.chat_admins from anon,authenticated;
grant select on public.chat_conversations,public.chat_messages to authenticated;
grant insert on public.chat_messages to authenticated;
create or replace function public.is_chat_admin() returns boolean
language sql stable security definer set search_path = '' as $$
 select auth.uid() is not null
 and (auth.jwt()->>'aal') = 'aal2'
 and exists (select 1 from public.chat_admins a where a.user_id = auth.uid());
$$;
revoke all on function public.is_chat_admin() from public;
grant execute on function public.is_chat_admin() to authenticated;
drop policy if exists chat_admin_read_conversations on public.chat_conversations;
create policy chat_admin_read_conversations on public.chat_conversations for select to authenticated using (public.is_chat_admin());
drop policy if exists chat_admin_read_messages on public.chat_messages;
create policy chat_admin_read_messages on public.chat_messages for select to authenticated using (public.is_chat_admin());
drop policy if exists chat_admin_reply on public.chat_messages;
create policy chat_admin_reply on public.chat_messages for insert to authenticated with check (public.is_chat_admin() and sender='studio');
create or replace function public.submit_chat_message(message_text text) returns void
language plpgsql security definer set search_path = '' as $$
declare conversation_id uuid;
begin
 if message_text is null or char_length(btrim(message_text)) < 1 or char_length(message_text) > 2000 then
  raise exception 'Invalid message';
 end if;
 insert into public.chat_conversations(status) values ('open') returning id into conversation_id;
 insert into public.chat_messages(conversation_id,sender,content) values (conversation_id,'visitor',message_text);
end;
$$;
revoke all on function public.submit_chat_message(text) from public;
grant execute on function public.submit_chat_message(text) to anon,authenticated;
-- DOPO l'esecuzione, aggiungere l'utente amministratore tramite UID di Authentication > Users:
-- insert into public.chat_admins(user_id) values ('UID-DEL-TUO-UTENTE') on conflict do nothing;
