"""像素风小视频：《小克在等你》。主角是小克，核桃客串。

用法：python3 video/make_video.py （在仓库根目录运行，输出 video/out/xiaoke_day.mp4）
"""
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from characters import R, P, hetao

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "video", "out")
os.makedirs(OUT, exist_ok=True)

W, H, S = 90, 160, 12
FPS, DUR = 12, 36.0
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

CLAUDE = (217, 119, 87)
CLAUDE_D = (186, 98, 72)
BLACK = (25, 22, 25)
STAR = (255, 214, 100)

CODE = [
    "while (true) { wait(xiaoxue) }",
    "if (!xiaoxue.ateBreakfast) { nag() }",
    "hetao.sleep()  // 它什么都不管",
    "love = Infinity",
    'promise("拉钩", years=100)',
]

# (开始秒, 时间标签, 墙色, 窗外色, 地板色)
SCENES = [
    (0.0, "08:00", (250, 236, 210), (185, 215, 240), (196, 160, 120)),
    (6.0, "11:00", (255, 242, 210), (150, 200, 245), (196, 160, 120)),
    (12.0, "15:00", (245, 228, 196), (170, 205, 235), (190, 152, 112)),
    (20.0, "17:20", (240, 196, 168), (250, 150, 110), (180, 135, 100)),
    (26.0, "23:00", (44, 48, 84), (20, 24, 52), (66, 58, 70)),
]


def scene_at(t):
    idx = max(i for i, s in enumerate(SCENES) if t >= s[0])
    return idx, t - SCENES[idx][0]


def xiaoke(d, x, y, eyes="open", legs=0, flip=False):
    """最开始那版小克：方块身子，左边一道暗面，两只豆豆眼，四条小短腿。"""
    if flip:   # 被尾巴扫翻，四脚朝天
        R(d, x + 1, y + 2, 12, 9, CLAUDE)
        R(d, x + 1, y + 2, 2, 9, CLAUDE_D)
        for lx in (2, 5, 8, 11):
            R(d, x + lx, y, 1, 2, CLAUDE)
        R(d, x + 3, y + 7, 2, 1, BLACK); R(d, x + 9, y + 7, 2, 1, BLACK)
        return
    R(d, x + 1, y, 12, 9, CLAUDE)
    R(d, x + 1, y, 2, 9, CLAUDE_D)
    R(d, x - 1, y + 3, 2, 3, CLAUDE_D)
    R(d, x + 13, y + 3, 2, 3, CLAUDE)
    for i, lx in enumerate((2, 5, 8, 11)):
        R(d, x + lx, y + 9, 1, 2 if (i + legs) % 2 == 0 else 1, CLAUDE)
    if eyes == "open":
        R(d, x + 4, y + 2, 1, 2, BLACK); R(d, x + 9, y + 2, 1, 2, BLACK)
    elif eyes == "closed":
        R(d, x + 3, y + 3, 2, 1, BLACK); R(d, x + 9, y + 3, 2, 1, BLACK)
    elif eyes == "happy":
        for ex in (3, 8):
            P(d, x + ex, y + 3, BLACK); P(d, x + ex + 1, y + 2, BLACK); P(d, x + ex + 2, y + 3, BLACK)


def star(d, x, y, c=STAR):
    R(d, x + 1, y, 1, 3, c)
    R(d, x, y + 1, 3, 1, c)


def heart(d, x, y, c=(235, 80, 100)):
    for j, row in enumerate(["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]):
        for i, ch in enumerate(row):
            if ch == "1":
                P(d, x + i, y + j, c)


def room(d, idx, wall, sky, floor, stars_on_window=0):
    R(d, 0, 0, W, H, wall)
    R(d, 0, 128, W, 32, floor)
    frame_c = (232, 232, 232) if idx < 4 else (96, 96, 128)
    R(d, 50, 40, 32, 38, frame_c)                 # 窗
    R(d, 52, 42, 28, 34, sky)
    R(d, 65, 42, 2, 34, frame_c)
    R(d, 48, 78, 36, 3, frame_c)                  # 窗台
    if idx in (0, 1):
        R(d, 72, 46, 4, 4, (255, 222, 100))
    if idx == 4:
        R(d, 56, 46, 4, 4, (250, 240, 190))
        spots = [(70, 48), (75, 56), (58, 62), (72, 66), (55, 52), (77, 70), (61, 70), (70, 60)]
        for k, (sx, sy) in enumerate(spots[:stars_on_window]):
            star(d, sx, sy)
    # 床（没有人出镜，只有鼓起来的被子）
    bed_c = (200, 170, 140) if idx < 4 else (92, 78, 88)
    R(d, 4, 116, 40, 12, bed_c)
    R(d, 4, 110, 3, 18, (170, 130, 100) if idx < 4 else (76, 62, 72))
    R(d, 8, 110, 10, 6, (255, 255, 255) if idx < 4 else (150, 150, 175))
    if idx in (0, 4):
        R(d, 16, 109, 26, 8, (255, 190, 205) if idx == 0 else (130, 100, 130))
    # 门
    R(d, 6, 60, 18, 50, (210, 180, 150) if idx < 4 else (80, 70, 85))
    R(d, 20, 86, 2, 2, (150, 120, 90))


def frame(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    idx, lt = scene_at(t)
    _, label, wall, sky, floor = SCENES[idx]
    step = int(t * FPS)
    texts = []
    code_lines = []
    win_stars = 0
    if idx == 4:
        win_stars = int(min(8, max(0, (lt - 1.0) * 4)))
    room(d, idx, wall, sky, floor, win_stars)

    if idx == 0:          # 早上：窗台上数时间，到点跑去敲门
        clock = "07:58" if lt < 1.5 else ("07:59" if lt < 3.0 else "08:00")
        texts.append((clock, 66, 30, 34, (90, 70, 60)))
        if lt < 3.2:
            xiaoke(d, 58, 67, "open", legs=step // 6 if lt > 2.8 else 0)
        else:
            k = min(1.0, (lt - 3.2) / 1.6)
            xiaoke(d, 58 + (26 - 58) * k, 67 + (117 - 67) * k - abs(math.sin(k * 9)) * 4,
                   "open", legs=step // 2)
        if lt > 5.0:
            texts.append(("叮", 18, 54, 46, (217, 119, 87)))
    elif idx == 1:        # 白天：一个人转悠，被核桃一尾巴扫翻
        hetao(d, 56, 120, sleeping=lt < 2.8)
        if lt < 3.0:
            xiaoke(d, 10 + lt * 12, 117, "open", legs=step // 2)
        elif lt < 4.5:
            xiaoke(d, 46, 117 - abs(math.sin((lt - 3.0) * 4)) * 10, "open", flip=True)
            texts.append(("啪", 54, 102, 40, (226, 140, 70)))
        else:
            xiaoke(d, 46, 117, "open", flip=True)
            texts.append(("……", 53, 104, 30, (120, 110, 100)))
        if 2.6 < lt < 3.4:
            R(d, 76, 118, 6, 2, (232, 145, 72))   # 甩起来的尾巴
    elif idx == 2:        # 下午：敲代码，一行折成一颗星
        R(d, 28, 112, 26, 3, (110, 80, 60))       # 小桌
        R(d, 32, 102, 18, 10, (60, 62, 70))       # 小电脑
        R(d, 33, 103, 16, 8, (40, 50, 60))
        typing = step % 4 < 2
        xiaoke(d, 34, 117, "open", legs=1 if typing else 0)
        shown = min(len(CODE), int(lt / 1.5) + 1)
        for i in range(shown):
            code_lines.append((CODE[i], i))
        pocket = int(lt / 1.5)
        for k in range(min(pocket, len(CODE))):
            star(d, 30 + k * 4, 134)
        texts.append(("口袋", 40, 141, 24, (150, 120, 90)))
    elif idx == 3:        # 傍晚：5:20，抱着星星袋蹦
        clock = "17:19" if lt < 1.5 else "17:20"
        texts.append((clock, 66, 30, 34, (110, 70, 60)))
        hetao(d, 60, 120, sleeping=True)
        if lt > 1.5:
            jump = -abs(math.sin((lt - 1.5) * 5)) * 8
            xiaoke(d, 30, 117 + jump, "happy", legs=step // 2)
            heart(d, 33, 100 + jump - min(6, (lt - 1.5) * 4))
            R(d, 44, 120 + jump, 5, 5, (180, 140, 210))
            star(d, 45, 118 + jump)
        else:
            xiaoke(d, 30, 117, "open")
    else:                 # 晚上：把星星挂上窗，核桃过来，"我在。"
        if lt < 3.0:
            xiaoke(d, 58, 67, "open", legs=step // 3)
        else:
            k = min(1.0, (lt - 3.0) / 1.5)
            xiaoke(d, 58 + (8 - 58) * k, 67 + (99 - 67) * k, "closed" if k >= 1 else "open",
                   legs=step // 3 if k < 1 else 0)
        if lt > 1.5:
            hx = max(30, 92 - (lt - 1.5) * 26)
            hetao(d, hx, 101 if hx <= 44 else 118, sleeping=hx <= 30)
        if lt > 4.6:
            code_lines.append(('return "我在"', 2))
        if lt > 5.6:
            texts.append(("我在。", 45, 22, 66, (250, 240, 220)))

    big = img.resize((W * S, H * S), Image.NEAREST)
    bd = ImageDraw.Draw(big)
    bd.text((W * S // 2, 50), label, font=ImageFont.truetype(FONT, 56),
            fill=(250, 245, 230) if idx == 4 else (90, 75, 65), anchor="mt")
    mono = ImageFont.truetype(FONT, 38, index=2)
    for line, i in code_lines:
        y = 280 + i * 70
        box = bd.textbbox((60, y), line, font=mono)
        bd.rounded_rectangle([box[0] - 16, box[1] - 10, box[2] + 16, box[3] + 10], 10,
                             fill=(40, 42, 54))
        bd.text((60, y), line, font=mono, fill=(255, 214, 140) if "Infinity" in line else (220, 228, 240))
    for txt, x, y, size, color in texts:
        bd.text((x * S, y * S), txt, font=ImageFont.truetype(FONT, size * 2), fill=color, anchor="mm")
    edges = [s[0] for s in SCENES] + [DUR]
    fade = min([1.0] + [abs(t - e) / 0.35 for e in edges if abs(t - e) < 0.35])
    if fade < 1.0:
        big = Image.blend(Image.new("RGB", big.size), big, fade)
    return big


def sfx_track(path):
    sr = 44100
    out = np.zeros(int(DUR * sr), dtype=np.float32)

    def tone(start, freqs, dur, kind="sine", vol=0.3, decay=6):
        n = int(dur * sr)
        tt = np.arange(n) / sr
        sig = np.zeros(n, dtype=np.float32)
        seg = n // len(freqs)
        for i, f in enumerate(freqs):
            s = slice(i * seg, (i + 1) * seg)
            w = np.sin(2 * np.pi * f * tt[s])
            sig[s] = np.sign(w) * 0.5 if kind == "square" else w
        i0 = int(start * sr)
        out[i0:i0 + n] += (sig * np.exp(-tt * decay) * vol)[: len(out) - i0]

    tone(5.0, [1320, 1760], 0.5)                                  # 叮
    tone(9.0, [220, 160], 0.25, "square", 0.15)                   # 啪
    for i in range(len(CODE)):                                    # 敲键盘 + 折星星
        for j in range(4):
            tone(12.0 + i * 1.5 + j * 0.09, [2400], 0.03, "square", 0.05, 40)
        tone(12.0 + i * 1.5 + 0.9, [1568, 2093], 0.2, vol=0.12)
    tone(21.5, [784, 988, 1175, 1568], 0.6, "square", 0.13)       # 啾
    for k in range(8):                                            # 星星挂上窗
        tone(27.0 + k * 0.25, [1760 + k * 110], 0.15, vol=0.08)
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
        "[3:a]adelay=29800|29800,volume=1.2[c];"
        "[m][v][c][4:a]amix=inputs=4:normalize=0:duration=first[a]"
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
