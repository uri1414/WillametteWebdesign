# The 30-Day Program application — setup and operation

The application behind every "Apply for the 30-Day Program" button.

```
/apply/              /es/apply/              the 4-step application
/apply/thank-you/    /es/apply/thank-you/    confirmation (noindex)
```

It writes into the **same Supabase project** as the referral program. One
database, one source of truth: an applicant who signs on becomes a client by
changing a status on their existing row, not by being re-entered somewhere else.

---

## The two decisions, and what settled them

**1. A separate `applications` table, not the customer table.**
There is no customer table. The Supabase project currently holds `referrers`,
`referrals` and `rewards` (Baseline Studio's `supabase/schema.sql`) and nothing
else — the client portal at `/platform/` on the old site is a *marketing demo*
of a portal, not a running application with logins, uploads and a progress
tracker. So there was no existing record for an applicant to become.

`applications` is therefore built to carry the whole lifecycle itself:

```
partial → complete → contacted → call_booked → won → lost
```

When the real portal exists, it reads this row rather than replacing it: a
client is an application with `status = 'won'`, plus whatever project tables get
added alongside. Applicant → customer stays a status change.

**2. A Netlify Function with the service-role key, not a browser write.**
This matches how the platform already talks to Supabase. Every table has RLS on
with **no policies at all**, so the anon key can read and write nothing, and all
access happens server-side with the service-role key. Writing from the browser
would have meant opening the first anon-writable policy in the project — a
public `insert` and a public `update` on a table holding leads — for no gain.

The functions have **no npm dependencies**: they call Supabase's REST API with
the runtime's own `fetch`. Nothing has to install or bundle for a deploy to
produce working endpoints.

---

## The progressive record — the part worth understanding

Step 1 asks for a name, a business name, and a phone number or an email. The
moment that step is completed, the browser posts it and the row is inserted
with `status = 'partial'`.

Steps 2–4 **update that same row** and set `status = 'complete'`.

So someone who fills in step 1 and then closes the tab is not a lost lead and
not a duplicate record: they are one row, with contact details, waiting to be
called. That is the single most valuable thing this flow does. Everything else
is detail that can be collected on the phone.

The row's id lives in the browser's `sessionStorage`, so a reload mid-way
continues the same record instead of starting a second one.

```
POST /.netlify/functions/application-start      {name, business_name, email, phone}  ->  {id}
POST /.netlify/functions/application-complete   {id, ...steps 2-4}                   ->  {ok}
```

**With JavaScript off** the whole form is on one page and posts to
`application-start` as an ordinary form submission; the function stores a
complete row and 303s to the confirmation page. Nothing about the flow depends
on JavaScript running.

---

## Setup

### 1. Supabase (once)

1. Open the **same project** the referral program uses.
2. **SQL Editor → New query** → paste and run
   [`supabase/applications.sql`](../supabase/applications.sql). It is additive:
   it creates the `applications` table, its indexes, an `updated_at` trigger,
   and turns RLS on. It does not touch the referral tables.
3. **Project Settings → API** → copy the **Project URL** and the **service_role**
   key.

### 2. Netlify environment variables

**Site configuration → Environment variables** on the *willametteweb.com* site:

| Variable | Value |
|---|---|
| `SUPABASE_URL` | the project URL, e.g. `https://abcdefgh.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | the **service_role** key — tick **"Contains secret values"** |

These reach only the functions, never the browser. Never put the service-role
key in client code or commit it.

Optional:

| Variable | Effect |
|---|---|
| `APPLICATION_FORMS_MIRROR=off` | turns off the Netlify Forms backup described below |

### 3. Netlify Forms notifications (the email alert)

Supabase is the source of truth, but a database row does not tell anyone that a
lead arrived. Every submission is therefore **also** mirrored into Netlify
Forms under the form name `application`, which gives an email alert and a
dashboard copy — and catches the lead even if Supabase is misconfigured or down.

Netlify does not email you by default. After the first deploy:

**Netlify → Forms → `application` → Settings → Form notifications** → add an
email notification to info@willametteweb.com. Then submit a real test and
confirm it arrives. Until that is done, submissions are captured and nobody is
told, which looks exactly like a working setup.

Each applicant produces up to two notifications: one when step 1 lands
(`stage: partial`) and one when they finish (`stage: complete`). That is
deliberate — the partial one is the lead you would otherwise never hear about.

### 4. Deploy

Push the branch Netlify builds. No build command is needed; the functions carry
no dependencies. The endpoints are:

```
POST /.netlify/functions/application-start
POST /.netlify/functions/application-complete
```

---

## Booking the discovery call

The confirmation page can show a "Book a call" CTA. It is off until a real
calendar exists — `booking.url` is `null` in `site.config.json`, and the page
then promises only the reply within one business day.

**Recommended, given you already have Google Workspace:**

1. **Google Calendar appointment schedules** — built into Workspace, no new
   vendor, no extra cost, and it books straight onto the calendar you already
   live in, with a Google Meet link attached automatically. In Google Calendar:
   **Create → Appointment schedule**, set your availability and a 30-minute
   slot, then copy the public booking page link (`https://calendar.app.google/…`).
   Check what your plan includes — Business Starter allows a single booking
   page, the higher plans allow several plus payment collection through Stripe.
   Start here; it is the least machinery for exactly what you need.

2. **Cal.com** — free tier, two-way Google Calendar sync, more control over
   buffers, routing and multiple call types. Worth moving to if you outgrow one
   booking page or want the booking form to ask qualifying questions.

3. **Calendly** — the name most clients recognise. Free tier is one event type,
   connects to Google Calendar. Functionally similar to Cal.com; pick it if
   familiarity matters more than the free tier's limits.

Whichever you use, one thing matters more than the tool: the link on the
confirmation page must lead to a calendar you actually keep. A booking page
with no availability is worse than no booking page.

To turn it on:

```jsonc
// site.config.json
"booking": {
  "provider": "google-calendar",
  "url": "https://calendar.app.google/your-link"
}
```

```bash
python3 scripts/build-apply.py && npm run css && npm run preflight
```

The CTA then appears on both confirmation pages, in English and Spanish.

---

## Rebuilding the pages

The application pages are **generated**. Edit the source, never the HTML.

| To change | Edit |
|---|---|
| Any wording, in either language | `scripts/apply_content.py` |
| Which fields exist, or their order | `scripts/apply_content.py` (`STEPS`) |
| Page structure, schema, markup | `scripts/build-apply.py` |
| Styling | `assets/css/site.css` |
| Step behaviour, validation, submission | `assets/js/apply.js` |
| Booking link, endpoints, statuses | `site.config.json` |

```bash
python3 scripts/build-apply.py     # /apply/, /es/apply/ + both confirmation pages
npm run preflight                  # css sync -> sitemap -> audit
```

A field's `name` is a **database column**. Adding a field means adding a column
in `supabase/applications.sql`, allowing it in the function's field list, and
adding it to the hidden Netlify detection form (which `build-apply.py` generates
from `STEPS`, so that part is automatic). Never translate a `name` — the EN and
ES forms write to one table and must send the same shape.

---

## Testing after the first deploy

Do both. The second one is the whole point of the design.

**A completed application**

1. Open `https://willametteweb.com/apply/`, fill in all four steps, submit.
2. You land on `/apply/thank-you/`.
3. In Supabase: `select * from applications order by created_at desc limit 1;`
   — one row, `status = 'complete'`, `completed_at` set, every answer present.
4. An email notification arrives from Netlify Forms.

**An abandoned application**

1. Open `/apply/`, fill in step 1 only, press Continue, then **close the tab**.
2. In Supabase: the row exists with `status = 'partial'` and the contact details.
3. There is exactly **one** row for that person — not two.

**Also worth checking**

- The Spanish flow at `/es/apply/`, which must behave identically and store
  `page_language = 'es'`.
- JavaScript disabled: the whole form shows at once and still submits.
- A submission with neither an email nor a phone number is refused.

---

## Day to day

```sql
-- Who needs contacting, newest first
select created_at, name, business_name, phone, email, status, page_language
  from applications
 where status in ('partial','complete')
 order by created_at desc;

-- The ones who dropped off after step 1 — call these
select * from applications where status = 'partial';

-- Move someone along
update applications set status = 'contacted'   where id = '<uuid>';
update applications set status = 'call_booked' where id = '<uuid>';
update applications set status = 'won'         where id = '<uuid>';
```

`source` separates applications from other lead types, and `referral_code` is
filled in when someone reached the form through a referral link
(`/apply/?ref=CODE`), so a referral can be credited when they sign on.

---

## What this does not include

The client portal itself — logins, file uploads, the per-stage progress tracker
— does not exist as running software in any of these repositories. The
`/platform/` page on the Baseline Studio site is a static demo of that idea.

Nothing here blocks it: the applications table is where a client record starts,
and the portal, when it is built, can key off `applications.id`. But it is a
separate build, not a configuration step.
