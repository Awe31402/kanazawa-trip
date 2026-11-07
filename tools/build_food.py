"""產生美食頁 food.html：Tabelog 百名店＋Google 高評價（評分 > 3.8、評價 > 500），照行程區域分類。

用法：
  python3 tools/build_food.py            → food.html（回行程的連結指向 index.html）
  python3 tools/build_food.py --embed OUT → 給 Artifact 用（回行程的連結指向 ./）
資料：
  data/food-research.json  百名店（award.tabelog.com）＋地址查證
  data/google-places.json  Google Places API 結果（先跑 tools/google_places.py）
  data/kanazawa-food-kids-check.xlsx  人工檢查過的清單（以這份為準）
規則：只放 Excel 裡有的店（行程區域外的百名店另外放「行程區域外」）；「Google兒童標示」＝不適合的店直接拿掉；永久歇業的店拿掉。
      Excel 的「類型」「來源」會蓋過自動判斷。
"""
import json, os, re, sys, urllib.parse
import openpyxl
from html import escape
from style import CSS

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EMBED = "--embed" in sys.argv
OUT = sys.argv[sys.argv.index("--embed") + 1] if EMBED else os.path.join(ROOT, "food.html")
HOME = "./" if EMBED else "index.html"
HM_ASOF = "2026-10-16"
HM = json.load(open(os.path.join(ROOT, "data", "food-research.json"), encoding="utf-8"))
G = json.load(open(os.path.join(ROOT, "data", "google-places.json"), encoding="utf-8"))
G_ASOF = G["asof"]

OLD_AREA = {"金沢駅": "st", "近江町": "omicho", "東茶屋": "higashi", "香林坊": "korinbo", "長町": "nagamachi", "小松": "komatsu"}
KANAZAWA_DATES = [("1/14", "四"), ("1/15", "五"), ("1/16", "六"), ("1/18", "一"), ("1/19", "二"), ("1/20", "三")]
AREAS = [  # id, 標題, 對應行程, 用來算公休的日期
 ("st", "金澤站周邊", "Day 1 抵達、Day 8 回程", KANAZAWA_DATES),
 ("omicho", "近江町市場周邊", "Day 6 午餐；1/14–16 住 Hotel Forza（就在旁邊），這 3 天的晚餐", [("1/14", "四"), ("1/15", "五"), ("1/16", "六"), ("1/19", "二")]),
 ("higashi", "東茶屋街周邊", "Day 6 上午", [("1/19", "二")]),
 ("korinbo", "香林坊／片町／広坂", "Day 2 午餐；1/18–20 住白鳥路山樂（附近），這幾天的晚餐", [("1/15", "五"), ("1/18", "一"), ("1/19", "二")]),
 ("nagamachi", "長町周邊", "Day 2 下午", [("1/15", "五")]),
 ("hakusan", "AEON 白山", "Day 7 整天（午餐、晚餐）", [("1/20", "三")]),
 ("komatsu", "小松站周邊", "目前行程沒有經過（機場巴士直接到金澤站）", KANAZAWA_DATES),
 ("wakura", "和倉溫泉", "Day 4 下午～Day 5 早上", [("1/17", "日"), ("1/18", "一")]),
 ("far", "行程區域外（要另外搭車）", "不在行程路線上，想專程去再排",
  KANAZAWA_DATES[:3] + [("1/17", "日")] + KANAZAWA_DATES[3:]),
]
AREA_TITLE = {a[0]: a[1] for a in AREAS}

CATS = [  # key, 標籤, 百名店 genre, Google type 關鍵字
 ("sweet", "甜點・咖啡", {"sweets", "wagashi", "cafe", "bread", "ice_gelato"},
  ("cafe", "coffee", "bakery", "dessert", "confectioner", "ice_cream", "tea_house", "cake", "donut")),
 ("sushi", "壽司・海鮮", {"sushi"}, ("sushi", "seafood")),
 ("ramen", "拉麵", {"ramen"}, ("ramen",)),
 ("curry", "咖哩", set(), ("curry",)),
 ("wa", "和食", {"japanese", "tempura", "soba"}, ("japanese_restaurant", "tempura", "soba", "udon", "tonkatsu",
                                                  "noodle", "donburi", "kaiseki", "oden")),
 ("izakaya", "居酒屋・燒鳥", {"izakaya", "yakitori", "toriryori"}, ("izakaya", "yakitori", "bar", "brewpub", "pub")),
 ("meat", "燒肉・牛排", {"steak"}, ("yakiniku", "steak", "barbecue", "shabu")),
 ("western", "西餐", {"french", "italian", "spanish", "creative_innovative", "hamburger"},
  ("french", "italian", "spanish", "hamburger", "pizza", "american", "western", "european", "bistro")),
 ("asia", "亞洲料理", {"asia_ethnic", "chinese"}, ("chinese", "korean", "thai", "indian", "vietnamese", "halal", "asian")),
 ("kona", "粉物", {"okonomiyaki"}, ("okonomiyaki", "takoyaki")),
]
HM_GENRE = {
 "asia_ethnic": "泰國料理", "bread": "麵包", "cafe": "咖啡廳", "chinese": "中華料理", "creative_innovative": "創作料理",
 "french": "法式", "hamburger": "漢堡", "ice_gelato": "冰淇淋", "italian": "義式", "izakaya": "居酒屋",
 "japanese": "日本料理", "okonomiyaki": "ねぎ焼", "ramen": "拉麵", "soba": "蕎麥麵", "spanish": "西班牙",
 "steak": "牛排・鐵板燒", "sushi": "壽司", "sweets": "甜點", "tempura": "天婦羅", "toriryori": "雞料理",
 "wagashi": "和菓子", "yakitori": "燒鳥",
}
G_TYPE = {
 "sushi_restaurant": "壽司", "seafood_restaurant": "海鮮", "japanese_restaurant": "日本料理", "ramen_restaurant": "拉麵",
 "japanese_curry_restaurant": "日式咖哩", "hamburger_restaurant": "漢堡", "japanese_izakaya_restaurant": "居酒屋",
 "italian_restaurant": "義式", "vietnamese_restaurant": "越南料理", "halal_restaurant": "清真料理", "cafe": "咖啡廳",
 "steak_house": "牛排", "brewpub": "精釀啤酒餐廳", "indian_restaurant": "印度料理", "hookah_bar": "水煙酒吧",
 "yakitori_restaurant": "燒鳥", "chinese_restaurant": "中華料理", "ice_cream_shop": "冰淇淋", "restaurant": "餐廳",
 "food": "餐飲", "bakery": "麵包", "dessert_shop": "甜點", "coffee_shop": "咖啡", "tonkatsu_restaurant": "豬排",
 "udon_noodle_shop": "烏龍麵", "soba_noodle_shop": "蕎麥麵", "yakiniku_restaurant": "燒肉", "bar": "酒吧",
 "french_restaurant": "法式", "korean_restaurant": "韓式", "confectionery": "和菓子・點心", "tea_house": "茶屋",
}
WD_JP = {"月": "一", "火": "二", "水": "三", "木": "四", "金": "五", "土": "六", "日": "日"}
WD_IDX = ["日", "一", "二", "三", "四", "五", "六"]  # Google: 0=週日


def g_cat(primary, types):
    """先看 Google 的主要類型，判斷不出來才看全部類型。"""
    for pool in ([primary], types):
        for key, label, _, hints in CATS:
            if any(h in t for t in pool for h in hints):
                return key
    return "other"


def hm_cat(genres):
    for key, label, gs, _ in CATS:
        if set(genres) & gs:
            return key
    return "other"


def clean_addr(a):
    return re.sub(r"^日本、(〒\d{3}-\d{4} )?", "", a)


# ───────── 合併兩個來源 ─────────
entries, kids_no, closed_perm = [], [], []
hm_ids = set()
for s in HM:
    if s["area"] == "範圍外":
        continue
    g = G["hyakumeiten"].get(s["tabelog"])
    if g:
        hm_ids.add(g["id"])
    if g and g["status"] == "CLOSED_PERMANENTLY":
        closed_perm.append(s["name"])
        continue
    area = (g or {}).get("area") or OLD_AREA.get(s["area"])
    if not area:
        continue  # Google 位置不在任何行程區域（料理 小松）
    e = dict(name=s["name"], area=area, cat=hm_cat(s["genres"]),
             genre="・".join(HM_GENRE.get(x, x) for x in s["genres"]), hm=s, g=g,
             address=clean_addr(g["address"]) if g else s["address"],
             addr_ok=bool(g), kids=(g or {}).get("kids"), tabelog=s["tabelog"],
             map=(g or {}).get("uri") or "https://www.google.com/maps/search/?api=1&query="
             + urllib.parse.quote(s["name"] + " 金沢市"))
    if g and g.get("closed") is not None:
        e["closed"] = {WD_IDX[d] for d in g["closed"]}
        e["closed_src"] = "Google"
    else:
        e["closed"] = {WD_JP[p[0]] for p in s["holiday"].split("、") if p and p[0] in WD_JP and "曜" in p}
        e["closed_src"] = "百名店頁面" if s["holiday"] else None
    entries.append(e)

for p in G["picked"] + G["kids_no"]:
    if p["id"] in hm_ids:
        continue
    e = dict(name=p["name"], area=p["area"], cat=g_cat(p["primaryType"], p["types"]),
             genre=G_TYPE.get(p["primaryType"], p["primaryType"] or "餐廳"), hm=None,
             g=dict(rating=p["rating"], count=p["count"]), address=clean_addr(p["address"]), addr_ok=True,
             kids=p["kids"], tabelog=None, map=p["uri"],
             closed={WD_IDX[d] for d in p["closed"]} if p["closed"] is not None else set(),
             closed_src="Google" if p["closed"] is not None else None)
    entries.append(e)

# ───────── 套用人工檢查的 Excel ─────────
_ws = openpyxl.load_workbook(os.path.join(ROOT, "data", "kanazawa-food-kids-check.xlsx")).active
_rows = list(_ws.iter_rows(values_only=True))
_col = {h: i for i, h in enumerate(_rows[0])}
XL = {r[_col["店名"]]: r for r in _rows[1:] if r[_col["店名"]]}
_names = {e["name"] for e in entries}
for n in XL:
    if n not in _names:
        print("⚠️ Excel 有、資料沒有：", n)
kept = []
for e in entries:
    r = XL.get(e["name"])
    if r is None:
        continue  # Excel 刪掉的店
    k = r[_col["Google兒童標示"]]
    if k == "不適合":
        kids_no.append(e)
        continue
    e["kids"] = True if k == "適合" else None
    if r[_col["類型"]]:
        e["genre"] = r[_col["類型"]]
    e["src_label"] = r[_col["來源"]]
    kept.append(e)
_dropped = {e["name"]: e for e in entries if e not in kept}
entries = kept
_kept = {e["name"] for e in entries}

# 使用者指定加入的店（不符合評價數門檻或 Google 標不適合小孩，但想去）
MANUAL = [  # (Google place id, 區域, 分類, 類型, 小孩備註)
    ("ChIJB5KhBoAz-F8RtHnvdTU3gGQ", "korinbo", "wa", "關東煮（おでん）",
     "Google 標「不適合小孩」（多半是店小、吧台座位），先打電話問能不能帶小孩、要不要訂位"),
]
_RAW = json.load(open(os.path.join(ROOT, "data", "google-places-raw.json"), encoding="utf-8"))["raw"]
for pid, area, cat, genre, knote in MANUAL:
    p = _RAW[pid]
    hours = p.get("regularOpeningHours")
    entries.append(dict(
        name=p["displayName"]["text"], area=area, cat=cat, genre=genre, hm=None,
        g=dict(rating=p.get("rating"), count=p.get("userRatingCount")), address=clean_addr(p["formattedAddress"]),
        addr_ok=True, kids=None, kids_note=knote, tabelog=None, map=p["googleMapsUri"], src_label="使用者指定",
        closed={WD_IDX[d] for d in range(7)} - {WD_IDX[x["open"]["day"]] for x in hours["periods"]} if hours else set(),
        closed_src="Google" if hours else None))

# 行程區域外的百名店（Excel 沒有）
for s in HM:
    if s["area"] != "範圍外" or s["name"] in _kept:
        continue  # 已在主清單的跳過（例：麺屋大河）
    d = _dropped.get(s["name"])
    if d:  # Google 找得到、位置其實在行程區域內（例：六角堂）→ 用 Google 資料＋百名店標記
        if d["kids"] is not False:
            d.update(hm=s, tabelog=s["tabelog"], cat=hm_cat(s["genres"]),
                     genre="・".join(HM_GENRE.get(x, x) for x in s["genres"]))
            entries.append(d)
        continue
    entries.append(dict(
        name=s["name"], area="far", cat=hm_cat(s["genres"]),
        genre="・".join(HM_GENRE.get(x, x) for x in s["genres"]), hm=s, g=None,
        address=s["address"], addr_ok=False, kids=None, tabelog=s["tabelog"],
        map="https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(s["name"]),
        closed={WD_JP[p[0]] for p in s["holiday"].split("、") if p and p[0] in WD_JP and "曜" in p},
        closed_src="百名店頁面" if s["holiday"] else None))


def sort_key(e):
    g = e["g"] or {}
    return (-(g.get("rating") or 0), -(g.get("count") or 0))


def is_h(e):
    lab = e.get("src_label")
    return lab == "百名店" if lab else bool(e["hm"])


def card(e, days):
    g = e["g"] or {}
    lab = e.get("src_label")
    is_hm = lab == "百名店" if lab else bool(e["hm"])
    src = ("h" if is_hm else "") + ("g" if g.get("rating") and g.get("count", 0) > 500 and g["rating"] > 3.8 else "")
    badges = []
    if is_hm:
        badges.append(f'<span class="chip hot">百名店{" " + e["hm"]["year"] if e["hm"] else ""}</span>')
    elif lab and lab != "Google":
        badges.append(f'<span class="chip hot">{escape(lab)}</span>')
    if g.get("rating"):
        badges.append(f'<span class="chip">Google ★{g["rating"]}・{g["count"]:,} 則</span>')
    hits = [f"{d}（{w}）" for d, w in days if w in e["closed"]]
    if e["closed_src"] is None:
        hol = '<span class="wtag">⚠️ 待查證</span>'
    else:
        hol = ("週" + "、".join(w for w in WD_IDX if w in e["closed"]) if e["closed"] else "無固定公休") + \
              f'<span class="hsrc">（{e["closed_src"]}）</span>'
        hol += (f' <span class="closed">❌ 行程中公休：{"、".join(hits)}</span>' if hits
                else ' <span class="open">✅ 行程那幾天有開</span>')
    kids = ('<span class="ok">✅ 適合小孩</span>' if e["kids"] else
            f'<span class="wtag">⚠️ 待查證</span>（{escape(e["kids_note"])}）' if e.get("kids_note") else
            '<span class="wtag">⚠️ 待查證</span>（Google 沒寫）')
    addr = escape(e["address"]) + ("" if e["addr_ok"] else ' <span class="wtag">⚠️ 番地待確認</span>')
    links = f'<a class="mapbtn" href="{e["map"]}" target="_blank" rel="noopener">📍 Google 地圖</a>'
    if e["tabelog"]:
        links += f'<a class="mapbtn" href="{e["tabelog"]}" target="_blank" rel="noopener">Tabelog（預約、評分）</a>'
    note = f'<p class="snote">{escape(e["hm"]["note"])}</p>' if e["hm"] and e["hm"]["note"] else ""
    asof = " · ".join(x for x in [f"百名店 {HM_ASOF}" if e["hm"] else "", f"Google {G_ASOF}" if g else ""] if x)
    return f'''<article class="shop" data-cat="{e["cat"]}" data-src="{src or ("m" if lab == "使用者指定" else "h")}">
 <header><h4>{escape(e["name"])}</h4><span class="tag">{escape(e["genre"])}</span></header>
 <div class="badges">{"".join(badges)}</div>
 {note}
 <dl class="sdl">
  <div><dt>地址</dt><dd>{addr}</dd></div>
  <div><dt>公休</dt><dd>{hol}</dd></div>
  <div><dt>小孩</dt><dd>{kids}</dd></div>
 </dl>
 <div class="slinks">{links}</div>
 <p class="src">查詢日期：{asof}</p>
</article>'''


def area_section(aid, title, when, days):
    items = [e for e in entries if e["area"] == aid]
    if not items:
        return ""
    blocks = []
    for key, label, _, _ in CATS + [("other", "其他", set(), ())]:
        group = sorted((e for e in items if e["cat"] == key), key=sort_key)
        if group:
            blocks.append(f'<div class="cat" data-cat="{key}"><h3>{label} <small>{len(group)}</small></h3>'
                          + "".join(card(e, days) for e in group) + "</div>")
    nh = sum(1 for e in items if is_h(e))
    return (f'<section id="{aid}"><h2>{title} <small>{len(items)} 家</small></h2>'
            f'<p class="legend">對應行程：{when}。百名店 {nh} 家、其他 {len(items) - nh} 家。</p>'
            f'{"".join(blocks)}</section>')


def ref_rows(rows):
    out = []
    for e in sorted(rows, key=lambda e: (list(AREA_TITLE).index(e["area"]), sort_key(e))):
        g = e["g"] or {}
        rating = f'★{g["rating"]}（{g["count"]:,}）' if g.get("rating") else "—"
        out.append(f'<tr><td>{escape(e["name"])}</td><td>{AREA_TITLE[e["area"]].split("／")[0]}</td>'
                   f'<td>{escape(e["genre"])}</td><td>{"百名店" if e["hm"] else "Google"}</td><td class="num">{rating}</td>'
                   f'<td><a href="{e["map"]}" target="_blank" rel="noopener">地圖</a></td></tr>')
    return "".join(out)


outside = [s["name"] for s in HM if s["area"] != "範圍外" and G["hyakumeiten"].get(s["tabelog"])
           and not G["hyakumeiten"][s["tabelog"]].get("area") and s["name"] not in closed_perm
           and G["hyakumeiten"][s["tabelog"]].get("kids") is not False]
outside_kids_no = [s["name"] for s in HM if s["area"] == "地址待查" and G["hyakumeiten"].get(s["tabelog"])
                   and not G["hyakumeiten"][s["tabelog"]].get("area")]

FOOD_CSS = r"""
.filter{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 4px}
.filter button{font:inherit;font-size:13px;padding:5px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.filter button[aria-pressed="true"]{background:var(--ai);border-color:var(--ai);color:var(--paper)}
.flabel{font-size:12px;color:var(--muted);margin:10px 0 0}
.cat h3{display:flex;align-items:baseline;gap:8px;border-bottom:1px solid var(--line);padding-bottom:4px}
.cat h3 small{font-family:var(--f-mono);color:var(--muted);font-weight:400}
.shop{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:10px 0;display:grid;gap:6px}
.shop header{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px}
.shop h4{font-family:var(--f-display);font-size:17px;margin:0;color:var(--ink);letter-spacing:0}
.tag{font-size:13px;color:var(--muted)}
.badges{display:flex;gap:6px;flex-wrap:wrap}
.snote{margin:0;font-size:14px;color:var(--muted)}
dl.sdl{display:grid;gap:3px;margin:0;font-size:14px}
dl.sdl div{display:grid;grid-template-columns:3em minmax(0,1fr);gap:8px}
.hsrc{font-size:12px;color:var(--muted)}
.closed{color:var(--hot);font-weight:600;white-space:nowrap}
.open,.ok{color:var(--muted);white-space:nowrap}
.slinks{display:flex;gap:8px;flex-wrap:wrap}
.slinks .mapbtn{flex:1 1 140px;text-align:center}
.src{margin:0;font-size:11px;color:var(--muted)}
.wtag{color:var(--warn-fg);background:var(--warn-bg);padding:0 4px;border-radius:4px}
.back{display:inline-block;margin-bottom:6px;font-size:14px}
details.ref{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0}
details.ref summary{display:block;padding:12px 14px;font-weight:600}
details.ref > div{padding:0 14px 12px}
.empty{color:var(--muted);font-size:14px}
"""

JS = r"""
(function(){
 var state={cat:'all',src:'all'};
 try{var s=JSON.parse(localStorage.getItem('kz-food-f')||'{}');if(s.cat)state.cat=s.cat;if(s.src)state.src=s.src}catch(e){}
 var groups=[].slice.call(document.querySelectorAll('.filter'));
 function apply(){
  groups.forEach(function(g){[].slice.call(g.querySelectorAll('button')).forEach(function(b){
   b.setAttribute('aria-pressed',String(state[g.dataset.f]===b.dataset.k))})});
  [].slice.call(document.querySelectorAll('article.shop')).forEach(function(a){
   var okc=state.cat==='all'||a.dataset.cat===state.cat;
   var oks=state.src==='all'||a.dataset.src.indexOf(state.src)>=0;
   a.hidden=!(okc&&oks);
  });
  [].slice.call(document.querySelectorAll('.cat')).forEach(function(c){c.hidden=!c.querySelector('article.shop:not([hidden])')});
  [].slice.call(document.querySelectorAll('main section.area')).forEach(function(s){s.hidden=!s.querySelector('article.shop:not([hidden])')});
  document.getElementById('none').hidden=!!document.querySelector('main section.area:not([hidden])');
  try{localStorage.setItem('kz-food-f',JSON.stringify(state))}catch(e){}
 }
 groups.forEach(function(g){g.addEventListener('click',function(ev){
  var b=ev.target.closest('button');if(!b)return;state[g.dataset.f]=b.dataset.k;apply();})});
 apply();
})();
"""

present = [c for c in CATS if any(e["cat"] == c[0] for e in entries)]
if any(e["cat"] == "other" for e in entries):
    present.append(("other", "其他", set(), ()))
cat_btns = '<button type="button" data-k="all">全部</button>' + "".join(
    f'<button type="button" data-k="{k}">{label}（{sum(1 for e in entries if e["cat"] == k)}）</button>'
    for k, label, _, _ in present)
n_hm = sum(1 for e in entries if is_h(e))
n_g = sum(1 for e in entries if (e["g"] or {}).get("count", 0) > 500 and (e["g"] or {}).get("rating", 0) > 3.8)
src_btns = (f'<button type="button" data-k="all">全部</button><button type="button" data-k="h">百名店（{n_hm}）</button>'
            f'<button type="button" data-k="g">Google 高評價（{n_g}）</button>')
toc = "".join(f'<a href="#{aid}">{t.split("／")[0].replace("周邊", "")}</a>'
              for aid, t, _, _ in AREAS if any(e["area"] == aid for e in entries))
sections = "".join(area_section(*a) for a in AREAS).replace('<section id=', '<section class="area" id=')

body = f'''<title>金澤百名店地圖</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+TC:wght@400;600;700&family=Noto+Serif+TC:wght@700&display=swap">
<style>{CSS}{FOOD_CSS}</style>

<header class="top"><div class="wrap">
 <a class="back" href="{HOME}">← 回行程手冊</a>
 <div class="eyebrow">Tabelog 百名店＋Google 高評價 · 照行程區域分類</div>
 <h1>金澤 附近吃什麼</h1>
 <p class="sub">共 {len(entries)} 家，都在行程會經過的區域。先選區域，再用下面的按鈕篩。</p>
</div></header>

<nav class="toc" aria-label="區域"><div class="wrap">{toc}<a href="#notes" class="w">⚠️ 說明</a></div></nav>

<main class="wrap">
 <section id="howto">
  <p class="flabel">食物種類</p><div class="filter" data-f="cat" role="group" aria-label="食物種類">{cat_btns}</div>
  <p class="flabel">來源</p><div class="filter" data-f="src" role="group" aria-label="來源">{src_btns}</div>
  <div class="alert"><b>先看這裡：</b>① 不適合小孩的店已經拿掉了。② 「⚠️ 待查證」＝還不知道能不能帶小孩，訂位或進門前問一下。③ 公休是用該區域對應的行程日期算的。</div>
 </section>
 {sections}
 <p id="none" class="empty" hidden>這個組合沒有店，換個篩選試試。</p>

 <section id="notes">
  <h2>⚠️ 說明</h2>
  <h3>選店規則</h3>
  <ul>
   <li><b>Tabelog 百名店</b>：來源 <a href="https://award.tabelog.com/hyakumeiten" target="_blank" rel="noopener">award.tabelog.com</a>，查詢日期 {HM_ASOF}。</li>
   <li><b>Google 高評價</b>：Google 評分<b>超過 3.8</b>、評價數<b>超過 500 則</b>、營業中，來源 Google Places API，查詢日期 {G_ASOF}。</li>
   <li>區域：以金澤站、近江町市場、東茶屋街、香林坊、長町、小松站、和倉溫泉為中心（AEON 白山還沒查 Google 資料，館內有 FOOD STREET 等約 50 家餐廳），半徑約 300–700 公尺。</li>
   <li>小孩：以人工檢查的清單為準（參考 Google 的「適合兒童」欄位）。不適合的 {len(kids_no)} 家已拿掉；沒標的寫 ⚠️。</li>
   <li>沒有收「Tabelog 評分 3.5 以上」（Tabelog 主站擋自動查詢）。「神泡達人」是人工補標的。</li>
  </ul>
  <details class="ref"><summary>沒列入的百名店（{len(closed_perm) + len(set(outside + outside_kids_no))} 家）</summary><div>
   <p><b>Google 顯示永久歇業：</b>{"、".join(closed_perm) or "無"}</p>
   <p><b>Google 位置不在行程區域、且標「不適合小孩」：</b>{"、".join(sorted(set(outside + outside_kids_no))) or "無"}</p>
   <p>其他不在行程區域的百名店，已放在上面「行程區域外」。</p>
  </div></details>
 </section>
</main>
<footer><div class="wrap">Google 評分、評價數、地址、營業時間與「適合兒童」資料來源：Google Maps。百名店資料 {HM_ASOF}、Google 資料 {G_ASOF}。營業時間、公休、預約規則以店家最新公告為準。本頁不代訂。</div></footer>
<script>{JS}</script>
'''

html = ('<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        + body.replace('<header class="top">', '</head><body>\n<header class="top">', 1) + "</body></html>\n")
open(OUT, "w", encoding="utf-8").write(html)
json.dump({aid: sum(1 for e in entries if e["area"] == aid) for aid, *_ in AREAS},
          open(os.path.join(ROOT, "data", "food-counts.json"), "w"))
print("wrote", OUT, f"{len(html)//1024} KB；主清單 {len(entries)} 家（百名店 {n_hm}），拿掉不適合小孩 {len(kids_no)} 家，歇業 {closed_perm}")
