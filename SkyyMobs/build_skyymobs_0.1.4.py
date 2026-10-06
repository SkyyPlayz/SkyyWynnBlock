"""SkyyMobs 0.1.4 - build script (javassist via jpype). A copy of the SET pin build_skyymobs_0.1.3.py (0.1.3 stays untouched; SkyyMobs has
no patch scripts) with the SkyyMobs part of research/Mob-Curve-Spec.md (every default accepted by Skyy 2026-10-05, docs/answered/mobs.md):
the Wynncraft-style Level curve, the BRUTAL level gap both directions, the damage floor / one hit at most rows (off), Fixed level by role,
mob:fn:info for SkyySkills' kill XP, the one-time update MobMig14. Everything else is 0.1.3's (its notes follow).
Run:   python SkyyMobs/build_skyymobs_0.1.4.py        -> SkyyMobs/SkyyMobs-0.1.4.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
       --set-file <copy of deploy_set.py inside tools/dev/scratch> --check-set = run only the pairing guard on that copy (verification)
Test:  python SkyyMobs/test_skyymobs_0.1.4.py         (bare JVM, -Xverify:all; scratch tools/dev/scratch/mc-mobs/harness; reads
       SkyyMobs-0.1.3.jar (O / Z / CU), 0.1.2 (NQ), 0.1.1 (Q / FL / U2), 0.1 (U2 / V / MIG) and SkyyMenu/SkyyMenu-0.3.5.jar, all read-only)

PAIRING (spec 7.1, renumbered for 2026-10-06): deploy and roll back ALL THREE together - SkyyMobs 0.1.4 + SkyyGear 0.2.5 (the gear curves,
gear:fn:curve) + SkyySkills 0.4.17 (kill XP by mob level through mob:fn:info). This build STOPS when tools/deploy_set.py pins SkyyMobs 0.1.4
with SkyyGear below 0.2.5 or SkyySkills below 0.4.17 (pair_problem below; the main session adds the same STOP to deploy_set.py).

0.1.4 CHANGES (spec sections 1, 3, 6.1, 6.4, 7.2, 7.3)
  1. STRENGTH SHAPE (new row strength.shape, choice curve "Level curve" | linear "Per level", default curve, live + confirm). Per level =
     0.1.3's maths with the caps, byte for byte (hpMult / dmgMult keep 0.1.3's code after a first "if (CURVE_ON) return curveMult(...)" -
     the harness compares it instruction for instruction). Level curve: health multiplier = the difficulty's health table at the level,
     damage = its damage table (8 key-family tables curve.<hp|dmg>.<easy|normal|hard|custom>.<level>=<factor>, Server Setup -> Mobs ->
     Level curve, one "Open - 10 entries" row each; straight lines between points, flat outside them = SkyyGear's GearBase.eval). The
     caps do not apply in curve shape; the health floor still goes on top. Defaults = the spec's section 1.3 block (Custom = Hard's
     copies); every Lv 1-20 point lies on 0.1.3's preset line, so Lv 1-20 plays exactly like today (float-exact vs SkyyMobs-0.1.3.jar).
     THE RULE: same-level fights play like 0.1.3's preset at every level (health x F_new / F_old, damage x player HP_new / HP_old).
     A file without strength.shape (0.1.3's, or a failed update) loads Per level for Difficulty Custom, else Level curve (= the update's
     decision table). A table with no valid line uses its default points (one WARN); the last entry of a table cannot be removed in game.
     The health signature (live re-apply, 0.1.2) now = shape + the ACTIVE health table (curve) or 0.1.3's % / cap (linear) + floor +
     the scale.role rows: a table edit with levelled mobs in view re-applies at once (health percent kept); damage tables stay live.
     /mobs inspect: "Health x7.94 (1795 / 1795 HP) ... damage x3.72 - Hard curve, Lv 34"; the ready line names the shape.
  2. LEVEL GAP (new tab Level gap: part.gap, gap.free 5, gap.dealtStep 2.5 %, gap.dealtMin 40 %, gap.takenStep 1.5 %, gap.takenMax x1.5).
     d = mob level - the player's class weapon skill (class:skill:<uuid> + skill:fn:level, cached 2 s per player in MobGap; level 0 =
     unknown = no gap and never overwrites a cached good level; no class = no gap). d > free: the player's hits x max(dealtMin, 1 -
     dealtStep (d - free)) in the NEW GapDamage (DamageEventSystem, Filter group, BEFORE ArmorDamageReduction; attacker = a player -
     PlayerRef on the source ref, a projectile counts as its shooter - victim = a levelled mob; cancelled hits skipped; GapDamageU = the
     unordered fallback, the LevelDamageU pattern) and the mob's hits on a player x min(takenMax, 1 + takenStep (d - free)) in
     LevelDamage. Mob vs mob / pet, pets / summons vs mobs, player vs player, unlevelled mobs: no gap. /mobs inspect adds "Level gap vs you
     +13: you deal 80%, it deals 112%"; /mobs info adds " - level gap: you deal 83-93%, they hit you for 105-111%" for a band above you.
  3. LevelDamage for a PLAYER victim (spec 3.3 order): damage floor (strength.dmgFloor %, default 0 = off: at least this % of the mob's Lv 1
     health = max(own base, health floor), only above Lv 20, ramped (L - 20) / 10 at Lv 21-29) -> x the level multiplier -> x taken(d) ->
     one hit at most (strength.hitCap %, default 0 = off: at most this % of the victim's max Health). Every other victim: 0.1.3 exactly.
     The Lv <= 1 early return stays.
  4. FIXED LEVEL BY ROLE (new table scale.role on the Which mobs tab, empty by default - the boss round fills it): a matching role always
     gets that level (checked before the saved level in MobLevel.onAdd; wins over Never level these, the lists and the attitude; levels.max
     still caps it), its health x on top of the curve (setMult / refreshOne take the factor; MobInfo.rx), plate / gap / kill XP like any
     levelled mob; level 0 = off; a changed row re-stamps the saved level on the next add; a removed row strips the excluded mob on its next
     add. The kit refuses * in a plain key table entry, so Server Setup takes exact role ids; a Prefix* line typed into the file still works.
  5. mob:fn:info (bridge, any thread, never throws): Object[]{String world, UUID npc} (or a bare UUID; world may be null) -> Object[]{
     Integer level, Double base, Double xpBase, Double hpMult, Double dmgMult, Double xpMult} or null (no level / unknown / wrong world /
     base unknown). base = own max health before our multiplier (MobLevel.baseOf at apply / re-apply), xpBase = max(base, health floor),
     hpMult = the level multiplier now (no floor factor) x the scale.role Health x, dmgMult = now, xpMult = min(1, hpMult(level) /
     hardRef(level)) - hardRef = the Hard health table (curve) or min(hpCap, 1 + 8 % (L - 1)) (Per level), float-rounded like hpMult so
     Hard / Hard = exactly 1. mob:fn:level unchanged. Removed on shutdown.
  6. MobMig14 - the one-time update (spec 6.4, PROJECT-RULES 4): a config.properties without the marker "SkyyMobs 0.1.4 level curve" gets,
     right after its LAST strength.* entry, the marker + strength.shape + strength.dmgFloor=0 + strength.hitCap=0 + the 8 tables (80 lines)
     + the 6 gap rows, each with a comment line, and the scale.role comment after levels.max; a key / table family already in the file
     (any case) is kept and named. strength.shape = linear for Difficulty custom (no log line), else curve + ONE config-changes.log line
     "strength.shape linear -> curve" (SkyyMobs 0.1.4, update) = Server Setup -> Changes -> Undo back to 0.1.3's numbers. Only lines are
     ADDED (Properties check: every old key keeps its value + exactly the new keys); verified History copy "before the 0.1.4 level curve"
     first; atomic write; line endings kept (new lines take the CR of the line they follow). Never touched: difficulty, hp, dmg, both caps
     (hand-set caps are named in the INFO line: inert in curve shape), floor, bands, plates. Skyy's live file (hard, hp 20 / dmg 8, caps
     20 / 6, LF) -> shape curve, Hard tables, + 89 lines, 1 Undo line. The fresh 0.1.4 default file = 0.1.3's default with exactly this
     block (and its version line), so it is never updated.
     FIXER 2 (2026-10-06, recheck finding 1): when the anchor entry (the last strength.* entry, levels.max, or - with no strength.* entry -
     the file's last entry) reaches the file's last line still open (odd trailing backslashes, or it swallowed the final newline), the new
     lines go BEFORE that entry's first line (SkyyGear's chAfter / chEnd rule) - appended, they became its continuation and sameAfter
     refused the update on every start. Harness MIG-OPEN executes it.
  7. The 15 s scan (MobScanTask) also WARNs once when shape = curve and SkyyGear's gear:fn:curve is missing or F(40) < 2 x F(20), and when
     shape = linear and F(40) >= 2 x F(20). Manifest: "No dependencies (the Level curve is made for SkyyGear's gear curves; use Per level
     without SkyyGear)". Engine members probed: + ArchetypeChunk.getReferenceTo, PlayerRef.getComponentType, Damage$ProjectileSource
     (a subclass of Damage$EntitySource - asserted).

CHECKED 2026-10-06 (0.1.4; re-run before a deploy - the harness is the source of truth, not this text):
  build: 118 engine members probed (exact descriptors), 36 classes (7 kit; 0.1.3's 31 + GapDamage, GapDamageU, MobGap, MobInfoFn, MobMig14);
  Server Setup fit: 321 texts (6 tabs, 128 row names + 128 help lines, 11 choice buttons, 28 table buttons) fit SkyyMenu 0.3.5's boxes with
  8 px to spare, the draft's "Per-level %" fails the same measure (negative control); "assembled ...SkyyMobs-0.1.4.jar 140738 bytes".
  python tools/ci/lint.py: 0 fails (26 warnings, all SkyySacks 0.7.13); lint --perm on this script: 0 fails; tools/skyycfg_test.py: PASS;
  tools/deploy_set.py --check: all 28 jars present (SkyyMobs pinned 0.1.3, 0.1.4 newer on disk).
  python SkyyMobs/test_skyymobs_0.1.4.py: 13812 ok, 0 fail - every 0.1 - 0.1.3 section against this jar in Per level shape (A 36 classes
  -Xverify:all, NQ 3000 sweep changes, AX 8030 references 0 refused, L 198 engine refs in release + 0.7 pre-release, 0 missing) + O / Z
  (0.1.3 -> 0.1.4: 20 entries byte-identical, the Per level code instruction for instruction) + CU / CU-K / GP / DM / SR / IF / WN / CMD
  / MIG (Skyy's live folder copied: + 89 lines, shape curve, 1 Undo line, second start no change) / SET (the pairing STOP).
UNVERIFIED (0.1.4, needs the game): the gap's class level read per hit (bridge call, cached 2 s) and GapDamage's order against the
  other Filter multipliers on a real server (all multipliers: order-free in the harness, not run with the real SkyyGear / SkyySkills /
  SkyyArmory systems together - cross-check); mob:fn:info at the DeathComponent (the MOBS entry lifetime SkyySkills already uses for
  mob:fn:level); real fight pacing (the spec's tables are a model); the live re-apply on a table edit with mobs in view (0.1.2 / 0.1.3's
  path, harness-proven on stand-ins); Server Setup drawing the new tabs / 8 table rows (measured against SkyyMenu 0.3.5's boxes).

0.1.3 NOTES (the version this copies)
SkyyMobs 0.1.3 - build script (javassist via jpype). A copy of the SET pin build_skyymobs_0.1.2.py (0.1.2 stays untouched; SkyyMobs
has no patch scripts) with ONE fix from the 0.1.2 cross-check (F1, medium-low; CONFIRMED IN GAME by Skyy on 2026-10-03): after a live
health re-apply the client could keep the old max health. Nothing else changed: every number, setting, text, file and saved byte is
0.1.2's (the 0.1.2 notes follow).
Run:   python SkyyMobs/build_skyymobs_0.1.3.py        -> SkyyMobs/SkyyMobs-0.1.3.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyMobs/test_skyymobs_0.1.3.py         (bare JVM, -Xverify:all; scratch tools/dev/scratch/mobs013/harness; reads
       SkyyMobs-0.1.2.jar (the 0.1.2 -> 0.1.3 compares + 0.1.2's network queue), SkyyMobs-0.1.1.jar (floor 0 = 0.1.1), SkyyMobs-0.1.jar
       (the one-time 0.1 -> 0.1.1 update still ships) and SkyyMenu/SkyyMenu-0.3.5.jar (the label check), all read-only)

0.1.3 CHANGE (the harness byte-compares every class against 0.1.2: only MobLevel's code changed, plus the version constants)
  SKYY'S REPORT (2026-10-03 evening): Server Setup -> Mobs -> Strength Hard -> Custom 20% / 8%, caps 20 / 6 with Yetis loaded nearby;
  /mobs inspect: "[Lv 32] Yeti - Health x7.2 (1627 / 1627 HP), base 226 HP, damage x3.48"; "the second one i tried took like 8 hits,
  but its hp bar looked empty long before it died". The server had 1627 HP, the client kept the Hard max (x3.48 = 786 HP), so its bar
  was empty after ~4 of the 8 hits (harness section NQ replays exactly this on real engine objects).
  THE BUG (engine bytecode; release = 0.7 pre-release): a health modifier change queues a PutModifier / RemoveModifier entry for the
  players who already see the mob (EntityStatMap.otherUpdates, sent by EntityStatsSystems$EntityTrackerUpdate; a player who starts
  seeing the mob gets its whole state instead). setStatValue / maximizeStatValue in the SAME tick go through
  EntityStatMap.tryMergeUpdate, which REWRITES the last pending entry of that stat into the Set / Maximize (its op and value; only a
  Remove entry is never merged into, an Init entry keeps its op). 0.1.2's live re-apply (refreshOne -> setMult: put the new amount,
  then setStatValue(share)) therefore sent those players a plain Set: their client kept the old max while the server's health, damage,
  kill XP and /mobs inspect were right. The same merge hit /mobs set N (RemoveModifier + Set: the client lost the new modifier),
  /mobs set 0 (a Set only: the client kept the old one) and /mobs set with strength.healOnLoad on (RemoveModifier + Maximize).
  THE FIX: one helper, MobLevel.writeValue(m, hi, target), writes the health after a modifier change with minStatValue(hi, target)
  when the target is below the current health (the max went down) and maxStatValue(hi, target) when it is above (the max went up, or
  removeOurs clamped the health while the old key was off); equal = no write (setStatValue would queue nothing either).
  tryMergeUpdate never merges Min / Max entries (it appends them), so the PutModifier / RemoveModifier entries survive next to them:
  the client gets the new max first, then the value (a later Set-type write in the same tick merges into OUR Min / Max entry; vanilla's
  damage / regen writes are Adds, appended). The server ends EXACTLY where 0.1.2 put it (min(cur, t) = t below cur, max(cur, t) = t
  above, the same shouldSuppressChange test and EntityStatValue.set clamp as setStatValue): the health PERCENT is kept, a hurt mob is
  never healed, a 0-HP mob is never touched by the live re-apply (refreshOne skips it), a living mob is never killed. setMult writes its
  share with it (0.1.2: setStatValue) and its full / heal value (0.1.2: maximizeStatValue -> writeValue(the new max)); stripStats writes
  its share with it. Spawns and chunk loads end the same as in 0.1.2 (no player sees that mob yet). Engine members probed:
  minStatValue / maxStatValue (int, float) replace setStatValue / maximizeStatValue (no longer referenced anywhere in the jar). No
  setting, text, file key, saved byte or Server Setup row changed.
  LIMITS: a full mob whose max went DOWN needs no value entry (the server clamps it; the client clamps on the modifier entry itself, as
  vanilla's armor Health modifiers need - StatModifiersManager puts / removes them with no value entry); in that one case a Set-type
  write by another system in the same tick (an NPC ActionSetStat on Health, a death, /entity stats) could still merge into the modifier
  entry. THE ONE DIFFERENCE THE ENGINE CAN SEE (harness NQ 12b, pinned and counted): its death rule (EntityStatsSystems$Changes) reads
  the self queue - an entry whose value is not above 0 at or below 0 HP kills a mob that has no DeathComponent yet. For a mob at EXACTLY
  0 HP given the heal path (strength.healOnLoad ON - default off, off on Skyy's server - or a spawn) with the same key re-put, 0.1.2's
  Maximize merge hid the PutModifier entry at 0 HP and the mob came back at full health; 0.1.3 heals it the same, but the entry stays
  visible and the engine lets it die - as 0.1.2 already did whenever the level changed (its RemoveModifier entry) or healOnLoad was off.
  A mob at 0 HP normally already has its DeathComponent (the rule skips it), and then nothing differs.

CHECKED 2026-10-03 (0.1.3; re-run before a deploy - the harness is the source of truth, not this text):
  build: 115 engine members probed (exact descriptors), 31 classes (7 kit), "assembled ...SkyyMobs-0.1.3.jar 117855 bytes"; python
  tools/ci/lint.py: 0 fails (26 warnings, all SkyySacks 0.7.12); lint --perm on this script: 0 fails; tools/skyycfg_test.py: PASS.
  python SkyyMobs/test_skyymobs_0.1.3.py: 13382 ok, 0 fail (U1 adds or drops a check with Skyy's live file) - every 0.1 / 0.1.1 /
  0.1.2 section against this jar (A 31 classes -Xverify:all; F / Q / FL / RA / IN / LV on stand-in maps that now answer minStatValue /
  maxStatValue the engine's way) + NQ (the network queue on real engine objects through the real tracker, packet wire format and
  clear: the named cases incl. Skyy's Yeti and its 8-hit fight, 3000 seeded changes on both jars - 0.1.2's player copy missed the
  server in 2019 of them, 0.1.3's in none; 12b 5 times - end to end through the world task) + AX (7064 references, 0 refused; control
  refused + IllegalAccessError) + O (0.1.2's header = 0.1.3's but the version) + Z (26 entries byte-identical; MobLevel: writeValue
  added, the three health writes changed, every other instruction 0.1.2's) + U1 (Skyy's live folder copied: start twice = no byte /
  time changed) + L (173 engine refs, release + 0.7 pre-release, 0 missing). The --dir guard battery (root, top-level, foreign
  non-empty, outside, '..', junction refused; a fresh folder runs and deletes only itself) passed for this harness and the fixed 0.1.1 one.
UNVERIFIED (0.1.3, needs the game): the client applying PutModifier / RemoveModifier, then Min / Max (the client code is not in the
  server jar; the harness replays what each player receives with the server's own EntityStatValue rules; vanilla's armor modifiers and
  ChangeStat interactions use the same entries); the live re-apply on real worlds (as 0.1.2: World.execute + Store.getComponent on the
  world thread). In-game check: with levelled mobs in view, change Server Setup -> Mobs -> Strength - their health bars show the new
  max at once (a full mob stays full, a hurt one keeps its percent) and are empty exactly when the mob dies.

0.1.2 NOTES (the version this copies)
SkyyMobs 0.1.2 - build script (javassist via jpype). A copy of the SET pin build_skyymobs_0.1.1.py (0.1.1 stays untouched; SkyyMobs
has no patch scripts) with Skyy's LEVEL HEALTH FLOOR (OPEN-QUESTIONS.md LOCKED 2026-10-02: "no leveled mob has less health than a 50-HP
mob of its level") and two fixes from Skyy's 0.1.1 test of the same evening (a difficulty change never reached the max health of mobs
that were already loaded; /mobs inspect printed the setting, not what the mob had). Everything else is 0.1.1's (its notes follow).
Run:   python SkyyMobs/build_skyymobs_0.1.2.py        -> SkyyMobs/SkyyMobs-0.1.2.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyMobs/test_skyymobs_0.1.2.py         (bare JVM, -Xverify:all; scratch under tools/dev/scratch/mobs012/; reads
       SkyyMobs-0.1.1.jar (0.1.1 -> 0.1.2 compares, floor 0 = 0.1.1), SkyyMobs-0.1.jar (the one-time 0.1 -> 0.1.1 update still ships)
       and SkyyMenu/SkyyMenu-0.3.5.jar (the label check), all read-only)

0.1.2 CHANGES (the harness byte-compares every class against 0.1.1: only the classes / methods named here changed)
  1. HEALTH FLOOR - new row strength.floor "Health floor (base HP)" (int 0-1000, default 50, live; 0 = off). The health modifier of a
     levelled mob is now  level multiplier x max(1, floor / base),  base = the mob's own max health before our multiplier (vanilla
     MaxHealth after the NPC_Max modifier). MobLevel.baseOf reads it off the stat the way EntityStatValue.computeModifiers builds it
     (bytecode 2026-10-02: max = (stat max + the additive MAX modifiers) x the SUM of the multiplicative MAX StaticModifiers), so base =
     max / that sum (max itself when there is none) - the same with or without our old modifier on the mob - rounded to 0.01 HP so a
     reload never reads a different base (no modifier churn). Max health = max(base, floor) x level multiplier: a Lv 32 Snake_Cobra
     (base 36 in the live log) on Normal 6% has 50 x 2.86 = 143 HP (0.1.1: 103), on Hard 8% 174; a Lv 1 one 50; 74-HP and 200-HP mobs
     are unchanged. The caps (strength.hpCap / dmgCap) still cap the LEVEL multiplier only, as in 0.1.1; the floor goes on top (so a
     floored mob's health / its own base may pass the cap: a Lv 60 cobra on Hard = 50 x 5.72 = 286 HP = x7.94 of 36). Floor 0, or any mob
     at or above the floor = exactly 0.1.1's amount (the harness proves it against SkyyMobs-0.1.1.jar's own code). Damage unchanged.
     Kill XP follows the higher max health (SkyySkills reads it at death). Still ONE modifier per mob under the key skyymobs_lv<N> (the
     save slot) - only its amount changed: no saved-data change; a file without the new line uses 50.
  2. LIVE HEALTH RE-APPLY (Skyy's 0.1.1 test 2026-10-02: Normal -> Hard changed damage at once but every loaded Lv 20 mob kept its max
     health - Goblin Scrapper 81 / 81 on both). MobCfg.derive keeps a health signature (health % per level | health cap | floor); when
     it changes - Difficulty, Custom health %, health cap (its row now runs derive too) or the floor, from the menu, a command, an
     import / restore / undo or a hand edit + reload - it runs MobCfg.ON_HEALTH (setup() sets a MobRefresh(null) there after the first
     load, shutdown clears it). MobRefresh(null) hands every loaded world that holds levelled mobs ONE task on its own world thread
     (World.execute); that task (MobLevel.refreshWorld) re-applies the health modifier of each of its levelled mobs that is still
     loaded (refreshOne -> setMult): the health PERCENT is kept, a hurt mob is never healed (strength.healOnLoad only counts on a chunk
     load, never here), a mob at 0 HP is never touched, so nothing is ever killed. The damage was already live. A chunk load
     re-applies exactly as in 0.1.1 (setMult's 4-argument form = the 5-argument one with heal = strength.healOnLoad).
  3. /mobs inspect shows the multiplier ACTUALLY on the mob (its skyymobs_lv<N> modifier, MobCmds.healthLine) and says so when it
     differs from what the settings give now: "applied x2.14 (setting x2.52 - updates on reload or /mobs set)"; plus base HP and
     "floor 50 HP applied" when the floor lifts the mob. /mobs set reports the multiplier it applied. The ready line names the floor.
  4. Server Setup texts: strength.hp help "Applies at once (health % kept)." (was "(mobs that spawn or reload)"), strength.hpCap help
     "Health per level never goes above this multiple ..."; the new row's label + help pass menu_fit (SkyyMenu 0.3.5's boxes) and the
     harness draws them with the real AdminPage. Every other key, category, choice value, flag and file key is 0.1.1's.

CHECKED 2026-10-02 (0.1.2; re-run before a deploy - the harness is the source of truth, not this text):
  build: 115 engine members probed (exact descriptors), 31 classes (7 kit; 0.1.1's 30 + MobRefresh), 244 built-in role ids; Server Setup
  fit: 191 texts (4 tabs, 78 row names + 78 help lines in every variant, 9 choice buttons, 10 table buttons, 12 page lines) fit SkyyMenu
  0.3.5's boxes with 8 px to spare; "assembled ...SkyyMobs-0.1.2.jar". python tools/ci/lint.py: 0 fails (26 warnings, all SkyySacks
  0.7.12); lint --perm: 0 fails; python tools/skyycfg_test.py: PASS (kit 1.1 unchanged).
  python SkyyMobs/test_skyymobs_0.1.2.py: 10287 ok, 0 fail - every 0.1 / 0.1.1 section against this jar (A 31 classes -Xverify:all, F with
  the floor off = 0.1.1's numbers, K 26 rows, V 328 texts drawn by the real SkyyMenu 0.3.5, L 173 engine refs in release + 0.7
  pre-release, 0 missing) + Q (the floor numbers above, caps, edge bases), FL (floor 0 = SkyyMobs-0.1.1.jar's own hpMult bit for bit,
  7852 amounts; both jars' setMult identical on 54 spawn + reload runs), RA (chunk-load re-apply keeps the percent, no churn), IN (the
  inspect line, Skyy's case word for word), LV (the live re-apply end to end through the real kit and the real World.execute on
  stand-in worlds), O (0.1.1 header vs 0.1.2), Z (class compare: exactly the changes listed here), U1 (Skyy's live folder copied: start
  twice = no byte / time changed, floor 50 by default, the new row on Skyy's real file) + U1b (Skyy's real pre-update bytes -> the 0.1.1
  update) + U2 (the 0.1 -> 0.1.1 update still ships unchanged).
UNVERIFIED (0.1.2, needs the game): the live re-apply on real worlds (World.execute + Store.getComponent on the world thread - the calls
  /mobs platetest and /mobs set already make in game; checked here with stand-ins only); the client redrawing a loaded mob's max health
  after the re-apply (the engine queues PutModifier / RemoveModifier / Set stat changes for the network - bytecode only); baseOf on real
  mobs (the computeModifiers rule from bytecode; it matches the live log's numbers). NOTE Snake_Cobra: its role file says MaxHealth 74
  (a variant of Snake_Marsh, 36) but the live server log shows base 36 - the floor uses whatever max the engine computed (36 -> 50).

0.1.1 NOTES (the version this copies)
SkyyMobs 0.1.1 - build script (javassist via jpype). A copy of the SET pin build_skyymobs_0.1.py (0.1 stays untouched; SkyyMobs has
no patch scripts) with two changes from Skyy's in-game test of 2026-10-02 (OPEN-QUESTIONS.md LOCKED 2026-10-02, after testing Hard:
"make the current hard mode the normal and give hard mode a little better bump. i can still beat lvl 19 at lvl 7 with my accessories
off, when im careful."; HANDOFF 2026-10-02 "UI FIX NEEDED (SkyyMobs 0.1.1)"). Everything else is 0.1's (the 0.1 notes follow below).
Run:   python SkyyMobs/build_skyymobs_0.1.1.py        -> SkyyMobs/SkyyMobs-0.1.1.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
Test:  python SkyyMobs/test_skyymobs_0.1.1.py         (bare JVM, -Xverify:all; scratch under tools/dev/scratch/mobs011/; reads
       SkyyMobs-0.1.jar for the 0.1 -> 0.1.1 compares and SkyyMenu/SkyyMenu-0.3.5.jar for the label check, both read-only)

0.1.1 CHANGES (nothing else changed - the harness byte-compares every class against 0.1)
  1. DIFFICULTY LADDER (health / damage added per level above 1): MobCfg.derive, the rows, the default file, the ready line, /mobs inspect
       Easy    4% / 2%   = 0.1's Normal            (0.1: Easy 3% / 1.5%)
       Normal  6% / 3%   = 0.1's Hard, the DEFAULT (0.1: Normal 4% / 2%)
       Hard    8% / 4%   new                       (0.1: Hard 6% / 3%)
     Caps (row defaults) health x6 / damage x3.5 (0.1: x5 / x3): Hard Lv 60 = x5.72 / x3.36, so no preset is clipped at Lv 60 (Hard
     first meets the caps at Lv 64, Normal at Lv 85). Custom (strength.hp 4 / strength.dmg 2) is unchanged: rows, defaults, meaning.
     The chosen difficulty WORD is kept: a server on "hard" now gets 8% / 4% (Skyy's live config is on hard; Server Setup -> Mobs ->
     Strength -> Difficulty Normal = the old Hard). The ready line and /mobs inspect print the numbers in force (MobCfg.difficultyText).
     ONE-TIME UPDATE of an existing config.properties (new class MobMig; setup() runs MobMig.run(dir) BEFORE MobCfg.load and
     CfgPub.start; the SkyySkills 0.4.11 HealMig / SkyyCollections 0.2.5 CollBypassMig machinery method for method): pure text step
     mgUpdate on the config kit's own parser (CfgFile.isComment / key / value / end / valStart): a cap whose effective (last) line is a
     one-line entry holding exactly 0.1's default text moves to the 0.1.1 default (strength.hpCap 5 -> 6, strength.dmgCap 3 -> 3.5;
     value text only - key, separator and CR kept); an admin's own cap is kept and named in an INFO line; a missing line stays missing
     (the code default is 0.1.1's); 0.1's exact difficulty comment line becomes the 0.1.1 one; a marker comment goes on its own line
     above the comment run on top of the first strength.difficulty / cap entry (else line 0), and a file whose comment lines hold
     MG_MARK_ID is never touched again (an admin who undoes a cap keeps it; the 0.1.1 default file carries the marker, so a fresh file
     is never updated). Before anything is written: the new text must parse (java.util.Properties) to the same keys and values except
     the moved caps; CfgHist.snapshot keeps the old file as a History version ("before the 0.1.1 difficulty update") and the rewrite
     only happens once config-history really holds those bytes (mgSaved); CfgRows.atomicWrite (ISO-8859-1 bytes; every other byte and
     the line endings kept); one config-changes.log line per moved cap in the kit's scalar format (via update, "SkyyMobs 0.1.1", ok) so
     Server Setup -> Changes -> Undo puts it back. The difficulty word is never touched; the INFO line says what it means now.
     Skyy's live file (the 0.1 default text, LF, strength.difficulty=hard, 9 History versions) gets: the marker line, the new comment
     line, strength.hpCap=6, strength.dmgCap=3.5 (History 10 = KEEP 10, nothing dropped) and 2 Undo lines.
  2. LABELS SkyyMenu 0.3.5 cut on Server Setup -> Mobs (Skyy's screenshot): the tab "Who gets levels" (SkyyMenu clips a tab text at 14
     characters and its inline filter drops the dots: drawn "Who gets le") is now "Which mobs"; the Difficulty choices "Easy 3% / 1.5%"
     ... (a 4-choice row = four 90 px buttons; the inline filter also turns % and . into spaces: "Easy 3  / 1 5" = 91 px -> the client
     shows "Easy 3 / 1...", "Normal 4 ...") are now "Easy" / "Normal" / "Hard" / "Custom" and the row's help line carries the
     numbers. Every tab, row name (+ unit + tag, also with the search mark and a draft star), help line, choice and table button is
     measured at build time against SkyyMenu 0.3.5's own layout (menu_fit below: tabs 126 px after the 14-character clip, choice
     buttons (380 - 6 x (n - 1)) / n px at FontSize 16 bold, names 556 px at 20 bold, help 1050 px at 15, button texts reduced like
     MenuUtil.inl) with the client's glyph advances (skyyui.text_width, FIT_PAD px to spare); the harness draws every tab and row
     through the REAL SkyyMenu 0.3.5 jar and measures what it sends. Config KEYS, category ids, choice values, flags and file keys are
     0.1's (the harness compares the two published headers).

0.1 NOTES (the version this copies; its STRENGTH paragraph and CHECKED block are updated for 0.1.1)
SkyyMobs 0.1 = NEW MOD: stage 1 of research/Mob-Levels-Plan.md (section 13), with the zone bands re-fitted in
research/cloud/Mob-Levels-Refit.md and Skyy's decisions in OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02" round 5 + the LOCKED
2026-10-01 zone bands (those win over the plan).

WHAT IT DOES
  Every hostile mob and every neutral fighter that spawns (or loads from a saved chunk) gets a level from WHERE it spawned. The level
  raises its max health and the damage it deals, and the vanilla nameplate shows "[Lv 9] Trork Warrior". No ticking system, no UI page.
  Zone bands (LOCKED 2026-10-01): Zone 1 = Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top: 18-20), Zone 2 = 20-30,
  Zone 3 = 30-45, Zone 4 = 45-60. Biome bands inside each zone = the refit's tables (rarer biomes higher). Random level inside the band.

WHO GETS A LEVEL (Skyy R5: hostile mobs AND neutral fighters; animals / passive never; never players, pets of other mods, NPC traders,
bosses). Engine finding that changes the plan's rule: WorldSupport.getDefaultPlayerAttitude() is HOSTILE for every role that does not
set an attitude (SupportConfigBuilder.readConfig default = Attitude.HOSTILE, bytecode 2026-10-02) - every bird, fish, frog, mouse,
snail and other mods' pets (FPets Floating_Pet_*, Kazzy mounts) would be "hostile". So the attitude alone is not the test:
  1. players never (the hook only sees NPCEntity + EntityStatMap holders);
  2. attitude HOSTILE or NEUTRAL only (FRIENDLY / REVERED = tamed animals, IGNORE = summons and lantern pets: never);
  3. the role id must be in the BUILT-IN list (the jar constant MobCfg.VANILLA) or match "Extra mobs that get levels" (levels.roles,
     empty by default). The built-in list = the EXACT vanilla role ids, generated HERE from Assets.zip: every vanilla role whose attitude
     is hostile and whose template is a fighter (Template_Predator / Intelligent / Flying_Aggressive / Swimming_Aggressive / Goblin* /
     Trork* / Cactee ...) + the neutral fighters Boar, Warthog, every Scarak, the Feran warriors (Sharptooth, Longtooth, Burrower,
     Windwalker) - 244 ids, proven equal to the role set at build time. Exact ids, not Prefix* patterns (review F1): other mods reuse
     vanilla prefixes for their own mounts, pets, NPCs and bosses (Bear_Grizzly_Mount, Wolf_Pet, Spider_Mount, Wraith_Trader,
     Dungeon_*NPCRole, Dungeon_*_Boss: 193 roles in Skyy's Mods folder matched the old patterns). ~5 KB = over the kit's 2000-character
     row, so the list is not a row; an admin removes a vanilla mob with levels.exclude and adds other mods' mobs with levels.roles;
  4. NEUTRAL roles also need "Neutral fighters get levels" (levels.neutral, default on);
  5. never a role in "Never level these" (levels.exclude): tests, tamed animals, temple NPCs, traders, summons, the bosses (Goblin_Duke,
     Trork_Chieftain, Dragon_*, the 0.7 Skeleton_Elite) - bosses get fixed levels in stage 3 - and other mods' mounts / pets / NPCs /
     bosses under an extra pattern (*_Mount*, *_Pet*, *_Boss*, *NPC*, *_Hub*, *Blacksmith*, *Trader*; not *_Sentry*: Trork_Sentry).
  Unknown roles from other mods get no level until an admin adds them (degrades safely); so do the roles new in the 0.7 pre-release
  (Coffer_Goblin_*, Goblin_Burner / Feastmaster / Guardian, Void_Spectre, Void_Spawn_* ...: the next build after 0.7 ships, or the
  extra row). A mob that stops qualifying (tamed: the role change re-adds it as Tamed_* REVERED, or an admin edits the lists) loses its
  level + plate the next time it is added.

WHERE THE LEVEL COMES FROM (first match wins; MobLevel.resolve, pure Java, the harness drives it with strings)
  0 saved   the level saved on the mob (see PERSISTENCE) - kept after chunk reloads and restarts
  2 world   bands.world: world name or its start (dungeon_ = dungeon_1 ...; 0,0 = no levels there) - instances, hub, admin pins
  3 island  SkyyIslands private island worlds (bridge island:owner:fn) -> bands.islands (default 0 = no level)
  4 lava    Skyy R5: vanilla's deep lava caves (Env_Zone1-3_Caves_Volcanic_T1..T3, Env_Zone4_Caves_Volcanic - ids checked in Assets.zip)
            = the band of the HARDEST biome row of that zone (Zone 1 18-20, Zone 2 28-30, Zone 3 43-45, Zone 4 58-60), any world type
  4 biome   classic worldgen (ChunkGenerator): region + biome at the spawn point -> bands.biome (exact Region.Biome, else the region
            row Region). Overlay biomes in bands.passThrough (rivers, lakes, dunes, valleys, villages ...) use the tile biome underneath.
            Caves = the ground above (the 2D lookup). The environment's Bonus column is added on top. The refit's pattern rows
            (Zone1_Tier1.*_Trork, Plateau_*, Mountain_*, Env_Zone1_Caves* ...) ship EXPANDED into one row per Assets.zip biome /
            environment, because the config kit refuses * in a table entry (only entry=itemprefix tables take one) - so every
            number is editable in Server Setup. A * key typed into the file by hand still works (MobBands.find: most specific wins).
  5 env     bands.env band (worlds without classic zone data: the hand-built island chain painted with /setenvironment, World Gen 2)
  6 zone    bands.zone from the region name (Zone2_Tier1 -> Zone2) or the env id (Env_Zone2_... -> Zone2)
  7 default bands.default (default 0 = no level). Oceans (Skyy R5: skip) have no rows - whatever the lookup gives (normally no level).
  Spawn point = NPCEntity.getLeashPoint() (saved LeashPos), else the current position. Spawn environment = NPCEntity.getEnvironment()
  (world spawns), else the block environment at the spawn point (3D, so caves get their cave environment). Level = roll inside the
  band (seeded: world seed + mob UUID + role) + bonus, capped at levels.max.

STRENGTH (Skyy R5 + the 0.1.1 lock of 2026-10-02: a DIFFICULTY setting): Easy 4% / 2%, Normal 6% / 3% (default), Hard 8% / 4%,
  Custom = strength.hp / strength.dmg (4 / 2). Max health x (1 + hp% x (L - 1)), damage x (1 + dmg% x (L - 1)), capped by
  strength.hpCap (x6) / strength.dmgCap (x3.5) - caps chosen so no preset is clipped at Lv 60 (Hard Lv 60 = x5.72 health, x3.36 damage).
  (0.1 shipped Easy 3% / 1.5%, Normal 4% / 2%, Hard 6% / 3%, caps x5 / x3.)
  Health: ONE StaticModifier(MAX, MULTIPLICATIVE) on Health. The engine sums every MULTIPLICATIVE amount of a stat and multiplies the
  max (after the additive NPC_Max modifier) by that sum (EntityStatValue.computeModifiers bytecode), so there is exactly one modifier.
  Because the engine SUMS multiplicative amounts, another mod's MULTIPLICATIVE Health modifier adds to ours instead of multiplying
  (x1.2 next to a Lv 1 x1.0 = x2.2) - only when mods are combined (review F9, info; MobScanTask warns about known scaling mods).
  SPAWN = full health; LOAD with a changed multiplier = the health share is kept (strength.healOnLoad = full instead).
  Damage: LevelDamage (DamageEventSystem, Filter group, BEFORE DamageSystems$ArmorDamageReduction = before armour, SkyyGear's slot):
  a hit whose source entity is a levelled mob (Damage$EntitySource.getRef; projectiles are a ProjectileSource whose ref is the
  shooter) x the damage multiplier of its level, computed live (a difficulty change applies to damage at once, to health on reload).
  Only the ATTACKER is checked: a levelled mob's hits on players, pets and other mobs are all scaled; players' hits never (review F8).

PERSISTENCE (task: component or UUID map - what this version uses: NEITHER, the engine's own stat save): the level is saved IN THE
  KEY of the health modifier "skyymobs_lv<N>" (one modifier, its amount = the health multiplier). EntityStatMap is an entity component
  with a codec (codecVersion 5, legacyVersioned: "Stats" -> EntityStatValue Id / Value / Modifiers; EntityStatsModule.setup registers
  StaticModifier.ENTITY_CODEC as "Static"), EntityStatsSystems$Setup keeps a loaded map and BalancingInitialisationSystem only re-puts
  NPC_Max, so on LOAD the hook reads its own key back (step 0). HARNESS-VERIFIED with the real codecs: the versioned entity path keeps
  the key, CalculationType MULTIPLICATIVE and the Amount through BSON; ENTITY_CODEC stores no Target (it decodes as MAX, the default,
  which is ours). No new ECS component and no codec code (nothing unknown left in saves after an uninstall - only the modifier, plan
  risk 2). Layer 2: KEPT, a session map uuid -> level filled on UNLOAD (bounded 50,000). Layer 3: the roll is deterministic (world
  seed + UUID + role), so a mob with neither re-rolls the same level while its band is unchanged. MOBS (uuid -> MobInfo, loaded levelled
  mobs only) feeds the damage filter, /mobs and the bridge. A real chunk save + restart is still UNVERIFIED in game (test 9).
  PRUNE (review F6): a removed world's store may never call onEntityRemoved, so MobPruneTask (every 5 min, scheduler thread) forgets the
  MOBS entries whose world is gone (MobInfo.wref = a WEAK World reference, compared by identity with Universe.getWorlds()), and each
  loaded world with levelled mobs drops, on its own world thread, the entries whose entity is gone. Entries younger than 60 s are kept.
UNINSTALL (review F5): the modifier and the plate stay in the save until the mob dies - 0.1 ships no strip command. Before removing the
  jar: Server Setup > Mobs > Never level these = * (no mob gets a level), then restart the server or let the chunks reload - every
  levelled mob loses its modifier + plate the next time it is added (health share kept). Mobs in chunks nobody loads keep them.
  tools/deploy_set.py needs a rollback note for this (main session: the builder may not edit it).

NAMEPLATE "[Lv 9] Trork Warrior" (plate.format) on every levelled mob (plate.mode all / off). Name = server.lang through
  I18nModule.getMessage("en-US", Role.getNameTranslationKey()) (variants point at their base name), else the role id without
  plate.strip endings, underscores -> spaces. COLOURS: UNVERIFIED client feature (plan stage 0) - OFF by default (plate.colorOn);
  plate.markup picks one of the three markups to try: tag = <color=#rrggbb>text</color>, section = the section sign + a legacy colour
  code (nearest of the 16), brace = {#rrggbb}text. Ladder plate.colors (lowest level -> colour; kit colours): 1 row-name white,
  20 warning yellow, 30 gold, 45 error red, 61 Mythic purple (refit 4.4). /mobs platetest shows all three on the mob you look at.

COMMANDS  /mobs and /mobs info (every player, hytale:Adventurer): the band where you stand + region / biome, compared with your class
  weapon skill (class:skill:<uuid> + skill:fn:level when SkyyClasses / SkyySkills run). Admin (requirePermission skyymobs.admin +
  setPermissionGroups(new String[0])): /mobs inspect (the mob you look at, else the nearest levelled mob within 8 blocks: level, how it
  was saved, the lookup step + key + band now, multipliers, plate, attitude, region / biome / env), /mobs set <level> (0 = remove),
  /mobs platetest (3 s per markup, then the plate comes back), /mobs reload (the config kit's reload op).
BRIDGE    mob:fn:level = java.util.function.Function: Object[]{String world, java.util.UUID npc} (or a bare UUID) -> Integer level,
  -1 = no level / unknown / wrong world. Any thread (reads the ConcurrentHashMap MOBS), never throws.
SETTINGS  Server Setup > Mobs (tools/skyycfg.py kit 1.1, node skyymobs.admin): Skyy_SkyyMobs/config.properties (who, strength,
  nameplate) + Skyy_SkyyMobs/bands.properties (biome / env / world / zone tables). Every number is a row.

DECISIONS where the plan left room (all editable rows unless noted):
  - the who-gets-a-level allow list above (the plan's attitude test would level birds, fish, critters and other mods' pets);
    neutral fighters = Boar, Warthog, Scarak_*, Feran warriors; NOT cows / horses / deer / moose / goats (they kick back when
    startled but are animals - Skyy R5), not Kweebecs (plan: Kweebec villages friendly), not Feran civilians / cubs, not Klops.
    QUESTION FOR SKYY (review F2): the neutral line is by name, not behaviour - Boar / Warthog use the same startle-kick setup as Cow /
    Moose, and Mosshorn (bites for 12, fights back only when hit) fits "fight back when hit" literally. Left out by default (the safe
    option: "animals never"): Mosshorn, Mosshorn_Plain, Cow, Horse, Moose_Bull, Moose_Cow, Bison, Ram, Camel, Antelope, Goat, Deer_Stag,
    Horse_Skeleton, Horse_Skeleton_Armored, Kweebec_Razorleaf(_Patrol). Typing any of them into "Extra mobs that get levels" levels them.
  - caps x6 health / x3.5 damage (0.1.1; no preset clipped at Lv 60).
  - bands.islands and bands.default = 0 (task: island worlds / instances get per-world rows, else no level).
  - shores take the lowest band of their land region (plan 4.1); shallow ocean regions have no rows (Skyy R5: oceans skip).
  - Zone 3 / 4 overlays the plan did not name: lakes, valleys, canyons, calderas, hills, volcanoes, villages and towns pass through to
    the tile biome underneath (the village env Bonus +2 then applies); Zone 3 mountains Mountain_* = the refit's overlay rows 32-34 /
    37-39 / 43-45; Zone 4 mountains use the region rows 45-50 / 53-60.
  - the lava-cave rule applies on every world type; "hardest biome" = the zone's biome row with the highest max (then min), region
    fallback rows (Region.*) left out; the volcanic env rows stay as data (used when bands.volcanicTop is off).
  - env Bonus only on top of a biome band (and the lava band); the env band itself never adds its own bonus.
  - a nameplate set to colours colours the whole plate text; the platetest uses error red #ff6b6b for all three markups.
  - KEEP 10 config history versions (RESUME follow-up direction).
NOT IN 0.1 (later stages): elites, rewards (XP gap rule, bonus drops, gear rarity), mob:fn:band, mob:fn:setLevel, scale.role / boss
  levels, /mobs survey, relevel / strip actions, bands.area, night bonus (Skyy R5: none), mob armour (Skyy R5: none).
REVIEW FIXES (2026-10-02, same version - never deployed): F1 exact built-in role ids + levels.roles = extra mobs (empty) + guard
  patterns in levels.exclude; F3 the worldgen cache keys the exact block column and never keeps a failed lookup or a missing generator;
  F4 no unordered fallback hook (an ERROR + MobLevel.HOOK, shown by /mobs inspect and /mobs info); F5 UNINSTALL note; F6 MobPruneTask;
  F7 isOurs also knows the default format and every format used this run (plate.format runs derive); F11 /mobs platetest claims the
  mob (one test at a time per mob) and puts back the mob's current level plate. F2 = a question for Skyy (above), F8-F10 info (F10:
  blanking levels.roles no longer switches levelling off - it only holds the extras now).
UNVERIFIED (needs the game): the modifier key surviving a real chunk save / restart (the codec round trip is verified); nameplate
  colour markup (the reason colours are off + /mobs platetest); the client drawing a plate on hostile mobs exactly like /entity
  nameplate; I18n key form "server.npcRoles.X.name" (fallback = id); projectile damage carrying the shooter (Damage$ProjectileSource
  ref); marker / beacon spawns' environment = Integer.MIN_VALUE; SkyySkills' getMax() including the multiplier (combat XP); a role
  change (taming) re-adding the mob with the new attitude; painted /setenvironment environments on the island chain; ordering against
  BalancingInitialisationSystem at runtime (a refused registration = no levels that start + one ERROR, no fallback); the prune's
  world-thread pass (Universe.getWorlds() + World.execute, bytecode-probed only).

CHECKED 2026-10-02 (0.1.1; re-run before a deploy - the harness is the source of truth, not this text):
  build: 113 engine members probed (exact descriptors), 30 classes (7 kit; 0.1's 29 + MobMig), 244 built-in role ids; Server Setup fit:
  183 texts (4 tabs, 74 row names + 74 help lines in every variant, 9 choice buttons, 10 table buttons, 12 page lines) fit SkyyMenu
  0.3.5's boxes with 8 px to spare (tightest: plate.markup "2 section sign" 104.0 / 122 px) and the 0.1 labels fail the same measure
  (tab levels, Difficulty easy / normal / hard); "assembled ...SkyyMobs-0.1.1.jar".
  python tools/ci/lint.py: 0 fails, no SkyyMobs warning (repo: 26 warnings, all SkyySacks 0.7.12); lint --perm: 0 fails.
  python tools/skyycfg_test.py: 273 checks + phase 1 (29 refused, 3 built) PASS (kit 1.1, unchanged).
  python SkyyMobs/test_skyymobs_0.1.1.py: 10015 ok, 0 fail - every 0.1 section (A 30 classes -Xverify:all, B, R 3365 + 20 lookups, E,
  X 1526 other-mod roles, G, F, I, W, N, T, H, K, S, P, L 168 engine refs in release + 0.7 pre-release, 0 missing) with the 0.1.1
  ladder in C / D / F / K - health / damage at Lv 1 / 20 / 60: Easy x1 / x1.76 / x3.36 and x1 / x1.38 / x2.18, Normal x1 / x2.14 /
  x4.54 and x1 / x1.57 / x2.77, Hard x1 / x2.52 / x5.72 and x1 / x1.76 / x3.36 (1208 multipliers float32-exact; caps x6 / x3.5 first
  reached by Hard at Lv 64) - plus:
    O SkyyMobs-0.1.jar's own header (child-first loader): the same 25 keys / category ids / types / choice values / flags / files; only
      the Difficulty opts + help, the two caps' default + help and the first tab label changed; 0.1.1's Easy / Normal = 0.1's Normal /
      Hard at every level 0-60, by both jars' own code;
    U Skyy's live Skyy_SkyyMobs folder (a scratch copy): the marker + the new comment line + caps 6 / 3.5, strength.difficulty=hard kept
      (memory: Hard 8% / 4%), LF + every other byte kept, bands.properties untouched, History 9 -> 10 (the old bytes, its index line),
      2 Undo lines the kit's log op lists as ok, a History restore preview, start 2 = no byte / time changed, Undo (via undo) -> 5 kept
      by start 3; synthetic files: the 0.1 default text -> exactly the 0.1.1 default (but line 1's version), CRLF, admin caps kept +
      named, caps already new, one moved / one kept, marker present, no file, a continued line, duplicate keys, other separators, every
      difficulty word (+ odd / missing), a blocked config-history (nothing written), no strength keys, ISO-8859-1 bytes;
    V 312 texts drawn by SkyyMenu 0.3.5's real AdminPage (tabRow + drawRow, every row with / without a search hit and a draft) fit with
      8 px to spare; the same drawing of the 0.1 header flags exactly the tab ("Who gets le") and Easy / Normal (+ the choice texts that
      lost their % and .); SkyyMenu-0.3.5.jar = the deployed SkyyMenu.jar;
    Z 25 jar entries byte-identical to 0.1, MobMig added, CfgFn = only its version string, code changed only in CfgRows.<clinit>,
      MobCfg.<clinit> / derive / apply and SkyyMobsPlugin.setup (+ constant-only: CfgRows.header, MobCfg.load / reloadAll / useDefaults).
  0.1 was checked the same way (9544 ok, 0 fail - build_skyymobs_0.1.py).
UNVERIFIED (0.1.1, needs the game): the client drawing the new labels as measured (its own glyph advances; Skyy's 0.1 screenshot matched
  the measure to 1.5 px); the update on Skyy's real world folder (proven on a copy of it); the ready line in the server log.
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
assert tuple(int(x) for x in getattr(CFG, "KIT_VERSION", "1.0").split(".")) >= (1, 1), "SkyyMobs needs config kit 1.1+"
import skyyui as SUI       # chat status colours + the nameplate ladder defaults come from the vanilla UI kit (no pages in 0.1)
SUI.verify(quiet=True)
KIT_ID = SUI.kit_id()

VERSION = "0.1.4"
MOD = "SkyyMobs"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ================================================================= 0.1.4: the pairing STOP (spec 7.1: deploy and roll back ALL THREE together)
# SkyyMobs 0.1.4 pinned <=> SkyyGear 0.2.5+ (the gear curves) and SkyySkills 0.4.17+ (kill XP by mob level through mob:fn:info). The build
# stops when tools/deploy_set.py pins this version any other way (the SkyyArmory pattern). --set-file <a copy inside tools/dev/scratch>
# + --check-set = verification only: run the guard on that copy and exit (no build).
GEAR_PARTNER, SKILLS_PARTNER = "0.2.5", "0.4.17"
SET_FILE = os.path.join(ROOT, "tools", "deploy_set.py")
if "--set-file" in sys.argv:
    SET_FILE = os.path.realpath(sys.argv[sys.argv.index("--set-file") + 1])
    if not (SET_FILE + os.sep).startswith(os.path.realpath(os.path.join(ROOT, "tools", "dev", "scratch")) + os.sep):
        raise SystemExit("--set-file must be a file inside tools/dev/scratch")
    if "--check-set" not in sys.argv:
        raise SystemExit("--set-file is for verification only: use it with --check-set (the real jar is checked against tools/deploy_set.py)")


def vtuple(s):
    return tuple(int(x) for x in s.split("."))


def pair_problem(text):
    """None, or why the SET in this deploy_set.py text pins SkyyMobs VERSION without its partners"""
    s0 = text.index("SET = [")
    pins = dict(re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', text[s0:text.index("\n]\n", s0)]))
    if pins.get(MOD) != VERSION:
        return None
    g, k = pins.get("SkyyGear"), pins.get("SkyySkills")
    if g is None or vtuple(g) < vtuple(GEAR_PARTNER):
        return "SkyyMobs %s is pinned with SkyyGear %s: pin SkyyGear %s+ (the gear curves) in the same deploy" % (VERSION, g, GEAR_PARTNER)
    if k is None or vtuple(k) < vtuple(SKILLS_PARTNER):
        return "SkyyMobs %s is pinned with SkyySkills %s: pin SkyySkills %s+ (kill XP by mob level) in the same deploy" % (VERSION, k, SKILLS_PARTNER)
    return None


_pp = pair_problem(open(SET_FILE, encoding="utf-8").read())
if _pp:
    raise SystemExit("STOP: " + _pp)
if "--check-set" in sys.argv:
    print("SET pairing ok (%s)" % SET_FILE)
    sys.exit(0)
NODE = "skyymobs.admin"
KEY_PREFIX = "skyymobs_lv"          # health modifier key = KEY_PREFIX + level (the save slot)

# ================================================================= 0.1.1: the difficulty ladder (Skyy 2026-10-02) - ONE place for every number
# (percent added per level above 1: health, damage). 0.1's ladder stays here only for the update's INFO line, its comment line and the checks.
PRESETS_01 = {"easy": (3.0, 1.5), "normal": (4.0, 2.0), "hard": (6.0, 3.0)}
CAPS_01 = (5.0, 3.0)                    # 0.1's strength.hpCap / strength.dmgCap defaults (what MobMig moves)
PRESETS = {"easy": (4.0, 2.0), "normal": (6.0, 3.0), "hard": (8.0, 4.0)}
CAPS = (6.0, 3.5)                       # strength.hpCap / strength.dmgCap defaults
CUSTOM = (4.0, 2.0)                     # strength.hp / strength.dmg defaults (Difficulty Custom) - unchanged from 0.1
DIFF_DEF = "normal"
LEVEL_TOP = 60                          # the top of the highest zone band (Zone 4 45-60): no preset may be clipped there


def num(x):
    """a number as the config kit writes a dec value (6.0 -> "6", 3.5 -> "3.5"), also the Java double literal source (repr)"""
    s = repr(float(x))
    return s[:-2] if s.endswith(".0") else s


def mult(pct, level):
    """MobCfg.hpMult / dmgMult before the cap (double maths, as Java does it)"""
    return 1.0 if level <= 1 else 1.0 + (pct / 100.0) * (level - 1)


def diff_comment(p):
    return ("# Difficulty: easy (%s%% health / %s%% damage per level), normal (%s%% / %s%%), hard (%s%% / %s%%) or custom (the two values "
            "below)." % (num(p["easy"][0]), num(p["easy"][1]), num(p["normal"][0]), num(p["normal"][1]), num(p["hard"][0]), num(p["hard"][1])))


assert PRESETS["easy"] == PRESETS_01["normal"] and PRESETS["normal"] == PRESETS_01["hard"], "0.1.1: Easy = 0.1's Normal, Normal = 0.1's Hard"
assert PRESETS["hard"][0] > PRESETS["normal"][0] and PRESETS["hard"][1] > PRESETS["normal"][1], "Hard is a bump over Normal"
assert CUSTOM == PRESETS_01["normal"], "Custom's two rows keep 0.1's defaults (4 / 2)"
for _p in PRESETS.values():
    assert mult(_p[0], LEVEL_TOP) <= CAPS[0] and mult(_p[1], LEVEL_TOP) <= CAPS[1], "a preset is clipped by the caps at Lv %d" % LEVEL_TOP
HARD_TOP = (mult(PRESETS["hard"][0], LEVEL_TOP), mult(PRESETS["hard"][1], LEVEL_TOP))
assert ("%.2f" % HARD_TOP[0], "%.2f" % HARD_TOP[1]) == ("5.72", "3.36"), "Hard Lv 60 = x5.72 / x3.36 (task)"
# the 0.1 default comment line (exactly as 0.1 wrote it - Skyy's live file holds it) and its 0.1.1 text: MobMig swaps the exact old line
DOC_OLD = diff_comment(PRESETS_01)
DOC_NEW = diff_comment(PRESETS)
assert DOC_OLD == "# Difficulty: easy (3% health / 1.5% damage per level), normal (4% / 2%), hard (6% / 3%) or custom (the two values below)."
# MobMig's one-time update: (key, the 0.1 default text, the 0.1.1 default text, what a kept admin value means now)
MG_ROWS = [("strength.hpCap", num(CAPS_01[0]), num(CAPS[0]),
            "x%s never clips Hard (%s%% a level) at Lv %d, which is x%.2f" % (num(CAPS[0]), num(PRESETS["hard"][0]), LEVEL_TOP, HARD_TOP[0])),
           ("strength.dmgCap", num(CAPS_01[1]), num(CAPS[1]),
            "x%s never clips Hard (%s%% a level) at Lv %d, which is x%.2f" % (num(CAPS[1]), num(PRESETS["hard"][1]), LEVEL_TOP, HARD_TOP[1]))]
assert [(k, o, n) for k, o, n, _w in MG_ROWS] == [("strength.hpCap", "5", "6"), ("strength.dmgCap", "3", "3.5")]
# the marker comment (in the 0.1.1 default file and in every updated file): a doc comment with spaces and no "=", so the config kit
# never takes it for a "#key=value" template line; MobMig looks for MG_MARK_ID in comment lines only
MG_MARK_ID = "SkyyMobs 0.1.1 difficulty update"
MG_MARK = ("# %s (Skyy 2026-10-02): per level above 1 easy is now %s%% / %s%%, normal %s%% / %s%% (the old hard), hard %s%% / %s%%; caps x%s / x%s"
           % (MG_MARK_ID, num(PRESETS["easy"][0]), num(PRESETS["easy"][1]), num(PRESETS["normal"][0]), num(PRESETS["normal"][1]),
              num(PRESETS["hard"][0]), num(PRESETS["hard"][1]), num(CAPS[0]), num(CAPS[1])))
MG_WHO = "SkyyMobs 0.1.1"               # the name on the update's config-changes.log lines and its History version
assert all(32 <= ord(_c) < 127 for _c in MG_MARK + DOC_NEW) and "=" not in MG_MARK and MG_MARK.startswith("# ") and '"' not in MG_MARK
assert MG_MARK_ID not in DOC_NEW and MG_MARK_ID not in DOC_OLD and DOC_OLD != DOC_NEW

# ================================================================= 0.1.2: the level health floor (Skyy 2026-10-02, OPEN-QUESTIONS LOCKED)
# "no leveled mob has less health than a 50-HP mob of its level": health modifier = level multiplier x max(1, floor / base), base = the
# mob's own max health before our multiplier. The caps still cap the level multiplier only (as in 0.1.1); the floor goes on top.
FLOOR_DEF = 50                          # strength.floor default (base HP); 0 = off
FLOOR_MAX = 1000
FLOOR_DOC = "# Health floor (Skyy 2026-10-02): no levelled mob has less health than a mob of this base HP at its level (0 turns it off)."
FLOOR_HELP = "No levelled mob has less health than a mob of this base HP at its level. 0 = off."


def floor_factor(base, floor=FLOOR_DEF):
    """= MobCfg.floorFactor: max(1, floor / base); 1 when the floor is off or the base is unknown"""
    return 1.0 if floor <= 0 or base <= 0 else max(1.0, float(floor) / base)


def floor_hp(base, pct, level, cap=CAPS[0], floor=FLOOR_DEF):
    """max health with the floor (double maths): base x min(cap, level multiplier) x floor factor = max(base, floor) x capped multiplier"""
    return base * min(cap, mult(pct, level)) * floor_factor(base, floor)


# the task's numbers: a Lv 32 cobra (base 36) = 50 x 2.86 = 143 HP on Normal 6% (0.1.1: 103), 174 on the new Hard 8%; stronger mobs unchanged
assert abs(floor_hp(36, PRESETS["normal"][0], 32) - 143.0) < 1e-6 and abs(floor_hp(36, PRESETS["hard"][0], 32) - 174.0) < 1e-6
assert abs(floor_hp(36, PRESETS["normal"][0], 32, floor=0) - 102.96) < 1e-6 and floor_hp(200, 6.0, 32) == 200 * mult(6.0, 32)
assert floor_hp(36, 6.0, 1) == 50.0 and floor_hp(74, 6.0, 1) == 74.0, "Lv 1: a 36-HP mob is lifted to 50, a 74-HP mob keeps 74"
assert "=" not in FLOOR_DOC and FLOOR_DOC.startswith("# ") and len(FLOOR_HELP) <= 100 and all(32 <= ord(_c) < 127 for _c in FLOOR_DOC)

# ================================================================= 0.1.4: the level curve (research/Mob-Curve-Spec.md, accepted 2026-10-05)
# Spec 1.2 / 1.3: one points table per difficulty and kind (health / damage), straight lines between points, flat outside them
# (SkyyGear's GearBase.eval rule). THE RULE: health(L) = today's preset health(L) x F_new(g) / F_old(g), damage(L) = today's preset
# damage(L) x player max HP_new(L) / max HP_old(L), g = min(L, 49) - same-level fights play like 0.1.3's preset at every level. Lv 1-20 of
# every table lies on 0.1.3's line 1 + p (L - 1). The default points below are the spec's section 1.3 block, exactly.
CURVE_DIFFS = ["easy", "normal", "hard", "custom"]
CURVE_KINDS = ["hp", "dmg"]
CURVE_SPEC = {
    ("hp", "hard"): "1=1.0, 20=2.52, 25=3.62, 30=5.6,  35=8.53, 40=13.18, 45=19.41, 49=24.52, 55=26.95, 60=28.98",
    ("hp", "normal"): "1=1.0, 20=2.14, 25=3.03, 30=4.62, 35=6.97, 40=10.69, 45=15.63, 49=19.66, 55=21.48, 60=23.0",
    ("hp", "easy"): "1=1.0, 20=1.76, 25=2.43, 30=3.65, 35=5.41, 40=8.19,  45=11.85, 49=14.79, 55=16.01, 60=17.02",
    ("dmg", "hard"): "1=1.0, 20=1.76, 25=2.32, 30=3.03, 35=3.89, 40=4.95,  45=6.41,  49=7.72,  55=8.31,  60=8.78",
    ("dmg", "normal"): "1=1.0, 20=1.57, 25=2.04, 30=2.62, 35=3.33, 40=4.2,   45=5.39,  49=6.45,  55=6.89,  60=7.24",
    ("dmg", "easy"): "1=1.0, 20=1.38, 25=1.75, 30=2.22, 35=2.77, 40=3.44,  45=4.36,  49=5.19,  55=5.47,  60=5.7",
}
for _k in CURVE_KINDS:                       # curve.hp.custom / curve.dmg.custom = copies of the Hard tables
    CURVE_SPEC[(_k, "custom")] = CURVE_SPEC[(_k, "hard")]


def curve_pts(text):
    return [(int(a), float(b)) for a, b in (x.strip().split("=") for x in text.split(","))]


CURVES = dict((k, curve_pts(v)) for k, v in CURVE_SPEC.items())
CURVE_IDX = [(k, d) for k in CURVE_KINDS for d in CURVE_DIFFS]     # MobCfg.CURVES index = kind x 4 + difficulty
CURVE_DEF_TEXT = [",".join("%d:%s" % (a, num(b)) for a, b in CURVES[kd]) for kd in CURVE_IDX]


def curve_eval(pts, x):
    """= MobCfg.eval (SkyyGear GearBase.eval): flat before the first / after the last point, straight lines between"""
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for i in range(1, len(pts)):
        if x <= pts[i][0]:
            l0, v0 = pts[i - 1]
            l1, v1 = pts[i]
            return v0 + (v1 - v0) * (x - l0) / (l1 - l0)
    return pts[-1][1]


# build checks of the default tables against the spec: 10 points each, levels 1..60 increasing, factors 0.1-1000, Lv 1 = x1, the Lv 1-20
# part ON 0.1.3's preset line (the point 20 = 1 + p x 19), increasing, Easy <= Normal <= Hard at every point, the health rule F_new / F_old
F_OLD = [(1, 1.0), (4, 1.6), (10, 2.0), (40, 3.0), (100, 5.0)]
F_NEW = [(1, 1.0), (4, 1.6), (10, 2.0), (20, 2.333333), (25, 3.1), (30, 4.5), (35, 6.5), (40, 9.6), (45, 13.6), (50, 17.5), (60, 22.5),
         (70, 36.0), (80, 57.0), (90, 90.0)]
for (_k, _d), _p in CURVES.items():
    assert len(_p) == 10 and [a for a, _b in _p] == [1, 20, 25, 30, 35, 40, 45, 49, 55, 60], (_k, _d)
    assert _p[0][1] == 1.0 and all(0.1 <= b <= 1000 for _a, b in _p) and all(_p[i][1] < _p[i + 1][1] for i in range(9)), (_k, _d)
    _pre = PRESETS["hard" if _d == "custom" else _d][0 if _k == "hp" else 1]
    assert abs(_p[1][1] - mult(_pre, 20)) < 1e-9, "the point 20 of %s %s lies on 0.1.3's preset line" % (_k, _d)
    if _k == "hp":
        for _a, _b in _p[1:]:
            _g = min(_a, 49)
            _want = min(CAPS[0], mult(_pre, _a)) * curve_eval(F_NEW, _g) / curve_eval(F_OLD, _g)
            assert abs(_b - _want) < 0.0051, "health rule: %s %s Lv %d = %s, rule %.4f" % (_k, _d, _a, _b, _want)
for _k in CURVE_KINDS:
    for _i in range(10):
        assert CURVES[(_k, "easy")][_i][1] <= CURVES[(_k, "normal")][_i][1] <= CURVES[(_k, "hard")][_i][1]
SHAPE_OPTS = "curve|Level curve,linear|Per level"
SHAPE_DEF = "curve"
HARD_STEP = PRESETS["hard"][0] / 100.0      # hardRef in Per level shape (kill XP share): min(hpCap, 1 + 0.08 (L - 1))
# the level gap (spec 3.1, accepted): free 5 levels, then -2.5 % of your damage / +1.5 % of its damage per level, floor 40 % / cap x1.5
GAP_DEF = {"free": 5, "dealtStep": 2.5, "dealtMin": 40.0, "takenStep": 1.5, "takenMax": 1.5}
GAP_TTL_MS = 2000                           # the class level cache (spec 3.3: a level-up mid-fight counts within 2 s)
# the one-time update (spec 6.4): marker, History title, the change-log name
MG14_MARK_ID = "SkyyMobs 0.1.4 level curve"
MG14_MARK = ("# %s (Skyy 2026-10-05): Strength shape, damage floor, one hit at most, the Level curve tables and the Level gap rows "
             "(research/Mob-Curve-Spec.md)" % MG14_MARK_ID)
MG14_WHO = "SkyyMobs 0.1.4"
MG14_WHAT = "before the 0.1.4 level curve"
ROLE_DOC = ("# Fixed level by role (Server Setup -> Mobs -> Which mobs): lines scale.role.<role id> with <level>,<health x> - that mob always "
            "gets this level (beats Never level these), health x on top; level 0 is off. None by default.")
SHAPE_DOC = "# Strength shape: curve (the Level curve tables below, Wynncraft style) or linear (Per level: the % and cap rows above, SkyyMobs 0.1.3)."
DMGFLOOR_DOC = "# Damage floor: mobs above Lv 20 hit players for at least this % of their Lv 1 health (ramped in from Lv 21, full from Lv 30); 0 is off."
HITCAP_DOC = "# One hit at most: a levelled mob's hit on a player (before armour) is at most this % of the player's max Health; 0 is off."
CURVE_DOC = {"hp": "# Health curve %s: mob max health x this factor at each level (curve.hp.%s.<level>); straight lines between, flat after the last.",
             "dmg": "# Damage curve %s: mob damage x this factor at each level (curve.dmg.%s.<level>); straight lines between, flat after the last."}
GAP_DOCS = [("part.gap", "true", "# Level gap (part switch): mobs above your class weapon skill take less damage from you and hit you harder (players vs mobs only)."),
            ("gap.free", str(GAP_DEF["free"]), "# Levels above your class weapon skill with no gap effect."),
            ("gap.dealtStep", num(GAP_DEF["dealtStep"]), "# Your damage lost per level past the free band, in percent."),
            ("gap.dealtMin", num(GAP_DEF["dealtMin"]), "# Your damage never drops below this percent of normal (no mob is ever immune)."),
            ("gap.takenStep", num(GAP_DEF["takenStep"]), "# Damage you take more per level past the free band, in percent."),
            ("gap.takenMax", num(GAP_DEF["takenMax"]), "# The gap never makes a mob's hits bigger than this multiple.")]


def mg14_groups(shape):
    """(file key or family prefix ending '.', [lines]) in file order: the block the update (and the fresh default file) puts right after
    the last strength.* entry. A group is left out when its key (any case) / any key of its family is already in the file."""
    G = [("strength.shape", [SHAPE_DOC, "strength.shape=" + shape]),
         ("strength.dmgFloor", [DMGFLOOR_DOC, "strength.dmgFloor=0"]),
         ("strength.hitCap", [HITCAP_DOC, "strength.hitCap=0"])]
    for k, d in CURVE_IDX:
        G.append(("curve.%s.%s." % (k, d), [CURVE_DOC[k] % (d.capitalize(), d)] + ["curve.%s.%s.%d=%s" % (k, d, a, num(b)) for a, b in CURVES[(k, d)]]))
    for key, val, doc in GAP_DOCS:
        G.append((key, [doc, key + "=" + val]))
    return G


for _t in [MG14_MARK, ROLE_DOC, SHAPE_DOC, DMGFLOOR_DOC, HITCAP_DOC] + [d for _k, _v, d in GAP_DOCS] + list(CURVE_DOC.values()):
    assert _t.startswith("# ") and "=" not in _t and all(32 <= ord(_c) < 127 for _c in _t) and '"' not in _t and "@" not in _t, _t
assert MG14_MARK_ID not in MG_MARK and MG_MARK_ID not in MG14_MARK

# ================================================================= Assets.zip (read-only): roles, zones, environments
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
AZ = zipfile.ZipFile(AZ_PATH)
AZ_NAMES = AZ.namelist()


def lenient(t):
    t = re.sub(r"//[^\n]*", "", t)
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    t = re.sub(r",\s*([}\]])", r"\1", t)
    return json.loads(t)


ROLES, ROLE_PATH = {}, {}
for _n in AZ_NAMES:
    if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json"):
        _nm = _n.rsplit("/", 1)[1][:-5]
        ROLES[_nm] = lenient(AZ.read(_n).decode("utf-8-sig", "replace"))
        ROLE_PATH[_nm] = _n[len("Server/NPC/Roles/"):]


def role_params(name, depth=0):
    r = ROLES.get(name)
    if r is None or depth > 12:
        return {}, None
    if r.get("Type") == "Variant":
        base, root = role_params(r.get("Reference"), depth + 1)
        p = dict(base)
        p.update(r.get("Modify") or {})
        return p, root
    p = {}
    for k, v in (r.get("Parameters") or {}).items():
        if isinstance(v, dict) and "Value" in v:
            p[k] = v["Value"]
    return p, name


def role_attitude(name):
    """the attitude the engine gives the role: DefaultPlayerAttitude of its root (Compute = a parameter), HOSTILE when it sets none"""
    p, root = role_params(name)
    rr = ROLES.get(root) if root else None
    a = rr.get("DefaultPlayerAttitude") if rr else None
    if isinstance(a, dict) and "Compute" in a:
        a = p.get(a["Compute"])
    if isinstance(a, dict):
        a = a.get("Value")
    if "DefaultPlayerAttitude" in p and isinstance(p["DefaultPlayerAttitude"], str):
        a = p["DefaultPlayerAttitude"]
    return (a or "Hostile").upper(), root


# a role is a mob that can be levelled (vanilla): not abstract / component, not a test, its root template is not a passive template
PASSIVE_ROOTS = {"Template_Birds_Passive", "Template_Swimming_Passive", "Template_Beasts_Passive_Critter", "Template_Edible_Critter",
                 "Template_Placeholder", "Template_Livestock", "Template_Temple", "Template_Summoned_Ally", "Template_Animal_Neutral"}
NEUTRAL_FIGHTERS = {"Boar", "Warthog", "Feran_Sharptooth", "Feran_Longtooth", "Feran_Burrower", "Feran_Windwalker"}
NEUTRAL_PREFIXES = ("Scarak_", "Dungeon_Scarak_")
BOSSES = ["Goblin_Duke*", "Trork_Chieftain", "Dragon_*", "Skeleton_Elite*"]
VANILLA = []          # every spawnable vanilla role name (the universe the lists are checked against)
FIGHTERS = set()      # hostile fighters + neutral fighters (before the boss exclusion)
ATT = {}
for _nm, _r in ROLES.items():
    if _r.get("Type") in ("Abstract", "Component") or ROLE_PATH[_nm].startswith("_Core/") or _nm == "Empty_Role":
        continue
    VANILLA.append(_nm)
    _a, _root = role_attitude(_nm)
    ATT[_nm] = _a
    if _a == "HOSTILE" and _root not in PASSIVE_ROOTS:
        FIGHTERS.add(_nm)
    if _a == "NEUTRAL" and (_nm in NEUTRAL_FIGHTERS or _nm.startswith(NEUTRAL_PREFIXES)):
        FIGHTERS.add(_nm)
VANILLA.sort()


def glob(p, s):
    return re.fullmatch(re.escape(p.lower()).replace(r"\*", ".*"), s.lower()) is not None


def matches(pats, s):
    return any(glob(p, s) for p in pats)


# Review F1: the built-in list is the EXACT vanilla role ids (no Prefix* patterns): other mods reuse vanilla prefixes for their own
# mounts, pets, NPCs and bosses (Bear_Grizzly_Mount, Wolf_Pet, Spider_Mount, Wraith_Trader, Dungeon_*NPCRole, Dungeon_*_Boss - 193 roles
# in Skyy's Mods folder matched the old patterns). 244 names = ~5 KB, over the kit's 2000-character text row, so they ship as the jar
# constant MobCfg.VANILLA; the row levels.roles is now "Extra mobs that get levels" (other mods' roles), empty by default.
_boss_roles = set(n for n in VANILLA if matches(BOSSES, n))
LEVELLED = sorted(FIGHTERS - _boss_roles)
LEVELLED_TEXT = ",".join(LEVELLED)
_lev_low = set(n.lower() for n in LEVELLED)
ROLES_DEF = ""
# other mods' mounts / pets / NPCs / bosses never get a level, even when an admin adds an extra pattern that matches them (review F1 (b);
# *_Sentry* is left out on purpose: it would remove the vanilla Trork_Sentry / Trork_Sentry_Patrol)
GUARDS = ["*_Mount*", "*_Pet*", "*_Boss*", "*NPC*", "*_Hub*", "*Blacksmith*", "*Trader*"]
EXCLUDE_DEF = ",".join(["Test_*", "Tamed_*", "Temple_*", "*_Merchant*", "Risen_*"] + BOSSES + GUARDS)
_excl = EXCLUDE_DEF.split(",")


def levelled(n, extra=()):
    """the Python mirror of MobCfg.whyNot's list part: built in (exact, any case) or an extra pattern, and not excluded"""
    return (n.lower() in _lev_low or matches(extra, n)) and not matches(_excl, n)


for _n in LEVELLED:
    assert re.fullmatch(r"[A-Za-z0-9_]+", _n), "role id with a separator in it: " + _n
for _n in VANILLA:      # build check: (built in and not exclude) == the role set, for every vanilla role
    assert levelled(_n) == (_n in FIGHTERS and _n not in _boss_roles), "the built-in list / levels.exclude disagree with the classification on " + _n
assert len(EXCLUDE_DEF) <= 2000, "levels.exclude longer than the kit's 2000-character text row"
assert len(LEVELLED_TEXT) < 60000, "the built-in role list must stay one Java string constant"
OLD_PREFIXES = ["Bear_*", "Wolf_*", "Spider*", "Wraith*", "Dungeon_*", "Skeleton*", "Zombie*", "Goblin_*", "Trork_*"]
OTHER_MOD_ROLES = ("Bear_Grizzly_Mount", "Wolf_Pet", "Spider_Mount", "Wraith_Trader", "Dungeon_BlacksmithNPCRole", "Dungeon_Hub_NPC_Role",
                   "Dungeon_ArcaneNPCRole", "Dungeon_Crypt_Boss", "Skeleton_Pet_Knight", "Zombie_Mount", "Goblin_Trader", "Trork_Boss_Warlord",
                   "KazzyPets_Mount_Cow_Undead", "KazzyPets_Mount_Crawler_Void", "KazzyPets_Mount_Bear_Grizzly", "Floating_Pet_Blue",
                   "Spark_Pet_Blue", "Pet_White_Wolf")
for _o in OTHER_MOD_ROLES:
    assert _o not in ROLES, "the other-mod sample %s is a vanilla role" % _o
    assert not levelled(_o), "another mod's mount / pet / NPC / boss would get a level: " + _o
    assert not levelled(_o, OLD_PREFIXES), "the guard patterns miss another mod's mount / pet / NPC / boss under an extra pattern: " + _o
for _yes in ("Skeleton_Fighter", "Skeleton_Fighter_Wander", "Trork_Warrior", "Trork_Sentry", "Boar", "Warthog", "Scarak_Louse",
             "Scarak_Fighter", "Feran_Sharptooth", "Bear_Grizzly", "Spectre_Void", "Golem_Firesteel", "Cactee", "Piranha"):
    assert levelled(_yes), "should get a level: " + _yes
for _no in ("Cow", "Sheep", "Horse", "Deer_Stag", "Bluebird", "Frog_Green", "Mouse", "Kweebec_Razorleaf", "Kweebec_Merchant",
            "Klops_Merchant", "Feran_Civilian", "Feran_Cub", "Tamed_Boar", "Goblin_Duke", "Trork_Chieftain", "Dragon_Fire",
            "Risen_Knight", "Temple_Kweebec", "Snail_Magma", "Shark_Hammerhead", "Mosshorn", "Moose_Bull", "Bison"):
    assert not levelled(_no), "should NOT get a level: " + _no
# review F2 (a question for Skyy, default kept = the safe option): neutral ANIMALS with an attack stay unlevelled (Skyy R5 "animals
# never"; Boar / Warthog are in because Skyy named boars). Listed in the header so Skyy can add them to "Extra mobs that get levels".
NEUTRAL_LEFT_OUT = ["Mosshorn", "Mosshorn_Plain", "Cow", "Horse", "Moose_Bull", "Moose_Cow", "Bison", "Ram", "Camel", "Antelope", "Goat",
                    "Deer_Stag", "Horse_Skeleton", "Horse_Skeleton_Armored", "Kweebec_Razorleaf", "Kweebec_Razorleaf_Patrol"]
for _n in NEUTRAL_LEFT_OUT:
    assert ATT.get(_n) == "NEUTRAL" and not levelled(_n) and levelled(_n, [_n]), "neutral left-out list: " + _n

# zone folders (classic worldgen): region -> biome names (Tile./Custom. prefix and .json stripped = Biome.getName(), bytecode-checked)
REGION_BIOMES = {}
for _n in AZ_NAMES:
    _m = re.match(r"^Server/World/Default/Zones/([^/]+)/(Tile|Custom)\.([^/]+)\.json$", _n)
    if _m:
        REGION_BIOMES.setdefault(_m.group(1), set()).add(_m.group(3))
ENV_IDS = set(_n.rsplit("/", 1)[1][:-5] for _n in AZ_NAMES if _n.startswith("Server/Environments/") and _n.endswith(".json"))
VOLCANIC_ENVS = ["Env_Zone1_Caves_Volcanic_T1", "Env_Zone1_Caves_Volcanic_T2", "Env_Zone1_Caves_Volcanic_T3",
                 "Env_Zone2_Caves_Volcanic_T1", "Env_Zone2_Caves_Volcanic_T2", "Env_Zone2_Caves_Volcanic_T3",
                 "Env_Zone3_Caves_Volcanic_T1", "Env_Zone3_Caves_Volcanic_T2", "Env_Zone3_Caves_Volcanic_T3", "Env_Zone4_Caves_Volcanic"]
for _e in VOLCANIC_ENVS:
    assert _e in ENV_IDS, "volcanic cave environment %s is not in Assets.zip" % _e
assert not [e for e in ENV_IDS if "Volcanic" in e and e not in VOLCANIC_ENVS], "an unlisted volcanic environment exists"

# ================================================================= the default tables (refit section 3 + 4.2; plan 4.5 / 4.6 for Zone 4)
# (key, min, max). Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60.
BIOME_ROWS = [
    # ---- Zone 1 Emerald Wilds 1-20 (refit 3, Zone 1)
    ("Zone1_Spawn.*", 1, 3), ("Zone1_Temple.*", 1, 3),
    ("Zone1_Tier1.Plains_Smooth", 1, 3), ("Zone1_Tier1.Plains_Birch", 3, 5),
    ("Zone1_Tier1.Forest_Birch", 5, 7), ("Zone1_Tier1.Forest_Flower", 5, 7),
    ("Zone1_Tier1.Mountain_Tier1", 5, 7), ("Zone1_Tier1.*_Trork", 5, 7), ("Zone1_Tier1.*", 1, 7),
    ("Zone1_Tier2.Plains_Gorge", 7, 9), ("Zone1_Tier2.Plains_Tallgrass", 9, 11),
    ("Zone1_Tier2.Forest_Aspen", 10, 12), ("Zone1_Tier2.Forest_Gully", 10, 12),
    ("Zone1_Tier2.Mountain_Tier2", 10, 12), ("Zone1_Tier2.*_Trork", 10, 12), ("Zone1_Tier2.*", 7, 12),
    ("Zone1_Tier3.Plains_Gorge", 12, 14), ("Zone1_Tier3.Forest_Swamp", 16, 18),
    ("Zone1_Tier3.Mountain_Tier3", 16, 18), ("Zone1_Tier3.*_Trork", 16, 18),
    ("Zone1_Tier3.Forest_Autumn", 18, 20), ("Zone1_Tier3.Forest_Moss", 18, 20), ("Zone1_Tier3.Forest_Azure", 18, 20),
    ("Zone1_Tier3.*", 12, 20),
    ("Zone1_Shore.*", 1, 3),
    # ---- Zone 2 Howling Sands 20-30
    ("Zone2_Tier1.Savannah_Forest", 20, 22), ("Zone2_Tier1.Savannah_Plains", 20, 22), ("Zone2_Tier1.Savannah_Boab", 20, 22),
    ("Zone2_Tier1.Savannah_Rock", 20, 22), ("Zone2_Tier1.Savannah_Mudflats", 20, 22),
    ("Zone2_Tier1.Plateau_*", 21, 23), ("Zone2_Tier1.Scrub_Bushland", 22, 24), ("Zone2_Tier1.*", 20, 24),
    ("Zone2_Tier2.Desert_Oasis", 25, 27), ("Zone2_Tier2.Desert_Rock", 25, 27), ("Zone2_Tier2.Desert_Springs", 25, 27),
    ("Zone2_Tier2.Desert_Red", 25, 27), ("Zone2_Tier2.*", 25, 27),
    ("Zone2_Tier3.Desert_Barren", 27, 29), ("Zone2_Tier3.Desert_Mushroom", 27, 29),
    ("Zone2_Tier3.Plateau_Desert_*", 28, 30), ("Zone2_Tier3.Desert_Oasis_Hidden*", 28, 30),
    ("Zone2_Tier3.Scrub_Tar_Pits", 28, 30), ("Zone2_Tier3.Desert_Mushroom_Foot", 28, 30), ("Zone2_Tier3.*", 27, 30),
    ("Zone2_Shore.*", 20, 22),
    # ---- Zone 3 Whisperfrost Frontiers 30-45
    ("Zone3_Tier1.Forest_Redwood", 30, 32), ("Zone3_Tier1.Plains_Shire", 30, 32),
    ("Zone3_Tier1.Forest_Fir", 32, 34), ("Zone3_Tier1.Forest_Tundra", 32, 34), ("Zone3_Tier1.Plains_Hotsprings", 32, 34),
    ("Zone3_Tier1.Mountain_*", 32, 34), ("Zone3_Tier1.*", 30, 34),
    ("Zone3_Tier2.Forest_Cedar", 36, 38),
    ("Zone3_Tier2.Plains_Frozen", 37, 39), ("Zone3_Tier2.Forest_Cedar_Mixed", 37, 39), ("Zone3_Tier2.Plains_Tundra", 37, 39),
    ("Zone3_Tier2.Mountain_*", 37, 39), ("Zone3_Tier2.*", 36, 39),
    ("Zone3_Tier3.Forest_Frozen", 41, 43), ("Zone3_Tier3.Forest_Frozen_Light", 41, 43), ("Zone3_Tier3.Plains_Frozen_Frost", 41, 43),
    ("Zone3_Tier3.Mountain_*", 43, 45), ("Zone3_Tier3.*", 41, 45),
    ("Zone3_Shore_Tier1.*", 30, 32), ("Zone3_Shore_Tier2.*", 36, 38), ("Zone3_Shore_Tier3.*", 41, 43),
    # ---- Zone 4 Devastated Lands 45-60 (plan 4.5, unchanged by the refit)
    ("Zone4_Tier4.Wastes_Grasslands", 45, 47), ("Zone4_Tier4.Wastes_Geysers", 48, 50), ("Zone4_Tier4.Forest_Ghost", 48, 50),
    ("Zone4_Tier4.Desert_Dunes", 48, 50), ("Zone4_Tier4.Forest_Swamp", 48, 50), ("Zone4_Tier4.*", 45, 50),
    ("Zone4_Tier5.Desert_Ash", 53, 55), ("Zone4_Tier5.Wastes_Ash", 53, 55), ("Zone4_Tier5.Wastes_Lava", 55, 57),
    ("Zone4_Tier5.Forest_Burned", 58, 60), ("Zone4_Tier5.Forest_Roots", 58, 60), ("Zone4_Tier5.*", 53, 60),
    ("Zone4_Shore_Tier4.*", 45, 47), ("Zone4_Shore_Tier5.*", 53, 55),
]
# (key, min, max, bonus): refit 4.2 for Zones 1-3, plan 4.6 for Zone 4 and the 0.7 portal shards (unchanged)
ENV_ROWS = [
    ("Env_Zone1_Plains", 1, 3, 0), ("Env_Zone1_Shores", 1, 3, 0), ("Env_Zone1_Kweebec", 1, 3, 0),
    ("Env_Zone1_Forests", 5, 9, 0), ("Env_Zone1_Mountains", 5, 14, 0), ("Env_Zone1_Trork", 5, 16, 0),
    ("Env_Zone1_Swamps", 14, 20, 0), ("Env_Zone1_Autumn", 16, 20, 0), ("Env_Zone1_Azure", 16, 20, 0),
    ("Env_Zone1_Caves*", 5, 14, 0),
    ("Env_Zone1_Caves_Volcanic_T1", 5, 9, 0), ("Env_Zone1_Caves_Volcanic_T2", 9, 14, 0), ("Env_Zone1_Caves_Volcanic_T3", 14, 18, 0),
    ("Env_Zone1_Caves_Goblins", 5, 16, 1), ("Env_Zone1_Mineshafts", 5, 16, 1),
    ("Env_Zone1_Encounters", 9, 18, 2), ("Env_Zone1_Graveyard", 9, 18, 2), ("Env_Zone1_Mage_Towers", 9, 18, 2),
    ("Env_Zone1_Dungeons", 14, 20, 2),
    ("Env_Zone2_Savanna", 20, 22, 0), ("Env_Zone2_Shores", 20, 22, 0), ("Env_Zone2_Scrub", 22, 24, 0),
    ("Env_Zone2_Plateaus", 21, 27, 0), ("Env_Zone2_Deserts", 25, 29, 0), ("Env_Zone2_Oasis", 25, 30, 0),
    ("Env_Zone2_Feran", 23, 28, 1), ("Env_Zone2_Scarak", 23, 28, 1),
    ("Env_Zone2_Caves*", 21, 27, 0),
    ("Env_Zone2_Caves_Volcanic_T1", 21, 23, 0), ("Env_Zone2_Caves_Volcanic_T2", 25, 27, 0), ("Env_Zone2_Caves_Volcanic_T3", 28, 30, 0),
    ("Env_Zone2_Mineshafts", 23, 27, 1), ("Env_Zone2_Caves_Goblins", 23, 27, 1),
    ("Env_Zone2_Encounters", 25, 29, 2), ("Env_Zone2_Mage_Towers", 25, 29, 2), ("Env_Zone2_Dungeons", 27, 30, 2),
    ("Env_Zone3_Tundra", 30, 35, 0), ("Env_Zone3_Shores", 30, 33, 0), ("Env_Zone3_Forests", 30, 38, 0),
    ("Env_Zone3_Mountains", 35, 41, 0), ("Env_Zone3_Glacial", 38, 45, 0), ("Env_Zone3_Caves*", 32, 41, 0),
    ("Env_Zone3_Trork", 35, 42, 1), ("Env_Zone3_Outlander*", 39, 45, 2), ("Env_Zone3_Encounters", 39, 45, 2),
    ("Env_Zone4_Wastes", 45, 50, 0), ("Env_Zone4_Shores", 45, 47, 0), ("Env_Zone4_Crucible", 48, 50, 0),
    ("Env_Zone4_Volcanoes", 48, 57, 0), ("Env_Zone4_Forests", 48, 60, 0), ("Env_Zone4_Jungles", 50, 58, 0),
    ("Env_Zone4_Encounters*", 53, 60, 2), ("Env_Zone4_Villages*", 55, 60, 2),
    ("Env_Portal_Goblin_Surface", 5, 8, 0), ("Env_Portal_Goblin_Cave", 7, 10, 0), ("Env_Portal_Goblin_Cave_Deep", 9, 11, 0),
    ("Env_Portal_Goblin_Cave_Void", 10, 12, 0),
]
ZONE_ROWS = [("Zone1", 1, 7), ("Zone2", 20, 24), ("Zone3", 30, 34), ("Zone4", 45, 50)]
# The config kit refuses * in a table entry (CfgRows.entryErr: only entry=itemprefix tables take a trailing *), so the shipped tables
# hold NO pattern keys - every number stays editable in Server Setup: "Region.*" becomes the plain region key "Region" (its fallback
# row) and every other pattern is expanded HERE into one explicit row per matching biome / environment of Assets.zip (exact rows win).
# The runtime still understands * keys (MobBands.find) for hand-edited files.
BIOME_PATTERNS = list(BIOME_ROWS)
ENV_PATTERNS = list(ENV_ROWS)
ZONE_TOPS = {1: 20, 2: 30, 3: 45, 4: 60}
ZONE_FLOORS = {1: 1, 2: 20, 3: 30, 4: 45}
PASS_DEF = "River_*,Lake*,Dunes_*,*_Mudflats,*_Kweebec,Valley_*,Canyon_*,Caldera_*,Hills_*,Volcano_*,Village_*,*_Village,*_Town,Town_*"
COLOR_ROWS = [("1", SUI.COLOR["rowName"]), ("20", SUI.COLOR["warning"]), ("30", SUI.COLOR["gold"]), ("45", SUI.COLOR["error"]),
              ("61", SUI.RARITY["Mythic"])]
TEST_RED = SUI.COLOR["error"]
STRIP_DEF = "_Wander,_Patrol,_Surge,_Static,_Sleep"
FORMAT_DEF = "[Lv {level}] {name}"

# build checks on the pattern tables: every key names a real region / biome / environment of Assets.zip
for _k, _a, _b in BIOME_PATTERNS:
    _reg, _, _bio = _k.partition(".")
    assert _reg in REGION_BIOMES, "biome row %s: no region folder %s" % (_k, _reg)
    assert 0 < _a <= _b, _k
    if "*" in _bio:
        assert _bio == "*" or any(glob(_bio, x) for x in REGION_BIOMES[_reg]), "biome row %s matches no biome of %s" % (_k, _reg)
    else:
        assert _bio in REGION_BIOMES[_reg], "biome row %s: %s has no biome %s" % (_k, _reg, _bio)
    _z = int(_k[4])
    assert ZONE_FLOORS[_z] <= _a and _b <= ZONE_TOPS[_z], "biome row %s outside the Zone %d band" % (_k, _z)


def expand_biomes(rows):
    exact = set(k for k, _a, _b in rows if "*" not in k)
    out = []
    for k, a, b in rows:
        reg, _, bio = k.partition(".")
        if bio == "*":
            out.append((reg, a, b))
        elif "*" in bio:
            for x in sorted(REGION_BIOMES[reg]):
                if glob(bio, x) and "%s.%s" % (reg, x) not in exact:
                    out.append(("%s.%s" % (reg, x), a, b))
        else:
            out.append((k, a, b))
    return out


def expand_envs(rows):
    exact = set(k for k, _a, _b, _c in rows if "*" not in k)
    out = []
    for k, a, b, c in rows:
        if "*" in k:
            for e in sorted(ENV_IDS):
                if glob(k, e) and e not in exact:
                    out.append((e, a, b, c))
        else:
            out.append((k, a, b, c))
    return out


BIOME_ROWS = expand_biomes(BIOME_PATTERNS)
for _z in ZONE_TOPS:
    _rows = [r for r in BIOME_ROWS if r[0].startswith("Zone%d_" % _z)]
    assert min(r[1] for r in _rows) == ZONE_FLOORS[_z] and max(r[2] for r in _rows) == ZONE_TOPS[_z], "Zone %d band" % _z
assert len(set(r[0].lower() for r in BIOME_ROWS)) == len(BIOME_ROWS)
for _k, _a, _b, _c in ENV_PATTERNS:
    assert 0 < _a <= _b and 0 <= _c <= 10, _k
    if _k.startswith("Env_Portal_"):
        continue        # the 0.7 pre-release goblin shard environments (plan 4.6): not in the release Assets.zip
    if "*" in _k:
        assert any(glob(_k, e) for e in ENV_IDS), "env row %s matches no environment" % _k
    else:
        assert _k in ENV_IDS, "env row %s: no such environment" % _k
ENV_ROWS = expand_envs(ENV_PATTERNS)
assert len(set(r[0].lower() for r in ENV_ROWS)) == len(ENV_ROWS)
assert not [r for r in BIOME_ROWS + ENV_ROWS if "*" in r[0]], "a * key left in the shipped tables"


def _band_lines():
    L = ["# SkyyMobs %s level bands. In game: SkyWynn Menu > Server Setup > Mobs > Level bands; /mobs reload re-reads this file." % VERSION,
         "# Every line: <table>.<key>=<lowest level>,<highest level> (environment lines add a third number: the bonus).",
         "# A mob rolls a random level inside its band when it spawns. A band change only reaches new spawns (mobs keep their level).",
         "# Lookup (first match wins): world > private island > lava cave > biome > environment > zone > default (config.properties).",
         "# Biome keys: <Region>.<Biome> for one biome, or <Region> alone for every other biome of that region (its fallback).",
         "",
         "# ---- biome.<Region>.<Biome> / biome.<Region>: classic Hytale worlds (the worldgen zone folder + its tile or overlay biome) ----"]
    zname = {1: "Zone 1 Emerald Wilds: Lv 1-20 (the blue forest Forest_Azure, Autumn and Moss at the top)",
             2: "Zone 2 Howling Sands: Lv 20-30", 3: "Zone 3 Whisperfrost Frontiers: Lv 30-45", 4: "Zone 4 Devastated Lands: Lv 45-60"}
    last = None
    for k, a, b in BIOME_ROWS:
        z = int(k[4])
        if z != last:
            L.append("# " + zname[z])
            last = z
        L.append("biome.%s=%d,%d" % (k, a, b))
    L += ["", "# ---- env.<Environment>=<min>,<max>,<bonus>: the band where no biome is known (islands, World Gen 2); the bonus is added",
          "# on top of a biome band (encounters, dungeons, camps). Lava caves (Env_ZoneN_Caves_Volcanic*) use the zone's hardest biome. ----"]
    for k, a, b, c in ENV_ROWS:
        L.append("env.%s=%d,%d,%d" % (k, a, b, c))
    L += ["", "# ---- zone.<ZoneN>: fallback when only the zone is known (region ZoneN_..., environment Env_ZoneN_...) ----"]
    for k, a, b in ZONE_ROWS:
        L.append("zone.%s=%d,%d" % (k, a, b))
    L += ["", "# ---- world.<world name or its start>=<min>,<max>: one band for a whole world (dungeon_ = every world named dungeon_...;",
          "# 0,0 = no levels there). None by default. ----"]
    return L


BANDS_TEXT = "\n".join(_band_lines()) + "\n"
CFG_LINES = [
    "# SkyyMobs %s settings (mob levels). In game: SkyWynn Menu > Server Setup > Mobs; /mobs reload re-reads this file." % VERSION,
    "# The level bands are in bands.properties next to this file.",
    "# Mob levels (false = new mobs get no level; mobs that have one keep it).",
    "part.levels=true",
    "# Neutral mobs that fight back when hit (boars, Scaraks, Feran warriors) get levels too.",
    "levels.neutral=true",
    "# Extra mobs that get levels (other mods' mobs): role ids or Prefix* patterns, comma separated. Vanilla hostile mobs and the",
    "# neutral fighters (boars, warthogs, Scaraks, Feran warriors) are built in; vanilla animals only get a level when listed here.",
    "levels.roles=" + ROLES_DEF,
    "# Never level these, even when built in or listed above: tests, tamed animals, temple NPCs, traders, summons, bosses and",
    "# other mods' mounts / pets / NPCs. * = no mob gets a level: every levelled mob loses its level + plate the next time it loads.",
    "levels.exclude=" + EXCLUDE_DEF,
    "# Highest mob level (band + bonus never goes above this).",
    "levels.max=100",
    ROLE_DOC,           # 0.1.4: scale.role (Fixed level by role) - no entries by default; MobMig14 puts this line after levels.max
    MG_MARK,            # 0.1.1: the default file carries the update marker (MobMig never touches a fresh file), where MobMig puts it
    DOC_NEW,
    "strength.difficulty=" + DIFF_DEF,
    "# Custom difficulty only: health and damage added per level above 1, in percent.",
    "strength.hp=" + num(CUSTOM[0]),
    "strength.dmg=" + num(CUSTOM[1]),
    "# Highest health and damage multipliers.",
    "strength.hpCap=" + num(CAPS[0]),
    "strength.dmgCap=" + num(CAPS[1]),
    FLOOR_DOC,                          # 0.1.2: the floor (a file without these lines uses the code default 50 - no update step)
    "strength.floor=%d" % FLOOR_DEF,
    "# Heal a mob to full when its chunk reloads (false = a wounded mob keeps its health share).",
    "strength.healOnLoad=false",
    # 0.1.4: the level curve block (the fresh file carries MobMig14's marker + exactly the block MobMig14 adds to an older file)
    MG14_MARK] + [ln for _key, _lines in mg14_groups(SHAPE_DEF) for ln in _lines] + [
    "# Overlay biomes that use the land biome underneath them (rivers, lakes, dunes, valleys, villages ...).",
    "bands.passThrough=" + PASS_DEF,
    "# Vanilla's deep lava caves (Env_ZoneN_Caves_Volcanic*) use the band of the zone's hardest biome.",
    "bands.volcanicTop=true",
    "# SkyyIslands private islands: a level range like 1-3, or 0 for no levels.",
    "bands.islands=0",
    "# Level range when nothing matches (0 = no level).",
    "bands.default=0",
    "# Nameplates: all (every levelled mob) or off.",
    "plate.mode=all",
    "# Nameplate text: {level} = the level, {name} = the mob's name.",
    "plate.format=" + FORMAT_DEF,
    "# Role id endings dropped when a mob has no translated name.",
    "plate.strip=" + STRIP_DEF,
    "# TRIAL (the client may not draw colours): colour the nameplate by level. Run /mobs platetest first and pick the markup that works.",
    "plate.colorOn=false",
    "# Colour markup: tag (<color=#rrggbb>), section (section sign colour codes) or brace ({#rrggbb}).",
    "plate.markup=tag",
    "# Level colours: plate.colors.<lowest level of the band>=#rrggbb",
] + ["plate.colors.%s=%s" % (k, v) for k, v in COLOR_ROWS]
CFG_TEXT = "\n".join(CFG_LINES) + "\n"
for _t in (CFG_TEXT, BANDS_TEXT):
    assert all(ord(c) < 127 for c in _t), "default files must be plain ASCII"
assert CFG_TEXT.count(MG_MARK_ID) == 1 and CFG_TEXT.count(DOC_NEW) == 1 and DOC_OLD not in CFG_TEXT
assert CFG_TEXT.index(MG_MARK) < CFG_TEXT.index(DOC_NEW) < CFG_TEXT.index("strength.difficulty="), "the marker sits on top of the difficulty block"
assert CFG_TEXT.count(MG14_MARK_ID) == 1 and CFG_TEXT.index("strength.healOnLoad=false") < CFG_TEXT.index(MG14_MARK) < CFG_TEXT.index("bands.passThrough=")
assert CFG_TEXT.index("levels.max=100\n" + ROLE_DOC + "\n") > 0 and sum(1 for ln in CFG_LINES if ln.startswith("curve.")) == 80

# ================================================================= JVM + engine classes (every member probed: a missing one fails the build)
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.mobs"
T = {
    "PKG": PKG, "VERSION": VERSION,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "HOLD": "com.hypixel.hytale.component.Holder",
    "CTYPE": "com.hypixel.hytale.component.ComponentType",
    "COMP": "com.hypixel.hytale.component.Component",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "WCFG": "com.hypixel.hytale.server.core.universe.world.WorldConfig",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "ENVA": "com.hypixel.hytale.server.core.asset.type.environment.config.Environment",
    "ILT": "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap",
    "CGEN": "com.hypixel.hytale.server.worldgen.chunk.ChunkGenerator",
    "ZBR": "com.hypixel.hytale.server.worldgen.chunk.ZoneBiomeResult",
    "ZGR": "com.hypixel.hytale.server.worldgen.zone.ZoneGeneratorResult",
    "ZONE": "com.hypixel.hytale.server.worldgen.zone.Zone",
    "ZDC": "com.hypixel.hytale.server.worldgen.zone.ZoneDiscoveryConfig",
    "BIOME": "com.hypixel.hytale.server.worldgen.biome.Biome",
    "BPG": "com.hypixel.hytale.server.worldgen.biome.BiomePatternGenerator",
    "NPCE": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ROLE": "com.hypixel.hytale.server.npc.role.Role",
    "WSUP": "com.hypixel.hytale.server.npc.role.support.WorldSupport",
    "ATT": "com.hypixel.hytale.server.core.asset.type.attitude.Attitude",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "SMO": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MODF": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier",
    "MTG": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "VEC": "org.joml.Vector3d",
    "HSYS": "com.hypixel.hytale.component.system.HolderSystem",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "INTL": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "TGT": "com.hypixel.hytale.server.core.util.TargetUtil",
    "PMGR": "com.hypixel.hytale.server.core.plugin.PluginManager",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "UNIV": "com.hypixel.hytale.server.core.universe.Universe",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    # every player command: its auto permission node goes to the default player group (vanilla /help /who pattern)
    "ADV": 'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    # admin sub-commands under a player command: own node AND no groups (lint perm_group_leaks; SkyyIslands 0.5 lesson)
    "ADMIN": 'requirePermission("%s"); setPermissionGroups(new String[0]);' % NODE,
    "KEYP": KEY_PREFIX,
    "KITID": KIT_ID,
}
# 0.1.1: the ladder as Java literals (MobCfg fields, derive, apply) - from the one Python table above
T.update({"DIFDEF": DIFF_DEF,
          "EASYH": repr(PRESETS["easy"][0]), "EASYD": repr(PRESETS["easy"][1]),
          "NORMH": repr(PRESETS["normal"][0]), "NORMD": repr(PRESETS["normal"][1]),
          "HARDH": repr(PRESETS["hard"][0]), "HARDD": repr(PRESETS["hard"][1]),
          "DEFH": repr(PRESETS[DIFF_DEF][0]), "DEFD": repr(PRESETS[DIFF_DEF][1]),
          "STEPH": repr(PRESETS[DIFF_DEF][0] / 100.0), "STEPD": repr(PRESETS[DIFF_DEF][1] / 100.0),
          "CUSTH": repr(CUSTOM[0]), "CUSTD": repr(CUSTOM[1]),
          "HPCAP": repr(CAPS[0]), "DMGCAP": repr(CAPS[1]),
          "FLDEF": str(FLOOR_DEF), "FLMAX": str(FLOOR_MAX)})          # 0.1.2: the floor row default / max
# 0.1.4: the shape default, the gap row defaults, Hard's per-level step (hardRef in Per level shape), the class level cache time
T.update({"SHPDEF": SHAPE_DEF, "GFREE": str(GAP_DEF["free"]), "GDSTEP": repr(GAP_DEF["dealtStep"]), "GDMIN": repr(GAP_DEF["dealtMin"]),
          "GTSTEP": repr(GAP_DEF["takenStep"]), "GTMAX": repr(GAP_DEF["takenMax"]), "HARDS": repr(HARD_STEP), "GTTL": str(GAP_TTL_MS)})
assert (T["STEPH"], T["STEPD"], T["HPCAP"], T["DMGCAP"]) == ("0.06", "0.03", "6.0", "3.5")
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
CRP = "com.hypixel.hytale.component.ComponentRegistryProxy"
ROLEB = "com.hypixel.hytale.server.npc.systems.RoleBuilderSystem"
SETUPS = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Setup"
BALS = "com.hypixel.hytale.server.npc.systems.BalancingInitialisationSystem"
ADRS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction"


def jdesc(t):
    if t.endswith("[]"):
        return "[" + jdesc(t[:-2])
    prim = {"int": "I", "long": "J", "float": "F", "double": "D", "boolean": "Z", "void": "V", "char": "C", "byte": "B", "short": "S"}
    return prim[t] if t in prim else "L" + t.replace(".", "/") + ";"


def probe_sig(cls, name, ret, args):
    """the exact member: cls.name(args) -> ret (own or inherited); a missing one stops the build (UNVERIFIED engine members)"""
    desc = "(" + "".join(jdesc(a) for a in args) + ")" + jdesc(ret)
    c = pool.get(cls)
    try:
        if name == "<init>":
            c.getConstructor(desc)
        else:
            c.getMethod(name, desc)
    except Exception:
        raise SystemExit("API probe failed: %s.%s%s not found" % (cls, name, desc))
    PROBED.append("%s.%s%s" % (cls.rsplit(".", 1)[1], name, desc))


PROBED = []
G = T
SIGS = [
    # spawn point / spawn environment / role (plan section 12)
    (G["NPCE"], "getComponentType", G["CTYPE"], []), (G["NPCE"], "getEnvironment", "int", []),
    (G["NPCE"], "getLeashPoint", G["VEC"], []), (G["NPCE"], "getRoleName", "java.lang.String", []),
    (G["NPCE"], "getRole", G["ROLE"], []), (G["ROLE"], "getNameTranslationKey", "java.lang.String", []),
    (G["WSUP"], "getComponentType", G["CTYPE"], []), (G["WSUP"], "getDefaultPlayerAttitude", G["ATT"], []),
    # nameplate
    (G["NPL"], "getComponentType", G["CTYPE"], []), (G["NPL"], "setText", "void", ["java.lang.String"]),
    (G["NPL"], "getText", "java.lang.String", []),
    # health modifier (the save slot)
    (G["ESM"], "getComponentType", G["CTYPE"], []), (G["ESM"], "get", G["ESV"], ["int"]),
    (G["ESM"], "putModifier", G["MODF"], ["int", "java.lang.String", G["MODF"]]),
    (G["ESM"], "getModifier", G["MODF"], ["int", "java.lang.String"]),
    (G["ESM"], "removeModifier", G["MODF"], ["int", "java.lang.String"]),
    # 0.1.3 (F1): the health write after a modifier change - Min / Max network entries are never merged into the pending PutModifier /
    # RemoveModifier entry (EntityStatMap.tryMergeUpdate); setStatValue / maximizeStatValue are no longer referenced
    (G["ESM"], "minStatValue", "float", ["int", "float"]), (G["ESM"], "maxStatValue", "float", ["int", "float"]),
    (G["ESV"], "get", "float", []), (G["ESV"], "getMax", "float", []), (G["ESV"], "getModifiers", "java.util.Map", []),
    (G["SMO"], "<init>", "void", [G["MTG"], G["CAL"], "float"]), (G["SMO"], "getAmount", "float", []),
    # 0.1.2: the base health under our multiplier (MobLevel.baseOf reads the multiplicative MAX modifiers like computeModifiers)
    (G["MODF"], "getTarget", G["MTG"], []), (G["SMO"], "getCalculationType", G["CAL"], []),
    (G["DST"], "getHealth", "int", []),
    # classic worldgen lookup (NPCMemory$GatherMemoriesSystem.findLocationZoneName recipe, seed = (int) WorldConfig.getSeed())
    (G["CHS"], "getGenerator", "com.hypixel.hytale.server.core.universe.world.worldgen.IWorldGen", []),
    (G["CHS"], "getChunkComponent", G["COMP"], ["long", G["CTYPE"]]),
    (G["CGEN"], "getZoneBiomeResultAt", G["ZBR"], ["int", "int", "int"]),
    (G["ZBR"], "getBiome", G["BIOME"], []), (G["ZBR"], "getZoneResult", G["ZGR"], []), (G["ZGR"], "getZone", G["ZONE"], []),
    (G["ZONE"], "name", "java.lang.String", []), (G["ZONE"], "biomePatternGenerator", G["BPG"], []),
    (G["ZONE"], "discoveryConfig", G["ZDC"], []), (G["ZDC"], "zone", "java.lang.String", []),
    (G["BPG"], "getBiome", "com.hypixel.hytale.server.worldgen.biome.TileBiome", ["int", "int", "int"]),
    (G["BIOME"], "getName", "java.lang.String", []),
    # block environment (3D: BlockChunk.getEnvironment(int, int, int) - the Vector3d form is gone in 0.7)
    (G["BCH"], "getComponentType", G["CTYPE"], []), (G["BCH"], "getEnvironment", "int", ["int", "int", "int"]),
    (G["CHU"], "indexChunkFromBlock", "long", ["int", "int"]),
    (G["ENVA"], "getAssetMap", G["ILT"], []), (G["ENVA"], "getId", "java.lang.String", []),
    (G["ILT"], "getAsset", "com.hypixel.hytale.assetstore.map.JsonAssetWithMap", ["int"]),
    (G["WLD"], "getName", "java.lang.String", []), (G["WLD"], "getChunkStore", G["CHS"], []),
    (G["WLD"], "getWorldConfig", G["WCFG"], []), (G["WLD"], "getEntityStore", G["EST"], []),
    (G["WLD"], "execute", "void", ["java.lang.Runnable"]), (G["WCFG"], "getSeed", "long", []),
    (G["UNIV"], "get", G["UNIV"], []), (G["UNIV"], "getWorlds", "java.util.Map", []),     # the prune of removed worlds (review F6)
    (G["EST"], "getWorld", G["WLD"], []), (G["EST"], "getRefFromUUID", G["REF"], ["java.util.UUID"]), (G["EST"], "getStore", G["ST"], []),
    (G["ST"], "getExternalData", "java.lang.Object", []), (G["ST"], "getComponent", G["COMP"], [G["REF"], G["CTYPE"]]),
    (G["ST"], "ensureAndGetComponent", G["COMP"], [G["REF"], G["CTYPE"]]), (G["ST"], "tryRemoveComponent", "void", [G["REF"], G["CTYPE"]]),
    (G["HOLD"], "getComponent", G["COMP"], [G["CTYPE"]]), (G["HOLD"], "ensureAndGetComponent", G["COMP"], [G["CTYPE"]]),
    (G["HOLD"], "tryRemoveComponent", "boolean", [G["CTYPE"]]),
    (G["UUIDC"], "getComponentType", G["CTYPE"], []), (G["UUIDC"], "getUuid", "java.util.UUID", []),
    (G["TC"], "getComponentType", G["CTYPE"], []), (G["TC"], "getPosition", G["VEC"], []),
    (G["REF"], "isValid", "boolean", []),
    # the systems
    (G["HSYS"], "onEntityAdd", "void", [G["HOLD"], G["ADDR"], G["ST"]]),
    (G["HSYS"], "onEntityRemoved", "void", [G["HOLD"], G["REMR"], G["ST"]]),
    (G["SDEP"], "<init>", "void", [G["ORD"], "java.lang.Class"]),
    (G["QRY"], "and", "com.hypixel.hytale.component.query.AndQuery", [G["QRY"] + "[]"]),
    (G["QRY"], "any", "com.hypixel.hytale.component.query.AnyQuery", []),
    (G["DMOD"], "get", G["DMOD"], []), (G["DMOD"], "getFilterDamageGroup", G["SG"], []),
    (G["DMG"], "getAmount", "float", []), (G["DMG"], "setAmount", "void", ["float"]), (G["DMG"], "getSource", G["DSRC"], []),
    (G["DMG"], "isCancelled", "boolean", []), (G["DENT"], "getRef", G["REF"], []),
    (G["CB"], "getComponent", G["COMP"], [G["REF"], G["CTYPE"]]),
    # 0.1.4: the level gap - the victim of a hit (the chunk's entity) and the player test (PlayerRef on the attacker / victim ref,
    # SkyySkills CombatDmgSys' pattern); a projectile hit's source is a Damage$ProjectileSource = an EntitySource whose ref is the shooter
    (G["ACH"], "getReferenceTo", G["REF"], ["int"]), (G["PR"], "getComponentType", G["CTYPE"], []),
    ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource", "getRef", G["REF"], []),
    (CRP, "registerSystem", "void", ["com.hypixel.hytale.component.system.ISystem"]),
    (PB, "getEntityStoreRegistry", CRP, []), (PB, "getCommandRegistry", "com.hypixel.hytale.server.core.command.system.CommandRegistry", []),
    (PB, "getDataDirectory", "java.nio.file.Path", []), (PB, "getLogger", G["LOG"], []), (PB, "shutdown", "void", []),
    # names, commands, look target, plugins
    (G["INTL"], "get", G["INTL"], []), (G["INTL"], "getMessage", "java.lang.String", ["java.lang.String", "java.lang.String"]),
    (G["TGT"], "getTargetEntity", G["REF"], [G["REF"], "com.hypixel.hytale.component.ComponentAccessor"]),
    (G["PMGR"], "get", G["PMGR"], []), (G["PMGR"], "getPlugins", "java.util.List", []),
    (AC, "setPermissionGroups", "void", ["java.lang.String[]"]), (AC, "requirePermission", "void", ["java.lang.String"]),
    (AC, "addSubCommand", "void", [AC]),
    (G["CTX"], "get", "java.lang.Object", ["com.hypixel.hytale.server.core.command.system.arguments.system.Argument"]),
    (G["PR"], "getUuid", "java.util.UUID", []), (G["PR"], "getUsername", "java.lang.String", []),
    (G["PR"], "sendMessage", "void", [G["MSG"]]), (G["MSG"], "raw", G["MSG"], ["java.lang.String"]),
    (G["MSG"], "color", G["MSG"], ["java.lang.String"]),
]
for _c, _m, _r, _a in SIGS:
    probe_sig(_c, _m, _r, _a)
for _c, _m in ((G["MTG"], "MAX"), (G["CAL"], "MULTIPLICATIVE"), (G["ADDR"], "SPAWN"), (G["REMR"], "UNLOAD"), (G["REMR"], "REMOVE"),
               (G["ORD"], "AFTER"), (G["ORD"], "BEFORE"), (G["ATT"], "HOSTILE"), (G["ATT"], "NEUTRAL"), (G["VEC"], "x"),
               (G["VEC"], "y"), (G["VEC"], "z"), (G["HSV"], "SCHEDULED_EXECUTOR"), (G["ATY"], "STRING"), (AC, "withRequiredArg")):
    B.probe(pool, _c, _m)
    PROBED.append("%s.%s" % (_c.rsplit(".", 1)[1], _m))
for _c in (ROLEB, SETUPS, BALS, ADRS):
    pool.get(_c)          # the classes our systems order against (looked up again at runtime with Class.forName)
# 0.1.4: a projectile hit's source IS an EntitySource (its getRef = the shooter), so the gap and the level damage see the shooter
assert pool.get("com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource").subclassOf(pool.get(G["DENT"]))
print("engine members probed: %d" % len(PROBED))

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def jstr(s):
    assert all(32 <= ord(c) < 127 for c in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jtext(s):
    """a multi-line Java string literal (\\n escapes) of a plain ASCII text"""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# ================================================================= classes (all top-level; methods before callers)
lg = pool.makeClass(PKG + ".MobLog")
gb = pool.makeClass(PKG + ".MobGlob")
bd = pool.makeClass(PKG + ".MobBands")
mi = pool.makeClass(PKG + ".MobInfo")
cfg = pool.makeClass(PKG + ".MobCfg")
lv = pool.makeClass(PKG + ".MobLevel")
hk = pool.makeClass(PKG + ".LevelHook", pool.get(G["HSYS"]))
dm = pool.makeClass(PKG + ".LevelDamage", pool.get(G["DES"]))
dmu = pool.makeClass(PKG + ".LevelDamageU", dm)
fn = pool.makeClass(PKG + ".MobLevelFn")
ps = pool.makeClass(PKG + ".MobPlateStep")
sc = pool.makeClass(PKG + ".MobScanTask")
pt = pool.makeClass(PKG + ".MobPruneTask")
rf = pool.makeClass(PKG + ".MobRefresh")  # 0.1.2: the live health re-apply (dispatcher + one task per world on its world thread)
mh = pool.makeClass(PKG + ".MobHooks")
mc = pool.makeClass(PKG + ".MobCmds")
mm = pool.makeClass(PKG + ".MobMig")      # 0.1.1: the one-time difficulty update of an existing config.properties (methods after the kit)
# 0.1.4: the level gap (pure maths + the class level cache), its damage system (+ the unordered fallback), mob:fn:info, the level curve update
gp = pool.makeClass(PKG + ".MobGap")
gd = pool.makeClass(PKG + ".GapDamage", pool.get(G["DES"]))
gdu = pool.makeClass(PKG + ".GapDamageU", gd)
ifn = pool.makeClass(PKG + ".MobInfoFn")
m14 = pool.makeClass(PKG + ".MobMig14")
pl = pool.makeClass(PKG + ".SkyyMobsPlugin", pool.get(G["JP"]))
ALL = [lg, gb, bd, mi, cfg, lv, hk, dm, dmu, fn, ps, sc, pt, rf, mh, mc, mm, gp, gd, gdu, ifn, m14]

# ---------------------------------------------------------------- MobLog: the server log (every class may call it)
F(lg, "public static @LOG@ LOG;")
F(lg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(lg, r"""
public static void info(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warn(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] WARN " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void error(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.SEVERE).log("[SkyyMobs] " + msg);
    else System.out.println("[SkyyMobs] ERROR " + msg);
  } catch (Throwable t) { }
}""")
M(lg, r"""
public static void warnOnce(String key, String msg) {
  if (key == null || ONCE.putIfAbsent(key, Boolean.TRUE) != null) return;
  warn(msg);
}""")

# ---------------------------------------------------------------- MobGlob: * patterns (lower case), comma lists
M(gb, r"""
public static boolean glob(String p, String s) {
  if (p == null || s == null) return false;
  int pi = 0, si = 0, star = -1, mark = 0;
  int pn = p.length(), sn = s.length();
  while (si < sn) {
    if (pi < pn && p.charAt(pi) != '*' && p.charAt(pi) == s.charAt(si)) { pi++; si++; }
    else if (pi < pn && p.charAt(pi) == '*') { star = pi; mark = si; pi++; }
    else if (star >= 0) { pi = star + 1; mark++; si = mark; }
    else return false;
  }
  while (pi < pn && p.charAt(pi) == '*') pi++;
  return pi == pn;
}""")
M(gb, r"""
public static int spec(String p) {
  int n = 0;
  for (int i = 0; p != null && i < p.length(); i++) if (p.charAt(i) != '*') n++;
  return n;
}""")
M(gb, r"""
public static String[] list(String csv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (csv != null) {
    String[] parts = csv.split(",");
    for (int i = 0; i < parts.length; i++) {
      String t = parts[i].trim().toLowerCase();
      if (t.length() > 0 && !out.contains(t)) out.add(t);
    }
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(gb, r"""
public static boolean any(String[] pats, String s) {
  if (pats == null || s == null) return false;
  String k = s.toLowerCase();
  for (int i = 0; i < pats.length; i++) if (glob(pats[i], k)) return true;
  return false;
}""")

# ---------------------------------------------------------------- MobBands: one band table (keys sorted, most specific match wins)
for f in ("public String name;", "public String[] raw;", "public String[] low;", "public int[] a;", "public int[] b;", "public int[] c;",
          "public int[] spec;", "public boolean[] wild;", "public java.util.HashMap exact;", "public int n;"):
    F(bd, f)
C(bd, r"""
public MobBands(String name, String[] raw, int[] a, int[] b, int[] c) {
  this.name = name;
  this.raw = raw; this.a = a; this.b = b; this.c = c;
  this.n = raw.length;
  this.low = new String[this.n];
  this.spec = new int[this.n];
  this.wild = new boolean[this.n];
  this.exact = new java.util.HashMap();
  for (int i = 0; i < this.n; i++) {
    this.low[i] = raw[i].toLowerCase();
    this.spec[i] = @PKG@.MobGlob.spec(this.low[i]);
    this.wild[i] = this.low[i].indexOf('*') >= 0;
    if (!this.wild[i] && !this.exact.containsKey(this.low[i])) this.exact.put(this.low[i], Integer.valueOf(i));
  }
}""")
M(bd, r"""
public int find(String key) {
  if (key == null || this.n == 0) return -1;
  String k = key.toLowerCase();
  Object o = this.exact.get(k);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int best = -1, bs = -1;
  for (int i = 0; i < this.n; i++) {
    if (!this.wild[i] || this.spec[i] <= bs) continue;
    if (@PKG@.MobGlob.glob(this.low[i], k)) { best = i; bs = this.spec[i]; }
  }
  return best;
}""")

# world rows: the exact name, else the longest key the name starts with (or a * pattern from a hand edit)
M(bd, r"""
public int findPrefix(String key) {
  int i = find(key);
  if (i >= 0 || key == null) return i;
  String k = key.toLowerCase();
  int best = -1, bl = 0;
  for (int j = 0; j < this.n; j++) {
    if (this.wild[j]) continue;
    if (this.low[j].length() > bl && k.startsWith(this.low[j])) { best = j; bl = this.low[j].length(); }
  }
  return best;
}""")

# ---------------------------------------------------------------- MobInfo: one loaded levelled mob
# wref = a WEAK reference to the World the mob lives in (the prune forgets mobs of removed worlds - review F6 - and never keeps a
# removed World alive)
for f in ("public String world;", "public java.util.UUID uuid;", "public String role;", "public String name;", "public int level;",
          "public String step;", "public String key;", "public int a;", "public int b;", "public int bonus;", "public long at;",
          "public java.lang.ref.WeakReference wref;",
          # 0.1.4: the mob's own max health under our multiplier (MobLevel.baseOf at apply / live re-apply; -1 = unknown) and the
          # scale.role Health x on it (1 = none) - mob:fn:info and the damage floor read them from any thread
          "public volatile double base;", "public volatile double rx;"):
    F(mi, f)
C(mi, "public MobInfo() { this.base = -1.0; this.rx = 1.0; }")

# MobLevel's maps first (MobCfg.derive clears the name cache)
F(lv, "public static final java.util.concurrent.ConcurrentHashMap MOBS = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap KEPT = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap WG = new java.util.concurrent.ConcurrentHashMap();")
F(lv, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
F(lv, 'public static final String KEY_PREFIX = "@KEYP@";')
F(lv, "public static final int KEPT_MAX = 50000;")
F(lv, "public static final int WG_MAX = 10000;")
# true once the level hook is registered (review F4: no unordered fallback - without the hook no mob gets a level this run)
F(lv, "public static volatile boolean HOOK = false;")
# the prune (review F6): a mob added less than PRUNE_GRACE ms ago is never pruned (a world that is still being added to the universe)
F(lv, "public static final long PRUNE_GRACE = 60000L;")
F(lv, "public static volatile java.util.concurrent.ScheduledFuture PRUNE;")

# ---------------------------------------------------------------- MobCfg: fields first (the config kit binds them), methods after emit
# 0.1.1: plain choice names - SkyyMenu 0.3.5 draws a 4-choice row as four 90 px buttons and cut "Easy 3% / 1.5%" to "Easy 3 / 1...";
# the numbers are in the row's help line (DIFF_HELP below). Values (easy / normal / hard / custom) = 0.1's.
DIFF_OPTS = "easy|Easy,normal|Normal,hard|Hard,custom|Custom"
assert [o.split("|")[0] for o in DIFF_OPTS.split(",")] == ["easy", "normal", "hard", "custom"] and sorted(PRESETS) == ["easy", "hard", "normal"]
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;", "public static java.nio.file.Path BANDS;",
          "public static volatile boolean ON = true;",
          "public static volatile boolean NEUTRAL = true;",
          "public static volatile String ROLES = %s;" % jstr(ROLES_DEF),
          "public static volatile String EXCLUDE = %s;" % jstr(EXCLUDE_DEF),
          "public static volatile int MAX_LEVEL = 100;",
          "public static volatile String DIFFICULTY = \"@DIFDEF@\";",
          "public static volatile double HP_PCT = @CUSTH@;",
          "public static volatile double DMG_PCT = @CUSTD@;",
          "public static volatile double HP_CAP = @HPCAP@;",
          "public static volatile double DMG_CAP = @DMGCAP@;",
          "public static volatile int HP_FLOOR = @FLDEF@;",                  # 0.1.2: strength.floor (base HP, 0 = off)
          "public static volatile boolean HEAL_ON_LOAD = false;",
          "public static volatile String PASS = %s;" % jstr(PASS_DEF),
          "public static volatile boolean VOLCANIC = true;",
          "public static volatile String ISLANDS = \"0\";",
          "public static volatile String DEFAULT_BAND = \"0\";",
          "public static volatile String PLATE_MODE = \"all\";",
          "public static volatile String FORMAT = %s;" % jstr(FORMAT_DEF),
          "public static volatile String STRIP = %s;" % jstr(STRIP_DEF),
          "public static volatile boolean COLOR_ON = false;",
          "public static volatile String MARKUP = \"tag\";",
          # derived (new arrays / objects are swapped in whole, never edited in place)
          "public static volatile String[] P_ROLES;", "public static volatile String[] P_EXCL;",
          "public static volatile String[] P_PASS;", "public static volatile String[] P_STRIP;",
          "public static volatile double HP_STEP = @STEPH@;", "public static volatile double DMG_STEP = @STEPD@;",
          "public static volatile int ISL_A = 0;", "public static volatile int ISL_B = 0;",
          "public static volatile int DEF_A = 0;", "public static volatile int DEF_B = 0;",
          "public static volatile @PKG@.MobBands BIOME;", "public static volatile @PKG@.MobBands ENV;",
          "public static volatile @PKG@.MobBands WORLD;", "public static volatile @PKG@.MobBands ZONE;",
          "public static volatile int[] COL_LV;", "public static volatile String[] COL_HEX;",
          "public static volatile int[] ZTOP_A;", "public static volatile int[] ZTOP_B;", "public static volatile String[] ZTOP_KEY;",
          "public static volatile long EPOCH = 0L;", "public static volatile String LOADED = \"\";",
          # 0.1.2: the health signature derive() saw last (health % per level | health cap | floor) and the live re-apply a change
          # starts (setup() puts a MobRefresh(null) here after the first load, shutdown clears it; null in a bare JVM)
          "public static volatile String HP_SIG = \"\";", "public static volatile Runnable ON_HEALTH;",
          # review F1: the built-in list = the exact vanilla role ids (lower-cased into VAN on first use)
          "public static final String VANILLA = %s;" % jstr(LEVELLED_TEXT),
          "public static volatile java.util.HashSet VAN;",
          # review F7: every plate format used this run (+ the default) still counts as our plate when a mob is stripped
          "public static final String FORMAT_DEFAULT = %s;" % jstr(FORMAT_DEF),
          "public static final java.util.concurrent.ConcurrentHashMap FORMATS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEF_CFG = %s;" % jtext(CFG_TEXT),
          "public static final String DEF_BANDS = %s;" % jtext(BANDS_TEXT),
          # 0.1.4: Strength shape (curve | linear), the damage floor / one hit at most (players only), the level gap rows
          "public static volatile String SHAPE = \"@SHPDEF@\";", "public static volatile boolean CURVE_ON = true;",
          "public static volatile int DMG_FLOOR = 0;", "public static volatile int HIT_CAP = 0;",
          "public static volatile boolean GAP_ON = true;", "public static volatile int GAP_FREE = @GFREE@;",
          "public static volatile double GAP_DSTEP = @GDSTEP@;", "public static volatile double GAP_DMIN = @GDMIN@;",
          "public static volatile double GAP_TSTEP = @GTSTEP@;", "public static volatile double GAP_TMAX = @GTMAX@;",
          # the 8 curve tables (index = kind x 4 + difficulty: hp easy / normal / hard / custom, then dmg ...), each Object[]{ double[]
          # levels, double[] factors } sorted by level; the whole array is swapped in by apply(), never edited in place
          "public static volatile Object[] CURVES;",
          "public static final String[] CURVE_DEF = %s;" % ("new String[] { " + ", ".join(jstr(t) for t in CURVE_DEF_TEXT) + " }"),
          "public static final String[] CURVE_KEY = %s;" % ("new String[] { " + ", ".join(jstr("curve.%s.%s" % kd) for kd in CURVE_IDX) + " }"),
          # scale.role (Fixed level by role): Object[]{ String[] raw, String[] low, int[] level, double[] health x } + its signature
          "public static volatile Object[] ROLES_TAB;", "public static volatile String ROLE_SIG = \"\";"):
    F(cfg, f)

# ================================================================= the config kit (Server Setup > Mobs)
CFG_FILE = "Skyy_SkyyMobs/config.properties"
BANDS_FILE = "Skyy_SkyyMobs/bands.properties"
# 0.1.1: the tab "Who gets levels" (15 characters) was cut by SkyyMenu's 14-character tab clip (drawn "Who gets le"); ids = 0.1's
# 0.1.4: + "Level curve" (the 8 curve tables) and "Level gap" (spec 6.1); the old ids / labels unchanged
CFG_CATS = [("levels", "Which mobs"), ("strength", "Strength"), ("curve", "Level curve"), ("gap", "Level gap"), ("bands", "Level bands"),
            ("plate", "Nameplate")]
# 0.1.1 help texts that carry the ladder (the Strength page says the numbers in force)
DIFF_HELP = ("Health / damage per level: Easy %s%% / %s%%, Normal %s%% / %s%%, Hard %s%% / %s%%. Custom = the two rows below."
             % (num(PRESETS["easy"][0]), num(PRESETS["easy"][1]), num(PRESETS["normal"][0]), num(PRESETS["normal"][1]),
                num(PRESETS["hard"][0]), num(PRESETS["hard"][1])))
# 0.1.2: the cap is on the per-level multiplier; the health floor goes on top of it (a floored mob's health / its own base may pass it)
HPCAP_HELP = "Health per level never goes above this multiple (x%s never clips Hard at Lv %d, which is x%.2f)." % (num(CAPS[0]), LEVEL_TOP, HARD_TOP[0])
DMGCAP_HELP = "Damage never goes above this multiple (x%s never clips Hard at Lv %d, which is x%.2f)." % (num(CAPS[1]), LEVEL_TOP, HARD_TOP[1])
assert DIFF_HELP == "Health / damage per level: Easy 4% / 2%, Normal 6% / 3%, Hard 8% / 4%. Custom = the two rows below."
# 0.1.4 help texts (spec 6.1): the Difficulty row picks the curve tables; the % and cap rows count only in Per level shape
DIFF_HELP14 = ("Picks the curve tables (Per level: Easy %s/%s, Normal %s/%s, Hard %s/%s %%). Custom = your own."
               % (num(PRESETS["easy"][0]), num(PRESETS["easy"][1]), num(PRESETS["normal"][0]), num(PRESETS["normal"][1]),
                  num(PRESETS["hard"][0]), num(PRESETS["hard"][1])))
assert DIFF_HELP14 == "Picks the curve tables (Per level: Easy 4/2, Normal 6/3, Hard 8/4 %). Custom = your own."
HP_HELP14 = "Per level shape, Custom only: max health +this % per level above 1. Applies at once (health % kept)."
DMG_HELP14 = "Per level shape, Custom only: damage +this % per level above 1, before armour. Applies at once."
HPCAP_HELP14 = "Per level shape only: health per level never goes above this multiple (x%s: Hard at Lv %d unclipped)." % (num(CAPS[0]), LEVEL_TOP)
DMGCAP_HELP14 = "Per level shape only: damage never goes above this multiple (x%s: Hard at Lv %d unclipped)." % (num(CAPS[1]), LEVEL_TOP)
CURVE_HELP = {"hp": "Mob health x this at each level (entry = level 0-100; straight lines between, flat after the last).",
              "dmg": "Mob damage x this at each level (entry = level 0-100; straight lines between, flat after the last)."}
CURVE_LABEL = {"hp": "Health curve: %s", "dmg": "Damage curve: %s"}
CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.levels", "Mob levels", "levels", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = new mobs get no level. Mobs that already have one keep it.", "field:MobCfg.ON;after=MobCfg.derive"),
    ("levels.neutral", "Neutral fighters get levels", "levels", "bool", "true", "", "", "", "", "new",
     "Neutral mobs that fight back when hit (boars, Scaraks, Feran warriors). Animals never.",
     "field:MobCfg.NEUTRAL;after=MobCfg.derive"),
    ("levels.roles", "Extra mobs that get levels", "levels", "text", ROLES_DEF, "", "2000", "", "", "new",
     "Other mods' role ids or Prefix* patterns. Vanilla hostile mobs + neutral fighters are built in.",
     "field:MobCfg.ROLES;after=MobCfg.derive"),
    ("levels.exclude", "Never level these", "levels", "text", EXCLUDE_DEF, "", "2000", "", "", "new",
     "Never levelled: tests, tamed, traders, bosses, mounts, pets. * = strip every level as mobs load.",
     "field:MobCfg.EXCLUDE;after=MobCfg.derive"),
    ("levels.max", "Highest mob level", "levels", "int", "100", "1", "1000", "", "", "new,adv",
     "Band + bonus never goes above this.", "field:MobCfg.MAX_LEVEL"),
    # 0.1.4 (spec 1.6): Fixed level by role - empty by default (the boss round fills it). The kit refuses * in an entry of a plain key
    # table, so Server Setup takes exact role ids; a Prefix* line typed into the file by hand still works (MobCfg.roleIdx)
    ("scale.role", "Fixed level by role", "levels", "table", "", "0", "1000", "int|dec;none;Level|Health x", "", "live,danger",
     "Bosses / special mobs: always this level (beats Never level these), Health x on top. 0 = off.",
     "reload@%s:scale.role.;check=MobHooks.checkScaleRole" % CFG_FILE),
    # 0.1.4: Strength shape (spec 1.2 / 6.1): Level curve = the curve tables, Per level = 0.1.3's % and cap maths byte for byte
    ("strength.shape", "Strength shape", "strength", "choice", SHAPE_DEF, "", "", SHAPE_OPTS, "", "live,danger",
     "Level curve = the Level curve tab. Per level = the old % and cap rows (SkyyMobs 0.1.3).", "field:MobCfg.SHAPE;after=MobCfg.derive"),
    ("strength.difficulty", "Difficulty", "strength", "choice", DIFF_DEF, "", "", DIFF_OPTS, "", "live",
     DIFF_HELP14, "field:MobCfg.DIFFICULTY;after=MobCfg.derive"),
    ("strength.hp", "Custom: health per level", "strength", "dec", num(CUSTOM[0]), "0", "100", "", "%", "live",
     HP_HELP14, "field:MobCfg.HP_PCT;after=MobCfg.derive"),
    ("strength.dmg", "Custom: damage per level", "strength", "dec", num(CUSTOM[1]), "0", "100", "", "%", "live",
     DMG_HELP14, "field:MobCfg.DMG_PCT;after=MobCfg.derive"),
    ("strength.hpCap", "Health multiplier cap", "strength", "dec", num(CAPS[0]), "1", "100", "", "x", "live",
     HPCAP_HELP14, "field:MobCfg.HP_CAP;after=MobCfg.derive"),
    ("strength.dmgCap", "Damage multiplier cap", "strength", "dec", num(CAPS[1]), "1", "100", "", "x", "live",
     DMGCAP_HELP14, "field:MobCfg.DMG_CAP"),
    # 0.1.2: the level health floor (live: derive sees the new health signature and re-applies every loaded levelled mob)
    ("strength.floor", "Health floor (base HP)", "strength", "int", str(FLOOR_DEF), "0", str(FLOOR_MAX), "", "", "live",
     FLOOR_HELP, "field:MobCfg.HP_FLOOR;after=MobCfg.derive"),
    ("strength.healOnLoad", "Heal mobs on chunk reload", "strength", "bool", "false", "", "", "", "", "live,adv",
     "Off = a wounded mob keeps its health share when it reloads with a new multiplier.", "field:MobCfg.HEAL_ON_LOAD"),
    # 0.1.4 (spec 1.6, both default off - Skyy 2026-10-05: no damage floor): players only, in LevelDamage
    ("strength.dmgFloor", "Damage floor", "strength", "int", "0", "0", "100", "", "%", "live,danger",
     "Mobs above Lv 20 hit players for at least this % of their Lv 1 health (full from Lv 30). 0 = off.", "field:MobCfg.DMG_FLOOR"),
    ("strength.hitCap", "One hit at most", "strength", "int", "0", "0", "100", "", "%", "live,danger",
     "A levelled mob's hit on a player (before armor) never exceeds this % of their max Health. 0 = off.", "field:MobCfg.HIT_CAP"),
] + [
    # 0.1.4: the 8 curve tables (key families in config.properties; every edit runs MobCfg.reloadAll -> derive -> the live re-apply)
    ("curve.%s.%s" % (_k, _d), CURVE_LABEL[_k] % _d.capitalize(), "curve", "table", "", "0.1", "1000", "dec;none;Factor", "", "live,danger",
     CURVE_HELP[_k], "reload@%s:curve.%s.%s.;check=MobHooks.checkCurvePoint" % (CFG_FILE, _k, _d)) for _k, _d in CURVE_IDX
] + [
    # 0.1.4: the level gap (spec 3.1; players vs levelled mobs only)
    ("part.gap", "Level gap", "gap", "bool", "true", "", "", "", "", "live,part,danger",
     "Mobs above your class skill take less from you and hit you harder. Players vs mobs only.", "field:MobCfg.GAP_ON"),
    ("gap.free", "Levels with no gap effect", "gap", "int", str(GAP_DEF["free"]), "0", "100", "", "", "live,danger",
     "Mobs up to this many levels above your class skill fight normally (like the XP gap).", "field:MobCfg.GAP_FREE"),
    ("gap.dealtStep", "Your damage lost per level", "gap", "dec", num(GAP_DEF["dealtStep"]), "0", "100", "", "%", "live,danger",
     "Each level past the free band: your hits on that mob deal this % less.", "field:MobCfg.GAP_DSTEP"),
    ("gap.dealtMin", "Your damage at least", "gap", "dec", num(GAP_DEF["dealtMin"]), "1", "100", "", "%", "live,danger",
     "Your hits never drop below this % of normal, so no mob is immune.", "field:MobCfg.GAP_DMIN"),
    ("gap.takenStep", "Damage taken per level", "gap", "dec", num(GAP_DEF["takenStep"]), "0", "100", "", "%", "live,danger",
     "Each level past the free band: that mob's hits on you deal this % more.", "field:MobCfg.GAP_TSTEP"),
    ("gap.takenMax", "Damage taken at most", "gap", "dec", num(GAP_DEF["takenMax"]), "1", "100", "", "x", "live,danger",
     "The gap never makes a mob's hits bigger than this multiple.", "field:MobCfg.GAP_TMAX"),
    ("bands.biome", "Level by biome", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "Region.Biome (Zone1_Tier3.Forest_Azure), or a Region alone = its other biomes (Zone1_Tier3).",
     "reload@%s:biome.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.env", "Level by environment", "bands", "table", "", "0", "1000", "int|int|int;type;Min|Max|Bonus", "", "new",
     "Band where no biome is known (islands, World Gen 2); Bonus is added on top of a biome band.",
     "reload@%s:env.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.world", "Level by world", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "World name or its start (dungeon_ = dungeon_1, dungeon_2) - wins over all. 0-0 = no levels.",
     "reload@%s:world.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.zone", "Zone fallback", "bands", "table", "", "0", "1000", "int|int;type;Min|Max", "", "new",
     "Zone1-Zone4: used when only the zone is known (region or environment name).",
     "reload@%s:zone.;check=MobHooks.checkBand" % BANDS_FILE),
    ("bands.volcanicTop", "Lava caves use the zone top", "bands", "bool", "true", "", "", "", "", "new",
     "Vanilla's deep lava caves get the band of the zone's hardest biome.", "field:MobCfg.VOLCANIC"),
    ("bands.islands", "Private islands", "bands", "range", "0", "0", "1000", "", "", "new",
     "SkyyIslands island worlds: a range like 1-3, or 0 for no levels.", "field:MobCfg.ISLANDS;after=MobCfg.derive"),
    ("bands.default", "When nothing matches", "bands", "range", "0", "0", "1000", "", "", "new",
     "Level range when no row matches (oceans, unknown worlds). 0 = no level.", "field:MobCfg.DEFAULT_BAND;after=MobCfg.derive"),
    ("bands.passThrough", "Use the land underneath", "bands", "text", PASS_DEF, "", "2000", "", "", "new,adv",
     "Overlay biomes (rivers, lakes, dunes, valleys, villages) that take the biome below them.",
     "field:MobCfg.PASS;after=MobCfg.derive"),
    ("plate.mode", "Level nameplates", "plate", "choice", "all", "", "", "all|All levelled mobs,off|Off", "", "new",
     "Show [Lv 9] Name over every levelled mob, or no plates.", "field:MobCfg.PLATE_MODE"),
    ("plate.format", "Nameplate text", "plate", "text", FORMAT_DEF, "", "60", "", "", "new",
     "{level} = the level, {name} = the mob's name. Must hold {level}.",
     "field:MobCfg.FORMAT;after=MobCfg.derive;check=MobHooks.checkFormat"),
    ("plate.colorOn", "Colour by level (trial)", "plate", "bool", "false", "", "", "", "", "new",
     "UNVERIFIED client support: try /mobs platetest, pick the markup that shows colour, then switch on.",
     "field:MobCfg.COLOR_ON"),
    ("plate.markup", "Colour markup", "plate", "choice", "tag", "", "",
     "tag|1 color tag,section|2 section sign,brace|3 brace token", "", "new",
     "1 = <color=#..> tag, 2 = section sign codes, 3 = {#..} token. Use the one /mobs platetest colours.",
     "field:MobCfg.MARKUP"),
    ("plate.colors", "Level colours", "plate", "table", "", "", "7", "text;type;Colour", "", "new",
     "Entry = lowest level of the band, value #rrggbb. Default white / yellow / gold / red / purple.",
     "reload@%s:plate.colors.;check=MobHooks.checkColor" % CFG_FILE),
    ("plate.strip", "Name endings to drop", "plate", "text", STRIP_DEF, "", "200", "", "", "new,adv",
     "Used when a mob has no translated name: Skeleton_Fighter_Wander -> Skeleton Fighter.",
     "field:MobCfg.STRIP;after=MobCfg.derive"),
]
_bad = ["%s help %d" % (r[0], len(r[10])) for r in CFG_ROWS if len(r[10]) > 100] + \
       ["%s label %d" % (r[0], len(r[1])) for r in CFG_ROWS if len(r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
_dp, _db = CFG.parse_props(CFG_TEXT), CFG.parse_props(BANDS_TEXT)
for _r in CFG_ROWS:
    if _r[3] != "table":
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: " + _r[0]
assert sum(1 for k in _db if k.startswith("biome.")) == len(BIOME_ROWS) and sum(1 for k in _db if k.startswith("env.")) == len(ENV_ROWS)
# config KEYS, category ids, choice values = 0.1's / 0.1.1's + the one new 0.1.2 key (Skyy's files, Changes / Undo lines and export codes
# keep working; the harness compares the published headers of 0.1.1 and 0.1.2, this is the cheap build-time half)
KEYS_01 = ["part.levels", "levels.neutral", "levels.roles", "levels.exclude", "levels.max", "strength.difficulty", "strength.hp",
           "strength.dmg", "strength.hpCap", "strength.dmgCap", "strength.healOnLoad", "bands.biome", "bands.env", "bands.world", "bands.zone",
           "bands.volcanicTop", "bands.islands", "bands.default", "bands.passThrough", "plate.mode", "plate.format", "plate.colorOn",
           "plate.markup", "plate.colors", "plate.strip"]
KEYS_012 = KEYS_01[:KEYS_01.index("strength.dmgCap") + 1] + ["strength.floor"] + KEYS_01[KEYS_01.index("strength.dmgCap") + 1:]
# 0.1.4 = 0.1.3's keys (= 0.1.2's) + the spec 6.1 rows, in display order
KEYS_014 = (KEYS_012[:KEYS_012.index("levels.max") + 1] + ["scale.role", "strength.shape"]
            + KEYS_012[KEYS_012.index("strength.difficulty"):KEYS_012.index("strength.healOnLoad") + 1] + ["strength.dmgFloor", "strength.hitCap"]
            + ["curve.%s.%s" % kd for kd in CURVE_IDX] + ["part.gap", "gap.free", "gap.dealtStep", "gap.dealtMin", "gap.takenStep", "gap.takenMax"]
            + KEYS_012[KEYS_012.index("strength.healOnLoad") + 1:])
assert [r[0] for r in CFG_ROWS] == KEYS_014 and sorted(KEYS_014) == sorted(KEYS_012 + [r[0] for r in CFG_ROWS if r[0] not in KEYS_012]), KEYS_014
assert [c for c, _l in CFG_CATS] == ["levels", "strength", "curve", "gap", "bands", "plate"], "0.1.4 = 0.1.3's tabs + Level curve + Level gap"
CFG_TITLE = "Mobs"
CFG_NOTE = "Chat: /mobs (players); /mobs inspect, set <level>, platetest, reload (admins)."

# ================================================================= 0.1.1: every Server Setup text fits SkyyMenu 0.3.5's boxes (menu_fit)
# SkyyMenu draws this page from the kit header (build_skyymenu_0.3.5.py AdminPage; the harness re-measures what the REAL jar sends):
#   tabRow   126 x 48 button, text = MenuUtil.inl(MenuUtil.clip(label, 14)), FontSize 16 bold (BS16 / SEL16)
#   drawRow  name label 556 px, FontSize 20 bold: MenuUtil.clip(nm, 52), nm = ("> " on a search hit) + label + (" (unit)") + (" *" for a
#            typed row holding a draft) + ("    " + tag when nm + 4 + tag <= 50 characters, else the tag goes in front of the help as
#            tag + "  -  " + help); help label 1050 px, FontSize 15: MenuUtil.clip(help, 140); a choice row with <= 4 choices = one button
#            per choice, (380 - 6 x (n - 1)) / n px, FontSize 16 bold, text MenuUtil.inl(label) (the value when that is empty); a table
#            row = a 240 px "Open - N entries" button, FontSize 18 bold
#   drawMod  header label (full 1080 px, FontSize 24 bold): tab label + "   -   N settings" (+ "   -   page P of Q") (+ "   -   K advanced
#            hidden"), 7 rows a page; frame title (28 bold) "Server Setup - <title> (<mod> <version>)", subtitle (16) the file line,
#            status line (17 bold) the header note
# Button texts pass MenuUtil.inl (letters, digits, space, < > / - kept, & -> and, any other character -> a space, 40 characters, trimmed).
# The client cuts a text wider than its box with "..." (Skyy's 2026-10-02 screenshot matched the measure: "Easy 3  / 1 5" = 91.3 px in
# a 90 px button -> "Easy 3 / 1..."; the tab cut is SkyyMenu's own 14-character clip, whose "..." the inline filter turns into
# spaces: drawn "Who gets le"). Widths = the client's glyph advances
# (skyyui.text_width, Client/Data/Shared/UI/Fonts, read-only); every text must leave FIT_PAD px of its box free.
FIT_PAD = 8
MENU_TAB = (126, 14, 16)                 # width, characters kept, font size (bold)
MENU_CHOICE = (380, 6, 16)               # widget width, gap, font size (bold); <= 4 choices = buttons
MENU_NAME = (556, 52, 20, 50)            # width, characters kept, font size (bold), longest name that still takes the tag inline
MENU_HELP = (1050, 140, 15)              # width, characters kept, font size
MENU_TABLE = (240, 18)                   # "Open - N entries" button width, font size (bold)
MENU_INNER, MENU_ROWS = 1080, 7          # page inner width, rows a page


def menu_inl(s):
    """= MenuUtil.inl (SkyyMenu 0.3.5)"""
    sb = ""
    for c in s or "":
        if len(sb) >= 40:
            break
        if ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9") or c in " <>/-":
            sb += c
        elif c == "&":
            sb += "and"
        else:
            sb += " "
    return sb.strip()


def menu_clip(s, n):
    """= MenuUtil.clip / AdminPage clip"""
    if s is None:
        return ""
    if len(s) <= n:
        return s
    return s[:n] if n <= 3 else s[:n - 3] + "..."


def menu_tag(flags):
    """= AdminPage.tagOf"""
    f = "," + flags + ","
    has = lambda x: ("," + x + ",") in f
    sb = "READ ONLY" if has("ro") else "RESTART" if has("restart") else "NEW ONLY" if has("new") else "LIVE" if has("live") else ""
    for fl, word in (("danger", "CONFIRM"), ("part", "PART"), ("adv", "ADVANCED")):
        if has(fl):
            sb = sb + (" - " if sb else "") + word
    return sb


def menu_texts(rows, cats, title, version, note, files, entries):
    """[(what, wanted text, drawn text, box px, font px, bold)] = everything SkyyMenu 0.3.5 draws from this header, every row variant"""
    out = []
    for cid, lab in cats:
        out.append(("tab " + cid, lab, menu_inl(menu_clip(lab, MENU_TAB[1])) or "-", MENU_TAB[0], MENU_TAB[2], True))
    for r in rows:
        key, label, cat, typ, _d, _lo, _hi, opts, unit, flags, hlp = r[:11]
        tg = menu_tag(flags)
        typed = typ in ("int", "dec", "text", "range", "color")
        for hit in (False, True):
            for draft in ((False, True) if typed else (False,)):
                nm = ("> " if hit else "") + label + ((" (" + unit + ")") if unit else "") + (" *" if draft else "")
                hp = hlp
                if tg and len(nm) + 4 + len(tg) <= MENU_NAME[3]:
                    nm = nm + "    " + tg
                elif tg:
                    hp = tg + "  -  " + hp
                v = (" (search hit)" if hit else "") + (" (draft)" if draft else "")
                out.append(("name " + key + v, nm, menu_clip(nm, MENU_NAME[1]), MENU_NAME[0], MENU_NAME[2], True))
                out.append(("help " + key + v, hp, menu_clip(hp, MENU_HELP[1]), MENU_HELP[0], MENU_HELP[2], False))
        if typ == "choice":
            parts = opts.split(",")
            if len(parts) <= 4:
                bw = (MENU_CHOICE[0] - MENU_CHOICE[1] * (len(parts) - 1)) // len(parts)
                for p in parts:
                    val, _, lab = p.partition("|")
                    lab = (lab if "|" in p else val).strip()
                    t = menu_inl(lab if menu_inl(lab) else val.strip()) or "-"      # = drawRow's label-or-value, then btn()'s inl
                    out.append(("choice %s=%s" % (key, val.strip()), lab, t, bw, MENU_CHOICE[2], True))
        if typ == "table":
            for n in (entries.get(key, 0), 9999):
                t = "Open - %d %s" % (n, "entry" if n == 1 else "entries")
                out.append(("table %s (%d)" % (key, n), t, menu_inl(t), MENU_TABLE[0], MENU_TABLE[1], True))
    for cid, lab in cats:
        mine = [r for r in rows if r[2] == cid]
        adv = len([r for r in mine if ",adv," in "," + r[9] + ","])
        for shown in (False, True):
            n = len(mine) if shown else len(mine) - adv
            pages = max(1, (n + MENU_ROWS - 1) // MENU_ROWS)
            for pg in range(1, pages + 1):
                t = "%s   -   %d %s" % (lab, n, "setting" if n == 1 else "settings")
                t += ("   -   page %d of %d" % (pg, pages)) if pages > 1 else ""
                t += ("   -   %d advanced hidden" % adv) if adv and not shown else ""
                out.append(("header %s%s p%d" % (cid, " (advanced shown)" if shown else "", pg), t, t, MENU_INNER, 24, True))
    t = "Server Setup - %s (%s %s)" % (title, MOD, version)
    out.append(("title", t, t, MENU_INNER, 28, True))
    more = " and 1 more file" if len(files) == 2 else (" and %d more files" % (len(files) - 1) if len(files) > 2 else "")
    t = "Saved to " + files[0] + more + " - changes are written at once."
    out.append(("subtitle", t, t, MENU_INNER, 16, False))
    out.append(("status (note)", note, note, MENU_INNER, 17, True))
    return out


def menu_fit(rows, cats, title, version, note, files, entries):
    """(problems, measured) - a problem = a text SkyyMenu clips (drawn != wanted) or one that leaves less than FIT_PAD px of its box"""
    bad, meas = [], []
    for what, want, drawn, box, fs, bold in menu_texts(rows, cats, title, version, note, files, entries):
        w = SUI.text_width(drawn, fs, bold)
        meas.append((box - w, what, drawn, w, box))
        if drawn != want and not what.startswith("choice ") and not what.startswith("table "):
            bad.append("%s: SkyyMenu draws %r for %r (clipped)" % (what, drawn, want))
        elif what.startswith("choice ") and menu_inl(want) != want:
            bad.append("%s: %r loses characters in the button (%r)" % (what, want, drawn))
        if w > box - FIT_PAD:
            bad.append("%s: %r is %.1f px in a %d px box (FontSize %d%s) - the client cuts it" % (what, drawn, w, box, fs, " bold" if bold else ""))
    return bad, sorted(meas)


_entries = {"bands.biome": len(BIOME_ROWS), "bands.env": len(ENV_ROWS), "bands.world": 0, "bands.zone": len(ZONE_ROWS),
            "plate.colors": len(COLOR_ROWS), "scale.role": 0}
_entries.update(("curve.%s.%s" % kd, len(CURVES[kd])) for kd in CURVE_IDX)       # 0.1.4: "Open - 10 entries"
_fit_bad, _fit = menu_fit(CFG_ROWS, CFG_CATS, CFG_TITLE, VERSION, CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)
assert not _fit_bad, "Server Setup texts that SkyyMenu 0.3.5 would cut:\n  " + "\n  ".join(_fit_bad)
# the same measure flags exactly what Skyy saw on 0.1 (so it is the right measure): the tab and the four difficulty choices
_old_rows = [r[:7] + ("easy|Easy 3% / 1.5%,normal|Normal 4% / 2%,hard|Hard 6% / 3%,custom|Custom",) + r[8:] if r[0] == "strength.difficulty" else r
             for r in CFG_ROWS]
_old_bad, _old = menu_fit(_old_rows, [("levels", "Who gets levels")] + CFG_CATS[1:], CFG_TITLE, "0.1", CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)
assert sorted(set(b.split(":")[0] for b in _old_bad)) == ["choice strength.difficulty=easy", "choice strength.difficulty=hard",
                                                         "choice strength.difficulty=normal", "tab levels"], _old_bad
# 0.1.4 negative control (feasibility critic F5): the draft's choice label "Per-level %" loses characters in SkyyMenu's button (menu_inl
# turns % into a space), "Per level" passes
_neg_rows = [r[:7] + ("curve|Level curve,linear|Per-level %",) + r[8:] if r[0] == "strength.shape" else r for r in CFG_ROWS]
_neg_bad = menu_fit(_neg_rows, CFG_CATS, CFG_TITLE, VERSION, CFG_NOTE, [CFG_FILE, BANDS_FILE], _entries)[0]
assert sorted(set(b.split(":")[0] for b in _neg_bad)) == ["choice strength.shape=linear"], _neg_bad
print("Server Setup fit (SkyyMenu 0.3.5 boxes, %d px to spare): %d texts - %d tabs, %d row names + %d help lines (every variant), %d choice "
      "buttons, %d table buttons, %d page lines; tightest: %s %r %.1f / %d px; the 0.1 labels fail it: %s"
      % (FIT_PAD, len(_fit), len(CFG_CATS), sum(1 for m in _fit if m[1].startswith("name ")), sum(1 for m in _fit if m[1].startswith("help ")),
         sum(1 for m in _fit if m[1].startswith("choice ")), sum(1 for m in _fit if m[1].startswith("table ")),
         sum(1 for m in _fit if m[1].split(" ")[0] in ("header", "title", "subtitle", "status")), _fit[0][1], _fit[0][2], _fit[0][3], _fit[0][4],
         ", ".join(sorted(set(b.split(":")[0] for b in _old_bad)))))
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Mobs", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE, BANDS_FILE], NOTE=CFG_NOTE,
               RELOAD="MobCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": CFG_TEXT, "bands.properties": BANDS_TEXT})

# ---------------------------------------------------------------- MobCfg methods
M(cfg, r"""
public static int[] range(String s) {
  int[] r = new int[] { 0, 0 };
  if (s == null) return r;
  String t = s.trim().replace(" ", "");
  if (t.length() == 0) return r;
  try {
    int i = t.indexOf('-', 1);
    int a = Integer.parseInt(i < 0 ? t : t.substring(0, i));
    int b = i < 0 ? a : Integer.parseInt(t.substring(i + 1));
    if (a < 0 || b < 0) return r;
    if (a > b) { int x = a; a = b; b = x; }
    if (b > 1000) b = 1000;
    if (a > 1000) a = 1000;
    r[0] = a; r[1] = b;
  } catch (Throwable e) { }
  return r;
}""")
M(cfg, r"""
public static double dec(String s, double def, double lo, double hi) {
  if (s == null) return def;
  try {
    double d = Double.parseDouble(s.trim());
    if (Double.isNaN(d) || Double.isInfinite(d)) return def;
    if (d < lo) d = lo;
    if (d > hi) d = hi;
    return d;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static int intOf(String s, int def, int lo, int hi) {
  if (s == null) return def;
  try {
    long v = Long.parseLong(s.trim());
    if (v < lo) v = lo;
    if (v > hi) v = hi;
    return (int) v;
  } catch (Throwable t) { return def; }
}""")
M(cfg, r"""
public static boolean bool(String s, boolean def) {
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return def;
}""")
M(cfg, r"""
public static String choice(String s, String def, String[] allowed) {
  if (s == null) return def;
  String t = s.trim().toLowerCase();
  for (int i = 0; i < allowed.length; i++) if (allowed[i].equals(t)) return t;
  return def;
}""")
M(cfg, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfg, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  if (f == null) return null;
  java.io.InputStream in = null;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    java.util.Properties p = new java.util.Properties();
    p.load(in);
    return p;
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not read " + f + ": " + t + " - using the built-in defaults for it");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfg, r"""
public static void seed(java.nio.file.Path f, String text) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.MobLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.MobLog.warn("could not write the default " + f + ": " + t); }
}""")
# a table from a properties map: every <prefix><key>=<n>[,<n>[,<n>]] line, keys sorted (deterministic ties), bad lines skipped + warned
M(cfg, r"""
public static @PKG@.MobBands table(java.util.Properties p, String prefix, int cols, String name) {
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith(prefix) && k.length() > prefix.length()) keys.add(k);
  }
  String[] ks = new String[keys.size()];
  for (int i = 0; i < ks.length; i++) ks[i] = (String) keys.get(i);
  java.util.Arrays.sort(ks);
  java.util.ArrayList raw = new java.util.ArrayList();
  int[] a = new int[ks.length], b = new int[ks.length], c = new int[ks.length];
  int n = 0;
  for (int i = 0; i < ks.length; i++) {
    String v = p.getProperty(ks[i], "").trim();
    String[] parts = v.split("[,|]");
    try {
      int x = Integer.parseInt(parts[0].trim());
      int y = parts.length > 1 ? Integer.parseInt(parts[1].trim()) : x;
      int z = (cols > 2 && parts.length > 2) ? Integer.parseInt(parts[2].trim()) : 0;
      if (x < 0 || y < 0 || z < 0 || x > 1000 || y > 1000 || z > 1000) throw new IllegalArgumentException("out of 0-1000");
      if (x > y) { int s = x; x = y; y = s; }
      raw.add(ks[i].substring(prefix.length()));
      a[n] = x; b[n] = y; c[n] = z; n++;
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("line:" + ks[i] + "=" + v, name + ": skipped the line " + ks[i] + "=" + v + " (needs whole numbers 0-1000)");
    }
  }
  String[] rk = new String[n];
  int[] ra = new int[n], rb = new int[n], rc = new int[n];
  for (int i = 0; i < n; i++) { rk[i] = (String) raw.get(i); ra[i] = a[i]; rb[i] = b[i]; rc[i] = c[i]; }
  return new @PKG@.MobBands(name, rk, ra, rb, rc);
}""")
M(cfg, r"""
public static void colors(java.util.Properties p) {
  java.util.TreeMap m = new java.util.TreeMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("plate.colors.")) continue;
    String v = p.getProperty(k, "").trim().toLowerCase();
    try {
      int lvl = Integer.parseInt(k.substring(13).trim());
      if (lvl < 1 || lvl > 1000 || !v.matches("#[0-9a-f]{6}")) throw new IllegalArgumentException("bad");
      m.put(Integer.valueOf(lvl), v);
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("col:" + k + "=" + v, "plate.colors: skipped the line " + k + "=" + v + " (needs <level 1-1000>=#rrggbb)");
    }
  }
  int[] lv = new int[m.size()];
  String[] hx = new String[m.size()];
  int i = 0;
  java.util.Iterator e = m.entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    lv[i] = ((Integer) en.getKey()).intValue();
    hx[i] = (String) en.getValue();
    i++;
  }
  COL_LV = lv;
  COL_HEX = hx;
}""")
# the band of the hardest biome row of each zone (Skyy R5 lava caves): highest max, then highest min; Region.* fallback rows left out
M(cfg, r"""
public static void zoneTops() {
  int[] za = new int[10], zb = new int[10];
  String[] zk = new String[10];
  @PKG@.MobBands t = BIOME;
  for (int i = 0; t != null && i < t.n; i++) {
    String k = t.raw[i];
    if (k.length() < 6 || !k.startsWith("Zone") || k.indexOf('.') < 0 || k.endsWith(".*")) continue;
    char d = k.charAt(4);
    if (d < '0' || d > '9' || k.charAt(5) != '_') continue;
    int z = d - '0';
    if (t.b[i] > zb[z] || (t.b[i] == zb[z] && t.a[i] > za[z])) { za[z] = t.a[i]; zb[z] = t.b[i]; zk[z] = k; }
  }
  ZTOP_A = za; ZTOP_B = zb; ZTOP_KEY = zk;
}""")
# ---- 0.1.4: the level curve tables (spec 1.2 / 1.3 / 6.1) and Fixed level by role (spec 1.6)
# eval = SkyyGear's GearBase.eval (Gear 0.2.4 GearBase.eval, the spec's "straight lines between points, flat outside them" rule)
M(cfg, r"""
public static double eval(Object[] p, double x) {
  if (p == null) return 1.0;
  double[] ls = (double[]) p[0];
  double[] vs = (double[]) p[1];
  int n = ls.length;
  if (n == 0) return 1.0;
  if (x <= ls[0]) return vs[0];
  if (x >= ls[n - 1]) return vs[n - 1];
  for (int i = 1; i < n; i++) {
    if (x <= ls[i]) return vs[i - 1] + (vs[i] - vs[i - 1]) * (x - ls[i - 1]) / (ls[i] - ls[i - 1]);
  }
  return vs[n - 1];
}""")
# a "level:factor,level:factor" text (the jar's own default points) -> Object[]{ double[] levels, double[] factors }
M(cfg, r"""
public static Object[] parsePts(String t) {
  String[] parts = t.split(",");
  double[] ls = new double[parts.length], vs = new double[parts.length];
  for (int i = 0; i < parts.length; i++) {
    int c = parts[i].indexOf(':');
    ls[i] = (double) Integer.parseInt(parts[i].substring(0, c).trim());
    vs[i] = Double.parseDouble(parts[i].substring(c + 1).trim());
  }
  return new Object[] { ls, vs };
}""")
M(cfg, "public static Object[] defPts(int i) { return parsePts(CURVE_DEF[i]); }")
# one curve table from the file: every <prefix><level 0-100>=<factor 0.1-1000> line (bad lines skipped + warned once); null = none valid
M(cfg, r"""
public static Object[] pts(java.util.Properties p, String prefix, String name) {
  java.util.TreeMap m = new java.util.TreeMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith(prefix) || k.length() == prefix.length()) continue;
    String v = p.getProperty(k, "").trim();
    try {
      int lv = Integer.parseInt(k.substring(prefix.length()).trim());
      double f = Double.parseDouble(v);
      if (lv < 0 || lv > 100 || Double.isNaN(f) || f < 0.1 || f > 1000.0) throw new IllegalArgumentException("out of range");
      m.put(Integer.valueOf(lv), Double.valueOf(f));
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("curve:" + k + "=" + v, name + ": skipped the line " + k + "=" + v + " (needs <level 0-100>=<factor 0.1-1000>)");
    }
  }
  if (m.isEmpty()) return null;
  double[] ls = new double[m.size()], vs = new double[m.size()];
  int i = 0;
  java.util.Iterator e = m.entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    ls[i] = (double) ((Integer) en.getKey()).intValue();
    vs[i] = ((Double) en.getValue()).doubleValue();
    i++;
  }
  return new Object[] { ls, vs };
}""")
# the 8 tables from config.properties; a table with no valid line uses its default points (one WARN) - never an empty curve
M(cfg, r"""
public static void curves(java.util.Properties c) {
  Object[] all = new Object[CURVE_KEY.length];
  for (int i = 0; i < all.length; i++) {
    Object[] q = pts(c, CURVE_KEY[i] + ".", CURVE_KEY[i]);
    if (q == null) {
      q = defPts(i);
      @PKG@.MobLog.warnOnce("curve-empty:" + CURVE_KEY[i], CURVE_KEY[i] + " has no valid entry in config.properties - using its default points (Server Setup -> Mobs -> Level curve)");
    }
    all[i] = q;
  }
  CURVES = all;
}""")
M(cfg, r"""
public static String ptsText(Object[] p) {
  if (p == null) return "";
  double[] ls = (double[]) p[0];
  double[] vs = (double[]) p[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ls.length; i++) { if (i > 0) sb.append(','); sb.append((int) ls[i]).append(':').append(vs[i]); }
  return sb.toString();
}""")
M(cfg, r"""
public static Object[] curveOf(int i) {
  Object[] all = CURVES;
  if (all == null || i < 0 || i >= all.length || all[i] == null) return defPts(i < 0 ? 0 : i);
  return (Object[]) all[i];
}""")
# the difficulty's table column: easy 0, normal 1, hard 2, custom 3 (an unknown word = the default normal, as derive's ladder)
M(cfg, r"""
public static int diffIdx() {
  String d = DIFFICULTY == null ? "@DIFDEF@" : DIFFICULTY.trim().toLowerCase();
  if (d.equals("easy")) return 0;
  if (d.equals("hard")) return 2;
  if (d.equals("custom")) return 3;
  return 1;
}""")
# the shape a file WITHOUT a strength.shape line gets (= MobMig14's decision table): custom -> linear (the owner's own %), else curve
M(cfg, r"""
public static String shapeFor(String difficulty) {
  String d = difficulty == null ? "" : difficulty.trim().toLowerCase();
  return d.equals("custom") ? "linear" : "@SHPDEF@";
}""")
# scale.role: every scale.role.<role id or Prefix*>=<level 0-100>,<health x 0.1-100> line (health x optional, default 1); level 0 = off
M(cfg, r"""
public static void roles(java.util.Properties p) {
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("scale.role.") && k.length() > 11) keys.add(k);
  }
  String[] ks = new String[keys.size()];
  for (int i = 0; i < ks.length; i++) ks[i] = (String) keys.get(i);
  java.util.Arrays.sort(ks);
  java.util.ArrayList raw = new java.util.ArrayList();
  int[] lv = new int[ks.length];
  double[] hx = new double[ks.length];
  int n = 0;
  StringBuilder sig = new StringBuilder();
  for (int i = 0; i < ks.length; i++) {
    String e = ks[i].substring(11).trim();
    String v = p.getProperty(ks[i], "").trim();
    try {
      String[] parts = v.split("[,|]");
      int l = Integer.parseInt(parts[0].trim());
      double x = (parts.length > 1 && parts[1].trim().length() > 0) ? Double.parseDouble(parts[1].trim()) : 1.0;
      if (e.length() == 0 || l < 0 || l > 100 || Double.isNaN(x) || x < 0.1 || x > 100.0) throw new IllegalArgumentException("out of range");
      if (l == 0) continue;
      raw.add(e); lv[n] = l; hx[n] = x; n++;
      sig.append(e.toLowerCase()).append('=').append(l).append(',').append(x).append(';');
    } catch (Throwable t) {
      @PKG@.MobLog.warnOnce("role:" + ks[i] + "=" + v, "scale.role: skipped the line " + ks[i] + "=" + v + " (needs <level 0-100>,<health x 0.1-100>)");
    }
  }
  String[] r = new String[n], lo = new String[n];
  int[] rl = new int[n];
  double[] rx = new double[n];
  for (int i = 0; i < n; i++) { r[i] = (String) raw.get(i); lo[i] = r[i].toLowerCase(); rl[i] = lv[i]; rx[i] = hx[i]; }
  ROLES_TAB = new Object[] { r, lo, rl, rx };
  ROLE_SIG = sig.toString();
}""")
# the row of a role: an exact id (any case) first, else the most specific Prefix* pattern (a hand-typed file line); -1 = none
M(cfg, r"""
public static int roleIdx(String role) {
  Object[] t = ROLES_TAB;
  if (t == null || role == null) return -1;
  String[] lo = (String[]) t[1];
  String k = role.toLowerCase();
  for (int i = 0; i < lo.length; i++) if (lo[i].indexOf('*') < 0 && lo[i].equals(k)) return i;
  int best = -1, bs = -1;
  for (int i = 0; i < lo.length; i++) {
    if (lo[i].indexOf('*') < 0) continue;
    int sp = @PKG@.MobGlob.spec(lo[i]);
    if (sp > bs && @PKG@.MobGlob.glob(lo[i], k)) { best = i; bs = sp; }
  }
  return best;
}""")
M(cfg, r"""
public static int roleLevel(String role) {
  int i = roleIdx(role);
  if (i < 0) return 0;
  int l = ((int[]) ROLES_TAB[2])[i];
  return l > MAX_LEVEL ? MAX_LEVEL : l;
}""")
M(cfg, r"""
public static double roleX(String role) {
  int i = roleIdx(role);
  return i < 0 ? 1.0 : ((double[]) ROLES_TAB[3])[i];
}""")
M(cfg, r"""
public static String roleKey(String role) {
  int i = roleIdx(role);
  if (i < 0) return null;
  return "scale.role." + ((String[]) ROLES_TAB[0])[i];
}""")
M(cfg, r"""
public static void derive(String key) {
  P_ROLES = @PKG@.MobGlob.list(ROLES);
  P_EXCL = @PKG@.MobGlob.list(EXCLUDE);
  P_PASS = @PKG@.MobGlob.list(PASS);
  P_STRIP = @PKG@.MobGlob.list(STRIP);
  String d = DIFFICULTY == null ? "@DIFDEF@" : DIFFICULTY.trim().toLowerCase();
  double hp = @DEFH@, dm = @DEFD@;
  if (d.equals("easy")) { hp = @EASYH@; dm = @EASYD@; }
  else if (d.equals("hard")) { hp = @HARDH@; dm = @HARDD@; }
  else if (d.equals("custom")) { hp = HP_PCT; dm = DMG_PCT; }
  HP_STEP = hp / 100.0;
  DMG_STEP = dm / 100.0;
  int[] i = range(ISLANDS);
  ISL_A = i[0]; ISL_B = i[1];
  int[] f = range(DEFAULT_BAND);
  DEF_A = f[0]; DEF_B = f[1];
  String fm = FORMAT;
  if (fm != null) {
    if (FORMATS.size() >= 16 && !FORMATS.containsKey(fm)) FORMATS.clear();
    FORMATS.put(fm, Boolean.TRUE);
  }
  EPOCH = EPOCH + 1L;
  try { @PKG@.MobLevel.NAMES.clear(); } catch (Throwable t) { }
  String sh = SHAPE == null ? "@SHPDEF@" : SHAPE.trim().toLowerCase();
  CURVE_ON = !sh.equals("linear");
  String sig = CURVE_ON ? "curve|" + diffIdx() + "|" + ptsText(curveOf(diffIdx())) + "|" + HP_FLOOR + "|" + ROLE_SIG
                        : "linear|" + HP_STEP + "|" + HP_CAP + "|" + HP_FLOOR + "|" + ROLE_SIG;
  if (!sig.equals(HP_SIG)) {
    HP_SIG = sig;
    Runnable r = ON_HEALTH;
    if (r != null) {
      try { r.run(); }
      catch (Throwable t2) { @PKG@.MobLog.warnOnce("hpsig:" + t2.getClass().getName(), "could not hand the new health settings to the loaded mobs (" + t2 + ") - they get them when their chunks reload"); }
    }
  }
}""")
M(cfg, r"""
public static synchronized void apply(java.util.Properties c, java.util.Properties b) {
  ON = bool(c.getProperty("part.levels"), true);
  NEUTRAL = bool(c.getProperty("levels.neutral"), true);
  ROLES = c.getProperty("levels.roles", "").trim();
  EXCLUDE = c.getProperty("levels.exclude", @PKG@.MobCfg.EXCL_DEFAULT()).trim();
  MAX_LEVEL = intOf(c.getProperty("levels.max"), 100, 1, 1000);
  DIFFICULTY = choice(c.getProperty("strength.difficulty"), "@DIFDEF@", new String[] { "easy", "normal", "hard", "custom" });
  HP_PCT = dec(c.getProperty("strength.hp"), @CUSTH@, 0.0, 100.0);
  DMG_PCT = dec(c.getProperty("strength.dmg"), @CUSTD@, 0.0, 100.0);
  HP_CAP = dec(c.getProperty("strength.hpCap"), @HPCAP@, 1.0, 100.0);
  DMG_CAP = dec(c.getProperty("strength.dmgCap"), @DMGCAP@, 1.0, 100.0);
  HP_FLOOR = intOf(c.getProperty("strength.floor"), @FLDEF@, 0, @FLMAX@);
  HEAL_ON_LOAD = bool(c.getProperty("strength.healOnLoad"), false);
  SHAPE = choice(c.getProperty("strength.shape"), shapeFor(c.getProperty("strength.difficulty")), new String[] { "curve", "linear" });
  DMG_FLOOR = intOf(c.getProperty("strength.dmgFloor"), 0, 0, 100);
  HIT_CAP = intOf(c.getProperty("strength.hitCap"), 0, 0, 100);
  GAP_ON = bool(c.getProperty("part.gap"), true);
  GAP_FREE = intOf(c.getProperty("gap.free"), @GFREE@, 0, 100);
  GAP_DSTEP = dec(c.getProperty("gap.dealtStep"), @GDSTEP@, 0.0, 100.0);
  GAP_DMIN = dec(c.getProperty("gap.dealtMin"), @GDMIN@, 1.0, 100.0);
  GAP_TSTEP = dec(c.getProperty("gap.takenStep"), @GTSTEP@, 0.0, 100.0);
  GAP_TMAX = dec(c.getProperty("gap.takenMax"), @GTMAX@, 1.0, 100.0);
  curves(c);
  roles(c);
  PASS = c.getProperty("bands.passThrough", @PKG@.MobCfg.PASS_DEFAULT()).trim();
  VOLCANIC = bool(c.getProperty("bands.volcanicTop"), true);
  int[] r1 = range(c.getProperty("bands.islands", "0"));
  ISLANDS = r1[0] == r1[1] ? String.valueOf(r1[0]) : r1[0] + "-" + r1[1];
  int[] r2 = range(c.getProperty("bands.default", "0"));
  DEFAULT_BAND = r2[0] == r2[1] ? String.valueOf(r2[0]) : r2[0] + "-" + r2[1];
  PLATE_MODE = choice(c.getProperty("plate.mode"), "all", new String[] { "all", "off" });
  String fm = c.getProperty("plate.format", "").trim();
  if (fm.indexOf("{level}") < 0 || fm.length() > 60) fm = "[Lv {level}] {name}";
  FORMAT = fm;
  STRIP = c.getProperty("plate.strip", @PKG@.MobCfg.STRIP_DEFAULT()).trim();
  COLOR_ON = bool(c.getProperty("plate.colorOn"), false);
  MARKUP = choice(c.getProperty("plate.markup"), "tag", new String[] { "tag", "section", "brace" });
  colors(c);
  BIOME = table(b, "biome.", 2, "bands.biome");
  ENV = table(b, "env.", 3, "bands.env");
  WORLD = table(b, "world.", 2, "bands.world");
  ZONE = table(b, "zone.", 2, "bands.zone");
  zoneTops();
  derive(null);
  LOADED = BIOME.n + " biome rows, " + ENV.n + " environment rows, " + WORLD.n + " world rows, " + ZONE.n + " zone rows";
}""".replace("@PKG@.MobCfg.EXCL_DEFAULT()", jstr(EXCLUDE_DEF))
   .replace("@PKG@.MobCfg.PASS_DEFAULT()", jstr(PASS_DEF)).replace("@PKG@.MobCfg.STRIP_DEFAULT()", jstr(STRIP_DEF)))
M(cfg, r"""
public static void reloadAll() {
  java.util.Properties c = read(FILE);
  if (c == null) c = props(DEF_CFG);
  java.util.Properties b = read(BANDS);
  if (b == null) b = props(DEF_BANDS);
  apply(c, b);
}""")
M(cfg, r"""
public static void load() {
  seed(FILE, DEF_CFG);
  seed(BANDS, DEF_BANDS);
  reloadAll();
}""")
M(cfg, "public static void useDefaults() { apply(props(DEF_CFG), props(DEF_BANDS)); }")
# the built-in list (review F1): the exact vanilla role ids, lower case, built once (a whole new set is published, never edited)
M(cfg, r"""
public static java.util.HashSet van() {
  java.util.HashSet s = VAN;
  if (s != null) return s;
  s = new java.util.HashSet();
  String[] p = VANILLA.split(",");
  for (int i = 0; i < p.length; i++) {
    String t = p[i].trim().toLowerCase();
    if (t.length() > 0) s.add(t);
  }
  VAN = s;
  return s;
}""")
M(cfg, "public static boolean builtIn(String role) { return role != null && van().contains(role.toLowerCase()); }")
# who gets a level (null = yes, else the reason): attitude, the exclude list, the built-in list or the extra list, the neutral switch
M(cfg, r"""
public static String whyNot(String att, String role) {
  if (role == null || role.length() == 0) return "not an NPC with a role";
  String a = att == null ? "" : att.trim().toUpperCase();
  boolean hostile = a.equals("HOSTILE"), neutral = a.equals("NEUTRAL");
  if (!hostile && !neutral) return "attitude " + (a.length() == 0 ? "unknown" : a) + " (only hostile mobs and neutral fighters)";
  if (@PKG@.MobGlob.any(P_EXCL, role)) return "in Never level these";
  if (!builtIn(role) && !@PKG@.MobGlob.any(P_ROLES, role)) return "not a built-in vanilla fighter and not in Extra mobs that get levels";
  if (neutral && !NEUTRAL) return "neutral fighters are switched off";
  return null;
}""")
# 0.1.4: a scale.role row (level > 0) always levels its mob - it wins over Never level these, the lists and the attitude (spec 1.6)
M(cfg, "public static String whyNotRole(String att, String role) { if (roleLevel(role) > 0) return null; return whyNot(att, role); }")
M(cfg, "public static boolean passes(String biome) { return biome != null && @PKG@.MobGlob.any(P_PASS, biome); }")
# 0.1.4: the Level curve multiplier of table i at a level (never below x0.1); hpMult / dmgMult call it first, so their Per level part
# stays 0.1.3's code instruction for instruction (the harness compares it)
M(cfg, r"""
public static float curveMult(int i, int level) {
  double c = eval(curveOf(i), (double) level);
  if (!(c >= 0.1)) c = 0.1;
  return (float) c;
}""")
M(cfg, r"""
public static float hpMult(int level) {
  if (CURVE_ON) return curveMult(diffIdx(), level);
  if (level <= 1) return 1.0f;
  double m = 1.0 + HP_STEP * (double) (level - 1);
  if (m > HP_CAP) m = HP_CAP;
  if (m < 1.0) m = 1.0;
  return (float) m;
}""")
M(cfg, r"""
public static float dmgMult(int level) {
  if (CURVE_ON) return curveMult(4 + diffIdx(), level);
  if (level <= 1) return 1.0f;
  double m = 1.0 + DMG_STEP * (double) (level - 1);
  if (m > DMG_CAP) m = DMG_CAP;
  if (m < 1.0) m = 1.0;
  return (float) m;
}""")
# 0.1.2: the floor factor max(1, floor / base) (1 when the floor is off or the base unknown) and the health amount = the 0.1.1 level
# multiplier (capped) x that factor - EXACTLY hpMult(level) when the factor is 1 (floor 0, or a mob at or above the floor)
M(cfg, r"""
public static double floorFactor(double base) {
  int f = HP_FLOOR;
  if (f <= 0 || !(base > 0.0)) return 1.0;
  double x = (double) f / base;
  return x > 1.0 ? x : 1.0;
}""")
M(cfg, r"""
public static float hpAmount(int level, double base) {
  float m = hpMult(level);
  double f = floorFactor(base);
  if (f <= 1.0) return m;
  return (float) ((double) m * f);
}""")
# 0.1.4: + the scale.role Health x on top (rx 1 = exactly hpAmount(level, base))
M(cfg, r"""
public static float hpAmount(int level, double base, double rx) {
  float m = hpAmount(level, base);
  if (rx == 1.0 || !(rx > 0.0)) return m;
  return (float) ((double) m * rx);
}""")
# 0.1.4: the health multiplier Hard would give a mob of this level in the same shape (mob:fn:info's xpMult = min(1, hpMult / this)):
# curve = the Hard health table, linear = min(hpCap, 1 + 8 % (L - 1)); float-rounded like hpMult, so Hard / Hard is exactly 1
M(cfg, r"""
public static double hardRef(int level) {
  if (CURVE_ON) {
    double c = eval(curveOf(2), (double) level);
    if (!(c >= 0.1)) c = 0.1;
    return (double) (float) c;
  }
  if (level <= 1) return 1.0;
  double m = 1.0 + @HARDS@ * (double) (level - 1);
  if (m > HP_CAP) m = HP_CAP;
  if (m < 1.0) m = 1.0;
  return (double) (float) m;
}""")
M(cfg, r"""
public static String pct(double d) {
  String s = String.valueOf(Math.round(d * 1000.0) / 10.0);
  if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
  return s;
}""")
M(cfg, r"""
public static String difficultyText() {
  String d = DIFFICULTY == null ? "normal" : DIFFICULTY;
  String n = d.equals("easy") ? "Easy" : d.equals("hard") ? "Hard" : d.equals("custom") ? "Custom" : "Normal";
  if (CURVE_ON) return n + " curve";
  return n + " " + pct(HP_STEP) + "% / " + pct(DMG_STEP) + "%";
}""")
M(cfg, "public static String num2(double d) { String s = String.valueOf(Math.round(d * 100.0) / 100.0); return s.endsWith(\".0\") ? s.substring(0, s.length() - 2) : s; }")
M(cfg, r"""
public static String strengthText() {
  String fl = HP_FLOOR > 0 ? HP_FLOOR + " HP" : "off";
  String gap = GAP_ON ? "level gap on (" + GAP_FREE + " levels free)" : "level gap off";
  if (CURVE_ON) return difficultyText() + " (Level curve shape, health floor " + fl + ", " + gap + ")";
  return difficultyText() + " (Per level shape, caps x" + num2(HP_CAP) + " / x" + num2(DMG_CAP) + ", health floor " + fl + ", " + gap + ")";
}""")

# ---------------------------------------------------------------- MobLevel: the level core (pure parts first, engine glue after)
M(lv, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# SplitMix64 finalizer (constants as signed decimals: 0xBF58476D1CE4E5B9, 0x94D049BB133111EB, 0x9E3779B97F4A7C15)
M(lv, r"""
public static long mix(long z) {
  z = (z ^ (z >>> 30)) * -4658895280553007687L;
  z = (z ^ (z >>> 27)) * -7723592293110705685L;
  return z ^ (z >>> 31);
}""")
M(lv, r"""
public static int roll(long worldSeed, java.util.UUID u, String role, int a, int b) {
  if (b <= a) return a;
  long h = mix(worldSeed + -7046029254386353131L);
  if (u != null) { h = mix(h ^ u.getMostSignificantBits()); h = mix(h ^ u.getLeastSignificantBits()); }
  h = mix(h ^ (long) (role == null ? 0 : role.hashCode()));
  long span = (long) (b - a + 1);
  return a + (int) Long.remainderUnsigned(h, span);
}""")
# res = Object[]{ Integer min, Integer max, Integer bonus, String step, String key } -> the final level (0 = none)
M(lv, r"""
public static int levelFor(Object[] res, long worldSeed, java.util.UUID u, String role) {
  if (res == null) return 0;
  int a = ((Integer) res[0]).intValue(), b = ((Integer) res[1]).intValue(), bonus = ((Integer) res[2]).intValue();
  if (a <= 0 && b <= 0) return 0;
  if (a <= 0) a = 1;
  int l = roll(worldSeed, u, role, a, b) + bonus;
  if (l > @PKG@.MobCfg.MAX_LEVEL) l = @PKG@.MobCfg.MAX_LEVEL;
  if (l < 1) l = 1;
  return l;
}""")
M(lv, 'public static String keyOf(int level) { return KEY_PREFIX + level; }')
M(lv, r"""
public static int levelOfKey(Object k) {
  if (!(k instanceof String)) return -1;
  String s = (String) k;
  if (!s.startsWith(KEY_PREFIX) || s.length() == KEY_PREFIX.length() || s.length() > KEY_PREFIX.length() + 4) return -1;
  int v = 0;
  for (int i = KEY_PREFIX.length(); i < s.length(); i++) {
    char c = s.charAt(i);
    if (c < '0' || c > '9') return -1;
    v = v * 10 + (c - '0');
  }
  return v >= 1 ? v : -1;
}""")
M(lv, r"""
public static int savedFromKeys(Object[] keys) {
  int best = -1;
  for (int i = 0; keys != null && i < keys.length; i++) {
    int v = levelOfKey(keys[i]);
    if (v > best) best = v;
  }
  return best;
}""")
# which kept level wins on an add: the save slot on the mob, else this session's memory (null = roll a new one)
M(lv, r"""
public static Object[] pick(int saved, Object kept) {
  if (saved > 0) return new Object[] { Integer.valueOf(saved), "saved" };
  if (kept instanceof Integer && ((Integer) kept).intValue() > 0) return new Object[] { kept, "kept" };
  return null;
}""")
# health after a max change: the same share of the new max (clamped 0..1)
M(lv, r"""
public static float share(float oldVal, float oldMax, float newMax) {
  if (oldMax <= 0.0f) return newMax;
  float s = oldVal / oldMax;
  if (s > 1.0f) s = 1.0f;
  if (s < 0.0f) s = 0.0f;
  return s * newMax;
}""")
# ---- names
M(lv, r"""
public static String stripRole(String role) {
  if (role == null) return "";
  String s = role;
  String[] ends = @PKG@.MobCfg.P_STRIP;
  boolean cut = true;
  for (int guard = 0; cut && guard < 8; guard++) {
    cut = false;
    String low = s.toLowerCase();
    for (int i = 0; ends != null && i < ends.length; i++) {
      String e = ends[i];
      if (e.length() > 0 && low.endsWith(e) && low.length() > e.length()) { s = s.substring(0, s.length() - e.length()); cut = true; break; }
    }
  }
  return s;
}""")
M(lv, r"""
public static String i18n(String key) {
  if (key == null || key.length() == 0) return null;
  try {
    @INTL@ m = @INTL@.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if ((s == null || s.length() == 0) && key.startsWith("server.")) s = m.getMessage("en-US", key.substring(7));
    return s == null || s.trim().length() == 0 ? null : s.trim();
  } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static String nameOf(String role, String tkey) {
  String r = role == null ? "" : role;
  String ck = r + "|" + (tkey == null ? "" : tkey);
  Object c = NAMES.get(ck);
  if (c instanceof String) return (String) c;
  String n = i18n(tkey);
  String base = stripRole(r);
  if (n == null) n = i18n("server.npcRoles." + base + ".name");
  if (n == null) n = base.replace('_', ' ').trim();
  if (n.length() == 0) n = r;
  if (NAMES.size() > 2000) NAMES.clear();
  NAMES.put(ck, n);
  return n;
}""")
# ---- nameplate text + markups (UNVERIFIED client support: colours off by default)
M(lv, r"""
public static String hexFor(int level) {
  int[] lv = @PKG@.MobCfg.COL_LV;
  String[] hx = @PKG@.MobCfg.COL_HEX;
  String h = "#ffffff";
  for (int i = 0; lv != null && hx != null && i < lv.length && i < hx.length; i++) if (lv[i] <= level) h = hx[i];
  return h;
}""")
# nearest of the 16 legacy colour codes (0-9, a-f) to a #rrggbb colour
M(lv, r"""
public static char legacy(String hex) {
  String codes = "0123456789abcdef";
  int[] pal = new int[] { 0x000000, 0x0000AA, 0x00AA00, 0x00AAAA, 0xAA0000, 0xAA00AA, 0xFFAA00, 0xAAAAAA, 0x555555, 0x5555FF, 0x55FF55, 0x55FFFF, 0xFF5555, 0xFF55FF, 0xFFFF55, 0xFFFFFF };
  int v = 0xFFFFFF;
  try { v = Integer.parseInt(hex.substring(1, 7), 16); } catch (Throwable t) { }
  int r = (v >> 16) & 255, g = (v >> 8) & 255, b = v & 255;
  int best = 15;
  long bd = Long.MAX_VALUE;
  for (int i = 0; i < 16; i++) {
    int pr = (pal[i] >> 16) & 255, pg = (pal[i] >> 8) & 255, pb = pal[i] & 255;
    long d = (long) (r - pr) * (r - pr) + (long) (g - pg) * (g - pg) + (long) (b - pb) * (b - pb);
    if (d < bd) { bd = d; best = i; }
  }
  return codes.charAt(best);
}""")
M(lv, r"""
public static String markup(String text, String hex, String mode) {
  if (text == null) return "";
  String m = mode == null ? "tag" : mode;
  if (m.equals("section")) return String.valueOf((char) 167) + legacy(hex) + text + String.valueOf((char) 167) + "r";
  if (m.equals("brace")) return "{" + hex + "}" + text;
  return "<color=" + hex + ">" + text + "</color>";
}""")
M(lv, r"""
public static String plateText(int level, String name) {
  String f = @PKG@.MobCfg.FORMAT;
  if (f == null || f.indexOf("{level}") < 0) f = "[Lv {level}] {name}";
  String t = f.replace("{level}", String.valueOf(level)).replace("{name}", name == null ? "" : name).trim();
  if (!@PKG@.MobCfg.COLOR_ON) return t;
  return markup(t, hexFor(level), @PKG@.MobCfg.MARKUP);
}""")
# the plate text without any of the three markups (and without a "1: " platetest prefix)
M(lv, r"""
public static String plain(String text) {
  if (text == null) return "";
  String s = text.replaceAll("</?color(=#[0-9A-Fa-f]{6})?>", "").replaceAll("\\{#[0-9A-Fa-f]{6}\\}", "");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == (char) 167) { i++; continue; }
    sb.append(c);
  }
  String r = sb.toString().trim();
  if (r.length() > 3 && r.charAt(0) >= '1' && r.charAt(0) <= '3' && r.charAt(1) == ':' && r.charAt(2) == ' ') r = r.substring(3);
  return r;
}""")
# a plate made with format f = the format's literal parts in order (the first one at the start when the format starts with it)
M(lv, r"""
public static boolean isOursFor(String text, String f) {
  if (text == null || f == null || f.indexOf("{level}") < 0) return false;
  String p = plain(text);
  String[] parts = f.replace("{name}", "{level}").split(java.util.regex.Pattern.quote("{level}"), -1);
  int pos = 0, hits = 0;
  for (int i = 0; i < parts.length; i++) {
    String s = parts[i];
    if (s.length() == 0) continue;
    int at = p.indexOf(s, pos);
    if (at < 0 || (i == 0 && at != 0)) return false;
    pos = at + s.length();
    hits++;
  }
  if (hits > 0) return true;
  return p.length() > 0 && p.charAt(0) >= '0' && p.charAt(0) <= '9';
}""")
# our plate (review F7): made with the current format, the default format or any format used this run - a mob that stops qualifying
# after an admin changed plate.format still loses its old plate
M(lv, r"""
public static boolean isOurs(String text) {
  if (text == null) return false;
  if (isOursFor(text, @PKG@.MobCfg.FORMAT) || isOursFor(text, @PKG@.MobCfg.FORMAT_DEFAULT)) return true;
  Object[] fs = @PKG@.MobCfg.FORMATS.keySet().toArray();
  for (int i = 0; i < fs.length; i++) if (fs[i] instanceof String && isOursFor(text, (String) fs[i])) return true;
  return false;
}""")
# ---- the lookup chain (pure: strings in, Object[]{Integer min, Integer max, Integer bonus, String step, String key} out)
M(lv, r"""
public static Object[] res(int a, int b, int bonus, String step, String key) {
  return new Object[] { Integer.valueOf(a), Integer.valueOf(b), Integer.valueOf(bonus), step, key };
}""")
M(lv, r"""
public static String zoneOfRegion(String region) {
  if (region == null || region.length() < 5 || !region.startsWith("Zone")) return null;
  int i = 4;
  while (i < region.length() && region.charAt(i) >= '0' && region.charAt(i) <= '9') i++;
  if (i == 4) return null;
  if (i < region.length() && region.charAt(i) != '_') return null;
  return region.substring(0, i);
}""")
M(lv, r"""
public static String zoneOfEnv(String env) {
  if (env == null || !env.startsWith("Env_Zone")) return null;
  return zoneOfRegion(env.substring(4));
}""")
M(lv, r"""
public static int volcanicZone(String env) {
  if (env == null || env.indexOf("_Caves_Volcanic") < 0) return 0;
  String z = zoneOfEnv(env);
  if (z == null || !env.startsWith("Env_" + z + "_Caves_Volcanic")) return 0;
  try { return Integer.parseInt(z.substring(4)); } catch (Throwable t) { return 0; }
}""")
M(lv, r"""
public static Object[] resolve(String wn, boolean island, boolean classic, String region, String biome, String tile, String env) {
  @PKG@.MobBands W = @PKG@.MobCfg.WORLD, E = @PKG@.MobCfg.ENV, BI = @PKG@.MobCfg.BIOME, Z = @PKG@.MobCfg.ZONE;
  int wi = W == null ? -1 : W.findPrefix(wn);
  if (wi >= 0) return res(W.a[wi], W.b[wi], 0, "world", W.raw[wi]);
  if (island) return res(@PKG@.MobCfg.ISL_A, @PKG@.MobCfg.ISL_B, 0, "island", "bands.islands");
  int ei = (E == null || env == null) ? -1 : E.find(env);
  int ebonus = ei >= 0 ? E.c[ei] : 0;
  int vz = volcanicZone(env);
  int[] ta = @PKG@.MobCfg.ZTOP_A, tb = @PKG@.MobCfg.ZTOP_B;
  if (@PKG@.MobCfg.VOLCANIC && vz > 0 && ta != null && vz < ta.length && tb[vz] > 0)
    return res(ta[vz], tb[vz], ebonus, "lava", "Zone" + vz + " top " + @PKG@.MobCfg.ZTOP_KEY[vz]);
  if (classic && region != null && BI != null) {
    String used = biome;
    if (biome != null && tile != null && @PKG@.MobCfg.passes(biome)) used = tile;
    int bi = used == null ? -1 : BI.find(region + "." + used);
    if (bi < 0 && used != biome && biome != null) bi = BI.find(region + "." + biome);
    if (bi < 0) bi = BI.find(region);
    if (bi < 0) bi = BI.find(region + ".*");
    if (bi >= 0) return res(BI.a[bi], BI.b[bi], ebonus, "biome", BI.raw[bi]);
  }
  if (ei >= 0) return res(E.a[ei], E.b[ei], 0, "env", E.raw[ei]);
  String z = zoneOfRegion(region);
  if (z == null) z = zoneOfEnv(env);
  int zi = (Z == null || z == null) ? -1 : Z.find(z);
  if (zi >= 0) return res(Z.a[zi], Z.b[zi], 0, "zone", Z.raw[zi]);
  return res(@PKG@.MobCfg.DEF_A, @PKG@.MobCfg.DEF_B, 0, "default", "bands.default");
}""")
# ---- engine glue: environment, worldgen, island
M(lv, r"""
public static String envId(int idx) {
  if (idx == Integer.MIN_VALUE || idx < 0) return null;
  try {
    Object a = @ENVA@.getAssetMap().getAsset(idx);
    if (a instanceof @ENVA@) return ((@ENVA@) a).getId();
  } catch (Throwable t) { }
  return null;
}""")
M(lv, r"""
public static int blockEnv(@WLD@ w, int x, int y, int z) {
  if (w == null) return Integer.MIN_VALUE;
  try {
    Object c = w.getChunkStore().getChunkComponent(@CHU@.indexChunkFromBlock(x, z), @BCH@.getComponentType());
    if (c instanceof @BCH@) return ((@BCH@) c).getEnvironment(x, y, z);
  } catch (Throwable t) { }
  return Integer.MIN_VALUE;
}""")
M(lv, r"""
public static boolean islandOf(String wn) {
  if (wn == null) return false;
  try {
    Object f = bridge().get("island:owner:fn");
    if (f instanceof java.util.function.Function) return ((java.util.function.Function) f).apply(wn) != null;
  } catch (Throwable t) { }
  return false;
}""")
# String[]{ region, biome, tile, zoneName, classic "1"/"0" } for a column of a world, cached per exact block column (review F3: an 8x8
# cell reused the first spawn's biome for its neighbours across a biome border; the engine caches the lookup itself, ChunkGeneratorCache).
# A failed lookup or a world whose generator is not attached yet is NOT cached: the next spawn there asks again.
M(lv, r"""
public static String[] worldgen(@WLD@ w, int x, int z) {
  if (w == null) return null;
  String wn = w.getName();
  String ck = wn + ":" + x + ":" + z;
  Object c = WG.get(ck);
  if (c instanceof String[]) return (String[]) c;
  String[] r = null;
  boolean keep = true;
  try {
    Object g = w.getChunkStore().getGenerator();
    if (g instanceof @CGEN@) {
      int seed = (int) w.getWorldConfig().getSeed();
      @ZBR@ zr = ((@CGEN@) g).getZoneBiomeResultAt(seed, x, z);
      @ZONE@ zone = zr.getZoneResult().getZone();
      String biome = zr.getBiome() == null ? null : zr.getBiome().getName();
      String tile = null;
      try { tile = zone.biomePatternGenerator().getBiome(seed, x, z).getName(); } catch (Throwable t1) { tile = null; }
      String zn = null;
      try { zn = zone.discoveryConfig() == null ? null : zone.discoveryConfig().zone(); } catch (Throwable t2) { zn = null; }
      r = new String[] { zone.name(), biome, tile, zn, "1" };
    } else {
      r = new String[] { null, null, null, null, "0" };
      keep = g != null;
    }
  } catch (Throwable t) {
    @PKG@.MobLog.warnOnce("worldgen:" + wn, "could not read the worldgen zone / biome in world " + wn + ": " + t + " - mobs spawned there meanwhile use the environment / zone / default rows (asked again on the next spawn)");
    r = new String[] { null, null, null, null, "0" };
    keep = false;
  }
  if (keep) {
    if (WG.size() >= WG_MAX) WG.clear();
    WG.put(ck, r);
  }
  return r;
}""")
# Object[]{ min, max, bonus, step, key, region, biome, tile, env, zoneName, classic, island } at a position (envIdx = the spawn env or MIN)
M(lv, r"""
public static Object[] lookupAt(@WLD@ w, double x, double y, double z, int envIdx) {
  int bx = (int) Math.floor(x), by = (int) Math.floor(y), bz = (int) Math.floor(z);
  String wn = w == null ? "" : w.getName();
  int ei = envIdx;
  if (ei == Integer.MIN_VALUE) ei = blockEnv(w, bx, by, bz);
  String env = envId(ei);
  String[] g = worldgen(w, bx, bz);
  boolean classic = g != null && "1".equals(g[4]);
  boolean island = islandOf(wn);
  Object[] r = resolve(wn, island, classic, classic ? g[0] : null, classic ? g[1] : null, classic ? g[2] : null, env);
  return new Object[] { r[0], r[1], r[2], r[3], r[4], classic ? g[0] : null, classic ? g[1] : null, classic ? g[2] : null, env,
                        classic ? g[3] : null, classic ? "1" : "0", island ? "1" : "0" };
}""")
# ---- the health modifier (save slot)
M(lv, r"""
public static Object[] modKeys(@ESM@ m, int hi) {
  try {
    @ESV@ v = m.get(hi);
    java.util.Map mods = v == null ? null : v.getModifiers();
    if (mods == null || mods.isEmpty()) return new Object[0];
    return mods.keySet().toArray();
  } catch (Throwable t) { return new Object[0]; }
}""")
M(lv, "public static int savedLevel(@ESM@ m, int hi) { return m == null ? -1 : savedFromKeys(modKeys(m, hi)); }")
# remove every save-slot key except keep; true when one was removed
M(lv, r"""
public static boolean removeOurs(@ESM@ m, int hi, String keep) {
  boolean any = false;
  Object[] ks = modKeys(m, hi);
  for (int i = 0; i < ks.length; i++) {
    if (levelOfKey(ks[i]) > 0 && (keep == null || !keep.equals(ks[i]))) { m.removeModifier(hi, (String) ks[i]); any = true; }
  }
  return any;
}""")
# 0.1.2: the mob's own max health under our multiplier (the floor's base). EntityStatValue.computeModifiers (bytecode 2026-10-02):
# max = (stat max + the additive MAX StaticModifiers) x the SUM of the multiplicative MAX StaticModifiers (when there is one), so
# base = max / that sum, or max when there is none - the same whether our old modifier is on the mob or not. Rounded to 0.01 HP: the
# same mob always reads the same base, so a reload never re-puts its modifier for a float hair. -1 = unknown (no stat, a 0 sum).
M(lv, r"""
public static double baseOf(@ESM@ m, int hi) {
  if (m == null) return -1.0;
  @ESV@ v = m.get(hi);
  if (v == null) return -1.0;
  double sum = 0.0;
  boolean any = false;
  java.util.Map mods = v.getModifiers();
  if (mods != null) {
    java.util.Iterator it = mods.values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @SMO@)) continue;
      @SMO@ s = (@SMO@) o;
      if (s.getTarget() == @MTG@.MAX && s.getCalculationType() == @CAL@.MULTIPLICATIVE) { sum = sum + (double) s.getAmount(); any = true; }
    }
  }
  double mx = (double) v.getMax();
  if (any) {
    if (sum < 0.000001) return -1.0;
    mx = mx / sum;
  }
  if (!(mx > 0.0) || mx > 1.0E9) return -1.0;
  return Math.round(mx * 100.0) / 100.0;
}""")
# the amount of one of our modifiers on the mob (-1 = not there)
M(lv, r"""
public static float amountOn(@ESM@ m, int hi, String key) {
  try {
    Object o = m == null ? null : m.getModifier(hi, key);
    return o instanceof @SMO@ ? ((@SMO@) o).getAmount() : -1.0f;
  } catch (Throwable t) { return -1.0f; }
}""")
# two health amounts are the same (one part in a million, at least 0.000001 - 0.1.1's absolute test for amounts up to 1)
M(lv, r"""
public static boolean same(float a, float b) {
  float t = 0.000001f * Math.max(1.0f, Math.max(Math.abs(a), Math.abs(b)));
  return Math.abs(a - b) <= t;
}""")
# 0.1.3 (F1): write a stat value right after a modifier change of that stat WITHOUT a Set / Maximize network entry. The engine merges a
# Set / Maximize into the pending PutModifier / RemoveModifier entry (EntityStatMap.tryMergeUpdate rewrites the last entry's op), so a
# player who already saw the mob never got its new max. Min / Max entries are appended, never merged: the modifier entry survives and
# the client gets the max first, then the value. The server value ends where setStatValue(target) put it: below the current value =
# minStatValue (min(cur, target) = target), above = maxStatValue (max(cur, target) = target), both clamped by EntityStatValue.set like
# setStatValue; equal = no write (setStatValue queues nothing then either).
M(lv, r"""
public static void writeValue(@ESM@ m, int hi, float target) {
  @ESV@ v = m.get(hi);
  if (v == null) return;
  float cur = v.get();
  if (target < cur) m.minStatValue(hi, target);
  else if (target > cur) m.maxStatValue(hi, target);
}""")
# put the level's health amount (0.1.2: level multiplier x the floor factor of the mob's base); full = maximize, heal = maximize when the
# amount is put (0.1.1's strength.healOnLoad); else the health SHARE is kept when the max changed (0.1.3: both writes go through
# writeValue - Min / Max entries, never Set / Maximize, so the PutModifier / RemoveModifier entry reaches the mob's viewers)
M(lv, r"""
public static float setMult(@ESM@ m, int hi, int level, boolean full, boolean heal, double rx) {
  double base = baseOf(m, hi);
  float mult = @PKG@.MobCfg.hpAmount(level, base, rx);
  String key = keyOf(level);
  @ESV@ v = m.get(hi);
  if (v == null) return mult;
  float oldMax = v.getMax(), oldVal = v.get();
  boolean changed = removeOurs(m, hi, key);
  Object cur = m.getModifier(hi, key);
  if (!(cur instanceof @SMO@) || !same(((@SMO@) cur).getAmount(), mult)) {
    m.putModifier(hi, key, new @SMO@(@MTG@.MAX, @CAL@.MULTIPLICATIVE, mult));
    changed = true;
  }
  if (full || heal) {
    @ESV@ vf = m.get(hi);
    if (vf != null) writeValue(m, hi, vf.getMax());
    return mult;
  }
  if (changed && oldMax > 0.0f) {
    @ESV@ v2 = m.get(hi);
    writeValue(m, hi, share(oldVal, oldMax, v2 == null ? oldMax : v2.getMax()));
  }
  return mult;
}""")
# 0.1.3's form (no scale.role factor) and 0.1.1's form (spawn / chunk load / /mobs set: heal = strength.healOnLoad), exactly as before
M(lv, r"""
public static float setMult(@ESM@ m, int hi, int level, boolean full, boolean heal) { return setMult(m, hi, level, full, heal, 1.0); }""")
M(lv, r"""
public static float setMult(@ESM@ m, int hi, int level, boolean full) { return setMult(m, hi, level, full, @PKG@.MobCfg.HEAL_ON_LOAD); }""")
M(lv, r"""
public static void stripStats(@ESM@ m, int hi) {
  @ESV@ v = m.get(hi);
  if (v == null) return;
  float oldMax = v.getMax(), oldVal = v.get();
  if (!removeOurs(m, hi, null)) return;
  @ESV@ v2 = m.get(hi);
  if (v2 != null && oldMax > 0.0f) writeValue(m, hi, share(oldVal, oldMax, v2.getMax()));
}""")
# ---- components through a Holder (the hook) or a Store + Ref (commands)
M(lv, r"""
public static @COMP@ comp(@HOLD@ h, @ST@ st, @REF@ r, @CTYPE@ t) {
  if (t == null) return null;
  if (h != null) return h.getComponent(t);
  if (st == null || r == null || !r.isValid()) return null;
  return st.getComponent(r, t);
}""")
M(lv, r"""
public static void setPlate(@HOLD@ h, @ST@ st, @REF@ r, String text) {
  @NPL@ p = null;
  if (h != null) p = (@NPL@) h.ensureAndGetComponent(@NPL@.getComponentType());
  else if (st != null && r != null && r.isValid()) p = (@NPL@) st.ensureAndGetComponent(r, @NPL@.getComponentType());
  if (p != null && !text.equals(p.getText())) p.setText(text);
}""")
M(lv, r"""
public static void dropPlate(@HOLD@ h, @ST@ st, @REF@ r, boolean onlyOurs) {
  if (h == null && (st == null || r == null)) return;
  @NPL@ p = (@NPL@) comp(h, st, r, @NPL@.getComponentType());
  if (p == null) return;
  if (onlyOurs && !isOurs(p.getText())) return;
  if (h != null) h.tryRemoveComponent(@NPL@.getComponentType());
  else if (st != null && r != null && r.isValid()) st.tryRemoveComponent(r, @NPL@.getComponentType());
}""")
M(lv, r"""
public static String plateOf(@HOLD@ h, @ST@ st, @REF@ r) {
  if (h == null && (st == null || r == null)) return null;
  @NPL@ p = (@NPL@) comp(h, st, r, @NPL@.getComponentType());
  return p == null ? null : p.getText();
}""")
M(lv, r"""
public static String tkeyOf(@NPCE@ npc) {
  try { return npc.getRole() == null ? null : npc.getRole().getNameTranslationKey(); } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static @PKG@.MobInfo apply(@HOLD@ h, @ST@ st, @REF@ r, @NPCE@ npc, @ESM@ m, java.util.UUID u, @WLD@ w, String wn, String role,
                                   int level, boolean full, String step, Object[] res) {
  int hi = @DST@.getHealth();
  double rx = @PKG@.MobCfg.roleX(role);
  setMult(m, hi, level, full, @PKG@.MobCfg.HEAL_ON_LOAD, rx);
  String name = nameOf(role, tkeyOf(npc));
  if ("off".equals(@PKG@.MobCfg.PLATE_MODE)) dropPlate(h, st, r, true);
  else setPlate(h, st, r, plateText(level, name));
  @PKG@.MobInfo i = new @PKG@.MobInfo();
  i.world = wn; i.uuid = u; i.role = role; i.name = name; i.level = level; i.step = step; i.at = System.currentTimeMillis();
  i.base = baseOf(m, hi); i.rx = rx;
  if (w != null) i.wref = new java.lang.ref.WeakReference(w);
  if (res != null) {
    i.a = ((Integer) res[0]).intValue(); i.b = ((Integer) res[1]).intValue(); i.bonus = ((Integer) res[2]).intValue();
    i.key = (String) res[4];
  }
  if (u != null) { MOBS.put(u, i); KEPT.remove(u); }
  return i;
}""")
M(lv, r"""
public static void strip(@HOLD@ h, @ST@ st, @REF@ r, @ESM@ m, java.util.UUID u) {
  if (m != null) stripStats(m, @DST@.getHealth());
  dropPlate(h, st, r, true);
  if (u != null) { MOBS.remove(u); KEPT.remove(u); }
}""")
M(lv, r"""
public static @WLD@ worldOf(@ST@ st) {
  try { Object e = st.getExternalData(); return e instanceof @EST@ ? ((@EST@) e).getWorld() : null; } catch (Throwable t) { return null; }
}""")
# the spawn point: the leash point (saved LeashPos) when set, else the current position
M(lv, r"""
public static double[] spawnPos(@NPCE@ npc, @HOLD@ h, @ST@ st, @REF@ r) {
  try {
    @VEC@ lp = npc.getLeashPoint();
    if (lp != null && (lp.x != 0.0 || lp.y != 0.0 || lp.z != 0.0)) return new double[] { lp.x, lp.y, lp.z };
  } catch (Throwable t) { }
  @TC@ tc = (@TC@) comp(h, st, r, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) return null;
  @VEC@ p = tc.getPosition();
  return new double[] { p.x, p.y, p.z };
}""")
M(lv, r"""
public static String attitudeOf(@HOLD@ h, @ST@ st, @REF@ r) {
  try {
    @WSUP@ ws = (@WSUP@) comp(h, st, r, @WSUP@.getComponentType());
    return ws == null || ws.getDefaultPlayerAttitude() == null ? "" : ws.getDefaultPlayerAttitude().name();
  } catch (Throwable t) { return ""; }
}""")
# Object[] lookup result (lookupAt) for a mob: its spawn point + its spawn environment
M(lv, r"""
public static Object[] lookupMob(@WLD@ w, @NPCE@ npc, @HOLD@ h, @ST@ st, @REF@ r) {
  double[] p = spawnPos(npc, h, st, r);
  if (p == null) return null;
  int ei = Integer.MIN_VALUE;
  try { ei = npc.getEnvironment(); } catch (Throwable t) { ei = Integer.MIN_VALUE; }
  return lookupAt(w, p[0], p[1], p[2], ei);
}""")
M(lv, r"""
public static void onAdd(@HOLD@ h, boolean spawn, @ST@ st) {
  @NPCE@ npc = (@NPCE@) h.getComponent(@NPCE@.getComponentType());
  if (npc == null) return;
  @ESM@ m = (@ESM@) h.getComponent(@ESM@.getComponentType());
  if (m == null) return;
  @UUIDC@ uc = (@UUIDC@) h.getComponent(@UUIDC@.getComponentType());
  java.util.UUID u = uc == null ? null : uc.getUuid();
  if (u == null) return;
  String role = npc.getRoleName();
  int hi = @DST@.getHealth();
  int saved = savedLevel(m, hi);
  Object kept = KEPT.remove(u);
  int fixed = @PKG@.MobCfg.roleLevel(role);
  String no = null;
  if (fixed <= 0) no = @PKG@.MobCfg.whyNot(attitudeOf(h, null, null), role);
  if (no != null) {
    if (saved > 0 || isOurs(plateOf(h, null, null))) strip(h, null, null, m, u);
    return;
  }
  @WLD@ w = worldOf(st);
  String wn = w == null ? "" : w.getName();
  Object[] pk = pick(saved, kept);
  int level = pk == null ? 0 : ((Integer) pk[0]).intValue();
  String step = pk == null ? null : (String) pk[1];
  Object[] res = null;
  if (fixed > 0) {
    if (level <= 0 && !@PKG@.MobCfg.ON) return;
    level = fixed;
    step = "role";
    res = @PKG@.MobLevel.res(fixed, fixed, 0, "role", @PKG@.MobCfg.roleKey(role));
  }
  if (level <= 0) {
    if (!@PKG@.MobCfg.ON) return;
    res = lookupMob(w, npc, h, null, null);
    long seed = 0L;
    try { seed = w == null ? 0L : w.getWorldConfig().getSeed(); } catch (Throwable t) { seed = 0L; }
    level = levelFor(res, seed, u, role);
    if (level <= 0) return;
    step = (String) res[3];
  }
  apply(h, null, null, npc, m, u, w, wn, role, level, spawn, step, res);
}""")
M(lv, r"""
public static void forget(java.util.UUID u, boolean unload) {
  if (u == null) return;
  Object o = MOBS.remove(u);
  if (unload && o instanceof @PKG@.MobInfo) {
    if (KEPT.size() >= KEPT_MAX) KEPT.clear();
    KEPT.put(u, Integer.valueOf(((@PKG@.MobInfo) o).level));
  } else KEPT.remove(u);
}""")
M(lv, r"""
public static void onRemove(@HOLD@ h, boolean unload) {
  @UUIDC@ uc = (@UUIDC@) h.getComponent(@UUIDC@.getComponentType());
  forget(uc == null ? null : uc.getUuid(), unload);
}""")
M(lv, r"""
public static void clearAll() { MOBS.clear(); KEPT.clear(); WG.clear(); NAMES.clear(); }""")
# ---- the prune (review F6: a removed world's store may never call onEntityRemoved, so MOBS could keep its mobs forever).
# MobPruneTask runs every 5 minutes on the scheduler: pruneWith forgets mobs whose world is gone, then each loaded world with levelled
# mobs checks its own on its world thread (pruneWorld). KEPT needs no prune: it is bounded (KEPT_MAX, cleared when full).
M(lv, r"""
public static java.util.ArrayList liveWorlds() {
  try {
    @UNIV@ u = @UNIV@.get();
    if (u == null) return null;
    java.util.Map m = u.getWorlds();
    return m == null ? null : new java.util.ArrayList(m.values());
  } catch (Throwable t) { return null; }
}""")
M(lv, r"""
public static java.util.ArrayList namesOf(java.util.Collection worlds) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = worlds == null ? null : worlds.iterator();
  while (it != null && it.hasNext()) {
    Object o = it.next();
    try { if (o instanceof @WLD@) out.add(((@WLD@) o).getName()); } catch (Throwable t) { }
  }
  return out;
}""")
# forget every mob (older than PRUNE_GRACE) whose world is not one of `worlds` (by identity; its weak reference cleared = gone too);
# a mob without a world reference goes by its world name (names == null: kept). Removes only the exact entry it looked at.
M(lv, r"""
public static int pruneWith(java.util.Collection worlds, java.util.Collection names, long now) {
  java.util.IdentityHashMap live = new java.util.IdentityHashMap();
  java.util.Iterator wi = worlds == null ? null : worlds.iterator();
  while (wi != null && wi.hasNext()) {
    Object o = wi.next();
    if (o != null) live.put(o, Boolean.TRUE);
  }
  int n = 0;
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    boolean gone = false;
    if (!(v instanceof @PKG@.MobInfo)) gone = true;
    else {
      @PKG@.MobInfo i = (@PKG@.MobInfo) v;
      if (now - i.at >= PRUNE_GRACE) {
        if (i.wref != null) { Object w = i.wref.get(); gone = w == null || !live.containsKey(w); }
        else gone = names != null && (i.world == null || !names.contains(i.world));
      }
    }
    if (gone && MOBS.remove(e.getKey(), v)) n++;
  }
  return n;
}""")
M(lv, r"""
public static boolean hasMobsIn(Object w) {
  if (w == null) return false;
  java.util.Iterator it = MOBS.values().iterator();
  while (it.hasNext()) {
    Object v = it.next();
    if (v instanceof @PKG@.MobInfo && ((@PKG@.MobInfo) v).wref != null && ((@PKG@.MobInfo) v).wref.get() == w) return true;
  }
  return false;
}""")
# on the world thread of w: forget its levelled mobs whose entity is gone (a removal that skipped the hook)
M(lv, r"""
public static int pruneWorld(@WLD@ w, long now) {
  if (w == null) return 0;
  @EST@ es = w.getEntityStore();
  if (es == null) return 0;
  int n = 0;
  java.util.Iterator it = MOBS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof @PKG@.MobInfo)) continue;
    @PKG@.MobInfo i = (@PKG@.MobInfo) v;
    if (i.wref == null || i.wref.get() != w || now - i.at < PRUNE_GRACE || i.uuid == null) continue;
    @REF@ r = es.getRefFromUUID(i.uuid);
    if ((r == null || !r.isValid()) && MOBS.remove(e.getKey(), v)) n++;
  }
  return n;
}""")

# ---- 0.1.2: the live health re-apply (Skyy's 0.1.1 test: a difficulty change never reached the max health of loaded mobs).
# refreshOne = one loaded levelled mob, on its world thread: the health modifier for the settings now, the health PERCENT kept, never
# healed (full = false, heal = false - strength.healOnLoad is for chunk loads), never killed (a mob at 0 HP is not touched).
# true = its modifier changed.
M(lv, r"""
public static boolean refreshOne(@ESM@ m, int hi, int level, double rx) {
  if (m == null || level <= 0) return false;
  @ESV@ v = m.get(hi);
  if (v == null || !(v.get() > 0.0f)) return false;
  float before = amountOn(m, hi, keyOf(level));
  float now = setMult(m, hi, level, false, false, rx);
  return before < 0.0f || !same(before, now);
}""")
M(lv, "public static boolean refreshOne(@ESM@ m, int hi, int level) { return refreshOne(m, hi, level, 1.0); }")
# on the world thread of w (a MobRefresh task): every levelled mob of w that is still loaded gets refreshOne; how many changed
M(lv, r"""
public static int refreshWorld(@WLD@ w) {
  if (w == null) return 0;
  @EST@ es = w.getEntityStore();
  if (es == null) return 0;
  @ST@ st = es.getStore();
  if (st == null) return 0;
  int hi = @DST@.getHealth();
  @CTYPE@ t = @ESM@.getComponentType();
  int n = 0;
  java.util.Iterator it = MOBS.values().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @PKG@.MobInfo)) continue;
    @PKG@.MobInfo i = (@PKG@.MobInfo) o;
    if (i.wref == null || i.wref.get() != w || i.uuid == null || i.level <= 0) continue;
    @REF@ r = es.getRefFromUUID(i.uuid);
    if (r == null || !r.isValid()) continue;
    try {
      @ESM@ m = (@ESM@) st.getComponent(r, t);
      double rx = @PKG@.MobCfg.roleX(i.role);
      if (refreshOne(m, hi, i.level, rx)) n++;
      i.rx = rx;
      if (m != null) i.base = baseOf(m, hi);
    } catch (Throwable x) { @PKG@.MobLog.warnOnce("refresh1:" + x.getClass().getName(), "could not re-apply the health of a levelled mob (" + x + ") - it gets it when its chunk reloads"); }
  }
  return n;
}""")

# ---------------------------------------------------------------- LevelHook (HolderSystem; ordered AFTER the NPC setup systems)
for f in ("public static Class RBS;", "public static Class SETUP;", "public static Class BAL;", "public java.util.Set deps;",
          "public boolean ordered;", "public @QRY@ query;"):
    F(hk, f)
C(hk, r"""
public LevelHook(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered;
  if (ordered) {
    if (RBS != null) this.deps.add(new @SDEP@(@ORD@.AFTER, RBS));
    if (SETUP != null) this.deps.add(new @SDEP@(@ORD@.AFTER, SETUP));
    if (BAL != null) this.deps.add(new @SDEP@(@ORD@.AFTER, BAL));
  }
}""")
M(hk, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @ESM@.getComponentType() });
  return this.query;
}""")
M(hk, "public java.util.Set getDependencies() { return this.deps; }")
M(hk, r"""
public void onEntityAdd(@HOLD@ h, @ADDR@ why, @ST@ st) {
  try { @PKG@.MobLevel.onAdd(h, why == @ADDR@.SPAWN, st); }
  catch (Throwable t) { @PKG@.MobLog.warnOnce("hook:" + t.getClass().getName(), "level hook failed (" + t + ") - that mob keeps vanilla stats"); }
}""")
M(hk, r"""
public void onEntityRemoved(@HOLD@ h, @REMR@ why, @ST@ st) {
  try { @PKG@.MobLevel.onRemove(h, why == @REMR@.UNLOAD); } catch (Throwable t) { }
}""")
# (no unordered fallback class any more - review F4: unordered, the hook could run before the role / stat map exist and level nothing,
# or read the attitude as unknown and strip saved levels on load; SkyyMobsPlugin.systems logs an ERROR instead)

# ---------------------------------------------------------------- 0.1.4 MobGap: the BRUTAL level gap (spec 3.1, accepted 2026-10-05)
# d = mob level - your class weapon skill level. d <= free: x1 both ways. Above: your hits x max(dealtMin, 1 - dealtStep x (d - free)),
# its hits on you x min(takenMax, 1 + takenStep x (d - free)). Mobs below you: no change. "Your level" = class:skill:<uuid> +
# skill:fn:level (the read /mobs info already does), cached per player for 2 s (a level-up mid-fight counts within 2 s). Level 0 =
# unknown (skill:fn:level turns every failure into 0; a player under 50 XP is 0): no gap, and a cached good level is never overwritten
# by a 0 (feasibility critic F6). No class (no class:skill) = no gap.
F(gp, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(gp, "public static volatile long TTL = @GTTL@L;")
F(gp, "public static final int CACHE_MAX = 10000;")
M(gp, r"""
public static double dealt(int d) {
  int free = @PKG@.MobCfg.GAP_FREE;
  if (d <= free) return 1.0;
  double f = 1.0 - @PKG@.MobCfg.GAP_DSTEP / 100.0 * (double) (d - free);
  double mn = @PKG@.MobCfg.GAP_DMIN / 100.0;
  if (f < mn) f = mn;
  if (f > 1.0) f = 1.0;
  return f;
}""")
M(gp, r"""
public static double taken(int d) {
  int free = @PKG@.MobCfg.GAP_FREE;
  if (d <= free) return 1.0;
  double f = 1.0 + @PKG@.MobCfg.GAP_TSTEP / 100.0 * (double) (d - free);
  double mx = @PKG@.MobCfg.GAP_TMAX;
  if (f > mx) f = mx;
  if (f < 1.0) f = 1.0;
  return f;
}""")
# one fresh read: -1 = no class (no class:skill:<uuid>), 0 = unknown (no skill:fn:level, a failure, a 0 answer), else the level
M(gp, r"""
public static int readLevel(java.util.UUID u) {
  if (u == null) return 0;
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object cs = b.get("class:skill:" + u);
    if (!(cs instanceof String) || ((String) cs).length() == 0) return -1;
    Object f = b.get("skill:fn:level");
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, cs });
    if (!(r instanceof Number)) return 0;
    int l = ((Number) r).intValue();
    return l > 0 ? l : 0;
  } catch (Throwable t) { return 0; }
}""")
# the cached level (2 s): > 0 = the gap applies against it; -1 / 0 = no gap
M(gp, r"""
public static int level(java.util.UUID u, long now) {
  if (u == null) return 0;
  Object o = CACHE.get(u);
  long[] c = null;
  if (o instanceof long[]) c = (long[]) o;
  if (c != null && now - c[1] >= 0L && now - c[1] < TTL) return (int) c[0];
  int r = readLevel(u);
  if (r == 0 && c != null && c[0] > 0L) r = (int) c[0];
  if (CACHE.size() >= CACHE_MAX) CACHE.clear();
  CACHE.put(u, new long[] { (long) r, now });
  return r;
}""")
# d for a mob of this level against player u (Integer.MIN_VALUE = no gap: part off, no class, level unknown)
M(gp, r"""
public static int gapOf(int mobLevel, java.util.UUID u, long now) {
  if (!@PKG@.MobCfg.GAP_ON || mobLevel <= 0) return Integer.MIN_VALUE;
  int l = level(u, now);
  if (l <= 0) return Integer.MIN_VALUE;
  return mobLevel - l;
}""")
M(gp, r"""
public static String pctOf(double f) { return String.valueOf(Math.round(f * 100.0)) + "%"; }""")
M(gp, r"""
public static String range(double a, double b) {
  String x = pctOf(Math.min(a, b)), y = pctOf(Math.max(a, b));
  return x.equals(y) ? x : x.substring(0, x.length() - 1) + "-" + y;
}""")
# /mobs info: the gap for mobs dlo..dhi levels above you ("" = none: part off, the whole band inside the free levels)
M(gp, r"""
public static String bandText(int dlo, int dhi) {
  int free = @PKG@.MobCfg.GAP_FREE;
  if (!@PKG@.MobCfg.GAP_ON || dhi <= free) return "";
  int lo = dlo > free ? dlo : free + 1;
  return " - level gap: you deal " + range(dealt(dhi), dealt(lo)) + ", they hit you for " + range(taken(lo), taken(dhi));
}""")

# ---------------------------------------------------------------- 0.1.4 GapDamage (Filter group, BEFORE ArmorDamageReduction): a player's hit
# on a levelled mob x dealt(d) (spec 3.3). Attacker = a player (PlayerRef on the source ref; a projectile's source is a ProjectileSource =
# an EntitySource whose ref is the shooter), victim = a levelled mob in MOBS. Pets, summons, mob vs mob and player vs player: no gap.
# Cancelled hits (SkyyClasses' DamageLock) are skipped. A multiplier like SkyyGear's GearHitSys / SkyySkills' CombatDmgSys /
# SkyyArmory's ArmoryTuneSys, so the order between them never changes the result. GapDamageU = the unordered fallback (LevelDamageU pattern).
for f in ("public static Class ADR;", "public java.util.Set deps;", "public boolean ordered;"):
    F(gd, f)
C(gd, r"""
public GapDamage(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ADR != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.BEFORE, ADR));
}""")
M(gd, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(gd, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(gd, "public java.util.Set getDependencies() { return this.deps; }")
M(gd, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.MobCfg.GAP_ON || @PKG@.MobLevel.MOBS.isEmpty() || !(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid()) return;
    @PR@ pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
    if (pr == null) return;
    @REF@ vr = chunk.getReferenceTo(idx);
    if (vr == null || !vr.isValid()) return;
    @UUIDC@ vu = (@UUIDC@) buf.getComponent(vr, @UUIDC@.getComponentType());
    if (vu == null) return;
    @PKG@.MobInfo i = (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(vu.getUuid());
    if (i == null || i.level <= 0) return;
    int g = @PKG@.MobGap.gapOf(i.level, pr.getUuid(), System.currentTimeMillis());
    if (g == Integer.MIN_VALUE) return;
    double f = @PKG@.MobGap.dealt(g);
    float a = d.getAmount();
    if (f < 1.0 && a > 0.0f) d.setAmount((float) ((double) a * f));
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("gapdmg", "level gap (your damage) failed: " + t); }
}""")
C(gdu, "public GapDamageU() { super(false); }")

# ---------------------------------------------------------------- LevelDamage (Filter group, BEFORE ArmorDamageReduction)
for f in ("public static Class ADR;", "public java.util.Set deps;", "public boolean ordered;"):
    F(dm, f)
C(dm, r"""
public LevelDamage(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  this.ordered = ordered && ADR != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.BEFORE, ADR));
}""")
M(dm, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(dm, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(dm, "public java.util.Set getDependencies() { return this.deps; }")
M(dm, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (@PKG@.MobLevel.MOBS.isEmpty() || !(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid()) return;
    @UUIDC@ uc = (@UUIDC@) buf.getComponent(att, @UUIDC@.getComponentType());
    if (uc == null) return;
    @PKG@.MobInfo i = (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(uc.getUuid());
    if (i == null || i.level <= 1) return;
    float mult = @PKG@.MobCfg.dmgMult(i.level);
    @REF@ vr = chunk.getReferenceTo(idx);
    @PR@ vp = null;
    if (vr != null && vr.isValid()) vp = (@PR@) buf.getComponent(vr, @PR@.getComponentType());
    if (vp == null) {
      if (mult != 1.0f) d.setAmount(d.getAmount() * mult);
      return;
    }
    float a = d.getAmount();
    double amt = (double) a;
    int fl = @PKG@.MobCfg.DMG_FLOOR;
    if (fl > 0 && i.level > 20 && a > 0.0f) {
      double b = i.base;
      if (b > 0.0) {
        int hf = @PKG@.MobCfg.HP_FLOOR;
        double xb = (hf > 0 && (double) hf > b) ? (double) hf : b;
        double ramp = i.level >= 30 ? 1.0 : (double) (i.level - 20) / 10.0;
        double low = (double) fl / 100.0 * xb * ramp;
        if (amt < low) amt = low;
      }
    }
    amt = amt * (double) mult;
    int g = @PKG@.MobGap.gapOf(i.level, vp.getUuid(), System.currentTimeMillis());
    if (g != Integer.MIN_VALUE) amt = amt * @PKG@.MobGap.taken(g);
    int hc = @PKG@.MobCfg.HIT_CAP;
    if (hc > 0) {
      @ESM@ vm = (@ESM@) buf.getComponent(vr, @ESM@.getComponentType());
      @ESV@ hv = vm == null ? null : vm.get(@DST@.getHealth());
      float vmax = hv == null ? 0.0f : hv.getMax();
      if (vmax > 0.0f) {
        double cap = (double) hc / 100.0 * (double) vmax;
        if (amt > cap) amt = cap;
      }
    }
    float out = (float) amt;
    if (out != a) d.setAmount(out);
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("dmg", "level damage failed: " + t); }
}""")
C(dmu, "public LevelDamageU() { super(false); }")

# ---------------------------------------------------------------- mob:fn:level (bridge, any thread, never throws)
fn.addInterface(pool.get("java.util.function.Function"))
C(fn, "public MobLevelFn() { }")
M(fn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    String w = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (a.length >= 2 && a[1] instanceof java.util.UUID) { u = (java.util.UUID) a[1]; w = a[0] == null ? null : String.valueOf(a[0]); }
      else if (a.length == 1 && a[0] instanceof java.util.UUID) u = (java.util.UUID) a[0];
    }
    if (u == null) return Integer.valueOf(-1);
    Object i = @PKG@.MobLevel.MOBS.get(u);
    if (!(i instanceof @PKG@.MobInfo)) return Integer.valueOf(-1);
    @PKG@.MobInfo m = (@PKG@.MobInfo) i;
    if (w != null && m.world != null && !w.equals(m.world)) return Integer.valueOf(-1);
    return Integer.valueOf(m.level);
  } catch (Throwable t) { return Integer.valueOf(-1); }
}""")

# ---------------------------------------------------------------- 0.1.4 mob:fn:info (bridge, any thread, never throws; spec 7.3)
# Object[]{String world, UUID npc} (or a bare UUID) -> Object[]{ Integer level, Double base, Double xpBase, Double hpMult, Double dmgMult,
# Double xpMult } or null (no level / unknown / wrong world / base unknown). base = the mob's own max health before our multiplier;
# xpBase = max(base, health floor) = its Lv 1 health; hpMult = the level health multiplier now (no floor factor) x the scale.role
# Health x; dmgMult = the damage multiplier now; xpMult = min(1, hpMult WITHOUT the scale.role factor / hardRef(level)) - Hard = 1,
# Easy / Normal keep their share, Custom never pays more than Hard. Reads MOBS (the entry stays until the entity is removed, so it still
# answers at the DeathComponent, as mob:fn:level).
ifn.addInterface(pool.get("java.util.function.Function"))
C(ifn, "public MobInfoFn() { }")
M(ifn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    String w = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o instanceof Object[]) {
      Object[] a = (Object[]) o;
      if (a.length >= 2 && a[1] instanceof java.util.UUID) { u = (java.util.UUID) a[1]; w = a[0] == null ? null : String.valueOf(a[0]); }
      else if (a.length == 1 && a[0] instanceof java.util.UUID) u = (java.util.UUID) a[0];
    }
    if (u == null) return null;
    Object i = @PKG@.MobLevel.MOBS.get(u);
    if (!(i instanceof @PKG@.MobInfo)) return null;
    @PKG@.MobInfo m = (@PKG@.MobInfo) i;
    if (w != null && m.world != null && !w.equals(m.world)) return null;
    int level = m.level;
    double base = m.base;
    if (level <= 0 || !(base > 0.0)) return null;
    int fl = @PKG@.MobCfg.HP_FLOOR;
    double xb = (fl > 0 && (double) fl > base) ? (double) fl : base;
    double hm = (double) @PKG@.MobCfg.hpMult(level);
    double rx = m.rx > 0.0 ? m.rx : 1.0;
    double hard = @PKG@.MobCfg.hardRef(level);
    double xm = hard > 0.0 ? hm / hard : 1.0;
    if (xm > 1.0) xm = 1.0;
    return new Object[] { Integer.valueOf(level), Double.valueOf(base), Double.valueOf(xb), Double.valueOf(hm * rx),
                          Double.valueOf((double) @PKG@.MobCfg.dmgMult(level)), Double.valueOf(xm) };
  } catch (Throwable t) { return null; }
}""")

# ---------------------------------------------------------------- MobPlateStep: /mobs platetest (scheduler thread -> world thread, 3 s steps)
ps.addInterface(pool.get("java.lang.Runnable"))
# RUNNING: uuid -> Long start time of the plate test running on that mob (review F11: two tests at once on one mob could restore a test
# text as its plate); a claim older than 30 s is stale (the world stopped mid-test) and may be taken over
F(ps, "public static final java.util.concurrent.ConcurrentHashMap RUNNING = new java.util.concurrent.ConcurrentHashMap();")
for f in ("public @WLD@ world;", "public java.util.UUID uuid;", "public String[] texts;", "public int idx;", "public boolean onWorld;",
          "public @PR@ pr;", "public String orig;", "public String label;"):
    F(ps, f)
C(ps, r"""
public MobPlateStep(@WLD@ world, java.util.UUID uuid, String[] texts, @PR@ pr, String orig, String label) {
  this.world = world; this.uuid = uuid; this.texts = texts; this.pr = pr; this.orig = orig; this.label = label;
  this.idx = 0; this.onWorld = false;
}""")
M(ps, r"""
public static boolean claim(java.util.UUID u, long now) {
  if (u == null) return false;
  Long mine = Long.valueOf(now);
  Object prev = RUNNING.putIfAbsent(u, mine);
  if (prev == null) return true;
  if (prev instanceof Long && now - ((Long) prev).longValue() < 30000L) return false;
  return RUNNING.replace(u, prev, mine);
}""")
M(ps, r"""
public void say(String text) {
  try { if (this.pr != null) this.pr.sendMessage(@MSG@.raw(text).color("%s")); } catch (Throwable t) { }
}""" % SUI.STATUS["="])
# the plate put back: a levelled mob gets its CURRENT level plate (a /mobs set or a format change during the test), else the old plate
M(ps, r"""
public void run() {
  boolean done = true;
  try {
    if (!this.onWorld) { this.onWorld = true; this.world.execute(this); done = false; return; }
    this.onWorld = false;
    @EST@ es = this.world.getEntityStore();
    @REF@ r = es == null ? null : es.getRefFromUUID(this.uuid);
    @ST@ st = es == null ? null : es.getStore();
    if (r == null || !r.isValid() || st == null) { say("[Mobs] Plate test stopped: the mob is gone (died or unloaded)."); return; }
    if (this.idx < this.texts.length) {
      @PKG@.MobLevel.setPlate(null, st, r, this.texts[this.idx]);
      this.idx++;
      @HSV@.SCHEDULED_EXECUTOR.schedule(this, 3L, java.util.concurrent.TimeUnit.SECONDS);
      done = false;
      return;
    }
    Object o = @PKG@.MobLevel.MOBS.get(this.uuid);
    if (o instanceof @PKG@.MobInfo && !"off".equals(@PKG@.MobCfg.PLATE_MODE))
      @PKG@.MobLevel.setPlate(null, st, r, @PKG@.MobLevel.plateText(((@PKG@.MobInfo) o).level, ((@PKG@.MobInfo) o).name));
    else if (this.orig != null) @PKG@.MobLevel.setPlate(null, st, r, this.orig);
    else @PKG@.MobLevel.dropPlate(null, st, r, false);
    say("[Mobs] Plate test done on " + this.label + " - its nameplate is back.");
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("platetest", "plate test failed: " + t); }
  finally { if (done && this.uuid != null) RUNNING.remove(this.uuid); }
}""")

# ---------------------------------------------------------------- MobScanTask: one WARN when another mob-scaling plugin runs (plan risk 3)
SCALERS = ["com.ziggfreed.mmomobscaling.MobScalingPlugin", "com.airijko.endlessleveling.EndlessLeveling",
           "org.zuxaw.plugin.RPGLevelingPlugin", "com.zbeve.endlesselitemobs.EndlessEliteMobs", "com.pedrijoe.difficulty.Difficulty"]
sc.addInterface(pool.get("java.lang.Runnable"))
C(sc, "public MobScanTask() { }")
# 0.1.4: the shape vs SkyyGear's weapon curve F (gear:fn:curve: Object[]{"F", Integer level} -> Double). null = fine; else the WARN text
M(sc, r"""
public static String curveWarn() {
  double f20 = -1.0, f40 = -1.0;
  boolean have = false;
  try {
    Object f = @PKG@.MobLevel.bridge().get("gear:fn:curve");
    if (f instanceof java.util.function.Function) {
      have = true;
      Object a = ((java.util.function.Function) f).apply(new Object[] { "F", Integer.valueOf(20) });
      Object b = ((java.util.function.Function) f).apply(new Object[] { "F", Integer.valueOf(40) });
      if (a instanceof Number) f20 = ((Number) a).doubleValue();
      if (b instanceof Number) f40 = ((Number) b).doubleValue();
    }
  } catch (Throwable t) { }
  boolean steep = f20 > 0.0 && f40 >= 2.0 * f20;
  String fx = "F(40) " + @PKG@.MobCfg.num2(f40) + " vs F(20) " + @PKG@.MobCfg.num2(f20);
  if (@PKG@.MobCfg.CURVE_ON && !steep)
    return "Strength shape is Level curve, but " + (have ? "SkyyGear's weapon curve is flat (" + fx + ", less than 2x)" : "SkyyGear's gear:fn:curve is missing (SkyyGear 0.2.5+ not running)")
        + ": mobs above Lv 20 will out-grow players' gear - install SkyyGear 0.2.5+ or set Server Setup -> Mobs -> Strength -> Strength shape to Per level";
  if (!@PKG@.MobCfg.CURVE_ON && steep)
    return "Strength shape is Per level, but SkyyGear's weapon curve is steep (" + fx + ", 2x or more): players' gear out-grows the mobs - set Server Setup -> Mobs -> Strength -> Strength shape to Level curve";
  return null;
}""")
M(sc, r"""
public void run() {
  try {
    String cw = curveWarn();
    if (cw != null) @PKG@.MobLog.warn(cw);
  } catch (Throwable t0) { }
  try {
    String[] known = new String[] { %s };
    java.util.List ps = @PMGR@.get().getPlugins();
    for (int i = 0; ps != null && i < ps.size(); i++) {
      Object p = ps.get(i);
      String cn = p == null ? "" : p.getClass().getName();
      for (int k = 0; k < known.length; k++) {
        if (known[k].equals(cn)) @PKG@.MobLog.warn("another mob scaling mod is running (" + cn + "): mob health / damage multipliers stack and nameplates fight - keep one of them");
      }
    }
  } catch (Throwable t) { }
}""" % ", ".join(jstr(s) for s in SCALERS))

# ---------------------------------------------------------------- MobPruneTask (review F6): every 5 minutes on the scheduler thread
# world == null: forget the mobs of removed worlds, then hand each loaded world with levelled mobs a world-thread check (world set)
pt.addInterface(pool.get("java.lang.Runnable"))
F(pt, "public @WLD@ world;")
C(pt, "public MobPruneTask(@WLD@ world) { this.world = world; }")
M(pt, r"""
public void run() {
  try {
    long now = System.currentTimeMillis();
    if (this.world != null) {
      int k = @PKG@.MobLevel.pruneWorld(this.world, now);
      if (k > 0) @PKG@.MobLog.info("forgot " + k + " levelled mobs that are gone from world " + this.world.getName());
      return;
    }
    java.util.ArrayList live = @PKG@.MobLevel.liveWorlds();
    if (live == null) return;
    int n = @PKG@.MobLevel.pruneWith(live, @PKG@.MobLevel.namesOf(live), now);
    if (n > 0) @PKG@.MobLog.info("forgot " + n + " levelled mobs of worlds that were removed");
    for (int i = 0; i < live.size(); i++) {
      Object o = live.get(i);
      if (o instanceof @WLD@ && @PKG@.MobLevel.hasMobsIn(o)) ((@WLD@) o).execute(new @PKG@.MobPruneTask((@WLD@) o));
    }
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("prune", "the prune of gone mobs failed: " + t); }
}""")

# ---------------------------------------------------------------- MobRefresh (0.1.2): the live health re-apply
# world == null (MobCfg.ON_HEALTH, run by derive when the health signature changes, on whatever thread changed the setting): no
# component is touched there - every loaded world that holds levelled mobs gets ONE MobRefresh(world) on its own task queue
# (World.execute). world set (on that world's thread): MobLevel.refreshWorld. RUNS counts the dispatches (the harness reads it).
rf.addInterface(pool.get("java.lang.Runnable"))
F(rf, "public @WLD@ world;")
F(rf, "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();")
C(rf, "public MobRefresh(@WLD@ world) { this.world = world; }")
M(rf, r"""
public static int dispatch(java.util.Collection worlds) {
  if (worlds == null || @PKG@.MobLevel.MOBS.isEmpty()) return 0;
  int n = 0;
  java.util.Iterator it = worlds.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @WLD@) || !@PKG@.MobLevel.hasMobsIn(o)) continue;
    try { ((@WLD@) o).execute(new @PKG@.MobRefresh((@WLD@) o)); n++; }
    catch (Throwable t) { @PKG@.MobLog.warnOnce("refreshq:" + t.getClass().getName(), "could not queue the health re-apply on a world (" + t + ") - its mobs get it when their chunks reload"); }
  }
  return n;
}""")
M(rf, r"""
public void run() {
  try {
    if (this.world == null) {
      RUNS.incrementAndGet();
      dispatch(@PKG@.MobLevel.liveWorlds());
      return;
    }
    int n = @PKG@.MobLevel.refreshWorld(this.world);
    if (n > 0) @PKG@.MobLog.info("re-applied the health of " + n + " loaded levelled mobs in world " + this.world.getName() + " (" + @PKG@.MobCfg.difficultyText() + ", health cap x" + (Math.round(@PKG@.MobCfg.HP_CAP * 100.0) / 100.0) + ", health floor " + (@PKG@.MobCfg.HP_FLOOR > 0 ? @PKG@.MobCfg.HP_FLOOR + " HP" : "off") + "; each kept its health percent)");
  } catch (Throwable t) { @PKG@.MobLog.warnOnce("refresh", "the health re-apply failed: " + t); }
}""")

# ---------------------------------------------------------------- MobHooks: config kit check= hooks
M(mh, r"""
public static String checkFormat(String key, String value) {
  if (value == null) return null;
  if (value.indexOf("{level}") < 0) return "The nameplate text must hold {level}.";
  if (value.trim().length() == 0) return "The nameplate text cannot be empty.";
  return null;
}""")
M(mh, r"""
public static String checkColor(String key, String value) {
  int i = key == null ? -1 : key.indexOf('[');
  String e = (i >= 0 && key.endsWith("]")) ? key.substring(i + 1, key.length() - 1) : "";
  try { int lvl = Integer.parseInt(e.trim()); if (lvl < 1 || lvl > 1000) return "The entry must be a level from 1 to 1000."; }
  catch (Throwable t) { return "The entry must be the lowest level of the band, like 20."; }
  if (value == null) return null;
  if (!value.trim().toLowerCase().matches("#[0-9a-f]{6}")) return "The colour must look like #ff6b6b.";
  return null;
}""")
# 0.1.4: a curve table entry = a whole level 0-100, factor 0.1-1000; the last entry of a table cannot be removed (an empty table would
# fall back to its defaults - change the factor instead). key = curve.<hp|dmg>.<difficulty>[<level>], value null = a removal
M(mh, r"""
public static String checkCurvePoint(String key, String value) {
  int i = key == null ? -1 : key.indexOf('[');
  String e = (i >= 0 && key.endsWith("]")) ? key.substring(i + 1, key.length() - 1).trim() : "";
  int lv;
  try { lv = Integer.parseInt(e); } catch (Throwable t) { return "The entry must be a level from 0 to 100 (a whole number), like 40."; }
  if (lv < 0 || lv > 100) return "The entry must be a level from 0 to 100.";
  if (value == null) {
    String tk = i >= 0 ? key.substring(0, i) : "";
    for (int k = 0; k < @PKG@.MobCfg.CURVE_KEY.length; k++) {
      if (!@PKG@.MobCfg.CURVE_KEY[k].equals(tk)) continue;
      double[] ls = (double[]) @PKG@.MobCfg.curveOf(k)[0];
      if (ls.length <= 1) return "A curve needs at least one entry - change its factor instead.";
    }
    return null;
  }
  try {
    double f = Double.parseDouble(value.trim());
    if (Double.isNaN(f) || f < 0.1 || f > 1000.0) return "The factor must be from 0.1 to 1000.";
  } catch (Throwable t) { return "The factor must be a number from 0.1 to 1000."; }
  return null;
}""")
# 0.1.4: scale.role value = <level 0-100>|<health x 0.1-100> (level 0 = the row is off)
M(mh, r"""
public static String checkScaleRole(String key, String value) {
  if (value == null) return null;
  String[] p = value.split("\\|");
  try {
    int l = Integer.parseInt(p[0].trim());
    if (l < 0 || l > 100) return "Level must be from 0 to 100 (0 = off).";
    if (p.length > 1 && p[1].trim().length() > 0) {
      double x = Double.parseDouble(p[1].trim());
      if (Double.isNaN(x) || x < 0.1 || x > 100.0) return "Health x must be from 0.1 to 100.";
    }
  } catch (Throwable t) { return "Type a whole level (0-100) and a Health x (0.1-100)."; }
  return null;
}""")
M(mh, r"""
public static String checkBand(String key, String value) {
  if (value == null) return null;
  String[] p = value.split("\\|");
  try {
    int a = Integer.parseInt(p[0].trim()), b = p.length > 1 ? Integer.parseInt(p[1].trim()) : a;
    if (a > b) return "Min must not be above Max.";
    if (a == 0 && b != 0) return "Use 0-0 for no levels, or a Min of 1 or more.";
  } catch (Throwable t) { return "Type whole numbers."; }
  return null;
}""")

# ---------------------------------------------------------------- MobMig (0.1.1): the one-time difficulty update of an existing config.properties
# setup() only, BEFORE MobCfg.load and CfgPub.start. The SkyySkills 0.4.11 HealMig machinery method for method (reviewed + live; SkyyCollections
# 0.2.5 CollBypassMig is the same): the pure text step mgUpdate on the config kit's own parser (CfgFile.isComment / key / value / end /
# valStart), a Properties check (only the moved caps may differ), CfgHist.snapshot + mgSaved (no rewrite unless config-history really holds
# the old bytes), CfgRows.atomicWrite, one config-changes.log line per moved cap (Server Setup -> Changes -> Undo), INFO lines (the change,
# what the chosen difficulty means now, one per kept admin value). Plain java.* + the kit's classes: a bare JVM runs it on scratch copies.
def _jarr(xs):
    for x in xs:
        assert all(32 <= ord(c) < 127 for c in x) and '"' not in x and "\\" not in x and "@" not in x, x
    return "new String[] { " + ", ".join('"' + x + '"' for x in xs) + " }"


def _diff_now(d):
    """what a kept difficulty word means in 0.1.1 (the update's INFO line; Skyy's live file is on hard)"""
    if d not in PRESETS:
        return "Custom keeps your own strength.hp / strength.dmg values (unchanged)"
    h, m = PRESETS[d]
    was = [k for k in sorted(PRESETS_01) if PRESETS_01[k] == PRESETS[d]]
    moved = [k for k in sorted(PRESETS) if PRESETS[k] == PRESETS_01[d]]
    s = "%s is now %s%% health / %s%% damage per level (%s" % (d.capitalize(), num(h), num(m), ("= 0.1's " + was[0].capitalize()) if was else "new")
    if moved:
        return s + "; 0.1's %s is %s now)" % (d.capitalize(), moved[0].capitalize())
    return s + "; 0.1's %s was %s%% / %s%%)" % (d.capitalize(), num(PRESETS_01[d][0]), num(PRESETS_01[d][1]))


DIFF_WORDS = ["easy", "normal", "hard", "custom"]
DIFF_NOW = [_diff_now(d) for d in DIFF_WORDS]
assert DIFF_NOW[2] == "Hard is now 8% health / 4% damage per level (new; 0.1's Hard is Normal now)", DIFF_NOW
assert DIFF_NOW[1] == "Normal is now 6% health / 3% damage per level (= 0.1's Hard; 0.1's Normal is Easy now)", DIFF_NOW
for _d in ("public static final String[] MG_KEY = %s;" % _jarr([t[0] for t in MG_ROWS]),
           "public static final String[] MG_OLD = %s;" % _jarr([t[1] for t in MG_ROWS]),
           "public static final String[] MG_NEW = %s;" % _jarr([t[2] for t in MG_ROWS]),
           "public static final String[] MG_WHY = %s;" % _jarr([t[3] for t in MG_ROWS]),
           "public static final String DOC_OLD = %s;" % jstr(DOC_OLD),
           "public static final String DOC_NEW = %s;" % jstr(DOC_NEW),
           "public static final String MG_MARK = %s;" % jstr(MG_MARK),
           "public static final String MG_MARK_ID = %s;" % jstr(MG_MARK_ID),
           "public static final String MG_WHO = %s;" % jstr(MG_WHO),
           'public static final String ANCHOR = "strength.difficulty";',
           'public static final String DIFF_DEFAULT = "@DIFDEF@";',
           "public static final String[] DIFF_WORD = %s;" % _jarr(DIFF_WORDS),
           "public static final String[] DIFF_NOW = %s;" % _jarr(DIFF_NOW)):
    F(mm, _d)
M(mm, r"""
public static int mgIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < MG_KEY.length; i++) if (MG_KEY[i].equals(k)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line
# (nothing to do). Else { new text, "strength.hpCap 5 -> 6, ..." or "", String[] kept notes, String[] { key, old, new }*, Integer docs }.
# A cap whose LAST live line (the one Properties keeps) is a one-line entry holding exactly 0.1's default text is moved: every one-line
# entry of it holding that text gets the 0.1.1 value (value text only: key, separator and CR stay). Anything else is kept: an admin's
# value (noted unless it already is the 0.1.1 default), a continued entry (noted), a missing line (silent: the code default is 0.1.1's).
# A comment line that is exactly DOC_OLD becomes DOC_NEW (CR kept). Marker: on its own line above the first strength.difficulty / cap
# entry - above the whole run of comment lines directly on top of it - else above line 0. Lines are scanned from the start of a logical
# line, so a continued entry's tail is never taken for a comment. Never throws for any text.
M(mm, r"""
public static Object[] mgUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MG_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MG_MARK_ID) >= 0) return null;
      if (s.trim().length() == 0) run = -1;
      else if (run < 0) run = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int m = mgIdx(key);
    if (first < 0 && (m >= 0 || ANCHOR.equals(key))) { first = k; above = run >= 0 ? run : k; }
    if (m >= 0) {
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    run = -1;
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && eff[i].equals(MG_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(MG_KEY[i]).append(' ').append(MG_OLD[i]).append(" -> ").append(MG_NEW[i]);
      rows.add(MG_KEY[i]);
      rows.add(MG_OLD[i]);
      rows.add(MG_NEW[i]);
    } else if (multi[i] || !eff[i].equals(MG_NEW[i])) {
      kept.add(MG_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (an admin's value) - the 0.1.1 default is " + MG_NEW[i] + " (" + MG_WHY[i] + "); Server Setup -> Mobs -> Strength");
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  int docs = 0;
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      if (s2.equals(DOC_OLD)) {
        out.add(DOC_NEW + (raw[k].endsWith("\r") ? "\r" : ""));
        docs++;
      } else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = mgIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(MG_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + MG_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = first >= 0 ? above : 0;
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MG_MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MG_MARK.length() + 256);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]), Integer.valueOf(docs) };
}""")
# the update may change nothing but the moved caps' values: both texts as java.util.Properties - same keys, same values, the moved keys
# exactly their new value (a marker / comment line can never change a value; this guards the parser corner cases)
M(mm, r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] rows) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (a.size() != b.size()) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String want = a.getProperty(k);
      for (int i = 0; i + 2 < rows.length; i += 3) if (rows[i].equals(k)) want = rows[i + 2];
      String got = b.getProperty(k);
      if (got == null || !got.equals(want)) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""")
M(mm, r"""
public static int fileIdx() {
  for (int k = 0; k < @PKG@.CfgRows.FILES.length; k++) if (@PKG@.CfgRows.FILES[k].endsWith("/config.properties")) return k;
  return -1;
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyMobs)
M(mm, r"""
public static void mgKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.MobLog.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds a copy with exactly these
# bytes (the new copy, or the newest one when snapshot skipped an equal file) - the copies themselves, not index.log
M(mm, r"""
public static boolean mgSaved(int f, byte[] old) {
  String[] have = @PKG@.CfgHist.list(f);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(f, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
M(mm, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + MG_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# what the chosen difficulty word means now (the word itself is never changed: Skyy 2026-10-02, a server on hard gets the new hard);
# a missing / unknown word = the loader's default word
M(mm, r"""
public static String diffNote(byte[] data) {
  String w = null;
  try {
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(data));
    w = p.getProperty("strength.difficulty");
  } catch (Throwable t) { w = null; }
  String d = w == null ? "" : w.trim().toLowerCase();
  int i = -1;
  for (int k = 0; k < DIFF_WORD.length; k++) if (DIFF_WORD[k].equals(d)) i = k;
  if (i < 0) { d = DIFF_DEFAULT; for (int k = 0; k < DIFF_WORD.length; k++) if (DIFF_WORD[k].equals(d)) i = k; }
  if (i < 0) return "";
  return "Difficulty kept (" + d + (w == null ? ", the default" : "") + "): " + DIFF_NOW[i] + " - Server Setup -> Mobs -> Strength -> Difficulty";
}""")
# setup(): the file before this update becomes a History version (KEEP 10, verified by mgSaved before the rewrite), the new text is
# written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line per moved cap, INFO lines (the change, the difficulty note,
# one per kept value). Returns the INFO lines joined by \n ("" = nothing done: no file - MobCfg.load writes the 0.1.1 default with the
# marker -, marker already there, or a failure - WARN, file untouched, retried at the next start)
M(mm, r"""
public static synchronized String run(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] rows = (String[]) r[3];
    if (!sameAfter(old, data, rows)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.1 difficulty ladder: the update would change more than the cap lines (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = fileIdx();
    if (fi < 0) return "";
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), MG_WHO, "before the 0.1.1 difficulty update");
    if (!mgSaved(fi, old)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.1 difficulty ladder: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    int docs = ((Integer) r[4]).intValue();
    String dt = docs > 0 ? "; the 0.1 difficulty comment line updated" : "";
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated for the 0.1.1 difficulty ladder (Easy / Normal / Hard = 4 / 6 / 8% health, 2 / 3 / 4% damage per level): " + chg + dt + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no cap line still had its 0.1 default - no value changed" + dt + " (0.1.1 difficulty update marker added; the old file is in config-history)";
    @PKG@.MobLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    String dn = diffNote(data);
    if (dn.length() > 0) { @PKG@.MobLog.info(dn); all.append('\n').append(dn); }
    for (int i = 0; i < kept.length; i++) { @PKG@.MobLog.info(kept[i]); all.append('\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not update config.properties for the 0.1.1 difficulty ladder (the file is used as it is): " + t);
    return "";
  }
}""")
assert "4 / 6 / 8% health, 2 / 3 / 4% damage" in "Easy / Normal / Hard = %s / %s / %s%% health, %s / %s / %s%% damage" % (
    num(PRESETS["easy"][0]), num(PRESETS["normal"][0]), num(PRESETS["hard"][0]), num(PRESETS["easy"][1]), num(PRESETS["normal"][1]),
    num(PRESETS["hard"][1])), "MobMig.run's INFO line names the ladder - keep it in step with PRESETS"

# ---------------------------------------------------------------- MobMig14 (0.1.4): the one-time level curve update of config.properties
# Spec 6.4 + PROJECT-RULES 4 (only new lines are added - no existing value changes; a verified History copy first; one change-log line
# with Undo; a run-once marker; every other byte and the line endings kept). setup() runs it after MobMig.run and BEFORE MobCfg.load.
#  1. a file whose comment lines hold MG14_MARK_ID is never touched again (the fresh default file carries the marker);
#  2. right after the LAST strength.* entry: the marker + the groups of mg14_groups (strength.shape, strength.dmgFloor, strength.hitCap, the 8
#     curve tables with their default points, the 6 gap rows), each with its comment line; a group whose key (any case) / any key of its
#     family is already in the file is left out and named in the INFO line (no strength.* entry at all: at the end of the file);
#  3. after the levels.max entry: the scale.role comment line (no entries; without levels.max it ends the block);
#  4. strength.shape (decision table): Difficulty custom -> linear (the owner's own %, no log line); easy / normal / hard / missing /
#     unknown -> curve + ONE config-changes.log line "strength.shape linear -> curve" (who SkyyMobs 0.1.4, via update), so Server Setup
#     -> Changes -> Undo puts back 0.1.3's numbers; a strength.shape already in the file is kept;
#  5. never touched: strength.difficulty / hp / dmg, both caps (hand-set caps are named: inert in curve shape), strength.floor, bands, plates.
# The new text must parse (java.util.Properties) to every old key with its old value + exactly the added keys with their values;
# CfgHist.snapshot keeps the old file ("before the 0.1.4 level curve") and the rewrite only happens once config-history really holds those
# bytes (MobMig.mgSaved); CfgRows.atomicWrite. Line endings: the new lines take the CR of the line they follow (a file ending without a
# newline in a CRLF file gets that CR on its old last line, so it stays all CRLF). Plain java.* + the kit: a bare JVM runs it on copies.
_G14 = mg14_groups("{shape}")
for _d in ("public static final String MARK = %s;" % jstr(MG14_MARK),
           "public static final String MARK_ID = %s;" % jstr(MG14_MARK_ID),
           "public static final String WHO = %s;" % jstr(MG14_WHO),
           "public static final String WHAT = %s;" % jstr(MG14_WHAT),
           "public static final String ROLE_DOC = %s;" % jstr(ROLE_DOC),
           "public static final String[] G_KEY = new String[] { %s };" % ", ".join(jstr(k) for k, _l in _G14),
           "public static final String[] G_TEXT = new String[] { %s };" % ", ".join(jtext("\n".join(l)) for _k, l in _G14),
           'public static final String CAP_HP = "%s";' % num(CAPS[0]), 'public static final String CAP_DMG = "%s";' % num(CAPS[1])):
    F(m14, _d)
# insert lines right after out[x] (x = -1: at the top). They take the CR of out[x]; after an unterminated last line (a file without a final
# newline) they go to the end, that old last line gets the file's CR (CRLF files) and the new last line ends the file without a newline
M(m14, r"""
public static void insertAfter(java.util.ArrayList out, int x, java.util.ArrayList lines, boolean crlf) {
  int n = out.size();
  boolean atEnd = x >= 0 && x == n - 1;
  String cr;
  if (x < 0) cr = crlf ? "\r" : "";
  else if (atEnd) {
    cr = crlf ? "\r" : "";
    String last = (String) out.get(x);
    if (crlf && !last.endsWith("\r")) out.set(x, last + "\r");
  } else cr = ((String) out.get(x)).endsWith("\r") ? "\r" : "";
  for (int i = lines.size() - 1; i >= 0; i--) {
    String ln = (String) lines.get(i);
    out.add(x + 1, ln + ((atEnd && i == lines.size() - 1) ? "" : cr));
  }
}""")
# FIXER 2 (2026-10-06, recheck finding 1): an anchor entry that reaches the file's LAST line still open (its last line ends in an odd
# number of backslashes, or it swallowed the final newline - the empty tail is its continuation) would take appended lines as its
# continuation (sameAfter caught it: "NOT updated" on every start). Such an anchor puts the new lines BEFORE the entry's first line (the
# SkyyGear chAfter / chEnd rule); with no strength.* entry the same holds for the file's last entry. openEnd: the last line is open.
M(m14, r"""
public static boolean openEnd(java.util.ArrayList l) {
  if (l.size() == 0) return false;
  String le = (String) l.get(l.size() - 1);
  return le.length() == 0 || @PKG@.CfgFile.cont(le);
}""")
# the insertAfter index for the anchor entry s..e (its last line, or the line before its first line when it reaches the end still open)
M(m14, r"""
public static int atAfter(java.util.ArrayList l, int s, int e) {
  if (e == l.size() - 1 && openEnd(l)) return s - 1;
  return e;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = the marker is already in a comment line.
# Else { new text, String shape added ("curve" / "linear", null = kept), String[] notes, String[] added keys, String[] added values,
# String[] { hpCap, dmgCap } (the file's effective values, null = no line) }. Never throws for any text.
M(m14, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  java.util.HashSet keys = new java.util.HashSet();
  int lastStr = -1, lvMax = -1, lastStrS = -1, lvMaxS = -1, tail = -1;
  boolean roleDoc = false;
  String diff = null, hpCap = null, dmgCap = null;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.equals(ROLE_DOC)) roleDoc = true;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null && key.length() > 0) {
      String lk = key.toLowerCase();
      keys.add(lk);
      if (lk.startsWith("strength.")) { lastStr = e; lastStrS = k; }
      if (lk.equals("levels.max")) { lvMax = e; lvMaxS = k; }
      if (key.equals("strength.difficulty")) diff = @PKG@.CfgFile.value(l, k).trim();
      if (key.equals("strength.hpCap")) hpCap = @PKG@.CfgFile.value(l, k).trim();
      if (key.equals("strength.dmgCap")) dmgCap = @PKG@.CfgFile.value(l, k).trim();
    }
    k = e + 1;
  }
  String shape = null;
  if (!keys.contains("strength.shape")) {
    String d = diff == null ? "" : diff.trim().toLowerCase();
    shape = d.equals("custom") ? "linear" : "curve";
  }
  java.util.ArrayList block = new java.util.ArrayList();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList ak = new java.util.ArrayList();
  java.util.ArrayList av = new java.util.ArrayList();
  block.add(MARK);
  for (int g = 0; g < G_KEY.length; g++) {
    String gk = G_KEY[g].toLowerCase();
    boolean fam = gk.endsWith(".");
    boolean have = false;
    java.util.Iterator it = keys.iterator();
    while (it.hasNext()) {
      String x = (String) it.next();
      if (fam ? x.startsWith(gk) : x.equals(gk)) { have = true; break; }
    }
    if (have) { notes.add((fam ? G_KEY[g] + "* lines" : G_KEY[g]) + " kept (already in the file)"); continue; }
    String[] ls = G_TEXT[g].replace("{shape}", shape == null ? "curve" : shape).split("\n");
    for (int q = 0; q < ls.length; q++) {
      block.add(ls[q]);
      if (ls[q].startsWith("#")) continue;
      int eq = ls[q].indexOf('=');
      ak.add(ls[q].substring(0, eq));
      av.add(ls[q].substring(eq + 1));
    }
  }
  boolean roleHere = !roleDoc && lvMax < 0;
  if (roleHere) block.add(ROLE_DOC);
  boolean crlf = text.indexOf("\r\n") >= 0;
  int n0 = raw.length;
  boolean endNl = n0 > 0 && raw[n0 - 1].length() == 0;
  int xb = lastStr >= 0 ? atAfter(l, lastStrS, lastStr) : ((tail >= 0 && openEnd(l)) ? tail - 1 : (endNl ? n0 - 1 : n0) - 1);
  int xr = lvMax >= 0 ? atAfter(l, lvMaxS, lvMax) : -1;
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < n0; i++) out.add(raw[i]);
  java.util.ArrayList rd = new java.util.ArrayList();
  rd.add(ROLE_DOC);
  boolean roleAfter = !roleDoc && lvMax >= 0;
  if (roleAfter && xr > xb) insertAfter(out, xr, rd, crlf);
  insertAfter(out, xb, block, crlf);
  if (roleAfter && xr <= xb) insertAfter(out, xr, rd, crlf);
  StringBuilder sb = new StringBuilder(text.length() + 8192);
  for (int i = 0; i < out.size(); i++) {
    if (i > 0) sb.append('\n');
    sb.append((String) out.get(i));
  }
  return new Object[] { sb.toString(), shape, (String[]) notes.toArray(new String[0]), (String[]) ak.toArray(new String[0]),
                        (String[]) av.toArray(new String[0]), new String[] { hpCap, dmgCap } };
}""")
# every old key keeps its old value, exactly the added keys are new, each with its value (a marker / comment line can never change a value)
M(m14, r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] ak, String[] av) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties b = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    b.load(new java.io.ByteArrayInputStream(nb));
    if (b.size() != a.size() + ak.length) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!a.getProperty(k).equals(b.getProperty(k))) return false;
    }
    for (int i = 0; i < ak.length; i++) {
      if (a.getProperty(ak[i]) != null || !av[i].equals(b.getProperty(ak[i]))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}""")
M(m14, r"""
public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(): returns the INFO lines joined by \n ("" = nothing done: no file - MobCfg.load writes the 0.1.4 default with the marker -,
# marker already there, or a failure: WARN, file untouched, retried at the next start)
M(m14, r"""
public static synchronized String run(java.nio.file.Path dir) {
  if (dir == null) return "";
  java.nio.file.Path f = dir.resolve("config.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String shape = (String) r[1];
    String[] notes = (String[]) r[2];
    String[] ak = (String[]) r[3];
    String[] av = (String[]) r[4];
    String[] caps = (String[]) r[5];
    if (!sameAfter(old, data, ak, av)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.4 level curve: the update would change more than the new lines (the file is used as it is - Strength shape " + @PKG@.MobCfg.shapeFor(null) + " from the code; the next start tries again)");
      return "";
    }
    int fi = @PKG@.MobMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.MobMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, WHAT);
    if (!@PKG@.MobMig.mgSaved(fi, old)) {
      @PKG@.MobLog.warn("config.properties NOT updated for the 0.1.4 level curve: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    if ("curve".equals(shape)) {
      @PKG@.CfgLog.enqueue(mgLog("strength.shape", "linear", "curve"));
      @PKG@.CfgLog.flush();
    }
    String msg = "config.properties updated for the 0.1.4 level curve: " + ak.length + " new lines (Strength shape, damage floor 0, one hit at most 0, the 8 Level curve tables, the Level gap rows)";
    if ("curve".equals(shape)) msg = msg + "; strength.shape=curve - same-level fights play like before, mobs above Lv 20 grow with the gear (Server Setup -> Changes can undo it: Per level = 0.1.3's numbers)";
    else if ("linear".equals(shape)) msg = msg + "; strength.shape=linear - Difficulty Custom keeps your own % per level (set Strength shape to Level curve for the new curve)";
    msg = msg + " (the old file is in config-history)";
    @PKG@.MobLog.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { String n = "level curve update: " + notes[i]; @PKG@.MobLog.info(n); all.append('\n').append(n); }
    boolean hand = (caps[0] != null && !caps[0].equals(CAP_HP)) || (caps[1] != null && !caps[1].equals(CAP_DMG));
    if (hand && !"linear".equals(shape)) {
      String n = "strength.hpCap=" + caps[0] + " / strength.dmgCap=" + caps[1] + " kept (hand-set): unused in Level curve shape - they still cap Per level";
      @PKG@.MobLog.info(n);
      all.append('\n').append(n);
    }
    return all.toString();
  } catch (Throwable t) {
    @PKG@.MobLog.warn("could not update config.properties for the 0.1.4 level curve (the file is used as it is): " + t);
    return "";
  }
}""")

# ---------------------------------------------------------------- MobCmds: the command bodies (world thread: AbstractPlayerCommand runs there)
for _s in SUI.java_status_methods():
    M(mc, _s)
M(mc, r"""
public static void tell(@PR@ p, String res) {
  if (p == null || res == null || res.length() == 0) return;
  try { p.sendMessage(@MSG@.raw(textOf(res)).color(colorOf(res))); } catch (Throwable t) { }
}""")
M(mc, r"""
public static void tellAll(@PR@ p, String[] lines) {
  for (int i = 0; lines != null && i < lines.length; i++) tell(p, lines[i]);
}""")
M(mc, r"""
public static String spaced(String s) { return s == null ? "" : s.replace('_', ' '); }""")
M(mc, r"""
public static String bandText(int a, int b, int bonus) {
  int max = @PKG@.MobCfg.MAX_LEVEL;
  int x = Math.min(a + bonus, max), y = Math.min(b + bonus, max);
  return x == y ? "Lv " + x : "Lv " + x + "-" + y;
}""")
M(mc, r"""
public static String zoneText(String region, String env, String zn) {
  String z = @PKG@.MobLevel.zoneOfRegion(region);
  if (z == null) z = @PKG@.MobLevel.zoneOfEnv(env);
  if (z == null) return null;
  String t = "Zone " + z.substring(4);
  String n = zn == null ? null : @PKG@.MobLevel.i18n("server.map.zone." + zn);
  if (n == null && zn != null) n = spaced(zn);
  return n == null ? t : t + " " + n;
}""")
# where the band comes from, for players
M(mc, r"""
public static String whereText(Object[] r, String wn) {
  String step = (String) r[3];
  if ("world".equals(step)) return "this world's band";
  if ("island".equals(step)) return "private island";
  String region = (String) r[5], biome = (String) r[6], env = (String) r[8], zn = (String) r[9];
  String zt = zoneText(region, env, zn);
  StringBuilder sb = new StringBuilder();
  if (zt != null) sb.append(zt);
  if (region != null) {
    String rn = @PKG@.MobLevel.i18n("server.map.region." + region);
    if (sb.length() > 0) sb.append(" - ");
    sb.append(rn == null ? spaced(region) : rn);
  }
  if ("lava".equals(step)) { if (sb.length() > 0) sb.append(" - "); sb.append("lava cave: the zone's hardest band"); }
  else if (biome != null && region != null) sb.append(" - ").append(spaced(biome));
  if ("env".equals(step) && env != null) { if (sb.length() > 0) sb.append(" - "); sb.append(spaced(env.startsWith("Env_") ? env.substring(4) : env)); }
  int bonus = ((Integer) r[2]).intValue();
  if (bonus != 0 && env != null) sb.append(" - ").append(spaced(env.startsWith("Env_") ? env.substring(4) : env)).append(" +").append(bonus);
  return sb.length() == 0 ? step : sb.toString();
}""")
M(mc, r"""
public static String skillLine(java.util.UUID u, int lo, int hi) {
  try {
    java.util.Map b = @PKG@.MobLevel.bridge();
    Object cs = b.get("class:skill:" + u);
    Object f = b.get("skill:fn:level");
    if (!(cs instanceof String) || ((String) cs).length() == 0 || !(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, cs });
    if (!(r instanceof Number)) return null;
    int l = ((Number) r).intValue();
    if (l < 0) l = 0;
    String s = "=Your " + cs + " is " + l + ": ";
    if (hi < l) { int x = l - hi, y = l - lo; return s + "these mobs are " + (x == y ? x + "" : x + " to " + y) + " levels below you."; }
    String gap = l > 0 ? @PKG@.MobGap.bandText(lo - l, hi - l) : "";
    if (lo > l) { int x = lo - l, y = hi - l; return s + "these mobs are " + (x == y ? x + "" : x + " to " + y) + " levels above you" + gap + "."; }
    return s + "your level is inside this range" + gap + ".";
  } catch (Throwable t) { return null; }
}""")
M(mc, r"""
public static String[] infoLines(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
  if (tc == null || tc.getPosition() == null) return new String[] { "-[Mobs] Could not read where you stand." };
  if (!@PKG@.MobCfg.ON || !@PKG@.MobLevel.HOOK) return new String[] { "=[Mobs] Mob levels are switched off on this server." };
  @VEC@ p = tc.getPosition();
  Object[] r = @PKG@.MobLevel.lookupAt(world, p.x, p.y, p.z, Integer.MIN_VALUE);
  int a = ((Integer) r[0]).intValue(), b = ((Integer) r[1]).intValue(), bonus = ((Integer) r[2]).intValue();
  String wn = world == null ? "" : world.getName();
  if (a <= 0 && b <= 0) return new String[] { "=[Mobs] Mobs here get no level (" + ("world".equals(r[3]) ? "this world has no levels" : "no band for this place") + ")." };
  if (a <= 0) a = 1;
  String first = "=[Mobs] Mobs here: " + bandText(a, b, bonus) + " (" + whereText(r, wn) + ").";
  String second = skillLine(pr.getUuid(), Math.min(a + bonus, @PKG@.MobCfg.MAX_LEVEL), Math.min(b + bonus, @PKG@.MobCfg.MAX_LEVEL));
  return second == null ? new String[] { first } : new String[] { first, second };
}""")
# the mob an admin means: the entity they look at, else the nearest levelled mob within 8 blocks
M(mc, r"""
public static @REF@ target(@ST@ store, @REF@ ref, @WLD@ world) {
  try {
    @REF@ t = @TGT@.getTargetEntity(ref, store);
    if (t != null && t.isValid() && store.getComponent(t, @NPCE@.getComponentType()) != null) return t;
  } catch (Throwable e) { }
  @TC@ me = (@TC@) store.getComponent(ref, @TC@.getComponentType());
  if (me == null || me.getPosition() == null || world == null) return null;
  @VEC@ mp = me.getPosition();
  String wn = world.getName();
  @EST@ es = (@EST@) store.getExternalData();
  @REF@ best = null;
  double bd = 64.0;
  java.util.Iterator it = @PKG@.MobLevel.MOBS.values().iterator();
  while (it.hasNext()) {
    @PKG@.MobInfo i = (@PKG@.MobInfo) it.next();
    if (i == null || !wn.equals(i.world)) continue;
    @REF@ r = es.getRefFromUUID(i.uuid);
    if (r == null || !r.isValid()) continue;
    @TC@ tc = (@TC@) store.getComponent(r, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) continue;
    @VEC@ q = tc.getPosition();
    double dx = q.x - mp.x, dy = q.y - mp.y, dz = q.z - mp.z;
    double d = dx * dx + dy * dy + dz * dz;
    if (d <= bd) { bd = d; best = r; }
  }
  return best;
}""")
M(mc, r"""
public static String f2(float v) {
  String s = String.valueOf(Math.round(v * 100.0f) / 100.0);
  if (s.endsWith(".0")) s = s.substring(0, s.length() - 2);
  return s;
}""")
# 0.1.2: the health line of /mobs inspect - the multiplier ACTUALLY on the mob (its skyymobs_lv<N> modifier), the setting now when it
# differs (Skyy's 0.1.1 test: inspect printed the setting while the mob kept its old max), the base HP and the floor
M(mc, r"""
public static String healthLine(@ESM@ m, int hi, int level, double rx) {
  if (level <= 0) return null;
  @ESV@ hv = m == null ? null : m.get(hi);
  float applied = @PKG@.MobLevel.amountOn(m, hi, @PKG@.MobLevel.keyOf(level));
  double base = @PKG@.MobLevel.baseOf(m, hi);
  float want = @PKG@.MobCfg.hpAmount(level, base, rx);
  double ff = @PKG@.MobCfg.floorFactor(base);
  int fl = @PKG@.MobCfg.HP_FLOOR;
  boolean ok = applied >= 0.0f && @PKG@.MobLevel.same(applied, want);
  StringBuilder sb = new StringBuilder("=Health ");
  if (applied < 0.0f) sb.append("NOT applied (no ").append(@PKG@.MobLevel.keyOf(level)).append(" modifier on the mob; setting x").append(f2(want)).append(" - it gets it on reload or /mobs set)");
  else if (!ok) sb.append("applied x").append(f2(applied)).append(" (setting x").append(f2(want)).append(" - updates on reload or /mobs set)");
  else sb.append("x").append(f2(applied));
  if (hv != null) sb.append(" (").append(Math.round(hv.get())).append(" / ").append(Math.round(hv.getMax())).append(" HP)");
  if (ff > 1.0) {
    if (ok) sb.append(" = level x").append(f2(@PKG@.MobCfg.hpMult(level))).append(" x floor ").append(f2((float) ff)).append(": floor ").append(fl).append(" HP applied (base ").append(Math.round(base)).append(" HP)");
    else sb.append("; the setting = level x").append(f2(@PKG@.MobCfg.hpMult(level))).append(" x floor ").append(f2((float) ff)).append(" (floor ").append(fl).append(" HP, base ").append(Math.round(base)).append(" HP)");
  }
  else if (fl <= 0) sb.append(", floor off");
  else if (base > 0.0) sb.append(", base ").append(Math.round(base)).append(" HP (at or above the ").append(fl).append(" HP floor)");
  if (rx != 1.0 && rx > 0.0) sb.append(", Fixed level by role health x").append(f2((float) rx));
  if (@PKG@.MobCfg.CURVE_ON) sb.append(", damage x").append(f2(@PKG@.MobCfg.dmgMult(level))).append(" - ").append(@PKG@.MobCfg.difficultyText()).append(", Lv ").append(level);
  else sb.append(", damage x").append(f2(@PKG@.MobCfg.dmgMult(level))).append(" - ").append(@PKG@.MobCfg.difficultyText()).append(", caps x").append(f2((float) @PKG@.MobCfg.HP_CAP)).append(" / x").append(f2((float) @PKG@.MobCfg.DMG_CAP));
  return sb.toString();
}""")
M(mc, "public static String healthLine(@ESM@ m, int hi, int level) { return healthLine(m, hi, level, 1.0); }")
# 0.1.4: the level gap of this mob against the admin who looks at it (null = none: part off, no class / level unknown, within the free levels)
M(mc, r"""
public static String gapLine(java.util.UUID u, int level) {
  int g = @PKG@.MobGap.gapOf(level, u, System.currentTimeMillis());
  if (g == Integer.MIN_VALUE || g <= @PKG@.MobCfg.GAP_FREE) return null;
  return "=Level gap vs you +" + g + ": you deal " + @PKG@.MobGap.pctOf(@PKG@.MobGap.dealt(g)) + ", it deals " + @PKG@.MobGap.pctOf(@PKG@.MobGap.taken(g));
}""")
M(mc, r"""
public static String[] inspect(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @REF@ t = target(store, ref, world);
  if (t == null) return new String[] { "-[Mobs] Look at a mob (or stand within 8 blocks of a levelled one), then try again." };
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  if (npc == null) return new String[] { "-[Mobs] That is not a mob." };
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  java.util.UUID u = uc == null ? null : uc.getUuid();
  @ESM@ m = (@ESM@) store.getComponent(t, @ESM@.getComponentType());
  int hi = @DST@.getHealth();
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  int saved = @PKG@.MobLevel.savedLevel(m, hi);
  @PKG@.MobInfo info = u == null ? null : (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(u);
  String att = @PKG@.MobLevel.attitudeOf(null, store, t);
  String no = @PKG@.MobCfg.whyNotRole(att, role);
  java.util.ArrayList L = new java.util.ArrayList();
  int level = info != null ? info.level : saved;
  L.add("=[Mobs] " + name + " (" + role + ") - " + (level > 0 ? "Lv " + level : "no level") + (no == null ? "" : " - gets no level: " + no));
  if (level > 0) L.add("=Saved: " + (saved > 0 ? "on the mob (health modifier " + @PKG@.MobLevel.keyOf(saved) + ")" : "NOT on the mob")
      + (info != null ? "; this run: step " + info.step + (info.key == null ? "" : " " + info.key) : ""));
  Object[] r = @PKG@.MobLevel.lookupMob(world, npc, null, store, t);
  if (r != null) {
    int a = ((Integer) r[0]).intValue(), b = ((Integer) r[1]).intValue(), bonus = ((Integer) r[2]).intValue();
    String band = (a <= 0 && b <= 0) ? "no level" : bandText(Math.max(a, 1), b, bonus) + (bonus != 0 ? " (band " + a + "-" + b + " +" + bonus + ")" : "");
    L.add("=Lookup now: step " + r[3] + " " + r[4] + " -> " + band);
    L.add("=Place: region " + r[5] + ", biome " + r[6] + (r[7] != null && !String.valueOf(r[7]).equals(String.valueOf(r[6])) ? " (land " + r[7] + ")" : "") + ", env " + r[8] + (("1".equals(r[11])) ? ", private island" : "") + ("1".equals(r[10]) ? "" : ", no classic worldgen"));
  }
  if (level > 0) {
    String hl = healthLine(m, hi, level, @PKG@.MobCfg.roleX(role));
    if (hl != null) L.add(hl);
    String gl = gapLine(pr == null ? null : pr.getUuid(), level);
    if (gl != null) L.add(gl);
  }
  String plate = @PKG@.MobLevel.plateOf(null, store, t);
  L.add("=Plate: " + (plate == null ? "none" : plate) + " - attitude " + (att.length() == 0 ? "unknown" : att));
  if (!@PKG@.MobLevel.HOOK) L.add("-The level hook is NOT running this start (see the ERROR in the server log): no mob gets a level.");
  String[] out = new String[L.size()];
  for (int i = 0; i < out.length; i++) out[i] = (String) L.get(i);
  return out;
}""")
M(mc, r"""
public static String set(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world, String typed) {
  int lvl;
  try { lvl = Integer.parseInt(typed == null ? "" : typed.trim()); } catch (Throwable e) { lvl = -1; }
  if (lvl < 0 || lvl > @PKG@.MobCfg.MAX_LEVEL) return "-[Mobs] Type a level from 0 to " + @PKG@.MobCfg.MAX_LEVEL + " (0 removes the level).";
  @REF@ t = target(store, ref, world);
  if (t == null) return "-[Mobs] Look at a mob (or stand within 8 blocks of a levelled one), then try again.";
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  @ESM@ m = (@ESM@) store.getComponent(t, @ESM@.getComponentType());
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  if (npc == null || m == null || uc == null) return "-[Mobs] That is not a mob with health.";
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  if (lvl == 0) {
    @PKG@.MobLevel.strip(null, store, t, m, uc.getUuid());
    return "+[Mobs] Removed the level from " + name + ".";
  }
  @PKG@.MobLevel.apply(null, store, t, npc, m, uc.getUuid(), world, world == null ? "" : world.getName(), role, lvl, false, "set", null);
  String no = @PKG@.MobCfg.whyNotRole(@PKG@.MobLevel.attitudeOf(null, store, t), role);
  int hi = @DST@.getHealth();
  float ap = @PKG@.MobLevel.amountOn(m, hi, @PKG@.MobLevel.keyOf(lvl));
  double ff = @PKG@.MobCfg.floorFactor(@PKG@.MobLevel.baseOf(m, hi));
  return "+[Mobs] " + name + " is now Lv " + lvl + " (health x" + f2(ap >= 0.0f ? ap : @PKG@.MobCfg.hpMult(lvl)) + (ff > 1.0 ? " with the " + @PKG@.MobCfg.HP_FLOOR + " HP floor" : "") + ", damage x" + f2(@PKG@.MobCfg.dmgMult(lvl)) + ")."
      + (no == null ? "" : " It is not in the level lists (" + no + "), so it loses the level when it reloads.");
}""")
M(mc, r"""
public static String[] plateTest(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  @REF@ t = target(store, ref, world);
  if (t == null) return new String[] { "-[Mobs] Look at a mob first, then run /mobs platetest." };
  @NPCE@ npc = (@NPCE@) store.getComponent(t, @NPCE@.getComponentType());
  @UUIDC@ uc = (@UUIDC@) store.getComponent(t, @UUIDC@.getComponentType());
  if (npc == null || uc == null) return new String[] { "-[Mobs] That is not a mob." };
  String role = npc.getRoleName();
  String name = @PKG@.MobLevel.nameOf(role, @PKG@.MobLevel.tkeyOf(npc));
  @PKG@.MobInfo info = (@PKG@.MobInfo) @PKG@.MobLevel.MOBS.get(uc.getUuid());
  int lvl = info == null ? 9 : info.level;
  String f = @PKG@.MobCfg.FORMAT == null ? "[Lv {level}] {name}" : @PKG@.MobCfg.FORMAT;
  String base = f.replace("{level}", String.valueOf(lvl)).replace("{name}", name).trim();
  String red = "%s";
  String[] steps = new String[] { "1: " + @PKG@.MobLevel.markup(base, red, "tag"), "2: " + @PKG@.MobLevel.markup(base, red, "section"),
                                  "3: " + @PKG@.MobLevel.markup(base, red, "brace") };
  if (!@PKG@.MobPlateStep.claim(uc.getUuid(), System.currentTimeMillis()))
    return new String[] { "-[Mobs] A plate test is already running on this mob - wait for it to finish (9 s)." };
  String orig = @PKG@.MobLevel.plateOf(null, store, t);
  @PKG@.MobPlateStep s = new @PKG@.MobPlateStep(world, uc.getUuid(), steps, pr, orig, name);
  s.onWorld = true;
  s.run();
  return new String[] { "=[Mobs] Plate test on " + name + ": watch its nameplate, 3 s each - 1 = color tag, 2 = section sign code, 3 = brace token.",
                        "=The step whose text turns RED with no code letters is the markup the client draws. Then Server Setup > Mobs > Nameplate: Colour markup = that number, Colour by level ON." };
}""" % TEST_RED)
M(mc, r"""
public static String reload(java.util.UUID who, String name) {
  if (who == null) return "-[Mobs] Could not tell who sent this command - nothing was changed.";
  Object o = null;
  try { o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, name, "command" }); } catch (Throwable t) { o = null; }
  if (!(o instanceof Object[]) || ((Object[]) o).length < 3) return "-[Mobs] The settings could not be re-read - see the server log.";
  Object[] r = (Object[]) o;
  if ("ok".equals(r[0])) return "+[Mobs] config.properties + bands.properties: " + r[2] + " New spawns use the new values.";
  return "-[Mobs] " + r[2];
}""")

# ================================================================= commands
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []


def cmd(clsname, name, desc, args, body, perm="@ADV@", subs=()):
    """One AbstractPlayerCommand. args = [(field, argName, argDesc, "STRING")], read into a0, a1, ..."""
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = ['super("%s", "%s");' % (name, desc), perm]
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s));\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.MobLog.warn(\"/mobs " + name + " failed: \" + t);\n"
      "    @PKG@.MobCmds.tell(pr, \"-[Mobs] Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


X = "@PKG@.MobCmds."
A = "@ADMIN@"
cmd("MobsInfoCmd", "info", "The mob level band where you stand", [], X + "tellAll(pr, " + X + "infoLines(pr, store, ref, world));")
cmd("MobsInspectCmd", "inspect", "Admin: level, lookup step and band of the mob you look at", [],
    X + "tellAll(pr, " + X + "inspect(pr, store, ref, world));", perm=A)
cmd("MobsSetCmd", "set", "Admin: set the level of the mob you look at (0 removes it)",
    [("levelArg", "level", "Level (0 = remove)", "STRING")], X + "tell(pr, " + X + "set(pr, store, ref, world, a0));", perm=A)
cmd("MobsPlateCmd", "platetest", "Admin: show the three nameplate colour markups on the mob you look at", [],
    X + "tellAll(pr, " + X + "plateTest(pr, store, ref, world));", perm=A)
cmd("MobsReloadCmd", "reload", "Admin: re-read config.properties and bands.properties", [],
    X + "tell(pr, " + X + "reload(pr.getUuid(), pr.getUsername()));", perm=A)
cmd("MobsCmd", "mobs", "Mob levels: /mobs shows the level band where you stand", [],
    X + "tellAll(pr, " + X + "infoLines(pr, store, ref, world));",
    subs=("MobsInfoCmd", "MobsInspectCmd", "MobsSetCmd", "MobsPlateCmd", "MobsReloadCmd"))

# ================================================================= plugin
C(pl, "public SkyyMobsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
M(pl, r"""
public void systems() {
  @PKG@.LevelHook.RBS = cls("%s");
  @PKG@.LevelHook.SETUP = cls("%s");
  @PKG@.LevelHook.BAL = cls("%s");
  @PKG@.LevelDamage.ADR = cls("%s");
  @PKG@.GapDamage.ADR = @PKG@.LevelDamage.ADR;
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelHook(true)); @PKG@.MobLevel.HOOK = true; }
  catch (Throwable t1) {
    @PKG@.MobLevel.HOOK = false;
    @PKG@.MobLog.error("the level hook could not be ordered after the NPC setup systems (" + t1 + ") - NO mob gets a level this start. "
        + "There is no unordered fallback on purpose: it could run before a mob's role and stats exist and strip saved levels. "
        + "Mobs keep the levels saved on them; /mobs inspect shows this too. Please report it with this log.");
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelDamage(true)); }
  catch (Throwable t3) {
    @PKG@.MobLog.warn("could not order the level damage before armour (" + t3 + ") - unordered fallback: this start a levelled mob's damage may be scaled after armour instead of before");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.LevelDamageU()); } catch (Throwable t4) { @PKG@.MobLog.warn("the level damage could not be registered: " + t4 + " - mobs deal vanilla damage this start"); }
  }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.GapDamage(true)); }
  catch (Throwable t5) {
    @PKG@.MobLog.warn("could not order the level gap before armour (" + t5 + ") - unordered fallback: this start your damage on out-levelled mobs may be cut after armour instead of before");
    try { getEntityStoreRegistry().registerSystem(new @PKG@.GapDamageU()); } catch (Throwable t6) { @PKG@.MobLog.warn("the level gap could not be registered: " + t6 + " - players deal full damage to out-levelled mobs this start"); }
  }
}""" % (ROLEB, SETUPS, BALS, ADRS))
M(pl, r"""
public void setup() {
  @PKG@.MobLog.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyMobs");
  @PKG@.MobCfg.DIR = dir;
  @PKG@.MobCfg.FILE = dir.resolve("config.properties");
  @PKG@.MobCfg.BANDS = dir.resolve("bands.properties");
  String mg = @PKG@.MobMig.run(dir);   // 0.1.1: untouched caps 5 / 3 -> 6 / 3.5 + the difficulty comment (once; History first; Undo in Server Setup)
  String mg14 = @PKG@.MobMig14.run(dir);   // 0.1.4: the level curve block + strength.shape (once; History first; Undo in Server Setup)
  if (mg14.length() > 0) mg = mg.length() > 0 ? mg + "\n" + mg14 : mg14;
  @PKG@.MobCfg.load();
  @PKG@.MobCfg.ON_HEALTH = new @PKG@.MobRefresh(null);   // 0.1.2: from now on a health setting change re-applies the loaded mobs
  systems();
  getCommandRegistry().registerCommand(new @PKG@.MobsCmd());
  @PKG@.MobLevel.bridge().put("mob:fn:level", new @PKG@.MobLevelFn());
  @PKG@.MobLevel.bridge().put("mob:fn:info", new @PKG@.MobInfoFn());   // 0.1.4: SkyySkills' kill XP by mob level
  @PKG@.MobLog.info("@VERSION@ ready (@KITID@) - levels " + (!@PKG@.MobLevel.HOOK ? "NOT RUNNING (level hook missing, see the error above)" : @PKG@.MobCfg.ON ? "on" : "OFF") + ", " + @PKG@.MobCfg.strengthText() + ", " + @PKG@.MobCfg.LOADED + "; plates " + @PKG@.MobCfg.PLATE_MODE + " '" + @PKG@.MobCfg.FORMAT + "' (colours " + (@PKG@.MobCfg.COLOR_ON ? @PKG@.MobCfg.MARKUP : "off") + "); /mobs; settings in Server Setup > Mobs; data in " + dir + (mg.length() > 0 ? "; " + mg.replace('\n', ' ') : ""));
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.MobScanTask(), 15L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
  try { @PKG@.MobLevel.PRUNE = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.MobPruneTask(null), 300L, 300L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.MobLog.warn("could not schedule the prune of gone mobs: " + t); }
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.MobCfg.ON_HEALTH = null; } catch (Throwable t) { }
  try { java.util.concurrent.ScheduledFuture f = @PKG@.MobLevel.PRUNE; if (f != null) f.cancel(false); @PKG@.MobLevel.PRUNE = null; } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.MobLevel.bridge().remove("mob:fn:level"); } catch (Throwable t) { }
  try { @PKG@.MobLevel.bridge().remove("mob:fn:info"); } catch (Throwable t) { }
  try { @PKG@.MobGap.CACHE.clear(); } catch (Throwable t) { }
  try { @PKG@.MobLevel.clearAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written:", len(ALL + CMDS) + 1 + len(kit.classes), "(%d kit)" % len(kit.classes))
print("built-in roles: %d exact vanilla ids (%d chars); levels.roles (extra) default %r; levels.exclude: %d chars; %d biome rows, %d env rows, "
      "%d zone rows" % (len(LEVELLED), len(LEVELLED_TEXT), ROLES_DEF, len(EXCLUDE_DEF), len(BIOME_ROWS), len(ENV_ROWS), len(ZONE_ROWS)))

jar = os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn mob levels: every hostile mob and neutral fighter gets a level from the zone / biome it spawns in "
                 "(Zone 1 Lv 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60), more health and damage per level with a difficulty "
                 "setting and a health floor, the Level curve (Wynncraft style) and a BRUTAL level gap, a [Lv 9] nameplate, /mobs, mob:fn:level + mob:fn:info "
                 "bridges. Settings in game (Server Setup > Mobs). No dependencies (the Level curve is made for SkyyGear's gear curves; use Per "
                 "level without SkyyGear).",
                 PKG + ".SkyyMobsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
