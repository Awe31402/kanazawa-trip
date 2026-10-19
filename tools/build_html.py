"""產生行程手冊 HTML。

用法：
  python3 tools/build_html.py            → index.html（照片外連 Commons、Google 地圖 iframe）
  python3 tools/build_html.py --embed OUT → 照片內嵌、地圖改成連結（給 Artifact 私人網頁用，
                                            因為 Artifact 會擋外部圖片和 iframe）
"""
import base64, json, os, sys, urllib.parse
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IMG = os.path.join(ROOT, "data", "img")
META = json.load(open(os.path.join(IMG, "meta.json"), encoding="utf-8"))
THUMBS = json.load(open(os.path.join(IMG, "thumbs.json"), encoding="utf-8"))

EMBED = "--embed" in sys.argv
OUT = sys.argv[sys.argv.index("--embed") + 1] if EMBED else os.path.join(ROOT, "index.html")

ASOF = "2026-10-16"

CAPTION = {
    "tsuzumi": "金澤站鼓門", "komatsu": "小松機場航廈", "kenrokuen": "兼六園冬季的徽軫燈籠",
    "castle": "金澤城公園", "ichirino": "白山一里野溫泉滑雪場", "chaya": "東茶屋街",
    "omicho": "近江町市場西口", "goldleaf": "安江金箔工芸館（金箔工藝參考照，不是箔一）",
    "nagamachi": "長町武家屋敷", "kagaribi": "特急能登篝火號（683 系）",
    "aquarium": "能登島水族館", "wakura": "和倉溫泉", "aeon": "AEON MALL 新小松",
}


def warn(text, url=None):
    link = f' → <a href="{url}" target="_blank" rel="noopener">{escape(url.split("//")[1].rstrip("/"))}</a>' if url else ""
    return f'<li class="warn"><span class="wtag">⚠️ 待查證</span> {text}{link}</li>'


# ───────────────────────── 逐日資料 ─────────────────────────
DAYS = [
 dict(n=1, date="1/14", wd="四", iso="2027-01-14", title="抵達金澤", base="金澤",
  lead="平安抵達、熟悉金澤站。不排景點。",
  rows=[("午後（依航班 ⚠️）", "小松機場入境", "—"),
        ("＋約 40–45 分", "機場巴士到金澤站", "小松機場巴士 ¥1,300（大人），可信用卡感應；座位有限"),
        ("傍晚前", "住宿 check-in；看鼓門（金澤站東口）", "步行"),
        ("有空的話", "到<b>金澤站西口北鐵售票中心</b>先買 1/16 滑雪巴士的兒童票／套票（車上買不到）", "步行")],
  notes=[("室內備案", "金澤站內商場（百番街）逛逛、吃晚餐。"),
         ("晚餐區域", "金澤站周邊（站內商場、あんと）。"),
         ("親子提醒", "第一天別排太滿，早點睡，隔天走路量大。")],
  warns=[("去程航班時刻", "https://www.evaair.com/"), ("（虎航）去程航班時刻", "https://www.tigerairtw.com/"),
         ("機場巴士兒童票價", "https://www.hokutetsu.co.jp/")],
  photos=["tsuzumi", "komatsu"], maps=[("金澤站鼓門", "金沢駅 鼓門")]),

 dict(n=2, date="1/15", wd="五", iso="2027-01-15", title="兼六園＋金澤城＋長町武家屋敷", base="金澤",
  lead="金澤最經典的一天。三個都是戶外景點，15:00 前走完，下午早點回去休息。",
  rows=[("09:00", "金澤站出發", "路線巴士約 15–20 分 ⚠️（到「兼六園下」或「広坂」）"),
        ("09:30–11:30", "<b>兼六園</b>：雪吊、徽軫燈籠", "—"),
        ("11:30–12:15", "<b>金澤城公園</b>（和兼六園相鄰）", "步行"),
        ("12:15–13:15", "午餐", "步行到香林坊／広坂"),
        ("13:30–15:00", "<b>長町武家屋敷</b>散步", "從香林坊步行約 10 分 ⚠️"),
        ("15:30", "回金澤站", "巴士 ⚠️")],
  notes=[("室內備案", "雨雪大就縮短兼六園（主要路線 1 小時）、長町只走主要街道；多出來的時間到香林坊百貨，或石川縣立美術館內的甜點店 ル ミュゼ ドゥ アッシュ 休息。"),
         ("午餐區域", "香林坊／広坂一帶（百貨地下街方便）。"),
         ("親子提醒", "三個都在戶外，雪地和石板路容易滑，穿防水防滑鞋，帶備用手套。"),
         ("門票", "兼六園大人 ¥320。")],
  warns=[("兼六園兒童票、冬季開園時間", "https://www.pref.ishikawa.jp/siro-niwa/kenrokuen/"),
         ("市區巴士路線與時間", "https://www.hokutetsu.co.jp/")],
  photos=["kenrokuen", "castle", "nagamachi"],
  maps=[("兼六園", "兼六園"), ("金澤城公園", "金沢城公園"), ("長町武家屋敷", "長町武家屋敷跡")]),

 dict(n=3, date="1/16", wd="六", iso="2027-01-16", title="一里野溫泉滑雪場", base="金澤", tag="滑雪日",
  lead="全家玩雪。這天移動時間最長（滑雪日例外）。停駛就和 1/17 對調。",
  rows=[("早上（⚠️ 班次待查）", "金澤站發車", "北鐵「一里野溫泉滑雪場直行巴士」"),
        ("白天", "滑雪／玩雪；初學者可租雪具", "—"),
        ("下午（⚠️ 回程班次待查）", "回金澤站", "同一路巴士"),
        ("18:00 前", "回金澤住宿", "—")],
  extra="""<h4>票價（2025–26 年度參考，2026–27 年度還沒公布）</h4>
<div class="tw"><table><thead><tr><th>票種</th><th>大人</th><th>兒童</th></tr></thead><tbody>
<tr><td>巴士單程（金澤站出發）</td><td class="num">¥1,330</td><td class="num">¥670</td></tr>
<tr><td>套票（纜車＋來回巴士）</td><td class="num">¥6,500</td><td class="num">¥4,500</td></tr>
<tr><td>初學者票＋來回巴士（附雪具租借半價券）</td><td class="num" colspan="2">¥5,000</td></tr>
</tbody></table></div>""",
  notes=[("購票", "兒童票和初學者套票<b>車上買不到</b>。要到金澤站西口北鐵售票中心，或武藏 M'za 北鐵巴士服務中心買。建議 Day 1 或 Day 2 傍晚先買。"),
         ("停駛備案", "大雪可能停駛。前一天傍晚打北鐵 <span class=\"tel\">076-234-0123</span> 確認。1/16 停駛 → 和 1/17（日）對調。兩天都不行 → 改室內行程（金箔體驗、近江町市場）。"),
         ("其他交通", "WHITE RING 有小松機場／JR 小松站 ⇄ 一里野的滑雪接駁（2025–26 年度資料）。"),
         ("親子提醒", "帶備用手套、襪子、毛巾；中午在雪場休息區吃，下午早點收。"),
         ("午餐區域", "滑雪場內餐廳。")],
  warns=[("2026–27 年度運行日期、時刻（往年 11–12 月公布，時刻表是圖片）", "https://www.hokutetsu.co.jp/tourism-bus/"),
         ("是否需預約、雪具租借價格", "https://www.sam-hakusan.com/white/ichirino/bus/index.html"),
         ("備案接駁巴士 2026–27 年度資訊", "https://whitering.co.jp/ski_shuttle_2026.html")],
  photos=["ichirino"], maps=[("一里野溫泉滑雪場", "白山一里野温泉スキー場")]),

 dict(n=4, date="1/17", wd="日", iso="2027-01-17", title="東茶屋街＋近江町市場＋金箔體驗", base="金澤",
  lead="老街＋手作。（如果滑雪改到今天，本日行程移到 1/16。）",
  rows=[("09:30", "金澤站出發", "巴士約 10 分 ⚠️ 或計程車"),
        ("10:00–11:30", "<b>東茶屋街</b>散步", "—"),
        ("11:30–12:30", "<b>近江町市場</b>午餐", "巴士／計程車短程"),
        ("13:30–15:00", "<b>金箔貼體驗</b>（室內）：箔一本店（箔巧館），明信片約 10 分、小物盒約 40 分", "巴士 ⚠️"),
        ("15:30", "回金澤站", "—")],
  notes=[("室內備案", "東茶屋街縮短成 30 分鐘，把時間給金箔體驗。"),
         ("午餐區域", "近江町市場（海鮮丼；小孩不吃生魚可選熟食攤）。"),
         ("親子提醒", "金箔體驗<b>要先預約</b>。市場人多，小孩牽好。"),
         ("今晚先打包", "明天（Day 5）去和倉住一晚，今晚先打包<b>一晚小包</b>，大行李明天寄放飯店。")],
  warns=[("近江町市場週日營業狀況（部分店家週日休）", "https://ohmicho-ichiba.com/"),
         ("金箔體驗價格、位置交通（其他店家約 ¥1,000–2,000 起）", "https://www.hakuichi.co.jp/")],
  photos=["chaya", "omicho", "goldleaf"], maps=[("東茶屋街", "ひがし茶屋街"), ("近江町市場", "近江町市場"), ("箔一 箔巧館", "箔一 本店 箔巧館")]),

 dict(n=5, date="1/18", wd="一", iso="2027-01-18", title="和倉溫泉＋能登島水族館", base="和倉溫泉", tag="換住宿",
  lead="帶小包去和倉住一晚＋水族館（全室內，下雪也不怕）。水族館沒有固定公休，週一有開。",
  rows=[("上午", "金澤飯店退房，大行李寄放飯店 ⚠️", "—"),
        ("上午（⚠️ 班次待查）", "金澤 → 和倉溫泉", "特急「能登篝火號」約 1 小時；自由席在 3 號車廂"),
        ("抵達後", "小包寄放旅館", "計程車短程"),
        ("中午前後", "和倉溫泉站前 → 能登島水族館", "能登島交通巴士（往のとじま臨海公園），約 30 分到終點"),
        ("約 12:30–15:00", "<b>能登島水族館</b>：海豚表演已恢復", "—"),
        ("15:00 後", "回和倉溫泉，check-in、泡湯", "巴士")],
  notes=[("冬季營業", "12/1–3/19 是 9:00–16:30（16:00 停止入館）；休館只有 12/29–31（官網，2026-10-19 查詢）。"),
         ("門票", "國中以下（3 歲以上）¥510；大人 ¥1,850 或 ¥1,890（兩個來源不一致）。"),
         ("注意", "2026 年 3 月時<b>沒有展示鯨鯊</b>。"),
         ("午餐區域", "水族館內。"),
         ("親子提醒", "巴士班次少，<b>先抄好回程時間</b>。水族館電話 <span class=\"tel\">0767-84-1271</span>。")],
  warns=[("金澤飯店能否寄放大行李一晚（訂房時問）", None),
         ("特急班次、車票運賃（自由席特急券大人 ¥960／兒童 ¥480）", "https://timetable.jr-odekake.net/line-timetable/2850"),
         ("能登島交通巴士時刻、票價", "https://mb.jorudan.co.jp/os/bus/1707/stop/75286.html"),
         ("水族館大人票價", "https://www.notoaqua.jp/")],
  photos=["kagaribi", "aquarium"], maps=[("能登島水族館", "のとじま水族館"), ("和倉溫泉站", "和倉温泉駅")]),

 dict(n=6, date="1/19", wd="二", iso="2027-01-19", title="和倉溫泉早晨 → 回金澤（緩衝）", base="金澤",
  lead="早上泡湯散步，中午前回金澤。下午不排景點：休息、買伴手禮，先把回程行李整理好（明天晚歸、後天就回台）。",
  rows=[("早上", "旅館早餐、泡湯、和倉溫泉街散步看七尾灣", "步行"),
        ("約 10:00–11:00（⚠️ 班次待查）", "和倉溫泉 → 金澤", "特急「能登篝火號」約 1 小時"),
        ("11:00–12:30", "金澤飯店寄放行李（下午 check-in）⚠️；金澤站周邊午餐", "步行"),
        ("下午", "check-in、拿回大行李；休息、買伴手禮、<b>整理回程行李</b>", "步行")],
  notes=[("室內備案", "金澤站商場（百番街、あんと）。"),
         ("午餐區域", "金澤站周邊（站內商場、あんと）。"),
         ("補位日", "Day 2–4 沒走完的行程可以移到今天下午。"),
         ("今天先整理", "明天（Day 7）晚歸、後天回台，<b>回程行李今天先整理好</b>。")],
  warns=[("和倉溫泉街店家災後營業狀況", "https://www.hot-ishikawa.jp/"),
         ("金澤飯店能否中午先寄放行李", None)],
  photos=["wakura", "tsuzumi"], maps=[("和倉溫泉", "和倉温泉"), ("金澤站", "金沢駅")]),

 dict(n=7, date="1/20", wd="三", iso="2027-01-20", title="AEON 新小松一日遊", base="金澤", tag="晚歸",
  lead="整天在 AEON 新小松逛街、吃飯（全室內），21:00 前回旅館。明天就回台，回程行李前一天已整理好。",
  rows=[("10:00", "金澤站出發", "IR いしかわ鐵道或北陸新幹線 ⚠️ 班次、時間、票價待查"),
        ("10:30", "小松站 → AEON", "社區巴士「こまち」約 10 分 ⚠️ 班次待查，或計程車短程（約 2 km）"),
        ("10:45–20:00", "<b>AEON MALL 新小松</b>：逛街、午餐、休息、晚餐（室內）", "—"),
        ("20:00–21:00", "AEON → 小松站 → 金澤站 → 回旅館", "計程車短程（晚上建議）＋電車")],
  notes=[("AEON 營業", "商場、餐廳街、美食街 10:00–21:00；AEON Style 1F 超市 08:00–23:00；館內有 AEON 影城（官網，2026-10-16 查詢）。部分店家時間不同。"),
         ("室內備案", "AEON 整個都在室內，不怕下雪。"),
         ("午餐・晚餐", "AEON 新小松的餐廳街或美食街。晚餐人多時可能提早停止接客，早點去。"),
         ("親子提醒", "在商場待很久，中午後找地方坐下休息；累了就提早回金澤。"),
         ("回程注意", "AEON 已經沒有免費接駁車。天黑後回程，社區巴士晚上可能已經收班，<b>建議直接搭計程車</b>到小松站（約 2 km）。不建議晚上帶小孩走 19 分鐘的雪路。"),
         ("明天回台", "回旅館後早點睡；機場巴士座位有限，明天提早出門。")],
  warns=[("金澤 ⇄ 小松的電車班次、時間、票價（IR いしかわ鐵道／北陸新幹線）", "https://www.ishikawa-railway.jp/"),
         ("社區巴士「こまち」班次、末班時間；計程車費用", "https://www.aeon.com/store/イオン/イオンスタイル新小松/shop_info/train_bus/")],
  photos=["aeon"], maps=[("AEON MALL 新小松", "イオンモール新小松")]),

 dict(n=8, date="1/21", wd="四", iso="2027-01-21", title="回程", base="—",
  lead="從金澤出發，機場巴士約 40–45 分。上午、下午航班都可以，不排景點。",
  rows=[("方案 A：上午航班", "金澤站 → 機場巴士約 40–45 分 → 小松機場", "參考：長榮 BR157 小松 11:45 起飛"),
        ("方案 B：下午航班", "金澤站上午自由（站內商場買伴手禮）→ 機場巴士約 40–45 分 → 小松機場", "參考：虎航回程 16:55 起飛（5 月資料）")],
  notes=[("機場巴士", "座位有限，人多時提早到金澤站排隊。"),
         ("伴手禮", "金澤站內商場（百番街、あんと）。")],
  warns=[("回程航班時刻", "https://booking.evaair.com/flyeva/eva/b2c/flight-schedules.aspx?lang=zh-tw"),
         ("機場巴士時刻", "https://www.hokutetsu.co.jp/")],
  photos=["komatsu"], maps=[("金澤站", "金沢駅"), ("小松機場", "小松空港")]),
]

# 每天加「附近美食」連到美食頁（家數由 build_food.py 產生）
_COUNTS = json.load(open(os.path.join(ROOT, "data", "food-counts.json")))
FOOD_LINKS = {1: [("st", "金澤站")], 2: [("korinbo", "香林坊／広坂"), ("nagamachi", "長町")], 4: [("higashi", "東茶屋街"), ("omicho", "近江町")],
              5: [("wakura", "和倉溫泉")], 6: [("st", "金澤站")], 7: [("komatsu", "AEON 新小松")], 8: [("st", "金澤站")]}
for _d in DAYS:
    links = [f'<a href="food.html#{aid}">{label} {_COUNTS[aid]} 家 →</a>' for aid, label in FOOD_LINKS.get(_d["n"], [])
             if _COUNTS.get(aid)]
    if links:
        _d["notes"].append(("附近美食", "、".join(links)))

PENDING = [
 ("2027/1 去回程航班時刻、票價", "Day 1、8", "https://www.evaair.com/"),
 ("機場巴士兒童票價", "Day 1、8", "https://www.hokutetsu.co.jp/"),
 ("一里野直行巴士 2026–27 年度日期、時刻、票價", "Day 3", "https://www.hokutetsu.co.jp/tourism-bus/"),
 ("一里野是否需預約、雪具租借價格", "Day 3", "https://www.sam-hakusan.com/white/ichirino/bus/index.html"),
 ("兼六園兒童票、冬季開園時間", "Day 2", "https://www.pref.ishikawa.jp/siro-niwa/kenrokuen/"),
 ("金澤市區巴士路線、時間、一日券", "Day 2、4", "https://www.hokutetsu.co.jp/"),
 ("近江町市場週日營業狀況", "Day 4", "https://ohmicho-ichiba.com/"),
 ("金箔體驗（箔一）價格、位置交通", "Day 4", "https://www.hakuichi.co.jp/"),
 ("和菓子體驗店家、價格、營業日", "備案", "https://www.hot-ishikawa.jp/"),
 ("特急能登篝火號實際班次、運賃", "Day 5、6", "https://timetable.jr-odekake.net/line-timetable/2850"),
 ("能登島交通巴士時刻、票價", "Day 5", "https://mb.jorudan.co.jp/os/bus/1707/stop/75286.html"),
 ("能登島水族館大人票價（¥1,850 或 ¥1,890）", "Day 5", "https://www.notoaqua.jp/"),
 ("和倉溫泉街餐廳、店家災後營業狀況", "Day 5、6", "https://www.hot-ishikawa.jp/"),
 ("小松站 ⇄ AEON 社區巴士「こまち」班次、末班；計程車費用", "Day 7", "https://www.aeon.com/store/イオン/イオンスタイル新小松/shop_info/train_bus/"),
 ("金澤、和倉住宿價格", "預算", None),
 ("交通 IC 卡在北鐵巴士的可用範圍", "全程", "https://www.hokutetsu.co.jp/"),
 ("金澤飯店能否在 1/18 寄放大行李一晚、1/19 中午先寄放行李", "Day 5、6", None),
 ("金澤 ⇄ 小松電車班次、票價（IR いしかわ鐵道／北陸新幹線）", "Day 7", "https://www.ishikawa-railway.jp/"),
]


# ───────────────────────── 元件 ─────────────────────────
def photo(k):
    m = META[k]
    if EMBED:
        b = base64.b64encode(open(os.path.join(IMG, f"{k}.jpg"), "rb").read()).decode()
        src = f"data:image/jpeg;base64,{b}"
    else:
        src = THUMBS[k]
    w, h = m["size"]
    artist = escape(m["artist"])
    return (f'<figure><img src="{src}" alt="{escape(CAPTION[k])}" width="{w}" height="{h}" loading="lazy">'
            f'<figcaption>{escape(CAPTION[k])}<span class="cred">{artist} · {escape(m["lic"])} · '
            f'<a href="{m["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a></span></figcaption></figure>')


def maps(items):
    out = []
    for label, q in items:
        link = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)
        btn = f'<a class="mapbtn" href="{link}" target="_blank" rel="noopener">📍 {escape(label)}：在 Google 地圖開啟</a>'
        if EMBED:
            out.append(btn)
        else:
            src = "https://maps.google.com/maps?q=" + urllib.parse.quote(q) + "&output=embed"
            out.append(f'<div class="map"><iframe src="{src}" loading="lazy" title="{escape(label)} 地圖" '
                       f'referrerpolicy="no-referrer-when-downgrade"></iframe>{btn}</div>')
    return '<div class="maps">' + "".join(out) + "</div>"


def day(d):
    tag = f'<span class="chip hot">{d["tag"]}</span>' if d.get("tag") else ""
    weekend = " wkend" if d["wd"] in "六日" else ""
    rows = "".join(f'<tr><td class="t">{t}</td><td>{w}</td><td class="how">{"" if h == "—" else h}</td></tr>' for t, w, h in d["rows"])
    notes = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in d["notes"])
    warns = "".join(warn(t, u) for t, u in d["warns"])
    figs = "".join(photo(k) for k in d["photos"])
    return f'''<details class="day" id="d{d["n"]}" data-date="{d["iso"]}">
<summary>
 <span class="dnum"><span class="dd">{d["date"]}</span><span class="wd{weekend}">週{d["wd"]}</span></span>
 <span class="dtitle"><span class="dlabel">Day {d["n"]}</span><span class="dname">{d["title"]}</span>
  <span class="dmeta"><span class="chip">🛏 {d["base"]}</span>{tag}<span class="chip warnchip">⚠️ {len(d["warns"])}</span></span></span>
 <span class="caret" aria-hidden="true"></span>
</summary>
<div class="dbody">
 <p class="lead">{d["lead"]}</p>
 <div class="figs n{len(d["photos"])}">{figs}</div>
 <div class="tw"><table class="sched"><thead><tr><th>時間</th><th>行程</th><th>交通</th></tr></thead><tbody>{rows}</tbody></table></div>
 {d.get("extra", "")}
 <dl class="notes">{notes}</dl>
 <ul class="warns">{warns}</ul>
 {maps(d["maps"])}
</div>
</details>'''


def pending_rows():
    out = []
    for i, (t, dd, u) in enumerate(PENDING, 1):
        link = f'<a href="{u}" target="_blank" rel="noopener">{escape(u.split("//")[1].split("/")[0])}</a>' if u else "訂房的旅館／飯店"
        out.append(f'<tr><td class="num">{i}</td><td>{t}</td><td>{dd}</td><td>{link}</td></tr>')
    return "".join(out)


CHECK = {
 "穿著": ["防水防滑的鞋（雪地、濕滑石板路）", "洋蔥式穿法：發熱衣＋刷毛＋防水外套", "帽子、圍巾、手套（小孩多帶一副備用）",
         "滑雪日：雪褲、防水手套、護目鏡（或在雪場租 ⚠️）"],
 "雨雪裝備": ["折疊傘或輕便雨衣（北陸冬天常下雨夾雪）", "鞋子防水噴霧", "塑膠袋裝濕衣物"],
 "親子": ["小孩常用藥、暈車藥（滑雪日巴士較久）", "零食、水壺", "平板／繪本（等車用）", "護唇膏、乳液（乾冷）",
         "小孩身上放家長聯絡卡（中日文）", "1/18 去和倉用的一晚小包"],
 "證件與錢": ["護照", "信用卡（機場巴士可感應）", "日圓現金（小店、巴士）", "交通 IC 卡（⚠️ 北鐵巴士可用範圍待查證）", "旅遊保險"],
 "手機": ["網卡或 eSIM", "存好這份手冊的連結", "北鐵 076-234-0123、水族館 0767-84-1271"],
}


def checklist():
    out, i = [], 0
    for g, items in CHECK.items():
        lis = []
        for t in items:
            i += 1
            lis.append(f'<li><label><input type="checkbox" id="c{i}"> <span>{t}</span></label></li>')
        out.append(f'<div class="cgroup"><h4>{g}</h4><ul class="check">{"".join(lis)}</ul></div>')
    return "".join(out)


def credits():
    return "".join(f'<tr><td>{escape(CAPTION[k])}</td><td>{escape(v["artist"])}</td><td>{escape(v["lic"])}</td>'
                   f'<td><a href="{v["page"]}" target="_blank" rel="noopener">頁面</a></td></tr>' for k, v in META.items())


TOTAL_WARN = len(PENDING)

from style import CSS

JS = r"""
(function(){
 var days=[].slice.call(document.querySelectorAll('details.day'));
 // 旅途中：自動展開「今天」
 var t=new Date(), iso=t.getFullYear()+'-'+String(t.getMonth()+1).padStart(2,'0')+'-'+String(t.getDate()).padStart(2,'0');
 var hit=days.filter(function(d){return d.dataset.date===iso})[0];
 if(hit){hit.open=true;hit.classList.add('today');}
 document.getElementById('openAll').onclick=function(){days.forEach(function(d){d.open=true})};
 document.getElementById('closeAll').onclick=function(){days.forEach(function(d){d.open=false})};
 // 從路線條點進來時展開該天
 [].slice.call(document.querySelectorAll('a[href^="#d"]')).forEach(function(a){
  a.addEventListener('click',function(){var d=document.querySelector(a.getAttribute('href'));if(d&&d.tagName==='DETAILS')d.open=true;});
 });
 // 行前清單：只存在這支手機
 var KEY='kz-check-v1', st={};
 try{st=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
 [].slice.call(document.querySelectorAll('ul.check input')).forEach(function(c){
  c.checked=!!st[c.id];
  c.addEventListener('change',function(){st[c.id]=c.checked;try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}});
 });
})();
"""


def route():
    out = []
    for d in DAYS:
        base = {"金澤": "金澤", "和倉溫泉": "和倉", "—": "回台"}[d["base"]]
        cls = "rb wk" if d["base"] == "和倉溫泉" else "rb"
        ski = " ski" if d.get("tag") == "滑雪日" else ""
        out.append(f'<a href="#d{d["n"]}" class="{ski.strip()}"><span class="rd">{d["date"]}</span>'
                   f'<span class="rw">週{d["wd"]}</span><span class="{cls}">{base}</span></a>')
    return "".join(out)


html = f'''<title>金澤能登冬季親子遊</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+TC:wght@400;600;700&family=Noto+Serif+TC:wght@700&display=swap">
<style>{CSS}</style>

<header class="top"><div class="wrap">
 <div class="eyebrow">2027.01.14 — 01.21 · 8 天 7 夜</div>
 <h1>金澤＋能登 冬季親子行程手冊</h1>
 <p class="sub">大人 2＋國小孩童 1 · 桃園 ⇄ 小松直飛 · 全程大眾運輸 · 資料查詢日期 {ASOF}</p>
</div></header>

<nav class="toc" aria-label="目錄"><div class="wrap">
 <a href="#overview">總覽</a><a href="#days">逐日行程</a><a href="#check1">關鍵查證</a><a href="#transport">交通</a>
 <a href="#budget">預算</a><a href="food.html">🍣 美食</a><a href="#prep">行前清單</a><a href="#pending" class="w">⚠️ 待查證 {TOTAL_WARN}</a>
</div></nav>

<main class="wrap">

<section id="overview">
 <h2>總覽</h2>
 <div class="route">{route()}</div>
 <p class="legend">點日期跳到當天。金框＝滑雪日。天黑約 17:00，戶外景點排在 15:00 前，每天約 18:00 前回住宿（Day 7 例外：21:00 前）。</p>
 <div class="alert"><b>出發前最重要的 2 件事：</b>① 11–12 月查一里野滑雪巴士 2026–27 年度日期（還沒公布）；② 金澤飯店訂「1/14–17＋1/19–20」同一間，並問 1/18 能不能寄放大行李。</div>
 <h3>住宿一覽</h3>
 <div class="tw"><table class="stay"><thead><tr><th>晚</th><th>日期</th><th>地點</th><th>備註</th></tr></thead><tbody>
  <tr><td class="num">1–4</td><td class="num">1/14–1/17</td><td>金澤站周邊</td><td>住金澤站步行範圍，方便搭機場巴士、滑雪巴士、特急</td></tr>
  <tr><td class="num">5</td><td class="num">1/18</td><td>和倉溫泉</td><td>候選：TAOYA 和倉、日本の宿 のと楽、白鷺の湯 能登 海舟（都已恢復營業）</td></tr>
  <tr><td class="num">6–7</td><td class="num">1/19–1/20</td><td>金澤站周邊</td><td>和前 4 晚同一間；1/18 大行李寄放 ⚠️</td></tr>
 </tbody></table></div>
 <p class="legend">路線：小松機場 → 金澤（4 晚）→ 和倉溫泉（1 晚）→ 金澤（2 晚）→ 小松機場。回程當天只要搭機場巴士約 40–45 分。</p>
</section>

<section id="days">
 <h2>逐日行程 <small>點一下展開</small></h2>
 <div class="tools"><button class="tb" id="openAll" type="button">全部展開</button><button class="tb" id="closeAll" type="button">全部收合</button></div>
 {"".join(day(d) for d in DAYS)}
</section>

<section id="check1">
 <h2>5 項關鍵查證 <small>{ASOF}</small></h2>
 <div class="tw"><table><thead><tr><th>項目</th><th>結果</th><th>狀態</th></tr></thead><tbody>
  <tr><td>一里野滑雪巴士 2027/1</td><td>2025–26 年度只在週末假日開（1 月有 17、18 日）。2026–27 年度還沒公布，往年 11–12 月公布。照往年規律 1/16、1/17 很可能有車。</td><td>⚠️ 待查證</td></tr>
  <tr><td>能登島水族館</td><td>2025 年 3 月全面恢復營業，海豚表演也恢復。冬季 9:00–16:30。和倉溫泉站前搭巴士約 30 分。</td><td>✅ 營業中</td></tr>
  <tr><td>和倉溫泉旅館</td><td>2026/7/16 為止 19 家中 11 家恢復營業（見下方名單）。</td><td>✅</td></tr>
  <tr><td>JR 七尾線／能登篝火號</td><td>2026/3/14 改點後的時刻表上有這班車，金澤 ⇄ 和倉溫泉約 1 小時。部分班次只在特定日期開。</td><td>✅ 運行中</td></tr>
  <tr><td>桃園 ⇄ 小松直飛</td><td>長榮每日飛（參考 BR157 小松 11:45 → 桃園 13:55）。台灣虎航也飛（5 月參考：去程 TPE 12:10，回程 16:55）。</td><td>⚠️ 待查證</td></tr>
 </tbody></table></div>
 <h3>和倉溫泉：已恢復營業（11 家）</h3>
 <ul class="wakura"><li>花ごよみ</li><li>味な宿 宝仙閣</li><li>湯の華</li><li>日本の宿 のと楽</li><li>TAOYA 和倉</li><li>はまづる</li><li>能州いろは</li><li>ゆけむりの宿 美湾荘（部分客房）</li><li>ホテル海望（部分客房）</li><li>奥田屋（4 間客房）</li><li>白鷺の湯 能登 海舟</li></ul>
 <h3>尚未恢復</h3>
 <div class="tw"><table><thead><tr><th>旅館</th><th>預定恢復</th></tr></thead><tbody>
  <tr><td>すず花</td><td>2027/3</td></tr><tr><td>宿守屋寿苑</td><td>2027/5 左右</td></tr><tr><td>大観荘</td><td>2027 年度內</td></tr>
  <tr><td>多田屋</td><td>2028/4</td></tr><tr><td>あえの風</td><td>2028 年度下半年</td></tr><tr><td>加賀屋（新館）</td><td>2028 年度末</td></tr>
  <tr><td>虹と海</td><td>未定</td></tr><tr><td>渡月庵</td><td>未定</td></tr>
 </tbody></table></div>
</section>

<section id="transport">
 <h2>交通攻略</h2>
 <div class="tw"><table><thead><tr><th>交通</th><th>重點</th><th>何時訂／買</th></tr></thead><tbody>
  <tr><td>桃園 ⇄ 小松 機票</td><td>長榮或台灣虎航；回程從金澤出發，上午、下午班都可以</td><td>開賣就訂 ⚠️</td></tr>
  <tr><td>小松機場巴士</td><td>約 40–45 分，¥1,300，可信用卡感應，座位有限</td><td>當天在機場買</td></tr>
  <tr><td>一里野滑雪直行巴士</td><td>兒童票、初學者套票只能在售票中心買</td><td>1/14 或 1/15 傍晚到金澤站西口北鐵售票中心；是否需預約 ⚠️</td></tr>
  <tr><td>特急能登篝火號</td><td>自由席在 3 號車廂；部分班次只在特定日期開</td><td>確認班次後再決定要不要買指定席 ⚠️</td></tr>
  <tr><td>能登島交通巴士</td><td>班次少，先抄好去回時間</td><td>出發前查 Jorudan ⚠️</td></tr>
  <tr><td>金澤市區</td><td>路線巴士＋短程計程車</td><td>一日券種類、價格 ⚠️</td></tr>
 </tbody></table></div>
 <h3>預約時間表</h3>
 <div class="tw"><table><thead><tr><th>什麼時候</th><th>要做什麼</th></tr></thead><tbody>
  <tr><td>現在～11 月</td><td>訂機票；訂金澤住宿（1/14–17 共 4 晚＋1/19–20 共 2 晚，同一間，問能不能寄放行李）；訂和倉溫泉旅館 1 晚（1/18）</td></tr>
  <tr><td>11–12 月</td><td>查一里野巴士 2026–27 年度日期與時刻（北鐵官網）</td></tr>
  <tr><td>出發前 2–4 週</td><td>預約金箔體驗；查特急、能登島巴士班次；再確認水族館營業</td></tr>
  <tr><td>1/15 傍晚</td><td>確認 1/16 滑雪巴士有沒有停駛（北鐵 <span class="tel">076-234-0123</span>）</td></tr>
 </tbody></table></div>
</section>

<section id="budget">
 <h2>預算表 <small>查詢日期 {ASOF}</small></h2>
 <p class="legend">只列查得到的數字。查不到的寫 ⚠️，不估假數字。</p>
 <div class="tw"><table><thead><tr><th>項目</th><th>大人／人</th><th>兒童</th><th>全家 3 人</th></tr></thead><tbody>
  <tr><td>機票 桃園 ⇄ 小松</td><td>⚠️</td><td>⚠️</td><td>⚠️</td></tr>
  <tr><td>機場巴士（來回）</td><td class="num">¥2,600</td><td>⚠️</td><td>⚠️</td></tr>
  <tr><td>一里野套票（纜車＋來回巴士，2025–26 參考）</td><td class="num">¥6,500</td><td class="num">¥4,500</td><td class="num">¥17,500</td></tr>
  <tr><td>雪具租借</td><td>⚠️</td><td>⚠️</td><td>⚠️</td></tr>
  <tr><td>特急能登篝火號 金澤 ⇄ 和倉（來回）</td><td class="num">約 ¥4,200–5,400（估算）</td><td>特急券 ¥480×2＋運賃 ⚠️</td><td>⚠️</td></tr>
  <tr><td>兼六園</td><td class="num">¥320</td><td>⚠️</td><td>⚠️</td></tr>
  <tr><td>能登島水族館</td><td class="num">¥1,850–1,890</td><td class="num">¥510</td><td class="num">¥4,210–4,290</td></tr>
  <tr><td>能登島交通巴士（來回）</td><td>⚠️</td><td>⚠️</td><td>⚠️</td></tr>
  <tr><td>金箔體驗</td><td class="num">約 ¥1,000–2,000 起（他店參考）</td><td>同左</td><td>⚠️</td></tr>
  <tr><td>金澤住宿 6 晚（4＋2）</td><td>—</td><td>—</td><td>⚠️</td></tr>
  <tr><td>和倉溫泉旅館 1 晚</td><td>—</td><td>—</td><td>⚠️</td></tr>
 </tbody></table></div>
</section>

<section id="prep">
 <h2>冬季親子行前清單 <small>打勾只存在這支手機</small></h2>
 <div class="cgrid">{checklist()}</div>
</section>

<section id="pending">
 <h2>⚠️ 待查證彙整 <small>{TOTAL_WARN} 項</small></h2>
 <p class="legend">出發前逐項到官方連結確認。查到後再更新手冊。</p>
 <div class="tw"><table><thead><tr><th>#</th><th>項目</th><th>影響</th><th>官方連結</th></tr></thead><tbody>{pending_rows()}</tbody></table></div>
</section>

<section id="noto">
 <h2>附錄：奧能登災後現況</h2>
 <p>輪島、珠洲、千枚田等奧能登地區，受 2024 年 1 月地震與 9 月豪雨影響很大，本次行程不前往。最新復原狀況請看 <a href="https://www.hot-ishikawa.jp/" target="_blank" rel="noopener">ほっと石川旅ねっと</a>（⚠️ 待查證）。</p>
</section>

<section id="credits">
 <h2>照片來源 <small>全部來自 Wikimedia Commons</small></h2>
 <div class="tw"><table><thead><tr><th>照片</th><th>作者</th><th>授權</th><th></th></tr></thead><tbody>{credits()}</tbody></table></div>
</section>

</main>
<footer><div class="wrap">資料查詢日期 {ASOF}。價格、時刻、營業狀況以官方最新公告為準。本手冊不代訂。</div></footer>
<script>{JS}</script>
'''

if not EMBED:  # Artifact 會自動包外框；本機檔要自己包
    html = ('<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
            + html.replace("<style>", "</head><body>\n<style>", 1) + "</body></html>\n")
open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, f"{len(html)//1024} KB")
