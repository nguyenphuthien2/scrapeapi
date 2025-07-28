# Version 1.3 – Fix đọc cookie từ file json dạng list
# Giữ nguyên từ 1.2, sửa: đọc cookies.json đúng định dạng list cookie

from fastapi import FastAPI
from facebook_scraper import get_posts
import traceback
import json

app = FastAPI()

@app.get("/scrape")
def scrape(profile: str, limit: int = 1, cookies_file: str = "cookies.json"):
    try:
        with open(cookies_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cookies = {item["name"]: item["value"] for item in raw}

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
    try:
        profile = "tai.ngo.308279"
        with open("cookies.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        cookies = {item["name"]: item["value"] for item in raw}

        for post in get_posts(profile, pages=1, cookies=cookies, options={"allow_extra_requests": True}):
            print("== RAW ==")
            print(post)
            break
    except Exception as e:
        print("Lỗi khi test profile mặc định:", e)
    return {"message": "API đang chạy ok"}
