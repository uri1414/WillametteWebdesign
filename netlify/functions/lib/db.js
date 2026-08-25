// Shared helpers for the application functions.
//
// This file lives in a subfolder so Netlify does NOT treat it as an endpoint;
// only top-level .js files in netlify/functions/ become functions.
//
// DELIBERATELY ZERO DEPENDENCIES. The referral backend on the predecessor site
// used @supabase/supabase-js, which meant the deploy had to install and bundle
// a package for what is, underneath, two HTTPS calls to PostgREST. Netlify
// config and function bundling cannot be tested from the agent sandbox
// (CLAUDE.md), so the fewer moving parts between a filled-in form and a stored
// row, the better. Node 18+ has global fetch; that is all this needs.

const SUPABASE_URL = (process.env.SUPABASE_URL || '').replace(/\/$/, '');
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

const SITE_ORIGIN = 'https://willametteweb.com';

// Scope CORS to our own origin instead of "*". The application form is served
// from the same origin as these functions (in production and on Netlify deploy
// previews), so same-origin requests are unaffected; this only blocks
// cross-site scripted calls, which is the abuse vector for a public endpoint.
const CORS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': SITE_ORIGIN,
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

function json(statusCode, body) {
  return { statusCode, headers: CORS, body: JSON.stringify(body) };
}

/** 303 so the browser re-issues the request as a GET (the no-JS success path). */
function redirect(location) {
  return { statusCode: 303, headers: { Location: location }, body: '' };
}

const configured = () => Boolean(SUPABASE_URL && SERVICE_KEY);

/**
 * One call to Supabase's REST API (PostgREST). Returns the parsed rows.
 * Throws with the database's own message on a non-2xx so the caller can log
 * something specific rather than "it failed".
 */
async function rest(path, { method = 'POST', body, prefer = 'return=representation' } = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    method,
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      'Content-Type': 'application/json',
      Prefer: prefer,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  const text = await res.text();
  let parsed = null;
  try { parsed = text ? JSON.parse(text) : null; } catch { /* non-JSON error body */ }

  if (!res.ok) {
    const err = new Error((parsed && (parsed.message || parsed.hint)) || text || `HTTP ${res.status}`);
    err.status = res.status;
    err.code = parsed && parsed.code;
    throw err;
  }
  return parsed;
}

/* --------------------------------------------------------------- input hygiene */

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

const isEmail = (v) => typeof v === 'string' && v.length <= 254 && EMAIL_RE.test(v);
const isUuid = (v) => typeof v === 'string' && UUID_RE.test(v);

// A US number, however the visitor chose to type it. Digits are what matters.
const isPhone = (v) => typeof v === 'string' && v.replace(/\D/g, '').length >= 10;

/** Trim, cap length, coerce to string. Returns '' for anything missing. */
function clean(v, max = 200) {
  return (typeof v === 'string' ? v : '').trim().slice(0, max);
}

/** '' -> null, so an empty optional field is NULL in the database, not ''. */
const orNull = (v) => (v ? v : null);

/** Checkbox groups arrive as an array (JSON) or repeated keys (form post). */
function cleanList(v, max = 12) {
  const list = Array.isArray(v) ? v : typeof v === 'string' && v ? [v] : [];
  return list.map((item) => clean(item, 60)).filter(Boolean).slice(0, max);
}

/** Parse either a JSON body (fetch) or a urlencoded one (no-JS form post). */
function parseBody(event) {
  const type = (event.headers['content-type'] || event.headers['Content-Type'] || '').toLowerCase();
  const raw = event.isBase64Encoded
    ? Buffer.from(event.body || '', 'base64').toString('utf8')
    : (event.body || '');

  if (type.includes('application/json')) {
    return { fields: JSON.parse(raw || '{}'), isFormPost: false };
  }

  // Repeated keys (checkbox groups) collapse into an array rather than
  // silently keeping only the last value.
  const params = new URLSearchParams(raw);
  const fields = {};
  for (const [k, v] of params.entries()) {
    if (k in fields) fields[k] = [].concat(fields[k], v);
    else fields[k] = v;
  }
  return { fields, isFormPost: true };
}

/* ------------------------------------------------------------ backup capture */

/**
 * Best-effort mirror into Netlify Forms.
 *
 * Supabase is the source of truth. This is the safety net: Netlify Forms gives
 * an email notification and a dashboard copy, so if the database is
 * misconfigured or down, the lead is still captured and somebody is still told.
 * It NEVER fails the request — a mirror that breaks the real submission would
 * be worse than no mirror at all.
 *
 * Requires the hidden detection form on /apply/ (Netlify only accepts a
 * submission for a form it found in the deployed HTML).
 */
async function mirrorToNetlifyForms(fields) {
  const base = (process.env.URL || process.env.DEPLOY_PRIME_URL || '').replace(/\/$/, '');
  if (!base || process.env.APPLICATION_FORMS_MIRROR === 'off') return false;

  const body = new URLSearchParams();
  body.append('form-name', 'application');
  for (const [k, v] of Object.entries(fields)) {
    if (v === null || v === undefined || v === '') continue;
    body.append(k, Array.isArray(v) ? v.join(', ') : String(v));
  }

  try {
    const res = await fetch(`${base}/apply/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export {
  CORS, SITE_ORIGIN,
  json, redirect, rest, configured,
  isEmail, isPhone, isUuid, clean, cleanList, orNull, parseBody,
  mirrorToNetlifyForms,
};
