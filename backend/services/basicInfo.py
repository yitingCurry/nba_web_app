from datetime import datetime
import time

import pandas as pd
from nba_api.stats.endpoints import DraftHistory, commonplayerinfo, playerawards, playercareerstats, playergamelog
from nba_api.stats.static import players

from services.helpFunction import team_abbr_to_ch



def _safe_per_game(df: pd.DataFrame, made_col: str = "", att_col: str = "") -> float:
    if df.empty or "GP" not in df.columns:
        return 0.0
    gp = df["GP"].sum()
    if gp <= 0:
        return 0.0
    if made_col and att_col:
        att = df[att_col].sum() if att_col in df.columns else 0
        made = df[made_col].sum() if made_col in df.columns else 0
        return round((made / att) * 100, 1) if att > 0 else 0.0
    return 0.0


def _aggregate_vs_stats(df: pd.DataFrame) -> dict:
    if df.empty or "GP" not in df.columns or df["GP"].sum() <= 0:
        return {
            "pts_avg": 0.0,
            "reb_avg": 0.0,
            "ast_avg": 0.0,
            "stl_avg": 0.0,
            "blk_avg": 0.0,
            "fg_pct": 0.0,
            "fg3_pct": 0.0,
            "ft_pct": 0.0,
        }
    gp = df["GP"].sum()
    return {
        "pts_avg": round(df["PTS"].sum() / gp, 1) if "PTS" in df.columns else 0.0,
        "reb_avg": round(df["REB"].sum() / gp, 1) if "REB" in df.columns else 0.0,
        "ast_avg": round(df["AST"].sum() / gp, 1) if "AST" in df.columns else 0.0,
        "stl_avg": round(df["STL"].sum() / gp, 1) if "STL" in df.columns else 0.0,
        "blk_avg": round(df["BLK"].sum() / gp, 1) if "BLK" in df.columns else 0.0,
        "fg_pct": _safe_per_game(df, "FGM", "FGA"),
        "fg3_pct": _safe_per_game(df, "FG3M", "FG3A"),
        "ft_pct": _safe_per_game(df, "FTM", "FTA"),
    }


def get_basic_info(player_id, is_active):
    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    df_info = info.get_data_frames()[0]

    height = df_info.at[0, "HEIGHT"] if "HEIGHT" in df_info.columns else None
    if height and "-" in str(height):
        try:
            feet, inches = str(height).split("-")
            height_cm = int(feet) * 30.48 + int(inches) * 2.54
            height_str = f"{round(height_cm, 1)} cm"
        except Exception:
            height_str = "未知"
    else:
        height_str = "未知"

    weight = "未知"
    if "WEIGHT" in df_info.columns and pd.notna(df_info.at[0, "WEIGHT"]):
        try:
            weight = f"{round(int(df_info.at[0, 'WEIGHT']) * 0.453592, 1)} kg"
        except Exception:
            weight = "未知"

    age = "未知"
    if "BIRTHDATE" in df_info.columns and pd.notna(df_info.at[0, "BIRTHDATE"]):
        try:
            birthdate_dt = datetime.strptime(str(df_info.at[0, "BIRTHDATE"]).split("T")[0], "%Y-%m-%d")
            today = datetime.today()
            age = today.year - birthdate_dt.year - ((today.month, today.day) < (birthdate_dt.month, birthdate_dt.day))
        except Exception:
            age = "未知"

    if is_active is not None:
        is_retired = not bool(is_active)
    else:
        team_abbr_raw = df_info.at[0, "TEAM_ABBREVIATION"] if "TEAM_ABBREVIATION" in df_info.columns else None
        team_id = df_info.at[0, "TEAM_ID"] if "TEAM_ID" in df_info.columns else None
        is_retired = team_abbr_raw is None or str(team_abbr_raw).strip() == ""
        if team_id is not None:
            try:
                if int(team_id) == 0:
                    is_retired = True
            except Exception:
                pass

    team_display = (
        "已退役"
        if is_retired
        else team_abbr_to_ch(df_info.at[0, "TEAM_ABBREVIATION"] if "TEAM_ABBREVIATION" in df_info.columns else None)
    )

    try:
        draft = DraftHistory()
        df_draft = draft.get_data_frames()[0] if draft.get_data_frames() else pd.DataFrame()
        player_draft = df_draft[df_draft["PERSON_ID"] == player_id] if not df_draft.empty else pd.DataFrame()
        if player_draft.empty:
            draft_year = "未知"
            draft_pick = "-"
            draft_team = "未知"
        else:
            row = player_draft.iloc[0]
            draft_year = int(row.get("SEASON")) if row.get("SEASON") is not None else "未知"
            draft_pick = int(row.get("OVERALL_PICK")) if row.get("OVERALL_PICK") is not None else "-"
            draft_team = team_abbr_to_ch(row.get("TEAM_ABBREVIATION"))
    except Exception:
        draft_year = "未知"
        draft_pick = "-"
        draft_team = "未知"

    return {
        "team": team_display,
        "position": df_info.at[0, "POSITION"] if "POSITION" in df_info.columns else "未知",
        "height": height_str,
        "weight": weight,
        "age": age,
        "draft_year": draft_year,
        "draft_pick": draft_pick,
        "draft_team": draft_team,
    }


def get_career_stats(player_id):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df1 = career.get_data_frames()[1] if len(career.get_data_frames()) > 1 else pd.DataFrame()
    df3 = career.get_data_frames()[3] if len(career.get_data_frames()) > 3 else pd.DataFrame()
    df_career = pd.concat([df1, df3], ignore_index=True) if not df1.empty or not df3.empty else pd.DataFrame()

    gp_sum = df_career["GP"].sum() if not df_career.empty else 0
    pts_avg = round(df_career["PTS"].sum() / gp_sum, 1) if gp_sum > 0 else 0.0
    reb_avg = round(df_career["REB"].sum() / gp_sum, 1) if gp_sum > 0 else 0.0
    ast_avg = round(df_career["AST"].sum() / gp_sum, 1) if gp_sum > 0 else 0.0
    stl_avg = round(df_career["STL"].sum() / gp_sum, 1) if gp_sum > 0 else 0.0
    blk_avg = round(df_career["BLK"].sum() / gp_sum, 1) if gp_sum > 0 else 0.0
    fg_pct = round((df_career["FGM"].sum() / df_career["FGA"].sum()) * 100, 1) if not df_career.empty and df_career["FGA"].sum() > 0 else 0.0
    fg3_pct = round((df_career["FG3M"].sum() / df_career["FG3A"].sum()) * 100, 1) if not df_career.empty and df_career["FG3A"].sum() > 0 else 0.0
    ft_pct = round((df_career["FTM"].sum() / df_career["FTA"].sum()) * 100, 1) if not df_career.empty and df_career["FTA"].sum() > 0 else 0.0

    return {
        "pts_avg": pts_avg,
        "reb_avg": reb_avg,
        "ast_avg": ast_avg,
        "stl_avg": stl_avg,
        "blk_avg": blk_avg,
        "fg_pct": fg_pct,
        "fg3_pct": fg3_pct,
        "ft_pct": ft_pct,
        "gp_total": int(gp_sum),
    }


def get_chart_and_split_stats(player_id):
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    dfs = career.get_data_frames()
    df_season_regular = dfs[0] if len(dfs) > 0 else pd.DataFrame()
    df_totals_regular = dfs[1] if len(dfs) > 1 else pd.DataFrame()
    df_season_playoff = dfs[2] if len(dfs) > 2 else pd.DataFrame()
    df_totals_playoff = dfs[3] if len(dfs) > 3 else pd.DataFrame()

    season_trends = []
    if not df_season_regular.empty:
        for _, row in df_season_regular.iterrows():
            gp = row.get("GP", 0) or 0
            season_id = str(row.get("SEASON_ID", ""))
            if len(season_id) >= 8:
                season_label = f"{season_id[:4]}-{season_id[4:]}"
            else:
                season_label = season_id
            season_trends.append(
                {
                    "season": season_label,
                    "pts_avg": round((row.get("PTS", 0) or 0) / gp, 1) if gp > 0 else 0.0,
                    "reb_avg": round((row.get("REB", 0) or 0) / gp, 1) if gp > 0 else 0.0,
                    "ast_avg": round((row.get("AST", 0) or 0) / gp, 1) if gp > 0 else 0.0,
                }
            )

    return {
        "season_trends": season_trends,
        "regular_vs_playoff": {
            "regular": _aggregate_vs_stats(df_totals_regular),
            "playoff": _aggregate_vs_stats(df_totals_playoff if not df_totals_playoff.empty else df_season_playoff),
        },
    }


def get_player_awards(player_id):
    time.sleep(0.3)
    awards = playerawards.PlayerAwards(player_id=player_id)
    df_awards = awards.get_data_frames()[0]
    return df_awards.to_dict(orient="records")


def get_recent_games_and_season_stats(player_id: int, season: str = "2025-26") -> dict:
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season, season_type_all_star="Regular Season")
        df_games = gamelog.get_data_frames()[0]
    except Exception:
        df_games = pd.DataFrame()

    if df_games.empty:
        return {"season_stats": {}, "recent_games": []}

    numeric_cols = ["PTS", "REB", "AST", "STL", "BLK", "FG_PCT", "FG3_PCT", "FT_PCT", "PLUS_MINUS"]
    for col in numeric_cols:
        if col in df_games.columns:
            df_games[col] = pd.to_numeric(df_games[col], errors="coerce").fillna(0)

    season_stats = {
        "pts_avg": round(df_games["PTS"].mean(), 1) if "PTS" in df_games.columns else 0.0,
        "reb_avg": round(df_games["REB"].mean(), 1) if "REB" in df_games.columns else 0.0,
        "ast_avg": round(df_games["AST"].mean(), 1) if "AST" in df_games.columns else 0.0,
        "stl_avg": round(df_games["STL"].mean(), 1) if "STL" in df_games.columns else 0.0,
        "blk_avg": round(df_games["BLK"].mean(), 1) if "BLK" in df_games.columns else 0.0,
        "fg_pct": round(df_games["FG_PCT"].mean() * 100, 1) if "FG_PCT" in df_games.columns else 0.0,
        "fg3_pct": round(df_games["FG3_PCT"].mean() * 100, 1) if "FG3_PCT" in df_games.columns else 0.0,
        "ft_pct": round(df_games["FT_PCT"].mean() * 100, 1) if "FT_PCT" in df_games.columns else 0.0,
        "games": int(len(df_games)),
    }

    show_cols = ["GAME_DATE", "MATCHUP", "WL", "PTS", "REB", "AST", "STL", "BLK", "PLUS_MINUS"]
    existing_cols = [col for col in show_cols if col in df_games.columns]
    recent_df = df_games[existing_cols].head(5)
    recent_games = recent_df.to_dict(orient="records")

    return {"season_stats": season_stats, "recent_games": recent_games}


def get_player_data(player_name_input, season: str = "2025-26"):
    nba_players = players.get_players()
    player = next((p for p in nba_players if p["full_name"].lower() == player_name_input.lower()), None)
    if not player:
        return None
    

    player_id = player["id"]
    is_active_flag = player.get("is_active", None)

    try:
        print("enter basic ok")
        basic_info = get_basic_info(player_id, is_active=is_active_flag)
        print("basic ok")
        career_stats = get_career_stats(player_id)
        chart_and_split_stats = get_chart_and_split_stats(player_id)
        awards = get_player_awards(player_id)
        recent_data = get_recent_games_and_season_stats(player_id, season=season)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"NBA API error for player={player_name_input}, season={season}")
        return None

    return {
        "player_id": player_id,
        "full_name": player["full_name"],
        **basic_info,
        **career_stats,
        **chart_and_split_stats,
        "awards": awards,
        "season": season,
        **recent_data,
    }
