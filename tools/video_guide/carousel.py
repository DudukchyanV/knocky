# Guide slides 1080x1350 drawn at 2x (2160x2700) from 3x PNG screenshots, saved as high-quality JPEG
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C
V = C.V; S = 2; W, H = 1080 * S, 1350 * S
BG, INK, MUT, RED = C.BG, C.INK, C.MUT, C.RED
F = lambda n, sz, w: C.font(n, sz * S, w)
F_T, F_S, F_N, F_SM = F("Unbounded", 54, 600), F("Manrope", 34, 600), F("Unbounded", 38, 700), F("Manrope", 28, 700)
BZ = 13 * S
def phone(im, shot, px, py, sh, tap=None):
    sw = round(1170 * sh / 2532)
    shad = Image.new("L", (W, H), 0); d = ImageDraw.Draw(shad)
    d.rounded_rectangle((px - BZ + 8 * S, py - BZ + 30 * S, px + sw + BZ - 8 * S, py + sh + BZ + 24 * S), 56 * S, fill=90)
    im.paste((150, 130, 135), (0, 0), shad.filter(ImageFilter.GaussianBlur(32 * S)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((px - BZ, py - BZ, px + sw + BZ, py + sh + BZ), 54 * S, fill=(18, 16, 17))
    s = Image.open(shot).convert("RGB").resize((sw, sh), Image.LANCZOS)
    mask = Image.new("L", (sw, sh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), 42 * S, fill=255)
    im.paste(s, (px, py), mask)
    if tap:
        x, y = px + tap["x"] * sw / 390, py + tap["y"] * sh / 844
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        for r, a in ((70, 70), (46, 120)):
            r *= S; dd.ellipse((x - r, y - r, x + r, y + r), fill=RED + (a // 2,), outline=(255, 255, 255, 200), width=5 * S)
        r = 19 * S; dd.ellipse((x - r, y - r, x + r, y + r), fill=RED + (220,), outline=(255, 255, 255, 255), width=4 * S)
        lay = lay.filter(ImageFilter.GaussianBlur(1.2 * S)); im.paste(lay, (0, 0), lay)
    return sw
def footer(d, n, total):
    d.text((70 * S, H - 66 * S), "knocky.ru", font=F_SM, fill=RED)
def step(n, title, sub, shot, tap):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    x, y = 70 * S, 72 * S
    d.ellipse((x, y, x + 72 * S, y + 72 * S), fill=RED); d.text((x + 36 * S, y + 38 * S), str(n), font=F_N, fill="white", anchor="mm")
    lines = C.wrap(d, title, F_T, W - 2 * x - 96 * S)
    for i, l in enumerate(lines): d.text((x + 96 * S, y + 6 * S + i * 68 * S - (30 * S if len(lines) > 1 else 0)), l, font=F_T, fill=INK)
    d.text((x, y + 100 * S + (34 * S if len(lines) > 1 else 0)), sub, font=F_S, fill=MUT)
    sh = 1000 * S; sw = round(1170 * sh / 2532)
    phone(im, shot, (W - sw) // 2, 262 * S + (20 * S if len(lines) > 1 else 0), sh, tap)
    return im
def cover(shot):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    fb = F("Unbounded", 55, 600)
    d.text((70 * S, 80 * S), "Приглашение на свадьбу", font=fb, fill=INK)
    d.text((70 * S, 158 * S), "по ссылке", font=fb, fill=INK)
    d.text((70 * S, 258 * S), "Как сделать за 6 шагов", font=F("Manrope", 40, 700), fill=RED)
    d.text((W - 70 * S, 262 * S), "Листайте →", font=F_S, fill=MUT, anchor="ra")
    sh = 900 * S; sw = round(1170 * sh / 2532); phone(im, shot, (W - sw) // 2, 362 * S, sh)
    return im
def end():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    s = Image.open(f"{V}/seal.png").convert("RGBA").resize((150 * S, 150 * S), Image.LANCZOS); im.paste(s, ((W - 150 * S) // 2, 380 * S), s)
    d.text((W // 2, 590 * S), "knocky.ru", font=F("Unbounded", 76, 600), fill=INK, anchor="ma")
    for i, l in enumerate(["Дизайны на любой вкус · от 640 ₽", "Оплата один раз, без подписки", "Примерить можно бесплатно"]):
        d.text((W // 2, (720 + i * 52) * S), l, font=F_S, fill=MUT, anchor="ma")
    return im
m1 = {x["f"]: x for x in json.load(open(f"{V}/f1hq/manifest.json"))}
STEPS = [("Выберите дизайн", "На любой вкус, у каждого 3 палитры", "f1hq", "00092.png"),
         ("Цвета и блоки", "Таймер, карта, программа, анкета", "f1hq", "00185.png"),
         ("Детали праздника", "Имена, дата, место, программа, дресс-код", "f1hq", "00232.png"),
         ("Ссылка для гостей", "Отправьте в любой мессенджер", "f2hq", "00027.png"),
         ("Гости открывают и отвечают", "В один клик, без регистрации", "f1hq", "00350.png"),
         ("Ответы в кабинете", "Кто придет и сколько человек", "f2hq", "ans.png")]
out = sys.argv[1]; os.makedirs(out, exist_ok=True); total = len(STEPS) + 2
def save(im, n):
    footer(ImageDraw.Draw(im), n, total); im.save(f"{out}/{n:02d}.jpg", quality=95, subsampling=0, optimize=True)
save(cover(f"{V}/f1hq/00255.png"), 1)
for i, (t, s, fo, f) in enumerate(STEPS, 1):
    save(step(i, t, s, f"{V}/{fo}/{f}", m1.get(f, {}).get("tap") if fo == "f1hq" else None), i + 1)
save(end(), total)
print("ok", total, W, H)
