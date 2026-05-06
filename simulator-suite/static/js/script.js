/* ============================================================
   SIMULATOR SUITE — Main SPA Script
   ============================================================ */

'use strict';

// ── Constants ──────────────────────────────────────────────
const API_BASE = '';
const STORAGE_KEY = 'simulator_suite_last';
const MAX_INPUT = 100;
const SAMPLE_INPUTS = [
  { label: 'Classic Textbook', ref: '1,2,3,4,1,2,5,1,2,3,4,5', frames: 3 },
  { label: 'Thrashing Scenario', ref: '1,2,3,4,5,1,2,3,4,5', frames: 3 },
  { label: 'Locality of Reference', ref: '1,2,1,3,2,1,4,1,2,3', frames: 3 },
  { label: 'Worst Case FIFO', ref: '1,2,3,4,1,2,3,4,1,2,3,4', frames: 4 },
];

// ── App State ──────────────────────────────────────────────
const state = {
  currentTab: 'home',
  simulationData: null,
  currentStep: 0,
  charts: {},
  animating: false,
};

// ── DOM Refs ───────────────────────────────────────────────
const dom = {
  tabs: () => document.querySelectorAll('.nav-tab'),
  pages: () => document.querySelectorAll('.page'),
  refInput: () => document.getElementById('refInput'),
  framesInput: () => document.getElementById('framesInput'),
  algoCheckboxes: () => document.querySelectorAll('.algo-checkbox'),
  runBtn: () => document.getElementById('runBtn'),
  resetBtn: () => document.getElementById('resetBtn'),
  sampleBtn: () => document.getElementById('sampleBtn'),
  spinner: () => document.getElementById('spinner'),
  alertBox: () => document.getElementById('alertBox'),
  vizArea: () => document.getElementById('vizArea'),
  emptyState: () => document.getElementById('emptyState'),
  timelineBar: () => document.getElementById('timelineBar'),
  stepSlider: () => document.getElementById('stepSlider'),
  stepLabel: () => document.getElementById('stepLabel'),
  prevStepBtn: () => document.getElementById('prevStepBtn'),
  nextStepBtn: () => document.getElementById('nextStepBtn'),
  resultsSection: () => document.getElementById('resultsSection'),
  resultsEmpty: () => document.getElementById('resultsEmpty'),
  chartsSection: () => document.getElementById('chartsSection'),
  chartsEmpty: () => document.getElementById('chartsEmpty'),
  exportCsvBtn: () => document.getElementById('exportCsvBtn'),
  exportPdfBtn: () => document.getElementById('exportPdfBtn'),
  refError: () => document.getElementById('refError'),
  framesError: () => document.getElementById('framesError'),
};

// ── Tab Navigation ─────────────────────────────────────────
function switchTab(tabId) {
  state.currentTab = tabId;
  dom.tabs().forEach(t => t.classList.toggle('active', t.dataset.tab === tabId));
  dom.pages().forEach(p => p.classList.toggle('active', p.id === `page-${tabId}`));
  if (tabId === 'charts' && state.simulationData) renderCharts();
}

// ── Alert Banner ───────────────────────────────────────────
function showAlert(msg, type = 'error') {
  const el = dom.alertBox();
  el.className = `alert alert-${type} visible`;
  el.innerHTML = `<span>${iconFor(type)}</span><span>${msg}</span>`;
}
function hideAlert() { dom.alertBox().classList.remove('visible'); }
function iconFor(t) { return { error:'⚠️', success:'✅', warning:'🔔', info:'ℹ️' }[t] || ''; }

// ── Input Validation ───────────────────────────────────────
function parseRefString(raw) {
  const parts = raw.trim().split(/[\s,]+/).filter(Boolean);
  if (!parts.length) throw new Error('Reference string cannot be empty.');
  if (parts.length > MAX_INPUT) throw new Error(`Maximum ${MAX_INPUT} values allowed (got ${parts.length}).`);
  const nums = parts.map((p, i) => {
    const n = parseInt(p, 10);
    if (isNaN(n) || n < 0) throw new Error(`Invalid value at position ${i + 1}: "${p}" (must be a non-negative integer).`);
    return n;
  });
  return nums;
}

function validateForm() {
  let ok = true;
  dom.refInput().classList.remove('invalid');
  dom.framesInput().classList.remove('invalid');
  dom.refError().style.display = 'none';
  dom.framesError().style.display = 'none';

  try { parseRefString(dom.refInput().value); }
  catch (e) {
    dom.refInput().classList.add('invalid');
    dom.refError().textContent = e.message;
    dom.refError().style.display = 'block';
    ok = false;
  }

  const f = parseInt(dom.framesInput().value, 10);
  if (isNaN(f) || f < 1 || f > 20) {
    dom.framesInput().classList.add('invalid');
    dom.framesError().textContent = 'Frames must be between 1 and 20.';
    dom.framesError().style.display = 'block';
    ok = false;
  }

  const algos = [...dom.algoCheckboxes()].filter(c => c.checked);
  if (!algos.length) {
    showAlert('Please select at least one algorithm.', 'warning');
    ok = false;
  }

  return ok;
}

// ── Run Simulation ─────────────────────────────────────────
async function runSimulation() {
  if (!validateForm()) return;
  hideAlert();

  const refString = parseRefString(dom.refInput().value);
  const frames = parseInt(dom.framesInput().value, 10);
  const algorithms = [...dom.algoCheckboxes()].filter(c => c.checked).map(c => c.value);

  if (refString.length > 50) {
    showAlert(`Large input detected (${refString.length} references). This may take a moment.`, 'info');
  }

  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reference_string: refString, frames, algorithms }),
    });
    const json = await res.json();

    if (!res.ok || json.status === 'error') {
      showAlert(json.message || 'Simulation failed.', 'error');
      return;
    }

    state.simulationData = json.data;
    state.currentStep = json.data.input_summary.total_references - 1;

    saveToStorage(json.data);
    renderVisualization(json.data);
    renderResults(json.data);
    if (state.currentTab === 'charts') renderCharts();

    showAlert(
      `✓ Simulation complete! Best algorithm: <strong>${json.data.best_algorithm_name}</strong>`,
      'success'
    );
  } catch (err) {
    showAlert('Network error — is the Flask server running?', 'error');
  } finally {
    setLoading(false);
  }
}

function setLoading(on) {
  const btn = dom.runBtn();
  const sp = dom.spinner();
  btn.disabled = on;
  sp.classList.toggle('visible', on);
  btn.querySelector('.btn-text').textContent = on ? 'Running…' : 'Run Simulation';
}

// ── Visualization ──────────────────────────────────────────
function renderVisualization(data) {
  dom.emptyState().style.display = 'none';
  dom.vizArea().innerHTML = '';
  dom.timelineBar().style.display = 'flex';

  const totalSteps = data.input_summary.total_references;
  const slider = dom.stepSlider();
  slider.max = totalSteps - 1;
  slider.value = totalSteps - 1;
  updateStepLabel(totalSteps - 1, totalSteps);

  for (const [algoKey, result] of Object.entries(data.results)) {
    dom.vizArea().appendChild(buildAlgoViz(result, state.currentStep));
  }
}

function buildAlgoViz(result, upToStep) {
  const block = document.createElement('div');
  block.className = 'algo-viz-block';
  block.dataset.algo = result.algorithm;

  const faults = result.steps.slice(0, upToStep + 1).filter(s => s.fault).length;
  const hits = upToStep + 1 - faults;
  const numFrames = result.steps[0].frames.length;

  block.innerHTML = `
    <div class="algo-viz-header">
      <div class="algo-viz-name">
        <span>${algoIcon(result.algorithm)}</span>
        ${result.algorithm_name}
      </div>
      <div class="algo-viz-stats">
        <span class="stat-chip stat-fault">⚡ ${faults} Faults</span>
        <span class="stat-chip stat-hit">✓ ${hits} Hits</span>
      </div>
    </div>
    <div class="viz-scroll">
      ${buildVizTable(result, upToStep, numFrames)}
    </div>`;
  return block;
}

function buildVizTable(result, upToStep, numFrames) {
  const steps = result.steps.slice(0, upToStep + 1);

  // Reference row
  let refRow = '<div class="viz-row viz-ref-row"><div class="viz-row-label">Page Ref</div><div class="viz-cells">';
  steps.forEach((s, i) => {
    const isCur = i === upToStep;
    refRow += `<div class="ref-cell${isCur ? ' current' : ''}">${s.page}</div>`;
  });
  refRow += '</div></div>';

  // Frame rows
  let frameRows = '';
  for (let f = 0; f < numFrames; f++) {
    frameRows += `<div class="viz-row" style="margin-top:4px"><div class="viz-row-label">Frame ${f + 1}</div><div class="viz-cells">`;
    steps.forEach((s, i) => {
      const val = s.frames[f];
      const isCur = i === upToStep;
      let cls = 'frame-cell';
      if (val !== null) cls += ' occupied';
      if (isCur && s.fault && val !== null) cls += ' fault-cell';
      if (isCur && !s.fault && val === s.page) cls += ' hit-cell';
      if (isCur) cls += ' current-col';
      frameRows += `<div class="${cls}">${val !== null ? val : ''}</div>`;
    });
    frameRows += '</div></div>';
  }

  // Fault/Hit indicator row
  let fhRow = '<div class="viz-row" style="margin-top:6px"><div class="viz-row-label">Status</div><div class="viz-cells">';
  steps.forEach(s => {
    fhRow += `<div class="fault-indicator ${s.fault ? 'f' : 'h'}">${s.fault ? 'F' : 'H'}</div>`;
  });
  fhRow += '</div></div>';

  return `<div class="viz-table">${refRow}${frameRows}${fhRow}</div>`;
}

function algoIcon(algo) {
  return { fifo: '📋', lru: '🕐', optimal: '⭐' }[algo] || '🔷';
}

function updateVisualizationStep(step) {
  if (!state.simulationData) return;
  state.currentStep = step;
  const total = state.simulationData.input_summary.total_references;
  updateStepLabel(step, total);

  document.querySelectorAll('.algo-viz-block').forEach(block => {
    const key = block.dataset.algo;
    const result = state.simulationData.results[key];
    block.replaceWith(buildAlgoViz(result, step));
  });
}

function updateStepLabel(step, total) {
  dom.stepLabel().textContent = `Step ${step + 1} / ${total}`;
}

// ── Results Table ──────────────────────────────────────────
function renderResults(data) {
  const sec = dom.resultsSection();
  const empty = dom.resultsEmpty();
  empty.style.display = 'none';
  sec.style.display = 'block';

  const best = data.best_algorithm;
  const rows = data.comparison.map(r => {
    const isBest = r.algorithm === best;
    const hitPct = (r.hit_ratio * 100).toFixed(1);
    const faultPct = (r.fault_rate * 100).toFixed(1);
    return `
      <tr class="${isBest ? 'best-row' : ''}">
        <td>
          <span>${algoIcon(r.algorithm)}</span>
          <strong>${r.algorithm_name}</strong>
          ${isBest ? '<span class="best-badge" style="margin-left:8px">🏆 Best</span>' : ''}
        </td>
        <td><span style="color:#fca5a5;font-weight:700">${r.page_faults}</span></td>
        <td><span style="color:#6ee7b7;font-weight:700">${r.page_hits}</span></td>
        <td>
          <div class="metric-bar-wrap">
            ${hitPct}%
            <div class="metric-bar">
              <div class="metric-bar-fill" style="width:${hitPct}%;background:var(--accent-green)"></div>
            </div>
          </div>
        </td>
        <td>
          <div class="metric-bar-wrap">
            ${faultPct}%
            <div class="metric-bar">
              <div class="metric-bar-fill" style="width:${faultPct}%;background:var(--accent-red)"></div>
            </div>
          </div>
        </td>
        <td>${r.execution_time_ms.toFixed(3)} ms</td>
      </tr>`;
  }).join('');

  sec.querySelector('tbody').innerHTML = rows;

  // Summary cards
  const summary = sec.querySelector('.summary-cards');
  if (summary) {
    const bestData = data.comparison.find(r => r.algorithm === best);
    summary.innerHTML = `
      <div class="card"><div class="card-title">Best Algorithm</div>
        <div class="card-value" style="font-size:1.4rem">${algoIcon(best)} ${bestData.algorithm_name}</div>
        <div class="card-sub">${bestData.page_faults} page faults</div>
      </div>
      <div class="card"><div class="card-title">Total References</div>
        <div class="card-value">${bestData.total_references}</div>
        <div class="card-sub">page accesses</div>
      </div>
      <div class="card"><div class="card-title">Best Hit Ratio</div>
        <div class="card-value">${(bestData.hit_ratio * 100).toFixed(1)}%</div>
        <div class="card-sub">page hits / total</div>
      </div>
      <div class="card"><div class="card-title">Min Fault Rate</div>
        <div class="card-value">${(bestData.fault_rate * 100).toFixed(1)}%</div>
        <div class="card-sub">faults / total refs</div>
      </div>`;
  }
}

// ── Charts ─────────────────────────────────────────────────
function renderCharts() {
  if (!state.simulationData) return;
  dom.chartsEmpty().style.display = 'none';
  dom.chartsSection().style.display = 'block';

  const comparison = state.simulationData.comparison;
  const labels = comparison.map(r => r.algorithm_name);
  const faults = comparison.map(r => r.page_faults);
  const hits = comparison.map(r => r.page_hits);
  const hitRatios = comparison.map(r => +(r.hit_ratio * 100).toFixed(2));
  const faultRates = comparison.map(r => +(r.fault_rate * 100).toFixed(2));

  const chartDefaults = {
    plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } } },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
    },
  };

  // Bar: Page Faults vs Hits
  buildChart('faultsChart', 'bar', labels, [
    { label: 'Page Faults', data: faults, backgroundColor: 'rgba(239,68,68,0.7)', borderColor: '#ef4444', borderWidth: 2 },
    { label: 'Page Hits',   data: hits,   backgroundColor: 'rgba(16,185,129,0.7)', borderColor: '#10b981', borderWidth: 2 },
  ], { ...chartDefaults, plugins: { ...chartDefaults.plugins, title: { display: false } } });

  // Bar: Hit Ratio %
  buildChart('hitRatioChart', 'bar', labels, [
    { label: 'Hit Ratio %',  data: hitRatios,  backgroundColor: 'rgba(6,182,212,0.7)', borderColor: '#06b6d4', borderWidth: 2 },
    { label: 'Fault Rate %', data: faultRates, backgroundColor: 'rgba(245,158,11,0.7)', borderColor: '#f59e0b', borderWidth: 2 },
  ], chartDefaults);

  // Line: cumulative faults per step
  const algorithms = Object.keys(state.simulationData.results);
  const stepCount = state.simulationData.results[algorithms[0]].steps.length;
  const stepLabels = Array.from({ length: stepCount }, (_, i) => i + 1);
  const lineColors = { fifo: '#7c3aed', lru: '#06b6d4', optimal: '#10b981' };

  const lineDatasets = algorithms.map(algo => {
    const steps = state.simulationData.results[algo].steps;
    let cum = 0;
    return {
      label: state.simulationData.results[algo].algorithm_name,
      data: steps.map(s => { if (s.fault) cum++; return cum; }),
      borderColor: lineColors[algo] || '#a78bfa',
      backgroundColor: 'transparent',
      tension: 0.3, borderWidth: 2, pointRadius: 3,
    };
  });
  buildChart('faultTrendChart', 'line', stepLabels, lineDatasets, chartDefaults);

  // Doughnut: best algo hit vs fault
  const best = state.simulationData.comparison.find(r => r.algorithm === state.simulationData.best_algorithm);
  buildChart('doughnutChart', 'doughnut', ['Page Hits', 'Page Faults'], [{
    data: [best.page_hits, best.page_faults],
    backgroundColor: ['rgba(16,185,129,0.8)', 'rgba(239,68,68,0.8)'],
    borderColor: ['#10b981', '#ef4444'], borderWidth: 2,
  }], {
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } }, position: 'bottom' },
    },
  });
}

function buildChart(canvasId, type, labels, datasets, options) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  if (state.charts[canvasId]) state.charts[canvasId].destroy();
  state.charts[canvasId] = new Chart(canvas, {
    type,
    data: { labels, datasets },
    options: { responsive: true, maintainAspectRatio: true, animation: { duration: 600 }, ...options },
  });
}

// ── Export ─────────────────────────────────────────────────
function exportCSV() {
  if (!state.simulationData) return;
  const rows = [['Algorithm', 'Page Faults', 'Page Hits', 'Hit Ratio %', 'Fault Rate %', 'Exec Time (ms)']];
  state.simulationData.comparison.forEach(r => {
    rows.push([
      r.algorithm_name, r.page_faults, r.page_hits,
      (r.hit_ratio * 100).toFixed(2), (r.fault_rate * 100).toFixed(2),
      r.execution_time_ms.toFixed(4),
    ]);
  });
  const csv = rows.map(r => r.join(',')).join('\n');
  downloadFile('simulation_results.csv', 'text/csv', csv);
}

function exportPDF() {
  window.print();
}

function downloadFile(name, mime, content) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type: mime }));
  a.download = name;
  a.click();
}

// ── LocalStorage ───────────────────────────────────────────
function saveToStorage(data) {
  try {
    const summary = {
      ref: data.input_summary.reference_string,
      frames: data.input_summary.frames,
      algorithms: data.input_summary.algorithms,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(summary));
  } catch (_) {}
}

function restoreFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    const { ref, frames, algorithms } = JSON.parse(saved);
    if (dom.refInput()) dom.refInput().value = ref.join(',');
    if (dom.framesInput()) dom.framesInput().value = frames;
    dom.algoCheckboxes().forEach(cb => { cb.checked = algorithms.includes(cb.value); });
  } catch (_) {}
}

// ── Reset ──────────────────────────────────────────────────
function resetAll() {
  dom.refInput().value = '';
  dom.framesInput().value = 3;
  dom.algoCheckboxes().forEach(cb => { cb.checked = true; });
  dom.refInput().classList.remove('invalid');
  dom.framesInput().classList.remove('invalid');
  dom.refError().style.display = 'none';
  dom.framesError().style.display = 'none';
  hideAlert();
  dom.emptyState().style.display = 'flex';
  dom.vizArea().innerHTML = '';
  dom.timelineBar().style.display = 'none';
  dom.resultsSection().style.display = 'none';
  dom.resultsEmpty().style.display = 'flex';
  dom.chartsSection().style.display = 'none';
  dom.chartsEmpty().style.display = 'flex';
  state.simulationData = null;
  localStorage.removeItem(STORAGE_KEY);
}

// ── Sample Input ───────────────────────────────────────────
function loadSample() {
  const idx = Math.floor(Math.random() * SAMPLE_INPUTS.length);
  const s = SAMPLE_INPUTS[idx];
  dom.refInput().value = s.ref;
  dom.framesInput().value = s.frames;
  dom.algoCheckboxes().forEach(cb => { cb.checked = true; });
  showAlert(`Loaded sample: "${s.label}"`, 'info');
}

// ── Boot ───────────────────────────────────────────────────
function init() {
  // Tab clicks
  dom.tabs().forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Buttons
  dom.runBtn()?.addEventListener('click', runSimulation);
  dom.resetBtn()?.addEventListener('click', resetAll);
  dom.sampleBtn()?.addEventListener('click', loadSample);
  document.getElementById('heroTryBtn')?.addEventListener('click', () => {
    loadSample(); switchTab('simulation');
  });
  dom.exportCsvBtn()?.addEventListener('click', exportCSV);
  dom.exportPdfBtn()?.addEventListener('click', exportPDF);

  // Step controls
  dom.stepSlider()?.addEventListener('input', e => {
    updateVisualizationStep(parseInt(e.target.value));
  });
  dom.prevStepBtn()?.addEventListener('click', () => {
    const s = dom.stepSlider();
    if (+s.value > 0) { s.value = +s.value - 1; updateVisualizationStep(+s.value); }
  });
  dom.nextStepBtn()?.addEventListener('click', () => {
    const s = dom.stepSlider();
    if (+s.value < +s.max) { s.value = +s.value + 1; updateVisualizationStep(+s.value); }
  });

  // Restore last run
  restoreFromStorage();

  // Initially hide timeline and results
  dom.timelineBar().style.display = 'none';
  dom.resultsSection().style.display = 'none';
  dom.chartsSection().style.display = 'none';

  // Fetch algo list for health-check (optional UX)
  fetch('/api/algorithms').catch(() => {});
}

document.addEventListener('DOMContentLoaded', init);

// Expose globals for inline onclick handlers
window.switchTab = switchTab;
window.loadSample = loadSample;
window.runSimulation = runSimulation;
