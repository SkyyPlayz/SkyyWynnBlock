"""skyyart - the shared SkyWynn ART kit: recolour vanilla item textures at BUILD TIME and render their inventory icons.

Why it exists: the repo is public, so vanilla pixels are never committed. A build script reads the vanilla texture / model / icon
out of Assets.zip (read-only), calls this kit, and writes the resulting PNG bytes straight into the mod jar. Pure Python (zlib +
struct only - no Pillow, the build machines run plain python), pure functions (bytes in, PNG bytes out), deterministic (no clocks,
no randomness, fixed zlib level, no text / time chunks: the same input gives the same pixels; the same zlib gives the same bytes).

    import skyyart as SA                    # tools/ is on sys.path in every build script
    SA.verify()                             # proves the PNG codec + the icon renderer against vanilla icons (fails the build loudly)
    z = SA.assets()                         # zipfile.ZipFile(Assets.zip), read-only
    tex, icon = SA.wand_art(z, "Cobalt", "A")          # the SkyWynn metal Priest wands (recipe at the end of this file)

    # the generic pieces the recipe is made of:
    grad = SA.palette_from([(png, rects), ...])        # luminance-sorted gradient (dark -> light) from pixels of vanilla art
    out  = SA.recolor(png, grad, rects, lo=, hi=)      # gradient map (rank / luminance mix), alpha kept, only inside rects
    out  = SA.shade(png, rects, mul=0.85)              # darken (e.g. keep a wood handle but a bit darker)
    rects = SA.node_rects(model, ["Stick"])            # the UV rectangles of named blockymodel nodes (which texels a part uses)
    icon = SA.render_icon(model, tex, props)           # re-render the 64x64 inventory icon like the game's icon generator
    icon = SA.recolor_icon(icon_png, grad, weights)    # fallback: recolour an existing icon (weights = SA.icon_weights(...))

Icon renderer (render_icon): reproduces the vanilla generated icons (Icons/ItemsGenerated/*.png) from Model + Texture +
IconProperties: orthographic, R = Ry * Rx * Rz of Rotation [x, y, z] (degrees), 2 px per model unit x Scale, Translation in
units on screen, model origin at (32.5, 32.5),
2x2 supersampling, unlit, alpha-tested texels, colours stored PREMULTIPLIED with the game's alpha curve 0/49/127/206/255.
Measured 2026-10-02: Weapon_Wand_Wood, Weapon_Wand_Wood_Rotten and Weapon_Staff_Iron (IconProperties Rotation [45, 90, 0]) come out
within ~2/255 mean colour error of the vanilla icons. NOT proven for other rotations: the Ingot's [22.5, 45, 22.5] view (the
default for blocks / materials) lands ~1.5 px off in Y - run check_icon() on a vanilla item with the same model / props before
trusting render_icon for a new item family (verify() only proves the wand / staff family).

Blockymodel rules the kit uses (proven by the renders above): a node sits at parent shape offset + position (in the parent frame),
rotated by its orientation quaternion; a box / quad is offset + stretch * corner in the node frame. UV per face: box face sizes are
front/back = x*y, left/right = z*y, top/bottom = x*z (quad: x*y, front only); the texel of face point (u, v) is
offset + R(angle) * M * (u, v) with M = the mirror flags (negate u / v) and R a clockwise turn (90: (u, v) -> (-v, u)).
"""
import os, json, math, struct, zlib, zipfile

KIT_VERSION = "1.0"   # 1.0 (2026-10-02, the metal wand art proof)

_HYTALE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale")
GAME_DIR = os.path.join(_HYTALE, "install", "release", "package", "game", "latest")
ASSETS_ZIP = os.path.join(GAME_DIR, "Assets.zip")


class ArtCheckError(SystemExit):
    """verify() failed (Assets.zip missing, a vanilla source moved, or the icon renderer no longer matches vanilla): stop the build."""


def assets(path=None):
    """Assets.zip opened READ-ONLY (zipfile never writes in mode 'r')."""
    p = path or ASSETS_ZIP
    if not os.path.isfile(p):
        raise ArtCheckError("skyyart: Assets.zip not found at %s" % p)
    return zipfile.ZipFile(p, "r")


def _read(z, name):
    """Assets.zip entry bytes; 'Common/' is added for model / texture / icon paths written the item-JSON way."""
    for n in (name, "Common/" + name):
        try:
            return z.read(n)
        except KeyError:
            pass
    raise ArtCheckError("skyyart: %s is not in Assets.zip" % name)


# ================================================================= images + PNG codec (RGBA8 in memory)
class Img(object):
    """w x h RGBA8 pixels in a bytearray (row-major, 4 bytes a pixel)."""
    __slots__ = ("w", "h", "px")

    def __init__(self, w, h, px=None):
        self.w, self.h = int(w), int(h)
        self.px = bytearray(px) if px is not None else bytearray(self.w * self.h * 4)

    def get(self, x, y):
        i = (y * self.w + x) * 4
        return tuple(self.px[i:i + 4])

    def put(self, x, y, c):
        i = (y * self.w + x) * 4
        self.px[i:i + 4] = bytes((_c8(c[0]), _c8(c[1]), _c8(c[2]), _c8(c[3])))

    def copy(self):
        return Img(self.w, self.h, self.px)


def _c8(v):
    v = int(round(v))
    return 0 if v < 0 else (255 if v > 255 else v)


def _img(src):
    """PNG bytes or Img -> a private Img copy."""
    if isinstance(src, Img):
        return src.copy()
    return png_decode(src)


_SIG = b"\x89PNG\r\n\x1a\n"
_ADAM7 = ((0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2))


def png_decode(data):
    """Any standard PNG (grey / RGB / palette / grey+alpha / RGBA, 1-16 bit, tRNS, Adam7) -> Img (RGBA8)."""
    data = bytes(data)
    if data[:8] != _SIG:
        raise ValueError("not a PNG")
    pos, idat, plte, trns, hdr = 8, [], None, None, None
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE":
            plte = body
        elif typ == b"tRNS":
            trns = body
        elif typ == b"IDAT":
            idat.append(body)
        elif typ == b"IEND":
            break
    if hdr is None:
        raise ValueError("PNG without IHDR")
    w, h, bd, ct, _comp, _filt, inter = hdr
    nch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    bits = nch * bd
    bpp = max(1, bits // 8)
    raw = zlib.decompress(b"".join(idat))
    img = Img(w, h)
    maxv = (1 << bd) - 1
    pal = [tuple(plte[i:i + 3]) for i in range(0, len(plte or b""), 3)]
    palA = list(trns) if (ct == 3 and trns) else []
    key = None
    if trns and ct == 0:
        key = struct.unpack(">H", trns[:2])[0]
    elif trns and ct == 2:
        key = struct.unpack(">HHH", trns[:6])

    def values(line, pw):
        if bd == 8:
            return list(line[:pw * nch])
        if bd == 16:
            return [(line[i] << 8) | line[i + 1] for i in range(0, pw * nch * 2, 2)]
        out, per = [], 8 // bd
        for i in range(pw * nch):
            b = line[i // per]
            out.append((b >> (8 - bd * (i % per + 1))) & maxv)
        return out

    def scale(v):
        if bd == 8:
            return v
        if bd == 16:
            return v >> 8
        return v * 255 // maxv

    off = 0
    passes = _ADAM7 if inter == 1 else ((0, 0, 1, 1),)
    for x0, y0, dx, dy in passes:
        pw = (w - x0 + dx - 1) // dx
        ph = (h - y0 + dy - 1) // dy
        if pw <= 0 or ph <= 0:
            continue
        stride = (pw * bits + 7) // 8
        prev = bytearray(stride)
        for yy in range(ph):
            ft = raw[off]
            line = bytearray(raw[off + 1:off + 1 + stride])
            off += 1 + stride
            if ft == 1:
                for i in range(bpp, stride):
                    line[i] = (line[i] + line[i - bpp]) & 255
            elif ft == 2:
                for i in range(stride):
                    line[i] = (line[i] + prev[i]) & 255
            elif ft == 3:
                for i in range(stride):
                    left = line[i - bpp] if i >= bpp else 0
                    line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
            elif ft == 4:
                for i in range(stride):
                    a = line[i - bpp] if i >= bpp else 0
                    b = prev[i]
                    c = prev[i - bpp] if i >= bpp else 0
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    line[i] = (line[i] + (a if (pa <= pb and pa <= pc) else (b if pb <= pc else c))) & 255
            prev = line
            vals = values(line, pw)
            y = y0 + yy * dy
            for xx in range(pw):
                v = vals[xx * nch:(xx + 1) * nch]
                if ct == 0:
                    g = scale(v[0])
                    c = (g, g, g, 0 if (key is not None and v[0] == key) else 255)
                elif ct == 2:
                    c = (scale(v[0]), scale(v[1]), scale(v[2]), 0 if (key is not None and tuple(v) == key) else 255)
                elif ct == 3:
                    r, g, b = pal[v[0]]
                    c = (r, g, b, palA[v[0]] if v[0] < len(palA) else 255)
                elif ct == 4:
                    g = scale(v[0])
                    c = (g, g, g, scale(v[1]))
                else:
                    c = (scale(v[0]), scale(v[1]), scale(v[2]), scale(v[3]))
                img.put(x0 + xx * dx, y, c)
    return img


def png_encode(img):
    """Img -> PNG bytes (RGBA8, no interlace, per-row filter = least sum of |byte| (deterministic), zlib level 9, no extra chunks)."""
    w, h, px = img.w, img.h, img.px
    stride = w * 4
    out = bytearray()
    prev = bytearray(stride)
    for y in range(h):
        line = px[y * stride:(y + 1) * stride]
        best = None
        for ft in range(5):
            f = bytearray(stride)
            for i in range(stride):
                a = line[i - 4] if i >= 4 else 0
                b = prev[i]
                if ft == 0:
                    f[i] = line[i]
                elif ft == 1:
                    f[i] = (line[i] - a) & 255
                elif ft == 2:
                    f[i] = (line[i] - b) & 255
                elif ft == 3:
                    f[i] = (line[i] - ((a + b) >> 1)) & 255
                else:
                    c = prev[i - 4] if i >= 4 else 0
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    f[i] = (line[i] - (a if (pa <= pb and pa <= pc) else (b if pb <= pc else c))) & 255
            score = sum(v if v < 128 else 256 - v for v in f)
            if best is None or score < best[0]:
                best = (score, ft, f)
        out.append(best[1])
        out += best[2]
        prev = line

    def chunk(typ, body):
        return struct.pack(">I", len(body)) + typ + body + struct.pack(">I", zlib.crc32(typ + body) & 0xffffffff)
    return (_SIG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(out), 9)) + chunk(b"IEND", b""))


def png_size(data):
    """(w, h) of a PNG without decoding it."""
    if bytes(data[:8]) != _SIG or bytes(data[12:16]) != b"IHDR":
        raise ValueError("not a PNG")
    return struct.unpack(">II", bytes(data[16:24]))


# ================================================================= colour, regions, gradients
def luma(c):
    """Rec. 709 luminance of an sRGB colour (0..255 scale)."""
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _region_points(img, regions, min_alpha=1):
    """Ordered unique (x, y, rect_index) of the pixels inside regions (None = the whole image) with alpha >= min_alpha.
    regions: list of (x0, y0, x1, y1) rects, x1 / y1 exclusive."""
    rects = [(0, 0, img.w, img.h)] if regions is None else list(regions)
    seen, pts = set(), []
    for ri, r in enumerate(rects):
        x0, y0, x1, y1 = (int(v) for v in r)
        for y in range(max(y0, 0), min(y1, img.h)):
            for x in range(max(x0, 0), min(x1, img.w)):
                if (x, y) in seen:
                    continue
                seen.add((x, y))
                if img.px[(y * img.w + x) * 4 + 3] >= min_alpha:
                    pts.append((x, y, ri))
    return pts


def palette_from(sources, steps=24, min_alpha=128):
    """A gradient (tuple of `steps` (r, g, b) floats, dark -> light) from vanilla art: all pixels (alpha >= min_alpha) of the
    sources, sorted by luminance, cut into `steps` equal-count bins, each bin averaged. Index t of the gradient = the t-th
    percentile colour of the source art. sources: a list of PNG bytes / Img, or (png_or_img, rects) pairs (rects = UV rectangles,
    e.g. node_rects() of the vanilla model, so only the metal part of a vanilla tool is sampled)."""
    pix = []
    for s in sources:
        src, rects = (s if isinstance(s, tuple) else (s, None))
        im = _img(src)
        for x, y, _ri in _region_points(im, rects, min_alpha):
            pix.append(im.get(x, y)[:3])
    if not pix:
        raise ValueError("palette_from: no opaque pixels in the sources")
    pix.sort(key=lambda c: (luma(c), c))
    n, grad = len(pix), []
    for i in range(steps):
        a = (i * n) // steps
        b = max(a + 1, ((i + 1) * n) // steps)
        chunk = pix[a:b] if a < n else pix[-1:]
        grad.append(tuple(sum(c[k] for c in chunk) / float(len(chunk)) for k in range(3)))
    return tuple(grad)


def sample(grad, t):
    """Colour at t (0..1) of a gradient, linear between its steps."""
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    f = t * (len(grad) - 1)
    i = int(f)
    if i >= len(grad) - 1:
        return grad[-1]
    k = f - i
    a, b = grad[i], grad[i + 1]
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k)


def grad_span(grad, lo, hi, steps=None):
    """The part lo..hi of a gradient, re-sampled to `steps` steps (default: the same count)."""
    n = steps or len(grad)
    return tuple(sample(grad, lo + (hi - lo) * i / float(n - 1)) for i in range(n))


def grad_mix(a, b, t, steps=None):
    """Blend of two gradients (t = 0 -> a, 1 -> b)."""
    n = steps or max(len(a), len(b))
    out = []
    for i in range(n):
        u = i / float(n - 1)
        ca, cb = sample(a, u), sample(b, u)
        out.append(tuple(ca[k] + (cb[k] - ca[k]) * t for k in range(3)))
    return tuple(out)


def grad_hex(grad):
    """'#rrggbb' list of a gradient (for logs / docs)."""
    return ["#%02x%02x%02x" % tuple(_c8(v) for v in c) for c in grad]


def recolor(png, grad, regions=None, lo=0.0, hi=1.0, rank=0.5, smooth=0.0, lift=None, min_alpha=1, as_img=False):
    """Gradient-map the pixels inside `regions` (None = all) onto `grad`; alpha and every pixel outside are kept.
    Each pixel's position t in the gradient = lo + (hi - lo) * (rank * its luminance RANK among the region's pixels (ties
    averaged) + (1 - rank) * its luminance stretched between the region's 2nd and 98th percentile). rank=1 makes the region take
    the source art's exact tonal spread (strongest material change), rank=0 keeps the texture's own contrast.
    smooth (0..1) blends each luminance with its 3x3 neighbours inside the same rect first (calms wood grain into metal).
    lift: optional {(x, y): dt} added to t after that (rim_lift() = bright bevelled face edges).
    Without smooth / lift the pixel order (dark -> light) is kept exactly, so the shading / detail of the vanilla texture survives."""
    img = _img(png)
    pts = _region_points(img, regions, min_alpha)
    if not pts:
        return img if as_img else png_encode(img)
    L = {}
    for x, y, _ri in pts:
        L[(x, y)] = luma(img.get(x, y))
    if smooth > 0:
        rect_of = dict(((x, y), ri) for x, y, ri in pts)
        L2 = {}
        for x, y, ri in pts:
            acc, n = 0.0, 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if rect_of.get(q) == ri:
                        acc += L[q]
                        n += 1
            L2[(x, y)] = (1 - smooth) * L[(x, y)] + smooth * acc / n
        L = L2
    order = sorted(L, key=lambda p: (L[p], p[1], p[0]))
    n = len(order)
    pr = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and L[order[j + 1]] == L[order[i]]:
            j += 1
        r = ((i + j) / 2.0) / (n - 1) if n > 1 else 0.5
        for k in range(i, j + 1):
            pr[order[k]] = r
        i = j + 1
    l_lo = L[order[int(0.02 * (n - 1))]]
    l_hi = L[order[int(round(0.98 * (n - 1)))]]
    span = (l_hi - l_lo) or 1.0
    for p in order:
        lin = (L[p] - l_lo) / span
        lin = 0.0 if lin < 0 else (1.0 if lin > 1 else lin)
        t = lo + (hi - lo) * (rank * pr[p] + (1 - rank) * lin)
        if lift:
            t += lift.get(p, 0.0)
        c = sample(grad, t)
        img.put(p[0], p[1], (c[0], c[1], c[2], img.px[(p[1] * img.w + p[0]) * 4 + 3]))
    return img if as_img else png_encode(img)


def rim_lift(rects, edge=0.12, inner=0.0):
    """{(x, y): dt} for recolor(lift=): the border texels of every rect (= the edges of each model face, whatever its UV
    rotation) get +edge, the ring just inside gets +inner (negative = a dark groove under the bright edge). A rect that lies
    inside another one (a narrow face reusing part of a wider face's texels) adds no rim: its edges are inside the wider face."""
    rs = [tuple(int(v) for v in r) for r in rects]
    out = {}
    for r in rs:
        if any(s != r and s[0] <= r[0] and s[1] <= r[1] and s[2] >= r[2] and s[3] >= r[3] for s in rs):
            continue
        x0, y0, x1, y1 = r
        for y in range(y0, y1):
            for x in range(x0, x1):
                d = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
                v = edge if d == 0 else (inner if d == 1 else 0.0)
                if v and abs(v) > abs(out.get((x, y), 0.0)):
                    out[(x, y)] = v
    return out


def shade(png, regions=None, mul=0.85, sat=1.0, as_img=False):
    """Darken (mul < 1) / brighten the pixels inside regions; sat scales the saturation (1 = keep). Alpha kept."""
    img = _img(png)
    for x, y, _ri in _region_points(img, regions):
        r, g, b, a = img.get(x, y)
        m = luma((r, g, b))
        c = [m + (v - m) * sat for v in (r, g, b)]
        img.put(x, y, (c[0] * mul, c[1] * mul, c[2] * mul, a))
    return img if as_img else png_encode(img)


# ================================================================= blockymodels (Hytale .blockymodel JSON)
def _qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def _qrot(q, v):
    x, y, z, w = q
    xx, yy, zz, xy, xz, yz, wx, wy, wz = x * x, y * y, z * z, x * y, x * z, y * z, w * x, w * y, w * z
    return (v[0] * (1 - 2 * (yy + zz)) + v[1] * 2 * (xy - wz) + v[2] * 2 * (xz + wy),
            v[0] * 2 * (xy + wz) + v[1] * (1 - 2 * (xx + zz)) + v[2] * 2 * (yz - wx),
            v[0] * 2 * (xz - wy) + v[1] * 2 * (yz + wx) + v[2] * (1 - 2 * (xx + yy)))


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _model(model):
    if isinstance(model, dict):
        return model
    if isinstance(model, (bytes, bytearray)):
        model = model.decode("utf-8-sig")
    return json.loads(model)


def _xyz(d, default=0.0):
    d = d or {}
    return (float(d.get("x", default)), float(d.get("y", default)), float(d.get("z", default)))


def model_faces(model):
    """Every textured face of a blockymodel: dicts with node, face, corners (4 model-space points TL, TR, BR, BL as seen from
    outside), wh (face size in texels), layout (the JSON textureLayout entry), normal (model space), double (doubleSided), quad."""
    m = _model(model)
    faces = []

    def walk(node, pos, rot, poff):
        lp = _add(_xyz(node.get("position")), poff)
        o = node.get("orientation") or {}
        lq = (float(o.get("x", 0)), float(o.get("y", 0)), float(o.get("z", 0)), float(o.get("w", 1)))
        wpos = _add(pos, _qrot(rot, lp))
        wrot = _qmul(rot, lq)
        sh = node.get("shape") or {}
        t = sh.get("type")
        off = _xyz(sh.get("offset"))
        st = _xyz(sh.get("stretch"), 1.0)
        if t in ("box", "quad") and sh.get("visible", True):
            sz = (sh.get("settings") or {}).get("size") or {}
            sx, sy, sz_ = float(sz.get("x", 0)), float(sz.get("y", 0)), float(sz.get("z", 0))
            hx, hy, hz = sx / 2.0, sy / 2.0, sz_ / 2.0
            if t == "box":
                spec = (("front", ((-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)), (sx, sy), (0, 0, 1)),
                        ("back", ((hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, -hz), (hx, -hy, -hz)), (sx, sy), (0, 0, -1)),
                        ("left", ((-hx, hy, -hz), (-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz)), (sz_, sy), (-1, 0, 0)),
                        ("right", ((hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)), (sz_, sy), (1, 0, 0)),
                        ("top", ((-hx, hy, -hz), (hx, hy, -hz), (hx, hy, hz), (-hx, hy, hz)), (sx, sz_), (0, 1, 0)),
                        ("bottom", ((-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)), (sx, sz_), (0, -1, 0)))
            else:
                spec = (("front", ((-hx, hy, 0), (hx, hy, 0), (hx, -hy, 0), (-hx, -hy, 0)), (sx, sy), (0, 0, 1)),)
            layouts = sh.get("textureLayout") or {}
            for fname, cs, wh, nrm in spec:
                lay = layouts.get(fname)
                if lay is None:
                    continue
                corners = [_add(wpos, _qrot(wrot, _add((c[0] * st[0], c[1] * st[1], c[2] * st[2]), off))) for c in cs]
                sgn = (1 if st[0] >= 0 else -1, 1 if st[1] >= 0 else -1, 1 if st[2] >= 0 else -1)
                normal = _qrot(wrot, (nrm[0] * sgn[0], nrm[1] * sgn[1], nrm[2] * sgn[2]))
                faces.append({"node": node.get("name", ""), "face": fname, "corners": corners, "wh": wh, "layout": lay,
                              "normal": normal, "double": bool(sh.get("doubleSided", False)), "quad": t == "quad"})
        for ch in node.get("children") or []:
            walk(ch, wpos, wrot, off)

    for nd in m.get("nodes") or []:
        walk(nd, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (0.0, 0.0, 0.0))
    return faces


def uv_point(layout, u, v):
    """Texture coordinate of face point (u, v) (texels from the face's top-left corner)."""
    mir = layout.get("mirror") or {}
    a = (-u if mir.get("x") else u, -v if mir.get("y") else v)
    ang = int(layout.get("angle", 0)) % 360
    if ang == 90:
        a = (-a[1], a[0])
    elif ang == 180:
        a = (-a[0], -a[1])
    elif ang == 270:
        a = (a[1], -a[0])
    o = layout.get("offset") or {}
    return (float(o.get("x", 0)) + a[0], float(o.get("y", 0)) + a[1])


def face_rect(face):
    """The texel rectangle (x0, y0, x1, y1) a face samples (x1 / y1 exclusive)."""
    w, h = face["wh"]
    pts = [uv_point(face["layout"], u, v) for u, v in ((0, 0), (w, 0), (w, h), (0, h))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (int(round(min(xs))), int(round(min(ys))), int(round(max(xs))), int(round(max(ys))))


def node_names(model):
    """Names of the nodes that carry a textured box / quad, in model order (no duplicates)."""
    out = []
    for f in model_faces(model):
        if f["node"] not in out:
            out.append(f["node"])
    return out


def _name_match(names):
    if callable(names):
        return names
    if isinstance(names, str):
        names = [names]
    exact = set(n for n in names if not n.endswith("*"))
    pref = tuple(n[:-1] for n in names if n.endswith("*"))
    return lambda n: n in exact or (bool(pref) and n.startswith(pref))


def node_rects(model, names):
    """UV rectangles of the faces of the named nodes (exact names, 'Prefix*', or a callable(name) -> bool), no duplicates."""
    ok = _name_match(names)
    out = []
    for f in model_faces(model):
        if ok(f["node"]):
            r = face_rect(f)
            if r not in out:
                out.append(r)
    return out


def rects_overlap(a, b):
    """True when any rect of list a overlaps any rect of list b (parts that share texels cannot be recoloured apart)."""
    for r in a:
        for s in b:
            if r[0] < s[2] and s[0] < r[2] and r[1] < s[3] and s[1] < r[3]:
                return True
    return False


# ================================================================= icon renderer
_ALPHA_CURVE = ((0.0, 0.0), (0.25, 49 / 255.0), (0.5, 127 / 255.0), (0.75, 206 / 255.0), (1.0, 1.0))   # vanilla 2x2 AA alpha


def _alpha_of(cov):
    for (c0, a0), (c1, a1) in zip(_ALPHA_CURVE, _ALPHA_CURVE[1:]):
        if cov <= c1:
            return a0 + (a1 - a0) * (cov - c0) / (c1 - c0)
    return 1.0


def _euler_yxz(rx, ry, rz):
    def ax(i, deg):
        s, c = math.sin(math.radians(deg) / 2.0), math.cos(math.radians(deg) / 2.0)
        return ((s, 0.0, 0.0, c), (0.0, s, 0.0, c), (0.0, 0.0, s, c))[i]
    return _qmul(_qmul(ax(1, ry), ax(0, rx)), ax(2, rz))


def _props(props):
    p = props or {}
    rot = p.get("Rotation") or [0, 0, 0]
    tr = p.get("Translation") or [0, 0]
    return (float(rot[0]), float(rot[1]), float(rot[2])), float(p.get("Scale", 1.0)), (float(tr[0]), float(tr[1]))


def _raster(faces, tex, props, size, ss):
    """Sample grid size*ss square: per sample (face index, texel colour) of the nearest alpha-tested texel."""
    (rx, ry, rz), scale, (tx, ty) = _props(props)
    q = _euler_yxz(rx, ry, rz)
    k = size / 64.0
    s = 2.0 * scale * k
    cx = size / 2.0 + tx * s + 0.5 * k
    cy = size / 2.0 - ty * s + 0.5 * k
    N = size * ss
    zbuf = [None] * (N * N)
    hit = [None] * (N * N)
    tw, th = (tex.w, tex.h) if tex is not None else (1, 1)
    for fi, f in enumerate(faces):
        nv = _qrot(q, f["normal"])
        if f["quad"] and not f["double"] and nv[2] < 0:
            continue
        P = []
        for c in f["corners"]:
            v = _qrot(q, c)
            P.append(((v[0] * s + cx) * ss, (-v[1] * s + cy) * ss, v[2]))
        w, h = f["wh"]
        UV = ((0.0, 0.0), (w, 0.0), (w, h), (0.0, h))
        for tri in ((0, 1, 2), (0, 2, 3)):
            a, b, c = P[tri[0]], P[tri[1]], P[tri[2]]
            ua, ub, uc = UV[tri[0]], UV[tri[1]], UV[tri[2]]
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-12:
                continue
            x0 = max(int(math.floor(min(a[0], b[0], c[0]))), 0)
            x1 = min(int(math.ceil(max(a[0], b[0], c[0]))), N - 1)
            y0 = max(int(math.floor(min(a[1], b[1], c[1]))), 0)
            y1 = min(int(math.ceil(max(a[1], b[1], c[1]))), N - 1)
            for py in range(y0, y1 + 1):
                Y = py + 0.5
                for px in range(x0, x1 + 1):
                    X = px + 0.5
                    l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
                    if l1 < -1e-9:
                        continue
                    l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den
                    if l2 < -1e-9:
                        continue
                    l3 = 1.0 - l1 - l2
                    if l3 < -1e-9:
                        continue
                    zz = l1 * a[2] + l2 * b[2] + l3 * c[2]
                    i = py * N + px
                    if zbuf[i] is not None and zbuf[i] >= zz:
                        continue
                    col = (255, 255, 255, 255)
                    if tex is not None:
                        u = l1 * ua[0] + l2 * ub[0] + l3 * uc[0]
                        v = l1 * ua[1] + l2 * ub[1] + l3 * uc[1]
                        tu, tv = uv_point(f["layout"], u, v)
                        ix = min(max(int(math.floor(tu)), 0), tw - 1)
                        iy = min(max(int(math.floor(tv)), 0), th - 1)
                        col = tex.get(ix, iy)
                        if col[3] < 128:
                            continue
                    zbuf[i] = zz
                    hit[i] = (fi, col)
    return hit, N


def render_icon(model, texture, props, size=64, ss=2, as_img=False):
    """The inventory icon the game would generate for Model + Texture + IconProperties (see the module notes: proven for the
    Rotation [45, 90, 0] wand / staff family). size=64 is the real icon; a bigger size (128, 256) gives a crisp 3D preview of
    the same view. Colours are premultiplied like the vanilla icons."""
    faces = model_faces(model)
    tex = _img(texture)
    hit, N = _raster(faces, tex, props, size, ss)
    out = Img(size, size)
    n = float(ss * ss)
    for y in range(size):
        for x in range(size):
            acc, k = [0.0, 0.0, 0.0], 0
            for sy in range(ss):
                row = (y * ss + sy) * N + x * ss
                for sx in range(ss):
                    hv = hit[row + sx]
                    if hv is not None:
                        c = hv[1]
                        acc[0] += c[0]
                        acc[1] += c[1]
                        acc[2] += c[2]
                        k += 1
            if k:
                a = _alpha_of(k / n)
                out.put(x, y, (acc[0] / k * a, acc[1] / k * a, acc[2] / k * a, a * 255))
    return out if as_img else png_encode(out)


def icon_weights(model, props, names, texture=None, size=64, ss=2):
    """{(x, y): share 0..1 of the pixel's covered samples that show the named nodes} for the icon view (for recolor_icon).
    Pass the vanilla texture so its see-through texels (leaf cut-outs) are skipped like in the real icon."""
    faces = model_faces(model)
    ok = _name_match(names)
    hit, N = _raster(faces, _img(texture) if texture is not None else None, props, size, ss)
    out = {}
    for y in range(size):
        for x in range(size):
            k = m = 0
            for sy in range(ss):
                for sx in range(ss):
                    hv = hit[(y * ss + sy) * N + x * ss + sx]
                    if hv is not None:
                        k += 1
                        m += 1 if ok(faces[hv[0]]["node"]) else 0
            if k and m:
                out[(x, y)] = m / float(k)
    return out


def recolor_icon(icon, grad, weights=None, lo=0.0, hi=1.0, rank=0.5, as_img=False):
    """Recolour an EXISTING (premultiplied) icon: un-premultiply, gradient-map like recolor() over the weighted pixels (all
    opaque ones when weights is None), blend by weight, premultiply again. Use when render_icon is not proven for a model; it
    cannot show texture edits the icon never had (a darker handle, new details) - render_icon can."""
    img = _img(icon)
    pts = []
    for y in range(img.h):
        for x in range(img.w):
            a = img.px[(y * img.w + x) * 4 + 3]
            wgt = 1.0 if weights is None else weights.get((x, y), 0.0)
            if a and wgt > 0:
                r, g, b, _ = img.get(x, y)
                f = 255.0 / a
                pts.append((x, y, wgt, (r * f, g * f, b * f), a))
    if not pts:
        return img if as_img else png_encode(img)
    order = sorted(range(len(pts)), key=lambda i: (luma(pts[i][3]), pts[i][1], pts[i][0]))
    n = len(order)
    pr = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and luma(pts[order[j + 1]][3]) == luma(pts[order[i]][3]):
            j += 1
        for k in range(i, j + 1):
            pr[order[k]] = ((i + j) / 2.0) / (n - 1) if n > 1 else 0.5
        i = j + 1
    ls = [luma(pts[order[k]][3]) for k in range(n)]
    l_lo, l_hi = ls[int(0.02 * (n - 1))], ls[int(round(0.98 * (n - 1)))]
    span = (l_hi - l_lo) or 1.0
    for idx, (x, y, wgt, c, a) in enumerate(pts):
        lin = min(max((luma(c) - l_lo) / span, 0.0), 1.0)
        nc = sample(grad, lo + (hi - lo) * (rank * pr[idx] + (1 - rank) * lin))
        mix = [c[k] + (nc[k] - c[k]) * wgt for k in range(3)]
        f = a / 255.0
        img.put(x, y, (mix[0] * f, mix[1] * f, mix[2] * f, a))
    return img if as_img else png_encode(img)


def check_icon(model, texture, props, icon):
    """(mean |colour| error over pixels opaque in both, mean |alpha| error over all pixels) of render_icon against a vanilla
    icon, both 0..255. The vanilla wand / staff icons give about (2, 0.2)."""
    mine = render_icon(model, texture, props, as_img=True)
    van = _img(icon)
    if (van.w, van.h) != (64, 64):
        raise ValueError("check_icon: the vanilla icon is %dx%d, not 64x64" % (van.w, van.h))
    e_c = e_a = 0.0
    n = 0
    for y in range(64):
        for x in range(64):
            a, b = van.get(x, y), mine.get(x, y)
            e_a += abs(a[3] - b[3])
            if a[3] == 255 and b[3] == 255:
                e_c += (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3.0
                n += 1
    return (e_c / max(n, 1), e_a / 4096.0)


def item_parts(z, item_json):
    """(item dict, model bytes, texture bytes, icon bytes or None) of a vanilla item JSON in Assets.zip."""
    d = json.loads(_read(z, item_json).decode("utf-8-sig"))
    icon = _read(z, d["Icon"]) if d.get("Icon") else None
    return d, _read(z, d["Model"]), _read(z, d["Texture"]), icon


# ================================================================= the SkyWynn metal wand recipe (2026-10-02 art proof)
# Base: the vanilla Wood Wand (vanilla Weapon_Wand_Wood_Rotten already reuses its model with another texture, so a texture swap on
# the same Model / IconProperties is the vanilla pattern). Parts = blockymodel node names of Items/Weapons/Wand/Wood.blockymodel.
WAND_ITEM = "Server/Item/Items/Weapon/Wand/Weapon_Wand_Wood.json"
WAND_PARTS = {"shaft": ("Handle", "Handle2"), "bands": ("Rope3", "Rope4"), "head": ("Stick",),
              "leaves": ("Leave_Staff", "Leave_Staff2")}
METALS = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
# metal colour = the head of the same tier's vanilla pickaxe (nodes Pickaxe, Pickaxe2, Pickaxe3: metal only on every tier - the
# weapon-style shading) blended 50/50 tone by tone with the tier's vanilla ingot texture (the material colour: it makes Thorium
# green-teal, Onyxium purple-black, Adamantite redder than Copper and Mithril whiter than Cobalt, like the bars in the game)
METAL_SOURCE = ("Server/Item/Items/Tool/Pickaxe/Tool_Pickaxe_%s.json", ("Pickaxe*",))
BAR_SOURCE = "Server/Item/Items/Ingredient/Bar/Ingredient_Bar_%s.json"
# leaf crystal colour = the accent of the same tier's vanilla staff: (item, nodes, keep the most colourful share of the texels)
GEM_SOURCE = {
    "Copper": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Copper.json", ("Ribbon",), 1.0),
    "Iron": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Iron.json", ("Base", "Claw*"), 0.25),
    "Thorium": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Thorium.json", ("Staffhead*",), 1.0),
    "Cobalt": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Cobalt.json", ("Knob",), 1.0),
    "Adamantite": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Adamantite.json", ("Gem",), 1.0),
    "Mithril": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Mithril.json", ("Gem",), 1.0),
    "Onyxium": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Onyxium.json", ("Gem",), 1.0),
}
# the bands (the wood wand's rope wraps) are the tier's metal, except where vanilla gives the tier another trim metal
BAND_SOURCE = {"Mithril": ("Server/Item/Items/Weapon/Staff/Weapon_Staff_Mithril.json", ("Band",))}   # vanilla mithril = gold trim
# per part: recolor() settings (+ rim = rim_lift(edge, inner)); style A = all metal, style B = wood handle (shade) + metal head
WAND_TUNE = {
    "shaftA": {"lo": 0.0, "hi": 0.8, "smooth": 0.75, "rank": 0.5, "rim": (0.10, 0.0)},
    "shaftB": {"mul": 0.85},
    "bands": {"lo": 0.35, "hi": 1.0, "smooth": 0.3, "rank": 0.5, "rim": (0.10, 0.0)},
    "head": {"lo": 0.05, "hi": 1.0, "smooth": 0.75, "rank": 0.5, "rim": (0.14, -0.04)},
    "leaves": {"lo": 0.15, "hi": 1.0},
}
WAND_METAL_TUNE = {   # per-metal changes to WAND_TUNE
    "Onyxium": {"shaftA": {"rank": 0.8, "lo": 0.1, "hi": 0.9}, "bands": {"rank": 0.8, "lo": 0.5}, "head": {"rank": 0.8, "lo": 0.22}},
    "Mithril": {"bands": {"lo": 0.1, "hi": 0.9}},   # the gold trim: richer gold, not the top yellow
}
WAND_STYLES = {"A": "full metal", "B": "wood handle + metal head"}


def _chroma(c):
    return max(c[:3]) - min(c[:3])


def metal_gradient(z, metal):
    """The tier's metal gradient (dark -> light): vanilla pickaxe head texels mixed 50/50 with the vanilla ingot texture."""
    item, nodes = METAL_SOURCE
    _d, model, tex, _icon = item_parts(z, item % metal)
    _bd, _bmodel, bar_tex, _bicon = item_parts(z, BAR_SOURCE % metal)
    return grad_mix(palette_from([(tex, node_rects(model, nodes))]), palette_from([bar_tex]), 0.5)


def gem_gradient(z, metal):
    """The tier's accent (leaf crystal) gradient from its vanilla staff (the most colourful share of the named node texels)."""
    item, nodes, share = GEM_SOURCE[metal]
    _d, model, tex, _icon = item_parts(z, item)
    im = _img(tex)
    pix = [im.get(x, y) for x, y, _ri in _region_points(im, node_rects(model, nodes), 128)]
    if share < 1.0:
        pix.sort(key=lambda c: (-_chroma(c), c))
        pix = pix[:max(8, int(len(pix) * share))]
    strip = Img(len(pix), 1)
    for i, c in enumerate(pix):
        strip.put(i, 0, c)
    return palette_from([strip])


def band_gradient(z, metal):
    """The tier's band (rope wrap) gradient: its trim metal from BAND_SOURCE, else its own metal."""
    if metal not in BAND_SOURCE:
        return metal_gradient(z, metal)
    item, nodes = BAND_SOURCE[metal]
    _d, model, tex, _icon = item_parts(z, item)
    return palette_from([(tex, node_rects(model, nodes))])


def _tuned(metal, part):
    p = dict(WAND_TUNE[part])
    p.update(WAND_METAL_TUNE.get(metal, {}).get(part, {}))
    return p


def wand_texture(z, metal, style):
    """The metal wand texture PNG (64x32, same UV layout as Items/Weapons/Wand/Wood_Texture.png) for METALS x WAND_STYLES."""
    if metal not in METALS or style not in WAND_STYLES:
        raise ValueError("wand_texture: metal %r / style %r" % (metal, style))
    _d, model, tex, _icon = item_parts(z, WAND_ITEM)
    rects = dict((k, node_rects(model, v)) for k, v in WAND_PARTS.items())
    grads = {"metal": metal_gradient(z, metal), "band": band_gradient(z, metal), "gem": gem_gradient(z, metal)}
    img = _img(tex)

    def part(img, grad, name, tune):
        p = dict(tune)
        rim = p.pop("rim", None)
        if rim:
            p["lift"] = rim_lift(rects[name], rim[0], rim[1])
        return recolor(img, grad, rects[name], as_img=True, **p)

    if style == "A":
        img = part(img, grads["metal"], "shaft", _tuned(metal, "shaftA"))
    else:
        img = shade(img, rects["shaft"], as_img=True, **_tuned(metal, "shaftB"))
    img = part(img, grads["band"], "bands", _tuned(metal, "bands"))
    img = part(img, grads["metal"], "head", _tuned(metal, "head"))
    img = part(img, grads["gem"], "leaves", _tuned(metal, "leaves"))
    return png_encode(img)


def wand_art(z, metal, style, icon_size=64):
    """(texture PNG, icon PNG) of a SkyWynn metal wand. The item JSON keeps the Wood Wand's Model and IconProperties and points
    Texture / Icon at these two files (the way vanilla Weapon_Wand_Wood_Rotten reuses the model)."""
    d, model, _tex, _icon = item_parts(z, WAND_ITEM)
    tex = wand_texture(z, metal, style)
    return tex, render_icon(model, tex, d["IconProperties"], size=icon_size)


# ================================================================= build-time self check
VERIFY_ICONS = ("Server/Item/Items/Weapon/Wand/Weapon_Wand_Wood.json", "Server/Item/Items/Weapon/Wand/Weapon_Wand_Wood_Rotten.json",
                "Server/Item/Items/Weapon/Staff/Weapon_Staff_Iron.json")


def verify(assets_zip=None, quiet=False, max_colour=4.0, max_alpha=1.5):
    """Prove at build time (Assets.zip read-only) that: the PNG codec round-trips vanilla files, render_icon still reproduces the
    vanilla wand / staff icons (VERIFY_ICONS, mean colour error <= max_colour, alpha <= max_alpha on 0..255), and every vanilla
    file / node the wand recipe reads still exists and the wand parts use separate texels. Raises ArtCheckError otherwise."""
    z = assets(assets_zip)
    try:
        bad, worst = _verify(z, max_colour, max_alpha)
    finally:
        z.close()
    if bad:
        raise ArtCheckError("skyyart.verify failed:\n  " + "\n  ".join(bad))
    if not quiet:
        print("skyyart %s checked: PNG codec, icon renderer on %d vanilla icons (worst colour %.2f, alpha %.2f / 255), wand recipe "
              "sources for %d metals" % (KIT_VERSION, len(VERIFY_ICONS), worst[0], worst[1], len(METALS)))
    return {"colour": worst[0], "alpha": worst[1]}


def _verify(z, max_colour, max_alpha):
    bad, worst = [], [0.0, 0.0]
    for item in VERIFY_ICONS:
        try:
            d, model, tex, icon = item_parts(z, item)
        except ArtCheckError as e:
            bad.append(str(e))
            continue
        for png in (tex, icon):
            img = png_decode(png)
            if bytes(png_decode(png_encode(img)).px) != bytes(img.px):
                bad.append("PNG round trip changed pixels of %s" % item)
        ec, ea = check_icon(model, tex, d.get("IconProperties"), icon)
        worst = [max(worst[0], ec), max(worst[1], ea)]
        if ec > max_colour or ea > max_alpha:
            bad.append("render_icon drifted from the vanilla icon of %s (colour %.2f, alpha %.2f)" % (item, ec, ea))
    try:
        _d, model, _t, _i = item_parts(z, WAND_ITEM)
        have = set(node_names(model))
        rects = {}
        for part, nodes in WAND_PARTS.items():
            for n in nodes:
                if n not in have:
                    bad.append("wand model has no node %r (part %s)" % (n, part))
            rects[part] = node_rects(model, nodes)
        keys = sorted(rects)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if rects_overlap(rects[keys[i]], rects[keys[j]]):
                    bad.append("wand parts %s and %s share texels" % (keys[i], keys[j]))
        for m in METALS:
            for item, nodes in ((METAL_SOURCE[0] % m, METAL_SOURCE[1]), (GEM_SOURCE[m][0], GEM_SOURCE[m][1]),
                                (BAND_SOURCE.get(m, (None, None))[0], BAND_SOURCE.get(m, (None, None))[1]), (BAR_SOURCE % m, None)):
                if item is None:
                    continue
                _d2, mdl, _tx, _ic = item_parts(z, item)
                if nodes and not node_rects(mdl, nodes):
                    bad.append("%s has no node %s" % (item, "/".join(nodes)))
    except ArtCheckError as e:
        bad.append(str(e))
    return bad, worst
