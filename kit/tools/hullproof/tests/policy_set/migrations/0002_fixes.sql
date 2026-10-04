drop policy if exists "old_policy" on public.notes;
drop policy "notes_all" on public.notes;
create policy "notes_owner_select" on public.notes for select to authenticated using (auth.uid() = user_id);
create policy "notes_owner_update" on public.notes for update to authenticated using (auth.uid() = user_id);
alter policy "notes_owner_update" on public.notes with check (auth.uid() = user_id);

create or replace function public.get_secret() returns text language sql security definer
  set search_path = '' as $$ select 'y' $$;
revoke execute on function public.get_secret() from public;
revoke execute on function public.get_secret() from anon;

alter function public.grant_credits(uuid, int) set search_path = public;
drop policy "meta_admin" on public.notes;

create table public.scratch (id int);
drop table public.scratch;
