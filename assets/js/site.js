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

     The form posts to a real endpoint. Until one is configured it must not
     pretend to succeed — a fake success screen loses the lead silently, which
     is worse than an honest error.
     ----------------------------------------------------------------------- */
  var form = document.querySelector('[data-audit-form]');
  var success = document.querySelector('[data-audit-success]');

  if (form) {
    form.addEventListener('submit', function (e) {
      var endpoint = form.getAttribute('action');

      if (!endpoint) {
        // No backend wired yet. Let the browser do nothing and say so loudly
        // in the console rather than showing a success state that is a lie.
        e.preventDefault();
        console.error(
          '[willamette] The audit form has no action endpoint, so this submission ' +
          'went nowhere. Wire it up (see docs/LAUNCH-CHECKLIST.md, Gate 5) before launch.'
        );
        return;
      }

      e.preventDefault();
      var button = form.querySelector('button[type="submit"]');
      if (button) {
        button.setAttribute('aria-disabled', 'true');
        button.dataset.label = button.textContent;
        button.textContent = form.getAttribute('data-sending-label') || 'Sending…';
      }

      fetch(endpoint, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      }).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        if (success) {
          form.hidden = true;
          success.hidden = false;
          success.setAttribute('role', 'status');
          success.focus && success.focus();
        }
      }).catch(function (err) {
        console.error('[willamette] audit form submission failed:', err);
        if (button) {
          button.removeAttribute('aria-disabled');
          if (button.dataset.label) button.textContent = button.dataset.label;
        }
        var msg = form.querySelector('[data-audit-error]');
        if (msg) msg.hidden = false;
      });
    });
  }
})();
