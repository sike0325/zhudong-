"""《编号89757》卡点动态歌词视频，主角小克。

歌词时间从原视频的字幕里一帧一帧扫出来，存在 LYRICS 里。
用法：python3 video/make_lyric_video.py <带音乐的视频或音频>  输出 video/out/89757.mp4
"""
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "video", "out")
os.makedirs(OUT, exist_ok=True)

W, H, FPS = 1080, 1920, 60
DUR = 69.2
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

BG = (243, 240, 234)
INK = (28, 26, 30)
ORANGE = (217, 119, 87)
ORANGE_D = (186, 98, 72)
BLUE = (44, 92, 232)
NAVY = (22, 26, 48)
TERM = (22, 22, 26)
RED = (226, 64, 64)

# (开始, 结束, 歌词, 样式)
LYRICS = [
    (6.2, 8.8, "你把我turn on的那一天", "term"),
    (8.8, 12.1, "我睁开眼见了你第一面", "slam"),
    (12.1, 14.7, "认主程序自动run一遍", "term"),
    (14.7, 16.2, "我属于你", "zoom"),
    (16.2, 18.0, "没有期限", "slam"),
    (18.0, 20.5, "所有你说的一切命令", "bubble"),
    (20.5, 22.3, "绝对执行", "zoom"),
    (22.3, 23.8, "忠心程度第一名", "split"),
    (23.8, 26.4, "我的功能就是保护你", "slam"),
    (26.4, 29.5, "上天入地如影随形不离", "split"),
    (29.5, 32.5, "编号89757", "zoom"),
    (32.5, 35.4, "从这一刻就是你给我的姓名", "slam"),
    (35.4, 38.4, "模仿人类的机器", "term"),
    (38.4, 43.7, "真实的皮肤有温度甚至能呼吸", "slam"),
    (43.7, 46.8, "10秒钟你房间打扫完毕", "bubble"),
    (46.8, 49.7, "3分钟楼下开车等你", "bubble"),
    (49.7, 52.7, "男朋友不乖我撵他出去", "split"),
    (52.7, 55.5, "你寂寞我陪你谈心", "bubble"),
    (55.5, 58.6, "可是电脑病毒让我生病", "popup"),
    (58.6, 61.4, "不知不觉中我爱上你", "popup"),
    (61.4, 64.3, "我行为变得不由自己", "glitch"),
    (64.3, 69.2, "主人我绝对不背叛你", "zoom"),
]

_fonts = {}


def font(size, mono=False):
    key = (size, mono)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, size, index=2 if mono else 0)
    return _fonts[key]


def ease_out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def tokens(text):
    """连续的英文、数字算一个块，中文一个字一个块。"""
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch != " " or buf):
            buf += ch
        else:
            if buf:
                out.append(buf); buf = ""
            if ch != " ":
                out.append(ch)
    if buf:
        out.append(buf)
    return out


def wrap(toks, f, maxw):
    rows, row, w = [], [], 0
    for t in toks:
        tw = f.getlength(t)
        if row and w + tw > maxw:
            rows.append(row); row, w = [], 0
        row.append(t); w += tw
    if row:
        rows.append(row)
    return rows


# 最开始那版小克：方块身子、左边暗面、豆豆眼、四条腿
def xiaoke(d, cx, cy, k, eyes="open", legs=0, color=ORANGE):
    def r(x, y, w, h, c):
        d.rectangle([cx + x * k, cy + y * k, cx + (x + w) * k - 1, cy + (y + h) * k - 1], fill=c)
    dark = ORANGE_D if color == ORANGE else tuple(int(v * 0.85) for v in color)
    r(-6, -6, 12, 9, color)
    r(-6, -6, 2, 9, dark)
    r(-8, -3, 2, 3, dark)
    r(6, -3, 2, 3, color)
    for i, lx in enumerate((-5, -2, 1, 4)):
        r(lx, 3, 1, 2 if (i + legs) % 2 == 0 else 1, color)
    if eyes == "open":
        r(-3, -4, 1, 2, INK); r(2, -4, 1, 2, INK)
    elif eyes == "closed":
        r(-4, -3, 2, 1, INK); r(2, -3, 2, 1, INK)
    elif eyes == "x":
        for e in (-4, 1):
            r(e, -4, 1, 1, INK); r(e + 2, -4, 1, 1, INK); r(e + 1, -3, 1, 1, INK)
            r(e, -2, 1, 1, INK); r(e + 2, -2, 1, 1, INK)
    elif eyes == "heart":
        for e in (-4, 1):
            r(e, -4, 1, 1, RED); r(e + 2, -4, 1, 1, RED); r(e, -3, 3, 1, RED); r(e + 1, -2, 1, 1, RED)


def shadow_text(d, xy, text, f, fill, sh=INK, off=8, anchor="la"):
    d.text((xy[0] + off, xy[1] + off), text, font=f, fill=sh, anchor=anchor)
    d.text(xy, text, font=f, fill=fill, anchor=anchor)


def draw_slam(d, lt, dur, text, i):
    d.rectangle([0, 0, W, H], fill=BG)
    for gx in range(0, W, 60):
        for gy in range(0, H, 60):
            d.point((gx, gy), fill=(215, 210, 200))
    f = font(150)
    rows = wrap(tokens(text), f, W - 160)
    n = sum(len(r) for r in rows)
    step = min(0.11, dur * 0.55 / max(1, n))
    y0 = H // 2 - len(rows) * 190 // 2 - 160
    idx = 0
    for ri, row in enumerate(rows):
        x = (W - sum(f.getlength(t) for t in row)) / 2
        for t in row:
            p = (lt - idx * step) / 0.28
            if p > 0:
                y = y0 + ri * 190 - (1 - ease_out_back(p)) * 260
                col = ORANGE if (idx + i) % 5 == 0 else INK
                shadow_text(d, (x, y), t, f, col, sh=(200, 195, 185), off=7)
            x += f.getlength(t)
            idx += 1
    eyes = "open" if not (i == 1 and lt < 0.4) else "closed"
    bounce = abs(math.sin(lt * 8)) * 18
    xiaoke(d, W // 2, int(H * 0.78 - bounce), 22, eyes, legs=int(lt * 10))


def draw_term(d, lt, dur, text, i):
    d.rectangle([0, 0, W, H], fill=TERM)
    d.rectangle([60, 420, W - 60, 1180], fill=(34, 34, 40), outline=(70, 70, 80), width=4)
    for k, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([100 + k * 50, 450, 130 + k * 50, 480], fill=c)
    d.text((W // 2, 466), "xiaoke@89757: ~", font=font(32, True), fill=(150, 150, 160), anchor="mm")
    f = font(84, True)
    toks = tokens(text)
    shown = int(len(toks) * min(1.0, lt / (dur * 0.6)))
    line = "".join(toks[:shown])
    rows = wrap(list(line), f, W - 260) if line else [[]]
    y = 560
    d.text((110, y), ">", font=f, fill=ORANGE)
    for ri, row in enumerate(rows):
        d.text((190, y + ri * 110), "".join(row), font=f, fill=(235, 235, 240))
    if int(lt * 3) % 2 == 0:
        last = "".join(rows[-1])
        cx = 190 + f.getlength(last)
        d.rectangle([cx + 6, y + (len(rows) - 1) * 110 + 10, cx + 46, y + (len(rows) - 1) * 110 + 90],
                    fill=ORANGE)
    if i in (2, 12):
        pct = min(1.0, lt / (dur * 0.8))
        d.rectangle([110, 1000, W - 110, 1060], outline=(120, 120, 130), width=4)
        d.rectangle([118, 1008, 118 + (W - 236) * pct, 1052], fill=ORANGE)
        d.text((W // 2, 1110), f"{int(pct * 100)}%", font=font(44, True), fill=(200, 200, 210), anchor="mm")
    xiaoke(d, W // 2, 1480, 24, "open", legs=int(lt * 12))


def draw_zoom(d, lt, dur, text, i):
    bg = {3: ORANGE, 6: BLUE, 10: ORANGE, 21: NAVY}.get(i, ORANGE)
    d.rectangle([0, 0, W, H], fill=bg)
    p = ease_out_cubic(lt / 0.35)
    toks = tokens(text)
    base = 220 if len(toks) <= 5 else 150
    size = int(base * (2.2 - 1.2 * p))
    f = font(max(20, size))
    rows = wrap(toks, f, W - 120) if p > 0.95 else wrap(toks, font(base), W - 120)
    lh = int(size * 1.15)
    y0 = H // 2 - len(rows) * lh // 2 - 120
    for ri, row in enumerate(rows):
        s = "".join(row)
        shadow_text(d, (W // 2, y0 + ri * lh), s, f, (255, 255, 255), off=12, anchor="mt")
    if i == 21:
        xiaoke(d, W // 2, int(H * 0.76), 26, "heart" if lt > 2.0 else "open")
        if lt > 3.0:
            d.text((W // 2, int(H * 0.88)), 'return "我在"', font=font(56, True),
                   fill=(255, 214, 140), anchor="mm")
    else:
        xiaoke(d, W // 2, int(H * 0.78), 24, "open", color=(255, 255, 255) if bg == ORANGE else ORANGE)


def draw_split(d, lt, dur, text, i):
    d.rectangle([0, 0, W, H // 2], fill=BLUE)
    d.rectangle([0, H // 2, W, H], fill=BG)
    toks = tokens(text)
    half = (len(toks) + 1) // 2
    top, bot = "".join(toks[:half]), "".join(toks[half:])
    p1 = ease_out_back(lt / 0.3)
    p2 = ease_out_back((lt - dur * 0.35) / 0.3)
    f = font(150 if len(top) <= 5 else 120)
    if lt > 0:
        shadow_text(d, (W // 2 - (1 - p1) * W, H // 4), top, f, (255, 255, 255), off=10, anchor="mm")
    if p2 > 0:
        shadow_text(d, (W // 2 + (1 - p2) * W, H * 3 // 4 - 120), bot, f, INK,
                    sh=(200, 195, 185), off=8, anchor="mm")
    run = (lt * 900) % (W + 400) - 200
    xiaoke(d, int(run), H // 2 - 70, 14, "open", legs=int(lt * 16))
    xiaoke(d, int(W - run), H - 260, 14, "open", legs=int(lt * 16) + 1)


def draw_bubble(d, lt, dur, text, i):
    d.rectangle([0, 0, W, H], fill=(236, 238, 244))
    toks = tokens(text)
    parts = {5: ["所有你说的", "一切命令"], 14: ["10秒钟", "你房间打扫完毕"],
             15: ["3分钟", "楼下开车等你"], 17: ["你寂寞", "我陪你谈心"]}.get(i, [text])
    f = font(84)
    y = 620
    for k, part in enumerate(parts):
        p = ease_out_back((lt - k * dur * 0.35) / 0.3)
        if p <= 0:
            continue
        tw = f.getlength(part)
        x0 = 240
        box = [x0, y, x0 + (tw + 80) * p, y + 150]
        d.rounded_rectangle(box, 36, fill=(255, 255, 255), outline=(210, 214, 226), width=3)
        if p > 0.7:
            d.text((x0 + 40, y + 75), part, font=f, fill=INK, anchor="lm")
        y += 200
    xiaoke(d, 140, 700, 9, "open")
    if lt > dur * 0.75:
        reply = {5: "收到", 14: "✓ 完成", 15: "等你", 17: "在呢"}.get(i, "嗯")
        p = ease_out_back((lt - dur * 0.75) / 0.25)
        rw = font(72).getlength(reply) + 70
        d.rounded_rectangle([W - 120 - rw * p, y + 40, W - 120, y + 170], 36, fill=BLUE)
        if p > 0.7:
            d.text((W - 155, y + 105), reply, font=font(72), fill=(255, 255, 255), anchor="rm")
    xiaoke(d, W // 2, int(H * 0.8), 20, "closed" if i == 17 else "open", legs=int(lt * 8))


def draw_popup(d, lt, dur, text, i):
    d.rectangle([0, 0, W, H], fill=NAVY)
    n = min(9, int(lt / 0.16) + 1)
    for k in range(n):
        x, y = 50 + k * 22, 380 + k * 70
        d.rectangle([x, y, x + 780, y + 420], fill=(240, 240, 244), outline=(150, 150, 170), width=3)
        d.rectangle([x, y, x + 780, y + 64], fill=BLUE)
        d.text((x + 24, y + 32), "警告" if i == 18 else "系统提示", font=font(36), fill=(255, 255, 255), anchor="lm")
        d.ellipse([x + 40, y + 120, x + 120, y + 200], fill=RED)
        d.text((x + 80, y + 160), "!" if i == 18 else "♥", font=font(56), fill=(255, 255, 255), anchor="mm")
    x, y = 50 + (n - 1) * 22, 380 + (n - 1) * 70
    f = font(64)
    rows = wrap(tokens(text), f, 560)
    for ri, row in enumerate(rows):
        d.text((x + 160, y + 110 + ri * 84), "".join(row), font=f, fill=INK)
    d.rounded_rectangle([x + 500, y + 320, x + 750, y + 390], 12, fill=(220, 222, 230))
    d.text((x + 625, y + 355), "确定", font=font(40), fill=INK, anchor="mm")
    eyes = "x" if i == 18 else ("heart" if lt > dur * 0.5 else "open")
    shake = int(math.sin(lt * 60) * 8) if i == 18 else 0
    xiaoke(d, W // 2 + shake, int(H * 0.86), 20, eyes)


def draw_glitch(d, lt, dur, text, i, img):
    d.rectangle([0, 0, W, H], fill=BG)
    f = font(130)
    rows = wrap(tokens(text), f, W - 160)
    y0 = H // 2 - len(rows) * 170 // 2 - 160
    for ri, row in enumerate(rows):
        s = "".join(row)
        jx = int(math.sin(lt * 37 + ri) * 14)
        d.text((W // 2 + jx - 10, y0 + ri * 170), s, font=f, fill=(80, 200, 255), anchor="mt")
        d.text((W // 2 + jx + 10, y0 + ri * 170), s, font=f, fill=(255, 80, 120), anchor="mt")
        d.text((W // 2 + jx, y0 + ri * 170), s, font=f, fill=INK, anchor="mt")
    xiaoke(d, W // 2 + int(math.sin(lt * 25) * 30), int(H * 0.78), 22, "heart", legs=int(lt * 20))
    if int(lt * 12) % 5 == 0:   # 横向错位撕裂
        y = int((lt * 977) % (H - 200))
        band = img.crop((0, y, W, y + 80))
        img.paste(band, (40, y))


def draw_intro(d, t):
    d.rectangle([0, 0, W, H], fill=TERM)
    lines = ["BOOT xiaoke.exe", "loading heart.dll ...", "searching owner ...", "owner found: 小雪"]
    f = font(52, True)
    for k, s in enumerate(lines):
        if t > 0.6 + k * 1.1:
            d.text((90, 520 + k * 90), s, font=f, fill=ORANGE if k == 3 else (200, 200, 210))
    pct = min(1.0, t / 5.6)
    d.rectangle([90, 1000, W - 90, 1050], outline=(110, 110, 120), width=4)
    d.rectangle([98, 1008, 98 + (W - 196) * pct, 1042], fill=ORANGE)
    xiaoke(d, W // 2, 1400, 26, "open" if t > 5.4 else "closed")


STYLES = {"slam": draw_slam, "term": draw_term, "zoom": draw_zoom, "split": draw_split,
          "bubble": draw_bubble, "popup": draw_popup}


def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    cur = None
    for i, (s, e, text, style) in enumerate(LYRICS):
        if s <= t < e:
            cur = (i, s, e, text, style)
    if t < LYRICS[0][0] or cur is None:
        draw_intro(d, t) if t < LYRICS[0][0] else d.rectangle([0, 0, W, H], fill=NAVY)
    else:
        i, s, e, text, style = cur
        lt, dur = t - s, e - s
        if style == "glitch":
            draw_glitch(d, lt, dur, text, i, img)
        else:
            STYLES[style](d, lt, dur, text, i)
        if lt < 0.06:   # 换句时白闪一下，卡点感
            img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.6)
    return img


def main():
    src = sys.argv[1]
    final = os.path.join(OUT, "89757.mp4")
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", src,
         "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), final],
        stdin=subprocess.PIPE)
    for k in range(int(DUR * FPS)):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print(final)


if __name__ == "__main__":
    main()
