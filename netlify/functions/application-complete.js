// POST /.netlify/functions/application-complete
//
// Steps 2-4 of the application. UPDATEs the row that step 1 created — the same
// row, filled in progressively — and moves it to status = 'complete'.
//
// Body: { id, ...step2, ...step3, ...step4 }
//
// The id is the row's uuid, which the browser got back from application-start.
// It is unguessable, and the update is deliberately narrow:
//   • only ever writes the step 2-4 columns, never name/business/contact, so a
//     replayed request cannot overwrite the details we already have;
//   • only matches rows still in 'partial' or 'complete', so an application
//     that has moved down the pipeline (contacted, won) can never be rewritten
//     by a stale browser tab;
//   • `status` is set here, never taken from the request body.

import {
  json, rest, configured, isUuid, clean, cleanList, orNull, parseBody,
  mirrorToNetlifyForms,
} from './lib/db.js';

export const handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') return json(204, {});
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed' });

  let fields;
  try { ({ fields } = parseBody(event)); }
  catch { return json(400, { error: 'Invalid request.' }); }

  const lang = clean(fields.page_language, 2) === 'es' ? 'es' : 'en';
  if (clean(fields.company, 100)) return json(200, { ok: true }); // honeypot

  const id = clean(fields.id, 36);
  if (!isUuid(id)) return json(400, { error: 'Missing application id.' });

  const patch = {
    industry: orNull(clean(fields.industry, 120)),
    service_area: orNull(clean(fields.service_area, 120)),
    website_url: orNull(clean(fields.website_url, 300)),
    has_gbp: ['yes', 'no', 'unsure'].includes(clean(fields.has_gbp, 10)) ? clean(fields.has_gbp, 10) : null,
    platforms: cleanList(fields.platforms),
    biggest_problem: orNull(clean(fields.biggest_problem, 1500)),
    primary_service: orNull(clean(fields.primary_service, 200)),
    target_customer: orNull(clean(fields.target_customer, 300)),
    typical_job_value: orNull(clean(fields.typical_job_value, 60)),
    primary_goal: orNull(clean(fields.primary_goal, 300)),
    preferred_language: ['en', 'es'].includes(clean(fields.preferred_language, 2))
      ? clean(fields.preferred_language, 2)
      : lang,
    notes: orNull(clean(fields.notes, 2000)),
    status: 'complete',
    completed_at: new Date().toISOString(),
  };

  const mirror = mirrorToNetlifyForms({ stage: 'complete', application_id: id, page_language: lang, ...patch });

  if (!configured()) {
    console.error('[willamette] SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY are not set.');
    const captured = await mirror;
    return captured ? json(200, { ok: true, stored: 'backup' }) : json(500, { error: 'Server not configured.' });
  }

  try {
    const rows = await rest(
      `applications?id=eq.${encodeURIComponent(id)}&status=in.(partial,complete)`,
      { method: 'PATCH', body: patch }
    );
    await mirror;

    if (!rows || rows.length === 0) {
      // No row matched: the id is stale or the application has already moved on.
      // The answers were still mirrored, so nothing the applicant typed is lost.
      console.warn('[willamette] application-complete matched no row for id', id);
      return json(200, { ok: true, stored: 'backup' });
    }
    return json(200, { ok: true });
  } catch (e) {
    console.error('[willamette] application update failed:', e.message);
    const captured = await mirror;
    if (captured) return json(200, { ok: true, stored: 'backup' });
    return json(500, {
      error: lang === 'es'
        ? 'No pudimos guardar el resto de tu solicitud. Ya tenemos tus datos de contacto y te llamaremos.'
        : "We couldn't save the rest of your answers — but we have your contact details and we'll be in touch.",
    });
  }
};
