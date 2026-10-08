"""SkyyHud mod icon generator (0.3.17). Writes SkyyHud/icon-256.png (256 x 256 RGBA).

The Hytale client reads a mod's root `icon-256.png` as its icon and wants it 256 x 256 (client log 2026-10-08: "has an icon.png with
wrong dimensions (64x64, expected 256x256)" - the 0.2.1 placeholder was a flat 64 x 64 green square).
Original art, drawn from code (no vanilla or third-party pixels): a dark rounded HUD panel, three stat bars on the left
(health red, mana blue, stamina gold) and a round minimap on the right (grass / water / path, a white arrow in the middle).
Deterministic: two runs give the same bytes (pure Python, no PIL). 4 x 4 supersampling for clean edges.
Run: python SkyyHud/make_icon.py
"""
import math
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
W = 256
SS = 4  # samples per axis per pixel


def rrect(x, y, x0, y0, x1, y1, r):
    """inside a rounded rectangle"""
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r and x0 <= x <= x1 and y0 <= y <= y1


def tri(px, py, a, b, c):
    def s(p, q, r):
        return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])
    p = (px, py)
    d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


# minimap circle
MX, MY, MR = 170.0, 128.0, 54.0
# arrow (pointing up-right a little), centred on the minimap
ANG = math.radians(-20.0)


def rot(x, y):
    c, s = math.cos(ANG), math.sin(ANG)
    return (MX + x * c - y * s, MY + x * s + y * c)


ARROW = [rot(0, -20), rot(14, 16), rot(0, 8), rot(-14, 16)]
ARROW_OUT = [rot(0, -26), rot(19, 21), rot(0, 12), rot(-19, 21)]

BARS = [  # y centre, fill fraction, colour (fill), colour (empty track)
    (82.0, 0.86, (214, 58, 58), (70, 30, 34)),
    (128.0, 0.64, (66, 132, 230), (28, 42, 72)),
    (174.0, 0.74, (236, 186, 64), (72, 58, 28)),
]
BX0, BX1, BH = 30.0, 100.0, 22.0


def terrain(x, y):
    """the minimap's ground: grass with two tones, a lake, a sandy path"""
    dx, dy = x - MX, y - MY
    lake = ((dx + 22) / 30.0) ** 2 + ((dy + 20) / 22.0) ** 2 <= 1.0
    if lake:
        return (58, 112, 186)
    shore = ((dx + 22) / 36.0) ** 2 + ((dy + 20) / 28.0) ** 2 <= 1.0
    if shore:
        return (214, 196, 138)
    path = abs(dy - 0.35 * dx - 26.0) < 6.0
    if path:
        return (176, 146, 96)
    patch = ((dx - 26) / 22.0) ** 2 + ((dy - 30) / 16.0) ** 2 <= 1.0 or ((dx + 30) / 14.0) ** 2 + ((dy - 34) / 12.0) ** 2 <= 1.0
    if patch:
        return (64, 128, 60)
    return (92, 160, 76)


def sample(x, y):
    """RGBA of one sub-sample (straight alpha)"""
    if not rrect(x, y, 8, 8, 248, 248, 40):
        return (0, 0, 0, 0)
    # panel: outer gold-ish frame, inner dark slate with a soft vertical gradient
    if not rrect(x, y, 16, 16, 240, 240, 33):
        return (176, 150, 104, 255)
    if not rrect(x, y, 20, 20, 236, 236, 29):
        return (40, 46, 62, 255)
    g = (y - 20) / 216.0
    base = (int(34 + 14 * (1 - g)), int(42 + 16 * (1 - g)), int(60 + 20 * (1 - g)), 255)
    # minimap ring + ground + arrow
    d = math.hypot(x - MX, y - MY)
    if d <= MR + 6:
        if d > MR:
            return (176, 150, 104, 255)
        if d > MR - 3:
            return (28, 32, 44, 255)
        if tri(x, y, ARROW[0], ARROW[1], ARROW[2]) or tri(x, y, ARROW[0], ARROW[2], ARROW[3]):
            return (250, 250, 246, 255)
        if tri(x, y, ARROW_OUT[0], ARROW_OUT[1], ARROW_OUT[2]) or tri(x, y, ARROW_OUT[0], ARROW_OUT[2], ARROW_OUT[3]):
            return (24, 28, 36, 255)
        t = terrain(x, y)
        return (t[0], t[1], t[2], 255)
    # stat bars (rounded), a dark outline, fill + a highlight stripe
    for cy, frac, fill, track in BARS:
        y0, y1 = cy - BH / 2, cy + BH / 2
        if rrect(x, y, BX0 - 3, y0 - 3, BX1 + 3, y1 + 3, BH / 2 + 3):
            if not rrect(x, y, BX0, y0, BX1, y1, BH / 2):
                return (20, 24, 32, 255)
            if x <= BX0 + (BX1 - BX0) * frac:
                if y < y0 + 6:
                    return (min(255, fill[0] + 40), min(255, fill[1] + 40), min(255, fill[2] + 40), 255)
                return (fill[0], fill[1], fill[2], 255)
            return (track[0], track[1], track[2], 255)
    return base


def render():
    rows = []
    n = SS * SS
    for py in range(W):
        row = bytearray([0])  # filter: none
        for px in range(W):
            r = g = b = a = 0
            for sy in range(SS):
                for sx in range(SS):
                    c = sample(px + (sx + 0.5) / SS, py + (sy + 0.5) / SS)
                    r += c[0] * c[3]
                    g += c[1] * c[3]
                    b += c[2] * c[3]
                    a += c[3]
            if a == 0:
                row += b"\x00\x00\x00\x00"
            else:
                row += bytes((int(round(r / a)), int(round(g / a)), int(round(b / a)), int(round(a / n))))
        rows.append(bytes(row))
    return b"".join(rows)


def png(w, h, raw):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def check_icon(data, size=W):
    """None when `data` is a valid PNG of size x size (the client's mod-icon rule), else the reason. Used by the build script
    (0.3.17+) so a wrong icon never ships again: signature, every chunk CRC, IHDR, IDAT inflates to the exact row bytes, IEND."""
    if not isinstance(data, (bytes, bytearray)) or data[:8] != b"\x89PNG\r\n\x1a\n":
        return "not a PNG (bad signature)"
    p, ihdr, idat, end = 8, None, b"", False
    while p + 12 <= len(data):
        ln = struct.unpack(">I", data[p:p + 4])[0]
        t = data[p + 4:p + 8]
        body = data[p + 8:p + 8 + ln]
        if len(body) != ln or p + 12 + ln > len(data):
            return "truncated %s chunk" % t
        if struct.unpack(">I", data[p + 8 + ln:p + 12 + ln])[0] != zlib.crc32(t + body) & 0xFFFFFFFF:
            return "bad CRC in %s chunk" % t
        if t == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif t == b"IDAT":
            idat += body
        elif t == b"IEND":
            end = True
            break
        p += 12 + ln
    if ihdr is None or not end:
        return "missing IHDR or IEND"
    w, h, depth, ctype, _c, _f, inter = ihdr
    if (w, h) != (size, size):
        return "wrong dimensions (%dx%d, expected %dx%d)" % (w, h, size, size)
    chans = {6: 4, 2: 3, 0: 1, 4: 2}.get(ctype)
    if chans is None or depth != 8 or inter != 0:
        return "unsupported format (colour type %d, depth %d, interlace %d)" % (ctype, depth, inter)
    try:
        raw = zlib.decompress(idat)
    except zlib.error as e:
        return "IDAT does not inflate: %s" % e
    if len(raw) != h * (w * chans + 1):
        return "IDAT holds %d bytes, expected %d" % (len(raw), h * (w * chans + 1))
    return None


if __name__ == "__main__":
    out = os.path.join(HERE, "icon-256.png")
    data = png(W, W, render())
    assert check_icon(data) is None, check_icon(data)
    open(out, "wb").write(data)
    print("wrote", out, len(data), "bytes, %dx%d" % (W, W))
