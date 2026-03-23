// ═══════════════════════════════════════
//  LEARNING JOURNEY COMPONENT
//  AI-guided adaptive path based on quiz scores
//  Resources: YouTube + Coursera recommendations
// ═══════════════════════════════════════

(function () {

  // ── State ────────────────────────────
  let currentPath = null;
  const quizScores = {}; // { domain: score }

  const DOMAINS = [
    { key: 'React / Frontend' },
    { key: 'Node.js / Backend' },
    { key: 'System Design' },
    { key: 'DevOps / Cloud' },
    { key: 'Machine Learning' },
    { key: 'DSA' },
    { key: 'Python' },
    { key: 'Databases / SQL' },
  ];

  const RESOURCE_ICONS = {
    youtube:  '',
    coursera: '',
    article:  '',
    practice: '',
  };

  const PRIORITY_LABELS = {
    critical: 'CRITICAL',
    high:     'HIGH',
    medium:   'POLISH',
  };

  // ── DOM Injection ────────────────────
  function injectUI() {
    const careerSection = document.getElementById('career');
    if (!careerSection) return;

    const container = careerSection.querySelector('.section-wrap');
    if (!container) return;

    const html = `
<!-- ══ LEARNING JOURNEY ══ -->
<div class="lj-setup reveal" id="ljSetup" style="margin-top:64px;">
  <div class="lj-setup-title">Your AI Learning Journey</div>
  <div class="lj-setup-sub">
    Tell us your target role and share your quiz scores — Groq AI will build a personalized,
    prioritized learning path with real YouTube and Coursera resources curated just for you.
  </div>

  <div class="lj-form-row">
    <div class="lj-field">
      <label>Target Role</label>
      <input class="lj-input" id="ljRole" placeholder="e.g. Senior Full Stack Developer" />
    </div>
    <div class="lj-field">
      <label>Hours available per week</label>
      <select class="lj-select" id="ljHours">
        <option value="5">5 hrs / week</option>
        <option value="10" selected>10 hrs / week</option>
        <option value="15">15 hrs / week</option>
        <option value="20">20+ hrs / week</option>
      </select>
    </div>
  </div>

  <div class="lj-scores-label">Add quiz scores (optional — AI adapts if you do)</div>
  <div class="lj-score-chips" id="ljScoreChips">
    ${DOMAINS.map(d => `
      <div class="lj-score-chip" data-domain="${d.key}" onclick="ljToggleDomain(this)">
        <span>${d.key}</span>
        <span class="chip-score" id="chip-score-${d.key.replace(/\s+/g,'-')}">—</span>
      </div>
    `).join('')}
  </div>

  <div class="lj-score-slider-wrap" id="ljSliderWrap">
    <label class="lj-scores-label" id="ljSliderLabel">Score for —</label>
    <input type="range" class="lj-slider" id="ljSlider" min="0" max="100" value="60"
      oninput="ljUpdateSlider(this.value)" onchange="ljSaveScore(this.value)" />
    <div class="lj-slider-labels"><span>0%</span><span>50%</span><span>100%</span></div>
  </div>

  <button class="lj-generate-btn" id="ljGenerateBtn" onclick="ljGenerate()" style="margin-top:28px;">
    <div class="spinner"></div>
    <span class="btn-label">Generate My Learning Path</span>
  </button>
</div>

<!-- ══ PATH DISPLAY ══ -->
<div class="lj-path" id="ljPath">
  <div class="lj-path-header" id="ljPathHeader"></div>
  <div class="lj-motive" id="ljMotive"></div>
  <div class="lj-modules" id="ljModules"></div>
  <div class="lj-adapt-banner" id="ljAdaptBanner">
    You've added a new quiz score — want to re-adapt your path?
    <button onclick="ljAdapt()">Re-adapt now</button>
  </div>
</div>
`;
    container.insertAdjacentHTML('beforeend', html);

    // Register reveals
    document.querySelectorAll('.lj-setup.reveal').forEach(el => {
      if (window.revObs) window.revObs.observe(el);
    });
  }

  // ── Domain chip toggle ───────────────
  window.ljToggleDomain = function (chip) {
    const domain = chip.dataset.domain;
    const allChips = document.querySelectorAll('.lj-score-chip');
    const sliderWrap = document.getElementById('ljSliderWrap');
    const sliderLabel = document.getElementById('ljSliderLabel');
    const slider = document.getElementById('ljSlider');

    // Deselect all, select clicked
    allChips.forEach(c => c.classList.remove('active'));
    chip.classList.add('active');

    sliderLabel.textContent = `Your score for: ${domain}`;
    slider.value = quizScores[domain] ?? 60;
    sliderWrap.classList.add('visible');
    window._activeDomain = domain;
    ljUpdateSlider(slider.value);
  };

  window.ljUpdateSlider = function (val) {
    const label = document.getElementById('ljSliderLabel');
    const domain = window._activeDomain;
    if (!domain) return;
    label.textContent = `Your score for: ${domain} — ${val}%`;

    // Update chip display immediately
    const safeKey = domain.replace(/\s+/g, '-');
    const chipScore = document.getElementById(`chip-score-${safeKey}`);
    if (chipScore) chipScore.textContent = val + '%';
  };

  window.ljSaveScore = function (val) {
    const domain = window._activeDomain;
    if (!domain) return;
    quizScores[domain] = parseInt(val);
    // Remember which domain was last saved so ljAdapt uses the right one
    window._lastSavedDomain = domain;

    // If path already exists, show adapt banner
    if (currentPath) {
      document.getElementById('ljAdaptBanner').classList.add('visible');
    }
  };

  // ── Generate path ────────────────────
  window.ljGenerate = async function () {
    const role = document.getElementById('ljRole').value.trim();
    if (!role) {
      showToast('Please enter your target role', 'warn');
      document.getElementById('ljRole').focus();
      return;
    }

    const btn = document.getElementById('ljGenerateBtn');
    btn.classList.add('loading');
    btn.disabled = true;

    const scores = Object.entries(quizScores).map(([domain, score]) => ({
      domain, score, difficulty: 'medium'
    }));

    try {
      const data = await window.API.learn.generate({
        target_role: role,
        quiz_scores: scores,
        weekly_hours: parseInt(document.getElementById('ljHours').value),
      });

      currentPath = data;
      renderPath(data);
      document.getElementById('ljPath').classList.add('visible');
      document.getElementById('ljPath').scrollIntoView({ behavior: 'smooth', block: 'start' });
      showToast('Learning path generated!', 'success');

    } catch (err) {
      showToast('Could not generate path — is the backend running?', 'error');
      console.error(err);
    }

    btn.classList.remove('loading');
    btn.disabled = false;
  };

  // ── Adapt path ───────────────────────
  window.ljAdapt = async function () {
    if (!currentPath) return;
    const banner = document.getElementById('ljAdaptBanner');
    banner.innerHTML = '<span>⏳ Re-adapting your path…</span>';

    // Use the domain that was most recently saved, not just selected
    const lastDomain = window._lastSavedDomain || window._activeDomain;
    const score = quizScores[lastDomain] ?? 60;

    try {
      const data = await window.API.learn.adapt({
        current_path: currentPath,
        new_quiz: { domain: lastDomain, score, difficulty: 'medium' },
      });
      currentPath = data;
      renderPath(data);
      banner.classList.remove('visible');
      showToast('Path adapted to your new score!', 'success');
    } catch (err) {
      banner.innerHTML = '⚡ Re-adapt failed. <button onclick="ljAdapt()">Retry</button>';
      console.error(err);
    }
  };

  // ── Render path ──────────────────────
  function renderPath(path) {
    // Header
    const header = document.getElementById('ljPathHeader');
    const pct = path.overall_readiness;
    const circumference = 188;
    const dashOffset = circumference - (circumference * pct / 100);

    header.innerHTML = `
      <div class="lj-readiness">
        <div class="lj-readiness-ring">
          <svg width="72" height="72" viewBox="0 0 72 72">
            <circle class="ring-bg" cx="36" cy="36" r="30"/>
            <circle class="ring-fill" id="ljRingFill" cx="36" cy="36" r="30"
              style="stroke-dashoffset:${circumference}"/>
          </svg>
          <div class="ring-text">${pct}%</div>
        </div>
        <div class="lj-readiness-info">
          <div class="lj-readiness-label">Overall Readiness</div>
          <div class="lj-readiness-role">${path.target_role}</div>
          <div class="lj-readiness-weeks">~${path.total_weeks} weeks to job-ready ${path.adapted_from_scores ? '· <span style="color:var(--teal)">Adapted from your scores</span>' : ''}</div>
        </div>
      </div>
      <div class="lj-next-action">
        <div class="lj-next-action-label">Next Action</div>
        <div class="lj-next-action-text">${path.next_action}</div>
      </div>
    `;

    // Animate ring
    setTimeout(() => {
      const fill = document.getElementById('ljRingFill');
      if (fill) fill.style.strokeDashoffset = dashOffset;
    }, 100);

    // Motivational note
    document.getElementById('ljMotive').textContent = `"${path.motivational_note}"`;

    // Modules
    const container = document.getElementById('ljModules');
    container.innerHTML = path.modules.map((mod, i) => renderModule(mod, i)).join('');

    // Animate score bars
    setTimeout(() => {
      document.querySelectorAll('.lj-score-fill').forEach(bar => {
        bar.style.width = bar.dataset.w;
      });
    }, 200);
  }

  function renderModule(mod, index) {
    const priorityClass = `priority-${mod.priority}`;
    const resources = (mod.resources || []).map(renderResource).join('');

    return `
<div class="lj-module ${priorityClass}" id="lj-mod-${index}">
  <div class="lj-module-header" onclick="ljToggleModule(${index})">
    <div class="lj-module-priority-dot"></div>
    <div class="lj-module-info">
      <div class="lj-module-domain">${PRIORITY_LABELS[mod.priority] || mod.priority} · ${mod.domain}</div>
      <div class="lj-module-title">${mod.title}</div>
      <div class="lj-module-why">${mod.why_this_now}</div>
    </div>
    <div class="lj-module-meta">
      <div class="lj-score-bar-wrap">
        <div class="lj-score-bar-label">
          <span>Score</span><span>${mod.current_score}% → ${mod.target_score}%</span>
        </div>
        <div class="lj-score-track">
          <div class="lj-score-fill" data-w="${mod.current_score}%" style="width:0%"></div>
        </div>
      </div>
      <div class="lj-weeks-badge">${mod.estimated_weeks}w</div>
    </div>
    <div class="lj-expand-icon">[+]</div>
  </div>
  <div class="lj-module-body">
    <div class="lj-module-body-inner">
      <div class="lj-milestone">Milestone: ${mod.milestone}</div>
      <div class="lj-resources-title">Recommended Resources</div>
      <div class="lj-resources-list">${resources}</div>
    </div>
  </div>
</div>
`;
  }

  function renderResource(res) {
    const typeClass = `type-${res.type}`;
    const icon = RESOURCE_ICONS[res.type] || '';
    const safeUrl = res.url && res.url.startsWith('http') ? res.url : '#';

    return `
<a class="lj-resource ${typeClass}" href="${safeUrl}" target="_blank" rel="noopener">
  <div class="lj-resource-icon">${icon}</div>
  <div class="lj-resource-info">
    <div class="lj-resource-title">${res.title}</div>
    <div class="lj-resource-why">${res.why}</div>
    <div class="lj-resource-meta">
      <span class="lj-resource-tag">${res.type.toUpperCase()}</span>
      <span class="lj-resource-tag">${res.duration}</span>
      <span class="lj-resource-tag">${res.difficulty}</span>
    </div>
  </div>
  <div class="lj-resource-arrow">>></div>
</a>
`;
  }

  // ── Module expand/collapse ───────────
  window.ljToggleModule = function (index) {
    const mod = document.getElementById(`lj-mod-${index}`);
    if (!mod) return;
    const wasExpanded = mod.classList.contains('expanded');

    // Close all
    document.querySelectorAll('.lj-module.expanded').forEach(m => m.classList.remove('expanded'));

    // Open clicked if it wasn't open
    if (!wasExpanded) mod.classList.add('expanded');
  };

  // ── Init ─────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectUI);
  } else {
    injectUI();
  }

})();
