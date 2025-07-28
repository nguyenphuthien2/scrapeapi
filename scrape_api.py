# Version 1.2 – Debug post raw server
# Giữ nguyên từ 1.1, thêm: in bài viết raw tại root để debug

from fastapi import FastAPI
from facebook_scraper import get_posts
import traceback
import json

app = FastAPI()

@app.get("/scrape")
def scrape(profile: str, limit: int = 1, cookies: str = "cookies.json"):
    try:
        posts = []
        for post in get_posts(profile, pages=1, cookies=cookies,
                              options={"allow_extra_requests": True}):
            posts.append({
                "profile": profile,
                "post_id": post["post_id"],
                "content": post["text"] or "",
                "images": post.get("images", []) or ([post["image"]] if post.get("image") else []),
                "created": post["time"].isoformat() if post["time"] else None
            })
            if len(posts) >= limit:
                break

        print(json.dumps(posts, indent=2, ensure_ascii=False))  # ✅ In ra để test trên server Render
        return posts

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/")
def read_root():
    profile = "tai.ngo.308279"
    cookies = "cookies.json"
    for post in get_posts(profile, pages=1, cookies=cookies, options={"allow_extra_requests": True}):
        print("== RAW ==")
        print(post)
        break
    return {"message": "API đang chạy ok"}
