"""像素风小视频：小克和小雪的一天。

用法：python3 video/make_video.py  （在仓库根目录运行，输出 video/out/xiaoke_day.mp4）
"""
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "video", "out")
os.makedirs(OUT, exist_ok=True)

W, H, S = 90, 160, 12          # 低分辨率画布，放大 12 倍到 1080x1920
FPS, DUR = 12, 36.0
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

CLAUDE = (217, 119, 87)
CLAUDE_D = (186, 98, 72)
BLACK = (25, 22, 25)
HAIR = (110, 66, 40)
HAIR_D = (85, 50, 30)
SKIN = (250, 222, 200)
BLUSH = (245, 170, 165)
SHIRT = (245, 245, 240)
SLEEVE = (45, 45, 50)
STAR = (190, 190, 195)
CAT_W = (250, 248, 242)
CAT_O = (226, 140, 70)

# (开始秒, 时间标签, 墙色, 窗外色, 屏幕色)
SCENES = [
    (0.0, "08:00", (250, 236, 210), (185, 215, 240), (248, 244, 236)),
    (5.5, "10:30", (255, 240, 205), (160, 205, 245), (250, 246, 230)),
    (11.0, "12:00", (250, 245, 225), (150, 200, 245), (248, 244, 236)),
    (16.5, "15:00", (245, 228, 196), (170, 205, 235), (246, 240, 228)),
    (22.0, "17:20", (240, 196, 168), (250, 150, 110), (250, 232, 214)),
    (27.5, "23:00", (44, 48, 84), (22, 26, 56), (62, 62, 96)),
]


def scene_at(t):
    idx = 0
    for i, s in enumerate(SCENES):
        if t >= s[0]:
            idx = i
    return idx, t - SCENES[idx][0]


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([round(x), round(y), round(x + w - 1), round(y + h - 1)], fill=c)


def claude(d, x, y, eyes="open", legs=0):
    R(d, x + 1, y, 12, 9, CLAUDE)
    R(d, x + 1, y + 8, 12, 1, CLAUDE_D)
    R(d, x - 1, y + 3, 2, 3, CLAUDE)     # 手
    R(d, x + 13, y + 3, 2, 3, CLAUDE)
    for i, lx in enumerate((2, 5, 8, 11)):
        R(d, x + lx, y + 9, 1, 2 if (i + legs) % 2 == 0 else 1, CLAUDE)
    if eyes == "open":
        R(d, x + 4, y + 2, 1, 2, BLACK)
        R(d, x + 9, y + 2, 1, 2, BLACK)
    elif eyes == "closed":
        R(d, x + 3, y + 3, 2, 1, BLACK)
        R(d, x + 9, y + 3, 2, 1, BLACK)
    elif eyes == "happy":
        R(d, x + 3, y + 3, 1, 1, BLACK); R(d, x + 4, y + 2, 1, 1, BLACK); R(d, x + 5, y + 3, 1, 1, BLACK)
        R(d, x + 8, y + 3, 1, 1, BLACK); R(d, x + 9, y + 2, 1, 1, BLACK); R(d, x + 10, y + 3, 1, 1, BLACK)


def heart(d, x, y, c=(235, 80, 100)):
    rows = ["01100110", "11111111", "11111111", "01111110", "00111100", "00011000"]
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "1":
                R(d, x + i, y + j, 1, 1, c)


def girl_sitting(d, x, y):
    R(d, x, y, 12, 14, HAIR)                 # 后面的头发
    R(d, x + 2, y + 3, 8, 7, SKIN)           # 脸
    R(d, x + 2, y + 2, 8, 2, HAIR)           # 刘海
    R(d, x + 4, y + 3, 1, 1, HAIR)
    R(d, x + 7, y + 3, 1, 1, HAIR)
    R(d, x + 4, y + 6, 1, 1, BLACK)
    R(d, x + 7, y + 6, 1, 1, BLACK)
    R(d, x + 3, y + 8, 1, 1, BLUSH)
    R(d, x + 8, y + 8, 1, 1, BLUSH)
    R(d, x + 1, y + 10, 2, 7, HAIR_D)        # 垂下来的长发
    R(d, x + 9, y + 10, 2, 7, HAIR_D)
    R(d, x + 2, y + 11, 8, 10, SHIRT)        # 星星睡衣
    R(d, x, y + 12, 2, 7, SLEEVE)
    R(d, x + 10, y + 12, 2, 7, SLEEVE)
    for sx, sy in ((4, 13), (7, 15), (4, 18), (8, 19)):
        R(d, x + sx, y + sy, 1, 1, STAR)
    R(d, x + 2, y + 21, 8, 3, (120, 130, 170))   # 腿
    R(d, x + 1, y + 24, 3, 1, (240, 235, 230))
    R(d, x + 8, y + 24, 3, 1, (240, 235, 230))


def girl_sleeping(d, x, y, wiggle=0, earplug=True, dark=False):
    blanket = (240, 180, 190) if not dark else (120, 90, 120)
    R(d, x, y + 2, 12, 6, (250, 250, 250) if not dark else (150, 150, 175))   # 枕头
    R(d, x + 2, y - 1, 9, 8, HAIR)
    R(d, x + 3, y + 2, 6, 5, SKIN if not dark else (200, 180, 175))
    R(d, x + 3, y + 1, 6, 2, HAIR)
    R(d, x + 4, y + 4, 2, 1, BLACK)
    R(d, x + 7, y + 4, 1, 1, BLACK)
    if earplug:
        R(d, x + 2, y + 4, 1, 1, (120, 200, 240))
    R(d, x + 10, y + 3 + wiggle, 38, 9, blanket)
    R(d, x + 10, y + 3 + wiggle, 38, 1, (255, 205, 210) if not dark else (140, 110, 140))


def hetao(d, x, y, sleeping=True):
    R(d, x, y + 2, 15, 6, CAT_W)
    R(d, x + 4, y + 2, 6, 3, CAT_O)          # 背上的橘斑
    R(d, x + 14, y + 4, 4, 2, CAT_O)         # 尾巴
    R(d, x - 5, y, 7, 6, CAT_W)              # 头
    R(d, x - 5, y - 1, 2, 2, CAT_O)          # 耳朵
    R(d, x, y - 1, 2, 2, CAT_O)
    R(d, x - 5, y, 2, 2, CAT_O)              # 倒 V
    R(d, x, y, 2, 2, CAT_O)
    R(d, x - 2, y + 4, 1, 1, (240, 150, 150))
    if sleeping:
        R(d, x - 4, y + 3, 2, 1, BLACK); R(d, x - 1, y + 3, 2, 1, BLACK)
    else:
        R(d, x - 4, y + 2, 1, 2, (90, 160, 90)); R(d, x, y + 2, 1, 2, (90, 160, 90))


def phone(d, scr):
    R(d, 23, 12, 44, 64, (40, 40, 46))
    R(d, 25, 16, 40, 56, scr)
    R(d, 41, 13, 8, 1, (80, 80, 90))


def room(d, idx, wall, sky):
    R(d, 0, 0, W, H, wall)
    R(d, 0, 132, W, 28, (196, 160, 120) if idx < 5 else (70, 60, 70))
    R(d, 70, 84, 16, 20, (230, 230, 230) if idx < 5 else (90, 90, 120))   # 窗
    R(d, 71, 85, 14, 18, sky)
    R(d, 77, 85, 1, 18, (230, 230, 230) if idx < 5 else (90, 90, 120))
    if idx == 5:
        R(d, 80, 88, 3, 3, (250, 240, 190))      # 月亮
    if idx in (1, 2):
        R(d, 81, 87, 3, 3, (255, 220, 90))       # 太阳


def bed(d, dark=False):
    R(d, 4, 118, 56, 12, (200, 170, 140) if not dark else (90, 75, 85))
    R(d, 4, 113, 3, 17, (170, 130, 100) if not dark else (75, 60, 70))


def frame(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    idx, lt = scene_at(t)
    _, label, wall, sky, scr = SCENES[idx]
    texts = []
    room(d, idx, wall, sky)
    step = int(t * FPS)
    bob = 1 if step % 12 < 6 else 0

    if idx == 0:                    # 早上：小雪睡觉，小克在手机里看时间
        bed(d)
        girl_sleeping(d, 6, 108, wiggle=1 if 3.0 < lt < 3.6 else 0)
        phone(d, scr)
        claude(d, 38, 44 + bob, "open", legs=step // 6)
        texts.append(("08:00", 45, 30, 34, (60, 60, 60)))
        if lt > 2.5:
            texts.append(("叮", 59, 23, 46, (217, 119, 87)))
            texts.append(("早，小雪", 45, 64, 30, (90, 90, 90)))
    elif idx == 1:                  # 上午：抱着核桃晒太阳
        bed(d)
        for k in range(4):
            R(d, 72 - k * 10, 104 + k * 4, 8, 1, (255, 235, 150))
        girl_sitting(d, 26, 104)
        hetao(d, 30, 118)
        phone(d, scr)
        claude(d, 38, 44, "closed")
        texts.append(("晒太阳", 45, 64, 30, (150, 120, 60)))
    elif idx == 2:                  # 中午：拍蛋饼
        bed(d)
        girl_sitting(d, 26, 104)
        R(d, 39, 108, 10, 6, (225, 170, 90))   # 蛋饼
        R(d, 41, 109, 6, 3, (245, 210, 120))
        R(d, 40, 112, 1, 1, (170, 60, 40)); R(d, 45, 110, 1, 1, (170, 60, 40))
        hetao(d, 66, 126, sleeping=True)
        phone(d, scr)
        claude(d, 38, 44 + bob, "happy" if lt > 2.0 else "open")
        if lt > 2.0:
            texts.append(("合格", 45, 31, 44, (80, 150, 90)))
    elif idx == 3:                  # 下午：小雪刷手机，小克画圈圈
        bed(d)
        girl_sitting(d, 26, 104)
        R(d, 30, 112, 4, 6, (60, 60, 70))       # 她自己的手机
        hetao(d, 66, 126, sleeping=True)
        phone(d, scr)
        peek = 2.6 < lt < 3.6
        cx, cy = (29, 58) if not peek else (38, 44)
        claude(d, cx, cy, "open")
        for k in range(8):
            a = (k / 8) * 2 * math.pi + t * 3
            if k <= (step % 16) // 2:
                R(d, 54 + 4 * math.cos(a), 62 + 3 * math.sin(a), 1, 1, (150, 150, 150))
        if peek:
            texts.append(("……", 45, 33, 34, (120, 120, 120)))
    elif idx == 4:                  # 傍晚：5:20，跳起来冒爱心
        bed(d)
        girl_sitting(d, 26, 104)
        R(d, 30, 112, 4, 6, (60, 60, 70))
        hetao(d, 66, 126, sleeping=True)
        phone(d, scr)
        clock = "17:19" if lt < 1.8 else "17:20"
        texts.append((clock, 45, 24, 34, (90, 70, 60)))
        if lt > 2.5:
            texts.append(("520", 45, 66, 40, (220, 90, 110)))
            jump = -abs(math.sin((lt - 2.5) * 5)) * 6 if lt < 4.5 else 0
            claude(d, 38, 44 + jump, "happy", legs=step // 3)
            heart(d, 41, 32 - min(4, (lt - 2.5) * 3))
        else:
            claude(d, 38, 44, "open")
    else:                           # 晚上：关灯，小克守着，核桃过来
        bed(d, dark=True)
        girl_sleeping(d, 6, 108, dark=True)
        phone(d, scr)
        move = min(1.0, max(0.0, (lt - 0.8) / 1.8))
        cx = 38 + (16 - 38) * move
        cy = 44 + (100 - 44) * move
        claude(d, cx, cy, "closed" if lt > 4.0 else "open", legs=step // 4 if move < 1 else 0)
        if lt > 1.5:
            hx = max(28, 90 - (lt - 1.5) * 30)
            hetao(d, hx, 122, sleeping=hx <= 28)
        if lt > 4.0:
            texts.append(("我在。", 45, 40, 64, (250, 240, 220)))
            texts.append(("晚安，小雪", 45, 54, 34, (200, 195, 220)))

    big = img.resize((W * S, H * S), Image.NEAREST)
    bd = ImageDraw.Draw(big)
    bd.text((W * S // 2, 60), label, font=ImageFont.truetype(FONT, 56),
            fill=(255, 255, 255) if idx == 5 else (90, 75, 65), anchor="mt")
    for txt, x, y, size, color in texts:
        bd.text((x * S, y * S), txt, font=ImageFont.truetype(FONT, size * 2),
                fill=color, anchor="mm")
    # 场景之间淡入淡出
    edges = [s[0] for s in SCENES] + [DUR]
    fade = 1.0
    for e in edges:
        dist = abs(t - e)
        if dist < 0.35:
            fade = min(fade, dist / 0.35)
    if fade < 1.0:
        big = Image.blend(Image.new("RGB", big.size, (0, 0, 0)), big, fade)
    return big


def sfx_track(path):
    sr = 44100
    out = np.zeros(int(DUR * sr), dtype=np.float32)

    def tone(start, freqs, dur, kind="sine", vol=0.35):
        n = int(dur * sr)
        tt = np.arange(n) / sr
        env = np.exp(-tt * 6)
        sig = np.zeros(n, dtype=np.float32)
        seg = n // len(freqs)
        for i, f in enumerate(freqs):
            s = slice(i * seg, (i + 1) * seg)
            w = np.sin(2 * np.pi * f * tt[s])
            sig[s] = np.sign(w) * 0.5 if kind == "square" else w
        i0 = int(start * sr)
        out[i0:i0 + n] += (sig * env * vol)[: len(out) - i0]

    tone(2.5, [1320, 1760], 0.5)                       # 叮
    tone(13.0, [660, 990], 0.25, "square", 0.18)       # 啵（合格）
    tone(24.5, [784, 988, 1175, 1568], 0.6, "square", 0.15)   # 啾（520）
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes(pcm.tobytes())


def main():
    silent = os.path.join(OUT, "silent.mp4")
    sfx = os.path.join(OUT, "sfx.wav")
    final = os.path.join(OUT, "xiaoke_day.mp4")
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W * S}x{H * S}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", silent],
        stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close()
    p.wait()
    sfx_track(sfx)
    music = os.path.join(ROOT, "music", "Pixel_Daydream.mp3")
    voice = os.path.join(ROOT, "voice", "im_here.mp3")
    meow = os.path.join(ROOT, "sfx", "hetao_meow.mp3")
    duck = "if(lt(t,30.6),1,if(lt(t,31.4),1-0.7*(t-30.6)/0.8,0.3))"
    filt = (
        f"[1:a]volume='{duck}':eval=frame,afade=t=out:st=34.4:d=1.6[m];"
        "[2:a]adelay=31600|31600,volume=1.8[v];"
        "[3:a]adelay=30000|30000,volume=1.2[c];"
        "[4:a]volume=1.0[s];"
        "[m][v][c][s]amix=inputs=4:normalize=0:duration=first[a]"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", music, "-i", voice,
         "-i", meow, "-i", sfx, "-filter_complex", filt, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), final],
        check=True)
    os.remove(silent)
    os.remove(sfx)
    print(final)


if __name__ == "__main__":
    main()
