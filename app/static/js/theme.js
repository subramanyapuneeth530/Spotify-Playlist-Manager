const THEMES = ['cyber', 'paper', 'aurora', 'obsidian', 'chalk'];
const LOGO_TEXT = { cyber: 'MELODEX', paper: 'Melodex', aurora: 'melodex', obsidian: 'Melodex', chalk: 'MELODEX' };
const LOGO_SUB  = { cyber: '// playlist manager', paper: 'your music, organised', aurora: 'playlist manager', obsidian: 'playlist manager', chalk: 'playlist manager' };

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('melodex_theme', theme);
  document.querySelectorAll('.theme-btn').forEach(b => b.classList.toggle('active', b.dataset.theme === theme));
  const logo = document.getElementById('logo-name');
  const sub  = document.getElementById('logo-sub');
  if (logo) logo.textContent = LOGO_TEXT[theme] || 'MELODEX';
  if (sub)  sub.textContent  = LOGO_SUB[theme]  || 'playlist manager';
  // Re-render all active Chart.js charts with new theme colors
  setTimeout(() => {
    document.querySelectorAll('canvas').forEach(canvas => {
      if (canvas._chart) {
        const chart = canvas._chart;
        const accent = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
        const text3  = getComputedStyle(document.documentElement).getPropertyValue('--text3').trim();
        const surf2  = getComputedStyle(document.documentElement).getPropertyValue('--surface2').trim();
        chart.data.datasets.forEach(ds => { ds.backgroundColor = accent; ds.borderColor = accent; });
        if (chart.options.scales?.x) { chart.options.scales.x.ticks.color = text3; chart.options.scales.x.grid.color = surf2; }
        if (chart.options.scales?.y) { chart.options.scales.y.ticks.color = text3; chart.options.scales.y.grid.color = surf2; }
        chart.update();
      }
    });
  }, 50);
}

function initTheme() {
  const saved = localStorage.getItem('melodex_theme') || 'cyber';
  applyTheme(saved);
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
  });
}

document.addEventListener('DOMContentLoaded', initTheme);
