"""Deploy the whole SkyWynn test set to the "HUD mod" world in one step - ONLY after Skyy says "deploy".

Usage (game closed):   python tools/deploy_set.py            -> shows the plan, asks for "yes"
                       python tools/deploy_set.py --yes      -> no question (Skyy already said deploy)
                       python tools/deploy_set.py --check    -> only checks that every jar exists

It does exactly what each build script's --deploy block does (B.deploy + B.enable_in_world with disable_prefix="Skyy:"), for every mod
in SET, using the jars that are ALREADY BUILT (it never rebuilds). It refuses to run while a Hytale server (HytaleServer.jar java
process) is running, because replacing a mod jar under a running server can break it. Mods not in SET are left alone.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skyybuild as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = "HUD mod"
# (mod, version) - keep in sync with HANDOFF section 3 "Versions"
SET = [
    ("SkyyHud", "0.3.17"), ("SkyySacks", "0.7.16"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.7"), ("SkyyParty", "0.1.7"),
    ("SkyyBank", "0.1.7"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.6"), ("SkyyGear", "0.2.11"), ("SkyySkills", "0.4.25"),
    ("SkyyAccessories", "0.5.9"), ("SkyyClasses", "0.1.14"), ("SkyyMenu", "0.3.12"), ("SkyyEssentials", "0.1.9"), ("SkyyProfiles", "0.1.7"),
    ("SkyyCooking", "0.1.6"), ("SkyyTrees", "0.3.3"),
    # Exploration round (research/Exploration-Build-Spec.md section 5): SkyySkills 0.4.1+ has the Exploration row, SkyyTrees 0.2+ the
    # Acrobatics + Exploration trees; never go back to SkyySkills 0.4 once Exploration XP exists (0.4 drops the unknown Exploration
    # keys on its next save)
    ("SkyyExploration", "0.2.5"),
    # party + guild round (Skyy 2026-09-24, 2-player test): SkyyHud's Party + Guild widgets read only the bridge keys SkyyParty 0.1.3
    # (party:fn:members / party:leader / party:name / party:stats) and SkyyGuilds (guild:<uuid> / guild:info / guild:fn:online) publish
    ("SkyyGuilds", "0.1.6"),
    # beta backlog round (Skyy 2026-09-24 20:10 list, cross-checked together): SkyySkills 0.4.2 + SkyyTrees 0.2.1 + SkyyCollections
    # 0.2.1 deploy TOGETHER (felled-log crediting: Skills -> coll:fn:add "skills:felled" + skill:on:felled; Double Jump: Trees posts
    # skill:bonus "doublejump.acrobatics", Skills publishes skill:dj:key); SkyyTrees 0.2.1 rewrites Acrobatics.RDodge as RDouble on
    # the next save, so do not go back to SkyyTrees 0.2 after it ran. SkyyIslands 0.5 migrates island files at start (0.4.x copies
    # kept as <key>.properties.v4bak). SkyyMenu 0.1.3 runs /island menu, /bank, /vault, /reforge, /party, /guild of the pins here.
    ("SkyyVault", "0.1.5"),
    # auction house (Skyy 2026-09-24, BIN only; research/Auction-House-Spec.md). Merges into SkyyEconomy 0.1 later (SkyyEconomy-Plan.md)
    ("SkyyAuctions", "0.1.2"),
    # in-game server setup (research/Server-Setup-Spec.md): SkyyMenu 0.3 = player Settings (0.2) + admin Server Setup / Mods section;
    # SkyyRanks 0.1 = ranks + grants + per-player denies + chat prefix, made in game (never removes hytale:Adventurer).
    # SkyyIslands 0.5.1 = SECURITY hotfix (0.5 gave every player skyyislands.admin through /island reload) - never deploy 0.5 again.
    ("SkyyRanks", "0.1.1"),
    # vanilla UI pass (2026-09-29): DEV/TEST mod - /skyprobe (admin only) opens the shared kit's probe pages so Skyy can confirm the
    # vanilla look works inline before any restyled page ships. Move it to RETIRED once the probe results are in.
    ("SkyyUiProbe", "0.4"),
    # gathering probe pack P0 (2026-10-06, research/Gathering-Progression-Spec.md): op-only dev mods for ONE test session - remove BOTH after Skyy's
    # test. SkyyGatherProbeB-0.1.jar is built into SkyyGatherProbe/ and moved to SkyyGatherProbeB/ by hand.
    ("SkyyGatherProbe", "0.1"), ("SkyyGatherProbeB", "0.1"),
    # FLOOR (2026-10-07): never roll SkyyArmory below 0.1.6 once spellbooks / kunai exist in player hands (15 new item ids -> unknown
    # items). SkyyGear below 0.2.8 with Armory 0.1.6 shows the new kunai as Lv 20-27 and changes the vanilla Weapon_Kunai damage base
    # (no data loss). Armory 0.1.6 + Classes 0.1.13 + Gear 0.2.8 deploy TOGETHER.
    # FLOOR (2026-10-07): never roll SkyyArmory below 0.1.7 once Bo staffs / hand wraps / gauntlets exist in player hands (new item
    # ids -> unknown items). Armory 0.1.7 + Gear 0.2.9 deploy TOGETHER (Gear 0.2.9 scales the Monk weapons; 0.2.8 under-scales them).
    # FLOOR (2026-10-07, Monk + Assassin playable): SkyyClasses 0.1.14 + SkyySkills 0.4.21 + SkyyProfiles 0.1.6 + SkyyMenu 0.3.9 deploy
    # TOGETHER (never Classes 0.1.14 without Skills 0.4.21 - the Monk would earn no XP). Roll back below them only if no Monk profile
    # exists; otherwise roll back all four together and expect classless Monk profiles (no items / coins / XP lost; Combat.Shaman kept).
    # FLOOR (2026-10-08, perks25): before rolling SkyySkills below 0.4.25 switch "Class Stamina" and "Class balance boost" OFF in Server
    # Setup and let players log in once (0.4.24 never removes the saved modifiers skyyskill_classstamina / classboosthp / classboostmana / classbooststamina).
    # FLOOR (2026-10-08, loot round): never roll SkyyGear below 0.2.11 without first setting unid.bags=false and having players identify every
    # mystery bag (bags become unknown items in 0.2.10). Never roll SkyyExploration below 0.2.4 without first setting luggage.enabled=false,
    # visiting each world until /exploreadmin stats shows out 0 / claimed 0, then deleting Skyy_SkyyExploration/luggage/. SkyyMobs 0.1.5: no floor.
    # FLOOR (2026-10-08, class path trees): rolling SkyyTrees back to 0.3.2 loses players' path picks (nothing else; 0.3.2 reads the
    # migrated files). SkyyArmory 0.1.9 is safe with Trees 0.3.2 (reads 0 for every node).
    # SkyyFishing 0.1 (2026-10-08, stage 1): takes over the reel probe's rod ids + SkyyFishing_Reel stat. Rollback floor: once players hold
    # fishing items, removing SkyyFishing turns rods / reels / parts / fish into unknown items.
    ("SkyyFishing", "0.1.1"),
    # mob levels (Skyy 2026-10-02, Q&A round 5): NEW standalone mod, stage 1 - hostile mobs + neutral fighters get a level from the
    # zone / biome they spawn in, more health + damage per level (Difficulty), "[Lv 9] Name" plates, /mobs, mob:fn:level. No dependency,
    # no data migration, nothing else needs a bump.
    ("SkyyMobs", "0.1.5"), ("SkyyWorldGen", "0.1"),
    # Zone 1 town probe (2026-10-08, admin-only, test island only): REMOVE after Skyy's test - run /townprobe undo until "Nothing to undo" first.
    ("SkyyTownProbe", "0.1"),
    # key probe (2026-10-08, op only): which client keys reach the server -> class ability hotkeys. REMOVE after Skyy's test.
    ("SkyyKeyProbe", "0.2"),
    # SkyyMerchants 0.1 (2026-10-09, roaming merchants): no dependency. Rollback: set part.merchants=false, let each zone world be visited
    # until /merchantadmin list shows no merchant out, then remove the jar (else Temple_Klops NPCs named "Traveling Merchant" stay).
    ("SkyyMerchants", "0.1"),
    # SkyyArmory round (2026-10-03): SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 deploy TOGETHER (the 8 ladder staffs move from
    # SkyySkills to SkyyArmory; the wand heal caps read SkyyArmory).
    # 0.1.10 (2026-10-08 hotfix): the 7 spellbook Levitate interactions no longer use a one-entry Parallel (the server refused 0.1.6-0.1.9).
    # 0.1.11 (2026-10-08): Bo staffs lose the charged magic orb (one shared swing root); the vanilla Wood / Bamboo Bo stay SkyySkills' until 0.4.22 hands them over.
    ("SkyyArmory", "0.1.14"),
    # 2026-10-06 evening: SkyySkills 0.4.19 (dodge move gate, no Acrobatics XP cap - roll back only after Undo of acro.maxXpPerMinute 240 -> 0),
    # SkyyHud 0.3.14 (minimap widget, needs BetterMap), SkyyGear 0.2.6 (weapon speed tiers, weapons only).
    # Mob curve (2026-10-06, research/Mob-Curve-Spec.md): SkyyMobs 0.1.4 + SkyyGear 0.2.5 + SkyySkills 0.4.17 TOGETHER (STOP check below). Never roll
    # one back alone; rolling all three back = Undo the "strength.shape linear -> curve" change first (or 0.1.3 runs per level with the file's values).
    # 2026-10-06 night: SkyyArmory 0.1.4 (blink.distance 10 -> 16 + blink.floorCheck 12 -> 0, one-time migration of untouched lines; rolling back
    # keeps 16 / 0 in the file) + SkyyGear 0.2.7 (Charged trust for the two _Wynn crossbows). No other data change; each rolls back alone.
    # SkyyArmory 0.1.3 (2026-10-06 evening): bow leap + blast, wand hang, particle lifespans, hop.force 30, crossbows Weapon_Crossbow_Copper_Wynn /
    # _Onyxium_Wynn. Rolling back below 0.1.3 leaves those crossbow stacks as unknown items - avoid once players crafted them.
    # SkyyArmory 0.1.2 (2026-10-06): crossbow Grapple Bolt (right click = grapple, replaces the guard) + trav.staminaCap 10 -> 5 (one-time
    # migration of an untouched 10 only). Rolling back to 0.1.1 brings the guard back; the cap line stays 5 (hand-edit back if wanted).
    # Traversal round (2026-10-06): SkyyClasses 0.1.12 -> SkyyArmory 0.1.1 -> SkyyGear 0.2.4 together (staff blink, wand hop / burst / heal orb,
    # quick shots; research/Magic-Traversal-Spec.md). No saved-data change; roll back all three together.
    # Sell from bags (2026-10-06): SkyyBazaar 0.1.5 needs SkyySacks 0.7.13 for bag sales (sacks:fn:count/all/take/put/commit); with an older
    # SkyySacks it behaves like 0.1.4. No data migration - rolling either back is safe.
    # Lantern-behind-Tree-Sap (2026-10-06): SkyyCollections 0.2.7 + SkyyAccessories 0.5.6 deploy TOGETHER (coll:lantern bridge; Accessories 0.5.6
    # with Collections 0.2.6 = every Lantern craftable). Rolling back is safe (no data rewritten; Lanterns go back to plain Workbench recipes).
]
# round 6 (2026-09-25): SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2 deploy TOGETHER (Berserker/Fury, Priest/Divinity, class kits;
# Profiles 0.1.1 only draws 6 class cards). Never go back to SkyySkills 0.4.3 once Fury/Divinity XP exists (0.4.3 drops those keys).
# adoption round (2026-09-25): the 16 bumps above register their admin settings (tools/skyycfg.py -> Server Setup) + player Settings
# switches; they need SkyyMenu 0.3. SkyyProfiles 0.1.1 raises an untouched maxProfiles=4 file to 6 (Skyy's 6-profile default).
# third-party mods that are part of the pack (enabled in the world by their manifest key; their files are NOT in this repo -
# a server owner installs them from their authors, see PACK.md). Never disabled by this script.
# 2026-10-06 (Skyy: "add hyfishing right now, along side dynamic season"): HyFishing (fishing until our own fishing mod replaces it) + Dynamic
# Seasons (its fishing seasons must keep working with our fishing mod later). Both only need Hytale modules; Dynamic Seasons optionally
# integrates Angler's Almanac / HyFishing.
PACK_THIRD_PARTY = ["Serj:More Crossbow Tiers", "Helios:Saplings From Trees", "TheRedlotus:HyFishing", "BlueOrbit:DynamicSeasons",
                    "NoCube:[NoCube's] Orchard",
                    "dev.ninesliced:BetterMap",
                    "Frah:Better Mob Expansion"]  # 2026-10-09 Skyy: test BME main mod (GPLv3, credit in PACK.md + server credits); Humans add-on stays OFF ("No guns")  # 2026-10-08 Skyy: "switch the armory on" - CC BY-NC (credit, never sell; PACK.md); combat armor + Warrior / Berserker / Assassin weapons + boss specials (research/Pack-Armor-Plan.md)  # 2026-10-06: the SkyyHud 0.3.14 minimap reads the map it streams (AGPL - never bundled, never called)  # 2026-10-06 Skyy: fruit trees, Fruit Press + juices (modpacks allowed by its page)
# Advanced Farming was NOT added (Skyy 2026-10-06: out of date, no longer updated -> build its tools into our own mod).
# Skyy mods that were MERGED into another mod and must be switched OFF in the world config on every deploy (their jar may stay in Mods;
# a disabled key is not loaded). Without this, deploy_set only disables older versions of the SAME mod name, and a retired mod would keep
# loading next to its replacement (duplicate commands, two systems). Example: SkyyRolls once SkyyGear replaces it; SkyyCoins, SkyyBank,
# SkyyBazaar and SkyyAuctions once SkyyEconomy replaces them. A name here must not also be in SET.
# round 8 (2026-09-28): SkyySacks 0.7.7 + SkyyCollections 0.2.3 deploy TOGETHER (bag recipe ids, coll:fn:where, migrated rewards file).
# Never roll back below SkyySacks 0.7.7 (Rare/Omni bags + Skyy_Bag_* qualities), SkyySkills 0.4.6 (saved max modifiers - switch Base Mana
# and Overall Level OFF and let players log in once first), or SkyyCollections 0.2.3 without restoring rewards-0.2.properties.
# round 9 + SkyyGear (2026-09-29): SkyyGear 0.1 REPLACES SkyyRolls (migrates SkyyRolls rolls on first touch; SkyyRolls switched off
# below). SkyyAuctions 0.1.2 + SkyyMenu 0.3.3 deploy with SkyyGear 0.1 (gear text, Identify tile). SkyyClasses 0.1.7 needs SkyySkills 0.4.6+.
# Never roll back below SkyyTrees 0.2.4 (Double Jump slot moved in saves). Rolling SkyyAuctions back to 0.1.1: restore 48h:1200 in its
# config.properties by hand first (0.1.1 cannot read 48h:x2).
# vanilla UI pass (2026-09-30): Skyy opened probe pages base1-base4 in game with no disconnect -> the 12 look-only restyles ship:
# Bank 0.1.4, Party 0.1.6, Accessories 0.4.5, Classes 0.1.8, Profiles 0.1.3, Vault 0.1.4, Collections 0.2.4, Guilds 0.1.4 (+ xpSkills
# mid-run fix), Islands 0.5.4, Skills 0.4.7 + Trees 0.2.5 + Exploration 0.2.2 (together). Rolling any of them back to the previous pin
# is safe (no data migration); the rollback floors above still apply.
# SkyyProfiles 0.1.5 (2026-10-01): profile delete + 6-hour undo + admin archive. ROLLBACK FLOOR once any profile was deleted:
# 0.1.4 treats a deleted profile as live again and can reuse an archived profile's id (the new profile would inherit its
# island, coins and bags) - never roll Profiles back below 0.1.5 after a delete.
# SkyyGear 0.2.2 (2026-10-03): wand / staff shot lines, Damage Data box hidden per type (row view.hideDamageBox, restart), crit popup + sparks; no migration - rolling back to 0.2.1 is safe (the box comes back on the next start).
# SkyyGear 0.2.1 (2026-10-03): rolling back to 0.2 is safe - 0.2 ignores the 0.2.1 config block, re-renders the tooltips and clears the
# armor Health lock bonus within one second. The floor stays 0.2.
# SkyyGear 0.2 (2026-10-02): ROLLBACK FLOOR - never roll SkyyGear below 0.2 without first restoring the config History copy
# 'before the 0.2 level bands' (Server Setup -> History): 0.1.3 cannot read '<min>,<cap>' rows, so items would fall back to Hytale's
# own item level (the kit wand / staff would read about Lv 40). Items themselves are safe to roll back.
# SkyyMobs 0.1.3 (2026-10-03): client health-bar fix only (MobLevel.writeValue: min/maxStatValue after a modifier change); no saved-data change - rolling back to 0.1.2 is safe.
# SkyyMobs 0.1 (2026-10-02): rolling it back = take it out of SET and add "SkyyMobs" to RETIRED. Saved mobs keep a Health modifier
# 'skyymobs_lv<N>' and a '[Lv N] Name' plate until they die; to strip them first: Server Setup > Mobs > Never level these = * , then
# walk / reload the chunks, then retire. Settings stay in mods/Skyy_SkyyMobs.
# SkyyWorldGen 0.1 (2026-10-03, NEW): removing it after /zone 1 has run = stop the server and delete
# Saves/HUD mod/universe/worlds/skywynn_z1 FIRST (the saved island names the WorldStructure SkyWynn_Z1_Small from the jar; without the
# jar the generator falls back to empty chunks and saves void into the island), then take it out of SET and add "SkyyWorldGen" to
# RETIRED. Settings stay in mods/Skyy_SkyyWorldGen.
# SkyyTrees 0.3 (2026-10-03): ROLLBACK FLOOR - never roll SkyyTrees below 0.3 once it saved a player file (0.2.5 drops every Alchemy /
# Smithing / class node level on its next save and leaves the skyytree_mana modifier unmanaged; Tokens / Dust are computed, nothing else is
# lost). Respec Alchemy + Smithing (+ class) first if a rollback is unavoidable.
# SkyyArmory 0.1 + SkyySkills 0.4.15 + SkyyClasses 0.1.11 (2026-10-03): deploy and roll back TOGETHER. Before SkyySkills goes below 0.4.15:
# switch Base Mana off and let players log in once. To roll SkyyArmory back: take it out of SET, add it to RETIRED and put SkyySkills back
# to 0.4.14 in the same deploy (vanilla staff files would charge 50 Mana behind a 10-Mana check otherwise). SkyyClasses back to 0.1.10 is safe.
RETIRED = ["SkyyRolls", "SkyyMonkProbe", "SkyyReelProbe"]   # SkyyMonkProbe: tested 2026-10-08 (TEST 48), the real moves are SkyyArmory 0.1.12


# Third-party pack mods switched OFF in the world on every deploy (kept installed).
# 2026-10-09 Skyy: "Armory off until 0.7" - The Armory (708 textures) overflowed the client item/creature texture atlas
# (8192x16384 needed, max 8192x8192: 395 of 2808 images dropped = broken copper ore, talismans, swords). Re-test on Hytale 0.7.
PACK_DISABLED = ["LadyPaladra:TheArmory"]


def disable_third_party(world, key):
    import json
    cfg = os.path.join(B.USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    if mods.get(key, {}).get("Enabled"):
        mods[key] = {"Enabled": False}
        json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
        print("world", world, "switched off", key)


def retire_in_world(world, mod):
    """Disable every world-config key 'Skyy:<ver> <mod>' (all versions). Returns how many were switched off."""
    import json
    cfg = os.path.join(B.USERDATA, "Saves", world, "config.json")
    d = json.load(open(cfg, encoding="utf-8"))
    mods = d.setdefault("Mods", {})
    n = 0
    for k in list(mods):
        if k.startswith("Skyy:") and k.endswith(" " + mod) and mods[k].get("Enabled"):
            mods[k] = {"Enabled": False}
            n += 1
    json.dump(d, open(cfg, "w", encoding="utf-8"), indent=2)
    print("world", world, "retired", mod, "(%d key(s) switched off)" % n)
    return n


def server_running():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              # java.exe only: the query's own powershell command line contains the search text and would match itself
                              "Get-CimInstance Win32_Process -Filter \"Name = 'java.exe'\" | Where-Object { $_.CommandLine -like '*HytaleServer*' } | Measure-Object | Select-Object -ExpandProperty Count"],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return out not in ("", "0")
    except Exception as e:
        print("could not check for a running server:", e)
        return True


def newer_builds(mod, ver):
    """Versions of <mod>-<version>.jar on disk that are HIGHER than the pinned one. A note only: SET decides what deploys (a newer jar
    can be an unreviewed build), but it makes a forgotten SET bump visible instead of silently redeploying the old set."""
    import re
    def v(s):
        return tuple(int(x) for x in s.split("."))
    d = os.path.join(ROOT, mod)
    if not os.path.isdir(d):
        return []
    out = []
    for n in os.listdir(d):
        m = re.match(r"^%s-(\d+(?:\.\d+)*)\.jar$" % re.escape(mod), n)
        if m and v(m.group(1)) > v(ver):
            out.append(m.group(1))
    return sorted(out, key=v)


def main():
    bad = [a for a in sys.argv[1:] if a not in ("--yes", "--check")]
    if bad:   # 2026-09-24: builders ran it with --help and landed on the deploy prompt; unknown arguments now only print the usage
        print(__doc__)
        print("unknown argument(s): %s - nothing done" % " ".join(bad))
        return 2
    clash = [m for m in RETIRED if m in [x[0] for x in SET]]
    if clash:
        print("STOP: retired mod(s) still in SET: %s" % ", ".join(clash))
        return 1
    _p = dict(SET)
    _v = lambda s: tuple(int(x) for x in s.split("."))
    if (_v(_p.get("SkyySkills", "0")) >= (0, 4, 15)) != ("SkyyArmory" in _p):
        print("STOP: SkyySkills 0.4.15+ and SkyyArmory deploy together (the staff handover) - pin both or neither"); return 1
    if "SkyyArmory" in _p and _v(_p.get("SkyyClasses", "0")) < (0, 1, 11):
        print("STOP: SkyyArmory needs SkyyClasses 0.1.11+ (the wand heal caps) in the same deploy"); return 1
    # traversal round (2026-10-06): SkyyArmory 0.1.1 calls class:fn:heal (SkyyClasses 0.1.12) - never roll SkyyClasses below 0.1.12 while it is pinned
    if _v(_p.get("SkyyArmory", "0")) >= (0, 1, 1) and _v(_p.get("SkyyClasses", "0")) < (0, 1, 12):
        print("STOP: SkyyArmory 0.1.1+ needs SkyyClasses 0.1.12+ (class:fn:heal for the heal orb) in the same deploy"); return 1
    # mob curve round (2026-10-06): SkyyMobs 0.1.4 + SkyyGear 0.2.5 + SkyySkills 0.4.17 deploy and roll back TOGETHER (mob:fn:info, gear:fn:curve, the level gap)
    _mob = _v(_p.get("SkyyMobs", "0")) >= (0, 1, 4)
    if _mob and _v(_p.get("SkyyGear", "0")) < (0, 2, 5):
        print("STOP: SkyyMobs 0.1.4+ needs SkyyGear 0.2.5+ (gear:fn:curve, the gear level curves) in the same deploy"); return 1
    if _mob and _v(_p.get("SkyySkills", "0")) < (0, 4, 17):
        print("STOP: SkyyMobs 0.1.4+ needs SkyySkills 0.4.17+ (kill XP by mob level through mob:fn:info) in the same deploy"); return 1
    if (_v(_p.get("SkyyGear", "0")) >= (0, 2, 5) or _v(_p.get("SkyySkills", "0")) >= (0, 4, 17)) and not _mob:
        print("STOP: SkyyGear 0.2.5+ / SkyySkills 0.4.17+ deploy with SkyyMobs 0.1.4+ (the mob curve round) - pin all three or none"); return 1
    # monk moves round (2026-10-08): SkyySkills 0.4.22 stops shipping the vanilla Wood / Bamboo Bo -> SkyyArmory 0.1.11+ must own them
    if _v(_p.get("SkyySkills", "0")) >= (0, 4, 22) and _v(_p.get("SkyyArmory", "0")) < (0, 1, 11):
        print("STOP: SkyySkills 0.4.22+ needs SkyyArmory 0.1.11+ (the Wood / Bamboo Bo handover) in the same deploy"); return 1
    # wood wand signature (2026-10-08): SkyySkills 0.4.24 wands name SkyyArmory_Wand_Signature (SkyyArmory 0.1.14) - never roll Armory below 0.1.14 while Skills is 0.4.24+
    if _v(_p.get("SkyySkills", "0")) >= (0, 4, 24) and _v(_p.get("SkyyArmory", "0")) < (0, 1, 14):
        print("STOP: SkyySkills 0.4.24+ needs SkyyArmory 0.1.14+ (the root SkyyArmory_Wand_Signature it names) in the same deploy"); return 1
    missing = []
    plan = []
    for mod, ver in SET:
        jar = os.path.join(ROOT, mod, "%s-%s.jar" % (mod, ver))
        if not os.path.isfile(jar):
            missing.append(jar)
        plan.append((mod, ver, jar))
    for mod, ver, jar in plan:
        print("  %-16s %-6s %s" % (mod, ver, "OK" if os.path.isfile(jar) else "MISSING " + jar))
    newer = [(mod, ver, newer_builds(mod, ver)) for mod, ver in SET]
    newer = [x for x in newer if x[2]]
    if newer:
        print("NOTE: newer builds are on disk than SET pins (SET decides what deploys - bump it, and HANDOFF section 3, only for the "
              "builds Skyy approved):")
        for mod, ver, vs in newer:
            print("  %-16s pinned %-6s newer on disk: %s" % (mod, ver, ", ".join(vs)))
    if missing:
        print("STOP: %d jar(s) missing - build them first (python <build script>, no --deploy)." % len(missing))
        return 1
    if "--check" in sys.argv:
        print("all %d jars present" % len(plan))
        return 0
    if server_running():
        print("STOP: a Hytale server is running. Close the world / game first, then run this again.")
        return 1
    if "--yes" not in sys.argv:
        if input("Deploy these %d mods to world '%s'? type yes: " % (len(plan), WORLD)).strip().lower() != "yes":
            print("cancelled")
            return 1
    for mod, ver, jar in plan:
        B.deploy(jar, mod + ".jar")
        B.enable_in_world(WORLD, "Skyy:%s %s" % (ver, mod), disable_prefix="Skyy:")
    for key in PACK_THIRD_PARTY:
        B.enable_in_world(WORLD, key)
    for mod in RETIRED:
        retire_in_world(WORLD, mod)
    for key in PACK_DISABLED:
        disable_third_party(WORLD, key)
    print("deployed %d mods. Start the world and watch the server log for every '[Skyy...] ready' line." % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
