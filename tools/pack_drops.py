"""pack_drops - THE pack drop table: which OTHER mods' armor / weapons drop from our mobs with SkyyGear's modifiers, per ZONE x WEIGHT
(armor: Heavy / Light / Cloth) or per WEAPON TYPE, and in which ROLE (normal drop, Untiered candidate, Mythic boss drop).
Spec: research/Pack-Drops-Spec.md. Read by the SkyyGear build (SkyyGear/build_skyygear_0.3.19.py: `import pack_drops as PKD`), so a table
change here reaches the jar at the next build without a new patch. Pure Python; ids only - nothing of another mod is read at import.

Skyy 2026-10-17 (docs/answered/gear.md "PACK ARMOR AS MOB DROPS", "PACK WEAPONS TOO", "ARMOR SETS FILL", "UT SCOPE", "ZONE TIERS CORRECTION"):
"lets build the arcane robes and armory into the mod so you drop from enemy's with our modifiers next" + "and the weapons too" + "fewer at
lower tiers on the normal drops keep 2 ut but do 1 mythic. and UT and mythic can reuse looks BUT enhanced (if we can.) ... save the coolest
armor and weapons for mythic" + "UT and mythic per zone! not tier. always make the UT and mythic the highest tier of that zone" + "all
combat gear is still drops only. and all Ut and mythic are combat gear".

LICENCE RULES (PROJECT-RULES 2, PACK.md): our code only REACTS to these ids at runtime (this table + our own drop roll + our own
modifiers). We never copy or ship their models, textures, recipes, stat numbers or lang texts, never override their ids, never recolour
their sets without the author's OK. A source is used only when its status is "on": today The Armory (LadyPaladra, CC BY-NC 3.0: credit,
never sold). Void Armor (Aipoc76, CC BY-NC 3.0) is allowed but its ids were never scanned ("needs-ids"). Every other source waits for
its author's OK ("todo"): no id of a todo / needs-ids source is ever written into a jar.

IDS: The Armory ids come from the read-only 2026-10-08 scan of TheArmoryMod-1.22.0.jar (research/Pack-Armor-Plan.md Appendix A / B,
1.3). RE-CHECKED 2026-10-17 (local rebuild of PR #17) on TheArmoryMod-1.23.0.jar with `--scan` (Parent chain followed): all 1,286 table
ids are still there, every armor row's ArmorSlot is a real slot, every weapon row's item has a Weapon part (most only through
"Parent": "Template_Weapon_<Type>" - the vanilla template's Weapon part; longswords / flails / Elemental / Rune Blade carry their own),
and the templates match the row kinds (Sword / Daggers / Mace / Battleaxe; Rune Blade stage 2 = Battleaxe, stage 3 = Mace, both off).
New in 1.23.0, deliberately NOT in the table: KanohiHau + 8 colours (an Armor part with no ArmorSlot / ItemLevel - unfinished),
EmptySign / HateKweebecSign / LoveKweebecSign (Lv 8 joke maces), TestBroom (a test item). A missing id is harmless: SkyyGear skips every
id whose item is not in the live item map (The Armory switched off = no Armory drops, nothing breaks). Re-check with `--scan <jar>`.

ROLES (spec section 2):
    drop    normal mob drop: joins SkyyGear's mystery-bag pool at its tier's level band (picked BY SET: a set weighs like one vanilla item,
            split over its pieces of the bag's slot, x loot.packWeight)
    ut      Untiered candidate: kept OUT of the normal bags (UT = special, never crafted); it becomes a real Untiered item the moment an
            admin / a later round adds its `ut.<id>` + `utfx.<id>` rows (SkyyGear's existing Untiered table - each UT needs Skyy's fixed
            lines + one trade-off, and an id a recipe makes is refused there). Nothing drops from a ut row before that.
    mythic  Mythic boss drop of its zone: only a boss kill (SkyyMobs mob:fn:boss) rolls it, as a Mythic mystery bag that identifies into
            one of the zone's Mythic pieces. Never in normal bags.
    off     listed, never used (the note says why)
TIERS / ZONES: tier = the level.material row word of SkyyGear (crude ... onyxium) = the item's level band (an admin moves it in Server
Setup -> Gear -> Levels). Zone = Skyy's zone metals (research/Zone-Tiers-Idea.md 2026-10-17 table; zone 1 goes through Iron): Crude / Copper /
Iron = 1, Thorium = 2, Cobalt = 3, Adamantite = 4, Mithril / Onyxium = 5. UT and Mythic sit at their zone's TOP tier (asserted).

CLI (run from the repo root):
    python tools/pack_drops.py            the grid (zone x weight / type, roles), counts, self-checks
    python tools/pack_drops.py --md       the same grid as markdown (research/Pack-Drops-Spec.md section 3)
    python tools/pack_drops.py --scan <mod jar or zip> [...]
                                          READ-ONLY list of the armor / weapon item ids inside a mod archive (id, armor slot, item level,
                                          and whether a row here has it) - for filling "needs-ids" rows and re-checking The Armory after an
                                          update. Prints ids only; never copies anything out of the archive.
"""
import os
import sys
import json
import zipfile

ZONES = [(1, "iron"), (2, "thorium"), (3, "cobalt"), (4, "adamantite"), (5, "mithril")]        # (zone, its TOP combat tier)
TIER_ZONE = {"crude": 1, "copper": 1, "iron": 1, "thorium": 2, "cobalt": 3, "adamantite": 4, "mithril": 5, "onyxium": 5}
TIER_WORD = {"crude": "Crude", "copper": "Copper", "iron": "Iron", "thorium": "Thorium", "cobalt": "Cobalt", "adamantite": "Adamantite",
             "mithril": "Mithril", "onyxium": "Onyxium"}
WEIGHTS = ["Heavy", "Light", "Cloth"]            # SkyyGear GearPool.AT_NAME index 1, 2, 3
ROLES = ["drop", "ut", "mythic", "off"]          # SkyyGear GearPool.P_ROLE 0, 1, 2 (off rows are never written into the jar)
WEAPON_TYPES = ["Weapon_Sword", "Weapon_Longsword", "Weapon_Daggers", "Weapon_Mace", "Weapon_Battleaxe", "Weapon_Club", "Weapon_Axe",
                "Weapon_Spear", "Weapon_Shortbow", "Weapon_Crossbow", "Weapon_Staff", "Weapon_Spellbook", "Weapon_Wand"]   # bag type keys

SOURCES = {
    "armory": dict(mod="The Armory", key="LadyPaladra:TheArmory", author="LadyPaladra (team: Larsonix, S3B4S5C, ScarForges)",
                   licence="CC BY-NC 3.0 (CurseForge FAQ): credit, never sold", status="on",
                   note="PACK.md row; ids from the 2026-10-08 scan of 1.22.0, re-checked on 1.23.0 (2026-10-17)"),
    "voidarmor": dict(mod="Void Armor & Weapons", key="?", author="Aipoc76", licence="CC BY-NC 3.0: credit, never sold", status="needs-ids",
                      note="allowed, but not in Skyy's Mods folder (checked 2026-10-17: the Void* mods there are Void Asylum, VoidProtect and Vort's Voidcloak Armory - other authors) and never scanned: fill ids with --scan, add a PACK.md row, then status on"),
    "slvr": dict(mod="SLVR Arcane Robes & Spells", key="?", author="SlverSkull", licence="none stated = All Rights Reserved",
                 status="todo", note="waits for SlverSkull's OK (ask list, RESUME NEXT 3)"),
    "fyrrage_fk": dict(mod="Fantastic Knight Armor Pack", key="?", author="Fyrrage", licence="All Rights Reserved", status="todo",
                       note="waits for Fyrrage's OK; loot-only sets (fits drops); ids not scanned"),
    "fyrrage_out": dict(mod="Outlanders Armor Pack", key="?", author="Fyrrage", licence="All Rights Reserved", status="todo",
                        note="waits for Fyrrage's OK; ids not scanned"),
    "elemental": dict(mod="Elemental Knights Pack", key="?", author="(Elemental Knights author)", licence="All Rights Reserved",
                      status="todo", note="waits for the author's OK; ids not scanned (it has an id Migrator: ids changed once)"),
    "stonedturtle": dict(mod="Ninja / Blood Armor / Magical Armor Set", key="?", author="stonedturtle", licence="All Rights Reserved",
                         status="todo", note="waits for stonedturtle's OK (one message for all three); ids not scanned"),
}

# The Armory ids (read-only scan 2026-10-08 of TheArmoryMod-1.22.0.jar = research/Pack-Armor-Plan.md Appendix A + B; ids only; all present in 1.23.0)
ARMORY_IDS = {
    'Academy': [
        'AcademyHat', 'BlackAcademyHat', 'BlackWizenedJacket', 'BlackWizenedSleeves', 'BlueWizenedJacket', 'BlueWizenedSleeves',
        'BrownAcademyHat', 'BrownWizenedJacket', 'BrownWizenedSleeves', 'GreenAcademyHat', 'GreenWizenedJacket', 'GreenWizenedSleeves',
        'PinkAcademyHat', 'PinkWizenedJacket', 'PinkWizenedSleeves', 'PurpleAcademyHat', 'PurpleWizenedJacket', 'PurpleWizenedSleeves',
        'RedAcademyHat', 'RedWizenedJacket', 'RedWizenedSleeves', 'WhiteAcademyHat', 'WhiteWizenedJacket', 'WhiteWizenedSleeves',
        'YellowAcademyHat', 'YellowWizenedJacket', 'YellowWizenedSleeves'
    ],
    'Skull Masks': [
        'Alt1_SkullMaskBlack', 'Alt1_SkullMaskBlue', 'Alt1_SkullMaskCyan', 'Alt1_SkullMaskDarkBlue', 'Alt1_SkullMaskDarkCyan',
        'Alt1_SkullMaskDarkGreen', 'Alt1_SkullMaskDarkMagenta', 'Alt1_SkullMaskDarkPurple', 'Alt1_SkullMaskDarkRed',
        'Alt1_SkullMaskDarkWhite', 'Alt1_SkullMaskDarkYellow', 'Alt1_SkullMaskGreen', 'Alt1_SkullMaskMagenta', 'Alt1_SkullMaskPurple',
        'Alt1_SkullMaskRed', 'Alt1_SkullMaskYellow', 'Alt2_SkullMaskBlack', 'Alt2_SkullMaskBlue', 'Alt2_SkullMaskCyan',
        'Alt2_SkullMaskDarkBlue', 'Alt2_SkullMaskDarkCyan', 'Alt2_SkullMaskDarkGreen', 'Alt2_SkullMaskDarkMagenta',
        'Alt2_SkullMaskDarkPurple', 'Alt2_SkullMaskDarkRed', 'Alt2_SkullMaskDarkWhite', 'Alt2_SkullMaskDarkYellow', 'Alt2_SkullMaskGreen',
        'Alt2_SkullMaskMagenta', 'Alt2_SkullMaskPurple', 'Alt2_SkullMaskRed', 'Alt2_SkullMaskYellow', 'Alt3_SkullMaskBlack',
        'Alt3_SkullMaskBlue', 'Alt3_SkullMaskCyan', 'Alt3_SkullMaskDarkBlue', 'Alt3_SkullMaskDarkCyan', 'Alt3_SkullMaskDarkGreen',
        'Alt3_SkullMaskDarkMagenta', 'Alt3_SkullMaskDarkPurple', 'Alt3_SkullMaskDarkRed', 'Alt3_SkullMaskDarkWhite',
        'Alt3_SkullMaskDarkYellow', 'Alt3_SkullMaskGreen', 'Alt3_SkullMaskMagenta', 'Alt3_SkullMaskPurple', 'Alt3_SkullMaskRed',
        'Alt3_SkullMaskYellow', 'SkullMask', 'SkullMaskBlack', 'SkullMaskBlue', 'SkullMaskCyan', 'SkullMaskGreen', 'SkullMaskMagenta',
        'SkullMaskPurple', 'SkullMaskRed', 'SkullMaskWhite'
    ],
    'Vanilla Recolor Iron': [
        'Armor_Iron_Chest_Black', 'Armor_Iron_Chest_Black_Alt', 'Armor_Iron_Chest_Black_Fab', 'Armor_Iron_Chest_Blue',
        'Armor_Iron_Chest_Blue_Alt', 'Armor_Iron_Chest_Blue_Fab', 'Armor_Iron_Chest_Cyan', 'Armor_Iron_Chest_Cyan_Alt',
        'Armor_Iron_Chest_Cyan_Fab', 'Armor_Iron_Chest_Green', 'Armor_Iron_Chest_Green_Alt', 'Armor_Iron_Chest_Green_Fab',
        'Armor_Iron_Chest_Magenta', 'Armor_Iron_Chest_Magenta_Alt', 'Armor_Iron_Chest_Magenta_Fab', 'Armor_Iron_Chest_Purple',
        'Armor_Iron_Chest_Purple_Alt', 'Armor_Iron_Chest_Purple_Fab', 'Armor_Iron_Chest_Red', 'Armor_Iron_Chest_Red_Alt',
        'Armor_Iron_Chest_Rusty', 'Armor_Iron_Chest_Stone', 'Armor_Iron_Chest_White', 'Armor_Iron_Chest_White_Alt',
        'Armor_Iron_Chest_White_Fab', 'Armor_Iron_Chest_Yellow', 'Armor_Iron_Chest_Yellow_Alt', 'Armor_Iron_Chest_Yellow_Fab',
        'Armor_Iron_Hands_Black', 'Armor_Iron_Hands_Black_Alt', 'Armor_Iron_Hands_Blue', 'Armor_Iron_Hands_Blue_Alt', 'Armor_Iron_Hands_Cyan',
        'Armor_Iron_Hands_Cyan_Alt', 'Armor_Iron_Hands_Green', 'Armor_Iron_Hands_Green_Alt', 'Armor_Iron_Hands_Magenta',
        'Armor_Iron_Hands_Magenta_Alt', 'Armor_Iron_Hands_Purple', 'Armor_Iron_Hands_Purple_Alt', 'Armor_Iron_Hands_Red',
        'Armor_Iron_Hands_Red_Alt', 'Armor_Iron_Hands_Rusty', 'Armor_Iron_Hands_Stone', 'Armor_Iron_Hands_White',
        'Armor_Iron_Hands_White_Alt', 'Armor_Iron_Hands_Yellow', 'Armor_Iron_Hands_Yellow_Alt', 'Armor_Iron_Head_Black',
        'Armor_Iron_Head_Black_Alt', 'Armor_Iron_Head_Blue', 'Armor_Iron_Head_Blue_Alt', 'Armor_Iron_Head_Cyan', 'Armor_Iron_Head_Cyan_Alt',
        'Armor_Iron_Head_Green', 'Armor_Iron_Head_Green_Alt', 'Armor_Iron_Head_Magenta', 'Armor_Iron_Head_Magenta_Alt',
        'Armor_Iron_Head_Purple', 'Armor_Iron_Head_Purple_Alt', 'Armor_Iron_Head_Red', 'Armor_Iron_Head_Red_Alt', 'Armor_Iron_Head_Rusty',
        'Armor_Iron_Head_Stone', 'Armor_Iron_Head_White', 'Armor_Iron_Head_White_Alt', 'Armor_Iron_Head_Yellow', 'Armor_Iron_Head_Yellow_Alt',
        'Armor_Iron_Legs_Black', 'Armor_Iron_Legs_Black_Alt', 'Armor_Iron_Legs_Black_Fab', 'Armor_Iron_Legs_Blue', 'Armor_Iron_Legs_Blue_Alt',
        'Armor_Iron_Legs_Blue_Fab', 'Armor_Iron_Legs_Cyan', 'Armor_Iron_Legs_Cyan_Alt', 'Armor_Iron_Legs_Cyan_Fab', 'Armor_Iron_Legs_Green',
        'Armor_Iron_Legs_Green_Alt', 'Armor_Iron_Legs_Green_Fab', 'Armor_Iron_Legs_Magenta', 'Armor_Iron_Legs_Magenta_Alt',
        'Armor_Iron_Legs_Magenta_Fab', 'Armor_Iron_Legs_Purple', 'Armor_Iron_Legs_Purple_Alt', 'Armor_Iron_Legs_Purple_Fab',
        'Armor_Iron_Legs_Red', 'Armor_Iron_Legs_Red_Alt', 'Armor_Iron_Legs_Red_Fab', 'Armor_Iron_Legs_Rusty', 'Armor_Iron_Legs_Stone',
        'Armor_Iron_Legs_White', 'Armor_Iron_Legs_White_Alt', 'Armor_Iron_Legs_White_Fab', 'Armor_Iron_Legs_Yellow',
        'Armor_Iron_Legs_Yellow_Alt', 'Armor_Iron_Legs_Yellow_Fab'
    ],
    'Amulets': [
        'BlueAmulet', 'BlueAmuletHead', 'GreenAmulet', 'GreenAmuletHead', 'PurpleAmulet', 'PurpleAmuletHead', 'YellowAmulet',
        'YellowAmuletHead'
    ],
    'Crowns': [
        'BlueCrown', 'BlueCrownAlt', 'BlueCrownEvil', 'GreenCrown', 'GreenCrownAlt', 'GreenCrownEvil', 'IronCrown', 'IronCrownAlt',
        'IronCrownBlueDiadem', 'IronCrownBlueDiademAlt', 'IronCrownEvil', 'IronCrownGreenDiadem', 'IronCrownGreenDiademAlt',
        'IronCrownGreenDiademEvil', 'IronCrownPurpleDiadem', 'IronCrownPurpleDiademAlt', 'IronCrownPurpleDiademEvil', 'IronCrownRedDiadem',
        'IronCrownRedDiademAlt', 'IronCrownRedDiademEvil', 'IronCrownYellowDiadem', 'IronCrownYellowDiademAlt', 'IronCrownYellowDiademEvil',
        'LichCrown', 'LichCrownAlt', 'LichCrownEvil', 'PurpleCrown', 'PurpleCrownAlt', 'PurpleCrownEvil', 'RedCrown', 'RedCrownAlt',
        'RedCrownEvil', 'RustedCrown', 'RustedCrownAlt', 'RustedCrownEvil', 'WhiteCrown', 'WhiteCrownAlt', 'WhiteCrownEvil', 'YellowCrown',
        'YellowCrownAlt', 'YellowCrownEvil'
    ],
    'Bramblekin': [
        'BramblekinBracers', 'BramblekinMask'
    ],
    'Daemon': [
        'CyclopsHelm', 'CyclopsHelmCyan', 'CyclopsHelmOpened', 'CyclopsHelmOpenedCyan', 'CyclopsHelmOpenedPurple', 'CyclopsHelmPurple',
        'DemonChestplate', 'DemonChestplateCyan', 'DemonChestplatePurple', 'DemonGauntlets', 'DemonGauntletsCyan', 'DemonGauntletsPurple',
        'DemonHelm', 'DemonHelmCyan', 'DemonHelmOpened', 'DemonHelmOpenedCyan', 'DemonHelmOpenedPurple', 'DemonHelmPurple', 'DemonLeggings',
        'DemonLeggingsCyan', 'DemonLeggingsPurple', 'GluttonHelm', 'GluttonHelmCyan', 'GluttonHelmOpened', 'GluttonHelmOpenedCyan',
        'GluttonHelmOpenedPurple', 'GluttonHelmPurple'
    ],
    'Elite Scorpion Helms': [
        'EliteScorpianAllBlack', 'EliteScorpianAllBlue', 'EliteScorpianAllGreen', 'EliteScorpianAllPink', 'EliteScorpianAllPurple',
        'EliteScorpianAllRed', 'EliteScorpianAllYellow', 'EliteScorpianBlack', 'EliteScorpianBlackBraid', 'EliteScorpianBlue',
        'EliteScorpianBlueBraid', 'EliteScorpianGingerBraid', 'EliteScorpianGreen', 'EliteScorpianGreenBraid', 'EliteScorpianHelm',
        'EliteScorpianPink', 'EliteScorpianPurple', 'EliteScorpianPurpleBraid', 'EliteScorpianRed', 'EliteScorpianWhite',
        'EliteScorpianYellow'
    ],
    'Engineering Rig': [
        'EngineeringRig', 'EngineeringRigAlt'
    ],
    'Grand Lich Hood': [
        'GrandLichHoodBlackAlt', 'GrandLichHoodBlackAltVeiless', 'GrandLichHoodBlue', 'GrandLichHoodBlueAlt', 'GrandLichHoodBlueAltVeiless',
        'GrandLichHoodBlueVeiless', 'GrandLichHoodCyan', 'GrandLichHoodCyanAlt', 'GrandLichHoodCyanAltVeiless', 'GrandLichHoodCyanVeiless',
        'GrandLichHoodDown', 'GrandLichHoodDownBlackAlt', 'GrandLichHoodDownBlue', 'GrandLichHoodDownBlueAlt', 'GrandLichHoodDownCyan',
        'GrandLichHoodDownCyanAlt', 'GrandLichHoodDownGreen', 'GrandLichHoodDownGreenAlt', 'GrandLichHoodDownMagenta',
        'GrandLichHoodDownMagentaAlt', 'GrandLichHoodDownPurple', 'GrandLichHoodDownPurpleAlt', 'GrandLichHoodDownRed',
        'GrandLichHoodDownWhite', 'GrandLichHoodDownWhiteAlt', 'GrandLichHoodDownYellow', 'GrandLichHoodDownYellowAlt', 'GrandLichHoodGreen',
        'GrandLichHoodGreenAlt', 'GrandLichHoodGreenAltVeiless', 'GrandLichHoodGreenVeiless', 'GrandLichHoodMagenta',
        'GrandLichHoodMagentaAlt', 'GrandLichHoodMagentaAltVeiless', 'GrandLichHoodMagentaVeiless', 'GrandLichHoodPurple',
        'GrandLichHoodPurpleAlt', 'GrandLichHoodPurpleAltVeiless', 'GrandLichHoodPurpleVeiless', 'GrandLichHoodRed',
        'GrandLichHoodRedVeiless', 'GrandLichHoodStandard', 'GrandLichHoodVieless', 'GrandLichHoodWhite', 'GrandLichHoodWhiteAlt',
        'GrandLichHoodWhiteAltVeiless', 'GrandLichHoodWhiteVeiless', 'GrandLichHoodYellow', 'GrandLichHoodYellowAlt',
        'GrandLichHoodYellowAltVeiless', 'GrandLichHoodYellowVeiless', 'GrandLichHoodless', 'GrandLichHoodlessBlackAlt',
        'GrandLichHoodlessBlue', 'GrandLichHoodlessBlueAlt', 'GrandLichHoodlessCyan', 'GrandLichHoodlessCyanAlt', 'GrandLichHoodlessGreen',
        'GrandLichHoodlessGreenAlt', 'GrandLichHoodlessMagenta', 'GrandLichHoodlessMagentaAlt', 'GrandLichHoodlessPurple',
        'GrandLichHoodlessPurpleAlt', 'GrandLichHoodlessRed', 'GrandLichHoodlessWhite', 'GrandLichHoodlessWhiteAlt',
        'GrandLichHoodlessYellow', 'GrandLichHoodlessYellowAlt'
    ],
    'Jester': [
        'JesterChest', 'JesterChestBlackBlue', 'JesterChestBlackCyan', 'JesterChestBlackGreen', 'JesterChestBlackMagenta',
        'JesterChestBlackRed', 'JesterChestBlackWhite', 'JesterChestBlackYellow', 'JesterChestBlueMagenta', 'JesterChestCyanGreen',
        'JesterChestCyanMagenta', 'JesterChestCyanYellow', 'JesterChestPurpleMagenta', 'JesterChestRedGreen', 'JesterChestYellowBlue',
        'JesterChestYellowGreen', 'JesterChestYellowMagenta', 'JesterChestYellowPurple', 'JesterHatDouble', 'JesterHatDoubleBlackBlue',
        'JesterHatDoubleBlackCyan', 'JesterHatDoubleBlackGreen', 'JesterHatDoubleBlackMagenta', 'JesterHatDoubleBlackRed',
        'JesterHatDoubleBlackWhite', 'JesterHatDoubleBlackYellow', 'JesterHatDoubleBlueMagenta', 'JesterHatDoubleCyanGreen',
        'JesterHatDoubleCyanMagenta', 'JesterHatDoubleCyanYellow', 'JesterHatDoublePurpleMagenta', 'JesterHatDoubleRedGreen',
        'JesterHatDoubleYellowBlue', 'JesterHatDoubleYellowGreen', 'JesterHatDoubleYellowMagenta', 'JesterHatDoubleYellowPurple',
        'JesterHatQuad', 'JesterHatQuadBlackBlue', 'JesterHatQuadBlackCyan', 'JesterHatQuadBlackGreen', 'JesterHatQuadBlackMagenta',
        'JesterHatQuadBlackRed', 'JesterHatQuadBlackWhite', 'JesterHatQuadBlackYellow', 'JesterHatQuadBlueMagenta', 'JesterHatQuadCyanGreen',
        'JesterHatQuadCyanMagenta', 'JesterHatQuadCyanYellow', 'JesterHatQuadPurpleMagenta', 'JesterHatQuadRedGreen',
        'JesterHatQuadYellowBlue', 'JesterHatQuadYellowGreen', 'JesterHatQuadYellowMagenta', 'JesterHatQuadYellowPurple', 'JesterHatReverse',
        'JesterHatReverseBlackBlue', 'JesterHatReverseBlackCyan', 'JesterHatReverseBlackGreen', 'JesterHatReverseBlackMagenta',
        'JesterHatReverseBlackRed', 'JesterHatReverseBlackWhite', 'JesterHatReverseBlackYellow', 'JesterHatReverseBlueMagenta',
        'JesterHatReverseCyanGreen', 'JesterHatReverseCyanMagenta', 'JesterHatReverseCyanYellow', 'JesterHatReversePurpleMagenta',
        'JesterHatReverseRedGreen', 'JesterHatReverseYellowBlue', 'JesterHatReverseYellowGreen', 'JesterHatReverseYellowMagenta',
        'JesterHatReverseYellowPurple', 'JesterHatSingle', 'JesterHatSingleBlackBlue', 'JesterHatSingleBlackCyan',
        'JesterHatSingleBlackGreen', 'JesterHatSingleBlackMagenta', 'JesterHatSingleBlackRed', 'JesterHatSingleBlackWhite',
        'JesterHatSingleBlackYellow', 'JesterHatSingleBlueMagenta', 'JesterHatSingleCyanGreen', 'JesterHatSingleCyanMagenta',
        'JesterHatSingleCyanYellow', 'JesterHatSinglePurpleMagenta', 'JesterHatSingleRedGreen', 'JesterHatSingleYellowBlue',
        'JesterHatSingleYellowGreen', 'JesterHatSingleYellowMagenta', 'JesterHatSingleYellowPurple', 'JesterHatSinister',
        'JesterHatSinisterBlackBlue', 'JesterHatSinisterBlackCyan', 'JesterHatSinisterBlackGreen', 'JesterHatSinisterBlackMagenta',
        'JesterHatSinisterBlackRed', 'JesterHatSinisterBlackWhite', 'JesterHatSinisterBlackYellow', 'JesterHatSinisterBlueMagenta',
        'JesterHatSinisterCyanGreen', 'JesterHatSinisterCyanMagenta', 'JesterHatSinisterCyanYellow', 'JesterHatSinisterPurpleMagenta',
        'JesterHatSinisterRedGreen', 'JesterHatSinisterYellowBlue', 'JesterHatSinisterYellowGreen', 'JesterHatSinisterYellowMagenta',
        'JesterHatSinisterYellowPurple', 'JesterLegs', 'JesterLegsAlt', 'JesterLegsAltBlackBlue', 'JesterLegsAltBlackCyan',
        'JesterLegsAltBlackGreen', 'JesterLegsAltBlackMagenta', 'JesterLegsAltBlackRed', 'JesterLegsAltBlackWhite',
        'JesterLegsAltBlackYellow', 'JesterLegsAltBlueMagenta', 'JesterLegsAltCyanGreen', 'JesterLegsAltCyanMagenta',
        'JesterLegsAltCyanYellow', 'JesterLegsAltPurpleMagenta', 'JesterLegsAltRedGreen', 'JesterLegsAltYellowBlue',
        'JesterLegsAltYellowGreen', 'JesterLegsAltYellowMagenta', 'JesterLegsAltYellowPurple', 'JesterLegsBlackBlue', 'JesterLegsBlackCyan',
        'JesterLegsBlackGreen', 'JesterLegsBlackMagenta', 'JesterLegsBlackRed', 'JesterLegsBlackWhite', 'JesterLegsBlackYellow',
        'JesterLegsBlueMagenta', 'JesterLegsCyanGreen', 'JesterLegsCyanMagenta', 'JesterLegsCyanYellow', 'JesterLegsPurpleMagenta',
        'JesterLegsRedGreen', 'JesterLegsYellowBlue', 'JesterLegsYellowGreen', 'JesterLegsYellowMagenta', 'JesterLegsYellowPurple'
    ],
    'Potion Bandolier': [
        'PotionBandolierBeltBlue', 'PotionBandolierBeltPink', 'PotionBandolierBeltPurple', 'PotionBandolierBeltRed', 'PotionBandolierBlue',
        'PotionBandolierBlueClip', 'PotionBandolierBurntSkeleton', 'PotionBandolierGreen', 'PotionBandolierGreenClip', 'PotionBandolierPink',
        'PotionBandolierPinkClip', 'PotionBandolierPurple', 'PotionBandolierPurpleClip', 'PotionBandolierRed', 'PotionBandolierRedClip',
        'PotionBeltBlueClip', 'PotionBeltPinkClip', 'PotionBeltPurpleClip', 'PotionBeltRedClip'
    ],
    'Priest': [
        'PriestChest', 'PriestChestAlt', 'PriestChestAltBlack', 'PriestChestAltBlue', 'PriestChestAltGreen', 'PriestChestAltPink',
        'PriestChestAltPurple', 'PriestChestAltWhite', 'PriestChestAltYellow', 'PriestChestBlack', 'PriestChestBlue', 'PriestChestGreen',
        'PriestChestPink', 'PriestChestPurple', 'PriestChestWhite', 'PriestChestYellow', 'PriestHelm', 'PriestHelmBlack', 'PriestHelmBlue',
        'PriestHelmGreen', 'PriestHelmOpen', 'PriestHelmOpenBlack', 'PriestHelmOpenBlue', 'PriestHelmOpenGreen', 'PriestHelmOpenPink',
        'PriestHelmOpenPurple', 'PriestHelmOpenWhite', 'PriestHelmOpenYellow', 'PriestHelmPink', 'PriestHelmPurple', 'PriestHelmWhite',
        'PriestHelmYellow', 'PriestRobes', 'PriestRobesBlack', 'PriestRobesBlue', 'PriestRobesGreen', 'PriestRobesPink', 'PriestRobesPurple',
        'PriestRobesWhite', 'PriestRobesYellow', 'PriestSleeves', 'PriestSleevesBlack', 'PriestSleevesBlue', 'PriestSleevesGreen',
        'PriestSleevesPink', 'PriestSleevesPurple', 'PriestSleevesWhite', 'PriestSleevesYellow', 'PriestTunic', 'PriestTunicBlack',
        'PriestTunicBlue', 'PriestTunicGreen', 'PriestTunicPink', 'PriestTunicPurple', 'PriestTunicWhite', 'PriestTunicYellow'
    ],
    'Relentless': [
        'Relentless'
    ],
    'Tribal Masks': [
        'RhinoMask', 'SnowLeopardMask', 'VultureMask'
    ],
    'Rook': [
        'RookBootsAzure', 'RookBootsBlack', 'RookBootsFrosty', 'RookBootsGhost', 'RookBootsGoth', 'RookBootsGreen', 'RookBootsPurple',
        'RookBootsRed', 'RookBootsRusty', 'RookBootsWraith', 'RookChestAzure', 'RookChestBlack', 'RookChestFrosty', 'RookChestGhost',
        'RookChestGoth', 'RookChestGreen', 'RookChestPurple', 'RookChestRed', 'RookChestRusty', 'RookChestWraith', 'RookGauntletsAzure',
        'RookGauntletsBlack', 'RookGauntletsFrosty', 'RookGauntletsGhost', 'RookGauntletsGoth', 'RookGauntletsGreen', 'RookGauntletsPurple',
        'RookGauntletsRed', 'RookGauntletsRusty', 'RookGauntletsWraith', 'RookHelmAzure', 'RookHelmAzureOpen', 'RookHelmBlack',
        'RookHelmBlackOpen', 'RookHelmFrosty', 'RookHelmFrostyOpen', 'RookHelmGhost', 'RookHelmGhostOpen', 'RookHelmGoth', 'RookHelmGothOpen',
        'RookHelmGreen', 'RookHelmGreenOpen', 'RookHelmPurple', 'RookHelmPurpleOpen', 'RookHelmRed', 'RookHelmRedOpen', 'RookHelmWraith',
        'RookHelmWraithOpen', 'RookRustyHelm', 'RookRustyOpen'
    ],
    'Elite Rook': [
        'RookEliteBootsCharred', 'RookEliteBootsCharred2', 'RookEliteBootsIradescent', 'RookEliteBootsMarble', 'RookEliteBootsMonster',
        'RookEliteBootsRainbow', 'RookEliteBootsRuby', 'RookEliteBootsSapphire', 'RookEliteBootsStone', 'RookEliteBootsVerdan',
        'RookEliteChestCharred', 'RookEliteChestIradescent', 'RookEliteChestMarble', 'RookEliteChestMonster', 'RookEliteChestRainbow',
        'RookEliteChestRuby', 'RookEliteChestSapphire', 'RookEliteChestStone', 'RookEliteChestVerdan', 'RookEliteGauntletsCharred',
        'RookEliteGauntletsIradescent', 'RookEliteGauntletsMarble', 'RookEliteGauntletsMonster', 'RookEliteGauntletsRainbow',
        'RookEliteGauntletsRuby', 'RookEliteGauntletsSapphire', 'RookEliteGauntletsStone', 'RookEliteGauntletsVerdan', 'RookEliteHelmCharred',
        'RookEliteHelmCharredOpen', 'RookEliteHelmIradescent', 'RookEliteHelmIradescentOpen', 'RookEliteHelmMarble',
        'RookEliteHelmMarbleOpen', 'RookEliteHelmMonster', 'RookEliteHelmMonsterOpen', 'RookEliteHelmRainbow', 'RookEliteHelmRainbowOpen',
        'RookEliteHelmRuby', 'RookEliteHelmRubyOpen', 'RookEliteHelmSapphire', 'RookEliteHelmStone', 'RookEliteHelmStoneOpen',
        'RookEliteHelmVerdan', 'RookEliteHelmVerdanOpen', 'RookEliteSapphireOpen'
    ],
    'Scarecrow': [
        'ScareCrowHatBlack', 'ScareCrowHatBlue', 'ScareCrowHatEvil', 'ScareCrowHatGreen', 'ScareCrowHatMagenta', 'ScareCrowHatPurple',
        'ScareCrowHatRed', 'ScareCrowHatWhite', 'ScareCrowHatYellow', 'ScareCrowHelm', 'ScareCrowHelmBlack', 'ScareCrowHelmCyan',
        'ScareCrowHelmEvil', 'ScareCrowHelmGreen', 'ScareCrowHelmMagenta', 'ScareCrowHelmPurple', 'ScareCrowHelmRed', 'ScareCrowHelmWhite',
        'ScareCrowHelmYellow'
    ],
    'Scorpion Helms': [
        'ScorpianAllBlack', 'ScorpianAllBlue', 'ScorpianAllGreen', 'ScorpianAllPink', 'ScorpianAllPurple', 'ScorpianAllRed',
        'ScorpianAllYellow', 'ScorpianBlackBraid', 'ScorpianBlueBraid', 'ScorpianBraidPurple', 'ScorpianGingerBraid', 'ScorpianGreenBraid',
        'ScorpianHelm', 'ScorpianHelmBlack', 'ScorpianHelmBlue', 'ScorpianHelmGreen', 'ScorpianHelmPink', 'ScorpianHelmPurple',
        'ScorpianHelmRed', 'ScorpianHelmWhite', 'ScorpianHelmYellow', 'ScorpianPinkBraid', 'ScorpianWhiteBraid'
    ],
    'Battlegrounds': [
        'TarnishedCrown', 'VerdantAmulet'
    ],
    'Warden': [
        'WardenChest', 'WardenChestDesert', 'WardenChestFire', 'WardenHelm', 'WardenHelmDesert', 'WardenHelmDesertOpen',
        'WardenHelmDesertOpenAlt', 'WardenHelmFire', 'WardenHelmFireOpen', 'WardenHelmFireOpenAlt', 'WardenHelmOpen', 'WardenHelmOpenAlt',
        'WardenLeggings', 'WardenLeggingsDesert', 'WardenLeggingsFire', 'WardenSleeves', 'WardenSleevesDesert', 'WardenSleevesFire'
    ],
    'Calvary': [
        'CalvaryChestAltBlack', 'CalvaryChestAltBlackBlack', 'CalvaryChestAltBlackBlue', 'CalvaryChestAltBlackCyan',
        'CalvaryChestAltBlackGreen', 'CalvaryChestAltBlackMagenta', 'CalvaryChestAltBlackPurple', 'CalvaryChestAltBlackRed',
        'CalvaryChestAltBlackYellow', 'CalvaryChestAltBlue', 'CalvaryChestAltCyan', 'CalvaryChestAltGoldBlack', 'CalvaryChestAltGoldBlue',
        'CalvaryChestAltGoldCyan', 'CalvaryChestAltGoldGreen', 'CalvaryChestAltGoldMagenta', 'CalvaryChestAltGoldPurple',
        'CalvaryChestAltGoldRed', 'CalvaryChestAltGoldYellow', 'CalvaryChestAltGreen', 'CalvaryChestAltMagenta', 'CalvaryChestAltPurple',
        'CalvaryChestAltRed', 'CalvaryChestAltWhite', 'CalvaryChestAltYellow', 'CalvaryChestBlack', 'CalvaryChestBlackBlack',
        'CalvaryChestBlackBlue', 'CalvaryChestBlackCyan', 'CalvaryChestBlackGreen', 'CalvaryChestBlackMagenta', 'CalvaryChestBlackPurple',
        'CalvaryChestBlackRed', 'CalvaryChestBlackYellow', 'CalvaryChestBlue', 'CalvaryChestCyan', 'CalvaryChestGoldBlack',
        'CalvaryChestGoldBlue', 'CalvaryChestGoldCyan', 'CalvaryChestGoldGreen', 'CalvaryChestGoldMagenta', 'CalvaryChestGoldPurple',
        'CalvaryChestGoldRed', 'CalvaryChestGoldYellow', 'CalvaryChestGreen', 'CalvaryChestMagenta', 'CalvaryChestPurple', 'CalvaryChestRed',
        'CalvaryChestWhite', 'CalvaryChestYellow', 'CalvaryGauntletBlack', 'CalvaryGauntletBlue', 'CalvaryGauntletsBlackBlack',
        'CalvaryGauntletsBlackBlue', 'CalvaryGauntletsBlackCyan', 'CalvaryGauntletsBlackGreen', 'CalvaryGauntletsBlackMagenta',
        'CalvaryGauntletsBlackPurple', 'CalvaryGauntletsBlackRed', 'CalvaryGauntletsBlackYellow', 'CalvaryGauntletsCyan',
        'CalvaryGauntletsGoldBlack', 'CalvaryGauntletsGoldBlue', 'CalvaryGauntletsGoldCyan', 'CalvaryGauntletsGoldGreen',
        'CalvaryGauntletsGoldMagenta', 'CalvaryGauntletsGoldPurple', 'CalvaryGauntletsGoldRed', 'CalvaryGauntletsGoldYellow',
        'CalvaryGauntletsGreen', 'CalvaryGauntletsMagenta', 'CalvaryGauntletsPurple', 'CalvaryGauntletsRed', 'CalvaryGauntletsWhite',
        'CalvaryGauntletsYellow', 'CalvaryHeadAlt2Black', 'CalvaryHeadAlt2BlackBlack', 'CalvaryHeadAlt2BlackBlue', 'CalvaryHeadAlt2BlackCyan',
        'CalvaryHeadAlt2BlackGreen', 'CalvaryHeadAlt2BlackMagenta', 'CalvaryHeadAlt2BlackPurple', 'CalvaryHeadAlt2BlackRed',
        'CalvaryHeadAlt2BlackYellow', 'CalvaryHeadAlt2Blue', 'CalvaryHeadAlt2Cyan', 'CalvaryHeadAlt2GoldBlack', 'CalvaryHeadAlt2GoldBlue',
        'CalvaryHeadAlt2GoldCyan', 'CalvaryHeadAlt2GoldGreen', 'CalvaryHeadAlt2GoldMagenta', 'CalvaryHeadAlt2GoldPurple',
        'CalvaryHeadAlt2GoldRed', 'CalvaryHeadAlt2GoldYellow', 'CalvaryHeadAlt2Green', 'CalvaryHeadAlt2Magenta', 'CalvaryHeadAlt2Purple',
        'CalvaryHeadAlt2Red', 'CalvaryHeadAlt2White', 'CalvaryHeadAlt2Yellow', 'CalvaryHeadAltBlack', 'CalvaryHeadAltBlackBlack',
        'CalvaryHeadAltBlackBlue', 'CalvaryHeadAltBlackCyan', 'CalvaryHeadAltBlackGreen', 'CalvaryHeadAltBlackMagenta',
        'CalvaryHeadAltBlackPurple', 'CalvaryHeadAltBlackRed', 'CalvaryHeadAltBlackYellow', 'CalvaryHeadAltBlue', 'CalvaryHeadAltCyan',
        'CalvaryHeadAltGoldBlack', 'CalvaryHeadAltGoldBlue', 'CalvaryHeadAltGoldCyan', 'CalvaryHeadAltGoldGreen', 'CalvaryHeadAltGoldMagenta',
        'CalvaryHeadAltGoldPurple', 'CalvaryHeadAltGoldRed', 'CalvaryHeadAltGoldYellow', 'CalvaryHeadAltGreen', 'CalvaryHeadAltMagenta',
        'CalvaryHeadAltPurple', 'CalvaryHeadAltRed', 'CalvaryHeadAltWhite', 'CalvaryHeadAltYellow', 'CalvaryHeadBlack',
        'CalvaryHeadBlackBlack', 'CalvaryHeadBlackBlue', 'CalvaryHeadBlackCyan', 'CalvaryHeadBlackGreen', 'CalvaryHeadBlackMagenta',
        'CalvaryHeadBlackPurple', 'CalvaryHeadBlackRed', 'CalvaryHeadBlackYellow', 'CalvaryHeadBlue', 'CalvaryHeadCyan',
        'CalvaryHeadGoldBlack', 'CalvaryHeadGoldBlue', 'CalvaryHeadGoldCyan', 'CalvaryHeadGoldGreen', 'CalvaryHeadGoldMagenta',
        'CalvaryHeadGoldPurple', 'CalvaryHeadGoldRed', 'CalvaryHeadGoldYellow', 'CalvaryHeadGreen', 'CalvaryHeadMagenta', 'CalvaryHeadPurple',
        'CalvaryHeadRed', 'CalvaryHeadWhite', 'CalvaryHeadYellow', 'CalvaryLeggingsBlack', 'CalvaryLeggingsBlue', 'CalvaryLegsBlackBlack',
        'CalvaryLegsBlackBlue', 'CalvaryLegsBlackCyan', 'CalvaryLegsBlackGreen', 'CalvaryLegsBlackMagenta', 'CalvaryLegsBlackPurple',
        'CalvaryLegsBlackRed', 'CalvaryLegsBlackYellow', 'CalvaryLegsCyan', 'CalvaryLegsGoldBlack', 'CalvaryLegsGoldBlue',
        'CalvaryLegsGoldCyan', 'CalvaryLegsGoldGreen', 'CalvaryLegsGoldMagenta', 'CalvaryLegsGoldPurple', 'CalvaryLegsGoldRed',
        'CalvaryLegsGoldYellow', 'CalvaryLegsGreen', 'CalvaryLegsMagenta', 'CalvaryLegsPurple', 'CalvaryLegsRed', 'CalvaryLegsWhite',
        'CalvaryLegsYellow', 'GhostCalvaryChest', 'GhostCalvaryGauntlets', 'GhostCalvaryHelm', 'GhostCalvaryLeggings'
    ],
    'Cobalt Dragon': [
        'CobaltDragonChestPlateBlackGreen', 'CobaltDragonChestPlateBlackMagenta', 'CobaltDragonChestPlateBlackPurple',
        'CobaltDragonChestPlateBlackRed', 'CobaltDragonChestPlateBlackYellow', 'CobaltDragonChestPlateCyan', 'CobaltDragonChestPlateGreen',
        'CobaltDragonChestPlatePurple', 'CobaltDragonChestPlateRed', 'CobaltDragonChestPlateWhite', 'CobaltDragonChestPlateYellow',
        'CobaltDragonChestplate', 'CobaltDragonChestplateBlackBlue', 'CobaltDragonChestplateBlackCyan', 'CobaltDragonGauntlets',
        'CobaltDragonGauntletsBlack', 'CobaltDragonHelm', 'CobaltDragonHelmAltBlue', 'CobaltDragonHelmAltCyan', 'CobaltDragonHelmAltGreen',
        'CobaltDragonHelmAltMagenta', 'CobaltDragonHelmAltPurple', 'CobaltDragonHelmAltRed', 'CobaltDragonHelmAltWhite',
        'CobaltDragonHelmAltYellow', 'CobaltDragonHelmBlackBlue', 'CobaltDragonHelmBlackCyan', 'CobaltDragonHelmBlackGreen',
        'CobaltDragonHelmBlackMagenta', 'CobaltDragonHelmBlackPurple', 'CobaltDragonHelmBlackRed', 'CobaltDragonHelmBlackYellow',
        'CobaltDragonHelmCyan', 'CobaltDragonHelmGreen', 'CobaltDragonHelmPurple', 'CobaltDragonHelmRed', 'CobaltDragonHelmWhite',
        'CobaltDragonHelmYellow', 'CobaltDragonLeggings', 'CobaltDragonLeggingsBlack'
    ],
    'Iron Dragon': [
        'IronDragonChesplateWhite', 'IronDragonChestplate', 'IronDragonChestplateCyan', 'IronDragonChestplateGreen',
        'IronDragonChestplatePurple', 'IronDragonChestplateRed', 'IronDragonChestplateYellow', 'IronDragonGauntlets', 'IronDragonHelm',
        'IronDragonHelmCyan', 'IronDragonHelmCyanOpen', 'IronDragonHelmGreen', 'IronDragonHelmGreenOpen', 'IronDragonHelmOpen',
        'IronDragonHelmPurple', 'IronDragonHelmPurpleOpen', 'IronDragonHelmRed', 'IronDragonHelmRedOpen', 'IronDragonHelmWhite',
        'IronDragonHelmWhiteOpen', 'IronDragonHelmYellow', 'IronDragonHelmYellowOpen', 'IronDragonLeggings'
    ],
    'Antique Dragon': [
        'AntigueDragonHelmBlueHorned', 'AntigueDragonHelmBlueHornedForward', 'AntigueDragonHelmCyanHorned',
        'AntigueDragonHelmCyanHornedForward', 'AntigueDragonHelmGreenHorned', 'AntigueDragonHelmGreenHornedForward',
        'AntigueDragonHelmPurpleHorned', 'AntigueDragonHelmPurpleHornedForward', 'AntigueDragonHelmRedHorned',
        'AntigueDragonHelmRedHornedForward', 'AntigueDragonHelmWhiteHorned', 'AntigueDragonHelmWhiteHornedForward',
        'AntigueDragonHelmYellowHorned', 'AntigueDragonHelmYellowHornedForward', 'AntiqueDragonChestplate', 'AntiqueDragonChestplateCyan',
        'AntiqueDragonChestplateGreen', 'AntiqueDragonChestplatePurple', 'AntiqueDragonChestplateRed', 'AntiqueDragonChestplateWhite',
        'AntiqueDragonChestplateYellow', 'AntiqueDragonGuantlets', 'AntiqueDragonHelm', 'AntiqueDragonHelmCyan', 'AntiqueDragonHelmCyanOpen',
        'AntiqueDragonHelmGreen', 'AntiqueDragonHelmGreenOpen', 'AntiqueDragonHelmOpen', 'AntiqueDragonHelmPurple',
        'AntiqueDragonHelmPurpleOpen', 'AntiqueDragonHelmRed', 'AntiqueDragonHelmRedOpen', 'AntiqueDragonHelmWhite',
        'AntiqueDragonHelmWhiteOpen', 'AntiqueDragonHelmYellow', 'AntiqueDragonHelmYellowOpen', 'AntiqueDragonLeggings'
    ],
    'Antique Shield (weapons)': [
        'AntiqueShieldBlue', 'AntiqueShieldGreen', 'AntiqueShieldRed', 'AntiqueShieldWhite', 'AntiqueShieldYellow', 'Antique_Shield'
    ],
    'Battleaxe (weapons)': [
        'Weapon_Battleaxe_Adamantite_Black', 'Weapon_Battleaxe_Adamantite_Blue', 'Weapon_Battleaxe_Adamantite_Cyan',
        'Weapon_Battleaxe_Adamantite_Gray', 'Weapon_Battleaxe_Adamantite_Green', 'Weapon_Battleaxe_Adamantite_Magenta',
        'Weapon_Battleaxe_Adamantite_Purple', 'Weapon_Battleaxe_Adamantite_Rusty', 'Weapon_Battleaxe_Adamantite_White',
        'Weapon_Battleaxe_Adamantite_Yellow', 'Weapon_Battleaxe_Cobalt_Black', 'Weapon_Battleaxe_Cobalt_Cyan', 'Weapon_Battleaxe_Cobalt_Gray',
        'Weapon_Battleaxe_Cobalt_Green', 'Weapon_Battleaxe_Cobalt_Magenta', 'Weapon_Battleaxe_Cobalt_Purple', 'Weapon_Battleaxe_Cobalt_Red',
        'Weapon_Battleaxe_Cobalt_Rusty', 'Weapon_Battleaxe_Cobalt_White', 'Weapon_Battleaxe_Cobalt_Yellow', 'Weapon_Battleaxe_Iron_Black',
        'Weapon_Battleaxe_Iron_Blue', 'Weapon_Battleaxe_Iron_Cyan', 'Weapon_Battleaxe_Iron_Green', 'Weapon_Battleaxe_Iron_Magenta',
        'Weapon_Battleaxe_Iron_Purple', 'Weapon_Battleaxe_Iron_Red', 'Weapon_Battleaxe_Iron_Rusty', 'Weapon_Battleaxe_Iron_White',
        'Weapon_Battleaxe_Iron_Yellow', 'Weapon_Battleaxe_Thorium_Black', 'Weapon_Battleaxe_Thorium_Blue', 'Weapon_Battleaxe_Thorium_Cyan',
        'Weapon_Battleaxe_Thorium_Gray', 'Weapon_Battleaxe_Thorium_Magenta', 'Weapon_Battleaxe_Thorium_Purple',
        'Weapon_Battleaxe_Thorium_Red', 'Weapon_Battleaxe_Thorium_Rusty', 'Weapon_Battleaxe_Thorium_White', 'Weapon_Battleaxe_Thorium_Yellow'
    ],
    'Dagger (weapons)': [
        'Dagger_Adamantite_Black', 'Dagger_Adamantite_Blue', 'Dagger_Adamantite_Cyan', 'Dagger_Adamantite_Gray', 'Dagger_Adamantite_Green',
        'Dagger_Adamantite_Magenta', 'Dagger_Adamantite_Purple', 'Dagger_Adamantite_Rusty', 'Dagger_Adamantite_White',
        'Dagger_Adamantite_Yellow', 'Dagger_Cobalt_Black', 'Dagger_Cobalt_Cyan', 'Dagger_Cobalt_Gray', 'Dagger_Cobalt_Green',
        'Dagger_Cobalt_Magenta', 'Dagger_Cobalt_Purple', 'Dagger_Cobalt_Red', 'Dagger_Cobalt_Rusty', 'Dagger_Cobalt_White',
        'Dagger_Cobalt_Yellow', 'Dagger_Iron_Black', 'Dagger_Iron_Blue', 'Dagger_Iron_Cyan', 'Dagger_Iron_Green', 'Dagger_Iron_Magenta',
        'Dagger_Iron_Purple', 'Dagger_Iron_Red', 'Dagger_Iron_Rusty', 'Dagger_Iron_White', 'Dagger_Iron_Yellow', 'Dagger_Thorium_Black',
        'Dagger_Thorium_Gray', 'Dagger_Thorium_Magenta', 'Dagger_Thorium_Purple', 'Dagger_Thorium_Red', 'Dagger_Thorium_White',
        'Dagger_Thorium_Yellow', 'Dagger_Throium_Blue', 'Dagger_Throium_Cyan', 'Dagger_Throrium_Rusty'
    ],
    'Longsword (weapons)': [
        'Longsword_Cobalt_Black', 'Longsword_Cobalt_Cyan', 'Longsword_Cobalt_Gray', 'Longsword_Cobalt_Green', 'Longsword_Cobalt_Magenta',
        'Longsword_Cobalt_Purple', 'Longsword_Cobalt_Red', 'Longsword_Cobalt_Rusty', 'Longsword_Cobalt_White', 'Longsword_Cobalt_Yellow',
        'Longsword_Iron_Black', 'Longsword_Iron_Blue', 'Longsword_Iron_Cyan', 'Longsword_Iron_Green', 'Longsword_Iron_Magenta',
        'Longsword_Iron_Purple', 'Longsword_Iron_Red', 'Longsword_Iron_Rusty', 'Longsword_Iron_White', 'Longsword_Iron_Yellow'
    ],
    'Mace (weapons)': [
        'Mace_Cobalt_Black', 'Mace_Cobalt_Cyan', 'Mace_Cobalt_Gray', 'Mace_Cobalt_Green', 'Mace_Cobalt_Magenta', 'Mace_Cobalt_Purple',
        'Mace_Cobalt_Red', 'Mace_Cobalt_Rusty', 'Mace_Cobalt_White', 'Mace_Cobalt_Yellow', 'Mace_Iron_Black', 'Mace_Iron_Blue',
        'Mace_Iron_Cyan', 'Mace_Iron_Green', 'Mace_Iron_Magenta', 'Mace_Iron_Purple', 'Mace_Iron_Red', 'Mace_Iron_Rusty', 'Mace_Iron_White',
        'Mace_Iron_Yellow', 'Mace_Thorium_Black', 'Mace_Thorium_Blue', 'Mace_Thorium_Cyan', 'Mace_Thorium_Gray', 'Mace_Thorium_Magenta',
        'Mace_Thorium_Purple', 'Mace_Thorium_Red', 'Mace_Thorium_Rusty', 'Mace_Thorium_White', 'Mace_Thorium_Yellow'
    ],
    'Shield (weapons)': [
        'Weapon_Shield_Adamantite_Black', 'Weapon_Shield_Adamantite_Blue', 'Weapon_Shield_Adamantite_Blue_Alt',
        'Weapon_Shield_Adamantite_Cyan', 'Weapon_Shield_Adamantite_Cyan_Alt', 'Weapon_Shield_Adamantite_Gray',
        'Weapon_Shield_Adamantite_Green', 'Weapon_Shield_Adamantite_Green_Alt', 'Weapon_Shield_Adamantite_Magenta',
        'Weapon_Shield_Adamantite_Magenta_Alt', 'Weapon_Shield_Adamantite_Purple', 'Weapon_Shield_Adamantite_Purple_Alt',
        'Weapon_Shield_Adamantite_Red_Alt', 'Weapon_Shield_Adamantite_Rusty', 'Weapon_Shield_Adamantite_White',
        'Weapon_Shield_Adamantite_Yellow', 'Weapon_Shield_Cobalt_Black', 'Weapon_Shield_Cobalt_Black_Pat', 'Weapon_Shield_Cobalt_Blue_Pat',
        'Weapon_Shield_Cobalt_Cyan', 'Weapon_Shield_Cobalt_Cyan_Pat', 'Weapon_Shield_Cobalt_Green', 'Weapon_Shield_Cobalt_Green_Pat',
        'Weapon_Shield_Cobalt_Inverse', 'Weapon_Shield_Cobalt_Magenta', 'Weapon_Shield_Cobalt_Magenta_Pat', 'Weapon_Shield_Cobalt_Purple',
        'Weapon_Shield_Cobalt_Purple_Pat', 'Weapon_Shield_Cobalt_Red', 'Weapon_Shield_Cobalt_Red_Pat', 'Weapon_Shield_Cobalt_Rusty',
        'Weapon_Shield_Cobalt_White', 'Weapon_Shield_Cobalt_Yellow', 'Weapon_Shield_Cobalt_Yellow_Pat', 'Weapon_Shield_Iron_Black',
        'Weapon_Shield_Iron_Black_Alt', 'Weapon_Shield_Iron_Black_Pat', 'Weapon_Shield_Iron_Blue', 'Weapon_Shield_Iron_Blue_Alt',
        'Weapon_Shield_Iron_Blue_Pat', 'Weapon_Shield_Iron_Cyan', 'Weapon_Shield_Iron_Cyan_Alt', 'Weapon_Shield_Iron_Cyan_Pat',
        'Weapon_Shield_Iron_Green', 'Weapon_Shield_Iron_Green_Alt', 'Weapon_Shield_Iron_Green_Pat', 'Weapon_Shield_Iron_Magenta',
        'Weapon_Shield_Iron_Magenta_Alt', 'Weapon_Shield_Iron_Magenta_Pat', 'Weapon_Shield_Iron_Purple', 'Weapon_Shield_Iron_Purple_Alt',
        'Weapon_Shield_Iron_Purple_Pat', 'Weapon_Shield_Iron_Red', 'Weapon_Shield_Iron_Red_Alt', 'Weapon_Shield_Iron_Red_Pat',
        'Weapon_Shield_Iron_Rusty', 'Weapon_Shield_Iron_White', 'Weapon_Shield_Iron_White_Alt', 'Weapon_Shield_Iron_Yellow',
        'Weapon_Shield_Iron_Yellow_Alt', 'Weapon_Shield_Iron_Yellow_Pat', 'Weapon_Shield_Thorium_Black', 'Weapon_Shield_Thorium_Black_Pat',
        'Weapon_Shield_Thorium_Blue', 'Weapon_Shield_Thorium_Blue_Alt', 'Weapon_Shield_Thorium_Blue_Pat', 'Weapon_Shield_Thorium_Cyan',
        'Weapon_Shield_Thorium_Cyan_Alt', 'Weapon_Shield_Thorium_Cyan_Pat', 'Weapon_Shield_Thorium_Gray', 'Weapon_Shield_Thorium_Green_Alt',
        'Weapon_Shield_Thorium_Green_Pat', 'Weapon_Shield_Thorium_Magenta', 'Weapon_Shield_Thorium_Magenta_Alt',
        'Weapon_Shield_Thorium_Magenta_Pat', 'Weapon_Shield_Thorium_Purple', 'Weapon_Shield_Thorium_Purple_Alt',
        'Weapon_Shield_Thorium_Purple_Pat', 'Weapon_Shield_Thorium_Red', 'Weapon_Shield_Thorium_Red_Alt', 'Weapon_Shield_Thorium_Red_Pat',
        'Weapon_Shield_Thorium_Rusty', 'Weapon_Shield_Thorium_White', 'Weapon_Shield_Thorium_Yellow', 'Weapon_Shield_Thorium_Yellow_Pat'
    ],
    'Sword (weapons)': [
        'Sword_Adamantite_Black', 'Sword_Adamantite_Blue', 'Sword_Adamantite_Cyan', 'Sword_Adamantite_Gray', 'Sword_Adamantite_Green',
        'Sword_Adamantite_Magenta', 'Sword_Adamantite_Purple', 'Sword_Adamantite_Rusty', 'Sword_Adamantite_White', 'Sword_Adamantite_Yellow',
        'Sword_Cobalt_Black', 'Sword_Cobalt_Cyan', 'Sword_Cobalt_Gray', 'Sword_Cobalt_Green', 'Sword_Cobalt_Magenta', 'Sword_Cobalt_Purple',
        'Sword_Cobalt_Red', 'Sword_Cobalt_Rusty', 'Sword_Cobalt_White', 'Sword_Cobalt_Yellow', 'Sword_Iron_Black', 'Sword_Iron_Blue',
        'Sword_Iron_Cyan', 'Sword_Iron_Green', 'Sword_Iron_Magenta', 'Sword_Iron_Purple', 'Sword_Iron_Red', 'Sword_Iron_Rusty',
        'Sword_Iron_White', 'Sword_Iron_Yellow', 'Sword_Thorium_Black', 'Sword_Thorium_Blue', 'Sword_Thorium_Cyan', 'Sword_Thorium_Gray',
        'Sword_Thorium_Magenta', 'Sword_Thorium_Purple', 'Sword_Thorium_Red', 'Sword_Thorium_White', 'Sword_Thorium_Yellow',
        'Sword_Throrium_Rusty'
    ],
}


def _ids(group, keep=None, drop=None):
    """the ids of one ARMORY_IDS group; keep / drop = substrings (any match)"""
    out = []
    for i in ARMORY_IDS[group]:
        if keep and not any(k in i for k in keep):
            continue
        if drop and any(k in i for k in drop):
            continue
        out.append(i)
    return out


def _metal(group, words):
    """weapon recolours of one metal (the scan's misspelt Thorium ids Throium / Throrium count as Thorium)"""
    return [i for i in ARMORY_IDS[group] if any(("_" + w + "_") in (i + "_") for w in words)]


GHOST = ("Ghost", "Wraith")
THORIUM = ("Thorium", "Throium", "Throrium")

# SETS: one row per set (a "look"); kind = "armor" (weight = Heavy / Light / Cloth) or a weapon bag type key (weight "-").
# fields: key, src, name, kind, weight, tier, role, ids, note
SETS = [
    # ---------------------------------------------------------------- The Armory: Heavy
    dict(key="armory_antique_dragon", src="armory", name="Antique Dragon", kind="armor", weight="Heavy", tier="crude", role="drop",
         ids=_ids("Antique Dragon"), note="their Lv 5 (wood + iron)"),
    dict(key="armory_rook", src="armory", name="Rook", kind="armor", weight="Heavy", tier="iron", role="drop",
         ids=_ids("Rook", drop=GHOST), note=""),
    dict(key="armory_calvary", src="armory", name="Calvary", kind="armor", weight="Heavy", tier="iron", role="drop",
         ids=_ids("Calvary", drop=GHOST), note="179 colourways of one look"),
    dict(key="armory_rook_ghost", src="armory", name="Ghost Rook", kind="armor", weight="Heavy", tier="iron", role="ut",
         ids=_ids("Rook", keep=GHOST), note="no recipe in their mod (scan) - a UT candidate (the Rook look, ghost colours)"),
    dict(key="armory_calvary_ghost", src="armory", name="Ghost Calvary", kind="armor", weight="Heavy", tier="iron", role="ut",
         ids=_ids("Calvary", keep=GHOST), note="no recipe in their mod (scan) - a UT candidate"),
    dict(key="armory_iron_dragon", src="armory", name="Iron Dragon", kind="armor", weight="Heavy", tier="iron", role="mythic",
         ids=_ids("Iron Dragon"), note="better than Iron, dragon look - Zone 1 Heavy Mythic"),
    dict(key="armory_elite_rook", src="armory", name="Elite Rook", kind="armor", weight="Heavy", tier="thorium", role="mythic",
         ids=_ids("Elite Rook", drop=("RookEliteBootsCharred2",)), note="their odd RookEliteBootsCharred2 left out (scan: test / odd)"),
    dict(key="armory_cobalt_dragon", src="armory", name="Cobalt Dragon", kind="armor", weight="Heavy", tier="cobalt", role="mythic",
         ids=_ids("Cobalt Dragon"), note="ice resistance of their own"),
    dict(key="armory_daemon", src="armory", name="Daemon", kind="armor", weight="Heavy", tier="adamantite", role="mythic",
         ids=_ids("Daemon"), note="fire resistance + Mana of their own"),
    dict(key="armory_iron_recolour", src="armory", name="Iron recolours", kind="armor", weight="Heavy", tier="iron", role="off",
         ids=_ids("Vanilla Recolor Iron"), note="recolours of vanilla Iron = the Mining Set look (Skyy 10-17: metals are mining gear) - question Q5"),
    # ---------------------------------------------------------------- The Armory: Light
    dict(key="armory_tribal", src="armory", name="Tribal Masks", kind="armor", weight="Light", tier="crude", role="drop",
         ids=_ids("Tribal Masks"), note="heads only; negative Health of their own"),
    dict(key="armory_jester", src="armory", name="Jester", kind="armor", weight="Light", tier="copper", role="drop",
         ids=_ids("Jester"), note="no hands"),
    dict(key="armory_skull", src="armory", name="Skull Masks", kind="armor", weight="Light", tier="iron", role="drop",
         ids=_ids("Skull Masks"), note="heads only"),
    dict(key="armory_bramblekin", src="armory", name="Bramblekin", kind="armor", weight="Light", tier="iron", role="drop",
         ids=_ids("Bramblekin"), note="mask + bracers"),
    dict(key="armory_warden", src="armory", name="Warden", kind="armor", weight="Light", tier="iron", role="mythic",
         ids=_ids("Warden"), note="Archer set (projectile resistance + their Arrow_Damage_Bonus) - Zone 1 Light Mythic"),
    dict(key="armory_engineering", src="armory", name="Engineering Rig", kind="armor", weight="Light", tier="thorium", role="mythic",
         ids=_ids("Engineering Rig"), note="chest only; their Move Speed + Jump Height"),
    dict(key="armory_scorpion", src="armory", name="Scorpion Helms", kind="armor", weight="Light", tier="adamantite", role="drop",
         ids=_ids("Scorpion Helms"), note="heads only; poison resistance"),
    dict(key="armory_elite_scorpion", src="armory", name="Elite Scorpion", kind="armor", weight="Light", tier="adamantite", role="mythic",
         ids=_ids("Elite Scorpion Helms") + _ids("Relentless"), note="Elite helms + the Relentless quiver"),
    # ---------------------------------------------------------------- The Armory: Cloth
    dict(key="armory_scarecrow", src="armory", name="Scarecrow", kind="armor", weight="Cloth", tier="copper", role="drop",
         ids=_ids("Scarecrow"), note="heads only; +Mana of their own"),
    dict(key="armory_crowns", src="armory", name="Crowns", kind="armor", weight="Cloth", tier="iron", role="drop",
         ids=_ids("Crowns"), note="heads (crowns = Cloth, LOCKED 2026-10-08)"),
    dict(key="armory_amulets", src="armory", name="Amulets", kind="armor", weight="Cloth", tier="iron", role="drop",
         ids=_ids("Amulets"), note="head / chest amulets"),
    dict(key="armory_bandolier", src="armory", name="Potion Bandolier", kind="armor", weight="Cloth", tier="iron", role="drop",
         ids=_ids("Potion Bandolier"), note="their Cotton tier; poison resistance"),
    dict(key="armory_battlegrounds", src="armory", name="Battlegrounds", kind="armor", weight="Cloth", tier="iron", role="ut",
         ids=_ids("Battlegrounds"), note="Tarnished Crown + Verdant Amulet: Legendary, no recipe (scan) - UT candidates"),
    dict(key="armory_priest", src="armory", name="Priest", kind="armor", weight="Cloth", tier="cobalt", role="mythic",
         ids=_ids("Priest"), note="+Mana - Zone 3 Cloth Mythic"),
    dict(key="armory_academy", src="armory", name="Academy", kind="armor", weight="Cloth", tier="adamantite", role="off",
         ids=_ids("Academy"), note="OFF (local rebuild 2026-10-17): 27 of its 27 pieces have a recipe in 1.23.0 (Armor_Bench 3 + "
         "Alteration 24), and a UT is never crafted - no longer a UT candidate. Multiplicative Mana = special only (LOCKED 2026-10-08), "
         "so it is no normal drop either. No recipe-free Armory Cloth set exists to replace it (Zone 4 Cloth UT stays empty) - Skyy's call"),
    dict(key="armory_grand_lich", src="armory", name="Grand Lich", kind="armor", weight="Cloth", tier="adamantite", role="mythic",
         ids=_ids("Grand Lich Hood"), note="head + chest; Mana multiplier - Zone 4 Cloth Mythic"),
    # ---------------------------------------------------------------- The Armory: weapon recolours (normal drops at their metal)
    dict(key="armory_sword_iron", src="armory", name="Armory Iron Swords", kind="Weapon_Sword", weight="-", tier="iron", role="drop",
         ids=_metal("Sword (weapons)", ("Iron",)), note="recolours"),
    dict(key="armory_sword_thorium", src="armory", name="Armory Thorium Swords", kind="Weapon_Sword", weight="-", tier="thorium", role="drop",
         ids=_metal("Sword (weapons)", THORIUM), note="incl. their misspelt Throrium id"),
    dict(key="armory_sword_cobalt", src="armory", name="Armory Cobalt Swords", kind="Weapon_Sword", weight="-", tier="cobalt", role="drop",
         ids=_metal("Sword (weapons)", ("Cobalt",)), note=""),
    dict(key="armory_sword_adamantite", src="armory", name="Armory Adamantite Swords", kind="Weapon_Sword", weight="-", tier="adamantite",
         role="drop", ids=_metal("Sword (weapons)", ("Adamantite",)), note=""),
    dict(key="armory_longsword_iron", src="armory", name="Armory Iron Longswords", kind="Weapon_Longsword", weight="-", tier="iron",
         role="drop", ids=_metal("Longsword (weapons)", ("Iron",)), note=""),
    dict(key="armory_longsword_cobalt", src="armory", name="Armory Cobalt Longswords", kind="Weapon_Longsword", weight="-", tier="cobalt",
         role="drop", ids=_metal("Longsword (weapons)", ("Cobalt",)), note=""),
    dict(key="armory_dagger_iron", src="armory", name="Armory Iron Daggers", kind="Weapon_Daggers", weight="-", tier="iron", role="drop",
         ids=_metal("Dagger (weapons)", ("Iron",)), note=""),
    dict(key="armory_dagger_thorium", src="armory", name="Armory Thorium Daggers", kind="Weapon_Daggers", weight="-", tier="thorium",
         role="drop", ids=_metal("Dagger (weapons)", THORIUM), note="incl. their misspelt Throium / Throrium ids"),
    dict(key="armory_dagger_cobalt", src="armory", name="Armory Cobalt Daggers", kind="Weapon_Daggers", weight="-", tier="cobalt",
         role="drop", ids=_metal("Dagger (weapons)", ("Cobalt",)), note=""),
    dict(key="armory_dagger_adamantite", src="armory", name="Armory Adamantite Daggers", kind="Weapon_Daggers", weight="-",
         tier="adamantite", role="drop", ids=_metal("Dagger (weapons)", ("Adamantite",)), note=""),
    dict(key="armory_mace_iron", src="armory", name="Armory Iron Maces", kind="Weapon_Mace", weight="-", tier="iron", role="drop",
         ids=_metal("Mace (weapons)", ("Iron",)), note=""),
    dict(key="armory_mace_thorium", src="armory", name="Armory Thorium Maces", kind="Weapon_Mace", weight="-", tier="thorium", role="drop",
         ids=_metal("Mace (weapons)", THORIUM), note=""),
    dict(key="armory_mace_cobalt", src="armory", name="Armory Cobalt Maces", kind="Weapon_Mace", weight="-", tier="cobalt", role="drop",
         ids=_metal("Mace (weapons)", ("Cobalt",)), note=""),
    dict(key="armory_battleaxe_iron", src="armory", name="Armory Iron Battleaxes", kind="Weapon_Battleaxe", weight="-", tier="iron",
         role="drop", ids=_metal("Battleaxe (weapons)", ("Iron",)), note=""),
    dict(key="armory_battleaxe_thorium", src="armory", name="Armory Thorium Battleaxes", kind="Weapon_Battleaxe", weight="-",
         tier="thorium", role="drop", ids=_metal("Battleaxe (weapons)", THORIUM), note=""),
    dict(key="armory_battleaxe_cobalt", src="armory", name="Armory Cobalt Battleaxes", kind="Weapon_Battleaxe", weight="-", tier="cobalt",
         role="drop", ids=_metal("Battleaxe (weapons)", ("Cobalt",)), note=""),
    dict(key="armory_battleaxe_adamantite", src="armory", name="Armory Adamantite Battleaxes", kind="Weapon_Battleaxe", weight="-",
         tier="adamantite", role="drop", ids=_metal("Battleaxe (weapons)", ("Adamantite",)), note=""),
    dict(key="armory_shields", src="armory", name="Armory shields", kind="Weapon_Sword", weight="-", tier="iron", role="off",
         ids=ARMORY_IDS["Shield (weapons)"] + ARMORY_IDS["Antique Shield (weapons)"],
         note="shields are never in mystery bags (no shield bag type) - off"),
    # ---------------------------------------------------------------- The Armory: named specials (ids from the scan's 1.3 table; all in 1.23.0)
    dict(key="armory_flails", src="armory", name="Armory flails", kind="Weapon_Club", weight="-", tier="iron", role="mythic",
         ids=["FireWhip", "ScorpianFlail"], note="their Lv 15 Club_Flail moveset; Berserker for now (flail class later) - Zone 1 Club Mythic"),
    dict(key="armory_ghost_sword", src="armory", name="Ghost Sword", kind="Weapon_Sword", weight="-", tier="iron", role="ut",
         ids=["GhostSword"], note="no recipe (scan); ItemLevel 20 in 1.23.0 = the Iron recolours' level, so Iron (checked 2026-10-17)"),
    # 2026-10-23 (SkyyGear 0.3.40, Skyy 2026-10-18 Q9 "Yes, after elements ship"): the 4 Elemental swords = Spellblade Mythic boss specials, ONE per
    # zone (the "one Mythic per zone x type" rule) at the zone of the boss research/Pack-Armor-Plan.md 3.3 b names for it: Poison = the
    # Broodmother's Zone 2, Gravity = the Void Golem's Zone 3, Ice = Dragon_Frost's Zone 4, Flame = Dragon_Fire's Zone 5. SkyyGear 0.3.40 makes their
    # swings weapon hits (level, rarity, lines) + their element (Flame Fire, Ice Water, Gravity Earth = SkyyClasses' elemOfItem; Poison the status).
    dict(key="armory_elemental_poison", src="armory", name="Elemental Poison sword", kind="Weapon_Longsword", weight="-", tier="thorium",
         role="mythic", ids=["Weapon_Elemental_Poison"], note="Spellblade, Poison status - Zone 2 Longsword Mythic (Broodmother's zone)"),
    dict(key="armory_elemental_gravity", src="armory", name="Elemental Gravity sword", kind="Weapon_Longsword", weight="-", tier="cobalt",
         role="mythic", ids=["Weapon_Elemental_Gravity"], note="Spellblade, Earth - Zone 3 Longsword Mythic (Void Golem's zone)"),
    dict(key="armory_elemental_ice", src="armory", name="Elemental Ice sword", kind="Weapon_Longsword", weight="-", tier="adamantite",
         role="mythic", ids=["Weapon_Elemental_Ice"], note="Spellblade, Water - Zone 4 Longsword Mythic (Dragon_Frost's zone)"),
    dict(key="armory_elemental_flame", src="armory", name="Elemental Flame sword", kind="Weapon_Longsword", weight="-", tier="mithril",
         role="mythic", ids=["Weapon_Elemental_Flame"], note="Spellblade, Fire - Zone 5 Longsword Mythic (Dragon_Fire's zone)"),
    dict(key="armory_runeblade", src="armory", name="Rune Blade", kind="Weapon_Club", weight="-", tier="adamantite", role="mythic",
         ids=["RuneBladeStage1"], note="stage 1 (club); stages 2 / 3 = an upgrade at our bench later (Pack-Armor-Plan 3.3 b)"),
    dict(key="armory_runeblade_up", src="armory", name="Rune Blade stages 2-3", kind="Weapon_Battleaxe", weight="-", tier="adamantite",
         role="off", ids=["RuneBladeStage2", "RuneBladeStage3"], note="upgrade chain later - never a drop"),
    dict(key="armory_dual_runeblade", src="armory", name="Dual Rune Blade", kind="Weapon_Daggers", weight="-", tier="adamantite",
         role="mythic", ids=["DualRuneBlade"], note="Assassin - Zone 4 Daggers Mythic"),
    dict(key="armory_lahat", src="armory", name="Lahat Chereb", kind="Weapon_Mace", weight="-", tier="adamantite", role="mythic",
         ids=["LahatChereb"], note="Legendary mace, Berserker (LOCKED 2026-10-08) - Zone 4 Mace Mythic"),
    dict(key="armory_hepta", src="armory", name="Hepta Axe", kind="Weapon_Battleaxe", weight="-", tier="adamantite", role="ut",
         ids=["Hepta_Axe"], note="Developer quality, no recipe (like the developer bows that became UT)"),
    dict(key="armory_zweihander", src="armory", name="Zweihander", kind="Weapon_Mace", weight="-", tier="mithril", role="mythic",
         ids=["Zweihander"], note="Warrior (Skyy 2026-10-08) on a mace moveset, their Lv 40 = Mithril band start - Zone 5 Mace Mythic"),
    dict(key="armory_fist", src="armory", name="Armory Fist", kind="Weapon_Sword", weight="-", tier="adamantite", role="off",
         ids=["Fist"], note="Monk boss drop (LOCKED 10-08) but no fist bag type yet and a sword template: check in game first (Q8)"),
    dict(key="armory_dualswords", src="armory", name="Iron Dual Swords", kind="Weapon_Daggers", weight="-", tier="iron", role="off",
         ids=["Weapon_Dualswords_Iron"], note="unfinished in their mod (vanilla Iron Sword model / name) - never a drop"),
    # ---------------------------------------------------------------- Void Armor (CC BY-NC, allowed) - ids NOT scanned yet
    dict(key="void_copper", src="voidarmor", name="Void Copper", kind="armor", weight="Heavy", tier="copper", role="drop", ids=[], note=""),
    dict(key="void_iron", src="voidarmor", name="Void Iron", kind="armor", weight="Heavy", tier="iron", role="drop", ids=[], note=""),
    dict(key="void_thorium", src="voidarmor", name="Void Thorium", kind="armor", weight="Heavy", tier="thorium", role="drop", ids=[], note=""),
    dict(key="void_adamantite", src="voidarmor", name="Void Adamantite", kind="armor", weight="Heavy", tier="adamantite", role="drop", ids=[],
         note=""),
    dict(key="void_mithril", src="voidarmor", name="Void Mithril", kind="armor", weight="Heavy", tier="mithril", role="mythic", ids=[],
         note="the only top-zone candidate (survey D) - Zone 5 Heavy Mythic"),
    dict(key="void_weapons", src="voidarmor", name="Void Mithril weapons", kind="Weapon_Sword", weight="-", tier="mithril", role="drop",
         ids=[], note="sword / longsword / shortbow / daggers / hammer: one row per type once the ids are known"),
    # ---------------------------------------------------------------- TODO: waiting on the authors' OK (never active, never in a jar)
    dict(key="slvr_wool", src="slvr", name="SLVR Wool robes", kind="armor", weight="Cloth", tier="crude", role="drop",
         ids=["SLVR_Armor_Wool_" + s for s in ("Head", "Chest", "Hands", "Legs")], note=""),
    dict(key="slvr_linen", src="slvr", name="SLVR Linen robes", kind="armor", weight="Cloth", tier="copper", role="drop",
         ids=["SLVR_Armor_Cloth_Linen_" + s for s in ("Head", "Chest", "Hands", "Legs")], note=""),
    dict(key="slvr_cotton", src="slvr", name="SLVR Cotton robes", kind="armor", weight="Cloth", tier="iron", role="mythic",
         ids=["SLVR_Armor_Cloth_Cotton_" + s for s in ("Head", "Chest", "Hands", "Legs")], note="would fill Zone 1 Cloth Mythic"),
    dict(key="slvr_silk", src="slvr", name="SLVR Silk robes", kind="armor", weight="Cloth", tier="thorium", role="mythic",
         ids=["SLVR_Armor_Cloth_Silk_" + s for s in ("Head", "Chest", "Hands", "Legs")], note="would fill Zone 2 Cloth Mythic"),
    dict(key="slvr_raven", src="slvr", name="SLVR Raven robes", kind="armor", weight="Cloth", tier="cobalt", role="drop",
         ids=["SLVR_Armor_Cloth_Raven_" + s for s in ("Head", "Chest", "Hands", "Legs")], note=""),
    dict(key="slvr_cindercloth", src="slvr", name="SLVR Cindercloth robes", kind="armor", weight="Cloth", tier="adamantite", role="drop",
         ids=["SLVR_Armor_Cloth_Cindercloth_" + s for s in ("Head", "Chest", "Hands", "Legs")], note=""),
    dict(key="fk_frostbite", src="fyrrage_fk", name="Frostbite Warden", kind="armor", weight="Heavy", tier="cobalt", role="drop", ids=[], note=""),
    dict(key="fk_dune", src="fyrrage_fk", name="Dune Walker", kind="armor", weight="Light", tier="thorium", role="drop", ids=[],
         note="weight from the page text (fabric + metal) - check the jar"),
    dict(key="fk_scorched", src="fyrrage_fk", name="Scorched Heart", kind="armor", weight="Heavy", tier="adamantite", role="drop", ids=[], note=""),
    dict(key="fk_neptune", src="fyrrage_fk", name="Neptune's Elite", kind="armor", weight="Heavy", tier="thorium", role="drop", ids=[], note=""),
    dict(key="fk_crystalwood", src="fyrrage_fk", name="Crystalwood", kind="armor", weight="Light", tier="thorium", role="mythic", ids=[],
         note="would fill Zone 2 Light Mythic (or swap with Engineering Rig)"),
    dict(key="fk_soulcage", src="fyrrage_fk", name="Soul Cage armor", kind="armor", weight="Heavy", tier="mithril", role="drop", ids=[],
         note="name clashes with our SkyyArmory Soul Cage wand (survey C) - rename in our lang only"),
    dict(key="fk_fen", src="fyrrage_fk", name="Fen Stalker", kind="armor", weight="Light", tier="thorium", role="drop", ids=[], note=""),
    dict(key="out_berserker", src="fyrrage_out", name="Outlanders Berserker", kind="armor", weight="Heavy", tier="thorium", role="drop", ids=[], note=""),
    dict(key="out_hunter", src="fyrrage_out", name="Outlanders Hunter", kind="armor", weight="Light", tier="thorium", role="drop", ids=[], note=""),
    dict(key="out_priest", src="fyrrage_out", name="Outlanders Priest", kind="armor", weight="Cloth", tier="thorium", role="drop", ids=[], note=""),
    dict(key="out_marauder", src="fyrrage_out", name="Outlanders Marauder", kind="armor", weight="Heavy", tier="cobalt", role="drop", ids=[], note=""),
    dict(key="out_stalker", src="fyrrage_out", name="Outlanders Stalker", kind="armor", weight="Light", tier="cobalt", role="mythic", ids=[],
         note="would fill Zone 3 Light Mythic"),
    dict(key="out_sorcerer", src="fyrrage_out", name="Outlanders Sorcerer", kind="armor", weight="Cloth", tier="cobalt", role="drop", ids=[], note=""),
    dict(key="ek_knights", src="elemental", name="Elemental Knights (4 sets)", kind="armor", weight="Heavy", tier="adamantite", role="drop",
         ids=[], note="Frost / Poison / Fire / Electric Knight + weapons (bow / daggers for Archer / Assassin)"),
    dict(key="st_ninja", src="stonedturtle", name="Ninja", kind="armor", weight="Light", tier="iron", role="drop", ids=[], note=""),
    dict(key="st_blood", src="stonedturtle", name="Blood Armor", kind="armor", weight="Heavy", tier="adamantite", role="drop", ids=[], note=""),
    dict(key="st_magical", src="stonedturtle", name="Magical Armor", kind="armor", weight="Cloth", tier="mithril", role="mythic", ids=[],
         note="would fill Zone 5 Cloth Mythic"),
]


def zone_of(tier):
    return TIER_ZONE[tier]


def tag_of(tier):
    """the tier tag our tooltip shows first in a pack item's flavour line ("T2 Iron", "T1 Crude"; tools/tier_tags.py numbering + word)"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import tier_tags as TT
    return TT.tag_text(TT.metal_tier(TIER_WORD[tier]), TT.metal_word(TIER_WORD[tier]))


def active_sets():
    """the sets that go into the jar: source status "on", role not "off", at least one id"""
    return [s for s in SETS if SOURCES[s["src"]]["status"] == "on" and s["role"] != "off" and s["ids"]]


def rows():
    """one row per id of the active sets: (id, set index into active_sets(), kind, weight index 0 / 1-3, tier, zone, role index 0-2)"""
    out = []
    for k, s in enumerate(active_sets()):
        for i in s["ids"]:
            out.append((i, k, s["kind"], 0 if s["kind"] != "armor" else WEIGHTS.index(s["weight"]) + 1, s["tier"], zone_of(s["tier"]),
                        ROLES.index(s["role"])))
    return out


def check():
    """the table's own rules (the SkyyGear build runs this too); returns the list of problems (empty = OK)"""
    bad = []
    keys = set()
    seen = {}
    for s in SETS:
        if s["key"] in keys:
            bad.append("duplicate set key " + s["key"])
        keys.add(s["key"])
        if s["src"] not in SOURCES:
            bad.append("%s: unknown source %s" % (s["key"], s["src"]))
        if s["role"] not in ROLES:
            bad.append("%s: unknown role %s" % (s["key"], s["role"]))
        if s["tier"] not in TIER_ZONE:
            bad.append("%s: unknown tier %s" % (s["key"], s["tier"]))
        if s["kind"] == "armor":
            if s["weight"] not in WEIGHTS:
                bad.append("%s: armor needs a weight Heavy / Light / Cloth" % s["key"])
        elif s["kind"] not in WEAPON_TYPES:
            bad.append("%s: %s is not a weapon bag type" % (s["key"], s["kind"]))
        # Skyy 2026-10-17 "always make the UT and mythic the highest tier of that zone"
        if s["role"] in ("ut", "mythic") and s["tier"] not in [t for z, t in ZONES] + ["onyxium"]:
            bad.append("%s: a %s set must sit at its zone's top tier (%s is not one)" % (s["key"], s["role"], s["tier"]))
        for i in s["ids"]:
            if not i or any(c in i for c in " ,=*\"\\") or not all(32 < ord(c) < 127 for c in i):
                bad.append("%s: bad id %r" % (s["key"], i))
            if i in seen:
                bad.append("id %s is in two sets (%s, %s)" % (i, seen[i], s["key"]))
            seen[i] = s["key"]
            if i.startswith("Skyy") or i.startswith("Armor_") and s["src"] == "armory" and s["role"] != "off":
                bad.append("%s: %s looks like one of ours / a vanilla-family id" % (s["key"], i))
        if SOURCES[s["src"]]["status"] == "on" and s["role"] != "off" and not s["ids"]:
            bad.append("%s: an active set without ids" % s["key"])
    # one Mythic per zone x weight / weapon type (Skyy 2026-10-17: "2 ut but do 1 mythic")
    cell = {}
    for s in active_sets():
        if s["role"] == "mythic":
            c = (zone_of(s["tier"]), s["weight"] if s["kind"] == "armor" else s["kind"])
            if c in cell:
                bad.append("two active Mythic sets in zone %d %s: %s, %s" % (c[0], c[1], cell[c], s["key"]))
            cell[c] = s["key"]
    return bad


def slot_guess(i):
    """the armor slot an id's words suggest (listing only - SkyyGear reads the LIVE item's ArmorSlot)"""
    for w, sl in (("Helm", "Head"), ("Hat", "Head"), ("Hood", "Head"), ("Mask", "Head"), ("Crown", "Head"), ("Diadem", "Head"),
                  ("AmuletHead", "Head"), ("Scorpian", "Head"), ("_Head", "Head"), ("Gauntlets", "Hands"), ("Guantlets", "Hands"),
                  ("Sleeves", "Hands"), ("Bracers", "Hands"), ("_Hands", "Hands"), ("Leggings", "Legs"), ("Boots", "Legs"),
                  ("_Legs", "Legs"), ("Chest", "Chest"), ("Chesplate", "Chest"), ("Robes", "Chest"), ("Jacket", "Chest"),
                  ("Bandolier", "Chest"), ("PotionBelt", "Chest"), ("Rig", "Chest"), ("Amulet", "Chest"), ("_Chest", "Chest")):
        if w in i:
            return sl
    return "?"


def grid(md=False):
    """zone x weight / weapon type: 'N normal + UT candidates + Mythic' with set names"""
    cols = WEIGHTS + sorted(set(s["kind"] for s in SETS if s["kind"] != "armor" and s["role"] != "off"))
    lines = []
    if md:
        lines.append("| Zone (top tier) | " + " | ".join(c.replace("Weapon_", "") for c in cols) + " |")
        lines.append("|---" * (len(cols) + 1) + "|")
    for z, top in ZONES:
        cells = []
        for c in cols:
            ss = [s for s in SETS if s["role"] != "off" and zone_of(s["tier"]) == z and (s["weight"] == c or s["kind"] == c)]
            part = []
            for role, tag in (("drop", ""), ("ut", "UT "), ("mythic", "MYTHIC ")):
                for s in ss:
                    if s["role"] != role:
                        continue
                    st = SOURCES[s["src"]]["status"]
                    part.append(tag + s["name"] + ("" if st == "on" else " [%s]" % st.upper()))
            cells.append("; ".join(part) if part else "-")
        if md:
            lines.append("| %d (%s) | %s |" % (z, TIER_WORD[top], " | ".join(cells)))
        else:
            lines.append("Zone %d (top %s)" % (z, TIER_WORD[top]))
            for c, t in zip(cols, cells):
                lines.append("    %-17s %s" % (c, t))
    return "\n".join(lines)


AZ_PATH = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "install", "release", "package", "game", "latest", "Assets.zip")


def _items(z):
    """{id: json} of every Server/Item/Items json in one open archive (read-only)"""
    out = {}
    for n in z.namelist():
        if not (n.startswith("Server/Item/Items/") and n.endswith(".json")):
            continue
        try:
            j = json.loads(z.read(n).decode("utf-8-sig"))
        except Exception:
            continue
        if isinstance(j, dict):
            out[os.path.basename(n)[:-5]] = j
    return out


def scan(path, az=AZ_PATH):
    """READ-ONLY: (id, armor slot or '-', item level or '-', weapon?, weapon template) of every Server/Item/Items json in a mod archive.
    Armor / Weapon / ItemLevel follow the Parent chain (inside the archive, then vanilla Assets.zip when present) - most Armory weapons
    have only "Parent": "Template_Weapon_<Type>" (1.23.0 scan, 2026-10-17); the template = the first Template_Weapon_* parent."""
    with zipfile.ZipFile(path) as z:
        mine = _items(z)
    base = {}
    if az and os.path.isfile(az):
        with zipfile.ZipFile(az) as z:
            base = _items(z)

    def field(i, f, d=0):
        j = mine.get(i) or base.get(i)
        if j is None or d > 12:
            return None
        if f in j:
            return j[f]
        return field(j.get("Parent"), f, d + 1) if j.get("Parent") else None

    def tmpl(i, d=0):
        j = mine.get(i) or base.get(i)
        if j is None or d > 12:
            return "-"
        if i.startswith("Template_Weapon_"):
            return i
        return tmpl(j.get("Parent"), d + 1) if j.get("Parent") else "-"

    out = []
    for i in sorted(mine):
        a = field(i, "Armor")
        a = a if isinstance(a, dict) else None
        w = isinstance(field(i, "Weapon"), dict)
        if a is None and not w:
            continue
        lv = field(i, "ItemLevel")
        out.append((i, (a or {}).get("ArmorSlot", "-"), "-" if lv is None else lv, w, tmpl(i) if w else "-"))
    return out


COIN_WORDS = ("value", "price", "sell", "coin", "worth")


def coin_keys(path):
    """READ-ONLY (the SkyyGear build's coin-loop guard, critic fix 7): [(id, key)] for every table id inside a mod archive whose item
    json (or a Parent inside the archive) has a TOP-LEVEL key naming a price - none today (vanilla items have no such field either); a
    future Armory update that adds one must be looked at before our Bazaar / Coins listings meet it"""
    with zipfile.ZipFile(path) as z:
        mine = _items(z)
    ids = set(i for s in SETS for i in s["ids"])
    out = []
    for i in sorted(ids & set(mine)):
        j, d = mine.get(i), 0
        while isinstance(j, dict) and d < 12:
            out += [(i, k) for k in j if any(w in k.lower() for w in COIN_WORDS)]
            j, d = mine.get(j.get("Parent")), d + 1
    return out


def main(argv):
    if "--scan" in argv:
        have = dict((i, s["key"]) for s in SETS for i in s["ids"])
        for p in argv[argv.index("--scan") + 1:]:
            print("# %s" % os.path.basename(p))
            for i, sl, lv, w, t in scan(p):
                print("%s\t%s\t%s\t%s\t%s\t%s" % (i, sl, lv, "weapon" if w else "armor", have.get(i, "-"), t))
        return 0
    if "--md" in argv:
        print(grid(md=True))
        return 0
    bad = check()
    act = active_sets()
    rw = rows()
    print(grid())
    print()
    for st in ("on", "needs-ids", "todo"):
        ss = [s for s in SETS if SOURCES[s["src"]]["status"] == st]
        print("%-10s %3d sets, %4d ids (%s)" % (st, len(ss), sum(len(s["ids"]) for s in ss),
                                               ", ".join(sorted(set(SOURCES[s["src"]]["mod"] for s in ss)))))
    print("active (into the jar): %d sets, %d ids - drop %d, ut %d, mythic %d sets" % (
        len(act), len(rw), sum(1 for s in act if s["role"] == "drop"), sum(1 for s in act if s["role"] == "ut"),
        sum(1 for s in act if s["role"] == "mythic")))
    for b in bad:
        print("PROBLEM:", b)
    print("OK" if not bad else "%d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
