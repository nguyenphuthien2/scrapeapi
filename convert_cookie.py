import json

with open("cookies.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

converted = {item["name"]: item["value"] for item in raw}

with open("cookies_converted.json", "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2)

print("✅ Đã chuyển cookie sang dạng dict.")
