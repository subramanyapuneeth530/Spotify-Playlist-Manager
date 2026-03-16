const SHORTCUTS = [
  { key: 'g d', desc: 'Go to Dashboard' , action: () => window.location.href = '/dashboard' },
  { key: 'g p', desc: 'Go to Playlists'  , action: () => window.location.href = '/playlists' },
  { key: 'g a', desc: 'Go to Artists'    , action: () => window.location.href = '/artists' },
  { key: 'g n', desc: 'Go to Analytics'  , action: () => window.location.href = '/analytics' },
  { key: 'g u', desc: 'Go to Duplicates' , action: () => window.location.href = '/duplicates' },
  { key: 'g h', desc: 'Go to History'    , action: () => window.location.href = '/history' },
  { key: '/',   desc: 'Focus search'     , action: () => document.getElementById('global-search')?.focus() },
  { key: '?',   desc: 'Show shortcuts'   , action: () => toggleShortcutsPanel() },
  { key: 'Escape', desc: 'Close panel'   , action: () => closeShortcutsPanel() },
];

let keyBuffer = '';
let keyTimer = null;

function toggleShortcutsPanel() {
  document.getElementById('shortcuts-overlay')?.classList.toggle('show');
}
function closeShortcutsPanel() {
  document.getElementById('shortcuts-overlay')?.classList.remove('show');
}

function buildShortcutsPanel() {
  const panel = document.getElementById('shortcuts-list');
  if (!panel) return;
  panel.innerHTML = SHORTCUTS.map(s => `
    <div class="shortcut-row">
      <span class="shortcut-desc">${s.desc}</span>
      <span class="shortcut-key">${s.key}</span>
    </div>
  `).join('');
}

document.addEventListener('keydown', e => {
  if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
  const key = e.key;
  keyBuffer += (keyBuffer ? ' ' : '') + key;
  clearTimeout(keyTimer);
  keyTimer = setTimeout(() => keyBuffer = '', 800);

  for (const s of SHORTCUTS) {
    if (keyBuffer === s.key || key === s.key) {
      e.preventDefault();
      s.action();
      keyBuffer = '';
      break;
    }
  }
});

document.addEventListener('DOMContentLoaded', buildShortcutsPanel);
