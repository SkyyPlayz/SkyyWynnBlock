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
    ("SkyyHud", "0.3.12"), ("SkyySacks", "0.7.12"), ("SkyyCoins", "0.1.5"), ("SkyyCollections", "0.2.5"), ("SkyyParty", "0.1.6"),
    ("SkyyBank", "0.1.6"), ("SkyyIslands", "0.5.5"), ("SkyyBazaar", "0.1.2"), ("SkyyGear", "0.2"), ("SkyySkills", "0.4.13"),
    ("SkyyAccessories", "0.5.3"), ("SkyyClasses", "0.1.10"), ("SkyyMenu", "0.3.5"), ("SkyyEssentials", "0.1.7"), ("SkyyProfiles", "0.1.5"),
    ("SkyyCooking", "0.1.4"), ("SkyyTrees", "0.2.5"),
    # Exploration round (research/Exploration-Build-Spec.md section 5): SkyySkills 0.4.1+ has the Exploration row, SkyyTrees 0.2+ the
    # Acrobatics + Exploration trees; never go back to SkyySkills 0.4 once Exploration XP exists (0.4 drops the unknown Exploration
    # keys on its next save)
    ("SkyyExploration", "0.2.2"),
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
    ("SkyyUiProbe", "0.3.1"),
    # mob levels (Skyy 2026-10-02, Q&A round 5): NEW standalone mod, stage 1 - hostile mobs + neutral fighters get a level from the
    # zone / biome they spawn in, more health + damage per level (Difficulty), "[Lv 9] Name" plates, /mobs, mob:fn:level. No dependency,
    # no data migration, nothing else needs a bump.
    ("SkyyMobs", "0.1.2"),
]
# round 6 (2026-09-25): SkyyClasses 0.1.6 + SkyySkills 0.4.4 + SkyyProfiles 0.1.2 deploy TOGETHER (Berserker/Fury, Priest/Divinity, class kits;
# Profiles 0.1.1 only draws 6 class cards). Never go back to SkyySkills 0.4.3 once Fury/Divinity XP exists (0.4.3 drops those keys).
# adoption round (2026-09-25): the 16 bumps above register their admin settings (tools/skyycfg.py -> Server Setup) + player Settings
# switches; they need SkyyMenu 0.3. SkyyProfiles 0.1.1 raises an untouched maxProfiles=4 file to 6 (Skyy's 6-profile default).
# third-party mods that are part of the pack (enabled in the world by their manifest key; their files are NOT in this repo -
# a server owner installs them from their authors, see PACK.md). Never disabled by this script.
PACK_THIRD_PARTY = ["Serj:More Crossbow Tiers", "Helios:Saplings From Trees"]
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
# SkyyGear 0.2 (2026-10-02): ROLLBACK FLOOR - never roll SkyyGear below 0.2 without first restoring the config History copy
# 'before the 0.2 level bands' (Server Setup -> History): 0.1.3 cannot read '<min>,<cap>' rows, so items would fall back to Hytale's
# own item level (the kit wand / staff would read about Lv 40). Items themselves are safe to roll back.
# SkyyMobs 0.1 (2026-10-02): rolling it back = take it out of SET and add "SkyyMobs" to RETIRED. Saved mobs keep a Health modifier
# 'skyymobs_lv<N>' and a '[Lv N] Name' plate until they die; to strip them first: Server Setup > Mobs > Never level these = * , then
# walk / reload the chunks, then retire. Settings stay in mods/Skyy_SkyyMobs.
RETIRED = ["SkyyRolls"]


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
    print("deployed %d mods. Start the world and watch the server log for every '[Skyy...] ready' line." % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
