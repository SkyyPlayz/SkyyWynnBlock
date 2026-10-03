# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `DESIGN-STATUS.md` "Open questions".

## Answer first (they block or shape the next builds)
1. ANSWERED 2026-09-25: **block** (refuse the sender). Was: **Settings menu: refuse or hide?** When a player switches off party invites, teleport requests or private messages, should the other
   player be refused (Hypixel style), or should the message just be hidden? Staff bypass? [not built yet - these 3 switches wait for you]
   (`research/Settings-Spec.md` section 6)
2. **SkyyEconomy merge:** go ahead once you have tested the separate Bank 0.1.3, Bazaar 0.1.2 and Auctions 0.1? [yes, next round after your test]
3. ANSWERED 2026-09-25: Mining bag from **Iron**. Was: **Bags:** do the Mining bag upgrades come from the Cobblestone or the Iron collection? Which collections grow Foraging, Farming, Combat and
   the new Smithing bag? [today every bag is crafted at a Workbench]

## Q&A with Skyy 2026-10-02 (all open questions, round by round - newest answers win)

- R1 LOCKED (Skyy) [LIVE 2026-10-02 SkyySkills 0.4.12]: CLASS SKILL CURVE = the cloud proposal as written (research/cloud/Class-Skill-Curve-Proposal.md): a separate table for
  class skills only, XP per level = 50 x L + 0.25 x L^3 (rounded); skill 20 ~4 h, 40 ~17 h, 100 ~200 h of fighting; never below today at
  any level (levels only go up); editable rows levels.class / .scale / .max / .sameAsOthers. [next SkyySkills]
- R1 LOCKED (Skyy): gathering skills keep the Hypixel table for now - revisit when tools get levels / requirements.
- R1 LOCKED (Skyy): wand / spellbook / staff recipes MATCH VANILLA WEAPONS - same bench and the same metals / amounts as that material's other
  vanilla weapons (Wood, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril). [with SkyyGear 0.2]
- R1 ANSWERED (Skyy, own answer): MANA REGEN IN COMBAT = HALF ("for now, might change later") instead of vanilla's 0 for 6 s after taking
  damage, so Mana Regen boosts work in and out of combat. Skyy asked whether to add the boost then halve, or halve vanilla then add the
  boost - see round 2 (recommended: Mana Regen boosts are %, and with % boosts the order makes no difference).
- R2 LOCKED (Skyy) [LIVE 2026-10-02 SkyySkills 0.4.12]: Mana Regen boosts are PERCENT ("+20% Mana Regen"); in combat the WHOLE regen (vanilla + boosts) runs at 50% - one
  Server Setup row "In-combat Mana regen" (default 50%). Combat = vanilla's window (6 s after taking damage), where vanilla gives 0 - our
  mod supplies the regen there. Replaces the earlier flat "+N every 5 s" recommendation. [next SkyySkills / caster build]
- R2 LOCKED (Skyy): bags keep collecting from the MAIN inventory only. Skyy's worry - pull 8 stacks of stone out for building, only 1 fits the
  hotbar: today the withdrawn item is EXEMPT from auto-collect for 10 minutes (SkyySacks SackPool.exempt 600000 ms; "Deposit all" clears it);
  after that, leftovers still in the main inventory go back into the bag. See round 3 for the timer.
- R2 LOCKED (Skyy) [TRIED 2026-10-02: NOT POSSIBLE with the current client - probes P1 + P2 showed no chest slots on our own page; the in-chest arrows stay; re-check on 0.7]: try the one-click vault arrow row on our own vanilla-look page next to the vault slots (one probe first; the in-chest arrows
  stay as a fallback). [next SkyyVault]
- R2 LOCKED (Skyy): Magic Bags are blocked in /trade too (same rule as the AH). [next SkyyEssentials]
- R3 LOCKED (Skyy) [LIVE 2026-10-02 SkyySacks 0.7.11 + Collections 0.2.5]: withdrawn bag items - auto-collect LEAVES ALONE THE AMOUNT YOU TOOK (take out 512 stone -> up to 512 stone stay in your
  inventory; placing blocks lowers it; anything above it, e.g. newly mined, still goes in; no timer; Deposit all resets). Replaces the
  10-minute per-item exemption. NEW IDEA from Skyy: stacks you are using AUTO-REFILL from the bag every few seconds (grab one stack of stone,
  build, it tops back up to full - never go back to the bag). Details in round 4. [next SkyySacks]
- R3 LOCKED (Skyy): Charged Attack Damage stays left out of the Vampire shortbow, Kunai and Crystal staffs for now; a stand-in trigger later.
- R3 LOCKED (Skyy): SkyyEconomy merge (Coins + Bank + Bazaar + Auctions) goes ahead after Skyy has tested the separate mods.
- R3 LOCKED (Skyy): bag unlock collections / tiers / upgrade scraps stay as they are. NEW RULE (replaces the 2026-09-24 coin-bypass lock and
  bypass.bagMax): COINS NEVER SKIP COLLECTIONS OR BAGS - coins can buy items you have not unlocked yet on the Auction House / Bazaar, but can
  never buy a collection tier, a recipe unlock or a bag (remove SkyyCollections' "Buy tier unlocks" and the bag coin unlock). Skyy: "you
  can just make 2 or 3 bags of a lower level if one isnt enough" -> today only the BEST carried bag counts per type (SkyySacks caps() takes
  the max) - see round 4 about adding them up.
- R4 LOCKED (Skyy) [LIVE 2026-10-02: refill in SkyySacks 0.7.11; benches + inventory crafting really use your bags since 0.7.12 - the 0.7.10 bench link never reached the client]: STACK AUTO-REFILL from bags with a player setting in the Sacks page, 3 options: HOTBAR ONLY / FULL INVENTORY / OFF.
  Skyy: full inventory is for brewing, cooking and crafting at normal benches - "unless you can get the normal benches to pull only from the
  players bag while they are crafting, and not everyone's bag. then id do hot bar stacks only." Note: SkyySacks already has that per-player
  bench link (BagMirror feeds the open vanilla bench from THAT player's carried bags only, 0.7.x) -> default HOTBAR ONLY; check in game that
  the bench link covers the cooking / alchemy benches. [next SkyySacks]
- R4 LOCKED (Skyy): carrying 2-3 bags of the same type ADDS their space together (today only the best bag counts - SkyySacks caps() max).
  [next SkyySacks]
- R4 LOCKED (Skyy): keep the late-game market wall (some late items can never be bought / sold); the list stays empty until Skyy names items.
- R4 LOCKED (Skyy): Overall Level +0.5 max Health / +0.2 max Mana per level stays until a playtest. NEW REQUEST: a HUD WIDGET for the Overall
  Level and skills, where each skill can be toggled on / off in the widget (show all, or just the class level, or Overall + Mining - any
  combo). [next SkyyHud]
- R5 LOCKED (Skyy) [LIVE 2026-10-02 SkyyMobs 0.1] - SkyyMobs (research/Mob-Levels-Plan.md + research/cloud/Mob-Levels-Refit.md): levels on HOSTILE mobs AND NEUTRAL
  FIGHTERS (mobs that fight back: boars, Scaraks ...); animals / passive never.
- R5 LOCKED (Skyy): +4% health / +2% damage per level by default, with a DIFFICULTY setting in Server Setup that changes it (e.g. presets
  Easy 3% / 1.5%, Normal 4% / 2%, Hard 6% / 3%, plus custom).
- R5 LOCKED (Skyy): rewards - XP follows mob health (higher levels pay more automatically); mobs far below your level pay less (5 levels free,
  then -5% per level, floor 10%); +1% bonus drop chance per level (cap 50%) and slightly better gear rarity from higher levels; no coins yet.
- R5 LOCKED (Skyy): keep the other defaults (nameplate "[Lv 9] Name" + colour ladder on every levelled mob; elites later 3% / +3 levels /
  2x health / 1.3x damage / a guaranteed gear roll; no mob armour; no night bonus; random level inside the range; mod name SkyyMobs).
  OCEANS: skip - the world gen islands have no oceans. CAVES: the level of the ground above, EXCEPT the deep lava caves (vanilla's volcanic
  caves, Env_ZoneN_Caves_Volcanic_T1-T3 - "really hard in the default game, lets keep that") = the range of the HARDEST biome of that zone
  (Zone 1 deep caves about Lv 17-20).
- R6 LOCKED (Skyy) - pets (research/Pets-Idea.md, research/cloud/Pets-Spec.md): the second slot is unlocked by a ZONE 2 STABLE QUEST (a
  stable master gives the slot + your first mount pet).
- R6 LOCKED (Skyy): a pet in the second slot gives its buffs at 50%, always (Server Setup row). LATER: a hotkey to SWAP the two slots (with a
  mount pet in both, swap which one is the pet and which the mount). Skyy's question - should combat pets in BOTH slots fight, or only the
  second? If only the second, rename it the "SUMMON SLOT": it holds mounts AND combat pets (many pets are both - they fight while you are on
  foot). See round 7.
- R6 LOCKED (Skyy): pet XP = its own skill's XP + 50% of all other XP (editable in settings).
- R6 LOCKED (Skyy): a fighting pet that loses all its health retreats into its slot and loses nothing; it can come out again after a short
  cooldown (default 60 s, editable).
- R6 ADDED (Skyy): the pet's resummon cooldown after a defeat SHRINKS WITH THE PET'S LEVEL (e.g. 60 s at Lv 1 down to about 15 s at
  Lv 100 - placeholder numbers, editable).
- R7 LOCKED (Skyy): only the SECOND slot fights - renamed the SUMMON SLOT: it holds mounts AND combat pets (50% buffs; the creature fights
  while you are on foot and is ridden when you mount); slot 1 = the pet slot, full buffs, never fights. The Summon slot unlocks with the
  Zone 2 stable quest; a later hotkey swaps the two slots.
- R7 LOCKED (Skyy) - Pocket Shards (research/cloud/Pocket-Shards-Spec.md): 12 types at launch, then grow - Cobblestone, Copper, Iron, Oak,
  Birch, Wheat, Carrot, Pumpkin, Bone, Hide, Feather, Charcoal; items count for collections WHEN YOU COLLECT them; auto-sell LATER with
  SkyyEconomy (NPC prices + a daily cap).
- R8 LOCKED (Skyy) - dragons (research/Dragon-Pets-Idea.md): ZONE 5 = the dinosaur caves under Zone 4 as their own zone, Lv 60-75, the
  dragon boss at 75 (needs our own gear tiers above 49 first).
- R8 LOCKED (Skyy): ONE DRAGON PER PROFILE for now. Later maybe a much harder quest for a second egg - Skyy's idea: when your dragon gets
  older it gets lonely and you go on a quest to find it a MATE, and that's how you get another egg.
- R8 LOCKED (Skyy): dragons follow the pet rules (combat XP + 50% of other XP), grow bigger at set levels, and can be flown from Lv 10
  (growth steps and the flight level are settings).
- R8 LOCKED (Skyy): starter shard gaps - BOTH: the first gap has a broken bridge you repair, the later gaps you build across with your own
  blocks (research/Isles-of-the-Void-Lore.md).
- R9 LOCKED (Skyy): KEEP ALL the small live defaults not otherwise marked in this file - tree felling XP (felled logs full XP +
  collections, leaves normal XP, placed logs never), party combat XP 50% within 48 blocks, menu hover tooltips on, staff bypass on, two
  crossbows share one big-arrow meter, AH 48h never cheaper than 24h (xFloorPrev on), old SkyyRolls rolls not clamped (clampToLevel off),
  SkyyRanks placeholders (Admin = kick + Server Setup + staff bypass, no ban; Developer = Admin's; Owner = rank editor; only real ops grant
  op-level nodes; no grants below Member), the vanilla UI look defaults (readable text, footer Close, vanilla colours / tabs / frames, Mythic
  #CC66CC, current text-box look), no sickle / gear swing-speed for now, a deleted profile's AH claims stay in its archive (admin can regrant),
  rank perks later, the picked non-metal gear levels (ranges in SkyyGear 0.2).
- R9 LOCKED (Skyy): outpost towns SHARE one outpost between near-identical biome variants (about 30-35 outposts, each an unlockable warp).
- R9 LOCKED (Skyy): pet details as the cloud spec proposes (rarity raised with Upgrade Stones, eggs can be found at higher rarities, pets per
  profile, pet score bonus later) - BUT Upgrade Stones are PER SKILL / MINION TYPE (Mining stones, Combat stones, ...), and late-game pets
  like dragons have their own DRAGON Upgrade Stones.
- R9 BUILD ORDER (Skyy): FIRST the quick fixes (SkyySacks: withdraw amount, auto-refill 3-way setting, bags add up; SkyyCollections: coins
  never buy tiers / recipes / bags; SkyyEssentials: bags blocked in /trade; SkyyVault: one-click arrow page behind a switch) + the skills HUD
  widget (SkyyHud); THEN the big round (class skill curve + in-combat Mana regen in SkyySkills; SkyyGear 0.2 per-item levels + Armor_Copper
  default + wand / spellbook / staff recipes); THEN SkyyMobs stage 1 if usage still looks good.

- OPEN 2026-10-02 (from the SkyySacks 0.7.11 review): carried bags of one type now add up with NO limit, so e.g. 54 Normal bags hold more
  than a Legendary. Keep unlimited (each extra bag costs a slot and a recipe), or a Server Setup cap on bags counted per type (e.g. 3)?
  [unlimited]
- OPEN 2026-10-02 (same review): an idle partial stack only tops up once you use it. Also top up the stack in your selected hotbar slot
  even when idle? [only when used]

- ANSWERED 2026-10-02 (Skyy: "custom metal wands. can you create the art?" - see the Q&A block). Was: OPEN 2026-10-02 (SkyyGear 0.2 review): vanilla has NO material wands or spellbooks - only the Wood Wand - so Priests can craft just
  the Wood Wand at their level (Mages get a staff per material: the new staff recipes mirror each material's shortbow). Make our own
  material wands / spellbooks (custom items, e.g. Copper -> Mithril), let Priests use staffs, or wait for custom Priest weapons? [wait]
- OPEN 2026-10-02 (SkyySkills 0.4.12 review): everyone has 10 base Mana, so Warriors / Archers also get the in-combat Mana refill. Limit it
  to classes that use Mana (Mage, Priest)? [everyone - harmless today]
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your
  live profiles gained nothing (little class XP yet); check the coin rate before a public launch.
- LOCKED 2026-10-02 (Skyy) - SMITHING TREE + XP (for research/Skill-Trees-2-Spec.md / SkyyTrees 0.3): (1) the craft RARITY CHANCE is raised by
  Smithing levels (live: smith.perLevel 0.5% a level, cap 50%) AND by Smithing tree nodes; (2) a REFORGE line in the tree gives BETTER ROLLS
  when reforging (higher modifier values / better picks); (3) an IDENTIFIER upgrade in the tree gives better-quality loot when you identify
  unidentified gear (better rolls / a chance at a higher rarity on identify); (4) CRAFTING gear, REFORGING and IDENTIFYING all pay Smithing XP
  (check what pays today - reforge pays per rarity; add crafting gear + identifying where missing). Today's craft odds (Server Setup -> Gear ->
  Drops): Normal 60 / Unique 25 / Rare 10 / Legendary 4 / Fabled 1 / Mythic 0 (crafting max Fabled); a reforge never changes the rarity.
- LOCKED 2026-10-02 (Skyy): a COMBAT INDICATOR HUD widget - red while in combat, with a small countdown and a shrinking bar showing how close
  you are to being out of combat (same rule as the in-combat Mana regen: 6 s after taking damage); out of combat hidden by default (widget
  setting). [building: SkyySkills 0.4.13 bridge skill:fn:combat + SkyyHud 0.3.12 widget]
- VERIFIED 2026-10-02 (Skyy's screenshot): /skills mana works ("out of combat - vanilla refills 5/s"; "In combat: 50% of (vanilla + boosts)
  = 2.5/s"); reforges pay Smithing XP (+5 / +10).
- LOCKED 2026-10-02 (Skyy, after testing Hard): "make the current hard mode the normal and give hard mode a little better bump. i can still
  beat lvl 19 at lvl 7 with my accessories off, when im careful." -> mob difficulty presets Easy 4% / 2%, NORMAL 6% / 3% (default), HARD 8% / 4%;
  caps raised to health x6 / damage x3.5. The chosen word is kept on update (Skyy is on Hard = the new 8% / 4%). [LIVE: SkyyMobs 0.1.1,
  deployed 2026-10-02 with the short labels]
- LOCKED 2026-10-02 (Skyy): crouching as you land (vanilla's roll) takes less fall damage - make that ROLL pay EXTRA Acrobatics XP.
  [queued: next SkyySkills after 0.4.13 (the combat-widget bridge) lands]
- LOCKED 2026-10-02 (Skyy): "boost the mining xp a little, kinda flatten the curve. at least through the early game." -> proposed defaults
  (editable rows): Mining XP x2 up to level 10, easing down to x1.25 by level 20 and staying x1.25 after (so early Mining levels come about
  twice as fast, later ones a bit faster); other gathering skills unchanged for now. [REPLACED 2026-10-02 by the tool-levels answer (4): x3 to Lv 10 -> x1.5 by Lv 20 for Mining, Foraging and Farming]
- LOCKED 2026-10-02 (Skyy): WAIT FOR THE 0.7 RELEASE - no pre-release pack / test world. Groundwork now on the current release: class skill
  trees with passive nodes + EMPTY ability slots shaped for runes (research/Skill-Trees-2-Spec.md, being written), the 0.7 compatibility audit
  of all 24 mods (research/PreRelease-Compat-Audit-1002.md), rune research. On release day: fix the audit's list, then build the abilities
  into the slots.
- ASKED 2026-10-02 (Skyy): "add a night vision accessory if you can." -> Hytale has no vanilla night-vision effect (Assets.zip: no such
  entity effect). Research running (wf_4726d526-aa2): screen/camera effect fields, a light on the player like a held torch, or any
  per-player light the server can send. If one works: SkyyAccessories 0.5.3 adds a Night Vision accessory (its own line so it stacks with the
  boosters, admin-give like the other boosters for now, only on while it sits in the Accessory Bag, off at once when removed; Server Setup
  switch). If nothing works, it waits for 0.7.
- LOCKED 2026-10-02 (Skyy): TOOL LEVELS like weapons - "tools like the pickaxe to have levels, linked to the users mining. (need a to be
  mining lvl 13 to use a lvl 13 pickaxe. like weapons, crafted tools are made at your level." + "same for foraging and farming" + "they
  need to be reformable [reforgeable] too". Gate skill: pickaxe + shovel = Mining, hatchet = Foraging, hoe + sickle = Farming. Crafted
  tools come out at that skill level inside the material band (Copper tools keep 10-18, locked 10-01).
  Answers (all picked 2026-10-02): (1) UNDER-LEVEL = the tool cannot break blocks; popup "Requires Mining 13 (you: 9)" (like weapons
  doing 0 damage). (2) The tool's LEVEL raises its breaking speed AND a small Fortune (double-drop chance); the better material a little
  more; hoes / sickles get Fortune only. (3) REFORGE pool: pickaxe / shovel = Mining Fortune, Mining Wisdom, Mining Speed; hatchet =
  Foraging Fortune, Foraging Wisdom, Chopping Speed; hoe / sickle = Farming Fortune, Farming Wisdom; rarity like weapons, reforge keeps
  rarity. (4) PACING ("Bigger boost for all 3", replaces the Mining-only x2 plan): Mining, Foraging AND Farming XP x3 up to Lv 10,
  easing to x1.5 by Lv 20, x1.5 after (editable rows; next SkyySkills after 0.4.13, with the roll-landing Acrobatics XP).
  R1 (gathering skills keep the Hypixel table "revisit when tools get levels") is answered by (4). [spec being written:
  research/Tool-Levels-Spec.md; build = SkyyGear 0.2.2 after 0.2.1 lands]
- LOCKED 2026-10-02 (Skyy): ACCESSORY TABLE - "instead of rolling it all into the normal crafting table, we should make our accessory's
  their own crafting table. (and an accessory for /craft. + added to omni." Answer (picked): EVERYTHING moves to the new table -
  every accessory (stat lines, bench accessories, the Omni), the Accessory Bag + its upgrades AND every Magic Bag (sack); the Workbench
  "Accessories & Sacks" tab goes away. The table itself is crafted at the Workbench. A new bench accessory for it unlocks its recipes in
  /craft (like the other bench accessories), and the Omni covers it (grant + recipe). Order inside the table as before: low levels first,
  Legendaries and Omnis last. [build: SkyyAccessories next version (after the Night Vision round) + SkyySacks 0.7.13, one shared bench
  definition so both mods stay standalone]
- LOCKED 2026-10-02 (Skyy): "make sure your memory crafting limiters work on /craft. so you cant bypass vanilla progression with /craft."
  Today /craft already checks recipe knowledge (KnowledgeRequired, SkyySacks 0.7.12 recipeAllowed) but NOT vanilla's Memories level
  (RequiredMemoriesLevel on 38 vanilla recipes: chests, trophies, morph potions ...). SkyySacks 0.7.13 adds that check and re-checks bench
  tiers, so /craft can never craft what the real bench would refuse.
- LOCKED 2026-10-02 (Skyy): "boost the drop rates of unidentified weapons and armor." Today SkyyGear only TAGS vanilla's own gear drops
  as unidentified (vanilla drop odds). Answer (picked): each kill of a leveled hostile mob gets an EXTRA 4% roll (1 in 25) for one
  unidentified weapon or armor piece matching the mob's level; about 1 in 3 world chests gets an extra unidentified piece matching the
  zone. Both editable in Server Setup. [build: SkyyGear 0.2.3 LOOT round (with the Wynncraft-style unidentified items), after 0.2.2 tools]
- LOCKED 2026-10-02 (Skyy): SMITHING TREE - "you can also add a chance to boost the rarity when identifying." -> a Smithing tree node:
  chance that identifying an item steps it up one rarity (joins Skyy's earlier Smithing tree list: better crafted-rarity chance, better
  reforge rolls, the identifier upgrade for better loot, Smithing XP from crafting / reforging / identifying). [goes into
  research/Skill-Trees-2-Spec.md + SkyyTrees 0.3; SkyyGear 0.2.2 reads the tree bonuses at craft / identify / reforge through skill:bonus
  so the nodes work the day the tree ships]
- LOCKED 2026-10-02 (Skyy): WYNNCRAFT-STYLE UNIDENTIFIED ITEMS - "do it like wynncraft where it lists the level and rarity, but you wont
  see what type of sword or bow or chess plate it will be till you identify it." -> an unidentified drop becomes a mystery item such as
  "Unidentified Sword" / "Unidentified Bow" / "Unidentified Chestplate" showing its level and rarity; which sword / bow / chestplate it
  really is (material, model, stats) appears only when identified. Defaults (change any): exact level shown (not a range); one mystery item
  per weapon family and armor slot; they do not stack; vanilla gear drops become mystery items too; unidentified items already owned stay
  as they are and identify normally. [build: SkyyGear 0.2.3 LOOT round = this + the drop boost + the Smithing-tree identify-rarity hook,
  after 0.2.2 tools; spec first]
- LOCKED 2026-10-02 (Skyy, from testing): "mana doesn't continue regening while charging an attack, id change that" -> vanilla Mana.json
  pauses regen while Charging (and 6 s after damage); SkyySkills 0.4.12 treats charging as "no regen" too. Change: Mana keeps regenerating
  while you charge (full rate out of combat, the half in-combat rate in combat). [next SkyySkills after 0.4.13, with the roll-landing XP and
  the x3 -> x1.5 gathering XP boost]
- LOCKED 2026-10-02 (Skyy): "id increase the amount of mining dust you get too, by probably double" -> Mining tree Dust rate 10 -> 5 XP
  per Dust (double). Live today in game: SkyWynn Menu > Server Setup > Trees > "Dust rate per tree" > add Mining = 5 (no restart; Dust
  is computed from total Mining XP and never stored, so everyone's Mining Dust doubles at once, spent Dust included). New pack default
  in SkyyTrees 0.3 (a file with no dust.xpPerDust.Mining line gets Mining=5; a hand-set value is kept). Note: the coming x3 early
  gathering XP boost also raises Dust (Dust comes from XP).
- LOCKED 2026-10-02 (Skyy): PRIEST WEAPON PATH = "custom metal wands. can you create the art?" -> our own Copper, Iron, Thorium, Cobalt,
  Adamantite, Mithril (+ Onyxium) wands, one per metal like the Mage staffs, same cast as the Wood Wand, levels from the metal bands
  (Copper 10-18 ... Mithril 40-49), recipes mirroring vanilla weapons of the same metal. ART: the vanilla pattern (Weapon_Wand_Wood_Rotten
  reuses the Wood Wand model with another texture) - each metal wand = the Wood Wand model + a texture / icon recoloured from that metal's
  own vanilla art AT BUILD TIME (shared kit tools/skyyart.py, nothing vanilla committed). Art proof running: two styles (full metal / wood
  handle + metal head) on a preview sheet for Skyy to pick before the build. Default home: a new content mod SkyyArmory (our own weapons
  and armor; later the Crude armor and Lv 50+ gear) so it does not wait behind the SkyyGear queue. [art proof -> Skyy picks -> build]
- LOCKED 2026-10-02 (Skyy): mod name "SkyyArmory is a good name, go with it". WANDS: tap = a cheaper FAST SHOT (blue, smaller projectile,
  3x faster, 1/5 the Mana and 1/5 the damage); click-and-hold = the CHARGED shot. Mana cost scales per metal and damage grows "slightly
  more": Wood (stick) 5 / quick 1 = 1x; Copper 10 / 2 (~2.25x); Iron 15 / 3 = 3.5x (Skyy's numbers); "the next 3 will be bigger jumps"
  (Thorium, Cobalt, Adamantite). Proposed defaults (rule: damage = 1.25 x cost multiple - 0.25; checked against the Priest's real max Mana
  in the spec): Thorium 25 / 5 (6x), Cobalt 40 / 8 (9.75x), Adamantite 60 / 12 (14.75x), Mithril + Onyxium 85 / 17 (21x). The wand's level
  still raises damage like all gear; the metal sets the Mana cost and its matching multiplier. Asked whether to merge SkyyArmory into
  SkyyGear: recommended separate (content mod ships without waiting behind the SkyyGear queue; SkyyGear's levels / rarity / reforge apply
  to the wands through the metal bands anyway). [spec running: research/SkyyArmory-Spec.md; art proof running; build after Skyy picks a style]
- CHECKED 2026-10-02 (Skyy: "not sure the levels are scaling right" after a Lv 32 cobra died in 2 shots for 60 XP and a Lv 33 skeleton
  paid 108): the live server log shows the level health scaling is exact - max health = vanilla x (1 + 6% per level - Skyy's current Hard,
  the coming Normal): Skeleton_Scout Lv 33 = 61 x 2.92 = 178 HP (-> 36 x 3 = 108 XP), Snake_Marsh Lv 17, Wolf_Black Lv 7, Bear_Grizzly
  Lv 10, Fen_Stalker Lv 16, Skeleton_Fighter Lv 9 all match; the cobra's real base is only 36 HP, so ~100 HP at Lv 31-32.
- LOCKED 2026-10-02 (Skyy): KILL XP = "level bonus + gap rule max +250%": kill XP x (1 + 5% per mob level); a mob more than 5 levels ABOVE
  your class skill gives +5% per extra level, at most +250%; more than 5 levels BELOW gives -5% per level, at least 10%; the party share uses
  each member's own skill. (Lv 33 skeleton at Divinity 11: 108 -> ~520 XP.) [next SkyySkills after 0.4.13]
- LOCKED 2026-10-02 (Skyy): LEVEL HEALTH FLOOR - no leveled mob has less health than a 50-HP mob of its level (a Lv 32 cobra ~100 -> ~143
  HP at 6%, more on the new Hard); stronger mobs unchanged; kill XP follows the health. [SkyyMobs 0.1.2]

## Numbers picked in the beta round (live now)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- LOCKED 2026-09-25 (Skyy): **Vault:** 2 free pages, max 10, page 3 = 50,000 coins, each next page +25,000. Pages are shared across all profiles
  (Wynncraft style). [as written — already the live defaults]
- LOCKED 2026-09-25 (Skyy): **Tree Feller:** same height as the cut. Extra logs 1 / 2 / 4 / 5 / 6 / 10 at levels 1–6. Level 6 jumps to 10 so a
  very large tree is not broken as a whole layer (that could crash). Cooldown 3 s (was 5). Was: 1 / 2 / 3 / 4 extra logs, then the whole
  layer at max. [new-file cooldown is 3; a file still on the old stock `feller.cooldownSec=5` keeps 5 until that line is set to 3. The
  6-level table is the next Trees build — `research/Tree-Fall-Spec.md`]
- LOCKED 2026-09-25 (Skyy): **Double Jump:** Acrobatics tier III (slot 7, replaces Sprinter; Quick Dodge returns to tier II). Jump again
  while already in mid-air, not crouch. Stamina stays 2 (tier III does not name a different cost). Was: tier II, crouch in mid-air.
  [new-file trigger is `jump`; a file still on `acro.doubleJump.trigger=crouch` keeps crouch until that line is set to `jump`. The slot
  move is the next Trees build — `research/Double-Jump-Spec.md`]
- **Tree felling:** every felled log pays full Foraging XP and counts for collections; felled leaves pay their normal XP (about 1 each);
  placed logs never pay. [fell.xpFactor 1.0, fell.leafXpFactor 1.0]
- **Party combat XP:** members within 48 blocks in the same world get 50% of the killer's combat XP (the killer keeps 100%). [as written]
- **Menu hover tooltips:** on by default; the book switch turns them off if the stuck tooltip after Esc still happens. Default off? [on]

## Round 8 defaults (live 2026-09-28)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- Bag unlock collections: Mining = Iron (your call), Foraging = Oak Log, Farming = Wheat, Combat = Bone, Smithing = Light Hide; tiers I / III / V / VII. [proposed]
- Bag upgrade materials: Unique 6 Linen Scraps, Rare 6 Shadoweave Scraps, Legendary 6 Cindercloth Scraps (the old Loom bolts were impossible to get). [6 each]
- Coins can unlock bags up to Unique; Rare and Legendary must be gathered (bypass.bagMax). [unique]
- Should Magic Bags be blocked in /trade too (the auction house blocks them)? Otherwise a bag can skip its collection. [allowed]
- Staff bypass for the blocking switches is ON by default (ops + players with skyyparty.bypass / skyyessentials.bypass). [on]
- Overall Level: +0.5 max Health and +0.2 max Mana per level. [placeholders]
- Two crossbows keep only ONE banked big-arrow meter. [one]

## Round 9 + SkyyGear defaults (live 2026-09-29)
(2026-10-02: every line below that is not marked otherwise was confirmed or changed in the Q&A block above - the Q&A wins.)
- Auction house 48h: "double the listing fee", but never cheaper than the 24h price (built literally, 48h cost 20 coins on a 1,000-coin item
  vs 360 for 24h, so everyone would pick 48h). Server Setup key `xFloorPrev` - OFF = exactly 2 x the listing fee. [on]
- SkyyGear: old SkyyRolls items keep their rolls (your lock). Switch `migrate.clampToLevel` caps old rolls at what that item's level can
  roll now (a cheap SkyyRolls max roll on junk gear stays strong otherwise). [off]
- LOCKED 2026-09-30 (Skyy): item durability is a Server Setup switch, OFF by default - tools, weapons and armor never lose durability or break
  while it is off. [queued]
- REQUEST 2026-09-30 (Skyy): a MOB LEVEL system - research + plan only for now (check how other Hytale mods do it). Levels set by biome (the
  easiest: where the mob spawns); zone 1's blue forest and other zone-1 biomes slightly higher, zone 2 a big step up; inside a zone, rarer biomes
  = higher level. [plan queued: research/Mob-Levels-Plan.md]
- LOCKED 2026-10-01 (Skyy): Charcoal goes in the Smithing bag (it stayed in the hotbar). [LIVE 2026-10-01, SkyySacks 0.7.10]
- OPEN 2026-10-01: bags auto-collect only from the MAIN inventory (every bag item, since the bags first shipped) - items already in the
  hotbar or backpack stay there until "Deposit all" or you move them. Sweep the hotbar too? (Careful: it would also pull tools/food
  you keep on the hotbar if they belong in a bag.) [main inventory only]
- NOTE 2026-10-01: the real Furnace's fuel slot does not take fuel from bags - withdraw charcoal first (/craft's Furnace does read bags).
- LOCKED 2026-10-01 (Skyy): a new Workbench tab for accessories + sacks, in crafting order - low tiers first, Legendaries and the Omni bag
  at the bottom. Pocket-crafted recipes (the Accessory Bag) stay craftable from the inventory. [LIVE 2026-10-01, Accessories 0.5.2 + Sacks 0.7.10;
  the server sends the exact order - whether the game client keeps it is checked on your first look]
- LOCKED 2026-10-01 (Skyy): copper ARMOR starts at level 1 ("since there is no lower tier armor"); copper weapons/tools keep their level.
  Works today with no build: Server Setup -> Gear -> Levels -> "Level by material" entry Armor_Copper = 1 (an id-word entry at the
  start of the id beats the Copper row). [next SkyyGear: Armor_Copper=1 as a default + one-time add; the Wynn-style level spec: the
  copper armor range starts at 1]
- LOCKED 2026-10-01 (Skyy): Priest healing XP = 1 Divinity XP per HP healed on others, 1.25 per HP on yourself (what the player gets;
  was 0.6 / 0.75 after the x3 class boost). The healing XP cap stays 900 a minute; kill XP unchanged. [LIVE 2026-10-01, SkyySkills 0.4.11]
- LOCKED 2026-10-01 (Skyy): the way to the next zone island is a PORTAL at each island's summit that only opens once you beat the boss
  (until bosses exist: the staged unlock rule). Placed automatically in every solo world (islands are separate worlds - nobody builds
  across); a return portal at each landing point; /zone + menu only for islands already unlocked. [SkyyWorldGen plan 2.3]
- LOCKED 2026-10-01 (Skyy): every zone island has its own hub / main town (city) with a WARP; unlocking a zone unlocks its town warp.
  The town is at the landing point (safe rim): portals and warps arrive there. [SkyyWorldGen plan 2.3]
- LOCKED 2026-10-01 (Skyy): no separate hub island - the HUB is the main starter town on the Zone 1 island. PROPOSED (Skyy asked
  "should we have a temple in each town too?"): yes - a zone-themed temple at the centre of every town as its anchor (warp arrival,
  respawn, return portal, the zone's discovery reward, later the Memories turn-in). LOCKED 2026-10-01 (Skyy): start with the
  VANILLA temples and build each zone's starter town around one; plus at least one OUTPOST TOWN PER BIOME in every zone, each with
  an unlockable warp (found = unlocked). [SkyyWorldGen plan]
- LOCKED 2026-10-01 (Skyy, final - replaces the earlier Zone 3 / Zone 4 lines): ZONE BANDS Zone 1 = Lv 1-20 (copper AND iron),
  Zone 2 = 20-30, Zone 3 = 30-45, Zone 4 = 45-60, more past 60 later (zones 1 and 3 have the most biomes, so they stretch furthest).
  Guardians at 20 / 30 / 45 / 60; skill unlock = class skill 20 / 30 / 45. Ring ladder in SkyyWorldGen plan 4.5; Mob-Levels-Plan
  zone bands (was Z1 1-10, Z2 15-25, Z3 30-40, Z4 45-60) follow when SkyyMobs is built.
- PLAN 2026-10-01 (Skyy: "dont build yet, just make a plan"): SkyyWorldGen - Hytale zones as their own islands, biomes as progressively
  harder levels with level ranges -> research/SkyyWorldGen-Plan.md.
  ANSWERED 2026-10-01 by Skyy: (1) unlock = reach the summit today, then class skill 20 / 30 / 45 once the flatter curve ships,
  then beat the summit guardian once bosses exist (the recommended staged rule); (2) solo players start on a SMALL HUB ISLAND (a fifth
  world) and travel to the zone islands from it - NOT the normal Hytale world; (3) SHIFT ZONE 4 DOWN to about Lv 40-49 so vanilla gear
  covers it (our own tiers extend it later) - Zone 3 / Zone 4 level tables, guardian gaps and the Mob-Levels-Plan bands need a re-fit
  (proposed: Zone 3 30-38 with its guardian at 38-40, Zone 4 40-49 with a capstone at 50 - confirm when building).
- LOCKED 2026-10-01 (Skyy, later game): PETS = one system - SkyBlock-style buff pets that level up; better pets grow and fight; some
  are mounts (all mounts are pets, not all pets are mounts); an active pet slot + an UNLOCKABLE mount slot (mount pets only) that
  still gives the pet's buffs, weaker. Dragons = the top tier (research/Dragon-Pets-Idea.md). Details + 4 questions:
  research/Pets-Idea.md. [idea, not scheduled]
- IDEA 2026-10-01 (Skyy): name for the pack / server = "Isles of the Void" ("Iles" was a typo; nothing renamed). Islands = fragments /
  shards; story: the Void pulls pieces of worlds (and players) in from everywhere; you wake on your personal shard and unlock a portal
  to the Zone 1 hub shard. The main objective should be silly and absurd - pitches in research/Isles-of-the-Void-Lore.md.
- REQUEST 2026-10-01 (Skyy): gear levels like Wynncraft - "the gears level determines the stat it gives, and the gear level is the use
  requirement level" (e.g. Wooden earth staff Lv1 6-8 damage, Lv4 10-12, needs Priest level 4); "all items crafted are crafted at your level".
  Gate skill stays as ruled 2026-09-25: combat gear = your class weapon skill, mining/foraging/farming gear = that skill.
  Skyy, same day: each armor/weapon/tool material has its own LEVEL RANGE, and the ranges OVERLAP like Wynncraft (leather 1-18, chain
  from ~15, gold from ~20). Crafting above a material's cap makes it AT the cap (a level 80 player crafting a copper pickaxe gets the
  copper cap, ~22, because iron starts ~20). Same level = about the same stats across materials (Lv 22 copper ~ Lv 20 iron), except the
  better material starts with a little more of its own base stat (iron: a bit more Mining Fortune). TOOLS become reforgeable too.
  [spec WRITTEN: research/Gear-Levels-Wynn-Spec.md]
  ANSWERED 2026-10-01 (Skyy, all four recommended): (1) FLATTEN the class skill XP curve so every gear tier is reachable (skill 20 in
  hours of play, 40 in days; editable); (2) keep the table with a +3 overlap: Wood 1-13, Copper 10-18 (copper ARMOR 1-18), Iron 15-23,
  Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril 40-49; (3) vanilla materials cover 1-49, our own tiers fill 50-100 later;
  (4) ADD simple Workbench recipes for wands, spellbooks and staffs by material now, so 'crafted at your level' works for every class.
  [waits for the weekly usage reset 2026-10-06: SkyySkills curve + SkyyGear 0.2 stages 0-3 + the magic weapon recipes]
- LOCKED 2026-10-01 (Skyy): ALL weapons and armor found in world chests start unidentified - also prebuilt-structure chests (no loot table) and
  SkyyExploration's chest-luck extras (0.1.2 only tagged loot-table chests). Player storage (own chests, vault, AH, trade, bags) never touched.
  LIVE 2026-10-01 (SkyyGear 0.1.3). Also new: 59 level rows for non-metal gear, all editable in Server Setup -> Gear -> Levels. Picked for you:
  Stone, Trork, Fishbone, Bone, Wool, Leather_Soft and plain staffs/wands (Root, Bamboo, Cane, Onion, Stoneskin) 5; Linen, Scrap, rusty
  Steel, Leaf, Kweebec, Cutlass, special shortbows 10; Cotton, Leather_Medium, Tribal 15; Silk, Leather_Heavy, Steel, Zombie, Katana, Kunai,
  Grimoire 20; Doomed, Void, Frost, Flame, Praetorian 25; Cindercloth, Ancient, Crystal, frost staff/spellbook 30; Scarab, Spectral,
  Silversteel, Demon 35; Crystal_Flame / Crystal_Ice 40; Prisma 45 (Hytale's top set, above Mithril). Change any you don't like. [as listed]
- DECIDED 2026-10-01 (Skyy): keep the Zone 1 Temple discovery reward (+1,000 Exploration XP, ~4 levels for a new profile at the hub) "for now".
- LOCKED 2026-10-01 (Skyy): the Warrior kit gets a Wood Shield (Weapon_Shield_Wood) next to the Crude Sword - into the off-hand slot when free.
  [SkyyClasses 0.1.10 - queued; it also takes the Priest self-heal 100% default + clearer label below]
- NOTE 2026-10-01 (Skyy): "Priest heals self" should default to 100% (the Priest heals itself as much as each party member). The placeholder heal
  is temporary, so DON'T spend a build on it - change the default only if SkyyClasses is rebuilt for another reason (also rename the row
  "Priest self-heal (% of what one party member gets)"). Skyy sets 100 in Server Setup meanwhile.
- LOCKED 2026-10-01 (Skyy): the guild member list shows each member's overall bank contribution = deposits minus withdrawals (can be negative,
  e.g. +100,000 - 25,000 = 75,000; +2,000 - 5,000 = -3,000). Sort: first by guild rank (Leader/owner top, then Admins, then Members), then by
  contribution, highest first - so the biggest donors and the biggest takers are visible in each rank. [SkyyGuilds 0.1.5, with the % refunds]
- LOCKED 2026-10-01 (Skyy): guild disband pays the bank back fairly, BY PERCENTAGE ("use %") - each member still in the guild gets the share of the
  whole bank equal to their share of everything the current members put in (their deposits minus withdrawals, from the bank log), so interest and
  rewards are shared the same way. Members with nothing put in get nothing; if nobody put anything in, the bank is split evenly. Same when the last
  member leaves. Was: everything to the Leader. [SkyyGuilds 0.1.5 - queued]
- LOCKED 2026-10-01 (Skyy): Server Setup shows every time setting in SECONDS, not milliseconds, and accepts decimals like 0.24 (files keep
  their old units, the menu converts). [SkyyMenu 0.3.4 - queued with the per-profile menu item]
- LIVE 2026-10-01 (SkyyGuilds 0.1.5): % disband refunds + Contribution column as decided above.
- LOCKED 2026-10-01 (Skyy): a member who LEAVES (or is kicked) gets part of their contribution back - "some of it but not all. like 30%-40%
  of what they donated" -> 35% of their positive net contribution (deposits - withdrawals), editable in Server Setup; the rest stays in
  the bank. [LIVE 2026-10-01, SkyyGuilds 0.1.6 - the rest of a leaver's contribution becomes the guild's, so rejoining starts at 0]
- LIVE 2026-10-01 (SkyyMenu 0.3.4; Server Setup now shows the 24 ms settings in seconds too): every profile gets the SkyWynn Menu item the first time it is used (today: once per player, so new profiles have none -
  /skymenu gives it back). [SkyyMenu 0.3.4]
- LOCKED 2026-10-01 (Skyy): profiles can be deleted - confirm question, then a 6-hour undo window (Restore button, frees the slot at once);
  never the active or the last profile; after 6 h the files go to an admin-only archive (not wiped). Restore works even over the limit. [SkyyProfiles 0.1.5]
  LIVE 2026-10-01. Review change: a restore may not push you past max(limit, how many profiles you had before that delete) - otherwise delete,
  create, restore made unlimited profiles. A lowered limit still lets every deleted profile come back.
- LOCKED 2026-10-01 (Skyy): yes, block it - "a player can always leave an island and make their own. so only the owner of an island can delete
  it." While the OWNER's profile is deleted (undo window) the island is closed to co-op members (anyone on it is sent away); a restore opens
  it again; once the profile is archived the members are released so they can make their own island. A member deleting their own profile
  never affects the island. [LIVE 2026-10-01, SkyyIslands 0.5.5]
- DECIDED 2026-10-01 (Skyy): starter coins, class kit and island starter chest stay ONCE PER PROFILE (no change).
- DECIDED 2026-10-01 (Skyy): the profile undo window stays in HOURS ("considering the amount of play time that could be lost"; Wynncraft
  uses a few days - Server Setup allows up to 168 h = 7 days). [default 6 h]
- LOCKED 2026-10-01 (Skyy): Campfire cooking (in /crafting) pays half the Cooking XP it did - "Campfire XP share" 0.5 -> 0.25.
  [SkyyCooking 0.1.3 + SkyySacks 0.7.9]
- LOCKED 2026-10-01 (Skyy): class skills level too slowly - new "Class skill XP multiplier" in Server Setup, default x3, on every XP gain into the
  class weapon skill (kills, party share, Priest heals). [SkyySkills 0.4.10]
- LOCKED 2026-10-01 (Skyy): Stamina accessory line - double the max Stamina (+3/+6/+9/+12), half the Stamina Regen (+2.5/+5/+7.5/+10%).
  [SkyyAccessories 0.5.1]
- LOCKED 2026-09-30 (Skyy): booster accessories (research/Booster-Accessories-Spec.md). No separate tier words - "they are all accessories.
  but they come in the same rarity tiers as weapons and armor"; a booster line UPGRADES through Normal -> Unique -> Rare -> Legendary and stops at
  Legendary; Fabled and Mythic accessories are rare finds / drops that cannot be crafted or upgraded (a few special ones, later). Bag: 18 slots to
  start, up to 60. The 25 current talismans fold into the new lines with the new numbers (Health/Stamina/Mana stronger, Regeneration weaker).
  "+stamina" = max Stamina AND Stamina Regen (this lifts the earlier "Stamina Regen armor-only" rule for accessories). How they are obtained and
  upgraded: later (mob drops, loot chests); admin give command for now. [SkyyAccessories 0.5]
- LOCKED 2026-09-30 (Skyy): new SkyyGear modifier "Charged Attack Damage" on weapons AND armor. Bows: only when the arrow GLOWS (held a few
  seconds - partial draws never count); crossbows: the 3rd bolt in a row (Hytale's charged hit) counts; spells (staff/wand/spellbook orbs): yes but
  reduced - a roll that gives +100% to a charged melee/bow hit gives only +15% to a spell; clubs: left alone (no charged attack, never rolls).
  Research: research/Charged-Attack-Research.md. [SkyyGear 0.1.2]
- QUESTION 2026-09-30: Mana Regen perks (research/Mana-Cost-And-Regen-Research.md) - vanilla Mana refills 5/s out of combat and NOT AT ALL for
  6 s after you take damage, so a %-of-vanilla perk does nothing in a fight. Recommended: every Mana Regen perk = flat "+N Mana every 5 s", works in
  and out of combat, one total cap (placeholders: gear roll up to +1.5/piece, booster line +0.5/+1/+1.5/+2, magic tree node +0.5/rank, cap 12).
  Also: the staff now needs 10 Mana to cast - Crystal Red/Ice staffs spend 0 but still need 10 present. OK? [recommended defaults]
- Mage + Priest start at 30 Mana and every spell's Mana cost is divided by 5 (wand 5, staff 10, spellbook 20) so a level-1 caster gets a few
  casts (Skyy 2026-09-30: "make priest start at like 30 mana" + "take your recommendation 1"). [SkyySkills 0.4.8]
- Profile cap default = number of classes you can pick (5 now, grows with Assassin/Shaman); more profiles later through ranks (Skyy 2026-09-30).
  [SkyyProfiles 0.1.4]
- SkyyGear "Item level with full modifier power" 50 -> 40 so the top material (Mithril/Onyxium 40) rolls at full power; raise it again when our own
  higher-level gear exists. [SkyyGear 0.1.1, default picked - change any time in Server Setup]
- LOCKED 2026-09-30 (Skyy): cooked food stays out of the Farming bag ("id keep cooked food out"). Farming keeps raw produce (plants, crops,
  fish, raw meat, eggs); cooked / prepared food (bread, pies, kebabs, salads, grilled fish, cooked meat, Skyy cooking dishes) stays in your
  inventory. Server Setup switch, default off; cooked food already stored can still be taken out. [SkyySacks 0.7.8]
- LOCKED 2026-09-30 (Skyy): "if its not in the game yet, dont leave it in the reforge list" - coming-later stats (Ferocity, Weaken Enemy,
  Thorns, ...) never roll: Server Setup -> Gear -> Stats "Roll coming-later stats" default OFF (was ON). Gear that already has one keeps it until
  its next reforge. [SkyyGear 0.1.1]
- LOCKED 2026-09-30 (Skyy): SkyyGear level by material = Crude 0, Wood 0, Copper 10, Bronze 15, Iron 15, Thorium 20, Cobalt 25,
  Adamantite 35, Mithril 40, Onyxium 40 (bronze is hard to get in vanilla; our own gear fills the gaps later). The level is checked against
  your class weapon skill (Archery, Swordsmanship, Sorcery, Fury, Divinity). Editable in Server Setup -> Gear -> Levels. [SkyyGear 0.1.1]
- SkyyGear stacking gear (17 spears, 5 spellbooks): stacks stay whole until you Identify / Reforge / craft; then one item comes off
  (5 free slots kept, never into the hotbar). A fresh loot chest splits its stacks into single rolled items. [as built]
- SkyyGear new stats Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus are listed as "coming later" (weight 2, weapons + armor). [later]
- SkyyRanks placeholders: Admin = kick + /modconfig + party/essentials staff bypass (no ban/unban); Developer = Admin's; Owner = rank editor.
  Only a real op may grant `*`, `skyyranks.*`, `hytale.*` or `hytale.permissionsmodule.*` (covers /op, /perm) - Owner included. [as listed]
- SkyyRanks: a rank below the default rank (Member) can't have grants or be staff, and the default rank can't be staff. [on]

## Vanilla UI look (kit tools/skyyui.py, 2026-09-29) - defaults picked, change any
- Text size: "readable" - vanilla's 11-14 px lines are shown at 14-18 px (vanilla list text tops out at 14). Exact vanilla sizes are one switch. [readable]
- Leaving a page: Esc + a footer Close button (Secondary, cancel sound) like vanilla pages; the corner X is optional (vanilla hides it). [footer Close]
- Result lines: vanilla green for done, vanilla red for refused, info blue #7caacc for notes (vanilla BarterPage); gold stays for highlights. [blue notes]
- Tabs: like vanilla's spawn page - the active tab is a Primary button (blue in game), the others Secondary, equal widths. [vanilla tabs]
- Window: decorated frame (title bar with runes + gold ornaments) for forms and dialogs, the plain frame for long list pages - both are vanilla. [both]
- Mythic on pages stays #CC66CC (your lock); HUD widgets get vanilla's #000000(0.2) background when the HUD is restyled. [as listed]
- Not possible inline: vanilla's full-screen dim and bottom-left Back button (a page's root may only have a width and height).
- Seen in game 2026-09-30 (/skyprobe): dropdowns, tooltips, progress bars, item slots with rarity backgrounds, search boxes, tiles,
  text gradients, stretching layouts all WORK; checkboxes half-work; rarity FRAMES and empty-slot backgrounds do not. Text box look
  (3 candidates on probe page 2): not picked yet - the current look stays. [current look]

## Vault arrows (`research/Vault-Arrows-Spec.md`, live in SkyyVault 0.1.2)
- QUESTION 2026-09-30: the vanilla chest never tells the server when you LIFT an item (research/Vault-Arrow-Click-Research.md), so an in-chest
  arrow can only turn the page on put-back, shift-click or the Drop key (SkyyVault 0.1.5). A true one-click arrow is possible only if the arrow row
  is drawn on our own vanilla-look page next to the vault slots (not a second page-switch screen - the arrows stay in the vault window). OK to try
  that (needs one probe first)? [not built]
- APPROVED 2026-09-25 (Skyy): cycle pages inside the vault GUI with the existing in-chest Prev/Next arrows. Do not add a second page-switch UI.
- The arrows sit in an extra 5th row, so all 36 slots stay free. If the 5-row chest doesn't fit your screen, switch Server Setup -> Vault ->
  arrow layout to "Inside the page" (the arrows then take the bottom-left and bottom-right slots, Wynncraft-exact). [extra row]
- LOCKED 2026-09-25 (Skyy): buying a page does not use two clicks within 10 s. Server Setup coin threshold `buyConfirmCoins`, default
  50,000. A price below that buys at once. A price at or above it asks "Buy page X for Y coins?" in a confirm dialog. The gold arrow,
  the page Buy button, and `/vault buy` share that rule. [SkyyVault 0.1.2 still uses the 10 s second click; the next Vault build reads
  the row]
- LOCKED 2026-09-25 (Skyy): a plain click turns the vault page immediately, the same as shift-click. Both turn the page at once.
  [the "plain click only lifts; the page turns on put-down" note is not the UX. 0.1.2 turns the page when the server hears the click]

## Berserker, Priest, class kits (`research/Classes-Berserker-Priest-Spec.md` section 8, live in Classes 0.1.6 / Skills 0.4.4 / Profiles 0.1.2)
- LOCKED 2026-09-25 (Skyy), TEMPORARY until healing spells exist: Priest heal stays 25% of the damage to party members within 16 blocks,
  self-heal 50% of that, cap 10 HP per hit and 10 HP/s per player, party only. [current numbers; replace when spells are built]
- LOCKED 2026-09-25 (Skyy): Divinity XP from healing others stays 0.2 XP per HP. Healing yourself pays 0.25 XP per HP (was 0). Max 300 XP
  a minute unchanged. [0.4.5 still pays nothing for a self-heal; the next Skills build pays 0.25]
- LOCKED 2026-09-25 (Skyy): heal chat lines stay on by default, and players can still turn theirs off. At most one line every 10 s (was
  5 s). [new-file `priestHeal.feedbackMs=10000`; a file already on 5000 keeps 5 s until that line is edited]
- ANSWERED 2026-09-25: base Mana 10, Mage/Priest 20, plus Overall Level Health/Mana. Was: **Mana:** vanilla max Mana is 0, so wand casts (25 Mana), spellbook casts (100) and the Mage staff summon (50) never work for a new
  character - only the swings. Give Priests / Mages base Mana? [not yet]
- ANSWERED 2026-09-25: wait for custom weapons. Was: **Priest weapons:** no wand or spellbook can be crafted and almost none drop - the kit's Wood Wand (never breaks) is the only way to get
  one. Add recipes/drops now or wait for custom Priest weapons? [wait]
- LOCKED 2026-09-25 (Skyy): the vanilla Healing Totem (AoE +5 HP/s, endgame recipe) is Priest only (was anyone). [0.1.6 still leaves every
  deployable unassigned, so anyone can throw it until the next Classes build]
- LOCKED 2026-09-25 (Skyy): Root wands, Stoneskin wands, and the Rekindle Embers spellbook count as Priest weapons. Confirms the existing
  yes. No behavior change (they already match the wand and spellbook prefixes).
- LOCKED 2026-09-25 (Skyy): the class kit drops straight into the hotbar immediately when a player selects or changes class. Replaces
  "into storage, about 31 s after a new profile arrives." Overflow that does not fit still waits on `/class kit`. Archer kit stays 64
  arrows. An admin `/profileadmin setclass` still does not hand out a kit by itself. [0.1.6 still uses storage and the 31 s wait]
- LOCKED 2026-09-25 (Skyy), to build: a daily arrow refill for Archer. Arrows only, claimable once per day, so Archers do not have to
  craft every arrow. Not in 0.1.6.

## Swing speed (`research/Swing-Speed-Spec.md`, live in SkyyTrees 0.2.3)
- LOCKED 2026-09-25 (Skyy): Mining Speed max is +40% faster pickaxe swings (was +25%). If 40% is still too slow, vanilla swing timing may
  need adjusting. [new-file `Mining.MSpeed.per=0.016`; a file already on 0.01 keeps +25% until that line is set to 0.016]
- LOCKED 2026-09-25 (Skyy): Chopping Speed II stays renamed Heavy Hatchet. HARD RULE: hatchet swing-speed bonuses apply only to
  tree-breaking and wood-chopping. They must not change weapon-axe combat speed for Berserker or any combat class. Weapon axes get their
  own combat swing-speed stat, untouched by Chopping Speed or Heavy Hatchet. [0.2.3 still speeds every hatchet swing, including hits on
  mobs, and has no combat swing-speed stat yet. Weapon axes are already on other roots, so Chopping Speed does not touch them today]
- LOCKED 2026-09-25 (Skyy): Heavy Pick applies to ore and rock (+40% breaking power at max). Was ore only.
- LOCKED 2026-09-25 (Skyy): Heavy Hatchet max is +100% wood breaking power, so a top hatchet (0.5 power) cuts a log in one hit. Was no,
  keep +40%. [new-file `Foraging.FSpeed2.per=0.05`; a file already on 0.02 keeps +40% until that line is set to 0.05. Chopping Speed
  swing stays +25%. This still must not change weapon-axe combat speed]
- Faster pickaxe hits on mobs stay accepted. Hatchet swings on mobs do not: see the Heavy Hatchet hard rule above. [pickaxe yes; hatchet no]
- A Farming sickle speed node later? Accessories/gear adding swing speed later? [not now]
- LOCKED 2026-09-25 (Skyy): one-time chat notice about the swing-speed change, plus a free respec. The default was already yes.

## Crossbows stay loaded (`research/Crossbow-Loaded-Spec.md`, SkyySkills 0.4.5 - building after round 6)
- LOCKED 2026-09-25 (Skyy): Archery level 5, Archer class only, crossbows only (not shortbows). [already the live defaults]
- LOCKED 2026-09-25 (Skyy): loaded bolts survive teleports. Was: drop the load and reload once after a teleport. [0.4.5 still wipes on a world change; the next Skills build keeps the load. Relog, death, and profile switch still drop it]
- LOCKED 2026-09-25 (Skyy): keep the big-arrow ability meter across a slot switch. Was no. [0.4.5 still resets it]
- LOCKED 2026-09-25 (Skyy): a sound and a chat hint when the bolts go back in. Was no. [0.4.5 stays quiet]
- LOCKED 2026-09-25 (Skyy): `/settings` switches so a player can turn the meter, the sound, and the chat hint off individually. Was no. [0.4.5 has no player switches]
- APPROVED 2026-09-25 (Skyy), to build: Archery level 15+ upgrades that raise a crossbow's max bolt capacity, up to +4 extra bolts. Not in 0.4.5.
- APPROVED 2026-09-25 (Skyy), to build, late-game only: near the top of the Archer tree, a holstered crossbow reloads itself in about 30 s while you use another weapon. Not an early or mid-tier node. Not in 0.4.5.

## Auction House (`research/Auction-House-Spec.md` section 12)
1. LOCKED 2026-09-25 (Skyy): Hypixel fee defaults stay. Listing 1% / 2% / 2.5%. Duration fees on 1h / 6h / 12h / 24h stay 20 / 45 / 100 / 350. 1% tax above 1,000,000. All of those fee values are adjustable in Server Setup (SkyyEconomy rows `ah.listingFee`, the fee half of `ah.durations`, `ah.claimTaxPercent`, `ah.claimTaxFrom`). [SkyyAuctions 0.1.1 still uses config.properties; the menu rows are the next economy build. 48h is question 2]
2. LOCKED 2026-09-25 (Skyy): durations stay 1h / 6h / 12h / 24h / 48h, default 24h. The 48h option costs double the normal listing fee. [0.1.1 still adds a flat 1,200 coins on 48h]
3. LOCKED 2026-09-25 (Skyy): Bazaar items stay refused on the AH. [refused, already the default]
4. LOCKED 2026-09-25 (Skyy): a different profile may buy your listing. The same profile may not. Was: never, even from another profile. [0.1.1 still refuses the other profile unless sameAccountBuy=true]
5. LOCKED 2026-09-25 (Skyy): Creative players browse and claim only. [yes, already the default]
6. LOCKED 2026-09-25 (Skyy): 14 listings per profile stays the default cap. Progression rewards or rank perks can raise it in game later. [14; 0.1.1 has no perk raise yet]
7. LOCKED 2026-09-25 (Skyy): a second click for buys of 10,000 coins or more. [10,000, already the default]
8. LOCKED 2026-09-25 (Skyy): cancelling keeps the fee (Hypixel). [kept, already the default]
9. LOCKED 2026-09-25 (Skyy): `/ah sell <price>` opens the pre-filled page for one click. [page, already the default]
10. LOCKED 2026-09-25 (Skyy): new listings wait 20 s before anyone can buy. [20 s, already the default]
11. LOCKED 2026-09-25 (Skyy): `/ah` works anywhere. [anywhere, already the default]
12. LOCKED 2026-09-25 (Skyy): late-game items that leave both markets. The list stays empty until Skyy names the items. [none yet - the list is ready and empty]
13. LOCKED 2026-09-25 (Skyy): bid auctions are parked for later. No rules yet. [later]
14. Claims of a deleted profile? [kept; admin can regrant]
15. LOCKED 2026-09-25 (Skyy): Magic Bags and the Accessory Bag are blocked on the AH. They cannot be listed or bought. Was: tradeable. [0.1.1 still allows them until blocked.txt has Skyy_Sack_* and Skyy_Accessory_Bag]
16. LOCKED 2026-09-25 (Skyy): ask before Claim all puts 100,000+ coins in the purse. [yes, already the default]

## /trade (`research/Trade-Spec.md` section 20)
1. LOCKED 2026-09-25 (Skyy): the 3 s countdown after both click Ready is the confirm. There is no extra click. [yes, already the default]
2. LOCKED 2026-09-25 (Skyy): max coins per trade is a flat server number. 0 means no cap. [flat, 0 = no cap, already the default]
3. LOCKED 2026-09-25 (Skyy): taking damage does not cancel the trade. Trades survive hits. [no; 0.1.4 still defaults tradeCancelOnDamage to true]
4. LOCKED 2026-09-25 (Skyy): 16 slots per side (a 4x4 grid). [16, already the default]
5. LOCKED 2026-09-25 (Skyy): trades stay private. There is no chat line to party or guild. [private, already the default]

## Islands (`research/Island-Settings-Spec.md`, live in SkyyIslands 0.5.1)
- LOCKED 2026-09-25 (Skyy): co-op size 5 including the owner. [5, already the default]
- LOCKED 2026-09-25 (Skyy): Island Admins may invite co-op members. Was: only the Owner. [yes; 0.5.2 still defaults coop.adminsInvite to false]
- LOCKED 2026-09-25 (Skyy): Admins may expel, ban and untrust visitors and helpers. Only the Owner kicks co-op members. [as written, already the default]
- LOCKED 2026-09-25 (Skyy): Trusted cannot harvest crops or open chests. Beds are in the visitor set. Crafting stations stay at trusted. [crops and chests stay member]
- LOCKED 2026-09-25 (Skyy): no visits to your own old island while you are in someone's co-op. [no, already the default]
- Old "build rights" invites became Trusted, not members. [done]
- LOCKED 2026-09-25 (Skyy): `/island reset` cooldown 24 h with 3 confirms. [24 h, already the default]
- LOCKED 2026-09-25 (Skyy): visitor limit 10. Was: 5. [10; 0.5.2 still writes defaults.visit.limit=5]
- LOCKED 2026-09-25 (Skyy): biome change is free. Unlocks tied to exploration come later. [free, already the default]
- LOCKED 2026-09-25 (Skyy): visitors may use doors, seats, and beds. Chests and crafting stations stay closed to visitors. Was, briefly: chests and crafting stations open. [beds visitor; chests member; crafting trusted; 0.5.2 still writes beds=member]

## In-game server setup (`research/Server-Setup-Spec.md` section 9)
1. LOCKED 2026-09-25 (Skyy): who sees Server Setup is ops only. The node skyymenu.modconfig can be given to staff. [ops only, already the default]
2. LOCKED 2026-09-25 (Skyy): which changes ask for a confirm are money, penalties, rates, caps, curves, switching a part off, imports, restores, undos. [already the default]
3. LOCKED 2026-09-25 (Skyy): old config file versions kept is 10. Was: 20. [10; skyycfg still defaults KEEP=20]
4. LOCKED 2026-09-25 (Skyy): when a part is off, players can still take out what is theirs (bank withdraw, auction claims). [yes, already the default]
5. LOCKED 2026-09-25 (Skyy): bank interest for the time the bank was off is paid. Players receive back-pay for interest accrued while the bank was switched off. Was: no back-pay. [yes]
6. LOCKED 2026-09-25 (Skyy): NPC shops have buy and sell-back per item, infinite stock by default, and optional limited stock with a restock timer. [yes, infinite stock stays the default]
7. LOCKED 2026-09-25 (Skyy): NPC shops are in SkyyEconomy 0.2. [0.2, already the default]
8. LOCKED 2026-09-25 (Skyy): ranks are in their own mod, SkyyRanks. 0.1 is live. [yes, already the default]
9. LOCKED 2026-09-25 (Skyy): seeded ranks are Member, Admin, and Developer. Admin and Developer are close to the owner and do not get full op. Was: Developer got the rank editor. The rank editing UI is for ops and players with the Owner rank. Was: ops only. Admin and Developer cannot edit rank permissions or create or modify ranks. skyymenu.modconfig does not open it. Ranks stay fully editable in that UI. Was: only Member. [Member, Admin, Developer; 0.1 still seeds only Member; 0.1 still opens /rankadmin for anyone with skyyranks.admin; 0.1 still refuses grants, delete, and ladder moves on the default rank]
10. LOCKED 2026-09-25 (Skyy): chat order is `[Rank] [Title] Name`. [yes, already the default]
11. LOCKED 2026-09-25 (Skyy): Player Settings and Server Setup are two menu versions, done as 0.2 + 0.3. [two, already the default]
12. LOCKED 2026-09-25 (Skyy): island template box default stays 3 x 3 chunks, y 96-191. Future, to build: players upgrade 3 x 3, then 4 x 4, 5 x 5, 6 x 6, 7 x 7, 8 x 8, up to 9 x 9. [3 x 3 default; max 9 x 9 later]
13. LOCKED 2026-09-25 (Skyy): SkyyClasses' class-switch settings are greyed out while switching is locked. Players can see the option and cannot use it. Was: hidden, with one read-only line. Future, to build: class changes unlock later through a special item earned from a quest, or a similar progression gate. [greyed out; 0.1.6 still leaves switchCost and cooldownMinutes off the page]
14. LOCKED 2026-09-25 (Skyy): quest hooks ship with SkyyQuests, not now. [with SkyyQuests, already the default]
15. Rank perks later (extra vault pages, bigger parties)? [later]
16. CONFIRMED intentionally open 2026-09-25 (Skyy): how a player raises the profile cap above 6 is left open. Likely linked to ranks, and undecided. Not a resolved mechanic. [parked; no way above 6 yet]
17. SkyyRanks before the other mods' settings pages? [done]
18. LOCKED 2026-09-25 (Skyy): the warps page does not move the world spawn. Was: yes, with a confirm. World spawn movement is an owner/ops-only command, for example /setspawn. [command, not the warps page]

## Server Setup pages (round 4, live)
- LOCKED 2026-09-25 (Skyy): changing the Furnace / Tannery caps does not ask for a confirm. They stay quick to tweak. [no confirm, already the default]
- LOCKED 2026-09-25 (Skyy): the party members switch does not hide "X kicked Y" and "X invited Y". Those lines are always shown. [no, already the default]
- LOCKED 2026-09-25 (Skyy): SkyyGuilds `onlineMessages` treats off, no, and 0 as OFF, the same as every other on/off setting. That stays. [yes, already the default]
- Profiles: the default cap is now 6 (your 2026-09-24 decision); lowering it never deletes a profile.

## Player Settings (`research/Settings-Spec.md` section 6)
- LOCKED 2026-09-25 (Skyy): the Settings icon sits next to the Mods button (slot 39, left of Mods at 40). Was: slot 51, the bottom row. [next to Mods; SkyyMenu 0.3.2 still uses slot 51]
- LOCKED 2026-09-25 (Skyy): the always-on list stays as written in Settings-Spec section 2.3. [keep as-is]
- LOCKED 2026-09-25 (Skyy), to be built: settings visibility is permission-based. A player sees only the settings they have permission to change. A basic player does not see admin-only or restricted settings. Those rows are hidden, with no greyed-out or disabled entry. [hidden; SkyyMenu 0.3.2 still shows every row]

## Known limits you should know about (not questions)
- A hard server crash within about a second of an auction listing, vault move or trade can leave an item in two places (the forced save
  shortens the window; admins can repair lost claims). It is the same for every mod that stores items.
- Permission nodes of Skyy commands contain the mod version (e.g. `skyy.0.5.1_skyyislands.command.island`), so a `/rank grant` or `deny`
  of one stops applying after that mod updates. Stable names are planned (Server-Setup-Spec 8.4.6).
- A player literally named accept / deny / cancel / claim can't be targeted with `/trade <name>`.
- `/r` (reply), `/hub` (SkyyIslands) and `/p` (party) take over vanilla shortcuts (/redo, CreativeHub's /hub, /prefab's alias) on purpose.
