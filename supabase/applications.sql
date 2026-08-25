-- ============================================================================
-- Willamette Web Design — 30-Day Program applications
-- Run this in the Supabase SQL Editor (Database -> SQL Editor -> New query).
--
-- This runs in the SAME Supabase project as the referral program
-- (referrers / referrals / rewards, created by the Baseline Studio
-- supabase/schema.sql). It is purely additive: it creates one new table and
-- touches nothing that already exists. One database, one source of truth.
-- ============================================================================
--
-- SECURITY MODEL — identical to the referral tables, deliberately.
--   RLS is ON with NO policies, so the anon/public key can read and write
--   NOTHING. Every write happens in a Netlify Function using the SERVICE ROLE
--   key, which bypasses RLS. The browser never holds a key that can touch this
--   table. See docs/APPLICATION-SETUP.md.
--
-- THE PROGRESSIVE RECORD — the point of this table.
--   Step 1 of the application INSERTs a row with status = 'partial'. Steps 2-4
--   UPDATE that same row to status = 'complete'. A half-finished application is
--   therefore one row with the contact details filled in, not a lost lead and
--   not a second messy record.
--
-- APPLICANT -> CLIENT is a status change, not a re-entry. The lifecycle lives
-- in this one row: partial -> complete -> contacted -> call_booked -> won/lost.
-- ============================================================================

create table if not exists public.applications (
  id                  uuid primary key default gen_random_uuid(),

  -- Step 1 — make contact. Captured before anything else, so a drop-off here
  -- is still someone we can call.
  name                text not null,
  business_name       text not null,
  email               text,
  phone               text,

  -- Step 2 — current presence.
  industry            text,
  service_area        text,
  website_url         text,
  has_gbp             text,          -- 'yes' | 'no' | 'unsure'
  platforms           text[],        -- e.g. {facebook,instagram,yelp}
  biggest_problem     text,

  -- Step 3 — goals.
  primary_service     text,
  target_customer     text,
  typical_job_value   text,          -- free text: people answer "$300-500", not a number
  primary_goal        text,

  -- Step 4 — finish.
  preferred_language  text,          -- 'en' | 'es'
  notes               text,

  -- Provenance. `source` distinguishes this from the free presence check, so
  -- lead origin stays trackable; `referral_code` ties an application back to a
  -- referrer when someone arrived through /refer/?ref=CODE.
  source              text not null default 'application',
  page_language       text,          -- which language the form was filled in
  referral_code       text,

  status              text not null default 'partial'
                        check (status in ('partial','complete','contacted',
                                          'call_booked','won','lost')),

  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  completed_at        timestamptz,

  -- At least one way to reach them. Step 1 enforces this in the UI and in the
  -- function; this is the backstop that makes an unreachable lead impossible.
  constraint applications_reachable check (
    coalesce(nullif(trim(email), ''), nullif(trim(phone), '')) is not null
  )
);

-- Reporting: "what came in this week", "what is still partial", "who to call".
create index if not exists idx_applications_status  on public.applications(status);
create index if not exists idx_applications_created on public.applications(created_at desc);
create index if not exists idx_applications_email   on public.applications(lower(email));

-- Keep updated_at honest without the function having to remember to set it.
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_applications_touch on public.applications;
create trigger trg_applications_touch
  before update on public.applications
  for each row execute function public.touch_updated_at();

-- Closed to the browser by default. That is the point.
alter table public.applications enable row level security;

-- ---------------------------------------------------------------------------
-- Day-to-day queries (run these in the SQL editor)
-- ---------------------------------------------------------------------------
--   -- Everyone who needs a call, newest first:
--   select created_at, name, business_name, phone, email, status
--     from public.applications
--    where status in ('partial','complete')
--    order by created_at desc;
--
--   -- Someone abandoned after step 1 — still a reachable lead:
--   select * from public.applications where status = 'partial';
--
--   -- Move one along the pipeline:
--   update public.applications set status = 'contacted' where id = '<uuid>';
