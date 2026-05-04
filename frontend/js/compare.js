async function fetchComparison(player1, player2) {
  const url = `/api/compare?player1=${encodeURIComponent(player1)}&player2=${encodeURIComponent(player2)}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(msg || "比較失敗");
  }
  return resp.json();
}

function formatValue(key, value) {
  const isPct = ["fg_pct", "fg3_pct", "ft_pct"].includes(key);
  return isPct ? `${value}%` : `${value}`;
}

function renderAwardList(targetId, awards, emptyLabel = "無獎項資料") {
  const ul = document.getElementById(targetId);
  if (!ul) return;
  ul.innerHTML = "";

  const counter = new Map();
  (Array.isArray(awards) ? awards : []).forEach((item) => {
    const desc = item.DESCRIPTION || item.description || "未知獎項";
    counter.set(desc, (counter.get(desc) || 0) + 1);
  });

  if (counter.size === 0) {
    const li = document.createElement("li");
    li.textContent = emptyLabel;
    ul.appendChild(li);
    return;
  }

  [...counter.entries()].forEach(([desc, count]) => {
    const li = document.createElement("li");
    li.textContent = `${desc} ×${count}`;
    ul.appendChild(li);
  });
}

function renderCompareTop(data) {
  const p1 = data.player1;
  const p2 = data.player2;

  document.getElementById("compare-name-1").textContent = p1.full_name;
  document.getElementById("compare-name-2").textContent = p2.full_name;
  document.getElementById("compare-meta-1").textContent = `🏀 ${p1.team} | 🎯 ${p1.position} | 🎂 ${p1.age}\n📏 ${p1.height} | ⚖️ ${p1.weight}`;
  document.getElementById("compare-meta-2").textContent = `🏀 ${p2.team} | 🎯 ${p2.position} | 🎂 ${p2.age}\n📏 ${p2.height} | ⚖️ ${p2.weight}`;
  document.getElementById("compare-awards-title-1").textContent = `${p1.full_name} 生涯榮譽`;
  document.getElementById("compare-awards-title-2").textContent = `${p2.full_name} 生涯榮譽`;

  const img1 = document.getElementById("compare-img-1");
  const img2 = document.getElementById("compare-img-2");
  img1.src = `https://cdn.nba.com/headshots/nba/latest/1040x760/${p1.player_id}.png`;
  img2.src = `https://cdn.nba.com/headshots/nba/latest/1040x760/${p2.player_id}.png`;
  img1.onerror = () => (img1.src = "");
  img2.onerror = () => (img2.src = "");

  renderAwardList("compare-awards-1", p1.awards);
  renderAwardList("compare-awards-2", p2.awards);
}

function renderCompareTable(data) {
  const body = document.getElementById("duel-body");
  body.innerHTML = "";

  data.comparison_rows.forEach((row) => {
    const tr = document.createElement("tr");
    const left = document.createElement("td");
    const mid = document.createElement("td");
    const right = document.createElement("td");

    left.className = `player1 ${row.winner === "player1" ? "win" : ""}`;
    right.className = `player2 ${row.winner === "player2" ? "win" : ""}`;
    mid.className = "metric";

    left.textContent = formatValue(row.key, row.player1);
    mid.textContent = row.label;
    right.textContent = formatValue(row.key, row.player2);

    tr.append(left, mid, right);
    body.appendChild(tr);
  });

  document.getElementById("duel-head-1").textContent = data.player1.full_name;
  document.getElementById("duel-head-2").textContent = data.player2.full_name;
  document.getElementById("duel-score").textContent =
    `勝出項目：${data.player1.full_name} ${data.score.player1} 項，${data.player2.full_name} ${data.score.player2} 項`;
}

const compareForm = document.getElementById("compare-form");
if (compareForm) {
  compareForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const p1 = document.getElementById("compare-player1").value.trim();
    const p2 = document.getElementById("compare-player2").value.trim();
    if (!p1 || !p2) return;

    const status = document.getElementById("compare-status");
    const empty = document.getElementById("compare-empty");
    const result = document.getElementById("compare-result");
    status.textContent = "🔍 比較中...";

    try {
      const data = await fetchComparison(p1, p2);
      renderCompareTop(data);
      renderCompareTable(data);
      status.textContent = "✅ 比較完成";
      empty.classList.add("hidden");
      result.classList.remove("hidden");
    } catch (error) {
      status.textContent = "❌ 比較失敗";
      empty.textContent = error.message;
      empty.classList.remove("hidden");
      result.classList.add("hidden");
    }
  });
}
