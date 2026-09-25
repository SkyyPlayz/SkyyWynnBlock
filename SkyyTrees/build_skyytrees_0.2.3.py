"""SkyyTrees 0.2.3 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
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
    - Mining S1 MSpeed "Mining Speed": SWING, max 25, per 0.016 = +1.6 % pickaxe swing speed per level, +40 % at max (a swing every
      0.25 s instead of 0.35 s). LOCKED Skyy 2026-09-25 (was per 0.01, +25 %). A file already on Mining.MSpeed.per=0.01 keeps +25 %
      until that line is set to 0.016. If +40 % is still too slow, vanilla swing timing may need adjusting. NOW "+%V pickaxe swing speed".
    - Mining S10 MHeavy "Heavy Pick": DMG (+2 % breaking power per level, +40 %). LOCKED Skyy 2026-09-25: rock and ore (was ore only).
    - Foraging S1 FSpeed "Chopping Speed": SWING like Mining Speed, for hatchets.
    - Foraging S10 FSpeed2 renamed "Heavy Hatchet" (was Chopping Speed II): unchanged DMG on wood (+40 %). Id and saved key stay FSpeed2.
    - TreeFx.dmgBonus: rock no longer gets MSpeed, wood no longer gets FSpeed. LOCKED Skyy 2026-09-25: rock and ore -> + MHeavy, Woods -> + FSpeed2.
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
0.2.2 = in-game server setup + player Settings (Skyy 2026-09-24: "everything a server owner might change must be doable in game, config
  files stay and always match"). DEFAULT BEHAVIOUR IS IDENTICAL TO 0.2.1 until an admin changes something: no file key, default,
  loader, clamp, node or message text changed; trees.properties is not written at start (only a first start writes the default file,
  as before, now with one more comment line saying it is editable in game).
  ADMIN CONFIG (research/Server-Setup-Spec.md 4.10 + 7, tools/CONFIG-CONTRACT.md, the kit tools/skyycfg.py):
    - SkyWynn Menu -> Server Setup -> "Trees" (SkyyMenu 0.3, /modconfig): config:def:SkyyTrees + config:fn:SkyyTrees (+ config:epoch)
      are put on the skyy.bridge as the LAST step of setup(), after TreeCfg.load (CfgPub.start); CfgPub.shutdown() in shutdown writes any
      pending change. Admin node skyytrees.admin (the same node /tree reload needs; ops have it through hytale:Admin's "*").
    - File Skyy_SkyyTrees/trees.properties (names and keys unchanged; the kit rewrites only the changed line, comments and order kept,
      every change logged in Skyy_SkyyTrees/config-changes.log, the file's last 20 versions in Skyy_SkyyTrees/config-history/).
    - EVERY key TreeCfg.load reads is bound to a row (build-asserted), so every hand edit is noticed by the kit (logged via=file) and
      applied. All rows bind reload: the kit writes the line, then runs TreeKit.reload = TreeCfg.load (the same loader /tree reload
      runs: parse + clamp, no world access) + TreeAbil.ITEMOK.clear on the scheduler thread; the change applies within about a second.
      No restart rows (every value is read live from the TreeCfg volatile fields).
    - Rows (key, type, flags; L = live, D = danger (asks first), A = advanced):
        general:   tier.levels text L,D (check: 6 whole numbers 0-1000, each >= the one before = the loader's rule) - tokens.first int
                   0-100 L,D - tokens.every int 1-100 L,D - dust.xpPerDust int 1-1e9 L,D - dust.perTree table (file lines
                   dust.xpPerDust.<Tree>, column XP per Dust 1-1e9, add by typing; check: a tree name, capitals matter) L,D -
                   respec.cooldownMinutes int min 0-100000 L - respec.coins int coins 0-1e12 L - feedbackMs int ms 500-600000 L,A -
                   debug.extraTokens int 0-1000 L,D,A - debug.extraDust int 0-1e15 L,D,A
        abilities: ability.disabledWorlds text L - ability.maxRadius int blocks 1-16 L - vein.cooldownSec int s 0-86400 L -
                   feller.cooldownSec int s 0-86400 L - feller.maxPerLayer int 1-256 L - feller.needLeaves bool L - feller.maxHeight
                   int blocks 1-64 L - felled.nodes bool L
        nodes:     nodes.Mining / nodes.Foraging / nodes.Farming / nodes.Cooking / nodes.Acrobatics / nodes.Exploration = one table per
                   tree (file lines <Tree>.<Id>.<field>, one text column "Value", add by typing) L,D
      Ranges = the loader's clamps (typed values are refused, never clamped).
    - SPEC DEVIATIONS (deliberate): (1) spec 4.10's node tables with columns Max|Per level|On plus a nodeCost table Tokens|Dust B are
      built as one key-family table per tree whose entries ARE the file lines (MSpeed.max, MSpeed.per, MSpeed.B, MSpeed.tokens,
      MSpeed.enabled, MVein.base, MGems.items, AGrain.crops ...). trees.properties keeps one line per node field, and a kit table entry
      with 3 columns spread over 3 file lines would have to be a custom: table, which the kit cannot log hand edits for, cannot restore
      from History and whose hand edits the menu's Reload does not apply (CONFIG-CONTRACT "Known limits"). This way every node field -
      also base and the item / crop lists the spec's columns left out - is editable, logged, undoable and restorable. (2) The spec's
      "table dust.xpPerDust" is row dust.perTree (row keys must be unique; the file prefix stays dust.xpPerDust.). (3) dust.xpPerDust,
      dust.perTree and the six nodes.<Tree> tables carry danger (the spec gave no flag): like a Collections curve they move every
      player at once - the Dust rate every Dust balance, a node's tokens / B what every owner has spent (TreeCalc.tokSpent / dustSpent
      recompute it from the current costs, so a raise can make balances negative), its max / per / enabled every owner's effect. A
      danger table asks for every set / add / remove ("Change MSpeed.max in Mining nodes from 25 to 30?"); a check's own "?" question
      replaces that text (one confirm, never two).
    - Node table checks (TreeKit.checkNode, the loader's parse + clamp ranges): max whole 1-100, per number 0-1000 (asks first when a
      percent node gets more than 1 = 100% per level), B whole 0-1e9, tokens whole 0-100, enabled true / false, base number 0-1000
      (Vein Burst, Tree Feller, Double Jump), items = existing item ids, crops = names with a Plant_Crop_<C>_Block block; plain digits /
      a dot decimal, because the loader reads them with Long.parseLong / Double.parseDouble (a typed "2k" or "on" would load as the
      default while the page said it was saved). An unknown node or field, a wrong capital or a Coming-later slot ASKS ("this line would
      do nothing - save it anyway?") instead of refusing, so an export / import / restore carrying old lines (the Acrobatics.RDodge.*
      lines 0.2.1 left in place) never fails. Removing an entry is always allowed: the built-in default applies again.
    - /tree reload (unchanged command: node skyytrees.admin, empty permission-group list): the same re-read as 0.2.1 (item-id
      cache, unreadable player files, TreeCfg.load with its summary) and then the kit's reload op (via=command), which logs every value
      changed by hand in config-changes.log; the reply adds the kit's line ("Read the files again: 1 value changed by hand ...").
    - Header note: node ids and names are the comments in trees.properties; hand edits: /tree reload or Reload file.
  PLAYER SETTINGS (research/Settings-Spec.md 1.3 + 3.2; SkyyMenu 0.2+ /settings, tab Cooking & Trees):
    - setup() registers trees.bonus "Tree bonus totals" and trees.abilities "Vein Burst and Tree Feller" (category cooking, default ON)
      with TreeStore.regSetting (settings:def:<key> + settings:fn:register; the creating bridge()).
    - Gates (only the sendMessage call, never the work): TreeMsg.flush (the aggregated "Tree bonus: ..." line; take() still clears the
      pending totals first, so a hidden line is dropped, not queued), TreeAbil.vein ("Vein Burst! ...") and TreeAbil.feller ("Tree
      Feller! ..."): the break, the cooldown and every drop happen either way.
    - TreeStore.notifyOn = the spec helper: settings:fn:get when SkyyMenu is there (before it, the one-shot moveQuiet: a profile with
      the old /tree quiet=true sets trees.bonus OFF with onlyIfUnset and, on TRUE, clears quiet in that profile file); without SkyyMenu
      trees.bonus = !quiet and trees.abilities = on, exactly 0.2.1. Player files are still only read on world threads (flush, vein,
      feller and /tree quiet all run there).
    - /tree quiet: with settings:fn:set it flips trees.bonus and answers "[Trees] Tree bonus messages hidden/shown. More switches:
      /settings"; without SkyyMenu the 0.2.1 per-profile toggle runs unchanged. Its help text no longer says ability messages always show.
  CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch/r4-trees, deleted afterwards; 140 checks, 0 fails): all
    31 classes load under -Xverify:all; a fresh start writes the default file, every loaded value equals 0.2.1's defaults and
    CfgPub.start leaves trees.properties byte for byte; config:def header (24 rows, 3 categories); every row reads back its default;
    export changed -> import preview = nothing to change; danger rows ask first and a confirm changes nothing; scalar sets write only
    their line (comments kept) and TreeKit.reload applies them (tokens.every, feller.cooldownSec 10s -> 10000 ms, needLeaves off,
    disabledWorlds list, respec 2min, feedbackMs); range refusals; tier.levels check (5 bad forms refused, equal tiers allowed);
    node tables (62 Mining entries, filter, max / per / enabled / base / items checks, remove -> built-in default and the line gone,
    add back, the ask-first cases: unknown node, wrong capitals, unknown field, base on a non-base node, Coming-later slot, per 2 on a
    percent node); dust.perTree (asks first, own Mining rate, remove Acrobatics -> 2); a hand edit is found by the reload op, logged
    via=file and applied; table changes logged as nodes.Mining[MSpeed.max]; file history + restore preview; export all / changed ->
    import preview = nothing to change; restore / import APPLY refused without an admin UUID (contract); an old 0.2-era file is
    upgraded by the 0.2.1 migration first and its stale Acrobatics.RDodge.* lines are listed, ask first on change, never block an
    export -> import and can be removed; settings: without SkyyMenu trees.bonus = !quiet and trees.abilities = on, settings:def
    written, the quiet move calls settings:fn:set {uuid, trees.bonus, FALSE, TRUE} once and clears quiet + saves, then both
    switches are read from the registry. NOT covered there: the real PermissionsModule / Item asset map / scheduler (in-game steps).
    Review fix (2026-09-25, a second scratch harness, 67 checks, 0 fails): the six node tables are published with danger (13 danger
    rows); a node set / add / remove answers confirm ("Change MSpeed.max in Mining nodes from 25 to 30? ...") and changes nothing, yes
    applies it (TreeCfg.MAX, file line, log nodes.Mining[MSpeed.max]); out-of-range / "off" are refused before any confirm; an unknown
    id asks only its own "would do nothing" question; feller.cooldownSec still saves without one; export all -> import preview =
    nothing to change; the /tree reload order (hand edit, direct TreeCfg.load, kit reload op) logs "1 value changed by hand" and the
    queued second load leaves the same values.
  UNVERIFIED (needs Skyy's in-game test): the Trees page in SkyyMenu 0.3 Server Setup (rows, the node tables' paging / filter / add),
    the settings switches in /settings, the quiet move with a real SkyyMenu, and the kit's scheduler save path in a running server.

=== SkyyTrees 0.2.1 notes (history; still true unless 0.2.2 above says otherwise) ===
0.2.1 = HANDOFF feedback round 2, the SkyyTrees parts of research/Tree-Fall-Spec.md (3.3) and research/Double-Jump-Spec.md (3.1).
  TREE FELLER REWORK (Skyy 2026-09-24: "Hytale already fells a tree when its whole base is broken, so Tree Feller breaks extra logs
    HORIZONTALLY on the broken block's Y level ... No vertical reach"):
    - TreeAbil.flatFlood: breadth-first search on the cut's Y level only, over the 8 horizontal neighbours in the order (1,0) (-1,0)
      (0,1) (0,-1) then the 4 diagonals, so the logs nearest the cut go first (level 1 = the log right beside it); |dx|, |dz| <=
      ability.maxRadius; ids starting with the cut's Wood_<W>_Trunk family (Trunk and Trunk_Full); never a placed log (skill:fn:placed)
      or one an ability broke in the last 5 s; at most 4000 reads. NOTHING above or below the cut level is ever broken.
    - Level curve (Foraging.FFeller: per 1.0, base 0.0, max 5): levels 1, 2, 3, 4 = 1, 2, 3, 4 more logs; the MAX level = every log of
      that tree on that level, up to feller.maxPerLayer (default 64, clamp 1-256) = TreeCfg.FELLER_ALL (TreeFx.value returns it at
      max, so tree:fn:bonus answers it too). A 2x2 tree needs level 3, a 3x3 needs the max level. The page says "Breaks 1 more log
      beside it on the same level" ... "Breaks every log of that tree on the same level (up to 64)".
    - Natural-tree check unchanged in spirit: with feller.needLeaves the old 26-neighbour flood runs READ-ONLY (max 0) from the cut
      up to feller.maxHeight up / down and only reports whether a Plant_Leaves_ block touches that wood (a partial cut of a thick tree
      fells nothing, so the tree is still whole). An empty layer or no leaves = no break and no cooldown (Timber Spread may still roll).
    - Every Feller log still breaks through BlockHarvestUtils.performBlockBreak = a real BreakBlockEvent each (island protection,
      SkyySkills XP + double drops, Collections). Once the whole layer is gone the engine fells the tree; SkyySkills 0.4.2 pays those
      logs as felled (its LAYER list reuses the first watch), so no log is ever both Feller-broken and felled.
    - feller.cooldownSec default 5 (was 30); chat "Tree Feller! +3 logs on this level (ready again in 5 s)".
    - trees.properties migration, ONCE (a file without feller.maxPerLayer): the unchanged old default lines Foraging.FFeller.per=8.0,
      Foraging.FFeller.base=8.0 and feller.cooldownSec=30 are rewritten in place to 1.0 / 0.0 / 5 (exact key and value text, comments
      untouched, bytes read and written as ISO-8859-1 = the java.util.Properties file encoding, so nothing else in the file changes);
      then the 0.2.1 block (feller.maxPerLayer=64, felled.nodes=true, comments) is appended. Custom per / base values are KEPT and the
      server log warns that they now count logs on one level. The whole new content is written through TreeCfg.writeAtomic and the
      in-memory settings are parsed from exactly that content (a failed write still runs with the migrated values; the next load
      retries). A 0.1 file gets the 0.2 block (now with Double Jump) + the migration in the same single write.
  FELLED-LOG NODE ROLLS (Tree-Fall-Spec 3.3): TreeFelledFn is registered as "trees" in the bridge map skill:on:felled (putIfAbsent,
    re-checked every 5 s like skill:on:gather, removed in shutdown). SkyySkills 0.4.2 calls it on the world thread once per credited
    felled position: Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey}. On a
    Foraging (row 1) _Trunk it rolls Sap Tapper, Replanter and Pocket Change exactly like TreeGather.run; NEVER Spread / Vein /
    Feller (no chains). Skipped while profile:busy:<uuid> is set, when pkey is not the player's active profile any more, or with
    felled.nodes=false. Without SkyySkills 0.4.2 the map is simply never called.
  DOUBLE JUMP (Double-Jump-Spec 3.1, Skyy 2026-09-24 "add a double jump node to the acrobatics tree"):
    - KINDS += DJUMP (22; every older kind number unchanged). Acrobatics S5 (tier II, Acrobatics 10) is now RDouble "Double Jump"
      (icon Plant_Fruit_Windwillow, max 10, base 0.5, per 0.05): value = base + per x level = 55% at level 1 .. 100% at level 10 of
      the player's own jump height. It replaces Quick Dodge (RDodge): same slot, so the same unlock token and the same Dust per level.
    - skill:bonus:<uuid>["trees"]: "doublejump.acrobatics" = that fraction (absent = no node / off); "dodge.acrobatics" = Evasion
      (RDodge2) only. SkyySkills 0.4.2 reads doublejump.acrobatics (crouch in mid-air, Stamina, landing reset - all SkyySkills side).
    - Card HOW "Press %K in mid-air ...": %K = bridge skill:dj:key (SkyySkills 0.4.2: "crouch" / "jump" / "jump or crouch"), else
      "crouch". Evasion's NOW text is "+%V dodge push" (Quick Dodge no longer exists).
    - OLD SAVES (0.2 is live, so Acrobatics.RDodge lines exist): TreeStore.readFile loads Acrobatics.RDodge=<n> as RDouble level n
      when the file has no Acrobatics.RDouble line (an RDouble line always wins), and "RDodge" in Acrobatics.off turns RDouble off.
      Tokens and Dust are computed from levels (never stored), so the balance is exactly what 0.2 showed. snap() writes current ids,
      so the next save has Acrobatics.RDouble=<n> and no RDodge line; an untouched file is aliased again on every load (harmless).
      Acrobatics.RDodge2 (Evasion) is a different id and is never aliased.
    - trees.properties: a file 0.2 wrote (0.2 keys, no Acrobatics.RDouble.* key) gets the RDouble node lines appended once, with a
      comment that the old Acrobatics.RDodge.* lines are unused (an admin's Quick Dodge numbers do NOT carry over; logged once).
  CHECKED at build time in a bare JVM (the session's scratch harness under tools/dev/scratch, deleted afterwards; see the build
    report): the trees.properties upgrade of a real 0.1 and a real 0.2 default file (read from those jars) and of a customised file,
    idempotence on a second load, the RDodge -> RDouble save alias (spec 3.1 point 6 cases a-d incl. the same Tokens / Dust as 0.2),
    the Feller values 1/2/3/4/64, Double Jump 0.55 / 1.0 and the bonus map.
  UNVERIFIED (needs Skyy's in-game test): flatFlood / the same-Y breaks in a real world (Tree-Fall-Spec T7), the felled rolls
    (needs SkyySkills 0.4.2, T3), the Double Jump itself (SkyySkills 0.4.2, Double-Jump-Spec section 5).
  REVIEW FIXES (same version, before any deploy):
    - Log family = the natural shapes only: TreeDefs.isLog(id, fam) = Wood_<W>_Trunk or Wood_<W>_Trunk_Full, plus their block
      states (a Stripped trunk "*Wood_Oak_Trunk_State_Stripped"). Trunk_Half, Trunk_Stairs and the *_Deco shapes never match any more
      (0.1 / 0.2 matched every id starting with Wood_<W>_Trunk). Assets.zip, checked 2026-09-24: none of the 1126 tree prefabs
      (Server/Prefabs/Trees) uses a Half / Stairs / Deco trunk, only Trunk + Trunk_Full, so natural trees lose nothing. Used by
      flatFlood, the read-only leaves check (TreeAbil.matches, prefix mode) and the cut itself (a Half / Stairs cut never fires Feller).
    - TreeGather.felled: never rolls on a position a SkyyTrees ability broke in the last 5 s (TreeAbil.recent; run() already rolled
      for it through its real BreakBlockEvent), whatever SkyySkills reports. Off the world thread (Store.isInThread false) it does
      nothing and warns once (SkyySkills 0.4.2 documents FellCredit.one on the world thread; the guard keeps inventory writes safe).
    - TreeDefs.valueText: explicit DJUMP case (percent), no behaviour change.
    - Detail panel: SkyyTrDetHow 52 -> 72 px high (the Tree Feller and Double Jump HOW texts are ~130 characters, the longest in 0.2
      was 100; 72 px holds 4 lines at FontSize 11 in the 310 px column). The panel column still has ~98 px spare below the buttons.
  SKYY SIGN-OFF NEEDED BEFORE DEPLOY (open in HANDOFF section 4 and the specs' section 6; this build uses the specs' recommendations):
    - Double-Jump-Spec 6.1: tier II slot 5 (built: replaces Quick Dodge) or tier III slot 7 (would replace Sprinter). The save alias is
      lossless - RDouble level n = the old RDodge level n in the SAME slot, so the same Token / Dust - and a tier-III rebuild can alias
      RDouble back to RDodge the same way. 6.2 / 6.3 (boots, numbers) are SkyySkills / trees.properties values.
    - Tree-Fall-Spec 6.3: Tree Feller curve 1 / 2 / 3 / 4 / whole layer and the 5 s cooldown. Plain trees.properties values
      (Foraging.FFeller.per / base, feller.cooldownSec, feller.maxPerLayer): retuning needs no new migration.

=== SkyyTrees 0.2 notes (history; still true unless 0.2.1 above says otherwise) ===
0.2 = research/Exploration-Build-Spec.md section 4, from Skyy's Exploration call 2026-09-24 (SkyyExploration-Plan.md 'trees' row):
  TWO NEW TREES on the same 12-slot template: Acrobatics (tree 4, #c8a0ff) and Exploration (tree 5, #e0a040); NT = 6, N = 72.
    Tree indices 0-3 and every 0.1 node id, kind number, default and saved key are unchanged, so 0.1 player files load as they are
    (players/<pkey>.properties: <Tree>.<Id>=level, <Tree>.off, <Tree>.respecAt; the two new trees simply start empty).
  ACROBATICS (12 nodes, verified hooks only): Fleet Foot / Sprinter / Windrunner = flat speed, Spring Step / High Jumper = flat jump
    (blocks), Soft Landing / Featherfall = flat fallDamage (negative), all posted as the movement protocol source "trees.acrobatics"
    (tools/skyymove.py; SkyySkills 0.2+ / SkyyAccessories 0.3+ apply it, the stat:owner:fallDamage owner sums fallDamage; TreeFx.acroPost
    every second, all zeros removes the entry, never another source). Second Wind / Marathon / Endurance = skyytree_stamina (+8 max
    Stamina at max). Quick Dodge / Evasion = skill:bonus:<uuid>["trees"] "dodge.acrobatics" (SkyySkills 0.4.1 reads it and caps it with
    acro.treeDodgeMax). At max: +20% speed, +0.7 blocks jump, -15% fall damage, +20% dodge push, +8 max Stamina.
  EXPLORATION (SMALL FIRST DRAFT - Skyy designs the rest later): Wanderer's Heart + Hearty Wanderer = skyytree_health (+20 max Health
    at max); Treasure Sense (LUCK) and Scavenger (SCAV) are numbers SkyyExploration reads through tree:fn:bonus ("Exploration.ELuck" /
    "Exploration.EScav", level x per); S5-S12 are "Coming later" placeholders (kind SOON): TreeCfg.EN baked false (no trees.properties
    line can turn one on), no trees.properties lines, TreeCalc.state / pathOk / tokSpent / dustSpent and the tree:<uuid> owned count skip
    them, the page shows "Coming later" (card #1a1a24 / #8890a0, no Turn off button), TreeOps.buy / toggle refuse them first, the load
    summary counts them apart ("N of 64 nodes on (8 coming later)"). Nothing in this tree boosts Exploration XP (Skyy Q3: no boosters).
  PER-TREE DUST RATE: dust.xpPerDust.<Tree> overrides dust.xpPerDust (defaults Acrobatics 2, Exploration 5; the other trees follow the
    global 10). Acrobatics XP is capped per minute and Exploration XP is one-time, so at 10 XP per Dust neither tree could be levelled.
    TreeCalc.dustEarned(tree, xp); the page note, the Dust need line and the load summary show each tree's own rate.
  BRIDGE: new tree:names = "Mining,Foraging,Farming,Cooking,Acrobatics,Exploration" (put in setup, removed in shutdown) - SkyySkills
    0.4.1 and SkyyExploration show their Tree buttons from it. clearOne also takes back move:<uuid>["trees.acrobatics"].
  CONFIG: an existing trees.properties (written by 0.1) gets the 0.2 block (per-tree Dust rates + the Acrobatics / Exploration node
    lines) added ONCE, when it has no dust.xpPerDust.* / Acrobatics.* / Exploration.* key; it holds the same numbers as the
    built-in defaults, so the trees work the same whether or not the write succeeds. The old content + the block go to
    trees.properties.tmp and then replace the file with an atomic move (TreeCfg.writeAtomic, the TreeStore.moveRetry pattern) - a
    crash leaves either the old file or the full new one, never a torn line. The default file of a first start is written the same way.
  PAGE: 6 tabs of 88 px with 4 px gaps, level / tokens / Dust labels 150 / 140 / 128 (970 of the 972 px inner width; sized from the
    client font's own glyph advances, NunitoSans: "Exploration" at 12 bold ~66 px, "SkyySkills missing" at 14 ~123, "Tokens 121 of 121"
    at 13 ~115 - a debug.extraTokens test - and "Dust 123,456,789" ~110). The Exploration
    tab's note: "Draft tree - Skyy designs the rest later - nothing here boosts Exploration XP", prefixed with "Exploration levels need
    SkyySkills 0.4.1" when the running SkyySkills publishes no Exploration level in skill:<uuid> (SkyySkills 0.4).
  COMMANDS: /tree acrobatics | exploration (3+ letter prefixes acr / exp work), help texts updated, same permission groups.
UNVERIFIED in 0.2 (needs Skyy's in-game test, spec 4.4): the SkyySkills / SkyyAccessories appliers picking up the new
  "trees.acrobatics" source (built against tools/skyymove.py), dodge.acrobatics (needs SkyySkills 0.4.1), and the Exploration numbers
  (need SkyyExploration 0.1 + SkyySkills 0.4.1).

=== SkyyTrees 0.1 notes (history; still true unless 0.2 above says otherwise) ===
SkyyTrees 0.1 - NEW mod.
Spec: research/Skill-Trees-Spec.md (Mining, Foraging, Farming trees) + research/Cooking-Skill-Spec.md section 7 (the Cooking tree,
orchestrator DECISION 3: "Cooking gets its own skill tree, the 4th tree in SkyyTrees").

Run:   python build_skyytrees_0.2.3.py            -> SkyyTrees/SkyyTrees-0.2.3.jar
       python build_skyytrees_0.2.3.py --deploy   -> also Mods/SkyyTrees.jar + enabled in the HUD mod world (only with Skyy's OK)

WHAT IT IS
  Four HOTM-style trees on ONE 12-slot template (spec sections 3-5): Mining, Foraging, Farming, Cooking ("Kitchen").
  - Tiers I..VI open at skill level 1/10/20/30/45/60 (trees.properties tier.levels). Path rule: a node in tier k >= 2 needs at least
    one owned node in tier k-1.
  - TOKENS unlock nodes: level >= 1 -> tokens.first + floor(level / tokens.every) (1 at 1, 21 at 100). Costs: S1-S9 1, S10-S11 2,
    S12 3 (16 for a whole tree).
  - DUST levels nodes: floor(total skill XP / dust.xpPerDust) (1 per 10 XP), never stored. Level n -> n+1 costs B x n^3 Dust
    (B per slot: 5 5 5 150 150 100 500 1000 1000 200 4000 150000). Only node levels, off flags, the respec time and quiet are saved,
    so a respec is exact and nothing can be duped or lost.
  - Levels come from SkyySkills' skill:fn:level (Object[]{UUID, "Mining"} -> Integer, per profile). XP for Dust comes from
    skill:fn:xp (SkyySkills 0.4, trees bridge). Without skill:fn:xp (SkyySkills 0.3.x) Dust is ESTIMATED from the level (the XP a
    player had at the start of the level, default 100-level table) and the page says so.
  - Respec: one tree at a time, free, full refund, click twice within 10 s, respec.cooldownMinutes (10) per tree, optional
    respec.coins (coins:fn:take). A negative balance (Skyy retuned costs) blocks buying, keeps effects, and allows a respec at once
    (no cooldown, no coins).
  - Every owned node can be turned off without losing its level (tree:fn:level then answers 0 for it).

THE NODES AND THEIR HOOKS (spec 6.4; every hook is VERIFIED there - nodes whose hook the spec marks 'later' are NOT built)
  DMG    TreeDmgSys = EntityEventSystem on DamageBlockEvent (query Archetype.empty(), player entities only):
         setDamage(getDamage() x (1 + bonus)); Mining Speed/Heavy Pick on ROCK (gather type Rocks, VolcanicRocks, Ore*, or an Ore_ id) /
         ORE (id starts Ore_), Chopping Speed I+II on WOOD (gather type Woods). BlockHarvestUtils.damageSingleBlock re-reads getDamage()
         after invoking the event (spec, bytecode).
  DD/XP  posted into skill:bonus:<uuid> (ConcurrentHashMap source -> immutable Map), source "trees": xp.mining, xp.foraging,
         xp.farming, xp.cooking, dd.mining, dd.foraging, dd.farming = FRACTIONS (0.15 = +15 %). SkyySkills 0.4 multiplies XP by
         (1 + sum xp.<skill>) and adds dd.<skill> to its double-drop chance (trees spec 9.3; Cooking's xp.cooking needs the 0.4 reader
         to cover slot 12, Cooking spec 7.2 S3).
  STAT   EntityStatMap StaticModifier(MAX, ADDITIVE) keys skyytree_health (Forest Vigor + Hearty Harvest + Well Fed) and
         skyytree_stamina (Miner Stamina), once per second by TreeTick (SkyySkills Perks.mod pattern). The modifiers are saved with
         the player (turn nodes off / respec before uninstalling, like SkyySkills' skyyskill_* keys).
  MOVE   movement protocol v1 (tools/skyymove.py): source "trees.tools", layer flat, speed = Tunnel Runner (Tool_Pickaxe_ in hand) /
         Woodland Stride (Tool_Hatchet_) / Field Runner (Tool_Hoe_ or Tool_Sickle_). SkyyTrees only POSTS; SkyySkills 0.2+ /
         SkyyAccessories 0.3+ apply it.
  ITEM / EXTRA / COINS / BREAK  run in TreeGather = the Function SkyyTrees registers as "trees" in the SkyySkills 0.4 map
         skill:on:gather (called on the world thread right after a gathering block PAID XP: Object[]{PlayerRef, Integer row,
         BlockType, String world, Boolean harvest, Integer x, Integer y, Integer z}). Player-placed blocks never pay, so they never
         roll. Nothing rolls while profile:busy:<uuid> is set (crash recovery at join - PROFILES-CONTRACT 4.5).
         ITEM  new ItemStack(id, 1) -> storage first (Inventory.getCombinedStorageHotbarBackpack + addOrDropItemStack): Gem Finder
               (random of Rock_Gem_Diamond/Emerald/Ruby/Sapphire/Topaz), Prospector (Ore_<Metal>_<Rock> -> Ingredient_Bar_<Metal>),
               Sap Tapper (Ingredient_Tree_Sap), Replanter (Wood_<W>_Trunk -> Plant_Sapling_<W>, not Burnt/Fir), Seed Saver
               (Plant_Crop_<C>... -> Plant_Seeds_<C>, no seeds for berries/wild grass), Essence Gatherer (Ingredient_Life_Essence).
               Every id is checked in Assets.zip at build time and against the live Item asset map before it is given.
         EXTRA skill:fn:drops (Object[]{BlockType, Boolean harvest} -> List, a FRESH roll of the block's own drops): Rich Veins,
               Grain / Root / Garden Mastery, Herbalist (once more), Cornucopia (two more times).
         COINS coins:fn:add (Object[]{UUID, Long}) = your skill level: Pocket Change (Mining, Foraging).
         BREAK BlockHarvestUtils.performBlockBreak(Ref player, ItemStack held, List<Vector3i>, 4096, entityStore, chunkStore) - the
               engine's own BreakBlockInteraction call: every extra block fires a REAL BreakBlockEvent on the player (SkyyIslands
               protection, SkyySkills XP + double drops, Collections all apply) then drops normally. Mining/Timber Spread (1 touching
               block/log of the same id), Vein Burst (paid Ore_ block: up to 4 + 2 x level touching blocks of the same id, 40 s
               cooldown), Tree Feller (paid log: up to 8 + 8 x level connected logs of the same Wood_<W>_Trunk family, only when the
               group touches a Plant_Leaves_ block, 30 s cooldown). 26-neighbourhood, horizontal radius ability.maxRadius (6), vertical
               6 for ore / feller.maxHeight (32) for trees, placed positions skipped via skill:fn:placed (no placed Function = no
               BREAK at all), positions broken by an ability are remembered 5 s and never trigger another ability (no chains), one
               extra-break action per player at a time, never in ability.disabledWorlds, needs an item in hand.
  COOK   the Cooking tree's effects run in SkyyCooking (it reads them): tree:fn:level (Object[]{UUID, "Cooking.CGourmet"} ->
         Integer, 0 when off / disabled - the Cooking spec's interface), tree:fn:bonus (same argument -> Double = level x per from
         trees.properties, Master Chef = (level - 1) x per). Those two Functions are the whole Cooking interface: SkyyCooking 0.1
         reads exactly them (review fix: the unrequested, unread per-player summary map tree:cook:<uuid> is no longer published).
         Cooking Wisdom = xp.cooking (SkyySkills), Well Fed = skyytree_health. Default per-level numbers are exactly
         Cooking-Skill-Spec 7.2 so a reader that only uses tree:fn:level and the spec's table agrees with SkyyTrees.

BRIDGE (System.getProperties().get("skyy.bridge"))
  reads  skill:fn:level, skill:fn:xp, skill:fn:drops, skill:fn:placed (SkyySkills), coins:fn:add, coins:fn:take (SkyyCoins),
         profile:fn:key, profile:epoch:<uuid>, profile:busy:<uuid> (SkyyProfiles)
  writes tree:fn:level, tree:fn:bonus (setup; removed in shutdown), skill:on:gather["trees"] (created with putIfAbsent, re-checked
         every 5 s so a map another mod replaced gets our listener again), skill:bonus:<uuid>["trees"], move:<uuid>["trees.tools"],
         tree:<uuid> = "Mining:5/7,Foraging:0/3,Farming:2/4,Cooking:0/1" (nodes owned / tokens earned).
  UUID-keyed values describe the ACTIVE profile and are recomputed every second by TreeTick, so an epoch change republishes them
  within 1 s (contract rules 3-4). The first epoch seen is a baseline.
  CLEANUP (review fix): TreeFx.FX doubles as the set of players we published for. TreeSaver.retainOnline (every 30 s) takes a player
  who is no longer in Universe.getPlayer (= disconnected; world transfers keep the PlayerRef) out of FX and THEN removes their
  skill:bonus:<uuid>["trees"], move:<uuid>["trees.tools"] and tree:<uuid> (TreeFx.clearOne); shutdown's clearAll does the same for
  whoever is still in FX. Every bridge write is followed by an FX put (TreeTick, TreeFx.refresh), so a tick racing a disconnect
  re-marks the player and the next pass clears it: no stale tree bonus or tool speed survives a logoff or an unload. The shared
  per-player containers (skill:bonus:<uuid>, move:<uuid>) stay, like every protocol member leaves them (removing one could drop
  another mod's concurrent post).

STORAGE (tools/PROFILES-CONTRACT.md)  <world>/mods/Skyy_SkyyTrees/players/<pkey>.properties (pkey = the contract helper; profile 1 =
  <uuid>, profile N = <uuid>-pN): name, v=1, quiet, <Tree>.<Id>=level, <Tree>.off=Id,Id, <Tree>.respecAt=millis. In-memory cache
  keyed by the pkey String. Atomic write (tmp + ATOMIC_MOVE, 5 x 20 ms retries on Windows sharing errors), dirty flush every 10 s
  on the scheduler, saved soon after a respec, flushed on shutdown. A file that exists but cannot be read is NEVER overwritten (the
  player sees "could not be read" and nothing can change until an admin fixes it). Player files are only READ on world threads
  (TreeTick, page, commands, gather) - never on the shared scheduler thread. The vanilla inventory is never touched for a switch.
  trees.properties (written with defaults on first run, /tree reload): tier.levels, tokens.first/every, dust.xpPerDust,
  respec.cooldownMinutes/coins, ability.disabledWorlds/maxRadius, vein.cooldownSec, feller.cooldownSec/needLeaves/maxHeight,
  feedbackMs, debug.extraTokens/extraDust (testing), per node <Tree>.<Id>.max/per/B/tokens/enabled (+ base, items, crops).

PAGE (HANDOFF section 2 rules)  inline only, no underscores in ids, root #SkyyTrRoot anchor = Width/Height only, TextButton +
  EventData for tabs / Back / Respec / Buy / Toggle, Button + ButtonStyle + ItemIcon + Label node cards (the proven SkyySacks bag-cell
  pattern - deliberate, not a slip), payloads matched with a trailing quote (trnode1 never matches trnode10), click handlers rebuild(),
  no MouseEntered handlers, no periodic updates, dynamic label text through b.set. 1000 x 660: tabs Mining | Foraging | Farming |
  Cooking + level / Tokens / Dust, 6 tier rows (VI on top) of node cards in 4 states (Locked #1c1414/#b07a68, Unlockable
  #16301f/#9adf86, Owned #10243d/#9cd8ff, Maxed #3a3010/#ffc300; the selected card uses its state's hover colour), a detail panel
  (icon, name, state, now, next level, cost, what is missing, how it triggers, Buy, Turn off/on), footer "< Skills" (runs /skills
  with CommandManager.handleCommand while this page is still open - the new page replaces it, nothing is closed first) + Respec.
COMMANDS  /tree (alias /trees) opens the last tree viewed (Mining first); /tree mining|foraging|farming|cooking (usage variant with a
  required arg; 3-letter prefixes work); /tree quiet (subcommand) toggles the aggregated "Tree bonus: ..." chat line (per profile);
  all carry setPermissionGroups({"hytale:Adventurer"}). /tree reload = requirePermission("skyytrees.admin") + setPermissionGroups({}).

ENGINE RULES KEPT  one registerSystem per class (TreeDmgSys, TreeTick); components / inventory / stats only on the world thread;
  items to storage first; no lambdas / generics / varargs / autoboxing / enhanced-for / inner classes / String switch /
  try-with-resources; methods added before their callers.

UNVERIFIED (needs Skyy's in-game test): the BREAK path from a world task (performBlockBreak with Store from world.execute, tool
  durability for extra blocks, what flag 4096 means), how the client's crack animation looks with more damage per hit, and everything
  that needs SkyySkills 0.4's trees bridge (built against trees spec 9.3 / 10, not against a built jar).
"""
import sys, os, json, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG   # 0.2.2: the admin config kit (tools/CONFIG-CONTRACT.md)

VERSION = "0.2.3"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.trees"

T = {
    "PKG": PKG,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "DBE": "com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BGA": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "BBD": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "V3I": "org.joml.Vector3i",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "MOD": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier",
    "SMO": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MTG": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BSC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "BHU": "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    # 0.2.3 swing speed (research/Swing-Speed-Spec.md 2.1, verified with tools/dev/reflect.py against HytaleServer.jar 2026-09-25)
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "AEE": "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "OVB": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
    "RIN": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.RootInteraction",
    "I2O": "it.unimi.dsi.fastutil.ints.Int2ObjectMap",
}

# every engine member this mod touches (javassist would also fail to compile, the probe names the drift early)
for c, m in (("DBE", "getDamage"), ("DBE", "setDamage"), ("DBE", "getBlockType"), ("DBE", "isCancelled"),
             ("BHU", "performBlockBreak"), ("INVC", "getItemInHand"), ("IS", "getItemId"), ("IS", "isEmpty"),
             ("SIC", "addOrDropItemStack"), ("PLA", "getInventory"), ("PLA", "getPageManager"), ("PLA", "isWaitingForClientReady"),
             ("PGM", "openCustomPage"), ("CHS", "getChunkSectionReferenceAtBlock"), ("CHS", "getStore"), ("BSC", "get"),
             ("BSC", "getComponentType"), ("BTY", "getAssetMap"), ("BTY", "getId"), ("BTY", "getItem"), ("BTY", "getGathering"),
             ("BGA", "getBreaking"), ("BBD", "getGatherType"), ("ITM", "getAssetMap"), ("ITM", "getId"),
             ("ESM", "getComponentType"), ("ESM", "get"), ("ESM", "putModifier"), ("ESM", "removeModifier"), ("ESM", "getModifier"),
             ("DST", "getHealth"), ("DST", "getStamina"), ("MTG", "MAX"), ("CAL", "ADDITIVE"),
             ("ACH", "getReferenceTo"), ("ST", "getComponent"), ("ST", "getExternalData"), ("ST", "isInThread"), ("EST", "getWorld"), ("WLD", "getName"),
             ("WLD", "getChunkStore"), ("REF", "isValid"), ("REF", "getStore"), ("PR", "getUuid"), ("PR", "getReference"),
             ("PR", "getUsername"), ("PR", "sendMessage"), ("PR", "hasPermission"), ("UNI", "get"), ("UNI", "getPlayer"),
             ("CMGR", "get"), ("CMGR", "handleCommand"), ("MSG", "raw"), ("MSG", "color"), ("PAGE", "rebuild"), ("EVD", "of"),
             ("HSV", "SCHEDULED_EXECUTOR"), ("AC", "setPermissionGroups"), ("AC", "requirePermission"), ("AC", "addSubCommand"),
             ("AC", "addUsageVariant"), ("AC", "withRequiredArg"), ("AC", "addAliases"), ("CB", "getComponent"),
             ("ETS", "tick"), ("ETS", "isParallel"), ("EES", "handle"), ("V3I", "x"), ("V3I", "y"), ("V3I", "z"),
             ("com.hypixel.hytale.component.Archetype", "empty"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove"),
             ("ECC", "getComponentType"), ("ECC", "getActiveEffects"), ("ECC", "addEffect"), ("ECC", "removeEffect"),
             ("EFX", "getAssetMap"), ("AEE", "getRemainingDuration"), ("OVB", "OVERWRITE"), ("RIN", "getAssetMap"),
             ("RIN", "getInteractionIds"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), ("I2O", "get")):
    B.probe(pool, T.get(c, c), m)

LEFT = re.compile(r"@[A-Z][A-Z0-9_]*@")
def sub(src):
    out = src
    for k in sorted(T, key=len, reverse=True):
        out = out.replace("@" + k + "@", T[k])
    left = LEFT.findall(out)
    if left:
        raise SystemExit("unreplaced tokens %s in:\n%s" % (left, out[:300]))
    return out
def _mk(kind, cls, src):
    s = sub(src)
    try:
        if kind == "M": cls.addMethod(CtNewMethod.make(s, cls))
        elif kind == "F": cls.addField(CtField.make(s, cls))
        else: cls.addConstructor(CtNewConstructor.make(s, cls))
    except Exception as e:
        print("COMPILE ERROR in", cls.getName(), ":", str(e)[:400])
        print(s[:1500])
        raise
def M(cls, src): _mk("M", cls, src)
def F(cls, src): _mk("F", cls, src)
def C(cls, src): _mk("C", cls, src)

# ================= Assets.zip checks (every id the jar hands out or shows) =================
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(ASSETS) as z:
    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
def must(i):
    if i not in ITEM_IDS: raise SystemExit("unknown item id: " + i)
    return i

# saplings: Wood_<W>_Trunk* -> Plant_Sapling_<W> (spec: every wood except Burnt and Fir)
WOODS = sorted(set(re.match(r"Wood_(.+?)_Trunk", i).group(1) for i in ITEM_IDS if re.match(r"Wood_(.+?)_Trunk", i)))
SAP_WOODS = [w for w in WOODS if "Plant_Sapling_" + w in ITEM_IDS]
assert "Oak" in SAP_WOODS and "Burnt" not in SAP_WOODS and "Fir" not in SAP_WOODS, SAP_WOODS
# seeds: Plant_Crop_<C>_Block -> Plant_Seeds_<C> (spec: none for Berry, Berry_Wet, Berry_Winter, Wild_Grass)
CROPS = sorted(set(re.match(r"Plant_Crop_(.+?)_Block$", i).group(1) for i in ITEM_IDS if re.match(r"Plant_Crop_(.+?)_Block$", i)))
SEED_CROPS = [c for c in CROPS if "Plant_Seeds_" + c in ITEM_IDS]
assert "Wheat" in SEED_CROPS and "Berry" not in SEED_CROPS and "Wild_Grass" not in SEED_CROPS, SEED_CROPS
# bars: Ore_<Metal>_<Rock> ore BLOCKS (an id with a rock part) -> Ingredient_Bar_<Metal>
ORE_METALS = sorted(set(i.split("_")[1] for i in ITEM_IDS if i.startswith("Ore_") and i.count("_") >= 2))
BAR_METALS = [m for m in ORE_METALS if "Ingredient_Bar_" + m in ITEM_IDS]
assert BAR_METALS == ORE_METALS and "Iron" in BAR_METALS, (ORE_METALS, BAR_METALS)
GEMS = [must("Rock_Gem_" + g) for g in ("Diamond", "Emerald", "Ruby", "Sapphire", "Topaz")]
must("Ingredient_Tree_Sap"); must("Ingredient_Life_Essence")
assert any(i.startswith("Plant_Leaves_") for i in ITEM_IDS)
def crops_ok(names):
    for c in names:
        if "Plant_Crop_%s_Block" % c not in ITEM_IDS: raise SystemExit("no crop block for " + c)
    return ",".join(names)

# SkyySkills' default 100-level table (build_skyyskills_0.3.2.py LEVELS, unchanged in 0.4) - only for the Dust ESTIMATE without
# skill:fn:xp (SkyySkills 0.3.x; 0.4 publishes skill:fn:xp). SkyySkills has ONE levels= table for every skill, Cooking included:
# decision 2 (Cooking 50 in about Alchemy's time) is SkyyCooking's XP per craft (its K_XP model against this same table), not a
# separate Cooking curve - so the estimate holds for all four trees (a custom levels= line in xp.properties skews all four alike).
LEVELS = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000,
          300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000,
          1700000, 1800000, 1900000, 2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2750000, 2900000, 3100000,
          3400000, 3700000, 4000000] + [4300000 + 300000 * i for i in range(50)]
assert len(LEVELS) == 100 and sum(LEVELS) == 637672425
CUM = [0]
for x in LEVELS: CUM.append(CUM[-1] + x)

# ================= the node table (spec 5 + 6, Cooking spec 7.2) =================
TREES = ["Mining", "Foraging", "Farming", "Cooking", "Acrobatics", "Exploration"]   # 0.2: append-only (tree index = saved key order)
TCOLOR = ["#8fc8ff", "#8fe08a", "#f0d060", "#ffb070", "#c8a0ff", "#e0a040"]
for n, tn in enumerate(TREES): T["T_" + tn.upper()] = str(n)
# 0.2 per-tree Dust rate defaults (dust.xpPerDust.<Tree>); a tree not listed follows the global dust.xpPerDust
DUST_DEF = {"Acrobatics": 2, "Exploration": 5}
SLOT_TIER = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6]
SLOT_MAX = [25, 20, 15, 10, 10, 15, 10, 10, 10, 20, 10, 5]
SLOT_B = [5, 5, 5, 150, 150, 100, 500, 1000, 1000, 200, 4000, 150000]
SLOT_TOK = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]
KINDS = ["DMG", "DD", "XP", "HP", "STA", "ITEM", "EXTRA", "COINS", "SPREAD", "MOVE", "VEIN", "FELLER", "EXTRA2", "COOK", "MASTER"]
KINDS += ["RSPD", "RJMP", "RFALL", "RDODGE", "LUCK", "SCAV", "SOON"]   # 0.2 (existing kind numbers unchanged)
assert KINDS.index("MASTER") == 14 and KINDS.index("SOON") == 21
KINDS += ["DJUMP"]   # 0.2.1 Double Jump (research/Double-Jump-Spec.md 3.1; existing kind numbers unchanged)
assert KINDS.index("DJUMP") == 22
_KINDS_022 = list(KINDS)
KINDS += ["SWING"]   # 0.2.3 swing speed (research/Swing-Speed-Spec.md 3.1; existing kind numbers unchanged)
assert KINDS.index("SWING") == 23 and KINDS[:23] == _KINDS_022 and len(_KINDS_022) == 23
assert _KINDS_022 == ["DMG", "DD", "XP", "HP", "STA", "ITEM", "EXTRA", "COINS", "SPREAD", "MOVE", "VEIN", "FELLER", "EXTRA2", "COOK", "MASTER",
                      "RSPD", "RJMP", "RFALL", "RDODGE", "LUCK", "SCAV", "SOON", "DJUMP"]
for n, k in enumerate(KINDS): T["K_" + k] = str(n)
PAIDM = "Rolls on every block that pays Mining XP"
PAIDF = "Rolls on every log that pays Foraging XP"
PAIDA = "Rolls on every crop that pays Farming XP"
FLAT = "Flat speed layer - applied by SkyySkills or SkyyAccessories (movement protocol)"
ON = "Always on while the node is on"
S04 = " - needs SkyySkills 0.4"
READ = "SkyyCooking reads it when you cook at a Cooking Bench"
AFLAT = "Flat layer of the movement protocol (trees.acrobatics) - applied by SkyySkills or SkyyAccessories"
AFALL = "Less damage from every fall (SkyySkills applies it) - a bigger fall is needed for Acrobatics fall XP"
ADODGE = "Your vanilla dodge pushes you further (SkyySkills dodge boost) - needs SkyySkills 0.4.1"
ELOOT = "SkyyExploration reads it when you open a world loot chest for the first time"
SOONHOW = "Draft slot - nothing here yet and it cannot be unlocked"
# 0.2.1 Double Jump (research/Double-Jump-Spec.md 2.2): %K = the trigger key SkyySkills 0.4.2 publishes as skill:dj:key (else "crouch")
DJ_ICON = "Plant_Fruit_Windwillow" if "Plant_Fruit_Windwillow" in ITEM_IDS else must("Ingredient_Feathers_Light")
ADJ = "Press %K in mid-air - once per jump - resets when you land - costs Stamina - no Acrobatics XP - needs SkyySkills 0.4.2"
# (id, name, icon, kind, max, per, base, now, how, list key, default list)
NODES = {
 "Mining": [
  # LOCKED Skyy 2026-09-25: per 0.016 = +40% at 25. A file already on 0.01 keeps +25% until edited.
  ("MSpeed", "Mining Speed", "Tool_Pickaxe_Iron", "SWING", 25, 0.016, 0, "+%V pickaxe swing speed", "Less wait between pickaxe swings - more blocks per second, even when one hit breaks the block (any pickaxe, also on mobs)", "", ""),
  ("MFortune", "Mining Fortune", "Ore_Gold", "DD", 20, 0.01, 0, "+%V double-drop chance on mined blocks", "Adds to your Mining double-drop perk" + S04, "", ""),
  ("MWisdom", "Mining Wisdom", "Ingredient_Crystal_Blue", "XP", 15, 0.01, 0, "+%V Mining XP", "Every block that pays Mining XP pays more" + S04, "", ""),
  ("MStamina", "Miner Stamina", "Tool_Pickaxe_Crude", "STA", 10, 0.3, 0, "+%V max Stamina", ON, "", ""),
  ("MGems", "Gem Finder", "Rock_Gem_Ruby", "ITEM", 10, 0.0002, 0, "%V chance per block for a random gem", PAIDM + " - diamond emerald ruby sapphire or topaz", "items", ",".join(GEMS)),
  ("MVeins", "Rich Veins", "Ore_Iron", "EXTRA", 15, 0.02, 0, "%V chance an ore drops once more", "Rolls on every ore block that pays Mining XP", "", ""),
  ("MCoins", "Pocket Change", "Ingredient_Bar_Gold", "COINS", 10, 0.002, 0, "%V chance per block for coins equal to your Mining level", PAIDM + " - needs SkyyCoins", "", ""),
  ("MSpread", "Mining Spread", "Rock_Stone", "SPREAD", 10, 0.03, 0, "%V chance to also break 1 touching block of the same kind", PAIDM + " - never placed blocks", "", ""),
  ("MRunner", "Tunnel Runner", "Armor_Leather_Light_Legs", "MOVE", 10, 0.01, 0, "+%V move speed while holding a pickaxe", FLAT, "", ""),
  # LOCKED Skyy 2026-09-25: rock and ore (was ore only).
  ("MHeavy", "Heavy Pick", "Tool_Pickaxe_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on rock and ore", "Rock and ore break in fewer hits (more damage per hit)", "", ""),
  ("MBars", "Prospector", "Ingredient_Bar_Iron", "ITEM", 10, 0.01, 0, "%V chance an ore also gives its smelted bar", "Rolls on every ore block that pays Mining XP (copper to adamantite)", "", ""),
  ("MVein", "Vein Burst", "Ore_Adamantite", "VEIN", 5, 2.0, 4.0, "Breaks up to %V more touching ore of the same kind", "On an ore block that pays Mining XP - cooldown %C s - never placed blocks", "", ""),
 ],
 "Foraging": [
  # LOCKED Skyy 2026-09-25 HARD RULE: this bonus is for tree and wood breaking only. It must not change weapon-axe combat speed.
  # Weapon axes get their own combat swing-speed stat. 0.2.3 still speeds every Hatchet_Attack swing, including hits on mobs.
  ("FSpeed", "Chopping Speed", "Tool_Hatchet_Iron", "SWING", 25, 0.01, 0, "+%V hatchet swing speed", "Less wait between hatchet swings - more logs per second (any hatchet, also on mobs)", "", ""),
  ("FFortune", "Foraging Fortune", "Wood_Oak_Trunk", "DD", 20, 0.01, 0, "+%V double-drop chance on logs", "Adds to your Foraging double-drop perk" + S04, "", ""),
  ("FWisdom", "Foraging Wisdom", "Ingredient_Crystal_Green", "XP", 15, 0.01, 0, "+%V Foraging XP", "Every log that pays Foraging XP pays more" + S04, "", ""),
  ("FVigor", "Forest Vigor", "Plant_Fruit_Apple", "HP", 10, 1.0, 0, "+%V max Health", ON, "", ""),
  ("FSap", "Sap Tapper", "Ingredient_Tree_Sap", "ITEM", 10, 0.01, 0, "%V chance per log for 1 Tree Sap", PAIDF, "items", "Ingredient_Tree_Sap"),
  ("FSapling", "Replanter", "Plant_Sapling_Oak", "ITEM", 15, 0.01, 0, "%V chance per log for a sapling of that wood", PAIDF + " (not Burnt or Fir)", "", ""),
  ("FCoins", "Pocket Change", "Ingredient_Bar_Gold", "COINS", 10, 0.002, 0, "%V chance per log for coins equal to your Foraging level", PAIDF + " - needs SkyyCoins", "", ""),
  ("FSpread", "Timber Spread", "Wood_Birch_Trunk", "SPREAD", 10, 0.03, 0, "%V chance to also break 1 touching log of the same kind", PAIDF + " - never placed logs", "", ""),
  ("FStride", "Woodland Stride", "Armor_Leather_Light_Legs", "MOVE", 10, 0.01, 0, "+%V move speed while holding a hatchet", FLAT, "", ""),
  ("FSpeed2", "Heavy Hatchet", "Tool_Hatchet_Mithril", "DMG", 20, 0.02, 0, "+%V breaking power on wood", "Wood blocks break in fewer hits (more damage per hit)", "", ""),
  ("FFortune2", "Fortune II", "Wood_Redwood_Trunk", "DD", 10, 0.02, 0, "+%V double-drop chance on logs - adds to Fortune", "Stacks with Foraging Fortune" + S04, "", ""),
  ("FFeller", "Tree Feller", "Tool_Hatchet_Adamantite", "FELLER", 5, 1.0, 0.0, "Breaks %V more logs beside it on the same level", "On a log that pays Foraging XP - same Y level only (Hytale fells the tree once that layer is cut) - natural trees - cooldown %C s", "", ""),
 ],
 "Farming": [
  ("AFortune", "Farming Fortune", "Plant_Crop_Pumpkin_Block", "DD", 25, 0.01, 0, "+%V double-drop chance on ripe crops", "Broken or F-harvested - adds to your Farming perk" + S04, "", ""),
  ("ASeeds", "Seed Saver", "Plant_Seeds_Wheat", "ITEM", 20, 0.01, 0, "%V chance per crop for 1 of its seeds", PAIDA + " (no seeds for berries)", "", ""),
  ("AWisdom", "Farming Wisdom", "Ingredient_Crystal_Yellow", "XP", 15, 0.01, 0, "+%V Farming XP", "Every crop that pays Farming XP pays more" + S04, "", ""),
  ("AHearty", "Hearty Harvest", "Plant_Fruit_Berries_Red", "HP", 10, 1.0, 0, "+%V max Health", ON, "", ""),
  ("AEssence", "Essence Gatherer", "Ingredient_Life_Essence", "ITEM", 10, 0.005, 0, "%V chance per crop for 1 Life Essence", PAIDA, "items", "Ingredient_Life_Essence"),
  ("AGrain", "Grain Mastery", "Plant_Crop_Wheat_Item", "EXTRA", 15, 0.02, 0, "%V extra-drop chance on wheat rice corn and cotton", "Gives the crop's drops once more", "crops", crops_ok(["Wheat", "Rice", "Corn", "Cotton"])),
  ("ARoots", "Root Mastery", "Plant_Seeds_Carrot", "EXTRA", 10, 0.03, 0, "%V extra-drop chance on carrot potato turnip and onion", "Gives the crop's drops once more", "crops", crops_ok(["Carrot", "Potato", "Turnip", "Onion"])),
  ("AGarden", "Garden Mastery", "Plant_Seeds_Tomato", "EXTRA", 10, 0.03, 0, "%V extra-drop chance on tomato lettuce cauliflower chilli aubergine and pumpkin", "Gives the crop's drops once more", "crops", crops_ok(["Tomato", "Lettuce", "Cauliflower", "Chilli", "Aubergine", "Pumpkin"])),
  ("ARunner", "Field Runner", "Tool_Hoe_Iron", "MOVE", 10, 0.01, 0, "+%V move speed while holding a hoe or sickle", FLAT, "", ""),
  ("AHerbs", "Herbalist", "Plant_Seeds_Health1", "EXTRA", 20, 0.015, 0, "%V extra-drop chance on health mana and stamina crops", "Potion crops - pairs with Alchemy", "crops", crops_ok(["Health1", "Health2", "Health3", "Mana1", "Mana2", "Mana3", "Stamina1", "Stamina2", "Stamina3"])),
  ("AFortune2", "Fortune II", "Plant_Crop_Wheat_Block", "DD", 10, 0.02, 0, "+%V double-drop chance on crops - adds to Fortune", "Stacks with Farming Fortune" + S04, "", ""),
  ("ACorn", "Cornucopia", "Ingredient_Life_Essence_Concentrated", "EXTRA2", 5, 0.03, 0, "%V chance a crop drops two more times", PAIDA, "", ""),
 ],
 "Cooking": [
  ("CGourmet", "Gourmet", "Food_Pie_Apple", "COOK", 25, 0.008, 0, "%V chance a dish comes out 1 Grade higher", READ, "", ""),
  ("CBatch", "Batch Cook", "Food_Bread", "COOK", 20, 0.01, 0, "%V chance of one extra dish of the same Grade", READ + " - the extra dish pays no XP", "", ""),
  ("CWisdom", "Cooking Wisdom", "Food_Cheese", "XP", 15, 0.01, 0, "+%V Cooking XP", "Every craft that pays Cooking XP pays more" + S04, "", ""),
  ("CFed", "Well Fed", "Food_Wildmeat_Cooked", "HP", 10, 1.0, 0, "+%V max Health", ON, "", ""),
  ("CFrugal", "Frugal", "Ingredient_Salt", "COOK", 10, 0.02, 0, "%V chance to get back one ingredient", READ + " - never fuel", "", ""),
  ("CGrill", "Grill Mastery", "Food_Fish_Grilled", "COOK", 15, 0.02, 0, "%V chance of +1 Grade on cooked meat fish and vegetables", READ + " - tier 1 dishes", "", ""),
  ("CPrep", "Prep Mastery", "Food_Kebab_Meat", "COOK", 10, 0.03, 0, "%V chance of +1 Grade on bread kebabs and salads", READ + " - tier 2 dishes", "", ""),
  ("CBaker", "Baker Mastery", "Food_Pie_Pumpkin", "COOK", 10, 0.03, 0, "%V chance of +1 Grade on popcorn pies and Caesar salad", READ + " - tier 3 dishes", "", ""),
  ("CIngr", "Prep Cook", "Ingredient_Flour", "COOK", 10, 0.03, 0, "%V chance an ingredient craft gives double output", READ + " - flour dough salt and spices", "", ""),
  ("CGourmet2", "Gourmet II", "Food_Pie_Meat", "COOK", 20, 0.01, 0, "%V chance of +1 Grade on any dish - adds to Gourmet", READ, "", ""),
  ("CSig", "Signature Dish", "Food_Salad_Caesar", "COOK", 10, 0.01, 0, "%V chance of +2 Grades on a dish", READ, "", ""),
  ("CMaster", "Master Chef", "Bench_Cooking", "MASTER", 5, 0.05, 0, "", "Level 1 = +1 Grade on every dish - each level after adds a chance of one more", "", ""),
 ],
 # 0.2 (research/Exploration-Build-Spec.md 4.2): verified hooks only - movement protocol source trees.acrobatics, skyytree_stamina,
 # skill:bonus dodge.acrobatics (SkyySkills 0.4.1)
 "Acrobatics": [
  ("RSpeed", "Fleet Foot", "Armor_Leather_Light_Legs", "RSPD", 25, 0.004, 0, "+%V move speed", AFLAT + " - always on", "", ""),
  ("RJump", "Spring Step", "Ingredient_Feathers_Light", "RJMP", 20, 0.02, 0, "+%V blocks jump height", AFLAT + " - always on", "", ""),
  ("RStamina", "Second Wind", "Food_Bread", "STA", 15, 0.2, 0, "+%V max Stamina", ON, "", ""),
  ("RFall", "Soft Landing", "Glider", "RFALL", 10, 0.01, 0, "-%V fall damage", AFALL, "", ""),
  ("RDouble", "Double Jump", DJ_ICON, "DJUMP", 10, 0.05, 0.5, "Jump once more in mid-air at %V of your jump height", ADJ, "", ""),
  ("RStamina2", "Marathon", "Food_Pie_Apple", "STA", 15, 0.2, 0, "+%V max Stamina - adds to Second Wind", ON, "", ""),
  ("RSpeed2", "Sprinter", "Armor_Leather_Light_Legs", "RSPD", 10, 0.005, 0, "+%V move speed - adds to Fleet Foot", AFLAT + " - always on", "", ""),
  ("RJump2", "High Jumper", "Ingredient_Feathers_Red", "RJMP", 10, 0.03, 0, "+%V blocks jump height - adds to Spring Step", AFLAT + " - always on", "", ""),
  ("RFall2", "Featherfall", "Ingredient_Feathers_Dark", "RFALL", 10, 0.005, 0, "-%V fall damage - adds to Soft Landing", AFALL, "", ""),
  ("RStamina3", "Endurance", "Food_Wildmeat_Cooked", "STA", 20, 0.1, 0, "+%V max Stamina - adds to Marathon", ON, "", ""),
  ("RDodge2", "Evasion", "Glider", "RDODGE", 10, 0.01, 0, "+%V dodge push", ADODGE, "", ""),
  ("RSpeed3", "Windrunner", "Armor_Leather_Light_Legs", "RSPD", 5, 0.01, 0, "+%V move speed - adds to Sprinter", AFLAT + " - always on", "", ""),
 ],
 # 0.2 (spec 4.3): SMALL FIRST DRAFT - Skyy designs the rest of the Exploration tree later. Nothing here boosts Exploration XP.
 "Exploration": [
  ("EHeart", "Wanderer's Heart", "Plant_Fruit_Apple", "HP", 25, 0.4, 0, "+%V max Health", ON, "", ""),
  ("ELuck", "Treasure Sense", "Rock_Gem_Ruby", "LUCK", 20, 0.005, 0, "+%V chest luck - the chance of an extra roll on a first-opened loot chest", ELOOT + " - adds to the chest luck of your Exploration level", "", ""),
  ("EScav", "Scavenger", "Ingredient_Bar_Gold", "SCAV", 15, 0.01, 0, "%V chance of coins (10 x Exploration level) on a first-opened loot chest", ELOOT + " - needs SkyyCoins", "", ""),
  ("EHeart2", "Hearty Wanderer", "Plant_Fruit_Berries_Red", "HP", 10, 1.0, 0, "+%V max Health - adds to Wanderer's Heart", ON, "", ""),
 ] + [("ESoon%d" % n, "Coming later", "Deco_Scroll", "SOON", SLOT_MAX[n - 1], 0.0, 0, "", SOONHOW, "", "") for n in range(5, 13)],
}
ROWS = []
for t, tn in enumerate(TREES):
    assert len(NODES[tn]) == 12
    for s, n in enumerate(NODES[tn]):
        nid, name, icon, kind, mx, per, base, now, how, lk, lst = n
        must(icon)
        assert mx == SLOT_MAX[s], (tn, nid)
        assert kind in KINDS and "_" not in nid and "," not in name and ":" not in name
        for x in (lst.split(",") if lk == "items" else []): must(x)
        ROWS.append(dict(t=t, s=s + 1, id=nid, name=name, icon=icon, kind=KINDS.index(kind), max=mx, per=per, base=base,
                         B=SLOT_B[s], tok=SLOT_TOK[s], tier=SLOT_TIER[s], now=now, how=how, lk=lk, lst=lst))
        T["I_" + nid.upper()] = str(t * 12 + s)
assert len(ROWS) == 72 and len(set(r["id"] for r in ROWS)) == 72
SOON_ROWS = [r for r in ROWS if KINDS[r["kind"]] == "SOON"]
assert len(SOON_ROWS) == 8 and all(TREES[r["t"]] == "Exploration" and r["s"] >= 5 for r in SOON_ROWS)
# spec 4.2 totals at max (Acrobatics) and 4.3 (Exploration)
def _tot(ids): return round(sum(r["max"] * r["per"] for r in ROWS if r["id"] in ids), 6)
assert _tot(("RSpeed", "RSpeed2", "RSpeed3")) == 0.2 and _tot(("RJump", "RJump2")) == 0.7 and _tot(("RFall", "RFall2")) == 0.15
assert _tot(("RDodge2",)) == 0.1 and _tot(("RStamina", "RStamina2", "RStamina3")) == 8.0 and _tot(("EHeart", "EHeart2")) == 20.0
assert _tot(("ELuck",)) == 0.1 and _tot(("EScav",)) == 0.15
# 0.2.1: Double Jump sits exactly where Quick Dodge sat (same index, same Token / Dust cost), 55% at level 1, 100% at level 10
_RD = [r for r in ROWS if r["id"] == "RDouble"]
assert len(_RD) == 1 and not [r for r in ROWS if r["id"] == "RDodge"]
_RD = _RD[0]
assert TREES[_RD["t"]] == "Acrobatics" and _RD["s"] == 5 and _RD["tier"] == 2 and _RD["max"] == 10 and _RD["B"] == 150 and _RD["tok"] == 1
assert abs(_RD["base"] + _RD["per"] * 1 - 0.55) < 1e-9 and abs(_RD["base"] + _RD["per"] * 10 - 1.0) < 1e-9 and T["I_RDOUBLE"] == "52"
_FF = [r for r in ROWS if r["id"] == "FFeller"][0]
assert _FF["per"] == 1.0 and _FF["base"] == 0.0 and _FF["max"] == 5 and TREES[_FF["t"]] == "Foraging" and _FF["s"] == 12
# spec 4.3: the 4 draft nodes cost 989,375 Dust (about 4.9M Exploration XP at 5 XP per Dust)
assert sum(sum(r["B"] * n ** 3 for n in range(1, r["max"])) for r in ROWS if TREES[r["t"]] == "Exploration" and KINDS[r["kind"]] != "SOON") == 989375
# spec 5: maxing a whole tree costs 37,778,125 Dust with the default template
assert sum(sum(r["B"] * n ** 3 for n in range(1, r["max"])) for r in ROWS[:12]) == 37778125

def jstr(xs): return "new String[] { " + ", ".join(json.dumps(x) for x in xs) + " }"
def jint(xs): return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }"
def jlong(xs): return "new long[] { " + ", ".join("%dL" % x for x in xs) + " }"
def jdbl(xs): return "new double[] { " + ", ".join(repr(float(x)) for x in xs) + " }"

# ================= 0.2.3 swing speed assets (research/Swing-Speed-Spec.md 2.3 + 3.7) =================
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

# ================= default trees.properties =================
DL = ["# SkyyTrees %s - skill trees for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration. /tree reload re-reads this file (perm skyytrees.admin)." % VERSION,
      "# Comments must stay on their own lines. A missing key uses the built-in default.",
      "# Also editable in game: SkyWynn Menu -> Server Setup -> Trees (SkyyMenu 0.3). Every change is logged in config-changes.log.",
      "# Skill level that opens tiers I..VI",
      "tier.levels=1,10,20,30,45,60",
      "# Tokens unlock nodes: level >= 1 -> first + floor(level / every)  (1 at level 1, 21 at level 100)",
      "tokens.first=1", "tokens.every=5",
      "# Dust levels nodes: floor(total skill XP / xpPerDust); node level n -> n+1 costs B x n^3 Dust",
      "dust.xpPerDust=10"] + ["# Per-tree Dust rate: dust.xpPerDust.<Tree> overrides dust.xpPerDust for that tree (a tree without a line uses dust.xpPerDust).",
      "# Acrobatics XP is capped per minute and Exploration XP is one-time, so their trees get more Dust per XP."] + \
     ["dust.xpPerDust.%s=%d" % (t, DUST_DEF[t]) for t in TREES if t in DUST_DEF] + [
      "# Respec: free full refund of one tree; minutes between respecs of the same tree; optional coin price (SkyyCoins)",
      "respec.cooldownMinutes=10", "respec.coins=0",
      "# Abilities (Mining/Timber Spread, Vein Burst, Tree Feller) never run in these worlds (comma list of world names, e.g. the hub)",
      "ability.disabledWorlds=",
      "# Horizontal radius cap for Spread / Vein Burst / Tree Feller (and the vertical cap for Vein Burst)",
      "ability.maxRadius=6",
      "vein.cooldownSec=40",
      "# Tree Feller: breaks logs beside the cut on the SAME Y level only. Hytale itself fells the tree once its whole layer is cut.",
      "# LOCKED Skyy 2026-09-25 (research/Tree-Fall-Spec.md): extra logs by level = 1, 2, 4, 5, 6, 10.",
      "# Level 6 jumps to 10 so a very large tree is not broken as a whole layer (that could crash). Cooldown 3 s (was 5).",
      "# This build still uses base + per x level, and the max level breaks every log on that level up to feller.maxPerLayer.",
      "# The locked table replaces that formula in the next Trees build. A file still on feller.cooldownSec=5 keeps 5 until edited.",
      "feller.cooldownSec=3", "feller.maxPerLayer=64",
      "# Natural-tree check: the cut wood must touch leaves within feller.maxHeight blocks above or below the cut (nothing there is broken)",
      "feller.needLeaves=true", "feller.maxHeight=32",
      "# Felled trees (SkyySkills 0.4.2 pays every log that falls): those logs also roll Sap Tapper, Replanter and Pocket Change",
      "felled.nodes=true",
      "# Swing speed (0.2.3): Mining Speed / Chopping Speed shorten the wait between pickaxe / hatchet swings. Their per = fraction per",
      "# level (0.01 = 1%), whole percents, capped at +40% (then the swings are back to back). false = those two nodes do nothing.",
      "swing.enabled=true",
      "# Aggregated 'Tree bonus: ...' chat line at most every feedbackMs (per player; /tree quiet hides it)",
      "feedbackMs=2000",
      "# Testing only: extra tokens / Dust for every tree of every player",
      "debug.extraTokens=0", "debug.extraDust=0",
      "# ---- nodes: <Tree>.<Id>.max / per / B / tokens / enabled (Vein Burst + Tree Feller also base; lists: items / crops) ----",
      "# per = amount per node level: a fraction for % nodes (0.02 = 2%), a flat amount for Health / Stamina, blocks for Vein Burst",
      "# (up to base + per x level), logs on the cut level for Tree Feller (this build: base + per x level; max level = the whole layer;",
      "# LOCKED 2026-09-25 table is 1, 2, 4, 5, 6, 10 extra logs - applied in the next Trees build),",
      "# a fraction of your own jump height for Double Jump (base + per x level); Master Chef: per = chance per level above 1."]
def node_lines(r):
    tn = TREES[r["t"]]
    k = "%s.%s." % (tn, r["id"])
    out = ["# %s S%d %s (tier %s)" % (tn, r["s"], r["name"], ["I", "II", "III", "IV", "V", "VI"][r["tier"] - 1])]
    out.append(k + "max=%d" % r["max"])
    out.append(k + "per=%s" % repr(float(r["per"])))
    if KINDS[r["kind"]] in ("VEIN", "FELLER", "DJUMP"): out.append(k + "base=%s" % repr(float(r["base"])))
    out.append(k + "B=%d" % r["B"])
    out.append(k + "tokens=%d" % r["tok"])
    out.append(k + "enabled=true")
    if r["lk"]: out.append(k + r["lk"] + "=" + r["lst"])
    return out
SOON_NOTE = "# Exploration S5-S12 are 'Coming later' placeholders of the draft tree: they have no lines and can never be turned on"
for r in ROWS:
    if KINDS[r["kind"]] == "SOON": continue   # 0.2 spec 4.1: no node lines for SOON slots
    DL.extend(node_lines(r))
DL.append(SOON_NOTE)
DEFAULTS = "\n".join(DL) + "\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
# 0.2: appended ONCE to a trees.properties that 0.1 wrote (TreeCfg.has02 finds none of these keys). Same numbers as the code defaults.
ADD02 = ["# ---------- SkyyTrees 0.2 (appended once to a 0.1 file): Acrobatics and Exploration trees, per-tree Dust rates ----------"]
ADD02 += ["# Per-tree Dust rate: dust.xpPerDust.<Tree> overrides dust.xpPerDust for that tree (a tree without a line uses dust.xpPerDust).",
      "# Acrobatics XP is capped per minute and Exploration XP is one-time, so their trees get more Dust per XP."] + \
     ["dust.xpPerDust.%s=%d" % (t, DUST_DEF[t]) for t in TREES if t in DUST_DEF]
for r in ROWS:
    if TREES[r["t"]] in ("Acrobatics", "Exploration") and KINDS[r["kind"]] != "SOON": ADD02.extend(node_lines(r))
ADD02.append(SOON_NOTE)
ADD02 = "\n".join(ADD02) + "\n"
assert all(ord(ch) < 128 for ch in ADD02)
assert "SOON" not in DEFAULTS and "ESoon" not in DEFAULTS and "ESoon" not in ADD02
assert "dust.xpPerDust.Acrobatics=2" in DEFAULTS and "dust.xpPerDust.Exploration=5" in DEFAULTS and "dust.xpPerDust.Exploration=5" in ADD02
assert "Acrobatics.RSpeed.max=25" in ADD02 and "Exploration.EHeart2.enabled=true" in ADD02 and "Mining." not in ADD02
# 0.2.1: appended ONCE to a file 0.2 wrote (it has the 0.2 keys but no Acrobatics.RDouble.* key): Double Jump replaced Quick Dodge
ADD021DJ = ["# ---------- SkyyTrees 0.2.1 (added once to a 0.2 file): Double Jump replaced Quick Dodge in Acrobatics S5 ----------",
            "# The old Acrobatics.RDodge.* lines are no longer read (their numbers do not carry over to Double Jump) - you can delete them."]
for r in ROWS:
    if r["id"] == "RDouble": ADD021DJ.extend(node_lines(r))
ADD021DJ = "\n".join(ADD021DJ) + "\n"
# 0.2.1: appended ONCE to any older file (no feller.maxPerLayer key), right after the old default Tree Feller lines were rewritten in
# place (TreeCfg.migrateFeller). It only ADDS keys: a second feller.cooldownSec / FFeller line here would override a custom value.
ADD021FEL = "\n".join([
    "# ---------- SkyyTrees 0.2.1 (added once): Tree Feller rework ----------",
    "# Tree Feller now breaks logs beside the cut on the SAME Y level only (Hytale itself fells a tree once its whole layer is cut):",
    "# levels 1-4 = 1-4 more logs (base + per x level), the max level = every log of that tree on that level, up to feller.maxPerLayer.",
    "# The old default lines Foraging.FFeller.per=8.0 / Foraging.FFeller.base=8.0 / feller.cooldownSec=30 were changed to 1.0 / 0.0 / 3",
    "# (custom values were kept). feller.maxHeight now only sets how far above / below the cut the leaves check looks.",
    "feller.maxPerLayer=64",
    "# Felled trees (SkyySkills 0.4.2 pays every log that falls): those logs also roll Sap Tapper, Replanter and Pocket Change.",
    "felled.nodes=true"]) + "\n"
for _b in (ADD021DJ, ADD021FEL): assert all(ord(ch) < 128 for ch in _b)
assert "Acrobatics.RDodge." not in DEFAULTS and "Acrobatics.RDodge." not in ADD02 and "Acrobatics.RDodge2.max=10" in DEFAULTS
assert "Acrobatics.RDouble.base=0.5" in DEFAULTS and "Acrobatics.RDouble.max=10" in ADD02 and "Acrobatics.RDouble.base=0.5" in ADD021DJ
assert "Foraging.FFeller.per=1.0" in DEFAULTS and "Foraging.FFeller.base=0.0" in DEFAULTS and "feller.cooldownSec=3" in DEFAULTS
assert "feller.maxPerLayer=64" in DEFAULTS and "felled.nodes=true" in DEFAULTS and "feller.cooldownSec=30" not in DEFAULTS
assert "feller.maxPerLayer=64" in ADD021FEL and "felled.nodes=true" in ADD021FEL
assert not [l for l in ADD021FEL.splitlines() if not l.startswith("#") and (l.startswith("feller.cooldownSec") or "FFeller" in l)]
assert "Acrobatics." not in ADD021FEL and "feller." not in ADD021DJ
# 0.2.3: appended ONCE to any older file (no swing.enabled key), right after the untouched old default lines Mining.MSpeed.per=0.02 /
# Foraging.FSpeed.per=0.02 were rewritten in place to 0.01 (TreeCfg.migrateSwing). It only ADDS keys: a second MSpeed / FSpeed line here
# would override a custom value.
ADD023 = "\n".join([
    "# ---------- SkyyTrees 0.2.3 (added once): swing speed ----------",
    "# Mining Speed / Chopping Speed no longer add breaking power: they shorten the wait between pickaxe / hatchet swings.",
    "# The old default lines Mining.MSpeed.per=0.02 / Foraging.FSpeed.per=0.02 were changed to 0.01 (custom values were kept).",
    "# Foraging S10 Chopping Speed II (the Foraging.FSpeed2 lines) is now called Heavy Hatchet - still breaking power on wood.",
    "# Swing speed (0.2.3): Mining Speed / Chopping Speed shorten the wait between pickaxe / hatchet swings. Their per = fraction per",
    "# level (0.01 = 1%), whole percents, capped at +40% (then the swings are back to back). false = those two nodes do nothing.",
    "swing.enabled=true"]) + "\n"
assert all(ord(ch) < 128 for ch in ADD023)
assert "swing.enabled=true" in DEFAULTS and "swing.enabled=true" in ADD023 and DEFAULTS.count("swing.enabled=") == 1
assert not [l for l in ADD023.splitlines() if not l.startswith("#") and l != "swing.enabled=true"]
assert "Mining.MSpeed.per=0.016" in DEFAULTS and "Foraging.FSpeed.per=0.01" in DEFAULTS and "Foraging.FSpeed2.per=0.02" in DEFAULTS
assert "Mining.MHeavy.per=0.02" in DEFAULTS and "# Foraging S10 Heavy Hatchet (tier V)" in DEFAULTS and "Chopping Speed II" not in DEFAULTS

# ================= classes =================
defs = pool.makeClass(PKG + ".TreeDefs")
cfg = pool.makeClass(PKG + ".TreeCfg")
dat = pool.makeClass(PKG + ".TreeData")
sto = pool.makeClass(PKG + ".TreeStore")
stk = pool.makeClass(PKG + ".SaveTask")
calc = pool.makeClass(PKG + ".TreeCalc")
fx = pool.makeClass(PKG + ".TreeFx")
swg = pool.makeClass(PKG + ".TreeSwing")   # 0.2.3 swing speed (no system - called from TreeTick)
msg = pool.makeClass(PKG + ".TreeMsg")
abil = pool.makeClass(PKG + ".TreeAbil")
gat = pool.makeClass(PKG + ".TreeGather")
tfn = pool.makeClass(PKG + ".TreeFn")
bfn = pool.makeClass(PKG + ".TreeBonusFn")
ffn = pool.makeClass(PKG + ".TreeFelledFn")
dmg = pool.makeClass(PKG + ".TreeDmgSys", pool.get(T["EES"]))
tick = pool.makeClass(PKG + ".TreeTick", pool.get(T["ETS"]))
svr = pool.makeClass(PKG + ".TreeSaver")
ops = pool.makeClass(PKG + ".TreeOps")
page = pool.makeClass(PKG + ".TreePage", pool.get(T["PAGE"]))
vcmd = pool.makeClass(PKG + ".TreeSkillCmd", pool.get(T["APC"]))
qcmd = pool.makeClass(PKG + ".TreeQuietCmd", pool.get(T["APC"]))
rcmd = pool.makeClass(PKG + ".TreeReloadCmd", pool.get(T["APC"]))
scmd = pool.makeClass(PKG + ".TreeSwingCmd", pool.get(T["APC"]))   # 0.2.3 /tree swing (admin)
cmd = pool.makeClass(PKG + ".TreesCmd", pool.get(T["APC"]))
pl = pool.makeClass(PKG + ".SkyyTreesPlugin", pool.get(T["JP"]))

# ================= TreeDefs: the generated node table + small pure helpers =================
F(defs, "public static final String[] TREES = %s;" % jstr(TREES))
F(defs, "public static final String[] TCOLOR = %s;" % jstr(TCOLOR))
F(defs, "public static final int NT = %d;" % len(TREES))
F(defs, "public static final int N = %d;" % len(ROWS))
F(defs, "public static final int SOON_N = %d;" % len(SOON_ROWS))
F(defs, "public static final String NAMES_CSV = %s;" % json.dumps(",".join(TREES)))
F(defs, "public static final long[] D_DUST = %s;" % jlong([DUST_DEF.get(t, 0) for t in TREES]))
F(defs, "public static final String[] ID = %s;" % jstr([r["id"] for r in ROWS]))
F(defs, "public static final String[] NAME = %s;" % jstr([r["name"] for r in ROWS]))
F(defs, "public static final String[] ICON = %s;" % jstr([r["icon"] for r in ROWS]))
F(defs, "public static final String[] NOW = %s;" % jstr([r["now"] for r in ROWS]))
F(defs, "public static final String[] HOW = %s;" % jstr([r["how"] for r in ROWS]))
F(defs, "public static final String[] LISTKEY = %s;" % jstr([r["lk"] for r in ROWS]))
F(defs, "public static final String[] D_LIST = %s;" % jstr([r["lst"] for r in ROWS]))
F(defs, "public static final int[] KIND = %s;" % jint([r["kind"] for r in ROWS]))
F(defs, "public static final int[] TIER = %s;" % jint([r["tier"] for r in ROWS]))
F(defs, "public static final int[] D_MAX = %s;" % jint([r["max"] for r in ROWS]))
F(defs, "public static final int[] D_TOK = %s;" % jint([r["tok"] for r in ROWS]))
F(defs, "public static final long[] D_B = %s;" % jlong([r["B"] for r in ROWS]))
F(defs, "public static final double[] D_PER = %s;" % jdbl([r["per"] for r in ROWS]))
F(defs, "public static final double[] D_BASE = %s;" % jdbl([r["base"] for r in ROWS]))
F(defs, "public static final String[] SAP_WOODS = %s;" % jstr(SAP_WOODS))
F(defs, "public static final String[] SEED_CROPS = %s;" % jstr(SEED_CROPS))
F(defs, "public static final String[] BAR_METALS = %s;" % jstr(BAR_METALS))
F(defs, "public static final long[] CUM = %s;" % jlong(CUM))
M(defs, r"""
public static boolean soon(int i) {
  return i >= 0 && i < N && KIND[i] == @K_SOON@;
}""")
M(defs, r"""
public static int tree(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.length() == 0) return -1;
  for (int i = 0; i < NT; i++) if (TREES[i].toLowerCase().equals(t)) return i;
  if (t.length() >= 3) {
    for (int i = 0; i < NT; i++) if (TREES[i].toLowerCase().startsWith(t)) return i;
  }
  return -1;
}""")
# "Mining.MSpeed" -> node index (tree * 12 + slot - 1), -1 when unknown
M(defs, r"""
public static int idx(String key) {
  if (key == null) return -1;
  int dot = key.indexOf('.');
  if (dot <= 0) return -1;
  int t = -1;
  String tn = key.substring(0, dot).trim();
  for (int i = 0; i < NT; i++) if (TREES[i].equalsIgnoreCase(tn)) t = i;
  if (t < 0) return -1;
  String id = key.substring(dot + 1).trim();
  for (int s = 0; s < 12; s++) if (ID[t * 12 + s].equalsIgnoreCase(id)) return t * 12 + s;
  return -1;
}""")
M(defs, r"""
public static String roman(int k) {
  if (k == 1) return "I";
  if (k == 2) return "II";
  if (k == 3) return "III";
  if (k == 4) return "IV";
  if (k == 5) return "V";
  if (k == 6) return "VI";
  return String.valueOf(k);
}""")
# compact number for button texts (no commas: inline text is sanitized): 950, 12.3k, 1.25m, 3.10b
M(defs, r"""
public static String fmt(long n) {
  if (n < 0L) return "-" + fmt(n == Long.MIN_VALUE ? Long.MAX_VALUE : -n);
  if (n < 10000L) return String.valueOf(n);
  if (n < 1000000L) { long t = n / 100L; return (t / 10L) + "." + (t % 10L) + "k"; }
  if (n < 1000000000L) { long h = n / 10000L; return (h / 100L) + "." + ((h % 100L) < 10L ? "0" : "") + (h % 100L) + "m"; }
  long g = n / 10000000L;
  return (g / 100L) + "." + ((g % 100L) < 10L ? "0" : "") + (g % 100L) + "b";
}""")
# grouped number for labels set through b.set (any character is safe there): 1,234,567
M(defs, r"""
public static String grp(long n) {
  boolean neg = n < 0L;
  String s = String.valueOf(neg ? (n == Long.MIN_VALUE ? Long.MAX_VALUE : -n) : n);
  StringBuilder sb = new StringBuilder();
  int len = s.length();
  for (int i = 0; i < len; i++) {
    if (i > 0 && (len - i) % 3 == 0) sb.append(',');
    sb.append(s.charAt(i));
  }
  return (neg ? "-" : "") + sb.toString();
}""")
# at most 3 decimals, trailing zeros cut, no Locale (SkyySkills StatsPage.num)
M(defs, r"""
public static String num(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = -t;
  long w = t / 1000L;
  long f = t % 1000L;
  if (f == 0L) return sign + w;
  String fs = String.valueOf(f + 1000L).substring(1);
  while (fs.endsWith("0")) fs = fs.substring(0, fs.length() - 1);
  return sign + w + "." + fs;
}""")
M(defs, r"""
public static String pct(double f) {
  return num(f * 100.0) + "%";
}""")
M(defs, r"""
public static String valueText(int i, double v) {
  int k = KIND[i];
  if (k == @K_HP@ || k == @K_STA@ || k == @K_RJMP@) return num(v);
  if (k == @K_VEIN@ || k == @K_FELLER@) return String.valueOf(Math.round(v));
  if (k == @K_DJUMP@) return pct(v);
  if (k == @K_SWING@) { long p = Math.round(v * 100.0); return p + "%" + (p >= 40L ? " (max)" : ""); }
  return pct(v);
}""")
M(defs, r"""
public static boolean inList(String[] xs, String v) {
  if (xs == null || v == null) return false;
  for (int i = 0; i < xs.length; i++) if (xs[i].equalsIgnoreCase(v)) return true;
  return false;
}""")
# crop family id (BlockType.getItem().getId(): Plant_Crop_Wheat_Block, ..._Block_Eternal) -> "Wheat"
M(defs, r"""
public static String cropOf(String fam) {
  if (fam == null || !fam.startsWith("Plant_Crop_")) return null;
  String r = fam.substring(11);
  int b = r.indexOf("_Block");
  if (b > 0) r = r.substring(0, b);
  return r.length() == 0 ? null : r;
}""")
M(defs, r"""
public static String seedsOf(String crop) {
  if (crop == null) return null;
  for (int i = 0; i < SEED_CROPS.length; i++) if (SEED_CROPS[i].equals(crop)) return "Plant_Seeds_" + crop;
  return null;
}""")
M(defs, r"""
public static String woodOf(String id) {
  if (id == null || !id.startsWith("Wood_")) return null;
  int t = id.indexOf("_Trunk");
  if (t <= 5) return null;
  return id.substring(5, t);
}""")
M(defs, r"""
public static String saplingOf(String id) {
  String w = woodOf(id);
  if (w == null) return null;
  for (int i = 0; i < SAP_WOODS.length; i++) if (SAP_WOODS[i].equals(w)) return "Plant_Sapling_" + w;
  return null;
}""")
# Wood_Oak_Trunk_Full -> "Wood_Oak_Trunk" (Tree Feller family)
M(defs, r"""
public static String logFamily(String id) {
  if (id == null) return null;
  int t = id.indexOf("_Trunk");
  return t > 0 ? id.substring(0, t + 6) : null;
}""")
# 0.2.1 review: a block of the Tree Feller family fam (logFamily) = ONLY the natural shapes Wood_<W>_Trunk / Wood_<W>_Trunk_Full, with
# or without a block state ("*Wood_Oak_Trunk_State_Stripped"); never Trunk_Half / Trunk_Stairs / *_Deco (crafted building shapes - no
# tree prefab in Assets.zip uses them: 1126 Server/Prefabs/Trees files hold only Trunk + Trunk_Full, checked 2026-09-24)
M(defs, r"""
public static boolean isLog(String id, String fam) {
  if (id == null || fam == null || id.length() == 0 || fam.length() == 0) return false;
  String b = id.startsWith("*") ? id.substring(1) : id;
  int s = b.indexOf("_State_");
  if (s > 0) b = b.substring(0, s);
  return b.equals(fam) || b.equals(fam + "_Full");
}""")
# Ore_Iron_Stone -> Ingredient_Bar_Iron
M(defs, r"""
public static String barOf(String id) {
  if (id == null || !id.startsWith("Ore_")) return null;
  String r = id.substring(4);
  int u = r.indexOf('_');
  if (u <= 0) return null;
  String m = r.substring(0, u);
  for (int i = 0; i < BAR_METALS.length; i++) if (BAR_METALS[i].equals(m)) return "Ingredient_Bar_" + m;
  return null;
}""")
M(defs, r"""
public static String label(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Rock_Gem_")) s = s.substring(9);
  else if (s.startsWith("Ingredient_Bar_")) s = s.substring(15) + " Bar";
  else if (s.startsWith("Plant_Sapling_")) s = s.substring(14) + " Sapling";
  else if (s.startsWith("Plant_Seeds_")) s = s.substring(12) + " Seeds";
  else if (s.startsWith("Ingredient_")) s = s.substring(11);
  return s.replace('_', ' ');
}""")
M(defs, r"""
public static String bid(@BTY@ bt) {
  if (bt == null) return "";
  String id = null;
  try { id = bt.getId(); } catch (Throwable t) { }
  if (id == null) return "";
  if (id.startsWith("*")) id = id.substring(1);
  return id;
}""")
# the block's item id (state variants share it; growth-stage crops -> Plant_Crop_<C>_Block) - SkyySkills SkillCfg.familyId
M(defs, r"""
public static String family(@BTY@ bt) {
  if (bt == null) return null;
  try {
    @ITM@ it = bt.getItem();
    if (it != null) { String iid = it.getId(); if (iid != null && iid.length() > 0) return iid; }
  } catch (Throwable t) { }
  String id = bid(bt);
  int s = id.indexOf("_State_");
  if (s > 0) id = id.substring(0, s);
  return id;
}""")
M(defs, r"""
public static String gatherType(@BTY@ bt) {
  try {
    @BGA@ g = bt.getGathering();
    if (g == null) return null;
    @BBD@ br = g.getBreaking();
    return br == null ? null : br.getGatherType();
  } catch (Throwable t) { return null; }
}""")

# ================= TreeCfg: trees.properties =================
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static @LOG@ LOG;")
F(cfg, "public static final String DEFAULTS = " + json.dumps(DEFAULTS) + ";")
F(cfg, "public static final String ADD02 = " + json.dumps(ADD02) + ";")
F(cfg, "public static final String ADD021DJ = " + json.dumps(ADD021DJ) + ";")
F(cfg, "public static final String ADD021FEL = " + json.dumps(ADD021FEL) + ";")
F(cfg, "public static final String ADD023 = " + json.dumps(ADD023) + ";")
for decl in ("int[] TIER_LV = new int[] { 1, 10, 20, 30, 45, 60 }", "int TOK_FIRST = 1", "int TOK_EVERY = 5", "long XP_PER_DUST = 10L",
             "long RESPEC_CD_MS = 600000L", "long RESPEC_COINS = 0L", "String[] OFF_WORLDS = new String[0]", "int RADIUS = 6",
             "int FELLER_H = 32", "long VEIN_CD_MS = 40000L", "long FELLER_CD_MS = 3000L", "boolean FELLER_LEAVES = true",
             "int FELLER_ALL = 64", "boolean FELLED_NODES = true", "boolean SWING_ON = true",
             "long FEEDBACK_MS = 2000L", "long EXTRA_TOKENS = 0L", "long EXTRA_DUST = 0L",
             "long[] XP_T = " + jlong([DUST_DEF.get(t, 10) for t in TREES]),
             "int[] MAX = @PKG@.TreeDefs.D_MAX", "double[] PER = @PKG@.TreeDefs.D_PER", "long[] B = @PKG@.TreeDefs.D_B",
             "double[] BASE = @PKG@.TreeDefs.D_BASE", "int[] TOK = @PKG@.TreeDefs.D_TOK", "boolean[] EN = new boolean[] { " + ", ".join("false" if KINDS[r["kind"]] == "SOON" else "true" for r in ROWS) + " }",
             "Object[] LIST = new Object[%d]" % len(ROWS)):
    F(cfg, "public static volatile %s;" % decl)
M(cfg, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyTrees] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyTrees] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static String str(java.util.Properties p, String k, String d) {
  String v = p.getProperty(k);
  return v == null ? d : v.trim();
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static double dbl(java.util.Properties p, String k, double d) {
  try {
    String v = p.getProperty(k);
    if (v == null) return d;
    double x = Double.parseDouble(v.trim());
    return (Double.isNaN(x) || Double.isInfinite(x)) ? d : x;
  } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""")
M(cfg, r"""
public static long clampL(long v, long lo, long hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}""")
M(cfg, r"""
public static double clampD(double v, double lo, double hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}""")
M(cfg, r"""
public static String[] split(String v) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (v != null) {
    String[] xs = v.split(",");
    for (int i = 0; i < xs.length; i++) { String x = xs[i].trim(); if (x.length() > 0) out.add(x); }
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(cfg, r"""
public static int[] tiers(String v) {
  int[] def = new int[] { 1, 10, 20, 30, 45, 60 };
  String[] xs = split(v);
  if (xs.length != 6) { warn("tier.levels needs 6 numbers - using 1,10,20,30,45,60"); return def; }
  int[] r = new int[6];
  try {
    for (int i = 0; i < 6; i++) {
      r[i] = Integer.parseInt(xs[i]);
      if (r[i] < 0 || r[i] > 1000 || (i > 0 && r[i] < r[i - 1])) { warn("tier.levels must rise from 0 to 1000 - using 1,10,20,30,45,60"); return def; }
    }
  } catch (Throwable t) { warn("tier.levels is not 6 numbers - using 1,10,20,30,45,60"); return def; }
  return r;
}""")
M(cfg, r"""
public static long rate(int t) {
  long[] xt = XP_T;
  if (t >= 0 && t < xt.length && xt[t] > 0L) return xt[t];
  return XP_PER_DUST < 1L ? 1L : XP_PER_DUST;
}""")
M(cfg, r"""
public static boolean has02(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("dust.xpPerDust.") || k.startsWith("Acrobatics.") || k.startsWith("Exploration.")) return true;
  }
  return false;
}""")
M(cfg, r"""
public static void apply(java.util.Properties p) {
  TIER_LV = tiers(str(p, "tier.levels", "1,10,20,30,45,60"));
  TOK_FIRST = (int) clampL(lng(p, "tokens.first", 1L), 0L, 100L);
  TOK_EVERY = (int) clampL(lng(p, "tokens.every", 5L), 1L, 100L);
  XP_PER_DUST = clampL(lng(p, "dust.xpPerDust", 10L), 1L, 1000000000L);
  long[] xt = new long[@PKG@.TreeDefs.NT];
  for (int tt = 0; tt < xt.length; tt++) {
    long dd = @PKG@.TreeDefs.D_DUST[tt] > 0L ? @PKG@.TreeDefs.D_DUST[tt] : XP_PER_DUST;
    xt[tt] = clampL(lng(p, "dust.xpPerDust." + @PKG@.TreeDefs.TREES[tt], dd), 1L, 1000000000L);
  }
  XP_T = xt;
  RESPEC_CD_MS = clampL(lng(p, "respec.cooldownMinutes", 10L), 0L, 100000L) * 60000L;
  RESPEC_COINS = clampL(lng(p, "respec.coins", 0L), 0L, 1000000000000L);
  OFF_WORLDS = split(str(p, "ability.disabledWorlds", ""));
  RADIUS = (int) clampL(lng(p, "ability.maxRadius", 6L), 1L, 16L);
  FELLER_H = (int) clampL(lng(p, "feller.maxHeight", 32L), 1L, 64L);
  VEIN_CD_MS = clampL(lng(p, "vein.cooldownSec", 40L), 0L, 86400L) * 1000L;
  FELLER_CD_MS = clampL(lng(p, "feller.cooldownSec", 3L), 0L, 86400L) * 1000L;
  FELLER_LEAVES = bool(p, "feller.needLeaves", true);
  FELLER_ALL = (int) clampL(lng(p, "feller.maxPerLayer", 64L), 1L, 256L);
  FELLED_NODES = bool(p, "felled.nodes", true);
  SWING_ON = bool(p, "swing.enabled", true);
  FEEDBACK_MS = clampL(lng(p, "feedbackMs", 2000L), 500L, 600000L);
  EXTRA_TOKENS = clampL(lng(p, "debug.extraTokens", 0L), 0L, 1000L);
  EXTRA_DUST = clampL(lng(p, "debug.extraDust", 0L), 0L, 1000000000000000L);
  int n = @PKG@.TreeDefs.N;
  int[] mx = new int[n];
  double[] pe = new double[n];
  long[] bb = new long[n];
  double[] ba = new double[n];
  int[] tk = new int[n];
  boolean[] en = new boolean[n];
  Object[] li = new Object[n];
  for (int i = 0; i < n; i++) {
    String k = @PKG@.TreeDefs.TREES[i / 12] + "." + @PKG@.TreeDefs.ID[i] + ".";
    mx[i] = (int) clampL(lng(p, k + "max", (long) @PKG@.TreeDefs.D_MAX[i]), 1L, 100L);
    pe[i] = clampD(dbl(p, k + "per", @PKG@.TreeDefs.D_PER[i]), 0.0, 1000.0);
    bb[i] = clampL(lng(p, k + "B", @PKG@.TreeDefs.D_B[i]), 0L, 1000000000L);
    ba[i] = clampD(dbl(p, k + "base", @PKG@.TreeDefs.D_BASE[i]), 0.0, 1000.0);
    tk[i] = (int) clampL(lng(p, k + "tokens", (long) @PKG@.TreeDefs.D_TOK[i]), 0L, 100L);
    en[i] = !@PKG@.TreeDefs.soon(i) && bool(p, k + "enabled", true);
    String lk = @PKG@.TreeDefs.LISTKEY[i];
    if (lk.length() > 0) li[i] = split(str(p, k + lk, @PKG@.TreeDefs.D_LIST[i]));
  }
  MAX = mx; PER = pe; B = bb; BASE = ba; TOK = tk; EN = en; LIST = li;
}""")
M(cfg, r"""
public static void writeAtomic(byte[] data) throws java.io.IOException {
  java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, data, new java.nio.file.OpenOption[0]);
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable x) { }
  throw last;
}""")
M(cfg, r"""
public static boolean hasPrefix(java.util.Properties p, String pre) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(pre)) return true;
  }
  return false;
}""")
# one "key=value" line whose key AND value text equal (key, old) -> "key=neu" (its \r kept); anything else (comments, other keys,
# custom values, other separators) -> null = untouched
M(cfg, r"""
public static String migrateLine(String ln, String key, String old, String neu) {
  String body = ln;
  String cr = "";
  if (body.endsWith("\r")) { body = body.substring(0, body.length() - 1); cr = "\r"; }
  String tb = body.trim();
  if (tb.length() == 0 || tb.charAt(0) == '#' || tb.charAt(0) == '!') return null;
  int eq = body.indexOf('=');
  if (eq <= 0) return null;
  if (!body.substring(0, eq).trim().equals(key)) return null;
  if (!body.substring(eq + 1).trim().equals(old)) return null;
  return key + "=" + neu + cr;
}""")
# 0.2.1 Tree Feller rework: the unchanged 0.1 / 0.2 default lines only (n[0] = lines changed)
M(cfg, r"""
public static String migrateFeller(String text, int[] n) {
  String[] ls = text.split("\n", -1);
  StringBuilder sb = new StringBuilder(text.length() + 16);
  for (int i = 0; i < ls.length; i++) {
    String ln = ls[i];
    String r = migrateLine(ln, "Foraging.FFeller.per", "8.0", "1.0");
    if (r == null) r = migrateLine(ln, "Foraging.FFeller.base", "8.0", "0.0");
    if (r == null) r = migrateLine(ln, "feller.cooldownSec", "30", "3");
    if (r != null) { ln = r; n[0] = n[0] + 1; }
    if (i > 0) sb.append('\n');
    sb.append(ln);
  }
  return sb.toString();
}""")
# 0.2.3 swing speed: the untouched old default lines Mining.MSpeed.per=0.02 / Foraging.FSpeed.per=0.02 -> 0.01 (n[0] = lines changed);
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
# ONE atomic write for everything an older trees.properties is missing: the 0.2 block (a 0.1 file; it already carries the Double Jump
# lines), the Double Jump block (a 0.2 file), the Tree Feller migration + block (any file without feller.maxPerLayer), the 0.2.3 swing
# migration + block (any file without swing.enabled - research/Swing-Speed-Spec.md 4.2). The returned
# settings are parsed from exactly the new content (ISO-8859-1 = what Properties.load(InputStream) reads), so a failed write still runs
# with the migrated numbers and the next load simply tries again.
M(cfg, r"""
public static java.util.Properties upgrade(java.util.Properties p) {
  boolean need02 = !has02(p);
  boolean needDj = !need02 && !hasPrefix(p, "Acrobatics.RDouble.");
  boolean needFel = p.getProperty("feller.maxPerLayer") == null;
  boolean need023 = p.getProperty("swing.enabled") == null;
  if (!need02 && !needDj && !needFel && !need023) return p;
  java.util.Properties q = p;
  try {
    byte[] old = java.nio.file.Files.readAllBytes(FILE);
    String text = new String(old, "ISO-8859-1");
    int[] n = new int[1];
    if (needFel) text = migrateFeller(text, n);
    int[] n2 = new int[1];
    if (need023) text = migrateSwing(text, n2);
    StringBuilder sb = new StringBuilder(text);
    if (need02) sb.append("\n").append(ADD02);
    if (needDj) sb.append("\n").append(ADD021DJ);
    if (needFel) sb.append("\n").append(ADD021FEL);
    if (need023) sb.append("\n").append(ADD023);
    byte[] data = sb.toString().getBytes("ISO-8859-1");
    java.util.Properties np = new java.util.Properties();
    np.load(new java.io.ByteArrayInputStream(data));
    q = np;
    try {
      writeAtomic(data);
      info("updated " + FILE + " for SkyyTrees 0.2.3:" + (need02 ? " added the 0.2 lines (Acrobatics and Exploration trees, per-tree Dust rates);" : "") + (needDj ? " added the Double Jump lines;" : "") + (needFel ? " Tree Feller rework (" + n[0] + " old default line(s) changed, feller.maxPerLayer added);" : "") + (need023 ? " swing speed (" + n2[0] + " old default Mining Speed / Chopping Speed line(s) changed to per=0.01, swing.enabled added)" : ""));
    } catch (Throwable t2) { warn("could not update trees.properties (the new values apply anyway, the next load tries again): " + t2); }
  } catch (Throwable t) {
    warn("could not read trees.properties for the update (the old default values are migrated in memory only): " + t);
    q = new java.util.Properties();
    q.putAll(p);
    if (needFel) {
      if ("8.0".equals(str(q, "Foraging.FFeller.per", ""))) q.setProperty("Foraging.FFeller.per", "1.0");
      if ("8.0".equals(str(q, "Foraging.FFeller.base", ""))) q.setProperty("Foraging.FFeller.base", "0.0");
      if ("30".equals(str(q, "feller.cooldownSec", ""))) q.setProperty("feller.cooldownSec", "3");
    }
    if (need023) {
      if ("0.02".equals(str(q, "Mining.MSpeed.per", ""))) q.setProperty("Mining.MSpeed.per", "0.01");
      if ("0.02".equals(str(q, "Foraging.FSpeed.per", ""))) q.setProperty("Foraging.FSpeed.per", "0.01");
    }
  }
  if (needFel) {
    String pe = str(q, "Foraging.FFeller.per", "1.0");
    String ba = str(q, "Foraging.FFeller.base", "0.0");
    if (!"1.0".equals(pe) || !"0.0".equals(ba)) warn("Tree Feller custom numbers kept (Foraging.FFeller.per=" + pe + ", base=" + ba + "): since 0.2.1 they count logs on the SAME level as the cut (default per=1.0 base=0.0 = 1, 2, 3, 4 logs; the max level breaks the whole layer)");
  }
  if (needDj && hasPrefix(q, "Acrobatics.RDodge.")) info("Acrobatics.RDodge.* lines in trees.properties are unused since 0.2.1 (Quick Dodge became Double Jump) - you can delete them");
  if (need023) {
    String mp = q.getProperty("Mining.MSpeed.per");
    String fp = q.getProperty("Foraging.FSpeed.per");
    if (mp != null && !"0.01".equals(mp.trim())) warn("Mining.MSpeed.per=" + mp.trim() + " kept - since 0.2.3 it is pickaxe swing speed per level (0.01 = 1%, capped at +40%)");
    if (fp != null && !"0.01".equals(fp.trim())) warn("Foraging.FSpeed.per=" + fp.trim() + " kept - since 0.2.3 it is hatchet swing speed per level (0.01 = 1%, capped at +40%)");
  }
  return q;
}""")
M(cfg, r"""
public static synchronized String load() {
  java.util.Properties p = new java.util.Properties();
  boolean loaded = false;
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      writeAtomic(DEFAULTS.getBytes("UTF-8"));
      info("wrote default " + FILE);
    }
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    loaded = true;
  } catch (Throwable t) { warn("could not read trees.properties (built-in defaults used): " + t); }
  if (loaded) p = upgrade(p);
  apply(p);
  int on = 0;
  for (int i = 0; i < EN.length; i++) if (EN[i] && !@PKG@.TreeDefs.soon(i)) on++;
  int[] tl = TIER_LV;
  StringBuilder rt = new StringBuilder();
  for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {
    if (rate(tt) == XP_PER_DUST) continue;
    rt.append(rt.length() == 0 ? " (" : ", ").append(@PKG@.TreeDefs.TREES[tt]).append(' ').append(rate(tt));
  }
  if (rt.length() > 0) rt.append(')');
  return on + " of " + (@PKG@.TreeDefs.N - @PKG@.TreeDefs.SOON_N) + " nodes on (" + @PKG@.TreeDefs.SOON_N + " coming later), tiers " + tl[0] + "/" + tl[1] + "/" + tl[2] + "/" + tl[3] + "/" + tl[4] + "/" + tl[5] + ", 1 Dust per " + XP_PER_DUST + " XP" + rt.toString() + (SWING_ON ? "" : ", tool swing speed OFF") + (EXTRA_TOKENS > 0L || EXTRA_DUST > 0L ? " (DEBUG extra tokens/Dust on)" : "");
}""")

# ================= TreeData: one profile's tree state =================
F(dat, "public int[] lv = new int[%d];" % len(ROWS))
F(dat, "public boolean[] off = new boolean[%d];" % len(ROWS))
F(dat, "public long[] respecAt = new long[%d];" % len(TREES))
F(dat, "public boolean quiet;")
F(dat, "public boolean noteSwing;")   # 0.2.3: the one-time swing-speed chat notice was shown for this profile (file key note.swing=1)
F(dat, "public boolean bad;")
F(dat, "public String name;")
C(dat, "public TreeData() { }")

# ================= TreeStore: per-profile files (PROFILES-CONTRACT), bridge =================
F(sto, "public static java.nio.file.Path DIR;")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final Object IO = new Object();")
F(sto, "public static Object FN;")
F(sto, "public static Object BFN;")
M(sto, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# the contract's helper, verbatim (tools/PROFILES-CONTRACT.md)
M(sto, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(sto, r"""
public static boolean busy(java.util.UUID u) {
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
M(sto, r"""
public static java.util.Properties readProps(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""")
# NIO read under the IO lock: on Windows an open handle makes the ATOMIC_MOVE of a save fail (SkyySkills 0.3.2 finding)
M(sto, r"""
public static java.util.Properties readLocked(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p;
  synchronized (IO) { p = readProps(f); }
  return p;
}""")
M(sto, r"""
public static @PKG@.TreeData readFile(String k) {
  @PKG@.TreeData d = new @PKG@.TreeData();
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return d;
    java.util.Properties p = readLocked(f);
    for (int i = 0; i < @PKG@.TreeDefs.N; i++) {
      String v = p.getProperty(@PKG@.TreeDefs.TREES[i / 12] + "." + @PKG@.TreeDefs.ID[i]);
      if (v == null) continue;
      try { int x = Integer.parseInt(v.trim()); d.lv[i] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t) { }
    }
    // 0.2.1: Acrobatics slot 5 was RDodge (Quick Dodge) in 0.2 - same slot = same Token and Dust cost; an RDouble line always wins
    if (p.getProperty("Acrobatics.RDouble") == null) {
      String ov = p.getProperty("Acrobatics.RDodge");
      if (ov != null) { try { int x = Integer.parseInt(ov.trim()); d.lv[@I_RDOUBLE@] = x < 0 ? 0 : (x > 1000 ? 1000 : x); } catch (Throwable t3) { } }
    }
    for (int tt = 0; tt < @PKG@.TreeDefs.NT; tt++) {
      String tn = @PKG@.TreeDefs.TREES[tt];
      String o = p.getProperty(tn + ".off");
      if (o != null) {
        String[] xs = o.split(",");
        for (int j = 0; j < xs.length; j++) {
          int i = @PKG@.TreeDefs.idx(tn + "." + xs[j].trim());
          if (i < 0 && "Acrobatics".equals(tn) && "RDodge".equalsIgnoreCase(xs[j].trim())) i = @I_RDOUBLE@;
          if (i >= 0) d.off[i] = true;
        }
      }
      try { String r = p.getProperty(tn + ".respecAt"); if (r != null) d.respecAt[tt] = Long.parseLong(r.trim()); } catch (Throwable t2) { }
    }
    d.quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
    d.noteSwing = "1".equals(String.valueOf(p.getProperty("note.swing")).trim());
    String nm = p.getProperty("name");
    if (nm != null && nm.trim().length() > 0) d.name = nm.trim();
  } catch (Throwable t) {
    d = new @PKG@.TreeData();
    d.bad = true;
    @PKG@.TreeCfg.warn("could not read tree file " + k + ".properties - it is NOT overwritten; fix or delete it, then run /tree reload: " + t);
  }
  return d;
}""")
M(sto, r"""
public static synchronized @PKG@.TreeData install(String k, java.util.UUID u, @PKG@.TreeData d) {
  @PKG@.TreeData cur = (@PKG@.TreeData) DATA.get(k);
  if (cur != null) return cur;
  OWNER.put(k, u);
  DATA.put(k, d);
  return d;
}""")
M(sto, r"""
public static @PKG@.TreeData dataK(String k, java.util.UUID u) {
  @PKG@.TreeData d = (@PKG@.TreeData) DATA.get(k);
  if (d != null) return d;
  return install(k, u, readFile(k));
}""")
M(sto, r"""
public static @PKG@.TreeData data(java.util.UUID u) {
  return dataK(pkey(u), u);
}""")
M(sto, r"""
public static synchronized java.util.Properties snap(String k) {
  @PKG@.TreeData d = (@PKG@.TreeData) DATA.get(k);
  if (d == null || d.bad) return null;
  java.util.Properties p = new java.util.Properties();
  if (d.name != null) p.setProperty("name", d.name);
  p.setProperty("v", "1");
  p.setProperty("quiet", d.quiet ? "true" : "false");
  if (d.noteSwing) p.setProperty("note.swing", "1");
  for (int t = 0; t < @PKG@.TreeDefs.NT; t++) {
    String tn = @PKG@.TreeDefs.TREES[t];
    StringBuilder off = new StringBuilder();
    for (int s = 0; s < 12; s++) {
      int i = t * 12 + s;
      if (d.lv[i] > 0) p.setProperty(tn + "." + @PKG@.TreeDefs.ID[i], String.valueOf(d.lv[i]));
      if (d.off[i] && d.lv[i] > 0) { if (off.length() > 0) off.append(','); off.append(@PKG@.TreeDefs.ID[i]); }
    }
    if (off.length() > 0) p.setProperty(tn + ".off", off.toString());
    if (d.respecAt[t] > 0L) p.setProperty(tn + ".respecAt", String.valueOf(d.respecAt[t]));
  }
  return p;
}""")
M(sto, r"""
public static void moveRetry(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(sto, r"""
public static boolean saveNow(String k) {
  try {
    java.util.Properties p = snap(k);
    if (p == null) return true;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyTrees - node levels of one profile (Tokens and Dust are computed from your skills, never stored)"); } finally { out.close(); }
    moveRetry(tmp, DIR.resolve(k + ".properties"));
    return true;
  } catch (Throwable t) {
    @PKG@.TreeCfg.warn("could not save trees for " + k + " (kept dirty, retried on the next save): " + t);
    return false;
  }
}""")
M(sto, r"""
public static boolean save(String k) {
  boolean r;
  synchronized (IO) { r = saveNow(k); }
  return r;
}""")
M(sto, r"""
public static void dirty(String k) {
  DIRTY.put(k, Boolean.TRUE);
}""")
M(sto, r"""
public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    it.remove();
    if (!save(k)) failed.add(k);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""")
M(sto, r"""
public static synchronized void setLevel(@PKG@.TreeData d, int i, int v) {
  d.lv[i] = v;
  if (v <= 0) d.off[i] = false;
}""")
M(sto, r"""
public static synchronized boolean flipOff(@PKG@.TreeData d, int i) {
  d.off[i] = !d.off[i];
  return d.off[i];
}""")
M(sto, r"""
public static synchronized void clearTree(@PKG@.TreeData d, int t, long now) {
  for (int s = 0; s < 12; s++) { d.lv[t * 12 + s] = 0; d.off[t * 12 + s] = false; }
  d.respecAt[t] = now;
}""")
M(sto, r"""
public static synchronized boolean flipQuiet(@PKG@.TreeData d) {
  d.quiet = !d.quiet;
  return d.quiet;
}""")
M(sto, r"""
public static synchronized void setName(@PKG@.TreeData d, String n) {
  if (n != null && n.length() > 0) d.name = n;
}""")
# 0.2.3: true once per profile (the caller then marks the file dirty and, from the tick, sends the notice)
M(sto, r"""
public static synchronized boolean setNote(@PKG@.TreeData d) {
  if (d.noteSwing) return false;
  d.noteSwing = true;
  return true;
}""")
# drop cached files of offline players that have nothing waiting to be saved (offline players cannot change their trees)
M(sto, r"""
public static void retain() {
  java.util.Iterator it = DATA.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    Object o = OWNER.get(k);
    if (!(o instanceof java.util.UUID) || DIRTY.containsKey(k)) continue;
    if (@UNI@.get().getPlayer((java.util.UUID) o) != null) continue;
    it.remove();
    OWNER.remove(k);
  }
}""")
# /tree reload: forget cached files that could not be read, so the fixed file is read again on next use (good files stay cached)
M(sto, r"""
public static int dropBad() {
  int n = 0;
  java.util.Iterator it = DATA.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (((@PKG@.TreeData) e.getValue()).bad) { it.remove(); n++; }
  }
  return n;
}""")
# SaveTask: write one profile file soon, on the scheduler (never on a world thread)
stk.addInterface(pool.get("java.lang.Runnable"))
F(stk, "public String key;")
C(stk, "public SaveTask(String k) { this.key = k; }")
M(stk, r"""
public void run() {
  try {
    @PKG@.TreeStore.DIRTY.remove(this.key);
    if (!@PKG@.TreeStore.save(this.key)) @PKG@.TreeStore.dirty(this.key);
  } catch (Throwable t) { @PKG@.TreeStore.dirty(this.key); }
}""")
M(sto, r"""
public static void saveSoon(String k) {
  dirty(k);
  try { @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.SaveTask(k)); } catch (Throwable t) { }
}""")
# 0.2.2 player Settings registry (SkyyMenu 0.2+, research/Settings-Spec.md 1.3 + 3.2). No SkyyMenu = no answer = 0.2.1 behaviour:
# trees.bonus follows the per-profile quiet flag, trees.abilities is on. moveQuiet = the one-shot move of an old /tree quiet=true into the
# per-player switch (onlyIfUnset); it may read a player file, and every caller runs on a world thread (flush, vein, feller, /tree quiet).
M(sto, r"""
public static synchronized boolean clearQuiet(@PKG@.TreeData d) {
  if (!d.quiet) return false;
  d.quiet = false;
  return true;
}""")
M(sto, r"""
public static void moveQuiet(java.util.UUID u) {
  String k = pkey(u);
  @PKG@.TreeData d = dataK(k, u);
  if (d == null || !d.quiet || d.bad) return;
  Object f = bridge().get("settings:fn:set");
  if (!(f instanceof java.util.function.Function)) return;
  if (!Boolean.TRUE.equals(((java.util.function.Function) f).apply(new Object[] { u, "trees.bonus", Boolean.FALSE, Boolean.TRUE }))) return;
  if (clearQuiet(d)) dirty(k);
}""")
M(sto, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      if ("trees.bonus".equals(key)) moveQuiet(u);
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  if ("trees.bonus".equals(key)) return !data(u).quiet;
  return true;
}""")
M(sto, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyTrees", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")

# ================= TreeCalc: levels, Tokens, Dust, costs, states =================
M(calc, r"""
public static java.util.function.Function fn(String key) {
  try {
    Object o = @PKG@.TreeStore.bridge().get(key);
    if (o instanceof java.util.function.Function) return (java.util.function.Function) o;
  } catch (Throwable t) { }
  return null;
}""")
M(calc, r"""
public static boolean hasSkills() {
  return fn("skill:fn:level") != null;
}""")
M(calc, r"""
public static boolean hasXp() {
  return fn("skill:fn:xp") != null;
}""")
# 0.2: does the running SkyySkills know this skill? skill:<uuid> = "Mining:12,...,Exploration:3,..." (SkyySkills 0.4.1 adds Exploration).
# Unknown (nothing published yet) counts as yes, so the page never claims a missing skill it cannot see.
M(calc, r"""
public static boolean skillKnown(java.util.UUID u, int t) {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:" + u.toString());
    if (!(o instanceof String)) return true;
    return ("," + (String) o).indexOf("," + @PKG@.TreeDefs.TREES[t] + ":") >= 0;
  } catch (Throwable e) { return true; }
}""")
# -1 = SkyySkills not loaded; else the active profile's level of that skill (0 for a skill SkyySkills does not know yet)
M(calc, r"""
public static int level(java.util.UUID u, int t) {
  java.util.function.Function f = fn("skill:fn:level");
  if (f == null) return -1;
  try {
    Object r = f.apply(new Object[] { u, @PKG@.TreeDefs.TREES[t] });
    if (r instanceof Number) { int l = ((Number) r).intValue(); return l < 0 ? 0 : l; }
  } catch (Throwable e) { }
  return 0;
}""")
# total XP of that skill (skill:fn:xp, SkyySkills 0.4); without it: the XP at the start of the level (default table) = an estimate
M(calc, r"""
public static long xp(java.util.UUID u, int t, int lvl) {
  java.util.function.Function f = fn("skill:fn:xp");
  if (f != null) {
    try {
      Object r = f.apply(new Object[] { u, @PKG@.TreeDefs.TREES[t] });
      if (r instanceof Number) { long x = ((Number) r).longValue(); return x < 0L ? 0L : x; }
    } catch (Throwable e) { }
    return 0L;
  }
  if (lvl <= 0) return 0L;
  int l = lvl;
  if (l > @PKG@.TreeDefs.CUM.length - 1) l = @PKG@.TreeDefs.CUM.length - 1;
  return @PKG@.TreeDefs.CUM[l];
}""")
M(calc, r"""
public static long tokensEarned(int lvl) {
  long x = @PKG@.TreeCfg.EXTRA_TOKENS;
  if (lvl < 1) return x;
  return x + (long) @PKG@.TreeCfg.TOK_FIRST + (long) (lvl / @PKG@.TreeCfg.TOK_EVERY);
}""")
M(calc, r"""
public static long dustEarned(int t, long xp) {
  return xp / @PKG@.TreeCfg.rate(t) + @PKG@.TreeCfg.EXTRA_DUST;
}""")
# effective level: 0 when the node is turned off by the player or disabled in trees.properties; capped at max
M(calc, r"""
public static int eff(@PKG@.TreeData d, int i) {
  if (d == null || i < 0 || i >= @PKG@.TreeDefs.N) return 0;
  if (!@PKG@.TreeCfg.EN[i] || d.off[i]) return 0;
  int l = d.lv[i];
  int m = @PKG@.TreeCfg.MAX[i];
  return l > m ? m : l;
}""")
# Dust to go from level lv to lv + 1 = B x lv^3
M(calc, r"""
public static long cost(int i, int lv) {
  if (lv < 1) return 0L;
  long n = (long) lv;
  return @PKG@.TreeCfg.B[i] * n * n * n;
}""")
M(calc, r"""
public static long tokSpent(@PKG@.TreeData d, int t) {
  long s = 0L;
  for (int k = 0; k < 12; k++) { int i = t * 12 + k; if (d.lv[i] >= 1 && !@PKG@.TreeDefs.soon(i)) s = s + (long) @PKG@.TreeCfg.TOK[i]; }
  return s;
}""")
M(calc, r"""
public static long dustSpent(@PKG@.TreeData d, int t) {
  long s = 0L;
  for (int k = 0; k < 12; k++) {
    int i = t * 12 + k;
    if (@PKG@.TreeDefs.soon(i)) continue;
    for (int n = 1; n < d.lv[i]; n++) s = s + cost(i, n);
  }
  return s;
}""")
# {tokens earned, tokens spent, Dust earned, Dust spent}
M(calc, r"""
public static long[] balance(java.util.UUID u, @PKG@.TreeData d, int t, int lvl) {
  long[] r = new long[4];
  r[0] = tokensEarned(lvl);
  r[1] = tokSpent(d, t);
  r[2] = dustEarned(t, xp(u, t, lvl));
  r[3] = dustSpent(d, t);
  return r;
}""")
M(calc, r"""
public static int gate(int i) {
  int[] tl = @PKG@.TreeCfg.TIER_LV;
  return tl[@PKG@.TreeDefs.TIER[i] - 1];
}""")
M(calc, r"""
public static boolean pathOk(@PKG@.TreeData d, int t, int tier) {
  if (tier <= 1) return true;
  for (int k = 0; k < 12; k++) {
    int i = t * 12 + k;
    if (@PKG@.TreeDefs.soon(i)) continue;
    if (@PKG@.TreeDefs.TIER[i] == tier - 1 && d.lv[i] >= 1) return true;
  }
  return false;
}""")
# 0 locked, 1 unlockable, 2 owned, 3 maxed
M(calc, r"""
public static int state(@PKG@.TreeData d, int i, int lvl, long tokA) {
  if (@PKG@.TreeDefs.soon(i)) return 0;
  int l = d.lv[i];
  if (l >= @PKG@.TreeCfg.MAX[i]) return 3;
  if (l >= 1) return 2;
  if (d.bad || !@PKG@.TreeCfg.EN[i]) return 0;
  if (lvl < gate(i)) return 0;
  if (!pathOk(d, i / 12, @PKG@.TreeDefs.TIER[i])) return 0;
  if (tokA < (long) @PKG@.TreeCfg.TOK[i]) return 0;
  return 1;
}""")
M(calc, r"""
public static String lockShort(@PKG@.TreeData d, int i, int lvl, long tokA) {
  int t = i / 12;
  if (d.bad) return "Unreadable";
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
  if (!@PKG@.TreeCfg.EN[i]) return "Turned off";
  if (lvl < gate(i)) return @PKG@.TreeDefs.TREES[t] + " " + gate(i);
  if (!pathOk(d, t, @PKG@.TreeDefs.TIER[i])) return "Tier " + @PKG@.TreeDefs.roman(@PKG@.TreeDefs.TIER[i] - 1) + " first";
  int need = @PKG@.TreeCfg.TOK[i];
  if (tokA < (long) need) return "Need " + need + (need == 1 ? " token" : " tokens");
  return "Locked";
}""")

# ================= TreeFx: per-player effect vector + everything published from it =================
F(fx, "public static final java.util.concurrent.ConcurrentHashMap FX = new java.util.concurrent.ConcurrentHashMap();")
F(fx, 'public static final String SRC = "trees";')
F(fx, 'public static final String MOVE_SRC = "trees.tools";')
F(fx, 'public static final String ACRO_SRC = "trees.acrobatics";')
F(fx, "public static boolean STAT_FAILED = false;")
M(fx, r"""
public static double value(int i, int eff) {
  if (eff <= 0) return 0.0;
  int k = @PKG@.TreeDefs.KIND[i];
  double per = @PKG@.TreeCfg.PER[i];
  if (k == @K_FELLER@ && eff >= @PKG@.TreeCfg.MAX[i]) return (double) @PKG@.TreeCfg.FELLER_ALL;
  if (k == @K_VEIN@ || k == @K_FELLER@ || k == @K_DJUMP@) return @PKG@.TreeCfg.BASE[i] + per * (double) eff;
  if (k == @K_MASTER@) return per * (double) (eff - 1);
  if (k == @K_SWING@) {
    double sp = Math.floor(per * (double) eff * 100.0 + 0.000001);
    if (sp > 40.0) sp = 40.0;
    if (sp < 0.0) sp = 0.0;
    return sp / 100.0;
  }
  return per * (double) eff;
}""")
M(fx, r"""
public static double[] compute(java.util.UUID u) {
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  double[] v = new double[@PKG@.TreeDefs.N];
  for (int i = 0; i < v.length; i++) v[i] = value(i, @PKG@.TreeCalc.eff(d, i));
  FX.put(u, v);
  return v;
}""")
M(fx, r"""
public static double[] get(java.util.UUID u) {
  return (double[]) FX.get(u);
}""")
M(fx, r"""
public static double r6(double x) {
  return Math.round(x * 1000000.0) / 1000000.0;
}""")
# 0.2.1 Double Jump card: the trigger key SkyySkills publishes (skill:dj:key = "crouch" / "jump" / "jump or crouch").
# LOCKED 2026-09-25: a missing bridge key reads as "jump" (second jump in mid-air), not crouch.
M(fx, r"""
public static String djKey() {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:dj:key");
    if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
  } catch (Throwable t) { }
  return "jump";
}""")
M(fx, r"""
public static void putNZ(java.util.HashMap m, String k, double x) {
  double r = r6(x);
  if (r != 0.0) m.put(k, Double.valueOf(r));
}""")
# the DD / XP numbers SkyySkills 0.4 reads (fractions)
M(fx, r"""
public static java.util.HashMap bonusMap(double[] v) {
  java.util.HashMap m = new java.util.HashMap();
  putNZ(m, "xp.mining", v[@I_MWISDOM@]);
  putNZ(m, "xp.foraging", v[@I_FWISDOM@]);
  putNZ(m, "xp.farming", v[@I_AWISDOM@]);
  putNZ(m, "xp.cooking", v[@I_CWISDOM@]);
  putNZ(m, "dd.mining", v[@I_MFORTUNE@]);
  putNZ(m, "dd.foraging", v[@I_FFORTUNE@] + v[@I_FFORTUNE2@]);
  putNZ(m, "dd.farming", v[@I_AFORTUNE@] + v[@I_AFORTUNE2@]);
  putNZ(m, "dodge.acrobatics", v[@I_RDODGE2@]);
  putNZ(m, "doublejump.acrobatics", v[@I_RDOUBLE@]);
  return m;
}""")
# skill:bonus:<uuid> -> ConcurrentHashMap source -> immutable Map; compared with the LIVE entry, so a replaced map is re-filled
M(fx, r"""
public static void postBonus(java.util.UUID u, double[] v) {
  java.util.Map b = @PKG@.TreeStore.bridge();
  String key = "skill:bonus:" + u.toString();
  java.util.HashMap m = bonusMap(v);
  Object o = b.get(key);
  if (m.isEmpty()) { if (o instanceof java.util.Map) ((java.util.Map) o).remove(SRC); return; }
  java.util.Map src = null;
  if (o instanceof java.util.Map) src = (java.util.Map) o;
  else {
    java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
    Object prev = b.putIfAbsent(key, n);
    if (prev instanceof java.util.Map) src = (java.util.Map) prev; else src = n;
  }
  if (m.equals(src.get(SRC))) return;
  src.put(SRC, java.util.Collections.unmodifiableMap(m));
}""")
M(fx, r"""
public static void postTree(java.util.UUID u, @PKG@.TreeData d) {
  StringBuilder sb = new StringBuilder();
  for (int t = 0; t < @PKG@.TreeDefs.NT; t++) {
    int owned = 0;
    for (int s = 0; s < 12; s++) if (d.lv[t * 12 + s] >= 1 && !@PKG@.TreeDefs.soon(t * 12 + s)) owned++;
    if (t > 0) sb.append(',');
    sb.append(@PKG@.TreeDefs.TREES[t]).append(':').append(owned).append('/').append(@PKG@.TreeCalc.tokensEarned(@PKG@.TreeCalc.level(u, t)));
  }
  String s = sb.toString();
  java.util.Map b = @PKG@.TreeStore.bridge();
  String key = "tree:" + u.toString();
  if (!s.equals(b.get(key))) b.put(key, s);
}""")
M(fx, r"""
public static void publish(java.util.UUID u, double[] v) {
  postBonus(u, v);
  postTree(u, @PKG@.TreeStore.data(u));
}""")
M(fx, r"""
public static void refresh(java.util.UUID u) {
  double[] v = compute(u);
  publish(u, v);
  FX.put(u, v);
}""")
# movement protocol v1 post (tools/skyymove.py MoveSync.post): all zeros removes our source; never touch another source
M(fx, r"""
public static void movePost(java.util.UUID u, float speed) {
  java.util.Map b = @PKG@.TreeStore.bridge();
  String k = "move:" + u.toString();
  Object o = b.get(k);
  if (speed == 0.0f) { if (o instanceof java.util.Map) ((java.util.Map) o).remove(MOVE_SRC); return; }
  java.util.Map m = null;
  if (o instanceof java.util.Map) m = (java.util.Map) o;
  else {
    java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
    Object prev = b.putIfAbsent(k, n);
    if (prev instanceof java.util.Map) m = (java.util.Map) prev; else m = n;
  }
  java.util.HashMap e = new java.util.HashMap();
  e.put("layer", "flat");
  e.put("speed", Float.valueOf(speed));
  e.put("jump", Float.valueOf(0.0f));
  e.put("fallDamage", Float.valueOf(0.0f));
  if (e.equals(m.get(MOVE_SRC))) return;
  m.put(MOVE_SRC, e);
}""")
# 0.2 Acrobatics tree: movement protocol v1 source "trees.acrobatics" (layer flat: speed = fraction of the default speed, jump = blocks,
# fallDamage = added to the multiplier, negative = less). All zeros removes our entry; never touches another source (skyymove rule 1).
M(fx, r"""
public static void acroPost(java.util.UUID u, double[] v) {
  float sp = (float) r6(v[@I_RSPEED@] + v[@I_RSPEED2@] + v[@I_RSPEED3@]);
  float jp = (float) r6(v[@I_RJUMP@] + v[@I_RJUMP2@]);
  float fd = (float) r6(0.0 - (v[@I_RFALL@] + v[@I_RFALL2@]));
  java.util.Map b = @PKG@.TreeStore.bridge();
  String k = "move:" + u.toString();
  Object o = b.get(k);
  if (sp == 0.0f && jp == 0.0f && fd == 0.0f) { if (o instanceof java.util.Map) ((java.util.Map) o).remove(ACRO_SRC); return; }
  java.util.Map m = null;
  if (o instanceof java.util.Map) m = (java.util.Map) o;
  else {
    java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
    Object prev = b.putIfAbsent(k, n);
    if (prev instanceof java.util.Map) m = (java.util.Map) prev; else m = n;
  }
  java.util.HashMap e = new java.util.HashMap();
  e.put("layer", "flat");
  e.put("speed", Float.valueOf(sp));
  e.put("jump", Float.valueOf(jp));
  e.put("fallDamage", Float.valueOf(fd));
  if (e.equals(m.get(ACRO_SRC))) return;
  m.put(ACRO_SRC, e);
}""")
M(fx, r"""
public static double toolSpeed(double[] v, String held) {
  if (held == null) return 0.0;
  if (held.startsWith("Tool_Pickaxe_")) return v[@I_MRUNNER@];
  if (held.startsWith("Tool_Hatchet_")) return v[@I_FSTRIDE@];
  if (held.startsWith("Tool_Hoe_") || held.startsWith("Tool_Sickle_")) return v[@I_ARUNNER@];
  return 0.0;
}""")
# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat - SkyySkills Perks.mod / SkyyAccessories AccEffects.mod
M(fx, r"""
public static void mod(@ESM@ m, int idx, String key, float amt) {
  if (idx < 0) return;
  try {
    if (m.get(idx) == null) return;
    @MOD@ cur = m.getModifier(idx, key);
    if (amt == 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
    @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  } catch (Throwable t) { }
}""")
M(fx, r"""
public static void stats(@CB@ cb, @REF@ ref, double[] v) {
  try {
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    if (m == null) return;
    double hp = v[@I_FVIGOR@] + v[@I_AHEARTY@] + v[@I_CFED@] + v[@I_EHEART@] + v[@I_EHEART2@];
    double sta = v[@I_MSTAMINA@] + v[@I_RSTAMINA@] + v[@I_RSTAMINA2@] + v[@I_RSTAMINA3@];
    mod(m, @DST@.getHealth(), "skyytree_health", (float) (Math.round(hp * 100.0) / 100.0));
    mod(m, @DST@.getStamina(), "skyytree_stamina", (float) (Math.round(sta * 100.0) / 100.0));
  } catch (Throwable t) {
    if (!STAT_FAILED) { STAT_FAILED = true; @PKG@.TreeCfg.warn("stat modifiers failed (logged once): " + t); }
  }
}""")
M(fx, r"""
public static double dmgBonus(double[] v, @BTY@ bt) {
  String gt = @PKG@.TreeDefs.gatherType(bt);
  String id = @PKG@.TreeDefs.bid(bt);
  boolean ore = id.startsWith("Ore_");
  boolean rock = ore || "Rocks".equals(gt) || "VolcanicRocks".equals(gt) || (gt != null && gt.startsWith("Ore"));
  double b = 0.0;
  if (rock) b = b + v[@I_MHEAVY@];
  if ("Woods".equals(gt)) b = b + v[@I_FSPEED2@];
  return b;
}""")
# take one player's UUID-keyed bridge entries back: our source in skill:bonus:<uuid> and move:<uuid> (the shared containers stay,
# other mods post into them too) and tree:<uuid>. Callers take the player out of FX FIRST (see TreeSaver.retainOnline).
M(fx, r"""
public static void clearOne(java.util.UUID u) {
  try {
    java.util.Map b = @PKG@.TreeStore.bridge();
    Object o = b.get("skill:bonus:" + u.toString());
    if (o instanceof java.util.Map) ((java.util.Map) o).remove(SRC);
    Object mv = b.get("move:" + u.toString());
    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove(MOVE_SRC);
    if (mv instanceof java.util.Map) ((java.util.Map) mv).remove(ACRO_SRC);
    b.remove("tree:" + u.toString());
  } catch (Throwable t) { }
}""")
# shutdown: the same for everyone still in FX (offline players already left through retainOnline; the StaticModifiers stay on the
# players, see the docstring)
M(fx, r"""
public static void clearAll() {
  java.util.Iterator it = FX.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    clearOne(u);
  }
}""")

# ================= TreeMsg: one aggregated "Tree bonus" chat line per feedbackMs =================
F(msg, "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();")
F(msg, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
M(msg, r"""
public static synchronized void add(java.util.UUID u, String label, long n) {
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) PEND.get(u);
  if (m == null) { m = new java.util.LinkedHashMap(); PEND.put(u, m); }
  long[] c = (long[]) m.get(label);
  if (c == null) { c = new long[1]; m.put(label, c); }
  c[0] = c[0] + n;
}""")
M(msg, r"""
public static synchronized String take(java.util.UUID u, long now) {
  java.util.LinkedHashMap m = (java.util.LinkedHashMap) PEND.get(u);
  if (m == null || m.isEmpty()) return null;
  Object l = LAST.get(u);
  if (l != null && now - ((Long) l).longValue() < @PKG@.TreeCfg.FEEDBACK_MS) return null;
  StringBuilder sb = new StringBuilder("Tree bonus:");
  int n = 0;
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String k = (String) e.getKey();
    long c = ((long[]) e.getValue())[0];
    if (n > 0) sb.append(',');
    n++;
    if (n > 6) { sb.append(" ..."); break; }
    if (k.equals("extra drops") || k.equals("Spread")) sb.append(' ').append(k).append(" x").append(c);
    else sb.append(" +").append(c).append(' ').append(k);
  }
  PEND.remove(u);
  LAST.put(u, Long.valueOf(now));
  return sb.toString();
}""")
M(msg, r"""
public static void flush(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String s = take(u, System.currentTimeMillis());
  if (s == null) return;
  if (!@PKG@.TreeStore.notifyOn(u, "trees.bonus")) return;
  pr.sendMessage(@MSG@.raw(s).color("#b8f0a0"));
}""")
M(msg, r"""
public static void say(@PR@ pr, String text, String color) {
  try { pr.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")

# ================= TreeAbil: Spread / Vein Burst / Tree Feller (BREAK hook) =================
F(abil, "public static final java.util.concurrent.ConcurrentHashMap RECENT = new java.util.concurrent.ConcurrentHashMap();")
F(abil, "public static final java.util.concurrent.ConcurrentHashMap CD = new java.util.concurrent.ConcurrentHashMap();")
F(abil, "public static final java.util.concurrent.ConcurrentHashMap ACTIVE = new java.util.concurrent.ConcurrentHashMap();")
F(abil, "public static final java.util.concurrent.ConcurrentHashMap ITEMOK = new java.util.concurrent.ConcurrentHashMap();")
F(abil, "public static boolean BREAK_FAILED = false;")
F(abil, "public static boolean NO_PLACED_TOLD = false;")
M(abil, r"""
public static String key(String wn, int x, int y, int z) {
  return wn + "|" + x + "|" + y + "|" + z;
}""")
M(abil, r"""
public static long pos(int x, int y, int z) {
  return (((long) x) & 0x3FFFFFFL) << 38 | (((long) z) & 0x3FFFFFFL) << 12 | (((long) y) & 0xFFFL);
}""")
# current block id at a position (world thread), "" for air/unknown, null when the section is not loaded (SkyySkills blockIdAt)
M(abil, r"""
public static String blockIdAt(@WLD@ w, int x, int y, int z) {
  try {
    @CHS@ cs = w.getChunkStore();
    if (cs == null) return null;
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return null;
    @BSC@ sec = (@BSC@) cs.getStore().getComponent(sr, @BSC@.getComponentType());
    if (sec == null) return null;
    @BTY@ bt = (@BTY@) @BTY@.getAssetMap().getAsset(sec.get(x, y, z));
    if (bt == null) return "";
    return @PKG@.TreeDefs.bid(bt);
  } catch (Throwable t) { return null; }
}""")
M(abil, r"""
public static boolean recent(String wn, int x, int y, int z) {
  Object e = RECENT.get(key(wn, x, y, z));
  return e != null && ((Long) e).longValue() > System.currentTimeMillis();
}""")
M(abil, r"""
public static void mark(String wn, java.util.ArrayList list) {
  Long exp = Long.valueOf(System.currentTimeMillis() + 5000L);
  for (int i = 0; i < list.size(); i++) {
    @V3I@ v = (@V3I@) list.get(i);
    RECENT.put(key(wn, v.x(), v.y(), v.z()), exp);
  }
}""")
M(abil, r"""
public static void prune() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = RECENT.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (((Long) e.getValue()).longValue() <= now) it.remove(); }
  it = CD.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (((Long) e.getValue()).longValue() <= now) it.remove(); }
}""")
M(abil, r"""
public static java.util.function.Function placedFn() {
  java.util.function.Function f = @PKG@.TreeCalc.fn("skill:fn:placed");
  if (f == null && !NO_PLACED_TOLD) {
    NO_PLACED_TOLD = true;
    @PKG@.TreeCfg.warn("skill:fn:placed is missing (SkyySkills 0.4 trees bridge) - Spread, Vein Burst and Tree Feller stay off so they can never break placed blocks");
  }
  return f;
}""")
# an unknown answer counts as placed (safe side)
M(abil, r"""
public static boolean placed(java.util.function.Function f, String wn, int x, int y, int z) {
  try {
    Object r = f.apply(new Object[] { wn, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) });
    return !Boolean.FALSE.equals(r);
  } catch (Throwable t) { return true; }
}""")
M(abil, r"""
public static boolean worldAllowed(String wn) {
  String[] off = @PKG@.TreeCfg.OFF_WORLDS;
  for (int i = 0; i < off.length; i++) if (off[i].equalsIgnoreCase(wn)) return false;
  return true;
}""")
M(abil, r"""
public static boolean itemOk(String id) {
  if (id == null || id.length() == 0) return false;
  Object c = ITEMOK.get(id);
  if (c != null) return ((Boolean) c).booleanValue();
  boolean ok = false;
  try { ok = @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { ok = false; }
  ITEMOK.put(id, Boolean.valueOf(ok));
  if (!ok) @PKG@.TreeCfg.warn("item id '" + id + "' does not exist - never given (check trees.properties)");
  return ok;
}""")
M(abil, r"""
public static @WLD@ worldOf(@PR@ pr, String wn) {
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  Object ext = r.getStore().getExternalData();
  if (!(ext instanceof @EST@)) return null;
  @WLD@ w = ((@EST@) ext).getWorld();
  if (w == null || wn == null || !wn.equals(w.getName())) return null;
  return w;
}""")
M(abil, r"""
public static boolean matches(String id, String match, boolean prefix) {
  if (id == null || id.length() == 0 || match == null) return false;
  return prefix ? @PKG@.TreeDefs.isLog(id, match) : id.equals(match);
}""")
# BFS over the 26-neighbourhood from (ox, oy, oz) (already broken). Adds up to max matching, unplaced, not-recent blocks within the
# box; keeps scanning matched blocks up to scanMax for the leaves check (Tree Feller). leavesOut[0] = a Plant_Leaves_ block touches it.
M(abil, r"""
public static java.util.ArrayList flood(@WLD@ w, String wn, int ox, int oy, int oz, String match, boolean prefix, int max, int scanMax, int rh, int rv, boolean[] leavesOut, java.util.function.Function pf) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayDeque q = new java.util.ArrayDeque();
  seen.add(Long.valueOf(pos(ox, oy, oz)));
  q.add(new int[] { ox, oy, oz });
  boolean leaves = false;
  int matched = 0;
  int reads = 0;
  while (!q.isEmpty() && reads < 4000) {
    int[] c = (int[]) q.poll();
    for (int dx = -1; dx <= 1; dx++) {
      for (int dy = -1; dy <= 1; dy++) {
        for (int dz = -1; dz <= 1; dz++) {
          if (dx == 0 && dy == 0 && dz == 0) continue;
          int x = c[0] + dx;
          int y = c[1] + dy;
          int z = c[2] + dz;
          if (Math.abs(x - ox) > rh || Math.abs(z - oz) > rh || Math.abs(y - oy) > rv) continue;
          Long k = Long.valueOf(pos(x, y, z));
          if (seen.contains(k)) continue;
          seen.add(k);
          reads++;
          String id = blockIdAt(w, x, y, z);
          if (id == null || id.length() == 0) continue;
          if (!leaves && id.startsWith("Plant_Leaves_")) leaves = true;
          if (!matches(id, match, prefix)) continue;
          if (matched >= scanMax) continue;
          if (recent(wn, x, y, z) || placed(pf, wn, x, y, z)) continue;
          matched++;
          q.add(new int[] { x, y, z });
          if (out.size() < max) out.add(new @V3I@(x, y, z));
        }
      }
    }
  }
  if (leavesOut != null) leavesOut[0] = leaves;
  return out;
}""")
# 0.2.1 Tree Feller (Tree-Fall-Spec 3.3): breadth-first on the cut's Y level ONLY, over the 8 horizontal neighbours - the 4 sides
# before the 4 diagonals - so the logs nearest the cut come first. TreeDefs.isLog(id, fam) = Wood_<W>_Trunk / _Trunk_Full (+ states)
# only, not placed, not broken by an ability in the last 5 s, |dx|, |dz| <= rh, at most max positions and 4000 reads. Never another Y level.
M(abil, r"""
public static java.util.ArrayList flatFlood(@WLD@ w, String wn, int ox, int oy, int oz, String fam, int max, int rh, java.util.function.Function pf) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (max <= 0 || fam == null) return out;
  int[] ddx = new int[] { 1, -1, 0, 0, 1, 1, -1, -1 };
  int[] ddz = new int[] { 0, 0, 1, -1, 1, -1, 1, -1 };
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayDeque q = new java.util.ArrayDeque();
  seen.add(Long.valueOf(pos(ox, oy, oz)));
  q.add(new int[] { ox, oz });
  int reads = 0;
  while (!q.isEmpty() && reads < 4000 && out.size() < max) {
    int[] c = (int[]) q.poll();
    for (int n = 0; n < 8 && out.size() < max; n++) {
      int x = c[0] + ddx[n];
      int z = c[1] + ddz[n];
      if (Math.abs(x - ox) > rh || Math.abs(z - oz) > rh) continue;
      Long k = Long.valueOf(pos(x, oy, z));
      if (seen.contains(k)) continue;
      seen.add(k);
      reads++;
      String id = blockIdAt(w, x, oy, z);
      if (!@PKG@.TreeDefs.isLog(id, fam)) continue;
      if (recent(wn, x, oy, z) || placed(pf, wn, x, oy, z)) continue;
      q.add(new int[] { x, z });
      out.add(new @V3I@(x, oy, z));
    }
  }
  return out;
}""")
M(abil, r"""
public static @V3I@ pickNeighbour(@WLD@ w, String wn, int x0, int y0, int z0, String id, java.util.function.Function pf) {
  java.util.ArrayList c = new java.util.ArrayList();
  for (int dx = -1; dx <= 1; dx++) {
    for (int dy = -1; dy <= 1; dy++) {
      for (int dz = -1; dz <= 1; dz++) {
        if (dx == 0 && dy == 0 && dz == 0) continue;
        int x = x0 + dx;
        int y = y0 + dy;
        int z = z0 + dz;
        if (!id.equals(blockIdAt(w, x, y, z))) continue;
        if (recent(wn, x, y, z) || placed(pf, wn, x, y, z)) continue;
        c.add(new @V3I@(x, y, z));
      }
    }
  }
  if (c.isEmpty()) return null;
  return (@V3I@) c.get(java.util.concurrent.ThreadLocalRandom.current().nextInt(c.size()));
}""")
# the engine's own multi-block break (BreakBlockInteraction pattern): each position fires a real BreakBlockEvent on the player
M(abil, r"""
public static int breakList(@PR@ pr, @WLD@ w, String wn, java.util.ArrayList list) {
  if (list == null || list.isEmpty()) return 0;
  java.util.UUID u = pr.getUuid();
  if (ACTIVE.containsKey(u)) return 0;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return 0;
  @ST@ st = r.getStore();
  @IS@ held = @INVC@.getItemInHand(st, r);
  if (held == null || held.isEmpty()) return 0;
  mark(wn, list);
  ACTIVE.put(u, Boolean.TRUE);
  int n = 0;
  try {
    java.util.List pl = list;
    n = @BHU@.performBlockBreak(r, held, pl, 4096, st, w.getChunkStore().getStore());
  } catch (Throwable t) {
    if (!BREAK_FAILED) { BREAK_FAILED = true; @PKG@.TreeCfg.warn("tree ability break failed (logged once): " + t); }
  }
  ACTIVE.remove(u);
  return n;
}""")
M(abil, r"""
public static boolean spread(@PR@ pr, String wn, int x, int y, int z, String id) {
  @WLD@ w = worldOf(pr, wn);
  if (w == null || id == null || id.length() == 0) return false;
  java.util.function.Function pf = placedFn();
  if (pf == null) return false;
  @V3I@ v = pickNeighbour(w, wn, x, y, z, id, pf);
  if (v == null) return false;
  java.util.ArrayList l = new java.util.ArrayList();
  l.add(v);
  int n = breakList(pr, w, wn, l);
  if (n > 0) @PKG@.TreeMsg.add(pr.getUuid(), "Spread", (long) n);
  return n > 0;
}""")
M(abil, r"""
public static boolean ready(java.util.UUID u, String what) {
  Object o = CD.get(u.toString() + "|" + what);
  return o == null || ((Long) o).longValue() <= System.currentTimeMillis();
}""")
M(abil, r"""
public static boolean vein(@PR@ pr, String wn, int x, int y, int z, String id, int max) {
  java.util.UUID u = pr.getUuid();
  if (max <= 0 || !ready(u, "vein")) return false;
  @WLD@ w = worldOf(pr, wn);
  if (w == null) return false;
  java.util.function.Function pf = placedFn();
  if (pf == null) return false;
  int rad = @PKG@.TreeCfg.RADIUS;
  java.util.ArrayList l = flood(w, wn, x, y, z, id, false, max, max, rad, rad, null, pf);
  if (l.isEmpty()) return false;
  int n = breakList(pr, w, wn, l);
  if (n <= 0) return false;
  long cd = @PKG@.TreeCfg.VEIN_CD_MS;
  CD.put(u.toString() + "|vein", Long.valueOf(System.currentTimeMillis() + cd));
  if (@PKG@.TreeStore.notifyOn(u, "trees.abilities")) @PKG@.TreeMsg.say(pr, "Vein Burst! +" + n + " ore (ready again in " + (cd / 1000L) + " s)", "#ffc300");
  return true;
}""")
M(abil, r"""
public static boolean feller(@PR@ pr, String wn, int x, int y, int z, String id, int max) {
  java.util.UUID u = pr.getUuid();
  if (max <= 0 || !ready(u, "feller")) return false;
  String fam = @PKG@.TreeDefs.logFamily(id);
  if (fam == null || !@PKG@.TreeDefs.isLog(id, fam)) return false;
  @WLD@ w = worldOf(pr, wn);
  if (w == null) return false;
  java.util.function.Function pf = placedFn();
  if (pf == null) return false;
  java.util.ArrayList l = flatFlood(w, wn, x, y, z, fam, max, @PKG@.TreeCfg.RADIUS, pf);
  if (l.isEmpty()) return false;
  if (@PKG@.TreeCfg.FELLER_LEAVES) {
    boolean[] leaves = new boolean[1];
    flood(w, wn, x, y, z, fam, true, 0, 256, @PKG@.TreeCfg.RADIUS, @PKG@.TreeCfg.FELLER_H, leaves, pf);
    if (!leaves[0]) return false;
  }
  int n = breakList(pr, w, wn, l);
  if (n <= 0) return false;
  long cd = @PKG@.TreeCfg.FELLER_CD_MS;
  CD.put(u.toString() + "|feller", Long.valueOf(System.currentTimeMillis() + cd));
  if (@PKG@.TreeStore.notifyOn(u, "trees.abilities")) @PKG@.TreeMsg.say(pr, "Tree Feller! +" + n + (n == 1 ? " log" : " logs") + " on this level" + (cd > 0L ? " (ready again in " + (cd / 1000L) + " s)" : ""), "#ffc300");
  return true;
}""")

# ================= TreeGather: the skill:on:gather listener (ITEM / EXTRA / COINS / BREAK) =================
gat.addInterface(pool.get("java.util.function.Function"))
F(gat, "public static Object INSTANCE;")
F(gat, "public static Object FELLED;")
F(gat, "public static boolean OFF_THREAD_TOLD = false;")
F(gat, "public static boolean FAILED_ONCE = false;")
C(gat, "public TreeGather() { }")
M(gat, r"""
public static boolean roll(double p) {
  if (p <= 0.0) return false;
  if (p >= 1.0) return true;
  return java.util.concurrent.ThreadLocalRandom.current().nextDouble() < p;
}""")
M(gat, r"""
public static String pick(Object list) {
  if (!(list instanceof String[])) return null;
  String[] xs = (String[]) list;
  if (xs.length == 0) return null;
  return xs[java.util.concurrent.ThreadLocalRandom.current().nextInt(xs.length)];
}""")
M(gat, r"""
public static @PLA@ player(@PR@ pr, String wn) {
  if (@PKG@.TreeAbil.worldOf(pr, wn) == null) return null;
  @REF@ r = pr.getReference();
  return (@PLA@) r.getStore().getComponent(r, @PLA@.getComponentType());
}""")
# storage > hotbar > backpack, dropped at the feet when full (SkyySkills Perks.give / SkyySacks 0.6.5 output path)
M(gat, r"""
public static void giveItem(@PR@ pr, String wn, String id) {
  if (!@PKG@.TreeAbil.itemOk(id)) return;
  @PLA@ p = player(pr, wn);
  if (p == null) return;
  @REF@ r = pr.getReference();
  @SIC@.addOrDropItemStack(r.getStore(), r, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, 1));
  @PKG@.TreeMsg.add(pr.getUuid(), @PKG@.TreeDefs.label(id), 1L);
}""")
M(gat, r"""
public static void giveDrops(@PR@ pr, String wn, @BTY@ bt, boolean harvest, int times) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("skill:fn:drops");
  if (f == null) return;
  @PLA@ p = player(pr, wn);
  if (p == null) return;
  @REF@ r = pr.getReference();
  for (int k = 0; k < times; k++) {
    Object o = f.apply(new Object[] { bt, Boolean.valueOf(harvest) });
    if (!(o instanceof java.util.List)) return;
    java.util.List l = (java.util.List) o;
    int n = 0;
    for (int i = 0; i < l.size(); i++) {
      Object e = l.get(i);
      if (!(e instanceof @IS@)) continue;
      @IS@ is = (@IS@) e;
      if (is.isEmpty() || is.getItemId() == null) continue;
      @SIC@.addOrDropItemStack(r.getStore(), r, p.getInventory().getCombinedStorageHotbarBackpack(), is);
      n++;
    }
    if (n > 0) @PKG@.TreeMsg.add(pr.getUuid(), "extra drops", 1L);
  }
}""")
M(gat, r"""
public static void coins(@PR@ pr, int t) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("coins:fn:add");
  if (f == null) return;
  java.util.UUID u = pr.getUuid();
  int lvl = @PKG@.TreeCalc.level(u, t);
  if (lvl <= 0) return;
  f.apply(new Object[] { u, Long.valueOf((long) lvl) });
  @PKG@.TreeMsg.add(u, "coins", (long) lvl);
}""")
M(gat, r"""
public static void run(@PR@ pr, int row, @BTY@ bt, String wn, boolean harvest, int x, int y, int z) {
  java.util.UUID u = pr.getUuid();
  if (bt == null || wn == null) return;
  if (@PKG@.TreeStore.busy(u)) return;
  double[] v = @PKG@.TreeFx.get(u);
  if (v == null) v = @PKG@.TreeFx.compute(u);
  String id = @PKG@.TreeDefs.bid(bt);
  boolean chained = @PKG@.TreeAbil.recent(wn, x, y, z);
  boolean abil = !chained && !harvest && @PKG@.TreeAbil.worldAllowed(wn);
  Object[] lists = @PKG@.TreeCfg.LIST;
  if (row == 0) {
    boolean ore = id.startsWith("Ore_");
    if (roll(v[@I_MGEMS@])) giveItem(pr, wn, pick(lists[@I_MGEMS@]));
    if (ore && roll(v[@I_MVEINS@])) giveDrops(pr, wn, bt, false, 1);
    if (ore && roll(v[@I_MBARS@])) giveItem(pr, wn, @PKG@.TreeDefs.barOf(id));
    if (roll(v[@I_MCOINS@])) coins(pr, 0);
    if (abil) {
      boolean fired = false;
      if (ore && v[@I_MVEIN@] >= 1.0) fired = @PKG@.TreeAbil.vein(pr, wn, x, y, z, id, (int) Math.round(v[@I_MVEIN@]));
      if (!fired && roll(v[@I_MSPREAD@])) @PKG@.TreeAbil.spread(pr, wn, x, y, z, id);
    }
    return;
  }
  if (row == 1) {
    if (id.indexOf("_Trunk") < 0) return;
    if (roll(v[@I_FSAP@])) giveItem(pr, wn, pick(lists[@I_FSAP@]));
    if (roll(v[@I_FSAPLING@])) giveItem(pr, wn, @PKG@.TreeDefs.saplingOf(id));
    if (roll(v[@I_FCOINS@])) coins(pr, 1);
    if (abil) {
      boolean fired = false;
      if (v[@I_FFELLER@] >= 1.0) fired = @PKG@.TreeAbil.feller(pr, wn, x, y, z, id, (int) Math.round(v[@I_FFELLER@]));
      if (!fired && roll(v[@I_FSPREAD@])) @PKG@.TreeAbil.spread(pr, wn, x, y, z, id);
    }
    return;
  }
  if (row == 2) {
    String crop = @PKG@.TreeDefs.cropOf(@PKG@.TreeDefs.family(bt));
    if (crop != null && roll(v[@I_ASEEDS@])) giveItem(pr, wn, @PKG@.TreeDefs.seedsOf(crop));
    if (roll(v[@I_AESSENCE@])) giveItem(pr, wn, pick(lists[@I_AESSENCE@]));
    if (crop != null) {
      if (@PKG@.TreeDefs.inList((String[]) lists[@I_AGRAIN@], crop) && roll(v[@I_AGRAIN@])) giveDrops(pr, wn, bt, harvest, 1);
      if (@PKG@.TreeDefs.inList((String[]) lists[@I_AROOTS@], crop) && roll(v[@I_AROOTS@])) giveDrops(pr, wn, bt, harvest, 1);
      if (@PKG@.TreeDefs.inList((String[]) lists[@I_AGARDEN@], crop) && roll(v[@I_AGARDEN@])) giveDrops(pr, wn, bt, harvest, 1);
      if (@PKG@.TreeDefs.inList((String[]) lists[@I_AHERBS@], crop) && roll(v[@I_AHERBS@])) giveDrops(pr, wn, bt, harvest, 1);
    }
    if (roll(v[@I_ACORN@])) giveDrops(pr, wn, bt, harvest, 2);
  }
}""")
# 0.2.1 (Tree-Fall-Spec 3.3): one log that FELL because this player cut the tree (SkyySkills 0.4.2 skill:on:felled, world thread).
# Foraging trunks roll Sap Tapper, Replanter and Pocket Change exactly like run(); abilities (Spread / Vein Burst / Tree Feller) never.
# Review guards: a position one of OUR abilities broke in the last 5 s (TreeAbil.mark) already rolled in run() through its real
# BreakBlockEvent, so it never rolls again here, whatever SkyySkills reports; off the world thread nothing happens (warned once).
M(gat, r"""
public static void felled(@PR@ pr, int row, @BTY@ bt, String wn, int x, int y, int z) {
  if (!@PKG@.TreeCfg.FELLED_NODES || row != 1 || bt == null || wn == null) return;
  if (@PKG@.TreeAbil.recent(wn, x, y, z)) return;
  @REF@ r = pr.getReference();
  if (r == null || !r.isValid()) return;
  if (!r.getStore().isInThread()) {
    if (!OFF_THREAD_TOLD) { OFF_THREAD_TOLD = true; @PKG@.TreeCfg.warn("skill:on:felled was called off the world thread - felled-log tree bonuses skipped (logged once)"); }
    return;
  }
  java.util.UUID u = pr.getUuid();
  if (@PKG@.TreeStore.busy(u)) return;
  String id = @PKG@.TreeDefs.bid(bt);
  if (id.indexOf("_Trunk") < 0) return;
  double[] v = @PKG@.TreeFx.get(u);
  if (v == null) v = @PKG@.TreeFx.compute(u);
  Object[] lists = @PKG@.TreeCfg.LIST;
  if (roll(v[@I_FSAP@])) giveItem(pr, wn, pick(lists[@I_FSAP@]));
  if (roll(v[@I_FSAPLING@])) giveItem(pr, wn, @PKG@.TreeDefs.saplingOf(id));
  if (roll(v[@I_FCOINS@])) coins(pr, 1);
}""")
# SkyySkills 0.4 calls this on the world thread: Object[]{PlayerRef, Integer row, BlockType, String world, Boolean harvest, x, y, z}
M(gat, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 8 || !(a[0] instanceof @PR@) || !(a[1] instanceof Number)) return null;
    int row = ((Number) a[1]).intValue();
    if (row < 0 || row > 2) return null;
    @BTY@ bt = null;
    if (a[2] instanceof @BTY@) bt = (@BTY@) a[2];
    String wn = null;
    if (a[3] instanceof String) wn = (String) a[3];
    boolean harvest = Boolean.TRUE.equals(a[4]);
    int x = ((Number) a[5]).intValue();
    int y = ((Number) a[6]).intValue();
    int z = ((Number) a[7]).intValue();
    run((@PR@) a[0], row, bt, wn, harvest, x, y, z);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("tree gather bonus failed (logged once): " + t); }
  }
  return null;
}""")
M(gat, r"""
public static java.util.Map gatherMap() {
  java.util.Map b = @PKG@.TreeStore.bridge();
  Object o = b.get("skill:on:gather");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent("skill:on:gather", n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""")
M(gat, r"""
public static java.util.Map felledMap() {
  java.util.Map b = @PKG@.TreeStore.bridge();
  Object o = b.get("skill:on:felled");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent("skill:on:felled", n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""")
M(gat, r"""
public static void ensure() {
  try {
    if (INSTANCE == null) return;
    java.util.Map m = gatherMap();
    if (m.get("trees") != INSTANCE) m.put("trees", INSTANCE);
  } catch (Throwable t) { }
  try {
    if (FELLED == null) return;
    java.util.Map f = felledMap();
    if (f.get("trees") != FELLED) f.put("trees", FELLED);
  } catch (Throwable t2) { }
}""")
M(gat, r"""
public static void unregister() {
  try {
    Object o = @PKG@.TreeStore.bridge().get("skill:on:gather");
    if (o instanceof java.util.Map && INSTANCE != null) ((java.util.Map) o).remove("trees", INSTANCE);
  } catch (Throwable t) { }
  try {
    Object f = @PKG@.TreeStore.bridge().get("skill:on:felled");
    if (f instanceof java.util.Map && FELLED != null) ((java.util.Map) f).remove("trees", FELLED);
  } catch (Throwable t2) { }
}""")

# ================= TreeFn / TreeBonusFn: tree:fn:level and tree:fn:bonus =================
tfn.addInterface(pool.get("java.util.function.Function"))
C(tfn, "public TreeFn() { }")
M(tfn, r"""
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;
    if (!(a[0] instanceof java.util.UUID)) return Integer.valueOf(0);
    int i = @PKG@.TreeDefs.idx(String.valueOf(a[1]));
    if (i < 0) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.TreeCalc.eff(@PKG@.TreeStore.data((java.util.UUID) a[0]), i));
  } catch (Throwable t) { return Integer.valueOf(0); }
}""")
bfn.addInterface(pool.get("java.util.function.Function"))
C(bfn, "public TreeBonusFn() { }")
M(bfn, r"""
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;
    if (!(a[0] instanceof java.util.UUID)) return Double.valueOf(0.0);
    int i = @PKG@.TreeDefs.idx(String.valueOf(a[1]));
    if (i < 0) return Double.valueOf(0.0);
    if (@PKG@.TreeDefs.KIND[i] == @K_SWING@ && !@PKG@.TreeCfg.SWING_ON) return Double.valueOf(0.0);
    int e = @PKG@.TreeCalc.eff(@PKG@.TreeStore.data((java.util.UUID) a[0]), i);
    return Double.valueOf(@PKG@.TreeFx.value(i, e));
  } catch (Throwable t) { return Double.valueOf(0.0); }
}""")

# 0.2.1: SkyySkills 0.4.2 calls this once per credited felled position, world thread:
# Object[]{PlayerRef, Integer row, BlockType, String world, Integer x, Integer y, Integer z, String pkey} (Tree-Fall-Spec 2.8)
ffn.addInterface(pool.get("java.util.function.Function"))
F(ffn, "public static boolean FAILED_ONCE = false;")
C(ffn, "public TreeFelledFn() { }")
M(ffn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 7 || !(a[0] instanceof @PR@) || !(a[1] instanceof Number)) return null;
    if (!(a[4] instanceof Number) || !(a[5] instanceof Number) || !(a[6] instanceof Number)) return null;
    @PR@ pr = (@PR@) a[0];
    if (a.length >= 8 && a[7] instanceof String && !((String) a[7]).equals(@PKG@.TreeStore.pkey(pr.getUuid()))) return null;
    @BTY@ bt = null;
    if (a[2] instanceof @BTY@) bt = (@BTY@) a[2];
    String wn = null;
    if (a[3] instanceof String) wn = (String) a[3];
    @PKG@.TreeGather.felled(pr, ((Number) a[1]).intValue(), bt, wn, ((Number) a[4]).intValue(), ((Number) a[5]).intValue(), ((Number) a[6]).intValue());
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("felled-log tree bonus failed (logged once): " + t); }
  }
  return null;
}""")

# ================= TreeDmgSys: breaking power (DMG) =================
C(dmg, "public TreeDmgSys() { super(@DBE@.class); }")
F(dmg, "public static boolean FAILED_ONCE = false;")
M(dmg, r"""
public @QRY@ getQuery() {
  return com.hypixel.hytale.component.Archetype.empty();
}""")
M(dmg, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    @DBE@ e = (@DBE@) ev;
    if (e.isCancelled()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    double[] v = @PKG@.TreeFx.get(pr.getUuid());
    if (v == null) return;
    @BTY@ bt = e.getBlockType();
    if (bt == null) return;
    double b = @PKG@.TreeFx.dmgBonus(v, bt);
    if (b <= 0.0) return;
    e.setDamage((float) (e.getDamage() * (1.0 + b)));
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("breaking power handler failed (logged once): " + t); }
  }
}""")

# ================= 0.2.3 TreeSwing: pickaxe / hatchet swing tiers (research/Swing-Speed-Spec.md 2.2 + 3.6) =================
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

# ================= TreeTick: once per second per player on the world thread =================
C(tick, "public TreeTick() { super(); }")
F(tick, "public static final java.util.concurrent.ConcurrentHashMap ACC = new java.util.concurrent.ConcurrentHashMap();")
F(tick, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")
F(tick, "public static boolean FAILED_ONCE = false;")
M(tick, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(tick, r"""
public boolean isParallel(int a, int b) {
  return false;
}""")
# PROFILES-CONTRACT 4.2: the first epoch seen is a baseline; an absent epoch is never recorded
M(tick, r"""
public static boolean epochChanged(java.util.UUID u) {
  long e = -1L;
  try {
    Object o = @PKG@.TreeStore.bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) e = ((Number) o).longValue();
  } catch (Throwable t) { }
  if (e < 0L) return false;
  Object last = EPOCH.put(u, Long.valueOf(e));
  return last != null && ((Long) last).longValue() != e;
}""")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    double[] s = (double[]) ACC.get(u);
    if (s == null) { s = new double[2]; ACC.put(u, s); }
    s[0] = s[0] + (double) dt;
    if (s[0] < 1.0) return;
    s[0] = 0.0;
    s[1] = s[1] + 1.0;
    if (epochChanged(u)) {
      @PKG@.TreeMsg.PEND.remove(u);
      @PKG@.TreeCfg.info("profile switch: " + u + " now uses the trees of " + @PKG@.TreeStore.pkey(u));
    }
    @PKG@.TreeData d = @PKG@.TreeStore.data(u);
    if (d.name == null) @PKG@.TreeStore.setName(d, pr.getUsername());
    double[] v = @PKG@.TreeFx.compute(u);
    @PKG@.TreeFx.publish(u, v);
    @PKG@.TreeFx.stats(cb, ref, v);
    @PKG@.TreeSwing.apply(cb, ref, v);
    @IS@ held = @INVC@.getItemInHand(cb, ref);
    String hid = null;
    if (held != null && !held.isEmpty()) hid = held.getItemId();
    @PKG@.TreeFx.movePost(u, (float) @PKG@.TreeFx.toolSpeed(v, hid));
    @PKG@.TreeFx.acroPost(u, v);
    @PKG@.TreeFx.FX.put(u, v);
    @PKG@.TreeMsg.flush(pr);
    @PKG@.TreeSwing.notice(pr, u);
    if (((long) s[1]) % 5L == 0L) @PKG@.TreeGather.ensure();
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TreeCfg.warn("tree tick failed (logged once): " + t); }
  }
}""")

# ================= TreeSaver: 1 s scheduler ticker (saves, pruning - never reads player files) =================
# retainOnline (every 30 s): a player who left (Universe.getPlayer == null; a world transfer keeps the PlayerRef) is taken out of FX
# FIRST and THEN their bridge entries are removed (TreeFx.clearOne). TreeTick / refresh write the bridge first and put FX after, so a
# tick racing the disconnect only re-marks the player for the next pass - nothing stale stays behind (review fix).
svr.addInterface(pool.get("java.lang.Runnable"))
F(svr, "public long n;")
C(svr, "public TreeSaver() { this.n = 0L; }")
M(svr, r"""
public static void retainOnline() {
  java.util.Iterator it = @PKG@.TreeFx.FX.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    if (@UNI@.get().getPlayer(u) != null) continue;
    it.remove();
    @PKG@.TreeFx.clearOne(u);
    @PKG@.TreeTick.ACC.remove(u);
    @PKG@.TreeTick.EPOCH.remove(u);
    @PKG@.TreeMsg.PEND.remove(u);
    @PKG@.TreeMsg.LAST.remove(u);
  }
}""")
M(svr, r"""
public void run() {
  this.n++;
  if (this.n % 10L == 0L) { try { @PKG@.TreeStore.flushDirty(); } catch (Throwable t) { } }
  if (this.n % 30L == 0L) {
    try { @PKG@.TreeAbil.prune(); } catch (Throwable t) { }
    try { retainOnline(); } catch (Throwable t) { }
    try { @PKG@.TreeStore.retain(); } catch (Throwable t) { }
  }
}""")

# ================= TreeOps: buy / toggle / respec / quiet (world thread; the server re-checks every rule) =================
M(ops, r"""
public static String tokensWord(long n) {
  return n == 1L ? " token" : " tokens";
}""")
M(ops, r"""
public static String soonText(int t, int s) {
  return "Node S" + s + " of the " + @PKG@.TreeDefs.TREES[t] + " tree is coming later - Skyy designs the rest of this draft tree later";
}""")
M(ops, r"""
public static String buy(@PR@ pr, int t, int s) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  int i = t * 12 + s - 1;
  String nm = @PKG@.TreeDefs.NAME[i];
  String tn = @PKG@.TreeDefs.TREES[t];
  if (@PKG@.TreeDefs.soon(i)) return soonText(t, s);
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (!@PKG@.TreeCfg.EN[i]) return nm + " is turned off on this server";
  int lvl = @PKG@.TreeCalc.level(u, t);
  if (lvl < 0) return "Skill trees need SkyySkills - it is not loaded";
  long[] bal = @PKG@.TreeCalc.balance(u, d, t, lvl);
  long tokA = bal[0] - bal[1];
  long dustA = bal[2] - bal[3];
  int cur = d.lv[i];
  int max = @PKG@.TreeCfg.MAX[i];
  if (cur >= max) return nm + " is already maxed";
  if (tokA < 0L || dustA < 0L) return "Your " + tn + " balance is negative (costs changed) - respec first, it is free right now";
  if (cur == 0) {
    int tier = @PKG@.TreeDefs.TIER[i];
    int g = @PKG@.TreeCalc.gate(i);
    if (lvl < g) return nm + " needs " + tn + " " + g;
    if (!@PKG@.TreeCalc.pathOk(d, t, tier)) return "Unlock a Tier " + @PKG@.TreeDefs.roman(tier - 1) + " node first";
    long need = (long) @PKG@.TreeCfg.TOK[i];
    if (tokA < need) return nm + " needs " + need + tokensWord(need) + " - you have " + tokA;
    @PKG@.TreeStore.setLevel(d, i, 1);
    if (i == @I_MSPEED@ || i == @I_FSPEED@ || i == @I_FSPEED2@) @PKG@.TreeStore.setNote(d);
    @PKG@.TreeStore.dirty(k);
    @PKG@.TreeFx.refresh(u);
    return "Unlocked " + nm + "!";
  }
  long c = @PKG@.TreeCalc.cost(i, cur);
  if (dustA < c) return "Needs " + @PKG@.TreeDefs.grp(c - dustA) + " more " + tn + " Dust";
  @PKG@.TreeStore.setLevel(d, i, cur + 1);
  @PKG@.TreeStore.dirty(k);
  @PKG@.TreeFx.refresh(u);
  return nm + " is now level " + (cur + 1) + (cur + 1 >= max ? " - MAX" : "");
}""")
M(ops, r"""
public static String toggle(@PR@ pr, int t, int s) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  int i = t * 12 + s - 1;
  if (@PKG@.TreeDefs.soon(i)) return soonText(t, s);
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  if (d.lv[i] <= 0) return "You do not own " + @PKG@.TreeDefs.NAME[i] + " yet";
  boolean off = @PKG@.TreeStore.flipOff(d, i);
  @PKG@.TreeStore.dirty(k);
  @PKG@.TreeFx.refresh(u);
  return @PKG@.TreeDefs.NAME[i] + (off ? " turned off - its level is kept" : " turned on");
}""")
M(ops, r"""
public static String waitText(long ms) {
  if (ms < 60000L) return ((ms + 999L) / 1000L) + " s";
  return ((ms + 59999L) / 60000L) + " min";
}""")
M(ops, r"""
public static String respec(@PR@ pr, int t) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  String tn = @PKG@.TreeDefs.TREES[t];
  if (d.bad) return "Your tree file could not be read - nothing can change until an admin fixes it";
  boolean any = false;
  for (int s = 0; s < 12; s++) if (d.lv[t * 12 + s] > 0) any = true;
  if (!any) return "Nothing to respec in " + tn;
  int lvl = @PKG@.TreeCalc.level(u, t);
  long[] bal = @PKG@.TreeCalc.balance(u, d, t, lvl);
  boolean neg = bal[0] < bal[1] || bal[2] < bal[3];
  long now = System.currentTimeMillis();
  long wait = d.respecAt[t] + @PKG@.TreeCfg.RESPEC_CD_MS - now;
  if (!neg && wait > 0L) return "You can respec " + tn + " again in " + waitText(wait);
  long price = @PKG@.TreeCfg.RESPEC_COINS;
  if (price > 0L && !neg) {
    java.util.function.Function f = @PKG@.TreeCalc.fn("coins:fn:take");
    if (f == null) return "A respec costs " + @PKG@.TreeDefs.grp(price) + " coins but SkyyCoins is not loaded";
    Object r = f.apply(new Object[] { u, Long.valueOf(price) });
    if (!Boolean.TRUE.equals(r)) return "A respec costs " + @PKG@.TreeDefs.grp(price) + " coins - you do not have enough";
  }
  @PKG@.TreeStore.clearTree(d, t, now);
  @PKG@.TreeStore.saveSoon(k);
  @PKG@.TreeFx.refresh(u);
  @PKG@.TreeCfg.info("respec " + tn + " for " + k);
  return "Respec done - every " + tn + " token and all your " + tn + " Dust are back";
}""")
M(ops, r"""
public static boolean quiet(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.TreeStore.pkey(u);
  @PKG@.TreeData d = @PKG@.TreeStore.dataK(k, u);
  boolean q = @PKG@.TreeStore.flipQuiet(d);
  if (!d.bad) @PKG@.TreeStore.dirty(k);
  return q;
}""")
# 0.2.2: with SkyyMenu's settings registry /tree quiet is a shortcut for the trees.bonus switch (notifyOn first = the one-shot quiet
# move, so the flip starts from what the player sees); without it the 0.2.1 per-profile toggle above runs unchanged
M(ops, r"""
public static String quietText(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  java.util.function.Function sf = @PKG@.TreeCalc.fn("settings:fn:set");
  if (sf != null) {
    boolean on = @PKG@.TreeStore.notifyOn(u, "trees.bonus");
    Object r = null;
    try { r = sf.apply(new Object[] { u, "trees.bonus", Boolean.valueOf(!on) }); } catch (Throwable t) { r = null; }
    if (!Boolean.TRUE.equals(r)) return "[Trees] Could not save the setting - try /settings (tab Cooking).";
    return on ? "[Trees] Tree bonus messages hidden. More switches: /settings" : "[Trees] Tree bonus messages shown. More switches: /settings";
  }
  boolean q = quiet(pr);
  return q ? "[Trees] Tree bonus messages hidden. /tree quiet again to show them." : "[Trees] Tree bonus messages shown.";
}""")

# ================= TreePage: the inline tree page =================
def tbs(bg, hv, pr, fg, fgh):
    lab = "FontSize: 12, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center"
    return ("Style: TextButtonStyle(Default: (Background: %s, LabelStyle: (%s)), Hovered: (Background: %s, LabelStyle: (%s)), "
            "Pressed: (Background: %s, LabelStyle: (%s)));") % (bg, lab % fg, hv, lab % fgh, pr, lab % fgh)
T["BSG"] = tbs("#27463a", "#3b6b54", "#172a22", "#dcffe8", "#ffffff")      # SkyySkills StatsPage button style
T["BSX"] = tbs("#262626", "#303030", "#1a1a1a", "#8a8a8a", "#b0b0b0")      # not possible right now (still clickable: reason shown)
T["BSOFF"] = tbs("#1d2c3c", "#2c4258", "#142030", "#b8c8d8", "#ffffff")
T["BSRED"] = tbs("#5a1e1e", "#7a2a2a", "#3a1414", "#ffd0d0", "#ffffff")
T["BTON"] = tbs("#3b6b54", "#4a8068", "#172a22", "#ffffff", "#ffffff")
T["BTOFF"] = T["BSOFF"]
for k in ("BSG", "BSX", "BSOFF", "BSRED", "BTON", "BTOFF"): assert '"' not in T[k] and "@" not in T[k]

F(page, "public int tree;")
F(page, "public int sel;")
F(page, "public String msg;")
F(page, "public int armT;")
F(page, "public long armAt;")
F(page, 'public static final String[] BG = new String[] { "#1c1414", "#16301f", "#10243d", "#3a3010" };')
F(page, 'public static final String[] HV = new String[] { "#2c2020", "#22462e", "#1a3a5e", "#54461a" };')
F(page, 'public static final String[] FG = new String[] { "#b07a68", "#9adf86", "#9cd8ff", "#ffc300" };')
F(page, "public static final java.util.concurrent.ConcurrentHashMap LASTTREE = new java.util.concurrent.ConcurrentHashMap();")
F(page, 'public static final String SOON_BG = "#1a1a24";')
F(page, 'public static final String SOON_HV = "#262634";')
F(page, 'public static final String SOON_FG = "#8890a0";')
C(page, r"""
public TreePage(@PR@ pr, int tree) {
  super(pr, @LIFE@.CanDismiss);
  this.tree = tree;
  this.sel = 1;
  this.msg = "";
  this.armT = -1;
  this.armAt = 0L;
}""")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""")
M(page, r"""
public static String cd(int i) {
  int k = @PKG@.TreeDefs.KIND[i];
  if (k == @K_VEIN@) return String.valueOf(@PKG@.TreeCfg.VEIN_CD_MS / 1000L);
  if (k == @K_FELLER@) return String.valueOf(@PKG@.TreeCfg.FELLER_CD_MS / 1000L);
  return "";
}""")
M(page, r"""
public static String text(int i, int eff) {
  if (@PKG@.TreeDefs.KIND[i] == @K_MASTER@) {
    if (eff <= 0) return "nothing yet";
    if (eff == 1) return "+1 Grade on every dish";
    return "+1 Grade on every dish and a " + @PKG@.TreeDefs.pct(@PKG@.TreeFx.value(i, eff)) + " chance of one more";
  }
  if (@PKG@.TreeDefs.KIND[i] == @K_FELLER@) {
    if (eff <= 0) return "nothing yet";
    if (eff >= @PKG@.TreeCfg.MAX[i]) return "Breaks every log of that tree on the same level (up to " + @PKG@.TreeCfg.FELLER_ALL + ")";
    long fn = Math.round(@PKG@.TreeFx.value(i, eff));
    return "Breaks " + fn + (fn == 1L ? " more log" : " more logs") + " beside it on the same level";
  }
  return @PKG@.TreeDefs.NOW[i].replace("%V", @PKG@.TreeDefs.valueText(i, @PKG@.TreeFx.value(i, eff))).replace("%C", cd(i));
}""")
M(page, r"""
public static String cardSub(@PKG@.TreeData d, int i, int stt, int lvl, long tokA) {
  int mx = @PKG@.TreeCfg.MAX[i];
  String off = d.off[i] ? " (off)" : "";
  if (stt == 3) return "MAX " + mx + off;
  if (stt == 2) return d.lv[i] + " / " + mx + off;
  if (stt == 1) { long n = (long) @PKG@.TreeCfg.TOK[i]; return "Unlock - " + n + @PKG@.TreeOps.tokensWord(n); }
  return @PKG@.TreeCalc.lockShort(d, i, lvl, tokA);
}""")
M(page, r"""
public static String stateLine(@PKG@.TreeData d, int i, int stt) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
  String off = d.off[i] ? " - turned off" : "";
  if (stt == 3) return "Maxed - level " + @PKG@.TreeCfg.MAX[i] + off;
  if (stt == 2) return "Owned - level " + d.lv[i] + " / " + @PKG@.TreeCfg.MAX[i] + off;
  if (stt == 1) return "Unlockable";
  return "Locked";
}""")
M(page, r"""
public static String nowLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
  if (d.lv[i] <= 0) return "Now: not unlocked";
  if (!@PKG@.TreeCfg.EN[i]) return "Now: turned off on this server";
  if (@PKG@.TreeDefs.KIND[i] == @K_SWING@ && !@PKG@.TreeCfg.SWING_ON) return "Now: turned off on this server (Faster tool swings is OFF)";
  if (d.off[i]) return "Now: turned off (no effect) - level kept";
  return "Now: " + text(i, @PKG@.TreeCalc.eff(d, i));
}""")
M(page, r"""
public static String nextLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "";
  int l = d.lv[i];
  if (l >= @PKG@.TreeCfg.MAX[i]) return "Next level: none - maxed";
  return (l == 0 ? "At level 1: " : "Level " + (l + 1) + ": ") + text(i, l + 1);
}""")
M(page, r"""
public static String costLine(@PKG@.TreeData d, int i) {
  if (@PKG@.TreeDefs.soon(i)) return "Cost: -";
  int l = d.lv[i];
  if (l >= @PKG@.TreeCfg.MAX[i]) return "Cost: -";
  if (l == 0) { long n = (long) @PKG@.TreeCfg.TOK[i]; return "Unlock cost: " + n + @PKG@.TreeOps.tokensWord(n); }
  return "Level " + (l + 1) + " costs " + @PKG@.TreeDefs.grp(@PKG@.TreeCalc.cost(i, l)) + " Dust";
}""")
M(page, r"""
public static String needLine(@PKG@.TreeData d, int i, int lvl, long tokA, long dustA) {
  if (@PKG@.TreeDefs.soon(i)) return "Draft - Skyy designs the rest of the " + @PKG@.TreeDefs.TREES[i / 12] + " tree later";
  int t = i / 12;
  String tn = @PKG@.TreeDefs.TREES[t];
  if (d.bad) return "Needs: your tree file to be fixed by an admin";
  int l = d.lv[i];
  if (l >= @PKG@.TreeCfg.MAX[i]) return "";
  if (!@PKG@.TreeCfg.EN[i]) return "Turned off on this server";
  if (tokA < 0L || dustA < 0L) return "Your balance is negative (costs changed) - respec to get everything back";
  if (l == 0) {
    if (lvl < 0) return "Needs: SkyySkills";
    int g = @PKG@.TreeCalc.gate(i);
    if (lvl < g) return "Needs: " + tn + " " + g + " (you are " + lvl + ")";
    int tier = @PKG@.TreeDefs.TIER[i];
    if (!@PKG@.TreeCalc.pathOk(d, t, tier)) return "Needs: a Tier " + @PKG@.TreeDefs.roman(tier - 1) + " node first";
    long need = (long) @PKG@.TreeCfg.TOK[i];
    if (tokA < need) return "Needs: " + need + @PKG@.TreeOps.tokensWord(need) + " - you have " + tokA + " (1 more every " + @PKG@.TreeCfg.TOK_EVERY + " levels)";
    return "";
  }
  long c = @PKG@.TreeCalc.cost(i, l);
  if (dustA < c) return "Needs: " + @PKG@.TreeDefs.grp(c - dustA) + " more Dust (1 per " + @PKG@.TreeCfg.rate(t) + " " + tn + " XP)";
  return "";
}""")
M(page, r"""
public static boolean canAct(@PKG@.TreeData d, int i, int stt, long tokA, long dustA) {
  if (d.bad || !@PKG@.TreeCfg.EN[i] || tokA < 0L || dustA < 0L) return false;
  int l = d.lv[i];
  if (l == 0) return stt == 1;
  return l < @PKG@.TreeCfg.MAX[i] && dustA >= @PKG@.TreeCalc.cost(i, l);
}""")
M(page, r"""
public static String buyText(@PKG@.TreeData d, int i, int stt, int lvl, long tokA, long dustA) {
  if (@PKG@.TreeDefs.soon(i)) return "Coming later";
  int l = d.lv[i];
  if (l >= @PKG@.TreeCfg.MAX[i]) return "MAX";
  if (d.bad) return "Unreadable file";
  if (tokA < 0L || dustA < 0L) return "Respec first";
  if (l == 0) {
    if (stt == 1) { long n = (long) @PKG@.TreeCfg.TOK[i]; return "Unlock - " + n + @PKG@.TreeOps.tokensWord(n); }
    if (@PKG@.TreeCfg.EN[i] && lvl >= 0 && lvl < @PKG@.TreeCalc.gate(i)) return "Need " + @PKG@.TreeDefs.TREES[i / 12] + " " + @PKG@.TreeCalc.gate(i);
    return @PKG@.TreeCalc.lockShort(d, i, lvl, tokA);
  }
  long c = @PKG@.TreeCalc.cost(i, l);
  if (dustA >= c) return "Level up - " + @PKG@.TreeDefs.fmt(c) + " Dust";
  return "Need " + @PKG@.TreeDefs.fmt(c - dustA) + " more Dust";
}""")
M(page, r"""
public static String note(java.util.UUID u, @PKG@.TreeData d, int t, int lvl, long tokA, long dustA) {
  if (d.bad) return "Your tree file could not be read - ask an admin (nothing is saved until it is fixed)";
  if (lvl < 0) return "Skill trees need SkyySkills - it is not loaded on this server";
  if (tokA < 0L || dustA < 0L) return "Costs changed - your balance is negative: effects keep working, buying is blocked, a respec is free right now";
  if (t == @T_EXPLORATION@) return (@PKG@.TreeCalc.skillKnown(u, t) ? "" : "Exploration levels need SkyySkills 0.4.1 - ") + "Draft tree - Skyy designs the rest later - nothing here boosts Exploration XP";
  if (!@PKG@.TreeCalc.hasXp()) return "Dust is estimated from your level until SkyySkills 0.4 (gather, XP and double-drop nodes need 0.4 too)";
  if (t == 3) return "Cooking nodes work when you cook at a Cooking Bench with SkyyCooking - Tokens unlock, Dust levels up";
  return "Tokens unlock nodes - Dust (1 per " + @PKG@.TreeCfg.rate(t) + " XP) levels them up - a respec gives everything back";
}""")
M(page, r"""
public static void line(@UCB@ b, String id, String text, String color, int size, boolean bold, int h) {
  b.appendInline("#SkyyTrDet", "Label #" + id + " { Anchor: (Height: " + h + "); Text: \"\"; Style: (FontSize: " + size + ", " + (bold ? "RenderBold: true, " : "") + "TextColor: " + color + ", VerticalAlignment: Center, Wrap: true); }");
  b.set("#" + id + ".Text", text == null ? "" : text);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int t = this.tree;
  if (t < 0 || t >= @PKG@.TreeDefs.NT) t = 0;
  int sl = this.sel;
  if (sl < 1 || sl > 12) sl = 1;
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  int lvl = @PKG@.TreeCalc.level(u, t);
  long[] bal = @PKG@.TreeCalc.balance(u, d, t, lvl);
  long tokA = bal[0] - bal[1];
  long dustA = bal[2] - bal[3];
  String tn = @PKG@.TreeDefs.TREES[t];
  String col = @PKG@.TreeDefs.TCOLOR[t];
  b.appendInline((String) null, "Group #SkyyTrRoot { Anchor: (Width: 1000, Height: 660); Background: #0b1524(0.96); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }");
  b.appendInline("#SkyyTrRoot", "Group #SkyyTrHead { Anchor: (Height: 36); LayoutMode: Left; }");
  for (int i = 0; i < @PKG@.TreeDefs.NT; i++) {
    b.appendInline("#SkyyTrHead", "TextButton #SkyyTrTab" + i + " { Anchor: (Width: 88, Height: 32); Text: \"" + @PKG@.TreeDefs.TREES[i] + "\"; " + (i == t ? "@BTON@" : "@BTOFF@") + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrTab" + i, @EVD@.of("a", "trtab" + i));
    b.appendInline("#SkyyTrHead", "Label { Anchor: (Width: 4, Height: 32); Text: \"\"; }");
  }
  b.appendInline("#SkyyTrHead", "Label #SkyyTrLvl { Anchor: (Width: 150, Height: 32); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + col + ", HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.appendInline("#SkyyTrHead", "Label #SkyyTrTok { Anchor: (Width: 140, Height: 32); Text: \"\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.appendInline("#SkyyTrHead", "Label #SkyyTrDust { Anchor: (Width: 128, Height: 32); Text: \"\"; Style: (FontSize: 13, RenderBold: true, TextColor: #c8a0ff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyTrLvl.Text", lvl < 0 ? "SkyySkills missing" : tn + " " + lvl);
  b.set("#SkyyTrTok.Text", "Tokens " + tokA + " of " + bal[0]);
  b.set("#SkyyTrDust.Text", "Dust " + @PKG@.TreeDefs.grp(dustA));
  b.appendInline("#SkyyTrRoot", "Label #SkyyTrNote { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 11, TextColor: #9fb8cc, VerticalAlignment: Center); }");
  b.set("#SkyyTrNote.Text", note(u, d, t, lvl, tokA, dustA));
  b.appendInline("#SkyyTrRoot", "Group { Anchor: (Height: 2); Background: " + col + "; }");
  b.appendInline("#SkyyTrRoot", "Group #SkyyTrBody { Anchor: (Height: 506); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline("#SkyyTrBody", "Group #SkyyTrGrid { Anchor: (Width: 630, Height: 502); LayoutMode: Top; }");
  for (int k = 6; k >= 1; k--) {
    int gate = @PKG@.TreeCfg.TIER_LV[k - 1];
    b.appendInline("#SkyyTrGrid", "Group #SkyyTrRow" + k + " { Anchor: (Height: 83); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyTrRow" + k, "Label #SkyyTrTier" + k + " { Anchor: (Width: 124, Height: 76); Text: \"\"; Style: (FontSize: 12, RenderBold: true, TextColor: " + (lvl >= gate ? "#9adf86" : "#b07a68") + ", VerticalAlignment: Center, Wrap: true); }");
    b.set("#SkyyTrTier" + k + ".Text", "Tier " + @PKG@.TreeDefs.roman(k) + " - " + tn + " " + gate);
    for (int s = 1; s <= 12; s++) {
      int i = t * 12 + s - 1;
      if (@PKG@.TreeDefs.TIER[i] != k) continue;
      int stt = @PKG@.TreeCalc.state(d, i, lvl, tokA);
      boolean so = @PKG@.TreeDefs.soon(i);
      String hv = so ? SOON_HV : HV[stt];
      String bg = s == sl ? hv : (so ? SOON_BG : BG[stt]);
      String fg = so ? SOON_FG : FG[stt];
      b.appendInline("#SkyyTrRow" + k, "Button #SkyyTrN" + s + " { Anchor: (Width: 158, Height: 76); Style: ButtonStyle( Default: ( Background: " + bg + " ), Hovered: ( Background: " + hv + " ), Disabled: ( Background: #141414 ) ); ItemIcon { Anchor: (Width: 44, Height: 44, Left: 6, Top: 16); ItemId: \"" + @PKG@.TreeDefs.ICON[i] + "\"; } Label { Anchor: (Left: 56, Top: 8, Width: 98, Height: 34); Text: \"" + safe(@PKG@.TreeDefs.NAME[i]) + "\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + fg + ", Wrap: true); } Label { Anchor: (Left: 56, Top: 46, Width: 98, Height: 22); Text: \"" + safe(cardSub(d, i, stt, lvl, tokA)) + "\"; Style: (FontSize: 10, TextColor: " + fg + "); } }");
      ev.addEventBinding(@BT@.Activating, "#SkyyTrN" + s, @EVD@.of("a", "trnode" + s));
      b.appendInline("#SkyyTrRow" + k, "Label { Anchor: (Width: 6, Height: 76); Text: \"\"; }");
    }
  }
  int i0 = t * 12 + sl - 1;
  int st0 = @PKG@.TreeCalc.state(d, i0, lvl, tokA);
  String fg0 = @PKG@.TreeDefs.soon(i0) ? SOON_FG : FG[st0];
  b.appendInline("#SkyyTrBody", "Label { Anchor: (Width: 12, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyTrBody", "Group #SkyyTrDet { Anchor: (Width: 330, Height: 498); Background: #101d30; Padding: (Horizontal: 10, Vertical: 8); LayoutMode: Top; }");
  b.appendInline("#SkyyTrDet", "Group #SkyyTrDetTop { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyTrDetTop", "Group { Anchor: (Width: 60, Height: 60); ItemIcon #SkyyTrDetIcon { Anchor: (Width: 52, Height: 52, Left: 2, Top: 4); ItemId: \"" + @PKG@.TreeDefs.ICON[i0] + "\"; } }");
  b.appendInline("#SkyyTrDetTop", "Label #SkyyTrDetName { Anchor: (Width: 246, Height: 60); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + fg0 + ", VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyTrDetName.Text", @PKG@.TreeDefs.NAME[i0] + "  (S" + sl + ")");
  line(b, "SkyyTrDetState", stateLine(d, i0, st0), fg0, 13, true, 24);
  line(b, "SkyyTrDetNow", nowLine(d, i0), "#dfe8f0", 12, false, 40);
  line(b, "SkyyTrDetNext", nextLine(d, i0), "#bfe8c8", 12, false, 40);
  line(b, "SkyyTrDetCost", costLine(d, i0), "#ffe08a", 12, false, 22);
  line(b, "SkyyTrDetNeed", needLine(d, i0, lvl, tokA, dustA), "#ffb080", 12, false, 40);
  line(b, "SkyyTrDetHow", @PKG@.TreeDefs.HOW[i0].replace("%C", cd(i0)).replace("%K", @PKG@.TreeFx.djKey()), "#8fa6ba", 11, false, 72);
  b.appendInline("#SkyyTrDet", "Label { Anchor: (Height: 10); Text: \"\"; }");
  boolean can = canAct(d, i0, st0, tokA, dustA);
  b.appendInline("#SkyyTrDet", "TextButton #SkyyTrBuy { Anchor: (Width: 306, Height: 36); Text: \"" + safe(buyText(d, i0, st0, lvl, tokA, dustA)) + "\"; " + (can ? "@BSG@" : "@BSX@") + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBuy", @EVD@.of("a", "trbuy"));
  b.appendInline("#SkyyTrDet", "Label { Anchor: (Height: 8); Text: \"\"; }");
  if (d.lv[i0] >= 1 && !@PKG@.TreeDefs.soon(i0)) {
    b.appendInline("#SkyyTrDet", "TextButton #SkyyTrToggle { Anchor: (Width: 306, Height: 32); Text: \"" + (d.off[i0] ? "Turn on" : "Turn off") + "\"; @BSOFF@ }");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrToggle", @EVD@.of("a", "trtoggle"));
  }
  b.appendInline("#SkyyTrRoot", "Group #SkyyTrFoot { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyTrFoot", "TextButton #SkyyTrBack { Anchor: (Width: 130, Height: 32); Text: \"< Skills\"; @BSG@ }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBack", @EVD@.of("a", "trback"));
  b.appendInline("#SkyyTrFoot", "Label { Anchor: (Width: 12, Height: 32); Text: \"\"; }");
  boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;
  b.appendInline("#SkyyTrFoot", "TextButton #SkyyTrRespec { Anchor: (Width: 220, Height: 32); Text: \"" + safe(armed ? "Click again to respec " + tn : "Respec " + tn) + "\"; " + (armed ? "@BSRED@" : "@BSOFF@") + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyTrRespec", @EVD@.of("a", "trrespec"));
  b.appendInline("#SkyyTrFoot", "Label { Anchor: (Width: 12, Height: 32); Text: \"\"; }");
  b.appendInline("#SkyyTrFoot", "Label #SkyyTrMsg { Anchor: (Width: 590, Height: 32); Text: \"\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyTrMsg.Text", this.msg == null ? "" : this.msg);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (data.indexOf("trback\"") >= 0) {
      if (!@PKG@.TreeCalc.hasSkills()) { this.msg = "SkyySkills is not installed - there is no skills page"; rebuild(); return; }
      @CMGR@.get().handleCommand(this.playerRef, "skills");
      return;
    }
    for (int i = 0; i < @PKG@.TreeDefs.NT; i++) {
      if (data.indexOf("trtab" + i + "\"") >= 0) {
        this.tree = i; this.sel = 1; this.msg = ""; this.armT = -1;
        LASTTREE.put(u, Integer.valueOf(i));
        rebuild();
        return;
      }
    }
    for (int s = 1; s <= 12; s++) {
      if (data.indexOf("trnode" + s + "\"") >= 0) { this.sel = s; this.msg = ""; rebuild(); return; }
    }
    int t = this.tree;
    if (t < 0 || t >= @PKG@.TreeDefs.NT) t = 0;
    int sl = this.sel;
    if (sl < 1 || sl > 12) sl = 1;
    if (data.indexOf("trbuy\"") >= 0) { this.msg = @PKG@.TreeOps.buy(this.playerRef, t, sl); rebuild(); return; }
    if (data.indexOf("trtoggle\"") >= 0) { this.msg = @PKG@.TreeOps.toggle(this.playerRef, t, sl); rebuild(); return; }
    if (data.indexOf("trrespec\"") >= 0) {
      long now = System.currentTimeMillis();
      if (this.armT == t && now - this.armAt <= 10000L) {
        this.armT = -1;
        this.msg = @PKG@.TreeOps.respec(this.playerRef, t);
      } else {
        this.armT = t;
        this.armAt = now;
        this.msg = "Click Respec again within 10 s to reset the whole " + @PKG@.TreeDefs.TREES[t] + " tree (everything spent comes back)";
      }
      rebuild();
      return;
    }
  } catch (Throwable e) { @PKG@.TreeCfg.warn("tree page event failed: " + e); }
}""")

# ================= 0.2.2: admin config kit (research/Server-Setup-Spec.md 4.10, tools/CONFIG-CONTRACT.md, tools/skyycfg.py) =========
# Every key TreeCfg.load reads is a row (asserted below), so a hand edit of any of them is noticed (logged via=file) and applied. Every row
# binds reload: the kit rewrites the one line, then runs TreeKit.reload (TreeCfg.load = the /tree reload loader, parse + clamp only, no
# world access) on the scheduler thread. The node lines are key-family tables, one per tree, whose entries ARE the file lines
# (<Id>.<field>): trees.properties keeps one line per node field, and a multi-column entry spread over several lines would need a
# custom: table (no hand-edit log, no History restore - CONFIG-CONTRACT "Known limits"). Ranges = the loader's clamps.
CFG_CATS = [("general", "General"), ("abilities", "Abilities"), ("nodes", "Nodes")]
NODE_HELP = "Entry = node id + field: max, per, B, tokens, enabled (+ base, items, crops). Removed = built-in."
CFG_NOTE = "Node ids and names: the comments in trees.properties. Hand edits: /tree reload or Reload file."
# (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
CFG_ROWS = [
    ("tier.levels", "Tier unlock levels", "general", "text", "1,10,20,30,45,60", "", "60", "", "", "live,danger",
     "Skill level that opens tiers I to VI: 6 whole numbers 0-1000, each at least the one before.", "reload;check=TreeKit.checkTiers"),
    ("tokens.first", "Tokens at skill level 1", "general", "int", "1", "0", "100", "", "", "live,danger",
     "Tokens a player has at level 1 of a skill; then 1 more every N levels (next row).", "reload"),
    ("tokens.every", "Levels per extra token", "general", "int", "5", "1", "100", "", "", "live,danger",
     "One more token every N levels. Fewer tokens can make a balance negative (a respec is then free).", "reload"),
    ("dust.xpPerDust", "Skill XP per Dust", "general", "int", "10", "1", "1000000000", "", "", "live,danger",
     "Dust = total skill XP / this, for every tree without its own rate (Dust rate per tree).", "reload"),
    ("dust.perTree", "Dust rate per tree", "general", "table", "", "1", "1000000000", "int;type;XP per Dust", "", "live,danger",
     "Entry = a tree name (Acrobatics). Removed: Acrobatics 2, Exploration 5, the others the rate above.",
     "reload@trees.properties:dust.xpPerDust.;check=TreeKit.checkDust"),
    ("respec.cooldownMinutes", "Respec cooldown per tree", "general", "int", "10", "0", "100000", "", "min", "live",
     "Minutes before a player can reset the same tree again. 0 = no wait.", "reload"),
    ("respec.coins", "Respec price", "general", "int", "0", "0", "1000000000000", "", "coins", "live",
     "Coins a respec costs (needs SkyyCoins). 0 = free. A negative balance always respecs for free.", "reload"),
    ("feedbackMs", "Tree bonus line every", "general", "int", "2000", "500", "600000", "", "ms", "live,adv",
     "The 'Tree bonus: ...' chat line is sent at most this often per player.", "reload"),
    ("debug.extraTokens", "Test: extra tokens", "general", "int", "0", "0", "1000", "", "", "live,danger,adv",
     "Testing only: extra tokens in every tree for every player. Keep 0 on a real server.", "reload"),
    ("debug.extraDust", "Test: extra Dust", "general", "int", "0", "0", "1000000000000000", "", "", "live,danger,adv",
     "Testing only: extra Dust in every tree for every player. Keep 0 on a real server.", "reload"),
    ("ability.disabledWorlds", "Abilities off in worlds", "abilities", "text", "", "", "2000", "", "", "live",
     "Comma list of world names where Spread, Vein Burst and Tree Feller never run (e.g. the hub).", "reload"),
    ("ability.maxRadius", "Ability reach", "abilities", "int", "6", "1", "16", "", "blocks", "live",
     "Sideways reach of Spread, Vein Burst and Tree Feller (also how high Vein Burst reaches).", "reload"),
    ("vein.cooldownSec", "Vein Burst cooldown", "abilities", "int", "40", "0", "86400", "", "s", "live",
     "Seconds between two Vein Bursts of one player.", "reload"),
    ("feller.cooldownSec", "Tree Feller cooldown", "abilities", "int", "3", "0", "86400", "", "s", "live",
     "Seconds between two Tree Fellers of one player. LOCKED 2026-09-25: 3 (was 5).", "reload"),
    ("feller.maxPerLayer", "Tree Feller max logs", "abilities", "int", "64", "1", "256", "", "", "live",
     "The max level breaks every log of the tree on the cut's level, up to this many.", "reload"),
    ("feller.needLeaves", "Tree Feller needs leaves", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: only wood that touches leaves (natural trees). Placed logs never count either way.", "reload"),
    ("feller.maxHeight", "Leaves check reach", "abilities", "int", "32", "1", "64", "", "blocks", "live",
     "How far above or below the cut the leaves check looks. Nothing up there is broken.", "reload"),
    ("felled.nodes", "Felled logs roll bonuses", "abilities", "bool", "true", "", "", "", "", "live",
     "Logs of a felled tree roll Sap Tapper, Replanter and Pocket Change (SkyySkills 0.4.2).", "reload"),
    ("swing.enabled", "Faster tool swings", "abilities", "bool", "true", "", "", "", "", "live",
     "ON: Mining / Chopping Speed shorten the wait between pickaxe / hatchet swings. OFF: they do nothing.", "reload"),
] + [("nodes." + _tn, _tn + " nodes", "nodes", "table", "", "", "", "text;type;Value", "", "live,danger", NODE_HELP,
      "reload@trees.properties:%s.;check=TreeKit.checkNode" % _tn) for _tn in TREES]
# every key of the default file is bound: exactly (a scalar row) or through a key family (dust.xpPerDust.<Tree>, <Tree>.<Id>.<field>)
_fams = ["dust.xpPerDust."] + [_tn + "." for _tn in TREES]
_exact = set(r[0] for r in CFG_ROWS if r[3] != "table")
for _k in CFG.parse_props(DEFAULTS):
    assert _k in _exact or any(_k.startswith(_p) for _p in _fams), "trees.properties key without a config row: " + _k
assert len(_exact) == 18 and len(CFG_ROWS) == 19 + len(TREES)   # 0.2.3: + swing.enabled (config:def 25 rows)
KIT = CFG.emit(pool, PKG, MOD="SkyyTrees", TITLE="Trees", VERSION=VERSION, NODE="skyytrees.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=["Skyy_SkyyTrees/trees.properties"], NOTE=CFG_NOTE, RELOAD="TreeKit.reload", KEEP=20,
               DEFAULTS={"trees.properties": DEFAULTS}, ITEMS=ITEM_IDS)

# TreeKit: the kit's hooks (check=, the reload routine) and /tree reload. Hooks never throw (the kit also catches) and never touch a
# world; check= answers null = fine, text = refuse, "?text" = ask first (spec 1.4.2). Checks mirror TreeCfg.apply: the same parse
# (Long.parseLong / Double.parseDouble / true|false) and the same ranges, so a value the page accepts is a value the loader uses.
kitc = pool.makeClass(PKG + ".TreeKit")
M(kitc, r"""
public static String entryOf(String key) {
  if (key == null) return null;
  int b = key.indexOf('[');
  if (b < 0 || !key.endsWith("]")) return null;
  return key.substring(b + 1, key.length() - 1).trim();
}""")
M(kitc, r"""
public static String tableOf(String key) {
  if (key == null) return "";
  int b = key.indexOf('[');
  return b < 0 ? key : key.substring(0, b);
}""")
M(kitc, r"""
public static String wholeIn(String v, long lo, long hi, String what) {
  long x = 0L;
  try { x = Long.parseLong(v.trim()); } catch (Throwable t) { return what + " must be a whole number from " + lo + " to " + hi + " (plain digits)."; }
  if (x < lo || x > hi) return what + " must be a whole number from " + lo + " to " + hi + ".";
  return null;
}""")
M(kitc, r"""
public static String numIn(String v, double lo, double hi, String what) {
  double x = 0.0;
  try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { return what + " must be a number from " + @PKG@.TreeDefs.num(lo) + " to " + @PKG@.TreeDefs.num(hi) + " (with a dot, like 0.02)."; }
  if (Double.isNaN(x) || Double.isInfinite(x) || x < lo || x > hi) return what + " must be a number from " + @PKG@.TreeDefs.num(lo) + " to " + @PKG@.TreeDefs.num(hi) + ".";
  return null;
}""")
# the asset map is always there in a running server; if it cannot be asked (not loaded yet) the id is accepted - TreeAbil.itemOk checks
# every id again before anything is given and warns once about an unknown one
M(kitc, r"""
public static boolean itemExists(String id) {
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return true; }
}""")
M(kitc, r"""
public static String listCheck(String v, boolean crops) {
  String[] xs = @PKG@.TreeCfg.split(v);
  if (xs.length == 0) return "List at least one " + (crops ? "crop" : "item id") + " - to stop the node, set its enabled entry to false.";
  for (int k = 0; k < xs.length; k++) {
    String x = xs[k];
    if (crops) { if (!itemExists("Plant_Crop_" + x + "_Block")) return "Unknown crop: " + x + " (there is no Plant_Crop_" + x + "_Block block)."; }
    else if (!itemExists(x)) return "Unknown item: " + x + ".";
  }
  return null;
}""")
# percent nodes (their page value is a %): per above 1 is more than 100% per level - allowed (the loader takes up to 1000), asked first
M(kitc, r"""
public static boolean fraction(int kd) {
  return kd != @K_HP@ && kd != @K_STA@ && kd != @K_RJMP@ && kd != @K_VEIN@ && kd != @K_FELLER@ && kd != @K_SOON@;
}""")
# 0.2.3 SWING nodes (Mining Speed / Chopping Speed): per x max above 0.40 = beyond the +40% the assets allow - asked first (spec 5)
M(kitc, r"""
public static String swingAsk(int i, double per, double max) {
  double tot = per * max;
  if (tot <= 0.40 + 0.000001) return null;
  return "?" + @PKG@.TreeDefs.NAME[i] + " would reach +" + @PKG@.TreeDefs.num(tot * 100.0) + "% - swings are capped at +40% (then they are back to back). Save it anyway?";
}""")
M(kitc, r"""
public static String checkTiers(String key, String value) {
  if (value == null) return null;
  String[] xs = @PKG@.TreeCfg.split(value);
  if (xs.length != 6) return "Needs exactly 6 whole numbers, like 1,10,20,30,45,60 (tiers I to VI).";
  int prev = 0;
  for (int i = 0; i < 6; i++) {
    int v = -1;
    try { v = Integer.parseInt(xs[i]); } catch (Throwable t) { return xs[i] + " is not a whole number - use 6 numbers like 1,10,20,30,45,60."; }
    if (v < 0 || v > 1000) return "Each tier level must be 0 to 1000 (tier " + @PKG@.TreeDefs.roman(i + 1) + " is " + v + ").";
    if (i > 0 && v < prev) return "Tier " + @PKG@.TreeDefs.roman(i + 1) + " (" + v + ") must not be below tier " + @PKG@.TreeDefs.roman(i) + " (" + prev + ").";
    prev = v;
  }
  return null;
}""")
M(kitc, r"""
public static String checkDust(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (e == null) return null;
  for (int t = 0; t < @PKG@.TreeDefs.NT; t++) if (@PKG@.TreeDefs.TREES[t].equals(e)) return null;
  return "?" + e + " is not a tree (Mining, Foraging, Farming, Cooking, Acrobatics, Exploration - capitals matter), so this line would do nothing. Save it anyway?";
}""")
M(kitc, r"""
public static String checkNode(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (e == null) return null;
  String tk = tableOf(key);
  String tn = tk.startsWith("nodes.") ? tk.substring(6) : tk;
  int t = -1;
  for (int k = 0; k < @PKG@.TreeDefs.NT; k++) if (@PKG@.TreeDefs.TREES[k].equals(tn)) t = k;
  if (t < 0) return null;
  int dot = e.lastIndexOf('.');
  String id = dot > 0 ? e.substring(0, dot) : e;
  String f = dot > 0 ? e.substring(dot + 1) : "";
  int i = -1;
  String near = null;
  for (int s = 0; s < 12; s++) {
    int j = t * 12 + s;
    if (@PKG@.TreeDefs.ID[j].equals(id)) i = j;
    else if (@PKG@.TreeDefs.ID[j].equalsIgnoreCase(id)) near = @PKG@.TreeDefs.ID[j];
  }
  if (i < 0) {
    if (near != null) return "?" + e + " does nothing - capitals matter, the node is " + near + " (" + near + "." + f + "). Save it anyway?";
    return "?" + id + " is not a " + tn + " node (the ids are in trees.properties, like " + @PKG@.TreeDefs.ID[t * 12] + ") - this line would do nothing. Save it anyway?";
  }
  if (@PKG@.TreeDefs.soon(i)) return "?" + id + " is a Coming later slot and always off - this line does nothing. Save it anyway?";
  int kd = @PKG@.TreeDefs.KIND[i];
  boolean hasBase = kd == @K_VEIN@ || kd == @K_FELLER@ || kd == @K_DJUMP@;
  String lk = @PKG@.TreeDefs.LISTKEY[i];
  String nm = @PKG@.TreeDefs.NAME[i] + " " + f;
  if (f.equals("max")) {
    String rm = wholeIn(value, 1L, 100L, nm);
    if (rm != null || kd != @K_SWING@) return rm;
    return swingAsk(i, @PKG@.TreeCfg.PER[i], (double) Long.parseLong(value.trim()));
  }
  if (f.equals("B")) return wholeIn(value, 0L, 1000000000L, nm);
  if (f.equals("tokens")) return wholeIn(value, 0L, 100L, nm);
  if (f.equals("per")) {
    String r = numIn(value, 0.0, 1000.0, nm);
    if (r != null) return r;
    double x = Double.parseDouble(value.trim());
    if (kd == @K_SWING@) return swingAsk(i, x, (double) @PKG@.TreeCfg.MAX[i]);
    if (fraction(kd) && x > 1.0) return "?" + nm + " " + value.trim() + " is " + @PKG@.TreeDefs.pct(x) + " per level (0.02 = 2%). Save it anyway?";
    return null;
  }
  if (f.equals("enabled")) {
    String b = value.trim();
    if (b.equalsIgnoreCase("true") || b.equalsIgnoreCase("false")) return null;
    return nm + " must be true or false.";
  }
  if (f.equals("base")) {
    if (hasBase) return numIn(value, 0.0, 1000.0, nm);
    return "?Only Vein Burst, Tree Feller and Double Jump use base - " + e + " does nothing. Save it anyway?";
  }
  if (lk.length() > 0 && f.equals(lk)) return listCheck(value, lk.equals("crops"));
  return "?" + f + " is not a field of " + id + " (max, per, B, tokens, enabled" + (hasBase ? ", base" : "") + (lk.length() > 0 ? ", " + lk : "") + ") - this line would do nothing. Save it anyway?";
}""")
# RELOAD (kit.write checks it): after every kit write, and for every hand edit the kit notices
M(kitc, r"""
public static void reload() {
  @PKG@.TreeCfg.load();
  @PKG@.TreeAbil.ITEMOK.clear();
}""")
# /tree reload: the 0.2.1 re-read (item-id cache, unreadable player files, TreeCfg.load and its summary), then the kit's reload op, which
# logs every value changed by hand (via=file) and, when it found any, queues the reload routine once more on the save task (harmless:
# TreeCfg.load is synchronized and re-parses the same file into the same values). The direct TreeCfg.load stays on purpose: it keeps the
# 0.2.1 reply (the loader summary) and applies the file even when the kit has nothing new to merge.
M(kitc, r"""
public static String reloadCmd(@PR@ pr) {
  @PKG@.TreeAbil.ITEMOK.clear();
  int bad = @PKG@.TreeStore.dropBad();
  String sum = @PKG@.TreeCfg.load();
  String k = "";
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
    if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) k = " " + String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { k = ""; }
  return "[Trees] trees.properties reloaded: " + sum + (bad > 0 ? "; " + bad + " unreadable player file(s) will be read again" : "") + "." + k;
}""")

# ================= commands (HANDOFF command rules) =================
def open_body(tree_expr):
    return r"""
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    int t = """ + tree_expr + r""";
    @PKG@.TreePage.LASTTREE.put(pr.getUuid(), Integer.valueOf(t));
    player.getPageManager().openCustomPage(ref, store, new @PKG@.TreePage(pr, t));
  } catch (Throwable e) {
    @PKG@.TreeCfg.warn("/tree failed: " + e);
    pr.sendMessage(@MSG@.raw("[Trees] could not open the tree page"));
  }"""
F(vcmd, "public @RA@ skillArg;")
C(vcmd, r"""
public TreeSkillCmd() {
  super("Open one skill tree: /tree mining | foraging | farming | cooking | acrobatics | exploration");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | cooking | acrobatics | exploration", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(vcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  int want = @PKG@.TreeDefs.tree(String.valueOf(ctx.get(this.skillArg)));
  if (want < 0) { pr.sendMessage(@MSG@.raw("[Trees] Unknown tree - use /tree mining, foraging, farming, cooking, acrobatics or exploration").color("#ff9090")); return; }
""" + open_body("want") + "\n}")
C(qcmd, r"""
public TreeQuietCmd() {
  super("quiet", "Toggle the 'Tree bonus' chat line (more switches: /settings)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(qcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw(@PKG@.TreeOps.quietText(pr)));
}""")
C(rcmd, r"""
public TreeReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyTrees/trees.properties");
  requirePermission("skyytrees.admin");
  setPermissionGroups(new String[0]);
}""")
M(rcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyytrees.admin")) { pr.sendMessage(@MSG@.raw("[Trees] no permission (skyytrees.admin)")); return; }
  pr.sendMessage(@MSG@.raw(@PKG@.TreeKit.reloadCmd(pr)));
}""")
C(scmd, r"""
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
C(cmd, r"""
public TreesCmd() {
  super("tree", "Open your skill trees: /tree, /tree mining | foraging | farming | cooking | acrobatics | exploration, /tree quiet");
  addAliases(new String[] { "trees" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addUsageVariant(new @PKG@.TreeSkillCmd());
  addSubCommand(new @PKG@.TreeQuietCmd());
  addSubCommand(new @PKG@.TreeReloadCmd());
  addSubCommand(new @PKG@.TreeSwingCmd());
}""")
M(cmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  Object last = @PKG@.TreePage.LASTTREE.get(pr.getUuid());
  int lt = last instanceof Integer ? ((Integer) last).intValue() : 0;
""" + open_body("lt") + "\n}")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyTreesPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.TreeCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyTrees");
  @PKG@.TreeStore.DIR = base.resolve("players");
  @PKG@.TreeCfg.FILE = base.resolve("trees.properties");
  String sum = @PKG@.TreeCfg.load();
  getEntityStoreRegistry().registerSystem(new @PKG@.TreeDmgSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.TreeTick());
  getCommandRegistry().registerCommand(new @PKG@.TreesCmd());
  java.util.Map b = @PKG@.TreeStore.bridge();
  @PKG@.TreeStore.FN = new @PKG@.TreeFn();
  @PKG@.TreeStore.BFN = new @PKG@.TreeBonusFn();
  b.put("tree:fn:level", @PKG@.TreeStore.FN);
  b.put("tree:fn:bonus", @PKG@.TreeStore.BFN);
  b.put("tree:names", @PKG@.TreeDefs.NAMES_CSV);
  @PKG@.TreeGather.INSTANCE = new @PKG@.TreeGather();
  @PKG@.TreeGather.FELLED = new @PKG@.TreeFelledFn();
  @PKG@.TreeGather.ensure();
  try {
    Object pv = b.putIfAbsent("move:proto", Integer.valueOf(1));
    if (pv instanceof Number && ((Number) pv).intValue() != 1) @PKG@.TreeCfg.warn("another mod speaks movement protocol " + pv + ", SkyyTrees speaks 1 - tool speed nodes may not apply");
  } catch (Throwable t) { }
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.TreeSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  String sk = @PKG@.TreeCalc.hasSkills() ? (@PKG@.TreeCalc.hasXp() ? "SkyySkills trees bridge found" : "SkyySkills found without the trees bridge (0.4 needed for Dust, gather, XP and double-drop nodes)") : "SkyySkills not loaded yet (trees read it at use time)";
  @PKG@.TreeStore.regSetting("trees.bonus", "Tree bonus totals", "cooking", true, "Tree bonus: +2 Copper Ore, extra drops x1, +3 coins");
  @PKG@.TreeStore.regSetting("trees.abilities", "Vein Burst and Tree Feller", "cooking", true, "Vein Burst! +6 ore (ready again in 40 s)");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyTrees] @VERSION@ ready - /tree; " + sum + "; " + sk + "; server settings: SkyWynn Menu -> Server Setup -> Trees");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@VERSION@", VERSION))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.TreeStore.flushDirty(); } catch (Throwable t) { }
  try { if (!@PKG@.TreeStore.DIRTY.isEmpty()) @PKG@.TreeStore.flushDirty(); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.TreeStore.bridge();
    if (@PKG@.TreeStore.FN != null) b.remove("tree:fn:level", @PKG@.TreeStore.FN);
    if (@PKG@.TreeStore.BFN != null) b.remove("tree:fn:bonus", @PKG@.TreeStore.BFN);
    b.remove("tree:names", @PKG@.TreeDefs.NAMES_CSV);
  } catch (Throwable t) { }
  try { @PKG@.TreeGather.unregister(); } catch (Throwable t) { }
  try { @PKG@.TreeFx.clearAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

ALL = (defs, cfg, dat, sto, stk, calc, fx, swg, msg, abil, gat, tfn, bfn, ffn, dmg, tick, svr, ops, page, kitc, vcmd, qcmd, rcmd, scmd, cmd, pl)
for c in ALL:
    c.writeFile(OUT)
KIT.write(OUT)   # deferred kit checks (TreeKit hooks + reload routine exist with the right signatures), then the 7 Cfg* classes
print("classes written:", len(ALL) + 7)

jar = os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)
m = B.manifest("SkyyTrees", VERSION, "SkyWynn skill trees (Heart of the Mountain style) for Mining, Foraging, Farming, Cooking, Acrobatics and Exploration (draft): tokens from your skill level unlock nodes, Dust from your skill XP levels them. Pickaxe / hatchet swing speed, breaking power, double drops, XP, max health / stamina, gems, bars, saplings, seeds, extra drops, coins, tool speed, Spread, Vein Burst, Tree Feller, the Cooking bonuses SkyyCooking reads, move speed / jump / fall damage / dodge push / Double Jump and the chest luck SkyyExploration reads. Free respec. /tree. Per profile with SkyyProfiles (optional). Server settings editable in game (SkyyMenu 0.3 Server Setup). Reads SkyySkills through the skyy bridge; zero dependencies.", PKG + ".SkyyTreesPlugin")
assert m["IncludesAssetPack"] is True   # 0.2.3: the jar carries the swing-speed asset pack (the page is still built inline)
B.assemble(jar, m, OUT, SWING_FILES)
if "--deploy" in sys.argv:   # only with Skyy's deploy OK (HANDOFF section 3); workflows never pass it
    B.deploy(jar, "SkyyTrees.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyTrees" % VERSION, disable_prefix="Skyy:")
