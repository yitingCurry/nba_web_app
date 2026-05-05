const teamForm = document.getElementById("team-form");
const teamSelectEl = document.getElementById("team-select");
const teamSeasonEl = document.getElementById("team-season");
const teamStatusEl = document.getElementById("team-status");
const teamEmptyEl = document.getElementById("team-empty");
const teamResultEl = document.getElementById("team-result");
const teamTitleEl = document.getElementById("team-title");
const teamStandingEl = document.getElementById("team-standing");
const teamCoachesEl = document.getElementById("team-coaches");
const teamPlayerGridEl = document.getElementById("team-player-grid");
const teamPlayerDetailEl = document.getElementById("team-player-detail");
const teamDetailImageEl = document.getElementById("team-detail-image");
const teamDetailNameEl = document.getElementById("team-detail-name");
const teamDetailMetaEl = document.getElementById("team-detail-meta");
const teamDetailDraftEl = document.getElementById("team-detail-draft");
const teamDetailSeasonTitleEl = document.getElementById("team-detail-season-title");
const teamDetailSeasonStatsEl = document.getElementById("team-detail-season-stats");
const teamDetailGamesEl = document.getElementById("team-detail-games");

let teamReady = false;
let teamListReady = false;

const API_BASE = 'https://nba-web-app-5.onrender.com';

async function fetchTeams() {
  const resp = await fetch(`${API_BASE}/api/teams`);
  if (!resp.ok) throw new Error("無法載入球隊清單");
  return resp.json();
}

async function fetchTeamInfo(abbr, season) {
  const resp = await fetch(`${API_BASE}/api/team/${encodeURIComponent(abbr)}?season=${encodeURIComponent(season)}`);
  if (!resp.ok) {
    const msg = await resp.text();
    throw new Error(msg || "無法載入球隊資料");
  }
  return resp.json();
}

async function fetchPlayerDetail(name, season) {
  const resp = await fetch(`${API_BASE}/api/player/${encodeURIComponent(name)}?season=${encodeURIComponent(season)}`);
  if (!resp.ok) throw new Error("無法載入球員資料");
  return resp.json();
}

function renderTeamOptions(teams) {
  teamSelectEl.innerHTML = "";
  teams.forEach((team) => {
    const option = document.createElement("option");
    option.value = team.abbr;
    option.textContent = `${team.abbr} - ${team.name}`;
    teamSelectEl.appendChild(option);
  });
  if (!teamSelectEl.value && teams.length > 0) {
    teamSelectEl.value = "LAL";
  }
}

function renderTeam(data) {
  const { team, season, standing, coaches, roster } = data;
  teamTitleEl.textContent = `${team.name} (${team.abbr}) - ${season}`;
  teamStandingEl.textContent = standing && Object.keys(standing).length
    ? `戰績 ${standing.wins}-${standing.losses} (${(standing.win_pct * 100).toFixed(1)}%) | ${standing.conference} 第 ${standing.conference_rank}`
    : "暫無戰績資料";

  teamCoachesEl.innerHTML = "";
  if (!coaches || coaches.length === 0) {
    teamCoachesEl.innerHTML = "<li>無教練資料</li>";
  } else {
    coaches.forEach((coach) => {
      const li = document.createElement("li");
      li.textContent = `${coach.name} - ${coach.role || "教練"}`;
      teamCoachesEl.appendChild(li);
    });
  }

  teamPlayerGridEl.innerHTML = "";
  teamPlayerDetailEl.classList.add("hidden");
  if (!roster || roster.length === 0) {
    teamPlayerGridEl.innerHTML = `<p>無球員名單</p>`;
  } else {
    roster.forEach((player) => {
      const btn = document.createElement("button");
      btn.className = "team-player-btn";
      btn.type = "button";
      const playerId = player.PLAYER_ID || "";
      const imgSrc = playerId ? `https://cdn.nba.com/headshots/nba/latest/1040x760/${playerId}.png` : "";
      btn.innerHTML = `
        <img src="${imgSrc}" alt="${player.PLAYER || ""}" onerror="this.style.display='none'" />
        <strong>${player.PLAYER || "-"}</strong>
        <span>${player.POSITION || "-"} | #${player.NUM || "-"}</span>
      `;
      btn.addEventListener("click", async () => {
        teamStatusEl.textContent = `🔍 載入 ${player.PLAYER} ...`;
        try {
          const detail = await fetchPlayerDetail(player.PLAYER, season);
          renderTeamPlayerDetail(detail);
          teamStatusEl.textContent = `✅ 已載入 ${player.PLAYER}`;
        } catch (error) {
          teamStatusEl.textContent = `❌ ${error.message}`;
        }
      });
      teamPlayerGridEl.appendChild(btn);
    });
  }
}

function renderTeamPlayerDetail(data) {
  teamPlayerDetailEl.classList.remove("hidden");
  teamDetailNameEl.textContent = data.full_name || "";
  teamDetailMetaEl.textContent = `目前球隊: ${data.team} | 位置: ${data.position} | 身高: ${data.height} | 體重: ${data.weight} | 年齡: ${data.age}`;
  teamDetailDraftEl.textContent = `選秀資訊: ${data.draft_year} 年 | ${data.draft_team} | 第 ${data.draft_pick} 順位`;
  teamDetailSeasonTitleEl.textContent = `${data.season || ""} 賽季個人數據`;
  teamDetailImageEl.src = `https://cdn.nba.com/headshots/nba/latest/1040x760/${data.player_id}.png`;
  teamDetailImageEl.onerror = () => {
    teamDetailImageEl.src = "";
  };

  const seasonStats = data.season_stats || {};
  teamDetailSeasonStatsEl.innerHTML = `
    <div>場均得分 <strong>${seasonStats.pts_avg ?? 0}</strong></div>
    <div>場均籃板 <strong>${seasonStats.reb_avg ?? 0}</strong></div>
    <div>場均助攻 <strong>${seasonStats.ast_avg ?? 0}</strong></div>
    <div>場均抄截 <strong>${seasonStats.stl_avg ?? 0}</strong></div>
    <div>場均阻攻 <strong>${seasonStats.blk_avg ?? 0}</strong></div>
    <div>投籃命中率 <strong>${seasonStats.fg_pct ?? 0}%</strong></div>
    <div>三分命中率 <strong>${seasonStats.fg3_pct ?? 0}%</strong></div>
    <div>罰球命中率 <strong>${seasonStats.ft_pct ?? 0}%</strong></div>
    <div>出賽場次 <strong>${seasonStats.games ?? 0}</strong></div>
  `;

  const games = data.recent_games || [];
  teamDetailGamesEl.innerHTML = "";
  if (!games.length) {
    teamDetailGamesEl.innerHTML = `<tr><td colspan="9">無近期比賽資料</td></tr>`;
    return;
  }
  games.forEach((g) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${g.GAME_DATE || "-"}</td>
      <td>${g.MATCHUP || "-"}</td>
      <td>${g.WL || "-"}</td>
      <td>${g.PTS ?? "-"}</td>
      <td>${g.REB ?? "-"}</td>
      <td>${g.AST ?? "-"}</td>
      <td>${g.STL ?? "-"}</td>
      <td>${g.BLK ?? "-"}</td>
      <td>${g.PLUS_MINUS ?? "-"}</td>
    `;
    teamDetailGamesEl.appendChild(tr);
  });
}

async function ensureTeamList() {
  if (teamListReady) return;
  const data = await fetchTeams();
  renderTeamOptions(data.teams || []);
  teamListReady = true;
}

async function loadTeam(abbr, season) {
  teamStatusEl.textContent = "🔍 載入中...";
  try {
    const data = await fetchTeamInfo(abbr, season);
    renderTeam(data);
    teamStatusEl.textContent = "✅ 載入完成";
    teamEmptyEl.classList.add("hidden");
    teamResultEl.classList.remove("hidden");
    teamReady = true;
  } catch (error) {
    teamStatusEl.textContent = "❌ 載入失敗";
    teamEmptyEl.textContent = error.message;
    teamEmptyEl.classList.remove("hidden");
    teamResultEl.classList.add("hidden");
  }
}

if (teamForm) {
  teamForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await ensureTeamList();
    await loadTeam(teamSelectEl.value, teamSeasonEl.value || "2025-26");
  });
}

const teamModeBtn = document.querySelector('.mode-btn[data-mode="team"]');
if (teamModeBtn) {
  teamModeBtn.addEventListener("click", async () => {
    await ensureTeamList();
    if (!teamReady) {
      await loadTeam(teamSelectEl.value || "LAL", teamSeasonEl.value || "2025-26");
    }
  });
}
