# Version 1.2 – cookie fallback + debug
# Giữ nguyên từ 1.1, thêm:
# - Tự tìm cookies.json ở project root hoặc /etc/secrets/ (Render Secret File).
# - Ghi log cảnh báo nếu không tìm thấy cookie.
# - Trả HTTP 500 rõ nghĩa khi thiếu cookie.

import os
import json
import logging
from typing import List

from fastapi import FastAPI, Query, HTTPException
from facebook_scraper import get_posts, _scraper

logger = logging.getLogger("uvicorn.error")

# Load mbasic headers (nếu có)
headers_path = os.getenv("MBASIC_HEADERS", "mbasic_headers.json")
if os.path.exists(headers_path):
    try:
        with open(headers_path, "r", encoding="utf-8") as f:
            _scraper.mbasic_headers = json.load(f)
    except Exception as e:
        logger.warning("Cannot load mbasic_headers.json: %s", e)

app = FastAPI()


def _resolve_cookie_path(path: str) -> str:
    """Tìm file cookie tại path, hoặc fallback /etc/secrets."""
    if os.path.exists(path):
        return path
    secret_path = f"/etc/secrets/{os.path.basename(path)}"
    if os.path.exists(secret_path):
        return secret_path
    return ""  # not found


def latest_post(profile: str, limit: int = 1, cookies: str = "cookies.json") -> List[dict]:
    cookie_path = _resolve_cookie_path(cookies)
    if not cookie_path:
        logger.error("Cookie file %s not found", cookies)
        raise FileNotFoundError("cookies.json not found in project root or /etc/secrets")

    start_url = f"https://mbasic.facebook.com/{profile}?v=timeline"
    gen = get_posts(
        profile,
        pages=1,
        cookies=cookie_path,
        base_url="https://mbasic.facebook.com",
        start_url=start_url,
        options={"allow_extra_requests": False},
    )
    posts = []
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
    profile: str = Query(..., description="Profile username hoặc ID"),
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
