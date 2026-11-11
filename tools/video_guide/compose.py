import json, sys, os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
V = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BG, INK, MUT, RED = (243, 238, 238), (36, 27, 32), (111, 96, 104), (198, 40, 40)
def font(n, size, w):
    f = ImageFont.truetype(f"{V}/{n}-VF.ttf", size); f.set_variation_by_axes([w]); return f
F_T, F_S, F_N, F_B, F_BIG = font("Unbounded", 58, 600), font("Manrope", 36, 600), font("Unbounded", 40, 700), font("Manrope", 30, 700), font("Unbounded", 84, 600)
SCENES = [("f1", "s1", "Выберите дизайн", "65 вариантов, у каждого 3 палитры"),
          ("f1", "s2", "Цвета и блоки", "Таймер, карта, программа, анкета"),
          ("f1", "s3", "Имена, дата и место", "Приглашение меняется сразу"),
          ("f2", "s4", "Ссылка для гостей", "Отправьте в любой мессенджер"),
          ("f1", "s5", "Гости открывают и отвечают", "В один клик, без регистрации"),
          ("f2", "s6", "Ответы в кабинете", "Кто придет и сколько человек")]
# phone geometry
SH = 1390; SW = round(780 * SH / 1688); BZ = 16
PX, PY = (W - SW) // 2, 430
def phone_base():
    im = Image.new("RGB", (W, H), BG)
    sh = Image.new("L", (W, H), 0); d = ImageDraw.Draw(sh)
    d.rounded_rectangle((PX - BZ + 10, PY - BZ + 40, PX + SW + BZ - 10, PY + SH + BZ + 30), 74, fill=90)
    im.paste((150, 130, 135), (0, 0), sh.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((PX - BZ, PY - BZ, PX + SW + BZ, PY + SH + BZ), 70, fill=(18, 16, 17))
    return im
MASK = Image.new("L", (SW, SH), 0); ImageDraw.Draw(MASK).rounded_rectangle((0, 0, SW - 1, SH - 1), 56, fill=255)
def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
def caption(im, n, title, sub, a=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x, y = 76, 110
    d.ellipse((x, y, x + 78, y + 78), fill=RED + (int(255 * a),))
    d.text((x + 39, y + 41), str(n), font=F_N, fill=(255, 255, 255, int(255 * a)), anchor="mm")
    lines = wrap(d, title, F_T, W - 2 * 76 - 100)
    ty = y + 4 if len(lines) == 1 else y - 30
    for i, l in enumerate(lines):
        d.text((x + 104, ty + i * 76), l, font=F_T, fill=INK + (int(255 * a),), anchor="la")
    d.text((x, y + 108 + (40 if len(lines) > 1 else 0)), sub, font=F_S, fill=MUT + (int(255 * a),))
    im.paste(lay, (0, 0), lay)
def tapmark(im, x, y, k):
    # k 0..1: ring grows and fades
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = 34 + 40 * k; al = int(200 * (1 - k) ** 0.8)
    d.ellipse((x - 30, y - 30, x + 30, y + 30), fill=RED + (int(150 * (1 - k)),))
    d.ellipse((x - r, y - r, x + r, y + r), outline=RED + (al,), width=8)
    im.paste(lay, (0, 0), lay)
def scene_frames(n, folder, sid, title, sub):
    man = [m for m in json.load(open(f"{V}/{folder}/manifest.json")) if m["scene"] == sid]
    base = phone_base(); i = 0
    for m in man:
        shot = Image.open(f"{V}/{folder}/{m['f']}").convert("RGB").resize((SW, SH), Image.LANCZOS)
        for k in range(m["hold"]):
            im = base.copy(); im.paste(shot, (PX, PY), MASK)
            caption(im, n, title, sub, min(1.0, (i + 1) / 8))
            if m["tap"] and k < 7:
                tapmark(im, PX + m["tap"]["x"] * SW / 390, PY + m["tap"]["y"] * SH / 844, k / 7)
            i += 1
            yield im
def card(lines_big, small, frames, seal=True):
    for i in range(frames):
        a = min(1.0, (i + 1) / 10)
        im = Image.new("RGB", (W, H), BG); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        y0 = 700 - len(lines_big) * 50
        if seal:
            s = Image.open(f"{V}/seal.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
            s.putalpha(s.getchannel("A").point(lambda v: int(v * a))); lay.paste(s, ((W - 150) // 2, y0 - 220), s)
        for j, l in enumerate(lines_big):
            d.text((W // 2, y0 + j * 108), l, font=F_BIG, fill=INK + (int(255 * a),), anchor="ma")
        yy = y0 + len(lines_big) * 108 + 40
        for j, l in enumerate(small):
            d.text((W // 2, yy + j * 52), l, font=F_S, fill=(RED if j == 0 and l.startswith("knocky") else MUT) + (int(255 * a),), anchor="ma")
        im.paste(lay, (0, 0), lay); yield im
def encode(frames, out):
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    n = 0
    for im in frames: p.stdin.write(im.tobytes()); n += 1
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return n
INTRO = (["Приглашение", "на свадьбу", "по ссылке"], ["Как сделать за 6 шагов"], 66)
OUTRO = (["knocky.ru"], ["65 дизайнов · от 640 ₽", "Оплата один раз, без подписки"], 84)
if __name__ == "__main__":
    mode = sys.argv[1]
    os.makedirs(f"{V}/out", exist_ok=True)
    if mode == "test":
        card(*INTRO[:2], 1)
        next(card(*INTRO[:2], 20)).save(f"{V}/out/t_intro.jpg", quality=88)
        for n, (fo, sid, t, s) in enumerate(SCENES, 1):
            fr = list(scene_frames(n, fo, sid, t, s)); fr[len(fr) * 2 // 3].save(f"{V}/out/t_{sid}.jpg", quality=88)
            print(sid, len(fr) / FPS)
        list(card(OUTRO[0], OUTRO[1], 20))[-1].save(f"{V}/out/t_outro.jpg", quality=88)
    else:
        parts = []
        parts.append((card(INTRO[0], INTRO[1], INTRO[2]), "00_intro"))
        for n, (fo, sid, t, s) in enumerate(SCENES, 1): parts.append((scene_frames(n, fo, sid, t, s), f"{n:02d}_{sid}"))
        parts.append((card(OUTRO[0], OUTRO[1], OUTRO[2]), "99_outro"))
        lst = []
        for fr, name in parts:
            out = f"{V}/out/{name}.mp4"; print(name, encode(fr, out)); lst.append(out)
        open(f"{V}/out/list.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{V}/out/list.txt", "-c", "copy", f"{V}/out/knocky_guide.mp4"], check=True)
        print("done")
