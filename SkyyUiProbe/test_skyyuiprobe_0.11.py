"""Harness for SkyyUiProbe 0.10 (the UI queue probe, 15 cases + the price-tooltip probe R0 + the INVENTORY PROBE P0;
SkyyUiProbe/build_skyyuiprobe_0.11.py, made by tools/uiprobe_0_10_patch.py). Build first: python SkyyUiProbe/build_skyyuiprobe_0.11.py

    python SkyyUiProbe/test_skyyuiprobe_0.11.py [--keep] [--old-jar <the 0.9 jar>] [--dir <folder inside tools/dev/scratch/>]

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
       TIP     (0.9) the price-tooltip probe with an I18nModule stand-in (the real server.lang of Assets.zip under the engine's "server."
               prefix) + an Item asset-map stand-in: tip = ONE UpdateTranslations AddOrUpdate to the caller with the item's description
               key, quotes / \\n cleaned, reset = the server's own text, a Description-less item and an item whose own key differs
               (both keys in the one packet), an unknown id; tiplater = nothing now, ONE packet when the timer task runs (not on the
               world queue); tipgear = ONE probe stack (claws, ItemDisplayMetadata with the translation child) counted 0 -> 1, the key
               packet; a full inventory = FAIL line, nothing sent; tip gear = only the key; the engine's own parser routes
               /skyprobe tip ... (3+ words, GREEDY text) and /skyprobe tipgear; 2 words / an extra word = refused
       INV     (0.10) the inventory probe on a fresh player (storage / hotbar / armour / utility stand-ins, a rolled sword with
               ItemDisplayMetadata): /uiprobe inv = ONE page packet (InventorySectionId -2 / -1 / -3 / -5, every grid's Slots, the
               sword's slot WITHOUT metadata but with its name + description, the drop zone, 25 bindings); every move as the client
               sends it (pick up + drop, the client's source fields or the tracked one): drag, merge (cap 100), swap, split, a part
               stack onto another item refused, release-on-another-slot + its duplicate Dropped (moved ONCE), two drops of one slot
               (the second fails), shift both ways, put back, cancel, double-click, Sort, drag outside (the probe's own drop: ok /
               refused = put back / the real ItemUtils call; the game's own drop through InventoryPacketHandler), native Move / Drop /
               SmartMove observed (left to the game, a drag right after a native move skipped), a change event = ONE refresh, none
               when nothing changed; each = exactly ONE page packet and item totals unchanged. The Probe Bag: tab = ONE rebuild (30
               bindings), drag / shift in and out, drag out of the bag onto the drop zone; EVERY close path gives the bag back:
               Esc, Tab, probe off, disconnect (queued + no world), world change (to the new world's inventory), shutdown, a full
               inventory (feet / kept in memory, given back at the next ready / open); a click after close moves nothing. Tab
               routing: off = untouched, on = PocketCrafting caught by the subhandler / the adapter (never both), CloseWindow 0
               absorbed, other windows left alone, Tab again closes; the sub-packet hooks on a GamePacketHandler stand-in (the
               game's own consumers wrapped, Inventory packets to InventoryPacketHandler, the factory, a connection without the
               natives); /skyprobe inv + /skyprobe tab on|off through the engine's parser
       CMDS    the command classes construct (admin: requirePermission skyyuiprobe.admin + no permission groups; alias uiprobe)
  AA  audit    every class / member reference the JVM's access rules would refuse (MethodHandles.privateLookupIn) + the control
Scratch: tools/dev/scratch/uip010/harness (deleted unless --keep). C = class compare vs the 0.9 jar. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, zipfile, subprocess, importlib.util, struct, math, zlib, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import serverjar

VERSION = "0.11"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old-jar", os.path.join(HERE, "SkyyUiProbe-0.9.jar")))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "uip010", "harness")))
PKG = "com.skyy.uiprobe."
CLASSES = ["ProbeLog", "ProbeData", "ProbeThreads", "ProbeTimer", "RtAsset", "RtPic", "HeadResult", "Heads", "Later", "MapPage", "ProbeCmds",
           "Tips", "TipSend", "SkyProbeArgCmd", "SkyProbeTipCmd", "SkyProbeCmd", "SkyyUiProbePlugin",
           "InvState", "InvPage", "InvTask", "InvRefresh", "InvClose", "InvChange", "InvHooks", "InvHookFactory", "InvWrap", "InvFilter",
           "InvBye", "InvReady", "InvCmds", "SkyProbeTabCmd"]
# class compare vs 0.9: only these classes / members may differ (everything else byte-identical)
CMP_EXPECT = {"ProbeCmds": ["~m arg", "~m help"], "SkyProbeArgCmd": ["~c "], "SkyProbeCmd": ["~c "],
              "SkyyUiProbePlugin": ["~m setup", "~m shutdown"]}
CMP_ADDED = ["InvState", "InvPage", "InvTask", "InvRefresh", "InvClose", "InvChange", "InvHooks", "InvHookFactory", "InvWrap", "InvFilter",
             "InvBye", "InvReady", "InvCmds", "SkyProbeTabCmd"]
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
    from jpype import JClass, JArray, JByte, JString, JShort, JImplements, JOverride
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
    LOG.TAIL.clear()
    n0 = 0
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
    # ---- TIP (0.9): the price-tooltip probe R0 (Price-Tooltips-Spec section 5), every path executed
    TIPS = JV("Tips")
    JMap, JLong = JClass("java.util.HashMap"), JClass("java.util.concurrent.atomic.AtomicLong")
    CHM = JClass("java.util.concurrent.ConcurrentHashMap")
    I18c = JClass(PH + "server.core.modules.i18n.I18nModule")
    i18 = Ucls.allocateInstance(I18c.class_)
    langs, en = CHM(), CHM()
    lang_txt = AZ.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for ln in lang_txt.splitlines():
        if "=" in ln and ln.startswith("items.") and ".description" in ln.split("=", 1)[0]:
            k_, v_ = ln.split("=", 1)
            en.put("server." + k_.strip(), v_.strip())          # the engine's prefix rule (getPrefix: "<file>." = "server.")
    en.put("server.items.Probe_Own_Key_Thing.desc", "Own key text")
    langs.put("en-US", en)
    for fname, val in (("languages", langs), ("cachedLanguages", CHM()), ("messagesVersion", JLong(1)), ("fallbacks", JMap()),
                       ("bundledDefaults", JMap()), ("pendingLanguages", CHM())):
        E.jf(I18c.class_, fname).set(i18, val)
    E.jf(I18c.class_, "instance").set(None, i18)
    oak_base = str(en.get("server.items.Wood_Oak_Trunk.description"))
    K.check(oak_base.startswith("Refines into Hardwood"), "TIP STAND-IN: I18nModule holds the real Oak Log text under server.items.Wood_Oak_Trunk.description")
    K.eq(str(TIPS.base(P.pr, "server.items.Wood_Oak_Trunk.description")), oak_base, "TIP: base() reads the server's own text through I18nModule.getMessages(lang)")
    K.check(TIPS.base(P.pr, "server.items.No_Such_Item.description") is None, "TIP: base() of a key the server lacks = none")
    # Item asset-map stand-in: Oak (own Description key = the standard one), a Description-less item, an item whose JSON key differs
    ITc = JClass(PH + "server.core.asset.type.item.config.Item")
    ITPc = JClass(PH + "server.core.asset.type.item.config.ItemTranslationProperties")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    item_ok = False
    try:
        dam = DAMc()
        AScls = JClass("com.hypixel.hytale.assetstore.AssetStore")
        ast = Ucls.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore").class_)
        E.jf(AScls.class_, "assetMap").set(ast, dam)
        amap = E.jf(DAMc.class_, "assetMap").get(dam)

        def fake_item(iid, desc_key, ms):
            it_ = Ucls.allocateInstance(ITc.class_)
            E.jf(ITc.class_, "id").set(it_, iid)
            tp_ = Ucls.allocateInstance(ITPc.class_)
            if desc_key:
                E.jf(ITPc.class_, "description").set(tp_, desc_key)
            E.jf(ITc.class_, "translationProperties").set(it_, tp_)
            E.jf(ITc.class_, "maxStack").setInt(it_, ms)
            amap.put(iid, it_)
        fake_item("Wood_Oak_Trunk", "server.items.Wood_Oak_Trunk.description", 100)
        fake_item("Plant_Crop_Wheat_Item", None, 100)
        fake_item("Probe_Own_Key_Thing", "server.items.Probe_Own_Key_Thing.desc", 1)
        E.jf(ITc.class_, "ASSET_STORE").set(None, ast)
        item_ok = TIPS.item("Wood_Oak_Trunk") is not None
    except Exception as ex:
        K.notes.append("TIP: the Item asset-map stand-in failed (%s)" % str(ex)[:200])
    K.check(item_ok, "TIP STAND-IN: an Item asset map (Oak, Wheat, an item with its own description key)")
    K.eq(str(TIPS.keyOf("Wood_Oak_Trunk")), "server.items.Wood_Oak_Trunk.description", "TIP: keyOf(Oak) = its JSON Description key")
    K.eq(str(TIPS.keyOf("Plant_Crop_Wheat_Item")), "server.items.Plant_Crop_Wheat_Item.description", "TIP: keyOf(Wheat, no Description) = the engine fallback")
    K.eq(str(TIPS.keyOf("Probe_Own_Key_Thing")), "server.items.Probe_Own_Key_Thing.desc", "TIP: keyOf = the item's own key when it differs")
    K.eq(str(TIPS.keyOf("No_Such_Item")), "server.items.No_Such_Item.description", "TIP: keyOf(unknown) = the standard key")
    K.eq(str(TIPS.clean('  "Test 1"  ')), "Test 1", "TIP: clean drops the surrounding quotes (GREEDY_STRING keeps them)")
    K.eq(str(TIPS.clean("Line A\\nLine B")), "Line A\nLine B", "TIP: clean turns \\n into a new line")
    K.eq(str(TIPS.show("a\nb")), "a / b", "TIP: show() for chat")

    def utr(f0, PP=None):
        return [p for p in E.sent(PP or P)[f0:] if str(p.getClass().getSimpleName()) == "UpdateTranslations"]

    def utmap(p):
        m_ = p.translations
        return dict((str(k), str(m_.get(k))) for k in m_.keySet())
    E.run_world(E.W1)
    if REC.tasks is not None:
        REC.tasks.clear()
        REC.delays.clear()
    # P1: tip = one AddOrUpdate, caller only, the description key
    f0, s0 = len(E.sent(P)), int(TIPS.SENT)
    CMDS.tip3(P.pr, "tip", "Wood_Oak_Trunk", '"Test 1"')
    u = utr(f0)
    K.eq(len(u), 1, "TIP P1: exactly ONE UpdateTranslations packet")
    if u:
        K.eq(str(u[0].type), "AddOrUpdate", "TIP P1: UpdateType AddOrUpdate")
        K.eq(utmap(u[0]), {"server.items.Wood_Oak_Trunk.description": "Test 1"}, "TIP P1: the one key = 'Test 1' (quotes dropped)")
    K.eq(kinds(f0), ["UpdateTranslations"], "TIP P1: no other packet (chat aside)")
    K.check("TIP sent: server.items.Wood_Oak_Trunk.description = 'Test 1'" in chats(f0) and oak_base[:20] in chats(f0),
            "TIP P1: the chat line names the key, the new text and the server's own text")
    K.eq(int(TIPS.SENT) - s0, 1, "TIP P1: SENT counts it")
    # multi-line + reset
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "TIP", "Wood_Oak_Trunk", "Market\\nNPC Sell: 320 each")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": "Market\nNPC Sell: 320 each"}, "TIP: \\n = a real new line in the sent text")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Wood_Oak_Trunk", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": oak_base}, "TIP: reset sends the server's own text back")
    # P5: a Description-less item; an item whose own key differs = both keys in ONE packet; an unknown id = sent + a note
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Plant_Crop_Wheat_Item", "Wheat test")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Plant_Crop_Wheat_Item.description": "Wheat test"}, "TIP P5: Wheat (no Description) = the fallback key")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "X")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "X", "server.items.Probe_Own_Key_Thing.description": "X"},
            "TIP: an item whose key differs = its key + the standard key in the ONE packet")
    K.check("(+ server.items.Probe_Own_Key_Thing.description)" in chats(f0), "TIP: the chat names both keys")
    # fix (critic note 2): reset of an item whose own key differs = each key gets ITS OWN server text (not the own-key text twice)
    en.put("server.items.Probe_Own_Key_Thing.description", "Std key text")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "Own key text", "server.items.Probe_Own_Key_Thing.description": "Std key text"},
            "TIP FIX: reset with two keys = each key its own server text, in ONE packet")
    en.remove("server.items.Probe_Own_Key_Thing.description")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "Probe_Own_Key_Thing", "reset")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Probe_Own_Key_Thing.desc": "Own key text", "server.items.Probe_Own_Key_Thing.description": ""},
            "TIP FIX: reset with no server text for the standard key = '' there (never the own-key text)")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "No_Such_Item", "Y")
    K.check(len(utr(f0)) == 1 and "no item 'No_Such_Item' is loaded" in chats(f0), "TIP: an unknown id is still sent, with a check-the-id note")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "nope", "Wood_Oak_Trunk", "Z")
    K.check(len(utr(f0)) == 0 and "Usage: /uiprobe tip" in chats(f0), "TIP: an unknown word = usage, nothing sent")
    for w in ("tip", "tiplater"):
        f0 = len(E.sent(P))
        CMDS.arg(P.ref, P.st, P.pr, w)
        K.check(len(utr(f0)) == 0 and ("Usage: /uiprobe " + w) in chats(f0) and P.pm.getCustomPage() is None, "TIP: /uiprobe %s alone = usage" % w)
    # P2: tiplater = nothing now; ONE packet when the timer task runs - from the timer task itself, not via the world queue
    f0 = len(E.sent(P))
    n_tasks = 0 if REC.tasks is None else int(REC.tasks.size())
    CMDS.tip3(P.pr, "tiplater", "Wood_Oak_Trunk", "Test 2")
    K.eq(len(utr(f0)), 0, "TIP P2: tiplater sends nothing at once")
    K.check("Open your inventory NOW" in chats(f0), "TIP P2: the chat says to open the inventory")
    K.eq(int(REC.tasks.size()) - n_tasks, 1, "TIP P2: one timer task")
    K.eq(int(REC.delays.get(REC.delays.size() - 1)), 5000, "TIP P2: 5000 ms")
    t_ = REC.tasks.get(REC.tasks.size() - 1)
    REC.tasks.clear()
    REC.delays.clear()
    f1 = len(E.sent(P))
    t_.run()
    u = utr(f1)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.items.Wood_Oak_Trunk.description": "Test 2"}, "TIP P2: the timer task sends ONE packet (Test 2) without the world queue")
    K.check("TIP sent now (5 s later, from the timer thread)" in chats(f1), "TIP P2: the chat line after the delayed send")
    # P3: tipgear = ONE probe stack (claws + ItemDisplayMetadata with the translation child), counted, then the key packet
    IDMc = JClass(PH + "server.core.asset.type.item.config.metadata.ItemDisplayMetadata")

    def storage_list(PP):
        ic_ = PP.slots["storage"].getInventory()
        out_ = []
        for i in range(int(ic_.getCapacity())):
            s_ = ic_.getItemStack(JShort(i))
            if s_ is not None and not s_.isEmpty():
                out_.append(str(s_.getItemId()) + "x" + str(s_.getQuantity()))
        return out_
    st0 = storage_list(P)
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 0, "TIP P3: no claws before")
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "TipGear")
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 1, "TIP P3: ONE probe item given")
    found = None
    sic_ = P.slots["storage"].getInventory()
    for i in range(int(sic_.getCapacity())):
        s_ = sic_.getItemStack(JShort(i))
        if s_ is not None and not s_.isEmpty() and str(s_.getItemId()) == "Weapon_Claws_Tribal":
            found = s_
    K.check(found is not None, "TIP P3: the probe item went into STORAGE first")
    if found is not None:
        idm = found.getFromMetadataOrNull(IDMc.KEYED_CODEC)
        K.check(idm is not None, "TIP P3: the stack carries ItemDisplayMetadata")
        if idm is not None:
            K.check("Probe Claws" in str(idm.getName().getRawText()), "TIP P3: the display name")
            ch = [c_ for c_ in idm.getDescription().getChildren()]
            K.check(any(c_.getMessageId() is not None and str(c_.getMessageId()) == "server.skyy.probe.tip" for c_ in ch),
                    "TIP P3: the description has the translation child server.skyy.probe.tip")
            K.check(any(c_.getRawText() is not None and "PROBE item" in str(c_.getRawText()) for c_ in ch), "TIP P3: + the grey explanation lines")
    u = utr(f0)
    K.eq(len(u), 1, "TIP P3: ONE key packet after the item")
    if u:
        mm_ = utmap(u[0])
        K.check(list(mm_) == ["server.skyy.probe.tip"] and 'NPC Sell: <color is="#e8c25a"><b>320</b></color> each' in mm_["server.skyy.probe.tip"]
                and "probe line #1" in mm_["server.skyy.probe.tip"], "TIP P3: the key text (gold 320 + line #1): %s" % mm_)
    K.check("you got 'Probe Claws'" in chats(f0), "TIP P3: the chat line")
    K.eq(sorted(storage_list(P)), sorted(st0 + ["Weapon_Claws_Tribalx1"]), "TIP P3: nothing else in storage changed")
    f0 = len(E.sent(P))
    CMDS.tip3(P.pr, "tip", "gear", "Test 3")
    u = utr(f0)
    K.check(len(u) == 1 and utmap(u[0]) == {"server.skyy.probe.tip": "Test 3"}, "TIP P3: tip gear Test 3 = only the probe key")
    K.eq(E.count(P, "Weapon_Claws_Tribal"), 1, "TIP P3: tip gear gives no item")
    # P3 with a full inventory: FAIL line, no packet, nothing lost
    PF = E.player(uid=JClass("java.util.UUID")(9, 9), name="SkyyFull")
    ISc = JClass(PH + "server.core.inventory.ItemStack")
    for fld in ("storage", "hotbar"):
        ic_ = PF.slots[fld].getInventory()
        for i in range(int(ic_.getCapacity())):
            ic_.setItemStackForSlot(JShort(i), ISc("Wood_Oak_Trunk", 100))
    n_oak = E.count(PF, "Wood_Oak_Trunk")
    f0 = len(E.sent(PF))
    CMDS.arg(PF.ref, PF.st, PF.pr, "tipgear")
    K.check(len(utr(f0, PF)) == 0 and "TIP P3 FAIL - the probe item could not be given" in E.strs_of(PF, f0), "TIP P3: a full inventory = a FAIL line, no packet")
    K.check(E.count(PF, "Weapon_Claws_Tribal") == 0 and E.count(PF, "Wood_Oak_Trunk") == n_oak, "TIP P3: a full inventory loses nothing, gains nothing (%d oak)" % n_oak)
    # help names the tip probe
    f0 = len(E.sent(P))
    CMDS.arg(P.ref, P.st, P.pr, "help")
    K.check("PRICE TOOLTIP PROBE (P1-P5)" in chats(f0) and "/uiprobe tipgear" in chats(f0), "TIP: help lists the tip probe")
    K.notes.append("TIP: %d UpdateTranslations sent; last keys %s on thread %s" % (int(TIPS.SENT), str(TIPS.LASTKEYS), str(TIPS.LASTTHREAD)))
    # the engine's own parser: /skyprobe tip ... (3+ words) reaches the 3-arg variant; tipgear / tour the 1-arg one; 2 words = refused
    Tok = JClass("com.hypixel.hytale.server.core.command.system.Tokenizer")
    PCx = JClass("com.hypixel.hytale.server.core.command.system.ParserContext")
    PRs = JClass("com.hypixel.hytale.server.core.command.system.ParseResult")
    MSGS = []

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Snd(object):
        @JOverride
        def getUsername(self):
            return "Tester"

        @JOverride
        def getUuid(self):
            return JClass("java.util.UUID")(1, 2)

        @JOverride
        def sendMessage(self, m):
            MSGS.append(str(m.getMessageId() or m.getRawText()))

        @JOverride
        def hasPermission(self, q, *rest):
            return True

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    snd, own = Snd(), Owner()
    rootc = JV("SkyProbeCmd")()
    rootc.setOwner(own)
    try:
        rootc.completeRegistration()
    except Exception as ex:
        K.notes.append("completeRegistration: %s" % str(ex)[:100])

    def parse(line):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        if res.failed():
            return False, ["tokenizer"]
        ctx = PCx.of(toks, line, res)
        try:
            rootc.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:200])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    for line in ("skyprobe tip Wood_Oak_Trunk Test 1", 'skyprobe tip Wood_Oak_Trunk "Test 1"', "skyprobe tiplater Wood_Oak_Trunk Test 2",
                 "skyprobe tip gear Test 3", "skyprobe tipgear", "skyprobe tour", "skyprobe", "skyprobe inv", "skyprobe tab on",
                 "skyprobe tab off", "uiprobe tab on"):
        ok, ms = parse(line)
        K.check(ok and "server.commands.errors.playerOrArg" in ms, "TIP PARSER: /%s parses and reaches a player command (%s)" % (line, ms[:2]))
    for line in ("skyprobe tip Wood_Oak_Trunk", "skyprobe tip", "skyprobe tiplater Wood_Oak_Trunk", "skyprobe tour extra", "skyprobe tab",
                 "skyprobe tab on extra"):
        ok, ms = parse(line)
        K.check(not ok, "TIP PARSER CONTROL: /%s is refused (%s)" % (line, ms[:1]))
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
    subs = dict((str(k), v) for k, v in dict(root.getSubCommands()).items())
    K.eq(sorted(subs), ["tab", "tip", "tiplater"], "CMDS: the sub-commands tab + tip + tiplater")
    for nm_, tc_ in sorted(subs.items()):
        want_ = "SkyProbeTabCmd" if nm_ == "tab" else "SkyProbeTipCmd"
        K.check(str(tc_.getClass().getSimpleName()) == want_ and str(tc_.getName()) == nm_, "CMDS: /skyprobe %s = %s" % (nm_, want_))
        K.check(str(tc_.getPermission()) == "skyyuiprobe.admin", "CMDS: /skyprobe %s requires skyyuiprobe.admin" % nm_)
        pg2 = tc_.getPermissionGroups() if hasattr(tc_, "getPermissionGroups") else None
        K.check(pg2 is None or len(list(pg2)) == 0, "CMDS: /skyprobe %s has no permission groups" % nm_)

    # ================================================================= INV (0.10): the inventory probe P0, every new path executed
    from jpype import JArray as _JA
    INVST, INVPG, INVCM = JV("InvState"), JV("InvPage"), JV("InvCmds")
    ISc = JClass(PH + "server.core.inventory.ItemStack")
    MSGc = JClass(PH + "server.core.Message")
    COWc, CWc = JClass(PH + "protocol.packets.window.ClientOpenWindow"), JClass(PH + "protocol.packets.window.CloseWindow")
    WTc = JClass(PH + "protocol.packets.window.WindowType")
    DISc, SMISc, MISc = (JClass(PH + "protocol.packets.inventory.DropItemStack"), JClass(PH + "protocol.packets.inventory.SmartMoveItemStack"),
                         JClass(PH + "protocol.packets.inventory.MoveItemStack"))
    SMTc = JClass(PH + "protocol.SmartMoveType")
    UUIDc = JClass("java.util.UUID")
    TTc = JClass(PH + "server.core.util.thread.TickingThread")
    ARc = JClass("java.util.concurrent.atomic.AtomicReference")
    for w_ in (E.W1, E.W2):
        E.jf(TTc.class_, "currentRun").set(w_, ARc())
    for iid_, ms_ in (("Rock_Stone", 100), ("Weapon_Sword_Iron", 1), ("Plant_Fruit_Apple", 100)):
        fake_item(iid_, None, ms_)
    INVST.install()                                    # no ServerManager in this JVM: the adapter-only path; ACTIVE = true
    K.check(bool(INVST.ACTIVE) and INVST.FILTER is not None and not bool(INVST.INSTALLED), "INV: install() without a ServerManager = adapter filter only, active")
    K.check(any("no ServerManager here" in l for l in tail()), "INV: install() says the sub-packet handler is not there")

    def inv(PP, f):
        return PP.slots[f].getInventory()

    def put(PP, f, slot, stack):
        inv(PP, f).addItemStackToSlot(JShort(slot), stack)

    def at(PP, f, slot):
        s_ = inv(PP, f).getItemStack(JShort(slot))
        return None if s_ is None or s_.isEmpty() else (str(s_.getItemId()), int(s_.getQuantity()))

    def bag_of(pg_):
        out_ = {}
        for i_ in range(int(pg_.bag.getCapacity())):
            s_ = pg_.bag.getItemStack(JShort(i_))
            if s_ is not None and not s_.isEmpty():
                out_[i_] = (str(s_.getItemId()), int(s_.getQuantity()))
        return out_

    def tot(PP, iid, pg_=None):
        n_ = E.count(PP, iid)
        if pg_ is not None:
            n_ += sum(q for i_, q in bag_of(pg_).values() if i_ == iid)
        return n_
    IDS = ("Wood_Oak_Trunk", "Rock_Stone", "Weapon_Sword_Iron", "Plant_Fruit_Apple")

    def totals(PP, pg_=None):
        return dict((i_, tot(PP, i_, pg_)) for i_ in IDS)

    def sword():
        nm_ = MSGc.raw("Rolled Iron Sword").color("#ff5555")
        ds_ = MSGc.join(_JA(MSGc)([MSGc.raw("T3 Iron - Sword\n"), MSGc.raw("Damage +5").color("#7ee08a")]))
        return ISc("Weapon_Sword_Iron", 1).withMetadata(IDMc.KEYED_CODEC, IDMc(nm_, ds_))

    def ev(PP, obj):
        E.pump(PP)
        f_ = len(E.sent(PP))
        PP.pm.handleLegacyCustomPageEvent(PP.ref, PP.st, E.CPE(E.CPT.Data, json.dumps(obj)))
        return [p_ for p_ in E.sent(PP)[f_:] if str(p_.getClass().getSimpleName()) == "CustomPage"]

    def cmap(pk_):
        d_ = {}
        for c_ in cmds_of(pk_):
            d_[str(c_.selector)] = (str(c_.data) if c_.data is not None else "") + (str(c_.text) if c_.text is not None else "")
        return d_

    def binds_of(pk_):
        b_ = pk_.eventBindings if hasattr(pk_, "eventBindings") else None
        return [] if b_ is None else [(str(x.type), str(x.selector), str(x.data)) for x in b_]

    def mark():
        LOG.TAIL.clear()                               # the log keeps 400 lines: each check reads the lines since its own mark
        return 0

    def lines_since(n_):
        return tail()

    def pchats(PP, f_):
        return E.strs_of(PP, f_)

    def drag(PP, sg, ss, tg, ts, q=None, client=True, iid=None):
        """the client's two events: pick up (SlotClicking) + drop (Dropped on the target grid) - returns both packet lists"""
        a_ = ev(PP, {"a": "sc", "g": sg, "SlotIndex": ss})
        o_ = {"a": "dr", "g": tg, "SlotIndex": ts}
        if client:
            o_.update({"SourceInventorySectionId": {"s": -2, "h": -1, "a": -3, "u": -5}[sg], "SourceSlotId": ss})
            if iid:
                o_["ItemStackId"] = iid
            if q:
                o_["ItemStackQuantity"] = q
        b_ = ev(PP, o_)
        return a_, b_

    PI = E.player(uid=UUIDc(0x51, 0x51), name="SkyyInv")
    put(PI, "storage", 0, ISc("Wood_Oak_Trunk", 10))
    put(PI, "storage", 1, ISc("Wood_Oak_Trunk", 95))
    put(PI, "storage", 2, ISc("Rock_Stone", 5))
    put(PI, "storage", 5, sword())
    put(PI, "storage", 7, ISc("Plant_Fruit_Apple", 30))
    put(PI, "hotbar", 0, ISc("Plant_Fruit_Apple", 3))
    T0 = totals(PI)
    K.eq(T0, {"Wood_Oak_Trunk": 105, "Rock_Stone": 5, "Weapon_Sword_Iron": 1, "Plant_Fruit_Apple": 33}, "INV SETUP: the test inventory")
    # I4 straight on the slot copy: no metadata, the name + description from ItemDisplayMetadata, the real stack keeps its metadata
    IGSc = JClass(PH + "server.core.ui.ItemGridSlot")
    sl = INVPG.slot(inv(PI, "storage").getItemStack(JShort(5)))
    sst = E.jf(IGSc.class_, "itemStack").get(sl)
    K.check(sst is not None and sst.getMetadata() is None and str(sst.getItemId()) == "Weapon_Sword_Iron", "I4: the grid copy of the rolled sword carries NO metadata")
    K.eq(str(E.jf(IGSc.class_, "name").get(sl)), "Rolled Iron Sword", "I4: the slot name comes from ItemDisplayMetadata")
    K.check("T3 Iron - Sword" in str(E.jf(IGSc.class_, "description").get(sl)) and "Damage +5" in str(E.jf(IGSc.class_, "description").get(sl)),
            "I4: the slot description = the metadata description, children joined")
    K.check(inv(PI, "storage").getItemStack(JShort(5)).getMetadata() is not None, "I4: the REAL sword keeps its metadata (only the copy is stripped)")
    # 0.11 (Skyy crash 11-14 "Property QualityOverride does not exist on ClientItemStack"): a quality-stamped stack (SkyyAccessories withQuality)
    _qf = JClass(PH + "server.core.inventory.ItemStack").class_.getDeclaredField("qualityIndexOverride"); _qf.setAccessible(True)
    _qs = inv(PI, "storage").getItemStack(JShort(5)).withQuality(3)
    _qd = E.jf(IGSc.class_, "itemStack").get(INVPG.slot(_qs))
    _q0 = _qf.get(E.jf(IGSc.class_, "itemStack").get(INVPG.slot(inv(PI, "storage").getItemStack(JShort(0)))))
    K.check(int(_qf.get(_qs)) != int(_q0) and int(_qf.get(_qd)) == int(_q0) and _qd.getMetadata() is None and int(_qd.getQuantity()) == int(_qs.getQuantity()),
            "I4 0.11: a quality-stamped stack's grid copy has NO quality override (= a plain item), no metadata, same count")
    pl_ = INVPG.slot(inv(PI, "storage").getItemStack(JShort(0)))
    K.check(E.jf(IGSc.class_, "name").get(pl_) is None and bool(E.jf(IGSc.class_, "isActivatable").get(pl_)), "I4: a plain item gets no name override, slots are activatable")
    K.check(E.jf(IGSc.class_, "itemStack").get(INVPG.slot(None)) is None, "I4: an empty slot = an empty ItemGridSlot")
    K.eq(str(INVPG.flat(MSGc.join(_JA(MSGc)([MSGc.raw("a"), MSGc.translation("server.x.y"), MSGc.join(_JA(MSGc)([MSGc.raw("b")]))])))), "a[server.x.y]b",
         "I4: flat() joins children in order, a translation key shows as [key]")
    for js_, k_, want_ in (('{"a":"dr","SlotIndex":3,"g":"s"}', "SlotIndex", "3"), ('{"g": "b", "ShiftHeld" : true}', "ShiftHeld", "true"),
                           ('{"ItemStackId":"Wood_Oak_Trunk","DragItemStackId":"X"}', "ItemStackId", "Wood_Oak_Trunk"),
                           ('{"DragSourceSlotId":4,"SourceSlotId":7}', "SourceSlotId", "7"), ('{"SourceSlotId":null}', "SourceSlotId", None),
                           ('{"a":"x"}', "SlotIndex", None)):
        got_ = INVPG.val(js_, k_)
        K.eq(None if got_ is None else str(got_), want_, "INV: val(%s, %s)" % (js_, k_))
    K.eq(int(INVPG.ival('{"SlotIndex":2.0}', "SlotIndex", -1)), 2, "INV: ival reads 2.0 as 2")
    K.eq(int(INVPG.ival('{"SlotIndex":"x"}', "SlotIndex", -1)), -1, "INV: ival of junk = the default")

    # ---- I1: open
    f0, n0 = len(E.sent(PI)), mark()
    CMDS.arg(PI.ref, PI.st, PI.pr, "inv")
    pg = PI.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "InvPage", "I1: /uiprobe inv opens the InvPage")
    pk = [p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]
    K.eq(len(pk), 1, "I1: ONE CustomPage packet")
    cm = cmap(pk[0]) if pk else {}
    K.eq([json.loads(cm.get("#SkyyPrI%s.InventorySectionId" % g_, "{}")).get("0") for g_ in "shau"], [-2, -1, -3, -5], "I1: InventorySectionId -2 / -1 / -3 / -5 (the InventoryComponent ids)")
    K.check(all(("#SkyyPrI%s.Slots" % g_) in cm for g_ in "shau") and "#SkyyPrIb.Slots" not in cm and "#SkyyPrDz.Slots" in cm,
            "I1: the server sends every grid's Slots (+ the drop zone; no bag in the inventory view)")
    sd = cm.get("#SkyyPrIs.Slots", "")
    K.check("Wood_Oak_Trunk" in sd and "Rolled Iron Sword" in sd and "Damage +5" in sd and "ItemDisplay" not in sd,
            "I1 / I4: the storage Slots hold the real items; the sword's name + description travel, its metadata does not")
    K.check("Plant_Fruit_Apple" in cm.get("#SkyyPrIh.Slots", ""), "I1: the hotbar Slots hold the hotbar apples")
    bl = binds_of(pk[0]) if pk else []
    K.eq(len(bl), 25, "I1: 25 bindings (4 buttons + 4 grids x 5 slot events + the drop zone)")
    K.check(("SlotClicking", "#SkyyPrIs") in [(t_, s_) for t_, s_, _d in bl] and ("Dropped", "#SkyyPrDz") in [(t_, s_) for t_, s_, _d in bl]
            and not any("MouseEntered" in t_ or "MouseExited" in t_ for t_, _s, _d in bl), "I1: slot events bound, the drop zone bound, NO hover event")
    K.check(any('"g":"s"' in d_.replace(" ", "") and '"a":"dr"' in d_.replace(" ", "") for t_, s_, d_ in bl if s_ == "#SkyyPrIs"), "I1: the grid events carry {a, g}")
    K.check("INV page opened (/uiprobe inv)" in pchats(PI, f0), "I1: the opened line in chat")
    K.check(INVST.PAGES.get(PI.pr.getUuid()) == pg, "I1: the open page is known by uuid")

    def one(pks, what):
        K.eq(len(pks), 1, what + ": exactly ONE page packet")
        return pks[0] if pks else None

    def ok_line(n_, frag):
        return any(frag in l for l in lines_since(n_))
    # ---- moves
    n0 = mark()
    a_, b_ = drag(PI, "s", 0, "h", 1, q=10, iid="Wood_Oak_Trunk")
    p_ = one(a_, "MOVE pick up")
    if p_ is not None:
        K.eq(list(cmap(p_)), ["#SkyyPrTCap.Text"], "MOVE pick up: only the caption (the grids are untouched while the client holds the stack)")
    p_ = one(b_, "MOVE drag")
    K.eq((at(PI, "storage", 0), at(PI, "hotbar", 1)), (None, ("Wood_Oak_Trunk", 10)), "MOVE drag: s:0 -> h:1")
    if p_ is not None:
        K.check(not is_clear(p_) and all(("#SkyyPrI%s.Slots" % g_) in cmap(p_) for g_ in "shau"), "MOVE drag: ONE update re-sends the grids")
    K.check(ok_line(n0, "inv drag s:0 Wood_Oak_Trunk x10 -> h:1 ok"), "MOVE drag: the log line")
    n0 = mark()
    one(drag(PI, "h", 1, "s", 1, q=10, iid="Wood_Oak_Trunk")[1], "MOVE merge")
    K.eq((at(PI, "hotbar", 1), at(PI, "storage", 1)), (("Wood_Oak_Trunk", 5), ("Wood_Oak_Trunk", 100)), "MOVE merge: onto 95 -> 100, 5 stay")
    K.check(ok_line(n0, "inv merge h:1 Wood_Oak_Trunk x10 -> s:1 ok"), "MOVE merge: the log line")
    n0 = mark()
    one(drag(PI, "s", 2, "s", 1, q=5, iid="Rock_Stone")[1], "MOVE swap")
    K.eq((at(PI, "storage", 1), at(PI, "storage", 2)), (("Rock_Stone", 5), ("Wood_Oak_Trunk", 100)), "MOVE swap: rock <-> wood")
    K.check(ok_line(n0, "inv swap s:2 Rock_Stone x5 -> s:1 ok"), "MOVE swap: the log line")
    n0 = mark()
    one(drag(PI, "s", 1, "s", 10, q=2, iid="Rock_Stone")[1], "MOVE split")
    K.eq((at(PI, "storage", 1), at(PI, "storage", 10)), (("Rock_Stone", 3), ("Rock_Stone", 2)), "MOVE split (right-drag half): 2 of 5")
    K.check(ok_line(n0, "inv split s:1 Rock_Stone x2 -> s:10 ok"), "MOVE split: the log line")
    n0 = mark()
    one(drag(PI, "s", 10, "s", 2, q=1, iid="Rock_Stone")[1], "MOVE part onto another item")
    K.eq((at(PI, "storage", 10), at(PI, "storage", 2)), (("Rock_Stone", 2), ("Wood_Oak_Trunk", 100)), "MOVE part onto another item: refused, nothing moved")
    K.check(ok_line(n0, "inv swap s:10 Rock_Stone x1 -> s:2 fail (part of a stack cannot swap"), "MOVE part onto another item: the fail line")
    n0 = mark()
    one(drag(PI, "h", 0, "s", 20, client=False)[1], "MOVE tracked source")
    K.eq((at(PI, "hotbar", 0), at(PI, "storage", 20)), (None, ("Plant_Fruit_Apple", 3)), "MOVE without the client's source fields = the tracked pick-up")
    K.check(ok_line(n0, "inv drag h:0 Plant_Fruit_Apple x3 -> s:20 ok"), "MOVE tracked source: the log line")
    # a release on another slot = the drop (CORE); the Dropped of the same gesture moves nothing twice
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 20}), "MOVE release pick up")
    one(ev(PI, {"a": "rl", "g": "h", "SlotIndex": 2}), "MOVE release on another slot")
    one(ev(PI, {"a": "dr", "g": "h", "SlotIndex": 2, "SourceInventorySectionId": -2, "SourceSlotId": 20, "ItemStackId": "Plant_Fruit_Apple"}), "MOVE its Dropped")
    K.eq((at(PI, "storage", 20), at(PI, "hotbar", 2)), (None, ("Plant_Fruit_Apple", 3)), "MOVE release + Dropped = moved ONCE")
    K.check(ok_line(n0, "inv drag s:20 Plant_Fruit_Apple x3 -> h:2 ok") and ok_line(n0, "duplicate callback for s:20>h:2"), "MOVE release + Dropped: one move, the duplicate logged")
    # two drops of the same slot (outside the 1.5 s duplicate window): the second finds the slot empty
    n0 = mark()
    one(drag(PI, "h", 2, "h", 3, iid="Plant_Fruit_Apple")[1], "MOVE first click")
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dr", "g": "h", "SlotIndex": 3, "SourceInventorySectionId": -1, "SourceSlotId": 2, "ItemStackId": "Plant_Fruit_Apple"}), "MOVE second click")
    K.eq((at(PI, "hotbar", 2), at(PI, "hotbar", 3)), (None, ("Plant_Fruit_Apple", 3)), "MOVE two drops of one slot: moved once")
    K.check(ok_line(n0, "inv drag h:2 -> h:3 fail (the source slot is empty now"), "MOVE two drops: the second fails, nothing duplicated")
    K.eq(totals(PI), T0, "MOVE: every item total unchanged after the drags")
    # shift both ways
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 7, "ShiftHeld": True}), "SHIFT pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 7, "ShiftHeld": True}), "SHIFT release")
    K.check(at(PI, "storage", 7) is None and E.count(PI, "Plant_Fruit_Apple") == 33 and sum(at(PI, "hotbar", i_)[1] for i_ in range(9)
            if at(PI, "hotbar", i_) and at(PI, "hotbar", i_)[0] == "Plant_Fruit_Apple") == 33, "SHIFT storage -> hotbar: all 30 apples to the hotbar")
    K.check(ok_line(n0, "inv shift s:7 Plant_Fruit_Apple x30 -> h ok (30 of 30 moved)"), "SHIFT: the log line")
    hs_ = [i_ for i_ in range(9) if at(PI, "hotbar", i_) == ("Wood_Oak_Trunk", 5)][0]
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hs_}), "SHIFT2 pick up")
    one(ev(PI, {"a": "rl", "g": "h", "SlotIndex": hs_, "ShiftHeld": True}), "SHIFT2 release (shift pressed late)")
    K.check(at(PI, "hotbar", hs_) is None and ok_line(n0, "inv shift h:%d Wood_Oak_Trunk x5 -> s ok" % hs_), "SHIFT hotbar -> storage")
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2}), "PUTBACK pick up")
    p_ = one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 2}), "PUTBACK release on the same slot")
    K.check(p_ is not None and list(cmap(p_)) == ["#SkyyPrTCap.Text"], "PUTBACK: a caption only (no slot re-send while the client may still hold the stack)")
    K.eq(at(PI, "storage", 2), ("Wood_Oak_Trunk", 100), "PUTBACK: nothing moved")
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2}), "CANCEL pick up")
    one(ev(PI, {"a": "cx", "g": "s"}), "CANCEL")
    K.check(pg.dg is None and ok_line(n0, "inv cancel Wood_Oak_Trunk from storage slot 3 -> back ok"), "CANCEL: the drag is forgotten, logged")
    p_ = one(ev(PI, {"a": "dc", "g": "s", "SlotIndex": 2}), "DOUBLE-CLICK")
    K.check(p_ is not None and list(cmap(p_)) == ["#SkyyPrTCap.Text"], "DOUBLE-CLICK: a caption only")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 4}), "RELEASE with nothing held")
    one(ev(PI, {"a": "dr", "g": "s", "SlotIndex": 4}), "DROP with no source anywhere")
    K.check(ok_line(n0, "the event names no source and nothing was picked up"), "DROP with no source: nothing moved, logged")
    n0 = mark()
    one(ev(PI, {"a": "sort"}), "SORT")
    K.check(ok_line(n0, "inv sort storage -> storage ok") and totals(PI) == T0, "SORT: storage sorted, totals unchanged")
    one(ev(PI, {"a": "zz"}), "UNKNOWN event (the safety net / say)")
    K.eq(totals(PI), T0, "MOVES: every item total unchanged")
    # drag outside the window = drop (the probe's own path: this player's packet handler is not the game's)
    DROPS = []

    @JImplements("java.util.function.Function")
    class Dropper(object):
        def __init__(self, ok):
            self.ok = ok

        @JOverride
        def apply(self, s):
            DROPS.append((str(s.getItemId()), int(s.getQuantity())))
            return JClass("java.lang.Boolean")(self.ok)
    hap = [i_ for i_ in range(9) if at(PI, "hotbar", i_) and at(PI, "hotbar", i_)[0] == "Plant_Fruit_Apple"][0]
    INVST.DROPPER = Dropper(True)
    n0 = mark()
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hap}), "DROP OUT pick up")
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 2}), "DROP OUT")
    K.eq((DROPS, tot(PI, "Plant_Fruit_Apple")), ([("Plant_Fruit_Apple", 2)], 31), "DROP OUT: 2 apples dropped at the feet, 2 fewer in the inventory")
    K.check(ok_line(n0, "inv drop-outside h:%d Plant_Fruit_Apple x2 -> world ok (dropped at your feet)" % hap), "DROP OUT: the log line")
    INVST.DROPPER = Dropper(False)
    one(ev(PI, {"a": "sc", "g": "h", "SlotIndex": hap}), "DROP REFUSED pick up")
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}), "DROP REFUSED")
    K.check(tot(PI, "Plant_Fruit_Apple") == 31 and ok_line(n0, "(the drop failed - put back into hotbar)"), "DROP REFUSED: the stack goes back, nothing lost")
    INVST.DROPPER = None
    pg.lastMoveAt = 0
    one(ev(PI, {"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}), "DROP REAL CALL")
    K.check(tot(PI, "Plant_Fruit_Apple") in (30, 31), "DROP REAL CALL: ItemUtils.dropItem on the stand-in store (dropped or put back - never lost: %d)" % tot(PI, "Plant_Fruit_Apple"))
    T0 = totals(PI)
    # the game's own drop (CORE): the player's packet handler IS an IPacketHandler -> InventoryPacketHandler.handle(DropItemStack) queues the
    # game's world task (not run here: that is the engine's own drop)
    GPHc, GENc = JClass(PH + "server.core.io.handlers.game.GamePacketHandler"), JClass(PH + "server.core.io.handlers.GenericPacketHandler")
    INVPHc = JClass(PH + "server.core.io.handlers.game.InventoryPacketHandler")
    PHc = JClass(PH + "server.core.io.PacketHandler")
    # a GamePacketHandler that forwards its writes to the recording handler (the page / chat packets stay recorded)
    CPx = JClass("javassist.ClassPool").getDefault()
    CPx.appendClassPath(B.SERVER_JAR)
    rg_ = CPx.makeClass("uiprobeharness.RecGame", CPx.get(PH + "server.core.io.handlers.game.GamePacketHandler"))
    rg_.addField(JClass("javassist.CtField").make("public static " + PH + "server.core.io.PacketHandler D;", rg_))
    _pt = [str(x.getName()) for x in list(GPHc.class_.getDeclaredConstructors())[0].getParameterTypes()]
    rg_.addConstructor(JClass("javassist.CtNewConstructor").make("public RecGame() { super(%s); }" % ", ".join("(%s) null" % x for x in _pt), rg_))
    for _m in ("public boolean writePacket(" + PH + "protocol.ToClientPacket p, boolean c) { D.writePacket(p, c); return true; }",
               "public void write(" + PH + "protocol.ToClientPacket p) { D.write(p); }",
               "public void write(" + PH + "protocol.ToClientPacket[] ps) { D.write(ps); }",
               "public void write(" + PH + "protocol.ToClientPacket[] ps, " + PH + "protocol.ToClientPacket p) { D.write(ps, p); }",
               "public void writeNoCache(" + PH + "protocol.ToClientPacket p) { D.writeNoCache(p); }"):
        rg_.addMethod(JClass("javassist.CtNewMethod").make(_m, rg_))
    rg_.writeFile(hcls)
    RGc = JClass("uiprobeharness.RecGame")
    old_ph = PI.pr.getPacketHandler()
    RGc.D = old_ph
    G = Ucls.allocateInstance(RGc.class_)
    E.jf(GPHc.class_, "playerRef").set(G, PI.pr)
    E.run_world(E.W1)
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "packetHandler").set(PI.pr, G)
    n0 = mark()
    pg.lastMoveAt = 0
    pg.handleDataEvent(PI.ref, PI.st, json.dumps({"a": "dz", "SourceInventorySectionId": -1, "SourceSlotId": hap, "ItemStackId": "Plant_Fruit_Apple", "ItemStackQuantity": 1}))
    q_ = E.queued(E.W1)
    K.check(len(q_) == 2 and "InventoryPacketHandler" in q_[0] and q_[1] == "InvTask", "DROP NATIVE: handed to InventoryPacketHandler -> the game's world task queued, then our drop-check (%s)" % q_)
    K.check(ok_line(n0, "(handed to the game's own drop, like the Q key"), "DROP NATIVE: the log line")
    tk_ = list(E.W1.tasks)
    E.W1.tasks.clear()
    f1_ = int(pg.fails)
    n0 = mark()
    tk_[1].run()                                           # the game's task NOT run: nothing left the inventory
    K.check(ok_line(n0, "the game's own drop did NOT drop it (fail; no item lost)") and int(pg.fails) == f1_ + 1, "DROP CHECK: a drop the game did not do is logged as a fail")
    ck_ = JV("InvTask")(3, PI.pr, "h:%d" % hap)
    ck_.pg, ck_.sid, ck_.n0 = pg, "Plant_Fruit_Apple", tot(PI, "Plant_Fruit_Apple") + 1
    n0 = mark()
    ck_.run()
    K.check(ok_line(n0, "Plant_Fruit_Apple: 1 left your inventory - the game's drop ok"), "DROP CHECK: a drop the game did is logged ok")
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "packetHandler").set(PI.pr, old_ph)
    K.eq(totals(PI), T0, "DROP NATIVE: the probe itself took nothing")
    # native packets while the page is open: observed + left to the game; a drag right after a native move is skipped
    E.run_world(E.W1)
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, MISc(-2, 2, 1, -1, 6), "subhandler")) and not bool(INVST.route(PI.pr, DISc(-1, hap, 1), "adapter"))
            and not bool(INVST.route(PI.pr, SMISc(-2, 2, 1, SMTc.PutInHotbarOrWindow), "subhandler")), "NATIVE: Move / Drop / SmartMove are left to the game")
    K.check(ok_line(n0, "inv native MoveItemStack -2:2 -> -1:6 x1") and ok_line(n0, "inv native DropItemStack section -1") and ok_line(n0, "inv native SmartMoveItemStack"),
            "NATIVE: each one logged")
    K.check(INVST.LASTNATIVE.get(PI.pr.getUuid()) is not None, "NATIVE: the time of the last native move is kept")
    one(drag(PI, "s", 2, "s", 30, iid="Wood_Oak_Trunk")[1], "NATIVE then a drag")
    K.check(at(PI, "storage", 2) == ("Wood_Oak_Trunk", 100) and ok_line(n0, "(skipped: the client sent its own native move"), "NATIVE: a drag right after it is skipped (no double move)")
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": 2, "ShiftHeld": True}), "NATIVE then a shift pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": 2, "ShiftHeld": True}), "NATIVE then a shift release")
    K.check(at(PI, "storage", 2) == ("Wood_Oak_Trunk", 100) and ok_line(n0, "(skipped: the client sent its own native SmartMove"), "NATIVE: a shift-click right after a native SmartMove is skipped")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    # fixer 2: a native Move / SmartMove that arrives AFTER our server move (within 1.5 s) is logged as a possible undo + counted as a fail
    sv_ = totals(PI)
    pg.moved("s:1>s:5")
    f1_ = int(pg.fails)
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, MISc(-2, 1, 1, -2, 5), "subhandler")), "LATE NATIVE: still left to the game")
    K.check(ok_line(n0, "inv native MoveItemStack -2:1 -> -2:5 x1 AFTER a server move (s:1>s:5,") and ok_line(n0, "possible undo") and int(pg.fails) == f1_ + 1,
            "LATE NATIVE: a native Move right after a server move is WARNed as a possible undo and counted as a fail")
    pg.moved("s:1>world")
    n0 = mark()
    INVST.route(PI.pr, SMISc(-2, 2, 1, SMTc.PutInHotbarOrWindow), "subhandler")
    K.check(not ok_line(n0, "AFTER a server move") and int(pg.fails) == f1_ + 1, "LATE NATIVE: not after a drop-outside")
    pg.lastMoveAt = 0
    n0 = mark()
    INVST.route(PI.pr, MISc(-2, 1, 1, -2, 5), "subhandler")
    K.check(not ok_line(n0, "AFTER a server move") and int(pg.fails) == f1_ + 1 and totals(PI) == sv_, "LATE NATIVE: no warning with no recent server move; the probe moved nothing")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    # change events: ONE refresh when the items changed outside a click, none when nothing changed
    E.run_world(E.W1)
    E.pump(PI)
    f0 = len(E.sent(PI))
    E.run_world(E.W1)
    K.eq(len([p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]), 0, "REFRESH: our own moves queue no extra packet")
    inv(PI, "storage").addItemStack(ISc("Rock_Stone", 1))
    K.check("InvRefresh" in E.queued(E.W1), "REFRESH: a change event queues ONE refresh on the world thread (%s)" % E.queued(E.W1))
    inv(PI, "hotbar").addItemStack(ISc("Rock_Stone", 1))
    K.eq(E.queued(E.W1).count("InvRefresh"), 1, "REFRESH: a second change before it runs queues nothing more")
    n0 = mark()
    E.run_world(E.W1)
    rp = [p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]
    K.check(len(rp) == 1 and "#SkyyPrIs.Slots" in cmap(rp[0]) and ok_line(n0, "inv refresh: the items changed"), "REFRESH: ONE update re-sent the grids")
    pg.changed()
    E.run_world(E.W1)
    K.eq(len([p_ for p_ in E.sent(PI)[f0:] if str(p_.getClass().getSimpleName()) == "CustomPage"]), 1, "REFRESH: nothing changed = no packet")
    T0 = totals(PI)

    # ---- I3: the Probe Bag
    pk_ = one(ev(PI, {"a": "tbag"}), "BAG tab")
    if pk_ is not None:
        K.check(bool(is_clear(pk_)) and "#SkyyPrIb.Slots" in cmap(pk_) and len(binds_of(pk_)) == 30, "BAG tab: ONE rebuild with the bag grid (30 bindings)")
    K.eq(str(pg.view), "bag", "BAG: the bag view")
    one(ev(PI, {"a": "tbag"}), "BAG tab again (already open)")
    ws_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Wood_Oak_Trunk"][0]
    n0 = mark()
    one(drag(PI, "s", ws_, "b", 3, iid="Wood_Oak_Trunk")[1], "BAG drag in")
    K.check(bag_of(pg).get(3, (None,))[0] == "Wood_Oak_Trunk" and ok_line(n0, "-> b:3 ok"), "BAG: storage -> bag slot 4")
    rs_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Rock_Stone"][0]
    one(ev(PI, {"a": "sc", "g": "s", "SlotIndex": rs_, "ShiftHeld": True}), "BAG shift pick up")
    one(ev(PI, {"a": "rl", "g": "s", "SlotIndex": rs_, "ShiftHeld": True}), "BAG shift in")
    K.check(any(v_[0] == "Rock_Stone" for v_ in bag_of(pg).values()) and ok_line(n0, "inv shift s:%d Rock_Stone" % rs_), "BAG: shift-click storage -> bag")
    K.eq(totals(PI, pg), T0, "BAG: totals (inventory + bag) unchanged")
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": 3}), "BAG out pick up")
    one(ev(PI, {"a": "dr", "g": "s", "SlotIndex": 35}), "BAG out drop (no client source - the bag has no section)")
    K.check(at(PI, "storage", 35) is not None and at(PI, "storage", 35)[0] == "Wood_Oak_Trunk" and 3 not in bag_of(pg), "BAG: bag -> storage by the tracked pick-up")
    rb_ = [i_ for i_, v_ in bag_of(pg).items() if v_[0] == "Rock_Stone"][0]
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": rb_, "ShiftHeld": True}), "BAG shift out pick up")
    one(ev(PI, {"a": "rl", "g": "b", "SlotIndex": rb_, "ShiftHeld": True}), "BAG shift out")
    K.check(bag_of(pg) == {} and ok_line(n0, "inv shift b:%d Rock_Stone" % rb_), "BAG: shift-click bag -> storage / hotbar")
    K.eq(totals(PI, pg), T0, "BAG: totals unchanged after in / out")
    # drag from the bag onto the drop zone (the bag has no section: the probe's own drop)
    wz_ = [i_ for i_ in range(36) if at(PI, "storage", i_) and at(PI, "storage", i_)[0] == "Wood_Oak_Trunk"][0]
    one(drag(PI, "s", wz_, "b", 0, iid="Wood_Oak_Trunk")[1], "BAG in again")
    K.check(bag_of(pg).get(0, (None,))[0] == "Wood_Oak_Trunk", "BAG: wood in bag slot 1 again")
    INVST.DROPPER = Dropper(True)
    del DROPS[:]
    one(ev(PI, {"a": "sc", "g": "b", "SlotIndex": 0}), "BAG drop-out pick up")
    one(ev(PI, {"a": "dz", "ItemStackQuantity": 4}), "BAG drop-out")
    K.check(DROPS == [("Wood_Oak_Trunk", 4)] and tot(PI, "Wood_Oak_Trunk", pg) == T0["Wood_Oak_Trunk"] - 4, "BAG: 4 dragged out of the bag = dropped at the feet")
    T0 = totals(PI, pg)
    # every close path returns the bag
    def fill_bag(pg_, PP, n_):
        """n_ stacks into the bag the way the player does it (drag from storage)"""
        moved_ = 0
        for i_ in range(36):
            if moved_ >= n_:
                break
            s_ = at(PP, "storage", i_)
            if s_ is None:
                continue
            pg_.lastMoveAt = 0
            drag(PP, "s", i_, "b", 10 + moved_, iid=s_[0])
            moved_ += 1
        return dict(bag_of(pg_))
    before_ = totals(PI, pg)
    pre_ = len(bag_of(pg))                             # the rest of the wood stack dragged out above is still in the bag
    filled = fill_bag(pg, PI, 3)
    NB = pre_ + 3
    K.eq(len(filled), NB, "BAG: %d stacks in the bag before Esc" % NB)
    n0, f0 = mark(), len(E.sent(PI))
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(PI.pm.getCustomPage() is None and bool(pg.closed) and bag_of(pg) == {}, "CLOSE Esc: the page is gone, the bag is empty")
    K.eq(totals(PI), before_, "CLOSE Esc: every bag item is back in the inventory (totals equal)")
    K.eq(sum(1 for l in lines_since(n0) if l.startswith("I inv bag-return b:") and "(page closed)" in l), NB, "CLOSE Esc: one bag-return line per stack")
    K.check(("Probe Bag: %d stack(s) went back to your inventory (page closed)." % NB) in pchats(PI, f0), "CLOSE Esc: the chat line")
    K.check(INVST.PAGES.get(PI.pr.getUuid()) is None and pg.regs.isEmpty(), "CLOSE Esc: the page is forgotten, its listeners unregistered")
    n0, f0 = mark(), len(E.sent(PI))
    pg.handleDataEvent(PI.ref, PI.st, json.dumps({"a": "dr", "g": "b", "SlotIndex": 0, "SourceInventorySectionId": -2, "SourceSlotId": 2}))
    K.check(len(E.sent(PI)) == f0 and ok_line(n0, "arrived after the page closed - ignored") and totals(PI) == before_, "AFTER CLOSE: a late click sends nothing, moves nothing")
    # probe off with the page open
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    f0 = len(E.sent(PI))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "off")
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and PI.pm.getCustomPage() is None, "CLOSE probe off: the page closes, the bag comes back")
    K.check("TAB OFF" in pchats(PI, f0) and not INVST.TAB.containsKey(PI.pr.getUuid()), "CLOSE probe off: Tab is vanilla again")
    # disconnect (queued on the world) + disconnect with no world reference (kept, given back at the next open)
    PDEc, PREc = JClass(PH + "server.core.event.events.player.PlayerDisconnectEvent"), JClass(PH + "server.core.event.events.player.PlayerReadyEvent")
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    K.check(not INVST.TAB.containsKey(PI.pr.getUuid()) and E.queued(E.W1) == ["InvClose"], "CLOSE disconnect: Tab switched off, the bag return queued on the world")
    K.check(ok_line(n0, "inv bag-hold (disconnect) for") and ok_line(n0, "b:10 ") and ok_line(n0, "b:11 "), "CLOSE disconnect: the bag contents are logged before the queued return")
    n0 = mark()
    E.run_world(E.W1)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "force-closed (disconnect)"), "CLOSE disconnect: the bag comes back")
    # fixer 2 (safety re-check #1): the engine's own removal task is queued AFTER the disconnect event (Universe.removePlayer: dispatch
    # PlayerDisconnectEvent, THEN CompletableFuture.runAsync(remove, world)); the world queue is FIFO - our bag return runs first
    _pool = JClass("javassist.ClassPool")(False)
    _pool.insertClassPath(B.SERVER_JAR)
    _IPc, _PSc, _BOSc = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    def _code(cls_, m_):
        for mm_ in _pool.get(cls_).getDeclaredMethods():
            if str(mm_.getName()) == m_:
                b_ = _BOSc()
                _IPc(_PSc(b_)).print_(mm_)
                return str(b_.toString())
        return ""
    def _order(src_, *needles_):
        at_ = [src_.find(nd_) for nd_ in needles_]
        return all(a_ >= 0 for a_ in at_) and at_ == sorted(at_)
    _rp = _code(PH + "server.core.universe.Universe", "removePlayer")
    K.check(_order(_rp, "PlayerDisconnectEvent.<init>", "IEventDispatcher.dispatch", "World.isInThread", "CompletableFuture.runAsync"),
            "ENGINE ORDER: Universe.removePlayer dispatches PlayerDisconnectEvent BEFORE it queues the player's removal on the world")
    _wx = _code(PH + "server.core.universe.world.World", "execute")
    _wq = _code(PH + "server.core.universe.world.World", "consumeTaskQueue")
    K.check("World.acceptingTasks" in _wx and "Deque.offer" in _wx and "Deque.poll" in _wq, "ENGINE ORDER: World.execute offers to the tail, consumeTaskQueue polls the head (FIFO)")
    _ws = _code(PH + "server.core.universe.world.World", "onShutdown")
    K.check(_order(_ws, "World.consumeTaskQueue", "PlayerRef.removeFromStore"), "ENGINE ORDER: World.onShutdown runs the queued tasks BEFORE it removes the players")
    @JImplements("java.lang.Runnable")
    class EngineRemove(object):
        @JOverride
        def run(self):
            E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(PI.pr, None)
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    K.check(E.queued(E.W1) == ["InvClose"], "DISCONNECT ORDER: our bag return is queued during the event, ahead of the engine's removal")
    E.W1.tasks.add(EngineRemove())                             # what Universe.removePlayer queues right after the event
    E.run_world(E.W1)
    E.jf(JClass(PH + "server.core.universe.PlayerRef").class_, "entity").set(PI.pr, PI.ref)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and INVST.PENDING.get(PI.pr.getUuid()) is None
            and ok_line(n0, "inv bag-return b:10") and not ok_line(n0, "kept in memory"),
            "DISCONNECT ORDER: the bag is back in the inventory before the engine removes (and saves) the player - nothing left in memory")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    E.run_world(E.W1)
    RUNc = JClass(PH + "server.core.util.thread.TickingThread$Run")
    run_ = Ucls.allocateInstance(RUNc.class_)
    E.jf(RUNc.class_, "thread").set(run_, JClass("java.lang.Thread").currentThread())
    E.jf(TTc.class_, "currentRun").get(E.W1).set(run_)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    E.jf(TTc.class_, "currentRun").get(E.W1).set(None)
    K.check(E.queued(E.W1) == [] and bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "force-closed (disconnect)"),
            "CLOSE disconnect on the world thread: the bag comes back at once, nothing queued")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    PRc = JClass(PH + "server.core.universe.PlayerRef")
    E.jf(PRc.class_, "entity").set(PI.pr, None)
    n0 = mark()
    JV("InvBye")().accept(PDEc(PI.pr))
    E.jf(PRc.class_, "entity").set(PI.pr, PI.ref)
    K.check(bag_of(pg) == {} and INVST.PENDING.get(PI.pr.getUuid()) is not None and int(INVST.PENDING.get(PI.pr.getUuid()).size()) == 2
            and ok_line(n0, "kept in memory for your next join"), "CLOSE disconnect without a world: the 2 stacks are kept in memory")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    K.check(INVST.PENDING.get(PI.pr.getUuid()) is None and totals(PI) == before_, "KEPT: given back when the page opens again (totals equal)")
    # world change: the old world's page hands its bag to the new world's inventory
    ev(PI, {"a": "tbag"})
    fill_bag(pg, PI, 2)
    old_tot = totals(PI, pg)
    PW = E.player(uid=PI.pr.getUuid(), name="SkyyInv", world=E.W2, world_u=E.W2U)
    n0 = mark()
    JV("InvReady")().accept(PREc(PW.ref, PW.pl, 0))
    K.check(bool(pg.closed) and bag_of(pg) == {} and INVST.PAGES.get(PI.pr.getUuid()) is None, "CLOSE world change: the old page closes, its bag empties")
    K.eq(sum(totals(PW).values()) + sum(totals(PI).values()), sum(old_tot.values()), "CLOSE world change: the bag items are in the NEW world's inventory (nothing lost, nothing doubled)")
    K.check(sum(totals(PW).values()) > 0 and ok_line(n0, "(world change)") and ok_line(n0, "kept items delivered"), "CLOSE world change: logged")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    # a full inventory: overflow at the feet; if the drop is refused, kept in memory and given back at the next ready
    PF2 = E.player(uid=UUIDc(0x52, 0x52), name="SkyyFull")
    put(PF2, "storage", 0, ISc("Plant_Fruit_Apple", 50))
    pgf = INVCM.openInv(PF2.ref, PF2.st, PF2.pr, "test")
    E.pump(PF2)
    ev(PF2, {"a": "tbag"})
    drag(PF2, "s", 0, "b", 0, iid="Plant_Fruit_Apple")
    for f_ in ("storage", "hotbar"):
        ic_ = inv(PF2, f_)
        for i_ in range(int(ic_.getCapacity())):
            ic_.addItemStackToSlot(JShort(i_), ISc("Rock_Stone", 100))
    rocks = E.count(PF2, "Rock_Stone")
    INVST.DROPPER = Dropper(True)
    del DROPS[:]
    PF2.pm.handleLegacyCustomPageEvent(PF2.ref, PF2.st, E.CPE(E.CPT.Dismiss, None))
    K.check(DROPS == [("Plant_Fruit_Apple", 50)] and bag_of(pgf) == {} and E.count(PF2, "Rock_Stone") == rocks, "FULL: the bag stack goes to the feet (inventory full)")
    pgf = INVCM.openInv(PF2.ref, PF2.st, PF2.pr, "test")
    E.pump(PF2)
    ev(PF2, {"a": "tbag"})
    pgf.bag.addItemStack(ISc("Plant_Fruit_Apple", 7))      # (a stack already in the bag - the full inventory leaves no slot to drag from)
    INVST.DROPPER = Dropper(False)
    PF2.pm.handleLegacyCustomPageEvent(PF2.ref, PF2.st, E.CPE(E.CPT.Dismiss, None))
    kept = INVST.PENDING.get(PF2.pr.getUuid())
    K.check(kept is not None and int(kept.size()) == 1 and bag_of(pgf) == {}, "FULL + drop refused: KEPT in memory, not lost")
    inv(PF2, "storage").removeItemStackFromSlot(JShort(4))
    n0 = mark()
    JV("InvReady")().accept(PREc(PF2.ref, PF2.pl, 0))
    K.check(INVST.PENDING.get(PF2.pr.getUuid()) is None and E.count(PF2, "Plant_Fruit_Apple") == 7 and ok_line(n0, "kept items delivered"), "FULL: given back at the next ready, into the freed slot")
    INVST.DROPPER = None
    # shutdown with the page open: the bag return is queued; leftovers in memory are named in the log
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    INVST.pend(UUIDc(9, 9), ISc("Rock_Stone", 3))
    E.run_world(E.W1)
    n0 = mark()
    INVST.shutdown()
    K.check(not bool(INVST.ACTIVE) and INVST.FILTER is None and E.queued(E.W1) == ["InvClose"], "SHUTDOWN: inactive, the adapter filter removed, the bag return queued")
    K.check(ok_line(n0, "inv bag-hold (server stopping) for"), "SHUTDOWN: the bag contents are named before the queued return (a loss would show)")
    K.check(ok_line(n0, "NOT RETURNED (the server stopped; the probe keeps no data) for player 00000000-0000-0009-0000-000000000009: Rock_Stone x3"), "SHUTDOWN: memory-only leftovers are named in the log")
    E.run_world(E.W1)
    K.check(bool(pg.closed) and bag_of(pg) == {} and totals(PI) == before_ and PI.pm.getCustomPage() is None, "SHUTDOWN: the bag comes back, the page closes")
    K.check(not bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")), "SHUTDOWN: the hooks pass every packet through")
    INVST.PENDING.clear()
    INVST.install()
    SPx = JClass("java.lang.System").getProperties()
    br_ = SPx.get("skyy.bridge")
    made_ = br_ is None
    if made_:
        br_ = JClass("java.util.concurrent.ConcurrentHashMap")()
        SPx.put("skyy.bridge", br_)
    ek_ = "profile:epoch:" + str(PI.pr.getUuid())
    br_.put(ek_, JClass("java.lang.Long").valueOf(3))
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    before_ = totals(PI, pg)
    fill_bag(pg, PI, 2)
    br_.put(ek_, JClass("java.lang.Long").valueOf(4))
    n0 = mark()
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(str(pg.epoch0) == "3" and bag_of(pg) == {} and totals(PI) == before_ and ok_line(n0, "profile changed (epoch 3 -> 4)"),
            "PROFILE: a profile switch with items in the bag is WARNed and the items still come back (nothing lost)")
    pg = INVCM.openInv(PI.ref, PI.st, PI.pr, "test")
    E.pump(PI)
    ev(PI, {"a": "tbag"})
    fill_bag(pg, PI, 1)
    n0 = mark()
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    K.check(str(pg.epoch0) == "4" and not ok_line(n0, "profile changed"), "PROFILE: same epoch = no warning")
    br_.remove(ek_)
    if made_:
        SPx.remove("skyy.bridge")

    # ---- I2: Tab routing
    E.run_world(E.W1)
    K.check(not bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")) and E.queued(E.W1) == [], "TAB off: PocketCrafting is left to the game")
    f0 = len(E.sent(PI))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "on")
    K.check(INVST.TAB.containsKey(PI.pr.getUuid()) and "TAB ON for you only" in pchats(PI, f0) and "NOT hooked" in pchats(PI, f0), "TAB on: switched on for this player (memory)")
    K.check(not bool(INVST.on(UUIDc(5, 5))), "TAB on: only for the op who switched it on")
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "maybe")
    K.check("Usage: /uiprobe tab on" in pchats(PI, f0), "TAB: a wrong word = usage")
    s0, n0 = int(INVST.SUB), mark()
    K.check(bool(INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")), "TAB: PocketCrafting taken by the subhandler")
    K.check(E.queued(E.W1) == ["InvTask"] and int(INVST.SUB) == s0 + 1 and INVST.REDIR.containsKey(PI.pr.getUuid()), "TAB: the redirect is queued on the world thread")
    E.run_world(E.W1)
    pg = PI.pm.getCustomPage()
    K.check(pg is not None and str(pg.getClass().getSimpleName()) == "InvPage" and "caught by subhandler" in str(pg.via), "TAB: the probe page opened from the Tab key")
    K.check(ok_line(n0, "Tab (ClientOpenWindow PocketCrafting) caught by subhandler"), "TAB: the log names the hook")
    E.pump(PI)
    o0 = int(INVST.ORPH)
    K.check(bool(INVST.route(PI.pr, CWc(0), "subhandler")) and int(INVST.ORPH) == o0 + 1, "TAB: the orphan CloseWindow 0 is absorbed")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() == pg and not bool(pg.closed), "TAB: ... and the probe page stays open")
    K.check(not bool(INVST.route(PI.pr, CWc(5), "subhandler")) and not bool(INVST.route(PI.pr, COWc(WTc.Container), "subhandler")), "TAB: other windows are left to the game")
    K.check(ok_line(n0, "ClientOpenWindow Container caught by subhandler - not the inventory key"), "TAB: the other window logged")
    INVST.route(PI.pr, COWc(WTc.PocketCrafting), "subhandler")
    n0 = mark()
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is None and bool(pg.closed) and ok_line(n0, "Tab pressed with the probe page open"), "TAB again: the page closes")
    K.check(bool(INVST.route(PI.pr, CWc(0), "subhandler")), "TAB: within 5 s of the redirect a CloseWindow 0 is still absorbed (the page just closed)")
    E.run_world(E.W1)
    INVST.REDIR.put(PI.pr.getUuid(), JClass("java.lang.Long").valueOf(0))
    n0 = mark()
    K.check(not bool(INVST.route(PI.pr, CWc(0), "subhandler")) and not INVST.REDIR.containsKey(PI.pr.getUuid()) and E.queued(E.W1) == []
            and ok_line(n0, "5 s after the redirect - left to the game"), "TAB: a CloseWindow 0 long after the redirect, no page open = the game's (REDIR cleared)")
    # the adapter (a connection the hook missed) - never both
    FL = JV("InvFilter")()
    a0, n0 = int(INVST.ADP), mark()
    K.check(bool(FL.test(PI.pr, COWc(WTc.PocketCrafting))) and int(INVST.ADP) == a0 + 1, "TAB adapter: an unhooked connection is caught by the adapter")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is not None and ok_line(n0, "caught by adapter"), "TAB adapter: the page opens, logged")
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    INVST.hooked(PI.pr.getPacketHandler())
    K.check(not bool(FL.test(PI.pr, COWc(WTc.PocketCrafting))) and int(INVST.ADP) == a0 + 1 and E.queued(E.W1) == [], "TAB adapter: a hooked connection is NOT routed twice")
    K.check(not bool(FL.test(PI.pr, DISc(-1, 0, 1))), "TAB adapter: inventory packets with no page = left to the game")
    INVST.HOOKED.remove(PI.pr.getPacketHandler())
    # the sub-packet hooks on a GamePacketHandler stand-in (the game's own consumers for ClientOpenWindow / CloseWindow are wrapped)
    REC_N = {"cow": 0, "cw": 0, "mv": 0}

    @JImplements("java.util.function.Consumer")
    class Native(object):
        def __init__(self, k):
            self.k = k

        @JOverride
        def accept(self, p):
            REC_N[self.k] += 1
    G = Ucls.allocateInstance(RGc.class_)
    CONS = JClass("java.util.function.Consumer")
    arr = _JA(CONS)(int(PHc.MAX_PACKET_ID) + 1)
    arr[int(COWc.PACKET_ID)] = Native("cow")
    arr[int(CWc.PACKET_ID)] = Native("cw")
    E.jf(GENc.class_, "handlers").set(G, arr)
    E.jf(GENc.class_, "packetHandlers").set(G, E.ArrayList())
    E.jf(GPHc.class_, "playerRef").set(G, PI.pr)
    IH = INVPHc(G)
    G.registerSubPacketHandler(IH)
    IH.registerHandlers()                                  # the game's own Drop / SmartMove / Move consumers in the table
    arr[int(COWc.PACKET_ID)] = Native("cow")
    arr[int(CWc.PACKET_ID)] = Native("cw")
    K.check(arr[int(DISc.PACKET_ID)] is not None and arr[int(SMISc.PACKET_ID)] is not None, "HOOKS: the game's inventory consumers are in the stand-in's table")
    arr[int(MISc.PACKET_ID)] = Native("mv")                # another mod's wrapper already on Move: ours must chain to it, not cut it off
    i0, n0 = int(INVST.INSTALLS), mark()
    hk = JV("InvHookFactory")().apply(G)
    K.check(str(hk.getClass().getSimpleName()) == "InvHooks", "HOOKS: the factory makes one InvHooks per connection")
    hk.registerHandlers()
    arr2 = E.jf(GENc.class_, "handlers").get(G)
    K.check(all(str(arr2[int(c_.PACKET_ID)].getClass().getSimpleName()) == "InvWrap" for c_ in (COWc, CWc, DISc, SMISc, MISc)),
            "HOOKS: ClientOpenWindow / CloseWindow / Drop / SmartMove / Move are wrapped")
    K.check(bool(INVST.isHooked(G)) and int(INVST.INSTALLS) == i0 + 1 and ok_line(n0, "inv hooks: 5 packet handlers wrapped on a new connection"), "HOOKS: the connection is marked hooked, logged")
    E.run_world(E.W1)
    arr2[int(COWc.PACKET_ID)].accept(COWc(WTc.PocketCrafting))
    K.check(REC_N["cow"] == 0 and E.queued(E.W1) == ["InvTask"], "HOOKS tab on: Tab is taken, the game's own handler NOT called")
    E.run_world(E.W1)
    K.check(PI.pm.getCustomPage() is not None, "HOOKS: the probe page opened through the wrapped handler")
    E.pump(PI)
    arr2[int(CWc.PACKET_ID)].accept(CWc(0))
    arr2[int(CWc.PACKET_ID)].accept(CWc(3))
    K.check(REC_N["cw"] == 1, "HOOKS: CloseWindow 0 absorbed, CloseWindow 3 goes to the game")
    E.run_world(E.W1)
    n0 = mark()
    arr2[int(DISc.PACKET_ID)].accept(DISc(-2, 0, 1))
    q_ = E.queued(E.W1)
    K.check(len(q_) == 1 and "InventoryPacketHandler" in q_[0] and ok_line(n0, "inv native DropItemStack section -2 slot 0 x1 while the probe page is open (subhandler)"),
            "HOOKS: a Drop is observed, then handed to InventoryPacketHandler (%s)" % q_)
    E.W1.tasks.clear()
    arr2[int(SMISc.PACKET_ID)].accept(SMISc(-2, 0, 1, SMTc.PutInHotbarOrWindow))
    K.check(len(E.queued(E.W1)) == 1, "HOOKS: SmartMoveItemStack handed to the game's own consumer (InventoryPacketHandler)")
    E.W1.tasks.clear()
    arr2[int(MISc.PACKET_ID)].accept(MISc(-2, 0, 1, -1, 0))
    K.check(REC_N["mv"] == 1 and E.queued(E.W1) == [], "HOOKS: Move goes to the consumer that was there before (another mod's wrapper is kept)")
    INVST.LASTNATIVE.remove(PI.pr.getUuid())
    PI.pm.handleLegacyCustomPageEvent(PI.ref, PI.st, E.CPE(E.CPT.Dismiss, None))
    INVCM.tabCmd(PI.ref, PI.st, PI.pr, "off")
    arr2[int(COWc.PACKET_ID)].accept(COWc(WTc.PocketCrafting))
    K.check(REC_N["cow"] == 1 and E.queued(E.W1) == [], "HOOKS tab off: Tab goes to the game's own handler")
    E.jf(GPHc.class_, "playerRef").set(G, None)
    arr2[int(CWc.PACKET_ID)].accept(CWc(0))
    K.check(REC_N["cw"] == 2, "HOOKS: no player ref = the game's own handler")
    G2 = Ucls.allocateInstance(GPHc.class_)
    E.jf(GENc.class_, "handlers").set(G2, _JA(CONS)(int(PHc.MAX_PACKET_ID) + 1))
    E.jf(GENc.class_, "packetHandlers").set(G2, E.ArrayList())
    n0 = mark()
    JV("InvHooks")(G2).registerHandlers()
    K.check(not bool(INVST.isHooked(G2)) and ok_line(n0, "inv hooks: 0 packet handlers wrapped on a new connection - the Tab hook is MISSING"), "HOOKS: a connection without the natives is not marked hooked (the adapter covers it)")
    JV("InvHookFactory")().apply(MSGc.raw("not a handler")).registerHandlers()
    K.check(True, "HOOKS: a non-game handler = an InvHooks that does nothing")
    K.notes.append("INV: moves %d, fails %d; SUB %d ADP %d ORPH %d NATIVE %d INSTALLS %d; dropped %s" % (
        int(pg.moves), int(pg.fails), int(INVST.SUB), int(INVST.ADP), int(INVST.ORPH), int(INVST.NATIVE), int(INVST.INSTALLS), list(INVST.DROPPED)[:6]))
    K.notes.append("X: %d log lines; asset sends %d" % (len(tail()), int(RTP.SENT)))
    K.save()


def run_cmp(out):
    """C: HK.run_compare (byte code of every class vs the 0.9 jar) - its non-class rule allows manifest.json only; here: the 14 case pages
    differ by exactly ONE line each (the title 'SkyyUiProbe 0.9 - ...' -> '0.10 - ...'), and the jar ADDS the two inventory page data files
    + the drop zone's transparent picture. Checked here, line by line, then that one expected FAIL is cleared."""
    HK.run_compare(out, JAR, OLD_JAR, PKG, CMP_EXPECT, CMP_ADDED)
    d = json.load(open(out))
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    na = [n for n in za.namelist() if not n.endswith(".class")]
    nb = [n for n in zb.namelist() if not n.endswith(".class")]
    ch = sorted(n for n in set(na) | set(nb) if n not in na or n not in nb or za.read(n) != zb.read(n))
    added = sorted(n for n in ch if n not in na)
    pages = [n for n in ch if n != "manifest.json" and n in na]
    good = ("manifest.json" in ch and len(pages) == 14 and all(n.startswith("com/skyy/uiprobe/pages/") and n in nb for n in pages)
            and added == ["Common/UI/Custom/SkyyUiProbe/Inv/Clear@2x.png", "com/skyy/uiprobe/pages/inv.txt", "com/skyy/uiprobe/pages/invbag.txt"]
            and not [n for n in na if n not in nb])
    for n in pages if good else []:
        a_, b_ = za.read(n).decode("utf-8").split("\n"), zb.read(n).decode("utf-8").split("\n")
        dl = [(x, y) for x, y in zip(a_, b_) if x != y]
        good = good and len(a_) == len(b_) and dl == [("S\t#SkyyPrTitle.Text\tSkyyUiProbe 0.9 - UI queue probe", "S\t#SkyyPrTitle.Text\tSkyyUiProbe 0.11 - UI queue probe")]
    fl = [f for f in d["fails"] if f.startswith("C: non-class entries changed")]
    if good and len(fl) == 1:
        d["fails"].remove(fl[0])
        d["ok"] += 1
        d["notes"].append("C: non-class entries: manifest.json + the 14 case pages (ONLY their title line 0.9 -> 0.11) + added %s" % added)
    else:
        d["fails"].append("C: the non-class entries differ from the expected (changed %s, added %s)" % (pages[:4], added))
    json.dump(d, open(out, "w"), indent=1)


WORLD = "NewBetaTest"          # tools/deploy_set.py WORLD (read only; copied into scratch)


def run_live(out):
    """LIVE: the live world's config.json (+ any Skyy_SkyyUiProbe* data folder - none exist: the probe keeps nothing) COPIED into scratch;
    setup() twice on fresh plugin objects (PluginBase fields: logger, dataDirectory inside the copy, a capturing CommandRegistry);
    each start = the '[SkyyUiProbe] 0.9 ready' line + ONE /skyprobe root (alias uiprobe, the 1-word variant, the tip / tiplater
    sub-commands); shutdown() between; the copy is byte + time identical after both starts and no data folder appears.
    0.10: + a capturing EventRegistry (the disconnect + ready listeners registered each start), a ServerManager stand-in (the sub-packet
    handler factory registered ONCE per server run), the PacketAdapters inbound list (our filter added at setup, removed at shutdown)."""
    import time
    from jpype import JClass
    K = HK.Child(out)
    live = os.path.join(B.USERDATA, "Saves", WORLD)
    home = os.path.join(SCRATCH, "live", WORLD)
    os.makedirs(os.path.join(home, "mods"))
    shutil.copy2(os.path.join(live, "config.json"), os.path.join(home, "config.json"))
    md = os.path.join(live, "mods")
    ours = sorted(d for d in os.listdir(md) if d.startswith("Skyy_SkyyUiProbe")) if os.path.isdir(md) else []
    for d in ours:
        shutil.copytree(os.path.join(md, d), os.path.join(home, "mods", d))
    K.check(os.path.isfile(os.path.join(home, "config.json")), "LIVE: %s config.json copied into scratch (read-only source); probe data folders in the live world: %s" % (WORLD, ours or "none"))
    hcls = os.path.join(SCRATCH, "hcls_live")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, JAR], verify=True)
    CPj = JClass("javassist.ClassPool").getDefault()
    CPj.appendClassPath(B.SERVER_JAR)
    rc = CPj.makeClass("uiprobeharness.CaptureCmds", CPj.get("com.hypixel.hytale.server.core.command.system.CommandRegistry"))
    rc.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", rc))
    rc.addConstructor(JClass("javassist.CtNewConstructor").make("public CaptureCmds() { super((java.util.List) null, (java.util.function.BooleanSupplier) null, "
                                                                 "(String) null, (com.hypixel.hytale.server.core.plugin.PluginBase) null); }", rc))
    rc.addMethod(JClass("javassist.CtNewMethod").make("public com.hypixel.hytale.server.core.command.system.CommandRegistration registerCommand("
                                                       "com.hypixel.hytale.server.core.command.system.AbstractCommand c) { CAP.add(c); return null; }", rc))
    rc.writeFile(hcls)
    re_ = CPj.makeClass("uiprobeharness.CaptureEvents", CPj.get("com.hypixel.hytale.event.EventRegistry"))
    re_.addField(JClass("javassist.CtField").make("public static java.util.List CAP = new java.util.ArrayList();", re_))
    re_.addConstructor(JClass("javassist.CtNewConstructor").make("public CaptureEvents() { super((java.util.List) null, (java.util.function.BooleanSupplier) null, "
                                                                   "(String) null, (com.hypixel.hytale.event.IEventRegistry) null); }", re_))
    re_.addMethod(JClass("javassist.CtNewMethod").make("public com.hypixel.hytale.event.EventRegistration registerGlobal(Class c, java.util.function.Consumer k) {"
                                                       " CAP.add(c.getName() + \" \" + k.getClass().getName()); return null; }", re_))
    re_.writeFile(hcls)
    CAPC = JClass("uiprobeharness.CaptureCmds")
    CAPE = JClass("uiprobeharness.CaptureEvents")
    SMc = JClass("com.hypixel.hytale.server.core.io.ServerManager")
    PADc = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    PBc = JClass("com.hypixel.hytale.server.core.plugin.PluginBase")
    PL = JClass(PKG + "SkyyUiProbePlugin")

    def setf(o, name, v):
        f_ = PBc.class_.getDeclaredField(name)
        f_.setAccessible(True)
        f_.set(o, v)
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend").subscribe(CAPLOG)

    def records():
        out_ = []
        for r in list(CAPLOG):
            try:
                out_.append(str(r.getMessage()))
            except Exception:
                pass
        return out_

    def snap():
        d_ = {}
        for dp, _dn, fns in os.walk(home):
            for f_ in fns:
                q = os.path.join(dp, f_)
                d_[os.path.relpath(q, home)] = (open(q, "rb").read(), os.path.getmtime(q))
        return d_
    s0 = snap()
    roots = []
    sm_ = U.allocateInstance(SMc.class_)
    fsub = SMc.class_.getDeclaredField("subPacketHandlers")
    fsub.setAccessible(True)
    fsub.set(sm_, JClass("java.util.concurrent.CopyOnWriteArrayList")())
    fins = SMc.class_.getDeclaredField("instance")
    fins.setAccessible(True)
    fins.set(None, sm_)
    finb = PADc.class_.getDeclaredField("inboundHandlers")
    finb.setAccessible(True)
    inb0 = int(finb.get(None).size())
    evs, inbs = [], []
    for n_ in range(2):
        CAPC.CAP.clear()
        CAPE.CAP.clear()
        p_ = U.allocateInstance(PL.class_)
        setf(p_, "logger", JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyUiProbe"))
        setf(p_, "dataDirectory", JClass("java.nio.file.Paths").get(os.path.join(home, "mods", "Skyy_SkyyUiProbe")))
        setf(p_, "commandRegistry", U.allocateInstance(CAPC.class_))
        setf(p_, "shutdownTasks", JClass("java.util.concurrent.CopyOnWriteArrayList")())
        setf(p_, "eventRegistry", U.allocateInstance(CAPE.class_))
        m_ = PL.class_.getDeclaredMethod("setup")
        m_.setAccessible(True)
        m_.invoke(p_)
        roots.append(list(CAPC.CAP))
        evs.append([str(x) for x in CAPE.CAP])
        inbs.append(int(finb.get(None).size()))
        sd_ = PL.class_.getDeclaredMethod("shutdown")
        sd_.setAccessible(True)
        try:
            sd_.invoke(p_)
        except Exception as ex:
            K.notes.append("LIVE: shutdown %d: %s" % (n_ + 1, str(ex)[:120]))
        time.sleep(0.3)
    K.eq(int(finb.get(None).size()), inb0, "LIVE: shutdown removed our adapter filter each time (inbound list back to %d)" % inb0)
    K.eq(inbs, [inb0 + 1, inb0 + 1], "LIVE: each start adds ONE inbound filter")
    K.eq(int(fsub.get(sm_).size()), 1, "LIVE: the sub-packet handler factory is registered ONCE per server run (2 starts)")
    if int(fsub.get(sm_).size()) == 1:
        K.eq(str(fsub.get(sm_).get(0).getClass().getSimpleName()), "InvHookFactory", "LIVE: ... it is ours")
    for n_, ev_ in enumerate(evs):
        K.eq(sorted(e_.split(" ")[0].rsplit(".", 1)[-1] + " " + e_.split(" ")[1].rsplit(".", 1)[-1] for e_ in ev_),
             ["PlayerDisconnectEvent InvBye", "PlayerReadyEvent InvReady"], "LIVE: start %d registers the disconnect + world-change listeners" % (n_ + 1))
    ready = [m_ for m_ in records() if "[SkyyUiProbe] %s ready" % VERSION in m_]
    K.eq(len(ready), 2, "LIVE: setup() twice = two '[SkyyUiProbe] %s ready' lines" % VERSION)
    K.check(bool(ready) and "/uiprobe tip / tiplater / tipgear" in ready[0] and "/uiprobe inv, /uiprobe tab on|off" in ready[0],
            "LIVE: the ready line names the tip probe + the inventory probe: %s" % (ready[:1] or [None])[0])
    for n_, rs in enumerate(roots):
        K.eq([str(c_.getName()) for c_ in rs], ["skyprobe"], "LIVE: start %d registers ONE root /skyprobe" % (n_ + 1))
        if len(rs) == 1:
            r_ = rs[0]
            K.check("uiprobe" in [str(a) for a in r_.getAliases()], "LIVE: start %d alias uiprobe" % (n_ + 1))
            K.eq(sorted(str(k) for k in r_.getSubCommands().keySet()), ["tab", "tip", "tiplater"], "LIVE: start %d sub-commands" % (n_ + 1))
            K.eq(int(r_.getVariantCommands().size()), 1, "LIVE: start %d the 1-word usage variant" % (n_ + 1))
    s2 = snap()
    K.check(sorted(s2) == sorted(s0) and all(s2[k] == s0[k] for k in s0), "LIVE: the scratch copy is byte + time identical after both starts (%d files)" % len(s0))
    K.check(not os.path.exists(os.path.join(home, "mods", "Skyy_SkyyUiProbe")), "LIVE: no data folder was created (the probe keeps nothing)")
    K.check(not [m_ for m_ in records() if "SEVERE" in m_ or "Exception" in m_], "LIVE: no error logged")
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
    _src = open(os.path.join(HERE, "build_skyyuiprobe_%s.py" % VERSION), encoding="utf-8").read()
    K.eq(len(re.findall(r"\.withMetadata\(", _src)), 1, "J: ONE withMetadata in the build: the fresh probe stack (0.11: the grid copy is a new stack)")
    K.check("g.setItemStack(new @IS@(s.getItemId(), s.getQuantity(), s.getDurability(), s.getMaxDurability(), (@BSON@) null));" in _src, "J: 0.11 the grid copy = a NEW ItemStack(id, qty, dur, max, null): no metadata, no quality override")
    K.check(re.search(r'return new @IS@\("@TIPIT@", 1\)\.withMetadata\(', _src) is not None, "J: ... and it is on a NEW ItemStack")
    K.check(not any(w in _src for w in ("FileOutputStream", "Files.write", "Files.newBufferedWriter", "FileWriter", "Files.createDirect")), "J: the build's Java writes no file")
    K.check(".setMetadata(" not in _src and "replaceItemStackInSlot" not in _src and "setItemStackForSlot" not in _src, "J: no setMetadata / slot writes")
    K.check(not any(n.lower().endswith(".ui") for n in names), "J: no .ui files")
    pngs = [n for n in names if n.endswith(".png")]
    K.check(all((n.startswith("Common/UI/Custom/SkyyUiProbe/") or n == "Common/Particles/Textures/SkyyUiProbe/TrailDot.png") and "_" not in n
                for n in pngs), "J: pictures under our roots only")
    bad = [n for n in pngs if n.endswith("@2x.png") and any(v % 2 for v in struct.unpack(">II", z.read(n)[16:24]))]
    K.eq(bad, [], "J: every @2x picture has even sizes")
    K.eq(sorted(n for n in names if n.startswith("com/skyy/uiprobe/pages/")),
         sorted("com/skyy/uiprobe/pages/%s.txt" % c for c in [c[0] for c in D["cases"]] + ["nodes", "inv", "invbag"]), "J: page data files")
    for k_ in ("inv", "invbag"):
        K.check("_" not in "".join(D["inv"]["pages"][k_]["ids"]) and D["inv"]["pages"][k_]["elements"] <= 1600, "J: %s ids hold no underscore, <= 1600 elements" % k_)
        t_ = z.read("com/skyy/uiprobe/pages/%s.txt" % k_).decode("utf-8")
        K.check("InventorySectionId" not in t_ and "SkyyUiProbe/Inv/Clear.png" in t_ and ("#SkyyPrIb" in t_) == (k_ == "invbag"), "J: %s markup (section ids set at run time, the drop zone, the bag only in invbag)" % k_)
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
    elif ph == "compare":
        run_cmp(HK.arg("--out"))
    elif ph == "live":
        run_live(HK.arg("--out"))
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
    assert os.path.isfile(OLD_JAR), "the 0.8 jar for the class compare: " + OLD_JAR
    for label in ("jar", "compare", "mkfake", "verify", "exec", "live", "audit"):
        out = os.path.join(SCRATCH, "%s.json" % label)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--phase", label, "--out", out, "--dir", SCRATCH, "--jar", JAR, "--old-jar", OLD_JAR], env=env)
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
