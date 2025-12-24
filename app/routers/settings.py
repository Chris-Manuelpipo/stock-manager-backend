from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/")
def get_settings():
    return {"message": "Settings endpoint"}