# -*- coding: utf-8 -*-
"""Cover for «Не в своём уме» — rendered at 2x and downsampled.

Design: an Argentine-tango step chart. Two tracks of footprints walk in from
opposite corners — one gold, one pale — meet at two hearth-rings burning down
into a single ember («два очага догорят в один»), and continue upward as one
shared track. The book's whole argument, drawn as a dance diagram.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"D:\Projekty\Fun Fic\book\cover.png")
S = 2                      # supersample factor
W, H = 1600 * S, 2560 * S
FONTS = Path(r"C:\Windows\Fonts")

INK_TOP = (24, 15, 21)      # deep plum
INK_BOT = (38, 20, 22)      # warmer at the hearth end
GOLD = (206, 166, 78)
GOLD_SOFT = (170, 134, 62)
PALE = (226, 214, 198)
CREAM = (242, 236, 226)
DIM = (150, 130, 128)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size * S)


def bez(p0, p1, p2, t):
    """Quadratic bezier point and tangent angle in degrees."""
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return x, y, math.degrees(math.atan2(-dx, -dy))   # 0deg = walking "up"


# ---------------------------------------------------------------- background
img = Image.new("RGB", (W, H), INK_TOP)
d = ImageDraw.Draw(img)
for y in range(H):
    t = y / H
    d.line([(0, y), (W, y)],
           fill=tuple(int(INK_TOP[i] + (INK_BOT[i] - INK_TOP[i]) * t) for i in range(3)))
img = img.convert("RGBA")

# ember glow behind the emblem
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy, R = W // 2, int(1140 * S), int(660 * S)
for i in range(140, 0, -1):
    r = R * i / 140
    a = int(30 * (1 - i / 140) ** 2)
    gd.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=(168, 96, 48, a))
img = Image.alpha_composite(img, glow)

# ------------------------------------------------------------- step chart
steps = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(steps)


def footprint(x, y, angle, colour, alpha):
    """One shoe print: sole + heel, drawn upright, then rotated into place."""
    w, hgt = int(40 * S), int(104 * S)
    pad = int(34 * S)
    tile = Image.new("RGBA", (w + 2 * pad, hgt + 2 * pad), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    td.ellipse([pad, pad, pad + w, pad + int(hgt * 0.60)],
               outline=colour + (alpha,), width=3 * S)
    td.ellipse([pad + int(w * 0.20), pad + int(hgt * 0.74),
                pad + int(w * 0.80), pad + hgt],
               outline=colour + (alpha,), width=3 * S)
    tile = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    steps.alpha_composite(tile, (int(x - tile.width / 2), int(y - tile.height / 2)))


def trace(p0, p1, p2, colours, n, spread, alphas, dotted=True):
    """Footprints alternating left/right along a bezier, plus its dotted trace.

    `colours` may be a single colour or a pair, alternated print by print —
    the shared track upward is danced by both.
    """
    if not isinstance(colours, tuple) or isinstance(colours[0], int):
        colours = (colours, colours)
    if dotted:
        for k in range(160):
            t = k / 159
            x, y, _ = bez(p0, p1, p2, t)
            if k % 4 < 2:
                sd.ellipse([(x - 1.5) * S, (y - 1.5) * S, (x + 1.5) * S, (y + 1.5) * S],
                           fill=colours[0] + (44,))
    for i in range(n):
        t = (i + 0.5) / n
        x, y, ang = bez(p0, p1, p2, t)
        side = -1 if i % 2 else 1
        perp = math.radians(ang + 90)
        x += math.sin(perp) * spread * side
        y -= math.cos(perp) * spread * side
        footprint(x * S, y * S, ang + side * 7, colours[i % 2],
                  alphas[0] + int((alphas[1] - alphas[0]) * t))


# his track, in from the lower left; hers, in from the lower right
trace((214, 1660), (386, 1256), (668, 1146), GOLD, 9, 22, (44, 112))
trace((1386, 1660), (1214, 1256), (932, 1146), PALE, 9, 22, (40, 104))
# and out again as one track, walking up the page: his step, hers, his, hers
trace((800, 986), (742, 690), (806, 330), (GOLD, PALE), 8, 26, (104, 30), dotted=False)

img = Image.alpha_composite(img, steps)
d = ImageDraw.Draw(img)

# ------------------------------------------------------------------ emblem
em_y = int(1140 * S)
r1 = int(118 * S)
off = int(78 * S)
for dx in (-off, off):
    d.ellipse([W // 2 + dx - r1, em_y - r1, W // 2 + dx + r1, em_y + r1],
              outline=GOLD_SOFT + (225,), width=3 * S)
d.ellipse([W // 2 - int(142 * S), em_y - int(142 * S),
           W // 2 + int(142 * S), em_y + int(142 * S)],
          outline=GOLD + (60,), width=1 * S)
for r, col in ((int(17 * S), (226, 176, 104)), (int(9 * S), (255, 240, 208))):
    d.ellipse([W // 2 - r, em_y - r, W // 2 + r, em_y + r], fill=col)

# ------------------------------------------------------------------- frame
for inset, alpha, w in ((84, 95, 2), (100, 42, 1)):
    d.rectangle([inset * S, inset * S, W - inset * S, H - inset * S],
                outline=GOLD_SOFT + (alpha,), width=w * S)

# -------------------------------------------------------------------- type
f_title = font("palab.ttf", 128)
f_kicker = font("palai.ttf", 32)
f_author = font("pala.ttf", 29)


def centred(text, f, y, fill, spacing=0):
    if spacing:
        widths = [d.textlength(c, font=f) for c in text]
        total = sum(widths) + spacing * S * (len(text) - 1)
        x = (W - total) / 2
        for c, cw in zip(text, widths):
            d.text((x, y), c, font=f, fill=fill)
            x += cw + spacing * S
    else:
        tw = d.textlength(text, font=f)
        d.text(((W - tw) / 2, y), text, font=f, fill=fill)


rule_y = int(1730 * S)
d.line([int(280 * S), rule_y, W - int(280 * S), rule_y], fill=GOLD_SOFT + (125,), width=1 * S)

centred("Не в своём", f_title, int(1810 * S), CREAM)
centred("уме", f_title, int(1965 * S), CREAM)
centred("роман", f_kicker, int(2175 * S), GOLD + (235,), spacing=9)

d.line([int(690 * S), int(2320 * S), W - int(690 * S), int(2320 * S)],
       fill=GOLD_SOFT + (95,), width=1 * S)
centred("МАРТИН", f_author, int(2385 * S), DIM, spacing=14)

# ------------------------------------------------------------------- write
img = img.convert("RGB").resize((1600, 2560), Image.LANCZOS)
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT}  {OUT.stat().st_size // 1024} KB")
