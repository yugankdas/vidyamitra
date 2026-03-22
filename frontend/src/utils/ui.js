// ═══════════════════════════════════════
//  UI UTILITIES
//  scroll, reveal, counter, accordion, toasts
// ═══════════════════════════════════════

// ── Smooth scroll helper ────────────────
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Section nav active state with IntersectionObserver ──
const sectionObserverOptions = {
  root: null,
  rootMargin: '-100px 0px -40% 0px',
  threshold: 0
};

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      let pageId = entry.target.id.replace('page-', '');
      if (pageId === 'hero') pageId = 'home';
      highlightNavPill(pageId);
    }
  });
}, sectionObserverOptions);

function highlightNavPill(pageId) {
  document.querySelectorAll('.nav-pill').forEach(pill => {
    const dp = pill.getAttribute('data-page');
    const isActive = (dp === pageId);
    pill.classList.toggle('active', isActive);
    
    if (isActive) {
      pill.style.background = '#FFFFFF';
      pill.style.color = '#000000';
    } else {
      pill.style.background = '';
      pill.style.color = '';
    }
  });

  document.querySelectorAll('.mobile-menu-link').forEach(link => {
    const dp = link.getAttribute('data-page');
    link.classList.toggle('active', dp === pageId);
  });
}

// Observe all major section/page units
function initSectionObserver() {
  const ids = ['hero', 'agent', 'page-resume', 'page-interview', 'page-career', 'page-roadmap', 'page-jobs'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) sectionObserver.observe(el);
  });
}

// ── Profile Modal ───────────────────────
function openProfile() {
  const p = document.getElementById('profileOverlay');
  if (p) {
    p.classList.add('open');
    const userName = localStorage.getItem('vm_user') || sessionStorage.getItem('vm_user') || 'User';
    document.getElementById('profileName').textContent = userName;
    document.getElementById('profileAvatarBig').textContent = userName.charAt(0).toUpperCase();
    
    // Sync with real data tracked in ST (index.html)
    if (window.updateMetrics) window.updateMetrics();
    if (window.updateProgBars) window.updateProgBars();
    if (window.renderProfileBookmarks) window.renderProfileBookmarks();
  }
}

function closeProfile() {
  const p = document.getElementById('profileOverlay');
  if (p) p.classList.remove('open');
}

function updateProgBars() {
  // Progress bars are rendered dynamically based on quiz scores
  const bars = document.getElementById('progBars');
  if (!bars) return;
  const scores = window.ST?.scores || {};
  if (Object.keys(scores).length === 0) {
    bars.innerHTML = '<div style="font-size:13px;color:var(--muted)">Complete quizzes to see your domain mastery here.</div>';
    return;
  }
  let html = '';
  for (const [domain, score] of Object.entries(scores)) {
    html += `<div style="margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
        <span style="font-weight:600; color:var(--text)">${domain}</span>
        <span style="color:var(--muted)">${score}%</span>
      </div>
      <div style="height:6px; background:var(--border); border-radius:3px; overflow:hidden;">
        <div class="bar-animate" data-width="${score}%" style="height:100%; background:#000; border-radius:3px; width:0%; transition: width 1s ease;"></div>
      </div>
    </div>`;
  }
  bars.innerHTML = html;
}

// Initialise observer
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSectionObserver);
} else {
  initSectionObserver();
}

// Legacy scroll listener for nav background toggle
window.addEventListener('scroll', () => {
  const nav = document.getElementById('mainNav');
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 20);
});

// ── Reveal on scroll ────────────────────
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObs.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => revealObs.observe(el));

// ── Word reveal for hero title ───────────
setTimeout(() => {
  document.querySelectorAll('.hero-title .word').forEach((word, i) => {
    word.style.animation = `wordReveal 0.7s ${0.4 + i * 0.12}s cubic-bezier(0.16,1,0.3,1) forwards`;
  });
}, 100);

// ── Accordion ───────────────────────────
document.querySelectorAll('.acc-header').forEach(header => {
  header.addEventListener('click', () => {
    const item = header.closest('.acc-item');
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.acc-item.open').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// ── Quiz option click ───────────────────
document.querySelectorAll('.quiz-opt').forEach(opt => {
  opt.addEventListener('click', () => {
    opt.closest('.quiz-opts').querySelectorAll('.quiz-opt').forEach(o => o.classList.remove('sel'));
    opt.classList.add('sel');
  });
});

// ── Mode button toggle ──────────────────
document.querySelectorAll('.mmode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.mint-mode').querySelectorAll('.mmode-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  });
});

// ── Progress bar animation ──────────────
const progressObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('.bar-animate').forEach(bar => {
        if (bar.dataset.width) {
          setTimeout(() => bar.style.width = bar.dataset.width, 100);
        }
      });
    }
  });
}, { threshold: 0.3 });

setTimeout(() => {
  document.querySelectorAll('#progress .reveal').forEach(el => progressObs.observe(el));
}, 200);

// ── Toast utility ───────────────────────
function showToast(msg, type = 'success') {
  // Disabled as per user request
  return;
}

// ── Feature card 3D tilt ────────────────
document.querySelectorAll('.feature-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `perspective(800px) rotateX(${-y * 4}deg) rotateY(${x * 4}deg) translateZ(4px)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.transition = 'transform 0.4s ease';
  });
  card.addEventListener('mouseenter', () => { card.style.transition = 'none'; });
});

// Export globals
window.scrollToSection = scrollToSection;
window.showToast = showToast;
window.revObs = revealObs;
window.openProfile = openProfile;
window.closeProfile = closeProfile;
window.updateProgBars = updateProgBars;

// ── Edit Profile Modal ────────────────
function openEditProfile() { document.getElementById('editProfileOverlay').classList.add('open'); }
function closeEditProfile() { document.getElementById('editProfileOverlay').classList.remove('open'); }
window.openEditProfile = openEditProfile;
window.closeEditProfile = closeEditProfile;

function saveProfileChanges() {
  const name = document.getElementById('editName')?.value.trim();
  const role = document.getElementById('editRole')?.value.trim();
  
  if (name) {
    if(document.getElementById('profileName')) document.getElementById('profileName').textContent = name;
    if(document.getElementById('navUserName')) document.getElementById('navUserName').textContent = name;
    if(document.getElementById('navAvatarLetter')) document.getElementById('navAvatarLetter').textContent = name[0].toUpperCase();
    if(document.getElementById('profileAvatarBig')) document.getElementById('profileAvatarBig').textContent = name[0].toUpperCase();
    if(localStorage.getItem('vm_token')) localStorage.setItem('vm_user', name);
    if(sessionStorage.getItem('vm_token')) sessionStorage.setItem('vm_user', name);
  }
  if (role) {
    if(document.getElementById('profileRole')) document.getElementById('profileRole').textContent = role;
    localStorage.setItem('vm_role', role);
    sessionStorage.setItem('vm_role', role);
  }
  
  if (typeof window.showToast === 'function') window.showToast('Profile updated!', 'success');
  closeEditProfile();
}
window.saveProfileChanges = saveProfileChanges;

document.addEventListener('DOMContentLoaded', () => {
  const role = localStorage.getItem('vm_role') || sessionStorage.getItem('vm_role') || 'Aspiring Developer';
  if (document.getElementById('profileRole')) document.getElementById('profileRole').textContent = role;
  if (document.getElementById('editRole')) document.getElementById('editRole').value = role;
});
