from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.brawl_client import BrawlAPIClient
from app.services.calculator import calculate_account_value
from app.services.ranking_service import save_player_ranking, get_top_rankings

app = FastAPI(title="Brawl Stars Account Value Analyzer")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
client = BrawlAPIClient()


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/api/player/{tag}")
async def analyze_player(tag: str):
    clean_tag = tag.replace("#", "").strip().upper()
    result = await client.fetch_player(clean_tag)
    
    if result.get("status") != 200:
        raise HTTPException(
            status_code=result.get("status", 500),
            detail=result.get("error", "알 수 없는 오류")
        )

    player_data = result["data"]
    analysis = calculate_account_value(player_data)

    # 서버에서 검증된 진짜 점수만 DB에 저장 (치팅 불가)
    save_player_ranking(clean_tag, player_data, analysis)

    return {
        "player": player_data,
        "analysis": analysis
    }


@app.get("/api/ranking")
async def get_ranking():
    return get_top_rankings(limit=None)