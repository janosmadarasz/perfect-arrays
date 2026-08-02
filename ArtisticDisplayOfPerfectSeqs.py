import math
import numpy as np
from PIL import ImageDraw as ImageDraw
from PIL import Image, ImageColor

from PerfectSequence import PerfectSequence

ImageWith = 1024
ImageHigh = 768
cx = ImageWith / 2
cy = ImageHigh / 2

# ---------- Perfect_seq_alpha=2_n=1-2-3-4.png (2-color) ----------
im = Image.new("RGB", (ImageWith, ImageHigh), (224, 224, 224))
draw = ImageDraw.Draw(im)

Colors = [ImageColor.getrgb("white"), ImageColor.getrgb("black")]

distFromCentral = [10, 70, 180, 310, 200, 250, 300]
deltaAngle = [0, 0, 22.5 * np.pi / 180, 0, 0]

for a in range(1, 5):
    r = distFromCentral[a - 1]
    w = PerfectSequence(2, a) 
    N = len(w)
    cr = r * math.sin(math.pi / N) if N > 0 else 10

    in_array = np.linspace(0, 2 * np.pi, N + 1)
    for i in range(len(in_array) - 1):
        ang = in_array[i] + deltaAngle[a - 1]
        ccx = cx + math.sin(ang) * r
        ccy = cy - math.cos(ang) * r
        draw.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr),
                     fill=Colors[w[i]], outline=(0, 0, 0))

im.save("results/Perfect_seq_alpha=2_n=1-2-3-4.png")


# ---------- Perfect_seq_alpha=3_n=1-2-3-4-5.png (3-color) ----------
im = Image.new("RGB", (ImageWith, ImageHigh), (224, 224, 224))
draw = ImageDraw.Draw(im)

Colors = [
    ImageColor.getrgb("red"),
    ImageColor.getrgb("green"),
    ImageColor.getrgb("blue")
]

distFromCentral = [75, 200, 300, 350, 370, 250, 300]
deltaAngle = [0, 22.5 * np.pi / 180, 0, 0, 0]

for a in range(1, 6):
    r = distFromCentral[a - 1]
    w = PerfectSequence(3, a)
    N = len(w)
    cr = r * math.sin(math.pi / N) if N > 0 else 10

    in_array = np.linspace(0, 2 * np.pi, N + 1)
    for i in range(len(in_array) - 1):
        ang = in_array[i] + deltaAngle[a - 1]
        ccx = cx + math.sin(ang) * r
        ccy = cy - math.cos(ang) * r
        draw.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr),
                     fill=Colors[w[i]], outline=(0, 0, 0))

im.save("results/Perfect_seq_alpha=3_n=1-2-3-4-5.png")
