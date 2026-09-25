"""Derive SkyyTrees/build_skyytrees_0.2.3.py from build_skyytrees_0.2.2.py (the trees_0_2_2_patch.py style: rep(old, new) with asserted
single anchors, newline-agnostic; 0.2.2 stays untouched and its CRLF line endings are kept). Edit THIS file, not the generated script.
0.2.3 = research/Swing-Speed-Spec.md (Skyy's report 2026-09-25: "once you have a pick that can break a block in one hit, you are limited
by how fast you swing the pick. so mining speed needs to increase how fast you swing your pick"). SkyyTrees 0.2.2 is the LIVE jar
(tools/deploy_set.py SET). Mining Speed / Chopping Speed become swing-speed nodes (a hidden per-player "swing tier" status effect +
SkyyTrees' own override of the vanilla Pickaxe_Attack / Hatchet_Attack root that shortens the 0.35 s left-click cooldown for that tier);
Heavy Pick / Heavy Hatchet (was Chopping Speed II) stay breaking power. No SkyySkills / SkyyAccessories / SkyyClasses change.
Run:  python tools/trees_0_2_3_patch.py   then   python SkyyTrees/build_skyytrees_0.2.3.py   (NO --deploy: coordinated deploy)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.2.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.2.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2.2"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:100]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:100])
    s = s.replace(old, new)


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


# ================================================================ header / version
rep('''"""SkyyTrees 0.2.2 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.1.py by tools/trees_0_2_2_patch.py - edit the patch, not this file (0.2.1 stays untouched; 0.2.1 was
derived from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py).
0.2.2 = in-game server setup''', r'''"""SkyyTrees 0.2.3 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
DERIVED from build_skyytrees_0.2.2.py by tools/trees_0_2_3_patch.py - edit the patch, not this file (0.2.2 stays untouched; 0.2.2 was
derived from 0.2.1 by tools/trees_0_2_2_patch.py, 0.2.1 from 0.2 by tools/trees_0_2_1_patch.py, 0.2 from 0.1 by tools/trees_0_2_patch.py).
0.2.3 = research/Swing-Speed-Spec.md. Skyy's report (2026-09-25): "the mining skill tree increases mining speed. but once you have a pick
  that can break a block in one hit, you are limited by how fast you swing the pick. so mining speed needs to increase how fast you swing
  your pick." The limit is the engine's default left-click cooldown (InteractionTypeUtils.getDefaultCooldown(Primary) = 0.35 s) over a
  0.25 s vanilla swing - the vanilla Pickaxe_Attack / Hatchet_Attack roots set no Cooldown of their own. Breaking power cannot beat one
  block per 0.35 s.
  MECHANISM (spec 2, the Hylamity 0.2.0 pattern; all stock engine interaction types, no new Java interaction class):
    - 40 hidden "swing tier" effects per tool, Server/Entity/Effects/SkyyTrees/Skyy_Tree_Swing_Mine_01..40 and _Chop_01..40
      ({"Duration": 3, "OverlapBehavior": "Overwrite"}, no icon, no stats).
    - Interactions Skyy_Tree_Swing_Mine / _Chop: a decision tree of instant EffectCondition (Match None) steps - the top node sends a
      player without any tier straight to the vanilla Interaction Pickaxe_Attack / Hatchet_Attack (unchanged vanilla swing and cadence);
      a player with tier k reaches the leaf TriggerCooldown {Id "Pickaxe_Attack" / "Hatchet_Attack", Cooldown round(0.35 / (1 + k/100), 4)}
      and then the same vanilla interaction. 6 levels deep, 0 extra time (instant steps run in the same tick). The vanilla swing, its
      animation, the block break at 0.133 s and the sounds are untouched; only the idle gap after the swing shrinks (+40 % = 0.25 s =
      back-to-back swings = the ceiling).
    - OVERRIDES of two vanilla files, same path and id: Server/Item/RootInteractions/Weapons/Pickaxe/Variants/Pickaxe_Attack.json =
      {"Interactions": ["Skyy_Tree_Swing_Mine"]} and .../Hatchet/Variants/Hatchet_Attack.json = {"Interactions": ["Skyy_Tree_Swing_Chop"]}
      - still no Cooldown key, so the engine default (0.35 s, id = the root id, reset on start) stays exactly as vanilla. Every item whose
      Primary root is Pickaxe_Attack / Hatchet_Attack (every vanilla pickaxe / hatchet via Tool_*_Crude) gets it; nothing else does, so
      "only while holding the tool" is built in and switching tools needs no check. Combat axes, the Bark Scraper and hoes are untouched.
    - Everything is GENERATED at build time from Assets.zip read in memory (no game file in the repo) with self-checks (spec 3.7): the
      vanilla roots are still exactly {"Interactions": [<same id>]} with no Cooldown, the vanilla Interactions exist and chain into
      Pickaxe_Mine / Hatchet_Chop, Tool_Pickaxe_Crude / Tool_Hatchet_Crude still use those Primary roots; the swing length worked out
      from Pickaxe_Mine / Hatchet_Chop (RunTime + longest Parallel branch, following Next / Failed / Replace defaults and a Selector's
      forked HitEntity / HitEntityRules / HitBlock chains - conservative) is <= 0.25 s and no tier cooldown is shorter than it; getDefaultCooldown still loads float 0.35 (javassist); a python walk of each generated tree lands
      every tier 0..40 on the right leaf; every referenced id exists and no generated id collides with a vanilla one except the 2 roots.
      The jar is now an asset pack (manifest IncludesAssetPack true, 84 JSON files: 80 effects, 2 decision trees, 2 root overrides).
  NODES (ids, slots, icons, B, tokens and max levels unchanged; KINDS += SWING = 23, every older kind number unchanged):
    - Mining S1 MSpeed "Mining Speed": SWING, max 25, per 0.01 = +1 % pickaxe swing speed per level, +25 % at max (a swing every 0.28 s
      instead of 0.35 s). NOW "+%V pickaxe swing speed".
    - Mining S10 MHeavy "Heavy Pick": unchanged DMG (+2 % breaking power on ORE per level, +40 %); text "+%V breaking power on ore".
    - Foraging S1 FSpeed "Chopping Speed": SWING like Mining Speed, for hatchets.
    - Foraging S10 FSpeed2 renamed "Heavy Hatchet" (was Chopping Speed II): unchanged DMG on wood (+40 %). Id and saved key stay FSpeed2.
    - TreeFx.dmgBonus: rock no longer gets MSpeed, wood no longer gets FSpeed: ore -> + MHeavy, Woods -> + FSpeed2 only.
    - TreeFx.value(SWING) = the EFFECTIVE fraction min(floor(per x level x 100 + 1e-6), 40) / 100 (whole percents, capped at +40 %), so the
      page and tree:fn:bonus("Mining.MSpeed") show what really applies; TreeDefs.valueText shows a whole percent, " (max)" at 40.
    - Farming: no change (no speed node, no multi-swing cadence, every slot taken).
  APPLYING (TreeSwing, called from the existing TreeTick after TreeFx.stats - world thread, once a second, NO new system):
    - ready(): resolves the 80 effect indexes (EntityEffect.getAssetMap().getIndex) the first time a player ticks; a missing id warns once
      ("swing effects missing - asset pack not loaded?") and keeps the bonus off (retried every 10 s). Then logs ONE line "swing speed
      ready: 80 effects, pickaxe root = SkyyTrees, hatchet root = SkyyTrees" (RootInteraction.getAssetMap().getAsset(id)
      .getInteractionIds()[0]); another mod's root is warned about, the effects are still applied (harmless).
    - apply(): tier = round(value x 100) from the fresh v[] of Mining Speed / Chopping Speed (0 with swing.enabled=false); every other
      tier effect of that family is removed, the wanted one is (re)added for 3 s (OverlapBehavior.OVERWRITE) when it is missing or has
      under 1.5 s left. Finite on purpose (an infinite effect would be saved with the player forever). Respec, node off, enabled=false,
      level change, profile switch (epoch -> compute reads the new profile) and swing.enabled OFF all correct the effect within 1 s;
      world switch: TreeTick runs in the new world; logout: at most 3 s left in the save, re-checked within 1 s of the next join.
  CONFIG (trees.properties, TreeCfg.load, before CfgPub.start so the kit's snapshot already has it and it is not a hand edit):
    - new key swing.enabled (default true) -> volatile TreeCfg.SWING_ON; the load summary says ", tool swing speed OFF" when false, the
      two nodes' "Now:" line says "turned off on this server (Faster tool swings is OFF)" and tree:fn:bonus answers 0 for them.
    - ONE-TIME MIGRATION of a file without swing.enabled (spec 4.2, the 0.2.1 Feller pattern: ISO-8859-1 text, exact key and value
      match, TreeCfg.writeAtomic, settings parsed from exactly the new content): the untouched old default lines Mining.MSpeed.per=0.02
      and Foraging.FSpeed.per=0.02 become 0.01; CUSTOM values are kept with a server-log warning ("Mining.MSpeed.per=X kept - since 0.2.3
      it is pickaxe swing speed per level (0.01 = 1%, capped at +40%)"); the 0.2.3 block (comments + swing.enabled=true) is appended.
      Nothing else in the file changes. A 0.1 / 0.2 / 0.2.1 file gets every older block plus this one in the same single write. A fresh
      file already has swing.enabled and the 0.01 lines (comment "# Foraging S10 Heavy Hatchet (tier V)").
    - SERVER SETUP (tools/skyycfg.py): new row swing.enabled "Faster tool swings" (abilities, bool, live, reload) - config:def goes from
      24 to 25 rows. The nodes.Mining / nodes.Foraging tables are unchanged in shape; MSpeed.per / FSpeed.per now mean swing speed.
      TreeKit.checkNode ASKS FIRST when a SWING node's per x max goes over 0.40 ("?Mining Speed would reach +50% - swings are capped at
      +40% (then they are back to back). Save it anyway?") for a typed per (x the current max) or a typed max (x the current per).
      Deviation: the spec's help text (117 characters) is over the kit's 100-character limit, so the row says "ON: Mining / Chopping
      Speed shorten the wait between pickaxe / hatchet swings. OFF: they do nothing."
  SAVED DATA: player files unchanged (levels, off flags, respec times; Tokens and Dust are recomputed, never stored, so every balance is
    identical). New key note.swing=1 per profile file: the ONE-TIME chat notice (Q7 default yes) on the first tick where the profile has
    MSpeed, FSpeed or FSpeed2 above 0: "[Trees] Mining Speed now makes your pickaxe swing faster (it no longer adds breaking power).
    Chopping Speed does the same for hatchets. Chopping Speed II is now Heavy Hatchet (breaking power on wood). A respec is free if you
    want to spend your Dust again." Additions: with respec.coins > 0 the last sentence says "You can respec the tree in /tree if you
    want to spend your Dust again." (so the line never claims a free respec that costs coins); unlocking one of those three nodes in
    0.2.3 sets note.swing (a new owner never gets the "no longer adds breaking power" line); skipped while profile:busy is set.
  ADMIN: /tree swing (requirePermission skyytrees.admin + an empty permission-group list, the HANDOFF rule) prints your pickaxe and
    hatchet tiers with their seconds per swing, the tier effects active right now, swing.enabled and whether the two roots are SkyyTrees'.
  UNVERIFIED (needs Skyy's in-game test): that the CLIENT swings faster too (it runs the same EffectCondition / TriggerCooldown chain
    and gets the effect through EntityEffectUpdate - this rests on Hylamity shipping the same pattern, not on a test); that the hidden
    effect shows no status icon or empty HUD slot (Q8); that SkyyTrees' root overrides win over the vanilla files in a running server;
    no rubber-banding / block pop-back right after a tier change; what the engine does with a saved Skyy_Tree_Swing_* effect after
    SkyyTrees is removed (turn swing.enabled off and wait 5 s before uninstalling).
  TEST: research/Swing-Speed-Spec.md section 7 (B).

=== SkyyTrees 0.2.2 notes (history; still true unless 0.2.3 above says otherwise) ===
0.2.2 = in-game server setup''')
rep('''Run:   python build_skyytrees_0.2.2.py            -> SkyyTrees/SkyyTrees-0.2.2.jar
       python build_skyytrees_0.2.2.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''',
    '''Run:   python build_skyytrees_0.2.3.py            -> SkyyTrees/SkyyTrees-0.2.3.jar
       python build_skyytrees_0.2.3.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)''')
rep('VERSION = "0.2.2"', 'VERSION = "0.2.3"')

# ================================================================ engine tokens + API probes (spec 6 item 8)
rep('''    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
}''', '''    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    # 0.2.3 swing speed (research/Swing-Speed-Spec.md 2.1, verified with tools/dev/reflect.py against HytaleServer.jar 2026-09-25)
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "AEE": "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "OVB": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
    "RIN": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction",
    "I2O": "it.unimi.dsi.fastutil.ints.Int2ObjectMap",
}''')
rep('''             ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove")):''',
    '''             ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove"),
             ("ECC", "getComponentType"), ("ECC", "getActiveEffects"), ("ECC", "addEffect"), ("ECC", "removeEffect"),
             ("EFX", "getAssetMap"), ("AEE", "getRemainingDuration"), ("OVB", "OVERWRITE"), ("RIN", "getAssetMap"),
             ("RIN", "getInteractionIds"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), ("I2O", "get")):''')

# ================================================================ nodes (spec 3.1)
rep('''  ("MSpeed", "Mining Speed", "Tool_Pickaxe_Iron", "DMG", 25, 0.02, 0, "+%V breaking power on rock and ore", "Rock and ore blocks break in fewer hits (more damage per hit)", "", ""),''',
    '''  ("MSpeed", "Mining Speed", "Tool_Pickaxe_Iron", "SWING", 25, 0.01, 0, "+%V pickaxe swing speed", "Less wait between pickaxe swings - more blocks per second, even when one hit breaks the block (any pickaxe, also on mobs)", "", ""),''')
rep('''  ("MHeavy", "Heavy Pick", "Tool_Pickaxe_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on ore - adds to Mining Speed", "Ore blocks only - with both maxed ore takes x1.9 damage per hit", "", ""),''',
    '''  ("MHeavy", "Heavy Pick", "Tool_Pickaxe_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on ore", "Ore blocks only - ore breaks in fewer hits (more damage per hit)", "", ""),''')
rep('''  ("FSpeed", "Chopping Speed", "Tool_Hatchet_Iron", "DMG", 25, 0.02, 0, "+%V breaking power on wood", "Wood blocks break in fewer hits (more damage per hit)", "", ""),''',
    '''  ("FSpeed", "Chopping Speed", "Tool_Hatchet_Iron", "SWING", 25, 0.01, 0, "+%V hatchet swing speed", "Less wait between hatchet swings - more logs per second (any hatchet, also on mobs)", "", ""),''')
rep('''  ("FSpeed2", "Chopping Speed II", "Tool_Hatchet_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on wood - adds to Chopping Speed", "Stacks with Chopping Speed", "", ""),''',
    '''  ("FSpeed2", "Heavy Hatchet", "Tool_Hatchet_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on wood", "Wood blocks break in fewer hits (more damage per hit)", "", ""),''')
after('''assert KINDS.index("DJUMP") == 22
''', '''_KINDS_022 = list(KINDS)
KINDS += ["SWING"]   # 0.2.3 swing speed (research/Swing-Speed-Spec.md 3.1; existing kind numbers unchanged)
assert KINDS.index("SWING") == 23 and KINDS[:23] == _KINDS_022 and len(_KINDS_022) == 23
assert _KINDS_022 == ["DMG", "DD", "XP", "HP", "STA", "ITEM", "EXTRA", "COINS", "SPREAD", "MOVE", "VEIN", "FELLER", "EXTRA2", "COOK", "MASTER",
                      "RSPD", "RJMP", "RFALL", "RDODGE", "LUCK", "SCAV", "SOON", "DJUMP"]
''')

# ================================================================ swing assets, generated in memory from Assets.zip (spec 2.3 + 3.7)
before('''# ================= default trees.properties =================
''', r'''# ================= 0.2.3 swing speed assets (research/Swing-Speed-Spec.md 2.3 + 3.7) =================
# Generated from Assets.zip read IN MEMORY (read-only); only our own JSON goes into the jar, no vanilla file is copied into the repo.
# Every self-check below fails the build (SystemExit) when a Hytale update changed what this design relies on.
SWING_MAX = 40          # tiers +1 % .. +40 %; +40 % = 0.25 s = the vanilla swing length = back-to-back swings (the ceiling)
SWING_BASE = 0.35       # InteractionTypeUtils.getDefaultCooldown(Primary) - self-check 3 re-reads it from the server jar
SWING_EFFECT = {"Duration": 3, "OverlapBehavior": "Overwrite"}   # hidden marker: no icon, no ApplicationEffects, no stats
# (family, vanilla root id = vanilla Interaction id = cooldown id, vanilla tool item, vanilla swing interaction, root path in Assets.zip)
SWING_FAMS = [("Mine", "Pickaxe_Attack", "Tool_Pickaxe_Crude", "Pickaxe_Mine", "Server/Item/RootInteractions/Weapons/Pickaxe/Variants/Pickaxe_Attack.json"),
              ("Chop", "Hatchet_Attack", "Tool_Hatchet_Crude", "Hatchet_Chop", "Server/Item/RootInteractions/Weapons/Hatchet/Variants/Hatchet_Attack.json")]
def swing_id(fam, k): return "Skyy_Tree_Swing_%s_%02d" % (fam, k)
def swing_tree_id(fam): return "Skyy_Tree_Swing_" + fam
SWING_CD = [SWING_BASE] + [round(SWING_BASE / (1.0 + k / 100.0), 4) for k in range(1, SWING_MAX + 1)]
assert SWING_CD[25] == 0.28 and SWING_CD[40] == 0.25 and SWING_CD[5] == 0.3333 and SWING_CD[1] == 0.3465
assert all(SWING_CD[k] < SWING_CD[k - 1] for k in range(1, SWING_MAX + 1))
def swing_tree(fam, target):
    ids = [None] + [swing_id(fam, k) for k in range(1, SWING_MAX + 1)]
    def leaf(k):
        return {"Type": "TriggerCooldown", "Cooldown": {"Id": target, "Cooldown": SWING_CD[k]}, "Next": target}
    def split(lo, hi):
        if lo == hi: return leaf(lo)
        mid = (lo + hi + 1) // 2
        return {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": ids[mid:hi + 1], "Next": split(lo, mid - 1), "Failed": split(mid, hi)}
    return {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": ids[1:], "Next": target, "Failed": split(1, SWING_MAX)}
SWING_FILES = {}
with zipfile.ZipFile(ASSETS) as _z:
    _names = _z.namelist()
    def _ids(prefix):
        out = {}
        for n in _names:
            if n.startswith(prefix) and n.endswith(".json"):
                out.setdefault(os.path.basename(n)[:-5], []).append(n)
        return out
    def _rd(path): return json.loads(_z.read(path).decode("utf-8-sig"))
    V_EFF, V_INT, V_ROOT, V_ITEM = (_ids("Server/Entity/Effects/"), _ids("Server/Item/Interactions/"), _ids("Server/Item/RootInteractions/"),
                                    _ids("Server/Item/Items/"))
    def _one(m, i, what):
        if i not in m: raise SystemExit("swing self-check: vanilla %s %s is missing" % (what, i))
        if len(m[i]) != 1: raise SystemExit("swing self-check: vanilla %s %s exists %d times: %s" % (what, i, len(m[i]), m[i]))
        return m[i][0]
    # swing length = RunTime + longest Parallel branch + the longest of Next / Failed / a Selector's hit chains, following string ids and
    # Replace defaults (a list of interactions runs one after the other). Pickaxe_Mine: 0.083 + max(0.05 + break, 0.083 + max(0.084,
    # hit 0), 0.167) = 0.25. CONSERVATIVE on purpose: the 2nd+ Parallel branches and a Selector's HitEntity / HitEntityRules[].Next /
    # HitBlock chains are FORKED chains (ParallelInteraction.tick0 / SelectInteraction.tick0 -> InteractionContext.fork, bytecode
    # 2026-09-25), counted as if they kept the swing busy; a hit chain forks while the Selector runs, so it ends at most RunTime + its
    # own length after that step starts (the same slot as Next).
    # a root-valued field (Parallel branch, Replace default, Selector hit chain): inline {"Interactions": [...]} or a RootInteraction id
    def _root(r, depth):
        if r is None: return 0.0
        if isinstance(r, str): return _dur(_rd(_one(V_ROOT, r, "root interaction")).get("Interactions"), depth + 1)
        if not isinstance(r, dict): raise SystemExit("swing self-check: unexpected root interaction value %r" % (r,))
        return _dur(r.get("Interactions"), depth + 1)
    def _dur(x, depth=0):
        if depth > 40: raise SystemExit("swing self-check: interaction nesting too deep near %r" % (x,))
        if x is None: return 0.0
        if isinstance(x, str): return _dur(_rd(_one(V_INT, x, "interaction")), depth + 1)
        if isinstance(x, list): return sum(_dur(e, depth + 1) for e in x)
        if not isinstance(x, dict): raise SystemExit("swing self-check: unexpected interaction node %r" % (x,))
        typ = x.get("Type")
        if typ == "Chaining": raise SystemExit("swing self-check: a Chaining step inside the swing - the swing-length check needs a look")
        if x.get("WaitForAnimationToFinish"): raise SystemExit("swing self-check: a WaitForAnimationToFinish step - the swing length now follows the animation")
        t = float(x.get("RunTime", 0) or 0)
        if typ == "Parallel": t += max(_root(b, depth + 1) for b in x["Interactions"])
        elif typ == "Replace": t += _root(x.get("DefaultValue"), depth + 1)
        tail = [_dur(x.get("Next"), depth + 1), _dur(x.get("Failed"), depth + 1)]
        if typ == "Selector":
            tail.append(_root(x.get("HitEntity"), depth + 1))
            tail.append(_root(x.get("HitBlock"), depth + 1))
            for _r in (x.get("HitEntityRules") or []):
                if not isinstance(_r, dict): raise SystemExit("swing self-check: unexpected HitEntityRules entry %r" % (_r,))
                tail.append(_root(_r.get("Next"), depth + 1))
        return t + max(tail)
    for fam, root, tool, swing, rpath in SWING_FAMS:
        tid = swing_tree_id(fam)
        # check 1: the vanilla root, interaction and tool this build overrides / points at
        if _one(V_ROOT, root, "root interaction") != rpath: raise SystemExit("swing self-check: root %s moved: %s" % (root, V_ROOT[root]))
        if _rd(rpath) != {"Interactions": [root]}:
            raise SystemExit("swing self-check: vanilla root %s is no longer exactly {\"Interactions\": [\"%s\"]} (no Cooldown): %s" % (root, root, json.dumps(_rd(rpath))))
        _vi = _rd(_one(V_INT, root, "interaction"))
        if _vi.get("Type") != "Chaining" or _vi.get("Next") != [swing]:
            raise SystemExit("swing self-check: vanilla interaction %s no longer chains into %s: %s" % (root, swing, json.dumps(_vi)))
        _ti = _rd(_one(V_ITEM, tool, "item"))
        if (_ti.get("Interactions") or {}).get("Primary") != root:
            raise SystemExit("swing self-check: %s no longer uses the Primary root %s: %s" % (tool, root, json.dumps(_ti.get("Interactions"))))
        # check 2: no tier cooldown is shorter than the vanilla swing
        _len = _dur(swing)
        if _len > 0.25 + 1e-9: raise SystemExit("swing self-check: %s now lasts %.4f s (> 0.25 s) - the +%d%% tier would cut into the swing" % (swing, _len, SWING_MAX))
        if min(SWING_CD) < _len - 1e-9: raise SystemExit("swing self-check: a tier cooldown (%.4f s) is shorter than the %s swing (%.4f s)" % (min(SWING_CD), swing, _len))
        # check 5 (collisions): our ids are new; only the root is an intended override (same path, same id)
        for k in range(1, SWING_MAX + 1):
            if swing_id(fam, k) in V_EFF: raise SystemExit("swing self-check: vanilla already has an effect " + swing_id(fam, k))
        if tid in V_INT or tid in V_ROOT or tid in V_EFF: raise SystemExit("swing self-check: vanilla already has an asset " + tid)
        tree = swing_tree(fam, root)
        # check 4: walk the generated tree for every tier (EffectCondition Match None fails when ANY listed effect is active)
        def _walk(node, have):
            depth = 0
            while isinstance(node, dict) and node["Type"] == "EffectCondition":
                assert node["Match"] == "None" and node["EntityEffectIds"], node
                node = node["Failed"] if any(e in have for e in node["EntityEffectIds"]) else node["Next"]
                depth += 1
            return node, depth
        _deep = 0
        for k in range(0, SWING_MAX + 1):
            got, d = _walk(tree, set([swing_id(fam, k)]) if k else set())
            _deep = max(_deep, d)
            if k == 0:
                if got != root: raise SystemExit("swing self-check: tier 0 does not reach the vanilla %s: %r" % (root, got))
            elif not (isinstance(got, dict) and got["Type"] == "TriggerCooldown" and got["Next"] == root and got["Cooldown"]["Id"] == root
                      and got["Cooldown"]["Cooldown"] == SWING_CD[k]):
                raise SystemExit("swing self-check: tier %d reaches %r" % (k, got))
        assert _deep == 7, _deep   # top node + 6 split levels
        # check 5 (references): every EffectCondition id is one of ours, every string Next is the vanilla interaction
        def _refs(node, effs, nexts):
            if isinstance(node, str): nexts.add(node); return
            for e in node.get("EntityEffectIds", []): effs.add(e)
            for key in ("Next", "Failed"):
                if key in node: _refs(node[key], effs, nexts)
        _effs, _nexts = set(), set()
        _refs(tree, _effs, _nexts)
        assert _effs == set(swing_id(fam, k) for k in range(1, SWING_MAX + 1)) and _nexts == set([root]) and root in V_INT
        for k in range(1, SWING_MAX + 1):
            SWING_FILES["Server/Entity/Effects/SkyyTrees/%s.json" % swing_id(fam, k)] = json.dumps(SWING_EFFECT, indent=2)
        SWING_FILES["Server/Item/Interactions/SkyyTrees/%s.json" % tid] = json.dumps(tree, indent=2)
        SWING_FILES[rpath] = json.dumps({"Interactions": [tid]}, indent=2)
assert len(SWING_FILES) == 2 * SWING_MAX + 4
for _p, _t in SWING_FILES.items():
    assert json.loads(_t) is not None and all(ord(ch) < 128 for ch in _t) and _p.startswith("Server/"), _p
# check 3: the base the tier numbers are computed from - InteractionTypeUtils.getDefaultCooldown still returns (ldc) float 0.35
import jpype as _jp
_IP = _jp.JClass("javassist.bytecode.InstructionPrinter")
_bos = _jp.JClass("java.io.ByteArrayOutputStream")()
_ITU = pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.InteractionTypeUtils")
_IP(_jp.JClass("java.io.PrintStream")(_bos)).print_(_ITU.getDeclaredMethod("getDefaultCooldown"))
_gdc = str(_bos.toString())
if not re.search(r"ldc(_w)? #\d+ = float 0\.35\b", _gdc):
    raise SystemExit("swing self-check: InteractionTypeUtils.getDefaultCooldown no longer loads float 0.35 - every tier number would be wrong:\n" + _gdc)

''')

# ================================================================ default trees.properties + the 0.2.3 migration block (spec 4.2)
SWING_CFG_COMMENT = '''      "# Swing speed (0.2.3): Mining Speed / Chopping Speed shorten the wait between pickaxe / hatchet swings. Their per = fraction per",
      "# level (0.01 = 1%), whole percents, capped at +40% (then the swings are back to back). false = those two nodes do nothing.",
'''
after('''      "felled.nodes=true",
''', SWING_CFG_COMMENT + '''      "swing.enabled=true",
''')
after('''assert "Acrobatics." not in ADD021FEL and "feller." not in ADD021DJ
''', '''# 0.2.3: appended ONCE to any older file (no swing.enabled key), right after the untouched old default lines Mining.MSpeed.per=0.02 /
# Foraging.FSpeed.per=0.02 were rewritten in place to 0.01 (TreeCfg.migrateSwing). It only ADDS keys: a second MSpeed / FSpeed line here
# would override a custom value.
ADD023 = "\\n".join([
    "# ---------- SkyyTrees 0.2.3 (added once): swing speed ----------",
    "# Mining Speed / Chopping Speed no longer add breaking power: they shorten the wait between pickaxe / hatchet swings.",
    "# The old default lines Mining.MSpeed.per=0.02 / Foraging.FSpeed.per=0.02 were changed to 0.01 (custom values were kept).",
    "# Foraging S10 Chopping Speed II (the Foraging.FSpeed2 lines) is now called Heavy Hatchet - still breaking power on wood.",
''' + SWING_CFG_COMMENT.replace('      "', '    "') + '''    "swing.enabled=true"]) + "\\n"
assert all(ord(ch) < 128 for ch in ADD023)
assert "swing.enabled=true" in DEFAULTS and "swing.enabled=true" in ADD023 and DEFAULTS.count("swing.enabled=") == 1
assert not [l for l in ADD023.splitlines() if not l.startswith("#") and l != "swing.enabled=true"]
assert "Mining.MSpeed.per=0.01" in DEFAULTS and "Foraging.FSpeed.per=0.01" in DEFAULTS and "Foraging.FSpeed2.per=0.02" in DEFAULTS
assert "Mining.MHeavy.per=0.02" in DEFAULTS and "# Foraging S10 Heavy Hatchet (tier V)" in DEFAULTS and "Chopping Speed II" not in DEFAULTS
''')

# ================================================================ classes
after('''fx = pool.makeClass(PKG + ".TreeFx")
''', '''swg = pool.makeClass(PKG + ".TreeSwing")   # 0.2.3 swing speed (no system - called from TreeTick)
''')
after('''rcmd = pool.makeClass(PKG + ".TreeReloadCmd", pool.get(T["APC"]))
''', '''scmd = pool.makeClass(PKG + ".TreeSwingCmd", pool.get(T["APC"]))   # 0.2.3 /tree swing (admin)
''')

# ================================================================ TreeDefs.valueText (spec 3.1)
rep('''  if (k == @K_DJUMP@) return pct(v);
  return pct(v);''', '''  if (k == @K_DJUMP@) return pct(v);
  if (k == @K_SWING@) { long p = Math.round(v * 100.0); return p + "%" + (p >= 40L ? " (max)" : ""); }
  return pct(v);''')

# ================================================================ TreeCfg: swing.enabled, the 0.2.3 migration (spec 4.2)
after('''F(cfg, "public static final String ADD021FEL = " + json.dumps(ADD021FEL) + ";")
''', '''F(cfg, "public static final String ADD023 = " + json.dumps(ADD023) + ";")
''')
rep('''             "int FELLER_ALL = 64", "boolean FELLED_NODES = true",''',
    '''             "int FELLER_ALL = 64", "boolean FELLED_NODES = true", "boolean SWING_ON = true",''')
after('''  FELLED_NODES = bool(p, "felled.nodes", true);
''', '''  SWING_ON = bool(p, "swing.enabled", true);
''')
before('''# ONE atomic write for everything an older trees.properties is missing''', r'''# 0.2.3 swing speed: the untouched old default lines Mining.MSpeed.per=0.02 / Foraging.FSpeed.per=0.02 -> 0.01 (n[0] = lines changed);
# a custom value is kept (upgrade warns about it)
M(cfg, r"""
public static String migrateSwing(String text, int[] n) {
  String[] ls = text.split("\n", -1);
  StringBuilder sb = new StringBuilder(text.length() + 16);
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    String r = migrateLine(ln, "Mining.MSpeed.per", "0.02", "0.01");
    if (r == null) r = migrateLine(ln, "Foraging.FSpeed.per", "0.02", "0.01");
    if (r != null) { ln = r; n[0] = n[0] + 1; }
    if (i > 0) sb.append('\n');
    sb.append(ln);
  }
  return sb.toString();
}""")
''')
rep('''# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer). The returned''',
    '''# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer), the 0.2.3 swing
# migration + block (any file without swing.enabled - research/Swing-Speed-Spec.md 4.2). The returned''')
rep('''  boolean needFel = p.getProperty("feller.maxPerLayer") == null;
  if (!need02 && !needDj && !needFel) return p;''', '''  boolean needFel = p.getProperty("feller.maxPerLayer") == null;
  boolean need023 = p.getProperty("swing.enabled") == null;
  if (!need02 && !needDj && !needFel && !need023) return p;''')
rep('''    if (needFel) text = migrateFeller(text, n);''', '''    if (needFel) text = migrateFeller(text, n);
    int[] n2 = new int[1];
    if (need023) text = migrateSwing(text, n2);''')
rep(r'''    if (needFel) sb.append("\n").append(ADD021FEL);''', r'''    if (needFel) sb.append("\n").append(ADD021FEL);
    if (need023) sb.append("\n").append(ADD023);''')
rep('''      info("updated " + FILE + " for SkyyTrees 0.2.1:" + (need02 ? " added the 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates);" : "") + (needDj ? " added the Double Jump lines;" : "") + (needFel ? " Tree Feller rework (" + n[0] + " old default line(s) changed, feller.maxPerLayer added)" : ""));''',
    '''      info("updated " + FILE + " for SkyyTrees 0.2.3:" + (need02 ? " added the 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates);" : "") + (needDj ? " added the Double Jump lines;" : "") + (needFel ? " Tree Feller rework (" + n[0] + " old default line(s) changed, feller.maxPerLayer added);" : "") + (need023 ? " swing speed (" + n2[0] + " old default Mining Speed / Chopping Speed line(s) changed to per=0.01, swing.enabled added)" : ""));''')
rep('''    warn("could not read trees.properties for the 0.2.1 update (the Tree Feller defaults are migrated in memory only): " + t);''',
    '''    warn("could not read trees.properties for the update (the old default values are migrated in memory only): " + t);''')
rep('''      if ("30".equals(str(q, "feller.cooldownSec", ""))) q.setProperty("feller.cooldownSec", "5");
    }''', '''      if ("30".equals(str(q, "feller.cooldownSec", ""))) q.setProperty("feller.cooldownSec", "5");
    }
    if (need023) {
      if ("0.02".equals(str(q, "Mining.MSpeed.per", ""))) q.setProperty("Mining.MSpeed.per", "0.01");
      if ("0.02".equals(str(q, "Foraging.FSpeed.per", ""))) q.setProperty("Foraging.FSpeed.per", "0.01");
    }''')
after('''  if (needDj && hasPrefix(q, "Acrobatics.RDodge.")) info("Acrobatics.RDodge.* lines in trees.properties are unused since 0.2.1 (Quick Dodge became Double Jump) - you can delete them");
''', '''  if (need023) {
    String mp = q.getProperty("Mining.MSpeed.per");
    String fp = q.getProperty("Foraging.FSpeed.per");
    if (mp != null && !"0.01".equals(mp.trim())) warn("Mining.MSpeed.per=" + mp.trim() + " kept - since 0.2.3 it is pickaxe swing speed per level (0.01 = 1%, capped at +40%)");
    if (fp != null && !"0.01".equals(fp.trim())) warn("Foraging.FSpeed.per=" + fp.trim() + " kept - since 0.2.3 it is hatchet swing speed per level (0.01 = 1%, capped at +40%)");
  }
''')
rep('''+ rt.toString() + (EXTRA_TOKENS > 0L''', '''+ rt.toString() + (SWING_ON ? "" : ", tool swing speed OFF") + (EXTRA_TOKENS > 0L''')

# ================================================================ TreeData / TreeStore: note.swing (spec 4.1)
after('''F(dat, "public boolean quiet;")
''', '''F(dat, "public boolean noteSwing;")   # 0.2.3: the one-time swing-speed chat notice was shown for this profile (file key note.swing=1)
''')
after('''    d.quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
''', '''    d.noteSwing = "1".equals(String.valueOf(p.getProperty("note.swing")).trim());
''')
after('''  p.setProperty("quiet", d.quiet ? "true" : "false");
''', '''  if (d.noteSwing) p.setProperty("note.swing", "1");
''')
after('''M(sto, r"""
public static synchronized void setName(@PKG@.TreeData d, String n) {
  if (n != null && n.length() > 0) d.name = n;
}""")
''', '''# 0.2.3: true once per profile (the caller then marks the file dirty and, from the tick, sends the notice)
M(sto, r"""
public static synchronized boolean setNote(@PKG@.TreeData d) {
  if (d.noteSwing) return false;
  d.noteSwing = true;
  return true;
}""")
''')

# ================================================================ TreeFx: SWING value, breaking power without the old speed nodes (spec 3.1)
rep('''  if (k == @K_MASTER@) return per * (double) (eff - 1);
  return per * (double) eff;''', '''  if (k == @K_MASTER@) return per * (double) (eff - 1);
  if (k == @K_SWING@) {
    double sp = Math.floor(per * (double) eff * 100.0 + 0.000001);
    if (sp > 40.0) sp = 40.0;
    if (sp < 0.0) sp = 0.0;
    return sp / 100.0;
  }
  return per * (double) eff;''')
rep('''  String gt = @PKG@.TreeDefs.gatherType(bt);
  String id = @PKG@.TreeDefs.bid(bt);
  boolean ore = id.startsWith("Ore_");
  boolean rock = ore || "Rocks".equals(gt) || "VolcanicRocks".equals(gt) || (gt != null && gt.startsWith("Ore"));
  double b = 0.0;
  if (rock) b = b + v[@I_MSPEED@];
  if (ore) b = b + v[@I_MHEAVY@];
  if ("Woods".equals(gt)) b = b + v[@I_FSPEED@] + v[@I_FSPEED2@];
  return b;''', '''  String gt = @PKG@.TreeDefs.gatherType(bt);
  String id = @PKG@.TreeDefs.bid(bt);
  boolean ore = id.startsWith("Ore_");
  double b = 0.0;
  if (ore) b = b + v[@I_MHEAVY@];
  if ("Woods".equals(gt)) b = b + v[@I_FSPEED2@];
  return b;''')

# ================================================================ TreeSwing (spec 2.2, 3.6, 4.1, 6 items 4 + 10)
SWING_CLASS = r'''# ================= 0.2.3 TreeSwing: pickaxe / hatchet swing tiers (research/Swing-Speed-Spec.md 2.2 + 3.6) =================
# World thread only (TreeTick, /tree swing). The tier effects are hidden markers read by SkyyTrees' Pickaxe_Attack / Hatchet_Attack root
# overrides (EffectCondition -> TriggerCooldown); this class only puts the right one on the player and takes the others away.
F(swg, "public static final String[] MINE_IDS = %s;" % jstr([""] + [swing_id("Mine", k) for k in range(1, SWING_MAX + 1)]))
F(swg, "public static final String[] CHOP_IDS = %s;" % jstr([""] + [swing_id("Chop", k) for k in range(1, SWING_MAX + 1)]))
F(swg, "public static final double[] CD = %s;" % jdbl(SWING_CD))
F(swg, "public static final int MAXT = %d;" % SWING_MAX)
F(swg, 'public static final String MINE_ROOT = "%s";' % SWING_FAMS[0][1])
F(swg, 'public static final String CHOP_ROOT = "%s";' % SWING_FAMS[1][1])
F(swg, 'public static final String MINE_TREE = "%s";' % swing_tree_id("Mine"))
F(swg, 'public static final String CHOP_TREE = "%s";' % swing_tree_id("Chop"))
F(swg, 'public static final String NOTICE = "[Trees] Mining Speed now makes your pickaxe swing faster (it no longer adds breaking power). Chopping Speed does the same for hatchets. Chopping Speed II is now Heavy Hatchet (breaking power on wood). ";')
F(swg, 'public static final String NOTICE_FREE = "A respec is free if you want to spend your Dust again.";')
F(swg, 'public static final String NOTICE_PAID = "You can respec the tree in /tree if you want to spend your Dust again.";')
F(swg, "public static volatile int[] MINE_IDX;")
F(swg, "public static volatile int[] CHOP_IDX;")
F(swg, "public static volatile int STATE = 0;")
F(swg, "public static volatile long NEXT = 0L;")
F(swg, "public static boolean MISS_TOLD = false;")
# apply() runs on EVERY world thread (TreeTick ticks per world): the logged-once flag is an atomic check-and-set
F(swg, "public static final java.util.concurrent.atomic.AtomicBoolean FAILED_ONCE = new java.util.concurrent.atomic.AtomicBoolean(false);")
# the first interaction id of a root asset ("missing" / "empty" / "unknown" when it cannot be read)
M(swg, r"""
public static String rootOf(String id) {
  try {
    Object o = @RIN@.getAssetMap().getAsset(id);
    if (!(o instanceof @RIN@)) return "missing";
    String[] xs = ((@RIN@) o).getInteractionIds();
    if (xs == null || xs.length == 0) return "empty";
    return xs[0];
  } catch (Throwable t) { return "unknown"; }
}""")
M(swg, r"""
public static String rootText(String root, String want) {
  String r = rootOf(root);
  return r.equals(want) ? "SkyyTrees" : "NOT SkyyTrees (" + r + ")";
}""")
# [0] = -1, [1..40] = asset indexes; null when one id is not loaded
M(swg, r"""
public static int[] resolve(String[] ids) {
  int[] r = new int[ids.length];
  r[0] = -1;
  for (int t = 1; t < ids.length; t++) {
    int x = Integer.MIN_VALUE;
    try { x = @EFX@.getAssetMap().getIndex(ids[t]); } catch (Throwable e) { x = Integer.MIN_VALUE; }
    if (x == Integer.MIN_VALUE || x < 0) return null;
    r[t] = x;
  }
  return r;
}""")
M(swg, r"""
public static synchronized boolean init() {
  if (STATE == 1) return true;
  long now = System.currentTimeMillis();
  if (now < NEXT) return false;
  NEXT = now + 10000L;
  int[] m = resolve(MINE_IDS);
  int[] c = resolve(CHOP_IDS);
  if (m == null || c == null) {
    if (!MISS_TOLD) { MISS_TOLD = true; @PKG@.TreeCfg.warn("swing effects missing - asset pack not loaded? The Mining Speed / Chopping Speed swing bonus stays off (retried every 10 s)"); }
    return false;
  }
  MINE_IDX = m;
  CHOP_IDX = c;
  STATE = 1;
  String pr = rootText(MINE_ROOT, MINE_TREE);
  String hr = rootText(CHOP_ROOT, CHOP_TREE);
  @PKG@.TreeCfg.info("swing speed ready: " + (2 * MAXT) + " effects, pickaxe root = " + pr + ", hatchet root = " + hr + (@PKG@.TreeCfg.SWING_ON ? "" : " (swing.enabled=false - off)"));
  if (!pr.equals("SkyyTrees")) @PKG@.TreeCfg.warn("another mod replaced the pickaxe swing root (Pickaxe_Attack) - Mining Speed swing bonus inactive for pickaxes");
  if (!hr.equals("SkyyTrees")) @PKG@.TreeCfg.warn("another mod replaced the hatchet swing root (Hatchet_Attack) - Chopping Speed swing bonus inactive for hatchets");
  return true;
}""")
M(swg, r"""
public static boolean ready() {
  if (STATE == 1) return true;
  return init();
}""")
# fraction from TreeFx.value (already whole percents, capped) -> tier 0..40
M(swg, r"""
public static int tier(double v) {
  long k = Math.round(v * 100.0);
  if (k < 0L) k = 0L;
  if (k > (long) MAXT) k = (long) MAXT;
  return (int) k;
}""")
# one family: every other tier effect off; tier k (> 0) on for 3 s, refreshed when it has under 1.5 s left (the 1 s tick keeps it alive)
M(swg, r"""
public static void fam(@CB@ cb, @REF@ ref, @ECC@ ecc, int[] idx, int k) {
  if (idx == null) return;
  @I2O@ map = ecc.getActiveEffects();
  if (map == null) return;
  for (int t = 1; t <= MAXT; t++) {
    if (t != k && map.get(idx[t]) != null) ecc.removeEffect(ref, idx[t], cb);
  }
  if (k <= 0) return;
  Object o = map.get(idx[k]);
  if (o instanceof @AEE@ && ((@AEE@) o).getRemainingDuration() >= 1.5f) return;
  @EFX@ fx = (@EFX@) @EFX@.getAssetMap().getAsset(idx[k]);
  if (fx == null) return;
  ecc.addEffect(ref, idx[k], fx, 3.0f, @OVB@.OVERWRITE, cb);
}""")
M(swg, r"""
public static void clear(@CB@ cb, @REF@ ref, @ECC@ ecc) {
  fam(cb, ref, ecc, MINE_IDX, 0);
  fam(cb, ref, ecc, CHOP_IDX, 0);
}""")
# TreeTick, after TreeFx.stats: v = the fresh effect vector of the ACTIVE profile (respec / off / enabled=false / profile switch all show
# up here within 1 s); swing.enabled OFF clears both families
M(swg, r"""
public static void apply(@CB@ cb, @REF@ ref, double[] v) {
  try {
    if (!ready()) return;
    @ECC@ ecc = (@ECC@) cb.getComponent(ref, @ECC@.getComponentType());
    if (ecc == null) return;
    if (!@PKG@.TreeCfg.SWING_ON || v == null) { clear(cb, ref, ecc); return; }
    fam(cb, ref, ecc, MINE_IDX, tier(v[@I_MSPEED@]));
    fam(cb, ref, ecc, CHOP_IDX, tier(v[@I_FSPEED@]));
  } catch (Throwable t) {
    if (FAILED_ONCE.compareAndSet(false, true)) @PKG@.TreeCfg.warn("swing speed effects failed (logged once): " + t);
  }
}""")
# spec 4.1: the one-time notice per profile (first tick with MSpeed, FSpeed or FSpeed2 above 0), then note.swing=1 in that profile file
M(swg, r"""
public static void notice(@PR@ pr, java.util.UUID u) {
  if (@PKG@.TreeStore.busy(u)) return;
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  if (d == null || d.bad || d.noteSwing) return;
  if (d.lv[@I_MSPEED@] <= 0 && d.lv[@I_FSPEED@] <= 0 && d.lv[@I_FSPEED2@] <= 0) return;
  if (!@PKG@.TreeStore.setNote(d)) return;
  @PKG@.TreeStore.dirty(k);
  pr.sendMessage(@MSG@.raw(NOTICE + (@PKG@.TreeCfg.RESPEC_COINS > 0L ? NOTICE_PAID : NOTICE_FREE)).color("#9cd8ff"));
}""")
M(swg, r"""
public static String secs(double s) {
  return String.valueOf(Math.round(s * 10000.0) / 10000.0);
}""")
M(swg, r"""
public static String tierText(int k) {
  if (k <= 0) return "tier 0 (vanilla - a swing every " + secs(CD[0]) + " s)";
  return "tier " + k + " (+" + k + "% - a swing every " + secs(CD[k]) + " s)";
}""")
M(swg, r"""
public static String activeTier(@ECC@ ecc, int[] idx) {
  if (ecc == null || idx == null) return "none";
  @I2O@ map = ecc.getActiveEffects();
  if (map == null) return "none";
  StringBuilder sb = new StringBuilder();
  for (int t = 1; t <= MAXT; t++) {
    Object o = map.get(idx[t]);
    if (!(o instanceof @AEE@)) continue;
    if (sb.length() > 0) sb.append(" + ");
    sb.append("tier ").append(t).append(" (").append(secs((double) ((@AEE@) o).getRemainingDuration())).append(" s left)");
  }
  return sb.length() == 0 ? "none" : sb.toString();
}""")
# /tree swing (world thread): the node tiers, the effects active right now, swing.enabled and whose roots are loaded (re-read every call)
M(swg, r"""
public static String report(@PR@ pr, @ST@ store, @REF@ ref) {
  double[] v = @PKG@.TreeFx.compute(pr.getUuid());
  String s = "[Trees] Swing speed " + (@PKG@.TreeCfg.SWING_ON ? "ON" : "OFF (swing.enabled=false - the nodes do nothing)") + ". Pickaxe (Mining Speed): " + tierText(tier(v[@I_MSPEED@])) + ". Hatchet (Chopping Speed): " + tierText(tier(v[@I_FSPEED@])) + ".";
  if (!ready()) return s + " The swing effects are NOT loaded (asset pack missing?) - see the server log.";
  @ECC@ ecc = null;
  try { ecc = (@ECC@) store.getComponent(ref, @ECC@.getComponentType()); } catch (Throwable t) { ecc = null; }
  return s + " Active now: pickaxe " + activeTier(ecc, MINE_IDX) + ", hatchet " + activeTier(ecc, CHOP_IDX) + ". Roots: pickaxe = " + rootText(MINE_ROOT, MINE_TREE) + ", hatchet = " + rootText(CHOP_ROOT, CHOP_TREE) + ".";
}""")

'''
before('''# ================= TreeTick: once per second per player on the world thread =================
''', SWING_CLASS)
rep('''    @PKG@.TreeFx.stats(cb, ref, v);
''', '''    @PKG@.TreeFx.stats(cb, ref, v);
    @PKG@.TreeSwing.apply(cb, ref, v);
''')
rep('''    @PKG@.TreeMsg.flush(pr);
''', '''    @PKG@.TreeMsg.flush(pr);
    @PKG@.TreeSwing.notice(pr, u);
''')

# ================================================================ swing.enabled OFF: the node says so (review fix; the per-node EN pattern)
# The detail page's "Now:" line of Mining Speed / Chopping Speed follows the existing "turned off on this server" wording while the
# Server Setup switch "Faster tool swings" is OFF (TreeSwing.apply clears the tier effects then); "Level N:" still shows what a level
# gives. tree:fn:bonus answers 0 for those two nodes then, like a node turned off by EN (nothing reads them today).
rep('''  if (!@PKG@.TreeCfg.EN[i]) return "Now: turned off on this server";
''', '''  if (!@PKG@.TreeCfg.EN[i]) return "Now: turned off on this server";
  if (@PKG@.TreeDefs.KIND[i] == @K_SWING@ && !@PKG@.TreeCfg.SWING_ON) return "Now: turned off on this server (Faster tool swings is OFF)";
''')
rep('''    int e = @PKG@.TreeCalc.eff(@PKG@.TreeStore.data((java.util.UUID) a[0]), i);
''', '''    if (@PKG@.TreeDefs.KIND[i] == @K_SWING@ && !@PKG@.TreeCfg.SWING_ON) return Double.valueOf(0.0);
    int e = @PKG@.TreeCalc.eff(@PKG@.TreeStore.data((java.util.UUID) a[0]), i);
''')

# ================================================================ TreeOps.buy: a new owner of a changed node never gets the "no longer" notice
rep('''    @PKG@.TreeStore.setLevel(d, i, 1);
    @PKG@.TreeStore.dirty(k);''', '''    @PKG@.TreeStore.setLevel(d, i, 1);
    if (i == @I_MSPEED@ || i == @I_FSPEED@ || i == @I_FSPEED2@) @PKG@.TreeStore.setNote(d);
    @PKG@.TreeStore.dirty(k);''')

# ================================================================ Server Setup: swing.enabled row + the SWING ask-first check (spec 5)
after('''    ("felled.nodes", "Felled logs roll bonuses", "abilities", "bool", "true", "", "", "", "", "live",
     "Logs of a felled tree roll Sap Tapper, Replanter and Pocket Change (SkyySkills 0.4.2).", "reload"),
''', '''    ("swing.enabled", "Faster tool swings", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: Mining / Chopping Speed shorten the wait between pickaxe / hatchet swings. OFF: they do nothing.", "reload"),
''')
rep('''assert len(_exact) == 17 and len(CFG_ROWS) == 18 + len(TREES)''', '''assert len(_exact) == 18 and len(CFG_ROWS) == 19 + len(TREES)   # 0.2.3: + swing.enabled (config:def 25 rows)''')
after('''M(kitc, r"""
public static boolean fraction(int kd) {
  return kd != @K_HP@ && kd != @K_STA@ && kd != @K_RJMP@ && kd != @K_VEIN@ && kd != @K_FELLER@ && kd != @K_SOON@;
}""")
''', '''# 0.2.3 SWING nodes (Mining Speed / Chopping Speed): per x max above 0.40 = beyond the +40% the assets allow - asked first (spec 5)
M(kitc, r"""
public static String swingAsk(int i, double per, double max) {
  double tot = per * max;
  if (tot <= 0.40 + 0.000001) return null;
  return "?" + @PKG@.TreeDefs.NAME[i] + " would reach +" + @PKG@.TreeDefs.num(tot * 100.0) + "% - swings are capped at +40% (then they are back to back). Save it anyway?";
}""")
''')
rep('''  if (f.equals("max")) return wholeIn(value, 1L, 100L, nm);''', '''  if (f.equals("max")) {
    String rm = wholeIn(value, 1L, 100L, nm);
    if (rm != null || kd != @K_SWING@) return rm;
    return swingAsk(i, @PKG@.TreeCfg.PER[i], (double) Long.parseLong(value.trim()));
  }''')
rep('''    double x = Double.parseDouble(value.trim());
    if (fraction(kd) && x > 1.0) return''', '''    double x = Double.parseDouble(value.trim());
    if (kd == @K_SWING@) return swingAsk(i, x, (double) @PKG@.TreeCfg.MAX[i]);
    if (fraction(kd) && x > 1.0) return''')

# ================================================================ /tree swing (spec 6 item 10; HANDOFF: requirePermission + empty groups)
before('''C(cmd, r"""
public TreesCmd() {''', '''C(scmd, r"""
public TreeSwingCmd() {
  super("swing", "(admin) Your pickaxe and hatchet swing speed tiers and whether the swing roots are SkyyTrees' own");
  requirePermission("skyytrees.admin");
  setPermissionGroups(new String[0]);
}""")
M(scmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyytrees.admin")) { pr.sendMessage(@MSG@.raw("[Trees] no permission (skyytrees.admin)")); return; }
  pr.sendMessage(@MSG@.raw(@PKG@.TreeSwing.report(pr, store, ref)));
}""")
''')
rep('''  addSubCommand(new @PKG@.TreeReloadCmd());
}""")''', '''  addSubCommand(new @PKG@.TreeReloadCmd());
  addSubCommand(new @PKG@.TreeSwingCmd());
}""")''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, fx, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, kitc, vcmd, qcmd, rcmd, cmd, pl)''',
    '''ALL = (defs, cfg, dat, sto, stk, calc, fx, swg, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, kitc, vcmd, qcmd, rcmd, scmd, cmd, pl)''')

# ================================================================ manifest + the asset pack
rep('''levels them. Breaking power, double drops,''', '''levels them. Pickaxe / hatchet swing speed, breaking power, double drops,''')
rep('''m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: the page is built inline''', '''assert m["IncludesAssetPack"] is True   # 0.2.3: the jar carries the swing-speed asset pack (the page is still built inline)
B.assemble(jar, m, OUT, SWING_FILES)''')

# ================================================================ sanity
assert 'VERSION = "0.2.3"' in s and "DERIVED from build_skyytrees_0.2.2.py by tools/trees_0_2_3_patch.py" in s
# one registerSystem per class, still exactly TreeDmgSys + TreeTick (TreeSwing is called from TreeTick, never registered)
assert s.count("registerSystem(") == 2 and "registerSystem(new @PKG@.TreeSwing" not in s
# the admin sub-commands: /tree reload + /tree swing, each requirePermission + empty permission-group list (HANDOFF rule)
assert s.count('setPermissionGroups(new String[] { "hytale:Adventurer" })') == 3 and s.count("setPermissionGroups(new String[0])") == 2
assert s.count('  requirePermission("skyytrees.admin");') == 2
# the old speed nodes are gone from breaking power; the swing hook runs from the tick only
_db = s[s.index("public static double dmgBonus(double[] v, @BTY@ bt) {"):s.index("# take one player's UUID-keyed bridge entries back")]
assert "I_MSPEED" not in _db and "I_FSPEED@" not in _db and "I_MHEAVY" in _db and "I_FSPEED2" in _db
assert s.count("@PKG@.TreeSwing.apply(cb, ref, v);") == 1 and s.count("@PKG@.TreeSwing.notice(pr, u);") == 1
# TreeSwing is compiled before TreeTick (methods before callers), TreeSwingCmd before TreesCmd
assert s.index("F(swg, ") < s.index("# ================= TreeTick: once per second") < s.index('M(tick, r"""\npublic void tick(')
assert s.index("public TreeSwingCmd()") < s.index("public TreesCmd()")
# the loader reads every row key (+ swing.enabled); migration reads and appends in one write
_ap = s[s.index("public static void apply(java.util.Properties p) {"):s.index("public static void writeAtomic(byte[] data)")]
_read = set(re.findall(r'(?:lng|str|dbl|bool)\(p, "([A-Za-z.]+)"', _ap))
assert "swing.enabled" in _read and len(_read) == 19, _read
assert s.index("public static String migrateSwing(") < s.index("public static java.util.Properties upgrade(")
assert s.count('if (need023) sb.append("\\n").append(ADD023);') == 1 and s.count("text = migrateSwing(text, n2);") == 1
assert s.count("B.assemble(jar, m, OUT, SWING_FILES)") == 1 and 'IncludesAssetPack"] = False' not in s
assert "--deploy" in s   # the script keeps its optional deploy switch; workflows never pass it
# review fixes: the swing-length walk follows a Selector's hit chains; the logged-once flag is atomic; swing.enabled OFF shows on the node
assert s.count('tail.append(_root(x.get("HitEntity"), depth + 1))') == 1 and s.count("FAILED_ONCE.compareAndSet(false, true)") == 1
assert 'F(swg, "public static boolean FAILED_ONCE' not in s and s.count('return "Now: turned off on this server (Faster tool swings is OFF)";') == 1
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
