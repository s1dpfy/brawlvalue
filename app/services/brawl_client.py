from urllib.parse import quote
import httpx
from app.config import BRAWL_API_KEY, ROYALE_API_PROXY_URL


class BrawlAPIClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {BRAWL_API_KEY}",
            "Accept": "application/json",
        }

    async def fetch_player(self, tag: str) -> dict:
        if not BRAWL_API_KEY:
            return {"error": "서버에 API 키가 설정되지 않았습니다.", "status": 500}

        # # 기호 제거 및 URL 인코딩 (%23)
        clean_tag = tag.replace("#", "").strip().upper()
        encoded_tag = quote(f"#{clean_tag}")
        url = f"{ROYALE_API_PROXY_URL}/{encoded_tag}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url, headers=self.headers)
            except httpx.RequestError as exc:
                return {"error": f"네트워크 통신 오류: {exc}", "status": 500}

        if response.status_code == 404:
            return {"error": "플레이어를 찾을 수 없습니다. 태그를 확인하세요.", "status": 404}
        if response.status_code == 403:
            return {"error": "API 키 인증 실패 또는 IP 차단입니다.", "status": 403}
        if response.status_code != 200:
            return {"error": f"슈퍼셀 서버 오류 (코드: {response.status_code})", "status": response.status_code}

        return {"data": response.json(), "status": 200}