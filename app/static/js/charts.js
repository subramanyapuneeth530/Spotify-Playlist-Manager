function getAccent() {
  return getComputedStyle(document.documentElement).getPropertyValue('--accent').trim();
}
function getText3() {
  return getComputedStyle(document.documentElement).getPropertyValue('--text3').trim();
}
function getSurface2() {
  return getComputedStyle(document.documentElement).getPropertyValue('--surface2').trim();
}

function drawBarChart(canvasId, labels, data, label = '') {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();
  ctx._chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label,
        data,
        backgroundColor: getAccent(),
        borderRadius: 3,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: getText3(), font: { size: 11 } }, grid: { color: getSurface2() } },
        y: { ticks: { color: getText3(), font: { size: 11 } }, grid: { color: getSurface2() } },
      }
    }
  });
}

function drawDonutChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (ctx._chart) ctx._chart.destroy();
  const accent = getAccent();
  ctx._chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: labels.map((_, i) => `${accent}${Math.round(255 * (0.9 - i * 0.07)).toString(16).padStart(2,'0')}`),
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'right', labels: { color: getText3(), font: { size: 11 }, boxWidth: 12 } }
      }
    }
  });
}
