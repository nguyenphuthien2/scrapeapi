# Version 1.1 – mbasic workaround
# Giữ nguyên từ 1.0, thêm:
# - Sử dụng fork facebook-scraper hỗ trợ mbasic.
# - Header di động tuỳ chỉnh để tránh checkpoint.
# - Thêm biến ENV MBASIC_HEADERS cho path.
# - Hàm latest_post(profile, limit=1).
# - Endpoint /scrape giống cũ nhưng gọi latest_post.
# Không thay đổi interface người dùng.

import os
import json
from typing import List

from fastapi import FastAPI, Query, HTTPException
from facebook_scraper import get_posts, _scraper

# Load mbasic headers (tuỳ chọn)
headers_path = os.getenv("MBASIC_HEADERS", "mbasic_headers.json")
if os.path.exists(headers_path):
    with open(headers_path, "r", encoding="utf-8") as f:
        try:
            _scraper.mbasic_headers = json.load(f)
        except json.JSONDecodeError:
            pass  # bỏ qua nếu file hỏng

app = FastAPI()


def latest_post(profile: str, limit: int = 1, cookies: str = "cookies.json") -> List[dict]:
    """
    Lấy <limit> bài mới nhất từ profile thông qua mbasic.facebook.com.
    """
    start_url = f"https://mbasic.facebook.com/{profile}?v=timeline"
    gen = get_posts(
        profile,
        pages=1,
        cookies=cookies,
        base_url="https://mbasic.facebook.com",
        start_url=start_url,
        options={"allow_extra_requests": False},
    )
    posts = []
    for post in gen:
        posts.append(
            {
                "profile": profile,
                "post_id": post["post_id"],
                "content": post.get("text") or "",
                "images": post.get("images", []) or ([post["image"]] if post.get("image") else []),
                "created": post["time"].isoformat() if post.get("time") else None,
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
    """
    Endpoint tương thích với Make.com:
    /scrape?profile=<id>&limit=1
    """
    if not profile:
        raise HTTPException(status_code=400, detail="Thiếu profile")
    try:
        return latest_post(profile, limit, cookies)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
