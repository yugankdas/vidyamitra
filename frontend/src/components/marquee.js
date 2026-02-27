// ═══════════════════════════════════════
//  MARQUEE COMPONENT
//  Handles click-to-chat on marquee cards
// ═══════════════════════════════════════

document.querySelectorAll('.marquee-card').forEach(card => {
  card.addEventListener('click', () => {
    const cmd = card.querySelector('.mcard-cmd')?.textContent || '';
    const text = card.querySelector('.mcard-text')?.textContent || '';
    const input = document.getElementById('chatInput');
    if (input) {
      input.value = `${cmd} — ${text}`;
      scrollToSection('agent');
      setTimeout(() => sendChat(), 300);
    }
  });
});
