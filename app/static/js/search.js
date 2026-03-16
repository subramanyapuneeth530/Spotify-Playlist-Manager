function liveFilter(inputId, itemSelector, textSelector) {
  const input = document.getElementById(inputId);
  if (!input) return;
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();
    document.querySelectorAll(itemSelector).forEach(el => {
      const text = el.querySelector(textSelector)?.textContent?.toLowerCase() || el.textContent.toLowerCase();
      el.style.display = q === '' || text.includes(q) ? '' : 'none';
    });
  });
}

function globalSearch(q) {
  q = q.toLowerCase().trim();
  if (!q) return;
  // Redirect to artists page with search pre-filled
  window.location.href = `/artists?q=${encodeURIComponent(q)}`;
}

document.addEventListener('DOMContentLoaded', () => {
  const globalInput = document.getElementById('global-search');
  if (globalInput) {
    globalInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') globalSearch(globalInput.value);
    });
  }
});
