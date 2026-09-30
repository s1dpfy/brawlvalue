import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 비밀 키 탐색 우선순위
# 1. Render 클라우드 Secret Files 마운트 경로 (/etc/secrets/serviceAccountKey.json)
# 2. 환경변수 지정 경로 (FIREBASE_KEY_PATH 또는 GOOGLE_APPLICATION_CREDENTIALS)
# 3. 로컬 프로젝트 루트 경로
CANDIDATE_PATHS = [
    Path("/etc/secrets/serviceAccountKey.json"),
    Path(os.getenv("FIREBASE_KEY_PATH", "")),
    Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")),
    BASE_DIR / "serviceAccountKey.json",
    Path("serviceAccountKey.json"),
]


def resolve_key_path() -> Path | None:
    for path in CANDIDATE_PATHS:
        if str(path) and path.exists() and path.is_file():
            return path
    return None


KEY_PATH = resolve_key_path()
db = None

if KEY_PATH:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(KEY_PATH))
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print(f"[Firebase] Firestore 연결 완료 (Key 경로: {KEY_PATH})")
    except Exception as e:
        print(f"[Firebase 초기화 실패] {e}")
else:
    print("[경고] serviceAccountKey.json 키 파일을 찾을 수 없습니다. (확인 경로: /etc/secrets/, 프로젝트 루트)")


def save_player_ranking(clean_tag: str, player: dict, analysis: dict):
    """서버에서 검증된 유저 가치 데이터를 Firestore에 저장"""
    if not db:
        return
    try:
        doc_ref = db.collection("festival_ranking").document(clean_tag)
        doc_ref.set({
            "tag": f"#{clean_tag}",
            "name": player.get("name", "PLAYER"),
            "score": analysis["total_score"],
            "tier": analysis["tier"],
            "tier_kr": analysis["tier_kr"],
            "tier_style": analysis["tier_style"],
            "trophies": player.get("trophies", 0),
            "updated_at": firestore.SERVER_TIMESTAMP,
        }, merge=True)
    except Exception as e:
        print(f"[Firestore 저장 실패] {e}")


def get_top_rankings(limit: int = None):
    """실시간 랭킹 전체 조회"""
    if not db:
        return []
    try:
        query = db.collection("festival_ranking").order_by(
            "score", direction=firestore.Query.DESCENDING
        )
        if limit:
            query = query.limit(limit)

        docs = query.stream()
        rankings = []
        for doc in docs:
            data = doc.to_dict()
            tag = data.get("tag")
            if not tag or doc.id == "TEST":
                continue

            rankings.append({
                "tag": tag,
                "name": data.get("name", "PLAYER"),
                "score": data.get("score", 0),
                "tier": data.get("tier", "UNRANKED"),
                "tier_kr": data.get("tier_kr", "미배정"),
                "tier_style": data.get("tier_style", "border-slate-700 text-slate-300"),
                "trophies": data.get("trophies", 0),
            })
        return rankings
    except Exception as e:
        print(f"[Firestore 조회 실패] {e}")
        return []