// ═══════════════════════════════════════
//  JOB CARD RENDERER
//  Fetches from backend and renders cards
// ═══════════════════════════════════════

async function loadJobs(role = '', location = 'India') {
  const container = document.getElementById('jobsGrid');
  if (!container) return;

  container.innerHTML = '<div style="color:var(--muted);font-size:14px;padding:20px;">Loading jobs…</div>';

  try {
    const data = await window.API.jobs.list(role, location);
    const jobs = data.jobs || [];

    if (jobs.length === 0) {
      container.innerHTML = '<div style="color:var(--muted);font-size:14px;padding:20px;">No jobs found. Try a different role.</div>';
      return;
    }

    container.innerHTML = jobs.map(job => `
      <div class="feature-card" style="--accent-color:var(--gold)">
        <div class="fc-icon">${job.icon || '🏢'}</div>
        <div class="fc-eyebrow">${job.location || 'India'} · ${job.type || 'Full Time'}</div>
        <div class="fc-title">${job.title}</div>
        <div class="fc-desc">${job.salary || ''} · ${job.experience || ''} · ${(job.skills || []).join(', ')}</div>
        ${job.url ? `<a href="${job.url}" target="_blank" class="fc-link">View Job →</a>` : ''}
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = '<div style="color:var(--muted);font-size:14px;padding:20px;">Could not load jobs. Backend may be offline.</div>';
  }
}

// Render static featured jobs on page load (no API needed for demo)
// Dynamic jobs loaded via loadJobs() when user searches
