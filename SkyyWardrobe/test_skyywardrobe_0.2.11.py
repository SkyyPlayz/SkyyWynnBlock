"""Harness for SkyyWardrobe 0.2.11 (tools/wardrobe_0_2_11_patch.py; Skyy: "i dont see my dragon in the requip list and the dog still
shows up as a sword.").
Derived from test_skyywardrobe_0.2.10.py: EVERY 0.2.10 section runs again on the 0.2.11 jar (W2's pet order is now rarity, name; the
pet Sort says "rarity, name"), plus:
  RQ  (inside W, after PI) SkyyPets' file gains a Plain Dragon (kind DragonPlain), a Tundra Dragon and a Dog; the test asset map knows
      their portraits. The picker (9 rows like Skyy's: Keep, None + 7 pets) is sorted rarity, name, level (Common Dog, Common Rabbit,
      Rare Wolf, Epic Bear, Epic Plain Dragon, Epic Tundra Dragon Lv 9 above Lv 2); each row carries its kind's own portrait
      (Skyy_PetIcon_Dog / Rabbit / Wolf / Bear / DragonPlain / DragonTundra), no collar; the kind from the FILE wins over the label;
      without the file kind the label guess finds the dragons (words reversed); an unknown kind / an odd kind in the file -> the collar.
      SEARCH: the box has an Enter (Validating) binding sending the same "q" data as the Search button; 'dra' -> Keep, None + the two
      dragons only ('DRA' too), the footer "2 pets - search: dra", the box drawn holding "dra"; Clear -> every row back, the box empty;
      a search of one tab is not the pet picker's (tabs keep their own). FIT: every normal row of the pool list is 47 high (7 whole
      rows in the 346 px list, <= 6 px of an 8th), the page is 980 high (fits 1080), the kit checks pass on the 9-row picker.
  C   class compare 0.2.10 -> 0.2.11 (--base): no class added; WdBridge + PKIND, rarRank, lvOf, petCmp; WdPage + petIcon
  Repro: python SkyyWardrobe/test_skyywardrobe_0.2.11.py --jar SkyyWardrobe/SkyyWardrobe-0.2.10.jar  -> RQ fails (dragons = the collar,
      no Enter binding, the 8th row half cut off)
The 0.2.10 harness text follows:
Harness for SkyyWardrobe 0.2.10 (tools/wardrobe_0_2_10_patch.py; Skyy: "can we make this show the pet icon").
Derived from test_skyywardrobe_0.2.9.py: EVERY 0.2.9 section runs again on the 0.2.10 jar, plus:
  PI  (inside W, after W3) the test asset map holds a Skyy_PetIcon_<Kind> item for every kind SkyyPets 0.4.4 builds (KINDS + KINDS_043,
      read from SkyyPets/build_skyypets_0.4.4.py) EXCEPT Gecko (= an older / missing portrait). WdPage.petPic: each kind's label (rarity +
      SkyyPets' display name, Skeleton = "Skeleton Archer") -> Skyy_PetIcon_<Kind>; Gecko (no item) -> the fallback; an unknown kind
      ("Epic Dragon"), a null / empty / odd label (a quote, too long) -> the fallback; a label without rarity word still works. The page:
      the picked Pet cell + the picker rows carry Skyy_PetIcon_Wolf / Rabbit / Bear (no Farming_Collar); an unknown kind in the list =
      Farming_Collar (no empty ItemId); the page passes SUI.assert_menu_page + check_page + check_sky_paths (the kit checks)
  C   class compare 0.2.9 -> 0.2.10 (--base): no class added; WdPage + petPic only (refViews / refList: bodies)
  Repro: python SkyyWardrobe/test_skyywardrobe_0.2.10.py --jar SkyyWardrobe/SkyyWardrobe-0.2.9.jar  -> PI fails (every pet = the collar)
The 0.2.9 harness text follows:
Harness for SkyyWardrobe 0.2.9 (tools/wardrobe_0_2_9_patch.py; FP1 review LOW: Deposit all leaves claimed food / potions).
Derived from test_skyywardrobe_0.2.8.py: EVERY 0.2.8 section runs again on the 0.2.9 jar, plus:
  RF  (inside X, after FP) a supply:fn:claims stand-in (bread + health potions claimed): Deposit all (+ deposit.hotbar) leaves the plain
      claimed storage + backpack stacks (the REPRO: 0.2.8 pooled them), takes the unclaimed potion, the helmet, a metadata bread and the
      hotbar bread; one ask per distinct id; a single Deposit click of claimed bread still goes in; claims answering FALSE / a bad answer /
      throwing (no exception escapes) / missing = as 0.2.8; auto-store unchanged; conservation + exactly once after every step
  C   class compare 0.2.8 -> 0.2.9 (--base): no class added; WdBridge + claimed only (depAllSkip: body)
  Repro: python SkyyWardrobe/test_skyywardrobe_0.2.9.py --jar SkyyWardrobe/SkyyWardrobe-0.2.8.jar  -> RF fails (the claimed food is pooled)
The 0.2.8 harness text follows:
Harness for SkyyWardrobe 0.2.8 (tools/wardrobe_0_2_8_patch.py; round FP1: the Potion Flask + Food Pouch are built-in kept ids).
Derived from test_skyywardrobe_0.2.7.py: EVERY 0.2.7 section runs again on the 0.2.8 jar, plus:
  FP  (inside X, after X5) WdCfg.builtinKeep / keep for both prefixes (look-alikes not), still kept with swap.keepIds "-" (the Menu item
      then not); the Items space refuses them (single deposit from storage + hotbar, also with items.allow naming them); Deposit all (with
      deposit.hotbar) leaves them; a loadout that picks Empty / a potion kind for their hotbar slots leaves them where they are on Equip;
      nothing of either prefix ever in the pool; conservation + exactly once
  C   class compare 0.2.7 -> 0.2.8 (--base): no class added; WdCfg + builtinKeep only (other changes are bodies)
The 0.2.7 harness text follows:
Harness for SkyyWardrobe 0.2.7 (tools/wardrobe_0_2_7_patch.py; THE REQUIP SALVAGE BUTTON, Skyy 2026-10-16: "add a 4th button to sell
gear you dont want." -> "Salvage to materials (Recommended)" + "Drops give less (Recommended)").
Derived from test_skyywardrobe_0.2.6.py: EVERY 0.2.6 section runs again on the 0.2.7 jar (the Z "Sell comes soon" check re-aimed: with no
SkyyGear the button answers "Salvage needs SkyyGear 0.3.17"), plus:
  SV  (inside X, after MP) THE SALVAGE on the real page + WdOps op 17 against a gear:fn:salvage stand-in that keeps SkyyGear's contract
      (quote / commit / release, its journal of keys, its refusals): the quote text (materials + the loadouts that lose it), the
      two-click confirm (the first click changes nothing), exactly once on a double / third click, the loadout picks cleared,
      storage-first with a top-up of the same plain stack, requip.log SALVAGE ... (no coins), NO coin bridge called; refusals (lifelong,
      unidentified, a potion kind, an OUT entry, a plain non-gear piece, salvage off, no SkyyGear, full inventory, a piece Requip's own
      journal still lists) change nothing; a refused commit puts the piece + its picks back; a save failure (once / twice); a failed
      give is owed and given on the next action; CRASH AT EVERY STEP (1-8) and after every file of the removal save, with the
      inventory as it was AND rolled back to before the salvage: after the restart + repair the piece is back XOR its materials were
      given exactly, SkyyGear's journal holds the key iff the materials were given, exactly once, a second repair / restart changes
      nothing; owed materials (no room after a crash) wait and are given once there is room (in-session and after a restart); the
      keep-window sweep and the stop close the given journals
  C   class compare 0.2.6 -> 0.2.7 (--base): WdSalv added, no member of another class changed (bodies only)
The 0.2.6 harness text follows:
Harness for SkyyWardrobe 0.2.6 (tools/wardrobe_0_2_6_patch.py; MENU PATTERN sweep S2, Skyy 2026-10-16: "I never want to have to use a
back button. The menus at the top should always be there for easy navigation." + "keep this top bar at this size consistent at the top
across every menu." + "i dont mind scrolling, but if there are only a few items try to scale them to all fit.").
Derived from test_skyywardrobe_0.2.5.py: EVERY 0.2.5 section runs again on the 0.2.6 jar (the view tab checks re-aimed at the sub-tab row
#SkyyRqSub0..3; the "search above the tabs" check at the search above the pool list), plus:
  MP  (inside X, after X16) THE MENU PATTERN on the REAL page builder: the tab registered (WdHubOpen.register = HUB_TABS' row; the Storage
      tabs of the other mods stand in), every view built - Armor / Weapons / Items / Inventory, the pocket-block, pet, ability and modifier
      pickers, a loadout slot selected, a long and a short list, the 0.1 question and returned-items notes, Requip shut - and each one
      passes SUI.assert_menu_page (1600 x 980, row 1 + row 2 with Requip selected, ONE sub-tab row, no back / < Menu / pager text, the
      content fits), check_page, check_sky_paths, every b.set / binding names an element that exists; the sub-tab clicks (tabv0 / 4 / 1
      / 2: no page token) switch the view like the old "tab" click, the picker's own sub-tab answers; a short loadout list = bigger rows;
      HubBar.route: the X closes, the own tab redraws, another hub / tab is handed on; nothing moved (exactly once)
  J   the jar = the classes + HubBar + WdHubOpen + manifest + the 59 kit files (IncludesAssetPack true)
  B   setup() puts the hub tab last (WdHubOpen.register)
  C   class compare 0.2.5 -> 0.2.6 (--base): HubBar + WdHubOpen added, members changed only in WdPage (hubAck, LSH)
The 0.2.5 harness text follows:
Harness for SkyyWardrobe 0.2.5 (tools/wardrobe_0_2_5_patch.py; Skyy 2026-10-16: "allow scrolling here." + "make it so, if you click
take out, the auto store doesn't put it back in automatically." + "add a 4th button to sell gear you dont want. and move the search above
the Armor, weapons and items section." + "i dont mind scrolling, but if there are only a few items try to scale them to all fit.").
Derived from test_skyywardrobe_0.2.4.py: EVERY 0.2.4 section runs again on the 0.2.5 jar; the paging checks (X16 inventory page 2, the Z
"more than one page" block) are re-aimed at the one scrolling list, plus:
  S   (inside X, after Z) THE SCROLLING LIST on the real page builder: 180 swords = the first 150 rows drawn + "The first 150 of 180", the
      pool area is TopScrolling, no Prev / Page / Next; a hotbar slot + a click on row 140 picks THAT eid; row 141 selected -> Take out
      takes THAT eid (marked, exactly once); Forget asks about the row's own item; search (none / one) and Sort keep working; the row
      size: <= 4 rows = 2x high, <= 6 = the 6-row fill, more = 44; the search row sits above the tabs; Sell (disabled look) answers
      "Selling gear comes soon" and moves nothing; Your inventory = one 10-row grid (hotbar + storage, then worn armor + backpack)
  O   (inside X, after FIX-F1) TAKE OUT STAYS OUT: the taken-out item carries SkyyRequipOut {p: profile key}; auto-store leaves it after
      a relog (WdAuto.KEEP gone) and after its metadata changes; other gear still auto-stores; a hand deposit (one slot / Deposit all)
      works and the pool entry carries no mark; another profile's mark is ignored; countKindU / unstamp see a marked item as the plain one;
      exactly once throughout
  C   class compare 0.2.4 -> 0.2.5 (--base): no class added or removed; only WdCodec gains members (OUTK, outOf, markOut)
The 0.2.4 harness text follows:
Harness for SkyyWardrobe 0.2.4 (tools/wardrobe_0_2_4_patch.py; Skyy 2026-10-16: "4? we need the 2 ability's you can equip at a time,
and the 2 modifiers for each." then, on the Class page loadout: "ohhh i see whay you put 4 ability's in the wardrobe. that was my bad" ->
the Requip loadout mirrors the class loadout: its 4 rows (Ability 2, Ability 3, Crouch + 2, Crouch + 3), each = the ability + its 2
modifier slots). Derived from test_skyywardrobe_0.2.3.py: EVERY 0.2.3 section runs again on the 0.2.4 jar; W is re-aimed at the new cell
numbers (pet 0, summon 1, row r: ability 2 + 3r, modifiers 3 + 3r / 4 + 3r), plus:
  V   (inside X, after W18) THE MODIFIER SLOTS, every new code path EXECUTED on the real page builders + WdOps with a class:fn:abilMods
      stand-in in SkyyClasses 0.1.29's layout (head + "mid|name|at|unlocked|level|...|now|next|doubles|max" rows) and a class:fn:loadoutSet
      stand-in that applies the "mods=" part slot by slot with the no-doubling rule:
      V1 Keep cells show the live modifiers of each row's ability; V2 the modifier picker = Keep, Empty + only the UNLOCKED modifiers of
         that ability in the tree's order (icons = SkyyTrees' Lattice gems), search; V3 a pick under a Keep row pins that row's ability,
         "abmods" saved; V4 the cell (icon + name + Lv); V5 the other slot's modifier trades places (unless the tree says it doubles);
         V6 refusals (locked, not that ability's, a CLOSED slot - shown "Closed" -, bad values); V7 EQUIP: one class:fn:loadoutSet with
         "mods=<ability>:<m1>+<m2>", again = no call; V8 a swap of the two slots is sent clear-then-set and lands; V9 Empty; V10 a modifier
         no longer unlocked: greyed + skipped at Equip + a line, the other slot still lands; V11 an ability moved to another row takes its
         modifier picks (a crouch row too); V12 another ability on a row starts Keep; V13 an ability that does not land: its modifiers
         skipped + a line, no call; V14 no class:fn:abilMods: the modifier cells hide, picks and Equip say why; V15 records written by the
         0.2.3 jar (own class loader) read by 0.2.4 - all four ability picks kept, modifiers start as Keep, pets / picks kept; V16 a restart
         reads "abmods" back; V17 Save pets/abilities / Reset clear the modifier picks; every selected-slot line <= 130 chars
  T   (after V) LIFELONG TOOLS (Skyy: "this shows my old crude hatchet after i upgraded to copper. and its not letting me put my hoe in the
      items. but it allows the other tools."): T1 every kind (pickaxe, hatchet, each hoe tier, sickle, fishing pole, watering can) classifies
      into Items, deposits and is picked; T2 a tier-up keeps the entry (stamp, not id) and its display follows; T3 a not-with-you record of the
      same lifelong tool next to a present one merges (picks moved, logged), a lone one stays; T4 the one-time plain-tool pass (run-once marker llDone: History copy + Undo line, lowest-eid target, never again)
  C   class compare 0.2.3 -> 0.2.4 (--base): no class added or removed; members changed only in WdBridge, WdCodec, WdData, WdEntry, WdLoad,
      WdOps, WdPage (only additions)
The 0.2.3 harness text follows:
Harness for SkyyWardrobe 0.2.3 (tools/wardrobe_0_2_3_patch.py; Skyy 2026-10-15: "add a slot to show the pets and ability's so you can see,
and edit them per loadout"). Derived from test_skyywardrobe_0.2.2.py: EVERY 0.2.2 section runs again on the 0.2.3 jar, plus:
  W   (inside X, after X16) THE PET / SUMMON / ABILITY SLOTS, every new code path EXECUTED on the real page builders + WdOps:
      W1 six slots under "PET, SUMMON + ABILITIES - <CLASS>" (Keep + what is there now), no old text lines, no empty ItemId / underscore id /
         Left-Right-Top-Bottom alignment; W2 the pet picker = Keep, None + the OWNED pets (ids from the profile's SkyyPets file READ ONLY,
         each checked through pets:fn:petName - a released pet is never listed; the file untouched), cached 3 s, pets:fn:owned preferred when
         published, search by name; W3 a pick saves only the loadout record (one slot Keep = "pets2", the slot shows collar + name + Lv);
         W4 the same pet in the other slot trades places, both picked = 0.2.2's "pets" record exactly, the Keep / Empty / Pocket buttons on
         a pet slot, refusals (a released pet, bad values); W5 the ability picker = Keep + only the abilities UNLOCKED in the class tree
         (class:fn:abilPanel stand-in with SkyyClasses 0.1.29's field layout), a pick onto another key trades places, "abrows" saved,
         refusals (locked, foreign, Empty); W6 EQUIP: pets:fn:loadoutSet(pet, summon) + class:fn:loadoutSet with the LIVE snapshot and the
         picks placed (no change = no call); W7 Keep = the live value, all Keep = no call; W8 a released pet: greyed slot, Equip keeps that
         slot + a line; W9 an ability no longer unlocked: greyed slot + row, Equip keeps that key + a line; W10 another class: kept + a
         line, a new pick clears the old class's picks; W11 Save pets/abilities = 0.2.2's record and Equip sends the saved snapshot EXACTLY,
         a hand pick on it starts from its saved rows and carries its modifiers; W12 all four keys Keep = no abilities saved; W13 a restart
         reads it all back, copy(); W14 a failed save rolls back, a locked loadout refuses; W15 no SkyyPets / no SkyyClasses / no abilPanel /
         no class: slots hide (or fall back), picks + Equip say why; W16 ROLLBACK: the 0.2.2 jar (own class loader) reads the 0.2.3 record;
         W17 Reset forgets the picks; no item appeared or moved, the SkyyPets file was only read;
      W18 FIX ROUND (wd023fix, patch header a-f): Keep slots show the live / predicted value (W1, W5: a Keep key another pick takes),
         another class (Keep refused, a new pick keeps the old snapshot, all-Keep keeps it), empty keys (hidden, refused, never filled at
         Equip, section line), owned-pets order under a 1100-id list, Sort / Pick it / Take out / Forget answer in the pickers, the hint
         (W1) and every selected-slot line <= 130 characters
  C   class compare 0.2.2 -> 0.2.3 (--base): no class added or removed; members changed only in WdBridge, WdLoad, WdOps, WdPage (only
      additions; WdStore changes method bodies only)
The 0.2.2 harness text follows:
Harness for SkyyWardrobe 0.2.2 (tools/wardrobe_0_2_2_patch.py; Skyy 2026-10-15: "i cant tell these apart in the wardrobe." + "id have
weapons seprate from items to make it easier." + "id start with 10 loadouts."). Derived from test_skyywardrobe_0.2.1.py: EVERY 0.2.1 section
runs again on the 0.2.2 jar (crash at every step, the fuzz, the join task ...), with these changes / additions:
  X1  a fresh config.properties holds slots.free=10 + the run-once marker; Z5 WdCfg.migFree EXECUTED on real files: an untouched 4 -> 10
      (marker under the line, every other byte kept, the old bytes in config-history, one config-changes.log line 4 -> 10), run twice =
      nothing, a hand-edited value (CRLF file) kept + marker in CRLF, no line -> slots.free=10 appended, a fresh 0.2.2 file = nothing to do
      (the 0.2.1 sections then run on the 0.1-style file with slots.free=4, as before)
  X16 the page: a hotbar slot opens the WEAPONS tab (the swords); the potion is on the Items tab; the search runs on the Weapons tab
  Z   (inside X16) THE POOL ROWS: names (SkyyGear's describe through a stand-in bridge; Requip's own name without it), rarity colours in the
      markup (RARITY + the kit gold for Untiered), Lv tags, x9 stack tags, the grey line (rarity - state - picked in N loadouts -
      modifiers), identical twins #1 / #2 by deposit order (the same under every sort), the search finds a SkyyGear name, the cache (no
      second bridge call for an unchanged stack), Armor | Weapons | Items | Inventory with counts (a mod weapon without the Weapon_ prefix
      goes to Weapons, tools / food / potions to Items), search + sort remembered per tab, a hotbar slot opens the tab of its pick, a taken
      out row = "on you" + the disabled look, 10 loadouts + the next locked one on the page, every item exactly once
  Z+  fix round: Weapons <-> Items keeps the hotbar slot; long names / grey lines cut with ... within their labels; the detail panel
      and the Take out prompt name a twin as its row (#N); twins numbered newest #1 (the default list reads #1 above #2); 10 entries =
      2 pages: page 2 rows, a pick from page 2, Take out of the last row of the last page (then page 1 of 1), every item once
  B   setup(): WdCfg.migFree runs before WdCfg.load
  C   class compare 0.2.1 -> 0.2.2 (--base): no class added or removed; members changed only in WdCfg (migFree) and WdPage
  D   setup()'s order on the live COPY includes migFree: start 1 may only update config.properties (slots.free 4 -> 10 + marker) and add
      config-history / config-changes.log; start 2 writes nothing
The 0.2.1 harness text follows:
Harness for SkyyWardrobe 0.2.1 (tools/wardrobe_0_2_1_patch.py; research/Code-Structure-Audit.md 9d; Skyy 2026-10-13: "lets audit the
code structure, and make sure they are working together in the smoothest easiest lag free way possible"). Derived from
test_skyywardrobe_0.2.py: EVERY 0.2 section runs again on the 0.2.1 jar - including X's crash-at-every-step of every transaction (each
move, mid-save after every file, after the save) with the live inventory as it was AND rolled back, the random-operation fuzz with "every
item exists exactly once" after every op and every crash (40 + 100 seeds), the join task through the real WdHop / scheduler - plus:
  restart() (a server restart in the harness) also forgets the 0.2.1 journal caches (KNOWN / GEN / PRE) - memory is gone on a restart
  Y (inside X, after X19) 0.2.1 EXECUTED:
    Y1 a crashed equip + join: WdHop.run pre-warms (the profile into the cache, the journal read) off the world thread; the world task
       asks the disk nothing (0 hasFile disk checks, 0 journal reads), uses the pre-read journal, keeps the same cached profile object
       and repairs: every item exactly once (census + once)
    Y2 a clean join: one disk question in the pre-warm, none on the world thread
    Y3 a busy profile is not pre-warmed; a journal written after the pre-read is never used (generation); a pre-read is taken once
    Y4 hasFile: unknown -> one disk question then memory; our write -> true, delete -> false; a leftover file is found after a restart;
       WdTx.run still refuses a change over an unrepaired journal (fixer 1) - from memory
    Y5 ONE LOCK PER KEY: while profile A's journal lock is held, profile B writes / reads / deletes at once; profile A waits; the 0.2 jar
       (control, its own class loader): profile B waits behind the class lock; 0.2.1 has no synchronized journal method
    Y6 FIXER (review), EXECUTED: a journal deleted BY HAND while the cache still says "yes" no longer blocks Requip (the refusal path
       asks the disk once more: RECHECKS) and a real journal is still refused; WdHop.later hands the join repair to the private daemon
       "SkyyWardrobe-reader" (its queue, not the shared scheduler) and the pre-warm runs there; other hops stay on the scheduler
  C  class compare 0.2 -> 0.2.1 (--prev): only the fixer's WdThreads added, none removed; members changed only in WdHop (READER),
     WdJournal and WdRepairTask (+ the config kit's Cfg* classes when tools/skyycfg.py changed)
  D  (re-aimed: the live world now holds 0.2 data) start twice on a scratch COPY writes nothing; the live 0.1 file migrates on the copy
     (or is already migrated: nothing added); the live folder is byte-identical before and after the whole run

    python SkyyWardrobe/test_skyywardrobe_0.2.1.py [--jar <0.2.1 jar>] [--prev <0.2 jar>] [--old <0.1 jar, the M01 fixtures>] [--dir <scratch>]

The 0.2 harness text follows (its sections are unchanged and run again on 0.2.1):
Harness for SkyyWardrobe 0.2 "Requip" (derived from test_skyywardrobe_0.1.py). Build first:
    python SkyyWardrobe/build_skyywardrobe_0.2.py
    python SkyyWardrobe/test_skyywardrobe_0.2.py [--jar <SkyyWardrobe-0.2.jar>] [--old <SkyyWardrobe-0.1.jar>] [--dir <scratch>]
                                                 [--live <world mods folder>] [--gear <SkyyGear jar>] [--seed N] [--keep]

Parent (plain Python, read only): J the jar (manifest, exactly the expected classes, no asset / .ui / lang file).
Children (fresh JVMs, the game's own JRE, -Xverify:all, -XX:-UsePerfData, java.io.tmpdir in scratch; HytaleServer.jar on the class path):
  F   stand-ins compiled with javassist (FakePr, MapStore, TestPage, FlakyBox, TestPM, TestAssets, LookupIn, BadAccess)
  M01 the 0.1 JAR (SkyyWardrobe-0.1.jar, the SET pin) in its own JVM makes REAL 0.1 files as migration fixtures: stored loadouts + the
      equipped one + an orphan; a crashed equip (a pending 0.1 journal) with the live inventory at the crash; + a scratch COPY of the real
      live 0.1 file (read only)
  X   EVERY NEW CODE PATH on REAL engine containers (SimpleItemContainer, ItemStack with metadata, the real ItemStack.CODEC, a REAL Item
      asset map: Item objects with real ItemArmor slots / ItemWeapon / ItemTool / consumable / max stack / ItemStackContainerConfig, so
      the classifier runs the engine's own getters) with the REAL component lookups (EntityModule / DamageModule / Universe /
      TimeResource primed by reflection) and the real Store.isInThread (its thread field): config (0.1 rows kept, new rows' defaults,
      every check hook), the classifier (P2), the stamp (P1 engine side: withMetadata / withDurability / the codec keep it), deposit /
      Deposit all / caps / refusals, picks, EQUIP (pool trips, the shared item in two loadouts, Keep / Empty, spills, not-with-you,
      kinds, pocket blocks through a fake SkyySacks incl. give-back, keep ids), Take out / fetch / Forget / gone, Use what I wear,
      Returned items, the gate, save / put / rollback failures, CRASH AT EVERY STEP of every transaction (each move, mid-save after every
      file, after the save) with the live inventory as it was AND rolled back to before, chained changes, a random-operation FUZZ with
      the invariant "every item exists exactly once" (live + pool) after every op and every crash, profile switches, the 0.1 MIGRATION
      (fixtures from M01: pending journal repaired first, refused stacks -> Returned items, the equipped loadout asked once, run once, the
      0.1 file untouched, History snapshot = its bytes, a crash in the middle of the first save), unreadable / newer files (shut, never
      written), shard boundaries, the page (every view + click), the commands, every bridge fn (+ off-thread null), the join task,
      the timer, quit, auto-store, and the stamp through SkyyGear's own GearData.put (the SkyyGear jar in the same JVM)
  P   /requip (aliases) + 3 variants = hytale:Adventurer; /requipadmin + 3 variants require skyywardrobe.admin, empty groups (no leak)
  B   BYTECODE: setup() order; every set / remove overload; no ItemGridSlot; the journal before the first move; SkyyGear's GearView.apply /
      GearData.put only write metadata with withMetadata(key, value) (the stamp survives reforge / level-up / identify - spec F2)
  AA  THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every class; every engine member referenced must be accessible)
  D   START TWICE on a scratch COPY of the live world mods folder (writes nothing), then the live 0.1 file migrates on that COPY
  C   CLASS COMPARE old (0.1) vs new (0.2): kept / added / removed classes and the public members of the kept ones
Scratch: tools/dev/scratch/requip02/test (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, time, re, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import skyyui as SUI   # 0.2.6: the menu pattern checks (kit 1.7)

VERSION = "0.2.11"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


def newest_gear_jar():
    best = None
    for n in os.listdir(os.path.join(ROOT, "SkyyGear")):
        m = re.fullmatch(r"SkyyGear-([0-9.]+)\.jar", n)
        if m:
            v = tuple(int(x) for x in m.group(1).split("."))
            if best is None or v > best[0]:
                best = (v, os.path.join(ROOT, "SkyyGear", n))
    return best[1] if best else ""


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyWardrobe-%s.jar" % VERSION)))
OLD = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyWardrobe-0.1.jar")))
PREV = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyWardrobe-0.2.jar")))   # 0.2.1: the Y5 lock control (the 0.2 class lock)
BASE = os.path.abspath(arg("--base", os.path.join(HERE, "SkyyWardrobe-0.2.10.jar")))  # 0.2.11: the class compare (the SET pin)
BASE023 = os.path.abspath(os.path.join(HERE, "SkyyWardrobe-0.2.3.jar"))  # 0.2.4's W16 rollback + V15 fixtures (written by the 0.2.3 jar)
GEAR = arg("--gear", newest_gear_jar())
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "ward011", "w0211")))
SEED = int(arg("--seed", "20261010"))
# X13 fuzz seeds run after the --seed one (requip021: 4242 = the phantom NOT WITH YOU case + 20 more; --fuzz-seeds a,b,c overrides)
FUZZ_SEEDS = [int(x) for x in arg("--fuzz-seeds", "4242,1,2,3,7,11,14,42,99,123,256,777,1001,2026,3141,5150,8080,9001,12345,31337,65535").split(",") if x.strip()]
# requip021fix: COLLIDING-KIND fuzz seeds (the pool = 3 kinds with the SAME metadata: Iron legs / Iron head / Iron sword; 8030 = the stamp lost
# by a failed-save "Use what I wear" put-back). requip022: the critic's full set by default - 7000-7029 @ 260 ops + 8000-8069 @ 400 ops
# (8030 first). --collide-seeds a,b@n,c overrides ("seed@ops"; a bare seed runs --collide-ops, default 400; "-" = none)
COLLIDE_DEFAULT = ",".join(["8030@400"] + ["%d@260" % s_ for s_ in range(7000, 7030)] + ["%d@400" % s_ for s_ in range(8000, 8070) if s_ != 8030])


def _collide(spec):
    out_ = []
    for x in spec.split(","):
        x = x.strip()
        if not x or x == "-":
            continue
        s_, _a, n_ = x.partition("@")
        out_.append((int(s_), int(n_) if n_ else int(arg("--collide-ops", "400"))))
    return out_


COLLIDE_SEEDS = _collide(arg("--collide-seeds", COLLIDE_DEFAULT))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyyrqtest"
MAPSTORE = "com.hypixel.hytale.component.SkyyRqTestStore"
TESTPM = "com.hypixel.hytale.server.core.entity.entities.player.pages.SkyyRqTestPM"
PKG = "com.skyy.wardrobe."
NODE = "skyywardrobe.admin"
OURS = ["WdLog", "WdApi", "WdInvApi", "WdEng", "WdCfg", "WdCodec", "WdClass", "WdInv", "Wd01Load", "Wd01Data", "Wd01", "WdEntry", "WdLoad",
        "WdData", "WdStore", "WdJournal", "WdSlots", "WdBridge", "WdMove", "WdTx", "WdGate", "WdAuto", "WdMig", "WdOps", "WdSort", "WdPage",
        "WdRepairTask", "WdHop", "WdOpenTask", "WdFloorTask", "WdAutoTask", "WdFn", "WdTimer", "WdReady", "WdQuit", "WdCmds", "WdScan",
        "WdThreads",   # 0.2.1 fixer: the private join pre-warm reader's thread factory
        "WdHubOpen", "HubBar",   # 0.2.6: the Storage > Requip hub tab (kit 1.7)
        "WdSalv",   # 0.2.7: the Requip SALVAGE button
        "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd", "WdCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd", "WdAdminCmd", "SkyyWardrobePlugin"]
KITC = ["CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"]
CLASSES = sorted(PKG + c for c in OURS + KITC)
FAILS, OKS = [], [0]

# the test items: id -> (kind, armor slot / max stack / container capacity)
ITEMS = {
    "Armor_Iron_Head": ("armor", 0), "Armor_Iron_Chest": ("armor", 1), "Armor_Iron_Hands": ("armor", 2), "Armor_Iron_Legs": ("armor", 3),
    "Armor_Copper_Head": ("armor", 0), "Armor_Copper_Chest": ("armor", 1), "Armor_Copper_Hands": ("armor", 2), "Armor_Copper_Legs": ("armor", 3),
    "Armor_Gold_Head": ("armor", 0),
    "Weapon_Sword_Iron": ("weapon", 1), "Weapon_Sword_Mithril": ("weapon", 1), "Weapon_Bow_Wood": ("weapon", 1), "Weapon_Kunai_Test": ("plain", 1),
    "Tool_Pickaxe_Iron": ("tool", 1), "Tool_Hatchet_Iron": ("tool", 1), "Skyy_Spear_Test": ("weapon", 1),   # 0.2.2: a mod weapon, no Weapon_ prefix
    "Potion_Health": ("consumable", 25), "Food_Bread": ("consumable", 25),
    "Rock_Stone": ("plain", 100), "Wood_Oak_Log": ("plain", 100), "Ingredient_Bar_Iron": ("plain", 100),
    "Backpack_Test": ("container", 9), "Skyy_Sack_Mining_Normal": ("plain", 1), "Skyy_Menu": ("plain", 1), "Skyy_Vault_Prev": ("plain", 1),
    "Skyy_Unid_Bag_Rare": ("plain", 1), "Skyy_Talisman_Speed": ("plain", 1),
    # 0.2.3: the pet slot icon, the rune shard (an ability without its own rune) and four rune items (abilPanel's icons)
    "Farming_Collar": ("plain", 1), "Ingredient_Rune_Shard": ("plain", 100), "Rune_Breach": ("plain", 1), "Rune_Imbue": ("plain", 1),
    "Rune_Sunder": ("plain", 1), "Rune_Rift": ("plain", 1),
    # 0.2.4: the Lattice's modifier icons the V section shows (SkyyTrees' MOD_ICON)
    "Rock_Gem_Ruby": ("plain", 25), "Rock_Gem_Topaz": ("plain", 25), "Rock_Gem_Sapphire": ("plain", 25), "Rock_Gem_Zephyr": ("plain", 25),
    "Potion_Mana": ("consumable", 25), "Ingredient_Feathers_Blue": ("plain", 25), "Deco_Scroll": ("plain", 1),
    # 0.2.8: SkyyCooking's Potion Flask + Food Pouch (MaxStack 1, usable - without the built-in keep they would be Items) + a look-alike
    "Skyy_Flask_Empty": ("consumable", 1), "Skyy_Flask_V_Potion_Health": ("consumable", 1), "Skyy_Food_Pouch_Empty": ("consumable", 1),
    "Skyy_Food_Pouch_V_Food_Bread": ("consumable", 1), "Skyy_FlaskLike_Test": ("consumable", 1),
    # 0.2.4 T: the lifelong kinds as the game defines them (the hoe has no Tool / Weapon block - it tills through Interactions)
    "Tool_Pickaxe_Crude": ("tool", 1), "Tool_Pickaxe_Copper": ("tool", 1), "Tool_Hatchet_Crude": ("tool", 1), "Tool_Hatchet_Copper": ("tool", 1), "Tool_Hoe_Crude": ("plain", 1),
    "Tool_Hoe_Copper": ("plain", 1), "Tool_Hoe_Iron": ("plain", 1), "Tool_Hoe_Thorium": ("plain", 1), "Tool_Sickle_Crude": ("weapon", 1),
    "SkyyFishing_Rod_Bamboo": ("plain", 1), "Tool_Watering_Can": ("plain", 1),
}
# 0.2.10 PI: SkyyPets 0.4.4's pet kinds (read only from its build script) + their portrait items Skyy_PetIcon_<Kind>, all but Gecko
# (= a kind whose portrait the loaded SkyyPets lacks); KIND_NAMES = SkyyPets' display names that are not the split kind id
_PSRC = open(os.path.join(ROOT, "SkyyPets", "build_skyypets_0.4.4.py"), encoding="utf-8").read()
PET_KINDS = re.findall(r'^\s+\("([A-Za-z]+)", "(?:Farming|Mining|Foraging|Combat|Exploration)", "(?:Common|Uncommon|Rare|Epic|Legendary|Mythic)",', _PSRC, re.M)
PET_NAMES = __import__("ast").literal_eval(re.search(r"^KIND_NAMES = (\{.*\})$", _PSRC, re.M).group(1))
del _PSRC
assert len(PET_KINDS) >= 31 and len(set(PET_KINDS)) == len(PET_KINDS) and {"Rabbit", "Wolf", "Bear", "Skeleton", "CrystalGolem", "Gecko"} <= set(PET_KINDS), PET_KINDS
PET_NOICON = "Gecko"
ITEMS.update(("Skyy_PetIcon_" + k_, ("plain", 1)) for k_ in PET_KINDS if k_ != PET_NOICON)
# 0.2.11 RQ: SkyyPets 0.4.11's dragon portraits (kinds DragonPlain / DragonTundra, shown "Plain Dragon" / "Tundra Dragon")
ITEMS.update({"Skyy_PetIcon_DragonPlain": ("plain", 1), "Skyy_PetIcon_DragonTundra": ("plain", 1)})
assert "Dog" in PET_KINDS


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].split("#")[0].strip().strip('"')   # 0.2.2: the WORLD line may carry a comment
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "mods")))


def tree_hash(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


# ====================================================================================================== children: shared
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def run_mkfake(out_dir):
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG

    def mk(name, sup=None):
        c = cp.makeClass(P + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = cp.makeClass(MAPSTORE)      # in the engine's package: Store's constructor is package-private
    ms.setSuperclass(cp.get(CR + "Store"))
    for d in ("java.util.Map comps", "java.lang.Object res", "java.lang.Object ext"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null || this.comps == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
    M(ms, "public com.hypixel.hytale.component.Resource getResource(com.hypixel.hytale.component.ResourceType t) { return (com.hypixel.hytale.component.Resource) this.res; }")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    for d in ("java.util.List msgs", "java.util.UUID fu", "String fname", "com.hypixel.hytale.component.Ref fref", "java.util.UUID fworld"):
        F(fp, "public %s;" % d)
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public java.util.UUID getUuid() { return this.fu; }")
    M(fp, "public String getUsername() { return this.fname; }")
    M(fp, "public com.hypixel.hytale.component.Ref getReference() { return this.fref; }")
    M(fp, "public java.util.UUID getWorldUuid() { return this.fworld; }")
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs == null) this.msgs = new java.util.ArrayList(); this.msgs.add(m == null ? \"null\" : m.getRawText()); }")
    fp.writeFile(out_dir)
    tp = mk("TestPage", PKG + "WdPage")
    F(tp, "public int rebuilds;")
    F(tp, "public int closes;")
    tp.addConstructor(CtNewConstructor.make("public TestPage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", tp))
    M(tp, "public void rebuild() { this.rebuilds = this.rebuilds + 1; }")
    M(tp, "public void close() { this.closes = this.closes + 1; }")
    tp.writeFile(out_dir)
    IS, ISST = "com.hypixel.hytale.server.core.inventory.ItemStack", "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
    fb = mk("FlakyBox", "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    F(fb, "public static int FAIL_AT = -1;")
    F(fb, "public static boolean FAIL_ALL = false;")
    F(fb, "public static boolean STICKY = false;")
    F(fb, "public static int SETS = 0;")
    fb.addConstructor(CtNewConstructor.make("public FlakyBox(short n) { super(n); }", fb))
    M(fb, ("public %s setItemStackForSlot(short s, %s i, boolean f) { SETS = SETS + 1; if (FAIL_ALL) return null; "
           "if (FAIL_AT == 0) { FAIL_AT = -1; if (STICKY) FAIL_ALL = true; return null; } if (FAIL_AT > 0) FAIL_AT = FAIL_AT - 1; "
           "return super.setItemStackForSlot(s, i, f); }") % (ISST, IS))
    fb.writeFile(out_dir)
    PP = "com.hypixel.hytale.server.core.entity.entities.player.pages."
    pm = cp.makeClass(TESTPM)
    pm.setSuperclass(cp.get(PP + "PageManager"))
    F(pm, "public static java.lang.Object CUR = null;")
    F(pm, "public static int OPENS = 0;")
    pm.addConstructor(CtNewConstructor.make("public TestPM() { super(); }", pm))
    M(pm, "public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, %sCustomUIPage p) { CUR = p; OPENS = OPENS + 1; }" % PP)
    M(pm, "public %sCustomUIPage getCustomPage() { return (%sCustomUIPage) CUR; }" % (PP, PP))
    pm.writeFile(out_dir)
    ta = mk("TestAssets", "com.hypixel.hytale.assetstore.AssetStore")
    ta.addConstructor(CtNewConstructor.make("public TestAssets() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", ta))
    ta.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== the engine stand-in
class Eng(object):
    """Unsafe-allocated engine singletons, primed so the REAL getComponentType() / getResourceType() lookups answer."""

    def __init__(self):
        from jpype import JClass
        self.J = JClass
        uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        self.U = uf.get(None)
        self.CP = JClass("javassist.ClassPool")(False)
        self.CP.appendSystemPath()
        self.CP.appendClassPath(B.SERVER_JAR)
        self.IP = JClass("javassist.bytecode.InstructionPrinter")

    def jf(self, c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)

    def code(self, cls, meth):
        cc = self.CP.get(cls)
        m = [x for x in cc.getDeclaredMethods() if str(x.getName()) == meth][0]
        ca = m.getMethodInfo().getCodeAttribute()
        it, cp, out = ca.iterator(), m.getMethodInfo().getConstPool(), []
        while it.hasNext():
            out.append(str(self.IP.instructionString(it, it.next(), cp)))
        return out

    def field_of(self, cls, getter):
        for l in self.code(cls, getter):
            m = re.search(r"(getfield|getstatic) #\d+ = Field ([\w.$]+)\.(\w+)\(", l)
            if m:
                return m.group(2), m.group(3)
        raise KeyError("%s.%s" % (cls, getter))

    def singleton(self, cls):
        c2, f = self.field_of(cls, "get")
        K = self.J(c2)
        fld = self.jf(K, f)
        o = fld.get(None)
        if o is None:
            o = self.U.allocateInstance(K.class_)
            fld.set(None, o)
        return o

    def prime(self, cls, getter, value):
        lines = self.code(cls, getter)
        mod = None
        for l in lines:
            m = re.search(r"invokestatic #\d+ = Method ([\w.$]+)\.get\(\(\)", l)
            if m:
                mod = m.group(1)
            m2 = re.search(r"invokevirtual #\d+ = Method ([\w.$]+)\.(\w+)\(\(\)", l)
            if m2 and mod:
                inst = self.singleton(mod)
                c2, f = self.field_of(m2.group(1), m2.group(2))
                self.jf(self.J(c2), f).set(inst, value)
                return value
        raise KeyError("%s.%s" % (cls, getter))


def item_map(E):
    """a REAL item asset map: Item objects whose real getters answer (armor slot, weapon, tool, consumable, max stack, container)"""
    J = E.J
    AS = J("com.hypixel.hytale.assetstore.AssetStore")
    st0 = E.U.allocateInstance(J(FAKE_PKG + ".TestAssets").class_)
    am = J("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()
    E.jf(AS, "assetMap").set(st0, am)
    I = J("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    E.jf(I, "ASSET_STORE").set(None, st0)
    inner = E.jf(J("com.hypixel.hytale.assetstore.map.DefaultAssetMap"), "assetMap").get(am)
    Slot = J("com.hypixel.hytale.protocol.ItemArmorSlot")
    IA = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor")
    IW = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon")
    IT = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemTool")
    CC = J("com.hypixel.hytale.server.core.asset.type.item.config.ItemStackContainerConfig")
    from jpype import JShort
    for iid, (kind, n) in ITEMS.items():
        it = I(iid)
        E.jf(I, "maxStack").setInt(it, n if kind in ("consumable", "plain", "container") and n > 1 else 1)
        if kind == "armor":
            a = E.U.allocateInstance(IA.class_)
            E.jf(IA, "armorSlot").set(a, Slot.values()[n])
            E.jf(I, "armor").set(it, a)
        elif kind == "weapon":
            E.jf(I, "weapon").set(it, E.U.allocateInstance(IW.class_))
        elif kind == "tool":
            E.jf(I, "tool").set(it, E.U.allocateInstance(IT.class_))
        elif kind == "consumable":
            E.jf(I, "consumable").setBoolean(it, True)
        elif kind == "container":
            c = CC()
            E.jf(CC, "capacity").setShort(c, JShort(n))
            E.jf(I, "itemStackContainerConfig").set(it, c)
        inner.put(iid, it)
    return am


def boot(K, scratch_mods, pkg=PKG):
    """the bare engine + the mod's statics pointed at a scratch mods folder; returns a dict of handles"""
    from jpype import JClass, JArray, JString
    E = Eng()
    U = E.U
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    item_map(E)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    E.jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    E.jf(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap, wbu = CHM(), CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", wbu),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        E.jf(UNI, n).set(uni, v)
    E.jf(UNI, "instance").set(None, uni)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    types = {}
    for key, cls, getter in (("pr", "com.hypixel.hytale.server.core.universe.PlayerRef", "getComponentType"),
                             ("pla", "com.hypixel.hytale.server.core.entity.entities.Player", "getComponentType"),
                             ("arm", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor", "getComponentType"),
                             ("hot", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar", "getComponentType"),
                             ("sto", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage", "getComponentType"),
                             ("bak", "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack", "getComponentType"),
                             ("death", "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getComponentType"),
                             ("ddc", "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", "getComponentType")):
        if key == "pr":
            types[key] = CT()
            E.jf(UNI, "playerRefComponentType").set(uni, types[key])
            continue
        types[key] = E.prime(cls, getter, CT())
    RT = JClass("com.hypixel.hytale.component.ResourceType")
    types["time"] = E.prime("com.hypixel.hytale.server.core.modules.time.TimeResource", "getResourceType", RT())
    World = JClass("com.hypixel.hytale.server.core.universe.world.World")
    world = U.allocateInstance(World.class_)
    Q = JClass("java.util.concurrent.LinkedBlockingDeque")()
    E.jf(World, "acceptingTasks").set(world, JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    E.jf(World, "taskQueue").set(world, Q)
    E.jf(World, "name").set(world, "requiptest")
    UUID = JClass("java.util.UUID")
    WU = UUID.fromString("00000000-0000-0000-0000-0000000000d1")
    wbu.put(WU, world)
    wmap.put("requiptest", world)
    br = CHM()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    P = lambda n: JClass(pkg + n)
    lines = JClass("java.util.ArrayList")()
    P("WdLog").LINES = lines
    Paths = JClass("java.nio.file.Paths")
    P("WdCfg").load(Paths.get(scratch_mods))
    root = Paths.get(scratch_mods).resolve("Skyy_SkyyWardrobe")
    P("WdStore").ROOT = root
    if pkg == PKG and hasattr(P("WdStore"), "RQ"):
        P("WdStore").DIR01 = root.resolve("loadouts")
        P("WdStore").RQ = root.resolve("requip")
        P("WdStore").LOGF = root.resolve("requip.log")
    else:
        P("WdStore").DIR = root.resolve("loadouts")
        P("WdStore").LOGF = root.resolve("wardrobe.log")
    return {"E": E, "U": U, "uni": uni, "pbu": pbu, "types": types, "world": world, "Q": Q, "WU": WU, "br": br, "lines": lines}


def drain(H):
    n = 0
    while not H["Q"].isEmpty():
        t = H["Q"].poll()
        t.run()
        n += 1
    return n


class World(object):
    """test players on REAL engine containers inside real InventoryComponents in a MapStore (whose Store.thread = this thread)"""

    def __init__(self, H):
        from jpype import JClass, JShort, JByte
        self.H, self.E, self.U, self.types = H, H["E"], H["U"], H["types"]
        self.J = JClass
        self.JShort, self.JByte = JShort, JByte
        self.UUID = JClass("java.util.UUID")
        self.IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
        self.BD = JClass("org.bson.BsonDocument")
        self.SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
        self.Flaky = JClass(FAKE_PKG + ".FlakyBox")
        self.MapStore, self.FakePr = JClass(MAPSTORE), JClass(FAKE_PKG + ".FakePr")
        self.IdM = JClass("java.util.IdentityHashMap")
        INV = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
        self.Arm, self.Hot, self.Sto, self.Bak = JClass(INV + "Armor"), JClass(INV + "Hotbar"), JClass(INV + "Storage"), JClass(INV + "Backpack")
        self.RefC = JClass("com.hypixel.hytale.component.Ref")
        self.Player = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
        self.TestPM = JClass(TESTPM)
        self.TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
        self.Inst = JClass("java.time.Instant")
        self.Thread = JClass("java.lang.Thread")
        self.hotreg = {}

    def stack(self, i, q=1, meta=None):
        return self.IS(i, q, 100.0, 100.0, 0, self.BD.parse(meta) if meta else None)

    def player(self, uid, name, flaky=False, bak=9):
        W = self
        S = self.JShort

        class P_(object):
            pass
        p = P_()
        p.u = W.UUID.fromString(uid)
        p.name = name
        p.arm = W.Flaky(S(4)) if flaky else W.SIC(S(4))
        p.hot, p.sto, p.bak = W.SIC(S(9)), W.SIC(S(36)), W.SIC(S(bak))
        p.st = W.MapStore()
        p.st.comps = W.IdM()
        W.E.jf(W.J("com.hypixel.hytale.component.Store"), "thread").set(p.st, W.Thread.currentThread())
        p.ref = W.U.allocateInstance(W.RefC.class_)
        W.E.jf(W.RefC, "store").set(p.ref, p.st)
        p.pr = W.FakePr()
        p.pr.fu, p.pr.fname, p.pr.fref, p.pr.fworld = p.u, name, p.ref, W.H["WU"]
        p.pla = W.U.allocateInstance(W.Player.class_)
        W.E.jf(W.Player, "pageManager").set(p.pla, W.TestPM())
        m = W.IdM()
        m.put(W.types["pr"], p.pr)
        m.put(W.types["pla"], p.pla)
        m.put(W.types["arm"], W.Arm(p.arm))
        m.put(W.types["hot"], W.Hot(p.hot, W.JByte(0)))
        m.put(W.types["sto"], W.Sto(p.sto))
        m.put(W.types["bak"], W.Bak(p.bak))
        p.st.comps.put(p.ref, m)
        tr = W.U.allocateInstance(W.TR.class_)
        W.E.jf(W.TR, "now").set(tr, W.Inst.now())
        p.st.res = tr
        W.H["pbu"].put(p.u, p.pr)
        p.secs = [p.arm, p.hot, p.sto, p.bak]
        W.hotreg[str(p.u)] = p.hot
        return p

    def setc(self, c, i, s):
        c.setItemStackForSlot(self.JShort(i), s, False)

    def getc(self, c, i):
        s = c.getItemStack(self.JShort(i))
        return None if s is None or s.isEmpty() else s

    def snap(self, p):
        """the live inventory as it is (the engine's last save)"""
        out = []
        for c in p.secs:
            out.append([c.getItemStack(self.JShort(i)) for i in range(int(c.getCapacity()))])
        return out

    def restore(self, p, sn):
        for c, sl in zip(p.secs, sn):
            for i, s in enumerate(sl):
                if s is None or s.isEmpty():
                    c.removeItemStackFromSlot(self.JShort(i), False)
                else:
                    c.setItemStackForSlot(self.JShort(i), s, False)

    def clear(self, p):
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                c.removeItemStackFromSlot(self.JShort(i), False)

    def dump(self, p, Codec):
        out = []
        for c in p.secs:
            sec = []
            for i in range(int(c.getCapacity())):
                s = c.getItemStack(self.JShort(i))
                sec.append(None if s is None or s.isEmpty() else json.loads(str(Codec.toJson(Codec.slotDoc(i, s)))))
            out.append(sec)
        return out

    def load(self, p, dumpd, Codec):
        self.clear(p)
        for c, sec in zip(p.secs, dumpd):
            for i, sd in enumerate(sec):
                if sd is not None:
                    c.setItemStackForSlot(self.JShort(i), Codec.stackOf(self.BD.parse(json.dumps(sd))), False)


SUIC = {"Normal": "#FFFFFF", "Rare": "#FF55FF", "Legendary": "#55FFFF", "gold": "#E8A93B"}   # 0.2.2: skyyui RARITY + COLOR gold (row name colours)
GEARDOC = '{"SkyyGear": {"v": 1, "r": "%s", "lvl": %d, "id": true}}'


def gdoc(r, lv):
    return GEARDOC % (r, lv)


def fake_bridges(br, state):
    """SkyyPets / SkyyClasses / SkyySkills / SkyyProfiles / SkyySacks stand-ins (state = a dict the test changes)"""
    from jpype import JImplements, JOverride, JArray, JObject, JInt, JLong

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    calls = state.setdefault("calls", {"pets": [], "abil": [], "take": [], "put": [], "commit": [], "deposit": []})

    def pets_set(a):
        calls["pets"].append((str(a[0]), str(a[1]), str(a[2])))
        state["pets"] = str(a[1]) + "|" + str(a[2])
        return "+Pets set."

    def abil_set(a):
        calls["abil"].append(str(a[1]))
        state["abil"] = str(a[1])
        return "+Abilities set."

    def bag(a):
        return state.setdefault("bags", {}).setdefault(str(a[0]), {})

    def take(a):
        b, q = bag(a), int(a[2])
        have = b.get(str(a[1]), 0)
        g = min(have, q)
        b[str(a[1])] = have - g
        calls["take"].append((str(a[1]), g))
        return JLong(g)

    def put(a):
        b = bag(a)
        b[str(a[1])] = b.get(str(a[1]), 0) + int(a[2])
        calls["put"].append((str(a[1]), int(a[2])))
        return JLong(int(a[2]))

    def commit(a):
        calls["commit"].append((str(a[1]), int(a[2])))
        return JLong(int(a[2]))

    def deposit(a):
        """the REAL SkyySacks 0.7.17 contract: {UUID, id, Long n, Integer hotbar slot}; the 3-argument form is refused (0); takes up to n
        of the plain stack IN THAT HOTBAR SLOT (read from the slot itself), what does not fit stays there"""
        from jpype import JShort
        if len(a) < 4 or a[3] is None:
            calls.setdefault("deposit3", []).append(str(a[1]))
            return JLong(0)
        hb = state.get("hotreg", {}).get(str(a[0]))
        slot = int(a[3])
        if hb is None:
            return JLong(0)
        s = hb.getItemStack(JShort(slot))
        if s is None or s.isEmpty() or str(s.getItemId()) != str(a[1]) or (s.getMetadata() is not None and not s.getMetadata().isEmpty()):
            return JLong(0)
        b, q = bag(a), int(a[2])
        acc = min(q, int(s.getQuantity()), state.get("bagRoom", 10 ** 9))
        if acc <= 0:
            return JLong(0)
        if acc == int(s.getQuantity()):
            hb.removeItemStackFromSlot(JShort(slot), False)
        else:
            hb.setItemStackForSlot(JShort(slot), s.withQuantity(int(s.getQuantity()) - acc), False)
        b[str(a[1])] = b.get(str(a[1]), 0) + acc
        calls["deposit"].append((str(a[1]), acc, slot))
        return JLong(acc)

    def count(a):
        return JLong(bag(a).get(str(a[1]), 0))

    def all_(u):
        """sacks:fn:all UUID -> HashMap id -> Long (SkyySacks 0.7.16+)"""
        from jpype import JClass
        m = JClass("java.util.HashMap")()
        for k_, v_ in state.setdefault("bags", {}).get(str(u), {}).items():
            m.put(k_, JLong(v_))
        return m
    fns = {"pets:fn:loadoutGet": lambda u: state.get("pets", "pA|sA"), "pets:fn:loadoutSet": pets_set,
           "pets:fn:petName": lambda a: ("Pet-" + str(a[1])) if state.get("owned") is None else state["owned"].get(str(a[1])), "class:fn:loadoutGet": lambda u: state.get("abil", "v=1;class=Mage;p1=Meteor;n1=Meteor"),
           "class:fn:loadoutSet": abil_set, "profile:fn:key": lambda u: state.get("key", {}).get(str(u), str(u)),
           "skill:fn:overall": lambda u: JArray(JObject)([JInt(state.get("overall", 0)), JInt(0)]),
           "sacks:fn:take": take, "sacks:fn:put": put, "sacks:fn:commit": commit, "sacks:fn:deposit": deposit, "sacks:fn:count": count, "sacks:fn:all": all_}
    objs = {}
    for k, f in fns.items():
        objs[k] = Fn(f)
        br.put(k, objs[k])
    return objs


# ====================================================================================================== child M01: REAL 0.1 files
def run_mk01(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, OLD, FAKE_DIR])
    fx = os.path.join(SCRATCH, "fx01")
    mods = os.path.join(fx, "mods")
    shutil.rmtree(fx, ignore_errors=True)
    os.makedirs(mods)
    H = boot(K, mods)
    W = World(H)
    P = lambda n: JClass(PKG + n)
    Codec, Ops, Tx, Gate, Store, Jr = P("WdCodec"), P("WdOps"), P("WdTx"), P("WdGate"), P("WdStore"), P("WdJournal")
    state = {"pets": "petA|sumA", "abil": "v=1;class=Priest;p1=SacredHeal;n1=Sacred Heal"}
    fake_bridges(H["br"], state)
    meta = {}
    # ---- A: loadout 1 stores a full set (+ potion, a block, a bag, a bow orphan), loadout 2 is EQUIPPED (its gear is on the player)
    A = W.player("00000000-0000-0000-0000-0000000001a1", "Ann")
    for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
        W.setc(A.arm, i, W.stack(a, 1, gdoc("rare", 12 + i)))
    W.setc(A.hot, 0, W.stack("Weapon_Sword_Iron", 1, gdoc("legendary", 20)))
    W.setc(A.hot, 1, W.stack("Potion_Health", 5))
    W.setc(A.hot, 2, W.stack("Rock_Stone", 64))
    W.setc(A.hot, 3, W.stack("Backpack_Test", 1))
    W.setc(A.hot, 4, W.stack("Armor_Gold_Head", 1))          # armor in a hotbar slot (0.1 allowed it)
    W.setc(A.hot, 8, W.stack("Skyy_Menu", 1))
    r1 = str(Ops.run(A.pr, A.ref, A.st, 2, 0, None))
    Gate.LAST.clear()
    r2 = str(Ops.run(A.pr, A.ref, A.st, 4, 0, "Combat"))
    r3 = str(Ops.run(A.pr, A.ref, A.st, 1, 1, None))          # equip the EMPTY loadout 2: the gear goes home into loadout 1
    Gate.LAST.clear()
    W.setc(A.arm, 0, W.stack("Armor_Copper_Head", 1, gdoc("unique", 5)))
    W.setc(A.arm, 1, W.stack("Armor_Copper_Chest", 1))
    W.setc(A.hot, 0, W.stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 3)))
    state["pets"] = "petB|"
    r4 = str(Ops.run(A.pr, A.ref, A.st, 2, 1, None))          # save current 2 (the equipped one: pets + abilities only)
    d = Store.get(str(A.u), A.u)
    d.orphan("loadout0:hotbar:6:test", W.stack("Weapon_Bow_Wood", 1, gdoc("rare", 7)))
    d.rev = d.rev + 1
    Store.save(d)
    K.check(r1.startswith("+Saved") and r3.startswith("+Equipped Loadout 2") and r4.startswith("+Saved") and d.worn == 1
            and d.slots[0].count() == 9 and d.orphans.size() == 1, "M01 A: loadout 1 stores 9 stacks + an orphan, loadout 2 is equipped (%s / %s / %s / %s)" % (r1, r2, r3, r4))
    meta["A"] = {"key": str(A.u), "live": W.dump(A, Codec)}
    # ---- B: loadout 1 stores gold head + a mithril sword; equipping it "crashes" after one move: a pending (moving) 0.1 journal
    Bo = W.player("00000000-0000-0000-0000-0000000001b2", "Bo")
    W.setc(Bo.arm, 0, W.stack("Armor_Gold_Head", 1, gdoc("fabled", 30)))
    W.setc(Bo.hot, 0, W.stack("Weapon_Sword_Mithril", 1, gdoc("mythic", 40)))
    W.setc(Bo.hot, 1, W.stack("Food_Bread", 7))
    Ops.run(Bo.pr, Bo.ref, Bo.st, 2, 0, None)
    Gate.LAST.clear()
    Ops.run(Bo.pr, Bo.ref, Bo.st, 1, 1, None)
    Gate.LAST.clear()
    W.setc(Bo.arm, 0, W.stack("Armor_Copper_Head", 1))
    W.setc(Bo.hot, 0, W.stack("Weapon_Bow_Wood", 1))
    Tx.CRASH_AT = 1
    crashed = False
    try:
        Ops.run(Bo.pr, Bo.ref, Bo.st, 1, 0, None)
    except Exception as e:
        crashed = "harness crash" in str(e)
    Tx.CRASH_AT = -1
    jf = os.path.join(mods, "Skyy_SkyyWardrobe", "loadouts", str(Bo.u) + ".journal.json")
    K.check(crashed and os.path.isfile(jf) and json.load(open(jf))["stage"] == "moving", "M01 B: a crashed 0.1 equip left a pending journal")
    meta["B"] = {"key": str(Bo.u), "live": W.dump(Bo, Codec)}
    json.dump(meta, open(os.path.join(fx, "meta.json"), "w"), indent=1)
    K.save()


# ====================================================================================================== child X
def run_x(out):
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JString, JInt, JShort, JLong, JByte
    K = Child(out)
    cp = [B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR] + ([GEAR] if GEAR and os.path.isfile(GEAR) else [])
    _jvm(cp)
    mods = os.path.join(SCRATCH, "x-mods")
    shutil.rmtree(mods, ignore_errors=True)
    os.makedirs(mods)
    H = boot(K, mods)
    W = World(H)
    E, U, types, br = H["E"], H["U"], H["types"], H["br"]
    P = lambda n: JClass(PKG + n)
    Cfg, Store, Tx, Ops, Gate, Jr, Slots, Brg, Codec, Cls, Inv, Mig, Auto = (P("WdCfg"), P("WdStore"), P("WdTx"), P("WdOps"), P("WdGate"),
                                                                              P("WdJournal"), P("WdSlots"), P("WdBridge"), P("WdCodec"), P("WdClass"),
                                                                              P("WdInv"), P("WdMig"), P("WdAuto"))
    Paths = JClass("java.nio.file.Paths")
    Auto.load(Paths.get(mods).resolve("Skyy_SkyyWardrobe").resolve("requip").resolve("autostore.json"))
    state = {"hotreg": W.hotreg}
    fns = fake_bridges(br, state)
    stack, setc, getc = W.stack, W.setc, W.getc
    UUID_ = JClass("java.util.UUID")
    Wd = os.path.join(mods, "Skyy_SkyyWardrobe")

    def ein(e):
        return bool(getattr(e, "in_")) if hasattr(e, "in_") else bool(getattr(e, "in"))

    def jn(v):
        if isinstance(v, dict):
            for k_ in ("$numberInt", "$numberLong"):
                if k_ in v:
                    return int(v[k_])
        return v

    def ukey(s):
        s2 = Codec.unstamp(s)
        md = s2.getMetadata()
        return (str(s2.getItemId()), "" if md is None or md.isEmpty() else str(md.toJson()))

    def census(p, k=None):
        """every physical item once: live (stamp stripped) + the pool FILES (IN gear, kind counts) + Returned items"""
        k = k or str(Store.pkey(p.u))
        d = Store.load(k, str(p.u))
        tot = {}

        def add(s, q):
            kk = ukey(s)
            tot[kk] = tot.get(kk, 0) + q
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                s = c.getItemStack(JShort(i))
                if s is not None and not s.isEmpty():
                    add(s, int(s.getQuantity()))
        for e in d.entries.values():
            if e.kind and e.stack is not None:
                add(e.stack, int(e.count))
            elif ein(e) and e.stack is not None:
                add(e.stack, int(e.stack.getQuantity()))
        for o in d.orphans:
            s = Codec.stackOf(o.asDocument())
            if s is not None:
                add(s, int(s.getQuantity()))
        return {kk: v for kk, v in tot.items() if v}, d

    def once(p, d=None, allow_out=()):
        """every gear entry exactly once: IN in the pool XOR its stamp in the live inventory; no live stamp the pool does not know"""
        if d is None:
            _c, d = census(p)
        live = {}
        for c in p.secs:
            for i in range(int(c.getCapacity())):
                e = Codec.stampOf(c.getItemStack(JShort(i)))
                if e is not None:
                    live[str(e)] = live.get(str(e), 0) + 1
        bad = []
        for e in d.entries.values():
            if e.kind:
                continue
            n = (1 if ein(e) else 0) + live.get(str(e.eid), 0)
            if n != 1 and not (n == 0 and str(e.eid) in allow_out):
                bad.append("%s %s in=%s live=%d" % (e.eid, e.itemId(), ein(e), live.get(str(e.eid), 0)))
        for k_ in live:
            if d.entry(k_) is None:
                bad.append("live stamp %s unknown to the pool" % k_)
            elif live[k_] > 1:
                bad.append("stamp %s on %d stacks" % (k_, live[k_]))
        return bad

    def run(p, op, n=0, a=None):
        return str(Ops.run(p.pr, p.ref, p.st, op, n, a))

    def gap():
        Gate.LAST.clear()

    def restart():
        """a server restart: memory gone (cache, pending journals, busy flags)"""
        Store.CACHE.clear()
        Jr.PENDING.clear(); Jr.KNOWN.clear(); Jr.GEN.clear(); Jr.PRE.clear()
        Gate.BUSY.clear()
        Tx.KEPT.clear()
        Auto.SEEN.clear()
        Sv_ = P("WdSalv")   # 0.2.7: the salvage memory (open journals, the keep window, the scanned folders)
        Sv_.TODO.clear(); Sv_.KEEP.clear(); Sv_.SCANNED.clear()

    def jresolved(k):
        """the journal is resolved: gone, or (fixer 2, data critic 2) a SAVED journal of older saved steps still inside the keep window"""
        f = os.path.join(Wd, "requip", k, "journal.json")
        if not os.path.isfile(f):
            return True
        j = json.load(open(f))
        return j.get("stage") == "saved" and bool(Jr.PENDING.containsKey(k)) and all(st_.get("savedAt") is not None for st_ in j.get("steps", []))

    def stamps_of(p):
        return [str(Codec.stampOf(c.getItemStack(JShort(i)))) for c in p.secs for i in range(int(c.getCapacity())) if Codec.stampOf(c.getItemStack(JShort(i))) is not None]

    def ent_by_id(d, iid):
        return [e for e in d.entries.values() if str(e.itemId()) == iid]

    try:
        # ============================================================ A: every class loads + verifies + initialises
        Cls_, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
        bad = []
        for cn in CLASSES:
            try:
                Cls_.forName(cn, True, loader)
            except Exception as e:
                bad.append("%s: %s" % (cn, e))
        K.check(not bad, "A. every class loads, verifies (-Xverify:all) and initialises: %s" % bad)

        # ============================================================ X1 config: 0.1 rows kept, new rows' defaults, checks, Server Setup
        cfgf = os.path.join(Wd, "config.properties")
        txt = open(cfgf).read()
        K.check("slots.free=10\n" + str(Cfg.MIG_MARK) + "\n" in txt and "space.armorCap=1000" in txt and "autoStore.enabled=true" in txt and "swap.strict=false" in txt, "X1 a fresh default config.properties holds the 0.1 rows and the new rows")
        K.check(int(Cfg.ARMOR_CAP) == 1000 and int(Cfg.ITEMS_CAP) == 1000 and int(Cfg.shard()) == 100 and not bool(Cfg.DEP_HOT) and bool(Cfg.POCKET)
                and int(Cfg.POCKET_N) == 0 and bool(Cfg.POCKET_BACK) and bool(Cfg.AUTO_ON) and int(Cfg.AUTO_S) == 2 and int(Cfg.FREE) == 10
                and str(Cfg.DENY_IDS) == "-" and str(Cfg.ALLOW_IDS) == "-", "X1 every new row reads its default")
        # the LIVE 0.1 file (no new keys): the new rows keep their defaults, the 0.1 values stay
        old01 = ("wardrobe.enabled=true\nslots.free=4\nslots.max=18\nslots.byLevel=6:10,10:20,14:30,18:40\nswap.hotbar=true\nswap.strict=false\n"
                 "swap.keepIds=Skyy_Menu,Skyy_Vault_*\nswap.gapSeconds=1\ncombatSeconds=10\nafterSwitchSeconds=30\njournalKeepSeconds=30\nnameMax=16\n")
        live_cfg = os.path.join(LIVE, "Skyy_SkyyWardrobe", "config.properties")
        if os.path.isfile(live_cfg) and "slots.free=4\n" in open(live_cfg, encoding="latin-1").read().replace("\r\n", "\n"):   # 0.2.5: only a 0.1-style live file
            old01 = open(live_cfg, encoding="latin-1").read()
        open(cfgf, "w", encoding="latin-1").write(old01)
        Cfg.reloadAll()
        K.check(int(Cfg.ARMOR_CAP) == 1000 and bool(Cfg.POCKET) and int(Cfg.FREE) == 4 and list(Cfg.keepList()) == ["Skyy_Menu", "Skyy_Vault_*"],
                "X1 a 0.1 config.properties (the live one): 0.1 values kept, new rows at their defaults, nothing rewritten")
        K.check(open(cfgf, encoding="latin-1").read() == old01, "X1 ... and the file is byte for byte the same")
        K.check(Cfg.checkIds("items.deny", "Foo_*,Bar") is None and Cfg.checkIds("items.deny", "*") is not None and Cfg.checkIds("items.allow", "a b") is not None,
                "X1 check= on items.deny / items.allow")
        P("CfgPub").start(Paths.get(mods), None)
        # ---- Z5 0.2.2: the one-time slots.free 4 -> 10 update of an existing config.properties (WdCfg.migFree, EXECUTED on the kit's file)
        MARK = str(Cfg.MIG_MARK)
        keep_cfg = open(cfgf, "rb").read()
        hist_d = os.path.join(Wd, "config-history")
        chg_f = os.path.join(Wd, "config-changes.log")

        def hist_has(b_):
            return os.path.isdir(hist_d) and any(open(os.path.join(hist_d, f_), "rb").read() == b_ for f_ in os.listdir(hist_d) if f_.endswith(".bak"))

        def chg_lines():
            return open(chg_f, encoding="utf-8").read().splitlines() if os.path.isfile(chg_f) else []

        def mig_on(b_):
            open(cfgf, "wb").write(b_)
            return str(Cfg.migFree(Paths.get(cfgf))), open(cfgf, "rb").read()

        A_ = b"# head\nwardrobe.enabled=true\nslots.free=4\nslots.max=18\n"
        n0 = len(chg_lines())
        rA, gotA = mig_on(A_)
        Cfg.reloadAll()
        cl = chg_lines()
        K.check(gotA == b"# head\nwardrobe.enabled=true\nslots.free=10\n" + MARK.encode("latin-1") + b"\nslots.max=18\n" and "slots.free 4 -> 10" in rA
                and hist_has(A_) and len(cl) == n0 + 1 and "\tslots.free\t4\t10\tok" in cl[-1] and "SkyyWardrobe 0.2.2" in cl[-1] and int(Cfg.FREE) == 10,
                "Z5 an untouched slots.free=4 -> 10: the marker under it, every other byte kept, the old bytes in config-history, one change-log "
                "line (Undo = 4), 10 free loadouts (%s / %r / %s)" % (rA, gotA, cl[-1:]))
        rA2 = str(Cfg.migFree(Paths.get(cfgf)))
        K.check(rA2 == "" and open(cfgf, "rb").read() == gotA and len(chg_lines()) == n0 + 1, "Z5 run once: the second start changes nothing (%s)" % rA2)
        B_ = b"a=1\r\nslots.free=6\r\nslots.max=18\r\n"
        rB, gotB = mig_on(B_)
        K.check(gotB == b"a=1\r\nslots.free=6\r\n" + MARK.encode("latin-1") + b"\r\nslots.max=18\r\n" and "kept" in rB and len(chg_lines()) == n0 + 1 and hist_has(B_),
                "Z5 a hand-edited slots.free=6 (a CRLF file) is KEPT (INFO), only the marker is added in CRLF, no change-log line (%s / %r)" % (rB, gotB))
        C_ = b"wardrobe.enabled=true\nslots.max=18\n"
        rC, gotC = mig_on(C_)
        K.check(gotC == C_ + b"slots.free=10\n" + MARK.encode("latin-1") + b"\n" and "line added" in rC and len(chg_lines()) == n0 + 2,
                "Z5 no slots.free line (it read the old default 4) -> slots.free=10 appended + marker (%s / %r)" % (rC, gotC))
        E_ = b"slots.free=\\\n  4\nslots.max=18\n"
        rE, gotE = mig_on(E_)
        K.check(gotE == b"slots.free=\\\n  4\n" + MARK.encode("latin-1") + b"\nslots.max=18\n" and "kept" in rE, "Z5 a continued (multi-line) value is an admin's: kept (%s / %r)" % (rE, gotE))
        K.check(Cfg.migPlan(str(Cfg.DEFAULT_TEXT)) is None and str(Cfg.DEFAULT_TEXT).count("slots.free=10\n" + MARK + "\n") == 1,
                "Z5 a fresh 0.2.2 file already carries the marker: nothing to do")
        open(cfgf, "wb").write(keep_cfg)
        Cfg.reloadAll()
        K.check(int(Cfg.FREE) == 4, "Z5 back to the 0.1-style file for the 0.2.1 sections (4 free)")
        cfn = br.get("config:fn:SkyyWardrobe")

        def cop(*args):
            a = JArray(JObject)(len(args))
            for i, x in enumerate(args):
                a[i] = x
            return cfn.apply(a)
        r = cop("set", "items.allow", "Weapon_Kunai_*", None, None, "yes", "console")
        r2 = cop("set", "items.deny", "**", None, None, "yes", "console")
        K.check(str(r[0]) == "ok" and str(r2[0]) != "ok" and bool(Cfg.allow("Weapon_Kunai_Test")) and str(cop("get", "space.itemsCap")) == "1000",
                "X1 Server Setup (config:fn): set / check refuses / get (%s / %s)" % (list(r), list(r2)))
        P("CfgPub").flush()

        # ============================================================ X2 the classifier (P2: the engine's own Item getters)
        cl = lambda iid, q=1, m=None: str(Cls.classify(stack(iid, q, m)))
        K.check([cl(x) for x in ("Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs")] == ["a0", "a1", "a2", "a3"],
                "X2 armor -> its armor slot (getArmor().getArmorSlot(): Head, Chest, Hands, Legs = 0-3)")
        K.check(cl("Weapon_Sword_Iron") == "i" and cl("Tool_Pickaxe_Iron") == "i" and cl("Potion_Health", 5) == "i" and cl("Weapon_Kunai_Test") == "i",
                "X2 weapon / tool / consumable / items.allow -> Items")
        refused = {x: cl(x) for x in ("Rock_Stone", "Ingredient_Bar_Iron", "Backpack_Test", "Skyy_Sack_Mining_Normal", "Skyy_Menu", "Skyy_Vault_Prev",
                                      "Skyy_Unid_Bag_Rare", "Skyy_Talisman_Speed", "Gone_Item")}
        K.check(all(v.startswith("-") for v in refused.values()) and "Magic Bags" in refused["Rock_Stone"] and "holds items" in refused["Backpack_Test"]
                and "Identify" in refused["Skyy_Unid_Bag_Rare"] and "Accessory" in refused["Skyy_Talisman_Speed"] and "no longer knows" in refused["Gone_Item"],
                "X2 refused: blocks, materials, a container item, a bag, the menu item, vault arrows, a mystery bag, a talisman, an unknown id (%s)" % refused)
        K.check(cl("Weapon_Sword_Iron", 1, '{"SkyyGear": {"r": "rare", "id": false}}').startswith("-Identify"), "X2 unidentified gear (SkyyGear id:false) is refused")
        Cfg.DENY_IDS = "Weapon_Bow_*"
        K.check(cl("Weapon_Bow_Wood").startswith("-The server"), "X2 items.deny")
        Cfg.DENY_IDS = "-"
        K.check(bool(Cls.unique(stack("Weapon_Sword_Iron"))) and not bool(Cls.unique(stack("Potion_Health", 3))) and int(Codec.maxStack("Potion_Health")) == 25,
                "X2 gear = max stack 1 (one entry each); potions = a kind")

        # ============================================================ X3 the stamp (P1 engine side) + the lossless format
        g = stack("Weapon_Sword_Iron", 1, gdoc("rare", 12))
        g.setOverrideDroppedItemAnimation(True)
        s1 = Codec.stamp(g, "00aa00aa00aa00aa")
        K.check(str(Codec.stampOf(s1)) == "00aa00aa00aa00aa" and str(Codec.rar(s1)) == "rare" and int(Codec.lv(s1)) == 12 and s1.getOverrideDroppedItemAnimation()
                and Codec.stampOf(g) is None, "X3 stamp: the eid rides along, the SkyyGear document + the drop animation flag are kept, the original is untouched")
        s2 = Codec.unstamp(s1)
        K.check(Codec.stampOf(s2) is None and Codec.same(s2, g) and Codec.same(Codec.unstamp(stack("Weapon_Sword_Iron")), stack("Weapon_Sword_Iron")),
                "X3 unstamp gives back exactly the plain item")
        s3 = Codec.unstamp(Codec.stamp(stack("Tool_Pickaxe_Iron"), "x"))
        K.check(s3.getMetadata() is None, "X3 unstamping an item that had no metadata leaves NO empty document (stacks / recipes as before)")
        d1 = s1.withDurability(40.0)
        K.check(str(Codec.stampOf(d1)) == "00aa00aa00aa00aa" and abs(float(d1.getDurability()) - 40.0) < 1e-6, "X3 P1: durability loss (withDurability) keeps the stamp")
        rt = Codec.stackOf(JClass("org.bson.BsonDocument").parse(str(Codec.toJson(Codec.slotDoc(0, s1)))))
        K.check(Codec.same(rt, s1) and str(Codec.stampOf(rt)) == "00aa00aa00aa00aa" and rt.getOverrideDroppedItemAnimation(), "X3 the lossless slot format (codec + explicit fields) keeps the stamp")
        ITEMCODEC = JClass("com.hypixel.hytale.server.core.inventory.ItemStack").CODEC
        rt2 = ITEMCODEC.decode(ITEMCODEC.encode(s1))
        K.check(str(Codec.stampOf(rt2)) == "00aa00aa00aa00aa", "X3 P1: the engine's own ItemStack.CODEC (player saves) keeps the stamp")

        # ============================================================ X4 deposit (single), kinds, refusals, caps
        A = W.player("00000000-0000-0000-0000-00000000000a", "Alice")
        kA = str(A.u)
        setc(A.sto, 0, stack("Armor_Iron_Head", 1, gdoc("rare", 12)))
        setc(A.sto, 1, stack("Potion_Health", 5))
        setc(A.sto, 2, stack("Potion_Health", 7))
        setc(A.sto, 3, stack("Rock_Stone", 64))
        setc(A.hot, 8, stack("Skyy_Menu", 1))
        base, _ = census(A)
        r = run(A, 6, 0, "2:0")
        d = Store.get(kA, A.u)
        e0 = ent_by_id(d, "Armor_Iron_Head")
        K.check(r.startswith("+Into Requip: Armor_Iron_Head") and getc(A.sto, 0) is None and len(e0) == 1 and ein(e0[0]) and e0[0].space == 0 and e0[0].spot == 0
                and str(Codec.stampOf(e0[0].stack)) == str(e0[0].eid) and str(e0[0].rar) == "rare", "X4 deposit a helmet: Armor space, Head spot, IN, the stored copy carries its eid (%s)" % r)
        r = run(A, 6, 0, "2:1")
        r2 = run(A, 6, 0, "2:2")
        d = Store.get(kA, A.u)
        pk = ent_by_id(d, "Potion_Health")
        K.check(r.startswith("+") and r2.startswith("+") and len(pk) == 1 and pk[0].kind and int(pk[0].count) == 12 and int(pk[0].stack.getQuantity()) == 1,
                "X4 two potion stacks: ONE kind entry with count 12 (template qty 1)")
        r = run(A, 6, 0, "2:3")
        r2 = run(A, 6, 0, "1:8")
        K.check(r.startswith("-Blocks and materials go in your Magic Bags") and r2.startswith("-The SkyWynn Menu item") and getc(A.sto, 3) is not None,
                "X4 a block and the menu item are refused, nothing moves (%s / %s)" % (r, r2))
        c_after, dA = census(A)
        K.check(c_after == base and not once(A, dA), "X4 conservation + exactly once")
        jfile = os.path.join(Wd, "requip", kA, "journal.json")
        K.check(os.path.isfile(jfile) and json.load(open(jfile))["stage"] == "saved" and Jr.PENDING.containsKey(kA), "X4 the journal is kept (saved) inside its keep window")
        jd = json.load(open(jfile))
        K.check(len(jd["steps"]) == 3 and all(st["op"] == "deposit" for st in jd["steps"]) and jd["steps"][0]["moves"][0]["fresh"] is True
                and jn(jd["steps"][0]["moves"][0]["kb"]) == 1 and jn(jd["steps"][2]["moves"][0]["cnt"]) == 5, "X4 chained steps, each with its evidence (kb / cnt)")
        Cfg.ARMOR_CAP = 1
        setc(A.sto, 5, stack("Armor_Iron_Chest", 1))
        r = run(A, 6, 0, "2:5")
        K.check(r.startswith("-Armor space full (1)") and getc(A.sto, 5) is not None, "X4 a full space refuses, nothing moves (%s)" % r)
        Cfg.ARMOR_CAP = 1000
        files = sorted(os.listdir(os.path.join(Wd, "requip", kA)))
        K.check(files == ["armor-000.json", "index.json", "items-000.json", "journal.json", "loadouts.json", "orphans.json"],
                "X4 the profile folder: index + shards + loadouts + orphans + journal (%s)" % files)
        ix = json.load(open(os.path.join(Wd, "requip", kA, "index.json")))
        K.check(jn(ix["format"]) == 2, "X4 index.json format 2")

        # ============================================================ X5 Deposit all (storage + backpack; the hotbar only with deposit.hotbar)
        Bea = W.player("00000000-0000-0000-0000-00000000000b", "Bea")
        kB = str(Bea.u)
        for i, a in enumerate(["Armor_Copper_Head", "Armor_Copper_Chest", None, "Armor_Copper_Legs"]):
            if a:
                setc(Bea.arm, i, stack(a, 1, gdoc("unique", 5 + i)))
        setc(Bea.hot, 0, stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 3)))
        setc(Bea.hot, 1, stack("Food_Bread", 3))
        setc(Bea.hot, 8, stack("Skyy_Menu", 1))
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
            setc(Bea.sto, i, stack(a, 1, gdoc("rare", 20 + i)))
        setc(Bea.sto, 4, stack("Weapon_Sword_Iron", 1, gdoc("rare", 15)))
        setc(Bea.sto, 5, stack("Weapon_Sword_Mithril", 1, gdoc("legendary", 30)))
        setc(Bea.sto, 6, stack("Potion_Health", 10))
        setc(Bea.sto, 7, stack("Rock_Stone", 64))
        setc(Bea.bak, 0, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
        setc(Bea.hot, 2, stack("Tool_Hatchet_Iron", 1))
        baseB, _ = census(Bea)
        r = run(Bea, 7)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Deposited 8 stacks (1 stayed out: Blocks and materials go in your Magic Bags") and getc(Bea.sto, 7) is not None
                and getc(Bea.hot, 2) is not None and getc(Bea.hot, 0) is not None and dB.count(0) == 4 and dB.count(1) == 4,
                "X5 Deposit all: storage + backpack in (4 armor, 3 weapons, 1 potion kind), the block stays, the HOTBAR is untouched (%s)" % r)
        Cfg.DEP_HOT = True
        r = run(Bea, 7)
        Cfg.DEP_HOT = False
        K.check(r.startswith("+Deposited 3 stacks") and getc(Bea.hot, 2) is None and getc(Bea.hot, 8) is not None and getc(Bea.hot, 0) is None,
                "X5 deposit.hotbar on: the hotbar too, never the SkyWynn Menu item (%s)" % r)
        r = run(Bea, 7)
        K.check(r.startswith("-Nothing could go in: Blocks") , "X5 nothing left but the block: refused with the reason (%s)" % r)
        cB, dB = census(Bea)
        K.check(cB == baseB and not once(Bea, dB), "X5 conservation + exactly once")

        # ============================================================ FP 0.2.8 the Potion Flask + Food Pouch stay with you (built-in keep)
        FLS = ["Skyy_Flask_Empty", "Skyy_Flask_V_Potion_Health", "Skyy_Food_Pouch_Empty", "Skyy_Food_Pouch_V_Food_Bread"]
        K.check(all(bool(Cfg.builtinKeep(x)) and bool(Cfg.keep(x)) for x in FLS) and not bool(Cfg.builtinKeep("Skyy_FlaskLike_Test"))
                and not bool(Cfg.builtinKeep("Skyy_Food_Pouch")) and not bool(Cfg.builtinKeep(None)), "FP builtinKeep / keep = exactly the two prefixes")
        clf = {x: str(Cls.classify(stack(x, 1))) for x in FLS}
        K.check(all(v.startswith("-The Potion Flask and Food Pouch stay with you") for v in clf.values()) and str(Cls.classify(stack("Skyy_FlaskLike_Test", 1))) == "i",
                "FP the Items space refuses the Flask / Pouch (a look-alike usable item is still an Item) (%s)" % clf)
        keep0, allow0 = Cfg.KEEP_IDS, Cfg.ALLOW_IDS
        Cfg.KEEP_IDS = "-"
        Cfg.ALLOW_IDS = "Skyy_Flask_*,Skyy_Food_Pouch_*"
        K.check(all(bool(Cfg.keep(x)) for x in FLS) and not bool(Cfg.keep("Skyy_Menu")) and all(str(Cls.classify(stack(x, 1))).startswith("-The Potion Flask") for x in FLS),
                "FP swap.keepIds '-' + items.allow naming them: still kept and refused (a server owner cannot remove them); the Menu item then is not kept")
        Cfg.KEEP_IDS, Cfg.ALLOW_IDS = keep0, allow0
        Fay = W.player("00000000-0000-0000-0000-0000000000f1", "Fay")
        kF = str(Fay.u)
        setc(Fay.sto, 0, stack(FLS[0], 1))
        setc(Fay.sto, 1, stack(FLS[3], 1))
        setc(Fay.sto, 2, stack("Armor_Iron_Head", 1, gdoc("rare", 7)))
        setc(Fay.sto, 3, stack("Potion_Health", 4))
        setc(Fay.hot, 2, stack(FLS[1], 1))
        setc(Fay.hot, 3, stack(FLS[2], 1))
        baseF, _ = census(Fay)
        rf = [run(Fay, 6, 0, "2:0"), run(Fay, 6, 0, "2:1"), run(Fay, 6, 0, "1:2"), run(Fay, 6, 0, "1:3")]
        K.check(all(x.startswith("-The Potion Flask and Food Pouch stay with you") for x in rf) and getc(Fay.sto, 0) is not None
                and getc(Fay.hot, 3) is not None, "FP a single deposit of each (storage + hotbar) is refused, nothing moves (%s)" % rf)
        Cfg.DEP_HOT = True
        rda = run(Fay, 7)
        Cfg.DEP_HOT = False
        dF = Store.get(kF, Fay.u)
        K.check(rda.startswith("+Deposited 2 stacks") and [str(getc(c_, i_).getItemId()) for c_, i_ in ((Fay.sto, 0), (Fay.sto, 1), (Fay.hot, 2), (Fay.hot, 3))] == [FLS[0], FLS[3], FLS[1], FLS[2]]
                and len(ent_by_id(dF, "Armor_Iron_Head")) == 1 and len(ent_by_id(dF, "Potion_Health")) == 1,
                "FP Deposit all (+ hotbar): the helmet + potions in, the Flask / Pouch stay in their slots (%s)" % rda)
        eidF = lambda iid: str(ent_by_id(Store.get(kF, Fay.u), iid)[0].eid)
        rp = [run(Fay, 10, 0, "6|empty"), run(Fay, 10, 0, "7|k:" + eidF("Potion_Health")), run(Fay, 10, 0, "0|e:" + eidF("Armor_Iron_Head"))]
        K.check(all(x.startswith("+") for x in rp), "FP a loadout picks Empty for the Flask's hotbar slot, the potion kind for the Pouch's, the helmet (%s)" % rp)
        gap()
        req = run(Fay, 1, 0)
        cF, dF = census(Fay)
        K.check(str(getc(Fay.hot, 2).getItemId()) == FLS[1] and str(getc(Fay.hot, 3).getItemId()) == FLS[2] and getc(Fay.arm, 0) is not None
                and str(getc(Fay.arm, 0).getItemId()) == "Armor_Iron_Head", "FP Equip: the helmet goes on, the Flask / Pouch stay in hotbar 3 / 4 (Keep wins) (%s)" % req)
        K.check(not any(str(e_.itemId()).startswith("Skyy_Flask_") or str(e_.itemId()).startswith("Skyy_Food_Pouch_") for e_ in list(dF.entries.values())),
                "FP nothing of either prefix is ever in the pool")
        K.check(cF == baseF and not once(Fay, dF), "FP conservation + exactly once")

        # ============================================================ RF 0.2.9 Deposit all leaves what the Potion Flask / Food Pouch claim
        from jpype import JImplements, JOverride

        @JImplements("java.util.function.Function")
        class ClaimFn(object):
            """SkyyCooking 0.1.11's supply:fn:claims contract: Object[] {UUID, String id} -> Boolean (TRUE = the Flask / Pouch takes it now)"""
            def __init__(self):
                self.ids, self.calls, self.mode = set(), [], "ok"

            @JOverride
            def apply(self, a):
                self.calls.append((str(a[0]), str(a[1])))
                if self.mode == "boom":
                    raise JClass("java.lang.IllegalStateException")("claims boom")
                if self.mode == "odd":
                    return JClass("java.lang.String")("yes")
                return JClass("java.lang.Boolean").valueOf(str(a[1]) in self.ids)
        CF = ClaimFn()
        CF.ids = {"Food_Bread", "Potion_Health"}
        br.put("supply:fn:claims", CF)
        Rae = W.player("00000000-0000-0000-0000-0000000000f2", "Rae")
        kR = str(Rae.u)
        setc(Rae.sto, 0, stack("Food_Bread", 10))
        setc(Rae.sto, 1, stack("Potion_Health", 4))
        setc(Rae.sto, 2, stack("Potion_Mana", 3))
        setc(Rae.sto, 3, stack("Armor_Iron_Head", 1, gdoc("rare", 7)))
        setc(Rae.sto, 4, stack("Food_Bread", 1, '{"Skyy_Test": {"note": "a metadata bread"}}'))
        setc(Rae.bak, 0, stack("Food_Bread", 5))
        setc(Rae.hot, 4, stack("Food_Bread", 2))
        baseR, _ = census(Rae)
        Cfg.DEP_HOT = True
        rr = run(Rae, 7)
        Cfg.DEP_HOT = False
        dR = Store.get(kR, Rae.u)
        poolR = sorted((str(e_.itemId()), int(e_.count) if e_.kind else 1) for e_ in list(dR.entries.values()))
        K.check(getc(Rae.sto, 0) is not None and str(getc(Rae.sto, 0).getItemId()) == "Food_Bread" and int(getc(Rae.sto, 0).getQuantity()) == 10
                and getc(Rae.sto, 1) is not None and int(getc(Rae.sto, 1).getQuantity()) == 4
                and getc(Rae.bak, 0) is not None and int(getc(Rae.bak, 0).getQuantity()) == 5,
                "RF REPRO: Deposit all leaves the claimed bread (storage 10 + backpack 5) and health potions (4) for the Flask / Pouch (0.2.8 pooled them) (%s; pool %s)" % (rr, poolR))
        K.check(getc(Rae.sto, 2) is None and getc(Rae.sto, 3) is None and getc(Rae.sto, 4) is None and getc(Rae.hot, 4) is None
                and len(ent_by_id(dR, "Potion_Mana")) == 1 and len(ent_by_id(dR, "Armor_Iron_Head")) == 1 and len(ent_by_id(dR, "Food_Bread")) == 2
                and not ent_by_id(dR, "Potion_Health"),
                "RF the unclaimed potion, the helmet, the metadata bread and the HOTBAR bread go in as before (pool %s)" % poolR)
        K.check(rr.startswith("+Deposited 4 stacks (3 stayed out: the Potion Flask / Food Pouch takes your"), "RF the answer names what stayed (%s)" % rr)
        ids_asked = [c_[1] for c_ in CF.calls]
        K.check(sorted(ids_asked) == sorted(set(ids_asked)) and set(ids_asked) == {"Food_Bread", "Potion_Health", "Potion_Mana"}
                and all(c_[0] == kR for c_ in CF.calls),
                "RF one supply:fn:claims ask per distinct plain storage / backpack id, with the player's uuid (%s)" % CF.calls)
        cR, dR = census(Rae)
        K.check(cR == baseR and not once(Rae, dR), "RF conservation + exactly once (after the skip)")
        # every claimed stack again: still left (a second press changes nothing)
        rr2 = run(Rae, 7)
        K.check(rr2.startswith("-Nothing could go in: the Potion Flask / Food Pouch takes your") and int(getc(Rae.sto, 0).getQuantity()) == 10,
                "RF a second Deposit all with only claimed stacks left moves nothing (%s)" % rr2)
        # the single Deposit click is an explicit choice: the claimed bread goes in
        r6 = run(Rae, 6, 0, "2:0")
        K.check(r6.startswith("+Into Requip: Food_Bread x10") and getc(Rae.sto, 0) is None, "RF a single Deposit click of claimed bread still puts it in (%s)" % r6)
        # claims answering FALSE (full / auto-fill off), a non-Boolean answer, a throwing claims, no key: as 0.2.8
        CF.ids = set()
        CF.calls = []
        setc(Rae.sto, 0, stack("Food_Bread", 6))
        baseR, _ = census(Rae)
        r7a = run(Rae, 7)
        K.check(r7a.startswith("+Deposited 3 stacks") and getc(Rae.sto, 0) is None and getc(Rae.sto, 1) is None and getc(Rae.bak, 0) is None,
                "RF claims FALSE (the Pouch is full / off): Deposit all takes them as 0.2.8 (%s)" % r7a)
        cR, dR = census(Rae)
        K.check(cR == baseR and not once(Rae, dR), "RF conservation + exactly once (claims FALSE)")
        for mode_ in ("odd", "boom", "gone"):
            setc(Rae.sto, 0, stack("Food_Bread", 3))
            setc(Rae.bak, 1, stack("Potion_Health", 2))
            CF.ids = {"Food_Bread", "Potion_Health"}
            CF.mode = mode_
            if mode_ == "gone":
                br.remove("supply:fn:claims")
            baseR, _ = census(Rae)
            rm = run(Rae, 7)
            K.check(rm.startswith("+Deposited 2 stacks") and getc(Rae.sto, 0) is None and getc(Rae.bak, 1) is None,
                    "RF claims %s: no exception escapes, Deposit all as 0.2.8 (%s)" % (mode_, rm))
            cR, dR = census(Rae)
            K.check(cR == baseR and not once(Rae, dR), "RF conservation + exactly once (claims %s)" % mode_)
        CF.mode = "ok"
        K.check(not br.containsKey("supply:fn:claims"), "RF the stand-in is gone again (later sections run as 0.2.8)")
        # take the hatchet + pickaxe + bread back out for the equip tests (Take out = plain items again)
        for iid in ("Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"):
            r = run(Bea, 8, 0, str(ent_by_id(Store.get(kB, Bea.u), iid)[0].eid))
            K.check(r.startswith("+Taken out: " + iid + " - it is a plain item again"), "X8 Take out %s (%s)" % (iid, r))
        r = run(Bea, 8, 0, str(ent_by_id(Store.get(kB, Bea.u), "Food_Bread")[0].eid))
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Taken out: Food_Bread x3") and not ent_by_id(dB, "Food_Bread") and not stamps_of(Bea), "X8 Take out a kind: the whole count (3), the empty unpicked kind entry goes, nothing stamped")
        cB, dB = census(Bea)
        K.check(cB == baseB and not once(Bea, dB), "X8 conservation after Take out")
        # move the taken-out items back to where the equip test wants them
        for c in Bea.secs:
            for i in range(int(c.getCapacity())):
                s = getc(c, i)
                if s is not None and str(s.getItemId()) in ("Tool_Pickaxe_Iron", "Food_Bread") and c is not Bea.hot:
                    c.removeItemStackFromSlot(JShort(i), False)
                    setc(Bea.hot, 0 if str(s.getItemId()) == "Tool_Pickaxe_Iron" else 1, s)

        # ============================================================ X6 picks (references only: no item moves)
        dB = Store.get(kB, Bea.u)
        eid = lambda iid: str(ent_by_id(Store.get(kB, Bea.u), iid)[0].eid)
        snapB = W.snap(Bea)
        res = [run(Bea, 10, 0, "%d|e:%s" % (k_, eid(a))) for k_, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"])]
        res.append(run(Bea, 10, 0, "4|e:" + eid("Weapon_Sword_Mithril")))
        res.append(run(Bea, 10, 0, "5|k:" + eid("Potion_Health")))
        res.append(run(Bea, 10, 0, "6|empty"))
        K.check(all(x.startswith("+") for x in res), "X6 picks: 4 armor pieces, a sword in hotbar 1, a potion kind in hotbar 2, Empty (%s)" % res)
        bad = [run(Bea, 10, 0, "0|e:" + eid("Armor_Iron_Chest")), run(Bea, 10, 0, "7|e:" + eid("Weapon_Sword_Mithril")),
               run(Bea, 10, 0, "8|e:" + eid("Armor_Iron_Head")), run(Bea, 10, 0, "1|k:" + eid("Potion_Health")),
               run(Bea, 10, 0, "2|pocket"), run(Bea, 10, 0, "9|pocket"), run(Bea, 10, 0, "4|e:ffffffffffffffff"), run(Bea, 10, 0, "13|keep")]
        K.check(bad[0].startswith("-That piece does not go on Head") and bad[1].startswith("-It is already picked for Hotbar 1")
                and bad[2].startswith("-Armor goes in the armor slots") and bad[3].startswith("-Potions and food go in hotbar")
                and bad[4].startswith("-Pocket blocks are for hotbar slots only") and bad[5].startswith("-Hold the block you want in hotbar slot 6")
                and bad[6].startswith("-That item is not in Requip") and bad[7].startswith("-Pick a slot"), "X6 every refused pick (%s)" % bad)
        setc(Bea.hot, 5, stack("Wood_Oak_Log", 3))
        r = run(Bea, 10, 0, "9|pocket")
        Bea.hot.removeItemStackFromSlot(JShort(5), False)
        K.check(r.startswith("+Loadout 1: Hotbar 6 fills with Wood_Oak_Log from your Magic Bags"), "X6 Pocket pick takes the block held in that slot (%s)" % r)
        r = run(Bea, 4, 0, "Combat")
        dB = Store.get(kB, Bea.u)
        L0 = dB.slots[0]
        K.check([str(L0.picks[k_]) if L0.picks[k_] is not None else None for k_ in (6, 9, 10)] == ["x", "p:Wood_Oak_Log:0", None] and str(L0.name) == "Combat"
                and W.snap(Bea) == snapB, "X6 the loadout file holds the picks (Empty, pocket, Keep), the name; no item moved")
        ld = json.load(open(os.path.join(Wd, "requip", kB, "loadouts.json")))
        K.check(ld["loadouts"][0]["picks"][9] == "p:Wood_Oak_Log:0" and ld["loadouts"][0]["picks"][12] == "", "X6 loadouts.json (Keep = \"\")")

        # ============================================================ X7 EQUIP
        state.setdefault("bags", {})[str(Bea.u)] = {"Wood_Oak_Log": 500, "Rock_Stone": 10}
        state["calls"]["take"][:] = []
        baseB, _ = census(Bea)
        gap()
        r = run(Bea, 1, 0)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Equipped Combat (11 moves, 1 pocket slots filled)"), "X7 Equip Combat: 5 deposits + 6 withdrawals + the pocket slot (%s)" % r)
        arm = [str(getc(Bea.arm, i).getItemId()) if getc(Bea.arm, i) else None for i in range(4)]
        K.check(arm == ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"] and all(Codec.stampOf(getc(Bea.arm, i)) is not None for i in range(4)),
                "X7 the picked armor is on, each stamped with its eid (%s)" % arm)
        K.check(str(getc(Bea.hot, 0).getItemId()) == "Weapon_Sword_Mithril" and str(Codec.stampOf(getc(Bea.hot, 0))) == eid("Weapon_Sword_Mithril")
                and str(getc(Bea.hot, 1).getItemId()) == "Potion_Health" and int(getc(Bea.hot, 1).getQuantity()) == 10 and Codec.stampOf(getc(Bea.hot, 1)) is None,
                "X7 the sword (stamped) in hotbar 1, the potions (10 = all of the kind, never stamped) in hotbar 2")
        K.check(getc(Bea.hot, 5) is not None and str(getc(Bea.hot, 5).getItemId()) == "Wood_Oak_Log" and int(getc(Bea.hot, 5).getQuantity()) == 100
                and state["bags"][str(Bea.u)]["Wood_Oak_Log"] == 400 and ("Wood_Oak_Log", 100) in state["calls"]["commit"],
                "X7 the pocket slot took a full stack (100) from the Magic Bags (sacks:fn:take), committed")
        pm = br.get("requip:pocket:" + kB)
        K.check(pm is not None and dict((int(k_), str(v)) for k_, v in pm.items()) == {5: "Wood_Oak_Log"}, "X7 requip:pocket:<uuid> = {hotbar 6: Wood_Oak_Log}")
        K.check(getc(Bea.hot, 8) is not None and str(getc(Bea.hot, 8).getItemId()) == "Skyy_Menu" and dB.lastWorn == 0, "X7 the menu item stays (Keep), loadout 1 is LAST WORN")
        cp_ = ent_by_id(dB, "Armor_Copper_Head") + ent_by_id(dB, "Tool_Pickaxe_Iron") + ent_by_id(dB, "Food_Bread")
        K.check(len(cp_) == 3 and all(ein(e) for e in cp_), "X7 what was worn in the picked slots went INTO the pool (copper, pickaxe, bread kind)")
        cB, dB = census(Bea)
        exp = dict(baseB)
        exp[("Wood_Oak_Log", "")] = exp.get(("Wood_Oak_Log", ""), 0) + 100
        K.check(cB == exp and not once(Bea, dB), "X7 conservation (+100 logs from the bags) + exactly once")
        # loadout 2 picks the SAME sword (shared) in another slot + the pickaxe + the copper head; Equip moves the sword hotbar 1 -> 3
        res = [run(Bea, 10, 1, "6|e:" + eid("Weapon_Sword_Mithril")), run(Bea, 10, 1, "4|e:" + eid("Tool_Pickaxe_Iron")),
               run(Bea, 10, 1, "0|e:" + eid("Armor_Copper_Head")), run(Bea, 10, 1, "9|empty")]
        K.check(all(x.startswith("+") for x in res) and Store.get(kB, Bea.u).picked(eid("Weapon_Sword_Mithril")) == 2, "X7 the same sword picked in 2 loadouts (%s)" % res)
        swordEid = eid("Weapon_Sword_Mithril")
        baseB, _ = census(Bea)
        gap()
        state["bagRoom"] = 60
        r = run(Bea, 1, 1)
        state.pop("bagRoom")
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("=Equipped Loadout 2") and "40 pocket blocks did not fit your bags - they are in your storage" in r and str(getc(Bea.hot, 2).getItemId()) == "Weapon_Sword_Mithril" and str(Codec.stampOf(getc(Bea.hot, 2))) == swordEid
                and str(getc(Bea.hot, 0).getItemId()) == "Tool_Pickaxe_Iron" and str(getc(Bea.arm, 0).getItemId()) == "Armor_Copper_Head"
                and str(getc(Bea.arm, 1).getItemId()) == "Armor_Iron_Chest", "X7 Equip 2: the shared sword moved hotbar 1 -> 3 (same eid), pickaxe on, copper head on, Keep slots keep the iron (%s)" % r)
        K.check(not ein(dB.entry(swordEid)) and ein(ent_by_id(dB, "Armor_Iron_Head")[0]), "X7 ... the sword is OUT (never IN at the end), the iron head went in")
        K.check(br.get("requip:pocket:" + kB) is None and state["bags"][str(Bea.u)]["Wood_Oak_Log"] == 460 and getc(Bea.hot, 5) is None
                and any(getc(Bea.sto, i) is not None and str(getc(Bea.sto, i).getItemId()) == "Wood_Oak_Log" and int(getc(Bea.sto, i).getQuantity()) == 40 for i in range(36)),
                "X7 leaving the pocket slot: its blocks went to storage, 60 back into the bags (sacks:fn:deposit, bag full), 40 stay in storage; requip:pocket removed")
        K.check(("Wood_Oak_Log", 60, 5) in state["calls"]["deposit"] and not state["calls"].get("deposit3"),
                "FIX-E1 the give-back calls sacks:fn:deposit with the HOTBAR SLOT (4th argument, SkyySacks 0.7.17 contract) BEFORE the Equip lifts the stack; Sacks took 60 from slot 6 itself (%s)" % state["calls"]["deposit"])
        cB, dB = census(Bea)
        exp = dict(baseB)
        exp[("Wood_Oak_Log", "")] = exp.get(("Wood_Oak_Log", ""), 0) - 60
        K.check(cB == exp and not once(Bea, dB), "X7 conservation (-60 logs to the bags) + exactly once")
        # NOT WITH YOU: the sword leaves the inventory (dropped), Equip 1 keeps that slot with a note; removed picks too
        sw = getc(Bea.hot, 2)
        Bea.hot.removeItemStackFromSlot(JShort(2), False)
        gap()
        r = run(Bea, 1, 0)
        K.check(r.startswith("=Equipped Combat") and "Hotbar 1: Weapon_Sword_Mithril is not with you" in r and getc(Bea.hot, 0) is not None
                and str(getc(Bea.hot, 0).getItemId()) == "Tool_Pickaxe_Iron", "X7 a picked item that is not with you: that slot is kept, a note (%s)" % r)
        setc(Bea.hot, 2, sw)
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once (the sword is back)")
        # a slot holding something refused (a block) with an Empty pick: it moves to storage; no room anywhere: kept + note
        setc(Bea.hot, 5, stack("Rock_Stone", 5))
        gap()
        r = run(Bea, 1, 1)
        K.check(getc(Bea.hot, 5) is None and any(getc(Bea.sto, i) is not None and str(getc(Bea.sto, i).getItemId()) == "Rock_Stone" and int(getc(Bea.sto, i).getQuantity()) == 5 for i in range(36)),
                "X7 Empty on a slot holding a block: the block moves to storage (spill) (%s)" % r)
        filler = []
        for c in (Bea.sto, Bea.bak):
            for i in range(int(c.getCapacity())):
                if getc(c, i) is None:
                    setc(c, i, stack("Ingredient_Bar_Iron", 1))
                    filler.append((c, i))
        setc(Bea.hot, 6, stack("Rock_Stone", 7))
        r = run(Bea, 10, 0, "10|empty")
        gap()
        r = run(Bea, 1, 0)
        K.check("Hotbar 7: no room in your inventory for Rock_Stone - kept" in r and getc(Bea.hot, 6) is not None, "X7 no room for a spill: the slot is kept + note (%s)" % r)
        for c, i in filler:
            c.removeItemStackFromSlot(JShort(i), False)
        Bea.hot.removeItemStackFromSlot(JShort(6), False)
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once after the spill tests")
        # a picked item that was taken out: the pick shows removed, Equip keeps the slot
        gap()
        run(Bea, 1, 1)
        hb = ent_by_id(Store.get(kB, Bea.u), "Armor_Iron_Head")[0]
        r0 = run(Bea, 8, 0, str(hb.eid)) if ein(hb) else "-not in the pool"
        gap()
        r = run(Bea, 1, 0)
        K.check(r0.startswith("+Taken out") and "Head: the picked item was taken out of Requip" in r, "X7 a picked item that was taken out: noted, the slot kept (%s / %s)" % (r0, r))
        cB, dB = census(Bea)
        K.check(not once(Bea, dB), "X7 exactly once")
        # locked loadout
        gap()
        r = run(Bea, 1, 6)
        K.check(r.startswith("-Loadout 7 is unlocks at Overall Level 20") or "unlocks at Overall Level" in r, "X7 a locked loadout cannot be equipped (%s)" % r)

        # ============================================================ X8 fetch / Forget / pets + abilities
        dB = Store.get(kB, Bea.u)
        bow = ent_by_id(dB, "Weapon_Bow_Wood")[0]
        r = run(Bea, 14, 0, str(bow.eid))
        dB = Store.get(kB, Bea.u)
        K.check(r == "+ok" and not ein(dB.entry(str(bow.eid))) and str(bow.eid) in stamps_of(Bea), "X8 fetch: into the inventory, stamp kept, the entry is OUT (%s)" % r)
        r = run(Bea, 9, 0, str(bow.eid))
        K.check(r.startswith("-It is with you"), "X8 Forget refuses an item that is with you (%s)" % r)
        for c in Bea.secs:
            for i in range(int(c.getCapacity())):
                if Codec.stampOf(getc(c, i)) == bow.eid:
                    c.removeItemStackFromSlot(JShort(i), False)
        r = run(Bea, 10, 0, "11|e:" + str(bow.eid))
        r2 = run(Bea, 9, 0, str(bow.eid))
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+") and r2.startswith("+Forgotten: Weapon_Bow_Wood") and dB.entry(str(bow.eid)) is None and dB.slots[0].picks[11] is None,
                "X8 Forget an OUT entry that is not with you: gone, and every pick of it cleared (%s)" % r2)
        r = run(Bea, 9, 0, eid("Weapon_Sword_Iron"))
        K.check(r.startswith("-It is in Requip"), "X8 Forget refuses an IN entry")
        state["pets"], state["abil"] = "pX|sY", "v=1;class=Mage;p1=Meteor;n1=Meteor"
        r = run(Bea, 2, 2)
        dB = Store.get(kB, Bea.u)
        K.check(r.startswith("+Saved into Loadout 3: your pets and your abilities") and dB.slots[2].hasPets and str(dB.slots[2].pet) == "pX", "X8 Save pets/abilities (%s)" % r)
        state["calls"]["pets"][:] = []
        gap()
        r = run(Bea, 1, 2)
        K.check(r.startswith("+Equipped Loadout 3 (0 moves)") and state["calls"]["pets"] == [(kB, "pX", "sY")], "X8 Equip a loadout without item picks: nothing moves, pets applied (%s)" % r)

        # ============================================================ X9 Use what I wear (registered IN PLACE) + the round trip
        Cy = W.player("00000000-0000-0000-0000-00000000000c", "Cyd")
        kC = str(Cy.u)
        for i, a in enumerate(["Armor_Gold_Head", "Armor_Iron_Chest", None, "Armor_Iron_Legs"]):
            if a:
                setc(Cy.arm, i, stack(a, 1, gdoc("rare", 30 + i)))
        setc(Cy.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("epic", 33)))
        setc(Cy.hot, 1, stack("Potion_Health", 4))
        setc(Cy.hot, 2, stack("Rock_Stone", 20))
        setc(Cy.hot, 3, stack("Ingredient_Bar_Iron", 3, '{"x": 1}'))
        setc(Cy.hot, 8, stack("Skyy_Menu", 1))
        baseC, _ = census(Cy)
        snapC = [[str(s.getItemId()) if s is not None and not s.isEmpty() else None for s in sec] for sec in W.snap(Cy)]
        r = run(Cy, 12, 0)
        dC = Store.get(kC, Cy.u)
        L = dC.slots[0]
        picks = [str(x) if x is not None else None for x in L.picks]
        K.check("Loadout 1 now uses what you wear (4 gear, 1 potion / food stacks)" in r and "Hotbar 4: Blocks and materials" in r and [p_[:2] if p_ else None for p_ in picks] == ["e:", "e:", None, "e:", "e:", "k:", "p:", None, None, None, None, None, None],
                "X9 Use what I wear: 4 gear picks, the potion kind, the block as a pocket pick, the metadata material + empty slots Keep (%s / %s)" % (r, picks))
        snapC2 = [[str(s.getItemId()) if s is not None and not s.isEmpty() else None for s in sec] for sec in W.snap(Cy)]
        K.check(snapC2 == snapC and len(stamps_of(Cy)) == 4 and all(not ein(e) for e in dC.entries.values() if not e.kind), "X9 nothing moved; the 4 gear pieces are stamped IN PLACE, their entries are OUT")
        cC, dC = census(Cy)
        K.check(cC == baseC and not once(Cy, dC), "X9 conservation + exactly once")
        r = run(Cy, 12, 0)
        dC = Store.get(kC, Cy.u)
        K.check("Loadout 1 now uses what you wear" in r and len([e for e in dC.entries.values() if not e.kind]) == 4, "X9 again: the same entries are re-used (no new eids)")
        gap()
        r = run(Cy, 1, 1)
        K.check(r.startswith("+Equipped Loadout 2 (0 moves)"), "X9 an empty loadout keeps everything (Keep) (%s)" % r)
        for k_ in range(13):
            run(Cy, 10, 1, "%d|empty" % k_)
        gap()
        r = run(Cy, 1, 1)
        dC = Store.get(kC, Cy.u)
        K.check(r.startswith("=Equipped Loadout 2") and all(getc(Cy.arm, i) is None for i in range(4)) and getc(Cy.hot, 0) is None and getc(Cy.hot, 8) is not None
                and all(ein(e) for e in dC.entries.values()), "X9 an all-Empty loadout puts everything away (blocks to storage, the menu item stays) (%s)" % r)
        cC, dC = census(Cy)
        K.check(cC == baseC and not once(Cy, dC), "X9 conservation")
        gap()
        r = run(Cy, 1, 0)
        cC, dC = census(Cy)
        K.check("Equipped Loadout 1" in r and "no Rock_Stone in your Magic Bags for hotbar 3" in r and str(getc(Cy.arm, 0).getItemId()) == "Armor_Gold_Head" and str(getc(Cy.hot, 0).getItemId()) == "Weapon_Sword_Iron"
                and int(getc(Cy.hot, 1).getQuantity()) == 4 and cC == baseC and not once(Cy, dC), "X9 Equip it back: the same gear returns (%s)" % r)

        # ============================================================ X10 the gate (REAL DeathComponent / DamageDataComponent / TimeResource reads)
        DDC = JClass("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent")
        Death = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
        TR = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
        Inst = JClass("java.time.Instant")
        G = W.player("00000000-0000-0000-0000-000000000010", "Gil")
        kG = str(G.u)
        setc(G.sto, 0, stack("Weapon_Sword_Iron", 1))
        setc(G.sto, 1, stack("Weapon_Bow_Wood", 1))
        comps = G.st.comps.get(G.ref)
        gap()
        Gate.BUSY.put(G.u, True)
        r = run(G, 1, 0)
        Gate.BUSY.remove(G.u)
        K.check(r.startswith("-One Requip change at a time"), "X10 a second click while a change runs: refused (%s)" % r)
        dc = U.allocateInstance(DDC.class_)
        tl = Inst.now()
        E.jf(TR, "now").set(G.st.res, tl)
        for g_ in ("getLastDamageTime", "getLastCombatAction"):
            E.jf(DDC, E.field_of("com.hypixel.hytale.server.core.entity.damage.DamageDataComponent", g_)[1]).set(dc, tl.minusSeconds(3))
        comps.put(types["ddc"], dc)
        r = run(G, 1, 0)
        r2 = run(G, 6, 0, "2:0")
        K.check(r.startswith("-You are in combat - wait 7 s") and r2.startswith("+Into Requip"), "X10 in combat: Equip refused, a deposit still works (%s / %s)" % (r, r2))
        comps.put(types["death"], U.allocateInstance(Death.class_))
        r = run(G, 1, 0)
        r2 = run(G, 6, 0, "2:1")
        K.check(r.startswith("-You cannot use Requip while dead") and r2.startswith("-You cannot use Requip while dead"), "X10 dead: everything refused (%s)" % r2)
        comps.remove(types["death"])
        comps.remove(types["ddc"])
        br.put("profile:busy:" + kG, True)
        r = run(G, 6, 0, "2:1")
        br.remove("profile:busy:" + kG)
        r2 = run(G, 6, 0, "2:1")
        K.check(r.startswith("-Your profile is still loading") and r2.startswith("-Requip opens again 30 s after a profile switch"), "X10 profile:busy, then the 30 s settle (%s / %s)" % (r, r2))
        Gate.BUSYAT.clear()
        Gate.EPOCH.put(G.u, JLong(5))
        br.put("profile:epoch:" + kG, JLong(6))
        r = run(G, 6, 0, "2:1")
        K.check(r.startswith("-Requip opens again"), "X10 a profile epoch change opens the settle window (%s)" % r)
        Gate.EPOCHAT.clear()
        Cfg.ON = False
        r = run(G, 6, 0, "2:1")
        r2 = run(G, 8, 0, str(ent_by_id(Store.get(kG, G.u), "Weapon_Sword_Iron")[0].eid))
        Cfg.ON = True
        K.check(r.startswith("-Requip is switched off") and r2.startswith("+Taken out"), "X10 switched off: deposits refused, Take out still works (%s / %s)" % (r, r2))

        # ============================================================ X11 save failure / put failure / rollback failure -> LOCKED -> admin repair
        Fk = W.player("00000000-0000-0000-0000-000000000011", "Fay", flaky=True)
        kF = str(Fk.u)
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest"]):
            setc(Fk.sto, i, stack(a, 1, gdoc("rare", 3)))
        setc(Fk.arm, 0, stack("Armor_Copper_Head", 1))
        setc(Fk.arm, 1, stack("Armor_Copper_Chest", 1))
        run(Fk, 7)
        dF = Store.get(kF, Fk.u)
        run(Fk, 10, 0, "0|e:" + str(ent_by_id(dF, "Armor_Iron_Head")[0].eid))
        run(Fk, 10, 0, "1|e:" + str(ent_by_id(dF, "Armor_Iron_Chest")[0].eid))
        baseF, _ = census(Fk)
        snapF = W.snap(Fk)
        Store.FAIL_NEXT = 1
        gap()
        r = run(Fk, 1, 0)
        cF, dF = census(Fk)
        jF0 = json.load(open(os.path.join(Wd, "requip", kF, "journal.json"))) if os.path.isfile(os.path.join(Wd, "requip", kF, "journal.json")) else {"steps": [], "stage": "saved"}
        K.check(r.startswith("-Could not save Requip - everything was put back") and cF == baseF and not once(Fk, dF) and W.snap(Fk) == snapF
                and jF0["stage"] == "saved" and not [st for st in jF0["steps"] if st["op"] == "equip"], "X11 a save failure: every move rolled back, the journal back to its earlier steps (%s)" % r)
        Flaky = JClass(FAKE_PKG + ".FlakyBox")
        Flaky.FAIL_AT = 1
        gap()
        r = run(Fk, 1, 0)
        Flaky.FAIL_AT = -1
        cF, dF = census(Fk)
        K.check(r.startswith("-Equip stopped (could not put") and "everything was put back" in r and cF == baseF and not once(Fk, dF), "X11 a put failure mid-Equip: rolled back (%s)" % r)
        Flaky.FAIL_AT, Flaky.STICKY = 1, True
        gap()
        r = run(Fk, 1, 0)
        Flaky.FAIL_AT, Flaky.STICKY, Flaky.FAIL_ALL = -1, False, False
        dF = Store.get(kF, Fk.u)
        jF = json.load(open(os.path.join(Wd, "requip", kF, "journal.json")))
        K.check(r.startswith("-The change failed and could not be undone - Requip is locked") and dF.bad and jF["stage"] == "failed", "X11 a failed rollback: LOCKED, journal 'failed' (%s)" % r)
        r = run(Fk, 6, 0, "2:5")
        r2 = run(Fk, 5)
        K.check(r.startswith("-") and "locked" in r and r2 == "=Nothing to repair.", "X11 locked: every change refused, a normal repair leaves a failed journal alone (%s / %s)" % (r, r2))
        restart()
        Fk.pr.msgs = None
        P("WdRepairTask")(Fk.u, 0, True, None).run()
        cF, dF = census(Fk)
        K.check(not dF.bad and cF == baseF and not once(Fk, dF) and not os.path.isfile(os.path.join(Wd, "requip", kF, "journal.json")),
                "X11 /requipadmin repair (force): reconciled from the live inventory, unlocked, every item once (%s)" % (Fk.pr.msgs,))

        # ============================================================ X12 CRASH AT EVERY STEP of every transaction, live as-is AND rolled back
        cases = [0]
        crash_fail = []
        uid_n = [100]

        def fresh(name):
            uid_n[0] += 1
            return W.player("00000000-0000-0000-0000-%012d" % uid_n[0], name)

        def setup_equip(p):
            for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
                setc(p.sto, i, stack(a, 1, gdoc("rare", 10 + i)))
            setc(p.sto, 4, stack("Weapon_Sword_Mithril", 1, gdoc("mythic", 40)))
            setc(p.sto, 5, stack("Potion_Health", 10))
            setc(p.sto, 6, stack("Weapon_Sword_Iron", 1, gdoc("rare", 2)))
            run(p, 7)
            setc(p.arm, 0, stack("Armor_Copper_Head", 1, gdoc("unique", 1)))
            setc(p.arm, 1, stack("Armor_Copper_Chest", 1))
            setc(p.hot, 0, stack("Tool_Pickaxe_Iron", 1, gdoc("normal", 2)))
            setc(p.hot, 1, stack("Food_Bread", 3))
            setc(p.hot, 2, stack("Rock_Stone", 10))
            setc(p.hot, 8, stack("Skyy_Menu", 1))
            d = Store.get(str(p.u), p.u)
            e_ = lambda iid: str(ent_by_id(d, iid)[0].eid)
            for k_, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs"]):
                run(p, 10, 0, "%d|e:%s" % (k_, e_(a)))
            run(p, 10, 0, "4|e:" + e_("Weapon_Sword_Mithril"))
            run(p, 10, 0, "5|k:" + e_("Potion_Health"))
            run(p, 10, 0, "6|empty")
            run(p, 10, 0, "7|e:" + e_("Weapon_Sword_Iron"))
            # loadout 2: the mithril sword (out on you after loadout 1) in hotbar 3 = a pool round trip; the pickaxe back on
            run(p, 10, 1, "6|e:" + e_("Weapon_Sword_Mithril"))
            run(p, 10, 1, "0|empty")

        def op_equip1(p):
            gap()
            return run(p, 1, 0)

        def setup_equip2(p):
            setup_equip(p)
            gap()
            run(p, 1, 0)
            d = Store.get(str(p.u), p.u)
            run(p, 10, 1, "4|e:" + str(ent_by_id(d, "Tool_Pickaxe_Iron")[0].eid))

        def op_equip2(p):
            gap()
            return run(p, 1, 1)

        def setup_dep(p):
            setc(p.sto, 0, stack("Armor_Iron_Head", 1, gdoc("rare", 1)))
            setc(p.sto, 1, stack("Potion_Health", 6))
            setc(p.sto, 2, stack("Weapon_Sword_Iron", 1))
            setc(p.sto, 3, stack("Weapon_Sword_Iron", 1))
            setc(p.bak, 0, stack("Potion_Health", 4))
            setc(p.bak, 1, stack("Rock_Stone", 3))

        def op_depall(p):
            return run(p, 7)

        def setup_take(p):
            setup_dep(p)
            run(p, 7)

        def op_take(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 8, 0, str(ent_by_id(d, "Weapon_Sword_Iron")[0].eid))

        def op_takekind(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 8, 0, str(ent_by_id(d, "Potion_Health")[0].eid))

        def op_fetch(p):
            d = Store.get(str(p.u), p.u)
            return run(p, 14, 0, str(ent_by_id(d, "Armor_Iron_Head")[0].eid))

        def setup_ret(p):
            d = Store.get(str(p.u), p.u)
            d.orphan("test", stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
            d.rev = d.rev + 1
            Store.save(d)

        def op_ret(p):
            return run(p, 13)

        def op_craft(p):
            return str(Ops.craft(p.pr, p.ref, p.st, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 22)), "test", ""))

        def count_points(setup, op):
            """how many moves (the op's journal step) and file writes the op makes, on a fresh player"""
            p = fresh("count")
            setup(p)
            f0 = int(Store.FILES)
            op(p)
            f1 = int(Store.FILES)
            jf_ = os.path.join(Wd, "requip", str(Store.pkey(p.u)), "journal.json")
            n_ = len(json.load(open(jf_))["steps"][-1]["moves"]) if os.path.isfile(jf_) else 0
            return n_, f1 - f0

        def crash_case(label, setup, op, how, n, roll, craft=False):
            cases[0] += 1
            p = fresh(label)
            setup(p)
            base, _ = census(p)
            if craft:
                base[(u"Weapon_Sword_Mithril", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 22)).toJson()))] = 1
            before = W.snap(p)
            if how == "at":
                Tx.CRASH_AT = n
            elif how == "save":
                Tx.CRASH_AFTER_SAVE = True
            else:
                Store.CRASH_FILES = n
            died = False
            res = ""
            try:
                res = op(p)
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE, Store.CRASH_FILES = -1, False, -1
            if not died:
                return "nodie"
            if roll:
                W.restore(p, before)
            restart()
            r = run(p, 5)
            c, d = census(p)
            if craft and roll is False and c != base:
                pass
            bad = once(p, d)
            ok = c == base and not bad and jresolved(str(p.u)) and not d.bad
            if not ok:
                crash_fail.append("%s %s=%d roll=%s: repair %s; census diff %s; once %s" % (label, how, n, roll, r,
                                  {k_: (base.get(k_), c.get(k_)) for k_ in set(base) | set(c) if base.get(k_) != c.get(k_)}, bad))
            return "ok" if ok else "bad"

        for label, setup, op, craft in (("eq1", setup_equip, op_equip1, False), ("eq2", setup_equip2, op_equip2, False), ("depall", setup_dep, op_depall, False),
                                        ("take", setup_take, op_take, False), ("takekind", setup_take, op_takekind, False), ("fetch", setup_take, op_fetch, False),
                                        ("ret", setup_ret, op_ret, False), ("craft", lambda p: None, op_craft, True)):
            nm, nf = count_points(setup, op)
            for roll in (False, True):
                res_ = [crash_case(label, setup, op, "at", n, roll, craft) for n in range(nm + 1)]
                res_.append(crash_case(label, setup, op, "save", 0, roll, craft))
                res_ += [crash_case(label, setup, op, "files", f, roll, craft) for f in range(nf)]
                if "nodie" in res_:
                    crash_fail.append("%s roll=%s: a crash point did not fire (%s)" % (label, roll, res_))
            K.notes.append("X12 %s: %d move points + after the save + %d file points, x2 (live as-is / rolled back)" % (label, nm, nf))
        K.check(not crash_fail, "X12 a crash after every move, mid-save after every file and after the save, live as-is and rolled back (%d cases): every item exactly once, the journal resolved: %s" % (cases[0], crash_fail[:4]))

        # chained changes inside one journal window (deposit, equip, take out), then a crash with the live inventory rolled back to before the first
        Ch = fresh("chain")
        setup_equip(Ch)
        base, _ = census(Ch)
        snapCh = W.snap(Ch)
        gap()
        run(Ch, 1, 0)
        setc(Ch.sto, 20, stack("Weapon_Bow_Wood", 1))
        run(Ch, 6, 0, "2:20")
        run(Ch, 8, 0, str(ent_by_id(Store.get(str(Ch.u), Ch.u), "Weapon_Bow_Wood")[0].eid))
        jC = json.load(open(os.path.join(Wd, "requip", str(Ch.u), "journal.json")))
        n_steps = len(jC["steps"])
        Tx.CRASH_AFTER_SAVE = True
        try:
            gap()
            run(Ch, 1, 1)
        except Exception:
            pass
        Tx.CRASH_AFTER_SAVE = False
        W.restore(Ch, snapCh)
        restart()
        r = run(Ch, 5)
        c, d = census(Ch)
        exp = dict(base)
        exp[("Weapon_Bow_Wood", "")] = 1
        K.check(n_steps >= 4 and c == exp and not once(Ch, d), "X12 CHAINED: %d steps in one journal + a crashed Equip, the live inventory rolled back before them all: every item once (%s; diff %s; once %s)"
                % (n_steps, r, {k_: (exp.get(k_), c.get(k_)) for k_ in set(exp) | set(c) if exp.get(k_) != c.get(k_)}, once(Ch, d)))
        # profile switch: a journal of profile 1 is never repaired against profile 2's inventory
        Pp = fresh("prof")
        state.setdefault("key", {})[str(Pp.u)] = str(Pp.u) + "-p1"
        setc(Pp.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 4)))
        setc(Pp.sto, 1, stack("Armor_Iron_Head", 1))
        run(Pp, 7)
        inv1 = W.snap(Pp)
        base1, _ = census(Pp, str(Pp.u) + "-p1")
        W.clear(Pp)
        setc(Pp.sto, 0, stack("Weapon_Bow_Wood", 1))
        state["key"][str(Pp.u)] = str(Pp.u) + "-p2"
        restart()
        r2 = run(Pp, 5)
        K.check(r2 == "=Nothing to repair." and os.path.isfile(os.path.join(Wd, "requip", str(Pp.u) + "-p1", "journal.json")), "X12 profile 2 active: profile 1's journal is left alone (%s)" % r2)
        W.clear(Pp)
        W.restore(Pp, inv1)
        state["key"][str(Pp.u)] = str(Pp.u) + "-p1"
        r1 = run(Pp, 5)
        c1, d1 = census(Pp, str(Pp.u) + "-p1")
        K.check(r1.startswith("=An interrupted Requip change") and c1 == base1 and not once(Pp, d1), "X12 back on profile 1: its journal is reconciled with ITS inventory (%s)" % r1)
        del state["key"][str(Pp.u)]

        # ============================================================ X13 random-operation FUZZ (invariant after every op and every crash)
        # requip021: the --seed run + seed 4242 (the phantom NOT WITH YOU after take out -> deposit -> take out -> crash) + 20 more seeds
        fz_seeds = [(s_, False, int(arg("--fuzz", "260"))) for s_ in [SEED] + [s_ for s_ in FUZZ_SEEDS if s_ != SEED]] + [(s_, True, n_) for s_, n_ in COLLIDE_SEEDS]
        for fz_seed, collide, fz_ops in fz_seeds:
            rnd = random.Random(fz_seed)
            Z = fresh("fuzz")
            kZ = str(Z.u)
            pool_ids = ["Armor_Iron_Head", "Armor_Iron_Chest", "Armor_Iron_Hands", "Armor_Iron_Legs", "Armor_Copper_Head", "Armor_Copper_Chest", "Armor_Copper_Legs",
                        "Weapon_Sword_Iron", "Weapon_Sword_Mithril", "Weapon_Bow_Wood", "Tool_Pickaxe_Iron", "Tool_Hatchet_Iron"]
            # requip021fix: COLLIDING-KIND = many identical items (same id + same metadata) - lineages, merges and put-backs of twins
            # (its own list: pool_ids is used again by X15)
            fz_ids = ["Armor_Iron_Legs", "Armor_Iron_Head", "Weapon_Sword_Iron"] if collide else pool_ids
            for i in range(14):
                setc(Z.sto, i, stack(fz_ids[i % len(fz_ids)], 1, gdoc("rare", 7) if collide else gdoc(rnd.choice(["rare", "unique", "normal"]), rnd.randint(1, 50))))
            setc(Z.sto, 14, stack("Potion_Health", 12))
            setc(Z.sto, 15, stack("Food_Bread", 9))
            setc(Z.sto, 16, stack("Rock_Stone", 30))
            expect, _ = census(Z)
            engine = W.snap(Z)
            Cfg.SETTLE_S = 0
            state["bagRoom"] = 0
            log_ = []
            hist_ = []
            fz_fail = []
            crashes = 0
            engine_step = -1
            fallback = []
            for step in range(fz_ops):
                d = Store.get(kZ, Z.u)
                ops_ = ["dep", "depall", "take", "fetch", "pick", "pick", "pick", "equip", "equip", "wear", "craft", "save", "ret", "shuffle", "auto"]
                o = rnd.choice(ops_)
                # fixer 2 (data critic): failing saves (1-3 in a row: the put-back + kept-journal paths) on any op
                if rnd.random() < 0.1:
                    Store.FAIL_NEXT = rnd.randint(1, 3)
                crash = rnd.random() < 0.12
                if crash:
                    how = rnd.choice(["at", "at", "save", "files"])
                    if how == "at":
                        Tx.CRASH_AT = rnd.randint(0, 6)
                    elif how == "save":
                        Tx.CRASH_AFTER_SAVE = True
                    else:
                        Store.CRASH_FILES = rnd.randint(0, 3)
                died = False
                res = ""
                try:
                    if o == "dep":
                        slots = [(s_, i) for s_ in (1, 2, 3) for i in range(int(Z.secs[s_].getCapacity())) if getc(Z.secs[s_], i) is not None]
                        if slots:
                            s_, i = rnd.choice(slots)
                            res = run(Z, 6, 0, "%d:%d" % (s_, i))
                    elif o == "depall":
                        res = run(Z, 7)
                    elif o in ("take", "fetch"):
                        ins = [e for e in d.entries.values() if ein(e) and (not e.kind or o == "take") and (e.kind is False or e.count > 0)]
                        if ins:
                            res = run(Z, 8 if o == "take" else 14, 0, str(rnd.choice(ins).eid))
                    elif o == "pick":
                        n = rnd.randint(0, 3)
                        k_ = rnd.randint(0, 12)
                        cand = [e for e in d.entries.values() if (k_ < 4 and not e.kind and e.space == 0 and e.spot == k_) or (k_ >= 4 and e.space == 1)]
                        choice = rnd.random()
                        if choice < 0.15:
                            res = run(Z, 10, n, "%d|keep" % k_)
                        elif choice < 0.3:
                            res = run(Z, 10, n, "%d|empty" % k_)
                        elif cand:
                            e = rnd.choice(cand)
                            res = run(Z, 10, n, "%d|%s:%s" % (k_, "k" if e.kind else "e", e.eid))
                    elif o == "equip":
                        gap()
                        res = run(Z, 1, rnd.randint(0, 3))
                    elif o == "wear":
                        res = run(Z, 12, rnd.randint(0, 3))
                    elif o == "craft":
                        res = str(Ops.craft(Z.pr, Z.ref, Z.st, stack("Weapon_Bow_Wood", 1, gdoc("rare", 60 + step)), "fuzz", ""))
                        if res.startswith("eid:"):
                            expect[("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))] = 1
                    elif o == "save":
                        # time passes: the engine saves the player, the journal keep window ends
                        engine = W.snap(Z)
                        engine_step = step
                        old_k = Cfg.JKEEP_S
                        Cfg.JKEEP_S = 0
                        Jr.sweep(int(time.time() * 1000) + 1000)
                        Cfg.JKEEP_S = old_k
                    elif o == "ret":
                        res = run(Z, 13)
                    elif o == "shuffle":
                        # the player moves stacks around inside the inventory (no Requip involved)
                        sl_ = [(s_, i) for s_ in (1, 2, 3) for i in range(int(Z.secs[s_].getCapacity()))]
                        (s1, i1), (s2, i2) = rnd.sample(sl_, 2)
                        x1, x2 = getc(Z.secs[s1], i1), getc(Z.secs[s2], i2)
                        if x1 is not None:
                            Z.secs[s1].removeItemStackFromSlot(JShort(i1), False)
                        if x2 is not None:
                            Z.secs[s2].removeItemStackFromSlot(JShort(i2), False)
                        if x1 is not None:
                            setc(Z.secs[s2], i2, x1)
                        if x2 is not None:
                            setc(Z.secs[s1], i1, x2)
                        res = "shuffled"
                    elif o == "auto":
                        Auto.ON.put(kZ, True)
                        Auto.LASTRUN.clear()
                        try:
                            P("WdAutoTask")(Z.u).run()
                        finally:
                            Auto.ON.remove(kZ)
                        res = "auto"
                except Exception as ex_:
                    died = "harness crash" in str(ex_)
                    if not died:
                        fz_fail.append("step %d %s raised %s" % (step, o, ex_))
                Tx.CRASH_AT, Tx.CRASH_AFTER_SAVE, Store.CRASH_FILES = -1, False, -1
                Store.FAIL_NEXT = 0
                if o == "craft" and not died and str(res).startswith("refused:"):
                    # the caller (SkyyGear) keeps a refused crafted item: it falls back to the inventory
                    fr = [i for i in range(int(Z.sto.getCapacity())) if getc(Z.sto, i) is None]
                    if fr:
                        setc(Z.sto, fr[0], stack("Weapon_Bow_Wood", 1, gdoc("rare", 60 + step)))
                        expect[("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))] = 1
                        fallback.append((("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson())), step))
                if o == "craft" and died:
                    # a craft that died before its journal step could not have taken materials (none here): it may or may not have landed
                    pass
                rolled = False
                rolled_from = engine_step
                if died:
                    crashes += 1
                    if rnd.random() < 0.5:
                        W.restore(Z, engine)
                        rolled = True
                    restart()
                    jz = os.path.join(Wd, "requip", kZ, "journal.json")
                    if os.path.isfile(jz):
                        shutil.copy(jz, os.path.join(SCRATCH, "fz-%d-%d.json" % (fz_seed, step)))
                    live_dump = W.dump(Z, Codec)
                    res = "CRASH -> " + run(Z, 5)
                    engine = W.snap(Z)
                    engine_step = step
                c, dz = census(Z)
                bad = once(Z, dz)
                # a refused craft the caller gave to the inventory AFTER the engine last saved the player: a rollback undoes that give too (and,
                # in game, the materials it cost) - not Requip's item
                if rolled:
                    for kk_, st_ in fallback:
                        if st_ > rolled_from and c.get(kk_, 0) == 0 and expect.get(kk_) == 1:
                            del expect[kk_]
                # a craft that crashed: the repair keeps the crafted entry (no material evidence) or the craft never journaled
                if o == "craft" and died and c != expect:
                    kk = ("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 60 + step)).toJson()))
                    if c.get(kk, 0) == 0 and expect.get(kk) == 1:
                        del expect[kk]
                    elif c.get(kk, 0) == 1 and expect.get(kk) is None:
                        expect[kk] = 1
                if (c != expect or bad) and died:
                    json.dump(live_dump, open(os.path.join(SCRATCH, "fz-%d-%d-live.json" % (fz_seed, step)), "w"))
                if c != expect or bad:
                    fz_fail.append("step %d %s%s: %s; before %s; diff %s; once %s" % (step, o, " (crash)" if died else "", res, hist_[-3:],
                                    {k_: (expect.get(k_), c.get(k_)) for k_ in set(expect) | set(c) if expect.get(k_) != c.get(k_)}, bad))
                    expect = c
                if not died and o != "save" and rnd.random() < 0.3:
                    engine = W.snap(Z)      # the engine saved the player in the MIDDLE of a journal window (a later crash rolls back to here)
                    engine_step = step
                log_.append("%s%s" % (o, "!" if died else ""))
                hist_.append("%d %s %s" % (step, o, str(res)[:70]))
            Cfg.SETTLE_S = 30
            state.pop("bagRoom", None)
            K.check(not fz_fail, "X13 FUZZ%s seed %d: %d random ops (%d crashes, half with the live inventory rolled back), every item exactly once after each: %s" % (" COLLIDING-KIND" if collide else "", fz_seed, len(log_), crashes, fz_fail[:3]))
            K.notes.append(("X13 fuzz%s seed %d ops: " % (" collide" if collide else "", fz_seed)) + " ".join(log_[:80]) + " ...")

        # ============================================================ X13b requip021: LINEAGES in the crash repair (fuzz seed 4242, made exact)
        # an item that was OUT (stamped) when the journal began is deposited, taken out (plain), deposited again (a NEW entry), taken out
        # again; then the server dies. Before the fix the repair counted that one plain item twice and kept the first entry as a phantom
        # NOT WITH YOU. B: the same, but the second entry is fetched (its stamp is in the inventory). C: a journal whose lineage link is
        # wrong (two items in the pool, one lineage): the IN count still follows conservation (the fill-up pass) - nothing is lost.
        def legs_slot(p):
            for s_ in (1, 2, 3):
                for i in range(int(p.secs[s_].getCapacity())):
                    x = getc(p.secs[s_], i)
                    if x is not None and str(x.getItemId()) == "Armor_Iron_Legs":
                        return "%d:%d" % (s_, i)
            return None

        def lin_start(name):
            p = fresh(name)
            setc(p.sto, 0, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
            setc(p.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 3)))
            run(p, 6, 0, "2:0")
            d = Store.get(str(p.u), p.u)
            e0 = str(ent_by_id(d, "Armor_Iron_Legs")[0].eid)
            r = run(p, 14, 0, e0)                       # fetch: the legs are OUT, stamped, in the inventory
            old_k = Cfg.JKEEP_S
            Cfg.JKEEP_S = 0
            Jr.sweep(int(time.time() * 1000) + 1000)    # the keep window ends: the next change starts a NEW journal
            Cfg.JKEEP_S = old_k
            base, _d = census(p)
            return p, e0, base, r

        for case in ("A", "B"):
            p, e0, base, r0 = lin_start("lineage" + case)
            k_ = str(p.u)
            r1 = run(p, 6, 0, legs_slot(p))             # deposit the stamped legs (the entry that was OUT)
            r2 = run(p, 8, 0, e0)                       # Take out: a plain item again, the entry is gone
            r3 = run(p, 6, 0, legs_slot(p))             # deposit again: a NEW entry
            d = Store.get(k_, p.u)
            e1 = [str(e.eid) for e in ent_by_id(d, "Armor_Iron_Legs")]
            r4 = run(p, 8 if case == "A" else 14, 0, e1[0] if e1 else "")   # A: Take out again (plain) / B: fetch (stamped, OUT)
            jx = os.path.isfile(os.path.join(Wd, "requip", k_, "journal.json"))
            restart()                                   # the server dies inside the keep window
            rr = run(p, 5)
            c, d = census(p)
            bad = once(p, d)
            legs = ent_by_id(d, "Armor_Iron_Legs")
            want = [] if case == "A" else [(e1[0] if e1 else "?", False)]
            got = [(str(e.eid), ein(e)) for e in legs]
            K.check(jx and rr.startswith("=An interrupted Requip change") and c == base and not bad and got == want,
                    "X13b lineage %s: OUT legs deposited, taken out, deposited again, %s, crash -> no phantom NOT WITH YOU, every item once "
                    "(%s | %s | %s | %s | %s | entries %s want %s, once %s)" % (case, "taken out again" if case == "A" else "fetched", r1, r2, r3, r4, rr, got, want, bad))

        # C: a lineage link that is wrong (hand-made journal): two plain legs deposited as two new entries, a fake Take out of the first
        # between them links the second to it - both must stay IN (conservation), never one deleted
        p = fresh("lineageC")
        k_ = str(p.u)
        setc(p.sto, 0, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
        setc(p.sto, 1, stack("Armor_Iron_Legs", 1, gdoc("unique", 18)))
        base, _d = census(p)
        rc1 = run(p, 6, 0, "2:0")
        rc2 = run(p, 6, 0, "2:1")
        jp = os.path.join(Wd, "requip", k_, "journal.json")
        okC = os.path.isfile(jp)
        if okC:
            jj = json.load(open(jp))
            okC = len(jj["steps"]) == 2 and len(jj["steps"][0]["moves"]) == 1
            if okC:
                fake = json.loads(json.dumps(jj["steps"][0]))
                fake["op"] = "take"
                m_ = fake["moves"][0]
                m_["t"] = {"$numberInt": "4"}
                m_["del"] = True
                m_["fresh"] = False
                jj["steps"].insert(1, fake)
                json.dump(jj, open(jp, "w"))
        restart()
        rc = run(p, 5)
        c, d = census(p)
        legs = ent_by_id(d, "Armor_Iron_Legs")
        K.check(okC and rc.startswith("=An interrupted Requip change") and c == base and not once(p, d) and len(legs) == 2 and all(ein(e) for e in legs),
                "X13b lineage C: a wrong lineage link never deletes an item the pool must hold - both legs stay IN (%s | %s | %s | %s)" % (rc1, rc2, rc, [(str(e.eid), ein(e)) for e in legs]))

        # ============================================================ X13c requip021fix: "Use what I wear" with a FAILED save (colliding fuzz seed 8030)
        # the worn gear is stamped in place; before the fix a failed save dropped the new entries but left the stamps on the items (a stamp
        # the pool did not know). Now every item is put back exactly as it was; a retry that saves stamps them as usual.
        p = fresh("wearfail")
        k_ = str(p.u)
        setc(p.arm, 3, stack("Armor_Iron_Legs", 1, gdoc("rare", 7)))
        setc(p.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        setc(p.hot, 1, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
        setc(p.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        before_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0), getc(p.hot, 1))]
        base, _d = census(p)
        Store.FAIL_NEXT = 1
        rw = run(p, 12, 0)
        Store.FAIL_NEXT = 0
        c, d = census(p)
        after_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0), getc(p.hot, 1))]
        K.check(rw.startswith("-Could not save") and not stamps_of(p) and not once(p, d) and c == base and after_w == before_w and not [e for e in d.entries.values() if not e.kind],
                "X13c Use what I wear, the save fails: every worn item put back unstamped, exactly as it was, no entry (%s | stamps %s | once %s)" % (rw, stamps_of(p), once(p, d)))
        rw2 = run(p, 12, 0)
        c, d = census(p)
        K.check(rw2.startswith("+") and len(stamps_of(p)) == 3 and not once(p, d) and c == base,
                "X13c ... a retry that saves stamps the worn gear as usual (%s | stamps %s | once %s)" % (rw2, stamps_of(p), once(p, d)))

        # ============================================================ X13d requip022: "Use what I wear" whose save fails HALF WAY (a real I/O error
        # after the armor shard was written, the items shard refuses): the undo puts the worn gear back unstamped AND rewrites the files from the
        # restored memory - after a restart (memory gone) the files hold no OUT record for the legs (before requip022: a phantom NOT WITH YOU).
        # Then the resave itself failing (FAIL_NEXT 2): still put back, the memory is right, the next change saves it.
        p = fresh("wearhalf")
        k_ = str(Store.pkey(p.u))
        setc(p.sto, 0, stack("Armor_Copper_Head", 1, gdoc("rare", 7)))
        setc(p.sto, 1, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
        rd1, rd2 = run(p, 6, 0, "2:0"), run(p, 6, 0, "2:1")     # both shards exist on disk (armor-000, items-000)
        old_k = Cfg.JKEEP_S
        Cfg.JKEEP_S = 0
        Jr.sweep(int(time.time() * 1000) + 1000)
        Cfg.JKEEP_S = old_k
        setc(p.arm, 3, stack("Armor_Iron_Legs", 1, gdoc("rare", 7)))
        setc(p.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        base, _d = census(p)
        before_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0))]
        rqd = os.path.join(Wd, "requip", k_)
        itf = os.path.join(rqd, "items-000.json")
        okD = os.path.isfile(itf) and os.path.isfile(os.path.join(rqd, "armor-000.json"))
        rw = ""
        if okD:
            shutil.move(itf, itf + ".bak")
            os.makedirs(os.path.join(itf, "x"))            # a non-empty folder where the shard goes: its atomic move fails (a real IOException)
            try:
                rw = run(p, 12, 0)
            finally:
                shutil.rmtree(itf, ignore_errors=True)
                shutil.move(itf + ".bak", itf)
                for t_ in (itf + ".tmp",):
                    if os.path.isfile(t_):
                        os.remove(t_)
        after_w = [str(x.toString()) if x is not None else None for x in (getc(p.arm, 3), getc(p.hot, 0))]
        armdisk = json.load(open(os.path.join(rqd, "armor-000.json"))) if okD else {}
        legs_disk = [e_ for e_ in armdisk.get("entries", []) if "Armor_Iron_Legs" in json.dumps(e_)]
        restart()
        c, d = census(p)
        bad = once(p, d)
        K.check(okD and rw.startswith("-Could not save") and after_w == before_w and not stamps_of(p) and not legs_disk and not bad and c == base
                and not ent_by_id(d, "Armor_Iron_Legs") and not ent_by_id(d, "Weapon_Sword_Iron"),
                "X13d Use what I wear, the save fails HALF WAY (armor shard written, items shard refused): worn gear put back unstamped and the "
                "armor shard rewritten - after a restart no phantom record (%s / %s | %s | legs on disk %s | once %s)" % (rd1, rd2, rw, legs_disk, bad))
        Store.FAIL_NEXT = 2
        rw3 = run(p, 12, 0)
        fl = int(Store.FAIL_NEXT)
        Store.FAIL_NEXT = 0
        c, d = census(p)
        K.check(rw3.startswith("-Could not save") and fl == 0 and not stamps_of(p) and not once(p, d) and c == base,
                "X13d ... the save AND the resave fail: still put back unstamped, nothing known only to memory (%s | FAIL_NEXT left %d | once %s)" % (rw3, fl, once(p, d)))
        rw4 = run(p, 12, 0)
        restart()
        c, d = census(p)
        K.check(rw4.startswith("+") and len(stamps_of(p)) == 2 and not once(p, d) and c == base,
                "X13d ... the next try saves and stamps the worn gear, the files agree after a restart (%s | stamps %s | once %s)" % (rw4, stamps_of(p), once(p, d)))

        # ============================================================ X13e requip022fix (critic 1): "Use what I wear" CRASHES part way through its
        # save (the JVM dies; the live inventory kept WITH the new stamps). register.txt names every eid before a stamp goes on; the next Requip
        # action unstamps a listed eid the pool never got. Another player's stamp (not listed) is never touched. Crash after 1, 2, 3, 4 files.
        FOREIGN = "f0e1f0e1f0e1f0e1"
        died_n, heal_ok, rows = 0, True, []
        for cf in range(0, 4):
            p = fresh("wearcrash%d" % cf)
            k_ = str(Store.pkey(p.u))
            setc(p.sto, 0, stack("Armor_Copper_Head", 1, gdoc("rare", 7)))
            setc(p.sto, 1, stack("Weapon_Bow_Wood", 1, gdoc("rare", 9)))
            run(p, 6, 0, "2:0"), run(p, 6, 0, "2:1")          # both shards on disk
            old_k = Cfg.JKEEP_S
            Cfg.JKEEP_S = 0
            Jr.sweep(int(time.time() * 1000) + 1000)
            Cfg.JKEEP_S = old_k
            setc(p.arm, 3, stack("Armor_Iron_Legs", 1, gdoc("rare", 7)))
            setc(p.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
            setc(p.sto, 5, Codec.stamp(stack("Weapon_Sword_Iron", 1, gdoc("rare", 8)), FOREIGN))   # picked up from another player
            base, _d = census(p)
            mkf = os.path.join(Wd, "requip", k_, "register.txt")
            Store.CRASH_FILES = cf
            died = False
            try:
                run(p, 12, 0)
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Store.CRASH_FILES = -1
            mk_at_crash = os.path.isfile(mkf)
            restart()
            rr = run(p, 5)
            c, d = census(p)
            bad = [b_ for b_ in once(p, d) if FOREIGN not in b_]
            st_ = stamps_of(p)
            ok_ = (not died or mk_at_crash) and not bad and c == base and FOREIGN in st_ and not os.path.isfile(mkf)
            heal_ok = heal_ok and ok_
            died_n += 1 if died else 0
            rows.append("crash after %d file(s): died=%s marker=%s stamps=%s bad=%s %s" % (cf + 1, died, mk_at_crash, st_, bad, rr))
        K.check(died_n >= 2 and heal_ok,
                "X13e Use what I wear CRASHES part way through its save: the next Requip action unstamps every listed eid the pool never got, "
                "another player's stamp untouched, nothing lost or copied (%s)" % " / ".join(rows))
        rwf = run(p, 12, 0)
        c, d = census(p)
        bad = [b_ for b_ in once(p, d) if FOREIGN not in b_]
        K.check(rwf.startswith("+") and not bad and c == base and not os.path.isfile(mkf),
                "X13e ... the next Use what I wear saves and stamps as usual, register.txt removed (%s | once %s)" % (rwf, bad))
        # register.txt cannot be written (a folder in its place): nothing stamped, nothing saved, the loadout unchanged
        p = fresh("wearmark")
        k_ = str(Store.pkey(p.u))
        setc(p.arm, 3, stack("Armor_Iron_Legs", 1, gdoc("rare", 7)))
        setc(p.hot, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 7)))
        base, _d = census(p)
        mkf = os.path.join(Wd, "requip", k_, "register.txt")
        os.makedirs(os.path.join(mkf, "x"))
        try:
            rwm = run(p, 12, 0)
        finally:
            shutil.rmtree(mkf, ignore_errors=True)
            if os.path.isfile(mkf + ".tmp"):
                os.remove(mkf + ".tmp")
        c, d = census(p)
        restart()
        c2, d2 = census(p)
        K.check(rwm.startswith("-Could not save") and not stamps_of(p) and not once(p, d) and c == base and c2 == base
                and not [e for e in d2.entries.values() if not e.kind],
                "X13e ... register.txt cannot be written: nothing stamped, no entry, the loadout unchanged (%s | stamps %s)" % (rwm, stamps_of(p)))

        # ============================================================ X14 MIGRATION of 0.1 files (fixtures made by the REAL 0.1 jar in M01)
        fx = os.path.join(SCRATCH, "fx01")
        meta = json.load(open(os.path.join(fx, "meta.json"))) if os.path.isfile(os.path.join(fx, "meta.json")) else None
        K.check(meta is not None, "X14 the M01 fixtures exist (the 0.1 jar ran)")
        lo01 = os.path.join(Wd, "loadouts")
        os.makedirs(lo01, exist_ok=True)

        def census01(f01, live_dump):
            """the items a 0.1 file + a live inventory dump hold (the stamp-free kind keys of the 0.2 census)"""
            tot = {}
            d01 = json.load(open(f01))
            docs = []
            for L_ in d01["loadouts"]:
                docs += L_["armor"] + L_["hotbar"]
            docs += d01["orphans"]
            for sec in live_dump:
                docs += [x for x in sec if x is not None]
            for x in docs:
                s_ = Codec.stackOf(JClass("org.bson.BsonDocument").parse(json.dumps(x)))
                kk = ukey(s_)
                tot[kk] = tot.get(kk, 0) + int(s_.getQuantity())
            return tot
        if meta:
            # ---- A: stored loadout 1 (armor + sword + potion + a block + a bag + armor in a hotbar slot), loadout 2 EQUIPPED, an orphan
            kA1 = meta["A"]["key"]
            src = os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kA1 + ".json")
            shutil.copy(src, os.path.join(lo01, kA1 + ".json"))
            raw01 = open(os.path.join(lo01, kA1 + ".json"), "rb").read()
            Mi = W.player(kA1, "Ann")
            W.load(Mi, meta["A"]["live"], Codec)
            exp01 = census01(os.path.join(lo01, kA1 + ".json"), meta["A"]["live"])
            restart()
            dM = Store.get(kA1, Mi.u)
            K.check(dM.mig == 1 and not dM.exists, "X14 a key with a 0.1 file and no Requip folder waits for its migration")
            r = run(Mi, 5)
            dM = Store.get(kA1, Mi.u)
            cM, dMf = census(Mi)
            K.check(dM.mig == 0 and dMf.migrated is not None and "0.1 rev" in str(dMf.migrated) and cM == exp01 and not once(Mi, dMf),
                    "X14 A migrated on the first load: every 0.1 stack is in the pool or a Returned item, nothing lost or doubled (%s; %s)" % (r, dMf.migrated))
            L1, L2 = dMf.slots[0], dMf.slots[1]
            pk1 = [str(x)[:2] if x is not None else None for x in L1.picks]
            K.check(str(L1.name) == "Combat" and pk1[:4] == ["e:"] * 4 and pk1[4] == "e:" and pk1[5] == "k:" and pk1[6] is None and pk1[7] is None and pk1[8] is None
                    and L1.hasPets and str(L1.pet) == "petA" and "Priest" in str(L1.abil), "X14 loadout 1: name, pets, abilities kept; picks point at the new entries; block / bag / misplaced armor = Keep (%s)" % pk1)
            K.check(L2.hasPets and str(L2.pet) == "petB" and L2.picked() == 0 and dMf.lastWorn == 1 and dMf.ask01 == 1,
                    "X14 the EQUIPPED loadout 2: pets kept, Keep everywhere (its gear stays on you), asked once (ask01)")
            rets = [str(Codec.stackOf(o.asDocument()).getItemId()) for o in dMf.orphans]
            K.check(sorted(rets) == ["Backpack_Test", "Rock_Stone"] and len(ent_by_id(dMf, "Armor_Gold_Head")) == 1 and len(ent_by_id(dMf, "Weapon_Bow_Wood")) == 1,
                    "X14 refused 0.1 stacks (the block, the bag) became Returned items; the misplaced helmet + the 0.1 orphan bow became pool entries (%s)" % rets)
            K.check(open(os.path.join(lo01, kA1 + ".json"), "rb").read() == raw01 and open(os.path.join(Wd, "requip", kA1, "from01", kA1 + ".json"), "rb").read() == raw01,
                    "X14 the 0.1 file is untouched; the History snapshot holds its exact bytes")
            restart()
            dM2 = Store.get(kA1, Mi.u)
            r2 = run(Mi, 5)
            cM2, dM3 = census(Mi)
            K.check(dM2.mig == 0 and r2 == "=Nothing to repair." and cM2 == exp01 and len(dM3.entries) == len(dMf.entries), "X14 RUN ONCE: a restart does not migrate again")
            # the 0.1 question: "Use what you wear for Loadout 2?" -> registered in place
            r = run(Mi, 12, 1)
            dM = Store.get(kA1, Mi.u)
            cM, dMf = census(Mi)
            K.check("Loadout 2 now uses what you wear" in r and dM.ask01 == -1 and dM.slots[1].picked() >= 3 and cM == exp01 and not once(Mi, dMf),
                    "X14 Yes = Use what I wear for the old equipped loadout: picked in place, asked no more (%s)" % r)
            r = run(Mi, 13)
            r2 = run(Mi, 13)
            r3 = run(Mi, 13)
            cM, dMf = census(Mi)
            K.check(r.startswith("+Returned item") and r2.startswith("+Returned item") and r3 == "=There are no returned items." and dMf.orphans.size() == 0
                    and cM == exp01, "X14 Returned items come out one per click (%s / %s / %s)" % (r, r2, r3))
            # ---- B: a PENDING 0.1 journal (a crashed 0.1 equip): repaired FIRST against the live inventory, then migrated
            kB1 = meta["B"]["key"]
            for ext in (".json", ".journal.json"):
                shutil.copy(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ext), os.path.join(lo01, kB1 + ext))
            Mb = W.player(kB1, "Bo")
            for roll in (False, True):
                W.load(Mb, meta["B"]["live"], Codec)
                if roll:
                    # the engine rolled the inventory back to before the 0.1 equip: copper head + bow worn, nothing of loadout 1
                    W.clear(Mb)
                    setc(Mb.arm, 0, stack("Armor_Copper_Head", 1))
                    setc(Mb.hot, 0, stack("Weapon_Bow_Wood", 1))
                shutil.rmtree(os.path.join(Wd, "requip", kB1), ignore_errors=True)
                restart()
                r = run(Mb, 5)
                cB1, dB1 = census(Mb)
                j01 = json.load(open(os.path.join(lo01, kB1 + ".journal.json")))
                exp = {("Armor_Gold_Head", str(JClass("org.bson.BsonDocument").parse(gdoc("fabled", 30)).toJson())): 1,
                       ("Weapon_Sword_Mithril", str(JClass("org.bson.BsonDocument").parse(gdoc("mythic", 40)).toJson())): 1,
                       ("Food_Bread", ""): 7, ("Armor_Copper_Head", ""): 1, ("Weapon_Bow_Wood", ""): 1}
                K.check(cB1 == exp and not once(Mb, dB1) and "0.1 journal repaired first" in str(dB1.migrated) and j01["stage"] == "moving",
                        "X14 B (live %s): the pending 0.1 journal was repaired FIRST (in memory), every item once; the 0.1 journal file untouched (%s; %s; diff %s)"
                        % ("rolled back" if roll else "as at the crash", r, dB1.migrated, {k_: (exp.get(k_), cB1.get(k_)) for k_ in set(exp) | set(cB1) if exp.get(k_) != cB1.get(k_)}))
            # ---- C: a FAILED 0.1 journal keeps the profile shut until /requipadmin repair
            kC1 = "00000000-0000-0000-0000-0000000001c3"
            shutil.copy(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ".json"), os.path.join(lo01, kC1 + ".json"))
            jf_ = json.load(open(os.path.join(fx, "mods", "Skyy_SkyyWardrobe", "loadouts", kB1 + ".journal.json")))
            jf_["stage"] = "failed"
            json.dump(jf_, open(os.path.join(lo01, kC1 + ".journal.json"), "w"))
            Mc = W.player(kC1, "Cid")
            W.load(Mc, meta["B"]["live"], Codec)
            restart()
            r = run(Mc, 6, 0, "1:0")
            dC1 = Store.get(kC1, Mc.u)
            K.check(r.startswith("-An interrupted 0.1 loadout change must be checked first") and dC1.bad and not os.path.isfile(os.path.join(Wd, "requip", kC1, "index.json")),
                    "X14 a FAILED 0.1 journal: Requip stays shut, nothing migrated (%s)" % r)
            P("WdRepairTask")(Mc.u, 0, True, None).run()
            cC1, dC1 = census(Mc)
            K.check(not dC1.bad and dC1.migrated is not None and not once(Mc, dC1) and cC1 == exp, "X14 /requipadmin repair: the failed 0.1 journal is repaired, then migrated (%s)" % dC1.migrated)
            # ---- D: a crash in the middle of the FIRST save of a migration: leftovers moved aside, migrated again, nothing doubled
            kD1 = "00000000-0000-0000-0000-0000000001d4"
            shutil.copy(src, os.path.join(lo01, kD1 + ".json"))
            Md = W.player(kD1, "Dee")
            W.load(Md, meta["A"]["live"], Codec)
            expD = census01(os.path.join(lo01, kD1 + ".json"), meta["A"]["live"])
            restart()
            Store.CRASH_FILES = 2
            died = False
            try:
                run(Md, 5)
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Store.CRASH_FILES = -1
            left = sorted(os.listdir(os.path.join(Wd, "requip", kD1)))
            restart()
            r = run(Md, 5)
            cD1, dD1 = census(Md)
            stale = [n_ for n_ in os.listdir(os.path.join(Wd, "requip", kD1)) if n_.startswith("stale-")]
            K.check(died and "index.json" not in left and stale and cD1 == expD and not once(Md, dD1) and dD1.migrated is not None,
                    "X14 a crash mid-way through the migration's first save: no index.json, so the next load moves the half files aside and migrates again (%s -> %s, %s)" % (left, stale, r))
            # ---- E: the REAL live 0.1 file (a scratch COPY, read only)
            live01 = os.path.join(LIVE, "Skyy_SkyyWardrobe", "loadouts")
            n_live = 0
            if os.path.isdir(live01):
                for f in sorted(os.listdir(live01)):
                    if not f.endswith(".json") or f.endswith(".journal.json"):
                        continue
                    k_ = f[:-5]
                    shutil.copy(os.path.join(live01, f), os.path.join(lo01, f))
                    uid = k_[:36]
                    state.setdefault("key", {})[uid] = k_
                    Ml = W.player(uid, "Skyy")
                    restart()
                    r = run(Ml, 5)
                    dL = Store.load(k_, uid)
                    j_ = json.load(open(os.path.join(live01, f)))
                    K.check(dL.migrated is not None and not dL.bad and dL.lastWorn == jn(j_["worn"]) and dL.ask01 == jn(j_["worn"]),
                            "X14 the live 0.1 file %s (copy) migrates: equipped loadout %d asked once, %d entries (%s)" % (f, jn(j_["worn"]) + 1, len(dL.entries), r))
                    del state["key"][uid]
                    n_live += 1
            K.notes.append("X14 live 0.1 files migrated (copies): %d" % n_live)

        # ============================================================ X15 files: unreadable / newer (shut, never written), shards, caps
        Fs = W.player("00000000-0000-0000-0000-000000000015", "Fil")
        kFs = str(Fs.u)
        Cfg.SHARD_RUN = 25
        for i in range(36):
            setc(Fs.sto, i, stack(pool_ids[i % len(pool_ids)], 1, gdoc("rare", i + 1)))
        r = run(Fs, 7)
        for i in range(30):
            setc(Fs.sto, i, stack("Weapon_Sword_Iron", 1, gdoc("unique", 100 + i)))
        r2 = run(Fs, 7)
        files = sorted(n_ for n_ in os.listdir(os.path.join(Wd, "requip", kFs)) if n_.startswith(("armor-", "items-")))
        K.check(r.startswith("+Deposited 36") and r2.startswith("+Deposited 30") and files == ["armor-000.json", "items-000.json", "items-001.json"],
                "X15 shards of 25 (pool.shardSize): 21 armor -> 1 file, 45 items -> 2 files (%s)" % files)
        sz = {n_: len(json.load(open(os.path.join(Wd, "requip", kFs, n_)))["entries"]) for n_ in files}
        K.check(sz == {"armor-000.json": 21, "items-000.json": 25, "items-001.json": 20}, "X15 ... filled in order (%s)" % sz)
        mt = {n_: os.path.getmtime(os.path.join(Wd, "requip", kFs, n_)) for n_ in files}
        time.sleep(0.05)
        f0 = int(Store.FILES)
        last = [e for e in Store.get(kFs, Fs.u).entries.values() if e.shard == 1 and e.space == 1][0]
        r = run(Fs, 14, 0, str(last.eid))
        mt2 = {n_: os.path.getmtime(os.path.join(Wd, "requip", kFs, n_)) for n_ in files}
        K.check(r == "+ok" and int(Store.FILES) - f0 == 2 and [n_ for n_ in files if mt2[n_] != mt[n_]] == ["items-001.json"],
                "X15 a change rewrites ONLY the shard it touches (+ index.json) (%s)" % [n_ for n_ in files if mt2[n_] != mt[n_]])
        restart()
        d15 = Store.get(kFs, Fs.u)
        K.check(d15.count(0) == 21 and d15.count(1) == 45 and not d15.bad, "X15 reload: every shard read back")
        Cfg.SHARD_RUN = 0
        Cfg.ITEMS_CAP = 40
        setc(Fs.sto, 35, stack("Weapon_Bow_Wood", 1))
        r = run(Fs, 6, 0, "2:35")
        restart()
        K.check(r.startswith("-Items space full (40)") and Store.get(kFs, Fs.u).count(1) == 45, "X15 a cap LOWER than the space: deposits refused, nothing deleted (%s)" % r)
        Cfg.ITEMS_CAP = 1000
        # unreadable shard / newer format: shut, never written over
        sh = os.path.join(Wd, "requip", kFs, "items-001.json")
        good = open(sh, "rb").read()
        open(sh, "wb").write(b"{ not json")
        restart()
        r = run(Fs, 6, 0, "2:35")
        d15 = Store.get(kFs, Fs.u)
        K.check(d15.bad and r.startswith("-Your Requip files could not be read") and open(sh, "rb").read() == b"{ not json", "X15 an unreadable shard: Requip shut, the file never written over (%s)" % r)
        ix = os.path.join(Wd, "requip", kFs, "index.json")
        ixb = open(ix, "rb").read()
        open(sh, "wb").write(good)
        open(ix, "w").write(json.dumps({"format": 3, "rev": 1}))
        restart()
        r = run(Fs, 6, 0, "2:35")
        K.check(Store.get(kFs, Fs.u).bad and "format 3" in r and json.load(open(ix))["format"] == 3, "X15 a NEWER format: shut, not written (%s)" % r)
        open(ix, "wb").write(ixb)
        restart()
        r = run(Fs, 6, 0, "2:35")
        K.check(r.startswith("+Into Requip") and not Store.get(kFs, Fs.u).bad, "X15 fixed by hand (+ reload): open again (%s)" % r)
        r = str(P("WdCmds").admin(None, JArray(JString)(["reload"])))
        K.check(r.startswith("+Reloaded:"), "X15 /requipadmin reload")

        # ============================================================ X16 THE PAGE (real builders, every view, every click)
        TP = JClass(FAKE_PKG + ".TestPage")
        UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
        Pg = W.player("00000000-0000-0000-0000-000000000016", "Pia")
        kPg = str(Pg.u)
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Copper_Head", "Armor_Iron_Chest", "Weapon_Sword_Iron", "Weapon_Sword_Mithril"]):
            setc(Pg.sto, i, stack(a, 1, gdoc(["rare", "unique", "normal", "legendary", "mythic"][i], 5 * i)))
        setc(Pg.sto, 5, stack("Potion_Health", 9))
        setc(Pg.sto, 6, stack("Rock_Stone", 9))
        setc(Pg.hot, 8, stack("Skyy_Menu", 1))
        run(Pg, 7)
        setc(Pg.sto, 10, stack("Weapon_Bow_Wood", 1))
        br.put("profile:name:" + kPg, "Fox")
        pg = TP(Pg.pr)

        def build():
            b, ev = UCB(), UEB()
            pg.build(Pg.ref, b, ev, Pg.st)
            cmds_ = list(b.getCommands())
            text = " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in cmds_)
            return text, list(ev.getEvents())

        def click(a, **kw):
            d_ = {"a": a, "t": str(pg.tok)}
            d_.update(kw)
            pg.handleDataEvent(Pg.ref, Pg.st, json.dumps(d_))
            return str(pg.info)

        text, evs = build()
        K.check("Profile Fox" in text and "Armor 3 / 1000" in text and "Items 3 / 1000" in text and "Loadouts 0 of 4" in text and "#SkyyRqL4" in text
                and "#SkyyRqL5" not in text, "X16 the head line + 4 open loadouts and the next locked one")
        K.check('ItemId: ""' not in text and not [m for m in re.findall(r"#(SkyyRq\w+)", text) if "_" in m], "X16 no empty ItemId (no client warning), no underscore in any element id")
        K.check("ItemGridSlot" not in text and "Auto-store: OFF" in text, "X16 icons only (no ItemGridSlot), auto-store shows OFF")
        r = click("sl", i="0")
        text, evs = build()
        K.check(pg.slot == 0 and pg.view == 0 and "Head pieces - click one to pick it" in text and "Selected: Head" in text, "X16 click the Head slot: the Armor space shows Head pieces")
        ihead = [c for c in pg.cells if c]
        K.check(len(ihead) == 2, "X16 ... exactly the 2 helmets (%s)" % ihead)
        r = click("pc", i="0")
        K.check(r.startswith("+Loadout 1: Head takes"), "X16 click a pool item with a slot selected = pick it (%s)" % r)
        build()
        r = click("sl", i="4")
        build()
        K.check(pg.view == 4 and len([c for c in pg.cells if c]) == 2, "X16 a hotbar slot (Keep) opens the WEAPONS tab: the 2 swords (0.2.2)")
        r = click("tab", v="1")
        build()
        K.check(pg.view == 1 and pg.slot == 4 and len([c for c in pg.cells if c]) == 1, "X16 ... the potion kind is on the Items tab; Hotbar 1 stays selected (0.2.2)")
        r = click("pk", v="empty")
        K.check(r.startswith("+Loadout 1: Hotbar 1 goes into Requip"), "X16 Empty (%s)" % r)
        build()
        r = click("pk", v="keep")
        build()
        # FIX2-F2 (fidelity critic 2): Pocket with no block held there shows the blocks in your Magic Bags; a click picks one
        state.setdefault("bags", {})[str(Pg.u)] = {"Rock_Stone": 120, "Ingredient_Bar_Iron": 0, "Weapon_Sword_Iron": 3}
        hb0 = getc(Pg.hot, 0)
        if hb0 is not None:
            Pg.hot.removeItemStackFromSlot(JShort(0), False)
        r = click("pk", v="pocket")
        text, evs = build()
        cellsP = [c for c in pg.cells if c]
        K.check(pg.view == 3 and r.startswith("=Click a block from your Magic Bags") and cellsP == ["b:Rock_Stone"] and "Blocks in your Magic Bags - click one for Hotbar 1" in text
                and "Pocket blocks" in text, "FIX2-F2 Pocket with nothing held: the page lists the BLOCKS in your Magic Bags (not the sword, not a 0 count) (%s / %s)" % (r, cellsP))
        r = click("pc", i="0")
        text, evs = build()
        pk4 = Store.get(str(Store.pkey(Pg.u)), Pg.u).slots[pg.sel].picks[4]
        K.check(r.startswith("+Loadout 1: Hotbar 1 fills with Rock_Stone") and pg.view == 1 and str(pk4) == "p:Rock_Stone:0",
                "FIX2-F2 ... a click on a bag block makes it the pocket pick, no block held (%s, %s)" % (r, pk4))
        r = click("pk", v="keep")
        build()
        if hb0 is not None:
            setc(Pg.hot, 0, hb0)
        click("tab", v="4")
        build()
        r = click("so")
        text, evs = build()
        K.check(pg.sort == 1 and "Sort: rarity" in text, "X16 sort cycles (rarity)")
        r = click("q", **{"@RqQ": "mithril"})
        text, evs = build()
        K.check(len([c for c in pg.cells if c]) == 1 and "search: mithril" in text, "X16 search by id")
        click("q", **{"@RqQ": "sword mithril"})
        build()
        n1 = len([c for c in pg.cells if c])
        click("q", **{"@RqQ": "Sword_Mithril"})
        build()
        K.check(n1 == 1 and len([c for c in pg.cells if c]) == 1, "FIX-F3 search matches the readable name the page shows (sword mithril) as well as the id")
        r = click("qc")
        build()
        r = click("tab", v="2")
        text, evs = build()
        K.check(pg.view == 2 and pg.slot == -1 and "Your hotbar (top row) and storage" in text and "#SkyyRqP15Out" in text, "X16 Your inventory: page 1 = hotbar + storage; the refused block is covered")
        bow_cell = 9 + 10
        K.check(str(pg.cells[bow_cell]) == "s2:10:Weapon_Bow_Wood", "FIX-E3 an inventory cell remembers the item it showed (%s)" % pg.cells[bow_cell])
        setc(Pg.sto, 10, stack("Tool_Pickaxe_Iron", 1))
        r0 = click("pc", i=str(bow_cell))
        K.check(r0.startswith("-That slot changed - here it is again.") and str(getc(Pg.sto, 10).getItemId()) == "Tool_Pickaxe_Iron",
                "FIX-E3 a click on a cell whose slot changed since the page was drawn deposits NOTHING (%s)" % r0)
        setc(Pg.sto, 10, stack("Weapon_Bow_Wood", 1))
        build()
        r = click("pc", i=str(bow_cell))
        K.check(r.startswith("+Into Requip: Weapon_Bow_Wood"), "X16 click an inventory item = deposit (%s)" % r)
        build()
        r = click("pc", i="8")
        K.check(r.startswith("-The SkyWynn Menu item"), "X16 the menu item refuses with its reason (%s)" % r)
        build()
        text, evs = build()
        K.check("then your worn armor and backpack" in text and "#SkyyRqP89" in text and "#SkyyRqPv" not in text and "#SkyyRqNx" not in text
                and "Scroll down for your worn armor and backpack" in text, "X16 (0.2.5) Your inventory = ONE scrolling grid: hotbar + storage, then worn armor + backpack (cells 45-89), no pager")
        click("tab", v="4")
        build()
        swd = [c for c in pg.cells if c][0]
        click("pc", i="0")
        text, evs = build()
        K.check(pg.det == swd and "#SkyyRqDn" in text and "In Requip. Picked in" in text, "X16 click an item without a slot = its details")
        r = click("dt")
        r2 = click("dt")
        K.check(r.startswith("+Taken out") or r.startswith("=Press Take out again"), "X16 Take out (asks twice only when it is picked) (%s / %s)" % (r, r2))
        build()
        r = click("da")
        build()
        click("tab", v="0")
        build()
        click("pc", i="0")
        build()
        r = click("df")
        r2 = click("df")
        K.check(r.startswith("=Press Forget again") and r2.startswith("-It is in Requip"), "X16 Forget asks twice, then refuses an IN entry (%s / %s)" % (r, r2))
        build()
        r = click("rn", **{"@RqName": "Tank"})
        build()
        K.check(str(Store.get(kPg, Pg.u).slots[0].name) == "Tank", "X16 Rename reads the name box (%s)" % r)
        r = click("sv")
        build()
        gap()
        r = click("eq")
        text, evs = build()
        K.check(r.startswith("+Equipped Tank") and "last worn" in text, "X16 Equip from the page (%s)" % r)
        r = click("uw")
        build()
        K.check("now uses what you wear" in r, "X16 Use what I wear from the page (%s)" % r)
        r = click("rs")
        r2 = click("rs")
        build()
        K.check(r.startswith("=Press Reset again") and r2.startswith("+Tank was reset"), "X16 Reset asks twice (%s / %s)" % (r, r2))
        r = click("au")
        text, evs = build()
        K.check(r.startswith("+Auto-store is ON") and "Auto-store: ON" in text, "X16 the auto-store toggle (%s)" % r)
        click("au")
        build()
        dP = Store.get(kPg, Pg.u)
        dP.ask01 = 0
        dP.orphan("test", stack("Weapon_Bow_Wood", 1, gdoc("rare", 99)))
        Store.save(dP)
        text, evs = build()
        K.check("Your old Wardrobe had" in text and "#SkyyRqY1" in text, "X16 the 0.1 question shows Yes / No")
        r = click("n1")
        text, evs = build()
        K.check(Store.get(kPg, Pg.u).ask01 == -1 and "returned item waits" in text and "#SkyyRqRo" in text, "X16 No: asked no more; then the Returned items line (%s)" % r)
        r = click("ro")
        K.check(r.startswith("+Returned item"), "X16 Take one out (%s)" % r)
        build()
        # ============================================================ Z 0.2.2: THE POOL ROWS, the Weapons tab, search + sort per tab, 10 loadouts
        @JImplements("java.util.function.Function")
        class GFn(object):
            def __init__(self, f):
                self.f = f

            @JOverride
            def apply(self, a):
                return self.f(a)

        gcalls = []

        def gdoc_of(a):
            md = a[1]
            return md.get("SkyyGear").asDocument() if md is not None and md.containsKey("SkyyGear") else None

        def g_desc(a):
            gcalls.append(str(a[0]))
            g = gdoc_of(a)
            if g is None:
                return None
            rf = str(g.getString("rf").getValue()) if g.containsKey("rf") else ""
            nm = {"Armor_Iron_Chest": "Iron Chestplate", "Weapon_Sword_Iron": "Iron Sword", "Weapon_Bow_Wood": "Wooden Bow"}.get(str(a[0]), str(a[0]))
            if g.containsKey("nm"):
                nm = str(g.getString("nm").getValue())
            return JArray(JString)([(rf + " " if rf else "") + nm, "Rarity: -"])

        def g_roll(a):
            g = gdoc_of(a)
            if g is None:
                return None
            r_ = str(g.getString("r").getValue())
            mods_ = str(g.getString("mods").getValue()) if g.containsKey("mods") else ""
            return r_.capitalize() + " - Lv " + str(int(g.getInt32("lvl").getValue())) + ((" - " + mods_) if mods_ else "")

        br.put("gear:fn:describe", GFn(g_desc))
        br.put("gear:fn:rollsLine", GFn(g_roll))
        Zp = W.player("00000000-0000-0000-0000-0000000000a2", "Zed")
        kZ = str(Zp.u)
        zitems = [("Armor_Iron_Chest", 1, gdoc("normal", 2)), ("Armor_Iron_Chest", 1, gdoc("normal", 2)),
                  ("Armor_Iron_Chest", 1, '{"SkyyGear": {"v": 1, "r": "rare", "lvl": 2, "id": true, "rf": "Sharp", "mods": "Defence +4"}}'),
                  ("Weapon_Sword_Iron", 1, '{"SkyyGear": {"v": 1, "r": "legendary", "lvl": 7, "id": true, "mods": "Strength +12 - Crit Chance +5%"}}'),
                  ("Weapon_Bow_Wood", 1, gdoc("untiered", 3)), ("Skyy_Spear_Test", 1, '{"SkyyGear": {"v": 1, "r": "normal", "lvl": 1, "id": true, "nm": "Extraordinarily Magnificent Spear Of The Endless Sky Kingdom And Its Seven Realms"}}'),
                  ("Potion_Health", 9, None), ("Tool_Pickaxe_Iron", 1, None), ("Food_Bread", 5, None)]
        for i, (a_, q_, m_) in enumerate(zitems):
            setc(Zp.sto, i, stack(a_, q_, m_) if m_ else stack(a_, q_))
        rz = run(Zp, 7)
        dZ = Store.get(kZ, Zp.u)
        K.check(dZ.count(0) == 3 and dZ.count(1) == 6, "Z the test pool: 3 chests (Armor), sword / bow / spear / potion kind / pickaxe / bread kind (Items space) (%s)" % rz)
        zp = TP(Zp.pr)

        def zbuild(page=None):
            p_ = page or zp
            b, ev = UCB(), UEB()
            p_.build(Zp.ref, b, ev, Zp.st)
            return " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in list(b.getCommands()))

        def zclick(a, page=None, **kw):
            p_ = page or zp
            d_ = {"a": a, "t": str(p_.tok)}
            d_.update(kw)
            p_.handleDataEvent(Zp.ref, Zp.st, json.dumps(d_))
            return str(p_.info)

        def zcells(page=None):
            return [str(c) for c in (page or zp).cells if c]

        def zix(eid):
            l_ = [str(c) for c in zp.cells]
            return l_.index(eid) if eid in l_ else -1

        def zid(eid):
            e_ = Store.get(kZ, Zp.u).entry(eid)
            return str(e_.itemId()) if e_ is not None else "?"

        zbuild()
        zclick("tab", v="0")
        t0 = zbuild()
        K.check("Armor 3" in t0 and "Weapons 3" in t0 and "Items 3" in t0 and "#SkyyRqSub1" in t0 and "Inventory" in t0,
                "Z tabs Armor | Weapons | Items | Inventory with their counts (a mod weapon without the Weapon_ prefix counts as a weapon)")
        ca = zcells()
        K.check(len(ca) == 3 and all(zid(c) == "Armor_Iron_Chest" for c in ca), "Z the Armor tab lists the 3 chests as rows (%s)" % ca)
        K.check("Iron Chestplate  #1" in t0 and "Iron Chestplate  #2" in t0 and "Sharp Iron Chestplate" in t0 and "Sharp Iron Chestplate  #" not in t0,
                "Z rows: SkyyGear's name (+ reforge); the two identical chests are #1 / #2, the different one has no number")
        K.check("Lv 2" in t0 and "Rare - Defence +4" in t0 and "#SkyyRqP0Nm" in t0 and "#SkyyRqP2Sb" in t0 and "#SkyyRqP3Nm" not in t0,
                "Z rows: the Lv tag and the grey line (rarity - modifiers), one row per entry, no empty rows")
        K.check(("TextColor: %s" % SUIC["Rare"]) in t0 and ("TextColor: %s" % SUIC["Normal"]) in t0, "Z the row names are drawn in their rarity colour")
        K.check('ItemId: ""' not in t0 and "ItemGridSlot" not in t0 and not [m for m in re.findall(r"#(SkyyRq\w+)", t0) if "_" in m],
                "Z rows use ItemIcon with a plain id (no ItemGridSlot, no empty id), no underscore in any id")
        ents = sorted([Store.get(kZ, Zp.u).entry(c) for c in ca if "rare" != str(Store.get(kZ, Zp.u).entry(c).rar)], key=lambda e_: (-int(e_.addedAt), str(e_.eid)))
        dZ = Store.get(kZ, Zp.u)
        tw = [int(zp.twinNo(dZ, e_)) for e_ in ents]
        K.check(tw == [1, 2] and t0.index("Iron Chestplate  #1") < t0.index("Iron Chestplate  #2"),
                "Z twins are numbered in the default list order (newest #1, ties by eid): the list reads #1 above #2 (%s)" % tw)
        # fix round: the detail panel and the Take out prompt name a twin as its row does
        twr = [c for c in ca if int(zp.twinNo(Store.get(kZ, Zp.u), Store.get(kZ, Zp.u).entry(c))) == 1][0]
        zclick("pc", i=str(zix(twr)))
        tD = zbuild()
        K.check("Iron Chestplate  #1 - Normal - Lv 2" in tD, "Z the detail panel names the twin as its row does (#1)")
        zclick("sl", i="1")
        zbuild()
        rpk = zclick("pc", i=str(zix(twr)))
        zbuild()
        zclick("sl", i="1")
        zbuild()
        zclick("pc", i=str(zix(twr)))
        zbuild()
        rq = zclick("dt")
        zbuild()
        K.check(rpk.startswith("+Loadout 1: Chest takes") and rq.startswith("=Press Take out again: Iron Chestplate  #1 leaves Requip"),
                "Z the Take out prompt names the picked twin as its row does (%s / %s)" % (rpk, rq))
        zclick("sl", i="1")
        zclick("pk", v="keep")
        zclick("sl", i="1")
        zclick("tab", v="0")
        zbuild()
        n_calls = len(gcalls)
        zbuild()
        K.check(len(gcalls) == n_calls, "Z SkyyGear's text is cached per page by the stack (no bridge call on a rebuild) (%d -> %d)" % (n_calls, len(gcalls)))
        zclick("so")
        t0b = zbuild()
        tw2 = [int(zp.twinNo(Store.get(kZ, Zp.u), e_)) for e_ in ents]
        K.check(zp.sort == 1 and tw2 == [1, 2] and "Iron Chestplate  #1" in t0b and "Iron Chestplate  #2" in t0b, "Z ... the same numbers under another sort")
        zclick("q", **{"@RqQ": "sharp"})
        zbuild()
        cs_ = zcells()
        K.check(len(cs_) == 1 and str(Store.get(kZ, Zp.u).entry(cs_[0]).rar) == "rare", "Z the search finds the SkyyGear name a row shows (sharp) (%s)" % cs_)
        zclick("pc", i="0")
        tS = zbuild()
        K.check("Sharp Iron Chestplate - Rare - Lv 2" in tS and "Defence +4." in tS, "Z the detail panel shows the row's name and the modifiers")
        zclick("tab", v="4")
        t4 = zbuild()
        cw = zcells()
        K.check(zp.view == 4 and str(zp.q) == "" and int(zp.sort) == 0 and sorted(zid(c) for c in cw) == ["Skyy_Spear_Test", "Weapon_Bow_Wood", "Weapon_Sword_Iron"],
                "Z the Weapons tab: sword, bow and the mod spear; its own (empty) search and sort (%s)" % [zid(c) for c in cw])
        K.check("Iron Sword" in t4 and "Legendary - Strength +12 - Crit Chance +5%" in t4 and "Untiered" in t4 and ("TextColor: %s" % SUIC["gold"]) in t4
                and ("TextColor: %s" % SUIC["Legendary"]) in t4, "Z weapon rows: modifiers, Untiered in the kit gold, Legendary colour")
        zclick("tab", v="1")
        t1 = zbuild()
        ci_ = zcells()
        K.check(sorted(zid(c) for c in ci_) == ["Food_Bread", "Potion_Health", "Tool_Pickaxe_Iron"] and "x9" in t1 and "x5" in t1,
                "Z the Items tab: potion + bread stacks (x9 / x5 tags) + the pickaxe (tools stay in Items) (%s)" % [zid(c) for c in ci_])
        zclick("tab", v="0")
        zbuild()
        K.check(str(zp.q) == "sharp" and int(zp.sort) == 1 and len(zcells()) == 1, "Z back on Armor: its own search (sharp) and sort (rarity) came back")
        zclick("qc")
        zclick("tab", v="4")
        zclick("q", **{"@RqQ": "bow"})
        zbuild()
        K.check(len(zcells()) == 1 and zid(zcells()[0]) == "Weapon_Bow_Wood", "Z search on the Weapons tab (bow)")
        zclick("tab", v="1")
        zbuild()
        K.check(str(zp.q) == "" and len(zcells()) == 3, "Z ... the Items tab keeps its own empty search")
        zclick("tab", v="4")
        zclick("qc")
        zbuild()
        # a hotbar slot opens the tab of its pick: Keep -> stays on the Weapons / Items tab you are on; a picked potion -> Items
        zclick("tab", v="0")
        zbuild()
        zclick("sl", i="4")
        zbuild()
        K.check(zp.view == 4, "Z a hotbar slot with Keep from the Armor tab opens Weapons")
        zclick("sl", i="4")
        zclick("tab", v="1")
        zbuild()
        zclick("sl", i="4")
        zbuild()
        K.check(zp.view == 1 and zp.slot == 4, "Z ... from the Items tab it stays on Items")
        zclick("tab", v="4")
        zbuild()
        k4 = (int(zp.view), int(zp.slot))
        zclick("tab", v="1")
        zbuild()
        K.check(k4 == (4, 4) and zp.view == 1 and zp.slot == 4, "Z fix round: Items <-> Weapons keeps the selected hotbar slot (%s)" % (k4,))
        pot = [c for c in zcells() if zid(c) == "Potion_Health"][0]
        rp = zclick("pc", i=str(zix(pot)))
        zbuild()
        zclick("sl", i="4")
        zclick("tab", v="0")
        zbuild()
        zclick("sl", i="4")
        zbuild()
        K.check(rp.startswith("+Loadout 1: Hotbar 1") and zp.view == 1, "Z a hotbar slot that picks the potion opens Items (%s)" % rp)
        zclick("pk", v="keep")
        zbuild()
        # picked marker: the sword in Hotbar 2
        zclick("tab", v="4")
        zbuild()
        zclick("sl", i="5")
        zbuild()
        K.check(zp.view == 4 and zp.slot == 5, "Z Hotbar 2 (Keep) from the Weapons tab stays on Weapons")
        swz = [c for c in zcells() if zid(c) == "Weapon_Sword_Iron"][0]
        rs_ = zclick("pc", i=str(zix(swz)))
        t5 = zbuild()
        K.check(rs_.startswith("+Loadout 1: Hotbar 2") and "Legendary - picked in 1 loadout - Strength +12" in t5, "Z the row says picked in 1 loadout (%s)" % rs_)
        # Equip: the picked sword goes to Hotbar 2 (stamped, OUT) -> its row says "on you" with the disabled look; Equip itself is 0.2.1's
        zclick("sl", i="5")
        zbuild()
        gap()
        re_ = zclick("eq")
        zbuild()
        bwz = [c for c in zcells() if zid(c) == "Weapon_Bow_Wood"][0]
        zclick("pc", i=str(zix(bwz)))   # the details move to the bow (no slot selected: nothing is picked)
        t6 = zbuild()
        si = zix(swz)
        K.check(re_.startswith("+Equipped") and si >= 0 and "Legendary - on you - picked in 1 loadout" in t6 and "Sword Iron" in t6 and ("#SkyyRqP%dOut" % si) in t6,
                "Z an equipped (OUT) row: Requip's own record (name, rarity) + on you + picked + the disabled look (%s / row %d / %s)" % (re_, si, [x_[:160] for x_ in t6.split("#SkyyRqP") if "Strength" in x_ or x_.startswith("%dOut" % si)]))
        # no SkyyGear: Requip's own record (a new page = a new cache)
        br.remove("gear:fn:describe")
        br.remove("gear:fn:rollsLine")
        zp2 = TP(Zp.pr)
        zbuild(zp2)
        zclick("tab", page=zp2, v="0")
        t7 = zbuild(zp2)
        K.check("Iron Chest  #1" in t7 and "Iron Chest  #2" in t7 and "Iron Chest  #3" not in t7 and "Chestplate" not in t7 and "Rare - picked" not in t7 and "Lv 2" in t7,
                "Z without SkyyGear the rows show Requip's own record (readable id name, rarity, level); the two normal chests stay #1 / #2")
        # 10 loadouts on the page (+ the next locked one)
        free0 = int(Cfg.FREE)
        Cfg.FREE = 10
        t8 = zbuild(zp2)
        Cfg.FREE = free0
        K.check("Loadouts 1 of 10" in t8 and "#SkyyRqL9" in t8 and "#SkyyRqL10" in t8 and "#SkyyRqL11" not in t8 and "11.  Loadout 11  - locked" in t8,
                "Z 10 free loadouts: 10 open + the next locked one in the list")
        cZ, dZc = census(Zp)
        K.check(not once(Zp, dZc), "Z exactly once after every row click")
        # fix round: long text is cut with "..." to its one-line label (the name keeps its #N; the grey line loses the modifiers first)
        WP = P("WdPage")
        br.put("gear:fn:describe", GFn(g_desc))
        br.put("gear:fn:rollsLine", GFn(g_roll))
        dZ = Store.get(kZ, Zp.u)
        e_sp = [e_ for e_ in dZ.entries.values() if str(e_.itemId()) == "Skyy_Spear_Test"][0]
        zp3 = TP(Zp.pr)
        rsp = [str(x_) for x_ in zp3.rowText(dZ, e_sp, Ops.secs(Zp.st, Zp.ref))]
        K.check(rsp[0].startswith("Extraordinarily Magnificent") and rsp[0].endswith("...") and int(WP.textW(rsp[0], True)) <= int(WP.NAME_MAX),
                "Z a long name is cut with ... to the row's name label (%s)" % rsp[0])
        lng = str(WP.fit("Iron Chestplate " * 12, int(WP.NAME_MAX), True))
        K.check(lng.endswith("...") and int(WP.textW(lng, True)) <= int(WP.NAME_MAX) and str(WP.fit("Short", 400, False)) == "Short", "Z fit(): cut + ... / short text kept")
        # 0.2.5: ONE SCROLLING LIST (Skyy "allow scrolling here.") - every row drawn, a click far down picks / takes out THAT entry
        Zq = W.player("00000000-0000-0000-0000-0000000000a3", "Quin")
        kQ = str(Zq.u)
        for i in range(10):
            setc(Zq.sto, i, stack("Armor_Copper_Head", 1, '{"SkyyGear": {"v": 1, "r": "rare", "lvl": %d, "id": true, "mods": "Strength +12 - Crit Chance +5%% - Dexterity +8 - Intelligence +7 - Agility +6 - Mana Regen +3 - Life Steal +2 - Walk Speed +4"}}' % (i + 1)))
        rq0 = str(Ops.run(Zq.pr, Zq.ref, Zq.st, 7, 0, None))
        qp = TP(Zq.pr)

        def qb():
            b, ev = UCB(), UEB()
            qp.build(Zq.ref, b, ev, Zq.st)
            return " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in list(b.getCommands()))

        def qc(a, **kw):
            d_ = {"a": a, "t": str(qp.tok)}
            d_.update(kw)
            qp.handleDataEvent(Zq.ref, Zq.st, json.dumps(d_))
            return str(qp.info)

        def qcells():
            return [str(c) for c in qp.cells if c]

        def rowh(t_, i_=0):
            m_ = re.search(r"#SkyyRqP%d \{[^}]*?Height: (\d+)" % i_, t_)
            return int(m_.group(1)) if m_ else -1

        qb()
        qc("tab", v="0")
        q1 = qb()
        p1 = qcells()
        K.check(Store.get(kQ, Zq.u).count(0) == 10 and len(p1) == 10 and "#SkyyRqP9Nm" in q1 and "Page " not in q1 and "#SkyyRqPv" not in q1
                and "10 in this list - scroll to see them all" in q1 and rowh(q1) == 47,
                "Z (0.2.5) 10 entries: ALL 10 rows in the one scrolling list, normal 44 px rows, no pager (%s)" % rq0)
        K.check("LayoutMode: TopScrolling" in q1.split("#SkyyRqPa {", 1)[1][:500], "Z (0.2.5) the pool area is a scroll list")
        dQ = Store.get(kQ, Zq.u)
        rtq = [str(x_) for x_ in qp.rowText(dQ, dQ.entry(p1[0]), Ops.secs(Zq.st, Zq.ref))]
        K.check(rtq[1].startswith("Rare - Strength +12") and rtq[1].endswith("...") and int(WP.textW(rtq[1], False)) <= int(WP.SUB_MAX),
                "Z a long grey line is cut with ... to its label, the modifiers last (%s)" % rtq[1])
        qc("sl", i="0")
        qb()
        p1b = qcells()
        rp2 = qc("pc", i="9")
        qb()
        pick = str(Store.get(kQ, Zq.u).slots[0].picks[0])
        K.check(rp2.startswith("+Loadout 1: Head takes") and p1b[9] in pick, "Z (0.2.5) a click on the LAST row (far down) picks THAT item (%s / %s)" % (rp2, pick))
        qc("sl", i="0")
        qb()
        nxt = qcells()
        other = [c for c in nxt if c not in pick][-1]
        qc("pc", i=str(nxt.index(other)))
        qb()
        K.check(str(qp.det) == other, "Z (0.2.5) a click (no slot) selects that row for the detail panel")
        rt2 = qc("dt")
        q3 = qb()
        K.check(rt2.startswith("+Taken out") and Store.get(kQ, Zq.u).entry(other) is None and len(qcells()) == 9 and "9 in this list" in q3,
                "Z (0.2.5) Take out of a row far down takes THAT entry: gone from the pool, 9 rows left (%s)" % rt2)
        pk_ix = [i_ for i_, c in enumerate(qcells()) if c in pick][0]
        qc("pc", i=str(pk_ix))
        qb()
        rq2 = qc("dt")
        rq3 = qc("dt")
        q4 = qb()
        K.check(rq2.startswith("=Press Take out again: ") and rq3.startswith("+Taken out") and len(qcells()) == 8 and "8 in this list" in q4 and rowh(q4) == 47,
                "Z (0.2.5) Take out of the (picked) row asks twice, then 8 rows (%s / %s)" % (rq2, rq3))
        # the row size: few rows = bigger rows that fill the list (Skyy: "if there are only a few items try to scale them to all fit.")
        q6 = None
        for _n in range(2):
            qc("pc", i="0")
            qb()
            qc("dt")
            q6 = qb()
        h6 = rowh(q6)
        for _n in range(2):
            qc("pc", i="0")
            qb()
            qc("dt")
            q4b = qb()
        h4 = rowh(q4b)
        K.check(len(qcells()) == 4 and 44 < h6 < h4 <= 88 and 6 * (h6 + 2) <= int(WP.LISTH) and 4 * (h4 + 2) <= int(WP.LISTH) and "#SkyyRqP3Nm" in q4b,
                "Z (0.2.5) 6 rows = %d px, 4 rows = %d px (<= 2x 44): a short list fills the list area without scrolling (inside %s px)" % (h6, h4, WP.LISTH))
        # the search row sits ABOVE the tab row (Skyy: "move the search above the Armor, weapons and items section.")
        K.check(0 <= q4b.index("#SkyyRqSub0 {") < q4b.index("#SkyyRqSr {") < q4b.index("#SkyyRqPa {") and "#SkyyRqTabs" not in q4b,
                "Z (0.2.6) the views are the sub-tab row at the top, the search sits above the pool list")
        # 0.2.7: the 4th button is SALVAGE - no SkyyGear (gear:fn:salvage) here: a clear line, nothing moves
        qc("pc", i="0")
        qb()
        sel0 = str(qp.det)
        cS0, _d = census(Zq)
        rsl = qc("ds")
        q7 = qb()
        cS1, _d = census(Zq)
        K.check(rsl.startswith("-Salvage needs SkyyGear 0.3.17") and cS0 == cS1 and Store.get(kQ, Zq.u).entry(sel0) is not None
                and "#SkyyRqDs" in q7 and "Salvage" in q7.split("#SkyyRqDs", 1)[1][:2500], "Z (0.2.7) Salvage: drawn, without SkyyGear it says so and moves nothing (%s)" % rsl)
        cQ, dQc = census(Zq)
        K.check(not once(Zq, dQc), "Z exactly once after the scrolling-list clicks")
        # ---- S 0.2.5: a LONG list (180 swords) - the first 150 rows drawn, picks / Take out / Forget far down act on THAT entry
        Zs = W.player("00000000-0000-0000-0000-0000000000a5", "Sami")
        kS = str(Zs.u)
        for b_ in range(5):
            for i in range(36):
                setc(Zs.sto, i, stack("Weapon_Sword_Iron", 1, '{"SkyyGear": {"v": 1, "r": "rare", "lvl": %d, "id": true}}' % (b_ * 36 + i + 1)))
            gap()
            Ops.run(Zs.pr, Zs.ref, Zs.st, 7, 0, None)
        sp_ = TP(Zs.pr)

        def sb():
            b, ev = UCB(), UEB()
            sp_.build(Zs.ref, b, ev, Zs.st)
            return " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in list(b.getCommands()))

        def sc(a, **kw):
            d_ = {"a": a, "t": str(sp_.tok)}
            d_.update(kw)
            sp_.handleDataEvent(Zs.ref, Zs.st, json.dumps(d_))
            return str(sp_.info)

        def scells():
            return [str(c) for c in sp_.cells if c]
        sb()
        sc("tab", v="4")
        s1 = sb()
        c1 = scells()
        K.check(Store.get(kS, Zs.u).count(1) == 180 and len(c1) == 150 and "#SkyyRqP149Nm" in s1 and "#SkyyRqP150" not in s1
                and "The first 150 of 180 - search to find the rest" in s1 and rowh(s1) == 47,
                "S 180 swords: the first 150 rows drawn in the scroll list + 'The first 150 of 180' (%d cells)" % len(c1))
        sc("sl", i="4")
        sb()
        c1b = scells()
        rps = sc("pc", i="140")
        sb()
        pkS = str(Store.get(kS, Zs.u).slots[0].picks[4])
        K.check(rps.startswith("+Loadout 1: Hotbar 1") and c1b[140] in pkS, "S a hotbar slot + a click on row 140 picks THAT sword (%s / %s)" % (rps, pkS))
        sc("sl", i="4")
        sb()
        c2 = scells()
        tgt = c2[141]
        sc("pc", i="141")
        sb()
        K.check(str(sp_.det) == tgt, "S a click on row 141 selects THAT entry")
        rft = sc("df")
        K.check(rft.startswith("=") and len(scells()) == 150, "S Forget on row 141 answers about the row's own item (%s)" % rft)
        sc("pc", i="141")
        sb()
        rts = sc("dt")
        sb()
        liveS = [(i_, q_) for i_, c_ in enumerate(Zs.secs) for q_ in range(int(c_.getCapacity())) if getc(c_, q_) is not None and str(getc(c_, q_).getItemId()) == "Weapon_Sword_Iron"]
        K.check(rts.startswith("+Taken out: Weapon_Sword_Iron") and Store.get(kS, Zs.u).entry(tgt) is None and len(liveS) == 1
                and str(Codec.outOf(getc(Zs.secs[liveS[0][0]], liveS[0][1]))) == str(Store.pkey(Zs.u)) and Store.get(kS, Zs.u).count(1) == 179,
                "S Take out of row 141 takes THAT entry (one sword out, marked for the profile; 179 left) (%s)" % rts)
        sc("q", **{"@RqQ": "no such thing"})
        s3 = sb()
        K.check(len(scells()) == 0 and "search: no such thing" in s3, "S search with no match = an empty list")
        sc("q", **{"@RqQ": "sword"})
        sb()
        K.check(len(scells()) == 150, "S search 'sword' = the capped list again")
        sc("qc")
        sc("so")
        s4 = sb()
        K.check(int(sp_.sort) == 1 and len(scells()) == 150 and "Sort: rarity" in s4, "S Sort still cycles (rarity) on the scroll list")
        cSs, dSs = census(Zs)
        K.check(not once(Zs, dSs), "S exactly once after the long-list clicks")
        br.remove("gear:fn:describe")
        br.remove("gear:fn:rollsLine")
        old_tok = str(pg.tok)
        pg.handleDataEvent(Pg.ref, Pg.st, json.dumps({"a": "eq", "t": "stale"}))
        K.check(str(pg.info).startswith("=The page changed"), "X16 a click from a stale page: rebuilt, nothing done")
        pg.handleDataEvent(Pg.ref, Pg.st, '{"a":"close"}')
        K.check(pg.closes == 1 and pg.rebuilds > 20, "X16 Close")
        cPg, dPg = census(Pg)
        K.check(not once(Pg, dPg), "X16 exactly once after every page click")

        # ============================================================ MP 0.2.6 THE MENU PATTERN (kit 1.7 hub page, every view, REAL builders)
        HBc = P("HubBar")
        hmap = HBc.map()
        K.check(hmap is not None and int(JClass("java.lang.System").identityHashCode(hmap)) == int(JClass("java.lang.System").identityHashCode(br)),
                "MP the kit HubBar uses skyy.bridge")
        K.check(int(P("WdHubOpen").register()) == 1, "MP WdHubOpen.register puts the tab")
        he = br.get("hub:tab:storage:requip")
        K.check(he is not None and len(he) == 6 and str(he[0]) == "SkyyWardrobe" and str(he[1]) == "Requip" and int(he[2]) == 20 and str(he[3]) == "requip"
                and str(he[4].getClass().getName()) == PKG + "WdHubOpen" and he[5] is None,
                "MP hub:tab:storage:requip = {SkyyWardrobe, Requip, 20, requip, WdHubOpen, null} (SUI.HUB_TABS)")
        FALSE_ = JClass("java.lang.Boolean").FALSE
        K.check(he[4].apply("not a uuid") == FALSE_ and he[4].apply(UUID_.randomUUID()) == FALSE_, "MP WdHubOpen: not a UUID / an offline player = FALSE (the bar runs /requip)")
        _others = [r_ for r_ in SUI.hub_page_tabs("storage") if r_[0] != "requip"]
        for r_ in _others:
            br.put("hub:tab:storage:%s" % r_[0], JArray(JClass("java.lang.Object"))([r_[2], SUI.hub_tab_label("storage", r_[0]), JClass("java.lang.Integer")(r_[1]), r_[4], None, None]))
        for h_ in SUI.HUB_ROW_IDS:
            br.put("hub:def:%s" % h_, JArray(JClass("java.lang.Object"))([SUI.hub_title_now(h_) if h_ != "home" else "Home", "skymenu" if h_ == "home" else SUI.HUB_DEFS[h_][1], "Skyy_Menu", None]))
        br.put("hub:last:" + str(Pg.u), JClass("java.util.concurrent.ConcurrentHashMap")())
        Pm = W.player("00000000-0000-0000-0000-0000000000a6", "Mira")
        kPm = str(Pm.u)
        for i, a in enumerate(["Armor_Iron_Head", "Armor_Iron_Chest", "Weapon_Sword_Iron", "Weapon_Bow_Wood", "Potion_Health"]):
            setc(Pm.sto, i, stack(a, 1 if i < 4 else 5))
        run(Pm, 7)
        cMp0, dMp0 = census(Pm)
        mp = TP(Pm.pr)

        def mpcmds():
            b, ev = UCB(), UEB()
            mp.build(Pm.ref, b, ev, Pm.st)
            cm = []
            for c in list(b.getCommands()):
                cm.append((None if c.type is None else str(c.type), None if c.selector is None else str(c.selector),
                           None if c.text is None else str(c.text), None if c.data is None else str(c.data)))
            bs = []
            for e_ in list(ev.getEvents()):
                bs.append(str(e_.selector) if getattr(e_, "selector", None) is not None else "")
            return cm, bs

        def unq(d_):
            try:
                v_ = json.loads(d_)
            except Exception:
                return str(d_)
            if isinstance(v_, dict) and len(v_) == 1:
                v_ = list(v_.values())[0]
            return v_ if isinstance(v_, str) else str(d_)

        def mpcheck(what):
            cm, bs = mpcmds()
            apps = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t_) for ty, s_, t_, d_ in cm if t_ is not None and ty and "Append" in ty])
            sets = [(s_, unq(d_)) for ty, s_, t_, d_ in cm if ty == "Set"]
            ok = True
            try:
                info = SUI.assert_menu_page(apps, hub="storage", what=what, sets=sets)
                SUI.check_page(apps, "Skyy")
                SUI.check_sky_paths(apps, tab_icons=True)
            except Exception as ex:
                ok, info = False, str(ex)
            ids = set()
            for _p, mk in apps:
                ids |= set(re.findall(r"\b[A-Za-z]+ #([A-Za-z0-9]+) \{", SUI.render(mk)))
            bad = [s_ for s_, _v in sets if s_.lstrip("#").split(".")[0] not in ids] + [s_ for s_ in bs if s_ and s_.lstrip("#") not in ids]
            txt = " ".join(str(t_) for _ty, _s, t_, _d in cm if t_)
            K.check(ok and not bad and isinstance(info, dict) and info["rows"] == 2 and info["subs"] == 1,
                    "MP %s: assert_menu_page (1600 x 980, rows 1 + 2, ONE sub row, no back / pager text, content fits) + check_page + sky paths; "
                    "every b.set / binding names an element (%s; bad %s)" % (what, info, bad[:4]))
            return txt, sets, apps

        def mpclick(a, **kw):
            d_ = {"a": a}
            d_.update(kw)
            mp.handleDataEvent(Pm.ref, Pm.st, json.dumps(d_))
            return str(mp.info)
        t_a, s_a, ap_a = mpcheck("Armor view")
        K.check("#SkyyRqBigT" in t_a and 'Text: "Requip"' in t_a and "#SkyyRqSub3" in t_a and "#SkyyRqSub4" not in t_a and "Auto-store: OFF" in [v_ for s_, v_ in s_a if s_ == "#SkyyRqAuto.Text"],
                "MP row 2 shows the Storage tabs (Requip among them), 4 sub-tabs (no picker open), the footer's Auto-store")
        _sel = [mk for p_, mk in ap_a if p_ == "SkyyRqBigTabs" and mk.startswith("Button")]
        K.check(len(_sel) == len(SUI.hub_page_tabs("storage")), "MP row 2: one big tab per Storage tab (%d)" % len(_sel))
        for tv_, nm_ in (("4", "Weapons"), ("1", "Items"), ("2", "Inventory"), ("0", "Armor")):
            n0_ = int(mp.rebuilds)
            mpclick("tabv" + tv_)
            K.check(int(mp.view) == int(tv_) and int(mp.rebuilds) == n0_ + 1 and not str(mp.info).startswith("=The page changed"),
                    "MP the %s sub-tab (no page token) switches the view (view %s) and redraws" % (nm_, mp.view))
            mpcheck("%s view" % nm_)
        mpclick("sl", i="0", t=str(mp.tok))
        t_s, _s, _a = mpcheck("Head slot selected")
        mpclick("sl", i="6", t=str(mp.tok))
        mpcheck("hotbar slot selected")
        for vw_, nm_, rk_ in ((3, "Pocket blocks", None), (5, "Pets", "0"), (6, "Abilities", "2"), (7, "Modifiers", "3")):
            if rk_ is None:
                mp.view = vw_      # the Magic Bag blocks of the selected hotbar slot (the Pocket button opens it when SkyySacks is loaded)
            else:
                mpclick("rf", i=rk_, t=str(mp.tok))   # a PET / ability / modifier slot opens its picker
            K.check(int(mp.view) == vw_, "MP the %s picker is open (view %s)" % (nm_, mp.view))
            t_v, _s, _a = mpcheck("%s picker" % nm_)
            K.check("#SkyyRqSub4" in t_v and ('Text: "%s"' % nm_) in t_v, "MP the open %s picker is the selected 5th sub-tab (an in-page selection)" % nm_)
            n0_ = int(mp.rebuilds)
            mpclick("tabvp")
            K.check(int(mp.view) == vw_ and int(mp.rebuilds) == n0_ + 1, "MP the picker's own sub-tab answers (redraw, the picker stays)")
        mpclick("tabv0")
        K.check(int(mp.view) == 0 and int(mp.rs) == -1, "MP the Armor sub-tab leaves the picker (view %s, slot %s)" % (mp.view, mp.rs))
        mpcheck("Armor again")
        # rule 7: the loadouts list - 4 open + 1 locked = 5 rows: the biggest tier (64); 18 rows = 32 px rows that scroll
        t_l, _s, _a = mpcheck("short loadouts list")
        m_ = re.search(r"#SkyyRqL0 \{[^}]*?Height: (\d+)", t_l)
        K.check(m_ is not None and int(m_.group(1)) == int(P("WdPage").LSH[2]) == 64, "MP rule 7: a short loadouts list = bigger rows (%s px)" % (m_.group(1) if m_ else None))
        # the 0.1 question / returned-items notes, a shut Requip: still one hub page each
        dM = Store.get(kPm, Pm.u)
        dM.ask01 = 0
        mpcheck("the 0.1 question note")
        dM.ask01 = -1
        # HubBar.route: the X closes, the own tab / hub redraws, another Storage tab is handed on (its command: no Function here)
        c0_ = int(mp.closes)
        mpclick("hub:close")
        K.check(int(mp.closes) == c0_ + 1, "MP the X (hub:close) closes the page")
        n0_ = int(mp.rebuilds)
        mpclick("hub:requip")
        K.check(int(mp.rebuilds) == n0_ + 1, "MP row 2's own tab (hub:requip) redraws the page")
        n0_ = int(mp.rebuilds)
        mpclick("hub:h:storage")
        K.check(int(mp.rebuilds) == n0_ + 1, "MP row 1's own hub (hub:h:storage) redraws the page")
        n0_, c0_ = int(mp.rebuilds), int(mp.closes)
        try:
            mpclick("hub:zzgone")
            gone_ok = True
        except Exception as ex_:
            gone_ok = str(ex_)
        K.check(gone_ok is True and int(mp.rebuilds) == n0_ and int(mp.closes) == c0_, "MP a missing tab: the page stays, nothing redrawn or closed (%s)" % gone_ok)
        for r_ in _others:
            br.remove("hub:tab:storage:%s" % r_[0])
        for h_ in SUI.HUB_ROW_IDS:
            br.remove("hub:def:%s" % h_)
        K.check(int(HBc.removeAll()) == 1, "MP HubBar.removeAll removes our tab")
        K.check(br.get("hub:tab:storage:requip") is None, "MP the tab key is gone")
        cMp1, dMp1 = census(Pm)
        K.check(cMp1 == cMp0 and not once(Pm, dMp1), "MP nothing moved: exactly once after every menu-pattern click")

        # ============================================================ SV 0.2.7 THE SALVAGE BUTTON (gear:fn:salvage stand-in, materials, never coins)
        mpcheck("Salvage button")
        _t_sv, _s_sv, _a_sv = mpcheck("Salvage button again")
        K.check("#SkyyRqDs" in _t_sv and 'Text: "Salvage"' in _t_sv.split("#SkyyRqDs", 1)[1][:2500] and "Sell" not in _t_sv.split("#SkyyRqDs", 1)[1][:400],
                "SV the 4th detail button reads Salvage on the kit 1.7 page (assert_menu_page passes)")
        Sv = P("WdSalv")
        JLongC = JClass("java.lang.Long")
        SALV_MATS = {"Weapon_Sword_Iron": [("Ingredient_Bar_Iron", 3), ("Wood_Oak_Log", 1)], "Armor_Iron_Head": [("Ingredient_Bar_Iron", 2)],
                     "Tool_Pickaxe_Iron": [("Ingredient_Bar_Iron", 2), ("Wood_Oak_Log", 1)], "Weapon_Bow_Wood": [("Wood_Oak_Log", 2)]}
        gst = {"journal": set(), "calls": [], "on": True, "refuse_commit": False}

        def g_doc(md):
            if md is None:
                return None
            try:
                return json.loads(str(md.toJson())).get("SkyyGear")
            except Exception:
                return None

        def g_ans(why, mats=(), key=None):
            return JArray(JObject)([JString(why) if why is not None else None, JArray(JString)([m_[0] for m_ in mats]),
                                    JArray(JLongC)([JLongC.valueOf(m_[1]) for m_ in mats]), JString(key) if key is not None else None])

        @JImplements("java.util.function.Function")
        class GearSalvStandIn(object):
            """SkyyGear 0.3.17's gear:fn:salvage contract: {UUID, id, metadata, mode} -> {why, String[] ids, Long[] qty, key}"""
            @JOverride
            def apply(self, a):
                iid, md, mode = str(a[1]), a[2], str(a[3])
                gst["calls"].append(mode)
                d_ = g_doc(md)
                key = None if d_ is None else iid + "|" + json.dumps(d_, sort_keys=True)
                if mode == "release":
                    if key in gst["journal"]:
                        gst["journal"].discard(key)
                        return g_ans(None, (), key)
                    return g_ans("That piece was not salvaged.")
                if not gst["on"]:
                    return g_ans("Salvaging is switched off on this server.")
                if d_ is None:
                    return g_ans("%s is no SkyyGear piece - it cannot be salvaged." % iid)
                if int(d_.get("ll", 0)) == 1:
                    return g_ans("Lifelong tools are never salvaged - they stay with you.")
                if d_.get("id") is False:
                    return g_ans("Identify %s first." % iid)
                mats = SALV_MATS.get(iid, [])
                if not mats:
                    return g_ans("%s has no recipe to salvage." % iid)
                if mode == "commit":
                    if gst["refuse_commit"]:
                        return g_ans("The salvage could not be saved - nothing was salvaged.")
                    if key in gst["journal"]:
                        return g_ans("That piece was salvaged already - nothing more to give.")
                    gst["journal"].add(key)
                return g_ans(None, mats, key)
        gfn = GearSalvStandIn()
        coin_calls = []

        @JImplements("java.util.function.Function")
        class CoinTrap(object):
            @JOverride
            def apply(self, a):
                coin_calls.append(str(a))
                return JLongC.valueOf(0)
        _trap = CoinTrap()
        for k_ in ("coins:fn:add", "coins:fn:give", "coins:fn:pay", "coins:fn:take", "coins:fn:credit", "bank:fn:deposit", "purse:fn:add"):
            br.put(k_, _trap)
        br.put("gear:fn:salvage", gfn)
        BAR, OAK = "Ingredient_Bar_Iron", "Wood_Oak_Log"

        def cnt(p, iid):
            return sum(int(c.getItemStack(JShort(i)).getQuantity()) for c in p.secs for i in range(int(c.getCapacity()))
                       if c.getItemStack(JShort(i)) is not None and not c.getItemStack(JShort(i)).isEmpty() and str(c.getItemStack(JShort(i)).getItemId()) == iid)

        def svfiles(k):
            dd = os.path.join(Wd, "requip", k)
            return sorted(f_ for f_ in os.listdir(dd) if f_.startswith("salvage-")) if os.path.isdir(dd) else []

        def svlog():
            f_ = os.path.join(Wd, "requip.log")
            return open(f_, encoding="utf8").read() if os.path.isfile(f_) else ""

        def gk(s):
            s2 = Codec.unstamp(s)
            return str(s2.getItemId()) + "|" + json.dumps(g_doc(s2.getMetadata()), sort_keys=True)

        SWD = '{"SkyyGear": {"v": 1, "r": "rare", "lvl": %d, "id": true, "at": %d}}'

        sv_at = [1000]

        def sv_player(uid, name, n_sw=1):
            p = W.player(uid, name)
            for i in range(n_sw):
                sv_at[0] += 1     # every piece its own birth stamp = its own SkyyGear key
                setc(p.sto, i, stack("Weapon_Sword_Iron", 1, SWD % (5 + i, sv_at[0])))
            setc(p.sto, 10, stack("Armor_Iron_Head", 1, gdoc("rare", 4)))
            gap()
            r_ = run(p, 7)
            Jr.dropAll()     # Requip's own keep window over (its guard is tested apart)
            d_ = Store.get(str(Store.pkey(p.u)), p.u)
            sw = sorted((e_ for e_ in ent_by_id(d_, "Weapon_Sword_Iron")), key=lambda e_: str(e_.eid))
            return p, d_, [str(e_.eid) for e_ in sw], str(ent_by_id(d_, "Armor_Iron_Head")[0].eid), r_

        # ---- the page: quote, two clicks, exactly once, the loadouts named + unpicked, storage first with a top-up
        Sa, dSa, swSa, hdSa, r0 = sv_player("00000000-0000-0000-0000-0000000000b1", "Sal")
        kSa = str(Store.pkey(Sa.u))
        e_sw = swSa[0]
        run(Sa, 4, 0, "Mining")
        K.check(run(Sa, 10, 0, "4|e:" + e_sw).startswith("+") and run(Sa, 10, 1, "5|e:" + e_sw).startswith("+"), "SV the sword is picked in loadouts 1 + 2")
        setc(Sa.sto, 20, stack(BAR, 98))
        bar0, oak0 = cnt(Sa, BAR), cnt(Sa, OAK)
        sp_ = TP(Sa.pr)

        def svb():
            b, ev = UCB(), UEB()
            sp_.build(Sa.ref, b, ev, Sa.st)
            return " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in list(b.getCommands()))

        def svc(a, **kw):
            d_ = {"a": a, "t": str(sp_.tok)}
            d_.update(kw)
            sp_.handleDataEvent(Sa.ref, Sa.st, json.dumps(d_))
            return str(sp_.info)
        svb()
        svc("tab", v="4")
        svb()
        ix_ = [str(c) for c in sp_.cells].index(e_sw) if e_sw in [str(c) for c in sp_.cells] else -1
        svc("pc", i=str(ix_))
        K.check(str(sp_.det) == e_sw and int(sp_.slot) < 0, "SV a click on the sword row selects it (no slot open: nothing picked)")
        cA0, _d = census(Sa)
        n_calls0 = len(gst["calls"])
        q1 = svc("ds")
        cA1, dA1 = census(Sa)
        K.check(q1.startswith("=Salvage for: 3 Iron Bar, 1 Wood Oak Log") and "within 10 s" in q1 and "never coins" in q1 and "Mining" in q1 and "Loadout 2" in q1
                and cA1 == cA0 and dA1.entry(e_sw) is not None and gst["calls"][n_calls0:] == ["quote"] and not svfiles(kSa),
                "SV the first click = the quote (materials, the loadouts that lose it, 10 s, never coins); nothing changed, only a quote asked (%s)" % q1)
        q2 = svc("ds")
        cA2, dA2 = census(Sa)
        lo_ = [str(dA2.slots[i].picks[k]) for i in range(2) for k in range(13) if dA2.slots[i].picks[k] is not None]
        K.check(q2.startswith("+Salvaged") and "3 Iron Bar, 1 Wood Oak Log in your inventory" in q2 and "It left Mining, Loadout 2" in q2
                and dA2.entry(e_sw) is None and ("e:" + e_sw) not in lo_ and cnt(Sa, BAR) == bar0 + 3 and cnt(Sa, OAK) == oak0 + 1
                and int(W.getc(Sa.sto, 20).getQuantity()) == 100 and gst["calls"].count("commit") == 1 and len(gst["journal"]) == 1,
                "SV the second click within 10 s salvages: the entry + its loadout picks gone, 3 bars (98 -> 100 top-up + 1) + 1 log, one commit (%s)" % q2)
        _bars = [(si_, i) for si_, c in enumerate(Sa.secs) for i in range(int(c.getCapacity())) if W.getc(c, i) is not None and str(W.getc(c, i).getItemId()) == BAR]
        _oaks = [(si_, i) for si_, c in enumerate(Sa.secs) for i in range(int(c.getCapacity())) if W.getc(c, i) is not None and str(W.getc(c, i).getItemId()) == OAK]
        K.check(all(si_ == 2 for si_, _i in _bars + _oaks) and not W.getc(Sa.sto, 20).getMetadata(), "SV storage first: every material stack is in storage (%s / %s)" % (_bars, _oaks))
        lg_ = svlog()
        K.check(("SALVAGE %s %s %s Weapon_Sword_Iron -> Ingredient_Bar_Iron*3,Wood_Oak_Log*1 (no coins) unpicked=0:4,1:5," % (Sa.u, kSa, e_sw)) in lg_,
                "SV requip.log: SALVAGE <uuid> <pkey> <eid> <item> -> materials (no coins) unpicked=...")
        K.check(svfiles(kSa) == ["salvage-%s.txt" % e_sw] and json.load(open(os.path.join(Wd, "requip", kSa, svfiles(kSa)[0])))["stage"] == "given",
                "SV the journal stays at 'given' for the keep window")
        q3 = svc("ds")
        q4 = str(Ops.run(Sa.pr, Sa.ref, Sa.st, 17, 0, e_sw))
        K.check(not q3.startswith("+") and q4.startswith("-That item is not in Requip any more") and gst["calls"].count("commit") == 1
                and cnt(Sa, BAR) == bar0 + 3 and cnt(Sa, OAK) == oak0 + 1, "SV exactly once: a third click / a repeated op 17 changes nothing (%s / %s)" % (q3, q4))
        K.check(not once(Sa), "SV exactly once (every other entry IN xor live)")
        Sv.sweep(JLong(int(time.time() * 1000) + 10 ** 8))
        K.check(not svfiles(kSa) and int(Sv.KEEP.size()) == 0, "SV the keep-window sweep deletes the given journal")
        # ---- the ask window: a click on another row between the two clicks = a new quote (nothing happens)
        e_hd = hdSa
        svc("tab", v="0")
        svb()
        ixh = [str(c) for c in sp_.cells].index(e_hd)
        svc("pc", i=str(ixh))
        qh1 = svc("ds")
        svc("pc", i=str(ixh))
        qh2 = svc("ds")
        K.check(qh1.startswith("=Salvage for: 2 Iron Bar") and qh2.startswith("=Salvage for:") and Store.get(kSa, Sa.u).entry(e_hd) is not None,
                "SV another click between the two = the quote again (the confirm is the SAME entry twice in a row)")
        sp_.pendAt = JLong(int(sp_.pendAt) - 11000)
        qh3 = svc("ds")
        K.check(qh3.startswith("=Salvage for:") and Store.get(kSa, Sa.u).entry(e_hd) is not None, "SV a second click after 10 s = the quote again")

        # ---- refusals: nothing changes, never a commit
        def refuse(p, eid, want, what):
            c0, _d0 = census(p)
            n0 = gst["calls"].count("commit")
            f0 = svfiles(str(Store.pkey(p.u)))
            r_ = str(Ops.run(p.pr, p.ref, p.st, 17, 0, eid))
            c1, d1 = census(p)
            K.check(r_.startswith(want) and c1 == c0 and gst["calls"].count("commit") == n0 and svfiles(str(Store.pkey(p.u))) == f0 and not once(p, d1),
                    "SV refused (%s): '%s', nothing changed (%s)" % (what, want, r_))
            return r_
        Rf = W.player("00000000-0000-0000-0000-0000000000b2", "Rufus")
        setc(Rf.sto, 0, stack("Tool_Pickaxe_Iron", 1, '{"SkyyGear": {"v": 1, "r": "common", "lvl": 1, "id": true, "ll": 1, "lu": "rf1"}}'))
        setc(Rf.sto, 1, stack("Potion_Health", 5))
        setc(Rf.sto, 2, stack("Weapon_Bow_Wood", 1))
        setc(Rf.sto, 3, stack("Weapon_Sword_Iron", 1, SWD % (7, 3001)))
        setc(Rf.sto, 4, stack("Weapon_Sword_Iron", 1, SWD % (8, 3002)))
        gap()
        run(Rf, 7)
        kRf = str(Store.pkey(Rf.u))
        dRf = Store.get(kRf, Rf.u)
        e_sw1, e_sw2 = sorted(str(e_.eid) for e_ in ent_by_id(dRf, "Weapon_Sword_Iron"))
        refuse(Rf, e_sw1, "-That piece moved a moment ago - Requip guards every change for 30 s", "Requip's own journal still lists it")
        Jr.dropAll()
        refuse(Rf, str(ent_by_id(dRf, "Tool_Pickaxe_Iron")[0].eid), "-Lifelong tools are never salvaged", "a lifelong tool (SkyyGear says why)")
        refuse(Rf, str(ent_by_id(dRf, "Potion_Health")[0].eid), "-Only gear can be salvaged", "a potion kind")
        refuse(Rf, str(ent_by_id(dRf, "Weapon_Bow_Wood")[0].eid), "-Weapon_Bow_Wood is no SkyyGear piece", "a plain piece")
        eU = dRf.entry(e_sw2)
        _keepS = eU.stack
        eU.stack = Codec.stamp(stack("Weapon_Sword_Iron", 1, '{"SkyyGear": {"v": 1, "r": "rare", "lvl": 8, "id": false, "at": 3002}}'), e_sw2)
        refuse(Rf, e_sw2, "-Identify Weapon_Sword_Iron first", "an unidentified piece (SkyyGear says why)")
        eU.stack = _keepS
        gst["on"] = False
        refuse(Rf, e_sw2, "-Salvaging is switched off on this server", "salvage.on off")
        gst["on"] = True
        br.remove("gear:fn:salvage")
        refuse(Rf, e_sw2, "-Salvage needs SkyyGear 0.3.17 or newer", "no SkyyGear")
        br.put("gear:fn:salvage", gfn)
        gap()
        K.check(run(Rf, 14, 0, e_sw2).startswith("+"), "SV fetch the second sword (OUT, stamped on you)")
        Jr.dropAll()
        refuse(Rf, e_sw2, "-It is not in Requip right now - deposit it first", "an OUT entry")
        # ---- full inventory: refused before anything; one free slot = done
        Fu, dFu, swFu, hdFu, _r = sv_player("00000000-0000-0000-0000-0000000000b3", "Fuller")
        kFu = str(Store.pkey(Fu.u))
        for c in (Fu.sto, Fu.hot, Fu.bak):
            for i in range(int(c.getCapacity())):
                setc(c, i, stack("Rock_Stone", 100))
        refuse(Fu, swFu[0], "-Inventory full - make room for 2 more stacks first (salvage gives 3 Iron Bar, 1 Wood Oak Log)", "a full inventory")
        Fu.bak.removeItemStackFromSlot(JShort(8), False)
        refuse(Fu, swFu[0], "-Inventory full - make room for 1 more stack first", "room for one of two stacks")
        Fu.bak.removeItemStackFromSlot(JShort(7), False)
        rF = run(Fu, 17, 0, swFu[0])
        K.check(rF.startswith("+Salvaged") and cnt(Fu, BAR) == 3 and cnt(Fu, OAK) == 1 and W.getc(Fu.bak, 7) is not None and W.getc(Fu.bak, 8) is not None,
                "SV two free backpack slots: salvaged, the materials in the last free slots (storage, hotbar full) (%s)" % rF)
        # ---- a refused COMMIT: the piece + its picks back, nothing given
        Cr, dCr, swCr, hdCr, _r = sv_player("00000000-0000-0000-0000-0000000000b4", "Cora")
        kCr = str(Store.pkey(Cr.u))
        run(Cr, 10, 0, "4|e:" + swCr[0])
        cC0, _d = census(Cr)
        gst["refuse_commit"] = True
        rC = run(Cr, 17, 0, swCr[0])
        gst["refuse_commit"] = False
        cC1, dC1 = census(Cr)
        K.check(rC.startswith("-Salvage refused: The salvage could not be saved") and "stays in Requip" in rC and cC1 == cC0 and dC1.entry(swCr[0]) is not None
                and str(dC1.slots[0].picks[4]) == "e:" + swCr[0] and not svfiles(kCr) and not once(Cr, dC1) and "SALVAGE-REFUSED" in svlog(),
                "SV a refused commit: the piece back in the pool AND in its loadout slot, nothing given, no journal left (%s)" % rC)
        # ---- save failures: once (put back at once), twice (memory holds it, the next action rewrites the files)
        Store.FAIL_NEXT = 1
        rS1 = run(Cr, 17, 0, swCr[0])
        cS1_, dS1_ = census(Cr)
        K.check(rS1.startswith("-Could not save Requip - nothing changed") and cS1_ == cC0 and dS1_.entry(swCr[0]) is not None and str(dS1_.slots[0].picks[4]) == "e:" + swCr[0]
                and not svfiles(kCr), "SV a failed save: nothing changed, no journal left (%s)" % rS1)
        Store.FAIL_NEXT = 2
        rS2 = run(Cr, 17, 0, swCr[0])
        K.check(rS2.startswith("-Could not save Requip - Sword Iron stays in Requip; Requip checks its files") and Store.get(kCr, Cr.u).entry(swCr[0]) is not None
                and len(svfiles(kCr)) == 1 and int(Sv.TODO.size()) == 1, "SV two failed saves: the memory holds the piece, the journal waits (%s)" % rS2)
        restart()
        rS3 = run(Cr, 5)
        cS3, dS3 = census(Cr)
        K.check("An interrupted salvage was undone: Sword Iron is back in Requip" in rS3 and cS3 == cC0 and dS3.entry(swCr[0]) is not None and not svfiles(kCr)
                and str(dS3.slots[0].picks[4]) == "e:" + swCr[0] and not once(Cr, dS3),
                "SV after a restart the waiting journal puts the piece back (files rewritten), nothing given (%s)" % rS3)
        # ---- a failed GIVE: committed, nothing given, owed - the next action gives it exactly
        Gv, dGv, swGv, hdGv, _r = sv_player("00000000-0000-0000-0000-0000000000b5", "Gav")
        kGv = str(Store.pkey(Gv.u))
        Sv.FAIL_GIVE_AT = 1
        rG = run(Gv, 17, 0, swGv[0])
        Sv.FAIL_GIVE_AT = -1
        K.check(rG.startswith("+Salvaged Sword Iron - its materials (3 Iron Bar, 1 Wood Oak Log) could not be put in your inventory just now") and cnt(Gv, BAR) == 0
                and cnt(Gv, OAK) == 0 and Store.get(kGv, Gv.u).entry(swGv[0]) is None and json.load(open(os.path.join(Wd, "requip", kGv, svfiles(kGv)[0])))["stage"] == "owed",
                "SV a failed give (the 2nd put): every put of it rolled back, the journal says owed (%s)" % rG)
        setc(Gv.sto, 30, stack(BAR, 5))     # the player picks up bars meanwhile: in-session the owed amount is exact (no evidence guess)
        rG2 = run(Gv, 5)
        K.check("Salvage: 3 Iron Bar, 1 Wood Oak Log in your inventory" in rG2 and cnt(Gv, BAR) == 8 and cnt(Gv, OAK) == 1 and int(Sv.TODO.size()) == 0
                and json.load(open(os.path.join(Wd, "requip", kGv, svfiles(kGv)[0])))["stage"] == "given", "SV the next action gives the owed materials exactly (%s)" % rG2)
        K.check(int(Sv.dropAll()) >= 1 and not svfiles(kGv), "SV a normal stop closes the given journals")
        # critic fix 1: an UNEXPECTED error part way (THROW_AT seam, not a JVM death) -> refused, the journal queued; the next action resolves it
        for th_, want_ in ((2, "back"), (4, "back"), (5, "gave"), (7, "gave")):
            Ex, dEx, swEx, hdEx, _r = sv_player("00000000-0000-0000-0000-%012x" % (0xe00 + th_), "Exa%d" % th_)
            kEx = str(Store.pkey(Ex.u))
            gkEx = gk(dEx.entry(swEx[0]).stack)
            cE0, _d = census(Ex)
            Sv.THROW_AT = th_
            rE = run(Ex, 17, 0, swEx[0])
            Sv.THROW_AT = -1
            K.check(rE.startswith("-Something went wrong with the salvage") and len(svfiles(kEx)) == 1 and ("%s|%s" % (kEx, swEx[0])) in [str(x_) for x_ in Sv.TODO.keySet()],
                    "SV an unexpected error after step %d: refused, the journal queued at once (%s)" % (th_, rE))
            rE2 = run(Ex, 5)
            cE2, dE2 = census(Ex)
            back_ = dE2.entry(swEx[0]) is not None
            K.check((want_ == "back") == back_ and (cE2 == cE0 if back_ else (cnt(Ex, BAR) == 3 and cnt(Ex, OAK) == 1)) and (gkEx in gst["journal"]) == (not back_)
                    and not once(Ex, dE2) and not [f_ for f_ in svfiles(kEx) if json.load(open(os.path.join(Wd, "requip", kEx, f_)))["stage"] != "given"],
                    "SV ... the next action (no restart) resolves it: %s exactly (%s)" % (want_, rE2))

        # ---- CRASH AT EVERY STEP + after every file of the removal save; the inventory as it was AND rolled back to before the salvage
        cr_n = [0]

        def crash_case(step, files, revert):
            cr_n[0] += 1
            uid = "00000000-0000-0000-0000-%012x" % (0xc00 + cr_n[0])
            p, d_, sw, hd, _r = sv_player(uid, "Cr%d" % cr_n[0])
            k = str(Store.pkey(p.u))
            e_ = sw[0]
            run(p, 10, 2, "4|e:" + e_)
            sk = gk(d_.entry(e_).stack)
            snap = W.snap(p)
            b0, o0 = cnt(p, BAR), cnt(p, OAK)
            c0, _d0 = census(p)
            if files is None:
                Sv.CRASH_AT = step
            else:
                Store.CRASH_FILES = files
            try:
                r_ = run(p, 17, 0, e_)
                crashed = "no crash: " + r_
            except Exception as ex_:
                crashed = str(ex_)
            Sv.CRASH_AT = -1
            Store.CRASH_FILES = -1
            Gate.BUSY.clear()
            if revert:
                W.restore(p, snap)
            restart()
            rr = run(p, 5)
            c1, d1 = census(p)
            back = d1.entry(e_) is not None
            gave = cnt(p, BAR) == b0 + 3 and cnt(p, OAK) == o0 + 1
            none = cnt(p, BAR) == b0 and cnt(p, OAK) == o0
            fs = svfiles(k)
            tag = "step %s%s, inventory %s" % (step if files is None else "-", "" if files is None else " (after %d files of the save)" % files, "rolled back" if revert else "as it was")
            K.check("harness crash" in crashed, "SV crash %s: the JVM died there (%s)" % (tag, crashed[:80]))
            K.check((back and none) != (not back and gave) and (back or gave), "SV crash %s: the piece back XOR its materials given (back %s, bars %d -> %d, logs %d -> %d; %s)"
                    % (tag, back, b0, cnt(p, BAR), o0, cnt(p, OAK), rr))
            K.check((sk in gst["journal"]) == gave, "SV crash %s: SkyyGear's journal holds the piece iff its materials were given" % tag)
            K.check(not once(p, d1) and (not back or str(d1.slots[2].picks[4]) == "e:" + e_), "SV crash %s: exactly once; a piece back is picked again" % tag)
            K.check(not fs or (json.load(open(os.path.join(Wd, "requip", k, fs[0])))["stage"] == "given" and len(fs) == 1), "SV crash %s: no open journal left (%s)" % (tag, fs))
            rr2 = run(p, 5)
            c2, d2 = census(p)
            restart()
            rr3 = run(p, 5)
            c3, d3 = census(p)
            K.check(c2 == c1 and c3 == c1 and (d3.entry(e_) is not None) == back and not svfiles(k),
                    "SV crash %s: a second repair and another restart change nothing (%s / %s)" % (tag, rr2, rr3))
            return back, gave
        exp = {1: "back", 2: "back", 3: "back", 4: "back", 5: "gave", 6: "gave", 7: "gave", 8: "gave"}
        for st_ in range(1, 9):
            for rv_ in (False, True):
                bk_, gv_ = crash_case(st_, None, rv_)
                K.check((exp[st_] == "back") == bk_, "SV crash step %d (%s): the expected outcome %s" % (st_, "rolled back" if rv_ else "as it was", exp[st_]))
        for nf_ in range(0, 3):
            for rv_ in (False, True):
                bk_, gv_ = crash_case(None, nf_, rv_)
                K.check(bk_, "SV crash after %d files of the removal save: the piece is back" % nf_)
        # ---- owed after a crash: no room at the repair -> waits (in-session, then by evidence after a restart); room -> given once
        Ow, dOw, swOw, hdOw, _r = sv_player("00000000-0000-0000-0000-0000000000b6", "Owen")
        kOw = str(Store.pkey(Ow.u))
        gkOw = gk(dOw.entry(swOw[0]).stack)
        Sv.CRASH_AT = 5
        try:
            run(Ow, 17, 0, swOw[0])
        except Exception:
            pass
        Sv.CRASH_AT = -1
        Gate.BUSY.clear()
        restart()
        free_ = [(c, i) for c in (Ow.sto, Ow.hot, Ow.bak) for i in range(int(c.getCapacity())) if W.getc(c, i) is None]
        for c, i in free_:
            setc(c, i, stack("Rock_Stone", 100))
        rO1 = run(Ow, 5)
        K.check("wait for room" in rO1 and cnt(Ow, BAR) == 0 and json.load(open(os.path.join(Wd, "requip", kOw, svfiles(kOw)[0])))["stage"] == "owed"
                and Store.get(kOw, Ow.u).entry(swOw[0]) is None, "SV no room at the repair: the materials wait (owed) (%s)" % rO1)
        restart()
        rO2 = run(Ow, 5)
        K.check(cnt(Ow, BAR) == 0 and len(svfiles(kOw)) == 1, "SV still no room after a restart: still owed (%s)" % rO2)
        Ow.sto.removeItemStackFromSlot(JShort(35), False)
        rO3 = run(Ow, 5)
        K.check(cnt(Ow, BAR) == 3 and cnt(Ow, OAK) == 0 and "still wait for room" in rO3, "SV one free slot: the bars given, the log still waits (%s)" % rO3)
        Ow.sto.removeItemStackFromSlot(JShort(34), False)
        rO4 = run(Ow, 5)
        rO5 = run(Ow, 5)
        K.check(cnt(Ow, BAR) == 3 and cnt(Ow, OAK) == 1 and "1 Wood Oak Log in your inventory" in rO4 and "Wood Oak Log" not in rO5 and gkOw in gst["journal"],
                "SV room again: the rest given exactly once (%s / %s)" % (rO4, rO5))
        K.check(not coin_calls and "coin" not in " ".join(gst["calls"]), "SV NO coin bridge was ever called by a salvage (%s)" % coin_calls[:3])
        for k_ in ("coins:fn:add", "coins:fn:give", "coins:fn:pay", "coins:fn:take", "coins:fn:credit", "bank:fn:deposit", "purse:fn:add", "gear:fn:salvage"):
            br.remove(k_)
        Sv.dropAll()

        # ============================================================ W 0.2.3 THE PET / SUMMON / ABILITY SLOTS (every new code path, EXECUTED)
        Pw = W.player("00000000-0000-0000-0000-000000000023", "Wren")
        kW = str(Store.pkey(Pw.u))
        uW = str(Pw.u)

        def WL(n=0):
            return Store.get(kW, Pw.u).slots[n]

        @JImplements("java.util.function.Function")
        class WFn(object):
            def __init__(self, f):
                self.f = f

            @JOverride
            def apply(self, a):
                return self.f(a)
        JBool, JIntC = JClass("java.lang.Boolean"), JClass("java.lang.Integer")
        state["owned"] = {"pa000001": "Common Rabbit Lv 24", "pb000002": "Rare Wolf Lv 12", "pc000003": "Epic Bear Lv 5"}
        state["pets"] = "pa000001|"
        SB = ("v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=RiftCleave;n1=Arcane Breach;n2=Elemental Imbue;n3=Sunder;"
              "n4=Rift Cleave;mods=ArcaneBreach:Power+-")
        abil_keep = state.get("abil")
        state["abil"] = SB
        state["usable"] = {"ArcaneBreach", "ElementalImbue", "RiftCleave"}   # Sunder: not unlocked in the class tree
        RUNES = {"ArcaneBreach": "Rune_Breach", "ElementalImbue": "Rune_Imbue", "Sunder": "Rune_Sunder", "RiftCleave": "Rune_Rift"}
        NAMES = {"ArcaneBreach": "Arcane Breach", "ElementalImbue": "Elemental Imbue", "Sunder": "Sunder", "RiftCleave": "Rift Cleave"}
        panel_calls = [0]

        def panel(u):
            """class:fn:abilPanel as SkyyClasses 0.1.29 answers it (Object[129]; the fields Requip reads)"""
            panel_calls[0] += 1
            o = JArray(JObject)(129)
            sn = state.get("abil") or ""
            kv = dict(x_.split("=", 1) for x_ in sn.split(";") if "=" in x_)
            o[0] = JString(state.get("pstatus", "ok"))
            o[1] = JString(kv.get("class", ""))
            for i_, k_ in enumerate(("p1", "p2", "a1", "a2")):
                b_ = 12 + 16 * i_
                aid = kv.get(k_, "")
                o[b_] = JString(aid)
                o[b_ + 1] = JString(NAMES.get(aid, aid))
                o[b_ + 2] = JString(RUNES.get(aid, ""))
                o[b_ + 6] = JIntC.valueOf(5 + i_)
                o[b_ + 10] = JString("Power" if aid == "ArcaneBreach" else "")
                o[b_ + 12] = JString("")
                o[95 + i_] = JBool.valueOf(aid in state["usable"])
            return o
        br.put("class:fn:abilPanel", WFn(panel))
        # 0.2.4: class:fn:abilMods {UUID, abilityId} as SkyyClasses 0.1.29 answers it + a loadoutSet that applies "mods=" slot by slot
        MNAME = {"Power": "Power+", "Radius": "Radius+", "Duration": "Duration+", "Chain": "Chain", "Efficiency": "Efficiency", "Slow": "Slow", "Echo": "Echo"}
        MODTAB = {"ArcaneBreach": ["Radius", "Duration", "Power", "Chain"], "ElementalImbue": ["Duration", "Power", "Efficiency", "Chain"],
                  "Sunder": ["Duration", "Power", "Chain", "Echo"], "RiftCleave": ["Duration", "Radius", "Slow", "Power", "Echo"]}
        state["meq"] = {"ArcaneBreach": ["Power", ""], "ElementalImbue": ["", ""], "Sunder": ["", ""], "RiftCleave": ["", ""]}
        state["munl"] = {"ArcaneBreach": {"Radius", "Power", "Chain"}, "ElementalImbue": {"Duration", "Power", "Chain"}, "Sunder": {"Power"},
                         "RiftCleave": {"Duration", "Radius", "Power"}}
        state["mdbl"] = set()          # (ability, modifier) pairs the tree lets double
        state["mslots"] = {}           # ability -> open modifier slots (default 2)

        def mods_fn(a):
            aid = str(a[1])
            if aid not in MODTAB or not (state.get("abil") or "").startswith("v=1;class=Spellblade"):
                return JArray(JString)(0)
            eq = state["meq"].setdefault(aid, ["", ""])
            out_ = ["%s|%s|3|40|Lv 3|damage|%d|%s|%s|+5%%|0|||0|2||5|2" % (aid, NAMES[aid], state["mslots"].get(aid, 2), eq[0], eq[1])]
            for mid in MODTAB[aid]:
                un = mid in state["munl"].get(aid, set())
                out_.append("%s|%s|0|%s|%d|5|10|%d|1|+%d%% %s|next|%s|0" % (mid, MNAME[mid], "1" if un else "0", 3 if un else 0, eq.count(mid),
                                                                          10, mid.lower(), "1" if (aid, mid) in state["mdbl"] else "0"))
            return JArray(JString)(out_)
        br.put("class:fn:abilMods", WFn(mods_fn))
        abil_set_0 = br.get("class:fn:loadoutSet")

        def abil_set_m(a):
            sn_ = str(a[1])
            state["calls"]["abil"].append(sn_)
            state["abil"] = sn_
            kv_ = dict(x_.split("=", 1) for x_ in sn_.split(";") if "=" in x_)
            skip_ = []
            for part_ in [p_ for p_ in kv_.get("mods", "").split("/") if ":" in p_]:
                aid_, two_ = part_.split(":", 1)
                two_ = (two_.split("+") + ["-", "-"])[:2]
                cur_ = state["meq"].setdefault(aid_, ["", ""])
                for sl_ in (0, 1):
                    md_ = "" if two_[sl_] == "-" else two_[sl_]
                    if md_ and md_ == cur_[1 - sl_] and (aid_, md_) not in state["mdbl"]:
                        skip_.append("%s slot %d (%s cannot be equipped twice)" % (aid_, sl_ + 1, md_))
                        continue
                    cur_[sl_] = md_
            return ("=Abilities set. Skipped: " + ", ".join(skip_) + ".") if skip_ else "+Abilities set."
        br.put("class:fn:loadoutSet", WFn(abil_set_m))
        # the profile's SkyyPets file (Requip only READS it): 3 owned pets + one released (pd000009: petName does not know it)
        pdir = os.path.join(mods, "Skyy_SkyyPets", "pets")
        os.makedirs(pdir, exist_ok=True)
        pfile = os.path.join(pdir, kW + ".properties")
        open(pfile, "w").write("v=1\nactive.1=pa000001\npet.pa000001.kind=Rabbit\npet.pb000002.kind=Wolf\npet.pc000003.kind=Bear\npet.pd000009.kind=Fox\n")
        pf_bytes = open(pfile, "rb").read()
        pgw = TP(Pw.pr)

        last_cmds = [[]]

        def wb():
            b, ev = UCB(), UEB()
            pgw.build(Pw.ref, b, ev, Pw.st)
            last_cmds[0] = list(b.getCommands())
            text_ = " ".join(" ".join(str(x) for x in (c.selector, c.text, c.data) if x is not None) for c in last_cmds[0])
            return text_, list(ev.getEvents())

        def wc(a, **kw):
            d_ = {"a": a, "t": str(pgw.tok)}
            d_.update(kw)
            pgw.handleDataEvent(Pw.ref, Pw.st, json.dumps(d_))
            return str(pgw.info)

        def wsel(i_):
            """select pet / ability slot i_ (a click on the selected one would unselect it)"""
            if int(pgw.rs) != i_:
                return wc("rf", i=str(i_))
            return "=" + str(pgw.info)

        def wcells():
            return [str(c) for c in pgw.cells if c is not None and str(c)]

        def wpick(cell):
            cs_ = [str(c) if c is not None else "" for c in pgw.cells]
            return wc("pc", i=str(cs_.index(cell))) if cell in cs_ else "NOT LISTED " + cell

        def lfile():
            f_ = os.path.join(Wd, "requip", kW, "loadouts.json")
            j_ = json.load(open(f_))
            return {jn(x_.get("n")): x_ for x_ in j_.get("loadouts", [])}

        def wsets(text_):
            """the b.set values of the slot labels of the last build: SkyyRqR<k>Nm / Sb -> text"""
            out_ = {}
            for c in last_cmds[0]:
                sel_ = str(c.selector) if c.selector is not None else ""
                m_ = re.fullmatch(r"#(SkyyRqR\d+(?:Nm|Sb))\.Text", sel_)
                if not m_:
                    continue
                v_ = c.data if c.data is not None else c.text
                v_ = str(v_) if v_ is not None else ""
                if len(v_) >= 2 and v_[0] == '"' and v_[-1] == '"':
                    v_ = json.loads(v_)
                elif v_.startswith("{"):
                    try:
                        j_ = json.loads(v_)
                        v_ = str(list(j_.values())[0]) if len(j_) == 1 else v_
                    except Exception:
                        pass
                out_[m_.group(1)] = v_
            return out_

        def rbuild():
            t_, e_ = wb()
            return t_

        def wval(sel):
            """the b.set value of one selector of the last build ("#SkyyRqSp.Text" ...)"""
            for c in last_cmds[0]:
                if c.selector is not None and str(c.selector) == sel:
                    v_ = c.data if c.data is not None else c.text
                    v_ = str(v_) if v_ is not None else ""
                    if len(v_) >= 2 and v_[0] == '"' and v_[-1] == '"':
                        v_ = json.loads(v_)
                    elif v_.startswith("{"):
                        try:
                            j_ = json.loads(v_)
                            v_ = str(list(j_.values())[0]) if len(j_) == 1 else v_
                        except Exception:
                            pass
                    return v_
            return None

        def cutok(got, exp):
            """a label = exp, or exp cut with ... by the page's font widths"""
            got = "" if got is None else str(got)
            return got == exp or (got.endswith("...") and len(got) > 3 and exp.startswith(got[:-3]))

        def cutall(gots, exps):
            return len(gots) == len(exps) and all(cutok(g_, e_) for g_, e_ in zip(gots, exps))

        sp_seen = []

        def sp_all(tag):
            """fix f: select every shown slot, read the selected-slot line (#SkyyRqSp), unselect again"""
            for i_ in range(14):
                if int(pgw.rs) != i_:
                    wc("rf", i=str(i_))
                rbuild()
                sp_seen.append((tag, i_, wval("#SkyyRqSp.Text")))
            if int(pgw.rs) >= 0:
                wc("rf", i=str(int(pgw.rs)))
            rbuild()
        text = rbuild()
        sets = wsets(text)
        K.check(all(("#SkyyRqR%d {" % i_) in text.replace("\\", "") for i_ in range(14)) and "#SkyyRqR14" not in text and "#SkyyRqPt" not in text
                and "#SkyyRqAb" not in text and "PET, SUMMON + ABILITIES - SPELLBLADE" in text and "#SkyyRqRr4" in text,
                "W1 (0.2.4) the loadout shows 14 cells (pet, summon, then the 4 class-loadout rows of ability + 2 modifiers) under PET, SUMMON + ABILITIES - SPELLBLADE")
        # fix a: a Keep slot shows WHAT Equip leaves there (the live pet / ability / modifier; icon-less) + "<slot> - Keep"
        K.check(cutall([sets.get("SkyyRqR%dNm" % i_) for i_ in range(14)], ["Common Rabbit", "Keep", "Arcane Breach", "Power+", "Empty", "Elemental Imbue", "Empty", "Empty",
                                                                             "Sunder", "Empty", "Empty", "Rift Cleave", "Empty", "Empty"])
                and cutall([sets.get("SkyyRqR%dSb" % i_) for i_ in range(14)],
                           ["Pet - Keep", "Summon - Keep (empty)", "Ability 2 - Keep", "Keep", "Keep", "Ability 3 - Keep", "Keep", "Keep",
                            "Crouch + 2 - Keep", "Keep", "Keep", "Crouch + 3 - Keep", "Keep", "Keep"]),
                "W1 fix a: a fresh loadout: every slot Keep and it SHOWS what is there now (live pet / abilities / modifiers) (%s)" % sets)
        lh = wval("#SkyyRqLh.Text") or ""
        K.check(lh.startswith("Equip: picked slots swap in, then pets, abilities + modifiers") and "Use what I wear / Save pets/abilities" in lh
                and "Reset" in lh and len(lh) <= 150,
                "W1 (0.2.4) the shorter hint explains Equip + Use what I wear + Save pets/abilities + Reset, 2 lines of the 420 px column (%d chars)" % len(lh))
        K.check('ItemId: ""' not in text and not [m for m in re.findall(r"#(SkyyRq\w+)", text) if "_" in m]
                and not re.search(r"Alignment: (Left|Right|Top|Bottom)\b", text), "W1 no empty ItemId, no underscore id, no Left/Right/Top/Bottom alignment")
        # ---- W2 the pet picker: Keep, None + the OWNED pets (the file's ids checked through pets:fn:petName; the released one never shows)
        fr0, oc0 = int(Brg.FILE_READS), int(Brg.OWNED_CALLS)
        r = wsel(0)
        text = rbuild()
        K.check(r.startswith("=Pet slot of Loadout 1: pick on the right") and int(pgw.rs) == 0 and int(pgw.view) == 5 and "Selected: Pet slot" in text
                and "Keep: Equip leaves your pet slot as it is (now: Common Rabbit Lv 24)." in text,
                "W2 click the Pet slot: selected, the pool column turns into its picker (%s)" % r)
        K.check(wcells() == ["rp:0|~", "rp:0|", "rp:0|pa000001", "rp:0|pb000002", "rp:0|pc000003"] and "Pick for the pet slot of Loadout 1 - 3 pets" in text
                and "In your pet slot now" in text and int(Brg.FILE_READS) == fr0 + 1 and open(pfile, "rb").read() == pf_bytes,
                "W2 (0.2.11) picker rows: Keep, None, the 3 owned pets sorted by rarity, then name (the released pd000009 is not listed); the SkyyPets file read once, untouched (%s)" % wcells())
        rbuild()
        K.check(int(Brg.FILE_READS) == fr0 + 1 and int(Brg.OWNED_CALLS) == oc0 + 1, "W2 the owned list is cached for 3 s (no second read on a rebuild)")
        br.put("pets:fn:owned", WFn(lambda u: JArray(JString)(["pc000003"])))
        pgw.petAt = 0
        rbuild()
        K.check(wcells() == ["rp:0|~", "rp:0|", "rp:0|pa000001", "rp:0|pc000003"] and int(Brg.FILE_READS) == fr0 + 1,
                "W2 pets:fn:owned (when a SkyyPets publishes it) is used instead of the file; the active pet is always offered (%s)" % wcells())
        br.remove("pets:fn:owned")
        pgw.petAt = 0
        wc("q", **{"@RqQ": "wolf"})
        rbuild()
        K.check(wcells() == ["rp:0|~", "rp:0|", "rp:0|pb000002"], "W2 the search filters pets by name (%s)" % wcells())
        wc("qc")
        rbuild()
        # ---- W3 pick a pet: only the loadout record changes; one Keep slot = "pets2" (0.2.2 ignores it), both picked = 0.2.2's "pets"
        r = wpick("rp:0|pb000002")
        L0 = WL()
        lf = lfile()
        K.check(r.startswith("+Loadout 1 - Pet slot: Rare Wolf Lv 12.") and L0.hasPets and not L0.petK and L0.sumK and str(L0.pet) == "pb000002"
                and "pets2" in lf[0] and "pets" not in lf[0] and lf[0]["pets2"].get("keep") == "summon" and lf[0]["pets2"].get("pet") == "pb000002",
                "W3 pick Rare Wolf for the pet slot: saved (summon stays Keep) as pets2 {keep: summon} (%s / %s)" % (r, lf.get(0)))
        text = rbuild()
        sets = wsets(text)
        K.check(sets.get("SkyyRqR0Nm") == "Rare Wolf" and sets.get("SkyyRqR0Sb") == "Pet - Lv 12" and "Skyy_PetIcon_Wolf" in text,
                "W3 (0.2.10) the Pet slot shows the wolf's own icon + Rare Wolf + Pet - Lv 12 (%s)" % sets)

        # ============================================================ PI 0.2.10 each pet shows its own icon (Skyy: "can we make this show the pet icon")
        WPg = JClass(PKG + "WdPage")
        FB = "Farming_Collar"

        def pdisp(k_):
            """SkyyPets PetKind.display: a NAMES entry, else the id split before each capital that follows a lower-case letter"""
            if k_ in PET_NAMES:
                return PET_NAMES[k_]
            return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", k_).replace("_", " ")
        rar_ = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
        bad_ = []
        for i_, k_ in enumerate(PET_KINDS):
            lab_ = "%s %s Lv %d" % (rar_[i_ % 6], pdisp(k_), i_ + 1)
            got_ = str(WPg.petPic(lab_, FB))
            exp_ = FB if k_ == PET_NOICON else "Skyy_PetIcon_" + k_
            if got_ != exp_:
                bad_.append((lab_, got_, exp_))
        K.check(not bad_, "PI icon id per kind: every SkyyPets kind's label -> Skyy_PetIcon_<Kind> (Skeleton Archer -> Skeleton) (%d kinds; bad %s)" % (len(PET_KINDS), bad_[:4]))
        K.check(str(WPg.petPic("Common Gecko Lv 1", FB)) == FB and str(WPg.petPic("Common Gecko Lv 1", "")) == "",
                "PI the fallback: a kind whose portrait item the client does not know -> the fallback icon (never an unknown id)")
        odd_ = [None, "", "Lv 3", "Epic Dragon Lv 2", "Rare", 'Rare Wo"lf Lv 1', "Rare Wolf; X Lv 1", "Mythic " + "W" * 60 + " Lv 1", "Rare Unknown Thing Lv 4"]
        K.check(all(str(WPg.petPic(o_, FB)) == FB for o_ in odd_),
                "PI an unknown kind / an empty, odd or too long label -> the fallback (%s)" % [str(WPg.petPic(o_, FB)) for o_ in odd_])
        K.check(str(WPg.petPic("Wolf Lv 3", FB)) == "Skyy_PetIcon_Wolf" and str(WPg.petPic("Unknown Crystal Golem", FB)) == "Skyy_PetIcon_CrystalGolem"
                and str(WPg.petPic("Legendary Skeleton Knight Lv 80", FB)) == "Skyy_PetIcon_SkeletonKnight",
                "PI a label without a rarity word / without a level / a two-word kind still finds the portrait")
        # the page: the picked Pet cell (Rare Wolf) + the picker rows of the pet slot
        wsel(0)
        text = rbuild()
        sets = wsets(text)
        K.check(sets.get("SkyyRqR0Nm") == "Rare Wolf" and "Skyy_PetIcon_Wolf" in text and "Skyy_PetIcon_Rabbit" in text and "Skyy_PetIcon_Bear" in text
                and FB not in text and 'ItemId: ""' not in text,
                "PI the picked Pet cell + the picker rows show each pet's own icon (Wolf, Rabbit, Bear), no collar left (%s)" % wcells())

        def pikit(what):
            b_, ev_ = UCB(), UEB()
            pgw.build(Pw.ref, b_, ev_, Pw.st)
            cm_ = [(None if c.type is None else str(c.type), None if c.selector is None else str(c.selector),
                    None if c.text is None else str(c.text), None if c.data is None else str(c.data)) for c in list(b_.getCommands())]
            apps_ = SUI.Appends([(None if s_ is None else s_.lstrip("#"), t_) for ty, s_, t_, d_ in cm_ if t_ is not None and ty and "Append" in ty])
            sets_ = [(s_, unq(d_)) for ty, s_, t_, d_ in cm_ if ty == "Set"]
            try:
                SUI.check_page(apps_, "Skyy")
                SUI.check_sky_paths(apps_, tab_icons=True)
                info_ = SUI.assert_menu_page(apps_, hub="storage", what=what, sets=sets_)
                return isinstance(info_, dict) and info_["rows"] == 2 and info_["subs"] == 1, info_
            except Exception as ex_:
                return False, str(ex_)
        ok_, info_ = pikit("pet picker with pet icons")
        K.check(ok_, "PI the page with the pet icons passes the kit checks (check_page + check_sky_paths + assert_menu_page) (%s)" % info_)
        # an unknown kind in the list -> the fallback icon, no empty ItemId; then back to the 0.2.9 fixture
        was_ = state["owned"]["pc000003"]
        state["owned"]["pc000003"] = "Epic Dragon Lv 5"
        open(pfile, "wb").write(pf_bytes.replace(b"pc000003.kind=Bear", b"pc000003.kind=Dragon"))   # 0.2.11: the FILE kind first - unknown there too
        pgw.petAt = 0
        text = rbuild()
        K.check(FB in text and "Skyy_PetIcon_Bear" not in text and "Skyy_PetIcon_Wolf" in text and 'ItemId: ""' not in text,
                "PI an unknown kind in the picker -> the fallback icon (the others keep theirs)")
        state["owned"]["pc000003"] = was_
        pgw.petAt = 0
        rbuild()

        # ============================================================ RQ 0.2.11 Skyy: "i dont see my dragon in the requip list and the dog still shows up as a sword."
        open(pfile, "wb").write(pf_bytes)   # PI changed Bear's kind in the file: back to the fixture
        pf_old = open(pfile, "rb").read()
        open(pfile, "wb").write(pf_old + b"pet.pe000005.kind=DragonPlain\npet.pf000006.kind=Dog\npet.pg000007.kind=DragonTundra\npet.ph000008.kind=DragonTundra\n")
        pf_new = open(pfile, "rb").read()
        own_old = dict(state["owned"])
        state["owned"].update({"pe000005": "Epic Plain Dragon Lv 1", "pf000006": "Common Dog Lv 25", "pg000007": "Epic Tundra Dragon Lv 2",
                               "ph000008": "Epic Tundra Dragon Lv 9"})
        Brg.PKIND.clear()
        pgw.petAt = 0
        wsel(0)
        text = rbuild()
        cmds_ = list(last_cmds[0])

        def row_icons():
            """{ cell value: the ItemId of its pool row } from the last build's appends (#SkyyRqP<n> rows)"""
            cs_ = [str(c) if c is not None else "" for c in pgw.cells]
            out_ = {}
            for c in last_cmds[0]:
                t_ = None if c.text is None else str(c.text)
                if not t_:
                    continue
                for m_ in re.finditer(r"#SkyyRqP(\d+) \{(.*?)(?=#SkyyRqP\d+ \{|$)", t_, re.S):
                    n_ = int(m_.group(1))
                    ids_ = re.findall(r'ItemId: "([^"]*)"', m_.group(2))
                    if n_ < len(cs_) and cs_[n_]:
                        out_[cs_[n_]] = ids_[0] if ids_ else ""
            return out_
        exp_order = ["rp:0|~", "rp:0|", "rp:0|pf000006", "rp:0|pa000001", "rp:0|pb000002", "rp:0|pc000003", "rp:0|pe000005", "rp:0|ph000008", "rp:0|pg000007"]
        K.check(wcells() == exp_order and "Sort: rarity, name" in text and "Pick for the pet slot of Loadout 1 - 7 pets" in text,
                "RQ the picker sorted rarity, name, level: Common Dog, Common Rabbit, Rare Wolf, Epic Bear, Epic Plain Dragon, Epic Tundra Dragon Lv 9, Lv 2 (%s)" % wcells())
        ri_ = row_icons()
        exp_ic = {"rp:0|pf000006": "Skyy_PetIcon_Dog", "rp:0|pa000001": "Skyy_PetIcon_Rabbit", "rp:0|pb000002": "Skyy_PetIcon_Wolf",
                  "rp:0|pc000003": "Skyy_PetIcon_Bear", "rp:0|pe000005": "Skyy_PetIcon_DragonPlain", "rp:0|pg000007": "Skyy_PetIcon_DragonTundra",
                  "rp:0|ph000008": "Skyy_PetIcon_DragonTundra"}
        K.check(all(ri_.get(k_) == v_ for k_, v_ in exp_ic.items()) and ri_.get("rp:0|~") == "" and ri_.get("rp:0|") == ""
                and "Farming_Collar" not in text and 'ItemId: ""' not in text,
                "RQ icons per kind: each pet row = its kind's own portrait (Dog, Rabbit, Wolf, Bear, DragonPlain, DragonTundra), Keep / None icon-less, no collar (%s)" % ri_)
        K.check(str(Brg.PKIND.get("pe000005")) == "DragonPlain" and str(Brg.PKIND.get("pf000006")) == "Dog" and open(pfile, "rb").read() == pf_new,
                "RQ the kinds come from SkyyPets' own file (read only) (%s / %s)" % (Brg.PKIND.get("pe000005"), Brg.PKIND.get("pf000006")))
        # the file's kind wins over the label; without it the label guess finds the dragons (words reversed); odd / unknown kinds -> collar
        FB = "Farming_Collar"
        K.check(str(WPg.petIcon("pe000005", "Common Dog Lv 1", FB)) == "Skyy_PetIcon_DragonPlain"
                and str(WPg.petIcon("zz000001", "Epic Plain Dragon Lv 1", FB)) == "Skyy_PetIcon_DragonPlain"
                and str(WPg.petIcon(None, "Legendary Tundra Dragon Lv 40", FB)) == "Skyy_PetIcon_DragonTundra"
                and str(WPg.petPic("Epic Plain Dragon Lv 1", FB)) == "Skyy_PetIcon_DragonPlain",
                "RQ the file's kind first; no kind -> the label guess (Plain Dragon -> DragonPlain)")
        Brg.PKIND.put("zq000001", "Nope")
        Brg.PKIND.put("zq000002", 'Wo"lf')
        K.check(str(WPg.petIcon("zq000001", "Rare Wolf Lv 1", FB)) == "Skyy_PetIcon_Wolf" and str(WPg.petIcon("zq000001", "Epic Stranger Lv 1", FB)) == FB
                and str(WPg.petIcon("zq000002", "Epic Stranger", FB)) == FB and str(WPg.petIcon("zq000001", None, FB)) == FB,
                "RQ an unknown / odd kind in the file -> the label guess, else the neutral collar (never an unknown id)")
        # the cell of a picked dragon (the loadout's Pet cell) shows the dragon too
        wpick("rp:0|pe000005")
        text = rbuild()
        K.check(wsets(text).get("SkyyRqR0Nm") == "Epic Plain Dragon" and "Skyy_PetIcon_DragonPlain" in text,
                "RQ the loadout's Pet cell with the dragon picked shows its portrait (%s)" % wsets(text))
        # SEARCH: the Enter binding + the box
        b_, ev_ = UCB(), UEB()
        pgw.build(Pw.ref, b_, ev_, Pw.st)
        bnd_ = [(str(getattr(e_, "type", "")), str(getattr(e_, "selector", "")), str(getattr(e_, "data", ""))) for e_ in list(ev_.getEvents())]
        ent_ = [x_ for x_ in bnd_ if x_[1] == "#SkyyRqQ"]
        btn_ = [x_ for x_ in bnd_ if x_[1] == "#SkyyRqQs"]
        K.check(len(ent_) == 1 and "Validating" in ent_[0][0] and len(btn_) == 1 and "#SkyyRqQ.Value" in ent_[0][2] and '"a":"q"' in ent_[0][2].replace(" ", "")
                and ent_[0][2] == btn_[0][2],
                "RQ Enter in the search box = the Search button (a Validating binding with the same data) (%s / %s)" % (ent_, btn_))
        n0_ = len([c for c in list(b_.getCommands()) if c.selector is not None and str(c.selector) == "#SkyyRqQ.Value"])
        wc("q", **{"@RqQ": "dra"})
        text = rbuild()
        K.check(wcells() == ["rp:0|~", "rp:0|", "rp:0|pe000005", "rp:0|ph000008", "rp:0|pg000007"] and "3 pets - search: dra" in text
                and wval("#SkyyRqQ.Value") == "dra" and n0_ == 0,
                "RQ search 'dra' -> Keep, None + the two dragons only; the footer says it; the box holds 'dra' (%s / %r / %d)" % (wcells(), wval("#SkyyRqQ.Value"), n0_))
        wc("q", **{"@RqQ": "  DRA  "})
        text = rbuild()
        K.check(wcells() == ["rp:0|~", "rp:0|", "rp:0|pe000005", "rp:0|ph000008", "rp:0|pg000007"], "RQ the search is case-insensitive (%s)" % wcells())
        wc("q", **{"@RqQ": "zzz"})
        text = rbuild()
        K.check(wcells() == ["rp:0|~", "rp:0|"] and "0 pets - search: zzz" in text, "RQ no match -> only Keep / None (%s)" % wcells())
        wc("qc")
        text = rbuild()
        K.check(wcells() == exp_order and wval("#SkyyRqQ.Value") is None and "search:" not in text,
                "RQ Clear -> every row back, the box drawn empty (%s)" % wcells())
        # FIT: the normal rows - 7 whole rows in the list, the page fits 1080
        hs_ = sorted(set(int(h_) for h_ in re.findall(r"#SkyyRqP\d+ \{ Anchor: \([^)]*?Height: (\d+)", text)))
        pa_ = re.search(r"#SkyyRqPa \{ Anchor: \([^)]*?Height: (\d+)", text)
        lin_ = int(pa_.group(1)) - 8 if pa_ else -1
        rem_ = lin_ - (lin_ // (hs_[0] + 2)) * (hs_[0] + 2) if hs_ and lin_ > 0 else -1
        K.check(hs_ == [47] and lin_ == 346 and lin_ // 49 == 7 and 0 <= rem_ <= 6,
                "RQ FIT: 9 rows scroll at 47 px: 7 whole rows fill the 346 px list, %d px of the 8th show (no half row) (%s, list %s)" % (rem_, hs_, lin_))
        ok_, info_ = pikit("pet picker, 9 rows, dragons")
        K.check(ok_, "RQ the 9-row pet picker passes the kit checks (assert_menu_page: 1600 x 980 fits 1080) (%s)" % info_)
        # a tab's search stays its own: search the Armor tab, back to the pet picker -> no pet search
        wc("tab", v="0")
        wc("q", **{"@RqQ": "iron"})
        text = rbuild()
        K.check(wval("#SkyyRqQ.Value") == "iron", "RQ the Armor tab's search shows in its box")
        wsel(0)
        text = rbuild()
        K.check(len(wcells()) == 9 and wval("#SkyyRqQ.Value") is None, "RQ back in the pet picker: its own (empty) search, the box empty (%s)" % wcells())
        # back to the fixture
        wc("tab", v="0")
        wc("qc")
        open(pfile, "wb").write(pf_old)
        state["owned"].clear()
        state["owned"].update(own_old)
        run(Pw, 16, 0, "0|~")
        pgw.petAt = 0
        wsel(0)
        rbuild()
        r = wsel(1)
        rbuild()
        r = wpick("rp:1|pb000002")
        L0 = WL()
        lf = lfile()
        K.check(r.startswith("+Loadout 1 - Summon slot: Rare Wolf") and L0.petK and not L0.sumK and str(L0.summon) == "pb000002" and lf[0]["pets2"].get("keep") == "pet",
                "W4 the same pet for the summon slot of the same loadout: the two trade places (pet slot -> Keep) (%s)" % r)
        wsel(0)
        rbuild()
        r = wpick("rp:0|pa000001")
        L0 = WL()
        lf = lfile()
        K.check(r.startswith("+Loadout 1 - Pet slot: Common Rabbit") and not L0.petK and not L0.sumK and lf[0].get("pets") == {"pet": "pa000001", "summon": "pb000002"}
                and "pets2" not in lf[0], "W4 both slots picked = the 0.2.2 pets record exactly (%s)" % lf.get(0))
        wsel(1)
        r1 = wc("pk", v="keep")
        L0 = WL()
        k1 = (L0.hasPets, L0.petK, L0.sumK)
        r2 = wc("pk", v="empty")
        L0 = WL()
        k2 = (L0.hasPets, L0.petK, L0.sumK, str(L0.summon))
        r3 = wc("pk", v="pocket")
        K.check(r1.startswith("+Loadout 1 - Summon slot: Keep") and k1 == (True, False, True) and r2.startswith("+Loadout 1 - Summon slot: None")
                and k2 == (True, False, False, "") and r3.startswith("=Pocket blocks are for hotbar slots"),
                "W4 the Keep / Empty / Pocket buttons on a selected pet slot: Keep, None, a reason (%s / %s / %s)" % (r1, r2, r3))
        rG = run(Pw, 16, 0, "0|pd000009")
        rB1, rB2, rB3 = run(Pw, 16, 0, "0|a;b=c"), run(Pw, 16, 0, "14|~"), run(Pw, 16, 0, "nothing")
        K.check(rG.startswith("-That pet is not yours any more") and rB1 == "-Pick what?" and rB2 == "-Pick what?" and rB3 == "-Pick what?",
                "W4 a released pet / a bad value / a bad slot are refused (%s / %s / %s / %s)" % (rG, rB1, rB2, rB3))
        # ---- W5 the ability picker: Keep + only what the class tree has UNLOCKED; a pick on another key of the loadout trades places
        r = wsel(2)
        text = rbuild()
        K.check(int(pgw.view) == 6 and wcells() == ["rp:2|~", "rp:2|ArcaneBreach", "rp:2|ElementalImbue", "rp:2|RiftCleave"] and "Rune_Breach" in text
                and "Pick for Ability 2 of Loadout 1 - abilities unlocked in your class tree" in text,
                "W5 click Ability 2: Keep + the 3 unlocked abilities with their rune icons (Sunder is locked: not offered) (%s)" % wcells())
        r = wpick("rp:2|RiftCleave")
        L0 = WL()
        K.check(r.startswith("+Loadout 1 - Ability 2: Rift Cleave.") and L0.abOwn and str(L0.abCls) == "Spellblade" and [str(x) if x is not None else None for x in L0.ab] == ["RiftCleave", None, None, None],
                "W5 pick Rift Cleave for Ability 2 (%s)" % r)
        wsel(5)
        rbuild()
        wpick("rp:5|ArcaneBreach")
        rbuild()
        r = wpick("rp:5|RiftCleave")
        L0 = WL()
        lf = lfile()
        K.check(r.startswith("+Loadout 1 - Ability 3: Rift Cleave") and [str(x) if x is not None else None for x in L0.ab] == ["ArcaneBreach", "RiftCleave", None, None]
                and lf[0].get("abrows") == {"class": "Spellblade", "rows": ["ArcaneBreach", "RiftCleave", "", ""]} and "abil" not in lf[0],
                "W5 Rift Cleave onto Ability 3 while it is on Ability 2: the two trade places; saved as abrows (%s)" % lf.get(0))
        rL, rN, rE = run(Pw, 16, 0, "8|Sunder"), run(Pw, 16, 0, "8|Meteor"), wc("pk", v="empty")
        K.check(rL.startswith("-Sunder is not unlocked in your class tree yet") and rN.startswith("-That is not one of your Spellblade abilities")
                and rE.startswith("=An ability key always holds an ability"), "W5 a locked / a foreign ability / Empty are refused (%s / %s / %s)" % (rL, rN, rE))
        text = rbuild()
        sets = wsets(text)
        K.check(sets.get("SkyyRqR2Nm") == "Arcane Breach" and sets.get("SkyyRqR2Sb") == "Ability 2" and sets.get("SkyyRqR5Nm") == "Rift Cleave"
                and cutok(sets.get("SkyyRqR8Nm"), "Sunder") and cutok(sets.get("SkyyRqR8Sb"), "Crouch + 2 - Keep") and "Rune_Rift" in text
                and sets.get("SkyyRqR3Nm") == "Power+" and sets.get("SkyyRqR6Nm") == "Empty",
                "W5 the ability slots show icon + name + key; a Keep key shows what it holds (%s)" % sets)
        # fix a (critic: "Keep on an ability key is not always kept"): Crouch + 3 is Keep but Rift Cleave (on it now) is picked for Ability 3,
        # so Equip gives it Elemental Imbue (the one moved off) - the slot shows that, its line and its picker's Keep row say why
        wsel(11)
        t5 = rbuild()
        sets = wsets(t5)
        sp5 = wval("#SkyyRqSp.Text") or ""
        K.check(cutok(sets.get("SkyyRqR11Nm"), "Elemental Imbue") and cutok(sets.get("SkyyRqR11Sb"), "Crouch + 3 - Keep")
                and sp5 == "Keep: Crouch + Ability 3 has Rift Cleave now; Equip gives it Elemental Imbue (Rift Cleave is picked for Ability 3)."
                and "Gets Elemental Imbue at Equip (Rift Cleave is picked for another key)" in t5,
                "W5 fix a: a Keep key another pick takes shows + explains what Equip really leaves there (%s / %s)" % (sets.get("SkyyRqR11Nm"), sp5))
        sp_all("W5")
        # ---- W6 EQUIP applies them through the same bridges: pets loadoutSet(pet, summon), abilities = the live snapshot with the picks placed
        wsel(1)
        rbuild()
        wpick("rp:1|pb000002")
        state["pets"] = "pc000003|"
        state["calls"]["pets"][:] = []
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        want = "v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=RiftCleave;a1=Sunder;a2=ElementalImbue;mods="
        K.check(r.startswith("+Equipped Loadout 1") and state["calls"]["pets"] == [(uW, "pa000001", "pb000002")] and state["calls"]["abil"] == [want],
                "W6 Equip: pets:fn:loadoutSet(Rabbit, Wolf); class:fn:loadoutSet gets the live snapshot with Arcane Breach on Ability 2 and Rift Cleave on "
                "Ability 3 (Keep rows take what is left) (%s / %s / %s)" % (r, state["calls"]["pets"], state["calls"]["abil"]))
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(r.startswith("+Equipped Loadout 1") and state["calls"]["abil"] == [], "W6 Equip again: the abilities are already so - no call (%s)" % state["calls"]["abil"])
        # ---- W7 Keep at Equip = the live slot; all Keep = no call
        run(Pw, 16, 0, "0|~")
        run(Pw, 16, 0, "1|")
        state["pets"] = "pc000003|pb000002"
        state["calls"]["pets"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(state["calls"]["pets"] == [(uW, "pc000003", "")], "W7 pet Keep + summon None: loadoutSet(the live pet, '') (%s)" % state["calls"]["pets"])
        run(Pw, 16, 0, "1|~")
        L0 = WL()
        state["calls"]["pets"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(not L0.hasPets and state["calls"]["pets"] == [], "W7 both Keep = no pets saved, no call at Equip (%s)" % state["calls"]["pets"])
        # ---- W8 a STALE pet (released): the slot shows it greyed; Equip keeps that slot + a line
        run(Pw, 16, 0, "0|pb000002")
        del state["owned"]["pb000002"]
        state["pets"] = "pa000001|"
        text = rbuild()
        sets = wsets(text)
        state["calls"]["pets"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(sets.get("SkyyRqR0Nm") == "Gone pet" and "#SkyyRqR0Out" in text and "your picked pet is gone" in r and state["calls"]["pets"] == [],
                "W8 a released pet: shown greyed (Gone pet), Equip keeps the slot + says so, nothing sent (%s / %s)" % (r, state["calls"]["pets"]))
        state["owned"]["pb000002"] = "Rare Wolf Lv 12"
        # ---- W9 a STALE ability (no longer unlocked): greyed, Equip keeps that key + a line
        state["abil"] = SB
        state["usable"].discard("RiftCleave")
        text = rbuild()
        sets = wsets(text)
        wsel(5)
        t9 = rbuild()
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(sets.get("SkyyRqR5Sb") == "Ability 3" and "#SkyyRqR5Out" in text and "Not unlocked in your class tree now" in t9
                and "Rift Cleave is not unlocked in your class tree now, so Equip leaves Ability 3 as it is" in t9
                and "Rift Cleave is not unlocked now - Ability 3 kept what it had" in r and state["calls"]["abil"] == [],
                "W9 an ability no longer unlocked: greyed slot + greyed row in its picker; Equip keeps that key + says so, no change = no call (%s / %s)" % (r, state["calls"]["abil"]))
        sp_all("W9")
        state["usable"].add("RiftCleave")
        # ---- W10 another class: picks kept, a line, no call
        state["abil"] = "v=1;class=Mage;p1=Meteor;p2=FrostNova;a1=Starfall;a2=ArcaneBeam;mods="
        state["usable"] |= {"Meteor", "FrostNova", "Starfall", "ArcaneBeam"}
        text = rbuild()
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check("for a Spellblade - you are a Mage, so your abilities were kept" in r and state["calls"]["abil"] == [] and "SPELLBLADE" not in text and "- MAGE" in text
                and "#SkyyRqR2Out" in text, "W10 picks of another class: kept + a line, the slots greyed (%s)" % r)
        sp_all("W10")
        # fix b: Keep on another class's picks changes nothing (refused, the record stays as it is)
        lf_b = lfile().get(0)
        rK = run(Pw, 16, 0, "5|~")
        L0 = WL()
        K.check(rK.startswith("=Ability 3 already keeps your ability - this loadout's picks are for a Spellblade") and str(L0.abCls) == "Spellblade"
                and [str(x) if x is not None else None for x in L0.ab] == ["ArcaneBreach", "RiftCleave", None, None] and lfile().get(0) == lf_b,
                "W10 fix b: Keep on another class's picks is refused, nothing changes (%s)" % rK)
        r = run(Pw, 16, 0, "2|Meteor")
        L0 = WL()
        K.check(r.startswith("+Loadout 1 - Ability 2: Meteor (new Mage picks)") and str(L0.abCls) == "Mage" and [str(x) if x is not None else None for x in L0.ab] == ["Meteor", None, None, None],
                "W10 a pick for the new class starts the new class's picks (%s)" % r)
        state["abil"] = SB
        # ---- W11 Save pets/abilities = the quick "use what I have now" (0.2.2's record; Equip sends the saved snapshot EXACTLY)
        state["pets"] = "pa000001|pb000002"
        r = wc("sv")
        L0 = WL()
        lf = lfile()
        text = rbuild()
        sets = wsets(text)
        K.check(r.startswith("+Saved into Loadout 1: your pets and your abilities") and not L0.abOwn and str(L0.abil) == SB and not L0.petK and not L0.sumK
                and lf[0].get("pets") == {"pet": "pa000001", "summon": "pb000002"} and lf[0].get("abil") == SB and "abrows" not in lf[0] and "pets2" not in lf[0]
                and sets.get("SkyyRqR2Nm") == "Arcane Breach" and sets.get("SkyyRqR11Nm") == "Rift Cleave" and sets.get("SkyyRqR3Nm") == "Power+"
                and sets.get("SkyyRqR3Sb") == "Lv 3" and sets.get("SkyyRqR4Nm") == "Empty" and sets.get("SkyyRqR4Sb") == "Picked" and "Rock_Gem_Ruby" in text,
                "W11 Save pets/abilities: the live pets + snapshot in 0.2.2's record; the slots show the saved abilities + modifiers (%s / %s / %s)" % (r, sets, lf.get(0)))
        state["abil"] = "v=1;class=Spellblade;alt=A;p1=ElementalImbue;p2=ArcaneBreach;a1=Sunder;a2=RiftCleave;mods="
        state["calls"]["abil"][:] = []
        gap()
        run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == [SB], "W11 Equip of a saved loadout sends the saved snapshot exactly as 0.2.2 (%s)" % state["calls"]["abil"])
        state["abil"] = SB
        r = run(Pw, 16, 0, "11|ArcaneBreach")
        L0 = WL()
        K.check([str(x) if x is not None else None for x in L0.ab] == ["RiftCleave", "ElementalImbue", "Sunder", "ArcaneBreach"] and L0.abOwn and str(L0.abil) == SB
                and [str(x) if x is not None else None for x in L0.am] == [None, None, None, None, None, None, "Power", ""],
                "W11 a hand pick on a saved loadout starts from its saved rows + modifiers (Arcane Breach -> Crouch + 3 WITH its modifiers, Rift Cleave -> "
                "Ability 2) (%s / %s)" % (r, [str(x) if x is not None else None for x in L0.am]))
        state["meq"]["ArcaneBreach"] = ["Chain", "Power"]
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == ["v=1;class=Spellblade;alt=A;p1=RiftCleave;p2=ElementalImbue;a1=Sunder;a2=ArcaneBreach;mods=ArcaneBreach:Chain+-/ArcaneBreach:Power+-"]
                and "Sunder is not unlocked now - Crouch + Ability 2 kept what it had" in r and state["meq"]["ArcaneBreach"] == ["Power", ""] and "Skipped" not in r,
                "W11 Equip: the picks placed on the live rows + Arcane Breach's picked modifiers (Power moves slot 2 -> 1: cleared first, then set - it "
                "lands), the locked Sunder keeps its key (%s / %s)" % (r, state["calls"]["abil"]))
        state["abil"] = SB
        # ---- W12 every ability key Keep = the loadout no longer changes abilities
        for i_ in (2, 5, 8):
            run(Pw, 16, 0, "%d|~" % i_)
        r = run(Pw, 16, 0, "11|~")
        L0 = WL()
        state["calls"]["abil"][:] = []
        gap()
        run(Pw, 1, 0)
        K.check("no longer changes your abilities" in r and not L0.abOwn and L0.abil is None and state["calls"]["abil"] == [],
                "W12 all four keys Keep: abilities not saved any more, no call at Equip (%s)" % r)
        # ---- W13 saved + read back after a restart (the new fields survive)
        run(Pw, 16, 0, "0|pb000002")
        run(Pw, 16, 0, "1|~")
        run(Pw, 16, 0, "5|RiftCleave")
        restart()
        L0 = WL()
        K.check(L0.hasPets and not L0.petK and L0.sumK and str(L0.pet) == "pb000002" and L0.abOwn and str(L0.abCls) == "Spellblade"
                and [str(x) if x is not None else None for x in L0.ab] == [None, "RiftCleave", None, None], "W13 a restart reads pets2 + abrows back")
        cp_ = L0.copy()
        K.check(cp_.sumK and str(cp_.ab[1]) == "RiftCleave" and cp_.ab is not L0.ab, "W13 copy() carries the new fields (its own row array)")
        # ---- W14 a failed save rolls the pick back; a locked loadout refuses
        Store.FAIL_NEXT = 1
        rF = run(Pw, 16, 0, "2|ArcaneBreach")
        L0 = WL()
        rLk = run(Pw, 16, 9, "0|~")
        K.check(rF.startswith("-Could not save") and L0.ab[0] is None and str(L0.ab[1]) == "RiftCleave" and rLk.startswith("-") and ("locked" in rLk or "unlocks" in rLk),
                "W14 a failed save changes nothing; a locked loadout refuses (%s / %s)" % (rF, rLk))
        # ---- W15 missing mods: the slots hide, picks refuse, Equip says so
        pkeys = ("pets:fn:loadoutGet", "pets:fn:loadoutSet", "pets:fn:petName")
        saved_p = {k_: br.get(k_) for k_ in pkeys}
        for k_ in pkeys:
            br.remove(k_)
        text = rbuild()
        wsel(0)
        tP = rbuild()
        rP = run(Pw, 16, 0, "0|~")
        gap()
        rQ = run(Pw, 1, 0)
        K.check("#SkyyRqR0 {" not in text.replace("\\", "") and "#SkyyRqR2 {" in text.replace("\\", "") and "PETS NEED SKYYPETS" in text and "Pets in loadouts need SkyyPets" in tP
                and rP.startswith("-Pets in loadouts need SkyyPets") and "Pets in loadouts need SkyyPets 0.2.3 - your pets were not changed" in rQ,
                "W15 no SkyyPets: the pet slots hide, the picker / a pick say why, Equip notes it (%s / %s)" % (rP, rQ))
        for k_, v_ in saved_p.items():
            br.put(k_, v_)
        ckeys = ("class:fn:loadoutGet", "class:fn:loadoutSet", "class:fn:abilPanel")
        saved_c = {k_: br.get(k_) for k_ in ckeys}
        for k_ in ckeys:
            br.remove(k_)
        text = rbuild()
        rA = run(Pw, 16, 0, "2|~")
        K.check("#SkyyRqR2 {" not in text.replace("\\", "") and "#SkyyRqR0 {" in text.replace("\\", "") and "ABILITIES NEED SKYYCLASSES" in text
                and rA.startswith("-Abilities in loadouts need SkyyClasses"), "W15 no SkyyClasses: the ability slots hide, a pick says why (%s)" % rA)
        for k_, v_ in saved_c.items():
            br.put(k_, v_)
        br.remove("class:fn:abilPanel")
        text = rbuild()
        K.check("#SkyyRqR2 {" in text.replace("\\", "") and "Ingredient_Rune_Shard" in text and "Rift Cleave" in text,
                "W15 SkyyClasses without abilPanel: the slots work from class:fn:loadoutGet (the rune shard icon)")
        br.put("class:fn:abilPanel", saved_c["class:fn:abilPanel"])
        state["pstatus"] = "noclass"
        state["abil"] = None
        text = rbuild()
        rN = run(Pw, 16, 0, "2|ArcaneBreach")
        K.check("#SkyyRqR2 {" not in text.replace("\\", "") and "NO CLASS ABILITIES YET" in text and rN.startswith("-Your profile has no class abilities yet"),
                "W15 a profile without a class: the ability slots hide (%s)" % rN)
        state.pop("pstatus")
        state["abil"] = SB
        # ---- W16 ROLLBACK: the 0.2.3 jar (its own class loader) reads a 0.2.4 loadouts record - abmods ignored, never an error
        dR = Store.get(kW, Pw.u)
        L1 = dR.slots[1]
        L1.hasPets, L1.pet, L1.summon, L1.petK, L1.sumK, L1.abil = True, "pa000001", "pb000002", False, False, SB
        L1.abOwn, L1.abCls = True, "Spellblade"
        L1.ab[0] = "RiftCleave"
        L1.am[0], L1.am[1] = "Power", ""
        docR = str(Store.loadoutsDoc(dR).toJson())
        jR = {jn(x_.get("n")): x_ for x_ in json.loads(docR).get("loadouts", [])}
        K.check(jR[1].get("abmods") == {"class": "Spellblade", "m": ["Power", "", "~", "~", "~", "~", "~", "~"]}, "W16 (0.2.4) the record carries abmods (%s)" % jR[1].get("abmods"))
        URL_, URLCL_, File_ = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
        ua3 = JArray(URL_)(2)
        ua3[0] = File_(BASE023).toURI().toURL()
        ua3[1] = File_(B.SERVER_JAR).toURI().toURL()
        L022 = URLCL_(ua3, JClass("java.lang.ClassLoader").getPlatformClassLoader())
        S022, D022 = JClass(PKG + "WdStore", loader=L022), JClass(PKG + "WdData", loader=L022)
        d22 = D022(kW, uW)
        S022.loadoutsFrom(d22, JClass("org.bson.BsonDocument", loader=L022).parse(docR))
        a0, a1 = d22.slots[0], d22.slots[1]
        K.check(a1.hasPets and str(a1.pet) == "pa000001" and str(a1.abil) == SB and a1.abOwn and str(a1.ab[0]) == "RiftCleave"
                and str(JClass(PKG + "WdCfg", loader=L022).class_.getName()).endswith("WdCfg"),
                "W16 rollback: 0.2.3 reads the 0.2.4 record - pets, the saved snapshot, the ability picks as before; abmods ignored, never an error")
        L1.hasPets, L1.abil, L1.abOwn = False, None, False
        L1.ab[0] = None
        L1.am[0], L1.am[1] = None, None
        # ---- W17 Reset forgets the new picks too; no pet / item was made, moved or lost by any pick
        r1 = wc("rs")
        r2 = wc("rs")
        L0 = WL()
        lf = lfile()
        K.check(r2.startswith("+Loadout 1 was reset") and not L0.hasPets and not L0.abOwn and L0.ab[1] is None and 0 not in lf,
                "W17 Reset (asked twice) forgets the pet / ability picks (%s / %s)" % (r1, r2))
        K.check(open(pfile, "rb").read() == pf_bytes and not once(Pw) and not [1 for c_ in Pw.secs for i_ in range(int(c_.getCapacity())) if c_.getItemStack(JShort(i_)) is not None],
                "W17 the SkyyPets file was only read; no item appeared or moved for any pet / ability pick")
        # ============================================================ W18 FIX ROUND (wd023fix): one check per fix, EXECUTED
        state["abil"] = SB
        state["pets"] = "pa000001|"
        # ---- fix c: a key the class has no ability on (empty row) hides; a pick onto it is refused; Equip never moves an ability there
        r = run(Pw, 16, 0, "11|ArcaneBreach")
        SBE = "v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=;n1=Arcane Breach;n2=Elemental Imbue;n3=Sunder;mods="
        state["abil"] = SBE
        text = rbuild()
        state["calls"]["abil"][:] = []
        gap()
        rq = run(Pw, 1, 0)
        K.check(r.startswith("+") and "#SkyyRqR11 {" in text.replace("\\", "") and "#SkyyRqR11Out" in text
                and "Crouch + Ability 3 has no ability at your level - Arcane Breach stayed where it is" in rq and state["calls"]["abil"] == [],
                "W18 fix c: a pick on a key that is empty now: the slot greyed, Equip leaves the ability where it is + says so, no call (%s / %s)" % (rq, state["calls"]["abil"]))
        wsel(11)
        rbuild()
        spE = wval("#SkyyRqSp.Text") or ""
        K.check(spE == "Crouch + Ability 3 has no ability at your level: Equip leaves Arcane Breach where it is.", "W18 fix c: its slot line says why (%s)" % spE)
        run(Pw, 16, 0, "11|~")
        text = rbuild()
        rE = run(Pw, 16, 0, "11|ArcaneBreach")
        K.check("#SkyyRqR11 {" not in text.replace("\\", "") and "#SkyyRqR8 {" in text.replace("\\", "") and "PET, SUMMON + ABILITIES - SPELLBLADE" in text
                and "#SkyyRqR12 {" not in text.replace("\\", "") and "#SkyyRqR13 {" not in text.replace("\\", "")
                and rE.startswith("-Crouch + Ability 3 has no ability at your level yet") and not WL().abOwn,
                "W18 fix c: an empty key without a pick has no slot; a pick onto it is refused (%s)" % rE)
        sp_all("W18c")
        state["abil"] = "v=1;class=Spellblade;alt=A;p1=;p2=;a1=;a2=;mods="
        text = rbuild()
        K.check(not [1 for i_ in range(2, 14) if ("#SkyyRqR%d {" % i_) in text.replace("\\", "")] and "NO ABILITIES AT YOUR LEVEL YET" in text,
                "W18 fix c: no ability on any key yet: the four ability rows (+ their modifier cells) hide and the section line says why")
        # ---- fix b: picks for a NEW class keep the saved snapshot of the old class (its modifiers) until Save / Reset
        state["abil"] = SB
        rS = run(Pw, 2, 0)
        MG = "v=1;class=Mage;p1=Meteor;p2=FrostNova;a1=Starfall;a2=ArcaneBeam;mods="
        state["abil"] = MG
        rK = run(Pw, 16, 0, "5|~")
        L0 = WL()
        k_ok = str(L0.abil) == SB and not L0.abOwn
        rM = run(Pw, 16, 0, "2|FrostNova")
        L0 = WL()
        lf = lfile()
        K.check(rS.startswith("+Saved into Loadout 1") and rK.startswith("=Ability 3 already keeps your ability") and k_ok
                and "the saved Spellblade abilities stay until Save pets/abilities or Reset" in rM and str(L0.abil) == SB and L0.abOwn and str(L0.abCls) == "Mage"
                and lf[0].get("abil") == SB and lf[0].get("abrows") == {"class": "Mage", "rows": ["FrostNova", "", "", ""]},
                "W18 fix b: a new class's pick keeps the old class's saved snapshot (Keep on it refused) (%s / %s)" % (rK, rM))
        state["calls"]["abil"][:] = []
        gap()
        rq = run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == ["v=1;class=Mage;alt=A;p1=FrostNova;p2=Meteor;a1=Starfall;a2=ArcaneBeam;mods="],
                "W18 fix b: Equip places the Mage pick on the live Mage rows, no Spellblade modifiers ride along (%s)" % state["calls"]["abil"])
        rA = run(Pw, 16, 0, "2|~")
        L0 = WL()
        K.check("every Mage key is Keep (the saved Spellblade abilities stay)" in rA and not L0.abOwn and str(L0.abil) == SB and lfile()[0].get("abil") == SB,
                "W18 fix b: all Mage keys Keep clears only the Mage picks; the Spellblade snapshot stays (%s)" % rA)
        run(Pw, 3, 0)
        state["abil"] = SB
        # ---- fix d: the active pet + the loadout pets are listed first: a 1100-id owned list (none of them owned) cannot crowd them out
        run(Pw, 16, 1, "0|pc000003")
        br.put("pets:fn:owned", WFn(lambda u: JArray(JString)(["x%07d" % i_ for i_ in range(1100)])))
        pgw.petAt = 0
        wsel(0)
        rbuild()
        K.check(wcells()[:2] == ["rp:0|~", "rp:0|"] and "rp:0|pa000001" in wcells() and "rp:0|pc000003" in wcells(),
                "W18 fix d: the active pet and a loadout's pet are always offered, whatever the owned list holds (%s)" % wcells())
        br.remove("pets:fn:owned")
        pgw.petAt = 0
        # ---- fix e: Sort and Pick it / Take out / Forget in the picker views answer (no dead click)
        so0 = int(pgw.sort)
        text = rbuild()
        rS5, rD5, rT5, rF5 = wc("so"), wc("dp"), wc("dt"), wc("df")
        K.check("Sort: rarity, name" in text and rS5.startswith("=Pets are listed by rarity (Common first), then name") and int(pgw.sort) == so0
                and all(x_.startswith("=Pick it, Take out and Forget are for items of the pool - click a row above to pick it for the Pet slot") for x_ in (rD5, rT5, rF5)),
                "W18 fix e: the pet picker's Sort / Pick it / Take out / Forget answer (%s / %s)" % (rS5, rD5))
        wsel(2)
        text = rbuild()
        rS6 = wc("so")
        K.check("Sort: key order" in text and rS6.startswith("=Abilities are listed in key order") and int(pgw.sort) == so0,
                "W18 fix e: the ability picker's Sort answers (%s)" % rS6)
        # ---- fix f: every selected-slot line seen in W5 / W9 / W10 / W18 is short enough for its 44 px label (<= 130 characters)
        sp_all("W18")
        long_ = [(t_, i_, s_) for t_, i_, s_ in sp_seen if s_ is None or len(s_) > 130]
        K.check(len(sp_seen) >= 30 and not long_, "W18 fix f: %d selected-slot lines, all <= 130 characters (%s)" % (len(sp_seen), long_[:3]))
        # ============================================================ V 0.2.4 THE MODIFIER SLOTS (every new code path, EXECUTED)
        # cells: Ability 2 = 2 (mods 3, 4), Ability 3 = 5 (6, 7), Crouch + 2 = 8 (9, 10), Crouch + 3 = 11 (12, 13)
        state["abil"] = SB
        state["pets"] = "pa000001|"
        state["usable"] = {"ArcaneBreach", "ElementalImbue", "RiftCleave"}
        state["meq"] = {"ArcaneBreach": ["Power", ""], "ElementalImbue": ["", ""], "Sunder": ["", ""], "RiftCleave": ["Duration", ""]}
        run(Pw, 3, 0)
        run(Pw, 3, 0)
        nn8 = lambda a_: [str(x) if x is not None else None for x in a_]

        def ams():
            return nn8(WL().am)

        def abs_():
            return nn8(WL().ab)
        K8 = [None] * 8
        # ---- V1 Keep cells = the live modifiers of each row's ability
        text = rbuild()
        sets = wsets(text)
        K.check([sets.get("SkyyRqR%dNm" % i_) for i_ in (3, 4, 6, 7, 9, 10, 12, 13)] == ["Power+", "Empty", "Empty", "Empty", "Empty", "Empty", "Duration+", "Empty"]
                and "Rock_Gem_Ruby" not in text, "V1 a fresh loadout: the modifier cells show the live modifiers of each row (Keep: no icon) (%s)" % sets)
        # ---- V2 the modifier picker: Keep, Empty + the UNLOCKED modifiers of Arcane Breach in the tree's order
        r = wsel(3)
        text = rbuild()
        K.check(r.startswith("=Ability 2 modifier 1 of Loadout 1: pick on the right") and int(pgw.view) == 7 and wcells() == ["rp:3|~", "rp:3|", "rp:3|Radius", "rp:3|Power", "rp:3|Chain"]
                and "Pick for Ability 2 modifier 1 of Loadout 1 - modifiers unlocked in your class tree" in text and "Rock_Gem_Topaz" in text and "Rock_Gem_Zephyr" in text
                and "In slot 1 now" in text and "Sort: tree order" in text,
                "V2 click Ability 2 modifier 1: Keep, Empty, Radius / Power / Chain (Duration is locked: not offered), the Lattice icons (%s)" % wcells())
        rS7 = wc("so")
        K.check(rS7.startswith("=Modifiers are listed in your class tree's order"), "V2 the modifier picker's Sort answers (%s)" % rS7)
        wc("q", **{"@RqQ": "cha"})
        rbuild()
        K.check(wcells() == ["rp:3|~", "rp:3|", "rp:3|Chain"], "V2 the search filters modifiers by name (%s)" % wcells())
        wc("qc")
        rbuild()
        # ---- V3 a pick under a Keep row pins that row's ability; abmods saved
        r = wpick("rp:3|Chain")
        lf = lfile()
        K.check(r.startswith("+Loadout 1 - Ability 2 modifier 1 (Arcane Breach): Chain - Arcane Breach is now picked for Ability 2.") and abs_() == ["ArcaneBreach", None, None, None]
                and ams() == ["Chain"] + [None] * 7 and lf[0].get("abmods") == {"class": "Spellblade", "m": ["Chain"] + ["~"] * 7}
                and lf[0].get("abrows") == {"class": "Spellblade", "rows": ["ArcaneBreach", "", "", ""]},
                "V3 pick Chain for Ability 2 modifier 1: Arcane Breach pinned on Ability 2, saved as abmods (%s / %s)" % (r, lf.get(0)))
        # ---- V4 the cell: icon + name + Lv
        text = rbuild()
        sets = wsets(text)
        K.check(sets.get("SkyyRqR3Nm") == "Chain" and sets.get("SkyyRqR3Sb") == "Lv 3" and "Rock_Gem_Zephyr" in text and sets.get("SkyyRqR2Sb") == "Ability 2",
                "V4 the modifier cell shows the Lattice icon + Chain + Lv 3 (%s)" % sets)
        # ---- V5 the other slot's modifier trades places; a doubling modifier may sit in both
        r1 = run(Pw, 16, 0, "4|Power")
        r2 = run(Pw, 16, 0, "3|Power")
        K.check(r1.startswith("+") and r2.startswith("+Loadout 1 - Ability 2 modifier 1 (Arcane Breach): Power+ (it left modifier 2: Chain there).") and ams()[:2] == ["Power", "Chain"],
                "V5 Power onto modifier 1 while it sits in modifier 2: the two trade places (%s / %s)" % (r2, ams()))
        state["mdbl"].add(("ArcaneBreach", "Chain"))
        run(Pw, 16, 0, "3|Chain")
        K.check(ams()[:2] == ["Chain", "Chain"], "V5 a modifier the tree lets double may fill both slots (%s)" % ams())
        state["mdbl"].discard(("ArcaneBreach", "Chain"))
        run(Pw, 16, 0, "3|Power")
        # ---- V6 refusals; a closed slot shows Closed
        state["mslots"]["ElementalImbue"] = 1
        rL, rN, rC, rB = run(Pw, 16, 0, "3|Duration"), run(Pw, 16, 0, "3|Echo"), run(Pw, 16, 0, "7|Power"), run(Pw, 16, 0, "14|Power")
        text = rbuild()
        sets = wsets(text)
        K.check(rL.startswith("-Duration+ is not unlocked for Arcane Breach yet") and rN.startswith("-Echo is not one of Arcane Breach's modifiers")
                and rC.startswith("-Modifier slot 2 of Elemental Imbue is not open yet") and rB == "-Pick what?" and sets.get("SkyyRqR7Nm") == "Closed"
                and sets.get("SkyyRqR7Sb") == "Not open" and ams() == ["Power", "Chain"] + [None] * 6 and abs_()[1] is None,
                "V6 a locked / another ability's modifier, a closed slot (shown Closed), a bad slot are refused; nothing changed (%s / %s / %s / %s / %s / %s)" % (rL, rN, rC, rB, ams(), sets.get("SkyyRqR7Sb")))
        state["mslots"].pop("ElementalImbue")
        # ---- V7 EQUIP: one loadoutSet with mods=; again = no call
        state["meq"]["ArcaneBreach"] = ["Power", ""]
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == ["v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=RiftCleave;mods=ArcaneBreach:Power+Chain"]
                and state["meq"]["ArcaneBreach"] == ["Power", "Chain"] and r.startswith("+Equipped Loadout 1"),
                "V7 Equip: the live snapshot + mods=ArcaneBreach:Power+Chain, landed (%s / %s)" % (r, state["calls"]["abil"]))
        state["calls"]["abil"][:] = []
        gap()
        run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == [], "V7 Equip again: the modifiers are already so - no call (%s)" % state["calls"]["abil"])
        # ---- V8 the live slots are the other way round: clear-then-set, it lands (no doubling refusal)
        state["meq"]["ArcaneBreach"] = ["Chain", "Power"]
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(state["calls"]["abil"] == ["v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=RiftCleave;mods=ArcaneBreach:-+-/ArcaneBreach:Power+Chain"]
                and state["meq"]["ArcaneBreach"] == ["Power", "Chain"] and "Skipped" not in r,
                "V8 a swap of the two slots is sent clear-then-set and lands (%s / %s)" % (r, state["calls"]["abil"]))
        # ---- V9 Empty
        wsel(4)
        rbuild()
        rE = wc("pk", v="empty")
        text = rbuild()
        sets = wsets(text)
        state["calls"]["abil"][:] = []
        gap()
        run(Pw, 1, 0)
        K.check(rE.startswith("+Loadout 1 - Ability 2 modifier 2 (Arcane Breach): Empty") and ams()[:2] == ["Power", ""] and sets.get("SkyyRqR4Nm") == "Empty" and sets.get("SkyyRqR4Sb") == "Picked"
                and state["calls"]["abil"] == ["v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=RiftCleave;mods=ArcaneBreach:Power+-"] and state["meq"]["ArcaneBreach"] == ["Power", ""],
                "V9 the Empty button on a modifier slot: Empty, Equip takes it out (%s / %s)" % (rE, state["calls"]["abil"]))
        # ---- V10 a modifier no longer unlocked: greyed, skipped at Equip + a line; the kept slot trades places with the other slot's pick
        run(Pw, 16, 0, "4|Chain")
        state["munl"]["ArcaneBreach"].discard("Chain")
        state["meq"]["ArcaneBreach"] = ["Radius", "Power"]
        wsel(3)
        text = rbuild()
        wsel(4)
        t10 = rbuild()
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check("#SkyyRqR4Out" in text and "Chain is not unlocked for Arcane Breach now" in t10 and "Not unlocked for Arcane Breach now - Equip keeps this slot" in t10
                and "Chain is not unlocked for Arcane Breach now - modifier slot 2 skipped it" in r
                and state["calls"]["abil"] == ["v=1;class=Spellblade;alt=A;p1=ArcaneBreach;p2=ElementalImbue;a1=Sunder;a2=RiftCleave;mods=ArcaneBreach:-+-/ArcaneBreach:Power+Radius"]
                and state["meq"]["ArcaneBreach"] == ["Power", "Radius"],
                "V10 a modifier no longer unlocked: greyed cell + row; Equip skips it + says so, slot 2 hands Power to slot 1 and takes Radius (%s / %s / %s)" % (r, state["calls"]["abil"], ("#SkyyRqR4Out" in text, "Chain is not unlocked for Arcane Breach now" in t10,
                "Not unlocked for Arcane Breach now - Equip keeps this slot" in t10, state["meq"]["ArcaneBreach"])))
        sp_all("V10")
        state["munl"]["ArcaneBreach"].add("Chain")
        # ---- V11 an ability moved to another row takes its modifier picks (a crouch row too); V12 another ability starts Keep
        run(Pw, 16, 0, "4|Chain")
        r = run(Pw, 16, 0, "5|ArcaneBreach")
        K.check(abs_() == [None, "ArcaneBreach", None, None] and ams() == [None, None, "Power", "Chain", None, None, None, None],
                "V11 Arcane Breach picked for Ability 3 (it was Ability 2's pick): it moves WITH its modifiers (%s / %s)" % (r, ams()))
        r = run(Pw, 16, 0, "11|ArcaneBreach")
        K.check(abs_() == [None, None, None, "ArcaneBreach"] and ams() == [None] * 6 + ["Power", "Chain"],
                "V11 ... and on to Crouch + 3, still with them (%s / %s)" % (r, ams()))
        r = run(Pw, 16, 0, "11|RiftCleave")
        K.check(abs_() == [None, None, None, "RiftCleave"] and ams() == K8, "V12 another ability on the row: its modifier picks start as Keep (%s)" % ams())
        # ---- V13 an ability that does not land: its modifiers are skipped + a line, no call
        run(Pw, 16, 0, "12|Radius")
        K.check(ams() == [None] * 6 + ["Radius", None], "V13 Radius for Rift Cleave's modifier 1 (%s)" % ams())
        state["usable"].discard("RiftCleave")
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check("Rift Cleave is not unlocked now - Crouch + Ability 3 kept what it had" in r and "the modifiers picked for Rift Cleave were skipped (it is not unlocked now)" in r
                and state["calls"]["abil"] == [], "V13 a locked ability (still on its row): row kept + a line, its modifiers skipped + a line, no call (%s)" % r)
        state["usable"].add("RiftCleave")
        run(Pw, 16, 0, "11|~")
        run(Pw, 16, 0, "5|RiftCleave")
        run(Pw, 16, 0, "6|Radius")
        state["usable"].discard("RiftCleave")
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check("Rift Cleave is not unlocked now - Ability 3 kept what it had" in r and "the modifiers picked for Rift Cleave were skipped (it is not on Ability 3)" in r
                and state["calls"]["abil"] == [], "V13 a locked ability moved onto another key: key kept, its modifiers skipped + two lines, no call (%s)" % r)
        sp_all("V13")
        state["usable"].add("RiftCleave")
        # ---- V14 no class:fn:abilMods: the modifier cells hide, picks + Equip say why
        mfn = br.get("class:fn:abilMods")
        br.remove("class:fn:abilMods")
        text = rbuild()
        rM = run(Pw, 16, 0, "3|Power")
        wsel(3)
        t14 = rbuild()
        state["calls"]["abil"][:] = []
        gap()
        r = run(Pw, 1, 0)
        K.check(not [1 for i_ in (3, 4, 6, 7, 9, 10, 12, 13) if ("#SkyyRqR%d {" % i_) in text.replace("\\", "")] and "#SkyyRqR5 {" in text.replace("\\", "")
                and rM.startswith("-Modifiers in loadouts need SkyyClasses 0.1.22") and "Modifiers in loadouts need SkyyClasses 0.1.22" in t14
                and "Modifiers in loadouts need SkyyClasses 0.1.22 (class:fn:abilMods) - the modifiers of Rift Cleave were not changed" in r,
                "V14 without class:fn:abilMods the modifier cells hide; a pick, its picker and Equip say why (%s / %s)" % (rM, r))
        br.put("class:fn:abilMods", mfn)
        # ---- V15 records written by the 0.2.3 jar (its own class loader) read back by 0.2.4: ability picks kept, modifiers start as Keep
        ua4 = JArray(URL_)(2)
        ua4[0] = File_(BASE023).toURI().toURL()
        ua4[1] = File_(B.SERVER_JAR).toURI().toURL()
        L023 = URLCL_(ua4, JClass("java.lang.ClassLoader").getPlatformClassLoader())
        S023, D023 = JClass(PKG + "WdStore", loader=L023), JClass(PKG + "WdData", loader=L023)
        d23 = D023(kW, uW)
        recs = {2: ["RiftCleave", None, "Sunder", "ArcaneBreach"], 3: ["ArcaneBreach", None, None, None], 4: [None, None, "Sunder", "RiftCleave"]}
        for n_, rows_ in recs.items():
            L_ = d23.slots[n_]
            L_.abOwn, L_.abCls, L_.abil = True, "Spellblade", SB
            for q_ in range(4):
                L_.ab[q_] = rows_[q_]
            L_.hasPets, L_.pet, L_.summon = True, "pa000001", "pb000002"
        d23.slots[3].picks[0] = "x"
        doc23 = str(S023.loadoutsDoc(d23).toJson())
        d24 = JClass(PKG + "WdData")(kW, uW)
        Store.loadoutsFrom(d24, JClass("org.bson.BsonDocument").parse(doc23))
        ok15 = all(d24.slots[n_].abOwn and nn8(d24.slots[n_].ab) == rows_ and nn8(d24.slots[n_].am) == K8 and str(d24.slots[n_].abil) == SB and d24.slots[n_].hasPets
                   and str(d24.slots[n_].summon) == "pb000002" for n_, rows_ in recs.items())
        K.check(ok15 and str(d24.slots[3].picks[0]) == "x", "V15 0.2.3 records: all four ability picks kept (crouch rows too), modifiers start as Keep, pets + picks kept")
        doc24 = json.loads(str(Store.loadoutsDoc(d24).toJson()))
        r3 = {jn(x_.get("n")): x_ for x_ in doc24.get("loadouts", [])}
        K.check(r3[2]["abrows"]["rows"] == ["RiftCleave", "", "Sunder", "ArcaneBreach"] and not [1 for n_ in recs if "abmods" in r3[n_]] and r3[4].get("abil") == SB,
                "V15 the next save writes the same abrows and no abmods (%s)" % r3.get(2))
        # ---- V16 a restart reads abmods back (Radius picked for slot 1 while the live slot 2 holds it: the two trade places - Power to slot 2)
        state["abil"] = SB
        run(Pw, 3, 0)
        run(Pw, 3, 0)
        run(Pw, 16, 0, "3|Radius")
        run(Pw, 16, 0, "7|Power")
        restart()
        K.check(abs_() == ["ArcaneBreach", "ElementalImbue", None, None] and ams() == ["Radius", "Power", None, "Power", None, None, None, None]
                and WL().copy().am is not WL().am and nn8(WL().copy().am) == ams(),
                "V16 a restart reads abrows + abmods back; copy() carries its own modifier array (%s)" % ams())
        sp_all("V16")
        long_v = [(t_, i_, s_) for t_, i_, s_ in sp_seen if s_ is None or len(s_) > 130]
        K.check(not long_v, "V every selected-slot line <= 130 characters (%s)" % long_v[:3])
        # ---- V17 Save pets/abilities and Reset clear the modifier picks
        r = run(Pw, 2, 0)
        K.check(not WL().abOwn and ams() == K8 and str(WL().abil) == str(state["abil"]), "V17 Save pets/abilities clears the modifier picks (%s)" % r)
        run(Pw, 16, 0, "3|Power")
        run(Pw, 3, 0)
        run(Pw, 3, 0)
        K.check(not WL().abOwn and ams() == K8 and 0 not in lfile(), "V17 Reset forgets them")
        K.check(open(pfile, "rb").read() == pf_bytes and not once(Pw), "V no item appeared or moved for any modifier pick")
        # ============================================================ T 0.2.4 LIFELONG TOOLS (Skyy: "this shows my old crude hatchet after i upgraded to copper.
        # and its not letting me put my hoe in the items. but it allows the other tools."): every kind goes into Items; a tier-up; old-tier ghosts
        Pt = W.player("00000000-0000-0000-0000-000000000024", "Tia")
        kT = str(Store.pkey(Pt.u))
        Klass = P("WdClass")
        JShortT = JClass("java.lang.Short")
        LLDOC = '{"SkyyGear": {"v": 1, "r": "normal", "lvl": %d, "id": true, "src": "lifelong", "ll": 1, "lu": "%s"}}'
        TK = ["Tool_Pickaxe_Crude", "Tool_Hatchet_Crude", "Tool_Hoe_Crude", "Tool_Hoe_Copper", "Tool_Hoe_Iron", "Tool_Hoe_Thorium", "Tool_Sickle_Crude",
              "SkyyFishing_Rod_Bamboo", "Tool_Watering_Can"]
        cls_ = [str(Klass.classify(stack(i_, 1))) for i_ in TK]
        K.check(cls_ == ["i"] * len(TK), "T1 every lifelong kind (each hoe tier, plain or lifelong) classifies into the Items space (%s)" % cls_)
        for j_, i_ in enumerate(TK):
            setc(Pt.sto, j_, stack(i_, 1, (LLDOC % (3, "lu%02d" % j_)) if i_ != "Tool_Watering_Can" else None))
        rD = []
        for j_ in range(len(TK)):
            gap()
            rD.append(run(Pt, 6, 0, "2:%d" % j_))
        dT = Store.get(kT, Pt.u)
        K.check(all(r_.startswith("+") for r_ in rD) and all(ent_by_id(dT, i_) for i_ in TK), "T1 every lifelong kind deposits - the hoe too (%s)" % rD)
        EIDT = {i_: str(ent_by_id(dT, i_)[0].eid) for i_ in TK}
        rP = [run(Pt, 10, 0, "%d|e:%s" % (4 + j_, EIDT[i_])) for j_, i_ in enumerate(TK)]
        K.check(all(r_.startswith("+") for r_ in rP), "T1 ... and each is picked into a hotbar slot of a loadout (%s)" % rP)

        def tfind(eid_):
            for c_ in Pt.secs:
                for i_ in range(int(c_.getCapacity())):
                    x_ = c_.getItemStack(JShortT(i_))
                    if x_ is not None and str(Codec.stampOf(x_)) == eid_:
                        return c_, i_
            return None, None
        # ---- T2 a TIER-UP of a stamped lifelong tool (SkyyGear's Anvil: a new item id, every other metadata key carried - our stamp too)
        eH = EIDT["Tool_Hatchet_Crude"]
        gap()
        rF = run(Pt, 14, 0, eH)
        c_, i_ = tfind(eH)
        setc(c_, i_, stack("Tool_Hatchet_Copper", 1, '{"SkyyGear": {"v": 1, "r": "normal", "lvl": 12, "id": true, "src": "lifelong", "ll": 1, "lu": "lu01"}, "SkyyRequip": {"e": "%s"}}' % eH))
        run(Pt, 5, 0)
        eHe = Store.get(kT, Pt.u).entry(eH)
        K.check(rF.startswith("+") and eHe is not None and str(eHe.sid) == "Tool_Hatchet_Copper" and int(eHe.lv) == 12 and str(eHe.lu) == "lu01" and not ein(eHe)
                and str(Store.get(kT, Pt.u).slots[0].picks[5]) == "e:" + eH,
                "T2 the tiered-up hatchet is the SAME entry (stamp, not id): its display follows (Copper, Lv 12), the loadout pick stays (%s)" % ((rF, None if eHe is None else (str(eHe.sid), int(eHe.lv), str(eHe.lu), ein(eHe)), str(Store.get(kT, Pt.u).slots[0].picks[5]), eH, c_ is not None, [str(x_) for x_ in P("WdLog").LINES if "tidy" in str(x_).lower()][:3]),))
        # ---- T3 a GHOST of the same lifelong tool (same lu) next to the real one: picks move, the record goes, nothing else changes
        setc(Pt.sto, 20, stack("Tool_Hatchet_Iron", 1, LLDOC % (20, "lu01")))
        gap()
        r3 = run(Pt, 6, 0, "2:20")
        eC = [str(e_.eid) for e_ in ent_by_id(Store.get(kT, Pt.u), "Tool_Hatchet_Iron") if ein(e_)][0]
        t0 = int(Ops.TIDIED)
        run(Pt, 5, 0)
        K.check(r3.startswith("+") and Store.get(kT, Pt.u).entry(eH) is not None and int(Ops.TIDIED) == t0,
                "T3 both copies present (one on you, one IN Requip) = no ghost, nothing tidied")
        c_, i_ = tfind(eH)
        setc(c_, i_, None)   # the copper copy is gone (dropped / broken / retired by SkyyGear)
        eP = EIDT["Tool_Pickaxe_Crude"]
        gap()
        run(Pt, 14, 0, eP)
        c2_, i2_ = tfind(eP)
        setc(c2_, i2_, None)   # the pickaxe is gone too - but it has NO twin: it stays NOT WITH YOU
        run(Pt, 5, 0)
        dT = Store.get(kT, Pt.u)
        lg_ = open(os.path.join(Wd, "requip.log"), encoding="utf8").read()
        K.check(dT.entry(eH) is None and str(dT.slots[0].picks[5]) == "e:" + eC and int(Ops.TIDIED) == t0 + 1 and dT.entry(eP) is not None
                and ("LIFELONG-TIDY " + str(Pt.u)) in lg_ and (eH + "(Tool_Hatchet_Copper)->" + eC) in lg_ and ein(dT.entry(eC)),
                "T3 the not-with-you record of the same lifelong hatchet merges into the one in Requip (pick moved, record gone, logged); a lone "
                "NOT WITH YOU pickaxe stays (%s)" % ((dT.entry(eH) is None, str(dT.slots[0].picks[5]), eC, int(Ops.TIDIED) - t0, dT.entry(eP) is not None, ("LIFELONG-TIDY " + str(Pt.u)) in lg_, lg_[-400:]),))
        # ---- T4 THE ONE-TIME PASS (run-once marker llDone in index.json): plain tool records (no SkyyGear document - Skyy's 'Hatchet Crude')
        ixT = os.path.join(Wd, "requip", kT, "index.json")

        def plain_ghost(slot_, iid):
            setc(Pt.sto, slot_, stack(iid, 1))
            gap()
            run(Pt, 6, 0, "2:%d" % slot_)
            e_ = [str(x_.eid) for x_ in ent_by_id(Store.get(kT, Pt.u), iid) if str(x_.lu) == "" and int(x_.lv) < 0 and ein(x_)][0]
            gap()
            run(Pt, 14, 0, e_)
            c9_, i9_ = tfind(e_)
            setc(c9_, i9_, None)   # gone (broken / dropped)
            return e_
        dT = Store.get(kT, Pt.u)
        K.check(bool(dT.llDone) and json.load(open(ixT)).get("llDone") is True, "T4 a profile born under 0.2.4 starts with the marker (saved in index.json)")
        ePl = plain_ghost(21, "Tool_Hoe_Crude")
        run(Pt, 10, 1, "4|e:" + ePl)
        o0 = int(Ops.ONCE_RUNS)
        run(Pt, 5, 0)
        kept4 = Store.get(kT, Pt.u).entry(ePl) is not None and int(Ops.ONCE_RUNS) == o0
        # a 0.2.3 profile: index.json without the marker -> the pass runs ONCE on the records that exist now
        jx = json.load(open(ixT))
        jx.pop("llDone", None)
        json.dump(jx, open(ixT, "w"))
        # much later (the saved journal's keep window is over - else the restart repair rightly undoes the last withdrawal of the gone hoe)
        jf_ = os.path.join(Wd, "requip", kT, "journal.json")
        if os.path.exists(jf_):
            os.remove(jf_)
        restart()
        was = bool(Store.get(kT, Pt.u).llDone)
        eg_ = Store.get(kT, Pt.u).entry(ePl)
        dbg4 = None if eg_ is None else (bool(eg_.kind), eg_.raw is None, sorted(str(k_) for k_ in Inv.stamps(Ops.secs(Pt.st, Pt.ref)).keySet()), ein(eg_), str(eg_.lu), str(eg_.rar), int(eg_.lv), str(eg_.sid), str(eg_.itemId()), int(Codec.llFam(eg_.itemId())), [(str(x_.eid), ein(x_), str(x_.itemId()), None if x_.stack is None else str(Codec.lu(x_.stack)), None if x_.stack is None or x_.stack.getMetadata() is None else str(x_.stack.getMetadata().toJson())[:160]) for x_ in Store.get(kT, Pt.u).entries.values() if str(x_.itemId()).startswith("Tool_Hoe")])
        histd = os.path.join(Wd, "history")
        h0 = set(os.listdir(histd)) if os.path.isdir(histd) else set()
        run(Pt, 5, 0)
        dT = Store.get(kT, Pt.u)
        hoesIn = sorted(EIDT[i_] for i_ in TK if i_.startswith("Tool_Hoe_") and ein(dT.entry(EIDT[i_])))
        hnew = sorted(n_ for n_ in (set(os.listdir(histd)) if os.path.isdir(histd) else set()) - h0 if n_.startswith("requip-lltidy-" + kT + "-"))
        hfiles = sorted(os.listdir(os.path.join(histd, hnew[0]))) if hnew else []
        lg_ = open(os.path.join(Wd, "requip.log"), encoding="utf8").read()
        lone = [l_ for l_ in lg_.splitlines() if "LIFELONG-ONCE " + str(Pt.u) in l_]
        K.check(kept4 and not was and dT.entry(ePl) is None and str(dT.slots[1].picks[4]) == "e:" + hoesIn[0] and bool(dT.llDone)
                and json.load(open(ixT)).get("llDone") is True and int(Ops.ONCE_RUNS) == o0 + 1 and len(hnew) == 1 and "index.json" in hfiles
                and "loadouts.json" in hfiles and len(lone) == 1 and (ePl + "(Tool_Hoe_Crude)->" + hoesIn[0]) in lone[0] and "undo:" in lone[0] and hnew[0] in lone[0],
                "T4 the one-time pass: with the marker it never touches a plain record; a 0.2.3 profile (no marker) runs it ONCE - History copy of "
                "the files first, the plain hoe record merges into the lifelong hoe with the LOWEST eid (deterministic), one LIFELONG-ONCE line "
                "with the Undo, the marker saved (%s / %s / %s / %s)" % (kept4, was, dbg4, (hnew, hfiles, lone[:1], str(dT.slots[1].picks[4]), hoesIn[:1])))
        # never again after the marker: a later plain hoe AND a plain pickaxe (its lifelong pickaxe present) are never merged
        setc(Pt.sto, 23, stack("Tool_Pickaxe_Copper", 1, LLDOC % (8, "luPX")))
        gap()
        run(Pt, 6, 0, "2:23")
        eP2 = plain_ghost(24, "Tool_Hoe_Crude")
        eP3 = plain_ghost(25, "Tool_Pickaxe_Iron")
        run(Pt, 5, 0)
        if os.path.exists(jf_):
            os.remove(jf_)
        restart()
        run(Pt, 5, 0)
        dT = Store.get(kT, Pt.u)
        K.check(dT.entry(eP2) is not None and dT.entry(eP3) is not None and int(Ops.ONCE_RUNS) == o0 + 1 and bool(dT.llDone),
                "T4 never again after the marker (a restart too): a later plain hoe record and a plain pickaxe record stay NOT WITH YOU")
        dT = Store.get(kT, Pt.u)
        K.check(all(ein(dT.entry(EIDT[i_])) for i_ in TK if i_ not in ("Tool_Hatchet_Crude", "Tool_Pickaxe_Crude")) and ein(dT.entry(eC)),
                "T the tidy never touched an entry that is IN Requip (only not-with-you records were merged)")
        run(Pw, 3, 1)
        pgw.handleDataEvent(Pw.ref, Pw.st, '{"a":"close"}')
        state.pop("owned")
        state.pop("usable")
        br.remove("class:fn:abilPanel")
        br.remove("class:fn:abilMods")
        br.put("class:fn:loadoutSet", abil_set_0)
        state["abil"] = abil_keep if abil_keep is not None else "v=1;class=Mage;p1=Meteor;n1=Meteor"

        # ============================================================ X17 the commands (player + admin forms)
        Cmds = P("WdCmds")
        Pg.pr.msgs = None
        for a_ in (["help"], ["dump"], ["auto"], ["auto", "off"], ["1"], ["equip", "2"], ["save", "1"], ["wear", "2"], ["name", "2", "Mine"], ["dance", "2"]):
            gap()
            Cmds.player(Pg.pr, Pg.ref, Pg.st, JArray(JString)(a_))
        said = [str(x) for x in (Pg.pr.msgs or [])]
        K.check(len(said) == 10 and said[0].startswith("[Requip] /requip opens") and said[2].startswith("[Requip] Auto-store is ON") and said[3].startswith("[Requip] Auto-store is OFF")
                and "Equipped" in said[4] and "Equipped" in said[5] and "Saved into" in said[6] and "now uses what you wear" in said[7] and "Mine" in said[8] and "/requip opens" in said[9],
                "X17 /requip help | dump | auto | auto off | <n> | equip | save | wear | name | unknown (%s)" % said)
        res = [str(Cmds.admin(None, JArray(JString)(a_))) for a_ in (["help"], ["info", "Pia"], ["slots", "Pia", "9"], ["slots", "Pia", "99"], ["info", "Nobody"])]
        nt_ = drain(H) if False else 0
        time.sleep(0.4)
        nt_ = drain(H)
        K.check(res[0].startswith("=/requipadmin") and res[1].startswith("=" + kPg) and res[2].startswith("=Slots change queued") and nt_ == 1 and Store.get(kPg, Pg.u).floor == 9
                and res[3].startswith("-Slots is 0") and res[4].startswith("-Nobody is not online"), "X17 /requipadmin forms; slots runs on the player's world thread (%s)" % res)

        # ============================================================ X18 the bridge functions (research/Requip-Smithing-Spec.md section 5)
        Fn = P("WdFn")
        Q = W.player("00000000-0000-0000-0000-000000000018", "Quin")
        kQ = str(Q.u)

        def fa(mode, *args):
            a = JArray(JObject)(len(args))
            for i, x in enumerate(args):
                a[i] = x
            return Fn(mode).apply(a)
        TPM = JClass(TESTPM)
        TPM.OPENS = 0
        K.check(bool(Fn(0).apply(Q.u)) and drain(H) == 1 and TPM.OPENS == 1 and str(TPM.CUR.getClass().getSimpleName()) == "WdPage"
                and not bool(Fn(0).apply("x")) and not bool(Fn(0).apply(UUID_.randomUUID())), "X18 wardrobe:fn:open (+ requip:fn:open): the page opens on the world thread; bad / offline -> FALSE")
        K.check(fa(1, Q.u, "Armor_Iron_Head", JInt(1)) is None and str(fa(1, Q.u, "Rock_Stone", JInt(5))).startswith("Blocks") and str(fa(1, Q.u, "Gone_Item", JInt(1))).startswith("The game no longer knows"),
                "X18 canDeposit: armor accepted (null), a block / an unknown id refused with the reason")
        Cfg.ARMOR_CAP = 0 + 1
        setc(Q.sto, 0, stack("Armor_Gold_Head", 1))
        r = str(fa(2, Q.u, "storage", JInt(0)))
        K.check(r.startswith("eid:") and len(r) == 20 and str(fa(1, Q.u, "Armor_Iron_Head", JInt(1))) == "Armor space full (1)", "X18 depositSlot -> eid:<hex>; then canDeposit says the space is full (%s)" % r)
        Cfg.ARMOR_CAP = 1000
        setc(Q.hot, 3, stack("Rock_Stone", 4))
        r2 = str(fa(2, Q.u, "hotbar", JInt(3)))
        r3 = str(fa(2, Q.u, "pocket", JInt(3)))
        K.check(r2.startswith("refused:Blocks") and r3.startswith("refused:unknown section"), "X18 depositSlot refusals (%s / %s)" % (r2, r3))
        craft = stack("Weapon_Sword_Mithril", 1, gdoc("rare", 33))
        r = str(fa(3, Q.u, craft, "smithing", '{"inv": {"Wood_Oak_Log": 5}}'))
        dQ = Store.get(kQ, Q.u)
        eC = dQ.entry(r[4:])
        K.check(r.startswith("eid:") and eC is not None and ein(eC) and str(Codec.rar(eC.stack)) == "rare", "X18 deposit (a crafted stack in no inventory) -> eid:<hex>, IN (%s)" % r)
        r = str(fa(3, Q.u, stack("Potion_Health", 3), "smithing", ""))
        K.check(r.startswith("kind:") and int(Store.get(kQ, Q.u).entry(r[5:]).count) == 3, "X18 deposit of a stackable -> kind:<hex> (%s)" % r)
        # a craft deposit that crashed: materials back (the engine rolled the inventory back) -> undone; materials gone -> kept
        for back in (True, False):
            setc(Q.sto, 20, stack("Ingredient_Bar_Iron", 5 if back else 1))
            Tx.CRASH_AT = 0
            died = False
            try:
                fa(3, Q.u, stack("Weapon_Bow_Wood", 1, gdoc("unique", 44 if back else 45)), "smithing", '{"inv": {"Ingredient_Bar_Iron": 5}}')
            except Exception as ex_:
                died = "harness crash" in str(ex_)
            Tx.CRASH_AT = -1
            restart()
            r = run(Q, 5)
            bows = [e for e in Store.get(kQ, Q.u).entries.values() if str(e.itemId()) == "Weapon_Bow_Wood"]
            K.check(died and (len(bows) == (0 if back else 1)) and (("undone" in r) == back), "X18 a crashed craft deposit, materials %s: %s (%s)" % ("back" if back else "spent", "undone" if back else "kept", r))
            Q.sto.removeItemStackFromSlot(JShort(20), False)
        lst = fa(4, Q.u, "armor")
        lsi = [x for x in fa(4, Q.u, "items") if str(x[1]) == "Weapon_Sword_Mithril"]
        K.check(len(lst) == 1 and str(lst[0][1]) == "Armor_Gold_Head" and len(lsi) == 1 and sorted(str(x[1]) for x in fa(4, Q.u, "items")) == ["Weapon_Bow_Wood", "Weapon_Sword_Mithril"]
                and len(fa(4, Q.u, "all")) == 3, "X18 list: IN gear only (kinds left out), per space")
        lst[0][2].put("x", JClass("org.bson.BsonString")("y")) if lst[0][2] is not None else None
        K.check(Store.get(kQ, Q.u).entry(str(lst[0][0])).stack.getMetadata() is None or not Store.get(kQ, Q.u).entry(str(lst[0][0])).stack.getMetadata().containsKey("x"),
                "X18 list hands out COPIES (changing one changes nothing)")
        r = str(fa(5, Q.u, str(lsi[0][0])))
        r2 = str(fa(5, Q.u, str(lsi[0][0])))
        K.check(r == "ok" and r2.startswith("It is not in Requip right now") and str(lsi[0][0]) in stamps_of(Q), "X18 fetch: ok (stamp kept, OUT); again: the reason (%s / %s)" % (r, r2))
        rp = run(Q, 10, 0, "4|e:" + str(lsi[0][0]))
        K.check(rp.startswith("+") and bool(fa(6, Q.u, str(lsi[0][0]), "merged")) and not bool(fa(6, Q.u, str(lst[0][0]), "merged")) and str(Store.get(kQ, Q.u).entry(str(lsi[0][0])).gone) == "merged"
                and run(Q, 10, 1, "4|e:" + str(lsi[0][0])).startswith("-That item is used up (merged)"), "X18 gone: an OUT entry is marked used up (merged); an IN entry refuses; it cannot be picked any more")
        for c in Q.secs:
            for i in range(int(c.getCapacity())):
                if Codec.stampOf(getc(c, i)) == lsi[0][0]:
                    c.removeItemStackFromSlot(JShort(i), False)
        gap()
        r = run(Q, 1, 0)
        K.check("Hotbar 1: Weapon_Sword_Mithril is used up (merged)" in r, "X18 a picked item that was used up: Equip notes it (%s)" % r)
        # off the player's world thread: null (never blocks, never hops)
        other = JClass("java.lang.Thread")()
        E.jf(JClass("com.hypixel.hytale.component.Store"), "thread").set(Q.st, other)
        K.check(fa(2, Q.u, "storage", JInt(0)) is None and fa(4, Q.u, "all") is None and fa(5, Q.u, "x") is None and fa(3, Q.u, craft, "s", "") is None
                and fa(6, Q.u, "x", "y") is None, "X18 every world-thread fn answers null off the world thread (the REAL Store.isInThread)")
        E.jf(JClass("com.hypixel.hytale.component.Store"), "thread").set(Q.st, JClass("java.lang.Thread").currentThread())
        K.check(fa(2, "x") is None and Fn(4).apply("x") is None, "X18 bad arguments -> null")

        # ============================================================ X19 join task, timer, quit, auto-store, admin repair through the hop
        Jn = W.player("00000000-0000-0000-0000-000000000019", "Jo")
        kJ = str(Jn.u)
        setc(Jn.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 1)))
        setc(Jn.hot, 4, stack("Wood_Oak_Log", 2))
        run(Jn, 10, 0, "8|pocket") if False else None
        setc(Jn.hot, 0, stack("Wood_Oak_Log", 2))
        run(Jn, 10, 0, "4|pocket")
        Jn.hot.removeItemStackFromSlot(JShort(0), False)
        state.setdefault("bags", {})[str(Jn.u)] = {"Wood_Oak_Log": 50}
        gap()
        run(Jn, 1, 0)
        base, _ = census(Jn)
        Tx.CRASH_AT = 0
        try:
            run(Jn, 6, 0, "2:0")
        except Exception:
            pass
        Tx.CRASH_AT = -1
        restart()
        br.remove("requip:pocket:" + kJ)
        PRE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent")
        evr = U.allocateInstance(PRE.class_)
        E.jf(PRE, "playerRef").set(evr, Jn.ref)
        br.put("profile:busy:" + kJ, True)
        P("WdReady")().accept(evr)
        time.sleep(2.6)
        n1 = drain(H)
        K.check(n1 == 1 and os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")), "X19 join: the repair task waits while profile:busy (%d tasks)" % n1)
        br.remove("profile:busy:" + kJ)
        time.sleep(1.4)
        n2 = drain(H)
        c, d = census(Jn)
        pm = br.get("requip:pocket:" + kJ)
        K.check(n2 == 1 and not os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")) and c == base and not once(Jn, d)
                and pm is not None and dict((int(k_), str(v)) for k_, v in pm.items()) == {0: "Wood_Oak_Log"},
                "X19 ... then repairs on the world thread and publishes requip:pocket of the last worn loadout (%d tasks)" % n2)
        P("WdReady")().accept(evr)
        time.sleep(2.4)
        K.check(drain(H) == 0, "X19 PlayerReadyEvent again (a world switch): once per session")

        @JImplements(PKG + "WdApi")
        class Api:
            @JOverride
            def online(self):
                return JArray(UUID_)([Jn.u])

            @JOverride
            def byName(self, n):
                return Jn.u

            @JOverride
            def nameOf(self, u):
                return "Jo"

            @JOverride
            def tell(self, u, t, c):
                pass
        P("WdEng").API = Api()
        Gate.EPOCH.put(Jn.u, JLong(1))
        br.put("profile:epoch:" + kJ, JLong(2))
        state.setdefault("key", {})[kJ] = kJ + "-p2"
        P("WdTimer")().run()
        K.check(br.get("requip:pocket:" + kJ) is None and Gate.settleLeft(Jn.u, int(time.time() * 1000)) > 25000,
                "X19 the timer sees the profile switch: settle window + requip:pocket of the old profile dropped")
        del state["key"][kJ]
        Gate.EPOCHAT.clear()
        Gate.BUSYAT.clear()
        # auto-store: plain armor / weapons / tools from storage + backpack (never the hotbar, potions, blocks or stamped items)
        setc(Jn.sto, 5, stack("Armor_Copper_Legs", 1))
        setc(Jn.sto, 6, stack("Potion_Health", 2))
        setc(Jn.sto, 7, stack("Rock_Stone", 2))
        setc(Jn.bak, 0, stack("Tool_Hatchet_Iron", 1))
        setc(Jn.hot, 6, stack("Weapon_Bow_Wood", 1))
        st_before = stamps_of(Jn)
        Cfg.AUTO_HOT = False
        run(Jn, 11, 0, "on")
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na = drain(H)
        dJ = Store.get(kJ, Jn.u)
        K.check(na == 1 and getc(Jn.sto, 5) is None and getc(Jn.bak, 0) is None and getc(Jn.sto, 6) is not None and getc(Jn.sto, 7) is not None
                and getc(Jn.hot, 6) is not None and getc(Jn.sto, 0) is None and stamps_of(Jn) == st_before and any("Auto-stored 3 items" in str(m) for m in (Jn.pr.msgs or [])),
                "X19 auto-store ON: the timer queues a world task that stores the plain sword, copper legs + hatchet only (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        P("WdTimer")().run()
        K.check(drain(H) == 0, "X19 auto-store waits autoStore.seconds between runs")
        aj = json.load(open(os.path.join(Wd, "requip", "autostore.json")))
        K.check(aj["players"].get(kJ) is True, "X19 the per-player switch is saved (autostore.json)")
        Auto.load(Auto.FILE)
        K.check(bool(Auto.isOn(Jn.u)), "X19 ... and read back after a restart")
        Cfg.AUTO_ON = False
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        K.check(drain(H) == 0, "X19 the server switch off: no auto-store runs")
        Cfg.AUTO_ON = True
        # FIX-F1 (fidelity critic 1) + FIX2-F1 (fixer 2, fidelity critic 1): autoStore.hotbar (default on) takes gear that ARRIVES in the
        # hotbar (pickups) - never what was already there (your own tools) and never the HELD slot
        ASIC = JClass("com.hypixel.hytale.server.core.inventory.ActiveSlotInventoryComponent")
        hotc = Jn.st.comps.get(Jn.ref).get(W.types["hot"])
        E.jf(ASIC, "activeSlot").set(hotc, JByte(3))
        setc(Jn.hot, 3, stack("Weapon_Sword_Iron", 1))
        Cfg.AUTO_HOT = True
        Auto.SEEN.clear()
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na0 = drain(H)
        K.check(na0 == 1 and getc(Jn.hot, 6) is not None and getc(Jn.hot, 3) is not None and not any("Auto-stored" in str(m) for m in (Jn.pr.msgs or [])),
                "FIX2-F1 auto-store's first look at the hotbar: the bow already in hotbar 7 and the held sword are YOURS - nothing is swept (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        setc(Jn.hot, 7, stack("Tool_Pickaxe_Iron", 1))
        setc(Jn.hot, 8, stack("Weapon_Bow_Wood", 1))
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        P("WdTimer")().run()
        na = drain(H)
        K.check(na == 1 and int(Ops.heldSlot(Jn.st, Jn.ref)) == 3 and getc(Jn.hot, 7) is None and getc(Jn.hot, 6) is not None and getc(Jn.hot, 8) is None
                and getc(Jn.hot, 3) is not None and getc(Jn.hot, 0) is not None and any("Auto-stored 2 items" in str(m) for m in (Jn.pr.msgs or [])),
                "FIX-F1/FIX2-F1 auto-store with autoStore.hotbar: the pickaxe and the 2nd bow that ARRIVED in the hotbar go in; the bow that was there, the HELD sword (4) and the pocket blocks stay (%s)" % [str(m) for m in (Jn.pr.msgs or [])])
        Auto.LASTRUN.clear()
        Jn.pr.msgs = None
        Jn.hot.removeItemStackFromSlot(JShort(6), False)
        P("WdTimer")().run()
        drain(H)
        setc(Jn.hot, 5, stack("Weapon_Bow_Wood", 1))
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        K.check(getc(Jn.hot, 5) is None, "FIX2-F1 ... a bow dropped from the hotbar and picked up again is a pickup: it goes in")
        Auto.SEEN.put(Jn.u, JArray(JObject)([JLong(-99), JClass("java.util.HashMap")()]))
        hk_ = Auto.hotKeep(Jn.u, JArray(JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer"))(Jn.secs))
        K.check(hk_ is None, "FIX2-F1 ... after a profile switch (another epoch) the new hotbar is looked at fresh (nothing swept)")
        picks = [e for e in ent_by_id(Store.get(kJ, Jn.u), "Tool_Pickaxe_Iron") if ein(e)]
        r = run(Jn, 8, 0, str(picks[0].eid))
        where = [(i, x) for i, x in enumerate(Jn.secs) for q in range(int(x.getCapacity())) if getc(x, q) is not None and str(getc(x, q).getItemId()) == "Tool_Pickaxe_Iron"]
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        where2 = [(i, q) for i, x in enumerate(Jn.secs) for q in range(int(x.getCapacity())) if getc(x, q) is not None and str(getc(x, q).getItemId()) == "Tool_Pickaxe_Iron"]
        K.check(r.startswith("+Taken out: Tool_Pickaxe_Iron") and len(where) == 1 and len(where2) == 1,
                "FIX-F1 what you Take out stays out: auto-store does not put the taken-out pickaxe straight back (%s, %s)" % (r, where2))
        sec_, sl_ = where2[0]
        Jn.secs[sec_].removeItemStackFromSlot(JShort(sl_), False)
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        setc(Jn.sto, 9, stack("Tool_Pickaxe_Iron", 1))
        Auto.LASTRUN.clear()
        P("WdTimer")().run()
        drain(H)
        K.check(getc(Jn.sto, 9) is None and Auto.KEEP.get(Jn.u) is not None and Auto.KEEP.get(Jn.u).isEmpty(),
                "FIX-F1 ... the keep-out shrinks when you no longer carry it: a pickaxe picked up later is auto-stored again")
        # ---- O 0.2.5 TAKE OUT STAYS OUT (Skyy: "make it so, if you click take out, the auto store doesn't put it back in automatically.")
        kJp = str(Store.pkey(Jn.u))

        def find_id(iid):
            return [(i_, q_) for i_, c_ in enumerate(Jn.secs) for q_ in range(int(c_.getCapacity())) if getc(c_, q_) is not None and str(getc(c_, q_).getItemId()) == iid]

        def auto_run():
            Auto.LASTRUN.clear()
            P("WdTimer")().run()
            drain(H)
        pk0 = [e for e in ent_by_id(Store.get(kJ, Jn.u), "Tool_Pickaxe_Iron") if ein(e)]
        gap()
        rO = run(Jn, 8, 0, str(pk0[0].eid))
        wO = find_id("Tool_Pickaxe_Iron")
        xO = getc(Jn.secs[wO[0][0]], wO[0][1]) if len(wO) == 1 else None
        K.check(rO.startswith("+Taken out: Tool_Pickaxe_Iron") and "auto-store leaves it" in rO and xO is not None and str(Codec.outOf(xO)) == kJp
                and Codec.stampOf(xO) is None, "O1 Take out marks THAT item SkyyRequipOut {p: the profile key}, no stamp (%s)" % rO)
        Auto.KEEP.clear()       # a relog / restart: 0.2.4's session keep-out is gone
        Auto.SEEN.clear()
        setc(Jn.secs[wO[0][0]], wO[0][1], xO.withMetadata("SkyyGear", JClass("org.bson.BsonDocument").parse('{"v": 1, "uses": 7}')))
        setc(Jn.sto, 20, stack("Weapon_Sword_Iron", 1))
        auto_run()
        auto_run()
        wO2 = find_id("Tool_Pickaxe_Iron")
        xO2 = getc(Jn.secs[wO2[0][0]], wO2[0][1]) if len(wO2) == 1 else None
        K.check(len(wO2) == 1 and xO2 is not None and str(Codec.outOf(xO2)) == kJp and getc(Jn.sto, 20) is None,
                "O2 after a relog and a metadata change auto-store still leaves the taken-out pickaxe; the plain iron sword next to it IS auto-stored")
        cO, dO = census(Jn)
        K.check(not once(Jn, dO), "O2 exactly once")
        K.check(int(Inv.countKindU(JArray(JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer"))(Jn.secs), Codec.unstamp(xO2))) == 1
                and Codec.outOf(Codec.unstamp(xO2)) is None and Codec.outOf(Codec.stamp(xO2, "zz")) is None,
                "O3 unstamp / stamp drop the mark: the repair's countKindU counts the marked item as the plain one")
        gap()
        rO4 = run(Jn, 6, 0, "%d:%d" % (wO2[0][0], wO2[0][1]))
        ein4 = [e for e in ent_by_id(Store.get(kJ, Jn.u), "Tool_Pickaxe_Iron") if ein(e)]
        K.check(rO4.startswith("+Into Requip: Tool_Pickaxe_Iron") and len(find_id("Tool_Pickaxe_Iron")) == 0 and len(ein4) >= 1
                and all(Codec.outOf(e.stack) is None for e in ein4), "O4 a hand deposit of the marked pickaxe works; the pool entry carries no mark (%s)" % rO4)
        gap()
        run(Jn, 8, 0, str(ein4[0].eid))
        w5 = find_id("Tool_Pickaxe_Iron")
        K.check(len(w5) == 1 and str(Codec.outOf(getc(Jn.secs[w5[0][0]], w5[0][1]))) == kJp, "O5 taken out again = marked again")
        gap()
        rO5 = run(Jn, 7, 0, None)
        ein5 = [e for e in ent_by_id(Store.get(kJ, Jn.u), "Tool_Pickaxe_Iron") if ein(e)]
        K.check(len(find_id("Tool_Pickaxe_Iron")) == 0 and all(Codec.outOf(e.stack) is None for e in ein5), "O5 Deposit all gear takes it too and clears the mark (%s)" % rO5)
        setc(Jn.sto, 21, Codec.markOut(stack("Tool_Hatchet_Iron", 1), "someone-else"))
        auto_run()
        K.check(getc(Jn.sto, 21) is None, "O6 another profile's mark is ignored: that hatchet is auto-stored")
        cO6, dO6 = census(Jn)
        K.check(not once(Jn, dO6), "O exactly once after every mark step")
        Jn.hot.removeItemStackFromSlot(JShort(3), False)
        E.jf(ASIC, "activeSlot").set(hotc, JByte(0))
        run(Jn, 11, 0, "off")
        PDE = JClass("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent")
        Gate.LAST.put(Jn.u, JLong(1))
        br.put("requip:pocket:" + kJ, JClass("java.util.HashMap")())
        P("WdQuit")().accept(PDE(Jn.pr))
        K.check(not P("WdReady").SESSION.containsKey(Jn.u) and not Gate.LAST.containsKey(Jn.u) and br.get("requip:pocket:" + kJ) is None, "X19 disconnect: session state + requip:pocket forgotten")
        P("WdEng").API = None
        onl = [str(x) for x in P("WdEng").online()]
        K.check(kJ in onl and str(P("WdEng").nameOf(Jn.u)) == "Jo", "X19 the real online() / nameOf (Universe)")
        Jr.PENDING.put("somekey", JLong(1))
        os.makedirs(os.path.join(Wd, "requip", "somekey"), exist_ok=True)
        open(os.path.join(Wd, "requip", "somekey", "journal.json"), "w").write('{"stage": "saved"}')
        Jr.PENDING.put("movekey", JLong(1))
        os.makedirs(os.path.join(Wd, "requip", "movekey"), exist_ok=True)
        open(os.path.join(Wd, "requip", "movekey", "journal.json"), "w").write('{"stage": "moving"}')
        P("WdTimer")().run()
        drain(H)
        K.check(not os.path.isfile(os.path.join(Wd, "requip", "somekey", "journal.json")) and os.path.isfile(os.path.join(Wd, "requip", "movekey", "journal.json")),
                "X19 the timer deletes saved journals past their keep time, never a moving one")
        Jr.PENDING.clear(); Jr.KNOWN.clear(); Jr.GEN.clear(); Jr.PRE.clear()
        Jr.PENDING.put("k2", JLong(int(time.time() * 1000)))
        os.makedirs(os.path.join(Wd, "requip", "k2"), exist_ok=True)
        open(os.path.join(Wd, "requip", "k2", "journal.json"), "w").write("{}")
        K.check(Jr.dropAll() == 1 and not os.path.isfile(os.path.join(Wd, "requip", "k2", "journal.json")), "X19 shutdown: pending journals dropped")
        open(os.path.join(Wd, "requip", "autostore.json"), "w").write("{ broken")
        Auto.load(Auto.FILE)
        r = run(Jn, 11, 0, "on")
        K.check(bool(Auto.BAD) and r.startswith("-Your auto-store switch could not be saved") and open(os.path.join(Wd, "requip", "autostore.json")).read() == "{ broken",
                "X19 an unreadable autostore.json: every switch off, never written over (%s)" % r)

        # ============================================================ X20 the stamp through SkyyGear's own document write (the jar in this JVM)
        if GEAR and os.path.isfile(GEAR):
            try:
                GD = JClass("com.skyy.gear.GearData")
                s0 = Codec.stamp(stack("Weapon_Sword_Iron", 1, gdoc("rare", 12)), "5eed5eed5eed5eed")
                doc = JClass("org.bson.BsonDocument").parse('{"v": 1, "r": "legendary", "lvl": 14, "id": true}')
                o = GD.put(s0, doc, None)
                md = o.getMetadata()
                K.check(str(Codec.stampOf(o)) == "5eed5eed5eed5eed" and str(Codec.rar(o)) == "legendary" and int(Codec.lv(o)) == 14,
                        "X20 SkyyGear %s GearData.put (reforge / level-up / identify write the document this way) keeps the SkyyRequip stamp (keys %s)"
                        % (os.path.basename(GEAR), sorted(str(k_) for k_ in md.keySet())))
            except Exception as ex_:
                K.notes.append("X20 SkyyGear GearData.put could not run in the bare JVM (%s) - the bytecode check (B) covers it" % ex_)
        else:
            K.notes.append("X20 no SkyyGear jar - skipped")

        # ============================================================ X21 the fixer round (critics of R1): one check per fix
        # FIX-S1: a save that fails after SOME files were written (index.json locked) - the files are rewritten from memory, or the
        # journal STAYS so the next action / join repairs them: never an item both on you and IN the pool after a restart
        ICA = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
        F1 = W.player("00000000-0000-0000-0000-000000000f01", "Fae")
        kF1 = str(F1.u)
        setc(F1.sto, 0, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 3)))
        setc(F1.sto, 1, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 4)))
        setc(F1.sto, 2, stack("Weapon_Sword_Iron", 1))
        base, _ = census(F1)
        r = run(F1, 6, 0, "2:0")
        ixp = os.path.join(Wd, "requip", kF1, "index.json")
        FIS = JClass("java.io.FileInputStream")
        lockf = FIS(ixp)
        kept0 = int(Tx.SAVE_KEPT)
        try:
            r2 = run(F1, 6, 0, "2:1")
            jkept = os.path.isfile(os.path.join(Wd, "requip", kF1, "journal.json"))
            r3 = run(F1, 6, 0, "2:2")
        finally:
            lockf.close()
        K.check(r.startswith("+") and r2.startswith("-Could not save Requip - everything was put back; Requip checks its files") and getc(F1.sto, 1) is not None
                and int(Tx.SAVE_KEPT) == kept0 + 1 and jkept and r3.startswith("-Requip still cannot save its files"),
                "FIX-S1 index.json locked: the 2nd deposit is put back, its files cannot be rewritten -> the journal is KEPT; the next action retries the save from memory first (FIX2-D2) (%s / %s / %s)" % (r, r2, r3))
        restart()
        r4 = run(F1, 5)
        c, d = census(F1)
        K.check(c == base and not once(F1, d) and jresolved(kF1) and len([e for e in ent_by_id(d, "Weapon_Sword_Mithril") if ein(e)]) == 1,
                "FIX-S1 ... after a restart the repair reconciles: ONE Mithril sword in the pool, one on you - no copy (%s; %s)" % (r4, c))
        Store.FAIL_NEXT = 1
        r5 = run(F1, 6, 0, "2:1")
        jp_ = os.path.join(Wd, "requip", kF1, "journal.json")
        jd = json.load(open(jp_)) if os.path.isfile(jp_) else None
        restart()
        c, d = census(F1)
        K.check(r5 == "-Could not save Requip - everything was put back (see the server log)." and getc(F1.sto, 1) is not None and c == base and not once(F1, d),
                "FIX-S1 a save that fails but whose files are rewritten from memory: the step is dropped, files match what you carry (%s, journal %s)" % (r5, None if jd is None else jd.get("stage")))
        Jr.PENDING.clear(); Jr.KNOWN.clear(); Jr.GEN.clear(); Jr.PRE.clear()
        os.makedirs(os.path.join(Wd, "requip", kF1), exist_ok=True)
        open(jp_, "w").write('{"format": 3, "stage": "moving", "steps": []}')
        dF = Store.get(kF1, F1.u)
        csF = JArray(ICA)(F1.secs)
        mvl = JClass("java.util.ArrayList")()
        mvl.add(Tx.depMove(dF, csF, 2, 1, JClass("java.util.HashMap")(), JArray(JInt)(2), JClass("java.util.ArrayList")()))
        rg = str(Tx.run(dF, "deposit", mvl, csF, "Deposit"))
        K.check(rg.startswith("-An interrupted Requip change is still being checked") and getc(F1.sto, 1) is not None and json.load(open(jp_))["stage"] == "moving",
                "FIX-S1 a transaction never writes over an unrepaired journal (%s)" % rg)
        os.remove(jp_)

        # FIX-S2: a journal left on a profile you were NOT using is repaired the moment you switch INTO it (not at your first Requip
        # action, after you may have picked up more of the same kind)
        @JImplements(PKG + "WdApi")
        class Api2:
            def __init__(self, u):
                self.u = u

            @JOverride
            def online(self):
                return JArray(UUID_)([self.u])

            @JOverride
            def byName(self, n):
                return self.u

            @JOverride
            def nameOf(self, u):
                return "Sam"

            @JOverride
            def tell(self, u, t, c):
                pass
        Sm = W.player("00000000-0000-0000-0000-000000000f02", "Sam")
        kS = str(Sm.u)
        state.setdefault("key", {})[kS] = kS + "-p1"
        P("WdEng").API = Api2(Sm.u)
        br.put("profile:epoch:" + kS, JLong(5))
        P("WdTimer")().run()
        drain(H)
        setc(Sm.sto, 0, stack("Armor_Iron_Head", 1))
        base1, _ = census(Sm, kS + "-p1")
        Tx.CRASH_AFTER_SAVE = True
        try:
            run(Sm, 6, 0, "2:0")
        except Exception:
            pass
        Tx.CRASH_AFTER_SAVE = False
        jp1 = os.path.join(Wd, "requip", kS + "-p1", "journal.json")
        restart()
        snap1 = W.snap(Sm)
        W.clear(Sm)
        state["key"][kS] = kS + "-p2"
        br.put("profile:epoch:" + kS, JLong(6))
        sw0 = int(P("WdTimer").SWITCH_REPAIRS.get())
        P("WdTimer")().run()
        time.sleep(0.6)
        drain(H)
        sw1 = int(P("WdTimer").SWITCH_REPAIRS.get())
        still = os.path.isfile(jp1)
        W.restore(Sm, snap1)
        state["key"][kS] = kS + "-p1"
        br.put("profile:epoch:" + kS, JLong(7))
        P("WdTimer")().run()
        time.sleep(0.6)
        nt = drain(H)
        sw2 = int(P("WdTimer").SWITCH_REPAIRS.get())
        gone1 = not os.path.isfile(jp1)
        setc(Sm.sto, 1, stack("Armor_Iron_Head", 1))
        c, d = census(Sm, kS + "-p1")
        exp = dict(base1)
        exp[("Armor_Iron_Head", "")] = exp.get(("Armor_Iron_Head", ""), 0) + 1
        K.check(still and sw1 == sw0 and sw2 == sw0 + 1 and nt >= 1 and gone1 and c == exp and len([e for e in ent_by_id(d, "Armor_Iron_Head") if ein(e)]) == 1,
                "FIX-S2 switching to profile 2 leaves profile 1's journal alone; switching BACK repairs it at once (the helmet stays IN), so a helmet picked up afterwards is never counted against it (%s %s %s %s %s %s)" % (still, sw0, sw1, sw2, nt, c))
        P("WdEng").API = None
        del state["key"][kS]
        br.remove("profile:epoch:" + kS)
        Gate.EPOCHAT.clear()
        Gate.BUSYAT.clear()

        # FIX-S4: zero / unreadable material counts are no evidence (a crash then KEEPS the crafted item)
        Mt = W.player("00000000-0000-0000-0000-000000000f04", "Mat")
        setc(Mt.sto, 0, stack("Ingredient_Bar_Iron", 2))
        csM = JArray(ICA)(Mt.secs)
        K.check(not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":0}}', csM, str(Mt.u))) and not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":"3"}}', csM, str(Mt.u)))
                and bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":2}}', csM, str(Mt.u))) and not bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":3}}', csM, str(Mt.u)))
                and bool(Tx.matsBack('{"inv":{"Ingredient_Bar_Iron":2, "Wood_Oak_Log":0}}', csM, str(Mt.u))),
                "FIX-S4 matsBack: a 0 or string count never proves the materials are back; real counts still do")
        craftS = stack("Weapon_Sword_Iron", 1, gdoc("rare", 7))
        Tx.CRASH_AT = 0
        diedM = False
        try:
            fa(3, Mt.u, craftS, "test", '{"inv":{"Ingredient_Bar_Iron":0}}')
        except Exception as ex_:
            diedM = "harness crash" in str(ex_)
        Tx.CRASH_AT = -1
        restart()
        rr = run(Mt, 5)
        dM = Store.get(str(Mt.u), Mt.u)
        K.check(diedM and len([e for e in ent_by_id(dM, "Weapon_Sword_Iron") if ein(e)]) == 1 and "undone" not in rr,
                "FIX-S4 a crashed craft deposit whose evidence is all zero keeps the crafted sword (%s)" % rr)

        # FIX-S5: a pocket slot never gets more than the block's max stack (pocket.target 500, Rock_Stone stacks to 100)
        Pk = W.player("00000000-0000-0000-0000-000000000f05", "Pok")
        setc(Pk.hot, 0, stack("Rock_Stone", 2))
        rp = run(Pk, 10, 0, "4|pocket")
        Pk.hot.removeItemStackFromSlot(JShort(0), False)
        state.setdefault("bags", {})[str(Pk.u)] = {"Rock_Stone": 1000}
        Cfg.POCKET_N = 500
        gap()
        r = run(Pk, 1, 0)
        Cfg.POCKET_N = 0
        K.check(rp.startswith("+") and getc(Pk.hot, 0) is not None and int(getc(Pk.hot, 0).getQuantity()) == 100 and state["bags"][str(Pk.u)]["Rock_Stone"] == 900,
                "FIX-S5 pocket.target 500: the slot gets 100 (the max stack), 900 stay in the bags (%s)" % r)

        # ============================================================ X22 fixer 2 (the second critics): one check per fix
        # FIX2-D1 (data critic 1): a craft deposit whose save fails twice is refused - the caller keeps the item. Its journal step is marked
        # aborted, so the repair after a restart never rebuilds it as IN (even when a failed save had already written it into a shard)
        Cr = W.player("00000000-0000-0000-0000-000000000f06", "Cra")
        kC = str(Cr.u)
        setc(Cr.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 5)))
        r0 = run(Cr, 6, 0, "2:0")
        craftB = stack("Weapon_Bow_Wood", 1, gdoc("rare", 77))
        Store.FAIL_NEXT = 2
        rc = str(fa(3, Cr.u, craftB, "test", ""))
        Store.FAIL_NEXT = 0
        jC = os.path.join(Wd, "requip", kC, "journal.json")
        jdC = json.load(open(jC)) if os.path.isfile(jC) else {}
        abC = [m for st_ in jdC.get("steps", []) for m in st_.get("moves", []) if jn(m.get("t")) == 5]
        K.check(r0.startswith("+") and rc.startswith("refused:Could not save Requip - everything was put back; Requip checks") and len(abC) == 1 and abC[0].get("ab") is True
                and bool(Tx.KEPT.containsKey(kC)), "FIX2-D1 a craft deposit whose save fails twice: refused, its journal move is marked aborted, the memory is kept (%s / %s)" % (rc, abC))
        setc(Cr.sto, 5, craftB)      # the caller (SkyyGear) falls back to the inventory
        eidC = str(abC[0]["eid"]) if abC else "0000000000000000"
        shp = Paths.get(os.path.join(Wd, "requip", kC, "items-000.json"))
        shd = Store.readDoc(shp)
        En = P("WdEntry")(eidC)
        En.space = 1
        En.spot = -1
        setattr(En, "in_", True)
        En.stack = Codec.stamp(craftB, eidC)
        En.setShow(craftB)
        shd.getArray("entries").add(En.toDoc())
        Store.atomicWrite(shp, JString(str(Codec.toJson(shd))).getBytes("UTF-8"))
        restart()
        K.check(len([e for e in ent_by_id(Store.load(kC, kC), "Weapon_Bow_Wood") if ein(e)]) == 1, "FIX2-D1 ... (set-up: a phantom IN bow in the shard, as a half-written save leaves it)")
        rrC = run(Cr, 5)
        c, d = census(Cr)
        bowk = ("Weapon_Bow_Wood", str(JClass("org.bson.BsonDocument").parse(gdoc("rare", 77)).toJson()))
        jdC2 = json.load(open(jC)) if os.path.isfile(jC) else {}
        K.check(c.get(bowk) == 1 and not once(Cr, d) and not [e for e in ent_by_id(d, "Weapon_Bow_Wood") if ein(e)] and jresolved(kC),
                "FIX2-D1 ... after a restart the repair drops the aborted craft: ONE bow (the caller's), none IN the pool (%s; %s)" % (rrC, c.get(bowk)))

        # FIX2-D2 (data critic 2): the change put back after a double save failure is fixed FROM MEMORY on the next action, and the older
        # saved step stays in the journal - a crash that later rolls the inventory back past it still finds its evidence
        R2 = W.player("00000000-0000-0000-0000-000000000f07", "Ret")
        kR = str(R2.u)
        setc(R2.sto, 0, stack("Weapon_Sword_Mithril", 1, gdoc("rare", 8)))
        setc(R2.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 9)))
        r00 = run(R2, 6, 0, "2:1")      # the files exist; the engine saves the player after it
        restart()
        Jr.delete(kR)
        engR = W.snap(R2)
        baseR, _ = census(R2)
        rA = run(R2, 6, 0, "2:0")
        kr0 = int(Tx.KEPT_RETRIES)
        Store.FAIL_NEXT = 2
        setc(R2.sto, 2, stack("Armor_Iron_Head", 1))
        rB = run(R2, 6, 0, "2:2")
        Store.FAIL_NEXT = 0
        keptB = bool(Tx.KEPT.containsKey(kR))
        rC = run(R2, 5)
        jR = os.path.join(Wd, "requip", kR, "journal.json")
        jdR = json.load(open(jR)) if os.path.isfile(jR) else {}
        K.check(r00.startswith("+") and rA.startswith("+") and rB.startswith("-Could not save Requip - everything was put back; Requip checks") and keptB and not Tx.KEPT.containsKey(kR)
                and int(Tx.KEPT_RETRIES) == kr0 + 1 and jdR.get("stage") == "saved" and len(jdR.get("steps", [])) == 1 and bool(Jr.PENDING.containsKey(kR)) and getc(R2.sto, 2) is not None,
                "FIX2-D2 the next action rewrites the files from memory; the journal keeps the older SAVED step (pending) (%s / %s / %s / %s)" % (rA, rB, rC, jdR.get("stage")))
        R2.sto.removeItemStackFromSlot(JShort(2), False)
        W.restore(R2, engR)
        restart()
        rD = run(R2, 5)
        c, d = census(R2)
        K.check(c == baseR and not once(R2, d) and len([e for e in ent_by_id(d, "Weapon_Sword_Mithril") if ein(e)]) == 0,
                "FIX2-D2 ... a crash that rolls the inventory back past that step: its evidence is still there - the Mithril sword is on you, NOT also in the pool (%s)" % rD)
        Jr.delete(kR)

        # FIX2-D3 (data critic 3): an unreadable journal no longer blocks for good: every change says why; /requipadmin repair moves it aside
        Ux = W.player("00000000-0000-0000-0000-000000000f08", "Unr")
        kU = str(Ux.u)
        setc(Ux.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 10)))
        setc(Ux.sto, 1, stack("Weapon_Sword_Iron", 1, gdoc("rare", 11)))
        run(Ux, 6, 0, "2:0")
        Jr.delete(kU)
        jU = os.path.join(Wd, "requip", kU, "journal.json")
        open(jU, "w").write("{ broken")
        restart()
        rU = run(Ux, 6, 0, "2:1")
        heldU = getc(Ux.sto, 1) is not None
        P("WdRepairTask")(Ux.u, 0, True, None).run()
        aside = [f for f in os.listdir(os.path.join(Wd, "requip", kU)) if f.startswith("journal-unreadable-")]
        goneU = not os.path.isfile(jU)
        rU2 = run(Ux, 6, 0, "2:1")
        K.check(rU.startswith("-The Requip journal of this profile cannot be read") and heldU and len(aside) == 1 and goneU and rU2.startswith("+"),
                "FIX2-D3 an unreadable journal: the change says why, /requipadmin repair moves the file aside, then Requip works again (%s / %s / %s)" % (rU, aside, rU2))

        # FIX2-E1 (engine critic 1): idle profiles leave the memory cache (never one with a journal / pending / kept / unsaved marks)
        Jr.delete(kU)
        Store.get(kF1, F1.u)
        Store.get(kC, Cr.u)
        Jr.PENDING.put(kC, JLong(int(time.time() * 1000)))
        hs = JClass("java.util.HashSet")()
        hs.add(kU)
        Store.get(kU, Ux.u)
        ev0 = int(P("WdTimer").EVICTED)
        nE = int(P("WdTimer").evict(hs))
        K.check(nE >= 1 and not Store.CACHE.containsKey(kF1) and Store.CACHE.containsKey(kC) and Store.CACHE.containsKey(kU) and int(P("WdTimer").EVICTED) == ev0 + nE,
                "FIX2-E1 the timer drops idle profiles from memory; the online one and one with a pending journal stay (%d evicted)" % nE)
        Jr.PENDING.remove(kC)
        cE, dE = census(F1)
        K.check(not Store.get(kF1, F1.u).bad and not once(F1, dE), "FIX2-E1 ... an evicted profile reloads from its files on demand")

        # FIX2-E2 (engine critic 2): wardrobe:fn:canDeposit never answers "accepted" (null) on a failure or a malformed call
        rq0 = Store.RQ
        Store.RQ = None
        try:
            ce = Fn(1).apply(JArray(JObject)([UUID_.fromString("00000000-0000-0000-0000-000000000f09"), JString("Weapon_Sword_Iron"), JInt(1)]))
        finally:
            Store.RQ = rq0
        cm = Fn(1).apply(JArray(JObject)([UUID_.fromString("00000000-0000-0000-0000-000000000f09")]))
        cm2 = Fn(1).apply(JString("x"))
        cok = fa(1, Q.u, "Weapon_Sword_Iron", JInt(1))
        K.check(str(ce) == "Requip error - try again" and str(cm) == "not storable" and str(cm2) == "not storable" and cok is None,
                "FIX2-E2 canDeposit: a failure says 'Requip error', a malformed call 'not storable', a real accept stays null (%s / %s / %s / %s)" % (ce, cm, cm2, cok))
        Store.CACHE.remove("00000000-0000-0000-0000-000000000f09")

        # FIX2-E3 (engine critic 3): the start only lists folders; the full pool-file read runs once in the background
        sh = list(Store.scanAll(False))
        P("WdScan")().run()
        dp = list(P("WdScan").LAST)
        K.check(sh[3] == -1 and dp[3] > 0 and dp[0] == sh[0] and dp[2] == sh[2], "FIX2-E3 scanAll(false) parses no pool file; WdScan reads them all (%s / %s)" % (sh, dp))

        # FIX2-F2 (fidelity critic 2): the pick op takes a bag block by id (no block held)
        pr1 = run(Pk, 10, 0, "5|pocket:Rock_Stone")
        pr2 = run(Pk, 10, 0, "5|pocket:Weapon_Sword_Iron")
        pr3 = run(Pk, 10, 0, "0|pocket:Rock_Stone")
        K.check(pr1.startswith("+Loadout 1: Hotbar 2 fills with Rock_Stone") and pr2.startswith("-That is not a block") and pr3.startswith("-Pocket blocks are for hotbar slots only"),
                "FIX2-F2 pick 'pocket:<id>': a block by id, never a sword, never an armor slot (%s / %s / %s)" % (pr1, pr2, pr3))

        # ============================================================ Y 0.2.1 (audit 9d): the join pre-warm, per-key journal locks, hasFile from memory
        RT = P("WdRepairTask")
        IDH = JClass("java.lang.System").identityHashCode
        Jn = W.player("00000000-0000-0000-0000-0000000000f1", "Yan")
        kJ = str(Jn.u)
        setc(Jn.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 1)))
        gap()
        r0_ = run(Jn, 6, 0, "2:0")
        K.check(r0_.startswith("+"), "Y0 a normal deposit works for the Y player (%s)" % r0_)
        # Y1 the join repair of a CRASHED equip: the pre-warm (WdHop.run, here on the test thread = the scheduler's role) loads the
        # profile + reads the journal; the world task repairs from them - no disk question, the same cached profile object
        setc(Jn.sto, 3, stack("Weapon_Sword_Iron", 1, gdoc("rare", 2)))
        base1, _ = census(Jn)
        gap()
        Tx.CRASH_AT = 0
        try:
            run(Jn, 6, 0, "2:3")
        except Exception:
            pass
        Tx.CRASH_AT = -1
        jcrash = os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json"))
        restart()
        pw0, pu0 = int(RT.PREWARMS), int(Jr.PREUSED)
        P("WdHop")(Jn.u, RT(Jn.u, 0, False, None)).run()
        d_pre = Store.CACHE.get(kJ)
        dc0, rd0 = int(Jr.DISKCHECKS), int(Jr.READS)
        pre_ok = d_pre is not None and Jr.PRE.containsKey(kJ) and bool(Jr.KNOWN.get(kJ)) and int(RT.PREWARMS) == pw0 + 1
        K.notes.append("Y1 r0=%s; diag: cached=%s pre=%s known=%s prewarms %d->%d busy=%s rq=%s" % (r0_, d_pre is not None, bool(Jr.PRE.containsKey(kJ)),
                       Jr.KNOWN.get(kJ), pw0, int(RT.PREWARMS), bool(P("WdGate").busy(Jn.u)), Store.RQ))
        n_ = drain(H)
        cY, dY = census(Jn)
        K.notes.append("Y1 diag2: n=%d disk %d->%d reads %d->%d preused %d->%d same=%s journal=%s base=%s once=%s" % (n_, dc0, int(Jr.DISKCHECKS), rd0,
                       int(Jr.READS), pu0, int(Jr.PREUSED), IDH(Store.CACHE.get(kJ)) == IDH(d_pre), os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")),
                       cY == base1, once(Jn, dY)))
        K.check(jcrash and pre_ok and n_ == 1 and int(Jr.DISKCHECKS) == dc0 and int(Jr.READS) == rd0 and int(Jr.PREUSED) == pu0 + 1
                and not os.path.isfile(os.path.join(Wd, "requip", kJ, "journal.json")) and cY == base1 and not once(Jn, dY),
                "Y1 crashed equip + join: the pre-warm loaded the profile and read the journal off the world thread; the world task asked the "
                "disk nothing (DISKCHECKS +%d), used the pre-read journal, repaired: every item exactly once"
                % (int(Jr.DISKCHECKS) - dc0))
        # Y2 a clean join (no journal): the pre-warm learns "no journal" (one disk question, scheduler side); the world task asks nothing
        restart()
        dq0, rq0 = int(Jr.DISKCHECKS), int(Jr.READS)
        P("WdHop")(Jn.u, RT(Jn.u, 0, False, None)).run()
        dq1, rq1 = int(Jr.DISKCHECKS), int(Jr.READS)
        d_pre2 = Store.CACHE.get(kJ)
        drain(H)
        K.check((dq1 - dq0) + (rq1 - rq0) >= 1 and int(Jr.DISKCHECKS) == dq1 and int(Jr.READS) == rq1 and d_pre2 is not None
                and IDH(Store.CACHE.get(kJ)) == IDH(d_pre2) and Jr.KNOWN.get(kJ) is not None and not bool(Jr.KNOWN.get(kJ)) and not Jr.PRE.containsKey(kJ),
                "Y2 clean join: the pre-warm asked the disk (%d), the world task nothing (%d) and kept the pre-loaded profile"
                % ((dq1 - dq0) + (rq1 - rq0), int(Jr.DISKCHECKS) - dq1 + int(Jr.READS) - rq1))
        # Y3 a busy profile is not pre-warmed (the task waits and comes back); a journal written after the pre-read is never used stale
        restart()
        br.put("profile:busy:" + kJ, True)
        pw1 = int(RT.PREWARMS)
        P("WdHop")(Jn.u, RT(Jn.u, 0, False, None)).run()
        K.check(int(RT.PREWARMS) == pw1 and Store.CACHE.get(kJ) is None, "Y3 profile:busy -> no pre-warm (nothing loaded)")
        br.remove("profile:busy:" + kJ)
        H["Q"].clear()
        doc_ = JClass("org.bson.BsonDocument").parse('{"format": 3, "stage": "saved", "steps": []}')
        Jr.write(kJ, doc_)
        Jr.preRead(kJ)
        Jr.write(kJ, JClass("org.bson.BsonDocument").parse('{"format": 3, "stage": "failed", "steps": []}'))
        K.check(Jr.takePre(kJ) is None, "Y3 a journal written after the pre-read: takePre answers nothing (the repair reads the file again)")
        Jr.preRead(kJ)
        tp = Jr.takePre(kJ)
        K.check(tp is not None and str(tp[1].getString("stage").getValue()) == "failed" and Jr.takePre(kJ) is None,
                "Y3 a current pre-read is taken once")
        Jr.delete(kJ)
        # Y4 hasFile: exact for our own writes / deletes / reads, one disk question when unknown
        kh = "00000000-0000-0000-0000-0000000000f4"
        restart()
        Jr.KNOWN.clear()
        h0 = int(Jr.DISKCHECKS)
        a1 = bool(Jr.hasFile(kh))
        a2 = bool(Jr.hasFile(kh))
        h1 = int(Jr.DISKCHECKS)
        os.makedirs(os.path.join(Wd, "requip", kh), exist_ok=True)
        Jr.write(kh, doc_)
        a3 = bool(Jr.hasFile(kh))
        Jr.delete(kh)
        a4 = bool(Jr.hasFile(kh))
        open(os.path.join(Wd, "requip", kh, "journal.json"), "w").write('{"stage": "moving"}')   # a crash leftover at "start"
        Jr.KNOWN.clear()
        a5 = bool(Jr.hasFile(kh))
        K.check(not a1 and not a2 and h1 == h0 + 1 and a3 and not a4 and a5 and int(Jr.DISKCHECKS) == h1 + 1,
                "Y4 hasFile: unknown -> one disk question, then memory; write -> true, delete -> false (no disk); after a restart a leftover file "
                "is found again (%s)" % [a1, a2, a3, a4, a5])
        # ... and the change pre-check refuses over it exactly like 0.2 (fixer 1), from memory
        Ky = W.player(kh, "Kay")
        setc(Ky.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 1)))
        dK = Store.get(kh, Ky.u)
        mv_ = JClass("java.util.ArrayList")()
        mv_.add(JClass("java.lang.Object")())   # (only the size is read before the pre-check)
        rK = str(Tx.run(dK, "test", mv_, None, "Test"))
        K.check("interrupted Requip change is still being checked" in rK, "Y4 WdTx.run refuses over an unrepaired journal file found by hasFile: %s" % rK)
        os.remove(os.path.join(Wd, "requip", kh, "journal.json"))
        Jr.forget(kh)
        # Y5 ONE LOCK PER KEY: a writer holding profile A's journal lock never blocks profile B; profile A waits (0.2: everyone waited)
        cpj = JClass("javassist.ClassPool")(True)
        hc = cpj.makeClass("skyywdtest.Hold")
        hc.addInterface(cpj.get("java.lang.Runnable"))
        for f_ in ("public Object lk;", "public long ms;", "public volatile boolean in;", "public volatile boolean done;"):
            hc.addField(JClass("javassist.CtField").make(f_, hc))
        hc.addConstructor(JClass("javassist.CtNewConstructor").make("public Hold(Object lk, long ms) { this.lk = lk; this.ms = ms; }", hc))
        hc.addMethod(JClass("javassist.CtNewMethod").make("public void hold() { this.in = true; try { Thread.sleep(this.ms); } catch (Throwable t) { } this.in = false; this.done = true; }", hc))
        hc.addMethod(JClass("javassist.CtNewMethod").make("public void run() { synchronized (this.lk) { hold(); } }", hc))
        cdir = os.path.join(SCRATCH, "y-cls")
        hc.writeFile(cdir)
        URL_, URLCL_, File_ = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
        ua = JArray(URL_)(1)
        ua[0] = File_(cdir).toURI().toURL()
        HoldC = URLCL_(ua, JClass("java.lang.ClassLoader").getSystemClassLoader()).loadClass("skyywdtest.Hold")
        kA, kB = "00000000-0000-0000-0000-0000000000a5", "00000000-0000-0000-0000-0000000000b5"
        for k_ in (kA, kB):
            os.makedirs(os.path.join(Wd, "requip", k_), exist_ok=True)

        def held(lk, fn_):
            hold = HoldC.getDeclaredConstructor(JClass("java.lang.Object").class_, JClass("java.lang.Long").TYPE).newInstance(lk, JLong(700))
            th = JClass("java.lang.Thread")(hold)
            th.start()
            while not bool(HoldC.getField("in").get(hold)):
                time.sleep(0.005)
            t0 = time.perf_counter()
            fn_()
            ms = (time.perf_counter() - t0) * 1000.0
            th.join()
            return ms
        ms_other = held(Jr.lockOf(kA), lambda: (Jr.write(kB, doc_), Jr.read(kB), Jr.delete(kB)))
        ms_same = held(Jr.lockOf(kA), lambda: Jr.write(kA, doc_))
        Jr.delete(kA)
        # control: the 0.2 jar's WdJournal (its own class loader) - the class monitor blocks every key
        ua2 = JArray(URL_)(1)
        ua2[0] = File_(PREV).toURI().toURL()
        ua2 = JArray(URL_)(2)
        ua2[0] = File_(PREV).toURI().toURL()
        ua2[1] = File_(B.SERVER_JAR).toURI().toURL()
        L02 = URLCL_(ua2, JClass("java.lang.ClassLoader").getPlatformClassLoader())   # not the system loader (it holds the 0.2.1 jar)
        S02 = JClass(PKG + "WdStore", loader=L02)
        P02 = JClass("java.nio.file.Paths")
        S02.ROOT = P02.get(str(Store.ROOT.toString()))
        S02.RQ = P02.get(str(Store.RQ.toString()))
        J02 = JClass(PKG + "WdJournal", loader=L02)
        doc02 = JClass("org.bson.BsonDocument", loader=L02).parse('{"format": 3, "stage": "saved", "steps": []}')
        ms_old = held(J02.class_, lambda: J02.write(kB, doc02))
        J02.delete(kB)
        syn_new = [str(m.getName()) for m in Jr.class_.getDeclaredMethods() if JClass("java.lang.reflect.Modifier").isSynchronized(m.getModifiers())]
        syn_old = [str(m.getName()) for m in J02.class_.getDeclaredMethods() if JClass("java.lang.reflect.Modifier").isSynchronized(m.getModifiers())]
        K.check(ms_other < 150.0 and ms_same >= 400.0 and ms_old >= 400.0 and not syn_new and len(syn_old) >= 9,
                "Y5 per-key journal locks: while profile A's lock is held, profile B wrote + read + deleted its journal in %.0f ms; profile A waited "
                "%.0f ms; 0.2 (one class lock, %d synchronized methods) made profile B wait %.0f ms; 0.2.1 has no synchronized journal method %s"
                % (ms_other, ms_same, len(syn_old), ms_old, syn_new))
        # Y6 (fixer) a stale cached "has a journal" re-checks the disk before it refuses; a real one is still refused
        kS = "00000000-0000-0000-0000-0000000000f6"
        restart()
        Ks = W.player(kS, "Sol")
        setc(Ks.sto, 0, stack("Weapon_Sword_Iron", 1, gdoc("rare", 1)))
        os.makedirs(os.path.join(Wd, "requip", kS), exist_ok=True)
        dS = Store.get(kS, Ks.u)   # the profile is loaded (cached) BEFORE the journal appears - a later load would re-read the folder
        Jr.write(kS, doc_)
        stale_known = bool(Jr.hasFile(kS))
        os.remove(os.path.join(Wd, "requip", kS, "journal.json"))   # an admin removes the journal by hand while the server runs
        rc0 = int(Jr.RECHECKS)
        stale_still = bool(Jr.hasFile(kS))   # the cache still says "yes" (nothing on our side touched the journal)
        mv3 = JClass("java.util.ArrayList")()
        mv3.add(JClass("java.lang.Object")())   # passes the pre-check, then fails on the stand-in move (nothing real moves)
        try:
            rS = str(Tx.run(dS, "test", mv3, None, "Test"))
        except Exception as e_:
            rS = "threw after the pre-check: %s" % str(e_)[:60]
        rc1 = int(Jr.RECHECKS)
        jf_ = os.path.join(Wd, "requip", kS, "journal.json")
        if os.path.isfile(jf_):
            os.remove(jf_)
        Jr.PENDING.remove(kS)
        Jr.forget(kS)
        K.check(stale_known and stale_still and "still being checked" not in rS and rc1 == rc0 + 1,
                "Y6 a journal deleted by hand while cached: WdTx.run asks the disk once more (%d) and does not refuse (%s) [%s %s]" % (rc1 - rc0, rS, stale_known, stale_still))
        Ky2 = W.player(kh, "Kay")
        open(os.path.join(Wd, "requip", kh, "journal.json"), "w").write('{"stage": "moving"}')
        Jr.forget(kh)
        dK2 = Store.get(kh, Ky2.u)
        mv2 = JClass("java.util.ArrayList")()
        mv2.add(JClass("java.lang.Object")())
        rK2 = str(Tx.run(dK2, "test", mv2, None, "Test"))
        K.check("interrupted Requip change is still being checked" in rK2 and int(Jr.RECHECKS) == rc1 + 1,
                "Y6 a real unrepaired journal is still refused after the re-check: %s" % rK2)
        os.remove(os.path.join(Wd, "requip", kh, "journal.json"))
        Jr.forget(kh)
        # Y6 (fixer) the join repair's hop + pre-warm on the private reader thread
        Hop = P("WdHop")
        Hop.READER = JClass("java.util.concurrent.ScheduledThreadPoolExecutor")(1, P("WdThreads")())   # (setup: Executors.newSingleThreadScheduledExecutor)
        try:
            @JImplements("java.util.concurrent.Callable")
            class TNw(object):
                @JOverride
                def call(self):
                    th = JClass("java.lang.Thread").currentThread()
                    return str(th.getName()) + "|" + str(th.isDaemon())
            nmw = str(Hop.READER.submit(TNw()).get())
            restart()
            pw2 = int(RT.PREWARMS)
            Hop.later(Jn.u, RT(Jn.u, 0, False, None), 300)
            q_rep = int(Hop.READER.getQueue().size())
            Hop.later(Jn.u, JClass("java.lang.Thread")(), 300)   # any other task (a no-op Runnable): the shared scheduler, not the reader
            q_oth = int(Hop.READER.getQueue().size())
            time.sleep(0.8)
            Hop.READER.submit(TNw()).get()
            pw3 = int(RT.PREWARMS)
            K.check(nmw == "SkyyWardrobe-reader|True" and q_rep == 1 and q_oth == 1 and pw3 == pw2 + 1 and Store.CACHE.get(str(Store.pkey(Jn.u))) is not None,
                    "Y6 WdHop.later: the join repair is queued on the daemon SkyyWardrobe-reader (%s; queue %d, another task %d) and its pre-warm ran "
                    "there (PREWARMS +%d, the profile cached)" % (nmw, q_rep, q_oth, pw3 - pw2))
        finally:
            ex_w = Hop.READER
            Hop.READER = None
            ex_w.shutdownNow()
        K.notes.append("Y: pre-warm + pre-read journal used on the world thread with 0 disk questions; per-key locks (other key %.0f ms vs 0.2 %.0f ms)"
                       % (ms_other, ms_old))




    except Exception as ex:
        import traceback
        traceback.print_exc()
        K.check(False, "X crashed: %s" % ex)
    K.save()


# ====================================================================================================== D: start twice on a live copy
def run_live(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    home = os.path.join(SCRATCH, "live")
    P = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    # setup()'s order: (0.2.2) the free loadouts update, config load, the store paths, auto-store file, the start scan, the kit, the bridge fns
    cf_ = os.path.join(home, "Skyy_SkyyWardrobe", "config.properties")
    exp_free = 10
    if os.path.isfile(cf_):
        txt_ = open(cf_, encoding="latin-1").read()
        vals = [l_.split("=", 1)[1].strip() for l_ in txt_.splitlines() if l_.strip().startswith("slots.free") and "=" in l_]
        if "requip-0.2.2-free10" in txt_ or (vals and vals[-1] != "4"):
            exp_free = int(vals[-1]) if vals else 10
    P("CfgRows").LOG = HL.get("SkyyWardrobeLive")
    P("CfgRows").HOME = Paths.get(home).resolve("Skyy_SkyyWardrobe")
    P("CfgHist").init()
    P("CfgLog").init()
    mig = str(P("WdCfg").migFree(Paths.get(cf_)))
    K.notes.append("D %s migFree: %s" % (step, mig or "nothing to do"))
    P("WdCfg").load(Paths.get(home))
    root = Paths.get(home).resolve("Skyy_SkyyWardrobe")
    P("WdStore").ROOT = root
    P("WdStore").DIR01 = root.resolve("loadouts")
    P("WdStore").RQ = root.resolve("requip")
    P("WdStore").LOGF = root.resolve("requip.log")
    P("WdAuto").load(P("WdStore").RQ.resolve("autostore.json"))
    sc = list(P("WdStore").scanAll(True))
    P("CfgPub").start(Paths.get(home), HL.get("SkyyWardrobeLive"))
    P("WdLog").bridge().put("wardrobe:fn:open", P("WdFn")(0))
    n01 = len([f for f in os.listdir(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts")) if f.endswith(".json") and not f.endswith(".journal.json")]) if os.path.isdir(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts")) else 0
    if step in ("1", "2"):
        K.check(sc[1] == 0 and sc[4] <= n01 and int(P("WdCfg").FREE) == exp_free and (step == "1" or mig == ""),
                "D %s: no unreadable Requip profile, at most the %d 0.1 wardrobes waiting, %d free loadouts, the update only on start 1 (%s, %s)" % (step, n01, exp_free, sc, mig))
    else:
        # step 3: the live 0.1 file(s) migrate on this COPY (no journal: file -> file, no inventory needed)
        done = []
        ld_ = os.path.join(home, "Skyy_SkyyWardrobe", "loadouts")
        for f in sorted(os.listdir(ld_) if os.path.isdir(ld_) else []):   # 0.2.2: a fresh world has no 0.1 loadouts folder
            if not f.endswith(".json") or f.endswith(".journal.json"):
                continue
            k = f[:-5]
            before = open(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts", f), "rb").read()
            d = P("WdStore").get(k, None)
            r = P("WdMig").run(d, None, False)
            d2 = P("WdStore").load(k, "")
            hist = os.path.join(home, "Skyy_SkyyWardrobe", "requip", k, "from01", f)
            K.check(d.mig == 0 and not d.bad and d2.migrated is not None and os.path.isfile(hist) and open(hist, "rb").read() == before
                    and open(os.path.join(home, "Skyy_SkyyWardrobe", "loadouts", f), "rb").read() == before,
                    "D3 the live 0.1 file %s migrated on the COPY: run-once marker, History snapshot = its bytes, the 0.1 file untouched (%s; %s)" % (f, r, d2.migrated))
            done.append((k, int(d2.ask01), d2.count(0) + d2.count(1)))
        K.notes.append("D3 migrated live copies: %s" % done)
    P("CfgPub").shutdown()
    P("WdJournal").dropAll()
    K.save()


# ====================================================================================================== P / B / AA / C
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("WdAdminCmd", "WdAdminArg1Cmd", "WdAdminArg2Cmd", "WdAdminArg3Cmd"):
        c = JClass(PKG + cn)()
        perm, groups = c.getPermission(), fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty" % cn)
        if cn == "WdAdminCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak and str(c.getName()) == "requipadmin" and sorted(str(a) for a in c.getAliases()) == ["wardrobeadmin"],
                    "P. /requipadmin (alias /wardrobeadmin) gives %s to no group (leak %s)" % (NODE, leak))
    for cn in ("WdCmd", "WdArg1Cmd", "WdArg2Cmd", "WdArg3Cmd"):
        c = JClass(PKG + cn)()
        K.check(list(fld.get(c)) == ["hytale:Adventurer"] and (c.getPermission() is None or NODE not in str(c.getPermission())), "P. %s = hytale:Adventurer" % cn)
    m = JClass(PKG + "WdCmd")()
    K.check(str(m.getName()) == "requip" and sorted(str(a) for a in m.getAliases()) == ["loadout", "loadouts", "rq", "wardrobe", "wardrobes", "wd"],
            "P. /requip aliases rq, wardrobe, wd, loadout, loadouts, wardrobes (%s)" % sorted(str(a) for a in m.getAliases()))
    K.save()


def bytecode_calls(CPl, IP, cls, meth):
    cc = CPl.get(cls)
    out = []
    for m in cc.getDeclaredMethods():
        if str(m.getName()) != meth:
            continue
        ca = m.getMethodInfo().getCodeAttribute()
        if ca is None:
            continue
        it, cp = ca.iterator(), m.getMethodInfo().getConstPool()
        while it.hasNext():
            out.append(str(IP.instructionString(it, it.next(), cp)))
    return out


def run_bytecode(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR], verify=False)
    CPl = JClass("javassist.ClassPool")(False)
    CPl.appendSystemPath()
    CPl.appendClassPath(B.SERVER_JAR)
    CPl.appendClassPath(JAR)
    IP = JClass("javassist.bytecode.InstructionPrinter")
    s = bytecode_calls(CPl, IP, PKG + "SkyyWardrobePlugin", "setup")
    names = [re.search(r"\.(\w+)\(\(", l).group(1) for l in s if ("invoke" in l and re.search(r"\.(\w+)\(\(", l))]
    want = ["migFree", "load", "load", "scanAll", "start"] + ["put"] * 9 + ["registerCommand", "registerCommand", "registerGlobal", "registerGlobal", "schedule", "scheduleWithFixedDelay", "register"]   # 0.2.6: + the hub tab
    seq = [n for n in names if n in set(want)]
    K.check(seq == want, "B setup() order: the 0.2.2 free loadouts update, config, autostore, the folder scan, kit, 8 bridge fns + stampKey, 2 commands, 2 events, the background file check (FIX2-E3), the timer (%s)" % seq)
    K.check(not any("registerSystem" in l for l in s), "B no ECS system")
    allcode = []
    for n in zipfile.ZipFile(JAR).namelist():
        if not n.endswith(".class"):
            continue
        cc = CPl.get(n[:-6].replace("/", "."))
        for m in cc.getDeclaredMethods():
            allcode += bytecode_calls(CPl, IP, n[:-6].replace("/", "."), str(m.getName()))
    sets = [l for l in allcode if "setItemStackForSlot" in l]
    rems = [l for l in allcode if "removeItemStackFromSlot" in l]
    K.check(sets and all("(SLcom/hypixel/hytale/server/core/inventory/ItemStack;Z)" in l for l in sets), "B every setItemStackForSlot is (short, ItemStack, boolean)")
    K.check(rems and all("(SZ)" in l for l in rems), "B every removeItemStackFromSlot is (short, boolean)")
    K.check(not any("ItemGridSlot" in l for l in allcode), "B no ItemGridSlot anywhere (icons only, metadata-free)")
    run_ = bytecode_calls(CPl, IP, PKG + "WdTx", "run")
    jb = next(i for i, l in enumerate(run_) if "WdJournal.begin" in l)
    dm = next(i for i, l in enumerate(run_) if "WdTx.doMove" in l)
    sv = next(i for i, l in enumerate(run_) if "WdStore.save" in l)
    K.check(jb < dm < sv, "B the journal is written before the first move, the files after the moves")
    # FIX-S1: after a failed save + rollback the files are rewritten (a 2nd save) BEFORE the journal step may be dropped (abort)
    sv2 = [i for i, l in enumerate(run_) if "WdStore.save" in l]
    ab = [i for i, l in enumerate(run_) if "WdJournal.abort" in l]
    K.check(len(sv2) >= 2 and ab and sv2[1] < ab[-1], "FIX-S1 bytecode: WdTx.run saves again from the restored memory before the journal's abort")
    # FIX-E1: the pocket give-back (sacks:fn:deposit with the hotbar slot) runs BEFORE the Equip transaction
    ops_ = bytecode_calls(CPl, IP, PKG + "WdOps", "run")
    gb = [i for i, l in enumerate(ops_) if "WdOps.giveBack" in l]
    tr = [i for i, l in enumerate(ops_) if "WdTx.run" in l]
    K.check(gb and tr and gb[0] < tr[0], "FIX-E1 bytecode: giveBack before the Equip transaction")

    def catches(cls, meth):
        out_ = []
        for m in CPl.get(cls).getDeclaredMethods():
            if str(m.getName()) != meth:
                continue
            ca = m.getMethodInfo().getCodeAttribute()
            et, cp = ca.getExceptionTable(), m.getMethodInfo().getConstPool()
            for i in range(int(et.size())):
                ct = int(et.catchType(i))
                if ct:
                    out_.append(str(cp.getClassInfo(ct)))
        return out_
    K.check("java.util.ConcurrentModificationException" in catches(PKG + "WdFn", "canDeposit") and "java.util.ConcurrentModificationException" in catches(PKG + "WdCmds", "admin"),
            "FIX-E2 bytecode: wardrobe:fn:canDeposit and /requipadmin info answer 'busy' when a read meets a change on the player's world thread")
    wm = [l for l in allcode if "ItemStack.withMetadata" in l]
    K.check(wm and all("(Ljava/lang/String;Lorg/bson/BsonValue;)" in l or "(Lorg/bson/BsonDocument;)" in l for l in wm), "B the stamp is written with withMetadata(key, value) only")
    # spec F2 desk check: SkyyGear's own document writes keep foreign keys (GearView.apply / GearData.put use withMetadata(key, value))
    if GEAR and os.path.isfile(GEAR):
        CPl.appendClassPath(GEAR)
        gv = bytecode_calls(CPl, IP, "com.skyy.gear.GearView", "apply")
        gp = bytecode_calls(CPl, IP, "com.skyy.gear.GearData", "put")
        bad = [l for l in gv + gp if ("ItemStack.withMetadata((Lorg/bson/BsonDocument;)" in l) or ("new #" in l and "ItemStack" in l and "Class com.hypixel.hytale.server.core.inventory.ItemStack" in l)]
        K.check(gv and gp and not bad, "B F2 (%s): GearView.apply / GearData.put never build a new ItemStack or replace the whole metadata - the stamp survives reforge / level-up / identify (%s)" % (os.path.basename(GEAR), bad[:3]))
    else:
        K.notes.append("B F2: no SkyyGear jar found - the SkyyGear desk check was skipped")
    K.save()


def run_audit(out):
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, FAKE_DIR):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)), str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": []}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    json.dump(res, open(out, "w"), indent=1)


def run_compare(out):
    """C: class compare 0.1 vs 0.2 (javassist reads both jars; nothing is loaded)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    res = {}
    for tag, jar in (("old", BASE), ("new", JAR)):
        cp = JClass("javassist.ClassPool")(False)
        cp.appendSystemPath()
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendClassPath(jar)
        m = {}
        for n in zipfile.ZipFile(jar).namelist():
            if not n.endswith(".class"):
                continue
            cn = n[:-6].replace("/", ".")
            cc = cp.get(cn)
            m[cn] = sorted("%s%s" % (x.getName(), x.getSignature()) for x in cc.getDeclaredMethods()) + sorted("F:%s" % f.getName() for f in cc.getDeclaredFields())
        res[tag] = m
    old, new = res["old"], res["new"]
    kept = sorted(set(old) & set(new))
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = {c.rsplit(".", 1)[-1]: {"-": len(set(old[c]) - set(new[c])), "+": len(set(new[c]) - set(old[c]))} for c in kept if old[c] != new[c]}
    K.check(not removed and added == [], "C 0.2.10 -> 0.2.11: no class added or removed (%s / %s)" % (removed, added))
    real = sorted(c for c in changed if not c.startswith("Cfg"))
    # WdStore / WdOps / WdPage: only method BODIES change (abmods, applyAbil, refPick, the cells / pickers) - the signature compare cannot see that
    K.check(real == ["WdBridge", "WdPage"] and changed["WdPage"] == {"-": 0, "+": 1} and changed["WdBridge"] == {"-": 0, "+": 4}
            and "petIcon(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;" in new[PKG + "WdPage"]
            and {"F:PKIND", "rarRank(Ljava/lang/String;)I", "lvOf(Ljava/lang/String;)I", "petCmp(Ljava/lang/String;Ljava/lang/String;)I"} <= set(new[PKG + "WdBridge"]),
            "C (0.2.11) WdPage + petIcon, WdBridge + PKIND / rarRank / lvOf / petCmp; the rest: bodies only: %s %s" % (real, changed))
    for c_ in real:
        K.check(set(old[PKG + c_]) <= set(new[PKG + c_]), "C every 0.2.6 %s member is still there (only additions)" % c_)
    K.notes.append("C kept %d classes, %d changed: %s" % (len(kept), len(changed), changed))
    K.save()


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD, "--live", LIVE,
                                                                                   "--gear", GEAR or "-", "--seed", str(SEED), "--fuzz", arg("--fuzz", "260"),
                                                                                   "--fuzz-seeds", ",".join(str(s_) for s_ in FUZZ_SEEDS),
                                                                                   "--collide-seeds", ",".join("%d@%d" % (s_, n_) for s_, n_ in COLLIDE_SEEDS) or "-",
                                                                                   "--collide-ops", arg("--collide-ops", "400")], env=env)


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
    global GEAR
    if GEAR == "-":
        GEAR = ""
    for flag, fn in (("--mkfake", lambda: run_mkfake(FAKE_DIR)), ("--mk01", lambda: run_mk01(arg("--out"))), ("--x", lambda: run_x(arg("--out"))),
                     ("--perm", lambda: run_perm(arg("--out"))), ("--bc", lambda: run_bytecode(arg("--out"))), ("--audit", lambda: run_audit(arg("--out"))),
                     ("--cmp", lambda: run_compare(arg("--out")))):
        if flag in sys.argv:
            fn()
            return
    if "--live-step" in sys.argv:
        run_live(arg("--live-step"), arg("--out"))
        return
    only = arg("--only")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp)
    env = dict(os.environ, TEMP=tmp, TMP=tmp)
    # ---- J: the jar
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    classes = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(man["Name"] == "%s SkyyWardrobe" % VERSION and man["Main"] == PKG + "SkyyWardrobePlugin" and man["IncludesAssetPack"] is True, "J manifest (0.2.6: an asset pack - the kit art)")
    check(classes == CLASSES, "J exactly the expected classes (extra %s, missing %s)" % (sorted(set(classes) - set(CLASSES)), sorted(set(CLASSES) - set(classes))))
    _kitf = SUI.kit_texture_files()
    check(sorted(n for n in names if not n.endswith(".class") and n != "manifest.json") == sorted(_kitf) and all(z.read(p_) == d_ for p_, d_ in _kitf.items()),
          "J (0.2.6) no asset / .ui / lang file but the 59 Sky Window kit files, the kit's pinned bytes")
    child(env, "--mkfake")
    steps = [("--mk01", "M01"), ("--x", "X"), ("--perm", "P"), ("--bc", "B"), ("--cmp", "C")]
    for flag, label in steps:
        if only and label not in only.split(","):
            continue
        o = os.path.join(SCRATCH, "%s.json" % label)
        child(env, flag, "--out", o)
        take(o, label)
    if not only or "AA" in only.split(","):
        o = os.path.join(SCRATCH, "AA.json")
        child(env, "--audit", "--out", o)
        if os.path.isfile(o):
            a = json.load(open(o))
            check(not a["refused"] and a["refs"] > 500 and a["classes"] == len(CLASSES), "AA every engine member referenced is accessible (%d refs, %d classes): %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) >= 1, "AA the control class (a protected engine call) IS refused")
        else:
            check(False, "AA wrote no result")
    # ---- D: start twice on a scratch COPY of the live world mods folder, then the live 0.1 file migrates on that copy
    if not only or "D" in only.split(","):
        home = os.path.join(SCRATCH, "live")
        if os.path.isdir(LIVE):
            live_before = tree_hash(LIVE)
            shutil.copytree(LIVE, home)
            before = tree_hash(home)
            o = os.path.join(SCRATCH, "D1.json")
            child(env, "--live-step", "1", "--out", o)
            take(o, "D1")
            mid = tree_hash(home)
            added = sorted(set(mid) - set(before))
            changed = sorted(k for k in before if k in mid and mid[k] != before[k])
            exp_added = [] if "Skyy_SkyyWardrobe/config.properties" in before else ["Skyy_SkyyWardrobe/config.properties"]
            kitf = lambda k_: k_.startswith("Skyy_SkyyWardrobe/config-history/") or k_ == "Skyy_SkyyWardrobe/config-changes.log"
            check(all(k_ in exp_added or kitf(k_) for k_ in added) and all(k_ in exp_added for k_ in added if not kitf(k_)) and set(changed) <= {"Skyy_SkyyWardrobe/config.properties"}
                  and (not changed or "requip-0.2.2-free10" in open(os.path.join(home, "Skyy_SkyyWardrobe", "config.properties"), encoding="latin-1").read()),
                  "D start 1 writes nothing but the 0.2.2 free loadouts update (config.properties + its history copy / change-log line); every other file "
                  "stays byte for byte (added %s, changed %s)" % (added, changed))
            o = os.path.join(SCRATCH, "D2.json")
            child(env, "--live-step", "2", "--out", o)
            take(o, "D2")
            after = tree_hash(home)
            check(after == mid, "D start 2 writes nothing (%s)" % sorted(k for k in set(after) | set(mid) if after.get(k) != mid.get(k)))
            o = os.path.join(SCRATCH, "D3.json")
            child(env, "--live-step", "3", "--out", o)
            take(o, "D3")
            after3 = tree_hash(home)
            ch3 = sorted(k for k in mid if after3.get(k) != mid[k])
            add3 = sorted(set(after3) - set(mid))
            check(not ch3 and all(k.startswith("Skyy_SkyyWardrobe/requip/") or k == "Skyy_SkyyWardrobe/requip.log" for k in add3),
                  "D3 the migration only ADDED files under Skyy_SkyyWardrobe/requip/ (+ the requip.log MIGRATE line), or nothing when the live "
                  "copy is already migrated (changed %s, added %s)" % (ch3, add3))
            check(tree_hash(LIVE) == live_before, "D nothing was written into the live folder itself (byte-identical before / after)")
        else:
            check(False, "D the live world mods folder is missing: " + LIVE)
    print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL", f)
    if "--keep" not in sys.argv:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()


