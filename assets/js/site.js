/* ===========================================================================
   Willamette Web Design — first-party JS

   Load this with `defer` only:
       <script src="/assets/js/site.js" defer></script>

   Keep it small. JavaScript on the main thread during load is what drives TBT,
   and TBT is 30% of the Lighthouse score (handbook §2.6). Anything that isn't
   needed for the first paint should wait for interaction or idle.

   Rules that matter here:
   - Never read layout immediately after writing the DOM — that's a forced
     reflow. Batch reads inside requestAnimationFrame.
   - Coalesce scroll/resize bursts with a ticking flag (pattern below).
   - Never declare `top`, `self`, `parent`, `name`, `status`, `length`, or
     `origin` at top level: they collide with window globals and the whole
     script throws silently.
   =========================================================================== */

(function () {
  'use strict';

  /**
   * rAF-batched scroll/resize handling. Register work with onFrame(fn); it runs
   * at most once per animation frame no matter how fast events fire.
   */
  var callbacks = [];
  var ticking = false;

  function flush() {
    ticking = false;
    for (var i = 0; i < callbacks.length; i++) callbacks[i]();
  }

  function schedule() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(flush);
  }

  window.wwdOnFrame = function (fn) {
    callbacks.push(fn);
    schedule();
  };

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
})();
