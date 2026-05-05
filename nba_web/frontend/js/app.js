const modeButtons = document.querySelectorAll(".mode-btn");
const panels = {
  single: document.getElementById("single-panel"),
  compare: document.getElementById("compare-panel"),
  quiz: document.getElementById("quiz-panel"),
  history: document.getElementById("history-panel"),
  team: document.getElementById("team-panel"),
};

function switchMode(mode) {
  Object.values(panels).forEach((panel) => panel.classList.remove("active"));
  modeButtons.forEach((btn) => btn.classList.remove("active"));

  if (panels[mode]) {
    panels[mode].classList.add("active");
  }
  const targetBtn = document.querySelector(`.mode-btn[data-mode="${mode}"]`);
  if (targetBtn) {
    targetBtn.classList.add("active");
  }
}

modeButtons.forEach((btn) => {
  btn.addEventListener("click", () => switchMode(btn.dataset.mode));
});

const form = document.getElementById("player-form");
const input = document.getElementById("player-name");
const statusEl = document.getElementById("status");
const playerTitleEl = document.getElementById("player-title");
const emptyResultEl = document.getElementById("empty-result");
const playerResultEl = document.getElementById("player-result");
const playerImageEl = document.getElementById("player-image");
const awardsListEl = document.getElementById("awards-list");
const awardsTitleEl = document.getElementById("awards-title");
const chartTitleEl = document.getElementById("chart-title");
const vsTableBodyEl = document.getElementById("vs-table-body");

let seasonChart = null;

function setText(id, value, suffix = "") {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = value === undefined || value === null || value === "" ? "未知" : `${value}${suffix}`;
}

function renderAwards(awards) {
  const counter = new Map();
  (Array.isArray(awards) ? awards : []).forEach((item) => {
    const desc = item.DESCRIPTION || item.description || "未知獎項";
    counter.set(desc, (counter.get(desc) || 0) + 1);
  });
  awardsListEl.innerHTML = "";
  if (counter.size === 0) {
    const li = document.createElement("li");
    li.textContent = "無獎項資料";
    awardsListEl.appendChild(li);
    return;
  }

  [...counter.entries()].forEach(([desc, count]) => {
    const li = document.createElement("li");
    li.textContent = `${desc} ×${count}`;
    awardsListEl.appendChild(li);
  });
}

function renderChart(fullName, seasonTrends = []) {
  const canvas = document.getElementById("season-chart");
  if (!canvas || typeof Chart === "undefined") return;

  if (seasonChart) {
    seasonChart.destroy();
  }
  const labels = seasonTrends.map((item) => item.season);
  const pts = seasonTrends.map((item) => item.pts_avg ?? 0);
  const reb = seasonTrends.map((item) => item.reb_avg ?? 0);
  const ast = seasonTrends.map((item) => item.ast_avg ?? 0);

  chartTitleEl.textContent = `${fullName} 生涯每季場均數據（例行賽）`;
  seasonChart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "場均得分", data: pts, borderColor: "#ff6b81", backgroundColor: "#ff6b81", tension: 0.25 },
        { label: "場均籃板", data: reb, borderColor: "#4ecdc4", backgroundColor: "#4ecdc4", tension: 0.25 },
        { label: "場均助攻", data: ast, borderColor: "#ffe66d", backgroundColor: "#ffe66d", tension: 0.25 },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#eaeaea" } } },
      scales: {
        x: { ticks: { color: "#b8bfd0" }, grid: { color: "#36547d" } },
        y: { ticks: { color: "#b8bfd0" }, grid: { color: "#36547d" } },
      },
    },
  });
}

function renderVsTable(regular = {}, playoff = {}) {
  const rows = [
    ["pts_avg", "場均得分", ""],
    ["reb_avg", "場均籃板", ""],
    ["ast_avg", "場均助攻", ""],
    ["stl_avg", "場均抄截", ""],
    ["blk_avg", "場均阻攻", ""],
    ["fg_pct", "FG%", "%"],
    ["fg3_pct", "3P%", "%"],
    ["ft_pct", "FT%", "%"],
  ];
  vsTableBodyEl.innerHTML = "";
  rows.forEach(([key, label, suffix]) => {
    const tr = document.createElement("tr");
    const tdReg = document.createElement("td");
    const tdLabel = document.createElement("td");
    const tdPlay = document.createElement("td");
    tdReg.className = "regular";
    tdLabel.className = "label";
    tdPlay.className = "playoff";
    tdReg.textContent = `${regular[key] ?? 0}${suffix}`;
    tdLabel.textContent = label;
    tdPlay.textContent = `${playoff[key] ?? 0}${suffix}`;
    tr.append(tdReg, tdLabel, tdPlay);
    vsTableBodyEl.appendChild(tr);
  });
}

function renderPlayer(data) {
  playerTitleEl.textContent = data.full_name || "查詢結果";
  awardsTitleEl.textContent = `${data.full_name || "球員"} 生涯榮譽`;
  playerImageEl.src = `https://cdn.nba.com/headshots/nba/latest/1040x760/${data.player_id}.png`;
  playerImageEl.onerror = () => {
    playerImageEl.src = "";
  };
  setText("team", data.team);
  setText("position", data.position);
  setText("height", data.height);
  setText("weight", data.weight);
  setText("age", data.age);
  setText("gp_total", data.gp_total);
  setText("pts_avg", data.pts_avg);
  setText("reb_avg", data.reb_avg);
  setText("ast_avg", data.ast_avg);
  setText("stl_avg", data.stl_avg);
  setText("blk_avg", data.blk_avg);
  setText("fg_pct", data.fg_pct, "%");
  setText("fg3_pct", data.fg3_pct, "%");
  setText("ft_pct", data.ft_pct, "%");
  setText("draft_year", data.draft_year);
  setText("draft_pick", data.draft_pick);
  setText("draft_team", data.draft_team);
  renderAwards(data.awards);
  renderChart(data.full_name || "球員", data.season_trends || []);
  renderVsTable(data.regular_vs_playoff?.regular || {}, data.regular_vs_playoff?.playoff || {});
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = input.value.trim();
  if (!name) return;

  statusEl.textContent = "🔍 搜尋中...";
  emptyResultEl.classList.remove("hidden");
  playerResultEl.classList.add("hidden");

  try {
    const data = await fetchPlayer(name);
    statusEl.textContent = "✅ 查詢完成";
    renderPlayer(data);
    emptyResultEl.classList.add("hidden");
    playerResultEl.classList.remove("hidden");
  } catch (error) {
    statusEl.textContent = "❌ 查詢失敗";
    playerTitleEl.textContent = "結果";
    emptyResultEl.textContent = error.message;
    emptyResultEl.classList.remove("hidden");
    playerResultEl.classList.add("hidden");
  }
});
