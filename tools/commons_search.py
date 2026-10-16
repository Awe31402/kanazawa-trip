import json, sys, urllib.request, urllib.parse, re
UA = {"User-Agent": "kanazawa-trip-planner/1.0 (personal itinerary)"}
def q(term, n=5):
    p = {"action":"query","format":"json","generator":"search","gsrsearch":term,"gsrnamespace":"6","gsrlimit":str(n),
         "prop":"imageinfo","iiprop":"url|size|extmetadata|mime","iiurlwidth":"900"}
    u = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA)))
    out = []
    for pg in sorted(d.get("query",{}).get("pages",{}).values(), key=lambda x: x.get("index",0)):
        ii = pg["imageinfo"][0]; m = ii.get("extmetadata",{})
        if "jpeg" not in ii["mime"]: continue
        artist = re.sub("<[^>]+>","", m.get("Artist",{}).get("value","")).strip()
        out.append(dict(title=pg["title"], w=ii["width"], h=ii["height"], thumb=ii.get("thumburl"),
                        page=ii["descriptionurl"], lic=m.get("LicenseShortName",{}).get("value",""), artist=artist[:60]))
    return out
for term in sys.argv[1:]:
    print("##", term)
    for r in q(term): print(json.dumps(r, ensure_ascii=False))
