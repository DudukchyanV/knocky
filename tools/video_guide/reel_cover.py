# Instagram Reels cover 1080x1920 drawn at 2x; everything important sits inside the central 1080x1350 (profile grid crop)
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C
V = C.V; S = 2; W, H = 1080 * S, 1920 * S
F = lambda n, sz, w: C.font(n, sz * S, w)
im = Image.new("RGB", (W, H), C.BG); d = ImageDraw.Draw(im)
top = 285 * S  # top of the safe zone
fb = F("Unbounded", 66, 600)
for i, l in enumerate(["Приглашение", "на свадьбу по ссылке"]):
    d.text((W // 2, top + (40 + i * 84) * S), l, font=fb, fill=C.INK, anchor="ma")
d.text((W // 2, top + 232 * S), "Как сделать за 6 шагов", font=F("Manrope", 44, 700), fill=C.RED, anchor="ma")
sh = 960 * S; sw = round(1170 * sh / 2532); px, py = (W - sw) // 2, top + 340 * S; BZ = 13 * S
shad = Image.new("L", (W, H), 0); ImageDraw.Draw(shad).rounded_rectangle((px - BZ + 8 * S, py - BZ + 30 * S, px + sw + BZ - 8 * S, py + sh + BZ + 24 * S), 56 * S, fill=90)
im.paste((150, 130, 135), (0, 0), shad.filter(ImageFilter.GaussianBlur(32 * S)))
d = ImageDraw.Draw(im); d.rounded_rectangle((px - BZ, py - BZ, px + sw + BZ, py + sh + BZ), 54 * S, fill=(18, 16, 17))
s = Image.open(f"{V}/f1hq/00255.png").convert("RGB").resize((sw, sh), Image.LANCZOS)
mask = Image.new("L", (sw, sh), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), 42 * S, fill=255)
im.paste(s, (px, py), mask)
d.text((W // 2, H - 150 * S), "knocky", font=F("Unbounded", 40, 600), fill=C.INK, anchor="ma")
im.save(sys.argv[1], quality=95, subsampling=0, optimize=True)
# preview with the grid crop marked
p = im.resize((540, 960)); pd = ImageDraw.Draw(p); pd.rectangle((0, 142, 539, 142 + 675), outline=(0, 160, 255), width=2); p.save(sys.argv[1].replace(".jpg", "_check.png"))
print("ok", W, H, "phone bottom", (py + sh) // S, "safe bottom", 285 + 1350)
