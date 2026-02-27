// ═══════════════════════════════════════
//  INTERVIEW COMPONENT
//  Scroll-pinned panels + canvas chart
// ═══════════════════════════════════════

// ── Pin panel activation ────────────────
function activatePin(n) {
  for (let i = 1; i <= 3; i++) {
    const item = document.getElementById(`pin-${i}`);
    const panel = document.getElementById(`panel-${i}`);
    if (item) item.classList.toggle('active', i === n);
    if (panel) panel.classList.toggle('active', i === n);
  }
  if (n === 3) drawInterviewChart();
}

// ── Scroll-driven pin update ────────────
const pinSection = document.querySelector('.pin-section');
if (pinSection) {
  window.addEventListener('scroll', () => {
    const rect = pinSection.getBoundingClientRect();
    const sectionH = pinSection.offsetHeight;
    const viewH = window.innerHeight;
    const scrolled = -rect.top;
    const total = sectionH - viewH;

    if (scrolled < 0 || scrolled > total) return;

    const progress = scrolled / total;
    let panel = 1;
    if (progress > 0.66) panel = 3;
    else if (progress > 0.33) panel = 2;
    activatePin(panel);
  });
}

// ── Canvas chart ────────────────────────
function drawInterviewChart() {
  const canvas = document.getElementById('interviewChart');
  if (!canvas || canvas.dataset.drawn) return;
  canvas.dataset.drawn = 'true';

  const ctx = canvas.getContext('2d');
  const data = [52, 61, 58, 70, 78, 74, 84];
  const labels = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'];
  const W = 260, H = 140;
  const pad = { t: 10, r: 10, b: 24, l: 26 };
  const cW = W - pad.l - pad.r, cH = H - pad.t - pad.b;
  const min = 40, max = 100;
  const xp = i => pad.l + (i / (data.length - 1)) * cW;
  const yp = v => pad.t + cH - ((v - min) / (max - min)) * cH;

  ctx.clearRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.05)';
  ctx.lineWidth = 1;
  [0.25, 0.5, 0.75, 1].forEach(t => {
    ctx.beginPath();
    ctx.moveTo(pad.l, pad.t + cH * (1 - t));
    ctx.lineTo(W - pad.r, pad.t + cH * (1 - t));
    ctx.stroke();
  });

  // Area fill
  const grad = ctx.createLinearGradient(0, pad.t, 0, H);
  grad.addColorStop(0, 'rgba(232,184,75,0.2)');
  grad.addColorStop(1, 'rgba(232,184,75,0)');
  ctx.beginPath();
  ctx.moveTo(xp(0), yp(data[0]));
  for (let i = 1; i < data.length; i++) {
    const cx = (xp(i - 1) + xp(i)) / 2;
    ctx.bezierCurveTo(cx, yp(data[i - 1]), cx, yp(data[i]), xp(i), yp(data[i]));
  }
  ctx.lineTo(xp(data.length - 1), H - pad.b);
  ctx.lineTo(xp(0), H - pad.b);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // Line
  ctx.beginPath();
  ctx.moveTo(xp(0), yp(data[0]));
  for (let i = 1; i < data.length; i++) {
    const cx = (xp(i - 1) + xp(i)) / 2;
    ctx.bezierCurveTo(cx, yp(data[i - 1]), cx, yp(data[i]), xp(i), yp(data[i]));
  }
  ctx.strokeStyle = '#e8b84b';
  ctx.lineWidth = 2.5;
  ctx.stroke();

  // Dots
  data.forEach((v, i) => {
    ctx.beginPath();
    ctx.arc(xp(i), yp(v), 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#e8b84b';
    ctx.fill();
  });

  // Labels
  ctx.fillStyle = 'rgba(138,130,153,0.8)';
  ctx.font = '10px Syne, sans-serif';
  ctx.textAlign = 'center';
  labels.forEach((l, i) => ctx.fillText(l, xp(i), H - pad.b + 14));
}

// Export
window.activatePin = activatePin;
window.drawInterviewChart = drawInterviewChart;

// Initialize first panel
activatePin(1);
