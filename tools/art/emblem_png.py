#!/usr/bin/env python3
"""Pure-Python PNG + raster helpers for the SkyWynn menu emblem (no Pillow / numpy needed).

Images are lists of rows of [r, g, b, a] ints (0..255). PNG write is deterministic (zlib level 9, no metadata),
so two runs give the same bytes. The reader handles 8-bit RGB / RGBA / grey / palette PNGs (all filter types),
which is enough for vanilla icons / textures (read only, for size + density checks).
"""
import struct, zlib


def new(w, h, c=(0, 0, 0, 0)):
    return [[list(c) for _ in range(w)] for _ in range(h)]


def size(img):
    return len(img[0]), len(img)


def write_png(path, img):
    w, h = size(img)
    raw = bytearray()
    for row in img:
        raw.append(0)
        for p in row:
            raw.extend(bytes(max(0, min(255, int(round(v)))) for v in p))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) \
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)
    return data


def png_size(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR"
    return struct.unpack(">II", data[16:24])


def read_png(data):
    """bytes -> image (8-bit only)"""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, plte, trns = 8, b"", None, None
    while pos < len(data):
        n, = struct.unpack(">I", data[pos:pos + 4]); t = data[pos + 4:pos + 8]; d = data[pos + 8:pos + 8 + n]; pos += 12 + n
        if t == b"IHDR":
            w, h, bd, ct, _c, _f, il = struct.unpack(">IIBBBBB", d)
            assert bd == 8 and il == 0, "only 8-bit non-interlaced PNGs"
        elif t == b"PLTE":
            plte = d
        elif t == b"tRNS":
            trns = d
        elif t == b"IDAT":
            idat += d
    bpp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat); stride = w * bpp
    out, prev, i = [], bytearray(stride), 0
    for _y in range(h):
        f = raw[i]; line = bytearray(raw[i + 1:i + 1 + stride]); i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0; b = prev[x]; c = prev[x - bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line; row = []
        for x in range(w):
            px = line[x * bpp:(x + 1) * bpp]
            if ct == 6: row.append(list(px))
            elif ct == 2: row.append(list(px) + [255])
            elif ct == 0: row.append([px[0]] * 3 + [255])
            elif ct == 4: row.append([px[0]] * 3 + [px[1]])
            else:
                k = px[0]; row.append(list(plte[k * 3:k * 3 + 3]) + [trns[k] if trns and k < len(trns) else 255])
        out.append(row)
    return out


def blit(dst, src, ox, oy, scale=1):
    """alpha-over src onto dst at (ox, oy), nearest-neighbour integer scale"""
    sw, sh = size(src); dw, dh = size(dst)
    for y in range(sh * scale):
        ty = oy + y
        if not 0 <= ty < dh: continue
        srow = src[y // scale]; drow = dst[ty]
        for x in range(sw * scale):
            tx = ox + x
            if not 0 <= tx < dw: continue
            s = srow[x // scale]; a = s[3] / 255.0
            if a <= 0: continue
            d = drow[tx]; da = d[3] / 255.0; oa = a + da * (1 - a)
            for k in range(3):
                d[k] = (s[k] * a + d[k] * da * (1 - a)) / oa if oa > 0 else 0
            d[3] = oa * 255


def fill_rect(img, x0, y0, x1, y1, c):
    w, h = size(img)
    for y in range(max(0, y0), min(h, y1)):
        for x in range(max(0, x0), min(w, x1)):
            img[y][x] = list(c)


def downsample(img, f):
    """box filter by integer factor f, alpha-weighted colour"""
    w, h = size(img); out = new(w // f, h // f)
    for y in range(h // f):
        for x in range(w // f):
            r = g = b = a = 0.0
            for yy in range(y * f, y * f + f):
                row = img[yy]
                for xx in range(x * f, x * f + f):
                    p = row[xx]; pa = p[3]
                    r += p[0] * pa; g += p[1] * pa; b += p[2] * pa; a += pa
            if a > 0:
                out[y][x] = [r / a, g / a, b / a, a / (f * f)]
    return out


# ---------------------------------------------------------------- tiny 5x7 bitmap font (original, for sheet labels)
_F = {
 "A": "01110100011000111111100011000110001", "B": "11110100011000111110100011000111110", "C": "01110100011000010000100001000101110",
 "D": "11110100011000110001100011000111110", "E": "11111100001000011110100001000011111", "F": "11111100001000011110100001000010000",
 "G": "01110100011000010111100011000101111", "H": "10001100011000111111100011000110001", "I": "01110001000010000100001000010001110",
 "J": "00111000100001000010000101001001100", "K": "10001100101010011000101001001010001", "L": "10000100001000010000100001000011111",
 "M": "10001110111010110101100011000110001", "N": "10001110011010110011100011000110001", "O": "01110100011000110001100011000101110",
 "P": "11110100011000111110100001000010000", "Q": "01110100011000110001101011001001101", "R": "11110100011000111110101001001010001",
 "S": "01111100001000001110000010000111110", "T": "11111001000010000100001000010000100", "U": "10001100011000110001100011000101110",
 "V": "10001100011000110001100010101000100", "W": "10001100011000110101101011010101010", "X": "10001100010101000100010101000110001",
 "Y": "10001100010101000100001000010000100", "Z": "11111000010001000100010001000011111",
 "0": "01110100011001110101110011000101110", "1": "00100011000010000100001000010001110", "2": "01110100010000100010001000100011111",
 "3": "11110000010000101110000010000111110", "4": "00010001100101010010111110001000010", "5": "11111100001111000001000011000101110",
 "6": "00110010001000011110100011000101110", "7": "11111000010001000100010000100001000", "8": "01110100011000101110100011000101110",
 "9": "01110100011000101111000010001001100", " ": "0" * 35, "-": "00000000000000011111000000000000000",
 ".": "00000000000000000000000000110001100", ",": "00000000000000000000001100010001000", ":": "00000011000110000000011000110000000",
 "/": "00001000010001000100010001000010000", "(": "00010001000100001000010000010000010", ")": "01000001000001000010000100010001000",
 "+": "00000001000010011111001000010000000", "=": "00000000001111100000111110000000000",
 "%": "11001110010001000100010001001110011", "#": "01010111110101001010111110101000000", "'": "00100001000100000000000000000000000",
 "_": "00000000000000000000000000000011111", ">": "01000001000001000001000100010001000", "<": "00010001000100010000010000010000010",
}


def text(img, x, y, s, c=(230, 230, 236, 255), scale=1):
    """draw text; lower-case letters are drawn as capitals , returns the end x"""
    for ch in s:
        g = _F.get(ch) or _F.get(ch.upper()) or _F[" "]
        for i, bit in enumerate(g):
            if bit == "1":
                fill_rect(img, x + (i % 5) * scale, y + (i // 5) * scale, x + (i % 5 + 1) * scale, y + (i // 5 + 1) * scale, c)
        x += 6 * scale
    return x
