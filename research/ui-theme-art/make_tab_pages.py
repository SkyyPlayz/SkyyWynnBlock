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
from make_ui_theme import px_icon, key_cap  # noqa: E402

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
PLAN_V1 = list(PLAN)
PLAN_V2 = list(PLAN)
PLAN_V2[0] = ("Inventory", I_HUB % "hubrow_character", "Your bag + everything you carry or wear",
              ["Inventory grid, hotbar, armor + off-hand", "Crafting (all benches, Furnace, Cooking, Tanning)", "Pocket tabs (bags, Vault)",
               "Requip + Charms panels open INSIDE it (preset pencil, 'All charms')", "Teleport row + Right now panel"],
              ["Storage: Pocket", "Storage: Vault", "Requip", "Accessories / Void Charms", "Smithing: Recipes"])
PLAN_V2[1] = ("Skills", I_HUB % "character_skills", "One page per skill - Combat = your class",
              ["Skill grid: Combat, Mining, Farming, Foraging ...", "COMBAT page = your class: loadout, abilities, class tree, combat gear",
               "Tool + armor upgrade, reforge, sigils", "Collections path, skill tree, the skill's shard"],
              ["Skills", "Trees", "Class (Combat page)", "Upgrade", "Smithing: Gear / Reforge / Identify / Multitool", "Collections", "World: Shards"])
V2 = True   # v2 (Skyy 11-14 "class is combat."): Class lives on the Combat skill page. False = the kept tab-plan-v1.png.
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
    for nm, _ic, *_ in (PLAN_V2 if V2 else PLAN_V1):
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
                     ("Gone as TABS (folded in):", PAL["xp"]), ("Class -> Skills (Combat page)" if V2 else "Class -> Skills", PAL["green"]), ("Collections -> Skills + World", PAL["green"]),
                     ("Storage -> Inventory + Market", PAL["green"]), ("Upgrade -> Skills (each skill page)", PAL["green"]),
                     ("Quests -> World", PAL["green"]), ("", None),
                     ("Commands stay: /pets, /bz, /quests ...", PAL["dim"]), ("open the tab on the right spot.", PAL["dim"])]
            yy = cyy + 46
            for s_, c in lines:
                if s_:
                    text(im, (cxx + 16, yy), s_, font("bodyb" if c in (PAL["xp"], PAL["green"]) else "body", 15), c, "lm")
                yy += 22 if s_ else 10
            continue
        nm, ic, sub, holds, folds = (PLAN_V2 if V2 else PLAN_V1)[i]
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


# ================================================================================================================ shared bits for the tab pages
I_EMB = K.I_EMB


def head_strip(im, X0, X1, y, icon, title, sub, right=None):
    box = (X0, y, X0 + 47, y + 47)
    grad_fill(im, box, mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.85), c=5)
    outline(im, box, A["base"], c=5)
    paste_icon(im, icon, X0 + 8, y + 8, 32)
    text(im, (X0 + 62, y + 16), title, font("headb", 24), PAL["title"], "lm", track=2)
    text(im, (X0 + 62, y + 38), sub, font("body", 14), PAL["dim"], "lm")


def sub_title(im, x, y, label, x_end, col=None):
    text(im, (x, y), label, font("head", 12), col or PAL["dim"], "lm", track=1.4)
    taper_line(im, x + tw(label, font("head", 12), 1.4) + 8, x_end, y, PAL["gold"], 110, 0.7)


def ico_btn(im, x, y, glyph, w=30):
    button(im, (x, y, x + w - 1, y + 25), "", "secondary", glyph=glyph)


def g_trade(size, col):
    def f(d, s):
        n = size * s
        d.line([(n * 0.15, n * 0.35), (n * 0.8, n * 0.35)], fill=rgb(col), width=int(2 * s))
        d.polygon([(n * 0.8, n * 0.2), (n * 0.95, n * 0.35), (n * 0.8, n * 0.5)], fill=rgb(col))
        d.line([(n * 0.2, n * 0.68), (n * 0.85, n * 0.68)], fill=rgb(col), width=int(2 * s))
        d.polygon([(n * 0.2, n * 0.53), (n * 0.05, n * 0.68), (n * 0.2, n * 0.83)], fill=rgb(col))
    return ss_glyph(size, size, f)


def g_chat(size, col):
    def f(d, s):
        n = size * s
        d.rounded_rectangle((n * 0.08, n * 0.15, n * 0.92, n * 0.68), radius=n * 0.15, outline=rgb(col), width=int(2 * s))
        d.polygon([(n * 0.28, n * 0.66), (n * 0.25, n * 0.9), (n * 0.48, n * 0.66)], fill=rgb(col))
    return ss_glyph(size, size, f)


def g_invite(size, col):
    def f(d, s):
        n = size * s
        d.ellipse((n * 0.2, n * 0.08, n * 0.52, n * 0.4), outline=rgb(col), width=int(2 * s))
        d.arc((n * 0.06, n * 0.45, n * 0.66, n * 1.05), 180, 360, fill=rgb(col), width=int(2 * s))
        d.line([(n * 0.7, n * 0.5), (n * 0.98, n * 0.5)], fill=rgb(col), width=int(2 * s))
        d.line([(n * 0.84, n * 0.36), (n * 0.84, n * 0.64)], fill=rgb(col), width=int(2 * s))
    return ss_glyph(size, size, f)


def dot(im, x, y, col, r=5):
    put(im, ss_glyph(2 * r, 2 * r, lambda d, s: d.ellipse((0, 0, 2 * r * s - 1, 2 * r * s - 1), fill=rgb(col))), x - r, y - r)


# ================================================================================================================ market
BZ_ITEMS = [("px:ore:#e08a4a", "Copper Ore", "T1", "21.4", "19.8", "+2%"), ("px:ore:#b8c4d0", "Iron Ore", "T2", "28.1", "26.0", "-1%"),
            ("px:ore:#7fd07a", "Thorium Ore", "T4", "44.0", "40.5", "+5%"), (K.I_ENCH % "copper-ingot", "Enchanted Copper", "T1", "2,310", "2,150", "+1%"),
            (K.I_ENCH % "iron-ingot", "Enchanted Iron", "T2", "3,020", "2,800", "-3%"), (K.I_ENCH % "cobblestone", "Enchanted Cobblestone", "", "640", "601", "0%"),
            ("px:coal", "Coal", "", "6.2", "5.5", "+1%"), (K.I_ENCH % "silver-ingot", "Enchanted Silver", "", "9,800", "9,100", "+4%")]
BZ_CATS = [("Mining", I_WARP % "Mining"), ("Foraging", I_WARP % "Foraging"), ("Farming", I_WARP % "Farming"), ("Combat", I_WARP % "Combat"),
           ("Fishing", I_WARP % "Fishing"), ("Cooking", I_NODE % "Cooking_B1R1a"), ("Alchemy", I_NODE % "Alchemy_B1R1a"),
           ("Pets + eggs", I_HUB % "character_pets"), ("Charms", K.I_VOID)]


def make_market():
    im, (WX0, WY0, WX1, WY1) = window_new("Market")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    # ---- left rail: search + bazaar categories + jump links (no sub-tabs: everything below is on this screen)
    LX1 = X0 + 220
    panel(im, (X0, Y0, LX1, 610), "Bazaar")
    search_box(im, (X0 + 12, Y0 + 36, LX1 - 12, Y0 + 66), "Search all items")
    yy = Y0 + 78
    for i, (nm, ic) in enumerate(BZ_CATS):
        row(im, (X0 + 10, yy, LX1 - 10, yy + 40), "selected" if i == 0 else "normal")
        paste_icon(im, ic, X0 + 20, yy + 8, 24, 1.0 if i == 0 else 0.8)
        text(im, (X0 + 52, yy + 20), nm, font("headb", 15), "#ffffff" if i == 0 else PAL["row"], "lm")
        yy += 44
    text(im, (X0 + 14, yy + 14), "Prices update live.", font("body", 13), PAL["dim"], "lm")
    # ---- centre: bazaar list
    CX0, CX1 = LX1 + 12, LX1 + 12 + 560
    panel(im, (CX0, Y0, CX1, 610), "Mining")
    text(im, (CX1 - 14, Y0 + 18), "sorted by tier", font("body", 13), PAL["dim"], "rm")
    hy = Y0 + 44
    for x_, lab, al in ((CX0 + 64, "ITEM", "lm"), (CX1 - 190, "BUY NOW", "rm"), (CX1 - 100, "SELL NOW", "rm"), (CX1 - 18, "24 H", "rm")):
        text(im, (x_, hy), lab, font("head", 12), PAL["dim"], al, track=1.2)
    yy = hy + 14
    for i, (ic, nm, t, b, s_, tr) in enumerate(BZ_ITEMS):
        row(im, (CX0 + 10, yy, CX1 - 10, yy + 52), "selected" if i == 1 else "normal")
        paste_icon(im, ic, CX0 + 18, yy + 6, 40)
        text(im, (CX0 + 64, yy + 18), nm, font("bodyb", 15), "#ffffff", "lm")
        if t:
            text(im, (CX0 + 64, yy + 37), {"T1": "T1 Copper", "T2": "T2 Iron", "T4": "T4 Thorium"}[t], font("bodyb", 13),
                 {"T1": "#e08a4a", "T2": "#b8c4d0", "T4": "#7fd07a"}[t], "lm")
        text(im, (CX1 - 190, yy + 26), b, font("headb", 15), "#ffd76a", "rm")
        text(im, (CX1 - 100, yy + 26), s_, font("headb", 15), "#ffd76a", "rm")
        text(im, (CX1 - 18, yy + 26), tr, font("bodyb", 14), PAL["green"] if tr.startswith("+") else (PAL["red"] if tr.startswith("-") else PAL["dim"]), "rm")
        yy += 56
    # ---- right: the selected item (4 big buttons + one short step) + your orders
    RX0 = CX1 + 12
    panel(im, (RX0, Y0, X1, 610), "Iron Ore")
    paste_icon(im, "px:ore:#b8c4d0", RX0 + 14, Y0 + 36, 48)
    text(im, (RX0 + 72, Y0 + 50), "Iron Ore", font("headb", 20), "#ffffff", "lm")
    rich(im, RX0 + 72, Y0 + 74, [("T2 Iron", font("bodyb", 14), "#b8c4d0"), ("   you hold ", font("body", 14), PAL["dim"]), ("1,912", font("bold", 14), "#ffffff")])
    bw = (X1 - RX0 - 36) // 2
    for k, (lab, price, kind) in enumerate((("BUY NOW", "28.1 each", "primary"), ("SELL NOW", "26.0 each", "green"),
                                            ("BUY ORDER", "set your price", "secondary"), ("SELL OFFER", "set your price", "secondary"))):
        bx = RX0 + 12 + (k % 2) * (bw + 12)
        by = Y0 + 100 + (k // 2) * 62
        button(im, (bx, by, bx + bw, by + 54), "", kind, "hover" if k == 3 else "normal")
        text(im, (bx + bw // 2, by + 20), lab, font("headb", 17), "#ffffff", "mm")
        text(im, (bx + bw // 2, by + 39), price, font("bodyb", 13), "#ffe9a8" if k < 2 else PAL["row"], "mm")
    sy = Y0 + 236
    panel(im, (RX0 + 10, sy, X1 - 10, sy + 150), inset=True, c=6)
    outline(im, (RX0 + 10, sy, X1 - 10, sy + 150), A["lo"], c=6)
    text(im, (RX0 + 22, sy + 16), "SELL OFFER  -  step 1 of 1", font("head", 12), A["hi"], "lm", track=1.3)
    text(im, (RX0 + 22, sy + 42), "Amount", font("bodyb", 14), PAL["row"], "lm")
    ax = RX0 + 100
    for i, lab in enumerate(["1", "64", "All (1,912)", "Type..."]):
        ax += chip(im, ax, sy + 28, lab, i == 2, h=28, fsize=13) + 6
    text(im, (RX0 + 22, sy + 82), "Price", font("bodyb", 14), PAL["row"], "lm")
    ax = RX0 + 100
    for i, lab in enumerate(["Best 27.9", "Beat by 1: 27.8", "Type..."]):
        ax += chip(im, ax, sy + 68, lab, i == 1, h=28, fsize=13) + 6
    rich(im, RX0 + 22, sy + 126, [("Total  ", font("body", 15), PAL["dim"]), ("53,153", font("headb", 18), "#ffd76a"), (" coins", font("body", 15), PAL["dim"]),
                                  ("   (tax 1%)", font("body", 13), PAL["dim"])])
    button(im, (X1 - 266, sy + 110, X1 - 170, sy + 140), "Back", "secondary", fsize=14)
    button(im, (X1 - 160, sy + 110, X1 - 22, sy + 140), "Confirm", "primary", fsize=15)
    oy = sy + 168
    sub_title(im, RX0 + 14, oy, "YOUR ORDERS  2", X1 - 14)
    for i, (t1, t2, fr) in enumerate((("Buy order  640 Coal at 5.6", "412 / 640 filled", 0.64), ("Sell offer  128 Enchanted Iron at 2,950", "ready to claim 377,600", 1.0))):
        ry = oy + 14 + i * 50
        row(im, (RX0 + 10, ry, X1 - 10, ry + 44), "normal")
        text(im, (RX0 + 20, ry + 13), t1, font("bodyb", 14), "#ffffff", "lm")
        bar(im, (RX0 + 20, ry + 28, RX0 + 220, ry + 35), fr, "green")
        text(im, (RX0 + 230, ry + 32), t2, font("body", 13), PAL["green"] if fr >= 1 else PAL["dim"], "lm")
        if fr >= 1:
            button(im, (X1 - 96, ry + 8, X1 - 18, ry + 36), "Claim", "green", fsize=13)
    # ---- bottom row: auctions | merchants | bank
    BY0 = 620
    AX1 = X0 + 620
    panel(im, (X0, BY0, AX1, Y1), "Auction House", link="Browse all")
    search_box(im, (X0 + 12, BY0 + 34, X0 + 300, BY0 + 62), "Search auctions")
    chip(im, X0 + 310, BY0 + 33, "Ending soon", True, h=30, fsize=13)
    auc = [(I_ACC % "razorfang-legendary", "Legendary Razorfang", "Legendary", "1.2M", "2m 10s", "bid"),
           (I_PET % "Hawk", "Epic Hawk  Lv 14", "Epic", "410k", "18m", "bin"),
           (K.I_ARM % "Mithril_Mining_Chest" if False else "px:sword", "Rare Iron Sword", "Rare", "36k", "1h 4m", "bin")]
    yy = BY0 + 74
    rcol = {"Legendary": "#bb8a2c", "Epic": "#8b339e", "Rare": "#2770b7"}
    for ic, nm, rr, pr, tl, kind in auc:
        row(im, (X0 + 10, yy, AX1 - 10, yy + 44), "normal")
        slot(im, X0 + 16, yy + 4, "empty", rcol[rr], ic, size=36)
        text(im, (X0 + 62, yy + 14), nm, font("bodyb", 14), mix(rcol[rr], "#ffffff", 0.35), "lm")
        text(im, (X0 + 62, yy + 32), ("Top bid " if kind == "bid" else "Buy now ") + pr, font("headb", 13), "#ffd76a", "lm")
        text(im, (AX1 - 120, yy + 22), tl, font("body", 13), PAL["dim"], "rm")
        button(im, (AX1 - 108, yy + 8, AX1 - 18, yy + 36), "Bid" if kind == "bid" else "Buy", "primary", fsize=13)
        yy += 48
    sub_title(im, X0 + 14, yy + 12, "YOUR LISTINGS  2 / 14", AX1 - 14)
    rich(im, X0 + 14, yy + 36, [("Enchanted Oak Log x64  ", font("bodyb", 14), "#ffffff"), ("sold 52,000", font("bodyb", 14), PAL["green"]),
                                ("     Rare Lantern  ", font("bodyb", 14), "#ffffff"), ("3h left", font("body", 14), PAL["dim"])])
    button(im, (X0 + 14, Y1 - 46, X0 + 190, Y1 - 14), "+ New listing", "primary", fsize=14)
    button(im, (AX1 - 156, Y1 - 46, AX1 - 14, Y1 - 14), "Claim 52,000", "green", fsize=14)
    MX0, MX1 = AX1 + 12, AX1 + 12 + 400
    panel(im, (MX0, BY0, MX1, Y1), "Merchants")
    mer = [("Travelling merchant", "Zone 1 town  -  leaves in 1h 40m", "3 rumours, 5 deals"), ("Blacksmith", "Hub  -  tools, repairs", "always open"),
           ("Fishmonger", "Hub docks  -  bait, rods", "always open"), ("Pet keeper", "Hub  -  Legendary eggs", "Legendary eggs only here + AH")]
    yy = BY0 + 34
    for i, (nm, where, note) in enumerate(mer):
        row(im, (MX0 + 10, yy, MX1 - 10, yy + 62), "normal")
        paste_icon(im, I_HUB % "market_merchants", MX0 + 18, yy + 15, 32)
        text(im, (MX0 + 62, yy + 15), nm, font("bodyb", 15), "#ffffff", "lm")
        text(im, (MX0 + 62, yy + 33), where, font("body", 13), PAL["row"], "lm")
        text(im, (MX0 + 62, yy + 50), note, font("body", 13), PAL["dim"], "lm")
        button(im, (MX1 - 84, yy + 18, MX1 - 18, yy + 44), "Go" if i == 0 else "Shop", "secondary", fsize=13)
        yy += 66
    # bank mini-game
    KX0 = MX1 + 12
    panel(im, (KX0, BY0, X1, Y1), "Bank")
    level_pill(im, X1 - 92, BY0 + 8, "Bank Lv 4")
    text(im, (KX0 + 14, BY0 + 48), "3,212,400", font("headb", 28), "#ffd76a", "lm")
    text(im, (KX0 + 16, BY0 + 72), "in the bank  -  capacity 5,000,000", font("body", 14), PAL["dim"], "lm")
    bar(im, (KX0 + 14, BY0 + 86, X1 - 14, BY0 + 98), 3212400 / 5000000.0, "xp")
    rich(im, KX0 + 14, BY0 + 122, [("Interest  ", font("body", 15), PAL["dim"]), ("1.2% a day", font("bold", 15), PAL["green"]),
                                   ("  ->  +38,548 at the next reset", font("bodyb", 15), PAL["row"])])
    button(im, (KX0 + 14, BY0 + 140, KX0 + 160, BY0 + 172), "Deposit", "primary", fsize=15)
    button(im, (KX0 + 170, BY0 + 140, KX0 + 316, BY0 + 172), "Withdraw", "secondary", fsize=15)
    sub_title(im, KX0 + 14, BY0 + 194, "UPGRADE  Lv 4 -> 5", X1 - 14, PAL["xp"])
    rich(im, KX0 + 14, BY0 + 218, [("Capacity  ", font("body", 14), PAL["dim"]), ("5M -> 10M", font("bold", 14), PAL["green"]),
                                   ("    Interest  ", font("body", 14), PAL["dim"]), ("1.2% -> 1.4%", font("bold", 14), PAL["green"])])
    rich(im, KX0 + 14, BY0 + 240, [("Vault pages allowed  ", font("body", 14), PAL["dim"]), ("10 -> 12", font("bold", 14), PAL["green"])])
    put(im, g_coin(16), KX0 + 14, BY0 + 256)
    text(im, (KX0 + 36, BY0 + 264), "500,000", font("headb", 15), "#ffd76a", "lm")
    button(im, (X1 - 150, BY0 + 252, X1 - 14, BY0 + 282), "Upgrade", "primary", fsize=14)
    sub_title(im, KX0 + 14, BY0 + 304, "VAULT PAGES  3 owned / 10 allowed", X1 - 14)
    vx = KX0 + 14
    for i in range(10):
        st = "selected" if i < 3 else "empty"
        bx_ = vx + i * 34
        grad_fill(im, (bx_, BY0 + 318, bx_ + 28, BY0 + 346), A["btnTop"] if i < 3 else "#16233a", A["btnBot"] if i < 3 else "#0c1424", c=3)
        outline(im, (bx_, BY0 + 318, bx_ + 28, BY0 + 346), A["base"] if i < 3 else "#2b3d5b", c=3)
        text(im, (bx_ + 14, BY0 + 332), str(i + 1), font("headb", 13), "#ffffff" if i < 3 else "#5d6a7c", "mm")
        _ = st
    button(im, (X1 - 150, BY0 + 356, X1 - 14, BY0 + 384), "Buy page 4", "secondary", fsize=13)
    text(im, (KX0 + 14, BY0 + 370), "50,000 coins", font("bodyb", 13), "#ffd76a", "lm")
    footer(im, [("LMB", "Select"), ("Shift+LMB", "Buy / sell 64"), ("Type", "Search"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ world
ZONES = [("Zone 1", "Emerald Wilds", "Lv 1-20", "#4fd88a", "Safe"), ("Zone 2", "Howling Sands", "Lv 20-40", "#f0c53a", "Low"),
         ("Zone 3", "Whisperfrost Frontiers", "Lv 40-60", "#6fb7e8", "Medium"), ("Zone 4", "Devastated Lands", "Lv 60-80", "#ff8a4a", "High"),
         ("Zone 5", "(name TBD)", "Lv 80-100", "#ff5c6c", "Deadly")]


def hub_town(a, cx, by, sc=1.0):
    """a tiny hub town: 3 houses + a little tower (our own drawing)"""
    ol = "#14100c"
    for dx, dy, hw, hh, roof in ((-16, 4, 12, 10, "#c0563a"), (2, 0, 14, 12, "#3a6ec0"), (19, 5, 11, 9, "#c08a3a")):
        x, y = cx + dx * sc, by + dy * sc
        a.rect((x - hw * sc / 2, y - hh * sc, x + hw * sc / 2, y), "#efe6d2", 1, ol, 0.8)
        a.poly([(x - hw * sc / 2 - 2, y - hh * sc), (x, y - hh * sc - 8 * sc), (x + hw * sc / 2 + 2, y - hh * sc)], roof, ol, 0.8)
    a.rect((cx + 30 * sc, by - 22 * sc, cx + 37 * sc, by + 4 * sc), "#b8b0a0", 1, ol, 0.8)
    a.poly([(cx + 28 * sc, by - 22 * sc), (cx + 33.5 * sc, by - 31 * sc), (cx + 39 * sc, by - 22 * sc)], "#c0563a", ol, 0.8)


SPOTS_V2 = [(0.16, 0.27, 68, "#5cbf4a", "#7a6a58"), (0.34, 0.68, 68, "#d9c27a", "#9a7a50"), (0.55, 0.22, 68, "#e6f0f8", "#7a8a9a"),
            (0.83, 0.36, 68, "#8a5a40", "#4a3a30"), (0.57, 0.77, 64, "#3f8a3a", "#5a4a38"), (0.1, 0.76, 40, "#5cbf4a", "#7a6a58")]


def world_map_v2(w, h):
    from make_skill_pages import Art, island, tree, cloud, crystal
    a = Art(w, h, 2, bg=rgb("#7fc0f0"))
    for k in range(20):
        t = k / 19.0
        a.rect((0, h * t, w, h * (t + 1 / 19.0) + 1), mix("#8fd0ff", "#3a78c0", t))
    for fx, fy, sc in ((0.1, 0.1, 0.6), (0.72, 0.06, 0.7), (0.4, 0.95, 1.0), (0.94, 0.62, 0.6)):
        cloud(a, w * fx, h * fy, sc, 120)
    for i, (fx, fy, r, g, rk) in enumerate(SPOTS_V2):
        island(a, w * fx, h * fy, r * 1.5, r * 0.6, r * 0.9, grass=g, rock=rk, cliff_steps=5)
        if i == 5:
            tree(a, w * fx - r * 0.3, h * fy + 2, r / 380.0, "oak")
            continue
        deco = ["oak", "dry", "ice", "fire", "beech"][i]
        if deco in ("ice", "fire"):
            crystal(a, w * fx - r * 0.55, h * fy + 4, r / 70.0, "#bfe6ff" if deco == "ice" else "#ff8a4a")
        else:
            tree(a, w * fx - r * 0.55, h * fy + 2, r / 430.0, deco)
        hub_town(a, w * fx + r * 0.25, h * fy - 2, r / 60.0)
    return a.done(), SPOTS_V2


def world_map(w, h):
    from make_skill_pages import Art, island, tree, cloud, crystal
    a = Art(w, h, 2, bg=rgb("#7fc0f0"))
    for k in range(20):
        t = k / 19.0
        a.rect((0, h * t, w, h * (t + 1 / 19.0) + 1), mix("#8fd0ff", "#3a78c0", t))
    for fx, fy, sc in ((0.1, 0.1, 0.6), (0.7, 0.08, 0.7), (0.5, 0.92, 1.0), (0.92, 0.6, 0.6)):
        cloud(a, w * fx, h * fy, sc, 120)
    spots = [(0.47, 0.45, 76, "#6fbf4a", "#7a6a58"), (0.15, 0.25, 62, "#5cbf4a", "#7a6a58"), (0.3, 0.7, 62, "#d9c27a", "#9a7a50"),
             (0.62, 0.17, 62, "#e6f0f8", "#7a8a9a"), (0.85, 0.36, 62, "#8a5a40", "#4a3a30"), (0.56, 0.78, 62, "#3f8a3a", "#5a4a38"),
             (0.1, 0.72, 40, "#5cbf4a", "#7a6a58")]
    for i, (fx, fy, r, g, rk) in enumerate(spots):
        island(a, w * fx, h * fy, r * 1.5, r * 0.6, r * 0.9, grass=g, rock=rk, cliff_steps=5)
        if i in (0, 1, 5, 6):
            tree(a, w * fx - r * 0.4, h * fy + 4, r / 420.0, "oak")
            tree(a, w * fx + r * 0.3, h * fy - 2, r / 380.0, "oak" if i != 5 else "beech")
        elif i == 3:
            crystal(a, w * fx, h * fy + 4, r / 60.0, "#bfe6ff")
        elif i == 2:
            tree(a, w * fx, h * fy, r / 420.0, "dry")
        elif i == 4:
            crystal(a, w * fx, h * fy + 4, r / 60.0, "#ff8a4a")
    return a.done(), spots


def make_world(v2=True):
    im, (WX0, WY0, WX1, WY1) = window_new("World")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    MX1 = X0 + 1000
    panel(im, (X0, Y0, MX1, 676), "Map")
    cx = X0 + 90
    for i, lab in enumerate(["Warps", "Homes", "Islands", "Quests", "Danger"]):
        cx += chip(im, cx, Y0 + 6, lab, True, h=26, fsize=13) + 6
    VX0, VY0, VX1, VY1 = X0 + 12, Y0 + 38, MX1 - 12, 664
    w, h = VX1 - VX0 + 1, VY1 - VY0 + 1
    mp, spots = world_map_v2(w, h) if v2 else world_map(w, h)
    m = __import__("PIL.Image", fromlist=["Image"]).new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=255)
    im.paste(mp, (VX0, VY0), m)
    outline(im, (VX0, VY0, VX1, VY1), "#34496b", c=8)
    labels = [("HUB", "Spawn, shops, Bazaar", "#ffffff", None), ("Zone 1", None, None, 0), ("Zone 2", None, None, 1), ("Zone 3", None, None, 2),
              ("Zone 4", None, None, 3), ("Zone 5", None, None, 4), ("YOUR ISLAND", "Home", "#8fe08a", None)]
    if v2:   # Skyy 11-14: "there is no separate hub island, there is a hub per zone island."
        labels = labels[1:]
    order = list(range(len(labels)))
    for i in order:
        fx, fy, r, _g, _rk = spots[i]
        lx, ly = VX0 + int(w * fx), VY0 + int(h * fy) + int(r * 0.35)
        t1, t2, col, zi = labels[i]
        if zi is not None:
            zn, name, lv, dc, dang = ZONES[zi]
            t1, t2 = "%s  %s" % (zn, name), "%s  -  danger: %s" % (lv, dang)
            col = dc
            if v2:
                hx_, hy_ = VX0 + int(w * fx) + int(r * 0.25), VY0 + int(h * fy) - int(r * 0.62)
                grad_fill(im, (hx_ - 30, hy_ - 9, hx_ + 30, hy_ + 8), "#0e1729", "#0a111e", c=4, alpha=220)
                text(im, (hx_, hy_), "Hub town", font("bodyb", 11), "#ffe9a8", "mm", shadow=False)
        bw = max(tw(t1, font("headb", 14)), tw(t2, font("body", 13))) + 22
        grad_fill(im, (lx - bw // 2, ly, lx + bw // 2, ly + 40), "#0e1729", "#0a111e", c=5, alpha=230)
        outline(im, (lx - bw // 2, ly, lx + bw // 2, ly + 40), col if zi is not None else "#34496b", c=5)
        text(im, (lx, ly + 13), t1, font("headb", 14), "#ffffff", "mm")
        text(im, (lx, ly + 29), t2, font("body", 13), col if zi is not None else PAL["dim"], "mm")
        # warp pin
        px_, py_ = VX0 + int(w * fx), VY0 + int(h * fy) - int(r * 0.9)
        pin = ss_glyph(22, 30, lambda d, s, c=(col or "#45a8ff"): (d.ellipse((s, s, 21 * s, 21 * s), fill=rgb(c), outline=rgb("#0a0f18"), width=int(1.5 * s)),
                                                                    d.polygon([(4 * s, 15 * s), (18 * s, 15 * s), (11 * s, 29 * s)], fill=rgb(c)),
                                                                    d.ellipse((7 * s, 7 * s, 15 * s, 15 * s), fill=rgb("#ffffff"))))
        put(im, pin, px_ - 11, py_ - 30)
    # you-are-here + quest marker
    fx, fy, r, _g, _rk = spots[0 if v2 else 1]
    hx, hy = VX0 + int(w * fx) - (60 if v2 else -40), VY0 + int(h * fy) - 10
    glow(im, (hx - 8, hy - 8, hx + 8, hy + 8), A["base"], 6, 200, 8, 3)
    dot(im, hx, hy, A["base"], 8)
    dot(im, hx, hy, "#ffffff", 3)
    text(im, (hx + 14, hy), "You", font("headb", 14), "#ffffff", "lm")
    fx, fy, r, _g, _rk = spots[1 if v2 else 2]
    qx, qy = VX0 + int(w * fx) + 30, VY0 + int(h * fy) - 20
    put(im, K.g_quest(26, PAL["action"]), qx - 13, qy - 13)
    # selected warp card (on the map)
    cx0, cy0 = VX1 - 300, VY1 - 128
    grad_fill(im, (cx0, cy0, VX1 - 12, cy0 + 116), "#0e1729", "#0a111e", c=6, alpha=238)
    outline(im, (cx0, cy0, VX1 - 12, cy0 + 116), A["base"], c=6)
    text(im, (cx0 + 14, cy0 + 18), "Zone 2  Howling Sands", font("headb", 16), "#ffffff", "lm")
    text(im, (cx0 + 14, cy0 + 40), "Hub town + warps: Oasis camp, Dune gate" if v2 else "Warps: Oasis camp, Dune gate", font("body", 13), PAL["row"], "lm")
    rich(im, cx0 + 14, cy0 + 60, [("Danger ", font("body", 13), PAL["dim"]), ("Low", font("bodyb", 13), "#f0c53a"),
                                  ("    Cost ", font("body", 13), PAL["dim"]), ("free", font("bodyb", 13), PAL["green"])])
    button(im, (cx0 + 14, cy0 + 78, cx0 + 134, cy0 + 106), "Teleport", "primary", fsize=14)
    button(im, (cx0 + 142, cy0 + 78, VX1 - 26, cy0 + 106), "Set as home", "secondary", fsize=13)
    # ---- bottom: island + explore
    BY0 = 686
    IX1 = X0 + 420
    panel(im, (X0, BY0, IX1, Y1), "Your island")
    text(im, (X0 + 14, BY0 + 46), "Skyy's Island", font("headb", 18), "#ffffff", "lm")
    text(im, (X0 + 14, BY0 + 68), "Members 2  -  Homes 1 / 2", font("body", 14), PAL["dim"], "lm")
    yy = BY0 + 92
    for lab, on in (("Visitors can enter", True), ("Visitors can open chests", False), ("PvP on my island", False)):
        text(im, (X0 + 14, yy + 11), lab, font("body", 15), PAL["row"], "lm")
        K.toggle(im, IX1 - 60, yy, on, w=40, h=22)
        yy += 32
    button(im, (X0 + 14, Y1 - 46, X0 + 150, Y1 - 14), "Go home", "primary", fsize=14)
    button(im, (X0 + 160, Y1 - 46, X0 + 290, Y1 - 14), "Members", "secondary", fsize=14)
    button(im, (X0 + 300, Y1 - 46, IX1 - 14, Y1 - 14), "Rename", "secondary", fsize=14)
    EX0 = IX1 + 12
    panel(im, (EX0, BY0, MX1, Y1), "Explore")
    text(im, (MX1 - 14, BY0 + 18), "Discoveries 47 / 160", font("headb", 14), PAL["xp"], "rm")
    yy = BY0 + 40
    for zn, name, lv, dc, dang in ZONES[:4]:
        frac = {"Zone 1": 0.82, "Zone 2": 0.45, "Zone 3": 0.12, "Zone 4": 0.0}[zn]
        text(im, (EX0 + 14, yy + 9), "%s %s" % (zn, name), font("bodyb", 14), PAL["row"], "lm")
        bar(im, (EX0 + 250, yy + 4, MX1 - 80, yy + 14), frac, "accent")
        text(im, (MX1 - 14, yy + 9), "%d%%" % int(frac * 100), font("headb", 13), PAL["xp"], "rm")
        yy += 26
    sub_title(im, EX0 + 14, yy + 12, "TITLE", MX1 - 14)
    rich(im, EX0 + 14, yy + 36, [("Wearing  ", font("body", 14), PAL["dim"]), ("Sandwalker", font("bodyb", 14), "#f0c53a"),
                                 ("   12 titles unlocked", font("body", 14), PAL["dim"])])
    sub_title(im, EX0 + 14, yy + 62, "BESTIARY + DROPS CODEX", MX1 - 14)
    bx = EX0 + 14
    for nm, ic in (("Wolf", I_PET % "Wolf"), ("Boar", I_PET % "Boar"), ("Hawk", I_PET % "Hawk"), ("Skrill", I_PET % "Skrill"), ("Bear", I_PET % "Bear")):
        slot(im, bx, yy + 76, "empty", None, ic, size=48)
        bx += 54
    text(im, (bx + 6, yy + 92), "every mob + loot bag", font("body", 13), PAL["dim"], "lm")
    text(im, (bx + 6, yy + 110), "with drop chances", font("body", 13), PAL["dim"], "lm")
    # ---- right: quests
    QX0 = MX1 + 12
    panel(im, (QX0, Y0, X1, Y1), "Quests")
    yy = Y0 + 38
    row(im, (QX0 + 10, yy, X1 - 10, yy + 168), "selected")
    text(im, (QX0 + 24, yy + 16), "TRACKED  -  STORY CHAPTER 2", font("head", 12), A["hi"], "lm", track=1.3)
    text(im, (QX0 + 24, yy + 40), "Into the Howling Sands", font("headb", 18), "#ffffff", "lm")
    for k, (ok, s_) in enumerate(((True, "Reach the Oasis camp"), (True, "Talk to the camp scout"), (False, "Defeat 10 sand mobs  6 / 10"),
                                  (False, "Return to the scout"))):
        put(im, g_check(13, PAL["green"]) if ok else g_diamond(9, PAL["action"]), QX0 + 24, yy + 58 + k * 21)
        text(im, (QX0 + 44, yy + 64 + k * 21), s_, font("body", 14), PAL["dim"] if ok else PAL["row"], "lm")
    rich(im, QX0 + 24, yy + 152, [("Rewards  ", font("body", 14), PAL["dim"]), ("2,500 coins", font("bodyb", 14), "#ffd76a"),
                                  ("  +600 Combat XP", font("bodyb", 14), PAL["xp"]), ("   340 m", font("bodyb", 14), PAL["action"])])
    yy += 182
    sub_title(im, QX0 + 14, yy, "DAILIES   reset in 5h 12m", X1 - 14, PAL["xp"])
    for k, (s_, fr, rw) in enumerate((("Mine 200 Copper Ore", 1.0, "Claim"), ("Catch 10 fish", 0.4, "4 / 10"), ("Defeat 25 Zone 1 mobs", 0.0, "0 / 25"))):
        ry = yy + 14 + k * 46
        row(im, (QX0 + 10, ry, X1 - 10, ry + 40), "normal")
        text(im, (QX0 + 20, ry + 13), s_, font("bodyb", 14), "#ffffff", "lm")
        bar(im, (QX0 + 20, ry + 26, QX0 + 260, ry + 32), fr, "green")
        if rw == "Claim":
            button(im, (X1 - 90, ry + 7, X1 - 18, ry + 33), "Claim", "green", fsize=13)
        else:
            text(im, (X1 - 20, ry + 20), rw, font("headb", 13), PAL["xp"], "rm")
    yy += 14 + 3 * 46 + 16
    sub_title(im, QX0 + 14, yy, "WEEKLIES   reset in 3d 5h", X1 - 14, PAL["xp"])
    for k, (s_, fr, rw) in enumerate((("Clear 3 dungeon floors", 0.33, "1 / 3"), ("Earn 50,000 coins at the Bazaar", 0.7, "35k / 50k"))):
        ry = yy + 14 + k * 46
        row(im, (QX0 + 10, ry, X1 - 10, ry + 40), "normal")
        text(im, (QX0 + 20, ry + 13), s_, font("bodyb", 14), "#ffffff", "lm")
        bar(im, (QX0 + 20, ry + 26, QX0 + 260, ry + 32), fr, "green")
        text(im, (X1 - 20, ry + 20), rw, font("headb", 13), PAL["xp"], "rm")
    yy += 14 + 2 * 46 + 16
    sub_title(im, QX0 + 14, yy, "STORY + SIDE", X1 - 14)
    for k, (s_, st) in enumerate((("Chapter 1  Emerald Wilds", "done"), ("Chapter 2  Into the Howling Sands", "active"),
                                  ("Side: The lost caravan", "open"), ("Achievements  34 / 120", "open"))):
        ry = yy + 16 + k * 26
        put(im, g_check(13, PAL["green"]) if st == "done" else g_diamond(9, A["hi"] if st == "active" else PAL["dim"]), QX0 + 18, ry - 6)
        text(im, (QX0 + 38, ry), s_, font("body", 14), PAL["dim"] if st == "done" else PAL["row"], "lm")
    yy += 16 + 4 * 26 + 12
    sub_title(im, QX0 + 14, yy, "ACHIEVEMENTS  34 / 120", X1 - 14)
    bar(im, (QX0 + 14, yy + 16, X1 - 14, yy + 24), 34 / 120.0, "xp")
    for k, (s_, rw) in enumerate((("Reach Mining 30", "done 2d ago"), ("Hatch an Epic pet", "done 5d ago"), ("Visit every Zone 2 warp", "3 / 5"))):
        ry = yy + 46 + k * 26
        put(im, g_star(14, "#ffd36b" if "done" in rw else "#6b7380"), QX0 + 16, ry - 7)
        text(im, (QX0 + 38, ry), s_, font("body", 14), PAL["row"], "lm")
        text(im, (X1 - 16, ry), rw, font("body", 13), PAL["dim"] if "done" in rw else PAL["xp"], "rm")
    footer(im, [("LMB", "Select / teleport"), ("RMB", "Track quest"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ social
PLAYERS = [("Brightleaf", "Archer", 27, "Zone 2  Howling Sands", True), ("Orebeard", "Warrior", 31, "Zone 1  Emerald Wilds", True),
           ("Mistveil", "Mage", 19, "Hub", False), ("Thornbuck", "Priest", 24, "Own island", True), ("Quillfeather", "Assassin", 12, "Zone 1", False),
           ("Embervale", "Spellblade", 35, "Zone 3", False), ("Stonejaw", "Berserker", 22, "Hub", False), ("Lotusfist", "Monk", 16, "Zone 1", False)]


def make_social():
    im, (WX0, WY0, WX1, WY1) = window_new("Social")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    PX1 = X0 + 560
    panel(im, (X0, Y0, PX1, Y1), "Players online")
    text(im, (PX1 - 14, Y0 + 18), "38 online", font("headb", 14), PAL["green"], "rm")
    search_box(im, (X0 + 12, Y0 + 36, X0 + 280, Y0 + 66), "Find a player")
    cx = X0 + 290
    for i, lab in enumerate(["All", "Friends", "Nearby"]):
        cx += chip(im, cx, Y0 + 35, lab, i == 0, h=31, fsize=13) + 6
    yy = Y0 + 80
    for i, (nm, cl, lv, where, fr) in enumerate(PLAYERS):
        row(im, (X0 + 10, yy, PX1 - 10, yy + 62), "selected" if i == 1 else "normal")
        slot(im, X0 + 18, yy + 7, "empty", None, I_EMB % cl, size=48)
        rich(im, X0 + 76, yy + 20, [(nm, font("headb", 16), "#ffffff"), ("   %s Lv %d" % (cl, lv), font("bodyb", 14), PAL["xp"])])
        text(im, (X0 + 76, yy + 42), where + ("   -  friend" if fr else ""), font("body", 13), PAL["dim"], "lm")
        bx = PX1 - 112
        for g in (g_trade(16, "#c2d1e2"), g_chat(16, "#c2d1e2"), g_invite(16, "#c2d1e2")):
            ico_btn(im, bx, yy + 18, g, 30)
            bx += 34
        yy += 66
    text(im, (X0 + 14, Y1 - 18), "Right-click a player: trade, whisper, party, guild invite, visit island", font("bodyb", 13), PAL["action"], "lm")
    # ---- centre: profile card + profiles
    CX0, CX1 = PX1 + 12, PX1 + 12 + 540
    panel(im, (CX0, Y0, CX1, 700), "You")
    slot(im, CX0 + 14, Y0 + 36, "empty", None, I_EMB % "Archer", size=96)
    text(im, (CX0 + 126, Y0 + 52), "Skyy", font("headb", 24), "#ffffff", "lm")
    rich(im, CX0 + 126, Y0 + 80, [("Archer", font("bodyb", 15), "#8fe08a"), ("   Combat Lv 27", font("bodyb", 15), PAL["xp"])])
    level_pill(im, CX0 + 126, Y0 + 98, "Overall Lv 23")
    text(im, (CX0 + 250, Y0 + 109), "Title: Sandwalker", font("bodyb", 14), "#f0c53a", "lm")
    sub_title(im, CX0 + 14, Y0 + 152, "SKILLS", CX1 - 14)
    sk = [("Combat", 27), ("Mining", 31), ("Farming", 24), ("Foraging", 27), ("Fishing", 19), ("Smithing", 15), ("Cooking", 12), ("Alchemy", 9)]
    for i, (nm, lv) in enumerate(sk):
        x = CX0 + 14 + (i % 2) * 262
        y = Y0 + 174 + (i // 2) * 34
        text(im, (x, y + 8), nm, font("body", 15), PAL["row"], "lm")
        text(im, (x + 240, y + 8), str(lv), font("headb", 15), PAL["xp"], "rm")
        bar(im, (x, y + 20, x + 240, y + 25), (lv * 37 % 100) / 100.0, "xp")
    sub_title(im, CX0 + 14, Y0 + 324, "STATS (gear on)", CX1 - 14)
    st = [("Health", "245"), ("Defense", "+41"), ("Damage", "+14"), ("Crit Chance", "5%"), ("Mana", "30"), ("Speed", "+4%")]
    for i, (nm, v) in enumerate(st):
        x = CX0 + 14 + (i % 2) * 262
        y = Y0 + 348 + (i // 2) * 26
        text(im, (x, y), nm, font("body", 15), PAL["row"], "lm")
        text(im, (x + 240, y), v, font("bold", 15), PAL["green"], "rm")
    sub_title(im, CX0 + 14, Y0 + 438, "PROGRESS", CX1 - 14)
    for i, (nm, v) in enumerate((("Coins (purse + bank)", "4,457,610"), ("Collections", "38 / 96"), ("Pets", "20 / 120"), ("Playtime", "212 h"))):
        y = Y0 + 462 + i * 26
        text(im, (CX0 + 14, y), nm, font("body", 15), PAL["row"], "lm")
        text(im, (CX1 - 14, y), v, font("bold", 15), "#ffd76a" if i == 0 else PAL["xp"], "rm")
    button(im, (CX0 + 14, 700 - 50, CX0 + 200, 700 - 16), "Show my profile in chat", "secondary", fsize=13)
    panel(im, (CX0, 710, CX1, Y1), "Profiles")
    text(im, (CX1 - 14, 728), "2 / 4", font("headb", 14), PAL["xp"], "rm")
    pw = (CX1 - CX0 - 36) // 3
    for i, (nm, sub, act) in enumerate((("Main", "Archer  -  Overall 23", True), ("Ironman", "Warrior  -  Overall 6", False), (None, None, False))):
        bx = CX0 + 12 + i * (pw + 6)
        box = (bx, 746, bx + pw - 1, Y1 - 12)
        if nm:
            grad_fill(im, box, mix(A["base"], "#111b2d", 0.62) if act else "#18253c", mix(A["base"], "#111b2d", 0.8) if act else "#121c2f", c=5)
            outline(im, box, A["base"] if act else "#2b3d5b", c=5)
            text(im, (bx + pw // 2, 790), nm, font("headb", 18), "#ffffff", "mm")
            text(im, (bx + pw // 2, 814), sub, font("body", 13), PAL["row"], "mm")
            if act:
                text(im, (bx + pw // 2, 846), "ACTIVE", font("headb", 13), A["hi"], "mm", track=1.5)
            else:
                button(im, (bx + 20, 834, bx + pw - 20, 862), "Switch", "primary", fsize=13)
        else:
            grad_fill(im, box, "#121c2f", "#0e1626", c=5)
            outline(im, box, "#2b3d5b", c=5)
            put(im, g_plus(22, "#5a7299"), bx + pw // 2 - 11, 772)
            text(im, (bx + pw // 2, 814), "New profile", font("headb", 15), PAL["row"], "mm")
            text(im, (bx + pw // 2, 836), "fresh start, same account", font("body", 12), PAL["dim"], "mm")
    text(im, (CX0 + 14, Y1 - 24), "", font("body", 12), PAL["dim"], "lm")
    # ---- right: party + guild
    RX0 = CX1 + 12
    panel(im, (RX0, Y0, X1, 470), "Party")
    text(im, (X1 - 14, Y0 + 18), "3 / 5", font("headb", 14), PAL["xp"], "rm")
    yy = Y0 + 38
    for i, (nm, cl, lv, hp) in enumerate((("Skyy", "Archer", 27, 0.9), ("Orebeard", "Warrior", 31, 0.55), ("Thornbuck", "Priest", 24, 1.0))):
        row(im, (RX0 + 10, yy, X1 - 10, yy + 58), "normal")
        paste_icon(im, I_EMB % cl, RX0 + 18, yy + 9, 40)
        rich(im, RX0 + 66, yy + 18, [(nm, font("headb", 15), "#ffffff"), ("  %s %d" % (cl, lv), font("bodyb", 13), PAL["xp"])] +
             ([("  leader", font("bodyb", 12), A["hi"])] if i == 0 else []))
        bar(im, (RX0 + 66, yy + 36, X1 - 24, yy + 44), hp, "health")
        yy += 62
    rich(im, RX0 + 14, yy + 14, [("Loot  ", font("body", 14), PAL["dim"]), ("each their own", font("bodyb", 14), PAL["row"]),
                                 ("    XP share  ", font("body", 14), PAL["dim"]), ("on", font("bodyb", 14), PAL["green"])])
    button(im, (RX0 + 14, 470 - 48, RX0 + 160, 470 - 16), "Invite", "primary", fsize=14)
    button(im, (X1 - 160, 470 - 48, X1 - 14, 470 - 16), "Leave party", "danger", fsize=14)
    panel(im, (RX0, 480, X1, Y1), "Guild")
    text(im, (RX0 + 14, 526), "Skyreach Wardens", font("headb", 20), "#ffffff", "lm")
    rich(im, RX0 + 14, 552, [("Guild Lv 6", font("bodyb", 14), PAL["xp"]), ("   24 members, 7 online", font("body", 14), PAL["dim"])])
    bar(im, (RX0 + 14, 566, X1 - 14, 574), 0.4, "xp")
    grad_fill(im, (RX0 + 12, 588, X1 - 12, 640), "#0e1729", "#0a111e", c=5)
    outline(im, (RX0 + 12, 588, X1 - 12, 640), "#2b3d5b", c=5)
    text(im, (RX0 + 24, 604), "MESSAGE OF THE DAY", font("head", 11), PAL["dim"], "lm", track=1.3)
    text(im, (RX0 + 24, 624), "Dungeon run tonight - bring potions!", font("body", 14), PAL["row"], "lm")
    sub_title(im, RX0 + 14, 660, "ONLINE NOW", X1 - 14)
    for i, (nm, rank) in enumerate((("Orebeard", "Leader"), ("Thornbuck", "Officer"), ("Embervale", "Member"), ("Mistveil", "Member"))):
        y = 684 + i * 26
        dot(im, RX0 + 22, y, PAL["green"], 4)
        text(im, (RX0 + 34, y), nm, font("bodyb", 14), "#ffffff", "lm")
        text(im, (X1 - 14, y), rank, font("body", 13), A["hi"] if rank != "Member" else PAL["dim"], "rm")
    sub_title(im, RX0 + 14, 806, "GUILD QUEST", X1 - 14, PAL["xp"])
    text(im, (RX0 + 14, 830), "Mine 10,000 ore together", font("bodyb", 14), PAL["row"], "lm")
    bar(im, (RX0 + 14, 844, X1 - 14, 852), 0.63, "green")
    text(im, (X1 - 14, 866), "6,310 / 10,000", font("headb", 13), PAL["xp"], "rm")
    button(im, (RX0 + 14, Y1 - 48, RX0 + 170, Y1 - 16), "Guild chat", "primary", fsize=14)
    button(im, (X1 - 170, Y1 - 48, X1 - 14, Y1 - 16), "Manage", "secondary", fsize=14)
    footer(im, [("LMB", "Select"), ("RMB", "Player actions"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ settings
def make_settings():
    im, (WX0, WY0, WX1, WY1) = window_new("Settings")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    C1 = X0 + 520
    panel(im, (X0, Y0, C1, Y1), "Settings")
    search_box(im, (X0 + 12, Y0 + 36, C1 - 12, Y0 + 66), "Search settings")
    yy = Y0 + 84
    groups = [("GAMEPLAY", [("Skill XP popups", True), ("Damage numbers", True), ("Auto-pickup into bags", True), ("Pet nameplates", False)]),
              ("CHAT", [("Hide XP lines in chat", True), ("Show drop messages", True), ("Party chat by default", False)]),
              ("INTERFACE", [("Bigger tooltips", True), ("Rarity frames on items", True), ("Menu sounds", True)])]
    for g, items in groups:
        sub_title(im, X0 + 14, yy, g, C1 - 14)
        yy += 16
        for lab, on in items:
            row(im, (X0 + 10, yy, C1 - 10, yy + 38), "normal")
            text(im, (X0 + 22, yy + 19), lab, font("body", 15), PAL["row"], "lm")
            K.toggle(im, C1 - 66, yy + 8, on, w=40, h=22)
            yy += 42
        yy += 14
    text(im, (X0 + 14, Y1 - 18), "Saved for you, on every profile.", font("body", 13), PAL["dim"], "lm")
    # ---- middle: HUD editor entry + menu layout
    C2 = C1 + 12 + 540
    panel(im, (C1 + 12, Y0, C2, 470), "HUD layout")
    px0, py0, px1, py1 = C1 + 26, Y0 + 40, C2 - 14, 400
    grad_fill(im, (px0, py0, px1, py1), "#5f8ec4", "#2f4f78", c=6)
    outline(im, (px0, py0, px1, py1), "#34496b", c=6)
    for bx in ((px0 + 10, py0 + 10, px0 + 110, py0 + 50), (px1 - 90, py0 + 10, px1 - 10, py0 + 90), (px0 + 10, py1 - 46, px0 + 120, py1 - 10),
               ((px0 + px1) // 2 - 120, py1 - 34, (px0 + px1) // 2 + 120, py1 - 12), (px1 - 130, py1 - 46, px1 - 10, py1 - 10),
               (px0 + 10, py0 + 70, px0 + 100, py0 + 150)):
        grad_fill(im, bx, "#0e1729", "#0a111e", c=4, alpha=220)
        outline(im, bx, A["hi"], c=4)
    text(im, ((px0 + px1) // 2, (py0 + py1) // 2), "preview of your HUD", font("bodyb", 14), "#ffffff", "mm")
    button(im, (C1 + 26, 420, C1 + 250, 456), "Open HUD editor", "primary", fsize=15)
    text(im, (C2 - 14, 438), "drag, scale, hide", font("body", 13), PAL["dim"], "rm")
    panel(im, (C1 + 12, 480, C2, Y1), "Top tab order")
    yy = 516
    for i, (nm, ic) in enumerate(NEW_TABS):
        row(im, (C1 + 22, yy, C2 - 10, yy + 40), "normal")
        text(im, (C1 + 36, yy + 20), "%d" % (i + 1), font("headb", 14), PAL["dim"], "mm")
        paste_icon(im, ic, C1 + 52, yy + 8, 24)
        text(im, (C1 + 86, yy + 20), nm, font("headb", 15), "#ffffff", "lm")
        put(im, K.g_arrows(14, "#8ea3bd", up=True), C2 - 70, yy + 13)
        put(im, K.g_arrows(14, "#8ea3bd", up=False), C2 - 44, yy + 13)
        if nm == "Settings":
            text(im, (C2 - 90, yy + 20), "always last", font("body", 12), PAL["dim"], "rm")
        yy += 44
    button(im, (C1 + 26, Y1 - 46, C1 + 196, Y1 - 14), "Reset order", "secondary", fsize=14)
    # ---- right: mods + server setup
    panel(im, (C2 + 12, Y0, X1, 640), "Mods")
    text(im, (X1 - 14, Y0 + 18), "38 SkyWynn + 12 pack", font("body", 13), PAL["dim"], "rm")
    mods = [("SkyyMenu", "0.3.51"), ("SkyySkills", "0.4.x"), ("SkyyPets", "0.4.25"), ("SkyyBazaar", "0.2.5"), ("SkyyShards", "0.4.22"),
            ("SkyySacks", "0.8.x"), ("SkyyGear", "0.3.x"), ("SkyyHud", "0.3.x")]
    yy = Y0 + 38
    for nm, v in mods:
        row(im, (C2 + 22, yy, X1 - 10, yy + 40), "normal")
        dot(im, C2 + 38, yy + 20, PAL["green"], 4)
        text(im, (C2 + 52, yy + 20), nm, font("bodyb", 15), "#ffffff", "lm")
        text(im, (X1 - 110, yy + 20), v, font("body", 13), PAL["dim"], "rm")
        text(im, (X1 - 22, yy + 20), "Help", font("head", 14), A["hi"], "rm")
        yy += 44
    text(im, (C2 + 26, 640 - 22), "Help shows what each mod adds + its commands.", font("body", 13), PAL["dim"], "lm")
    panel(im, (C2 + 12, 650, X1, Y1), "Server Setup")
    level_pill(im, X1 - 74, 658, "ADMIN", PAL["red"])
    text(im, (C2 + 26, 696), "Every number a server owner can change,", font("body", 14), PAL["row"], "lm")
    text(im, (C2 + 26, 716), "by mod and category, times in seconds.", font("body", 14), PAL["row"], "lm")
    search_box(im, (C2 + 22, 734, X1 - 12, 764), "Search 1,200 settings")
    for i, (nm, n) in enumerate((("Economy", 84), ("Pets", 61), ("Shards", 47), ("Skills + XP", 112))):
        y = 784 + i * 28
        text(im, (C2 + 26, y), nm, font("body", 14), PAL["row"], "lm")
        text(im, (X1 - 22, y), "%d rows" % n, font("body", 13), PAL["dim"], "rm")
    button(im, (C2 + 26, Y1 - 50, X1 - 14, Y1 - 16), "Open Server Setup", "danger", fsize=15)
    text(im, (C2 + 26, 912), "Players without admin see this box locked.", font("body", 13), PAL["dim"], "lm")
    footer(im, [("LMB", "Toggle / select"), ("Type", "Search"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ charms (Void Charms)
CHARM_LINES = [("health", "Health", "+max Health"), ("stamina", "Stamina", "+max Stamina"), ("mana", "Mana", "+% max Mana"),
               ("speed", "Speed", "+% move speed"), ("regeneration", "Regeneration", "heal every 2 s"), ("brawler", "Brawler", "Strength"),
               ("runic", "Runic", "Magical Power"), ("stonehide", "Stonehide", "Defense"), ("razorfang", "Razorfang", "Crit"),
               ("feather", "Feather", "fall / jump"), ("lantern", "Lantern", "light")]
GEAR_R = dict(K.GEAR_RARITY)
OWN = {"health": "legendary", "stamina": "rare", "mana": "unique", "speed": "rare", "regeneration": "unique", "brawler": "rare",
       "runic": "normal", "stonehide": "rare", "razorfang": "legendary", "feather": "unique", "lantern": "unique"}


def make_charms():
    im, (WX0, WY0, WX1, WY1) = window_new("Inventory")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    # no back button (Skyy 10-16 "I never want to have to use a back button"): a breadcrumb + the top tab row stay
    text(im, (X0, Y0 + 18), "INVENTORY  >", font("head", 14), A["hi"], "lm", track=1.2)
    bx = X0 + tw("INVENTORY  >", font("head", 14), 1.2) + 10
    paste_icon(im, K.I_VOID, bx, Y0 - 2, 40)
    text(im, (bx + 48, Y0 + 18), "VOID CHARMS", font("headb", 24), PAL["title"], "lm", track=2)
    x = bx + 48 + tw("VOID CHARMS", font("headb", 24), 2) + 16
    x += level_pill(im, x, Y0 + 7, "Bag: Rare  x1.20 power") + 10
    x += chip(im, x, Y0 + 3, "Charm collection IV  15 / 20", True) + 10
    text(im, (X1, Y0 + 10), "Opened from the Inventory charm row", font("bodyb", 14), A["hi"], "rm")
    text(im, (X1, Y0 + 28), "('Charms page') or any skill page", font("body", 14), PAL["dim"], "rm")
    taper_line(im, X0, X1, Y0 + 50, PAL["gold"], 150, 0.85)
    T0 = Y0 + 62
    # ---- left: the bag (slots) + bag upgrade
    LX1 = X0 + 600
    panel(im, (X0, T0, LX1, 760), "Your charm bag")
    text(im, (LX1 - 14, T0 + 18), "13 / 23 slots", font("headb", 14), PAL["xp"], "rm")
    items = [(k, OWN[k]) for k, _n, _s in CHARM_LINES] + [("speed", "unique"), ("health", "rare")]
    sx0, sy0 = X0 + 14, T0 + 40
    for i in range(28):
        x = sx0 + (i % 7) * 80
        y = sy0 + (i // 7) * 86
        if i < 23 and i < len(items):
            k, r = items[i]
            rc = GEAR_R[r.capitalize()]
            dup = i >= len(CHARM_LINES)
            slot(im, x, y, "selected" if k == "lantern" and not dup else "empty", rc, I_ACC % ("%s-%s" % (k, r)), size=74, dim=dup)
            if dup:
                text(im, (x + 37, y + 64), "not counting", font("bodyb", 11), PAL["red"], "mm")
        elif i < 23:
            slot(im, x, y, "empty", None, None, size=74)
        else:
            slot(im, x, y, "empty", None, None, size=74)
            put(im, g_lock(18, "#5a6a80"), x + 28, y + 26)
    yy = sy0 + 4 * 86 + 4
    text(im, (X0 + 14, yy + 6), "Only the best of each line counts.  Slots grow with the Charm collection + Overall Level.", font("body", 13), PAL["dim"], "lm")
    text(im, (X0 + 14, yy + 26), "Click: select   Shift-click: take out   Drag from your inventory: put in", font("bodyb", 13), PAL["action"], "lm")
    panel(im, (X0, 770, LX1, Y1), "Bag upgrade")
    rich(im, X0 + 14, 812, [("Rare", font("headb", 18), GEAR_R["Rare"]), ("  x1.20   ->   ", font("bodyb", 16), PAL["row"]),
                            ("Legendary", font("headb", 18), GEAR_R["Legendary"]), ("  x1.35 power", font("bodyb", 16), PAL["green"])])
    text(im, (X0 + 14, 838), "Raises every booster number of every charm.", font("body", 14), PAL["dim"], "lm")
    for i, (lab, ok) in enumerate((("Charm collection VI   (you: IV)", False), ("8,000 Copper Ore   (need 1,280)", False), ("8,000 Oak Log", True),
                                   ("8,000 Wheat", True), ("8,000 Bone Fragments   (need 3,400)", False), ("250,000 coins", True))):
        x = X0 + 14 + (i % 2) * 290
        y = 866 + (i // 2) * 26
        put(im, g_check(13, PAL["green"]) if ok else g_x(13, PAL["red"], 2.2), x, y - 7)
        text(im, (x + 20, y), lab, font("body", 14), PAL["green"] if ok else PAL["red"], "lm")
    button(im, (LX1 - 190, Y1 - 46, LX1 - 14, Y1 - 14), "Upgrade bag", "primary", "disabled", fsize=15)
    # ---- middle: selected charm
    MX0, MX1 = LX1 + 12, LX1 + 12 + 520
    panel(im, (MX0, T0, MX1, 640), "Selected charm")
    slot(im, MX0 + 14, T0 + 38, "empty", GEAR_R["Unique"], I_ACC % "lantern-unique", size=96)
    paste_icon(im, I_ACC % "lantern-unique", MX0 + 22, T0 + 46, 80)
    text(im, (MX0 + 126, T0 + 56), "Unique Lantern", font("headb", 24), GEAR_R["Unique"], "lm")
    rich(im, MX0 + 126, T0 + 84, [("Light line", font("bodyb", 14), PAL["row"]), ("   -  needs Tree Sap collection", font("body", 14), PAL["dim"])])
    kind = MX0 + 126
    for lab, col in (("COUNTING", PAL["green"]), ("CAN TIER UP", PAL["xp"])):
        f = font("headb", 12)
        w = tw(lab, f, 1) + 14
        grad_fill(im, (kind, T0 + 100, kind + w, T0 + 120), mix(col, "#0c1422", 0.75), mix(col, "#0c1422", 0.85), c=4)
        outline(im, (kind, T0 + 100, kind + w, T0 + 120), col, c=4)
        text(im, (kind + w // 2, T0 + 110), lab, f, col, "mm", shadow=False, track=1)
        kind += w + 6
    yy = T0 + 156
    sub_title(im, MX0 + 14, yy, "GIVES NOW  (bag x1.20)", MX1 - 14)
    for v, n_ in (("+3", "Light radius (blocks)"), ("on", "Lights the way in caves and at night"), ("x1.20", "bag power applied")):
        yy += 24
        text(im, (MX0 + 20, yy), v, font("bold", 15), PAL["green"], "lm")
        text(im, (MX0 + 70, yy), n_, font("body", 15), PAL["row"], "lm")
    yy += 34
    sub_title(im, MX0 + 14, yy, "TIER UP  Unique -> Rare", MX1 - 14, PAL["xp"])
    yy += 22
    text(im, (MX0 + 20, yy), "Gives  +4 Light radius  (bigger glow)", font("bodyb", 14), PAL["green"], "lm")
    yy += 24
    for lab, ok in (("Unique Lantern (this one)", True), ("64 Tree Sap", True), ("16 Enchanted Iron   (need 9)", False), ("2,500 coins", True)):
        put(im, g_check(13, PAL["green"]) if ok else g_x(13, PAL["red"], 2.2), MX0 + 20, yy - 7)
        text(im, (MX0 + 40, yy), lab, font("body", 14), PAL["green"] if ok else PAL["red"], "lm")
        yy += 22
    yy += 6
    text(im, (MX0 + 20, yy), "or MERGE 3 Unique Lanterns (no materials):  you have 1", font("body", 14), PAL["dim"], "lm")
    button(im, (MX0 + 14, 640 - 48, MX0 + 200, 640 - 14), "Tier up", "primary", "disabled", fsize=15)
    button(im, (MX0 + 210, 640 - 48, MX0 + 360, 640 - 14), "Merge 3", "secondary", "disabled", fsize=15)
    button(im, (MX0 + 370, 640 - 48, MX1 - 14, 640 - 14), "Take out", "secondary", fsize=15)
    # total bonuses
    panel(im, (MX0, 650, MX1, Y1), "All charms together")
    tot = [("Health", "+62"), ("Stamina", "+18"), ("Mana", "+12%"), ("Speed", "+9%"), ("Regeneration", "1.4 / 2 s"), ("Strength", "+14"),
           ("Magical Power", "+4"), ("Defense", "+22"), ("Crit Chance", "+7%"), ("Fall damage", "-40%"), ("Light radius", "+3")]
    for i, (n_, v) in enumerate(tot):
        x = MX0 + 14 + (i % 2) * 250
        y = 690 + (i // 2) * 28
        row(im, (x, y - 12, x + 236, y + 12), "normal")
        text(im, (x + 10, y), n_, font("body", 14), PAL["row"], "lm")
        text(im, (x + 226, y), v, font("bold", 14), PAL["green"], "rm")
    text(im, (MX0 + 14, Y1 - 18), "These add to tool + gear + pets (the four power sources).", font("body", 13), PAL["dim"], "lm")
    # ---- right: every line (album + craft)
    RX0 = MX1 + 12
    panel(im, (RX0, T0, X1, Y1), "Every charm line")
    text(im, (X1 - 14, T0 + 18), "craft + best you own", font("body", 13), PAL["dim"], "rm")
    yy = T0 + 38
    rows_h = (Y1 - yy - 60) // len(CHARM_LINES)
    for k, nm, st in CHARM_LINES:
        r = OWN[k]
        row(im, (RX0 + 10, yy, X1 - 10, yy + rows_h - 4), "selected" if k == "lantern" else "normal")
        paste_icon(im, I_ACC % ("%s-%s" % (k, r)), RX0 + 16, yy + (rows_h - 4) // 2 - 16, 32)
        text(im, (RX0 + 56, yy + 14), nm, font("bodyb", 14), "#ffffff", "lm")
        text(im, (RX0 + 56, yy + 31), st, font("body", 12), PAL["dim"], "lm")
        text(im, (X1 - 100, yy + 20), r.capitalize(), font("bodyb", 13), GEAR_R[r.capitalize()], "rm")
        button(im, (X1 - 88, yy + 8, X1 - 18, yy + rows_h - 12), "Craft" if r == "normal" else "Tier up", "secondary", fsize=12)
        yy += rows_h
    text(im, (RX0 + 14, Y1 - 38), "Normal charms craft from their recipe; higher", font("body", 13), PAL["dim"], "lm")
    text(im, (RX0 + 14, Y1 - 20), "rarities tier up. Fabled / Mythic: drops only.", font("body", 13), PAL["dim"], "lm")
    footer(im, [("LMB", "Select"), ("Shift+LMB", "Take out"), ("Drag", "Put in"), ("Tab / Esc", "Close")])
    return im


# ================================================================================================================ requip (loadouts)
PRESETS = [("Combat", I_WARP % "Combat", "Archer build", "worn"), ("Mining", I_WARP % "Mining", "Iron Mining set", "1 missing"),
           ("Farming", I_WARP % "Farming", "Farming set", "ready"), ("Foraging", I_WARP % "Foraging", "Foraging set", "ready"),
           ("Fishing", I_WARP % "Fishing", "Fishing set", "ready"), ("Boss fight", I_EMB % "Archer", "custom", "ready"),
           ("Night caves", "px:torch", "custom", "2 missing")]
ST_COL = {"on": PAL["green"], "store": "#7cb6ff", "miss": PAL["red"]}


def state_mark(im, x, y, st):
    """corner mark on a slot: on you (check) / in Requip storage (box) / missing (x)"""
    grad_fill(im, (x, y, x + 17, y + 17), "#0a111e", "#0a111e", c=3)
    outline(im, (x, y, x + 17, y + 17), ST_COL[st], c=3)
    if st == "on":
        put(im, g_check(12, ST_COL[st]), x + 3, y + 3)
    elif st == "store":
        put(im, K.g_box(12, ST_COL[st]), x + 3, y + 3)
    else:
        put(im, g_x(11, ST_COL[st], 2.0), x + 3, y + 3)


def mannequin(w, h):
    from make_skill_pages import Art
    a = Art(w, h, 3)
    c, ol = "#2a3a56", "#4a6086"
    cx = w / 2
    a.glow(cx, h * 0.55, w * 0.35, h * 0.45, "#45a8ff", 60, 20)
    a.ell(cx, h * 0.14, w * 0.13, w * 0.13, c, ol, 1.5)
    a.rect((cx - w * 0.2, h * 0.27, cx + w * 0.2, h * 0.6), c, 10, ol, 1.5)
    for sx in (-1, 1):
        a.rect((cx + sx * w * 0.21 - (w * 0.08 if sx > 0 else 0), h * 0.28, cx + sx * w * 0.21 + (w * 0.08 if sx < 0 else 0), h * 0.55), c, 8, ol, 1.5)
        a.rect((cx + sx * w * 0.1 - w * 0.08, h * 0.6, cx + sx * w * 0.1 + w * 0.08, h * 0.95), c, 8, ol, 1.5)
    a.ell(cx, h * 0.98, w * 0.3, h * 0.02, ("#000000", 90))
    return a.done()


def make_requip():
    im, (WX0, WY0, WX1, WY1) = window_new("Inventory")
    X0, X1 = WX0 + 16, WX1 - 16
    Y0, Y1 = 86, 1020
    text(im, (X0, Y0 + 18), "INVENTORY  >", font("head", 14), A["hi"], "lm", track=1.2)
    bx = X0 + tw("INVENTORY  >", font("head", 14), 1.2) + 10
    paste_icon(im, I_HUB % "storage_requip", bx, Y0 - 2, 40)
    text(im, (bx + 48, Y0 + 18), "REQUIP", font("headb", 24), PAL["title"], "lm", track=2)
    x = bx + 48 + tw("REQUIP", font("headb", 24), 2) + 16
    chip(im, x, Y0 + 3, "Loadouts: armor, tools, hotbar, charms, pet, abilities", True)
    text(im, (X1, Y0 + 10), "Opened from the Inventory preset buttons (pencil)", font("bodyb", 14), A["hi"], "rm")
    text(im, (X1, Y0 + 28), "or a skill page's Requip button", font("body", 14), PAL["dim"], "rm")
    taper_line(im, X0, X1, Y0 + 50, PAL["gold"], 150, 0.85)
    T0 = Y0 + 62
    # ---- left: presets
    LX1 = X0 + 300
    panel(im, (X0, T0, LX1, Y1), "Presets")
    text(im, (LX1 - 14, T0 + 18), "7 / 10", font("headb", 14), PAL["xp"], "rm")
    yy = T0 + 38
    for i, (nm, ic, sub, st) in enumerate(PRESETS):
        if i == 5:
            sub_title(im, X0 + 14, yy + 12, "CUSTOM", LX1 - 14)
            yy += 26
        row(im, (X0 + 10, yy, LX1 - 10, yy + 62), "selected" if nm == "Mining" else "normal")
        slot(im, X0 + 18, yy + 7, "empty", None, ic, size=48)
        text(im, (X0 + 76, yy + 20), nm, font("headb", 16), "#ffffff", "lm")
        text(im, (X0 + 76, yy + 42), sub, font("body", 13), PAL["dim"], "lm")
        col = {"worn": A["hi"], "ready": PAL["green"]}.get(st, PAL["red"])
        text(im, (LX1 - 20, yy + 20), {"worn": "WORN"}.get(st, st), font("headb", 12), col, "rm")
        key_cap(im, LX1 - 40, yy + 34, str(i + 1), small=True) if i < 5 else None
        yy += 66
    button(im, (X0 + 14, yy + 10, LX1 - 14, yy + 44), "+ New preset", "secondary", fsize=15)
    text(im, (X0 + 14, Y1 - 40), "Keys 1-5 on the Inventory screen", font("body", 13), PAL["dim"], "lm")
    text(im, (X0 + 14, Y1 - 20), "swap a skill preset in one press.", font("body", 13), PAL["dim"], "lm")
    # ---- centre: the selected preset as a paper doll
    MX0, MX1 = LX1 + 12, LX1 + 12 + 760
    panel(im, (MX0, T0, MX1, Y1), "Mining preset")
    text(im, (MX1 - 14, T0 + 18), "per profile", font("body", 13), PAL["dim"], "rm")
    # legend
    lx = MX0 + 14
    for st, lab in (("on", "on you"), ("store", "in Requip storage"), ("miss", "missing")):
        state_mark(im, lx, T0 + 36, st)
        text(im, (lx + 24, T0 + 45), lab, font("body", 14), PAL["row"], "lm")
        lx += 40 + tw(lab, font("body", 14)) + 12
    # armor column + mannequin + tool / off-hand
    ay = T0 + 72
    arm = [("head", "Iron Mining Helmet", "Rare", "on"), ("chest", "Iron Mining Chestplate", "Rare", "on"),
           ("hands", "Iron Mining Gauntlets", "Unique", "store"), ("legs", "Iron Mining Greaves", "Normal", "miss")]
    for i, (pc, nm, rr, st) in enumerate(arm):
        y = ay + i * 84
        slot(im, MX0 + 14, y, "empty", K.RAR[rr] if st != "miss" else None, None, size=74)
        put_px = K.put_px
        if st != "miss":
            put_px(im, K.px_armor(pc), MX0 + 19, y + 5, 64)
        else:
            put_px(im, K.px_armor(pc, "#3a4658", "#26324a"), MX0 + 19, y + 5, 64)
        state_mark(im, MX0 + 14 + 54, y + 2, st)
        text(im, (MX0 + 100, y + 26), nm, font("bodyb", 15), mix(K.RAR[rr], "#ffffff", 0.2) if st != "miss" else PAL["red"], "lm")
        text(im, (MX0 + 100, y + 48), {"on": "on you", "store": "in Requip storage - Equip pulls it", "miss": "not found - last seen: Mining pocket"}[st],
             font("body", 13), ST_COL[st], "lm")
    man = mannequin(170, 330)
    im.paste(man, (MX0 + 360, ay), man)
    tx = MX1 - 210
    text(im, (tx, ay + 6), "TOOL", font("head", 12), PAL["dim"], "lm", track=1.3)
    slot(im, tx, ay + 18, "empty", None, None, size=74)
    K.put_px(im, px_icon("pickaxe"), tx + 5, ay + 23, 64)
    state_mark(im, tx + 54, ay + 20, "on")
    text(im, (tx + 84, ay + 46), "Copper Pickaxe", font("bodyb", 14), "#ffffff", "lm")
    text(im, (tx + 84, ay + 66), "Lv 14", font("headb", 13), PAL["xp"], "lm")
    text(im, (tx, ay + 120), "OFF-HAND", font("head", 12), PAL["dim"], "lm", track=1.3)
    slot(im, tx, ay + 132, "empty", None, None, size=74)
    K.put_px(im, px_icon("torch"), tx + 5, ay + 137, 64)
    state_mark(im, tx + 54, ay + 134, "on")
    text(im, (tx + 84, ay + 168), "Torch x32", font("bodyb", 14), "#ffffff", "lm")
    text(im, (tx, ay + 234), "PET  /  MOUNT", font("head", 12), PAL["dim"], "lm", track=1.3)
    slot(im, tx, ay + 246, "empty", RAR["Epic"], I_PET % "Goat", size=74)
    state_mark(im, tx + 54, ay + 248, "on")
    slot(im, tx + 82, ay + 246, "empty", RAR["Rare"], I_PET % "Horse", size=74)
    state_mark(im, tx + 136, ay + 248, "store")
    # hotbar
    hy = ay + 350
    sub_title(im, MX0 + 14, hy, "HOTBAR", MX1 - 14)
    hot = [("pickaxe", "on", None), ("shovel", "on", None), ("torch", "on", "32"), ("bread", "on", "12"), ("sword", "store", None),
           (None, None, None), ("chest", "on", "1"), (None, None, None), ("stew", "miss", None)]
    for i, (ic, st, cnt) in enumerate(hot):
        x = MX0 + 14 + i * 80
        slot(im, x, hy + 14, "empty", None, ("px:" + ic) if ic else None, size=74, count=cnt, keycap=str(i + 1))
        if st:
            state_mark(im, x + 54, hy + 16, st)
    # charms + abilities
    cy = hy + 108
    sub_title(im, MX0 + 14, cy, "CHARMS IN USE", MX0 + 360)
    for i, (k, r) in enumerate((("stonehide", "rare"), ("lantern", "unique"), ("speed", "rare"), ("health", "legendary"))):
        x = MX0 + 14 + i * 64
        slot(im, x, cy + 14, "empty", dict(K.GEAR_RARITY)[r.capitalize()], I_ACC % ("%s-%s" % (k, r)), size=56)
    state_mark(im, MX0 + 14 + 3 * 64 + 36, cy + 16, "on")
    sub_title(im, MX0 + 380, cy, "ABILITIES  (Archer)", MX1 - 14)
    for i, ab in enumerate(("RapidFire", "PinningShot", "HuntersNet", "ArrowRain")):
        x = MX0 + 380 + i * 64
        slot(im, x, cy + 14, "empty", None, K.I_ABI % ab, size=56)
    text(im, (MX0 + 380, cy + 88), "kept from your class loadout", font("body", 13), PAL["dim"], "lm")
    oy = cy + 120
    sub_title(im, MX0 + 14, oy, "WHEN I EQUIP THIS PRESET", MX1 - 14)
    for i, (lab, on) in enumerate((("Put what I take off into Requip storage", True), ("Pull missing gear from bags + Void", True),
                                   ("Also refill the hotbar (food, torches) from bags", True), ("Swap my class abilities too", False))):
        x = MX0 + 14 + (i % 2) * 372
        y = oy + 16 + (i // 2) * 40
        row(im, (x, y, x + 360, y + 34), "normal")
        text(im, (x + 10, y + 17), lab, font("body", 13), PAL["row"], "lm")
        K.toggle(im, x + 310, y + 6, on, w=40, h=22)
    # actions
    by = Y1 - 52
    button(im, (MX0 + 14, by, MX0 + 230, by + 38), "Equip Mining", "primary", fsize=17)
    button(im, (MX0 + 240, by, MX0 + 470, by + 38), "Save from what I wear", "secondary", fsize=14)
    button(im, (MX0 + 480, by, MX0 + 590, by + 38), "Rename", "secondary", fsize=14)
    button(im, (MX0 + 600, by, MX1 - 14, by + 38), "Delete", "danger", fsize=14)
    # ---- right: hints + Requip storage
    RX0 = MX1 + 12
    panel(im, (RX0, T0, X1, T0 + 330), "Smart hints")
    hints = [("miss", "Iron Mining Greaves are not on you", "Last seen in your Mining pocket.", "Pull it"),
             ("better", "Better helmet in Requip storage", "Rare Iron Mining Helmet +3 Fortune", "Swap"),
             ("miss", "Hotbar 9: Hearty Stew - you have 0", "Cook more or pick another food.", None),
             ("store", "Mount (Horse) is in Requip storage", "Equip puts it in your mount slot.", None)]
    yy = T0 + 38
    for kind, t1, t2, btn in hints:
        row(im, (RX0 + 10, yy, X1 - 10, yy + 64), "normal")
        if kind == "better":
            put(im, K.g_arrows(16, PAL["green"], up=True), RX0 + 18, yy + 12)
        else:
            state_mark(im, RX0 + 16, yy + 10, kind)
        text(im, (RX0 + 44, yy + 19), t1, font("bodyb", 14), "#ffffff", "lm")
        text(im, (RX0 + 44, yy + 40), t2, font("body", 13), PAL["green"] if kind == "better" else PAL["dim"], "lm")
        if btn:
            button(im, (X1 - 84, yy + 30, X1 - 18, yy + 56), btn, "green" if kind == "better" else "primary", fsize=12)
        yy += 70
    panel(im, (RX0, T0 + 340, X1, Y1), "Requip storage")
    text(im, (X1 - 14, T0 + 358), "18 / 45", font("headb", 14), PAL["xp"], "rm")
    search_box(im, (RX0 + 12, T0 + 376, X1 - 12, T0 + 404), "Search stored gear")
    store = [("head", "Rare", "Mining"), ("hands", "Unique", "Mining"), ("chest", "Unique", "Farming"), ("legs", "Unique", "Farming"),
             ("head", "Rare", "Foraging"), ("chest", "Rare", "Foraging"), ("hands", "Normal", "Fishing"), ("legs", "Normal", "Fishing"),
             ("sword", "Rare", "Combat"), ("pet", "Rare", "Mining"), ("head", "Normal", None), ("chest", "Normal", None)]
    sx0, sy0 = RX0 + 14, T0 + 416
    for i in range(20):
        x = sx0 + (i % 5) * 62
        y = sy0 + (i // 5) * 78
        if i < len(store):
            pc, rr, used = store[i]
            if pc == "pet":
                slot(im, x, y, "empty", K.RAR["Rare"], I_PET % "Horse", size=56)
            elif pc == "sword":
                slot(im, x, y, "empty", K.RAR[rr], "px:sword", size=56)
            else:
                slot(im, x, y, "selected" if i == 0 else "empty", K.RAR[rr], None, size=56)
                K.put_px(im, K.px_armor(pc, {"Mining": "#b8c4d0", "Farming": "#d9b84a", "Foraging": "#8a6a3a", "Fishing": "#6fb7e8"}.get(used, "#9aa6b4")),
                         x + 4, y + 4, 48)
            if used:
                text(im, (x + 28, y + 62), used, font("body", 11), PAL["dim"], "mm")
        else:
            slot(im, x, y, "empty", None, None, size=56)
    by2 = Y1 - 48
    button(im, (RX0 + 14, by2, RX0 + 120, by2 + 32), "Take out", "secondary", fsize=13)
    button(im, (RX0 + 128, by2, RX0 + 234, by2 + 32), "Salvage", "danger", fsize=13)
    button(im, (RX0 + 242, by2, X1 - 14, by2 + 32), "Auto-store: ON", "secondary", fsize=13)
    footer(im, [("LMB", "Select"), ("1-5", "Equip a preset"), ("Drag", "Gear into a slot"), ("Tab / Esc", "Close")])
    return im



# ================================================================================================================ inventory panels (v5 screen)
def _inventory_with(panel_fn, highlight):
    """Draw the approved v5 inventory screen (make_ui_theme.make_mockup_v3(.., v4=True)) with its top-middle crafting panel replaced by
    panel_fn(im, X0, X1, Y0, Y1); the new 7-tab bar; the Craft / pocket tabs below show nothing selected. Monkeypatches are undone."""
    saved = (K.furnace_v4, K.TABS_V4, K.hang_tabs, K.requip_row)
    orig_hang, orig_req = K.hang_tabs, K.requip_row

    def hang(im, x0, y0, x1, h, items, sel, fsize=16):
        return orig_hang(im, x0, y0, x1, h, items, -1, fsize)

    def req(im, x0, y0, x1, active):
        orig_req(im, x0, y0, x1, active)
        if highlight == "requip":   # the pencil is ON: this panel edits presets
            ew = 30
            box = (x1 - ew + 1, y0 + 7, x1, y0 + 38)
            glow(im, box, A["base"], 5, 200, 5, 2)
            button(im, box, "", "primary", glyph=K.g_pencil(14, "#ffffff"))
    try:
        K.furnace_v4 = panel_fn
        K.TABS_V4 = NEW_TABS
        K.hang_tabs = hang
        K.requip_row = req
        im = K.make_mockup_v3("furnace", True)
    finally:
        K.furnace_v4, K.TABS_V4, K.hang_tabs, K.requip_row = saved
    if highlight == "charms":   # the charm row's 'All charms' link is ON
        lx1 = 138 + 16 + 420
        vy = 86 + 62 + 4 * 92 + 2
        grad_fill(im, (lx1 - 128, vy - 2, lx1 - 14, vy + 22), mix(A["base"], "#111b2d", 0.6), mix(A["base"], "#111b2d", 0.8), c=4)
        outline(im, (lx1 - 128, vy - 2, lx1 - 14, vy + 22), A["base"], c=4)
        text(im, (lx1 - 30, vy + 10), "All charms", font("head", 14), "#ffffff", "rm")
        put(im, g_chev(13, "#ffffff"), lx1 - 28, vy + 4)
    return im


def requip_panel(im, X0, X1, Y0, Y1):
    panel(im, (X0, Y0, X1, Y1), "Requip  -  editing Mining")
    text(im, (X1 - 110, Y0 + 18), "drag gear in from the bag", font("body", 13), PAL["dim"], "rm")
    button(im, (X1 - 98, Y0 + 6, X1 - 12, Y0 + 30), "Done", "secondary", fsize=13)
    # presets
    px1 = X0 + 168
    yy = Y0 + 36
    for i, (nm, ic, sub, st) in enumerate(PRESETS):
        sel = nm == "Mining"
        row(im, (X0 + 10, yy, px1, yy + 31), "selected" if sel else "normal")
        paste_icon(im, ic, X0 + 16, yy + 4, 22)
        text(im, (X0 + 44, yy + 16), nm, font("headb", 13), "#ffffff" if sel else PAL["row"], "lm")
        col = {"worn": A["hi"], "ready": PAL["green"]}.get(st, PAL["red"])
        text(im, (px1 - 6, yy + 16), {"worn": "WORN", "1 missing": "1 miss", "2 missing": "2 miss"}.get(st, st), font("headb", 11), col, "rm")
        yy += 34
    button(im, (X0 + 10, yy + 2, px1, yy + 28), "+ New preset", "secondary", fsize=12)
    # selected preset slots
    sx0 = px1 + 14
    lx = sx0
    for st, lab in (("on", "on you"), ("store", "in storage"), ("miss", "missing")):
        state_mark(im, lx, Y0 + 38, st)
        text(im, (lx + 22, Y0 + 47), lab, font("body", 12), PAL["row"], "lm")
        lx += 30 + tw(lab, font("body", 12)) + 10
    ay = Y0 + 64
    arm = [("head", "Rare", "store"), ("chest", "Rare", "store"), ("hands", "Unique", "store"), ("legs", "Normal", "miss")]
    for i, (pc, rr, st) in enumerate(arm):
        x = sx0 + i * 60
        slot(im, x, ay, "empty", K.RAR[rr] if st != "miss" else None, None, size=56)
        K.put_px(im, K.px_armor(pc) if st != "miss" else K.px_armor(pc, "#3a4658", "#26324a"), x + 4, ay + 4, 48)
        state_mark(im, x + 38, ay + 2, st)
    x = sx0 + 4 * 60 + 10
    slot(im, x, ay, "empty", None, None, size=56)
    K.put_px(im, px_icon("pickaxe"), x + 4, ay + 4, 48)
    state_mark(im, x + 38, ay + 2, "store")
    slot(im, x + 60, ay, "empty", RAR["Epic"], I_PET % "Goat", size=56)
    state_mark(im, x + 98, ay + 2, "store")
    text(im, (sx0, ay + 70), "Armor - tool - pet", font("body", 12), PAL["dim"], "lm")
    hy = ay + 86
    hot = [("pickaxe", "store"), ("shovel", "on"), ("torch", "on"), ("bread", "on"), ("sword", "on"), (None, None), ("chest", "on"), (None, None), ("stew", "miss")]
    for i, (ic, st) in enumerate(hot):
        x = sx0 + i * 40
        slot(im, x, hy, "empty", None, ("px:" + ic) if ic else None, size=36)
        if st:
            state_mark(im, x + 22, hy - 4, st)
    text(im, (sx0, hy + 48), "Hotbar", font("body", 12), PAL["dim"], "lm")
    cy = hy + 62
    for i, (k, r) in enumerate((("stonehide", "rare"), ("lantern", "unique"), ("speed", "rare"), ("health", "legendary"))):
        slot(im, sx0 + i * 44, cy, "empty", dict(K.GEAR_RARITY)[r.capitalize()], I_ACC % ("%s-%s" % (k, r)), size=40)
    for i, ab in enumerate(("RapidFire", "PinningShot", "HuntersNet", "ArrowRain")):
        slot(im, sx0 + 192 + i * 44, cy, "empty", None, K.I_ABI % ab, size=40)
    text(im, (sx0, cy + 52), "Charms", font("body", 12), PAL["dim"], "lm")
    text(im, (sx0 + 192, cy + 52), "Abilities (off: class loadout stays)", font("body", 12), PAL["dim"], "lm")
    # hints + actions (right)
    hx0 = sx0 + 4 * 60 + 10 + 132
    yy = Y0 + 64
    for kind, t1, t2 in (("miss", "Greaves not on you", "last seen: Mining pocket"), ("better", "Better helmet in storage", "+3 Fortune - Swap"),
                         ("miss", "Hearty Stew: 0 left", "cook more")):
        if kind == "better":
            put(im, K.g_arrows(14, PAL["green"], up=True), hx0, yy + 2)
        else:
            state_mark(im, hx0 - 2, yy, kind)
        text(im, (hx0 + 22, yy + 8), t1, font("bodyb", 13), "#ffffff", "lm")
        text(im, (hx0 + 22, yy + 26), t2, font("body", 12), PAL["green"] if kind == "better" else PAL["dim"], "lm")
        yy += 46
    button(im, (hx0 - 2, yy + 2, X1 - 12, yy + 32), "Equip Mining", "primary", fsize=15)
    button(im, (hx0 - 2, yy + 38, X1 - 12, yy + 64), "Save from what I wear", "secondary", fsize=12)
    button(im, (hx0 - 2, yy + 70, X1 - 12, yy + 96), "Rename", "secondary", fsize=12)
    # requip storage strip
    sy = Y1 - 66
    sub_title(im, X0 + 14, sy - 10, "REQUIP STORAGE  18 / 45", X1 - 14)
    store = [("head", "Rare"), ("hands", "Unique"), ("chest", "Unique"), ("legs", "Unique"), ("head", "Rare"), ("chest", "Rare"), ("hands", "Normal"),
             ("legs", "Normal"), ("sword", "Rare"), ("pet", "Rare"), ("head", "Normal"), ("chest", "Normal")]
    for i in range(14):
        x = X0 + 14 + i * 46
        if i < len(store):
            pc, rr = store[i]
            if pc == "pet":
                slot(im, x, sy + 4, "empty", K.RAR[rr], I_PET % "Horse", size=42)
            elif pc == "sword":
                slot(im, x, sy + 4, "empty", K.RAR[rr], "px:sword", size=42)
            else:
                slot(im, x, sy + 4, "empty", K.RAR[rr], None, size=42)
                K.put_px(im, K.px_armor(pc), x + 5, sy + 9, 32)
        else:
            slot(im, x, sy + 4, "empty", None, None, size=42)
    button(im, (X1 - 82, sy + 6, X1 - 12, sy + 30), "Take out", "secondary", fsize=12)
    button(im, (X1 - 82, sy + 34, X1 - 12, sy + 56), "Salvage", "danger", fsize=12)


def charms_panel(im, X0, X1, Y0, Y1):
    panel(im, (X0, Y0, X1, Y1), "Void charms  13 / 23")
    rich(im, X0 + 240, Y0 + 18, [("Bag ", font("body", 13), PAL["dim"]), ("Rare", font("headb", 14), dict(K.GEAR_RARITY)["Rare"]),
                                 (" x1.20 power", font("bodyb", 13), PAL["green"])])
    button(im, (X1 - 196, Y0 + 6, X1 - 106, Y0 + 30), "Upgrade bag", "secondary", fsize=12)
    button(im, (X1 - 98, Y0 + 6, X1 - 12, Y0 + 30), "Done", "secondary", fsize=13)
    items = [(k, OWN[k]) for k, _n, _s in CHARM_LINES] + [("speed", "unique"), ("health", "rare")]
    gx0, gy0 = X0 + 14, Y0 + 40
    for i in range(24):
        x = gx0 + (i % 8) * 56
        y = gy0 + (i // 8) * 58
        if i < len(items):
            k, r = items[i]
            dup = i >= len(CHARM_LINES)
            slot(im, x, y, "selected" if k == "lantern" and not dup else "empty", dict(K.GEAR_RARITY)[r.capitalize()],
                 I_ACC % ("%s-%s" % (k, r)), size=52, dim=dup)
            if dup:
                state_mark(im, x + 2, y + 32, "miss")
        elif i < 23:
            slot(im, x, y, "empty", None, None, size=52)
        else:
            slot(im, x, y, "empty", None, None, size=52)
            put(im, g_lock(16, "#5a6a80"), x + 18, y + 18)
    text(im, (gx0, gy0 + 3 * 58 + 8), "Best of each line counts; red x = duplicate. Drag charms in.", font("body", 12), PAL["dim"], "lm")
    # selected charm (right)
    sx0 = gx0 + 8 * 56 + 10
    grad_fill(im, (sx0, Y0 + 40, X1 - 12, Y0 + 262), "#0e1729", "#0a111e", c=6)
    outline(im, (sx0, Y0 + 40, X1 - 12, Y0 + 262), "#2b3d5b", c=6)
    slot(im, sx0 + 10, Y0 + 50, "empty", dict(K.GEAR_RARITY)["Unique"], I_ACC % "lantern-unique", size=52)
    text(im, (sx0 + 72, Y0 + 66), "Unique Lantern", font("headb", 16), dict(K.GEAR_RARITY)["Unique"], "lm")
    text(im, (sx0 + 72, Y0 + 86), "+3 Light radius", font("bodyb", 13), PAL["green"], "lm")
    text(im, (sx0 + 10, Y0 + 120), "TIER UP  ->  Rare  (+4 Light)", font("head", 12), PAL["xp"], "lm", track=1)
    yy = Y0 + 140
    for lab, ok in (("this Unique Lantern", True), ("64 Tree Sap", True), ("16 Ench. Iron  (need 9)", False), ("2,500 coins", True)):
        put(im, g_check(12, PAL["green"]) if ok else g_x(12, PAL["red"], 2.0), sx0 + 10, yy - 6)
        text(im, (sx0 + 28, yy), lab, font("body", 13), PAL["green"] if ok else PAL["red"], "lm")
        yy += 19
    button(im, (sx0 + 10, Y0 + 226, sx0 + 120, Y0 + 254), "Tier up", "primary", "disabled", fsize=13)
    button(im, (sx0 + 128, Y0 + 226, X1 - 22, Y0 + 254), "Merge 3", "secondary", "disabled", fsize=13)
    # totals
    ty = Y0 + 272
    sub_title(im, X0 + 14, ty, "ALL CHARMS TOGETHER", X1 - 14)
    tot = [("Health", "+62"), ("Stamina", "+18"), ("Mana", "+12%"), ("Speed", "+9%"), ("Regen", "1.4/2s"), ("Strength", "+14"),
           ("Magic", "+4"), ("Defense", "+22"), ("Crit", "+7%"), ("Fall dmg", "-40%"), ("Light", "+3")]
    cw = (X1 - X0 - 28) // 4
    for i, (n_, v) in enumerate(tot):
        x = X0 + 14 + (i % 4) * cw
        y = ty + 22 + (i // 4) * 26
        row(im, (x, y - 11, x + cw - 6, y + 11), "normal")
        text(im, (x + 8, y), n_, font("body", 13), PAL["row"], "lm")
        text(im, (x + cw - 14, y), v, font("bold", 13), PAL["green"], "rm")


def make_inv_requip():
    return _inventory_with(requip_panel, "requip")


def make_inv_charms():
    return _inventory_with(charms_panel, "charms")



def _v1(fn):
    global V2
    V2 = False
    try:
        return fn()
    finally:
        V2 = True



def main():
    out = {"tab-plan.png": make_tab_plan, "tab-plan-v1.png": lambda: _v1(make_tab_plan), "pets-page.png": make_pets,
           "market-page.png": make_market, "world-page.png": make_world, "social-page.png": make_social, "settings-page.png": make_settings,
           "world-page-v1.png": lambda: make_world(False),
           "charms-page-v1.png": make_charms, "requip-page-v1.png": make_requip,
           "inventory-mockup-requip.png": make_inv_requip, "inventory-mockup-charms.png": make_inv_charms}
    only = sys.argv[1:]
    for fn, maker in out.items():
        if only and fn not in only:
            continue
        im = maker()
        im.save(os.path.join(HERE, fn), optimize=True)
        print("wrote", fn, im.size)


if __name__ == "__main__":
    main()
