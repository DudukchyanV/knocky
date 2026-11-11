import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C
V = C.V; W, H = 1080, 1350
BG, INK, MUT, RED = C.BG, C.INK, C.MUT, C.RED
F_T, F_S, F_N, F_BIG = C.font("Unbounded", 54, 600), C.font("Manrope", 34, 600), C.font("Unbounded", 38, 700), C.font("Unbounded", 76, 600)
F_SM = C.font("Manrope", 28, 700)
SH = 1000; SW = round(780 * SH / 1688); BZ = 13
def phone(im, shot, px, py, tap=None):
    sh = Image.new("L", (W, H), 0); d = ImageDraw.Draw(sh)
    d.rounded_rectangle((px - BZ + 8, py - BZ + 30, px + SW + BZ - 8, py + SH + BZ + 24), 56, fill=90)
    im.paste((150, 130, 135), (0, 0), sh.filter(ImageFilter.GaussianBlur(32)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((px - BZ, py - BZ, px + SW + BZ, py + SH + BZ), 54, fill=(18, 16, 17))
    s = Image.open(shot).convert("RGB").resize((SW, SH), Image.LANCZOS)
    mask = Image.new("L", (SW, SH), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, SW - 1, SH - 1), 42, fill=255)
    im.paste(s, (px, py), mask)
    if tap:
        x, y = px + tap["x"] * SW / 390, py + tap["y"] * SH / 844
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        for r, a in ((70, 70), (46, 120)):
            dd.ellipse((x - r, y - r, x + r, y + r), fill=RED + (a // 2,), outline=(255, 255, 255, 200), width=5)
        dd.ellipse((x - 19, y - 19, x + 19, y + 19), fill=RED + (220,), outline=(255, 255, 255, 255), width=4)
        lay = lay.filter(ImageFilter.GaussianBlur(1.2)); im.paste(lay, (0, 0), lay)
def footer(d, n, total):
    d.text((70, H - 66), "knocky.ru", font=F_SM, fill=RED)
    d.text((W - 70, H - 66), f"{n} / {total}", font=F_SM, fill=MUT, anchor="ra")
def step(n, title, sub, shot, tap, total):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    x, y = 70, 72
    d.ellipse((x, y, x + 72, y + 72), fill=RED); d.text((x + 36, y + 38), str(n), font=F_N, fill="white", anchor="mm")
    lines = C.wrap(d, title, F_T, W - 2 * 70 - 96)
    for i, l in enumerate(lines): d.text((x + 96, y + 6 + i * 68 - (30 if len(lines) > 1 else 0)), l, font=F_T, fill=INK)
    d.text((x, y + 100 + (34 if len(lines) > 1 else 0)), sub, font=F_S, fill=MUT)
    phone(im, shot, (W - SW) // 2, 262 + (20 if len(lines) > 1 else 0), tap)
    return im
def cover(shot, total):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    fb = C.font("Unbounded", 55, 600)
    d.text((70, 80), "Приглашение на свадьбу", font=fb, fill=INK)
    d.text((70, 158), "по ссылке", font=fb, fill=INK)
    d.text((70, 258), "Как сделать за 6 шагов", font=C.font("Manrope", 40, 700), fill=RED)
    d.text((W - 70, 262), "Листайте →", font=F_S, fill=MUT, anchor="ra")
    global SH, SW
    sh0, sw0 = SH, SW; SH = 900; SW = round(780 * SH / 1688)
    phone(im, shot, (W - SW) // 2, 362); SH, SW = sh0, sw0
    footer(d, 1, total); return im
def end(total):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    s = Image.open(f"{V}/seal.png").convert("RGBA").resize((150, 150), Image.LANCZOS); im.paste(s, ((W - 150) // 2, 380), s)
    d.text((W // 2, 590), "knocky.ru", font=F_BIG, fill=INK, anchor="ma")
    for i, l in enumerate(["65 дизайнов · от 640 ₽", "Оплата один раз, без подписки", "Примерить можно бесплатно"]):
        d.text((W // 2, 720 + i * 52), l, font=F_S, fill=MUT, anchor="ma")
    footer(d, total, total); return im
m1 = {x["f"]: x for x in json.load(open(f"{V}/f1/manifest.json"))}; m2 = {x["f"]: x for x in json.load(open(f"{V}/f2/manifest.json"))}
STEPS = [("Выберите дизайн", "65 вариантов, у каждого 3 палитры", "f1", "00092.jpg"),
         ("Цвета и блоки", "Таймер, карта, программа, анкета", "f1", "00185.jpg"),
         ("Имена, дата и место", "Приглашение меняется сразу", "f1", "00232.jpg"),
         ("Ссылка для гостей", "Отправьте в любой мессенджер", "f2", "00027.jpg"),
         ("Гости открывают и отвечают", "В один клик, без регистрации", "f1", "00350.jpg"),
         ("Ответы в кабинете", "Кто придет и сколько человек", "f2", "ans.jpg")]
out = sys.argv[1]; os.makedirs(out, exist_ok=True); total = len(STEPS) + 2
cover(f"{V}/f1/00255.jpg", total).save(f"{out}/01.jpg", quality=92)
for i, (t, s, fo, f) in enumerate(STEPS, 1):
    im = step(i, t, s, f"{V}/{fo}/{f}", (m1 if fo == "f1" else m2).get(f, {}).get("tap"), total)
    footer(ImageDraw.Draw(im), i + 1, total); im.save(f"{out}/{i + 1:02d}.jpg", quality=92)
end(total).save(f"{out}/{total:02d}.jpg", quality=92)
print("ok", total)
