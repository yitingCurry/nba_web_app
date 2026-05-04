import pandas as pd
from fastapi import APIRouter, Query
from nba_api.stats.endpoints import leagueleaders
from nba_api.stats.static import players as static_players


router = APIRouter(tags=["history"])


METRIC_MAP = {
    "PTS": ("生涯總得分", "count"),
    "AST": ("生涯總助攻", "count"),
    "REB": ("生涯總籃板", "count"),
    "BLK": ("生涯總阻攻", "count"),
    "STL": ("生涯總抄截", "count"),
    "FG3M": ("生涯三分命中", "count"),
    "FG_PCT": ("投籃命中率", "percent"),
    "FG3_PCT": ("三分命中率", "percent"),
    "FT_PCT": ("罰球命中率", "percent"),
    "PTSAVG": ("場均得分", "avg_pts"),
    "ASTAVG": ("場均助攻", "avg_ast"),
    "REBAVG": ("場均籃板", "avg_reb"),
}

_PLAYER_ID_NAME_CACHE = {}
try:
    for player in static_players.get_players():
        pid = int(player.get("id"))
        _PLAYER_ID_NAME_CACHE[pid] = player.get("full_name")
except Exception:
    _PLAYER_ID_NAME_CACHE = {}


def _format_value(value: float, value_type: str) -> str:
    if value_type == "percent":
        return f"{float(value) * 100:.1f}%"
    if value_type.startswith("avg_"):
        return f"{float(value):.1f}"
    return f"{int(value):,}"


def _resolve_player_name(raw_name) -> str:
    if raw_name is None:
        return "Unknown"
    text = str(raw_name).strip()
    if text.isdigit():
        return _PLAYER_ID_NAME_CACHE.get(int(text), text)
    return text


@router.get("/history")
def get_history_ranking(
    metric: str = Query(default="PTS"),
    limit: int = Query(default=500, ge=10, le=500),
    q: str = Query(default=""),
) -> dict:
    metric = metric.upper()
    if metric not in METRIC_MAP:
        metric = "PTS"

    metric_label, value_type = METRIC_MAP[metric]
    stat_abbr = "PTS" if value_type.startswith("avg_") else metric
    avg_to_total = {"avg_pts": "PTS", "avg_ast": "AST", "avg_reb": "REB"}

    resp = leagueleaders.LeagueLeaders(
        stat_category_abbreviation=stat_abbr,
        league_id="00",
        season="All Time",
        per_mode48="Totals",
        scope="S",
        season_type_all_star="Regular Season",
    )
    df = resp.get_data_frames()[0]
    if df is None or df.empty:
        return {"metric": metric, "label": metric_label, "rows": [], "available_metrics": METRIC_MAP}

    name_col = "PLAYER" if "PLAYER" in df.columns else df.columns[0]

    if value_type.startswith("avg_"):
        total_col = avg_to_total.get(value_type, "PTS")
        if total_col not in df.columns or "GP" not in df.columns:
            rows = []
        else:
            df["GP"] = pd.to_numeric(df["GP"], errors="coerce").fillna(0)
            df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)
            df = df[df["GP"] >= 400]
            df[metric] = df.apply(lambda row: (row[total_col] / row["GP"]) if row["GP"] > 0 else 0.0, axis=1)
            df_sorted = df.sort_values(by=metric, ascending=False).head(limit)
            rows = [
                {
                    "rank": idx + 1,
                    "name": _resolve_player_name(row[name_col]),
                    "value": float(row[metric]),
                    "value_text": _format_value(row[metric], value_type),
                }
                for idx, (_, row) in enumerate(df_sorted.iterrows())
            ]
    else:
        val_col = metric if metric in df.columns else stat_abbr if stat_abbr in df.columns else None
        if not val_col:
            rows = []
        else:
            df_sorted = df.sort_values(by=val_col, ascending=False).head(limit)
            rows = [
                {
                    "rank": idx + 1,
                    "name": _resolve_player_name(row[name_col]),
                    "value": float(row[val_col]) if pd.notna(row[val_col]) else 0,
                    "value_text": _format_value(row[val_col], value_type) if pd.notna(row[val_col]) else "N/A",
                }
                for idx, (_, row) in enumerate(df_sorted.iterrows())
            ]

    if q.strip():
        needle = q.strip().lower()
        rows = [row for row in rows if needle in str(row["name"]).lower()]

    return {
        "metric": metric,
        "label": metric_label,
        "rows": rows,
        "available_metrics": METRIC_MAP,
    }
