# scrape_api.py  — v1.2.1 (clean)
import os, json, logging
from typing import List
from fastapi import FastAPI, Query, HTTPException
from facebook_scraper import get_posts, _scraper

logger = logging.getLogger("uvicorn.error")

# ── mbasic headers (tùy chọn) ───────────────────────────────────────────────────
hdr_path = os.getenv("MBASIC_HEADERS", "mbasic_headers.json")
if os.path.exists(hdr_path):
    try:
        with open(hdr_path, encoding="utf-8") as f:
            _scraper.mbasic_headers = json.load(f)
    except Exception as e:
        logger.warning("Cannot load mbasic_headers.json: %s", e)

app = FastAPI()


def _resolve_cookie_path(path: str) -> str:
    """Trả về đường dẫn cookie hợp lệ (root hoặc /etc/secrets)."""
    if os.path.exists(path):
        return path
    secret = f"/etc/secrets/{os.path.basename(path)}"
    return secret if os.path.exists(secret) else ""


def latest_post(profile: str, limit: int = 1, cookies: str = "cookies.json") -> List[dict]:
    """Lấy tối đa <limit> bài mới nhất của <profile>."""
    cookie_path = _resolve_cookie_path(cookies)
    if not cookie_path:
        raise FileNotFoundError("cookies.json not found in project root hoặc /etc/secrets")
    logger.info(">>> USING COOKIE FILE: %s", cookie_path)
    start_url = f"https://mbasic.facebook.com/{profile}"
    gen = get_posts(
        profile,
        pages=7,
        cookies=cookie_path,
        base_url="https://mbasic.facebook.com",
        start_url=start_url,
        options={"allow_extra_requests": True,
                 "posts_per_page": 30,},
    )

    posts: List[dict] = []
    for post in gen:
        posts.append(
            {
                "profile": profile,
                "post_id": post.get("post_id"),
                "content": post.get("text") or "",
                "images": post.get("images", []) or ([post.get("image")] if post.get("image") else []),
                "created": post.get("time").isoformat() if post.get("time") else None,
            }
        )
        if len(posts) >= limit:
            break
    return posts


@app.get("/scrape")
def scrape(
    profile: str = Query(..., description="Username hoặc ID"),
    limit: int = Query(1, ge=1, le=5),
    cookies: str = Query("cookies.json"),
):
    try:
        return latest_post(profile, limit, cookies)
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as exc:
        logger.exception("Scrape error for %s", profile)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/")
def root():
    return {"status": "ok"}
