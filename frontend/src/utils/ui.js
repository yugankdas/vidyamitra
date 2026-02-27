// ═══════════════════════════════════════
//  UI UTILITIES
//  scroll, reveal, counter, accordion, toasts
// ═══════════════════════════════════════

// ── Smooth scroll helper ────────────────
function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Nav scroll class ────────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('mainNav');
  if (nav) nav.classList.toggle('scrolled', window.scrollY > 20);
  updateSectionNav();
});

// ── Section nav active state ────────────
function updateSectionNav() {
  const sections = ['agent', 'resume', 'interview', 'quiz', 'career', 'progress', 'jobs', 'tech'];
  const scrollY = window.scrollY + 120;

  for (let i = sections.length - 1; i >= 0; i--) {
    const el = document.getElementById(sections[i]);
    if (el && el.offsetTop <= scrollY) {
      document.querySelectorAll('.snav-link').forEach((l, idx) => {
        l.classList.toggle('active', idx === i);
      });
      document.querySelectorAll('.nav-pill').forEach((l, idx) => {
        l.classList.toggle('active', idx === i);
      });
      break;
    }
  }
}

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

// ── Counter animation ───────────────────
function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10);
  const suffix = el.dataset.suffix || '';
  const duration = 1800;
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(eased * target);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = target + suffix;
  }
  requestAnimationFrame(update);
}

const counterObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounter(e.target);
      counterObs.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.counter').forEach(el => counterObs.observe(el));

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
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️' };
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = (icons[type] || '✅') + ' ' + msg;
  const container = document.getElementById('toastContainer');
  if (container) container.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = '0.3s';
    setTimeout(() => t.remove(), 300);
  }, 3000);
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
