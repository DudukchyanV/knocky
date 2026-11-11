"""Design pages for search: knocky.ru/dizain/ (catalog) and knocky.ru/dizain/<slug>/ (one per design).
Data: dizain/designs.json (id, name, style, palettes, slug, swatches), dizain/texts.py (short title + description),
previews dizain/img/<id>.webp (tools/design_thumbs.js). Output: dizain/<slug>/index.html, dizain/index.html.
Usage: python3 tools/build_design_pages.py [only_slug]"""
import json, sys, html, pathlib
R = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R / "dizain"))
from texts import T
D = json.loads((R / "dizain/designs.json").read_text())
sh = R / "shared"
HEADER = ("<style id=\"kh-css\">" + (sh / "header.css").read_text() + "</style>\n" + (sh / "header.html").read_text()
          + "<script id=\"kh-js\">" + (sh / "header.js").read_text() + "</script>")
e = html.escape
ORDER = ["Классика", "Цветы", "Картины", "Минимализм", "Современные", "Темные"]

CSS = """
:root{--bg:#F7F4F4;--soft:#F3EEEE;--surface:#fff;--ink:#241B20;--muted:#6F6068;--line:#E6D6D6;--seal:#C62828;
--f-disp:'Unbounded','Arial Black',system-ui,sans-serif;--f-body:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:500 16px/1.55 var(--f-body);-webkit-font-smoothing:antialiased}
a{color:inherit}
.wrap{max-width:1160px;margin:0 auto;padding:0 24px}
.crumbs{font-size:14px;color:var(--muted);padding:22px 0 8px}.crumbs a{text-decoration:none}.crumbs a:hover{color:var(--seal)}
.crumbs span{margin:0 6px}
h1,h2{font-family:var(--f-disp);font-weight:600;letter-spacing:-.03em;margin:0;text-wrap:balance}
.d-top{display:grid;grid-template-columns:minmax(0,440px) minmax(0,1fr);gap:56px;align-items:start;padding:18px 0 56px}
.d-pic{position:relative;border-radius:22px;overflow:hidden;background:var(--soft);aspect-ratio:3/4;box-shadow:0 24px 60px -28px rgba(36,27,32,.35)}
.d-pic img{display:block;width:100%;height:100%;object-fit:cover}
.chip{display:inline-block;padding:6px 12px;border-radius:999px;background:var(--soft);font-size:13px;font-weight:700;text-decoration:none}
.d-info h1{font-size:clamp(28px,3.6vw,44px);line-height:1.1;margin:14px 0 10px}
.d-sub{font-size:18px;color:var(--muted);margin:0 0 20px}
.d-desc{font-size:17px;margin:0 0 26px;max-width:560px}
.pals{display:flex;flex-wrap:wrap;gap:10px 18px;margin:0 0 26px;padding:0;list-style:none}
.pals li{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--muted)}
.sw{display:flex}.sw i{width:18px;height:18px;border-radius:50%;border:2px solid var(--bg);box-shadow:inset 0 0 0 1px rgba(36,27,32,.18);margin-left:-6px}.sw i:first-child{margin-left:0}
.lbl{font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 10px}
.inc{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px;padding:0;list-style:none}
.inc li{padding:6px 12px;border-radius:999px;background:var(--surface);border:1px solid var(--line);font-size:14px}
.cta{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:52px;padding:0 26px;border-radius:999px;font:700 16px/1 var(--f-body);text-decoration:none}
.btn-seal{background:var(--seal);color:#fff}.btn-seal:hover{transform:translateY(-1px)}
.btn-line{background:var(--soft)}.btn-line:hover{background:#EADFE0}
.price{margin:16px 0 0;font-size:14px;color:var(--muted)}
.more{padding:8px 0 64px}.more h2{font-size:clamp(22px,2.4vw,30px);margin:0 0 22px}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}
.card{text-decoration:none}.card .pic{border-radius:16px;overflow:hidden;aspect-ratio:3/4;background:var(--soft);transition:transform .2s}
.card:hover .pic{transform:translateY(-3px)}.card img{display:block;width:100%;height:100%;object-fit:cover}
.card b{display:block;margin:10px 0 0;font-size:15px}.card span{font-size:13px;color:var(--muted)}
.cat-head{padding:18px 0 28px}.cat-head h1{font-size:clamp(28px,4vw,48px);line-height:1.1;margin:10px 0 12px}.cat-head p{max-width:640px;color:var(--muted);font-size:17px;margin:0}
.grp{padding:0 0 48px}.grp h2{font-size:22px;margin:0 0 18px}
.foot{border-top:1px solid var(--line);padding:28px 0 40px;font-size:14px;color:var(--muted)}
.foot .wrap{display:flex;flex-wrap:wrap;gap:10px 24px;justify-content:space-between}.foot a{text-decoration:none}.foot a:hover{color:var(--seal)}
@media (max-width:860px){.d-top{grid-template-columns:1fr;gap:28px}.d-pic{max-width:420px}.cards{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}
@media (max-width:480px){.wrap{padding:0 16px}.btn{width:100%}.d-pic{max-width:none}}
"""
INC = ["Таймер до праздника", "Место и маршрут", "Программа дня", "Дресс-код", "Ответы гостей", "Именные ссылки", "Рассадка", "Фото и вишлист"]

def page(title, desc, canon, body, ld, img=None):
    og = f'<meta property="og:image" content="https://knocky.ru{img}">\n' if img else ""
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:type" content="website"><meta property="og:locale" content="ru_RU">
{og}<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" type="image/x-icon" sizes="16x16 32x32 48x48"><link rel="icon" href="/favicon-120.png" type="image/png" sizes="120x120"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Unbounded:wght@600&family=Manrope:wght@500;700&display=swap">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>
{HEADER}
<main>{body}</main>
<footer class="foot"><div class="wrap"><span>© Knocky - приглашения на свадьбу по ссылке</span>
<span><a href="/">Главная</a> · <a href="/dizain/">Все дизайны</a> · <a href="/#prices">Тарифы</a> · <a href="/#faq">Вопросы</a></span></div></footer>
</body></html>
"""

def card(x):
    return (f'<a class="card" href="/dizain/{x["slug"]}/"><div class="pic"><img src="/dizain/img/{x["id"]}.webp" '
            f'alt="Приглашение на свадьбу «{e(x["name"])}»" loading="lazy" width="600" height="800"></div>'
            f'<b>{e(x["name"])}</b><span>{e(x["style"])}</span></a>')

def crumbs(items):
    parts = [f'<a href="{u}">{e(n)}</a>' if u else f'<b>{e(n)}</b>' for n, u in items]
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": "https://knocky.ru" + u} if u else {})} for i, (n, u) in enumerate(items)]}
    return '<nav class="crumbs" aria-label="Навигация">' + "<span>/</span>".join(parts) + "</nav>", ld

def design_page(x):
    short, desc = T[x["id"]]
    title = f'Приглашение на свадьбу «{x["name"]}» - {short} | Knocky'
    meta = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "..."
    canon = f'https://knocky.ru/dizain/{x["slug"]}/'
    cr, ld = crumbs([("Главная", "/"), ("Дизайны", "/dizain/"), (x["name"], None)])
    pals = "".join(f'<li><span class="sw">{"".join(f"<i style=background:{c}></i>" for c in sw)}</span>{e(n)}</li>'
                   for n, sw in zip(x["pals"], x["sw"]))
    same = [y for y in D if y["style"] == x["style"] and y["id"] != x["id"]]
    other = [y for y in D if y["style"] != x["style"]]
    i = D.index(x)
    pick = (same + other[i % len(other):] + other)[:4]
    body = f"""<div class="wrap">{cr}
<section class="d-top">
<div class="d-pic"><img src="/dizain/img/{x["id"]}.webp" alt="Приглашение на свадьбу «{e(x["name"])}»: {e(short)}" width="600" height="800" fetchpriority="high"></div>
<div class="d-info">
<a class="chip" href="/dizain/#{e(x["style"])}">{e(x["style"])}</a>
<h1>Приглашение на свадьбу «{e(x["name"])}»</h1>
<p class="d-sub">{e(short[0].upper() + short[1:])}</p>
<p class="d-desc">{e(desc)}</p>
<p class="lbl">3 палитры на выбор</p><ul class="pals">{pals}</ul>
<p class="lbl">Что можно добавить</p><ul class="inc">{"".join(f"<li>{e(s)}</li>" for s in INC)}</ul>
<div class="cta"><a class="btn btn-seal" href="/#dizain={x["id"]}">Примерить со своими именами</a><a class="btn btn-line" href="/dizain/">Все дизайны</a></div>
<p class="price">От 640 ₽, оплата один раз. Ссылку можно отправить в любой мессенджер.</p>
</div></section>
<section class="more"><h2>Похожие дизайны</h2><div class="cards">{"".join(card(y) for y in pick)}</div></section>
</div>"""
    return page(title, meta, canon, body, ld, f'/dizain/img/{x["id"]}.webp')

def catalog():
    cr, ld = crumbs([("Главная", "/"), ("Дизайны", None)])
    groups = "".join(f'<section class="grp" id="{s}"><h2>{s}</h2><div class="cards">{"".join(card(x) for x in D if x["style"] == s)}</div></section>'
                     for s in ORDER if any(x["style"] == s for x in D))
    rest = [x for x in D if x["style"] not in ORDER]
    if rest: groups += f'<section class="grp"><h2>Другие</h2><div class="cards">{"".join(card(x) for x in rest)}</div></section>'
    body = f"""<div class="wrap">{cr}<header class="cat-head"><h1>Дизайны приглашений на свадьбу</h1>
<p>{len(D)} дизайнов: классика, цветы, акварельные картины, минимализм и современные. У каждого 3 палитры. Нажмите на дизайн, чтобы посмотреть подробнее и примерить со своими именами.</p></header>{groups}</div>"""
    return page(f"Дизайны приглашений на свадьбу - {len(D)} вариантов | Knocky",
                f"{len(D)} дизайнов онлайн-приглашений на свадьбу: классика, цветы, акварель, минимализм. У каждого 3 палитры, примерка со своими именами бесплатно.",
                "https://knocky.ru/dizain/", body, ld)

only = sys.argv[1] if len(sys.argv) > 1 else None
for x in D:
    if only and x["slug"] != only: continue
    p = R / "dizain" / x["slug"]; p.mkdir(exist_ok=True); (p / "index.html").write_text(design_page(x))
if not only: (R / "dizain/index.html").write_text(catalog())
print("design pages:", 1 if only else len(D), "+ catalog" if not only else "")
