create schema if not exists auth;
create table auth.users (id uuid primary key);
create table public.profiles (id uuid primary key references auth.users(id), name text);
create table public.organizations (id uuid primary key, name text);
create table public.memberships (org_id uuid references public.organizations(id), user_id uuid references auth.users(id), role text);
create table public.projects (id uuid primary key, organization_id uuid references public.organizations(id), title text);
create table public.notes (id uuid primary key, owner uuid references auth.users(id), body text);
create table public.subscriptions (id uuid primary key, user_id uuid, stripe_customer_id text, plan text);
create table public.credits (user_id uuid, balance int);
