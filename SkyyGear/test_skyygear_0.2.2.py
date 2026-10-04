"""Bare-JVM check for SkyyGear 0.2.2 (the 0.2.1 harness carried forward + section AD: the wand / staff shot lines, no note, the vanilla
Damage Data box hidden per item type, the crit effects), kept next to the build so the build report's JVM claim can be re-run.

    python SkyyGear/test_skyygear_0.2.2.py [--jar <SkyyGear-0.2.2.jar>] [--dir <scratch folder>] [--live <config.properties>] [--keep]

0.2.2 changes to the carried-forward sections (each marked "0.2.2" in the code): the JVM also gets the pinned SkyyArmory jar (read from the
SET line, read only); the More Crossbow Tiers pack zip is found by its manifest (Skyy re-downloaded it as More_Crossbow_Tiers_0.6.8.zip on
2026-10-03 - the 0.2.1 harness and build looked for More_Crossbow_Tiers.zip only); shape02 / shape013 + the new shape021 drop the 0.2.2
block (six rows under charged.log that NO one-time update writes), so Z7 / Z8 / AB7 compare as before and Z8 checks the six keys stay out
of the live file; AB8 allows the new Server/Entity/UI/SkyyGear_CritText.json; AC1 counts 63 rows; AC7 / AC8 / AC11: the grey notes are
GONE (0.2.1's HINT_W / HINT_A / GearView.hints removed - no tooltip, describe line or page column shows them; the jar's classes carry no
note text); AC10 stays the historical 0.2 -> 0.2.1 compare of the two SHIPPED jars.
  AD 0.2.2 - every new code path EXECUTED:
     AD0 the SkyyArmory model: its REAL ArmoryInfoFn (armory:fn:info), ArmoryCfg, ladder tables and 31 projectile files from the pinned
         jar, its REAL config kit started on a scratch folder (config:fn:SkyyArmory get + console set);
     AD1 the shot lines for every SkyyArmory wand + staff and the Wood wand (+ Rotten / Tribal) at band start / middle / cap (+ Lv 6) vs an
         independent Python formula (projectile damage x SkyyArmory's tune x F(L) x material bonus), Skyy's Lv 6 sample 43 / 9, no melee /
         spell line; SkyyArmory's live rows (tune %, Wood quick-only, quick.damage, part.tune off), part.base / base.mode off, the item's
         own modifiers, a tap that is still a melee swing, SkyyArmory ABSENT (0.2.1's lines), wands / staffs it does not own,
         gear:fn:describe + the Reforge page columns, the re-render on SkyyArmory's config epoch;
     AD2 no note in any written tooltip (with / without SkyyArmory, weapons + armor);
     AD3 the vanilla box per item type on real Item / ItemWeapon objects carrying the ENGINE-computed breakdowns: hidden (protocol
         ItemWeapon.toPacket = 0 entries, packet cache dropped), SkyyGear's own K / ranges / plain line unchanged (snapshot), non-gear
         weapons and spellbooks untouched, twice = once, a real LoadedAssetsEvent after a reload (fresh breakdown re-snapshotted), switched
         off at start = nothing, restore = the engine's own objects back; the row; the setup / start wiring; the ENGINE scan (no reader
         but toPacket, ItemModule.computeWeaponData the only writer, no ItemWeapon JSON field) and the SET scan (no other jar reads the
         breakdowns / combat text / UIComponentList or ships an EntityUI asset; their weapon files untouched);
     AD4 the crit effects: critLevel = the crit hitAmount rolled (4000 random hits); the style asset decoded by the engine's
         EntityUIComponent codec (+ validators, a bad Scale refused) and its join packet; the loaded-index model; the strip (UIComponentList
         .update gives all three styles -> [0, 1]) + the REAL GearCritClean.onEntityAdd; a real crit through the REAL GearHitSys then the
         REAL GearCritSys then vanilla's DamageSystems$EntityUIEvents on the ECS shim: the defaults (CRIT! then vanilla's number, sparks to
         the attacker at the hit location as a real SpawnParticleSystem packet), the trial swap (style list first, then popup + number),
         one pending restore per pair, the REAL GearCritTick restore after ~0.55 s, a mob that left view, a mob never seen, the asset not
         loaded, the player switch off, crit.fx off, sparks everyone (ParticleUtil's own 75-block collect) / nobody, the overcrit text,
         bad text fallback, the text check hook + loader, the per-hit fix after an asset reload, the unordered fallback, no tick = no
         swap, the crit table bound, the rows + player switch + wiring;
     AD5 the new engine calls resolve from MethodHandles.publicLookup; AD10 the class byte-compare 0.2.1 -> 0.2.2 (every difference listed).

THE 0.2.1 HARNESS TEXT (still true for the carried-forward sections):

0.2.1 changes to the carried-forward sections (each marked "0.2.1" in the code): shape013 / the new shape02 strip the 0.2.1 block (the
fresh file = the 0.2 file + that block under level.armorNative); Z7 / AB7 compare with those shapes; Z8 (start twice on a scratch copy of
the whole live folder) runs migrate021 after migrate02 in setup()'s order; Z9 finds the moved weapon branch in GearHit.weaponHit; AB9 stays
the historical 0.1.3 -> 0.2 compare of the two SHIPPED jars; every scratch case helper first waits for the config kit's fallback save
threads (cfg_quiet: their async change-log flush could write a line twice into a later case's log - Y(b) / Y(c) / Y(e) failed now and
then in the carried-forward 0.2 harness; a bare-JVM artefact, in game the updates run before the kit starts). The JVM also gets the pinned
SkyyMobs jar on its classpath (read only) for AC6 - since the review of 0.2.1 the version is read from tools/deploy_set.py's SET line.
  REVIEW OF 0.2.1 (applied; each check below FAILS on the reviewed jar and passes on the fixed one):
     AC3(c) finding 1 - the REAL GearHitSys.handle on the ECS shim with real Damage objects carrying the engine's DamageSequence meta and
         the REAL calculators of the AC0 model's walk (GearChg.ensure): the reviewer's two cases (a Lv 40 Mithril shortbow arrow with a
         newer Lv 40 staff record = the bow's x1.12 + its own Strength, never x3.36; an Iron crossbow bolt with a newer Lv 13 shortbow
         record = exactly 10, never 21), the Lv 13 shortbow's own arrow keeps 25.2, the same item at two levels = the lower multiplier,
         no step / an unknown step = the clamp fallback (53.76 / 10 / 12), an incomplete walk never rules a record out, a weak bow's arrow
         never gets a strong bow's numbers, a blocked record still blocks, one record = unchanged; calcOf / cands / minMult / pickFor
         directly; AC11 the wiring (GearHitSys -> pickFor(calcOf), weaponHit -> minMult between weaponMult and setAmount, pick = pickFor
         with no step); AC10 lists the new GearShotTrack members.
     AC7 finding 2 - the Lv 1 kit wand reads 'Damage: 6-8' with no hint (the Iron crossbow at Lv 15 too: m = 1 up to float noise); a Lv 2
         wand keeps 'Damage at Lv 2' + the hint; the same rule for armor (a Lv 1 copper chestplate keeps 0.2's 'Health: 9', no hint; a Lv 2
         copper helmet is levelled). Finding 3 - 'Spell at Lv 6: 43' under the Lv 6 wand's damage line (the hint under it),
         'Spell: 25' on the Lv 1 kit wand, a Lv 30 Fire spellbook / Frost staff from the projectile damage read straight from
         Assets.zip x F(30) x bonus(30), no spell line on a sword or with part.base / base.mode off, gear:fn:describe carries it.
         Finding 4 - both hints at most 57 characters (the armor hint was 65). AC2 nit - a failed damage-data read is not cached (fixing
         the item gives the real K at the next call). AC1 nit - the base.armor comment names no internal doc section. AC6 nit - the
         SkyyMobs classes come from the SET pin's jar.
  AC 0.2.1 - every new code path EXECUTED against real engine classes, not only loaded:
     AC0 the model: real DamageCause objects (public constructor) in an indexed asset map, fake EntityStatType assets (Health / Mana /
         Stamina) + DefaultEntityStatTypes, the weapon damage breakdowns COMPUTED BY THE ENGINE'S WeaponDamageDataCollector over the Z3
         model of Assets.zip with each DamageCalculator's real numbers (every vanilla + pack weapon; Wood wand 6-8 = Skyy's screenshot),
         real ItemArmor assets (Health StaticModifier, Percent ResistanceModifiers, extra lines); AC1 the seven rows (types, defaults,
         flags, help), the fresh file's block, the loader (bad curve -> default + WARN, any slot case, clamps), checkCurve / checkArmorBase;
     AC2 F(L) = the spec 3.1 table, F(1) = R(1) = 1 EXACTLY, R(L), the material bonus, a live curve change, family bases, K = the engine
         breakdowns' ratio, kits m = 1.0 exactly, the Iron crossbow exactly vanilla at Lv 15, the unreadable step (K = 1 + one WARN), the
         per-weapon table at band starts (spec bounds; R10 and odd items printed for Skyy);
     AC3 the worked table (spec 3.3: wand / orb / staff / sword / thrust / shortbow full draw + headshot at Lv 1 / 4 / 10 / 20 / 40) through
         GearHit.weaponHit on real Damage objects, Skyy's Lv 6 wand 10-14, the Lv 1 kit wand exactly 6 / 8, part.stats / part.base /
         base.mode, the level-then-chain order, non-weapon hits, no player; then the REAL GearHitSys.handle on an ECS shim (a CommandBuffer
         / ArchetypeChunk subclass + the engine singletons Universe / EntityModule / EntityStatsModule): melee, a projectile by its own
         record, an arrow by the shooter's live record, a mob's hit unchanged, the 0.2 gate still blocking first, part.base off;
     AC4 armor Health through the lock plumbing (GearFx.armorPass / lowerNow on a REAL EntityStatMap, the engine's Armor modifier with its
         real key): equip +9 at once, no stacking on re-equip, removed by the next tick after unequip, the chestplate column 9 / 14 / 18 /
         21 / 27, a piece below its vanilla Health (waits for the engine sync), unidentified, switches off, a full set;
     AC5 resistance through the REAL engine ArmorDamageReduction.handle + GearArmorSys.handle + GearTrueSys.handle: the chestplate column
         6.5 / 7.3 / 9.1 / 11.0 / 14.3 %, Projectile, Fire, a set, base.armorOn off, an unidentified piece;
     AC6 SkyyMobs 0.1's real LevelDamage.handle with GearHitSys in both orders (mob hits player / player hits mob), both Filter + BEFORE
         the armor pass (bytecode), the Priest heal cap (SkyyClasses 0.1.10 build script, read only);
     AC7 the tooltip lines (+ the grey hint, colours, off modes, armor lines, other vanilla lines, re-render on a curve change, gear:fn:
         describe, /gear read); AC8 the vanilla-block evidence (ItemWithAllMetadata, ItemDisplayMetadata, the ItemBase packet fields; the
         client's client.lang + HytaleClient.exe strings, read only) and the decision; AC9 migrate021 on a scratch COPY of the live file
         (exact bytes, INFO, History, no change-log line, loader, second start, CRLF, typed keys kept, fresh file, anchors, the
         continuation trap, 400 random files vs java.util.Properties, History blocked) + the rows LIVE through the kit's own set / tset
         ops (curve, bonus, mode, armor table; bad values refused; part.base confirms); AC10 the class byte-compare 0.2 -> 0.2.1 (every
         difference listed exactly, GearBase new, only manifest.json differs among other entries); AC11 the wiring (bytecode).

THE 0.2 HARNESS TEXT (still true for the carried-forward sections):

0.2 changes to the carried-forward sections (only where 0.2 changed what they look at, each marked "0.2" in the code): B the level.material
row help + its Min | Cap columns + the default file's band rows; V a Crude sword reads Lv 1 (its Fabled top roll one level higher); X the
built-in table (Wood / Crude 1), X(a) the ready line shows bands, X(f) in-game edits are bands ("25|32") and a pre-0.2 one-number Undo is
refused by the 2-column table (the band form works - the KNOWN LIMIT of the build header); X / Z7 compare with the fresh file in its 0.1.3
shape (shape013: single numbers, no Armor_Copper, no 0.2 block); Z8 runs migrate02 too and expects every value of a fresh 0.2 file; Z9
the roll moved into newDoc(id, r, ident, src, lvl); AA1 the built-in table (+ Armor_Copper, Wood / Crude 1, copper armor 1), the 0.2 row
help, the fresh file's family bands; AA2 runs on the live file's "before the 0.1.3 level family rows" History copy (0.1.3 is deployed;
the 0.1.3 harness failed here: it noted the copy but never loaded it), the ready line after migrate013 alone shows the width rule, an
in-game edit is a band; AA9 stays the historical 0.1.2 -> 0.1.3 compare of the two shipped jars.
  AB 0.2: AB1 the bands (an independent copy of Skyy's table; GearLevel.band over all 304 vanilla gear ids + 32 gathering tools vs an
     independent Python rule; Armor_Copper 1-18; the fresh file; one-number rows, width 5 / 1, cap below min, a bad line, Level by item;
     the check hooks; the six rows); AB2 crafted at your level (Divinity 0 / 4 / 12 / 13 / 14 / 80 on wand / staff / copper armor / Mithril /
     Prisma; Skyy's level-80 copper pickaxe; Mining / Foraging / Farming tools; 60 craftDoc rolls inside the level-12 bounds; the tool
     document; craftable; craft.levelFrom band; part.levels off; gate floor 0; no SkyySkills; no class; no SkyyClasses; craft.weaponSkill;
     craft.belowBand block texts; the bench roll GearCraftTask.rollIn; gear:fn:roll mode 8 with a requested level); AB3 the gate floor in
     every state (st 0 / 1 / 2), stored levels (check, hit judge popup text, GearStats.active, armor inactive + why), old items without lvl
     (legacy, SkyyRolls, the passive stamp, a band change in Server Setup), reforge / identify / unidDoc / give stamps, part.levels off;
     AB4 the tooltip lines (met / too low / unidentified / tool / no owner / no SkyySkills / under-level armor / plain lines / the render
     signature); AB5 gear:fn:sig with the level (= the hash of id|quality|rarity|identified|mods|level); AB6 /gear relevel on a bare
     Inventory (re-stamped, kept, unstamped, SkyyRolls and plain items untouched, twice = once); AB7 migrate02 on a scratch COPY of the live
     config.properties (exact bytes, INFO, the 69 changed + 7 new keys, History, 70 change-log lines, the loader = a fresh 0.2 file, start
     twice = once) + CRLF, custom values kept, Armor_Copper typed by hand (1 -> 1,18; 3 kept), settings already there, the kit Undo,
     History blocked, the fresh file, a 0.1 file through all five updates, text-step edge cases, 1200 random files vs java.util.Properties;
     AB8 the 8 recipes (decoded through CraftingRecipe.CODEC with no validation failure / unknown key, = the same material's shortbow
     recipe decoded the same way, output x1, no duplicate id vs Assets.zip + the other SET jars, no vanilla file overridden, crafted at
     your level); AB9 the class byte-compare 0.1.3 -> 0.2 (every difference listed exactly, 3 new classes, non-class entries = manifest +
     the 8 recipe files); AB10 the wiring (setup order, GearCraftPreSys, the craft paths, the floor, the sig, relevel admin-only).
  REVIEW OF 0.2 (applied): AB2 finding 1 - a tool below its band gets no "you need Mining N to use it" line and Refuse mode never refuses
     a tool (all 304 gear ids + 32 tools at skill 0: the line + the refusal exactly where the gate is enforced); finding 3 - GearRoll.noteDue
     (a 10-unit queue 3 s / 4 s apart = one note, 10 s of quiet = a new burst, per player + item, the time map purge) + both craft paths
     ask it between craftNote and the send, the refusal is not throttled; AB4 finding 4 - with a test quality asset map (bare JVM): a
     crafted Mithril pickaxe keeps the item's own quality + its colour in the name, a Rare sword keeps Skyy_Gear_Rare, a tool carrying
     today's Skyy_Gear_Normal goes back to its own (then stays put), another mod's quality is kept, a gear.include tool keeps its rarity
     quality; AB8 finding 5 - no recipe carries the Armory bench (7 model bows have it), each keeps its Crafting benches; AB1 finding 6 -
     level.gateFloor has danger; X / AA2 / AB7 finding 6 - the History copies come from the live config-history or, once KEEP 10 evicted
     them, the deploy backups (hist_copy).

THE 0.1.3 HARNESS TEXT (still true for the carried-forward sections):

0.1.3 changes to the carried-forward sections (only where 0.1.3 changed what they look at): B the level.material row help; X / Y / Z7
replay the 0.1.1 / 0.1.2 updates on the live file AS IT WAS BEFORE THEM (its "before the 0.1.1 level table update" copy in the live
config-history - the live file itself is already updated in game) and compare with the 0.1.2-shaped default text (the 0.1.3 family
block left out); X(a)'s ready-line table gained the family count; Z1 the fresh file's version line; Z8 expects exactly the updates
whose marker the live file lacks (today: migrate013 only); Z10 stays the historical 0.1.1 -> 0.1.2 compare of the two shipped jars.
  AA 0.1.3: AA1 the 59 level family rows (an independent copy of the table) + GearLevel.level over all 304 vanilla weapon / armor ids
     from Assets.zip vs an independent Python rule (160 fell back in 0.1.2, 153 now have a row, only the 7 developer ids left, every
     metal-resolved id unchanged, Stone Trork Daggers 5), the multi-word rule (one-word tables = the 0.1.2 loop, 2 / 3 words, a 4-word
     entry never matches, case), Level by item still wins, the row help, the fresh file; AA2 migrate013 on a scratch COPY of the live
     config.properties (exact bytes, INFO, every old key kept, the old lines in order, one History copy, 59 change-log lines with old
     "(none)", the loader, the ready line, second start = no change), CRLF, a family row already there (kept + noted), the config kit:
     log op lists the 59 lines, Undo = remove + a tset apply at once, a removed row never comes back, no file / fresh file, History
     blocked, the text step's edge cases (anchors, the end-of-file continuation trap, marker in a value, commented rows) + 1500 random
     files vs java.util.Properties; AA3 GearChestOpen.decide on plain containers: a prefab chest (no placer / a builder's placer) tagged
     on the first open (sword, armor, each spear of a stack, src chest; counts equal; rock, ammo and documented gear untouched), never
     a second time (open by another player, break), the Chest odds; a loot-table chest tagged at add (0.1.2) unchanged by its open; an
     admin's placed loot container (L -> T); player storage (P) never touched, a P spot without placer decided again, a W spot a player
     built on -> P, an unreadable player list -> untouched + not remembered, islands (name + island:owner:fn), part.chests off; AA4 the
     chests/<world>.txt memory (lines in order, header once, read back after a restart, still never twice, safe names, bad lines);
     AA5 SkyyExploration 0.2.2's chest luck (read from its build script) through the loot window on a bare Inventory: decide -> give ->
     scan, scan -> give -> scan, a late scan in the grace time, the window expired = legacy Normal, the overflow drop (lootStack);
     AA6 no leak (another player, the player's own chest, a full inventory keeps the stack whole); AA7 bytecode: decide only from
     process, process only from UseBlockEvent$Pre / BreakBlockEvent / the window task, block entity -> ItemContainerBlock -> placer,
     the window backup only on ContainerBlockWindow, ContainerWindow (SkyyVault / SkyyEssentials trade / SkyySacks) is no BlockWindow,
     the storage mods' build scripts use no block container, the event classes, GearChestMark keeps chestMark then lootMark, the
     stamps ask the loot window, GearLevel reads MAT_WORDS; AA8 setup order (migrate012 -> migrate013 -> load -> GearOpened.DIR ->
     GearKnownTask -> CfgPub.start), both systems registered, shutdown flush, GearTick / GearReady hooks; AA9 the class byte-compare
     0.1.2 -> 0.1.3 (every difference listed exactly, 8 new classes, only manifest.json differs among the other entries).
  REVIEW OF 0.1.3 (applied): AA1 Bone 5 / Praetorian 25 / Spellbook_Frost + Staff_Frost 30 and the WARN for a 4-word entry;
     AA3(d) an L / T record keeps its placer (another player of this server -> P, a builder -> still loot, list unread -> -5, a line
     without placer -> as before); AA3(e) the loot window's hard cap (refreshes never past start + 15 s, the window task after the cap
     opens nothing, a new open restarts it, a container decided by the window task starts it); AA3(c) known() never reads the list;
     AA4 placer= in L / T lines + read back, X lines, a regenerated chunk forgets its records (P too; negative chunks; reads the file
     first; no file = nothing), pack / unpack, block -> chunk, a temporary world never writes a file, evict on world removal, the
     prefetch task; AA7 known() / second() / decide / spawned / GearChunkRegen / GearWorldBye / wkey bytecode; AA8 the new wiring.
--live = the config.properties to copy (read only) for tests X(a) / AA2; default: the "HUD mod" test world's Skyy_SkyyGear/config.properties.
Build the jar first (python SkyyGear/build_skyygear_0.2.py). A child process starts a fresh JVM (the game's own JRE, -Xverify:all,
-XX:-UsePerfData, HytaleServer.jar + the jar + tools/javassist.jar on the classpath; TEMP / TMP / java.io.tmpdir in the scratch
folder) and checks:
  A  every class loads and verifies
  B  config rows: gear.include, kind.prefix, migrate.clampToLevel (danger), KEEP 10, help <= 100, the Placeholder suffix on the five
     rows (design 10), the stat legend (design 7), the default file's per-key legend lines
  C  exploit 3: the 14 ammo ids stay ammo, Weapon_Shortbow_Bomb is gear
  D  design 1: gear.include (bags never), kind.prefix (longest wins, bad values dropped), the Equipment slot 4 + letter e, enforced kinds
  E  design 2: gear:extra:<uuid> parsed into the one totals function (withExtra on / off)
  F  design 3 / 4: vanilla #ff6b6b / #39f493, Mythic #CC66CC (defs + the quality asset), no old red / orange constants left
  G  design 5: Health Regen % never rolls without Raw Health Regen; its label
  H  design 6 / 8 / 9 / 11: the spell suffix, elements out of the hit math and into info[5], identify texts follow identify.command,
     the five coming-later Keep stats
  L  engine 1: GearFx.plan (lower always, raise only when the engine's Armor modifier is synced), a simulation of the engine clamp
     (EntityStatValue.computeModifiers) over equip / unequip / swap / level-up / break sequences in every order the two passes can
     run relative to EntityStatsSystems$Recalculate, the Armor key, GearLockSys ordered BEFORE Recalculate, raise flags (bytecode)
  M  engine 2: broken armor = amount x BrokenPenalties factor (the engine's computeStatModifiers shape)
  N  engine 3: armor in the hand is never judged as a weapon; an unidentified weapon still is
  O  engine 4: quality.properties parse / write / moved-index WARN (no epoch bump since follow-up 7); a stale stack quality is
     rewritten; sig uses names
  P  engine 5: GearFxInvSys only reacts to the armor container (bytecode)
  Q  engine 6: GearLog - line() and take() never wait for the disk lock; flush() writes under WLOCK only
  R  engine 7: writeAtomic replace / no-replace, no temp file left
  S  exploit 1: GearShotTrack.newest (newest live record of that shooter inside the 10 s window); GearHitSys uses pick (bytecode)
  T  exploit 2: stack split (storage first, counted, full inventory keeps the stack, nonces), craft rolls per item + the q <= cap - n
     rule, chest split per item, Identify all skips rows it cannot split
  U  exploit 4: migrated armor drops dmg and scores without it
  V  exploit 5: migrate.clampToLevel caps each migrated value at GearRoll.bounds(i, rarity, level)[1]
  W  follow-up review of e43c8bf: 1 gear.include guard (check hook, loader drops, ammo beats include, stackable included ids,
     kind equipment), 2 MaxStack ammo rule + split ceiling (fake Item assets with a MaxStack), 3 no hotbar split + 5-slot floor +
     no passive split + Identify / Reforge / Identify all take one item off a stack, 4 GearShotTrack.pick (weaker weapon) + the
     no-record WARN, 5 GearLockSys primes from saved locks, 6 scheduleRecalculate after waits, 7 unreadable quality.properties
     kept, 8 a throwing destination restores the source (split + takeOne), 9 gear:extra saturation + hit never below 0,
     10 negative armor sums cancelled (plan + clamp simulation)
  X  0.1.1: Skyy's level table (built-in, default file, loader, GearLevel.level, the row help) and the one-time config.properties
     update GearCfg.migrate011 on scratch copies: (a) the live file (exact bytes: six lines + the marker, History copy = the old
     bytes, six config-changes.log lines, the INFO line printed), (b) one hand-edited material kept + noted, (c) CRLF kept, (d) no
     file (nothing written; the loader's fresh 0.1.1 file carries the marker), (e) a second start changes nothing, (f) a file the
     config kit wrote in game (tset / set / remove through config:fn:SkyyGear + flush): custom kept, removed line stays removed, the
     kit's history + log lines kept, undo of an update line and of the kit's own line still work, old values set back after the
     update survive the next start, (g) the pure text step on edge cases (spacing, case, duplicates, continuation, templates, no
     header, no final newline, separators, trailing spaces, marker in a value), (i) the review of 0.1.1: finding 4 = a file ending
     inside a still-open continued entry gets the marker just before that entry (fixed cases + 3000 random files checked against
     java.util.Properties and byte for byte + migrate011 end to end, no marker per start), finding 3 = no rewrite unless
     config-history holds the old bytes (blocked History folder -> WARN + untouched, then updated; a failed write retried without a
     second copy; a copy whose index line failed still counts), (h) non-ASCII bytes + BOM kept, a folder in place of the file = WARN and nothing written;
     setup() order importRolls -> migrate011 -> migrateStat011 -> load -> CfgPub.start (bytecode)
  Y  0.1.1 stat defaults (OPEN-QUESTIONS LOCKED 2026-09-30: pool.later off, stat.levelFull 40): (a) row defaults + help (pool.later
     has no Placeholder claim any more - B's design-10 list drops it), the field initial values (bytecode), the loader fallback
     (missing / unreadable line), the level factor (full power from 40), the fresh default file (values + the stat marker above the
     pool.later help line; neither update touches it); (b) the live file on a scratch copy through both updates in the setup order:
     exact bytes (two value lines + the marker), the INFO line printed, two History versions, two scalar change-log lines, the
     loader + the ready line's stat part; (c) a second start changes nothing; (d) CRLF; (e) hand-edited values kept + noted (on,
     True, 45, 50.0) or silent (already new, missing lines -> the marker under the level marker); (f) the config kit's log op lists
     the two lines, Undo (set back) works and survives the next start; (g) History blocked -> no rewrite + WARN (also on the whole
     live start), then updated; a failed write retried without a second copy; no anchor -> WARN, untouched; (h) the pure text step
     on edge cases + 2000 random files checked against java.util.Properties and byte for byte; (i) EVERY roll path with pool.later
     off never yields a coming-later stat: GearRoll.rollMods over all slots / rarities / levels, /gear give (newDoc), crafting
     (craftDoc, the bench per-item roll GearCraftTask.rollIn, the SkyySacks /craft bridge gear:fn:roll for craft and other sources),
     mob drops (GearTag.unid + gear:fn:unid, then the Identify page GearIdent.identify and /gear identify GearRoll.identify), loot
     chests (GearTag.tagContainer + Identify all GearIdent.allIn), the Reforge page (GearForge.reforge paid) and /gear reroll (free),
     SkyyRolls migration (GearData.migrate / effective / the passive stamp) - with the coming-later weights raised to 100000 so one
     leak would dominate (a pool.later-on control run shows them), GearRoll.RNG is a never-seeded SecureRandom so "many seeds" =
     many independent rolls; the bytecode shows GearRoll.pool is the only way into a roll (callers of pool / GearData.mod /
     rollMods); gear that already has one keeps it until its next reforge (the lock), and loses it on that reforge
  Z  0.1.2 Charged Attack Damage: Z1 the stat row (after Crit Damage), the rows charged.on / spellFactor / log, loader clamps, the
     fresh default file, the tooltip (+ grey "off on this server"); Z2 hitAmount (x (1 + chg) after Strength / Magical Power, spells x
     (1 + 0.15 chg), crits after, clamp at 0, True / element damage never multiplied); Z3 the calculator index built from the REAL
     Assets.zip: the build's own Python walk vs the jar's collector on engine objects walked by the engine's InteractionManager.walkChain
     for every vanilla weapon + the More Crossbow Tiers crossbows (per calculator flags + class, launches, has / partial), and the
     runtime eligibility == the baked list; Z4 the per-hit rule on those real calculators (bow glow draw + headshot yes, partial draws
     no, volley / signature no, sword / axe / longsword / daggers + backstab / mace / Void scythe yes, crossbow 3rd bolt yes (trusted),
     the same bolt / a Class-tagged swing on an untrusted id no, unknown calculators, flail club / Crystal Ice no, prototype bow
     ambiguous no, legacy launches, charged.on off; GearCharged.judge on a real Damage when a bare JVM can build one); Z4b the review
     of 0.1.2 (finding 1: a picked launch record of another weapon - spear / sword record, bow arrow - never lets a partial draw count,
     the glow draw and the crossbow combo still count via the live records' walks, the Class-tag fallback is melee only, every live
     weapon that knows a step must call it charged, a legacy launch flag counts only with one weapon in the air; finding 2: the
     Vampire bow never counts / rolls; finding 3: one chgmiss WARN per weapon id; finding 4 + 5 in Z9 / Z6); Z5 roll
     eligibility per weapon family + armor / Equipment, charged.on off = never (every roll path, chg the only weighted stat), the baked fallback
     when the walk cannot run; Z6 the verifier's cases (single spellbook, single spear: the hand snapshot supplies the stack, its own
     stats + the charged flag now apply; stale / foreign / non-gear snapshots never; per player); Z7 the one-time update migrate012 on
     scratch copies (the live file through all three updates: exact bytes, INFO, History, no change-log line, the loader, Server Setup
     lists chg; second start; fresh file; CRLF; kept hand edits; missing anchors + the end-of-file continuation trap; 3000 random
     files vs java.util.Properties; History blocked); Z8 setup()'s file steps twice on a scratch copy of the whole live
     Skyy_SkyyGear folder (second start: every file but gear.log byte-identical); Z9 bytecode (setup order, the combat hook, the shot
     record, roll entry points, /gear charged admin); Z10 the class byte-compare 0.1.1 -> 0.1.2 (every difference listed)
Not testable without the game (UNVERIFIED in the build report): the real system order around Recalculate, the engine recalculating a
live EntityStatMap, projectile records on real arrows, item entities, loot chests, pages on a client, the quality asset pack.
Nothing is deployed. Default scratch folder: tools/dev/scratch/gear02/harness (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, time, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.2.2"
PKG = "com.skyy.gear."
LIVE_DEFAULT = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyGear",
                            "config.properties")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "gear022", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
# 0.2.1: the pinned SkyyMobs jar (tools/deploy_set.py SET) - section AC6 runs its LevelDamage next to GearHitSys (read only). Review of
# 0.2.1 nit: the version is READ from the SET line in tools/deploy_set.py (the file is only read, never run), so the harness follows the
# pin (0.1.1 today; it was hard-coded to 0.1); no SET line -> 0.1


def mobs_pin():
    try:
        m_ = re.search(r'\(\s*"SkyyMobs"\s*,\s*"([0-9][0-9.]*)"\s*\)', open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
        return m_.group(1) if m_ else "0.1"
    except Exception:
        return "0.1"


MOBS_PIN = mobs_pin()


def mct_zip(mods_dir):
    """0.2.2: the pack mod More Crossbow Tiers (Serj) was re-downloaded on 2026-10-03 as More_Crossbow_Tiers_0.6.8.zip (same 1.1.0, same 4
    crossbows) - the build script's finder: any More_Crossbow_Tiers*.zip whose manifest is Serj / More Crossbow Tiers (read only)"""
    try:
        names = sorted((n for n in os.listdir(mods_dir) if n.startswith("More_Crossbow_Tiers") and n.endswith(".zip")),
                       key=lambda n: (n != "More_Crossbow_Tiers.zip", -os.path.getmtime(os.path.join(mods_dir, n))))
    except Exception:
        return None
    for n in names:
        try:
            with zipfile.ZipFile(os.path.join(mods_dir, n)) as z_:
                m_ = json.loads(z_.read("manifest.json").decode("utf-8-sig"))
            if m_.get("Group") == "Serj" and m_.get("Name") == "More Crossbow Tiers":
                return os.path.join(mods_dir, n)
        except Exception:
            continue
    return None
MOBS_JAR = os.path.join(ROOT, "SkyyMobs", "SkyyMobs-%s.jar" % MOBS_PIN)


# 0.2.2: the pinned SkyyArmory jar (tools/deploy_set.py SET) - section AD reads its REAL bridge answer (com.skyy.armory.ArmoryInfoFn =
# armory:fn:info), its projectile files and its config kit (config:fn:SkyyArmory get / console set), read only; no SET line -> 0.1
def armory_pin():
    try:
        m_ = re.search(r'\(\s*"SkyyArmory"\s*,\s*"([0-9][0-9.]*)"\s*\)', open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
        return m_.group(1) if m_ else "0.1"
    except Exception:
        return "0.1"


ARMORY_PIN = armory_pin()
ARMORY_JAR = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-%s.jar" % ARMORY_PIN)

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def hist_copy(reason):
    """(bytes, folder) of the config-history copy written with this reason, or (None, [folders searched]). Review of 0.2 finding 6: the
    live Skyy_SkyyGear/config-history keeps 10 copies (KEEP 10), so in-game Server Setup edits evict the old update copies the replays
    below run on; every deploy backs the whole Skyy_SkyyGear folder up first (PROJECT-RULES 3: backups/deploy-<date>-<time>/data/), so
    the live folder is asked first and then those backups, newest first. Read only."""
    dirs = [os.path.join(os.path.dirname(LIVE), "config-history")]
    bk = os.path.join(ROOT, "backups")
    if os.path.isdir(bk):
        for n in sorted(os.listdir(bk), reverse=True):
            dirs.append(os.path.join(bk, n, "data", "Skyy_SkyyGear", "config-history"))
    for hd in dirs:
        ix = os.path.join(hd, "index.log")
        if not os.path.isfile(ix):
            continue
        rows = [l.split("\t") for l in open(ix, encoding="utf-8").read().split("\n") if l.strip()]
        for e in rows:
            if len(e) > 4 and e[4] == reason and "#" in e[0]:
                bp = os.path.join(hd, "%s.%s.bak" % tuple(e[0].split("#", 1)))
                if os.path.isfile(bp):
                    return open(bp, "rb").read(), hd
    return None, dirs


PH = " Placeholder - Skyy tunes this."
AMMO_IDS = ["Weapon_Arrow_Clearshot", "Weapon_Arrow_Crude", "Weapon_Arrow_Deadeye", "Weapon_Arrow_Iron", "Weapon_Arrow_Trueshot",
            "Weapon_Bomb", "Weapon_Bomb_Continuous", "Weapon_Bomb_Fire", "Weapon_Bomb_Large_Fire", "Weapon_Bomb_Popberry",
            "Weapon_Bomb_Potion_Poison", "Weapon_Bomb_Stun", "Weapon_Dart_Tribal", "Weapon_Grenade_Frag"]


# ============================================================================================================== engine clamp model
class StatModel:
    """EntityStatValue as the bytecode does it (2026-09-29): every putModifier / removeModifier recomputes max = base + the MAX
    ADDITIVE modifiers and clamps value into [min, max] at once."""

    def __init__(self, base, value):
        self.base = base
        self.value = value
        self.mods = {}

    def max(self):
        return self.base + sum(self.mods.values())

    def put(self, key, amt):
        if amt == 0:
            self.mods.pop(key, None)
        else:
            self.mods[key] = amt
        self.value = min(max(self.value, 0.0), self.max())


# ============================================================================================================== child: the checks
def run(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JFloat, JInt, JBoolean, JLong, JString, JChar
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST] + ([MOBS_JAR] if os.path.isfile(MOBS_JAR) else [])
                   + ([ARMORY_JAR] if os.path.isfile(ARMORY_JAR) else []), convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    # a bare JVM has no Item asset store and every ItemStack constructor calls getItem(): an empty store (Item.UNKNOWN for every
    # id) is put in place without running its constructor, so stacks, containers and the gear writes can run here
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = us.allocateInstance(fake.toClass(AS.class_))    # never constructed: only getAssetMap() (a plain field read) is used
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)

    J = lambda n: JClass(PKG + n)
    Gear, Defs, Cfg, Data, Roll, View, Stats, Stamp, Forge, Hit, Shot, Track, Armor, Fx, Tag, Ident, Qual, Log, Rows, Lvl = (
        J("Gear"), J("GearDefs"), J("GearCfg"), J("GearData"), J("GearRoll"), J("GearView"), J("GearStats"), J("GearStamp"),
        J("GearForge"), J("GearHit"), J("GearShot"), J("GearShotTrack"), J("GearArmor"), J("GearFx"), J("GearTag"), J("GearIdent"),
        J("GearQual"), J("GearLog"), J("CfgRows"), J("GearLevel"))
    CraftTask = J("GearCraftTask")
    UUID, Paths, Props = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BD = JClass("org.bson.BsonDocument")
    SMO = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier")
    CAL = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType")
    MTG = JClass("com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget")
    HashMap, IdMap, ArrayList = JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"), JClass("java.util.ArrayList")
    Integer = JClass("java.lang.Integer")
    bridge = Gear.bridge()
    Cfg.apply(Props(), False)          # the built-in defaults (no file): material table + every default
    U1 = UUID.fromString("00000000-0000-0000-0000-00000000aaaa")
    U2 = UUID.fromString("00000000-0000-0000-0000-00000000bbbb")
    SK = [str(x) for x in Defs.S_KEY]
    si = SK.index

    # ---------------- B. config rows
    keys = [str(k) for k in Rows.KEYS]
    helps = dict(zip(keys, [str(h) for h in Rows.HELPS]))
    flags = dict(zip(keys, [str(f) for f in Rows.FLAGS]))
    types = dict(zip(keys, [str(t) for t in Rows.TYPES]))
    defs = dict(zip(keys, [str(d) for d in Rows.DEFS]))
    opts = dict(zip(keys, [str(o) for o in Rows.OPTS]))
    check(int(Rows.KEEP) == 10, "config kit KEEP = 10 (LOCKED)")
    check("gear.include" in keys and types["gear.include"] == "text" and defs["gear.include"] == "", "row gear.include (text, empty)")
    check("kind.prefix" in keys and types["kind.prefix"] == "table" and opts["kind.prefix"] == "text;type;Kind", "row kind.prefix (text table)")
    check("migrate.clampToLevel" in keys and types["migrate.clampToLevel"] == "bool" and defs["migrate.clampToLevel"] == "false"
          and "danger" in flags["migrate.clampToLevel"].split(","), "row migrate.clampToLevel (bool, default false, danger)")
    check(all(len(h) <= 100 for h in helps.values()), "every help <= 100 characters")
    # (0.1.1 stat defaults: pool.later left the design-10 list - its default is Skyy's lock now; section Y checks its help)
    for k in ("craft.maxRarity", "migrate.maxRarity", "regen.periodMs", "level.armorNative"):
        check(helps[k].endswith(PH), "design 10: %s help ends with the Placeholder suffix" % k)
    check("Placeholder" not in helps["pool.later"], "0.1.1: pool.later help makes no Placeholder claim (Skyy's lock)")
    check(helps["stat"].startswith("dmg Damage, str Strength, mp Magical Power"), "design 7: the stat row help is a key legend")
    dt = str(Cfg.defaultsText())
    check("# dmg = Damage (weapon, %)" in dt and "# hprp = Health Regen % (weapon, armor, %)" in dt and "# lbonus = Loot Bonus" in dt,
          "design 7: config.properties names every stat key above its line")
    check("(spec 4.2)" not in str(Cfg.checkStat("stat[nope]", "1|1")) and "config.properties" in str(Cfg.checkStat("stat[nope]", "1|1")),
          "design 7: the unknown-stat message has no spec pointer")
    check("migrate.clampToLevel=false" in dt and "gear.include=" in dt and "kind.prefix.<id prefix>" in dt, "default file has the new keys")
    # 0.1.1: Skyy's level table in the default file, the marker under the levels header, the row help, the kit's version
    # (0.2: the row is a Min | Cap band table - its help says so; the default file's rows are Skyy's bands: section AB checks the rest)
    check(helps["level.material"] == "Band by the first id word (Leather_Soft = 2 words). One number = N to N+width-1. Skyy 10-01."
          and types["level.material"] == "table" and opts["level.material"] == "int;type;Min|Cap",
          "0.1.1 / 0.2: the Level by material row help (no Placeholder claim, <= 100) + the Min | Cap columns")
    check(all(("\nlevel.material.%s=%d,%d\n" % tl) in dt for tl in (("Crude", 1, 13), ("Wood", 1, 13), ("Copper", 10, 18), ("Bronze", 15, 23),
          ("Iron", 15, 23), ("Thorium", 20, 28), ("Cobalt", 25, 38), ("Adamantite", 35, 43), ("Mithril", 40, 49), ("Onyxium", 40, 49))),
          "0.1.1 / 0.2: the default file has Skyy's table (as bands)")
    check(("\n" + str(Cfg.LV_HEAD) + "\n" + str(Cfg.LV_MARK) + "\n") in dt and dt.startswith("# SkyyGear %s - " % VERSION),
          "0.1.1: the default file carries the update marker under the levels header + the %s header line" % VERSION)
    check(str(Rows.VERSION) == VERSION and str(Cfg.LV_WHO) == "SkyyGear 0.1.1", "0.1.1: kit VERSION (%s) + the update's fixed name" % VERSION)
    print("B. config rows done")

    # ---------------- C. exploit 3: ammo
    for i in AMMO_IDS:
        check(bool(Data.ammo(i)) and not bool(Data.isGear(i)), "exploit 3: %s is ammo, not gear" % i)
    check(not bool(Data.ammo("Weapon_Shortbow_Bomb")) and bool(Data.isGear("Weapon_Shortbow_Bomb")), "exploit 3: Weapon_Shortbow_Bomb is gear")
    check(bool(Data.isGear("Weapon_Sword_Iron")) and bool(Data.isGear("Armor_Iron_Chest")) and not bool(Data.isGear("Weapon_Shield_Iron")),
          "gear rules unchanged for swords, armor, shields")
    print("C. ammo done")

    # ---------------- D. design 1: gear.include / kind.prefix / Equipment
    check(not bool(Data.isGear("Skyy_Sword_Test")) and not bool(Data.isGear("Tool_Pickaxe_Iron")), "Skyy_ and Tool_ ids are not gear by default")
    p = Props()
    p.setProperty("gear.include", "Skyy_Sword_, Skyy_Ring_,Skyy_Sack_,Skyy_Bag_,Skyy_Accessory_Bag,Tool_Pickaxe_")
    p.setProperty("kind.prefix.Skyy_Ring_", "Equipment")
    p.setProperty("kind.prefix.Armor_", "mining")
    p.setProperty("kind.prefix.Armor_Iron_", "farming")
    p.setProperty("kind.prefix.Weapon_Bad_", "sword")
    Cfg.apply(p, False)
    check(bool(Data.isGear("Skyy_Sword_Test")) and bool(Data.isGear("Skyy_Ring_Gold")), "gear.include opts Skyy_ ids in")
    for b in ("Skyy_Sack_Mining_Small", "Skyy_Bag_Rare", "Skyy_Accessory_Bag"):
        check(not bool(Data.isGear(b)), "bags are never gear, even through gear.include: " + b)
    check(str(Data.kindFor("Skyy_Ring_Gold")) == "equipment" and int(Data.slotOf("Skyy_Ring_Gold")) == 4, "kind.prefix equipment -> slot 4")
    check(str(View.slotWord("Skyy_Ring_Gold")) == "EQUIPMENT", "slot word EQUIPMENT")
    check(str(Data.kindFor("Armor_Iron_Chest")) == "farming" and str(Data.kindFor("Armor_Copper_Chest")) == "mining", "longest kind prefix wins")
    check(str(Data.kindFor("Weapon_Bad_X")) == "combat" and not Cfg.KINDP.containsKey("Weapon_Bad_"), "a bad kind value is dropped")
    check(int(Data.slotOf("Tool_Pickaxe_Iron")) == 3 and str(Data.kindFor("Tool_Pickaxe_Iron")) == "mining", "an included tool stays a tool (slot 3, mining)")
    e_ok = sorted(SK[i] for i in range(int(Defs.NS)) if bool(Roll.allowed(i, 4)))
    check(e_ok == sorted(["str", "mp", "as", "spd"]), "letter e = Strength, Magical Power, Attack Speed, Speed: %s" % e_ok)
    check(bool(Defs.enforcedKind("combat")) and bool(Defs.enforcedKind("equipment")) and not bool(Defs.enforcedKind("mining")),
          "enforced kinds: combat + equipment (gathering later)")
    check(Cfg.checkKind("kind.prefix[Skyy_Ring_]", "Equipment") is None and Cfg.checkKind("kind.prefix[X]", "sword") is not None,
          "kind.prefix check hook")
    d = Roll.newDoc("Skyy_Ring_Gold", 5, True, "admin")
    ms = [str(m.asDocument().getString("s").getValue()) for m in Data.mods(d)]
    check(all(k in ("str", "mp", "as", "spd") for k in ms) and len(ms) >= 1, "an Equipment piece rolls only letter-e stats: %s" % ms)
    Cfg.apply(Props(), False)
    check(not bool(Data.isGear("Skyy_Sword_Test")) and str(Data.kindFor("Armor_Iron_Chest")) == "combat", "defaults back")
    print("D. include / kinds done")

    # ---------------- E. design 2: gear:extra
    bridge.put("gear:extra:" + str(U1), "str:40, cc:10,bogus:5,def:x,spd:-2,cd")
    x = Stats.extra(U1)
    check(x is not None and int(x[si("str")]) == 40 and int(x[si("cc")]) == 10 and int(x[si("spd")]) == -2 and int(x[si("def")]) == 0,
          "gear:extra parsed (unknown keys and bad parts skipped)")
    ok = JArray(JClass("boolean"))(1)
    t = Stats.totals(U1, None, None, ok, True)
    check(int(t[si("str")]) == 40 and int(t[si("cc")]) == 10 and bool(ok[0]), "totals withExtra adds gear:extra")
    t = Stats.totals(U1, None, None, None, False)
    check(sum(int(v) for v in t) == 0, "totals without extra = gear only (gear:stats stays SkyyGear's own)")
    check(Stats.extra(U2) is None, "no gear:extra -> null")
    bridge.remove("gear:extra:" + str(U1))
    print("E. extra done")

    # ---------------- F. design 3 / 4: colours
    check(str(Defs.C_BAD) == "#ff6b6b" and str(Defs.C_OK) == "#39f493", "vanilla red / green")
    check(str(Defs.R_HEX[5]) == "#CC66CC" and str(Defs.R_PAGEHEX[5]) == "#CC66CC", "Mythic #CC66CC")
    zq = json.loads(zipfile.ZipFile(jar).read("Server/Item/Qualities/Skyy_Gear_Mythic.json").decode("utf-8"))
    check(zq["TextColor"] == "#cc66cc", "the Mythic quality asset TextColor")
    raw = zipfile.ZipFile(jar)
    for cn in ("GearGate", "IdentifyPage", "GearView", "ReforgePage"):
        b = raw.read("com/skyy/gear/%s.class" % cn)
        check(b"#ff9d6b" not in b and b"#FF5555" not in b and b"#55FF55" not in b, "%s has no old red / orange / green literal" % cn)
    print("F. colours done")

    # ---------------- G. design 5: Health Regen % only with Raw Health Regen
    check(str(Defs.S_LABEL[si("hprp")]) == "Health Regen %", "hprp label")
    w0 = [int(v) for v in Cfg.S_W]
    w = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        w[i] = 0
    w[si("hprp")] = 1000
    w[si("str")] = 1
    Cfg.S_W = w
    alone = 0
    for _ in range(300):
        ks = [str(m.asDocument().getString("s").getValue()) for m in Roll.rollMods(0, 5, 50)]
        if "hprp" in ks and "hpr" not in ks:
            alone += 1
    check(alone == 0, "hprp never rolls without hpr (hpr weight 0)")
    w[si("hpr")] = 1
    Cfg.S_W = w
    both = 0
    for _ in range(300):
        ks = [str(m.asDocument().getString("s").getValue()) for m in Roll.rollMods(0, 5, 50)]
        if "hprp" in ks:
            both += 1
            if "hpr" not in ks:
                alone += 1
    check(alone == 0 and both > 0, "hprp rolls after hpr (%d rolls had it)" % both)
    w2 = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        w2[i] = w0[i]
    Cfg.S_W = w2
    print("G. regen rule done")

    # ---------------- H. design 6 / 8 / 9 / 11
    check(str(View.suffix(si("mp"))) == " (spell attacks only)", "design 6: Magical Power suffix")
    for k in ("lbonus", "lquality", "stealing", "trophy", "xpb"):
        i = si(k)
        check(int(Defs.S_LIVE[i]) == 0 and int(Defs.S_WDEF[i]) == 2 and str(Defs.S_SLOT[i]) == "wa", "design 11: %s coming later, weight 2" % k)
    t = JArray(JInt)(int(Defs.NS))
    t[si("fFire")] = 6
    t[si("fAir")] = 2
    t[si("rElem")] = 3
    check(abs(float(Hit.hitAmount(10.0, t, False, 0.9, 0.9)) - 10.0) < 1e-9, "design 8: flat elements are not in the hit math")
    check(int(Hit.elemSum(t)) == 6 + 2 + 15, "design 8: elemSum = flats + 5 x Raw Elemental")
    t[si("cc")] = 100
    check(abs(float(Hit.hitAmount(10.0, t, False, 0.0, 0.9)) - 20.0) < 1e-9, "design 8: a crit doubles only the physical part")
    inf = Hit.info(U1, t)
    check(len(inf) == 6 and int(inf[5]) == 23, "design 8: info[5] carries the element sum for GearTrueSys")
    unid = Roll.newDoc("Weapon_Sword_Iron", 2, False, "drop")
    Cfg.IDENTIFY_CMD = False
    pl = " | ".join(str(s) for s in View.plain("Weapon_Sword_Iron", unid, None))
    check("Identify: at the identifier - " in pl and "/identify" not in pl, "design 9: tooltip text without /identify: " + pl)
    st = Data.put(IS("Weapon_Sword_Iron", 1), unid, U1)
    check(str(Forge.refuse(st, unid)) == "Identify it first", "design 9: reforge refusal without /identify")
    jb = Hit.judge(U1, st, False)
    check(jb is not None and str(jb[2]) == "Identify it first", "design 9: popup without /identify")
    Cfg.IDENTIFY_CMD = True
    pl = " | ".join(str(s) for s in View.plain("Weapon_Sword_Iron", unid, None))
    check("Identify: /identify - " in pl and str(Forge.refuse(st, unid)) == "Identify it first: /identify", "design 9: /identify when the command is on")
    print("H. texts done")

    # ---------------- L. engine 1: the lock never eats the current value
    plan = lambda have, want, raise_, eng, full: float(Fx.plan(JFloat(have), JFloat(want), raise_, JFloat(eng), JFloat(full)))
    check(plan(17, 0, False, 0, 0) == 0 and plan(17, 12.75, False, 17, 12.75) == 12.75, "plan: lowering is always done")
    check(plan(0, 17, False, 17, 17) == 0, "plan: never raises without raise (GearFxInvSys / GearLockSys)")
    check(plan(0, 17, True, 0, 17) == 0, "plan: no raise while the engine has not applied the piece")
    check(plan(0, 17, True, 17, 17) == 17 and plan(5, 17, True, 22, 22) == 17, "plan: raise once synced")
    check(str(Fx.armorKey()) == str(CAL.ADDITIVE.createKey("Armor")), "the engine's Armor key: %s" % Fx.armorKey())

    def sim(steps, base=100.0):
        """steps: list of (container_sum_full, inactive_sum, order). order = the sequence of passes for this change:
        'E' engine Recalculate (Armor := full), 'L' a lower-only pass (GearLockSys / GearFxInvSys), 'T' the 1 s tick (raise allowed).
        Returns the list of (value, steady max) after each change."""
        m = StatModel(base, base)
        lock = 0.0
        engine = 0.0
        out = []
        for full, inact, order in steps:
            for o in order:
                if o == "E":
                    engine = full
                    m.put("Armor", engine)
                else:
                    nxt = plan(lock, inact, o == "T", engine, full)
                    if nxt != lock:
                        lock = nxt
                        m.put("lock", -lock)
            out.append((m.value, base + full - inact))
        return out

    # the player starts full; a change is applied in the orders the engine can produce: the lower-only pass runs BEFORE
    # Recalculate (GearLockSys dependency) or at the latest from the armor change event; the tick comes after (next second)
    cases = {
        "equip an inactive +17 piece": [(0, 0, "ET"), (17, 17, "LET")],
        "unequip it": [(17, 17, "ET"), (0, 0, "LET")],
        "swap active +17 for inactive +17": [(17, 0, "ET"), (17, 17, "LET")],
        "swap inactive +17 for active +17": [(17, 17, "ET"), (17, 0, "LET")],
        "level up (inactive becomes active)": [(17, 17, "ET"), (17, 0, "T")],
        "class change (active becomes inactive)": [(17, 0, "ET"), (17, 17, "T")],
        "inactive piece breaks (x0.75)": [(17, 17, "ET"), (12.75, 12.75, "LET")],
        "two pieces, one inactive leaves": [(34, 17, "ET"), (17, 0, "LET")],
        "tick before the engine (equip)": [(0, 0, "ET"), (17, 17, "TLET")],
    }
    for name, steps in cases.items():
        res = sim(steps)
        ok_ = True
        for i, (v, steady) in enumerate(res):
            prev_v = res[i - 1][0] if i else 100.0
            # the value may only drop to the new steady max (vanilla behaviour for a lower max), never below it
            if v + 1e-6 < min(prev_v, steady):
                ok_ = False
        check(ok_, "engine 1 simulation keeps the current value: %s -> %s" % (name, res))
    # negative control: an unequipped piece whose lock shrinks only AFTER Recalculate loses the value - why GearLockSys is ordered
    # BEFORE EntityStatsSystems$Recalculate (and GearFxInvSys lowers too)
    late = sim([(17, 17, "ET"), (0, 0, "ELT")])
    check(late[1][0] == 83.0, "the model sees the loss when the lock shrinks after Recalculate: %s" % late)
    # the old order (lock raised on the change event, before Recalculate) loses current value: the simulation sees it
    old = StatModel(100.0, 100.0)
    old.put("lock", -17.0)
    old.put("Armor", 17.0)
    check(old.value == 83.0 and old.max() == 100.0, "the reviewed bug reproduces in the model (lock before Recalculate eats 17 HP)")
    # bytecode: GearFxInvSys never raises, GearFx.second raises, GearLockSys is lower-only, ordered BEFORE Recalculate
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendClassPath(B.SERVER_JAR)
    pool.appendSystemPath()

    def code(cls, meth):
        cc = pool.get(PKG + cls)
        out = []
        for mm in cc.getDeclaredMethods():
            if str(mm.getName()) == meth:
                bos = BOS()
                IP(PS(bos)).print_(mm)
                out += str(bos.toString()).splitlines()
        return out

    def before_call(lines, needle):
        for i, l in enumerate(lines):
            if needle in l:
                return lines[i - 1].strip()
        return ""

    fi = code("GearFxInvSys", "handle")
    check(before_call(fi, "GearFx.armorPass").endswith("iconst_0"), "GearFxInvSys: armorPass(..., raise = false)")
    se = code("GearFx", "second")
    check(before_call(se, "GearFx.armorPass").endswith("iconst_1"), "GearFx.second (1 s tick): armorPass(..., raise = true)")
    lo = code("GearFx", "lowerNow")
    check(before_call(lo, "GearFx.locks").endswith("iconst_0"), "GearFx.lowerNow: locks(..., raise = false)")
    lk = code("GearLockSys", "tick")
    check(any("GearFx.lowerNow" in l for l in lk) and not any("armorPass" in l for l in lk), "GearLockSys only lowers")
    LS = J("GearLockSys")
    Recalc = Cls.forName("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate", False, loader)
    LS.RECALC = Recalc
    deps = LS(True).getDependencies()
    dep = deps.iterator().next() if deps.size() == 1 else None
    check(dep is not None and str(dep.getOrder()) == "BEFORE" and str(dep.getSystemClass().getName()).endswith("EntityStatsSystems$Recalculate"),
          "GearLockSys is ordered BEFORE EntityStatsSystems$Recalculate")
    check(LS(False).getDependencies().size() == 0 and not bool(LS(True).isParallel(1, 1)), "unordered fallback has no dependency; not parallel")
    su = code("GearFx", "setup")
    check(any("EntityStatsSystems$Recalculate" in l for l in su) and any("GearLockSysU" in l for l in su), "setup orders GearLockSys + fallback")
    print("L. engine 1 done")

    # ---------------- M. engine 2: broken armor factor
    m = HashMap()
    a0 = JArray(SMO)(1)
    a0[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(17.0))
    a2 = JArray(SMO)(2)
    a2[0] = SMO(MTG.MAX, CAL.ADDITIVE, JFloat(5.0))
    a2[1] = SMO(MTG.MAX, CAL.MULTIPLICATIVE, JFloat(0.1))
    m.put(Integer.valueOf(0), a0)
    m.put(Integer.valueOf(2), a2)
    out = HashMap()
    Armor.addSums(m, True, JFloat(0.75), out, None)
    check(abs(float(out.get(Integer.valueOf(0))) - 12.75) < 1e-6 and abs(float(out.get(Integer.valueOf(2))) - 3.75) < 1e-6,
          "broken piece: amount x 0.75 (additive only): %s" % out)
    out = HashMap()
    Armor.addSums(m, False, JFloat(0.75), out, None)
    check(abs(float(out.get(Integer.valueOf(0))) - 17.0) < 1e-6 and abs(float(out.get(Integer.valueOf(2))) - 5.0) < 1e-6, "whole piece: full amount")
    a3 = JArray(SMO)(1)
    a3[0] = SMO(MTG.MIN, CAL.ADDITIVE, JFloat(4.0))
    m3 = HashMap()
    m3.put(Integer.valueOf(1), a3)
    out = HashMap()
    Armor.addSums(m3, False, JFloat(1.0), out, None)
    check(abs(float(out.get(Integer.valueOf(1))) - 4.0) < 1e-6, "every target counts (the engine puts every additive sum on MAX)")
    check(abs(float(Armor.brokenFactor(None)) - 1.0) < 1e-6, "no world -> factor 1")
    print("M. engine 2 done")

    # ---------------- N. engine 3: armor in the hand is not a weapon
    ua = Data.put(IS("Armor_Iron_Chest", 1), Roll.newDoc("Armor_Iron_Chest", 3, False, "drop"), U1)
    check(Hit.judge(U1, ua, False) is None and Hit.judge(U1, ua, True) is None, "unidentified armor in hand / utility is never judged")
    check(Hit.judge(U1, st, False) is not None, "an unidentified weapon still blocks")
    print("N. engine 3 done")

    # ---------------- O. engine 4: quality indices
    pq = Props()
    pq.setProperty("Skyy_Gear_Normal", "40")
    pq.setProperty("Skyy_Gear_Rare", "42")
    q = Qual.parse(pq)
    check(q is not None and int(q[0]) == 40 and int(q[1]) == -1 and int(q[2]) == 42, "quality.properties parse")
    check(Qual.parse(Props()) is None, "an empty file = no indices")
    now = JArray(JInt)(7)
    for i in range(7):
        now[i] = 40 + i
    check(not bool(Qual.differs(q, now)), "same indices -> not moved")
    now[2] = 50
    check(bool(Qual.differs(q, now)) and not bool(Qual.differs(None, now)), "a moved index is seen; no file = not moved")
    qf = os.path.join(SCRATCH, "work", "Skyy_SkyyGear", "quality.properties")
    os.makedirs(os.path.dirname(qf), exist_ok=True)
    open(qf, "w").write("Skyy_Gear_Normal=40\nSkyy_Gear_Unique=41\nSkyy_Gear_Rare=42\n")
    Qual.load(Paths.get(qf))
    check(bool(Qual.wasOurs(41)) and not bool(Qual.wasOurs(7)), "wasOurs = an index of the last start")
    ep = int(Cfg.EPOCH)
    Qual.CHECKED = False
    Qual.check(now)
    # follow-up review 7 (changed check): no epoch bump any more - GearView.apply rewrites a stack whose quality index moved
    check(bool(Qual.MOVED) and int(Cfg.EPOCH) == ep, "moved indices: WARN, the config epoch stays (GearView.apply rewrites effQ != curQ)")
    J("GearQual")(Qual.text(now)).run()
    txtq = open(qf).read()
    check("Skyy_Gear_Rare=50" in txtq and "Skyy_Gear_Mythic=45" in txtq, "quality.properties rewritten with today's indices")
    check(bool(Defs.validQ(Integer.MIN_VALUE)) and not bool(Defs.validQ(5)) and not bool(Defs.validQ(-3)), "validQ: own ok, unknown index not")
    check(str(Defs.qName(Integer.MIN_VALUE)) == "own", "sig names the quality, never the raw index")
    doc = Roll.newDoc("Weapon_Sword_Iron", 1, True, "admin")
    good = Data.put(IS("Weapon_Sword_Iron", 1), doc, U1)
    stale = good.withQuality(5)
    fixed = View.apply(stale, doc, U1)
    ident = JClass("java.lang.System").identityHashCode
    check(int(fixed.getQualityIndex()) == int(good.getQualityIndex()) and ident(fixed) != ident(stale),
          "a stack whose quality index resolves to nothing is rewritten to the item's own quality (%s)" % fixed.getQualityIndex())
    check(ident(View.apply(fixed, doc, U1)) == ident(fixed), "and stays put afterwards (no rewrite loop)")
    check(ident(View.apply(good, doc, U1)) == ident(good), "a correct stack is left alone (same object)")
    print("O. engine 4 done")

    # ---------------- P. engine 5: armor container only
    check(any("InventoryChangeEvent.getItemContainer" in l for l in fi) and any("InventoryChangeEvent.getInventory" in l for l in fi)
          and any("Inventory.getArmor" in l for l in fi), "GearFxInvSys checks the event's container against the armor container")
    ia = [i for i, l in enumerate(fi) if "getItemContainer" in l]
    ap = [i for i, l in enumerate(fi) if "GearFx.armorPass" in l]
    check(ia and ap and ia[0] < ap[0], "the container check comes before the armor pass")
    print("P. engine 5 done")

    # ---------------- Q. engine 6: GearLog outside its lock
    Mod = JClass("java.lang.reflect.Modifier")
    LogC = Cls.forName(PKG + "GearLog", False, loader)
    msync = lambda n: bool(Mod.isSynchronized([x for x in LogC.getDeclaredMethods() if str(x.getName()) == n][0].getModifiers()))
    check(not msync("flush") and msync("take") and msync("kick") and not msync("write"), "flush / write unsynchronized, take / kick hold the monitor")
    lf = os.path.join(SCRATCH, "work", "gear.log")
    Log.FILE = Paths.get(lf)
    WL = Log.WLOCK
    holding = {"on": False}

    @JImplements("java.lang.Runnable")
    class Hold:
        @JOverride
        def run(self):
            with jpype.synchronized(WL):
                holding["on"] = True
                time.sleep(1.2)
            holding["on"] = False

    th = JClass("java.lang.Thread")(Hold())
    th.start()
    for _ in range(50):
        if holding["on"]:
            break
        time.sleep(0.02)
    t0 = time.time()
    Log.line("REVIEW-TEST one")
    Log.line("REVIEW-TEST two")
    s_ = str(Log.take())
    dt_ = time.time() - t0
    check(holding["on"] and dt_ < 0.5 and "REVIEW-TEST one" in s_ and "REVIEW-TEST two" in s_,
          "line() + take() never wait for the disk lock (%.3f s while WLOCK is held)" % dt_)
    Log.line("REVIEW-TEST three")
    t0 = time.time()
    Log.flush()
    dt2 = time.time() - t0
    th.join()
    check(dt2 > 0.2, "flush() writes under WLOCK (it waited %.3f s)" % dt2)
    check(os.path.isfile(lf) and "REVIEW-TEST three" in open(lf).read(), "gear.log written")
    Log.FILE = None
    print("Q. engine 6 done")

    # ---------------- R. engine 7: writeAtomic
    wf = os.path.join(SCRATCH, "work", "atomic", "a.properties")
    if os.path.exists(wf):
        os.remove(wf)
    Cfg.writeAtomic(Paths.get(wf), "x=1\n", False)
    Cfg.writeAtomic(Paths.get(wf), "x=2\n", False)
    check(open(wf).read() == "x=1\n", "replace = false never overwrites an existing file")
    Cfg.writeAtomic(Paths.get(wf), "x=3\n", True)
    check(open(wf).read() == "x=3\n" and not os.path.exists(wf + ".tmp"), "replace = true writes, no temp file left")
    wa = code("GearCfg", "writeAtomic")
    check(any("ATOMIC_MOVE" in l for l in wa) and any("REPLACE_EXISTING" in l for l in wa), "writeAtomic moves with ATOMIC_MOVE + REPLACE_EXISTING")
    check(any("FileDescriptor.sync" in l for l in wa) and any("getFD" in l for l in wa), "writeAtomic fsyncs the temp file first")
    print("R. engine 7 done")

    # ---------------- S. exploit 1: newest launch record
    Track.SHOTS.clear()
    bowA, bowB, bowC = IS("Weapon_Shortbow_Crude", 1), IS("Weapon_Shortbow_Iron", 1), IS("Weapon_Shortbow_Copper", 1)
    ms_ = int(JClass("java.lang.System").currentTimeMillis())
    for key, bow, age, who in (("a", bowA, 5000, U1), ("b", bowB, 1000, U1), ("c", bowC, 20000, U1), ("d", bowC, 100, U2)):
        r = Shot(who, bow, None, None)
        r.at = ms_ - age
        Track.SHOTS.put(UUID.nameUUIDFromBytes(key.encode()), r)
    nw = Track.newest(U1)
    check(nw is not None and str(nw.main.getItemId()) == "Weapon_Shortbow_Iron", "newest live record of that shooter (not another player's)")
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"b"))
    check(str(Track.newest(U1).main.getItemId()) == "Weapon_Shortbow_Crude", "an older live record next")
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"a"))
    check(Track.newest(U1) is None, "a record outside the 10 s window never counts")
    Track.SHOTS.clear()
    hs = code("GearHitSys", "handle")
    # follow-up review 4 (changed check): GearHitSys now asks GearShotTrack.pick (newest, or the weaker weapon), not newest()
    # (review of 0.2.1 finding 1: pickFor = pick's rule over the records of the weapon that owns the hit's damage step, calcOf(d))
    check(any("GearShotTrack.pickFor" in l for l in hs) and any("GearShotTrack.calcOf" in l for l in hs) and any("GearHit.family" in l for l in hs)
          and not any("GearShotTrack.pick(" in l for l in hs), "GearHitSys takes projectile hits from pickFor(calcOf(d))")
    print("S. exploit 1 done")

    # ---------------- T. exploit 2: per-item rolls / stamps
    # (follow-up review 3: split takes a floor argument - 0 here, the player floor is tested in W; give = storage, backpack)
    hot, sto, bak = SIC(9), SIC(36), SIC(9)
    give = JArray(IC)([sto, bak])
    alls = JArray(IC)([hot, sto, bak])
    hot.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 3))
    moved = int(Stamp.split(hot, 0, give, alls, U1, 0, 64, 0, None))
    s0, s1, s2 = hot.getItemStack(0), sto.getItemStack(0), sto.getItemStack(1)
    check(moved == 2 and int(s0.getQuantity()) == 1 and s1 is not None and int(s1.getQuantity()) == 1 and int(s2.getQuantity()) == 1,
          "a stack of 3 spears -> the slot keeps 1, two singles go to storage first")
    check(int(Stamp.countId(alls, "Weapon_Spear_Crude")) == 3, "counted before / after: still 3 spears")
    d1, d2 = Data.gearDoc(s1.getMetadata()), Data.gearDoc(s2.getMetadata())
    check(d1 is not None and d2 is not None and d1.containsKey("k") and d2.containsKey("k") and str(d1.toJson()) != str(d2.toJson()),
          "each split single has its own document with a nonce (they never stack again)")
    check(not bool(s1.isStackableWith(s2)), "two split singles are not stackable")
    # full inventory: nothing moves, the stack stays whole
    fh, fs = SIC(2), SIC(2)
    fs.setItemStackForSlot(0, IS("Ingredient_Stick", 1))
    fs.setItemStackForSlot(1, IS("Ingredient_Stick", 1))
    fh.setItemStackForSlot(1, IS("Ingredient_Stick", 1))
    fh.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    moved = int(Stamp.split(fh, 0, JArray(IC)([fs, fh]), JArray(IC)([fh, fs]), U1, 0, 64, 0, None))
    check(moved == 0 and int(fh.getItemStack(0).getQuantity()) == 5, "full inventory: the stack stays whole (never dropped)")
    fs.setItemStackForSlot(1, None)
    moved = int(Stamp.split(fh, 0, JArray(IC)([fs, fh]), JArray(IC)([fh, fs]), U1, 0, 64, 0, None))
    check(moved == 1 and int(fh.getItemStack(0).getQuantity()) == 4 and int(Stamp.countId(JArray(IC)([fh, fs]), "Weapon_Spear_Crude")) == 5,
          "one free slot: one single moves, the rest stays one stack, count unchanged")
    # an unidentified stack: every single keeps the rarity, stays unidentified
    uh, us = SIC(3), SIC(9)
    ud = Roll.unidDoc("Weapon_Spellbook_Frost", 1, "drop")
    ud.put("r", JClass("org.bson.BsonString")("rare"))
    uh.setItemStackForSlot(0, Data.put(IS("Weapon_Spellbook_Frost", 4), ud, None))
    moved = int(Stamp.split(uh, 0, JArray(IC)([us, uh]), JArray(IC)([uh, us]), U1, 0, 64, 0, None))
    docs = [Data.gearDoc(us.getItemStack(i).getMetadata()) for i in range(3)]
    check(moved == 3 and all(dd is not None and not bool(Data.identified(dd)) and int(Data.rarity(dd)) == 2 for dd in docs),
          "an unidentified stack of 4 -> 4 unidentified Rare singles")
    # crafted output: every item rolls; a stack bigger than the craft count is never rolled as one
    ch, cs_ = SIC(9), SIC(36)
    ch.setItemStackForSlot(2, IS("Weapon_Spear_Crude", 3))
    got = JClass("java.lang.StringBuilder")()
    n = int(CraftTask.rollIn(JArray(IC)([ch, cs_]), JArray(IC)([cs_]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, got))
    rolled = [x for x in [ch.getItemStack(2)] + [cs_.getItemStack(i) for i in range(4)] if x is not None and not x.isEmpty()]
    srcs = [str(Data.gearDoc(x.getMetadata()).getString("src").getValue()) for x in rolled]
    check(n == 3 and len(rolled) == 3 and all(int(x.getQuantity()) == 1 for x in rolled) and srcs == ["craft"] * 3,
          "Weapon_Spear_Crude outputs 3 -> 3 rolled singles (%d, %s, got%s)" % (n, srcs, got))
    ch2, cs2 = SIC(9), SIC(36)
    ch2.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    n = int(CraftTask.rollIn(JArray(IC)([ch2, cs2]), JArray(IC)([cs2]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None))
    check(n == 0 and int(ch2.getItemStack(0).getQuantity()) == 5 and not bool(Data.hasAnyDoc(ch2.getItemStack(0).getMetadata())),
          "a merged stack of 5 for a craft of 3 is never rolled as one (q > cap - n)")
    # loot chest: per-item unidentified documents inside the same chest
    Cfg.PART_CHESTS = True
    chest = SIC(27)
    chest.setItemStackForSlot(0, IS("Weapon_Spellbook_Demon", 5))
    tagged = int(Tag.tagContainer(chest, "test"))
    items = [chest.getItemStack(i) for i in range(27) if chest.getItemStack(i) is not None and not chest.getItemStack(i).isEmpty()]
    check(len(items) == 5 and all(int(x.getQuantity()) == 1 and not bool(Data.identified(Data.gearDoc(x.getMetadata()))) for x in items)
          and tagged == 5, "a loot chest stack of 5 spellbooks -> 5 unidentified singles (%d tagged)" % tagged)
    # Identify all skips a refused row and goes on
    coins = {"take": 0}

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, o):
            coins["take"] += 1
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class Purse:
        @JOverride
        def apply(self, o):
            return JLong(10 ** 9)

    bridge.put("coins:fn:take", Take())
    bridge.put("coins:fn:get", Purse())
    bridge.put("coins:fn:add", Purse())
    ih = SIC(9)
    ud2 = Roll.unidDoc("Weapon_Sword_Iron", 1, "drop")
    ih.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 2), Roll.unidDoc("Weapon_Spear_Crude", 1, "drop"), None))
    ih.setItemStackForSlot(1, Data.put(IS("Weapon_Sword_Iron", 1), ud2, None))
    by = JArray(IC)(6)
    by[0] = ih
    rows = ArrayList()
    for sl in (0, 1):
        rr = JArray(JInt)(2)
        rr[0] = 0
        rr[1] = sl
        rows.add(rr)
    rec = ArrayList()
    res = Ident.allIn(by, rows, U1, "tester", rec)
    # follow-up review 3 (changed check): a stack is no longer refused as such - with no storage / backpack room (none here) it
    # cannot give up one item: "Free 6 slots to split this stack"
    check(int(res[0]) == 1 and int(res[2]) == 1 and res[4] is None and "Free 6 slots to split this stack" in str(res[3]),
          "Identify all: the stack row without room is skipped, the next item is identified (%s)" % [str(x) for x in res])
    check(bool(Data.identified(Data.gearDoc(ih.getItemStack(1).getMetadata()))) and coins["take"] == 1, "exactly one paid identify")
    print("T. exploit 2 done")

    # ---------------- W. follow-up review of the fix commit e43c8bf
    BA_, BS_, BI_ = JClass("org.bson.BsonArray"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    amf = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_.getDeclaredField("assetMap")
    amf.setAccessible(True)
    idf = ItemC.class_.getDeclaredField("id")
    idf.setAccessible(True)
    msf = ItemC.class_.getDeclaredField("maxStack")
    msf.setAccessible(True)
    unsafe = uf.get(None)             # (section T reuses the name us for a container)

    def fake_item(iid, ms):
        """an Item asset with only an id + MaxStack (never constructed, like the fake store) so GearData.maxStack sees it"""
        it_ = unsafe.allocateInstance(ItemC.class_)
        idf.set(it_, iid)
        msf.setInt(it_, ms)
        amf.get(store.getAssetMap()).put(iid, it_)

    def with_mods(iid, pairs):
        dd = Roll.newDoc(iid, 0, True, "admin")
        arr = BA_()
        for k, v in pairs:
            md = BD()
            md.append("s", BS_(k))
            md.append("v", BI_(v))
            arr.add(md)
        dd.put("mods", arr)
        return dd

    def qty(c, i):
        s_ = c.getItemStack(i)
        return 0 if s_ is None or s_.isEmpty() else int(s_.getQuantity())

    FREE = int(Defs.FREE_KEEP)
    check(FREE == 5 and int(Defs.STACK_CEIL) == 30, "follow-up constants: 5 free slots, split ceiling MaxStack 30")

    # 1. gear.include guard
    for bad in ("Skyy_", "Weapon_", "Armor_", "Tool_", "skyy_", "Wea", "Sky"):
        check(Cfg.checkInclude("gear.include", "Skyy_Ring_," + bad) is not None, "W1: gear.include refuses %r" % bad)
    check(Cfg.checkInclude("gear.include", "Skyy_Ring_, Tool_Pickaxe_,Weapon_Arrow_") is None and Cfg.checkInclude("gear.include", "") is None
          and Cfg.checkInclude("gear.include", None) is None, "W1: narrow prefixes (6+ characters) pass the check")
    check(any("checkInclude" in str(x) for x in Rows.BCHECK), "W1: the gear.include row binds the check hook")
    check("6+" in helps["gear.include"], "W1: the row help names the 6-character rule")
    p = Props()
    p.setProperty("gear.include", "Skyy_,Weapon_,Wea,Skyy_Talisman_,Weapon_Arrow_,Skyy_Cook_Food_,Weapon_Knife_")
    Cfg.apply(p, False)
    check([str(x) for x in Cfg.incl()] == ["Skyy_Talisman_", "Weapon_Arrow_", "Skyy_Cook_Food_", "Weapon_Knife_"],
          "W1: the loader drops refused entries from a hand edit: %s" % [str(x) for x in Cfg.incl()])
    check(not any(bool(Data.isGear(x)) for x in ("Skyy_Menu", "Skyy_Market", "Skyy_Vault_Small", "Skyy_Accessory_Omni")),
          "W1: a bare Skyy_ entry pulls nothing in (menu, market, vault, accessory)")
    check(not bool(Data.isGear("Weapon_Arrow_Iron")) and not bool(Data.isGearMs("Weapon_Arrow_Iron", 40)) and not bool(Data.isGearMs("Weapon_Arrow_Iron", 1)),
          "W1: include never beats the ammo rule (Weapon_Arrow_ included, arrows stay ammo)")
    tal = "Skyy_Talisman_Luck"
    check(bool(Data.isGear(tal)) and str(Data.kindFor(tal)) == "equipment" and int(Data.slotOf(tal)) == 4,
          "W1: an included non-family id without a kind.prefix row is kind equipment (slot 4)")
    tst = Data.put(IS(tal, 1), Roll.newDoc(tal, 2, False, "drop"), U1)
    check(Hit.judge(U1, tst, False) is None and Hit.judge(U1, tst, True) is None, "W1: an unidentified included talisman never blocks a hit")
    check(not bool(Data.isGearMs("Skyy_Cook_Food_Pie", 64)) and not bool(Data.isGearMs(tal, 5)),
          "W1: an included id that stacks is gear only in Weapon_ / Armor_ / Tool_")
    check(not bool(Data.isGearMs("Weapon_Knife_Throw", 40)) and bool(Data.isGearMs("Weapon_Knife_Throw", 20)) and bool(Data.isGearMs("Weapon_Knife_Throw", 1)),
          "W1: an included family id is gear up to MaxStack 30, never above")
    fake_item("Skyy_Cook_Food_Pie", 64)
    fake_item("Weapon_Knife_Throw", 40)
    check(int(Data.maxStack("Skyy_Cook_Food_Pie")) == 64 and int(Data.maxStack("Nope_Item")) == -1, "W1: maxStack reads the Item asset (-1 = none)")
    check(not bool(Data.isGear("Skyy_Cook_Food_Pie")) and not bool(Data.isGear("Weapon_Knife_Throw")),
          "W1: through the asset: included food (64) and an included Weapon_ above 30 stay plain items")
    Cfg.apply(Props(), False)

    # 2. MaxStack ammo rule + split ceiling
    check(not bool(Data.ammoMs("Weapon_Shortbow_Bomb", 1)) and bool(Data.ammoMs("Weapon_Shortbow_Bomb", 20)),
          "W2: parts[1] rule only for single items; a stackable id keeps the any-token test")
    check(bool(Data.ammoMs("Weapon_Arrow_Iron", 40)) and bool(Data.ammoMs("Weapon_Arrow_Iron", 1)) and not bool(Data.ammoMs("Weapon_Spear_Iron", 30)),
          "W2: arrows are ammo either way, spears (30) are not")
    fake_item("Weapon_Knife_Stack", 40)
    fake_item("Weapon_Knife_Small", 20)
    check(bool(Data.isGear("Weapon_Knife_Stack")), "W2: a stackable Weapon_ id above 30 is still gear (gear.exclude decides)")
    kh, ks = SIC(3), SIC(9)
    kh.setItemStackForSlot(0, IS("Weapon_Knife_Stack", 10))
    m40 = int(Stamp.split(kh, 0, JArray(IC)([ks]), JArray(IC)([kh, ks]), U1, 0, 64, 0, None))
    check(m40 == 0 and qty(kh, 0) == 10 and all(qty(ks, i) == 0 for i in range(9)), "W2: split skips an id with MaxStack 40 (stack untouched)")
    kh.setItemStackForSlot(1, IS("Weapon_Knife_Small", 3))
    m20 = int(Stamp.split(kh, 1, JArray(IC)([ks]), JArray(IC)([kh, ks]), U1, 0, 64, 0, None))
    check(m20 == 2 and qty(kh, 1) == 1, "W2: an id with MaxStack 20 still splits (%d)" % m20)

    # 3. no hotbar, 5-slot floor, no passive split, actions take one item off a stack
    gv = code("GearStamp", "giveOf")
    check(any("Inventory.getStorage" in l for l in gv) and any("Inventory.getBackpack" in l for l in gv) and not any("getHotbar" in l for l in gv),
          "W3: giveOf = storage + backpack, never the hotbar")
    sc = code("GearStamp", "scan")
    check(not any("GearStamp.split" in l for l in sc) and not any("takeOne" in l for l in sc), "W3: the passive scan never splits")
    fc, fsto = SIC(9), SIC(6)
    fc.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 3))
    nf = int(CraftTask.rollIn(JArray(IC)([fc, fsto]), JArray(IC)([fsto]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None))
    check(nf == 1 and qty(fc, 0) == 2 and sum(1 for i in range(6) if qty(fsto, i) == 0) == 5
          and not bool(Data.hasAnyDoc(fc.getItemStack(0).getMetadata())),
          "W3: craft rolls keep the 5-slot floor (6 free: one rolled single, the stack of 2 stays unrolled)")
    h3, s3 = SIC(9), SIC(7)
    h3.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 5))
    mv3 = int(Stamp.split(h3, 0, JArray(IC)([s3]), JArray(IC)([h3, s3]), U1, 1, 4, FREE, None))
    free3 = sum(1 for i in range(7) if qty(s3, i) == 0)
    check(mv3 == 2 and qty(h3, 0) == 3 and free3 == 5 and all(qty(h3, i) == 0 for i in range(1, 9))
          and int(Stamp.countId(JArray(IC)([h3, s3]), "Weapon_Spear_Crude")) == 5,
          "W3: 7 free storage slots -> 2 singles, 5 stay free, nothing lands in the hotbar (%d moved)" % mv3)
    sp3 = IS("Weapon_Spear_Crude", 3)
    st3 = Stamp.stampStack(sp3, U1, None)
    d3 = Data.gearDoc(st3.getMetadata())
    check(int(st3.getQuantity()) == 3 and d3 is not None and int(Data.rarity(d3)) == 0, "W3: the passive stamp keeps a stack of identical items whole")
    check(Stamp.stackWhy(IS("Weapon_Spear_Crude", 1), JArray(IC)([]), "identify") is None
          and str(Stamp.stackWhy(sp3, JArray(IC)([SIC(4)]), "identify")) == "Free 2 slots to split this stack - identify works on one item at a time."
          and Stamp.stackWhy(sp3, JArray(IC)([SIC(6)]), "identify") is None, "W3: stackWhy needs 6 free slots (1 + the 5 kept free)")
    coins["take"] = 0
    ud3 = Roll.unidDoc("Weapon_Spear_Crude", 1, "drop")
    ud3.put("r", BS_("rare"))
    ih3, is3 = SIC(9), SIC(9)
    ih3.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    it3 = ih3.getItemStack(0)
    r3 = Ident.identify(ih3, 0, "Weapon_Spear_Crude", Forge.fp(it3), U1, "tester", False, JArray(IC)([is3, None]), JArray(IC)([ih3, is3]))
    rest3 = Data.gearDoc(is3.getItemStack(0).getMetadata()) if qty(is3, 0) else None
    check(int(r3[0]) == 1 and qty(ih3, 0) == 1 and bool(Data.identified(Data.gearDoc(ih3.getItemStack(0).getMetadata())))
          and qty(is3, 0) == 2 and rest3 is not None and not bool(Data.identified(rest3)) and int(Data.rarity(rest3)) == 2
          and coins["take"] == 1 and r3[6] is not None and int(r3[6][1]) == 0,
          "W3: Identify on a stack of 3 identifies one item in place, the other 2 move on unidentified, paid once (%s)" % str(r3[1]))
    ih4, is4 = SIC(9), SIC(5)
    ih4.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    it4 = ih4.getItemStack(0)
    r4 = Ident.identify(ih4, 0, "Weapon_Spear_Crude", Forge.fp(it4), U1, "tester", False, JArray(IC)([is4]), JArray(IC)([ih4, is4]))
    check(int(r4[0]) == 0 and str(r4[1]) == "Free 1 slot to split this stack - identify works on one item at a time." and qty(ih4, 0) == 3
          and coins["take"] == 1, "W3: no room -> refused before any coin moves, the stack is untouched (%s)" % str(r4[1]))
    rh, rs5 = SIC(9), SIC(9)
    rh.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 2), with_mods("Weapon_Spear_Crude", [("dmg", 3)]), U1))
    r5 = Forge.reforge(rh, 0, "Weapon_Spear_Crude", Forge.fp(rh.getItemStack(0)), U1, "tester", True, JArray(IC)([rs5]), JArray(IC)([rh, rs5]))
    check(int(r5[0]) == 1 and qty(rh, 0) == 1 and qty(rs5, 0) == 1 and int(Stamp.countId(JArray(IC)([rh, rs5]), "Weapon_Spear_Crude")) == 2,
          "W3: Reforge on a stack of 2 reforges one item, the other moves to a free slot (%s)" % str(r5[1]))
    ah, as_ = SIC(9), SIC(9)
    ah.setItemStackForSlot(0, Data.put(IS("Weapon_Spear_Crude", 3), ud3, None))
    ah.setItemStackForSlot(1, Data.put(IS("Weapon_Sword_Iron", 1), Roll.unidDoc("Weapon_Sword_Iron", 1, "drop"), None))
    by2 = JArray(IC)(6)
    by2[0] = ah
    by2[1] = as_
    rows2 = ArrayList()
    for sl in (0, 1):
        rr = JArray(JInt)(2)
        rr[0] = 0
        rr[1] = sl
        rows2.add(rr)
    coins["take"] = 0
    res2 = Ident.allIn(by2, rows2, U1, "tester", ArrayList())
    left = [x for c_ in (ah, as_) for i in range(9) for x in [c_.getItemStack(i)] if x is not None and not x.isEmpty()]
    check(int(res2[0]) == 4 and int(res2[2]) == 0 and coins["take"] == 4 and len(left) == 4 and all(int(x.getQuantity()) == 1 for x in left)
          and all(bool(Data.identified(Data.gearDoc(x.getMetadata()))) for x in left),
          "W3: Identify all works a stack of 3 item by item (4 paid identifies, 4 identified singles) %s" % [str(x) for x in res2])

    # 4. projectile attribution
    Track.SHOTS.clear()
    ms_ = int(JClass("java.lang.System").currentTimeMillis())
    strong = Data.put(IS("Weapon_Shortbow_Crude", 1), with_mods("Weapon_Shortbow_Crude", [("dmg", 20), ("str", 10)]), U1)
    weak = Data.put(IS("Weapon_Shortbow_Crude", 1), with_mods("Weapon_Shortbow_Crude", [("dmg", 2)]), U1)
    ra, rb = Shot(U1, strong, None, None), Shot(U1, weak, None, None)
    ra.at, rb.at = ms_ - 1000, ms_ - 3000
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wa"), ra)
    check(str(Forge.fp(Track.pick(U1, None).main)) == str(Forge.fp(strong)), "W4: one live record -> that record")
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wb"), rb)
    check(str(Forge.fp(Track.newest(U1).main)) == str(Forge.fp(strong)) and str(Forge.fp(Track.pick(U1, None).main)) == str(Forge.fp(weak)),
          "W4: two live records with different weapons -> the WEAKER one, not the newest")
    rc = Shot(U1, strong, None, None)
    rc.at = ms_ - 500
    Track.SHOTS.remove(UUID.nameUUIDFromBytes(b"wb"))
    Track.SHOTS.put(UUID.nameUUIDFromBytes(b"wc"), rc)
    pk = Track.pick(U1, None)
    check(pk is not None and int(pk.at) == int(rc.at), "W4: the same weapon twice -> the newest record")
    Track.SHOTS.clear()
    check(Track.pick(U1, None) is None, "W4: no live record -> none")
    check(any("norecord" in l for l in hs) and any("Gear.warnOnce" in l for l in hs), "W4: a projectile hit without a record logs one WARN")

    # 5 / 6. saved locks + the Recalculate nudge (bytecode)
    lt = code("GearLockSys", "tick")
    check(any("GearFx.PRIMED" in l for l in lt) and any("GearFx.hasLock" in l for l in lt), "W5: GearLockSys looks once for saved lock modifiers")
    ga = code("GearReady", "accept")
    check(any("GearFx.PRIMED" in l for l in ga), "W5: PlayerReady (join / world switch) clears PRIMED")
    check(any("GearFx.PRIMED" in l for l in code("GearFx", "forget")), "W5: disconnect forgets PRIMED")
    hl = code("GearFx", "hasLock")
    check(any("EntityStatMap.getModifier" in l for l in hl) and not bool(Fx.hasLock(None)), "W5: hasLock reads the lock modifiers (null map = none)")
    lk2 = code("GearFx", "locks")
    check(any("getStatModifiersManager" in l for l in lk2) and any("StatModifiersManager.scheduleRecalculate" in l for l in lk2),
          "W6: a lock that keeps waiting asks the engine for a Recalculate")

    # 7. unreadable quality.properties is left alone
    open(qf, "w").write("Skyy_Gear_Normal=forty\nSkyy_Gear_Rare=42\n")
    Qual.load(Paths.get(qf))
    Qual.CHECKED = False
    Qual.check(now)
    J("GearQual")(Qual.text(now)).run()
    time.sleep(0.4)
    check(bool(Qual.UNREAD) and Qual.OLD is None and open(qf).read() == "Skyy_Gear_Normal=forty\nSkyy_Gear_Rare=42\n",
          "W7: an unreadable quality.properties is never overwritten")
    open(qf, "w").write("")
    Qual.load(Paths.get(qf))
    check(not bool(Qual.UNREAD), "W7: an empty file is not 'unreadable' (it may be rewritten)")

    # 8. a throwing destination restores the source
    CtC = JClass("javassist.CtNewConstructor")
    CtM = JClass("javassist.CtNewMethod")
    tb = jp.makeClass("com.hypixel.hytale.server.core.inventory.container.SkyyTestThrowBox",
                      jp.get("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"))
    tb.addConstructor(CtC.make("public SkyyTestThrowBox(short n) { super(n); }", tb))
    tb.addMethod(CtM.make("public com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction setItemStackForSlot(short s, "
                          "com.hypixel.hytale.server.core.inventory.ItemStack st) { throw new IllegalStateException(\"test: no writes\"); }", tb))
    ThrowBox = JClass(tb.toClass(SIC.class_).getName())
    from jpype import JShort
    dstb = ThrowBox(JShort(9))
    srcb = SIC(3)
    srcb.setItemStackForSlot(0, IS("Weapon_Spear_Crude", 4))
    both = JArray(IC)([srcb, dstb])
    mv8 = int(Stamp.split(srcb, 0, JArray(IC)([dstb]), both, U1, 0, 64, 0, None))
    check(mv8 == 0 and qty(srcb, 0) == 4 and int(Stamp.countId(both, "Weapon_Spear_Crude")) == 4, "W8: split - destination write throws -> the source is restored")
    t8 = Stamp.takeOne(srcb, 0, JArray(IC)([dstb]), both, U1)
    check(t8 is None and qty(srcb, 0) == 4 and int(Stamp.countId(both, "Weapon_Spear_Crude")) == 4, "W8: takeOne - destination write throws -> the source is restored")
    tg = code("GearTag", "tagContainer")
    check(any("chestsplit" in l for l in tg), "W8: tagContainer catches its own split")

    # 9. gear:extra saturation, Damage % floor, hit never below 0
    xs = Stats.parseExtra(",".join(["str:1000000"] * 3000) + ",dmg:-500,cd:-400")
    check(int(xs[si("str")]) == 1000000 and int(xs[si("dmg")]) == -500, "W9: 3000 parts of str:1000000 saturate at 1,000,000 (no wrap)")
    t9 = JArray(JInt)(int(Defs.NS))
    t9[si("dmg")] = -500
    check(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) == 0.0, "W9: Damage % below -100 counts as -100 (hit 0, never negative)")
    t9[si("dmg")] = -50
    check(abs(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) - 5.0) < 1e-9, "W9: Damage -50 % halves the hit")
    t9[si("dmg")] = 0
    t9[si("str")] = -1000
    check(float(Hit.hitAmount(10.0, t9, False, 0.9, 0.9)) == 0.0, "W9: negative Strength never makes a hit negative")
    t9[si("str")] = 0
    t9[si("cc")] = 100
    t9[si("cd")] = -400
    check(float(Hit.hitAmount(10.0, t9, False, 0.0, 0.9)) == 0.0, "W9: a negative crit multiplier floors at 0")
    t9 = JArray(JInt)(int(Defs.NS))
    t9[si("rElem")] = 1000000000
    t9[si("fFire")] = 1000000000
    check(int(Hit.elemSum(t9)) == 1000000000, "W9: elemSum saturates")
    bridge.put("gear:extra:" + str(U2), "str:1000000")
    top9 = Data.put(IS("Weapon_Sword_Crude", 1), with_mods("Weapon_Sword_Crude", [("str", 2147483000)]), U2)
    t10 = Stats.totals(U2, top9, None, None, True)
    check(int(t10[si("str")]) == 1000000000, "W9: gear + gear:extra totals saturate instead of wrapping (%d)" % int(t10[si("str")]))
    bridge.remove("gear:extra:" + str(U2))

    # 10. negative armor sums cancelled (signed plan)
    check(plan(0, -5, False, 0, 0) == -5, "W10: a negative sum is cancelled at once (+5 max = safe)")
    check(plan(-5, 0, False, -5, 0) == -5 and plan(-5, 0, True, -5, 0) == -5 and plan(-5, 0, True, 0, 0) == 0,
          "W10: taking a negative cancel away waits for the tick + the synced engine")
    check(plan(-5, 12, True, 7, 7) == 12, "W10: a mixed sum grows like a positive one once synced")
    neg = {
        "equip an inactive -5 piece": [(0, 0, "ET"), (-5, -5, "LET")],
        "unequip an inactive -5 piece": [(-5, -5, "LET"), (0, 0, "LET")],
        "level up: inactive -5 becomes active": [(-5, -5, "LET"), (-5, 0, "T")],
        "class change: active -5 becomes inactive": [(-5, 0, "LET"), (-5, -5, "T")],
        "tick before the engine (unequip -5)": [(-5, -5, "LET"), (0, 0, "TLET")],
        "inactive +17 and -5 on one stat (sum +12), unequip the -5": [(12, 12, "LET"), (17, 17, "LET")],
    }
    for name, steps in neg.items():
        res = sim(steps)
        ok_ = True
        for i, (v, steady) in enumerate(res):
            prev_v = res[i - 1][0] if i else 100.0
            if v + 1e-6 < min(prev_v, steady):
                ok_ = False
        check(ok_, "W10 simulation keeps the current value: %s -> %s" % (name, res))
    ctl = StatModel(100.0, 100.0)
    ctl.put("lock", 5.0)          # the -5 piece goes on: its cancel first (max 105) ...
    ctl.put("Armor", -5.0)        # ... then the engine's -5 (max 100, value 100)
    ctl.put("lock", 0.0)          # unequip, cancel removed BEFORE Recalculate drops the -5: max 95 -> the value is clamped
    check(ctl.value == 95.0, "W10: the model sees the loss when a negative cancel goes before Recalculate (why it waits)")
    for k in ("coins:fn:take", "coins:fn:get", "coins:fn:add"):
        bridge.remove(k)
    print("W. follow-up review done")

    # ---------------- U / V. exploit 4 / 5: migration
    BI = JClass("org.bson.BsonInt32")
    rolls = BD()
    rolls.append("dmg", BI(30))
    rolls.append("str", BI(0))
    rolls.append("crit", BI(0))
    rolls.append("quality", BI(10))
    ma = Data.migrate("Armor_Iron_Chest", rolls)
    mw = Data.migrate("Weapon_Sword_Iron", rolls)
    check([str(m.asDocument().getString("s").getValue()) for m in Data.mods(ma)] == [] and int(Data.rarity(ma)) == 0,
          "exploit 4: migrated armor drops dmg and scores 0 without it")
    check([str(m.asDocument().getString("s").getValue()) for m in Data.mods(mw)] == ["dmg"] and int(Data.rarity(mw)) == 1,
          "a migrated weapon keeps dmg (score 33 -> Unique)")
    check(ma.containsKey("old") and int(ma.getDocument("old").getInt32("dmg").getValue()) == 30, "the whole old document stays in old")
    top = BD()
    top.append("dmg", BI(30))
    top.append("str", BI(25))
    top.append("crit", BI(15))
    Cfg.MIGRATE_CLAMP = False
    m0 = Data.migrate("Weapon_Sword_Crude", top)
    vals0 = dict((str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(m0))
    check(vals0 == {"dmg": 30, "str": 25, "cc": 15} and int(Data.rarity(m0)) == 4, "clampToLevel off: the rolls stay (LOCKED) %s" % vals0)
    Cfg.MIGRATE_CLAMP = True
    m1 = Data.migrate("Weapon_Sword_Crude", top)
    vals1 = dict((str(m.asDocument().getString("s").getValue()), int(m.asDocument().getInt32("v").getValue())) for m in Data.mods(m1))
    want = dict((k, int(Roll.bounds(si(k), 4, int(Lvl.level("Weapon_Sword_Crude", m1)))[1])) for k in ("dmg", "str", "cc"))
    # 0.2: a Crude sword reads Lv 1 (the Wood / Crude band starts at 1), so its Fabled top roll is one level higher than at 0.1.x's level 0
    check(int(Lvl.level("Weapon_Sword_Crude", m1)) == 1 and vals1 == want and vals1 == {"dmg": 9, "str": 7, "cc": 4},
          "clampToLevel on: capped at bounds(i, Fabled, level 1)[1] %s" % vals1)
    Cfg.MIGRATE_CLAMP = False
    print("U/V. migration done")

    # ---------------- X. 0.1.1: Skyy's level table + the one-time config.properties update (GearCfg.migrate011)
    NEW = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 15), ("Thorium", 20), ("Cobalt", 25), ("Adamantite", 35),
           ("Mithril", 40), ("Onyxium", 40)]
    CH6 = [("Iron", 20, 15), ("Thorium", 30, 20), ("Cobalt", 35, 25), ("Adamantite", 40, 35), ("Mithril", 50, 40), ("Onyxium", 50, 40)]
    old_of = dict((t, o) for t, o, n in CH6)
    check([str(x) for x in Cfg.MAT_T] == [t for t, l in NEW] and [int(x) for x in Cfg.MAT_L] == [l for t, l in NEW],
          "X: built-in table = Skyy's 2026-09-30 table")
    check([int(x) for x in Cfg.MAT_OLD] == [old_of.get(t, l) for t, l in NEW], "X: MAT_OLD = the 0.1 placeholders")
    Cfg.apply(Props(), False)
    # (0.2: the built-in table is the band table - Wood / Crude start at 1; MAT_T / MAT_L above stay the 0.1.1 values migrate011 writes)
    for iid, lv_ in (("Weapon_Sword_Crude", 1), ("Weapon_Staff_Wood", 1), ("Weapon_Sword_Copper", 10), ("Weapon_Sword_Bronze", 15),
                     ("Armor_Iron_Chest", 15), ("Weapon_Sword_Thorium", 20), ("Weapon_Sword_Cobalt", 25), ("Weapon_Sword_Adamantite", 35),
                     ("Armor_Mithril_Head", 40), ("Weapon_Sword_Onyxium", 40)):
        check(int(Lvl.level(iid, None)) == lv_, "X: GearLevel.level(%s) = %d (built-in defaults)" % (iid, lv_))
    LVM, LVH = str(Cfg.LV_MARK), str(Cfg.LV_HEAD)
    check(LVM == "# SkyyGear 0.1.1 level defaults (Skyy 2026-09-30): Crude 0, Wood 0, Copper 10, Bronze 15, Iron 15, Thorium 20, Cobalt 25, "
          "Adamantite 35, Mithril 40, Onyxium 40", "X: the marker text")
    dflt = str(Cfg.defaultsText())
    # 0.1.3: the family block (marker + 59 rows) right under the metals - not part of the 0.1.1 / 0.1.2 shapes
    FAM_LINES = [str(Cfg.FM_MARK)] + ["level.material.%s=%d" % (str(t_), int(l_)) for t_, l_ in zip(Cfg.FAM_T, Cfg.FAM_L)]
    # 0.2: the default file carries bands, Armor_Copper and the bands block; shape013 = that text in the 0.1.3 shape (the metals as Skyy's
    # 0.1.1 single numbers, the family rows as their 0.1.3 single numbers, no Armor_Copper, no 0.2 block) - what the carried-forward
    # sections compare an updated old file with
    BD02 = [(str(t_), int(s_), int(c_)) for t_, s_, c_ in zip(Cfg.BD_T, Cfg.BD_MIN, Cfg.BD_CAP)]
    OLD013 = dict((str(t_), str(v_)) for t_, v_ in zip(Cfg.BO_T, Cfg.BO_V))

    # 0.2.1: the level stats block (marker, six settings with their help, the base.armor comment + four lines) right under level.armorNative;
    # shape02 = the fresh file without it (the 0.2 shape the carried-forward 0.2 sections compare with); shape013 drops it too
    LS021 = set([str(Cfg.LS_MARK)] + [str(x) for x in Cfg.LS_ROWC] + [str(x) for x in Cfg.LS_ROWL] + [str(Cfg.LS_TBLC)] + [str(x) for x in Cfg.LS_TBLL])
    # 0.2.2: the crit + vanilla-box block (heading, six rows with their help) right under charged.log - NO one-time update writes it (new
    # settings start at their defaults), so every older shape and the live file's expected values drop it: shape021 = the fresh file in its
    # 0.2.1 shape; shape02 / shape013 drop it too
    CF022 = set(str(x) for x in Cfg.CF_LINES)
    CF022K = [str(x).split("=", 1)[0] for x in Cfg.CF_LINES if not str(x).startswith("#")]

    def shape021(t):
        nl_ = "\r\n" if "\r\n" in t else "\n"
        return nl_.join(l_ for l_ in t.split(nl_) if l_ not in CF022)

    def shape02(t):
        nl_ = "\r\n" if "\r\n" in t else "\n"
        return nl_.join(l_ for l_ in t.split(nl_) if l_ not in LS021 and l_ not in CF022)

    def shape013(t):
        nl_ = "\r\n" if "\r\n" in t else "\n"
        drop = set([str(Cfg.BD_MARK)] + [str(x) for x in Cfg.BD_ROWC] + [str(x) for x in Cfg.BD_ROWL] + ["level.material.Armor_Copper=1,18"]) | LS021 | CF022
        band = dict(("level.material.%s=%d,%d" % b_, "level.material.%s=%s" % (b_[0], OLD013[b_[0]])) for b_ in BD02)
        return nl_.join(band.get(l_, l_) for l_ in t.split(nl_) if l_ not in drop)
    # the 0.1.2 default file without its 0.1.2 lines (the chg stat line + the charged block) = what sections X / Y compared with in 0.1.1
    _chl = set(["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5", str(Cfg.CH_MARK)] + [str(x) for x in Cfg.CH_ROWC]
               + [str(x) for x in Cfg.CH_ROWL] + FAM_LINES)
    dflt011 = "\n".join(l_ for l_ in shape013(dflt).split("\n") if l_ not in _chl)
    INFO6 = ("config.properties updated to the 0.1.1 level table: Iron 20 -> 15, Thorium 30 -> 20, Cobalt 35 -> 25, Adamantite 40 -> 35, "
             "Mithril 50 -> 40, Onyxium 50 -> 40 (the old file is in config-history; Server Setup -> Changes can undo each line)")
    XD = os.path.join(SCRATCH, "work", "x011")
    Log.FILE = None

    def cfg_quiet(limit_=8.0):
        """0.2.1 harness: wait until no config kit fallback save thread is alive. In a bare JVM the kit's saves run on daemon threads
        ("SkyyCfg-<mod>", 500 ms delay) started by earlier kit ops; such a thread's CfgLog.flush (snap -> write -> drop) can race a later
        case's synchronous flush into THAT case's config-changes.log (CfgLog.FILE is static) and write a line twice - the cause of the
        occasional Y(b) / Y(c) / Y(e) change-log count failures. In game the one-time updates run in setup() before the kit starts."""
        TH_ = JClass("java.lang.Thread")
        t0_ = time.time()
        while time.time() - t0_ < limit_:
            if not [t_ for t_ in TH_.getAllStackTraces().keySet() if str(t_.getName()).startswith("SkyyCfg-") and t_.isAlive()]:
                return True
            time.sleep(0.05)
        return False

    def case(name, data):
        """<XD>/<name>/mods/Skyy_SkyyGear/config.properties with these bytes (None = no file); GearCfg.FILE / DIR point there"""
        cfg_quiet()
        shutil.rmtree(os.path.join(XD, name), ignore_errors=True)
        d_ = os.path.join(XD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def rb(p):
        return open(p, "rb").read()

    def baks(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []

    def lines_of(p):
        return [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()] if os.path.isfile(p) else []

    def idx(d_):
        return lines_of(os.path.join(d_, "config-history", "index.log"))

    def clog(d_):
        return lines_of(os.path.join(d_, "config-changes.log"))

    def upd(text, changes):
        """the expected update: these (material, old, new) value lines changed + the marker under the levels header, endings kept"""
        nl = "\r\n" if "\r\n" in text else "\n"
        out = text
        for t, o, n in changes:
            a_ = nl + "level.material.%s=%d%s" % (t, o, nl)
            assert out.count(a_) == 1, (t, o)
            out = out.replace(a_, nl + "level.material.%s=%d%s" % (t, n, nl))
        assert out.count(LVH + nl) == 1
        return out.replace(LVH + nl, LVH + nl + LVM + nl)

    def info_for(changes):
        return ("config.properties updated to the 0.1.1 level table: " + ", ".join("%s %d -> %d" % c for c in changes)
                + " (the old file is in config-history; Server Setup -> Changes can undo each line)")

    check(info_for(CH6) == INFO6, "X: expected INFO text helper")
    live = None
    LIVE_NOW = None
    if not os.path.isfile(LIVE):
        check(False, "X(a): the live config.properties is missing: %s (pass --live <file>)" % LIVE)
    else:
        live = rb(LIVE)            # read only: every test below works on scratch copies
        LIVE_NOW = live
        if b"SkyyGear 0.1.1 level defaults" in live:
            # 0.1.3 harness: 0.1.1 + 0.1.2 are deployed, so the live file already carries their updates. Sections X / Y / Z7 replay those
            # updates on the live file as it was before them = its copy "before the 0.1.1 level table update" in the live config-history
            # (read only); section AA runs the 0.1.3 update on the live file as it is now.
            # (review of 0.2 finding 6: hist_copy asks the live config-history first, then the deploy backups - KEEP 10 evicts old copies)
            pre, where_ = hist_copy("before the 0.1.1 level table update")
            check(pre is not None, "X: a 'before the 0.1.1 level table update' History copy exists (the live config-history or a deploy "
                                   "backup): searched %s" % where_)
            if pre is not None:
                live = pre
                check(live.startswith(b"# SkyyGear 0.1 - ") and b"SkyyGear 0.1.1" not in live, "X: that copy is the 0.1 file")
                print("X. the live file is already updated in game - X / Y / Z7 replay 0.1.1 / 0.1.2 on its pre-0.1.1 copy (from %s)" % where_)
    if live is not None:
        lt = live.decode("latin-1")
        # (a) the exact live file
        d, f = case("a-live", live)
        exp = upd(lt, CH6)
        res = str(Cfg.migrate011())
        got = rb(f)
        check(got == exp.encode("latin-1"), "X(a): the live file -> exactly six value lines changed + the marker, every other byte kept")
        check(res.split("\n") == [INFO6], "X(a): one INFO line: %r" % res)
        print("X. INFO line the live file produces: [SkyyGear] " + res.split("\n")[0])
        b = baks(d)
        check(len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == live, "X(a): History keeps the old file (one .bak = the old bytes)")
        ix = idx(d)
        check(len(ix) == 1 and ix[0].split("\t")[1] == "Skyy_SkyyGear/config.properties"
              and ix[0].split("\t")[3:] == ["SkyyGear 0.1.1", "before the 0.1.1 level table update"], "X(a): index.log names the update: %s" % ix)
        cl = clog(d)
        want = [["SkyyGear 0.1.1", "-", "update", "level.material[%s]" % t, str(o), str(n), "ok"] for t, o, n in CH6]
        check([l.split("\t")[1:] for l in cl] == want and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in cl),
              "X(a): six config-changes.log lines in the kit's format (Undo-able ok lines): %s" % cl)
        check(not os.path.exists(f + ".tmp"), "X(a): no temp file left")
        Cfg.load()
        check(all(int(Cfg.MAT.get(t.lower())) == n for t, o, n in CH6) and int(Cfg.MAT.get("copper")) == 10, "X(a): the loader reads the new levels")
        # (0.2: the ready line shows bands - a one-number row reads N to N+7 until migrate02 turns the defaults into bands; Armor_Copper
        # arrives with migrate02)
        check(str(Cfg.matText()) == "Crude 0-7, Wood 0-7, Copper 10-17, Armor_Copper -, Bronze 15-22, Iron 15-22, Thorium 20-27, Cobalt 25-32, "
              "Adamantite 35-42, Mithril 40-47, Onyxium 40-47; 0 of 59 family rows (0 at the 0.2 default band)",
              "X(a): the ready line's table (0.1.3: + the family count; 0.2: bands): " + str(Cfg.matText()))
        same = exp.replace("# SkyyGear 0.1 - ", "# SkyyGear %s - " % VERSION, 1) == dflt011
        print("X. the level-updated live file %s the 0.1.1 default file apart from the version in line 1 (the stat defaults follow in Y)"
              % ("EQUALS" if same else "DIFFERS FROM"))
        # (e) a second start
        check(str(Cfg.migrate011()) == "" and rb(f) == got and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 6,
              "X(e): a second start changes nothing (file, History, change log)")

        # (b) one hand-edited material
        tb = lt.replace("\nlevel.material.Cobalt=35\n", "\nlevel.material.Cobalt=30\n")
        check(tb != lt, "X(b): test file has Cobalt=30")
        d, f = case("b-custom", tb.encode("latin-1"))
        ch5 = [c for c in CH6 if c[0] != "Cobalt"]
        res = str(Cfg.migrate011()).split("\n")
        check(rb(f) == upd(tb, ch5).encode("latin-1"), "X(b): Cobalt=30 kept, the other five updated, every other byte kept")
        check(res == [info_for(ch5), "level.material.Cobalt=30 kept (custom) - the 0.1.1 default is 25"], "X(b): INFO + the kept note: %s" % res)
        check([l.split("\t")[4] for l in clog(d)] == ["level.material[%s]" % c[0] for c in ch5], "X(b): five change-log lines, none for Cobalt")
        Cfg.load()
        check(int(Cfg.MAT.get("cobalt")) == 30 and int(Cfg.MAT.get("iron")) == 15, "X(b): the loader: Cobalt 30, Iron 15")
        check(str(Cfg.migrate011()) == "", "X(b): the kept note is logged once (the next start does nothing)")

        # (c) CRLF
        tc = lt.replace("\n", "\r\n")
        d, f = case("c-crlf", tc.encode("latin-1"))
        res = str(Cfg.migrate011())
        gc = rb(f)
        check(gc == upd(tc, CH6).encode("latin-1") and gc.count(b"\n") == gc.count(b"\r\n") and gc.replace(b"\r\n", b"\n") == got,
              "X(c): a CRLF file gets the same update, every line (the marker too) still ends CRLF")
        check(res == INFO6, "X(c): same INFO line")
        Cfg.load()
        check(int(Cfg.MAT.get("mithril")) == 40, "X(c): the loader reads the CRLF file")

    # (d) no file
    d, f = case("d-nofile", None)
    check(str(Cfg.migrate011()) == "" and not os.path.exists(f) and not os.path.exists(os.path.join(d, "config-history"))
          and not os.path.exists(os.path.join(d, "config-changes.log")), "X(d): no file -> the update writes nothing")
    Cfg.load()
    fd = rb(f) if os.path.isfile(f) else b""
    check(fd == dflt.encode("utf-8") and LVM.encode("ascii") in fd, "X(d): the loader writes the 0.1.1 default file, marker included")
    check(str(Cfg.migrate011()) == "" and rb(f) == fd, "X(d): the next start leaves the fresh file alone")
    check(int(Cfg.MAT.get("iron")) == 15 and int(Cfg.MAT.get("onyxium")) == 40, "X(d): fresh file levels")
    Cfg.FILE = None
    check(str(Cfg.migrate011()) == "", "X(d): no FILE set -> nothing")

    # (f) a file the config kit wrote in game (Server Setup): tset / set / remove through config:fn:SkyyGear, then 0.1.1 starts
    if live is not None:
        CfgPub = J("CfgPub")
        OA = JArray(JObject)
        d, f = case("f-kit", live)
        mods = os.path.dirname(d)
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyGear")
        # 0.2: Level by material is a 2-column Min | Cap table, so an in-game edit is a band ("25|32" -> the file line 25,32)
        r1 = fn.apply(OA(["tset", "level.material", "Iron", "25|32", None, "console", "yes", "console"]))
        r2 = fn.apply(OA(["set", "part.gate", "false", None, "console", "yes", "console"]))
        r3 = fn.apply(OA(["remove", "level.material", "Onyxium", None, "console", "yes", "console"]))
        check(all(r_ is not None and str(r_[0]) == "ok" for r_ in (r1, r2, r3)), "X(f): in-game changes accepted: %s" % [
            None if r_ is None else str(r_[2]) for r_ in (r1, r2, r3)])
        CfgPub.flush()
        kt = rb(f).decode("latin-1")
        kit_log = clog(d)
        check("\nlevel.material.Iron=25,32\n" in kt and "\npart.gate=false\n" in kt and "level.material.Onyxium" not in kt and len(baks(d)) == 1
              and len(kit_log) == 3, "X(f): the kit wrote the file (Iron 25,32, part.gate off, Onyxium removed), 1 History copy, 3 log lines")
        res = str(Cfg.migrate011()).split("\n")
        ch4 = [("Thorium", 30, 20), ("Cobalt", 35, 25), ("Adamantite", 40, 35), ("Mithril", 50, 40)]
        check(rb(f) == upd(kt, ch4).encode("latin-1"),
              "X(f): four updated; Iron 25,32, part.gate=false and the kit's line layout kept; the removed Onyxium line is not added back")
        check(res == [info_for(ch4), "level.material.Iron=25,32 kept (custom) - the 0.1.1 default is 15"], "X(f): INFO + kept note: %s" % res)
        cl = clog(d)
        check(cl[:3] == kit_log and [l.split("\t")[4] for l in cl[3:]] == ["level.material[%s]" % c[0] for c in ch4],
              "X(f): the kit's own log lines stay as they were, four update lines after them")
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == live and rb(os.path.join(d, "config-history", b[1])) == kt.encode("latin-1"),
              "X(f): the kit's History copy stays, the update adds one (= the kit-written file)")
        # the next start: loader + kit read the updated file; Undo the way SkyyMenu sends it (tset back to the log line's old value)
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        lg = [str(x) for x in fn.apply(OA(["log", Integer.valueOf(20)]))]
        check(sum(1 for l in lg if "\tupdate\tlevel.material[" in l and l.endswith("\tok")) == 4 and len(lg) == 7,
              "X(f): the kit's log op lists the four update lines as ok (SkyyMenu offers Undo on them)")
        ks = fn.apply(OA(["keys", "level.material", ""]))
        now_ = dict(zip([str(x) for x in ks[0]], [str(x) for x in ks[2]]))
        check(now_.get("Thorium") == "20" and now_.get("Iron") == "25|32" and "Onyxium" not in now_, "X(f): kit memory = the updated file: %s" % now_)
        # Undo the way SkyyMenu sends it (tset back to the log line's old value). 0.2 KNOWN LIMIT: a pre-0.2 line whose old side is ONE
        # number ('Thorium 30 -> 20', the kit's own 'Iron 20 -> 25|32') is refused by the 2-column table - the band form of the same
        # number (N|N+7, what migrate02 itself logs as the old value) goes through
        u1 = fn.apply(OA(["tset", "level.material", "Thorium", "30", None, "console", "yes", "console"]))    # Undo 'Thorium 30 -> 20'
        u2 = fn.apply(OA(["tset", "level.material", "Iron", "20", None, "console", "yes", "console"]))       # Undo the kit's 'Iron 20 -> 25|32'
        check(str(u1[0]) != "ok" and str(u2[0]) != "ok" and "Needs 2 value(s): Min | Cap." in str(u1[2]),
              "X(f) 0.2: a one-number Undo is refused by the Min | Cap table: %s" % [str(u1[2]), str(u2[2])])
        u1 = fn.apply(OA(["tset", "level.material", "Thorium", "30|37", None, "console", "yes", "console"]))
        u2 = fn.apply(OA(["tset", "level.material", "Iron", "20|27", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt2 = rb(f).decode("latin-1")
        check(str(u1[0]) == "ok" and str(u2[0]) == "ok" and "\nlevel.material.Thorium=30,37\n" in kt2 and "\nlevel.material.Iron=20,27\n" in kt2,
              "X(f): the band form of an update line's and of the kit's older line's old value both work")
        check(str(Cfg.migrate011()) == "" and rb(f).decode("latin-1") == kt2, "X(f): old numbers set back after the update survive the next start")
        Cfg.load()
        check(int(Cfg.MAT.get("thorium")) == 30 and int(Cfg.MAT.get("iron")) == 20 and Cfg.MAT.get("onyxium") is None
              and int(Cfg.MAT.get("cobalt")) == 25 and int(Cfg.MATCAP.get("thorium")) == 37 and int(Cfg.MATCAP.get("cobalt")) == 32,
              "X(f): loader after the undos: Thorium 30-37, Iron 20, no Onyxium line, Cobalt 25 (one number = 25-32)")

    # (g) the pure text step on edge cases
    BS = chr(92)
    H = LVH + "\n"

    def lv(t):
        r_ = Cfg.lvUpdate(t)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])

    r = lv(H + "level.material.Iron = 20\nlevel.material.thorium:30\nlevel.material.Cobalt 35\nlevel.material.MITHRIL=50   \n")
    check(r[0] == H + LVM + "\nlevel.material.Iron = 15\nlevel.material.thorium:20\nlevel.material.Cobalt 25\nlevel.material.MITHRIL=40\n"
          and r[3] == ["Iron", "20", "15", "thorium", "30", "20", "Cobalt", "35", "25", "MITHRIL", "50", "40"],
          "X(g): spacing, ':' / ' ' separators, any-case entry words and trailing spaces: value text replaced only (%r)" % (r,))
    r = lv(H + "level.material.Iron=20\nx=1\nlevel.material.Iron=22\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=20\nx=1\nlevel.material.Iron=22\n" and r[3] == []
          and r[2] == ["level.material.Iron=22 kept (custom) - the 0.1.1 default is 15"], "X(g): last line wins - custom 22 kept, the dead 20 left")
    r = lv(H + "level.material.Iron=22\nlevel.material.Iron=20\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=22\nlevel.material.Iron=15\n" and r[3] == ["Iron", "20", "15"], "X(g): last line 20 -> updated")
    r = lv(H + "level.material.Iron=2" + BS + "\n    0\nlevel.material.Mithril=50\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=2" + BS + "\n    0\nlevel.material.Mithril=40\n" and r[3] == ["Mithril", "50", "40"]
          and r[2] == ["level.material.Iron=20 kept (custom) - the 0.1.1 default is 15"], "X(g): a continued entry is never rewritten (noted)")
    r = lv(H + "a=x" + BS + "\nlevel.material.Iron=20\n")
    check(r[0] == H + LVM + "\na=x" + BS + "\nlevel.material.Iron=20\n" and r[3] == [] and r[2] == [], "X(g): a continuation line is not a key")
    r = lv(H + "#level.material.Iron=20\n! level.material.Mithril=50\n")
    check(r[0] == H + LVM + "\n#level.material.Iron=20\n! level.material.Mithril=50\n" and r[1] == "" and r[2] == [] and r[3] == [],
          "X(g): commented / template lines never change (a missing line stays missing)")
    r = lv(H + "level.material.Iron=15\nlevel.material.Copper=12\nlevel.material.Gold=20\nlevel.material.=20\nlevel.material.Onyxium=20.0\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=15\nlevel.material.Copper=12\nlevel.material.Gold=20\nlevel.material.=20\nlevel.material.Onyxium=20.0\n"
          and r[3] == [] and r[2] == ["level.material.Onyxium=20.0 kept (custom) - the 0.1.1 default is 40"],
          "X(g): already new / unchanged material / unknown word / empty word untouched and silent; 20.0 is custom")
    r = lv("a=1\nlevel.material.Iron=20\nb=2\n")
    check(r[0] == "a=1\n" + LVM + "\nlevel.material.Iron=15\nb=2\n", "X(g): no levels header -> marker before the first level.material line")
    check(lv("a=1\nb=2\n")[0] == "a=1\nb=2\n" + LVM + "\n", "X(g): no header, no level lines -> marker at the end")
    check(lv("a=1")[0] == "a=1\n" + LVM and lv("a=1\r\nb=2")[0] == "a=1\r\nb=2\r\n" + LVM and lv("")[0] == LVM + "\n",
          "X(g): no final newline stays so (CRLF kept); empty text")
    check(lv(LVH + "\r\nlevel.material.Iron=20\n")[0] == LVH + "\r\n" + LVM + "\r\nlevel.material.Iron=15\n", "X(g): the marker takes the header's CR")
    r = lv(H + "level.material.Iron=20\n\n# ---- changed in game (SkyWynn Menu) ----\nlevel.material.Mithril=50\n")
    check(r[0] == H + LVM + "\nlevel.material.Iron=15\n\n# ---- changed in game (SkyWynn Menu) ----\nlevel.material.Mithril=40\n",
          "X(g): a line the kit appended under its 'changed in game' header is updated in place")
    check(Cfg.lvUpdate("# SkyyGear 0.1.1 level defaults, anything\nlevel.material.Iron=20\n") is None
          and Cfg.lvUpdate("x=1\n  ! SkyyGear 0.1.1 level defaults\n") is None, "X(g): a comment line with the marker id = already done")
    r = lv("note=SkyyGear 0.1.1 level defaults\nlevel.material.Iron=20\n")
    check(r is not None and "level.material.Iron=15" in r[0], "X(g): the marker id inside a value does not count")

    # (i) review of 0.1.1, finding 4: a file that ends inside a still-open continued entry (the append-at-end branch) gets the marker
    # just before that entry; java.util.Properties reads the same values before and after, the marker is a comment, a second pass
    # finds it, every other byte is kept
    StringReader = JClass("java.io.StringReader")
    MID = str(Cfg.LV_MARK_ID)

    def props(t):
        p_ = Props()
        p_.load(StringReader(t))
        return dict((str(k_), str(p_.getProperty(k_))) for k_ in p_.stringPropertyNames())

    def marker_ok(t, out, rows=()):
        """Properties(out) = Properties(t) + the updated rows, no key / value holds the marker id, the next pass does nothing"""
        want = props(t)
        for i_ in range(0, len(rows), 3):
            want["level.material." + rows[i_]] = rows[i_ + 2]
        got_ = props(out)
        return (got_ == want and not any(MID in k_ or MID in v_ for k_, v_ in got_.items()) and Cfg.lvUpdate(out) is None
                and out.count(MID) == 1)

    for t, want in (
            ("a=abc" + BS, LVM + "\na=abc" + BS),
            ("a=abc" + BS + "\n", LVM + "\na=abc" + BS + "\n"),
            ("x=1\r\na=abc" + BS + "\r\n", "x=1\r\n" + LVM + "\r\na=abc" + BS + "\r\n"),
            ("x=1\r\na=abc" + BS, "x=1\r\n" + LVM + "\r\na=abc" + BS),
            ("x=1\na=x" + BS + "\n  y" + BS + "\n", "x=1\n" + LVM + "\na=x" + BS + "\n  y" + BS + "\n"),
            ("# c\na=x" + BS + "\n#c" + BS, "# c\n" + LVM + "\na=x" + BS + "\n#c" + BS),        # '#c\' is a continuation line here
            ("a=1\n" + BS + "\n", "a=1\n" + LVM + "\n" + BS + "\n"),                            # a lone backslash (Properties: key "")
            ("#c" + BS + "\n", "#c" + BS + "\n" + LVM + "\n"),                                  # a comment never continues: at the end
            ("a=1\n#c" + BS, "a=1\n#c" + BS + "\n" + LVM),
            ("a=abc" + BS + BS + "\n", "a=abc" + BS + BS + "\n" + LVM + "\n"),                  # an even count = an escaped backslash
            ("a=x" + BS + "\n#c\n", "a=x" + BS + "\n#c\n" + LVM + "\n")):                       # the entry ended before the last line
        r = lv(t)
        check(r is not None and r[0] == want and marker_ok(t, r[0]), "X(i): finding 4 - %r -> %r (got %r)" % (t, want, r and r[0]))
    # the same rule over random files (fixed seed): pieces with odd / even backslashes, comments ending in one, lone backslashes,
    # blank lines, level lines (one spelling per material, so Properties keys match the rows), LF / CRLF, with / without final newline
    import random
    rnd = random.Random(20260930)
    pieces = ["a=1", "b=x" + BS, "c=y" + BS + BS, "#c" + BS, "# note", "", "   z" + BS, BS, "d:e", "  f g" + BS, "!x" + BS,
              "level.material.Iron=20", "level.material.Mithril=50", "level.material.Copper=10", "level.material.Iron=22", LVH]
    def bytes_kept(t, out):
        """out = t + exactly one marker line; only level.material value lines differ (a CR may join the last line when the marker
        is appended after a last line without newline)"""
        ol, tl = out.split("\n"), t.split("\n")
        mi = [i_ for i_, x_ in enumerate(ol) if MID in x_]
        if len(mi) != 1 or ol[mi[0]].rstrip("\r") != LVM:
            return False
        m_ = mi[0]
        rest = ol[:m_] + ol[m_ + 1:]
        if len(rest) != len(tl):
            return False
        for i_, (a_, b_) in enumerate(zip(rest, tl)):
            if a_ == b_ or (a_.startswith("level.material.") and b_.startswith("level.material.")):
                continue
            if i_ == len(tl) - 1 and m_ == len(ol) - 1 and a_ == b_ + "\r":
                continue
            return False
        return True

    bad = []
    for n_ in range(3000):
        ls_ = [rnd.choice(pieces) for _q in range(rnd.randint(0, 7))]
        if n_ % 2 == 0:
            ls_ = [p_ for p_ in ls_ if not p_.startswith("level.material.") and p_ != LVH]      # half the cases hit the end branch
        if BS in ls_:
            # a lone backslash line continues into the next line and adds nothing, so java.util.Properties takes the NEXT line's key;
            # the kit's CfgFile.key reads only the first physical line (key ""). A kit-wide limit, not the update's: no level lines here
            ls_ = [p_ for p_ in ls_ if not p_.startswith("level.material.")]
        nl_ = "\r\n" if rnd.random() < 0.3 else "\n"
        t = nl_.join(ls_) + (nl_ if rnd.random() < 0.6 else "")
        r = lv(t)
        if r is None or not marker_ok(t, r[0], r[3]) or not bytes_kept(t, r[0]):
            bad.append(t)
    check(not bad, "X(i): finding 4 - 3000 random files: same Properties values (+ updated rows), marker = one comment line and the "
                   "only line added, the next pass does nothing (%d bad, first %r)" % (len(bad), bad[:1]))
    # migrate011 end to end: such a file is updated once; before the fix the next start added another marker every time
    ti = b"a=1\nb=abc\\"
    d, f = case("i-open", ti)
    res = str(Cfg.migrate011())
    check(res == "config.properties: no level.material line still had its 0.1 default - nothing changed (0.1.1 level table marker added)"
          and rb(f) == b"a=1\n" + LVM.encode("ascii") + b"\nb=abc\\", "X(i): finding 4 - migrate011 on a file ending in a continued entry")
    check(str(Cfg.migrate011()) == "" and rb(f) == b"a=1\n" + LVM.encode("ascii") + b"\nb=abc\\" and len(baks(d)) == 1,
          "X(i): finding 4 - the next start finds the marker (no second marker, no second History copy)")

    # (i) finding 3: the update only rewrites the file once config-history holds the old bytes
    tx = ("a=1\n" + H + "level.material.Iron=20\nlevel.material.Mithril=50\n").encode("latin-1")
    info2 = info_for([("Iron", 20, 15), ("Mithril", 50, 40)])
    d, f = case("i-nohist", tx)
    open(os.path.join(d, "config-history"), "wb").write(b"blocker")          # a plain file where the History folder goes
    glf = os.path.join(XD, "i-gear.log")                                      # Gear.warn's gear.log copy (no server logger here)
    Log.FILE = Paths.get(glf)
    res = str(Cfg.migrate011())
    Log.flush()
    Log.FILE = None
    gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
    check(res == "" and rb(f) == tx and not os.path.exists(os.path.join(d, "config-changes.log"))
          and not os.path.exists(f + ".tmp"), "X(i): finding 3 - config-history cannot be written -> file untouched, no change-log lines")
    check("WARN config.properties NOT updated to the 0.1.1 level table: the old file could not be kept in " in gl
          and "(the file is used as it is; the next start tries again)" in gl and "CONFIG 0.1.1" not in gl,
          "X(i): finding 3 - the WARN line says why and that the next start retries: %r" % gl)
    os.remove(os.path.join(d, "config-history"))
    res = str(Cfg.migrate011())
    b = baks(d)
    check(res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx and len(clog(d)) == 2
          and LVM.encode("ascii") in rb(f), "X(i): finding 3 - the next start (History writable again) updates; the old bytes are kept: %r" % res)
    # a failed file write after the History copy: the retry reuses the equal copy (snapshot skips it, lvSaved accepts it)
    d, f = case("i-retry", tx)
    os.makedirs(f + ".tmp")                                                   # the kit's temp file cannot be created
    ok1 = str(Cfg.migrate011()) == "" and rb(f) == tx and len(baks(d)) == 1 and not os.path.exists(os.path.join(d, "config-changes.log"))
    os.rmdir(f + ".tmp")
    res = str(Cfg.migrate011())
    b = baks(d)
    check(ok1 and res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx and len(idx(d)) == 1
          and len(clog(d)) == 2, "X(i): finding 3 - a failed write keeps the file; the retry updates without a second History copy: %r" % res)
    # a copy whose index.log line failed still holds the bytes: the update goes on (no endless retry on an orphan copy)
    d, f = case("i-noindex", tx)
    os.makedirs(os.path.join(d, "config-history", "index.log"))              # a folder where index.log goes
    res = str(Cfg.migrate011())
    b = baks(d)
    check(res == info2 and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == tx,
          "X(i): finding 3 - a History copy without its index line still counts: %r" % res)

    # (h) bytes: BOM + ISO-8859-1 bytes + a \u escape kept; a folder in place of the file
    rawh = (b"\xef\xbb\xbf# caf\xe9 \xff\r\n" + LVH.encode("ascii") + b"\r\nlevel.material.Iron=20\r\nname=\\u00e9t\xe9\r\n")
    d, f = case("h-bytes", rawh)
    Cfg.migrate011()
    check(rb(f) == b"\xef\xbb\xbf# caf\xe9 \xff\r\n" + LVH.encode("ascii") + b"\r\n" + LVM.encode("ascii")
          + b"\r\nlevel.material.Iron=15\r\nname=\\u00e9t\xe9\r\n", "X(h): BOM, ISO-8859-1 bytes and escapes kept byte for byte")
    d, f = case("h-folder", None)
    os.makedirs(f)
    check(str(Cfg.migrate011()) == "" and os.path.isdir(f) and not os.path.exists(os.path.join(d, "config-history")),
          "X(h): a folder named config.properties -> WARN, nothing written, no exception")
    Cfg.FILE = None
    Cfg.DIR = None

    # setup() order (bytecode): SkyyRolls cost import -> the update -> the loader -> the config kit; the ready line reads the table
    su = code("SkyyGearPlugin", "setup")

    def pos(needle):
        return next((i for i, l in enumerate(su) if needle in l), -1)

    check(0 <= pos("GearCfg.importRolls") < pos("GearCfg.migrate011") < pos("GearCfg.migrateStat011") < pos("GearCfg.load") < pos("CfgPub.start"),
          "X/Y: setup() runs importRolls -> migrate011 -> migrateStat011 -> load -> CfgPub.start")
    check(pos("GearCfg.load") < pos("GearCfg.matText") < pos("GearCfg.statText") < pos("CfgPub.start"),
          "X/Y: the ready line lists the loaded level table, then the loaded stat defaults")
    print("X. 0.1.1 level table + update done")

    # ---------------- Y. 0.1.1 stat defaults: pool.later off + stat.levelFull 40 (defaults, loader, one-time update, every roll path)
    STM, STID = str(Cfg.ST_MARK), str(Cfg.ST_MARK_ID)
    check(STM == "# SkyyGear 0.1.1 stat defaults (Skyy 2026-09-30): coming-later stats never roll (pool.later false), full modifier power "
          "from item level 40 (stat.levelFull 40, Mithril / Onyxium)", "Y: the stat marker text")
    check([str(x) for x in Cfg.ST_KEY] == ["pool.later", "stat.levelFull"] and [str(x) for x in Cfg.ST_OLD] == ["true", "50"]
          and [str(x) for x in Cfg.ST_NEW] == ["false", "40"], "Y: keys, 0.1 texts, 0.1.1 texts")
    check(STID not in LVM and str(Cfg.LV_MARK_ID) not in STM, "Y: the two markers never match each other")
    WHY = {"pool.later": "coming-later stats never roll", "stat.levelFull": "full modifier power from item level 40 = Mithril / Onyxium"}
    ST2 = [("pool.later", "true", "false"), ("stat.levelFull", "50", "40")]

    def st_info(changes):
        return ("config.properties updated to the 0.1.1 stat defaults: " + ", ".join("%s %s -> %s (%s)" % (k, o, n, WHY[k]) for k, o, n in changes)
                + " (the old file is in config-history; Server Setup -> Changes can undo each line)")

    STINFO = st_info(ST2)
    NOCHG = "config.properties: no pool.later / stat.levelFull line still had its 0.1 default - nothing changed (0.1.1 stat defaults marker added)"
    READY = "coming-later stats never roll; full modifier power from item level 40"

    def st_upd(text, changes, anchor="# Roll coming-later stats: "):
        """the expected stat update: these value lines changed + the marker on its own line right above the anchor line"""
        nl = "\r\n" if "\r\n" in text else "\n"
        out = text
        for k, o, n in changes:
            a_ = nl + "%s=%s%s" % (k, o, nl)
            assert out.count(a_) == 1, (k, o)
            out = out.replace(a_, nl + "%s=%s%s" % (k, n, nl))
        assert out.count(nl + anchor) == 1, anchor
        return out.replace(nl + anchor, nl + STM + nl + anchor)

    # (a) defaults: rows, field initial values, loader fallback, level factor, the fresh file
    check(defs["pool.later"] == "false" and types["pool.later"] == "bool" and defs["stat.levelFull"] == "40" and types["stat.levelFull"] == "int",
          "Y(a): row defaults pool.later false, stat.levelFull 40")
    check(helps["pool.later"] == "Off (Skyy, 2026-09-30) = stats that do nothing yet never roll. On = they may roll, shown grey."
          and helps["stat.levelFull"] == "Gear this level or higher rolls at full power (40 = Mithril)." + PH, "Y(a): the two row help texts")
    mi_ = pool.get(PKG + "GearCfg").getClassInitializer().getMethodInfo()
    it_ = mi_.getCodeAttribute().iterator()
    clinit = []
    while it_.hasNext():
        clinit.append(str(IP.instructionString(it_, it_.next(), mi_.getConstPool())))
    check("iconst_0" in before_call(clinit, "GearCfg.POOL_LATER") and "bipush 40" in before_call(clinit, "GearCfg.LEVEL_FULL"),
          "Y(a): field initial values POOL_LATER false, LEVEL_FULL 40 (%s / %s)" % (before_call(clinit, "GearCfg.POOL_LATER"),
                                                                                    before_call(clinit, "GearCfg.LEVEL_FULL")))
    Cfg.POOL_LATER = True
    Cfg.LEVEL_FULL = 50
    Cfg.apply(Props(), False)
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(a): loader fallback without the lines = off / 40")
    p = Props()
    p.setProperty("pool.later", "maybe")
    p.setProperty("stat.levelFull", "lots")
    Cfg.POOL_LATER = True
    Cfg.apply(p, False)
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(a): an unreadable value falls back to off / 40 too")
    Cfg.apply(Props(), False)
    check(abs(float(Lvl.factor(0)) - 25.0) < 1e-9 and abs(float(Lvl.factor(20)) - 62.5) < 1e-9 and abs(float(Lvl.factor(40)) - 100.0) < 1e-9
          and abs(float(Lvl.factor(50)) - 100.0) < 1e-9, "Y(a): level factor 25 % at 0, 62.5 % at 20 (Thorium), full power from 40")
    check(int(Roll.bounds(si("dmg"), 5, 40)[1]) == int(Roll.bounds(si("dmg"), 5, 100)[1]) > int(Roll.bounds(si("dmg"), 5, 35)[1]),
          "Y(a): Mithril / Onyxium (level 40) reach the top roll, Adamantite (35) does not")
    check(("\n" + STM + "\n# Roll coming-later stats: " + helps["pool.later"] + "\npool.later=false\n") in dflt and dflt.count(STID) == 1
          and ("\n# Item level with full modifier power: " + helps["stat.levelFull"] + "\nstat.levelFull=40\n") in dflt,
          "Y(a): the default file: pool.later=false, stat.levelFull=40, the marker right above the pool.later help line")
    d, f = case("y-fresh", None)
    Cfg.load()
    fd = rb(f) if os.path.isfile(f) else b""
    check(fd == dflt.encode("utf-8") and str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f) == fd
          and not os.path.exists(os.path.join(d, "config-history")) and not os.path.exists(os.path.join(d, "config-changes.log")),
          "Y(a): a fresh file carries both markers - neither update touches it")
    Cfg.load()
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40 and str(Cfg.statText()) == READY, "Y(a): the fresh file loads off / 40")

    OA = JArray(JObject)
    if live is not None:
        lt = live.decode("latin-1")
        # (b) the live file on a scratch copy, both updates in the setup order
        d, f = case("y-live", live)
        r1 = str(Cfg.migrate011())
        mid = rb(f)
        r2 = str(Cfg.migrateStat011())
        got = rb(f)
        exp_mid = upd(lt, CH6)
        exp = st_upd(exp_mid, ST2)
        check(mid == exp_mid.encode("latin-1") and got == exp.encode("latin-1"),
              "Y(b): the live file -> the level update, then exactly the two value lines (pool.later, stat.levelFull) + the stat marker, "
              "every other byte kept")
        check(r1 == INFO6 and r2.split("\n") == [STINFO], "Y(b): the INFO lines: %r / %r" % (r1, r2))
        print("Y. INFO line the live file produces: [SkyyGear] " + r2.split("\n")[0])
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == live and rb(os.path.join(d, "config-history", b[1])) == mid,
              "Y(b): History = the 0.1 file (before the level update) + the file before the stat update")
        ix = idx(d)
        check(len(ix) == 2 and ix[1].split("\t")[1] == "Skyy_SkyyGear/config.properties"
              and ix[1].split("\t")[3:] == ["SkyyGear 0.1.1", "before the 0.1.1 stat defaults update"], "Y(b): index.log names the stat update: %s" % ix)
        cl = clog(d)
        want = [["SkyyGear 0.1.1", "-", "update", k, o, n, "ok"] for k, o, n in ST2]
        check(len(cl) == 8 and [l.split("\t")[1:] for l in cl[6:]] == want
              and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l.split("\t")[0]) for l in cl[6:]),
              "Y(b): two more config-changes.log lines in the kit's scalar-row format (Undo-able ok lines): %s" % cl[6:])
        check(not os.path.exists(f + ".tmp"), "Y(b): no temp file left")
        Cfg.load()
        check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40 and str(Cfg.statText()) == READY, "Y(b): the loader reads off / 40")
        print("Y. ready line (live copy, after both updates): [SkyyGear] 0.1.1 ready - ... level by material (combat gear vs the class weapon skill): "
              + str(Cfg.matText()) + "; " + str(Cfg.statText()) + "; Server Setup -> Gear")
        gl_, dl_ = got.decode("latin-1").split("\n"), dflt011.split("\n")
        dif = [i_ for i_ in range(max(len(gl_), len(dl_))) if i_ >= len(gl_) or i_ >= len(dl_) or gl_[i_] != dl_[i_]]
        print("Y. the fully updated live file %s every value of a fresh 0.1.1 file; it differs in %d line(s) (comments are never rewritten): %s"
              % ("HAS" if props(got.decode("latin-1")) == props(dflt011) else "does NOT have", len(dif), [dl_[i_][:45] for i_ in dif if i_ < len(dl_)]))
        # (c) a second start
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f) == got and len(baks(d)) == 2 and len(idx(d)) == 2
              and len(clog(d)) == 8, "Y(c): a second start changes nothing (file, History, change log)")

        # (d) CRLF
        tc = lt.replace("\n", "\r\n")
        d, f = case("y-crlf", tc.encode("latin-1"))
        Cfg.migrate011()
        midc = rb(f).decode("latin-1")
        res = str(Cfg.migrateStat011())
        gc = rb(f)
        check(gc == st_upd(midc, ST2).encode("latin-1") and gc.count(b"\n") == gc.count(b"\r\n") and gc.replace(b"\r\n", b"\n") == got
              and res == STINFO, "Y(d): a CRLF file gets the same update, every line (the marker too) still ends CRLF")

        # (e) hand-edited values: kept + noted once, or silent
        for name, edits, notes, chs, pl, lf in (
                ("on", [("\npool.later=true\n", "\npool.later=on\n")], ["pool.later=on kept (custom) - the 0.1.1 default is false"], [ST2[1]], True, 40),
                ("True", [("\npool.later=true\n", "\npool.later=True\n")], ["pool.later=True kept (custom) - the 0.1.1 default is false"], [ST2[1]], True, 40),
                ("off", [("\npool.later=true\n", "\npool.later=false\n")], [], [ST2[1]], False, 40),
                ("45", [("\nstat.levelFull=50\n", "\nstat.levelFull=45\n")], ["stat.levelFull=45 kept (custom) - the 0.1.1 default is 40"], [ST2[0]], False, 45),
                ("50.0", [("\nstat.levelFull=50\n", "\nstat.levelFull=50.0\n")], ["stat.levelFull=50.0 kept (custom) - the 0.1.1 default is 40"], [ST2[0]], False, 50),
                ("both", [("\npool.later=true\n", "\npool.later=yes\n"), ("\nstat.levelFull=50\n", "\nstat.levelFull=60\n")],
                 ["pool.later=yes kept (custom) - the 0.1.1 default is false", "stat.levelFull=60 kept (custom) - the 0.1.1 default is 40"], [], True, 60)):
            te = lt
            for a_, b_ in edits:
                te = te.replace(a_, b_)
            d, f = case("y-" + name, te.encode("latin-1"))
            Cfg.migrate011()
            mide = rb(f).decode("latin-1")
            res = str(Cfg.migrateStat011()).split("\n")
            check(te != lt and rb(f) == st_upd(mide, chs).encode("latin-1"), "Y(e) %s: the custom line kept, the other updated, every other byte kept" % name)
            check(res == [st_info(chs) if chs else NOCHG] + notes, "Y(e) %s: INFO + note: %s" % (name, res))
            # (0.2.1 harness: the lines are printed on a failure; case() now waits for the kit's save threads first - cfg_quiet)
            check([l.split("\t")[4] for l in clog(d)[6:]] == [c[0] for c in chs], "Y(e) %s: change-log lines only for the updated key (%s)"
                  % (name, [l.split("\t")[1:7] for l in clog(d)]))
            Cfg.load()
            check(bool(Cfg.POOL_LATER) == pl and int(Cfg.LEVEL_FULL) == lf and (("ROLL" in str(Cfg.statText())) == pl),
                  "Y(e) %s: the loader: pool.later %s, levelFull %d, the ready line says so (%s)" % (name, pl, lf, str(Cfg.statText())))
            check(str(Cfg.migrateStat011()) == "", "Y(e) %s: the note is logged once (the next start does nothing)" % name)
        # both lines missing: silent, the marker right under the level marker, the loader's fallback applies
        tm = lt.replace("\npool.later=true\n", "\n").replace("\nstat.levelFull=50\n", "\n")
        d, f = case("y-missing", tm.encode("latin-1"))
        Cfg.migrate011()
        midm = rb(f).decode("latin-1")
        res = str(Cfg.migrateStat011())
        check(tm != lt and res == NOCHG and rb(f) == midm.replace(LVM + "\n", LVM + "\n" + STM + "\n", 1).encode("latin-1") and len(clog(d)) == 6,
              "Y(e) missing: no line -> nothing changed, the marker right under the level marker")
        Cfg.load()
        check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(e) missing: the loader's new fallback = off / 40")

        # (f) the config kit after the update: log op, Undo (set back), the next start keeps the undone values
        CfgPub = J("CfgPub")
        d, f = case("y-kit", live)
        mods = os.path.dirname(d)
        Cfg.migrate011()
        Cfg.migrateStat011()
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyGear")
        lg = [str(x) for x in fn.apply(OA(["log", Integer.valueOf(20)]))]
        check(sum(1 for l in lg if l.endswith("\tupdate\tpool.later\ttrue\tfalse\tok") or l.endswith("\tupdate\tstat.levelFull\t50\t40\tok")) == 2,
              "Y(f): the kit's log op lists the two stat update lines as ok (SkyyMenu offers Undo on them)")
        g1, g2 = fn.apply(OA(["get", "pool.later"])), fn.apply(OA(["get", "stat.levelFull"]))
        check("false" in str(g1) and "40" in str(g2), "Y(f): kit memory = the updated file (%s / %s)" % (g1, g2))
        u1 = fn.apply(OA(["set", "pool.later", "true", None, "console", "yes", "console"]))
        u2 = fn.apply(OA(["set", "stat.levelFull", "50", None, "console", "yes", "console"]))
        CfgPub.flush()
        kt2 = rb(f).decode("latin-1")
        check(str(u1[0]) == "ok" and str(u2[0]) == "ok" and "\npool.later=true\n" in kt2 and "\nstat.levelFull=50\n" in kt2 and STID in kt2,
              "Y(f): Undo (set back to the old value) of both update lines works, the marker stays")
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and rb(f).decode("latin-1") == kt2,
              "Y(f): values set back after the update survive the next start")
        Cfg.load()
        check(bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 50 and "ROLL" in str(Cfg.statText()),
              "Y(f): the loader after the undo: on / 50, the ready line says coming-later stats ROLL")
        # (g) the whole live start with History blocked: both updates WARN, nothing is written
        d, f = case("y-nohist-live", live)
        open(os.path.join(d, "config-history"), "wb").write(b"blocker")
        glf = os.path.join(XD, "y-gear-live.log")
        Log.FILE = Paths.get(glf)
        ra, rb2 = str(Cfg.migrate011()), str(Cfg.migrateStat011())
        Log.flush()
        Log.FILE = None
        gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
        check(ra == "" and rb2 == "" and rb(f) == live and not os.path.exists(os.path.join(d, "config-changes.log")),
              "Y(g): live start with History blocked -> the file stays the 0.1 file byte for byte")
        check("NOT updated to the 0.1.1 level table" in gl and "NOT updated to the 0.1.1 stat defaults" in gl, "Y(g): two WARN lines (%r)" % gl)

    # (g) History blocked on a file that only needs the stat update, then writable again; a failed write; no anchor
    ty = (H + LVM + "\nlevel.material.Iron=15\n# Roll coming-later stats: x\npool.later=true\nstat.levelFull=50\n").encode("latin-1")
    d, f = case("y-nohist", ty)
    open(os.path.join(d, "config-history"), "wb").write(b"blocker")
    glf = os.path.join(XD, "y-gear.log")
    Log.FILE = Paths.get(glf)
    res = str(Cfg.migrateStat011())
    Log.flush()
    Log.FILE = None
    gl = open(glf, encoding="utf-8").read() if os.path.isfile(glf) else ""
    check(res == "" and rb(f) == ty and not os.path.exists(os.path.join(d, "config-changes.log")) and not os.path.exists(f + ".tmp"),
          "Y(g): config-history cannot be written -> file untouched, no change-log lines")
    check("WARN config.properties NOT updated to the 0.1.1 stat defaults: the old file could not be kept in " in gl
          and "(the file is used as it is; the next start tries again)" in gl and "CONFIG 0.1.1" not in gl, "Y(g): the WARN says why + retry: %r" % gl)
    Cfg.load()
    check(bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 50, "Y(g): the untouched file is used as it is until the update can run")
    os.remove(os.path.join(d, "config-history"))
    res = str(Cfg.migrateStat011())
    b = baks(d)
    check(res == STINFO and len(b) == 1 and rb(os.path.join(d, "config-history", b[0])) == ty and len(clog(d)) == 2
          and rb(f) == st_upd(ty.decode("latin-1"), ST2).encode("latin-1"), "Y(g): the next start (History writable) updates: %r" % res)
    Cfg.load()
    check(not bool(Cfg.POOL_LATER) and int(Cfg.LEVEL_FULL) == 40, "Y(g): then off / 40")
    d, f = case("y-retry", ty)
    os.makedirs(f + ".tmp")
    ok1 = str(Cfg.migrateStat011()) == "" and rb(f) == ty and len(baks(d)) == 1 and not os.path.exists(os.path.join(d, "config-changes.log"))
    os.rmdir(f + ".tmp")
    res = str(Cfg.migrateStat011())
    check(ok1 and res == STINFO and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 2,
          "Y(g): a failed write keeps the file; the retry updates without a second History copy: %r" % res)
    d, f = case("y-noanchor", b"a=1\nb=2\n")
    check(str(Cfg.migrateStat011()) == "" and rb(f) == b"a=1\nb=2\n" and not os.path.exists(os.path.join(d, "config-history")),
          "Y(g): no stat line and no level marker -> WARN, untouched (unreachable after migrate011)")
    res1, res2 = str(Cfg.migrate011()), str(Cfg.migrateStat011())
    check(res2 == NOCHG and rb(f) == ("a=1\nb=2\n" + LVM + "\n" + STM + "\n").encode("ascii"), "Y(g): in the setup order the marker goes under the level marker")

    # (h) the pure text step on edge cases
    def st(t):
        r_ = Cfg.stUpdate(t)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])

    r = st("pool.later = true\nstat.levelFull:50   \n")
    check(r[0] == STM + "\npool.later = false\nstat.levelFull:40\n" and r[3] == ["pool.later", "true", "false", "stat.levelFull", "50", "40"]
          and r[1] == "pool.later true -> false (%s), stat.levelFull 50 -> 40 (%s)" % (WHY["pool.later"], WHY["stat.levelFull"]),
          "Y(h): spacing, ':' separator, trailing spaces: value text replaced only; the marker above the first entry (%r)" % (r,))
    check(st("a=1\n# help\npool.later=true\n")[0] == "a=1\n" + STM + "\n# help\npool.later=false\n", "Y(h): a help comment right on top -> above it")
    check(st("# help\n\npool.later=true\n")[0] == "# help\n\n" + STM + "\npool.later=false\n", "Y(h): a blank line between -> right above the entry")
    check(st("a=x" + BS + "\n# no comment\npool.later=true\n")[0] == "a=x" + BS + "\n# no comment\n" + STM + "\npool.later=false\n",
          "Y(h): a continuation line that looks like a comment is not a help comment")
    r = st("pool.later=true\nx=1\npool.later=on\n")
    check(r[0] == STM + "\npool.later=true\nx=1\npool.later=on\n" and r[3] == [] and r[2] == ["pool.later=on kept (custom) - the 0.1.1 default is false"],
          "Y(h): last line wins - custom on kept, the dead true left")
    r = st("pool.later=on\npool.later=true\n")
    check(r[0] == STM + "\npool.later=on\npool.later=false\n" and r[3] == ["pool.later", "true", "false"], "Y(h): last line true -> updated")
    r = st("pool.later=tr" + BS + "\n    ue\nstat.levelFull=50\n")
    check(r[0] == STM + "\npool.later=tr" + BS + "\n    ue\nstat.levelFull=40\n" and r[3] == ["stat.levelFull", "50", "40"]
          and r[2] == ["pool.later=true kept (custom) - the 0.1.1 default is false"], "Y(h): a continued entry is never rewritten (noted)")
    r = st(LVM + "\n#pool.later=true\n! stat.levelFull=50\n")
    check(r[0] == LVM + "\n" + STM + "\n#pool.later=true\n! stat.levelFull=50\n" and r[1] == "" and r[2] == [] and r[3] == [],
          "Y(h): commented / template lines never change; no entry -> the marker right under the level marker")
    r = st("POOL.LATER=true\nstat.levelfull=50\n" + LVM + "\n")
    check(r[0] == "POOL.LATER=true\nstat.levelfull=50\n" + LVM + "\n" + STM + "\n" and r[3] == [] and r[2] == [],
          "Y(h): keys are case-sensitive like the loader (other-case lines are not the setting and stay)")
    check(st(LVM)[0] == LVM + "\n" + STM and st("a=1\r\n" + LVM)[0] == "a=1\r\n" + LVM + "\r\n" + STM
          and st(LVM + "\r\nb=2\r\n")[0] == LVM + "\r\n" + STM + "\r\nb=2\r\n", "Y(h): under the level marker: no final newline stays so, CRLF kept")
    check(st("a=1\r\npool.later=true")[0] == "a=1\r\n" + STM + "\r\npool.later=false", "Y(h): the marker takes the file's CRLF above a last line")
    check(Cfg.stUpdate("# SkyyGear 0.1.1 stat defaults, anything\npool.later=true\n") is None
          and Cfg.stUpdate("x=1\n  ! SkyyGear 0.1.1 stat defaults\n") is None, "Y(h): a comment line with the marker id = already done")
    r = st("note=SkyyGear 0.1.1 stat defaults\npool.later=true\n")
    check(r is not None and "\npool.later=false\n" in r[0], "Y(h): the marker id inside a value does not count")
    r = st("stat.levelFull=40\npool.later=false\n")
    check(r[0] == STM + "\nstat.levelFull=40\npool.later=false\n" and r[1] == "" and r[2] == [] and r[3] == [], "Y(h): already the new defaults: silent")
    try:
        Cfg.stUpdate("a=1\nb=2\n")
        thrown = False
    except Exception:
        thrown = True
    check(thrown, "Y(h): no entry and no level marker -> refused (the caller WARNs)")
    # random files (fixed seed): the level marker first, then pieces with odd / even backslashes, comments, blanks, stat lines,
    # LF / CRLF, with / without final newline: Properties values = before + the updated rows, the marker = one comment line and the only
    # line added, the next pass does nothing
    rnd2 = random.Random(20260930 + 11)
    spieces = ["a=1", "b=x" + BS, "c=y" + BS + BS, "#c" + BS, "# note", "", "   z" + BS, "d:e", "  f g" + BS, "!x" + BS, "# help",
               "pool.later=true", "pool.later=on", "pool.later = true", "stat.levelFull=50", "stat.levelFull = 45", "stat.levelFull:50"]

    def st_ok(t, out, rows):
        want_ = props(t)
        for i_ in range(0, len(rows), 3):
            want_[rows[i_]] = rows[i_ + 2]
        got_ = props(out)
        return (got_ == want_ and not any(STID in k_ or STID in v_ for k_, v_ in got_.items()) and Cfg.stUpdate(out) is None
                and out.count(STID) == 1)

    def st_bytes(t, out):
        ol, tl = out.split("\n"), t.split("\n")
        mi = [i_ for i_, x_ in enumerate(ol) if STID in x_]
        if len(mi) != 1 or ol[mi[0]].rstrip("\r") != STM:
            return False
        m_ = mi[0]
        rest = ol[:m_] + ol[m_ + 1:]
        if len(rest) != len(tl):
            return False
        for i_, (a_, b_) in enumerate(zip(rest, tl)):
            if a_ == b_ or (a_.startswith(("pool.later", "stat.levelFull")) and b_.startswith(("pool.later", "stat.levelFull"))):
                continue
            if i_ == len(tl) - 1 and m_ == len(ol) - 1 and a_ == b_ + "\r":
                continue
            return False
        return True

    bad = []
    for n_ in range(2000):
        ls_ = [LVM] + [rnd2.choice(spieces) for _q in range(rnd2.randint(0, 8))]
        nl_ = "\r\n" if rnd2.random() < 0.3 else "\n"
        t = nl_.join(ls_) + (nl_ if rnd2.random() < 0.6 else "")
        r = st(t)
        if r is None or not st_ok(t, r[0], r[3]) or not st_bytes(t, r[0]):
            bad.append(t)
    check(not bad, "Y(h): 2000 random files: same Properties values (+ updated rows), the marker = one comment line and the only line added, "
                   "the next pass does nothing (%d bad, first %r)" % (len(bad), bad[:1]))

    # (i) EVERY roll path with pool.later off (the loader default) never yields a coming-later stat
    later = set(SK[i] for i in range(int(Defs.NS)) if int(Defs.S_LIVE[i]) == 0)
    check(len(later) == 19 and {"fer", "thorns", "weak", "as", "lbonus", "xpb"} <= later, "Y(i): 19 coming-later stats: %s" % sorted(later))
    p = Props()
    p.setProperty("gear.include", "Skyy_Ring_")
    p.setProperty("kind.prefix.Skyy_Ring_", "equipment")
    Cfg.apply(p, False)
    check(not bool(Cfg.POOL_LATER), "Y(i): pool.later is off from the loader default")
    w0 = [int(v) for v in Cfg.S_W]
    wa = JArray(JInt)(len(w0))
    for i in range(len(w0)):
        wa[i] = 100000 if SK[i] in later else w0[i]
    Cfg.S_W = wa                       # one leak would dominate: every coming-later stat outweighs every live one 1000+ to 1

    def keys_of(dd):
        return [str(m.asDocument().getString("s").getValue()) for m in Data.mods(dd)]

    def doc_of(s_):
        return Data.gearDoc(s_.getMetadata())

    tally = {}

    def seen(path, dd):
        t_ = tally.setdefault(path, [0, 0, []])
        ks_ = keys_of(dd) if dd is not None else []
        t_[0] += 1
        t_[1] += len(ks_)
        t_[2] += [k_ for k_ in ks_ if k_ in later]

    IDS = ["Weapon_Sword_Iron", "Weapon_Shortbow_Crude", "Weapon_Staff_Wood", "Weapon_Spellbook_Frost", "Weapon_Daggers_Crude",
           "Armor_Mithril_Chest", "Armor_Iron_Head", "Skyy_Ring_Gold"]
    check(sorted(set(int(Data.slotOf(i)) for i in IDS)) == [0, 1, 2, 4], "Y(i): the test items cover weapon, spell weapon, armor, Equipment")
    # control: with pool.later ON the same weights make coming-later stats show up on every path shape (the detector works)
    Cfg.POOL_LATER = True
    ctl = sum(1 for _ in range(40) for k_ in keys_of(Roll.newDoc("Armor_Mithril_Chest", 5, True, "admin")) if k_ in later)
    ctl2 = sum(1 for _ in range(40) for k_ in keys_of(Roll.craftDoc("Skyy_Ring_Gold", U1)) if k_ in later)
    Cfg.POOL_LATER = False
    check(ctl > 100 and ctl2 > 0, "Y(i): control run with pool.later ON: coming-later stats roll (%d on 40 Mythic armor pieces, %d on rings)" % (ctl, ctl2))
    # 1. the roll itself: every slot, rarity, level
    for slot in (0, 1, 2, 4):
        for rr in range(7):
            for lvl in (0, 15, 40, 100):
                for _ in range(60):
                    arr = Roll.rollMods(slot, rr, lvl)
                    dd = BD()
                    dd.put("mods", arr)
                    seen("GearRoll.rollMods (every slot / rarity / level)", dd)
    # 2. /gear give (newDoc) and crafting (craftDoc = GearCraftSys on the benches)
    for iid in IDS:
        for rr in range(7):
            for _ in range(30):
                seen("/gear give (GearRoll.newDoc)", Roll.newDoc(iid, rr, True, "admin"))
        for _ in range(150):
            seen("crafting (GearRoll.craftDoc)", Roll.craftDoc(iid, U1))
    # 3. the bench per-item roll (GearCraftTask.rollIn) on a stack of spears
    for _ in range(40):
        ch_, cs_ = SIC(9), SIC(36)
        ch_.setItemStackForSlot(2, IS("Weapon_Spear_Crude", 3))
        CraftTask.rollIn(JArray(IC)([ch_, cs_]), JArray(IC)([cs_]), U1, "Weapon_Spear_Crude", IdMap(), 3, None, None)
        for x_ in [ch_.getItemStack(2)] + [cs_.getItemStack(i) for i in range(36)]:
            if x_ is not None and not x_.isEmpty():
                seen("bench craft per item (GearCraftTask.rollIn)", doc_of(x_))
    # 4. the SkyySacks /craft bridge gear:fn:roll (craft rolls + another source). setup() is not run here: the same GearFn objects it
    # puts on the bridge (gear:fn:roll = new GearFn(8), gear:fn:unid = new GearFn(9) - checked in the setup() bytecode)
    su_ = code("SkyyGearPlugin", "setup")
    fi_r = next((i_ for i_, l_ in enumerate(su_) if '"gear:fn:roll"' in l_), -1)
    fi_u = next((i_ for i_, l_ in enumerate(su_) if '"gear:fn:unid"' in l_), -1)
    check(fi_r > 0 and any("bipush 8" in l_ for l_ in su_[fi_r:fi_r + 4]) and fi_u > 0 and any("bipush 9" in l_ for l_ in su_[fi_u:fi_u + 4]),
          "Y(i): setup() registers gear:fn:roll = GearFn(8), gear:fn:unid = GearFn(9)")
    froll = J("GearFn")(8)
    for iid in IDS[:6]:
        for src in ("craft", "sacks"):
            outs = froll.apply(OA([U1, iid, Integer.valueOf(64), src]))
            check(outs is not None and len(outs) == 64, "Y(i): gear:fn:roll %s x64 for %s" % (src, iid))
            for x_ in outs:
                seen("SkyySacks /craft bridge (gear:fn:roll)", doc_of(x_))
    # 5. mob drops (GearTag.unid, gear:fn:unid) -> the Identify page (GearIdent.identify, paid) and /gear identify (GearRoll.identify)
    bridge.put("coins:fn:take", Take())
    bridge.put("coins:fn:get", Purse())
    bridge.put("coins:fn:add", Purse())
    funid = J("GearFn")(9)
    Cfg.PART_DROPS = True
    for iid in IDS:
        for _ in range(40):
            s_ = Tag.unid(IS(iid, 1), 1)
            dd = doc_of(s_)
            check(dd is not None and not bool(Data.identified(dd)) and keys_of(dd) == [], "Y(i): a mob drop is unidentified without modifiers") if _ == 0 else None
            c_, g_ = SIC(9), SIC(9)
            c_.setItemStackForSlot(0, s_)
            ri = Ident.identify(c_, 0, iid, Forge.fp(c_.getItemStack(0)), U1, "tester", False, JArray(IC)([g_]), JArray(IC)([c_, g_]))
            if int(ri[0]) != 1:
                check(False, "Y(i): Identify page refused %s: %s" % (iid, ri[1]))
                continue
            seen("mob drop -> Identify page (GearTag.unid + GearIdent.identify)", doc_of(c_.getItemStack(0)))
            s2_ = funid.apply(OA([IS(iid, 1), "mob"]))
            seen("mob drop -> /gear identify (gear:fn:unid + GearRoll.identify)", Roll.identify(iid, doc_of(s2_), U1))
    # 6. loot chests (GearTag.tagContainer) -> Identify all (GearIdent.allIn)
    for _ in range(15):
        chest = SIC(27)
        chest.setItemStackForSlot(0, IS("Weapon_Spellbook_Demon", 4))
        for j_, iid in enumerate(IDS[:4] + IDS[5:7]):
            chest.setItemStackForSlot(10 + j_, IS(iid, 1))
        Tag.tagContainer(chest, "test")
        by_ = JArray(IC)(6)
        by_[0] = chest
        rows_ = ArrayList()
        for sl in range(27):
            x_ = chest.getItemStack(sl)
            if x_ is not None and not x_.isEmpty():
                rr_ = JArray(JInt)(2)
                rr_[0] = 0
                rr_[1] = sl
                rows_.add(rr_)
        Ident.allIn(by_, rows_, U1, "tester", ArrayList())
        for sl in range(27):
            x_ = chest.getItemStack(sl)
            if x_ is not None and not x_.isEmpty():
                dd = doc_of(x_)
                if dd is not None and bool(Data.identified(dd)):
                    seen("loot chest -> Identify all (GearTag.tagContainer + GearIdent.allIn)", dd)
    # 7. reforge: the Reforge page (paid) and /gear reroll (free) on gear that HAS a coming-later stat; GearRoll.reforge itself
    def with_fer(iid):
        dd = Roll.newDoc(iid, 3, True, "admin")
        arr = JClass("org.bson.BsonArray")()
        arr.add(Data.mod("fer", 5))
        arr.add(Data.mod("dmg", 3))
        dd.put("mods", arr)
        return dd

    for iid in IDS:
        for free in (False, True):
            for _ in range(40):
                c_, g_ = SIC(9), SIC(9)
                c_.setItemStackForSlot(0, Data.put(IS(iid, 1), with_fer(iid), U1))
                rf_ = Forge.reforge(c_, 0, iid, Forge.fp(c_.getItemStack(0)), U1, "tester", free, JArray(IC)([g_]), JArray(IC)([c_, g_]))
                if int(rf_[0]) != 1:
                    check(False, "Y(i): reforge refused %s: %s" % (iid, rf_[1]))
                    continue
                seen("/gear reroll (GearForge.reforge, free)" if free else "Reforge page (GearForge.reforge, paid)", doc_of(c_.getItemStack(0)))
        for _ in range(30):
            seen("GearRoll.reforge", Roll.reforge(iid, with_fer(iid)))
    for k in ("coins:fn:take", "coins:fn:get", "coins:fn:add"):
        bridge.remove(k)
    # 8. SkyyRolls migration (GearData.migrate, the in-memory view GearData.effective, the passive stamp GearStamp.stampStack)
    BI2 = JClass("org.bson.BsonInt32")
    rng3 = random.Random(7)
    for mb in ("stats", "roll", "item"):
        Cfg.MIGRATE_BY = mb
        for _ in range(60):
            ro = BD()
            ro.append("dmg", BI2(rng3.randint(0, 30)))
            ro.append("str", BI2(rng3.randint(0, 25)))
            ro.append("crit", BI2(rng3.randint(0, 15)))
            ro.append("quality", BI2(rng3.randint(0, 100)))
            iid = rng3.choice(IDS[:7])
            seen("SkyyRolls migration (GearData.migrate)", Data.migrate(iid, ro))
            md_ = BD()
            md_.append("SkyyRolls", ro)
            seen("SkyyRolls migration (GearData.effective)", Data.effective(iid, md_))
            seen("SkyyRolls migration (GearStamp.stampStack)", doc_of(Stamp.stampStack(IS(iid, 1).withMetadata(md_), U1, None)))
    Cfg.MIGRATE_BY = "stats"
    for path_, (n_items, n_mods, leaks) in sorted(tally.items()):
        check(n_items > 0 and n_mods > 0 and not leaks, "Y(i): %s: %d items / %d modifiers, %d coming-later (%s)" % (path_, n_items, n_mods, len(leaks), sorted(set(leaks))[:5]))
    print("Y. roll paths with pool.later off: " + "; ".join("%s %d/%d" % (p_, v_[0], v_[1]) for p_, v_ in sorted(tally.items())))
    # gear that already has one keeps it until its next reforge (the lock): a split / the passive scan copy the document, no roll
    kd = with_fer("Weapon_Sword_Iron")
    ks_ = Data.put(IS("Weapon_Sword_Iron", 1), kd, U1)
    check("fer" in keys_of(doc_of(Stamp.stampStack(ks_, U1, None))) and "fer" in keys_of(Stamp.splitDoc("Weapon_Sword_Iron", ks_.getMetadata(), 0, U1)),
          "Y(i): gear that already has a coming-later stat keeps it (passive stamp, stack split)")
    check(any("(coming later)" in str(x) for x in View.plain("Weapon_Sword_Iron", kd, None)), "Y(i): ... shown '(coming later)' in its tooltip")
    check("fer" not in keys_of(Roll.reforge("Weapon_Sword_Iron", kd)), "Y(i): ... and loses it on its next reforge")
    # the bytecode: GearRoll.pool is the only way into a roll - pool <- rollMods only; GearData.mod <- rollMods + migrate only;
    # rollMods <- newDoc / reforge / identify only (every path above ends in one of these)
    callers = {}
    for cn in names:
        if not cn.startswith(PKG):
            continue
        for mm in pool.get(cn).getDeclaredMethods():
            bo_ = BOS()
            IP(PS(bo_)).print_(mm)
            tx_ = str(bo_.toString())
            for callee in ("GearRoll.pool(", "GearData.mod(", "GearRoll.rollMods(", "GearRoll.newDoc(", "GearRoll.reforge(", "GearRoll.identify(",
                           "GearRoll.craftDoc(", "GearRoll.unidDoc("):
                if ("gear." + callee) in tx_:
                    callers.setdefault(callee, set()).add(cn[len(PKG):] + "." + str(mm.getName()))
    # 0.1.2: pool(slot, id) / rollMods(id, ...) got the item id; the old signatures stay as one-line overloads (Z9 checks by signature)
    check(callers.get("GearRoll.pool(") == {"GearRoll.rollMods", "GearRoll.pool"}, "Y(i): GearRoll.pool is called by rollMods (+ its own overload) only: %s" % callers.get("GearRoll.pool("))
    check(callers.get("GearData.mod(") == {"GearRoll.rollMods", "GearData.migrate"}, "Y(i): GearData.mod (a new modifier) only in rollMods + migrate: %s" % callers.get("GearData.mod("))
    check(callers.get("GearRoll.rollMods(") == {"GearRoll.newDoc", "GearRoll.reforge", "GearRoll.identify", "GearRoll.rollMods"},
          "Y(i): rollMods is called by newDoc / reforge / identify only: %s" % callers.get("GearRoll.rollMods("))
    print("Y. roll entry points (bytecode): " + "; ".join("%s <- %s" % (k_[:-1], ", ".join(sorted(v_))) for k_, v_ in sorted(callers.items())
                                                         if k_ in ("GearRoll.newDoc(", "GearRoll.reforge(", "GearRoll.identify(", "GearRoll.craftDoc(", "GearRoll.unidDoc(")))
    Cfg.apply(Props(), False)
    Cfg.FILE = None
    Cfg.DIR = None
    print("Y. 0.1.1 stat defaults + update + roll paths done")

    # ================================================================================================================================
    # Z. 0.1.2 Charged Attack Damage (OPEN-QUESTIONS LOCKED 2026-09-30, research/Charged-Attack-Research.md + the verifier's cases)
    # ================================================================================================================================
    Chg, Hand, Charged = J("GearChg"), J("GearHand"), J("GearCharged")
    I_CHG = si("chg")
    Cfg.apply(Props(), False)
    Cfg.FILE = None
    Cfg.DIR = None
    Log.FILE = None
    # ---- Z1. the stat row, the config rows, the loader, the default file, the tooltip
    check(I_CHG == si("cd") + 1 and int(Defs.I_CHG) == I_CHG and int(Hit.I_CHG) == I_CHG, "Z1: chg sits right after cd; I_CHG constants")
    check(str(Defs.S_LABEL[I_CHG]) == "Charged Attack Damage" and str(Defs.S_SLOT[I_CHG]) == "wa" and str(Defs.S_UNIT[I_CHG]) == "%"
          and int(Defs.S_MAXDEF[I_CHG]) == 30 and int(Defs.S_WDEF[I_CHG]) == 5 and int(Defs.S_LIVE[I_CHG]) == 1 and str(Defs.S_SUF[I_CHG]) == ""
          and int(Cfg.S_MAX[I_CHG]) == 30 and int(Cfg.S_W[I_CHG]) == 5, "Z1: STATS row chg (weapons + armor, %, max 30, weight 5, live)")
    zk = [str(k) for k in Rows.KEYS]
    zcol = lambda arr: dict(zip(zk, [str(x) for x in arr]))
    zt, zd, zf, zh, zu, zmin, zmax = (zcol(Rows.TYPES), zcol(Rows.DEFS), zcol(Rows.FLAGS), zcol(Rows.HELPS), zcol(Rows.UNITS), zcol(Rows.MINS),
                                      zcol(Rows.MAXS))
    check(zt.get("charged.on") == "bool" and zd.get("charged.on") == "true" and zf.get("charged.on") == "live"
          and zh.get("charged.on") == "Charged Attack Damage boosts fully charged hits. Off = it does nothing and never rolls.",
          "Z1: row charged.on (bool, default on, live)")
    check(zt.get("charged.spellFactor") == "dec" and zd.get("charged.spellFactor") == "0.15" and zmin.get("charged.spellFactor") == "0"
          and zmax.get("charged.spellFactor") == "1" and zu.get("charged.spellFactor") == "x" and "danger" in zf.get("charged.spellFactor", "").split(",")
          and "Placeholder" not in zh.get("charged.spellFactor", "") and "(Skyy)" in zh.get("charged.spellFactor", ""),
          "Z1: row charged.spellFactor (dec 0.15, 0-1, x, danger, Skyy's number - no Placeholder claim)")
    check(zt.get("charged.log") == "bool" and zd.get("charged.log") == "false" and "adv" in zf.get("charged.log", "").split(","),
          "Z1: row charged.log (bool, off, advanced)")
    check(all(len(zh[k]) <= 100 for k in ("charged.on", "charged.spellFactor", "charged.log")), "Z1: help texts <= 100 characters")
    check(bool(Cfg.CHG_ON) and abs(float(Cfg.CHG_SPELL) - 0.15) < 1e-12 and not bool(Cfg.CHG_LOG), "Z1: built-in defaults on / 0.15 / off")
    for txt, want in ((("charged.on", "off"), ("charged.spellFactor", "2"), ("charged.log", "yes")), (False, 1.0, True)), \
                     ((("charged.spellFactor", "-1"),), (True, 0.0, False)), ((("charged.spellFactor", "abc"), ("charged.on", "maybe")), (True, 0.15, False)):
        pz = Props()
        for k_, v_ in txt:
            pz.setProperty(k_, v_)
        Cfg.apply(pz, True)
        check((bool(Cfg.CHG_ON), round(float(Cfg.CHG_SPELL), 6), bool(Cfg.CHG_LOG)) == want, "Z1: loader %s -> %s (clamps / defaults)" % (txt, want))
    Cfg.apply(Props(), False)
    zdt = str(Cfg.defaultsText())
    zdl = zdt.split("\n")
    CHM = str(Cfg.CH_MARK)
    check(CHM == "# SkyyGear 0.1.2 charged attack lines (Skyy 2026-09-30): Charged Attack Damage on weapons with a charged attack + armor, "
          "bows only the glowing full draw, spells x 0.15, never clubs" and str(Cfg.CH_WHO) == "SkyyGear 0.1.2", "Z1: the 0.1.2 marker text + name")
    check(zdl[zdl.index("stats.cd=30,10") + 1:zdl.index("stats.cd=30,10") + 3] == ["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5"]
          and zdl[zdl.index("speed.per=1") + 1] == CHM and zdl[zdl.index("speed.per=1") + 2:zdl.index("speed.per=1") + 8:2] == [
              "# Charged Attack Damage in combat: " + zh["charged.on"], "# Charged bonus on spells: " + zh["charged.spellFactor"],
              "# Log charged hits: " + zh["charged.log"]]
          and zdl[zdl.index("speed.per=1") + 3:zdl.index("speed.per=1") + 9:2] == ["charged.on=true", "charged.spellFactor=0.15", "charged.log=false"]
          and zdt.count(str(Cfg.CH_MARK_ID)) == 1 and zdt.startswith("# SkyyGear %s - " % VERSION),
          "Z1: fresh default file: stats.chg under stats.cd, the marker + the three rows under speed.per")
    check(str(View.modLine("chg", 12)) == "Charged Attack Damage: +12%" and not bool(View.dim("chg")), "Z1: tooltip line 'Charged Attack Damage: +12%'")
    Cfg.CHG_ON = False
    check(str(View.modLine("chg", 12)) == "Charged Attack Damage: +12% (off on this server)" and bool(View.dim("chg")) and not bool(View.dim("cd")),
          "Z1: charged.on off -> the line says so and is grey")
    Cfg.CHG_ON = True
    print("Z1. stat row + config rows + loader + default file + tooltip done")

    # ---- Z2. hitAmount: one separate factor after Strength / Magical Power, before the crit roll; spells x charged.spellFactor
    def tz(**kw):
        a_ = JArray(JInt)(int(Defs.NS))
        for k_, v_ in kw.items():
            a_[si(k_)] = v_
        return a_
    t0 = tz(chg=30, str=10, mp=20)
    HA = Hit.hitAmount
    check(abs(float(HA(100.0, t0, False, False, 0.9, 0.9)) - 110.0) < 1e-9 and float(HA(100.0, t0, False, 0.9, 0.9)) == float(HA(100.0, t0, False, False, 0.9, 0.9)),
          "Z2: not charged = 100 x 1.10 (Strength) - the 5-argument hitAmount is the same")
    check(abs(float(HA(100.0, t0, False, True, 0.9, 0.9)) - 143.0) < 1e-9, "Z2: charged melee / bow = 100 x 1.10 x 1.30 = 143")
    check(abs(float(HA(100.0, t0, True, True, 0.9, 0.9)) - 100.0 * 1.20 * 1.045) < 1e-9, "Z2: charged spell = 100 x 1.20 (Magical Power) x (1 + 0.15 x 30%) = 125.4")
    check(abs(float(HA(100.0, t0, True, False, 0.9, 0.9)) - 120.0) < 1e-9, "Z2: uncharged spell = 100 x 1.20")
    Cfg.CHG_SPELL = 0.5
    check(abs(float(HA(100.0, t0, True, True, 0.9, 0.9)) - 100.0 * 1.2 * 1.15) < 1e-9, "Z2: the spell share follows charged.spellFactor (0.5 -> x 1.15)")
    Cfg.CHG_SPELL = 0.15
    tc = tz(chg=30, str=10, cc=100, cd=0)
    check(abs(float(HA(100.0, tc, False, True, 0.0, 0.9)) - 286.0) < 1e-9 and abs(float(HA(100.0, tc, False, False, 0.0, 0.9)) - 220.0) < 1e-9,
          "Z2: a charged crit gets both (143 x 2 = 286; uncharged crit 220)")
    to = tz(chg=30, cc=150)
    check(abs(float(HA(100.0, to, False, True, 0.0, 0.1)) - 520.0) < 1e-9, "Z2: overcrit after the charged factor (100 x 1.3 x 2 x 2)")
    check(float(HA(100.0, tz(chg=-200), False, True, 0.9, 0.9)) == 0.0 and float(HA(100.0, tz(chg=-50), False, True, 0.9, 0.9)) == 50.0,
          "Z2: the factor is clamped at 0 (gear:extra may be negative), never below 0")
    te = tz(chg=30, tdmg=5, fFire=6, rElem=1)
    check(float(HA(100.0, te, False, True, 0.9, 0.9)) == float(HA(100.0, tz(chg=30), False, True, 0.9, 0.9)) == 130.0,
          "Z2: True Damage and element lines are not in the multiplied amount")
    ie = Hit.info(U1, te)
    check(int(ie[1]) == 5 and int(ie[5]) == 11, "Z2: ... they travel unmultiplied to GearTrueSys (info: True 5, elements 6 + 5 x 1 = 11)")
    print("Z2. hitAmount maths done")

    # ---- Z3. the calculator index built from the REAL Assets.zip. The build's own Python walk (exec'd from the build script, so it
    # is the same code the build self-check ran) resolves every weapon item from the raw JSON; the same JSON is turned into real engine
    # objects (ChargingInteraction, ReplaceInteraction, SerialInteraction, SimpleInteraction, DamageEntityInteraction + DamageCalculator
    # / Angled / Targeted, ProjectileInteraction + ProjectileConfig, LaunchProjectileInteraction, RootInteraction; one object per asset
    # id or inline JSON object = the engine's sharing) in fake Interaction / RootInteraction / ProjectileConfig / Item asset maps; then
    # the JAR walks them with the ENGINE's InteractionManager.walkChain (GearChg.ensure -> GearChgWalk). Both answers must agree per
    # calculator object for every vanilla weapon + the pack's More Crossbow Tiers crossbows.
    import zipfile as _zf
    bsrc = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    wz = {}
    exec(bsrc[bsrc.index("# ---- CHARGED WALKER BEGIN"):bsrc.index("# ---- CHARGED WALKER END")], wz)
    AzWalker = wz["AzWalker"]
    AZP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    azz = _zf.ZipFile(AZP)
    mct = {}
    mctp = mct_zip(B.MODS_DIR) or os.path.join(B.MODS_DIR, "More_Crossbow_Tiers.zip")    # 0.2.2: the zip is More_Crossbow_Tiers_0.6.8.zip now
    if os.path.isfile(mctp):
        with _zf.ZipFile(mctp) as zz_:
            for n_ in zz_.namelist():
                if n_.startswith("Server/Item/Items/") and n_.endswith(".json"):
                    mct[os.path.basename(n_)[:-5]] = json.loads(zz_.read(n_).decode("utf-8-sig"))
    WK = AzWalker(azz, azz.namelist(), mct)
    VAN = sorted(i for i in WK.items if i.startswith("Weapon_") and not str(WK.items[i]).startswith("overlay:"))
    PACKI = sorted(mct)
    check(sorted([str(x) for x in Chg.TRUST]) == sorted(set(VAN) | set(PACKI)) and len(PACKI) in (0, 4),
          "Z3: the jar's trust list = every vanilla weapon id + the pack's More Crossbow Tiers ids (%d + %d)" % (len(VAN), len(PACKI)))
    ufz = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    ufz.setAccessible(True)
    UZ = ufz.get(None)
    FKC = store.getClass()          # the fake AssetStore class made at the start (only getAssetMap() is ever used)
    ASz = JClass("com.hypixel.hytale.assetstore.AssetStore")

    def fz(cls, name):
        f_ = cls.class_.getDeclaredField(name)
        f_.setAccessible(True)
        return f_

    def zstore(amap):
        st_ = UZ.allocateInstance(FKC)
        fz(ASz, "assetMap").set(st_, amap)
        return st_

    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    Inter, RootI = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    ChargingI, SerialI, ReplaceI, SimpleI = (JClass(PI + "client.ChargingInteraction"), JClass(PI + "none.SerialInteraction"),
                                             JClass(PI + "none.ReplaceInteraction"), JClass(PI + "SimpleInteraction"))
    DEIz, TGTz, ANGz = (JClass(PI + "server.DamageEntityInteraction"), JClass(PI + "server.DamageEntityInteraction$TargetedDamage"),
                        JClass(PI + "server.DamageEntityInteraction$AngledDamage"))
    DCALCz, DCLSz = JClass(PI + "server.combat.DamageCalculator"), JClass(PI + "server.combat.DamageClass")
    LPIz = JClass(PI + "server.LaunchProjectileInteraction")
    PJIz = JClass("com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction")
    PJCz = JClass("com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig")
    ItemZ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    F2O = JClass("it.unimi.dsi.fastutil.floats.Float2ObjectOpenHashMap")
    O2I = JClass("it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap")
    SLk = JClass("java.util.concurrent.locks.StampedLock")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMz = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    JAWM = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    F_ID = fz(Inter, "id")
    HM = JClass("java.util.HashMap")

    def zalloc(cls, iid=None):
        o_ = UZ.allocateInstance(cls.class_)
        if iid is not None:
            F_ID.set(o_, iid)
        return o_

    def item_ms(iid):
        seen_, cur_ = 0, iid
        while cur_ in WK.items and seen_ < 16:
            d_ = WK.js(WK.items[cur_]) or {}
            if "MaxStack" in d_:
                return int(d_["MaxStack"])
            cur_, seen_ = d_.get("Parent"), seen_ + 1
        return 1

    class Model(object):
        """real engine objects from the JSON, one per interaction key (asset id / inline object identity) like the engine"""
        def __init__(s):
            s.inter, s.roots, s.cfgs, s.bykey, s.rootkey, s.calc, s.n, s.missing = {}, {}, {}, {}, {}, {}, 0, []

        def gen(s, p_):
            s.n += 1
            return "*%s%d" % (p_, s.n)

        def root(s, refs, key=None):
            if key is not None and key in s.rootkey:
                return s.rootkey[key]
            rid = s.gen("root")
            if key is not None:
                s.rootkey[key] = rid
            ids_ = [i_ for i_ in (s.ref(r_) for r_ in refs) if i_]
            s.roots[rid] = RootI(rid, JArray(JString)(ids_))
            return rid

        def serial(s, refs):
            ids_ = [i_ for i_ in (s.ref(r_) for r_ in refs) if i_]
            if not ids_:
                return None
            if len(ids_) == 1:
                return ids_[0]
            sid = s.gen("ser")
            o_ = zalloc(SerialI, sid)
            fz(SerialI, "interactions").set(o_, JArray(JString)(ids_))
            s.inter[sid] = o_
            return sid

        def mkcalc(s, c_, key):
            if not isinstance(c_, dict):
                return None
            o_ = UZ.allocateInstance(DCALCz.class_)
            fz(DCALCz, "damageClass").set(o_, {"Charged": DCLSz.CHARGED, "Signature": DCLSz.SIGNATURE, "Light": DCLSz.LIGHT}.get(
                c_.get("Class", "Unknown"), DCLSz.UNKNOWN))
            s.calc[key] = o_
            return o_

        def simple(s, o_, nx, fl):
            fz(SimpleI, "next").set(o_, s.serial(nx))
            fz(SimpleI, "failed").set(o_, s.serial(fl))

        def ref(s, r_):
            iid, d_, key = WK.interaction(r_)
            if d_ is None:
                s.missing.append(r_ if isinstance(r_, str) else "<inline>")
                return None
            if key in s.bykey:
                return s.bykey[key]
            my = iid if iid is not None else s.gen("inl")
            s.bykey[key] = my
            o = WK.norm(d_)
            if o["charge"] is not None:
                ob = zalloc(ChargingI, my)
                m_ = F2O()
                for k_, rs in o["charge"]:
                    cid = s.serial(rs)
                    if cid:
                        m_.put(JFloat(k_), JString(cid))
                fz(ChargingI, "next").set(ob, m_)
                fz(ChargingI, "failed").set(ob, s.serial(o["failed"]))
            elif o["replace"] is not None:
                ob = zalloc(ReplaceI, my)
                var, dflt_ = o["replace"]
                fz(ReplaceI, "variable").set(ob, var)
                fz(ReplaceI, "defaultValue").set(ob, s.root(dflt_, ("replace", key)) if dflt_ else None)
            elif o["dmg"] is not None:
                ob = zalloc(DEIz, my)
                calc, ang, tgt = o["dmg"]
                fz(DEIz, "damageCalculator").set(ob, s.mkcalc(calc, key + (None,)))
                arr = JArray(ANGz)(len(ang))
                for i_, c_ in enumerate(ang):
                    a_ = UZ.allocateInstance(ANGz.class_)
                    fz(TGTz, "damageCalculator").set(a_, s.mkcalc(c_, key + ("a%d" % i_,)))
                    arr[i_] = a_
                fz(DEIz, "angledDamage").set(ob, arr)
                tm = HM()
                for k_, c_ in tgt.items():
                    t_ = UZ.allocateInstance(TGTz.class_)
                    fz(TGTz, "damageCalculator").set(t_, s.mkcalc(c_, key + ("t:" + k_,)))
                    tm.put(k_, t_)
                fz(DEIz, "targetedDamage").set(ob, tm)
                fz(DEIz, "next").set(ob, s.serial(o["next"]))
                fz(DEIz, "failed").set(ob, s.serial(o["failed"]))
            elif o["proj"] is not None:
                ob = zalloc(PJIz, my)
                cfg = o["proj"]
                cid = cfg if isinstance(cfg, str) else s.gen("cfg")
                if cid not in s.cfgs:
                    pc = UZ.allocateInstance(PJCz.class_)
                    fz(PJCz, "id").set(pc, cid)
                    s.cfgs[cid] = pc
                    im = HM()
                    im.put(ITY.ProjectileHit, s.root(WK.pcfg_hit(cfg), ("cfg", cid)))
                    fz(PJCz, "interactions").set(pc, im)
                fz(PJIz, "config").set(ob, cid)
                s.simple(ob, o["next"], o["failed"])
            elif o["launch"] is not None:
                ob = zalloc(LPIz, my)
                fz(LPIz, "projectileId").set(ob, o["launch"])
                s.simple(ob, o["next"], o["failed"])
            else:
                ob = zalloc(SimpleI, my)
                s.simple(ob, o["next"], o["failed"])
            s.inter[my] = ob
            return my

        def item(s, iid, as_id=None):
            it = WK.item(iid)
            ob = UZ.allocateInstance(ItemZ.class_)
            fz(ItemZ, "id").set(ob, as_id or iid)
            fz(ItemZ, "maxStack").setInt(ob, item_ms(iid))
            im = HM()
            for t_, rr in (it.get("Interactions") or {}).items():
                try:
                    ty = ITY.valueOf(t_)
                except Exception:
                    continue
                im.put(ty, s.root(WK.root_ids(rr), ("iroot", rr) if isinstance(rr, str) else ("iroot", id(rr))))
            vm = HM()
            for var, v_ in (it.get("InteractionVars") or {}).items():
                vm.put(var, s.root(WK.root_ids(v_), ("var", v_) if isinstance(v_, str) else ("var", id(v_))))
            fz(ItemZ, "interactions").set(ob, im)
            fz(ItemZ, "interactionVars").set(ob, vm)
            return ob

    def indexed(entries):
        m_ = UZ.allocateInstance(ILT.class_)
        fz(DAMz, "assetMapLock").set(m_, SLk())
        am_ = HM()
        fz(DAMz, "assetMap").set(m_, am_)
        fz(ILT, "keyToIndexLock").set(m_, SLk())
        kti = O2I()
        kti.defaultReturnValue(-2147483648)
        arr = JArray(JAWM)(len(entries))
        for i_, (k_, v_) in enumerate(entries.items()):
            arr[i_] = v_
            kti.put(JString(k_), JInt(i_))
            am_.put(k_, v_)
        fz(ILT, "keyToIndex").set(m_, kti)
        fz(ILT, "array").set(m_, arr)
        return m_

    MZ = Model()
    ALLW = sorted(set(VAN) | set(PACKI))
    zitems = dict((i, MZ.item(i)) for i in ALLW)
    # two fake third-party items for the verifier's "loose Class tag" case (never vanilla / pack = untrusted): the vanilla crossbow's
    # chains under a modded id, and a sword whose normal swing a mod tagged Class Charged
    zitems["Weapon_Crossbow_Modded"] = MZ.item("Weapon_Crossbow_Iron", "Weapon_Crossbow_Modded")
    loose_calc = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(loose_calc, DCLSz.CHARGED)
    ld = zalloc(DEIz, "*loose_dmg")
    fz(DEIz, "damageCalculator").set(ld, loose_calc)
    fz(DEIz, "angledDamage").set(ld, JArray(ANGz)(0))
    fz(DEIz, "targetedDamage").set(ld, HM())
    MZ.inter["*loose_dmg"] = ld
    MZ.roots["*loose_root"] = RootI("*loose_root", JArray(JString)(["*loose_dmg"]))
    lit = UZ.allocateInstance(ItemZ.class_)
    fz(ItemZ, "id").set(lit, "Weapon_Sword_LooseTag")
    fz(ItemZ, "maxStack").setInt(lit, 1)
    lim = HM()
    lim.put(ITY.Primary, "*loose_root")
    fz(ItemZ, "interactions").set(lit, lim)
    fz(ItemZ, "interactionVars").set(lit, HM())
    zitems["Weapon_Sword_LooseTag"] = lit
    check(not MZ.missing, "Z3: every interaction / root the weapons reference resolves (%s)" % MZ.missing[:5])
    old_inter_store = fz(Inter, "ASSET_STORE").get(None)
    fz(Inter, "ASSET_STORE").set(None, zstore(indexed(MZ.inter)))
    fz(RootI, "ASSET_STORE").set(None, zstore(indexed(MZ.roots)))
    dcf = DAMz()
    for k_, v_ in MZ.cfgs.items():
        fz(DAMz, "assetMap").get(dcf).put(k_, v_)
    fz(PJCz, "ASSET_STORE").set(None, zstore(dcf))
    imap = fz(DAMz, "assetMap").get(store.getAssetMap())
    for k_, v_ in zitems.items():
        imap.put(k_, v_)
    print("Z3. engine model from Assets.zip: %d interactions, %d roots, %d projectile configs, %d items" % (len(MZ.inter), len(MZ.roots),
                                                                                                         len(MZ.cfgs), len(zitems)))
    Chg.clear()
    zsum, zbad = {}, []
    for i in ALLW:
        e = Chg.ensure(i)
        py = WK.summary(i, True)
        zsum[i] = (e, py)
        jc = e[0]
        if not bool(e[7]) or not bool(e[5]):
            zbad.append("%s: walk not ok (%s)" % (i, str(e[4])))
            continue
        for k_, pe in py["calcs"].items():
            jo = MZ.calc.get(k_)
            jf = jc.get(jo) if jo is not None else None
            if jf is None or int(jf[0]) != pe[0] or int(jf[1]) != {"Unknown": 0, "Light": 1, "Charged": 2, "Signature": 3}[pe[1]]:
                zbad.append("%s: calc %s py %s java %s" % (i, k_[-1], pe[:2], None if jf is None else [int(x) for x in jf]))
        if jc.size() != len(py["calcs"]):
            zbad.append("%s: %d java calculators vs %d python" % (i, jc.size(), len(py["calcs"])))
        jl = dict((str(k_), int(e[1].get(k_)[0])) for k_ in e[1].keySet())
        if jl != dict((p_, v_[0]) for p_, v_ in py["launches"].items()):
            zbad.append("%s: launches java %s python %s" % (i, jl, py["launches"]))
        if bool(e[2]) != py["has"] or bool(e[3]) != py["partial"]:
            zbad.append("%s: has/partial java %s/%s python %s/%s" % (i, bool(e[2]), bool(e[3]), py["has"], py["partial"]))
    check(not zbad, "Z3: the jar's engine walk == the build's Python walk for all %d weapons (per calculator flags + class, launches, has, "
                    "partial): %d differences %s" % (len(ALLW), len(zbad), zbad[:6]))
    check(sorted(i for i in ALLW if bool(Chg.hasCharged(i)) and bool(Data.isGear(i))) == sorted(str(x) for x in Chg.FALLBACK),
          "Z3: the runtime eligibility (walk) == the list the build baked (GearChg.FALLBACK, %d items)" % len(Chg.FALLBACK))

    # ---- Z4. the per-hit rule on the real calculators (signal A / B / C, the glow step, the verifier's loose-tag case, exclusions)
    def zcalcs(i, want_flags, cls=None, sub="any"):
        e_, py_ = zsum[i]
        out_ = []
        for k_, pe in py_["calcs"].items():
            if pe[0] == want_flags and (cls is None or pe[1] == cls) and (sub == "any" or pe[2] == sub):
                out_.append((MZ.calc[k_], pe))
        return out_

    WHY = JArray(JString)(1)
    SysId = JClass("java.lang.System").identityHashCode

    def same(a_, b_):
        return a_ is not None and b_ is not None and int(SysId(a_)) == int(SysId(b_))

    def jc(calc, wid, seq=True, shot=False, pid=None, proj=False, alts=None):
        """proj = a projectile hit judged against a launch record; alts = None for the projectile's own record (find), else the item
        ids of the shooter's live records (a record GearShotTrack.pick chose)"""
        al = None if alts is None else JArray(JString)(list(alts))
        r_ = int(Chg.judgeCalc(calc, seq, wid, proj, al, shot, pid, WHY))
        return r_, str(WHY[0])

    FULL_, PART_, NORM_ = 1, 2, 4
    bfull = zcalcs("Weapon_Shortbow_Iron", FULL_)
    bpart = zcalcs("Weapon_Shortbow_Iron", PART_)
    check(sorted((pe[1], pe[2] or "") for c_, pe in bfull) == [("Charged", ""), ("Unknown", "targeted:Head")] and len(bpart) == 4
          and all(pe[1] == "Charged" for c_, pe in bpart), "Z4: Iron shortbow: FULL = the glow draw + its headshot, 4 PARTIAL draws (all tagged Charged)")
    # the glow step IS the 1.2 s draw strength 4: the FULL calculator is the Iron bow's own Primary_Shoot_Damage_Strength_4 override
    ivars = WK.item("Weapon_Shortbow_Iron")["InteractionVars"]
    s4 = ivars["Primary_Shoot_Damage_Strength_4"]["Interactions"][0]
    s4key = WK.interaction(s4)[2]
    check(MZ.calc.get(s4key + (None,)) is not None and any(same(c_, MZ.calc.get(s4key + (None,))) for c_, pe in bfull)
          and any(same(c_, MZ.calc.get(s4key + ("t:Head",))) for c_, pe in bfull), "Z4: ... that FULL step is the Iron bow's Strength_4 damage (+ Head)")
    # an arrow hit is a projectile hit judged against the bow's launch record (picked: alts = the live record ids) - also as a melee call
    for kw_ in ({}, {"proj": True, "alts": ["Weapon_Shortbow_Iron"]}, {"proj": True}):
        for c_, pe in bfull:
            r_, w_ = jc(c_, "Weapon_Shortbow_Iron", **kw_)
            check(r_ == 1 and w_.startswith("full charge 1.2 s"), "Z4: glow draw %s counts %s: %s" % (pe[2] or "body", kw_, w_))
        for c_, pe in bpart:
            r_, w_ = jc(c_, "Weapon_Shortbow_Iron", **kw_)
            check(r_ == 0 and w_.startswith("partial charge (") and "only the full charge counts" in w_, "Z4: partial draw never counts %s: %s" % (kw_, w_))
    sig = zcalcs("Weapon_Shortbow_Iron", 7, "Signature")
    check(len(sig) == 1 and jc(sig[0][0], "Weapon_Shortbow_Iron") == (0, "signature ability (Hytale Class Signature)"),
          "Z4: the shortbow volley (Signature, charged 1.5 s) never counts")
    sw = zcalcs("Weapon_Sword_Iron", FULL_)
    check(len(sw) == 1 and jc(sw[0][0], "Weapon_Sword_Iron") == (1, "full charge 0.65 s (Hytale Charged tag)"), "Z4: sword thrust 0.65 s counts")
    swl = zcalcs("Weapon_Sword_Iron", NORM_, "Light")
    check(len(swl) == 3 and all(jc(c_, "Weapon_Sword_Iron") == (0, "normal attack") for c_, pe in swl), "Z4: sword swings (Light) never count")
    sws = [c_ for c_, pe in zcalcs("Weapon_Sword_Iron", NORM_ | 8, "Signature")]
    check(len(sws) == 2 and all(jc(c_, "Weapon_Sword_Iron")[0] == 0 for c_ in sws), "Z4: sword signature (Ability1) never counts")
    ax = zcalcs("Weapon_Axe_Iron", FULL_)
    check(len(ax) == 1 and jc(ax[0][0], "Weapon_Axe_Iron") == (1, "full charge 1.39 s (untagged step, from the walk)"),
          "Z4: axe 1.39 s charged swing counts (untagged: signal B only)")
    check(all(jc(c_, "Weapon_Axe_Iron") == (0, "normal attack") for c_, pe in zcalcs("Weapon_Axe_Iron", NORM_)), "Z4: axe normal swings do not")
    ls = zcalcs("Weapon_Longsword_Iron", FULL_)
    check(len(ls) == 1 and jc(ls[0][0], "Weapon_Longsword_Iron")[1] == "full charge 1.565 s (untagged step, from the walk)", "Z4: longsword 1.565 s")
    dg = zcalcs("Weapon_Daggers_Iron", FULL_)
    check(sorted(pe[2] or "" for c_, pe in dg) == ["", "angled0"] and all(jc(c_, "Weapon_Daggers_Iron")[0] == 1 for c_, pe in dg),
          "Z4: dagger pounce + its backstab (untagged AngledDamage) count")
    mc = zcalcs("Weapon_Mace_Iron", FULL_)
    check(len(mc) == 3 and all(jc(c_, "Weapon_Mace_Iron")[1] == "full charge 2 s (Hytale Charged tag)" for c_, pe in mc), "Z4: mace 2.0 s charged swings")
    scy = zcalcs("Weapon_Battleaxe_Scythe_Void", FULL_)
    check(len(scy) == 1 and jc(scy[0][0], "Weapon_Battleaxe_Scythe_Void")[1] == "full charge 1.67 s (untagged step, from the walk)", "Z4: Void scythe")
    xb = zcalcs("Weapon_Crossbow_Iron", NORM_, "Charged")
    check(len(xb) == 1 and jc(xb[0][0], "Weapon_Crossbow_Iron") == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)")
          and jc(xb[0][0], "Weapon_Crossbow_Iron", proj=True, alts=["Weapon_Crossbow_Iron"]) == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)"),
          "Z4: crossbow 3rd bolt (Hytale's Charged combo, no hold) counts (signal A, trusted vanilla), also as the projectile hit it is")
    if PACKI:
        xbm = zcalcs("Weapon_Crossbow_Cobalt", NORM_, "Charged")
        check(len(xbm) == 1 and jc(xbm[0][0], "Weapon_Crossbow_Cobalt")[0] == 1 and bool(Chg.hasCharged("Weapon_Crossbow_Cobalt")),
              "Z4: More Crossbow Tiers Cobalt crossbow: its inherited combo counts + it may roll (pack item = trusted)")
    # verifier: signal A trusts loose Class tags from other mods -> only vanilla + pack ids; an untrusted item needs B or C
    xmod = Chg.ensure("Weapon_Crossbow_Modded")
    xmc = [c_ for c_ in xmod[0].keySet() if int(xmod[0].get(c_)[1]) == 2 and int(xmod[0].get(c_)[0]) == NORM_]
    check(len(xmc) == 1 and same(xmc[0], xb[0][0]) and jc(xmc[0], "Weapon_Crossbow_Modded") == (0, "Charged tag on an untrusted item (not vanilla or pack) - ignored")
          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")), "Z4: the same combo bolt on an untrusted (modded) id never counts and never rolls")
    check(jc(loose_calc, "Weapon_Sword_LooseTag") == (0, "Charged tag on an untrusted item (not vanilla or pack) - ignored")
          and not bool(Chg.hasCharged("Weapon_Sword_LooseTag")) and "Hytale Charged-tagged combo hit" in str(Chg.summary("Weapon_Sword_LooseTag")),
          "Z4: a mod's normal swing tagged Class Charged: ignored, the stat never rolls on that weapon")
    # not in the item's walk (another item's calculator / a new asset object): Class tag only for trusted ids without partial levels
    nc = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(nc, DCLSz.CHARGED)
    check(jc(nc, "Weapon_Sword_Iron") == (1, "Hytale Charged tag (the step is not in the walk)"), "Z4: unknown Charged calc, trusted sword -> counts")
    check(jc(nc, "Weapon_Shortbow_Iron") == (0, "Charged tag on an item with partial charge levels, step not in the walk - ignored"),
          "Z4: ... on a bow (partial draws) it does not (a partial draw can never slip through)")
    check(jc(nc, "Weapon_Sword_LooseTag")[0] == 0, "Z4: ... nor on an untrusted item")
    fz(DCALCz, "damageClass").set(nc, DCLSz.UNKNOWN)
    check(jc(nc, "Weapon_Sword_Iron") == (0, "normal attack (the step is not in the walk)"), "Z4: an unknown untagged calc never counts")
    # exclusions (Skyy: clubs, Kunai, Crystal Flame; verifier: Crystal Ice)
    fl = zcalcs("Weapon_Club_Steel_Flail_Rusty", FULL_)
    ci = zcalcs("Weapon_Staff_Crystal_Ice", FULL_)
    check(len(fl) == 1 and jc(fl[0][0], "Weapon_Club_Steel_Flail_Rusty") == (0, "excluded family (clubs, Kunai, Crystal Flame / Crystal Ice staff, Vampire bow)")
          and len(ci) == 1 and jc(ci[0][0], "Weapon_Staff_Crystal_Ice")[0] == 0, "Z4: flail club charged spin + Crystal Ice charged ball never count")
    amb = zcalcs("Weapon_Shortbow_Bomb", FULL_ | PART_)
    check(len(amb) == 1 and jc(amb[0][0], "Weapon_Shortbow_Bomb") == (0, "ambiguous: this damage step is reached charged and uncharged")
          and not bool(Chg.hasCharged("Weapon_Shortbow_Bomb")), "Z4: prototype bow: one damage step for every draw = ambiguous, never counts / rolls")
    # signal C: legacy projectiles (spear throw, spell orbs)
    check(int(Chg.launchCode("Weapon_Spear_Iron", "Spear_Iron")) == 1 and int(Chg.launchCode("Weapon_Spear_Iron", "Spear_Copper")) == -1
          and int(Chg.launchCode("Weapon_Staff_Iron", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Spellbook_Fire", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Wand_Wood", "Skeleton_Mage_Corruption_Orb")) == 1
          and int(Chg.launchCode("Weapon_Staff_Frost", "Ice_Ball")) == 1 and int(Chg.launchCode("Weapon_Staff_Crystal_Red", "Fireball")) == 1
          and int(Chg.launchCode("Weapon_Shortbow_Vampire", "Arrow_FullCharge")) == 1 and int(Chg.launchCode("Weapon_Shortbow_Vampire", "Arrow_HalfCharge")) == 0,
          "Z4: launch codes: spear throw / staff / spellbook / wand orbs / Frost Ice_Ball / Crystal Red Fireball charged; Vampire full vs half draw")
    # a legacy projectile hit carries its own record (GearShotTrack.find): proj, alts None
    check(jc(None, "Weapon_Spear_Iron", False, True, "Spear_Iron", proj=True) == (1, "charged launch (Spear_Iron)")
          and jc(None, "Weapon_Spear_Iron", False, False, "Spear_Iron", proj=True) == (0, "launch not charged (Spear_Iron)")
          and jc(None, "Weapon_Sword_Iron", False, False, None) == (0, "no damage step and no charged launch"), "Z4: signal C (no DamageSequence)")
    # the Vampire bow (review of 0.1.2 finding 2): its 1.0 s arrow never glows -> excluded, never counts (its launch code stays 1 = the
    # walk itself is unchanged), never rolls
    check(jc(None, "Weapon_Shortbow_Vampire", False, True, "Arrow_FullCharge", proj=True) == (0, "excluded family (clubs, Kunai, Crystal Flame / Crystal Ice staff, Vampire bow)")
          and not bool(Chg.hasCharged("Weapon_Shortbow_Vampire")) and not bool(Chg.canRoll("Weapon_Shortbow_Vampire", 0))
          and "the Vampire bow's arrow never glows" in str(Chg.summary("Weapon_Shortbow_Vampire"))
          and "Weapon_Shortbow_Vampire" in [str(x) for x in Chg.EXCL] and "Weapon_Shortbow_Vampire" not in [str(x) for x in Chg.FALLBACK],
          "Z4: Vampire bow (no glow): its full-charge arrow never counts, it never rolls, the probe says why")

    # ---- Z4b. review of 0.1.2 finding 1: a picked record (GearShotTrack.pick = the WEAKER weapon when several are in the air) may be
    # another weapon than the arrow's. The reviewer's case: a spear / sword record picked for a bow arrow - the old melee fallback
    # ("Class Charged, step not in the walk") counted a PARTIAL draw (judgeCalc(Charged calc, spear) = 1). Now:
    SP_, SW_, BW_, XB_ = "Weapon_Spear_Iron", "Weapon_Sword_Iron", "Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron"
    for wid_ in (SP_, SW_):
        for c_, pe in bpart:
            check(jc(c_, wid_, proj=True, alts=[wid_]) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
                  "Z4b: a partial draw judged against a picked %s record (only it in the air) never counts" % wid_)
            check(jc(c_, wid_, proj=True) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
                  "Z4b: ... nor against an exact %s record" % wid_)
            r_, w_ = jc(c_, wid_, proj=True, alts=[wid_, BW_])
            check(r_ == 0 and w_.startswith("partial charge (") and w_.endswith(" - only the full charge counts - fired by " + BW_),
                  "Z4b: a partial draw with a %s shot + the bow's shots in the air: found in the bow's walk = partial (%s)" % (wid_, w_))
        for c_, pe in bfull:
            check(jc(c_, wid_, proj=True, alts=[BW_, wid_]) == (1, "full charge 1.2 s (Hytale Charged tag) - fired by " + BW_)
                  if pe[1] == "Charged" else jc(c_, wid_, proj=True, alts=[BW_, wid_])[0] == 1,
                  "Z4b: the glow draw %s with a %s shot in the air still counts (found in the bow's walk)" % (pe[2] or "body", wid_))
    check(jc(xb[0][0], SP_, proj=True, alts=[SP_, XB_]) == (1, "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row) - fired by " + XB_)
          and jc(xb[0][0], SP_, proj=True, alts=[SP_])[0] == 0,
          "Z4b: the crossbow's 3rd bolt with a spear in the air counts via the crossbow's walk; judged against the spear alone never")
    # the melee fallback is unchanged (a melee hit has no record): an unknown Charged calc on a trusted sword still counts
    ncm = UZ.allocateInstance(DCALCz.class_)
    fz(DCALCz, "damageClass").set(ncm, DCLSz.CHARGED)
    check(jc(ncm, SW_) == (1, "Hytale Charged tag (the step is not in the walk)") and jc(ncm, SW_, proj=True, alts=[SW_, SP_])[0] == 0
          and jc(ncm, XB_, proj=True) == (0, "projectile step not in the walk of its shot's weapon - not charged"),
          "Z4b: the Class-tag fallback is melee only; an unknown projectile step never counts")
    # several live weapons that know the same step must all call it charged (fake index entries: a weapon whose walk has the glow
    # calculator as a partial step, and an excluded weapon whose walk has it)
    OBJ = JClass("java.lang.Object")

    def fake_entry(calc, flags, ms):
        m_ = IdMap()
        m_.put(calc, JArray(JInt)([flags, 2, ms]))
        e_ = JArray(OBJ)(8)
        BT_ = JClass("java.lang.Boolean").TRUE
        for i_, v_ in enumerate([m_, HashMap(), BT_, BT_, JString("fake"), BT_, JClass("java.lang.Long").valueOf(JLong(int(time.time() * 1000))), BT_]):
            e_[i_] = v_
        return e_
    gc_ = [c_ for c_, pe in bfull if pe[1] == "Charged"][0]
    Chg.ITEMS.put("Weapon_Shortbow_FakePartial", fake_entry(gc_, PART_, 900))
    Chg.ITEMS.put("Weapon_Club_FakeShooter", fake_entry(gc_, FULL_, 1200))
    check(jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Shortbow_FakePartial"]) == (0, "partial charge (0.9 s) - only the full charge counts - fired by Weapon_Shortbow_FakePartial")
          and jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Club_FakeShooter"]) == (0, "fired by Weapon_Club_FakeShooter - excluded family")
          and jc(gc_, BW_, proj=True, alts=[BW_, "Weapon_Shortbow_Crude"])[0] == 1,
          "Z4b: a step one live weapon calls partial (or an excluded weapon knows) never counts; unknown to the others = the bow decides")
    Chg.ITEMS.remove("Weapon_Shortbow_FakePartial")
    Chg.ITEMS.remove("Weapon_Club_FakeShooter")
    # a legacy launch flag without a damage step: only while one weapon is in the air
    check(jc(None, SP_, False, True, "Spear_Iron", proj=True, alts=[SP_]) == (1, "charged launch (Spear_Iron)")
          and jc(None, SP_, False, True, "Spear_Iron", proj=True, alts=[SP_, BW_]) == (0, "charged launch (Spear_Iron) but shots of several weapons are in the air and the hit has no damage step - not charged"),
          "Z4b: a picked charged launch record counts only when it is the only weapon in the air")
    # finding 3: one WARN per weapon id when a Class-tagged step of a walked vanilla weapon is missing after the re-walk
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if k_.startswith("chgmiss:"):
            Gear.ONCE.remove(k_)
    jc(ncm, SW_)
    jc(ncm, SW_)
    jc(ncm, XB_, proj=True)
    jc(ncm, "Weapon_Sword_LooseTag")
    fz(DCALCz, "damageClass").set(ncm, DCLSz.UNKNOWN)
    jc(ncm, "Weapon_Axe_Iron")
    for c_, pe in bfull:
        jc(c_, BW_, proj=True, alts=[BW_])
    jc(bpart[0][0], SP_, proj=True, alts=[SP_, BW_])
    miss_ = sorted(str(x) for x in Gear.ONCE.keySet() if str(x).startswith("chgmiss:"))
    check(miss_ == ["chgmiss:" + XB_, "chgmiss:" + SW_],
          "Z4b: finding 3 - a missing Class-tagged step logs once per weapon id (never for untrusted ids, untagged steps, known steps, a step "
          "another live weapon knows): %s" % miss_)
    print("Z4b. review of 0.1.2: picked records, the melee-only fallback, the missing-step WARN done")
    check(jc(bfull[0][0], None) == (0, "no weapon"), "Z4: no weapon -> no")
    Cfg.CHG_ON = False
    check(jc(bfull[0][0], "Weapon_Shortbow_Iron") == (0, "charged.on is off") and jc(None, "Weapon_Spear_Iron", False, True, "Spear_Iron")[0] == 0,
          "Z4: charged.on off -> nothing counts")
    Cfg.CHG_ON = True
    # GearCharged.judge end to end on a real Damage with the engine's DamageSequence meta (when a bare JVM can build one)
    try:
        Dmg = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
        DSq = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems$DamageSequence")
        DCS_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems")
        dz = Dmg(None, 0, 10.0)
        sq = UZ.allocateInstance(DSq.class_)
        fz(DSq, "damageCalculator").set(sq, sw[0][0])
        dz.putMetaObject(DCS_.DAMAGE_SEQUENCE, sq)
        w2 = JArray(JString)(1)
        r_a = bool(Charged.judge(dz, "Weapon_Sword_Iron", None, None, w2))
        wa_ = str(w2[0])
        dz2 = Dmg(None, 0, 10.0)
        r_b = bool(Charged.judge(dz2, "Weapon_Sword_Iron", None, None, w2))
        check(r_a and wa_ == "full charge 0.65 s (Hytale Charged tag)" and not r_b and str(w2[0]) == "no damage step and no charged launch",
              "Z4: GearCharged.judge on a real Damage: the DamageSequence meta decides (%s)" % wa_)
        # review finding 1 end to end: a partial-draw arrow Damage judged against a picked spear record
        dz3 = Dmg(None, 0, 10.0)
        sq3 = UZ.allocateInstance(DSq.class_)
        fz(DSq, "damageCalculator").set(sq3, bpart[0][0])
        dz3.putMetaObject(DCS_.DAMAGE_SEQUENCE, sq3)
        spr_ = Shot(U1, IS("Weapon_Spear_Iron", 1), None, None)
        r_c = bool(Charged.judge(dz3, "Weapon_Spear_Iron", spr_, JArray(JString)(["Weapon_Spear_Iron"]), w2))
        wc_ = str(w2[0])
        r_d = bool(Charged.judge(dz3, "Weapon_Spear_Iron", spr_, JArray(JString)(["Weapon_Spear_Iron", "Weapon_Shortbow_Iron"]), w2))
        wd_ = str(w2[0])
        r_e = bool(Charged.judge(dz3, "Weapon_Spear_Iron", None, JArray(JString)(["Weapon_Spear_Iron"]), w2))
        check(not r_c and wc_ == "projectile step not in the walk of its shot's weapon - not charged" and not r_d and wd_.startswith("partial charge (")
              and wd_.endswith("fired by Weapon_Shortbow_Iron") and r_e and str(w2[0]) == "Hytale Charged tag (the step is not in the walk)",
              "Z4: GearCharged.judge: a partial-draw arrow against a picked spear record never counts (%s / %s); melee (no record) keeps the fallback"
              % (wc_, wd_))
    except Exception as ex_:
        print("Z4. note: a bare JVM cannot build a Damage here (%s) - judge() is covered through judgeCalc + the bytecode check" % ex_)
    print("Z4. per-hit rules done")

    # ---- Z5. roll eligibility per family (runtime walk), charged.on off, and the fallback when the walk cannot run
    fam_tab = []
    FAMS = ["Weapon_Sword_", "Weapon_Battleaxe_", "Weapon_Mace_", "Weapon_Daggers_", "Weapon_Axe_", "Weapon_Longsword_", "Weapon_Spear_",
            "Weapon_Shortbow_", "Weapon_Crossbow_", "Weapon_Staff_", "Weapon_Wand_", "Weapon_Spellbook_", "Weapon_Club_", "Weapon_Kunai"]
    for fp in FAMS:
        g_ = [i for i in ALLW if i.startswith(fp) and bool(Data.isGear(i))]
        yes = [i for i in g_ if I_CHG in [int(x) for x in Roll.pool(int(Data.slotOf(i)), i)]]
        e0 = zsum[yes[0]][0] if yes else None
        fam_tab.append((fp, len(g_), len(yes), sorted(set(g_) - set(yes)), str(e0[4]).split(" - ", 1)[1].split(";")[0] if e0 is not None else "-"))
    exp_tab = {"Weapon_Sword_": (23, 23), "Weapon_Battleaxe_": (15, 15), "Weapon_Mace_": (12, 12), "Weapon_Daggers_": (16, 16),
               "Weapon_Axe_": (13, 13), "Weapon_Longsword_": (18, 18), "Weapon_Spear_": (17, 17), "Weapon_Shortbow_": (19, 14),
               "Weapon_Crossbow_": (2 + len(PACKI), 2 + len(PACKI)), "Weapon_Staff_": (24, 22), "Weapon_Wand_": (5, 3),
               "Weapon_Spellbook_": (6, 5), "Weapon_Club_": (22, 0), "Weapon_Kunai": (1, 0)}
    check(all((ng, nr) == exp_tab[fp] for fp, ng, nr, _no, _s in fam_tab), "Z5: per family (gear items, may roll chg) = %s"
          % [(fp, ng, nr) for fp, ng, nr, _no, _s in fam_tab])
    print("Z5. per family (runtime walk, charged.on on): family | gear | may roll | never rolls on | what counts (first item)")
    for fp, ng, nr, no, sm in fam_tab:
        print("     %-18s %3d %3d  %s | %s" % (fp, ng, nr, ", ".join(x[len("Weapon_"):] for x in no) or "-", sm))
    check(I_CHG in [int(x) for x in Roll.pool(2, "Armor_Iron_Chest")] and I_CHG in [int(x) for x in Roll.pool(2, None)]
          and I_CHG not in [int(x) for x in Roll.pool(0, None)] and I_CHG not in [int(x) for x in Roll.pool(4, "Skyy_Ring_Gold")],
          "Z5: armor always may roll it; a weapon without a known id never; Equipment never")
    Cfg.CHG_ON = False
    check(not any(I_CHG in [int(x) for x in Roll.pool(s_, i)] for i in ALLW + ["Armor_Iron_Chest", None] for s_ in (0, 1, 2, 4)),
          "Z5: charged.on off -> never in any pool (Skyy's lock: a stat that does nothing never rolls)")
    Cfg.CHG_ON = True
    # every roll path with chg the ONLY stat that has a weight (every other stats.<key> weight 0, chg at the loader's cap 100000) so
    # one leak would show and a charged item's every roll must carry it (review-of-0.1.2 run: with the other weights left on, a
    # one-modifier roll - Normal craft / identify - could still pick another stat now and then: one run gave a flaky 119/120)
    pw = Props()
    smx_ = [int(x) for x in Cfg.S_MAX]
    for i_, k_ in enumerate(SK):
        pw.setProperty("stats." + k_, "%d,%d" % (smx_[i_], 100000 if k_ == "chg" else 0))
    Cfg.apply(pw, False)
    check([i_ for i_ in range(len(SK)) if int(Cfg.S_W[i_]) != 0] == [I_CHG] and int(Cfg.S_W[I_CHG]) == 100000,
          "Z5: roll-path test setup: chg is the only weighted stat")

    def has_chg(dd):
        return "chg" in keys_of(dd)
    paths = lambda iid: [Roll.newDoc(iid, 5, True, "admin"), Roll.craftDoc(iid, U1), Roll.identify(iid, Roll.unidDoc(iid, 1, "drop"), U1),
                         Roll.reforge(iid, Roll.newDoc(iid, 3, True, "admin"))]
    on_sword = sum(1 for _ in range(30) for dd in paths("Weapon_Sword_Iron") if has_chg(dd))
    on_bow = sum(1 for _ in range(30) for dd in paths("Weapon_Shortbow_Crude") if has_chg(dd))
    on_armor = sum(1 for _ in range(30) for dd in paths("Armor_Iron_Chest") if has_chg(dd))
    on_club = sum(1 for _ in range(30) for dd in paths("Weapon_Club_Iron") + paths("Weapon_Club_Steel_Flail_Rusty") + paths("Weapon_Kunai")
                  + paths("Weapon_Staff_Crystal_Ice") + paths("Weapon_Staff_Crystal_Flame") + paths("Weapon_Shortbow_Bomb")
                  + paths("Weapon_Shortbow_Vampire") if has_chg(dd))
    Cfg.CHG_ON = False
    off_all = sum(1 for _ in range(30) for iid in ("Weapon_Sword_Iron", "Armor_Iron_Chest", "Weapon_Spear_Iron", "Weapon_Staff_Wood")
                  for dd in paths(iid) if has_chg(dd))
    Cfg.CHG_ON = True
    check(on_sword == 120 and on_bow == 120 and on_armor == 120 and on_club == 0 and off_all == 0,
          "Z5: /gear give, crafting, identify, reforge: chg on every charged weapon / armor roll (%d/%d/%d of 120), never on clubs / Kunai / "
          "Crystal Ice / Crystal Flame / prototype bow / Vampire bow (%d), never with charged.on off (%d)" % (on_sword, on_bow, on_armor, on_club, off_all))
    Cfg.apply(Props(), False)
    # the walk cannot run (no item assets): the list the build baked decides, excluded families still never
    saved = dict((k_, imap.get(k_)) for k_ in ("Weapon_Sword_Iron", "Weapon_Club_Iron", "Weapon_Shortbow_Bomb", "Weapon_Crossbow_Modded"))
    for k_ in saved:
        imap.remove(k_)
    Chg.clear()
    check(bool(Chg.hasCharged("Weapon_Sword_Iron")) and not bool(Chg.hasCharged("Weapon_Club_Iron")) and not bool(Chg.hasCharged("Weapon_Shortbow_Bomb"))
          and not bool(Chg.hasCharged("Weapon_Crossbow_Modded")) and "using the built-in list: has a charged attack" in str(Chg.summary("Weapon_Sword_Iron")),
          "Z5: without a runtime walk the baked vanilla list decides (sword yes; club, prototype bow, unknown modded id no)")
    for k_, v_ in saved.items():
        imap.put(k_, v_)
    Chg.clear()
    print("Z5. roll eligibility done")

    # ---- Z6. the verifier's failure cases: a single spellbook / a single thrown spear is used up by the cast before GearShotTrack
    # records the projectile -> GearHand.pick supplies the stack that launched it (live hand first, then the snapshot <= 1 s old)
    def gstack(iid, pairs=(("chg", 20), ("str", 7))):
        dd = Roll.newDoc(iid, 0, True, "admin")
        arr_ = JClass("org.bson.BsonArray")()
        for k_, v_ in pairs:
            arr_.add(Data.mod(k_, v_))
        dd.put("mods", arr_)
        return Data.put(IS(iid, 1), dd, U1)

    ORB, SPR = "Skeleton_Mage_Corruption_Orb", "Spear_Iron"
    book, spear, sword = gstack("Weapon_Spellbook_Fire"), gstack("Weapon_Spear_Iron"), gstack("Weapon_Sword_Iron")
    EMPTY = None
    now_ms = int(time.time() * 1000)
    Hand.CUR.clear()
    Hand.seen(U1, book)                                   # the book was in the hand at the last tick
    pk = Hand.pick(U1, EMPTY, ORB, now_ms + 50)
    check(pk is not None and pk.equals(book), "Z6: single spellbook: the hand is empty at the record, the snapshot supplies the book")
    check(int(Chg.launchCode(pk.getItemId(), ORB)) == 1, "Z6: ... and its orb launch is charged (GearShot.charged)")
    Hand.CUR.clear()
    Hand.seen(U1, book)
    Hand.seen(U1, EMPTY)                                  # GearHandSys ran after the cast used the book up (the other system order)
    check(Hand.pick(U1, EMPTY, ORB, int(time.time() * 1000) + 20).equals(book), "Z6: ... also when the snapshot already saw the empty hand")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    ps_ = Hand.pick(U1, EMPTY, SPR, int(time.time() * 1000) + 30)
    check(ps_ is not None and ps_.equals(spear) and int(Chg.launchCode(ps_.getItemId(), SPR)) == 1, "Z6: single thrown spear: the snapshot supplies the spear")
    four = IS("Weapon_Spellbook_Fire", 4)
    check(same(Hand.pick(U1, four, ORB, now_ms), four), "Z6: a stack of books still in the hand = the live hand wins")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    Hand.seen(U1, EMPTY)
    check(Hand.pick(U1, EMPTY, SPR, int(time.time() * 1000) + 2500) is None, "Z6: a snapshot older than 1 s is never used")
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    check(Hand.pick(U1, EMPTY, ORB, now_ms) is None, "Z6: a snapshot that does not launch this projectile is never used")
    Hand.CUR.clear()
    Hand.seen(U1, IS("Weapon_Bomb_Potion_Poison", 1))
    check(Hand.pick(U1, EMPTY, "Bomb_Potion_Poison", now_ms) is None, "Z6: a non-gear snapshot (a thrown potion bomb) is never used (0.1 behaviour)")
    Hand.CUR.clear()
    Hand.seen(U1, sword)
    check(Hand.pick(U2, EMPTY, SPR, now_ms) is None, "Z6: snapshots are per player")
    # review of 0.1.2 finding 5: an empty hand that turns into another empty hand (null <-> ItemStack.EMPTY) keeps the previous slot
    Hand.CUR.clear()
    Hand.seen(U1, spear)
    Hand.seen(U1, EMPTY)
    Hand.seen(U1, IS.EMPTY)
    Hand.seen(U1, EMPTY)
    ps2_ = Hand.pick(U1, IS.EMPTY, SPR, int(time.time() * 1000) + 30)
    check(ps2_ is not None and ps2_.equals(spear) and bool(IS.EMPTY.isEmpty()),
          "Z6: finding 5 - null / empty-stack flips of an empty hand never push the thrown spear out of the snapshot")
    # what the fix changes in combat: the recorded main now carries the book's own stats (it had none) and the level gate sees it
    rec_ = Shot(U1, book, None, None)
    rec_.charged = True
    rec_.pid = ORB
    tb = Stats.totals(U1, rec_.main, None, None, True)
    check(int(tb[I_CHG]) == 20 and int(tb[si("str")]) == 7 and int(Stats.totals(U1, None, None, None, True)[I_CHG]) == 0,
          "Z6: the single book's own Charged Attack Damage 20% + Strength 7 now apply to its orb (before: empty hand = armor only)")
    check(jc(None, rec_.main.getItemId(), False, rec_.charged, rec_.pid, proj=True) == (1, "charged launch (Skeleton_Mage_Corruption_Orb)")
          and abs(float(Hit.hitAmount(100.0, tb, True, True, 0.9, 0.9)) - 100.0 * 1.0 * 1.03) < 1e-9,
          "Z6: the orb counts as charged, as a spell: 100 x (1 + 0.15 x 20%) = 103 (no Magical Power on the book)")
    check(not bool(Chg.canRoll("Weapon_Staff_Crystal_Ice", 1)) and not bool(Chg.canRoll("Weapon_Staff_Crystal_Flame", 1))
          and bool(Chg.canRoll("Weapon_Staff_Iron", 1)) and bool(Chg.canRoll("Weapon_Spellbook_Fire", 1)) and bool(Chg.canRoll("Weapon_Wand_Wood", 1)),
          "Z6: Crystal Ice (its Ice hits never reach the stat code) + Crystal Flame never roll it; orb staffs / spellbooks / wands do")
    Hand.CUR.clear()
    print("Z6. verifier cases done")

    # ---- Z7. the one-time config.properties update GearCfg.migrate012 (setup order importRolls -> migrate011 -> migrateStat011 ->
    # migrate012 -> load), on scratch copies
    ZD = os.path.join(SCRATCH, "work", "z012")

    def zcase(name, data):
        cfg_quiet()
        shutil.rmtree(os.path.join(ZD, name), ignore_errors=True)
        d_ = os.path.join(ZD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    CHG2 = ["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5"]
    BLK = [CHM] + [x for k_ in ("charged.on", "charged.spellFactor", "charged.log") for x in (
        {"charged.on": "# Charged Attack Damage in combat: ", "charged.spellFactor": "# Charged bonus on spells: ",
         "charged.log": "# Log charged hits: "}[k_] + zh[k_], "%s=%s" % (k_, zd[k_]))]
    ADD_ALL = "stats.chg, charged.on, charged.spellFactor, charged.log"
    INFO12 = ("config.properties: added the 0.1.2 Charged Attack Damage lines (%s) with their built-in defaults - nothing changes in effect; "
              "the old file is in config-history" % ADD_ALL)

    def exp12(t, anchor_c="stats.cd=30,10", anchor_b="speed.per=1", nl="\n"):
        """the expected result, built independently: the two blocks right after their anchor lines"""
        ls_ = t.split(nl)
        i_ = ls_.index(anchor_b)
        ls_[i_ + 1:i_ + 1] = BLK
        j_ = ls_.index(anchor_c)
        ls_[j_ + 1:j_ + 1] = CHG2
        return nl.join(ls_)

    if live is not None:
        d, f = zcase("a-live", live)
        r011 = str(Cfg.migrate011())
        r_st = str(Cfg.migrateStat011())
        mid = rb(f)
        r12 = str(Cfg.migrate012())
        got = rb(f)
        check(r011.startswith("config.properties updated to the 0.1.1 level table") and r_st.startswith("config.properties updated to the 0.1.1 stat defaults"),
              "Z7(a): the live 0.1 file first gets both 0.1.1 updates (sections X / Y)")
        check(got == exp12(mid.decode("latin-1")).encode("latin-1"), "Z7(a): exactly the stat line under stats.cd + the marker and three rows under speed.per")
        check(r12 == INFO12, "Z7(a): the INFO line: %s" % r12)
        print("Z7. INFO line the live file produces: [SkyyGear] " + r12)
        pm, pg = props(mid.decode("latin-1")), props(got.decode("latin-1"))
        check(all(pg.get(k_) == v_ for k_, v_ in pm.items()) and sorted(set(pg) - set(pm)) == ["charged.log", "charged.on", "charged.spellFactor", "stats.chg"]
              and pg["stats.chg"] == "30,5" and pg["charged.spellFactor"] == "0.15", "Z7(a): every old value kept; the four new keys hold their defaults")
        b_ = baks(d)
        ix = idx(d)
        check(len(b_) == 3 and rb(os.path.join(d, "config-history", b_[0])) == live and rb(os.path.join(d, "config-history", b_[2])) == mid
              and ix[2].split("\t")[3:] == ["SkyyGear 0.1.2", "before the 0.1.2 charged attack lines"],
              "Z7(a): History = the 0.1 file, after the level update, after the stat update (3 versions; the last named 'SkyyGear 0.1.2')")
        check(len(clog(d)) == 8, "Z7(a): no config-changes.log line (values unchanged) - still the 8 lines of the two 0.1.1 updates")
        Cfg.load()
        check(bool(Cfg.CHG_ON) and abs(float(Cfg.CHG_SPELL) - 0.15) < 1e-12 and int(Cfg.S_MAX[I_CHG]) == 30 and int(Cfg.S_W[I_CHG]) == 5,
              "Z7(a): the loader reads the new lines")
        fresh = zdt.encode("latin-1")
        # (0.2: compared with the fresh file in its 0.1.3 shape - shape013 - without the 0.1.3 family rows)
        zdt012 = "\n".join(l_ for l_ in shape013(zdt).split("\n") if l_ not in FAM_LINES)
        check(props(got.decode("latin-1")) == props(zdt012), "Z7(a): the 0.1.2-updated live file has every value of a fresh file but the 0.1.3 family rows")
        # (b) the second start changes nothing
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and str(Cfg.migrate012()) == "" and rb(f) == got
              and len(baks(d)) == 3 and len(idx(d)) == 3, "Z7(b): a second start changes nothing (file, History)")
        # (f) Server Setup's stat table lists chg now (the reason for the update): the kit's keys op after CfgPub.start
        CfgPubZ = J("CfgPub")
        OAz = JArray(JObject)
        CfgPubZ.start(Paths.get(os.path.dirname(d)), None)
        ks_ = bridge.get("config:fn:SkyyGear").apply(OAz(["keys", "stat", ""]))
        kd_ = dict(zip([str(x) for x in ks_[0]], [str(x) for x in ks_[2]]))
        cg_ = bridge.get("config:fn:SkyyGear").apply(OAz(["get", "charged.spellFactor"]))
        check(kd_.get("chg") == "30|5" and str(cg_) == "0.15", "Z7(f): Server Setup lists stat chg 30|5 and charged.spellFactor 0.15 (%s)" % kd_.get("chg"))
        rset = bridge.get("config:fn:SkyyGear").apply(OAz(["set", "charged.on", "false", None, "console", "yes", "console"]))
        CfgPubZ.flush()
        check(str(rset[0]) == "ok" and "\ncharged.on=false\n" in rb(f).decode("latin-1") and not bool(Cfg.CHG_ON),
              "Z7(f): switching charged.on off in game rewrites only that line and applies at once")
        Cfg.CHG_ON = True
    # (c) no file: the loader writes the fresh 0.1.2 file (marker included); the update leaves it alone
    d, f = zcase("c-fresh", None)
    check(str(Cfg.migrate012()) == "" and not os.path.exists(f), "Z7(c): no file -> nothing written")
    Cfg.load()
    fz_ = rb(f)
    check(fz_ == zdt.encode("utf-8") and str(Cfg.migrate012()) == "" and rb(f) == fz_ and not baks(d), "Z7(c): the fresh file never updates")
    # (d) CRLF kept; (e) keys already there kept + noted; (g) anchors missing / the end-of-file continuation trap
    base = zdt.replace(CHM + "\n", "").replace("\n".join(CHG2) + "\n", "")
    for k_ in ("charged.on", "charged.spellFactor", "charged.log"):
        base = base.replace(BLK[1 + 2 * ("charged.on", "charged.spellFactor", "charged.log").index(k_)] + "\n%s=%s\n" % (k_, zd[k_]), "")
    check("charged." not in base and "stats.chg" not in base and str(Cfg.CH_MARK_ID) not in base, "Z7: the 0.1.1-shaped test file has no 0.1.2 line")
    r = Cfg.chUpdate(base)
    check(r is not None and str(r[0]) == exp12(base) and str(r[0]) == zdt, "Z7: the text step on the 0.1.1 shape gives exactly the fresh 0.1.2 file")
    crlf = base.replace("\n", "\r\n")
    r = Cfg.chUpdate(crlf)
    check(r is not None and str(r[0]) == exp12(base).replace("\n", "\r\n"), "Z7(d): CRLF kept on every added line")
    hand_ = base.replace("stats.cd=30,10\n", "stats.cd=30,10\nstats.chg=10,1\n").replace("speed.per=1\n", "speed.per=1\ncharged.on=false\n")
    r = Cfg.chUpdate(hand_)
    check(r is not None and str(r[1]) == "charged.spellFactor, charged.log" and [str(x) for x in r[2]] == [
        "stats.chg is already in the file - kept", "charged.on is already in the file - kept"]
          and props(str(r[0]))["stats.chg"] == "10,1" and props(str(r[0]))["charged.on"] == "false", "Z7(e): hand-added lines kept + noted")
    ends = [("a=1\nstats.dmg=30,10\ncombat.strPer=1\n", "a=1\nstats.dmg=30,10\n" + "\n".join(CHG2) + "\ncombat.strPer=1\n" + "\n".join(BLK) + "\n"),
            ("a=1\n", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\n"),
            ("a=1", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:])),
            ("a=1\r\nb=x\\", "a=1\r\n" + "\r\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\r\nb=x\\"),
            ("speed.per=2\\", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nspeed.per=2\\"),
            ("a=1\nb=x\\\n", "a=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nb=x\\\n"),
            ("speed.per=1\\\n", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\nspeed.per=1\\\n"),
            ("stats.cd=1\\\n\ncombat.strPer=1\n", "stats.cd=1\\\n\n" + "\n".join(CHG2) + "\ncombat.strPer=1\n" + "\n".join(BLK) + "\n"),
            ("\\\ncharged.on=false\nspeed.per=1\n", "\\\ncharged.on=false\nspeed.per=1\n" + "\n".join(BLK[:1] + CHG2 + BLK[3:]) + "\n"),
            ("", "\n".join(BLK[:1] + CHG2 + BLK[1:]) + "\n")]
    for t_, want in ends:
        r = Cfg.chUpdate(t_)
        check(r is not None and str(r[0]) == want and Cfg.chUpdate(str(r[0])) is None, "Z7(g): %r -> %r (got %r)" % (t_, want, r and str(r[0])))
    check(Cfg.chUpdate("x=1\n# " + str(Cfg.CH_MARK_ID) + " anything\n") is None and Cfg.chUpdate("x=1\n  ! " + str(Cfg.CH_MARK_ID) + "\n") is None
          and Cfg.chUpdate("note=" + str(Cfg.CH_MARK_ID) + "\n") is not None, "Z7(g): the marker counts only in a comment line")
    # (h) random files: same Properties values + only the missing new keys (with their defaults), the old lines in order, run once
    import random as _r
    rz = _r.Random(20260930 + 12)
    BSl = "\\"
    zpieces = ["a=1", "b=x" + BSl, "c=y" + BSl + BSl, "#c" + BSl, "# note", "", "   z" + BSl, BSl, "d:e", "  f g" + BSl, "!x" + BSl,
               "stats.cd=30,10", "stats.dmg=30,10", "speed.per=1", "combat.strPer=1", "stats.chg=9,9", "charged.on=false", "crit.base=0"]
    newk = {"stats.chg": "30,5", "charged.on": "true", "charged.spellFactor": "0.15", "charged.log": "false"}
    zbad2 = []
    for n_ in range(3000):
        ls_ = [rz.choice(zpieces) for _q in range(rz.randint(0, 10))]
        nl_ = "\r\n" if rz.random() < 0.3 else "\n"
        t_ = nl_.join(ls_) + (nl_ if rz.random() < 0.6 else "")
        r = Cfg.chUpdate(t_)
        if r is None:
            zbad2.append(("none", t_))
            continue
        o_ = str(r[0])
        pt_, po_ = props(t_), props(o_)
        want = dict(pt_)
        for k_, v_ in newk.items():
            want.setdefault(k_, v_)
        # the added lines removed again = the original text, byte for byte (CR of an appended-after line aside)
        added = set(BLK + CHG2)
        back = [x for x in o_.split("\n") if x.rstrip("\r") not in added]
        back_t = "\n".join(back)
        if po_ != want or Cfg.chUpdate(o_) is not None or (back_t != t_ and back_t.replace("\r", "") != t_.replace("\r", "")):
            zbad2.append(("bad", t_))
    check(not zbad2, "Z7(h): 3000 random files (continuations, comments ending in a backslash, lone backslashes, CRLF, no final newline): "
                     "Properties = old values + only the missing new keys, old lines kept in order, the next pass does nothing (%d bad, first %r)"
                     % (len(zbad2), zbad2[:1]))
    # (i) History cannot be written -> WARN, untouched, the next start updates
    if live is not None:
        d, f = zcase("i-nohist", live)
        Cfg.migrate011()
        Cfg.migrateStat011()
        before = rb(f)
        shutil.rmtree(os.path.join(d, "config-history"))
        open(os.path.join(d, "config-history"), "w").write("x")
        Log.FILE = Paths.get(os.path.join(d, "gear.log"))
        check(str(Cfg.migrate012()) == "" and rb(f) == before, "Z7(i): History blocked -> the file stays untouched")
        Log.flush()
        gl = open(os.path.join(d, "gear.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "gear.log")) else ""
        check("NOT given the 0.1.2 charged attack lines" in gl and "the next start tries again" in gl, "Z7(i): one WARN says why")
        os.remove(os.path.join(d, "config-history"))
        check(str(Cfg.migrate012()) == INFO12 and rb(f) == exp12(before.decode("latin-1")).encode("latin-1"), "Z7(i): the next start updates it")
        Log.FILE = None
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    print("Z7. migrate012 done")

    # ---- Z8. start twice on a scratch COPY of the whole live Skyy_SkyyGear folder (read only source): setup()'s file steps in its
    # order - GearQual.load, importRolls, migrate011, migrateStat011, migrate012, (0.1.3) migrate013, load, CfgPub.start - then the same
    # again. 0.1.3 harness: the updates whose marker the live file already has must do nothing; the others run once.
    live_dir = os.path.dirname(LIVE)
    if os.path.isdir(live_dir):
        z8 = os.path.join(ZD, "live-start", "mods")
        shutil.rmtree(os.path.dirname(z8), ignore_errors=True)
        shutil.copytree(live_dir, os.path.join(z8, "Skyy_SkyyGear"))
        rolls_src = os.path.join(os.path.dirname(live_dir), "Skyy_SkyyRolls")
        if os.path.isdir(rolls_src):
            shutil.copytree(rolls_src, os.path.join(z8, "Skyy_SkyyRolls"))
        gdir = os.path.join(z8, "Skyy_SkyyGear")

        def snapshot_dir():
            out_ = {}
            for root_, _ds, fs_ in os.walk(gdir):
                for fn_ in fs_:
                    p_ = os.path.join(root_, fn_)
                    out_[os.path.relpath(p_, gdir).replace(os.sep, "/")] = rb(p_)
            return out_

        def start_once():
            Cfg.DIR = Paths.get(gdir)
            Cfg.FILE = Paths.get(os.path.join(gdir, "config.properties"))
            Log.FILE = Paths.get(os.path.join(gdir, "gear.log"))
            Qual.load(Paths.get(os.path.join(gdir, "quality.properties")))
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(z8, "Skyy_SkyyRolls", "reforge.properties")))
            # (0.2: + migrate02, right after migrate013 - the setup order; 0.2.1: + migrate021 right after migrate02)
            infos = [str(Cfg.migrate011()), str(Cfg.migrateStat011()), str(Cfg.migrate012()), str(Cfg.migrate013()), str(Cfg.migrate02()),
                     str(Cfg.migrate021())]
            Cfg.load()
            J("CfgPub").start(Paths.get(z8), None)
            J("CfgPub").flush()
            Log.flush()
            return infos

        pre = snapshot_dir()
        ptxt = pre["config.properties"].decode("latin-1")
        due = [str(Cfg.LV_MARK_ID) not in ptxt, str(Cfg.ST_MARK_ID) not in ptxt, str(Cfg.CH_MARK_ID) not in ptxt, str(Cfg.FM_MARK_ID) not in ptxt,
               str(Cfg.BD_MARK_ID) not in ptxt, str(Cfg.LS_MARK_ID) not in ptxt]
        hist0 = sorted(k_ for k_ in pre if k_.startswith("config-history/") and k_.endswith(".bak"))
        i1 = start_once()
        s1 = snapshot_dir()
        i2 = start_once()
        s2 = snapshot_dir()
        changed1 = sorted(k_ for k_ in set(s1) | set(pre) if s1.get(k_) != pre.get(k_))
        changed2 = sorted(k_ for k_ in set(s2) | set(s1) if s2.get(k_) != s1.get(k_) and k_ != "gear.log")
        check([bool(x) for x in i1] == due and (not due[2] or i1[2] == INFO12) and not any(x for x in i2),
              "Z8: first start: exactly the one-time updates whose marker is missing run (%s); second start: none" % due)
        check(not changed2, "Z8: second start - every file except gear.log is byte-identical: %s" % changed2)
        hist = sorted(k_ for k_ in s1 if k_.startswith("config-history/") and k_.endswith(".bak"))
        new_h = [k_ for k_ in hist if k_ not in hist0]
        check(len(new_h) == sum(1 for x in due if x) and (not new_h or s1[new_h[0]] == pre["config.properties"]),
              "Z8: first start keeps one History version per update that ran, the first = the live file (%d new)" % len(new_h))
        check(props(s1["config.properties"].decode("latin-1")) == props(shape021(zdt)), "Z8: the live data ends with every value of a fresh %s file "
              "(0.2.2: in its 0.2.1 shape - no one-time update writes the six new rows)" % VERSION)
        check(not any(k_ in props(s1["config.properties"].decode("latin-1")) for k_ in CF022K) and len(CF022K) == 6,
              "Z8: 0.2.2 - none of the six new keys is written into the live file by a start (they read their defaults): %s" % CF022K)
        print("Z8. live copy: first start changed %s; second start changed %s (gear.log only)" % (changed1, changed2 or "nothing"))
        for x in i1:
            print("Z8.   [SkyyGear] " + x.split("\n")[0])
        Log.FILE = None
        Cfg.FILE = None
        Cfg.DIR = None
        Cfg.apply(Props(), False)
    else:
        print("Z8. note: no live Skyy_SkyyGear folder at %s - the live start test was skipped" % live_dir)

    # ---- Z9. bytecode: setup order, the combat hook, the shot record, the roll entry points, /gear charged (admin)
    def mcode(cls, name, sig=None):
        cc_ = pool.get(PKG + cls)
        outs = []
        for mm in list(cc_.getDeclaredMethods()):
            if str(mm.getName()) == name and (sig is None or sig in str(mm.getSignature())):
                bo_ = BOS()
                IP(PS(bo_)).print_(mm)
                outs.append(str(bo_.toString()))
        return "\n".join(outs)

    su = mcode("SkyyGearPlugin", "setup")
    order = [su.find("GearCfg.importRolls("), su.find("GearCfg.migrate011("), su.find("GearCfg.migrateStat011("), su.find("GearCfg.migrate012("),
             su.find("GearCfg.load("), su.find("GearCharged.setup("), su.find("CfgPub.start(")]
    check(all(x >= 0 for x in order) and order == sorted(order), "Z9: setup(): importRolls -> migrate011 -> migrateStat011 -> migrate012 -> load -> "
                                                                  "GearCharged.setup -> CfgPub.start (%s)" % order)
    hs = mcode("GearHitSys", "handle")
    # (0.2.1: the weapon branch moved byte for byte into the static GearHit.weaponHit - GearHitSys resolves attacker / weapon / armor and
    # calls it; section AC executes it with real engine Damage objects)
    wh = mcode("GearHit", "weaponHit")
    check("GearHit.weaponHit(" in hs and "hitAmount" not in hs and "GearCharged.judge(" not in hs
          and "GearCharged.watch(" in wh and "GearCharged.judge(" in wh and "GearCharged.note(" in wh
          and "GearHit.hitAmount((D[IZZDD)D)" in wh and "GearHit.hitAmount((D[IZDD)D)" not in wh,
          "Z9: GearHitSys -> GearHit.weaponHit judges the hit and calls the 6-argument hitAmount (never the old 5-argument one)")
    # review of 0.1.2 finding 1: the judge gets the live record ids only for a picked record (GearShotTrack.find's own record = exact)
    check("GearShotTrack.liveIds(" in wh and wh.find("GearShotTrack.liveIds(") < wh.find("GearCharged.judge("),
          "Z9: GearHit.weaponHit passes GearShotTrack.liveIds to GearCharged.judge")
    # finding 4: note() builds its line only while a probe is armed or charged.log is on
    nt_ = mcode("GearCharged", "note")
    check(0 <= nt_.find("GearCharged.watch(") < nt_.find("Gear.fnum(") and 0 <= nt_.find("GearCfg.CHG_LOG") < nt_.find("Gear.fnum("),
          "Z9: finding 4 - GearCharged.note checks the probe + charged.log before it builds the line")
    Charged.PROBE.clear()
    Charged.LAST.clear()
    Cfg.CHG_LOG = False
    Charged.note(U1, None, IS("Weapon_Sword_Iron", 1), True, "test", False, 20, JFloat(10.0), 12.0)
    lz_ = Charged.LAST.size()
    Charged.PROBE.put(U1, JClass("java.lang.Long").valueOf(JLong(int(time.time() * 1000) + 60000)))
    Charged.note(U1, None, IS("Weapon_Sword_Iron", 1), True, "test", False, 20, JFloat(10.0), 12.0)
    lp_ = Charged.LAST.get(U1)
    check(lz_ == 0 and lp_ is not None and str(lp_[1]).startswith("CHARGED - test - Weapon_Sword_Iron - damage "),
          "Z9: note(): nothing kept without a probe; an armed probe keeps the line (%s)" % (None if lp_ is None else str(lp_[1])))
    Charged.PROBE.clear()
    Charged.LAST.clear()
    st_ = mcode("GearShotTrack", "onEntityAdded")
    check("getProjectileAssetName" in st_ and "GearHand.pick(" in st_ and "GearChg.launchCode(" in st_ and "GearShot.charged" in st_,
          "Z9: GearShotTrack records the projectile id, takes the hand snapshot, sets GearShot.charged")
    callers2 = {}
    for cn in names:
        if not cn.startswith(PKG):
            continue
        for mm in pool.get(cn).getDeclaredMethods():
            bo_ = BOS()
            IP(PS(bo_)).print_(mm)
            tx_ = str(bo_.toString())
            for callee in ("GearRoll.pool((ILjava/lang/String;)", "GearRoll.pool((I)", "GearRoll.rollMods((Ljava/lang/String;III)",
                           "GearRoll.rollMods((III)", "GearChg.canRoll(", "GearHand.pick(", "GearCharged.judge("):
                if ("gear." + callee) in tx_:
                    callers2.setdefault(callee, set()).add(cn[len(PKG):] + "." + str(mm.getName()) + str(mm.getSignature()).split(")")[0] + ")")
    check(callers2.get("GearRoll.pool((ILjava/lang/String;)") == {"GearRoll.rollMods(Ljava/lang/String;III)", "GearRoll.pool(I)"},
          "Z9: pool(slot, id) <- rollMods(id, ...) + the pool(slot) overload only: %s" % callers2.get("GearRoll.pool((ILjava/lang/String;)"))
    check("GearRoll.pool((I)" not in callers2, "Z9: nothing calls the id-less pool(slot) (%s)" % callers2.get("GearRoll.pool((I)"))
    # (0.2: the roll moved into newDoc(id, r, ident, src, lvl) - the level is stamped first; the 0.1.3 newDoc(id, r, ident, src) calls it)
    check(callers2.get("GearRoll.rollMods((Ljava/lang/String;III)") == {"GearRoll.newDoc(Ljava/lang/String;IZLjava/lang/String;I)",
                                                                        "GearRoll.reforge(Ljava/lang/String;Lorg/bson/BsonDocument;)",
                                                                        "GearRoll.identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)",
                                                                        "GearRoll.rollMods(III)"},
          "Z9: rollMods(id, ...) <- newDoc / reforge / identify (with the item id) + the old overload: %s" % callers2.get("GearRoll.rollMods((Ljava/lang/String;III)"))
    check("GearRoll.rollMods((III)" not in callers2, "Z9: nothing calls the id-less rollMods(slot, r, lvl)")
    check(callers2.get("GearChg.canRoll(") == {"GearRoll.pool(ILjava/lang/String;)", "GearCharged.probe(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/inventory/ItemStack;[ILjava/lang/String;)"},
          "Z9: canRoll <- GearRoll.pool (+ the read-only probe): %s" % callers2.get("GearChg.canRoll("))
    cc_ = pool.get(PKG + "GearChargedCmd")
    IPc = JClass("javassist.bytecode.InstructionPrinter")
    k0 = cc_.getDeclaredConstructors()[0]
    it_ = k0.getMethodInfo().getCodeAttribute().iterator()
    cpz = k0.getMethodInfo().getConstPool()
    ops = []
    while it_.hasNext():
        pos_ = it_.next()
        ops.append(str(IPc.instructionString(it_, pos_, cpz)))
    ctxt = "\n".join(ops)
    check("requirePermission" in ctxt and "setPermissionGroups" in ctxt and "anewarray" in ctxt and "iconst_0" in ctxt and "skyygear.admin" in ctxt
          and '"charged"' in ctxt, "Z9: /gear charged = requirePermission(skyygear.admin) + setPermissionGroups(new String[0])")
    gk = pool.get(PKG + "GearCmd").getDeclaredConstructors()[0]
    it_ = gk.getMethodInfo().getCodeAttribute().iterator()
    cpz = gk.getMethodInfo().getConstPool()
    ops = []
    while it_.hasNext():
        pos_ = it_.next()
        ops.append(str(IPc.instructionString(it_, pos_, cpz)))
    check("GearChargedCmd" in "\n".join(ops) and '"hytale:Adventurer"' in "\n".join(ops), "Z9: /gear (Adventurer) adds the admin sub-command charged")
    try:
        cmdz = J("GearChargedCmd")()
        AC_ = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
        fpg = AC_.class_.getDeclaredField("permissionGroups")
        fpg.setAccessible(True)
        grp = fpg.get(cmdz)
        check(grp is not None and len(grp) == 0, "Z9: the constructed /gear charged command carries an empty permission-group list")
    except Exception as ex_:
        print("Z9. note: constructing the command object in a bare JVM failed (%s) - the constructor bytecode check above stands" % ex_)
    print("Z9. bytecode done")

    # ---- Z10. class byte-compare 0.1.1 -> 0.1.2 (instruction text with constant-pool numbers stripped, fields with their types and
    # constant values): every difference must be one of the listed new parts (a member outside this list = FAIL)
    jar011 = os.path.join(HERE, "SkyyGear-0.1.1.jar")
    # 0.1.3 harness: Z10 stays the historical 0.1.1 -> 0.1.2 compare of the two shipped jars (the 0.1.2 -> 0.1.3 compare is AA9)
    jar012z = os.path.join(HERE, "SkyyGear-0.1.2.jar")

    def znorm(t):
        """instruction text without constant-pool numbers, byte offsets and branch targets; ldc_w = ldc (a constant pool that grew past
        255 entries turns ldc into ldc_w and shifts every offset after it - the same code)"""
        out_ = []
        for ln in t.split("\n"):
            ln = re.sub(r"#\d+ = ", "", ln)
            ln = re.sub(r"^\s*\d+: ", "", ln)
            ln = ln.replace("ldc_w ", "ldc ")
            ln = re.sub(r"^(goto|goto_w|jsr|if\w*) \d+", r"\1 L", ln)
            out_.append(ln)
        return "\n".join(out_)

    def ival(ln):
        m_ = re.match(r"^(?:iconst_(\d)|bipush (-?\d+)|sipush (-?\d+))$", ln.strip())
        return None if not m_ else int([g for g in m_.groups() if g is not None][0])

    def shift_only(a_, b_):
        """0.1.1 -> 0.1.2 differs ONLY by the stat-index shift: chg went in at index 5, so every stat index >= 5 (and the stat count 40,
        i.e. NS) is exactly one higher; javassist inlines static final int constants, so the methods that use them change that way"""
        la_, lb_ = a_.split("\n"), b_.split("\n")
        if len(la_) != len(lb_):
            return False
        for x_, y_ in zip(la_, lb_):
            if x_ == y_:
                continue
            vx, vy = ival(x_), ival(y_)
            if vx is None or vy is None or vy != vx + 1 or not (5 <= vx <= 40):
                return False
        return True

    if os.path.isfile(jar011) and os.path.isfile(jar012z):
        def cls_members(p_, cn):
            cc_ = p_.get(cn)
            mem = {}
            for mm in list(cc_.getDeclaredMethods()):
                bo_ = BOS()
                IP(PS(bo_)).print_(mm)
                mem["m " + str(mm.getName()) + str(mm.getSignature())] = znorm(str(bo_.toString()))
            for k0 in list(cc_.getDeclaredConstructors()):
                ca = k0.getMethodInfo().getCodeAttribute()
                it_ = ca.iterator()
                cp_ = k0.getMethodInfo().getConstPool()
                ops_ = []
                while it_.hasNext():
                    pz_ = it_.next()
                    ops_.append(str(JClass("javassist.bytecode.InstructionPrinter").instructionString(it_, pz_, cp_)))
                mem["c " + str(k0.getSignature())] = znorm("\n".join(ops_))
            ci = cc_.getClassInitializer()
            if ci is not None:
                ca = ci.getMethodInfo().getCodeAttribute()
                it_ = ca.iterator()
                cp_ = ci.getMethodInfo().getConstPool()
                ops_ = []
                while it_.hasNext():
                    pz_ = it_.next()
                    ops_.append(str(JClass("javassist.bytecode.InstructionPrinter").instructionString(it_, pz_, cp_)))
                mem["<clinit>"] = znorm("\n".join(ops_))
            for f_ in list(cc_.getDeclaredFields()):
                cv = None
                try:
                    cv = f_.getConstantValue()
                except Exception:
                    cv = None
                mem["f " + str(f_.getName())] = str(f_.getSignature()) + " = " + str(cv)
            mem["interfaces"] = ",".join(sorted(str(x) for x in cc_.getClassFile().getInterfaces())) + " super " + str(cc_.getClassFile().getSuperclass())
            return mem

        pa = Pool(False)
        pa.appendClassPath(jar011)
        pa.appendClassPath(B.SERVER_JAR)
        pa.appendSystemPath()
        pb = Pool(False)
        pb.appendClassPath(jar012z)
        pb.appendClassPath(B.SERVER_JAR)
        pb.appendSystemPath()
        n011 = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar011).namelist() if n.endswith(".class"))
        n012 = sorted(n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar012z).namelist() if n.endswith(".class"))
        added_cls = sorted(set(n012) - set(n011))
        gone_cls = sorted(set(n011) - set(n012))
        diffs, shifted = {}, {}
        for cn in sorted(set(n011) & set(n012)):
            ma, mb = cls_members(pa, cn), cls_members(pb, cn)
            dd = sorted(k_ for k_ in set(ma) | set(mb) if ma.get(k_) != mb.get(k_))
            for k_ in dd:
                if k_ in ma and k_ in mb and k_.startswith("f ") and ma[k_].split(" = ")[0] == mb[k_].split(" = ")[0]:
                    try:
                        if int(mb[k_].split(" = ")[1]) == int(ma[k_].split(" = ")[1]) + 1 and 5 <= int(ma[k_].split(" = ")[1]) <= 40:
                            shifted.setdefault(cn[len(PKG):], []).append(k_)
                            continue
                    except ValueError:
                        pass
                if k_ in ma and k_ in mb and not k_.startswith("f ") and shift_only(ma[k_], mb[k_]):
                    shifted.setdefault(cn[len(PKG):], []).append(k_)
                    continue
                diffs.setdefault(cn[len(PKG):], []).append(("+" if k_ not in ma else ("-" if k_ not in mb else "~")) + k_)
        # every difference, with its reason (checked by hand against the build script; kept exact so a stray change fails here)
        EXPECT = {
            # config kit (tools/skyycfg.py, regenerated from the rows): 41 -> 44 rows, VERSION 0.1.1 -> 0.1.2
            "CfgFile": ["~<clinit>"],
            "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # /gear charged (read only, before the profile:busy check)
            "GearAdmin": ["~m run(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/lang/String;Ljava/lang/String;)V"],
            # disconnect: GearCharged.forget (probe + hand snapshot)
            "GearBye": ["~m accept(Ljava/lang/Object;)V"],
            # the charged.* fields + loader lines, the stat arrays (41 stats), the default text, migrate012 + its text step
            "GearCfg": ["~<clinit>", "+f CHG_ADD", "+f CHG_LOG", "+f CHG_ON", "+f CHG_SPELL", "+f CH_MARK", "+f CH_MARK_ID", "+f CH_ROWC",
                        "+f CH_ROWK", "+f CH_ROWL", "+f CH_WHO", "~m apply(Ljava/util/Properties;Z)V", "+m chAfter(Ljava/util/ArrayList;II)I",
                        "+m chEnd(Ljava/util/ArrayList;I[Ljava/lang/String;)I", "+m chPut(Ljava/util/ArrayList;ILjava/util/ArrayList;Ljava/lang/String;)V",
                        "+m chUpdate(Ljava/lang/String;)[Ljava/lang/Object;", "~m defaultsText()Ljava/lang/String;", "+m migrate012()Ljava/lang/String;"],
            # /gear adds the charged sub-command
            "GearCmd": ["~c ()V"],
            # the stat tables with chg after cd + I_CHG
            "GearDefs": ["~<clinit>", "+f I_CHG"],
            # the charged factor (6-argument hitAmount; the 5-argument one now delegates with chg = false)
            "GearHit": ["+f I_CHG", "~m hitAmount(D[IZDD)D", "+m hitAmount(D[IZZDD)D"],
            # judge + note + the 6-argument hitAmount, srec
            "GearHitSys": ["~m handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"],
            # the item id reaches the pool (newDoc / reforge / identify pass it; the id-less overloads delegate)
            "GearRoll": ["~m identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lorg/bson/BsonDocument;",
                         "~m newDoc(Ljava/lang/String;IZLjava/lang/String;)Lorg/bson/BsonDocument;", "~m pool(I)[I", "+m pool(ILjava/lang/String;)[I",
                         "~m reforge(Ljava/lang/String;Lorg/bson/BsonDocument;)Lorg/bson/BsonDocument;", "~m rollMods(III)Lorg/bson/BsonArray;",
                         "+m rollMods(Ljava/lang/String;III)Lorg/bson/BsonArray;"],
            # the launch record: charged flag, projectile id, snapshot used
            "GearShot": ["+f charged", "+f pid", "+f snap"],
            # + the review of 0.1.2 finding 1: liveIds (the item ids of the shooter's live records for the charged judge)
            "GearShotTrack": ["+m liveIds(Ljava/util/UUID;)[Ljava/lang/String;",
                              "~m onEntityAdded(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/AddReason;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"],
            # the grey "(off on this server)" line while charged.on is off
            "GearView": ["+m dim(Ljava/lang/String;)Z", "~m statLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;Ljava/util/ArrayList;)V",
                         "~m suffix(I)Ljava/lang/String;"],
            # migrate012 in the setup order, GearCharged.setup (GearHandSys), the ready line
            "SkyyGearPlugin": ["~m setup()V"]}
        check([c[len(PKG):] for c in added_cls] == ["GearCharged", "GearChargedCmd", "GearChg", "GearChgState", "GearChgVars", "GearChgWalk", "GearHand",
                                                    "GearHandSys"] and not gone_cls,
              "Z10: new classes = the 7 charged-attack classes + GearChargedCmd, none removed: %s / %s" % (added_cls, gone_cls))
        extra = dict((c, [m for m in ms if m not in EXPECT.get(c, [])]) for c, ms in diffs.items())
        extra = dict((c, ms) for c, ms in extra.items() if ms)
        missing_ = dict((c, [m for m in ms if m not in diffs.get(c, [])]) for c, ms in EXPECT.items())
        missing_ = dict((c, ms) for c, ms in missing_.items() if ms)
        check(not extra, "Z10: no difference outside the listed new parts: %s" % extra)
        check(not missing_, "Z10: every listed part really differs (the list is exact): %s" % missing_)
        same_cls = len(set(n011) & set(n012)) - len(set(diffs) | set(shifted))
        print("Z10. 0.1.1 -> 0.1.2 class compare: %d classes identical, %d with new parts, %d with only the stat-index shift, %d new"
              % (same_cls, len(diffs), len(set(shifted) - set(diffs)), len(added_cls)))
        for c in sorted(diffs):
            print("     %-16s %s" % (c, ", ".join(re.sub(r"\(.*", "", m_) for m_ in diffs[c])))
        print("     stat-index shift only (every stat index >= 5 and NS exactly +1): " + "; ".join(
            "%s: %s" % (c, ", ".join(re.sub(r"\(.*", "", m_) for m_ in ms)) for c, ms in sorted(shifted.items())))
        ea = [n for n in zipfile.ZipFile(jar011).namelist() if not n.endswith(".class")]
        eb = [n for n in zipfile.ZipFile(jar012z).namelist() if not n.endswith(".class")]
        za, zb = zipfile.ZipFile(jar011), zipfile.ZipFile(jar012z)
        ndiff = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
        check(ndiff == ["manifest.json"], "Z10: non-class entries: only manifest.json differs (version): %s" % ndiff)
    else:
        print("Z10. note: SkyyGear-0.1.1.jar not found - the class compare was skipped")
    print("Z. 0.1.2 Charged Attack Damage done")

    # ============================================================================================================== AA. 0.1.3
    # AA1 the level families (table, lookup over every vanilla id, multi-word rule, loader), AA2 migrate013 on a scratch COPY of the live
    # config.properties (+ CRLF, custom row kept, kit Undo, removed row never re-added, History blocked, fresh file, text-step edge cases
    # + random files), AA3 the world-chest decision (prefab chest tagged once, loot-table chest unchanged, player storage / islands /
    # undecidable placer never touched), AA4 the per-world memory file, AA5 SkyyExploration's extra items through the loot window (both
    # orders, grace, overflow drop), AA6 no leak into player inventories, AA7 the engine side (bytecode: hooks, entry points, ContainerWindow),
    # AA8 setup / tick / ready wiring, AA9 the class byte-compare 0.1.2 -> 0.1.3.
    Chest, Opened = J("GearChestOpen"), J("GearOpened")
    AZp = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    azz = zipfile.ZipFile(AZp)
    AZJ = {}
    for n_ in azz.namelist():
        if n_.startswith("Server/Item/Items/") and n_.endswith(".json"):
            try:
                AZJ[os.path.basename(n_)[:-5]] = json.loads(azz.read(n_).decode("utf-8-sig"))
            except Exception:
                pass

    def azget(i_, k_):
        seen_, cur_ = 0, i_
        while cur_ in AZJ and seen_ < 16:
            if k_ in AZJ[cur_]:
                return AZJ[cur_][k_]
            cur_, seen_ = AZJ[cur_].get("Parent"), seen_ + 1
        return None

    def maxst(i_):
        seen_, cur_, sect_ = 0, i_, False
        while cur_ in AZJ and seen_ < 16:
            d_ = AZJ[cur_]
            if "MaxStack" in d_:
                return int(d_["MaxStack"])
            sect_ = sect_ or any(k_ in d_ for k_ in ("Weapon", "Armor", "Tool"))
            cur_, seen_ = d_.get("Parent"), seen_ + 1
        return 1 if sect_ else 100

    AMMO_T = ["arrow", "arrows", "bolt", "bolts", "bomb", "bombs", "dart", "darts", "grenade", "grenades", "ammo", "bullet", "bullets",
              "shell", "shells", "shuriken", "shurikens", "thrown"]

    def is_ammo(i_):
        ps_ = i_.split("_")
        if maxst(i_) <= 1:
            return len(ps_) > 1 and ps_[1].lower() in AMMO_T
        return any(p_.lower() in AMMO_T for p_ in ps_[1:])

    EXCL_T = ("Weapon_Shield_", "Weapon_Bomb", "Weapon_Gun", "Weapon_Deployable_", "Weapon_Dart_", "Weapon_Claws_", "Weapon_Blowgun_",
              "Weapon_Assault_Rifle", "Weapon_Handgun", "Weapon_Grenade_", "Weapon_Test_")
    GEAR_AZ = sorted(i_ for i_ in AZJ if i_.startswith("Armor_") or (i_.startswith("Weapon_") and not is_ammo(i_) and not i_.startswith(EXCL_T)))
    METALS = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 15), ("Thorium", 20), ("Cobalt", 25), ("Adamantite", 35),
              ("Mithril", 40), ("Onyxium", 40)]
    # the 59 family rows, written out here on their own (a change in the build that is not repeated here fails AA1; review of 0.1.3
    # finding 7: Bone 5, Praetorian 25, Spellbook_Frost + Staff_Frost 30)
    FAMS = [("Wool", 5), ("Linen", 10), ("Cotton", 15), ("Silk", 20), ("Cindercloth", 30), ("Leather_Soft", 5), ("Leather_Light", 10),
            ("Leather_Medium", 15), ("Leather_Heavy", 20), ("Leather_Raven", 20), ("Stone", 5), ("Trork", 5), ("Fishbone", 5), ("Scrap", 10),
            ("Steel_Rusty", 10), ("Steel_Flail_Rusty", 10), ("Leaf", 10), ("Kweebec", 10), ("Cutlass", 10), ("Shortbow_Bomb", 10),
            ("Shortbow_Combat", 10), ("Shortbow_Pull", 10), ("Shortbow_Ricochet", 10), ("Shortbow_Vampire", 10), ("Tribal", 15), ("Bone", 5),
            ("Steel", 20), ("Incandescent", 20), ("Zombie", 20), ("Katana", 20), ("Nexus", 20), ("Runic", 20), ("Kunai", 20), ("Grimoire", 20),
            ("Wizard", 20), ("Doomed", 25), ("Void", 25), ("Frost", 25), ("Flame", 25), ("Praetorian", 25), ("Ancient", 30), ("Steel_Ancient", 30),
            ("Crystal", 30), ("Spellbook_Fire", 30), ("Spellbook_Frost", 30), ("Staff_Frost", 30), ("Scarab", 35), ("Spectral", 35), ("Silversteel", 35), ("Demon", 35), ("Rekindle", 35),
            ("Crystal_Flame", 40), ("Crystal_Ice", 40), ("Prisma", 45), ("Root", 5), ("Stoneskin", 5), ("Bamboo", 5), ("Cane", 5), ("Onion", 5)]

    def pylook(table, i_, mw=None):
        """the lookup rule written independently: at each id word from the left, the longest entry first (max 3 words)"""
        m_ = dict((t_.lower(), l_) for t_, l_ in table)
        mw_ = mw if mw is not None else min(3, max(len(t_.split("_")) for t_, _l in table))
        tk_ = i_.split("_")
        for a_ in range(len(tk_)):
            for n2 in range(mw_, 0, -1):
                if a_ + n2 <= len(tk_) and "_".join(tk_[a_:a_ + n2]).lower() in m_:
                    return m_["_".join(tk_[a_:a_ + n2]).lower()]
        return None

    def oldlook(i_):
        """0.1.2's loop: the first id word that is in the metal table"""
        for t_ in i_.split("_"):
            for mt, ml in METALS:
                if t_.lower() == mt.lower():
                    return ml
        return None

    # ---- AA1. the family table + GearLevel.level over every vanilla weapon / armor id
    check([(str(t_), int(l_)) for t_, l_ in zip(Cfg.FAM_T, Cfg.FAM_L)] == FAMS, "AA1: GearCfg.FAM_T / FAM_L = the 59 family rows in order")
    check(len(FAMS) == 59 and len(set(t_.lower() for t_, _l in FAMS)) == 59, "AA1: 59 distinct rows")
    Cfg.apply(Props(), False)
    # 0.2: the built-in table is the band table - the metal starts with Wood / Crude at 1 and the new Armor_Copper row (1), the same family
    # starts; section AB checks the caps
    METALS02 = [("Crude", 1), ("Wood", 1), ("Copper", 10), ("Armor_Copper", 1), ("Bronze", 15), ("Iron", 15), ("Thorium", 20), ("Cobalt", 25),
                ("Adamantite", 35), ("Mithril", 40), ("Onyxium", 40)]
    check(int(Cfg.MAT_WORDS) == 3 and all(int(Cfg.MAT.get(t_.lower())) == l_ for t_, l_ in METALS02 + FAMS) and Cfg.MAT.size() == 70,
          "AA1: built-in defaults (no file) = the 10 metals + Armor_Copper (0.2) + 59 families, MAT_WORDS 3")
    Cfg.LEVEL_DEFAULT = 77             # the bare JVM has no Item assets: 77 = "no table row matched" (Hytale's level would apply in game)
    fallback = [i_ for i_ in GEAR_AZ if oldlook(i_) is None]
    devs = [i_ for i_ in fallback if pylook(METALS + FAMS, i_) is None]
    mism, metal_changed = [], []
    for i_ in GEAR_AZ:
        want_ = pylook(METALS02 + FAMS, i_)
        got_ = int(Lvl.level(i_, None))
        if got_ != (77 if want_ is None else want_):
            mism.append((i_, got_, want_))
        if oldlook(i_) is not None and got_ != oldlook(i_):
            metal_changed.append(i_)
    check(not mism, "AA1: the jar's GearLevel.level = the independent rule for all %d vanilla ids: %s" % (len(GEAR_AZ), mism[:5]))
    # (0.2: exactly the Wood / Crude ids move 0 -> 1 and the copper armor 10 -> 1; every other metal-resolved id keeps its 0.1.2 level)
    mc_want = sorted(i_ for i_ in GEAR_AZ if oldlook(i_) == 0 or i_.startswith("Armor_Copper_"))
    check(sorted(metal_changed) == mc_want and all(int(Lvl.level(i_, None)) == 1 for i_ in mc_want) and len(mc_want) > 4,
          "AA1: every metal-resolved id keeps its 0.1.2 level except Wood / Crude (0 -> 1) and copper armor (10 -> 1): %s"
          % sorted(set(metal_changed) ^ set(mc_want))[:5])
    check(len(GEAR_AZ) == 304 and len(fallback) == 160, "AA1: 304 vanilla weapon / armor ids, 160 fell back in 0.1.2 (%d / %d)" % (len(GEAR_AZ), len(fallback)))
    check(sorted(devs) == ["Armor_QA_Chest", "Armor_QA_Hands", "Armor_QA_Legs", "Armor_Trooper_Chest", "Armor_Trooper_Head", "Armor_Trooper_Legs",
                           "Weapon_Shortbow_Test_Zoom"] and all(str(azget(i_, "Quality")) in ("Debug", "Developer") for i_ in devs),
          "AA1: only the 7 developer-quality ids still use Hytale's level: %s" % devs)
    check(int(Lvl.level("Weapon_Daggers_Stone_Trork", None)) == 5, "AA1: Stone Trork Daggers -> 5 (Skyy's report: was Lv 25)")
    for i_, l_ in (("Weapon_Sword_Steel_Rusty", 10), ("Weapon_Club_Steel_Flail_Rusty", 10), ("Weapon_Sword_Steel", 20), ("Armor_Steel_Ancient_Head", 30),
                   ("Weapon_Crossbow_Ancient_Steel", 30), ("Armor_Leather_Soft_Chest", 5), ("Armor_Cloth_Wool_Legs", 5), ("Armor_Wool_Head", 5),
                   ("Weapon_Staff_Crystal_Ice", 40), ("Weapon_Staff_Crystal_Fire_Trork", 30), ("Weapon_Spellbook_Fire", 30), ("Weapon_Staff_Bo_Wood", 1),
                   ("Weapon_Staff_Wood_Kweebec", 1), ("Armor_Kweebec_Chest", 10), ("Weapon_Daggers_Claw_Bone", 5), ("Weapon_Daggers_Fang_Doomed", 25),
                   ("Weapon_Club_Iron_Rusty", 15), ("Armor_Prisma_Chest", 45), ("Weapon_Sword_Iron", 15), ("Weapon_Staff_Bone", 5),
                   ("Weapon_Spellbook_Frost", 30), ("Weapon_Staff_Frost", 30), ("Weapon_Sword_Frost", 25), ("Weapon_Shortbow_Frost", 25),
                   ("Weapon_Longsword_Praetorian", 25), ("Weapon_Club_Zombie_Frost_Arm", 20)):
        check(int(Lvl.level(i_, None)) == l_, "AA1: GearLevel.level(%s) = %d" % (i_, l_))
    def pyentry(table, i_):
        m_ = dict((t2.lower(), t2) for t2, _l in table)
        tk_ = i_.split("_")
        for a_ in range(len(tk_)):
            for n2 in range(3, 0, -1):
                if a_ + n2 <= len(tk_) and "_".join(tk_[a_:a_ + n2]).lower() in m_:
                    return m_["_".join(tk_[a_:a_ + n2]).lower()]
        return None

    print("AA1. family table (entry, new level, Hytale levels of its vanilla items, how many):")
    for t_, l_ in FAMS:
        its = [i_ for i_ in fallback if pyentry(METALS + FAMS, i_) == t_]
        print("     %-18s %3d  Hytale %-9s %2d" % (t_, l_, ",".join(sorted(set(str(azget(x, "ItemLevel")) for x in its), key=int)), len(its)))
    check(sum(1 for i_ in fallback if pyentry(METALS + FAMS, i_) in dict(FAMS)) == 153, "AA1: the 59 rows cover 153 ids")
    # the multi-word rule: only one-word entries -> exactly the 0.1.2 loop (MAT_WORDS 1); entries of 2 / 3 words; case; a 4-word entry
    pm_ = Props()
    pm_.setProperty("level.default", "77")
    for t_, l_ in METALS:
        pm_.setProperty("level.material." + t_, str(l_))
    Cfg.apply(pm_, True)
    check(int(Cfg.MAT_WORDS) == 1 and all(int(Lvl.level(i_, None)) == (77 if oldlook(i_) is None else oldlook(i_)) for i_ in GEAR_AZ),
          "AA1: a table of one-word entries = the 0.1.2 loop over every vanilla id (MAT_WORDS 1)")
    pm_.setProperty("level.material.STEEL_rusty", "3")
    Cfg.apply(pm_, True)
    check(int(Cfg.MAT_WORDS) == 2 and int(Lvl.level("Weapon_Sword_Steel_Rusty", None)) == 3 and int(Lvl.level("Weapon_Sword_Steel", None)) == 77,
          "AA1: a two-word entry in any case matches those words in a row only (MAT_WORDS 2)")
    pm_.setProperty("level.material.Sword_Steel_Rusty", "4")
    Cfg.apply(pm_, True)
    check(int(Cfg.MAT_WORDS) == 3 and int(Lvl.level("Weapon_Sword_Steel_Rusty", None)) == 4, "AA1: at one id word the longer entry wins (3 words)")
    pm_.setProperty("level.material.Weapon_Sword_Steel_Rusty", "6")
    LW1 = os.path.join(SCRATCH, "work", "aa1-warn", "gear.log")
    Log.FILE = Paths.get(LW1)
    Cfg.apply(pm_, True)
    check(int(Cfg.MAT_WORDS) == 3 and int(Lvl.level("Weapon_Sword_Steel_Rusty", None)) == 4, "AA1: a 4-word entry never matches (max 3 words)")
    Log.flush()
    lw_ = ""
    for _w in range(30):
        lw_ = open(LW1, encoding="utf-8").read() if os.path.isfile(LW1) else ""
        if "has 4 words" in lw_:
            break
        time.sleep(0.1)
    check("WARN config.properties: level.material.Weapon_Sword_Steel_Rusty has 4 words - an entry matches at most 3 words" in lw_,
          "AA1: the loader WARNs once about a 4-word entry (review of 0.1.3 finding 8)")
    Log.FILE = None
    pm_.setProperty("level.material.Iron_Rusty", "10")
    Cfg.apply(pm_, True)
    check(int(Lvl.level("Weapon_Club_Iron_Rusty", None)) == 10 and int(Lvl.level("Weapon_Club_Iron", None)) == 15,
          "AA1: Skyy can add Iron_Rusty 10 later (the note in the Steel_Rusty row)")
    pi_ = Props()
    pi_.setProperty("level.item.Weapon_Daggers_Stone_Trork", "12")
    for t_, l_ in METALS + FAMS:
        pi_.setProperty("level.material." + t_, str(l_))
    Cfg.apply(pi_, True)
    check(int(Lvl.level("Weapon_Daggers_Stone_Trork", None)) == 12, "AA1: Level by item still wins over the family row")
    Cfg.LEVEL_DEFAULT = 0
    Cfg.apply(Props(), False)
    rowh = [str(h) for k_, h in zip([str(k) for k in Rows.KEYS], Rows.HELPS) if k_ == "level.material"]
    check(rowh == ["Band by the first id word (Leather_Soft = 2 words). One number = N to N+width-1. Skyy 10-01."], "AA1: the row help (0.2 text)")
    zdt3 = str(Cfg.defaultsText())
    zl3 = zdt3.split("\n")
    # (0.2: the fresh file's family rows are bands start..start+7, never above 49)
    FML = [str(Cfg.FM_MARK)] + ["level.material.%s=%d,%d" % (t_, l_, min(l_ + 7, 49)) for t_, l_ in FAMS]
    check(zl3[zl3.index("level.material.Onyxium=40,49") + 1:zl3.index("level.material.Onyxium=40,49") + 1 + len(FML)] == FML
          and zdt3.count(str(Cfg.FM_MARK_ID)) == 1 and Cfg.fmUpdate(zdt3) is None, "AA1: the fresh file: the marker + 59 rows right under Onyxium; it never updates")
    check(str(Cfg.FM_MARK).startswith("# SkyyGear 0.1.3 level families (Skyy 2026-10-01): ") and "=" not in str(Cfg.FM_MARK)
          and str(Cfg.FM_WHO) == "SkyyGear 0.1.3", "AA1: the marker text + name")
    print("AA1. level families done")

    # ---- AA2. migrate013 on a scratch COPY of the live config.properties (read only source) and on derived cases
    AD = os.path.join(SCRATCH, "work", "aa013")

    def acase(name, data):
        cfg_quiet()
        shutil.rmtree(os.path.join(AD, name), ignore_errors=True)
        d_ = os.path.join(AD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def expf(t, rows=FAMS, after="level.material.Onyxium=40"):
        """the expected result, built independently: the marker + the rows right after the anchor line, line endings kept"""
        nl_ = "\r\n" if "\r\n" in t else "\n"
        a_ = nl_ + after + nl_
        assert t.count(a_) == 1, after
        return t.replace(a_, nl_ + after + nl_ + nl_.join([str(Cfg.FM_MARK)] + ["level.material.%s=%d" % r_ for r_ in rows]) + nl_)

    INFO13 = ("config.properties: added %d level family rows (" % len(FAMS) + ", ".join("%s %d" % r_ for r_ in FAMS) + ") - those weapons and armor use "
              "these levels now instead of Hytale's item level; the old file is in config-history, Server Setup -> Changes can undo each row")
    live13 = LIVE_NOW
    if live13 is not None and b"SkyyGear 0.1.3 level families" in live13:
        print("AA2. note: the live file already has the 0.1.3 rows - the live-copy case runs on its pre-0.1.3 History copy")
        live13 = None
        # (0.2 harness: SkyyGear 0.1.3 is deployed, so the live file carries its update; the live config-history keeps the copy "before the
        # 0.1.3 level family rows" - read only - which is the live file the 0.1.3 update ran on)
        # (review of 0.2 finding 6: the live config-history first, then the deploy backups)
        pre3, where3 = hist_copy("before the 0.1.3 level family rows")
        check(pre3 is not None, "AA2: a 'before the 0.1.3 level family rows' History copy exists (the live config-history or a deploy "
                                "backup): searched %s" % where3)
        if pre3 is not None:
            live13 = pre3
            check(b"SkyyGear 0.1.2 charged attack lines" in live13 and b"SkyyGear 0.1.3 level families" not in live13,
                  "AA2: that copy is the 0.1.2-updated live file (0.1.1 / 0.1.2 markers, no 0.1.3 rows)")
    if live13 is not None:
        lt3 = live13.decode("latin-1")
        d, f = acase("a-live", live13)
        hist_pre = baks(d)
        log_pre = clog(d)
        res = str(Cfg.migrate013())
        got = rb(f)
        check(got == expf(lt3).encode("latin-1"), "AA2(a): the live copy -> exactly the marker + 59 rows after Onyxium, every other byte kept")
        check(res.split("\n") == [INFO13], "AA2(a): one INFO line: %r" % res[:200])
        print("AA2. INFO line the live file produces: [SkyyGear] " + res[:160] + " ...")
        po_, pn_ = props(lt3), props(got.decode("latin-1"))
        check(all(pn_.get(k_) == v_ for k_, v_ in po_.items()) and sorted(set(pn_) - set(po_)) == sorted("level.material." + t_ for t_, _l in FAMS)
              and all(pn_["level.material." + t_] == str(l_) for t_, l_ in FAMS), "AA2(a): every old key keeps its value; only the 59 family keys are new")
        ol_, nl2 = lt3.split("\n"), got.decode("latin-1").split("\n")
        i0 = ol_.index("level.material.Onyxium=40") + 1
        check(nl2[:i0] == ol_[:i0] and nl2[i0 + 1 + len(FAMS):] == ol_[i0:], "AA2(a): the old lines are all there, in order, unchanged")
        b_ = baks(d)
        ix = idx(d)
        check(len(b_) == len(hist_pre) + 1 and rb(os.path.join(d, "config-history", b_[-1])) == live13
              and ix[-1].split("\t")[3:] == ["SkyyGear 0.1.3", "before the 0.1.3 level family rows"], "AA2(a): History keeps the old file (one new copy, named)")
        cl = clog(d)
        want = [["SkyyGear 0.1.3", "-", "update", "level.material[%s]" % t_, "(none)", str(l_), "ok"] for t_, l_ in FAMS]
        check(cl[:len(log_pre)] == log_pre and [l_.split("\t")[1:] for l_ in cl[len(log_pre):]] == want
              and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l_.split("\t")[0]) for l_ in cl[len(log_pre):]),
              "AA2(a): 59 config-changes.log lines (old '(none)' = Undo removes the row), the earlier lines kept")
        Cfg.load()
        check(int(Lvl.level("Weapon_Daggers_Stone_Trork", None)) == 5 and int(Cfg.MAT_WORDS) == 3 and int(Cfg.MAT.get("iron")) == 15,
              "AA2(a): the loader reads the rows (Stone Trork Daggers 5)")
        # (0.2: before migrate02 the one-number rows read N to N+7 - for the 59 families that IS their 0.2 default band)
        check(str(Cfg.matText()).endswith("Onyxium 40-47; 59 of 59 family rows (59 at the 0.2 default band)"), "AA2(a): the ready line: " + str(Cfg.matText()))
        # (b) the second start changes nothing
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and str(Cfg.migrate012()) == "" and str(Cfg.migrate013()) == ""
              and rb(f) == got and len(baks(d)) == len(b_) and len(clog(d)) == len(cl), "AA2(b): a second start changes nothing (file, History, log)")
        # (c) CRLF
        d, f = acase("c-crlf", lt3.replace("\n", "\r\n").encode("latin-1"))
        res = str(Cfg.migrate013())
        gc = rb(f)
        check(gc == expf(lt3.replace("\n", "\r\n")).encode("latin-1") and gc.replace(b"\r\n", b"\n") == got and res == INFO13,
              "AA2(c): a CRLF file gets the same rows, every line still ends CRLF")
        # (d) a family row Skyy already has (any case) is kept + noted, never doubled
        td = lt3.replace("\nlevel.material.Onyxium=40\n", "\nlevel.material.Onyxium=40\nlevel.material.stone=3\n")
        d, f = acase("d-custom", td.encode("latin-1"))
        res = str(Cfg.migrate013()).split("\n")
        f56 = [r_ for r_ in FAMS if r_[0] != "Stone"]
        check(rb(f) == expf(td, f56, "level.material.stone=3").encode("latin-1"), "AA2(d): stone=3 kept, 58 rows added after it")
        check(res[1:] == ["level.material.Stone is already in the file - kept"] and res[0].startswith("config.properties: added 58 level family rows (Wool 5,"),
              "AA2(d): INFO + the kept note: %s" % res[1:])
        Cfg.load()
        check(int(Lvl.level("Weapon_Sword_Stone_Trork", None)) == 3, "AA2(d): the loader: Stone 3 (Skyy's value)")
        # (e) Undo through the config kit (SkyyMenu sends the inverse: remove), and the removed row never comes back
        d, f = acase("e-kit", live13)
        Cfg.migrate013()
        Cfg.load()
        CfgPubA = J("CfgPub")
        OAa = JArray(JObject)
        CfgPubA.start(Paths.get(os.path.dirname(d)), None)
        fna = bridge.get("config:fn:SkyyGear")
        lga = [str(x) for x in fna.apply(OAa(["log", Integer.valueOf(100)]))]
        check(sum(1 for l_ in lga if "\tupdate\tlevel.material[" in l_ and "\t(none)\t" in l_ and l_.endswith("\tok")) == 59,
              "AA2(e): the kit's log op lists the 59 added rows as ok lines (SkyyMenu offers Undo)")
        ksa = fna.apply(OAa(["keys", "level.material", ""]))
        kda = dict(zip([str(x) for x in ksa[0]], [str(x) for x in ksa[2]]))
        check(kda.get("Stone") == "5" and kda.get("Leather_Soft") == "5" and kda.get("Steel_Flail_Rusty") == "10" and len(kda) == 69,
              "AA2(e): Server Setup lists the 69 rows (multi-word entries too)")
        ua = fna.apply(OAa(["remove", "level.material", "Fishbone", None, "console", "yes", "console"]))
        # (0.2: a change in Server Setup is a Min | Cap band)
        ub = fna.apply(OAa(["tset", "level.material", "Bone", "12|19", None, "console", "yes", "console"]))
        CfgPubA.flush()
        kt3 = rb(f).decode("latin-1")
        check(str(ua[0]) == "ok" and str(ub[0]) == "ok" and "level.material.Fishbone=" not in kt3 and "\nlevel.material.Bone=12,19\n" in kt3
              and int(Lvl.level("Weapon_Spear_Fishbone", None)) == 0 and int(Lvl.level("Weapon_Sword_Bone", None)) == 12,
              "AA2(e): Undo of one added row (remove) + a change of another apply at once (Fishbone -> Hytale's level, Bone 12-19)")
        check(str(Cfg.migrate013()) == "" and rb(f).decode("latin-1") == kt3, "AA2(e): the next start never adds the removed row back")
    else:
        check(False, "AA2: no live config.properties to copy")
    # (f) no file / fresh file
    d, f = acase("f-fresh", None)
    check(str(Cfg.migrate013()) == "" and not os.path.exists(f), "AA2(f): no file -> nothing written")
    Cfg.load()
    ff_ = rb(f)
    check(ff_ == zdt3.encode("utf-8") and str(Cfg.migrate013()) == "" and rb(f) == ff_ and not baks(d), "AA2(f): the fresh %s file never updates (0.1.3 update)" % VERSION)
    # (g) History cannot be written -> WARN, untouched; the next start adds the rows
    if live13 is not None:
        d, f = acase("g-nohist", live13)
        open(os.path.join(d, "config-history"), "w").write("x")
        Log.FILE = Paths.get(os.path.join(d, "gear.log"))
        check(str(Cfg.migrate013()) == "" and rb(f) == live13, "AA2(g): History blocked -> the file stays untouched")
        Log.flush()
        gl = open(os.path.join(d, "gear.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "gear.log")) else ""
        check("NOT given the 0.1.3 level family rows" in gl and "the next start tries again" in gl, "AA2(g): one WARN says why")
        os.remove(os.path.join(d, "config-history"))
        check(str(Cfg.migrate013()) == INFO13 and rb(f) == expf(lt3).encode("latin-1"), "AA2(g): the next start adds them")
        Log.FILE = None
    # (h) the pure text step on edge cases
    LVHa, LVMa, FMa = str(Cfg.LV_HEAD), str(Cfg.LV_MARK), str(Cfg.FM_MARK)
    BLK13 = "\n".join([FMa] + ["level.material.%s=%d" % r_ for r_ in FAMS])

    def fu(t):
        r_ = Cfg.fmUpdate(t)
        return None if r_ is None else str(r_[0])

    check(fu("a=1\n" + LVHa + "\n" + LVMa + "\nb=2\n") == "a=1\n" + LVHa + "\n" + LVMa + "\n" + BLK13 + "\nb=2\n",
          "AA2(h): no level.material line -> right under the 0.1.1 marker")
    check(fu("a=1\n" + LVHa + "\nb=2\n") == "a=1\n" + LVHa + "\n" + BLK13 + "\nb=2\n", "AA2(h): no marker -> right under the levels header")
    check(fu("a=1\nb=2\n") == "a=1\nb=2\n" + BLK13 + "\n" and fu("a=1") == "a=1\n" + BLK13 and fu("") == BLK13 + "\n",
          "AA2(h): no anchor -> the end of the file (no final newline stays so)")
    BSL = chr(92)
    t_ = "level.material.Iron=15\nx=a" + BSL + "\n"
    check(fu(t_) == "level.material.Iron=15\n" + BLK13 + "\nx=a" + BSL + "\n", "AA2(h): after the last level.material entry, not at the open end")
    t_ = "a=1\nlevel.material.Iron=1" + BSL + "\n"
    r_ = fu(t_)
    check(r_ == "a=1\n" + BLK13 + "\nlevel.material.Iron=1" + BSL + "\n" and props(r_).get("level.material.Iron") == props(t_).get("level.material.Iron"),
          "AA2(h): a last level.material entry still open at the end -> the block goes before it (the 0.1.1 finding 4 trap)")
    check(Cfg.fmUpdate("  ! SkyyGear 0.1.3 level families, old\nlevel.material.Iron=15\n") is None, "AA2(h): a comment with the marker id = done")
    r_ = fu("note=SkyyGear 0.1.3 level families\nlevel.material.Iron=15\n")
    check(r_ is not None and BLK13 in r_, "AA2(h): the marker id inside a value does not count")
    r_ = fu("level.material.Iron=15\n#level.material.Stone=1\n")
    check(r_ == "level.material.Iron=15\n" + BLK13 + "\n#level.material.Stone=1\n", "AA2(h): a commented row is not a row (Stone added)")
    # (i) 1500 random files: Properties = old + only the missing family keys, old lines kept in order, the next pass does nothing
    import random as _rnd
    rg = _rnd.Random(13)
    pieces = ["a=1", "level.material.Iron=15", "level.material.stone=2", "level.material.LEATHER_SOFT=7", "#c", "! d", "", "k" + BSL, "  v",
              "x:y", "level.item.Weapon_Sword_Iron=3", LVHa, LVMa, "level.material.Wood 0", "z=" + BSL + BSL, "  ", "w=" + BSL]
    badr = []
    for _n in range(1500):
        lines_ = [rg.choice(pieces) for _ in range(rg.randint(0, 9))]
        t_ = ("\r\n" if rg.random() < 0.3 else "\n").join(lines_) + ("" if rg.random() < 0.3 else "\n")
        r_ = fu(t_)
        if r_ is None:
            badr.append(("none", t_))
            continue
        po_, pn_ = props(t_), props(r_)
        have_ = set(k_[15:].lower() for k_ in po_ if k_.startswith("level.material."))
        wantk = dict(po_)
        for t2, l2 in FAMS:
            if t2.lower() not in have_:
                wantk["level.material." + t2] = str(l2)
        if pn_ != wantk or Cfg.fmUpdate(r_) is not None:
            badr.append(("props", t_))
    check(not badr, "AA2(i): 1500 random files vs java.util.Properties (%d bad, first %r)" % (len(badr), badr[:1]))
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    print("AA2. migrate013 done")

    # ---- AA3. the world-chest decision (GearChestOpen.decide: pure, no engine lookups)
    CD = os.path.join(SCRATCH, "work", "aa013", "chests")
    shutil.rmtree(CD, ignore_errors=True)
    Opened.DIR = None                  # AA3 keeps the memory in RAM (no background file write between cases); AA4 tests the file
    Opened.W.clear()
    Opened.Q.clear()
    Cfg.PART_CHESTS = True
    UP = UUID.fromString("00000000-0000-0000-0000-0000000000a1")       # a player of this server
    UF = UUID.fromString("00000000-0000-0000-0000-0000000000f1")       # a prefab builder's UUID (not a player here)
    Chest.KNOWN.clear()
    Chest.KNOWN.put(UP, JBoolean(True))
    Chest.KNOWN_OK = True
    Chest.LOOT.clear()
    WN = "default"

    def snap(c):
        return [(None if (x is None or x.isEmpty()) else (str(x.getItemId()), int(x.getQuantity()),
                                                            None if x.getMetadata() is None else str(x.getMetadata().toJson())))
                for x in [c.getItemStack(i_) for i_ in range(c.getCapacity())]]

    def counts(c):
        out_ = {}
        for x in [c.getItemStack(i_) for i_ in range(c.getCapacity())]:
            if x is not None and not x.isEmpty():
                out_[str(x.getItemId())] = out_.get(str(x.getItemId()), 0) + int(x.getQuantity())
        return out_

    def docs_of(c, iid):
        return [Data.gearDoc(x.getMetadata()) for x in [c.getItemStack(i_) for i_ in range(c.getCapacity())]
                if x is not None and not x.isEmpty() and str(x.getItemId()) == iid]

    legacy_sword = Data.put(IS("Weapon_Sword_Copper", 1), Data.legacy("Weapon_Sword_Copper"), None)

    def prefab_chest():
        c = SIC(18)
        c.setItemStackForSlot(0, IS("Weapon_Sword_Iron", 1))
        c.setItemStackForSlot(1, IS("Armor_Leather_Light_Chest", 1))
        c.setItemStackForSlot(2, IS("Weapon_Spear_Crude", 3))
        c.setItemStackForSlot(3, IS("Rock_Stone", 10))
        c.setItemStackForSlot(4, legacy_sword)
        c.setItemStackForSlot(5, IS("Weapon_Arrow_Crude", 20))
        return c

    # (a) a prebuilt-structure chest (items in the prefab, no drop list, no placer / a builder's placer): first open tags, never twice
    for nm_, placer_ in (("no placer", None), ("a prefab builder's placer", UF)):
        Opened.W.clear()
        c = prefab_chest()
        before_s, before_c = snap(c), counts(c)
        n = int(Chest.decide(WN, 10, 64, -20, c, placer_, U1, "tester", "open"))
        sw, ar, sp = docs_of(c, "Weapon_Sword_Iron"), docs_of(c, "Armor_Leather_Light_Chest"), docs_of(c, "Weapon_Spear_Crude")
        ok_ = (n == 5 and len(sw) == 1 and len(ar) == 1 and len(sp) == 3 and all(d_ is not None and not bool(Data.identified(d_))
               and str(d_.getString("src").getValue()) == "chest" for d_ in sw + ar + sp))
        check(ok_, "AA3(a) %s: first open -> sword, armor and the 3 spears (split per item) unidentified, src chest (%d written)" % (nm_, n))
        check(counts(c) == before_c, "AA3(a) %s: every item id counted before = after (%s)" % (nm_, counts(c)))
        sn_ = snap(c)
        check(sn_[3] == before_s[3] and sn_[4] == before_s[4] and sn_[5] == before_s[5],
              "AA3(a) %s: the rock, the already documented sword and the ammo stay byte-identical" % nm_)
        check(str(Opened.get(WN, 10, 64, -20)) == "W" and bool(Chest.looting(U1)), "AA3(a) %s: remembered W + the opener's loot window" % nm_)
        c.setItemStackForSlot(10, IS("Weapon_Sword_Thorium", 1))
        s2_ = snap(c)
        n2 = int(Chest.decide(WN, 10, 64, -20, c, placer_, U2, "other", "open"))
        check(n2 == -3 and snap(c) == s2_ and bool(Chest.looting(U2)), "AA3(a) %s: the next open (another player) writes nothing - tagged once, never twice; it still starts a loot window" % nm_)
        n3 = int(Chest.decide(WN, 10, 64, -20, c, placer_, None, "breaker", "break"))
        check(n3 == -3 and snap(c) == s2_, "AA3(a) %s: breaking it later writes nothing either" % nm_)
    # rarity by the Chest odds column: many first opens of a one-sword chest, the rarity histogram follows odds.chest
    Opened.W.clear()
    hist_r = {}
    for k_ in range(3000):
        c = SIC(1)
        c.setItemStackForSlot(0, IS("Weapon_Sword_Iron", 1))
        Chest.decide(WN, k_, 1, 1, c, None, None, "odds", "open")
        r_ = str(Defs.R_ID[int(Data.rarity(Data.gearDoc(c.getItemStack(0).getMetadata())))])
        hist_r[r_] = hist_r.get(r_, 0) + 1
    wch = [float(x) for x in Cfg.O_CHEST]
    tot = sum(wch)
    exp_ = dict((str(Defs.R_ID[i_]), wch[i_] / tot) for i_ in range(len(wch)))
    check(abs(hist_r.get("normal", 0) / 3000.0 - exp_["normal"]) < 0.05 and abs(hist_r.get("unique", 0) / 3000.0 - exp_["unique"]) < 0.05
          and hist_r.get("set", 0) == 0, "AA3(a): rarities follow the Chest odds column (%s vs %s)" % (hist_r, dict((k_, round(v_, 3)) for k_, v_ in exp_.items())))
    # (b) a loot-table chest: the 0.1.2 tag at add (GearTag.tagContainer, unchanged) - the first open then changes nothing
    Opened.W.clear()
    c = SIC(27)
    c.setItemStackForSlot(0, IS("Weapon_Spellbook_Demon", 5))
    c.setItemStackForSlot(1, IS("Weapon_Sword_Iron", 1))
    t0 = int(Tag.tagContainer(c, "droplist Zone1_Encounters_Tier1 in default"))
    s_after_add = snap(c)
    n = int(Chest.decide(WN, 5, 70, 5, c, None, U1, "tester", "open"))
    check(t0 == 6 and n == 0 and snap(c) == s_after_add, "AA3(b): a loot-table chest tagged at add (6 items) - its first open writes nothing")
    # an admin's /stash set chest (a player placed it; GearChestMark remembered it as L): world loot, tagged + loot window, then T
    Opened.W.clear()
    Opened.put(WN, 6, 70, 6, JChar("L"), "drop list X, placed by " + str(UP))
    Chest.LOOT.clear()
    c = prefab_chest()
    n = int(Chest.decide(WN, 6, 70, 6, c, UP, U1, "tester", "open"))
    check(n == 5 and str(Opened.get(WN, 6, 70, 6)) == "T" and bool(Chest.looting(U1)), "AA3(b): a placed loot container (L) counts as world loot: tagged, T, loot window")
    s_ = snap(c)
    Chest.LOOT.clear()
    check(int(Chest.decide(WN, 6, 70, 6, c, UP, U2, "other", "open")) == -3 and snap(c) == s_ and bool(Chest.looting(U2)),
          "AA3(b): T: later opens write nothing, every opener gets the loot window (SkyyExploration luck is per profile)")
    # (c) player storage is never touched: a container a player of this server placed
    Opened.W.clear()
    Chest.LOOT.clear()
    c = prefab_chest()
    before_s = snap(c)
    n = int(Chest.decide(WN, 20, 64, 20, c, UP, U1, "tester", "open"))
    check(n == -4 and snap(c) == before_s and str(Opened.get(WN, 20, 64, 20)) == "P" and not bool(Chest.looting(U1)),
          "AA3(c): placed by a player here -> untouched (undocumented gear included), remembered P, no loot window")
    check(int(Chest.decide(WN, 20, 64, 20, c, UP, U2, "other", "open")) == -4 and int(Chest.decide(WN, 20, 64, 20, c, UP, None, "b", "break")) == -4
          and snap(c) == before_s, "AA3(c): every later open / break: untouched")
    check(int(Chest.decide(WN, 20, 64, 20, c, UF, U1, "tester", "open")) == -4 and snap(c) == before_s,
          "AA3(c): a P position stays player storage while a placer is there")
    n = int(Chest.decide(WN, 20, 64, 20, c, None, U1, "tester", "open"))
    check(n == 5 and str(Opened.get(WN, 20, 64, 20)) == "W", "AA3(c): a P position whose container has no placer any more is decided again (world)")
    # a world container a player later replaced with their own (W + a player's placer now) -> P from then on
    c2 = prefab_chest()
    s2_ = snap(c2)
    check(int(Chest.decide(WN, 20, 64, 20, c2, UP, U1, "tester", "open")) == -4 and snap(c2) == s2_ and str(Opened.get(WN, 20, 64, 20)) == "P",
          "AA3(c): W + now placed by a player -> P, untouched")
    # the player list not read yet: a placed container stays undecided (untouched, not remembered); an unplaced one is decided
    Chest.KNOWN_OK = False
    c = prefab_chest()
    before_s = snap(c)
    check(int(Chest.decide(WN, 30, 64, 30, c, UF, U1, "tester", "open")) == -5 and snap(c) == before_s and str(Opened.get(WN, 30, 64, 30)) == "\x00",
          "AA3(c): placer not judgeable yet (player list unread) -> untouched, not remembered")
    check(int(Chest.decide(WN, 30, 64, 30, c, UP, U1, "tester", "open")) == -4, "AA3(c): ... but a placer seen at PlayerReady (KNOWN) is judged at once")
    check(all(int(Chest.known(UF)) == -1 for _k in range(3)) and not bool(Chest.KNOWN_OK),
          "AA3(c): known() never reads the player list itself while it is unread (review of 0.1.3 finding 5: GearKnownTask only)")
    Chest.KNOWN_OK = True
    # islands: never touched (the naming and the SkyyIslands bridge function)
    c = prefab_chest()
    before_s = snap(c)
    check(int(Chest.decide("skyy-island-u1", 1, 2, 3, c, None, U1, "tester", "open")) == -2 and snap(c) == before_s
          and str(Opened.get("skyy-island-u1", 1, 2, 3)) == "\x00", "AA3(c): a SkyyIslands island world (skyy-island-...) -> untouched, not remembered")

    @JImplements("java.util.function.Function")
    class OwnerFn:
        @JOverride
        def apply(self, o):
            return JString("owner-key") if str(o) == "MyIsle" else None

    bridge.put("island:owner:fn", OwnerFn())
    check(int(Chest.decide("MyIsle", 1, 2, 3, c, None, U1, "tester", "open")) == -2 and snap(c) == before_s
          and int(Chest.decide("hub", 1, 2, 3, prefab_chest(), None, U1, "tester", "open")) == 5,
          "AA3(c): island:owner:fn names an island -> untouched; any other world is decided")
    bridge.remove("island:owner:fn")
    # the memory key = world name + "~" + the world's own UUID: islands are still recognized by their name; a world made again under
    # the same name (another UUID) has its own memory
    check(str(Chest.wname("skyy-island-u1~0f8d1cb0-b011-4620-ab7f-f5901d0c7bff")) == "skyy-island-u1" and str(Chest.wname("default")) == "default",
          "AA3: wname = the world name of a memory key")
    check(int(Chest.decide("skyy-island-u1~0f8d1cb0-b011-4620-ab7f-f5901d0c7bff", 1, 2, 3, prefab_chest(), None, U1, "t", "open")) == -2,
          "AA3: an island key with its world uuid is still an island")
    bridge.put("island:owner:fn", OwnerFn())
    check(int(Chest.decide("MyIsle~0f8d1cb0-b011-4620-ab7f-f5901d0c7bff", 1, 2, 3, prefab_chest(), None, U1, "t", "open")) == -2,
          "AA3: island:owner:fn is asked with the world name, not the key")
    bridge.remove("island:owner:fn")
    ka_, kb_ = "arena~00000000-0000-0000-0000-00000000000a", "arena~00000000-0000-0000-0000-00000000000b"
    check(int(Chest.decide(ka_, 7, 7, 7, prefab_chest(), None, U1, "t", "open")) == 5 and int(Chest.decide(ka_, 7, 7, 7, prefab_chest(), None, U1, "t", "open")) == -3
          and int(Chest.decide(kb_, 7, 7, 7, prefab_chest(), None, U1, "t", "open")) == 5,
          "AA3: the same world name with another UUID (made again) has a fresh memory")
    # (d) review of 0.1.3 finding 2: an L / T record keeps its placer; another player's container there is player storage
    UA = UUID.fromString("00000000-0000-0000-0000-0000000000a2")       # an admin who placed a /stash set chest (a player here)
    Chest.KNOWN.put(UA, JBoolean(True))
    Opened.W.clear()
    Chest.LOOT.clear()
    Opened.put(WN, 70, 64, 70, JChar("L"), UA, "drop list X")
    check(str(Opened.placer(WN, 70, 64, 70)) == str(UA), "AA3(d): an L record keeps its placer")
    c = prefab_chest()
    before_s = snap(c)
    n = int(Chest.decide(WN, 70, 64, 70, c, UP, U1, "tester", "open"))
    check(n == -4 and snap(c) == before_s and str(Opened.get(WN, 70, 64, 70)) == "P" and not bool(Chest.looting(U1)) and Opened.placer(WN, 70, 64, 70) is None,
          "AA3(d): L + now placed by ANOTHER player of this server -> P, untouched, no loot window")
    Opened.put(WN, 71, 64, 71, JChar("L"), UA, "drop list X")
    c = prefab_chest()
    n = int(Chest.decide(WN, 71, 64, 71, c, UA, U1, "tester", "open"))
    check(n == 5 and str(Opened.get(WN, 71, 64, 71)) == "T" and str(Opened.placer(WN, 71, 64, 71)) == str(UA) and bool(Chest.looting(U1)),
          "AA3(d): L + the same placer -> tagged as loot, the T record keeps the placer, loot window")
    Chest.LOOT.clear()
    c2 = prefab_chest()
    s2_ = snap(c2)
    check(int(Chest.decide(WN, 71, 64, 71, c2, UP, U2, "other", "open")) == -4 and snap(c2) == s2_ and str(Opened.get(WN, 71, 64, 71)) == "P"
          and not bool(Chest.looting(U2)), "AA3(d): T + now placed by another player -> P, untouched, no loot window")
    Opened.put(WN, 72, 64, 72, JChar("T"), UA, "x")
    c3 = prefab_chest()
    s3_ = snap(c3)
    check(int(Chest.decide(WN, 72, 64, 72, c3, UF, U2, "other", "open")) == -3 and snap(c3) == s3_ and bool(Chest.looting(U2))
          and str(Opened.get(WN, 72, 64, 72)) == "T", "AA3(d): T + a placer that is not a player here (a builder) -> still the loot spot (window, nothing written)")
    Chest.LOOT.clear()
    Chest.KNOWN_OK = False
    UQ = UUID.fromString("00000000-0000-0000-0000-0000000000b9")       # nobody known, the list unread
    check(int(Chest.decide(WN, 72, 64, 72, prefab_chest(), UQ, U2, "other", "open")) == -5 and str(Opened.get(WN, 72, 64, 72)) == "T" and not bool(Chest.looting(U2)),
          "AA3(d): T + another placer while the player list is unread -> undecided (-5), the record stays")
    Chest.KNOWN_OK = True
    Opened.put(WN, 73, 64, 73, JChar("L"), "no placer known")
    check(int(Chest.decide(WN, 73, 64, 73, prefab_chest(), UP, U1, "tester", "open")) == 5 and str(Opened.get(WN, 73, 64, 73)) == "T",
          "AA3(d): an L record without a placer (nothing to compare) -> the loot container, as before")
    Chest.LOOT.clear()
    # (e) review of 0.1.3 finding 1: the loot window has a hard cap after its start; refreshes never extend it past start + CAP_MS
    check(int(Chest.CAP_MS) == 15000 and int(Chest.GRACE_MS) == 3000, "AA3(e): the loot window: 3 s grace, 15 s hard cap")
    Opened.W.clear()
    Chest.LOOT.clear()
    Chest.LOOT_AT.clear()
    Chest.decide(WN, 80, 64, 80, prefab_chest(), None, U1, "tester", "open")
    now_ = int(time.time() * 1000)
    check(bool(Chest.looting(U1)) and abs(int(Chest.LOOT_AT.get(U1)) - now_) < 2000, "AA3(e): a first open starts the window (its start is kept)")
    Chest.LOOT_AT.put(U1, JLong(now_ - 14000))
    Chest.LOOT.put(U1, JLong(now_ - 1))
    Chest.lootMore(U1)
    u_ = int(Chest.LOOT.get(U1))
    check(bool(Chest.looting(U1)) and u_ <= now_ + 1000 + 5, "AA3(e): a refresh 14 s after the start extends it only up to start + 15 s (%d ms left)" % (u_ - now_))
    Chest.LOOT_AT.put(U1, JLong(now_ - 16000))
    Chest.LOOT.put(U1, JLong(now_ - 1))
    Chest.lootMore(U1)
    check(not bool(Chest.looting(U1)) and not Chest.LOOT_AT.containsKey(U1), "AA3(e): 16 s after the start a refresh (GearTick's sighting) extends nothing")
    check(int(Chest.decide(WN, 80, 64, 80, prefab_chest(), None, U1, "tester", "window")) == -3 and not bool(Chest.looting(U1)),
          "AA3(e): the window task on the decided chest after the cap opens nothing (a chest kept open does not keep the window alive)")
    check(int(Chest.decide(WN, 80, 64, 80, prefab_chest(), None, U1, "tester", "open")) == -3 and bool(Chest.looting(U1)),
          "AA3(e): a new open (UseBlockEvent$Pre) starts a new window")
    Chest.LOOT.clear()
    Chest.LOOT_AT.clear()
    Chest.lootMore(U2)
    check(not bool(Chest.looting(U2)), "AA3(e): a refresh without a start opens nothing")
    check(int(Chest.decide(WN, 81, 64, 81, prefab_chest(), None, U2, "other", "window")) == 5 and bool(Chest.looting(U2)),
          "AA3(e): a container the window task decides just now starts the window (its first sighting)")
    Chest.LOOT.clear()
    Chest.LOOT_AT.clear()
    # part.chests off: nothing
    Cfg.PART_CHESTS = False
    c = prefab_chest()
    before_s = snap(c)
    check(int(Chest.decide(WN, 40, 1, 40, c, None, U1, "t", "open")) == -9 and snap(c) == before_s and str(Opened.get(WN, 40, 1, 40)) == "\x00",
          "AA3: part.chests off -> nothing (not remembered either)")
    Cfg.PART_CHESTS = True
    print("AA3. world-chest decision done")

    # ---- AA4. the per-world memory file (decisions of one world appended by the scheduler, read once per world after a restart)
    Opened.Q.clear()
    Opened.W.clear()
    Opened.DIR = Paths.get(CD)
    c = prefab_chest()
    Chest.decide(WN, 10, 64, -20, c, None, U1, "tester", "open")
    Chest.decide(WN, 20, 64, 20, prefab_chest(), UP, U1, "tester", "open")
    Opened.put(WN, 6, 70, 6, JChar("L"), "drop list X")
    Chest.decide(WN, 6, 70, 6, prefab_chest(), UP, U1, "tester", "open")
    Chest.decide(WN, 20, 64, 20, prefab_chest(), None, U1, "tester", "open")      # no placer any more -> decided again (W)
    Opened.flush()
    fdef = os.path.join(CD, "default.txt")
    txt_ = open(fdef, encoding="utf-8").read() if os.path.isfile(fdef) else ""
    lns = [l_ for l_ in txt_.split("\n") if l_.strip()]
    check(len(lns) == 6 and lns[0].startswith("# SkyyGear - the containers of world default ") and txt_.count("# SkyyGear - the containers") == 1
          and lns[1].startswith("10 64 -20 W ") and lns[2].startswith("20 64 20 P ") and lns[3].startswith("6 70 6 L ") and lns[4].startswith("6 70 6 T ")
          and lns[5].startswith("20 64 20 W "), "AA4: chests/default.txt: the header once + one line per decision in order: %s" % [l_[:12] for l_ in lns])
    Opened.put(WN, 1, 1, 1, JChar("W"), "x")
    Opened.flush()
    check(open(fdef, encoding="utf-8").read().count("# SkyyGear - the containers") == 1, "AA4: appending never repeats the header")
    Opened.W.clear()
    check(str(Opened.get(WN, 20, 64, 20)) == "W" and str(Opened.get(WN, 6, 70, 6)) == "T" and str(Opened.get(WN, 10, 64, -20)) == "W",
          "AA4: read back after a restart (the last line of a position wins)")
    c.setItemStackForSlot(11, IS("Weapon_Sword_Thorium", 1))
    s_ = snap(c)
    check(int(Chest.decide(WN, 10, 64, -20, c, None, U2, "other", "open")) == -3 and snap(c) == s_, "AA4: after a restart the chest is still never tagged twice")
    check(str(Opened.safe("default")) == "default" and str(Opened.safe("a b/c")).startswith("a_b_c-") and str(Opened.safe("..x")).startswith("..x-")
          and str(Opened.safe("default~0f8d1cb0-b011-4620-ab7f-f5901d0c7bff")).startswith("default_0f8d1cb0-b011-4620-ab7f-f5901d0c7bff-"),
          "AA4: file names: plain names kept, others get a hash suffix (a world key: <name>_<uuid>-<hash>)")
    open(os.path.join(CD, str(Opened.safe("w2")) + ".txt"), "w", encoding="utf-8").write("# x\n1 2 3 Q\nbad line\n4 5\n7 8 9\n-5 300 -7 P extra words\n")
    check(str(Opened.get("w2", 1, 2, 3)) == "W" and str(Opened.get("w2", 7, 8, 9)) == "W" and str(Opened.get("w2", -5, 300, -7)) == "P"
          and str(Opened.get("w2", 4, 5, 0)) == "\x00", "AA4: an unknown state = W, a line without one = W, bad lines skipped, negative x / z")
    check(int(Opened.pack(-30000000, 319, 30000000)) != int(Opened.pack(30000000, 319, -30000000)), "AA4: the key keeps the sign of x and z")
    # review of 0.1.3: L / T lines carry their placer (finding 2); X forgets + regenerated chunks (3); temporary worlds + world removal
    # (4); the prefetch task (5)
    Opened.Q.clear()
    Opened.W.clear()
    WK2 = "rv~00000000-0000-0000-0000-0000000000c1"
    Opened.put(WK2, 5, 64, 5, JChar("L"), UA, "drop list X")
    Chest.decide(WK2, 5, 64, 5, prefab_chest(), UA, U1, "tester", "open")
    Opened.put(WK2, 40, 64, 40, JChar("W"), "w")
    Opened.put(WK2, 33, 70, 63, JChar("P"), "p")
    Opened.put(WK2, 64, 64, 40, JChar("W"), "w2")
    Opened.put(WK2, -1, 64, -1, JChar("W"), "neg")
    Opened.flush()
    f2 = os.path.join(CD, str(Opened.safe(WK2)) + ".txt")
    l2 = [l_ for l_ in (open(f2, encoding="utf-8").read() if os.path.isfile(f2) else "").split("\n") if l_.strip() and not l_.startswith("#")]
    check(len(l2) == 6 and l2[0].split()[3] == "L" and l2[0].split()[5] == "placer=" + str(UA) and l2[1].split()[3] == "T"
          and l2[1].split()[5] == "placer=" + str(UA) and all("placer=" not in l_ for l_ in l2[2:]),
          "AA4: L / T lines carry placer=<uuid> right after the time, the other lines do not: %s" % [l_[:60] for l_ in l2[:2]])
    Opened.W.clear()
    Opened.PW.clear()
    Opened.CH.clear()
    check(str(Opened.get(WK2, 5, 64, 5)) == "T" and str(Opened.placer(WK2, 5, 64, 5)) == str(UA) and Opened.placer(WK2, 40, 64, 40) is None,
          "AA4: after a restart the T record still knows its placer")
    n_ = int(Opened.regen(WK2, 1, 1))
    check(n_ == 2 and str(Opened.get(WK2, 40, 64, 40)) == "\x00" and str(Opened.get(WK2, 33, 70, 63)) == "\x00" and str(Opened.get(WK2, 64, 64, 40)) == "W"
          and str(Opened.get(WK2, -1, 64, -1)) == "W" and str(Opened.get(WK2, 5, 64, 5)) == "T",
          "AA4: a regenerated chunk (1, 1) forgets its 2 records (W and P), keeps every other one")
    check(int(Opened.regen(WK2, 1, 1)) == 0 and int(Opened.regen(WK2, 9, 9)) == 0, "AA4: a chunk without records (or done already) does nothing")
    check(int(Opened.regen(WK2, -1, -1)) == 1 and str(Opened.get(WK2, -1, 64, -1)) == "\x00", "AA4: negative chunk coordinates")
    Opened.flush()
    Opened.W.clear()
    Opened.PW.clear()
    Opened.CH.clear()
    check(str(Opened.get(WK2, 40, 64, 40)) == "\x00" and str(Opened.get(WK2, 33, 70, 63)) == "\x00" and str(Opened.get(WK2, 64, 64, 40)) == "W"
          and str(Opened.get(WK2, 5, 64, 5)) == "T", "AA4: the X lines keep them forgotten after a restart")
    Opened.W.clear()
    Opened.PW.clear()
    Opened.CH.clear()
    check(int(Opened.regen(WK2, 2, 1)) == 1 and str(Opened.get(WK2, 64, 64, 40)) == "\x00", "AA4: regen reads a world's file first when its memory is not loaded yet")
    NK = "nofile~00000000-0000-0000-0000-0000000000c2"
    check(int(Opened.regen(NK, 0, 0)) == 0 and not Opened.W.containsKey(NK), "AA4: regen in a world without a memory file loads nothing")
    check(all(int(Opened.ux(Opened.pack(x_, y_, z_))) == x_ and int(Opened.uy(Opened.pack(x_, y_, z_))) == y_ and int(Opened.uz(Opened.pack(x_, y_, z_))) == z_
              for x_, y_, z_ in ((0, 0, 0), (-1, 5, -1), (30000000, 319, -30000000), (-30000000, 4095, 30000000), (31, 64, 32))),
          "AA4: pack / unpack round trip")
    check(int(Opened.ck(31, 31)) == int(Opened.ckc(0, 0)) and int(Opened.ck(32, -1)) == int(Opened.ckc(1, -1)) and int(Opened.ck(-33, 64)) == int(Opened.ckc(-2, 2)),
          "AA4: block -> chunk = ChunkUtil.chunkCoordinate (32 blocks)")
    TK = "inst~00000000-0000-0000-0000-0000000000c3"
    Opened.TEMP.put(TK, JBoolean(True))
    check(int(Chest.decide(TK, 1, 64, 1, prefab_chest(), None, U1, "t", "open")) == 5 and int(Chest.decide(TK, 1, 64, 1, prefab_chest(), None, U1, "t", "open")) == -3,
          "AA4: a temporary world (Hytale deletes it) still decides each container once (memory)")
    Opened.flush()
    check(not os.path.exists(os.path.join(CD, str(Opened.safe(TK)) + ".txt")), "AA4: ... but never writes a chests/ file")
    WK3 = "gone~00000000-0000-0000-0000-0000000000c4"
    Opened.put(WK3, 2, 64, 2, JChar("W"), "w")
    Opened.evict(WK3)
    Opened.evict(TK)
    check(not Opened.W.containsKey(WK3) and not Opened.PW.containsKey(WK3) and not Opened.CH.containsKey(WK3) and not Opened.W.containsKey(TK)
          and not Opened.TEMP.containsKey(TK) and os.path.isfile(os.path.join(CD, str(Opened.safe(WK3)) + ".txt")),
          "AA4: world removal (evict) writes the queued lines and drops the world's maps (a temporary world too)")
    check(str(Opened.get(WK3, 2, 64, 2)) == "W", "AA4: a removed world that comes back reads its file again")
    Opened.W.clear()
    Opened.PW.clear()
    Opened.CH.clear()
    Opened(JString(WK3)).run()
    check(Opened.W.containsKey(WK3) and Opened.PW.containsKey(WK3) and str(Opened.get(WK3, 2, 64, 2)) == "W",
          "AA4: PlayerReady's prefetch task (GearOpened(key).run, scheduler) loads the world's memory")
    Opened.DIR = None
    print("AA4. memory file done")

    # ---- AA5. SkyyExploration 0.2.2's chest luck: one extra drop-list roll into the OPENER's inventory (read from its build script),
    # covered by the loot window whatever order the two mods run in
    exs = open(os.path.join(ROOT, "SkyyExploration", "build_skyyexploration_0.2.2.py"), encoding="utf-8").read()
    lu_ = exs[exs.index("public static void luck("):exs.index("public static void scav(")]
    check("getRandomItemDrops(dl)" in lu_ and "addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), is)" in lu_
          and "super(@UBP@.class)" in exs, "AA5: SkyyExploration 0.2.2 gives the luck roll into the opener's inventory (drop at the feet when full), from UseBlockEvent$Post")
    Inv0 = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    inv_ok = True
    try:
        ti_ = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get("com.hypixel.hytale.server.core.inventory.Inventory"))
        _ICn = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
        _SICn = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
        for fn_, cap_ in (("h", 9), ("s", 36), ("b", 9), ("a", 4), ("u", 4), ("t", 4)):
            ti_.addField(JClass("javassist.CtField").make("public %s %s = new %s((short) %d);" % (_ICn, fn_, _SICn, cap_), ti_))
        for g_, fn_ in (("getHotbar", "h"), ("getStorage", "s"), ("getBackpack", "b"), ("getArmor", "a"), ("getUtility", "u"), ("getTools", "t")):
            ti_.addMethod(JClass("javassist.CtNewMethod").make("public %s %s() { return this.%s; }" % (_ICn, g_, fn_), ti_))
        TInv = ti_.toClass(Inv0.class_)
        Inv = lambda: TInv.getDeclaredConstructor().newInstance()

        def mk_player(u_, nm_):
            pr_ = unsafe.allocateInstance(PRc.class_)
            for fn_, v_ in (("uuid", u_), ("username", JString(nm_))):
                f_ = PRc.class_.getDeclaredField(fn_)
                f_.setAccessible(True)
                f_.set(pr_, v_)
            return pr_
        PR1, PR2 = mk_player(U1, "tester"), mk_player(U2, "other")
        Inv()
    except Exception as e_:
        inv_ok = False
        check(False, "AA5: a bare Inventory / PlayerRef could not be made: %s" % e_)
    if inv_ok:
        def luck_give(inv_, items):
            """what SkyyExploration does: addOrDropItemStack -> ItemContainer.addItemStack on getCombinedStorageHotbarBackpack =
            storage first (the test inventory's storage has room, so the storage container takes it)"""
            for iid, q in items:
                inv_.getStorage().addItemStack(IS(iid, q))

        def inv_docs(inv_, iid):
            out_ = []
            for c_ in (inv_.getHotbar(), inv_.getStorage(), inv_.getBackpack()):
                if c_ is None:
                    continue
                for i_ in range(c_.getCapacity()):
                    x = c_.getItemStack(i_)
                    if x is not None and not x.isEmpty() and str(x.getItemId()) == iid:
                        out_.append((int(x.getQuantity()), Data.gearDoc(x.getMetadata())))
            return out_

        def all_chest(ds):
            return all(d_ is not None and not bool(Data.identified(d_)) and str(d_.getString("src").getValue()) == "chest" for _q, d_ in ds)

        LUCK = [("Weapon_Sword_Iron", 1), ("Weapon_Spear_Crude", 3), ("Food_Bread", 2)]
        # order 1: SkyyGear's UseBlockEvent$Pre decided first (the window starts), then the luck give, then the coalesced stamp scan
        Opened.W.clear()
        Chest.LOOT.clear()
        inv1 = Inv()
        Chest.decide(WN, 50, 64, 50, prefab_chest(), None, U1, "tester", "open")
        luck_give(inv1, LUCK)
        cnt_ = Stamp.scan(PR1, inv1)
        sw_, sp_ = inv_docs(inv1, "Weapon_Sword_Iron"), inv_docs(inv1, "Weapon_Spear_Crude")
        check(all_chest(sw_) and len(sw_) == 1 and all_chest(sp_) and sorted(q for q, _d in sp_) == [1, 1, 1] and len(inv_docs(inv1, "Food_Bread")) == 1,
              "AA5 order 1: decide -> luck give -> scan: the sword and each spear (split per item) unidentified with src chest; bread untouched")
        # order 2: SkyyGear's own scan ran before the give (nothing to do), the give, the next scan
        Chest.LOOT.clear()
        inv2 = Inv()
        Chest.decide(WN, 50, 64, 50, prefab_chest(), None, U1, "tester", "open")      # a later open of the decided chest: loot window too
        Stamp.scan(PR1, inv2)
        luck_give(inv2, LUCK)
        Stamp.scan(PR1, inv2)
        check(all_chest(inv_docs(inv2, "Weapon_Sword_Iron")) and all_chest(inv_docs(inv2, "Weapon_Spear_Crude")),
              "AA5 order 2: scan first, then the give, then the scan: still chest loot (the window is a state, not an event order)")
        # order 3: the scan only runs after the window closed but inside the grace time
        Chest.LOOT.clear()
        inv3 = Inv()
        Chest.decide(WN, 50, 64, 50, prefab_chest(), None, U1, "tester", "open")
        luck_give(inv3, LUCK)
        Chest.LOOT.put(U1, JLong(int(time.time() * 1000) + 300))      # 0.3 s of grace left
        Stamp.scan(PR1, inv3)
        check(all_chest(inv_docs(inv3, "Weapon_Sword_Iron")), "AA5 order 3: a late scan inside the grace time: chest loot")
        # the window expired -> the old legacy Normal stamp (and the window is dropped)
        inv4 = Inv()
        luck_give(inv4, [("Weapon_Sword_Iron", 1)])
        Chest.LOOT.put(U1, JLong(int(time.time() * 1000) - 1))
        Stamp.scan(PR1, inv4)
        d4 = inv_docs(inv4, "Weapon_Sword_Iron")
        check(len(d4) == 1 and bool(Data.identified(d4[0][1])) and str(d4[0][1].getString("src").getValue()) == "legacy" and not Chest.LOOT.containsKey(U1),
              "AA5: after the grace time the stamp is the legacy Normal one again (no window left)")
        # the full-inventory overflow (ItemUtils.dropItem -> DropItemEvent$Drop -> GearThrowSys): lootStack during the window
        Chest.loot(U1)
        ds_ = Chest.lootStack(IS("Armor_Iron_Head", 1), U1, "(dropped while a world chest was open)")
        dd_ = Data.gearDoc(ds_.getMetadata())
        check(dd_ is not None and not bool(Data.identified(dd_)) and str(dd_.getString("src").getValue()) == "chest",
              "AA5: the overflow drop (GearThrowSys during the window) is chest loot too")
        ls_ = Chest.lootStack(legacy_sword, U1, "x")
        check(not bool(Chest.lootable(legacy_sword)) and str(ls_.getMetadata().toJson()) == str(legacy_sword.getMetadata().toJson()),
              "AA5: a documented stack is never touched by the loot window")
        # ---- AA6. no leak: another player (no window) and a player-storage open give the legacy stamp; the loot never reaches storage
        inv5 = Inv()
        luck_give(inv5, [("Weapon_Sword_Iron", 1)])
        Stamp.scan(PR2, inv5)
        d5 = inv_docs(inv5, "Weapon_Sword_Iron")
        check(len(d5) == 1 and bool(Data.identified(d5[0][1])) and str(d5[0][1].getString("src").getValue()) == "legacy",
              "AA6: a player without a loot window: undocumented gear in the inventory is stamped Normal as before")
        Chest.LOOT.clear()
        Opened.W.clear()
        Chest.decide(WN, 60, 64, 60, prefab_chest(), UP, U2, "other", "open")      # their own chest
        inv6 = Inv()
        luck_give(inv6, [("Weapon_Sword_Iron", 1)])
        Stamp.scan(PR2, inv6)
        check(not bool(Chest.looting(U2)) and bool(Data.identified(inv_docs(inv6, "Weapon_Sword_Iron")[0][1])),
              "AA6: opening their own (player-placed) chest starts no loot window")
        # a big stack in a nearly full inventory is tagged whole (the 5-slot floor), counted before = after
        inv7 = Inv()
        st7 = inv7.getStorage()
        for i_ in range(st7.getCapacity()):
            st7.setItemStackForSlot(i_, IS("Rock_Stone", 1))
        for c_ in (inv7.getHotbar(), inv7.getBackpack()):
            if c_ is not None:
                for i_ in range(c_.getCapacity()):
                    c_.setItemStackForSlot(i_, IS("Rock_Stone", 1))
        inv7.getHotbar().setItemStackForSlot(0, IS("Weapon_Spear_Crude", 4))
        Chest.loot(U1)
        Stamp.scan(PR1, inv7)
        d7 = inv_docs(inv7, "Weapon_Spear_Crude")
        check(len(d7) == 1 and d7[0][0] == 4 and all_chest(d7), "AA6: no free slots -> the stack stays one stack with one unidentified document (4 items kept)")
        Chest.LOOT.clear()
    print("AA5/AA6. SkyyExploration extra items + no leak done")

    # ---- AA7. the engine side (bytecode): the only ways into the decision, block containers only, never ContainerWindow
    dec_callers, proc_callers = set(), set()
    for cn_ in [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class")]:
        cc_ = pool.get(cn_)
        for mm in list(cc_.getDeclaredMethods()):
            bo_ = BOS()
            IP(PS(bo_)).print_(mm)
            t_ = str(bo_.toString())
            if "GearChestOpen.decide(" in t_:
                dec_callers.add(cn_[len(PKG):] + "." + str(mm.getName()))
            if "GearChestOpen.process(" in t_:
                proc_callers.add(cn_[len(PKG):] + "." + str(mm.getName()))
    check(dec_callers == set(["GearChestOpen.process"]), "AA7: only GearChestOpen.process calls decide: %s" % sorted(dec_callers))
    check(proc_callers == set(["GearChestOpenSys.handle", "GearChestBreakSys.handle", "GearChestTask.run"]),
          "AA7: process is reached only from UseBlockEvent$Pre, BreakBlockEvent and the window task: %s" % sorted(proc_callers))
    pr_c = mcode("GearChestOpen", "process")
    check("BlockModule.getBlockEntity(" in pr_c and "GearChestOpen.icbOf(" in pr_c and "ItemContainerBlock.getItemContainer(" in pr_c
          and "GearChestOpen.origin(" in pr_c and "GearChestOpen.placedBy(" in pr_c and "GearChestOpen.wkey(" in pr_c
          and "WorldConfig.getUuid(" in mcode("GearChestOpen", "wkey"), "AA7: process: block entity -> ItemContainerBlock (filler origin as fallback) -> its placer")
    check("ItemContainerBlock.getComponentType(" in mcode("GearChestOpen", "icbOf") and "PlacedByInteractionComponent.getWhoPlacedUuid(" in mcode("GearChestOpen", "placedBy"),
          "AA7: icbOf / placedBy read the engine components")
    sc_ = mcode("GearChestOpen", "second")

    def instanceof_targets(cls_, meth_):
        """the classes of every instanceof in a method (the printer leaves them out): opcode 0xC1 + its constant-pool class"""
        out_ = []
        for mm in list(pool.get(PKG + cls_).getDeclaredMethods()):
            if str(mm.getName()) != meth_:
                continue
            ci_ = mm.getMethodInfo().getCodeAttribute().iterator()
            cp_ = mm.getMethodInfo().getConstPool()
            while ci_.hasNext():
                pos_ = ci_.next()
                if (ci_.byteAt(pos_) & 0xFF) == 0xC1:
                    out_.append(str(cp_.getClassInfo(ci_.u16bitAt(pos_ + 1))))
        return out_

    check(instanceof_targets("GearChestOpen", "second") == ["com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow"]
          and "WindowManager.getWindows(" in sc_ and "GearChestTask.<init>(" in sc_,
          "AA7: the window backup only looks at ContainerBlockWindow instances (%s)" % instanceof_targets("GearChestOpen", "second"))
    CW_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    BW_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow")
    CBW_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow")
    check(not BW_.class_.isAssignableFrom(CW_.class_) and not CBW_.class_.isAssignableFrom(CW_.class_) and BW_.class_.isAssignableFrom(CBW_.class_),
          "AA7: ContainerWindow (SkyyVault / SkyyEssentials trade / SkyySacks windows) is no BlockWindow")
    for mod_, ver_ in (("SkyyVault", "0.1.5"), ("SkyyEssentials", "0.1.6"), ("SkyySacks", "0.7.9"), ("SkyyAuctions", "0.1.2"), ("SkyyAccessories", "0.5.1")):
        pth_ = os.path.join(ROOT, mod_, "build_%s_%s.py" % (mod_.lower(), ver_))
        if os.path.isfile(pth_):
            src_ = open(pth_, encoding="utf-8", errors="replace").read()
            check("ContainerBlockWindow" not in src_ and "ItemContainerBlock" not in src_ and "PlacedByInteraction" not in src_,
                  "AA7: %s %s keeps its storage in no block container" % (mod_, ver_))
    oh_ = mcode("GearChestOpenSys", "handle")
    bh_ = mcode("GearChestBreakSys", "handle")
    check("UseBlockEvent$Pre.isCancelled(" in oh_ and "UseBlockEvent.getTargetBlock(" in oh_ and "GearChestOpen.process(" in oh_,
          "AA7: GearChestOpenSys: UseBlockEvent$Pre, skipped when cancelled")
    check(("CancellableEcsEvent.isCancelled(" in bh_ or "BreakBlockEvent.isCancelled(" in bh_) and "BreakBlockEvent.getTargetBlock(" in bh_
          and "aconst_null" in bh_, "AA7: GearChestBreakSys: BreakBlockEvent (skipped when cancelled), no loot window (who = null)")
    for cls_, evc in (("GearChestOpenSys", "UseBlockEvent$Pre"), ("GearChestBreakSys", "BreakBlockEvent")):
        k0 = pool.get(PKG + cls_).getDeclaredConstructors()[0]
        ca_ = k0.getMethodInfo().getCodeAttribute()
        it_ = ca_.iterator()
        ops_ = []
        while it_.hasNext():
            ops_.append(str(IP.instructionString(it_, it_.next(), k0.getMethodInfo().getConstPool())))
        check(any(evc in o_ for o_ in ops_), "AA7: %s listens to %s" % (cls_, evc))
    cm_ = mcode("GearChestMark", "onEntityAdded")
    check(cm_.find("GearTag.chestMark(") >= 0 and cm_.find("GearChestOpen.lootMark(") > cm_.find("GearTag.chestMark("),
          "AA7: GearChestMark: the 0.1.2 chestMark unchanged, then lootMark")
    sc2 = mcode("GearStamp", "scan")
    th_ = mcode("GearThrowSys", "handle")
    check("GearChestOpen.looting(" in sc2 and "GearChestOpen.lootSlot(" in sc2 and "GearChestOpen.looting(" in th_ and "GearChestOpen.lootStack(" in th_,
          "AA7: the passive stamp and the drop stamp ask the loot window")
    check("GearCfg.MAT_WORDS" in mcode("GearLevel", "level"), "AA7: GearLevel.level reads MAT_WORDS")
    # review of 0.1.3
    check("GearChestOpen.refreshKnown(" not in mcode("GearChestOpen", "known"), "AA7: known() never reads the player list (only GearKnownTask, finding 5)")
    check("GearChestOpen.lootMore(" in sc_ and "GearChestOpen.loot(" not in sc_, "AA7: the window backup only extends a started window (lootMore, finding 1)")
    dc_ = mcode("GearChestOpen", "decide")
    check("GearChestOpen.lootMore(" in dc_ and "GearChestOpen.loot(" in dc_ and "GearOpened.placer(" in dc_,
          "AA7: decide starts (open / new) or extends (window task) the window and reads the L / T placer")
    check(0 <= cm_.find("GearChestOpen.spawned(") < cm_.find("GearTag.chestMark(") and "AddReason.SPAWN" in cm_,
          "AA7: GearChestMark: a container added with SPAWN is checked first (spawned), then the 0.1.2 chestMark + lootMark")
    sp_ = mcode("GearChestOpen", "spawned")
    check("PlacedByInteractionComponent.getWhoPlacedUuid(" in sp_ and "GearOpened.put(" in sp_ and "GearChestOpen.posOf(" in sp_,
          "AA7: spawned: no placer + a W / T / L record -> X (finding 3a)")
    cr_ = mcode("GearChunkRegen", "onEntityAdded")
    check("AddReason.SPAWN" in cr_ and "ChunkFlag.NEWLY_GENERATED" in cr_ and "WorldChunk.is(" in cr_ and "GearOpened.regen(" in cr_ and "WorldChunk.getComponentType(" in cr_,
          "AA7: GearChunkRegen = Hytale's TriggerVolumeChunkRegenSystem test (SPAWN + NEWLY_GENERATED) -> GearOpened.regen (finding 3b)")
    wb_ = mcode("GearWorldBye", "accept")
    check("isCancelled(" in wb_ and "GearOpened.evict(" in wb_ and "GearChestOpen.wkey(" in wb_, "AA7: GearWorldBye: RemoveWorldEvent (not cancelled) -> evict (finding 4)")
    wk_ = mcode("GearChestOpen", "wkey")
    check("WorldConfig.isDeleteOnRemove(" in wk_ and "WorldConfig.isDeleteOnUniverseStart(" in wk_ and "GearOpened.TEMP" in wk_,
          "AA7: wkey notes the worlds Hytale deletes (memory only)")
    # ---- AA8. setup / tick / ready wiring
    su3 = mcode("SkyyGearPlugin", "setup")
    o3 = [su3.find("GearCfg.migrate012("), su3.find("GearCfg.migrate013("), su3.find("GearCfg.load("), su3.find("GearOpened.DIR"),
          su3.find("GearKnownTask.later("), su3.find("CfgPub.start(")]
    check(all(x >= 0 for x in o3) and o3 == sorted(o3), "AA8: setup(): migrate012 -> migrate013 -> load -> GearOpened.DIR -> GearKnownTask -> CfgPub.start (%s)" % o3)
    check(su3.count("registerSystem(") >= 6 and "GearChestOpenSys.<init>" in su3 and "GearChestBreakSys.<init>" in su3, "AA8: both chest systems registered")
    check("GearChestOpen.statusText(" in su3, "AA8: the ready line names the world-chest rule")
    check("GearOpened.flush(" in mcode("SkyyGearPlugin", "shutdown"), "AA8: shutdown writes the pending memory lines")
    check("GearChestOpen.second(" in mcode("GearTick", "tick"), "AA8: GearTick runs the window backup each second")
    check("GearChestOpen.seen(" in mcode("GearReady", "accept"), "AA8: PlayerReady adds the player to the players of this server")
    check("GearOpened.prefetch(" in mcode("GearReady", "accept"), "AA8: PlayerReady prefetches the world's container memory on the scheduler")
    check("GearChunkRegen.<init>" in su3 and "getChunkStoreRegistry(" in su3 and "GearWorldBye.<init>" in su3 and "RemoveWorldEvent" in su3,
          "AA8: setup registers GearChunkRegen (chunk store) and GearWorldBye (RemoveWorldEvent)")
    kt_ = mcode("GearKnownTask", "run")
    check("GearChestOpen.refreshKnown(" in kt_ and "GearKnownTask.later(" in kt_, "AA8: GearKnownTask reads the player list and reschedules itself")
    print("AA7/AA8. engine side + wiring done")

    # ---- AA9. class byte-compare 0.1.2 -> 0.1.3 (Z10's machinery): every difference must be one of the listed new parts
    jar012 = os.path.join(HERE, "SkyyGear-0.1.2.jar")
    # (0.2 harness: this stays the historical 0.1.2 -> 0.1.3 compare of the two shipped jars, like Z10; AB9 compares 0.1.3 -> 0.2)
    jar013 = os.path.join(HERE, "SkyyGear-0.1.3.jar")
    if os.path.isfile(jar012) and os.path.isfile(jar013):
        pa3 = Pool(False)
        pa3.appendClassPath(jar012)
        pa3.appendClassPath(B.SERVER_JAR)
        pa3.appendSystemPath()
        pb3 = Pool(False)
        pb3.appendClassPath(jar013)
        pb3.appendClassPath(B.SERVER_JAR)
        pb3.appendSystemPath()
        n12 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar012).namelist() if n_.endswith(".class"))
        n13 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar013).namelist() if n_.endswith(".class"))
        add3 = sorted(c_[len(PKG):] for c_ in set(n13) - set(n12))
        gone3 = sorted(set(n12) - set(n13))
        diffs3 = {}
        for cn_ in sorted(set(n12) & set(n13)):
            ma_, mb_ = cls_members(pa3, cn_), cls_members(pb3, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs3[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        EXPECT3 = {
            # config kit (tools/skyycfg.py, regenerated from the rows): two help texts + VERSION 0.1.2 -> 0.1.3 (CfgRows), the export
            # header inlines the VERSION constant (CfgFn.opExport)
            "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # the family arrays + marker, MAT_WORDS (loader), the default text, matText, migrate013 + its text step + log line
            "GearCfg": ["~<clinit>", "+f FAM_L", "+f FAM_T", "+f FM_MARK", "+f FM_MARK_ID", "+f FM_WHO", "+f MAT_WORDS",
                        "~m apply(Ljava/util/Properties;Z)V", "~m defaultsText()Ljava/lang/String;", "+m fmLog(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                        "+m fmUpdate(Ljava/lang/String;)[Ljava/lang/Object;", "~m matText()Ljava/lang/String;", "+m matWords(Ljava/util/HashMap;)I",
                        "+m migrate013()Ljava/lang/String;"],
            # GearChestMark: + lootMark after the unchanged chestMark (its fallback GearChestMarkU inherits it)
            "GearChestMark": ["~m onEntityAdded(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/AddReason;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"],
            # the multi-word lookup
            "GearLevel": ["~m level(Ljava/lang/String;Lorg/bson/BsonDocument;)I"],
            # PlayerReady: GearChestOpen.seen
            "GearReady": ["~m accept(Ljava/lang/Object;)V"],
            # the loot window in the passive stamp
            "GearStamp": ["~m scan(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/Inventory;)[I"],
            # the loot window in the drop stamp
            "GearThrowSys": ["~m handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"],
            # GearChestOpen.second each second
            "GearTick": ["~m tick(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V"],
            # migrate013, GearOpened.DIR, GearKnownTask, the two systems, the ready line; shutdown flushes GearOpened
            "SkyyGearPlugin": ["~m setup()V", "~m shutdown()V"]}
        check(add3 == ["GearChestBreakSys", "GearChestOpen", "GearChestOpenSys", "GearChestTask", "GearChunkRegen", "GearKnownTask", "GearOpened",
                       "GearWorldBye"] and not gone3,
              "AA9: new classes = the 8 world-chest classes, none removed: %s / %s" % (add3, gone3))
        extra3 = dict((c_, [m_ for m_ in ms_ if m_ not in EXPECT3.get(c_, [])]) for c_, ms_ in diffs3.items())
        extra3 = dict((c_, ms_) for c_, ms_ in extra3.items() if ms_)
        miss3 = dict((c_, [m_ for m_ in ms_ if m_ not in diffs3.get(c_, [])]) for c_, ms_ in EXPECT3.items())
        miss3 = dict((c_, ms_) for c_, ms_ in miss3.items() if ms_)
        check(not extra3, "AA9: no difference outside the listed new parts: %s" % extra3)
        check(not miss3, "AA9: every listed part really differs (the list is exact): %s" % miss3)
        print("AA9. 0.1.2 -> 0.1.3 class compare: %d classes identical, %d with new parts, %d new" % (len(set(n12) & set(n13)) - len(diffs3), len(diffs3), len(add3)))
        for c_ in sorted(diffs3):
            print("     %-16s %s" % (c_, ", ".join(re.sub(r"\(.*", "", m_) for m_ in diffs3[c_])))
        ea3 = [n_ for n_ in zipfile.ZipFile(jar012).namelist() if not n_.endswith(".class")]
        eb3 = [n_ for n_ in zipfile.ZipFile(jar013).namelist() if not n_.endswith(".class")]
        za3, zb3 = zipfile.ZipFile(jar012), zipfile.ZipFile(jar013)
        nd3 = sorted(n_ for n_ in set(ea3) | set(eb3) if n_ not in ea3 or n_ not in eb3 or za3.read(n_) != zb3.read(n_))
        check(nd3 == ["manifest.json"], "AA9: non-class entries: only manifest.json differs (version): %s" % nd3)
    else:
        check(False, "AA9: SkyyGear-0.1.2.jar / SkyyGear-0.1.3.jar not found - the class compare could not run")
    Opened.DIR = None
    Opened.W.clear()
    print("AA. 0.1.3 world chests + level families done")

    # ============================================================================================================== AB. 0.2 (stage 1)
    # AB1 the level bands (an independent copy of Skyy's table, GearLevel.band over every vanilla gear id + gathering tool vs an
    # independent Python rule, Armor_Copper 1-18, the fresh file, one-number rows, odd values, the rows + check hooks); AB2 crafted at
    # your level (below / inside / above the band, Skyy's level-80 copper pickaxe, tools, the gate floor, craft.levelFrom / weaponSkill /
    # belowBand block, part.levels off, no SkyySkills, no class, the bench roll, the /craft bridge); AB3 the gate floor in every gate state +
    # the requirement check with stored levels + old items without lvl (legacy, SkyyRolls, a table change, reforge / identify stamp a
    # missing lvl only); AB4 the tooltip lines; AB5 gear:fn:sig with the level; AB6 /gear relevel; AB7 migrate02 on a scratch COPY of the
    # live config.properties (+ the start twice, CRLF, custom values, Armor_Copper typed by hand, scalar keys already there, the kit Undo,
    # History blocked, the fresh file, a 0.1 file through all five updates, edge cases, random files); AB8 the new recipes (engine codec
    # decode, the vanilla model recipe, outputs, ids, no vanilla recipe changed, crafted at your level); AB9 the class byte-compare
    # 0.1.3 -> 0.2; AB10 the wiring (bytecode).
    Gate, Admin, Fn, Stats_, Armor_ = J("GearGate"), J("GearAdmin"), J("GearFn"), J("GearStats"), J("GearArmor")
    BI2, BB2 = JClass("org.bson.BsonInt32"), JClass("org.bson.BsonBoolean")
    SB = JClass("java.lang.StringBuilder")
    OAb = JArray(JObject)
    C_BAD, C_OK, C_GRAY = str(Defs.C_BAD), str(Defs.C_OK), str(Defs.C_GRAY)
    BANDS_T = [("Crude", 1, 13), ("Wood", 1, 13), ("Copper", 10, 18), ("Armor_Copper", 1, 18), ("Bronze", 15, 23), ("Iron", 15, 23),
               ("Thorium", 20, 28), ("Cobalt", 25, 38), ("Adamantite", 35, 43), ("Mithril", 40, 49), ("Onyxium", 40, 49)]
    FAMB_T = [(t_, l_, min(l_ + 7, 49)) for t_, l_ in FAMS]
    ALLB = BANDS_T + FAMB_T
    OLDT = dict([(t_, str(l_)) for t_, l_ in METALS] + [("Armor_Copper", "1")] + [(t_, str(l_)) for t_, l_ in FAMS])

    def pyband(i_, table=None, default=77):
        """the band rule written independently: the row level() matches (at each id word from the left the longest entry first, max 3
        words) gives (min, cap, 1); no row = (default, default, 3)"""
        table = ALLB if table is None else table
        m_ = dict((t_.lower(), (s_, c_)) for t_, s_, c_ in table)
        mw_ = min(3, max(len(t_.split("_")) for t_, _s, _c in table))
        tk_ = i_.split("_")
        for a_ in range(len(tk_)):
            for n2 in range(mw_, 0, -1):
                k_ = "_".join(tk_[a_:a_ + n2]).lower()
                if a_ + n2 <= len(tk_) and k_ in m_:
                    return (m_[k_][0], m_[k_][1], 1)
        return (default, default, 3)

    def bandj(i_):
        return tuple(int(x_) for x_ in Lvl.band(i_))

    # ---- AB1. the level bands
    check([(str(t_), int(s_), int(c_)) for t_, s_, c_ in zip(Cfg.BD_T, Cfg.BD_MIN, Cfg.BD_CAP)] == ALLB and int(Cfg.BD_METALS) == 11,
          "AB1: GearCfg.BD_T / BD_MIN / BD_CAP = Skyy's bands (Wood / Crude 1-13, Copper 10-18, Armor_Copper 1-18, Bronze / Iron 15-23, "
          "Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49) + the 59 families start..start+7 (max 49)")
    check(int(Cfg.VTOP) == 49 and int(Cfg.BAND_W_DEF) == 8 and [(str(t_), str(v_)) for t_, v_ in zip(Cfg.BO_T, Cfg.BO_V)]
          == [(t_, str(l_)) for t_, l_ in METALS] + [("Armor_Copper", "1")] + [(t_, str(l_)) for t_, l_ in FAMS],
          "AB1: the vanilla ceiling 49, width 8, the 0.1.3 default texts migrate02 replaces (metals, Armor_Copper=1, families)")
    Cfg.apply(Props(), False)
    Cfg.LEVEL_DEFAULT = 77                 # the bare JVM has no Item assets: 77 = "no table row matched" (Hytale's level would apply in game)
    TOOLS_AZ = sorted(i_ for i_ in AZJ if i_.startswith(("Tool_Pickaxe_", "Tool_Hatchet_", "Tool_Hoe_", "Tool_Sickle_", "Tool_Shovel_")))
    bm_ = []
    for i_ in GEAR_AZ + TOOLS_AZ:
        if bandj(i_) != pyband(i_):
            bm_.append((i_, bandj(i_), pyband(i_)))
        if int(Lvl.level(i_, None)) != bandj(i_)[0]:
            bm_.append((i_, "level", int(Lvl.level(i_, None))))
    check(not bm_ and len(GEAR_AZ) == 304 and len(TOOLS_AZ) == 32,
          "AB1: GearLevel.band = the independent rule for all %d vanilla gear ids + %d gathering tools, band start = level(): %s" % (len(GEAR_AZ), len(TOOLS_AZ), bm_[:4]))
    cu_ = [i_ for i_ in GEAR_AZ if i_.startswith("Armor_Copper_")]
    check(len(cu_) == 4 and all(bandj(i_) == (1, 18, 1) and str(Lvl.entry(i_)) == "armor_copper" for i_ in cu_),
          "AB1: Armor_Copper 1-18 (LOCKED 2026-10-01) for the 4 copper armor pieces: %s" % [(i_, bandj(i_)) for i_ in cu_])
    for i_, w_ in (("Weapon_Sword_Copper", (10, 18, 1)), ("Tool_Pickaxe_Copper", (10, 18, 1)), ("Weapon_Wand_Wood", (1, 13, 1)),
                   ("Weapon_Sword_Crude", (1, 13, 1)), ("Weapon_Staff_Iron", (15, 23, 1)), ("Weapon_Sword_Bronze", (15, 23, 1)),
                   ("Armor_Thorium_Chest", (20, 28, 1)), ("Weapon_Staff_Cobalt", (25, 38, 1)), ("Weapon_Staff_Adamantite", (35, 43, 1)),
                   ("Weapon_Staff_Mithril", (40, 49, 1)), ("Armor_Onyxium_Head", (40, 49, 1)), ("Armor_Prisma_Chest", (45, 49, 1)),
                   ("Weapon_Daggers_Stone_Trork", (5, 12, 1)), ("Weapon_Staff_Crystal_Ice", (40, 47, 1)), ("Armor_QA_Chest", (77, 77, 3))):
        check(bandj(i_) == w_, "AB1: band(%s) = %s (%s)" % (i_, w_, bandj(i_)))
    ABD = os.path.join(SCRATCH, "work", "ab02")

    def bcase(name, data):
        cfg_quiet()
        shutil.rmtree(os.path.join(ABD, name), ignore_errors=True)
        d_ = os.path.join(ABD, name, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    FRESH_TXT = ("Crude 1-13, Wood 1-13, Copper 10-18, Armor_Copper 1-18, Bronze 15-23, Iron 15-23, Thorium 20-28, Cobalt 25-38, "
                 "Adamantite 35-43, Mithril 40-49, Onyxium 40-49; 59 of 59 family rows (59 at the 0.2 default band)")
    d, f = bcase("fresh", None)
    Cfg.load()
    pf_ = props(rb(f).decode("latin-1"))
    pf_["level.default"] = "77"
    ppf = Props()
    for k_, v_ in pf_.items():
        ppf.setProperty(k_, v_)
    Cfg.apply(ppf, True)
    check(all(bandj(i_) == pyband(i_) for i_ in GEAR_AZ + TOOLS_AZ) and str(Cfg.matText()) == FRESH_TXT,
          "AB1: the fresh file gives the same bands (the loader path) and the ready line: %s" % str(Cfg.matText()))
    check(all(pf_.get("level.material." + t_) == "%d,%d" % (s_, c_) for t_, s_, c_ in ALLB) and pf_.get("part.levels") == "true"
          and pf_.get("level.bandWidth") == "8" and pf_.get("level.gateFloor") == "1" and pf_.get("craft.levelFrom") == "gate"
          and pf_.get("craft.belowBand") == "min" and pf_.get("craft.weaponSkill") == "", "AB1: the fresh file's band rows + the six new settings")
    p1_ = Props()
    for k_, v_ in (("level.material.Copper", "12"), ("level.material.Prisma", "45"), ("level.material.Mithril", "60"), ("level.material.Iron", "15,9"),
                   ("level.material.Thorium", "20|30"), ("level.material.Cobalt", "x,y"), ("level.material.Wood", "0"), ("level.material.Onyxium", "98"),
                   ("level.item.Weapon_Sword_Bronze", "33"), ("level.default", "77")):
        p1_.setProperty(k_, v_)
    Cfg.apply(p1_, True)
    check(bandj("Weapon_Sword_Copper") == (12, 19, 1) and bandj("Armor_Prisma_Head") == (45, 49, 1) and bandj("Weapon_Sword_Mithril") == (60, 67, 1)
          and bandj("Weapon_Sword_Iron") == (15, 15, 1) and bandj("Weapon_Sword_Thorium") == (20, 30, 1) and bandj("Weapon_Sword_Cobalt") == (77, 77, 3)
          and bandj("Weapon_Staff_Wood") == (0, 7, 1) and bandj("Weapon_Sword_Onyxium") == (98, 100, 1) and bandj("Weapon_Sword_Bronze") == (33, 33, 0),
          "AB1: one number = N to N+7 (never past 49 for a vanilla level, never past 100), cap below min = exactly min, a hand-typed '|', "
          "a bad line ignored, Level by item = exactly that level (no range)")
    p1_.setProperty("level.bandWidth", "5")
    Cfg.apply(p1_, True)
    w5_ = bandj("Weapon_Sword_Copper")
    p1_.setProperty("level.bandWidth", "1")
    Cfg.apply(p1_, True)
    check(w5_ == (12, 16, 1) and bandj("Weapon_Sword_Copper") == (12, 12, 1) and int(Cfg.BAND_W) == 1, "AB1: level.bandWidth 5 -> 12-16, 1 -> exactly 12")
    p1_.setProperty("level.bandWidth", "999")
    Cfg.apply(p1_, True)
    check(int(Cfg.BAND_W) == 50, "AB1: level.bandWidth is clamped to 1-50")
    check(Cfg.checkBand("level.material[Copper]", "10|9") is not None and "Cap must be at least Min" in str(Cfg.checkBand("level.material[Copper]", "10|9"))
          and Cfg.checkBand("level.material[Copper]", "10|18") is None and Cfg.checkBand("level.material[Copper]", None) is None
          and Cfg.checkBand("level.material[Copper]", "10|10") is None, "AB1: the band check hook refuses a cap below min only")
    check(Cfg.checkCraftSkill("craft.weaponSkill", "Weapon_Staff_:Sorcery, Weapon_Wand_:Divinity") is None and Cfg.checkCraftSkill("craft.weaponSkill", "") is None
          and Cfg.checkCraftSkill("craft.weaponSkill", "Weapon_Staff_") is not None and Cfg.checkCraftSkill("craft.weaponSkill", ":Sorcery") is not None
          and Cfg.checkCraftSkill("craft.weaponSkill", "Weapon_Staff_: ") is not None, "AB1: craft.weaponSkill accepts prefix:Skill pairs only")
    rk_ = [str(k) for k in Rows.KEYS]
    rd_ = dict(zip(rk_, zip([str(x) for x in Rows.TYPES], [str(x) for x in Rows.DEFS], [str(x) for x in Rows.FLAGS], [str(x) for x in Rows.OPTS])))
    check(rd_.get("part.levels") == ("bool", "true", "live,part,danger", "") and rd_.get("level.bandWidth", ("",))[:3] == ("int", "8", "live,danger")
          and rd_.get("level.gateFloor", ("",))[:3] == ("int", "1", "live,danger") and rd_.get("craft.levelFrom") == ("choice", "gate", "live", "gate|Your skill,band|Band start")
          and rd_.get("craft.belowBand") == ("choice", "min", "live", "min|Make at band start,block|Refuse")
          and rd_.get("craft.weaponSkill", ("",))[:3] == ("text", "", "live,adv") and rd_.get("level.material", ("",))[3] == "int;type;Min|Cap",
          "AB1: the six new Server Setup rows (part.levels is a part switch with the confirm; level.gateFloor confirms like level.bandWidth - "
          "review finding 6) + the Min | Cap table: %s" % [rd_.get(k_) for k_ in
          ("part.levels", "level.bandWidth", "level.gateFloor", "craft.levelFrom", "craft.belowBand", "craft.weaponSkill", "level.material")])
    Cfg.LEVEL_DEFAULT = 0
    Cfg.apply(Props(), False)
    print("AB1. bands done: %d vanilla gear ids + %d tools, 4 copper armor pieces 1-18" % (len(GEAR_AZ), len(TOOLS_AZ)))

    # ---- AB2. crafted at your level (spec 4): the crafter's skill level (floored) moved into the band
    LVS = {}

    @JImplements("java.util.function.Function")
    class SkillFn:
        @JOverride
        def apply(self, o):
            v_ = LVS.get((str(o[0]), str(o[1])))
            return None if v_ is None else Integer.valueOf(v_)

    @JImplements("java.util.function.Function")
    class AllowFn:
        @JOverride
        def apply(self, o):
            return JBoolean(True)

    def setlv(u_, sk_, v_):
        LVS[(str(u_), sk_)] = v_
        Gate.forget(u_)

    def skills_on():
        bridge.put("skill:fn:level", SkillFn())
        for u_ in (U1, U2):
            Gate.forget(u_)

    def skills_off():
        bridge.remove("skill:fn:level")
        for u_ in (U1, U2):
            Gate.forget(u_)

    skills_on()
    bridge.put("class:skill:" + str(U1), "Divinity")
    bridge.put("class:skill:" + str(U2), "Divinity")

    def cl(i_, u_=None):
        return int(Roll.craftLevel(i_, U1 if u_ is None else u_))

    def cnote(i_, u_=None):
        n_ = Roll.craftNote(i_, U1 if u_ is None else u_)
        return None if n_ is None else str(n_)

    setlv(U1, "Divinity", 0)
    check(cl("Weapon_Wand_Wood") == 1 and cnote("Weapon_Wand_Wood") is None, "AB2: a fresh Divinity 0 Priest crafts a Wood wand at Lv 1 (the gate floor), no note")
    setlv(U1, "Divinity", 4)
    check(cl("Weapon_Wand_Wood") == 4 and cnote("Weapon_Wand_Wood") is None, "AB2: Divinity 4 -> a Lv 4 Wood wand (inside the band)")
    check(cl("Weapon_Staff_Copper") == 10 and cnote("Weapon_Staff_Copper") == "Made at Lv 10 (the lowest level of Copper gear) - you need Divinity 10 to use it (you: 4).",
          "AB2: below the band -> made at the band start + the chat note: %s" % cnote("Weapon_Staff_Copper"))
    check(cl("Armor_Copper_Chest") == 4, "AB2: copper ARMOR has no gap below (1-18): Divinity 4 -> Lv 4")
    setlv(U1, "Divinity", 12)
    check(cl("Weapon_Staff_Copper") == 12 and cnote("Weapon_Staff_Copper") is None and cl("Weapon_Sword_Iron") == 15, "AB2: Divinity 12: Copper staff 12, Iron sword 15 (its start)")
    setlv(U1, "Divinity", 13)
    t13 = (cl("Weapon_Wand_Wood"), cnote("Weapon_Wand_Wood"))
    setlv(U1, "Divinity", 14)
    check(t13 == (13, None) and cl("Weapon_Wand_Wood") == 13 and cnote("Weapon_Wand_Wood") == "Wood gear caps at Lv 13 - a better material goes higher.",
          "AB2: Divinity 13 -> 13 (the cap, no note); 14 -> still 13 + the cap note: %s" % cnote("Weapon_Wand_Wood"))
    setlv(U1, "Divinity", 80)
    check(cl("Weapon_Staff_Copper") == 18 and cnote("Weapon_Staff_Copper") == "Copper gear caps at Lv 18 - a better material goes higher."
          and cl("Armor_Copper_Head") == 18 and cnote("Armor_Copper_Head") == "Copper armor caps at Lv 18 - a better material goes higher."
          and cl("Weapon_Staff_Mithril") == 49 and cl("Armor_Prisma_Chest") == 49, "AB2: Divinity 80 -> every band's cap (Copper 18, Mithril 49, Prisma 49)")
    setlv(U1, "Mining", 80)
    check(cl("Tool_Pickaxe_Copper") == 18 and cnote("Tool_Pickaxe_Copper") == "Copper gear caps at Lv 18 - a better material goes higher.",
          "AB2: Skyy's example - a level 80 player crafting a Copper pickaxe gets the Copper cap (Mining 80 -> Lv 18)")
    setlv(U1, "Mining", 3)
    # review of 0.2 finding 1: the gathering tools' gate is "coming later" (never enforced) - no "you need Mining 10 to use it" line
    check(cl("Tool_Pickaxe_Copper") == 10 and cnote("Tool_Pickaxe_Copper") is None,
          "AB2: a pickaxe reads Mining (not the class skill): Mining 3 -> Lv 10, and NO 'you need Mining 10 to use it' line (tool gates "
          "are coming later; review finding 1): %s" % cnote("Tool_Pickaxe_Copper"))
    # review of 0.2 finding 1 over every vanilla gear id + gathering tool: with every skill at 0 a below-band craft gets the chat line AND
    # the craft.belowBand block refusal exactly where the item's gate is enforced (combat / equipment) - never for a tool
    for sk_ in ("Divinity", "Mining", "Foraging", "Farming"):
        setlv(U1, sk_, 0)
    Cfg.CRAFT_BELOW = "block"
    wrong1 = []
    n_line = n_tline = 0
    for i_ in GEAR_AZ + TOOLS_AZ:
        b_ = bandj(i_)
        enf_ = bool(Defs.enforcedKind(Data.kindFor(i_)))
        want_ = b_[2] == 1 and b_[0] > 1 and enf_
        nt_, bw_ = cnote(i_), Roll.blockWhy(i_, U1)
        if ((nt_ is not None) != want_ or (bw_ is not None) != want_ or (nt_ is not None and not nt_.endswith("to use it (you: 0)."))
                or (bw_ is not None and not str(bw_).startswith("You need "))):
            wrong1.append((i_, b_, enf_, nt_, None if bw_ is None else str(bw_)))
        n_line += 1 if nt_ is not None else 0
        n_tline += 1 if (b_[2] == 1 and b_[0] > 1 and not enf_) else 0
    Cfg.CRAFT_BELOW = "min"
    check(not wrong1 and n_line > 100 and n_tline >= 20 and all(not bool(Defs.enforcedKind(Data.kindFor(t_))) for t_ in TOOLS_AZ),
          "AB2 (review finding 1): all %d gear ids + %d tools at skill 0 - the below-band line and the block refusal only where the gate is "
          "enforced (%d gear lines; %d tools below their band get neither): %s" % (len(GEAR_AZ), len(TOOLS_AZ), n_line, n_tline, wrong1[:3]))
    setlv(U1, "Divinity", 0)
    Cfg.CRAFT_BELOW = "block"
    bwt_ = (Roll.blockWhy("Tool_Pickaxe_Mithril", U1), Roll.blockWhy("Tool_Hatchet_Copper", U1), Roll.blockWhy("Weapon_Staff_Copper", U1))
    Cfg.CRAFT_BELOW = "min"
    check(bwt_[0] is None and bwt_[1] is None and bwt_[2] is not None and "Divinity 10" in str(bwt_[2]),
          "AB2 (review finding 1): Refuse mode at skill 0 - a Mithril pickaxe / Copper hatchet are crafted (no refusal), a Copper staff is refused")
    setlv(U1, "Mining", 3)
    setlv(U1, "Foraging", 16)
    setlv(U1, "Farming", 0)
    check(cl("Tool_Hatchet_Iron") == 16 and cl("Tool_Hoe_Crude") == 1 and cl("Tool_Sickle_Crude" if "Tool_Sickle_Crude" in AZJ else "Tool_Hoe_Crude") == 1,
          "AB2: a hatchet reads Foraging (16 -> 16), a hoe Farming (0 -> 1)")
    setlv(U1, "Divinity", 12)
    bad_ = []
    for _n in range(60):
        dd_ = Roll.craftDoc("Weapon_Staff_Copper", U1)
        if int(dd_.getInt32("lvl").getValue()) != 12 or int(Lvl.level("Weapon_Staff_Copper", dd_)) != 12 or str(dd_.getString("src").getValue()) != "craft":
            bad_.append("lvl")
        r_ = int(Data.rarity(dd_))
        for m_ in Data.mods(dd_):
            k_, v_ = str(m_.asDocument().getString("s").getValue()), int(m_.asDocument().getInt32("v").getValue())
            b2_ = Roll.bounds(si(k_), r_, 12)
            if not (int(b2_[0]) <= v_ <= int(b2_[1])):
                bad_.append((k_, v_, r_))
    check(not bad_, "AB2: craftDoc stamps lvl 12 BEFORE the roll - every modifier lies inside its bounds at level 12 (60 rolls): %s" % bad_[:3])
    setlv(U1, "Mining", 80)
    td_ = Roll.craftDoc("Tool_Pickaxe_Copper", U1)
    check(int(td_.getInt32("lvl").getValue()) == 18 and int(Data.rarity(td_)) == 0 and Data.mods(td_).size() == 0 and str(Data.kind(td_)) == "mining"
          and str(Data.gate(td_)) == "Mining" and not bool(Data.isGear("Tool_Pickaxe_Copper")) and bool(Roll.craftable("Tool_Pickaxe_Copper")),
          "AB2: a crafted pickaxe stores Lv 18, stays Normal with no modifiers (coming-later stats never roll), kind mining, gate Mining")
    check(bool(Roll.craftable("Weapon_Sword_Iron")) and bool(Roll.craftable("Tool_Hatchet_Iron")) and not bool(Roll.craftable("Ingredient_Bar_Iron"))
          and not bool(Roll.craftable("Weapon_Arrow_Crude")) and not bool(Roll.craftable("Weapon_Shield_Iron")) and not bool(Roll.craftable(None)),
          "AB2: craftable = gear + the gathering tools; never ammo, shields, materials")
    Cfg.CRAFT_FROM = "band"
    check(cl("Weapon_Staff_Copper") == 10 and cnote("Weapon_Staff_Copper") is None, "AB2: craft.levelFrom band -> always the band start, no note")
    Cfg.CRAFT_FROM = "gate"
    Cfg.PART_LEVELS = False
    nd0 = Roll.craftDoc("Weapon_Staff_Copper", U1)
    gd0 = Roll.newDoc("Weapon_Sword_Iron", 0, True, "admin")
    check(cl("Weapon_Staff_Copper") == -1 and not nd0.containsKey("lvl") and not gd0.containsKey("lvl") and not bool(Roll.craftable("Tool_Pickaxe_Copper"))
          and int(Lvl.level("Weapon_Staff_Copper", nd0)) == 10, "AB2: part.levels off = 0.1.3: nothing stamped, the table's start level, tools not documented")
    Cfg.PART_LEVELS = True
    Cfg.GATE_FLOOR = 0
    setlv(U1, "Divinity", 0)
    check(cl("Weapon_Wand_Wood") == 1 and cnote("Weapon_Wand_Wood") == "Made at Lv 1 (the lowest level of Wood gear) - you need Divinity 1 to use it (you: 0).",
          "AB2: level.gateFloor 0 -> Divinity 0 is below the Wood band (note)")
    Cfg.GATE_FLOOR = 1
    setlv(U1, "Divinity", 12)
    skills_off()
    check(cl("Weapon_Staff_Copper") == 10 and cnote("Weapon_Staff_Copper") is None, "AB2: without SkyySkills -> the band start, no note")
    skills_on()
    bridge.remove("class:skill:" + str(U1))
    bridge.put("class:fn:allowed", AllowFn())
    Gate.forget(U1)
    check(cl("Weapon_Staff_Copper") == 10 and cnote("Weapon_Staff_Copper") is None and Roll.craftSkill("Weapon_Staff_Copper", U1) is None,
          "AB2: SkyyClasses present but no class picked -> the band start")
    bridge.remove("class:fn:allowed")
    Gate.forget(U1)
    check(str(Roll.craftSkill("Weapon_Staff_Copper", U1)) == "Combat", "AB2: without SkyyClasses the class gate asks the pseudo-skill Combat (as the gate does)")
    bridge.put("class:skill:" + str(U1), "Divinity")
    Gate.forget(U1)
    Cfg.CRAFT_SKILL = "Weapon_Staff_:Sorcery, Weapon_:Fury"
    setlv(U1, "Sorcery", 20)
    setlv(U1, "Fury", 3)
    check(cl("Weapon_Staff_Copper") == 18 and str(Roll.craftLabel("Weapon_Staff_Copper", U1)) == "Sorcery" and cl("Weapon_Wand_Wood") == 3
          and cl("Tool_Pickaxe_Copper") == 18, "AB2: craft.weaponSkill - the longest prefix names the skill (staff: Sorcery 20 -> 18; wand: Weapon_ -> Fury 3)")
    Cfg.CRAFT_SKILL = ""
    setlv(U1, "Divinity", 4)
    Cfg.CRAFT_BELOW = "block"
    check(str(Roll.blockWhy("Weapon_Staff_Copper", U1)) == "You need Divinity 10 to craft Staff Copper (you: 4) - Copper gear starts at Lv 10."
          and Roll.blockWhy("Weapon_Wand_Wood", U1) is None, "AB2: craft.belowBand block: the bench refusal text below the band; inside it nothing")
    setlv(U1, "Divinity", 12)
    check(Roll.blockWhy("Weapon_Staff_Copper", U1) is None, "AB2: block mode, Divinity 12 -> allowed")
    Cfg.CRAFT_BELOW = "min"
    setlv(U1, "Divinity", 4)
    check(Roll.blockWhy("Weapon_Staff_Copper", U1) is None, "AB2: min mode never refuses")
    # the bench roll (GearCraftTask.rollIn on plain containers) and the /craft bridge (gear:fn:roll mode 8)
    setlv(U1, "Divinity", 12)
    setlv(U1, "Mining", 80)
    hb_, st_ = SIC(9), SIC(9)
    hb_.setItemStackForSlot(0, IS("Weapon_Staff_Copper", 1))
    hb_.setItemStackForSlot(1, IS("Tool_Pickaxe_Copper", 1))
    css_ = JArray(IC)([hb_, st_])
    gv_ = JArray(IC)([st_])
    n1_ = int(CraftTask.rollIn(css_, gv_, U1, "Weapon_Staff_Copper", IdMap(), 1, None, SB()))
    n2_ = int(CraftTask.rollIn(css_, gv_, U1, "Tool_Pickaxe_Copper", IdMap(), 1, None, SB()))
    ds_, dt_ = Data.gearDoc(hb_.getItemStack(0).getMetadata()), Data.gearDoc(hb_.getItemStack(1).getMetadata())
    check(n1_ == 1 and n2_ == 1 and int(ds_.getInt32("lvl").getValue()) == 12 and int(dt_.getInt32("lvl").getValue()) == 18,
          "AB2: the vanilla bench path stamps the crafter's level (staff Divinity 12 -> 12, pickaxe Mining 80 -> 18)")
    fr_ = Fn(8)
    o3_ = fr_.apply(OAb([U1, "Weapon_Staff_Copper", Integer.valueOf(3), "craft", "SkyyGear_Recipe_Weapon_Staff_Copper"]))
    lv3_ = [int(Data.gearDoc(x_.getMetadata()).getInt32("lvl").getValue()) for x_ in o3_]
    o5_ = fr_.apply(OAb([U1, "Weapon_Staff_Copper", Integer.valueOf(1), "craft", "r", Integer.valueOf(5)]))
    o99 = fr_.apply(OAb([U1, "Weapon_Staff_Copper", Integer.valueOf(1), "craft", "r", Integer.valueOf(99)]))
    o14 = fr_.apply(OAb([U1, "Weapon_Staff_Copper", Integer.valueOf(1), "craft", "r", Integer.valueOf(11)]))
    opk = fr_.apply(OAb([U1, "Tool_Pickaxe_Copper", Integer.valueOf(1), "craft", "r"]))
    olt = fr_.apply(OAb([U1, "Weapon_Staff_Copper", Integer.valueOf(1), "loot", "r"]))
    check(lv3_ == [12, 12, 12] and all(str(x_.getItemId()) == "Weapon_Staff_Copper" and int(x_.getQuantity()) == 1 for x_ in o3_),
          "AB2: /craft (gear:fn:roll mode 8): 3 items, each its own document at the crafter's level 12: %s" % lv3_)
    lvof = lambda a_: int(Data.gearDoc(a_[0].getMetadata()).getInt32("lvl").getValue())
    check(lvof(o5_) == 10 and lvof(o99) == 12 and lvof(o14) == 11, "AB2: an optional requested level is kept in the band (5 -> 10) and never above the crafter's level (99 -> 12; 11 stays 11)")
    check(lvof(opk) == 18 and int(Data.rarity(Data.gearDoc(opk[0].getMetadata()))) == 0 and lvof(olt) == 10,
          "AB2: the bridge stamps a crafted pickaxe (18, Normal); another source gets the band start (10)")
    check(fr_.apply(OAb([U1, "Ingredient_Bar_Iron", Integer.valueOf(1), "craft", "r"])) is None, "AB2: a non-gear output -> null (SkyySacks gives it plain)")
    # review of 0.2 finding 3: the craft note once per crafting burst - GearRoll.noteDue(u, id, now) = no note for that player + item in
    # the last NOTE_MS (10 s); every noted craft refreshes the time. A timed bench queue fires one CraftRecipeEvent$Post (= one
    # GearCraftTask) per unit: 10 Copper staffs at 3 s each must print ONE line, not 10 (and not one per fixed 10 s window either).
    if not (hasattr(Roll, "noteDue") and hasattr(Roll, "NOTED")):
        check(False, "AB2 (review finding 3): GearRoll.noteDue / NOTED missing - the craft note is not throttled")
    else:
        Roll.NOTED.clear()
        T0 = 7000000
        due = lambda u_, i_, t_: bool(Roll.noteDue(u_, i_, JLong(t_)))
        q10 = [due(U1, "Weapon_Staff_Copper", T0 + 3000 * k_) for k_ in range(10)]
        q4s = [due(U1, "Weapon_Staff_Iron", T0 + 4000 * k_) for k_ in range(10)]
        tl_ = T0 + 3000 * 9
        gap = (due(U1, "Weapon_Staff_Copper", tl_ + 9999), due(U1, "Weapon_Staff_Copper", tl_ + 9999 + 10000))
        oth = (due(U2, "Weapon_Staff_Copper", tl_ + 9999 + 10001), due(U1, "Weapon_Staff_Thorium", tl_ + 9999 + 10001),
               due(U1, "Weapon_Staff_Copper", tl_ + 9999 + 10002))
        check(int(Roll.NOTE_MS) == 10000 and q10 == [True] + [False] * 9 and q4s == [True] + [False] * 9,
              "AB2 (review finding 3): a queue of 10 Copper staffs (one Post per unit, 3 s / 4 s apart) gets ONE note: %s / %s" % (q10, q4s))
        check(gap == (False, True) and oth == (True, True, False),
              "AB2 (review finding 3): 9.999 s after the last noted craft still quiet, 10 s of quiet = a new burst gets its note; another player / "
              "another item has its own time: %s %s" % (gap, oth))
        Roll.NOTED.clear()
        big = [due(U1, "Weapon_Sword_X%03d" % k_, T0 + k_) for k_ in range(600)]
        n600 = int(Roll.NOTED.size())
        late = due(U1, "Weapon_Sword_Late", T0 + 30000)
        check(all(big) and n600 == 600 and late and int(Roll.NOTED.size()) == 1 and Roll.NOTED.containsKey(str(U1) + "|Weapon_Sword_Late"),
              "AB2 (review finding 3): the time map only purges entries older than 10 s (600 fresh entries stay, the next call 30 s later "
              "leaves just its own key): %d -> %d" % (n600, int(Roll.NOTED.size())))
        Roll.NOTED.clear()
    rt_, ap_, pre_ = mcode("GearCraftTask", "run"), mcode("GearFn", "apply"), mcode("GearCraftPreSys", "handle")
    i_rt = (rt_.find("GearRoll.craftNote("), rt_.find("GearRoll.noteDue("), rt_.find("PlayerRef.sendMessage("))
    i_ap = (ap_.find("GearRoll.craftNote("), ap_.find("GearRoll.noteDue("), ap_.find("Gear.tell("))
    check(all(x_ >= 0 for x_ in i_rt + i_ap) and list(i_rt) == sorted(i_rt) and list(i_ap) == sorted(i_ap) and rt_.count("GearRoll.noteDue(") == 1
          and ap_.count("GearRoll.noteDue(") == 1 and "noteDue" not in pre_ and pre_.count("PlayerRef.sendMessage(") == 1,
          "AB2 (review finding 3): both craft paths ask noteDue between craftNote and the send (bench task, /craft mode 8); the bench "
          "refusal is not throttled (one line per refused click): %s %s" % (i_rt, i_ap))
    print("AB2. crafted at your level done")

    # ---- AB3. the gate floor in every state + the requirement check with stored levels + old items without lvl
    setlv(U2, "Divinity", 0)
    wold = Data.legacy("Weapon_Wand_Wood")
    c_ = Gate.check(U2, "Weapon_Wand_Wood", wold, Lvl.level("Weapon_Wand_Wood", wold))
    check(not wold.containsKey("lvl") and int(Lvl.level("Weapon_Wand_Wood", wold)) == 1 and bool(c_[0]) and int(c_[3]) == 0 and int(c_[5]) == 0,
          "AB3: a fresh Priest (Divinity 0) can use the kit's unstamped Wood wand: it reads Lv 1, the gate floor counts 0 as 1")
    Cfg.GATE_FLOOR = 0
    c0_ = Gate.check(U2, "Weapon_Wand_Wood", wold, 1)
    Cfg.GATE_FLOOR = 1
    check(not bool(c0_[0]), "AB3: without the floor (level.gateFloor 0) the Lv 1 kit wand would be blocked at Divinity 0")
    w4_ = wold.clone()
    w4_.put("lvl", BI2(4))
    setlv(U2, "Divinity", 2)
    c2_ = Gate.check(U2, "Weapon_Wand_Wood", w4_, Lvl.level("Weapon_Wand_Wood", w4_))
    s2_ = Data.put(IS("Weapon_Wand_Wood", 1), w4_, U2)
    j2_ = Hit.judge(U2, s2_, False)
    setlv(U2, "Divinity", 4)
    c4_ = Gate.check(U2, "Weapon_Wand_Wood", w4_, Lvl.level("Weapon_Wand_Wood", w4_))
    j4_ = Hit.judge(U2, s2_, False)
    check(int(Lvl.level("Weapon_Wand_Wood", w4_)) == 4 and not bool(c2_[0]) and int(c2_[2]) == 4 and int(c2_[3]) == 2 and bool(c4_[0])
          and j2_ is not None and str(j2_[2]) == "Wand Wood needs Divinity 4 - you are 2" and j4_ is None,
          "AB3: a stored Lv 4 wand needs Divinity 4 (the table's Wood 1 is ignored): blocked at 2 (hit popup text), fine at 4")
    check(bool(Stats_.active(U2, "Weapon_Wand_Wood", w4_)), "AB3: GearStats.active follows the stored level")
    ar_ = Data.legacy("Armor_Iron_Chest")
    ar_.put("lvl", BI2(20))
    sa_ = Data.put(IS("Armor_Iron_Chest", 1), ar_, U2)
    setlv(U2, "Divinity", 12)
    check(bool(Armor_.inactive(U2, sa_)) and str(Armor_.why(U2, sa_)) == "Your Iron Chest gives no stats until Divinity 20 (you: 12)",
          "AB3: armor stamped Lv 20 is inactive at Divinity 12: %s" % Armor_.why(U2, sa_))
    bridge.remove("class:skill:" + str(U2))
    bridge.put("class:fn:allowed", AllowFn())
    Gate.forget(U2)
    s1a_ = Gate.check(U2, "Weapon_Wand_Wood", wold, 1)
    s1b_ = Gate.check(U2, "Weapon_Wand_Wood", w4_, 4)
    bridge.remove("class:fn:allowed")
    bridge.put("class:skill:" + str(U2), "Divinity")
    Gate.forget(U2)
    check(int(s1a_[5]) == 1 and bool(s1a_[0]) and not bool(s1b_[0]), "AB3: no class picked (state 1): Lv 1 passes (floor), Lv 4 does not")
    skills_off()
    Cfg.NO_SKILLS = "block"
    s2a_, s2b_ = Gate.check(U2, "Weapon_Wand_Wood", wold, 1), Gate.check(U2, "Weapon_Wand_Wood", w4_, 4)
    Cfg.NO_SKILLS = "pass"
    s2c_ = Gate.check(U2, "Weapon_Wand_Wood", w4_, 4)
    skills_on()
    check(int(s2a_[5]) == 2 and bool(s2a_[0]) and not bool(s2b_[0]) and bool(s2c_[0]), "AB3: no SkyySkills + level.noSkills block: Lv 1 passes (floor), Lv 4 blocked; pass = all")
    # old items without lvl keep reading the table (band start): legacy / SkyyRolls / passive stamp; a table change moves them, not stamped ones
    rl_ = BD()
    rl_.append("dmg", BI2(10))
    mg_ = Data.migrate("Weapon_Sword_Copper", rl_)
    st0 = Stamp.stampStack(IS("Weapon_Sword_Iron", 1), U2, None)
    sd0 = Data.gearDoc(st0.getMetadata())
    check(not mg_.containsKey("lvl") and int(Lvl.level("Weapon_Sword_Copper", mg_)) == 10 and sd0 is not None and not sd0.containsKey("lvl")
          and int(Lvl.level("Weapon_Sword_Iron", sd0)) == 15 and int(Lvl.level("Weapon_Sword_Crude", Data.legacy("Weapon_Sword_Crude"))) == 1,
          "AB3: existing gear is never stamped by the passive stamp / SkyyRolls migration: it reads the band start (Copper 10, Iron 15, Crude 1)")
    cs_ = Data.legacy("Weapon_Sword_Copper")
    cs10 = cs_.clone()
    cs10.put("lvl", BI2(10))
    p2_ = Props()
    for t_, s_, c2 in ALLB:
        p2_.setProperty("level.material." + t_, "%d,%d" % (s_, c2))
    p2_.setProperty("level.material.Copper", "12,20")
    Cfg.apply(p2_, True)
    check(int(Lvl.level("Weapon_Sword_Copper", cs_)) == 12 and int(Lvl.level("Weapon_Sword_Copper", cs10)) == 10,
          "AB3: a band changed in Server Setup: an unstamped Copper sword follows it (12), a stamped one keeps its level (10)")
    Cfg.apply(Props(), False)
    rf_ = Roll.reforge("Weapon_Sword_Iron", Data.legacy("Weapon_Sword_Iron"))
    rs_ = Roll.reforge("Weapon_Sword_Iron", Roll.newDoc("Weapon_Sword_Iron", 1, True, "craft", 18))
    ud_ = Data.legacy("Weapon_Sword_Iron")
    ud_.put("id", BB2(False))
    idf = Roll.identify("Weapon_Sword_Iron", ud_, U2)
    un_ = Roll.unidDoc("Weapon_Sword_Iron", 1, "drop")
    gv2 = Roll.newDoc("Weapon_Sword_Copper", 0, True, "admin")
    check(int(rf_.getInt32("lvl").getValue()) == 15 and int(rs_.getInt32("lvl").getValue()) == 18 and int(idf.getInt32("lvl").getValue()) == 15
          and int(un_.getInt32("lvl").getValue()) == 15 and int(Roll.identify("Weapon_Sword_Iron", un_, U2).getInt32("lvl").getValue()) == 15
          and int(gv2.getInt32("lvl").getValue()) == 10, "AB3: reforge / identify stamp a missing lvl (the level it reads now), never change one (18 stays); "
          "found gear (unidDoc) and /gear give (newDoc) store the band start")
    Cfg.PART_LEVELS = False
    rf0 = Roll.reforge("Weapon_Sword_Iron", Data.legacy("Weapon_Sword_Iron"))
    un0 = Roll.unidDoc("Weapon_Sword_Iron", 1, "drop")
    Cfg.PART_LEVELS = True
    check(not rf0.containsKey("lvl") and not un0.containsKey("lvl"), "AB3: part.levels off: reforge and drops stamp nothing (0.1.3)")
    print("AB3. gate floor + stored levels + old items done")

    # ---- AB4. the tooltip lines (spec 7): "Lv N - Requires <Skill> N" first, under the name
    def tip(i_, d_, o_):
        tx_, co_ = ArrayList(), ArrayList()
        View.lines(i_, d_, o_, tx_, co_)
        return [(str(t2), None if c2 is None else str(c2)) for t2, c2 in zip(tx_, co_)]

    setlv(U2, "Divinity", 2)
    t2_ = tip("Weapon_Wand_Wood", w4_, U2)
    setlv(U2, "Divinity", 4)
    t4_ = tip("Weapon_Wand_Wood", w4_, U2)
    check(t2_[0] == ("Lv 4 - Requires Divinity 4 (you: 2)", C_BAD) and t4_[0] == ("Lv 4 - Requires Divinity 4", C_OK),
          "AB4: the first line: red + '(you: 2)' when too low, the vanilla 'met' green when met: %s / %s" % (t2_[0], t4_[0]))
    check([x_[0] for x_ in t4_[1:]] == [x_[0] for x_ in t2_[1:]] and t4_[-1][0] == "NORMAL WEAPON" and not any(x_[0].startswith("Lv ") for x_ in t4_[1:]),
          "AB4: the level line appears once; the rest of the tooltip is unchanged")
    tu_ = tip("Weapon_Sword_Iron", un_, U2)
    check(tu_[0] == ("Lv 15 - Requires Divinity 15 (you: 4)", C_BAD) and tu_[1][0].startswith("Rarity: ") and tu_[2][0].startswith("Unidentified - "),
          "AB4: unidentified: the level line first, then the rarity: %s" % tu_[:2])
    tt_ = tip("Tool_Pickaxe_Copper", td_, U2)
    check(tt_[0] == ("Lv 18 - Requires Mining 18 (coming later)", C_GRAY) and tt_[-1][0] != "(coming later: gathering gear)",
          "AB4: a crafted pickaxe: 'Lv 18 - Requires Mining 18 (coming later)' in grey: %s" % tt_)
    tn_ = tip("Weapon_Wand_Wood", w4_, None)
    check(tn_[0] == ("Lv 4 - Requires Combat 4", C_GRAY), "AB4: no owner (AH / bridge text): neutral grey: %s" % (tn_[0],))
    skills_off()
    Cfg.NO_SKILLS = "block"
    tb_ = tip("Weapon_Wand_Wood", w4_, U2)
    Cfg.NO_SKILLS = "pass"
    tp_ = tip("Weapon_Wand_Wood", w4_, U2)
    skills_on()
    check(tb_[0] == ("Lv 4 - skills unavailable", C_BAD) and tp_[0] == ("Lv 4", C_GRAY), "AB4: without SkyySkills: 'Lv 4' / blocked 'Lv 4 - skills unavailable'")
    setlv(U2, "Divinity", 4)
    ta_ = tip("Armor_Iron_Chest", ar_, U2)
    check(ta_[0] == ("Lv 20 - Requires Divinity 20 (you: 4)", C_BAD) and ta_[1] == ("Gives no stats until Divinity 20", C_BAD),
          "AB4: under-level armor: the level line + 'Gives no stats until Divinity 20' right under it")
    pl_ = [str(x_) for x_ in View.plain("Weapon_Wand_Wood", w4_, U2)]
    check(pl_[0] == "Wand Wood" and pl_[1] == "Lv 4 - Requires Divinity 4", "AB4: plain lines (/gear, gear:fn:describe): name, then the level line")
    sv4 = str(View.sig("Weapon_Wand_Wood", 0, w4_, ArrayList(), ArrayList()))
    w9_ = w4_.clone()
    w9_.put("lvl", BI2(9))
    sv9 = str(View.sig("Weapon_Wand_Wood", 0, w9_, ArrayList(), ArrayList()))
    check(sv4 != sv9 and ":4:" in sv4 and ":9:" in sv9, "AB4: the render signature carries the level (a level change re-renders the tooltip)")
    # review of 0.2 finding 4: a crafted PLAIN tool (Normal, no modifiers) keeps the item's own quality frame + that quality's name colour
    # (a Mithril pickaxe stays Epic purple, not Normal white); gear keeps its rarity quality. A bare JVM has no quality assets, so a
    # quality asset map is put in place for this block only (ItemQuality.ASSET_STORE -> the same never-constructed fake store, its map
    # an IndexedLookupTableAssetMap whose lookup array holds test qualities): at own_ (the item's own quality index in a bare JVM, Item.UNKNOWN's)
    # "Epic" #8b339e, index 3 = a foreign quality (another mod's), 60..66 = today's Skyy_Gear_* rarity qualities (GearDefs.QIDX).
    from jpype import JByte
    IQ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    PCol = JClass("com.hypixel.hytale.protocol.Color")
    IDMK = str(JClass("com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata").KEY)
    SysJ = JClass("java.lang.System")

    @JImplements("java.util.function.IntFunction")
    class QArr:
        @JOverride
        def apply(self, n_):
            return JArray(IQ)(int(n_))

    def sb8(x_):
        return JByte(x_ - 256 if x_ > 127 else x_)

    def mkq(qid_, hx_):
        return IQ(qid_, 0, None, None, None, None, None, PCol(sb8(int(hx_[1:3], 16)), sb8(int(hx_[3:5], 16)), sb8(int(hx_[5:7], 16))),
                  None, True, False, False, None)

    def namehex(s_):
        """the colours in the tooltip NAME only (ItemDisplay.Name; the description has its own colours, e.g. the white NORMAL line)"""
        md_ = s_.getMetadata()
        v_ = md_.get(IDMK) if md_ is not None else None
        n_ = v_.asDocument().get("Name") if v_ is not None and v_.isDocument() else None
        j_ = str(BD().append("n", n_).toJson()).lower() if n_ is not None else ""
        return [h_ for h_ in ("#8b339e", "#123456", "#ffffff", "#ff55ff", "#55ffff") if h_ in j_]

    own_ = int(IS("Tool_Pickaxe_Mithril", 1).getQualityIndex())
    if not (0 <= own_ < 50 and own_ != 3):
        check(False, "AB4 (review finding 4): the bare JVM's own item quality index %d is not usable for the test quality map" % own_)
    else:
        qarr = JArray(IQ)(70)
        qarr[own_] = mkq("Epic", "#8b339e")
        qarr[3] = mkq("OtherModQuality", "#123456")
        for k_ in range(7):
            qarr[60 + k_] = mkq(str(Defs.R_QID[k_]), str(Defs.R_HEX[k_]).lower())
        qmap = ILT(QArr())
        fa_ = ILT.class_.getDeclaredField("array")
        fa_.setAccessible(True)
        fa_.set(qmap, qarr)
        # (fresh handles: the names of the bare-JVM setup at the top - us, store, fm - are reused by later sections)
        uq_ = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
        uq_.setAccessible(True)
        fiq_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
        fiq_.setAccessible(True)
        fmq_ = JClass("com.hypixel.hytale.assetstore.AssetStore").class_.getDeclaredField("assetMap")
        fmq_.setAccessible(True)
        qstore = uq_.get(None).allocateInstance(fiq_.get(None).getClass())     # the never-constructed fake store class (section A)
        fmq_.set(qstore, qmap)
        fq_ = IQ.class_.getDeclaredField("ASSET_STORE")
        fq_.setAccessible(True)
        oldqs, oldq, oldm = fq_.get(None), Defs.QIDX, Defs.QMISS
        fq_.set(None, qstore)
        Defs.QIDX = JArray(JInt)([60, 61, 62, 63, 64, 65, 66])
        Defs.QMISS = JLong(0)
        hasq = hasattr(View, "ourQ") and hasattr(View, "qualHex")      # (a jar without the fix fails these checks instead of stopping)
        ourq = lambda i_: hasq and bool(View.ourQ(i_))
        qhex = lambda i_: str(View.qualHex(i_)) if hasq and View.qualHex(i_) is not None else None
        try:
            setlv(U1, "Mining", 45)
            tdm = Roll.craftDoc("Tool_Pickaxe_Mithril", U1)
            tsm = Data.put(IS("Tool_Pickaxe_Mithril", 1), tdm, U1)
            wdr = Roll.newDoc("Weapon_Sword_Iron", 2, True, "admin")
            wsr = Data.put(IS("Weapon_Sword_Iron", 1), wdr, U1)
            check(bool(Defs.validQ(own_)) and bool(Defs.validQ(60)) and not bool(Defs.validQ(5)) and int(Defs.qIndex(2)) == 62,
                  "AB4 (review finding 4): the test quality map answers (own quality %d, Skyy_Gear_* 60..66, an empty slot is no quality)" % own_)
            check(int(Data.rarity(tdm)) == 0 and int(tsm.getQualityIndex()) == own_ and namehex(tsm) == ["#8b339e"],
                  "AB4 (review finding 4): a crafted Mithril pickaxe keeps the item's own quality (index %d, not Skyy_Gear_Normal 60) and its "
                  "name takes that quality's colour #8b339e (Epic purple), not Normal white: q=%d %s" % (own_, int(tsm.getQualityIndex()), namehex(tsm)))
            check(int(wsr.getQualityIndex()) == 62 and namehex(wsr) == ["#ff55ff"],
                  "AB4 (review finding 4): gear is unchanged - a Rare sword gets the Skyy_Gear_Rare quality (62) and the rarity colour: q=%d %s"
                  % (int(wsr.getQualityIndex()), namehex(wsr)))
            stale_ = IS("Tool_Pickaxe_Mithril", 1).withQuality(60)
            fix_ = View.apply(stale_, tdm, U1)
            check(not bool(Qual.wasOurs(60)) and ourq(60) and int(fix_.getQualityIndex()) == own_ and namehex(fix_) == ["#8b339e"]
                  and SysJ.identityHashCode(fix_) != SysJ.identityHashCode(stale_)
                  and SysJ.identityHashCode(View.apply(fix_, tdm, U1)) == SysJ.identityHashCode(fix_),
                  "AB4 (review finding 4): a tool that already carries today's Skyy_Gear_Normal quality (a valid index, not one of the last "
                  "start's: only ourQ sees it) goes back to its own quality, then stays put (no rewrite loop): q=%d" % int(fix_.getQualityIndex()))
            frn_ = View.apply(IS("Tool_Pickaxe_Mithril", 1).withQuality(3), tdm, U1)
            check(int(frn_.getQualityIndex()) == 3 and namehex(frn_) == ["#123456"] and hasq and not ourq(3) and not ourq(-1),
                  "AB4 (review finding 4): a quality another mod gave the stack is kept (the name takes its colour): q=%d %s"
                  % (int(frn_.getQualityIndex()), namehex(frn_)))
            check(qhex(own_) == "#8b339e" and hasq and qhex(5) is None and qhex(Integer.MIN_VALUE) is None and qhex(500) is None,
                  "AB4 (review finding 4): qualHex = the quality asset's text colour; an empty / unknown index = null (the rarity colour stays)")
            pi_ = Props()
            pi_.setProperty("gear.include", "Tool_Pickaxe_")
            Cfg.apply(pi_, False)
            gdi = Roll.newDoc("Tool_Pickaxe_Mithril", 2, True, "admin")
            gsi = Data.put(IS("Tool_Pickaxe_Mithril", 1), gdi, U1)
            check(bool(Data.isGear("Tool_Pickaxe_Mithril")) and int(gsi.getQualityIndex()) == 62 and namehex(gsi) == ["#ff55ff"],
                  "AB4 (review finding 4): a tool made gear by gear.include keeps 0.1.3's rarity quality (Rare 62): q=%d %s"
                  % (int(gsi.getQualityIndex()), namehex(gsi)))
        finally:
            fq_.set(None, oldqs)
            Defs.QIDX = oldq
            Defs.QMISS = oldm
            Cfg.apply(Props(), False)
    print("AB4. tooltip lines done")

    # ---- AB5. gear:fn:sig includes the level (spec 8: the AH shows "rolls differ" for a Lv 4 and a Lv 9 wand)
    def jhash(s_):
        h_ = 0
        for ch_ in s_:
            h_ = (31 * h_ + ord(ch_)) & 0xFFFFFFFF
        return h_

    def mdoc(d_):
        m_ = BD()
        m_.put("SkyyGear", d_)
        return m_

    fs_ = Fn(5)
    sg = lambda d_: str(fs_.apply(OAb(["Weapon_Wand_Wood", mdoc(d_)])))
    w1s = wold.clone()
    w1s.put("lvl", BI2(1))
    exp4 = "Weapon_Wand_Wood|%d|normal|true|%s|4" % (-2147483648, str(Data.mods(w4_).toString()))
    check(sg(w4_) != sg(w9_) and sg(w4_) == sg(w4_.clone()) and sg(wold) == sg(w1s)
          and sg(w4_) == format(jhash(exp4), "x") + format(len(exp4), "x"),
          "AB5: gear:fn:sig differs for Lv 4 / Lv 9, equal for equal items (an unstamped Lv 1 = a stamped Lv 1); = hash of id|quality|rarity|identified|mods|level")
    print("AB5. gear:fn:sig done")

    # ---- AB6. /gear relevel: stamped items move into today's band; unstamped follow the table; /gear level ones stay
    if inv_ok:
        ir_ = Inv()
        c10 = Data.legacy("Weapon_Sword_Copper")
        c10.put("lvl", BI2(10))
        c25 = Data.legacy("Weapon_Sword_Copper")
        c25.put("lvl", BI2(25))
        c25.put("mods", Roll.rollMods("Weapon_Sword_Copper", 0, 2, 18))
        cad = Data.legacy("Weapon_Sword_Copper")
        cad.put("lvl", BI2(60))
        cad.put("lvlA", BB2(True))
        rdoc = BD()
        rdoc.append("dmg", BI2(5))
        ir_.getHotbar().setItemStackForSlot(0, Data.put(IS("Weapon_Sword_Copper", 1), c10, U2))
        ir_.getStorage().setItemStackForSlot(3, Data.put(IS("Weapon_Sword_Copper", 1), c25, U2))
        ir_.getBackpack().setItemStackForSlot(1, Data.put(IS("Weapon_Sword_Copper", 1), Data.legacy("Weapon_Sword_Copper"), U2))
        ir_.getArmor().setItemStackForSlot(0, Data.put(IS("Weapon_Sword_Copper", 1), cad, U2))
        ir_.getTools().setItemStackForSlot(0, IS("Weapon_Sword_Copper", 1).withMetadata("SkyyRolls", rdoc))
        ir_.getUtility().setItemStackForSlot(0, IS("Ingredient_Bar_Iron", 5))
        mods25 = str(Data.mods(c25).toString())
        Cfg.apply(p2_, True)               # Copper 12-20 now
        sb1 = SB()
        r1_ = [int(x_) for x_ in Admin.relevelInv(ir_, U2, sb1)]
        g_ = lambda c3, sl: Data.gearDoc(c3.getItemStack(sl).getMetadata())
        check(r1_ == [4, 2, 1, 1] and str(sb1.toString()) == "Sword Copper 10 -> 12, Sword Copper 25 -> 20",
              "AB6: relevel: 4 stamped / unstamped gear items checked, 2 re-stamped (10 -> 12, 25 -> 20), 1 kept (/gear level), 1 unstamped: %s %s" % (r1_, sb1))
        check(int(g_(ir_.getHotbar(), 0).getInt32("lvl").getValue()) == 12 and int(g_(ir_.getStorage(), 3).getInt32("lvl").getValue()) == 20
              and str(Data.mods(g_(ir_.getStorage(), 3)).toString()) == mods25 and int(g_(ir_.getArmor(), 0).getInt32("lvl").getValue()) == 60
              and not g_(ir_.getBackpack(), 1).containsKey("lvl") and int(Data.state(ir_.getTools().getItemStack(0).getMetadata())) == 2
              and int(ir_.getUtility().getItemStack(0).getQuantity()) == 5, "AB6: the modifiers stay; /gear level 60 stays; the unstamped one, the SkyyRolls item and the plain item are untouched")
        sb2 = SB()
        r2_ = [int(x_) for x_ in Admin.relevelInv(ir_, U2, sb2)]
        check(r2_ == [4, 0, 1, 1] and str(sb2.toString()) == "", "AB6: a second relevel changes nothing")
        check(str(Admin.relevelText("tester", Admin.relevelInv(ir_, U2, SB()), SB())).startswith("relevel of tester: 4 gear item(s) checked, 0 re-stamped"),
              "AB6: the admin message")
        Cfg.apply(Props(), False)
    else:
        check(False, "AB6: no bare Inventory - relevel could not be tested")
    print("AB6. /gear relevel done")

    # ---- AB7. migrate02 on a scratch COPY of the live config.properties (read only source) and on derived cases
    BDM, BDID = str(Cfg.BD_MARK), str(Cfg.BD_MARK_ID)
    ROWC, ROWL = [str(x_) for x_ in Cfg.BD_ROWC], [str(x_) for x_ in Cfg.BD_ROWL]
    ROWK = [str(x_) for x_ in Cfg.BD_ROWK]
    NEWB = dict((t_.lower(), "%d,%d" % (s_, c2)) for t_, s_, c2 in ALLB)
    OLDL = dict((t_.lower(), v_) for t_, v_ in OLDT.items())
    SPELL = dict((t_.lower(), t_) for t_, _s, _c in ALLB)

    def exp02(t, skip=()):
        """the expected update, built independently: each 'level.material.<E>=<old 0.1.3 default>' line (E any case) -> the band, an
        Armor_Copper line after the Copper line when the file has none, the block (marker + the missing settings) after the last
        level.material line; every other line kept; line endings kept"""
        nl_ = "\r\n" if "\r\n" in t else "\n"
        ls_ = t.split(nl_)
        pr_ = props(t)
        out_ = []
        last_mat, cu_at = -1, -1
        for l_ in ls_:
            m_ = re.match(r"^level\.material\.([A-Za-z_]+)=(.*)$", l_)
            if m_ and m_.group(1).lower() in OLDL and m_.group(2) == OLDL[m_.group(1).lower()] and m_.group(1).lower() not in skip:
                out_.append("level.material.%s=%s" % (m_.group(1), NEWB[m_.group(1).lower()]))
            else:
                out_.append(l_)
            if m_:
                last_mat = len(out_) - 1
                if m_.group(1).lower() == "copper":
                    cu_at = len(out_) - 1
        blk_ = [BDM]
        for k2, c3, l3 in zip(ROWK, ROWC, ROWL):
            if k2 not in pr_:
                blk_ += [c3, l3]
        has_arm = any(k_.lower() == "level.material.armor_copper" for k_ in pr_)
        out_[last_mat + 1:last_mat + 1] = blk_
        if not has_arm:
            out_[cu_at + 1:cu_at + 1] = ["level.material.Armor_Copper=1,18"]
        return nl_.join(out_)

    def info02(t, skip=()):
        pr_ = props(t)
        parts_ = []
        for t_, _s, _c in ALLB:
            if t_ == "Armor_Copper":
                continue
            ks_ = [k_ for k_ in pr_ if k_.lower() == ("level.material." + t_).lower()]
            if ks_ and pr_[ks_[-1]] == OLDT[t_] and t_.lower() not in skip:
                parts_.append("%s %s -> %d-%d" % (ks_[-1][15:], OLDT[t_], _s, _c))
        if not any(k_.lower() == "level.material.armor_copper" for k_ in pr_):
            parts_.append("added Armor_Copper 1-18")
        add_ = [k_ for k_ in ROWK if k_ not in pr_]
        return ("config.properties updated to the 0.2 level bands: " + ", ".join(parts_) + " (the old file is in config-history; "
                "Server Setup -> Changes can undo each band)" + ("; new settings with their defaults: " + ", ".join(add_) if add_ else ""))

    live02 = LIVE_NOW
    if live02 is not None and BDID.encode("ascii") in live02:
        print("AB7. note: the live file already has the 0.2 bands marker - the live-copy case runs on its pre-0.2 History copy")
        live02, where2 = hist_copy("before the 0.2 level bands")      # review of 0.2 finding 6: live config-history, then the backups
        check(live02 is not None, "AB7: a 'before the 0.2 level bands' History copy exists: searched %s" % where2)
    if live02 is not None:
        lt2 = live02.decode("latin-1")
        check(b"SkyyGear 0.1.3 level families" in live02 and BDID.encode("ascii") not in live02, "AB7: the live copy is a 0.1.3 file (its marker, no 0.2 marker)")
        d, f = bcase("a-live", live02)
        hp_, lp_ = baks(d), clog(d)
        res = str(Cfg.migrate02())
        got2 = rb(f)
        check(got2 == exp02(lt2).encode("latin-1"), "AB7(a): the live copy -> every untouched default row a band (value text only), Armor_Copper after "
              "Copper, the marker + 6 settings after the last band row, every other byte kept")
        check(res.split("\n") == [info02(lt2)], "AB7(a): one INFO line: %r" % res[:300])
        print("AB7. INFO line the live file produces: [SkyyGear] " + res[:200] + " ...")
        po2, pn2 = props(lt2), props(got2.decode("latin-1"))
        chk_ = [k_ for k_ in po2 if pn2.get(k_) != po2[k_]]
        check(all(k_.startswith("level.material.") and pn2[k_] == NEWB[k_[15:].lower()] for k_ in chk_) and len(chk_) == 69
              and sorted(set(pn2) - set(po2)) == sorted(["level.material.Armor_Copper"] + ROWK) and pn2["level.material.Armor_Copper"] == "1,18",
              "AB7(a): only the 69 default rows changed (to their bands); new keys: Armor_Copper 1,18 + the 6 settings (%d changed)" % len(chk_))
        b2_ = baks(d)
        ix2_ = idx(d)
        check(len(b2_) == len(hp_) + 1 and rb(os.path.join(d, "config-history", b2_[-1])) == live02
              and ix2_[-1].split("\t")[3:] == ["SkyyGear 0.2", "before the 0.2 level bands"], "AB7(a): History: one new copy = the old bytes, named 'before the 0.2 level bands'")
        cl2 = clog(d)
        want2 = [["SkyyGear 0.2", "-", "update", "level.material[%s]" % t_, "%s|%d" % (OLDT[t_], min(int(OLDT[t_]) + 7, 49)), "%d|%d" % (s_, c2), "ok"]
                 for t_, s_, c2 in ALLB if t_ != "Armor_Copper"] + [["SkyyGear 0.2", "-", "update", "level.material[Armor_Copper]", "(none)", "1|18", "ok"]]
        check(cl2[:len(lp_)] == lp_ and [l_.split("\t")[1:] for l_ in cl2[len(lp_):]] == want2
              and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", l_.split("\t")[0]) for l_ in cl2[len(lp_):]),
              "AB7(a): 70 config-changes.log lines (69 bands: old = what the old number means in 0.2 'N|N+7', so Undo goes through the "
              "2-column table; Armor_Copper old '(none)' = Undo removes it), the earlier lines kept")
        Cfg.load()
        check(str(Cfg.matText()) == FRESH_TXT and bool(Cfg.PART_LEVELS) and int(Cfg.BAND_W) == 8 and int(Cfg.GATE_FLOOR) == 1
              and str(Cfg.CRAFT_FROM) == "gate" and str(Cfg.CRAFT_BELOW) == "min" and str(Cfg.CRAFT_SKILL) == "",
              "AB7(a): the loader reads Skyy's bands + the six settings (= a fresh 0.2 file): %s" % str(Cfg.matText()))
        Cfg.LEVEL_DEFAULT = 77
        check(all(bandj(i_) == pyband(i_) for i_ in GEAR_AZ + TOOLS_AZ) and bandj("Armor_Copper_Chest") == (1, 18, 1),
              "AB7(a): every vanilla id gets Skyy's band from the updated live file (copper armor 1-18)")
        Cfg.LEVEL_DEFAULT = 0
        check(props(got2.decode("latin-1")) == props(shape02(zdt3)), "AB7(a): the updated live file holds every value of a fresh 0.2 file (0.2.1: without the 0.2.1 block - migrate021 adds it, section AC)")
        # (b) the second start changes nothing
        check(str(Cfg.migrate011()) == "" and str(Cfg.migrateStat011()) == "" and str(Cfg.migrate012()) == "" and str(Cfg.migrate013()) == ""
              and str(Cfg.migrate02()) == "" and rb(f) == got2 and len(baks(d)) == len(b2_) and len(clog(d)) == len(cl2),
              "AB7(b): a second start changes nothing (file, History, log)")
        # (c) CRLF
        d, f = bcase("c-crlf", lt2.replace("\n", "\r\n").encode("latin-1"))
        rc_ = str(Cfg.migrate02())
        gc2 = rb(f)
        check(gc2 == exp02(lt2.replace("\n", "\r\n")).encode("latin-1") and gc2.replace(b"\r\n", b"\n") == got2 and rc_ == res,
              "AB7(c): a CRLF file gets the same update, every line still ends CRLF")
        # (d) values Skyy changed are kept + noted; Armor_Copper typed by hand: exactly 1 = the old advice -> 1,18, anything else kept
        td2 = lt2.replace("\nlevel.material.Copper=10\n", "\nlevel.material.Copper=12\nlevel.material.Armor_Copper=1\n").replace(
            "\nlevel.material.Stone=5\n", "\nlevel.material.Stone=6,9\n")
        check(td2.count("level.material.Copper=12") == 1 and "level.material.Stone=6,9" in td2, "AB7(d): test file: Copper 12, Armor_Copper 1, Stone 6,9")
        d, f = bcase("d-custom", td2.encode("latin-1"))
        rd2 = str(Cfg.migrate02()).split("\n")
        exd = exp02(td2, skip=("copper",)).replace("\nlevel.material.Armor_Copper=1\n", "\nlevel.material.Armor_Copper=1,18\n")
        check(rb(f) == exd.encode("latin-1"), "AB7(d): Copper=12 and Stone=6,9 kept, Armor_Copper=1 -> 1,18 (no second Armor_Copper line), the rest updated")
        check(rd2[1:] == ["level.material.Copper=12 kept (custom) - the 0.2 default band is 10-18", "level.material.Stone=6,9 kept (custom) - the 0.2 default band is 5-12"]
              and "Armor_Copper 1 -> 1-18" in rd2[0] and "Copper 10" not in rd2[0] and "added Armor_Copper" not in rd2[0], "AB7(d): INFO + the kept notes: %s" % rd2)
        cld = [l_.split("\t") for l_ in clog(d)]
        check(["level.material[Armor_Copper]", "1|8", "1|18"] in [c4[4:7] for c4 in cld] and not any(c4[4] in ("level.material[Copper]", "level.material[Stone]") for c4 in cld),
              "AB7(d): the Armor_Copper rewrite is logged (old 1|8), the kept rows are not")
        Cfg.load()
        check(bandj("Weapon_Sword_Copper") == (12, 19, 1) and bandj("Armor_Copper_Legs") == (1, 18, 1) and bandj("Weapon_Sword_Stone_Trork") == (6, 9, 1),
              "AB7(d): the loader: Copper 12 = 12-19 (the width rule), copper armor 1-18, Stone 6-9")
        td3 = lt2.replace("\nlevel.material.Copper=10\n", "\nlevel.material.Copper=10\nlevel.material.ARMOR_copper=3\n")
        d, f = bcase("d-armor3", td3.encode("latin-1"))
        rd3 = str(Cfg.migrate02()).split("\n")
        check("level.material.ARMOR_copper=3 kept (custom) - the 0.2 default band is 1-18" in rd3 and "level.material.ARMOR_copper=3\n" in rb(f).decode("latin-1")
              and "Armor_Copper=1,18" not in rb(f).decode("latin-1"), "AB7(d): Armor_Copper=3 (any case) is Skyy's value: kept, nothing added")
        # (e) a new setting already in the file is kept (and the old one-number Undo value uses the file's own width)
        te_ = lt2.replace("\nlevel.vanilla=true", "\npart.levels=false\nlevel.bandWidth=5\nlevel.vanilla=true")
        d, f = bcase("e-keys", te_.encode("latin-1"))
        re_ = str(Cfg.migrate02()).split("\n")
        cle = [l_.split("\t") for l_ in clog(d)]
        check("part.levels is already in the file - kept" in re_ and "level.bandWidth is already in the file - kept" in re_
              and "new settings with their defaults: level.gateFloor, craft.levelFrom, craft.belowBand, craft.weaponSkill" in re_[0]
              and ["level.material[Copper]", "10|14", "10|18"] in [c4[4:7] for c4 in cle], "AB7(e): settings already there are kept + noted; the Undo value uses width 5")
        Cfg.load()
        check(not bool(Cfg.PART_LEVELS) and int(Cfg.BAND_W) == 5, "AB7(e): the loader keeps part.levels=false, bandWidth 5")
        # (f) Undo through the config kit (what SkyyMenu sends): tset back to the logged old value / remove the added row
        d, f = bcase("f-kit", live02)
        Cfg.migrate02()
        Cfg.load()
        CfgPubB = J("CfgPub")
        CfgPubB.start(Paths.get(os.path.dirname(d)), None)
        fnb = bridge.get("config:fn:SkyyGear")
        lgb = [str(x) for x in fnb.apply(OAb(["log", Integer.valueOf(200)]))]
        check(sum(1 for l_ in lgb if "\tSkyyGear 0.2\t" in l_ and "\tupdate\tlevel.material[" in l_ and l_.endswith("\tok")) == 70,
              "AB7(f): the kit's log op lists the 70 band lines as ok lines (SkyyMenu offers Undo)")
        ksb = fnb.apply(OAb(["keys", "level.material", ""]))
        kdb = dict(zip([str(x) for x in ksb[0]], [str(x) for x in ksb[2]]))
        check(kdb.get("Copper") == "10|18" and kdb.get("Armor_Copper") == "1|18" and kdb.get("Prisma") == "45|49" and len(kdb) == 70,
              "AB7(f): Server Setup lists the 70 band rows as Min | Cap")
        ua_ = fnb.apply(OAb(["tset", "level.material", "Copper", "10|17", None, "console", "yes", "console"]))
        ub_ = fnb.apply(OAb(["remove", "level.material", "Armor_Copper", None, "console", "yes", "console"]))
        CfgPubB.flush()
        kt5 = rb(f).decode("latin-1")
        check(str(ua_[0]) == "ok" and str(ub_[0]) == "ok" and "\nlevel.material.Copper=10,17\n" in kt5 and "Armor_Copper" not in kt5.replace(BDM, "")
              and bandj("Armor_Copper_Chest") == (10, 17, 1), "AB7(f): Undo of a band (tset 10|17) and of the added Armor_Copper (remove) apply at once")
        check(str(Cfg.migrate02()) == "" and rb(f).decode("latin-1") == kt5, "AB7(f): the next start never adds Armor_Copper back (the marker)")
        # (g) History cannot be written -> WARN, untouched; the next start updates
        d, f = bcase("g-nohist", live02)
        open(os.path.join(d, "config-history"), "w").write("x")
        Log.FILE = Paths.get(os.path.join(d, "gear.log"))
        check(str(Cfg.migrate02()) == "" and rb(f) == live02, "AB7(g): History blocked -> the file stays untouched")
        Log.flush()
        gl2 = ""
        for _w in range(30):
            gl2 = open(os.path.join(d, "gear.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "gear.log")) else ""
            if "NOT updated to the 0.2 level bands" in gl2:
                break
            time.sleep(0.1)
        check("NOT updated to the 0.2 level bands" in gl2 and "the next start tries again" in gl2, "AB7(g): one WARN says why")
        os.remove(os.path.join(d, "config-history"))
        check(str(Cfg.migrate02()) == res and rb(f) == got2, "AB7(g): the next start updates")
        Log.FILE = None
    else:
        check(False, "AB7: no live config.properties to copy")
    # (h) no file / the fresh 0.2 file never updates
    d, f = bcase("h-fresh", None)
    check(str(Cfg.migrate02()) == "" and not os.path.exists(f), "AB7(h): no file -> nothing written")
    Cfg.load()
    check(rb(f) == zdt3.encode("utf-8") and str(Cfg.migrate02()) == "" and Cfg.bdUpdate(zdt3) is None and not baks(d), "AB7(h): the fresh 0.2 file never updates")
    # (i) a 0.1 file (the live file's pre-0.1.1 History copy, section X) through all five updates in the setup order = a fresh 0.2 file
    if live is not None:
        d, f = bcase("i-from01", live)
        r5_ = [str(Cfg.migrate011()), str(Cfg.migrateStat011()), str(Cfg.migrate012()), str(Cfg.migrate013()), str(Cfg.migrate02())]
        check(all(x_ != "" for x_ in r5_) and props(rb(f).decode("latin-1")) == props(shape02(zdt3)) and len(baks(d)) == 5,
              "AB7(i): the 0.1 file -> all five one-time updates run once (5 History copies) and it holds every value of a fresh 0.2 file")
    # (j) the pure text step on edge cases
    LVHb, LVMb = str(Cfg.LV_HEAD), str(Cfg.LV_MARK)
    BLK2 = "\n".join([BDM] + [x_ for p3 in zip(ROWC, ROWL) for x_ in p3])
    ARM = "level.material.Armor_Copper=1,18"

    def bu(t):
        r_ = Cfg.bdUpdate(t)
        return None if r_ is None else str(r_[0])

    check(bu("a=1\n" + LVHb + "\n" + LVMb + "\nb=2\n") == "a=1\n" + LVHb + "\n" + LVMb + "\n" + ARM + "\n" + BLK2 + "\nb=2\n",
          "AB7(j): no level.material line -> Armor_Copper + the block right under the 0.1.1 marker")
    check(bu("a=1\nb=2") == "a=1\nb=2\n" + ARM + "\n" + BLK2 and bu("") == ARM + "\n" + BLK2 + "\n", "AB7(j): no anchor -> the end of the file")
    check(bu("level.material.Copper=10\nlevel.material.Iron=15\nx=1\n") == "level.material.Copper=10,18\n" + ARM + "\nlevel.material.Iron=15,23\n" + BLK2 + "\nx=1\n",
          "AB7(j): Armor_Copper right after Copper, the block after the last band row")
    check(bu("level.material.copper = 10\nlevel.material.IRON:15   \n") == "level.material.copper = 10,18\n" + ARM + "\nlevel.material.IRON:15,23\n" + BLK2 + "\n",
          "AB7(j): any case, ' = ' / ':' separators, trailing spaces: the value text only")
    BSL = chr(92)
    t_ = "a=1\nlevel.material.Copper=10" + BSL + "\n"
    r_ = bu(t_)
    check(r_ == "a=1\n" + ARM + "\n" + BLK2 + "\nlevel.material.Copper=10" + BSL + "\n" and props(r_).get("level.material.Copper") == props(t_).get("level.material.Copper"),
          "AB7(j): a continued Copper entry at the end stays as it was (kept) and nothing is appended into it (the 0.1.1 finding 4 trap)")
    check(Cfg.bdUpdate("  # SkyyGear 0.2 level bands old\nlevel.material.Iron=15\n") is None, "AB7(j): a comment with the marker id = done")
    r_ = bu("note=SkyyGear 0.2 level bands\nlevel.material.Iron=15\n")
    check(r_ is not None and "level.material.Iron=15,23" in r_, "AB7(j): the marker id inside a value does not count")
    r_ = bu("#level.material.Copper=10\nlevel.material.Iron=15\n")
    check(r_ == "#level.material.Copper=10\nlevel.material.Iron=15,23\n" + ARM + "\n" + BLK2 + "\n", "AB7(j): a commented row is no row (Armor_Copper still added)")
    r_ = bu("level.material.Copper=10\nlevel.material.Copper=11\n")
    check(r_ == "level.material.Copper=10\nlevel.material.Copper=11\n" + ARM + "\n" + BLK2 + "\n",
          "AB7(j): the LAST line wins: Copper 11 = custom, nothing rewritten (Armor_Copper after the last Copper line)")
    r_ = bu("level.material.Copper=11\nlevel.material.copper=10\n")
    check(r_ == "level.material.Copper=11\nlevel.material.copper=10,18\n" + ARM + "\n" + BLK2 + "\n", "AB7(j): the last line holds the default -> only lines with the default are rewritten")
    # (k) 1200 random files: Properties = the old keys (each untouched default -> its band) + the missing Armor_Copper / settings, the next
    # pass does nothing (entries spelled one way each; the case rules are the fixed cases above)
    import random as _rnd2
    rg2 = _rnd2.Random(2)
    pcs = ["a=1", "level.material.Copper=10", "level.material.Copper=12", "level.material.Wood=0", "level.material.Wool=5", "level.material.Wool=5,12",
           "level.material.Armor_Copper=1", "level.material.Armor_Copper=3", "part.levels=false", "level.bandWidth=6", "#c", "! d", "", "k" + BSL,
           "  v", "x:y", LVHb, LVMb, "level.material.Iron 15", "level.material.Iron=9" + BSL, "z=" + BSL + BSL, "  ", "level.item.Weapon_Sword_Iron=3"]
    badk = []
    for _n in range(1200):
        ls_ = [rg2.choice(pcs) for _ in range(rg2.randint(0, 10))]
        t_ = ("\r\n" if rg2.random() < 0.3 else "\n").join(ls_) + ("" if rg2.random() < 0.3 else "\n")
        r_ = bu(t_)
        if r_ is None:
            badk.append(("none", t_))
            continue
        po_, pn_ = props(t_), props(r_)
        w_ = dict(po_)
        for k_ in po_:
            if k_.startswith("level.material.") and k_[15:].lower() in OLDL and po_[k_] == OLDL[k_[15:].lower()]:
                w_[k_] = NEWB[k_[15:].lower()]
        if not any(k_.lower() == "level.material.armor_copper" for k_ in po_):
            w_["level.material.Armor_Copper"] = "1,18"
        for k2, l3 in zip(ROWK, ROWL):
            if k2 not in po_:
                w_[k2] = l3.split("=", 1)[1]
        if pn_ != w_ or Cfg.bdUpdate(r_) is not None:
            badk.append(("props", t_))
    check(not badk, "AB7(k): 1200 random files vs java.util.Properties (%d bad, first %r)" % (len(badk), badk[:1]))
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    print("AB7. migrate02 done")

    # ---- AB8. the new wand / staff recipes (Q&A R1): decode through the engine's own codec, = the same material's shortbow recipe
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    zj_ = zipfile.ZipFile(jar)
    RFILES = sorted(n_ for n_ in zj_.namelist() if n_.startswith("Server/Item/Recipes/"))
    MODEL = {"Weapon_Wand_Wood": "Weapon_Shortbow_Crude", "Weapon_Staff_Wood": "Weapon_Shortbow_Crude", "Weapon_Staff_Copper": "Weapon_Shortbow_Copper",
             "Weapon_Staff_Iron": "Weapon_Shortbow_Iron", "Weapon_Staff_Thorium": "Weapon_Shortbow_Thorium", "Weapon_Staff_Cobalt": "Weapon_Shortbow_Cobalt",
             "Weapon_Staff_Adamantite": "Weapon_Shortbow_Adamantite", "Weapon_Staff_Mithril": "Weapon_Shortbow_Mithril"}
    # independent: which magic ids exist per material of Skyy's R1 list (Wood, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril)
    mag_ = sorted(f2 + m2 for f2 in ("Weapon_Wand_", "Weapon_Spellbook_", "Weapon_Staff_") for m2 in ("Wood", "Copper", "Iron", "Thorium", "Cobalt",
                                                                                                   "Adamantite", "Mithril") if (f2 + m2) in AZJ)
    check(mag_ == sorted(MODEL) and RFILES == sorted("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_%s.json" % o_ for o_ in MODEL),
          "AB8: one recipe file per magic id that exists in Skyy's materials (no material spellbook exists; only the Wood wand): %s" % RFILES)

    def dec(txt, key):
        ei_ = AEI(Paths.get(key + ".json"), ADT(CRR.class_, key, None))
        try:
            o_ = CRR.CODEC.decodeJson(RJR.fromJsonString(txt), ei_)
        except Exception as e_:
            return None, str(e_)[:200]
        vr_ = ei_.getValidationResults()
        bad3 = []
        if vr_.hasFailed():
            bad3.append("validation failed: %s" % ([str(x_) for x_ in vr_.getResults()] if vr_.getResults() is not None else "?"))
        if len(list(ei_.getUnknownKeys())) > 0:
            bad3.append("unknown keys %s" % [str(x_) for x_ in ei_.getUnknownKeys()])
        return o_, "; ".join(bad3)

    def flat(o_):
        return {"in": [(None if m_.getItemId() is None else str(m_.getItemId()), None if m_.getResourceTypeId() is None else str(m_.getResourceTypeId()),
                        int(m_.getQuantity())) for m_ in o_.getInput()],
                "bench": [(str(b_.type), str(b_.id), None if b_.categories is None else [str(c_) for c_ in b_.categories], int(b_.requiredTierLevel))
                          for b_ in (o_.getBenchRequirement() or [])],
                "t": float(o_.getTimeSeconds()), "know": bool(o_.isKnowledgeRequired()), "mem": int(o_.getRequiredMemoriesLevel())}

    rec_ok = []
    arm_n = [0]
    for rf3 in RFILES:
        key3 = os.path.basename(rf3)[:-5]
        out3 = key3[len("SkyyGear_Recipe_"):]
        o_, why_ = dec(zj_.read(rf3).decode("utf-8"), key3)
        mo_, mwhy = dec(json.dumps(azget(MODEL[out3], "Recipe")), MODEL[out3] + "_Recipe_Generated_0")
        if o_ is None or why_ or mo_ is None or mwhy:
            rec_ok.append((key3, why_, mwhy))
            continue
        a3, b3 = flat(o_), flat(mo_)
        # review of 0.2 finding 5: the bows' developer-only Armory entry (DiagramCrafting, fixed slots per category) is the one thing
        # not copied - everything else equals the model bow's recipe
        arm_n[0] += 1 if any(x_[1] == "Armory" for x_ in b3["bench"]) else 0
        b3["bench"] = [x_ for x_ in b3["bench"] if x_[1] != "Armory"]
        po3 = o_.getPrimaryOutput()
        outs3 = [(str(m_.getItemId()), int(m_.getQuantity())) for m_ in o_.getOutputs()]
        if a3 != b3 or po3 is None or str(po3.getItemId()) != out3 or int(po3.getQuantity()) != 1 or outs3 != [(out3, 1)]:
            rec_ok.append((key3, a3, b3, outs3))
    check(not rec_ok and len(RFILES) == 8, "AB8: all 8 recipes decode through CraftingRecipe.CODEC (no validation failure, no unknown key) and equal the "
          "same material's shortbow recipe (inputs, bench + category + tier, time, knowledge) with the magic item x1 as the only output: %s" % rec_ok[:2])
    jw_ = json.loads(zj_.read("Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Weapon_Staff_Thorium.json").decode("utf-8"))
    check([(b_["Id"], b_.get("Categories"), b_.get("RequiredTierLevel")) for b_ in jw_["BenchRequirement"]]
          == [("Weapon_Bench", ["Weapon_Bow"], 2)] and jw_["Input"][0] == {"ItemId": "Ingredient_Bar_Thorium", "Quantity": 8},
          "AB8: e.g. the Thorium staff: Weapon Bench (Bow tab) tier 2, 8 Thorium bars - like the Thorium shortbow (no Armory entry)")
    benches8 = dict((n_, [(b_.get("Type"), b_.get("Id")) for b_ in json.loads(zj_.read(n_).decode("utf-8")).get("BenchRequirement") or []]) for n_ in RFILES)
    check(arm_n[0] == 7 and all(bl_ and all(t_ == "Crafting" and i_ != "Armory" for t_, i_ in bl_) for bl_ in benches8.values())
          and benches8["Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_Weapon_Wand_Wood.json"] == [("Crafting", "Workbench"), ("Crafting", "Weapon_Bench")],
          "AB8 (review finding 5): no recipe carries the developer-only Armory bench (7 of the 8 model bows have it); every recipe keeps "
          "its Crafting benches (the Wood wand: Workbench + Weapon Bench): %s" % benches8)
    # no duplicate ids: none of Assets.zip's recipe ids (item recipes <item>_Recipe_Generated_0 + standalone files), none of the SET jars'
    van_ids = set()
    van_outs = {}
    for n_ in azz.namelist():
        if n_.startswith("Server/Item/Recipes/") and n_.endswith(".json"):
            van_ids.add(os.path.basename(n_)[:-5])
    for i_, d3 in AZJ.items():
        if isinstance(d3, dict) and isinstance(d3.get("Recipe"), dict):
            van_ids.add(i_ + "_Recipe_Generated_0")
            van_outs.setdefault(i_, []).append(i_)
    set_ids = {}
    dsp = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
    for mod_, ver_ in re.findall(r'\("(Skyy[A-Za-z]+)", "([0-9.]+)"\)', dsp[dsp.index("SET = ["):dsp.index("PACK_THIRD_PARTY")]):
        jp3 = os.path.join(ROOT, mod_, "%s-%s.jar" % (mod_, ver_))
        if mod_ == "SkyyGear" or not os.path.isfile(jp3):
            continue
        with zipfile.ZipFile(jp3) as z3:
            for n_ in z3.namelist():
                if n_.startswith("Server/Item/Recipes/") and n_.endswith(".json"):
                    set_ids.setdefault(os.path.basename(n_)[:-5], mod_)
                elif n_.startswith("Server/Item/Items/") and n_.endswith(".json"):
                    try:
                        d4 = json.loads(z3.read(n_).decode("utf-8-sig"))
                    except Exception:
                        continue
                    if isinstance(d4, dict) and isinstance(d4.get("Recipe"), dict):
                        set_ids.setdefault(os.path.basename(n_)[:-5] + "_Recipe_Generated_0", mod_)
    mine_ = [os.path.basename(n_)[:-5] for n_ in RFILES]
    check(len(set(mine_)) == len(mine_) and not (set(mine_) & van_ids) and not (set(mine_) & set(set_ids)) and len(set_ids) > 50,
          "AB8: no duplicate recipe ids (none among themselves, none of Assets.zip's %d, none of the %d of the other SET jars)" % (len(van_ids), len(set_ids)))
    check(not [o_ for o_ in MODEL if o_ in van_outs], "AB8: none of the 8 items had a vanilla recipe (each gets exactly one: ours)")
    # 0.2.2: + the crit style asset Server/Entity/UI/SkyyGear_CritText.json (a NEW id, nothing of Assets.zip or another jar has it - AD3)
    nonrec = sorted(n_ for n_ in zj_.namelist() if n_.startswith("Server/") and not n_.startswith(("Server/Item/Qualities/", "Server/Languages/", "Server/Item/Recipes/SkyyGear/"))
                    and n_ != "Server/Entity/UI/SkyyGear_CritText.json")
    check(not nonrec and not any(n_.startswith("Server/Item/Items/") for n_ in zj_.namelist()),
          "AB8: no vanilla recipe changed - the jar overrides no item / recipe file (only its qualities, lang and its own recipe files): %s" % nonrec)
    van_staff = [n_ for n_ in azz.namelist() if n_.startswith("Server/Item/Recipes/") and any(("Recipe_" + o_) in n_ for o_ in MODEL)]
    check(not van_staff and all(("Server/Item/Recipes/SkyyGear/" + os.path.basename(n_)) not in set(azz.namelist()) for n_ in RFILES),
          "AB8: no recipe path of ours exists in Assets.zip")
    setlv(U1, "Divinity", 30)
    check(cl("Weapon_Staff_Iron") == 23 and cl("Weapon_Staff_Thorium") == 28 and cl("Weapon_Staff_Cobalt") == 30 and cl("Weapon_Staff_Adamantite") == 35
          and cl("Weapon_Wand_Wood") == 13 and all(bool(Roll.craftable(o_)) and bool(Data.isGear(o_)) for o_ in MODEL),
          "AB8: crafted ones get levels like any craft (Divinity 30: Iron staff 23, Thorium 28, Cobalt 30, Adamantite 35, Wood wand 13)")
    print("AB8. recipes done: %s" % ", ".join(mine_))

    # ---- AB9. class byte-compare 0.1.3 -> 0.2 (Z10's machinery): every difference must be one of the listed parts
    # (0.2.1 harness: AB9 stays the historical 0.1.3 -> 0.2 compare of the two shipped jars; the 0.2 -> 0.2.1 compare is AC9)
    jar013b = os.path.join(HERE, "SkyyGear-0.1.3.jar")
    jar02b = os.path.join(HERE, "SkyyGear-0.2.jar")
    if os.path.isfile(jar013b) and os.path.isfile(jar02b):
        pa4 = Pool(False)
        pa4.appendClassPath(jar013b)
        pa4.appendClassPath(B.SERVER_JAR)
        pa4.appendSystemPath()
        pb4 = Pool(False)
        pb4.appendClassPath(jar02b)
        pb4.appendClassPath(B.SERVER_JAR)
        pb4.appendSystemPath()
        n13b = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar013b).namelist() if n_.endswith(".class"))
        n02 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar02b).namelist() if n_.endswith(".class"))
        add4 = sorted(c_[len(PKG):] for c_ in set(n02) - set(n13b))
        gone4 = sorted(set(n13b) - set(n02))
        diffs4 = {}
        for cn_ in sorted(set(n13b) & set(n02)):
            ma_, mb_ = cls_members(pa4, cn_), cls_members(pb4, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs4[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        EXPECT02 = {
            # config kit (tools/skyycfg.py, regenerated from the rows): the six new rows + the Min | Cap table (CfgFile / CfgRows tables),
            # VERSION 0.1.3 -> 0.2 (CfgRows), the export header inlines the VERSION constant (CfgFn.opExport)
            "CfgFile": ["~<clinit>"],
            "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # the chat line to the /craft crafter (the bridge only knows the UUID)
            "Gear": ["+m tell(Ljava/util/UUID;Ljava/lang/String;Ljava/lang/String;)V"],
            # /gear read prints the band; /gear level marks lvlA; /gear relevel
            "GearAdmin": ["~m read(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/ItemStack;)V",
                          "+m relevelCmd(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/inventory/Inventory;Ljava/lang/String;)V",
                          "+m relevelInv(Lcom/hypixel/hytale/server/core/inventory/Inventory;Ljava/util/UUID;Ljava/lang/StringBuilder;)[I",
                          "+m relevelText(Ljava/lang/String;[ILjava/lang/StringBuilder;)Ljava/lang/String;",
                          "~m run(Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/lang/String;Ljava/lang/String;)V"],
            # the bands (tables, loader, default text, ready line), the six settings, migrate02 + its text step, the check hooks, the recipe ids
            "GearCfg": ["~<clinit>", "+f BAND_W", "+f BAND_W_DEF", "+f BD_CAP", "+f BD_MARK", "+f BD_MARK_ID", "+f BD_METALS", "+f BD_MIN", "+f BD_ROWC",
                        "+f BD_ROWK", "+f BD_ROWL", "+f BD_T", "+f BD_WHO", "+f BO_T", "+f BO_V", "+f CRAFT_BELOW", "+f CRAFT_FROM", "+f CRAFT_SKILL",
                        "+f GATE_FLOOR", "+f MATCAP", "+f MATNAME", "+f PART_LEVELS", "+f RCP_ID", "+f RCP_OUT", "+f VTOP",
                        "~m apply(Ljava/util/Properties;Z)V", "+m bandOf(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/String;",
                        "+m bdIdx(Ljava/lang/String;)I", "+m bdLog(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                        "+m bdNew(I)[I", "+m bdUpdate(Ljava/lang/String;)[Ljava/lang/Object;", "+m capOf(II)I",
                        "+m checkBand(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                        "+m checkCraftSkill(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "~m defaultsText()Ljava/lang/String;",
                        "+m levelText()Ljava/lang/String;", "~m matText()Ljava/lang/String;", "+m migrate02()Ljava/lang/String;",
                        "+m recipeText()Ljava/lang/String;"],
            # /gear relevel registered under /gear
            "GearCmd": ["~c ()V"],
            # the bench roll takes gear + gathering tools (craftable); the task logs the level + sends the craft note
            "GearCraftSys": ["~m handle(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"],
            "GearCraftTask": ["~m run()V"],
            # gear:fn:roll mode 8: craftable, the level once per craft, the requested-level element, the note; gear:fn:sig with the level
            "GearFn": ["~m apply(Ljava/lang/Object;)Ljava/lang/Object;"],
            # the gate floor in every gate state
            "GearGate": ["~m check(Ljava/util/UUID;Ljava/lang/String;Lorg/bson/BsonDocument;I)[Ljava/lang/Object;"],
            # bands (level() itself is byte-identical)
            "GearLevel": ["+m band(Ljava/lang/String;)[I", "+m bandWord(Ljava/lang/String;)Ljava/lang/String;", "+m entry(Ljava/lang/String;)Ljava/lang/String;",
                          "+m floor(I)I", "+m stamped(Lorg/bson/BsonDocument;)Z"],
            # lvl stamped before the roll (newDoc 5-arg), crafted at your level, the block reason, tools, reforge / identify stamp a missing lvl;
            # review of 0.2 finding 3: the craft note once per burst (noteDue + its time map NOTED / NOTE_MS, set up in <clinit>)
            "GearRoll": ["~<clinit>", "+f NOTED", "+f NOTE_MS", "+m noteDue(Ljava/util/UUID;Ljava/lang/String;J)Z",
                         "+m blockWhy(Ljava/lang/String;Ljava/util/UUID;)Ljava/lang/String;", "~m craftDoc(Ljava/lang/String;Ljava/util/UUID;)Lorg/bson/BsonDocument;",
                         "+m craftDoc(Ljava/lang/String;Ljava/util/UUID;I)Lorg/bson/BsonDocument;", "+m craftHave(Ljava/lang/String;Ljava/util/UUID;)I",
                         "+m craftLabel(Ljava/lang/String;Ljava/util/UUID;)Ljava/lang/String;", "+m craftLevel(Ljava/lang/String;Ljava/util/UUID;)I",
                         "+m craftNote(Ljava/lang/String;Ljava/util/UUID;)Ljava/lang/String;", "+m craftSkill(Ljava/lang/String;Ljava/util/UUID;)Ljava/lang/String;",
                         "+m craftable(Ljava/lang/String;)Z", "~m identify(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lorg/bson/BsonDocument;",
                         "~m newDoc(Ljava/lang/String;IZLjava/lang/String;)Lorg/bson/BsonDocument;",
                         "+m newDoc(Ljava/lang/String;IZLjava/lang/String;I)Lorg/bson/BsonDocument;",
                         "~m reforge(Ljava/lang/String;Lorg/bson/BsonDocument;)Lorg/bson/BsonDocument;",
                         "+m stampIfMissing(Ljava/lang/String;Lorg/bson/BsonDocument;)V", "+m weaponSkill(Ljava/lang/String;)Ljava/lang/String;"],
            # "Lv N - Requires <Skill> N" first; gear:fn:sig with the level; review of 0.2 finding 4: a plain tool keeps the item's own
            # quality + its colour (apply, ourQ, qualHex)
            "GearView": ["~m apply(Lcom/hypixel/hytale/server/core/inventory/ItemStack;Lorg/bson/BsonDocument;Ljava/util/UUID;)Lcom/hypixel/hytale/server/core/inventory/ItemStack;",
                         "+m ourQ(I)Z", "+m qualHex(I)Ljava/lang/String;",
                         "~m bridgeSig(Ljava/lang/String;ILorg/bson/BsonDocument;)Ljava/lang/String;",
                         "~m gateLine(Ljava/util/UUID;Ljava/lang/String;Lorg/bson/BsonDocument;I)[Ljava/lang/Object;",
                         "~m lines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/UUID;Ljava/util/ArrayList;Ljava/util/ArrayList;)V"],
            # migrate02, GearCraftPreSys registered, the ready line
            "SkyyGearPlugin": ["~m setup()V"]}
        check(add4 == ["GearCraftPreSys", "GearRelevelCmd", "GearRelevelTask"] and not gone4,
              "AB9: new classes = GearCraftPreSys (craft.belowBand block), GearRelevelCmd + GearRelevelTask (/gear relevel), none removed: %s / %s" % (add4, gone4))
        extra4 = dict((c_, [m_ for m_ in ms_ if m_ not in EXPECT02.get(c_, [])]) for c_, ms_ in diffs4.items())
        extra4 = dict((c_, ms_) for c_, ms_ in extra4.items() if ms_)
        miss4 = dict((c_, [m_ for m_ in ms_ if m_ not in diffs4.get(c_, [])]) for c_, ms_ in EXPECT02.items())
        miss4 = dict((c_, ms_) for c_, ms_ in miss4.items() if ms_)
        check(not extra4, "AB9: no difference outside the listed 0.2 parts: %s" % extra4)
        check(not miss4, "AB9: every listed part really differs (the list is exact): %s" % miss4)
        print("AB9. 0.1.3 -> 0.2 class compare: %d classes identical, %d with new parts, %d new" % (len(set(n13b) & set(n02)) - len(diffs4), len(diffs4), len(add4)))
        for c_ in sorted(diffs4):
            print("     %-16s %s" % (c_, ", ".join(re.sub(r"\(.*", "", m_) for m_ in diffs4[c_])))
        ea4 = [n_ for n_ in zipfile.ZipFile(jar013b).namelist() if not n_.endswith(".class")]
        eb4 = [n_ for n_ in zipfile.ZipFile(jar02b).namelist() if not n_.endswith(".class")]
        za4, zb4 = zipfile.ZipFile(jar013b), zipfile.ZipFile(jar02b)
        nd4 = sorted(n_ for n_ in set(ea4) | set(eb4) if n_ not in ea4 or n_ not in eb4 or za4.read(n_) != zb4.read(n_))
        check(nd4 == sorted(["manifest.json"] + RFILES), "AB9: non-class entries: manifest.json (version) + the 8 new recipe files only: %s" % nd4)
    else:
        check(False, "AB9: SkyyGear-0.1.3.jar / SkyyGear-0.2.jar not found - the class compare could not run")

    # ---- AB10. wiring (bytecode)
    su4 = mcode("SkyyGearPlugin", "setup")
    o4 = [su4.find("GearCfg.migrate013("), su4.find("GearCfg.migrate02("), su4.find("GearCfg.load(")]
    check(all(x_ >= 0 for x_ in o4) and o4 == sorted(o4), "AB10: setup(): migrate013 -> migrate02 -> load (%s)" % o4)
    check("GearCraftPreSys.<init>" in su4 and su4.count("registerSystem(") >= 7 and "GearCfg.levelText(" in su4 and "GearCfg.recipeText(" in su4,
          "AB10: setup registers GearCraftPreSys; the ready line names the level settings + the recipes")
    hs_ = mcode("GearCraftSys", "handle")
    hp_ = mcode("GearCraftPreSys", "handle")
    check("GearRoll.craftable(" in hs_ and "GearData.isGear(" not in hs_ and "GearRoll.blockWhy(" in hp_ and "setCancelled(" in hp_ and "CraftRecipeEvent$Pre" in hp_,
          "AB10: the bench roll takes gear + tools (craftable); the Pre system refuses only through blockWhy")
    check("GearRoll.craftLevel(" in mcode("GearFn", "apply") and "GearRoll.craftDoc((Ljava/lang/String;Ljava/util/UUID;I)" in mcode("GearFn", "apply")
          and "GearRoll.craftNote(" in mcode("GearCraftTask", "run") and "GearRoll.craftNote(" in mcode("GearFn", "apply"),
          "AB10: /craft (mode 8) computes the level once + stamps it on every item; both craft paths send the note")
    check("GearLevel.floor(" in mcode("GearGate", "check") and "GearLevel.level(" in mcode("GearView", "bridgeSig")
          and "GearRoll.stampIfMissing(" in mcode("GearRoll", "reforge") and "GearRoll.stampIfMissing(" in mcode("GearRoll", "identify"),
          "AB10: the gate floor in GearGate.check; the level in gear:fn:sig; reforge / identify stamp a missing level")
    ca4 = pool.get(PKG + "GearRelevelCmd").getDeclaredConstructors()[0]
    it4 = ca4.getMethodInfo().getCodeAttribute().iterator()
    cp4 = ca4.getMethodInfo().getConstPool()
    ops4 = []
    while it4.hasNext():
        p4 = it4.next()
        ops4.append(str(IP.instructionString(it4, p4, cp4)))
    ct4 = "\n".join(ops4)
    gc4 = pool.get(PKG + "GearCmd").getDeclaredConstructors()[0]
    it5 = gc4.getMethodInfo().getCodeAttribute().iterator()
    cp5 = gc4.getMethodInfo().getConstPool()
    ops5 = []
    while it5.hasNext():
        p5 = it5.next()
        ops5.append(str(IP.instructionString(it5, p5, cp5)))
    check("requirePermission(" in ct4 and "\"skyygear.admin\"" in ct4 and "setPermissionGroups(" in ct4 and "anewarray" in ct4
          and "GearRelevelCmd.<init>" in "\n".join(ops5) and "\"relevel\"" in mcode("GearAdmin", "run"),
          "AB10: /gear relevel is admin only (skyygear.admin + no permission groups), registered under /gear, dispatched by GearAdmin.run")
    for u_ in (U1, U2):
        bridge.remove("class:skill:" + str(u_))
        Gate.forget(u_)
    skills_off()
    Cfg.apply(Props(), False)
    print("AB. 0.2 per-item levels (stage 1) done")

    # ======================================================================================================================== AC 0.2.1
    # SkyyGear 0.2.1 = stages 2 + 3 of research/Gear-Levels-Wynn-Spec.md: weapon base damage + armor base stats by item level. Every new
    # code path is EXECUTED here against real engine classes (Damage, DamageCause, ItemStack, Item / ItemWeapon / ItemArmor, DamageBreakdown,
    # ResistanceModifier, ArmorResistanceModifiers, EntityStatMap / EntityStatValue / StaticModifier) - not only loaded: the real
    # GearHitSys.handle, the engine's own DamageSystems$ArmorDamageReduction.handle, GearArmorSys.handle, GearTrueSys.handle and SkyyMobs
    # 0.1's LevelDamage.handle run on a minimal ECS shim (a CommandBuffer / ArchetypeChunk subclass made here + the engine's static
    # singletons Universe / EntityModule / EntityStatsModule filled with never-constructed objects), so a member the JVM refuses at run time
    # (the SkyyUiProbe 0.3 IllegalAccessError lesson) fails a check here.
    import math as _m
    print("AC. 0.2.1 base stats by level")
    OAc = JArray(JObject)
    SysJ = JClass("java.lang.System")

    def acf(cls_name, name):
        f_ = JClass(cls_name).class_.getDeclaredField(name)
        f_.setAccessible(True)
        return f_

    def acalloc(cls_name):
        return UZ.allocateInstance(JClass(cls_name).class_)

    def rnd(x):
        return int(_m.floor(float(x) + 0.5))

    ENG = "com.hypixel.hytale.server.core."
    DCSc = JClass(ENG + "modules.entity.damage.DamageCause")
    DMGc = JClass(ENG + "modules.entity.damage.Damage")
    DENTc = JClass(ENG + "modules.entity.damage.Damage$EntitySource")
    DPRJc = JClass(ENG + "modules.entity.damage.Damage$ProjectileSource")
    RMODc = JClass(ENG + "modules.entity.damage.ResistanceModifier")
    RCTc = JClass(ENG + "modules.entity.damage.ResistanceModifier$ResistanceCalculationType")
    ADRc = JClass(ENG + "modules.entity.damage.DamageSystems$ArmorDamageReduction")
    IWPc = JClass(ENG + "asset.type.item.config.ItemWeapon")
    IARc = JClass(ENG + "asset.type.item.config.ItemArmor")
    IASc = JClass("com.hypixel.hytale.protocol.ItemArmorSlot")
    ESTc = JClass(ENG + "modules.entitystats.asset.EntityStatType")
    DSTc = JClass(ENG + "modules.entitystats.asset.DefaultEntityStatTypes")
    ESMc = JClass(ENG + "modules.entitystats.EntityStatMap")
    I2O = JClass("it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap")
    Base = J("GearBase")
    Hsys, Asys, Tsys = J("GearHitSys"), J("GearArmorSys"), J("GearTrueSys")

    # ---- AC0. the bare-JVM engine model for this section: damage causes, stat types, weapon breakdowns, armor assets
    # damage causes (the real DamageCause class through its public constructor) in an indexed asset map like the engine's
    CAUSES = [("Physical", None), ("Projectile", None), ("Fire", None), ("Ice", None), ("Poison", None), ("Fall", None), ("Bludgeoning", "Physical")]
    cause_obj = dict((c_, DCSc(c_, p_, True, False, False)) for c_, p_ in CAUSES)
    old_dcs_store = acf(DCSc.class_.getName(), "ASSET_STORE").get(None)
    acf(DCSc.class_.getName(), "ASSET_STORE").set(None, zstore(indexed(dict((c_, cause_obj[c_]) for c_, _p in CAUSES))))
    CIDX = dict((c_, int(DCSc.getAssetMap().getIndex(c_))) for c_, _p in CAUSES)
    check(sorted(CIDX.values()) == list(range(len(CAUSES))) and str(DCSc.getAssetMap().getAsset(JInt(CIDX["Projectile"])).getId()) == "Projectile",
          "AC0: the damage cause model answers (real DamageCause objects in an indexed asset map: %s)" % CIDX)

    # entity stat types (Health 0, Mana 1, Stamina 2) + DefaultEntityStatTypes pointing at them
    def stat_type(id_, init_, mx_):
        t_ = acalloc(ESTc.class_.getName())
        acf(ESTc.class_.getName(), "id").set(t_, id_)
        acf(ESTc.class_.getName(), "initialValue").setFloat(t_, JFloat(init_))
        acf(ESTc.class_.getName(), "min").setFloat(t_, JFloat(0.0))
        acf(ESTc.class_.getName(), "max").setFloat(t_, JFloat(mx_))
        return t_
    STYPES = [("Health", 100.0, 100.0), ("Mana", 50.0, 50.0), ("Stamina", 10.0, 10.0)]
    old_est_store = acf(ESTc.class_.getName(), "ASSET_STORE").get(None)
    est_map = indexed(dict((n_, stat_type(n_, a_, b_)) for n_, a_, b_ in STYPES))
    fz(ILT, "nextIndex").set(est_map, JClass("java.util.concurrent.atomic.AtomicInteger")(len(STYPES)))   # EntityStatMap.update() reads it
    acf(ESTc.class_.getName(), "ASSET_STORE").set(None, zstore(est_map))
    old_dst = [int(acf(DSTc.class_.getName(), f_).getInt(None)) for f_ in ("HEALTH", "MANA", "STAMINA")]
    for f_, v_ in (("HEALTH", 0), ("MANA", 1), ("STAMINA", 2)):
        acf(DSTc.class_.getName(), f_).setInt(None, JInt(v_))
    HP_I = int(DSTc.getHealth())
    check(HP_I == 0 and str(View.statName(0)) == "Health" and str(View.statName(1)) == "Mana", "AC0: the stat type model answers (Health = index %d)" % HP_I)

    # weapon damage breakdowns COMPUTED BY THE ENGINE: the Z3 model (real Interaction / RootInteraction / DamageEntityInteraction /
    # ProjectileInteraction objects from Assets.zip) gets each DamageCalculator's real numbers (Type, BaseDamage, RandomPercentageModifier
    # from the resolved JSON) and the engine's own WeaponDamageDataCollector.calculate(item, Primary) walks it - the same call
    # ItemModule.computeWeaponData makes at asset load, i.e. the data damageText and GearBase.maxEntry read in game
    DTYPEc = JClass(PI + "server.combat.DamageCalculator$Type")
    I2F = JClass("it.unimi.dsi.fastutil.ints.Int2FloatOpenHashMap")
    WDC = JClass(ENG + "asset.type.item.config.damageData.WeaponDamageDataCollector")
    calc_json = {}

    class Model2(Model):
        def mkcalc(s, c_, key):
            o_ = Model.mkcalc(s, c_, key)
            if o_ is not None:
                calc_json[key] = (o_, c_)
            return o_

    MZ2 = Model2()
    zitems2 = dict((i, MZ2.item(i)) for i in ALLW)
    nb_ = 0
    for key_, (o_, c_) in calc_json.items():
        bd_ = I2F()
        for k_i, (cn_, val_) in enumerate(sorted((c_.get("BaseDamage") or {}).items())):
            try:
                bd_.put(JInt(k_i), JFloat(float(val_)))
            except Exception:
                pass
        fz(DCALCz, "baseDamage").set(o_, bd_)
        fz(DCALCz, "type").set(o_, DTYPEc.DPS if str(c_.get("Type", "Absolute")).lower() == "dps" else DTYPEc.ABSOLUTE)
        fz(DCALCz, "randomPercentageModifier").setFloat(o_, JFloat(float(c_.get("RandomPercentageModifier", 0.0) or 0.0)))
        nb_ += 1
    fz(Inter, "ASSET_STORE").set(None, zstore(indexed(MZ2.inter)))
    fz(RootI, "ASSET_STORE").set(None, zstore(indexed(MZ2.roots)))
    dcf2 = DAMz()
    for k_, v_ in MZ2.cfgs.items():
        fz(DAMz, "assetMap").get(dcf2).put(k_, v_)
    fz(PJCz, "ASSET_STORE").set(None, zstore(dcf2))
    BRK = {}
    brk_fail = []
    for i_ in ALLW:
        try:
            b_ = WDC.calculate(zitems2[i_], ITY.Primary)
            BRK[i_] = [(None if e_.labelKey() is None else str(e_.labelKey()), float(e_.min()), float(e_.max())) for e_ in b_.entries()]
            w_ = IWPc()
            w_.setBasicDamageBreakdown(b_)
            fz(ItemZ, "weapon").set(zitems2[i_], w_)
        except Exception as ex_:
            brk_fail.append("%s: %s" % (i_, ex_))
    old_weapon_items = dict((k_, imap.get(k_)) for k_ in zitems2)
    for k_, v_ in zitems2.items():
        imap.put(k_, v_)
    Base.clear()

    def bmax(i_):
        return max([e_[2] for e_ in BRK.get(i_, [])] or [0.0])
    check(not brk_fail and len(BRK) == len(ALLW), "AC0: the engine's WeaponDamageDataCollector computed a breakdown for every vanilla + pack weapon "
                                                  "(%d / %d; %d damage calculators with their real numbers): %s" % (len(BRK), len(ALLW), nb_, brk_fail[:3]))
    # the breakdowns the spec quotes (spec 3.2 table, VERIFIED 2026-10-01 from Assets.zip): the engine's own numbers agree
    check(BRK.get("Weapon_Wand_Wood") == [(None, 6.0, 8.0)], "AC0: Wood wand basic breakdown = 6-8 (Skyy's screenshot: Damage Data Basic 6.0-8.0): %s" % BRK.get("Weapon_Wand_Wood"))
    check(bmax("Weapon_Sword_Crude") == 16.0 and min(e_[1] for e_ in BRK["Weapon_Sword_Crude"]) == 6.0,
          "AC0: Crude sword = 6 .. 16 (swings 6 / 6 / 11, thrust 16): %s" % BRK.get("Weapon_Sword_Crude"))
    check(bmax("Weapon_Staff_Wood") == 5.0 and bmax("Weapon_Staff_Iron") == 5.0, "AC0: plain staffs swing 5 in every material: %s / %s"
          % (BRK.get("Weapon_Staff_Wood"), BRK.get("Weapon_Staff_Iron")))
    print("AC0. engine breakdowns (largest entry): " + ", ".join("%s %g" % (i_[7:], bmax(i_)) for i_ in (
        "Weapon_Wand_Wood", "Weapon_Staff_Wood", "Weapon_Sword_Crude", "Weapon_Sword_Copper", "Weapon_Sword_Iron", "Weapon_Sword_Mithril",
        "Weapon_Shortbow_Crude", "Weapon_Shortbow_Iron", "Weapon_Battleaxe_Crude", "Weapon_Crossbow_Iron", "Weapon_Club_Crude", "Weapon_Club_Iron",
        "Weapon_Spellbook_Fire", "Weapon_Kunai")))

    # armor assets: real Item objects with a real ItemArmor (public constructor: slot, base damage resistance, Health stat modifiers) +
    # Physical / Projectile ResistanceModifier[] (Percent) + optional extra lines, the vanilla numbers (VERIFIED Assets.zip)
    PERC = RCTc.PERCENT
    ARMOR_AZ = {"Armor_Copper_Head": ("Head", 5, 0.036, None), "Armor_Copper_Chest": ("Chest", 9, 0.0648, None),
                "Armor_Copper_Legs": ("Legs", 7, 0.0504, None), "Armor_Copper_Hands": ("Hands", 4, 0.0288, None),
                "Armor_Iron_Chest": ("Chest", 17, 0.09, None), "Armor_Mithril_Chest": ("Chest", 24, 0.144, None),
                "Armor_Cloth_Wool_Chest": ("Chest", 17, 0.09, None), "Armor_Thorium_Chest": ("Chest", 22, 0.1152, ("Poison", 0.1)),
                "Armor_Cloth_Cindercloth_Head": ("Head", 9, 0.05, ("Mana", 10.0))}

    def armor_item(iid, slot_, hp_, res_, extra_):
        it_ = UZ.allocateInstance(ItemZ.class_)
        fz(ItemZ, "id").set(it_, iid)
        fz(ItemZ, "maxStack").setInt(it_, 1)
        sm_ = I2O()
        sm_.put(JInt(HP_I), JArray(SMO)([SMO(MTG.MAX, CAL.ADDITIVE, JFloat(float(hp_)))]))
        if extra_ is not None and extra_[0] == "Mana":
            sm_.put(JInt(1), JArray(SMO)([SMO(MTG.MAX, CAL.ADDITIVE, JFloat(float(extra_[1])))]))
        ar_ = IARc(IASc.valueOf(slot_), 0.0, sm_, None)
        dr_ = HashMap()
        dr_.put(cause_obj["Physical"], JArray(RMODc)([RMODc(PERC, JFloat(res_))]))
        dr_.put(cause_obj["Projectile"], JArray(RMODc)([RMODc(PERC, JFloat(res_))]))
        if extra_ is not None and extra_[0] == "Poison":
            dr_.put(cause_obj["Poison"], JArray(RMODc)([RMODc(PERC, JFloat(extra_[1]))]))
        fz(IARc, "damageResistanceValues").set(ar_, dr_)
        fz(ItemZ, "armor").set(it_, ar_)
        return it_
    old_armor_items = dict((k_, imap.get(k_)) for k_ in ARMOR_AZ)
    for k_, (s_, h_, r_, x_) in ARMOR_AZ.items():
        imap.put(k_, armor_item(k_, s_, h_, r_, x_))
    check(int(Base.slotIdx(Gear.item("Armor_Copper_Chest"))) == 1 and abs(float(Base.nativeHealth(Gear.item("Armor_Copper_Chest"))) - 9.0) < 1e-6
          and abs(float(Base.assetRes(Gear.item("Armor_Copper_Chest"), "Physical")) - 0.0648) < 1e-6
          and abs(float(Base.assetRes(Gear.item("Armor_Copper_Chest"), "Fire"))) < 1e-9,
          "AC0: GearBase reads the real ItemArmor: slot Chest, Health 9 (ADDITIVE StaticModifier), Physical 6.48 %% (Percent ResistanceModifier), no Fire")

    Cfg.apply(Props(), False)
    skills_off()
    for u_ in (U1, U2):
        bridge.remove("class:skill:" + str(u_))
        Gate.forget(u_)

    def doc(iid, lv_, mods_=None):
        d_ = Roll.newDoc(iid, 0, True, "admin", lv_)
        ar_ = JClass("org.bson.BsonArray")()
        for k_, v_ in (mods_ or []):
            ar_.add(Data.mod(k_, v_))
        d_.put("mods", ar_)
        return d_

    def gstack(iid, lv_, mods_=None):
        return Data.put(IS(iid, 1), doc(iid, lv_, mods_), U1)

    # ---- AC1. the Server Setup rows, the fresh default file, the loader, the check hooks
    keys1 = [str(k) for k in Rows.KEYS]
    rw = dict((str(k), (str(t), str(dd), str(fl), str(h), str(o))) for k, t, dd, fl, h, o in
              zip(Rows.KEYS, Rows.TYPES, Rows.DEFS, Rows.FLAGS, Rows.HELPS, Rows.OPTS))
    NEWK = ["part.base", "base.mode", "base.curve", "base.matBonus", "base.armorOn", "base.resCurve", "base.armor"]
    # (0.2.2: 57 + the six crit / vanilla-box rows = 63; section AD checks those)
    check(all(k_ in keys1 for k_ in NEWK) and len(keys1) == 63, "AC1: the seven 0.2.1 rows are in Server Setup (63 rows with 0.2.2's six): %s" % [k_ for k_ in NEWK if k_ not in keys1])
    check(rw["part.base"][0] == "bool" and rw["part.base"][1] == "true" and set(rw["part.base"][2].split(",")) == {"live", "part", "danger"}
          and rw["base.mode"][0] == "choice" and rw["base.mode"][1] == "shape" and rw["base.mode"][4] == "shape|Level x vanilla,off|Vanilla damage"
          and rw["base.curve"][:3] == ("text", "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0", "live,danger")
          and rw["base.matBonus"][:3] == ("dec", "0.3", "live,danger") and rw["base.armorOn"][:3] == ("bool", "true", "live,danger")
          and rw["base.resCurve"][:3] == ("text", "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0", "live,danger")
          and rw["base.armor"][0] == "table" and rw["base.armor"][4] == "dec;none;Health|Resist %",
          "AC1: row types / defaults / flags (part.base = a part switch with the confirm; every base row live + danger): %s" % [rw[k_][:3] for k_ in NEWK])
    check(all(rw[k_][3].endswith(PH) for k_ in ("base.curve", "base.matBonus", "base.resCurve", "base.armor"))
          and all(len(rw[k_][3]) <= 100 for k_ in NEWK), "AC1: the curve / bonus / armor rows say Placeholder; every help <= 100 characters")
    zdtA = str(Cfg.defaultsText())
    zlA = zdtA.split("\n")
    ia_ = zlA.index("level.armorNative=true")
    blockA = [str(Cfg.LS_MARK)] + [x_ for p_ in zip([str(x) for x in Cfg.LS_ROWC], [str(x) for x in Cfg.LS_ROWL]) for x_ in p_] + [str(Cfg.LS_TBLC)] + [str(x) for x in Cfg.LS_TBLL]
    check(zlA[ia_ + 1:ia_ + 1 + len(blockA)] == blockA and zlA[ia_ + 1 + len(blockA)] == "" and zdtA.count(str(Cfg.LS_MARK_ID)) == 1,
          "AC1: the fresh file carries the 0.2.1 block (marker, 6 settings with their help, the base.armor table) right under level.armorNative")
    # review of 0.2.1 nit: what a server owner reads in config.properties names no internal doc section ("spec 3.4" was in the table comment)
    check(not any(re.search(r"\bspec\b", x_, re.I) for x_ in blockA) and "default = the vanilla Copper row" in str(Cfg.LS_TBLC),
          "AC1: nit - the 0.2.1 block's comments name no internal doc section: %s" % [x_ for x_ in blockA if re.search(r"\bspec\b", x_, re.I)])
    pA = props(zdtA)
    check(pA.get("base.armor.Chest") == "9,6.48" and pA.get("base.armor.Hands") == "4,2.88" and pA.get("part.base") == "true" and pA.get("base.mode") == "shape",
          "AC1: the fresh file's values (base.armor.Chest 9,6.48 = the Copper chestplate)")
    Cfg.apply(Props(), False)
    check(bool(Cfg.PART_BASE) and str(Cfg.BASE_MODE) == "shape" and str(Cfg.BASE_CURVE) == "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0" and abs(float(Cfg.BASE_MAT) - 0.3) < 1e-12
          and bool(Cfg.BASE_ARMOR) and str(Cfg.BASE_RES) == "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0"
          and [float(x) for x in Cfg.BA_H] == [5.0, 9.0, 7.0, 4.0] and [float(x) for x in Cfg.BA_R] == [3.6, 6.48, 5.04, 2.88],
          "AC1: the built-in defaults (no file)")
    pp_ = Props()
    for k_, v_ in (("part.base", "false"), ("base.mode", "OFF"), ("base.curve", "1:1,2:9"), ("base.matBonus", "50"), ("base.armorOn", "no"),
                   ("base.resCurve", "garbage"), ("base.armor.chest", "12,7.5"), ("base.armor.Feet", "3,3"), ("base.armor.Head", "1,200")):
        pp_.setProperty(k_, v_)
    Cfg.apply(pp_, True)
    check(not bool(Cfg.PART_BASE) and str(Cfg.BASE_MODE) == "off" and str(Cfg.BASE_CURVE) == "1:1,2:9" and float(Cfg.BASE_MAT) == 10.0
          and not bool(Cfg.BASE_ARMOR) and str(Cfg.BASE_RES) == str(Cfg.RES_DEF) and [float(x) for x in Cfg.BA_H] == [5.0, 12.0, 7.0, 4.0]
          and [float(x) for x in Cfg.BA_R] == [3.6, 7.5, 5.04, 2.88] and Gear.ONCE.containsKey("rcurve:garbage")
          and Gear.ONCE.containsKey("barmor:base.armor.Feet") and Gear.ONCE.containsKey("barmor:base.armor.Head"),
          "AC1: the loader: any case of the slot word, a bad curve -> its default + one WARN, matBonus clamped to 10, an unknown slot / resistance > 100 ignored + WARN")
    Cfg.apply(Props(), False)
    cc_ = lambda v_: Cfg.checkCurve("base.curve", v_)
    check(cc_("1:1.0,4:1.6,10:2.0,40:3.0,100:5.0") is None and cc_("0:1") is None and cc_("1:1,1:2") is not None and cc_("5:1,4:2") is not None
          and cc_("1:0") is not None and cc_("1:-1,2:2") is not None and cc_("101:1") is not None and cc_("1.5:1") is not None and cc_("") is not None
          and cc_("1:1,") is None and cc_("1:1,,2:2") is not None and cc_("abc") is not None and cc_("1:200") is not None,
          "AC1: checkCurve (rising whole levels 0-100, factors above 0 and at most 100; a trailing comma is ignored like Java's split)")
    ca_ = Cfg.checkArmorBase
    check(ca_("base.armor[Chest]", "9|6.48") is None and ca_("base.armor[legs]", "7,5") is None and ca_("base.armor[Feet]", "1|1") is not None
          and ca_("base.armor[Head]", "5|101") is not None and ca_("base.armor[Head]", "-1|3") is not None,
          "AC1: checkArmorBase (Head / Chest / Legs / Hands in any case; Health >= 0; resistance 0-100 %%)")
    print("AC1. rows + default file + loader done")

    # ---- AC2. the curves, the material bonus, K and the family bases
    F_ = lambda l_: float(Base.curveF(l_))
    R_ = lambda l_: float(Base.curveR(l_))
    check(F_(1) == 1.0 and R_(1) == 1.0 and float(Base.bonus(1)) == 1.0 and float(Base.bonus(0)) == 1.0,
          "AC2: F(1) = R(1) = 1 EXACTLY and a band starting at Lv 1 gets no material bonus (a Lv 1 kit item keeps its vanilla numbers)")
    check([round(F_(l_), 2) for l_ in (1, 4, 5, 9, 10, 15, 20, 25, 30, 35, 40, 49, 60, 100)] ==
          [1.0, 1.6, 1.67, 1.93, 2.0, 2.17, 2.33, 2.5, 2.67, 2.83, 3.0, 3.3, 3.67, 5.0], "AC2: F(L) = the spec 3.1 table")
    check([round(R_(l_), 4) for l_ in (1, 4, 10, 20, 40, 100)] == [1.0, 1.1333, 1.4, 1.7, 2.2, 3.0] and F_(0) == 1.0 and F_(100) == 5.0,
          "AC2: R(L) = 1:1.0, 10:1.4, 20:1.7, 40:2.2, 100:3.0; F flat outside the points (F(0) = 1, F(100) = 5)")
    check([round(float(Base.bonus(s_)), 4) for s_ in (5, 10, 15, 20, 25, 35, 40, 45)] == [1.015, 1.03, 1.045, 1.06, 1.075, 1.105, 1.12, 1.135],
          "AC2: material bonus 0.3 %% per band-start level (Copper +3 %%, Iron +4.5 %%, Mithril +12 %%, Prisma +13.5 %% - spec 3.1)")
    Cfg.BASE_CURVE = "1:1.0,10:4.0"
    f10_ = F_(10)
    Cfg.BASE_CURVE = "nonsense"
    fbad_ = F_(4)
    Cfg.BASE_CURVE = str(Cfg.CURVE_DEF)
    check(f10_ == 4.0 and fbad_ == 1.6 and F_(4) == 1.6, "AC2: a new base.curve text applies at the next hit (live); an unreadable one falls back to the default")
    Base.clear()
    fams = {}
    for i_ in ALLW:
        if not bool(Data.isGear(i_)):
            continue
        fams.setdefault(str(Base.family(i_)), []).append(i_)
    check(str(Base.baseOf("Weapon_Sword_Copper")) == "Weapon_Sword_Crude" and str(Base.baseOf("Weapon_Staff_Iron")) == "Weapon_Staff_Wood"
          and str(Base.baseOf("Weapon_Crossbow_Mithril")) == "Weapon_Crossbow_Iron" and str(Base.baseOf("Weapon_Kunai")) == "Weapon_Kunai"
          and str(Base.baseOf("Weapon_Spellbook_Fire")) == "Weapon_Spellbook_Fire" and str(Base.family("Weapon_Kunai")) == "Kunai",
          "AC2: family bases (Crude / Wood / Iron crossbow; Kunai + spellbooks are their own base; the pack's Mithril crossbow -> Iron)")
    kits = ["Weapon_Wand_Wood", "Weapon_Staff_Wood", "Weapon_Sword_Crude", "Weapon_Shortbow_Crude", "Weapon_Battleaxe_Crude"]
    check(all(float(Base.kOf(k_, False)) == 1.0 and float(Base.mult(k_, doc(k_, 1), False)) == 1.0 for k_ in kits)
          and all(float(Base.mult(k_, None, False)) == 1.0 for k_ in kits),
          "AC2: the five class kits are their family's base -> K = 1 and m = 1.0 EXACTLY at Lv 1 (stamped and unstamped = band start 1)")
    xm_ = float(Base.mult("Weapon_Crossbow_Iron", doc("Weapon_Crossbow_Iron", 15), False))
    check(abs(xm_ - 1.0) < 1e-12, "AC2: the Iron crossbow (base of its family, band 15) deals exactly vanilla at Lv 15 (m = %.15f, spec 3.2)" % xm_)
    kc_ = float(Base.kOf("Weapon_Sword_Copper", False))
    check(abs(kc_ - bmax("Weapon_Sword_Crude") / bmax("Weapon_Sword_Copper")) < 1e-9 and float(Base.kOf("Weapon_Sword_Copper", True)) == 1.0
          and float(Base.kOf("Weapon_Spellbook_Fire", False)) > 0.0,
          "AC2: K = the Crude sword's largest entry / the Copper sword's (%g / %g = %.4f); a spell shot has K = 1" % (bmax("Weapon_Sword_Crude"), bmax("Weapon_Sword_Copper"), kc_))
    # the unreadable step -> plain multiply, logged once (a modded weapon whose damage data cannot be read)
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if k_.startswith("basek:"):
            Gear.ONCE.remove(k_)
    odd_ = UZ.allocateInstance(ItemZ.class_)
    fz(ItemZ, "id").set(odd_, "Weapon_Sword_Oddmod")
    fz(ItemZ, "maxStack").setInt(odd_, 1)
    imap.put("Weapon_Sword_Oddmod", odd_)
    r1_, r2_ = float(Base.ratio("Weapon_Sword_Oddmod")), float(Base.ratio("Weapon_Sword_Oddmod"))
    check(r1_ == 1.0 and r2_ == 1.0 and [str(x) for x in Gear.ONCE.keySet() if str(x).startswith("basek:")] == ["basek:Weapon_Sword_Oddmod"],
          "AC2: a weapon whose damage data cannot be read gets K = 1 (the plain level multiplier) and ONE warning")
    # review of 0.2.1 nit: that failed read is NOT cached - once the item's damage data reads (a transient failure is over), the next call
    # gives the real K (here: the Copper sword's breakdown -> the Crude sword's 16 / the Copper sword's largest entry) and caches it
    cached_ = bool(Base.RAT.containsKey("Weapon_Sword_Oddmod"))
    wodd_ = IWPc()
    wodd_.setBasicDamageBreakdown(Gear.item("Weapon_Sword_Copper").getWeapon().getBasicDamageBreakdown())
    fz(ItemZ, "weapon").set(odd_, wodd_)
    r3_ = float(Base.ratio("Weapon_Sword_Oddmod"))
    check(not cached_ and abs(r3_ - bmax("Weapon_Sword_Crude") / bmax("Weapon_Sword_Copper")) < 1e-9 and bool(Base.RAT.containsKey("Weapon_Sword_Oddmod"))
          and [str(x) for x in Gear.ONCE.keySet() if str(x).startswith("basek:")] == ["basek:Weapon_Sword_Oddmod"],
          "AC2: nit - a failed damage-data read is not cached: when it reads again the real K applies (%.4f) and is cached; still one warning" % r3_)
    imap.remove("Weapon_Sword_Oddmod")
    Base.clear()
    # per family: m at each item's band start = what every hit of that item gets vs its vanilla numbers (the spec's 'against vanilla')
    rows10 = []
    for fam_, ids_ in sorted(fams.items()):
        for i_ in sorted(ids_):
            if not BRK.get(i_):
                continue
            st_ = int(Lvl.band(i_)[0])
            rows10.append((fam_, i_, st_, float(Base.kOf(i_, False)), float(Base.mult(i_, doc(i_, st_), False))))
    # the spec's own table (spec 3.3) assumed every step of a material scales like the Crude one; K takes the largest entry (spec 3.2).
    # Spec bounds: Sword / Shortbow / Spear / Mace / Battleaxe metal items stay within +5 % .. +70 % of vanilla (a little slack for K)
    METALS = ("Copper", "Bronze", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")
    inb_ = [(r_[1], round(r_[4], 3)) for r_ in rows10 if r_[0] in ("Sword", "Shortbow", "Spear", "Mace", "Battleaxe")
            and r_[1].split("_")[-1] in METALS]
    # the one outlier: vanilla's Onyxium spear stabs for only 6 (Mithril 12, Crude 4) - levelled it hits like every Lv 40 spear (4 x F(40) x
    # 1.12 = 13.4, spec 3.2 "the same damage at the same level"), which is 2.24 x its own weak vanilla stab (reported to Skyy with R10)
    OUT021 = ["Weapon_Spear_Onyxium"]
    outs_ = [x_ for x_ in inb_ if not 0.97 <= x_[1] <= 1.75]
    check(len(inb_) >= 30 and [x_[0] for x_ in outs_] == OUT021, "AC2: metal Sword / Shortbow / Spear / Mace / Battleaxe items at their band start hit "
          "0.97 .. 1.75 x vanilla (spec: +5 %% .. +70 %%), except the listed outlier(s): %s" % outs_)
    print("AC2. outlier: %s - breakdowns Spear Crude %s / Mithril %s / Onyxium %s" % (outs_, BRK.get("Weapon_Spear_Crude"), BRK.get("Weapon_Spear_Mithril"),
                                                                                     BRK.get("Weapon_Spear_Onyxium")))
    sw_ = dict((r_[1], round(r_[4], 2)) for r_ in rows10)
    print("AC2. swords at their band start (spec 3.3 says Copper +58 %%, Iron +37 %%, Thorium +24 %%, Cobalt +34 %%, Adamantite +29 %%, Mithril +10 %% "
          "with swing averages): %s" % dict((i_[13:], sw_.get(i_)) for i_ in ("Weapon_Sword_Copper", "Weapon_Sword_Iron", "Weapon_Sword_Thorium",
                                                                             "Weapon_Sword_Cobalt", "Weapon_Sword_Adamantite", "Weapon_Sword_Mithril")))
    print("AC2. per weapon at its band start (Lv, m = levelled / vanilla per hit):")
    for fam_ in sorted(fams):
        rs_ = [r_ for r_ in rows10 if r_[0] == fam_]
        if rs_:
            print("     %-10s %s" % (fam_, ", ".join("%s Lv%d x%.2f" % (r_[1][len("Weapon_" + fam_) + 1:] or r_[1], r_[2], r_[4]) for r_ in rs_)))
    # the items whose largest vanilla entry is far off their family base's (special shapes - spec 3.2 "odd items"; R8 / R10): K (base max /
    # item max) then lifts a weak special item or shrinks a strong one a lot at its band start - listed for Skyy (staffs and wands are
    # expected high: vanilla staffs / wands deal the same in every material, so the level is their only growth)
    odd21 = [(r_[1], r_[2], bmax(r_[1]), bmax(str(Base.baseOf(r_[1]))), round(r_[4], 2)) for r_ in rows10
             if r_[0] not in ("Axe", "Longsword", "Club", "Staff", "Wand") and (r_[4] > 1.9 or r_[4] < 0.5)]
    print("AC2. odd items (outside x0.5 .. x1.9 at their band start; id, Lv, its largest entry, its base's, m): %s" % odd21)
    r10 = [(r_[1], r_[2], round(r_[4], 2)) for r_ in rows10 if r_[0] in ("Axe", "Longsword", "Club") and r_[1].split("_")[-1] in METALS and r_[2] >= 25]
    print("AC2. R10 (spec risk): Axe / Longsword / Club metal items from Lv 25 - one curve leaves them under vanilla (per-family curves later): %s" % r10)
    check(len(r10) >= 9 and all(m_ < 1.0 for _i, _l, m_ in r10), "AC2: R10 noted - every Axe / Longsword / Club metal item from Lv 25 hits under its "
          "vanilla damage (as the spec warned; %d items)" % len(r10))
    print("AC2. curves + K + family bases done")

    # ---- AC3. the worked table (spec 3.3) through the REAL hit path
    # (a) GearHit.weaponHit - the weapon branch GearHitSys calls - on real engine Damage objects (cause = a real DamageCause by index)
    WORKED = {1: ("6-8", 25, 5, "6-11", 16, 12, 16), 4: ("10-13", 40, 8, "10-18", 26, 19, 26), 10: ("12-16", 50, 10, "12-22", 32, 24, 32),
              20: ("14-19", 58, 12, "14-26", 37, 28, 37), 40: ("18-24", 75, 15, "18-33", 48, 36, 48)}
    Shot_ = J("GearShot")

    def whit(stack_, amount_, cause_="Physical", shot_=False, srec_=None, rec_=None, u_=None):
        d_ = DMGc(None, JInt(CIDX[cause_]), JFloat(float(amount_)))
        r_ = Hit.weaponHit(d_, U1 if u_ is None else u_, None, stack_, shot_, srec_, rec_, None)
        return float(d_.getAmount()), r_

    def table_row(lv_):
        wand_, staff_, sword_, bow_ = (gstack("Weapon_Wand_Wood", lv_), gstack("Weapon_Staff_Wood", lv_), gstack("Weapon_Sword_Crude", lv_),
                                       gstack("Weapon_Shortbow_Crude", lv_))
        rw_, rs_, rb_ = Shot_(U1, wand_, None, None), Shot_(U1, staff_, None, None), Shot_(U1, bow_, None, None)
        w_ = lambda st_, a_, c_="Physical", sh_=False, sr_=None, rc_=None: whit(st_, a_, c_, sh_, sr_, rc_)[0]
        return ("%d-%d" % (rnd(w_(wand_, 6)), rnd(w_(wand_, 8))), rnd(w_(wand_, 25, "Fire", True, rw_, rw_)), rnd(w_(staff_, 5)),
                "%d-%d" % (rnd(w_(sword_, 6)), rnd(w_(sword_, 11))), rnd(w_(sword_, 16)),
                rnd(w_(bow_, 12, "Projectile", True, rb_, None)), rnd(w_(bow_, 16, "Projectile", True, rb_, None)),
                rnd(w_(staff_, 25, "Ice", True, rs_, rs_)))
    for lv_, exp_ in sorted(WORKED.items()):
        got_ = table_row(lv_)
        check(got_[:7] == exp_ and got_[7] == exp_[1], "AC3(a): Lv %d through GearHit.weaponHit (real Damage objects): wand %s / orb %d, staff %d / orb %d, "
              "sword %s / thrust %d, shortbow full draw %d / headshot %d (projectile record) = spec 3.3 %s"
              % (lv_, got_[0], got_[1], got_[2], got_[7], got_[3], got_[4], got_[5], got_[6], exp_))
    w6_ = gstack("Weapon_Wand_Wood", 6)
    a6_, a8_ = whit(w6_, 6)[0], whit(w6_, 8)[0]
    check(rnd(a6_) == 10 and rnd(a8_) == 14 and abs(a6_ - 6 * F_(6)) < 1e-4, "AC3(a): Skyy's crafted Lv 6 Wood wand now hits 10-14 (was 6-8): %.3f / %.3f" % (a6_, a8_))
    k1_ = gstack("Weapon_Wand_Wood", 1)
    check(whit(k1_, 6)[0] == 6.0 and whit(k1_, 8)[0] == 8.0 and whit(IS("Weapon_Wand_Wood", 1), 8)[0] == 8.0,
          "AC3(a): the Lv 1 kit wand (stamped Lv 1, or a plain kit stack without a document = band start 1) keeps EXACTLY 6 / 8")
    # part.stats off: the base still applies (its own switch, spec 3.5 item 2); part.base off / base.mode off: vanilla
    Cfg.PART_STATS = False
    s_off = whit(w6_, 6)
    Cfg.PART_STATS = True
    Cfg.PART_BASE = False
    b_off = whit(w6_, 6)[0]
    Cfg.PART_BASE = True
    Cfg.BASE_MODE = "off"
    m_off = whit(w6_, 6)[0]
    Cfg.BASE_MODE = "shape"
    check(rnd(s_off[0]) == 10 and s_off[1] is None and b_off == 6.0 and m_off == 6.0,
          "AC3(a): part.stats off -> the level still applies (no stats info); part.base off / base.mode off -> vanilla 6")
    # then the 0.2 chain on the LEVELLED amount: Damage % and Strength multiply the levelled hit (spec 3.5 item 3)
    wm_ = gstack("Weapon_Wand_Wood", 6, [("dmg", 50), ("str", 20)])
    dm_, info_ = whit(wm_, 6)
    check(abs(dm_ - 6 * F_(6) * 1.5 * 1.2) < 1e-3 and info_ is not None, "AC3(a): order = level first, then Damage %% (+50 %%) and Strength (+20): "
          "6 x %.4f x 1.5 x 1.2 = %.3f" % (F_(6), dm_))
    # a non-weapon hit (a fire tick) is never scaled; a cause inheriting Physical is a weapon hit
    check(whit(w6_, 6, "Fire")[0] == 6.0 and whit(w6_, 6, "Bludgeoning")[0] > 6.0, "AC3(a): a Fire tick from a melee item is not a weapon hit (unscaled); "
          "a cause inheriting Physical is (Bludgeoning)")
    dnull_ = DMGc(None, JInt(CIDX["Physical"]), JFloat(6.0))
    check(Hit.weaponHit(dnull_, None, None, w6_, False, None, None, None) is None and float(dnull_.getAmount()) == 6.0,
          "AC3(a): weaponHit with no player UUID (a mob) changes nothing")
    # a Copper sword is first scaled to Crude size (K), then F x the Copper bonus
    cs_ = gstack("Weapon_Sword_Copper", 10)
    exp_cs = bmax("Weapon_Sword_Crude") * 2.0 * 1.03
    check(abs(whit(cs_, bmax("Weapon_Sword_Copper"))[0] - exp_cs) < 1e-3, "AC3(a): a Lv 10 Copper sword's biggest vanilla step %g -> %.2f (= the Crude "
          "sword's %g x F(10) 2.0 x Copper +3 %%)" % (bmax("Weapon_Sword_Copper"), exp_cs, bmax("Weapon_Sword_Crude")))
    print("AC3(a). worked table through GearHit.weaponHit done")

    # (b) the REAL GearHitSys.handle / the engine's ArmorDamageReduction.handle / GearArmorSys.handle / GearTrueSys.handle / SkyyMobs'
    # LevelDamage.handle on an ECS shim: a CommandBuffer + ArchetypeChunk subclass made here (fixtures by Ref + ComponentType identity) and
    # the engine's static singletons (Universe / EntityModule / EntityStatsModule .instance) set to never-constructed objects whose
    # ComponentType fields are distinct never-constructed ComponentType objects - so every getComponentType() the systems call resolves
    jpz = JClass("javassist.ClassPool")(True)
    jpz.appendClassPath(B.SERVER_JAR)
    CTFz, CTMz = JClass("javassist.CtField"), JClass("javassist.CtNewMethod")
    REFc = JClass("com.hypixel.hytale.component.Ref")

    def mkfake(name_, sup_, members_):
        cc_ = jpz.makeClass("com.hypixel.hytale.component." + name_, jpz.get(sup_))
        for src_ in members_:
            if src_.startswith("F "):
                cc_.addField(CTFz.make(src_[2:], cc_))
            else:
                cc_.addMethod(CTMz.make(src_, cc_))
        return cc_.toClass(REFc.class_)
    CMPc = "com.hypixel.hytale.component.Component"
    CTc = "com.hypixel.hytale.component.ComponentType"
    RFc = "com.hypixel.hytale.component.Ref"
    AcBufC = mkfake("SkyyAcBuf", "com.hypixel.hytale.component.CommandBuffer", [
        "F public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();",
        "F public static Object EXT = null;",
        "F public static java.util.ArrayList REMOVED = new java.util.ArrayList();",
        "public %s getComponent(%s r, %s t) { java.util.IdentityHashMap m = (java.util.IdentityHashMap) COMP.get(r); if (m == null) return null; return (%s) m.get(t); }" % (CMPc, RFc, CTc, CMPc),
        "public Object getExternalData() { return EXT; }",
        "public void tryRemoveComponent(%s r, %s t) { REMOVED.add(t); }" % (RFc, CTc)])
    AcChunkC = mkfake("SkyyAcChunk", "com.hypixel.hytale.component.ArchetypeChunk", [
        "F public static %s REF = null;" % RFc,
        "F public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();",
        "public %s getReferenceTo(int i) { return REF; }" % RFc,
        "public %s getComponent(int i, %s t) { return (%s) COMP.get(t); }" % (CMPc, CTc, CMPc)])
    AcBuf = JClass(AcBufC.getName())
    AcChunk = JClass(AcChunkC.getName())
    buf_ = UZ.allocateInstance(AcBufC)
    chk_ = UZ.allocateInstance(AcChunkC)
    CTYc = JClass(CTc)
    MODc = JClass("java.lang.reflect.Modifier")
    old_single = {}

    def fill_single(cls_name):
        c_ = JClass(cls_name)
        o_ = UZ.allocateInstance(c_.class_)
        for fd_ in c_.class_.getDeclaredFields():
            if fd_.getType() == CTYc.class_ and not MODc.isStatic(fd_.getModifiers()):
                fd_.setAccessible(True)
                fd_.set(o_, UZ.allocateInstance(CTYc.class_))
        fi_ = c_.class_.getDeclaredField("instance")
        fi_.setAccessible(True)
        old_single[cls_name] = fi_.get(None)
        fi_.set(None, o_)
        return o_
    uni_ = fill_single(ENG + "universe.Universe")
    fill_single(ENG + "modules.entity.EntityModule")
    fill_single(ENG + "modules.entitystats.EntityStatsModule")
    acf(ENG + "universe.Universe", "playersByUuid").set(uni_, HashMap())
    PRc = JClass(ENG + "universe.PlayerRef")
    INVCc = ENG + "inventory.InventoryComponent"
    CT = {"pr": PRc.getComponentType(), "arm": JClass(INVCc + "$Armor").getComponentType(), "util": JClass(INVCc + "$Utility").getComponentType(),
          "tool": JClass(INVCc + "$Tool").getComponentType(), "hot": JClass(INVCc + "$Hotbar").getComponentType(),
          "kb": JClass(ENG + "entity.knockback.KnockbackComponent").getComponentType(), "uuid": JClass(ENG + "entity.UUIDComponent").getComponentType(),
          "ecc": JClass(ENG + "entity.effect.EffectControllerComponent").getComponentType(), "ply": JClass(ENG + "entity.entities.Player").getComponentType(),
          "esm": ESMc.getComponentType()}
    check(all(v_ is not None for v_ in CT.values()) and len(set(SysJ.identityHashCode(v_) for v_ in CT.values())) == len(CT),
          "AC3(b): the ECS shim - every component type the systems ask for resolves to its own object (%s)" % sorted(CT))
    AcBuf.EXT = acalloc(ENG + "universe.world.storage.EntityStore")
    SHORT = JClass("java.lang.Short")

    def sh(i_):
        return SHORT.valueOf(i_).shortValue()

    def mkref(i_):
        r_ = UZ.allocateInstance(REFc.class_)
        acf(RFc, "index").setInt(r_, JInt(i_))
        return r_

    def putc(ref_, key_, comp_):
        m_ = AcBuf.COMP.get(ref_)
        if m_ is None:
            m_ = IdMap()
            AcBuf.COMP.put(ref_, m_)
        m_.put(CT[key_], comp_)

    def mkplayer(u_, name_):
        p_ = acalloc(PRc.class_.getName())
        acf(PRc.class_.getName(), "uuid").set(p_, u_)
        acf(PRc.class_.getName(), "username").set(p_, name_)
        return p_

    def mkinv(kind_, cont_, slot_=None):
        c_ = acalloc(INVCc + "$" + kind_)
        acf(INVCc, "inventory").set(c_, cont_)
        if slot_ is not None:
            acf(ENG + "inventory.ActiveSlotInventoryComponent", "activeSlot").setByte(c_, JClass("java.lang.Byte").valueOf(JClass("java.lang.Byte").parseByte(str(slot_))).byteValue())
        return c_

    def mkuuid(u_):
        c_ = acalloc(ENG + "entity.UUIDComponent")
        acf(ENG + "entity.UUIDComponent", "uuid").set(c_, u_)
        return c_
    MOB_U = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    PJ_U = UUID.fromString("00000000-0000-0000-0000-0000000000b1")
    ref_p, ref_mob, ref_v, ref_j = mkref(1), mkref(2), mkref(3), mkref(4)
    hot_ = SIC(sh(9))
    pr1_ = mkplayer(U1, "AcAttacker")
    pr2_ = mkplayer(U2, "AcVictim")
    putc(ref_p, "pr", pr1_)
    putc(ref_p, "hot", mkinv("Hotbar", hot_, 0))
    putc(ref_p, "arm", mkinv("Armor", SIC(sh(4))))
    putc(ref_mob, "uuid", mkuuid(MOB_U))
    varm_ = SIC(sh(4))
    putc(ref_v, "pr", pr2_)
    putc(ref_v, "arm", mkinv("Armor", varm_))
    putc(ref_j, "uuid", mkuuid(PJ_U))
    acf(ENG + "universe.Universe", "playersByUuid").get(uni_).put(U1, pr1_)
    ADRcls = ADRc.class_
    Hsys.ADR = ADRcls
    Asys.ADR = ADRcls
    Tsys.AFTERSYS = Asys.class_
    hs_, as_, ts_, adr_ = Hsys(True), Asys(True), Tsys(True), ADRc()
    check(bool(hs_.ordered) and bool(as_.ordered) and bool(ts_.ordered), "AC3(b): GearHitSys / GearArmorSys / GearTrueSys constructed ordered (as setup() registers them)")

    def ecs(d_, victim_, systems_):
        AcChunk.REF = victim_
        AcChunk.COMP.clear()
        for s_ in systems_:
            s_.handle(JInt(0), chk_, None, buf_, d_)
        return float(d_.getAmount())

    def melee(stack_, amount_, cause_="Physical", victim_=None, systems_=None):
        hot_.setItemStackForSlot(sh(0), stack_)
        d_ = DMGc(DENTc(ref_p), JInt(CIDX[cause_]), JFloat(float(amount_)))
        return ecs(d_, ref_mob if victim_ is None else victim_, [hs_] if systems_ is None else systems_), d_
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if "GearHitSys" in k_ or "GearArmorSys" in k_ or k_ == "norecord":
            Gear.ONCE.remove(k_)
    e6_, _d6 = melee(w6_, 6)
    e8_, _d8 = melee(w6_, 8)
    check(rnd(e6_) == 10 and rnd(e8_) == 14 and abs(e6_ - a6_) < 1e-5 and not [str(x) for x in Gear.ONCE.keySet() if "GearHitSys" in str(x)],
          "AC3(b): the REAL GearHitSys.handle - a player hits a mob with the Lv 6 Wood wand: 6 / 8 -> %.2f / %.2f (10-14), no system error (%s)"
          % (e6_, e8_, [str(x) for x in Gear.ONCE.keySet() if "Gear" in str(x)][:4]))
    ek_, _dk = melee(gstack("Weapon_Wand_Wood", 1), 8)
    check(ek_ == 8.0, "AC3(b): GearHitSys - the Lv 1 kit wand keeps exactly 8")
    # projectile with its own launch record (ProjectileSource -> GearShotTrack.find by the projectile's UUID): a Lv 4 wand orb 25 -> 40
    Track.SHOTS.clear()
    Track.SHOTS.put(PJ_U, Shot_(U1, gstack("Weapon_Wand_Wood", 4), None, None))
    ej_ = ecs(DMGc(DPRJc(ref_p, ref_j), JInt(CIDX["Fire"]), JFloat(25.0)), ref_mob, [hs_])
    # an arrow through a plain EntitySource (Projectile family) takes the shooter's live record (GearShotTrack.pick): Lv 10 shortbow 12 -> 24
    Track.SHOTS.clear()
    Track.SHOTS.put(UUID.randomUUID(), Shot_(U1, gstack("Weapon_Shortbow_Crude", 10), None, None))
    ea_, _da = melee(gstack("Weapon_Sword_Crude", 40), 12, "Projectile")
    Track.SHOTS.clear()
    check(rnd(ej_) == 40 and rnd(ea_) == 24, "AC3(b): GearHitSys projectiles - a Lv 4 wand orb via its own launch record 25 -> %.1f, a Lv 10 shortbow arrow "
          "via the shooter's live record 12 -> %.1f (never the Lv 40 sword in hand at landing)" % (ej_, ea_))
    # a MOB's hit: no PlayerRef on the attacker -> GearHitSys never scales it (SkyyMobs scales mob damage in its own system)
    em2_ = ecs(DMGc(DENTc(ref_mob), JInt(CIDX["Physical"]), JFloat(10.0)), ref_mob, [hs_])
    check(em2_ == 10.0, "AC3(b): a mob's hit passes GearHitSys unchanged (10 -> %.2f)" % em2_)
    # the 0.2 gate still blocks first: an under-level wand deals 0, cancelled, no knockback (the base step is never reached)
    skills_on()
    bridge.put("class:skill:" + str(U1), "Divinity")
    setlv(U1, "Divinity", 2)
    AcBuf.REMOVED.clear()
    eb_, db_ = melee(w6_, 6)
    check(eb_ == 0.0 and bool(db_.isCancelled()) and AcBuf.REMOVED.contains(CT["kb"]), "AC3(b): an under-level wand (Lv 6, Divinity 2) is still blocked first: 0, cancelled, knockback removed")
    setlv(U1, "Divinity", 6)
    eo_, _do = melee(w6_, 6)
    check(rnd(eo_) == 10, "AC3(b): at Divinity 6 the same wand hits 10")
    bridge.remove("class:skill:" + str(U1))
    skills_off()
    Cfg.PART_BASE = False
    ev_, _dv = melee(w6_, 6)
    Cfg.PART_BASE = True
    check(ev_ == 6.0, "AC3(b): part.base off -> GearHitSys leaves the vanilla 6")
    print("AC3(b). real GearHitSys.handle on the ECS shim done")

    # (c) review of 0.2.1 finding 1: an arrow / bolt never takes another live weapon's multiplier (the reviewer's cases). GearHitSys asks
    # GearShotTrack.pickFor(u, armor, calcOf(d)): the hit's damage step keeps the records whose weapon's GearChg index knows it (+ records
    # of a weapon whose walk is incomplete), then the 0.2 rule (newest / weaker); GearHit.weaponHit clamps a picked record to the smallest
    # multiplier among those candidates (minMult). The REAL GearHitSys.handle on the ECS shim; real Damage objects carrying the engine's
    # DamageSequence meta with the REAL calculator objects of the AC0 model's walk (GearChg.ensure over the MZ2 items).
    DSqc = JClass(ENG + "modules.entity.damage.DamageCalculatorSystems$DamageSequence")
    DCSYc = JClass(ENG + "modules.entity.damage.DamageCalculatorSystems")
    Chg.clear()
    Track.SHOTS.clear()
    MB_, MS_, XI_, CB_ = "Weapon_Shortbow_Mithril", "Weapon_Staff_Mithril", "Weapon_Crossbow_Iron", "Weapon_Shortbow_Crude"

    def knows(i_, c_):
        return Chg.step(Chg.ensure(i_), c_) is not None

    def own_calc(i_, others_):
        for c_ in list(Chg.ensure(i_)[0].keySet()):
            if not any(knows(o_, c_) for o_ in others_):
                return c_
        return None
    c_mb, c_xb, c_cb = own_calc(MB_, [MS_, XI_, CB_]), own_calc(XI_, [MB_, MS_, CB_]), own_calc(CB_, [MB_, MS_, XI_])
    check(c_mb is not None and c_xb is not None and c_cb is not None and all(bool(Chg.walked(Chg.ensure(i_))) for i_ in (MB_, MS_, XI_, CB_)),
          "AC3(c): the AC0 model's walk (GearChg.ensure) gives the Mithril shortbow, the Iron crossbow and the Crude shortbow damage steps of "
          "their own and walks all four weapons (+ the Mithril staff) completely")

    def seq_dmg(amount_, calc_):
        d_ = DMGc(DENTc(ref_p), JInt(CIDX["Projectile"]), JFloat(float(amount_)))
        if calc_ is not None:
            sq_ = UZ.allocateInstance(DSqc.class_)
            fz(DSqc, "damageCalculator").set(sq_, calc_)
            d_.putMetaObject(DCSYc.DAMAGE_SEQUENCE, sq_)
        return d_

    def arrow(amount_, calc_=None):
        hot_.setItemStackForSlot(sh(0), gstack("Weapon_Sword_Crude", 40))     # the hand at landing never counts for an arrow
        d_ = seq_dmg(amount_, calc_)
        return ecs(d_, ref_mob, [hs_]), d_

    def recs(*pairs_):
        Track.SHOTS.clear()
        now_ = int(SysJ.currentTimeMillis())
        for st_, age_ in pairs_:
            r_ = Shot_(U1, st_, None, None)
            r_.at = now_ - age_
            Track.SHOTS.put(UUID.randomUUID(), r_)
    meta_ok = False
    try:
        dq_ = seq_dmg(10.0, c_mb)
        meta_ok = c_mb is not None
    except Exception as ex_:
        check(False, "AC3(c): a real Damage with the engine's DamageSequence meta could not be built here (%s) - finding 1 unchecked" % ex_)
    if meta_ok:
        try:
            cq_ = Track.calcOf(dq_)
            check(cq_ is not None and int(SysJ.identityHashCode(cq_)) == int(SysJ.identityHashCode(c_mb))
                  and Track.calcOf(DMGc(DENTc(ref_p), JInt(CIDX["Projectile"]), JFloat(10.0))) is None,
                  "AC3(c): GearShotTrack.calcOf reads the hit's damage step (the same calculator object) from the engine's DamageSequence meta; none without it")
        except Exception as ex_:
            check(False, "AC3(c): GearShotTrack.calcOf is not callable (%s)" % ex_)
        bowM = gstack(MB_, 40, [("str", 20)])
        stfM = gstack(MS_, 40)
        m_mb, m_st = float(Base.weaponMult(bowM, False)), float(Base.weaponMult(stfM, True))
        fstr = 1.0 + 20 * float(Cfg.STR_PER) / 100.0
        exp_bow, exp_clamp = 48 * m_mb * fstr, 48 * m_mb
        # the reviewer's case 1: a Lv 40 Mithril shortbow arrow (48) while a NEWER Lv 40 Mithril staff record is in the air
        recs((bowM, 3000), (stfM, 1000))
        a_cal, _da = arrow(48, c_mb)
        a_none, _da = arrow(48)
        a_unk, _da = arrow(48, UZ.allocateInstance(DCALCz.class_))
        check(abs(a_cal - exp_bow) < 1e-3, "AC3(c): finding 1 - a Lv 40 Mithril shortbow arrow (48) with a NEWER Lv 40 Mithril staff record live: its damage step "
              "names the bow -> the bow's x%.3f and its own Strength +20 = %.2f (the reviewed jar: the staff's x%.2f = %.2f)" % (m_mb, a_cal, m_st, 48 * m_st))
        check(abs(a_none - exp_clamp) < 1e-3 and abs(a_unk - exp_clamp) < 1e-3, "AC3(c): ... the same arrow with no damage step / a step no walk knows: the 0.2 rule "
              "picks the weaker record (the staff) and the clamp keeps the smallest multiplier of the live weapons: %.2f / %.2f (= 48 x %.3f)" % (a_none, a_unk, m_mb))
        # the reviewer's case 2 (one class, Archer): an Iron crossbow Lv 15 bolt (10) while a NEWER Lv 13 Crude shortbow record is in the air
        xbI, cb13, cb1 = gstack(XI_, 15), gstack(CB_, 13), gstack(CB_, 1)
        m13 = float(Base.weaponMult(cb13, False))
        recs((xbI, 3000), (cb13, 1000))
        b_x, _db = arrow(10, c_xb)
        b_c, _db = arrow(12, c_cb)
        b_xn, _db = arrow(10)
        b_cn, _db = arrow(12)
        check(abs(b_x - 10.0) < 1e-4 and abs(b_c - 12 * m13) < 1e-4 and abs(12 * m13 - 25.2) < 1e-6,
              "AC3(c): finding 1 - an Iron crossbow Lv 15 bolt (10) with a NEWER Lv 13 Crude shortbow record: exactly %.4f (the reviewed jar: x2.1 = 21); "
              "the shortbow's own arrow keeps x%.2f = %.2f (the reviewer's quick fix alone made it 12)" % (b_x, m13, b_c))
        check(abs(b_xn - 10.0) < 1e-4 and abs(b_cn - 12.0) < 1e-4, "AC3(c): ... with no damage step the clamp fallback: bolt %.2f, arrow %.2f (the trade-off "
              "while both are in the air: the smaller multiplier)" % (b_xn, b_cn))
        # the same item at two levels shares its damage steps -> the lower multiplier
        recs((cb1, 3000), (cb13, 1000))
        c_two, _dc = arrow(12, c_cb)
        check(abs(c_two - 12.0) < 1e-4, "AC3(c): the same shortbow at Lv 1 and Lv 13 in the air (shared damage steps): the lower multiplier (%.2f, never 25.2)" % c_two)
        # one record = its own numbers, with or without a damage step
        recs((bowM, 1000))
        d1_, _dd = arrow(48, c_mb)
        d2_, _dd = arrow(48)
        check(abs(d1_ - exp_bow) < 1e-3 and abs(d2_ - exp_bow) < 1e-3, "AC3(c): one record in the air = its own numbers with or without a damage step (%.2f / %.2f)" % (d1_, d2_))
        # an incomplete walk never rules a record out (a fake copy of the staff's index entry marked 'walk incomplete')
        recs((bowM, 3000), (stfM, 1000))
        es_ = Chg.ensure(MS_)
        ec_ = JArray(OBJ)(8)
        for i_ in range(8):
            ec_[i_] = es_[i_]
        ec_[5] = JClass("java.lang.Boolean").FALSE
        Chg.ITEMS.put(MS_, ec_)
        e_inc, _de = arrow(48, c_mb)
        Chg.ITEMS.put(MS_, es_)
        check(abs(e_inc - exp_clamp) < 1e-3, "AC3(c): a live weapon whose walk is incomplete is never ruled out by a step it does not list: the weaker record + "
              "the clamp (%.2f)" % e_inc)
        # exploit direction: a weak Lv 1 shortbow and a strong Lv 40 Mithril bow (Strength +20) in the air - each arrow gets ITS weapon
        recs((bowM, 3000), (cb1, 1000))
        f_weak, _df = arrow(12, c_cb)
        f_strong, _df = arrow(48, c_mb)
        check(abs(f_weak - 12.0) < 1e-4 and abs(f_strong - exp_bow) < 1e-3, "AC3(c): a weak Lv 1 shortbow and a strong Lv 40 Mithril bow in the air: the weak bow's "
              "arrow stays vanilla 12 (%.2f - never the strong bow's numbers), the strong bow's arrow gets its own (%.2f)" % (f_weak, f_strong))
        # a blocked record still blocks every arrow of that shooter (liveBad), whatever weapon the damage step names
        recs((bowM, 3000))
        Track.SHOTS.put(UUID.randomUUID(), Shot_(U1, gstack(CB_, 13), None, JArray(JString)(["Weapon_Shortbow_Crude", "Level too low", "test"])))
        g_, dg_ = arrow(48, c_mb)
        check(g_ == 0.0 and bool(dg_.isCancelled()), "AC3(c): a blocked record in the air still blocks (0, cancelled) although the damage step names another weapon")
        # the new GearShotTrack members directly
        try:
            recs((bowM, 3000), (stfM, 1000))
            cs1_, cs0_ = Track.cands(U1, c_mb), Track.cands(U1, None)
            mm1_, mm0_ = float(Track.minMult(U1, c_mb)), float(Track.minMult(U1, None))
            p1_, p0_ = Track.pickFor(U1, None, c_mb), Track.pick(U1, None)
            check(int(cs1_.size()) == 1 and str(cs1_.get(0).main.getItemId()) == MB_ and int(cs0_.size()) == 2 and mm1_ == -1.0 and abs(mm0_ - m_mb) < 1e-9
                  and str(p1_.main.getItemId()) == MB_ and str(p0_.main.getItemId()) == MS_,
                  "AC3(c): cands / minMult / pickFor - the step keeps only the bow's record (no clamp: -1); no step keeps both (clamp x%.3f); pick() = the 0.2 rule (the weaker staff)" % mm0_)
        except Exception as ex_:
            check(False, "AC3(c): GearShotTrack.cands / minMult / pickFor are not callable (%s)" % ex_)
        print("AC3(c). Mithril shortbow arrow 48 + a newer staff record: with its damage step %.2f (bow x%.3f, Strength x%.2f), no step %.2f, unknown "
              "step %.2f (the reviewed jar: %.2f); Iron crossbow bolt 10 + a newer Lv 13 shortbow: %.2f (no step %.2f), that shortbow's arrow 12: %.2f "
              "(no step %.2f); Lv 1 + Lv 13 shortbow: %.2f; weak / strong bow arrows: %.2f / %.2f"
              % (a_cal, m_mb, fstr, a_none, a_unk, 48 * m_st, b_x, b_xn, b_c, b_cn, c_two, f_weak, f_strong))
    Track.SHOTS.clear()
    Chg.clear()
    print("AC3(c). review of 0.2.1 finding 1 (picked arrows) done")

    # ---- AC4. armor Health per stack through the EXISTING LOCK PLUMBING (GearFx.armorPass / locks / plan / lowerNow) on a REAL EntityStatMap
    # (EntityStatValue computes max = base + the MAX ADDITIVE modifiers and clamps the value at once - the engine's own code). The engine's
    # own armor Health is the "Armor" modifier StatModifiersManager puts at EntityStatsSystems$Recalculate (key CalculationType.ADDITIVE
    # .createKey("Armor") = GearFx.armorKey()); engine_recalc() puts exactly that (the container's native sum) like the engine does.
    sm_ = ESMc()
    sm_.update()
    putc(ref_v, "esm", sm_)
    hv_ = sm_.get(JInt(HP_I))
    AKEY = str(Fx.armorKey())

    def engine_recalc():
        tot_ = 0.0
        for s_i in range(int(varm_.getCapacity())):
            st_ = varm_.getItemStack(sh(s_i))
            if st_ is not None and not st_.isEmpty():
                tot_ += float(Base.nativeHealth(Gear.item(st_.getItemId())))
        if tot_ == 0.0:
            sm_.removeModifier(JInt(HP_I), AKEY)
        else:
            sm_.putModifier(JInt(HP_I), AKEY, SMO(MTG.MAX, CAL.ADDITIVE, JFloat(tot_)))

    def lockv():
        mo_ = sm_.getModifier(JInt(HP_I), str(Fx.LOCK) + "Health")
        return 0.0 if mo_ is None else float(mo_.getAmount())

    def slot(i_, stack_):
        varm_.setItemStackForSlot(sh(i_), stack_)

    def apass(raise_):
        Fx.armorPass(U2, None, buf_, ref_v, varm_, raise_)

    def settle():
        apass(False)
        engine_recalc()
        apass(True)
    check(abs(float(hv_.getMax()) - 100.0) < 1e-6 and abs(float(hv_.get()) - 100.0) < 1e-6, "AC4: a real EntityStatMap: Health 100 / 100 (fake stat asset)")
    # equip a Lv 10 Copper chestplate: target 9 x F(10) = 18, native 9 -> the lock ADDS 9 at once (raise = false, the armor change event pass)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 10), U2))
    apass(False)
    l1_ = lockv()
    engine_recalc()
    mx1_ = float(hv_.getMax())
    apass(True)
    mx1b_ = float(hv_.getMax())
    check(abs(l1_ - 9.0) < 1e-4 and abs(mx1_ - 118.0) < 1e-4 and abs(mx1b_ - 118.0) < 1e-4 and abs(float(hv_.get()) - 100.0) < 1e-4,
          "AC4: equip a Lv 10 Copper chestplate -> the lock adds +9 at once, the engine adds its own 9 -> max 118 (= 100 + 18, spec Lv 10 row), "
          "current kept: lock %.2f max %.2f" % (l1_, mx1_))
    # no stacking on re-equip: the same piece passed again (event + tick), and put on again, keeps ONE +9
    apass(False)
    apass(True)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 10), U2))
    settle()
    check(abs(lockv() - 9.0) < 1e-4 and abs(float(hv_.getMax()) - 118.0) < 1e-4, "AC4: re-equip / repeated passes never stack (lock %.2f, max %.2f)" % (lockv(), float(hv_.getMax())))
    # unequip: the bonus never lowers max before the engine dropped the piece's own Health (engine review 1); the 1 s tick removes it
    slot(1, None)
    apass(False)
    l2_ = lockv()
    engine_recalc()
    mx2_ = float(hv_.getMax())
    apass(True)
    l3_, mx3_ = lockv(), float(hv_.getMax())
    check(abs(l2_ - 9.0) < 1e-4 and abs(mx2_ - 109.0) < 1e-4 and l3_ == 0.0 and abs(mx3_ - 100.0) < 1e-4,
          "AC4: unequip -> the change pass keeps +9 until the engine dropped its 9 (max %.0f), the next 1 s tick removes the bonus -> max %.0f, lock gone" % (mx2_, mx3_))
    # the spec 3.3 chestplate column (Health 9 / 14 / 18 / 21 / 27 at Lv 1 / 4 / 10 / 20 / 40) = what the player really gets
    col_ = {}
    for lv_ in (1, 4, 10, 20, 40):
        slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", lv_), U2))
        settle()
        col_[lv_] = rnd(float(hv_.getMax()) - 100.0)
    slot(1, None)
    settle()
    check(col_ == {1: 9, 4: 14, 10: 18, 20: 21, 40: 27} and lockv() == 0.0, "AC4: chestplate Health per level through the lock plumbing = spec 3.3 (9 / 14 / 18 / 21 / 27): %s" % col_)
    # a piece BELOW its vanilla Health (Wool chest Lv 5: native 17, target 9 x F(5) x 1.015 = 15.2): the lock CANCELS 1.8 - only once the
    # engine is synced (lowering max waits, like every lock raise)
    slot(1, Data.put(IS("Armor_Cloth_Wool_Chest", 1), doc("Armor_Cloth_Wool_Chest", 5), U2))
    apass(False)
    lw0_ = lockv()
    engine_recalc()
    apass(True)
    lw1_, mw_ = lockv(), float(hv_.getMax())
    tw_ = 9.0 * F_(5) * 1.015
    check(lw0_ == 0.0 and abs(lw1_ + (17.0 - tw_)) < 1e-3 and abs(mw_ - (100.0 + tw_)) < 1e-3,
          "AC4: a Lv 5 Wool chestplate (native 17 > target %.2f): nothing before the engine sync, then the lock cancels %.2f -> max %.2f" % (tw_, -lw1_, mw_))
    # an inactive piece (unidentified) loses everything (level.armorNative), the per-stack target never applies to it
    ud_ = Roll.unidDoc("Armor_Copper_Chest", 2, "drop")
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), ud_, U2))
    settle()
    check(abs(float(hv_.getMax()) - 100.0) < 1e-4 and abs(lockv() + 9.0) < 1e-4, "AC4: an unidentified chestplate gives no Health at all (the lock cancels its 9; max %.1f)" % float(hv_.getMax()))
    # base.armorOn / part.base off -> vanilla 9
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 40), U2))
    for flag_ in ("BASE_ARMOR", "PART_BASE"):
        setattr(Cfg, flag_, False)
        settle()
        mo_ = float(hv_.getMax())
        setattr(Cfg, flag_, True)
        check(abs(mo_ - 109.0) < 1e-4, "AC4: %s off -> a Lv 40 Copper chestplate gives its vanilla 9 (max %.1f)" % (flag_, mo_))
    settle()
    check(abs(float(hv_.getMax()) - 127.0) < 1e-4, "AC4: switched back on -> Lv 40 = +27 again")
    # a full Copper set at Lv 10: 2 x the Copper row = 2 x 25 = +50 (copper armor starts at Lv 1: no material bonus)
    for i_, iid_ in enumerate(("Armor_Copper_Head", "Armor_Copper_Chest", "Armor_Copper_Legs", "Armor_Copper_Hands")):
        slot(i_, Data.put(IS(iid_, 1), doc(iid_, 10), U2))
    settle()
    check(abs(float(hv_.getMax()) - 150.0) < 1e-3, "AC4: a Lv 10 Copper set = 2 x 25 = +50 Health (max %.1f)" % float(hv_.getMax()))
    # GearLockSys's lower-only pass (lowerNow) never lowers max on an unequip; the tick does once the engine is synced
    mx_before = float(hv_.getMax())
    slot(1, None)
    Fx.lowerNow(U2, sm_, varm_, JFloat(1.0))
    check(abs(float(hv_.getMax()) - mx_before) < 1e-4, "AC4: GearFx.lowerNow (GearLockSys) never lowers max on an unequip (%.1f)" % float(hv_.getMax()))
    engine_recalc()
    apass(True)
    check(abs(float(hv_.getMax()) - (100.0 + 2 * (5 + 7 + 4))) < 1e-3, "AC4: after the tick the set without its chestplate = +32 (max %.1f)" % float(hv_.getMax()))
    for i_ in range(4):
        slot(i_, None)
    settle()
    check(lockv() == 0.0 and abs(float(hv_.getMax()) - 100.0) < 1e-4, "AC4: everything off -> no lock, max 100")
    print("AC4. armor Health through the lock plumbing done")

    # ---- AC5. armor RESISTANCE per stack through the REAL engine ArmorDamageReduction.handle + GearArmorSys.handle (+ GearHitSys keeping
    # the pre-armor amount, GearTrueSys after): a mob hits the player for 100
    def mobhit(amount_, cause_="Physical", systems_=None):
        d_ = DMGc(DENTc(ref_mob), JInt(CIDX[cause_]), JFloat(float(amount_)))
        return ecs(d_, ref_v, [hs_, adr_, as_, ts_] if systems_ is None else systems_)
    rescol = {}
    for lv_ in (1, 4, 10, 20, 40):
        slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", lv_), U2))
        rescol[lv_] = "%.1f" % (rnd((100.0 - mobhit(100.0)) * 10.0) / 10.0)
    check(rescol == {1: "6.5", 4: "7.3", 10: "9.1", 20: "11.0", 40: "14.3"}, "AC5: chestplate resistance per level through the real engine armor pass + "
          "GearArmorSys = spec 3.3 (6.5 / 7.3 / 9.1 / 11.0 / 14.3 %%): %s" % rescol)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 10), U2))
    eng_only = mobhit(100.0, systems_=[adr_])
    check(abs(eng_only - 93.52) < 1e-3, "AC5: the engine alone still applies the ASSET value (6.48 %% -> %.2f) - GearArmorSys corrects it" % eng_only)
    epj_ = mobhit(100.0, "Projectile")
    efi_ = mobhit(100.0, "Fire")
    check(abs(epj_ - 100.0 * (1 - 0.0648 * 1.4)) < 1e-3 and efi_ == 100.0, "AC5: Projectile gets the same per-stack resistance (%.3f); Fire is not resisted (%.1f)" % (epj_, efi_))
    for i_, iid_ in enumerate(("Armor_Copper_Head", "Armor_Copper_Chest", "Armor_Copper_Legs", "Armor_Copper_Hands")):
        slot(i_, Data.put(IS(iid_, 1), doc(iid_, 10), U2))
    eset_ = mobhit(100.0)
    check(abs(eset_ - 100.0 * (1 - 0.18 * 1.4)) < 1e-3, "AC5: a Lv 10 Copper set: 18 %% x R(10) 1.4 = 25.2 %% -> %.2f" % eset_)
    Cfg.BASE_ARMOR = False
    evan_ = mobhit(100.0)
    Cfg.BASE_ARMOR = True
    check(abs(evan_ - 82.0) < 1e-3, "AC5: base.armorOn off -> the vanilla 18 %% (%.2f)" % evan_)
    slot(1, Data.put(IS("Armor_Copper_Chest", 1), ud_, U2))
    einact_ = mobhit(100.0)
    exp_in = 100.0 * (1 - (0.036 + 0.0504 + 0.0288) * 1.4)
    check(abs(einact_ - exp_in) < 1e-3, "AC5: an unidentified chestplate gives no resistance, the other levelled pieces keep theirs (%.3f = %.3f)" % (einact_, exp_in))
    for i_ in range(4):
        slot(i_, None)
    check(mobhit(100.0) == 100.0, "AC5: no armor -> 100")
    print("AC5. armor resistance through the real engine armor pass + GearArmorSys done")

    # ---- AC6. SkyyMobs 0.1 (the LIVE pin) LevelDamage + GearHitSys: two separate chains, both before the engine's armor pass, either order
    # gives the same result (mob damage x its level first; vanilla armor is multiplier-only, so GearArmorSys's ratio is exact either way)
    mobs_ok = False
    try:
        LD = JClass("com.skyy.mobs.LevelDamage")
        MobLevelJ, MobInfoJ, MobCfgJ = JClass("com.skyy.mobs.MobLevel"), JClass("com.skyy.mobs.MobInfo"), JClass("com.skyy.mobs.MobCfg")
        ld_ = LD(False)
        mi_ = MobInfoJ()
        mi_.level = 10
        mi_.uuid = MOB_U
        MobLevelJ.MOBS.put(MOB_U, mi_)
        mobs_ok = True
    except Exception as ex_:
        check(False, "AC6: SkyyMobs-%s.jar classes could not be used (%s)" % (MOBS_PIN, ex_))
    # review of 0.2.1 nit: the SkyyMobs classes come from the jar PINNED in tools/deploy_set.py (read from its SET line), not a fixed 0.1
    if mobs_ok:
        src_ = str(LD.class_.getProtectionDomain().getCodeSource().getLocation())
        setp_ = re.findall(r'\(\s*"SkyyMobs"\s*,\s*"([0-9][0-9.]*)"\s*\)', open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read())
        check(len(setp_) == 1 and MOBS_PIN == setp_[0] and src_.replace("%20", " ").endswith("/SkyyMobs-%s.jar" % setp_[0]),
              "AC6: the SkyyMobs classes are the SET pin's jar (tools/deploy_set.py: SkyyMobs %s; LevelDamage loaded from %s)" % (setp_, src_))
    if mobs_ok:
        mm10 = float(MobCfgJ.dmgMult(10))
        slot(1, Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 10), U2))
        oa_ = mobhit(10.0, systems_=[ld_, hs_, adr_, as_, ts_])
        ob_ = mobhit(10.0, systems_=[hs_, ld_, adr_, as_, ts_])
        exp_o = 10.0 * mm10 * (1 - 0.0648 * 1.4)
        check(mm10 > 1.0 and abs(oa_ - exp_o) < 1e-3 and abs(ob_ - exp_o) < 1e-3, "AC6: a Lv 10 mob hits a player in a Lv 10 chestplate: LevelDamage x%.2f then the "
              "levelled armor - LevelDamage before GearHitSys %.4f, after it %.4f (both = %.4f)" % (mm10, oa_, ob_, exp_o))
        # a player's hit on that mob: LevelDamage leaves it (players are never levelled), GearHitSys applies the weapon level - either order
        hot_.setItemStackForSlot(sh(0), w6_)
        pa_ = ecs(DMGc(DENTc(ref_p), JInt(CIDX["Physical"]), JFloat(6.0)), ref_mob, [ld_, hs_, adr_, as_])
        pb_ = ecs(DMGc(DENTc(ref_p), JInt(CIDX["Physical"]), JFloat(6.0)), ref_mob, [hs_, ld_, adr_, as_])
        check(abs(pa_ - 6 * F_(6)) < 1e-4 and abs(pb_ - pa_) < 1e-6, "AC6: a player's Lv 6 wand hit on a Lv 10 mob: only the weapon level applies (%.3f / %.3f), never the mob's" % (pa_, pb_))
        mo1_ = mobhit(10.0, systems_=[hs_])
        mo2_ = mobhit(10.0, systems_=[ld_])
        check(mo1_ == 10.0 and abs(mo2_ - 10.0 * mm10) < 1e-4, "AC6: the gear chain alone leaves a mob's 10 (%.1f); SkyyMobs alone scales it (%.2f)" % (mo1_, mo2_))
        MobLevelJ.MOBS.remove(MOB_U)
        slot(1, None)
    # bytecode of the pinned SkyyMobs jar: LevelDamage = Filter damage group, ordered BEFORE ArmorDamageReduction (= GearHitSys's slot)
    mjar_ = MOBS_JAR
    if os.path.isfile(mjar_):
        pm_ = Pool(False)
        pm_.appendClassPath(mjar_)
        pm_.appendClassPath(B.SERVER_JAR)
        pm_.appendSystemPath()
        ldc_ = pm_.get("com.skyy.mobs.LevelDamage")
        txt_ = ""
        for mm_ in list(ldc_.getDeclaredMethods()) + [c_.toMethod("ctor", ldc_) for c_ in ldc_.getDeclaredConstructors()]:
            bo_ = BOS()
            IP(PS(bo_)).print_(mm_)
            txt_ += str(bo_.toString())
        ghs_ = mcode("GearHitSys", "getGroup")
        check("getFilterDamageGroup" in txt_ and "Order.BEFORE" in txt_ and "getFilterDamageGroup" in ghs_,
              "AC6: SkyyMobs 0.1 LevelDamage and GearHitSys are both Filter-group damage systems ordered BEFORE the engine's armor pass")
    print("AC6. SkyyMobs LevelDamage + GearHitSys order done")
    # the Priest heal stays capped: SkyyClasses 0.1.10's PriestHealSys reads the LANDED damage (Inspect group, after every Filter system)
    # and caps it per hit + per second (read from its build script, read only)
    cbs_ = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.10.py")
    if os.path.isfile(cbs_):
        ctx_ = open(cbs_, encoding="utf-8").read()
        mh_ = re.search(r"\nDEF_HEAL_MAX_HIT\s*=\s*([0-9.]+)", ctx_)
        ms_ = re.search(r"\nDEF_HEAL_MAX_SEC\s*=\s*([0-9.]+)", ctx_)
        ph_ = ctx_[ctx_.find("0.1.6 PriestHealSys"):ctx_.find("0.1.6 PriestHealSys") + 1500]
        check(mh_ is not None and float(mh_.group(1)) == 10.0 and ms_ is not None and float(ms_.group(1)) == 10.0 and "getInspectDamageGroup" in ph_,
              "AC6: the Priest heal stays capped - SkyyClasses heals from the landed damage (Inspect group) capped at %s HP per hit / %s per second, so a Lv 40 orb "
              "(25 x 3 = 75) heals 10, like a Lv 4 one" % (mh_.group(1) if mh_ else "?", ms_.group(1) if ms_ else "?"))

    # ---- AC7. the tooltip lines: our per-stack line shows the LEVELLED numbers; in the item tooltip itself (GearView.apply = lines + hints)
    # a grey line says what the client's vanilla box below is
    def tl(stack_, owner_=None):
        txt_, col_ = ArrayList(), ArrayList()
        d_ = Data.effective(stack_.getItemId(), stack_.getMetadata())
        View.lines(stack_.getItemId(), d_, owner_, txt_, col_)
        # (0.2.2: no GearView.hints any more - the grey note is gone everywhere, Skyy 2026-10-03)
        return [str(x) for x in txt_], [None if c_ is None else str(c_) for c_ in col_]
    GRAY = str(Defs.C_GRAY)
    # 0.2.2: 0.2.1's two grey notes - GearBase.HINT_W / HINT_A are gone; no tooltip, describe line or page column may show them
    HW, HA = "(the Damage Data box below is vanilla - before levels)", "(Health / Resistance below are vanilla - before levels)"
    # review of 0.2.1 finding 3: the legacy Projectile assets (what a wand / staff / spellbook cast launches) with their REAL damage read
    # straight from Assets.zip (Server/Projectiles/**.json, Parent chain resolved), in the engine's own DefaultAssetMap
    LPRJc = JClass(ENG + "asset.type.projectile.config.Projectile")
    prj_json = {}
    with zipfile.ZipFile(AZP) as zp_:
        for n_ in zp_.namelist():
            if n_.startswith("Server/Projectiles/") and n_.endswith(".json"):
                try:
                    prj_json[os.path.basename(n_)[:-5]] = json.loads(zp_.read(n_).decode("utf-8-sig"))
                except Exception:
                    pass

    def prj_dmg(p_):
        seen_ = 0
        while p_ in prj_json and seen_ < 16:
            if prj_json[p_].get("Damage") is not None:
                return int(prj_json[p_]["Damage"])
            p_, seen_ = prj_json[p_].get("Parent"), seen_ + 1
        return None
    pmap_ = DAMz()
    for p_ in prj_json:
        dv_ = prj_dmg(p_)
        if dv_ is None:
            continue
        po_ = acalloc(LPRJc.class_.getName())
        acf(LPRJc.class_.getName(), "id").set(po_, p_)
        acf(LPRJc.class_.getName(), "damage").setInt(po_, JInt(dv_))
        fz(DAMz, "assetMap").get(pmap_).put(p_, po_)
    old_lprj = acf(LPRJc.class_.getName(), "ASSET_STORE").get(None)
    acf(LPRJc.class_.getName(), "ASSET_STORE").set(None, zstore(pmap_))
    check(prj_dmg("Skeleton_Mage_Corruption_Orb") == 25 and prj_dmg("Ice_Ball") == 20 and prj_dmg("Fireball") == 60
          and int(LPRJc.getAssetMap().getAsset("Skeleton_Mage_Corruption_Orb").getDamage()) == 25,
          "AC7: the legacy Projectile model answers (Assets.zip: the orb 25, Ice_Ball 20, Fireball 60 - %d projectile files)" % len(prj_json))
    Chg.clear()
    t6_, c6_ = tl(w6_)
    i6_ = t6_.index("Damage at Lv 6: 10-14") if "Damage at Lv 6: 10-14" in t6_ else -1
    sp6_ = "Spell at Lv 6: %d" % rnd(25 * F_(6))
    check(i6_ >= 0 and sp6_ == "Spell at Lv 6: 43" and t6_[i6_ + 1] == sp6_ and c6_[i6_:i6_ + 2] == [None, None] and t6_[0].startswith("Lv 6") and HW not in t6_,
          "AC7: Skyy's Lv 6 Wood wand tooltip without SkyyArmory: 'Damage at Lv 6: 10-14', then finding 3's '%s' (the orb 25 x F(6)) - and NO grey note "
          "(0.2.2; with SkyyArmory loaded the shot lines replace both, section AD1) (lines %s)" % (sp6_, t6_[:5]))
    t1_, _c1 = tl(gstack("Weapon_Wand_Wood", 1))
    check("Damage: 6-8" in t1_ and "Spell: 25" in t1_ and HW not in t1_ and not any(x_.startswith("Damage at") or x_.startswith("Spell at") for x_ in t1_),
          "AC7: finding 2 - the Lv 1 kit wand reads 0.2's 'Damage: 6-8' (= the vanilla box below) + 'Spell: 25', no hint: %s" % t1_[:4])
    txi_, _cxi = tl(gstack("Weapon_Crossbow_Iron", 15))
    t2w_, _c2w = tl(gstack("Weapon_Wand_Wood", 2))
    check(("Damage: " + str(View.damageText("Weapon_Crossbow_Iron"))) in txi_ and HW not in txi_ and not any(x_.startswith("Damage at") for x_ in txi_)
          and any(x_.startswith("Damage at Lv 2: ") for x_ in t2w_) and HW not in t2w_,
          "AC7: finding 2 - the Iron crossbow at Lv 15 (its own family base at its band start: m = 1 up to float noise) keeps the plain line too; "
          "a Lv 2 wand gets 'Damage at Lv 2' (0.2.2: no note): %s / %s" % (txi_[1:3], t2w_[1:4]))
    for sid_, slv_ in (("Weapon_Spellbook_Fire", 30), ("Weapon_Staff_Frost", 30)):
        pids_ = sorted(str(k_) for k_ in Chg.ensure(sid_)[1].keySet())
        dms_ = [prj_dmg(p_) for p_ in pids_ if prj_dmg(p_)]
        sst_ = int(Lvl.band(sid_)[0])
        smm_ = F_(slv_) * float(Base.bonus(sst_))
        slo_, shi_ = (rnd(min(dms_) * smm_), rnd(max(dms_) * smm_)) if dms_ else (-1, -1)
        exs_ = "Spell at Lv %d: %s" % (slv_, str(slo_) if slo_ == shi_ else "%d-%d" % (slo_, shi_))
        tsp_, _csp = tl(gstack(sid_, slv_))
        check(bool(dms_) and exs_ in tsp_, "AC7: finding 3 - %s Lv %d: '%s' (its launches %s, damage %s straight from Assets.zip x F(%d) x the band-%d bonus): %s"
              % (sid_, slv_, exs_, pids_, dms_, slv_, sst_, tsp_[1:4]))
    tsw_, _csw = tl(gstack("Weapon_Sword_Crude", 6))
    check(not any(x_.startswith("Spell") for x_ in tsw_) and any(x_.startswith("Damage at Lv 6: ") for x_ in tsw_),
          "AC7: finding 3 - no spell line on a melee weapon: %s" % tsw_[1:3])
    jb_ = b"".join(zipfile.ZipFile(jar).read(n_) for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
    check(b"before levels" not in jb_ and b"box below is vanilla" not in jb_ and b"below are vanilla" not in jb_,
          "AC7: 0.2.2 - neither grey note (0.2.1 finding 4's two hints) is left anywhere in the jar's classes")
    for lab_, st_ in (("Lv 6 Wood wand", w6_), ("Lv 1 kit wand", gstack("Weapon_Wand_Wood", 1)), ("Lv 30 Fire spellbook", gstack("Weapon_Spellbook_Fire", 30)),
                      ("Lv 10 Copper staff", gstack("Weapon_Staff_Copper", 10))):
        print("AC7. tooltip %s: %s" % (lab_, " | ".join(x_ for x_ in tl(st_)[0] if x_)))
    tm_, _cm = tl(wm_)
    check("Damage at Lv 6: 10-14 (+50%)" in tm_ and not any(x_.startswith("Damage: +50") for x_ in tm_),
          "AC7: a Damage %% modifier sits in brackets on the levelled line (no second Damage line)")
    tc18_, _x = tl(gstack("Weapon_Sword_Copper", 18))
    rcs_ = [x_ for x_ in tc18_ if x_.startswith("Damage at Lv 18: ")]
    m18_ = float(Base.mult("Weapon_Sword_Copper", doc("Weapon_Sword_Copper", 18), False))
    lo_ = min(e_[1] for e_ in BRK["Weapon_Sword_Copper"]) * m18_
    hi_ = bmax("Weapon_Sword_Copper") * m18_
    check(rcs_ == ["Damage at Lv 18: %d-%d" % (rnd(lo_), rnd(hi_))], "AC7: a Lv 18 Copper sword shows its levelled range: %s" % rcs_)
    for flag_, val_ in (("PART_BASE", False), ("BASE_MODE", "off")):
        old_ = getattr(Cfg, flag_)
        setattr(Cfg, flag_, val_)
        to_, _co = tl(w6_)
        setattr(Cfg, flag_, old_)
        check("Damage: 6-8" in to_ and HW not in to_ and not any(x_.startswith("Damage at") or x_.startswith("Spell") for x_ in to_),
              "AC7: %s = %s -> the 0.2 line 'Damage: 6-8' (vanilla numbers, no hint, no spell line)" % (flag_, val_))
    ta_, ca2_ = tl(Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 4), U2))
    ia2_ = ta_.index("Health at Lv 4: +14") if "Health at Lv 4: +14" in ta_ else -1
    check(ia2_ >= 0 and ta_[ia2_ + 1] == "Resistance at Lv 4: 7.3% (physical, projectile)" and HA not in ta_,
          "AC7: a Lv 4 Copper chestplate: 'Health at Lv 4: +14' / 'Resistance at Lv 4: 7.3%% (physical, projectile)', no note (0.2.2) (%s)" % ta_[:5])
    # review of 0.2.1 finding 2, the same rule for armor: a Lv 1 copper piece's levelled numbers ARE its asset's (the slot base = the vanilla
    # Copper row) -> 0.2's armor lines, no hint; a Lv 2 one is levelled again
    t1a_, _c1a = tl(Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 1), U2))
    t2a_, _c2a = tl(Data.put(IS("Armor_Copper_Head", 1), doc("Armor_Copper_Head", 2), U2))
    try:
        av1_ = bool(Base.armorAsVanilla("Armor_Copper_Chest", doc("Armor_Copper_Chest", 1)))
        av2_ = bool(Base.armorAsVanilla("Armor_Iron_Chest", doc("Armor_Iron_Chest", 15)))
    except Exception:
        av1_, av2_ = False, True
    check("Health: 9" in t1a_ and HA not in t1a_ and not any(x_.startswith("Health at") or x_.startswith("Resistance at") for x_ in t1a_)
          and "Health at Lv 2: +%d" % rnd(5 * F_(2)) in t2a_ and HA not in t2a_ and av1_ and not av2_,
          "AC7: finding 2 for armor - a Lv 1 copper chestplate keeps 0.2's line 'Health: 9' (no hint): %s; a Lv 2 copper helmet is levelled: %s; "
          "an Iron chestplate at Lv 15 (vanilla 17) is not 'as vanilla'" % (t1a_[1:4], t2a_[1:4]))
    print("AC7. tooltip Lv 1 copper chestplate: %s ;; Lv 4: %s" % (" | ".join(x_ for x_ in t1a_ if x_), " | ".join(x_ for x_ in ta_ if x_)))
    tt_, _ct = tl(Data.put(IS("Armor_Thorium_Chest", 1), doc("Armor_Thorium_Chest", 20), U2))
    tx_, _cx = tl(Data.put(IS("Armor_Cloth_Cindercloth_Head", 1), doc("Armor_Cloth_Cindercloth_Head", 30), U2))
    check("Health at Lv 20: +%d" % rnd(9 * F_(20) * 1.06) in tt_ and "Poison resistance: 10%" in tt_ and "Mana: 10" in tx_
          and "Health at Lv 30: +%d" % rnd(5 * F_(30) * 1.09) in tx_,
          "AC7: the other vanilla lines stay (Thorium poison resistance, Cindercloth Mana - spec 3.4: not scaled): %s / %s" % (tt_[1:5], tx_[1:5]))
    Cfg.BASE_ARMOR = False
    tv_, _cv = tl(Data.put(IS("Armor_Copper_Chest", 1), doc("Armor_Copper_Chest", 4), U2))
    Cfg.BASE_ARMOR = True
    check(not any(x_.startswith("Health at") for x_ in tv_) and HA not in tv_ and "Health: 9" in tv_, "AC7: base.armorOn off -> the 0.2 armor lines ('Health: 9')")
    # the render signature: the levelled numbers are in the rendered lines, so a level or curve change re-renders the stack (and only then)
    dv_ = doc("Weapon_Wand_Wood", 6)
    sv1_ = View.apply(IS("Weapon_Wand_Wood", 1), dv_, U1)
    sv2_ = View.apply(sv1_, dv_, U1)
    Cfg.BASE_CURVE = "1:1.0,6:3.0"
    sv3_ = View.apply(sv1_, dv_, U1)
    t3_, _c3 = tl(sv3_)
    Cfg.BASE_CURVE = str(Cfg.CURVE_DEF)
    check(SysJ.identityHashCode(sv1_) == SysJ.identityHashCode(sv2_) and SysJ.identityHashCode(sv3_) != SysJ.identityHashCode(sv1_)
          and "Damage at Lv 6: 18-24" in t3_, "AC7: the tooltip re-renders when the curve changes (Lv 6 = x3 -> 18-24) and stays put otherwise")
    # gear:fn:describe = GearFn mode 0 (setup() puts new GearFn(0) on the bridge); it takes the ItemStack itself
    rr_ = J("GearFn")(JInt(0)).apply(w6_)
    dsc_ = [str(x) for x in rr_] if rr_ is not None else []
    check("Damage at Lv 6: 10-14" in dsc_ and sp6_ in dsc_ and HW not in dsc_, "AC7: gear:fn:describe (the AH tooltip) carries the levelled line + the "
          "spell line, without the hint (no vanilla box there): %s" % dsc_[:5])
    stx_, scl_ = ArrayList(), ArrayList()
    View.statLines("Armor_Copper_Chest", doc("Armor_Copper_Chest", 4), stx_, scl_)
    stx2_, scl2_ = ArrayList(), ArrayList()
    View.statLines("Weapon_Wand_Wood", dv_, stx2_, scl2_)
    check("Health at Lv 4: +14" in [str(x) for x in stx_] and HA not in [str(x) for x in stx_] and "Damage at Lv 6: 10-14" in [str(x) for x in stx2_]
          and HW not in [str(x) for x in stx2_], "AC7: the Reforge page's columns (statLines) show the levelled lines without the hint")
    rd_ = str(Base.describe("Weapon_Wand_Wood", dv_))
    ra_ = str(Base.describe("Armor_Copper_Chest", doc("Armor_Copper_Chest", 10)))
    check(rd_.startswith("base stats: Lv 6 - K 1.0 (family base Weapon_Wand_Wood, band start 1) x F(6) 1.733 x material 1.0 = x1.733 per hit (10-14)")
          and ra_.startswith("base stats: Lv 10 - Health 18 (the item's own 9), resistance 9.1% physical / 9.1% projectile (the item's own 6.5% / 6.5%)"),
          "AC7: /gear read explains the base stats: %s | %s" % (rd_, ra_))
    print("AC7. tooltip lines done")

    # ---- AC8. the VANILLA BLOCK decision (spec R2 / stage 0 check b; Skyy's screenshot shows the client's own 'Damage Data - Basic: 6.0-8.0'
    # under our text). Facts: per stack the server sends only ItemWithAllMetadata (id, quantity, durability, max durability, quality, the
    # metadata JSON); the client's per-stack model ClientItemMetadata has Adventure / CapturedEntity / ItemDisplay / Extra; ItemDisplay (the
    # server's ItemDisplayMetadata) is name + description. The damage / Health / resistance block comes from the ITEM ASSET (ItemBase.weapon
    # basicDamageBreakdown, ItemBase.armor statModifiers / damageResistance), one per item id - nothing per stack can hide or change it.
    # Decision: our line is worded as the real number ("Damage at Lv 6: 10-14") + the grey hint that the box below is vanilla.
    inst_fields = lambda c_: sorted(str(f_.getName()) for f_ in JClass(c_).class_.getDeclaredFields() if not MODc.isStatic(f_.getModifiers()))
    check(inst_fields("com.hypixel.hytale.protocol.ItemWithAllMetadata") == sorted(["itemId", "quantity", "durability", "maxDurability", "quality",
                                                                                  "overrideDroppedItemAnimation", "metadata"]),
          "AC8: per stack the client gets only ItemWithAllMetadata %s - no weapon / armor stats per stack" % inst_fields("com.hypixel.hytale.protocol.ItemWithAllMetadata"))
    check(inst_fields(ENG + "asset.type.item.config.metadata.ItemDisplayMetadata") == ["description", "name"],
          "AC8: the per-stack ItemDisplay is name + description only (the server's ItemDisplayMetadata)")
    ib_ = inst_fields("com.hypixel.hytale.protocol.ItemBase")
    check("weapon" in ib_ and "armor" in ib_ and "basicDamageBreakdown" in inst_fields("com.hypixel.hytale.protocol.ItemWeapon")
          and "damageResistance" in inst_fields("com.hypixel.hytale.protocol.ItemArmor") and "statModifiers" in inst_fields("com.hypixel.hytale.protocol.ItemArmor"),
          "AC8: the vanilla block's numbers ride on the ITEM ASSET packet (ItemBase.weapon.basicDamageBreakdown, ItemBase.armor.statModifiers / damageResistance)")
    cl_dir = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client")
    lang_ = os.path.join(cl_dir, "Data", "Shared", "Language", "en-US", "client.lang")
    exe_ = os.path.join(cl_dir, "HytaleClient.exe")
    if os.path.isfile(lang_) and os.path.isfile(exe_):
        lt_ = open(lang_, encoding="utf-8", errors="replace").read()
        eb_ = open(exe_, "rb").read()
        props_ok = all(eb_.find(x_) >= 0 for x_ in (b"ClientItemMetadata", b"get_Adventure", b"get_CapturedEntity", b"get_ItemDisplay", b"get_Extra"))
        check("itemTooltip.stats.damage.title = Damage Data" in lt_ and "itemTooltip.stats.damage.onHit" in lt_ and "itemTooltip.stats.Health = Health: {value}" in lt_
              and "itemTooltip.damageCauseResistance.physical = Physical Resistance: {value}" in lt_ and props_ok,
              "AC8: the client (read only): its own tooltip block = 'Damage Data / Basic', 'Health:', 'Physical Resistance:' (client.lang); its per-stack "
              "model ClientItemMetadata = Adventure / CapturedEntity / ItemDisplay / Extra (HytaleClient.exe strings)")
        del eb_
    else:
        print("AC8. note: the client files are not at %s - the client-side evidence was skipped" % cl_dir)
    check(i6_ >= 0 and HW not in t6_ and HA not in ta_,
          "AC8: 0.2.2 decision (Skyy: 'hide it instead of leaving a note') - per STACK nothing can hide the box (above), so no note at all; the box "
          "is hidden per item TYPE at run time (GearBox, section AD3)")
    print("AC8. vanilla block: not hideable per stack (evidence above) -> 0.2.2 hides it per item type (AD3), no note")

    # ---- AC9. migrate021 (the one-time config.properties update) on a scratch COPY of the live file and on derived cases
    ACD = os.path.join(SCRATCH, "work", "ac021")

    def acase(name_, data_):
        cfg_quiet()
        shutil.rmtree(os.path.join(ACD, name_), ignore_errors=True)
        d_ = os.path.join(ACD, name_, "mods", "Skyy_SkyyGear")
        os.makedirs(d_)
        f_ = os.path.join(d_, "config.properties")
        if data_ is not None:
            open(f_, "wb").write(data_)
        Cfg.DIR = Paths.get(d_)
        Cfg.FILE = Paths.get(f_)
        return d_, f_
    LSB = [str(Cfg.LS_MARK)] + [x_ for p_ in zip([str(x) for x in Cfg.LS_ROWC], [str(x) for x in Cfg.LS_ROWL]) for x_ in p_] + [str(Cfg.LS_TBLC)] + [str(x) for x in Cfg.LS_TBLL]
    INFO21 = ("config.properties: added the 0.2.1 level stats settings (part.base, base.mode, base.curve, base.matBonus, base.armorOn, base.resCurve, "
              "base.armor.Head, base.armor.Chest, base.armor.Legs, base.armor.Hands) with their built-in defaults - weapon damage and armor Health / "
              "resistance now grow with each item's level (Server Setup -> Gear -> Level stats; part.base off = vanilla numbers); the old file is in config-history")

    def exp21(text_):
        raw_ = text_.split("\n")
        last_ = max(i_ for i_, l_ in enumerate(raw_) if l_.rstrip("\r").split("=", 1)[0].strip() == "level.armorNative")
        cr_ = "\r" if raw_[last_].endswith("\r") else ""
        return "\n".join(raw_[:last_ + 1] + [x_ + cr_ for x_ in LSB] + raw_[last_ + 1:])
    live21 = open(LIVE, "rb").read() if os.path.isfile(LIVE) else None
    # 0.2.2: 0.2.1 is deployed and has started in game - the live file carries the 0.2.1 block now, so the replay runs on the live file AS IT
    # WAS BEFORE it: its "before the 0.2.1 level stats" copy in the live config-history (or a deploy backup) - the X / Y / Z7 / AB7 rule
    if live21 is not None and str(Cfg.LS_MARK_ID).encode("latin-1") in live21:
        h21_, hd21_ = hist_copy("before the 0.2.1 level stats")
        check(h21_ is not None and str(Cfg.LS_MARK_ID).encode("latin-1") not in h21_,
              "AC9: 0.2.2 - the live file already holds the 0.2.1 block (deployed); its 'before the 0.2.1 level stats' History copy is found for the replay (%s)" % hd21_)
        live21 = h21_
    if live21 is not None:
        lt21 = live21.decode("latin-1")
        d, f = acase("a-live", live21)
        hp0_, cl0_ = baks(d), clog(d)
        r21 = str(Cfg.migrate021())
        g21 = rb(f)
        check(str(Cfg.LS_MARK_ID) not in lt21 and g21 == exp21(lt21).encode("latin-1"),
              "AC9(a): the live copy gets exactly the 0.2.1 block (marker + 6 settings + the base.armor table) right under level.armorNative, every other byte kept")
        check(r21 == INFO21, "AC9(a): one INFO line: %s" % r21)
        print("AC9. INFO line the live file produces: [SkyyGear] " + r21[:160] + " ...")
        po_, pn_ = props(lt21), props(g21.decode("latin-1"))
        check(all(pn_.get(k_) == v_ for k_, v_ in po_.items()) and sorted(set(pn_) - set(po_)) == sorted([str(x) for x in Cfg.LS_ROWK] + ["base.armor." + s_ for s_ in ("Head", "Chest", "Legs", "Hands")]),
              "AC9(a): every old value kept; the 10 new keys hold their defaults")
        b1_, i1_ = baks(d), idx(d)
        check(len(b1_) == len(hp0_) + 1 and rb(os.path.join(d, "config-history", b1_[-1])) == live21 and i1_[-1].split("\t")[3:] == ["SkyyGear 0.2.1", "before the 0.2.1 level stats"]
              and clog(d) == cl0_, "AC9(a): one History copy (the old bytes, 'before the 0.2.1 level stats'), no config-changes.log line (new settings start at their defaults)")
        Cfg.load()
        check(bool(Cfg.PART_BASE) and str(Cfg.BASE_MODE) == "shape" and [float(x) for x in Cfg.BA_H] == [5.0, 9.0, 7.0, 4.0], "AC9(a): the loader reads the new lines")
        check(str(Cfg.migrate021()) == "" and rb(f) == g21 and len(baks(d)) == len(b1_), "AC9(b): a second start changes nothing")
        pfr_ = props(str(Cfg.defaultsText()))
        check(all(pn_.get(k_) == pfr_.get(k_) for k_ in [str(x) for x in Cfg.LS_ROWK] + ["base.armor." + s_ for s_ in ("Head", "Chest", "Legs", "Hands")]),
              "AC9(a): the live copy now has the same 0.2.1 values as a fresh file")
        # CRLF
        tcr_ = lt21.replace("\r\n", "\n").replace("\n", "\r\n")
        d, f = acase("b-crlf", tcr_.encode("latin-1"))
        Cfg.migrate021()
        gcr_ = rb(f)
        check(gcr_ == exp21(tcr_).encode("latin-1") and gcr_.count(b"\n") == gcr_.count(b"\r\n"), "AC9(c): a CRLF file gets the block with CRLF on every new line")
        # keys typed by hand before the update: kept + noted, never doubled
        th_ = lt21 + ("" if lt21.endswith("\n") else "\n") + "part.base=false\nbase.armor.chest=12,7\n"
        d, f = acase("c-typed", th_.encode("latin-1"))
        rh_ = str(Cfg.migrate021()).split("\n")
        ph_ = props(rb(f).decode("latin-1"))
        check(ph_.get("part.base") == "false" and ph_.get("base.armor.chest") == "12,7" and "base.armor.Chest" not in ph_ and ph_.get("base.armor.Head") == "5,3.6"
              and rh_[1:] == ["part.base is already in the file - kept", "base.armor.Chest is already in the file - kept"] and "part.base, " not in rh_[0],
              "AC9(d): values typed before the update are kept + noted once, the block lacks them: %s" % rh_)
    else:
        print("AC9. note: no live config.properties at %s - the live copy cases were skipped" % LIVE)
    # no file -> the loader writes the fresh 0.2.1 file (marker inside) -> never updates
    d, f = acase("d-fresh", None)
    check(str(Cfg.migrate021()) == "" and not os.path.exists(f), "AC9(e): no file -> nothing written")
    Cfg.load()
    ff21 = rb(f)
    check(ff21 == str(Cfg.defaultsText()).encode("utf-8") and str(Cfg.migrate021()) == "" and rb(f) == ff21 and Cfg.lsUpdate(ff21.decode("latin-1")) is None,
          "AC9(e): the fresh 0.2.1 file never updates")
    # the pure text step's anchors and the end-of-file continuation trap
    BLKt = "\n".join(LSB)

    def lu(t_):
        r_ = Cfg.lsUpdate(t_)
        return None if r_ is None else str(r_[0])
    check(lu("a=1\nlevel.armorNative=true\nb=2\n") == "a=1\nlevel.armorNative=true\n" + BLKt + "\nb=2\n", "AC9(f): right after level.armorNative")
    check(lu("level.default=0\nlevel.noSkills=pass\nx=1\n") == "level.default=0\nlevel.noSkills=pass\n" + BLKt + "\nx=1\n", "AC9(f): no level.armorNative -> after the last level.* entry")
    check(lu("a=1\nb=2") == "a=1\nb=2\n" + BLKt and lu("") == BLKt + "\n", "AC9(f): no anchor -> the end of the file")
    BSL = chr(92)
    tq_ = "a=1\nlevel.armorNative=true" + BSL + "\n"
    rq_ = lu(tq_)
    check(rq_ == "a=1\n" + BLKt + "\nlevel.armorNative=true" + BSL + "\n" and props(rq_).get("level.armorNative") == props(tq_).get("level.armorNative"),
          "AC9(f): a still-open continued anchor at the end keeps its bytes last, the block goes before it (the 0.1.1 finding 4 trap)")
    check(Cfg.lsUpdate("# SkyyGear 0.2.1 level stats (done)\nlevel.armorNative=true\n") is None and lu("x=SkyyGear 0.2.1 level stats\n") is not None,
          "AC9(f): a comment with the marker id = done; the id inside a value is no marker")
    import random as _rd
    rg_ = _rd.Random(21)
    bad_ = []
    NK21 = set([str(x) for x in Cfg.LS_ROWK] + ["base.armor." + s_ for s_ in ("Head", "Chest", "Legs", "Hands")])
    for n_ in range(400):
        ls_ = []
        for _q in range(rg_.randint(0, 12)):
            ls_.append(rg_.choice(["a=1", "level.armorNative=" + rg_.choice(["true", "false", "maybe"]), "level.vanilla=true", "# c", "! c", "",
                                   "part.base=" + rg_.choice(["true", "false"]), "base.armor.Legs=1,2", "base.armor.LEGS=3,4", "base.curve=1:2",
                                   "x=" + BSL, "  y : z", "level.armorNative=true" + BSL, "  cont", "base.mode=off"]))
        t_ = rg_.choice(["\n", "\r\n"]).join(ls_) + rg_.choice(["", "\n"])
        r_ = Cfg.lsUpdate(t_)
        if r_ is None:
            bad_.append(("null", t_))
            continue
        po_, pn_ = props(t_), props(str(r_[0]))
        newk_ = set(pn_) - set(po_)
        if any(pn_.get(k_) != v_ for k_, v_ in po_.items()) or not newk_ <= NK21 or str(r_[0]).count(str(Cfg.LS_MARK_ID)) != 1 \
                or Cfg.lsUpdate(str(r_[0])) is not None:
            bad_.append(("diff", t_))
    check(not bad_, "AC9(g): 400 random files: every value java.util.Properties reads stays, only 0.2.1 keys are added, one marker, a second run "
                    "does nothing (%d bad: %r)" % (len(bad_), bad_[:2]))
    # History blocked -> no rewrite (WARN), the next start updates
    if live21 is not None:
        d, f = acase("h-blocked", live21)
        open(os.path.join(d, "config-history"), "wb").write(b"not a folder")
        Log.FILE = Paths.get(os.path.join(d, "gear.log"))
        rbk_ = str(Cfg.migrate021())
        check(rbk_ == "" and rb(f) == live21, "AC9(h): History blocked -> the file stays untouched, nothing written")
        Log.flush()
        gl21 = ""
        for _w in range(30):
            gl21 = open(os.path.join(d, "gear.log"), encoding="utf-8").read() if os.path.exists(os.path.join(d, "gear.log")) else ""
            if "NOT given the 0.2.1 level stats settings" in gl21:
                break
            time.sleep(0.1)
        check("NOT given the 0.2.1 level stats settings" in gl21 and "the next start tries again" in gl21, "AC9(h): one WARN says why")
        os.remove(os.path.join(d, "config-history"))
        check(str(Cfg.migrate021()) == INFO21 and rb(f) == exp21(live21.decode("latin-1")).encode("latin-1"), "AC9(h): the next start updates")
        Log.FILE = None
    # the rows are LIVE through the config kit itself (Server Setup's set / tset ops on config:fn:SkyyGear): the next hit / tooltip uses them
    d, f = acase("i-kit", str(Cfg.defaultsText()).encode("utf-8"))
    Cfg.load()
    CfgPubC = J("CfgPub")
    CfgPubC.start(Paths.get(os.path.dirname(d)), None)
    fnc_ = bridge.get("config:fn:SkyyGear")
    r_c = fnc_.apply(OAc(["set", "base.curve", "1:1.0,6:3.0", None, "console", "yes", "console"]))
    f6_ = F_(6)
    r_b = fnc_.apply(OAc(["set", "base.curve", "1:1,2", None, "console", "yes", "console"]))
    r_m = fnc_.apply(OAc(["set", "base.matBonus", "1.5", None, "console", "yes", "console"]))
    b10_ = float(Base.bonus(10))
    r_o = fnc_.apply(OAc(["set", "base.mode", "off", None, "console", "yes", "console"]))
    on_ = bool(Base.on())
    r_t = fnc_.apply(OAc(["tset", "base.armor", "Chest", "12|7", None, "console", "yes", "console"]))
    r_x = fnc_.apply(OAc(["tset", "base.armor", "Feet", "1|1", None, "console", "yes", "console"]))
    r_p = fnc_.apply(OAc(["set", "part.base", "false", None, "console", "", "console"]))
    CfgPubC.flush()
    tk_ = rb(f).decode("latin-1")
    check(str(r_c[0]) == "ok" and f6_ == 3.0 and str(r_b[0]) == "bad" and str(Cfg.BASE_CURVE) == "1:1.0,6:3.0" and str(r_m[0]) == "ok" and abs(b10_ - 1.15) < 1e-9
          and str(r_o[0]) == "ok" and not on_ and str(r_t[0]) == "ok" and abs(float(Cfg.BA_H[1]) - 12.0) < 1e-9 and str(r_x[0]) == "bad"
          and str(r_p[0]) == "confirm" and bool(Cfg.PART_BASE)
          and "\nbase.curve=1:1.0,6:3.0\n" in tk_ and "\nbase.mode=off\n" in tk_ and "\nbase.armor.Chest=12,7\n" in tk_,
          "AC9(i): Server Setup ops apply at once - base.curve (F(6) = 3 at the next hit; a bad curve refused), base.matBonus, base.mode off, a "
          "base.armor row (a Feet row refused); part.base asks to confirm before switching off; the file keeps the lines: %s"
          % [str(x_[0]) for x_ in (r_c, r_b, r_m, r_o, r_t, r_x, r_p)])
    Cfg.FILE = None
    Cfg.DIR = None
    Cfg.apply(Props(), False)
    print("AC9. migrate021 + live rows done")

    # ---- AC10. class byte-compare 0.2 -> 0.2.1 (Z10's machinery: instruction text with constant-pool numbers stripped, fields with their
    # types and constant values): every difference must be one of the listed 0.2.1 parts (a member outside this list = FAIL)
    jar02c = os.path.join(HERE, "SkyyGear-0.2.jar")
    # 0.2.2: this stays the HISTORICAL 0.2 -> 0.2.1 compare of the two SHIPPED jars (AD10 compares 0.2.1 -> 0.2.2)
    jar021s = os.path.join(HERE, "SkyyGear-0.2.1.jar")
    if os.path.isfile(jar02c) and os.path.isfile(jar021s):
        pa5 = Pool(False)
        pa5.appendClassPath(jar02c)
        pa5.appendClassPath(B.SERVER_JAR)
        pa5.appendSystemPath()
        pb5 = Pool(False)
        pb5.appendClassPath(jar021s)
        pb5.appendClassPath(B.SERVER_JAR)
        pb5.appendSystemPath()
        n02c = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar02c).namelist() if n_.endswith(".class"))
        n021 = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar021s).namelist() if n_.endswith(".class"))
        add5 = sorted(c_[len(PKG):] for c_ in set(n021) - set(n02c))
        gone5 = sorted(set(n02c) - set(n021))
        diffs5 = {}
        for cn_ in sorted(set(n02c) & set(n021)):
            ma_, mb_ = cls_members(pa5, cn_), cls_members(pb5, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs5[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        DS = "Lcom/hypixel/hytale/server/core/modules/entity/damage/DamageCause;"
        ICs = "Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;"
        ISs = "Lcom/hypixel/hytale/server/core/inventory/ItemStack;"
        WLs = "Lcom/hypixel/hytale/server/core/universe/world/World;"
        HSIG = "(ILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/system/EcsEvent;)V"
        EXPECT021 = {
            # config kit (tools/skyycfg.py, regenerated from the rows): the seven new rows, the new category, VERSION 0.2 -> 0.2.1
            "CfgFile": ["~<clinit>"],
            "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # /gear read prints the base stats
            "GearAdmin": ["~m read(Lcom/hypixel/hytale/server/core/universe/PlayerRef;" + ISs + ")V"],
            # stage 3: the Health delta in the lock want, the per-stack resistance (fix / levelRes / addRes / resDelta / hasResDelta / resBroken)
            "GearArmor": ["+m addRes(Ljava/util/Map;Ljava/lang/String;F)V",
                          "+m fix(Ljava/util/UUID;FF" + DS + ICs + WLs + "ZLcom/hypixel/hytale/server/core/entity/effect/EffectControllerComponent;)F",
                          "+m hasResDelta(Ljava/util/UUID;" + ICs + ")Z", "+m healthDelta(Ljava/util/UUID;" + ISs + "F)F",
                          "+m levelRes(Ljava/util/UUID;" + ICs + "Ljava/util/Map;Z" + WLs + ")V", "~m lockSums(Ljava/util/UUID;" + ICs + "F)Ljava/util/HashMap;",
                          "+m resBroken(" + WLs + ")F", "+m resDelta(Ljava/util/UUID;" + ISs + "Ljava/lang/String;)F"],
            "GearArmorSys": ["~m handle" + HSIG],
            # the rows' fields, the Lv 1 armor table, the curves, the migrate021 constants + methods, the loader, the default text
            "GearCfg": ["~<clinit>", "+f BASE_ARMOR", "+f BASE_CURVE", "+f BASE_MAT", "+f BASE_MODE", "+f BASE_RES", "+f BA_H", "+f BA_R", "+f BA_SLOT",
                        "+f CURVE_DEF", "+f DBA_H", "+f DBA_R", "+f LS_MARK", "+f LS_MARK_ID", "+f LS_ROWC", "+f LS_ROWK", "+f LS_ROWL", "+f LS_TBLC",
                        "+f LS_TBLL", "+f LS_WHO", "+f PART_BASE", "+f RES_DEF", "~m apply(Ljava/util/Properties;Z)V", "+m baseText()Ljava/lang/String;",
                        "+m checkArmorBase(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "+m checkCurve(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                        "+m curvePts(Ljava/lang/String;)[Ljava/lang/Object;", "~m defaultsText()Ljava/lang/String;", "+m lsUpdate(Ljava/lang/String;)[Ljava/lang/Object;",
                        "+m migrate021()Ljava/lang/String;"],
            # the family base table
            "GearDefs": ["~<clinit>", "+f FB_FAM", "+f FB_ID"],
            # the lock want no longer gated by level.armorNative alone (lockSums decides), the setup WARN texts
            "GearFx": ["~m armorPass(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/component/CommandBuffer;Lcom/hypixel/hytale/component/Ref;" + ICs + "Z)V",
                       "~m lowerNow(Ljava/util/UUID;Lcom/hypixel/hytale/server/core/modules/entitystats/EntityStatMap;" + ICs + "F)V",
                       "~m setup(Lcom/hypixel/hytale/server/core/plugin/JavaPlugin;)V"],
            # stage 2: the weapon branch (level first, then the 0.2 chain) as a static method
            "GearHit": ["+m weaponHit(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;Ljava/util/UUID;Lcom/hypixel/hytale/server/core/universe/PlayerRef;" + ISs
                        + "ZLcom/skyy/gear/GearShot;Lcom/skyy/gear/GearShot;" + ICs + ")[Ljava/lang/Object;"],
            "GearHitSys": ["~m handle" + HSIG],
            # review of 0.2.1 finding 1: the records of the weapon that owns the hit's damage step (calcOf / cands / pickFor; pick = pickFor
            # with no step) + the clamp of a picked record (minMult)
            "GearShotTrack": ["+m calcOf(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;)Ljava/lang/Object;",
                              "+m cands(Ljava/util/UUID;Ljava/lang/Object;)Ljava/util/ArrayList;", "+m minMult(Ljava/util/UUID;Ljava/lang/Object;)D",
                              "~m pick(Ljava/util/UUID;" + ICs + ")Lcom/skyy/gear/GearShot;",
                              "+m pickFor(Ljava/util/UUID;" + ICs + "Ljava/lang/Object;)Lcom/skyy/gear/GearShot;"],
            # the tooltip: levelled damage / armor lines + the hint
            "GearView": ["~m apply(" + ISs + "Lorg/bson/BsonDocument;Ljava/util/UUID;)" + ISs, "+m hints(Ljava/util/ArrayList;Ljava/util/ArrayList;)V",
                         "+m levelArmorLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;)Z", "+m otherArmorLines(Ljava/lang/String;Ljava/util/ArrayList;)V",
                         "~m statLines(Ljava/lang/String;Lorg/bson/BsonDocument;Ljava/util/ArrayList;Ljava/util/ArrayList;)V"],
            # setup(): migrate021 after migrate02, the ready line's base part
            "SkyyGearPlugin": ["~m setup()V"],
        }
        check(add5 == ["GearBase"] and not gone5, "AC10: new classes = GearBase (base stats from the level), none removed: %s / %s" % (add5, gone5))
        unexp5 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT021.get(c_, [])]) for c_, v_ in diffs5.items())
        unexp5 = dict((c_, v_) for c_, v_ in unexp5.items() if v_)
        missing5 = dict((c_, [m_ for m_ in v_ if m_ not in diffs5.get(c_, [])]) for c_, v_ in EXPECT021.items())
        missing5 = dict((c_, v_) for c_, v_ in missing5.items() if v_)
        check(not unexp5, "AC10: no difference outside the listed 0.2.1 parts: %s" % unexp5)
        check(not missing5, "AC10: every listed 0.2.1 part is really in the jar: %s" % missing5)
        ea5 = [n_ for n_ in zipfile.ZipFile(jar02c).namelist() if not n_.endswith(".class")]
        eb5 = [n_ for n_ in zipfile.ZipFile(jar021s).namelist() if not n_.endswith(".class")]
        za5, zb5 = zipfile.ZipFile(jar02c), zipfile.ZipFile(jar021s)
        ediff5 = sorted(n_ for n_ in set(ea5) | set(eb5) if n_ not in ea5 or n_ not in eb5 or za5.read(n_) != zb5.read(n_))
        check(ediff5 == ["manifest.json"] and sorted(ea5) == sorted(eb5), "AC10: non-class entries: only manifest.json differs (recipes + quality assets byte-identical): %s" % ediff5)
        print("AC10. class compare 0.2 -> 0.2.1: %d classes changed (%s), new %s" % (len(diffs5), ", ".join(sorted(diffs5)), add5))
    else:
        check(False, "AC10: SkyyGear-0.2.jar not found - the class compare could not run")

    # ---- AC11. wiring (bytecode)
    su5 = mcode("SkyyGearPlugin", "setup")
    o5 = [su5.find("GearCfg.migrate02("), su5.find("GearCfg.migrate021("), su5.find("GearCfg.load(")]
    check(all(x_ >= 0 for x_ in o5) and o5 == sorted(o5) and "GearCfg.baseText(" in su5, "AC11: setup(): migrate02 -> migrate021 -> load; the ready line names the base stats (%s)" % o5)
    hs5 = mcode("GearHitSys", "handle")
    check(0 <= hs5.find("GearGate.popup(") < hs5.find("GearHit.weaponHit(") and "GearArmor.hasResDelta(" in hs5 and "GearArmor.hasInactive(" in hs5,
          "AC11: GearHitSys - the gate block (popup + return) comes BEFORE the weapon branch; the pre-armor amount is kept for inactive pieces or a per-stack resistance")
    wh5 = mcode("GearHit", "weaponHit")
    check(0 <= wh5.find("GearBase.weaponMult(") < wh5.find("GearCfg.PART_STATS") < wh5.find("GearHit.hitAmount("),
          "AC11: GearHit.weaponHit - the level multiplier first (own switch inside weaponMult), then part.stats, then the 0.2 chain")
    # review of 0.2.1 finding 1: the picked record's multiplier is clamped between weaponMult and the first setAmount; GearHitSys picks by
    # the damage step; pick() is pickFor with no step; cands asks GearChg (step, walked, the re-walk)
    cd5 = mcode("GearShotTrack", "cands")
    check("GearShotTrack.pickFor(" in hs5 and "GearShotTrack.calcOf(" in hs5 and "GearShotTrack.pick(" not in hs5
          and 0 <= wh5.find("GearBase.weaponMult(") < wh5.find("GearShotTrack.minMult(") < wh5.find("Damage.setAmount(") and "GearShotTrack.calcOf(" in wh5
          and "GearShotTrack.pickFor(" in mcode("GearShotTrack", "pick") and "aconst_null" in mcode("GearShotTrack", "pick")
          and "GearShotTrack.cands(" in mcode("GearShotTrack", "pickFor") and "GearStats.totals(" in mcode("GearShotTrack", "pickFor")
          and "GearShotTrack.cands(" in mcode("GearShotTrack", "minMult") and "GearBase.weaponMult(" in mcode("GearShotTrack", "minMult")
          and all(x_ in cd5 for x_ in ("GearChg.ensure(", "GearChg.step(", "GearChg.walked(", "GearChg.rewalk(")),
          "AC11: finding 1 - GearHitSys picks with pickFor(calcOf(d)); weaponHit clamps with minMult between weaponMult and the first setAmount; "
          "pick(u, arm) = pickFor(u, arm, null); cands asks GearChg (ensure, step, walked, rewalk)")
    sl5x = mcode("GearView", "statLines")
    sb5 = mcode("GearBase", "spellBase")
    check("GearBase.asVanilla(" in sl5x and "GearBase.spellRange(" in sl5x and "GearChg.ensure(" in sb5 and "Projectile.getDamage(" in sb5
          and "GearBase.mult(" in mcode("GearBase", "spellRange") and "GearBase.mult(" in mcode("GearBase", "asVanilla")
          and "GearBase.armorAsVanilla(" in mcode("GearView", "levelArmorLines"),
          "AC11: findings 2 + 3 - statLines asks GearBase.asVanilla (the plain line at m = 1) and spellRange (GearChg's launches x Projectile.getDamage x mult); "
          "levelArmorLines asks armorAsVanilla")
    as5 = mcode("GearArmorSys", "handle")
    check("GearArmor.fix(" in as5 and "GearArmor.reduce(" not in as5 and "GearCfg.ARMOR_NATIVE" not in as5, "AC11: GearArmorSys hands the correction to GearArmor.fix")
    ls5 = mcode("GearArmor", "lockSums")
    check("GearArmor.healthDelta(" in ls5 and "GearCfg.ARMOR_NATIVE" in ls5 and "GearBase.armorOn(" in ls5, "AC11: GearArmor.lockSums = the inactive natives (level.armorNative) + the Health deltas (base.armorOn)")
    check(all("GearArmor.lockSums(" in mcode("GearFx", m_) and "GearCfg.ARMOR_NATIVE" not in mcode("GearFx", m_) for m_ in ("armorPass", "lowerNow")),
          "AC11: GearFx.armorPass / lowerNow ask lockSums for the whole want")
    sl5 = mcode("GearView", "statLines")
    ap5 = mcode("GearView", "apply")
    check("GearBase.range(" in sl5 and "GearView.levelArmorLines(" in sl5 and "GearBase.on(" in sl5 and "HINT" not in sl5
          and 0 <= ap5.find("GearView.lines(") < ap5.find("GearView.sig(") and "GearView.hints(" not in ap5,
          "AC11: the tooltip lines come from GearBase; GearView.apply = lines -> sig (0.2.2: no hints step)")
    check("GearBase.describe(" in mcode("GearAdmin", "read"), "AC11: /gear read prints GearBase.describe")
    print("AC10/AC11. class compare + wiring done")

    # ======================================================================================================================== AD 0.2.2
    # SkyyGear 0.2.2 = Skyy's three LOCKED asks of 2026-10-03: the wand / staff SHOT LINES (SkyyArmory's real bridge + kit), NO NOTE + the
    # vanilla Damage Data box hidden per item TYPE (GearBox), and the CRIT EFFECTS (research/Crit-Indicator-Research.md). Every new path is
    # EXECUTED: the real ArmoryInfoFn / ArmoryCfg / SkyyArmory config kit from the pinned jar, real engine Item / ItemWeapon /
    # DamageBreakdown / protocol packets, a real LoadedAssetsEvent, real Damage objects through the REAL GearHitSys.handle, the REAL
    # GearCritSys / GearCritTick / GearCritClean, the vanilla DamageSystems$EntityUIEvents queueing its number after ours, real
    # EntityViewer / UIComponentList / CombatTextUpdate / UIComponentsUpdate objects, the crit style asset DECODED by the engine's own
    # EntityUIComponent codec (+ its validators), ParticleUtil sending real SpawnParticleSystem packets to the players' packet handlers.
    print("AD. 0.2.2: tooltip shots, no note, the vanilla box, crit effects")
    AD_DIR = os.path.join(SCRATCH, "work", "ad022")
    shutil.rmtree(AD_DIR, ignore_errors=True)
    os.makedirs(AD_DIR)
    ABox, ACrit, ACSys, ACTick, ACClean = J("GearBox"), J("GearCrit"), J("GearCritSys"), J("GearCritTick"), J("GearCritClean")
    bsrc22 = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    GOLD_CURVE = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"

    def pyF(lv_):
        pts_ = [(float(a_), float(b_)) for a_, b_ in (p_.split(":") for p_ in GOLD_CURVE.split(","))]
        if lv_ <= pts_[0][0]:
            return pts_[0][1]
        for (l0_, v0_), (l1_, v1_) in zip(pts_, pts_[1:]):
            if lv_ <= l1_:
                return v0_ + (v1_ - v0_) * (lv_ - l0_) / (l1_ - l0_)
        return pts_[-1][1]

    def pyBonus(st_):
        return 1.0 if st_ <= 1 else 1.0 + 0.3 * st_ / 100.0

    # ---- AD0. the SkyyArmory model: its REAL classes from the pinned jar (read only)
    have_arm = os.path.isfile(ARMORY_JAR)
    check(have_arm, "AD0: the pinned SkyyArmory %s jar is on the JVM classpath (%s)" % (ARMORY_PIN, ARMORY_JAR))
    AP = "com.skyy.armory."
    ADefs, ACfgA, AInfo, ARows, AFn, APub = (JClass(AP + "ArmoryDefs"), JClass(AP + "ArmoryCfg"), JClass(AP + "ArmoryInfoFn"), JClass(AP + "CfgRows"),
                                            JClass(AP + "CfgFn"), JClass(AP + "CfgPub"))
    akeys_ = [str(k_) for k_ in ARows.KEYS]
    arow_ = dict((str(k_), (str(t_), str(d_), str(f_))) for k_, t_, d_, f_ in zip(ARows.KEYS, ARows.TYPES, ARows.DEFS, ARows.FLAGS))
    check(arow_.get("part.tune") == ("bool", "true", "live,part,danger") and arow_.get("quick.damage", ("",))[:2] == ("int", "20")
          and "tune.wand" in akeys_ and "tune.staff" in akeys_,
          "AD0: SkyyArmory's own kit rows the shot lines read: part.tune (bool, true) + quick.damage (int, 20) + the two tune tables (%s)"
          % [arow_.get(k_) for k_ in ("part.tune", "quick.damage")])
    # its projectile files (fully resolved, Damage on each) into the same legacy Projectile map AC7 built from Assets.zip
    aprj = {}
    with zipfile.ZipFile(ARMORY_JAR) as za_:
        for n_ in za_.namelist():
            if n_.startswith("Server/Projectiles/") and n_.endswith(".json"):
                aprj[os.path.basename(n_)[:-5]] = json.loads(za_.read(n_).decode("utf-8-sig"))
    for p_, j_ in aprj.items():
        po_ = acalloc(LPRJc.class_.getName())
        acf(LPRJc.class_.getName(), "id").set(po_, p_)
        acf(LPRJc.class_.getName(), "damage").setInt(po_, JInt(int(j_["Damage"])))
        fz(DAMz, "assetMap").get(pmap_).put(p_, po_)
    METALS_A = [str(x_) for x_ in ADefs.METALS]
    check(METALS_A == ["Wood", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"] and len(aprj) == 31
          and int(LPRJc.getAssetMap().getAsset("SkyyArmory_Orb_Copper").getDamage()) == 56
          and int(LPRJc.getAssetMap().getAsset("SkyyArmory_QuickOrb_Wood").getDamage()) == 5,
          "AD0: SkyyArmory's 31 projectiles in the projectile map (Copper orb 56, Wood quick orb 5 - its baked ladder) + the 8 metals")
    # its config kit, started for real on a scratch data folder (CfgPub.start publishes config:def / fn / epoch:SkyyArmory on the shared bridge)
    akd = os.path.join(AD_DIR, "mods")
    os.makedirs(akd)
    ACfgA.DIR = Paths.get(os.path.join(akd, "Skyy_SkyyArmory"))
    ACfgA.FILE = ACfgA.DIR.resolve("config.properties")
    ACfgA.load()
    arm_kit = True
    try:
        APub.start(Paths.get(akd), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyArmory"))
    except Exception as ex_:
        arm_kit = False
        print("AD0. note: SkyyArmory's kit could not start in the bare JVM (%s)" % ex_)
    afn_ = bridge.get("config:fn:SkyyArmory")
    check(arm_kit and afn_ is not None and str(afn_.apply(JArray(JObject)(["get", "part.tune"]))) == "true"
          and str(afn_.apply(JArray(JObject)(["get", "quick.damage"]))) == "20",
          "AD0: SkyyArmory's REAL config kit answers the read-only get op on the bridge (part.tune true, quick.damage 20)")

    def aset(key_, val_):
        """a console change through SkyyArmory's own kit (who = null + via console, the contract's console path)"""
        r_ = afn_.apply(JArray(JObject)(["set", key_, val_, None, "harness", "yes", "console"]))
        return None if r_ is None else str(r_[0])
    bridge.put("armory:fn:info", AInfo())

    # ---- AD1. THE SHOT LINES: every SkyyArmory wand + staff and the Wood wand (+ its Rotten / Tribal twins) at several levels
    def shot_lines(iid_, lv_):
        d_ = doc(iid_, lv_)
        txt_, col_ = ArrayList(), ArrayList()
        View.lines(iid_, d_, U1, txt_, col_)
        return [str(x_) for x_ in txt_]

    BANDS_A = {"Wood": (1, 13), "Copper": (10, 18), "Iron": (15, 23), "Thorium": (20, 28), "Cobalt": (25, 38), "Adamantite": (35, 43),
               "Mithril": (40, 49), "Onyxium": (40, 49)}
    W_C, W_Q, W_CD, W_QD = [list(int(x_) for x_ in a_) for a_ in (ADefs.W_C, ADefs.W_Q, ADefs.W_CD, ADefs.W_QD)]
    S_C, S_Q, S_CD, S_QD = [list(int(x_) for x_ in a_) for a_ in (ADefs.S_C, ADefs.S_Q, ADefs.S_CD, ADefs.S_QD)]
    check(W_C == [5, 10, 15, 25, 40, 60, 85, 85] and W_Q == [1, 2, 3, 5, 8, 12, 17, 17] and S_C == [10, 20, 30, 50, 80, 120, 170, 170],
          "AD1: SkyyArmory's ladder from its jar (wand Mana 5..85 / quick 1..17, staff 10..170) = Skyy's LOCKED costs")

    def expect(kind_, metal_, lv_, tune_=100.0, ton_=True, qpct_=20.0, base_on=True, iid_=None, start_=None):
        i_ = METALS_A.index(metal_)
        if kind_ == "wand":
            cm_, qm_, cd_, qd_ = W_C[i_], W_Q[i_], W_CD[i_], W_QD[i_]
            cp_ = "Skeleton_Mage_Corruption_Orb" if metal_ == "Wood" else "SkyyArmory_Orb_" + metal_
            qp_ = "SkyyArmory_QuickOrb_" + metal_
        else:
            cm_, qm_, cd_, qd_ = S_C[i_], S_Q[i_], S_CD[i_], S_QD[i_]
            cp_, qp_ = "SkyyArmory_StaffOrb_" + metal_, "SkyyArmory_StaffQuickOrb_" + metal_
        cb_ = prj_dmg(cp_) if cp_ in prj_json else int(aprj[cp_]["Damage"])
        qb_ = int(aprj[qp_]["Damage"])
        st_ = BANDS_A[metal_][0] if start_ is None else start_
        m_ = pyF(lv_) * pyBonus(st_) if base_on else 1.0
        cf_ = tune_ / 100.0 if (ton_ and cp_.startswith("SkyyArmory_")) else 1.0
        qf_ = tune_ / 100.0 * qpct_ / 20.0 if ton_ else 1.0
        at_ = (" damage at Lv %d" % lv_) if base_on else " damage"
        return ("Charged shot - %d Mana - %d%s" % (cm_, rnd(cb_ * cf_ * m_), at_), "Quick shot - %d Mana - %d%s" % (qm_, rnd(qb_ * qf_ * m_), at_))

    ok1, bad1, samples = 0, [], {}
    for kind_ in ("wand", "staff"):
        for metal_ in METALS_A:
            iid_ = ("Weapon_Wand_" if kind_ == "wand" else "Weapon_Staff_") + metal_
            a_, z_ = BANDS_A[metal_]
            for lv_ in sorted(set([a_, (a_ + z_) // 2, z_] + ([6] if metal_ == "Wood" else []))):
                got_ = shot_lines(iid_, lv_)
                ex_ = expect(kind_, metal_, lv_)
                melee_ = [x_ for x_ in got_ if x_.startswith("Damage at Lv") or x_.startswith("Damage: ") or x_.startswith("Spell")]
                if ex_[0] in got_ and ex_[1] in got_ and got_.index(ex_[1]) == got_.index(ex_[0]) + 1 and not melee_:
                    ok1 += 1
                else:
                    bad1.append((iid_, lv_, ex_, got_[:4]))
                samples[(iid_, lv_)] = got_
    check(not bad1 and ok1 == 50, "AD1: every SkyyArmory wand + staff and the Wood wand at band start / middle / cap (+ Lv 6): 'Charged shot - N Mana - X damage "
          "at Lv L' then 'Quick shot - M Mana - Y damage at Lv L' = the projectile damage x SkyyArmory's tune x F(L) x material bonus, and NO melee / "
          "spell line (%d cases): %s" % (ok1, bad1[:3]))
    w6l_ = samples[("Weapon_Wand_Wood", 6)]
    check("Charged shot - 5 Mana - 43 damage at Lv 6" in w6l_ and "Quick shot - 1 Mana - 9 damage at Lv 6" in w6l_,
          "AD1: Skyy's sample - the Lv 6 Wood wand reads 'Charged shot - 5 Mana - 43 damage at Lv 6' / 'Quick shot - 1 Mana - 9 damage at Lv 6' "
          "(Skyy: about 43 / 9): %s" % w6l_[:4])
    for tw_ in ("Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
        gt_ = shot_lines(tw_, 6)
        bs_ = int(Lvl.band(tw_)[0])
        et_ = expect("wand", "Wood", 6, start_=bs_)
        check(et_[0] in gt_ and et_[1] in gt_ and not any(x_.startswith("Damage") for x_ in gt_),
              "AD1: %s (SkyyArmory answers it as the Wood wand - same Wand_Primary tap) shows the Wood wand's shots with ITS OWN material bonus "
              "(band start %d): %s" % (tw_, bs_, gt_[:3]))
    for lab_, key_ in (("Lv 6 Wood wand", ("Weapon_Wand_Wood", 6)), ("Lv 10 Copper wand", ("Weapon_Wand_Copper", 10)),
                       ("Lv 14 Copper wand", ("Weapon_Wand_Copper", 14)), ("Lv 40 Mithril wand", ("Weapon_Wand_Mithril", 40)),
                       ("Lv 1 Wood staff", ("Weapon_Staff_Wood", 1)), ("Lv 23 Iron staff", ("Weapon_Staff_Iron", 23)),
                       ("Lv 49 Onyxium staff", ("Weapon_Staff_Onyxium", 49))):
        print("AD1. tooltip %s: %s" % (lab_, " | ".join(x_ for x_ in samples[key_] if x_)))
    # SkyyArmory's live rows: tune % (its info answer, element 5), part.tune and quick.damage (its kit, through config:fn:SkyyArmory)
    tw0 = [float(x_) for x_ in ACfgA.TUNE_W]
    tw1 = list(tw0)
    tw1[2] = 150.0
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw1)
    gi_ = shot_lines("Weapon_Wand_Iron", 15)
    gw_ = shot_lines("Weapon_Wand_Wood", 6)
    check(expect("wand", "Iron", 15, tune_=150.0)[0] in gi_ and expect("wand", "Iron", 15, tune_=150.0)[1] in gi_ and expect("wand", "Wood", 6)[0] in gw_,
          "AD1: 'Damage by wand' Iron 150 %% -> both Iron shots x1.5; the Wood wand untouched: %s" % gi_[1:3])
    tw2 = list(tw0)
    tw2[0] = 200.0
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw2)
    gw2_ = shot_lines("Weapon_Wand_Wood", 6)
    check(expect("wand", "Wood", 6)[0] in gw2_ and "Quick shot - 1 Mana - %d damage at Lv 6" % rnd(5 * 2.0 * pyF(6)) in gw2_,
          "AD1: Wood 200 %% doubles only its QUICK shot - its charged shot is the shared vanilla orb SkyyArmory never tunes: %s" % gw2_[1:3])
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw0)
    r_qd = aset("quick.damage", "40")
    gq_ = shot_lines("Weapon_Staff_Cobalt", 30)
    check(r_qd == "ok" and expect("staff", "Cobalt", 30, qpct_=40.0)[1] in gq_ and expect("staff", "Cobalt", 30)[0] in gq_,
          "AD1: SkyyArmory's 'Quick shot damage' 40 (its kit, console set: %s) doubles the quick line only: %s" % (r_qd, gq_[1:3]))
    aset("quick.damage", "20")
    r_pt = aset("part.tune", "false")
    tw3 = list(tw0)
    tw3[3] = 300.0
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw3)
    gp_ = shot_lines("Weapon_Wand_Thorium", 20)
    check(r_pt == "ok" and expect("wand", "Thorium", 20, ton_=False)[0] in gp_ and expect("wand", "Thorium", 20, ton_=False)[1] in gp_,
          "AD1: SkyyArmory 'Damage tune' off -> the built-in numbers (Thorium 300 %% ignored, as ArmoryTuneSys does): %s (%s)" % (gp_[1:3], r_pt))
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw0)
    aset("part.tune", "true")
    # part.base / base.mode off: no level in the numbers, no "at Lv"
    Cfg.PART_BASE = False
    gb_ = shot_lines("Weapon_Wand_Copper", 14)
    Cfg.PART_BASE = True
    Cfg.BASE_MODE = "off"
    gm_ = shot_lines("Weapon_Wand_Copper", 14)
    Cfg.BASE_MODE = "shape"
    check(expect("wand", "Copper", 14, base_on=False)[0] in gb_ and expect("wand", "Copper", 14, base_on=False)[1] in gm_
          and gb_[1] == "Charged shot - 10 Mana - 56 damage",
          "AD1: part.base / base.mode off -> 'Charged shot - 10 Mana - 56 damage' (the built-in orb, no 'at Lv'): %s" % gb_[1:3])
    # the item's own modifiers: Damage % shows as its own modifier line (no melee line to put it on), Magical Power too
    tmod_ = [str(x_) for x_ in (lambda d_: (lambda t_, c_: (View.lines("Weapon_Wand_Wood", d_, U1, t_, c_), t_)[1])(ArrayList(), ArrayList()))(
        doc("Weapon_Wand_Wood", 6, [("dmg", 12), ("mp", 8)]))]
    check("Damage: +12%" in tmod_ and any(x_.startswith("Magical Power: +8") for x_ in tmod_) and "Charged shot - 5 Mana - 43 damage at Lv 6" in tmod_,
          "AD1: a Lv 6 wand with Damage +12 %% and Magical Power +8 keeps both modifier lines under the shots: %s" % tmod_[1:6])
    # a tap that is still a melee swing (an answer without a quick shot = SkyyArmory built with the vanilla tap) keeps the damage line
    @JImplements("java.util.function.Function")
    class NoQuick:
        @JOverride
        def apply(self, o_):
            a_ = list(o_)
            if len(a_) >= 2 and str(a_[1]) == "Weapon_Wand_Wood":
                return JArray(JObject)([Integer.valueOf(5), Integer.valueOf(0), JClass("java.lang.Double").valueOf(1.0), Integer.valueOf(25),
                                        Integer.valueOf(0), JClass("java.lang.Double").valueOf(100.0), "Skeleton_Mage_Corruption_Orb", ""])
            return None
    bridge.put("armory:fn:info", NoQuick())
    gn_ = shot_lines("Weapon_Wand_Wood", 6)
    check(gn_[1] == "Damage at Lv 6: 10-14" and gn_[2] == "Charged shot - 5 Mana - 43 damage at Lv 6" and not any(x_.startswith("Quick") for x_ in gn_),
          "AD1: a tap that is still the melee swing (no quick shot in the answer) -> its damage line, then the charged shot: %s" % gn_[1:4])
    # SkyyArmory absent: 0.2.1's lines exactly (no note)
    bridge.remove("armory:fn:info")
    ga_ = shot_lines("Weapon_Wand_Wood", 6)
    check(ga_[1:3] == ["Damage at Lv 6: 10-14", "Spell at Lv 6: 43"] and not any(x_.startswith("Charged") or x_.startswith("Quick") for x_ in ga_)
          and HW not in ga_, "AD1: SkyyArmory absent -> 0.2.1's lines exactly ('Damage at Lv 6: 10-14' + 'Spell at Lv 6: 43'), no note: %s" % ga_[1:4])
    bridge.put("armory:fn:info", AInfo())
    # other spell weapons SkyyArmory does not own keep 0.2.1's lines (Frost staff, a spellbook)
    gf_ = shot_lines("Weapon_Staff_Frost", 30)
    gs_ = shot_lines("Weapon_Spellbook_Fire", 30)
    check(any(x_.startswith("Spell at Lv 30: ") for x_ in gf_) and not any(x_.startswith("Charged") for x_ in gf_ + gs_),
          "AD1: a staff / spellbook SkyyArmory does not own (Frost staff, Fire spellbook) keeps 0.2.1's lines: %s / %s" % (gf_[1:3], gs_[1:3]))
    # gear:fn:describe (the AH) + the Reforge page columns carry the shots; the item tooltip itself = the same lines
    dsc_ = [str(x_) for x_ in J("GearFn")(JInt(0)).apply(gstack("Weapon_Wand_Copper", 14))]
    stx_, scl_ = ArrayList(), ArrayList()
    View.statLines("Weapon_Staff_Mithril", doc("Weapon_Staff_Mithril", 45), stx_, scl_)
    check(expect("wand", "Copper", 14)[0] in dsc_ and expect("wand", "Copper", 14)[1] in dsc_
          and [str(x_) for x_ in stx_][:2] == list(expect("staff", "Mithril", 45)),
          "AD1: gear:fn:describe (AH) and the Reforge page columns (statLines) show the shots too: %s / %s" % (dsc_[1:3], [str(x_) for x_ in stx_][:2]))
    # the render signature follows SkyyArmory's config epoch (cfgEpoch adds it): a tune change re-renders the stack, nothing else does
    dv22 = doc("Weapon_Wand_Iron", 15)
    sva_ = View.apply(IS("Weapon_Wand_Iron", 1), dv22, U1)
    svb_ = View.apply(sva_, dv22, U1)
    ep0_ = int(Cfg.cfgEpoch())
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw1)
    aset("check.share", "45")
    ep1_ = int(Cfg.cfgEpoch())
    svc_ = View.apply(sva_, dv22, U1)
    ACfgA.TUNE_W = jpype.JArray(jpype.JDouble)(tw0)
    aset("check.share", "40")
    check(SysJ.identityHashCode(sva_) == SysJ.identityHashCode(svb_) and ep1_ > ep0_ and SysJ.identityHashCode(svc_) != SysJ.identityHashCode(sva_),
          "AD1: the item re-renders when SkyyArmory's settings change (config:epoch:SkyyArmory is in cfgEpoch: %d -> %d) and stays put otherwise" % (ep0_, ep1_))
    print("AD1. shot lines done")

    # ---- AD2. no note anywhere: the item tooltip text written into the stack (View.apply -> ItemDisplayMetadata), every weapon / armor kind
    IDMc = JClass(ENG + "asset.type.item.config.metadata.ItemDisplayMetadata")
    notes_ = []
    for iid_, lv_ in (("Weapon_Wand_Wood", 6), ("Weapon_Wand_Wood", 2), ("Weapon_Wand_Wood", 1), ("Weapon_Sword_Copper", 18), ("Weapon_Staff_Frost", 30),
                      ("Armor_Copper_Chest", 4), ("Armor_Copper_Head", 2), ("Armor_Copper_Chest", 1), ("Weapon_Crossbow_Iron", 15)):
        s_ = View.apply(IS(iid_, 1), doc(iid_, lv_), U1)
        md_ = s_.getFromMetadataOrNull(IDMc.KEYED_CODEC)
        t_ = str(s_.getMetadata().toJson())
        if "before levels" in t_ or "below is vanilla" in t_ or "below are vanilla" in t_ or md_ is None:
            notes_.append((iid_, lv_))
    bridge.remove("armory:fn:info")
    s_ = View.apply(IS("Weapon_Wand_Wood", 1), doc("Weapon_Wand_Wood", 6), U1)
    if "before levels" in str(s_.getMetadata().toJson()):
        notes_.append(("Weapon_Wand_Wood (no SkyyArmory)", 6))
    bridge.put("armory:fn:info", AInfo())
    check(not notes_, "AD2: no grey note in any written tooltip (wands with / without SkyyArmory, Lv 1 / 2 / 6, sword, Frost staff, crossbow, copper "
          "armor Lv 1 / 2 / 4): %s" % notes_)
    print("AD2. no note done")

    # ---- AD3. THE VANILLA DAMAGE DATA BOX, HIDDEN PER ITEM TYPE (GearBox) on the AC0 model: real Item objects whose ItemWeapon carries the
    # breakdowns the ENGINE's WeaponDamageDataCollector computed (the data ItemModule.computeWeaponData writes in game)
    PDD = JClass("com.hypixel.hytale.protocol.DamageData")
    DBDc = JClass(ENG + "asset.type.item.config.damageData.DamageBreakdown")

    def pk_entries(it_):
        # what the client gets: protocol ItemWeapon (ItemWeapon.toPacket - the call Item.toPacket makes for the join packet)
        pw_ = it_.getWeapon().toPacket()
        b_, u_ = pw_.basicDamageBreakdown, pw_.ultimateDamageBreakdown
        return (None if b_ is None else len(b_.entries)), (None if u_ is None else len(u_.entries))
    gear_w = sorted(i_ for i_ in zitems2 if int(Data.slotOf(i_)) in (0, 1) and bool(Data.isGear(i_)))
    nong_w = sorted(i_ for i_ in zitems2 if i_ not in gear_w)
    full_ = [i_ for i_ in gear_w if BRK.get(i_)]
    before_ = dict((i_, (float(Base.maxEntry(i_)), None if View.damageText(i_) is None else str(View.damageText(i_)),
                         [float(x_) for x_ in (Base.range(i_, doc(i_, 20)) or [])], float(Base.ratio(i_)))) for i_ in gear_w)
    pk0_ = dict((i_, pk_entries(zitems2[i_])) for i_ in full_)
    # the packet cache is dropped: a stale cached ItemBase may not survive the hide
    cpf_ = acf(ItemZ.class_.getName(), "cachedPacket")
    for i_ in gear_w:
        cpf_.set(zitems2[i_], JClass("java.lang.ref.SoftReference")(JObject(i_)))
    ABox.SNAP.clear()
    ABox.ON = True
    nh_ = int(ABox.applyAll(True))
    pk1_ = dict((i_, pk_entries(zitems2[i_])) for i_ in full_)
    check(nh_ == len(full_) and int(ABox.SNAP.size()) == len(full_) and all(pk0_[i_][0] and pk1_[i_] == (0, 0) for i_ in full_),
          "AD3: GearBox.applyAll hides the box on every gear weapon with damage data (%d of %d gear weapons: the EMPTY breakdowns vanilla sends for a "
          "weapon without damage entries, as protocol ItemWeapon.toPacket shows - basic %s -> 0 entries)" % (nh_, len(gear_w), pk0_.get("Weapon_Sword_Crude")))
    check(all(cpf_.get(zitems2[i_]) is None for i_ in full_), "AD3: the hidden items' packet cache is dropped (the next join sends the EMPTY breakdowns)")
    after_ = dict((i_, (float(Base.maxEntry(i_)), None if View.damageText(i_) is None else str(View.damageText(i_)),
                        [float(x_) for x_ in (Base.range(i_, doc(i_, 20)) or [])], float(Base.ratio(i_)))) for i_ in gear_w)
    Base.clear()
    after2_ = dict((i_, (float(Base.maxEntry(i_)), float(Base.ratio(i_)))) for i_ in gear_w)
    check(after_ == before_ and all(after2_[i_] == (before_[i_][0], before_[i_][3]) for i_ in gear_w),
          "AD3: SkyyGear's own maths read the snapshot - K, the largest entry, the levelled range and the plain 'Damage: x-y' are identical for "
          "all %d gear weapons (also after GearBase.clear re-reads them)" % len(gear_w))
    m18h_ = float(Base.mult("Weapon_Sword_Copper", doc("Weapon_Sword_Copper", 18), False))
    tsw_h = shot_lines("Weapon_Sword_Copper", 18)
    tk1_h = shot_lines("Weapon_Sword_Crude", 1)
    check(("Damage at Lv 18: %d-%d" % (rnd(min(e_[1] for e_ in BRK["Weapon_Sword_Copper"]) * m18h_), rnd(bmax("Weapon_Sword_Copper") * m18h_))) in tsw_h
          and ("Damage: " + str(before_["Weapon_Sword_Crude"][1])) in tk1_h,
          "AD3: with the box hidden the tooltip lines are unchanged - the Lv 18 Copper sword's levelled range, the Lv 1 Crude sword's plain line "
          "(the snapshot's numbers): %s / %s" % (tsw_h[1:2], tk1_h[1:2]))
    untouched_ = [i_ for i_ in nong_w if zitems2[i_].getWeapon() is not None and BRK.get(i_) and pk_entries(zitems2[i_])[0] == 0]
    empties_ = [i_ for i_ in gear_w if not BRK.get(i_) and ABox.SNAP.containsKey(i_)]
    check(not untouched_ and not empties_ and len(nong_w) > 0,
          "AD3: weapons that are not gear (%d: shields, bombs, darts ...) keep their box; a gear weapon without damage entries (spellbooks) gets no "
          "snapshot: %s / %s" % (len(nong_w), untouched_[:3], empties_[:3]))
    # a second applyAll / a listener call on the hidden items never replaces a snapshot with the EMPTY breakdowns
    snap_sw = ABox.SNAP.get("Weapon_Sword_Crude")[0]
    n2_ = int(ABox.applyAll(True))
    check(n2_ == 0 and SysJ.identityHashCode(ABox.SNAP.get("Weapon_Sword_Crude")[0]) == SysJ.identityHashCode(snap_sw) and len(list(snap_sw.entries())) > 0, "AD3: hiding twice changes nothing (the snapshot stays the engine's)")
    # an asset reload: ItemModule writes FRESH breakdowns onto the reloaded items, then our LAST-priority listener runs with the real event
    LAEc = JClass("com.hypixel.hytale.assetstore.event.LoadedAssetsEvent")
    WDCc = JClass(ENG + "asset.type.item.config.damageData.WeaponDamageDataCollector")
    rel_ = zitems2["Weapon_Sword_Iron"]
    fresh_ = WDCc.calculate(rel_, ITY.Primary)
    nwz_ = rel_.unshareWeapon()
    nwz_.setBasicDamageBreakdown(fresh_)
    nwz_.setUltimateDamageBreakdown(DBDc.EMPTY)
    lm_ = HashMap()
    lm_.put("Weapon_Sword_Iron", rel_)
    lm_.put("Weapon_Kunai", zitems2["Weapon_Kunai"])
    ev_ = LAEc(ItemZ.class_, store.getAssetMap(), lm_, JBoolean(False), None)
    ABox.STARTED = True
    J("GearBoxL")().accept(ev_)
    check(pk_entries(rel_) == (0, 0) and SysJ.identityHashCode(ABox.SNAP.get("Weapon_Sword_Iron")[0]) == SysJ.identityHashCode(fresh_)
          and not ABox.SNAP.containsKey("Weapon_Kunai") and not BRK.get("Weapon_Kunai"),
          "AD3: a real LoadedAssetsEvent(Item) after an asset reload: the listener snapshots the FRESH engine breakdown and hides it again; "
          "the Kunai (no damage entries) in the same event is left alone (packet %s, snapshot %s = %s, fresh %s, entries %d, equal %s)" % (pk_entries(rel_),
              ABox.SNAP.containsKey("Weapon_Sword_Iron"), SysJ.identityHashCode(ABox.SNAP.get("Weapon_Sword_Iron")[0]), SysJ.identityHashCode(fresh_),
              len(list(fresh_.entries())), bool(fresh_.equals(ABox.SNAP.get("Weapon_Sword_Iron")[0]))))
    ABox.ON = False
    rel2_ = zitems2["Weapon_Sword_Thorium"]
    f2_ = WDCc.calculate(rel2_, ITY.Primary)
    w2z_ = rel2_.unshareWeapon()
    w2z_.setBasicDamageBreakdown(f2_)
    lm2_ = HashMap()
    lm2_.put("Weapon_Sword_Thorium", rel2_)
    J("GearBoxL")().accept(LAEc(ItemZ.class_, store.getAssetMap(), lm2_, JBoolean(False), None))
    check(pk_entries(rel2_)[0] > 0, "AD3: view.hideDamageBox off at start (GearBox.ON false) -> the listener hides nothing")
    ABox.ON = True
    # restore (the switch off at the next start = nothing hidden; restore puts the engine's objects back exactly)
    nr_ = int(ABox.applyAll(False))
    # (Weapon_Sword_Thorium got a NEWER engine computation while the box was hidden and the listener was off: restore never writes over it -
    # its old snapshot is dropped, the item keeps the newer breakdown)
    check(nr_ == len(full_) - 1 and int(ABox.SNAP.size()) == 0 and SysJ.identityHashCode(rel2_.getWeapon().getBasicDamageBreakdown()) == SysJ.identityHashCode(f2_)
          and all(pk_entries(zitems2[i_])[0] == pk0_[i_][0] for i_ in full_ if i_ not in ("Weapon_Sword_Iron", "Weapon_Sword_Thorium"))
          and SysJ.identityHashCode(zitems2["Weapon_Sword_Crude"].getWeapon().getBasicDamageBreakdown()) == SysJ.identityHashCode(snap_sw),
          "AD3: GearBox.restore puts every engine breakdown back (the same objects; the box returns) - never over a newer engine computation "
          "(the Thorium sword re-computed meanwhile keeps its new one): %d of %d" % (nr_, len(full_)))
    # the row + the setup wiring
    rwb = dict((str(k_), (str(t_), str(d_), str(f_), str(h_))) for k_, t_, d_, f_, h_ in zip(Rows.KEYS, Rows.TYPES, Rows.DEFS, Rows.FLAGS, Rows.HELPS))
    check(rwb.get("view.hideDamageBox", ("",))[:3] == ("bool", "true", "restart") and len(rwb["view.hideDamageBox"][3]) <= 100,
          "AD3: Server Setup row 'Hide the vanilla Damage Data box' (bool, default on, restart - clients load item definitions at join): %s" % (rwb.get("view.hideDamageBox"),))
    su22 = mcode("SkyyGearPlugin", "setup")
    st22 = mcode("SkyyGearPlugin", "start")
    check("GearBox.ON" in su22 and "EventPriority.LAST" in su22 and "LoadedAssetsEvent" in su22 and "GearBoxL.<init>" in su22
          and su22.find("GearCfg.load(") < su22.find("GearBox.ON") and "GearBox.start(" in st22 and "GearCrit.startCheck(" in st22,
          "AD3: setup() reads view.hideDamageBox once after the config load and registers GearBoxL for LoadedAssetsEvent(Item) at LAST priority; "
          "start() hides every gear weapon + checks the crit style asset")
    # the ENGINE side (bytecode, HytaleServer.jar): nothing but ItemWeapon.toPacket reads the server breakdowns; ItemModule.computeWeaponData
    # is their only writer; the ItemWeapon codec has no field for them (so no item-asset field can hide the box)
    rdr_, wrt_ = [], []
    with zipfile.ZipFile(B.SERVER_JAR) as zs_:
        for n_ in zs_.namelist():
            if not n_.endswith(".class") or not n_.startswith("com/hypixel/"):
                continue
            by_ = zs_.read(n_)
            if b"BasicDamageBreakdown" in by_ or b"UltimateDamageBreakdown" in by_:
                cn_ = n_[:-6].replace("/", ".")
                if cn_ in ("com.hypixel.hytale.protocol.ItemWeapon",):
                    continue
                for mm_ in pool.get(cn_).getDeclaredMethods():
                    bo_ = BOS()
                    IP(PS(bo_)).print_(mm_)
                    tx_ = str(bo_.toString())
                    if "config.ItemWeapon.getBasicDamageBreakdown" in tx_ or "config.ItemWeapon.getUltimateDamageBreakdown" in tx_:
                        rdr_.append("%s.%s" % (cn_.rsplit(".", 1)[-1], mm_.getName()))
                    if "config.ItemWeapon.setBasicDamageBreakdown" in tx_ or "config.ItemWeapon.setUltimateDamageBreakdown" in tx_:
                        wrt_.append("%s.%s" % (cn_.rsplit(".", 1)[-1], mm_.getName()))
    ciw_ = pool.get(ENG + "asset.type.item.config.ItemWeapon").getClassInitializer()
    bo_ = BOS()
    IP(PS(bo_)).print_(ciw_.toMethod("clinitx", pool.get(ENG + "asset.type.item.config.ItemWeapon")))
    ckeys_ = re.findall(r'ldc[_w]* #\d+ = "([A-Za-z]+)"', str(bo_.toString()))
    check(not rdr_ and sorted(set(wrt_)) == ["ItemModule.computeWeaponData"] and ckeys_ == ["StatModifiers", "EntityStatsToClear", "RenderDualWielded"],
          "AD3: the engine - no class reads the server breakdowns (only ItemWeapon.toPacket, its own field); ItemModule.computeWeaponData is the only "
          "writer (%s); the ItemWeapon JSON keys are %s - no item-asset field controls the box" % (sorted(set(wrt_)), ckeys_))
    # the SET jars: no other jar reads the breakdowns or ships an EntityUI asset; the weapon item files other jars override are untouched
    # (GearBox overrides no file, it acts on whichever definition won)
    setj_ = []
    src_set = open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8").read()
    SETL = re.findall(r'\(\s*"(Skyy\w+)"\s*,\s*"([0-9.]+)"\s*\)', src_set.split("SET = [", 1)[1].split("\n]", 1)[0])
    readers_, uis_, overr_ = [], [], {}
    for m_, v_ in SETL:
        jp_ = os.path.join(ROOT, m_, "%s-%s.jar" % (m_, v_))
        if m_ == "SkyyGear" or not os.path.isfile(jp_):
            continue
        with zipfile.ZipFile(jp_) as zq_:
            for n_ in zq_.namelist():
                if n_.endswith(".class") and (b"DamageBreakdown" in zq_.read(n_) or b"CombatTextUpdate" in zq_.read(n_) or b"UIComponentList" in zq_.read(n_)):
                    readers_.append("%s:%s" % (m_, n_))
                if n_.startswith("Server/Entity/UI/"):
                    uis_.append("%s:%s" % (m_, n_))
                if n_.startswith("Server/Item/Items/") and os.path.basename(n_).startswith("Weapon_"):
                    overr_[m_] = overr_.get(m_, 0) + 1
    check(not readers_ and not uis_ and overr_.get("SkyySkills", 0) > 0 and overr_.get("SkyyArmory", 0) == 15,
          "AD3: the other %d SET jars - none reads the breakdowns / sends combat text / touches UIComponentList, none ships an EntityUI asset; "
          "their weapon item files (%s) stay theirs (GearBox writes no file): %s %s" % (len(SETL) - 1, overr_, readers_[:3], uis_[:3]))
    print("AD3. vanilla Damage Data box hidden per item type done (%d gear weapons hidden, snapshot kept)" % nh_)

    # ---- AD4. THE CRIT EFFECTS
    # (a) critLevel = the crit hitAmount rolled (same chance, same two numbers) - 4000 random cases
    import random as _rnd
    rg_ = _rnd.Random(22)
    mism_ = []
    nst_ = [0, 0, 0]
    T0 = JArray(JInt)(int(Defs.NS))
    for k_ in range(4000):
        cc_ = rg_.choice([0, 0, 5, 30, 60, 99, 100, 120, 150, 199, 250])
        cb_ = rg_.choice([0.0, 0.0, 10.0, 100.0])
        cdm_ = rg_.choice([0, 50])
        Cfg.CRIT_BASE = cb_
        tt_ = JArray(JInt)(int(Defs.NS))
        tt_[int(Hit.I_CC)] = cc_
        tt_[int(Hit.I_CD)] = cdm_
        r1_, r2_ = rg_.random(), rg_.random()
        a_ = float(Hit.hitAmount(100.0, tt_, False, False, r1_, r2_))
        lv_ = int(Hit.critLevel(tt_, r1_, r2_))
        fc_ = 2.0 * (1.0 + cdm_ / 100.0)
        want_ = 100.0 if lv_ == 0 else (100.0 * fc_ if lv_ == 1 else 100.0 * fc_ * 2.0)
        nst_[lv_] += 1
        if abs(a_ - want_) > 1e-6:
            mism_.append((cc_, cb_, r1_, r2_, a_, lv_))
    Cfg.CRIT_BASE = 0.0
    check(not mism_ and all(nst_), "AD4(a): GearHit.critLevel tells exactly the crit hitAmount rolled - 4000 random hits (none %d / crit %d / overcrit %d), "
          "0 mismatches: %s" % (nst_[0], nst_[1], nst_[2], mism_[:2]))
    # (b) the style asset DECODED by the engine's own EntityUIComponent codec (+ validators, no unknown key), next to vanilla's two
    EUIc = JClass("com.hypixel.hytale.server.core.modules.entityui.asset.EntityUIComponent")
    CTUIc = JClass("com.hypixel.hytale.server.core.modules.entityui.asset.CombatTextUIComponent")
    UCLc = JClass("com.hypixel.hytale.server.core.modules.entityui.UIComponentList")
    EVWc = JClass(ENG + "modules.entity.tracker.EntityTrackerSystems$EntityViewer")
    CTUc, UCUc = JClass("com.hypixel.hytale.protocol.CombatTextUpdate"), JClass("com.hypixel.hytale.protocol.UIComponentsUpdate")

    def dec_ui(txt_, key_):
        ei_ = AEI(Paths.get(key_ + ".json"), ADT(EUIc.class_, key_, None))
        try:
            o_ = EUIc.CODEC.decodeJson(RJR.fromJsonString(txt_), ei_)
            EUIc.CODEC.validate(o_, ei_)            # the validators the store runs on every loaded asset (Scale 0..1, Duration ...)
        except Exception as e_:
            return None, str(e_)[:200]
        vr_ = ei_.getValidationResults()
        bad_ = []
        if vr_.hasFailed():
            bad_.append("validation failed: %s" % ([str(x_) for x_ in vr_.getResults()] if vr_.getResults() is not None else "?"))
        if len(list(ei_.getUnknownKeys())) > 0:
            bad_.append("unknown keys %s" % [str(x_) for x_ in ei_.getUnknownKeys()])
        return o_, "; ".join(bad_)
    # the codec registrations EntityUIModule.setup makes in game (CodecMapRegistry$Assets.register on the shared static codec maps) - a bare
    # JVM has none: the same ids, classes and codecs registered here, then every file decodes through EntityUIComponent.CODEC like the store
    EAI = "com.hypixel.hytale.server.core.modules.entityui.asset."
    for map_, id_, cn_ in ((EUIc.CODEC, "EntityStat", EAI + "EntityStatUIComponent"), (EUIc.CODEC, "CombatText", EAI + "CombatTextUIComponent"),
                           (JClass(EAI + "CombatTextUIComponentAnimationEvent").CODEC, "Scale", EAI + "CombatTextUIComponentScaleAnimationEvent"),
                           (JClass(EAI + "CombatTextUIComponentAnimationEvent").CODEC, "Position", EAI + "CombatTextUIComponentPositionAnimationEvent"),
                           (JClass(EAI + "CombatTextUIComponentAnimationEvent").CODEC, "Opacity", EAI + "CombatTextUIComponentOpacityAnimationEvent")):
        try:
            map_.register(JString(id_), JClass(cn_).class_, JClass(cn_).CODEC)
        except Exception as e_:
            print("AD4(b). note: codec register %s failed: %s" % (id_, str(e_)[:120]))
    crit_txt = zipfile.ZipFile(jar).read("Server/Entity/UI/SkyyGear_CritText.json").decode("utf-8")
    van_ct, why_v = dec_ui(azz.read("Server/Entity/UI/CombatText.json").decode("utf-8-sig"), "CombatText")
    van_hb, why_h = dec_ui(azz.read("Server/Entity/UI/Healthbar.json").decode("utf-8-sig"), "Healthbar")
    crit_o, why_c = dec_ui(crit_txt, "SkyyGear_CritText")
    check(crit_o is not None and not why_c and isinstance(crit_o, CTUIc) and van_ct is not None and not why_v and van_hb is not None
          and abs(float(acf(CTUIc.class_.getName(), "fontSize").getFloat(crit_o)) - 62.0) < 1e-6
          and abs(float(acf(CTUIc.class_.getName(), "duration").getFloat(crit_o)) - 0.5) < 1e-6,
          "AD4(b): the jar's SkyyGear_CritText.json decodes through the engine's EntityUIComponent codec as a CombatTextUIComponent (62 px, 0.5 s), "
          "no unknown key (%s); vanilla CombatText + Healthbar decode the same way" % (why_c or "clean"))
    # the engine's OWN validator objects (BuilderCodec.entries -> BuilderField.validators -> RangeValidator min / max): every value of our
    # style lies inside them (a validate() in a bare JVM only logs a failure, so the bounds are read and compared here; a Scale of 1.6 would not)
    BCc, BFc = "com.hypixel.hytale.codec.builder.BuilderCodec", "com.hypixel.hytale.codec.builder.BuilderField"

    def vbounds(codec_, key_):
        out_ = []
        lst_ = None
        c_ = codec_
        while c_ is not None and lst_ is None:          # the key may sit on a parent codec (StartAt / EndAt: the animation event base)
            ents_ = acf(BCc, "entries").get(c_)
            lst_ = ents_.get(key_) if ents_ is not None else None
            c_ = acf(BCc, "parentCodec").get(c_)
        for f_ in (lst_ or []):
            vs_ = acf(BFc, "validators").get(f_)
            for v_ in (vs_ or []):
                if str(v_.getClass().getSimpleName()) == "RangeValidator":
                    mn_ = acf(v_.getClass().getName(), "min").get(v_)
                    mx_ = acf(v_.getClass().getName(), "max").get(v_)
                    out_.append((None if mn_ is None else float(str(mn_)), None if mx_ is None else float(str(mx_))))
        return out_

    def inside(val_, bs_):
        return all((lo_ is None or val_ >= lo_ - 1e-9) and (hi_ is None or val_ <= hi_ + 1e-9) for lo_, hi_ in bs_)
    CSTY = json.loads(crit_txt)
    AEVB = JClass(EAI + "CombatTextUIComponentAnimationEvent")
    vb_ = {"Duration": vbounds(CTUIc.CODEC, "Duration"), "ViewportMargin": vbounds(CTUIc.CODEC, "ViewportMargin"),
           "HitAngleModifierStrength": vbounds(CTUIc.CODEC, "HitAngleModifierStrength"),
           "StartScale": vbounds(JClass(EAI + "CombatTextUIComponentScaleAnimationEvent").CODEC, "StartScale"),
           "EndScale": vbounds(JClass(EAI + "CombatTextUIComponentScaleAnimationEvent").CODEC, "EndScale"),
           "StartAt": vbounds(JClass(EAI + "CombatTextUIComponentScaleAnimationEvent").CODEC, "StartAt"),
           "EndAt": vbounds(JClass(EAI + "CombatTextUIComponentScaleAnimationEvent").CODEC, "EndAt")}
    vals_ok = (inside(CSTY["Duration"], vb_["Duration"]) and inside(CSTY["ViewportMargin"], vb_["ViewportMargin"])
               and inside(CSTY["HitAngleModifierStrength"], vb_["HitAngleModifierStrength"])
               and all(inside(e_[k_], vb_[k_]) for e_ in CSTY["AnimationEvents"] for k_ in ("StartScale", "EndScale", "StartAt", "EndAt") if k_ in e_))
    check([(round(a_, 6), round(z_, 6)) for a_, z_ in vb_["Duration"]] == [(0.1, 10.0)] and vb_["EndScale"] and vb_["StartAt"] and vals_ok and not inside(1.6, vb_["EndScale"]) and not inside(1.2, vb_["StartAt"]),
          "AD4(b): every value of the crit style lies inside the engine's own range validators %s (and a Scale of 1.6 or a StartAt of 1.2 would not)" % vb_)
    pk_c = crit_o.toPacket()
    check(pk_c is not None and int(pk_c.combatTextColor.red) & 0xFF == 0xFF and abs(float(pk_c.combatTextFontSize) - 62.0) < 1e-6,
          "AD4(b): the packet the client gets at join (protocol EntityUIComponent): red text colour, font size 62")
    # the EntityUI asset model: vanilla CombatText 0, Healthbar 1, our style 2 (an engine IndexedLookupTableAssetMap)
    old_eui = acf(EUIc.class_.getName(), "ASSET_STORE").get(None)
    eui_map = indexed({"CombatText": van_ct, "Healthbar": van_hb, "SkyyGear_CritText": crit_o})
    fz(ILT, "nextIndex").set(eui_map, JClass("java.util.concurrent.atomic.AtomicInteger")(3))
    acf(EUIc.class_.getName(), "ASSET_STORE").set(None, zstore(eui_map))
    fill_single(ENG + "modules.entityui.EntityUIModule")
    check(int(ACrit.styleIndex("SkyyGear_CritText")) == 2 and int(ACrit.styleIndex("CombatText")) == 0 and bool(ACrit.isText(2)) and not bool(ACrit.isText(1))
          and int(ACrit.styleIndex("NoSuchStyle")) == -2147483648, "AD4(b): GearCrit resolves the LOADED style indices (ours 2, vanilla 0; health bar no text style; unknown = MIN_VALUE)")

    def mk_ucl(ids_=None):
        l_ = UCLc()
        acf(UCLc.class_.getName(), "componentIds").set(l_, JArray(JInt)(0) if ids_ is None else JArray(JInt)(ids_))
        if ids_ is None:
            l_.update()
        return l_
    # (c) the strip: UIComponentList.update() gives every entity EVERY loaded style (0, 1, 2 = two numbers per hit!) -> GearCrit strips ours
    l0_ = mk_ucl()
    full_ids = [int(x_) for x_ in l0_.getComponentIds()]
    ch_ = bool(ACrit.strip(l0_))
    check(full_ids == [0, 1, 2] and ch_ and [int(x_) for x_ in l0_.getComponentIds()] == [0, 1] and not bool(ACrit.strip(l0_)),
          "AD4(c): the engine's UIComponentList.update() hands an entity all three styles %s; GearCrit.strip leaves [0, 1] (vanilla number + health "
          "bar) by reflection on the protected componentIds; a stripped list stays" % full_ids)
    # GearCritClean.onEntityAdd on a holder (a Holder whose getComponent answers the list) - the real HolderSystem method
    HoldC = mkfake("SkyyAdHolder", "com.hypixel.hytale.component.Holder", [
        "F public static Object L = null;",
        "public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.ComponentType t) { return (com.hypixel.hytale.component.Component) L; }"])
    hold_ = UZ.allocateInstance(HoldC)
    JClass(HoldC.getName()).L = mk_ucl()
    ACClean.SETUP = JClass("com.hypixel.hytale.server.core.modules.entityui.UIComponentSystems$Setup").class_
    cl_ = ACClean(True)
    cl_.onEntityAdd(hold_, JClass("com.hypixel.hytale.component.AddReason").SPAWN, None)
    check([int(x_) for x_ in JClass(HoldC.getName()).L.getComponentIds()] == [0, 1] and bool(cl_.ordered)
          and "UIComponentSystems$Setup" in str(list(cl_.getDependencies())[0]) and str(list(cl_.getDependencies())[0]).find("AFTER") >= 0,
          "AD4(c): the REAL GearCritClean.onEntityAdd strips a new entity's list; it is ordered AFTER UIComponentSystems$Setup (%s)" % list(cl_.getDependencies()))
    JClass(HoldC.getName()).L = None
    cl_.onEntityAdd(hold_, JClass("com.hypixel.hytale.component.AddReason").SPAWN, None)
    check(True, "AD4(c): a holder without a list is ignored (no error)")
    # (d) GearCritSys on the AC3 ECS shim: the attacker (player U1) hits the mob with a crit through the REAL GearHitSys.handle
    CT["evw"] = EVWc.getComponentType()
    CT["ucl"] = UCLc.getComponentType()
    CT["tc"] = JClass(ENG + "modules.entity.component.TransformComponent").getComponentType()
    check(len(set(SysJ.identityHashCode(v_) for v_ in CT.values())) == len(CT), "AD4(d): the shim's EntityViewer / UIComponentList / Transform types are distinct objects")
    TCc = JClass(ENG + "modules.entity.component.TransformComponent")
    V3 = JClass("org.joml.Vector3d")

    def mk_tc(x_, y_, z_):
        t_ = acalloc(TCc.class_.getName())
        acf(TCc.class_.getName(), "position").set(t_, V3(float(x_), float(y_), float(z_)))
        return t_
    # a capturing packet handler for the players (ParticleUtil writes SpawnParticleSystem into PlayerRef.getPacketHandler())
    PHC = mkfake("SkyyAdPH", "com.hypixel.hytale.server.core.io.PacketHandler", [
        "F public static java.util.ArrayList SENT = new java.util.ArrayList();",
        "F public String who;",
        "public String getIdentifier() { return who; }",
        "public void accept(com.hypixel.hytale.protocol.ToServerPacket p) { }",
        "public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { SENT.add(new Object[] { who, p }); }"])
    PHJ = JClass(PHC.getName())

    def mk_ph(who_):
        h_ = UZ.allocateInstance(PHC)
        acf(PHC.getName(), "who").set(h_, who_)
        return h_
    acf(PRc.class_.getName(), "packetHandler").set(pr1_, mk_ph("attacker"))
    acf(PRc.class_.getName(), "packetHandler").set(pr2_, mk_ph("bystander"))
    acf(PRc.class_.getName(), "entity").set(pr1_, ref_p)        # PlayerRef.isValid (vanilla EntityUIEvents asks it)
    viewer_ = EVWc(JInt(64), None)
    putc(ref_p, "evw", viewer_)
    mob_list = mk_ucl([0, 1])
    putc(ref_mob, "ucl", mob_list)
    putc(ref_mob, "tc", mk_tc(10, 64, 20))
    viewer_.visible.add(ref_mob)
    ACSys.EUI = JClass(ENG + "modules.entity.damage.DamageSystems$EntityUIEvents").class_     # what GearCrit.setup sets before registering
    csys_ = ACSys(True)
    check(bool(csys_.ordered) and "EntityUIEvents" in str(list(csys_.getDependencies())[0]) and "BEFORE" in str(list(csys_.getDependencies())[0])
          and "getInspectDamageGroup" in mcode("GearCritSys", "getGroup"),
          "AD4(d): GearCritSys is an Inspect system ordered BEFORE DamageSystems$EntityUIEvents (%s)" % list(csys_.getDependencies()))
    eui_ = JClass(ENG + "modules.entity.damage.DamageSystems$EntityUIEvents")()
    ACrit.TICK_OK = True

    def crit_hit(stack_=None, amount_=6.0, angle_=30.0, loc_=None, vanilla_=True):
        """one melee hit of U1 on the mob through the REAL GearHitSys, then GearCritSys, then vanilla's EntityUIEvents; returns the updates
        queued for the mob in U1's viewer (in order) + the Damage"""
        viewer_.updates.clear()
        PHJ.SENT.clear()
        hot_.setItemStackForSlot(sh(0), gstack("Weapon_Sword_Crude", 6) if stack_ is None else stack_)
        d_ = DMGc(DENTc(ref_p), JInt(CIDX["Physical"]), JFloat(float(amount_)))
        if angle_ is not None:
            d_.putMetaObject(DMGc.HIT_ANGLE, JClass("java.lang.Float").valueOf(float(angle_)))
        if loc_ is not None:
            d_.putMetaObject(DMGc.HIT_LOCATION, JClass("org.joml.Vector4d")(float(loc_[0]), float(loc_[1]), float(loc_[2]), 1.0))
        AcChunk.REF = ref_mob
        AcChunk.COMP.clear()
        hs_.handle(JInt(0), chk_, None, buf_, d_)
        csys_.handle(JInt(0), chk_, None, buf_, d_)
        if vanilla_:
            eui_.handle(JInt(0), chk_, None, buf_, d_)
        eu_ = viewer_.updates.get(ref_mob)
        ups_ = [] if eu_ is None else list(eu_.toUpdatesArray())
        return ups_, d_

    def utxt(u_):
        if isinstance(u_, CTUc):
            return "number %s @%g" % (str(u_.text), float(u_.hitAngleDeg))
        if isinstance(u_, UCUc):
            return "style %s" % [int(x_) for x_ in u_.components]
        return str(u_)
    # crit.base 100 = every hit crits (the in-game test switch); the defaults: popup on, sparks self, red number OFF
    Cfg.CRIT_BASE = 100.0
    Cfg.CRIT_FX, Cfg.CRIT_SPARKS, Cfg.CRIT_STYLE = True, "self", False
    for k_ in [str(x) for x in Gear.ONCE.keySet()]:
        if "Crit" in k_ or "crit" in k_:
            Gear.ONCE.remove(k_)
    ups_, d1_ = crit_hit(loc_=(10.5, 65.0, 20.5))
    lines1 = [utxt(u_) for u_ in ups_]
    sp1 = [(str(w_), str(p_.particleSystemId), round(float(p_.position.x), 2), round(float(p_.position.y), 2), round(float(p_.position.z), 2)) for w_, p_ in PHJ.SENT]
    num_ = rnd(float(d1_.getAmount()))
    check(lines1 == ["number CRIT! @10", "number %d @30" % int(_m.floor(float(d1_.getAmount())))] and sp1 == [("attacker", "Impact_Critical", 10.5, 65.0, 20.5)]
          and not [str(x) for x in Gear.ONCE.keySet() if "Crit" in str(x)],
          "AD4(d): DEFAULTS - a real crit (crit.base 100) through GearHitSys: the attacker's viewer gets 'CRIT!' (angle 30 - 20) and then vanilla's own "
          "number (DamageSystems$EntityUIEvents, queued after it in the same dispatch); vanilla's Impact_Critical sparks go to the attacker only, at "
          "the hit location: %s / %s" % (lines1, sp1))
    # the trial switch ON: our style swapped in for this attacker BEFORE the popup and the number (both drawn red), the restore pending
    Cfg.CRIT_STYLE = True
    ups2_, d2_ = crit_hit()
    lines2 = [utxt(u_) for u_ in ups2_]
    check(lines2[:2] == ["style [1, 2]", "number CRIT! @10"] and lines2[2].startswith("number ") and len(lines2) == 3
          and int(ACrit.NPEND) == 1 and bool(ACrit.open(ref_p, ref_mob)) and [int(x_) for x_ in mob_list.getComponentIds()] == [0, 1],
          "AD4(d): crit.fx.style ON - the mob's style list for THIS attacker = [health bar, our style] queued first, then 'CRIT!', then vanilla's number "
          "(so both draw red + bigger); the server's own list stays [0, 1]; one restore pending: %s" % lines2)
    # a second crit on the same pair only pushes the restore out (one entry, never a swapped list stored)
    ups3_, _d3 = crit_hit()
    check(int(ACrit.NPEND) == 1 and [utxt(u_) for u_ in ups3_][0] == "style [1, 2]", "AD4(d): a second crit on the same mob keeps ONE pending restore")
    # GearCritTick: not due yet -> nothing; ~0.6 s later -> the server's list goes back to this attacker; then nothing pending
    viewer_.updates.clear()
    tick_ = ACTick()
    AcChunk.REF = ref_p
    tick_.tick(JFloat(0.05), JInt(0), chk_, None, buf_)
    early_ = viewer_.updates.get(ref_mob)
    time.sleep(float(ACrit.RESTORE_MS) / 1000.0 + 0.1)
    tick_.tick(JFloat(0.05), JInt(0), chk_, None, buf_)
    late_ = viewer_.updates.get(ref_mob)
    late_l = [] if late_ is None else [utxt(u_) for u_ in late_.toUpdatesArray()]
    check(early_ is None and late_l == ["style [0, 1]"] and int(ACrit.NPEND) == 0 and not bool(ACrit.open(ref_p, ref_mob)),
          "AD4(e): the REAL GearCritTick - nothing before %d ms; after it the mob's server list [0, 1] (vanilla number + health bar) goes back to the "
          "attacker; nothing pending: %s" % (int(ACrit.RESTORE_MS), late_l))
    # a restore whose mob left the attacker's view is dropped (vanilla re-sends the real list when it comes back) - no throw
    crit_hit()
    viewer_.visible.remove(ref_mob)
    viewer_.updates.clear()
    n4_ = int(ACrit.N[4])
    time.sleep(float(ACrit.RESTORE_MS) / 1000.0 + 0.1)
    AcChunk.REF = ref_p
    tick_.tick(JFloat(0.05), JInt(0), chk_, None, buf_)
    check(viewer_.updates.get(ref_mob) is None and int(ACrit.N[4]) == n4_ + 1 and int(ACrit.NPEND) == 0,
          "AD4(e): the mob left view before the restore -> nothing sent (queueUpdate would throw 'Entity is not visible!'), the entry dropped")
    # an attacker that left (its Ref no longer valid - its own tick never runs again) and an entry past its drop time are purged, so the
    # pending count returns to 0 and GearCritTick stops looking
    gone_ = mkref(77)
    acf(RFc, "index").setInt(gone_, JInt(-2147483648))
    nowp_ = int(SysJ.currentTimeMillis())
    ACrit.pend(gone_, ref_mob, JArray(JInt)([0, 1]), JLong(nowp_))
    ACrit.pend(ref_p, ref_v, JArray(JInt)([0, 1]), JLong(nowp_ - 60000))
    np0_ = int(ACrit.NPEND)
    ACrit.purge(JLong(nowp_))
    check(np0_ == 2 and int(ACrit.NPEND) == 0 and int(ACrit.PEND.size()) == 0 and int(ACrit.LAST_PURGE) == nowp_,
          "AD4(e): purge drops the entries of an attacker whose Ref is gone and every entry past its drop time (2 -> 0 pending)")
    # not visible at the hit: nothing queued at all (no exception), counted
    n8_ = int(ACrit.N[8])
    ups5_, _d5 = crit_hit(vanilla_=False)
    check(ups5_ == [] and int(ACrit.N[8]) == n8_ + 1 and not [str(x) for x in Gear.ONCE.keySet() if "GearCritSys" in str(x)],
          "AD4(d): a crit on a mob the attacker cannot see sends nothing (the visible check comes before every send) and throws nothing")
    viewer_.visible.add(ref_mob)
    # the style asset not loaded -> no swap (only loaded indices are ever sent), the popup still shows, one WARN
    eui_map2 = indexed({"CombatText": van_ct, "Healthbar": van_hb})
    fz(ILT, "nextIndex").set(eui_map2, JClass("java.util.concurrent.atomic.AtomicInteger")(2))
    acf(EUIc.class_.getName(), "ASSET_STORE").set(None, zstore(eui_map2))
    ups6_, _d6 = crit_hit()
    l6_ = [utxt(u_) for u_ in ups6_]
    acf(EUIc.class_.getName(), "ASSET_STORE").set(None, zstore(eui_map))
    check(l6_[0] == "number CRIT! @10" and not any(x_.startswith("style") for x_ in l6_) and "critasset" in [str(x) for x in Gear.ONCE.keySet()],
          "AD4(d): the style asset not loaded -> no style list sent (no unknown index ever reaches the client), 'CRIT!' still shows, one WARN: %s" % l6_)
    # the player's own switch off (Settings: Crit effects) -> nothing for their crits
    @JImplements("java.util.function.Function")
    class SetGet:
        @JOverride
        def apply(self, o_):
            a_ = list(o_)
            return JClass("java.lang.Boolean").valueOf(False) if (len(a_) >= 2 and str(a_[1]) == "gear.critFx") else None
    bridge.put("settings:fn:get", SetGet())
    ups7_, _d7 = crit_hit()
    bridge.remove("settings:fn:get")
    check([utxt(u_) for u_ in ups7_] == [utxt(ups7_[0])] and utxt(ups7_[0]).startswith("number ") and "CRIT" not in utxt(ups7_[0]) and not PHJ.SENT,
          "AD4(d): the player's switch 'Crit effects' off -> only vanilla's number, no popup, no sparks, no style: %s" % [utxt(u_) for u_ in ups7_])
    # crit.fx off + the trial on -> the red number only; sparks 'everyone nearby' -> both players within 75 blocks get the burst
    Cfg.CRIT_FX = False
    ups8_, _d8 = crit_hit()
    l8_ = [utxt(u_) for u_ in ups8_]
    Cfg.CRIT_FX = True
    Cfg.CRIT_STYLE = False
    time.sleep(float(ACrit.RESTORE_MS) / 1000.0 + 0.1)
    AcChunk.REF = ref_p
    tick_.tick(JFloat(0.05), JInt(0), chk_, None, buf_)
    check(l8_[0] == "style [1, 2]" and not any("CRIT" in x_ for x_ in l8_) and len(l8_) == 2, "AD4(d): crit.fx off + the trial on -> only the swap + vanilla's number: %s" % l8_)
    # 'everyone nearby': ParticleUtil's own 75-block collect through the player spatial resource (a SpatialResource over a SpatialStructure that
    # answers both players), SpawnParticleSystem to each
    @JImplements("com.hypixel.hytale.component.spatial.SpatialStructure")
    class Near:
        @JOverride
        def size(self): return 2
        @JOverride
        def rebuild(self, d_): return None
        @JOverride
        def closest(self, p_): return ref_p
        @JOverride
        def collect(self, p_, r_, out_):
            out_.add(ref_p)
            out_.add(ref_v)
        @JOverride
        def collectCylinder(self, p_, r_, h_, out_): return None
        @JOverride
        def collectBox(self, a_, b_, out_): return None
        @JOverride
        def ordered(self, p_, r_, out_): return None
        @JOverride
        def ordered3DAxis(self, p_, a_, b_, c_, out_): return None
        @JOverride
        def dump(self): return "near"
    SPR = JClass("com.hypixel.hytale.component.spatial.SpatialResource")(Near())
    BufAll = mkfake("SkyyAdBuf", AcBufC.getName(), [
        "F public static Object RES = null;",
        "public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return (com.hypixel.hytale.component.Resource) RES; }"])
    JClass(BufAll.getName()).RES = SPR
    buf_all = UZ.allocateInstance(BufAll)
    Cfg.CRIT_SPARKS = "all"
    PHJ.SENT.clear()
    viewer_.updates.clear()
    hot_.setItemStackForSlot(sh(0), gstack("Weapon_Sword_Crude", 6))
    d9_ = DMGc(DENTc(ref_p), JInt(CIDX["Physical"]), JFloat(6.0))
    AcChunk.REF = ref_mob
    hs_.handle(JInt(0), chk_, None, buf_all, d9_)
    csys_.handle(JInt(0), chk_, None, buf_all, d9_)
    sp9 = sorted((str(w_), str(p_.particleSystemId), round(float(p_.position.y), 2)) for w_, p_ in PHJ.SENT)
    Cfg.CRIT_SPARKS = "off"
    PHJ.SENT.clear()
    crit_hit()
    sp_off = list(PHJ.SENT)
    Cfg.CRIT_SPARKS = "self"
    check(sp9 == [("attacker", "Impact_Critical", 64.9), ("bystander", "Impact_Critical", 64.9)] and not sp_off,
          "AD4(d): sparks 'everyone nearby' -> both players in ParticleUtil's 75-block collect get the burst (no hit location: the mob's position "
          "+ 0.9); 'nobody' -> none: %s" % sp9)
    # an overcrit (chance above 100 %) shows the overcrit text; the text rows: plain ASCII only (the number font), never null
    Cfg.CRIT_BASE = 200.0
    ups10_, _d10 = crit_hit()
    check(utxt(ups10_[0]) == "number CRIT!! @10", "AD4(d): an overcrit (crit.base 200 = every hit doubles twice) shows 'CRIT!!': %s" % utxt(ups10_[0]))
    Cfg.CRIT_BASE = 100.0
    Cfg.CRIT_TEXT = "<b>x</b>"
    ups11_, _d11 = crit_hit()
    Cfg.CRIT_TEXT = "CRIT!"
    check(utxt(ups11_[0]) == "number CRIT! @10", "AD4(d): a popup text that is not plain (markup slipped into memory) falls back to 'CRIT!' - the client never gets null / markup")
    ch_ok = [str(Cfg.checkCritText("crit.fx.text", v_)) for v_ in ("CRIT!", "Crit +2", "BOOM?!")]
    ch_bad = [Cfg.checkCritText("crit.fx.text", v_) for v_ in ("", "   ", "★ CRIT", "<b>CRIT</b>", "A" * 17, "CRIT#1")]
    pt_ = Props()
    pt_.setProperty("crit.fx.text", "★")
    pt_.setProperty("crit.fx.sparks", "maybe")
    Cfg.apply(pt_, True)
    lt_ = (str(Cfg.CRIT_TEXT), str(Cfg.CRIT_SPARKS))
    Cfg.apply(Props(), False)
    check(ch_ok == ["None"] * 3 and all(x_ is not None for x_ in ch_bad) and lt_ == ("CRIT!", "self"),
          "AD4(f): crit.fx.text check hook - plain 1-16 characters pass, empty / symbols / markup / 17 characters are refused; a hand-edited bad "
          "text or sparks value loads as the default ('CRIT!', 'self')")
    # (g) the per-hit fix: an EntityUI asset reload re-adds our style to a mob's server list (update() again) -> the next landed hit of a player
    # strips the server list and sends THIS attacker the clean list before vanilla's number - no second (red) number ever
    Cfg.CRIT_BASE = 0.0
    polluted = mk_ucl()
    putc(ref_mob, "ucl", polluted)
    ups12_, _d12 = crit_hit()
    l12_ = [utxt(u_) for u_ in ups12_]
    check([int(x_) for x_ in polluted.getComponentIds()] == [0, 1] and l12_[0] == "style [0, 1]" and l12_[1].startswith("number ") and len(l12_) == 2,
          "AD4(g): a mob whose list carries our style again (asset reload) - a plain hit strips the server list AND queues the clean list to the "
          "attacker BEFORE vanilla's number: %s" % l12_)
    ups13_, _d13 = crit_hit()
    check([utxt(u_) for u_ in ups13_] == [utxt(ups13_[0])] and utxt(ups13_[0]).startswith("number "), "AD4(g): the next hit needs no fix (one number only)")
    putc(ref_mob, "ucl", mob_list)
    # the unordered fallback never swaps (the number could already be queued); no tick = no swap either
    Cfg.CRIT_BASE = 100.0
    Cfg.CRIT_STYLE = True
    csysU_ = J("GearCritSysU")()
    viewer_.updates.clear()
    hot_.setItemStackForSlot(sh(0), gstack("Weapon_Sword_Crude", 6))
    du_ = DMGc(DENTc(ref_p), JInt(CIDX["Physical"]), JFloat(6.0))
    AcChunk.REF = ref_mob
    hs_.handle(JInt(0), chk_, None, buf_, du_)
    csysU_.handle(JInt(0), chk_, None, buf_, du_)
    lu_ = [utxt(u_) for u_ in list(viewer_.updates.get(ref_mob).toUpdatesArray())]
    ACrit.TICK_OK = False
    ups14_, _d14 = crit_hit(vanilla_=False)
    ACrit.TICK_OK = True
    Cfg.CRIT_STYLE = False
    check(not bool(csysU_.ordered) and lu_ == ["number CRIT! @-20"] and [utxt(u_) for u_ in ups14_] == ["number CRIT! @10"] and int(ACrit.NPEND) == 0,
          "AD4(d): the unordered fallback GearCritSysU never swaps (popup only; this hit has no hit angle: 0 - 20 = -20): %s; without the restore "
          "tick (TICK_OK false) no swap either" % lu_)
    # GearLeechSys (Inspect, unordered) still takes INFO; the crit table is separate: a Damage cancelled on the way keeps no state forever
    Hit.CRIT.clear()
    for k_ in range(600):
        Hit.putCrit(JObject(k_), JInt(1))
    check(int(Hit.CRIT.size()) <= 513 and Hit.takeCrit(None) is None, "AD4(h): the crit table stays small (cleared above 512 like INFO; takeCrit(null) = null)")
    Hit.CRIT.clear()
    # (i) the rows + the player switch + the wiring
    for k_, want_ in (("crit.fx", ("bool", "true", "live")), ("crit.fx.sparks", ("choice", "self", "live")), ("crit.fx.style", ("bool", "false", "live")),
                      ("crit.fx.text", ("text", "CRIT!", "live,adv")), ("crit.fx.textOver", ("text", "CRIT!!", "live,adv"))):
        check(rwb.get(k_, ("",))[:3] == want_ and len(rwb[k_][3]) <= 100, "AD4(i): Server Setup row %s = %s (help %d)" % (k_, rwb.get(k_, ("",))[:3], len(rwb.get(k_, ("", "", "", ""))[3])))
    check(str(dict(zip([str(k_) for k_ in Rows.KEYS], [str(o_) for o_ in Rows.OPTS]))["crit.fx.sparks"]) == "self|Only the attacker,all|Everyone nearby,off|Nobody",
          "AD4(i): who sees the sparks: Only the attacker / Everyone nearby / Nobody")
    check('"gear.critFx"' in bsrc22 and "regSetting(\"gear.critFx\", \"Crit effects\", \"combat\", true" in bsrc22 and "gear.critFx" in su22,
          "AD4(i): the player switch 'Crit effects' (gear.critFx, default on) is registered in setup()")
    ps22 = mcode("SkyyGearPlugin", "setup")
    wh22 = mcode("GearHit", "weaponHit")
    cs22 = mcode("GearCrit", "setup")
    check(0 <= ps22.find("GearFx.setup(") < ps22.find("GearCrit.setup(") and "GearCritSys.<init>" in cs22 and "GearCritSysU.<init>" in cs22
          and "GearCritClean.<init>" in cs22 and "GearCritTick.<init>" in cs22 and "EntityTrackerSystems$EntityViewer" not in mcode("GearLeechSys", "handle")
          and 0 <= wh22.find("GearHit.hitAmount(") < wh22.find("GearHit.critLevel(") < wh22.find("GearHit.putCrit(")
          and "GearHit.take(" in mcode("GearLeechSys", "handle"),
          "AD4(i): wiring - GearCrit.setup right after GearFx.setup registers GearCritSys (ordered + fallback), GearCritClean, GearCritTick; weaponHit = "
          "hitAmount -> critLevel -> putCrit; GearLeechSys still takes INFO")
    print("AD4. crit effects done: popup %s, sparks %s, swap / restore / strip / per-hit fix / fallbacks executed" % (lines1[0], sp1[0][1]))
    Cfg.CRIT_BASE = 0.0
    Cfg.CRIT_FX, Cfg.CRIT_SPARKS, Cfg.CRIT_STYLE, Cfg.CRIT_TEXT, Cfg.CRIT_TEXT2 = True, "self", False, "CRIT!", "CRIT!!"

    # ---- AD5. access: every engine member the new classes use resolves from a plain lookup (the build's access audit, re-checked here)
    MHL = JClass("java.lang.invoke.MethodHandles").publicLookup()
    MT = JClass("java.lang.invoke.MethodType")
    acc_bad = []
    for cls_, nm_, rt_, args_ in ((EVWc, "queueUpdate", "void", [REFc, JClass("com.hypixel.hytale.protocol.ComponentUpdate")]),
                                   (UCLc, "getComponentIds", "int[]", []), (UCLc, "update", "void", []),
                                   (ItemZ, "unshareWeapon", "w", []), (ItemZ, "invalidatePacketCache", "void", [])):
        try:
            rcls_ = {"void": JClass("java.lang.Void").TYPE, "int[]": JClass("java.lang.Class").forName("[I"), "w": IWPc.class_}[rt_]
            MHL.findVirtual(cls_.class_, nm_, MT.methodType(rcls_, JArray(JClass("java.lang.Class"))([a_.class_ for a_ in args_])))
        except Exception as e_:
            acc_bad.append("%s.%s: %s" % (cls_.class_.getSimpleName(), nm_, str(e_)[:80]))
    check(not acc_bad, "AD5: the new engine calls resolve from MethodHandles.publicLookup (EntityViewer.queueUpdate, UIComponentList.getComponentIds / update, "
                       "Item.unshareWeapon / invalidatePacketCache): %s" % acc_bad)
    print("AD5. access re-check done")

    # ---- AD10. class byte-compare 0.2.1 -> 0.2.2 (the AC10 machinery): every difference must be one of the listed 0.2.2 parts
    jar021c = os.path.join(HERE, "SkyyGear-0.2.1.jar")
    if os.path.isfile(jar021c) and "cls_members" in dir():
        pa6 = Pool(False)
        pa6.appendClassPath(jar021c)
        pa6.appendClassPath(B.SERVER_JAR)
        pa6.appendSystemPath()
        pb6 = Pool(False)
        pb6.appendClassPath(jar)
        pb6.appendClassPath(B.SERVER_JAR)
        pb6.appendSystemPath()
        n21c = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar021c).namelist() if n_.endswith(".class"))
        n22c = sorted(n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(jar).namelist() if n_.endswith(".class"))
        add6 = sorted(c_[len(PKG):] for c_ in set(n22c) - set(n21c))
        gone6 = sorted(set(n21c) - set(n22c))
        diffs6 = {}
        for cn_ in sorted(set(n21c) & set(n22c)):
            ma_, mb_ = cls_members(pa6, cn_), cls_members(pb6, cn_)
            dd_ = sorted(k_ for k_ in set(ma_) | set(mb_) if ma_.get(k_) != mb_.get(k_))
            if dd_:
                diffs6[cn_[len(PKG):]] = [("+" if k_ not in ma_ else ("-" if k_ not in mb_ else "~")) + k_ for k_ in dd_]
        BDs = "Lorg/bson/BsonDocument;"
        EXPECT022 = {
            # config kit: six new rows, VERSION 0.2.1 -> 0.2.2
            "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport([Ljava/lang/Object;)Ljava/lang/Object;"],
            "CfgRows": ["~<clinit>", "~f VERSION", "~m header()[Ljava/lang/Object;"],
            # the shot lines + no hints + the box readers
            "GearBase": ["-f HINT_A", "-f HINT_W", "+m armoryAsk(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;",
                         "+m armoryGet(Ljava/lang/String;)Ljava/lang/String;", "+m armoryQuickPct()D", "+m armoryTuneOn()Z",
                         "+m inum(Ljava/lang/Object;)I", "~m maxEntry(Ljava/lang/String;)F", "+m prjDamage(Ljava/lang/String;I)D",
                         "~m range(Ljava/lang/String;" + BDs + ")[F", "+m shots(Ljava/lang/String;" + BDs + ")[Ljava/lang/Object;"],
            "GearView": ["~m apply(Lcom/hypixel/hytale/server/core/inventory/ItemStack;" + BDs + "Ljava/util/UUID;)Lcom/hypixel/hytale/server/core/inventory/ItemStack;",
                         "~m damageText(Ljava/lang/String;)Ljava/lang/String;", "-m hints(Ljava/util/ArrayList;Ljava/util/ArrayList;)V",
                         "~m statLines(Ljava/lang/String;" + BDs + "Ljava/util/ArrayList;Ljava/util/ArrayList;)V"],
            # the rows' fields, the loader, the text check, the default text, the SkyyArmory epoch
            "GearCfg": ["~<clinit>", "+f CF_LINES", "+f CRIT_FX", "+f CRIT_SPARKS", "+f CRIT_STYLE", "+f CRIT_TEXT", "+f CRIT_TEXT2", "+f HIDE_BOX",
                        "~m apply(Ljava/util/Properties;Z)V", "~m cfgEpoch()J", "+m checkCritText(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;",
                        "+m critText(Ljava/util/Properties;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "+m critTextOk(Ljava/lang/String;)Z",
                        "~m defaultsText()Ljava/lang/String;"],
            # the crit level + its table
            "GearHit": ["~<clinit>", "+f CRIT", "+m critLevel([IDD)I", "+m putCrit(Ljava/lang/Object;I)V", "+m takeCrit(Ljava/lang/Object;)Ljava/lang/Integer;",
                        "~m weaponHit(Lcom/hypixel/hytale/server/core/modules/entity/damage/Damage;Ljava/util/UUID;Lcom/hypixel/hytale/server/core/universe/PlayerRef;"
                        "Lcom/hypixel/hytale/server/core/inventory/ItemStack;ZLcom/skyy/gear/GearShot;Lcom/skyy/gear/GearShot;"
                        "Lcom/hypixel/hytale/server/core/inventory/container/ItemContainer;)[Ljava/lang/Object;"],
            # setup(): the box listener, the crit setup, the player switch, the ready line; start() is new
            "SkyyGearPlugin": ["~m setup()V", "+m start()V"],
        }
        check(add6 == ["GearBox", "GearBoxL", "GearCrit", "GearCritClean", "GearCritCleanU", "GearCritSys", "GearCritSysU", "GearCritTick"] and not gone6,
              "AD10: new classes = GearBox / GearBoxL (the vanilla box) + GearCrit / GearCritSys(+U) / GearCritClean(+U) / GearCritTick (crit effects), "
              "none removed: %s / %s" % (add6, gone6))
        unexp6 = dict((c_, [m_ for m_ in v_ if m_ not in EXPECT022.get(c_, [])]) for c_, v_ in diffs6.items())
        unexp6 = dict((c_, v_) for c_, v_ in unexp6.items() if v_)
        missing6 = dict((c_, [m_ for m_ in v_ if m_ not in diffs6.get(c_, [])]) for c_, v_ in EXPECT022.items())
        missing6 = dict((c_, v_) for c_, v_ in missing6.items() if v_)
        check(not unexp6, "AD10: no difference outside the listed 0.2.2 parts: %s" % unexp6)
        check(not missing6, "AD10: every listed 0.2.2 part is really in the jar: %s" % missing6)
        za6, zb6 = zipfile.ZipFile(jar021c), zipfile.ZipFile(jar)
        ea6 = [n_ for n_ in za6.namelist() if not n_.endswith(".class")]
        eb6 = [n_ for n_ in zb6.namelist() if not n_.endswith(".class")]
        ediff6 = sorted(n_ for n_ in set(ea6) | set(eb6) if n_ not in ea6 or n_ not in eb6 or za6.read(n_) != zb6.read(n_))
        check(ediff6 == ["Server/Entity/UI/SkyyGear_CritText.json", "manifest.json"],
              "AD10: non-class entries: + the crit style asset, manifest.json changed; recipes, qualities and lang byte-identical: %s" % ediff6)
        print("AD10. class compare 0.2.1 -> 0.2.2: %d classes changed (%s), new %s" % (len(diffs6), ", ".join(sorted(diffs6)), add6))
    else:
        check(False, "AD10: SkyyGear-0.2.1.jar (or the compare helper) not found - the class compare could not run")

    # tidy: the bridge keys this section added, SkyyArmory's kit, the EntityUI model
    bridge.remove("armory:fn:info")
    try:
        APub.shutdown()
    except Exception:
        pass
    ACfgA.useDefaults()
    acf(EUIc.class_.getName(), "ASSET_STORE").set(None, old_eui)
    ABox.SNAP.clear()
    ABox.STARTED = False
    print("AD. 0.2.2 done")

    # ---- restore the bare-JVM state this section changed (it is the last section; kept tidy anyway)
    Track.SHOTS.clear()
    for cn_, o_ in old_single.items():
        fi_ = JClass(cn_).class_.getDeclaredField("instance")
        fi_.setAccessible(True)
        fi_.set(None, o_)
    acf(DCSc.class_.getName(), "ASSET_STORE").set(None, old_dcs_store)
    acf(ESTc.class_.getName(), "ASSET_STORE").set(None, old_est_store)
    acf(LPRJc.class_.getName(), "ASSET_STORE").set(None, old_lprj)
    Chg.clear()
    for f_, v_ in zip(("HEALTH", "MANA", "STAMINA"), old_dst):
        acf(DSTc.class_.getName(), f_).setInt(None, JInt(v_))
    for k_, v_ in list(old_armor_items.items()) + list(old_weapon_items.items()):
        if v_ is None:
            imap.remove(k_)
        else:
            imap.put(k_, v_)
    fz(Inter, "ASSET_STORE").set(None, zstore(indexed(MZ.inter)))
    fz(RootI, "ASSET_STORE").set(None, zstore(indexed(MZ.roots)))
    for u_ in (U1, U2):
        bridge.remove("class:skill:" + str(u_))
        Gate.forget(u_)
    skills_off()
    Cfg.apply(Props(), False)
    Base.clear()
    print("AC. 0.2.1 base stats by level done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyGear/build_skyygear_%s.py)" % (JAR, VERSION))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH, "--live", LIVE], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
