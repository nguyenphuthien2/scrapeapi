from facebook_scraper import get_posts
import json

profile = "vnexpress"  # hoặc "zingnews", "thanhnien"
posts = []

for post in get_posts(profile, pages=2, options={
    "allow_extra_requests": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}):
    print("== Bài viết ==")
    print(post.get("text"))
    posts.append({
        "post_id": post["post_id"],
        "content": post["text"] or "",
        "images": post.get("images", []) or ([post["image"]] if post.get("image") else []),
        "created": post["time"].isoformat() if post["time"] else None
    })
    if len(posts) >= 3:
        break

print("== Kết quả JSON ==")
print(json.dumps(posts, indent=2, ensure_ascii=False))
