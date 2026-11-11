"""Publish the site without a password: SRC.html -> index.html with SEO and link-preview tags.
Usage: python3 tools/publish_site.py SRC.html index.html
(While the site was closed, tools/encrypt_site.py produced index.html instead.)
"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()
T = "Приглашение на свадьбу онлайн по ссылке - 60+ дизайнов | Knocky"
D = "Приглашение на свадьбу, которое приятно открыть. Таймер до праздника, местоположение, ответы гостей и многое другое - по одной ссылке. 60+ дизайнов"
meta = (f'<meta name="description" content="{D}">\n'
        f'<meta property="og:title" content="{T}">\n<meta property="og:description" content="{D}">\n'
        '<meta property="og:url" content="https://knocky.ru/">\n<meta property="og:type" content="website">\n'
        '<meta name="zen-verification" content="aDL1eVdW6ajNtF4BvjuFsbB6PjkpKqab2J2QbEG38M0ecYo3ky4PwwEpHfePDFah">\n'  # Dzen site claim, keep
        '<meta name="p:domain_verify" content="c4fb0101210578d0604e75b9951939f4">\n'  # Pinterest site claim, keep
        '<meta property="og:locale" content="ru_RU">\n<link rel="canonical" href="https://knocky.ru/">\n')
ICONS = ('<link rel="icon" href="/favicon.svg" type="image/svg+xml">\n<link rel="icon" href="/favicon.ico" type="image/x-icon" sizes="16x16 32x32 48x48">\n'
         '<link rel="icon" href="/favicon-120.png" type="image/png" sizes="120x120">\n<link rel="icon" href="/favicon-96.png" type="image/png" sizes="96x96">\n<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n'
         '<link rel="manifest" href="/site.webmanifest">\n')
# real icon files instead of the inline one: search engines (Google) only show an icon that has its own URL
h = re.sub(r'<link rel="icon" href="data:[^>]*>\n?', "", h, count=1)
meta += ICONS
h = re.sub(r"<title>.*?</title>", f"<title>{T}</title>\n" + meta, h, count=1, flags=re.S)
# structured data for search engines: organization, service with prices, FAQ (built from the FAQ block)
import json, html as _html
def _txt(x): return _html.unescape(re.sub(r"<[^>]+>", "", x)).strip()
faq = [{"@type": "Question", "name": _txt(q), "acceptedAnswer": {"@type": "Answer", "text": _txt(a)}}
       for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", h, re.S)]
ld = [{"@context": "https://schema.org", "@type": "Organization", "name": "Knocky", "url": "https://knocky.ru/",
       "logo": "https://knocky.ru/icon-512.png",
       "sameAs": ["https://t.me/knocky1", "https://vk.ru/knocky_invite", "https://dzen.ru/knocky", "https://pinterest.com/knocky_invite/"]},
      {"@context": "https://schema.org", "@type": "WebApplication", "name": "Knocky", "url": "https://knocky.ru/",
       "applicationCategory": "LifestyleApplication", "operatingSystem": "Any", "description": D,
       "offers": {"@type": "AggregateOffer", "priceCurrency": "RUB", "lowPrice": "640", "highPrice": "1990"}},
      {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq}]
_m = '<link rel="manifest" href="/site.webmanifest">\n'
h = h.replace(_m, _m + "".join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + "</script>\n" for x in ld), 1)
open(out, "w", encoding="utf-8").write(h)
print("published", out, len(h))
