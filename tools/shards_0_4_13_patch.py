"""Derive SkyyShards/build_skyyshards_0.4.13.py from the GENERATED SkyyShards 0.4.12 (build_skyyshards_0.4.12.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_12_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.12 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_13_patch.py   then   python SkyyShards/build_skyyshards_0.4.13.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.13.py

0.4.13 (2026-10-25) = THE TOTEM PAGE + THE TOTEM BENCH, REBUILT FROM THE APPROVED MOCKUPS (art/ui-totem-page/mockup.html + bench-mockup.html;
  research/Totem-Page-Redesign.md; docs/answered/world.md 2026-10-25 TOTEM PAGE / TOTEM BENCH / TOTEM BENCH STYLE / MOCKUPS APPROVED).
  Skyy: "this whole us for the totem feels clunky, ugly and slow. how can you make it look better, and show what information you need in a
  good way. like i have no idea how the modifiers work, or how i could give it seeds to replant." + (the bench) "make it visual, make it
  pretty, and make it easy to use" + "make it look more like a vanilla bench with the upgrade on the side and stuff."
  1. THE TOTEM PAGE (view 3, 1240 x 900): three columns of cards.
     Left: the totem (its icon on a frame in its tier's rarity colour - I Uncommon, II Rare, III Epic, IV-V Legendary - the name in that
     colour, the tier tag "T2 Totem - pad 1 - <island>", its job), the RANGE card (a picture of the island grid with the cells it works lit
     and the range edge as a dashed ring - one picture per island size + range, our own geometry, Map/Range/S<size>R<range>), the SHOW RANGE
     toggle, Pick up (two clicks).
     Middle: OUTPUT (items / min or + %, crops in range "72 of 112" + a bar, where it goes), SEEDS AND REPLANTING (the seed store, what you
     carry, GIVE SEEDS / TAKE SEEDS right here = the Map tab's seedsGive / seedsTake), BOOSTER (slot, what one essence does, Add booster).
     Right: TIER UP (from -> to, the gain, every cost line green / red "(you have N)" = inventory + Pocket Dimension, the bench note, ONE
     Tier up button), MODIFIERS (the 2 slots with what each does + Remove, then all 6 modifiers with what they do, how many you have, the
     bench tier that crafts them, an Add button on the ones you can add now).
     Only buttons you can use now are drawn; every other place says why (owner only, missing items, bench too low, store full ...).
  2. SHOW RANGE = A REAL AURA, PER PLAYER: a toggle; while on, every second a ring of vanilla Block_Top_Glow particles stands on the range
     edge (radius range + 0.5 around the totem's island centre, the coverage rule of ShTotem.cov) and a rotating fifth of the covered crop
     cells gets a faint Seed_Place_Dust puff - sent to THAT player only (ParticleUtil.spawnParticleEffect(String, Vector3dc, List<Ref>,
     ComponentAccessor), the SkyyZones Z13 way). It stays on while the page is open and totem.rangeAuraSec seconds after it closes
     (Server Setup -> Shards, default 30, 0 = off at once); leaving the shard world ends it. Both particles are Server Setup rows too
     (totem.rangeEdge / totem.rangeCell, checked against the game's particle systems like totem.particle). ShCore.AURA (memory only).
  3. THE TOTEM BENCH (view 4, 1500 x 900) = the vanilla crafting bench layout (client BasicCraftingPanel / BenchInfoPanel: a 72 px recipe
     slot grid, the selected recipe with its ingredient slots, the bench tier panel at the side): the strip (bench + tier + "How totems
     work"), a CATEGORY strip (Workers / Weather / Helpers / Modifiers / Totem Pole), the recipe ICON GRID (rarity edge = the bench tier that
     unlocks it, a state dot: green can craft / gold missing items / red a rule blocks it; a bench-locked recipe is dimmed with "Bench II"),
     the SELECTED RECIPE (big icon, name in its rarity colour, what it does + how to use it, ingredient slots "have / need" incl. the Pocket
     Dimension, coins, ONE Craft button - greyed with the missing part named under it) and the BENCH UPGRADE side panel (tier pips I-IV, what
     the next tier unlocks as icons, its cost slots, coins / collection / time, Upgrade bench). "Make Pole" is the Totem Pole category: the
     hand-held Totem I in your inventory are its recipes. Lists sort by bench tier, then name.
  KEPT: every 0.4.12 payment path (payInvBags, refundPaid, commitBags) and action (bkcraft / brup / bebench / tup / tmodadd / tmodrem /
  tboost / tpick, seedsGive / seedsTake), every older fill (kTx / rTx / fTx / dTx - the Totems tab of the shard menu is unchanged), the
  0.4.10 hotfix. New clicks: bcat<n>, bg<n>, wseed, wseedb, tmodadd<n>; trange toggles the aura (it was a 10 s broadcast circle).
  Every new page variant is walked in order by the harness (every selector exists when its command runs - phases O / O2 + the new O3).
  4. THE LIVE FREEZE (main session, NewBetaTest server log 2026-10-26 02:38: "Abandoning TickingThread ... WorldThread - skyy-island-...
     (stuck for >30000ms)" in ReentrantLock.lock <- ShCore.pauseStale <- ShPage.fill <- ShPage.build <- openCustomPage): a world thread
     waited forever for ShStore.LOCK. ShStore.LOCK is now a ShLock - its lock() gives up after 50 ms on a world thread / 1.5 s elsewhere
     (ShBusy) and logs the holder thread + stack once a minute, so no world thread ever freezes on it and a lock-order inversion with
     another mod's lock (the bridges to SkyySacks / SkyyCoins / SkyyCollections / SkyyIslands called while holding it) breaks by itself;
     a page that meets it shows a small "busy - try again" page, a click says so. ShTick moved off HytaleServer.SCHEDULED_EXECUTOR to
     Shards' own daemon thread SkyyShards-tick (shut down with the plugin).
  5. TOTEM POLES PLACED BY HAND (Skyy: "i should be able to place them wherever i want on the island"): right-click your island's
     farmland in the shard with a totem pole = it stands there (inside the rim, not the centre 3 x 3 pads, not on another totem; the
     island's totem count as before), works the cells in its range around that spot (ShTotem.covAt), shows your range aura for
     totem.rangeAuraSec (min 10 s); Pick up clears its block. Menu placement on the pads is unchanged.
  6. REVIEW FIXES (research/Shards-0.4.13-Review.md, patch section 8): the timed lock may give up anywhere, so benchUp, the placed-totem
     Tier up and a shard craft take the lock BEFORE paying (busy = nothing taken); the Collect's collection / XP credit waits in memory
     when the lock is busy (never dropped); a first-load migration is never cached half done; the placed-totem Tier up keeps a hand-placed
     totem's spot (8th part); grow0's re-lock, ShPlace's check, ShLv20's undo, placeHand's aura and the regrow timestamp are busy-safe.
  SAVED DATA: no migration; a hand-placed totem's entry gets an 8th part "dx;dz" (every other entry byte-identical); three new config rows.
  ROLLBACK 0.4.13 -> 0.4.12: alone. The old list pages come back, Show range is the 10 s circle again, the shared scheduler + plain lock
  again. A hand-placed totem then counts as a pad totem (0.4.12 reads 7 parts) - it is drawn on a pad and its old block stays as a plain
  block until picked up / cleared; pick hand-placed totems up before a rollback to avoid that.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

# ==PAGES==
PAGES = r'''# --- 0.4.13 VIEW 3: THE TOTEM PAGE (art/ui-totem-page/mockup.html, approved 2026-10-25; research/Totem-Page-Redesign.md). Skyy: "this whole
# us for the totem feels clunky, ugly and slow. how can you make it look better, and show what information you need in a good way. like i
# have no idea how the modifiers work, or how i could give it seeds to replant." Three columns of cards: the totem (rarity frame, tier tag,
# range picture, Show range, Pick up) | what it does (output, seeds with Give / Take here, booster) | improve it (tier up with bag-aware
# costs, the 2 modifier slots + what every modifier does and where it is crafted). Only buttons you can use now; every other place says why.
# Every runtime text is a b.set inside its own segment and every conditional element goes into a holder the shell segment drew first
# (HANDOFF section 2 / the 0.4.10 rule: a command never names an element the client does not have yet).
KROWS = len(RECIPES)          # (0.4.2) every recipe of a bench fits the grid
RROWS = 20                    # (0.4.2) hand-held totems listed for Make pole
TQ = ["Uncommon", "Rare", "Epic", "Legendary", "Legendary"]       # the display rarity of a totem tier I-V / a bench tier I-IV (Style Guide 15)
TQC = [SUI.QUALITY[_q] for _q in TQ]
BCATS = ["Workers", "Weather", "Helpers", "Modifiers", "Totem Pole"]
WEATHER_KEYS = ["rain", "sun_blessing", "season_ward", "harvest_moon", "mushroom_shade"]
assert all(_k in [t[0] for t in TOTEMS] for _k in WEATHER_KEYS)
W = "SkyyShW"
WPW, WPH = 1240, 900
shw = SUI.page_shell(W, WPW, WPH, title=J_("this.title", "Harvest Spirit Totem Pole I"), kind="decorated")
WIW, WIH = shw.inner_w, shw.inner_h
WB = "#" + shw.body
WG = 12
WCA = 300
WCB = (WIW - WCA - 2 * WG) // 2
WCC = WIW - WCA - WCB - 2 * WG
WFOOT = 34 + 6 + SUI.BTN_H
WCOLH = WIH - WFOOT - 6
assert (WIW, WIH) == (1206, 828) and WCOLH >= 730, (WIW, WIH, WCOLH)
wa = SUI.Appends()
wa.append((WB, SUI.group(W + "Cols", layout="Left", w=WIW, h=WCOLH, anchor={"bottom": 6})))
for _cid, _cw in (("ColA", WCA), ("ColB", WCB), ("ColC", WCC)):
    if _cid != "ColA":
        wa.append(("#" + W + "Cols", SUI.spacer(w=WG)))
    wa.append(("#" + W + "Cols", SUI.group(W + _cid, layout="Top", w=_cw, h=WCOLH)))
WUSED = {"ColA": 0, "ColB": 0, "ColC": 0}


def wcard(cid, col, cw, h, head, what=None, what_h=22):
    """one card of the totem page: a simple panel, its gold head + a one-line 'what is this' (Style Guide 15)"""
    wa.append(("#" + W + col, SUI.panel(W + cid, "simple", w=cw, h=h, layout="Top", pad=12, anchor={"bottom": WG})))
    wa.text("#" + W + cid, W + cid + "H", head, "section", size=14, h=26, w=cw - 24, col=GOLD)
    if what:
        wa.text("#" + W + cid, W + cid + "W", what, "caption", size=13, h=what_h, w=cw - 24, wrap=what_h > 22)
    WUSED[col] += h + WG
    return "#" + W + cid, cw - 24


# ---- left: the totem
WFR = 116
c_, cw_ = wcard("Tot", "ColA", WCA, 246, "Totem")
wa.append((c_, SUI.group(W + "FrR", layout="Left", w=cw_, h=WFR, anchor={"bottom": 6})))
wa.append(("#" + W + "FrR", SUI.spacer(w=(cw_ - WFR) // 2)))
wa.append(("#" + W + "FrR", SUI.group(W + "Fr", layout=None, w=WFR, h=WFR, bg=J_("this.wRar", TQC[1]))))
wa.append(("#" + W + "Fr", SUI.group(W + "FrIn", layout=None, w=WFR - 4, h=WFR - 4, anchor={"left": 2, "top": 2}, bg="slotBorder")))
wa.append(("#" + W + "FrIn", SUI.item_icon(W + "Ic", J_("this.wItem", TOTEM_ITEM[0]), size=96, anchor={"left": 8, "top": 8})))
wa.text(c_, W + "Nm", J_("this.wName", "Harvest Spirit Totem Pole II"), "bold", size=16, h=28, w=cw_, align="Center", col=J_("this.wRar", TQC[1]))
wa.text(c_, W + "Tg", J_("this.wTag", "T2 Totem - pad 1 - T1 Wheat Island Small"), "default", size=13, h=22, w=cw_, align="Center", col=GOLD)
wa.text(c_, W + "Ro", J_("this.wRole", "Worker - gathers the crops in its range"), "caption", size=13, h=22, w=cw_, align="Center")
# ---- left: the range picture + the Show range toggle
WRP = 200
c_, cw_ = wcard("Rng", "ColA", WCA, 362, "Range")
wa.text(c_, W + "RgT", J_("this.wRgTx", "5 blocks around the totem - 72 of 112 crops"), "default", size=13, h=22, w=cw_)
wa.append((c_, SUI.group(W + "RgP", layout=None, w=cw_, h=WRP, anchor={"bottom": 6})))
wa.text(c_, W + "RgC", J_("this.wRgCap", "Show range draws it in the world for you."), "caption", size=13, h=52, w=cw_, wrap=True)
wa.append((c_, SUI.group(W + "RgB", layout=None, w=cw_, h=SUI.BTN_SMALL_H)))
wa.append(("#" + W + "ColA", SUI.group(W + "PkB", layout=None, w=WCA, h=SUI.BTN_SMALL_H)))
WUSED["ColA"] += SUI.BTN_SMALL_H
# the range pictures (pure Python, our own geometry): the island grid of a size (soil, rim, centre), the cells in range lit green, the
# totem gold, the range edge as a dashed purple ring (the colour of the aura's glow) - one picture per size x range up to full cover
RPMAX = [int(math.ceil(max(math.hypot(_dx, _dz) for _dx, _dz in _crop_tiles(_s)))) for _s in (1, 2, 3)]
RPBASE = [0, RPMAX[0] + 1, RPMAX[0] + RPMAX[1] + 2]
RPART = {"soil": "#3a2a1a", "lit": "#6a8f3a", "rim": "#5c5248", "hub": "#7a6a4e", "totem": "#E8A93B", "ring": "#c85dff"}   # ui-data: picture colours (not UI)


def range_picture(s, r):
    h = HALF[s - 1]
    n = 2 * h + 1
    px = 2 * WRP
    pic = SMAP.Pic(px, px)
    cell = px / float(n)
    tiles = set(_crop_tiles(s))

    def rect(x0, y0, x1, y1, col):
        c = SMAP.rgb(col)
        for yy in range(max(0, int(y0)), min(px, int(y1))):
            for xx in range(max(0, int(x0)), min(px, int(x1))):
                i = (yy * px + xx) * 4
                pic.px[i], pic.px[i + 1], pic.px[i + 2], pic.px[i + 3] = c[0], c[1], c[2], 255
    for dz in range(-h, h + 1):
        for dx in range(-h, h + 1):
            if abs(dx) == h and abs(dz) == h:
                continue
            if (dx, dz) == (0, 0):
                col = RPART["totem"]
            elif (dx, dz) in tiles:
                col = RPART["lit"] if dx * dx + dz * dz <= r * r else RPART["soil"]
            elif abs(dx) <= 1 and abs(dz) <= 1:
                col = RPART["hub"]
            else:
                col = RPART["rim"]
            x0, y0 = (dx + h) * cell, (dz + h) * cell
            rect(x0 + 1, y0 + 1, x0 + cell - 1, y0 + cell - 1, col)
    rr = (r + 0.5) * cell
    k = max(24, int(2 * math.pi * rr / 9.0))
    for i in range(k):
        a = 2 * math.pi * i / k
        SMAP.disc(pic, px / 2.0 + rr * math.cos(a), px / 2.0 + rr * math.sin(a), 2.6, SMAP.rgb(RPART["ring"]), 1.0)
    return pic


RPATHS = []
for _s in (1, 2, 3):
    for _r in range(RPMAX[_s - 1] + 1):
        RPATHS.append(map_ship("Range/S%dR%d" % (_s, _r), range_picture(_s, _r)))
assert len(RPATHS) == RPBASE[2] + RPMAX[2] + 1
wpic = []
for _i, _pth in enumerate(RPATHS):
    _a = SUI.Appends()
    _a.append(("#" + W + "RgP", SUI.map_pic(W + "RgPic", (WCA - 24 - WRP) // 2, 0, WRP, WRP, _pth)))
    wpic.append(_a)
wrg = []
for _on in (False, True):
    _a = SUI.Appends()
    _a.append(("#" + W + "RgB", SUI.button(W + "Rg", "Hide range" if _on else "Show range", "tertiary", "small", w=WCA - 24, selected=_on)))
    wrg.append(_a)
wpk = SUI.Appends()
wpk.append(("#" + W + "PkB", SUI.button(W + "Pick", "Pick up", "secondary", "small", w=WCA)))
wvw = SUI.Appends()
wvw.text("#" + W + "PkB", W + "View", "Only the island owner can change or pick up this totem.", "caption", size=13, h=SUI.BTN_SMALL_H, w=WCA, wrap=True)
# ---- middle: output
WBARW = WCB - 24
c_, cw_ = wcard("Out", "ColB", WCB, 190, "Output", J_("this.wOutW", "What this totem makes while it is placed."))
wa.append((c_, SUI.group(W + "OutR", layout="Left", w=cw_, h=44)))
wa.text("#" + W + "OutR", W + "OutN", J_("this.wOut", "4.05"), "display", size=30, h=44, w=170, col=J_("this.wOutC", GOOD))
wa.text("#" + W + "OutR", W + "OutU", J_("this.wOutU", "items / min"), "default", size=15, h=44, w=cw_ - 170)
wa.text(c_, W + "Out2", J_("this.wOut2", "In range: 72 of 112 crops"), "default", size=14, h=24, w=cw_)
wa.append((c_, SUI.bar(W + "OutB", WBARW, 8, J_("this.wBarF", "180"), col="success", anchor={"bottom": 6})))
wa.text(c_, W + "Out3", J_("this.wOut3", "Goes to the island's storage - collect it on the Collect tab."), "caption", size=13, h=36, w=cw_, wrap=True,
        col=J_("this.wOut3C", SUI.COLOR["caption"]))
# ---- middle: seeds + replanting (Give / Take seeds here = the Map tab's seedsGive / seedsTake of this island)
c_, cw_ = wcard("Sd", "ColB", WCB, 208, "Seeds and replanting", "Give the totem seeds and it replants the harvested cells in its range by itself.", 36)
wa.text(c_, W + "Sd0", J_("this.wSd[0]", "Seed store: 0 Wheat Seeds - 8 of 96 cells Eternal"), "default", size=14, h=24, w=cw_, col=J_("this.wSdC[0]", BAD))
wa.text(c_, W + "Sd1", J_("this.wSd[1]", "You carry 40 Wheat Seeds + 2 Eternal Wheat Seeds"), "default", size=13, h=22, w=cw_, col=J_("this.wSdC[1]", TEXT))
wa.append((c_, SUI.group(W + "SdB", layout="Left", w=cw_, h=SUI.BTN_SMALL_H, anchor={"top": 4, "bottom": 4})))
wa.text(c_, W + "Sd3", J_("this.wSd[3]", "Give seeds takes the ones you carry; each Eternal seed makes one more cell Eternal for good."), "caption", size=13, h=36,
        w=cw_, wrap=True)
wsdg = SUI.Appends()
wsdg.append(("#" + W + "SdB", SUI.button(W + "SdG", "Give seeds", "secondary", "small", w=160, anchor={"right": 10})))
wsdt = SUI.Appends()
wsdt.append(("#" + W + "SdB", SUI.button(W + "SdT", "Take seeds", "secondary", "small", w=160)))
wsdn = SUI.Appends()
wsdn.text("#" + W + "SdB", W + "Sd2", J_("this.wSd[2]", "You carry no Wheat Seeds - get some, then come back."), "default", size=13, h=SUI.BTN_SMALL_H, w=cw_,
          col=J_("this.wSdC[2]", BAD))
# ---- middle: the booster
c_, cw_ = wcard("Bo", "ColB", WCB, 166, "Booster", "A short power-up for this totem.")
wa.append((c_, SUI.group(W + "BoR", layout="Left", w=cw_, h=52, anchor={"bottom": 6})))
wa.append(("#" + W + "BoR", SUI.group(W + "BoI", layout=None, w=48, h=48, bg="slotBorder")))
wa.append(("#" + W + "BoR", SUI.spacer(w=10)))
wa.append(("#" + W + "BoR", SUI.group(W + "BoT", layout="Top", w=cw_ - 58, h=52)))
wa.text("#" + W + "BoT", W + "Bo0", J_("this.wBo[0]", "Empty"), "default", size=14, bold=True, h=22, w=cw_ - 58, col=J_("this.wBoC[0]", SUI.COLOR["rowName"]))
wa.text("#" + W + "BoT", W + "Bo1", J_("this.wBo[1]", "1 Life, Water or Void Essence = +2 range and +25 % for 10 min"), "caption", size=13, h=30, w=cw_ - 58,
        wrap=True, col=GOOD)
wa.append((c_, SUI.group(W + "BoB", layout="Left", w=cw_, h=SUI.BTN_SMALL_H)))
wboi = SUI.Appends()
wboi.append(("#" + W + "BoI", SUI.item_icon(W + "BoIc", J_("this.wBoIt", BOOSTERS[0]), size=40, anchor={"left": 4, "top": 4})))
wbob = SUI.Appends()
wbob.append(("#" + W + "BoB", SUI.button(W + "Boost", "Add booster", "secondary", "small", w=180)))
wbon = SUI.Appends()
wbon.text("#" + W + "BoB", W + "Bo2", J_("this.wBo[2]", "You have no Life, Water or Void Essence."), "default", size=13, h=SUI.BTN_SMALL_H, w=cw_,
          col=J_("this.wBoC[2]", BAD))
# ---- right: tier up
c_, cw_ = wcard("Tu", "ColC", WCC, 266, "Tier up")
wa.text(c_, W + "Tu0", J_("this.wTu[0]", "Totem Pole II -> Grand Pole III"), "bold", size=16, h=26, w=cw_, col=J_("this.wTuC[0]", TQC[2]))
wa.text(c_, W + "TuW", "A higher tier works faster and reaches further.", "caption", size=13, h=22, w=cw_)
for _j in range(1, 5):
    wa.text(c_, W + "Tu%d" % _j, J_("this.wTu[%d]" % _j, "2 Enchanted Wheat (you have 3)"), "default", size=14, h=22, w=cw_, col=J_("this.wTuC[%d]" % _j, GOOD))
wa.text(c_, W + "Tu5", J_("this.wTu[5]", "Your Totem Bench I stops at Totem Pole II - upgrade the bench first."), "default", size=13, h=36, w=cw_, wrap=True,
        col=J_("this.wTuC[5]", BAD))
wa.append((c_, SUI.group(W + "TuB", layout=None, w=cw_, h=SUI.BTN_H)))
wtub = SUI.Appends()
wtub.append(("#" + W + "TuB", SUI.button(W + "Up", "Tier up", "primary", w=220)))
# ---- right: the modifiers (2 slots, then all 6 with what they do, how many you have and the bench tier that crafts them)
c_, cw_ = wcard("Md", "ColC", WCC, 440, "Modifiers - 2 slots", "Craft them at the Totem Bench (Modifiers), then add them here.")
WMT = cw_ - 44 - 8 - 8 - 100
for _i in range(2):
    _r = W + "Ms%d" % _i
    wa.append((c_, SUI.group(_r, layout="Left", w=cw_, h=48, anchor={"bottom": 4})))
    wa.append(("#" + _r, SUI.group(_r + "I", layout=None, w=44, h=44, bg="slotBorder")))
    wa.append(("#" + _r, SUI.spacer(w=8)))
    wa.append(("#" + _r, SUI.group(_r + "T", layout="Top", w=WMT, h=48)))
    wa.text("#" + _r + "T", _r + "N", J_("this.wMNm[%d]" % _i, "Slot 1 - empty"), "default", size=14, bold=True, h=20, w=WMT, col=J_("this.wMNmC[%d]" % _i, TEXT))
    wa.text("#" + _r + "T", _r + "E", J_("this.wMEf[%d]" % _i, "Add one from the list below."), "caption", size=12, h=28, w=WMT, wrap=True, col=J_("this.wMEfC[%d]" % _i, TEXT))
    wa.append(("#" + _r, SUI.spacer(w=8)))
    wa.append(("#" + _r, SUI.group(_r + "B", layout=None, w=100, h=48)))
wa.text(c_, W + "MdL", "All modifiers", "section", size=13, h=24, w=cw_)
WML = cw_ - 90
for _i, _m in enumerate(MODS):
    _r = W + "Ml%d" % _i
    wa.append((c_, SUI.group(_r, layout="Left", w=cw_, h=34, anchor={"bottom": 2})))
    wa.append(("#" + _r, SUI.group(_r + "T", layout="Top", w=WML, h=34)))
    wa.text("#" + _r + "T", _r + "N", J_("this.wMl[%d]" % _i, _m[2] + " - you have 0 - Bench I"), "default", size=13, bold=True, h=18, w=WML, col=J_("this.wMlC[%d]" % _i, TEXT))
    wa.text("#" + _r + "T", _r + "E", _m[3], "caption", size=12, h=16, w=WML, col=GOOD)
    wa.append(("#" + _r, SUI.group(_r + "B", layout=None, w=90, h=34)))
wa.text(c_, W + "MdC", J_("this.wMdC", "You have none yet - craft them at the Totem Bench (Modifiers)."), "caption", size=13, h=22, w=cw_)
wms = []
for _i in range(2):
    _r = W + "Ms%d" % _i
    _ic, _rm = SUI.Appends(), SUI.Appends()
    _ic.append(("#" + _r + "I", SUI.item_icon(_r + "Ic", J_("this.wMIt[%d]" % _i, MOD_ITEM[0]), size=36, anchor={"left": 4, "top": 4})))
    _rm.append(("#" + _r + "B", SUI.button(_r + "Rm", "Remove", "secondary", "small", w=100, anchor={"top": 8})))
    wms.append((_ic, _rm))
wml = []
for _i in range(len(MODS)):
    _a = SUI.Appends()
    _a.append(("#" + W + "Ml%dB" % _i, SUI.button(W + "Ml%dAdd" % _i, "Add", "secondary", "small", w=84, anchor={"top": 1})))
    wml.append(_a)
for _col, _used in sorted(WUSED.items()):
    assert _used <= WCOLH, "0.4.13: the totem page column %s is %d px (room %d)" % (_col, _used, WCOLH)
wgone = SUI.Appends()
wgone.text(WB, W + "Gone", "This totem is gone - it was picked up or moved. Close this page.", "bold", size=16, h=40, w=WIW, align="Center")
wgone.append((WB, SUI.spacer(h=WCOLH - 40)))
wft = SUI.Appends()
wft.text(WB, W + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=WIW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
wft.append((WB, SUI.group(W + "Foot", layout="Left", w=WIW, h=SUI.BTN_H, anchor={"top": 6})))
wft.append(("#" + W + "Foot", SUI.spacer(w=WIW - 172)))
wft.append(("#" + W + "Foot", SUI.button(W + "Close", "Close", "secondary", w=172, sound="cancel")))
shw.fit([WCOLH + 6, 34, 6 + SUI.BTN_H], "the totem page")


def wvariant(owner, pic, aura, give, take, boost, tier, mods):
    """one coherent totem page variant (the window checks below + the harness walk the same choices)"""
    v = SUI.Appends(shw.appends)
    v.extend(wa)
    v.extend(wpic[pic]); v.extend(wrg[1 if aura else 0])
    if give:
        v.extend(wsdg)
    if take:
        v.extend(wsdt)
    if not give and not take:
        v.extend(wsdn)
    if boost == "on":
        v.extend(wboi)
    if boost == "can":
        v.extend(wbob)
    else:
        v.extend(wbon)
    if tier:
        v.extend(wtub)
    for _i in range(2):
        if mods[_i]:
            v.extend(wms[_i][0])
            if owner:
                v.extend(wms[_i][1])
    if owner and not all(mods):
        for _i in range(len(MODS)):
            v.extend(wml[_i])
    v.extend(wpk if owner else wvw)
    v.extend(wft)
    v.check(W)
    return v


for _wv in (wvariant(True, 3, True, True, True, "can", True, (False, False)), wvariant(True, len(RPATHS) - 1, False, False, False, "on", False, (True, True)),
            wvariant(False, 0, True, False, False, "no", False, (True, False))):
    VARIANTS.append(_wv)
_wv = SUI.Appends(shw.appends); _wv.extend(wgone); _wv.extend(wft); _wv.check(W); VARIANTS.append(_wv)
BUILD_TOTEM = "\n".join(
    [shw.java("b"), "  if (!this.dHas) {", wgone.java("b"), "  } else {", wa.java("b")]
    + ["    if (this.wPic == %d) {\n%s\n    }" % (_i, _a.java("b")) for _i, _a in enumerate(wpic)]
    + ["    if (this.wAura) {", wrg[1].java("b"), "    } else {", wrg[0].java("b"), "    }", binds([(W + "Rg", "trange")]),
       "    if (this.wSdGive) {", wsdg.java("b"), binds([(W + "SdG", "wseed")]), "    }",
       "    if (this.wSdTake) {", wsdt.java("b"), binds([(W + "SdT", "wseedb")]), "    }",
       "    if (!this.wSdGive && !this.wSdTake) {", wsdn.java("b"), "    }",
       "    if (this.wBoOn) {", wboi.java("b"), "    }",
       "    if (this.wBoCan) {", wbob.java("b"), binds([(W + "Boost", "tboost")]), "    } else {", wbon.java("b"), "    }",
       "    if (this.wTuCan) {", wtub.java("b"), tup_bind(W + "Up"), "    }"]
    + ["    if (this.wMHas[%d]) {\n%s\n    }\n    if (this.wMRem[%d]) {\n%s\n%s\n    }" % (_i, wms[_i][0].java("b"), _i, wms[_i][1].java("b"),
                                                                                    binds([(W + "Ms%dRm" % _i, "tmodrem%d" % (_i + 1))])) for _i in range(2)]
    + ["    if (this.wMAdd[%d]) {\n%s\n%s\n    }" % (_i, wml[_i].java("b"), binds([(W + "Ml%dAdd" % _i, "tmodadd%d" % _i)])) for _i in range(len(MODS))]
    + ["    if (this.mine) {", wpk.java("b"), binds([(W + "Pick", "tpick")]), "    } else {", wvw.java("b"), "    }",
       "  }", wft.java("b"), binds([(W + "Close", "close")])])

# --- 0.4.13 VIEW 4: THE TOTEM BENCH as a vanilla crafting bench (art/ui-totem-page/bench-mockup.html; Skyy: "make it visual, make it pretty,
# and make it easy to use" + "make it look more like a vanilla bench with the upgrade on the side and stuff."). The vanilla client pages it
# copies (Client/Data/Game/Interface/InGame/Pages/Inventory, read only): BasicCraftingPanel (the recipe ItemGrid of 72 px slots, the item
# name, the recipe's ingredient rows, the Craft buttons), BasicCraftingIngredient (a 72 px slot + the quantity in green #48d185 / red #D13B3B)
# and BenchInfoPanel (the bench tier + the tier upgrade requirements at the SIDE). Columns: categories | recipe grid | the selected recipe |
# the bench upgrade. Clicks: bcat<n> (a category), bg<n> (a slot), bkcraft, brup:..., bebench (the 0.4.12 actions, unchanged).
BP = "SkyyShB"
BPW, BPH = 1500, 900
shb = SUI.page_shell(BP, BPW, BPH, title=J_("this.title", "Farming Totem Bench"), kind="decorated")
BIW, BIH = shb.inner_w, shb.inner_h
BB = "#" + shb.body
assert (BIW, BIH) == (1466, 828), (BIW, BIH)
BSEG = {}


def bseg(name):
    a = SUI.Appends()
    BSEG[name] = a
    return a


def jb(name):
    return BSEG[name].java("b")


BSTRIP = 76
bs = bseg("shell")
bs.append((BB, SUI.panel(BP + "Strip", "simple", w=BIW, h=BSTRIP, layout="Left", pad=12)))
bs.append(("#" + BP + "Strip", SUI.item_icon(BP + "Icon", J_("this.bIcon", BENCH_BLOCKS[FARM_K]), size=52)))
bs.append(("#" + BP + "Strip", SUI.spacer(w=12)))
bs.append(("#" + BP + "Strip", SUI.group(BP + "Sum", layout="Top", w=520, h=52)))
bs.text("#" + BP + "Sum", BP + "Sum1", J_("this.bTitle", "Totem Bench I of IV"), "bold", size=16, h=28, w=520)
bs.text("#" + BP + "Sum", BP + "Sum2", J_("this.bSub", "Next: Bench II - see the upgrade on the right"), "caption", size=13, h=24, w=520, col=J_("this.bSubC", GOOD))
bs.append(("#" + BP + "Strip", SUI.spacer(w=12)))
HOWW = BIW - 24 - 52 - 12 - 520 - 12
bs.append(("#" + BP + "Strip", SUI.group(BP + "How", layout="Top", w=HOWW, h=52)))
bs.text("#" + BP + "How", BP + "How1", "How totems work", "section", size=13, h=20, w=HOWW, col=GOLD)
bs.text("#" + BP + "How", BP + "How2", "Craft one here, place it on a pad in your shard (shard menu - Totems tab), it works its range - then tier it up and add "
        "modifiers on its own page.", "caption", size=13, h=32, w=HOWW, wrap=True)
BROWH = BIH - BSTRIP - 10 - 34 - 6 - SUI.BTN_H - 10
BCW, BGW, BSW, BUW = 190, 520, 420, 300
assert BCW + BGW + BSW + BUW + 3 * 12 == BIW and BROWH >= 640, BROWH
bs.append((BB, SUI.group(BP + "Row", layout="Left", w=BIW, h=BROWH, anchor={"top": 10, "bottom": 10})))
bs.append(("#" + BP + "Row", SUI.group(BP + "Cat", layout="Top", w=BCW, h=BROWH)))
for _cid, _cw in (("Gp", BGW), ("Sp", BSW), ("Up", BUW)):
    bs.append(("#" + BP + "Row", SUI.spacer(w=12)))
    bs.append(("#" + BP + "Row", SUI.panel(BP + _cid, "simple", w=_cw, h=BROWH, layout="Top", pad=12)))
# the category strip (the active one in the selected look)
for _i, _c in enumerate(BCATS):
    bseg("cat%d" % _i).append(("#" + BP + "Cat", SUI.button(BP + "Cat%d" % _i, _c, "tertiary", w=BCW, anchor={"bottom": 8})))
    bseg("cats%d" % _i).append(("#" + BP + "Cat", SUI.button(BP + "Cat%d" % _i, _c, "tertiary", w=BCW, selected=True, anchor={"bottom": 8})))
bs.append(("#" + BP + "Cat", SUI.spacer(h=8)))
# the recipe grid (vanilla 72 px recipe slots -> 80 px cells, 5 a row, on the list well; a short category leaves empty well)
GCS, GIC, GC = 80, 60, 5
GN = max(KROWS, RROWS)
GROWS = (GN + GC - 1) // GC
GP = "#" + BP + "Gp"
bs.text(GP, BP + "GH", J_("this.gTitle", "Workers"), "section", size=14, h=26, w=BGW - 24, col=GOLD)
bs.text(GP, BP + "GLg", "Green dot - you can craft it. Gold - items or coins missing. Red - a rule blocks it. Dimmed - needs a better bench.", "caption",
        size=13, h=36, w=BGW - 24, wrap=True)
GLH = BROWH - 24 - 26 - 36 - 4
bs.append((GP, SUI.scroll_list(BP + "GL", h=GLH, w=BGW - 24, well=True, anchor={"top": 4})))
assert GC * (GCS + 8) <= BGW - 24 - 2 * SUI.WELL_LIST_PAD - 18, "0.4.13: the grid row fits next to the scrollbar"
for _r in range(GROWS):
    bseg("gr%d" % _r).append(("#" + BP + "GL", SUI.group(BP + "Gr%d" % _r, layout="Left", w=GC * (GCS + 8), h=GCS, anchor={"bottom": 8})))
for _i in range(GN):
    _id = BP + "G%d" % _i
    _row = "#" + BP + "Gr%d" % (_i // GC)
    for _st, _nm in (("normal", "gn"), ("selected", "gs"), ("disabled", "gd")):
        bseg("%s%d" % (_nm, _i)).append((_row, SUI.icon_cell(_id, item=J_("this.gIt[%d]" % _i, TOTEM_ITEM[0]), size=GCS, state=_st, icon=GIC, anchor={"right": 8})))
    bseg("ge%d" % _i).append(("#" + _id, SUI.group(_id + "E", layout=None, w=GCS - 12, h=4, anchor={"left": 6, "top": GCS - 8}, bg=J_("this.gEd[%d]" % _i, TQC[0]))))
    bseg("gdt%d" % _i).append(("#" + _id, SUI.group(_id + "D", layout=None, w=10, h=10, anchor={"left": GCS - 16, "top": 6}, bg=J_("this.gDot[%d]" % _i, GOOD))))
    bseg("gl%d" % _i).text("#" + _id, _id + "L", J_("this.gLk[%d]" % _i, "Bench II"), "rowBadge", size=12, bold=True, h=18, w=GCS - 8, align="Center",
                           anchor={"left": 4, "top": GCS - 30})
bseg("gempty").text("#" + BP + "GL", BP + "GE", J_("this.gEmpty", "Nothing in this group at this bench."), "caption", size=13, h=60, w=BGW - 60, wrap=True)
# the selected recipe (big icon, name in its rarity colour, what it does + how to use it, the ingredient slots, coins, ONE Craft button)
SP = "#" + BP + "Sp"
SW_ = BSW - 24
bs.append((SP, SUI.group(BP + "SbR", layout="Left", w=SW_, h=104, anchor={"bottom": 6})))
bs.append(("#" + BP + "SbR", SUI.spacer(w=(SW_ - 104) // 2)))
bs.append(("#" + BP + "SbR", SUI.group(BP + "Sb", layout=None, w=104, h=104, bg=J_("this.qRar", TQC[0]))))
bs.append(("#" + BP + "Sb", SUI.group(BP + "SbIn", layout=None, w=100, h=100, anchor={"left": 2, "top": 2}, bg="slotBorder")))
bs.text(SP, BP + "SNm", J_("this.qNm", "Harvest Spirit Totem Pole I"), "bold", size=17, h=28, w=SW_, align="Center", col=J_("this.qRar", TQC[0]))
bs.text(SP, BP + "STg", J_("this.qTag", "T1 Totem - Uncommon - Bench I"), "default", size=13, h=22, w=SW_, align="Center", col=GOLD)
bs.text(SP, BP + "SDs", J_("this.qDs", "A worker: gathers the crops in its range and stores them on its island. Place it on a pad in the shard, then give it seeds."),
        "default", size=13, h=72, w=SW_, wrap=True)
bs.text(SP, BP + "SNd", "Needs", "section", size=13, h=24, w=SW_, col=GOLD)
bs.append((SP, SUI.group(BP + "SIn", layout="Left", w=SW_, h=92)))
bs.text(SP, BP + "SCo", J_("this.qCo", "500 coins (you have 12,000)"), "default", size=14, h=24, w=SW_, col=J_("this.qCoC", GOOD))
bs.text(SP, BP + "SBg", J_("this.qBag", "Counts your inventory and your Pocket Dimension."), "caption", size=13, h=22, w=SW_)
bs.text(SP, BP + "SWh", J_("this.qWhy", "Missing: 128 more Wheat."), "default", size=13, h=40, w=SW_, wrap=True, col=J_("this.qWhyC", BAD))
bs.append((SP, SUI.group(BP + "SBt", layout=None, w=SW_, h=SUI.BTN_H)))
bseg("sic").append(("#" + BP + "SbIn", SUI.item_icon(BP + "SbIc", J_("this.qIt", TOTEM_ITEM[0]), size=88, anchor={"left": 6, "top": 6})))
for _i in range(4):
    _a = bseg("sin%d" % _i)
    _a.append(("#" + BP + "SIn", SUI.group(BP + "SI%d" % _i, layout="Top", w=92, h=92, anchor={"right": 9})))
    _a.append(("#" + BP + "SI%d" % _i, SUI.icon_cell(BP + "SI%dC" % _i, item=J_("this.qInIt[%d]" % _i, "Plant_Crop_Wheat_Item"), size=64, state="static", icon=52,
                                                     anchor={"left": 14})))
    _a.text("#" + BP + "SI%d" % _i, BP + "SI%dT" % _i, J_("this.qInTx[%d]" % _i, "40 / 128"), "default", size=13, bold=True, h=24, w=92, align="Center",
            col=J_("this.qInC[%d]" % _i, BAD))
bseg("scr").append(("#" + BP + "SBt", SUI.button(BP + "Craft", "Craft", "primary", w=SW_)))
bseg("scrd").append(("#" + BP + "SBt", SUI.button(BP + "Craft", "Craft", "primary", w=SW_, disabled=True)))
bseg("smp").append(("#" + BP + "SBt", SUI.button(BP + "MkP", "Make pole", "primary", w=SW_)))
bseg("smpd").append(("#" + BP + "SBt", SUI.button(BP + "MkP", "Make pole", "primary", w=SW_, disabled=True)))
# the bench upgrade at the side (BenchInfoPanel: the tier, what the next one needs; ours: pips I-IV, what it unlocks, its cost slots)
UP = "#" + BP + "Up"
UW_ = BUW - 24
bs.text(UP, BP + "UH", "Bench upgrade", "section", size=14, h=26, w=UW_, col=GOLD)
bs.append((UP, SUI.group(BP + "Pp", layout="Left", w=UW_, h=30, anchor={"bottom": 6})))
_pw = (UW_ - 3 * 6) // 4
for _i in range(4):
    bs.append(("#" + BP + "Pp", SUI.group(BP + "Pp%d" % _i, layout="Left", w=_pw, h=28, anchor={"right": 6} if _i < 3 else None, bg=J_("this.vPip[%d]" % _i, SUI.COLOR["row"]))))
    bs.append(("#" + BP + "Pp%d" % _i, SUI.label(BP + "Pp%dL" % _i, ROMAN[_i], "bold", size=14, w=_pw, h=28, align="Center")))
bs.text(UP, BP + "U0", J_("this.vTx[0]", "Bench I -> II unlocks:"), "default", size=14, bold=True, h=24, w=UW_, col=J_("this.vTxC[0]", SUI.COLOR["rowName"]))
bs.append((UP, SUI.group(BP + "UuR", layout="Left", w=UW_, h=52, anchor={"bottom": 4})))
bs.text(UP, BP + "U1", J_("this.vTx[1]", "Fertilizer, Blessing of the Sun - totems up to Grand Pole III."), "caption", size=13, h=52, w=UW_, wrap=True)
bs.text(UP, BP + "UC", "Cost", "section", size=13, h=24, w=UW_, col=GOLD)
bs.append((UP, SUI.group(BP + "UcR", layout="Left", w=UW_, h=92)))
for _j in range(2, 5):
    bs.text(UP, BP + "U%d" % _j, J_("this.vTx[%d]" % _j, "25,000 coins (you have 12,000)"), "default", size=13, h=22, w=UW_, col=J_("this.vTxC[%d]" % _j, GOOD))
bs.text(UP, BP + "U5", J_("this.vTx[5]", "Missing: 6 more Enchanted Wheat."), "default", size=13, h=40, w=UW_, wrap=True, col=J_("this.vTxC[5]", BAD))
bs.append((UP, SUI.group(BP + "UBt", layout=None, w=UW_, h=SUI.BTN_H)))
for _i in range(5):
    _a = bseg("vu%d" % _i)
    _a.append(("#" + BP + "UuR", SUI.icon_cell(BP + "Uu%d" % _i, item=J_("this.vIt[%d]" % _i, TOTEM_ITEM[2]), size=48, state="static", icon=40, anchor={"right": 6})))
    _a.append(("#" + BP + "Uu%d" % _i, SUI.group(BP + "Uu%dE" % _i, layout=None, w=40, h=3, anchor={"left": 4, "top": 44}, bg=J_("this.vEd[%d]" % _i, TQC[1]))))
for _i in range(3):
    _a = bseg("vc%d" % _i)
    _a.append(("#" + BP + "UcR", SUI.group(BP + "Uc%d" % _i, layout="Top", w=84, h=92, anchor={"right": 8} if _i < 2 else None)))
    _a.append(("#" + BP + "Uc%d" % _i, SUI.icon_cell(BP + "Uc%dC" % _i, item=J_("this.vCIt[%d]" % _i, "Skyy_Ench_Wheat"), size=64, state="static", icon=52, anchor={"left": 10})))
    _a.text("#" + BP + "Uc%d" % _i, BP + "Uc%dT" % _i, J_("this.vCTx[%d]" % _i, "2 / 8"), "default", size=13, bold=True, h=24, w=84, align="Center",
            col=J_("this.vCC[%d]" % _i, BAD))
bseg("vb").append(("#" + BP + "UBt", SUI.button(BP + "EUp", "Upgrade bench", "secondary", w=UW_)))
bseg("vbd").append(("#" + BP + "UBt", SUI.button(BP + "EUp", "Upgrade bench", "secondary", w=UW_, disabled=True)))
bft = bseg("foot")
bft.text(BB, BP + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=BIW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
bft.append((BB, SUI.group(BP + "Foot", layout="Left", w=BIW, h=SUI.BTN_H, anchor={"top": 6})))
bft.append(("#" + BP + "Foot", SUI.spacer(w=BIW - 172)))
bft.append(("#" + BP + "Foot", SUI.button(BP + "Close", "Close", "secondary", w=172, sound="cancel")))
shb.fit([BSTRIP, 10 + BROWH + 10, 34, 6 + SUI.BTN_H], "the Totem Bench")


def bvariant(cat, n, sel, locked, dots, ins, pole, can, vn, vc, vcan):
    """one coherent bench variant (the window checks + the harness walk the same choices)"""
    v = SUI.Appends(shb.appends)
    v.extend(BSEG["shell"])
    for _i in range(len(BCATS)):
        v.extend(BSEG[("cats%d" if _i == cat else "cat%d") % _i])
    for _r in range(GROWS):
        if n > _r * GC:
            v.extend(BSEG["gr%d" % _r])
            for _i in range(_r * GC, min(n, (_r + 1) * GC)):
                v.extend(BSEG[("gs%d" if _i == sel else ("gd%d" if _i in locked else "gn%d")) % _i])
                v.extend(BSEG["ge%d" % _i])
                if _i in dots:
                    v.extend(BSEG["gdt%d" % _i])
                if _i in locked:
                    v.extend(BSEG["gl%d" % _i])
    if n == 0:
        v.extend(BSEG["gempty"])
    if sel >= 0:
        v.extend(BSEG["sic"])
    for _i in range(ins):
        v.extend(BSEG["sin%d" % _i])
    if sel >= 0:
        v.extend(BSEG[("smp" if can else "smpd") if pole else ("scr" if can else "scrd")])
    for _i in range(vn):
        v.extend(BSEG["vu%d" % _i])
    for _i in range(vc):
        v.extend(BSEG["vc%d" % _i])
    if vcan is not None:
        v.extend(BSEG["vb" if vcan else "vbd"])
    v.extend(BSEG["foot"])
    v.check(BP)
    return v


for _bv in (bvariant(0, GN, 1, (3, 4), (0, 1, 2), 4, False, True, 5, 3, True), bvariant(3, 7, -1, (), (), 0, False, False, 0, 0, None),
            bvariant(4, 0, -1, (), (), 0, True, False, 2, 1, False), bvariant(4, 3, 0, (), (0, 1, 2), 3, True, False, 0, 0, None),
            bvariant(1, 4, 2, (2,), (0, 1), 2, False, False, 1, 2, False)):
    VARIANTS.append(_bv)
_cell = []
for _i in range(GN):
    _cell.append("\n".join([
        "    if (this.gN > %d) {" % _i,
        "      if (this.gSel == %d) {\n%s\n      } else if (this.gLk[%d].length() > 0) {\n%s\n      } else {\n%s\n      }" % (_i, jb("gs%d" % _i), _i, jb("gd%d" % _i), jb("gn%d" % _i)),
        jb("ge%d" % _i),
        "      if (this.gDot[%d].length() > 0) {\n%s\n      }" % (_i, jb("gdt%d" % _i)),
        "      if (this.gLk[%d].length() > 0) {\n%s\n      }" % (_i, jb("gl%d" % _i)),
        binds([(BP + "G%d" % _i, "bg%d" % _i)]),
        "    }"]))
BUILD_BENCH = "\n".join(
    [shb.java("b"), jb("shell")]
    + ["  if (this.bCat == %d) {\n%s\n  } else {\n%s\n  }\n%s" % (_i, jb("cats%d" % _i), jb("cat%d" % _i), binds([(BP + "Cat%d" % _i, "bcat%d" % _i)])) for _i in range(len(BCATS))]
    + ["  if (this.gN > %d) {\n%s\n%s\n  }" % (_r * GC, jb("gr%d" % _r), "\n".join(_cell[_r * GC:(_r + 1) * GC])) for _r in range(GROWS)]
    + ["  if (this.gN == 0) {", jb("gempty"), "  }",
       "  if (this.qHas) {", jb("sic"), "  }"]
    + ["  if (this.qIn > %d) {\n%s\n  }" % (_i, jb("sin%d" % _i)) for _i in range(4)]
    + ["  if (this.bCat == 4) {",
       "    if (this.qCan && this.rN > 0) {", jb("smp"),
       # the click carries what the page showed (slot, tier, uid): a second click from the old page can never tier up twice (0.4.7)
       '  ev.addEventBinding(@BT@.Activating, "#%sMkP", @EVD@.of("a", "brup:" + this.rCi[this.rSel] + ":" + this.rSi[this.rSel] + ":" + this.rTier[this.rSel] + ":" + this.rUid[this.rSel]));' % BP,
       "    } else if (this.qHas) {", jb("smpd"), "    }",
       "  } else {",
       "    if (this.qCan) {", jb("scr"), binds([(BP + "Craft", "bkcraft")]), "    } else if (this.qHas) {", jb("scrd"), "    }",
       "  }"]
    + ["  if (this.vN > %d) {\n%s\n  }" % (_i, jb("vu%d" % _i)) for _i in range(5)]
    + ["  if (this.vCn > %d) {\n%s\n  }" % (_i, jb("vc%d" % _i)) for _i in range(3)]
    + ["  if (this.vCan) {", jb("vb"), binds([(BP + "EUp", "bebench")]), "  } else if (this.vShow) {", jb("vbd"), "  }",
       jb("foot"), binds([(BP + "Close", "close")])])

# --- 0.4.13 the BUSY page: the shard data lock was taken (another thread holds it - see the ShLock WARN); a world thread never waits on it,
# the player gets this small page instead (one packet) and tries again
ZP = "SkyyShZ"
shz = SUI.page_shell(ZP, 640, 260, title="Shard", kind="decorated")
ZB = "#" + shz.body
za = SUI.Appends()
za.text(ZB, ZP + "T", "The shard is busy right now - try again in a moment.", "bold", size=15, h=40, w=shz.inner_w, align="Center")
za.text(ZB, ZP + "C", "Nothing was changed.", "caption", size=13, h=26, w=shz.inner_w, align="Center")
za.append((ZB, SUI.group(ZP + "Foot", layout="Left", w=shz.inner_w, h=SUI.BTN_H, anchor={"top": 12})))
za.append(("#" + ZP + "Foot", SUI.spacer(w=shz.inner_w - 172)))
za.append(("#" + ZP + "Foot", SUI.button(ZP + "Close", "Close", "secondary", w=172, sound="cancel")))
shz.fit([40, 26, 12 + SUI.BTN_H], "the busy page")
_zv = SUI.Appends(shz.appends); _zv.extend(za); _zv.check(ZP); VARIANTS.append(_zv)
BUILD_BUSY = "\n".join([shz.java("b"), za.java("b"), binds([(ZP + "Close", "close")])])
'''
FILLS = r'''# 0.4.13 THE TOTEM PAGE FILL (after fill(): the selected totem tIsl / tpad, the bags loaded once): the w* texts, colours and which buttons are
# drawn. Never writes (the aura refresh is memory only). A count of a cost = inventory + Pocket Dimension (hav); the seed counts = what
# seedsGive takes (the inventory). Short numbers for big Pocket Dimension counts in the slots (shortN).
M(page, r"""
public static String shortN(long v) {
  if (v < 0L) return "?";
  if (v >= 1000000L) return @PKG@.ShCfg.dec(Math.floor((double) v / 100000.0) / 10.0) + "M";
  if (v >= 100000L) return (v / 1000L) + "K";
  return @PKG@.ShCfg.num(v);
}""")
M(page, r"""
public void fillTotemPage(String k, @IC@[] cs) {
  this.wItem = "@TI0@"; this.wRar = TQC[0]; this.wName = this.dTitle == null ? "" : this.dTitle; this.wTag = ""; this.wRole = "";
  this.wRgTx = ""; this.wRgCap = ""; this.wPic = 0; this.wAura = @PKG@.ShCore.auraOn(this.me);
  this.wOutW = ""; this.wOut = ""; this.wOutC = "@GOOD@"; this.wOutU = ""; this.wOut2 = ""; this.wBarF = 0; this.wOut3 = ""; this.wOut3C = "@CAP@";
  this.wSd = new String[4]; this.wSdC = new String[4]; this.wBo = new String[3]; this.wBoC = new String[3]; this.wTu = new String[6]; this.wTuC = new String[6];
  for (int i = 0; i < 4; i++) { this.wSd[i] = ""; this.wSdC[i] = "@TEXT@"; }
  for (int i = 0; i < 3; i++) { this.wBo[i] = ""; this.wBoC[i] = "@TEXT@"; }
  for (int i = 0; i < 6; i++) { this.wTu[i] = ""; this.wTuC[i] = "@TEXT@"; }
  this.wMIt = new String[2]; this.wMNm = new String[2]; this.wMNmC = new String[2]; this.wMEf = new String[2]; this.wMEfC = new String[2];
  this.wMHas = new boolean[2]; this.wMRem = new boolean[2];
  for (int i = 0; i < 2; i++) { this.wMIt[i] = "@MI0@"; this.wMNm[i] = "Slot " + (i + 1) + " - empty"; this.wMNmC[i] = "@ROW@"; this.wMEf[i] = "Add one from the list below."; this.wMEfC[i] = "@CAP@"; }
  int nm = @PKG@.ShTotem.MOD_ITEMS.length;
  this.wMl = new String[nm]; this.wMlC = new String[nm]; this.wMAdd = new boolean[nm];
  for (int i = 0; i < nm; i++) { this.wMl[i] = @PKG@.ShTotem.MOD_NAMES[i]; this.wMlC[i] = "@CAP@"; }
  this.wMdC = "";
  this.wSdGive = false; this.wSdTake = false; this.wBoCan = false; this.wBoOn = false; this.wTuCan = false; this.wBoIt = "@B0@";
  if (!this.dHas || k == null) return;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) { this.dHas = false; return; }
  int kd = this.kind;
  int s = this.tIsl;
  long now = @PKG@.ShCore.now();
  String[] f = null;
  int sz = 1; int ty = 0; long seeds = 0L; int et = 0; int fn = 0; int bt = 1; boolean au = false; double ench = 0.0; String cost = "";
  @PKG@.ShStore.LOCK.lock(); try {
    String[] e = @PKG@.ShTotem.entries(kd, p, s);
    if (this.tpad >= 0 && this.tpad < e.length) {
      f = @PKG@.ShTotem.onPad(e[this.tpad]);
      sz = @PKG@.ShMath.size(kd, p, s);
      ty = @PKG@.ShIsl.ty(kd, p, s);
      seeds = @PKG@.ShIsl.seeds(kd, p, s);
      et = @PKG@.ShIsl.eternal(kd, p, s);
      fn = @PKG@.ShIsl.farmN(sz, @PKG@.ShIsl.sub(p, kd, s, 0));
      bt = @PKG@.ShCore.benchTier(kd, p, now);
      au = @PKG@.ShIsl.auto(kd, p);
      ench = @PKG@.ShTotem.enchChance(kd, p, s);
      int ti0 = @PKG@.ShTotem.idx(f[0]);
      if (ti0 >= 0 && @PKG@.ShTotem.tierOf(f[1]) < 5) cost = @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[ti0], @PKG@.ShTotem.doc(f, now).toJson());
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (f == null) { this.dHas = false; return; }
  int ti = @PKG@.ShTotem.idx(f[0]);
  int t = @PKG@.ShTotem.tierOf(f[1]);
  boolean wk = ti >= 0 && @PKG@.ShTotem.WORKER[ti];
  int ef = ti >= 0 ? @PKG@.ShTotem.EFFECT[ti] : 1;
  boolean here = ti >= 0 && @PKG@.ShTotem.accepts(ti, kd);
  int r = @PKG@.ShTotem.range(f, now);
  String what = @PKG@.ShKind.WHAT[kd];
  int[] fp = @PKG@.ShTotem.posOf(f);   // 0.4.13: placed by hand = its range around where it stands
  // the totem + its range
  if (ti >= 0) this.wItem = @PKG@.ShTotem.ITEMS[ti];
  this.wRar = TQC[t - 1];
  this.wName = @PKG@.ShTotem.name(f);
  this.wTag = "T" + t + " Totem - " + (fp != null ? "placed by hand" : "pad " + (this.tpad + 1)) + " - " + @PKG@.ShIsl.tname(ty) + " " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small"));
  this.wRole = wk ? "Worker - gathers the " + what + " in its range" : (ef == 5 ? "Rare finds for its island" : (ef == 6 ? "Auto-Smelt for its island" : (ef == 4 ? "Harvest Moon - more at night" : "Support - more items for its island")));
  int c0 = @PKG@.ShTotem.covOf(sz, f, r);
  int c9 = @PKG@.ShTotem.cov(sz, 99);
  this.wRgTx = "Range " + r + " blocks - " + c0 + " of " + c9 + " " + what;
  int sp = sz < 1 ? 1 : (sz > 3 ? 3 : sz);
  this.wPic = fp != null ? -1 : RPB[sp - 1] + (r < 0 ? 0 : (r > RPM[sp - 1] ? RPM[sp - 1] : r));
  int as = @PKG@.ShCfg.AURA_SEC;
  this.wRgCap = this.wAura ? "Shown now: a ring on the edge, puffs on the cells it works. Only you see it" + (as > 0 ? " - " + as + " s more after you close this page." : ".")
      : "Show range marks it in the world, only for you" + (as > 0 ? " - while this page is open and " + as + " s after." : ".");
  if (fp != null) this.wRgCap = "Placed by hand at " + fp[0] + ", " + fp[1] + " from the centre. " + (this.wAura ? "Shown in the world now - only you see it." : "Show range draws it in the world, only for you.");
  if (this.wAura) @PKG@.ShCore.auraKeep(this.me, k, kd, s, this.tpad);
  // output
  boolean bo = @PKG@.ShTotem.boosted(f, now);
  int bar = c9 > 0 ? (int) ((long) BARW * (long) c0 / (long) c9) : 0;
  if (!here) {
    this.wOutW = "What this totem does here."; this.wOut = "0"; this.wOutC = "@BAD@"; this.wOutU = "items / min";
    this.wOut2 = ti >= 0 ? "It works in the " + @PKG@.ShTotem.kindsOf(ti) + " Shard." : "An unknown totem.";
    this.wOut3 = "Pick it up and place it in that shard."; this.wOut3C = "@BAD@";
  } else if (wk) {
    this.wOutW = "What this totem makes while it is placed.";
    this.wOut = @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(kd, f, sz, now)); this.wOutU = "items / min" + (bo ? " (boosted)" : "");
    this.wOut2 = "In range: " + c0 + " of " + c9 + " " + what; this.wBarF = bar;
    this.wOut3 = "Goes to the island's storage - collect it on the Collect tab of the shard menu.";
  } else if (ef == 5) {
    this.wOutW = "What this totem adds to its island.";
    this.wOut = @PKG@.ShCfg.dec(ench * 100.0) + " %"; this.wOutU = "chance per item";
    this.wOut2 = "Rare find: " + @PKG@.ShTotem.pretty(@PKG@.ShKind.BONUS[kd]); this.wBarF = BARW;
    this.wOut3 = "Rare finds go to the island's storage with the rest.";
  } else if (ef == 6) {
    this.wOutW = "What this totem adds to its island.";
    this.wOut = "Ingots"; this.wOutU = "instead of ore"; this.wOut2 = "Every ore of this island comes out smelted."; this.wBarF = BARW;
    this.wOut3 = "Collect gives ingots instead of ore.";
  } else {
    this.wOutW = "What this totem adds to its island.";
    this.wOut = "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(kd, f, now)) + " %"; this.wOutU = "for this island" + (bo ? " (boosted)" : "");
    this.wOut2 = "In range: " + c0 + " of " + c9 + " " + what; this.wBarF = bar;
    this.wOut3 = ef == 4 ? "Harvest Moon: more crops at night + rare Enchanted crops." : "Every worker on the island makes more.";
  }
  // seeds + replanting (the island's seed store: Give / Take seeds = seedsGive / seedsTake, the inventory)
  String st = @PKG@.ShIsl.STYLE[kd];
  boolean farm = "farm".equals(st);
  String sd = @PKG@.ShIsl.SEED[ty];
  String es = @PKG@.ShIsl.ESEED[ty];
  boolean seedy = !au && (farm || @PKG@.ShIsl.trees(kd)) && sd.length() > 0;
  if (seedy) {
    this.wSd[0] = "Seed store: " + @PKG@.ShCfg.num(seeds) + " " + @PKG@.ShTotem.pretty(sd) + (farm ? " - " + et + " of " + fn + " cells Eternal" : "");
    this.wSdC[0] = seeds > 0L ? "@GOOD@" : "@BAD@";
    boolean twoE = farm && es.length() > 0 && !es.equals(sd);
    long hs = cs == null ? 0L : @PKG@.ShInv.count(cs, sd);
    long he = (cs == null || !twoE) ? 0L : @PKG@.ShInv.count(cs, es);
    this.wSd[1] = "You carry " + @PKG@.ShCfg.num(hs) + " " + @PKG@.ShTotem.pretty(sd) + (twoE ? " + " + @PKG@.ShCfg.num(he) + " " + @PKG@.ShTotem.pretty(es) : "");
    this.wSdGive = this.mine && ((hs > 0L && seeds < (long) @PKG@.ShCfg.SEED_MAX) || (he > 0L && et < fn));
    this.wSdTake = this.mine && seeds > 0L;
    if (!this.mine) this.wSd[2] = "Only the island owner gives this totem seeds.";
    else if (!this.wSdGive && !this.wSdTake) this.wSd[2] = (hs <= 0L && he <= 0L) ? "You carry no " + @PKG@.ShTotem.pretty(sd) + " - get some, then come back." : "The seed store is full.";
    this.wSdC[2] = "@BAD@";
    this.wSd[3] = farm ? "Give seeds takes the ones you carry; each Eternal seed makes one more cell Eternal for good." : "Give seeds takes the saplings you carry.";
  } else {
    this.wSd[0] = au ? "Automated - every cell is Eternal, no seeds needed." : ("mine".equals(st) ? "Ore regrows by itself - nothing to replant." : "Nothing to replant on this island.");
    this.wSdC[0] = "@GOOD@";
    this.wSd[2] = au ? "Nothing to give." : "This island needs no seeds.";
    this.wSdC[2] = "@CAP@";
    this.wSd[3] = au ? "Automation is a shard upgrade on the Map tab." : "";
  }
  // the booster
  long bu = 0L;
  try { bu = Long.parseLong(f[4]); } catch (Throwable x) { bu = 0L; }
  boolean burn = bu > now;
  String bid = null;
  for (int i = 0; i < @PKG@.ShTotem.BOOSTERS.length && bid == null; i++) if (hav(cs, @PKG@.ShTotem.BOOSTERS[i]) > 0L) bid = @PKG@.ShTotem.BOOSTERS[i];
  this.wBoOn = burn;
  this.wBo[0] = burn ? "Burning - " + ((bu - now + 59999L) / 60000L) + " min left" : "Empty";
  this.wBoC[0] = burn ? "@GOOD@" : "@ROW@";
  this.wBo[1] = "1 Life, Water or Void Essence = +2 range and +" + @PKG@.ShCfg.BOOST_PCT + " % for " + (@PKG@.ShCfg.BOOST_SEC / 60) + " min";
  this.wBoCan = this.mine && !burn && bid != null;
  if (!this.mine) this.wBo[2] = "Only the island owner adds boosters.";
  else if (burn) this.wBo[2] = "One booster at a time - this one is still burning.";
  else if (bid == null) this.wBo[2] = "You have no Life, Water or Void Essence" + (this.bagSt < 0 ? " in your inventory (Pocket Dimension paused)." : ".");
  this.wBoC[2] = burn ? "@CAP@" : "@BAD@";
  // tier up (the cost = inventory + Pocket Dimension, the bench cap)
  if (t >= 5) {
    this.wTu[0] = "Highest tier - " + @PKG@.ShTotem.LADDER[4]; this.wTuC[0] = "@GOLD@";
    this.wTu[1] = "Nothing left to tier up."; this.wTuC[1] = "@CAP@";
  } else {
    this.wTu[0] = @PKG@.ShTotem.form(f) + " -> " + @PKG@.ShTotem.LADDER[t];
    this.wTuC[0] = TQC[t];
    String[] g = new String[f.length];
    for (int i = 0; i < f.length; i++) g[i] = f[i];
    g[1] = String.valueOf(t + 1);
    int r2 = @PKG@.ShTotem.range(g, now);
    String gain = wk ? "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(kd, g, sz, now) - @PKG@.ShTotem.workerRate(kd, f, sz, now)) + " items / min"
        : (ef == 5 || ef == 6 ? "A stronger effect" : "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(kd, g, now) - @PKG@.ShTotem.supportPct(kd, f, now)) + " %");
    this.wTu[1] = gain + " - range " + r + " -> " + r2 + " blocks";
    this.wTuC[1] = "@GOOD@";
    int cap = @PKG@.ShCfg.benchCap(bt);
    Object[] rc = null;
    if (cost.length() > 0 && !cost.startsWith("err:")) rc = @PKG@.ShCore.recipe(cost);
    boolean all = rc != null;
    String miss = "";
    if (rc == null) { this.wTu[2] = "The tier-up cost setting is broken - ask an admin."; this.wTuC[2] = "@BAD@"; }
    else {
      String[] ids = (String[]) rc[0];
      long[] q = (long[]) rc[1];
      int j = 2;
      for (int i = 0; i < ids.length && j < 5; i++) {
        long h = hav(cs, ids[i]);
        boolean ok = cs != null && h >= q[i];
        this.wTu[j] = @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you have " + (cs == null ? "?" : @PKG@.ShCfg.num(h)) + ")";
        this.wTuC[j] = ok ? "@GOOD@" : "@BAD@";
        j++;
        if (!ok) { all = false; if (miss.length() == 0) miss = @PKG@.ShCfg.num(q[i] - (h < 0L ? 0L : h)) + " more " + @PKG@.ShTotem.pretty(ids[i]); }
      }
    }
    if (t + 1 > cap) { this.wTu[5] = "Your Totem Bench " + @PKG@.ShTotem.ROMAN[bt - 1] + " stops at " + @PKG@.ShTotem.LADDER[cap - 1] + " - upgrade the bench first."; this.wTuC[5] = "@BAD@"; }
    else if (!this.mine) { this.wTu[5] = "Only the island owner tiers totems up."; this.wTuC[5] = "@CAP@"; }
    else if (rc != null && !all) { this.wTu[5] = "Missing: " + miss + (this.bagSt < 0 ? " (your Pocket Dimension is paused - only your inventory counts)." : "."); this.wTuC[5] = "@BAD@"; }
    else if (rc != null) { this.wTu[5] = "Paid from your inventory first, then your Pocket Dimension."; this.wTuC[5] = "@CAP@"; }
    this.wTuCan = this.mine && all && t + 1 <= cap;
  }
  // the modifiers: the 2 slots, then every modifier with what it does, how many you have, the bench tier that crafts it
  int m1 = @PKG@.ShTotem.modIdx(f[2]);
  int m2 = @PKG@.ShTotem.modIdx(f[3]);
  int[] ms = new int[] { m1, m2 };
  for (int i = 0; i < 2; i++) {
    if (ms[i] < 0) continue;
    this.wMHas[i] = true; this.wMIt[i] = @PKG@.ShTotem.MOD_ITEMS[ms[i]];
    this.wMNm[i] = "Slot " + (i + 1) + " - " + @PKG@.ShTotem.MOD_NAMES[ms[i]]; this.wMNmC[i] = TQC[0];
    this.wMEf[i] = @PKG@.ShTotem.MOD_DESC[ms[i]]; this.wMEfC[i] = "@GOOD@";
    this.wMRem[i] = this.mine;
  }
  boolean free = m1 < 0 || m2 < 0;
  int any = 0;
  for (int i = 0; i < nm; i++) {
    long h = hav(cs, @PKG@.ShTotem.MOD_ITEMS[i]);
    if (h > 0L) any++;
    this.wMl[i] = @PKG@.ShTotem.MOD_NAMES[i] + " - you have " + (h < 0L ? "?" : @PKG@.ShCfg.num(h)) + " - Bench " + @PKG@.ShTotem.ROMAN[@PKG@.ShCfg.modUnlock(i) - 1];
    this.wMlC[i] = h > 0L ? TQC[0] : "@CAP@";
    this.wMAdd[i] = this.mine && free && h > 0L;
  }
  this.wMdC = !free ? "Both slots are full - remove one to swap it." : (any == 0 ? "You have none yet - craft them at the Totem Bench (Modifiers)." : (this.mine ? "Add puts it in the first empty slot; Remove gives it back." : "Only the island owner adds modifiers."));
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@CAP@", SUI.COLOR["caption"])
     .replace("@ROW@", SUI.COLOR["rowName"]).replace("@TI0@", TOTEM_ITEM[0]).replace("@MI0@", MOD_ITEM[0]).replace("@B0@", BOOSTERS[0]))
# 0.4.13 THE BENCH GRID: the category of a craft recipe (-1 = not on this bench), the bench tier that unlocks it, a category's recipes by
# bench tier then name (PROJECT-RULES 4: sort by tier everywhere)
M(page, "public static boolean weather(String key) { return WEATHER.indexOf(\",\" + key + \",\") >= 0; }")
M(page, r"""
public int catOf(int kd, int i) {
  if (i < 0 || i >= @PKG@.ShCfg.CRAFT_ID.length) return -1;
  String id = @PKG@.ShCfg.CRAFT_ID[i];
  int ti = @PKG@.ShTotem.itemIdx(id);
  if (ti >= 0) {
    if (!@PKG@.ShTotem.accepts(ti, kd)) return -1;
    if (@PKG@.ShTotem.WORKER[ti]) return 0;
    return weather(@PKG@.ShTotem.KEYS[ti]) ? 1 : 2;
  }
  if (@PKG@.ShTotem.modItemIdx(id) >= 0) return 3;
  if (@PKG@.ShKind.ofShard(id) >= 0 && @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]) != null) return 2;
  return -1;
}""")
M(page, r"""
public int needOf(int kd, int i) {
  String id = @PKG@.ShCfg.CRAFT_ID[i];
  int ti = @PKG@.ShTotem.itemIdx(id);
  int u = 4;
  if (ti >= 0) u = @PKG@.ShCfg.benchUnlock(kd, ti);
  else { int mi = @PKG@.ShTotem.modItemIdx(id); if (mi >= 0) u = @PKG@.ShCfg.modUnlock(mi); }
  return u < 1 ? 1 : (u > 4 ? 4 : u);
}""")
M(page, r"""
public boolean before(int kd, int x, int y) {
  int nx = needOf(kd, x);
  int ny = needOf(kd, y);
  if (nx != ny) return nx < ny;
  return @PKG@.ShTotem.pretty(@PKG@.ShCfg.CRAFT_ID[x]).compareTo(@PKG@.ShTotem.pretty(@PKG@.ShCfg.CRAFT_ID[y])) < 0;
}""")
M(page, r"""
public int[] catList(int kd, int cat) {
  int n = @PKG@.ShCfg.CRAFT_ID.length;
  int[] a = new int[n];
  int m = 0;
  for (int i = 0; i < n; i++) if (catOf(kd, i) == cat) { a[m] = i; m++; }
  for (int i = 1; i < m; i++) {
    int x = a[i];
    int j = i - 1;
    while (j >= 0 && before(kd, x, a[j])) { a[j + 1] = a[j]; j--; }
    a[j + 1] = x;
  }
  int[] out = new int[m];
  for (int i = 0; i < m; i++) out[i] = a[i];
  return out;
}""")
# the ingredient slots of the selected panel: a recipe's items (have / need, inventory + bags) and its coins; returns what is missing first
M(page, r"""
public String qSlots(Object[] rc, @IC@[] cs, long purse) {
  if (rc == null) return "";
  String miss = "";
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  for (int j = 0; j < ids.length; j++) {
    long h = hav(cs, ids[j]);
    boolean ok = cs != null && h >= q[j];
    if (this.qIn < 4) {
      this.qInIt[this.qIn] = ids[j];
      this.qInTx[this.qIn] = (cs == null ? "?" : shortN(h)) + " / " + shortN(q[j]);
      this.qInC[this.qIn] = ok ? "@GOOD@" : "@BAD@";
      this.qIn++;
    }
    if (!ok && miss.length() == 0) miss = @PKG@.ShCfg.num(q[j] - (h < 0L ? 0L : h)) + " more " + @PKG@.ShTotem.pretty(ids[j]);
  }
  long co = ((Long) rc[2]).longValue();
  if (co > 0L) {
    boolean ok = purse < 0L || purse >= co;
    this.qCo = @PKG@.ShCfg.num(co) + " coins (you have " + (purse < 0L ? "?" : @PKG@.ShCfg.num(purse)) + ")";
    this.qCoC = ok ? "@GOOD@" : "@BAD@";
    if (!ok && miss.length() == 0) miss = @PKG@.ShCfg.num(co - purse) + " more coins";
  }
  return miss;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD))
M(page, r"""
public void fillPickCraft(int kd, int tier, @IC@[] cs, long purse) {
  if (this.gSel < 0 || this.kSel < 0 || this.kSel >= @PKG@.ShCfg.CRAFT_ID.length) { this.qNm = "Pick a recipe"; this.qDs = "Click a slot to see what it does and what it needs."; return; }
  int i = this.kSel;
  String id = @PKG@.ShCfg.CRAFT_ID[i];
  int ti = @PKG@.ShTotem.itemIdx(id);
  int mi = @PKG@.ShTotem.modItemIdx(id);
  int sk = @PKG@.ShKind.ofShard(id);
  int need = needOf(kd, i);
  this.qHas = true; this.qIt = id; this.qRar = this.gEd[this.gSel];
  this.qNm = @PKG@.ShTotem.pretty(id);
  this.qTag = ti >= 0 ? "T1 Totem - " + TQN[need - 1] + " - Bench " + @PKG@.ShTotem.ROMAN[need - 1] : (mi >= 0 ? "Totem modifier - " + TQN[need - 1] + " - Bench " + @PKG@.ShTotem.ROMAN[need - 1] : "Shard - " + TQN[3]);
  if (ti >= 0) {
    boolean wk = @PKG@.ShTotem.WORKER[ti];
    int ef = @PKG@.ShTotem.EFFECT[ti];
    String w0 = wk ? "A worker: gathers the " + @PKG@.ShKind.WHAT[kd] + " in its range and stores them on its island." : (ef == 5 ? "Rare finds: a chance per item of a rare extra on its island." : (ef == 6 ? "Auto-Smelt: its island's ore comes out as ingots." : (ef == 4 ? "Harvest Moon: more crops at night + rare Enchanted crops." : (weather(@PKG@.ShTotem.KEYS[ti]) ? "Weather: more items for every worker on its island." : "A helper: more items for its whole island."))));
    String how = @PKG@.ShTotem.HAND[ti] ? " It starts hand-held (Totem I): right-click it anywhere, then make it a Totem Pole II here (Totem Pole)." : " Place it on a pad in the shard (shard menu - Totems tab)" + (wk ? ", then give it seeds on its page." : ".");
    this.qDs = w0 + how;
  } else if (mi >= 0) this.qDs = @PKG@.ShTotem.MOD_NAMES[mi] + ": " + @PKG@.ShTotem.MOD_DESC[mi] + ". Add it on a placed totem's own page - 2 slots a totem.";
  else this.qDs = "A " + (sk >= 0 ? @PKG@.ShKind.NAMES[sk] : "") + " Shard for a profile that never had one (rebirth 2; one per profile, ever).";
  Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]);
  String bg = @PKG@.ShCore.benchGate(kd, tier, i);
  String g = bg != null ? bg : @PKG@.ShCore.craftGate(this.me, i);
  String miss = qSlots(rc, cs, purse);
  if (rc == null) { this.qWhy = "This recipe is switched off (Server Setup -> Shards -> Crafting)."; this.qWhyC = "@BAD@"; }
  else if (g != null) { this.qWhy = g; this.qWhyC = "@BAD@"; }
  else if (!this.mine) { this.qWhy = "Only the island owner crafts here."; this.qWhyC = "@CAP@"; }
  else if (miss.length() > 0) { this.qWhy = "Missing: " + miss + "."; this.qWhyC = "@BAD@"; }
  else { this.qWhy = "Ready to craft - it goes into your inventory."; this.qWhyC = "@GOOD@"; }
  this.qCan = this.mine && rc != null && g == null && miss.length() == 0;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@CAP@", SUI.COLOR["caption"]))
M(page, r"""
public void fillPickPole(int kd, int tier, @IC@[] cs) {
  if (this.rN == 0 || this.rSel < 0 || this.rSel >= this.rN) {
    this.qNm = "No Totem I in your inventory";
    this.qDs = "A hand-held Totem I (Rain, Fertilizer, Blessing of the Sun) becomes a Totem Pole II here - a pole you place on a pad in the shard.";
    return;
  }
  int r = this.rSel;
  int ti = @PKG@.ShTotem.idx(this.rTy[r]);
  this.gSel = r;
  this.qHas = true; this.qIt = ti >= 0 ? @PKG@.ShTotem.ITEMS[ti] : "@TI0@"; this.qRar = TQC[0];
  this.qNm = this.rName[r];
  this.qTag = "T1 Totem - " + TQN[0] + " - becomes T2 " + @PKG@.ShTotem.LADDER[1];
  this.qDs = "Make it a " + @PKG@.ShTotem.LADDER[1] + ": a pole you place on a pad in the shard (shard menu - Totems tab). Range " + @PKG@.ShCfg.RANGES[0] + " -> " + @PKG@.ShCfg.RANGES[1] + " blocks.";
  int cap = @PKG@.ShCfg.benchCap(tier);
  String c = this.rCost[r];
  Object[] rc = null;
  if (c != null && c.length() > 0 && !c.startsWith("err:")) rc = @PKG@.ShCore.recipe(c);
  String miss = qSlots(rc, cs, -1L);
  boolean capOk = this.rTier[r] + 1 <= cap;
  if (!capOk) { this.qWhy = "Needs a higher bench: Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " stops at " + @PKG@.ShTotem.LADDER[cap - 1] + "."; this.qWhyC = "@BAD@"; }
  else if (rc == null) { this.qWhy = "The tier-up cost setting is broken - ask an admin."; this.qWhyC = "@BAD@"; }
  else if (!this.mine) { this.qWhy = "Only the island owner makes poles here."; this.qWhyC = "@CAP@"; }
  else if (miss.length() > 0) { this.qWhy = "Missing: " + miss + "."; this.qWhyC = "@BAD@"; }
  else { this.qWhy = "Ready - the pole goes back into your inventory."; this.qWhyC = "@GOOD@"; }
  this.qCan = this.mine && rc != null && capOk && miss.length() == 0;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@CAP@", SUI.COLOR["caption"]).replace("@TI0@", TOTEM_ITEM[0]))
# the bench upgrade side panel (the 0.4.12 Bench tab's facts as pips, unlock icons and cost slots; the payment is benchUp, unchanged)
M(page, r"""
public void fillBenchSide(java.util.Properties p, @IC@[] cs, int kd, int tier, int to, long at, long now) {
  this.vPip = new String[4]; this.vTx = new String[6]; this.vTxC = new String[6];
  this.vIt = new String[5]; this.vEd = new String[5]; this.vCIt = new String[3]; this.vCTx = new String[3]; this.vCC = new String[3];
  for (int n = 1; n <= 4; n++) this.vPip[n - 1] = n == tier ? "@SEL@" : (n < tier ? "@ACT@" : "@ROWC@");
  for (int i = 0; i < 6; i++) { this.vTx[i] = ""; this.vTxC[i] = "@TEXT@"; }
  for (int i = 0; i < 5; i++) { this.vIt[i] = "@TI0@"; this.vEd[i] = TQC[0]; }
  for (int i = 0; i < 3; i++) { this.vCIt[i] = "@TI0@"; this.vCTx[i] = ""; this.vCC[i] = "@TEXT@"; }
  this.vN = 0; this.vCn = 0; this.vCan = false; this.vShow = false;
  this.vTxC[0] = "@ROW@";
  if (p == null) { this.vTx[0] = "This shard's file could not be read."; this.vTxC[0] = "@BAD@"; return; }
  if (at > now) {
    if (to >= 1 && to <= 4) this.vPip[to - 1] = "@GOLDP@";
    this.vTx[0] = "Upgrading to Bench " + @PKG@.ShTotem.ROMAN[to - 1]; this.vTxC[0] = "@GOLD@";
    this.vTx[1] = @PKG@.ShCore.secs((at - now + 999L) / 1000L) + " left, also offline. It works at Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " meanwhile.";
    return;
  }
  if (tier >= 4) { this.vTx[0] = "Fully upgraded - Bench IV"; this.vTxC[0] = "@GOLD@"; this.vTx[1] = "Every totem and modifier of this shard is unlocked."; return; }
  int nt = tier + 1;
  this.vTx[0] = "Bench " + @PKG@.ShTotem.ROMAN[tier - 1] + " -> " + @PKG@.ShTotem.ROMAN[nt - 1] + " unlocks:";
  StringBuilder nb = new StringBuilder();
  for (int ti = 0; ti < @PKG@.ShTotem.KEYS.length; ti++) {
    if (!@PKG@.ShTotem.accepts(ti, kd)) continue;
    int u = @PKG@.ShCfg.benchUnlock(kd, ti);
    if ((u < 1 ? 1 : u) != nt) continue;
    if (this.vN < 5) { this.vIt[this.vN] = @PKG@.ShTotem.ITEMS[ti]; this.vEd[this.vN] = TQC[nt - 1]; this.vN++; }
    if (nb.length() > 0) nb.append(", ");
    nb.append(@PKG@.ShTotem.BASE[ti]);
  }
  for (int mi = 0; mi < @PKG@.ShTotem.MOD_NAMES.length; mi++) {
    if (@PKG@.ShCfg.modUnlock(mi) != nt) continue;
    if (this.vN < 5) { this.vIt[this.vN] = @PKG@.ShTotem.MOD_ITEMS[mi]; this.vEd[this.vN] = TQC[nt - 1]; this.vN++; }
    if (nb.length() > 0) nb.append(", ");
    nb.append(@PKG@.ShTotem.MOD_NAMES[mi]);
  }
  this.vTx[1] = (nb.length() > 0 ? nb.toString() + " - " : "") + "totems up to " + @PKG@.ShTotem.LADDER[@PKG@.ShCfg.benchCap(nt) - 1] + ".";
  String miss = "";
  long coins = @PKG@.ShCfg.BENCH_COINS[nt];
  long purse = @PKG@.ShPay.coins(this.me);
  boolean cok = purse < 0L || purse >= coins;
  this.vTx[2] = @PKG@.ShCfg.num(coins) + " coins (you have " + (purse < 0L ? "?" : @PKG@.ShCfg.num(purse)) + ")"; this.vTxC[2] = cok ? "@GOOD@" : "@BAD@";
  if (!cok) miss = @PKG@.ShCfg.num(coins - purse) + " more coins";
  String txt = @PKG@.ShCfg.benchItems(nt, kd).trim();
  Object[] rc = null;
  if (txt.length() > 0) rc = @PKG@.ShCore.recipe(txt);
  boolean broken = txt.length() > 0 && rc == null;
  if (rc != null) {
    String[] ids = (String[]) rc[0];
    long[] q = (long[]) rc[1];
    for (int i = 0; i < ids.length; i++) {
      long h = hav(cs, ids[i]);
      boolean ok = cs != null && h >= q[i];
      if (this.vCn < 3) { this.vCIt[this.vCn] = ids[i]; this.vCTx[this.vCn] = (cs == null ? "?" : shortN(h)) + " / " + shortN(q[i]); this.vCC[this.vCn] = ok ? "@GOOD@" : "@BAD@"; this.vCn++; }
      if (!ok && miss.length() == 0) miss = @PKG@.ShCfg.num(q[i] - (h < 0L ? 0L : h)) + " more " + @PKG@.ShTotem.pretty(ids[i]);
    }
  }
  int need = @PKG@.ShCfg.BENCH_NEED[nt];
  boolean lok = true;
  if (need > 0) {
    int ct = @PKG@.ShPay.collTier(this.me, @PKG@.ShKind.COLL[kd]);
    lok = ct >= need;
    this.vTx[3] = @PKG@.ShKind.CNAME[kd] + " collection " + need + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ")"; this.vTxC[3] = lok ? "@GOOD@" : "@BAD@";
    if (!lok && miss.length() == 0) miss = @PKG@.ShKind.CNAME[kd] + " collection " + need;
  }
  this.vTx[4] = "Takes " + @PKG@.ShCore.secs((long) @PKG@.ShCfg.BENCH_SEC[nt]) + ", also offline."; this.vTxC[4] = "@CAP@";
  this.vShow = true;
  if (broken) { this.vTx[5] = "The upgrade item setting is broken (Server Setup)."; this.vTxC[5] = "@BAD@"; }
  else if (!this.mine) { this.vTx[5] = "Only the island owner upgrades the bench."; this.vTxC[5] = "@CAP@"; }
  else if (miss.length() > 0) { this.vTx[5] = "Missing: " + miss + "."; this.vTxC[5] = "@BAD@"; }
  else { this.vTx[5] = "Ready to upgrade."; this.vTxC[5] = "@GOOD@"; }
  this.vCan = this.eCan && !broken && miss.length() == 0;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@CAP@", SUI.COLOR["caption"])
     .replace("@ROW@", SUI.COLOR["rowName"]).replace("@TI0@", TOTEM_ITEM[0]).replace("@SEL@", SUI.COLOR["selected"]).replace("@ACT@", SUI.COLOR["accentPressed"])
     .replace("@ROWC@", SUI.COLOR["row"]).replace("@GOLDP@", GOLD))
M(page, r"""
public void fillBenchGrid(java.util.Properties p, @IC@[] cs, int kd, int tier, int to, long at, long now) {
  int gn = @GN@;
  this.gIt = new String[gn]; this.gEd = new String[gn]; this.gDot = new String[gn]; this.gLk = new String[gn]; this.gRef = new int[gn];
  for (int i = 0; i < gn; i++) { this.gIt[i] = "@TI0@"; this.gEd[i] = TQC[0]; this.gDot[i] = ""; this.gLk[i] = ""; this.gRef[i] = -1; }
  this.qInIt = new String[4]; this.qInTx = new String[4]; this.qInC = new String[4];
  for (int i = 0; i < 4; i++) { this.qInIt[i] = "@TI0@"; this.qInTx[i] = ""; this.qInC[i] = "@TEXT@"; }
  this.qHas = false; this.qIt = "@TI0@"; this.qRar = TQC[0]; this.qNm = ""; this.qTag = ""; this.qDs = ""; this.qIn = 0; this.qCo = ""; this.qCoC = "@TEXT@";
  this.qWhy = ""; this.qWhyC = "@BAD@"; this.qCan = false;
  this.qBag = this.bagSt < 0 ? "Pocket Dimension paused - only your inventory counts now." : (this.bagSt > 0 ? "Counts your inventory and your Pocket Dimension." : "Counts your inventory.");
  this.gN = 0; this.gSel = -1;
  if (this.bCat < 0 || this.bCat > 4) this.bCat = 0;
  if (this.bCat != 4 && !this.bHold) { int c = catOf(kd, this.kSel); if (c >= 0) this.bCat = c; }
  this.gTitle = CATS[this.bCat];
  if (this.bCat < 4) {
    long purse = @PKG@.ShPay.coins(this.me);
    int[] l = catList(kd, this.bCat);
    for (int j = 0; j < l.length && this.gN < gn; j++) {
      int i = l[j];
      int r = this.gN;
      String id = @PKG@.ShCfg.CRAFT_ID[i];
      this.gIt[r] = id; this.gRef[r] = i;
      this.gEd[r] = @PKG@.ShKind.ofShard(id) >= 0 ? TQC[3] : TQC[needOf(kd, i) - 1];
      String bg = @PKG@.ShCore.benchGate(kd, tier, i);
      String g = bg != null ? bg : @PKG@.ShCore.craftGate(this.me, i);
      Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]);
      boolean items = rc != null && haveB(rc, cs);
      long co = rc == null ? 0L : ((Long) rc[2]).longValue();
      boolean coins = purse < 0L || purse >= co;
      if (bg != null) this.gLk[r] = "Bench " + @PKG@.ShTotem.ROMAN[needOf(kd, i) - 1];
      else this.gDot[r] = (g != null || rc == null) ? "@BAD@" : (items && coins ? "@GOOD@" : "@GOLD@");
      if (i == this.kSel) this.gSel = r;
      this.gN++;
    }
    this.gEmpty = "Nothing in this group at this bench.";
    fillPickCraft(kd, tier, cs, purse);
  } else {
    int cap = @PKG@.ShCfg.benchCap(tier);
    for (int r = 0; r < this.rN && this.gN < gn; r++) {
      int ti = @PKG@.ShTotem.idx(this.rTy[r]);
      this.gIt[r] = ti >= 0 ? @PKG@.ShTotem.ITEMS[ti] : "@TI0@"; this.gRef[r] = r; this.gEd[r] = TQC[0];
      String c = this.rCost[r];
      Object[] rc = null;
      if (c != null && c.length() > 0 && !c.startsWith("err:")) rc = @PKG@.ShCore.recipe(c);
      if (this.rTier[r] + 1 > cap) this.gLk[r] = "Bench " + @PKG@.ShTotem.ROMAN[tier < 4 ? tier : 3];
      else this.gDot[r] = rc == null ? "@BAD@" : (haveB(rc, cs) ? "@GOOD@" : "@GOLD@");
      this.gN++;
    }
    this.gEmpty = "No hand-held Totem I of this shard in your inventory. Craft a Rain, Fertilizer or Blessing of the Sun totem first - it starts as Totem I.";
    fillPickPole(kd, tier, cs);
  }
  fillBenchSide(p, cs, kd, tier, to, at, now);
}""".replace("@GN@", str(GN)).replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@TI0@", TOTEM_ITEM[0]))
'''
# ==END==

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.12.py"), os.path.join(HERE, "build_skyyshards_0.4.13.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.12"\n') and P.has("GENERATED by tools/shards_0_4_12_patch.py") and not P.has("fillTotemPage"), "not the generated SkyyShards 0.4.12"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.13 (2026-10-25)"):].rstrip() + "\n"

P.rep('''"""SkyyShards 0.4.12 - build script (javassist via jpype). GENERATED by tools/shards_0_4_12_patch.py from build_skyyshards_0.4.11.py
(generated by tools/shards_0_4_11_patch.py from 0.4.10, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.12" / "0.4.11" / "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.12.py   -> SkyyShards/SkyyShards-0.4.12.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.12.py
''', '''"""SkyyShards 0.4.13 - build script (javassist via jpype). GENERATED by tools/shards_0_4_13_patch.py from build_skyyshards_0.4.12.py
(generated by tools/shards_0_4_12_patch.py from 0.4.11, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.13" / "0.4.12" / "0.4.11" / "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.13.py   -> SkyyShards/SkyyShards-0.4.13.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.13.py
''' + NOTE + '''
0.4.12 notes:
''')
P.rep('VERSION = "0.4.12"\n', 'VERSION = "0.4.13"\n')

# ---------------------------------------------------------------------------------------------------- 1. config: the aura rows
P.rep('''          "public static volatile String PARTICLE = %s;" % jlit(PARTICLE), "public static volatile int PART_SEC = 2;",''',
      '''          "public static volatile String PARTICLE = %s;" % jlit(PARTICLE), "public static volatile int PART_SEC = 2;",
          "public static volatile int AURA_SEC = 30;", "public static volatile String AURA_EDGE = %s;" % jlit(AURA_EDGE),   # 0.4.13: the range aura
          "public static volatile String AURA_CELL = %s;" % jlit(AURA_CELL),''')
P.rep('''PARTICLE = "Dust_Sparkles_Fine"
''', '''PARTICLE = "Dust_Sparkles_Fine"
AURA_EDGE, AURA_CELL = "Block_Top_Glow", "Seed_Place_Dust"   # 0.4.13: the range aura (vanilla: a 1.5 s glow square on a block top / a small seed puff)
''')
P.rep('''assert any(n.endswith("/" + PARTICLE + ".particlesystem") for n in AZN), "particle system %s missing" % PARTICLE
''', '''assert any(n.endswith("/" + PARTICLE + ".particlesystem") for n in AZN), "particle system %s missing" % PARTICLE
for _pp in (AURA_EDGE, AURA_CELL):
    assert any(n.endswith("/" + _pp + ".particlesystem") for n in AZN), "0.4.13: particle system %s missing" % _pp
''')
P.rep('''    "totem.particleSec=2",
''', '''    "totem.particleSec=2",
    "# 0.4.13 totem.rangeAuraSec = seconds the Show range aura stays after the totem page closes (0 = off at once); rangeEdge / rangeCell = its particles.",
    "totem.rangeAuraSec=30",
    "totem.rangeEdge=" + AURA_EDGE,
    "totem.rangeCell=" + AURA_CELL,
''')
P.rep('''     "Seconds between two particle bursts above a working totem.", "field:ShCfg.PART_SEC@config.properties:totem.particleSec"),
]''', '''     "Seconds between two particle bursts above a working totem.", "field:ShCfg.PART_SEC@config.properties:totem.particleSec"),
    ("totem.rangeAuraSec", "Range aura after closing", "shards", "int", "30", "0", "600", "", "s", "live",
     "Seconds Show range stays after the totem page closes (only that player sees it). 0 = off at once.",
     "field:ShCfg.AURA_SEC@config.properties:totem.rangeAuraSec"),   # 0.4.13
    ("totem.rangeEdge", "Range aura edge particle", "shards", "text", AURA_EDGE, "", "120", "", "", "live",
     "The vanilla particle system drawn on the range edge by Show range.", "field:ShCfg.AURA_EDGE@config.properties:totem.rangeEdge"),
    ("totem.rangeCell", "Range aura cell particle", "shards", "text", AURA_CELL, "", "120", "", "", "live",
     "The vanilla particle system on the cells a totem works (Show range).", "field:ShCfg.AURA_CELL@config.properties:totem.rangeCell"),
]''')
P.rep('''          "  PART_SEC = intOf(p.getProperty(\\"totem.particleSec\\"), 2, 1, 60);"]''',
      '''          "  PART_SEC = intOf(p.getProperty(\\"totem.particleSec\\"), 2, 1, 60);",
          "  AURA_SEC = intOf(p.getProperty(\\"totem.rangeAuraSec\\"), 30, 0, 600);",   # 0.4.13
          "  String ae = p.getProperty(\\"totem.rangeEdge\\");", "  AURA_EDGE = (ae == null || ae.trim().length() == 0) ? %s : ae.trim();" % jlit(AURA_EDGE),
          "  String ac = p.getProperty(\\"totem.rangeCell\\");", "  AURA_CELL = (ac == null || ac.trim().length() == 0) ? %s : ac.trim();" % jlit(AURA_CELL)]''')
# the aura particles as sent: an admin's name only when the game has that particle system (the fix2 particle() rule, one WARN)
P.rep('''  return Boolean.TRUE.equals(seen) ? n : @DEF@;
}""".replace("@DEF@", jlit(PARTICLE)))''', '''  return Boolean.TRUE.equals(seen) ? n : @DEF@;
}""".replace("@DEF@", jlit(PARTICLE)))
M(cfg, r"""
public static String partOr(String n, String def, String row) {
  if (n == null || n.length() == 0 || n.equals(def)) return def;
  Object seen = PART_SEEN.get(n);
  if (seen == null) {
    boolean good = false;
    try {
      if (PART_TEST != null) good = Boolean.TRUE.equals(PART_TEST.apply(n));
      else { @DAM@ m = @PSY@.getAssetMap(); good = m != null && m.getAsset((Object) n) != null; }
    } catch (Throwable t) { good = false; }
    seen = Boolean.valueOf(good);
    PART_SEEN.put(n, seen);
    if (!good) warnOnce("particle:" + n, row + " '" + n + "' is not a particle system of this game - showing " + def + " instead (Server Setup -> Shards)");
  }
  return Boolean.TRUE.equals(seen) ? n : def;
}""")   # 0.4.13: the range aura's particles (totem.rangeEdge / totem.rangeCell)''')

# ---------------------------------------------------------------------------------------------------- 2. the aura (per player)
P.rep('''M(core, "public static String showRange(String k, int slot, int pad) { return showRange(k, FK, slot, pad); }")
''', '''M(core, "public static String showRange(String k, int slot, int pad) { return showRange(k, FK, slot, pad); }")
# 0.4.13 THE RANGE AURA (Skyy: "the show range button should show an aura to indicate what range it has"): per player, a toggle on the totem
# page; AURA = uuid -> Object[]{ world, double[]{ x, y, z, range, until ms, island size } }; ShTick hands each live one to ShAura every second
# (that player only). Open page = 10 minutes (refreshed by every build of the page), closed = totem.rangeAuraSec more; memory only.
F(core, "public static final java.util.concurrent.ConcurrentHashMap AURA = new java.util.concurrent.ConcurrentHashMap();")
F(core, "public static final long AURA_OPEN_MS = 600000L;")
M(core, "public static boolean auraOn(java.util.UUID u) { return u != null && AURA.get(u) != null; }")
M(core, r"""
public static int auraSet(java.util.UUID u, String k, int kd, int slot, int pad, long until) {
  if (u == null || k == null) return -1;
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return -1;
  String[] f;
  int sz = 1;
  @PKG@.ShStore.LOCK.lock(); try { f = at(kd, p, slot, pad); if (f != null) sz = @PKG@.ShMath.size(kd, p, slot); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (f == null) return -1;
  int r = @PKG@.ShTotem.range(f, now());
  double[] c = @PKG@.ShGeo.totemSpot(kd, slot);
  int[] o = @PKG@.ShTotem.posOf(f);   // a pole placed by hand: its own spot (dx, dz from the island centre)
  AURA.put(u, new Object[] { @PKG@.ShWorlds.name(k), new double[] { c[0], (double) @PKG@.ShGeo.Y, c[2], (double) r, (double) until, (double) (sz < 1 ? 1 : (sz > 3 ? 3 : sz)),
      (double) (o == null ? 0 : o[0]), (double) (o == null ? 0 : o[1]) } });
  return r;
}""")
M(core, r"""
public static String auraToggle(java.util.UUID u, String k, int kd, int slot, int pad) {
  if (u == null) return "";
  if (AURA.remove(u) != null) return "=Range hidden.";
  int r = auraSet(u, k, kd, slot, pad, System.currentTimeMillis() + AURA_OPEN_MS);
  if (r < 0) return "-That totem is gone - the page is up to date now.";
  int s = @PKG@.ShCfg.AURA_SEC;
  return "=Range " + r + " blocks: a ring marks the edge, puffs mark the cells it works. Only you see it" + (s > 0 ? " - it stays " + s + " s after you close this page." : ".");
}""")
M(core, r"""
public static void auraKeep(java.util.UUID u, String k, int kd, int slot, int pad) {
  if (u == null || AURA.get(u) == null) return;
  auraSet(u, k, kd, slot, pad, System.currentTimeMillis() + AURA_OPEN_MS);
}""")
M(core, r"""
public static void auraClose(java.util.UUID u) {
  if (u == null) return;
  Object o = AURA.get(u);
  if (!(o instanceof Object[])) return;
  int s = @PKG@.ShCfg.AURA_SEC;
  if (s <= 0) { AURA.remove(u); return; }
  double[] c = (double[]) ((Object[]) o)[1];
  long until = System.currentTimeMillis() + 1000L * (long) s;
  if ((long) c[4] > until) c[4] = (double) until;
}""")
''')
P.rep('''    DRAWS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("range", "the range circle failed (logged once): " + t); }
}""")
''', '''    DRAWS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("range", "the range circle failed (logged once): " + t); }
}""")
# 0.4.13 the range aura (world thread, once a second, ONE player): the edge ring (totem.rangeEdge on radius range + 0.5, one particle a block
# of the circle, 16-128) + a rotating fifth of the covered crop cells (totem.rangeCell; the ShTotem.cov rule: inside the island rim, not the
# centre 3 x 3, dx^2 + dz^2 <= range^2). The player is not in this world any more = the aura ends.
aura = mk("ShAura", None, ("java.lang.Runnable",))
F(aura, "public @WLD@ w;")
F(aura, "public java.util.UUID u;")
F(aura, "public double[] c;")
F(aura, "public long n;")
F(aura, "public static final java.util.concurrent.atomic.AtomicLong DRAWS = new java.util.concurrent.atomic.AtomicLong();")
F(aura, "public static final int[] HALF = new int[] { %s };" % ", ".join(str(_h) for _h in HALF))
C(aura, "public ShAura(@WLD@ w, java.util.UUID u, double[] c, long n) { this.w = w; this.u = u; this.c = c; this.n = n; }")
M(aura, r"""
public void run() {
  try {
    @REF@ ref = null;
    java.util.Iterator it = this.w.getPlayerRefs().iterator();
    while (it.hasNext() && ref == null) {
      @PR@ pr = (@PR@) it.next();
      if (pr != null && pr.isValid() && this.u.equals(pr.getUuid())) ref = pr.getReference();
    }
    if (ref == null || !ref.isValid()) { @PKG@.ShCore.AURA.remove(this.u); return; }
    java.util.ArrayList to = new java.util.ArrayList();
    to.add(ref);
    @CA@ ca = (@CA@) this.w.getEntityStore().getStore();
    String edge = @PKG@.ShCfg.partOr(@PKG@.ShCfg.AURA_EDGE, "@EDGE@", "totem.rangeEdge");
    String cell = @PKG@.ShCfg.partOr(@PKG@.ShCfg.AURA_CELL, "@CELL@", "totem.rangeCell");
    double cx = this.c[0];
    double y = this.c[1];
    double cz = this.c[2];
    int ox = this.c.length > 7 ? (int) this.c[6] : 0;   // the totem's spot on the island (0, 0 = the centre pads)
    int oz = this.c.length > 7 ? (int) this.c[7] : 0;
    int r = (int) this.c[3];
    int sz = (int) this.c[5];
    double rr = (double) r + 0.5;
    int n = (int) Math.round(2.0 * Math.PI * rr);
    if (n < 16) n = 16;
    if (n > 128) n = 128;
    for (int i = 0; i < n; i++) {
      double a = 2.0 * Math.PI * (double) i / (double) n;
      @PTU@.spawnParticleEffect(edge, (@V3DC@) new @V3D@(cx + (double) ox + rr * Math.cos(a), y + 0.5, cz + (double) oz + rr * Math.sin(a)), (java.util.List) to, ca);
    }
    int h = HALF[sz >= 3 ? 2 : (sz == 2 ? 1 : 0)];
    int lim = r * r;
    int ph = (int) (this.n % 5L);
    for (int dx = 1 - h; dx < h; dx++) {
      for (int dz = 1 - h; dz < h; dz++) {
        if ((dx - ox) * (dx - ox) + (dz - oz) * (dz - oz) > lim) continue;
        int ax = dx < 0 ? -dx : dx;
        int az = dz < 0 ? -dz : dz;
        if (ax <= 1 && az <= 1) continue;
        if (((dx * 3 + dz * 7) % 5 + 5) % 5 != ph) continue;
        @PTU@.spawnParticleEffect(cell, (@V3DC@) new @V3D@(cx + (double) dx, y, cz + (double) dz), (java.util.List) to, ca);
      }
    }
    DRAWS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("aura", "the range aura failed (logged once): " + t); }
}""".replace("@EDGE@", AURA_EDGE).replace("@CELL@", AURA_CELL))
''')
P.rep('''      sw.execute(new @PKG@.ShRain(sw, sc, (String) sv[2]));
    }
''', '''      sw.execute(new @PKG@.ShRain(sw, sc, (String) sv[2]));
    }
    java.util.Iterator au = @PKG@.ShCore.AURA.entrySet().iterator();   // 0.4.13: the per-player range auras
    while (au.hasNext()) {
      java.util.Map.Entry ae = (java.util.Map.Entry) au.next();
      Object[] av = (Object[]) ae.getValue();
      double[] ac = (double[]) av[1];
      if ((long) ac[4] < now) { au.remove(); continue; }
      @WLD@ aw = @UNI@.get().getWorld((String) av[0]);
      if (aw == null || !aw.isAlive()) { au.remove(); continue; }
      aw.execute(new @PKG@.ShAura(aw, (java.util.UUID) ae.getKey(), ac, this.n));
    }
''')

# ---------------------------------------------------------------------------------------------------- 3. the markup: view 3 + view 4
_a = P.s.index("# --- 0.4 VIEW 3: a placed totem's OWN page")
_e = P.s.index("SUI.assert_proven([mk_ for v in VARIANTS")
OLDV = P.s[_a:_e]
assert OLDV.count("BUILD_TOTEM = ") == 1 and OLDV.count("BUILD_BENCH = ") == 1 and OLDV.endswith("])\n"), "0.4.13: the view 3 + 4 block"
NEWV = PAGES
assert NEWV.startswith("# --- 0.4.13 VIEW 3") and '"""' not in NEWV.split("\n", 1)[0]
P.rep(OLDV, NEWV)
P.rep('''print("shard pages: menu %d segments + bench %d segments, %d variants checked, menu %d x %d (content %d px), exit 640 x 340, totem 660 x 700, bench %d x %d"
      % (len(SEG), len(BSEG), len(VARIANTS), MENU_W, MENU_H, MENU_CH, PW, PH))''',
      '''print("shard pages: menu %d segments + bench %d segments, %d variants checked, menu %d x %d (content %d px), exit 640 x 340, totem %d x %d, bench %d x %d"
      % (len(SEG), len(BSEG), len(VARIANTS), MENU_W, MENU_H, MENU_CH, WPW, WPH, BPW, BPH))   # 0.4.13''')

# ---------------------------------------------------------------------------------------------------- 4. ShPage: fields, fills, clicks
P.rep('''          "public boolean rCan;", "public String[] eTx;", "public String[] eCol;", "public String[] fTx;", "public String[] fCol;", "public boolean eCan;"):
    F(page, f)''', '''          "public boolean rCan;", "public String[] eTx;", "public String[] eCol;", "public String[] fTx;", "public String[] fCol;", "public boolean eCan;",
          # 0.4.13 the totem page (w*), the bench grid (b / g*), the selected recipe (q*), the bench upgrade side panel (v*), the pole rows' type + cost
          "public String wItem;", "public String wRar;", "public String wName;", "public String wTag;", "public String wRole;", "public String wRgTx;",
          "public String wRgCap;", "public int wPic;", "public boolean wAura;", "public String wOutW;", "public String wOut;", "public String wOutC;",
          "public String wOutU;", "public String wOut2;", "public int wBarF;", "public String wOut3;", "public String wOut3C;", "public String[] wSd;",
          "public String[] wSdC;", "public boolean wSdGive;", "public boolean wSdTake;", "public String[] wBo;", "public String[] wBoC;", "public String wBoIt;",
          "public boolean wBoOn;", "public boolean wBoCan;", "public String[] wTu;", "public String[] wTuC;", "public boolean wTuCan;", "public String[] wMIt;",
          "public String[] wMNm;", "public String[] wMNmC;", "public String[] wMEf;", "public String[] wMEfC;", "public boolean[] wMHas;", "public boolean[] wMRem;",
          "public String[] wMl;", "public String[] wMlC;", "public boolean[] wMAdd;", "public String wMdC;",
          "public int bCat;", "public boolean bHold;", "public int gN;", "public int gSel;", "public String[] gIt;", "public String[] gEd;", "public String[] gDot;",
          "public String[] gLk;", "public int[] gRef;", "public String gTitle;", "public String gEmpty;",
          "public boolean qHas;", "public String qIt;", "public String qRar;", "public String qNm;", "public String qTag;", "public String qDs;", "public int qIn;",
          "public String[] qInIt;", "public String[] qInTx;", "public String[] qInC;", "public String qCo;", "public String qCoC;", "public String qBag;",
          "public String qWhy;", "public String qWhyC;", "public boolean qCan;",
          "public String[] vPip;", "public String[] vTx;", "public String[] vTxC;", "public int vN;", "public String[] vIt;", "public String[] vEd;", "public int vCn;",
          "public String[] vCIt;", "public String[] vCTx;", "public String[] vCC;", "public boolean vCan;", "public boolean vShow;",
          "public String[] rTy;", "public String[] rCost;"):
    F(page, f)
for f in ("public static final String[] TQC = new String[] { %s };" % ", ".join(jlit(_c) for _c in TQC),        # 0.4.13: tier I-V -> rarity colour / name
          "public static final String[] TQN = new String[] { %s };" % ", ".join(jlit(_c) for _c in TQ),
          "public static final int[] RPB = new int[] { %s };" % ", ".join(str(_b) for _b in RPBASE),                 # the range pictures: base index per size
          "public static final int[] RPM = new int[] { %s };" % ", ".join(str(_m) for _m in RPMAX),                  # the last range drawn per size
          "public static final int BARW = %d;" % WBARW,
          "public static final String[] CATS = new String[] { %s };" % ", ".join(jlit(_c) for _c in BCATS),
          "public static final String WEATHER = %s;" % jlit("," + ",".join(WEATHER_KEYS) + ",")):
    F(page, f)''')
P.rep(''' this.rSel = 0; this.rN = 0; this.title = \\"\\"; this.tab = 1; this.mview = 0; this.zoom = 0; this.kZ = -1; this.kKind = -1;")''',
      ''' this.rSel = 0; this.rN = 0; this.title = \\"\\"; this.tab = 1; this.mview = 0; this.zoom = 0; this.kZ = -1; this.kKind = -1;"
              " this.bCat = 0; this.bHold = false; this.gN = 0; this.gSel = -1;")   # 0.4.13: the bench category / grid''')
# the pole rows keep their type + tier-up cost (the bench grid's dots and the selected panel read them)
P.rep('''  this.rTx = new String[9]; this.rCol = new String[9];
''', '''  this.rTx = new String[9]; this.rCol = new String[9];
  this.rTy = new String[@RR@]; this.rCost = new String[@RR@];   // 0.4.13
  for (int i = 0; i < @RR@; i++) { this.rTy[i] = ""; this.rCost[i] = ""; }
''')
P.rep('''    this.rUid[r] = @PKG@.ShTotem.dstr((@BD@) a[3], "uid");
''', '''    this.rUid[r] = @PKG@.ShTotem.dstr((@BD@) a[3], "uid");
    this.rTy[r] = f[0];   // 0.4.13
    this.rCost[r] = @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[ti], @PKG@.ShTotem.doc(f, now).toJson());
''')
P.rep('''  if (p == null) { this.kCan = false; this.rCan = false; this.eCan = false; }
}''', '''  if (p == null) { this.kCan = false; this.rCan = false; this.eCan = false; }
  fillBenchGrid(p, cs, kd, tier, to, at, now);   // 0.4.13: the vanilla-bench page
}''')
P.rep('''  else this.bSub = tier >= 4 ? "Fully upgraded" : "Next: Bench " + @PKG@.ShTotem.ROMAN[tier] + " - see the Bench tab";''',
      '''  else this.bSub = tier >= 4 ? "Fully upgraded" : "Next: Bench " + @PKG@.ShTotem.ROMAN[tier] + " - see the upgrade on the right";   // 0.4.13: no Bench tab''')
P.rep('''M(page, r"""
public void fillBench(String k, @IC@[] cs) {''', FILLS + '''M(page, r"""
public void fillBench(String k, @IC@[] cs) {''')
P.rep('''    if (this.view == 3) this.title = this.dHas ? @PKG@.ShTotem.name(@PKG@.ShTotem.onPad(@PKG@.ShTotem.entries(this.kind, @PKG@.ShStore.get(k), this.tIsl)[this.tpad])) : "Totem";
''', '''    if (this.view == 3) this.title = this.dHas ? @PKG@.ShTotem.name(@PKG@.ShTotem.onPad(@PKG@.ShTotem.entries(this.kind, @PKG@.ShStore.get(k), this.tIsl)[this.tpad])) : "Totem";
    if (this.view == 3) fillTotemPage(k, cs);   // 0.4.13: the card page
''')
# the bench clicks: a category, a grid slot (the craft index / the pole row it showed)
P.rep('''public String actBench(String a, @REF@ ref, @ST@ st) {
''', '''public String actBench(String a, @REF@ ref, @ST@ st) {
  if (a.startsWith("bcat")) {   // 0.4.13: a category - its first recipe (an empty one holds the category)
    int t = -1;
    try { t = Integer.parseInt(a.substring(4)); } catch (Throwable x) { t = -1; }
    if (t < 0 || t > 4) return "";
    this.bCat = t; this.bHold = false;
    if (t < 4) { int[] l = catList(@PKG@.ShKind.ok(this.kind) ? this.kind : @PKG@.ShKind.FARM, t); if (l.length > 0) this.kSel = l[0]; else this.bHold = true; }
    return "";
  }
  if (a.startsWith("bg")) {   // 0.4.13: a grid slot = what the page showed there
    int n = -1;
    try { n = Integer.parseInt(a.substring(2)); } catch (Throwable x) { n = -1; }
    if (this.gRef == null || n < 0 || n >= this.gN || n >= this.gRef.length || this.gRef[n] < 0) return "";
    if (this.bCat == 4) this.rSel = this.gRef[n]; else { this.kSel = this.gRef[n]; this.bHold = false; }
    return "";
  }
''')
# the totem page clicks: seeds here, add a picked modifier, the aura toggle
P.rep('''  if (a.startsWith("tplace") || a.startsWith("tmod") || a.equals("tboost") || a.equals("trange") || a.startsWith("tup") || a.equals("tpick")) {''',
      '''  if (a.startsWith("tplace") || a.startsWith("tmod") || a.equals("tboost") || a.equals("trange") || a.startsWith("tup") || a.equals("tpick") || a.equals("wseed") || a.equals("wseedb")) {   // 0.4.13: + the seeds''')
P.rep('''    if (!this.dHas) return "-Pick a totem first.";
    if (a.equals("tmodadd")) return @PKG@.ShCore.addMod(u, k, kd, this.tIsl, this.tpad, this.modSel, cs);''',
      '''    if (!this.dHas) return "-Pick a totem first.";
    if (a.equals("wseed")) return @PKG@.ShCore.seedsGive(u, k, kd, this.tIsl, cs);   // 0.4.13: the totem page's Give / Take seeds (its island)
    if (a.equals("wseedb")) return @PKG@.ShCore.seedsTake(u, k, kd, this.tIsl, cs);
    if (a.startsWith("tmodadd") && a.length() > 7) {   // 0.4.13: Add on one modifier of the list
      int mi = (int) (a.charAt(7) - '0');
      if (mi < 0 || mi >= @PKG@.ShTotem.MOD_ITEMS.length) return "";
      this.modSel = mi;
      return @PKG@.ShCore.addMod(u, k, kd, this.tIsl, this.tpad, mi, cs);
    }
    if (a.equals("tmodadd")) return @PKG@.ShCore.addMod(u, k, kd, this.tIsl, this.tpad, this.modSel, cs);''')
P.rep('''    if (a.equals("trange")) return @PKG@.ShCore.showRange(k, kd, this.tIsl, this.tpad);''',
      '''    if (a.equals("trange")) return @PKG@.ShCore.auraToggle(u, k, kd, this.tIsl, this.tpad);   // 0.4.13: the per-player aura (was a 10 s circle for everyone)''')
P.rep('''M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''', '''M(page, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  try { @PKG@.ShCore.auraClose(this.me); } catch (Throwable t) { }
}""")   # 0.4.13: a closed page - the range aura stays totem.rangeAuraSec more
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {''')

# ==SAFE==
# ---------------------------------------------------------------------------------------------------- 6. LOCK DISCIPLINE (the live freeze)
# Skyy's island froze 2026-10-26 02:38 (NewBetaTest server log: "Abandoning TickingThread ... WorldThread - skyy-island-...-p3-r1 (stuck
# for >30000ms)" in ReentrantLock.lock <- ShCore.pauseStale <- ShPage.fill <- ShPage.build <- PageManager.openCustomPage): a world thread
# waited forever for ShStore.LOCK, held by a thread that never let go (no thread dump; SkyySacks saw HytaleServer.SCHEDULED_EXECUTOR stall
# in the same window and ShTick's idle unloads stopped after 01:54). Several paths hold the lock across other mods' bridges (SkyyCoins,
# SkyyCollections, SkyySacks take / put / commit, SkyyIslands roles) - one lock-order inversion with another mod's own lock = both stuck.
# FIX: (a) ShStore.LOCK is a ShLock: a reentrant lock whose lock() never waits forever - a world thread gives up after 50 ms, any other
# thread after 1.5 s (ShBusy); the first give-up of a minute logs the HOLDER thread + its stack (the next incident names the culprit).
# An inversion therefore breaks by itself: the side that times out unwinds (finally) and the other side goes on. (b) The page build
# catches ShBusy and draws a small "busy - try again" page (one packet); a click that hits it says so. (c) ShTick runs on Shards' OWN
# single daemon thread (SkyyShards-tick), not the shared HytaleServer.SCHEDULED_EXECUTOR (world unloads ~75 ms each no longer delay other
# mods; nothing of ours can stall it).
P.rep('''# ================= ShStore: Skyy_SkyyShards/shards/<pkey>.properties (one profile), cached, written at once (tmp + move) =================
st = mk("ShStore")''', '''# 0.4.13 the timed data lock (see the patch note: the 2026-10-26 freeze)
busyc = mk("ShBusy", "java.lang.RuntimeException")
C(busyc, "public ShBusy(String m) { super(m); }")
lockc = mk("ShLock", "java.util.concurrent.locks.ReentrantLock")
F(lockc, "public static volatile long WAIT_MS = 1500L;")
F(lockc, "public static volatile long WORLD_MS = 50L;")
F(lockc, "public static volatile long SAID = 0L;")
F(lockc, "public static final java.util.concurrent.atomic.AtomicLong TIMEOUTS = new java.util.concurrent.atomic.AtomicLong();")
F(lockc, "public static volatile String LAST = \\"\\";")
C(lockc, "public ShLock() { super(); }")
M(lockc, r"""
public String holder() {
  Thread o = getOwner();
  if (o == null) return "nobody (released meanwhile)";
  StringBuilder sb = new StringBuilder(o.getName());
  StackTraceElement[] st = o.getStackTrace();
  for (int i = 0; i < st.length && i < 30; i++) sb.append("\\n    at ").append(st[i].toString());
  return sb.toString();
}""")
M(lockc, r"""
public void lock() {
  if (isHeldByCurrentThread()) { super.lock(); return; }
  String me = Thread.currentThread().getName();
  long w = me != null && me.startsWith("WorldThread") ? WORLD_MS : WAIT_MS;
  boolean got = false;
  try { got = tryLock(w, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (InterruptedException e) { Thread.currentThread().interrupt(); got = false; }
  if (got) return;
  TIMEOUTS.incrementAndGet();
  long now = System.currentTimeMillis();
  if (now - SAID > 60000L) {
    SAID = now;
    String h = holder();
    LAST = h;
    @PKG@.ShCfg.warn("the shard data lock was busy for " + w + " ms - " + me + " gave up instead of waiting (a world thread never blocks on it). Holder: " + h);
  }
  throw new @PKG@.ShBusy("the shard data is busy");
}""")
thrc = mk("ShThreads", None, ("java.util.concurrent.ThreadFactory",))
C(thrc, "public ShThreads() { }")
M(thrc, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyShards-tick");
  t.setDaemon(true);
  return t;
}""")

# ================= ShStore: Skyy_SkyyShards/shards/<pkey>.properties (one profile), cached, written at once (tmp + move) =================
st = mk("ShStore")''')
P.rep('''          "public static final java.util.concurrent.locks.ReentrantLock LOCK = new java.util.concurrent.locks.ReentrantLock();"):''',
      '''          "public static final java.util.concurrent.locks.ReentrantLock LOCK = new @PKG@.ShLock();"):   # 0.4.13: timed (ShLock)''')
P.rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''',
      '''  this.exec = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.ShThreads());   // 0.4.13: our own tick thread
  this.ticker = this.exec.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);''')
P.rep('''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''',
      '''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.concurrent.ScheduledExecutorService exec;")   # 0.4.13''')
P.rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
''', '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.exec != null) this.exec.shutdownNow(); } catch (Throwable t) { }   // 0.4.13
''')
# the page: a busy lock = the small busy page (build), a busy click says so
P.rep('''M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.kst = null;''', '''M(page, r"""
public void buildBusy(@UCB@ b, @UEB@ ev) {
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", BUILD_BUSY))
M(page, r"""
public void build0(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.kst = null;''')
P.rep('''  if (this.kst != null && this.view == 0 && this.tab == 1) this.kShown = kShownSig(this.kZ);   // 0.4.10: the Map page the client gets
}""")''', '''  if (this.kst != null && this.view == 0 && this.tab == 1) this.kShown = kShownSig(this.kZ);   // 0.4.10: the Map page the client gets
}""")
F(page, "public static final java.util.concurrent.atomic.AtomicLong BUSY = new java.util.concurrent.atomic.AtomicLong();")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  try { build0(ref, b, ev, st); }
  catch (@PKG@.ShBusy x) { BUSY.incrementAndGet(); this.kst = null; this.kShown = null; buildBusy(b, ev); }   // 0.4.13: never wait on the data lock
}""")''')
P.rep('''  try { r = act(a, ref, st); } catch (Throwable t) { @PKG@.ShCfg.warn("shard page action " + a + " failed: " + t); r = "-Something went wrong - the server log has the details."; }''',
      '''  try { r = act(a, ref, st); } catch (Throwable t) {
    if (t instanceof @PKG@.ShBusy) r = "-The shard is busy right now - nothing changed, try again in a moment.";   // 0.4.13
    else { @PKG@.ShCfg.warn("shard page action " + a + " failed: " + t); r = "-Something went wrong - the server log has the details."; }
  }''')

# ---------------------------------------------------------------------------------------------------- 7. TOTEM POLES PLACED BY HAND (Skyy)
# Skyy 2026-10-26: "tried to place a new totem and the game broke, i should be able to place them wherever i want on the island" (the log:
# "Harvest Spirit Totem Pole I is a totem pole: place it from your ... Shard menu" each right-click). Now: right-click the farmland of one
# of your islands in the shard with a totem pole in hand = it stands THERE (inside the island's rim, not on the centre 3 x 3 = the pads,
# never on another totem; the island's totem count limit as before) and works the cells in its range around that spot; your range aura
# shows for totem.rangeAuraSec (min 10 s). Pick up gives it back and clears its block. Menu placement (Totems tab -> the pads) still works.
# DATA: the entry gets an 8th part "dx;dz" (after the flag part) only when placed by hand - every other entry is byte-identical; 0.4.12
# reads the first 7 parts (a rollback puts such a totem back on a pad by its list place; its hand-placed block stays as a plain block).
P.rep('''  String[] f = new String[] { "", "1", "", "", "0", "", "" };   // 0.4: f[6] = flags ("gf" = a grandfathered pre-0.4 tier-I hand-held kind)''',
      '''  String[] f = new String[] { "", "1", "", "", "0", "", "", "" };   // 0.4: f[6] = flags ("gf" = a grandfathered pre-0.4 tier-I hand-held kind); 0.4.13: f[7] = "dx;dz" placed by hand''')
P.rep('''  if (a.length > 6 && "gf".equals(a[6].trim())) f[6] = "gf";   // 0.4
  return f;''', '''  if (a.length > 6 && "gf".equals(a[6].trim())) f[6] = "gf";   // 0.4
  if (a.length > 7 && a[7].trim().matches("-?[0-9]{1,3};-?[0-9]{1,3}")) f[7] = a[7].trim();   // 0.4.13: its spot
  return f;''')
P.rep('''  if (f.length > 6 && f[6] != null && f[6].length() > 0) s = s + ":" + f[6];
  return s;''', '''  if (f.length > 7 && f[7] != null && f[7].length() > 0) s = s + ":" + (f[6] == null ? "" : f[6]) + ":" + f[7];   // 0.4.13: placed by hand
  else if (f.length > 6 && f[6] != null && f[6].length() > 0) s = s + ":" + f[6];
  return s;''')
P.rep('''M(tot, r"""
public static int cov(int size, int r) {''', '''F(tot, "public static final int[] HALFS = new int[] { %s };" % ", ".join(str(_h) for _h in HALF))   # 0.4.13
M(tot, r"""
public static int[] posOf(String[] f) {
  if (f == null || f.length < 8 || f[7] == null || f[7].length() == 0) return null;
  int c = f[7].indexOf(';');
  if (c <= 0) return null;
  try { return new int[] { Integer.parseInt(f[7].substring(0, c)), Integer.parseInt(f[7].substring(c + 1)) }; } catch (Throwable t) { return null; }
}""")   # 0.4.13: a hand-placed pole's spot (dx, dz from the island centre) or null (a pad)
M(tot, r"""
public static int covAt(int size, int r, int dx, int dz) {
  int h = HALFS[size >= 3 ? 2 : (size == 2 ? 1 : 0)];
  long lim = (long) r * (long) r;
  int n = 0;
  for (int x = 1 - h; x < h; x++) {
    for (int z = 1 - h; z < h; z++) {
      if (x >= -1 && x <= 1 && z >= -1 && z <= 1) continue;
      long a = (long) (x - dx);
      long b = (long) (z - dz);
      if (a * a + b * b <= lim) n++;
    }
  }
  return n;
}""")   # 0.4.13: the crop cells (the cov rule: inside the rim, not the centre 3 x 3) within r of (dx, dz)
M(tot, r"""
public static int cov(int size, int r) {''')
P.rep('''  double reach = (double) cov(size, range(f, t)) / (double) ref;''',
      '''  double reach = (double) covOf(size, f, range(f, t)) / (double) ref;   // 0.4.13: around its own spot when placed by hand''')
P.rep('''M(tot, r"""
public static double ownMult(String[] f, long t) {''', '''M(tot, r"""
public static int covOf(int size, String[] f, int r) {
  int[] o = posOf(f);
  return o == null ? cov(size, r) : covAt(size, r, o[0], o[1]);
}""")
M(tot, r"""
public static double ownMult(String[] f, long t) {''')
P.rep('''      this.dTx[1] = "Range " + r + " blocks: " + @PKG@.ShTotem.cov(sz, r) + " of " + @PKG@.ShTotem.cov(sz, 99) + " " + what;''',
      '''      this.dTx[1] = "Range " + r + " blocks: " + @PKG@.ShTotem.covOf(sz, f, r) + " of " + @PKG@.ShTotem.cov(sz, 99) + " " + what;   // 0.4.13''')
P.rep('''M(geo, "public static int[] padPos(int slot, int pad) { return padPos(FK, slot, pad); }")
''', '''M(geo, "public static int[] padPos(int slot, int pad) { return padPos(FK, slot, pad); }")
M(geo, r"""
public static int[] spotOf(int kd, java.util.Properties p, int slot, int i) {
  String[] e = @PKG@.ShTotem.entries(kd, p, slot);
  if (i >= 0 && i < e.length) {
    int[] o = @PKG@.ShTotem.posOf(@PKG@.ShTotem.parse(e[i]));
    if (o != null) return new int[] { ox(kd) + SX[slot] + o[0], Y + 1, OZ + SZ[slot] + o[1] };
  }
  return padPos(kd, slot, i);
}""")   # 0.4.13: where totem entry i stands (its own spot, else pad i)
''')
P.rep('''  String[] e = @PKG@.ShTotem.entries(kd, p, slot);
  for (int i = 0; i < 5; i++) {
    int[] q = padPos(kd, slot, i);
    int ti = i < e.length ? @PKG@.ShTotem.idx(@PKG@.ShTotem.parse(e[i])[0]) : -1;
    add(out, q[0], q[1], q[2], ti >= 0 ? TOTEM + ti : AIR);
  }
}""")''', '''  String[] e = @PKG@.ShTotem.entries(kd, p, slot);
  for (int i = 0; i < 5; i++) {
    int[] q = padPos(kd, slot, i);
    int ti = -1;
    if (i < e.length) { String[] f = @PKG@.ShTotem.parse(e[i]); if (@PKG@.ShTotem.posOf(f) == null) ti = @PKG@.ShTotem.idx(f[0]); }   // 0.4.13: a hand-placed one leaves its pad empty
    add(out, q[0], q[1], q[2], ti >= 0 ? TOTEM + ti : AIR);
  }
  for (int i = 0; i < e.length; i++) {   // 0.4.13: the hand-placed poles on their own spots (painted last: they win their cell)
    String[] f = @PKG@.ShTotem.parse(e[i]);
    int[] o = @PKG@.ShTotem.posOf(f);
    int ti = @PKG@.ShTotem.idx(f[0]);
    if (o == null || ti < 0) continue;
    add(out, ox(kd) + SX[slot] + o[0], Y + 1, OZ + SZ[slot] + o[1], TOTEM + ti);
  }
}""")''')
P.rep('''      int[] q = @PKG@.ShGeo.padPos(kd, s, i);
      double dx = (double) q[0] + 0.5 - x;''', '''      int[] q = @PKG@.ShGeo.spotOf(kd, p, s, i);   // 0.4.13: a hand-placed pole's own spot
      double dx = (double) q[0] + 0.5 - x;''')
# a picked-up hand-placed pole: its block goes (its cell is farmland again at the next paint)
P.rep('''M(w2, "public static boolean repaint(String k) { return repaint(k, %d); }" % FARM_K)
''', '''M(w2, "public static boolean repaint(String k) { return repaint(k, %d); }" % FARM_K)
clr = mk("ShClear", None, ("java.lang.Runnable",))
F(clr, "public @WLD@ w;")
F(clr, "public int[] q;")
F(clr, "public String k;")
F(clr, "public int kd;")
C(clr, "public ShClear(@WLD@ w, int[] q, String k, int kd) { this.w = w; this.q = q; this.k = k; this.kd = kd; }")
M(clr, r"""
public void run() {
  try {
    String id = @PKG@.ShFill.idAt(this.w, this.q[0], this.q[1], this.q[2]);
    if (id != null && id.startsWith("Skyy_TotemBlock_")) @PKG@.ShFill.clear(this.w, this.q[0], this.q[1], this.q[2]);
    @PKG@.ShWorld2.repaint(this.k, this.kd);
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("clear", "a picked-up totem's block could not be cleared (logged once): " + t); }
}""")
M(w2, r"""
public static boolean clearAt(String k, int kd, int[] q) {
  try {
    @WLD@ w = @UNI@.get().getWorld(@PKG@.ShWorlds.name(k));
    if (w == null || !w.isAlive() || q == null) return false;
    w.execute(new @PKG@.ShClear(w, q, k, kd));
    return true;
  } catch (Throwable t) { return false; }
}""")   # 0.4.13
''')
P.rep('''    String[] f = at(kd, p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (@PKG@.ShTotem.idx(f[0]) < 0) return "-That totem's type is unknown on this server - ask an admin (totem.log).";
    @PKG@.ShMath.settle(kd, p, slot, now);''', '''    String[] f = at(kd, p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (@PKG@.ShTotem.idx(f[0]) < 0) return "-That totem's type is unknown on this server - ask an admin (totem.log).";
    if (@PKG@.ShTotem.posOf(f) != null) gone = @PKG@.ShGeo.spotOf(kd, p, slot, pad);   // 0.4.13: a hand-placed pole's block is cleared after
    @PKG@.ShMath.settle(kd, p, slot, now);''')
P.rep('''    res = "+" + @PKG@.ShTotem.name(f) + " is in your inventory - its tier, modifiers and booster stay with it.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);''', '''    res = "+" + @PKG@.ShTotem.name(f) + " is in your inventory - its tier, modifiers and booster stay with it.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (gone != null && @PKG@.ShWorld2.clearAt(k, kd, gone)) return res;   // 0.4.13 (the clear repaints after)
  @PKG@.ShWorld2.repaint(k, kd);''')
P.rep('''public static String pickTotem(java.util.UUID u, String k, int kd, int slot, int pad, @IC@[] cs) {
  Object[] o = new Object[1];''', '''public static String pickTotem(java.util.UUID u, String k, int kd, int slot, int pad, @IC@[] cs) {
  int[] gone = null;   // 0.4.13
  Object[] o = new Object[1];''')
# placeAt = placeTotem0 with the spot (every 0.3-0.4.12 rule of the menu placement kept: owner, item taken first + counted, same uid,
# duplicate-uid guard, refused save = the same document back)
_a = P.s.index('M(core, r"""\npublic static String placeTotem0(')
_e = P.s.index('}""")\n', _a) + len('}""")\n')
_pa = P.s[_a:_e]
for _o, _n in (
        ("public static String placeTotem0(java.util.UUID u, String k, int kd, int slot, int ci, int si, @IC@[] cs) {   // 0.3.1: the 0.3 placeTotem, renamed",
         "public static String placeAt(java.util.UUID u, String k, int kd, int slot, int ci, int si, int dx, int dz, @IC@[] cs) {   // 0.4.13: a pole placed by hand where it stands"),
        ("  if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();\n",
         "  if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();\n  String[] g8 = new String[8];\n  for (int i = 0; i < 8; i++) g8[i] = i < f.length && f[i] != null ? f[i] : \"\";\n  f = g8;\n  f[7] = dx + \";\" + dz;\n"),
        ("    if (e.length >= pads) return \"-No free totem pad on this island (\" + e.length + \" of \" + pads + \"). Grow it or pick a totem up first.\";\n",
         "    if (e.length >= pads) return \"-This island has all its totems (\" + e.length + \" of \" + pads + \"). Grow it or pick a totem up first.\";\n"
         "    int hh = @PKG@.ShGeo.HALF[sz - 1];\n"
         "    if (dx <= -hh || dx >= hh || dz <= -hh || dz >= hh) return \"-That spot is off the island's farmland - a totem stands inside the island.\";\n"
         "    if (dx >= -1 && dx <= 1 && dz >= -1 && dz <= 1) return \"-The island's centre holds its totem pads - stand it on the farmland around it (or place it from the shard menu).\";\n"
         "    for (int i = 0; i < e.length; i++) { int[] q = @PKG@.ShTotem.posOf(@PKG@.ShTotem.parse(e[i])); if (q != null && q[0] == dx && q[1] == dz) return \"-Another totem stands right there - pick another spot.\"; }\n"),
        ('" place slot " + slot + " pad " + e.length + " "', '" place slot " + slot + " by hand at " + dx + "," + dz + " "'),
        ('    res = "+Placed " + @PKG@.ShTotem.name(f) + " on island " + (slot + 1) + " (pad " + (e.length + 1) + " of " + pads + ").";',
         '    res = "+Placed " + @PKG@.ShTotem.name(f) + " here on island " + (slot + 1) + " (" + (e.length + 1) + " of " + pads + " totems) - it works the crops in its range around this spot.";')):
    assert _pa.count(_o) == 1, _o[:80]
    _pa = _pa.replace(_o, _n)
P.rep('''M(core, "public static String placeTotem(java.util.UUID u, String k, int kd, int slot, int ci, int si, @IC@[] cs) { String r = placeTotem0(u, k, kd, slot, ci, si, cs); @PKG@.ShSnd.ok(u, r, 1); return r; }")   # 0.3.1''',
      '''M(core, "public static String placeTotem(java.util.UUID u, String k, int kd, int slot, int ci, int si, @IC@[] cs) { String r = placeTotem0(u, k, kd, slot, ci, si, cs); @PKG@.ShSnd.ok(u, r, 1); return r; }")   # 0.3.1
''' + _pa + '''M(core, r"""
public static int[] spotFor(java.util.Properties p, int kd, int bx, int bz) {
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(kd, p, s)) continue;
    int h = @PKG@.ShGeo.HALF[@PKG@.ShMath.size(kd, p, s) - 1];
    int dx = bx - (@PKG@.ShGeo.ox(kd) + @PKG@.ShGeo.SX[s]);
    int dz = bz - (@PKG@.ShGeo.OZ + @PKG@.ShGeo.SZ[s]);
    if (dx >= -h && dx <= h && dz >= -h && dz <= h) return new int[] { s, dx, dz };
  }
  return null;
}""")   # 0.4.13: the island (slot) + spot (dx, dz from its centre) of block column (bx, bz) in shard kd, or null
M(core, "public static String placeHere(java.util.UUID u, String k, int kd, int slot, int ci, int si, int dx, int dz, @IC@[] cs) { String r = placeAt(u, k, kd, slot, ci, si, dx, dz, cs); @PKG@.ShSnd.ok(u, r, 1); return r; }")
''')
P.rep('''M(hand, r"""
public static String use(@PR@ pr) {''', '''M(hand, r"""
public static String placeHand(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, @IS@ it, String id, String[] f) {
  java.util.UUID u = pr.getUuid();
  int ti = @PKG@.ShTotem.idx(f[0]);
  String nm = @PKG@.ShTotem.name(f);
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  String own = @PKG@.ShWorlds.ownerOf(w.getName());
  if (own == null) return "=" + nm + " is a totem pole: take it into your " + @PKG@.ShTotem.kindsOf(ti) + " Shard and right-click the farmland of an island where it should stand (or place it from the shard menu - Totems tab).";
  String k = @PKG@.ShCfg.pkey(u);
  if (k == null || !k.equals(own)) return "-Only the island owner places totems in this shard.";
  @V3I@ b = null;
  try { b = @TU@.getTargetBlockOrigin(ref, 8.0, st); } catch (Throwable t) { b = null; }
  if (b == null || b.y < @PKG@.ShGeo.Y - 1 || b.y > @PKG@.ShGeo.Y + 2) return "=Look at the island's farmland where the totem should stand, then right-click.";
  int kd = @PKG@.ShKind.ofX((double) b.x + 0.5);
  if (!@PKG@.ShKind.ok(kd)) return "-That is not a shard island.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  int[] sp;
  @PKG@.ShStore.LOCK.lock(); try { sp = @PKG@.ShCore.spotFor(p, kd, b.x, b.z); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (sp == null) return "-Look at the farmland of one of your " + @PKG@.ShKind.NAMES[kd] + " islands - a totem stands on an island, not beside it.";
  @IC@[] cs = @PKG@.ShInv.containers(st, ref);
  String uid = @PKG@.ShTotem.dstr(@PKG@.ShTotem.docOf(it), "uid");
  int[] at = null;
  if (uid.length() > 0) at = @PKG@.ShInv.findUid(cs, id, uid);
  if (at == null) {
    java.util.ArrayList l = @PKG@.ShInv.totems(cs);
    for (int i = 0; i < l.size() && at == null; i++) { Object[] a = (Object[]) l.get(i); if (id.equals(a[2]) && @PKG@.ShTotem.dstr((@BD@) a[3], "uid").length() == 0) at = new int[] { ((Integer) a[0]).intValue(), ((Integer) a[1]).intValue() }; }
  }
  if (at == null) return "-That totem moved in your inventory - try again.";
  String r = @PKG@.ShCore.placeHere(u, k, kd, sp[0], at[0], at[1], sp[1], sp[2], cs);
  if (r.startsWith("+")) {   // its range for a moment (only this player)
    int s2 = @PKG@.ShCfg.AURA_SEC < 10 ? 10 : @PKG@.ShCfg.AURA_SEC;
    int n = @PKG@.ShTotem.entries(kd, p, sp[0]).length - 1;
    if (n >= 0) @PKG@.ShCore.auraSet(u, k, kd, sp[0], n, System.currentTimeMillis() + 1000L * (long) s2);
  }
  return r;
}""")   # 0.4.13 (Skyy: "i should be able to place them wherever i want on the island")
M(hand, r"""
public static String use(@PR@ pr) {''')
P.rep('''  org.joml.Vector3d v = tc.getPosition();
  return act(pr.getUuid(), f, w, v.x, v.y, v.z, now);''', '''  org.joml.Vector3d v = tc.getPosition();
  if (!@PKG@.ShTotem.usable(f)) return placeHand(pr, ref, st, w, it, id, f);   // 0.4.13: a pole in hand = place it where you look
  return act(pr.getUuid(), f, w, v.x, v.y, v.z, now);''')
# ---------------------------------------------------------------------------------------------------- 8. REVIEW FIXES (research/Shards-0.4.13-Review.md)
# The timed lock (6.) can now throw ShBusy wherever ShStore.LOCK.lock() runs. Every path that pays (or hands out) BEFORE a later lock would
# lose the payment when that lock gives up, so: (1) benchUp, tierUpPlaced0 and a shard craft take the lock BEFORE paying (the purchaseM
# way; reentrant, so every inner lock - markCrafted, its undo, put / save - can never meet a busy lock); a busy lock = nothing taken, the
# click says "busy - nothing changed". (2) The collection / XP credit after a Collect (owed / owedXp, the items are given already): a busy
# lock keeps the due amount in memory (MEM_OWED, the fix2 path) - paid on the next Collect, never dropped. (3) tierUpPlaced0 keeps a
# hand-placed totem's 8th part "dx;dz" (the first 0.4.13 build dropped it = the pole jumped to a pad and its block went stale).
# (4) ShStore.get: the first-load migrations run under the lock taken BEFORE the cache sees the profile (busy = nothing cached, the next
# get loads + migrates again). (5) grow0's re-lock tracks a held flag (no IllegalMonitorStateException masking a busy lock); ShPlace's
# check of a placement re-queues it when unplace meets a busy lock; ShLv20.grant holds its lock through the give + its undo; placeHand's
# aura is cosmetic (a busy lock after a placement never turns the "+Placed" into "busy"); the regrow timestamp moves only after the mask.
_s = P.s.index("public static String benchUp(java.util.UUID u, String k, int kd, @IC@[] cs) {")
_a = P.s.index("  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags\n", _s)
_e = P.s.index("  } finally { @PKG@.ShStore.LOCK.unlock(); }\n  if (e != null) {\n", _a)
_old = P.s[_a:_e]
assert _old.count("payInvBags(") == 1 and _old.count("LOCK.lock()") == 1 and _old.count("takeCoins(") == 1
P.rep(_old, r'''  long[] took = null;
  int sec = @PKG@.ShCfg.BENCH_SEC[nt];
  String e;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.13 review: the lock BEFORE paying (a busy lock = nothing taken; it was: paid, then the lock gave up = lost)
    took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags
    if (took == null) return "-The items could not be taken - nothing was bought.";
    if (!@PKG@.ShPay.takeCoins(u, coins)) { refundPaid(u, cs, ids, took, bag, kept); return "-The coins could not be taken - your items are back."; }
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    p.setProperty(@PKG@.ShMath.kk(kd, "bench"), String.valueOf(sec <= 0 ? nt : tier));   // a finished earlier upgrade is folded in here
    if (sec <= 0) { p.remove(@PKG@.ShMath.kk(kd, "benchTo")); p.remove(@PKG@.ShMath.kk(kd, "benchUpAt")); }
    else { p.setProperty(@PKG@.ShMath.kk(kd, "benchTo"), String.valueOf(nt)); p.setProperty(@PKG@.ShMath.kk(kd, "benchUpAt"), String.valueOf(now + 1000L * (long) sec)); }
    e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); }
''')
# (1) + (3) tierUpPlaced0: pay under the lock; the 8th part kept
P.rep(r'''  long[] inv = payInvBags(u, cs, ids, q, kept, bag);
  if (inv == null) return "-The cost could not be taken - everything is back.";
  String res = null;
  String[] nf = null;
  java.util.Properties old = null;
  @PKG@.ShStore.LOCK.lock(); try {
    try {''', r'''  long[] inv = null;
  String res = null;
  String[] nf = null;
  java.util.Properties old = null;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.13 review: the lock BEFORE paying (a busy lock = nothing taken; it was: paid, then the lock gave up = lost)
    inv = payInvBags(u, cs, ids, q, kept, bag);
    if (inv == null) return "-The cost could not be taken - everything is back.";
    try {''')
P.rep(r'''        nf = new String[] { f2[0], String.valueOf(t + 1), f2[2], f2[3], f2[4], f2[5].length() == 0 ? @PKG@.ShTotem.newUid() : f2[5], "" };
        put(kd, p, slot, pad, nf);''', r'''        nf = new String[] { f2[0], String.valueOf(t + 1), f2[2], f2[3], f2[4], f2[5].length() == 0 ? @PKG@.ShTotem.newUid() : f2[5], "", f2.length > 7 && f2[7] != null ? f2[7] : "" };   // 0.4.13 review: a hand-placed totem keeps its spot (8th part)
        put(kd, p, slot, pad, nf);''')
# (1) craft: a shard's crafted mark under the lock taken before paying
P.rep(r'''  java.util.ArrayList kept = new java.util.ArrayList();   // fix (critic shards03): stacks with data taken (a stamped Soul Orb) = exact refunds
  long[] bag = new long[ids.length];
  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags; a short take = everything back already''',
      r'''  boolean lk = false;
  if (sk >= 0) { @PKG@.ShStore.LOCK.lock(); lk = true; }   // 0.4.13 review: a shard = the crafted mark + its undo under the lock taken BEFORE paying (busy = nothing taken)
  try {
  java.util.ArrayList kept = new java.util.ArrayList();   // fix (critic shards03): stacks with data taken (a stamped Soul Orb) = exact refunds
  long[] bag = new long[ids.length];
  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags; a short take = everything back already''')
P.rep(r'''  if (paid) refundPaid(u, cs, ids, took, bag, kept);   // 0.4.12 (a failed payInvBags gave everything back already)
  return "-The items or coins could not be taken - everything is back.";
}""")''', r'''  if (paid) refundPaid(u, cs, ids, took, bag, kept);   // 0.4.12 (a failed payInvBags gave everything back already)
  return "-The items or coins could not be taken - everything is back.";
  } finally { if (lk) @PKG@.ShStore.LOCK.unlock(); }   // 0.4.13 review
}""")''')
# (2) owed / owedXp: a busy lock keeps the credit in memory (signed: what the file still says is corrected by the memory part)
P.rep(r'''M(core, "public static long now() { long t = NOW_TEST; return t > 0L ? t : System.currentTimeMillis(); }")''',
      r'''M(core, r"""
public static void memAdj(String ck, String key, long d, java.util.UUID u) {
  if (d == 0L) return;
  String mk = ck + "|" + key;
  Object o = MEM_OWED.get(mk);
  long nv = (o instanceof Long ? ((Long) o).longValue() : 0L) + d;
  if (nv == 0L) MEM_OWED.remove(mk); else MEM_OWED.put(mk, Long.valueOf(nv));
  @PKG@.ShStore.log(u + " " + ck + " " + key + " " + d + " KEPT IN MEMORY (shard data busy) - settled on the next Collect");
}""")   # 0.4.13 review: the busy-lock twin of memKeep (signed: the file part it could not rewrite is corrected here)
M(core, "public static long now() { long t = NOW_TEST; return t > 0L ? t : System.currentTimeMillis(); }")''')
for _ret, _nm in (("return 0L;", "owed"), ("return -1L;", "owedXp")):
    _s = P.s.index("public static long %s(java.util.UUID u, String " % _nm)
    _e = P.s.index('}""")\n', _s)
    _b = P.s[_s:_e]
    _n = _b.replace("  java.util.Properties q = @PKG@.ShStore.get(ck);\n",
                    "  java.util.Properties q;\n  try { q = @PKG@.ShStore.get(ck); } catch (@PKG@.ShBusy b0) { q = null; }   // 0.4.13 review: a busy first load = this credit waits in memory\n", 1)
    _n = _n.replace("  if (q != null) { @PKG@.ShStore.LOCK.lock(); try { due += @PKG@.ShStore.lng(q, key, 0L); } finally { @PKG@.ShStore.LOCK.unlock(); } }\n  if (due <= 0L) %s\n" % _ret,
                    "  long fh = 0L;\n"
                    "  if (q != null) {\n"
                    "    try { @PKG@.ShStore.LOCK.lock(); } catch (@PKG@.ShBusy b1) { memAdj(ck, key, due, u); return due > 0L ? due : %s; }   // 0.4.13 review: busy = all of it waits\n"
                    "    try { fh = @PKG@.ShStore.lng(q, key, 0L); } finally { @PKG@.ShStore.LOCK.unlock(); }\n"
                    "  }\n"
                    "  due += fh;\n"
                    "  if (due <= 0L) { memAdj(ck, key, due - fh, u); %s }\n" % (_ret[7:-1], _ret), 1)
    _n = _n.replace("  if (q != null) {\n    @PKG@.ShStore.LOCK.lock(); try {\n      long had",
                    "  boolean lk = false;\n"
                    "  if (q != null) { try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b2) { memAdj(ck, key, left - fh, u); } }   // 0.4.13 review: paid, the file not rewritten = memory corrects it\n"
                    "  if (lk) {\n    try {\n      long had", 1)
    assert _n.count("ShBusy") == 3 and _n.count("memAdj(") == 3, (_nm, _n.count("ShBusy"), _n.count("memAdj("))
    P.rep(_b, _n)
# (4) ShStore.get: migrate under the lock taken before the cache sees the profile
P.rep(r'''  Object prev = CACHE.putIfAbsent(k, p);
  if (prev != null) return (java.util.Properties) prev;
  migrate(k, p);   // 0.4: the 9.8 forms migration, once per profile file (marker forms=1)
  migrate2(k, p);   // 0.4.8: Automation grandfathered, 0.4.6's extra islands -> the next tiers, Mining caves (marker map.done=1)
  return p;''', r'''  LOCK.lock(); try {   // 0.4.13 review: a busy lock = ShBusy BEFORE the cache sees it (the next get loads + migrates again; it was: cached unmigrated)
    Object prev = CACHE.putIfAbsent(k, p);
    if (prev != null) return (java.util.Properties) prev;
    migrate(k, p);   // 0.4: the 9.8 forms migration, once per profile file (marker forms=1)
    migrate2(k, p);   // 0.4.8: Automation grandfathered, 0.4.6's extra islands -> the next tiers, Mining caves (marker map.done=1)
  } finally { LOCK.unlock(); }
  return p;''')
# (5) grow0: the re-lock tracks whether the lock is held
_s = P.s.index("public static String grow0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {")
_e = P.s.index('}""")\n', _s)
_b = P.s[_s:_e]
_n = _b.replace("  String res;\n  @PKG@.ShStore.LOCK.lock(); try {\n", "  String res;\n  boolean held = false;   // 0.4.13 review: a busy re-lock below never ends in an IllegalMonitorStateException\n  @PKG@.ShStore.LOCK.lock(); held = true; try {\n", 1)
_n = _n.replace("      @PKG@.ShStore.LOCK.unlock();\n      try { ct = @PKG@.ShPay.collTier(u, @PKG@.ShKind.COLL[kd]); } finally { @PKG@.ShStore.LOCK.lock(); }\n",
                "      held = false;\n      @PKG@.ShStore.LOCK.unlock();\n      try { ct = @PKG@.ShPay.collTier(u, @PKG@.ShKind.COLL[kd]); } finally { @PKG@.ShStore.LOCK.lock(); held = true; }\n", 1)
_n = _n.replace("  } finally { @PKG@.ShStore.LOCK.unlock(); }\n  @PKG@.ShWorld2.repaint(k, kd);\n  return res;", "  } finally { if (held) @PKG@.ShStore.LOCK.unlock(); }\n  @PKG@.ShWorld2.repaint(k, kd);\n  return res;", 1)
assert _n.count("held") == 5, _n.count("held")
P.rep(_b, _n)
# (5) ShPlace: a busy unplace re-queues the check (it was: dropped from PENDING, the record kept without its block)
P.rep(r'''chk = mk("ShCheck", None, ("java.lang.Runnable",))''', r'''M(place, r"""
public static boolean undo(String k, Object[] a, long now) {
  String wn = (String) a[0];
  try {
    if (unplace(ownerOfKey(k), kindOf(a), wn + "|" + a[1] + "|" + a[2] + "|" + a[3])) told(a, false);
    return true;
  } catch (@PKG@.ShBusy b) { again(k, a, now); return false; }
}""")   # 0.4.13 review: unplace, or (busy lock) checked again a second later
chk = mk("ShCheck", None, ("java.lang.Runnable",))''')
P.rep(r'''    if (id.indexOf(@PKG@.ShKind.SHARD[kd]) < 0) { if (@PKG@.ShPlace.unplace(@PKG@.ShPlace.ownerOfKey(this.k), kd, wn + "|" + x + "|" + y + "|" + z)) @PKG@.ShPlace.told(this.a, false); }''',
      r'''    if (id.indexOf(@PKG@.ShKind.SHARD[kd]) < 0) @PKG@.ShPlace.undo(this.k, this.a, System.currentTimeMillis());   // 0.4.13 review: busy = checked again''')
P.rep(r'''      if (!Boolean.TRUE.equals(bt)) { if (unplace(ownerOfKey(k), kindOf(a), wn + "|" + x + "|" + y + "|" + z)) told(a, false); undone++; }''',
      r'''      if (!Boolean.TRUE.equals(bt)) { if (undo(k, a, now)) undone++; }   // 0.4.13 review: busy = checked again''')
# (5) ShLv20.grant: one lock hold from the record through the give and its undo
_s = P.s.index("public static String grant(java.util.UUID u, String k, int kd, @IC@[] cs) {")
_e = P.s.index('}""")\n', _s)
_b = P.s[_s:_e]
_n = _b.replace("  String hadC = null;\n  @PKG@.ShStore.LOCK.lock(); try {\n", "  String hadC = null;\n  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.13 review: held through the give + its undo (the undo can never meet a busy lock)\n", 1)
_n = _n.replace("  } finally { @PKG@.ShStore.LOCK.unlock(); }\n  if (@PKG@.ShInv.give(cs, id, 1L) >= 1L) {\n", "  if (@PKG@.ShInv.give(cs, id, 1L) >= 1L) {\n", 1)
assert _n.endswith("  return \"~Your \" + nm + \" Shard (reward for \" + how(kd) + \") is waiting - make room in your inventory for it.\";\n")
_n = _n + "  } finally { @PKG@.ShStore.LOCK.unlock(); }\n"
assert _n.count("LOCK.unlock()") == _b.count("LOCK.unlock()")
P.rep(_b, _n)
# (5) placeHand: the aura after a placement is cosmetic
P.rep(r'''  if (r.startsWith("+")) {   // its range for a moment (only this player)
    int s2 = @PKG@.ShCfg.AURA_SEC < 10 ? 10 : @PKG@.ShCfg.AURA_SEC;
    int n = @PKG@.ShTotem.entries(kd, p, sp[0]).length - 1;
    if (n >= 0) @PKG@.ShCore.auraSet(u, k, kd, sp[0], n, System.currentTimeMillis() + 1000L * (long) s2);
  }''', r'''  if (r.startsWith("+")) {   // its range for a moment (only this player)
    try {   // 0.4.13 review: cosmetic - a busy lock here never turns the placement into a "busy" answer
      int s2 = @PKG@.ShCfg.AURA_SEC < 10 ? 10 : @PKG@.ShCfg.AURA_SEC;
      int n;
      @PKG@.ShStore.LOCK.lock(); try { n = @PKG@.ShTotem.entries(kd, p, sp[0]).length - 1; } finally { @PKG@.ShStore.LOCK.unlock(); }
      if (n >= 0) @PKG@.ShCore.auraSet(u, k, kd, sp[0], n, System.currentTimeMillis() + 1000L * (long) s2);
    } catch (Throwable t) { }
  }''')
# (5) ShTick: the regrow timestamp only after the mask (a busy lock = tried again next second, the other worlds still tick)
P.rep(r'''        LAST_REGROW.put(nm, Long.valueOf(now));
        String ow = @PKG@.ShWorlds.ownerOf(nm);
        int mk = mask(nm, @PKG@.ShStore.get(ow));''', r'''        String ow = @PKG@.ShWorlds.ownerOf(nm);
        int mk;
        try { mk = mask(nm, @PKG@.ShStore.get(ow)); } catch (@PKG@.ShBusy b) { continue; }   // 0.4.13 review: busy = next second
        LAST_REGROW.put(nm, Long.valueOf(now));''')
# ==SAFE END==
P.rep('''ALLC = [cfg, smig, smig45, smig46, smig48, smig49, st, knd, isl48, lv, tot, tfn, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, rng, sweep,''',
      '''ALLC = [busyc, lockc, thrc, aura, clr] + [cfg, smig, smig45, smig46, smig48, smig49, st, knd, isl48, lv, tot, tfn, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, rng, sweep,''')   # 0.4.13: + ShBusy, ShLock, ShThreads, ShAura, ShClear

# ---------------------------------------------------------------------------------------------------- 5. the ready line
P.rep('''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.12: every shard''',
      '''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.13: the totem page (cards, seeds here, modifiers explained, a per-player range aura) + the Totem Bench as a vanilla bench (categories, recipe grid, upgrade at the side) + totem poles placed by hand anywhere on an island + a timed data lock (a world thread never waits on it) on our own tick thread; 0.4.12: every shard''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
_k = P.s.index
assert _k("aura = mk(\"ShAura\"") < _k("Object rc = @PKG@.ShCore.RANGE.get(nm);"), "0.4.13: ShAura before the tick that makes it"
assert _k("lockc = mk(\"ShLock\"") < _k("new @PKG@.ShLock()") and _k("public void buildBusy(") < _k("public void build(@REF@") and _k("public static int[] posOf(") < _k("public static int[] spotOf(")
assert _k("public static void auraClose(") < _k("public void onDismiss(") and _k("public void fillTotemPage(") < _k("public void build(@REF@")
assert _k("public int[] catList(") < _k("public void fillBenchGrid(") < _k("public void fillBench(String k") < _k("public String actBench(")
P.finish()
