// ═══════════════════════════════════════
//  SKILLS BAR ANIMATION
// ═══════════════════════════════════════

const skillObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('[data-width]').forEach(bar => {
        setTimeout(() => {
          bar.style.width = bar.dataset.width;
        }, 100);
      });
      skillObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });

// Observe all containers that hold skill bars
document.querySelectorAll('.bar-animate-group, #progress .reveal').forEach(el => {
  skillObs.observe(el);
});
