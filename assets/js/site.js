/* ===========================================================================
   Willamette Web Design — first-party JS

   Loaded with `defer`, so it never blocks parsing or first paint. Everything
   here is progressive enhancement: with this file removed the page still
   renders, reads, navigates and submits correctly.

   Budget matters. TBT is 30% of the Lighthouse score, so this stays small and
   does no work during load beyond attaching a few passive listeners.

   Never declare `top`, `self`, `parent`, `name`, `status`, `length` or
   `origin` at top level — they collide with window globals and the whole
   script throws silently.
   =========================================================================== */

(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* -----------------------------------------------------------------------
     Scroll reveal

     IntersectionObserver rather than a scroll handler: the browser does the
     intersection maths off the main thread, and each element is unobserved
     the moment it lands, so the work is strictly finite.
     ----------------------------------------------------------------------- */
  var revealTargets = document.querySelectorAll('[data-reveal]');

  if (!('IntersectionObserver' in window) || reduced) {
    // No observer, or the visitor asked for no motion: show everything now.
    for (var i = 0; i < revealTargets.length; i++) {
      revealTargets[i].classList.add('is-in');
    }
  } else {
    var io = new IntersectionObserver(function (entries) {
      for (var j = 0; j < entries.length; j++) {
        if (entries[j].isIntersecting) {
          entries[j].target.classList.add('is-in');
          io.unobserve(entries[j].target);
        }
      }
    }, {
      // Start the reveal slightly before the element reaches the viewport so
      // it is already settling by the time it is properly in view.
      rootMargin: '0px 0px -12% 0px',
      threshold: 0.05
    });

    for (var k = 0; k < revealTargets.length; k++) io.observe(revealTargets[k]);

    // Anything already on screen at load should not animate in — it was
    // never "revealed", it was just there.
    requestAnimationFrame(function () {
      for (var n = 0; n < revealTargets.length; n++) {
        var rect = revealTargets[n].getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.9) {
          revealTargets[n].classList.add('is-in');
          io.unobserve(revealTargets[n]);
        }
      }
    });
  }

  /* -----------------------------------------------------------------------
     Sticky header state

     Driven by an IntersectionObserver on a zero-height sentinel rather than a
     scroll listener, so there is no per-frame work and no forced reflow.
     ----------------------------------------------------------------------- */
  var header = document.querySelector('[data-header]');
  if (header && 'IntersectionObserver' in window) {
    var sentinel = document.createElement('div');
    sentinel.setAttribute('aria-hidden', 'true');
    sentinel.style.cssText = 'position:absolute;top:0;left:0;width:1px;height:1px;pointer-events:none';
    document.body.insertBefore(sentinel, document.body.firstChild);

    new IntersectionObserver(function (entries) {
      header.classList.toggle('is-stuck', !entries[0].isIntersecting);
    }, { threshold: 0 }).observe(sentinel);
  }

  /* -----------------------------------------------------------------------
     Mobile drawer
     ----------------------------------------------------------------------- */
  var drawer = document.querySelector('[data-drawer]');
  var toggle = document.querySelector('[data-drawer-toggle]');

  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle('is-open', open);
    if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    // Keep the panel out of the tab order and the accessibility tree while shut.
    drawer.toggleAttribute('inert', !open);
  }

  if (drawer && toggle) {
    setDrawer(false);

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      setDrawer(!drawer.classList.contains('is-open'));
    });

    // Any link inside closes it, including the language switch.
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a')) setDrawer(false);
    });

    document.addEventListener('click', function (e) {
      if (!drawer.contains(e.target) && !toggle.contains(e.target)) setDrawer(false);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
        setDrawer(false);
        toggle.focus();
      }
    });
  }

  /* -----------------------------------------------------------------------
     Free-audit form

     Submits to Netlify Forms: Netlify detects the form in the deployed HTML
     and captures POSTs to "/" rather than routing them. That means a real
     backend with no server to run — but it only works on a Netlify deploy, so
     locally the request will fail and the error path below is what you see.

     The error path matters as much as the success path: a visitor who filled
     the form is a warm lead, so a failure hands them the phone number rather
     than a dead end.
     ----------------------------------------------------------------------- */
  var form = document.querySelector('[data-audit-form]');
  var success = document.querySelector('[data-audit-success]');
  var status = document.querySelector('[data-audit-status]');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // Honeypot: a real person never fills a field they cannot see. Bail
      // silently so a bot learns nothing from the response.
      if (form.company && form.company.value) return;

      var button = form.querySelector('button[type="submit"]');
      var sending = form.getAttribute('data-sending-label') || 'Sending…';

      if (button) {
        button.setAttribute('aria-disabled', 'true');
        button.dataset.label = button.textContent;
        button.textContent = sending;
      }
      if (status) {
        status.hidden = false;
        status.textContent = sending;
      }

      // Netlify Forms expects urlencoded, not multipart.
      var body = new URLSearchParams();
      new FormData(form).forEach(function (v, k) { body.append(k, v); });

      fetch(form.getAttribute('action') || '/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString()
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        form.reset();
        if (success) {
          form.hidden = true;
          success.hidden = false;
        } else if (status) {
          status.textContent = form.getAttribute('data-success-label') || 'Thank you.';
        }
      }).catch(function (err) {
        console.error('[willamette] audit form submission failed:', err);
        if (button) {
          button.removeAttribute('aria-disabled');
          if (button.dataset.label) button.textContent = button.dataset.label;
        }
        if (status) {
          status.hidden = false;
          status.textContent = form.getAttribute('data-error-label') ||
            'Something went wrong. Please call (541) 497-9531.';
        }
      });
    });
  }

  /* -----------------------------------------------------------------------
     FAQ accordion — opening one closes the others.

     Keeps the section scannable instead of letting it grow into a wall, and
     means the answer you just opened is the one on screen.
     ----------------------------------------------------------------------- */
  var faqs = document.querySelectorAll('.faq-item');
  for (var f = 0; f < faqs.length; f++) {
    faqs[f].addEventListener('toggle', function () {
      if (!this.open) return;
      for (var g = 0; g < faqs.length; g++) {
        if (faqs[g] !== this) faqs[g].open = false;
      }
    });
  }

  /* -----------------------------------------------------------------------
     Footer year — so the copyright never silently goes stale.
     ----------------------------------------------------------------------- */
  var years = document.querySelectorAll('[data-year]');
  for (var y = 0; y < years.length; y++) {
    years[y].textContent = String(new Date().getFullYear());
  }
})();
