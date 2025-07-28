from fastapi import FastAPI
from facebook_scraper import get_posts

app = FastAPI()

@app.get("/scrape")
def scrape(
    profile: str,
    limit: int = 1,
    cookies: str = "cookies.json",
):
    posts = []
    for post in get_posts(profile, pages=1, cookies=cookies,
                          options={"allow_extra_requests": False}):
        posts.append({
            "profile": profile,
            "post_id": post["post_id"],
            "content": post["text"] or "",
            "images": post.get("images", []) or ([post["image"]] if post.get("image") else []),
            "created": post["time"].isoformat() if post["time"] else None
        })
        if len(posts) >= limit:
            break
    return posts
@app.get("/")
def read_root():
    return {"message": "API đang chạy ok"}