"""Fishing UI mockup sheet (SkyyFishing): HUD minigame states + Fishing Bench tabs, vanilla-kit palette.
Deterministic, Pillow only. Usage: python3 make_fishing_ui.py <out.png>
Fonts: DejaVu Sans / Bold stand in for NunitoSans (Default) and Lexend (Secondary) - widths are close, not exact.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

FD = "/usr/share/fonts/truetype/dejavu/"
def F(size, bold=False):
    return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)

# --- skyyui COLOR names (tools/skyyui.py COLOR) ---
C = {'text': '#96a9be', 'title': '#b4c8c9', 'section': '#9aacbc', 'caption': '#878e9c', 'rowName': '#d6e4ee',
     'rowSub': '#7f93a6', 'rowBadge': '#9aacbc', 'disabled': '#797b7c', 'gold': '#E8A93B', 'buttonText': '#bfcdd5',
     'value': '#b7cedd', 'propKey': '#7a8a9a', 'error': '#ff6b6b', 'success': '#39f493', 'warning': '#ffcc00',
     'info': '#7caacc', 'have': '#3d913f', 'outOfStock': '#cc4444', 'row': '#101925(0.55)', 'well': '#000000(0.15)',
     'hud': '#000000(0.2)', 'separator': '#2b3542', 'formLine': '#5e512c', 'slotBorder': '#1a2530',
     'slotBorderHave': '#2a5a3a', 'progressTrack': '#1a2030', 'progressBlue': '#4a7caa', 'progressGreen': '#7caa4a',
     'progressFill': '#aa7c4a', 'selected': '#4274a5', 'cardHover': '#c9a050'}
QUAL = {"Common": "#c9d2dd", "Uncommon": "#3e9049", "Rare": "#2770b7", "Epic": "#8b339e", "Legendary": "#d6a032"}
# mockup-only stand-ins for the vanilla TEXTURES (ContainerPatch / Header / button textures are images, not colours)
SHELL_BODY = "#1b2430"; SHELL_EDGE = "#3a4656"; SHELL_HEAD = "#141b24"
BTN = {"primary": ("#3f6f9e", "#5a8cbd", "#e8f0f6"), "secondary": ("#2a3442", "#3a4757", "#bfcdd5"),
       "destructive": ("#7a2f2f", "#9a4040", "#f0dada"), "disabled": ("#262a30", "#30353c", "#797b7c")}


def rgba(s):
    a = 255
    if "(" in s:
        s, al = s.split("(")
        a = int(round(float(al.rstrip(")")) * 255))
    s = s.lstrip("#")
    if len(s) == 8:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4, 6))
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


class Sheet:
    def __init__(self, w, h, bg):
        self.im = Image.new("RGBA", (w, h), rgba(bg))
        self.d = ImageDraw.Draw(self.im)

    def rect(self, box, col, outline=None, width=1):
        x0, y0, x1, y1 = [int(v) for v in box]
        c = rgba(col)
        if c[3] < 255:
            layer = Image.new("RGBA", (x1 - x0, y1 - y0), c)
            self.im.alpha_composite(layer, (x0, y0))
        else:
            self.d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=c)
        if outline:
            self.d.rectangle((x0, y0, x1 - 1, y1 - 1), outline=rgba(outline), width=width)

    def text(self, xy, s, col="text", size=15, bold=False, anchor="la"):
        col = C.get(col, col)
        self.d.text(xy, s, fill=rgba(col), font=F(size, bold), anchor=anchor)

    def tw(self, s, size=15, bold=False):
        return self.d.textlength(s, font=F(size, bold))

    # ---- kit look-alikes ----
    def shell(self, x, y, w, h, title):
        # gold ornament (+12 px above the root, ContainerDecorationTop stand-in)
        cx = x + w // 2
        self.d.polygon([(cx - 60, y + 2), (cx, y - 12), (cx + 60, y + 2)], fill=rgba("#8a6a2a"))
        self.d.polygon([(cx - 40, y + 2), (cx, y - 8), (cx + 40, y + 2)], fill=rgba(C["cardHover"]))
        self.rect((x, y, x + w, y + h), SHELL_BODY, outline=SHELL_EDGE, width=2)
        self.rect((x + 2, y + 2, x + w - 2, y + 38), SHELL_HEAD)
        self.d.line((x + 2, y + 38, x + w - 2, y + 38), fill=rgba(C["formLine"]), width=2)
        self.text((cx, y + 20), title.upper(), "title", 15, True, "mm")
        # bottom ornament
        self.d.polygon([(cx - 30, y + h - 1), (cx, y + h + 6), (cx + 30, y + h - 1)], fill=rgba("#8a6a2a"))
        return x + 17, y + 38 + 17, w - 34, h - 38 - 34   # inner box (padding 17)

    def button(self, x, y, w, h, s, kind="secondary", size=15):
        base, top, txt = BTN[kind]
        self.rect((x, y, x + w, y + h), base, outline="#0e141b")
        self.rect((x + 1, y + 1, x + w - 1, y + h // 2), top)
        self.rect((x + 1, y + h // 2, x + w - 1, y + h - 1), base)
        self.text((x + w / 2, y + h / 2), s, txt, size, True, "mm")

    def tabs(self, x, y, w, names, sel, h=36):
        n = len(names); gap = 5
        bw = (w - gap * (n - 1)) / n
        for i, s in enumerate(names):
            self.button(x + i * (bw + gap), y, bw, h, s.upper(), "primary" if i == sel else "secondary", 14)
        return h

    def section(self, x, y, s):
        self.text((x, y), s.upper(), "section", 13, True)

    def row(self, x, y, w, h, sel=False, static=False):
        self.rect((x, y, x + w, y + h), "#132033(0.8)" if sel else C["row"])
        self.rect((x, y, x + 4, y + h), C["selected"] if sel else "#1d2a38")

    def slot(self, x, y, s=44, have=False, empty=False, qual=None):
        self.rect((x, y, x + s, y + s), "#0c121a(0.85)", outline=C["slotBorderHave"] if have else C["slotBorder"], width=2)
        if qual:
            self.d.rectangle((x + 2, y + 2, x + s - 3, y + s - 3), outline=rgba(QUAL[qual]), width=1)
        if empty:
            self.d.line((x + s // 2 - 6, y + s // 2, x + s // 2 + 6, y + s // 2), fill=rgba("#3a4656"), width=2)
            self.d.line((x + s // 2, y + s // 2 - 6, x + s // 2, y + s // 2 + 6), fill=rgba("#3a4656"), width=2)

    def prop(self, x, y, w, k, v, vcol="value"):
        self.text((x, y), k, "propKey", 15)
        self.text((x + w, y), v, vcol, 15, True, "ra")

    def bar(self, x, y, w, h, frac, col, track="progressTrack", mark=None):
        self.rect((x, y, x + w, y + h), C[track], outline="#0b0f15")
        fw = int((w - 2) * max(0, min(1, frac)))
        if fw > 0:
            self.rect((x + 1, y + 1, x + 1 + fw, y + h - 1), col)
            self.rect((x + 1, y + 1, x + 1 + fw, y + 1 + max(1, h // 4)), "#ffffff(0.18)")
        if mark is not None:
            mx = x + int(w * mark)
            self.d.line((mx, y - 3, mx, y + h + 2), fill=rgba(C["gold"]), width=2)


# ---------------- tiny item icons (40 px, 1 px dark outline, lit top-left) ----------------
def icon(sh, kind, x, y, s=40, tint="#b87333"):
    d = sh.d; o = rgba("#0b0d10")
    def px(xx, yy, ww, hh, c):
        d.rectangle((x + xx, y + yy, x + xx + ww - 1, y + yy + hh - 1), fill=rgba(c))
    if kind == "rod":
        for i in range(30):
            px(6 + i, 33 - i, 3, 3, "#0b0d10")
        for i in range(29):
            px(7 + i, 33 - i, 2, 2, tint if i < 8 else "#9c7a4e")
        px(9, 26, 6, 6, "#0b0d10"); px(10, 27, 4, 4, tint)
        d.line((x + 36, y + 4, x + 36, y + 30), fill=rgba("#d6e4ee"), width=1)
    elif kind == "reel":
        d.ellipse((x + 6, y + 6, x + 34, y + 34), fill=o)
        d.ellipse((x + 8, y + 8, x + 32, y + 32), fill=rgba(tint))
        d.ellipse((x + 10, y + 10, x + 22, y + 22), fill=rgba("#ffffff(0.35)"))
        d.ellipse((x + 15, y + 15, x + 25, y + 25), fill=o)
        px(30, 18, 8, 4, "#0b0d10"); px(31, 19, 6, 2, "#c6bfb0")
    elif kind == "hook":
        d.arc((x + 8, y + 14, x + 30, y + 36), 0, 200, fill=o, width=5)
        d.arc((x + 9, y + 15, x + 29, y + 35), 0, 200, fill=rgba(tint), width=3)
        px(27, 4, 4, 22, "#0b0d10"); px(28, 5, 2, 20, tint)
        px(8, 20, 4, 4, "#0b0d10")
    elif kind == "line":
        d.ellipse((x + 6, y + 8, x + 34, y + 32), fill=o)
        d.ellipse((x + 8, y + 10, x + 32, y + 30), fill=rgba("#cfc6a8"))
        for k in range(12, 30, 3):
            d.line((x + k, y + 11, x + k - 2, y + 29), fill=rgba("#9e9478"), width=1)
        d.ellipse((x + 16, y + 16, x + 24, y + 24), fill=rgba("#5c3a22"))
    elif kind == "sinker":
        d.polygon([(x + 20, y + 5), (x + 33, y + 30), (x + 20, y + 36), (x + 7, y + 30)], fill=o)
        d.polygon([(x + 20, y + 8), (x + 30, y + 29), (x + 20, y + 33), (x + 10, y + 29)], fill=rgba(tint))
        d.polygon([(x + 20, y + 8), (x + 13, y + 26), (x + 20, y + 22)], fill=rgba("#ffffff(0.25)"))
    elif kind == "fish":
        d.polygon([(x + 4, y + 20), (x + 14, y + 10), (x + 28, y + 12), (x + 34, y + 20), (x + 28, y + 28), (x + 14, y + 30)], fill=o)
        d.polygon([(x + 6, y + 20), (x + 15, y + 12), (x + 27, y + 14), (x + 32, y + 20), (x + 27, y + 26), (x + 15, y + 28)], fill=rgba(tint))
        d.polygon([(x + 32, y + 20), (x + 39, y + 12), (x + 39, y + 28)], fill=o)
        d.polygon([(x + 33, y + 20), (x + 38, y + 14), (x + 38, y + 26)], fill=rgba(tint))
        px(10, 17, 3, 3, "#0b0d10"); px(14, 13, 12, 3, "#ffffff(0.3)")
    elif kind == "fillet":
        d.rounded_rectangle((x + 6, y + 12, x + 34, y + 28), 6, fill=o)
        d.rounded_rectangle((x + 8, y + 14, x + 32, y + 26), 5, fill=rgba("#e89a7a"))
        for k in range(12, 32, 5):
            d.line((x + k, y + 15, x + k - 3, y + 25), fill=rgba("#f6c6b0"), width=1)
    elif kind == "dish":
        d.ellipse((x + 4, y + 18, x + 36, y + 34), fill=o)
        d.ellipse((x + 6, y + 19, x + 34, y + 32), fill=rgba("#c6bfb0"))
        d.ellipse((x + 10, y + 16, x + 30, y + 27), fill=rgba(tint))
        d.ellipse((x + 13, y + 17, x + 21, y + 21), fill=rgba("#ffffff(0.3)"))


def main(out):
    W, H = 2120, 2680
    sh = Sheet(W, H, "#0d1117")
    sh.text((40, 28), "SkyyFishing - UI mockup (cloud draft 2026-10-06, paper only)", "rowName", 26, True)
    sh.text((40, 64), "Vanilla kit palette (tools/skyyui.py COLOR). Window frames, buttons and fonts are stand-ins for the real textures; "
            "pages drawn 1:1 in px, the screen at 50%.", "caption", 15)

    # ================= A. the screen during the fight (50% scale of 1920x1080) =================
    ax, ay, aw, ah = 40, 110, 960, 540
    sh.text((ax, ay - 4), "A. SCREEN DURING THE FIGHT (1920 x 1080 at 50%)", "section", 15, True)
    ay += 22
    for i in range(ah):   # sky -> water
        t = i / ah
        c = (int(120 + 60 * t), int(170 + 30 * t), int(215 - 10 * t)) if i < 250 else (int(40 + 20 * (1 - t)), int(90 + 30 * (1 - t)), int(110 + 20 * (1 - t)))
        sh.d.line((ax, ay + i, ax + aw, ay + i), fill=c + (255,))
    sh.d.polygon([(ax + 560, ay + 250), (ax + 640, ay + 200), (ax + 700, ay + 215), (ax + 790, ay + 190), (ax + 880, ay + 250)], fill=(84, 120, 78, 255))
    sh.d.polygon([(ax, ay + 250), (ax + 160, ay + 236), (ax + 260, ay + 250)], fill=(70, 104, 64, 255))
    sh.d.polygon([(ax, ay + 540), (ax, ay + 420), (ax + 180, ay + 400), (ax + 300, ay + 540)], fill=(92, 128, 70, 255))
    for k in range(0, aw, 37):   # ripples
        sh.d.line((ax + k, ay + 300 + (k * 7) % 200, ax + k + 18, ay + 300 + (k * 7) % 200), fill=(150, 190, 200, 255))
    # bobber + line + "!"
    bx, by = ax + 470, ay + 330
    sh.d.line((ax + 900, ay + 540, ax + 760, ay + 300), fill=(90, 60, 30, 255), width=5)
    sh.d.line((ax + 760, ay + 300, bx, by), fill=(235, 235, 235, 255), width=1)
    sh.d.ellipse((bx - 7, by - 7, bx + 7, by + 7), fill=(200, 40, 40, 255), outline=(20, 20, 20, 255))
    sh.d.ellipse((bx - 18, by - 2, bx + 18, by + 10), outline=(220, 240, 250, 255))
    sh.text((bx, by - 30), "!", "#ffcc00", 30, True, "mm")
    # crosshair, hotbar, vitals (vanilla HUD positions UNVERIFIED)
    cx, cy = ax + aw // 2, ay + ah // 2
    sh.d.line((cx - 5, cy, cx + 5, cy), fill=(255, 255, 255, 200)); sh.d.line((cx, cy - 5, cx, cy + 5), fill=(255, 255, 255, 200))
    hx = cx - 9 * 26 // 2
    for i in range(9):
        sh.rect((hx + i * 26, ay + ah - 34, hx + i * 26 + 24, ay + ah - 10), "#000000(0.45)", outline="#c6bfb0" if i == 0 else "#3a4656")
    icon(sh, "rod", hx + 1, ay + ah - 34, 24)
    sh.bar(hx, ay + ah - 48, 110, 7, 0.8, "#c84040"); sh.bar(hx + 124, ay + ah - 48, 110, 7, 0.6, "#4a7caa")
    # the fishing widget (50%): centre, above the vitals
    wx, wy, ww, wh = cx - 110, ay + ah - 132, 220, 66
    sh.rect((wx, wy, wx + ww, wy + wh), C["hud"])
    sh.text((wx + 10, wy + 7), "REEL IN", "title", 10, True)
    sh.text((wx + ww - 10, wy + 7), "8.4 s", "value", 10, True, "ra")
    sh.bar(wx + 10, wy + 24, ww - 20, 12, 0.62, C["progressBlue"], mark=0.35)
    sh.text((wx + 10, wy + 44), "Click Use fast - 7 per s", "caption", 9)
    sh.d.rectangle((wx - 3, wy - 3, wx + ww + 2, wy + wh + 2), outline=rgba(C["gold"]), width=1)
    sh.text((wx + ww + 10, wy + 20), "<- the Fishing widget", "#ffcc00", 13, True)
    sh.text((wx + ww + 10, wy + 38), "   (HUD, not a page)", "#ffcc00", 12)
    # other HUD widgets that may sit on screen (SkyyHud) - placement only
    sh.rect((ax + 8, ay + 8, ax + 128, ay + 30), C["hud"]); sh.text((ax + 14, ay + 12), "Coins 12,450", "value", 10, True)
    sh.rect((ax + aw - 130, ay + 8, ax + aw - 8, ay + 30), C["hud"]); sh.text((ax + aw - 124, ay + 12), "Fishing 14  62%", "value", 10, True)

    # ================= B. widget states at 1:1 =================
    bx0, by0 = 1040, 110
    sh.text((bx0, by0 - 4), "B. FISHING WIDGET STATES (1:1, panel hud #000000(0.2) on a mid-grey test strip)", "section", 15, True)
    by0 += 24
    states = []
    def wbox(y, h):
        sh.rect((bx0, y, bx0 + 1040, y + h + 20), "#3b4a55")   # test background so the 0.2 black shows
        sh.rect((bx0 + 20, y + 10, bx0 + 460, y + 10 + h), C["hud"])
        return bx0 + 20, y + 10
    # 1 bite
    x, y = wbox(by0, 78)
    sh.text((x + 20, y + 10), "BITE", "warning", 16, True); sh.text((x + 420, y + 10), "Use now", "value", 15, True, "ra")
    sh.bar(x + 20, y + 40, 400, 14, 0.55, C["warning"])
    sh.text((x + 20, y + 58), "1.2 s window - bar shrinks", "caption", 13)
    sh.text((bx0 + 480, by0 + 14), "1  BITE  (fish.biteWindow 1.2 s)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "World: \"!\" above the bobber + splash sound.", "text", 14)
    sh.text((bx0 + 480, by0 + 60), "HUD: yellow word + a draining stat_bar. Miss it = re-wait.", "text", 14)
    by0 += 112
    # 2 fight
    x, y = wbox(by0, 96)
    sh.text((x + 20, y + 10), "REEL IN", "title", 16, True); sh.text((x + 420, y + 10), "8.4 s", "value", 16, True, "ra")
    sh.bar(x + 20, y + 40, 400, 22, 0.62, C["progressBlue"], mark=0.35)
    sh.text((x + 20, y + 70), "Click Use fast", "caption", 13); sh.text((x + 420, y + 70), "7 per s", "info", 13, True, "ra")
    sh.text((bx0 + 480, by0 + 14), "2  FIGHT  (bar 0-100, starts at 35 = gold tick)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "Fill = progressBlue; above 80 it turns progressGreen.", "text", 14)
    sh.text((bx0 + 480, by0 + 60), "Timer counts down fish.timeLimit 12 s. Click rate shown", "text", 14)
    sh.text((bx0 + 480, by0 + 80), "so slow clickers see why they lose. Species stays hidden.", "text", 14)
    by0 += 130
    # 3 surge
    x, y = wbox(by0, 96)
    sh.text((x + 20, y + 10), "SURGE", "error", 16, True); sh.text((x + 420, y + 10), "6.1 s", "value", 16, True, "ra")
    sh.bar(x + 20, y + 40, 400, 22, 0.41, C["error"], mark=0.35)
    sh.text((x + 20, y + 70), "The fish pulls hard", "caption", 13); sh.text((x + 420, y + 70), "8 per s", "info", 13, True, "ra")
    sh.text((bx0 + 480, by0 + 14), "3  SURGE  (pull x1.6 for 0.6 s every 3 s)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "Word + fill switch to error red for the surge only;", "text", 14)
    sh.text((bx0 + 480, by0 + 60), "a short warning ~0.3 s before (stage 2 option).", "text", 14)
    by0 += 130
    # 4 nearly
    x, y = wbox(by0, 96)
    sh.text((x + 20, y + 10), "REEL IN", "title", 16, True); sh.text((x + 420, y + 10), "3.0 s", "warning", 16, True, "ra")
    sh.bar(x + 20, y + 40, 400, 22, 0.88, C["progressGreen"], mark=0.35)
    sh.text((x + 20, y + 70), "Almost", "caption", 13); sh.text((x + 420, y + 70), "9 per s", "info", 13, True, "ra")
    sh.text((bx0 + 480, by0 + 14), "4  ALMOST  (bar > 80, timer < 4 s)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "Green fill; the timer turns warning yellow under 4 s.", "text", 14)
    by0 += 130
    # 5 landed
    x, y = wbox(by0, 96)
    sh.text((x + 20, y + 10), "LANDED", "success", 16, True); sh.text((x + 420, y + 10), "Uncommon", QUAL["Uncommon"], 15, True, "ra")
    icon(sh, "fish", x + 20, y + 36, 40, "#7a9a5a")
    sh.text((x + 70, y + 38), "Trout  2.41 kg  52 cm", "rowName", 16, True)
    sh.text((x + 70, y + 62), "Personal record", "gold", 13, True)
    sh.text((bx0 + 480, by0 + 14), "5  LANDED  (shown 3 s, then hidden)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "Species, grade (quality colour), weight, length.", "text", 14)
    sh.text((bx0 + 480, by0 + 60), "Record line only when it is one. Same line in chat.", "text", 14)
    by0 += 130
    # 6 lost
    x, y = wbox(by0, 70)
    sh.text((x + 20, y + 10), "IT GOT AWAY", "error", 16, True)
    sh.text((x + 20, y + 40), "The bar ran empty", "caption", 14)
    sh.text((bx0 + 480, by0 + 14), "6  LOST  (bar 0 or time up; shown 2 s)", "rowName", 16, True)
    sh.text((bx0 + 480, by0 + 40), "Reason line: \"The bar ran empty\" / \"Out of time\".", "text", 14)
    by0 += 104
    sh.text((bx0, by0), "Treasure / junk land the same way: LANDED + \"Lost Property - Great\" or \"Junk - Old Boot\".", "caption", 14)

    # ================= C. Fishing Bench pages (1:1) =================
    PW, PH = 1000, 760
    tabs = ["Parts", "Rig", "Fillet", "Recipes"]
    ox = [40, 1080]; oy = [990, 1840]
    sh.text((40, 940), "C. FISHING BENCH PAGE (1:1, 1000 x 760 - fits 1080 with room; one page, four tabs)", "section", 15, True)

    def page(px_, py_, sel):
        ix, iy, iw, ih = sh.shell(px_, py_, PW, PH, "Fishing Bench")
        sh.tabs(ix, iy, iw, tabs, sel)
        # footer
        fy = py_ + PH - 17 - 36
        sh.d.line((ix, fy - 9, ix + iw, fy - 9), fill=rgba(C["separator"]), width=1)
        sh.button(ix + iw - 150, fy, 150, 36, "Close")
        return ix, iy + 36 + 10, iw, fy - 9 - 8 - (iy + 46), fy

    # ---- Parts ----
    ix, iy, iw, ihh, fy = page(ox[0], oy[0], 0)
    sh.text((ix, iy), "Craft rods, reels, hooks, lines and sinkers. Recipes open with Fish + metal collections.", "text", 15)
    lw = 520; ly = iy + 28; lh = ihh - 28 - 40
    sh.rect((ix, ly, ix + lw, ly + lh), C["well"])
    rows = [("ROD", None), ("rod", "Bamboo Rod", "Max 3 kg - Lv 1", "Owned", "#9c7a4e", 0),
            ("rod", "Copper Rod", "Max 6 kg - Lv 10", "Craft", "#b87333", 1),
            ("rod", "Iron Rod", "Max 10 kg - Lv 15", "Pond Fish VI", "#a0a8b0", 2),
            ("REEL", None), ("reel", "Copper Reel", "Reel Power 4.9", "Craft", "#b87333", 0),
            ("reel", "Iron Reel", "Reel Power 5.7", "Pond Fish VII", "#a0a8b0", 2),
            ("HOOK", None), ("hook", "Barbed Hook I", "Grade luck +5%", "Craft", "#b87333", 0),
            ("hook", "Lure Hook I", "Fishing Speed +5", "Craft", "#b87333", 0),
            ("LINE", None), ("line", "Braided Line I", "Time limit +1 s", "Pond Fish V", "#cfc6a8", 2),
            ("SINKER", None), ("sinker", "Weighted Sinker I", "Bar start +5", "Craft", "#8a8a8a", 0)]
    ry = ly + 8
    for r in rows:
        if r[1] is None:
            sh.section(ix + 12, ry + 4, r[0]); ry += 24; continue
        kind, name, sub, tag, tint, st = r
        sel = name == "Copper Rod"
        sh.row(ix + 8, ry, lw - 28, 48, sel)
        sh.slot(ix + 18, ry + 4, 40)
        icon(sh, kind, ix + 18, ry + 4, 40, tint)
        sh.text((ix + 68, ry + 6), name, "rowName" if st != 2 else "disabled", 15, True)
        sh.text((ix + 68, ry + 26), sub, "rowSub", 13)
        sh.text((ix + lw - 32, ry + 16), tag, {0: "rowBadge", 1: "success", 2: "disabled"}[st] if tag != "Owned" else "info", 13, True, "ra")
        ry += 51
        if ry > ly + lh - 50:
            break
    sh.rect((ix + lw - 14, ly + 6, ix + lw - 8, ly + lh - 6), "#ffffff(0.06)"); sh.rect((ix + lw - 14, ly + 6, ix + lw - 8, ly + 120), "#ffffff(0.25)")
    # right: recipe panel
    rx = ix + lw + 14; rw = iw - lw - 14
    sh.rect((rx, ly, rx + rw, ly + lh), C["well"])
    sh.slot(rx + 14, ly + 14, 64, qual=None); icon(sh, "rod", rx + 26, ly + 26, 40, "#b87333")
    sh.text((rx + 92, ly + 18), "Copper Rod", "rowName", 18, True)
    sh.text((rx + 92, ly + 44), "Tier 1 - Fishing Lv 10", "rowSub", 14)
    sh.section(rx + 14, ly + 96, "Stats")
    yy = ly + 120
    for k, v in [("Max fish weight", "6 kg"), ("Reforge pool", "Speed, Treasure, Power, Wisdom"), ("Upgrades from", "Bamboo Rod")]:
        sh.prop(rx + 14, yy, rw - 28, k, v); yy += 26
    sh.section(rx + 14, yy + 10, "Needs"); yy += 36
    for k, v, ok in [("Bamboo Rod", "1 / 1", True), ("Copper Bar", "14 / 8", True), ("Plant Fibre", "3 / 6", False), ("Pond Fish III", "done", True), ("Copper IV", "done", True)]:
        sh.prop(rx + 14, yy, rw - 28, k, v, "have" if ok else "outOfStock"); yy += 26
    sh.text((rx + 14, yy + 10), "Missing 3 Plant Fibre", "error", 14, True)
    sh.button(rx + 14, ly + lh - 50, rw - 28, 36, "Craft", "disabled")
    sh.text((ix, fy - 8 - 26), "- Need 3 more Plant Fibre", "error", 14, True)

    # ---- Rig ----
    ix, iy, iw, ihh, fy = page(ox[1], oy[0], 1)
    sh.text((ix, iy), "Put a rod in, then add a reel, hook, line and sinker. Parts come off free.", "text", 15)
    ly = iy + 28; lh = 330
    sh.rect((ix, ly, ix + 470, ly + lh), C["well"])
    sh.section(ix + 14, ly + 10, "Your rig")
    # rod slot big + four part slots
    sh.slot(ix + 20, ly + 40, 72, have=True, qual="Rare"); icon(sh, "rod", ix + 36, ly + 56, 40, "#b87333")
    sh.text((ix + 104, ly + 46), "Copper Rod", "rowName", 16, True); sh.text((ix + 104, ly + 68), "Rare - Lv 12 - reforged", "rowSub", 13)
    parts = [("Reel", "reel", "Copper Reel", "#b87333"), ("Hook", "hook", "Lure Hook I", "#b87333"), ("Line", None, "empty", None), ("Sinker", "sinker", "Weighted Sinker I", "#8a8a8a")]
    for i, (lab, k, nm, t) in enumerate(parts):
        yy = ly + 130 + i * 48
        sh.text((ix + 20, yy + 12), lab.upper(), "section", 13, True)
        sh.slot(ix + 100, yy, 44, have=k is not None, empty=k is None)
        if k:
            icon(sh, k, ix + 102, yy + 2, 40, t)
        sh.text((ix + 156, yy + 12), nm, "rowName" if k else "disabled", 15, k is not None)
        if k:
            sh.button(ix + 470 - 14 - 92, yy + 6, 92, 30, "Remove", "secondary", 13)
    # stats panel
    sx = ix + 484; sw = iw - 484
    sh.rect((sx, ly, sx + sw, ly + lh), C["well"])
    sh.section(sx + 14, ly + 10, "Rig total")
    yy = ly + 38
    for k, v, c in [("Max fish weight", "6 kg", "value"), ("Reel Power", "4.9 per click", "value"), ("Fishing Speed", "+5 (+3 reforge)", "success"),
                    ("Treasure Chance", "+0.4", "success"), ("Grade luck", "-", "disabled"), ("Bar start", "40", "value"),
                    ("Time limit", "12 s", "value"), ("Double catch", "-", "disabled"), ("Junk", "10%", "value"), ("Fishing Wisdom", "+2%", "success")]:
        sh.prop(sx + 14, yy, sw - 28, k, v, c); yy += 27
    # parts grid
    gy = ly + lh + 12
    sh.section(ix, gy, "Parts in your bags - click one to fit it")
    gy += 22
    sh.rect((ix, gy, ix + iw, gy + 2 * 50 + 12), C["well"])
    kinds = [("line", "#cfc6a8"), ("line", "#9fb7c8"), ("hook", "#a0a8b0"), ("sinker", "#6a6a6a"), ("reel", "#a0a8b0"), ("hook", "#b87333"), ("sinker", "#8a8a8a")]
    for i in range(16):
        gx = ix + 8 + (i % 16) * 58; gyy = gy + 6 + (i // 16) * 50
        sh.slot(gx, gyy, 46, empty=False)
        if i < len(kinds):
            icon(sh, kinds[i][0], gx + 3, gyy + 3, 40, kinds[i][1])
    for i in range(16):
        gx = ix + 8 + i * 58; sh.slot(gx, gy + 56, 46)
    sh.text((ix, fy - 8 - 26), "+ Fitted Weighted Sinker I", "success", 14, True)
    sh.button(ix, fy, 200, 36, "Take rod out", "secondary")

    # ---- Fillet ----
    ix, iy, iw, ihh, fy = page(ox[0], oy[1], 2)
    sh.text((ix, iy), "Cut whole fish into fillets for Cooking and the Bazaar - 1 fillet per 0.5 kg, max 40.", "text", 15)
    ly = iy + 28
    cols = [("", 56), ("Fish", 300), ("Grade", 130), ("Weight", 120), ("Fillets", 100), ("", 120)]
    xx = ix + 12
    for n, wv in cols:
        sh.text((xx, ly + 4), n.upper(), "section", 13, True); xx += wv
    ly += 26
    lh = 420
    sh.rect((ix, ly, ix + iw, ly + lh), C["well"])
    fish = [("Trout", "Uncommon", 2.41, "#7a9a5a"), ("Bluegill", "Common", 0.62, "#5a8aba"), ("Catfish", "Rare", 7.80, "#8a7a6a"),
            ("Minnow", "Common", 0.21, "#9aaab0"), ("Trout", "Common", 1.10, "#7a9a5a"), ("Pondering Pike", "Epic", 8.90, "#5a7a4a"),
            ("Bluegill", "Common", 0.95, "#5a8aba")]
    ry = ly + 8
    for i, (nm, gr, kg, t) in enumerate(fish):
        sel = i == 2
        sh.row(ix + 8, ry, iw - 16, 52, sel)
        sh.slot(ix + 16, ry + 4, 44, qual=gr); icon(sh, "fish", ix + 18, ry + 6, 40, t)
        n = min(40, int(kg / 0.5))
        xx = ix + 12 + 56
        sh.text((xx, ry + 16), nm, "rowName", 15, True); xx += 300
        sh.text((xx, ry + 16), gr, QUAL[gr], 15, True); xx += 130
        sh.text((xx, ry + 16), "%.2f kg" % kg, "value", 15); xx += 120
        sh.text((xx, ry + 16), str(n) if n else "0 - too small", "value" if n else "disabled", 15, n > 0); xx += 100
        sh.button(ix + iw - 16 - 110, ry + 9, 110, 34, "Fillet" if n else "Sell only", "secondary" if n else "disabled", 14)
        ry += 56
    sh.text((ix, ly + lh + 10), "Fish Cooler 7 / 27   -   Rare and better ask once: \"Fillet a Rare Catfish? Selling whole pays more.\"", "caption", 14)
    sh.text((ix, fy - 8 - 26), "+ 15 Pond Fillets from Catfish 7.80 kg", "success", 14, True)
    sh.button(ix, fy, 220, 36, "Fillet all Common", "secondary")
    sh.button(ix + 228, fy, 200, 36, "Open Cooler", "secondary")

    # ---- Recipes ----
    ix, iy, iw, ihh, fy = page(ox[1], oy[1], 3)
    sh.text((ix, iy), "Fish foods. Cook them at the Cooking Bench - SkyyCooking grades them.", "text", 15)
    ly = iy + 28; lw = 440; lh = ihh - 28 - 40
    sh.rect((ix, ly, ix + lw, ly + lh), C["well"])
    dishes = [("Grilled Fish", "Stamina - vanilla", True, "#c08040"), ("Fish Skewer", "Stamina + Health", True, "#a07040"),
              ("Fish Sticks", "Stamina", True, "#d0a050"), ("Chowder", "Stamina + Health", False, "#e0d0b0"),
              ("Frost Cod Stew", "Stamina + Health - Zone 3", False, "#b0c0d0"), ("Cinderfin Jerky", "Stamina - Zone 4", False, "#8a4a2a")]
    ry = ly + 8
    for i, (nm, sub, ok, t) in enumerate(dishes):
        sh.row(ix + 8, ry, lw - 16, 52, i == 1)
        sh.slot(ix + 16, ry + 4, 44); icon(sh, "dish", ix + 18, ry + 6, 40, t)
        sh.text((ix + 70, ry + 8), nm, "rowName" if ok else "disabled", 15, True)
        sh.text((ix + 70, ry + 29), sub, "rowSub", 13)
        sh.text((ix + lw - 24, ry + 18), "Known" if ok else "Locked", "info" if ok else "disabled", 13, True, "ra")
        ry += 56
    rx = ix + lw + 14; rw = iw - lw - 14
    sh.rect((rx, ly, rx + rw, ly + lh), C["well"])
    sh.slot(rx + 14, ly + 14, 64); icon(sh, "dish", rx + 26, ly + 26, 40, "#a07040")
    sh.text((rx + 92, ly + 18), "Fish Skewer", "rowName", 18, True)
    sh.text((rx + 92, ly + 44), "Meat + veggie family", "rowSub", 14)
    sh.section(rx + 14, ly + 96, "Ingredients")
    yy = ly + 120
    for k, v, ok in [("Pond Fillet", "5 / 2", True), ("Carrot", "0 / 1", False), ("Stick", "12 / 1", True)]:
        sh.prop(rx + 14, yy, rw - 28, k, v, "have" if ok else "outOfStock"); yy += 26
    sh.section(rx + 14, yy + 10, "Effect at grade C"); yy += 36
    for k, v in [("Stamina", "+18 now, +24 over 10 s"), ("Health", "+8 now, +12 over 10 s"), ("Where", "Cooking Bench")]:
        sh.prop(rx + 14, yy, rw - 28, k, v); yy += 26
    sh.text((rx + 14, yy + 14), "Numbers from Food-Expansion-Draft (placeholders)", "caption", 13)
    sh.button(rx + 14, ly + lh - 50, rw - 28, 36, "Show in Cooking Bench", "secondary")
    sh.text((ix, fy - 8 - 26), "= Recipe list only - nothing is cooked here", "info", 14, True)

    sh.im.convert("RGB").save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1])
