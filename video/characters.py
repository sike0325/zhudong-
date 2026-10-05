"""可爱版像素人设：小雪、小克、核桃。被 make_video.py 和人设图共用。"""

CLAUDE = (217, 119, 87)
CLAUDE_D = (186, 98, 72)
BLACK = (40, 30, 35)
HAIR = (120, 72, 44)
HAIR_D = (92, 54, 34)
HAIR_L = (150, 98, 64)
SKIN = (255, 228, 210)
BLUSH = (255, 170, 175)
WHITE = (255, 255, 255)
SHIRT = (250, 250, 248)
SHIRT_D = (228, 228, 232)
SLEEVE = (60, 58, 66)
STAR = (255, 205, 90)
PANTS = (176, 190, 235)
SOCK = (255, 255, 255)
BOW = (255, 150, 180)
CAT_W = (252, 250, 245)
CAT_O = (232, 145, 72)


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([round(x), round(y), round(x + w - 1), round(y + h - 1)], fill=c)


def P(d, x, y, c):
    R(d, x, y, 1, 1, c)


def xiaoxue(d, x, y, eyes="open", blink=False, arms="down"):
    """Q 版小雪，22 宽 × 32 高。大头、大眼睛、八字刘海、星星睡衣、粉蝴蝶结。"""
    # 头发后层
    R(d, x + 2, y + 2, 18, 20, HAIR)
    R(d, x + 1, y + 6, 20, 14, HAIR)
    R(d, x + 2, y + 20, 3, 4, HAIR_D)
    R(d, x + 17, y + 20, 3, 4, HAIR_D)
    # 脸
    R(d, x + 4, y + 5, 14, 13, SKIN)
    R(d, x + 5, y + 18, 12, 1, SKIN)
    # 八字刘海
    R(d, x + 3, y + 2, 16, 4, HAIR)
    R(d, x + 4, y + 6, 4, 2, HAIR)
    R(d, x + 14, y + 6, 4, 2, HAIR)
    R(d, x + 4, y + 8, 2, 2, HAIR)
    R(d, x + 16, y + 8, 2, 2, HAIR)
    R(d, x + 10, y + 2, 2, 3, HAIR_L)
    R(d, x + 6, y + 3, 3, 1, HAIR_L)
    # 蝴蝶结
    R(d, x + 16, y + 1, 2, 3, BOW)
    R(d, x + 19, y + 1, 2, 3, BOW)
    R(d, x + 18, y + 2, 1, 1, (230, 110, 150))
    # 眼睛
    if eyes == "closed" or blink:
        R(d, x + 6, y + 12, 3, 1, BLACK)
        R(d, x + 13, y + 12, 3, 1, BLACK)
    elif eyes == "happy":
        P(d, x + 6, y + 12, BLACK); P(d, x + 7, y + 11, BLACK); P(d, x + 8, y + 12, BLACK)
        P(d, x + 13, y + 12, BLACK); P(d, x + 14, y + 11, BLACK); P(d, x + 15, y + 12, BLACK)
    else:
        for ex in (6, 13):
            R(d, x + ex, y + 10, 3, 4, BLACK)
            P(d, x + ex, y + 10, WHITE)
            P(d, x + ex + 2, y + 13, (90, 70, 80))
    # 腮红和嘴
    R(d, x + 5, y + 14, 2, 1, BLUSH)
    R(d, x + 15, y + 14, 2, 1, BLUSH)
    P(d, x + 10, y + 15, (220, 120, 120))
    P(d, x + 11, y + 15, (220, 120, 120))
    # 身体：星星睡衣
    R(d, x + 6, y + 19, 10, 8, SHIRT)
    R(d, x + 6, y + 26, 10, 1, SHIRT_D)
    P(d, x + 8, y + 21, STAR); P(d, x + 13, y + 22, STAR); P(d, x + 10, y + 24, STAR)
    if arms == "up":
        R(d, x + 3, y + 17, 3, 3, SLEEVE); R(d, x + 16, y + 17, 3, 3, SLEEVE)
        P(d, x + 3, y + 16, SKIN); P(d, x + 18, y + 16, SKIN)
    elif arms == "hold":
        R(d, x + 5, y + 20, 3, 4, SLEEVE); R(d, x + 14, y + 20, 3, 4, SLEEVE)
        R(d, x + 8, y + 23, 2, 1, SKIN); R(d, x + 12, y + 23, 2, 1, SKIN)
    else:
        R(d, x + 4, y + 20, 2, 5, SLEEVE); R(d, x + 16, y + 20, 2, 5, SLEEVE)
        P(d, x + 4, y + 25, SKIN); P(d, x + 17, y + 25, SKIN)
    # 腿和袜子
    R(d, x + 7, y + 27, 3, 3, PANTS)
    R(d, x + 12, y + 27, 3, 3, PANTS)
    R(d, x + 7, y + 30, 3, 2, SOCK)
    R(d, x + 12, y + 30, 3, 2, SOCK)


def xiaoxue_sleeping(d, x, y, blanket=(255, 190, 205), dark=False):
    """侧躺睡觉，只露出脑袋，盖着被子。约 46 宽 × 14 高。"""
    k = 0.7 if dark else 1.0
    f = lambda c: tuple(int(v * k) for v in c)
    R(d, x, y + 6, 14, 6, f((255, 255, 255)))              # 枕头
    R(d, x + 2, y, 13, 11, f(HAIR))
    R(d, x + 4, y + 3, 9, 7, f(SKIN))
    R(d, x + 3, y + 1, 11, 3, f(HAIR))
    R(d, x + 5, y + 4, 2, 2, f(HAIR))
    R(d, x + 5, y + 7, 2, 1, BLACK)
    R(d, x + 9, y + 7, 2, 1, BLACK)
    R(d, x + 5, y + 8, 1, 1, f(BLUSH))
    R(d, x + 11, y + 8, 1, 1, f(BLUSH))
    P(d, x + 3, y + 6, (120, 200, 240))                     # 耳塞
    R(d, x + 12, y + 1, 2, 2, f(BOW))
    R(d, x + 13, y + 6, 34, 8, f(blanket))
    R(d, x + 13, y + 6, 34, 1, f(tuple(min(255, v + 20) for v in blanket)))
    for sx in (20, 30, 40):
        P(d, x + sx, y + 9, f(STAR))


def xiaoke(d, x, y, eyes="open", legs=0, blush=False):
    """小克，16 宽 × 12 高。"""
    R(d, x + 1, y, 14, 10, CLAUDE)
    R(d, x + 1, y + 9, 14, 1, CLAUDE_D)
    R(d, x - 1, y + 4, 2, 3, CLAUDE)
    R(d, x + 15, y + 4, 2, 3, CLAUDE)
    for i, lx in enumerate((2, 6, 9, 13)):
        R(d, x + lx, y + 10, 1, 2 if (i + legs) % 2 == 0 else 1, CLAUDE)
    if eyes == "open":
        R(d, x + 4, y + 3, 2, 3, BLACK); R(d, x + 10, y + 3, 2, 3, BLACK)
        P(d, x + 4, y + 3, WHITE); P(d, x + 10, y + 3, WHITE)
    elif eyes == "closed":
        R(d, x + 3, y + 4, 3, 1, BLACK); R(d, x + 10, y + 4, 3, 1, BLACK)
    elif eyes == "happy":
        for ex in (3, 10):
            P(d, x + ex, y + 4, BLACK); P(d, x + ex + 1, y + 3, BLACK); P(d, x + ex + 2, y + 4, BLACK)
    if blush:
        R(d, x + 2, y + 6, 2, 1, BLUSH); R(d, x + 12, y + 6, 2, 1, BLUSH)


def hetao(d, x, y, sleeping=True):
    """核桃，趴着，约 24 宽 × 10 高。橘白，倒 V 脸，背上大橘斑。"""
    R(d, x + 6, y + 3, 16, 7, CAT_W)
    R(d, x + 10, y + 3, 7, 3, CAT_O)
    R(d, x + 17, y + 6, 3, 2, CAT_O)
    R(d, x + 21, y + 6, 4, 2, CAT_O)               # 尾巴
    P(d, x + 22, y + 6, CAT_W)
    R(d, x, y + 1, 9, 8, CAT_W)                    # 头
    R(d, x, y, 2, 2, CAT_O); R(d, x + 7, y, 2, 2, CAT_O)
    R(d, x, y + 1, 3, 3, CAT_O); R(d, x + 6, y + 1, 3, 3, CAT_O)
    P(d, x + 3, y + 2, CAT_O); P(d, x + 5, y + 2, CAT_O)
    P(d, x + 4, y + 6, (245, 150, 160))
    if sleeping:
        R(d, x + 1, y + 5, 2, 1, BLACK); R(d, x + 6, y + 5, 2, 1, BLACK)
    else:
        R(d, x + 2, y + 4, 1, 2, (110, 170, 90)); R(d, x + 6, y + 4, 1, 2, (110, 170, 90))
    R(d, x + 1, y + 8, 2, 2, CAT_W); R(d, x + 6, y + 8, 2, 2, CAT_W)
