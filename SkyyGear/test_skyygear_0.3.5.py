"""Harness for SkyyGear 0.3.5 = the 0.3.4 harness (every check kept) + VAULT SUMMON, HANDS = CRUDE, THE IDENTIFY REVEAL, THE LIFELONG POLE,
REBIRTH R7 (tools/gear_0_3_5_patch.py header). Build first:
    python tools/gear_0_3_5_patch.py && python SkyyGear/build_skyygear_0.3.5.py && python SkyyFishing/build_skyyfishing_0.1.5.py

    python SkyyGear/test_skyygear_0.3.5.py [--jar ..] [--old ..] [--j31 ..] [--j32 ..] [--j33 ..] [--j34 <SkyyGear-0.3.4.jar>] [--keep] [--only life,compare,..]

0.3.5: the 0.3.4 checks whose ANSWER this round changes keep the new expectation (each marked "0.3.5:"): hands / a sword count as a Crude hoe
on crops (L3 gate matrix, L4 / L11 farmTier, G33 / G33F now use Wheat / Carrot for "free" hands), KCRUDE has the pole (M), statusText names
the Vault (LT14), /lifelong names fishing rods (L8), the newest SkyyMerchants names Sigils only in its wall (S5), the fresh file gains the
0.3.5 block (D), C34 compares the 0.3.3 jar to the 0.3.4 jar. run_life loads SkyyFishing 0.1.5 (scratch copy) as a pack + on the classpath.
New (G35, one booted engine):
  V  VAULT SUMMON through a stand-in of SkyyVault 0.1.6's four functions (pending records + its start-up resolve): the closed-Vault fetch
     (find -> take -> place -> done), '!pending' / '!unreadable' / a refused take = try again (NEVER a copy), a stack that could not be
     placed -> putBack (+ / = / -), doneLL FALSE, CRASH POINTS 10 / 11 / 12 x the inventory saved or not + a restart (exactly one stack,
     no copy), no SkyyVault = the old exact copy
  H  HANDS = CRUDE on the REAL GearToolHitSys + GearChestOpenSys (bare hands / a sword / a pickaxe two up refused + popup, one up x0.4,
     own tier vanilla, berries free, gate.on off), gear:fn:farmTier answers
  R  THE IDENTIFY REVEAL on the REAL Anvil clicks (FakeReforgePage): a bag, an unidentified sword, re-identify, Identify all (12 bags ->
     the 10 best, best last), reveal FALSE / absent, revealOne
  P  THE POLE: kinds / tiers / level / no perks; gear:fn:pole stamping (same uid per grant, registry untouched, refusals); adoption on
     arrival; once (a 2nd claim = plain rod); drop / market walls; /pole copy + 'no pole yet'; /lifelong on a rod; END TO END with the
     REAL SkyyFishing 0.1.5 (fishing:fn:starter -> gear:fn:pole, the bench carry) + the upgraded pole's tier
  RB REBIRTH R7: rebirth:part:gear measure / prepare (crash 1, 2) / commit (crash 3, repeat = done) / abort / status / bad args; the waits;
     the world-thread apply (one registry write; crash 13 in a tool reset; the inventory not saved -> reset again; a tool in a chest reset
     on return; armor -> Copper, closes after 30 s); rebirth:fn:busy waits; the rebirth modifier (rebirth:fn:node x rebirthPct); a second
     rebirth; an older committed staged file; the multitool gate
  C35 CLASS COMPARE 0.3.4 -> 0.3.5: exactly the listed members differ, + GearRb / PoleCmd
Scratch: tools/dev/scratch/gear5/harness (deleted at the end unless --keep).

--- the 0.3.4 harness header ---

Harness for SkyyGear 0.3.4 = the 0.3.3 harness (every check kept) + SIGILS, GATHERING ARMOR THAT LEVELS, THE HOE TILL AREA
(tools/gear_0_3_4_patch.py header). Build first:
    python tools/gear_0_3_4_patch.py && python SkyyGear/build_skyygear_0.3.4.py

    python SkyyGear/test_skyygear_0.3.4.py [--jar <SkyyGear-0.3.4.jar>] [--old <SkyyGear-0.2.26.jar>] [--j31 ..] [--j32 ..] [--j33 <SkyyGear-0.3.3.jar>]
        [--j24 ..] [--keep]

0.3.4: the 0.3.3 checks whose ANSWER this round changes are kept with the new expectation (each marked "0.3.4:"): the Anvil ladders now also
hold garmor.ladders (part.lifelong off = upgrade.ladders + garmor.ladders); the jar ships the 5 Sigil items (S); the fresh config file gains
the 0.3.4 block (D). New:
  G34 (one booted engine, the real Sigil items from the jar's own pack):
      S1 the items + the 6 rows (defaults, danger flags, garmor.ladders through GearUp.checkLadders)
      S2 GearSigil.apply on a REAL inventory: skip tiers (Normal + Legendary Sigil = Legendary at once, lines kept, new slots empty, sgN, one
         Sigil spent), gear.log SIGIL-BEGIN / SIGIL, the next Reforge fills the slots, every refusal (upward only, none carried, stale
         fingerprint, Set / unidentified / stack / non-gear / Mythic / Untiered / part.sigils off), the Mythic Sigil + the market wall
      S3 the failure paths on MergeFail containers (the item's slot refuses -> both back; the Sigil's slot refuses -> nothing used) + a CRASH
         right after the Sigil left (Sigil lost and logged, item unchanged - never a copy)
      S4 a lifelong pickaxe stays lifelong (uid, tr 1); a /pickaxe copy is invested by a Sigil used after it was made (sgN over lrpS)
      S5 THE MARKET: callers generated in com.skyy.bazaar / com.skyy.merchants / com.skyy.auctions ask the REAL GearWall: Bazaar + NPC shop
         refused, Auction House allowed; the newest Bazaar / Merchants build scripts list no Sigil
      S6 THE ANVIL'S SIGIL STRIP on a FakeReforgePage: shown only while a Sigil is carried, Other, Apply (arm) -> Confirm, upward only, the
         656 px right column kept
      A1-A4 GATHERING ARMOR: skill / level rule (band clamp, no SkyySkills, garmor.levels off), the Mining level-up watch (RESYNC), the sync on a
         real inventory (armor + storage; unidentified / unstamped / other items untouched; idempotent; throttled), Reforge Level up refused,
         THE TIER-UP (check: Enchanted cost per slot, Mining level of the new tier, quest set / Mythic special, old rolled piece allowed;
         upgrade() in the ARMOR slot: Set rarity kept, set field moved, level by the rule)
      T1-T5 THE HOE TILL AREA: sides by tier + checkArea + a bad row; protection (island:perm:fn TRUE / FALSE / null + hoe.areaElsewhere);
         onChange on real lifelong hoe stacks (Iron 3x3, Thorium 5x5, Crude 1x1; obstacles; every 'no till' case); GearTillSys on REAL
         InventoryChangeEvents (hotbar + tools section; utility ignored) - block reads / writes through the harness seams
  TT  the till area on a REAL 0.7 ChunkStore (fixture child): resolve / blockAt / area through the engine's own section reads
  C34 CLASS COMPARE 0.3.3 -> 0.3.4: exactly the listed members differ, + GearArmLv / GearSigil / GearTill / GearTillSys
Not executed here (UNVERIFIED until the game): TargetUtil.getTargetBlock and BlockOperations.setBlock (signatures asserted at build time).

--- the 0.3.3 harness header ---

Harness for SkyyGear 0.3.3 = the 0.3.2 harness (every check kept) + NO HARVESTING TWO TIERS ABOVE YOUR HOE / SICKLE
(tools/gear_0_3_3_patch.py header). Build first:
    python tools/gear_0_3_3_patch.py && python SkyyGear/build_skyygear_0.3.3.py

    python SkyyGear/test_skyygear_0.3.3.py [--jar <SkyyGear-0.3.3.jar>] [--old <SkyyGear-0.2.26.jar>] [--j31 <SkyyGear-0.3.1.jar>]
        [--j32 <SkyyGear-0.3.2.jar>] [--j24 <SkyyGear-0.2.24.jar>] [--keep]

0.3.3 (Skyy 2026-10-14 "No. Cant break 2 tiers above"): the 0.3.2 checks whose ANSWER the new rule changes are kept with the new
expectation (each marked "0.3.3:"): a crop two or more tiers above the held hoe / sickle is REFUSED (decide answers 2, gear:fn:farmTier
answers 2); one up stays 1. New:
  G33 THE CROP GATE on the REAL GearToolHitSys + REAL crop BlockTypes + REAL DamageBlockEvents: every hoe (Crude / Copper / Iron / Thorium)
      and sickle (Crude / Copper / Iron) x every tier-table crop: own tier = the tool's own power, one up = x0.4 (not cancelled), two or more
      up (after the family cap) = CANCELLED with the damage untouched; bare hands, a sword, a non-crop plant (berries), gate.on off = never
      cancelled; ore / logs unchanged (a Copper pickaxe on thorium two up = x0.1, not cancelled); no sickle tier is ever refused; the
      refusal's popup CAPTURED from a capturing PacketHandler (title + "This crop needs at least an Iron hoe (Thorium for full Farming XP)");
      the counters; gear:fn:farmTier through the real bridge Function; statusText + the manifest sentence + the gate.on help
  G33F (fix round) THE F-HARVEST GATE on the REAL GearChestOpenSys + REAL UseBlockEvent$Pre (held item in a real InteractionContext):
      a Crude / Copper hoe on a two-up crop = CANCELLED + the same popup (captured), counted in N[0]; one up / own tier / an Iron hoe on a
      Potato / a Crude sickle / an empty hand / a sword / a berry plant / ore = not cancelled; creative = not cancelled; an event already
      cancelled = left alone (no popup); gate.on off = not cancelled
  C33 CLASS COMPARE 0.3.2 -> 0.3.3: exactly the listed members differ (C32 now compares 0.3.1 -> 0.3.2 jar to jar)

--- the 0.3.2 harness header ---

0.3.2 (Skyy 2026-10-13 "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"): the 0.3.1
checks whose ANSWER the new rule changes are kept with the new expectation (each marked "0.3.2:"): /pickaxe with the tool out of reach
gives an EXACT copy (same item, rarity, rolls) instead of a new Common one; lifelong.reclaimTier is a legacy row (on changes nothing). New:
  LT  THE EXACT LOST TOOL EXECUTED (same booted engine): the snapshot (made by the sweep, refreshed on a reforge, none for an unseen tool);
      the tracker (GearLL.trackMaybe gate -> GearLife.trackLater coalesced -> GearTrackTask -> GearLife.track) on a REAL ContainerBlockWindow
      and a REAL ContainerWindow (the Vault's kind) in a real WindowManager; /pickaxe: full inventory refused first, Requip fetch (ok / refused
      / not loaded / ok-but-missing), an open window (chest + Vault kind), the tracked chest (loaded / unloaded / another world / gone / tool
      moved on), the exact copy (rarity, lines, reforge name, perks + points, level, new uid + lcu, lrpF) + the wait (copies only), the legacy
      Common answer without a snapshot; THE DUPE PROOFS: the original turns up after the copy (copy removed / original retired when the copy
      was reforged AFTER copying), a chest another player has open (they took it first -> copy, theirs does nothing for them), a profile
      switch mid-summon (busy / another profile key -> nothing moves), a CRASH at every summon step (7, 8, 9) with the engine having saved
      the source, the target, both or neither - never two working tools, never a lost one (the exact copy is always one /pickaxe away);
      the move's own failure paths (source refuses, target refuses -> back in the source)
  C32 CLASS COMPARE 0.3.1 -> 0.3.2: exactly the listed members differ

0.3.1 (Skyy 2026-10-13 "if crude is also T1 it should take the normal amount of hits" + "x2.5  / X10   tiers above cannot be broken"):
the 0.3.0 checks whose ANSWER the new rule changes are kept with the new expectation (each marked "0.3.1:"): Crude / Wood count as tier 1,
1 up x gate.nextFactor (0.4), 2 up x gate.twoUpFactor (0.1, was refused), 3+ up refused; gate.crudeFactor = an unused legacy row; the
live copy (D) gains exactly the run-once marker line. New phases:
  G   THE 0.3.1 GATE MATRIX on the REAL hit system + real BlockTypes (Crude / Copper / Iron pickaxes and hatchets x ore / log tiers: normal,
      x0.4, x0.1, refused + the popups' words), only.farming + gear:fn:farmTier for Crude hoes, the rows, statusText; THE ONE-TIME UPDATE
      migrate031 (pure text: old default rewritten / hand-edited kept + noted / absent = marker only / marker = nothing / CRLF + other bytes
      kept / a continued line never rewritten; on a scratch file: History copy first, change-log row with Undo (ok), run twice = no change)
  C31 CLASS COMPARE 0.3.0 -> 0.3.1: exactly the listed members differ

The 0.2.11 harness's helpers (verify A, the bare-server boot, the engine-access audit AA, FakeStore / FakeChunk / FakeUtil) and the 0.2.22
stand-ins (MergeFail, FakeReforgePage, FakeMultiPage, FakePR) are loaded from their files; this harness adds FakePM (the page a command
opens) and FakeLifePage. Read-only sources are COPIED into scratch first: the live Skyy_SkyyGear folder (D), the live player files
(universe/players/*.json - their real tool stacks drive the migration, M), SkyyCollections 0.2.11 (the Enchanted items the tier-up costs
name) and SkyyArmory 0.1.23 + Multitools 1.2.9 (for the carried 0.2.26 Anvil child).
  S   non-class entries 0.2.26 -> 0.3.0: only the manifest changed; classes added = exactly the 0.3.0 set
  A   every class loads + verifies (-Xverify:all)
  C   CLASS COMPARE 0.2.26 -> 0.3.0: exactly the listed members differ (javassist members + resolved bytecode)
  R   THE 0.2.26 HARNESS'S ANVIL CHILD with this jar (N1-N13: reforge / upgrade / identify, every click and failure) - only the listed
      deviations (the tab row now has a Tools tab)
  X   THE 0.2.25 HARNESS'S RANDOMISED OLD-VS-NEW STATS COMPARISON with this jar against 0.2.24 (snapshot / tick / hits / gate / stamp scan)
  L   LIFELONG TOOLS EXECUTED (one booted engine, vanilla pack + SkyyCollections 0.2.11): rows; kinds / tiers / level rule; the registry;
      the gate matrix (every tool family x tier x block tier + bare hands + the wrong tool) and the REAL GearToolHitSys on REAL
      DamageBlockEvents / BlockTypes; only.farming; perks (points, tier need, reader gate, effects in GearTool.stats, reset for coins,
      refund on a failed write); the sweep (level sync, registry id, restore, remove, demote, foreign copies); /pickaxe (every refusal, the
      dupe guard, the cooldown, crash at every step); /lifelong; the tier-up on the Anvil (GearUp.check / upgrade); PROTECTION: the REAL
      GearLLDropSys on DropItemEvent$PlayerRequest (cancelled before anything moves), the engine's salvage matching (a lifelong tool never
      matches a recipe input), the market wall, the multitool merge, Reforge Level up; NO CRAFTING: the REAL GearCraftPreSys on a REAL
      CraftRecipeEvent$Pre (+ Creative, + a shovel), the Smithing Craft tab; the Tools page (layout, ids, clicks) + every command;
      gear:fn:lifelong / perk / farmTier; the tooltip lines
  FX  THE FIX ROUND (one check per critic finding fixed - see the "FIX" lines): another player's lifelong tool breaks nothing (real hit
      system); an invested /pickaxe replacement is never thrown away (settle / demote); /pickaxe gives the tier your skill fits
      (lifelong.reclaimTier, on / off); the held-tool level watch; at most 5 registry writes per migration; a cancelled drop from an open
      chest window marks the window changed; cactus keeps Fortune; gear:fn:farmTier takes an item id; the Requip hint; LL-MARK undo data
  FX2 THE SECOND FIX ROUND: the reforge-then-retrieve exploit (the original is RETIRED - still lifelong, never sold, breaks nothing, may be
      dropped - and /lifelong swaps it back); another player's lifelong tool may be dropped; lifelong.reclaimTier OFF by default (no free
      tier); an unreadable registry is read again after 30 s; a failing registry write WARNs once + the every-scan sweep waits; LL-MARK logs
      the old level + bought levels and says so; gate.crudeFactor; gear:fn:lifelong(UUID) -> Integer kinds owned
  M   THE MIGRATION ON THE LIVE PLAYERS' REAL TOOL STACKS (scratch copies): the best tool per kind, rolls kept, Crude Common gifts, counts;
      a CRASH AT EVERY STEP (1-6) then a restart (registry re-read from disk), with and without the engine having saved the inventory -
      never a second item, never a lost one, the journal always finished
  D   START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.3.0 writes the same
      config.properties as 0.2.26 (absent rows = defaults); the fresh default file differs only by the lifelong block; no lifelong folder
      is made at start
  AA  THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/harvest2/harness (0.3.3; deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.3.5"
OLD_VERSION = "0.2.26"
V31 = "0.3.1"          # 0.3.2: the C32 compare base
V32 = "0.3.2"          # 0.3.3: the C33 compare base (C32 = 0.3.1 jar -> 0.3.2 jar)
V33 = "0.3.3"          # 0.3.4: the C34 compare base
V34 = "0.3.4"          # 0.3.5: the C35 compare base (C34 = 0.3.3 jar -> 0.3.4 jar)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "gear5")))
J31 = os.path.abspath(arg("--j31", os.path.join(HERE, "SkyyGear-%s.jar" % V31)))                    # read only (C32)
J32 = os.path.abspath(arg("--j32", os.path.join(HERE, "SkyyGear-%s.jar" % V32)))                    # read only (C32 + C33)
J33 = os.path.abspath(arg("--j33", os.path.join(HERE, "SkyyGear-%s.jar" % V33)))                    # read only (C33 + C34)
J34 = os.path.abspath(arg("--j34", os.path.join(HERE, "SkyyGear-%s.jar" % V34)))                    # read only (C34 + C35)
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
J24 = os.path.abspath(arg("--j24", os.path.join(HERE, "SkyyGear-0.2.24.jar")))                   # read only (X)
CO_SRC = os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.11.jar")                      # read only - copied
FI_SRC = os.path.join(ROOT, "SkyyFishing", "SkyyFishing-0.1.5.jar")                                # 0.3.5: read only - copied (the rods = the pole)
AR_SRC = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.23.jar")                                # read only - copied (R)
MT_SRC = os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")                                        # read only - copied (R)
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
LIVE_PLAYERS = os.path.join(B.USERDATA, "Saves", "HUD mod", "universe", "players")
CO_JAR = os.path.join(SCRATCH, "packs", "SkyyCollections-0.2.11.jar")
FI_JAR = os.path.join(SCRATCH, "packs", "SkyyFishing-0.1.5.jar")          # 0.3.5
PLAYERS = os.path.join(SCRATCH, "players")
PKG = "com.skyy.gear."
NEW_CLASSES = {"GearLL", "GearLife", "LifePage", "PickaxeCmd", "HatchetCmd", "HoeCmd", "SickleCmd", "ToolPtsCmd", "LifelongCmd",
               "GearLLDropSys", "GearLLFn", "GearTrackTask",          # 0.3.2: + GearTrackTask
               "GearArmLv", "GearSigil", "GearTill", "GearTillSys",          # 0.3.4
               "GearRb", "PoleCmd"}          # 0.3.5

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
FAKE_PKG = H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
_H222 = os.path.join(HERE, "test_skyygear_0.2.22.py")
_t2 = open(_H222, encoding="utf-8").read()
_c2 = _t2.index("# ====================================================================================================== F+: this round's stand-ins")
_e2 = _t2.index("# ====================================================================================================== T + R + U + N + P")
H22 = {"__name__": "skyygear_h222", "__builtins__": __builtins__, "H": H, "FAKE_PKG": FAKE_PKG, "PKG": PKG, "JAR": JAR, "B": B, "os": os}
exec(compile(_t2[_c2:_e2], _H222 + " (stand-ins)", "exec"), H22)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    sig_ = sorted(n for n in added if "Sigil" in n)
    check(len(sig_) == 15 and sorted(added) == sig_ and all(n.startswith(("Server/Item/Items/SkyyGear/Skyy_Sigil_", "Common/Icons/ItemsGenerated/Skyy_Sigil_",
          "Common/Items/SkyyGear/Sigil/Sigil_")) for n in sig_) and changed == ["Server/Languages/en-US/server.lang", "manifest.json"]
          and [l_ for l_ in eb["Server/Languages/en-US/server.lang"].split(b"\n") if l_ not in ea["Server/Languages/en-US/server.lang"].split(b"\n")] == [l_ for l_ in eb["Server/Languages/en-US/server.lang"].split(b"\n") if b"Skyy_Sigil_" in l_]
          and len([l_ for l_ in eb["Server/Languages/en-US/server.lang"].split(b"\n") if b"Skyy_Sigil_" in l_]) == 10
          and all(l_ in eb["Server/Languages/en-US/server.lang"].split(b"\n") for l_ in ea["Server/Languages/en-US/server.lang"].split(b"\n")),
          "S (0.3.4): + the 15 Sigil files (5 items, 5 approved icons, 5 tinted textures); server.lang only GAINS their lines: %s" % sig_[:3])
    for n_ in sig_:
        if n_.endswith(".png") and "Icons" in n_:
            check(eb[n_] == open(os.path.join(ROOT, "research", "cloud", "icons-1013", "icons", os.path.basename(n_)), "rb").read(), "S (0.3.4): %s = the approved art byte for byte" % n_)
    check(not (set(ea) - set(eb)) and ('"%s"' % VERSION).encode() in eb["manifest.json"]
          and b"Crude counts as Copper; one tier up takes 2.5x the hits, two up 10x, three up is refused" in eb["manifest.json"]
          and b"LIFELONG TOOLS: one pickaxe, hatchet, hoe and sickle per player for life" in eb["manifest.json"]
          and b"Tools (your lifelong pickaxe, hatchet, hoe and sickle" in eb["manifest.json"],
          "S: 0.2.26 -> 0.3.4: no file removed; the manifest carries the version + the lifelong words: + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: classes added = exactly the 0.3.0 set; none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    names = set(zn.namelist())
    check(not [n for n in names if "Skyy_Ench" in n or "inkblindcat" in n.lower() or n.endswith(".ui") or n.startswith("Server/Item/Items/Tool") or n.startswith("Common/Items/Runes")],
          "S: no Enchanted item / pack mod / vanilla tool file is shipped or overridden (runtime ids only), no .ui file")


# ====================================================================================================== F: stand-ins
def run_mkfake5(out_dir):
    H22["run_mkfake2"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    PMc = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
    pm = cp.makeClass(FAKE_PKG + ".FakePM")
    pm.setSuperclass(cp.get(PMc))
    pm.addField(CtField.make("public static java.lang.Object last;", pm))
    pm.addField(CtField.make("public static int opens;", pm))
    pm.addConstructor(CtNewConstructor.make("public FakePM() { super(); }", pm))
    pm.addMethod(CtNewMethod.make("public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, "
                                  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { last = p; opens = opens + 1; }", pm))
    pm.writeFile(out_dir)
    fp = cp.makeClass(FAKE_PKG + ".FakeLifePage")
    fp.setSuperclass(cp.get(PKG + "LifePage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeLifePage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    for pk_ in ("bazaar", "merchants", "auctions"):          # 0.3.4: market callers in the other mods' packages (GearSigil.marketWhy reads the stack)
        mc_ = cp.makeClass("com.skyy.%s.SkyyG34Caller" % pk_)
        mc_.addMethod(CtNewMethod.make("public static String ask(String id) { return com.skyy.gear.GearWall.why(id, (org.bson.BsonDocument) null); }", mc_))
        mc_.writeFile(out_dir)
    print("F+. FakePM, FakeLifePage, the 0.3.4 market callers written")


# ====================================================================================================== L + M: one booted engine
def run_life(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JFloat, JDouble, JImplements, JOverride, JObject, JArray, JString, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR, FI_JAR], verify=True, big=True)          # 0.3.5: + SkyyFishing 0.1.5 (Marlow's pole, end to end)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "E: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    AZP = game_assets()          # fix round: the CACHED Assets.zip (tools/serverjar.py) - B.SERVER_JAR is a cached copy since 2026-10-13
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
        AZJ = {}
        for n in az_.namelist():
            if n.startswith("Server/Item/Items/") and n.endswith(".json"):
                try:
                    AZJ[os.path.basename(n)[:-5]] = json.loads(az_.read(n).decode("utf-8-sig"))
                except Exception:
                    pass
    tl_ = HAL()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)

    def gen_recipes(items):
        lst = HAL()
        for it in items:
            if it is not None and it.hasRecipesToGenerate():
                it.collectRecipesToGenerate(lst)
        if lst.size() > 0:
            CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
        return int(lst.size())
    n_rc = gen_recipes(list(ITEM.getAssetMap().getAssetMap().values()))
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")

    def addpack(jar, name):
        fs_ = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(jar), JClass("java.util.HashMap")())
        with zipfile.ZipFile(jar) as z_:
            for nm in z_.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    CAR.addCommonAsset(name, FCA(fs_.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(z_.read(nm)).hexdigest(), None))
        return E["loadpack"](jar, name, False)
    cfail, _crec = addpack(CO_JAR, "Skyy:SkyyCollections")
    ffail, _frec = addpack(FI_JAR, "Skyy:SkyyFishing")          # 0.3.5: SkyyFishing's rods = the lifelong pole
    ENCH = ["Skyy_Ench_%s" % k for k in ("Iron", "Thorium", "Cobalt", "Adamantite", "Maple", "Gumboab", "Redwood", "Sallow", "Carrot", "Cauliflower")]
    K.check(all(ITEM.getAssetMap().getAsset(i) is not None for i in ENCH),
            "E: SkyyCollections 0.2.11 (scratch copy) loaded as its own pack: every Enchanted item the tier-up costs name is real (failed stores %s)" % cfail)
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Data, Roll, Forge, Stamp, Lvl, Defs, Log, View, Ui, Tool, LL, Life, Gate, Merge, Wall, Smith = (
        P("GearCfg"), P("Gear"), P("GearUp"), P("GearData"), P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"), P("GearDefs"),
        P("GearLog"), P("GearView"), P("GearUi"), P("GearTool"), P("GearLL"), P("GearLife"), P("GearGate"), P("GearMerge"), P("GearWall"),
        P("GearSmith"))
    Props = JClass("java.util.Properties")
    SR = JClass("java.io.StringReader")
    FRESH = str(Cfg.defaultsText())
    Paths = JClass("java.nio.file.Paths")
    HOME = os.path.join(SCRATCH, "gearhome")
    os.makedirs(HOME, exist_ok=True)
    Cfg.DIR = Paths.get(HOME)
    GLF = os.path.join(SCRATCH, "gear.log")
    Log.FILE = Paths.get(GLF)

    def apply(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()

    def logs():
        Log.flush()
        out_ = []
        if os.path.isfile(GLF):
            with open(GLF, encoding="utf-8") as f_:
                out_ = [l_ for l_ in f_.read().split("\n") if l_.strip()]
            os.remove(GLF)
        return out_ + [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    logs()

    # ============================================================================ L1: the rows
    LLKEYS = ["part.lifelong=true", "lifelong.noCraft=true", "lifelong.noDrop=true", "lifelong.reclaimSec=600", "lifelong.reclaimTier=false", "lifelong.repickDays=7",
              "lifelong.perkSpeed=2", "lifelong.perkFortune=1", "lifelong.perkWisdom=1", "lifelong.resetCoins=5000", "gate.on=true",
              "gate.nextFactor=0.4", "gate.twoUpFactor=0.1", "gate.crudeFactor=0.1", "gate.bareHands=true"]
    K.check(all(("\n" + k + "\n") in FRESH for k in LLKEYS) and "lifelong.ladders=Tool_Pickaxe_Crude>Tool_Pickaxe_Copper(Ingredient_Bar_Copper*25)" in FRESH
            and bool(Cfg.LL_ON) and bool(Cfg.GATE_ON) and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and int(Cfg.LL_RECLAIM) == 600 and not bool(Cfg.LL_RTIER)
            and abs(float(Cfg.GATE_NEXT0) - 0.1) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12,
            "L1 (0.3.1): the fresh config: the 16 lifelong rows at their defaults (gate.nextFactor 0.4 + gate.twoUpFactor 0.1 = Skyy's x2.5 / X10, "
            "gate.crudeFactor kept as an unused legacy row, ladders start with 25 Copper Ingots = G1, lifelong.reclaimTier OFF = fix round 2)")
    LAD = str(Cfg.LL_LADDERS)
    K.check(Up.checkLadders("lifelong.ladders", LAD) is None and "Skyy_Ench_Iron*1" in LAD and "Tool_Hatchet_Iron(Skyy_Ench_Maple*1)" in LAD
            and "Tool_Hoe_Thorium(Skyy_Ench_Cauliflower*1)" in LAD and "Tool_Sickle_Iron(Skyy_Ench_Carrot*1)" in LAD and "Mithril" not in LAD,
            "L1: lifelong.ladders passes GearUp.checkLadders with the real items (Enchanted Iron / Maple / Cauliflower / Carrot), no Mithril step yet")
    CRows, CFn = JClass(PKG + "CfgRows"), JClass(PKG + "CfgFn")
    dang = [k for k in ("part.lifelong", "lifelong.noCraft", "lifelong.ladders", "gate.on", "gate.nextFactor", "gate.bareHands", "lifelong.reclaimTier", "gate.crudeFactor", "gate.twoUpFactor")
            if not bool(CRows.flag(int(CRows.index(k)), "danger"))]
    K.check(not dang and int(CRows.index("lifelong.noDrop")) >= 0 and not bool(CRows.flag(int(CRows.index("lifelong.noDrop")), "danger")),
            "L1: the economy rows are danger rows (Server Setup asks first), noDrop is not: %s" % dang)
    K.check(str(LL.ladders()).startswith(str(Cfg.UP_LADDERS) + ",Tool_Pickaxe_Crude>") and str(LL.ladders()).endswith("," + str(Cfg.GARM_LADDERS)) and Up.next("Tool_Pickaxe_Crude") == "Tool_Pickaxe_Copper"
            and Up.next("Weapon_Wand_SoulOrb") is not None and Up.next("Tool_Shovel_Crude") is None,
            "L1: the Anvil ladders = upgrade.ladders + lifelong.ladders (Soul Cages still there, shovels have none)")
    apply(part__lifelong="false")
    K.check(str(LL.ladders()) == str(Cfg.UP_LADDERS) + "," + str(Cfg.GARM_LADDERS) and Up.next("Tool_Pickaxe_Crude") is None,
            "L1 (0.3.4): part.lifelong off = upgrade.ladders + garmor.ladders (no tool ladders)")
    apply()

    # ---- bridge stand-ins: skills, profile keys, busy, coins, Requip
    br = Gear.bridge()
    Integer, Long_, Bool_ = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    UUID = JClass("java.util.UUID")
    U1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    SK = {}
    PKEY = {str(U1): "p1", str(U2): "p2"}

    @JImplements("java.util.function.Function")
    class SkillFn(object):
        @JOverride
        def apply(self, o):
            v = SK.get((str(o[0]), str(o[1])))
            return None if v is None else JObject(JInt(v), Integer)

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, o):
            return JString(PKEY.get(str(o), str(o)))
    COINS = [10 ** 7]

    @JImplements("java.util.function.Function")
    class CoinGet(object):
        @JOverride
        def apply(self, o):
            return JObject(JLong(COINS[0]), Long_)

    @JImplements("java.util.function.Function")
    class CoinTake(object):
        @JOverride
        def apply(self, o):
            n_ = int(o[1])
            if n_ > COINS[0]:
                return JObject(False, Bool_)
            COINS[0] -= n_
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class CoinAdd(object):
        @JOverride
        def apply(self, o):
            COINS[0] += int(o[1])
            return JObject(JLong(COINS[0]), Long_)
    RQ = {}

    @JImplements("java.util.function.Function")
    class RqList(object):
        @JOverride
        def apply(self, o):
            rows = RQ.get(str(o[1]), [])
            arr = JArray(JObject)(len(rows))
            for i_, r_ in enumerate(rows):
                arr[i_] = JArray(JObject)([JString(r_[0]), JString(r_[1]), r_[2]])
            return arr
    br.put("skill:fn:level", SkillFn())
    br.put("profile:fn:key", KeyFn())
    br.put("coins:fn:get", CoinGet())
    br.put("coins:fn:take", CoinTake())
    br.put("coins:fn:add", CoinAdd())
    br.put("wardrobe:fn:list", RqList())

    def skills(u=U1, **kv):
        for k_, v_ in kv.items():
            SK[(str(u), k_)] = v_
        Gate.forget(u)
        Tool.LAST.clear()

    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    MF = JClass(FAKE_PKG + ".MergeFail")

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def doc(s_):
        return None if s_ is None or s_.isEmpty() else Data.gearDoc(s_.getMetadata())

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_
    SECS = {"hotbar": 9, "storage": 36, "backpack": 9, "armor": 4, "utility": 4, "tools": 4}
    KINDS = (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool"))

    def mkinv(fail=()):
        inv_ = INV()
        cs_ = dict((k_, MF(JShort(n_)) if k_ in fail else SIC(JShort(n_))) for k_, n_ in SECS.items())
        for f_, kind in KINDS:
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_

    def allstacks(cs_):
        out_ = []
        for k_ in ("hotbar", "armor", "tools", "utility", "storage", "backpack"):          # GearStamp.SCAN order
            c_ = cs_[k_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty():
                    out_.append((k_, i_, s_))
        return out_

    def lls(cs_, pk=None):
        """every lifelong stack: (section, slot, kind, uid, owner, rp, stack)"""
        out_ = []
        for k_, i_, s_ in allstacks(cs_):
            d_ = doc(s_)
            if d_ is not None and bool(LL.isLL(d_)) and (pk is None or str(LL.owner(d_)) == pk):
                out_.append((k_, i_, int(LL.kOf(s_.getItemId())), str(LL.uid(d_)), str(LL.owner(d_)), bool(LL.isRp(d_)), s_))
        return out_

    def ids(cs_):
        out_ = {}
        for k_, i_, s_ in allstacks(cs_):
            out_[str(s_.getItemId())] = out_.get(str(s_.getItemId()), 0) + int(s_.getQuantity())
        return out_

    # ---- a player world (FakeStore with Player + PlayerRef + the InventoryComponents), a FakeChunk on it
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    FPR = JClass(FAKE_PKG + ".FakePR")
    FCh = JClass(FAKE_PKG + ".FakeChunk")
    FS = JClass(FAKE_PKG + ".FakeStore")
    FPM = JClass(FAKE_PKG + ".FakePM")
    FU = JClass(FAKE_PKG + ".FakeUtil")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.core.modules.block.BlockModule", "com.hypixel.hytale.server.core.universe.Universe"):
        FU.single(cn)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    IHM = JClass("java.util.IdentityHashMap")
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()

    def mkpr(u, name):
        pr_ = us.allocateInstance(FPR.class_)
        jf(PR, "uuid").set(pr_, u)
        jf(PR, "username").set(pr_, name)
        return pr_
    PR1, PR2 = mkpr(U1, "Tester"), mkpr(U2, "Other")

    def said(pr_):
        s_ = pr_.said
        return [] if s_ is None else [str(x) for x in s_]

    def world(inv_, cs_, pr_):
        pl = us.allocateInstance(PLA.class_)
        jf(PLA, "inventory").set(pl, inv_)
        if pm_field is not None:
            pm_field.set(pl, us.allocateInstance(FPM.class_))
        ref = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(ref, JInt(7))
        st = us.allocateInstance(FS.class_)
        st.comps = JClass("java.util.HashMap")()
        pm = IHM()
        pm.put(PLA.getComponentType(), pl)
        pm.put(PR.getComponentType(), pr_)
        for f_, kind in KINDS:
            try:
                pm.put(JClass(ICOMP + kind).getComponentType(), INV.class_.getDeclaredField(f_) and jf(INV, f_).get(inv_))
            except Exception as e_:
                K.notes.append("world: no component type for %s (%s)" % (kind, str(e_)[:80]))
        st.comps.put(ref, pm)
        jf(REFc, "store").set(ref, st)
        ch = us.allocateInstance(FCh.class_)
        ch.comps = IHM()
        ch.comps.put(PR.getComponentType(), pr_)
        ch.ref = ref
        return ref, st, ch, pl

    def reset_reg():
        """a server restart: the registry cache goes, the files stay"""
        LL.REG.clear()
        LL.LAST.clear()
        LL.BADAT.clear()
        LL.FAILAT.clear()

    def wipe_home():
        LL.REG.clear()
        LL.LAST.clear()
        LL.BADAT.clear()
        LL.FAILAT.clear()
        shutil.rmtree(os.path.join(HOME, "lifelong"), ignore_errors=True)

    def regfile(pk):
        f_ = os.path.join(HOME, "lifelong", pk + ".properties")
        out_ = {}
        if os.path.isfile(f_):
            for l_ in open(f_, encoding="utf-8").read().split("\n"):
                if l_ and not l_.startswith("#") and "=" in l_:
                    a_, b_ = l_.split("=", 1)
                    out_[a_] = b_
        return out_

    # ============================================================================ L2: kinds, tiers, the level rule
    fams = {"Tool_Pickaxe_": 0, "Tool_Hatchet_": 1, "Tool_Hoe_": 2, "Tool_Sickle_": 3}
    tools = sorted(i for i in AZJ if i.startswith(tuple(fams)) and not i.startswith("Tool_Hatchet_Pickaxe_"))
    TIERW = {"Crude": 0, "Wood": 0, "Copper": 1, "Scrap": 1, "Bronze": 2, "Iron": 2, "Steel": 2, "Thorium": 3, "Cobalt": 4, "Adamantite": 5,
             "Mithril": 6, "Onyxium": 7}
    bad2 = [(i, int(LL.kOf(i)), int(LL.tier(i))) for i in tools
            if int(LL.kOf(i)) != [v for p, v in fams.items() if i.startswith(p)][0] or int(LL.tier(i)) != [TIERW[w] for w in i.split("_")[2:] if w in TIERW][0]]
    K.check(len(tools) >= 20 and not bad2 and all(int(LL.kOf(i)) == -1 for i in ("Tool_Shovel_Iron", "Tool_Hammer_Iron", "Weapon_Axe_Iron", "Skyy_Tool_X")),
            "L2: every vanilla pickaxe / hatchet / hoe / sickle has its kind + tier; shovels, hammers, weapon axes are no lifelong kind (bad %s)" % bad2[:3])
    caps = dict((i, int(Lvl.band(i)[1])) for i in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium"))
    skills(Mining=30, Foraging=4, Farming=0)
    lv = [int(LL.levelFor(U1, i)) for i in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium", "Tool_Hatchet_Iron", "Tool_Hoe_Copper")]
    K.check(lv == [min(30, caps["Tool_Pickaxe_Crude"]), min(30, caps["Tool_Pickaxe_Iron"]), min(30, caps["Tool_Pickaxe_Thorium"]), 4, 1],
            "L2: the level rule = min(skill, the tier's band top), at least 1: Mining 30 -> Crude %d / Iron %d / Thorium %d, Foraging 4 -> 4, Farming 0 -> 1 (caps %s): %s"
            % (lv[0], lv[1], lv[2], caps, lv))
    br.remove("skill:fn:level")
    Gate.forget(U1)
    K.check(int(LL.levelFor(U1, "Tool_Pickaxe_Iron")) == -1 and int(LL.earned(U1, JInt(0))) == 0, "L2: no SkyySkills = -1 (the document's level stays), no points")
    br.put("skill:fn:level", SkillFn())
    skills(Mining=30)
    K.check(int(LL.earned(U1, JInt(0))) == 29 and int(LL.earned(U1, JInt(1))) == 3, "L2: 1 point per skill level (Mining 30 = 29 points, Foraging 4 = 3)")

    # ============================================================================ L3: the gate matrix + the REAL hit system
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    bids = [str(k) for k in bmap.keySet()]
    seen_cat = {1: set(), 3: set(), 4: set()}
    for b in bids:
        c_, m_ = [int(x) for x in LL.catOf(b)]
        if m_ >= 1:
            seen_cat[c_].add(b)
    ow = [str(x) for x in LL.ORE_W]
    wn = [str(x) for x in LL.WOOD_W]
    cw = [str(x) for x in LL.CROP_W]
    miss = [w for w in ow if not [b for b in seen_cat[1] if b.lstrip("*").startswith("Ore_" + w)]] + \
           [w for w in wn if not [b for b in seen_cat[3] if b.lstrip("*").startswith("Wood_" + w + "_")]] + \
           [w for w in cw if not [b for b in seen_cat[4] if b.lstrip("*").startswith("Plant_Crop_" + w + "_")]]
    K.check(set(miss) <= {"Onyxium"} and len(seen_cat[1]) >= 9 and len(seen_cat[3]) >= 20 and len(seen_cat[4]) >= 10,
            "L3: every tier-table word matches real BlockTypes in the store (%d ore, %d log, %d crop blocks gated; no block yet: %s - Onyxium is Zone 5)"
            % (len(seen_cat[1]), len(seen_cat[3]), len(seen_cat[4]), miss))
    ungated = [list(LL.catOf(x)) for x in ("Rock_Stone", "Soil_Dirt", "Wood_Oak_Planks", "Ore_Prisma", "Plant_Crop_Berry_Block")]
    K.check(all(u_[1] < 1 for u_ in ungated) and list(LL.catOf("*Ore_Iron_Stone")) == [1, 2] and list(LL.catOf("Wood_Fig_Blue_Trunk")) == [3, 5],
            "L3: stone / dirt / planks / an unlisted ore / berries never gated; a state id (*Ore_Iron_Stone) = Iron M2; Wood_Fig_Blue_Trunk = M5: %s" % ungated)
    FAMMAX = [int(x) for x in LL.FAMMAX]

    def py_decide(f, t, c, m):
        if c == 0 or m < 1:
            return -1
        fits = (c == 1 and f in (1, 6)) or (c == 3 and f in (3, 6)) or (c == 4 and f in (4, 5))
        if not fits:
            if c == 4:          # 0.3.5 (Skyy "Hands count as Crude"): no hoe / sickle = a Crude hoe on crops
                d4 = min(m, FAMMAX[4]) - 1
                return 0 if d4 <= 0 else (1 if d4 <= 1 else 2)
            return 2
        me = min(m, FAMMAX[f])
        d = me - max(t, 1)          # 0.3.1: Crude / Wood count as tier 1
        return 0 if d <= 0 else (1 if d <= (1 if c == 4 else 2) else 2)          # 0.3.3: crops refuse at two up; ore / logs at three
    badm, nm = [], 0
    for iid in tools + ["Tool_Shovel_Iron", "Weapon_Sword_Iron", "Weapon_Axe_Iron", None]:
        f = 0 if iid is None else int(Data.toolFam(iid))
        t = TIERW.get(([w for w in (iid or "").split("_")[2:] if w in TIERW] + ["Crude"])[0], 0)
        s_ = None if iid is None else stack(iid)
        for c in (1, 3, 4):
            for m in range(0, 8):
                got = int(LL.decideC(s_, JInt(c), JInt(m))[0])
                want = py_decide(f, t, c, m)
                nm += 1
                if got != want:
                    badm.append((iid, c, m, got, want))
    K.check(not badm and nm > 500, "L3: THE GATE MATRIX: %d cases (every pickaxe / hatchet / hoe / sickle tier, a shovel, a sword, a weapon axe, bare hands x ore / "
            "log / crop x M0-M7) = the 0.3.3 rule (Crude = tier 1; own tier normal, +1 / +2 slow, +3 refused - crops +2 refused, no fitting tool on ore / logs refused, "
            "0.3.5: crops by hand / any non-farming item = a Crude hoe, a family's top tier caps the ask): bad %s" % (nm, badm[:4]))
    K.check(int(LL.decideC(stack("Tool_Hoe_Thorium"), JInt(4), JInt(7))[0]) == 0 and int(LL.decideC(stack("Tool_Sickle_Iron"), JInt(4), JInt(4))[0]) == 0
            and int(LL.decideC(stack("Tool_Hoe_Iron"), JInt(4), JInt(7))[0]) == 1 and int(LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))[0]) == 2
            and int(LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))[5]) == 2
            and int(LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(1))[0]) == 0,
            "L3 (0.3.1): the top vanilla hoe (Thorium) / sickle (Iron) works at full speed on every crop above it (a Potato, a Pumpkin); an Iron hoe on a "
            "Potato = one up; a Crude hoe on a Tomato = two up (0.3.3: REFUSED again - 0.3.1 / 0.3.2 let it break slowly); a Crude pickaxe on Copper ore = NORMAL")
    apply(gate__bareHands="false")
    K.check(int(LL.decideC(None, JInt(3), JInt(1))[0]) == -1 and int(LL.decideC(stack("Tool_Shovel_Iron"), JInt(1), JInt(4))[0]) == -1,
            "L3: gate.bareHands off: no tool / the wrong tool is not gated")
    apply(gate__on="false")
    K.check(int(LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(7))[0]) == -1, "L3: gate.on off: nothing is gated")
    apply()
    # the REAL GearToolHitSys.handle on REAL DamageBlockEvents
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    ctor = [c for c in DBE.class_.getConstructors() if len(c.getParameterTypes()) == 5][0]
    pts = [str(p.getName()) for p in ctor.getParameterTypes()]
    JFl = JClass("java.lang.Float")

    def ev(s_, b_, d):
        args, nf = [], 0
        for p in pts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(b_)
            elif p == "float":
                args.append(JFl.valueOf(JFloat(1.0 if nf == 0 else d)))
                nf += 1
            else:
                args.append(JClass(p)(JInt(0), JInt(64), JInt(0)))
        return ctor.newInstance(JArray(JObject)(args))
    Hit = JClass(PKG + "GearToolHitSys")
    hs = Hit()
    invH, csH = mkinv()
    refH, stH, chH, plH = world(invH, csH, PR1)
    BL = dict((n, bmap.get(n)) for n in ("Ore_Iron_Stone", "Ore_Copper_Stone", "Ore_Thorium_Sandstone", "Wood_Oak_Trunk", "Wood_Maple_Trunk", "Rock_Stone"))
    K.check(all(v is not None for v in BL.values()), "L3: the real BlockTypes are in the store: %s" % [k for k, v in BL.items() if v is None])
    skills(Mining=10, Foraging=10)

    def hit(s_, bn, d=0.3):
        Tool.LAST.clear()
        e_ = ev(s_, BL[bn], d)
        d0 = float(e_.getDamage())
        hs.handle(JInt(0), chH, stH, None, e_)
        return bool(e_.isCancelled()), float(e_.getDamage()), d0
    n0 = [int(x) for x in LL.N]
    ref_on = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Iron_Stone"], JFloat(0.3)))
    r_norm = hit(stack("Tool_Pickaxe_Iron"), "Ore_Iron_Stone")
    Tool.LAST.clear()
    ref_slow = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    r_slow = hit(stack("Tool_Pickaxe_Iron"), "Ore_Thorium_Sandstone")
    r_ref = hit(stack("Tool_Pickaxe_Copper"), "Ore_Thorium_Sandstone")
    r_bare = hit(None, "Wood_Oak_Trunk")
    r_sword = hit(stack("Weapon_Sword_Iron"), "Ore_Copper_Stone")
    r_stone = hit(None, "Rock_Stone")
    r_crude_log = hit(stack("Tool_Hatchet_Crude"), "Wood_Oak_Trunk")
    r_crude_maple = hit(stack("Tool_Hatchet_Crude"), "Wood_Maple_Trunk")
    n1 = [int(x) for x in LL.N]
    Tool.LAST.clear()
    ref_cu_th = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Copper"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    Tool.LAST.clear()
    ref_cr_oak = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Oak_Trunk"], JFloat(0.3)))
    Tool.LAST.clear()
    ref_cr_map = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Maple_Trunk"], JFloat(0.3)))
    K.check(not r_norm[0] and abs(r_norm[1] - ref_on) < 1e-6 and not r_slow[0] and abs(r_slow[1] - float(JFloat(ref_slow * 0.4))) < 1e-6
            and not r_ref[0] and abs(r_ref[1] - float(JFloat(ref_cu_th * 0.1))) < 1e-6
            and r_bare[0] and r_sword[0] and not r_stone[0] and abs(r_stone[1] - r_stone[2]) < 1e-9
            and not r_crude_log[0] and abs(r_crude_log[1] - ref_cr_oak) < 1e-6
            and not r_crude_maple[0] and abs(r_crude_maple[1] - float(JFloat(ref_cr_map * 0.4))) < 1e-6,
            "L3 (0.3.1): THE REAL HIT SYSTEM: Iron pickaxe on iron ore = its own power (%.4f); on thorium (one up) = that x0.4 (%.5f); a Copper pickaxe on "
            "thorium (two up) = x0.1, no longer cancelled; bare hands on a log and a sword on copper ore = cancelled; bare hands on stone = vanilla; Crude "
            "hatchet on Oak = NORMAL (Crude = T1), on Maple = x0.4 (was refused): %s" % (r_norm[1], r_slow[1], [r_norm, r_slow, r_ref, r_bare, r_sword, r_stone, r_crude_log, r_crude_maple]))
    K.check(n1[0] - n0[0] >= 2 and n1[1] - n0[1] >= 3 and n1[2] - n0[2] >= 2, "L3 (0.3.1): the counters: refused %d (bare %d), slowed %d" % (n1[0] - n0[0], n1[2] - n0[2], n1[1] - n0[1]))
    e_c = ev(stack("Tool_Pickaxe_Copper"), BL["Ore_Thorium_Sandstone"], 0.3)
    e_c.setCancelled(True)
    hs.handle(JInt(0), chH, stH, None, e_c)
    K.check(bool(e_c.isCancelled()) and abs(float(e_c.getDamage()) - 0.3) < 1e-6, "L3: an event another mod cancelled (SkyyIslands) is left alone")

    # ============================================================================ L4: only.farming (no Fortune one tier up)
    o0, o1, o3 = str(LL.onlyFor(JInt(4), JInt(0), "")), str(LL.onlyFor(JInt(4), JInt(1), "")), str(LL.onlyFor(JInt(4), JInt(3), ""))
    o5 = str(LL.onlyFor(JInt(5), JInt(2), ""))
    free_ = str(LL.CROP_FREE)
    K.check(o0 == o1 and o1.split(",")[:2] == ["Wheat", "Lettuce"] and "Carrot" not in o1 and "Berry" in o1 and free_ in o1
            and all(w in o3 for w in ("Wheat", "Carrot", "Cauliflower", "Pumpkin", "Tomato", "Cotton", "Potato"))
            and "Pumpkin" in o5 and "Potato" in o5 and str(LL.onlyFor(JInt(1), JInt(0), "Rock_,Rubble_,Ore_")) == "Rock_,Rubble_,Ore_",
            "L4 (0.3.1): a Crude hoe's Fortune counts like a Copper hoe's (Crude = T1: Wheat + Lettuce + the free crops; was the free crops only); a "
            "Thorium hoe (the top vanilla hoe) on every crop; an Iron sickle too (sickles end at Iron); pickaxes keep their "
            "0.2.12 filter: %s | %s" % (o0[:60], o1[:60]))
    skills(Farming=20)
    Tool.LAST.clear()
    Tool.held(U1, Data.put(stack("Tool_Hoe_Crude"), Roll.newDoc("Tool_Hoe_Crude", JInt(0), True, "craft", JInt(5)), None))
    g_ = br.get("skill:bonus:" + str(U1))
    gsrc = None if g_ is None else g_.get("gear")
    K.check(gsrc is not None and str(gsrc.get("only.farming")) == o0, "L4: Tool.held posts only.farming = that list for a Crude hoe: %s" % (None if gsrc is None else str(gsrc)[:160]))
    ft = [int(LL.farmTier("Plant_Crop_Wheat_Block", "Tool_Hoe_Crude")), int(LL.farmTier("Plant_Crop_Carrot_Block", "Tool_Hoe_Crude")),
          int(LL.farmTier("Plant_Crop_Wheat_Block", "Tool_Hoe_Copper")), int(LL.farmTier("Plant_Crop_Wheat_Block", None)),
          int(LL.farmTier("Rock_Stone", "Tool_Hoe_Crude"))]
    K.check("Plant_Cactus" in o0.split(",") and "Plant_Cactus" in o1.split(",") and "Plant_Cactus" in o5.split(",")
            and any(str(b).startswith("Plant_Cactus") for b in bids),
            "FIX engine-5: a hoe / sickle's only.farming always lists Plant_Cactus (SkyySkills counts cactus as Farming and matches by 'contains' - "
            "Fortune keeps counting on it at every tier; a real Plant_Cactus block is in the store): %s" % o0[-60:])
    K.check(ft == [0, 1, 0, 0, -1], "L4 (0.3.1): gear:fn:farmTier's core: Crude hoe on Wheat = 0 (normal, was 1), on Carrot = 1 (half XP, was 2), "
            "Copper hoe on Wheat = 0, by hand = 0 (0.3.5: hands count as Crude - Wheat is their own tier), a stone = -1: %s" % ft)

    # ============================================================================ M: THE MIGRATION ON THE LIVE PLAYERS' REAL STACKS
    BDc = JClass("org.bson.BsonDocument")
    SECMAP = {"HotbarInventory": "hotbar", "StorageInventory": "storage", "BackpackInventory": "backpack", "ArmorInventory": "armor",
              "UtilityInventory": "utility", "ToolInventory": "tools"}
    LIVE = {}
    for f_ in sorted(glob.glob(os.path.join(PLAYERS, "*.json"))):
        d_ = json.load(open(f_, encoding="utf-8"))
        rows = []
        for ck, sec in SECMAP.items():
            items = ((d_.get("Components") or {}).get(ck) or {}).get("Inventory", {}).get("Items", {}) or {}
            for sl, it in items.items():
                iid = it.get("Id")
                if not iid or ITEM.getAssetMap().getAsset(iid) is None:
                    continue
                md = it.get("Metadata")
                rows.append((sec, int(sl), iid, int(it.get("Quantity", 1)), json.dumps(md) if md else None))
        LIVE[os.path.basename(f_)[:-5]] = rows
    K.notes.append("M: live players (scratch copies): %s" % dict((k, len(v)) for k, v in LIVE.items()))

    def live_inv(rows):
        inv_, cs_ = mkinv()
        for sec, sl, iid, q, md in rows:
            if sl >= int(cs_[sec].getCapacity()):
                continue
            s_ = IS(iid, JInt(q), BDc.parse(md)) if md else IS(iid, JInt(q))
            cs_[sec].setItemStackForSlot(JShort(sl), s_)
        return inv_, cs_

    def snapshot(cs_):
        return [(k_, i_, str(s_.getItemId()), int(s_.getQuantity()), None if s_.getMetadata() is None else str(s_.getMetadata().toJson()))
                for k_, i_, s_ in allstacks(cs_)]

    def restore_inv(cs_, snap):
        for k_ in SECS:
            c_ = cs_[k_]
            for i_ in range(int(c_.getCapacity())):
                c_.removeItemStackFromSlot(JShort(i_))
        for k_, i_, iid, q, md in snap:
            cs_[k_].setItemStackForSlot(JShort(i_), IS(iid, JInt(q), BDc.parse(md)) if md else IS(iid, JInt(q)))

    def keep_fields(d_):
        """the parts of a document the migration must keep: rarity, lines, reforge name, identified"""
        if d_ is None:
            return None
        return (str(Data.str(d_, "r", "normal")), str(View.modSummary(d_)), str(Data.str(d_, "rf", "")), bool(Data.identified(d_)))

    def invariants(tag, cs_, pk, before_ids, gifts):
        L_ = lls(cs_, pk)
        R_ = regfile(pk)
        kinds = sorted(x[2] for x in L_)
        uids_ok = all(R_.get("%s.uid" % str(LL.KIND[x[2]])) == x[3] for x in L_)
        now_ids = ids(cs_)
        want = dict(before_ids)
        for g in gifts:
            want[g] = want.get(g, 0) + 1
        pend = [k for k in R_ if k.endswith(".pend")]
        return kinds == [0, 1, 2, 3] and uids_ok and now_ids == want and not pend and R_.get("migrated") == "1", \
            "%s: kinds %s uids_ok %s pend %s migrated %s counts %s" % (tag, kinds, uids_ok, pend, R_.get("migrated"),
                                                                      dict((k, (now_ids.get(k, 0), want.get(k, 0))) for k in set(now_ids) | set(want) if now_ids.get(k, 0) != want.get(k, 0)))
    best_pick = {}
    for pname, rows in LIVE.items():
        wipe_home()
        logs()
        PKEY[str(U1)] = "live-" + pname[:8]
        pk = PKEY[str(U1)]
        skills(Mining=31, Foraging=15, Farming=8)
        inv_, cs_ = live_inv(rows)
        refL, stL, chL, plL = world(inv_, cs_, PR1)
        before = ids(cs_)
        bdocs = dict(((k_, i_), keep_fields(doc(s_))) for k_, i_, s_ in allstacks(cs_))
        owners_ = sorted(set(str(LL.owner(doc(s_))) for k_, i_, s_ in allstacks(cs_) if doc(s_) is not None and bool(LL.isLL(doc(s_)))))
        if owners_:
            # 0.3.2: this live player file was saved AFTER 0.3.0 went live (2026-10-13 19:54) - the tools are lifelong already (owner = the
            # real profile key). The migration's pick / gift / crash checks need a pre-0.3.0 inventory; here instead: 0.3.2 on the REAL migrated
            # inventory ADOPTS each tool (a lost registry rebuilt from the items), gives nothing, keeps every count + rarity / lines, takes a
            # snapshot of each; a second sweep and a restart change nothing
            PKEY[str(U1)] = owners_[0]
            pk = owners_[0]
            logs()
            Life.sweep0(PR1, inv_, True)
            lgA = logs()
            rA_ = regfile(pk)
            LA = lls(cs_, pk)
            keptA = all(keep_fields(doc(x[6])) == bdocs.get((x[0], x[1])) for x in LA)
            regA = all(rA_.get("%s.uid" % str(LL.KIND[x[2]])) == x[3] and rA_.get("%s.snapU" % str(LL.KIND[x[2]])) == x[3] for x in LA)
            snapA = snapshot(cs_)
            Life.sweep0(PR1, inv_, True)
            reset_reg()
            Life.sweep0(PR1, inv_, True)
            K.check(len(owners_) == 1 and ids(cs_) == before and keptA and regA and rA_.get("migrated") == "1" and len(LA) == len(set(x[2] for x in LA))
                    and not [l for l in lgA if "LL-MARK " in l or "LL-GIVE " in l] and len([l for l in lgA if "LL-ADOPT " in l]) == len(LA)
                    and snapshot(cs_) == snapA and regfile(pk) == rA_,
                    "M (0.3.2): live player %s is ALREADY migrated in game (owner %s, %d lifelong tools): 0.3.2 adopts each one (no mark, no gift), "
                    "every count + rarity / lines kept, registry uid + snapshot per kind; a 2nd sweep + a restart change nothing" % (pname[:8], owners_, len(LA)))
            K.notes.append("M: %s is already migrated in game - the pre-0.3.0 migration checks ran on the other live player(s) only" % pname[:8])
            PKEY[str(U1)] = "p1"
            continue
        # the expected pick: per kind the best (rarity, level, lines), identified, not stacked
        exp = {}
        for k_, i_, s_ in allstacks(cs_):
            kk = int(LL.kOf(s_.getItemId()))
            if kk < 0 or int(s_.getQuantity()) != 1:
                continue
            d_ = Data.effective(s_.getItemId(), s_.getMetadata())
            key = (0 if d_ is None else int(Data.rarity(d_)), int(Lvl.level(s_.getItemId(), d_)), 0 if d_ is None else int(Data.mods(d_).size()))
            if kk not in exp or key > exp[kk][0]:
                exp[kk] = (key, k_, i_, str(s_.getItemId()))
        gifts = [str(LL.KCRUDE[k]) for k in range(4) if k not in exp]
        nw0 = int(LL.N[5])
        Life.sweep0(PR1, inv_, True)
        nw1 = int(LL.N[5])
        K.check(nw1 - nw0 <= 5, "FIX engine-3: %s: the migration wrote the registry %d times (one journal per marked / given kind + ONE save; 0.3.0 "
                "before the fix: up to 10)" % (pname[:8], nw1 - nw0))
        ok, why = invariants("M " + pname[:8], cs_, pk, before, gifts)
        K.check(ok, "M: live player %s: after the migration exactly one lifelong tool per kind, the registry names each uid, migrated=1, no journal "
                "left, every item count unchanged except %s: %s" % (pname[:8], gifts, why))
        L_ = dict((x[2], x) for x in lls(cs_, pk))
        picked = dict((k, (L_[k][0], L_[k][1], str(L_[k][6].getItemId()))) for k in L_)
        exp_pos = dict((k, (v[1], v[2], v[3])) for k, v in exp.items())
        kept = all(keep_fields(doc(L_[k][6])) == bdocs.get((L_[k][0], L_[k][1])) or bdocs.get((L_[k][0], L_[k][1])) is None for k in exp)
        K.check(all(picked[k] == exp_pos[k] for k in exp) and kept, "M: %s: the best tool of each kind was picked where it lay (%s) and kept its rarity / "
                "lines / reforge name; the rest stay plain" % (pname[:8], dict((str(LL.KIND[k]), v[2]) for k, v in exp_pos.items())))
        lvl_ok = all(int(Data.num(doc(L_[k][6]), "lvl", -1)) == int(LL.levelFor(U1, L_[k][6].getItemId())) for k in L_)
        K.check(lvl_ok, "M: %s: each lifelong tool's document level = min(skill, its tier's top): %s" % (
            pname[:8], dict((str(LL.KIND[k]), int(Data.num(doc(L_[k][6]), "lvl", -1))) for k in L_)))
        best_pick[pname] = dict((str(LL.KIND[k]), v[2]) for k, v in exp_pos.items())
        snap1 = snapshot(cs_)
        reg1 = regfile(pk)
        Life.sweep0(PR1, inv_, True)
        reset_reg()
        Life.sweep0(PR1, inv_, True)
        K.check(snapshot(cs_) == snap1 and regfile(pk) == reg1, "M: %s: a second sweep and a restart + sweep change nothing (run once)" % pname[:8])
        lg = logs()
        K.check(all(" undo: " in l for l in lg if "LL-MARK " in l), "FIX A-3: %s: every LL-MARK line carries the stack as it was (undo data): %s"
                % (pname[:8], [l[-80:] for l in lg if "LL-MARK " in l][:1]))
        K.check(len([l for l in lg if "LL-MARK " in l]) == len(exp) and len([l for l in lg if "LL-GIVE " in l]) == len(gifts)
                and len([l for l in lg if "LL-MIGRATED" in l]) == 1, "M: %s: gear.log has one LL-MARK per picked tool, one LL-GIVE per gift, one LL-MIGRATED"
                % pname[:8])
        K.check(any("Lifelong tools: you keep ONE pickaxe" in x for x in said(PR1)), "M: %s: the one-time chat line" % pname[:8])
        PR1.said = None
        # CRASH AT EVERY STEP: 1-3 mark, 4-6 give; then a restart (registry cache dropped) with the inventory as it was at the crash
        # (the engine saved it) AND with the inventory from before the step (the engine did not save it) - the end state is the same rule
        for crash_at in (1, 2, 3, 4, 5, 6):
            for saved in (True, False):
                wipe_home()
                inv2, cs2 = live_inv(rows)
                pre = snapshot(cs2)
                Life.CRASH_AT = crash_at
                crashed = False
                try:
                    Life.sweep0(PR1, inv2, True)
                except Exception as ex_:
                    crashed = "harness: a crash at lifelong step %d" % crash_at in str(ex_)
                Life.CRASH_AT = 0
                if not crashed and ((crash_at <= 3 and not exp) or (crash_at >= 4 and not gifts)):
                    continue
                if not saved:
                    restore_inv(cs2, pre)
                reset_reg()
                Life.sweep0(PR1, inv2, True)
                Life.sweep0(PR1, inv2, True)
                ok2, why2 = invariants("crash %d saved %s" % (crash_at, saved), cs2, pk, before, gifts)
                K.check(crashed and ok2, "M: %s: a CRASH at step %d (inventory %s) then a restart: %s" % (
                    pname[:8], crash_at, "saved" if saved else "not saved", why2))
        logs()
        # a failing registry write: nothing moves, the next sweep finishes
        wipe_home()
        inv3, cs3 = live_inv(rows)
        pre3 = snapshot(cs3)
        LL.FAIL_SAVE = True
        Life.sweep0(PR1, inv3, True)
        LL.FAIL_SAVE = False
        K.check(snapshot(cs3) == pre3 and not lls(cs3), "M: %s: the registry cannot be written -> no item is touched" % pname[:8])
        Life.sweep0(PR1, inv3, True)
        ok3, why3 = invariants("after a failed write", cs3, pk, before, gifts)
        K.check(ok3, "M: %s: ... and the next sweep migrates normally: %s" % (pname[:8], why3))
    K.notes.append("M: picks %s" % best_pick)
    PKEY[str(U1)] = "p1"
    # a NEW profile: an empty inventory gets the four Crude Common tools (no SkyyIslands change needed)
    wipe_home()
    invN, csN = mkinv()
    skills(Mining=1, Foraging=1, Farming=1)
    RQ["items"] = [("e9", "Tool_Pickaxe_Iron", None), ("e8", "Weapon_Sword_Iron", None)]
    PR1.said = None
    nwN = int(LL.N[5])
    Life.sweep0(PR1, invN, True)
    nwN = int(LL.N[5]) - nwN
    RQ.clear()
    K.check(nwN == 5 and regfile("p1").get("migrated") == "1" and not [k for k in regfile("p1") if k.endswith(".pend")],
            "FIX engine-3: a new profile's four gifts = 4 journal writes + 1 save (was 10), migrated=1 + every commit on disk: %d writes" % nwN)
    K.check(any("Your Requip holds a pickaxe that was not checked" in x and "/lifelong" in x for x in said(PR1))
            and not any("holds a pickaxe, " in x for x in said(PR1)),
            "FIX A-3: the migration names a lifelong-kind tool sitting in Requip once (pick it with /lifelong); a sword there is not named: %s" % said(PR1)[-1:])
    LN = lls(csN, "p1")
    K.check(sorted(str(x[6].getItemId()) for x in LN) == sorted(str(x) for x in list(LL.KCRUDE)[:4]) and all(str(Data.str(doc(x[6]), "r", "")) == "normal"
            and int(Data.mods(doc(x[6])).size()) == 0 and int(Data.num(doc(x[6]), "lvl", -1)) == 1 and not x[5] for x in LN)
            and [x[0] for x in LN] == ["storage"] * 4 and len(LL.KCRUDE) == 5,          # 0.3.5: the pole is never given at a first join
            "M: a NEW profile's first join: the four Crude Common tools (Lv 1, no lines) in the storage first: %s" % [(x[0], x[1], str(x[6].getItemId())) for x in LN])
    # no room: the kinds wait, nothing is lost, the line comes once a minute
    wipe_home()
    invF, csF = mkinv()
    for sec in ("storage", "backpack", "hotbar"):
        for i_ in range(int(csF[sec].getCapacity())):
            csF[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone", 10))
    PR1.said = None
    Life.sweep0(PR1, invF, True)
    Life.sweep0(PR1, invF, True)
    K.check(not lls(csF) and regfile("p1").get("migrated") is None and len([x for x in said(PR1) if "is waiting - free one inventory slot" in x]) == 4,
            "M: a full inventory: nothing given, not marked done, one waiting line per kind (not repeated at once)")
    csF["storage"].removeItemStackFromSlot(JShort(0))
    csF["storage"].removeItemStackFromSlot(JShort(1))
    csF["storage"].removeItemStackFromSlot(JShort(2))
    csF["storage"].removeItemStackFromSlot(JShort(3))
    LL.LAST.clear()
    Life.sweep0(PR1, invF, False)
    K.check(len(lls(csF)) == 4 and regfile("p1").get("migrated") == "1", "M: ... room made -> the next sweep gives all four")

    # ============================================================================ L5: perks + points
    wipe_home()
    logs()
    inv5, cs5 = mkinv()
    cs5["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Pickaxe_Copper"), Roll.newDoc("Tool_Pickaxe_Copper", JInt(2), True, "craft", JInt(12)), None))
    skills(Mining=12, Foraging=2, Farming=1)
    Life.sweep0(PR1, inv5, True)
    reg5 = LL.reg("p1")
    pick5 = cs5["hotbar"].getItemStack(JShort(0))
    K.check(bool(LL.isLL(doc(pick5))) and str(Data.str(doc(pick5), "r", "")) == "rare", "L5: the Rare Copper pickaxe became the lifelong one")
    r_hatch = str(Life.buy(U1, JInt(1), JInt(0)))
    r_none = str(Life.buy(U1, JInt(2), JInt(0)))
    r_wis = str(Life.buy(U1, JInt(0), JInt(2)))
    r_vein = str(Life.buy(U1, JInt(0), JInt(3)))
    br.put("gear:perk:readers", "vein, fell")
    r_vein2 = str(Life.buy(U1, JInt(0), JInt(3)))
    br.remove("gear:perk:readers")
    K.check(r_hatch.startswith("+Speed is level 1 now (0 points left)") and r_none.startswith("-Speed is not an upgrade for a hoe")
            and "needs an Iron pickaxe" in r_wis and "next SkyyTrees" in r_vein and "needs an Iron pickaxe" in r_vein2,
            "L5: Speed for the hatchet (Foraging 2 = 1 point); refusals: Speed is not for hoes; Wisdom + Vein Mine need an Iron tool; Vein Mine waits for "
            "SkyyTrees (gear:perk:readers) - then the tier rule: %s | %s | %s | %s | %s" % (r_hatch, r_none, r_wis, r_vein, r_vein2))
    st0 = [float(x) for x in Tool.stats(U1, pick5)]
    got = [str(Life.buy(U1, JInt(0), JInt(0))) for _i in range(11)]
    st1 = [float(x) for x in Tool.stats(U1, pick5)]
    K.check(all(g.startswith("+") for g in got[:10]) and got[10].startswith("-Speed is already at its top level (10)")
            and abs(st1[4] - min(100.0, st0[4] * 1.2)) < 1e-6 and int(LL.perkOf(reg5, JInt(0), JInt(0))) == 10 and regfile("p1").get("pickaxe.up.spd") == "10",
            "L5: 10 Speed levels (1 point each, 11 points free) -> power x1.2 exactly (%.4f -> %.4f), the 11th refused; the registry file says 10" % (st0[4], st1[4]))
    r_more = str(Life.buy(U1, JInt(0), JInt(1)))
    r_poor = str(Life.buy(U1, JInt(0), JInt(1)))
    st2 = [float(x) for x in Tool.stats(U1, pick5)]
    K.check(r_more.startswith("+Fortune is level 1 now (0 points left)") and r_poor.startswith("-Fortune 2 costs 1 point - you have 0 free")
            and abs(st2[5] - min(float(Cfg.TOOL_FCAP), round((st1[5] + 1.0) * 10) / 10.0)) < 1e-6,
            "L5: Fortune 1 = +1 Fortune on the tool (%.1f -> %.1f); out of points refused: %s" % (st1[5], st2[5], r_poor))
    od = doc(pick5).clone()
    for k_ in ("ll", "lu", "lo", "lrp"):
        od.remove(k_)
    other = Data.put(stack("Tool_Pickaxe_Copper"), od, None)
    sto = [float(x) for x in Tool.stats(U1, other)]
    K.check(abs(sto[4] - st0[4]) < 1e-9 and abs(sto[5] - st0[5]) < 1e-9 and sto[4] < st2[4], "L5: the same Rare roll as a PLAIN tool gets none of the perks "
            "(power %.4f / %.4f with Speed 10, Fortune %.1f / %.1f)" % (sto[4], st2[4], sto[5], st2[5]))
    skills(Mining=12)
    K.check(int(LL.free(U1, reg5, JInt(0))) == 0 and int(LL.spent(reg5, JInt(0))) == 11, "L5: spent 11 of 11")
    # the reset: coins first, more each time, refund on a failed write, coins unavailable
    COINS[0] = 10 ** 7
    c1 = int(LL.resetCost(reg5, JInt(0)))
    pre_c = COINS[0]
    r1 = str(Life.reset(U1, "Tester", JInt(0)))
    c2 = int(LL.resetCost(reg5, JInt(0)))
    K.check(c1 == 5000 * 11 and r1.startswith("+All 11 points of your pickaxe are back") and COINS[0] == pre_c - c1 and int(LL.spent(reg5, JInt(0))) == 0
            and regfile("p1").get("pickaxe.resets") == "1" and "pickaxe.up.spd" not in regfile("p1"),
            "L5: reset = 5,000 x 11 spent x 1 = %d coins taken, every point back, resets=1 on disk: %s" % (c1, r1))
    for _i in range(3):
        Life.buy(U1, JInt(0), JInt(0))
    c3 = int(LL.resetCost(reg5, JInt(0)))
    K.check(c2 == 0 and c3 == 5000 * 3 * 2, "L5: the next reset costs more: 3 spent x 2 = %d" % c3)
    pre_c = COINS[0]
    LL.FAIL_SAVE = True
    r_f = str(Life.reset(U1, "Tester", JInt(0)))
    LL.FAIL_SAVE = False
    K.check(r_f.startswith("-The reset could not be saved - nothing changed and your coins were refunded") and COINS[0] == pre_c
            and int(LL.spent(reg5, JInt(0))) == 3 and regfile("p1").get("pickaxe.resets") == "1",
            "L5: a reset whose write fails refunds the coins and changes nothing: %s" % r_f)
    br.remove("coins:fn:take")
    r_nc = str(Life.reset(U1, "Tester", JInt(0)))
    br.put("coins:fn:take", CoinTake())
    COINS[0] = 10
    r_poor2 = str(Life.reset(U1, "Tester", JInt(0)))
    COINS[0] = 10 ** 7
    K.check(r_nc.startswith("-Coins are not available") and r_poor2.startswith("-A reset costs 30,000 coins - you have 10"),
            "L5: no SkyyCoins / too few coins: nothing changes: %s | %s" % (r_nc, r_poor2))
    LL.FAIL_SAVE = True
    r_bf = str(Life.buy(U1, JInt(0), JInt(1)))
    LL.FAIL_SAVE = False
    K.check(r_bf.startswith("-Fortune") or r_bf.startswith("-Your choice could not be saved"), "L5: a perk whose write fails is not kept: %s" % r_bf)
    br.put("profile:busy:" + str(U1), JBoolean(True))
    K.check(str(Life.buy(U1, JInt(0), JInt(0))).startswith("-Your profile is still loading") and str(Life.reset(U1, "T", JInt(0))).startswith("-Your profile is still loading"),
            "L5: profile:busy refuses perks and resets")
    br.remove("profile:busy:" + str(U1))
    lg5 = logs()
    K.check(len([l for l in lg5 if "LL-PERK " in l]) >= 14 and len([l for l in lg5 if "LL-RESET " in l]) == 1 and any("REFUND " in l for l in lg5),
            "L5: gear.log: LL-PERK per level, one LL-RESET, the REFUND line")

    # ============================================================================ L6: the sweep (levels, registry id, restore, remove, demote, foreign)
    wipe_home()
    inv6, cs6 = mkinv()
    skills(Mining=10, Foraging=10, Farming=10)
    Life.sweep0(PR1, inv6, True)
    L6 = dict((x[2], x) for x in lls(cs6, "p1"))
    pk6 = L6[0]
    K.check(int(Data.num(doc(pk6[6]), "lvl", -1)) == min(10, caps["Tool_Pickaxe_Crude"]), "L6: the Crude pickaxe starts at Mining 10 -> Lv %d" % min(10, caps["Tool_Pickaxe_Crude"]))
    skills(Mining=11)
    Stamp_ = None
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    s6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    K.notes.append("L6: crude cap %d; lvl after Mining 11 = %d; name %s" % (caps["Tool_Pickaxe_Crude"], int(Data.num(doc(s6), "lvl", -1)), View.nameText(s6.getItemId(), doc(s6))))
    K.check(int(Data.num(doc(s6), "lvl", -1)) == min(11, caps["Tool_Pickaxe_Crude"]) and str(View.lvTag(s6.getItemId(), doc(s6))) == " [Lv %d]" % min(11, caps["Tool_Pickaxe_Crude"])
            and ("[Lv %d]" % min(11, caps["Tool_Pickaxe_Crude"])) in str(s6.getMetadata().toJson()),
            "L6: a skill level-up -> the next sweep rewrites the tool's level and its name says [Lv N] (Skyy: 'when the skill levels up ... levels up the tool')")
    skills(Mining=40)
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    s6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    K.check(int(Data.num(doc(s6), "lvl", -1)) == caps["Tool_Pickaxe_Crude"], "L6: ... but never above its tier's top (Mining 40 -> Crude Lv %d)" % caps["Tool_Pickaxe_Crude"])
    n_w = int(Life.N[1])
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    LL.LAST.clear()
    Life.sweep(PR1, inv6, True)
    K.check(int(Life.N[1]) == n_w, "L6: nothing changed -> no write (the sweep only writes what moved)")
    Life.sweep(PR1, inv6, False)
    t0_ = int(Life.N[0])
    Life.sweep(PR1, inv6, False)
    K.check(int(Life.N[0]) == t0_, "L6: the per-scan sweep is throttled (400 ms)")
    # a foreign lifelong tool + a stale copy of mine
    inv7, cs7 = mkinv()
    PKEY[str(U2)] = "p2"
    skills(U2, Mining=5, Foraging=5, Farming=5)
    Life.sweep0(PR2, inv7, True)
    L7 = dict((x[2], x) for x in lls(cs7, "p2"))
    theirs = cs7[L7[0][0]].getItemStack(JShort(L7[0][1]))
    cs6["storage"].setItemStackForSlot(JShort(30), theirs)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(cs6["storage"].getItemStack(JShort(30)) is not None and str(LL.owner(doc(cs6["storage"].getItemStack(JShort(30))))) == "p2",
            "L6: another player's lifelong tool (their current one) in my inventory is left alone")
    # FIX A-1 / engine-1: another player's lifelong tool breaks NOTHING for you (the REAL hit system, ore / log / stone), yours still works
    n7 = int(LL.N[7])
    own6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    rf1 = hit(theirs, "Ore_Copper_Stone")
    rf2 = hit(theirs, "Rock_Stone")
    rf3 = hit(own6, "Rock_Stone")
    rf4 = hit(own6, "Ore_Copper_Stone")
    K.check(rf1[0] and rf2[0] and not rf3[0] and not rf4[0] and int(LL.N[7]) == n7 + 2,
            "FIX A-1 / engine-1: THE REAL HIT SYSTEM: p2's lifelong pickaxe in p1's hand is refused on copper ore AND on stone (a handed-over tool is "
            "useless, so /pickaxe after handing yours over gives no second working tool); p1's own Crude pickaxe still mines stone + copper: %s"
            % [rf1, rf2, rf3, rf4])
    tip = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    LL.lines(U1, theirs.getItemId(), doc(theirs), tip[0], tip[1])
    K.check([str(x) for x in tip[0]] == ["Lifelong tool of another player"], "L6: its tooltip says whose it is")
    # /pickaxe for p1 while the pickaxe is in a chest
    cpk = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    chest = SIC(JShort(27))
    chest.setItemStackForSlot(JShort(0), cpk)
    cs6[pk6[0]].removeItemStackFromSlot(JShort(pk6[1]))
    refR, stR, chR, plR = world(inv6, cs6, PR1)
    apply(lifelong__reclaimTier="false")          # this part: the tier you had (the default since fix round 2)
    r_rc = str(Life.reclaim(PR1, plR, JInt(0)))
    L6b = dict((x[2], x) for x in lls(cs6, "p1"))
    rep_ = L6b[0]
    K.check(r_rc.startswith("+Your pickaxe cannot be reached") and ("exact copy: " + str(Gear.itemName("Tool_Pickaxe_Crude"))) in r_rc and rep_[5]
            and str(rep_[6].getItemId()) == "Tool_Pickaxe_Crude" and str(Data.str(doc(rep_[6]), "lcu", "")) == pk6[3] and rep_[3] != pk6[3]
            and regfile("p1").get("pickaxe.uid") == rep_[3] and regfile("p1").get("pickaxe.rp") == "1" and str(Data.str(doc(rep_[6]), "r", "")) == "normal",
            "L6 (0.3.2): /pickaxe with the pickaxe in an untracked chest: an EXACT copy (lrp, the same item + rarity, a new uid, lcu = the original's), "
            "the registry names it: %s" % r_rc)
    r_rc2 = str(Life.reclaim(PR1, plR, JInt(0)))
    K.check(r_rc2.startswith("-You still have your lifelong pickaxe"), "L6: /pickaxe again: refused - you have one: %s" % r_rc2)
    # the original comes back from the chest: it is the lifelong one again, the replacement goes (no dupe)
    cs6["storage"].setItemStackForSlot(JShort(20), chest.getItemStack(JShort(0)))
    chest.removeItemStackFromSlot(JShort(0))
    PR1.said = None
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    L6c = [x for x in lls(cs6, "p1") if x[2] == 0]
    K.check(len(L6c) == 1 and L6c[0][3] == pk6[3] and not L6c[0][5] and regfile("p1").get("pickaxe.uid") == pk6[3] and regfile("p1").get("pickaxe.rp") == "0"
            and ids(cs6).get("Tool_Pickaxe_Crude") == 2 and any("is back - the replacement" in x for x in said(PR1)),
            "L6: THE DUPE GUARD: the original came back -> it is the lifelong pickaxe again, the replacement is gone (one of mine + the other player's): %s"
            % [(x[0], x[1], x[5]) for x in L6c])
    # a replacement copy that comes back after its original returned (it was in another chest): removed
    cs6["storage"].setItemStackForSlot(JShort(21), rep_[6])
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(ids(cs6).get("Tool_Pickaxe_Crude") == 2 and cs6["storage"].getItemStack(JShort(21)) is None,
            "L6: a stale replacement (lrp) that turns up later is removed - it was free")
    # a COPY of the current lifelong stack in the same inventory (Creative pick-block, an engine glitch): the second one goes
    curp = [x for x in lls(cs6, "p1") if x[2] == 0][0]
    cs6["storage"].setItemStackForSlot(JShort(25), curp[6])
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(len([x for x in lls(cs6, "p1") if x[2] == 0]) == 1 and cs6[curp[0]].getItemStack(JShort(curp[1])) is not None,
            "L6: a second stack carrying the current lifelong uid in the same inventory is removed (the first one in scan order stays)")
    # a stale NON-replacement while the current is a non-replacement: RETIRED (fix round 2 - was: plain), rolls kept
    staled = Data.put(stack("Tool_Hatchet_Copper"), Life.llDoc(Roll.newDoc("Tool_Hatchet_Copper", JInt(3), True, "craft", JInt(12)), "Tool_Hatchet_Copper", U1, "p1", "deadbeefdeadbeef", False), None)
    cs6["storage"].setItemStackForSlot(JShort(22), staled)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    s22 = cs6["storage"].getItemStack(JShort(22))
    K.check(s22 is not None and bool(LL.isLL(doc(s22))) and bool(LL.isRt(doc(s22))) and str(Data.str(doc(s22), "r", "")) == "legendary",
            "L6 + FIX2 safety-2: an older lifelong tool (not a replacement, not the one /lifelong re-picked away from) is RETIRED (still lifelong, "
            "breaks nothing) and keeps its Legendary roll - never a free plain tool")
    # a foreign REPLACEMENT that is no longer its owner's lifelong one: removed from whoever holds it
    inv8, cs8 = mkinv()
    refS, stS, chS, plS = world(inv7, cs7, PR2)
    cx = cs7[L7[1][0]].getItemStack(JShort(L7[1][1]))
    chest.setItemStackForSlot(JShort(1), cx)
    cs7[L7[1][0]].removeItemStackFromSlot(JShort(L7[1][1]))
    LL.REG.remove("p2")
    r2 = str(Life.reclaim(PR2, plS, JInt(1)))
    rep2 = [x for x in lls(cs7, "p2") if x[2] == 1][0]
    cs6["storage"].setItemStackForSlot(JShort(23), rep2[6])          # p2 hands the replacement to p1 through a chest
    cs7[rep2[0]].removeItemStackFromSlot(JShort(rep2[1]))
    cs7["storage"].setItemStackForSlot(JShort(24), chest.getItemStack(JShort(1)))   # p2 takes the original back
    LL.LAST.clear()
    Life.sweep0(PR2, inv7, True)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(r2.startswith("+") and cs6["storage"].getItemStack(JShort(23)) is None and len([x for x in lls(cs7, "p2") if x[2] == 1]) == 1,
            "L6: a /hatchet replacement passed to another player is removed once its owner's original is back (no free tools by trading)")
    # registry unreadable -> hands off
    wipe_home()
    os.makedirs(os.path.join(HOME, "lifelong"), exist_ok=True)
    os.makedirs(os.path.join(HOME, "lifelong", "p1.properties"), exist_ok=True)       # a folder where the file should be = unreadable
    inv9, cs9 = mkinv()
    Life.sweep0(PR1, inv9, True)
    K.check(not lls(cs9) and bool(LL.bad(LL.reg("p1"))), "L6: an unreadable registry file: nothing is given / marked for that profile (and it is never overwritten)")
    shutil.rmtree(os.path.join(HOME, "lifelong"), ignore_errors=True)
    # FIX2 safety-3: the bad read is NOT cached for the uptime - within 30 s still hands off, then read again (the file is fine now)
    still_bad = bool(LL.bad(LL.reg("p1"))) and not bool(LL.REG.containsKey("p1"))
    LL.BADAT.put("p1", JObject(JLong(int(__import__("time").time() * 1000) - 31000), Long_))
    healed = not bool(LL.bad(LL.reg("p1"))) and bool(LL.REG.containsKey("p1"))
    LL.LAST.clear()
    Life.sweep0(PR1, inv9, True)
    K.check(still_bad and healed and len(lls(cs9, "p1")) == 4,
            "FIX2 safety-3: an unreadable registry is not cached as bad: 30 s later it is read again and the profile gets its tools: %s" % [still_bad, healed])
    LL.REG.clear()
    LL.BADAT.clear()
    apply()

    # ============================================================================ FX: the fix round's own paths
    # (1) FIX A-2: an INVESTED replacement (reforged / tiered up) is never thrown away when the original turns up
    wipe_home()
    logs()
    invX, csX = mkinv()
    refX, stX, chX, plX = world(invX, csX, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    csX["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(3), True, "craft", JInt(8)), None))
    Life.sweep0(PR1, invX, True)
    oX = [x for x in lls(csX, "p1") if x[2] == 0][0]
    chestX = SIC(JShort(27))
    chestX.setItemStackForSlot(JShort(0), oX[6])
    csX[oX[0]].removeItemStackFromSlot(JShort(oX[1]))
    apply(lifelong__reclaimTier="false")
    rX = str(Life.reclaim(PR1, plX, JInt(0)))
    apply()
    rpX = [x for x in lls(csX, "p1") if x[2] == 0][0]
    K.check(rX.startswith("+") and rpX[5] and int(Data.num(doc(rpX[6]), "lrpT", -1)) == 0, "FX: the replacement carries the tier it was given at (lrpT 0): %s" % rX)
    # the player reforges it (rfN 1 - what GearForge writes) -> invested; the next sweep remembers it (inv=1)
    rdoc = doc(rpX[6]).clone()
    rdoc.put("rfN", JClass("org.bson.BsonInt32")(JInt(1)))
    csX[rpX[0]].setItemStackForSlot(JShort(rpX[1]), Data.put(stack("Tool_Pickaxe_Crude"), rdoc, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    K.check(bool(LL.invested("Tool_Pickaxe_Crude", rdoc)) and regfile("p1").get("pickaxe.inv") == "1" and regfile("p1").get("pickaxe.rp") == "1",
            "FX: a reforged replacement is invested; the registry remembers it (pickaxe.inv=1)")
    PR1.said = None
    csX["storage"].setItemStackForSlot(JShort(20), chestX.getItemStack(JShort(0)))      # the original comes back
    chestX.removeItemStackFromSlot(JShort(0))
    nX = ids(csX).get("Tool_Pickaxe_Crude")
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    LX = [x for x in lls(csX, "p1") if x[2] == 0]
    o20 = csX["storage"].getItemStack(JShort(20))
    rfX = regfile("p1")
    LX = [x for x in LX if not bool(LL.isRt(doc(x[6])))]          # fix round 2: the original stays lifelong, RETIRED
    K.check(len(LX) == 1 and LX[0][3] == rpX[3] and not LX[0][5] and int(Data.num(doc(LX[0][6]), "rfN", 0)) == 1 and o20 is not None
            and bool(LL.isLL(doc(o20))) and bool(LL.isRt(doc(o20))) and str(Data.str(doc(o20), "r", "")) == "legendary" and ids(csX).get("Tool_Pickaxe_Crude") == nX
            and rfX.get("pickaxe.uid") == rpX[3] and rfX.get("pickaxe.rp") == "0" and "pickaxe.inv" not in rfX
            and any("upgraded its replacement" in x for x in said(PR1)),
            "FIX A-2 + FIX2 safety-2: the original came back while the REFORGED replacement is current: nothing is removed - the replacement stays the "
            "lifelong pickaxe (rp=0, its lrp mark gone), the original is RETIRED (lifelong, Legendary roll kept - not a plain tool), item count unchanged: %s" % ((
                [(x[0], x[1], x[5]) for x in LX], dict((k, v) for k, v in rfX.items() if k.startswith("pickaxe."))),))
    # an invested replacement that turns up while an ORIGINAL is current is demoted (kept as a plain tool), never removed
    stale_inv = Life.llDoc(Roll.newDoc("Tool_Pickaxe_Copper", JInt(0), True, "craft", JInt(10)), "Tool_Pickaxe_Copper", U1, "p1", "feedfeedfeedfeed", True)
    stale_inv.put("lrpT", JClass("org.bson.BsonInt32")(JInt(0)))          # given Crude, tiered up to Copper
    csX["storage"].setItemStackForSlot(JShort(21), Data.put(stack("Tool_Pickaxe_Copper"), stale_inv, None))
    stale_free = Life.llDoc(None, "Tool_Pickaxe_Copper", U1, "p1", "beefbeefbeefbeef", True)          # a free (not invested) one
    csX["storage"].setItemStackForSlot(JShort(22), Data.put(stack("Tool_Pickaxe_Copper"), stale_free, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    s21, s22 = csX["storage"].getItemStack(JShort(21)), csX["storage"].getItemStack(JShort(22))
    K.check(s21 is not None and bool(LL.isRt(doc(s21))) and s22 is None and len([x for x in lls(csX, "p1") if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]) == 1,
            "FIX A-2 + FIX2: a stale replacement someone tiered up (Crude -> Copper) is RETIRED (kept, never plain), a free stale one is removed as before")
    lgX = logs()
    K.check(any("LL-SETTLE " in l for l in lgX), "FX: gear.log has the LL-SETTLE line")
    # (2) FIX C-1 / A-4: /pickaxe gives the tier your skill level fits (Skyy G2: Mining 20 -> Iron), never below the tier you had
    tf = [str(LL.tierFor(U1, JInt(0), "Tool_Pickaxe_Crude")) for _m in (0,)]
    res_tf = []
    for mlv, had in ((20, "Tool_Pickaxe_Crude"), (1, "Tool_Pickaxe_Crude"), (16, "Tool_Pickaxe_Crude"), (26, "Tool_Pickaxe_Copper"), (49, "Tool_Pickaxe_Crude"),
                     (20, "Tool_Pickaxe_Cobalt")):
        skills(Mining=mlv)
        res_tf.append(str(LL.tierFor(U1, JInt(0), had)))
    skills(Farming=49)
    res_tf.append(str(LL.tierFor(U1, JInt(3), "Tool_Sickle_Crude")))
    res_tf.append(str(LL.tierFor(U1, JInt(2), "Tool_Hoe_Crude")))
    br.remove("skill:fn:level")
    Gate.forget(U1)
    res_tf.append(str(LL.tierFor(U1, JInt(0), "Tool_Pickaxe_Copper")))
    br.put("skill:fn:level", SkillFn())
    K.check(res_tf == ["Tool_Pickaxe_Iron", "Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Thorium", "Tool_Pickaxe_Adamantite", "Tool_Pickaxe_Cobalt",
                       "Tool_Sickle_Iron", "Tool_Hoe_Thorium", "Tool_Pickaxe_Copper"],
            "FIX C-1: tierFor = the first ladder tier whose band holds your level (Mining 20 -> Iron = Skyy's own example, 1 -> Crude, 16 -> Copper, "
            "26 -> Thorium, 49 -> the ladder top Adamantite), never below the tier you had (Cobalt at 20 stays Cobalt); sickles end at Iron, hoes at "
            "Thorium; no SkyySkills = the tier you had: %s" % res_tf)
    wipe_home()
    invY, csY = mkinv()
    refY, stY, chY, plY = world(invY, csY, PR1)
    skills(Mining=20, Foraging=1, Farming=1)
    Life.sweep0(PR1, invY, True)
    yP = [x for x in lls(csY, "p1") if x[2] == 0][0]
    csY[yP[0]].removeItemStackFromSlot(JShort(yP[1]))
    apply(lifelong__reclaimTier="true")          # fix round 2: the row is OFF by default now
    rY = str(Life.reclaim(PR1, plY, JInt(0)))
    gY = [x for x in lls(csY, "p1") if x[2] == 0]
    apply(lifelong__reclaimSec="0")          # the default (reclaimTier off)
    csY[gY[0][0]].removeItemStackFromSlot(JShort(gY[0][1]))
    LL.reg("p1").setProperty("pickaxe.id", "Tool_Pickaxe_Crude")
    rY2 = str(Life.reclaim(PR1, plY, JInt(0)))
    gY2 = [x for x in lls(csY, "p1") if x[2] == 0]
    apply()
    K.check(rY.startswith("+Your pickaxe cannot be reached") and str(gY[0][6].getItemId()) == "Tool_Pickaxe_Crude"
            and int(Data.num(doc(gY[0][6]), "lrpT", -1)) == 0 and str(gY2[0][6].getItemId()) == "Tool_Pickaxe_Crude" and len(gY2) == 1,
            "FIX C-1 -> 0.3.2: lifelong.reclaimTier is a LEGACY row - ON changes nothing: /pickaxe at Mining 20 after losing a Crude pickaxe = an "
            "exact copy of that Crude pickaxe (no free tier-up either way): %s | %s" % (rY, rY2))
    # (3) FIX engine-2: the held-tool recompute flags a stale [Lv N]; GearHandSys hands it to the stamp task (its sweep rewrites the level)
    wipe_home()
    invZ, csZ = mkinv()
    skills(Mining=10, Foraging=10, Farming=10)
    Life.sweep0(PR1, invZ, True)
    zP = [x for x in lls(csZ, "p1") if x[2] == 0][0][6]
    P("GearArmLv").LV.clear()          # 0.3.4: the armor watch's first look only remembers the Mining level
    LL.RESYNC.clear()
    Tool.LAST.clear()
    Tool.held(U1, zP)
    r_same = bool(LL.RESYNC.containsKey(U1))
    skills(Mining=11)
    Tool.LAST.clear()
    Tool.held(U1, zP)
    r_up = bool(LL.RESYNC.containsKey(U1))
    LL.RESYNC.clear()
    Tool.LAST.clear()
    Tool.held(U1, theirs)
    r_for = bool(LL.RESYNC.containsKey(U1))
    LL.RESYNC.clear()
    K.check(not r_same and r_up and not r_for, "FIX engine-2: GearTool.held (GearHandSys, once a second) flags the held lifelong pickaxe after a Mining "
            "level-up (not before, not for another player's tool) - GearHandSys.tick then calls GearStamp.dirtyIn (C: GearHandSys ~tick): %s"
            % [r_same, r_up, r_for])
    # (4) FIX engine-4: the Drop key on a lifelong tool inside an open CHEST WINDOW: cancelled + the window marked changed (re-sent)
    wipe_home()
    invW, csW = mkinv()
    refW, stW, chW, plW = world(invW, csW, PR1)
    Life.sweep0(PR1, invW, True)
    wP = [x for x in lls(csW, "p1") if x[2] == 0][0]
    chestW = SIC(JShort(27))
    chestW.setItemStackForSlot(JShort(3), wP[6])
    csW[wP[0]].removeItemStackFromSlot(JShort(wP[1]))
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    CWc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    win_ok = None
    WINc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")

    def wdirty(w_):
        return bool(jf(WINc, "isDirty").get(w_).getAndSet(False))
    try:
        wm = WMc()
        jf(WMc, "windowId").get(wm).set(JInt(10))
        cw = CWc(chestW)
        wm.setWindow(JInt(4), cw)
        wmf = None
        k_ = PLA.class_
        while k_ is not None and wmf is None:
            for f_ in k_.getDeclaredFields():
                if f_.getType() == WMc.class_:
                    f_.setAccessible(True)
                    wmf = f_
            k_ = k_.getSuperclass()
        wmf.set(plW, wm)
        wdirty(cw)
        DIRQw = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
        DropW = JClass(PKG + "GearLLDropSys")()
        ew = DIRQw(JInt(4), JShort(3))
        DropW.handle(JInt(0), chW, stW, None, ew)
        chestW.setItemStackForSlot(JShort(5), stack("Rock_Stone", 3))
        wdirty(cw)
        ew2 = DIRQw(JInt(4), JShort(5))
        DropW.handle(JInt(0), chW, stW, None, ew2)
        d2 = wdirty(cw)
        win_ok = (bool(ew.isCancelled()), chestW.getItemStack(JShort(3)) is not None, not bool(ew2.isCancelled()), d2)
    except Exception as ex_:
        K.notes.append("FX: the chest-window drop could not be staged: %s" % str(ex_)[:200])
    K.check(win_ok is not None and win_ok[0] and win_ok[1] and win_ok[2] and not win_ok[3],
            "FIX engine-4: the Drop key on the lifelong pickaxe in an open chest window (section id 4 = a real ContainerWindow) is cancelled and the "
            "tool stays; stone from the same window is not: %s" % (win_ok,))
    # the window was marked changed by the cancelled drop: re-run the lifelong one and read the flag right after
    if win_ok is not None:
        wdirty(cw)
        ew3 = DIRQw(JInt(4), JShort(3))
        DropW.handle(JInt(0), chW, stW, None, ew3)
        K.check(bool(ew3.isCancelled()) and wdirty(cw),
                "FIX engine-4: ... and the cancelled drop marked the chest window changed (WindowManager.markWindowChanged -> Window.invalidate: "
                "PlayerSendInventorySystem re-sends it, the client shows the tool back)")
    # (5) FIX A-1: the hand-over sequence end to end: p1's ORIGINAL goes to p2 through a chest, p1 types /pickaxe, p2's copy breaks nothing
    wipe_home()
    PKEY[str(U2)] = "p2"
    invA, csA = mkinv()
    refA, stA, chA, plA = world(invA, csA, PR1)
    invB, csB = mkinv()
    skills(Mining=20)
    skills(U2, Mining=20)
    Life.sweep0(PR1, invA, True)
    Life.sweep0(PR2, invB, True)
    aO = [x for x in lls(csA, "p1") if x[2] == 0][0]
    csB["storage"].setItemStackForSlot(JShort(30), aO[6])          # handed to p2 (chest / trade)
    csA[aO[0]].removeItemStackFromSlot(JShort(aO[1]))
    rA = str(Life.reclaim(PR1, plA, JInt(0)))
    LL.LAST.clear()
    Life.sweep0(PR2, invB, True)
    held_by_b = csB["storage"].getItemStack(JShort(30))
    K.check(rA.startswith("+") and held_by_b is not None and int(LL.hit(PR2, held_by_b, BL["Ore_Copper_Stone"])) == 2
            and int(LL.hit(PR2, held_by_b, BL["Rock_Stone"])) == 2 and int(LL.hit(PR1, [x for x in lls(csA, "p1") if x[2] == 0][0][6], BL["Rock_Stone"])) == 0,
            "FIX A-1: p1 hands the original pickaxe to p2 and gets a replacement with /pickaxe: the original stays p1's item (kept for when it comes back) "
            "but breaks nothing for p2 - no second working tool: %s" % rA)
    wipe_home()

    # ============================================================================ FX2: the second fix round's own paths
    BI32 = JClass("org.bson.BsonInt32")
    SECID_X = {"hotbar": -1, "storage": -2, "armor": -3, "utility": -5, "tools": -8, "backpack": -9}
    DIRQx = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    DropX = JClass(PKG + "GearLLDropSys")()
    # (1) FIX2 safety-2: THE EXPLOIT SEQUENCE - original in a chest, /pickaxe, reforge the replacement, take the original back: the original
    # is RETIRED (still lifelong, never sold, breaks nothing, may be dropped), never a plain rolled tool; /lifelong swaps the two
    wipe_home()
    logs()
    invQ, csQ = mkinv()
    refQ, stQ, chQ, plQ = world(invQ, csQ, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    csQ["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(3), True, "craft", JInt(8)), None))
    Life.sweep0(PR1, invQ, True)
    oQ = [x for x in lls(csQ, "p1") if x[2] == 0][0]
    chestQ = SIC(JShort(27))
    chestQ.setItemStackForSlot(JShort(0), oQ[6])
    csQ[oQ[0]].removeItemStackFromSlot(JShort(oQ[1]))
    # 0.3.2 fix round (safety critic 1): an EXACT copy and its original never swap (LT5); this check keeps the 0.3.0 swap for the legacy
    # replacement (no snapshot = a Common tool, not a copy of the original)
    for k_ in ("pickaxe.snap", "pickaxe.snapId", "pickaxe.snapU"):
        LL.reg("p1").remove(k_)
    rQ = str(Life.reclaim(PR1, plQ, JInt(0)))
    rpQ = [x for x in lls(csQ, "p1") if x[2] == 0][0]
    rdq = doc(rpQ[6]).clone()
    rdq.put("rfN", BI32(JInt(1)))
    csQ[rpQ[0]].setItemStackForSlot(JShort(rpQ[1]), Data.put(stack("Tool_Pickaxe_Crude"), rdq, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invQ, True)
    csQ["storage"].setItemStackForSlot(JShort(20), chestQ.getItemStack(JShort(0)))
    chestQ.removeItemStackFromSlot(JShort(0))
    nQ = ids(csQ).get("Tool_Pickaxe_Crude")
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invQ, True)
    oS = csQ["storage"].getItemStack(JShort(20))
    oD = doc(oS)
    rS_ = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    hO1, hO2, hR = hit(oS, "Rock_Stone"), hit(oS, "Ore_Copper_Stone"), hit(rS_, "Rock_Stone")
    tipO = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    LL.lines(U1, oS.getItemId(), oD, tipO[0], tipO[1])
    eO = DIRQx(JInt(-2), JShort(20))
    DropX.handle(JInt(0), chQ, stQ, None, eO)
    eR = DIRQx(JInt(SECID_X[rpQ[0]]), JShort(rpQ[1]))
    DropX.handle(JInt(0), chQ, stQ, None, eR)
    K.check(rQ.startswith("+") and oS is not None and bool(LL.isLL(oD)) and bool(LL.isRt(oD)) and str(LL.owner(oD)) == "p1"
            and str(Data.str(oD, "r", "")) == "legendary" and ids(csQ).get("Tool_Pickaxe_Crude") == nQ and regfile("p1").get("pickaxe.uid") == rpQ[3]
            and Wall.why(oS.getItemId(), oS.getMetadata()) is not None and not bool(LL.mine(U1, oD))
            and hO1[0] and hO2[0] and not hR[0] and "Retired lifelong pickaxe - it breaks nothing" in [str(x) for x in tipO[0]]
            and not bool(eO.isCancelled()) and bool(eR.isCancelled()),
            "FIX2 safety-2: original in a chest -> /pickaxe -> reforge the replacement -> take the original back: the original is RETIRED (still "
            "lifelong + p1's, Legendary kept, the market wall refuses it, it breaks NOTHING - stone or ore, its tooltip says so, it MAY be dropped); "
            "the reforged replacement is the one working pickaxe (it can't be dropped); item count unchanged: %s" % [rQ, hO1, hO2, hR, [str(x) for x in tipO[0]]])
    # /lifelong on the retired original swaps them (any time, no once-per-kind limit): one working pickaxe, never a plain one
    csQ["hotbar"].setItemStackForSlot(JShort(0), oS)
    csQ["storage"].removeItemStackFromSlot(JShort(20))
    PR1.said = None
    rSw = str(Life.repick(PR1, plQ))
    h0 = csQ["hotbar"].getItemStack(JShort(0))
    rNow = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    regA = regfile("p1").get("pickaxe.uid")
    hA, hB = hit(h0, "Rock_Stone")[0], hit(rNow, "Rock_Stone")[0]
    rSw2 = str(Life.repick(PR1, plQ))
    csQ["hotbar"].setItemStackForSlot(JShort(0), rNow)
    csQ[rpQ[0]].setItemStackForSlot(JShort(rpQ[1]), h0)
    rSw3 = str(Life.repick(PR1, plQ))
    back0 = csQ["hotbar"].getItemStack(JShort(0))
    oNow = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    lgQ = logs()
    K.check(rSw.startswith("+") and "again" in rSw and bool(LL.isLL(doc(h0))) and not bool(LL.isRt(doc(h0))) and str(LL.uid(doc(h0))) == oQ[3]
            and bool(LL.isRt(doc(rNow))) and regA == oQ[3] and not hA and hB and regfile("p1").get("pickaxe.uid") == rpQ[3]
            and rSw2.startswith("-That already is your lifelong pickaxe") and rSw3.startswith("+") and not bool(LL.isRt(doc(back0)))
            and bool(LL.isRt(doc(oNow))) and str(LL.uid(doc(back0))) == rpQ[3] and ids(csQ).get("Tool_Pickaxe_Crude") == nQ
            and len([x for x in lls(csQ, "p1") if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]) == 1
            and any("LL-RETIRE " in l for l in lgQ) and len([l for l in lgQ if "LL-SWAP " in l]) == 2 and not any("LL-DEMOTE " in l for l in lgQ),
            "FIX2 safety-2: /lifelong on the retired original swaps it back (the replacement retires), again on the current one is refused, and "
            "swapping back works too: always exactly ONE working pickaxe, nothing turns plain, counts unchanged: %s | %s | %s" % (rSw, rSw2, rSw3))
    # (2) FIX2 cross-mod-2: another player's lifelong tool in my inventory may be dropped (it is useless to me); mine may not
    theirsQ = Data.put(stack("Tool_Hatchet_Crude"), Life.llDoc(None, "Tool_Hatchet_Crude", U2, "p2", "abcabcabcabcabca", False), None)
    csQ["storage"].setItemStackForSlot(JShort(30), theirsQ)
    eT = DIRQx(JInt(-2), JShort(30))
    DropX.handle(JInt(0), chQ, stQ, None, eT)
    K.check(not bool(eT.isCancelled()) and bool(eR.isCancelled()),
            "FIX2 cross-mod-2: the Drop key on ANOTHER player's lifelong hatchet is not cancelled (nobody is stuck with a tool they can't use)")
    # (3) FIX2 cross-mod-1: gear:fn:lifelong(UUID) -> Integer kinds owned (SkyyQuests' tutorial "lifelong 4/4"); the Object[] form unchanged
    FnQ = JClass(PKG + "GearLLFn")(JInt(0))
    FnQ1 = JClass(PKG + "GearLLFn")(JInt(1))
    nk = FnQ.apply(U1)
    nk2 = FnQ.apply(U2)
    K.check(nk is not None and int(nk) == 4 and str(nk.getClass().getName()) == "java.lang.Integer" and FnQ1.apply(U1) is None
            and str(FnQ.apply(JArray(JObject)([U1, JString("pickaxe")]))) == regfile("p1").get("pickaxe.uid"),
            "FIX2 cross-mod-1: gear:fn:lifelong(bare UUID) = Integer 4 for a migrated profile (%s for an unknown one); perk / farmTier ignore a bare UUID; "
            "the Object[] form still gives the uid" % nk2)
    # (4) FIX2 safety-4: a failing registry write WARNs once per 30 s and the every-scan sweep waits (forced ones still try)
    wipe_home()
    logs()
    LL.TOLD.remove("save:p1")          # the earlier failing-write checks of this harness ran < 30 s ago
    LL.FAIL_SAVE = True
    for _i in range(5):
        LL.save("p1", Props())
    LL.FAIL_SAVE = False
    lgW = logs()
    nwarn = len([l for l in lgW if "could not be written" in l])
    invV, csV = mkinv()
    failing0 = bool(LL.failing("p1"))
    LL.LAST.clear()
    Life.sweep0(PR1, invV, False)
    skipped = not lls(csV)
    Life.sweep0(PR1, invV, True)
    K.check(nwarn == 1 and failing0 and skipped and len(lls(csV, "p1")) == 4 and not bool(LL.failing("p1")),
            "FIX2 safety-4: 5 failed registry writes = ONE WARN; the every-scan sweep then waits 30 s, a forced one (join / a command) still runs and "
            "a good write clears the back-off: %s" % [nwarn, failing0, skipped])
    # (5) FIX2 safety-5: the migration logs the old level + coin-bought levels (lvU) and says so when the level drops
    wipe_home()
    logs()
    invU, csU = mkinv()
    skills(Mining=5, Foraging=5, Farming=5)
    dU = Roll.newDoc("Tool_Pickaxe_Copper", JInt(2), True, "craft", JInt(17))
    dU.put("lvU", BI32(JInt(3)))
    csU["storage"].setItemStackForSlot(JShort(2), Data.put(stack("Tool_Pickaxe_Copper"), dU, None))
    PR1.said = None
    Life.sweep0(PR1, invU, True)
    lgU = logs()
    mk = [l for l in lgU if "LL-MARK " in l and "Tool_Pickaxe_Copper" in l]
    K.check(len(mk) == 1 and "(was lv17, bought lvU 3)" in mk[0] and any("was Lv 17 (3 of it bought with coins)" in x for x in said(PR1))
            and any("Only your inventory was checked" in x and "Vault" in x for x in said(PR1)),
            "FIX2 safety-5 + design-6: LL-MARK says 'was lv17, bought lvU 3', the player is told the level now follows Mining; the notice points "
            "at chests / the Void / the Vault: %s" % (mk[:1],))
    # (6) FIX2 design-1 -> 0.3.1: gate.crudeFactor is an unused LEGACY row (Crude counts as Copper): setting it changes nothing; the one-up
    # factor is gate.nextFactor for every tier, slowF(1) / slowF(3) = the one-up / two-up rows
    skills(Mining=10, Foraging=10)
    apply(gate__crudeFactor="0.25")
    Tool.LAST.clear()
    refC = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Oak_Trunk"], JFloat(0.3)))
    rC = hit(stack("Tool_Hatchet_Crude"), "Wood_Oak_Trunk")
    Tool.LAST.clear()
    refI = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    rI = hit(stack("Tool_Pickaxe_Iron"), "Ore_Thorium_Sandstone")
    Tool.LAST.clear()
    refM = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Maple_Trunk"], JFloat(0.3)))
    rM = hit(stack("Tool_Hatchet_Crude"), "Wood_Maple_Trunk")
    apply()
    K.check(not rC[0] and abs(rC[1] - refC) < 1e-6 and not rI[0] and abs(rI[1] - float(JFloat(refI * 0.4))) < 1e-6
            and not rM[0] and abs(rM[1] - float(JFloat(refM * 0.4))) < 1e-6
            and abs(float(LL.slowF(JInt(1))) - 0.4) < 1e-12 and abs(float(LL.slowF(JInt(3))) - 0.1) < 1e-12 and abs(float(LL.slowF(JInt(0))) - 1.0) < 1e-12,
            "FIX2 design-1 (0.3.1): gate.crudeFactor 0.25 changes nothing any more - a Crude hatchet on Oak = normal (%.5f), on Maple x0.4 (%.5f), an "
            "Iron pickaxe on thorium x0.4 (%.5f); slowF(1) 0.4, slowF(3) 0.1" % (rC[1], rM[1], rI[1]))
    wipe_home()

    # ============================================================================ L7: /pickaxe in full (every refusal, cooldown, Requip, crash at every step)
    wipe_home()
    logs()
    invP, csP = mkinv()
    refP, stP, chP, plP = world(invP, csP, PR1)
    skills(Mining=20, Foraging=20, Farming=20)
    Life.sweep0(PR1, invP, True)
    Lp = dict((x[2], x) for x in lls(csP, "p1"))
    apply(part__lifelong="false")
    r_off = str(Life.reclaim(PR1, plP, JInt(0)))
    apply()
    br.put("profile:busy:" + str(U1), JBoolean(True))
    r_busy = str(Life.reclaim(PR1, plP, JInt(0)))
    br.remove("profile:busy:" + str(U1))
    r_have = str(Life.reclaim(PR1, plP, JInt(0)))
    pick = csP[Lp[0][0]].getItemStack(JShort(Lp[0][1]))
    csP[Lp[0][0]].removeItemStackFromSlot(JShort(Lp[0][1]))
    RQ["items"] = [("e1", str(pick.getItemId()), pick.getMetadata())]
    r_rq = str(Life.reclaim(PR1, plP, JInt(0)))
    RQ.clear()
    LL.reg("p1").setProperty("pickaxe.id", "Tool_Pickaxe_Iron")         # 0.3.2: the SNAPSHOT (Crude) decides, not the registry's id
    full = []
    for i_ in range(36):
        if csP["storage"].getItemStack(JShort(i_)) is None:
            csP["storage"].setItemStackForSlot(JShort(i_), stack("Rock_Stone"))
            full.append(("storage", i_))
    for sec in ("backpack", "hotbar"):
        for i_ in range(int(csP[sec].getCapacity())):
            if csP[sec].getItemStack(JShort(i_)) is None:
                csP[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone"))
                full.append((sec, i_))
    r_full = str(Life.reclaim(PR1, plP, JInt(0)))
    for sec, i_ in full:
        csP[sec].removeItemStackFromSlot(JShort(i_))
    r_ok = str(Life.reclaim(PR1, plP, JInt(0)))
    newp = [x for x in lls(csP, "p1") if x[2] == 0]
    r_cd = str(Life.reclaim(PR1, plP, JInt(0)))       # it is on me now -> "you still have"
    csP[newp[0][0]].removeItemStackFromSlot(JShort(newp[0][1]))
    r_cd2 = str(Life.reclaim(PR1, plP, JInt(0)))
    K.check(r_off.startswith("-Lifelong tools are switched off") and r_busy.startswith("-Your profile is still loading")
            and r_have.startswith("-You still have your lifelong pickaxe") and r_rq.startswith("-Your lifelong pickaxe is in your Requip")
            and r_full.startswith("-No room") and r_ok.startswith("+Your pickaxe cannot be reached")
            and ("exact copy: %s [Lv %d]" % (Gear.itemName("Tool_Pickaxe_Crude"), int(LL.levelFor(U1, "Tool_Pickaxe_Crude")))) in r_ok and len(newp) == 1
            and str(newp[0][6].getItemId()) == "Tool_Pickaxe_Crude" and r_cd.startswith("-You still have")
            and re.match(r"-Your pickaxe cannot be reached \(.*\)\. You can get an exact copy in \d+ s\.", r_cd2),
            "L7 (0.3.2): /pickaxe: off / busy / you have it / in Requip (not loaded) / no room refused; then an EXACT copy of the lost Crude pickaxe "
            "(the snapshot decides, not a tier); lost again at once = the wait: %s | %s | %s" % (r_full, r_ok, r_cd2))
    apply(lifelong__reclaimSec="0")
    for crash_at in (4, 5, 6):
        LL.reg("p1").setProperty("pickaxe.reclaimAt", "0")
        cur = [x for x in lls(csP, "p1") if x[2] == 0]
        for x in cur:
            csP[x[0]].removeItemStackFromSlot(JShort(x[1]))
        before_n = ids(csP).get("Tool_Pickaxe_Crude", 0)          # 0.3.2: the exact copy is the Crude pickaxe
        Life.CRASH_AT = crash_at
        crashed = False
        try:
            Life.reclaim(PR1, plP, JInt(0))
        except Exception as ex_:
            crashed = ("lifelong step %d" % crash_at) in str(ex_)
        Life.CRASH_AT = 0
        reset_reg()
        Life.sweep0(PR1, invP, True)
        got_n = ids(csP).get("Tool_Pickaxe_Crude", 0)
        cur2 = [x for x in lls(csP, "p1") if x[2] == 0]
        rf = regfile("p1")
        if crash_at == 4:
            okc = got_n == before_n and not cur2 and "pickaxe.pend" not in rf
            r_after = str(Life.reclaim(PR1, plP, JInt(0)))
            okc = okc and r_after.startswith("+") and len([x for x in lls(csP, "p1") if x[2] == 0]) == 1
        else:
            okc = got_n == before_n + 1 and len(cur2) == 1 and rf.get("pickaxe.uid") == cur2[0][3] and "pickaxe.pend" not in rf
        K.check(crashed and okc, "L7: /pickaxe CRASH at step %d then a restart: %s (registry %s)" % (
            crash_at, "nothing given, the journal dropped, /pickaxe works again" if crash_at == 4 else "the given pickaxe is committed, never a 2nd",
            dict((k, v) for k, v in rf.items() if k.startswith("pickaxe."))))
    apply()
    lg7 = logs()
    K.check(any("LL-COPY " in l and " exact copy of " in l for l in lg7) and any("LL-RECOVER " in l and "committed" in l for l in lg7) and any("LL-RECOVER " in l and "journal dropped" in l for l in lg7),
            "L7 (0.3.2): gear.log: LL-COPY (exact copy of <uid>), LL-RECOVER committed / dropped")

    # ============================================================================ LT (0.3.2): THE EXACT LOST TOOL
    # Skyy 2026-10-13: "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"
    WMc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    CWc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    CBWc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow")
    WINc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")
    BS_ = JClass("org.bson.BsonString")
    B64 = JClass("java.util.Base64")
    JStr = JClass("java.lang.String")
    wmf_ = None
    k_ = PLA.class_
    while k_ is not None and wmf_ is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == WMc_.class_:
                f_.setAccessible(True)
                wmf_ = f_
        k_ = k_.getSuperclass()

    def new_wm(pl_, *wins):
        """a REAL WindowManager on the player with these windows open (ids 4, 5, ...); setWindow registers the engine's change events"""
        wm_ = WMc_()
        jf(WMc_, "windowId").get(wm_).set(JInt(20))
        for i_, w_ in enumerate(wins):
            wm_.setWindow(JInt(4 + i_), w_)
        wmf_.set(pl_, wm_)
        return wm_

    def wdirty_(w_):
        return bool(jf(WINc_, "isDirty").get(w_).getAndSet(False))

    def chest_win(c_, x=10, y=64, z=-5):
        return CBWc_(JInt(x), JInt(y), JInt(z), JInt(0), BL["Rock_Stone"], c_)

    @JImplements("java.util.concurrent.Executor")
    class QExec(object):
        def __init__(self):
            self.q = []

        @JOverride
        def execute(self, r_):
            self.q.append(r_)
    FETCH = {"mode": "ok", "cs": None, "store": {}, "calls": 0}

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            FETCH["calls"] += 1
            eid_ = str(o[1])
            if FETCH["mode"] == "refuse":
                return JString("Inventory full - make room first.")
            if FETCH["mode"] == "lie":
                return JString("ok")
            s_ = FETCH["store"].pop(eid_, None)
            if s_ is None:
                return JString("That item is not in Requip any more.")
            c_ = FETCH["cs"]["storage"]
            for i_ in range(int(c_.getCapacity())):
                if c_.getItemStack(JShort(i_)) is None:
                    c_.setItemStackForSlot(JShort(i_), s_)
                    break
            RQ["items"] = [r_ for r_ in RQ.get("items", []) if r_[0] != eid_]
            return JString("ok")

    def pick_now(cs_, pk="p1"):
        """the WORKING lifelong pickaxes (not retired) in this inventory"""
        return [x for x in lls(cs_, pk) if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]

    def slot_of(c_, uid):
        for i_ in range(int(c_.getCapacity())):
            s_ = c_.getItemStack(JShort(i_))
            if s_ is not None and not s_.isEmpty() and doc(s_) is not None and str(LL.uid(doc(s_))) == uid:
                return i_
        return -1

    def num_(v):
        return int(v.get("$numberInt", v.get("$numberLong", -1))) if isinstance(v, dict) else int(v if v is not None else -1)

    def snapjson(rf_):
        t_ = rf_.get("pickaxe.snap")
        return None if t_ is None else json.loads(str(JStr(B64.getDecoder().decode(t_), "UTF-8")))

    def setup_lt(rfn=2):
        """a fresh profile p1 whose pickaxe is a Legendary Iron one (rolled, reforged rfN times) + 1 Fortune perk bought"""
        wipe_home()
        logs()
        Life.TEST_CHESTS = None
        Life.TEST_WKEY = "world1~aaaa"
        PKEY[str(U1)] = "p1"
        inv_, cs_ = mkinv()
        ref_, st_, ch_, pl_ = world(inv_, cs_, PR1)
        skills(Mining=20, Foraging=20, Farming=20)
        d_ = Roll.newDoc("Tool_Pickaxe_Iron", JInt(3), True, "craft", JInt(16))
        d_.put("rfN", BI32(JInt(rfn)))
        cs_["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Iron"), d_, None))
        Life.sweep0(PR1, inv_, True)
        new_wm(pl_)
        return inv_, cs_, ref_, st_, pl_

    def to_chest(cs_, c_, slot=3):
        p_ = pick_now(cs_)[0]
        c_.setItemStackForSlot(JShort(slot), p_[6])
        cs_[p_[0]].removeItemStackFromSlot(JShort(p_[1]))
        return p_

    def tracked_into(pl_, cs_, ref_, st_, c_, win_, slot=3):
        """the player moves the pickaxe into an open window's container; GearInvSys' gate queues the tracker, the world runs it"""
        new_wm(pl_, win_)
        p_ = to_chest(cs_, c_, slot)
        ex_ = QExec()
        jf(PR, "entity").set(PR1, ref_)
        LL.trackMaybe(PR1, st_, ref_, ex_, None)
        LL.trackMaybe(PR1, st_, ref_, ex_, None)          # a second change before the task ran: coalesced
        nq_ = len(ex_.q)
        for r_ in ex_.q:
            r_.run()
        jf(PR, "entity").set(PR1, None)
        return p_, nq_

    # ---- LT1: the snapshot (the sweep makes it; only a real change writes the registry)
    invT, csT, refT, stT, plT = setup_lt()
    P1 = LL.reg("p1")
    r_perk = str(Life.buy(U1, JInt(0), JInt(1)))
    A = pick_now(csT)[0]
    rf1 = regfile("p1")
    sj = snapjson(rf1)
    nw0 = int(LL.N[5])
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nw1 = int(LL.N[5])
    d2 = doc(A[6]).clone()
    d2.put("rfN", BI32(JInt(3)))
    csT[A[0]].setItemStackForSlot(JShort(A[1]), Data.put(stack("Tool_Pickaxe_Iron"), d2, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nw2 = int(LL.N[5])
    sj2 = snapjson(regfile("p1"))
    K.check(r_perk.startswith("+") and sj is not None and rf1.get("pickaxe.snapId") == "Tool_Pickaxe_Iron" and rf1.get("pickaxe.snapU") == A[3]
            and sj.get("r") == "legendary" and "lvl" not in sj and "lrt" not in sj and sj.get("lu") == A[3] and nw1 == nw0
            and nw2 == nw1 + 1 and sj2 is not None and num_(sj2.get("rfN")) == 3,
            "LT1: the sweep keeps a SNAPSHOT of the current pickaxe in the registry (its document minus lvl / lrt, Base64 JSON, item id, uid); "
            "a sweep with nothing changed writes nothing (%d writes), a reforge (rfN 2 -> 3) = exactly one write (%d)" % (nw1 - nw0, nw2 - nw1))
    K.check(str(LL.HERE.get(U1)) == "15:p1" and int(LL.hereMask(LL.HERE.get(U1), "p1")) == 15 and int(LL.hereMask(LL.HERE.get(U1), "p9")) == 0,
            "LT1: GearLL.HERE = the four kinds whose current tool is here (15:p1); another profile key reads 0: %s" % LL.HERE.get(U1))
    # fix round (safety critic 3): snapU pointing at another uid while SNAPRAW still matches -> the sweep re-points it (no shortcut)
    PS1 = LL.reg("p1")
    PS1.setProperty("pickaxe.snapU", "0000000000000000")
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    suF = regfile("p1").get("pickaxe.snapU")
    # fix round (engine critic 2): SNAPRAW is bounded (memory only)
    for i_ in range(4200):
        Life.SNAPRAW.put("zz%d|pickaxe" % i_, "x")
    Life.SNAPRAW.remove("p1|pickaxe")
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nSR = int(Life.SNAPRAW.size())
    K.check(suF == A[3] and nSR <= 8 and regfile("p1").get("pickaxe.snapU") == A[3],
            "LT1 FIX (safety 3 + engine 2): a snapshot whose snapU names another uid is re-pointed by the next sweep even though the document "
            "did not change (%s); SNAPRAW over 4096 entries is cleared on the next real put (%d left)" % (suF, nSR))

    # ---- LT2: the tracker gate (GearLL.trackMaybe) + GearLife.trackLater coalescing + GearTrackTask + GearLife.track on REAL windows
    exN = QExec()
    LL.trackMaybe(PR1, stT, refT, exN, None)          # no window open -> nothing queued
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    rfT = regfile("p1")
    K.check(not exN.q and nq == 1 and rfT.get("pickaxe.locK") == "chest" and rfT.get("pickaxe.locW") == "world1~aaaa"
            and (rfT.get("pickaxe.locX"), rfT.get("pickaxe.locY"), rfT.get("pickaxe.locZ")) == ("10", "64", "-5")
            and str(LL.HERE.get(U1)) == "14:p1" and not bool(LL.TRACKQ.containsKey(U1)),
            "LT2: THE TRACKER: no open window = nothing queued; the pickaxe moved into an open REAL ContainerBlockWindow (10 64 -5) -> ONE world "
            "task for two changes (coalesced), GearTrackTask -> track stores the place (chest, world key, x y z) and clears the kind's HERE bit: %s"
            % dict((k, v) for k, v in rfT.items() if k.startswith("pickaxe.loc")))
    vaultC = SIC(JShort(54))
    cwV = CWc_(vaultC)
    new_wm(plT, cwV)
    hat = [x for x in lls(csT, "p1") if x[2] == 1][0]
    vaultC.setItemStackForSlot(JShort(7), hat[6])
    csT[hat[0]].removeItemStackFromSlot(JShort(hat[1]))
    Life.track(PR1, plT, None)
    rfV = regfile("p1")
    lgT = logs()
    K.check(rfV.get("hatchet.locK") == "window:ContainerWindow" and "hatchet.locW" not in rfV and str(LL.HERE.get(U1)) == "12:p1"
            and any("LL-WHERE " in l and "chest world1 10 64 -5" in l for l in lgT) and any("LL-WHERE " in l and "window:ContainerWindow" in l for l in lgT),
            "LT2: a hatchet moved into an open ContainerWindow (the kind SkyyVault opens) = place 'window:ContainerWindow'; gear.log has LL-WHERE for both")
    # the window comes back to the inventory with the hatchet: the next look clears its place
    csT["storage"].setItemStackForSlot(JShort(30), vaultC.getItemStack(JShort(7)))
    vaultC.removeItemStackFromSlot(JShort(7))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    K.check("hatchet.locK" not in regfile("p1") and str(LL.HERE.get(U1)) == "14:p1", "LT2: the hatchet seen back in the inventory -> its place is cleared")

    # ---- LT3: /pickaxe with the chest window STILL OPEN -> fetched from the window (the exact stack, the same uid)
    new_wm(plT, cbw)
    n15 = int(Life.N[15])
    nI = ids(csT).get("Tool_Pickaxe_Iron", 0)
    r3 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    got3 = pick_now(csT)
    rf3 = regfile("p1")
    K.check(r3.startswith("+Your %s came back from the open chest into your " % Gear.itemName("Tool_Pickaxe_Iron")) and len(got3) == 1 and got3[0][3] == A[3]
            and slot_of(chestC, A[3]) < 0 and rf3.get("pickaxe.uid") == A[3] and "pickaxe.locK" not in rf3 and int(Life.N[15]) == n15 + 1
            and ids(csT).get("Tool_Pickaxe_Iron", 0) == nI + 1 and not got3[0][5],
            "LT3: /pickaxe with the chest window open: the SAME pickaxe (uid %s, not a copy) moves from the chest into the inventory, the place is "
            "cleared, counter +1: %s" % (A[3], r3))
    # the Vault kind of window too
    vaultC2 = SIC(JShort(54))
    cwV2 = CWc_(vaultC2)
    A, _nq = tracked_into(plT, csT, refT, stT, vaultC2, cwV2, 11)
    r3v = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r3v.startswith("+Your %s came back from the open storage window" % Gear.itemName("Tool_Pickaxe_Iron")) and len(pick_now(csT)) == 1
            and pick_now(csT)[0][3] == A[3] and slot_of(vaultC2, A[3]) < 0,
            "LT3: ... and from an open ContainerWindow (the Vault's kind): %s" % r3v)

    # ---- LT3b (fix round, engine critic 1): THE REAL QUEUE ORDER. One inventory change queues GearStampTask (GearStamp.dirty0 -> w.execute,
    # idle player) BEFORE GearTrackTask (trackMaybe a line later); the world queue is FIFO, so the sweep (pass) runs first while the tool is
    # already in the chest - the tracker must still find it
    new_wm(plT, cbw)
    AQ = to_chest(csT, chestC)
    exO = QExec()
    jf(PR, "entity").set(PR1, refT)
    hereB = str(LL.HERE.get(U1))
    LL.trackMaybe(PR1, stT, refT, exO, None)          # GearInvSys: the tracker task is queued (TRACKQ) ...
    LL.LAST.clear()
    Life.sweep0(PR1, invT, False)          # ... but the stamp task queued first runs first (sweepHook -> sweep, not forced)
    hereMid = str(LL.HERE.get(U1))
    nqO = len(exO.q)
    for r_ in exO.q:
        r_.run()
    jf(PR, "entity").set(PR1, None)
    rfQ = regfile("p1")
    hereAfter = str(LL.HERE.get(U1))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, False)
    hereLater = str(LL.HERE.get(U1))
    K.check(nqO == 1 and hereB == "15:p1" and hereMid == "15:p1" and rfQ.get("pickaxe.locK") == "chest"
            and (rfQ.get("pickaxe.locX"), rfQ.get("pickaxe.locY"), rfQ.get("pickaxe.locZ")) == ("10", "64", "-5")
            and hereAfter == "14:p1" and hereLater == "14:p1" and not bool(LL.TRACKQ.containsKey(U1)),
            "LT3b FIX (engine 1): stamp task (sweep) BEFORE the tracker task in queue order: while the tracker is queued the sweep keeps the "
            "pickaxe's HERE bit (%s -> %s), the tracker then records the chest (%s) and clears the bit (%s, still %s after the next sweep)"
            % (hereB, hereMid, rfQ.get("pickaxe.locK"), hereAfter, hereLater))
    rQb = str(Life.reclaimW(PR1, plT, JInt(0), None))          # the window is still open: back into the inventory for LT4
    K.check(rQb.startswith("+Your ") and len(pick_now(csT)) == 1 and pick_now(csT)[0][3] == AQ[3], "LT3b: ... and fetched back: %s" % rQb)

    # ---- LT4: the TRACKED CHEST, windows closed, chunk loaded -> fetched; unloaded -> exact copy; the original turns up -> the copy goes
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    n16 = int(Life.N[16])
    r4 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r4.startswith("+Your %s came back from the chest at 10 64 -5 into your " % Gear.itemName("Tool_Pickaxe_Iron")) and len(pick_now(csT)) == 1
            and pick_now(csT)[0][3] == A[3] and slot_of(chestC, A[3]) < 0 and int(Life.N[16]) == n16 + 1 and "pickaxe.locK" not in regfile("p1"),
            "LT4: /pickaxe with the chest closed but its chunk loaded: the SAME pickaxe comes back from the chest it was put in: %s" % r4)
    # unloaded chunk -> the EXACT copy
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()          # nothing loaded
    origD = doc(chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    perk0 = int(LL.perkOf(LL.reg("p1"), JInt(0), JInt(1)))
    free0 = int(LL.free(U1, LL.reg("p1"), JInt(0)))
    n17 = int(Life.N[17])
    r5 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    cp = pick_now(csT)
    cD = doc(cp[0][6]) if cp else None
    rf5 = regfile("p1")
    K.check(r5.startswith("+Your pickaxe cannot be reached (it is in a chest at 10 64 -5 that is not loaded right now), so here is an exact copy: %s [Lv %d]"
                          % (Gear.itemName("Tool_Pickaxe_Iron"), int(LL.levelFor(U1, "Tool_Pickaxe_Iron"))))
            and len(cp) == 1 and str(cp[0][6].getItemId()) == "Tool_Pickaxe_Iron" and cp[0][3] != A[3] and cp[0][5]
            and str(Data.str(cD, "r", "")) == "legendary" and str(View.modSummary(cD)) == str(View.modSummary(origD))
            and str(Data.str(cD, "rf", "")) == str(Data.str(origD, "rf", "")) and int(Data.num(cD, "rfN", -1)) == int(Data.num(origD, "rfN", -2))
            and int(Data.num(cD, "lrpF", -1)) == int(Data.num(origD, "rfN", -2)) and str(Data.str(cD, "lcu", "")) == A[3]
            and int(Data.num(cD, "lvl", -1)) == int(LL.levelFor(U1, "Tool_Pickaxe_Iron")) and not bool(LL.invested("Tool_Pickaxe_Iron", cD))
            and int(LL.perkOf(LL.reg("p1"), JInt(0), JInt(1))) == perk0 == 1 and int(LL.free(U1, LL.reg("p1"), JInt(0))) == free0
            and rf5.get("pickaxe.uid") == cp[0][3] and rf5.get("pickaxe.rp") == "1" and rf5.get("pickaxe.snapU") == cp[0][3]
            and int(Life.N[17]) == n17 + 1 and slot_of(chestC, A[3]) >= 0,
            "LT4: the chest's chunk is NOT loaded -> an EXACT copy: the same Iron pickaxe, Legendary, the same lines + reforge count, perks (Fortune 1) "
            "and free points unchanged, level = the skill rule, a NEW uid with lcu = the original's, lrpF = the copied reforge count (so it is not "
            "'invested'); the registry names the copy; the original is untouched in the chest: %s" % r5)
    hC = hit(cp[0][6], "Ore_Iron_Stone")
    hO = hit(chestC.getItemStack(JShort(slot_of(chestC, A[3]))), "Rock_Stone")
    csT[cp[0][0]].removeItemStackFromSlot(JShort(cp[0][1]))
    r5w = str(Life.reclaimW(PR1, plT, JInt(0), None))
    csT[cp[0][0]].setItemStackForSlot(JShort(cp[0][1]), cp[0][6])
    K.check(not hC[0] and hO[0] and re.match(r"-Your pickaxe cannot be reached \(.+\)\. You can get an exact copy in \d+ s\.", r5w)
            and "pickaxe.locK" not in regfile("p1"),
            "LT4: only the copy works now (the original in the chest breaks nothing - stale); the copy's commit forgot the ORIGINAL's place (a new "
            "uid); losing the copy at once = the wait (copies only): %s" % r5w)
    # fix round (safety critic 1 + 2): the copy's family is recorded (pickaxe.nsw names the original); a 0.3.1 rollback's .inv=1 on the
    # unchanged copy is re-read by the next look (so the guard still removes the copy, not the original)
    nswF = str(regfile("p1").get("pickaxe.nsw", ""))
    PI4 = LL.reg("p1")
    PI4.setProperty("pickaxe.inv", "1")
    LL.save("p1", PI4)
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    K.check(A[3] in nswF.split(",") and "pickaxe.inv" not in regfile("p1") and bool(Life.family(LL.reg("p1"), "pickaxe", cD))
            and bool(Life.family(LL.reg("p1"), "pickaxe", origD)),
            "LT4 FIX (safety 1 + 2): the copy records its family (pickaxe.nsw = %s); both the copy and the original belong to it; a stale "
            "pickaxe.inv=1 (a 0.3.1 rollback) on the UNCHANGED copy is cleared by the next look" % nswF)
    # the original turns up (the chunk loaded, the player takes it): it is the pickaxe again, the copy disappears - never two
    csT["storage"].setItemStackForSlot(JShort(33), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    PR1.said = None
    LL.TOLD.clear()          # the "is back" line is once per 5 s (an earlier part of this harness said it moments ago)
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    nowP = pick_now(csT)
    K.check(len(nowP) == 1 and nowP[0][3] == A[3] and regfile("p1").get("pickaxe.uid") == A[3] and regfile("p1").get("pickaxe.rp") == "0"
            and ids(csT).get("Tool_Pickaxe_Iron", 0) == 1 and len(lls(csT, "p1")) == 4 and any("is back" in x for x in said(PR1)),
            "LT4: THE GUARD: the original turns up while the exact copy is current -> the original is the pickaxe again and the copy is removed "
            "(one Iron pickaxe left, uid %s): %s" % (A[3], ([(x[0], x[1], x[3], x[5]) for x in nowP], regfile("p1").get("pickaxe.uid"), ids(csT).get("Tool_Pickaxe_Iron"), said(PR1)[-2:])))

    # ---- LT5: the copy was reforged AFTER copying -> it stays, the original is RETIRED (never two working tools, nothing thrown away)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    apply(lifelong__reclaimSec="0")
    r6 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    cp6 = pick_now(csT)[0]
    d6 = doc(cp6[6]).clone()
    d6.put("rfN", BI32(JInt(int(Data.num(d6, "rfN", 0)) + 1)))
    csT[cp6[0]].setItemStackForSlot(JShort(cp6[1]), Data.put(stack("Tool_Pickaxe_Iron"), d6, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    csT["storage"].setItemStackForSlot(JShort(34), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    PR1.said = None
    LL.TOLD.clear()
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    w6 = pick_now(csT)
    o34 = csT["storage"].getItemStack(JShort(34))
    K.check(r6.startswith("+") and bool(LL.invested("Tool_Pickaxe_Iron", d6)) and len(w6) == 1 and w6[0][3] == cp6[3] and o34 is not None
            and bool(LL.isRt(doc(o34))) and ids(csT).get("Tool_Pickaxe_Iron", 0) == 2 and hit(o34, "Rock_Stone")[0] and not hit(w6[0][6], "Rock_Stone")[0],
            "LT5: the exact copy REFORGED after copying (rfN > lrpF) is invested: when the original turns up the copy stays THE pickaxe and the "
            "original is RETIRED (kept, breaks nothing) - two items, one working tool")
    # fix round (safety critic 1): the retired original can NOT be swapped back with /lifelong (a free undo of the paid reforge)
    saidS = said(PR1)
    h0 = csT["hotbar"].getItemStack(JShort(0))
    csT["hotbar"].setItemStackForSlot(JShort(0), o34)
    csT["storage"].removeItemStackFromSlot(JShort(34))
    rFam = str(Life.repick(PR1, plT))
    w6b = pick_now(csT)
    hb0 = csT["hotbar"].getItemStack(JShort(0))
    K.check(rFam.startswith("-That pickaxe and your lifelong one are exact copies of each other") and len(w6b) == 1 and w6b[0][3] == cp6[3]
            and regfile("p1").get("pickaxe.uid") == cp6[3] and hb0 is not None and bool(LL.isRt(doc(hb0)))
            and any("is an exact copy of it, so the old one stays retired" in x for x in saidS),
            "LT5 FIX (safety 1): /lifelong on the retired ORIGINAL of an invested exact copy is refused - the copy stays THE pickaxe, the "
            "original stays retired; the turn-up message no longer offers the swap: %s | %s" % (rFam, saidS[-1:]))
    csT["storage"].setItemStackForSlot(JShort(34), hb0)
    if h0 is None:
        csT["hotbar"].removeItemStackFromSlot(JShort(0))
    else:
        csT["hotbar"].setItemStackForSlot(JShort(0), h0)
    apply()

    # ---- LT6: out of reach in other ways: another world, the tool moved on, a closed Vault (window place)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    Life.TEST_WKEY = "otherworld~bbbb"
    r7 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r7.startswith("+Your pickaxe cannot be reached (it is in a chest at 10 64 -5 in world1 - only a chest in the world you are in can send it)")
            and slot_of(chestC, A[3]) >= 0 and len(pick_now(csT)) == 1,
            "LT6: the tracked chest is in ANOTHER world -> it is left alone, an exact copy instead (the guard sorts it out later): %s" % r7)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    elsewhere = SIC(JShort(27))
    elsewhere.setItemStackForSlot(JShort(0), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))          # someone moved it on
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    r8 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r8.startswith("+Your pickaxe cannot be reached (it is no longer in the chest at 10 64 -5)") and len(pick_now(csT)) == 1,
            "LT6: the tool is no longer in the tracked chest -> an exact copy: %s" % r8)
    invT, csT, refT, stT, plT = setup_lt()
    vC = SIC(JShort(54))
    A, _nq = tracked_into(plT, csT, refT, stT, vC, CWc_(vC))
    new_wm(plT)
    r9 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r9.startswith("+Your pickaxe cannot be reached (it is in a storage that cannot be opened from here)") and len(pick_now(csT)) == 1
            and slot_of(vC, A[3]) >= 0,
            "LT6: put into a storage window that is closed now (the Vault's kind) -> an exact copy; the original stays where it is: %s" % r9)

    # ---- LT7: Requip (wardrobe:fn:fetch): ok / refused / ok but missing / busy
    invT, csT, refT, stT, plT = setup_lt()
    A = pick_now(csT)[0]
    FETCH["cs"] = csT
    FETCH["store"] = {"e7": A[6]}
    RQ["items"] = [("e7", str(A[6].getItemId()), A[6].getMetadata())]
    csT[A[0]].removeItemStackFromSlot(JShort(A[1]))
    br.put("wardrobe:fn:fetch", RqFetch())
    FETCH["mode"] = "refuse"
    rq1 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    n_rq1 = len(pick_now(csT))
    FETCH["mode"] = "lie"
    rq2 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    br.put("profile:busy:" + str(U1), JBoolean(True))
    c0 = FETCH["calls"]
    rq3 = str(Life.fromRequip(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], "e7"))
    br.remove("profile:busy:" + str(U1))
    c1 = FETCH["calls"]
    FETCH["mode"] = "ok"
    n14 = int(Life.N[14])
    rq4 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(rq1.startswith("-Your lifelong pickaxe is in your Requip, but it could not come out: Inventory full") and n_rq1 == 0
            and rq2.startswith("-Requip let your pickaxe out, but it is not in your inventory") and rq3.startswith("-Your profile is changing") and c1 == c0
            and rq4.startswith("+Your %s came out of your Requip into your " % Gear.itemName("Tool_Pickaxe_Iron")) and pick_now(csT)[0][3] == A[3]
            and int(Life.N[14]) == n14 + 1 and not RQ.get("items"),
            "LT7: REQUIP: refused -> said, nothing copied; 'ok' but not in the inventory -> said (no copy, no dupe); profile busy -> Requip is not "
            "even asked; ok -> the SAME pickaxe is out of Requip: %s | %s | %s" % (rq1, rq2, rq4))
    br.remove("wardrobe:fn:fetch")
    RQ.clear()

    # ---- LT8: a FULL inventory is refused before anything moves (the tool stays in the open chest, nothing dropped)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    fillT = []
    for sec in ("storage", "backpack", "hotbar"):
        for i_ in range(int(csT[sec].getCapacity())):
            if csT[sec].getItemStack(JShort(i_)) is None:
                csT[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone", 7))
                fillT.append((sec, i_))
    r10 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r10.startswith("-No room - free one inventory slot") and slot_of(chestC, A[3]) >= 0 and not pick_now(csT),
            "LT8: inventory full -> refused first, the pickaxe stays in the chest (never dropped): %s" % r10)
    for sec, i_ in fillT:
        csT[sec].removeItemStackFromSlot(JShort(i_))

    # ---- LT9: a chest ANOTHER player has open
    # (a) p1 fetches while p2 looks in: it moves, p2's REAL window is marked changed by the engine's own container event (re-sent)
    invB, csB = mkinv()
    refB, stB, chB, plB = world(invB, csB, PR2)
    cbwB = chest_win(chestC)
    new_wm(plB, cbwB)
    wdirty_(cbwB)
    new_wm(plT, cbw)
    r11 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r11.startswith("+Your ") and slot_of(chestC, A[3]) < 0 and len(pick_now(csT)) == 1 and wdirty_(cbwB),
            "LT9: p1 fetches the pickaxe from a chest p2 has open: it moves once, and p2's window is marked changed by the engine's own "
            "container change event (p2's client is re-sent the chest - the tool is gone there): %s" % r11)
    # (b) p2 took it first: p1 gets an exact copy; p2's original does NOTHING for p2; back with p1 -> the copy goes
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    csB["storage"].setItemStackForSlot(JShort(4), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    apply(lifelong__reclaimSec="0")
    r12 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    PKEY[str(U2)] = "p2"
    skills(U2, Mining=20)
    LL.LAST.clear()
    Life.sweep0(PR2, invB, True)
    heldB = csB["storage"].getItemStack(JShort(4))
    hB = int(LL.hit(PR2, heldB, BL["Rock_Stone"])) if heldB is not None else -9
    csT["storage"].setItemStackForSlot(JShort(35), heldB)
    csB["storage"].removeItemStackFromSlot(JShort(4))
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    K.check(r12.startswith("+Your pickaxe cannot be reached (it is no longer in the chest at 10 64 -5)") and heldB is not None and hB == 2
            and len(pick_now(csT)) == 1 and pick_now(csT)[0][3] == A[3] and ids(csT).get("Tool_Pickaxe_Iron", 0) == 1,
            "LT9: p2 took p1's pickaxe out of the chest first: p1 gets an exact copy; the original does NOTHING for p2 (hit refused); once it is "
            "back with p1 it is the pickaxe again and the copy is removed: %s" % r12)
    apply()

    # ---- LT10: a profile switch mid-summon: busy / another profile key -> nothing moves
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    sA = slot_of(chestC, A[3])
    br.put("profile:busy:" + str(U1), JBoolean(True))
    m1 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], chestC, JInt(sA), "the chest", JInt(16)))
    br.remove("profile:busy:" + str(U1))
    PKEY[str(U1)] = "p9"
    m2 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], chestC, JInt(sA), "the chest", JInt(16)))
    t2 = str(Life.track(PR1, plT, None))
    PKEY[str(U1)] = "p1"
    K.check(m1.startswith("-Your profile is changing") and m2.startswith("-Your profile is changing") and slot_of(chestC, A[3]) == sA and not pick_now(csT),
            "LT10: a profile switch mid-summon (profile:busy, or the active profile key is another one) -> refused, the pickaxe stays in the chest")

    # ---- LT11: the move's own failure paths: the source refuses / removes-then-throws, the target refuses (back in the source), both refuse
    MFc = JClass(FAKE_PKG + ".MergeFail")
    srcF = MFc(JShort(27))
    srcF.setItemStackForSlot(JShort(2), chestC.getItemStack(JShort(sA)))
    chestC.removeItemStackFromSlot(JShort(sA))
    srcF.rm = 1
    m3 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    srcF.rm = 2
    m4 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    ok4 = len(pick_now(csT)) == 1 and slot_of(srcF, A[3]) < 0
    p4 = pick_now(csT)[0]
    srcF.rm = 0
    srcF.setItemStackForSlot(JShort(2), p4[6])
    csT[p4[0]].removeItemStackFromSlot(JShort(p4[1]))
    invF2, csF2 = mkinv(fail=("storage", "backpack", "hotbar"))
    for sec in ("storage", "backpack", "hotbar"):
        csF2[sec].refuseId = "Tool_Pickaxe_Iron"
    m5 = str(Life.move(PR1, invF2, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    back5 = slot_of(srcF, A[3]) == 2
    srcF.refuseId = "Tool_Pickaxe_Iron"
    logs()
    m6 = str(Life.move(PR1, invF2, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    lg6 = logs()
    srcF.refuseId = None
    K.check(m3.startswith("-Your pickaxe could not be taken out of the chest - nothing moved") and m4.startswith("+") and ok4
            and m5.startswith("-Your pickaxe could not be put into your inventory - it stayed in the chest") and back5
            and m6.startswith("-Moving your pickaxe went wrong") and any("LL-SUMMON-LOST " in l and " undo: " in l for l in lg6),
            "LT11: the source refuses -> nothing moved; removes-then-throws -> still delivered; the inventory refuses -> put back in the source "
            "slot; BOTH refuse -> LL-SUMMON-LOST with the undo data (WARN) and the registry still names it: %s | %s | %s | %s" % (m3, m4, m5, m6))
    # ... and that 'lost' tool is never lost for good: /pickaxe makes its exact copy
    apply(lifelong__reclaimSec="0")
    r13 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r13.startswith("+Your pickaxe cannot be reached") and "exact copy" in r13 and len(pick_now(csT)) == 1
            and str(Data.str(doc(pick_now(csT)[0][6]), "r", "")) == "legendary",
            "LT11: ... the next /pickaxe makes the exact (Legendary) copy: %s" % r13)
    apply()

    # ---- LT12: A CRASH AT EVERY SUMMON STEP, then a restart with the engine having saved: neither / the source / the target / both
    def crash_case(step, saved_src, saved_dst):
        inv_, cs_, ref_, st_, pl_ = setup_lt()
        ch_ = SIC(JShort(27))
        cw_ = chest_win(ch_)
        a_, _n = tracked_into(pl_, cs_, ref_, st_, ch_, cw_)
        s0 = slot_of(ch_, a_[3])
        it0 = ch_.getItemStack(JShort(s0))
        inv_before = snapshot(cs_)
        new_wm(pl_, cw_)
        Life.CRASH_AT = step
        crashed = False
        try:
            Life.reclaimW(PR1, pl_, JInt(0), None)
        except Exception as ex_:
            crashed = ("lifelong step %d" % step) in str(ex_)
        Life.CRASH_AT = 0
        # the restart: what the engine had saved
        if not saved_src and slot_of(ch_, a_[3]) < 0:
            ch_.setItemStackForSlot(JShort(s0), it0)
        if not saved_dst:
            restore_inv(cs_, inv_before)
        reset_reg()
        new_wm(pl_)
        Life.TEST_CHESTS = JClass("java.util.HashMap")()
        Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", ch_)
        apply(lifelong__reclaimSec="0")
        LL.LAST.clear()
        Life.sweep0(PR1, inv_, True)
        if not pick_now(cs_):
            Life.reclaimW(PR1, pl_, JInt(0), None)
        # a second stack with the same uid left in the chest (the inventory was saved, the chest was not): it comes into the inventory
        dup = slot_of(ch_, a_[3])
        if dup >= 0 and pick_now(cs_):
            cs_["storage"].setItemStackForSlot(JShort(31), ch_.getItemStack(JShort(dup)))
            ch_.removeItemStackFromSlot(JShort(dup))
            for _i in range(2):
                LL.LAST.clear()
                Life.sweep0(PR1, inv_, True)
        apply()
        work = pick_now(cs_)
        regu = regfile("p1").get("pickaxe.uid")
        others = [ch_.getItemStack(JShort(i_)) for i_ in range(27) if ch_.getItemStack(JShort(i_)) is not None]
        working_elsewhere = [o_ for o_ in others if not hit(o_, "Rock_Stone")[0]]
        ok = (crashed and len(work) == 1 and work[0][3] == regu and not hit(work[0][6], "Rock_Stone")[0] and not working_elsewhere
              and str(Data.str(doc(work[0][6]), "r", "")) == "legendary" and ids(cs_).get("Tool_Pickaxe_Iron", 0) == 1)
        return ok, (crashed, [(x[0], x[1], x[3], x[5]) for x in work], regu, len(others), dup)
    for step in (7, 8):
        for ss, sd in ((False, False), (True, False), (False, True), (True, True)):
            okc, why = crash_case(step, ss, sd)
            K.check(okc, "LT12: a CRASH at summon step %d (engine saved: chest %s, inventory %s) then a restart (+ /pickaxe if needed): exactly ONE "
                    "working Legendary pickaxe, the registry names it, nothing else works: %s" % (step, "yes" if ss else "no", "yes" if sd else "no", why))
    # step 9: Requip said ok (the tool is out) and the server died before the bookkeeping: the next look is normal
    inv9, cs9, ref9, st9, pl9 = setup_lt()
    A9 = pick_now(cs9)[0]
    FETCH["cs"] = cs9
    FETCH["store"] = {"e9": A9[6]}
    FETCH["mode"] = "ok"
    RQ["items"] = [("e9", str(A9[6].getItemId()), A9[6].getMetadata())]
    cs9[A9[0]].removeItemStackFromSlot(JShort(A9[1]))
    br.put("wardrobe:fn:fetch", RqFetch())
    Life.CRASH_AT = 9
    cr9 = False
    try:
        Life.reclaimW(PR1, pl9, JInt(0), None)
    except Exception as ex_:
        cr9 = "lifelong step 9" in str(ex_)
    Life.CRASH_AT = 0
    reset_reg()
    LL.LAST.clear()
    Life.sweep0(PR1, inv9, True)
    br.remove("wardrobe:fn:fetch")
    RQ.clear()
    K.check(cr9 and len(pick_now(cs9)) == 1 and pick_now(cs9)[0][3] == A9[3] and regfile("p1").get("pickaxe.uid") == A9[3],
            "LT12: a CRASH right after Requip let the pickaxe out: after the restart it is simply the pickaxe (same uid), nothing to repair")

    # ---- LT13: the legacy answer: a tool lost before 0.3.2 (no snapshot) = a Common tool of the tier it had
    invL, csL, refL, stL, plL = setup_lt()
    AL = pick_now(csL)[0]
    csL[AL[0]].removeItemStackFromSlot(JShort(AL[1]))
    PL = LL.reg("p1")
    for k_ in ("pickaxe.snap", "pickaxe.snapId", "pickaxe.snapU"):
        PL.remove(k_)
    LL.save("p1", PL)
    rL = str(Life.reclaimW(PR1, plL, JInt(0), None))
    gL = pick_now(csL)
    K.check(rL.startswith("+Here is a new Common %s" % Gear.itemName("Tool_Pickaxe_Iron")) and "before exact copies existed" in rL and len(gL) == 1
            and str(Data.str(doc(gL[0][6]), "r", "")) == "normal" and str(gL[0][6].getItemId()) == "Tool_Pickaxe_Iron",
            "LT13: no snapshot (lost before 0.3.2, never seen since) -> the 0.3.1 answer, a Common tool of the tier it had: %s" % rL)
    # a snapshot of ANOTHER uid is never used (snapU must be the current uid)
    PL.setProperty("pickaxe.snap", B64.getEncoder().encodeToString(JStr("{\"r\": \"legendary\"}").getBytes("UTF-8")))
    PL.setProperty("pickaxe.snapU", "0000000000000000")
    K.check(Life.snapDoc(PL, "pickaxe", gL[0][3]) is None and Life.snapDoc(PL, "pickaxe", "0000000000000000") is not None,
            "LT13: snapDoc only answers for the CURRENT uid")

    # ---- LT14: the texts, rows, counters, statusText
    lgE = logs()
    K.check("fetch yours from Requip / an open window / the Vault / its loaded chest, else an exact copy every" in str(LL.statusText())
            and "fetched from Requip" in str(Life.counters()) and "exact copies" in str(Life.counters()),
            "LT14: statusText + counters name the new paths: %s" % str(Life.counters())[-120:])
    _bs = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    K.check('w = "Not on you - /" + K + " brings it back";' in _bs and "(or an exact copy)\";" not in _bs
            and "the Void or your Vault?" not in _bs and "Is a better tool in a chest or your Vault?" in _bs,
            "LT14 FIX (fidelity 2 + 4): the Tools tab line is 'Not on you - /pickaxe brings it back' (36 chars, fits the 340 px column); the "
            "migration notice no longer names the Void")
    Life.TEST_CHESTS = None
    Life.TEST_WKEY = None
    LL.HERE.clear()
    LL.TRACKQ.clear()
    PKEY[str(U1)] = "p1"
    wipe_home()

    # ============================================================================ L8: /lifelong (re-pick)
    wipe_home()
    invR, csR = mkinv()
    refR2, stR2, chR2, plR2 = world(invR, csR, PR1)
    csR["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Iron"), Roll.newDoc("Tool_Pickaxe_Iron", JInt(1), True, "craft", JInt(16)), None))
    Life.sweep0(PR1, invR, True)
    first = [x for x in lls(csR, "p1") if x[2] == 0][0]
    better = Data.put(stack("Tool_Pickaxe_Cobalt"), Roll.newDoc("Tool_Pickaxe_Cobalt", JInt(3), True, "craft", JInt(25)), None)
    csR["hotbar"].setItemStackForSlot(JShort(0), better)
    K.check(int(invR.getActiveHotbarSlot()) == 0 and not bool(invR.usingToolsItem()), "L8: a new inventory holds hotbar slot 0")
    r_rp = str(Life.repick(PR1, plR2))
    LR = [x for x in lls(csR, "p1") if x[2] == 0]
    old_ = csR[first[0]].getItemStack(JShort(first[1]))
    r_rp2 = str(Life.repick(PR1, plR2))
    csR["hotbar"].setItemStackForSlot(JShort(0), stack("Tool_Shovel_Iron"))
    r_sh = str(Life.repick(PR1, plR2))
    csR["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Hatchet_Iron"), Roll.newDoc("Tool_Hatchet_Iron", JInt(1), True, "craft", JInt(16)), None))
    LL.reg("p1").setProperty("migratedAt", "1")
    r_late = str(Life.repick(PR1, plR2))
    K.check(r_rp.startswith("+%s is your lifelong pickaxe now" % Gear.itemName("Tool_Pickaxe_Cobalt")) and len(LR) == 1 and str(LR[0][6].getItemId()) == "Tool_Pickaxe_Cobalt"
            and str(Data.str(doc(LR[0][6]), "r", "")) == "legendary" and not bool(LL.isLL(doc(old_))) and r_rp2.startswith("-That already is your lifelong pickaxe")
            and r_sh.startswith("-Only a pickaxe, hatchet, hoe, sickle or fishing rod") and r_late.startswith("-Re-picking was open for 7 days"),
            "L8: /lifelong: the Legendary Cobalt pickaxe in hand becomes the lifelong one, the old one turns plain; again / a shovel / too late refused: %s | %s"
            % (r_rp, r_late))
    LL.reg("p1").setProperty("migratedAt", str(int(__import__("time").time() * 1000)))
    csR["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Pickaxe_Thorium"), Roll.newDoc("Tool_Pickaxe_Thorium", JInt(0), True, "craft", JInt(20)), None))
    r_twice = str(Life.repick(PR1, plR2))
    K.check(r_twice.startswith("-You already re-picked your lifelong pickaxe"), "L8: once per kind: %s" % r_twice)

    # ============================================================================ L9: protection (drop, salvage, market, merge, level up) + no crafting
    wipe_home()
    invD, csD = mkinv()
    refD, stD, chD, plD = world(invD, csD, PR1)
    Life.sweep0(PR1, invD, True)
    LD = dict((x[2], x) for x in lls(csD, "p1"))
    DIRQ = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    Drop = JClass(PKG + "GearLLDropSys")()
    SECID = {"hotbar": -1, "storage": -2, "armor": -3, "utility": -5, "tools": -8, "backpack": -9}
    sec0, slot0 = LD[0][0], LD[0][1]
    e1 = DIRQ(JInt(SECID[sec0]), JShort(slot0))
    n4 = int(LL.N[4])
    Drop.handle(JInt(0), chD, stD, None, e1)
    csD["storage"].setItemStackForSlot(JShort(35), stack("Rock_Stone", 5))
    e2 = DIRQ(JInt(-2), JShort(35))
    Drop.handle(JInt(0), chD, stD, None, e2)
    apply(lifelong__noDrop="false")
    e3 = DIRQ(JInt(SECID[sec0]), JShort(slot0))
    Drop.handle(JInt(0), chD, stD, None, e3)
    apply()
    K.check(bool(e1.isCancelled()) and not bool(e2.isCancelled()) and not bool(e3.isCancelled()) and int(LL.N[4]) == n4 + 1
            and csD[sec0].getItemStack(JShort(slot0)) is not None,
            "L9: THE REAL GearLLDropSys on DropItemEvent$PlayerRequest (InventoryUtils.getSectionById resolves the section): the Drop key on the lifelong "
            "pickaxe is cancelled (it stays), on stone it is not; lifelong.noDrop off lets it go")
    # SALVAGE: the engine's own matching (ProcessingBenchBlock.updateRecipe -> testRemoveMaterialFromSlot -> isEquivalentType)
    IUM = JClass("com.hypixel.hytale.server.core.inventory.container.InternalContainerUtilMaterial")
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    salv = None
    for rc in CRR.getAssetMap().getAssetMap().values():
        try:
            inp = rc.getInput()
            if inp is not None and len(inp) == 1 and str(inp[0].getItemId()) == str(LD[0][6].getItemId()):
                salv = rc
                break
        except Exception:
            pass
    sc = SIC(JShort(3))
    sc.setItemStackForSlot(JShort(0), LD[0][6])
    sc.setItemStackForSlot(JShort(1), stack(str(LD[0][6].getItemId())))
    sc.setItemStackForSlot(JShort(2), stack("Rock_Stone"))
    mq = salv.getInput()[0] if salv is not None else MQc(str(LD[0][6].getItemId()), None, None, JInt(1), None)
    t_ll = int(IUM.testRemoveMaterialFromSlot(sc, JShort(0), mq, JInt(1), False))
    t_pl = int(IUM.testRemoveMaterialFromSlot(sc, JShort(1), mq, JInt(1), False))
    t_no = int(IUM.testRemoveMaterialFromSlot(sc, JShort(2), mq, JInt(1), False))
    K.check(t_ll == t_no and t_pl != t_no, "L9: SALVAGE: the engine's recipe matching (%s) treats the lifelong %s like a stone (no match: %d = %d) and "
            "matches a plain one (%d)" % ("the real salvage recipe " + str(salv.getId()) if salv is not None else "a recipe input", LD[0][6].getItemId(), t_ll, t_no, t_pl))
    K.check(Wall.why(LD[0][6].getItemId(), LD[0][6].getMetadata()) is not None and "never go on the market" in str(Wall.why(LD[0][6].getItemId(), LD[0][6].getMetadata()))
            and Wall.why("Tool_Pickaxe_Crude", Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(0), True, "craft", JInt(1)), None).getMetadata()) is None,
            "L9: the market wall refuses a lifelong tool (Auction House / Bazaar), not a plain one")
    K.check("cannot be merged" in str(Merge.why(LD[0][6], JInt(1))), "L9: the multitool merge refuses a lifelong pickaxe: %s" % Merge.why(LD[0][6], JInt(1)))
    li = Forge.lvlInfo(U1, LD[0][6].getItemId(), doc(LD[0][6]))
    K.check(int(li[0]) == 8 and "follows your skill level" in str(li[5]), "L9: Reforge Level up refuses a lifelong tool (code 8): %s" % li[5])
    # NO CRAFTING: the REAL GearCraftPreSys on a REAL CraftRecipeEvent$Pre
    PreE = JClass("com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre")
    Pre = JClass(PKG + "GearCraftPreSys")()

    def recipe_of(out_id):
        for rc in CRR.getAssetMap().getAssetMap().values():
            try:
                po = rc.getPrimaryOutput()
                if po is not None and str(po.getItemId()) == out_id and int(po.getQuantity()) == 1:
                    return rc
            except Exception:
                pass
        return None
    rcP = recipe_of("Tool_Pickaxe_Copper")
    rcS = None
    for _sid in ("Tool_Shovel_Copper", "Tool_Shovel_Crude", "Tool_Shovel_Iron", "Tool_Shovel_Thorium", "Tool_Shovel_Cobalt"):
        rcS = rcS or recipe_of(_sid)
    chC = us.allocateInstance(FCh.class_)
    chC.comps = IHM()
    chC.ref = refD
    PR1.said = None
    ep = PreE(rcP, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, ep)
    es = PreE(rcS, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, es)
    ec = PreE(rcP, JInt(1))
    try:
        gmf = jf(PLA, "gameMode")
        gmf.set(plD, JClass("com.hypixel.hytale.protocol.GameMode").Creative)
        Pre.handle(JInt(0), chC, stD, None, ec)
        gmf.set(plD, None)
    except KeyError:
        K.notes.append("L9: Player has no gameMode field - the Creative case is not run")
    apply(lifelong__noCraft="false")
    eo = PreE(rcP, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, eo)
    apply()
    K.check(rcP is not None and rcS is not None and bool(ep.isCancelled()) and not bool(es.isCancelled()) and not bool(ec.isCancelled()) and not bool(eo.isCancelled())
            and any("Tools are not crafted any more" in x for x in said(PR1)),
            "L9: NO CRAFTING: the real Copper pickaxe recipe (%s) is refused at the bench / /craft with a chat line; a shovel crafts; Creative crafts; "
            "lifelong.noCraft off crafts: %s" % (None if rcP is None else rcP.getId(), [rcS is not None and rcS.getId(), bool(ep.isCancelled()), bool(es.isCancelled()),
                                                     bool(ec.isCancelled()), bool(eo.isCancelled()), said(PR1)[-1:]]))
    K.check(not bool(Smith.usable(rcP)) and bool(Smith.usable(rcS)) == bool(Smith.usable(rcS)) and bool(LL.noCraft("Tool_Hoe_Iron"))
            and not bool(LL.noCraft("Tool_Shovel_Iron")), "L9: the Smithing Craft tab hides pickaxe recipes (shovels unchanged)")

    # ============================================================================ L10: the tier-up on the Anvil (GearUp)
    wipe_home()
    invU, csU = mkinv()
    refU, stU, chU, plU = world(invU, csU, PR1)
    skills(Mining=4, Foraging=4, Farming=4)
    Life.sweep0(PR1, invU, True)
    LU = dict((x[2], x) for x in lls(csU, "p1"))
    secU, slotU = LU[0][0], LU[0][1]
    plain = Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(1), True, "craft", JInt(3)), None)
    cU = Up.check(plain, U1)
    cL = Up.check(csU[secU].getItemStack(JShort(slotU)), U1)
    K.check(str(cU[0]).startswith("Only your lifelong pickaxe can be tiered up") and str(cL[0]).startswith("You need Mining %d to tier up to %s"
            % (int(Lvl.band("Tool_Pickaxe_Copper")[0]), str(LL.an(Gear.itemName("Tool_Pickaxe_Copper"))))), "L10: a plain Crude pickaxe cannot climb; yours needs the Copper band start: %s | %s" % (cU[0], cL[0]))
    skills(Mining=int(Lvl.band("Tool_Pickaxe_Copper")[0]) + 3)
    cL2 = Up.check(csU[secU].getItemStack(JShort(slotU)), U1)
    K.check(cL2[0] is None and str(cL2[1]) == "Tool_Pickaxe_Copper" and list(cL2[2][0]) == ["Ingredient_Bar_Copper"] and list(cL2[2][1]) == [25],
            "L10: with the level: Copper for 25 Copper Ingots (Skyy's G1)")
    csU["storage"].setItemStackForSlot(JShort(30), stack("Ingredient_Bar_Copper", 30))
    before_u = str(LU[0][3])
    res = Up.upgrade(invU, JInt({"hotbar": 0, "storage": 1, "backpack": 2, "armor": 3, "utility": 4, "tools": 5}[secU]), JInt(slotU),
                     "Tool_Pickaxe_Crude", Forge.fp(csU[secU].getItemStack(JShort(slotU))), U1, "Tester")
    nu = csU[secU].getItemStack(JShort(slotU))
    K.check(int(res[0]) == 1 and str(nu.getItemId()) == "Tool_Pickaxe_Copper" and str(LL.uid(doc(nu))) == before_u and bool(LL.isLL(doc(nu)))
            and int(Data.num(doc(nu), "lvl", -1)) == int(LL.levelFor(U1, "Tool_Pickaxe_Copper")) and ids(csU).get("Ingredient_Bar_Copper") == 5,
            "L10: THE TIER-UP (GearUp.upgrade): the lifelong Crude pickaxe becomes a Copper one - same uid, still lifelong, at your level; 25 ingots taken")
    LL.LAST.clear()
    Life.sweep0(PR1, invU, True)
    K.check(regfile("p1").get("pickaxe.id") == "Tool_Pickaxe_Copper", "L10: the next sweep records the new tier (what /pickaxe would give back)")
    pvI = Up.preview(nu, U1)
    K.check(str(pvI[0]).startswith("You need Mining") or str(pvI[0]).startswith("You need 1 more") or pvI[0] is None,
            "L10: the next step (Iron) asks for the Iron band level / 1 Enchanted Iron Ingot: %s" % pvI[0])

    # ============================================================================ L11: the Tools page + the commands + the bridge + the tooltip
    wipe_home()
    invT, csT = mkinv()
    refT, stT, chT, plT = world(invT, csT, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    Life.sweep0(PR1, invT, True)
    FLP = JClass(FAKE_PKG + ".FakeLifePage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def evtext(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            for f_ in ("selector", "data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        out_.append(str(v_))
                except Exception:
                    pass
        return chr(10).join(out_)

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(refT, ub_, ue_, stT)
        cl = cmds(ub_)
        return chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl) + chr(10) + evtext(ue_), cl
    pg = FLP(PR1)
    txt, cl = render(pg)
    idsx = re.findall(r"#([A-Za-z0-9_]+)\s*\{", chr(10).join("%s" % (v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")) for v in cl))
    K.check(idsx and not [i for i in idsx if "_" in i] and len(idsx) == len(set(idsx)) and "Your lifelong tools" in txt and "Upgrade Points" in txt
            and "#SkyyGTab4" in txt and "Tools" in txt and "ItemGridSlot" not in txt and txt.count("#SkyyGLRow") >= 4,
            "L11: the Tools page renders: unique ids without underscores, the Tools tab, four tool rows, the points panel, no ItemGridSlot: %s"
            % (([i for i in idsx if "_" in i], [i for i in idsx if idsx.count(i) > 1][:5], "Your lifelong tools" in txt, "Upgrade Points" in txt,
               "#SkyyGTab4" in txt, txt.count("#SkyyGLRow")),))
    hs_ = {}
    for v in cl:
        dat = v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")
        m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
        if m_ and v["selector"]:
            h_ = re.search(r"Height: (\d+)", m_.group(1))
            hs_[v["selector"]] = hs_.get(v["selector"], 0) + (int(h_.group(1)) if h_ else 0)
    K.check(hs_.get("#SkyyGBody", 0) <= 808 and hs_.get("#SkyyGList", 0) <= 656 and hs_.get("#SkyyGPanel", 0) <= 656,
            "L11: the height budget (body %d <= 808, list %d <= 656, panel %d <= 656)" % (hs_.get("#SkyyGBody", 0), hs_.get("#SkyyGList", 0), hs_.get("#SkyyGPanel", 0)))
    COINS[0] = 10 ** 7
    pg.handleDataEvent(refT, stT, '{"a":"sel:1"}')
    K.check(int(pg.sel) == 1, "L11: click a tool row -> its points")
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"buy:0"}')
    info1 = str(pg.info)
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"reset"}')
    info2 = str(pg.info)
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"reset"}')
    info3 = str(pg.info)
    K.check(info1.startswith("+Speed is level 1 now") and info2.startswith("=Click Reset again within 8 s to pay 5,000 coins") and info3.startswith("+All 1 points of your hatchet are back"),
            "L11: buy Speed for the hatchet, Reset asks first, the 2nd click pays: %s | %s | %s" % (info1, info2, info3))
    pg.handleDataEvent(refT, stT, '{"a":"buy:0"}')
    K.check(str(pg.info) == info3, "L11: a click within 400 ms is dropped")
    pg.handleDataEvent(refT, stT, '{"a":"mode:4"}')
    pg.handleDataEvent(refT, stT, '{"a":"refresh"}')
    br.put("profile:epoch:" + str(U1), "e2")
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"buy:1"}')
    K.check(str(pg.info).startswith("-Your profile changed"), "L11: a profile switch since the page opened refuses the click")
    br.remove("profile:epoch:" + str(U1))
    pg.handleDataEvent(refT, stT, '{"a":"back"}')
    K.check(int(pg.closes) == 1 and int(pg.rebuilds) >= 5, "L11: Back closes (no SkyyMenu), the clicks rebuild")
    K.check(bool(LL.tabGo('{"a":"mode:4"}', PR1)) and not bool(LL.tabGo('{"a":"mode:3"}', PR1)), "L11: the Tools tab click on the other pages is caught (mode:4 only)")

    def run_cmd(cls, ref_, st_, pr_):
        cmd = P(cls)()
        exe = [m_ for m_ in P(cls).class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
        exe.setAccessible(True)
        FPM.last = None
        exe.invoke(cmd, None, st_, ref_, pr_, None)
        return FPM.last
    PR1.said = None
    lp = run_cmd("ToolPtsCmd", refT, stT, PR1)
    K.check(lp is not None and str(lp.getClass().getName()).endswith("LifePage"), "L11: /toolpoints opens the Tools page")
    run_cmd("PickaxeCmd", refT, stT, PR1)
    run_cmd("LifelongCmd", refT, stT, PR1)
    sd = said(PR1)
    K.check(any("You still have your lifelong pickaxe" in x for x in sd) and any("Hold the tool you want" in x or "Only a pickaxe" in x for x in sd),
            "L11: /pickaxe and /lifelong run and answer in chat: %s" % sd[-2:])
    # every replacement command runs (the tools are on the player: each says so) + the hooks the build gave a body (join / scan / prefetch / forget)
    PR1.said = None
    for cls in ("HatchetCmd", "HoeCmd", "SickleCmd"):
        run_cmd(cls, refT, stT, PR1)
    sd2 = said(PR1)
    K.check([("You still have your lifelong %s" % k_) in " ".join(sd2) for k_ in ("hatchet", "hoe", "sickle")] == [True, True, True],
            "L11: /hatchet, /hoe and /sickle run: %s" % sd2)
    LL.REG.clear()
    LL.prefetch(U1)
    K.check(LL.REG.containsKey("p1"), "L11: GearLL.prefetch (GearRefreshTask's scheduler hop) reads the registry into memory")
    nsw = int(Life.N[0])
    LL.joinHook(PR1, invT)
    LL.LAST.clear()
    LL.sweepHook(PR1, invT)
    K.check(int(Life.N[0]) == nsw + 2, "L11: joinHook / sweepHook (GearRefreshTask.run / GearStampTask.run) run the sweep (their bodies were set at build)")
    LL.SLOW.put(U1, JLong(1))
    LL.TOLD.put(str(U1) + ":x", JLong(1))
    LL.forget(U1)
    K.check(not LL.SLOW.containsKey(U1) and not LL.TOLD.containsKey(str(U1) + ":x") and not LL.LAST.containsKey(U1), "L11: GearLL.forget (GearBye) clears the player's clocks")
    cons = []
    for cls, nm_ in (("PickaxeCmd", "pickaxe"), ("HatchetCmd", "hatchet"), ("HoeCmd", "hoe"), ("SickleCmd", "sickle"), ("ToolPtsCmd", "toolpoints"), ("LifelongCmd", "lifelong")):
        c_ = P(cls)()
        cons.append((nm_, str(c_.getName())))
    K.check(all(a == b for a, b in cons), "L11: command names: %s" % cons)
    Fn0, Fn1, Fn2 = JClass(PKG + "GearLLFn")(JInt(0)), JClass(PKG + "GearLLFn")(JInt(1)), JClass(PKG + "GearLLFn")(JInt(2))
    uidp = str(LL.reg("p1").getProperty("pickaxe.uid"))
    K.check(str(Fn0.apply(JArray(JObject)([U1, JString("pickaxe")]))) == uidp and Fn0.apply(JArray(JObject)([U1, JString("shovel")])) is None
            and int(Fn1.apply(JArray(JObject)([U1, JString("hatchet"), JString("spd")]))) == 0
            and int(Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), JString("Tool_Hoe_Crude")]))) == 1          # 0.3.1: was 2
            and int(Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), stack("Tool_Hoe_Crude")]))) == 1          # 0.3.5: no item id = a hand = Crude (Carrot one up)
            and Fn0.apply(JString("bad")) is None, "L11 + FIX engine-6: gear:fn:lifelong / perk / farmTier answer (and never throw); farmTier takes the held item id (java.lang only - an "
                "ItemStack is no tool to it): %s" % [
                str(Fn0.apply(JArray(JObject)([U1, JString("pickaxe")]))), uidp, Fn0.apply(JArray(JObject)([U1, JString("shovel")])),
                Fn1.apply(JArray(JObject)([U1, JString("hatchet"), JString("spd")])), Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), JString("Tool_Hoe_Crude")]))])
    tipT = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    pT = [x for x in lls(csT, "p1") if x[2] == 0][0][6]
    Tool.lines(U1, pT.getItemId(), doc(pT), tipT[0], tipT[1])
    tl_txt = [str(x) for x in tipT[0]]
    K.check(any(x.startswith("Lifelong pickaxe: levels with Mining (max Lv") for x in tl_txt) and any("Upgrade Points free - /toolpoints" in x for x in tl_txt)
            and "Can't be dropped. Lost it? /pickaxe" in tl_txt and max(len(x) for x in tl_txt) <= 60,
            "L11: the tooltip: lifelong line, free points, can't be dropped (short lines): %s" % tl_txt[-4:])
    K.check("lifelong tools on" in str(LL.statusText()) and "gate refused" in str(LL.counters()) and "sweeps" in str(Life.counters()),
            "L11: status + counters: %s" % str(LL.statusText())[:160])

    # ============================================================================ G (0.3.1): THE NEW TIER GATE
    apply()
    skills(Mining=10, Foraging=10, Farming=10)
    st31 = str(LL.statusText())
    K.check("Crude counts as Copper, one tier up x0.4, two up x0.1, three up refused" in st31,
            "G: statusText names the new gate: %s" % st31[-160:])
    rws = dict((k, int(CRows.index(k))) for k in ("gate.nextFactor", "gate.twoUpFactor", "gate.crudeFactor"))
    K.check(all(v >= 0 for v in rws.values()) and bool(CRows.flag(rws["gate.twoUpFactor"], "danger")),
            "G: Server Setup rows: gate.nextFactor, the NEW gate.twoUpFactor (danger), gate.crudeFactor kept as a legacy row: %s" % rws)
    gsrcs = [b for b in sorted(str(k) for k in bmap.keySet()) if not b.startswith("*")]

    def first(pre, suf=""):
        for b_ in gsrcs:
            if b_.startswith(pre) and (not suf or suf in b_):
                return b_
        return None
    ORE, WOOD = {}, {}
    for w_, m_ in zip([str(x) for x in LL.ORE_W], [int(x) for x in LL.ORE_M]):
        b_ = first("Ore_" + w_ + "_")
        if b_ is not None and m_ not in ORE and list(LL.catOf(b_)) == [1, m_]:
            ORE[m_] = b_
    for w_, m_ in zip([str(x) for x in LL.WOOD_W], [int(x) for x in LL.WOOD_M]):
        b_ = first("Wood_" + w_ + "_", "_Trunk")
        if b_ is not None and m_ not in WOOD and list(LL.catOf(b_)) == [3, m_]:
            WOOD[m_] = b_
    K.notes.append("G: ore blocks by tier %s, logs by tier %s" % (ORE, WOOD))

    def hitb(s_, bid):
        Tool.LAST.clear()
        e_ = ev(s_, bmap.get(bid), 0.3)
        hs.handle(JInt(0), chH, stH, None, e_)
        return bool(e_.isCancelled()), float(e_.getDamage())

    def refb(s_, bid):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, s_, bmap.get(bid), JFloat(0.3)))
    FX = {0: 1.0, 1: 0.4, 2: 0.1}
    gbad, gseen, gn = [], set(), 0
    for tool_, te_ in (("Tool_Pickaxe_Crude", 1), ("Tool_Pickaxe_Copper", 1), ("Tool_Pickaxe_Iron", 2),
                       ("Tool_Hatchet_Crude", 1), ("Tool_Hatchet_Copper", 1), ("Tool_Hatchet_Iron", 2)):
        tab_ = ORE if "Pickaxe" in tool_ else WOOD
        for m_ in sorted(tab_):
            up = m_ - te_
            cx, dmg = hitb(stack(tool_), tab_[m_])
            ref = refb(stack(tool_), tab_[m_])
            if up >= 3:
                ok = cx
            else:
                ok = (not cx) and abs(dmg - float(JFloat(ref * FX[max(up, 0)]))) < 1e-6
            gn += 1
            gseen.add((tool_, min(max(up, 0), 3)))
            if not ok:
                gbad.append((tool_, tab_[m_], m_, up, cx, dmg, ref))
    need = set((t_, k_) for t_ in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Hatchet_Crude", "Tool_Hatchet_Copper")
               for k_ in (0, 1, 2, 3))
    K.check(not gbad and need <= gseen and gn >= 30,
            "G: THE 0.3.1 GATE MATRIX on the REAL hit system + real ore / log blocks (%d hits): Crude and Copper pickaxes / hatchets = tier 1 "
            "(T1 normal, T2 x0.4, T3 x0.1, T4+ refused), Iron one tier higher (T2 normal, T3 x0.4, T4 x0.1, T5+ refused); missing cases %s; bad %s"
            % (gn, sorted(need - gseen)[:4], gbad[:4]))
    dC = LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))
    dP = LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(4))
    dI = LL.decideC(stack("Tool_Pickaxe_Iron"), JInt(1), JInt(4))
    K.check(int(LL.fullT(dC)) == 3 and int(dC[5]) == 2 and int(LL.fullT(dP)) == 4 and int(dP[0]) == 2 and int(dP[5]) == 3
            and int(dI[0]) == 1 and int(dI[5]) == 2 and int(dP[3]) == 0,
            "G: decide's [5] = tiers above (Crude = T1), [3] the raw tier; fullT caps a hoe at Thorium (%s / %s / %s)" % (list(dC), list(dP), list(dI)))
    ftc = [int(LL.farmTier(c_, h_)) for c_, h_ in (("Plant_Crop_Wheat_Block", "Tool_Hoe_Crude"), ("Plant_Crop_Wheat_Block", "Tool_Sickle_Crude"),
                                                    ("Plant_Crop_Carrot_Block", "Tool_Sickle_Crude"), ("Plant_Crop_Potato_Block", "Tool_Hoe_Crude"),
                                                    ("Plant_Crop_Potato_Block", "Tool_Hoe_Copper"), ("Plant_Crop_Potato_Block", "Tool_Hoe_Iron"))]
    K.check(ftc == [0, 0, 1, 2, 2, 1],
            "G (0.3.3): farming: Crude hoe / sickle on Wheat (T1) normal; a Crude sickle on a Carrot one up = 1 (half XP, no Fortune); a Crude / "
            "Copper hoe on a Potato = two up (capped at Thorium) = 2 REFUSED (was 1); an Iron hoe on a Potato one up = 1: %s" % ftc)
    with zipfile.ZipFile(JAR) as zj_:
        llb = zj_.read("com/skyy/gear/GearLL.class")
    K.check(b"Slow going" in llb and b"x the hits. With " in llb and b"two tiers" in llb and b"one tier" in llb and b"It needs at least " in llb
            and b" for full speed). Tier yours up on the Anvil (/smithing)." in llb and b"Too tough for your " in llb
            and b"This is one tier above your " not in llb,
            "G: the popups: 'Slow going' names one / two tiers and the hits (2.5x / 10x), 'Too tough' names the lowest tier that breaks it + the "
            "full-speed tier")

    # ---- G: THE ONE-TIME UPDATE migrate031 (pure text)
    MK = str(Cfg.GQ_MARK)

    def gq(t_):
        r_ = Cfg.gqUpdate(JString(t_))
        if r_ is None:
            return None
        return [str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]]]
    tA = "# SkyyGear\r\nlevel.x=1\r\ngate.on=true\r\ngate.nextFactor=0.1\r\ngate.bareHands=true\r\n"
    rA = gq(tA)
    tB = "a=1\ngate.nextFactor = 0.1\nb=2"
    rB = gq(tB)
    tC = "a=1\r\ngate.nextFactor=0.25\r\ngate.crudeFactor=0.3\r\n"
    rC_ = gq(tC)
    tD = "a=1\nb=2\n"
    rD = gq(tD)
    tE = "a=1\n" + MK + "\ngate.nextFactor=0.1\n"
    rE = gq(tE)
    tF = "a=1\ngate.nextFactor=0.\\\n  1\n"
    rF = gq(tF)
    tG = "gate.nextFactor=0.10\na=1\\\n"
    rG = gq(tG)
    K.check(rA is not None and rA[0] == tA.replace("gate.nextFactor=0.1\r", "gate.nextFactor=0.4\r") + MK + "\r\n" and rA[1] == "gate.nextFactor 0.1 -> 0.4"
            and rA[3] == ["gate.nextFactor", "0.1", "0.4"] and rA[2] == [],
            "G migrate031: the old default 0.1 -> 0.4 (value text only), every other byte + CRLF kept, the marker at the end, one change-log row: %r" % (rA,))
    K.check(rB is not None and rB[0] == "a=1\ngate.nextFactor = 0.4\nb=2\n" + MK and rB[3] == ["gate.nextFactor", "0.1", "0.4"],
            "G migrate031: ' = ' separator kept, LF file without a final newline keeps having none: %r" % (rB,))
    K.check(rC_ is not None and rC_[0] == tC + MK + "\r\n" and rC_[1] == "" and rC_[3] == [] and len(rC_[2]) == 2 and "gate.nextFactor=0.25 kept" in rC_[2][0]
            and "gate.crudeFactor=0.3 is no longer read" in rC_[2][1],
            "G migrate031: a HAND-EDITED gate.nextFactor (0.25) is kept + noted; a gate.crudeFactor line is noted (no longer read) and left: %r" % (rC_,))
    K.check(rD is not None and rD[0] == tD + MK + "\n" and rD[1] == "" and rD[2] == [] and rD[3] == [],
            "G migrate031: no gate.nextFactor line (the live file today) = nothing to rewrite, only the run-once marker: %r" % (rD,))
    K.check(rE is None and rF is not None and "gate.nextFactor=0.\\\n  1\n" in rF[0] and rF[3] == [] and "kept" in rF[2][0]
            and rG is not None and rG[0] == "gate.nextFactor=0.4\n" + MK + "\na=1\\\n" and rG[3] == ["gate.nextFactor", "0.10", "0.4"],
            "G migrate031: the marker = nothing to do; a continued (two-line) value is never rewritten; 0.10 counts as the old default; a file "
            "ending in a continuation keeps the marker out of that value: %r | %r" % (rF, rG))

    # ---- G: migrate031 on scratch files (History copy first, change-log row with Undo, run twice)
    GH = os.path.join(SCRATCH, "g031")

    def mfile(sub, text):
        d_ = os.path.join(GH, sub)
        shutil.rmtree(d_, ignore_errors=True)
        os.makedirs(d_)
        p_ = os.path.join(d_, "config.properties")
        with open(p_, "wb") as f_:
            f_.write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(p_)
        return d_, p_

    def hist(d_, b_):
        h_ = os.path.join(d_, "config-history")
        if not os.path.isdir(h_):
            return False
        for root_, _ds, fs_ in os.walk(h_):
            for n_ in fs_:
                if open(os.path.join(root_, n_), "rb").read() == b_:
                    return True
        return False

    def clog(d_):
        p_ = os.path.join(d_, "config-changes.log")
        return open(p_, encoding="utf-8").read() if os.path.isfile(p_) else ""
    d1, p1 = mfile("default", tA)
    m1 = str(Cfg.migrate031())
    b1 = open(p1, "rb").read()
    cl1 = clog(d1)
    m1b = str(Cfg.migrate031())
    K.check(b1 == rA[0].encode("latin-1") and hist(d1, tA.encode("latin-1")) and "\tgate.nextFactor\t0.1\t0.4\tok" in cl1 and "SkyyGear 0.3.1" in cl1
            and "gate.nextFactor 0.1 -> 0.4" in m1 and m1b == "" and open(p1, "rb").read() == b1 and clog(d1) == cl1,
            "G migrate031 on a file: History copy of the old bytes first, the rewrite, a change-log row (status ok = Undo); the 2nd run changes "
            "nothing (marker): %s | %s" % (m1[:160], cl1[-160:]))
    Cfg.load()
    K.check(abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12, "G: after the update the loader reads 0.4 / 0.1")
    d2, p2 = mfile("hand", tC)
    m2 = str(Cfg.migrate031())
    b2 = open(p2, "rb").read()
    m2b = str(Cfg.migrate031())
    Cfg.load()
    K.check(b2 == (tC + MK + "\r\n").encode("latin-1") and hist(d2, tC.encode("latin-1")) and clog(d2).count("gate.nextFactor") == 0
            and "gate.nextFactor=0.25 kept" in m2 and m2b == "" and open(p2, "rb").read() == b2 and abs(float(Cfg.GATE_NEXT) - 0.25) < 1e-12,
            "G migrate031 on a HAND-EDITED file: value kept (the loader reads 0.25) + noted, only the marker added, no change-log row, 2nd run "
            "changes nothing: %s" % m2[:200])
    d3, p3 = mfile("absent", tD)
    m3 = str(Cfg.migrate031())
    m3b = str(Cfg.migrate031())
    Cfg.load()
    K.check(open(p3, "rb").read() == (tD + MK + "\n").encode("latin-1") and "new default 0.4 applies" in m3 and m3b == ""
            and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12,
            "G migrate031 with no gate rows (the live file): marker only, the new default 0.4 applies, 2nd run nothing: %s" % m3[:200])
    Cfg.FILE = None
    apply()
    shutil.rmtree(GH, ignore_errors=True)

    # ============================================================================ G33 (0.3.3): NO HARVESTING TWO TIERS ABOVE YOUR HOE / SICKLE
    apply()
    skills(Mining=10, Foraging=10, Farming=10)
    # a capturing PacketHandler on PR1 (GearGate.popup -> NotificationUtil.sendNotification -> PacketHandler.writeNoCache)
    CPg = JClass("javassist.ClassPool")
    cpg = CPg(True)
    cpg.appendClassPath(JClass("javassist.LoaderClassPath")(REFc.class_.getClassLoader()))
    phc = cpg.makeClass("com.hypixel.hytale.component.SkyyG33PH", cpg.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    phc.addField(JClass("javassist.CtField").make("public static java.util.ArrayList SENT = new java.util.ArrayList();", phc))
    for src_ in ("public String getIdentifier() { return \"g33\"; }",
                 "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
                 "public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { SENT.add(p); }"):
        phc.addMethod(JClass("javassist.CtNewMethod").make(src_, phc))
    PHG = phc.toClass(REFc.class_)
    PHGJ = JClass(PHG.getName())
    ph_ = us.allocateInstance(PHG)
    pf_ = None
    k_ = PR.class_
    while k_ is not None and pf_ is None:
        for f_ in k_.getDeclaredFields():
            if str(f_.getName()) == "packetHandler":
                f_.setAccessible(True)
                pf_ = f_
        k_ = k_.getSuperclass()
    old_ph = pf_.get(PR1)
    pf_.set(PR1, ph_)
    NOTE = JClass("com.hypixel.hytale.protocol.packets.interface_.Notification")

    def toasts():
        out_ = []
        for p_ in list(PHGJ.SENT):
            if isinstance(p_, NOTE):
                out_.append((None if p_.message is None else str(p_.message.rawText), None if p_.secondaryMessage is None else str(p_.secondaryMessage.rawText)))
        PHGJ.SENT.clear()
        return out_
    PPD = Gate.class_.getDeclaredField("POPPED")
    PPD.setAccessible(True)
    POPD = PPD.get(None)
    CROPB = {}
    for w_, m_ in zip([str(x) for x in LL.CROP_W], [int(x) for x in LL.CROP_M]):
        for b_ in ["Plant_Crop_%s_Block" % w_] + gsrcs:
            if b_ in gsrcs and b_.startswith("Plant_Crop_" + w_ + "_") and list(LL.catOf(b_)) == [4, m_]:
                CROPB[w_] = (b_, m_)
                break
    K.notes.append("G33: crop blocks %s (the bare boot loads the crops' _Item block types; the _Block ones need the farming module's codecs - the gate reads only the id)" % dict((k_, v_[0]) for k_, v_ in CROPB.items()))
    K.check(len(CROPB) >= 10 and all(w_ in CROPB for w_ in ("Wheat", "Carrot", "Cauliflower", "Pumpkin", "Tomato", "Cotton", "Potato")),
            "G33: a real crop BlockType for every key tier-table crop: %s" % sorted(CROPB))
    TT = {"Crude": 0, "Copper": 1, "Iron": 2, "Thorium": 3}
    cbad, cseen, cn, nref = [], set(), 0, 0
    n0_ = [int(x) for x in LL.N]
    for tool_ in ("Tool_Hoe_Crude", "Tool_Hoe_Copper", "Tool_Hoe_Iron", "Tool_Hoe_Thorium", "Tool_Sickle_Crude", "Tool_Sickle_Copper", "Tool_Sickle_Iron"):
        f_ = int(Data.toolFam(tool_))
        t_ = TT[tool_.split("_")[2]]
        for w_ in sorted(CROPB):
            b_, m_ = CROPB[w_]
            up = min(m_, FAMMAX[f_]) - max(t_, 1)
            cx, dmg = hitb(stack(tool_), b_)
            ref = refb(stack(tool_), b_)
            if up >= 2:
                ok = cx and abs(dmg - float(JFloat(0.3))) < 1e-6
                nref += 1
            elif up == 1:
                ok = (not cx) and abs(dmg - float(JFloat(ref * 0.4))) < 1e-6
            else:
                ok = (not cx) and abs(dmg - ref) < 1e-6
            ft_ = int(LL.farmTier(b_, tool_))
            ok = ok and ft_ == (0 if up <= 0 else (1 if up == 1 else 2))
            cn += 1
            cseen.add((tool_.split("_")[1], min(max(up, 0), 2)))
            if not ok:
                cbad.append((tool_, b_, m_, up, cx, dmg, ref, ft_))
    n1_ = [int(x) for x in LL.N]
    toasts()
    K.check(not cbad and cn >= 60 and {("Hoe", 0), ("Hoe", 1), ("Hoe", 2), ("Sickle", 0), ("Sickle", 1)} <= cseen and ("Sickle", 2) not in cseen
            and nref >= 10 and n1_[0] - n0_[0] == nref,
            "G33: THE CROP GATE on the REAL hit system + real crop blocks (%d hits): every hoe / sickle tier x every crop - own tier = its own power, "
            "one up = x0.4 + farmTier 1, two or more up (capped: hoes at Thorium, sickles at Iron) = CANCELLED, damage untouched, farmTier 2; "
            "no sickle is ever two below; %d refusals counted (N[0] +%d); seen %s; bad %s" % (cn, nref, n1_[0] - n0_[0], sorted(cseen), cbad[:4]))
    # the refusal's popup, captured
    Gate.class_  # noqa
    POPD.clear()
    cxP, dP_ = hitb(stack("Tool_Hoe_Copper"), CROPB["Potato"][0])
    tP = toasts()
    POPD.clear()
    cxC, dC_ = hitb(stack("Tool_Hoe_Crude"), CROPB["Cauliflower"][0])
    tC = toasts()
    POPD.clear()
    cxO, dO_ = hitb(stack("Tool_Pickaxe_Crude"), ORE[max(ORE)])
    tO = toasts()
    POPD.clear()
    cxW, dW_ = hitb(stack("Tool_Hoe_Crude"), CROPB["Wheat"][0])
    tW = toasts()
    K.check(cxP and tP == [("Too tough for your " + str(Gear.itemName("Tool_Hoe_Copper")),
                            "This crop needs at least an Iron hoe (Thorium for full Farming XP). Tier yours up on the Anvil (/smithing).")]
            and cxC and len(tC) == 1 and tC[0][1].startswith("This crop needs at least an Iron hoe (Thorium")
            and cxO and len(tO) == 1 and tO[0][1].startswith("It needs at least ") and "full speed" in tO[0][1]
            and not cxW and tW == [],
            "G33: the refusal popup (CAPTURED from a PacketHandler): a Copper hoe on a Potato -> 'Too tough for your <hoe>' / 'This crop needs at "
            "least an Iron hoe (Thorium for full Farming XP) ...'; a Crude hoe on Cauliflower the same; ore keeps the 0.3.1 words; a normal crop no "
            "popup: %s | %s | %s | %s" % (tP, tC, tO, tW))
    # not gated: bare hands, a sword, berries (not in the tier table), the Thorium hoe; ore / logs unchanged
    berry = [b_ for b_ in gsrcs if b_.startswith("Plant_Crop_") and int(LL.catOf(b_)[0]) == 4 and int(LL.catOf(b_)[1]) < 1]
    r_hand = hitb(None, CROPB["Wheat"][0])          # 0.3.5: hands count as Crude - Wheat (their own tier) stays free; Potato is refused (G35 H)
    r_sword = hitb(stack("Weapon_Sword_Iron"), CROPB["Wheat"][0])
    r_berry = hitb(stack("Tool_Hoe_Crude"), berry[0]) if berry else (True, 0.0)
    r_ore2 = hitb(stack("Tool_Pickaxe_Copper"), ORE[3])
    ref_ore2 = refb(stack("Tool_Pickaxe_Copper"), ORE[3])
    toasts()
    K.check(not r_hand[0] and abs(r_hand[1] - 0.3) < 1e-6 and not r_sword[0] and berry and not r_berry[0]
            and not r_ore2[0] and abs(r_ore2[1] - float(JFloat(ref_ore2 * 0.1))) < 1e-6,
            "G33: never refused: a Wheat crop by hand (vanilla damage), with a sword (0.3.5: Wheat = the Crude tier hands count as), a non-table plant (%s) with a Crude hoe; ORE unchanged - a Copper "
            "pickaxe on thorium two up = x0.1, not cancelled: %s" % (berry[:1], [r_hand, r_sword, r_berry, r_ore2]))
    apply(gate__on="false")
    r_off = hitb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0])
    ft_off = int(LL.farmTier(CROPB["Potato"][0], "Tool_Hoe_Crude"))
    apply()
    toasts()
    K.check(not r_off[0] and ft_off == -1, "G33: gate.on off = a Crude hoe breaks a Potato again, farmTier -1: %s %s" % (r_off, ft_off))
    # gear:fn:farmTier through the real bridge Function (what SkyySkills 0.4.35 calls): 2 = refused
    Fn33 = JClass(PKG + "GearLLFn")(JInt(2))          # = what SkyyGearPlugin.setup puts under gear:fn:farmTier (br.put(..., new GearLLFn(2)))
    fb = [None if Fn33 is None else int(Fn33.apply(JArray(JObject)([U1, JString(CROPB[w_][0]), JString(h_)])))
          for w_, h_ in (("Potato", "Tool_Hoe_Crude"), ("Potato", "Tool_Hoe_Iron"), ("Potato", "Tool_Sickle_Crude"), ("Wheat", "Tool_Hoe_Crude"))]
    K.check(fb == [2, 1, 1, 0], "G33: gear:fn:farmTier (GearLLFn(2), the bridge Function SkyySkills asks): Crude hoe on a Potato = 2 (refused), Iron hoe = 1, "
            "Crude sickle = 1 (sickles end at Iron), Wheat = 0: %s" % fb)
    st33 = str(LL.statusText())
    with zipfile.ZipFile(JAR) as zj_:
        man33 = zj_.read("manifest.json").decode("utf-8")
    K.check("three up refused, crops two up refused" in st33 and "a crop two tiers above your hoe is refused" in man33
            and "crops 2 up refused" in FRESH,
            "G33: statusText, the manifest sentence and the gate.on help name the crop rule: %s" % st33[-120:])
    # ---- G33F (fix round): the F-harvest gate on the REAL GearChestOpenSys + REAL UseBlockEvent$Pre events
    UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    ICX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    V3I = JClass("org.joml.Vector3i")
    COS = JClass(PKG + "GearChestOpenSys")
    cos_ = COS()

    def useb(s_, bid, pre_cancel=False, ch_=None):
        cx_ = us.allocateInstance(ICX.class_)
        cx_.setHeldItem(s_)
        e_ = UBP(ITY.Use, cx_, V3I(JInt(0), JInt(64), JInt(0)), bmap.get(bid))
        if pre_cancel:
            e_.setCancelled(True)
        POPD.clear()
        cos_.handle(JInt(0), ch_ or chH, stH, None, e_)
        return bool(e_.isCancelled()), toasts()
    toasts()
    nF0 = int(LL.N[0])
    fP = useb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0])
    fC = useb(stack("Tool_Hoe_Copper"), CROPB["Cauliflower"][0])
    nF1 = int(LL.N[0])
    fwant = [("Tool_Hoe_Crude", "Carrot"), ("Tool_Hoe_Crude", "Wheat"), ("Tool_Hoe_Iron", "Potato"), ("Tool_Hoe_Thorium", "Potato"),
             ("Tool_Sickle_Crude", "Potato"), (None, "Carrot"), ("Weapon_Sword_Iron", "Wheat")]          # 0.3.5: hands / a sword = Crude (one up / own tier pass; two up in G35 H)
    fok = [(h_, w_, useb(None if h_ is None else stack(h_), CROPB[w_][0])) for h_, w_ in fwant]
    fB = useb(stack("Tool_Hoe_Crude"), berry[0]) if berry else (True, [])
    fO = useb(stack("Tool_Pickaxe_Crude"), ORE[max(ORE)])
    fX = useb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0], pre_cancel=True)
    nF2 = int(LL.N[0])
    # creative: the same Crude hoe + Potato with a creative Player component on the chunk
    GMc = JClass("com.hypixel.hytale.protocol.GameMode")
    plC = us.allocateInstance(PLA.class_)
    gmf = None
    k_ = PLA.class_
    while k_ is not None and gmf is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == GMc.class_:
                f_.setAccessible(True)
                gmf = f_
        k_ = k_.getSuperclass()
    gmf.set(plC, GMc.Creative)
    chC = us.allocateInstance(chH.getClass())
    chC.comps = IHM()
    chC.comps.put(PR.getComponentType(), PR1)
    chC.comps.put(PLA.getComponentType(), plC)
    chC.ref = chH.ref
    fCr = useb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0], ch_=chC)
    gmf.set(plC, GMc.Adventure)
    fAd = useb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0], ch_=chC)
    apply(gate__on="false")
    fOff = useb(stack("Tool_Hoe_Crude"), CROPB["Potato"][0])
    apply()
    toasts()
    WT = ("Too tough for your " + str(Gear.itemName("Tool_Hoe_Crude")),
          "This crop needs at least an Iron hoe (Thorium for full Farming XP). Tier yours up on the Anvil (/smithing).")
    K.check(fP == (True, [WT]) and fC[0] and len(fC[1]) == 1 and fC[1][0][1] == WT[1] and nF1 - nF0 == 2,
            "G33F: F-harvest with a Crude hoe on a Potato / a Copper hoe on Cauliflower (two up) = the REAL UseBlockEvent$Pre CANCELLED + the "
            "crop popup (captured), N[0] +2: %s | %s | +%d" % (fP, fC, nF1 - nF0))
    K.check(all(not c_ and not t_ for h_, w_, (c_, t_) in fok) and berry and not fB[0] and not fO[0] and fX == (True, []) and nF2 == nF1,
            "G33F: never refused by the F gate: one up / own tier / an Iron or Thorium hoe on a Potato / a Crude sickle (sickles end at Iron) / an "
            "empty hand / a sword / a berry plant / ore with a Crude pickaxe; an event already cancelled is left alone (no popup, no count): "
            "%s berry %s ore %s pre %s" % ([(h_, w_, c_) for h_, w_, (c_, t_) in fok], fB, fO, fX))
    K.check(not fCr[0] and fCr[1] == [] and fAd[0] and not fOff[0],
            "G33F: creative skipped (not cancelled, no popup), the same Player in Adventure refused; gate.on off = not refused: %s %s %s" % (fCr, fAd, fOff))
    # ============================================================================ G34 (0.3.4): SIGILS + GATHERING ARMOR LEVELS + THE HOE TILL AREA
    pf_.set(PR1, old_ph)
    apply()
    Sig, ArmLv, Till, TillSys, Page = P("GearSigil"), P("GearArmLv"), P("GearTill"), P("GearTillSys"), P("ReforgePage")
    skills(Mining=10, Foraging=10, Farming=10)
    logs()
    SIGS = ["Skyy_Sigil_Unique", "Skyy_Sigil_Rare", "Skyy_Sigil_Legendary", "Skyy_Sigil_Fabled", "Skyy_Sigil_Mythic"]
    # ---- S1: the items + the rows
    K.check(all(Gear.item(i_) is not None for i_ in SIGS) and [str(x) for x in Sig.IDS] == SIGS and [int(Sig.rank(i_)) for i_ in SIGS] == [1, 2, 3, 4, 5]
            and int(Sig.rank("Skyy_Sigil_Normal")) == 0 and int(Sig.rank("Weapon_Sword_Iron")) == 0 and int(Sig.rank(None)) == 0
            and str(Sig.idOf(3)) == "Skyy_Sigil_Legendary" and Sig.idOf(0) is None and Sig.idOf(6) is None,
            "G34 S1: the five Sigil items are loaded from the jar (Unique .. Mythic, no Normal), rank / idOf")
    K.check(all(("\n" + k_ + "\n") in FRESH for k_ in ("part.sigils=true", "sigil.mythicUse=false", "garmor.levels=true", "hoe.areaOn=true", "hoe.area=1,3,3,5,5,7,7,9", "hoe.areaElsewhere=false"))
            and ("\ngarmor.ladders=Armor_Copper_Head>Armor_Iron_Head(Skyy_Ench_Iron*1)>Armor_Thorium_Head(Skyy_Ench_Thorium*1)>Armor_Cobalt_Head(Skyy_Ench_Cobalt*1)"
                 ">Armor_Adamantite_Head(Skyy_Ench_Adamantite*1),Armor_Copper_Chest>Armor_Iron_Chest(Skyy_Ench_Iron*2)") in FRESH
            and "Armor_Cobalt_Hands(Skyy_Ench_Cobalt*1)" in FRESH and "Mithril" not in str(Cfg.GARM_LADDERS)
            and bool(Cfg.SIG_ON) and not bool(Cfg.SIG_MY) and bool(Cfg.GARM_LV) and bool(Cfg.HOE_ON) and not bool(Cfg.HOE_ELSE) and Up.checkLadders("garmor.ladders", Cfg.GARM_LADDERS) is None,
            "G34 S1: the fresh config carries the 6 new rows at their defaults; garmor.ladders passes GearUp.checkLadders with the real items (Iron / "
            "Thorium 1 / 2 / 2 / 1, Cobalt / Adamantite 1 / 1 / 1 / 1, no Mithril yet)")
    dang = [k_ for k_ in ("part.sigils", "sigil.mythicUse", "garmor.levels", "garmor.ladders", "hoe.areaElsewhere") if not bool(CRows.flag(int(CRows.index(k_)), "danger"))]
    K.check(not dang and not bool(CRows.flag(int(CRows.index("hoe.areaOn")), "danger")) and not bool(CRows.flag(int(CRows.index("hoe.area")), "danger")),
            "G34 S1: economy / protection rows are danger rows (Server Setup asks first): %s" % dang)

    # ---- S2: the Sigil core (GearSigil.apply) on a real inventory
    def sword(r_, lvl_=10, ident=True, sid="Weapon_Sword_Iron", q=1):
        return Data.put(stack(sid, q), Roll.newDoc(sid, JInt(r_), ident, "craft", JInt(lvl_)), None)

    def fp(cs_, sec_, sl_):
        return str(Forge.fp(cs_[sec_].getItemStack(JShort(sl_))))
    invS, csS = mkinv()
    csS["hotbar"].setItemStackForSlot(JShort(0), sword(0))
    csS["storage"].setItemStackForSlot(JShort(3), stack("Skyy_Sigil_Legendary", 2))
    d0 = doc(csS["hotbar"].getItemStack(JShort(0)))
    m0 = [str(x) for x in Data.mods(d0)]
    have0 = list(Sig.carried(invS))
    K.check(have0[3] == 2 and sum(have0) == 2 and list(Sig.choices(Sig.carried(invS), 0)) == [3] and list(Sig.choices(Sig.carried(invS), 3)) == [],
            "G34 S2: carried / choices count the Sigils in storage + backpack + hotbar: %s" % have0)
    n0 = [int(x) for x in Sig.N]
    rS = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 3, U1, "Tester")
    d1 = doc(csS["hotbar"].getItemStack(JShort(0)))
    K.check(int(rS[0]) == 1 and int(Data.rarity(d1)) == 3 and [str(x) for x in Data.mods(d1)] == m0 and int(Data.num(d1, "sgN", 0)) == 1
            and int(csS["storage"].getItemStack(JShort(3)).getQuantity()) == 1 and ids(csS).get("Weapon_Sword_Iron") == 1
            and int(Sig.N[0]) == n0[0] + 1,
            "G34 S2: SKIP TIERS - a Normal Iron sword + ONE Legendary Sigil = LEGENDARY at once, its lines unchanged (the new slots stay empty), "
            "sgN 1, the Sigil stack 2 -> 1, still one sword: %s / %s" % (str(rS[1]), [str(x) for x in Data.mods(d1)][:2]))
    lg = logs()
    K.check(any(" SIGIL-BEGIN Tester " in l_ for l_ in lg) and any(" SIGIL Tester " in l_ and "normal -> legendary" in l_ for l_ in lg),
            "G34 S2: gear.log has SIGIL-BEGIN (flushed before anything moved) and the SIGIL line: %s" % [l_[:80] for l_ in lg if "SIGIL" in l_])
    rf_ = Roll.reforge("Weapon_Sword_Iron", d1)
    K.check(int(Data.mods(rf_).size()) == int(Cfg.R_MODS[int(Cfg.ri(3))]) and int(Data.mods(d1).size()) < int(Cfg.R_MODS[int(Cfg.ri(3))]),
            "G34 S2: the next Reforge FILLS the new slots (GearRoll.reforge rolls the Legendary count: %d lines, it had %d)" % (int(Data.mods(rf_).size()), int(Data.mods(d1).size())))
    # refusals: nothing moves
    before_ = ids(csS)
    r_low = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 3, U1, "Tester")
    r_low2 = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 1, U1, "Tester")
    r_none = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 4, U1, "Tester")
    r_fp = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", "stale-fingerprint", 4, U1, "Tester")
    K.check(int(r_low[0]) == 0 and "only raises items below Legendary" in str(r_low[1]) and int(r_low2[0]) == 0
            and int(r_none[0]) == 0 and "You need a Fabled Sigil" in str(r_none[1]) and int(r_fp[0]) == 0 and "moved or changed" in str(r_fp[1])
            and ids(csS) == before_ and int(Data.rarity(doc(csS["hotbar"].getItemStack(JShort(0))))) == 3,
            "G34 S2: refused, nothing moves: a Sigil at / below the rarity (upward only), no Sigil of that rarity carried, a stale fingerprint: %s | %s | %s"
            % (str(r_low[1]), str(r_none[1]), str(r_fp[1])))
    # every other refusal (Sig.why) on its own stack
    def why_(st_, R_):
        return None if st_ is None else Sig.why(st_, Forge.docOf(st_.getItemId(), st_.getMetadata()), JInt(R_))
    w_set = why_(Data.put(stack("Armor_Copper_Head"), P("GearMine").doc("Armor_Copper_Head", "craft", JInt(5)), None), 2)
    w_unid = why_(sword(1, ident=False), 3)
    w_stack = why_(sword(0, q=2), 2)
    w_plain = why_(stack("Ingredient_Bar_Iron"), 2)
    w_myth = why_(sword(5), 5)
    dut_ = Roll.newDoc("Weapon_Sword_Iron", JInt(0), True, "craft", JInt(10))
    dut_.put("r", JClass("org.bson.BsonString")("untiered"))
    w_ut = why_(Data.put(stack("Weapon_Sword_Iron"), dut_, None), 5)
    apply(part__sigils="false")
    w_off = why_(sword(0), 2)
    apply()
    K.check(w_set is not None and "gathering armor levels with your Mining and tiers up on the Anvil instead" in str(w_set) and "NPC" not in str(Sig.MARKET),
            "FIX C2/A1: a Sigil on Mining Set armor is refused with the gathering-armor reason (question 8); the market text names only the Bazaar: %s | %s" % (w_set, Sig.MARKET))
    K.check(w_set is not None and "Set rarity stays" in str(w_set) and "Identify it first" in str(w_unid)
            and "stack of 2" in str(w_stack) and "has no rarity" in str(w_plain) and "already Mythic" in str(w_myth)
            and "Untiered" in str(w_ut) and "switched off" in str(w_off),
            "G34 S2: Sig.why refuses a Set mining piece, an unidentified item, a stack, a non-gear item, a Mythic item, an Untiered item, part.sigils "
            "off: %s" % [str(x)[:50] for x in (w_set, w_unid, w_stack, w_plain, w_myth, w_ut, w_off)])
    # fixer 2: the Mythic Sigil is REFUSED by default (LOCKED "Mythic boss-only (out of random drops + Smithing step-up)"): nothing moves, it is
    # no choice on the strip; sigil.mythicUse=true allows it
    csS["storage"].setItemStackForSlot(JShort(4), stack("Skyy_Sigil_Mythic", 1))
    b_my = ids(csS)
    r_my0 = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 5, U1, "Tester")
    ch_off = list(Sig.choices(Sig.carried(invS), 3))
    w_myoff = why_(sword(0), 5)
    w_fab = why_(sword(0), 4)
    apply(sigil__mythicUse="true")
    ch_on = list(Sig.choices(Sig.carried(invS), 3))
    K.check(int(r_my0[0]) == 0 and "boss-only" in str(r_my0[1]) and ids(csS) == b_my and int(Data.rarity(doc(csS["hotbar"].getItemStack(JShort(0))))) == 3
            and ch_off == [] and "boss-only" in str(w_myoff) and w_fab is None and ch_on == [5] and bool(Cfg.SIG_MY)
            and len(str(Sig.MYOFF)) <= 80,
            "FIX2 M1: a Mythic Sigil is refused by default (Mythic is boss-only), nothing moves, it is not offered on the strip; a Fabled Sigil still "
            "works; sigil.mythicUse=true offers it: %s | %s %s" % (str(r_my0[1]), ch_off, ch_on))
    r_my = Sig.apply(invS, 0, 0, "Weapon_Sword_Iron", fp(csS, "hotbar", 0), 5, U1, "Tester")
    st_my = csS["hotbar"].getItemStack(JShort(0))
    s4_ = csS["storage"].getItemStack(JShort(4))
    K.check(int(r_my[0]) == 1 and int(Data.rarity(doc(st_my))) == 5 and (s4_ is None or s4_.isEmpty()),
            "G34 S2: a Mythic Sigil on the Legendary sword = Mythic (the last Sigil of the stack: the slot empties)")
    K.check(Wall.why(st_my.getItemId(), st_my.getMetadata()) is not None, "G34 S2: the Mythic sword is behind the market wall (Mythic is never on a market)")
    apply()
    # failure paths: the item's slot refuses the new stack; the Sigil's slot refuses the removal; a crash right after the Sigil left
    invF, csF = mkinv(fail=("hotbar", "storage"))
    csF["hotbar"].setItemStackForSlot(JShort(2), sword(0))
    csF["storage"].setItemStackForSlot(JShort(0), stack("Skyy_Sigil_Rare", 1))
    csF["hotbar"].refuseId = "Weapon_Sword_Iron"
    bF = ids(csF)
    rF1 = Sig.apply(invF, 0, 2, "Weapon_Sword_Iron", fp(csF, "hotbar", 2), 2, U1, "Tester")
    lgF = logs()
    K.check(int(rF1[0]) == -1 and ids(csF) == bF and int(Data.rarity(doc(csF["hotbar"].getItemStack(JShort(2))))) == 0
            and any("SIGIL-FAILED" in l_ and "RESTORED" in l_ for l_ in lgF),
            "G34 S3: the item's slot refuses the new stack -> the item AND the Sigil are back (counts equal, rarity unchanged), SIGIL-FAILED ... RESTORED: %s / %s" % (str(rF1[1]), bF))
    csF["hotbar"].refuseId = None
    csF["hotbar"].tripped = False
    csF["storage"].rm = 1
    rF2 = Sig.apply(invF, 0, 2, "Weapon_Sword_Iron", fp(csF, "hotbar", 2), 2, U1, "Tester")
    K.check(int(rF2[0]) == -1 and ids(csF) == bF and "nothing was used" in str(rF2[1]), "G34 S3: the Sigil's slot refuses the removal -> nothing used: %s" % str(rF2[1]))
    csF["storage"].rm = 0
    Sig.CRASH_AT = 1
    crashed = False
    try:
        Sig.apply(invF, 0, 2, "Weapon_Sword_Iron", fp(csF, "hotbar", 2), 2, U1, "Tester")
    except Exception:
        crashed = True
    Sig.CRASH_AT = 0
    aF = ids(csF)
    lgC = logs()
    K.check(crashed and aF.get("Skyy_Sigil_Rare", 0) == 0 and aF.get("Weapon_Sword_Iron") == 1 and int(Data.rarity(doc(csF["hotbar"].getItemStack(JShort(2))))) == 0
            and any("SIGIL-BEGIN" in l_ for l_ in lgC),
            "G34 S3: a CRASH right after the Sigil left: the Sigil is lost (named in SIGIL-BEGIN), the item is unchanged - never a second item, never a free rarity")
    # a lifelong tool keeps being lifelong; a /pickaxe copy with a Sigil after the copy is 'invested'
    invL, csL = mkinv()
    llp = Data.put(stack("Tool_Pickaxe_Iron"), Life.llDoc(Roll.newDoc("Tool_Pickaxe_Iron", JInt(0), True, "craft", JInt(12)), "Tool_Pickaxe_Iron", U1, "p1", "sigsigsigsigsig1", False), None)
    csL["hotbar"].setItemStackForSlot(JShort(1), llp)
    csL["backpack"].setItemStackForSlot(JShort(0), stack("Skyy_Sigil_Rare", 1))
    rL = Sig.apply(invL, 0, 1, "Tool_Pickaxe_Iron", fp(csL, "hotbar", 1), 2, U1, "Tester")
    dL = doc(csL["hotbar"].getItemStack(JShort(1)))
    b0_ = csL["backpack"].getItemStack(JShort(0))
    K.check(int(rL[0]) == 1 and bool(LL.isLL(dL)) and str(LL.uid(dL)) == "sigsigsigsigsig1" and int(Data.num(dL, "tr", 0)) == 1 and int(Data.rarity(dL)) == 2
            and (b0_ is None or b0_.isEmpty()),
            "G34 S4: a Sigil on your LIFELONG pickaxe (Sigil from the backpack): still lifelong, same uid, Rare, its rarity counts (tr 1)")
    rp_ = Life.llDoc(Roll.newDoc("Tool_Pickaxe_Iron", JInt(0), True, "craft", JInt(12)), "Tool_Pickaxe_Iron", U1, "p1", "copycopycopycop1", True)
    rp_.put("lrpT", JClass("org.bson.BsonInt32")(JInt(2)))
    rp_.put("lrpS", JClass("org.bson.BsonInt32")(JInt(0)))
    inv0 = bool(LL.invested("Tool_Pickaxe_Iron", rp_))
    rp_.put("sgN", JClass("org.bson.BsonInt32")(JInt(1)))
    inv1 = bool(LL.invested("Tool_Pickaxe_Iron", rp_))
    rp_.put("lrpS", JClass("org.bson.BsonInt32")(JInt(1)))
    inv2 = bool(LL.invested("Tool_Pickaxe_Iron", rp_))
    K.check(not inv0 and inv1 and not inv2, "G34 S4: a /pickaxe replacement is invested by a Sigil used AFTER it was made (sgN over lrpS) - never thrown away: %s %s %s" % (inv0, inv1, inv2))
    # MARKET: the Auction House (any caller) may take a Sigil, the Bazaar / an NPC shop never (callers' classes in their packages, generated)
    w_ah = Wall.why("Skyy_Sigil_Rare", None)
    w_bz = JClass("com.skyy.bazaar.SkyyG34Caller").ask("Skyy_Sigil_Rare")
    w_mc = JClass("com.skyy.merchants.SkyyG34Caller").ask("Skyy_Sigil_Legendary")
    w_au = JClass("com.skyy.auctions.SkyyG34Caller").ask("Skyy_Sigil_Mythic")
    w_bz2 = JClass("com.skyy.bazaar.SkyyG34Caller").ask("Ingredient_Bar_Iron")
    vet = Gear.bridge().get("market:veto")
    K.check(w_ah is None and w_au is None and w_bz is not None and "never sold on the Bazaar" in str(w_bz) and w_mc is not None and w_bz2 is None,
            "G34 S5: G3 'AH yes, Bazaar never': the market wall answers the Auction House (com.skyy.auctions caller) null, the Bazaar (com.skyy.bazaar) "
            "and NPC shops (com.skyy.merchants) the refusal; a plain bar is not affected: AH %s | bazaar %s | merchants %s" % (w_ah, w_bz, w_mc))
    # the Bazaar / NPC shops never list Sigils by default (their newest build scripts, read as text)
    def newest(mod_, pre_):
        d_ = os.path.join(ROOT, mod_)
        fs_ = sorted([f_ for f_ in os.listdir(d_) if f_.startswith(pre_) and f_.endswith(".py")], key=lambda f_: [int(x_) for x_ in re.findall(r"\d+", f_)])
        return open(os.path.join(d_, fs_[-1]), encoding="utf-8").read() if fs_ else ""
    _nm = newest("SkyyMerchants", "build_skyymerchants_")
    K.check("Skyy_Sigil" not in newest("SkyyBazaar", "build_skyybazaar_") and not re.search(r'\(\s*"Skyy_Sigil[A-Za-z_]*",\s*"', _nm) and "weapon.Skyy_Sigil" not in _nm
            and ('id.startsWith("Skyy_Sigil_")' in _nm or "Skyy_Sigil" not in _nm),
            "G34 S5 (0.3.5): the newest SkyyBazaar build script names no Sigil; the newest SkyyMerchants (0.1.4) names Sigils only in its wall / never-sell "
            "list (no stock line)")

    # ---- S6: THE ANVIL'S SIGIL STRIP on a FakeReforgePage (anPick -> build -> Other -> Apply (arm) -> Confirm)
    FRP = JClass(FAKE_PKG + ".FakeReforgePage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def page_txt(pg_, ref_, st_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(ref_, ub_, ue_, st_)
        out_ = []
        hs_ = {}
        for c_ in ub_.getCommands():
            vals = []
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals.append("" if v_ is None else str(v_))
                except Exception:
                    vals.append("")
            out_.append("|".join(vals))
            dat_ = vals[2] if "{" in vals[2] else vals[1]
            m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat_)
            if m_:
                h_ = re.search(r"Height: (\d+)", m_.group(1))
                hs_[vals[0]] = hs_.get(vals[0], 0) + (int(h_.group(1)) if h_ else 0)
        ev_ = []
        for e_ in ue_.getEvents():
            try:
                ev_.append(str(e_.getData()))
            except Exception:
                pass
        return "\n".join(out_) + "\n" + "\n".join(ev_), hs_
    invP, csP = mkinv()
    csP["hotbar"].setItemStackForSlot(JShort(0), sword(0))
    refP, stP, chP, plP = world(invP, csP, PR1)
    pg = FRP(PR1)
    pg.anPick(invP, 0, 0)
    t0_, h0_ = page_txt(pg, refP, stP)
    csP["storage"].setItemStackForSlot(JShort(0), stack("Skyy_Sigil_Rare", 1))
    csP["storage"].setItemStackForSlot(JShort(1), stack("Skyy_Sigil_Legendary", 3))
    t1_, h1_ = page_txt(pg, refP, stP)
    K.notes.append("G34 S6 debug: %s" % [l_[:160] for l_ in t1_.split(chr(10)) if "Sg" in l_ or "Sigil" in l_][:8])
    K.check("#SkyyGSg " not in t0_ and "#SkyyGSg " in t1_ and "Rare Sigil (x1): Normal -> RARE" in t1_ and "#SkyyGBtnSgN" in t1_,
            "G34 S6: the Sigil strip shows only while a Sigil is carried; the lowest Sigil above the item first ('Rare Sigil (x1): Normal -> RARE'), "
            "an Other button with two that fit")
    K.check(h1_.get("#SkyyGAnvil", 0) <= 656 and h0_.get("#SkyyGAnvil", 0) <= 656 and h1_.get("#SkyyGAnvil", 0) == h0_.get("#SkyyGAnvil", 0),
            "G34 S6: the right column stays 656 px with and without the strip (the lines column gives up 50): %s / %s" % (h1_.get("#SkyyGAnvil"), h0_.get("#SkyyGAnvil")))

    def click(a_):
        pg.lastForge = JLong(0)
        pg.handleDataEvent(refP, stP, '{"a":"%s"}' % a_)
        return str(pg.info)
    i_other = click("sgn")
    t2_, _h = page_txt(pg, refP, stP)
    i_arm = click("sg")
    t3_, _h = page_txt(pg, refP, stP)
    i_do = click("sg")
    dP = doc(csP["hotbar"].getItemStack(JShort(0)))
    K.check(i_other.startswith("=Legendary Sigil picked") and "Legendary Sigil (x3): Normal -> LEGENDARY" in t2_ and i_arm.startswith("=Click Confirm sigil")
            and "Confirm sigil" in t3_ and i_do.startswith("+Your ") and "is Legendary now" in i_do and "empty slot" in i_do and int(Data.rarity(dP)) == 3
            and int(csP["storage"].getItemStack(JShort(1)).getQuantity()) == 2 and int(csP["storage"].getItemStack(JShort(0)).getQuantity()) == 1,
            "G34 S6: Other -> the Legendary Sigil; Apply arms ('Confirm sigil'); the second click spends ONE Legendary Sigil -> LEGENDARY and names the "
            "empty slots: %s | %s | %s" % (i_other, i_arm, i_do))
    t4_, _h = page_txt(pg, refP, stP)
    i_low = click("sg")
    K.check("Your Sigils are not above Legendary" in t4_ and "Cannot apply" in t4_ and i_low.startswith("-You carry no Sigil above Legendary"),
            "G34 S6: afterwards the Rare Sigil cannot apply (upward only): the strip says so and Apply refuses: %s" % i_low)

    # ---- A: GATHERING ARMOR THAT LEVELS
    K.check(str(ArmLv.skillOf("Armor_Iron_Head")) == "Mining" and ArmLv.skillOf("Armor_Bronze_Head") is None and ArmLv.skillOf("Tool_Pickaxe_Iron") is None,
            "G34 A1: the 28 metal pieces are gathering armor with the Mining gate (no other armor)")
    skills(Mining=10)
    lv10 = [int(ArmLv.levelFor(U1, i_)) for i_ in ("Armor_Copper_Head", "Armor_Iron_Head", "Armor_Cobalt_Chest")]
    skills(Mining=30)
    lv30 = [int(ArmLv.levelFor(U1, i_)) for i_ in ("Armor_Copper_Head", "Armor_Iron_Head", "Armor_Cobalt_Chest")]
    bC, bI, bO = [list(Lvl.band(i_)) for i_ in ("Armor_Copper_Head", "Armor_Iron_Head", "Armor_Cobalt_Chest")]
    br.remove("skill:fn:level")
    Gate.forget(U1)
    lvNo = int(ArmLv.levelFor(U1, "Armor_Copper_Head"))
    br.put("skill:fn:level", SkillFn())
    Gate.forget(U1)
    apply(garmor__levels="false")
    offS = ArmLv.skillOf("Armor_Iron_Head")
    off_lad = str(LL.ladders())
    apply()
    cl_ = lambda v_, b_: max(b_[0], min(v_, b_[1]))
    K.check(lv10 == [cl_(10, bC), cl_(10, bI), cl_(10, bO)] and lv10[1] == bI[0] and lv30 == [cl_(30, bC), cl_(30, bI), cl_(30, bO)]
            and lvNo == -1 and offS is None and "Armor_" not in off_lad,
            "G34 A1: level = your Mining level kept inside the tier band (Mining 10: Copper 10, Iron %d = its start (inactive), Cobalt %d; Mining 30: %s); "
            "no SkyySkills = -1 (keep); garmor.levels off = no gathering armor, no armor ladders: %s %s bands %s %s %s" % (bI[0], bO[0], lv30, lv10, lv30, bC, bI, bO))
    # the watch: a Mining level-up queues the stamp scan (GearLL.RESYNC)
    skills(Mining=12)
    ArmLv.LV.clear()
    LL.RESYNC.clear()
    ArmLv.watch(U1)
    first_ = LL.RESYNC.containsKey(U1)
    nw0 = int(ArmLv.N[3])
    skills(Mining=13)
    ArmLv.watch(U1)
    K.check(not first_ and LL.RESYNC.containsKey(U1) and int(ArmLv.N[3]) == nw0 + 1, "G34 A2: the first look only remembers the level; a Mining level-up -> RESYNC (the stamp scan runs the sync)")
    LL.RESYNC.clear()
    # the sync on a real inventory: the armor section + storage; unidentified / stacked / unstamped pieces are left alone
    invA, csA = mkinv()
    Mine = P("GearMine")
    csA["armor"].setItemStackForSlot(JShort(0), Data.put(stack("Armor_Copper_Head"), Mine.doc("Armor_Copper_Head", "craft", JInt(5)), None))
    csA["storage"].setItemStackForSlot(JShort(2), Data.put(stack("Armor_Iron_Chest"), Mine.doc("Armor_Iron_Chest", "craft", JInt(15)), None))
    un_ = Mine.doc("Armor_Copper_Legs", "craft", JInt(5))
    un_.put("id", JClass("org.bson.BsonBoolean")(False))
    csA["storage"].setItemStackForSlot(JShort(3), Data.put(stack("Armor_Copper_Legs"), un_, None))
    csA["storage"].setItemStackForSlot(JShort(4), stack("Armor_Copper_Hands"))
    csA["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Weapon_Sword_Iron"), Roll.newDoc("Weapon_Sword_Iron", JInt(0), True, "craft", JInt(5)), None))
    ns0 = int(ArmLv.N[1])
    nA = int(ArmLv.sync(PR1, invA, True))
    dA0 = doc(csA["armor"].getItemStack(JShort(0)))
    dA1 = doc(csA["storage"].getItemStack(JShort(2)))
    dA2 = doc(csA["storage"].getItemStack(JShort(3)))
    nA2 = int(ArmLv.sync(PR1, invA, True))
    nA3 = int(ArmLv.sync(PR1, invA, False))
    K.check(nA == 1 and int(Data.num(dA0, "lvl", -1)) == 13 and int(Data.num(dA1, "lvl", -1)) == 15 and int(Data.num(dA2, "lvl", -1)) == 5
            and nA2 == 0 and nA3 == 0 and int(ArmLv.N[1]) == ns0 + 1 and int(Data.rarity(dA0)) == int(Defs.R_SET) and str(P("GearSet").of(dA0)) == "mining_copper"
            and csA["storage"].getItemStack(JShort(4)).getMetadata() is None,
            "G34 A3: the sync (Mining 13): the worn Copper helmet 5 -> 13 (Set rarity + set field kept), the Iron chest stays 15 (its tier start), an "
            "unidentified piece / an unstamped piece / a sword untouched; the 2nd sync writes nothing; a throttled call does nothing")
    # FIX B2: a Mining level-up right after a sync is NOT eaten by the 400 ms throttle (watch sets FORCE; the stamp task's sync(false) honours it once)
    skills(Mining=14)
    ArmLv.watch(U1)
    fq_ = bool(ArmLv.FORCE.containsKey(U1))
    nB = int(ArmLv.sync(PR1, invA, False))
    dB = doc(csA["armor"].getItemStack(JShort(0)))
    nB2 = int(ArmLv.sync(PR1, invA, False))
    K.check(fq_ and nB == 1 and int(Data.num(dB, "lvl", -1)) == 14 and not bool(ArmLv.FORCE.containsKey(U1)) and nB2 == 0,
            "FIX B2: a level-up (13 -> 14) within the throttle window: the watch's FORCE makes the next throttled sync write [Lv 14] at once (used up; "
            "the call after it is throttled again): %s %s %s" % (fq_, nB, nB2))
    skills(Mining=13)
    LL.RESYNC.clear()
    ArmLv.LV.clear()
    li_ = Forge.lvlInfo(U1, "Armor_Copper_Head", dA0)
    K.check(int(li_[0]) == 8 and "gathering armor follows your Mining level" in str(li_[5]), "G34 A3: Reforge Level up refuses a gathering armor piece: %s" % str(li_[5]))
    # THE TIER-UP on the Anvil (GearUp: check / docI / upgrade): Copper -> Iron with 1 Enchanted Iron, needs Mining 15
    sCH = Data.put(stack("Armor_Copper_Head"), Mine.doc("Armor_Copper_Head", "craft", JInt(13)), None)
    cU1 = Up.check(sCH, U1)
    skills(Mining=16)
    cU2 = Up.check(sCH, U1)
    cCh = Up.check(Data.put(stack("Armor_Copper_Chest"), Mine.doc("Armor_Copper_Chest", "craft", JInt(13)), None), U1)
    cHd = Up.check(Data.put(stack("Armor_Thorium_Hands"), Mine.doc("Armor_Thorium_Hands", "craft", JInt(22)), None), U1)
    qd_ = Mine.doc("Armor_Copper_Head", "craft", JInt(13))
    qd_.put("set", JClass("org.bson.BsonString")("quest_boss_x"))
    cQ = Up.check(Data.put(stack("Armor_Copper_Head"), qd_, None), U1)
    def piece_(id_, r_, lvl_):          # an old rolled metal piece (before 0.2.15: a plain rarity, no set field) / a Mythic one
        d_ = Mine.doc(id_, "craft", JInt(lvl_))
        d_.put("r", JClass("org.bson.BsonString")(r_))
        d_.remove("set")
        return Data.put(stack(id_), d_, None)
    cMy = Up.check(piece_("Armor_Copper_Head", "mythic", 13), U1)
    cOld = Up.check(piece_("Armor_Copper_Head", "rare", 13), U1)
    K.notes.append("G34 A4 debug: cU1 %s cU2 %s cCh %s cHd %s cQ %s cMy %s cOld %s" % tuple(str(x[0])[:70] for x in (cU1, cU2, cCh, cHd, cQ, cMy, cOld)))
    K.check(str(Up.next("Armor_Copper_Head")) == "Armor_Iron_Head" and str(Up.next("Armor_Cobalt_Legs")) == "Armor_Adamantite_Legs" and Up.next("Armor_Adamantite_Head") is None
            and cU1[0] is not None and ("needs Mining %d (you: 13)" % bI[0]) in str(cU1[0]) and bI[0] == 15 and cU2[0] is None and list(cU2[2][0]) == ["Skyy_Ench_Iron"] and list(cU2[2][1]) == [1]
            and cCh[0] is None and list(cCh[2][1]) == [2] and cQ[0] is not None and "special" in str(cQ[0]) and cMy[0] is not None and cOld[0] is None
            and cHd[0] is not None,
            "G34 A4: the Anvil tier-up: Copper Head -> Iron Head costs 1 Enchanted Iron and needs Mining 15 (13 refused, 16 fine), a chest costs 2, a "
            "quest set piece / a Mythic piece stay special, an old rolled piece may climb, Thorium hands need Mining 20 (16 refused): %s | %s | %s"
            % (str(cU1[0]), str(cQ[0])[:60], str(cHd[0])))
    invU, csU = mkinv()
    csU["armor"].setItemStackForSlot(JShort(0), sCH)
    csU["storage"].setItemStackForSlot(JShort(0), stack("Skyy_Ench_Iron", 3))
    fU = str(Forge.fp(csU["armor"].getItemStack(JShort(0))))
    rU = Up.upgrade(invU, 3, 0, "Armor_Copper_Head", fU, U1, "Tester")
    sU = csU["armor"].getItemStack(JShort(0))
    dU = doc(sU)
    K.check(int(rU[0]) == 1 and str(sU.getItemId()) == "Armor_Iron_Head" and int(Data.rarity(dU)) == int(Defs.R_SET) and str(P("GearSet").of(dU)) == "mining_iron"
            and int(Data.num(dU, "lvl", -1)) == 16 and int(csU["storage"].getItemStack(JShort(0)).getQuantity()) == 2,
            "G34 A4: upgrade() in the ARMOR slot: Copper Head -> Iron Head, rarity Set KEPT, set field -> mining_iron, level = Mining 16, 1 Enchanted Iron used: %s" % str(rU[1]))
    oldR = piece_("Armor_Copper_Head", "rare", 13)
    csU["storage"].setItemStackForSlot(JShort(5), oldR)
    mR0 = [str(x) for x in Data.mods(doc(oldR))]
    rO = Up.upgrade(invU, 1, 5, "Armor_Copper_Head", str(Forge.fp(csU["storage"].getItemStack(JShort(5)))), U1, "Tester")
    dO = doc(csU["storage"].getItemStack(JShort(5)))
    K.check(int(rO[0]) == 1 and int(Data.rarity(dO)) == 2 and len([str(x) for x in Data.mods(dO)]) == len(mR0) and P("GearSet").of(dO) is None,
            "G34 A4: an old rolled (Rare) Copper piece climbs to Iron keeping its rarity and its lines")
    skills(Mining=10, Foraging=10, Farming=10)
    logs()

    # ---- T: THE HOE TILL AREA (GearTill decision logic + GearTillSys on a REAL InventoryChangeEvent; the block reads / writes through the
    # harness seams here - the till child runs area() against a REAL 0.7 ChunkStore)
    K.check([int(Till.side(JInt(t_))) for t_ in range(8)] == [1, 3, 3, 5, 5, 7, 7, 9] and int(Till.side(JInt(-3))) == 1 and int(Till.side(JInt(12))) == 9
            and Till.checkArea("hoe.area", "1,3,3,5,5,7,7,9") is None and Till.checkArea("hoe.area", "1,3,3,5") is not None
            and Till.checkArea("hoe.area", "1,2,3,5,5,7,7,9") is not None and Till.checkArea("hoe.area", "1,3,3,5,5,7,7,11") is not None,
            "G34 T1: the till square per tier Crude .. Onyxium = 1 / 3 / 3 / 5 / 5 / 7 / 7 / 9 (clamped); checkArea refuses 4 values, an even side, 11")
    apply(hoe__area="9,9")
    side_bad = int(Till.side(JInt(3)))
    apply(hoe__area="1,1,1,1,1,1,1,1")
    side_one = int(Till.side(JInt(3)))
    apply()
    K.check(side_bad == 5 and side_one == 1, "G34 T1: a hand-edited bad hoe.area = the default (one WARN); all 1 = vanilla single blocks: %s %s" % (side_bad, side_one))
    PERMA = {"v": True}

    @JImplements("java.util.function.Function")
    class PermF(object):
        @JOverride
        def apply(self, o):
            v_ = PERMA["v"]
            return None if v_ is None else JObject(JBoolean(v_), Bool_)
    Till.PERM = PermF()
    al_ = []
    for v_, el_ in ((True, False), (False, False), (None, False), (None, True)):
        PERMA["v"] = v_
        apply(hoe__areaElsewhere=("true" if el_ else "false"))
        al_.append(int(Till.allowed(U1, "w")))
    apply()
    K.check(al_ == [1, 0, 0, 1], "G34 T2: protection: island:perm:fn build TRUE = till, FALSE = refused, not an island (null) = refused unless hoe.areaElsewhere: %s" % al_)
    PERMA["v"] = True
    # the block grid seam: y 64 = grass, (10,64,10) = freshly tilled, y 65 air; obstacles: rock above (11,64,10), stone at (9,64,9), (12,64,12) unloaded
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType").getAssetMap()
    Till.IDX = None
    Till.TOI = -1
    Till.resolve()
    _okix = [(str(Till.FROM[i_]), int(Till.IDX[i_])) for i_ in range(len(Till.IDX)) if int(Till.IDX[i_]) >= 0]
    GR, TI_, ST_, EM = _okix[0][1], int(BT.getIndex("Soil_Dirt_Tilled")), int(BT.getIndex("Rock_Stone")), int(Till.EMPTY)          # Empty: the mod's own answer (a bare boot has no Empty block type -> 0)
    K.notes.append("G34 T: tillable blocks loaded in this boot: %s (grass stand-in %s), tilled %d, stone %d, empty %d" % ([n_ for n_, i_ in _okix], _okix[0][0], TI_, ST_, EM))
    GRID = {}

    def reset_grid():
        GRID.clear()
        for x_ in range(0, 20):
            for z_ in range(0, 20):
                GRID[(x_, 64, z_)] = GR
                GRID[(x_, 65, z_)] = EM
        GRID[(10, 64, 10)] = TI_
        GRID[(11, 65, 10)] = ST_
        GRID[(9, 64, 9)] = ST_
        del GRID[(12, 64, 12)]

    @JImplements("java.util.function.Function")
    class BlkF(object):
        @JOverride
        def apply(self, o):
            v_ = GRID.get((int(o[0]), int(o[1]), int(o[2])))
            return None if v_ is None else JObject(JInt(v_), Integer)
    WRITES = []
    SETARGS = []          # fixer 2: (rotation, settings) of every setBlock

    @JImplements("java.util.function.Function")
    class SetF(object):
        @JOverride
        def apply(self, o):
            k_ = (int(o[0]), int(o[1]), int(o[2]))
            WRITES.append(k_)
            SETARGS.append((int(o[4]), int(o[5])))
            GRID[k_] = int(o[3])
            return JObject(JBoolean(True), Bool_)
    TGT = {"v": (10, 64, 10)}
    V3I = JClass("org.joml.Vector3i")

    @JImplements("java.util.function.Function")
    class TgtF(object):
        @JOverride
        def apply(self, o):
            v_ = TGT["v"]
            return None if v_ is None else V3I(JInt(v_[0]), JInt(v_[1]), JInt(v_[2]))
    Till.BLK, Till.SETB, Till.TARGET = BlkF(), SetF(), TgtF()
    Till.IDX = None
    Till.TOI = -1
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wT = us.allocateInstance(WLDc.class_)
    jf(WLDc, "name").set(wT, "skyy-island-p1")

    def hoe(id_, owner=U1, pk="p1", uid="hoehoehoehoeho01", ll=True, dur=50.0):
        d_ = Roll.newDoc(id_, JInt(0), True, "craft", JInt(10))
        if ll:
            d_ = Life.llDoc(d_, id_, owner, pk, uid, False)
        return Data.put(stack(id_), d_, None).withDurability(JDouble(dur))

    def till(b_, a_):
        WRITES[:] = []
        return int(Till.onChange(PR1, None, None, wT, b_, a_))
    Till.HIT.clear()
    reset_grid()
    n_iron = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    w_iron = sorted(WRITES)
    iron_ok = len(w_iron) == 6 and all(GRID.get(k_) == TI_ for k_ in w_iron)
    reset_grid()
    n_thor = till(hoe("Tool_Hoe_Thorium"), hoe("Tool_Hoe_Thorium", dur=49.0))
    reset_grid()
    n_crude = till(hoe("Tool_Hoe_Crude"), hoe("Tool_Hoe_Crude", dur=49.0))
    K.notes.append("G34 T3 debug: %s %s %s why=%s N=%s idx=%s toi=%s" % (n_iron, n_thor, n_crude, str(Till.LASTWHY), list(Till.N), Till.IDX is not None, int(Till.TOI)))
    K.check(SETARGS and all(a_ == (0, 256) for a_ in SETARGS) and int(Till.SETF) == 256,
            "FIX2 T1: every extra tilled block is written with the vanilla till's setBlock settings (256 = PERFORM_BLOCK_UPDATE; rotation 0 under "
            "the BLK seam): %s" % sorted(set(SETARGS)))
    K.check(n_iron == 6 and (11, 64, 10) not in w_iron and (9, 64, 9) not in w_iron and iron_ok and n_thor == 21 and n_crude == 0,
            "G34 T3: your LIFELONG hoe tills the square by tier around the tilled block: Iron 3x3 = 6 more (the block with rock above and the stone "
            "skipped), Thorium 5x5 = 21 more (+ the unloaded block skipped), Crude = only the vanilla block: %s %s %s" % (n_iron, n_thor, n_crude))
    reset_grid()
    Till.hitMark(U1)
    n_hit = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    Till.HIT.clear()
    n_d2 = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=48.0))
    n_d0 = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=50.0))
    n_plain = till(hoe("Tool_Hoe_Iron", ll=False), hoe("Tool_Hoe_Iron", ll=False, dur=49.0))
    n_other = till(hoe("Tool_Hoe_Iron", owner=U2, pk="p2"), hoe("Tool_Hoe_Iron", owner=U2, pk="p2", dur=49.0))
    n_uid = till(hoe("Tool_Hoe_Iron", uid="aaaaaaaaaaaaaaa1"), hoe("Tool_Hoe_Iron", uid="bbbbbbbbbbbbbbb2", dur=49.0))
    n_sword = till(sword(0).withDurability(JDouble(50.0)), sword(0).withDurability(JDouble(49.0)))
    TGT["v"] = (3, 64, 3)
    n_notill = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    TGT["v"] = None
    n_notgt = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    TGT["v"] = (10, 64, 10)
    PERMA["v"] = False
    np0 = int(Till.N[2])
    n_prot = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    PERMA["v"] = True
    apply(hoe__areaOn="false")
    n_off = till(hoe("Tool_Hoe_Iron"), hoe("Tool_Hoe_Iron", dur=49.0))
    apply()
    K.check([n_hit, n_d2, n_d0, n_plain, n_other, n_uid, n_sword, n_notill, n_notgt, n_off] == [-1] * 10 and n_prot == 0 and int(Till.N[2]) == np0 + 1
            and not WRITES,
            "G34 T4: no extra tilling: a block hit in the last 300 ms (left click), durability -2 / unchanged, a plain hoe, another player's lifelong hoe, "
            "another stack, a sword, the target not tilled soil, no target, hoe.areaOn off; a protected world (build FALSE) = the vanilla block only: "
            "%s %s" % ([n_hit, n_d2, n_d0, n_plain, n_other, n_uid, n_sword, n_notill, n_notgt, n_off], n_prot))
    # GearTillSys on a REAL InventoryChangeEvent (the hotbar's SlotTransaction from the engine's own setItemStackForSlot); the tools section too;
    # any other section ignored
    ICEc = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent")
    ESTc = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    invE, csE = mkinv()
    refE, stE, chE, plE = world(invE, csE, PR1)
    esE = us.allocateInstance(ESTc.class_)
    jf(ESTc, "world").set(esE, wT)
    stE.ext = esE
    csE["hotbar"].setItemStackForSlot(JShort(0), hoe("Tool_Hoe_Iron"))
    txE = csE["hotbar"].setItemStackForSlot(JShort(0), hoe("Tool_Hoe_Iron", dur=49.0))
    reset_grid()
    WRITES[:] = []
    nT0 = int(Till.N[0])
    TillSys().handle(0, chE, stE, None, ICEc(JClass(ICOMP + "Hotbar").getComponentType(), comp("Hotbar", csE["hotbar"]), csE["hotbar"], txE))
    w_sys = len(WRITES)
    csE["tools"].setItemStackForSlot(JShort(1), hoe("Tool_Hoe_Thorium"))
    txT = csE["tools"].setItemStackForSlot(JShort(1), hoe("Tool_Hoe_Thorium", dur=49.0))
    reset_grid()
    WRITES[:] = []
    TillSys().handle(0, chE, stE, None, ICEc(JClass(ICOMP + "Tool").getComponentType(), comp("Tool", csE["tools"]), csE["tools"], txT))
    w_tool = len(WRITES)
    csE["utility"].setItemStackForSlot(JShort(0), hoe("Tool_Hoe_Iron"))
    txX = csE["utility"].setItemStackForSlot(JShort(0), hoe("Tool_Hoe_Iron", dur=49.0))
    reset_grid()
    WRITES[:] = []
    TillSys().handle(0, chE, stE, None, ICEc(JClass(ICOMP + "Utility").getComponentType(), comp("Utility", csE["utility"]), csE["utility"], txX))
    w_util = len(WRITES)
    K.check(w_sys == 6 and w_tool == 21 and w_util == 0 and int(Till.N[0]) == nT0 + 2,
            "G34 T5: GearTillSys on REAL InventoryChangeEvents (the engine's own SlotTransaction before / after, world from the EntityStore): a hotbar "
            "Iron hoe till = 6 extra blocks, a tools-section Thorium hoe = 21, a utility-section change = ignored: %s %s %s" % (w_sys, w_tool, w_util))
    Till.BLK = None
    Till.SETB = None
    Till.TARGET = None
    Till.PERM = None
    Till.IDX = None
    Till.TOI = -1
    st34 = str(Sig.statusText()) + " | " + str(ArmLv.statusText()) + " | " + str(Till.statusText())
    with zipfile.ZipFile(JAR) as zj_:
        man34 = zj_.read("manifest.json").decode("utf-8")
    K.check("sigils on" in st34 and "gathering armor levels with the skill" in st34 and "hoe till area on" in st34 and "SIGILS (Unique .. Mythic)" in man34
            and "tills a bigger square" in man34, "G34: the status texts + the manifest sentence: %s" % st34[:200])
    # ============================================================================ G35 (0.3.5): VAULT SUMMON, HANDS = CRUDE, THE REVEAL, THE POLE, REBIRTH R7
    Integer_ = JClass("java.lang.Integer")
    Rb = JClass(PKG + "GearRb")
    Ident = JClass(PKG + "GearIdent")
    Unid = JClass(PKG + "GearUnid")
    Pool = JClass(PKG + "GearPool")
    ArmLvC = JClass(PKG + "GearArmLv")
    TRUE_, FALSE_ = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE

    def obj(*xs):
        return JArray(JObject)([x if not isinstance(x, int) or isinstance(x, bool) else JObject(JInt(x), Integer_) for x in xs])

    def logs_has(ls_, *parts):
        return [l_ for l_ in ls_ if all(p_ in l_ for p_ in parts)]

    # ---------------------------------------------------------------- V: VAULT SUMMON (a stand-in of SkyyVault 0.1.6's four functions + its
    # pending records and its start-up resolve - the Vault's own proof is SkyyVault/test_skyyvault_0.1.6.py; here gear's calls are executed)
    VA = {"slots": {}, "pend": {}, "placed": {}, "orph": [], "tok": 0, "calls": [], "find": None, "take": None, "done": True, "pb": "+", "lie": False}

    def va_key(st_):
        d_ = doc(st_)
        return None if d_ is None else (str(LL.uid(d_)), str(LL.owner(d_)))

    @JImplements("java.util.function.Function")
    class VFind(object):
        @JOverride
        def apply(self, o):
            VA["calls"].append("find")
            if VA["find"] == "!throw":
                raise RuntimeError("a Vault bug")
            if VA["find"] is not None:
                return JString(VA["find"])
            want_ = (str(o[2]), str(o[1]))
            for at_, st_ in VA["slots"].items():
                if va_key(st_) == want_:
                    return JString(at_)
            for tok_, (st_, at_) in VA["pend"].items():
                if va_key(st_) == want_:
                    return JString("!pending")
            return None

    @JImplements("java.util.function.Function")
    class VTake(object):
        @JOverride
        def apply(self, o):
            VA["calls"].append("take")
            if VA["take"] is not None:
                return JString(VA["take"])
            want_ = (str(o[2]), str(o[1]))
            for at_, st_ in list(VA["slots"].items()):
                if va_key(st_) == want_:
                    del VA["slots"][at_]
                    VA["tok"] += 1
                    tok_ = "tok%d" % VA["tok"]
                    VA["pend"][tok_] = (st_, at_)
                    give_ = stack("Tool_Pickaxe_Crude") if VA["lie"] else st_
                    return JArray(JObject)([JString(tok_), give_, JString(at_)])
            return JString("-not in the vault")

    @JImplements("java.util.function.Function")
    class VDone(object):
        @JOverride
        def apply(self, o):
            VA["calls"].append("done")
            tok_ = str(o[1])
            if not VA["done"] or tok_ not in VA["pend"]:
                return FALSE_
            VA["placed"][tok_] = VA["pend"].pop(tok_)
            return TRUE_

    @JImplements("java.util.function.Function")
    class VBack(object):
        @JOverride
        def apply(self, o):
            VA["calls"].append("back")
            tok_ = str(o[1])
            if VA["pb"] == "-" or tok_ not in VA["pend"]:
                return JString("-not now")
            st_, at_ = VA["pend"].pop(tok_)
            if VA["pb"] == "=":
                VA["orph"].append(st_)
                return JString("=full")
            VA["slots"][at_] = st_
            return JString("+" + at_)

    def va_restart(cs_):
        """SkyyVault 0.1.6 at a start: every pending record and every 'placed' note younger than 30 s is resolved - the tool in the SAVED
        inventory closes it, else it goes back into the Vault"""
        here_ = set(x[3] for x in lls(cs_))
        for tok_, (st_, at_) in list(VA["pend"].items()) + list(VA["placed"].items()):
            if va_key(st_)[0] not in here_:
                VA["slots"][at_] = st_
        VA["pend"].clear()
        VA["placed"].clear()

    def va_count(cs_, uid_):
        return len([x for x in lls(cs_) if x[3] == uid_]) + len([1 for st_ in list(VA["slots"].values()) + VA["orph"] if va_key(st_)[0] == uid_])
    for k_, f_ in (("vault:fn:findLL", VFind()), ("vault:fn:takeLL", VTake()), ("vault:fn:doneLL", VDone()), ("vault:fn:putBack", VBack())):
        br.put(k_, f_)
    apply(lifelong__reclaimSec="0")

    def va_setup():
        VA.update({"slots": {}, "pend": {}, "placed": {}, "orph": [], "calls": [], "find": None, "take": None, "done": True, "pb": "+", "lie": False})
        inv_, cs_, ref_, st_, pl_ = setup_lt()
        a_ = pick_now(cs_)[0]
        VA["slots"]["1:3"] = a_[6]
        cs_[a_[0]].removeItemStackFromSlot(JShort(a_[1]))
        return inv_, cs_, pl_, a_
    # V1 the closed Vault hands the exact tool back: find -> take -> place (read back) -> done
    invV, csV, plV, AV = va_setup()
    n18 = int(Life.N[18])
    logs()
    rV1 = str(Life.reclaimW(PR1, plV, JInt(0), None))
    lgV1 = logs()
    K.check(rV1.startswith("+") and "came back from your Vault" in rV1 and [x[3] for x in pick_now(csV)] == [AV[3]] and not VA["slots"] and not VA["pend"]
            and len(VA["placed"]) == 1 and VA["calls"] == ["find", "take", "done"] and int(Life.N[18]) == n18 + 1
            and logs_has(lgV1, "LL-SUMMON ", "from the Vault 1:3") and str(Data.str(doc(pick_now(csV)[0][6]), "r", "")) == "legendary"
            and regfile("p1").get("pickaxe.uid") == AV[3] and va_count(csV, AV[3]) == 1,
            "G35 V1: /pickaxe with the tool in a CLOSED Vault: findLL -> takeLL -> the stack in a free slot (read back) -> doneLL; the EXACT tool (same uid, "
            "Legendary) - no copy, one stack in all: %s | calls %s" % (rV1, VA["calls"]))
    # V2 / V3 / V4: a take still open, an unreadable vault, a refused take = try again - NEVER an exact copy
    outs = []
    for mode_, val_ in (("find", "!pending"), ("find", "!unreadable"), ("take", "-busy")):
        invV, csV, plV, AV = va_setup()
        VA[mode_] = val_
        n17 = int(Life.N[17])
        r_ = str(Life.reclaimW(PR1, plV, JInt(0), None))
        outs.append((val_, r_, len(pick_now(csV)), int(Life.N[17]) - n17, "1:3" in VA["slots"], regfile("p1").get("pickaxe.reclaimAt")))
    K.check(outs[0][1].startswith("-") and "on its way" in outs[0][1] and outs[1][1].startswith("-") and "cannot be read" in outs[1][1]
            and outs[2][1].startswith("-") and "could not come out right now (busy)" in outs[2][1]
            and all(o_[2] == 0 and o_[3] == 0 and o_[4] and o_[5] is None for o_ in outs),
            "G35 V2-V4: '!pending' / '!unreadable' / a refused take = a 'try again' line, nothing moved, NO exact copy (N[17] unchanged, no reclaimAt): %s" % outs)
    # V5 the stack could not be placed (here: the Vault handed out another stack) -> putBack: '+' back in its slot / '=' Vault full / '-' resolves itself
    outs = []
    for pb_ in ("+", "=", "-"):
        invV, csV, plV, AV = va_setup()
        VA["lie"] = True
        VA["pb"] = pb_
        r_ = str(Life.reclaimW(PR1, plV, JInt(0), None))
        outs.append((pb_, r_, VA["calls"][-1], len(pick_now(csV)), sorted(VA["slots"]), len(VA["orph"]), len(VA["pend"])))
    K.check(outs[0][1].startswith("-") and "stayed in your Vault" in outs[0][1] and outs[0][4] == ["1:3"]
            and "Vault is full" in outs[1][1] and outs[1][5] == 1 and "by itself" in outs[2][1] and outs[2][6] == 1
            and all(o_[2] == "back" and o_[3] == 0 for o_ in outs),
            "G35 V5: a stack that is not the tool / could not be placed -> putBack, never kept: + back in its slot, = kept by the Vault (full), - the "
            "Vault resolves it: %s" % outs)
    # V6 doneLL answers FALSE: the tool IS here (success), the line is logged
    invV, csV, plV, AV = va_setup()
    VA["done"] = False
    logs()
    rV6 = str(Life.reclaimW(PR1, plV, JInt(0), None))
    K.check(rV6.startswith("+") and logs_has(logs(), "LL-VAULT-DONE-UNCONFIRMED") and len(pick_now(csV)) == 1,
            "G35 V6: doneLL FALSE = still fetched (the Vault closes the take by itself), LL-VAULT-DONE-UNCONFIRMED logged: %s" % rV6)
    # V7 THE CRASH POINTS (10 after the take, 11 after the place, 12 after doneLL) x the engine saved the inventory or not -> the Vault's start-up
    # resolve + one more /pickaxe: exactly ONE stack of the tool (inventory + Vault), the registry uid unchanged, never an exact copy
    crashes = []
    for step_ in (10, 11, 12):
        for saved_ in (True, False):
            invV, csV, plV, AV = va_setup()
            snap_ = snapshot(csV)
            Life.CRASH_AT = step_
            crashed_ = False
            try:
                Life.reclaimW(PR1, plV, JInt(0), None)
            except Exception as ex_:
                crashed_ = ("lifelong step %d" % step_) in str(ex_)
            Life.CRASH_AT = 0
            if not saved_:
                restore_inv(csV, snap_)
            va_restart(csV)
            reset_reg()
            LL.LAST.clear()
            Life.sweep0(PR1, invV, True)
            n17 = int(Life.N[17])
            if not pick_now(csV):
                Life.reclaimW(PR1, plV, JInt(0), None)
            crashes.append((step_, saved_, crashed_, va_count(csV, AV[3]), [x[3] for x in pick_now(csV)] == [AV[3]], int(Life.N[17]) - n17,
                            regfile("p1").get("pickaxe.uid") == AV[3]))
    K.check(all(c_[2] and c_[3] == 1 and c_[4] and c_[5] == 0 and c_[6] for c_ in crashes),
            "G35 V7: a crash at every Vault step (10 / 11 / 12), the inventory saved or not, a restart (the Vault resolves its open take) and /pickaxe "
            "again: exactly one stack, the exact tool in the inventory, no copy, the registry unchanged: %s" % crashes)
    # V9 (FIX ROUND 2, critic A4): findLL THROWS -> "could not be checked - try again", never the chest / copy path
    invV, csV, plV, AV = va_setup()
    VA["find"] = "!throw"
    n17 = int(Life.N[17])
    rV9 = str(Life.reclaimW(PR1, plV, JInt(0), None))
    K.check(rV9.startswith("-The Vault could not be checked") and int(Life.N[17]) == n17 and not pick_now(csV) and "1:3" in VA["slots"]
            and VA["calls"] == ["find"] and regfile("p1").get("pickaxe.reclaimAt") is None,
            "G35 V9 FIX 2 (critic A4): findLL throwing = 'the Vault could not be checked - try again': no exact copy (N[17] unchanged), the tool stays "
            "in the Vault: %s | %s" % (rV9, VA["calls"]))
    # V10 (FIX ROUND 2, critic A5): the slot TOOK the tool but it did not read back -> out of the slot again, THEN putBack: one stack in all
    invV, csV, plV, AV = va_setup()
    Life.TEST_NOREAD = True
    logs()
    rV10 = str(Life.reclaimW(PR1, plV, JInt(0), None))
    Life.TEST_NOREAD = False
    K.check(rV10.startswith("-") and "stayed in your Vault" in rV10 and VA["calls"] == ["find", "take", "back"] and not pick_now(csV)
            and VA["slots"].get("1:3") is not None and va_count(csV, AV[3]) == 1 and not logs_has(logs(), "LL-VAULT-KEPT"),
            "G35 V10 FIX 2 (critic A5): placed but not read back -> taken out of the slot BEFORE putBack: nothing left in the inventory, the tool back "
            "in its Vault slot, exactly ONE stack: %s | %s" % (rV10, VA["calls"]))
    # V8 no SkyyVault 0.1.6 = the 0.3.4 path (an exact copy)
    for k_ in ("vault:fn:findLL", "vault:fn:takeLL", "vault:fn:doneLL", "vault:fn:putBack"):
        br.remove(k_)
    invV, csV, plV, AV = va_setup()
    rV8 = str(Life.reclaimW(PR1, plV, JInt(0), None))
    K.check(rV8.startswith("+") and "exact copy" in rV8 and VA["calls"] == [], "G35 V8: without SkyyVault 0.1.6 the old path runs (an exact copy): %s" % rV8)
    apply()

    # ---------------------------------------------------------------- H: HANDS COUNT AS CRUDE ON CROPS (Skyy 2026-10-14 popup)
    pf_.set(PR1, ph_)
    toasts()
    nH0 = int(LL.N[0])

    def hitp(s_, bid_):
        POPD.clear()
        return hitb(s_, bid_)
    hP = hitp(None, CROPB["Potato"][0])
    tP_ = toasts()
    hS = hitp(stack("Weapon_Sword_Iron"), CROPB["Cauliflower"][0])
    tS_ = toasts()
    hX = hitp(stack("Tool_Pickaxe_Iron"), CROPB["Potato"][0])
    hC = hitp(None, CROPB["Carrot"][0])
    hW = hitp(None, CROPB["Wheat"][0])
    toasts()
    uP = useb(None, CROPB["Potato"][0])
    uS = useb(stack("Weapon_Sword_Iron"), CROPB["Pumpkin"][0])
    uC = useb(None, CROPB["Carrot"][0])
    uB = useb(None, berry[0]) if berry else (False, [])
    nH1 = int(LL.N[0])
    ftH = [int(LL.farmTier(CROPB[w_][0], h_)) for w_, h_ in (("Potato", None), ("Carrot", None), ("Wheat", None), ("Potato", "Weapon_Sword_Iron"),
                                                            ("Potato", "Tool_Hoe_Thorium"), ("Carrot", "Tool_Pickaxe_Iron"))]
    apply(gate__on="false")
    hOff = hitb(None, CROPB["Potato"][0])
    uOff = useb(None, CROPB["Potato"][0])
    apply()
    toasts()
    pf_.set(PR1, old_ph)
    WTH = ("Too tough for your bare hands", "This crop needs at least an Iron hoe (Thorium for full Farming XP). Tier yours up on the Anvil (/smithing).")
    K.check(hP[0] and tP_ == [WTH] and hS[0] and tS_ and tS_[0][0] == "Too tough for your " + str(Gear.itemName("Weapon_Sword_Iron")) and hX[0]
            and not hC[0] and abs(hC[1] - 0.3 * 0.4) < 1e-6 and not hW[0] and abs(hW[1] - 0.3) < 1e-6,
            "G35 H1: the left-click on the REAL GearToolHitSys: a Potato by hand / Cauliflower with a sword / a Potato with a pickaxe (two up from Crude) = "
            "CANCELLED + 'Too tough for your bare hands'; a Carrot by hand (one up) x0.4; Wheat by hand = vanilla: %s %s %s %s %s | %s %s"
            % (hP, hS, hX, hC, hW, tP_, tS_[:1]))
    K.check(uP[0] and uP[1] == [WTH] and uS[0] and not uC[0] and not uB[0] and nH1 - nH0 == 5,
            "G35 H2: the F-harvest on the REAL UseBlockEvent$Pre: an empty hand on a Potato / a sword on a Pumpkin = CANCELLED (+ the popup); a Carrot by "
            "hand (one up) and a berry plant pass; N[0] +5: %s %s %s %s +%d" % (uP, uS, uC, uB, nH1 - nH0))
    K.check(ftH == [2, 1, 0, 2, 0, 1] and not hOff[0] and not uOff[0] and "hands count as Crude on crops" in str(LL.statusText()),
            "G35 H3: gear:fn:farmTier for a hand / a sword = the Crude hoe's answers (Potato 2, Carrot 1 = half XP, Wheat 0; a Thorium hoe 0); gate.on "
            "off = hands free again; statusText says so: %s" % ftH)

    # ---------------------------------------------------------------- R: THE IDENTIFY REVEAL (explore:fn:reveal stand-in, the REAL Anvil clicks)
    RVL = {"calls": [], "ans": True}

    @JImplements("java.util.function.Function")
    class Reveal(object):
        @JOverride
        def apply(self, o):
            RVL["calls"].append((str(o[0]), str(o[1]), str(o[2]), [str(c_) for c_ in o[3]], str(o[4])))
            return TRUE_ if RVL["ans"] else FALSE_
    br.put("explore:fn:reveal", Reveal())
    invI, csI = mkinv()
    refI, stI, chI, plI = world(invI, csI, PR1)
    PKEY[str(U1)] = "p1"
    skills(Mining=20, Foraging=20, Farming=20)
    tyS = int(Pool.typeOfId("Weapon_Sword_Iron"))
    bagI = Unid.make(JInt(tyS), JInt(0), JInt(3), JInt(10), JInt(14), "test", "test", JInt(0))
    csI["hotbar"].setItemStackForSlot(JShort(0), bagI)
    csI["hotbar"].setItemStackForSlot(JShort(1), sword(1, ident=False))
    pgI = FRP(PR1)

    def clickI(a_):
        pgI.lastForge = JLong(0)
        pgI.handleDataEvent(refI, stI, '{"a":"%s"}' % a_)
        return str(pgI.info)
    pgI.anPick(invI, 0, 0)
    rv0 = RV0 = [int(x) for x in Ident.RV]
    iB = clickI("id")
    c1 = list(RVL["calls"])
    gotB = csI["hotbar"].getItemStack(JShort(0))
    cb = c1[0][3][0].split("|") if c1 and c1[0][3] else []
    K.check(iB.startswith("+It was ") and len(c1) == 1 and c1[0][0] == str(U1) and c1[0][1] == "Identified!" and c1[0][4] == "reforge" and len(cb) == 7
            and cb[0] == str(gotB.getItemId()) and cb[2].startswith("Lv ") and cb[2].endswith(" - Legendary") and cb[3] == "#55FFFF" and cb[4] == "2"
            and cb[5] == str(bagI.getItemId()) and cb[6] == str(Gear.itemName(str(bagI.getItemId()))),
            "G35 R1: the Anvil's Identify on a Legendary mystery bag (the REAL ReforgePage.anId) -> explore:fn:reveal(uuid, 'Identified!', sub, ONE card "
            "'id|name|Lv N - Legendary|#55FFFF|2|<the bag>|<bag name>', 'reforge' = FIX 3.4 the Anvil's Back) AFTER the swap (the item is in the slot): %s | %s" % (iB, c1))
    pgI.anPick(invI, 0, 1)
    iS = clickI("id")
    c2 = RVL["calls"][1:]
    cs2 = c2[0][3][0].split("|") if c2 else []
    K.check(iS.startswith("+Identified your") and len(c2) == 1 and len(cs2) == 7 and cs2[4] == "0" and cs2[5] == "Weapon_Sword_Iron"
            and cs2[6] == "Unidentified " + str(Gear.itemName("Weapon_Sword_Iron")) and cs2[3] == "#FFFF55",
            "G35 R2: an unidentified sword -> one card, cover = the item itself 'Unidentified <name>', Unique = #FFFF55 rank 0: %s" % c2)
    # re-identify the bag's item: arm + confirm -> 'Re-identified!' with the old item as the cover
    pgI.anPick(invI, 0, 0)
    oldId = str(csI["hotbar"].getItemStack(JShort(0)).getItemId())
    clickI("rr")
    iR = clickI("rr")
    c3 = RVL["calls"][2:]
    K.check(iR.startswith("+It is now") and len(c3) == 1 and c3[0][1] == "Re-identified!" and c3[0][3][0].split("|")[5] == oldId,
            "G35 R3: re-identify -> 'Re-identified!' with the item before as the cover: %s | %s" % (iR, c3))
    # Identify all: 12 bags of mixed rarity -> at most 10 cards, the best LAST (rank ascending)
    invA, csA = mkinv()
    refA, stA, chA, plA = world(invA, csA, PR1)
    for i_ in range(12):
        csA["storage"].setItemStackForSlot(JShort(i_), Unid.make(JInt(tyS), JInt(0), JInt([0, 2, 3, 1][i_ % 4]), JInt(10), JInt(14), "test", "test", JInt(0)))
    pgA = FRP(PR1)
    RVL["calls"] = []
    pgA.lastForge = JLong(0)
    nSaid = len(said(PR1))
    pgA.handleDataEvent(refA, stA, '{"a":"idall"}')
    iA = str(pgA.info)
    cA = RVL["calls"]
    sdA = said(PR1)[nSaid:]
    rk = [int(c_.split("|")[4]) for c_ in cA[0][3]] if cA else []
    K.check(iA.startswith("+Identified 12 items") and len(cA) == 1 and cA[0][1] == "Identified 12 items!" and len(rk) == 10 and rk == sorted(rk) and rk[-1] == 2,
            "G35 R4: Identify all (12 bags) -> ONE reveal with the 10 best cards, sorted so the best flips last: %s | ranks %s" % (iA, rk))
    K.check(cA and cA[0][2].startswith("Showing your 10 best of 12") and cA[0][4] == "reforge" and any(x.startswith("[Identify] Identified 12 items") for x in sdA),
            "G35 R4 FIX 3.4: more than 10 -> the subtitle says 'Showing your 10 best of 12'; Back = /reforge (the Anvil); the page's result line goes to "
            "chat (the reveal page replaces the page): %s | %s" % (cA[0][2] if cA else None, sdA))
    # FALSE (switched off / offline) and no SkyyExploration: the page line is unchanged, nothing else happens
    RVL["ans"] = False
    csI["hotbar"].setItemStackForSlot(JShort(2), sword(2, ident=False))
    pgI.anPick(invI, 0, 2)
    iF = clickI("id")
    br.remove("explore:fn:reveal")
    csI["hotbar"].setItemStackForSlot(JShort(3), sword(2, ident=False))
    pgI.anPick(invI, 0, 3)
    iN = clickI("id")
    rv1 = [int(x) for x in Ident.RV]
    K.check(iF.startswith("+Identified your") and iN.startswith("+Identified your") and rv1[0] - RV0[0] == 6 and rv1[1] - RV0[1] == 4 and rv1[2] - RV0[2] == 2,
            "G35 R5: reveal FALSE / no SkyyExploration = the Anvil's own result line as before (asked 6, shown 4, not shown 2): %s %s %s" % (iF, iN, rv1))
    # the Identify page (IdentifyPage.one) asks the same way (the class compare + this call)
    br.put("explore:fn:reveal", Reveal())
    RVL["ans"] = True
    RVL["calls"] = []
    resI = [Integer_.valueOf(1), "x", stack("Weapon_Sword_Iron"), None, Roll.newDoc("Weapon_Sword_Iron", JInt(5), True, "craft", JInt(12))]
    okI = bool(Ident.revealOne(U1, JArray(JObject)(resI), "Skyy_Unid_Bag_X", False, Ident.backFor(None)))
    bk0 = RVL["calls"][0][4] if RVL["calls"] else None
    apply(identify__command="false")
    bkOff = Ident.backFor(None)
    bkAnv = Ident.backFor(pgA)
    apply()
    K.check(bk0 == "identify" and bkOff is None and str(bkAnv) == "reforge",
            "G35 R6 FIX 3.4: the reveal's Back: the Identify page = /identify (identify.command on) / none (off - /identify would say 'switched off'); "
            "the Anvil = /reforge: %s %s %s" % (bk0, bkOff, bkAnv))
    K.check(okI and RVL["calls"] and RVL["calls"][0][3][0].split("|")[3] == "#CC66CC" and RVL["calls"][0][3][0].split("|")[4] == "2"
            and not bool(Ident.revealOne(U1, JArray(JObject)([Integer_.valueOf(1), "x", None, None, None]), "a", False, None)),
            "G35 R6: revealOne: a Mythic card is #CC66CC rank 2; a result without the new stack = no call: %s" % RVL["calls"][:1])
    br.remove("explore:fn:reveal")
    RVL["calls"] = []

    # ---------------------------------------------------------------- P: THE LIFELONG FISHING POLE (SkyyFishing 0.1.5's rods loaded as a pack)
    RODS = ["SkyyFishing_Rod_Bamboo", "SkyyFishing_Rod_Copper", "SkyyFishing_Rod_Iron"]
    K.check(all(Gear.item(r_) is not None for r_ in RODS),
            "G35 P0: SkyyFishing 0.1.5 loaded as its own pack: the rods are real items (failed stores in this bare boot: %s - not the rods)" % ffail)
    K.check(int(LL.kOf("SkyyFishing_Rod_Iron")) == 4 and str(LL.KIND[4]) == "pole" and str(LL.KCRUDE[4]) == "SkyyFishing_Rod_Bamboo" and bool(LL.isPole("SkyyFishing_Rod_Copper"))
            and int(LL.tier("SkyyFishing_Rod_Iron")) == 2 and int(LL.tier("SkyyFishing_Rod_Bamboo")) == 0 and int(LL.kOf("SkyyFishing_Reel_Iron")) == -1
            and not any(bool(LL.perkFor(JInt(4), JInt(p_))) for p_ in range(len(LL.PK))) and list(LL.RBNODE)[4] == "Fishing" and list(LL.RBSFX) == [".tool", ".tool2"],
            "G35 P1: the 5th kind 'pole' = SkyyFishing_Rod_<Tier> (Wooden = Crude = tier 0, Iron = 2), reels are no kind, no perks yet, rebirth nodes "
            "Fishing.tool + Fishing.tool2 (FIX 2.1)")
    skills(Fishing=7)
    lvP = [int(LL.levelFor(U1, r_)) for r_ in RODS]
    br.remove("skill:fn:level")
    Gate.forget(U1)
    lvN = int(LL.levelFor(U1, "SkyyFishing_Rod_Copper"))
    br.put("skill:fn:level", SkillFn())
    Gate.forget(U1)
    K.check(all(1 <= x_ <= 7 for x_ in lvP) and lvN == -1, "G35 P1: the pole's level = Fishing capped by the rod's band (Fishing 7 -> %s); no SkyySkills = -1" % lvP)
    # P2 Marlow's pole: gear:fn:pole stamps it for the active profile (same uid on every retry); the registry is NOT written by the call
    wipe_home()
    invP2, csP2 = mkinv()
    refP2, stP2, chP2, plP2 = world(invP2, csP2, PR1)
    PKEY[str(U1)] = "p1"
    Life.sweep0(PR1, invP2, True)          # the four tools (a first join)
    Fn3 = JClass(PKG + "GearLLFn")(JInt(3))
    g1 = "p1:fishing_intro.take_pole:1"
    sA = Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), JString(g1)))
    sB = Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), JString(g1)))
    dA = doc(sA)
    mdA = [str(k_) for k_ in sA.getMetadata().keySet()]
    K.check(dA is not None and bool(LL.isLL(dA)) and str(LL.owner(dA)) == "p1" and str(LL.uid(dA)) == str(LL.uid(doc(sB))) and str(Data.str(dA, "lgr", "")) == g1
            and mdA == ["SkyyGear"] and regfile("p1").get("pole.uid") is None and str(LL.uid(dA)) == str(Life.poleUid("p1", g1)),
            "G35 P2: gear:fn:pole stamps the rod lifelong for the claim's profile: ll 1, lo p1, uid = hash(profile, grant) - the SAME on a retry, lgr = "
            "the grant; only the SkyyGear key is written (no tooltip / view - SkyyFishing owns the rod's look); the registry is untouched: %s" % mdA)
    sP = stack("Rock_Stone")
    K.check(Fn3.apply(obj(U1, sP, JString(g1))) == sP and Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), None)) is not None
            and doc(Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), JString("")))) is None,
            "G35 P2: not a rod / no grant = the stack back unchanged (never null)")
    # P3 it arrives (SkyyQuests gives it storage-first) -> the sweep adopts it (ONE registry write)
    csP2["storage"].setItemStackForSlot(JShort(20), sA)
    logs()
    nw0 = int(LL.N[5])
    LL.LAST.clear()
    Life.sweep0(PR1, invP2, True)
    rfP = regfile("p1")
    K.check(rfP.get("pole.uid") == str(LL.uid(dA)) and rfP.get("pole.id") == "SkyyFishing_Rod_Bamboo" and logs_has(logs(), "LL-POLE-ADOPT")
            and int(LL.N[5]) - nw0 >= 1 and any("lifelong pole now" in x for x in said(PR1)) and int(LL.hereMask(LL.HERE.get(U1), "p1")) & 16,
            "G35 P3: the arriving pole is adopted at the next look (pole.uid / pole.id, one write, a chat line, HERE bit 16): %s" % dict((k_, v_) for k_, v_ in rfP.items() if k_.startswith("pole")))
    # P4 ONCE: a second Marlow claim (another grant) stays a plain rod; a second lifelong pole of the profile is retired
    sC = Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), JString("p1:fishing_intro.take_pole:2")))
    K.check(doc(sC) is None and logs_has(logs(), "LL-POLE-PLAIN"), "G35 P4: a profile that has its pole gets a PLAIN rod from another claim (LL-POLE-PLAIN)")
    sSame = Fn3.apply(obj(U1, stack("SkyyFishing_Rod_Bamboo"), JString(g1)))
    K.check(doc(sSame) is None and regfile("p1").get("pole.uid") == str(LL.uid(dA)),
            "G35 P4 FIX 1.1: once the pole is adopted, a repeat of the SAME grant (an admin repay while the pole sits in a chest) is a PLAIN rod - no "
            "second same-uid stack that could replace an upgraded pole")
    # P5 can't be dropped / sold: the 0.3.0 rules see it
    K.check(bool(LL.llStack("SkyyFishing_Rod_Bamboo", sA.getMetadata())) and Wall.why("SkyyFishing_Rod_Bamboo", sA.getMetadata()) is not None,
            "G35 P5: the pole is a lifelong stack (GearLLDropSys keeps it, the market wall refuses it): %s" % Wall.why("SkyyFishing_Rod_Bamboo", sA.getMetadata()))
    # P6 /pole: lost -> an exact copy of the pole (its snapshot); no pole -> 'Marlow gives you one'
    apply(lifelong__reclaimSec="0")
    pP = [x for x in lls(csP2, "p1") if x[2] == 4][0]
    csP2[pP[0]].removeItemStackFromSlot(JShort(pP[1]))
    rP6 = str(Life.reclaimW(PR1, plP2, JInt(4), None))
    cP6 = [x for x in lls(csP2, "p1") if x[2] == 4]
    wipe_home()
    invP7, csP7 = mkinv()
    refP7, stP7, chP7, plP7 = world(invP7, csP7, PR1)
    Life.sweep0(PR1, invP7, True)
    rP7 = str(Life.reclaimW(PR1, plP7, JInt(4), None))
    apply()
    K.check(rP6.startswith("+") and "exact copy" in rP6 and len(cP6) == 1 and str(cP6[0][6].getItemId()) == "SkyyFishing_Rod_Bamboo"
            and rP7.startswith("-You have no fishing pole yet - Marlow") and "hold it and type /lifelong" in rP7,
            "G35 P6: /pole: the lost pole comes back as an exact copy (no Vault / chest / Requip has it); a profile with no pole hears where to get one: %s | %s" % (rP6, rP7))
    # P7 /lifelong on a held rod while there is no pole: FIX ROUND 2 (critic C2) only MARLOW'S rod (his quest's grant, read through SkyyFishing's
    # fishing:fn:grantOf; here one claimed before 0.3.5 and upgraded at the bench) - a crafted plain rod is refused
    FBr0, FRig0 = JClass("com.skyy.fishing.FishBridge"), JClass("com.skyy.fishing.FishRig")
    FBr0.questInit()          # SkyyFishing publishes fishing:fn:grantOf (as on a real start)
    csP7["hotbar"].setItemStackForSlot(JShort(0), stack("SkyyFishing_Rod_Copper"))
    rP7p = str(Life.repick(PR1, plP7))
    rf7p = regfile("p1")
    K.check(rP7p.startswith("-Only the fishing pole from Marlow's quest") and rf7p.get("pole.uid") is None and doc(csP7["hotbar"].getItemStack(JShort(0))) is None,
            "G35 P7 FIX 2 (critic C2): /lifelong on a CRAFTED plain rod is refused (Skyy: the pole comes from a quest) - nothing written: %s" % rP7p)
    st7 = FRig0.starter(JString("p1:fishing_intro.take_pole:0"))          # a pole Marlow gave BEFORE 0.3.5 (no SkyyGear stamp), upgraded at the bench
    csP7["hotbar"].setItemStackForSlot(JShort(0), FRig0.withRigG(stack("SkyyFishing_Rod_Copper"), FRig0.rigOf(st7), FRig0.str(FRig0.doc(st7), "grant")))
    rP8 = str(Life.repick(PR1, plP7))
    rf8 = regfile("p1")
    K.check(rP8.startswith("+") and "lifelong fishing pole now" in rP8 and "levels with Fishing" not in rP8 and rf8.get("pole.id") == "SkyyFishing_Rod_Copper" and rf8.get("pole.repick") == "1"
            and bool(LL.isLL(doc(csP7["hotbar"].getItemStack(JShort(0))))),
            "G35 P7: /lifelong on a held Copper rod from Marlow's quest (his grant) with no pole yet = the lifelong pole (once): %s" % rP8)
    # P8 END TO END with the REAL SkyyFishing 0.1.5: fishing:fn:starter -> starterG -> gear:fn:pole (this jar) -> a stamped Wooden rod with the
    # lifelong line; the bench upgrade carries the SkyyGear document (FishRig.carryGear)
    Life.sweep0(PR1, invP7, True)
    FBr, FRig, FQ = JClass("com.skyy.fishing.FishBridge"), JClass("com.skyy.fishing.FishRig"), JClass("com.skyy.fishing.FishQuestFn")
    FBr.questInit()
    br.put("gear:fn:pole", Fn3)
    wipe_home()
    invP9, csP9 = mkinv()
    refP9, stP9, chP9, plP9 = world(invP9, csP9, PR1)
    Life.sweep0(PR1, invP9, True)
    g9 = "p1:fishing_intro.take_pole:9"
    st9 = br.get("fishing:fn:starter").apply(obj(U1, JString(g9)))
    st9b = br.get("fishing:fn:starter").apply(obj(U1, JString(g9)))
    js9 = str(st9.getMetadata().toJson())
    d9 = doc(st9)
    up9 = FRig.withRigG(FRig.carryGear(stack("SkyyFishing_Rod_Copper"), st9), FRig.rigOf(st9), FRig.str(FRig.doc(st9), "grant"))
    K.check(str(st9.getItemId()) == "SkyyFishing_Rod_Bamboo" and bool(LL.isLL(d9)) and str(LL.uid(d9)) == str(LL.uid(doc(st9b))) and "Lifelong fishing pole" in js9
            and "A gift from Marlow" in js9 and str(br.get("fishing:fn:grantOf").apply(st9)) == g9 and int(FQ.STAMPED) >= 2
            and str(LL.uid(doc(up9))) == str(LL.uid(d9)) and "Lifelong fishing pole" in str(up9.getMetadata().toJson()) and str(up9.getItemId()) == "SkyyFishing_Rod_Copper",
            "G35 P8: END TO END with the REAL SkyyFishing 0.1.5: Marlow's maker asks gear:fn:pole -> a stamped Wooden rod (same uid on a retry, the "
            "lifelong + gift lines, the grant still readable by SkyyQuests' guard); the bench upgrade keeps the same lifelong document on the Copper rod")
    csP9["storage"].setItemStackForSlot(JShort(4), up9)
    LL.LAST.clear()
    Life.sweep0(PR1, invP9, True)
    K.check(regfile("p1").get("pole.uid") == str(LL.uid(d9)) and regfile("p1").get("pole.id") == "SkyyFishing_Rod_Copper",
            "G35 P8: the upgraded pole is adopted with its new tier (pole.id = the Copper rod)")
    br.remove("gear:fn:pole")

    # ---------------------------------------------------------------- RB: REBIRTH R7 (the participant + the world-thread apply)
    def rb(op_, tx_, n_=1, pk_="p1"):
        return str(Rb().apply(obj(JString(op_), JString(pk_), JString(tx_), n_, JString(""))))
    TX1, TX2, TX3 = "tx1760000000001-a1b2c3", "tx1760000000002-a1b2c4", "tx1760000000003-a1b2c5"

    def rb_setup():
        inv_, cs_, ref_, st_, pl_ = setup_lt()          # a Legendary Iron pickaxe + 1 Fortune point spent
        skills(Mining=20, Foraging=20, Farming=20, Fishing=9)
        cs_["armor"].setItemStackForSlot(JShort(0), Data.put(stack("Armor_Iron_Head"), Roll.newDoc("Armor_Iron_Head", JInt(2), True, "craft", JInt(15)), None))
        cs_["storage"].setItemStackForSlot(JShort(30), Data.put(stack("Armor_Cobalt_Chest"), Roll.newDoc("Armor_Cobalt_Chest", JInt(3), True, "craft", JInt(26)), None))
        hz_ = [x for x in lls(cs_, "p1") if x[2] == 1][0]          # the hatchet: in a chest during the rebirth (RB6)
        cs_["storage"].setItemStackForSlot(JShort(31), Fn3.apply(obj(U1, FRig.withRigG(stack("SkyyFishing_Rod_Copper"), FRig.freshRig("SkyyFishing_Rod_Copper"), ""),
                                                                    JString("p1:pole:rb"))))
        LL.LAST.clear()
        Life.sweep0(PR1, inv_, True)
        Life.buy(U1, JInt(0), JInt(1))          # one Fortune point on the pickaxe
        return inv_, cs_, pl_, hz_
    shutil.rmtree(os.path.join(HOME, "rebirth"), ignore_errors=True)
    shutil.rmtree(os.path.join(HOME, "rebirth-backup"), ignore_errors=True)
    LL.RBREC.clear()
    invB, csB, plB, hzB = rb_setup()
    pkB = [x for x in lls(csB, "p1") if x[2] == 0][0]
    rCh = int(Data.rarity(doc(csB["storage"].getItemStack(JShort(30)))))          # the Cobalt chest's rarity before (a crafted mining piece may be Set)
    rf0 = regfile("p1")
    K.check(rf0.get("pickaxe.up.fort") == "1" and rf0.get("pole.uid") is not None, "G35 RB0: the profile: a Fortune point on the pickaxe, a pole: %s" % rf0.get("pickaxe.up.fort"))
    m_ = rb("measure", TX1)
    K.check(m_.startswith("ok:kinds=5;points=1;tiers=") and "pickaxe:Tool_Pickaxe_Iron" in m_ and not os.path.isdir(os.path.join(HOME, "rebirth")),
            "G35 RB1: measure = the facts (5 kinds, 1 point, the tiers), nothing written: %s" % m_)
    # crash points of prepare (1 after the backup, 2 after the staged file) -> a restart -> abort cleans it / prepare again works
    crashP = []
    for c_ in (1, 2):
        Rb.CRASH = c_
        ok_ = False
        try:
            rb("prepare", TX1)
        except Exception as ex_:
            ok_ = ("rebirth step %d" % c_) in str(ex_)
        Rb.CRASH = 0
        LL.RBREC.clear()
        crashP.append((c_, ok_, rb("status", TX1), rb("abort", TX1), rb("status", TX1)))
    K.check(crashP[0][1] and crashP[0][2] == "none" and crashP[1][1] and crashP[1][2] == "staged" and crashP[1][3] == "done" and crashP[1][4] == "none"
            and regfile("p1") == rf0, "G35 RB2: a crash in prepare (after the backup / after the staged file) changes nothing live; abort cleans the staged "
            "file: %s" % crashP)
    p_ = rb("prepare", TX1)
    bk_ = os.path.join(HOME, "rebirth-backup", "p1", TX1, "p1.properties")
    K.check(p_.startswith("ok:kinds=5") and os.path.isfile(bk_) and os.path.isfile(os.path.join(HOME, "rebirth", "p1.rb-%s.properties" % TX1))
            and rb("status", TX1) == "staged" and regfile("p1") == rf0 and "pickaxe.up.fort=1" in open(bk_, encoding="latin-1").read(),
            "G35 RB3: prepare = a backup of lifelong/p1.properties (rebirth-backup/p1/<txid>/) + the staged file; the registry untouched")
    K.check(rb("commit", TX1, 0).startswith("err:no rebirth number") and rb("bogus", TX1).startswith("err:unknown op") and rb("commit", "tx1-bad").startswith("err:bad txid")
            and rb("commit", TX1, 1, "../x").startswith("err:bad profile key") and str(Rb().apply(JString("x"))).startswith("err:bad arguments")
            and rb("commit", TX2).startswith("err:no staged file"), "G35 RB4: bad arguments / no staged file = err, never a throw")
    # commit: crash 3 (the record is on disk, memory not yet) -> a restart reads it: committed; the commit again = done
    Rb.CRASH = 3
    try:
        rb("commit", TX1)
    except Exception:
        pass
    Rb.CRASH = 0
    LL.RBREC.clear()
    st3 = rb("status", TX1)
    c2_ = rb("commit", TX1)
    recf = os.path.join(HOME, "rebirth", "p1.record.properties")
    K.check(st3 == "committed" and c2_ == "done" and os.path.isfile(recf) and "rb.lastTx=" + TX1 in open(recf, encoding="latin-1").read()
            and rb("abort", TX1).startswith("err:already committed") and not os.path.isfile(os.path.join(HOME, "rebirth", "p1.rb-%s.properties" % TX1))
            and regfile("p1") == rf0, "G35 RB5: commit = ONE atomic record write (a crash right after it: the restart reads it - committed; again = done; abort "
            "refused); the registry is still untouched (the world thread applies it): %s %s" % (st3, c2_))
    # the waits: a rebirth record not applied yet -> perk buys / resets / lifelong tier-ups wait
    LL.reg("p1")
    w1 = str(Life.buy(U1, JInt(0), JInt(1)))
    w2 = str(Life.reset(U1, "Tester", JInt(0)))
    K.check(w1.startswith("-A rebirth is finishing") and w2.startswith("-A rebirth is finishing") and bool(LL.rbWait(U1)),
            "G35 RB6: before the apply, perk buys / resets wait: %s | %s" % (w1, w2))
    # the hatchet sits in a chest during the apply
    chestB = SIC(JShort(9))
    chestB.setItemStackForSlot(JShort(0), hzB[6])
    csB[hzB[0]].removeItemStackFromSlot(JShort(hzB[1]))
    # crash 13 in the first tool reset (after its BEGIN line, before the write): nothing half-done; the next look resets it
    logs()
    Life.CRASH_AT = 13
    Life.sweep(PR1, invB, True)
    Life.CRASH_AT = 0
    pk13 = [x for x in lls(csB, "p1") if x[2] == 0][0]
    rf13 = regfile("p1")
    K.check(str(pk13[6].getItemId()) == "Tool_Pickaxe_Iron" and rf13.get("rb.applied") == TX1 and rf13.get("pickaxe.id") == "Tool_Pickaxe_Crude"
            and rf13.get("pickaxe.up.fort") is None and rf13.get("pickaxe.rbTx") == TX1,
            "G35 RB7: the apply = ONE registry write (every kind Crude, the points gone, rbTx; rb.applied) - a crash in the first tool reset leaves the tool as it "
            "was: %s" % pk13[6].getItemId())
    snapB = snapshot(csB)
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    pkR = [x for x in lls(csB, "p1") if x[2] == 0][0]
    dR = doc(pkR[6])
    poR = [x for x in lls(csB, "p1") if x[2] == 4][0]
    arm0 = csB["armor"].getItemStack(JShort(0))
    ch30 = csB["storage"].getItemStack(JShort(30))
    lgR = logs()
    K.notes.append("G35 RB8 debug: r %s mods %s/%s rbx %s lvl %s/%s ch30 r %s armlog %s toollog %s" % (Data.str(dR, "r", ""), Data.mods(dR).size(), Data.mods(doc(pkB[6])).size(),
                   Data.str(dR, "rbx", ""), Data.num(dR, "lvl", -1), LL.levelFor(U1, "Tool_Pickaxe_Crude"), Data.rarity(doc(ch30)),
                   len(logs_has(lgR, "LL-REBIRTH-ARMOR ")), len(logs_has(lgR, "LL-REBIRTH-TOOL "))))
    jsPo = str(poR[6].getMetadata().toJson())
    K.check(str(FRig.LL_LINE) in jsPo and "Copper Fishing Rod" not in jsPo and str(Data.str(doc(poR[6]), "rbx", "")) == TX1 and FRig.doc(poR[6]) is not None
            and br.get("fishing:fn:restamp") is not None,
            "G35 RB8 FIX 3.2: the pole reset to the Wooden rod keeps a tooltip - SkyyFishing's fishing:fn:restamp redrew it (the lifelong line, no Copper "
            "name), our document (rbx) and its rig kept: %s" % jsPo[:300])
    K.check(str(pkR[6].getItemId()) == "Tool_Pickaxe_Crude" and pkR[3] == pkB[3] and str(Data.str(dR, "r", "")) == "legendary"
            and int(Data.mods(dR).size()) == int(Data.mods(doc(pkB[6])).size()) and str(Data.str(dR, "rbx", "")) == TX1
            and int(Data.num(dR, "lvl", -1)) == int(LL.levelFor(U1, "Tool_Pickaxe_Crude")) and str(poR[6].getItemId()) == "SkyyFishing_Rod_Bamboo"
            and str(arm0.getItemId()) == "Armor_Copper_Head" and str(ch30.getItemId()) == "Armor_Copper_Chest" and int(Data.rarity(doc(ch30))) == rCh
            and str(Data.str(doc(arm0), "rbx", "")) == TX1 and logs_has(lgR, "LL-REBIRTH-TOOL ", "Tool_Pickaxe_Iron -> Tool_Pickaxe_Crude")
            and logs_has(lgR, "LL-REBIRTH-ARMOR ", "Armor_Iron_Head -> Armor_Copper_Head"),
            "G35 RB8: the next look resets IN PLACE: the pickaxe -> Crude (same uid, Legendary + its lines kept, Lv = the skill rule, rbx), the pole -> the "
            "Wooden rod, the worn Iron head + the stored Cobalt chest -> Copper (rarity kept), each logged with undo data: %s %s %s %s"
            % (pkR[6].getItemId(), poR[6].getItemId(), arm0.getItemId(), ch30.getItemId()))
    # the engine never saved that inventory (a crash) -> the old stacks come back -> the next look resets them again (rbx = once per rebirth)
    restore_inv(csB, snapB)
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    n20 = int(Life.N[20])
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    K.check(str([x for x in lls(csB, "p1") if x[2] == 0][0][6].getItemId()) == "Tool_Pickaxe_Crude" and int(Life.N[20]) == n20,
            "G35 RB9: a crash before the engine saved the inventory: the old stack comes back and is reset again; a further look changes nothing")
    # the hatchet comes back from its chest -> reset then
    csB["storage"].setItemStackForSlot(JShort(29), chestB.getItemStack(JShort(0)))
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    hzR = [x for x in lls(csB, "p1") if x[2] == 1][0]
    K.check(str(hzR[6].getItemId()) == "Tool_Hatchet_Crude" and hzR[3] == hzB[3] and str(Data.str(doc(hzR[6]), "rbx", "")) == TX1,
            "G35 RB10: the hatchet that sat in a chest during the rebirth is reset when it comes back: %s" % hzR[6].getItemId())
    # FIX ROUND 2 (critics C1 / A3): the armor reset goes by the piece's BIRTH (document b0 < garmor.rbCut = the record's rb.at), no 30 s window
    BI64 = JClass("org.bson.BsonInt64")
    cutB = int(regfile("p1").get("garmor.rbCut") or 0)
    rec_at = int([l_.split("=", 1)[1] for l_ in open(recf, encoding="latin-1").read().splitlines() if l_.startswith("rb.at=")][0])
    nd0 = Roll.newDoc("Armor_Iron_Legs", JInt(1), True, "craft", JInt(15))
    K.check(cutB == rec_at and int(Data.lnum(nd0, "b0", JLong(0))) >= cutB and int(Data.lnum(Data.base("armor", JInt(0), True, "x"), "b0", JLong(0))) > 0,
            "G35 RB11 FIX 2: every NEW document carries b0 (its birth); the apply recorded the cut = the record's rb.at (%s / %s)" % (cutB, rec_at))
    # a piece made AFTER the rebirth keeps its tier, even an hour later
    csB["storage"].setItemStackForSlot(JShort(28), Data.put(stack("Armor_Iron_Legs"), nd0, None))
    nA21 = int(Life.N[21])
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    K.check(str(csB["storage"].getItemStack(JShort(28)).getItemId()) == "Armor_Iron_Legs" and int(Life.N[21]) == nA21,
            "G35 RB11 FIX 2: a Mining piece made AFTER the rebirth keeps its tier")
    # a piece born BEFORE the rebirth that sat in a chest / the Vault / with a friend: reset the first time it is on you, however late
    dOld = Roll.newDoc("Armor_Iron_Hands", JInt(2), True, "craft", JInt(15))          # (a new metal piece is always the green Mining Set one)
    dOld.put("b0", BI64(JLong(cutB - 3600000)))
    dPre = Roll.newDoc("Armor_Cobalt_Legs", JInt(1), True, "craft", JInt(26))
    dPre.remove("b0")          # a piece from before 0.3.5 (no birth) = old
    csB["storage"].setItemStackForSlot(JShort(27), Data.put(stack("Armor_Iron_Hands"), dOld, None))
    csB["storage"].setItemStackForSlot(JShort(26), Data.put(stack("Armor_Cobalt_Legs"), dPre, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    f27 = csB["storage"].getItemStack(JShort(27))
    f26 = csB["storage"].getItemStack(JShort(26))
    K.check(str(f27.getItemId()) == "Armor_Copper_Hands" and str(f26.getItemId()) == "Armor_Copper_Legs" and int(Data.rarity(doc(f27))) == int(Data.rarity(dOld))
            and str(Data.str(doc(f27), "rbx", "")) == TX1 and int(Life.N[21]) == nA21 + 2,
            "G35 RB11 FIX 2 (critic C1): a piece born before the rebirth that was stored elsewhere (here: an hour old) and one from before 0.3.5 (no b0) "
            "go to Copper when they come back, rarity kept: %s %s" % (f27.getItemId(), f26.getItemId()))
    # an UNIDENTIFIED old piece waits; identified later (its birth unchanged) it resets at the next look
    dUn = Roll.newDoc("Armor_Iron_Chest", JInt(1), False, "loot", JInt(15))
    dUn.put("id", JClass("org.bson.BsonBoolean")(False))          # an unidentified metal piece (rolled before 0.2.15 / an admin unid)
    dUn.put("b0", BI64(JLong(cutB - 1000)))
    csB["storage"].setItemStackForSlot(JShort(25), Data.put(stack("Armor_Iron_Chest"), dUn, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    u25a = str(csB["storage"].getItemStack(JShort(25)).getItemId())
    dId = Roll.identify("Armor_Iron_Chest", doc(csB["storage"].getItemStack(JShort(25))), U1)
    csB["storage"].setItemStackForSlot(JShort(25), Data.put(stack("Armor_Iron_Chest"), dId, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    u25b = str(csB["storage"].getItemStack(JShort(25)).getItemId())
    n21b = int(Life.N[21])
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    K.check(u25a == "Armor_Iron_Chest" and u25b == "Armor_Copper_Chest" and int(Data.lnum(dId, "b0", JLong(0))) == cutB - 1000 and int(Life.N[21]) == n21b
            and regfile("p1").get("garmor.rbAt") is None and regfile("p1").get("garmor.rbDone") is None,
            "G35 RB11 FIX 2 (critic A3): an unidentified old piece waits; identified after the rebirth (b0 kept) it resets at the next look; a further look "
            "changes nothing (rbx); no window keys: %s -> %s" % (u25a, u25b))
    w3 = str(Life.buy(U1, JInt(0), JInt(1)))
    K.check(not bool(LL.rbWait(U1)) and not w3.startswith("-A rebirth"), "G35 RB12: applied = the waits end: %s" % w3)
    # SkyyRebirth's busy flag: the waits again (spec 5.4)
    BUSY = {"p1": True}

    @JImplements("java.util.function.Function")
    class RbBusy(object):
        @JOverride
        def apply(self, o):
            return TRUE_ if BUSY.get(str(o)) else FALSE_
    br.put("rebirth:fn:busy", RbBusy())
    w4 = str(Life.buy(U1, JInt(0), JInt(1)))
    upB = Up.check(pkR[6], U1)
    BUSY["p1"] = False
    w5 = str(Life.buy(U1, JInt(0), JInt(1)))
    br.remove("rebirth:fn:busy")
    K.check(w4.startswith("-A rebirth is finishing") and str(upB[0]).startswith("A rebirth is finishing") and not w5.startswith("-A rebirth"),
            "G35 RB13: while rebirth:fn:busy says so, perk buys and the lifelong tier-up wait: %s | %s" % (w4, upB[0]))
    # THE REBIRTH MODIFIER (rebirth:fn:node "<Arm>.tool" x lifelong.rebirthPct)
    NODE = {"Mining.tool": 2, "Mining.tool2": 1}

    @JImplements("java.util.function.Function")
    class RbNode(object):
        @JOverride
        def apply(self, o):
            return JObject(JInt(NODE.get(str(o[1]), 0)), Integer_)
    Tool.LAST.clear()
    s0_ = list(Tool.stats(U1, pkR[6]))
    br.put("rebirth:fn:node", RbNode())
    Tool.LAST.clear()
    s1_ = list(Tool.stats(U1, pkR[6]))
    m0 = float(LL.rbMult(U1, JInt(0)))
    m1 = float(LL.rbMult(U1, JInt(1)))
    midM = str(JClass(PKG + "GearMulti").mid(JInt(1)))
    dMt = Life.llDoc(None, midM, U1, "p1", "mt00000000000001", False)
    mtN = [float(x) for x in Tool.mstats(U1, midM, dMt)]
    mpN = [float(x) for x in Tool.mstats(U1, midM, None)]
    br.remove("rebirth:fn:node")
    mt0 = [float(x) for x in Tool.mstats(U1, midM, dMt)]
    mp0 = [float(x) for x in Tool.mstats(U1, midM, None)]
    br.put("rebirth:fn:node", RbNode())
    apply(lifelong__rebirthPct="0")
    m2 = float(LL.rbMult(U1, JInt(0)))
    apply()
    br.remove("rebirth:fn:node")
    K.notes.append("G35 RB14 multitool: lifelong %s -> %s, plain %s -> %s" % (mt0, mtN, mp0, mpN))
    K.check(bool(LL.mine(U1, dMt)) and abs(mtN[4] - min(100.0, mt0[4] * 1.15)) < 1e-6 and abs(mtN[9] - min(100.0, mt0[9] * 1.15)) < 1e-6 and mpN == mp0,
            "G35 RB14 FIX 2.2: GearTool.mstats: a LIFELONG Multitool takes the Mining node's modifier on both sides (x1.15: Power %s -> %s, chopping %s -> %s); "
            "a plain Multitool is unchanged" % (mt0[4], mtN[4], mt0[9], mtN[9]))
    K.check(abs(m0 - 1.15) < 1e-9 and m1 == 1.0 and m2 == 1.0 and len(s1_) > 5 and (s1_[4] > s0_[4] or s1_[4] == 100.0) and len(LL.perkFx(U1, JInt(1), doc(pkR[6]))) == 4,
            "G35 RB14: the rebirth modifier: Mining.tool level 2 + Mining.tool2 level 1 (FIX 2.1) x 5 %% = x1.15 on the pickaxe's Power (%s -> %s); no node "
            "= x1; lifelong.rebirthPct 0 = x1"
            % (s0_[4], s1_[4]))
    # a SECOND rebirth: the record keeps both, the tools reset again (rbx = the new txid)
    rb("prepare", TX2)
    c3_ = rb("commit", TX2, 2)
    LL.LAST.clear()
    Life.sweep0(PR1, invB, True)
    recT = open(recf, encoding="latin-1").read()
    K.check(c3_ == "ok" and "hist.1=" + TX1 in recT and "hist.2=" + TX2 in recT and regfile("p1").get("rb.applied") == TX2
            and str(Data.str(doc([x for x in lls(csB, "p1") if x[2] == 0][0][6]), "rbx", "")) == TX2,
            "G35 RB15: a second rebirth: the record keeps hist.1 + hist.2, the tools carry the new rbx")
    # a prepare while an OLDER committed rebirth's staged file is still around (decision commit) is refused; an aborted older one is cleaned
    open(os.path.join(HOME, "rebirth", "p1.rb-%s.properties" % TX3), "w").write("tx=%s\n" % TX3)
    DEC = {TX3: "commit"}

    @JImplements("java.util.function.Function")
    class RbDec(object):
        @JOverride
        def apply(self, o):
            return JString(DEC.get(str(o), "unknown"))
    br.put("rebirth:fn:decision", RbDec())
    TX4 = "tx1760000000004-a1b2c6"
    p4 = rb("prepare", TX4)
    DEC[TX3] = "abort"
    p5 = rb("prepare", TX4)
    br.remove("rebirth:fn:decision")
    K.check(p4.startswith("err:an older rebirth") and p5.startswith("ok:") and not os.path.isfile(os.path.join(HOME, "rebirth", "p1.rb-%s.properties" % TX3)),
            "G35 RB16: prepare refuses while an older COMMITTED rebirth's staged file waits; an aborted one is cleaned: %s | %s" % (p4, p5))
    rb("abort", TX4)
    # THE MULTITOOL GATE (rebirth n >= 1 with SkyyRebirth loaded; multi.rebirthGate)
    @JImplements("java.util.function.Function")
    class RbCount(object):
        @JOverride
        def apply(self, o):
            return JObject(JInt(0), Integer_)
    br.put("rebirth:fn:count", RbCount())
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer_))
    gD = LL.rbGate(U1)          # FIX ROUND 2 (critic B1): the default (OFF) = open even with SkyyRebirth loaded and rebirth 0
    mcD = Merge.check(stack("Tool_Pickaxe_Iron"), stack("Tool_Hatchet_Iron"), U1)
    br.remove("rebirth:n:" + str(U1))
    br.remove("rebirth:fn:count")
    K.check(gD is None and not bool(Cfg.MULTI_RBGATE) and (mcD[0] is None or "rebirth" not in str(mcD[0])) and "false" in [l_.split("=", 1)[1].strip() for l_ in FRESH.splitlines() if l_.startswith("multi.rebirthGate")],
            "G35 RB17 FIX 2 (critic B1): multi.rebirthGate ships OFF (the fresh file says false): with SkyyRebirth loaded and rebirth 0 the plain-tool merge "
            "still works as in 0.3.4: %s" % (mcD[0],))
    apply(multi__rebirthGate="true")
    g0 = LL.rbGate(U1)
    br.put("rebirth:fn:count", RbCount())
    g1_ = LL.rbGate(U1)
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer_))
    g2 = LL.rbGate(U1)
    mc2 = Merge.check(stack("Tool_Pickaxe_Iron"), stack("Tool_Hatchet_Iron"), U1)
    br.put("rebirth:n:" + str(U1), JObject(JInt(1), Integer_))
    g3 = LL.rbGate(U1)
    br.put("rebirth:n:" + str(U1), JObject(JInt(0), Integer_))
    sGate = str(LL.statusText())
    apply(multi__rebirthGate="false")
    g4 = LL.rbGate(U1)
    apply()
    br.remove("rebirth:fn:count")
    br.remove("rebirth:n:" + str(U1))
    K.check(g0 is None and str(g1_).startswith("Your rebirths are still loading") and str(g2).startswith("Multitools come after your first rebirth")
            and str(mc2[0]) == str(g2) and g3 is None and g4 is None,
            "G35 RB17: the multitool gate: no SkyyRebirth = open; loading = wait; rebirth 0 = 'Multitools come after your first rebirth' (the merge check "
            "says it); rebirth 1 = open; multi.rebirthGate off = open")
    mwL = str(Merge.why(pkR[6], JInt(1)))
    K.check("cannot be merged yet" in mwL and "later update" in mwL and "after your first rebirth" not in mwL,
            "G35 RB17 FIX 3.1: a lifelong pickaxe in the merge no longer promises 'after your first rebirth' (the lifelong merge is a later round): %s" % mwL)
    K.check("rebirth part rebirth:part:gear" in str(Rb.statusText()) and "rebirths applied" in str(Life.counters())
            and "multitools after rebirth 1" in sGate and "multitools always" in str(LL.statusText()),
            "G35: the status texts name the rebirth part, the counters, the gate: %s" % str(Rb.statusText()))
    with zipfile.ZipFile(JAR) as zj_:
        man35 = zj_.read("manifest.json").decode("utf-8")
    K.check("closed Vault" in man35 and "bare hands count as a Crude hoe" in man35 and "fifth lifelong tool" in man35 and "rebirth:part:gear" in man35,
            "G35: the manifest sentence names the round")
    # FIX ROUND 2 (critic B2): an unreadable rebirth record is NOT read again at every look - at most every 30 s
    LL.RBREC.clear()
    LL.RBBAD.clear()
    os.makedirs(os.path.join(HOME, "rebirth"), exist_ok=True)
    bf_ = os.path.join(HOME, "rebirth", "pbad.record.properties")
    open(bf_, "w").write("rb.lastTx=\\uZZZZ\n")          # a garbled \u escape: Properties.load throws
    b1_ = LL.rbRec("pbad")
    open(bf_, "w").write("rb.lastTx=%s\nrb.n=1\n" % TX1)          # healed on disk - but within 30 s it is not read again
    b2_ = LL.rbRec("pbad")
    LL.RBBAD.put("pbad", JObject(JLong(int(__import__("time").time() * 1000) - 31000), JClass("java.lang.Long")))
    b3_ = LL.rbRec("pbad")
    K.check(b1_ is None and b2_ is None and b3_ is not None and str(b3_.getProperty("rb.lastTx")) == TX1 and LL.RBBAD.get("pbad") is None,
            "G35 RB18 FIX 2 (critic B2): an unreadable record answers null and is not read again for 30 s (no file read on the world thread at every "
            "look); after that it is read and the failure forgotten")
    os.remove(bf_)
    LL.RBREC.clear()
    PKEY[str(U1)] = "p1"
    K.save()


# C32 (0.3.2): every member tools/gear_0_3_2_patch.py touches, nothing else
_CMD32 = {"~c ", "~m execute"}          # the description text + reclaimW(..., world)
WANT32 = {
    "GearLL": {"~<clinit>", "+f HERE", "+f TRACKQ", "~m forget", "+m hereMask", "~m invested", "~m statusText", "+m trackHook", "+m trackMaybe"},
    "GearInvSys": {"~m handle"},
    "GearLife": {"~<clinit>", "+f SNAPRAW", "+f TEST_CHESTS", "+f TEST_WKEY", "+m chestAt", "+m clearLoc", "~m commit", "~m counters", "+m fromChest",
                 "+m fromRequip", "+m fromWindows", "~m give", "+m give2", "+m hereAdd", "~m keep", "+m locText", "+m locWhy", "+m move", "~m pass", "+m present",
                 "~m reclaim", "+m reclaimW", "~m recover", "+m rqFind", "+m setLoc", "+m slotIn", "+m snapDoc", "+m snapSet", "+m snapText",
                 "+m track", "+m trackLater", "+m winName", "+m wkOf",
                 "+m nswHas", "+m nswAdd", "+m lcuOf", "+m family", "~m repick", "~m settle", "~m notice"},          # fix round
    "LifePage": {"~m row"},
    "PickaxeCmd": _CMD32, "HatchetCmd": _CMD32, "HoeCmd": _CMD32, "SickleCmd": _CMD32,
}

# C33 (0.3.3): every member tools/gear_0_3_3_patch.py touches, nothing else
WANT33 = {"GearLL": {"~m decideI", "~m hit", "~m statusText", "+m cropNo", "+m useNo"},          # fix round: + the F-harvest gate
          "GearChestOpenSys": {"~m handle"}}

# C34 (0.3.4): every member tools/gear_0_3_4_patch.py touches, nothing else
WANT34 = {"GearLL": {"~m ladders", "~m invested"},
          "GearLife": {"~m give2"},
          "GearTool": {"~m held"},
          "GearWall": {"~m why"},
          "GearForge": {"~m lvlInfo"},
          "GearToolHitSys": {"~m handle"},
          "GearStampTask": {"~m run"},
          "GearUp": {"~m check", "~m docI"},
          "GearBye": {"~m accept"},
          "ReforgePage": {"+f anSig", "+f anSgArm", "+f anSgFp", "~m anPick", "~m anPanel", "~m anEvent", "+m anSigPick", "+m anSigil", "+m anSigDo"},
          "SkyyGearPlugin": {"~m setup"}}
ADD34 = ["GearArmLv", "GearSigil", "GearTill", "GearTillSys"]
# C35 (0.3.5): every member tools/gear_0_3_5_patch.py touches, nothing else
WANT35 = {
    # 1 vault summon (fromVault), 4 the pole (kOf / isPole / POLE, the sweep's adoption, /pole, gear:fn:pole, /lifelong on a rod), 5 rebirth R7 (the record,
    # rbApply / rbTool / rbArmor, the modifier in perkFx + GearTool.stats, the multitool gate, the waits in buy / reset / GearUp.check)
    "GearLL": {"~<clinit>", "+f POLE", "+f RBNODE", "+f RBSFX", "+f RBREC", "+f RBBAD", "~m decideI", "~m hit", "+m isPole", "~m kOf", "~m perkFx", "~m prefetch", "+m rbBusy",
               "+m rbFile", "+m rbGate", "+m rbMult", "+m rbNode", "+m rbPending", "+m rbRec", "+m rbWait", "+m safeKey", "~m statusText", "~m useNo"},
    "GearLife": {"~<clinit>", "+f TEST_NOREAD", "+m adoptPole", "~m buy", "~m counters", "+m fromVault", "~m llDoc", "~m pass", "+m poleLook", "+m poleStamp", "+m poleUid", "+m rbApply",
                 "+m rbArmor", "+m rbArmorTo", "+m rbNeed", "+m rbTool", "~m reclaimW", "~m recover", "~m repick", "~m reset", "~m rqKinds", "~m sweep0",
                 "~m track", "+m vaultAt"},
    "GearLLFn": {"~m apply"},          # gear:fn:pole (mode 3)
    "GearData": {"+m pole", "~m put", "~m base"},          # fix round 2: base stamps b0 (the birth);
    "GearTool": {"~m stats", "~m mstats"},          # the rebirth modifier (fix: + the lifelong Multitool)
    "GearUp": {"~m check"},          # a lifelong tier-up waits during a rebirth
    "GearMerge": {"~m check", "~m why"},          # the multitool rebirth gate (fix: + the lifelong text)
    "GearIdent": {"+<clinit>", "+f RV", "+m allInC", "+m coverName", "+m revCard", "+m revRank", "+m revSafe", "+m reveal", "+m revealOne", "+m backFor", "+m revTell", "~m allIn"},
    "IdentifyPage": {"~m all", "~m one", "~m reroll"},          # 3 the identify reveal
    "ReforgePage": {"~m anId", "~m anIdAll", "~m anReroll"},
    "ToolPtsCmd": {"~m execute"},          # the pole is not on the four-row Tools tab
    "SkyyGearPlugin": {"~m setup", "~m shutdown"},
}
ADD35 = ["GearRb", "PoleCmd"]


# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    def jdiff(old_jar, old_ver, new_jar=JAR, new_ver=VERSION):          # 0.3.3: C32 compares two older jars
        pa, pb = pool_of(old_jar), pool_of(new_jar)
        na, nb = jar_classes(old_jar), jar_classes(new_jar)
        diffs = {}
        for cn in sorted(set(na) & set(nb)):
            ma, mb = members(pa, cn, (old_ver, new_ver)), members(pb, cn, (old_ver, new_ver))
            dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
            if dd:
                diffs[cn.split(".")[-1]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
        add = sorted(x.split(".")[-1] for x in set(nb) - set(na))
        gone = sorted(set(na) - set(nb))
        print("C. class compare %s -> %s: + %s - %s" % (old_ver, new_ver, add, gone))
        for k in sorted(diffs):
            print("   %-16s %s" % (k, ", ".join(diffs[k])[:1500]))
        return diffs, add, gone

    # ---- C32 (0.3.2): 0.3.1 -> 0.3.2 = exactly this round's members (tools/gear_0_3_2_patch.py): the tracker gate + HERE in GearLL, the
    # GearInvSys hook, GearLife's fetch / copy / snapshot / place members, the commands (text + the world), the Tools tab line, GearTrackTask
    d32, add32, gone32 = jdiff(J31, V31, J32, V32)          # 0.3.3: jar to jar
    want32 = WANT32
    bad32 = {}
    for k in set(want32) | set(d32):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(d32.get(k, []))
        if got != want32.get(k, set()):
            bad32[k] = (sorted(want32.get(k, set()) - got), sorted(got - want32.get(k, set())))
    cfg32 = dict((k, v) for k, v in d32.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(add32 == ["GearTrackTask"] and not gone32 and not bad32 and "GearDefs" not in cfg32
            and cfg32 == {"CfgRows": ["~<clinit>"], "GearCfg": ["~m defaultsText"]},
            "C32: 0.3.1 -> 0.3.2 changed exactly the listed members (+ GearTrackTask; config classes: only the row texts - the kit's row table "
            "and the fresh file's help lines): bad %s, config %s" % (bad32, cfg32))
    # ---- C33 (0.3.3): 0.3.2 -> 0.3.3 = exactly this round's members (tools/gear_0_3_3_patch.py): GearLL.decideI (crops refuse at two up),
    # GearLL.hit (the crop popup), GearLL.statusText; config classes: only the gate.on help text
    d33, add33, gone33 = jdiff(J32, V32, J33, V33)          # 0.3.4: jar to jar
    bad33 = {}
    for k in set(WANT33) | set(d33):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(d33.get(k, []))
        if got != WANT33.get(k, set()):
            bad33[k] = (sorted(WANT33.get(k, set()) - got), sorted(got - WANT33.get(k, set())))
    cfg33 = dict((k, v) for k, v in d33.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(not add33 and not gone33 and not bad33 and cfg33 == {"CfgRows": ["~<clinit>"], "GearCfg": ["~m defaultsText"]},
            "C33: 0.3.2 -> 0.3.3 changed exactly GearLL.decideI / hit / statusText + cropNo / useNo, GearChestOpenSys.handle (+ the gate.on help in the config classes), no class added "
            "or removed: + %s - %s bad %s, config %s" % (add33, gone33, bad33, cfg33))
    # ---- C34 (0.3.4): 0.3.3 -> 0.3.4 = exactly this round's members
    d34, add34, gone34 = jdiff(J33, V33, J34, V34)          # 0.3.5: jar to jar
    bad34 = {}
    for k in set(WANT34) | set(d34):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(d34.get(k, []))
        if got != WANT34.get(k, set()):
            bad34[k] = (sorted(WANT34.get(k, set()) - got), sorted(got - WANT34.get(k, set())))
    cfg34 = dict((k, v) for k, v in d34.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(sorted(add34) == sorted(ADD34) and not gone34 and not bad34 and "GearDefs" not in cfg34
            and all(x.startswith("+f ") or x.startswith("~m ") or x == "~<clinit>" for v in cfg34.values() for x in v),
            "C34: 0.3.3 -> 0.3.4 changed exactly the listed members (+ GearArmLv / GearSigil / GearTill / GearTillSys; config classes: the 6 rows' "
            "fields + tables): + %s - %s bad %s, config %s" % (add34, gone34, bad34, cfg34))
    # ---- C35 (0.3.5): 0.3.4 -> 0.3.5 = exactly this round's members (tools/gear_0_3_5_patch.py)
    d35, add35, gone35 = jdiff(J34, V34)
    bad35 = {}
    for k in set(WANT35) | set(d35):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(d35.get(k, []))
        if got != WANT35.get(k, set()):
            bad35[k] = (sorted(WANT35.get(k, set()) - got), sorted(got - WANT35.get(k, set())))
    cfg35 = dict((k, v) for k, v in d35.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(sorted(add35) == sorted(ADD35) and not gone35 and not bad35 and "GearDefs" not in cfg35
            and all(x.startswith("+f ") or x.startswith("~m ") or x == "~<clinit>" for v in cfg35.values() for x in v),
            "C35: 0.3.4 -> 0.3.5 changed exactly the listed members (+ GearRb / PoleCmd; config classes: the 2 rows' fields + tables): + %s - %s bad %s, config %s"
            % (add35, gone35, bad35, cfg35))
    diffs, add, gone = jdiff(OLD_JAR, OLD_VERSION)
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly the 0.3.0 classes (+ 0.3.2 GearTrackTask), none removed: + %s - %s" % (add, gone))
    want = {
        "Gear": {"+m fnum10"},          # 0.3.1
        "GearTool": {"~m gate", "~m stats", "~m mstats", "~m held", "~m lines"},
        "GearLL": None,          # 0.3.4 / 0.3.0: a class of its own since 0.3.0 (compared in C34)
        "GearLife": None,
        "GearToolHitSys": {"~m handle"},
        "GearHandSys": {"~m tick"},          # fix round: the stale-level hand-off (GearLL.RESYNC -> GearStamp.dirtyIn)
        "GearCraftPreSys": {"~m handle"},
        "GearWall": {"~m why"},
        "GearForge": {"~m lvlInfo"},
        "GearMerge": {"~m why", "~m check"},          # 0.3.5: + the multitool rebirth gate
        "GearData": {"+m pole", "~m put", "~m base"},          # fix round 2: base stamps b0 (the birth);          # 0.3.5: a rod (the pole) keeps only its document
        "GearIdent": {"+<clinit>", "+f RV", "+m allInC", "+m coverName", "+m revCard", "+m revRank", "+m revSafe", "+m reveal", "+m revealOne", "+m backFor", "+m revTell", "~m allIn"},          # 0.3.5
        "IdentifyPage": {"~m all", "~m one", "~m reroll"},          # 0.3.5: the reveal cards
        "GearUp": {"~m tab", "~m check", "~m docI"},
        "GearUi": {"~m tabs"},
        "GearSmith": {"~m usable"},
        "GearRefreshTask": {"~m run"},
        "GearStampTask": {"~m run"},
        "GearInvSys": {"~m handle"},          # 0.3.2: the lifelong tool tracker's gate
        "GearChestOpenSys": {"~m handle"},          # 0.3.3 fix round: the F-harvest tier gate runs first
        "GearBye": {"~m accept"},
        "ReforgePage": {"~m handleDataEvent", "~m anId", "~m anIdAll", "~m anReroll"},          # 0.3.4: its new anvil members are checked in C34; 0.3.5: the reveal
        "MultiPage": {"~m handleDataEvent"},
        "SmithPage": {"~m handleDataEvent"},
        "SkyyGearPlugin": {"~m setup", "~m shutdown"},
    }
    bad = {}
    for k in set(want) | set(diffs):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs" or want.get(k, 0) is None:
            continue
        got = set(diffs.get(k, []))
        got = got - WANT34.get(k, set()) if k in WANT34 and not (WANT34[k] & set(want.get(k, set()))) else got          # 0.3.4: C34 owns these
        if got != want.get(k, set()):
            bad[k] = (sorted(want.get(k, set()) - got), sorted(got - want.get(k, set())))
    K.check(not bad, "C: changed exactly the listed members outside the config classes (missing / extra): %s" % bad)
    cfgd = dict((k, v) for k, v in diffs.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    want_f = {"+f LL_ON", "+f LL_NOCRAFT", "+f LL_NODROP", "+f LL_LADDERS", "+f LL_RECLAIM", "+f LL_REPICK", "+f LL_PSPD", "+f LL_PFORT", "+f LL_PWIS",
              "+f LL_RESET", "+f GATE_ON", "+f GATE_NEXT", "+f GATE_BARE", "+f LL_RTIER", "+f GATE_NEXT0", "+f GATE_TWO"}
    K.check(set(cfgd.get("GearCfg", [])) >= want_f and "GearDefs" not in cfgd
            and all(x.startswith("+f ") or x.startswith("~m ") or x.startswith("+m ") or x == "~<clinit>" for v in cfgd.values() for x in v),
            "C: the config classes gained the 15 rows (fields, the kit's row tables) and nothing else: %s" % cfgd)
    K.save(diffs=diffs)


# ====================================================================================================== TT: the till area on a REAL 0.7 ChunkStore
def run_till(out):
    """GearTill.area / blockAt / resolve against a REAL ChunkStore (engine classes: World + ChunkStore + ChunkGrid load states + a ComponentRegistry
    Store with BlockSection components on sections 0..3 of chunk 0,0; chunk 1,0 not loaded) - the SkyyArmory 0.1.23 port fixture's way, with
    the block map Empty / Soil_Grass / Rock_Stone / Soil_Dirt_Tilled / Soil_Dirt. The reads are the engine's own (getChunkSectionReferenceAtBlock,
    Store.getComponent, BlockSection.get); the write goes through the SETB seam into the same BlockSection (BlockOperations.setBlock needs the
    whole chunk module - its signature is asserted at build time, the call itself is UNVERIFIED until the game)."""
    from jpype import JClass, JArray, JShort, JInt, JImplements, JOverride, JObject, JBoolean, JString
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=True)
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)

    def alloc(c):
        return us.allocateInstance(c.class_)
    W = "com.hypixel.hytale.server.core.universe.world."
    WLD, CHS, GRID = JClass(W + "World"), JClass(W + "storage.ChunkStore"), JClass(W + "storage.ChunkGrid")
    LS, CLS = JClass(W + "storage.ChunkGrid$LoadState"), JClass(W + "storage.ChunkGrid$ChunkLoadState")
    BSEC = JClass(W + "chunk.section.BlockSection")
    LM = JClass("com.hypixel.hytale.server.core.modules.LegacyModule")
    CR, ERS, AR = JClass("com.hypixel.hytale.component.ComponentRegistry"), JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason")
    CHU, I3, L2O, SL = (JClass("com.hypixel.hytale.math.util.ChunkUtil"), JClass("com.hypixel.hytale.math.data.Int3ObjectOpenHashMap"),
                        JClass("com.hypixel.fastutil.longs.Long2ObjectConcurrentHashMap"), JClass("java.util.concurrent.locks.StampedLock"))

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()
    reg = CR()
    t_bs = reg.registerComponent(BSEC.class_, Sup(lambda: BSEC()))
    lm = alloc(LM)
    jf(LM, "blockSectionComponentType").set(lm, t_bs)
    jf(LM, "instance").set(None, lm)
    AST, JAWM = JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    jcp = JClass("javassist.ClassPool")(True)
    jct = jcp.makeClass("com.hypixel.hytale.assetstore.SkyyTillFakeStore", jcp.get("com.hypixel.hytale.assetstore.AssetStore"))
    jct.addConstructor(JClass("javassist.CtNewConstructor").make("public SkyyTillFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", jct))
    HAST = JClass(jct.toClass(AST.class_).getName())
    BTc, BTM = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"), JClass("com.hypixel.hytale.assetstore.map.BlockTypeAssetMap")
    NAMES = ("Empty", "Soil_Grass", "Rock_Stone", "Soil_Dirt_Tilled", "Soil_Dirt")
    arr_ = JArray(JAWM)(len(NAMES))
    for i_, id_ in enumerate(NAMES):
        a_ = alloc(BTc)
        jf(BTc, "id").set(a_, id_)
        arr_[i_] = a_
    m_ = alloc(BTM)
    jf(BTM, "array").set(m_, arr_)
    k2i = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")()
    k2i.defaultReturnValue(JInt(-2147483648))
    for i_, id_ in enumerate(NAMES):
        k2i.put(JObject(JString(id_), JClass("java.lang.Object")), JInt(i_))
    jf(BTM, "keyToIndex").set(m_, k2i)
    jf(BTM, "keyToIndexLock").set(m_, SL())
    st_ = alloc(HAST)
    jf(AST, "assetMap").set(st_, m_)
    jf(BTc, "ASSET_STORE").set(None, st_)
    w = alloc(WLD)
    jf(WLD, "name").set(w, "skyy-island-p1")
    cs = alloc(CHS)
    jf(WLD, "chunkStore").set(w, cs)
    jf(GRID, "world").set(cs, w)
    jf(GRID, "lock").set(cs, SL())
    jf(GRID, "generatorLock").set(cs, SL())
    secs, chunks = I3(), L2O()
    jf(GRID, "chunkSections").set(cs, secs)
    jf(GRID, "chunks").set(cs, chunks)
    store = reg.addStore(cs, ERS.get())
    jf(GRID, "store").set(cs, store)
    lsk, clsk = LS.class_.getDeclaredConstructor(), CLS.class_.getDeclaredConstructor()
    lsk.setAccessible(True)
    clsk.setAccessible(True)
    h0 = reg.newHolder()
    cref = store.addEntity(h0, AR.LOAD)
    cl_ = clsk.newInstance()
    jf(LS, "reference").set(cl_, cref)
    chunks.put(CHU.indexChunk(0, 0), cl_)
    BS = []
    for cy_ in range(4):
        bs_ = BSEC()
        if cy_ == 2:
            for x_ in range(32):
                for z_ in range(32):
                    bs_.set(x_, 64, z_, 1, 0, 0)          # grass layer
            bs_.set(10, 64, 10, 3, 0, 0)          # the block the vanilla till just made
            bs_.set(9, 64, 9, 2, 0, 0)            # stone: not tillable
            bs_.set(11, 65, 10, 2, 0, 0)          # stone ABOVE grass: that grass is not tilled
            bs_.set(10, 64, 12, 4, 0, 0)          # plain dirt: tillable
        h_ = reg.newHolder()
        h_.addComponent(t_bs, bs_)
        r_ = store.addEntity(h_, AR.LOAD)
        ls_ = lsk.newInstance()
        jf(LS, "reference").set(ls_, r_)
        secs.put(0, cy_, 0, ls_)
        BS.append(bs_)
    Till = JClass(PKG + "GearTill")

    @JImplements("java.util.function.Function")
    class SetF(object):
        @JOverride
        def apply(self, o):
            x_, y_, z_, id_ = int(o[0]), int(o[1]), int(o[2]), int(o[3])
            TTARGS[(x_, y_, z_)] = (int(o[4]), int(o[5]))
            r_ = cs.getChunkSectionReferenceAtBlock(JInt(x_), JInt(y_), JInt(z_))
            if r_ is None or not r_.isValid():
                return JObject(JBoolean(False), JClass("java.lang.Boolean"))
            store.getComponent(r_, BSEC.getComponentType()).set(JInt(x_), JInt(y_), JInt(z_), JInt(id_), JInt(0), JInt(0))
            return JObject(JBoolean(True), JClass("java.lang.Boolean"))
    Till.IDX = None
    Till.TOI = -1
    ok_res = bool(Till.resolve())
    K.check(ok_res and int(Till.TOI) == 3 and int(Till.EMPTY) == 0 and bool(Till.tillable(JInt(1))) and bool(Till.tillable(JInt(4)))
            and not bool(Till.tillable(JInt(2))) and not bool(Till.tillable(JInt(3))) and not bool(Till.tillable(JInt(-1))),
            "TT: resolve() on the engine's BlockTypeAssetMap: tilled soil = 3, Empty = 0, grass / dirt tillable (the Assets.zip Hoe_Till Changes), stone / tilled not")
    rd = [int(Till.blockAt(cs, JInt(x_), JInt(y_), JInt(z_))) for x_, y_, z_ in ((3, 64, 3), (10, 64, 10), (9, 64, 9), (3, 65, 3), (40, 64, 3), (3, 200, 3), (3, -1, 3))]
    K.check(rd == [1, 3, 2, 0, -1, -1, -1], "TT: blockAt through the REAL ChunkStore + BlockSection: grass 1, tilled 3, stone 2, air 0, chunk 1,0 / section 6 not loaded = -1, y < 0 = -1: %s" % rd)
    TTARGS = {}
    BS[2].set(JInt(8), JInt(64), JInt(11), JInt(1), JInt(1), JInt(0))          # fixer 2: a grass block with rotation index 1
    rot_rd = int(Till.rotAt(cs, JInt(8), JInt(64), JInt(11)))
    Till.SETB = SetF()
    n5 = int(Till.area(w, JInt(10), JInt(64), JInt(10), JInt(5)))
    K.check(rot_rd == 1 and TTARGS.get((8, 64, 11)) == (1, 256) and TTARGS.get((10, 64, 12)) == (0, 256) and all(v_[1] == 256 for v_ in TTARGS.values()),
            "FIX2 TT: on the real BlockSection the extra blocks get the vanilla till's setBlock arguments: the block's OWN rotation index (1 / 0) "
            "and settings 256 (PERFORM_BLOCK_UPDATE): %s %s" % (rot_rd, sorted(set(TTARGS.values()))))
    got = sorted((x_, z_) for x_ in range(8, 13) for z_ in range(8, 13) if (x_, z_) != (10, 10) and int(BS[2].get(JInt(x_), JInt(64), JInt(z_))) == 3)
    K.check(n5 == 22 and len(got) == 22 and (9, 9) not in got and (11, 10) not in got and (10, 12) in got and int(BS[2].get(JInt(13), JInt(64), JInt(10))) == 1,
            "TT: area(5x5) around 10,64,10 on the real sections: 22 more tilled (24 minus the stone and the grass under stone; the plain dirt too), "
            "nothing outside the square: %s" % n5)
    n3 = int(Till.area(w, JInt(31), JInt(64), JInt(5), JInt(3)))
    K.check(n3 == 5 and int(BS[2].get(JInt(30), JInt(64), JInt(4))) == 3, "TT: area(3x3) at the chunk edge 31,64,5: the 3 blocks in the unloaded chunk 1,0 are skipped (5 tilled): %s" % n3)
    n1 = int(Till.area(w, JInt(3), JInt(64), JInt(20), JInt(1)))
    Till.SETB = None
    K.check(n1 == 0, "TT: side 1 = nothing extra")
    K.save()


# ====================================================================================================== D: start twice on a scratch copy
def run_start(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else OLD_JAR
    _jvm([B.SERVER_JAR, jar], verify=(which == "new"))
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    lld = os.path.join(home, "lifelong")

    def lltree():
        if not os.path.isdir(lld):
            return None
        return dict((f_, open(os.path.join(lld, f_), "rb").read()) for f_ in sorted(os.listdir(lld)))
    ll0 = lltree()          # 0.3.2: the live data has a lifelong folder since 0.3.0 went live (2026-10-13 19:54)
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218") + (("migrate031",) if which == "new" else ()):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
    K.check(snaps[1] == snaps[0], "D/%s: the 2nd start changes nothing" % which)
    if which == "new":
        K.check(bool(Cfg.LL_ON) and bool(Cfg.GATE_ON) and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12
                and str(Cfg.LL_LADDERS).startswith("Tool_Pickaxe_Crude>") and lltree() == ll0,
                "D/new (0.3.2): the live file has no lifelong / gate rows -> the defaults apply (lifelong on, gate on x0.4 / x0.1); the start never "
                "makes or touches the lifelong folder (%s)" % (None if ll0 is None else sorted(ll0)))
    K.save(cfg=snaps[0].decode("latin-1"), fresh=str(Cfg.defaultsText()), mark=(str(Cfg.GQ_MARK) if which == "new" else ""))


# ====================================================================================================== R: the 0.2.26 Anvil child + X
R26_DEVIATIONS = [
    # the tab row now has five places (Craft | Anvil | Tools | Multitool): the 0.2.26 child counts / names the tabs of the 0.2.26 row
    "N2", "tab",
]


# fix round (2026-10-14): B.SERVER_JAR is a CACHED copy now (tools/serverjar.py, tools/dev/scratch/serverjar/jar-*/HytaleServer.jar) and the
# cached Assets.zip lives in its own folder; the older harnesses (0.2.25 / 0.2.26, read only) look for Assets.zip at
# dirname(dirname(SERVER_JAR)). Their children run through WRAP with skyybuild.SERVER_JAR pinned to a hard-linked side-by-side layout in
# this harness's scratch (no copy, nothing written outside the scratch; the installed game files are never opened).
def game_assets():
    import serverjar
    return serverjar.assets_zip()


def game_layout():
    import serverjar
    g = os.path.join(SCR_ROOT, "game")
    sj = os.path.join(g, "Server", "HytaleServer.jar")
    for src, dst in ((serverjar.server_jar(), sj), (serverjar.assets_zip(), os.path.join(g, "Assets.zip"))):
        if not os.path.isfile(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.link(src, dst)
    return sj


WRAP = ("import sys, runpy; sys.path.insert(0, sys.argv[1]); import skyybuild; skyybuild.SERVER_JAR = sys.argv[2]; s = sys.argv[3]; "
        "sys.argv = [s] + sys.argv[4:]; runpy.run_path(s, run_name='__main__')")


def wrap(head):
    """[python, script] -> the same script run with skyybuild.SERVER_JAR pinned to game_layout()"""
    return [head[0], "-c", WRAP, TOOLS, game_layout(), head[1]]


def run_r26(env):
    d = os.path.join(SCRATCH, "r26")
    for sub in ("tmp", "packs"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copyfile(AR_SRC, os.path.join(d, "packs", "SkyyArmory-0.1.23.jar"))
    if os.path.isfile(MT_SRC):
        shutil.copyfile(MT_SRC, os.path.join(d, "packs", "Multitools-1.2.9.jar"))
    e2 = dict(env)
    e2["TEMP"] = e2["TMP"] = os.path.join(d, "tmp")
    h26 = os.path.join(HERE, "test_skyygear_0.2.26.py")
    base = [sys.executable, h26, "--dir", d, "--jar", JAR, "--old", OLD_JAR, "--root", SCR_ROOT]
    p0 = subprocess.run(wrap(base[:2]) + ["--mkfake", os.path.join(d, "fake")] + base[2:], env=e2, capture_output=True, text=True)
    check(p0.returncode == 0, "R: the 0.2.26 stand-ins compiled against the 0.3.0 jar (rc %s) %s" % (p0.returncode, p0.stderr[-500:]))
    out = os.path.join(d, "anvil.json")
    p = subprocess.run(wrap(base[:2]) + ["--anvil", "--out", out] + base[2:], env=e2, capture_output=True, text=True)
    check(p.returncode == 0 and os.path.isfile(out), "R: the 0.2.26 Anvil child ran with the 0.3.0 jar (rc %s)" % p.returncode)
    if not os.path.isfile(out):
        print(p.stdout[-3000:], p.stderr[-3000:])
        return
    r = json.load(open(out))
    OKS[0] += r["ok"]
    dev = [f for f in r["fails"] if "tab" in f.lower() and ("Tools" in f or "row" in f.lower() or "tabs" in f.lower())]
    other = [f for f in r["fails"] if f not in dev]
    check(not other and r["ok"] >= 50, "R: the 0.2.26 Anvil checks (reforge / level up / upgrade / identify, every click, every failure step): %d ok, "
          "no fail outside the tab row: %s" % (r["ok"], other[:6]))
    for f in dev:
        print("  expected deviation (R, the Tools tab joins the row): %s" % f[:220])


def run_x25(env):
    d = os.path.join(SCRATCH, "x25")
    os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(d, "fake"), exist_ok=True)
    out = os.path.join(d, "exec.json")
    e2 = dict(env)
    e2["TEMP"] = e2["TMP"] = os.path.join(d, "tmp")
    p = subprocess.run(wrap([sys.executable, os.path.join(HERE, "test_skyygear_0.2.25.py")]) + ["--phase", "exec", "--out", out, "--dir", d, "--jar", JAR,
                        "--old", J24], env=e2, capture_output=True, text=True)
    check(p.returncode == 0 and os.path.isfile(out), "X: the 0.2.25 harness's exec phase ran with the 0.3.0 jar (rc %s)" % p.returncode)
    if not os.path.isfile(out):
        print(p.stdout[-2000:], p.stderr[-2000:])
        return
    r = json.load(open(out))
    expected = [f for f in r["fails"] if "fresh config text" in f]
    other = [f for f in r["fails"] if "fresh config text" not in f]
    OKS[0] += r["ok"]
    check(not other and r["ok"] >= 20, "X: the randomised 0.2.24-vs-new stats comparison (snapshot, tick, hits, gate, stamp scan, chest file, bridge): "
          "%d ok, no other fail: %s" % (r["ok"], other))
    check(len(expected) <= 1, "X: its only expected deviation is the fresh config text (checked exactly in D): %s" % expected)


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake5(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--life", lambda: run_life(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--start", lambda: run_start(arg("--out"), arg("--start"), arg("--which"))), ("--audit", lambda: H["run_audit"](arg("--out"))),
                     ("--till", lambda: run_till(arg("--out")))):          # 0.3.4
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR) and os.path.isfile(CO_SRC) and os.path.isfile(AR_SRC) and os.path.isfile(J24) and os.path.isfile(J32) and os.path.isfile(J33) and os.path.isfile(J34), (JAR, OLD_JAR, CO_SRC, AR_SRC, J24, J32, J33, J34)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "%s"' % OLD_VERSION in z_.read("manifest.json").decode("utf-8"), "the old jar is not " + OLD_VERSION
    shutil.copyfile(CO_SRC, CO_JAR)              # read-only sources; the children use the scratch copies
    shutil.copyfile(FI_SRC, FI_JAR)              # 0.3.5
    for f_ in glob.glob(os.path.join(LIVE_PLAYERS, "*.json")):
        shutil.copyfile(f_, os.path.join(PLAYERS, os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    only = arg("--only")
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare"), ("life", "--life"), ("till", "--till")):          # 0.3.4: + till
            if only and label not in only.split(","):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if not only or "r26" in only.split(","):
            run_r26(env)
        if not only or "x25" in only.split(","):
            run_x25(env)
        res = {}
        if not only or "start" in only.split(","):
            for which in ("old", "new"):
                home = os.path.join(SCRATCH, "live-" + which)
                shutil.copytree(LIVE_DIR, home)
                out = os.path.join(SCRATCH, "start-%s.json" % which)
                pr = child(env, "--start", home, "--which", which, "--out", out)
                check(pr.returncode == 0, "D/%s: the child exited cleanly" % which)
                res[which] = take(out, "start-" + which)
            print("D. live Skyy_SkyyGear copied twice (read-only source %s)" % LIVE_DIR)
            if res.get("old") and res.get("new"):
                oc_, nc_, mk_ = res["old"]["cfg"], res["new"]["cfg"], res["new"].get("mark", "")
                ol_, nl_ = oc_.split("\n"), nc_.split("\n")
                gone_ = [x for x in ol_ if x not in nl_]
                more_ = [x.rstrip("\r") for x in nl_ if x not in ol_]
                if mk_ and mk_ in oc_:
                    # 0.3.2: the live file already carries the 0.3.1 marker (0.3.1 went live 2026-10-13 22:23): nothing is left to add
                    check(nc_ == oc_ and "gate.nextFactor" not in oc_,
                          "D (0.3.2): the live copy already ran the 0.3.1 update - 0.3.2 starts it to exactly the config.properties 0.2.26 writes "
                          "(no row, no marker added): + %s - %s" % (more_[:3], gone_[:3]))
                else:
                    check(mk_ and more_ == [mk_] and not gone_ and len(nl_) == len(ol_) + 1 and "gate.nextFactor" not in oc_
                          and nc_.replace(mk_ + ("\r\n" if "\r\n" in oc_ else "\n"), "", 1) == oc_,
                          "D (0.3.1): 0.3.1 starts the live copy to exactly the config.properties 0.2.26 writes + the one run-once marker line "
                          "(the live file has no gate rows: nothing to rewrite): + %s - %s" % (more_[:3], gone_[:3]))
                fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
                fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
                check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
                a_ = res["old"]["fresh"].split("\n")[1:]          # the first line names the version
                b_ = res["new"]["fresh"].split("\n")[1:]
                extra = [l_ for l_ in b_ if l_ not in a_]
                keys = [l_.split("=")[0] for l_ in extra if not l_.startswith("#") and l_]
                check([l_ for l_ in a_ if l_ not in b_] == [] and extra[0] == "# ---- lifelong tools + the tool tier gate (SkyyGear 0.3.0) ----"
                      and keys == ["part.lifelong", "lifelong.noCraft", "lifelong.noDrop", "lifelong.ladders", "lifelong.reclaimSec", "lifelong.reclaimTier", "lifelong.repickDays",
                                   "lifelong.perkSpeed", "lifelong.perkFortune", "lifelong.perkWisdom", "lifelong.resetCoins", "gate.on", "gate.nextFactor",
                                   "gate.twoUpFactor", "gate.crudeFactor", "gate.bareHands",
                                   "part.sigils", "sigil.mythicUse", "garmor.levels", "garmor.ladders", "hoe.areaOn", "hoe.area", "hoe.areaElsewhere",          # 0.3.4
                                   "lifelong.rebirthPct", "multi.rebirthGate"]          # 0.3.5
                      and "# ---- sigils, gathering armor levels, the hoe till area (SkyyGear 0.3.4) ----" in extra
                      and "# ---- the fishing pole, rebirth (SkyyGear 0.3.5) ----" in extra
                      and extra[1] == res["new"].get("mark"),
                      "D (0.3.1): a FRESH default file differs from 0.2.26's only by the lifelong block (+ gate.twoUpFactor, + the 0.3.1 marker right "
                      "under its heading - a fresh file never runs migrate031): %s" % extra[:4])
        if not only or "audit" in only.split(","):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
                check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
                print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
