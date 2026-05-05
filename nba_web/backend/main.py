from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routers import compare, history, player, quiz, team


app = FastAPI(title="NBA Web API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(player.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(team.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "assets")), name="assets")
app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}
