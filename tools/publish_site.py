"""Publish the site without a password: SRC.html -> index.html with SEO and link-preview tags.
Usage: python3 tools/publish_site.py SRC.html index.html
(While the site was closed, tools/encrypt_site.py produced index.html instead.)
"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()
T = "Knocky - приглашения на свадьбу по ссылке"
D = "Онлайн-приглашение на свадьбу: 60+ дизайнов, программа дня, карта, ответы гостей, именные ссылки и рассадка. Оплата один раз, без подписки."
meta = (f'<meta name="description" content="{D}">\n'
        f'<meta property="og:title" content="{T}">\n<meta property="og:description" content="{D}">\n'
        '<meta property="og:url" content="https://knocky.ru/">\n<meta property="og:type" content="website">\n'
        '<meta name="p:domain_verify" content="c4fb0101210578d0604e75b9951939f4">\n'  # Pinterest site claim, keep
        '<meta property="og:locale" content="ru_RU">\n<link rel="canonical" href="https://knocky.ru/">\n')
ICONS = ('<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n'
         '<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
         '<link rel="manifest" href="/site.webmanifest">\n')
# real icon files instead of the inline one: search engines (Google) only show an icon that has its own URL
h = re.sub(r'<link rel="icon" href="data:[^>]*>\n?', "", h, count=1)
meta += ICONS
h = re.sub(r"<title>.*?</title>", f"<title>{T}</title>\n" + meta, h, count=1, flags=re.S)
open(out, "w", encoding="utf-8").write(h)
print("published", out, len(h))
