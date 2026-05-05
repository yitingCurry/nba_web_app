from fastapi import APIRouter, HTTPException, Query

from services.basicInfo import get_player_data


router = APIRouter(tags=["player"])


@router.get("/player/{player_name}")
def get_single_player(player_name: str, season: str = Query(default="2025-26")) -> dict:
    try:
        data = get_player_data(player_name, season=season)
    except Exception as e:
        return -1

    if not data:
        raise HTTPException(status_code=404, detail="Player not found or data unavailable.")
    return data
