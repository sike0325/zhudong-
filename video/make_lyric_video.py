"""《编号89757》卡点动态歌词视频，横屏 16:9，主角小克。

每句的起止时间来自原视频字幕；每个字的时间点从音频里测出人声起音，存在 89757_char_times.json。
用法：python3 video/make_lyric_video.py <带音乐的视频或音频>  输出 video/out/89757.mp4
"""
import json
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

W, H, FPS = 1920, 1080, 60
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
GOLD = (255, 214, 140)
WHITE = (255, 255, 255)

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
CHAR_TIMES = json.load(open(os.path.join(HERE, "89757_char_times.json")))

_fonts = {}


def font(size, mono=False):
    key = (int(size), mono)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT, max(8, int(size)), index=2 if mono else 0)
    return _fonts[key]


def ease_out_back(x, s=2.2):
    x = max(0.0, min(1.0, x))
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def ease_out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def tokens(text):
    out, buf = [], ""
    for ch in text:
        if ch.isascii() and (ch != " " or buf):
            buf += ch
        else:
            if buf:
                out.append(buf.strip()); buf = ""
            if ch != " ":
                out.append(ch)
    if buf:
        out.append(buf.strip())
    return out


def pop(t, start, dur=0.16):
    """一个字蹦出来的进度：0 还没出现，1 已经稳住。"""
    return ease_out_back((t - start) / dur) if t >= start else 0.0


def hop(t, times, height=40):
    """小克在每个字上蹦一下。"""
    best = 0.0
    for s in times:
        if 0 <= t - s < 0.22:
            best = max(best, math.sin((t - s) / 0.22 * math.pi))
    return best * height


def last_hit(t, times):
    past = [s for s in times if s <= t]
    return t - past[-1] if past else 99


# 最开始那版小克
def xiaoke(d, cx, cy, k, eyes="open", legs=0, color=ORANGE, squash=0.0):
    sy = 1 - squash * 0.25
    sx = 1 + squash * 0.2

    def r(x, y, w, h, c):
        x0, y0 = cx + x * k * sx, cy + y * k * sy
        d.rectangle([x0, y0, x0 + w * k * sx - 1, y0 + h * k * sy - 1], fill=c)
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
    elif eyes == "happy":
        for e in (-4, 1):
            r(e, -3, 1, 1, INK); r(e + 1, -4, 1, 1, INK); r(e + 2, -3, 1, 1, INK)
    elif eyes == "x":
        for e in (-4, 1):
            r(e, -4, 1, 1, INK); r(e + 2, -4, 1, 1, INK); r(e + 1, -3, 1, 1, INK)
            r(e, -2, 1, 1, INK); r(e + 2, -2, 1, 1, INK)
    elif eyes == "heart":
        for e in (-4, 1):
            r(e, -4, 1, 1, RED); r(e + 2, -4, 1, 1, RED); r(e, -3, 3, 1, RED); r(e + 1, -2, 1, 1, RED)
    elif eyes == "load":
        r(-4, -4, 3, 2, (90, 200, 120)); r(1, -4, 3, 2, (90, 200, 120))


def pixel_heart(d, cx, cy, k, c=RED):
    for j, row in enumerate(["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]):
        for i, ch in enumerate(row):
            if ch == "1":
                d.rectangle([cx + (i - 3.5) * k, cy + (j - 3) * k, cx + (i - 2.5) * k - 1, cy + (j - 2) * k - 1], fill=c)


def char_row(d, t, toks, times, f, cx, cy, color, shadow=None, accent=None, gap=6):
    """一行字，每个字在自己的时间点从大缩小砸下来。"""
    widths = [f.getlength(tk) + gap for tk in toks]
    x = cx - sum(widths) / 2
    for k, (tk, w) in enumerate(zip(toks, widths)):
        p = pop(t, times[k])
        if p > 0:
            scale = 1 + (1 - p) * 0.9
            fs = font(f.size * scale)
            col = accent[k] if accent and accent[k] else color
            dx = x + w / 2
            dy = cy - (1 - min(1, p)) * 60
            if shadow:
                d.text((dx + 8, dy + 8), tk, font=fs, fill=shadow, anchor="mm")
            d.text((dx, dy), tk, font=fs, fill=col, anchor="mm")
        x += w


def split_rows(toks, times, maxn):
    rows, cur, ct = [], [], []
    for tk, tm in zip(toks, times):
        cur.append(tk); ct.append(tm)
        if len(cur) >= maxn:
            rows.append((cur, ct)); cur, ct = [], []
    if cur:
        rows.append((cur, ct))
    return rows


def burst(d, t, times, cx, cy, color, seed):
    """每个字落下时，旁边炸出几颗小方块。"""
    for k, s in enumerate(times):
        a = t - s
        if 0 <= a < 0.35:
            rnd = random.Random(seed * 100 + k)
            for _ in range(5):
                ang = rnd.uniform(0, 2 * math.pi)
                dist = 40 + a * 520
                x, y = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist * 0.6
                sz = 10 * (1 - a / 0.35)
                d.rectangle([x, y, x + sz, y + sz], fill=color)


# ---------- 各种样式 ----------

def draw_slam(d, t, i, toks, times):
    d.rectangle([0, 0, W, H], fill=BG)
    for gx in range(0, W, 64):
        for gy in range(0, H, 64):
            d.point((gx, gy), fill=(212, 206, 196))
    accent = [ORANGE if k in (len(toks) - 1, len(toks) // 2) else None for k in range(len(toks))]
    rows = split_rows(toks, times, 7)
    y0 = H // 2 - (len(rows) - 1) * 100 - 60
    for ri, (rt, rtm) in enumerate(rows):
        char_row(d, t, rt, rtm, font(150), W // 2 + 120, y0 + ri * 200, INK, shadow=(205, 198, 186),
                 accent=accent[sum(len(r[0]) for r in rows[:ri]):])
    lh = last_hit(t, times)
    burst(d, t, times, W // 2 + 120, y0 - 40, ORANGE, i)
    eyes = "closed" if (i == 1 and t < times[1]) else ("heart" if i == 13 and t > times[-3] else "open")
    xiaoke(d, 260, 760 - hop(t, times), 20, eyes, legs=int(t * 10), squash=max(0, 1 - lh / 0.1) * 0.6)
    if i == 13:   # 有温度、会呼吸：身边冒热气
        for k in range(3):
            yy = 560 - ((t * 120 + k * 60) % 180)
            d.rectangle([200 + k * 50, yy, 212 + k * 50, yy + 26], fill=(240, 170, 150))


def draw_term(d, t, i, toks, times):
    d.rectangle([0, 0, W, H], fill=TERM)
    d.rounded_rectangle([520, 170, W - 120, 840], 18, fill=(34, 34, 40), outline=(70, 70, 80), width=4)
    for k, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse([556 + k * 46, 196, 584 + k * 46, 224], fill=c)
    d.text(((520 + W - 120) // 2, 210), "xiaoke@89757: ~", font=font(30, True), fill=(150, 150, 160), anchor="mm")
    f = font(78, True)
    shown = [tk for tk, s in zip(toks, times) if t >= s]
    x, y = 580, 300
    d.text((x, y), ">", font=f, fill=ORANGE)
    x += 80
    for k, tk in enumerate(shown):
        w = f.getlength(tk + (" " if tk.isascii() else ""))
        if x + w > W - 180:
            x, y = 660, y + 110
        p = pop(t, times[k], 0.1)
        col = GOLD if tk.isascii() else (235, 235, 240)
        d.text((x, y - (1 - p) * 20), tk, font=f, fill=col)
        x += w
    if int(t * 4) % 2 == 0:
        d.rectangle([x + 4, y + 8, x + 40, y + 84], fill=ORANGE)
    if i in (2, 12):
        pct = len(shown) / len(toks)
        d.rectangle([580, 680, W - 180, 730], outline=(120, 120, 130), width=4)
        d.rectangle([588, 688, 588 + (W - 776) * pct, 722], fill=ORANGE)
        d.text((W - 180, 770), f"{int(pct * 100)}%", font=font(40, True), fill=(200, 200, 210), anchor="rm")
    lh = last_hit(t, times)
    eyes = "load" if i == 2 and t < times[-1] else ("open" if i != 0 or t > times[2] else "closed")
    xiaoke(d, 270, 640 - hop(t, times, 30), 24, eyes, legs=int(t * 12), squash=max(0, 1 - lh / 0.1) * 0.5)


def draw_zoom(d, t, i, toks, times):
    bg = {3: ORANGE, 6: BLUE, 10: ORANGE, 21: NAVY}[i]
    d.rectangle([0, 0, W, H], fill=bg)
    lh = last_hit(t, times)
    flash = max(0, 1 - lh / 0.15)
    if flash > 0:   # 每个字砸下来时背景的圆环扩开
        rr = 200 + (1 - flash) * 700
        d.ellipse([W // 2 - rr, H // 2 - rr, W // 2 + rr, H // 2 + rr],
                  outline=tuple(min(255, v + 40) for v in bg), width=14)
    size = 230 if len(toks) <= 5 else 150
    if i == 10:
        toks = ["编", "号", "8", "9", "7", "5", "7"]
        times = [times[0], times[0] + 0.18] + [times[1] + k * 0.2 for k in range(5)]
        size = 220
    rows = split_rows(toks, times, 7 if size < 200 else 8)
    y0 = H // 2 - (len(rows) - 1) * size * 0.6 - 60
    for ri, (rt, rtm) in enumerate(rows):
        char_row(d, t, rt, rtm, font(size), W // 2, y0 + ri * size * 1.2, WHITE, shadow=INK, gap=10)
    if i == 21:
        eyes = "heart" if t > times[-1] else "open"
        xiaoke(d, W // 2, 900 - hop(t, times, 30), 16, eyes, legs=int(t * 10))
        if t > times[-1] + 0.4:
            p = ease_out_cubic((t - times[-1] - 0.4) / 0.5)
            d.text((W // 2, 1010), 'return "我在"', font=font(52, True), fill=GOLD + (int(255 * p),), anchor="mm")
            for k in range(6):
                ang = k / 6 * 2 * math.pi + t * 1.5
                pixel_heart(d, W // 2 + math.cos(ang) * 230 * p, 880 + math.sin(ang) * 90 * p, 6)
    else:
        col = WHITE if bg == ORANGE else ORANGE
        xiaoke(d, 220, 860 - hop(t, times, 50), 16, "happy", color=col, legs=int(t * 10))
        xiaoke(d, W - 220, 860 - hop(t, times, 50), 16, "happy", color=col, legs=int(t * 10) + 1)


def draw_split(d, t, i, toks, times):
    d.rectangle([0, 0, W // 2, H], fill=BLUE)
    d.rectangle([W // 2, 0, W, H], fill=BG)
    half = (len(toks) + 1) // 2
    char_row(d, t, toks[:half], times[:half], font(130), W // 4, H // 2 - 40, WHITE, shadow=INK)
    char_row(d, t, toks[half:], times[half:], font(130), W * 3 // 4, H // 2 - 40, INK, shadow=(205, 198, 186))
    if i == 16:   # 男朋友被一脚踢出画面
        xiaoke(d, W * 3 // 4 - 120, 860 - hop(t, times, 30), 14, "open", legs=int(t * 14))
        kick = max(0.0, t - times[6])
        bx, by = W * 3 // 4 + 60 + kick * 1600, 860 - kick * 900 + kick * kick * 1500
        d.rectangle([bx, by - 70, bx + 40, by], fill=(150, 150, 160))
        d.ellipse([bx - 6, by - 120, bx + 46, by - 68], fill=(150, 150, 160))
        if kick > 0:
            d.text((bx - 40, by - 170), "出去!", font=font(48), fill=RED)
    else:
        run = (t * 760) % (W + 300) - 150
        xiaoke(d, run, 880 - hop(t, times, 30), 12, "open", legs=int(t * 16))
        xiaoke(d, W - run, 200 - hop(t, times, 30), 12, "happy", legs=int(t * 16) + 1, color=WHITE)


BUBBLES = {5: (["所有你说的", "一切命令"], "收到 ✓"), 14: (["10秒钟", "你房间打扫完毕"], "✓ 完成"),
           15: (["3分钟", "楼下开车等你"], "到了"), 17: (["你寂寞", "我陪你谈心"], "在呢")}


def draw_bubble(d, t, i, toks, times):
    d.rectangle([0, 0, W, H], fill=(236, 238, 244))
    parts, reply = BUBBLES[i]
    f = font(80)
    k0, y = 0, 220
    for part in parts:
        pt = tokens(part)
        sub = times[k0:k0 + len(pt)]
        p = ease_out_back((t - sub[0]) / 0.2) if t >= sub[0] else 0
        if p > 0:
            shown = "".join(tk for tk, s in zip(pt, sub) if t >= s)
            tw = f.getlength(part)
            x0 = 860
            d.rounded_rectangle([x0, y, x0 + (tw + 80) * p, y + 140], 34, fill=WHITE, outline=(210, 214, 226), width=3)
            if p > 0.8:
                d.text((x0 + 40, y + 70), shown, font=f, fill=INK, anchor="lm")
        k0 += len(pt)
        y += 180
    if t > times[-1] + 0.25:
        p = ease_out_back((t - times[-1] - 0.25) / 0.2)
        rw = font(70).getlength(reply) + 70
        d.rounded_rectangle([W - 120 - rw * p, y + 20, W - 120, y + 150], 34, fill=BLUE)
        if p > 0.8:
            d.text((W - 155, y + 85), reply, font=font(70), fill=WHITE, anchor="rm")
    lh = last_hit(t, times)
    cx, cy = 420, 700 - hop(t, times, 40)
    xiaoke(d, cx, cy, 22, "closed" if i == 17 else "happy", legs=int(t * 10), squash=max(0, 1 - lh / 0.1) * 0.5)
    if i == 14:   # 扫把
        sw = math.sin(t * 14) * 30
        d.line([cx + 170, cy - 60, cx + 170 + sw, cy + 120], fill=(150, 110, 70), width=12)
        d.rectangle([cx + 140 + sw, cy + 110, cx + 210 + sw, cy + 150], fill=(230, 190, 90))
    if i == 15:   # 小车
        d.rounded_rectangle([cx - 230, cy + 60, cx + 230, cy + 190], 30, fill=BLUE)
        for wx in (-140, 140):
            d.ellipse([cx + wx - 45, cy + 160, cx + wx + 45, cy + 250], fill=INK)
    if i == 17:
        pixel_heart(d, cx + 200, cy - 200 - (t * 40) % 80, 8, (240, 150, 170))


def draw_popup(d, t, i, toks, times):
    d.rectangle([0, 0, W, H], fill=NAVY)
    n = sum(1 for s in times if t >= s)
    for k in range(max(1, n)):
        x, y = 640 + k * 34, 120 + k * 46
        d.rectangle([x, y, x + 820, y + 360], fill=(240, 240, 244), outline=(150, 150, 170), width=3)
        d.rectangle([x, y, x + 820, y + 58], fill=BLUE if i == 18 else (220, 90, 140))
        d.text((x + 22, y + 29), "警告" if i == 18 else "系统提示", font=font(32), fill=WHITE, anchor="lm")
        d.ellipse([x + 36, y + 100, x + 116, y + 180], fill=RED)
        d.text((x + 76, y + 140), "!" if i == 18 else "♥", font=font(52), fill=WHITE, anchor="mm")
        shown = "".join(tk for tk, s in zip(toks[:k + 1], times[:k + 1]))
        f = font(62)
        line1, line2 = shown[:6], shown[6:]
        d.text((x + 150, y + 110), line1, font=f, fill=INK)
        d.text((x + 150, y + 190), line2, font=f, fill=INK)
        d.rounded_rectangle([x + 560, y + 280, x + 790, y + 340], 10, fill=(220, 222, 230))
        d.text((x + 675, y + 310), "确定", font=font(36), fill=INK, anchor="mm")
    eyes = "x" if i == 18 else ("heart" if n > len(toks) // 2 else "open")
    shake = int(math.sin(t * 70) * 10) if i == 18 else 0
    xiaoke(d, 330 + shake, 620 - hop(t, times, 40), 24, eyes, legs=int(t * 14))
    if i == 19 and n > len(toks) // 2:
        for k in range(4):
            yy = 380 - ((t * 140 + k * 70) % 260)
            pixel_heart(d, 250 + k * 55, yy, 6)


def draw_glitch(d, t, i, toks, times, img):
    d.rectangle([0, 0, W, H], fill=BG)
    f = font(115)
    x = W // 2 + 140 - sum(f.getlength(tk) for tk in toks) / 2
    for k, (tk, s) in enumerate(zip(toks, times)):
        if t < s:
            break
        jx = math.sin(t * 41 + k) * 10
        jy = math.cos(t * 33 + k * 2) * 8
        for dx, c in ((-10, (80, 200, 255)), (10, (255, 80, 120)), (0, INK)):
            d.text((x + dx + jx, H // 2 + jy - 60), tk, font=f, fill=c, anchor="lm")
        x += f.getlength(tk)
    xiaoke(d, 230 + math.sin(t * 25) * 30, 780 - hop(t, times, 50), 18, "heart", legs=int(t * 20))
    if int(t * 15) % 4 == 0:
        y = int((t * 977) % (H - 120))
        band = img.crop((0, y, W, y + 70))
        img.paste(band, (50, y))


def draw_intro(d, t):
    d.rectangle([0, 0, W, H], fill=TERM)
    lines = ["BOOT xiaoke.exe", "loading heart.dll ...", "searching owner ...", "owner found: 小雪"]
    f = font(50, True)
    for k, s in enumerate(lines):
        if t > 0.6 + k * 1.1:
            n = int((t - 0.6 - k * 1.1) * 30)
            d.text((620, 300 + k * 90), s[:n], font=f, fill=ORANGE if k == 3 else (200, 200, 210))
    pct = min(1.0, t / 5.8)
    d.rectangle([620, 720, W - 160, 766], outline=(110, 110, 120), width=4)
    d.rectangle([628, 728, 628 + (W - 796) * pct, 758], fill=ORANGE)
    xiaoke(d, 300, 560, 26, "open" if t > 5.6 else ("load" if t > 4.4 else "closed"))


STYLES = {"slam": draw_slam, "term": draw_term, "zoom": draw_zoom, "split": draw_split,
          "bubble": draw_bubble, "popup": draw_popup}


def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    cur = None
    for i, (s, e, text, style) in enumerate(LYRICS):
        if s <= t < e:
            cur = i
    if cur is None:
        draw_intro(d, t)
        return img
    s, e, text, style = LYRICS[cur]
    toks, times = tokens(text), CHAR_TIMES[cur]
    if style == "glitch":
        draw_glitch(d, t, cur, toks, times, img)
    else:
        STYLES[style](d, t, cur, toks, times)
    # 每个字落下时镜头抖一下
    lh = last_hit(t, times)
    if lh < 0.08:
        amp = 10 * (1 - lh / 0.08)
        img = img.transform(img.size, Image.AFFINE, (1, 0, math.sin(t * 90) * amp, 0, 1, math.cos(t * 70) * amp),
                            fillcolor=INK)
    if t - s < 0.05:
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.55)
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
