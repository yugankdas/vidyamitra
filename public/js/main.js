// ═══════════════════════════════════════
//  VIDYAMITRA — MAIN ENTRY POINT
//  Bootstraps all components after DOM is ready.
//  Loaded last in index.html after all other scripts.
// ═══════════════════════════════════════

(function () {
  function init() {
    // Restore auth token from sessionStorage so window.API sends it
    const token = sessionStorage.getItem('vm_token');
    if (token && window.API) {
      window.API.setAuthToken(token);
    }

    // Wire marquee card clicks to chat input (deduplicates marquee.js logic)
    document.querySelectorAll('.marquee-card').forEach(card => {
      card.addEventListener('click', () => {
        const cmd  = card.querySelector('.mcard-cmd')?.textContent || '';
        const text = card.querySelector('.mcard-text')?.textContent || '';
        const input = document.getElementById('chatInput');
        if (input && typeof window.injectPrompt === 'function') {
          window.injectPrompt(`${cmd} — ${text}`);
        }
      });
    });

    console.log('[VidyaMitra] Initialised ✓');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
