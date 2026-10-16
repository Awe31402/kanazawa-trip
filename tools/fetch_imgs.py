import json, urllib.request, urllib.parse, re, time, io, os
from PIL import Image
# 輸出到專案的 data/img（不論從哪裡執行）
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "img")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "kanazawa-trip-planner/1.0 (personal itinerary)"}
PICK = {
 "tsuzumi":"File:Tsuzumi-mon, Kanazawa Station - Kanazawa, Japan - DSC09640.jpg",
 "kenrokuen":"File:Kenroku-en-winter-lantern.jpg",
 "castle":"File:Kanazawa Castle - Jan 26, 2016 (1).jpg",
 "nagamachi":"File:Street - Nagamachi - Kanazawa, Japan - DSC00307.jpg",
 "ichirino":"File:Hakusan Ichirino Hot Spring Ski Area.jpg",
 "chaya":"File:Higashi Chaya District of Kanazawa - panoramio.jpg",
 "omicho":"File:Omicho covered market western entrance, Kanazawa, 2016.jpg",
 "goldleaf":"File:Yasuekinpakukogeikan003.jpg",
 "kagaribi":"File:JR-WEST 683 series Noto-Kagaribi.jpg",
 "aquarium":"File:Notojima Suizokukan.jpg",
 "wakura":"File:Wakura View.JPG",
 "aeon":"File:Aeon Mall Shinkomatsu.jpg",
 "komatsu":"File:Komatsu airport terminal building.jpg",
}
p = {"action":"query","format":"json","titles":"|".join(PICK.values()),"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"960"}
d = json.load(urllib.request.urlopen(urllib.request.Request("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p), headers=UA)))
norm = {n["to"]:n["from"] for n in d["query"].get("normalized",[])}
bytitle = {}
for pg in d["query"]["pages"].values():
    ii = pg["imageinfo"][0]; m = ii["extmetadata"]
    bytitle[norm.get(pg["title"], pg["title"])] = dict(
        thumb=ii.get("thumburl") or ii["url"], page=ii["descriptionurl"],
        lic=m.get("LicenseShortName",{}).get("value",""),
        artist=re.sub(r"\s+"," ",re.sub("<[^>]+>","",m.get("Artist",{}).get("value",""))).strip())
meta = {}
for key, title in PICK.items():
    info = bytitle[title]
    raw = urllib.request.urlopen(urllib.request.Request(info["thumb"], headers=UA)).read()
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    im.thumbnail((800, 800))
    im.save(os.path.join(OUT, f"{key}.jpg"), "JPEG", quality=72, optimize=True, progressive=True)
    meta[key] = dict(title=title[5:], page=info["page"], lic=info["lic"], artist=info["artist"], size=im.size)
    time.sleep(2)
json.dump(meta, open(os.path.join(OUT, "meta.json"),"w"), ensure_ascii=False, indent=1)
# contact sheet
ims = [Image.open(os.path.join(OUT, f"{k}.jpg")) for k in PICK]
sheet = Image.new("RGB", (4*300, 4*220), "white")
for i,(k,im) in enumerate(zip(PICK, ims)):
    t = im.copy(); t.thumbnail((300,200)); sheet.paste(t, ((i%4)*300, (i//4)*220))
sheet.save(os.path.join(OUT, "contact-sheet.jpg"))
for k,v in meta.items(): print(k, v["lic"], "|", v["artist"][:40], v["size"])
