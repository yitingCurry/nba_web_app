from fastapi import APIRouter, HTTPException

from services.basicInfo import get_player_data


router = APIRouter(tags=["compare"])


@router.get("/compare")
def compare_players(player1: str, player2: str) -> dict:
    p1 = get_player_data(player1)
    p2 = get_player_data(player2)

    if not p1 and not p2:
        raise HTTPException(status_code=404, detail="兩位球員都找不到。")
    if not p1:
        raise HTTPException(status_code=404, detail=f"找不到球員：{player1}")
    if not p2:
        raise HTTPException(status_code=404, detail=f"找不到球員：{player2}")

    metrics = [
        ("pts_avg", "場均得分"),
        ("reb_avg", "場均籃板"),
        ("ast_avg", "場均助攻"),
        ("stl_avg", "場均抄截"),
        ("blk_avg", "場均阻攻"),
        ("fg_pct", "FG%"),
        ("fg3_pct", "3P%"),
        ("ft_pct", "FT%"),
    ]

    rows = []
    p1_win = 0
    p2_win = 0

    for key, label in metrics:
        v1 = float(p1.get(key, 0))
        v2 = float(p2.get(key, 0))
        if v1 > v2:
            winner = "player1"
            p1_win += 1
        elif v2 > v1:
            winner = "player2"
            p2_win += 1
        else:
            winner = "tie"
        rows.append({"key": key, "label": label, "player1": v1, "player2": v2, "winner": winner})

    return {
        "player1": p1,
        "player2": p2,
        "comparison_rows": rows,
        "score": {"player1": p1_win, "player2": p2_win},
    }
