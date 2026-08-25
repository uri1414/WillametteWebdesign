// POST /.netlify/functions/application-start
//
// Step 1 of the 30-Day Program application: name, business, and a way to reach
// them. Inserts ONE row with status = 'partial' and hands the id back, so the
// remaining steps fill in that same row (see application-complete.js).
//
// This is the decision the whole flow turns on: somebody who fills in step 1
// and then closes the tab is already a lead we can call. Nothing about the
// rest of the form is allowed to get in the way of storing that.
//
// Two request shapes, one endpoint:
//   • JSON  {name, business_name, email, phone, ...}  -> {ok, id}   (the JS path)
//   • urlencoded form post of the whole 4-step form   -> 303 redirect
//     (the no-JS path: the <form action> points here, so the application still
//     works with JavaScript switched off — it just posts in one go.)

import {
  json, redirect, rest, configured,
  isEmail, isPhone, clean, cleanList, orNull, parseBody,
  mirrorToNetlifyForms,
} from './lib/db.js';

const THANKS = { en: '/apply/thank-you/', es: '/es/apply/thank-you/' };
const APPLY = { en: '/apply/', es: '/es/apply/' };

/** Fields collected in steps 2-4. Only present on the no-JS single post. */
function laterSteps(f) {
  return {
    industry: orNull(clean(f.industry, 120)),
    service_area: orNull(clean(f.service_area, 120)),
    website_url: orNull(clean(f.website_url, 300)),
    has_gbp: ['yes', 'no', 'unsure'].includes(clean(f.has_gbp, 10)) ? clean(f.has_gbp, 10) : null,
    platforms: cleanList(f.platforms),
    biggest_problem: orNull(clean(f.biggest_problem, 1500)),
    primary_service: orNull(clean(f.primary_service, 200)),
    target_customer: orNull(clean(f.target_customer, 300)),
    typical_job_value: orNull(clean(f.typical_job_value, 60)),
    primary_goal: orNull(clean(f.primary_goal, 300)),
    preferred_language: ['en', 'es'].includes(clean(f.preferred_language, 2)) ? clean(f.preferred_language, 2) : null,
    notes: orNull(clean(f.notes, 2000)),
  };
}

export const handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return json(204, {});
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' });

  let fields, isFormPost;
  try { ({ fields, isFormPost } = parseBody(event)); }
  catch { return json(400, { error: 'Invalid request.' }); }

  const lang = clean(fields.page_language, 2) === 'es' ? 'es' : 'en';

  // Everything arrives at once on two paths: the no-JS form post, and the JS
  // fallback where step 1 never reached the database and the browser re-sends
  // the whole application at the end. Both produce a finished row.
  const complete = isFormPost || fields.finish === true || fields.finish === 'true';

  // Honeypot: a real person never fills a field they cannot see. Bail with a
  // success-shaped response so a bot learns nothing from the difference.
  if (clean(fields.company, 100)) {
    return isFormPost ? redirect(THANKS[lang]) : json(200, { ok: true, id: null });
  }

  const name = clean(fields.name, 120);
  const business_name = clean(fields.business_name, 160);
  const email = clean(fields.email, 254).toLowerCase();
  const phone = clean(fields.phone, 40);

  const problems = [];
  if (!name) problems.push('name');
  if (!business_name) problems.push('business_name');
  if (!email && !phone) problems.push('contact');
  if (email && !isEmail(email)) problems.push('email');
  if (phone && !isPhone(phone)) problems.push('phone');

  if (problems.length) {
    if (isFormPost) return redirect(`${APPLY[lang]}?error=invalid`);
    return json(400, {
      error: lang === 'es'
        ? 'Necesitamos tu nombre, el nombre de tu negocio y un teléfono o correo válido.'
        : 'We need your name, your business name, and a valid phone number or email.',
      fields: problems,
    });
  }

  const row = {
    name,
    business_name,
    email: orNull(email),
    phone: orNull(phone),
    source: 'application',
    page_language: lang,
    referral_code: orNull(clean(fields.referral_code, 32).toUpperCase()),
    // The no-JS path arrives with everything at once, so it is complete on
    // submission. The JS path stores the contact details and nothing else yet.
    status: complete ? 'complete' : 'partial',
    ...(complete ? laterSteps(fields) : {}),
    ...(complete ? { completed_at: new Date().toISOString() } : {}),
  };

  // Backup capture first-class: the mirror is what produces an email alert and
  // a Netlify dashboard copy. It never blocks or fails the submission.
  const mirror = mirrorToNetlifyForms({
    stage: row.status, name, business_name, email, phone,
    page_language: lang,
    ...(complete ? laterSteps(fields) : {}),
  });

  if (!configured()) {
    console.error('[willamette] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set.');
    const captured = await mirror;
    if (captured) return isFormPost ? redirect(THANKS[lang]) : json(200, { ok: true, id: null, stored: 'backup' });
    return json(500, { error: 'Server not configured.' });
  }

  try {
    const [saved] = await rest('applications', { body: row });
    await mirror;
    return isFormPost ? redirect(THANKS[lang]) : json(200, { ok: true, id: saved.id });
  } catch (e) {
    console.error('[willamette] application insert failed:', e.message);
    // The database refused it, but the lead is not allowed to evaporate: if the
    // backup captured it, this is still a success from the applicant's side.
    const captured = await mirror;
    if (captured) return isFormPost ? redirect(THANKS[lang]) : json(200, { ok: true, id: null, stored: 'backup' });
    return json(500, {
      error: lang === 'es'
        ? 'No pudimos guardar tu solicitud. Llámanos al (541) 497-9531 y lo hacemos por teléfono.'
        : "We couldn't save your application. Please call (541) 497-9531 and we'll take it over the phone.",
    });
  }
};
