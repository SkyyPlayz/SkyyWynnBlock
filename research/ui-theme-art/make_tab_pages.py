"""SkyWynn full UI redesign - compacted top tabs + one-screen tab pages, concept art (2026-11-14). Skyglass theme / Sky Azure accent.

Skyy's words: docs/answered/ui.md 2026-11-14 "FULL UI REDESIGN, ONE SCREEN PER TAB". README: research/ui-theme-art/README.md
("Full UI redesign: fewer tabs, one screen each"). Today's tabs: research/Inventory-Screen-Plan.md section 3, research/Hubs-Spec.md 1.2.

Writes, next to this file (1920 x 1080):
  tab-plan.png    the compacted top tab list (12 -> 7): one card per tab - what it holds and which old menus fold in
  pets-page.png   the PETS tab as ONE screen: pet + mount slots, your pets grid, selected pet, fusing, hatchery, eggs (craft + upgrade)

Deterministic (no randomness, no timestamps): two runs give the same bytes. Imports the kit from make_ui_theme.py (its pictures stay
byte-identical) and a few helpers from make_skill_pages.py. Pictures: only our own committed icons (art/, research/cloud/*-art/).
Run: PYTHONPATH=<tools/dev/scratch/pil> python research/ui-theme-art/make_tab_pages.py [file.png ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import ImageDraw  # noqa: E402
import make_ui_theme as K  # noqa: E402
from make_ui_theme import (PAL, A, rgb, mix, font, tw, text, rich, paste_icon, put, ss_glyph, grad_fill, outline, hline,  # noqa: E402
                           taper_line, glow, panel, button, slot, bar, level_pill, chip, row, search_box, scrollbar,
                           g_diamond, g_coin, g_check, g_x, g_chev, g_plus, g_sword, g_shield, g_heart, g_envelope, bg_world,
                           window_frame, stacked_tab, I_WARP, I_HUB, I_PET, I_EGG, I_MENU, I_ACC, I_NODE)
from make_skill_pages import g_lock, g_star, footer  # noqa: E402

RAR = dict(K.QUALITY_RARITY)          # pets / eggs use the item quality colours (Style Guide 15)
RAR_TXT = dict((k, mix(v, "#ffffff", 0.35) if k in ("Uncommon", "Rare", "Epic") else v) for k, v in RAR.items())   # readable on dark
I_DRAGON = "art/dragons/Common/Icons/ItemsGenerated/Skyy_PetIcon_Dragon%s.png"

NEW_TABS = [("Inventory", I_HUB % "hubrow_character"), ("Skills", I_HUB % "character_skills"), ("Pets", I_HUB % "character_pets"),
            ("Market", I_HUB % "hubrow_market"), ("World", I_HUB % "hubrow_world"), ("Social", I_HUB % "hubrow_social"),
            ("Settings", I_HUB % "hubrow_settings")]


def window_new(sel_name):
    """The approved window (window_v4) with the NEW compact tab row (7 wider tabs)."""
    K.set_accent("Sky Azure")
    W, H = 1920, 1080
    im = bg_world(W, H, 205)
    WX0, WY0, WX1, WY1 = 138, 12, 1781, 1067
    window_frame(im, (WX0, WY0, WX1, WY1))
    TB0, TB1 = WY0 + 8, WY0 + 62
    grad_fill(im, (WX0 + 5, TB0, WX1 - 5, TB1), "#0a111e", "#0c1525", c=4)
    hline(im, WX0 + 6, WX1 - 6, TB1, PAL["lineHi"])
    taper_line(im, WX0 + 20, WX1 - 20, TB1 + 1, PAL["gold"], 120, 0.8)
    tx = WX0 + 16
    for nm, ic in NEW_TABS:
        stacked_tab(im, (tx, TB0 + 2, tx + 95, TB1 - 1), nm, ic, nm == sel_name)
        tx += 99
    rx = WX1 - 18
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=K.g_x(18, "#d6e4ee"))
    rx -= 48
    button(im, (rx - 40, TB0 + 9, rx, TB0 + 49), "", "secondary", glyph=g_envelope(20, "#c2d1e2"))
    put(im, ss_glyph(18, 18, lambda d, s: d.ellipse((0, 0, 18 * s - 1, 18 * s - 1), fill=rgb(PAL["red"]))), rx - 12, TB0 + 3)
    text(im, (rx - 3, TB0 + 12), "2", font("headb", 13), "#ffffff", "mm", shadow=False)
    rx -= 50
    fv, fk = font("headb", 16), font("head", 13)
    panel(im, (rx - 104, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    paste_icon(im, I_HUB % "storage_bank", rx - 98, TB0 + 17, 24)
    text(im, (rx - 68, TB0 + 21), "BANK", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 68, TB0 + 38), "3.2M", fv, "#e9eef7", "lm")
    rx -= 112
    panel(im, (rx - 128, TB0 + 9, rx, TB0 + 49), inset=True, c=4)
    put(im, g_coin(22), rx - 120, TB0 + 18)
    text(im, (rx - 90, TB0 + 21), "COINS", fk, PAL["dim"], "lm", track=1)
    text(im, (rx - 90, TB0 + 38), "1,245,210", fv, "#ffd76a", "lm")
    return im, (WX0, WY0, WX1, WY1)


def wrap(s, f, w):
    out, line = [], ""
    for word in s.split():
        if line and tw(line + " " + word, f) > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


# ================================================================================================================ tab plan
PLAN = [
    ("Inventory", I_HUB % "hubrow_character", "Your bag + everything you carry or wear",
     ["Inventory grid, hotbar, armor + off-hand", "Crafting (all benches, Furnace, Cooking, Tanning)", "Pocket tabs (bags, Vault)",
      "Charms (Void Charms) + Requip presets", "Teleport row + Right now panel"],
     ["Storage: Pocket", "Storage: Vault", "Requip", "Accessories / Charms", "Smithing: Recipes"]),
    ("Skills", I_HUB % "character_skills", "One page per skill (+ your Class)",
     ["Skill grid: Combat, Mining, Farming, Foraging ... + Class", "Level, next unlock, stats with that gear", "Tool + armor upgrade, reforge, sigils",
      "Collections path + rewards", "Skill tree + the skill's shard"],
     ["Skills", "Trees", "Class", "Upgrade", "Smithing: Gear / Reforge / Identify / Multitool", "Collections", "World: Shards"]),
    ("Pets", I_HUB % "character_pets", "Everything pet on one screen",
     ["Pet slot + Mount slot (Summon)", "Your pets grid with filters", "Selected pet: buffs, level, rebirth", "Fusing, Hatchery, Eggs (craft + upgrade)"],
     ["Pets", "Pets: Eggs", "Pets: Hatchery", "egg recipes from the benches"]),
    ("Market", I_HUB % "hubrow_market", "Buy, sell and your money",
     ["Bazaar (instant buy / sell orders)", "Auction House + your listings", "Merchants + NPC shops", "Bank (coins, interest)"],
     ["Bazaar", "Auctions", "Merchants", "Storage: Bank"]),
    ("World", I_HUB % "hubrow_world", "Where to go and what to do",
     ["Map with warps, islands, zones + danger", "Your island settings", "Quest log + tracked quest", "Explore: discoveries, titles, bestiary / drops codex"],
     ["World: Teleport", "Island", "Explore", "Quests", "Collections: bestiary codex"]),
    ("Social", I_HUB % "hubrow_social", "People + you",
     ["Players online (trade, whisper, invite)", "Party + Guild", "Your profile card: overall level, stats", "Profiles (switch / create)"],
     ["Players", "Party", "Guild", "Character: Stats", "Profiles"]),
    ("Settings", I_HUB % "hubrow_settings", "Unchanged home for options",
     ["Settings", "HUD editor", "Menu layout", "Mods + Server Setup (admin)"],
     ["Settings", "HUD", "Menu layout", "Mods", "Server Setup"]),
]
OLD_TABS = ["Inventory", "Skills", "Class", "Pets", "Collections", "Storage", "Upgrade", "Market", "Quests", "World", "Social", "Settings"]


def make_tab_plan():
    im, (WX0, WY0, WX1, WY1) = window_new("Skills")
    X0, X1 = WX0 + 16, WX1 - 16
    y = 90
    text(im, (X0, y + 14), "TOP TABS:  12  ->  7", font("headb", 26), PAL["title"], "lm", track=2)
    text(im, (X0, y + 44), "Each tab = ONE screen for its topic (like the Mining page).",
         font("body", 16), PAL["dim"], "lm")
    # old row -> new row
    ox = X0 + 760
    text(im, (ox, y + 6), "TODAY", font("head", 13), PAL["dim"], "lm", track=1.5)
    cx = ox + 70
    gone = {"Class", "Collections", "Storage", "Upgrade", "Quests"}
    for nm in OLD_TABS:
        f = font("headc", 13)
        w = tw(nm, f) + 12
        col = "#5d6a7c" if nm in gone else "#a9bad0"
        grad_fill(im, (cx, y - 4, cx + w, y + 16), "#121c2f", "#0e1626", c=3)
        outline(im, (cx, y - 4, cx + w, y + 16), "#2b3d5b" if nm not in gone else "#1e2a3c", c=3)
        text(im, (cx + w // 2, y + 6), nm, f, col, "mm")
        if nm in gone:
            ImageDraw.Draw(im).line([(cx + 4, y + 6), (cx + w - 4, y + 6)], fill=rgb(PAL["red"], 220), width=1)
        cx += w + 4
    text(im, (ox, y + 36), "NEW", font("head", 13), A["hi"], "lm", track=1.5)
    cx = ox + 70
    for nm, _ic, *_ in PLAN:
        f = font("headc", 14)
        w = tw(nm, f) + 18
        grad_fill(im, (cx, y + 25, cx + w, y + 47), mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.8), c=3)
        outline(im, (cx, y + 25, cx + w, y + 47), A["base"], c=3)
        text(im, (cx + w // 2, y + 36), nm, f, "#ffffff", "mm")
        cx += w + 6
    taper_line(im, X0, X1, y + 64, PAL["gold"], 150, 0.85)
    # cards: 4 + 4 (the 8th = "nothing lost")
    cy0 = y + 78
    gap = 12
    cw = (X1 - X0 - 3 * gap) // 4
    ch = (1022 - cy0 - gap) // 2
    for i in range(8):
        cxx = X0 + (i % 4) * (cw + gap)
        cyy = cy0 + (i // 4) * (ch + gap)
        box = (cxx, cyy, cxx + cw - 1, cyy + ch - 1)
        if i == 7:
            panel(im, box, "Nothing lost")
            lines = [("Every old menu has a new home - the full", PAL["row"]), ("old -> new table is in the README.", PAL["row"]),
                     ("", None),
                     ("Gone as TABS (folded in):", PAL["xp"]), ("Class -> Skills", PAL["green"]), ("Collections -> Skills + World", PAL["green"]),
                     ("Storage -> Inventory + Market", PAL["green"]), ("Upgrade -> Skills (each skill page)", PAL["green"]),
                     ("Quests -> World", PAL["green"]), ("", None),
                     ("Commands stay: /pets, /bz, /quests ...", PAL["dim"]), ("open the tab on the right spot.", PAL["dim"])]
            yy = cyy + 46
            for s_, c in lines:
                if s_:
                    text(im, (cxx + 16, yy), s_, font("bodyb" if c in (PAL["xp"], PAL["green"]) else "body", 15), c, "lm")
                yy += 22 if s_ else 10
            continue
        nm, ic, sub, holds, folds = PLAN[i]
        grad_fill(im, box, PAL["panel2"], PAL["panel"], c=6)
        outline(im, box, A["lo"] if nm != "Settings" else PAL["line"], c=6)
        hline(im, cxx + 6, cxx + cw - 7, cyy + 1, "#ffffff", 14)
        ibox = (cxx + 14, cyy + 14, cxx + 63, cyy + 63)
        grad_fill(im, ibox, mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.85), c=6)
        outline(im, ibox, A["base"], c=6)
        paste_icon(im, ic, cxx + 22, cyy + 22, 34)
        text(im, (cxx + 76, cyy + 30), nm.upper(), font("headb", 21), PAL["title"], "lm", track=1.5)
        text(im, (cxx + 76, cyy + 54), sub, font("body", 14), PAL["dim"], "lm")
        text(im, (cxx + 14, cyy + 88), "ONE SCREEN HOLDS", font("head", 12), PAL["dim"], "lm", track=1.3)
        yy = cyy + 110
        for h_ in holds:
            for k, ln in enumerate(wrap(h_, font("body", 16), cw - 48)):
                if k == 0:
                    put(im, g_diamond(9, A["hi"]), cxx + 16, yy - 4)
                text(im, (cxx + 32, yy), ln, font("body", 16), PAL["row"], "lm")
                yy += 24
            yy += 4
        yy = cyy + ch - 86
        taper_line(im, cxx + 14, cxx + cw - 14, yy - 12, PAL["gold"], 120, 0.7)
        text(im, (cxx + 14, yy), "FOLDS IN", font("head", 12), PAL["xp"], "lm", track=1.3)
        fx, fy = cxx + 14, yy + 12
        for fo in folds:
            f = font("bodyb", 13)
            w = tw(fo, f) + 14
            if fx + w > cxx + cw - 12:
                fx, fy = cxx + 14, fy + 25
            grad_fill(im, (fx, fy, fx + w, fy + 20), "#2b2212", "#1a140a", c=4)
            outline(im, (fx, fy, fx + w, fy + 20), PAL["goldLo"], c=4)
            text(im, (fx + w // 2, fy + 10), fo, f, PAL["goldHi"], "mm", shadow=False)
            fx += w + 6
    footer(im, [("1-7", "Jump to a tab"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ pets page
# (name, icon, rarity, level, roles, skill)  - real SkyyPets kinds (SkyyPets build scripts KINDS; dragons = Fighter + Mount)
PETS = [("Wolf", I_PET % "Wolf", "Legendary", 37, "F", "Combat"), ("Plain Dragon", I_DRAGON % "Plain", "Epic", 24, "FM", "Combat"),
        ("Horse", I_PET % "Horse", "Rare", 22, "M", "Exploration"), ("Rabbit", I_PET % "Rabbit", "Mythic", 8, "B", "Farming"),
        ("Goat", I_PET % "Goat", "Epic", 30, "B", "Mining"), ("Warthog", I_PET % "Warthog", "Rare", 18, "B", "Mining"),
        ("Bear", I_PET % "Bear", "Rare", 25, "B", "Foraging"), ("Hawk", I_PET % "Hawk", "Epic", 16, "F", "Combat"),
        ("Boar", I_PET % "Boar", "Uncommon", 20, "F", "Combat"), ("Turkey", I_PET % "Turkey", "Uncommon", 14, "B", "Foraging"),
        ("Camel", I_PET % "Camel", "Rare", 9, "M", "Exploration"), ("Ram", I_PET % "Ram", "Epic", 11, "B", "Combat"),
        ("Wolf", I_PET % "Wolf", "Rare", 12, "F", "Combat"), ("Wolf", I_PET % "Wolf", "Rare", 6, "F", "Combat"),
        ("Wolf", I_PET % "Wolf", "Rare", 3, "F", "Combat"), ("Chicken", I_PET % "Chicken", "Common", 33, "B", "Farming"),
        ("Mouflon", I_PET % "Mouflon", "Epic", 7, "B", "Combat"), ("Skrill", I_PET % "Skrill", "Epic", 5, "F", "Combat"),
        ("Tusker", I_PET % "Tusker", "Rare", 19, "B", "Combat"), ("Fire Dragon", I_DRAGON % "Fire", "Legendary", 2, "FM", "Combat")]


def role_badge(im, x, y, roles):
    """small role marks in a cell corner: sword = Fighter, horseshoe-like U = Mount"""
    for r in roles:
        if r == "B":
            continue
        grad_fill(im, (x, y, x + 17, y + 17), "#0a111e", "#0a111e", c=3)
        outline(im, (x, y, x + 17, y + 17), "#ff8a7a" if r == "F" else "#7cd0ff", c=3)
        if r == "F":
            put(im, g_sword(13, "#ff8a7a"), x + 2, y + 2)
        else:
            put(im, ss_glyph(13, 13, lambda d, s: d.arc((s, s, 12 * s, 14 * s), 180, 360, fill=rgb("#7cd0ff"), width=int(2.4 * s))), x + 2, y + 4)
        x += 19


def kind_tag(im, x, y, label, col):
    f = font("headb", 12)
    w = tw(label, f, 1) + 14
    grad_fill(im, (x, y, x + w, y + 20), mix(col, "#0c1422", 0.75), mix(col, "#0c1422", 0.85), c=4)
    outline(im, (x, y, x + w, y + 20), col, c=4)
    text(im, (x + w // 2, y + 10), label, f, col, "mm", shadow=False, track=1)
    return w


def pet_slot_card(im, box, cap, pet, sub, btn=None, locked=False):
    x0, y0, x1, y1 = box
    grad_fill(im, box, "#152138", "#111b2d", c=6)
    outline(im, box, A["base"] if not locked else PAL["line"], c=6)
    text(im, (x0 + 12, y0 + 14), cap, font("head", 12), A["hi"], "lm", track=1.3)
    nm, ic, rr, lv, roles, _sk = pet
    slot(im, x0 + 12, y0 + 28, "empty", RAR[rr], ic, size=64)
    text(im, (x0 + 86, y0 + 42), "%s %s" % (rr, nm), font("headb", 16), RAR_TXT[rr], "lm")
    text(im, (x0 + 86, y0 + 62), "Lv %d" % lv, font("headb", 14), PAL["xp"], "lm")
    text(im, (x0 + 86, y0 + 82), sub, font("body", 13), PAL["dim"], "lm")
    if btn:
        button(im, (x1 - 100, y0 + 70, x1 - 12, y0 + 98), btn, "primary", fsize=14)


def make_pets():
    im, (WX0, WY0, WX1, WY1) = window_new("Pets")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    LX1 = X0 + 600
    MX0, MX1 = LX1 + 12, LX1 + 12 + 500
    RX0 = MX1 + 12
    # ---------------- left: slots + your pets
    panel(im, (X0, Y0, LX1, Y0 + 152), "Equipped")
    pet_slot_card(im, (X0 + 12, Y0 + 34, X0 + 292, Y0 + 142), "PET SLOT  -  follows you", PETS[0], "Fights + full buffs")
    pet_slot_card(im, (X0 + 304, Y0 + 34, LX1 - 12, Y0 + 142), "MOUNT SLOT  -  ride", PETS[1], "Summon = ride", btn="Summon")
    gy0 = Y0 + 162
    panel(im, (X0, gy0, LX1, Y1), "Your pets")
    text(im, (LX1 - 14, gy0 + 18), "20 / 120", font("headb", 14), PAL["xp"], "rm")
    search_box(im, (X0 + 14, gy0 + 36, X0 + 200, gy0 + 66), "Search pets")
    cx = X0 + 210
    for i, lab in enumerate(["All", "Bonus", "Fighter", "Mount"]):
        cx += chip(im, cx, gy0 + 35, lab, i == 0, h=31, fsize=14) + 6
    cx = X0 + 14
    for i, (lab, ic) in enumerate([("Combat", I_WARP % "Combat"), ("Mining", I_WARP % "Mining"), ("Farming", I_WARP % "Farming"),
                                   ("Foraging", I_WARP % "Foraging"), ("Exploration", I_NODE % "Exploration_B1R1a")]):
        cx += chip(im, cx, gy0 + 74, lab, False, h=30, icon_rel=ic, fsize=13) + 5
    text(im, (LX1 - 14, gy0 + 51), "Sort: rarity", font("bodyb", 13), A["hi"], "rm")
    sx0, sy0 = X0 + 14, gy0 + 116
    cols = 7
    pitch = 80
    for i in range(42):
        x = sx0 + (i % cols) * pitch
        y = sy0 + (i // cols) * (pitch + 6)
        if i < len(PETS):
            nm, ic, rr, lv, roles, _sk = PETS[i]
            st = "selected" if i == 0 else ("hover" if i == 12 else "empty")
            slot(im, x, y, st, RAR[rr], ic, size=74)
            text(im, (x + 70, y + 70), "Lv %d" % lv, font("headb", 13), "#ffffff", "rs")
            role_badge(im, x + 4, y + 4, roles)
            if i in (0, 1):
                put(im, g_check(14, PAL["green"]), x + 56, y + 4)
        else:
            slot(im, x, y, "empty", None, None, size=74)
    text(im, (X0 + 14, Y1 - 46), "Click: select   Shift-click: pet slot   Right-click: mount slot", font("bodyb", 14), PAL["action"], "lm")
    rich(im, X0 + 14, Y1 - 22, [("Marks:  ", font("body", 14), PAL["dim"]), ("sword", font("bodyb", 14), "#ff8a7a"), (" Fighter   ", font("body", 14), PAL["row"]),
                                ("U", font("bodyb", 14), "#7cd0ff"), (" Mount   ", font("body", 14), PAL["row"]),
                                ("none", font("bodyb", 14), PAL["text"]), (" Bonus (stats only)", font("body", 14), PAL["row"])])
    # ---------------- middle: selected pet + fusing
    dy1 = Y0 + 600
    panel(im, (MX0, Y0, MX1, dy1), "Selected pet")
    nm, ic, rr, lv, roles, sk = PETS[0]
    slot(im, MX0 + 14, Y0 + 36, "empty", RAR[rr], ic, size=96)
    paste_icon(im, ic, MX0 + 22, Y0 + 44, 80)
    text(im, (MX0 + 124, Y0 + 52), "Legendary Wolf", font("headb", 24), RAR_TXT[rr], "lm")
    x = MX0 + 124
    x += kind_tag(im, x, Y0 + 70, "FIGHTER", "#ff8a7a") + 6
    x += kind_tag(im, x, Y0 + 70, "COMBAT PET", "#ffb070") + 6
    kind_tag(im, x, Y0 + 70, "ZONE 3", "#9fb0c6")
    level_pill(im, MX0 + 124, Y0 + 100, "Lv 37 / 50")
    bar(im, (MX0 + 212, Y0 + 106, MX1 - 16, Y0 + 116), 0.62, "xp")
    text(im, (MX1 - 16, Y0 + 128), "41,200 / 66,000 pet XP", font("body", 13), PAL["dim"], "rm")
    yy = Y0 + 152

    def sec(title, ys):
        text(im, (MX0 + 16, ys), title, font("head", 13), PAL["dim"], "lm", track=1.5)
        taper_line(im, MX0 + 16 + tw(title, font("head", 13), 1.5) + 8, MX1 - 16, ys, PAL["gold"], 110, 0.7)
    sec("BUFFS NOW  (rarity x1.4)", yy)
    yy += 24
    for v, n_ in (("+24", "Damage"), ("+6%", "Crit Chance"), ("+40", "Health"), ("+3%", "Combat XP")):
        text(im, (MX0 + 20, yy), v, font("bold", 15), PAL["green"], "lm")
        text(im, (MX0 + 76, yy), n_, font("body", 15), PAL["row"], "lm")
        yy += 22
    yy += 6
    sec("WHERE IT WORKS", yy)
    yy += 24
    for ok, s_ in ((True, "Pet slot: follows you and FIGHTS, full buffs"), (False, "Mount slot: not a mount (no riding)"),
                   (True, "Your attacks pass through it")):
        put(im, g_check(14, PAL["green"]) if ok else g_x(14, PAL["red"], 2.2), MX0 + 20, yy - 7)
        text(im, (MX0 + 42, yy), s_, font("body", 15), PAL["row"], "lm")
        yy += 22
    yy += 6
    sec("PROGRESS", yy)
    yy += 24
    rich(im, MX0 + 20, yy, [("Rebirths  ", font("body", 15), PAL["dim"]), ("0", font("bold", 15), "#ffffff"),
                            ("    at Lv 50: rebirth, +10 max level", font("body", 15), PAL["row"])])
    yy += 22
    rich(im, MX0 + 20, yy, [("Next rarity  ", font("body", 15), PAL["dim"]), ("Mythic only from eggs", font("bodyb", 15), RAR["Mythic"])])
    yy += 30
    sec("AT LV 50", yy)
    yy += 24
    rich(im, MX0 + 20, yy, [("+32", font("bold", 15), PAL["green"]), (" Damage    ", font("body", 15), PAL["row"]),
                            ("+8%", font("bold", 15), PAL["green"]), (" Crit Chance    ", font("body", 15), PAL["row"]),
                            ("+54", font("bold", 15), PAL["green"]), (" Health", font("body", 15), PAL["row"])])
    by = dy1 - 52
    button(im, (MX0 + 16, by, MX0 + 166, by + 34), "In pet slot", "secondary", "disabled", fsize=15)
    button(im, (MX0 + 176, by, MX0 + 326, by + 34), "Mount slot", "secondary", "disabled", fsize=15)
    button(im, (MX0 + 336, by, MX1 - 16, by + 34), "Rebirth (Lv 50)", "primary", "disabled", fsize=15)
    # fusing
    fy0 = dy1 + 10
    panel(im, (MX0, fy0, MX1, Y1), "Pet fusing")
    text(im, (MX1 - 14, fy0 + 18), "4 same pets -> next rarity", font("body", 13), PAL["dim"], "rm")
    fx = MX0 + 16
    for k in range(4):
        if k < 3:
            p = PETS[12 + k]
            slot(im, fx, fy0 + 44, "empty", RAR["Rare"], p[1], size=64)
            text(im, (fx + 60, fy0 + 104), "Lv %d" % p[3], font("headb", 12), "#ffffff", "rs")
        else:
            slot(im, fx, fy0 + 44, "empty", None, None, size=64)
            put(im, g_plus(20, "#3a4e6e"), fx + 22, fy0 + 66)
        fx += 70
    put(im, K.g_tri(20, PAL["goldHi"]), fx + 4, fy0 + 66)
    rx_ = fx + 32
    slot(im, rx_, fy0 + 38, "empty", RAR["Epic"], I_PET % "Wolf", size=76)
    glow(im, (rx_, fy0 + 38, rx_ + 75, fy0 + 113), RAR["Epic"], 6, 120, 4, 2)
    text(im, (rx_ + 38, fy0 + 126), "Epic Wolf", font("headb", 14), RAR_TXT["Epic"], "mm")
    text(im, (MX0 + 16, fy0 + 140), "3 / 4 Rare Wolf", font("bodyb", 15), PAL["row"], "lm")
    text(im, (MX0 + 16, fy0 + 162), "Keeps the highest level (Lv 12).", font("body", 14), PAL["dim"], "lm")
    text(im, (MX0 + 16, fy0 + 184), "Needs 1 more Rare Wolf (need 1)", font("bodyb", 14), PAL["red"], "lm")
    text(im, (MX0 + 16, fy0 + 206), "Mythic cannot be fused - eggs only.", font("body", 14), PAL["dim"], "lm")
    button(im, (MX1 - 150, Y1 - 50, MX1 - 16, Y1 - 16), "Fuse", "primary", "disabled", fsize=16)
    # ---------------- right: hatchery + eggs
    hy1 = Y0 + 432
    panel(im, (RX0, Y0, X1, hy1), "Hatchery")
    text(im, (X1 - 14, Y0 + 18), "4 / 6 slots", font("headb", 14), PAL["xp"], "rm")
    hs = [("Mining_Common", "Common Mining Egg", None, "Ready!"), ("Combat_Rare", "Rare Combat Egg", 0.35, "1h 12m left"),
          ("Farming_Uncommon", "Uncommon Farming Egg", 0.8, "6m left"), (None, "Empty - drop an egg here", None, ""),
          ("lock", "Beastmastery tree: +1 slot", None, ""), ("lock", "Beastmastery tree: +1 slot", None, "")]
    hy = Y0 + 38
    for eg, lab, frac, t in hs:
        row(im, (RX0 + 10, hy, X1 - 10, hy + 56), "normal" if eg not in (None, "lock") else "hover")
        if eg and eg != "lock":
            rr = eg.split("_")[1]
            slot(im, RX0 + 16, hy + 4, "empty", RAR[rr], I_EGG % eg, size=48)
            text(im, (RX0 + 74, hy + 16), lab, font("bodyb", 15), RAR_TXT[rr], "lm")
            if frac is None:
                text(im, (RX0 + 74, hy + 38), t, font("headb", 14), PAL["green"], "lm")
                button(im, (X1 - 110, hy + 12, X1 - 20, hy + 44), "Hatch", "green", fsize=15)
            else:
                bar(im, (RX0 + 74, hy + 34, X1 - 120, hy + 42), frac, "accent")
                text(im, (X1 - 20, hy + 38), t, font("bodyb", 13), PAL["text"], "rm")
        elif eg is None:
            slot(im, RX0 + 16, hy + 4, "empty", None, None, size=48)
            put(im, g_plus(16, "#3a4e6e"), RX0 + 32, hy + 20)
            text(im, (RX0 + 74, hy + 28), lab, font("body", 14), PAL["dim"], "lm")
        else:
            slot(im, RX0 + 16, hy + 4, "empty", None, None, size=48)
            put(im, g_lock(20, "#7f93a6"), RX0 + 30, hy + 18)
            text(im, (RX0 + 74, hy + 28), lab, font("body", 14), "#5d6a7c", "lm")
        hy += 60
    text(im, (RX0 + 14, hy1 - 14), "Hatch = 2 rolls: which pet, then rarity. Time by egg rarity.", font("body", 13), PAL["dim"], "lm")
    # eggs
    ey0 = hy1 + 10
    panel(im, (RX0, ey0, X1, Y1), "Eggs")
    text(im, (X1 - 14, ey0 + 18), "craft Common, upgrade the rest", font("body", 13), PAL["dim"], "rm")
    ex = RX0 + 14
    eggs = [("Combat_Common", 2), ("Mining_Common", 1), ("Mining_Uncommon", 1), ("Foraging_Common", 3), ("Exploration_Rare", 1)]
    text(im, (RX0 + 14, ey0 + 44), "YOUR EGGS", font("head", 12), PAL["dim"], "lm", track=1.3)
    for i, (eg, n) in enumerate(eggs):
        rr = eg.split("_")[1]
        slot(im, ex, ey0 + 56, "selected" if i == 1 else "empty", RAR[rr], I_EGG % eg, size=56)
        text(im, (ex + 52, ey0 + 108), str(n), font("headb", 13), "#ffffff", "rs")
        ex += 62
    yy = ey0 + 136
    text(im, (RX0 + 14, yy), "CRAFT  (Common eggs only)", font("head", 12), PAL["dim"], "lm", track=1.3)
    yy += 14
    for eg, nm_, cost, need in (("Mining_Common", "Common Mining Egg", "64 Copper Ore", 0), ("Farming_Common", "Common Farming Egg", "64 Wheat", 22),
                                ("Combat_Common", "Common Combat Egg", "128 Bone Fragments", 106)):
        row(im, (RX0 + 10, yy, X1 - 10, yy + 44), "normal")
        paste_icon(im, I_EGG % eg, RX0 + 16, yy + 6, 32)
        text(im, (RX0 + 56, yy + 14), nm_, font("bodyb", 14), "#ffffff", "lm")
        rich(im, RX0 + 56, yy + 32, [("1 Egg + " + cost, font("body", 13), PAL["green"] if not need else PAL["red"]),
                                     (("  (need %d)" % need) if need else "", font("bodyb", 13), PAL["red"])])
        button(im, (X1 - 96, yy + 8, X1 - 18, yy + 36), "Craft", "primary", "normal" if not need else "disabled", fsize=13)
        yy += 48
    yy += 8
    text(im, (RX0 + 14, yy), "UPGRADE THE SELECTED EGG", font("head", 12), PAL["dim"], "lm", track=1.3)
    yy += 14
    row(im, (RX0 + 10, yy, X1 - 10, yy + 94), "selected")
    paste_icon(im, I_EGG % "Mining_Common", RX0 + 20, yy + 10, 40)
    put(im, K.g_tri(14, PAL["goldHi"]), RX0 + 66, yy + 22)
    paste_icon(im, I_EGG % "Mining_Uncommon", RX0 + 86, yy + 10, 40)
    text(im, (RX0 + 136, yy + 20), "Uncommon Mining Egg", font("bodyb", 15), RAR_TXT["Uncommon"], "lm")
    text(im, (RX0 + 136, yy + 40), "better pet odds", font("body", 13), PAL["dim"], "lm")
    rich(im, RX0 + 20, yy + 66, [("Common Mining Egg + 32 Iron Ore + 8 Enchanted Copper", font("body", 13), PAL["green"])])
    rich(im, RX0 + 20, yy + 84, [("+ 500 coins", font("body", 13), PAL["green"])])
    button(im, (X1 - 112, yy + 54, X1 - 18, yy + 86), "Upgrade", "primary", fsize=14)
    footer(im, [("LMB", "Select"), ("Shift+LMB", "Pet slot"), ("RMB", "Mount slot"), ("Drag", "Egg to hatchery"), ("Tab / Esc", "Close")])
    return im


def main():
    out = {"tab-plan.png": make_tab_plan, "pets-page.png": make_pets}
    only = sys.argv[1:]
    for fn, maker in out.items():
        if only and fn not in only:
            continue
        im = maker()
        im.save(os.path.join(HERE, fn), optimize=True)
        print("wrote", fn, im.size)


if __name__ == "__main__":
    main()
