"""用 Google Places API (New) 查行程區域的餐廳，存成 data/google-places.json。

用法（金鑰只從環境變數讀，不寫進任何檔案）：
  GOOGLE_MAPS_API_KEY=... python3 tools/google_places.py
  python3 tools/google_places.py --offline   只用 google-places-raw.json 重新篩選，不打 API
輸出：
  data/google-places-raw.json  所有原始結果（快取，含百名店查詢）
  data/google-places.json      篩選後：評分 > 3.8、評價數 > 500、營業中、沒有被標「不適合小孩」
"""
import json, math, os, sys, time, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OFFLINE = "--offline" in sys.argv
RAW_PATH = os.path.join(ROOT, "data", "google-places-raw.json")
KEY = "" if OFFLINE else (os.environ.get("GOOGLE_MAPS_API_KEY") or sys.exit("請設定 GOOGLE_MAPS_API_KEY"))
ASOF = json.load(open(RAW_PATH))["asof"] if OFFLINE else time.strftime("%Y-%m-%d")
MIN_RATING, MIN_COUNT = 3.8, 500  # 「超過」：rating > 3.8 且 count > 500

FIELDS = ",".join(f"places.{f}" for f in [
    "id", "displayName", "formattedAddress", "location", "rating", "userRatingCount", "primaryType", "types",
    "goodForChildren", "businessStatus", "googleMapsUri", "regularOpeningHours.periods",
    "regularOpeningHours.weekdayDescriptions", "priceLevel"]) + ",nextPageToken"

# 區域：地標 → 半徑（公尺）。地標座標也用 Places API 取得。
AREAS = [
    ("st", "金沢駅 兼六園口", 600), ("omicho", "近江町市場", 300), ("higashi", "ひがし茶屋街", 400),
    ("korinbo", "香林坊 交差点", 650), ("nagamachi", "長町武家屋敷跡", 300),
    ("komatsu", "JR小松駅", 600), ("komatsu", "イオンモール新小松", 400), ("wakura", "和倉温泉 総湯", 700),
]
QUERIES = ["レストラン", "寿司", "海鮮丼", "ラーメン", "うどん そば", "カフェ", "スイーツ", "和菓子",
           "居酒屋", "洋食", "焼肉", "カレー", "パン", "定食"]

FOOD_HINTS = ("restaurant", "cafe", "coffee", "bakery", "dessert", "confectioner", "ice_cream", "tea_house",
              "meal_takeaway", "izakaya", "bar", "food_court", "sandwich", "diner", "cake", "donut", "noodle")
NOT_FOOD = {"lodging", "hotel", "japanese_inn", "supermarket", "grocery_store", "convenience_store",
            "shopping_mall", "department_store", "market", "tourist_attraction", "store", "gift_shop"}


def post(body):
    req = urllib.request.Request("https://places.googleapis.com/v1/places:searchText", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "X-Goog-Api-Key": KEY,
                                          "X-Goog-FieldMask": FIELDS})
    return json.load(urllib.request.urlopen(req, timeout=30))


def rect(lat, lng, r):
    dlat = r / 111_320
    dlng = r / (111_320 * math.cos(math.radians(lat)))
    return {"rectangle": {"low": {"latitude": lat - dlat, "longitude": lng - dlng},
                          "high": {"latitude": lat + dlat, "longitude": lng + dlng}}}


def dist(a, b):
    return math.hypot((a[0] - b[0]) * 111_320, (a[1] - b[1]) * 111_320 * math.cos(math.radians(a[0])))


calls = 0
centers = []
for aid, landmark, r in ([] if OFFLINE else AREAS):
    p = post({"textQuery": landmark, "languageCode": "ja", "maxResultCount": 1})["places"][0]
    calls += 1
    loc = (p["location"]["latitude"], p["location"]["longitude"])
    centers.append((aid, landmark, r, loc))
    print(f"{aid:9} {landmark} → {p['displayName']['text']} {loc}")

raw = {}
if OFFLINE:
    _cache = json.load(open(RAW_PATH, encoding="utf-8"))
    raw, centers, hm_ids = _cache["raw"], [tuple(c[:3]) + (tuple(c[3]),) for c in _cache["centers"]], _cache["hm_ids"]
for aid, landmark, r, loc in ([] if OFFLINE else centers):
    for q in QUERIES:
        body = {"textQuery": q, "languageCode": "ja", "locationRestriction": rect(*loc, r), "minRating": 3.5,
                "pageSize": 20}
        for _ in range(3):
            d = post(body)
            calls += 1
            for p in d.get("places", []):
                raw[p["id"]] = p
            if not d.get("nextPageToken"):
                break
            body["pageToken"] = d["nextPageToken"]
            time.sleep(1)
    print(f"{aid:9} {landmark}: 累計 {len(raw)} 家，API 呼叫 {calls} 次")


def is_food(p):
    types = set(p.get("types", []))
    if p.get("primaryType") in NOT_FOOD:
        return False
    return any(h in t for t in types for h in FOOD_HINTS)


def nearest_area(p):
    loc = (p["location"]["latitude"], p["location"]["longitude"])
    inside = [(dist(loc, c), aid) for aid, _, r, c in centers if dist(loc, c) <= r * 1.45]  # 矩形角落
    return min(inside)[1] if inside else None


def closed_days(p):
    periods = p.get("regularOpeningHours", {}).get("periods")
    if not periods:
        return None
    open_days = {x["open"]["day"] for x in periods if "open" in x}
    if len(periods) == 1 and "close" not in periods[0]:
        return []  # 24 小時
    return [d for d in range(7) if d not in open_days]  # 0=週日


picked, kids_no = [], []
for p in raw.values():
    if not (p.get("rating", 0) > MIN_RATING and p.get("userRatingCount", 0) > MIN_COUNT):
        continue
    if p.get("businessStatus") != "OPERATIONAL" or not is_food(p):
        continue
    area = nearest_area(p)
    if not area:
        continue
    (kids_no if p.get("goodForChildren") is False else picked).append(dict(id=p["id"], name=p["displayName"]["text"], address=p.get("formattedAddress", ""),
                       lat=p["location"]["latitude"], lng=p["location"]["longitude"], rating=p["rating"],
                       count=p["userRatingCount"], primaryType=p.get("primaryType", ""), types=p.get("types", []),
                       kids=p.get("goodForChildren"), closed=closed_days(p), uri=p.get("googleMapsUri", ""),
                       hours=p.get("regularOpeningHours", {}).get("weekdayDescriptions", []),
                       price=p.get("priceLevel", ""), area=area))

# 百名店也查一次 Google（補評分、地址、小孩欄位）
food = json.load(open(os.path.join(ROOT, "data", "food-research.json"), encoding="utf-8"))
hm = {}
if not OFFLINE:
    hm_ids = {}
for s in food:
    if s["area"] == "範圍外":
        continue
    city = "小松市" if s["area"] == "小松" else "金沢市"
    if OFFLINE:
        p = raw.get(hm_ids.get(s["tabelog"], ""))
    else:
        d = post({"textQuery": f'{s["name"]} {city}', "languageCode": "ja", "maxResultCount": 1})
        calls += 1
        p = (d.get("places") or [None])[0]
    if p and city in p.get("formattedAddress", ""):
        raw[p["id"]] = p
        hm_ids[s["tabelog"]] = p["id"]
        hm[s["tabelog"]] = dict(id=p["id"], gname=p["displayName"]["text"], address=p.get("formattedAddress", ""),
                                rating=p.get("rating"), count=p.get("userRatingCount"), kids=p.get("goodForChildren"),
                                status=p.get("businessStatus"), uri=p.get("googleMapsUri", ""), closed=closed_days(p),
                                area=nearest_area(p), lat=p["location"]["latitude"], lng=p["location"]["longitude"])
    print(("✓ " if s["tabelog"] in hm else "✗ ") + s["name"], "→", hm.get(s["tabelog"], {}).get("gname", ""))

json.dump(dict(asof=ASOF, raw=raw, centers=centers, hm_ids=hm_ids), open(RAW_PATH, "w"), ensure_ascii=False)
json.dump(dict(asof=ASOF, rule=f"rating > {MIN_RATING} 且 userRatingCount > {MIN_COUNT}", picked=picked,
               kids_no=kids_no, hyakumeiten=hm), open(os.path.join(ROOT, "data", "google-places.json"), "w"),
          ensure_ascii=False, indent=1)
print(f"完成：符合條件 {len(picked)} 家（另有 {len(kids_no)} 家被標不適合小孩）；百名店對到 {len(hm)} 家；API 呼叫共 {calls} 次")
