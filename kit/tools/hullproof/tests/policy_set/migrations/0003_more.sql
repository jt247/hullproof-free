alter table public.profiles add column is_verified boolean default false;
alter table public.orders enable row level security;
create policy "orders_read" on public.orders for select to authenticated using (true);
