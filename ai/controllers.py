from fastapi import APIRouter, Request
from ai.services import generate_insight

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/api/insight")
async def insight_route(request: Request):
    data = await request.json()
    portfolio = data.get("portfolio", [])
    result = await generate_insight(portfolio)
    return {"text": result}
