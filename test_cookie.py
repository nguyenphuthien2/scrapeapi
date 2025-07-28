from facebook_scraper import get_posts
import traceback

profile = "phun.nguyendn"
cookies = "cookies_converted.json"

try:
    for post in get_posts(profile, pages=10, cookies=cookies, options={"allow_extra_requests": True}):
        print("== BÀI VIẾT ==")
        print(post)
        break
    else:
        print("⚠️ Không có bài viết nào được trả về.")
except Exception as e:
    print("❌ Lỗi xảy ra:")
    traceback.print_exc()
