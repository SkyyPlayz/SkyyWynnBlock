"""SkyyUiProbe 0.9 - build script (javassist via jpype). A small, OP-ONLY dev / test mod: the probe of research/UI-Queue-Spec.md section 10
(the Hylterium UI queue): 15 cases in ONE ~5 minute session, '/skyprobe tour'. Nothing a player can use, no saved data, no config, no
items, NO HUD of its own (one custom HUD per player - a probe HUD would replace SkyyHud's).

Run:   python SkyyUiProbe/build_skyyuiprobe_0.9.py    -> SkyyUiProbe/SkyyUiProbe-0.9.jar (no --deploy on purpose)
       --dump-only : build the layout, pictures and page data and stop before the JVM (prints the counts)
       --assets-out <dir under tools/dev/scratch/> : also write every jar asset + dump.json there (previews, the harness)
Check: python SkyyUiProbe/test_skyyuiprobe_0.9.py   (J jar, A verify -Xverify:all, X exec every case's server path through the real
       PageManager + EVERY bound event of every case = exactly one page packet, AA engine-access audit)

0.9 (tools/uiprobe_0_9_patch.py - read its header for the engine facts): + the PRICE-TOOLTIP PROBE R0 of research/Price-Tooltips-Spec.md
section 5, every 0.8 case kept. Op only: /uiprobe tip <item id> <text> (ONE UpdateTranslations AddOrUpdate for the item's description key,
to you only; "\n" = new line; reset = the server's own text back), /uiprobe tiplater <item id> <text> (the same 5 s later from the timer
thread), /uiprobe tipgear (one probe Weapon_Claws_Tribal whose ItemDisplayMetadata description has a translation child
server.skyy.probe.tip, then that key is sent), /uiprobe tip gear <text> (a new text for that key). No real stack is touched.

Skyy's words (docs/answered/ui.md 2026-10-22 UI QUEUE) + "work through your whole list.": popups "Fold the quest tracker (Recommended)",
"Yes if the probe looks good (Recommended)" (vanilla feed), "Particle trail instead" (quest guide: a dotted per-player particle trail
toward the target; the Objective / distance text on the HUD above the hotbar), "Bottom bar (Recommended)" (NPC talk).

Derived from build_skyyuiprobe_0.7.1.py (kept as it is): the same mod name / package / command, the 0.7.1 one-packet rule + safety net,
the page data resources (com/skyy/uiprobe/pages/<case>.txt: A parent / markup, S b.set text, E binding lines). 0.7.1's M1-M3 / M7
passed (research/Radial-Trees-Spec.md "Probe results") and are GONE; the map layout now comes from tools/skyymap.py (build + scaled +
its pictures) instead of 0.7.1's copy. The /skyprobe map <case> form is removed (replace, never add); /skyprobe <case> stays.

THE TOUR (/skyprobe tour; every page has Back / Next case; /skyprobe next opens the case after the last one you saw; /skyprobe <case>):
  1  m4   map-assetimage  (retest) 0.7.1's three discs; Next state = b.set(#Id.AssetPath) via sendUpdate
  2  m5   map-anchor      (retest) click nodes: the halo moves by ONE Anchor update
  3  m6   map-tooltip     (retest) 3 discs with TooltipText; Esc with a tooltip open
  4  m8a  keep-scroll     the Gathering map at 200 % in the 2-axis scroll box; a node click = ONE sendUpdate: the halo Anchor, the
                          node's pre-placed 'max' picture .Visible true (+ the last one's false), the AssetImage disc's AssetPath, 2 texts
  5  m8b  clip-pan        the 200 % map in a plain 840 x 774 Group; Left / Right / Up / Down / Centre move the map with ONE
                          b.setObject(#SkyyPrMp.Anchor); Rebuild redraws at the server-kept offset
  6  m8c  pan-in-scroll   (learn) the same Anchor move on the canvas INSIDE the scroll box
  7  h1a  head-before-open a runtime picture (your initials, 128 px) sent BEFORE the page / the case page is sent, in an AssetImage
  8  h1b  head-while-open 'Send a new picture': a NEW content-named PNG sent while the page is open + ONE sendUpdate of the AssetPath
  9  h1c  your head       your PlayerSkin's 20 part ids to chat + log; a 128 px front-view head composed AT RUN TIME from the INSTALLED
                          game's own models + textures (CosmeticRegistry + CommonAssetRegistry, read only - nothing vanilla is shipped)
  10 d1   dialogue-bar    a transparent 1600 x 980 root + a 1100 x 190 bar at the bottom ("Pebble", 3 lines, Skip / Next / Accept /
                          Not now); every page turn = one rebuild, Accept / Not now = one update, Esc closes
  11 t1   picture-tiles   4 draft tiles at 120 px + 1 at 150 px (our own build-time art @2x, a blue label bar, a gold hover edge)
  12 k1   key-hints       a look: close the page and check the vanilla bottom-right ability boxes (Mouse 5 / Q / E with our class icons)
  13 f1   vanilla-feed    'Close and run feed test': the page closes FIRST, 1 s later 9 notifications to you (skill XP with a text bar,
                          a kill with a gold name, Fortune with an item icon x3, a heal, collection progress, the 4 styles)
  14 f2   feed-tag        'Close and run tag test': 5 '+10 XP' notifications with the SAME tag, 300 ms apart (one card or five?)
  15 g1   ground-trail    'Close and run trail test': a target 48 blocks away; for 21 s, every 1 s, a dotted trail toward it that
                          only YOU see (viewer list = you): A our own dot picture (0-6 s), B the vanilla glow recoloured (7-13 s), C ONE
                          rotated particle system of 6 dots (14-20 s, Rotation3f yaw toward the target); the 'Objective / N blocks'
                          text = a chat stand-in every 5 s (the real one goes on SkyyHud's HUD above the hotbar - this probe has no HUD)
Every case logs + chats "PASS", "FAIL" or "Skyy: look - <what>". Every bound click answers with exactly ONE page packet (a rebuild,
one sendUpdate, or the close for the Close / run buttons); a safety net in handleDataEvent sends the engine's empty update when no
path answered.

ART (all generated HERE at build time, pure Python, our own geometry - no vanilla pixels; jar only, never committed):
  Common/UI/Custom/SkyyUiProbe/Map/...      skyymap pictures (base lines, gold edges, node states, hubs, halo, emblem) + M4 discs
  Common/UI/Custom/SkyyUiProbe/Tiles/...    the T1 draft tiles (painted-look scenes from polygons) + the gold hover edge
  Common/Particles/Textures/SkyyUiProbe/TrailDot.png   G1 trail A's dot (the path layout other mods ship particle textures with)
  Server/Particles/SkyyUiProbe/...          G1's 3 particle systems + their spawners (B / C use the vanilla Glow texture by path)
The heads case reads the installed game's models / textures at RUN TIME only (CommonAssetRegistry blobs, Gson, ImageIO); no
vanilla-derived file is in the jar or the repo.
"""
import sys, os, re, json, math, zipfile, hashlib, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyui as SUI
import skyymap as SM
import serverjar
import trees_v3_data as TD

if "--deploy" in sys.argv:
    raise SystemExit("SkyyUiProbe: --deploy is not supported - tools/deploy_set.py is the only deploy path")
VERSION = "0.9"
PKG = "com.skyy.uiprobe"
P = "SkyyPr"                              # every element id starts with this (no underscores)
NODE_PERM = "skyyuiprobe.admin"
TEX_ROOT = "Common/UI/Custom/"
MAP_DIR = "SkyyUiProbe/Map/"               # markup paths are written WITHOUT @2x (the client loads the @2x file)
TILE_DIR = "SkyyUiProbe/Tiles/"
ASSET_NAME_ROOT = "UI/Custom/"             # an AssetImage AssetPath = the common asset name (the jar path without "Common/")
RT_DIR = "UI/SkyyUiProbe/rt/"              # runtime pictures (content-named, SkyyHud's proven "UI/SkyyHud/mm/" pattern)
RES_DIR = "com/skyy/uiprobe/pages/"        # page data resources (next to the classes; never an asset)
PART_DIR = "Server/Particles/SkyyUiProbe/"
DOT_TEX = "Particles/Textures/SkyyUiProbe/TrailDot.png"
GLOW_TEX = "Particles/Textures/Basic/Glow.png"   # vanilla, referenced by path only (never shipped)
T0 = time.time()
# ---- HEAD NOTES (H1c; the Java class Heads draws from these rules at run time, from the installed game's files - read only)
# Checked at build time on the installed Common/Characters/Player.blockymodel (see the assert in section 2): with "a node's pivot = the
# parent's child frame + R_parent * position, its geometry centre AND its children's frame = pivot + R * offset" the body stacks feet
# 0..8 / calves / thighs / pelvis / belly / chest / head 93..121 with no gaps; an attachment root named after a Player head bone
# (Head, R-Eye-Attachment, Mouth-Attachment, ...) sits in that bone's child frame (its own position / offset are ignored).
SKIN_FIELDS = ["bodyCharacteristic", "underwear", "face", "eyes", "ears", "mouth", "facialHair", "haircut", "eyebrows", "pants", "overpants",
               "undertop", "overtop", "shoes", "headAccessory", "faceAccessory", "earAccessory", "skinFeature", "gloves", "cape"]
HEAD_ORDER = ["bodyCharacteristic", "ears", "face", "mouth", "eyes", "eyebrows", "facialHair", "haircut", "faceAccessory", "headAccessory",
              "earAccessory"]                    # draw order on equal depth (the skin first, accessories last)
# box faces front / back / left / right / top / bottom: corner templates TL, TR, BL on a +-1 box seen from outside + the 2 size axes
HEAD_FACES = [(((-1, 1, 1), (1, 1, 1), (-1, -1, 1)), (0, 1)), (((1, 1, -1), (-1, 1, -1), (1, -1, -1)), (0, 1)),
              (((1, 1, 1), (1, 1, -1), (1, -1, 1)), (2, 1)), (((-1, 1, -1), (-1, 1, 1), (-1, -1, -1)), (2, 1)),
              (((-1, 1, -1), (1, 1, -1), (-1, 1, 1)), (0, 2)), (((-1, -1, 1), (1, -1, 1), (-1, -1, -1)), (0, 2))]
HEAD_PX = 128                                    # the head picture (shown at 256 / 64 / 32 UI px on the h1c page)
HEAD_VIEW = (-26.0, 26.0, -20.0, 34.0, 34.0)     # the view = the faces' bounds clamped to x / y (head units, y up), at least 34 wide

# ================================================================= colours (data colours of our art + the probe texts; lint: UI_DATA_COLORS)
TREE_COLOR = dict((t, SUI.TREE_COLOR[t]) for t in ("Mining", "Foraging", "Farming", "Fishing"))
ART = {"gold": "#E8A93B", "goldLight": "#ffd36b", "cyan": "#d6f1ff", "green": "#7ee08a", "dim": "#7f93a6", "red": "#ff7a7a",  # ui-data
       "labelBar": "#4274a5(0.9)", "white": "#f4f8ff", "skyTop": "#5b9fe0", "skyBot": "#bfe3ff", "grass": "#5fae4a",  # ui-data
       "rock": "#8a7a66", "rockDark": "#5d5145", "portal": "#7d5cff", "portalCore": "#c9b8ff", "coin": "#f2c14e", "coinDark": "#b8862b",  # ui-data
       "wood": "#9a6a3c", "woodDark": "#6b4524", "iron": "#9aa6b2", "ironDark": "#5c6670", "cloth": "#c0392b", "clothDark": "#7d2419",  # ui-data
       "bag": "#b08850", "bagDark": "#7a5a30", "hudBg": "#000000(0.35)", "trailDotA": "#ffcf4a", "trailDotB": "#ffd36b"}  # ui-data
FEED_COL = {"gold": "#e8c25a", "green": "#7ee08a", "dim": "#7f93a6", "white": "#ffffff"}   # ui-data - F1 / F2 card spans (Style Guide 15 colour code)
H1_PAL = ["#3f7fbf", "#bf5f3f", "#4f9f5f", "#8f5fbf", "#bf9f3f", "#3f9f9f"]               # ui-data - the H1 runtime picture colours
UI_DATA_COLORS = list(TREE_COLOR.values()) + list(ART.values()) + list(FEED_COL.values()) + H1_PAL
GATHERING = ("Mining", "Foraging", "Farming", "Fishing")
MOTTO = {"Mining": "dig - smelt - prosper", "Foraging": "fell - gather - replant", "Farming": "sow - tend - harvest",
         "Fishing": "cast - reel - land"}
ICONS = {"Mining": ["Tool_Pickaxe_Iron", "Ore_Copper", "Ore_Cobalt"], "Foraging": ["Tool_Hatchet_Iron", "Tool_Hatchet_Copper", "Tool_Hatchet_Crude"],
         "Farming": ["Tool_Hoe_Iron", "Plant_Crop_Wheat_Item", "Plant_Seeds_Wheat"], "Fishing": ["Fish_Bluegill_Item", "Fish_Catfish_Item"]}
HUB_ICON = {"Mining": "Tool_Pickaxe_Iron", "Foraging": "Tool_Hatchet_Iron", "Farming": "Tool_Hoe_Iron", "Fishing": "Fish_Bluegill_Item"}
FIXTURE = {"Mining": 19, "Foraging": 8, "Farming": 3, "Fishing": 0}  # the mid-progress player of the map pages (points per tree)
FEED_ICONS = ("Tool_Pickaxe_Iron", "Ore_Copper")                  # F1 card icons (vanilla items, checked below)
# the 5 x 7 pixel glyphs of the H1a / H1b initials picture (our own pixel font: capitals, digits, "?" for anything else)
FONT5X7 = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10011 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    "?": "01110 10001 00001 00010 00100 00000 00100",
}


def rgb(h):
    return SM.rgb(h)


# ================================================================= 1. THE MAP (tools/skyymap.py: the 0.7.1 parameters, 100 % + 200 %)
TREES = dict((n, TD.tree(n)) for n in GATHERING)
GROUPS = [(n, TREE_COLOR[n], TREES[n]["branches"]) for n in GATHERING]
LAY = SM.build(GROUPS, node=32, ring0=0.46, s=40.0, emb=96, hub=44, want_ids=SM.want_of(GROUPS), what="Gathering")
LAY2 = SM.scaled(LAY, 2.0, what="Gathering")
W, H = LAY["W"], LAY["H"]
W2, H2 = LAY2["W"], LAY2["H"]
NODES, NODES2 = LAY["nodes"], LAY2["nodes"]
assert [n["id"] for n in NODES] == [n["id"] for n in NODES2]
print("layout: Gathering %d nodes at 100 %% (min gap %.2f px) and 200 %% (%d x %d), %d edges" % (
    len(NODES), LAY["info"]["min_gap"], W2, H2, len(LAY["edges"])))


def fixture_ranks():
    ranks = {}
    for t in GATHERING:
        left, spent = FIXTURE[t], 0
        rows = max(len(b["rows"]) for b in TREES[t]["branches"])
        for ri in range(rows):
            for bi, b in enumerate(TREES[t]["branches"]):
                if ri >= len(b["rows"]) or b["rows"][ri]["gate"] > spent:
                    continue
                for u in b["rows"][ri]["ups"]:
                    give = min(u["max"], 2, left)
                    if give > 0:
                        ranks[(t, bi, ri, u["id"])] = give
                        left -= give
                        spent += give
        assert left == 0, "fixture %s: %d points left over" % (t, left)
    return ranks


RANKS = fixture_ranks()
SPENT = dict((t, sum(v for k, v in RANKS.items() if k[0] == t)) for t in GATHERING)


def row_open(t, bi, ri):
    return TREES[t]["branches"][bi]["rows"][ri]["gate"] <= SPENT[t]


def up_of(nid):
    t, bi, ri, uid = nid
    row = TREES[t]["branches"][bi]["rows"][ri]
    if uid == "free":
        return None, row
    return [u for u in row["ups"] if u["id"] == uid][0], row


def state_of(n):
    """the node's picture name (skyymap.state_name) for the fixture player"""
    t, bi, ri, uid = n["id"]
    u, row = up_of(n["id"])
    opened = row_open(t, bi, ri)
    if u is None:
        return SM.state_name("free", TREE_COLOR[t], False, 0, 1, 1 if opened else 0)
    k = RANKS.get(n["id"], 0)
    return SM.state_name("up", TREE_COLOR[t], bool(row.get("cap")), k, u["max"], 1 if opened else 0)


def alt_of(n):
    """the M8a swap picture: the node's fully learnt look"""
    t, bi, ri, uid = n["id"]
    u, row = up_of(n["id"])
    if u is None:
        return SM.state_name("free", TREE_COLOR[t], False, 0, 1, 1)
    return SM.state_name("up", TREE_COLOR[t], bool(row.get("cap")), u["max"], u["max"], 3)


def edge_lit(e):
    a, b, kind, ri = e
    if kind == "spine":
        return a[0] == "hub" or row_open(b[0], b[1], b[2])
    return RANKS.get(b, 0) >= 1


# ================================================================= 2. PICTURES (skyymap's own art + ours; deterministic PNG bytes)
ASSETS = {}            # jar path -> bytes
TEXPATH = {}           # picture key -> markup path (no @2x)


def ship(key, pic, folder=MAP_DIR):
    data = SM.png(pic)
    w, h = SM.png_size(data)
    assert w % 2 == 0 and h % 2 == 0, key
    name = key.rsplit("/", 1)[-1]
    assert "_" not in key and re.fullmatch(r"[A-Za-z0-9/]+", key), key
    jp = TEX_ROOT + folder + key + "@2x.png"
    assert jp not in ASSETS, key
    ASSETS[jp] = data
    TEXPATH[key] = folder + key + ".png"
    return TEXPATH[key]


MAXES = sorted(set(u["max"] for t in GATHERING for b in TREES[t]["branches"] for r in b["rows"] for u in r["ups"]))
for nm, pic in sorted(SM.node_pictures(list(TREE_COLOR.values()), MAXES).items()):
    ship("Node/" + nm, pic)
for t in GATHERING:
    ship("Hub" + t, SM.hub_picture(TREE_COLOR[t]))
ship("Halo", SM.halo_picture())
ship("Emblem", SM.emblem_picture())
ship("Base", SM.base_picture(LAY))
EDGE_BOX = SM.edge_boxes(LAY)
EDGE_BOX2 = SM.scaled_boxes(EDGE_BOX, 2.0, W2, H2)
for k, g in SM.gold_pictures(LAY).items():
    ship("Edge/E%d" % k, g)
LIT = [k for k, e in enumerate(LAY["edges"]) if edge_lit(e) and k in EDGE_BOX]
for n in NODES:
    assert ("Node/" + state_of(n)) in TEXPATH and ("Node/" + alt_of(n)) in TEXPATH, n["id"]
# M4 (0.7.1's): five Mining states at 64 UI (128 px @2x) + a 1x copy of each (64 px) under the same name without @2x
M4_STATES = [("locked", (0, 0), "Locked"), ("ready", (0, 0), "Ready - can learn now"), ("learnt", (3, 1), "Learnt 1 / 3"),
             ("learnt", (3, 2), "Learnt 2 / 3"), ("max", (3, 3), "Max rank 3 / 3")]
for i, (st, km, _cap) in enumerate(M4_STATES):
    ship("Asset/S%d" % i, SM.node_picture(128, st, TREE_COLOR["Mining"], km))
    ASSETS[TEX_ROOT + MAP_DIR + "Asset/S%d.png" % i] = SM.png(SM.node_picture(64, st, TREE_COLOR["Mining"], km))
M4_PATH_2X = [ASSET_NAME_ROOT + MAP_DIR + "Asset/S%d@2x.png" % i for i in range(len(M4_STATES))]
M4_PATH_1X = [ASSET_NAME_ROOT + MAP_DIR + "Asset/S%d.png" % i for i in range(len(M4_STATES))]
for p_ in M4_PATH_2X + M4_PATH_1X:
    assert "Common/" + p_ in ASSETS, p_
# the placeholder of the runtime-picture AssetImages (h1a / h1b / h1c) until the runtime path is b.set in the same packet
PLACEHOLDER = ASSET_NAME_ROOT + MAP_DIR + "Asset/S0@2x.png"


# ---- T1: draft tiles (232 x 232 = 116 UI @2x), our own painted-look scenes from polygons (skywynn-art does the real sheet in R5)
def vgrad(pic, top, bot, y0=0, y1=None):
    y1 = pic.h if y1 is None else y1
    for y in range(y0, y1):
        f = (y - y0) / float(max(1, y1 - y0 - 1))
        c = tuple(int(round(top[i] + (bot[i] - top[i]) * f)) for i in range(3))
        for x in range(pic.w):
            pic.blend(x, y, c, 1.0)


def cloud(pic, x, y, s):
    for dx, dy, r in ((0, 0, 1.0), (1.1, 0.2, 0.8), (-1.0, 0.3, 0.7), (0.4, -0.5, 0.75)):
        SM.disc(pic, x + dx * s, y + dy * s, r * s, rgb(ART["white"]), 0.85)


def island(pic, cx, cy, w):
    g, r, rd = rgb(ART["grass"]), rgb(ART["rock"]), rgb(ART["rockDark"])
    SM.poly(pic, [(cx - w, cy), (cx + w, cy), (cx + w * 0.55, cy + w * 0.55), (cx + w * 0.1, cy + w * 0.95), (cx - w * 0.35, cy + w * 0.6)], r, 1.0, ss=2)
    SM.poly(pic, [(cx + w * 0.1, cy + w * 0.95), (cx + w * 0.55, cy + w * 0.55), (cx + w, cy), (cx + w * 0.3, cy + w * 0.3)], rd, 1.0, ss=2)
    SM.poly(pic, [(cx - w * 1.04, cy - w * 0.12), (cx + w * 1.04, cy - w * 0.12), (cx + w, cy + w * 0.08), (cx - w, cy + w * 0.08)], g, 1.0, ss=2)


def tile_teleport(S):
    pic = SM.Pic(S, S)
    vgrad(pic, rgb(ART["skyTop"]), rgb(ART["skyBot"]))
    k = S / 232.0
    cloud(pic, 40 * k, 50 * k, 16 * k)
    cloud(pic, 190 * k, 70 * k, 12 * k)
    island(pic, 116 * k, 160 * k, 80 * k)
    SM.ring(pic, 116 * k, 104 * k, 30 * k, 42 * k, rgb(ART["iron"]), 1.0)
    SM.disc(pic, 116 * k, 104 * k, 30 * k, rgb(ART["portal"]), 0.95)
    SM.disc(pic, 116 * k, 104 * k, 16 * k, rgb(ART["portalCore"]), 0.9)
    SM.poly(pic, SM.star(116 * k, 104 * k, 10 * k, inner=0.35, n=4), rgb(ART["white"]), 0.9, ss=2)
    return pic


def tile_market(S):
    pic = SM.Pic(S, S)
    vgrad(pic, rgb(ART["skyTop"]), rgb(ART["skyBot"]))
    k = S / 232.0
    SM.poly(pic, [(30 * k, 150 * k), (202 * k, 150 * k), (202 * k, 200 * k), (30 * k, 200 * k)], rgb(ART["wood"]), 1.0, ss=2)
    SM.poly(pic, [(30 * k, 196 * k), (202 * k, 196 * k), (202 * k, 206 * k), (30 * k, 206 * k)], rgb(ART["woodDark"]), 1.0, ss=2)
    for i in range(5):                                   # the striped awning
        x0 = 22 * k + i * 37.6 * k
        SM.poly(pic, [(x0, 60 * k), (x0 + 37.6 * k, 60 * k), (x0 + 37.6 * k, 92 * k), (x0, 92 * k)],
                rgb(ART["cloth"] if i % 2 == 0 else ART["white"]), 1.0, ss=2)
    SM.poly(pic, [(38 * k, 92 * k), (46 * k, 92 * k), (46 * k, 150 * k), (38 * k, 150 * k)], rgb(ART["woodDark"]), 1.0, ss=2)
    SM.poly(pic, [(186 * k, 92 * k), (194 * k, 92 * k), (194 * k, 150 * k), (186 * k, 150 * k)], rgb(ART["woodDark"]), 1.0, ss=2)
    for i, (x, y) in enumerate(((90, 140), (112, 136), (134, 140), (101, 126), (123, 126), (112, 116))):
        SM.disc(pic, x * k, y * k, 13 * k, rgb(ART["coinDark"]), 1.0)
        SM.disc(pic, x * k, (y - 2) * k, 11 * k, rgb(ART["coin"]), 1.0)
    return pic


def tile_crafting(S):
    pic = SM.Pic(S, S)
    vgrad(pic, rgb(ART["woodDark"]), rgb(ART["wood"]))
    k = S / 232.0
    SM.poly(pic, [(46 * k, 96 * k), (186 * k, 96 * k), (168 * k, 124 * k), (64 * k, 124 * k)], rgb(ART["iron"]), 1.0, ss=2)
    SM.poly(pic, [(20 * k, 96 * k), (46 * k, 96 * k), (64 * k, 112 * k), (36 * k, 110 * k)], rgb(ART["iron"]), 1.0, ss=2)
    SM.poly(pic, [(92 * k, 124 * k), (140 * k, 124 * k), (150 * k, 168 * k), (82 * k, 168 * k)], rgb(ART["ironDark"]), 1.0, ss=2)
    SM.poly(pic, [(66 * k, 168 * k), (166 * k, 168 * k), (166 * k, 186 * k), (66 * k, 186 * k)], rgb(ART["ironDark"]), 1.0, ss=2)
    SM.poly(pic, [(120 * k, 40 * k), (176 * k, 40 * k), (176 * k, 60 * k), (120 * k, 60 * k)], rgb(ART["iron"]), 1.0, ss=2)
    SM.poly(pic, [(144 * k, 60 * k), (152 * k, 60 * k), (152 * k, 92 * k), (144 * k, 92 * k)], rgb(ART["wood"]), 1.0, ss=2)
    SM.poly(pic, SM.star(100 * k, 84 * k, 12 * k, inner=0.3, n=4), rgb(ART["goldLight"]), 1.0, ss=2)
    return pic


def tile_storage(S):
    pic = SM.Pic(S, S)
    vgrad(pic, rgb(ART["skyBot"]), rgb(ART["skyTop"]))
    k = S / 232.0
    for cx, cy, r in ((80, 150, 46), (150, 140, 54)):
        SM.disc(pic, cx * k, cy * k, r * k, rgb(ART["bagDark"]), 1.0)
        SM.disc(pic, (cx - 4) * k, (cy - 4) * k, (r - 6) * k, rgb(ART["bag"]), 1.0)
        SM.poly(pic, [((cx - 14) * k, (cy - r - 4) * k), ((cx + 14) * k, (cy - r - 4) * k), ((cx + 8) * k, (cy - r + 12) * k),
                      ((cx - 8) * k, (cy - r + 12) * k)], rgb(ART["bagDark"]), 1.0, ss=2)
        SM.ring(pic, cx * k, (cy - r + 10) * k, 4 * k, 7 * k, rgb(ART["gold"]), 1.0)
    SM.disc(pic, 150 * k, 146 * k, 12 * k, rgb(ART["coin"]), 1.0)
    return pic


def edge_pic(S):
    """the gold hover edge: transparent with a 4 px (@2x) gold border (a 9-slice patch, Border 4)"""
    pic = SM.Pic(S, S)
    g = rgb(ART["gold"])
    for y in range(S):
        for x in range(S):
            if x < 4 or y < 4 or x >= S - 4 or y >= S - 4:
                pic.blend(x, y, g, 1.0)
    return pic


TILES = [("Teleport", tile_teleport), ("Market", tile_market), ("Crafting", tile_crafting), ("Storage", tile_storage)]
for nm, fn in TILES:
    ship(nm, fn(232), TILE_DIR)
ship("Big", tile_teleport(292), TILE_DIR)                  # the 150 px tile (146 UI @2x)
ship("Edge", edge_pic(32), TILE_DIR)


# ---- G1: trail A's dot (64 px, a soft gold disc with a bright core) at the particle texture path other mods use
def dot_pic():
    pic = SM.Pic(64, 64)
    SM.disc(pic, 32, 32, 30, rgb(ART["trailDotA"]), 0.35)
    SM.disc(pic, 32, 32, 22, rgb(ART["trailDotA"]), 0.9)
    SM.disc(pic, 32, 32, 12, rgb(ART["white"]), 0.95)
    return pic


ASSETS["Common/" + DOT_TEX] = SM.png(dot_pic())


def spawner(texture, colour, blend, scale, life=1.1):
    """one billboard particle that sits still and fades in / out (shaped like the vanilla Gobliterator glow spawner, trimmed)"""
    return {"RenderMode": blend, "ParticleRotationInfluence": "Billboard", "ParticleLifeSpan": {"Min": life, "Max": life},
            "TrailSpawnerPositionMultiplier": 0, "TrailSpawnerRotationMultiplier": 0,
            "Particle": {"Texture": texture, "ScaleRatioConstraint": "None",
                         "Animation": {"0": {"Opacity": 0, "Color": colour}, "20": {"Opacity": 1}, "75": {"Opacity": 1},
                                       "100": {"Opacity": 0, "Color": colour}},
                         "InitialAnimationFrame": {"Opacity": 0, "Scale": {"X": {"Min": scale, "Max": scale}, "Y": {"Min": scale, "Max": scale}}}},
            "SpawnRate": {"Min": 1, "Max": 1}, "MaxConcurrentParticles": 1, "ParticleRotateWithSpawner": True, "SpawnBurst": True,
            "TotalParticles": {"Min": 1, "Max": 1}, "LinearFiltering": True}


PSYS = {"SkyyUiProbe_TrailA": [{"SpawnerId": "SkyyUiProbe_TrailA_Dot"}],
        "SkyyUiProbe_TrailB": [{"SpawnerId": "SkyyUiProbe_TrailB_Dot"}],
        # C: ONE system, 6 dots along its local -Z (1.5 .. 9 blocks), staggered - spawned with a Rotation3f yaw toward the target
        "SkyyUiProbe_TrailC": [{"SpawnerId": "SkyyUiProbe_TrailB_Dot", "PositionOffset": {"Z": -1.5 * (i + 1)}, "StartDelay": round(0.08 * i, 2)}
                               for i in range(6)]}
PSPAWN = {"SkyyUiProbe_TrailA_Dot": spawner(DOT_TEX, ART["trailDotA"], "BlendLinear", 0.35),
          "SkyyUiProbe_TrailB_Dot": spawner(GLOW_TEX, ART["trailDotB"], "BlendAdd", 0.5)}
for sid, spl in PSYS.items():
    ASSETS[PART_DIR + sid + ".particlesystem"] = json.dumps({"Spawners": spl, "CullDistance": 64.0, "IsImportant": False}, indent=2).encode("utf-8")
for sid, sp in PSPAWN.items():
    ASSETS[PART_DIR + "Spawners/" + sid + ".particlespawner"] = json.dumps(sp, indent=2).encode("utf-8")
with zipfile.ZipFile(serverjar.assets_zip()) as _az:
    _azn = set(_az.namelist())
    assert "Common/" + GLOW_TEX in _azn, GLOW_TEX
    assert not any(n.startswith(PART_DIR) or n.startswith("Common/Particles/Textures/SkyyUiProbe/") for n in _azn), "our particle folder in Assets.zip"
    _vanilla_spawn = set(os.path.basename(n).rsplit(".", 1)[0] for n in _azn if n.endswith((".particlespawner", ".particlesystem")))
    assert not (set(PSYS) | set(PSPAWN)) & _vanilla_spawn, "a particle id clashes with a vanilla one"
    _keys = set()
    for n in _azn:                                         # every key our spawner uses appears in some vanilla spawner (the codec knows it)
        if n.endswith(".particlespawner") and len(_keys) < 40:
            _keys |= set(json.loads(_az.read(n).decode("utf-8-sig")))
    for sp in PSPAWN.values():
        assert set(sp) <= _keys | {"LinearFiltering", "SpawnBurst", "TotalParticles"}, set(sp) - _keys
print("pictures: %d files, %d KB, %.1f s" % (len(ASSETS), sum(len(v) for v in ASSETS.values()) // 1024, time.time() - T0))

# ================================================================= 3. THE PAGES (markup data; kit blocks + raw map elements)
SUI.verify(assets_zip=serverjar.assets_zip(), quiet=True)
SUI.register_map_textures([v for k, v in TEXPATH.items() if v.startswith(MAP_DIR)])
with zipfile.ZipFile(serverjar.assets_zip()) as _az:
    _vanilla_items = set(n.rsplit("/", 1)[-1][:-5] for n in _az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    assert not any(n.startswith(TEX_ROOT + "SkyyUiProbe/") for n in _az.namelist()), "our texture folder exists in Assets.zip"
for _ids in list(ICONS.values()) + [list(HUB_ICON.values()), list(FEED_ICONS)]:
    for _i in _ids:
        assert _i in _vanilla_items, "icon %s is not a vanilla item" % _i
# 0.9 tip probe (Price-Tooltips-Spec R0): the probe item + the P1 / P5 example ids are vanilla items
TIP_ITEM = "Weapon_Claws_Tribal"          # NOT a sword: SkyyGear GearView re-stamps Weapon_* gear with its own ItemDisplayMetadata
TIP_KEY = "server.skyy.probe.tip"         # the translation child of the probe item (only this jar names it; never in a lang file)
TIP_LATER_MS = 5000
for _i in (TIP_ITEM, "Wood_Oak_Trunk", "Plant_Crop_Wheat_Item"):
    assert _i in _vanilla_items, "tip probe: %s is not a vanilla item" % _i

CASES = [  # key, name, title line, what to look at (the page shows both; the chat repeats WHAT)
    ("m4", "map-assetimage", "PROBE M4 - map-assetimage: swap a disc picture without a rebuild (retest)",
     "Skyy: look - press Next state 5 times: which of the 3 discs at the right change picture each time? Any empty disc or Loading?"),
    ("m5", "map-anchor", "PROBE M5 - map-anchor: move the cyan halo with one Anchor update (retest)",
     "Skyy: look - click 5 nodes: does the cyan ring jump to each one, with nothing else flickering?"),
    ("m6", "map-tooltip", "PROBE M6 - map-tooltip: hover text on 3 node discs (retest)",
     "Skyy: look - hover the 3 discs at the right: does a tooltip show the name and rank? Then press Next case while one shows."),
    ("m8a", "keep-scroll", "PROBE M8a - keep-scroll: the map at 200 percent, clicks answer without a rebuild",
     "Skyy: look - scroll to the FAR bottom-right, click 3 nodes there: did the view stay put? Halo, node picture and the disc changed?"),
    ("m8b", "clip-pan", "PROBE M8b - clip-pan: the 200 percent map in a plain box, moved by buttons",
     "Skyy: look - press Left / Right / Up / Down / Centre: does the map move? Anything drawn outside the box? Rebuild keeps the view?"),
    ("m8c", "pan-in-scroll", "PROBE M8c - pan-in-scroll (learn): the same move inside the scroll box",
     "Skyy: look - press the move buttons, then use the mouse wheel / scrollbars: does the wheel still pan? Does the box clip?"),
    ("h1a", "head-before-open", "PROBE H1a - a picture made at run time, sent BEFORE this page was sent",
     "Skyy: look - do you see a coloured square with your initials at the right? (no empty box, no missing-texture look)"),
    ("h1b", "head-while-open", "PROBE H1b - a NEW picture sent while the page is open",
     "Skyy: look - press Send a new picture 3 times: does the square change colour each time, without flicker or Loading?"),
    ("h1c", "your-head", "PROBE H1c - your head, drawn by the server from your skin and the game files",
     "Skyy: look - is that you, hair included? Send a screenshot. Your 20 skin parts are in chat and the log."),
    ("d1", "dialogue-bar", "PROBE D1 - the NPC dialogue bar at the bottom of the screen",
     "Skyy: look - is the world visible above the bar (no dark screen)? Skip / Next / Accept work, each click answers once, Esc closes?"),
    ("t1", "picture-tiles", "PROBE T1 - picture tiles for the SkyWynn Menu (draft art)",
     "Skyy: look - are the tiles crisp, the labels readable, the gold edge on hover? Send a screenshot."),
    ("k1", "key-hints", "PROBE K1 - key hints: the vanilla ability boxes bottom right",
     "Skyy: look - press Close and look, then with a class and 2 abilities on: do the bottom-right boxes show Mouse 5 / Q / E with OUR icons?"),
    ("f1", "vanilla-feed", "PROBE F1 - our cards in the vanilla pickup feed",
     "Skyy: look - press Close and run feed test: 9 cards come bottom right. Readable? Colours show? Pick an item up too. Screenshot."),
    ("f2", "feed-tag", "PROBE F2 - one card that counts up (same tag)",
     "Skyy: look - press Close and run tag test: 5 XP cards with the same tag. Did ONE card update, or did FIVE cards stack?"),
    ("g1", "ground-trail", "PROBE G1 - the quest guide trail (particles only you see)",
     "Skyy: look - press Close and run trail test, then walk: which trail reads best (A, B or C)? Does C point at the target?"),
]
CASE_KEYS = [c[0] for c in CASES]
CASE_NAME = dict((c[0], c[1]) for c in CASES)
MAP_CASES = ("m4", "m5", "m6", "m8a", "m8b", "m8c")
RUN_CASES = {"k1": "Close and look", "f1": "Close and run feed test", "f2": "Close and run tag test", "g1": "Close and run trail test"}
PAGE_W, PAGE_H = 1600, 980
RAIL_W, CV_W, PANEL_W, MAIN_H = 232, W, 456, H
NAV_H = SUI.BTN_SMALL_H + 6
WHAT_H = 48


def raw_group(ident, l, t, w, h, tex=None, extra=""):
    bg = (' Background: "%s";' % tex) if tex else ""
    return "Group #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d);%s%s }" % (ident, l, t, w, h, bg, extra)


def hit_button(ident, l, t, s, tip=None):
    tt = (" " + SUI.tooltip(tip, trial=True)) if tip else ""
    return ("Button #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); Style: ButtonStyle(Hovered: (Background: %s));%s }"
            % (ident, l, t, s, s, SUI.COLOR["hover"], tt))


def node_label(n):
    t, bi, ri, uid = n["id"]
    u, row = up_of(n["id"])
    b = TREES[t]["branches"][bi]
    nm = row["free"]["name"] if u is None else u["name"]
    rank = "free perk" if u is None else "Rank %d / %d" % (RANKS.get(n["id"], 0), u["max"])
    return "%s - %s - Row %d - %s (%s)" % (t, b["name"], ri + 1, nm, rank)


def canvas(ap, parent, lay, boxes, halo_k=None, alt=False):
    """the map: base picture, lit gold edges, emblem, hubs, banners, halo, nodes (picture, [alt picture hidden], icon, hit box)"""
    z = float(lay.get("zoom", 1.0))
    ap.append((parent, raw_group(P + "Bs", 0, 0, lay["W"], lay["H"], TEXPATH["Base"])))
    for k in LIT:
        l, t, w_, h_ = boxes[k]
        ap.append((parent, raw_group(P + "E%d" % k, l, t, w_, h_, TEXPATH["Edge/E%d" % k])))
    ap.append((parent, raw_group(P + "Emb", lay["emb_l"], lay["emb_t"], lay["emb"], lay["emb"], TEXPATH["Emblem"])))
    for i, h in enumerate(lay["hubs"]):
        hs = lay["hub"]
        ap.append((parent, raw_group(P + "H%d" % i, h["l"], h["t"], hs, hs, TEXPATH["Hub" + h["key"]])))
        isz = int(round(hs * SUI.MAP_HUB_ICON_FRAC))
        ap.append(("#" + P + "H%d" % i, SUI.item_icon(P + "H%dI" % i, HUB_ICON[h["key"]], size=isz,
                                                       anchor={"left": (hs - isz) // 2, "top": (hs - isz) // 2})))
    for i, b in enumerate(lay["banners"]):
        ap.append((parent, SUI.label(P + "Bn%dA" % i, b["key"].upper(), "default", size=15, bold=True, col=TREE_COLOR[b["key"]],
                                     w=b["w"], h=22, align=b["align"], anchor={"left": b["l"], "top": b["t"]})))
        ap.append((parent, SUI.label(P + "Bn%dB" % i, MOTTO[b["key"]], "caption", size=14, w=b["w"], h=20, align=b["align"],
                                     anchor={"left": b["l"], "top": b["t"] + 22})))
    if halo_k is not None:
        n = lay["nodes"][halo_k]
        hz = int(round(SUI.MAP_HALO * z))
        ap.append((parent, raw_group(P + "Sel", int(round(n["cx"] - hz / 2.0)), int(round(n["cy"] - hz / 2.0)), hz, hz, TEXPATH["Halo"])))
    for k, n in enumerate(lay["nodes"]):
        t, bi, ri, uid = n["id"]
        s = n["size"]
        nid = P + "N%d" % k
        ap.append((parent, raw_group(nid, n["l"], n["t"], s, s, TEXPATH["Node/" + state_of(LAY["nodes"][k])])))
        if alt:
            ap.append(("#" + nid, raw_group(nid + "V", 0, 0, s, s, TEXPATH["Node/" + alt_of(LAY["nodes"][k])], extra=" Visible: false;")))
        if n["kind"] == "up":
            ic = int(round(s * SUI.MAP_ICON_FRAC))
            ap.append(("#" + nid, SUI.item_icon(nid + "I", ICONS[t][bi % len(ICONS[t])], size=ic,
                                                anchor={"left": (s - ic) // 2, "top": (s - ic) // 2})))
        hs = int(round(s * SUI.HIT_NUM_MAP / float(SUI.HIT_DEN_MAP)))
        ho = (s - hs) // 2
        ap.append(("#" + nid, hit_button(nid + "B", ho, ho, hs)))


def rail(ap, parent):
    """the left rail stub (0.7.1's): 5 page rows (28) + 13 tree rows (42) + the legend (4 x 21) = 770 of 774"""
    pages = [("Gathering", [("Mining", 23, 4), ("Foraging", 11, 3), ("Farming", 7, 4), ("Fishing", 3, 3)]),
             ("Crafting", [("Smithing", 5, 5), ("Cooking", 9, 2), ("Alchemy", 2, 2)]),
             ("Adventure", [("Combat", 14, 6), ("Acrobatics", 4, 4), ("Exploration", 6, 6), ("Beastmastery", 0, 0)]),
             ("Class", [("Warrior", 12, 1)]), ("Rebirth Nexus", [("Void", 0, 0)])]
    used, i = 0, 0
    for pi, (pg, trees) in enumerate(pages):
        rid = P + "Rp%d" % pi
        ap.append((parent, SUI.hover_row(rid, "selected" if pi == 0 else "normal", h=28, pad=0, w=RAIL_W)))
        ap.append(("#" + rid, SUI.label(P + "Rp%dL" % pi, pg, "section", h=28, w=RAIL_W - 8, anchor={"left": 8})))
        used += 28
        for t, lv, pts in trees:
            tid = P + "Rt%d" % i
            ap.append((parent, SUI.hover_row(tid, "selected" if t == "Mining" else "normal", h=42, pad=0, w=RAIL_W)))
            ap.append(("#" + tid, SUI.item_icon(P + "Rt%dI" % i, HUB_ICON.get(t, "Tool_Pickaxe_Iron"), size=24,
                                                anchor={"left": 10, "right": 8})))
            ap.append(("#" + tid, SUI.group(P + "Rt%dC" % i, layout="Top", w=RAIL_W - 50, h=42)))
            ap.append(("#" + P + "Rt%dC" % i, SUI.label(P + "Rt%dN" % i, t, "default", size=15, bold=True,
                                                        col=SUI.TREE_COLOR.get(t, "rowName"), h=22, w=RAIL_W - 50)))
            ap.append(("#" + P + "Rt%dC" % i, SUI.label(P + "Rt%dS" % i, "Lv %d - %d points" % (lv, pts), "rowSub", size=13, h=18,
                                                        w=RAIL_W - 50)))
            used += 42
            i += 1
    for li, (pic, cap) in enumerate((("Node/" + SM.colour_name(TREE_COLOR["Mining"]) + "L13", "learnt - ring in the tree colour"),
                                     ("Node/Ready", "ready - gold ring"), ("Node/Locked", "locked - grey with a padlock"),
                                     ("Halo", "selected - cyan halo"))):
        lid = P + "Lg%d" % li
        ap.append((parent, SUI.group(lid, layout="Left", w=RAIL_W, h=21)))
        ap.append(("#" + lid, 'Group #%s { Anchor: (Width: 20, Height: 20, Right: 6); Background: "%s"; }' % (P + "Lg%dP" % li, TEXPATH[pic])))
        ap.append(("#" + lid, SUI.label(P + "Lg%dT" % li, cap, "caption", size=13, h=20, w=RAIL_W - 26)))
        used += 21
    assert i == 13 and used <= MAIN_H, (i, used)


SEL0 = [k for k, n in enumerate(NODES) if RANKS.get(n["id"], 0) >= 1][0]      # the selected node of the stub panel (first learnt)


def panel(ap, parent):
    """the right panel stub: tree head + the talent detail; returns the height left for the case block"""
    n = NODES[SEL0]
    t, bi, ri, uid = n["id"]
    u, row = up_of(n["id"])
    br = TREES[t]["branches"][bi]
    inner = PANEL_W - 2 * 8
    hd = P + "Ph"
    ap.append((parent, SUI.group(hd, layout="Left", w=inner, h=64)))
    ap.append(("#" + hd, SUI.item_icon(P + "PhI", HUB_ICON[t], size=40, anchor={"top": 12, "right": 10})))
    ap.append(("#" + hd, SUI.group(P + "PhC", layout="Top", w=inner - 50, h=64)))
    ap.append(("#" + P + "PhC", SUI.label(P + "PhN", t.upper(), "heading", col=TREE_COLOR[t], h=30, w=inner - 50)))
    ap.text("#" + P + "PhC", P + "PhL", "Level 23 / 50  -  %d points spent" % SPENT[t], "default", size=15, h=24, w=inner - 50)
    ap.text(parent, P + "PhX", "XP 12,400 / 20,000 to level 24", "gold", size=15, h=22, w=inner)
    ap.text(parent, P + "TCap", "%s - %s - Row %d" % (t, br["name"], ri + 1), "caption", size=13, h=40, w=inner, wrap=True, max_lines=2)
    ap.text(parent, P + "TName", u["name"], "tipName", col=TREE_COLOR[t], h=28, w=inner)
    ap.text(parent, P + "TRank", "Rank %d / %d" % (RANKS.get(n["id"], 0), u["max"]), "gold", size=15, h=24, w=inner)
    ap.text(parent, P + "TText", u["text"], "default", size=15, h=22, w=inner)
    ap.append((parent, SUI.label(P + "TState", "Ready to unlock", "success", size=15, h=24, w=inner)))
    used = 64 + 22 + 40 + 28 + 24 + 22 + 24
    return MAIN_H - 2 * 8 - used


def head_rows(ap, body, iw, case):
    key, name, head, what = [c for c in CASES if c[0] == case][0]
    ci = CASE_KEYS.index(case)
    ap.text(body, P + "Head", head, "strong", size=17, h=28, w=iw)
    ap.text(body, P + "What", what, "default", size=15, h=WHAT_H, w=iw, wrap=True, max_lines=2)
    ap.append((body, SUI.group(P + "Nav", layout="Left", w=iw, h=NAV_H)))
    ap.append(("#" + P + "Nav", SUI.button(P + "Back", "Back", "secondary", "small", w=120, anchor={"right": 8})))
    ap.append(("#" + P + "Nav", SUI.button(P + "Next", "Next case", "primary", "small", w=160, anchor={"right": 12})))
    ap.text("#" + P + "Nav", P + "NavL", "Case %d of %d - %s %s" % (ci + 1, len(CASES), key.upper(), name), "gold", size=15,
            h=SUI.BTN_SMALL_H, w=iw - 120 - 8 - 160 - 12 - 120 - 18)
    ap.append(("#" + P + "Nav", SUI.button(P + "Close", "Close", "secondary", "small", w=120, sound="cancel", anchor={"left": 18})))
    ap.append((body, SUI.spacer(h=8)))
    return 28 + WHAT_H + NAV_H + 8


def map_page(case):
    sh = SUI.page_shell(P, PAGE_W, PAGE_H, "SkyyUiProbe %s - UI queue probe" % VERSION, kind="decorated")
    ap, body, iw = sh.appends, sh.body, sh.inner_w
    used_h = head_rows(ap, body, iw, case)
    ap.append((body, SUI.group(P + "Main", layout="Left", w=RAIL_W + 12 + CV_W + 12 + PANEL_W, h=MAIN_H)))
    SUI.fit([used_h + MAIN_H], sh.inner_h, "probe page body")
    ap.append(("#" + P + "Main", SUI.group(P + "Rail", layout="Top", w=RAIL_W, h=MAIN_H)))
    rail(ap, "#" + P + "Rail")
    ap.append(("#" + P + "Main", SUI.spacer(w=12)))
    if case in ("m8a", "m8c"):                     # the 2-axis scroll box of the zoomed map (kit 1.8 map_scroll, M7 proven)
        outer, inner_, cv = SUI.map_scroll(P + "Out", P + "In", P + "Cv", CV_W, MAIN_H, W2, H2)
        ap.append(("#" + P + "Main", outer))
        ap.append(("#" + P + "Out", inner_))
        ap.append(("#" + P + "In", cv))
        canvas(ap, "#" + P + "Cv", LAY2, EDGE_BOX2, halo_k=SEL0, alt=(case == "m8a"))
        if case == "m8a":                          # the AssetImage disc (M4's swap on a zoomed map), far bottom-right
            ap.append(("#" + P + "Cv", 'AssetImage #%s { Anchor: (Left: %d, Top: %d, Width: 64, Height: 64); AssetPath: "%s"; }'
                       % (P + "Ad", AD_L, AD_T, M4_PATH_2X[0])))
            ap.append(("#" + P + "Cv", SUI.label(P + "AdL", "AssetImage disc", "caption", size=13, w=140, h=20, align="Center",
                                                 anchor={"left": AD_L - 38, "top": AD_T + 66})))
    elif case == "m8b":                            # a plain clip box holding the whole 200 % map (moved by its Anchor)
        ap.append(("#" + P + "Main", "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P + "Clip", CV_W, MAIN_H,
                                                                                                        SUI.COLOR["well"])))
        ap.append(("#" + P + "Clip", "Group #%s { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); }" % (P + "Mp", W2, H2)))
        canvas(ap, "#" + P + "Mp", LAY2, EDGE_BOX2, halo_k=SEL0)
    else:
        ap.append(("#" + P + "Main", "Group #%s { Anchor: (Width: %d, Height: %d); Background: %s; }" % (P + "Cv", W, H, SUI.COLOR["well"])))
        canvas(ap, "#" + P + "Cv", LAY, EDGE_BOX, halo_k=SEL0)
    ap.append(("#" + P + "Main", SUI.spacer(w=12)))
    ap.append(("#" + P + "Main", SUI.panel(P + "Pn", "well", w=PANEL_W, h=MAIN_H)))
    pn = "#" + P + "Pn"
    left = panel(ap, pn)
    inner = PANEL_W - 16
    if case == "m4":                              # AssetImage @2x path / 1x path / the proven Background control
        ap.text(pn, P + "A4H", "AssetImage 2x path  |  AssetImage 1x path  |  control", "caption", size=13, h=20, w=inner)
        ap.append((pn, SUI.group(P + "A4", layout=None, w=inner, h=70)))
        ap.append(("#" + P + "A4", 'AssetImage #%s { Anchor: (Left: 30, Top: 3, Width: 64, Height: 64); AssetPath: "%s"; }'
                   % (P + "A1", M4_PATH_2X[0])))
        ap.append(("#" + P + "A4", 'AssetImage #%s { Anchor: (Left: 188, Top: 3, Width: 64, Height: 64); AssetPath: "%s"; }'
                   % (P + "A2", M4_PATH_1X[0])))
        ap.append(("#" + P + "A4", raw_group(P + "A3", 346, 3, 64, 64, TEXPATH["Asset/S0"])))
        ap.append((pn, SUI.group(P + "A4R", layout="Left", w=inner, h=SUI.BTN_SMALL_H + 4)))
        ap.append(("#" + P + "A4R", SUI.button(P + "A4N", "Next state", "secondary", "small", w=150, anchor={"right": 12})))
        ap.text("#" + P + "A4R", P + "A4S", "State 1 of 5 - " + M4_STATES[0][2], "default", size=15, h=SUI.BTN_SMALL_H, w=inner - 170)
        assert 20 + 70 + SUI.BTN_SMALL_H + 4 <= left
    if case == "m6":                              # 3 node discs with TooltipText (kit trial key "tooltip")
        ap.text(pn, P + "TtH", "Hover each disc - a tooltip should name it and its rank", "caption", size=13, h=20, w=inner)
        ap.append((pn, SUI.group(P + "Tt", layout=None, w=inner, h=50)))
        cn = SM.colour_name(TREE_COLOR["Mining"])
        for i, (nm, st) in enumerate((("Quick Swing - Rank 2 / 5", cn + "L25"), ("Rich Seams - Rank 0 / 3", "Ready"),
                                      ("Deep Veins - locked - Row 3", "Locked"))):
            gid = P + "Tt%d" % i
            ap.append(("#" + P + "Tt", raw_group(gid, 40 + i * 140, 3, 44, 44, TEXPATH["Node/" + st])))
            ap.append(("#" + gid, SUI.item_icon(gid + "I", "Tool_Pickaxe_Iron", size=24, anchor={"left": 10, "top": 10})))
            ap.append(("#" + gid, hit_button(gid + "B", 4, 4, 36, tip=nm)))
        assert 20 + 50 <= left
    if case in ("m8b", "m8c"):                    # the move buttons (Left / Right / Up / Down / Centre or Reset / Rebuild)
        ap.text(pn, P + "MvH", "Move the map %d px per click (the server keeps the offset)" % PAN_STEP, "caption", size=13, h=20, w=inner)
        bw = (inner - 2 * 8) // 3
        for r, row in enumerate(((("Left", "pan:left"), ("Up", "pan:up"), ("Right", "pan:right")),
                                 (("Down", "pan:down"), ("Centre" if case == "m8b" else "Reset", "pan:centre" if case == "m8b" else "pan:reset"),
                                  ("Rebuild", "pan:rebuild")))):
            rid = P + "Mv%d" % r
            ap.append((pn, SUI.group(rid, layout="Left", w=inner, h=SUI.BTN_SMALL_H + 6)))
            for j, (txt, _act) in enumerate(row):
                ap.append(("#" + rid, SUI.button(P + "Mv%d%d" % (r, j), txt, "secondary", "small", w=bw, anchor={"right": 8} if j < 2 else None)))
        ap.text(pn, P + "MvS", "Offset 0, 0", "gold", size=15, h=24, w=inner)
        assert 20 + 2 * (SUI.BTN_SMALL_H + 6) + 24 <= left
    if case == "m8a":
        ap.text(pn, P + "KsH", "Every node click: halo Anchor + 2 picture Visible flags + the disc AssetPath + 2 texts, ONE update", "caption",
                size=13, h=40, w=inner, wrap=True, max_lines=2)
    return sh


PAN_STEP = 210
AD_L, AD_T = W2 - 4 - 64 - 40, H2 - 4 - 44 - 130          # the M8a AssetImage disc: above the bottom-right banner
for n in NODES2:                                             # ... and clear of every node
    assert (n["l"] + n["size"] < AD_L - 40 or n["l"] > AD_L + 104 or n["t"] + n["size"] < AD_T or n["t"] > AD_T + 90), ("M8a disc on", n["id"])


def text_page(case):
    """the shell + header rows + a content panel (cases h1a / h1b / h1c / t1 / k1 / f1 / f2 / g1)"""
    sh = SUI.page_shell(P, PAGE_W, PAGE_H, "SkyyUiProbe %s - UI queue probe" % VERSION, kind="decorated")
    ap, body, iw = sh.appends, sh.body, sh.inner_w
    used_h = head_rows(ap, body, iw, case)
    ch = sh.inner_h - used_h
    ap.append((body, SUI.panel(P + "Pn", "well", w=iw, h=ch, layout="Top")))
    pn = "#" + P + "Pn"
    inner = iw - 16
    ap.text(pn, P + "TCap", "Waiting for your click", "caption", size=15, h=26, w=inner)      # the click answer line (say())
    used = 26
    if case in ("h1a", "h1b"):
        ap.append((pn, SUI.group(P + "Hr", layout="Left", w=inner, h=150)))
        ap.append(("#" + P + "Hr", SUI.panel(P + "HrF", "simple", w=150, h=150, layout=None)))
        ap.append(("#" + P + "HrF", 'AssetImage #%s { Anchor: (Left: 2, Top: 2, Width: 128, Height: 128); AssetPath: "%s"; }'
                   % (P + "Hp", PLACEHOLDER)))
        ap.append(("#" + P + "Hr", SUI.spacer(w=20)))
        ap.append(("#" + P + "Hr", SUI.group(P + "HrT", layout="Top", w=inner - 170, h=150)))
        ap.text("#" + P + "HrT", P + "HpN", "Picture: -", "gold", size=15, h=26, w=inner - 170)
        ap.text("#" + P + "HrT", P + "HpI", ("Sent to you as a runtime asset (AssetInitialize + AssetPart + AssetFinalize) BEFORE this case "
                                             "page was sent, then named in the AssetImage." if case == "h1a" else
                                             "Each click: a NEW picture (new name = its content hash) goes to you first, then ONE "
                                             "page update sets the AssetImage path. No rebuild."), "default", size=15, h=48,
                w=inner - 170, wrap=True, max_lines=2)
        if case == "h1b":
            ap.append(("#" + P + "HrT", SUI.button(P + "HbN", "Send a new picture", "primary", "normal", w=260)))
        used += 150
    if case == "h1c":
        ap.append((pn, SUI.group(P + "Hr", layout="Left", w=inner, h=300)))
        ap.append(("#" + P + "Hr", SUI.panel(P + "HcF", "simple", w=300, h=300, layout=None)))
        ap.append(("#" + P + "HcF", 'AssetImage #%s { Anchor: (Left: 6, Top: 6, Width: 256, Height: 256); AssetPath: "%s"; }'
                   % (P + "Hc", PLACEHOLDER)))
        ap.append(("#" + P + "Hr", SUI.spacer(w=16)))
        ap.append(("#" + P + "Hr", SUI.group(P + "HcS", layout="Top", w=180, h=300)))
        ap.text("#" + P + "HcS", P + "HcSz", "64 and 32 px", "caption", size=13, h=22, w=180)
        ap.append(("#" + P + "HcS", SUI.panel(P + "HcG", "simple", w=76, h=76, layout=None)))
        ap.append(("#" + P + "HcG", 'AssetImage #%s { Anchor: (Left: 2, Top: 2, Width: 64, Height: 64); AssetPath: "%s"; }'
                   % (P + "Hd", PLACEHOLDER)))
        ap.append(("#" + P + "HcS", SUI.spacer(h=8)))
        ap.append(("#" + P + "HcS", SUI.panel(P + "HcH", "simple", w=44, h=44, layout=None)))
        ap.append(("#" + P + "HcH", 'AssetImage #%s { Anchor: (Left: 2, Top: 2, Width: 32, Height: 32); AssetPath: "%s"; }'
                   % (P + "He", PLACEHOLDER)))
        ap.append(("#" + P + "Hr", SUI.spacer(w=16)))
        tw = inner - 300 - 16 - 180 - 16
        ap.append(("#" + P + "Hr", SUI.group(P + "HcT", layout="Top", w=tw, h=300)))
        ap.text("#" + P + "HcT", P + "HcN", "Head: not drawn yet", "gold", size=15, h=26, w=tw)
        for i in range(HEAD_ROWS):
            ap.text("#" + P + "HcT", P + "HcL%d" % i, "-", "default", size=14, h=22, w=tw)
        ap.append(("#" + P + "HcT", SUI.group(P + "HcB", layout="Left", w=tw, h=SUI.BTN_SMALL_H)))
        ap.append(("#" + P + "HcB", SUI.button(P + "HcR", "Redraw", "secondary", "small", w=150, anchor={"right": 8})))
        ap.append(("#" + P + "HcB", SUI.button(P + "HcP", "Parts to chat", "secondary", "small", w=180)))
        assert 26 + HEAD_ROWS * 22 + SUI.BTN_SMALL_H <= 300
        used += 300
    if case == "t1":
        ap.append((pn, SUI.group(P + "Tr", layout="Left", w=inner, h=170)))
        for i, (nm, _fn) in enumerate(TILES + [("Big", None)]):
            s = 150 if nm == "Big" else 120
            tid = P + "Tl%d" % i
            lab = "Teleport" if nm == "Big" else nm
            ap.append(("#" + P + "Tr", SUI.group(tid, layout=None, w=s, h=s, anchor={"right": 24, "top": 0 if s == 150 else 15})))
            ap.append(("#" + tid, raw_group(tid + "P", 2, 2, s - 4, s - 4, TEXPATH[nm])))
            ap.append(("#" + tid, raw_group(tid + "B", 2, s - 2 - 22, s - 4, 22, extra=" Background: %s;" % ART["labelBar"])))
            ap.append(("#" + tid + "B", SUI.label(tid + "L", lab, "default", size=15, bold=True, col="white", w=s - 4, h=22, align="Center",
                                                  font="Secondary")))
            ap.append(("#" + tid, 'Button #%s { Anchor: (Left: 0, Top: 0, Width: %d, Height: %d); Style: ButtonStyle(Hovered: '
                                  '(Background: (TexturePath: "%s", Border: 2))); }' % (tid + "H", s, s, TEXPATH["Edge"])))
        ap.text(pn, P + "TlI", "Draft art (our own, drawn from shapes at build time) - the real paintings come from the art sheet "
                               "Skyy approves (R5). Hover a tile for the gold edge, click it for the answer line.", "default", size=15,
                h=48, w=inner, wrap=True, max_lines=2)
        used += 170 + 48
    if case in RUN_CASES:
        lines = RUN_LINES[case]
        for i, ln in enumerate(lines):
            ap.text(pn, P + "Rl%d" % i, ln, "default", size=15, h=24, w=inner)
        if case == "g1":                           # how the HUD label above the hotbar would look (a page stand-in: no probe HUD)
            ap.append((pn, SUI.spacer(h=8)))
            ap.append((pn, "Group #%s { Anchor: (Width: 520, Height: 34); Background: %s; LayoutMode: Left; Padding: (Horizontal: 12); }"
                       % (P + "Gh", ART["hudBg"])))
            ap.append(("#" + P + "Gh", SUI.label(P + "GhA", "Objective", "default", size=15, bold=True, col=ART["gold"], w=96, h=34)))
            ap.text("#" + P + "Gh", P + "GhB", "Probe target - 48 blocks", "default", size=15, col="white", h=34, w=380)
            ap.text(pn, P + "GhC", "Above = the look of the planned HUD label over the hotbar (SkyyHud R3). In this test it comes as a "
                                   "chat line every 5 s.", "caption", size=13, h=40, w=inner, wrap=True, max_lines=2)
            used += 8 + 34 + 40
        ap.append((pn, SUI.spacer(h=10)))
        ap.append((pn, SUI.button(P + "Run", RUN_CASES[case], "primary", "normal", w=360)))
        used += 24 * len(lines) + 10 + SUI.BTN_H
    assert used <= ch - 16, (case, used, ch)
    return sh


HEAD_ROWS = 10
RUN_LINES = {
    "k1": ["1. Pick a class and put 2 abilities on (Q / E), hold a weapon with a signature (Mouse 5).",
           "2. Press Close and look - the page closes.",
           "3. Look bottom right: the vanilla ability boxes. Do they show YOUR keys (Mouse 5 / Q / E) with OUR class icons?",
           "4. Send a screenshot, then type /skyprobe next for F1."],
    "f1": ["The page closes first; 1 second later 9 cards arrive bottom right, 0.25 s apart:",
           "skill XP with a text bar, a kill with a gold name, Fortune with an item icon x3, a heal, collection progress,",
           "then one card in each style: Default, Success, Warning, Danger. Pick an item up too, to compare with a pickup card.",
           "Then type /skyprobe next for F2."],
    "f2": ["The page closes first; then 5 cards '+10 XP' ... '+50 XP', 0.3 s apart, all with the SAME tag.",
           "One card that counts up = the vanilla feed can merge our cards. Five cards = we merge them ourselves.",
           "Then type /skyprobe next for G1."],
    "g1": ["The page closes first. The target = 48 blocks from where you stand (towards -Z). For 21 s a dotted trail shows the way:",
           "A (0-6 s) our own dot picture, B (7-13 s) the vanilla glow in gold, C (14-20 s) ONE rotated effect of 6 dots.",
           "Walk around: the trail should always point at the target. Only YOU should see it (ask a friend if one is on).",
           "Tell me: which reads best? Does C point the same way as A and B? Then the tour is done."],
}


def dialogue_page():
    """D1: a TRANSPARENT 1600 x 980 root (Width / Height only, no Background) + a small nav panel top left + the 1100 x 190 bar"""
    ap = SUI.Appends()
    ap.append((None, "Group #%s { Anchor: (Width: %d, Height: %d); }" % (P, PAGE_W, PAGE_H)))
    ap.append((P, SUI.panel(P + "Dn", "simple", w=760, h=150, layout="Top", anchor={"left": 0, "top": 0})))
    dn = "#" + P + "Dn"
    ci = CASE_KEYS.index("d1")
    ap.text(dn, P + "Head", CASES[ci][2], "strong", size=15, h=24, w=736)
    ap.text(dn, P + "What", CASES[ci][3], "default", size=14, h=40, w=736, wrap=True, max_lines=2)
    ap.append((dn, SUI.group(P + "Nav", layout="Left", w=736, h=NAV_H)))
    ap.append(("#" + P + "Nav", SUI.button(P + "Back", "Back", "secondary", "small", w=110, anchor={"right": 8})))
    ap.append(("#" + P + "Nav", SUI.button(P + "Next", "Next case", "primary", "small", w=150, anchor={"right": 8})))
    ap.text("#" + P + "Nav", P + "NavL", "Case %d of %d - D1" % (ci + 1, len(CASES)), "gold", size=14, h=SUI.BTN_SMALL_H, w=220)
    ap.append(("#" + P + "Nav", SUI.button(P + "Close", "Close", "secondary", "small", w=110, sound="cancel", anchor={"left": 8})))
    ap.text(dn, P + "TCap", "Waiting for your click", "caption", size=14, h=22, w=736)
    bar = P + "Db"
    ap.append((P, "Group #%s { Anchor: (Left: %d, Top: %d, Width: %d, Height: %d); Background: %s; LayoutMode: Top; Padding: (Full: 14); }"
               % (bar, DB_L, DB_T, DB_W, DB_H, SUI.theme_bg("frame", "vanilla"))))
    iw = DB_W - 28
    ap.append(("#" + bar, SUI.group(P + "Dt", layout="Left", w=iw, h=30)))
    ap.text("#" + P + "Dt", P + "DSp", "Pebble", "tipName", size=18, col=ART["gold"], h=30, w=iw - 260)
    ap.text("#" + P + "Dt", P + "DPg", "line 1 / 3", "caption", size=15, h=30, w=260, align="End")
    ap.text("#" + bar, P + "DLn", "-", "default", size=18, col=ART["cyan"], h=86, w=iw, wrap=True, max_lines=3)
    ap.append(("#" + bar, SUI.group(P + "Dr", layout=None, w=iw, h=SUI.BTN_H)))
    dr = "#" + P + "Dr"
    ap.append((dr, SUI.button(P + "DSk", "Skip", "secondary", "normal", w=150, anchor={"left": 0, "top": 0})))
    ap.text(dr, P + "DRw", "", "gold", size=15, h=SUI.BTN_H, w=360, align="Center", anchor={"left": (iw - 360) // 2, "top": 0})
    ap.append((dr, SUI.button(P + "DNx", "Next", "primary", "normal", w=180, anchor={"left": iw - 180, "top": 0})))
    ap.append((dr, SUI.button(P + "DAc", "Accept", "primary", "normal", w=180, anchor={"left": iw - 180, "top": 0})))
    ap.append((dr, SUI.button(P + "DNo", "Not now", "secondary", "normal", w=160, anchor={"left": iw - 180 - 12 - 160, "top": 0})))
    assert 30 + 86 + SUI.BTN_H <= DB_H - 28
    return ap


DB_L, DB_T, DB_W, DB_H = 250, 770, 1100, 190
assert DB_L + DB_W <= PAGE_W and DB_T + DB_H <= PAGE_H
D1_LINES = ["Oh! A new face on the island. I'm Pebble - I keep the sky lanterns lit around here.",
            "The lanterns went dark last night and the spirits got restless. Could you light three of them for me?",
            "Bring me 3 Torches and I'll show you the old path to the second island. Deal?"]
D1_REWARD = "Reward: 50 coins"


def count_elements(appends):
    return sum(SUI._strip_quoted(SUI.render(mk)).count("{") for _p, mk in appends)


def bindings(case):
    b = [("#" + P + "Back", "back"), ("#" + P + "Next", "next"), ("#" + P + "Close", "close")]
    if case in MAP_CASES:
        b += [("#" + P + "N%dB" % k, "n%d" % k) for k in range(len(NODES))]
    if case == "m4":
        b.append(("#" + P + "A4N", "m4next"))
    if case == "m6":
        b += [("#" + P + "Tt%dB" % i, "tip%d" % i) for i in range(3)]
    if case in ("m8b", "m8c"):
        acts = ["pan:left", "pan:up", "pan:right", "pan:down", "pan:centre" if case == "m8b" else "pan:reset", "pan:rebuild"]
        b += [("#" + P + "Mv%d%d" % (i // 3, i % 3), a) for i, a in enumerate(acts)]
    if case == "h1b":
        b.append(("#" + P + "HbN", "h1bnew"))
    if case == "h1c":
        b += [("#" + P + "HcR", "h1credraw"), ("#" + P + "HcP", "h1cparts")]
    if case == "d1":
        b += [("#" + P + "DSk", "dskip"), ("#" + P + "DNx", "dnext"), ("#" + P + "DAc", "daccept"), ("#" + P + "DNo", "dnotnow")]
    if case == "t1":
        b += [("#" + P + "Tl%dH" % i, "tile%d" % i) for i in range(len(TILES) + 1)]
    if case in RUN_CASES:
        b.append(("#" + P + "Run", "run"))
    return b


# the unproven tokens each case is ALLOWED to carry (its own probe question; everything else must be proven / base)
PROBE_TOKENS = {"m4": {"element AssetImage", "AssetPath"}, "m6": {"TooltipText", "TextTooltipStyle", "MaxWidth"},
                "m8a": {"element AssetImage", "AssetPath"}, "h1a": {"element AssetImage", "AssetPath"},
                "h1b": {"element AssetImage", "AssetPath"}, "h1c": {"element AssetImage", "AssetPath"}}
PAGES = {}
for c in CASE_KEYS:
    if c in MAP_CASES:
        sh = map_page(c)
    elif c == "d1":
        sh = None
    else:
        sh = text_page(c)
    if sh is None:
        ap = dialogue_page()
        sets = list(ap.sets)
        pw, ph = PAGE_W, PAGE_H
    else:
        ap = sh.appends
        sets = list(ap.sets) + list(sh.sets)
        pw, ph = sh.w, sh.h
    chk = SUI.Appends(ap)
    chk.sets = sets
    for _p, mk in ap:                                              # every markup: syntax / id / text rules (our own texture paths)
        SUI.check_markup(mk, prefix=P, root=(_p is None), kit_paths=False)
    SUI.check_page(chk, P)
    SUI.assert_page_size(pw, ph)
    toks = SUI.proven_tokens(chk)
    unproven = set(k for k, g in toks.items() if g == "unknown" or (g is not None and "base" not in g and not all(x in SUI.PROBED for x in g)))
    PAGES[c] = dict(unproven=sorted(unproven))
    allowed = PROBE_TOKENS.get(c, set())
    assert unproven <= allowed | {"Visible", "Border", "TexturePath"}, "%s: unproven tokens %s (allowed %s)" % (c, sorted(unproven), sorted(allowed))
    for _p, mk in ap:                                              # every texture path = a kit texture or one this jar ships
        for m in re.finditer(r'(?:Background|TexturePath|Handle|HoveredHandle|DraggedHandle|Default|Hovered|Pressed): *"([^"]+\.png)"', mk):
            pth = m.group(1)
            assert pth in set(SUI.TEX.values()) or (pth.startswith("SkyyUiProbe/") and TEX_ROOT + pth[:-4] + "@2x.png" in ASSETS), (c, pth)
        for m in re.finditer(r'AssetPath: *"([^"]+)"', mk):
            assert "Common/" + m.group(1) in ASSETS, m.group(1)
    binds = bindings(c)
    ids = set(i for _p, mk in ap for i in SUI._static_ids(mk))
    for sel, act in binds:
        assert sel[1:] in ids, "%s: binding %s has no element" % (c, sel)
    assert len(set(a for _s, a in binds)) == len(binds), c
    for need in ("TCap", "Next", "Back", "Close"):
        assert P + need in ids, (c, need)
    lines = []
    for _p, mk in ap:
        mk_ = SUI.render(mk)
        assert "\t" not in mk_ and "\n" not in mk_
        lines.append("A\t%s\t%s" % ("" if _p is None else SUI.render(_p if _p.startswith("#") else "#" + _p), mk_))
    for ident, prop, val in sets:
        assert isinstance(val, str) and not SUI.has_j(val) and "\t" not in val and "\n" not in val, (ident, prop, val)
        lines.append("S\t#%s.%s\t%s" % (SUI.render(ident).lstrip("#"), prop, val))
    for sel, act in binds:
        lines.append("E\t%s\t%s" % (sel, act))
    text = "\n".join(lines) + "\n"
    PAGES[c].update(text=text, elements=count_elements(ap), appends=len(ap), sets=len(sets), binds=len(binds),
                    bytes=len(text.encode("utf-8")), markup=sum(len(SUI.render(mk)) for _p, mk in ap), ids=sorted(ids))
    ASSETS[RES_DIR + c + ".txt"] = text.encode("utf-8")
    assert PAGES[c]["elements"] <= 1600, (c, PAGES[c]["elements"])         # M1c opened 1,602 (0.7)
# node metadata for the click lines + the halo move: k, label, centre x / y at 100 %, at 200 %, size at 200 %
NODE_LINES = ["%d\t%s\t%d\t%d\t%d\t%d\t%d" % (k, node_label(n), int(round(n["cx"])), int(round(n["cy"])), int(round(NODES2[k]["cx"])),
                                             int(round(NODES2[k]["cy"])), NODES2[k]["size"]) for k, n in enumerate(NODES)]
ASSETS[RES_DIR + "nodes.txt"] = ("\n".join(NODE_LINES) + "\n").encode("utf-8")
for c in CASE_KEYS:
    print("page %-4s %-16s %5d elements, %4d appends, %3d b.set, %3d bindings, %6d bytes markup%s" % (
        c, CASE_NAME[c], PAGES[c]["elements"], PAGES[c]["appends"], PAGES[c]["sets"], PAGES[c]["binds"], PAGES[c]["markup"],
        ("  unproven: " + ", ".join(PAGES[c]["unproven"])) if PAGES[c]["unproven"] else ""))
DUMP = {"cases": CASES, "pages": dict((c, dict((k, v) for k, v in PAGES[c].items() if k not in ("text", "ids"))) for c in CASE_KEYS),
        "ids": dict((c, PAGES[c]["ids"]) for c in CASE_KEYS),
        "nodes": len(NODES), "sel0": SEL0, "m4_2x": M4_PATH_2X, "m4_1x": M4_PATH_1X, "m4_states": [s[2] for s in M4_STATES],
        "node_xy": [(int(round(n["cx"])), int(round(n["cy"]))) for n in NODES],
        "node_xy2": [(int(round(n["cx"])), int(round(n["cy"]))) for n in NODES2],
        "node_labels": [node_label(n) for n in NODES], "assets": sorted(ASSETS), "pan_step": PAN_STEP, "map2": [W2, H2],
        "binds": dict((c, [act for _sel, act in bindings(c)]) for c in CASE_KEYS), "d1_lines": D1_LINES, "d1_reward": D1_REWARD,
        "psys": sorted(PSYS), "run_cases": sorted(RUN_CASES), "rt_dir": RT_DIR, "head_rows": HEAD_ROWS}
if "--assets-out" in sys.argv:               # dev preview: every jar asset (pictures + page data) + dump.json into a scratch folder
    _od = os.path.realpath(sys.argv[sys.argv.index("--assets-out") + 1])
    assert _od.startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep), "--assets-out: only under tools/dev/scratch/"
    for _pth, _b in ASSETS.items():
        os.makedirs(os.path.dirname(os.path.join(_od, _pth)), exist_ok=True)
        with open(os.path.join(_od, _pth), "wb") as _f:
            _f.write(_b)
    with open(os.path.join(_od, "dump.json"), "w", encoding="utf-8") as _f:
        json.dump(DUMP, _f, indent=1)
    print("assets written to %s" % _od)
if "--dump-only" in sys.argv:
    print("dump-only: stop before the JVM (%.1f s)" % (time.time() - T0))
    raise SystemExit(0)

# ================================================================= 4. JAVA
import skyybuild as B
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE_PERM, "RES": RES_DIR, "PFX": P, "RTDIR": RT_DIR, "PSTEP": str(PAN_STEP),
    "W2": str(W2), "H2": str(H2), "CVW": str(CV_W), "MAINH": str(MAIN_H), "NCASE": str(len(CASES)),
    "CGOLD": FEED_COL["gold"], "CGREEN": FEED_COL["green"], "CDIM": FEED_COL["dim"], "CWHITE": FEED_COL["white"],
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "ES": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "ANC": "com.hypixel.hytale.server.core.ui.Anchor",
    "VAL": "com.hypixel.hytale.server.core.ui.Value",
    "CMA": "com.hypixel.hytale.server.core.asset.common.CommonAsset",
    "CAR": "com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry",
    "AST": "com.hypixel.hytale.protocol.Asset",
    "AINI": "com.hypixel.hytale.protocol.packets.setup.AssetInitialize",
    "APRT": "com.hypixel.hytale.protocol.packets.setup.AssetPart",
    "AFIN": "com.hypixel.hytale.protocol.packets.setup.AssetFinalize",
    "TCP": "com.hypixel.hytale.protocol.ToClientPacket",
    "PSC": "com.hypixel.hytale.server.core.modules.entity.player.PlayerSkinComponent",
    "PSK": "com.hypixel.hytale.protocol.PlayerSkin",
    "CSM": "com.hypixel.hytale.server.core.cosmetics.CosmeticsModule",
    "CREG": "com.hypixel.hytale.server.core.cosmetics.CosmeticRegistry",
    "PSP": "com.hypixel.hytale.server.core.cosmetics.PlayerSkinPart",
    "PSPV": "com.hypixel.hytale.server.core.cosmetics.PlayerSkinPart$Variant",
    "PSPT": "com.hypixel.hytale.server.core.cosmetics.PlayerSkinPartTexture",
    "PSGS": "com.hypixel.hytale.server.core.cosmetics.PlayerSkinGradientSet",
    "PSG": "com.hypixel.hytale.server.core.cosmetics.PlayerSkinGradient",
    "GJP": "com.google.gson.JsonParser",
    "GJO": "com.google.gson.JsonObject",
    "GJE": "com.google.gson.JsonElement",
    "GJA": "com.google.gson.JsonArray",
    "NTU": "com.hypixel.hytale.server.core.util.NotificationUtil",
    "NST": "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IWM": "com.hypixel.hytale.protocol.ItemWithAllMetadata",
    "PH": "com.hypixel.hytale.server.core.io.PacketHandler",
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "V3D": "org.joml.Vector3d",
    "V3DC": "org.joml.Vector3dc",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "UTR": "com.hypixel.hytale.protocol.packets.assets.UpdateTranslations",
    "UTY": "com.hypixel.hytale.protocol.UpdateType",
    "IDM": "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "ISTX": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "TIPIT": TIP_ITEM, "TIPKEY": TIP_KEY, "TIPMS": str(TIP_LATER_MS),
}
for c, m in ((T["JP"], "getLogger"), (T["JP"], "getCommandRegistry"), (T["APC"], "requirePermission"), (T["APC"], "setPermissionGroups"),
             (T["APC"], "addAliases"), (T["APC"], "addUsageVariant"), (T["APC"], "withRequiredArg"), (T["CTX"], "get"),
             (T["ATY"], "STRING"), (T["PR"], "sendMessage"), (T["PR"], "getUsername"), (T["PR"], "getUuid"), (T["PR"], "getReference"),
             (T["PR"], "isValid"), (T["PR"], "getPacketHandler"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["MSG"], "join"),
             (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (T["PAGE"], "build"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "close"), (T["PAGE"], "rebuild"), (T["PAGE"], "sendUpdate"),
             (T["PAGE"], "onDismiss"), (T["LIFE"], "CanDismiss"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UCB"], "setObject"),
             (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["BT"], "Activating"), (T["ANC"], "setLeft"), (T["ANC"], "setTop"),
             (T["ANC"], "setWidth"), (T["ANC"], "setHeight"), (T["VAL"], "of"), (T["ST"], "getComponent"), (T["ST"], "getExternalData"),
             (T["ES"], "getWorld"), (T["WLD"], "execute"), (T["REF"], "getStore"),
             (T["CMA"], "hash"), (T["CMA"], "getBlob"), (T["CMA"], "getName"), (T["CMA"], "toPacket"), (T["CAR"], "getByName"),
             (T["PSC"], "getComponentType"), (T["PSC"], "getPlayerSkin"), (T["CSM"], "get"), (T["CSM"], "getRegistry"),
             (T["CREG"], "getHaircuts"), (T["CREG"], "getFaces"), (T["CREG"], "getEyes"), (T["CREG"], "getEyebrows"), (T["CREG"], "getMouths"),
             (T["CREG"], "getEars"), (T["CREG"], "getFacialHairs"), (T["CREG"], "getHeadAccessories"), (T["CREG"], "getFaceAccessories"),
             (T["CREG"], "getEarAccessories"), (T["CREG"], "getBodyCharacteristics"), (T["CREG"], "getGradientSets"),
             (T["PSP"], "getModel"), (T["PSP"], "getGreyscaleTexture"), (T["PSP"], "getGradientSet"), (T["PSP"], "getTextures"),
             (T["PSP"], "getVariants"), (T["PSP"], "getHairType"), (T["PSP"], "doesRequireGenericHaircut"), (T["PSP"], "getHeadAccessoryType"),
             (T["PSPV"], "getModel"), (T["PSPV"], "getGreyscaleTexture"), (T["PSPV"], "getTextures"), (T["PSPT"], "getTexture"),
             (T["PSGS"], "getGradients"), (T["PSG"], "getTexture"), (T["GJP"], "parseString"),
             (T["NTU"], "sendNotification"), (T["NST"], "Default"), (T["NST"], "Success"), (T["NST"], "Warning"), (T["NST"], "Danger"),
             (T["IS"], "toPacket"), (T["PTU"], "spawnParticleEffect"), (T["R3F"], "setYaw"), (T["R3F"], "yaw"),
             (T["TC"], "getComponentType"), (T["TC"], "getPosition"), (T["TC"], "getRotation")):
    B.probe(pool, c, m)
_sig = lambda cls, name: [str(x.getSignature()) for x in pool.get(cls).getDeclaredMethods() if str(x.getName()) == name]
assert ("(Ljava/lang/String;Lorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3f;Ljava/util/List;Lcom/hypixel/hytale/component/ComponentAccessor;)V"
        in _sig(T["PTU"], "spawnParticleEffect")), "ParticleUtil.spawnParticleEffect(String, Vector3dc, Rotation3f, List, ComponentAccessor) changed"
assert ("(Ljava/lang/String;Lorg/joml/Vector3dc;Ljava/util/List;Lcom/hypixel/hytale/component/ComponentAccessor;)V"
        in _sig(T["PTU"], "spawnParticleEffect")), "ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor) changed"
assert ("(Lcom/hypixel/hytale/server/core/io/PacketHandler;Lcom/hypixel/hytale/server/core/Message;Lcom/hypixel/hytale/server/core/Message;"
        "Ljava/lang/String;Lcom/hypixel/hytale/protocol/ItemWithAllMetadata;Lcom/hypixel/hytale/protocol/packets/interface_/NotificationStyle;"
        "Ljava/lang/String;)V" in _sig(T["NTU"], "sendNotification")), "NotificationUtil.sendNotification(..., String tag) changed"
assert _sig(T["PSC"], "getPlayerSkin") == ["()Lcom/hypixel/hytale/protocol/PlayerSkin;"], "PlayerSkinComponent.getPlayerSkin changed"
assert "(Ljava/lang/String;)Lcom/google/gson/JsonElement;" in _sig(T["GJP"], "parseString"), "Gson JsonParser.parseString changed"
_skin_fields = [str(f.getName()) for f in pool.get(T["PSK"]).getDeclaredFields() if str(f.getType().getName()) == "java.lang.String"]
assert sorted(_skin_fields) == sorted(SKIN_FIELDS), "protocol PlayerSkin fields changed: %s" % _skin_fields
# 0.9 tip probe: every engine member it calls + the two facts the probe stands on (tools/uiprobe_0_9_patch.py header)
for c, m in ((T["ITM"], "getAssetMap"), (T["ITM"], "getDescriptionTranslationKey"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (T["I18N"], "get"), (T["I18N"], "getMessages"), (T["I18N"], "getMessage"), (T["PR"], "getLanguage"), (T["PH"], "writeNoCache"),
             (T["UTY"], "AddOrUpdate"), (T["IDM"], "KEYED_CODEC"), (T["IS"], "withMetadata"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"),
             (T["IS"], "isEmpty"), (T["PLA"], "getInventory"), (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["IC"], "addItemStack"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["ISTX"], "succeeded"), (T["ISTX"], "getRemainder"), (T["MSG"], "translation"),
             (T["APC"], "addSubCommand"), (T["APC"], "getName")):
    B.probe(pool, c, m)
_ctors = lambda cls: [str(x.getSignature()) for x in pool.get(cls).getDeclaredConstructors()]
assert "(Lcom/hypixel/hytale/protocol/UpdateType;Ljava/util/Map;)V" in _ctors(T["UTR"]), "UpdateTranslations(UpdateType, Map) changed"
assert "(Lcom/hypixel/hytale/server/core/Message;Lcom/hypixel/hytale/server/core/Message;)V" in _ctors(T["IDM"]), "ItemDisplayMetadata(Message, Message) changed"
assert "(Lcom/hypixel/hytale/protocol/ToClientPacket;)V" in _sig(T["PH"], "writeNoCache"), "PacketHandler.writeNoCache(ToClientPacket) changed"
assert "(Ljava/lang/String;)Ljava/util/Map;" in _sig(T["I18N"], "getMessages"), "I18nModule.getMessages(String) changed"
assert _sig(T["ITM"], "getDescriptionTranslationKey") == ["()Ljava/lang/String;"], "Item.getDescriptionTranslationKey changed"


def _cp_strings(cls):
    cp_ = pool.get(cls).getClassFile().getConstPool()
    out_ = set()
    for i_ in range(1, cp_.getSize()):
        try:
            if int(cp_.getTag(i_)) == 8:
                out_.add(str(cp_.getStringInfo(i_)))
        except Exception:
            pass
    return out_
# the key form: the lang map holds "server."-prefixed keys (getPrefix ends in "<file>." ; the engine's own keys in that map start
# "server.items."), and an item without a Description falls back to "server.items.<id>.description"
assert "\x01\x01." in _cp_strings(T["I18N"]) and "server.items.\x01.bench.descriptiveLabel" in _cp_strings(T["I18N"]), "I18nModule key prefix rule changed"
assert "server.items.\x01.description" in _cp_strings(T["ITM"]), "Item description key fallback changed"
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    out = TOKEN.sub(rep, src)
    if re.search(r"@[A-Za-z0-9]+@", out):
        raise SystemExit("an @TOKEN@ was left in the Java source (tokens are 2-7 capitals / digits): %s" % out[:300])
    return out


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None, iface=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    if iface:
        c.addInterface(pool.get(iface))
    return c


def jl(s):
    return SUI.java_lit(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


log = mk("ProbeLog")
data = mk("ProbeData")
thr = mk("ProbeThreads", None, "java.util.concurrent.ThreadFactory")
tim = mk("ProbeTimer")
rta = mk("RtAsset", T["CMA"])
rtp = mk("RtPic")
hres = mk("HeadResult")
heads = mk("Heads")
later = mk("Later", None, "java.lang.Runnable")
page_c = mk("MapPage", T["PAGE"])
cmds = mk("ProbeCmds")
tips = mk("Tips")
tsend = mk("TipSend", None, "java.lang.Runnable")

# ---- ProbeLog: server log + chat; the last 400 lines kept in memory (the harness reads them; nothing is written anywhere)
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.LinkedList TAIL = new java.util.LinkedList();")
M(log, r"""
public static synchronized void remember(String s) {
  TAIL.add(s);
  while (TAIL.size() > 400) TAIL.removeFirst();
}""")
M(log, r"""
public static void info(String s) {
  remember("I " + s);
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyUiProbe] " + s); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String s) {
  remember("W " + s);
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyUiProbe] " + s); } catch (Throwable t) { }
}""")
M(log, r"""
public static void chat(@PR@ pr, String s) {
  remember("C " + s);
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[SkyyUiProbe] " + s)); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  info(s);
  chat(pr, s);
}""")

# ---- ProbeData: the cases + the page data resources (read once from the jar, cached) + the node table + small texts
F(data, "public static final String[] KEYS = %s;" % jarr(CASE_KEYS))
F(data, "public static final String[] NAMES = %s;" % jarr([c[1] for c in CASES]))
F(data, "public static final String[] HEADS = %s;" % jarr([c[2] for c in CASES]))
F(data, "public static final String[] WHAT = %s;" % jarr([c[3] for c in CASES]))
F(data, "public static final int[] ELEMENTS = new int[] { %s };" % ", ".join(str(PAGES[c]["elements"]) for c in CASE_KEYS))
F(data, "public static final String[] M4_2X = %s;" % jarr(M4_PATH_2X))
F(data, "public static final String[] M4_1X = %s;" % jarr(M4_PATH_1X))
F(data, "public static final String[] M4_TEXT = %s;" % jarr(["State %d of %d - %s" % (i + 1, len(M4_STATES), s[2]) for i, s in enumerate(M4_STATES)]))
F(data, "public static final String[] D1 = %s;" % jarr(D1_LINES))
F(data, "public static final String D1REWARD = %s;" % jl(D1_REWARD))
F(data, "public static final String[] FONTK = %s;" % jarr(sorted(FONT5X7)))
F(data, "public static final String[] FONTV = %s;" % jarr([FONT5X7[k].replace(" ", "") for k in sorted(FONT5X7)]))
F(data, "public static final int[] PAL = new int[] { %s };" % ", ".join("0x%s" % c[1:7] for c in H1_PAL))
F(data, "public static final int SEL0 = %d;" % SEL0)
F(data, "public static final int NODES = %d;" % len(NODES))
F(data, "public static java.util.HashMap CACHE = new java.util.HashMap();")
F(data, "public static String[] LABEL;")
F(data, "public static int[] NX;")
F(data, "public static int[] NY;")
F(data, "public static int[] NX2;")
F(data, "public static int[] NY2;")
F(data, "public static int[] NS2;")
M(data, r"""
public static int index(String c) {
  if (c == null) return -1;
  String t = c.trim().toLowerCase();
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(t) || NAMES[i].equals(t)) return i;
  return -1;
}""")
M(data, r"""
public static String[] read(String name) {
  java.io.InputStream in = @PKG@.ProbeData.class.getClassLoader().getResourceAsStream("@RES@" + name + ".txt");
  if (in == null) throw new IllegalStateException("page data @RES@" + name + ".txt is missing from the jar");
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.io.BufferedReader r = new java.io.BufferedReader(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8));
    String s = r.readLine();
    while (s != null) { if (s.length() > 0) out.add(s); s = r.readLine(); }
  } catch (java.io.IOException e) {
    throw new IllegalStateException("page data " + name + " unreadable: " + e);
  } finally {
    try { in.close(); } catch (Throwable t) { }
  }
  return (String[]) out.toArray(new String[0]);
}""")
M(data, r"""
public static synchronized String[] lines(String c) {
  String[] l = (String[]) CACHE.get(c);
  if (l == null) { l = read(c); CACHE.put(c, l); }
  return l;
}""")
M(data, r"""
public static synchronized void nodes() {
  if (LABEL != null) return;
  String[] l = read("nodes");
  String[] lab = new String[l.length];
  int[] x = new int[l.length];
  int[] y = new int[l.length];
  int[] x2 = new int[l.length];
  int[] y2 = new int[l.length];
  int[] s2 = new int[l.length];
  for (int i = 0; i < l.length; i++) {
    String[] p = l[i].split("\t");
    int k = Integer.parseInt(p[0]);
    lab[k] = p[1];
    x[k] = Integer.parseInt(p[2]);
    y[k] = Integer.parseInt(p[3]);
    x2[k] = Integer.parseInt(p[4]);
    y2[k] = Integer.parseInt(p[5]);
    s2[k] = Integer.parseInt(p[6]);
  }
  NX = x; NY = y; NX2 = x2; NY2 = y2; NS2 = s2; LABEL = lab;
}""")
M(data, r"""
public static String act(String d) {
  if (d == null) return "";
  int i = d.indexOf("\"a\"");
  if (i < 0) return "";
  int c = d.indexOf(':', i + 3);
  if (c < 0) return "";
  int q = d.indexOf('"', c + 1);
  if (q < 0) return "";
  int e = d.indexOf('"', q + 1);
  if (e < 0) return "";
  return d.substring(q + 1, e);
}""")
F(data, "public static java.util.HashMap LAST = new java.util.HashMap();")
M(data, r"""
public static void remember(@PR@ pr, int i) {
  try { if (pr != null) LAST.put(pr.getUuid(), Integer.valueOf(i)); } catch (Throwable t) { }
}""")
M(data, r"""
public static String glyph(char ch) {
  String k = String.valueOf(Character.toUpperCase(ch));
  for (int i = 0; i < FONTK.length; i++) if (FONTK[i].equals(k)) return FONTV[i];
  for (int i = 0; i < FONTK.length; i++) if (FONTK[i].equals("?")) return FONTV[i];
  return null;
}""")

# ---- ProbeTimer: one daemon scheduler thread for the timed tests (F1 / F2 / G1); the harness swaps EX for a recording one
C(thr, "public ProbeThreads() { }")
M(thr, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyUiProbe-timer");
  t.setDaemon(true);
  return t;
}""")
F(tim, "public static java.util.concurrent.ScheduledExecutorService EX;")
M(tim, r"""
public static synchronized java.util.concurrent.ScheduledExecutorService ex() {
  if (EX == null) EX = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.ProbeThreads());
  return EX;
}""")
M(tim, r"""
public static void after(Runnable r, long ms) {
  ex().schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(tim, r"""
public static synchronized void stop() {
  try { if (EX != null) EX.shutdownNow(); } catch (Throwable t) { }
  EX = null;
}""")

# ---- RtAsset: one runtime picture (CommonAsset keeps only a WeakReference to its bytes - SkyyHud's MmAsset)
F(rta, "public byte[] bytes;")
C(rta, "public RtAsset(String name, String hash, byte[] b) { super(name, hash, b); this.bytes = b; }")
M(rta, "protected java.util.concurrent.CompletableFuture getBlob0() { return java.util.concurrent.CompletableFuture.completedFuture(this.bytes); }")

# ---- RtPic: runtime pictures (PNG by ImageIO), content-named, sent to ONE player once per connection (SkyyHud's minimap sequence)
F(rtp, "public static java.util.WeakHashMap DELIVERED = new java.util.WeakHashMap();")
F(rtp, "public static int SENT;")
M(rtp, r"""
public static byte[] png(int[] argb, int w, int h) throws java.io.IOException {
  java.awt.image.BufferedImage im = new java.awt.image.BufferedImage(w, h, java.awt.image.BufferedImage.TYPE_INT_ARGB);
  im.setRGB(0, 0, w, h, argb, 0, w);
  java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
  if (!javax.imageio.ImageIO.write(im, "png", bo)) throw new java.io.IOException("no PNG writer");
  return bo.toByteArray();
}""")
M(rtp, r"""
public static @PKG@.RtAsset asset(String kind, byte[] png) {
  String hash = @CMA@.hash(png);
  return new @PKG@.RtAsset("@RTDIR@" + kind + "-" + hash.substring(0, 16) + ".png", hash, png);
}""")
M(rtp, r"""
public static String initialsOf(String name) {
  if (name == null) return "?";
  String n = name.trim();
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < n.length() && b.length() < 2; i++) {
    char c = n.charAt(i);
    if (Character.isLetterOrDigit(c) && (b.length() == 0 || Character.isUpperCase(c) || (i > 0 && !Character.isLetterOrDigit(n.charAt(i - 1))))) b.append(Character.toUpperCase(c));
  }
  if (b.length() < 2) for (int i = 1; i < n.length() && b.length() < 2; i++) { char c = n.charAt(i); if (Character.isLetterOrDigit(c)) b.append(Character.toUpperCase(c)); }
  return b.length() == 0 ? "?" : b.toString();
}""")
# the H1 picture: 128 x 128, a rounded square in one of 6 colours (n picks the colour), a darker 6 px edge, the initials in our 5 x 7
# pixel font x 8 with a 4 px shadow
M(rtp, r"""
public static int[] initials(String name, int n) {
  int S = 128;
  int[] px = new int[S * S];
  int h = 0;
  if (name != null) for (int i = 0; i < name.length(); i++) h = h * 31 + name.charAt(i);
  if (h < 0) h = -h;
  if (h < 0) h = 0;
  int bg = @PKG@.ProbeData.PAL[(h % @PKG@.ProbeData.PAL.length + n) % @PKG@.ProbeData.PAL.length];
  int r = (bg >> 16) & 255; int g = (bg >> 8) & 255; int b = bg & 255;
  int edge = ((r * 3 / 5) << 16) | ((g * 3 / 5) << 8) | (b * 3 / 5);
  for (int y = 0; y < S; y++) {
    for (int x = 0; x < S; x++) {
      int dx = x < 20 ? 20 - x : (x > S - 21 ? x - (S - 21) : 0);
      int dy = y < 20 ? 20 - y : (y > S - 21 ? y - (S - 21) : 0);
      int d2 = dx * dx + dy * dy;
      if (d2 > 18 * 18) continue;
      boolean onEdge = x < 6 || y < 6 || x > S - 7 || y > S - 7 || d2 > 14 * 14;
      px[y * S + x] = 0xff000000 | (onEdge ? edge : bg);
    }
  }
  String t = initialsOf(name);
  int sc = 8;
  int gw = 5 * sc;
  int tw = t.length() * gw + (t.length() - 1) * sc;
  int x0 = (S - tw) / 2;
  int y0 = (S - 7 * sc) / 2;
  for (int pass = 0; pass < 2; pass++) {
    int off = pass == 0 ? 4 : 0;
    int col = pass == 0 ? (0xff000000 | edge) : 0xffffffff;
    for (int c = 0; c < t.length(); c++) {
      String gl = @PKG@.ProbeData.glyph(t.charAt(c));
      if (gl == null) continue;
      for (int i = 0; i < 35; i++) {
        if (gl.charAt(i) != '1') continue;
        int gx = x0 + c * (gw + sc) + (i % 5) * sc + off;
        int gy = y0 + (i / 5) * sc + off;
        for (int yy = 0; yy < sc; yy++) for (int xx = 0; xx < sc; xx++) {
          int X = gx + xx; int Y = gy + yy;
          if (X >= 0 && Y >= 0 && X < S && Y < S) px[Y * S + X] = col;
        }
      }
    }
  }
  return px;
}""")
M(rtp, r"""
public static synchronized boolean delivered(@PR@ pr, String name) {
  java.util.HashSet d = (java.util.HashSet) DELIVERED.get(pr);
  return d != null && d.contains(name);
}""")
# one picture to ONE player, once per connection (PlayerRef = one connection): AssetInitialize + AssetPart + AssetFinalize in ONE write;
# returns true when the packets went out now, false when this connection already has it
M(rtp, r"""
public static synchronized boolean send(@PR@ pr, @PKG@.RtAsset a) {
  if (pr == null || a == null) return false;
  java.util.HashSet d = (java.util.HashSet) DELIVERED.get(pr);
  if (d == null) { d = new java.util.HashSet(); DELIVERED.put(pr, d); }
  if (d.contains(a.getName())) return false;
  byte[] b = a.bytes;
  @TCP@[] ps = new @TCP@[3];
  ps[0] = new @AINI@((@AST@) a.toPacket(), b.length);
  ps[1] = new @APRT@(b);
  ps[2] = new @AFIN@();
  pr.getPacketHandler().write(ps);
  d.add(a.getName());
  SENT = SENT + 1;
  return true;
}""")
M(rtp, r"""
public static @PKG@.RtAsset initialsAsset(@PR@ pr, int n) throws java.io.IOException {
  String nm = pr == null ? "?" : pr.getUsername();
  return asset("h1", png(initials(nm, n), 128, 128));
}""")

# ---- HeadResult: what one head composition gave (memory only)
for _f in ("public String path;", "public String note;", "public String[] parts;", "public long ms;", "public int faces;", "public int drawn;",
           "public int skipped;", "public byte[] png;", "public boolean ok;", "public boolean sentNow;", "public int[] px;"):
    F(hres, _f)
C(hres, "public HeadResult() { }")

# ---- Heads: YOUR head from the INSTALLED game's own files, at run time (nothing vanilla in the jar): the skin's part ids -> the engine's
# CosmeticRegistry parts (model, texture, gradient) -> the blockymodel nodes (Gson, from CommonAssetRegistry) -> the front faces (box faces
# facing the camera + quads), depth sorted -> texture pixels (ImageIO) with greyscale texels mapped through the gradient row -> 128 px PNG.
# Transform rule (HEAD NOTES at the top of this file): a node's pivot = the parent's child frame + R_parent * position; its geometry
# centre AND its children's frame = pivot + R * offset; an attachment root named after a Player head bone IS that bone's child frame.
F(heads, "public static java.util.HashMap BLOB = new java.util.HashMap();")
F(heads, "public static java.util.HashMap IMG = new java.util.HashMap();")
F(heads, "public static java.util.HashMap FRAMES;")
F(heads, "public static String FRAMES_OF;")
F(heads, "public static final String[] SKIN = %s;" % jarr(SKIN_FIELDS))
F(heads, "public static final String[] ORDER = %s;" % jarr(HEAD_ORDER))
F(heads, 'public static final String[] FN = new String[] { "front", "back", "left", "right", "top", "bottom" };')
# face corner templates (TL, TR, BL) on a +-1 box seen from outside; the size axes of each face's texture rect
F(heads, "public static final double[] FT = new double[] { %s };" % ", ".join("%d" % v for f in HEAD_FACES for c in f[0] for v in c))
F(heads, "public static final int[] FAX = new int[] { %s };" % ", ".join("%d" % v for f in HEAD_FACES for v in f[1]))
F(heads, 'public static final String[] QN = new String[] { "+Z", "-Z", "+X", "-X", "+Y", "-Y" };')
F(heads, "public static final int S = %d;" % HEAD_PX)
M(heads, r"""
public static synchronized byte[] blob(String path) throws Exception {
  Object o = BLOB.get(path);
  if (o != null) return (byte[]) o;
  @CMA@ a = @CAR@.getByName(path);
  if (a == null) a = @CAR@.getByName("Common/" + path);        // UNVERIFIED which spelling the registry keys vanilla files by
  if (a == null) throw new IllegalStateException("game file not found: " + path);
  byte[] b = (byte[]) a.getBlob().get(3L, java.util.concurrent.TimeUnit.SECONDS);
  if (b == null) throw new IllegalStateException("game file empty: " + path);
  BLOB.put(path, b);
  return b;
}""")
M(heads, r"""
public static synchronized int[] image(String path) throws Exception {
  Object o = IMG.get(path);
  if (o != null) return (int[]) o;
  java.awt.image.BufferedImage im = javax.imageio.ImageIO.read(new java.io.ByteArrayInputStream(blob(path)));
  if (im == null) throw new IllegalStateException("not a picture: " + path);
  int w = im.getWidth();
  int h = im.getHeight();
  int[] out = new int[2 + w * h];
  out[0] = w;
  out[1] = h;
  int[] px = im.getRGB(0, 0, w, h, null, 0, w);
  System.arraycopy(px, 0, out, 2, w * h);
  IMG.put(path, out);
  return out;
}""")
M(heads, r"""
public static @GJO@ json(String path) throws Exception {
  String s = new String(blob(path), java.nio.charset.StandardCharsets.UTF_8);
  if (s.length() > 0 && s.charAt(0) == (char) 65279) s = s.substring(1);
  return @GJP@.parseString(s).getAsJsonObject();
}""")
M(heads, r"""
public static @GJO@ obj(@GJO@ o, String k) {
  if (o == null || !o.has(k)) return null;
  @GJE@ e = o.get(k);
  return (e != null && e.isJsonObject()) ? e.getAsJsonObject() : null;
}""")
M(heads, r"""
public static @GJA@ arr(@GJO@ o, String k) {
  if (o == null || !o.has(k)) return null;
  @GJE@ e = o.get(k);
  return (e != null && e.isJsonArray()) ? e.getAsJsonArray() : null;
}""")
M(heads, r"""
public static double num(@GJO@ o, String k, double d) {
  if (o == null || !o.has(k)) return d;
  @GJE@ e = o.get(k);
  if (e == null || !e.isJsonPrimitive()) return d;
  try { return e.getAsDouble(); } catch (Throwable t) { return d; }
}""")
M(heads, r"""
public static String str(@GJO@ o, String k) {
  if (o == null || !o.has(k)) return null;
  @GJE@ e = o.get(k);
  if (e == null || !e.isJsonPrimitive()) return null;
  return e.getAsString();
}""")
M(heads, r"""
public static boolean flag(@GJO@ o, String k, boolean d) {
  if (o == null || !o.has(k)) return d;
  @GJE@ e = o.get(k);
  if (e == null || !e.isJsonPrimitive()) return d;
  try { return e.getAsBoolean(); } catch (Throwable t) { return d; }
}""")
M(heads, r"""
public static double[] vec(@GJO@ o, String k, double d) {
  @GJO@ v = obj(o, k);
  return new double[] { num(v, "x", d), num(v, "y", d), num(v, "z", d) };
}""")
M(heads, r"""
public static double[] quat(@GJO@ o, String k) {
  @GJO@ v = obj(o, k);
  return new double[] { num(v, "x", 0.0), num(v, "y", 0.0), num(v, "z", 0.0), num(v, "w", 1.0) };
}""")
M(heads, r"""
public static double[] qmul(double[] a, double[] b) {
  return new double[] { a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1], a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
                        a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3], a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2] };
}""")
M(heads, r"""
public static double[] qrot(double[] q, double vx, double vy, double vz) {
  double n = Math.sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
  if (n == 0.0) n = 1.0;
  double x = q[0] / n; double y = q[1] / n; double z = q[2] / n; double w = q[3] / n;
  double tx = 2.0 * (y * vz - z * vy); double ty = 2.0 * (z * vx - x * vz); double tz = 2.0 * (x * vy - y * vx);
  return new double[] { vx + w * tx + (y * tz - z * ty), vy + w * ty + (z * tx - x * tz), vz + w * tz + (x * ty - y * tx) };
}""")
# one face -> double[18]: TL TR BL (x y z), the uv of TL TR BL, nz, kind (0 box / 1 quad), part order
M(heads, r"""
public static void emit(java.util.ArrayList out, double[] ctr, double[] qw, int f, double hx, double hy, double hz, double w, double h, @GJO@ lay, boolean neg, int kind, int part) {
  double[] r = new double[18];
  for (int i = 0; i < 3; i++) {
    double[] c = qrot(qw, @PKG@.Heads.FT[f * 9 + i * 3] * hx, @PKG@.Heads.FT[f * 9 + i * 3 + 1] * hy, @PKG@.Heads.FT[f * 9 + i * 3 + 2] * hz);
    r[i * 3] = ctr[0] + c[0];
    r[i * 3 + 1] = ctr[1] + c[1];
    r[i * 3 + 2] = ctr[2] + c[2];
  }
  @GJO@ off = obj(lay, "offset");
  double ox = num(off, "x", 0.0);
  double oy = num(off, "y", 0.0);
  @GJO@ mi = obj(lay, "mirror");
  boolean mx = flag(mi, "x", false);
  boolean my = flag(mi, "y", false);
  int a = ((int) Math.round(num(lay, "angle", 0.0)) % 360 + 360) % 360;
  double rw = (a == 0 || a == 180) ? w : h;
  double rh = (a == 0 || a == 180) ? h : w;
  for (int i = 0; i < 3; i++) {
    double s = i == 1 ? 1.0 : 0.0;
    double t = i == 2 ? 1.0 : 0.0;
    if (mx) s = 1.0 - s;
    if (my) t = 1.0 - t;
    double s2 = s; double t2 = t;
    if (a == 90) { s2 = t; t2 = 1.0 - s; }
    else if (a == 180) { s2 = 1.0 - s; t2 = 1.0 - t; }
    else if (a == 270) { s2 = 1.0 - t; t2 = s; }
    r[9 + i * 2] = ox + s2 * rw;
    r[10 + i * 2] = oy + t2 * rh;
  }
  double e1x = r[3] - r[0]; double e1y = r[4] - r[1];
  double e2x = r[6] - r[0]; double e2y = r[7] - r[1];
  double nz = e2x * e1y - e2y * e1x;
  if (neg) nz = -nz;
  r[15] = nz;
  r[16] = kind;
  r[17] = part;
  out.add(r);
}""")
M(heads, r"""
public static void shape(@GJO@ n, double[] ctr, double[] qw, int part, java.util.ArrayList out) {
  @GJO@ sh = obj(n, "shape");
  if (sh == null || !flag(sh, "visible", true)) return;
  String type = str(sh, "type");
  if (type == null || !(type.equals("box") || type.equals("quad"))) return;
  @GJO@ st = obj(sh, "settings");
  double[] sz = vec(st, "size", 0.0);
  double[] sx = obj(sh, "stretch") == null ? new double[] { 1.0, 1.0, 1.0 } : vec(sh, "stretch", 1.0);
  for (int i = 0; i < 3; i++) if (sx[i] == 0.0) sx[i] = 1.0;
  boolean neg = sx[0] * sx[1] * sx[2] < 0.0;
  @GJO@ tl = obj(sh, "textureLayout");
  if (tl == null) return;
  if (type.equals("box")) {
    for (int f = 0; f < 6; f++) {
      @GJO@ lay = obj(tl, @PKG@.Heads.FN[f]);
      if (lay == null) continue;
      emit(out, ctr, qw, f, sz[0] * sx[0] / 2.0, sz[1] * sx[1] / 2.0, sz[2] * sx[2] / 2.0, sz[@PKG@.Heads.FAX[f * 2]], sz[@PKG@.Heads.FAX[f * 2 + 1]], lay, neg, 0, part);
    }
    return;
  }
  @GJO@ lay = obj(tl, "front");
  if (lay == null) return;
  String nm = str(st, "normal");
  int f = 0;
  for (int i = 0; i < 6; i++) if (@PKG@.Heads.QN[i].equals(nm)) f = i;
  double[] h3 = new double[3];
  h3[@PKG@.Heads.FAX[f * 2]] = sz[0] * sx[0] / 2.0;
  h3[@PKG@.Heads.FAX[f * 2 + 1]] = sz[1] * sx[1] / 2.0;
  emit(out, ctr, qw, f, h3[0], h3[1], h3[2], sz[0], sz[1], lay, neg, 1, part);
}""")
M(heads, r"""
public static void walk(@GJO@ n, double[] origin, double[] q, boolean root, boolean kids, int part, java.util.ArrayList out) {
  double[] ctr = origin;
  double[] qw = q;
  if (!root) {
    double[] p = vec(n, "position", 0.0);
    double[] r = qrot(q, p[0], p[1], p[2]);
    qw = qmul(q, quat(n, "orientation"));
    double[] o = vec(obj(n, "shape"), "offset", 0.0);
    double[] r2 = qrot(qw, o[0], o[1], o[2]);
    ctr = new double[] { origin[0] + r[0] + r2[0], origin[1] + r[1] + r2[1], origin[2] + r[2] + r2[2] };
  }
  shape(n, ctr, qw, part, out);
  if (!kids) return;
  @GJA@ ch = arr(n, "children");
  if (ch == null) return;
  for (int i = 0; i < ch.size(); i++) {
    @GJE@ e = ch.get(i);
    if (e != null && e.isJsonObject()) walk(e.getAsJsonObject(), ctr, qw, false, true, part, out);
  }
}""")
M(heads, r"""
public static @GJO@ find(@GJO@ n, String name) {
  if (n == null) return null;
  if (name.equals(str(n, "name"))) return n;
  @GJA@ ch = arr(n, "children");
  if (ch == null) return null;
  for (int i = 0; i < ch.size(); i++) {
    @GJE@ e = ch.get(i);
    if (e != null && e.isJsonObject()) { @GJO@ r = find(e.getAsJsonObject(), name); if (r != null) return r; }
  }
  return null;
}""")
M(heads, r"""
public static @GJO@ headNode(String body) throws Exception {
  @GJA@ ns = arr(json(body), "nodes");
  if (ns == null) throw new IllegalStateException("no nodes in " + body);
  for (int i = 0; i < ns.size(); i++) {
    @GJO@ h = find(ns.get(i).getAsJsonObject(), "Head");
    if (h != null) return h;
  }
  throw new IllegalStateException("no Head node in " + body);
}""")
M(heads, r"""
public static synchronized java.util.HashMap frames(String body) throws Exception {
  if (FRAMES != null && body.equals(FRAMES_OF)) return FRAMES;
  @GJO@ h = headNode(body);
  java.util.HashMap fr = new java.util.HashMap();
  fr.put("Head", new double[] { 0, 0, 0, 0, 0, 0, 1 });
  @GJA@ ch = arr(h, "children");
  if (ch != null) for (int i = 0; i < ch.size(); i++) {
    @GJO@ c = ch.get(i).getAsJsonObject();
    String nm = str(c, "name");
    if (nm == null || nm.equals("Neck")) continue;
    double[] q = quat(c, "orientation");
    double[] p = vec(c, "position", 0.0);
    double[] o = vec(obj(c, "shape"), "offset", 0.0);
    double[] r = qrot(q, o[0], o[1], o[2]);
    fr.put(nm, new double[] { p[0] + r[0], p[1] + r[1], p[2] + r[2], q[0], q[1], q[2], q[3] });
  }
  FRAMES = fr;
  FRAMES_OF = body;
  return fr;
}""")
# the faces of one part model: the body model gives only its Head box (centred on 0); an attachment's roots named after a head bone sit
# in that bone's frame; roots named otherwise (Neck / Chest attachments) are skipped (counted)
M(heads, r"""
public static int model(String path, String body, int part, java.util.ArrayList out) throws Exception {
  if (path.equals(body)) {
    walk(headNode(body), new double[] { 0, 0, 0 }, new double[] { 0, 0, 0, 1 }, true, false, part, out);
    return 0;
  }
  java.util.HashMap fr = frames(body);
  @GJA@ ns = arr(json(path), "nodes");
  int skipped = 0;
  if (ns == null) return 0;
  for (int i = 0; i < ns.size(); i++) {
    @GJO@ root = ns.get(i).getAsJsonObject();
    double[] f = (double[]) fr.get(str(root, "name"));
    if (f == null) { skipped++; continue; }
    walk(root, new double[] { f[0], f[1], f[2] }, new double[] { f[3], f[4], f[5], f[6] }, true, true, part, out);
  }
  return skipped;
}""")
M(heads, r"""
public static java.util.Map regMap(@CREG@ reg, String type) {
  if (type.equals("bodyCharacteristic")) return reg.getBodyCharacteristics();
  if (type.equals("ears")) return reg.getEars();
  if (type.equals("face")) return reg.getFaces();
  if (type.equals("mouth")) return reg.getMouths();
  if (type.equals("eyes")) return reg.getEyes();
  if (type.equals("eyebrows")) return reg.getEyebrows();
  if (type.equals("facialHair")) return reg.getFacialHairs();
  if (type.equals("haircut")) return reg.getHaircuts();
  if (type.equals("faceAccessory")) return reg.getFaceAccessories();
  if (type.equals("headAccessory")) return reg.getHeadAccessories();
  if (type.equals("earAccessory")) return reg.getEarAccessories();
  return null;
}""")
M(heads, r"""
public static String[] values(@PSK@ s) {
  return new String[] { %s };
}""" % ", ".join("s." + f for f in SKIN_FIELDS))
M(heads, r"""
public static String valueOf(String[] v, String key) {
  for (int i = 0; i < @PKG@.Heads.SKIN.length; i++) if (@PKG@.Heads.SKIN[i].equals(key)) return v[i];
  return null;
}""")
# a part id "asset.texture.variant" -> { model, texture, ramp texture or null } (null = not drawable); tint = the skin tone for parts
# that carry no colour of their own (face, mouth, ears)
M(heads, r"""
public static String[] resolve(@CREG@ reg, String type, String value, String tint, StringBuilder note) {
  if (value == null || value.length() == 0) return null;
  java.util.Map m = regMap(reg, type);
  if (m == null) return null;
  String[] p = value.split("\\.");
  @PSP@ part = (@PSP@) m.get(p[0]);
  if (part == null) { note.append(type + " '" + p[0] + "' unknown; "); return null; }
  String tex = p.length > 1 ? p[1] : tint;
  String var = p.length > 2 ? p[2] : null;
  String model = part.getModel();
  String grey = part.getGreyscaleTexture();
  java.util.Map texs = part.getTextures();
  java.util.Map vars = part.getVariants();
  Object vo = null;
  if (vars != null && var != null) vo = vars.get(var);
  if (vo == null && model == null && vars != null && !vars.isEmpty()) vo = vars.values().iterator().next();
  if (vo != null) {
    @PSPV@ v = (@PSPV@) vo;
    if (v.getModel() != null) model = v.getModel();
    if (v.getGreyscaleTexture() != null || v.getTextures() != null) { grey = v.getGreyscaleTexture(); texs = v.getTextures(); }
  }
  if (model == null) { note.append(type + " '" + value + "' has no model; "); return null; }
  String texture = null;
  String ramp = null;
  if (texs != null && tex != null && texs.get(tex) != null) texture = ((@PSPT@) texs.get(tex)).getTexture();
  else if (grey != null) {
    texture = grey;
    String gs = part.getGradientSet();
    if (gs != null && tex != null) {
      @PSGS@ set = (@PSGS@) reg.getGradientSets().get(gs);
      Object go = (set == null || set.getGradients() == null) ? null : set.getGradients().get(tex);
      if (go instanceof @PSG@) ramp = ((@PSG@) go).getTexture();
      else if (go instanceof @PSPT@) ramp = ((@PSPT@) go).getTexture();
    }
  } else if (texs != null && !texs.isEmpty()) texture = ((@PSPT@) texs.values().iterator().next()).getTexture();
  if (texture == null) { note.append(type + " '" + value + "' has no texture; "); return null; }
  return new String[] { model, texture, ramp };
}""")
# draw: the visible faces (a box face facing the camera, any quad not edge-on), back to front (the face centre's depth, then the part
# order, then the file order), nearest texel, greyscale texels mapped through the gradient row; the view = the faces' bounds (clamped to
# the head area, at least 34 units) as a square
M(heads, r"""
public static int[] raster(java.util.ArrayList faces, int[][] tex, int[][] ramps, int[] stats) {
  int n = faces.size();
  int[] idx = new int[n];
  int m = 0;
  double minx = 1e9; double maxx = -1e9; double miny = 1e9; double maxy = -1e9;
  for (int i = 0; i < n; i++) {
    double[] f = (double[]) faces.get(i);
    if (f[16] == 0.0 ? f[15] <= 1e-6 : Math.abs(f[15]) <= 1e-6) continue;
    if (tex[(int) f[17]] == null) continue;
    idx[m] = i;
    m++;
    double x3 = f[3] + f[6] - f[0]; double y3 = f[4] + f[7] - f[1];
    minx = Math.min(Math.min(minx, Math.min(f[0], f[3])), Math.min(f[6], x3));
    maxx = Math.max(Math.max(maxx, Math.max(f[0], f[3])), Math.max(f[6], x3));
    miny = Math.min(Math.min(miny, Math.min(f[1], f[4])), Math.min(f[7], y3));
    maxy = Math.max(Math.max(maxy, Math.max(f[1], f[4])), Math.max(f[7], y3));
  }
  for (int i = 1; i < m; i++) {
    int k = idx[i];
    double[] fk = (double[]) faces.get(k);
    double dk = (fk[5] + fk[8]) / 2.0;
    int j = i - 1;
    while (j >= 0) {
      double[] fj = (double[]) faces.get(idx[j]);
      double dj = (fj[5] + fj[8]) / 2.0;
      if (dj > dk || (dj == dk && (fj[17] > fk[17] || (fj[17] == fk[17] && idx[j] > k)))) { idx[j + 1] = idx[j]; j--; } else break;
    }
    idx[j + 1] = k;
  }
  minx = Math.max(minx, @HXMIN@); maxx = Math.min(maxx, @HXMAX@); miny = Math.max(miny, @HYMIN@); maxy = Math.min(maxy, @HYMAX@);
  if (m == 0) { minx = -15.0; maxx = 15.0; miny = -14.0; maxy = 14.0; }
  double size = Math.max(Math.max(maxx - minx, maxy - miny), @HMIN@) + 2.0;
  double cx = (minx + maxx) / 2.0;
  double cy = (miny + maxy) / 2.0;
  double k = @PKG@.Heads.S / size;
  int[] img = new int[@PKG@.Heads.S * @PKG@.Heads.S];
  int drawn = 0;
  for (int q = 0; q < m; q++) {
    double[] f = (double[]) faces.get(idx[q]);
    int[] t = tex[(int) f[17]];
    int[] rp = ramps[(int) f[17]];
    int tw = t[0]; int th = t[1];
    double p0x = (f[0] - cx) * k + @PKG@.Heads.S / 2.0; double p0y = (cy - f[1]) * k + @PKG@.Heads.S / 2.0;
    double ax = (f[3] - f[0]) * k; double ay = (f[1] - f[4]) * k;
    double bx = (f[6] - f[0]) * k; double by = (f[1] - f[7]) * k;
    double det = ax * by - ay * bx;
    if (Math.abs(det) < 1e-9) continue;
    double xa = Math.min(Math.min(p0x, p0x + ax), Math.min(p0x + bx, p0x + ax + bx));
    double xb = Math.max(Math.max(p0x, p0x + ax), Math.max(p0x + bx, p0x + ax + bx));
    double ya = Math.min(Math.min(p0y, p0y + ay), Math.min(p0y + by, p0y + ay + by));
    double yb = Math.max(Math.max(p0y, p0y + ay), Math.max(p0y + by, p0y + ay + by));
    int x0 = Math.max(0, (int) Math.floor(xa)); int x1 = Math.min(@PKG@.Heads.S - 1, (int) Math.floor(xb));
    int y0 = Math.max(0, (int) Math.floor(ya)); int y1 = Math.min(@PKG@.Heads.S - 1, (int) Math.floor(yb));
    drawn++;
    for (int py = y0; py <= y1; py++) {
      for (int px = x0; px <= x1; px++) {
        double qx = px + 0.5 - p0x; double qy = py + 0.5 - p0y;
        double s = (qx * by - qy * bx) / det;
        double tt = (ax * qy - ay * qx) / det;
        if (s < 0.0 || s >= 1.0 || tt < 0.0 || tt >= 1.0) continue;
        double u = f[9] + s * (f[11] - f[9]) + tt * (f[13] - f[9]);
        double v = f[10] + s * (f[12] - f[10]) + tt * (f[14] - f[10]);
        int iu = (int) Math.floor(u); int iv = (int) Math.floor(v);
        if (iu < 0 || iv < 0 || iu >= tw || iv >= th) continue;
        int c = t[2 + iv * tw + iu];
        if (((c >>> 24) & 255) < 8) continue;
        int r = (c >> 16) & 255; int g = (c >> 8) & 255; int b = c & 255;
        if (rp != null && r == g && g == b) c = rp[r];
        img[py * @PKG@.Heads.S + px] = 0xff000000 | (c & 0xffffff);
      }
    }
  }
  stats[0] = m;
  stats[1] = drawn;
  return img;
}""".replace("@HXMIN@", repr(HEAD_VIEW[0])).replace("@HXMAX@", repr(HEAD_VIEW[1])).replace("@HYMIN@", repr(HEAD_VIEW[2]))
   .replace("@HYMAX@", repr(HEAD_VIEW[3])).replace("@HMIN@", repr(HEAD_VIEW[4])))
M(heads, r"""
public static int[] rampOf(String path) throws Exception {
  int[] im = image(path);
  int w = im[0];
  int[] r = new int[256];
  for (int i = 0; i < 256; i++) r[i] = im[2 + Math.min(w - 1, i * w / 256)];
  return r;
}""")
M(heads, r"""
public static @PKG@.HeadResult compose(@PR@ pr, @REF@ ref, @ST@ st) {
  @PKG@.HeadResult res = new @PKG@.HeadResult();
  long t0 = System.nanoTime();
  StringBuilder note = new StringBuilder();
  try {
    @PSC@ psc = (@PSC@) st.getComponent(ref, @PSC@.getComponentType());
    if (psc == null || psc.getPlayerSkin() == null) { res.note = "no skin on this player (PlayerSkinComponent missing)"; return res; }
    String[] v = values(psc.getPlayerSkin());
    String[] parts = new String[v.length];
    for (int i = 0; i < v.length; i++) parts[i] = @PKG@.Heads.SKIN[i] + " = " + (v[i] == null ? "-" : v[i]);
    res.parts = parts;
    @CSM@ cm = @CSM@.get();
    if (cm == null || cm.getRegistry() == null) { res.note = "the game's cosmetics registry is not loaded"; return res; }
    @CREG@ reg = cm.getRegistry();
    String body = valueOf(v, "bodyCharacteristic");
    String tone = null;
    if (body != null && body.indexOf('.') > 0) tone = body.split("\\.")[1];
    String hair = valueOf(v, "haircut");
    String hat = valueOf(v, "headAccessory");
    if (hat != null && hat.length() > 0) {
      @PSP@ hp = (@PSP@) reg.getHeadAccessories().get(hat.split("\\.")[0]);
      String ht = (hp == null || hp.getHeadAccessoryType() == null) ? "" : hp.getHeadAccessoryType().toString();
      if (ht.equals("FullyCovering")) { hair = null; note.append("the hat covers the hair; "); }
      else if (ht.equals("HalfCovering") && hair != null && hair.length() > 0) {
        String[] hs = hair.split("\\.");
        @PSP@ hc = (@PSP@) reg.getHaircuts().get(hs[0]);
        if (hc != null && hc.doesRequireGenericHaircut() && hc.getHairType() != null) {
          String gen = "Generic" + hc.getHairType().toString();
          if (reg.getHaircuts().get(gen) != null) { hair = gen + (hs.length > 1 ? "." + hs[1] : ""); note.append("hair under the hat: " + gen + "; "); }
        }
      }
    }
    String[] bodyR = resolve(reg, "bodyCharacteristic", body, tone, note);
    if (bodyR == null) { res.note = "no body model: " + note; return res; }
    java.util.ArrayList faces = new java.util.ArrayList();
    int np = @PKG@.Heads.ORDER.length;
    int[][] tex = new int[np][];
    int[][] ramps = new int[np][];
    int skipped = 0;
    for (int i = 0; i < np; i++) {
      String key = @PKG@.Heads.ORDER[i];
      String val = key.equals("haircut") ? hair : valueOf(v, key);
      String[] r = resolve(reg, key, val, tone, note);
      if (r == null) continue;
      try {
        tex[i] = image(r[1]);
        if (r[2] != null) ramps[i] = rampOf(r[2]);
        skipped = skipped + model(r[0], bodyR[0], i, faces);
      } catch (Throwable t) {
        tex[i] = null;
        note.append(key + " not drawn: " + t.getMessage() + "; ");
      }
    }
    int[] stats = new int[2];
    int[] img = raster(faces, tex, ramps, stats);
    res.px = img;
    res.faces = stats[0];
    res.drawn = stats[1];
    res.skipped = skipped;
    res.png = @PKG@.RtPic.png(img, @PKG@.Heads.S, @PKG@.Heads.S);
    @PKG@.RtAsset a = @PKG@.RtPic.asset("head", res.png);
    res.sentNow = @PKG@.RtPic.send(pr, a);
    res.path = a.getName();
    res.ok = true;
    res.note = note.length() == 0 ? "all parts drawn" : note.toString();
  } catch (Throwable t) {
    res.ok = false;
    res.note = "FAIL - " + t + (note.length() > 0 ? " (" + note + ")" : "");
  } finally {
    res.ms = (System.nanoTime() - t0) / 1000000L;
  }
  return res;
}""")

# ---- Later: the timed tests F1 / F2 / G1 (started AFTER the page closed). The scheduler thread only hops to the world thread
# (world.execute); every step runs on the world thread, then schedules the next one. Memory only; stops when the player leaves.
for _f in ("public String kind;", "public @PR@ pr;", "public @WLD@ world;", "public int step;", "public boolean hop;", "public boolean haveTarget;",
           "public double tx;", "public double ty;", "public double tz;", "public int dotsA;", "public int dotsB;", "public int dotsC;",
           "public boolean reached;", "public int fails;", "public int sent;"):
    F(later, _f)
C(later, r"""
public Later(String k, @PR@ pr, @WLD@ w) {
  this.kind = k;
  this.pr = pr;
  this.world = w;
}""")
M(later, r"""
public void next(long ms) { @PKG@.ProbeTimer.after(this, ms); }""")
M(later, r"""
public static @MSG@ c(String s, String col) { return @MSG@.raw(s).color(col); }""")
M(later, r"""
public static @IWM@ icon(String id, int n) {
  try { return (@IWM@) new @IS@(id, n).toPacket(); } catch (Throwable t) { return null; }
}""")
# F1: the 9 cards (the colour code of Style Guide 15: gold head words, green gains, dim bar cells)
M(later, r"""
public void card(int i) {
  @MSG@ m = null;
  @MSG@ sec = null;
  @IWM@ it = null;
  @NST@ st = @NST@.Default;
  String what = "";
  if (i == 0) { m = @MSG@.join(new @MSG@[] { c("[Mining 23] ", "@CGOLD@"), c("+42 XP  ", "@CGREEN@"), c("|||||||", "@CGOLD@"), c("---", "@CDIM@"), c("  71%", "@CGOLD@") }); it = icon("Tool_Pickaxe_Iron", 1); what = "skill XP + text bar"; }
  else if (i == 1) { m = @MSG@.join(new @MSG@[] { c("You killed: ", "@CWHITE@"), c("[Lv 9] Trork Mauler", "@CGOLD@") }); sec = c("Elite - +12 Combat XP", "@CDIM@"); what = "kill, gold name, 2nd line"; }
  else if (i == 2) { m = @MSG@.join(new @MSG@[] { c("Fortune! ", "@CGOLD@"), c("Copper Ore x3", "@CWHITE@") }); it = icon("Ore_Copper", 3); what = "Fortune, item icon x3"; }
  else if (i == 3) { m = @MSG@.join(new @MSG@[] { c("[Lifesteal] ", "@CGREEN@"), c("Healed 4", "@CWHITE@") }); what = "heal"; }
  else if (i == 4) { m = @MSG@.join(new @MSG@[] { c("[Copper Collection III] ", "@CGOLD@"), c("1,240 / 2,500  ", "@CWHITE@"), c("|||||", "@CGOLD@"), c("-----", "@CDIM@") }); it = icon("Ore_Copper", 1); what = "collection progress"; }
  else {
    String[] nm = new String[] { "Default", "Success", "Warning", "Danger" };
    int k = i - 5;
    if (k == 1) st = @NST@.Success; else if (k == 2) st = @NST@.Warning; else if (k == 3) st = @NST@.Danger;
    m = c("Style: " + nm[k], "@CWHITE@");
    sec = c("NotificationStyle." + nm[k], "@CDIM@");
    what = "style " + nm[k];
  }
  @NTU@.sendNotification(this.pr.getPacketHandler(), m, sec, (String) null, it, st, (String) null);
  this.sent = this.sent + 1;
  @PKG@.ProbeLog.info("F1 card " + (i + 1) + " of 9 sent: " + what);
}""")
# F2: 5 cards with the SAME tag (does the client replace the card in place?)
M(later, r"""
public void tagCard(int i) {
  @MSG@ m = @MSG@.join(new @MSG@[] { c("[Mining 23] ", "@CGOLD@"), c("+" + (10 * (i + 1)) + " XP", "@CGREEN@") });
  @NTU@.sendNotification(this.pr.getPacketHandler(), m, (@MSG@) null, (String) null, icon("Tool_Pickaxe_Iron", 1), @NST@.Default, "skyy:xp:Mining");
  this.sent = this.sent + 1;
  @PKG@.ProbeLog.info("F2 card " + (i + 1) + " of 5 sent with tag skyy:xp:Mining (+" + (10 * (i + 1)) + " XP)");
}""")
M(later, r"""
public void spawn(String id, double x, double y, double z, java.util.List viewers, @ST@ st) {
  @PTU@.spawnParticleEffect(id, (@V3DC@) new @V3D@(x, y, z), viewers, (@CAC@) st);
}""")
# G1: one step a second for 21 s: A (0-6) our dot per spot, B (7-13) the vanilla glow per spot, C (14-20) ONE rotated system of 6 dots
M(later, r"""
public void trail(int i) {
  @REF@ ref = this.pr.getReference();
  if (ref == null) { this.fails = this.fails + 1; return; }
  @ST@ st = ref.getStore();
  @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) { this.fails = this.fails + 1; @PKG@.ProbeLog.warn("G1 step " + i + ": no position"); return; }
  @V3D@ p = tc.getPosition();
  if (!this.haveTarget) {
    this.tx = p.x; this.ty = p.y; this.tz = p.z - 48.0; this.haveTarget = true;
    @PKG@.ProbeLog.tell(this.pr, "G1 started: the target is 48 blocks away (towards -Z from where you stood). Follow the trail for 21 s.");
  }
  double dx = this.tx - p.x;
  double dz = this.tz - p.z;
  double dist = Math.sqrt(dx * dx + dz * dz);
  java.util.ArrayList viewers = new java.util.ArrayList();
  viewers.add(ref);
  String v = i < 7 ? "A" : (i < 14 ? "B" : "C");
  if (i == 0) @PKG@.ProbeLog.chat(this.pr, "G1 trail A (0-6 s): our own dot picture, 7 dots ahead of you towards the target.");
  if (i == 7) @PKG@.ProbeLog.chat(this.pr, "G1 trail B (7-13 s): the vanilla glow in gold, same spots.");
  if (i == 14) @PKG@.ProbeLog.chat(this.pr, "G1 trail C (14-20 s): ONE effect of 6 dots, turned towards the target (Rotation3f yaw).");
  float pyaw = tc.getRotation() == null ? 0.0f : tc.getRotation().yaw();
  float yaw = 0.0f;
  if (dist > 2.5) {
    double ux = dx / dist;
    double uz = dz / dist;
    if (v.equals("C")) {
      @R3F@ rot = new @R3F@();
      yaw = (float) Math.atan2(-ux, -uz);
      rot.setYaw(yaw);
      @PTU@.spawnParticleEffect("SkyyUiProbe_TrailC", (@V3DC@) new @V3D@(p.x + ux * 0.5, p.y + 0.15, p.z + uz * 0.5), rot, viewers, (@CAC@) st);
      this.dotsC = this.dotsC + 6;
    } else {
      for (int k = 0; k < 7; k++) {
        double d = 2.0 + 1.5 * k;
        if (d > dist - 1.0) break;
        spawn("SkyyUiProbe_Trail" + v, p.x + ux * d, p.y + 0.15, p.z + uz * d, viewers, st);
        if (v.equals("A")) this.dotsA = this.dotsA + 1; else this.dotsB = this.dotsB + 1;
      }
    }
  }
  if (i % 5 == 0) {
    @PKG@.ProbeLog.chat(this.pr, "Objective: Probe target - " + Math.round(dist) + " blocks   (G1 chat stand-in for the HUD label above the hotbar)");
    @PKG@.ProbeLog.info("G1 step " + i + ": distance " + Math.round(dist) + ", your yaw " + pyaw + ", trail C yaw " + yaw + " (radians; trail " + v + ")");
  }
  if (dist <= 3.0 && !this.reached) {
    this.reached = true;
    @PKG@.ProbeLog.tell(this.pr, "G1 PASS (server) - you reached the target. Skyy: look - did the trail lead you here?");
  }
}""")
M(later, r"""
public void tick() {
  if (this.pr == null || !this.pr.isValid()) { @PKG@.ProbeLog.info(this.kind.toUpperCase() + " stopped at step " + this.step + ": the player left"); return; }
  if (this.kind.equals("f1")) {
    card(this.step);
    this.step = this.step + 1;
    if (this.step < 9) { next(250L); return; }
    @PKG@.ProbeLog.tell(this.pr, "F1 PASS (server) - 9 cards sent to the vanilla feed. Skyy: look - readable? colours? stacked with pickups? Screenshot, then /skyprobe next");
    return;
  }
  if (this.kind.equals("f2")) {
    tagCard(this.step);
    this.step = this.step + 1;
    if (this.step < 5) { next(300L); return; }
    @PKG@.ProbeLog.tell(this.pr, "F2 PASS (server) - 5 cards with ONE tag sent. Skyy: look - one card counting up to +50 XP, or five cards? Then /skyprobe next");
    return;
  }
  if (this.kind.equals("g1")) {
    trail(this.step);
    this.step = this.step + 1;
    if (this.step < 21) { next(1000L); return; }
    @PKG@.ProbeLog.tell(this.pr, "G1 PASS (server) - 21 s of trail sent to you only: A " + this.dotsA + " dots, B " + this.dotsB + " dots, C " + this.dotsC + " dots" + (this.fails > 0 ? " (" + this.fails + " steps without a position)" : "") + ". Skyy: look - which trail reads best? Did C point at the target like A and B? The tour is done - thank you!");
    return;
  }
}""")
M(later, r"""
public void run() {
  if (!this.hop) {
    this.hop = true;
    try { this.world.execute(this); } catch (Throwable t) { this.hop = false; @PKG@.ProbeLog.warn(this.kind.toUpperCase() + " could not reach the world thread: " + t); }
    return;
  }
  this.hop = false;
  try { tick(); }
  catch (Throwable t) {
    @PKG@.ProbeLog.warn(this.kind.toUpperCase() + " step " + this.step + " FAIL: " + t);
    @PKG@.ProbeLog.chat(this.pr, this.kind.toUpperCase() + " FAIL - " + t);
  }
}""")

# ---- MapPage: one inline page per case (switched in place by rebuild); every click answered with ONE packet, every result logged
for _f in ("public String cs;", "public int ci;", "public int clicks;", "public int builds;", "public int m4;", "public int sel;",
           "public int lastAlt;", "public int m8n;", "public int ox;", "public int oy;", "public int picN;", "public String picPath;",
           "public boolean picSentBefore;", "public @PKG@.HeadResult head;", "public int dpage;", "public int lastElements;",
           "public int lastBytes;", "public int lastBinds;", "public long lastMs;", "public long sumMs;", "public boolean quiet;",
           "public boolean answered;", "public int answers;", "public int nets;"):
    F(page_c, _f)
C(page_c, r"""
public MapPage(@PR@ pr, String c) {
  super(pr, @LIFE@.CanDismiss);
  this.cs = c;
  this.ci = @PKG@.ProbeData.index(c);
  this.sel = @PKG@.ProbeData.SEL0;
  this.lastAlt = -1;
}""")
M(page_c, r"""
public String tag() { return this.cs.toUpperCase() + " " + @PKG@.ProbeData.NAMES[this.ci]; }""")
M(page_c, r"""
public boolean big() { return this.cs.startsWith("m8"); }""")
M(page_c, r"""
public static @ANC@ anchor(int l, int t, int w, int h) {
  @ANC@ a = new @ANC@();
  a.setLeft(@VAL@.of(Integer.valueOf(l)));
  a.setTop(@VAL@.of(Integer.valueOf(t)));
  a.setWidth(@VAL@.of(Integer.valueOf(w)));
  a.setHeight(@VAL@.of(Integer.valueOf(h)));
  return a;
}""")
M(page_c, r"""
public void haloTo(@UCB@ b, int k) {
  @PKG@.ProbeData.nodes();
  if (big()) b.setObject("#@PFX@Sel.Anchor", anchor(@PKG@.ProbeData.NX2[k] - 44, @PKG@.ProbeData.NY2[k] - 44, 88, 88));
  else b.setObject("#@PFX@Sel.Anchor", anchor(@PKG@.ProbeData.NX[k] - 22, @PKG@.ProbeData.NY[k] - 22, 44, 44));
}""")
M(page_c, r"""
public void panTo(@UCB@ b) {
  if (this.cs.equals("m8b")) b.setObject("#@PFX@Mp.Anchor", anchor(-this.ox, -this.oy, @W2@, @H2@));
  else b.setObject("#@PFX@Cv.Anchor", anchor(-this.ox, -this.oy, @W2@, @H2@));
  b.set("#@PFX@MvS.Text", "Offset " + this.ox + ", " + this.oy + " (of " + (@W2@ - @CVW@) + ", " + (@H2@ - @MAINH@) + ")");
}""")
M(page_c, r"""
public void d1Texts(@UCB@ b) {
  int n = @PKG@.ProbeData.D1.length;
  boolean last = this.dpage >= n - 1;
  b.set("#@PFX@DLn.Text", @PKG@.ProbeData.D1[this.dpage]);
  b.set("#@PFX@DPg.Text", "line " + (this.dpage + 1) + " / " + n);
  b.set("#@PFX@DRw.Text", last ? @PKG@.ProbeData.D1REWARD : "");
  b.set("#@PFX@DNx.Visible", !last);
  b.set("#@PFX@DAc.Visible", last);
  b.set("#@PFX@DNo.Visible", last);
  b.set("#@PFX@DSk.Visible", !last);
}""")
M(page_c, r"""
public void headTexts(@UCB@ b) {
  @PKG@.HeadResult h = this.head;
  if (h == null) { b.set("#@PFX@HcN.Text", "Head: not drawn yet"); return; }
  if (h.path != null) { b.set("#@PFX@Hc.AssetPath", h.path); b.set("#@PFX@Hd.AssetPath", h.path); b.set("#@PFX@He.AssetPath", h.path); }
  b.set("#@PFX@HcN.Text", (h.ok ? "Drawn in " + h.ms + " ms: " + h.drawn + " faces of " + h.faces + " visible" : "Not drawn") + " - " + h.note);
  int rows = @HROWS@;
  for (int i = 0; i < rows; i++) {
    String t = "-";
    if (h.parts != null) {
      int a = i * 2;
      t = (a < h.parts.length ? h.parts[a] : "") + (a + 1 < h.parts.length ? "     " + h.parts[a + 1] : "");
    }
    b.set("#@PFX@HcL" + i + ".Text", t);
  }
}""".replace("@HROWS@", str(HEAD_ROWS)))
M(page_c, r"""
public void dyn(@UCB@ b) {
  if (this.cs.equals("m4")) {
    b.set("#@PFX@A1.AssetPath", @PKG@.ProbeData.M4_2X[this.m4]);
    b.set("#@PFX@A2.AssetPath", @PKG@.ProbeData.M4_1X[this.m4]);
    b.set("#@PFX@A4S.Text", @PKG@.ProbeData.M4_TEXT[this.m4]);
  }
  if (this.cs.equals("m8a")) {
    if (this.lastAlt >= 0) b.set("#@PFX@N" + this.lastAlt + "V.Visible", true);
    b.set("#@PFX@Ad.AssetPath", @PKG@.ProbeData.M4_2X[this.m8n % @PKG@.ProbeData.M4_2X.length]);
  }
  if (this.cs.equals("m8b") || this.cs.equals("m8c")) { if (this.cs.equals("m8b") || this.ox != 0 || this.oy != 0) panTo(b); }
  if ((this.cs.equals("h1a") || this.cs.equals("h1b")) && this.picPath != null) {
    b.set("#@PFX@Hp.AssetPath", this.picPath);
    b.set("#@PFX@HpN.Text", "Picture " + (this.picN + 1) + ": " + this.picPath);
  }
  if (this.cs.equals("h1c")) headTexts(b);
  if (this.cs.equals("d1")) d1Texts(b);
}""")
# THE answer to a click that changes nothing else: ONE short page update (the caption line, + the talent name on map pages)
M(page_c, r"""
public void say(String cap, String name) {
  @UCB@ ub = new @UCB@();
  ub.set("#@PFX@TCap.Text", cap == null ? "" : cap);
  if (name != null) ub.set("#@PFX@TName.Text", name);
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(page_c, r"""
public void update(@UCB@ ub) {
  this.answered = true;
  this.answers = this.answers + 1;
  this.sendUpdate(ub);
}""")
M(page_c, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  long t0 = System.nanoTime();
  String[] l = @PKG@.ProbeData.lines(this.cs);
  int els = 0;
  int bytes = 0;
  int binds = 0;
  for (int i = 0; i < l.length; i++) {
    String s = l[i];
    char k = s.charAt(0);
    int a = s.indexOf('\t', 2);
    String x = s.substring(2, a);
    String y = s.substring(a + 1);
    if (k == 'A') {
      b.appendInline(x.length() == 0 ? (String) null : x, y);
      bytes = bytes + y.length();
      boolean q = false;
      for (int j = 0; j < y.length(); j++) { char c = y.charAt(j); if (c == '"') q = !q; else if (c == '{' && !q) els = els + 1; }
    } else if (k == 'S') {
      b.set(x, y);
    } else if (k == 'E') {
      ev.addEventBinding(@BT@.Activating, x, @EVD@.of("a", y));
      binds = binds + 1;
    }
  }
  dyn(b);
  if (this.cs.equals("m5") || (this.ci >= 0 && this.sel != @PKG@.ProbeData.SEL0 && (this.cs.startsWith("m5") || big()))) haloTo(b, this.sel);
  long ms = (System.nanoTime() - t0) / 1000000L;
  this.builds = this.builds + 1;
  this.lastElements = els;
  this.lastBytes = bytes;
  this.lastBinds = binds;
  this.lastMs = ms;
  this.sumMs = this.sumMs + ms;
  if (!this.quiet) @PKG@.ProbeLog.info(tag() + " build #" + this.builds + ": " + els + " elements, " + (bytes / 1024) + " KB markup, " + binds + " click bindings, built in " + ms + " ms");
}""")
# what a case needs BEFORE its page packet goes out: the H1 pictures (sent first), the H1c head (composed + sent first)
M(page_c, r"""
public void enter(@REF@ ref, @ST@ st) {
  @PR@ pr = this.playerRef;
  if (this.cs.equals("h1a") || this.cs.equals("h1b")) {
    try {
      @PKG@.RtAsset a = @PKG@.RtPic.initialsAsset(pr, this.picN);
      boolean now = @PKG@.RtPic.send(pr, a);
      this.picPath = a.getName();
      if (this.cs.equals("h1a")) @PKG@.ProbeLog.tell(pr, "H1a picture " + a.getName() + " (" + a.bytes.length + " bytes) " + (now ? "sent now, BEFORE this case page" : "was sent when the tour / page started, BEFORE any page") + " - PASS (server). Skyy: look - do you see it?");
    } catch (Throwable t) {
      this.picPath = null;
      @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " FAIL - the runtime picture could not be made: " + t);
    }
  }
  if (this.cs.equals("h1c")) {
    this.head = @PKG@.Heads.compose(pr, ref, st);
    @PKG@.HeadResult h = this.head;
    if (h.parts != null) {
      StringBuilder all = new StringBuilder("H1c your 20 skin parts: ");
      for (int i = 0; i < h.parts.length; i++) all.append(i > 0 ? " | " : "").append(h.parts[i]);
      @PKG@.ProbeLog.info(all.toString());
      for (int i = 0; i < h.parts.length; i = i + 5) {
        StringBuilder sb = new StringBuilder("H1c parts " + (i + 1) + "-" + Math.min(h.parts.length, i + 5) + ": ");
        for (int j = i; j < Math.min(h.parts.length, i + 5); j++) sb.append(j > i ? "; " : "").append(h.parts[j]);
        @PKG@.ProbeLog.chat(pr, sb.toString());
      }
    }
    if (h.ok) @PKG@.ProbeLog.tell(pr, "H1c head drawn from the installed game files in " + h.ms + " ms (" + h.drawn + " faces, " + h.png.length + " bytes, " + (h.sentNow ? "sent now" : "already sent") + ") - PASS (server). " + h.note + " Skyy: look - is that you, hair included?");
    else @PKG@.ProbeLog.tell(pr, "H1c FAIL - no head: " + h.note);
  }
}""")
M(page_c, r"""
public void announce() {
  @PKG@.ProbeLog.tell(this.playerRef, "Case " + (this.ci + 1) + " of @NCASE@: " + tag() + " opened (" + this.lastElements + " elements, " + (this.lastBytes / 1024) + " KB markup, built in " + this.lastMs + " ms) - PASS (server) if the page shows. " + @PKG@.ProbeData.WHAT[this.ci]);
}""")
M(page_c, r"""
public void switchTo(int i, @REF@ ref, @ST@ st) {
  this.cs = @PKG@.ProbeData.KEYS[i]; this.ci = i; this.clicks = 0; this.m4 = 0; this.sel = @PKG@.ProbeData.SEL0; this.lastAlt = -1;
  this.m8n = 0; this.ox = 0; this.oy = 0; this.dpage = 0;
  @PKG@.ProbeData.remember(this.playerRef, i);
  enter(ref, st);
  this.answered = true;
  this.answers = this.answers + 1;
  rebuild();
  announce();
}""")
M(page_c, r"""
public void node(@PR@ pr, int k) {
  @PKG@.ProbeData.nodes();
  if (k < 0 || k >= @PKG@.ProbeData.NODES) { @PKG@.ProbeLog.tell(pr, tag() + " FAIL - click on an unknown node " + k); say("Unknown node " + k + " - nothing selected", null); return; }
  this.clicks = this.clicks + 1;
  String nm = @PKG@.ProbeData.LABEL[k];
  int cut = nm.lastIndexOf(" - ");
  String nm1 = cut > 0 ? nm.substring(0, cut) : nm;
  String nm2 = cut > 0 ? nm.substring(cut + 3) : nm;
  if (this.cs.equals("m5") || big()) {
    this.sel = k;
    @UCB@ ub = new @UCB@();
    haloTo(ub, k);
    int sets = 3;
    if (this.cs.equals("m8a")) {
      if (this.lastAlt >= 0 && this.lastAlt != k) { ub.set("#@PFX@N" + this.lastAlt + "V.Visible", false); sets++; }
      ub.set("#@PFX@N" + k + "V.Visible", true);
      this.lastAlt = k;
      this.m8n = this.m8n + 1;
      ub.set("#@PFX@Ad.AssetPath", @PKG@.ProbeData.M4_2X[this.m8n % @PKG@.ProbeData.M4_2X.length]);
      sets = sets + 2;
    }
    ub.set("#@PFX@TName.Text", nm2);
    ub.set("#@PFX@TCap.Text", "Click " + this.clicks + ": " + nm1 + " - ONE update, no rebuild");
    update(ub);
    if (this.cs.equals("m5")) @PKG@.ProbeLog.tell(pr, "M5 sent: ONE Anchor update moved the halo to node " + k + " (" + nm + ") + 2 panel texts, no rebuild - Skyy: look, did only the halo jump?");
    else @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " click " + this.clicks + ": node " + k + " (" + nm2 + ") answered with ONE update of " + sets + " changes (halo" + (this.cs.equals("m8a") ? ", node picture Visible, disc AssetPath" : "") + ", texts), no rebuild");
    if (this.cs.equals("m8a") && this.clicks == 3) @PKG@.ProbeLog.tell(pr, "M8a PASS (server) - 3 node clicks, 3 updates, 0 rebuilds. Skyy: look - did the view stay where you scrolled it?");
    return;
  }
  say("Click " + this.clicks + ": " + nm1, nm2);
  @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " click " + this.clicks + " reached the server: node " + k + " = " + nm + " (answered: the panel names it)");
}""")
M(page_c, r"""
public void pan(@PR@ pr, String how) {
  int mx = @W2@ - @CVW@;
  int my = @H2@ - @MAINH@;
  if (how.equals("rebuild")) {
    this.answered = true;
    this.answers = this.answers + 1;
    rebuild();
    @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " Rebuild at the server-kept offset " + this.ox + ", " + this.oy + " - Skyy: look, same view after the redraw?");
    return;
  }
  if (how.equals("left")) this.ox = this.ox - @PSTEP@;
  else if (how.equals("right")) this.ox = this.ox + @PSTEP@;
  else if (how.equals("up")) this.oy = this.oy - @PSTEP@;
  else if (how.equals("down")) this.oy = this.oy + @PSTEP@;
  else if (how.equals("reset")) { this.ox = 0; this.oy = 0; }
  else if (how.equals("centre")) {
    @PKG@.ProbeData.nodes();
    this.ox = @PKG@.ProbeData.NX2[this.sel] - @CVW@ / 2;
    this.oy = @PKG@.ProbeData.NY2[this.sel] - @MAINH@ / 2;
  }
  if (this.cs.equals("m8b")) {
    this.ox = Math.max(0, Math.min(mx, this.ox));
    this.oy = Math.max(0, Math.min(my, this.oy));
  }
  @UCB@ ub = new @UCB@();
  panTo(ub);
  update(ub);
  @PKG@.ProbeLog.tell(pr, this.cs.toUpperCase() + " pan " + how + ": ONE Anchor update -> offset " + this.ox + ", " + this.oy + (this.cs.equals("m8c") ? " (inside the scroll box: does the wheel still pan?)" : " - Skyy: look, did the map move inside the box only?"));
}""")
M(page_c, r"""
public void run(@PR@ pr, @ST@ st) {
  String k = this.cs;
  this.answered = true;
  close();
  if (k.equals("k1")) {
    @PKG@.ProbeLog.tell(pr, "K1 page closed. Skyy: look - with a class and 2 abilities on, do the bottom-right vanilla boxes show Mouse 5 / Q / E with OUR class icons? Screenshot, then /skyprobe next");
    return;
  }
  @WLD@ w = null;
  try { w = ((@ES@) st.getExternalData()).getWorld(); } catch (Throwable t) { w = null; }
  if (w == null) { @PKG@.ProbeLog.tell(pr, k.toUpperCase() + " FAIL - no world for the timed test"); return; }
  @PKG@.Later l = new @PKG@.Later(k, pr, w);
  long ms = k.equals("f1") ? 1000L : (k.equals("f2") ? 600L : 500L);
  l.next(ms);
  @PKG@.ProbeLog.tell(pr, k.toUpperCase() + " page closed FIRST; the test starts in " + ms + " ms" + (k.equals("g1") ? " and runs 21 s" : ""));
}""")
M(page_c, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String d) {
  @PR@ pr = this.playerRef;
  String a = @PKG@.ProbeData.act(d);
  this.answered = false;                         // every path below answers with exactly ONE page packet (or the close)
  try {
    if (a.equals("close")) { @PKG@.ProbeLog.info(tag() + " closed with the Close button by " + pr.getUsername()); this.answered = true; close(); return; }
    if (a.equals("next") || a.equals("back") || a.startsWith("case:")) {
      int i = a.equals("next") ? this.ci + 1 : (a.equals("back") ? this.ci - 1 : @PKG@.ProbeData.index(a.substring(5)));
      if (a.equals("next") && i >= @NCASE@) { @PKG@.ProbeLog.tell(pr, "That was the last case - the tour is done."); say("This is the last case - the tour is done", null); return; }
      if (a.equals("back") && i < 0) { say("This is the first case", null); return; }
      if (i < 0) { @PKG@.ProbeLog.tell(pr, "FAIL - unknown case " + a.substring(5)); say("No case '" + a.substring(5) + "' - nothing changed", null); return; }
      switchTo(i, ref, st);
      return;
    }
    if (a.startsWith("n")) { node(pr, Integer.parseInt(a.substring(1))); return; }
    if (a.equals("m4next")) {
      this.m4 = (this.m4 + 1) % @PKG@.ProbeData.M4_2X.length;
      @UCB@ ub = new @UCB@();
      dyn(ub);
      update(ub);
      @PKG@.ProbeLog.tell(pr, "M4 sent: " + @PKG@.ProbeData.M4_TEXT[this.m4] + " - only 2 AssetPath sets + 1 text, no rebuild. Skyy: look - which discs changed (left 2x path, middle 1x path; right = control, never changes)?");
      return;
    }
    if (a.startsWith("tip")) { @PKG@.ProbeLog.tell(pr, "M6 click on tooltip disc " + a.substring(3) + " reached the server"); say("M6: tooltip disc " + a.substring(3) + " clicked", null); return; }
    if (a.startsWith("pan:")) { pan(pr, a.substring(4)); return; }
    if (a.equals("h1bnew")) {
      this.picN = this.picN + 1;
      @PKG@.RtAsset pa = @PKG@.RtPic.initialsAsset(pr, this.picN);
      boolean now = @PKG@.RtPic.send(pr, pa);
      this.picPath = pa.getName();
      @UCB@ ub = new @UCB@();
      ub.set("#@PFX@Hp.AssetPath", this.picPath);
      ub.set("#@PFX@HpN.Text", "Picture " + (this.picN + 1) + ": " + this.picPath);
      ub.set("#@PFX@TCap.Text", "Click " + this.picN + ": picture " + (now ? "sent" : "already on your client") + ", then ONE update set its path");
      update(ub);
      @PKG@.ProbeLog.tell(pr, "H1b click " + this.picN + ": picture " + pa.getName() + " " + (now ? "sent while the page is open" : "was already sent") + " + ONE update (AssetPath + 2 texts), no rebuild. Skyy: look - did the square change colour?");
      return;
    }
    if (a.equals("h1credraw")) {
      this.head = @PKG@.Heads.compose(pr, ref, st);
      @UCB@ ub = new @UCB@();
      headTexts(ub);
      ub.set("#@PFX@TCap.Text", "Redrawn in " + this.head.ms + " ms" + (this.head.sentNow ? " - a new picture was sent" : " - same picture (your skin did not change)"));
      update(ub);
      @PKG@.ProbeLog.tell(pr, "H1c redraw: " + (this.head.ok ? "drawn in " + this.head.ms + " ms, " + (this.head.sentNow ? "new picture sent" : "same picture") : "FAIL - " + this.head.note));
      return;
    }
    if (a.equals("h1cparts")) {
      @PKG@.HeadResult h = this.head;
      if (h != null && h.parts != null) for (int i = 0; i < h.parts.length; i++) @PKG@.ProbeLog.chat(pr, "H1c part " + (i + 1) + ": " + h.parts[i]);
      @PKG@.ProbeLog.info("H1c parts printed to chat");
      say(h == null || h.parts == null ? "No skin parts to print" : "Your 20 skin parts are in chat", null);
      return;
    }
    if (a.equals("dskip") || a.equals("dnext")) {
      int n = @PKG@.ProbeData.D1.length;
      this.dpage = a.equals("dskip") ? n - 1 : Math.min(n - 1, this.dpage + 1);
      this.answered = true;
      this.answers = this.answers + 1;
      rebuild();
      @PKG@.ProbeLog.tell(pr, "D1 " + (a.equals("dskip") ? "Skip -> the last line" : "Next") + " -> line " + (this.dpage + 1) + " of " + n + ": ONE rebuild. Skyy: look - the world still visible above the bar?");
      return;
    }
    if (a.equals("daccept") || a.equals("dnotnow")) {
      @UCB@ ub = new @UCB@();
      ub.set("#@PFX@TCap.Text", a.equals("daccept") ? "Accepted - the real bar starts the quest and closes here" : "Not now - the real bar closes here, no quest");
      ub.set("#@PFX@DRw.Text", a.equals("daccept") ? "Quest accepted" : "Maybe later");
      update(ub);
      @PKG@.ProbeLog.tell(pr, "D1 " + (a.equals("daccept") ? "Accept" : "Not now") + " answered with ONE update - PASS (server). Skyy: look - then press Esc: does the bar close cleanly?");
      return;
    }
    if (a.startsWith("tile")) { @PKG@.ProbeLog.tell(pr, "T1 tile " + a.substring(4) + " clicked - answered"); say("T1: tile " + a.substring(4) + " clicked - the real tile opens its page", null); return; }
    if (a.equals("run")) { run(pr, st); return; }
    @PKG@.ProbeLog.warn(tag() + " unknown click data: " + d);
    say("Unknown click - nothing changed", null);
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn(tag() + " FAIL - the click '" + a + "' failed: " + t);
    @PKG@.ProbeLog.chat(pr, tag() + " FAIL - the click failed: " + t);
  } finally {
    if (!this.answered) {                        // the safety net: nothing was sent (an error) - the engine's empty update ends "Loading..."
      this.answered = true;
      this.nets = this.nets + 1;
      this.answers = this.answers + 1;
      try { this.sendUpdate(); } catch (Throwable t2) { @PKG@.ProbeLog.warn(tag() + " the empty answer failed: " + t2); }
    }
  }
}""")
M(page_c, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  String extra = "";
  if (this.cs.equals("m6")) extra = ". M6: Skyy: look - was a tooltip showing when you pressed Esc, and did the game stay fine?";
  if (this.cs.equals("d1")) extra = ". D1: Esc closed the dialogue bar - PASS (server)";
  @PKG@.ProbeLog.info(tag() + " page closed (Esc or Close) by " + this.playerRef.getUsername() + " after " + this.clicks + " clicks - server OK" + extra);
}""")


# ---- Tips (0.9, Price-Tooltips-Spec R0): per-player runtime tooltip texts - ONE UpdateTranslations(AddOrUpdate) packet to ONE player.
# Memory only; never a lang file, never an ItemStack already in an inventory. writeNoCache is safe off the world thread (patch header).
F(tips, "public static int SENT = 0;")
F(tips, "public static int GEARS = 0;")
F(tips, "public static int LINE = 0;")
F(tips, "public static String LASTKEYS = \"\";")
F(tips, "public static String LASTTHREAD = \"\";")
M(tips, r"""
public static String stdKey(String id) { return "server.items." + id + ".description"; }""")
M(tips, r"""
public static Object item(String id) {
  try { return @ITM@.getAssetMap().getAsset(id); } catch (Throwable t) { return null; }
}""")
M(tips, r"""
public static String keyOf(String id) {
  Object o = item(id);
  if (o != null) {
    try {
      String k = ((@ITM@) o).getDescriptionTranslationKey();
      if (k != null && k.length() > 0) return k;
    } catch (Throwable t) { }
  }
  return stdKey(id);
}""")
M(tips, r"""
public static String lang(@PR@ pr) {
  String l = null;
  try { if (pr != null) l = pr.getLanguage(); } catch (Throwable t) { l = null; }
  return (l == null || l.length() == 0) ? "en-US" : l;
}""")
M(tips, r"""
public static String base(@PR@ pr, String key) {
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    java.util.Map mm = m.getMessages(lang(pr));
    Object v = mm == null ? null : mm.get(key);
    if (v != null) return (String) v;
    return m.getMessage(lang(pr), key);
  } catch (Throwable t) { return null; }
}""")
M(tips, r"""
public static String clean(String t) {
  String s = t == null ? "" : t.trim();
  if (s.length() >= 2 && s.charAt(0) == '"' && s.charAt(s.length() - 1) == '"') s = s.substring(1, s.length() - 1);
  return s.replace("\\n", "\n");
}""")
M(tips, r"""
public static String show(String s) {
  if (s == null) return "(none)";
  if (s.length() == 0) return "(empty)";
  String o = s.replace("\n", " / ");
  return o.length() > 140 ? o.substring(0, 137) + "..." : o;
}""")
M(tips, r"""
public static boolean send(@PR@ pr, java.util.Map m, String why) {
  if (pr == null || m == null || m.isEmpty()) return false;
  try {
    @PH@ ph = pr.getPacketHandler();
    if (ph == null) { @PKG@.ProbeLog.warn("TIP " + why + ": no packet handler"); return false; }
    ph.writeNoCache(new @UTR@(@UTY@.AddOrUpdate, m));
    SENT = SENT + 1;
    StringBuilder sb = new StringBuilder();
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) { if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }
    LASTKEYS = sb.toString();
    LASTTHREAD = Thread.currentThread().getName();
    @PKG@.ProbeLog.info("TIP " + why + ": ONE UpdateTranslations AddOrUpdate (" + m.size() + " key(s): " + LASTKEYS + ") sent to " + pr.getUsername() + " only, on thread '" + LASTTHREAD + "' - server OK");
    return true;
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn("TIP " + why + " FAIL - the packet could not be sent: " + t);
    return false;
  }
}""")
for _f in ("public @PR@ pr;", "public java.util.Map m;", "public String why;", "public String hint;", "public boolean done;"):
    F(tsend, _f)
C(tsend, "public TipSend(@PR@ pr, java.util.Map m, String why, String hint) { this.pr = pr; this.m = m; this.why = why; this.hint = hint; }")
# the P2 send: runs ON THE PROBE'S TIMER THREAD on purpose (no world hop) - the in-game proof that writeNoCache is fine off the world thread
M(tsend, r"""
public void run() {
  this.done = true;
  try {
    if (this.pr == null || !this.pr.isValid()) { @PKG@.ProbeLog.info("TIP " + this.why + ": the player left - nothing sent"); return; }
    boolean ok = @PKG@.Tips.send(this.pr, this.m, this.why);
    @PKG@.ProbeLog.chat(this.pr, (ok ? "TIP sent now (5 s later, from the timer thread). " : "TIP FAIL - the delayed send failed. ") + this.hint);
  } catch (Throwable t) { @PKG@.ProbeLog.warn("TIP " + this.why + " FAIL: " + t); }
}""")
M(tips, r"""
public static void tip(@PR@ pr, String id0, String text, boolean later) {
  String id = id0 == null ? "" : id0.trim();
  if (id.length() == 0) { @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tip <item id> <text>  (e.g. /uiprobe tip Wood_Oak_Trunk Test 1)"); return; }
  boolean gear = id.equalsIgnoreCase("gear");
  String t = clean(text);
  boolean reset = t.equalsIgnoreCase("reset");
  String key = gear ? "@TIPKEY@" : keyOf(id);
  boolean known = gear || item(id) != null;
  String was = gear ? null : base(pr, key);
  String v = t;
  if (reset) v = gear ? "Probe line (reset)" : (was == null ? "" : was);
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  m.put(key, v);
  if (!gear && !key.equals(stdKey(id))) {
    String v2 = v;
    if (reset) { String w2 = base(pr, stdKey(id)); v2 = w2 == null ? "" : w2; }   // reset: each key gets ITS OWN server text back
    m.put(stdKey(id), v2);
  }
  String what = gear ? "P3 probe item line" : (reset ? "reset " + id : id);
  String hint = gear ? "Skyy: look - hover the probe claws: does the last line now read '" + show(v) + "'?"
                     : "Skyy: look - hover " + id + ": is its text now '" + show(v) + "' (the server's own text was '" + show(was) + "')?";
  if (!known) hint = hint + " NOTE: no item '" + id + "' is loaded on this server - check the id (case matters).";
  if (later) {
    @PKG@.ProbeTimer.after(new @PKG@.TipSend(pr, m, "P2 " + what + " (later)", hint), @TIPMS@L);
    @PKG@.ProbeLog.tell(pr, "TIP P2: in 5 s you get the new text for " + key + " = '" + show(v) + "'. Open your inventory NOW and keep hovering " + (gear ? "the probe claws" : id) + " - does it change while the inventory stays open?");
    return;
  }
  boolean ok = send(pr, m, what);
  @PKG@.ProbeLog.chat(pr, (ok ? "TIP sent: " : "TIP FAIL - not sent: ") + key + (m.size() > 1 ? " (+ " + stdKey(id) + ")" : "") + " = '" + show(v) + "', to you only (one packet). " + hint);
}""")
M(tips, r"""
public static int count(@IC@ ic, String id) {
  int n = 0;
  if (ic == null) return 0;
  int cap = ic.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ s = ic.getItemStack((short) i);
    if (s != null && !s.isEmpty() && id.equals(s.getItemId())) n = n + s.getQuantity();
  }
  return n;
}""")
M(tips, r"""
public static boolean added(@ISTX@ tx) {
  if (tx == null || !tx.succeeded()) return false;
  @IS@ r = tx.getRemainder();
  return r == null || r.isEmpty();
}""")
M(tips, r"""
public static @IS@ probeStack() {
  @MSG@ name = @MSG@.raw("Probe Claws (price tooltip test P3)").color("@CGOLD@");
  @MSG@ desc = @MSG@.join(new @MSG@[] {
    @MSG@.raw("PROBE item (SkyyUiProbe) - not a real item.\nThe next line comes from a translation key:\n").color("@CDIM@"),
    @MSG@.translation("@TIPKEY@") });
  return new @IS@("@TIPIT@", 1).withMetadata(@IDM@.KEYED_CODEC, new @IDM@(name, desc));
}""")
M(tips, r"""
public static void gear(@REF@ ref, @ST@ store, @PR@ pr) {
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - no player component"); return; }
  @INV@ inv = p.getInventory();
  if (inv == null) { @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - no inventory"); return; }
  int before = count(inv.getStorage(), "@TIPIT@") + count(inv.getHotbar(), "@TIPIT@");
  boolean ok = false;
  try {
    ok = added(inv.getStorage().addItemStack(probeStack()));
    if (!ok) ok = added(inv.getHotbar().addItemStack(probeStack()));
  } catch (Throwable t) { @PKG@.ProbeLog.warn("TIP P3: adding the probe item failed: " + t); ok = false; }
  int after = count(inv.getStorage(), "@TIPIT@") + count(inv.getHotbar(), "@TIPIT@");
  if (!ok || after - before != 1) {
    @PKG@.ProbeLog.tell(pr, "TIP P3 FAIL - the probe item could not be given (inventory full? counted " + before + " -> " + after + "). Make room and run /uiprobe tipgear again.");
    return;
  }
  GEARS = GEARS + 1;
  LINE = LINE + 1;
  String v = "NPC Sell: <color is=\"@CGOLD@\"><b>320</b></color> each <color is=\"@CDIM@\">(probe line #" + LINE + ", " + new java.text.SimpleDateFormat("HH:mm:ss").format(new java.util.Date()) + ")</color>";
  java.util.LinkedHashMap m = new java.util.LinkedHashMap();
  m.put("@TIPKEY@", v);
  boolean sent = send(pr, m, "P3 probe item line #" + LINE);
  @PKG@.ProbeLog.info("TIP P3: probe item @TIPIT@ given to " + pr.getUsername() + " (counted " + before + " -> " + after + ", storage first) - server OK");
  @PKG@.ProbeLog.chat(pr, "TIP P3: you got 'Probe Claws' (in your inventory). " + (sent ? "" : "FAIL - the key text was not sent. ") + "Skyy: look - hover them: under the grey lines, is there 'NPC Sell: 320 each (probe line #" + LINE + ", time)' with 320 in gold, or a raw key / nothing? Then /uiprobe tip gear Test 3 - does that line change?");
}""")
# ---- ProbeCmds: help, tour, next, open a case (the last case seen per player is kept in memory only)
M(cmds, r"""
public static void help(@PR@ pr) {
  @PKG@.ProbeLog.chat(pr, "UI queue probe (op only, research/UI-Queue-Spec.md section 10). /skyprobe tour walks you through all @NCASE@ cases (~5 minutes); /skyprobe next opens the next one; /skyprobe <case> opens one:");
  for (int i = 0; i < @PKG@.ProbeData.KEYS.length; i++) @PKG@.ProbeLog.chat(pr, (i + 1) + ". " + @PKG@.ProbeData.KEYS[i] + " (" + @PKG@.ProbeData.NAMES[i] + ") - " + @PKG@.ProbeData.HEADS[i].substring(@PKG@.ProbeData.HEADS[i].indexOf(':') + 2));
  @PKG@.ProbeLog.chat(pr, "Each result prints PASS, FAIL or 'Skyy: look' here and in the server log. Start with /skyprobe tour.");
  @PKG@.ProbeLog.chat(pr, "PRICE TOOLTIP PROBE (P1-P5): /uiprobe tip <item id> <text> = a new tooltip text for that item, for you only (\\n = new line, reset = the normal text back); /uiprobe tiplater <item id> <text> = the same 5 s later (open your inventory while you wait); /uiprobe tipgear = probe claws with a line from a translation key; /uiprobe tip gear <text> = change that line.");
  @PKG@.ProbeLog.info("help listed for " + (pr == null ? "?" : pr.getUsername()));
}""")
M(cmds, r"""
public static void open(@REF@ ref, @ST@ store, @PR@ pr, int i) {
  @PLA@ p = null;
  try { p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null) { @PKG@.ProbeLog.tell(pr, "FAIL - the page could not be opened (no player component)"); return; }
  @PKG@.MapPage pg = new @PKG@.MapPage(pr, @PKG@.ProbeData.KEYS[i]);
  @PKG@.ProbeData.remember(pr, i);
  try {
    pg.enter(ref, store);
    p.getPageManager().openCustomPage(ref, store, pg);
  } catch (Throwable t) {
    @PKG@.ProbeLog.warn(pg.tag() + " FAIL - could not open: " + t);
    @PKG@.ProbeLog.chat(pr, pg.tag() + " FAIL - the page could not be opened: " + t);
    return;
  }
  pg.announce();
}""")
M(cmds, r"""
public static void tour(@REF@ ref, @ST@ store, @PR@ pr) {
  try {
    @PKG@.RtAsset a = @PKG@.RtPic.initialsAsset(pr, 0);
    boolean now = @PKG@.RtPic.send(pr, a);
    @PKG@.ProbeLog.info("tour: the H1a picture " + a.getName() + " " + (now ? "sent BEFORE any page" : "was already on this connection"));
  } catch (Throwable t) { @PKG@.ProbeLog.warn("tour: the H1a picture failed: " + t); }
  @PKG@.ProbeLog.chat(pr, "UI queue probe tour: @NCASE@ cases, about 5 minutes. Read the 'Skyy: look' line on each page, then press Next case.");
  open(ref, store, pr, 0);
}""")
M(cmds, r"""
public static void arg(@REF@ ref, @ST@ store, @PR@ pr, String a) {
  String t = a == null ? "" : a.trim().toLowerCase();
  if (t.length() == 0 || t.equals("help") || t.equals("list")) { help(pr); return; }
  if (t.equals("tour")) { tour(ref, store, pr); return; }
  if (t.equals("tipgear")) { @PKG@.Tips.gear(ref, store, pr); return; }
  if (t.equals("tip") || t.equals("tiplater")) { @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe " + t + " <item id> <text>  (e.g. /uiprobe " + t + " Wood_Oak_Trunk Test 1; /uiprobe tip gear <text> for the probe claws)"); return; }
  if (t.equals("next")) {
    Integer last = null;
    if (pr != null) last = (Integer) @PKG@.ProbeData.LAST.get(pr.getUuid());
    int i = last == null ? 0 : last.intValue() + 1;
    if (i >= @NCASE@) { @PKG@.ProbeLog.chat(pr, "The tour is done (that was case @NCASE@). /skyprobe tour starts again."); return; }
    open(ref, store, pr, i);
    return;
  }
  int i = @PKG@.ProbeData.index(t);
  if (i < 0) { @PKG@.ProbeLog.chat(pr, "No case '" + a + "'. /skyprobe help lists them (tour, next, m4, m5, m6, m8a ... g1)."); return; }
  open(ref, store, pr, i);
}""")

M(cmds, r"""
public static void tip3(@PR@ pr, String what, String id, String text) {
  String w = what == null ? "" : what.trim().toLowerCase();
  if (w.equals("tip")) { @PKG@.Tips.tip(pr, id, text, false); return; }
  if (w.equals("tiplater")) { @PKG@.Tips.tip(pr, id, text, true); return; }
  @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe tip <item id> <text>, /uiprobe tiplater <item id> <text> (or /uiprobe help)");
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
cmdA = mk("SkyProbeArgCmd", T["APC"])
F(cmdA, "public @RA@ caseArg;")
C(cmdA, r"""
public SkyProbeArgCmd() {
  super("(admin) /skyprobe tour | next | <case> - the UI queue probe; /skyprobe help lists the cases");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.caseArg = withRequiredArg("what", "tour, next, help, tipgear, or a case: m4, m5, m6, m8a, m8b, m8c, h1a, h1b, h1c, d1, t1, k1, f1, f2, g1", @ATY@.STRING);
}""")
M(cmdA, EXEC + r""" {
  try { @PKG@.ProbeCmds.arg(ref, store, pr, String.valueOf(ctx.get(this.caseArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/skyprobe failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /skyprobe tour, /skyprobe next, /skyprobe <case>"); }
}""")
cmdT = mk("SkyProbeTipCmd", T["APC"])
# a SUB-command (not a usage variant): the engine picks usage variants by the EXACT token count (AbstractCommand.variantCommands is an
# Int2ObjectMap looked up with the token count), so a multi-word text could never reach a 3-argument variant; a sub-command is found by
# its first word, then GREEDY_STRING takes the rest. Two instances: "tip" and "tiplater" (getName() says which).
F(cmdT, "public @RA@ idArg;")
F(cmdT, "public @RA@ textArg;")
C(cmdT, r"""
public SkyProbeTipCmd(String name) {
  super(name, "(admin) /uiprobe " + name + " <item id> <text> - the price-tooltip probe: a new tooltip text for you only" + (name.equals("tiplater") ? ", 5 s later" : ""));
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.idArg = withRequiredArg("item", "an item id (Wood_Oak_Trunk), or gear for the probe claws' line", @ATY@.STRING);
  this.textArg = withRequiredArg("text", "the tooltip text (\\n = new line; reset = the normal text)", @ATY@.GREEDY_STRING);
}""")
M(cmdT, EXEC + r""" {
  try { @PKG@.ProbeCmds.tip3(pr, getName(), String.valueOf(ctx.get(this.idArg)), String.valueOf(ctx.get(this.textArg))); }
  catch (Throwable t) { @PKG@.ProbeLog.warn("/uiprobe " + getName() + " failed: " + t); @PKG@.ProbeLog.chat(pr, "Usage: /uiprobe " + getName() + " <item id> <text>"); }
}""")
cmd = mk("SkyProbeCmd", T["APC"])
C(cmd, r"""
public SkyProbeCmd() {
  super("skyprobe", "(admin) PROBE: the UI queue test pages (15 cases) + the price-tooltip probe (tip / tiplater / tipgear) - /skyprobe help lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "uiprobe" });
  addUsageVariant(new @PKG@.SkyProbeArgCmd());
  addSubCommand(new @PKG@.SkyProbeTipCmd("tip"));
  addSubCommand(new @PKG@.SkyProbeTipCmd("tiplater"));
}""")
M(cmd, EXEC + r""" {
  @PKG@.ProbeCmds.help(pr);
}""")

pl = mk("SkyyUiProbePlugin", T["JP"])
C(pl, "public SkyyUiProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ProbeLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.SkyProbeCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyUiProbe] @VERSION@ ready - PROBE (op only): /skyprobe tour (alias /uiprobe) walks through the @NCASE@ UI queue cases + /uiprobe tip / tiplater / tipgear (price-tooltip probe P1-P5); no data, no HUD, nothing for players");
}""")
M(pl, "protected void shutdown() { @PKG@.ProbeTimer.stop(); super.shutdown(); }")
CLASSES = [log, data, thr, tim, rta, rtp, hres, heads, later, page_c, cmds, tips, tsend, cmdA, cmdT, cmd, pl]
for c in CLASSES:
    c.writeFile(OUT)
print("classes written: %d" % len(CLASSES))

jar = os.path.join(HERE, "SkyyUiProbe-%s.jar" % VERSION)
man = B.manifest("SkyyUiProbe", VERSION, "SkyWynn DEV PROBE (op only): /skyprobe tour (alias /uiprobe) walks through the 15 UI queue test cases (map retests M4-M6, zoom keep-scroll / clip-pan M8, runtime pictures and your head H1, dialogue bar D1, picture tiles T1, key hints K1, vanilla feed F1 / F2, ground trail G1) + the price-tooltip probe (/uiprobe tip, tiplater, tipgear: P1-P5) for one test session - no data, no config, no HUD, nothing for players. Retire after the test.", PKG + ".SkyyUiProbePlugin")
assert man["IncludesAssetPack"] is True
B.assemble(jar, man, OUT, dict(sorted(ASSETS.items())))
with zipfile.ZipFile(jar) as _jz:
    names = _jz.namelist()
    assert not [n for n in names if n.lower().endswith(".ui")], "inline pages only"
    for n in names:
        if n.endswith(".png"):
            assert n.startswith(TEX_ROOT + "SkyyUiProbe/") or n == "Common/" + DOT_TEX, n
    for p_, b_ in ASSETS.items():
        assert _jz.read(p_) == b_, p_
print("jar: %d entries, %d pictures, %d page data files, %d particle files; build %.1f s" % (
    len(names), sum(1 for n in names if n.endswith(".png")), sum(1 for n in names if n.startswith(RES_DIR)),
    sum(1 for n in names if n.startswith(PART_DIR)), time.time() - T0))
