const historyForm = document.getElementById("history-form");
const historyMetricEl = document.getElementById("history-metric");
const historySearchEl = document.getElementById("history-search");
const historyStatusEl = document.getElementById("history-status");
const historyTitleEl = document.getElementById("history-title");
const historyValueHeadEl = document.getElementById("history-value-head");
const historyBodyEl = document.getElementById("history-body");

let historyReady = false;

function renderHistoryRows(rows) {
  historyBodyEl.innerHTML = "";
  if (!Array.isArray(rows) || rows.length === 0) {
    historyBodyEl.innerHTML = `<tr><td colspan="3">查無資料</td></tr>`;
    return;
  }
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.rank}</td><td>${row.name}</td><td>${row.value_text}</td>`;
    historyBodyEl.appendChild(tr);
  });
}

function setupMetricOptions(availableMetrics, selectedMetric) {
  historyMetricEl.innerHTML = "";
  Object.entries(availableMetrics).forEach(([key, info]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = `${info[0]} (${key})`;
    if (key === selectedMetric) option.selected = true;
    historyMetricEl.appendChild(option);
  });
}

const API_BASE = 'https://nba-web-app-5.onrender.com';

async function fetchHistory(metric = "PTS", q = "") {
  const url = `${API_BASE}/api/history?metric=${encodeURIComponent(metric)}&limit=500&q=${encodeURIComponent(q)}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(msg || "歷史排名查詢失敗");
  }
  return resp.json();
}

async function loadHistory(metric = "PTS", q = "") {
  historyStatusEl.textContent = "🔍 載入中...";
  try {
    const data = await fetchHistory(metric, q);
    setupMetricOptions(data.available_metrics, data.metric);
    historyTitleEl.textContent = `NBA 歷史總排名 - ${data.label}`;
    historyValueHeadEl.textContent = data.label;
    renderHistoryRows(data.rows);
    historyStatusEl.textContent = `✅ 共 ${data.rows.length} 筆`;
    historyReady = true;
  } catch (error) {
    historyStatusEl.textContent = "❌ 查詢失敗";
    historyBodyEl.innerHTML = `<tr><td colspan="3">${error.message}</td></tr>`;
  }
}

if (historyForm) {
  historyForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await loadHistory(historyMetricEl.value || "PTS", historySearchEl.value || "");
  });
}

const historyModeBtn = document.querySelector('.mode-btn[data-mode="history"]');
if (historyModeBtn) {
  historyModeBtn.addEventListener("click", async () => {
    if (!historyReady) {
      await loadHistory("PTS", "");
    }
  });
}
