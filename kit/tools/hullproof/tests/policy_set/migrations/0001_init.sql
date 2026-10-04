-- synthetic migration, no real data
create table public.profiles (
  id uuid primary key,
  email text,
  display_name text,
  role text default 'member',
  plan text default 'free',
  constraint profiles_email_len check (length(email) < 300)
);
alter table public.profiles enable row level security;

create policy "profiles_select" on public.profiles for select to authenticated using (true);
create policy "profiles_update" on public.profiles for update to authenticated using (auth.uid() = id);

create table public.notes (
  id uuid primary key,
  user_id uuid not null,
  body text
);
alter table public.notes enable row level security;
create policy "notes_all" on public.notes for all using (auth.uid() = user_id);
create policy "old_policy" on public.notes for select to authenticated using (true);

create table public.orders (
  id uuid primary key,
  status text,
  stripe_customer_id text
);

create table public.accounts (
  id uuid primary key,
  display_name text,
  credits integer default 0
);
alter table public.accounts enable row level security;
revoke update on public.accounts from authenticated, anon;
grant update (display_name) on public.accounts to authenticated;
create policy "accounts_update" on public.accounts for update to authenticated
  using (auth.uid() = id) with check (auth.uid() = id);

create policy "meta_admin" on public.notes for select to authenticated
  using ((auth.jwt() -> 'user_metadata' ->> 'role') = 'admin');

/* block comment; with a semicolon */
create function public.get_secret() returns text language sql security definer as $$
  select 'x'; -- semicolon inside body must not split the statement
$$;

create function public.admin_tool(target uuid) returns void language plpgsql
  security definer set search_path = public as $fn$
begin
  update public.profiles set role = 'admin' where id = target;
end;
$fn$;

create function public.grant_credits(target uuid, amount int) returns void language plpgsql
  security definer as $$ begin null; end; $$;
revoke execute on function public.grant_credits(uuid, int) from public, anon;
grant execute on function public.grant_credits(uuid, int) to authenticated;
