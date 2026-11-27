from fastapi import APIRouter


router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/ask")
def agent_ask():
    pass