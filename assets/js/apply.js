/* ===========================================================================
   Willamette Web Design — 30-Day Program application

   Loaded with `defer` on /apply/ and /es/apply/ only.

   PROGRESSIVE ENHANCEMENT, AND THE ORDER MATTERS
   Without this file the page is one long form that posts to
   /.netlify/functions/application-start and works end to end. Everything here
   is layered on top:

     • one step on screen at a time, with a "Step 2 of 4" indicator
     • step 1 is submitted on its own, the moment it is filled in, creating the
       row with status = 'partial'
     • the remaining steps UPDATE that same row via application-complete

   That first point is the whole design. Someone who fills in their name and
   number and then closes the tab has already reached us — the rest of the form
   is detail we can collect on the phone. A form that only stores anything at
   the very end throws those people away silently.

   The id of the row lives in sessionStorage, so a reload mid-application
   continues the same record instead of starting a second one.

   Never declare `top`, `self`, `parent`, `name`, `status`, `length` or
   `origin` at top level — they collide with window globals and the whole
   script throws silently.
   =========================================================================== */

(function () {
  'use strict';

  var form = document.querySelector('[data-apply-form]');
  if (!form) return;

  var steps = Array.prototype.slice.call(form.querySelectorAll('[data-apply-step]'));
  if (steps.length < 2) return;

  var progressLabel = document.querySelector('[data-apply-progress-label]');
  var segments = Array.prototype.slice.call(document.querySelectorAll('[data-apply-seg]'));
  var statusEl = form.querySelector('[data-apply-status]');
  var submitBtn = form.querySelector('.apply-submit');

  var STORAGE_KEY = 'wwd-application-id';
  var START = form.getAttribute('data-apply-start');
  var COMPLETE = form.getAttribute('data-apply-complete');
  var THANKS = form.getAttribute('data-apply-thanks') || '/apply/thank-you/';
  var LANG = form.getAttribute('data-apply-lang') || 'en';
  var LABEL_TPL = (progressLabel && progressLabel.getAttribute('data-apply-label')) || 'Step {n} of {total}';

  var MSG = {
    required: form.getAttribute('data-required-label') || '',
    contact: form.getAttribute('data-contact-label') || '',
    invalid: form.getAttribute('data-invalid-label') || '',
    sending: form.getAttribute('data-sending-label') || 'Sending…',
    error: form.getAttribute('data-error-label') || ''
  };

  var current = 0;
  var applicationId = null;
  try { applicationId = window.sessionStorage.getItem(STORAGE_KEY); } catch (e) { /* private mode */ }

  function remember(id) {
    applicationId = id || null;
    try {
      if (id) window.sessionStorage.setItem(STORAGE_KEY, id);
      else window.sessionStorage.removeItem(STORAGE_KEY);
    } catch (e) { /* private mode — the id still lives in this closure */ }
  }

  function track(event, params) {
    if (typeof window.gtag === 'function') window.gtag('event', event, params || {});
  }

  /* ------------------------------------------------------------- step display */

  function setStatus(text) {
    if (!statusEl) return;
    if (text) {
      statusEl.textContent = text;
      statusEl.hidden = false;
    } else {
      statusEl.textContent = '';
      statusEl.hidden = true;
    }
  }

  function show(index, moveFocus) {
    current = Math.max(0, Math.min(index, steps.length - 1));

    for (var i = 0; i < steps.length; i++) {
      // .is-later is the pre-script state; from here the hidden property is
      // what decides, so the class must go or the step could never come back.
      steps[i].classList.remove('is-later');
      steps[i].hidden = i !== current;
    }
    for (var s = 0; s < segments.length; s++) {
      segments[s].classList.toggle('is-done', s <= current);
    }
    if (progressLabel) {
      progressLabel.textContent = LABEL_TPL
        .replace('{n}', String(current + 1))
        .replace('{total}', String(steps.length));
    }
    setStatus('');

    if (moveFocus) {
      // Send focus to the step itself rather than its first input: a screen
      // reader then reads the legend ("Your business today") before the field,
      // which is the context that makes the field make sense.
      var legend = steps[current].querySelector('.apply-step__legend');
      var target = legend || steps[current];
      target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
      var box = steps[current].getBoundingClientRect();
      if (box.top < 0 || box.top > window.innerHeight * 0.4) {
        steps[current].scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  /* ---------------------------------------------------------------- validation */

  function controlsIn(step) {
    return Array.prototype.slice.call(step.querySelectorAll('input, textarea, select'));
  }

  function flag(control, invalid) {
    if (invalid) control.setAttribute('aria-invalid', 'true');
    else control.removeAttribute('aria-invalid');
  }

  function validate(step) {
    var controls = controlsIn(step);
    var firstBad = null;
    var message = '';

    for (var i = 0; i < controls.length; i++) {
      var c = controls[i];
      if (c.type === 'hidden') continue;
      var ok = c.checkValidity();
      flag(c, !ok);
      if (!ok && !firstBad) {
        firstBad = c;
        message = c.value ? MSG.invalid : MSG.required;
      }
    }

    // Step 1 only: an application with neither a phone number nor an email is
    // not a lead, it is a note to nobody. Enforced here and again in the
    // function, which is the one that actually protects the database.
    if (!firstBad && step === steps[0]) {
      var email = form.querySelector('[name="email"]');
      var phone = form.querySelector('[name="phone"]');
      if (email && phone && !email.value.trim() && !phone.value.trim()) {
        firstBad = email;
        message = MSG.contact;
        flag(email, true);
        flag(phone, true);
      }
    }

    if (firstBad) {
      setStatus(message);
      firstBad.focus();
      return false;
    }
    setStatus('');
    return true;
  }

  /* ------------------------------------------------------------- serialisation */

  function collect(scope) {
    var data = {};
    var controls = scope
      ? controlsIn(scope).concat(Array.prototype.slice.call(form.querySelectorAll('input[type="hidden"]')))
      : controlsIn(form);

    for (var i = 0; i < controls.length; i++) {
      var c = controls[i];
      if (!c.name) continue;
      if (c.type === 'checkbox') {
        if (!c.checked) continue;
        if (!data[c.name]) data[c.name] = [];
        data[c.name].push(c.value);
      } else if (c.type === 'radio') {
        if (c.checked) data[c.name] = c.value;
      } else {
        data[c.name] = c.value;
      }
    }
    return data;
  }

  function post(url, payload) {
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (body) {
        if (!res.ok) throw new Error(body.error || ('HTTP ' + res.status));
        return body;
      });
    });
  }

  function busy(button, on) {
    if (!button) return;
    if (on) {
      button.setAttribute('aria-disabled', 'true');
      if (!button.dataset.label) button.dataset.label = button.textContent;
      button.textContent = MSG.sending;
    } else {
      button.removeAttribute('aria-disabled');
      if (button.dataset.label) button.textContent = button.dataset.label;
    }
  }

  /* -------------------------------------------------------------------- wiring */

  form.addEventListener('click', function (e) {
    var next = e.target.closest('[data-apply-next]');
    var back = e.target.closest('[data-apply-back]');
    if (!next && !back) return;
    e.preventDefault();

    if (back) { show(current - 1, true); return; }
    if (!validate(steps[current])) return;

    // Leaving step 1 is what creates the row. Everything after this point is
    // an update to it, so a drop-off costs the detail, never the lead.
    if (current === 0 && !applicationId) {
      busy(next, true);
      setStatus(MSG.sending);
      post(START, collect(steps[0]))
        .then(function (body) {
          remember(body.id);
          track('application_start', { language: LANG });
        })
        .catch(function (err) {
          // Deliberately non-blocking: the applicant is mid-flow and it is not
          // their problem. The final submit re-sends everything, so nothing is
          // lost as long as they finish; if they don't, the console and the
          // function logs say why.
          console.error('[willamette] could not save step 1:', err);
        })
        .then(function () {
          busy(next, false);
          show(current + 1, true);
        });
      return;
    }

    show(current + 1, true);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    // Honeypot: a real person never fills in a field they cannot see.
    if (form.company && form.company.value) { window.location.assign(THANKS); return; }

    if (!validate(steps[current])) return;

    busy(submitBtn, true);
    setStatus(MSG.sending);

    var payload = collect(null);
    var request;

    if (applicationId) {
      payload.id = applicationId;
      request = post(COMPLETE, payload);
    } else {
      // Step 1 never made it to the database (offline, a cold function, a
      // misconfigured key). Send the whole thing to the insert endpoint and
      // mark it finished, rather than telling the applicant to start over.
      payload.finish = true;
      request = post(START, payload);
    }

    request.then(function () {
      track('application_complete', { language: LANG });
      remember(null);
      window.location.assign(THANKS);
    }).catch(function (err) {
      console.error('[willamette] application submission failed:', err);
      busy(submitBtn, false);
      setStatus((err && err.message) || MSG.error);
    });
  });

  // Someone arriving from a referral link (/refer/?ref=CODE) carries the code
  // through to their application, so the referral can be credited later.
  var refField = form.querySelector('[name="referral_code"]');
  if (refField) {
    var match = /[?&]ref=([^&#]+)/.exec(window.location.search);
    if (match) refField.value = decodeURIComponent(match[1]).slice(0, 32);
  }

  show(0, false);
})();
