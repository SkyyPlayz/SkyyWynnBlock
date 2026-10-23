"""Harness for SkyyUiProbe 0.8 (the UI queue probe, 15 cases; SkyyUiProbe/build_skyyuiprobe_0.8.py).
Build first: python SkyyUiProbe/build_skyyuiprobe_0.8.py

    python SkyyUiProbe/test_skyyuiprobe_0.8.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs: the game's JRE, the cached HytaleServer.jar, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  J   jar      manifest (op-only probe text, asset pack), the classes, every picture under our roots with even (2x) sizes, no .ui file,
               the 15 page data files + nodes, the particle files (JSON, every spawner id + texture resolves: ours in the jar, the
               vanilla Glow in Assets.zip), the build's asset list (dump.json written by the build's dump-only run below)
  A   verify   every class loads + initialises with -Xverify:all
  X   exec     -Xverify:all, the SkyyMenu 0.3.19 harness's engine stand-ins (a player with the REAL PageManager / WindowManager, a
               recording packet handler, a world with a task queue) + a TransformComponent, a PlayerSkinComponent, the game's
               CosmeticRegistry filled from the installed Cosmetics JSON (the engine's own PlayerSkinPart(BsonDocument) parsers) and the
               test skin's models / textures registered as CommonAssets from Assets.zip (in memory, read only), the probe's scheduler
               swapped for a RECORDING one (the harness runs each timed step itself, then the world queue). EVERY case's server path:
       HELP    /skyprobe help / "" / list = the 15 cases; an unknown case = a chat line, no page
       OPEN    each case through ProbeCmds (the real PageManager.openCustomPage): one CustomPage packet = every element + the case's
               runtime sets, its bindings, the 'build #1: N elements' log line, the 'opened' line
       TOUR    /skyprobe tour: the H1a picture goes out (AssetInitialize / AssetPart / AssetFinalize) BEFORE the first CustomPage
               packet; /skyprobe next walks case by case; after the last case it says the tour is done
       CASES   M4 Next state x5 = 5 updates of 3 commands; M5 a node = 1 update (Anchor + 2 texts); M8a 3 nodes = 3 updates (halo Anchor,
               the node picture Visible pair, the disc AssetPath, 2 texts), 0 rebuilds; M8b pans = 1 Anchor update each, clamped, Centre
               on the selected node, Rebuild redraws AT the kept offset; M8c pans + Reset; H1a / H1b / H1c pictures (asset packets
               BEFORE the page packet, H1b = assets + ONE update, a repeat = no assets); H1c your head composed from the installed game
               files == the harness's own Python reference render (same rules), with a hat (half covering -> the generic haircut);
               D1 Next / Skip = one rebuild each, Accept / Not now = one update, Esc logged; T1 tiles answer; K1 / F1 / F2 / G1 'run' =
               the close FIRST, then (F1) 9 Notification packets (styles, the item icons, the texts), (F2) 5 with ONE tag, (G1) 21
               steps of SpawnParticleSystem packets to the player only (A / B per dot, C one rotated system), the chat stand-in lines,
               C's yaw follows the target when the player moves
       ANSWER  on every case page, EVERY bound event id = exactly ONE CustomPage packet (a case switch = its rebuild, Rebuild = 1,
               Close / run = the close); malformed / unknown data and a thrown error get one answer too (the safety net)
       CMDS    the command classes construct (admin: requirePermission skyyuiprobe.admin + no permission groups; alias uiprobe)
  AA  audit    every class / member reference the JVM's access rules would refuse (MethodHandles.privateLookupIn) + the control
Scratch: tools/dev/scratch/uiprobe08/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, importlib.util, struct, math, zlib, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import serverjar

VERSION = "0.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "uiprobe08", "harness")))
PKG = "com.skyy.uiprobe."
CLASSES = ["ProbeLog", "ProbeData", "ProbeThreads", "ProbeTimer", "RtAsset", "RtPic", "HeadResult", "Heads", "Later", "MapPage", "ProbeCmds",
           "SkyProbeArgCmd", "SkyProbeCmd", "SkyyUiProbePlugin"]
SKIN_FIELDS = ["bodyCharacteristic", "underwear", "face", "eyes", "ears", "mouth", "facialHair", "haircut", "eyebrows", "pants", "overpants",
               "undertop", "overtop", "shoes", "headAccessory", "faceAccessory", "earAccessory", "skinFeature", "gloves", "cape"]
HEAD_ORDER = ["bodyCharacteristic", "ears", "face", "mouth", "eyes", "eyebrows", "facialHair", "haircut", "faceAccessory", "headAccessory",
              "earAccessory"]
REG_FILE = {"bodyCharacteristic": "BodyCharacteristics", "ears": "Ears", "face": "Faces", "mouth": "Mouths", "eyes": "Eyes",
            "eyebrows": "Eyebrows", "facialHair": "FacialHair", "haircut": "Haircuts", "faceAccessory": "FaceAccessory",
            "headAccessory": "HeadAccessory", "earAccessory": "EarAccessory"}
REG_FIELD = {"bodyCharacteristic": "bodyCharacteristics", "ears": "ears", "face": "faces", "mouth": "mouths", "eyes": "eyes",
             "eyebrows": "eyebrows", "facialHair": "facialHair", "haircut": "haircuts", "faceAccessory": "faceAccessory",
             "headAccessory": "headAccessory", "earAccessory": "earAccessory"}
SKIN_A = {"bodyCharacteristic": "Default.07", "face": "Face_Neutral", "eyes": "Medium_Eyes.Blue", "ears": "Default", "mouth": "Mouth_Default",
          "eyebrows": "Medium.BrownDark", "haircut": "Morning.Black", "facialHair": "Goatee.Black", "faceAccessory": "RoundGlasses.Black",
          "underwear": "Bra.Blue", "pants": "Jeans.Blue", "undertop": "Tshirt.White", "shoes": "Boots.Brown"}
SKIN_B = dict(SKIN_A, haircut="PonyTail.Red", facialHair="", faceAccessory="", headAccessory="CowboyHat.Brown", bodyCharacteristic="Default.14")


def load_dump():
    return json.load(open(os.path.join(SCRATCH, "assets", "dump.json"), encoding="utf-8"))


# ================================================================= the Python reference head (the same rules as the Java Heads class)
def png_decode(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    i, idat, plte, trns = 8, b"", None, None
    while i < len(data):
        n, = struct.unpack(">I", data[i:i + 4]); t = data[i + 4:i + 8]; body = data[i + 8:i + 8 + n]; i += 12 + n
        if t == b"IHDR":
            w, h, bd, ct, _c, _f, il = struct.unpack(">IIBBBBB", body)
        elif t == b"PLTE":
            plte = body
        elif t == b"tRNS":
            trns = body
        elif t == b"IDAT":
            idat += body
    assert bd == 8 and il == 0, (bd, il)
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat)
    stride = w * ch
    out, prev, p = [], bytearray(stride), 0
    for y in range(h):
        f = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        for x in range(w):
            q = line[x * ch:(x + 1) * ch]
            if ct == 6: out.append(tuple(q))
            elif ct == 2: out.append((q[0], q[1], q[2], 255))
            elif ct == 0: out.append((q[0], q[0], q[0], 255))
            elif ct == 4: out.append((q[0], q[0], q[0], q[1]))
            else:
                k = q[0]; a_ = trns[k] if trns and k < len(trns) else 255
                out.append((plte[3 * k], plte[3 * k + 1], plte[3 * k + 2], a_))
        prev = line
    return w, h, out


class Ref(object):
    """the Python twin of Heads: resolve the skin -> faces -> raster (auto-fit view), from Assets.zip (read only, in memory)"""
    FACES = [(((-1, 1, 1), (1, 1, 1), (-1, -1, 1)), (0, 1)), (((1, 1, -1), (-1, 1, -1), (1, -1, -1)), (0, 1)),
             (((1, 1, 1), (1, 1, -1), (1, -1, 1)), (2, 1)), (((-1, 1, -1), (-1, 1, 1), (-1, -1, -1)), (2, 1)),
             (((-1, 1, -1), (1, 1, -1), (-1, 1, 1)), (0, 2)), (((-1, -1, 1), (1, -1, 1), (-1, -1, -1)), (0, 2))]
    FN = ["front", "back", "left", "right", "top", "bottom"]
    QN = ["+Z", "-Z", "+X", "-X", "+Y", "-Y"]

    def __init__(self, z):
        self.z = z
        self.reg = dict((k, dict((e["Id"], e) for e in json.loads(z.read("Cosmetics/CharacterCreator/%s.json" % f).decode("utf-8-sig"))))
                        for k, f in REG_FILE.items())
        self.gs = dict((g["Id"], g["Gradients"]) for g in json.loads(z.read("Cosmetics/CharacterCreator/GradientSets.json").decode("utf-8-sig")))
        self.used = set()

    def j(self, path):
        self.used.add(path)
        return json.loads(self.z.read("Common/" + path).decode("utf-8-sig"))

    def tex(self, path):
        self.used.add(path)
        return png_decode(self.z.read("Common/" + path))

    @staticmethod
    def V(d, k, dflt=0.0):
        v = (d or {}).get(k) or {}
        return [float(v.get("x", dflt)), float(v.get("y", dflt)), float(v.get("z", dflt))]

    @staticmethod
    def Q(d, k):
        v = (d or {}).get(k) or {}
        return [float(v.get("x", 0)), float(v.get("y", 0)), float(v.get("z", 0)), float(v.get("w", 1))]

    @staticmethod
    def qmul(a, b):
        return [a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
                a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2]]

    @staticmethod
    def qrot(q, vx, vy, vz):
        n = math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]) or 1.0
        x, y, z, w = q[0] / n, q[1] / n, q[2] / n, q[3] / n
        tx = 2.0 * (y * vz - z * vy); ty = 2.0 * (z * vx - x * vz); tz = 2.0 * (x * vy - y * vx)
        return [vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx)]

    def emit(self, out, ctr, qw, f, hx, hy, hz, w, h, lay, neg, kind, part):
        r = [0.0] * 18
        cs = self.FACES[f][0]
        for i in range(3):
            c = self.qrot(qw, cs[i][0] * hx, cs[i][1] * hy, cs[i][2] * hz)
            r[i * 3:i * 3 + 3] = [ctr[0] + c[0], ctr[1] + c[1], ctr[2] + c[2]]
        off = lay.get("offset") or {}
        ox, oy = float(off.get("x", 0)), float(off.get("y", 0))
        mi = lay.get("mirror") or {}
        mx, my = bool(mi.get("x", False)), bool(mi.get("y", False))
        a = (int(round(float(lay.get("angle", 0) or 0))) % 360 + 360) % 360
        rw, rh = (w, h) if a in (0, 180) else (h, w)
        for i in range(3):
            s = 1.0 if i == 1 else 0.0
            t = 1.0 if i == 2 else 0.0
            if mx: s = 1.0 - s
            if my: t = 1.0 - t
            s2, t2 = s, t
            if a == 90: s2, t2 = t, 1.0 - s
            elif a == 180: s2, t2 = 1.0 - s, 1.0 - t
            elif a == 270: s2, t2 = 1.0 - t, s
            r[9 + i * 2] = ox + s2 * rw
            r[10 + i * 2] = oy + t2 * rh
        e1x, e1y = r[3] - r[0], r[4] - r[1]
        e2x, e2y = r[6] - r[0], r[7] - r[1]
        nz = e2x * e1y - e2y * e1x
        r[15] = -nz if neg else nz
        r[16] = kind
        r[17] = part
        out.append(r)

    def shape(self, n, ctr, qw, part, out):
        sh = n.get("shape")
        if not sh or not sh.get("visible", True) or sh.get("type") not in ("box", "quad"):
            return
        st = sh.get("settings") or {}
        sz = self.V(st, "size")
        sx = [1.0, 1.0, 1.0] if not sh.get("stretch") else self.V(sh, "stretch", 1.0)
        sx = [1.0 if v == 0.0 else v for v in sx]
        neg = sx[0] * sx[1] * sx[2] < 0.0
        tl = sh.get("textureLayout")
        if not tl:
            return
        if sh["type"] == "box":
            for f in range(6):
                lay = tl.get(self.FN[f])
                if not isinstance(lay, dict):
                    continue
                ax = self.FACES[f][1]
                self.emit(out, ctr, qw, f, sz[0] * sx[0] / 2.0, sz[1] * sx[1] / 2.0, sz[2] * sx[2] / 2.0, sz[ax[0]], sz[ax[1]], lay, neg, 0, part)
            return
        lay = tl.get("front")
        if not isinstance(lay, dict):
            return
        f = 0
        for i in range(6):
            if self.QN[i] == st.get("normal"):
                f = i
        ax = self.FACES[f][1]
        h3 = [0.0, 0.0, 0.0]
        h3[ax[0]] = sz[0] * sx[0] / 2.0
        h3[ax[1]] = sz[1] * sx[1] / 2.0
        self.emit(out, ctr, qw, f, h3[0], h3[1], h3[2], sz[0], sz[1], lay, neg, 1, part)

    def walk(self, n, origin, q, root, kids, part, out):
        ctr, qw = origin, q
        if not root:
            p = self.V(n, "position")
            r = self.qrot(q, p[0], p[1], p[2])
            qw = self.qmul(q, self.Q(n, "orientation"))
            o = self.V(n.get("shape"), "offset")
            r2 = self.qrot(qw, o[0], o[1], o[2])
            ctr = [origin[0] + r[0] + r2[0], origin[1] + r[1] + r2[1], origin[2] + r[2] + r2[2]]
        self.shape(n, ctr, qw, part, out)
        if kids:
            for c in n.get("children") or []:
                if isinstance(c, dict):
                    self.walk(c, ctr, qw, False, True, part, out)

    def head_node(self, body):
        def find(n):
            if n.get("name") == "Head":
                return n
            for c in n.get("children") or []:
                r = find(c)
                if r:
                    return r
        for n in self.j(body)["nodes"]:
            h = find(n)
            if h:
                return h

    def frames(self, body):
        h = self.head_node(body)
        fr = {"Head": [0, 0, 0, 0, 0, 0, 1]}
        for c in h.get("children") or []:
            if c.get("name") in (None, "Neck"):
                continue
            q = self.Q(c, "orientation")
            p = self.V(c, "position")
            o = self.V(c.get("shape"), "offset")
            r = self.qrot(q, o[0], o[1], o[2])
            fr[c["name"]] = [p[0] + r[0], p[1] + r[1], p[2] + r[2]] + q
        return fr

    def model(self, path, body, part, out):
        if path == body:
            self.walk(self.head_node(body), [0, 0, 0], [0, 0, 0, 1], True, False, part, out)
            return
        fr = self.frames(body)
        for root in self.j(path).get("nodes") or []:
            f = fr.get(root.get("name"))
            if f:
                self.walk(root, f[:3], f[3:], True, True, part, out)

    def resolve(self, typ, value, tint):
        if not value:
            return None
        p = value.split(".")
        part = self.reg[typ].get(p[0])
        if part is None:
            return None
        tex = p[1] if len(p) > 1 else tint
        var = p[2] if len(p) > 2 else None
        model, grey, texs, vars_ = part.get("Model"), part.get("GreyscaleTexture"), part.get("Textures"), part.get("Variants")
        vo = vars_.get(var) if (vars_ and var) else None
        if vo is None and model is None and vars_:
            vo = list(vars_.values())[0]
        if vo is not None:
            if vo.get("Model"):
                model = vo["Model"]
            if vo.get("GreyscaleTexture") is not None or vo.get("Textures") is not None:
                grey, texs = vo.get("GreyscaleTexture"), vo.get("Textures")
        if model is None:
            return None
        texture = ramp = None
        if texs and tex and texs.get(tex):
            texture = texs[tex]["Texture"]
        elif grey:
            texture = grey
            gs = part.get("GradientSet")
            if gs and tex and gs in self.gs and tex in self.gs[gs]:
                ramp = self.gs[gs][tex]["Texture"]
        elif texs:
            texture = list(texs.values())[0]["Texture"]
        return None if texture is None else (model, texture, ramp)

    def compose(self, skin):
        body = skin.get("bodyCharacteristic")
        tone = body.split(".")[1] if body and "." in body else None
        hair = skin.get("haircut")
        hat = skin.get("headAccessory")
        if hat:
            hp = self.reg["headAccessory"].get(hat.split(".")[0])
            ht = (hp or {}).get("HeadAccessoryType", "")
            if ht == "FullyCovering":
                hair = None
            elif ht == "HalfCovering" and hair:
                hs = hair.split(".")
                hc = self.reg["haircut"].get(hs[0])
                if hc and hc.get("RequiresGenericHaircut") and hc.get("HairType"):
                    gen = "Generic" + hc["HairType"]
                    if gen in self.reg["haircut"]:
                        hair = gen + ("." + hs[1] if len(hs) > 1 else "")
        bodyR = self.resolve("bodyCharacteristic", body, tone)
        faces, tex, ramps = [], {}, {}
        for i, key in enumerate(HEAD_ORDER):
            r = self.resolve(key, hair if key == "haircut" else skin.get(key), tone)
            if r is None:
                continue
            tex[i] = self.tex(r[1])
            if r[2]:
                w, h, px = self.tex(r[2])
                ramps[i] = [px[min(w - 1, k * w // 256)] for k in range(256)]
            self.model(r[0], bodyR[0], i, faces)
        return self.raster(faces, tex, ramps), hair

    def raster(self, faces, tex, ramps, S=128):
        vis = []
        minx = miny = 1e9
        maxx = maxy = -1e9
        for i, f in enumerate(faces):
            if (f[15] <= 1e-6) if f[16] == 0.0 else (abs(f[15]) <= 1e-6):
                continue
            if int(f[17]) not in tex:
                continue
            vis.append(i)
            x3, y3 = f[3] + f[6] - f[0], f[4] + f[7] - f[1]
            minx = min(minx, f[0], f[3], f[6], x3); maxx = max(maxx, f[0], f[3], f[6], x3)
            miny = min(miny, f[1], f[4], f[7], y3); maxy = max(maxy, f[1], f[4], f[7], y3)
        vis.sort(key=lambda i: ((faces[i][5] + faces[i][8]) / 2.0, faces[i][17], i))
        minx, maxx, miny, maxy = max(minx, -26.0), min(maxx, 26.0), max(miny, -20.0), min(maxy, 34.0)
        if not vis:
            minx, maxx, miny, maxy = -15.0, 15.0, -14.0, 14.0
        size = max(maxx - minx, maxy - miny, 34.0) + 2.0
        cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0
        k = S / size
        img = [0] * (S * S)
        for i in vis:
            f = faces[i]
            w, h, px = tex[int(f[17])]
            rp = ramps.get(int(f[17]))
            p0x, p0y = (f[0] - cx) * k + S / 2.0, (cy - f[1]) * k + S / 2.0
            ax, ay = (f[3] - f[0]) * k, (f[1] - f[4]) * k
            bx, by = (f[6] - f[0]) * k, (f[1] - f[7]) * k
            det = ax * by - ay * bx
            if abs(det) < 1e-9:
                continue
            xs = (p0x, p0x + ax, p0x + bx, p0x + ax + bx)
            ys = (p0y, p0y + ay, p0y + by, p0y + ay + by)
            for py in range(max(0, int(math.floor(min(ys)))), min(S - 1, int(math.floor(max(ys)))) + 1):
                for qx_ in range(max(0, int(math.floor(min(xs)))), min(S - 1, int(math.floor(max(xs)))) + 1):
                    qx, qy = qx_ + 0.5 - p0x, py + 0.5 - p0y
                    s = (qx * by - qy * bx) / det
                    t = (ax * qy - ay * qx) / det
                    if s < 0.0 or s >= 1.0 or t < 0.0 or t >= 1.0:
                        continue
                    u = f[9] + s * (f[11] - f[9]) + t * (f[13] - f[9])
                    v = f[10] + s * (f[12] - f[10]) + t * (f[14] - f[10])
                    iu, iv = int(math.floor(u)), int(math.floor(v))
                    if iu < 0 or iv < 0 or iu >= w or iv >= h:
                        continue
                    r, g, b, a = px[iv * w + iu]
                    if a < 8:
                        continue
                    if rp is not None and r == g == b:
                        r, g, b, _a = rp[r]
                    img[py * S + qx_] = (0xff << 24) | (r << 16) | (g << 8) | b
        return img


def png_rgba(S, argb):
    raw = b"".join(b"\x00" + b"".join(bytes(((v >> 16) & 255, (v >> 8) & 255, v & 255, (v >> 24) & 255)) for v in argb[y * S:(y + 1) * S]) for y in range(S))

    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", S, S, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


# ================================================================= X: exec
def run_exec(out):
    import jpype
    from jpype import JClass, JArray, JByte, JString
    K = HK.Child(out)
    _s = importlib.util.spec_from_file_location("test_skyymenu_0_3_19", os.path.join(ROOT, "SkyyMenu", "test_skyymenu_0.3.19.py"))
    T19 = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(T19)
    hcls = os.path.join(SCRATCH, "hcls_x")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR], verify=True)
    E = T19.engine(SCRATCH, hcls)
    D = load_dump()
    JV = lambda n: JClass(PKG + n)
    LOG, DATA, CMDS, PAGE, TIM, RTP, HEADS = JV("ProbeLog"), JV("ProbeData"), JV("ProbeCmds"), JV("MapPage"), JV("ProbeTimer"), JV("RtPic"), JV("Heads")
    P = E.player(uid=E.OP, name="SkyyProbe")
    PH = "com.hypixel.hytale."
    Ucls = E.U
    # ---- stand-ins: the recording scheduler, the player's position + skin, the cosmetics registry, the test skin's game files
    REC = Ucls.allocateInstance(E.RecEx.class_)
    TIM.EX = REC
    EMc = JClass(PH + "server.core.modules.entity.EntityModule")
    em = EMc.get()
    CTc = JClass(PH + "component.ComponentType")
    ct_skin = CTc()
    E.jf(CTc.class_, "index").setInt(ct_skin, 977)
    E.jf(CTc.class_, "hashCode").setInt(ct_skin, 977)
    E.jf(EMc.class_, "playerSkinComponentType").set(em, ct_skin)
    TCc, V3D, R3F = JClass(PH + "server.core.modules.entity.component.TransformComponent"), JClass("org.joml.Vector3d"), JClass(PH + "math.vector.Rotation3f")
    tc = TCc(V3D(10.5, 64.0, 20.5), R3F())
    P.st.row(P.ref).put(TCc.getComponentType(), tc)
    PSKc, PSCc = JClass(PH + "protocol.PlayerSkin"), JClass(PH + "server.core.modules.entity.player.PlayerSkinComponent")

    def set_skin(sk):
        s_ = PSKc()
        for f_ in SKIN_FIELDS:
            v_ = sk.get(f_)
            setattr(s_, f_, JString(v_) if v_ else None)
        P.st.row(P.ref).put(ct_skin, PSCc(s_))
    set_skin(SKIN_A)
    AZ = zipfile.ZipFile(serverjar.assets_zip())
    BSON = JClass("org.bson.BsonDocument")
    REGc = JClass(PH + "server.core.cosmetics.CosmeticRegistry")
    reg = Ucls.allocateInstance(REGc.class_)
    PSPc, GSc = JClass(PH + "server.core.cosmetics.PlayerSkinPart"), JClass(PH + "server.core.cosmetics.PlayerSkinGradientSet")

    def bson_ctor(cls):
        k_ = cls.class_.getDeclaredConstructor(BSON.class_)
        k_.setAccessible(True)
        return lambda doc: k_.newInstance(doc)
    PSPc, GSc = bson_ctor(PSPc), bson_ctor(GSc)
    for key, fn in REG_FILE.items():
        m_ = E.HashMap()
        for e_ in json.loads(AZ.read("Cosmetics/CharacterCreator/%s.json" % fn).decode("utf-8-sig")):
            m_.put(e_["Id"], PSPc(BSON.parse(json.dumps(e_))))
        E.jf(REGc.class_, REG_FIELD[key]).set(reg, m_)
    gm = E.HashMap()
    for g_ in json.loads(AZ.read("Cosmetics/CharacterCreator/GradientSets.json").decode("utf-8-sig")):
        gm.put(g_["Id"], GSc(BSON.parse(json.dumps(g_))))
    E.jf(REGc.class_, "gradientSets").set(reg, gm)
    CSMc = JClass(PH + "server.core.cosmetics.CosmeticsModule")
    csm = Ucls.allocateInstance(CSMc.class_)
    E.jf(CSMc.class_, "registry").set(csm, reg)
    E.jf(CSMc.class_, "INSTANCE").set(None, csm)
    K.check(CSMc.get() is not None and CSMc.get().getRegistry() is not None, "STAND-IN: the cosmetics registry (the engine's own part parsers)")
    REF = Ref(AZ)
    ref_a, hair_a = REF.compose(SKIN_A)
    ref_b, hair_b = REF.compose(SKIN_B)
    CARc, RTA = JClass(PH + "server.core.asset.common.CommonAssetRegistry"), JV("RtAsset")
    CMAc = JClass(PH + "server.core.asset.common.CommonAsset")
    for pth in sorted(REF.used):
        b_ = AZ.read("Common/" + pth)
        jb = JArray(JByte)(len(b_))
        jb[:] = [x if x < 128 else x - 256 for x in b_]
        CARc.addCommonAsset("Hytale:Hytale", RTA(pth, CMAc.hash(jb), jb))
    K.check(CARc.getByName("Characters/Player.blockymodel") is not None, "STAND-IN: %d game files registered as common assets (read from Assets.zip in memory)" % len(REF.used))

    def tail():
        return [str(x) for x in LOG.TAIL.toArray()]

    def new_lines(n0):
        return tail()[n0:]

    def chats(frm):
        return E.strs_of(P, frm)

    def data(js):
        P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Data, js))

    def click(a):
        E.pump(P)
        data('{"a":"%s"}' % a)

    def kinds(frm):
        return [k_ for k_ in (str(p.getClass().getSimpleName()) for p in E.sent(P)[frm:]) if k_ != "ServerMessage"]

    def pkts(f0, kind="CustomPage"):
        return [p for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == kind]

    def cmds_of(pkt):
        cs = pkt.commands if hasattr(pkt, "commands") else None
        return [] if cs is None else list(cs)

    def cmd_txt(pkt):
        return "\n".join("%s | %s | %s | %s" % (c.type, c.selector, c.data, c.text) for c in cmds_of(pkt)).replace("\\/", "/")

    def is_clear(p):
        return bool(p.clear) if hasattr(p, "clear") else None

    def open_case(key):
        CMDS.arg(P.ref, P.st, P.pr, key)
        E.pump(P)
        return P.pm.getCustomPage()

    def drain(limit=200):
        """run the recorded timer tasks (each hops to the world queue), then the world queue - like the scheduler + world threads"""
        n = 0
        while REC.tasks is not None and not REC.tasks.isEmpty() and n < limit:
            t_ = REC.tasks.get(0)
            REC.tasks.subList(0, 1).clear()
            REC.delays.subList(0, 1).clear()
            t_.run()
            E.run_world(E.W1)
            n += 1
        return n

    # ---- pure helpers
    K.eq([str(x) for x in DATA.KEYS], [c[0] for c in D["cases"]], "DATA: the 15 case keys")
    for i, c in enumerate(D["cases"]):
        K.eq(int(DATA.index(c[0])), i, "DATA: index(%s)" % c[0])
        K.eq(int(DATA.index(c[1].upper())), i, "DATA: index(name %s)" % c[1])
        K.eq(int(DATA.ELEMENTS[i]), D["pages"][c[0]]["elements"], "DATA: element count of %s" % c[0])
    K.eq(int(DATA.index("m1")), -1, "DATA: the retired case m1 is gone")
    for js, want in (('{"a":"n12"}', "n12"), ('{ "a" : "case:m4" }', "case:m4"), ('{"b":"x"}', ""), (None, ""), ('{"a":', "")):
        K.eq(str(DATA.act(js)), want, "DATA: act(%r)" % (js,))
    DATA.nodes()
    K.eq(len(DATA.LABEL), D["nodes"], "DATA: node labels")
    K.eq([(int(DATA.NX[k]), int(DATA.NY[k])) for k in range(D["nodes"])], [tuple(x) for x in D["node_xy"]], "DATA: node centres 100 %")
    K.eq([(int(DATA.NX2[k]), int(DATA.NY2[k])) for k in range(D["nodes"])], [tuple(x) for x in D["node_xy2"]], "DATA: node centres 200 %")
    K.eq(str(RTP.initialsOf("SkyyPlayz")), "SP", "RTPIC: initials of SkyyPlayz")
    K.eq(str(RTP.initialsOf("bob")), "BO", "RTPIC: initials of bob")
    K.eq(str(RTP.initialsOf("")), "?", "RTPIC: initials of nothing")
    p1, p2 = RTP.initials("SkyyProbe", 0), RTP.initials("SkyyProbe", 1)
    K.check(len(p1) == 128 * 128 and list(p1) != list(p2) and list(RTP.initials("SkyyProbe", 0)) == list(p1), "RTPIC: 128 px, the colour follows n, deterministic")

    # ---- HELP
    for w in ("help", "", "list", "HELP"):
        f0 = len(E.sent(P))
        CMDS.arg(P.ref, P.st, P.pr, w)
        s = chats(f0)
        K.check(all(c[0] + " (" + c[1] in s for c in D["cases"]) and "Start with /skyprobe tour" in s, "HELP: '%s' lists the 15 cases" % w)
        K.check(P.pm.getCustomPage() is None, "HELP: '%s' opens no page" % w)
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "m1")
    K.check("No case 'm1'" in chats(f0) and P.pm.getCustomPage() is None, "HELP: an unknown (retired) case says so, no page")

    # ---- TOUR: the H1a picture before ANY page packet; next walks on
    f0, n0 = len(E.sent(P)), len(tail())
    CMDS.arg(P.ref, P.st, P.pr, "tour")
    ks = kinds(f0)
    K.check("AssetInitialize" in ks and "CustomPage" in ks and ks.index("AssetFinalize") < ks.index("CustomPage"),
            "TOUR: the H1a picture (AssetInitialize / Part / Finalize) goes out BEFORE the first page packet")
    pg = P.pm.getCustomPage()
    K.check(pg is not None and str(pg.cs) == "m4", "TOUR: case 1 (m4) is open")
    K.check(any("sent BEFORE any page" in l for l in new_lines(n0)), "TOUR: the log says the picture went first")
    E.pump(P)
    for i in range(1, 4):
        f0 = len(E.sent(P))
        CMDS.arg(P.ref, P.st, P.pr, "next")
        E.pump(P)
        pg = P.pm.getCustomPage()
        K.check(pg is not None and str(pg.cs) == D["cases"][i][0], "TOUR: /skyprobe next opens case %d (%s)" % (i + 1, D["cases"][i][0]))
    CMDS.arg(P.ref, P.st, P.pr, "g1")
    E.pump(P)
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "next")
    K.check("The tour is done" in chats(f0), "TOUR: next after the last case = the tour is done")
    click("close")

    # ---- OPEN every case (fresh page each), check the packet
    DYN = {"m4": 3, "m5": 1, "m6": 0, "m8a": 1, "m8b": 2, "m8c": 0, "h1a": 2, "h1b": 2, "h1c": 3 + 1 + D["head_rows"], "d1": 7, "t1": 0,
           "k1": 0, "f1": 0, "f2": 0, "g1": 0}
    for i, c in enumerate(D["cases"]):
        key = c[0]
        f0, n0 = len(E.sent(P)), len(tail())
        CMDS.arg(P.ref, P.st, P.pr, key if i % 2 == 0 else c[1])
        pg = P.pm.getCustomPage()
        K.check(pg is not None and str(pg.cs) == key, "OPEN %s: the page is open" % key)
        if pg is None:
            continue
        pk = pkts(f0)
        K.eq(len(pk), 1, "OPEN %s: one CustomPage packet" % key)
        if pk:
            cm = cmds_of(pk[0])
            want = D["pages"][key]["appends"] + D["pages"][key]["sets"] + DYN[key]
            K.eq(len(cm), want, "OPEN %s: commands = appends + b.set + the case's runtime sets (%d)" % (key, DYN[key]))
            evs = pk[0].eventBindings if hasattr(pk[0], "eventBindings") else None
            K.eq(0 if evs is None else len(list(evs)), D["pages"][key]["binds"], "OPEN %s: the click bindings" % key)
        K.eq(int(pg.lastElements), D["pages"][key]["elements"], "OPEN %s: elements counted at run time" % key)
        lines = new_lines(n0)
        K.check(any("build #1: %d elements" % D["pages"][key]["elements"] in l for l in lines), "OPEN %s: the build log line" % key)
        K.check(any("opened (" in l and "PASS (server)" in l and "Skyy: look" in l for l in lines), "OPEN %s: the opened line" % key)
        if key == "h1a":
            ks = kinds(f0)
            K.check("CustomPage" in ks and ("AssetInitialize" not in ks or ks.index("AssetFinalize") < ks.index("CustomPage")),
                    "OPEN h1a: a picture (if not on the client yet) goes out BEFORE the page packet")
            K.check(any("H1a picture" in l and "PASS (server)" in l for l in lines), "OPEN h1a: the H1a line")
        if key == "h1c":
            ks = kinds(f0)
            K.check(ks.count("AssetInitialize") == 1 and ks.index("AssetFinalize") < ks.index("CustomPage"), "OPEN h1c: the head picture goes out BEFORE the page")
            K.check(any("H1c head drawn" in l and "PASS (server)" in l for l in lines), "OPEN h1c: the head line")
            K.check(any(l.startswith("C H1c parts 1-5: bodyCharacteristic = Default.07") for l in lines), "OPEN h1c: the parts in chat (5 per line)")
            K.check(sum(1 for l in lines if l.startswith("C H1c parts")) == 4, "OPEN h1c: 20 parts = 4 chat lines")
            K.check(any("H1c your 20 skin parts:" in l and "haircut = Morning.Black" in l for l in lines), "OPEN h1c: all 20 parts in the log")
        E.pump(P)
    click("close")

    # ---- H1c: the head == the Python reference render (the same rules, from the same game files)
    hr = HEADS.compose(P.pr, P.ref, P.st)
    K.check(bool(hr.ok) and hr.png is not None, "H1C: composed (%s)" % str(hr.note))
    if hr.px is not None:
        jpx = [int(v) & 0xffffffff for v in hr.px]
        same = sum(1 for a, b in zip(jpx, ref_a) if a == b)
        K.check(same >= 0.995 * len(ref_a), "H1C: the Java head == the Python reference (%d of %d pixels)" % (same, len(ref_a)))
        drawn = sum(1 for v in jpx if v)
        K.check(drawn > 4000, "H1C: the head fills the picture (%d drawn pixels of 16384)" % drawn)
        hairpx = sum(1 for v in jpx if v and ((v >> 16) & 255) < 40 and ((v >> 8) & 255) < 40 and (v & 255) < 50)
        K.check(hairpx > 300, "H1C: dark (black hair / goatee) pixels present: %d" % hairpx)
        open(os.path.join(SCRATCH, "head_java.png"), "wb").write(bytes(bytearray((x + 256) % 256 for x in hr.png)))
        open(os.path.join(SCRATCH, "head_ref.png"), "wb").write(png_rgba(128, ref_a))
        K.notes.append("H1c: %s, %d faces visible, %d drawn, %d ms, skipped roots %d" % (str(hr.note), int(hr.faces), int(hr.drawn), int(hr.ms), int(hr.skipped)))
    set_skin(SKIN_B)
    hb = HEADS.compose(P.pr, P.ref, P.st)
    K.check(bool(hb.ok), "H1C: the hat skin composes (%s)" % str(hb.note))
    K.check("GenericLong" in str(hb.note) or "GenericMedium" in str(hb.note) or "GenericShort" in str(hb.note) or hair_b == SKIN_B["haircut"],
            "H1C: a half-covering hat swaps the haircut like the reference (%s / ref %s)" % (str(hb.note), hair_b))
    if hb.px is not None:
        jpx = [int(v) & 0xffffffff for v in hb.px]
        same = sum(1 for a, b in zip(jpx, ref_b) if a == b)
        K.check(same >= 0.995 * len(ref_b), "H1C: the hat head == the reference (%d of %d)" % (same, len(ref_b)))
        open(os.path.join(SCRATCH, "head_hat_java.png"), "wb").write(bytes(bytearray((x + 256) % 256 for x in hb.png)))
    set_skin(SKIN_A)
    P.st.row(P.ref).remove(ct_skin)
    hn = HEADS.compose(P.pr, P.ref, P.st)
    K.check(not bool(hn.ok) and "no skin" in str(hn.note), "H1C: no skin component = a clear note, no crash")
    set_skin(SKIN_A)

    # ---- CASE CLICKS
    pg = open_case("m4")
    seen = []
    for i in range(5):
        f0 = len(E.sent(P))
        click("m4next")
        pk = pkts(f0)
        K.eq(len(pk), 1, "M4 #%d: one packet" % (i + 1))
        if pk:
            K.eq(len(cmds_of(pk[0])), 3, "M4 #%d: ONLY 3 commands (2 AssetPath + 1 text)" % (i + 1))
            j = (i + 1) % 5
            s = cmd_txt(pk[0])
            K.check(D["m4_2x"][j] in s and D["m4_1x"][j] in s and "#SkyyPrA1.AssetPath" in s, "M4 #%d: the state %d paths" % (i + 1, j))
            seen.append(j)
    K.eq(seen, [1, 2, 3, 4, 0], "M4: states cycle")
    K.eq(int(pg.builds), 1, "M4: never rebuilt")
    pg = open_case("m5")
    f0, n0 = len(E.sent(P)), len(tail())
    click("n7")
    pk = pkts(f0)
    K.eq(len(pk), 1, "M5: one update packet")
    if pk:
        K.eq(len(cmds_of(pk[0])), 3, "M5: 3 commands (the Anchor + 2 texts)")
        K.check("#SkyyPrSel.Anchor" in cmd_txt(pk[0]), "M5: the halo Anchor set")
    K.check(int(pg.sel) == 7 and int(pg.builds) == 1, "M5: selected 7, never rebuilt")
    K.check(any("M5 sent: ONE Anchor update moved the halo to node 7" in l for l in new_lines(n0)), "M5: the line")
    pg = open_case("m6")
    n0 = len(tail())
    for i in range(3):
        click("tip%d" % i)
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Dismiss, None))
    l_ = new_lines(n0)
    K.eq(sum(1 for l in l_ if l.startswith("I M6 click on tooltip disc")), 3, "M6: 3 tooltip discs answer")
    K.check(any("page closed (Esc or Close)" in l and "M6: Skyy: look" in l for l in l_), "M6: Esc logged")
    pg = open_case("m8a")
    n0 = len(tail())
    for i, k in enumerate((140, 141, 142)):
        f0 = len(E.sent(P))
        click("n%d" % k)
        pk = pkts(f0)
        K.eq(len(pk), 1, "M8A click %d: one packet" % (i + 1))
        if pk:
            s = cmd_txt(pk[0])
            K.check(not is_clear(pk[0]), "M8A click %d: an update, not a redraw" % (i + 1))
            K.check("#SkyyPrSel.Anchor" in s and "#SkyyPrN%dV.Visible" % k in s and "#SkyyPrAd.AssetPath" in s and "#SkyyPrTName.Text" in s,
                    "M8A click %d: halo Anchor + node picture Visible + disc AssetPath + texts" % (i + 1))
            if i > 0:
                K.check("#SkyyPrN%dV.Visible" % (k - 1) in s, "M8A click %d: the last node's picture swapped back" % (i + 1))
            K.eq(len(cmds_of(pk[0])), 5 if i == 0 else 6, "M8A click %d: commands" % (i + 1))
            if i == 0:
                K.notes.append("M8a update: " + s[:500])
    K.eq(int(pg.builds), 1, "M8A: 3 clicks, 0 rebuilds")
    K.check(any("M8a PASS (server) - 3 node clicks" in l for l in new_lines(n0)), "M8A: the PASS line")
    pg = open_case("m8b")
    W2, H2 = D["map2"]
    mx, my = W2 - 840, H2 - 774
    for act, want in (("pan:right", (210, 0)), ("pan:right", (420, 0)), ("pan:down", (420, 210)), ("pan:left", (210, 210)), ("pan:up", (210, 0)),
                      ("pan:up", (210, 0)), ("pan:right", (420, 0)), ("pan:right", (630, 0)), ("pan:right", (mx, 0)), ("pan:right", (mx, 0))):
        f0 = len(E.sent(P))
        click(act)
        pk = pkts(f0)
        K.check(len(pk) == 1 and (int(pg.ox), int(pg.oy)) == want, "M8B %s: one update, offset %s (got %s)" % (act, want, (int(pg.ox), int(pg.oy))))
        if pk:
            K.check("#SkyyPrMp.Anchor" in cmd_txt(pk[0]) and len(cmds_of(pk[0])) == 2, "M8B %s: ONE Anchor + the offset text" % act)
    click("n50")
    f0 = len(E.sent(P))
    click("pan:centre")
    want = (max(0, min(mx, D["node_xy2"][50][0] - 420)), max(0, min(my, D["node_xy2"][50][1] - 387)))
    K.eq((int(pg.ox), int(pg.oy)), want, "M8B: Centre on the selected node 50")
    f0 = len(E.sent(P))
    click("pan:rebuild")
    pk = pkts(f0)
    K.check(len(pk) == 1 and int(pg.builds) == 2, "M8B: Rebuild = one page packet")
    if pk:
        s = cmd_txt(pk[0])
        K.check("#SkyyPrMp.Anchor" in s and ("Offset %d, %d" % want) in s, "M8B: the rebuild draws AT the kept offset")
    pg = open_case("m8c")
    f0 = len(E.sent(P))
    for act in ("pan:right", "pan:down", "pan:reset", "pan:left"):
        click(act)
    K.eq(len(pkts(f0)), 4, "M8C: 4 pans = 4 updates")
    K.eq((int(pg.ox), int(pg.oy)), (-210, 0), "M8C: inside the scroll box the offset is not clamped (learn case)")
    K.check("#SkyyPrCv.Anchor" in cmd_txt(pkts(f0)[-1]), "M8C: the canvas Anchor inside the scroll box")
    # H1a / H1b
    pg = open_case("h1b")
    f0, n0 = len(E.sent(P)), len(tail())
    click("h1bnew")
    ks = kinds(f0)
    K.eq(ks, ["AssetInitialize", "AssetPart", "AssetFinalize", "CustomPage"], "H1B: a new picture = its 3 asset packets, then ONE page update")
    pk = pkts(f0)
    if pk:
        K.check(not is_clear(pk[0]) and "#SkyyPrHp.AssetPath" in cmd_txt(pk[0]) and str(pg.picPath) in cmd_txt(pk[0]), "H1B: the update names the new picture")
    p_a = str(pg.picPath)
    for i in range(5):
        click("h1bnew")
    K.check(str(pg.picPath) != p_a, "H1B: each click a new picture name")
    K.check(any("H1b click 1:" in l and "sent while the page is open" in l for l in new_lines(n0)), "H1B: the log line")
    pg.picN = 5                                   # back to a colour already sent (6 colours): no asset packets, still ONE update
    f0 = len(E.sent(P))
    click("h1bnew")
    K.eq(kinds(f0), ["CustomPage"], "H1B: a picture already on the client = no asset packets, ONE update")
    # H1c redraw / parts
    pg = open_case("h1c")
    f0 = len(E.sent(P))
    click("h1credraw")
    K.eq(kinds(f0), ["CustomPage"], "H1C: Redraw with the same skin = no new picture, ONE update")
    set_skin(dict(SKIN_A, haircut="Viking.Blond"))
    f0 = len(E.sent(P))
    click("h1credraw")
    K.eq(kinds(f0), ["AssetInitialize", "AssetPart", "AssetFinalize", "CustomPage"], "H1C: Redraw after a skin change = the new picture + ONE update")
    set_skin(SKIN_A)
    f0, n0 = len(E.sent(P)), len(tail())
    click("h1cparts")
    K.eq(sum(1 for l in new_lines(n0) if l.startswith("C H1c part ")), 20, "H1C: Parts to chat = 20 lines")
    # D1
    pg = open_case("d1")
    f0 = len(E.sent(P))
    click("dnext")
    pk = pkts(f0)
    K.check(len(pk) == 1 and int(pg.dpage) == 1 and D["d1_lines"][1][:30] in cmd_txt(pk[0]) and int(pg.builds) == 2, "D1: Next = ONE rebuild with line 2")
    f0 = len(E.sent(P))
    click("dskip")
    pk = pkts(f0)
    K.check(len(pk) == 1 and int(pg.dpage) == 2 and D["d1_reward"] in cmd_txt(pk[0]), "D1: Skip = the last line + the reward")
    K.check("#SkyyPrDAc.Visible | true" in cmd_txt(pk[0]).replace('"', "") or "SkyyPrDAc.Visible" in cmd_txt(pk[0]), "D1: Accept shown on the last line")
    for a in ("daccept", "dnotnow"):
        f0 = len(E.sent(P))
        click(a)
        K.check(len(pkts(f0)) == 1 and int(pg.builds) == 3, "D1: %s = ONE update" % a)
    n0 = len(tail())
    P.pm.handleLegacyCustomPageEvent(P.ref, P.st, E.CPE(E.CPT.Dismiss, None))
    K.check(any("D1: Esc closed the dialogue bar" in l for l in new_lines(n0)), "D1: Esc logged")
    # T1
    pg = open_case("t1")
    n0 = len(tail())
    for i in range(5):
        click("tile%d" % i)
    K.eq(sum(1 for l in new_lines(n0) if l.startswith("I T1 tile") and "clicked" in l), 5, "T1: 5 tiles answer")
    # K1 / F1 / F2 / G1: the close FIRST, then the timed test
    pg = open_case("k1")
    f0, n0 = len(E.sent(P)), len(tail())
    click("run")
    K.check(P.pm.getCustomPage() is None and len(pkts(f0)) == 0, "K1: run = the close")
    K.check(any("K1 page closed" in l and "Skyy: look" in l for l in new_lines(n0)), "K1: the look line")
    for key, n_, kind in (("f1", 9, "Notification"), ("f2", 5, "Notification")):
        pg = open_case(key)
        f0, n0 = len(E.sent(P)), len(tail())
        click("run")
        K.check(P.pm.getCustomPage() is None and len(pkts(f0)) == 0 and len(pkts(f0, kind)) == 0, "%s: the page closes FIRST, nothing sent yet" % key.upper())
        K.eq([int(x) for x in REC.delays.toArray()], [1000 if key == "f1" else 600], "%s: the test starts later (scheduled)" % key.upper())
        steps = drain()
        nt = pkts(f0, kind)
        K.eq(len(nt), n_, "%s: %d notifications" % (key.upper(), n_))
        K.eq(steps, n_, "%s: %d timed steps" % (key.upper(), n_))
        if key == "f1" and len(nt) == 9:
            st_ = [str(p.style) for p in nt]
            K.eq(st_[5:], ["Default", "Success", "Warning", "Danger"], "F1: the 4 styles")
            K.check(all(p.tag is None for p in nt), "F1: no tag")
            K.check(nt[0].item is not None and nt[2].item is not None, "F1: the XP and Fortune cards carry an item icon")
            txt = E.strs_of(P, f0)
            K.check("Trork Mauler" in txt and "Fortune! " in txt and "|||||||" in txt and "Copper Collection III" in txt and "#e8c25a" in txt,
                    "F1: the card texts + the gold colour")
            K.check(nt[1].secondaryMessage is not None, "F1: the kill card has a second line")
        if key == "f2" and len(nt) == 5:
            K.check(all(str(p.tag) == "skyy:xp:Mining" for p in nt), "F2: one tag on all 5")
            K.check("+50 XP" in E.strs_of(P, f0), "F2: counts up to +50 XP")
        K.check(any(key.upper() + " PASS (server)" in l for l in new_lines(n0)), "%s: the PASS line" % key.upper())
    pg = open_case("g1")
    f0, n0 = len(E.sent(P)), len(tail())
    click("run")
    K.check(P.pm.getCustomPage() is None and len(pkts(f0)) == 0, "G1: the page closes FIRST")
    steps = 0
    for i in range(21):
        if i == 15:                                  # the player walks 12 blocks east: trail C must turn
            tc.setPosition(V3D(22.5, 64.0, 20.5))
        steps += drain(1)
    K.eq(steps, 21, "G1: 21 timed steps")
    sp = pkts(f0, "SpawnParticleSystem")
    ids = [str(p.particleSystemId) for p in sp]
    K.eq((ids.count("SkyyUiProbe_TrailA"), ids.count("SkyyUiProbe_TrailB"), ids.count("SkyyUiProbe_TrailC")), (49, 49, 7),
         "G1: A 7 x 7 dots, B 7 x 7 dots, C 7 rotated systems")
    cs_ = [p for p in sp if str(p.particleSystemId) == "SkyyUiProbe_TrailC"]
    if len(cs_) == 7:
        yw = lambda p: 0.0 if p.rotation is None else float(p.rotation.yaw)
        y0, y1 = yw(cs_[0]), yw(cs_[-1])
        K.check(abs(y0) < 1e-6 and abs(y1) > 0.1, "G1: C's yaw follows the target (straight -Z: %.3f, after walking east: %.3f)" % (y0, y1))
    a_ = [p for p in sp if str(p.particleSystemId) == "SkyyUiProbe_TrailA"]
    if a_:
        K.check(abs(float(a_[0].position.z) - (20.5 - 2.0)) < 1e-6 and abs(float(a_[0].position.y) - 64.15) < 1e-6, "G1: the first dot 2 blocks towards the target, at the feet")
    l_ = new_lines(n0)
    K.check(sum(1 for l in l_ if l.startswith("C Objective: Probe target - ")) == 5, "G1: the chat stand-in every 5 s (5 lines)")
    K.check(any("G1 PASS (server) - 21 s of trail sent to you only" in l for l in l_), "G1: the end line")
    K.check(sum(1 for p in E.sent(P)[f0:] if str(p.getClass().getSimpleName()) == "SpawnParticleSystem") == len(sp), "G1: every particle went to this player")
    # a timed test whose player left stops quietly
    pg = open_case("f2")
    click("run")
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(P.pr, None)
    n0 = len(tail())
    drain()
    K.check(any("stopped at step 0: the player left" in l for l in new_lines(n0)), "LATER: a player who left = the test stops")
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(P.pr, P.ref)
    # nav
    pg = open_case("m4")
    f0, n0 = len(E.sent(P)), len(tail())
    click("back")
    K.check(len(pkts(f0)) == 1 and str(pg.cs) == "m4", "NAV: Back on case 1 = one answer, stays")
    f0 = len(E.sent(P))
    click("next")
    K.check(P.pm.getCustomPage() == pg and str(pg.cs) == "m5" and "SetPage" not in kinds(f0) and len(pkts(f0)) == 1, "NAV: Next = the same page, ONE rebuild")
    click("case:d1")
    K.check(str(pg.cs) == "d1", "NAV: case:d1")
    click("case:m99")
    K.check(str(pg.cs) == "d1", "NAV: an unknown case changes nothing")
    click("close")
    K.check(P.pm.getCustomPage() is None, "NAV: Close closes the page")
    warns = [l for l in tail() if l.startswith("W ") and "unknown click data" not in l]
    K.eq(warns, [], "no WARNING lines")

    # ---- ANSWER: on every case page, EVERY bound event id = exactly ONE page packet
    bad, total, by_kind = [], 0, {}
    for c in D["cases"]:
        key = c[0]
        acts = D["binds"][key]
        K.eq(len(acts), D["pages"][key]["binds"], "ANSWER %s: the binding list = the page's %d bindings" % (key, D["pages"][key]["binds"]))
        pg = open_case(key)
        later = []
        for a in acts:
            if a in ("next", "back", "close", "run", "pan:rebuild", "dnext", "dskip", "h1credraw"):
                later.append(a)
                continue
            if P.pm.getCustomPage() != pg:
                pg = open_case(key)
            f0 = len(E.sent(P))
            click(a)
            pk = pkts(f0)
            total += 1
            kind = a.rstrip("0123456789") if a[:1] == "n" or a[:3] in ("tip", "til") else a.split(":")[0]
            by_kind[kind] = by_kind.get(kind, 0) + 1
            if len(pk) != 1 or is_clear(pk[0]) or P.pm.getCustomPage() != pg or str(pg.cs) != key or int(pg.builds) != 1:
                bad.append((key, a, len(pk), is_clear(pk[0]) if pk else None))
        for a in later:
            pg = open_case(key)
            f0 = len(E.sent(P))
            click(a)
            pk = pkts(f0)
            total += 1
            by_kind[a] = by_kind.get(a, 0) + 1
            if a in ("close", "run"):
                ok = len(pk) == 0 and P.pm.getCustomPage() is None and len(E.sent(P)) > f0
            elif a == "back" and key == "m4" or a == "next" and key == "g1":
                ok = len(pk) == 1 and not is_clear(pk[0]) and P.pm.getCustomPage() == pg
            else:
                ok = len(pk) == 1 and P.pm.getCustomPage() == pg
            if not ok:
                bad.append((key, a, len(pk), P.pm.getCustomPage() is None))
        K.eq(int(pg.nets), 0, "ANSWER %s: the safety net was never needed for a bound event" % key)
        REC.tasks.clear() if REC.tasks is not None else None
        REC.delays.clear() if REC.delays is not None else None
    K.eq(bad, [], "ANSWER: %d bound events on %d case pages, each answered by exactly one page packet (Close / run = the close)" % (total, len(D["cases"])))
    K.notes.append("ANSWER: %d bound events clicked: %s" % (total, ", ".join("%s %d" % kv for kv in sorted(by_kind.items()))))
    pg = open_case("m8a")
    for js, what, net in (('{"b":"x"}', "no 'a' field", 0), ('{"a":"zzz"}', "unknown data", 0), ('{"a":"case:m99"}', "unknown case", 0),
                          ('{"a":"n999"}', "unknown node", 0), ('{"a":"nzz"}', "a thrown error (bad node number)", 1), ("not json", "not JSON", 0)):
        E.pump(P)
        f0, nets0 = len(E.sent(P)), int(pg.nets)
        data(js)
        pk = pkts(f0)
        K.check(len(pk) == 1 and not is_clear(pk[0]) and P.pm.getCustomPage() == pg, "ANSWER: %s = one update packet (%d)" % (what, len(pk)))
        K.eq(int(pg.nets) - nets0, net, "ANSWER: %s - safety net used %d time(s)" % (what, net))
        if net and pk:
            K.eq(len(cmds_of(pk[0])), 0, "ANSWER: the safety net's answer is the engine's EMPTY update (no commands)")
    click("close")
    # ---- commands
    for cn in ("SkyProbeCmd", "SkyProbeArgCmd"):
        try:
            JV(cn)()
            K.check(True, "CMDS: %s constructs" % cn)
        except Exception as ex:
            K.check(False, "CMDS: %s constructs: %s" % (cn, ex))
    root = JV("SkyProbeCmd")()
    K.check("uiprobe" in [str(a) for a in root.getAliases()], "CMDS: alias uiprobe")
    pgs = root.getPermissionGroups() if hasattr(root, "getPermissionGroups") else None
    K.check(pgs is None or len(list(pgs)) == 0, "CMDS: no permission groups")
    K.notes.append("X: %d log lines; asset sends %d" % (len(tail()), int(RTP.SENT)))
    K.save()


def run_jar(out):
    K = HK.Child(out)
    D = load_dump()
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    K.eq((man["Version"], man["Main"], man["IncludesAssetPack"]), (VERSION, "com.skyy.uiprobe.SkyyUiProbePlugin", True), "J: manifest")
    K.check("op only" in man["Description"] and "no data" in man["Description"] and "no HUD" in man["Description"], "J: the description says op only, no data, no HUD")
    K.eq(sorted(n[:-6].split("/")[-1] for n in names if n.endswith(".class")), sorted(CLASSES), "J: classes")
    K.check(not any(n.lower().endswith(".ui") for n in names), "J: no .ui files")
    pngs = [n for n in names if n.endswith(".png")]
    K.check(all((n.startswith("Common/UI/Custom/SkyyUiProbe/") or n == "Common/Particles/Textures/SkyyUiProbe/TrailDot.png") and "_" not in n
                for n in pngs), "J: pictures under our roots only")
    bad = [n for n in pngs if n.endswith("@2x.png") and any(v % 2 for v in struct.unpack(">II", z.read(n)[16:24]))]
    K.eq(bad, [], "J: every @2x picture has even sizes")
    K.eq(sorted(n for n in names if n.startswith("com/skyy/uiprobe/pages/")),
         sorted("com/skyy/uiprobe/pages/%s.txt" % c for c in [c[0] for c in D["cases"]] + ["nodes"]), "J: page data files")
    K.eq(sorted(n for n in names if not n.endswith(".class") and n != "manifest.json"), sorted(D["assets"]), "J: assets = the build's")
    with zipfile.ZipFile(serverjar.assets_zip()) as az:
        azn = set(az.namelist())
        K.check(not any(n in azn for n in names if not n.endswith(".class") and n != "manifest.json"), "J: no jar file shadows a vanilla file")
        systems = [n for n in names if n.endswith(".particlesystem")]
        spawners = dict((n.rsplit("/", 1)[-1].rsplit(".", 1)[0], n) for n in names if n.endswith(".particlespawner"))
        K.eq(sorted(n.rsplit("/", 1)[-1].rsplit(".", 1)[0] for n in systems), sorted(D["psys"]), "J: the 3 particle systems")
        for n in systems:
            for sp in json.loads(z.read(n))["Spawners"]:
                K.check(sp["SpawnerId"] in spawners, "J: %s spawner %s in the jar" % (n, sp["SpawnerId"]))
        for sid, n in spawners.items():
            tx = json.loads(z.read(n))["Particle"]["Texture"]
            K.check(("Common/" + tx) in names or ("Common/" + tx) in azn, "J: %s texture %s resolves" % (sid, tx))
    for c in D["cases"]:
        t = z.read("com/skyy/uiprobe/pages/%s.txt" % c[0]).decode("utf-8")
        K.check("@2x" not in "".join(l for l in t.split("\n") if "Background" in l), "J: %s markup names no @2x file" % c[0])
        K.check("_" not in "".join(i for i in D["ids"][c[0]]), "J: %s element ids hold no underscore" % c[0])
    K.save()


if "--phase" in sys.argv:
    ph = HK.arg("--phase")
    if ph == "mkfake":
        HK.run_mkfake(os.path.join(SCRATCH, "fake"), JAR)
    elif ph == "verify":
        HK.run_verify(HK.arg("--out"), JAR)
    elif ph == "audit":
        HK.run_audit(HK.arg("--out"), JAR, os.path.join(SCRATCH, "fake"))
    elif ph == "exec":
        run_exec(HK.arg("--out"))
    elif ph == "jar":
        run_jar(HK.arg("--out"))
    sys.exit(0)

assert os.path.isfile(JAR), JAR
sc = os.path.realpath(SCRATCH)
assert sc.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "scratch must be inside tools/dev/scratch/"
shutil.rmtree(SCRATCH, ignore_errors=True)
os.makedirs(os.path.join(SCRATCH, "tmp"))
os.makedirs(os.path.join(SCRATCH, "fake"))
env = dict(os.environ)
env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
try:
    p = subprocess.run([sys.executable, os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION), "--dump-only", "--assets-out",
                        os.path.join(SCRATCH, "assets")], env=env, capture_output=True, text=True)
    HK.check(p.returncode == 0, "the build's dump-only run: %s" % p.stderr[-800:])
    for label in ("jar", "mkfake", "verify", "exec", "audit"):
        out = os.path.join(SCRATCH, "%s.json" % label)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR], env=env)
        HK.check(r.returncode == 0, "%s: the child exited cleanly (%s)" % (label, r.returncode))
        if label == "audit":
            if os.path.isfile(out):
                a = json.load(open(out))
                HK.check(not a["refused"] and a["refs"] > 100, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
                HK.check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
                print("AA. engine-access audit: %d references in %d classes, %d refused, control refused" % (a["refs"], a["classes"], len(a["refused"])))
        elif label != "mkfake":
            HK.take(out, label)
finally:
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
print("SkyyUiProbe %s harness: %d ok, %d fail(s)" % (VERSION, HK.OKS[0], len(HK.FAILS)))
for f in HK.FAILS:
    print("FAIL:", f)
sys.exit(1 if HK.FAILS else 0)
