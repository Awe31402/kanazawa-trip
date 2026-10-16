"""兩頁共用的樣式（行程手冊、美食頁）。"""
CSS = r"""
/* 版面：手機優先的單欄手冊；頂部黏著目錄，逐日卡片可收合。色調取自加賀藍與金箔。 */
:root{
 --paper:#f4f6f9; --card:#ffffff; --ink:#1b2231; --muted:#5a6476; --line:#d8dde6;
 --ai:#24467a; --ai-soft:#e3eaf5; --gold:#a8812a; --gold-soft:#f6eed9;
 --warn-bg:#fff3d1; --warn-fg:#6e4a00; --warn-line:#ecc864; --hot:#b3352b;
 --f-display:"Noto Serif TC","Songti TC","PMingLiU",serif;
 --f-body:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;
 --f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
 --paper:#10141c; --card:#171c26; --ink:#e5e9f0; --muted:#9aa4b6; --line:#2a3242;
 --ai:#93b3ea; --ai-soft:#1e2a40; --gold:#d9b65c; --gold-soft:#2e2814;
 --warn-bg:#33290f; --warn-fg:#f2d27c; --warn-line:#6b5420; --hot:#ef7b70; color-scheme:dark}}
:root[data-theme="dark"]{
 --paper:#10141c; --card:#171c26; --ink:#e5e9f0; --muted:#9aa4b6; --line:#2a3242;
 --ai:#93b3ea; --ai-soft:#1e2a40; --gold:#d9b65c; --gold-soft:#2e2814;
 --warn-bg:#33290f; --warn-fg:#f2d27c; --warn-line:#6b5420; --hot:#ef7b70; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.65}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--paper)}
a{color:var(--ai)}
a:focus-visible,summary:focus-visible,button:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.wrap{max-width:760px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header.top{padding-block:28px 18px}
.eyebrow{font-family:var(--f-mono);font-size:12px;letter-spacing:.08em;color:var(--gold);text-transform:uppercase}
h1{font-family:var(--f-display);font-weight:700;font-size:clamp(26px,6vw,36px);line-height:1.25;margin:.2em 0 .3em;text-wrap:balance}
.sub{color:var(--muted);margin:0}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--paper);border-bottom:1px solid var(--line)}
nav.toc .wrap{display:flex;gap:6px;overflow-x:auto;padding-block:8px;scrollbar-width:none}
nav.toc a{flex:none;text-decoration:none;color:var(--ink);font-size:14px;padding:5px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card)}
nav.toc a.w{border-color:var(--warn-line);background:var(--warn-bg);color:var(--warn-fg)}
section{padding-block:26px 6px;scroll-margin-top:56px}
h2{font-family:var(--f-display);font-size:22px;margin:0 0 12px;text-wrap:balance;display:flex;align-items:baseline;gap:10px}
h2 small{font-family:var(--f-mono);font-size:12px;color:var(--muted);font-weight:400}
h3{font-size:16px;margin:18px 0 8px}
h4{font-size:14px;margin:14px 0 6px;color:var(--muted);letter-spacing:.04em}
.num,.t,.dd{font-family:var(--f-mono);font-variant-numeric:tabular-nums}
.tw{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;vertical-align:top;padding:7px 8px;border-bottom:1px solid var(--line)}
th{font-weight:600;color:var(--muted);font-size:12px;letter-spacing:.04em;white-space:nowrap}
/* 路線條 */
.route{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:4px;margin:6px 0 4px}
.route a{display:flex;flex-direction:column;align-items:center;gap:2px;text-decoration:none;color:var(--ink);padding:8px 2px;border-radius:8px;background:var(--card);border:1px solid var(--line);min-width:0}
.route .rd{font-family:var(--f-mono);font-size:13px;font-weight:600}
.route .rw{font-size:11px;color:var(--muted)}
.route .rb{font-size:11px;padding:1px 6px;border-radius:999px;background:var(--ai-soft);color:var(--ai);white-space:nowrap}
.route .rb.wk{background:var(--gold-soft);color:var(--gold)}
.route .ski{outline:2px solid var(--gold);outline-offset:-2px}
.legend{font-size:12px;color:var(--muted);margin:0 0 6px}
.alert{border:1px solid var(--warn-line);background:var(--warn-bg);color:var(--warn-fg);border-radius:10px;padding:10px 14px;margin:12px 0;font-size:14px}
.alert b{color:inherit}
/* 逐日 */
.tools{display:flex;gap:8px;margin:0 0 10px;flex-wrap:wrap}
button.tb{font:inherit;font-size:13px;padding:5px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.day{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:0 0 10px;overflow:hidden}
.day[open]{border-color:var(--ai)}
.day.today{box-shadow:0 0 0 2px var(--gold)}
summary{list-style:none;display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:12px;align-items:center;padding:12px 14px;cursor:pointer}
summary::-webkit-details-marker{display:none}
.dnum{display:flex;flex-direction:column;align-items:center;min-width:52px;padding-right:12px;border-right:1px solid var(--line)}
.dd{font-size:20px;font-weight:600;color:var(--ai);line-height:1.1}
.wd{font-size:12px;color:var(--muted)}
.wd.wkend{color:var(--hot);font-weight:600}
.dtitle{display:flex;flex-direction:column;gap:3px;min-width:0}
.dlabel{font-family:var(--f-mono);font-size:11px;color:var(--gold);letter-spacing:.08em}
.dname{font-family:var(--f-display);font-weight:700;font-size:17px;line-height:1.35;text-wrap:balance}
.dmeta{display:flex;gap:6px;flex-wrap:wrap}
.chip{font-size:12px;padding:1px 8px;border-radius:999px;background:var(--ai-soft);color:var(--ai);white-space:nowrap}
.chip.hot{background:var(--gold-soft);color:var(--gold);font-weight:600}
.chip.warnchip{background:var(--warn-bg);color:var(--warn-fg)}
.caret{width:10px;height:10px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg);transition:transform .2s;margin-right:4px}
.day[open] .caret{transform:rotate(-135deg)}
.dbody{padding:0 14px 16px;border-top:1px solid var(--line)}
.lead{font-weight:600;margin:12px 0}
.figs{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
figure{margin:0;min-width:0}
figure img{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:8px;background:var(--line)}
figcaption{font-size:12px;color:var(--muted);margin-top:4px;display:flex;flex-direction:column}
.cred{font-size:11px;opacity:.85}
table.sched td.t{white-space:nowrap;color:var(--ai);font-size:13px}
table.sched td.how{color:var(--muted);font-size:13px}
@media (max-width:520px){
 table.sched thead{display:none}
 table.sched tr{display:grid;grid-template-columns:1fr;padding:8px 0;border-bottom:1px solid var(--line)}
 table.sched td{border:0;padding:1px 0}
 table.sched td.how:not(:empty)::before{content:"↳ "}
}
dl.notes{display:grid;gap:6px;margin:12px 0}
dl.notes div{display:grid;grid-template-columns:5.5em minmax(0,1fr);gap:8px}
dt{font-size:13px;font-weight:600;color:var(--ai)}
dd{margin:0}
ul.warns{list-style:none;padding:0;margin:10px 0;display:grid;gap:6px}
li.warn{background:var(--warn-bg);color:var(--warn-fg);border-left:3px solid var(--warn-line);padding:6px 10px;border-radius:0 6px 6px 0;font-size:13.5px;overflow-wrap:anywhere}
li.warn a{color:inherit}
.wtag{font-weight:700;white-space:nowrap}
.tel{font-family:var(--f-mono);user-select:all}
.maps{display:grid;gap:10px;margin-top:12px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.map{display:flex;flex-direction:column;gap:4px;min-width:0}
.map iframe{width:100%;height:200px;border:0;border-radius:8px;background:var(--line)}
a.mapbtn{display:block;font-size:13px;text-decoration:none;padding:7px 10px;border-radius:8px;border:1px solid var(--line);background:var(--paper)}
/* 清單 */
.cgrid{display:grid;gap:4px 20px;grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
ul.check{list-style:none;padding:0;margin:0}
ul.check li{padding:3px 0}
ul.check label{display:flex;gap:8px;align-items:flex-start;cursor:pointer}
ul.check input{margin-top:5px;accent-color:var(--ai)}
ul.check input:checked + span{color:var(--muted);text-decoration:line-through}
table.stay td:nth-child(-n+3){white-space:nowrap}
.wakura{columns:2 220px;font-size:14px;padding-left:1.2em}
footer{padding-block:30px 40px;color:var(--muted);font-size:12px}
@media (prefers-reduced-motion:reduce){.caret{transition:none}}
"""
