from fastapi import APIRouter, HTTPException
from nba_api.stats.endpoints import commonteamroster, leaguestandings
from nba_api.stats.static import teams


router = APIRouter(tags=["team"])


@router.get("/teams")
def get_teams() -> dict:
    all_teams = teams.get_teams()
    rows = [
        {
            "id": t["id"],
            "abbr": t["abbreviation"],
            "name": t["full_name"],
            "city": t["city"],
            "nickname": t["nickname"],
        }
        for t in all_teams
    ]
    rows.sort(key=lambda row: row["abbr"])
    return {"teams": rows}


@router.get("/team/{team_abbr}")
def get_team_info(team_abbr: str, season: str = "2025-26") -> dict:
    abbr = team_abbr.upper().strip()
    t = next((row for row in teams.get_teams() if row["abbreviation"] == abbr), None)
    if not t:
        raise HTTPException(status_code=404, detail=f"找不到球隊：{abbr}")

    team_id = t["id"]
    team_name = t["full_name"]

    roster_resp = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
    roster_df = roster_resp.get_data_frames()[0]
    coach_df = roster_resp.get_data_frames()[1]

    standings_resp = leaguestandings.LeagueStandings(season=season)
    standings_df = standings_resp.get_data_frames()[0]
    standing_row = standings_df[standings_df["TeamID"] == team_id]
    standing = {}
    if not standing_row.empty:
        row = standing_row.iloc[0]
        standing = {
            "wins": int(row.get("WINS", 0)),
            "losses": int(row.get("LOSSES", 0)),
            "win_pct": float(row.get("WinPCT", 0)),
            "conference": row.get("Conference", "未知"),
            "conference_rank": row.get("ConferenceRank", "未知"),
        }

    roster_cols = ["PLAYER_ID", "PLAYER", "NUM", "POSITION", "HEIGHT", "WEIGHT", "AGE", "EXP", "SCHOOL"]
    roster_view = roster_df[roster_cols].fillna("") if not roster_df.empty else roster_df
    roster = roster_view.to_dict(orient="records")

    coaches = []
    if not coach_df.empty:
        for _, r in coach_df.iterrows():
            coaches.append(
                {
                    "name": r.get("COACH_NAME", ""),
                    "role": r.get("COACH_TYPE", ""),
                    "is_assistant": bool(r.get("IS_ASSISTANT", 0)),
                }
            )

    return {
        "team": {"id": team_id, "abbr": abbr, "name": team_name},
        "season": season,
        "standing": standing,
        "coaches": coaches,
        "roster": roster,
    }
