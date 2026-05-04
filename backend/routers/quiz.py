from fastapi import APIRouter


router = APIRouter(tags=["quiz"])


@router.get("/quiz")
def quiz_stub() -> dict:
    return {"message": "TODO: implement quiz API"}
