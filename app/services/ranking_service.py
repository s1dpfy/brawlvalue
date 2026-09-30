from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# 루트 디렉토리 및 키 파일 경로
BASE_DIR = Path(__file__).resolve().parent.parent.parent
KEY_PATH = BASE_DIR / "serviceAccountKey.json"

db = None

if KEY_PATH.exists():
    try:
        # 중복 초기화 방지
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(KEY_PATH))
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("[Firebase] Firestore 연결 완료")
    except Exception as e:
        print(f"[Firebase 초기화 실패] {e}")
else:
    print("[경고] serviceAccountKey.json 파일이 없습니다. 랭킹 기능이 비활성화됩니다.")


def save_player_ranking(clean_tag: str, player: dict, analysis: dict):
    """서버에서 검증된 점수만 안전하게 DB에 저장"""
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
    """실시간 전체 랭킹 조회 (limit가 None이면 전체 반환)"""
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