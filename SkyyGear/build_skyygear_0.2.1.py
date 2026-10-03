"""SkyyGear 0.2.1 - build script (javassist via jpype). NEW mod: rarity, level and modifiers on every weapon and armor piece.
Spec: research/SkyyGear-Stage1-Spec.md (the spec wins over this script; section numbers below point into it). Design docs (read only):
SkyyGear-Plan.md, SkyyGear-Stat-Catalog.md. SkyyGear REPLACES SkyyRolls (same /reforge command; deploy: SkyyRolls goes into
tools/deploy_set.py RETIRED - main-session work, spec 8.3).
Run:   python SkyyGear/build_skyygear_0.2.1.py          -> SkyyGear/SkyyGear-0.2.1.jar (never pass --deploy from a builder agent)

0.2.1 STAGES 2 + 3 (2026-10-02; a direct copy of the FINISHED build_skyygear_0.2.py - SkyyGear has no patch scripts - with ONLY these
changes). Spec: research/Gear-Levels-Wynn-Spec.md sections 3.1-3.5 (stage 2 weapon damage, stage 3 armor), 7 (tooltip), 9 (rows), 10
(stages), R2 / R10. Why now: SkyyGear 0.2 (stage 1) is LIVE and Skyy tested it - a crafted Wooden Earth Wand shows "Lv 6 - Requires
Divinity 6" but "Damage: 6-8", the same as the Lv 1 kit wand. Skyy: "new weapon level, same stats" -> the level now sets the stats.
  (1) STAGE 2 - WEAPON BASE DAMAGE BY LEVEL (spec 3.1-3.3 + 3.5). Every weapon hit of a PLAYER gets m = K x F(level) x material bonus on
  the engine's own amount, as a NEW FIRST STEP of the weapon branch with its own switch part.base (+ base.mode shape | off), never inside
  part.stats (spec 3.5 item 2); then the 0.2 chain runs unchanged on the levelled amount (Damage % -> Strength / Magical Power -> Charged
  Attack Damage -> crit, GearHit.hitAmount). The weapon branch moved byte for byte from GearHitSys into the static GearHit.weaponHit(Damage,
  UUID, PlayerRef, weapon, shot, records, armor) so the harness executes it on real engine Damage objects; GearHitSys still resolves the
  attacker / weapon / armor container and still runs the 0.2 gate first (an under-level or unidentified weapon deals 0 before any scaling).
  - F(L): base.curve "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0" (straight lines between level:factor points, flat outside; F(1) = 1 EXACTLY).
  - material bonus: 1 + base.matBonus % (0.3) x the band's start level (Copper +3 %, Iron +4.5 %, Mithril +12 %); DECISION: a band that
    starts at Lv 1 (Wood / Crude, copper armor) gets none, so a Lv 1 kit item keeps EXACTLY its vanilla numbers (the spec's worked table
    leaves the bonus out too; with +0.3 % the Lv 20 orb would read 59, not the table's 58).
  - K (spec 3.2): the family base item's largest basic (primary-attack) damage entry / this item's - the engine's own
    WeaponDamageDataCollector result (ItemWeapon.getBasicDamageBreakdown, what damageText shows), cached per id. Family = the id word
    after Weapon_; base = its Crude item, else Wood, else Iron (crossbow); the build bakes the vanilla table (GearDefs.FB_FAM / FB_ID: 12
    families) and other mods' families search the live item map the same way. An item that is its own family base (Kunai, spellbooks)
    deals exactly vanilla at its band start: K divides by F(start) x bonus(start) of the base (1 for every Crude / Wood base; the Iron
    crossbow - band 15 - deals exactly vanilla at Lv 15, spec 3.2). Spell projectiles (orbs, the same projectile for every wand / staff
    / spellbook) have K = 1. Unreadable damage data -> K = 1 (the plain level multiplier) + ONE warning per id; an unreadable level -> m = 1
    + one warning; a weapon with no primary damage entry (spellbooks) -> K = 1 silently.
  - projectiles: the GearShot launch record's stack (no new field; spec 3.5 item 1): a ProjectileSource by the projectile's own record
    (GearShotTrack.find), an arrow through a plain EntitySource by the shooter's live record (GearShotTrack.pick); no record = no scaling
    (the 0.1.x one-time WARN).
  - mobs: only a player attacker reaches the weapon branch (PlayerRef / a launch record made by a player), so mobs' own attacks are never
    scaled here - SkyyMobs 0.1 LevelDamage scales those in its own Filter system BEFORE the engine armor pass (the same slot as GearHitSys;
    the two act on different attackers, and GearArmorSys's ratio correction keeps a factor applied in between: either order gives the same
    result with vanilla's multiplier-only armor - harness AC6 runs both real systems in both orders).
  - SPEC R10 (noted, not fixed): with one curve, Axe / Longsword / Club metal items fall under vanilla from about Lv 20-25 (x0.12 - x0.65
    at their band starts); per-family curves (base.curve.<Family>) come later. Odd items with a far-off largest entry: Void scythe x0.23,
    the four prototype bows (Bomb / Combat / Pull / Ricochet) x5.49, Bronze daggers x2.43, Onyxium spear x2.24 at their band starts (the
    harness prints them) - spec 9's base.item.<id> (a per-item multiplier, NOT built here) is the lever for those.
  (2) STAGE 3 - ARMOR BASE STATS BY LEVEL (spec 3.4 + 3.5 items 5-6). Per worn SkyyGear armor piece (active = identified + gate met, an
  enforced kind): Health = the slot's Lv 1 Health x F(level) x material bonus, Physical = Projectile resistance = the slot's Lv 1 % x
  R(level) (base.resCurve "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0", no material bonus); slot base = base.armor table (Head 5 / 3.6 %, Chest 9 /
  6.48 %, Legs 7 / 5.04 %, Hands 4 / 2.88 % = the vanilla Copper row); other vanilla lines (Thorium poison, Cindercloth fire, Mana) stay.
  - Health THROUGH THE EXISTING LOCK PLUMBING: GearArmor.lockSums (the want of the skyygear_lock_<stat> modifier, SIGNED since follow-up
    review 10) = the inactive pieces' natives (level.armorNative, as before) + for every ACTIVE piece (its native Health - its per-stack
    target): positive cancels part of the native, NEGATIVE makes the lock modifier ADD Health (a Lv 10 Copper chestplate: 9 - 18 = -9 ->
    +9). DECISION (vs the spec's second key skyygear_base_<Health>): one keyed modifier, so it never stacks, GearFx.plan keeps the
    engine-review-1 rule for both signs (max only goes DOWN in the 1 s tick once the engine's own Armor modifier is synced - never eats
    current Health; going up applies at once) and a rollback to 0.2 recomputes the same key without the bonus (no orphan modifier). So
    the bonus comes on equip at once and leaves within one second of unequip. GearFx.armorPass / lowerNow now ask lockSums for the whole
    want (it applies level.armorNative and base.armorOn itself).
  - Resistance in GearArmorSys: GearArmor.fix(pre, cur, ...) = cur x act / full, full = our copy of the engine formula with every piece,
    act = only the active pieces (level.armorNative) with each active piece's (per-stack - asset) Physical / Projectile multiplier added
    to the engine-built map (GearArmor.levelRes / addRes; a broken piece's delta gets the engine's own broken factor). GearHitSys keeps the
    pre-armor amount for a player victim wearing an inactive piece OR a piece whose per-stack resistance differs from its asset
    (GearArmor.hasResDelta). Needs the ordered systems (the setup WARN now says the per-stack resistance is off when they are not).
    VERIFIED bytecode: armor DamageResistance values are ResistanceModifier (FLAT -> flatModifier, every other type -> multiplierModifier;
    Assets.zip "Percent" 0.0648 = 6.48 %), not StaticModifier; ArmorResistanceModifiers has a public constructor + public fields;
    getResistanceModifiers builds a new map per call.
  (3) TOOLTIP (spec 7) + THE VANILLA-BLOCK DECISION (spec R2). Our per-stack line shows the LEVELLED numbers: "Damage at Lv 6: 10-14"
  (+ " (+12%)" with a Damage % modifier) for weapons, "Health at Lv 4: +14" + "Resistance at Lv 4: 7.3% (physical, projectile)" + the
  item's other vanilla lines for armor (GearView.levelArmorLines / otherArmorLines; ResistanceModifier read correctly). FOUND (bytecode +
  the client files, read only): the client draws its own "Damage Data - Basic: x-y" / "Health:" / "Physical Resistance:" block from the
  ITEM ASSET (ItemBase.weapon.basicDamageBreakdown, ItemBase.armor statModifiers / damageResistance - one per item id); per stack it gets
  only ItemWithAllMetadata (id, quantity, durability, max durability, quality, the metadata JSON) whose client model ClientItemMetadata =
  Adventure / CapturedEntity / ItemDisplay / Extra, and ItemDisplay = name + description. Nothing per stack can hide or change that box,
  so we WORDED our line as the real number and add one grey line under it: "(the Damage Data box below is vanilla - before levels)" /
  "(the Health / Resistance lines below are vanilla - before levels)" - only in the item tooltip itself (GearView.hints, called by
  GearView.apply), where that box really sits under our text; /gear, gear:fn:describe (AH) and the Reforge page show the levelled lines
  without it. part.base / base.mode / base.armorOn off -> the 0.2 lines. The levelled numbers are in the rendered lines, so the render
  signature (and the config epoch) re-render a stack when its level or a curve changes. /gear read prints GearBase.describe (K, F,
  bonus, m / the armor targets).
  (4) SERVER SETUP (spec 9, new category "Level stats"): part.base (general, part switch), base.mode, base.curve, base.matBonus,
  base.armorOn, base.resCurve, base.armor (table Head / Chest / Legs / Hands -> Health | Resist %, check hook GearCfg.checkArmorBase);
  every row live + danger (curves / rates / a part switch are on the LOCKED confirm list); curves checked by GearCfg.checkCurve (rising
  whole levels 0-100, factors > 0 and <= 100) and a bad hand edit falls back to the default with one WARN. Not built (spec 9 rows):
  base.spread (default 0 = no change), base.family.<Family> (the baked table), base.item.<id>, base.curve.<Family> (R10, later).
  (5) ONE-TIME UPDATE GearCfg.migrate021 (setup() right after migrate02, before load(); the migrate012 pattern): an existing
  config.properties gains the 0.2.1 block - marker LS_MARK + the six settings with their help + the base.armor comment and its four
  lines (exactly the fresh file's lines) - right after the last level.armorNative entry (else the last level.* entry, else the end; the
  end-of-file continuation trap handled by chAfter / chEnd). Keys already there (any case of the slot word) are kept + noted and never
  doubled. CfgHist.snapshot + lvSaved first ("before the 0.2.1 level stats"), atomicWrite (ISO-8859-1 bytes, CR per anchor line), one
  INFO line, no config-changes.log line (new settings start at their defaults - the 0.1.2 rule). Runs once (marker); a fresh file
  carries it. ROLLBACK to 0.2 is safe: 0.2 ignores the new lines, recomputes the lock without the Health bonus within a second, and keeps
  no per-stack state.
  REVIEW OF 0.2.1 (2026-10-02, PASS WITH FINDINGS; applied here):
  - finding 1 (an arrow / bolt could take another live weapon's multiplier: a Lv 40 staff record picked for a Lv 40 Mithril shortbow
    arrow gave x3.36 instead of x1.12, a newer Lv 13 shortbow record gave an Iron crossbow bolt x2.1): GearHitSys now asks
    GearShotTrack.pickFor(u, armor, calcOf(d)) - the hit's damage step (the DamageSequence meta, read like GearCharged.judge) keeps only
    the live records whose weapon's GearChg index knows that calculator (+ any record whose weapon was not walked completely), then the
    0.2 rule (newest / weaker) runs over them; no step, an unknown step (even after GearChg's 30 s re-walk) or fewer than two records =
    every live record (pick(u, arm) = pickFor(u, arm, null) = exactly the 0.2 rule). GearHit.weaponHit clamps a picked record's
    multiplier to GearShotTrack.minMult = the smallest GearBase.weaponMult among those candidates (the reviewer's quick fix as the
    fallback): when the step names its weapon nothing changes (Mithril arrow x1.12 with its strength, crossbow bolt exactly 10, the Lv 13
    shortbow's own arrow 25.2 - not the quick fix's 12); when it cannot (no step / unknown / the same item at two levels, which share
    calculators) no other live weapon can raise the hit. UNVERIFIED in game: that a live arrow carries the walked calculator object (the
    charged-attack index relies on the same identity); if it does not, the fallback is the clamp.
  - finding 2: a weapon whose levelled hits equal its vanilla ones (GearBase.asVanilla: m = 1 up to float noise - the Lv 1 kit items, an
    item that is its own family base at its band start) keeps 0.2's plain "Damage: 6-8" line and gets no grey hint; the same rule for
    armor (GearBase.armorAsVanilla: levelled Health + Physical / Projectile resistance = the asset's own - a Lv 1 copper piece, the
    commonest early armor) keeps 0.2's line ("Health: 9"; the vanilla lines below show its resistance) and no hint.
  - finding 3: spell weapons (staff / wand / spellbook) get "Spell at Lv 6: 43" under the damage line = every legacy projectile their
    interactions launch (GearChg's walk: Skeleton_Mage_Corruption_Orb 25, Ice_Ball 20, Fireball 60; Projectile.getDamage(), what the
    engine deals on the hit - VERIFIED bytecode ProjectileComponent.onProjectileHitEvent) x the spell multiplier (K = 1, as weaponHit);
    "Spell: 25" when the level changes nothing; part.base / base.mode off = the 0.2 lines. The hint moves under the spell line.
  - finding 4 (UNVERIFIED wrap of long tooltip lines): the armor hint is shortened to "(Health / Resistance below are vanilla - before
    levels)" (55 characters; 0.2's longest line in game was 57); the weapon hint (54) stays.
  - finding 6 (balance, a design question - safe option, NO change): Life Steal is a % of the landed damage, so it grows with the levelled
    hit (x3.4 at Lv 40) like the hit itself; it stays as built (the stat reads "Life Steal +5%"; its roll range is a Server Setup row;
    a cap would be Skyy's call). Mana Steal is a FLAT amount per steal window (GearFx.manaSteal) - levels do not change it.
  - nits: the base.armor comment in config.properties names no internal doc section; GearBase.ratio caches no FAILED read (a transient
    failure no longer fixes K = 1 for the server's lifetime; the WARN stays once); the harness runs AC6 against the SkyyMobs jar pinned in
    tools/deploy_set.py (read from the SET, not a hard-coded 0.1).
  Bare-JVM harness: SkyyGear/test_skyygear_0.2.1.py (section AC; every 0.2 section carried forward).

0.2 STAGE 1 (2026-10-02; a direct copy of the FINISHED build_skyygear_0.1.3.py - SkyyGear has no patch scripts - with ONLY these changes).
Spec: research/Gear-Levels-Wynn-Spec.md (Skyy's answers in its section 11, the review log in section 12) + OPEN-QUESTIONS.md "Q&A with
Skyy 2026-10-02" (R1: magic weapon recipes) + the LOCKED 2026-10-01 gear lines (copper armor 1-18). Spec section 10: "ship stage 1 first
and tune before stage 2" - WEAPON DAMAGE AND ARMOR STATS STAY VANILLA in this version (no base.* rows, no part.base, GearHitSys /
GearArmorSys / GearFx untouched); found gear keeps its band start (stage 4 zone levels wait for the pacing call, no loot.* rows).
  (1) EVERY NEW GEAR DOCUMENT STORES ITS OWN LEVEL (spec 1 + 4): lvl = the item's use requirement against the gate skill already ruled
  (LOCKED 2026-09-25: combat gear + Equipment = the class weapon skill; mining / foraging / farming tools = that gathering skill).
  GearRoll.newDoc(id, r, ident, src, lvl) puts lvl into the document BEFORE rollMods (spec 4 "order matters": the modifiers roll at the
  item's own level); the 0.1.3 newDoc(id, r, ident, src) stamps the band start (admin /gear give, unidDoc = mob drops + world chests +
  gear:fn:unid, the /craft bridge with another source); craftDoc stamps the crafter's level (4). reforge / identify stamp a MISSING lvl
  (the level the item reads now, so it keeps the level its modifiers rolled at) and never change one (spec 4 / 8). Existing gear is never
  rewritten for it (spec 8): the legacy stamp, the SkyyRolls migration and the passive scan write no lvl, so an unstamped item keeps
  reading the table live (now its band start: Crude / Wood read 1, Copper 10, Iron 15 ...). /gear level <n> ignores the bands and marks
  the document lvlA (clear removes both). Server Setup part.levels (part switch, default on): off = 0.1.3 - nothing new is stamped.
  (2) OVERLAPPING MATERIAL LEVEL BANDS (spec 2; Skyy: "keep the table with a +3 overlap"): level.material.<entry>=<min>,<cap> - Wood /
  Crude 1-13, Copper 10-18, Armor_Copper 1-18 (LOCKED 2026-10-01: a default row; an entry at the start of the id beats Copper), Bronze /
  Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49 (cap = the next material's start + 3; the top = 49,
  question 3: vanilla materials cover 1-49); the 59 family rows start..start+7, never above 49. A row with ONE number still works: N to
  N + level.bandWidth - 1 (default 8; never past 49 while N <= 49, never past 100 - GearCfg.capOf). Level by item stays an exact level (no
  range); Hytale's own item level / the default too. Server Setup: the table has Min | Cap columns (kit 2-column table, check hook
  GearCfg.checkBand: Cap >= Min). GearLevel.band(id) = { min, cap, kind } with the same lookup as level() (level() itself is byte-
  identical; band start == level(id, unstamped) always). Build check: the band of all 304 vanilla gear ids + 32 gathering tools (36 start
  levels change: Wood / Crude 0 -> 1, copper armor 10 -> 1).
  (3) GATE FLOOR (spec 1): a skill below level.gateFloor (1) counts as that floor in EVERY gate state (no class picked, no SkyySkills
  with level.noSkills block, an unknown skill), so a fresh Divinity 0 Priest can use the kit's Lv 1 Wood wand. "(you: N)" shows the real
  level. 0 = off.
  (4) CRAFTED AT YOUR LEVEL (spec 4, LOCKED 2026-10-01): a craft (vanilla bench: GearCraftSys -> GearCraftTask -> rollIn -> craftDoc;
  SkyySacks /craft: gear:fn:roll mode 8) makes the item at the crafter's level in the item's gate skill (weapons / armor / Equipment: the
  crafter's CLASS skill, "Combat" without SkyyClasses; tools: Mining / Foraging / Farming), raised to the gate floor and moved into the
  material band: below it = the band start + one chat line "Made at Lv 10 (the lowest level of Copper gear) - you need Divinity 10 to use
  it (you: 4)."; above it = the cap + "Copper gear caps at Lv 18 - a better material goes higher." (Skyy: a level 80 player crafting a
  Copper pickaxe gets the Copper cap). No class picked / no SkyySkills = the band start, no line. Rows: craft.levelFrom (gate | band =
  always the band start), craft.belowBand (min | block: a VANILLA BENCH craft below the band is refused by GearCraftPreSys on
  CraftRecipeEvent$Pre - CraftingManager.queueCraft / craftItem return before the job is queued / an input is taken when Pre is cancelled,
  VERIFIED bytecode and re-checked by this build; the /craft bridge cannot refuse, SkyySacks then gives the plain output, so /craft makes
  it at the band start in both modes), craft.weaponSkill (adv: optional prefix:Skill pairs, the longest prefix names the skill).
  Mode 8 computes the level once per craft (every item its own document at that level) and accepts an optional 6th element = a requested
  level, kept inside the band and never above the crafter's level (a later "craft lower" picker). The GATHERING TOOLS of TOOL_FAMILIES
  (pickaxe, shovel, hatchet, hoe, sickle) now get a document when crafted (GearRoll.craftable; spec 1 "Tools: they store and show a
  level"): Normal rarity, NO modifiers (no tool stat is live - LOCKED 2026-09-30 "coming later stats never roll"), gate shown "(coming
  later)", never enforced, never reforged (unchanged refusal); tools already owned stay plain.
  (5) REQUIREMENT UX (spec 7): the tooltip's first line under the name = "Lv N - Requires <Skill> N" - the vanilla "met" green (0.1.3's
  design review 3; grey means "coming later" in these tooltips), the vanilla red + "(you: M)" when too low; "Lv N - Requires Mining N
  (coming later)" in grey on tools; under-level armor keeps "Gives no stats until <Skill> N" right under it. gear:fn:sig includes the level
  (spec 8: the AH says "rolls differ" for a Lv 4 and a Lv 9 wand; it calls the sig live on both sides). /gear read prints where the
  level comes from + the band + what a craft by you would stamp. NEW admin /gear relevel [player] (spec 2): every STAMPED gear item in
  that player's inventory moves into today's band (below = start, above = cap); unstamped ones follow the table already, lvlA ones stay;
  Vault / AH / bags are never touched.
  (6) WAND / STAFF RECIPES THAT MATCH VANILLA WEAPONS (Q&A R1 LOCKED, see the block "0.2: wand / spellbook / staff RECIPES"): 8 standalone
  recipe assets in this jar (Server/Item/Recipes/SkyyGear/SkyyGear_Recipe_<item>.json, generated from Assets.zip at build time, never
  committed): Weapon_Wand_Wood, Weapon_Staff_Wood / Copper / Iron / Thorium / Cobalt / Adamantite / Mithril, each = the same material's
  SHORTBOW recipe unchanged (Crude for Wood): the Weapon Bench's Bow tab (tier 2 Thorium / Cobalt, 3 Adamantite / Mithril), the Workbench
  Survival tab too for Wood, the same metals / amounts / time. No spellbook exists per material and no wand but Wood (Assets.zip) -
  nothing is invented; no vanilla item or recipe file is overridden. Crafted ones get levels like any craft.
  (7) ONE-TIME UPDATE GearCfg.migrate02 (setup() right after migrate013, before load(); the established pattern): every level.material
  row whose LAST live line is a one-line entry holding EXACTLY its 0.1.3 default text (the metals' 0.1.1 values, the 59 family values,
  Armor_Copper=1 = what OPEN-QUESTIONS told Skyy to type) becomes its 0.2 band (value text only; key, separator, CR kept); any other value
  is kept + noted (a custom one number reads N to N+7); a missing Armor_Copper row is added right after the last Copper row; the marker
  BD_MARK + the six new settings the file lacks (exactly the fresh file's lines) go right after the last level.material row (the 0.1.1
  finding 4 end-of-file trap handled by chAfter / chEnd). CfgHist.snapshot + lvSaved first ("before the 0.2 level bands"), the kit's
  atomicWrite (ISO-8859-1 bytes), one config-changes.log line per band row it wrote (name "SkyyGear 0.2"; old = what the old ONE number
  means in 0.2, "N|N+7", because Server Setup's Undo sends the old value back through the 2-column table, which refuses a single cell -
  for the 59 family rows that is the same band: a text-only rewrite) + Armor_Copper with old "(none)" (Undo = remove); the new settings
  start at their defaults (no log line, the 0.1.2 rule). Runs once (marker); a fresh file carries it. KNOWN LIMIT: Undo of a PRE-0.2
  level.material change-log line (a single number, e.g. 0.1.1's "Iron 20 -> 15") is refused by the Min | Cap table ("Needs 2 values")
  - type the band instead (N|N+7); History still restores whole files.
  REVIEW OF 0.2 (2026-10-02, PASS WITH FIXES; applied here):
  - finding 1: GearRoll.craftNote / blockWhy look at the kind the new document gets (GearDefs.enforcedKind(GearData.kindFor(id))): the
    gathering tools' gate is "coming later" (never enforced), so a tool crafted below its band gets NO "you need Mining N to use it" line
    (it was false) and craft.belowBand block never refuses a tool; the cap line stays for tools (true; Skyy's level-80 copper pickaxe).
  - finding 3: the craft note is sent once per crafting burst - GearRoll.noteDue: only when that player got no note for that item in the
    last 10 s (each noted craft refreshes the time), on both craft paths (a timed bench queue fires one Post per unit: 10 staffs = 1 line).
  - finding 4: GearView.apply - a PLAIN gathering tool document (isTool && !isGear: Normal, no modifiers) keeps the item's own quality
    frame + its name in that quality's vanilla text colour (Mithril pickaxe purple, Iron green ...); a Skyy_Gear_* stack quality on a tool
    goes back to the item's own; tools made gear by gear.include keep 0.1.3's rarity quality.
  - finding 5: the recipe copies drop the bows' "Armory" entry (Bench_Armory: Quality Developer, DiagramCrafting with fixed slots per
    category); every recipe keeps the bow's real Crafting benches (asserted), nothing else changes.
  - finding 6: level.gateFloor carries danger (confirm on change) like level.bandWidth (100 = every gear item usable). Kept as they are
    (safe option): /craft cannot refuse (noted in the row help); the 0.1.1 marker / levels header text stays in a fresh file (migration
    anchors - the 0.2 marker right above the new settings explains the band format). The harness reads the live History copies with a
    fallback to the deploy backups (backups/deploy-*/data/Skyy_SkyyGear/config-history, read only) for when KEEP 10 evicts them.
  - finding 2 (ROLLBACK FLOOR, main-session work: tools/deploy_set.py + HANDOFF): SkyyGear 0.1.3 cannot read a <min>,<cap> row (its loader
    takes one number per level.material row and drops the row), so after migrate02 ran, rolling SkyyGear below 0.2 needs the History copy
    "before the 0.2 level bands" restored first (Server Setup -> History), or every band row is ignored and items fall back to Hytale's
    own item level (the kit Wood wand / staff would read about Lv 40). Items themselves are rollback-safe (0.1.3 reads lvl).
  - findings 7 / 8 (main session): Priests can craft only the Wood Wand and no spellbook exists per material (Q&A R1 names spellbooks -
    confirm with Skyy); staffs sit in the Weapon Bench's Bow tab (no staff category). Pinning 0.2 also needs SkyyMenu MODS_VERSIONS +
    menu_check updated.
  Bare-JVM harness: SkyyGear/test_skyygear_0.2.py (section AB; every 0.1.3 section carried forward).

0.1.3 (2026-10-01; a direct copy of the FINISHED build_skyygear_0.1.2.py - SkyyGear has no patch scripts - with ONLY these changes):
  (1) ALL WORLD-CHEST GEAR STARTS UNIDENTIFIED (OPEN-QUESTIONS LOCKED 2026-10-01, Skyy: "please make all weapons and armor found in
  chests start unidentified"). 0.1.2 only tagged containers that still had a loot TABLE when their block entity was added (GearChestMark
  / GearChestTag around StashPlugin$StashSystem - unchanged here), so prebuilt-structure chests whose items sit in the prefab (vanilla
  has almost none; the pack's structure mods have them: Fullmetal Labyrinth, Skyreach Ravines, EndgameAndQoL, NecromancerSpire, Tower
  of Shiva - 25+ prefab chests with weapons / armor, scanned from the Mods folder) and SkyyExploration's chest-luck extra roll stayed
  plain. NEW: the first time a player opens (or breaks) a WORLD container, every weapon / armor stack in it with NO SkyyGear document
  becomes unidentified - the 0.1.2 chest tag itself (GearTag.tagContainer: rarity from the Chest odds column, stacks split per item into
  the same chest's empty slots), so it looks exactly like a loot-table chest.
  - HOOK (HytaleServer.jar bytecode): UseBlockInteraction.doInteraction fires the cancellable ECS event UseBlockEvent$Pre on the player
    (CommandBuffer.invoke, synchronous) BEFORE it runs the block's root interaction, whose OpenContainerInteraction then builds the
    ContainerBlockWindow from ItemContainerBlock.getItemContainer() - so the tag lands before the window shows the items.
    SimpleBlockInteraction.tick0 resolves a multi-block filler to its origin first (resolveBaseBlockPosition); GearChestOpen still
    resolves a filler itself (SkyyExploration's StashCommand math) when the target has no ItemContainerBlock. GearChestOpenSys =
    UseBlockEvent$Pre (skipped when already cancelled); GearChestBreakSys = BreakBlockEvent (BlockHarvestUtils.performBlockBreak
    fires it before the block goes, so a world chest broken unopened drops tagged items - otherwise breaking would bypass the rule);
    backup: GearTick (1 s) looks at the player's open ContainerBlockWindows (a container opened by any other path) and queues the
    same decision as a world task (GearChestTask).
  - WHICH CONTAINERS: only an ItemContainerBlock reached through those three paths. SkyyVault, SkyyEssentials trade escrow,
    SkyySacks / Magic Bags, the accessory bag and SkyyAuctions are never block containers (ContainerWindow / custom pages - checked in
    the live set's build scripts), player inventories are never containers here. PLAYER STORAGE IS NEVER TOUCHED: the engine puts a
    PlacedByInteractionComponent (persisted, ChunkStore codec "PlacedByInteraction") on every block entity a player places
    (BlockPlaceUtils.tryPlaceBlock), so a container whose placer is a player of THIS server (Universe.getPlayerStorage().getPlayers()
    + online players + every PlayerReady) is player storage and stays exactly as it is. Why not trust "only documented gear can be in
    a player chest": (a) chests filled before SkyyGear existed (live since 2026-09-29) hold undocumented gear; (b) pipes / hoppers
    (HyPipes, AutoStorage), CarryChest and any mod that moves items between containers never pass a player inventory; (c) the passive
    stamp runs <= 250 ms after an inventory change, a shift-click into a chest can be faster. So the decision is by WHO PLACED the
    container, not by what is in it. A placer UUID that is NOT a player here (394 vanilla prefabs and the structure mods carry their
    builders' UUIDs - e.g. Fullmetal Labyrinth chests with gear) counts as a world container. Before the player list is read the
    first time, a container with a placer is left undecided (untouched, not remembered, decided on a later open). SkyyIslands island
    worlds (bridge island:owner:fn, or a world name starting skyy-island-) are skipped completely: the starter-kit chest is placed by
    code, has no placer and may hold admin kit gear (an unidentified starter weapon would deal 0 damage until paid for).
    LIVE WORLD CHECK (2026-10-01, the "HUD mod" region files copied to scratch and read with the engine's IndexedStorageFile): world
    default has 453 containers - 128 without a placer that hold Weapon_ / Armor_ items (old loot rolled before SkyyGear: they get
    tagged on their first open), 311 without a placer and without gear, 14 with the placer a80feddb-cc0a-3d47-b0ba-eebab755c461 (a
    vanilla prefab builder - 197 vanilla prefab blocks carry it; all 14 empty) - and none placed by a player of this server; the 5
    island containers are the SkyyIslands starter chests, no placer (why islands are skipped).
  - ONCE PER CONTAINER, remembered per world in Skyy_SkyyGear/chests/<world>_<world uuid>-<hash>.txt (append-only "x y z state ..."
    lines, read once per world, written on the scheduler like gear.log; the key is the world name + its own UUID from WorldConfig, so a
    world deleted and made again under the same name - an instance, a reset - starts fresh): W = world container, decided and tagged; P = player storage, never touched; L = a
    container that had a drop list when its block entity was added AND carries a placer (an admin's /stash set chest - GearChestMark
    notes it), not opened yet; T = such a loot container, tagged. A W container that has a player's placer now (broken + replaced by
    a player's own chest) becomes P; a P position whose container has no placer any more is decided again. A remembered container is
    never tagged a second time, whatever gets into it later.
  - SKYYEXPLORATION'S CHEST LUCK (0.2.2 ExpAward.luck, read): ONE extra ItemModule.getRandomItemDrops(droplist) roll goes into the
    OPENER'S INVENTORY (SimpleItemContainer.addOrDropItemStack: storage first, ItemUtils.dropItem -> throwItem at the feet when full),
    never into the chest, from a world task after its UseBlockEvent$Post poll sees the chest window open, on the first open per
    PROFILE. So the luck items are covered where they land, whatever order the two mods run in: every open of a world container
    (W / T / L or newly decided, never P or an island) starts a LOOT WINDOW for the opener (GearChestOpen.LOOT: until 3 s after the
    container window was last seen open - refreshed by GearTick every second while it stays open, never past 15 s after the open:
    review finding 1 below). While it lasts, undocumented gear
    that shows up in that player's inventory (GearStamp.scan, the coalesced passive stamp) or is dropped by that player
    (GearThrowSys = the full-inventory overflow) becomes unidentified with the Chest odds (stacks split per item into storage /
    backpack, the 5-slot floor kept) instead of the legacy Normal stamp. The window starts at UseBlockEvent$Pre, before SkyyExploration's
    Post handler can even queue its award, and the stamp decides when it runs, so neither mod's order matters.
  - Part switch: part.chests (existing row, help text updated) covers loot tables AND first opens. gear.log: CHEST / UNID chest /
    UNID chestloot lines. Ready line: GearChestOpen.statusText().
  (2) LEVELS FOR NON-METAL GEAR FAMILIES (Skyy: Stone Trork Daggers asked Lv 25 = Hytale's ItemLevel). 160 of the 304 vanilla weapon /
  armor ids had no word in "Level by material" and fell back to the vanilla ItemLevel (9-75). FAMILIES below gives 59 family rows
  around Skyy's metal tiers (table + reasons next to it) covering 153 of them; only the developer-only QA / Trooper / Test_Zoom items
  (7 ids, Debug / Developer quality, not obtainable) keep "Use Hytale item level otherwise". Every metal-resolved id resolves exactly
  as before (build check, also over the 574 Weapon_ / Armor_ ids of the installed mods: 0 changes; 32 modded fallback ids gain a row,
  listed by the build).
  - Entries may be several words of the id in a row (Leather_Soft, Steel_Rusty, Crystal_Flame, Shortbow_Pull): GearLevel.level tries,
    at each id word from the left, the longest entry first (up to GearCfg.MAT_WORDS = the most words any entry has, max 3); with only
    one-word entries this is exactly the 0.1.2 loop. Needed because "Leather" / "Cloth" come first in those ids, Steel_Rusty /
    Steel_Ancient must beat Steel, and generic words (Light, Heavy, Pull, Combat) must not catch other mods' items.
  - ONE-TIME UPDATE of an existing config.properties (GearCfg.migrate013, setup() right after migrate012, before the loader): adds the
    family lines the file does not have yet (an entry is "there" when any level.material.<entry> key matches it in any case, as the
    loader reads them) under the marker FM_MARK right after the last level.material entry - never changes or removes a line. Values =
    the new defaults, so this DOES change levels: History keeps the old file ("before the 0.1.3 level family rows", checked by lvSaved
    before the write), CfgRows.atomicWrite writes it, and one config-changes.log line per added row (level.material[<Entry>], old
    "(none)", new <level>, status ok, name "SkyyGear 0.1.3") lets Server Setup -> Changes undo each one (the kit's inverse = remove).
    Its own marker, run once (a row Skyy removes later is never added back); a fresh file carries the marker. The 0.1.1 / 0.1.2 updates
    are byte-for-byte unchanged.
  Bare-JVM harness: SkyyGear/test_skyygear_0.1.3.py (section AA).
  REVIEW OF 0.1.3 (2026-10-01, verdict PASS; applied, still 0.1.3, not deployed):
  - Finding 1 (the loot window went by time, and an open chest kept it alive): the window now has a HARD CAP - LOOT_CAP_MS (15 s)
    after its START. Only an open (UseBlockEvent$Pre) or a container decided just now starts it (GearChestOpen.loot); GearTick's
    window sightings and the window task only extend it (lootMore: + GRACE_MS, never past start + 15 s). SkyyExploration 0.2.2 gives
    its luck roll while the window is open, at its first OpenCheck poll that sees it (every 100 ms, gives up after 2 s) or its 1 s
    ExpTick backup, so 15 s covers it with room; gear that turns up later (a /give, another mod's reward) gets the legacy Normal
    stamp again. The cleaner fix (SkyyExploration calls the gear:fn:unid bridge on its luck stacks, then no window) is SkyyExploration
    work, not done here.
  - Finding 2 (L / T skipped the player check): an L / T record keeps the placer it was made with (GearOpened.PW, "placer=<uuid>" in
    the memory line). A container there whose placer is a DIFFERENT player of this server is player storage (P: untouched, no loot
    window); a different placer that is not a player here still counts as the loot spot; the player list unread -> undecided (-5).
  - Finding 3 (stale memory after a regenerated / replaced container): (a) a container block entity added with AddReason.SPAWN
    and no placer (a runtime setBlock / setBlockEntity: a new container, never the chest's open / close state change - that
    setBlock passes flag 2 = keep the block entity, VERIFIED bytecode) forgets a W / T / L record at its spot (GearChestOpen.spawned,
    in GearChestMark before the 0.1.2 chestMark); (b) a REGENERATED chunk: its block entities come back with AddReason.LOAD (the
    section loading system), so (a) cannot see it - GearChunkRegen copies Hytale's own TriggerVolumeChunkRegenSystem test (the
    WorldChunk entity added with SPAWN + ChunkFlag.NEWLY_GENERATED) and forgets every record in that chunk column, P included (the
    blocks there are all new). Forgetting appends an "x y z X" line (read back as "no record").
  - Finding 4 (instance worlds): a world whose WorldConfig deletes it (isDeleteOnRemove / isDeleteOnUniverseStart) keeps its
    decisions in memory only (no chests/ file, GearOpened.TEMP); RemoveWorldEvent (GearWorldBye) writes the pending lines and drops
    that world's maps.
  - Finding 5 (world-thread disk reads): known() never reads the player list itself any more - only GearKnownTask does (scheduler);
    until it has, a container with a placer stays undecided (-5), as documented. PlayerReady prefetches the world's memory file on
    the scheduler (GearOpened.prefetch), so the world thread normally finds it loaded.
  - Finding 6: the build prints old -> new level for every modded fallback id that gains a family row (old = the mod item's own
    ItemLevel through its Parent chain).
  - Finding 7 (Skyy's buckets, the reviewer's suggested defaults): Bone 15 -> 5 (Skyy: Stone / Bone / Wool / Soft leather 0-5),
    Praetorian 30 -> 25 (Hytale's own 25: no family above Hytale's level), new rows Spellbook_Frost 30 + Staff_Frost 30 (= the fire
    spellbook / crystal staffs; Frost stays 25 for the frost sword / shortbow). 59 rows; Prisma 45 and Iron_Rusty (Iron 15) unchanged
    and still Skyy's call.
  - Finding 8: an entry of more than 3 words logs one WARN at load (it can never match). Findings 9-12: no change (by design / info).

0.1.2 (2026-09-30; a direct copy of the FINISHED build_skyygear_0.1.1.py - SkyyGear has no patch scripts - with ONLY these changes):
  NEW MODIFIER "Charged Attack Damage" (key chg, %, weapons AND armor; OPEN-QUESTIONS LOCKED 2026-09-30, research/Charged-Attack-
  Research.md). Skyy's answers, verbatim where quoted: bows - "charge damage only kicks in when the arrow starts to glow"; crossbow -
  the 3rd bolt in a row (Hytale's own Charged-tagged combo bolt) counts; spells (staff / wand / spellbook orbs) - "yes, but at a reduced
  amount ... it would only add +15% to a spell" (charged.spellFactor 0.15); clubs - "Leave clubs alone" (never rolls, never counts;
  Kunai + Crystal Flame likewise; Crystal Ice excluded too: its Ice hits never reach the stat code - verifier). Skyy's lock: a stat
  that does nothing must never roll, so it rolls ONLY while charged.on is on, always on armor, and on a weapon only when the weapon
  really has a charged step the detection can see.
  - STATS row ("chg", "Charged Attack Damage", "wa", "%", 30, 5, live) right after Crit Damage (display order; saved gear stores
    modifiers by key, so nothing on existing items moves). Tooltip "Charged Attack Damage: +N%" (grey " (off on this server)" while
    charged.on is off). Server Setup: charged.on, charged.spellFactor (0.15, Skyy's number), charged.log + the stat row stats.chg=30,5.
  - DETECTION (GearChg + GearCharged; the research's three signals with the verifier's fixes):
      B = a per-item IdentityHashMap of DamageCalculator -> how it is reached, built by walking the item's own chains with the
          engine's InteractionManager.walkChain (the tooltip walk WeaponDamageDataCollector does) and a collector (GearChgWalk).
          A step is FULLY CHARGED when the Charging edge above it is that Charging step's LARGEST Next key: every melee charged
          step (Sword thrust 0.65 s, Battleaxe downstrike, Mace 2.0 s, Daggers pounce + its backstab, Axe 1.39 s, Longsword
          1.565 s, Void scythe 1.67 s) and, on bows, ONLY the 1.2 s full draw - the step that makes the arrow GLOW (Assets.zip
          evidence, checked by this build: Weapon_Shortbow_Primary_Shoot_Charge plays particle system Bow_Charging, whose own
          comment says its "delays are tuned to appear at max charge (1.2s)" - first spawner StartDelay 0.75 + the ~0.45 s built-in
          delay = 1.2 = the largest Next key -> Primary_Shoot_Strength_4, the only draw with the Impact_Dagger_Stab_Charged impact,
          knockback 8 and a headshot). Partial draws (0.1 / 0.3 / 0.6 / 0.9 s) are PARTIAL and never count, although Hytale tags
          every draw Class Charged. The headshot calculator of the glow step counts too (same step).
      A = Hytale's own Class Charged on the hit's DamageSequence - trusted ONLY for vanilla weapon ids + the pack's More Crossbow
          Tiers crossbows (verifier: a loose Class tag from another mod never counts) and only where the walk shows no partial
          levels: the crossbow's 3rd-bolt combo (reached without any hold, Class Charged).
      C = legacy projectiles (spear throws, staff / wand / spellbook orbs): GearShot.charged, set at launch when the item's walk
          launches that projectile id only from a FULL step.
      Never: Class Signature (every signature, e.g. the shortbow volley that charges 0.75 / 1.5 s), anything reached from an
      Ability1-3 root, a calculator reached both charged and uncharged (the prototype bows Bomb / Combat / Pull / Ricochet share
      one damage step over every draw - so the stat never rolls on them either), the excluded families above.
  - VERIFIER FIXES: a single spellbook / a single thrown spear is used up by the cast before the projectile exists, so the hand was
    empty when GearShotTrack recorded it (no weapon stats, no charged flag, no level gate). GearHandSys (every tick, one identity
    compare per player) keeps the last two hand stacks; GearShotTrack takes the live hand when it launches that projectile, else the
    newest snapshot (<= 1 s old) whose GEAR item launches it (GearHand.pick). Loose Class tags: see A. Crystal Ice: excluded.
    Signature hits: see Never.
  - hitAmount: one extra factor x (1 + chg / 100) (spells x (1 + charged.spellFactor x chg / 100)) after Strength / Magical Power,
    before the crit roll (a charged crit gets both); True Damage + the flat element lines are added after armor as before (never
    multiplied). The 5-argument hitAmount stays (= no charged hit).
  - ROLLS: GearRoll.pool(slot, id) - chg only while charged.on, always on armor, on a weapon only when GearChg.hasCharged(id) (the
    runtime walk; if the walk cannot run, the vanilla list this build baked from the same rules). newDoc / reforge / identify pass
    the item id (every roll path goes through them).
  - /gear charged (ADMIN, skyygear.admin + no groups): the held weapon's charged steps from the index, whether it may roll, your
    last judged hit (turns on a 10 min probe: your hits are judged even without the stat; /gear charged off ends it).
  - ONE-TIME UPDATE of an existing config.properties (GearCfg.migrate012, setup() right after migrateStat011, before the loader): adds
    the missing lines only - "# chg = ..." + stats.chg=30,5 right under stats.cd, and the marker + charged.on / spellFactor / log
    with their help right under speed.per (the fresh file's places) - so Server Setup lists the new stat row. Values are the
    built-in defaults (nothing changes in effect, so no config-changes.log line); History keeps the old file ("before the 0.1.2
    charged attack lines", checked by lvSaved before the write); its own marker, run once; an open continued entry at the end of the
    file gets the lines before it (the 0.1.1 review finding 4 trap). The 0.1.1 updates are byte-for-byte unchanged.
  Build self-check (the SkyyTrees pattern): the Python walk of this build over Assets.zip must still find every family's charged
  step, the bow glow evidence above, Club_Attack a plain Chaining, clubs / Kunai / Crystal Flame without a detectable step.
  Bare-JVM harness: SkyyGear/test_skyygear_0.1.2.py (section Z).
  REVIEW OF 0.1.2 (2026-09-30, applied):
  - Finding 1 (a partial bow draw could count): the "Class Charged, step not in the walk" fallback is MELEE only now. A projectile
    hit judged against a record GearShotTrack.pick chose (the weaker weapon when several are in the air, e.g. a spear / orb still
    flying while bow arrows land) looks its damage step up in every live record's weapon (GearShotTrack.liveIds): it counts only when
    every weapon whose walk knows the step calls it charged; a step no live weapon knows = not charged (the re-walk still runs). A
    legacy launch flag without a damage step counts only while one weapon is in the air. The projectile's own record (find) = exact.
  - Finding 2 (the Vampire bow counted without a glow): Weapon_Shortbow_Vampire is excluded (CHG_EXCL; its deprecated draw has no
    particles and its full-charge arrow looks like the partial ones - build self-check 1b). Shortbow family: 19 gear / 14 may roll.
  - Finding 3: a Light / Charged-tagged step a completely walked vanilla / pack weapon's index misses after the re-walk logs one WARN
    per weapon id (gear.log "chgmiss:<id>").
  - Finding 4: GearCharged.note builds its line only while a probe is armed or charged.log is on.
  - Finding 5: GearHand.seen ignores an empty hand turning into another empty hand (null <-> empty stack).

0.1.1 (2026-09-30; a direct copy of build_skyygear_0.1.py - SkyyGear has no patch scripts - with ONLY these changes):
  - LEVEL BY MATERIAL, Skyy's lock (OPEN-QUESTIONS 2026-09-30: "bronze is hard to get in vanilla; our own gear fills the gaps later"):
    Crude 0, Wood 0, Copper 10, Bronze 15, Iron 15, Thorium 20, Cobalt 25, Adamantite 35, Mithril 40, Onyxium 40 (0.1 placeholders:
    Iron 20, Thorium 30, Cobalt 35, Adamantite 40, Mithril 50, Onyxium 50). MATERIALS below feeds the config.properties template, the
    built-in defaults (GearCfg.MAT_T / MAT_L, no file) and the kit's DEFAULTS (Server Setup -> Gear -> Levels "Level by material").
  - ONE-TIME UPDATE of an existing config.properties (GearCfg.migrate011, setup() after the SkyyRolls cost import and BEFORE the loader
    and the config kit start; the SkyyTrees 0.2.4 / SkyyAuctions 0.1.2 pattern): a level.material.<Material> line whose value is still
    EXACTLY the 0.1 default becomes the 0.1.1 default (Iron 20 -> 15, Thorium 30 -> 20, Cobalt 35 -> 25, Adamantite 40 -> 35, Mithril
    50 -> 40, Onyxium 50 -> 40); any other value is kept and logged once ("level.material.X=N kept (custom)"); a missing line stays
    missing (the loader's normal rule); the entry word matches case-insensitively like the loader; lines are read the kit's way
    (CfgFile.key / value / end: escapes, continuation lines - a continued line is never rewritten, last line wins). Only the value
    text of a changed line is replaced (its key, separator and CR stay); every other byte is kept (ISO-8859-1 in and out = what
    java.util.Properties and the kit read; LF / CRLF per line as found). Run once: the marker comment LV_MARK is inserted under the
    levels header (else before the first level.material line, else at the end) and a file that has it is never touched again - so a
    value an admin sets back to an old number later stays. The 0.1.1 default text carries the marker, so a fresh file never updates.
    Through the config kit's own path (kit 1.1, KEEP 10): CfgHist.snapshot keeps the old file as a History version ("before the 0.1.1
    level table update", restorable in Server Setup -> History), CfgRows.atomicWrite writes it (tmp + fsync + ATOMIC_MOVE, retries),
    and one config-changes.log line per changed material (name "SkyyGear 0.1.1", via update, status ok) lets Server Setup -> Changes
    undo each one; earlier in-game lines and history copies are left as they are (their Undo keeps working). One INFO line lists what
    changed; a failure leaves the file as it was (WARN) and the loader reads it as it is.
  - Version strings 0.1 -> 0.1.1; the ready line lists the live level table (GearCfg.matText).
  - STAT DEFAULTS (2026-09-30, OPEN-QUESTIONS LOCKED; still 0.1.1, not deployed): (1) Skyy: "if its not in the game yet, dont leave it
    in the reforge list" -> "Roll coming-later stats" (pool.later) default FALSE (was true): row default, GearCfg.POOL_LATER field and
    the loader fallback (a missing or unreadable pool.later line = off), so no stat with live 0 (Ferocity, Thorns, Weaken Enemy, ...)
    can roll on any path - every roll goes through GearRoll.pool (craft, bench + SkyySacks /craft bridge, identify of mob / chest
    drops, reforge page, /gear reroll | identify | give); SkyyRolls migration only moves dmg / str / crit (all live); gear that already
    has one keeps it until its next reforge (the lock). (2) stat.levelFull default 50 -> 40 (Mithril / Onyxium are level 40 now, so the
    top material rolls at full power): row, field, loader fallback. Row help texts say so; the ready line adds GearCfg.statText().
  - ONE-TIME UPDATE of the two lines in an existing config.properties (GearCfg.migrateStat011, setup() right after migrate011, before
    the loader): pool.later=true -> false and stat.levelFull=50 -> 40 ONLY when the line (the last one = what the loader reads, a
    one-line entry) still holds exactly the 0.1 default text; any other value is kept and noted once ("pool.later=on kept (custom)");
    a missing line stays missing (the loader's new fallback applies). The level update's machinery, method for method: pure text step
    stUpdate on the kit's parser (value text only; key, separator and CR kept; ISO-8859-1 bytes in and out), CfgHist.snapshot +
    lvSaved (no rewrite unless config-history really holds the old bytes - else WARN, untouched, the next start retries),
    CfgRows.atomicWrite, one config-changes.log line per changed key in the kit's scalar-row format (Server Setup -> Changes undoes
    each), one INFO line. ITS OWN MARKER (ST_MARK, "SkyyGear 0.1.1 stat defaults"), not the level marker: each marker records one
    decision and each update runs exactly once on its own (a file that already carries one still gets the other; a value set back by
    an admin later is never touched again), and the level update stays byte-for-byte the reviewed code. The marker goes above the
    first pool.later / stat.levelFull line (above its help comment when one sits right on top - where the fresh default file has it),
    else right under the level marker (always there after migrate011; neither = WARN, untouched, retried). First start of 0.1.1 on a
    0.1 file = two History versions ("before the 0.1.1 level table update", "before the 0.1.1 stat defaults update") and two writes.
  Nothing else changed: gear documents, rarity, rolls, identify / reforge, locks, drops, bridge keys, commands and permissions are
  byte-identical (class compare in the 0.1.1 build report). Bare-JVM harness: SkyyGear/test_skyygear_0.1.1.py (section X = the level
  update, section Y = the stat defaults + their update + every roll path with pool.later off).
  REVIEW FIXES (2026-09-30, review of 0.1.1; still 0.1.1, not deployed): (3) the update only rewrites the file once Server Setup ->
  History really lists a version holding the old bytes (GearCfg.lvSaved; CfgHist.snapshot swallows its own errors) - else WARN, file
  untouched, the next start tries again, so the INFO line's "the old file is in config-history" is always true; (4) a file that ends
  inside a still-open continued entry gets the marker just before that entry instead of after it (appended, it was swallowed as a
  continuation line, changing that value and re-running the update every start; the entry's bytes stay last and unchanged); (5)
  LV_WHO is the literal "SkyyGear 0.1.1". (The two items left here for the main session - the pool.later default and stat.levelFull
  vs the top material level 40 - are the STAT DEFAULTS change above.)

THIS FILE IS BUILT IN TWO PARTS (Skyy / RESUME step 4). PART A = this build. PART B = a second builder adds its classes at the
"PART B PLUGS IN HERE" markers below without rewriting PART A:
  PART A (built here): the gear document on the ItemStack with its GATE SKILL (spec 1), the Wynn rarity ladder + 7 quality assets
    (2.1), the level table (3.1-3.2), the gate check + level cache used by tooltips / bridge (3.3; enforcement is PART B), the modifier
    pool + rolling by rarity with the level-scaled strength (2.2-2.3, 4.2), crafted-gear rolls on the vanilla benches (GearCraftSys,
    5.1) + the gear:fn:roll bridge for SkyySacks /craft (5.2, 7.3.3), smithing rarity odds (5.3), /reforge (5.4, vanilla look 5.8),
    SkyyRolls migration (1.6, migrate.by=stats default, migrate.maxRarity), SkyBlock-style tooltips (6), the legacy stamp + the
    drop stamp GearThrowSys (1.5), bridge functions (7.1; GearTick publishes gear:stats:<uuid> = the active totals, gear:fn:stats
    reads it), Server Setup rows via tools/skyycfg.py kit 1.1 with KEEP=10 (9), player
    switches (9.3), admin /gear commands (8.1), gear.log (8.2), the SkyyRolls cost import (1.6) and the SkyyRolls-still-loaded
    warning (8.4).
  PART B (built 2026-09-28, second builder; declarations at the four "PART B PLUGS IN HERE" markers, code in the blocks
    "PART B (1/2)" before GearTick and "PART B (2/2)" after /reforge):
    - unidentified drops (5.5): mobs = GearDeathMark (EntityTickingSystem ordered BEFORE NPCDamageSystems$DropDeathItems, the same
      drop condition, marks {world, NPC position + (0,1,0)} for exactly one world tick) + GearDropSys (RefSystem on ItemComponent,
      AddReason.SPAWN, tags undocumented gear spawning within 2 blocks of a mark); world chests = GearChestMark / GearChestTag
      (ChunkStore RefSystems ordered BEFORE / AFTER StashPlugin$StashSystem: a container with a drop list is remembered, then every
      undocumented gear stack the stash roll put in is made unidentified inside the engine's own add). Rarity from odds.mob /
      odds.chest, no modifiers stored until identify (5.6). Unordered fallbacks + one WARN when the other system is missing.
    - /identify (5.7): IdentifyPage (the /reforge page's vanilla item-repair look: list of unidentified gear, detail panel with cost,
      Identify button, "Identify all N items" paid one by one and stopping at the first refusal) + IdentifyCmd (identify.command is
      checked live). GearIdent.identify = write safety 1.7: same slot + fingerprint, coins TAKEN FIRST (coins:fn:take), roll, same
      slot, REFUND (coins:fn:add) on any failure, gear.log TAKE / IDENTIFY / REFUND lines.
    - live stats (4.3): GearShotTrack (SkyyClasses ShotTrack copy: what a shooter held at launch), GearHitSys (Filter, BEFORE
      DamageSystems$ArmorDamageReduction: gate + Damage % / Strength or Magical Power / flat elements / crit / overcrit on weapon hits,
      pre-armor capture), GearArmorSys (AFTER it: the copied engine armor formula over only the active pieces, then Defense),
      GearTrueSys (AFTER GearArmorSys: + True Damage + the flat element damage, lock 17), GearLeechSys (Inspect: Life Steal / Mana
      Steal owed); GearFx (GearTick every second + GearFxInvSys on armor-container changes + GearLockSys every tick BEFORE
      EntityStatsSystems$Recalculate): skyygear_lock_<stat> MAX modifiers cancelling under-level armor's own Health / Mana /
      Stamina ... (x BrokenPenalties armor factor for broken pieces), Raw Health Regen x (1 + Health Regen %) and Stamina Regen
      every regen.periodMs, Life Steal payout every steal.windowS, Mana Steal, Speed through skyymove protocol v1 (source
      gear.armor, layer flat).
  REVIEW FIXES (2026-09-29, research/SkyyGear-0.1-Review-Findings.md; version stays 0.1, not deployed yet):
    - the armor lock never eats CURRENT Health / Mana / Stamina (engine review 1). EntityStatValue.putModifier / removeModifier
      recompute max and clamp the current value at once (VERIFIED bytecode), and the engine only adds a piece's own stats at
      EntityStatsSystems$Recalculate (LegacyArmorChangeStatSystem.scheduleRecalculate -> StatModifiersManager.applyStatModifiers,
      one MAX modifier per calculation type under CalculationType.createKey("Armor")). So a lock only GROWS in the 1 s tick and
      only when the engine's own Armor modifier already equals the container's sum for that stat (GearFx.plan: the piece's +sum is
      in, so -sum lands on the final max); a lock SHRINKS at once (always safe: max only goes up) from GearFxInvSys, from the tick
      and from GearLockSys, ordered BEFORE Recalculate so an unequipped piece's lock is gone before the engine drops its +sum.
    - projectile hits take the launcher's stats from the newest live launch record (exploit 1); armor in the hand is never judged
      as a weapon (engine 3); stackable gear (spears, spellbooks) is rolled / stamped per item: stacks are split into single items
      in empty slots, storage first (the /gear give order), counted before and after; what does not fit stays one stack (exploit
      2; no MaxStack override - splitting keeps the vanilla item assets); Weapon_Shortbow_Bomb is gear (exploit 3); migrated armor
      drops dmg (exploit 4); migrate.clampToLevel (exploit 5); the resolved Skyy_Gear_* quality indices persist in
      Skyy_SkyyGear/quality.properties and a stale / unknown stack quality is rewritten (engine 4); GearLog writes outside its
      lock, GearCfg.writeAtomic = temp + fsync + ATOMIC_MOVE (engine 6, 7); gear.include + kind.prefix + an Equipment slot letter
      (design 1), one totals function + the gear:extra:<uuid> bridge string (design 2), vanilla #ff6b6b / #39f493 (design 3),
      Mythic #CC66CC (design 4), Health Regen % rolls only with Raw Health Regen (design 5), element damage after armor (design 8),
      identify texts follow identify.command (design 9), 5 more coming-later Keep stats (design 11).
  FOLLOW-UP FIXES (2026-09-29, second review of the fix commit e43c8bf; version stays 0.1):
    - gear.include is guarded: the row check (and the loader) refuse prefixes under 6 characters and bare Skyy_ / Weapon_ / Armor_ /
      Tool_; include never beats the ammo rule; an included id with MaxStack > 1 is gear only as Weapon_ / Armor_ / Tool_, never
      above MaxStack 30; an included id that is not Weapon_ / Armor_ / Tool_ and has no kind.prefix row is kind equipment.
    - the ammo rule: parts[1] only for ids with MaxStack <= 1 (Weapon_Shortbow_Bomb stays gear), the old any-token test for
      stackable ids; split() skips ids with MaxStack > 30 (one WARN per id: add the prefix to gear.exclude).
    - stacks are split only when an action needs one item: Identify / Identify all / Reforge take ONE item off the stack (the rest
      moves as one stack to a free slot), crafted gear and loot chests roll per item; the passive scan never splits (a stack of
      identical documents stays one stack). Splits never go into the hotbar and always leave 5 storage + backpack slots free; a
      failed destination write restores the source (tagContainer catches its own split).
    - projectile hits with no launch record log one WARN; several live records with different weapons -> the weaker one (lower
      totals; a blocked record still blocks through liveBad). Locks saved with the player are picked up by GearLockSys once per
      join / world switch; a lock that waited 3 s for the engine schedules a Recalculate (then every 10 s, the 30 s WARN stays);
      negative armor sums are cancelled too. An unreadable quality.properties is left alone; no epoch bump on moved indices
      (GearView.apply rewrites a stack whose effective quality differs). gear:extra is summed with saturation, Damage % >= -100,
      a hit never goes below 0.
    - level enforcement: weapon (main hand + utility slot, projectiles by launch record + the 10 s shot window) above the gate level
      or unidentified -> amount 0 + cancelled + knockback removed + GearGate.popup (gear.blockedPopup gates only the popup); armor
      above the level or unidentified -> no SkyyGear stats, native Health / resistance cancelled (level.armorNative), one
      gear.armorWarn chat line each time a piece becomes inactive.
  Bare-JVM harness (spec 11.1 #3): SkyyGear/test_skyygear_0.1.2.py (load + verify every class under -Xverify:all, then the review
  fixes that a bare JVM can reach; scratch in tools/dev/scratch/, deleted after the run).

Commands (spec 8.1):
  /reforge                 player (hytale:Adventurer): the Reforge page (vanilla item-repair look): pick a weapon or armor piece,
                           pay coins (cost.reforge by rarity + level), its modifiers are re-rolled for its rarity and level; the
                           rarity never changes; Smithing XP through skill:fn:addxp (xp.reforge).
  /identify                player (hytale:Adventurer; Server Setup identify.command, live): the Identify page - reveal the
                           modifiers of unidentified gear for coins (cost.identify by rarity + level), one item or all of them.
  /gear                    player: the held item's gear lines, your active totals, your Smithing rarity.
  /gear give <item> [--rarity <id>] [--unid true] | read | reroll | clear | rarity <id> | unid | identify | level <n|clear> |
        gate <skill|class> | migrate [player] | charged [off] | relevel [player]
                           ADMIN: requirePermission("skyygear.admin") + setPermissionGroups(new String[0]) on every sub-command
                           (lint perm_group_leaks); the root /gear lists hytale:Adventurer. 0.2: /gear relevel [player] re-stamps
                           the stamped gear a player holds into today's bands; /gear level ignores the bands (marked lvlA).
Data: <world>/mods/Skyy_SkyyGear/ (getDataDirectory().resolveSibling): config.properties (the kit's rows), config-changes.log +
  config-history/ (kit, KEEP 10), players/<pkey>.properties (noticeShown), gear.log (rotated at 5 MB), quality.properties (the
  Skyy_Gear_* quality indices of the last start, engine review 4).
Bridge in (design review 2): gear:extra:<uuid> = "str:40,cc:10,..." (stat keys of section 4.2) another mod publishes (Accessory
  Power, the Equipment bar, set bonuses, powders later); SkyyGear adds it to the active totals it applies (combat, Defense, regen,
  steal, Speed). gear:stats:<uuid> stays SkyyGear's own items only, so a publisher never reads its own values back.
UI rules: inline pages only, no underscores in ids, root anchor Width/Height only, TextButton / Button + EventData, no periodic
  updates, never close-then-open, no ItemGridSlot at all (icons are ItemIcon { ItemId } = metadata free).
Vanilla look (spec 5.8, AGENT-BRIEF "UI LOOK"): the values in VANILLA below are copied from Assets.zip Common/UI/Custom/Common.ui,
  Sounds.ui and Pages/ItemRepairPage.ui / ItemRepairElement.ui (checked by this build). They are meant for the shared vanilla style
  helper of RESUME step 5 - move them there when it exists. Server Setup switch ui.frames (adv) turns the textures and sounds off
  (flat vanilla colours) as a safety valve if a texture path does not resolve in an inline page (UNVERIFIED in game).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG

VERSION = "0.2.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J0 = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J0["pool"], J0["CtField"], J0["CtNewMethod"], J0["CtNewConstructor"]
OUT = B.class_out(HERE)
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
AZ = zipfile.ZipFile(AZ_PATH)
AZ_NAMES = set(AZ.namelist())

# ================================================================= engine classes (probed below)
JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
BD  = "org.bson.BsonDocument"
BV  = "org.bson.BsonValue"
BA  = "org.bson.BsonArray"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IDM = "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata"
IQ  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality"
IWP = "com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon"
IAR = "com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor"
DBD = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown"
DBE = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown$Entry"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
EST2 = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
DCS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause"
I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
PCOL = "com.hypixel.hytale.protocol.Color"
TXN = "com.hypixel.hytale.server.core.inventory.transaction.Transaction"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
PAGE = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE = "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
CMGR = "com.hypixel.hytale.server.core.command.system.CommandManager"
NTU = "com.hypixel.hytale.server.core.util.NotificationUtil"
NST = "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle"
IWM = "com.hypixel.hytale.protocol.ItemWithAllMetadata"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
ARC = "com.hypixel.hytale.component.Archetype"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
DIE = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop"      # '$' form for the class literal (SkyySkills CREP)
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CREP = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"
CREPRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre"   # 0.2 (craft.belowBand block)
PERM = "com.hypixel.hytale.server.core.permissions.PermissionsModule"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"

for c, m in ((IS, "withMetadata"), (IS, "getMetadata"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItemId"),
             (IS, "getQuantity"), (IS, "getDurability"), (IS, "getMaxDurability"), (IS, "isEmpty"), (IS, "getItem"),
             (IS, "getFromMetadataOrNull"), (IS, "CODEC"), (IS, "toPacket"), (ITM, "getItemLevel"), (ITM, "getAssetMap"),
             (ITM, "getWeapon"), (ITM, "getArmor"), (ITM, "getTranslationKey"), (ITM, "getTranslationMessage"),
             (ITM, "getDescriptionTranslationKey"), (ITM, "getDescriptionTranslationMessage"), (ITM, "getMaxStack"),
             (IAR, "getStatModifiers"), (IAR, "getDamageResistanceValues"), (SMO, "getAmount"), (SMO, "getCalculationType"),
             (CAL, "MULTIPLICATIVE"), (EST2, "getAssetMap"), (DCS, "getId"),
             (IWP, "getBasicDamageBreakdown"), (IWP, "getUltimateDamageBreakdown"), (DBD, "entries"), (DBE, "min"), (DBE, "max"),
             (IQ, "getAssetMap"), (IQ, "getTextColor"), (IQ, "getId"), (IQ, "getLocalizationKey"), (PCOL, "red"),
             (IDM, "KEYED_CODEC"), (IDM, "KEY"), (I18N, "get"), (I18N, "getMessage"), (MSG, "raw"), (MSG, "color"), (MSG, "insert"),
             (MSG, "empty"), (INV, "getHotbar"), (INV, "getStorage"), (INV, "getBackpack"), (INV, "getArmor"), (INV, "getUtility"),
             (INV, "getTools"), (INV, "usingToolsItem"), (INV, "getActiveToolsSlot"), (INV, "getActiveHotbarSlot"),
             (IC, "getItemStack"), (IC, "setItemStackForSlot"), (IC, "getCapacity"), (IC, "addItemStack"), (TXN, "succeeded"),
             (PLA, "getInventory"), (PLA, "getPageManager"), (PLA, "getGameMode"), (PLA, "isWaitingForClientReady"), (GM, "Creative"),
             (PR, "getUuid"), (PR, "getUsername"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"), (PR, "sendMessage"),
             (PR, "getPacketHandler"), (PR, "hasPermission"), (PR, "getComponentType"), (PRE, "getPlayerRef"), (UNI, "get"),
             (UNI, "getWorld"), (UNI, "getPlayers"), (WLD, "execute"), (REF, "isValid"), (REF, "getStore"), (ST, "getComponent"),
             (ST, "getExternalData"), (EST, "getWorld"), (HSV, "SCHEDULED_EXECUTOR"), (ACH, "getReferenceTo"),
             (ICE, "getTransaction"), (DIE, "getItemStack"), (DIE, "setItemStack"), (DIE, "isCancelled"), (CRE, "getCraftedRecipe"),
             (CRE, "getQuantity"), (CRR, "getPrimaryOutput"), (CRR, "getTimeSeconds"), (CRR, "getId"), (MQ, "getItemId"),
             (MQ, "getQuantity"), (MQ, "getMetadata"), (PAGE, "rebuild"), (PAGE, "close"), (PAGE, "build"), (PAGE, "handleDataEvent"),
             (LIFE, "CanDismiss"), ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (UCB, "appendInline"), (UCB, "set"), (UEB, "addEventBinding"), (EVD, "of"), (BT, "Activating"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "setAllowsExtraArguments"),
             (CTX, "getInputString"), (CTX, "provided"), (CTX, "get"), (AC, "withOptionalArg"), (ATY, "STRING"), (ATY, "BOOLEAN"), (CMGR, "get"), (CMGR, "handleCommand"), (NTU, "sendNotification"), (NST, "Warning"),
             (JP, "getDataDirectory"), (JP, "getEntityStoreRegistry"), (JP, "getEventRegistry"), (JP, "getCommandRegistry"),
             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"), (PERM, "get"), (PERM, "hasPermission"),
             (BD, "append"), (BD, "clone"), (BD, "remove"), (BD, "containsKey"), (BD, "toJson"), (BA, "add"), (BV, "asDocument"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset")):
    B.probe(pool, c, m)
# spec 11.1 #2 probes that belong to PART B (kept here so a missing API fails the build early, before PART B is written)
for c, m in (("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction", "getResistanceModifiers"),
             ("com.hypixel.hytale.server.core.modules.entity.item.ItemComponent", "setItemStack"),
             ("com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility", "getActiveItem"),
             ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "putModifier")):
    B.probe(pool, c, m)
for c in ("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems",
          "com.hypixel.hytale.builtin.adventure.stash.StashPlugin$StashSystem"):
    try:
        pool.get(c)
    except Exception:
        # PART B targets; a missing class only matters to PART B (it registers unordered + WARN then)
        print("note: PART B target class not in the pool:", c)

PKG = "com.skyy.gear"
T = {"PKG": PKG, "IS": IS, "BD": BD, "BV": BV, "BA": BA, "MSG": MSG, "ITM": ITM, "IQ": IQ, "IWP": IWP, "IAR": IAR, "DBD": DBD,
     "DBE": DBE, "INV": INV, "IC": IC, "SIC": SIC, "PLA": PLA, "PR": PR, "REF": REF, "ST": ST, "WLD": WLD, "EST": EST, "CTX": CTX,
     "TXN": TXN, "PAGE": PAGE, "LIFE": LIFE, "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT, "IDM": IDM, "I18N": I18N,
     "PCOL": PCOL, "HSV": HSV, "UNI": UNI, "LOG": LOG, "GM": GM, "CRR": CRR, "MQ": MQ, "SMO": SMO, "CAL": CAL, "ESTT": EST2,
     "DCS": DCS, "CMGR": CMGR, "NTU": NTU, "NST": NST, "IWM": IWM, "ACH": ACH, "CB": CB, "EV": EV, "QRY": QRY, "ARC": ARC,
     "ICE": ICE, "DIE": DIE, "CRE": CRE, "CREP": CREP, "PRE": PRE, "APC": APC, "PERM": PERM, "JPI": JPI, "ATY": ATY, "OA": OA,
     "CREPRE": CREPRE}
# 0.2: the craft.belowBand block hook (CraftingManager.queueCraft / craftItem fire CraftRecipeEvent$Pre and return before the job is queued
# or any input is taken when it was cancelled - VERIFIED bytecode 2026-10-02, re-checked below) + the chat line to the /craft crafter
for c, m in ((CREPRE, "getCraftedRecipe"), (CREPRE, "isCancelled"), (CREPRE, "setCancelled"), (UNI, "getPlayer"), (CRR, "getPrimaryOutput")):
    B.probe(pool, c, m)


def J(src):
    for k in sorted(T, key=len, reverse=True):
        src = src.replace("@" + k + "@", T[k])
    left = re.findall(r"@[A-Z]+@", src)
    assert not left, "unresolved placeholder(s): %s" % left
    return src


def _mk(c, src):
    try:
        c.addMethod(CtNewMethod.make(J(src), c))
    except Exception as e:
        raise SystemExit("compile error in %s: %s\n%s" % (c.getName(), e, J(src)[:1500]))


def M(c, src):
    _mk(c, src)


def F(c, src):
    c.addField(CtField.make(J(src), c))


def C(c, src):
    try:
        c.addConstructor(CtNewConstructor.make(J(src), c))
    except Exception as e:
        raise SystemExit("constructor compile error in %s: %s\n%s" % (c.getName(), e, J(src)[:1200]))


def jstr(s):
    assert all(32 <= ord(ch) < 127 for ch in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }" if xs else "new String[0]"


def jints(xs):
    return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }" if xs else "new int[0]"


def jlit(txt):
    return '"' + txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# ================================================================= spec 2.1: the rarity ladder (LOCKED names + colours)
# (id, Name, hex (tooltip + quality TextColor), page hex (vanilla panel, spec 5.8: Mythic readable variant = SkyySacks' choice),
#  frame art: tooltip + arrow texture quality, slot texture quality, drop particle)
RARITIES = [
    ("normal", "Normal", "#FFFFFF", "#FFFFFF", "Common", "Common", "Drop_Common"),
    ("unique", "Unique", "#FFFF55", "#FFFF55", "Legendary", "Legendary", "Drop_Legendary"),
    ("rare", "Rare", "#FF55FF", "#FF55FF", "Epic", "Epic", "Drop_Epic"),
    ("legendary", "Legendary", "#55FFFF", "#55FFFF", "Rare", "Rare", "Drop_Rare"),
    ("fabled", "Fabled", "#FF5555", "#FF5555", "Common", "Developer", "Drop_Legendary"),
    # design review 4: Wynn's #AA00AA reads at ~2.8:1 on the tooltip; #CC66CC (still purple, LOCKED colour name) is SkyySacks' choice
    ("mythic", "Mythic", "#CC66CC", "#CC66CC", "Epic", "Epic", "Drop_Epic"),
    ("set", "Set", "#55FF55", "#55FF55", "Uncommon", "Uncommon", "Drop_Uncommon"),
]
NR = len(RARITIES)
R_IDS = [r[0] for r in RARITIES]
R_NAMES = [r[1] for r in RARITIES]
QUAL_IDS = ["Skyy_Gear_" + r[1] for r in RARITIES]
assert R_IDS == ["normal", "unique", "rare", "legendary", "fabled", "mythic", "set"]
LADDER = R_IDS[:6]          # stepping order for Smithing (never to Set)

# spec 2.2 rarity table (PLACEHOLDER): modifiers | low % | high %
RARITY_DEF = {"normal": (1, 30, 60), "unique": (2, 35, 70), "rare": (3, 40, 80), "legendary": (4, 45, 95),
              "fabled": (5, 50, 110), "mythic": (6, 60, 130), "set": (3, 45, 95)}
# spec 5.3 / 5.5 odds (PLACEHOLDER weights): craft | mob | chest
ODDS_DEF = {"normal": (60, 50, 45), "unique": (25, 30, 30), "rare": (10, 13, 15), "legendary": (4, 5, 7), "fabled": (1, 1.5, 2.4),
            "mythic": (0, 0.5, 0.6), "set": (0, 0, 0)}
# spec 5.4 reforge cost (base | per level), 5.7 identify cost, 5.4 Smithing XP per reforge (all PLACEHOLDER)
COST_R_DEF = {"normal": (250, 0), "unique": (500, 0), "rare": (1000, 0), "legendary": (2500, 0), "fabled": (5000, 0),
              "mythic": (10000, 0), "set": (2500, 0)}
COST_I_DEF = {"normal": (50, 5), "unique": (100, 10), "rare": (250, 20), "legendary": (500, 40), "fabled": (1000, 80),
              "mythic": (2500, 150), "set": (500, 40)}
XP_R_DEF = {"normal": 5, "unique": 10, "rare": 20, "legendary": 40, "fabled": 80, "mythic": 160, "set": 40}
# spec 1.6 migration score table (PLACEHOLDER): min score % per rarity (anything lower = normal)
MIG_DEF = {"unique": 25, "rare": 50, "legendary": 75, "fabled": 90}
MIG_IDS = ["unique", "rare", "legendary", "fabled"]
# SkyyRolls quality -> SkyyGear rarity (the cost import 1.6 and migrate.by=item)
ROLLS_QMAP = [("Junk", "normal"), ("Common", "normal"), ("Uncommon", "unique"), ("Rare", "rare"), ("Epic", "legendary"),
              ("Legendary", "fabled")]
for _r in R_IDS:
    assert _r in RARITY_DEF and _r in ODDS_DEF and _r in COST_R_DEF and _r in COST_I_DEF and _r in XP_R_DEF
    lo, hi = RARITY_DEF[_r][1], RARITY_DEF[_r][2]
    assert 0 <= lo <= hi <= 1000

# ================================================================= spec 4.2: the modifier pool (Keep rows only)
# key, label, slots (w = any gear weapon, s = spell weapon only, a = armor, e = Equipment - design review 1: the Equipment bar is
# a later stage; e marks the rows SkyyGear-Plan names for Equipment: Strength lock 16, Attack Speed lock 18, Speed lock 25,
# Magical Power lock 103), unit ("%" or ""), max @100 % (PLACEHOLDER), weight (PLACEHOLDER), live (1 = 0.1 applies it - PART B
# code; 0 = "(coming later)"), suffix kind
STATS = [
    ("dmg", "Damage", "w", "%", 30, 10, 1, ""),
    ("str", "Strength", "wae", "", 25, 10, 1, ""),
    ("mp", "Magical Power", "sae", "", 25, 10, 1, "spells"),
    ("cc", "Crit Chance", "wa", "%", 15, 10, 1, ""),
    ("cd", "Crit Damage", "wa", "%", 30, 10, 1, ""),
    # 0.1.2 (OPEN-QUESTIONS LOCKED 2026-09-30, research/Charged-Attack-Research.md 4.1-4.2): max 30 at 100 % power like Crit Damage,
    # weight 5 like the other situational lines (PLACEHOLDER numbers - the research found no reason to change Skyy's placeholder).
    # Live, but it may roll only while charged.on is on, on armor, and on a weapon with a detectable charged attack (GearRoll.pool)
    ("chg", "Charged Attack Damage", "wa", "%", 30, 5, 1, ""),
    ("tdmg", "True Damage", "w", "", 5, 5, 1, ""),
    ("fEarth", "Earth Damage", "w", "", 6, 4, 1, ""),
    ("fThunder", "Thunder Damage", "w", "", 6, 4, 1, ""),
    ("fWater", "Water Damage", "w", "", 6, 4, 1, ""),
    ("fFire", "Fire Damage", "w", "", 6, 4, 1, ""),
    ("fAir", "Air Damage", "w", "", 6, 4, 1, ""),
    ("rThunder", "Raw Thunder Damage", "w", "", 6, 3, 1, ""),
    ("rWater", "Raw Water Damage", "w", "", 6, 3, 1, ""),
    ("rElem", "Raw Elemental Damage", "w", "", 3, 3, 1, "elem"),
    ("msteal", "Mana Steal", "s", "", 3, 5, 1, "steal"),
    ("lsteal", "Life Steal", "wa", "%", 5, 5, 1, "steal"),
    ("hpr", "Raw Health Regen", "wa", "", 2, 5, 1, "regen"),
    ("hprp", "Health Regen %", "wa", "%", 20, 5, 1, "hprp"),      # design review 5: the catalog's "% Health Regen"
    ("def", "Defense", "a", "", 25, 10, 1, ""),
    ("spd", "Speed", "ae", "", 5, 10, 1, ""),
    ("stam", "Stamina Regen", "a", "", 2, 5, 1, "regen"),
    ("as", "Attack Speed", "wae", "%", 10, 5, 0, ""),
    ("fer", "Ferocity", "wa", "", 10, 5, 0, ""),
    ("thorns", "Thorns", "a", "%", 10, 5, 0, ""),
    ("expl", "Exploding", "w", "%", 10, 5, 0, ""),
    ("poison", "Poison", "w", "", 20, 5, 0, ""),
    ("kb", "Knockback", "w", "%", 20, 5, 0, ""),
    ("slow", "Slow Enemy", "w", "%", 10, 5, 0, ""),
    ("weak", "Weaken Enemy", "w", "%", 10, 5, 0, ""),
    ("dEarth", "Earth Defence", "a", "", 10, 3, 0, ""),
    ("dThunder", "Thunder Defence", "a", "", 10, 3, 0, ""),
    ("dWater", "Water Defence", "a", "", 10, 3, 0, ""),
    ("dFire", "Fire Defence", "a", "", 10, 3, 0, ""),
    ("dAir", "Air Defence", "a", "", 10, 3, 0, ""),
    ("cwis", "Combat Wisdom", "wa", "%", 10, 5, 0, ""),
    # design review 11: the Keep rows of Plan lock 124 that spec 4.2 left out (placement not stated, spec Q15 -> lock 125's general
    # rule: any combat gear). Coming later, small PLACEHOLDER weights.
    ("lbonus", "Loot Bonus", "wa", "%", 10, 2, 0, ""),
    ("lquality", "Loot Quality", "wa", "%", 10, 2, 0, ""),
    ("stealing", "Stealing", "wa", "%", 5, 2, 0, ""),
    ("trophy", "Trophy Hunter", "wa", "%", 10, 2, 0, ""),
    ("xpb", "XP Bonus", "wa", "%", 5, 2, 0, ""),
]
NS = len(STATS)
S_KEYS = [s[0] for s in STATS]
assert len(set(S_KEYS)) == NS, "duplicate stat key"
SPEC_KEYS = ("dmg str mp cc cd tdmg fEarth fThunder fWater fFire fAir rThunder rWater rElem msteal lsteal hpr hprp def spd stam "
             "as fer thorns expl poison kb slow weak dEarth dThunder dWater dFire dAir cwis").split()
LATER_KEYS = "lbonus lquality stealing trophy xpb".split()      # design review 11, appended after the spec 4.2 rows
# 0.1.2: Charged Attack Damage sits right after Crit Damage (display order = table order; research 4.3)
SPEC_KEYS = SPEC_KEYS[:SPEC_KEYS.index("cd") + 1] + ["chg"] + SPEC_KEYS[SPEC_KEYS.index("cd") + 1:]
assert S_KEYS == SPEC_KEYS + LATER_KEYS, "the stat table must match spec 4.2 (keys + display order) + the design-review rows + chg"
assert S_KEYS.index("chg") == S_KEYS.index("cd") + 1 and STATS[S_KEYS.index("chg")] == ("chg", "Charged Attack Damage", "wa", "%", 30, 5, 1, "")
for _s in STATS:
    assert re.match(r"^[a-z][a-zA-Z]*$", _s[0]) and re.match(r"^(?!.*(.).*\1)[wsae]{1,4}$", _s[2]) and _s[3] in ("", "%"), _s
    assert _s[4] > 0 and _s[5] >= 0 and _s[6] in (0, 1) and _s[7] in ("", "spells", "elem", "steal", "regen", "hprp"), _s
    assert '"' not in _s[1] and "|" not in _s[1], _s
assert [s[0] for s in STATS if s[6] == 1] == SPEC_KEYS[:22], "live stats = spec 4.2 LIVE rows + chg (0.1.2)"

# ================================================================= spec 3.3: the gate skill per gear kind (LOCKED)
GATE_BY_KIND = [("combat", "class"), ("mining", "Mining"), ("foraging", "Foraging"), ("farming", "Farming"), ("tool", ""),
                ("equipment", "class"), ("accessory", "")]
# the kinds whose gate 0.1 enforces: combat, and Equipment (same class gate, spec 1.4) so the Equipment stage needs no code edit;
# the gathering kinds get enforced with their own hooks (block break, harvest) in the gathering stage
ENFORCED_KINDS = ["combat", "equipment"]
# design review 1: the kinds kind.prefix may name (Server Setup table), and the ids that are never gear, even through gear.include
KIND_CHOICES = ["combat", "mining", "foraging", "farming", "equipment"]
NEVER_GEAR = ["Skyy_Sack_", "Skyy_Bag_", "Skyy_Accessory_Bag"]     # Magic Bags, bag upgrade items, the Accessory Bag
# follow-up review 1: gear.include entries that are refused (too broad): shorter than INCL_MIN characters or one of these families
INCL_MIN = 6
INCL_BARE = ["Skyy_", "Weapon_", "Armor_", "Tool_"]
GEAR_FAMILIES = ["Weapon_", "Armor_", "Tool_"]     # the only included ids that may stack (MaxStack > 1)
STACK_CEIL = 30             # follow-up review 2: no gear above this MaxStack is split (vanilla max: spears 30, VERIFIED below)
FREE_KEEP = 5               # follow-up review 3: a split always leaves this many storage + backpack slots empty
# spec 1.6 tool families of SkyyRolls-rolled tools (VERIFIED families in Assets.zip); every other Tool_* -> kind "tool", no gate
TOOL_FAMILIES = [("Tool_Pickaxe_", "mining"), ("Tool_Hatchet_", "foraging"), ("Tool_Hoe_", "farming"), ("Tool_Sickle_", "farming"),
                 ("Tool_Shovel_", "mining")]
_gk = dict(GATE_BY_KIND)
assert _gk["combat"] == "class" and _gk["mining"] == "Mining" and _gk["foraging"] == "Foraging" and _gk["farming"] == "Farming"
for _p, _k in TOOL_FAMILIES:
    assert _k in _gk, _p
    assert any(n.startswith("Server/Item/Items/") and os.path.basename(n).startswith(_p) for n in AZ_NAMES), "no Assets item " + _p
# spec 3.3: SkyyGear's own class -> weapon skill copy (tooltip text only, when SkyyClasses is absent)
CLASS_SKILLS = [("Archer", "Archery"), ("Warrior", "Swordsmanship"), ("Mage", "Sorcery"), ("Berserker", "Fury"),
                ("Priest", "Divinity"), ("Assassin", "Assassination")]
# spec 1.3: weapon prefixes that are not gear (config row gear.exclude) + the SkyyRolls AMMO tokens (code rule)
EXCLUDE_DEF = ",".join(["Weapon_Shield_", "Weapon_Bomb", "Weapon_Gun", "Weapon_Deployable_", "Weapon_Dart_", "Weapon_Claws_",
                        "Weapon_Blowgun_", "Weapon_Assault_Rifle", "Weapon_Handgun", "Weapon_Grenade_", "Weapon_Test_"])
AMMO = ["arrow", "arrows", "bolt", "bolts", "bomb", "bombs", "dart", "darts", "grenade", "grenades", "ammo", "bullet", "bullets",
        "shell", "shells", "shuriken", "shurikens", "thrown"]
SPELL_PREFIXES = ["Weapon_Staff_", "Weapon_Wand_", "Weapon_Spellbook_"]
# exploit review 3: only the token right after the family counts (GearData.ammo = parts[1]). Build check against Assets.zip: the
# 14 real ammo ids stay ammo, and the only id the old any-token rule caught besides them is the Archer shortbow Weapon_Shortbow_Bomb.
_W_IDS = sorted(set(os.path.basename(n)[:-5] for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json")
                    and os.path.basename(n).startswith("Weapon_")))
_AMMO_NEW = [i for i in _W_IDS if len(i.split("_")) > 1 and i.split("_")[1].lower() in AMMO]
_AMMO_OLD = [i for i in _W_IDS if any(p.lower() in AMMO for p in i.split("_")[1:])]
AMMO_IDS = ["Weapon_Arrow_Clearshot", "Weapon_Arrow_Crude", "Weapon_Arrow_Deadeye", "Weapon_Arrow_Iron", "Weapon_Arrow_Trueshot",
            "Weapon_Bomb", "Weapon_Bomb_Continuous", "Weapon_Bomb_Fire", "Weapon_Bomb_Large_Fire", "Weapon_Bomb_Popberry",
            "Weapon_Bomb_Potion_Poison", "Weapon_Bomb_Stun", "Weapon_Dart_Tribal", "Weapon_Grenade_Frag"]
assert _AMMO_NEW == AMMO_IDS, "ammo ids changed in Assets.zip: %s" % _AMMO_NEW
assert sorted(set(_AMMO_OLD) - set(_AMMO_NEW)) == ["Weapon_Shortbow_Bomb"], sorted(set(_AMMO_OLD) - set(_AMMO_NEW))
# follow-up review 2: the rule the jar runs (GearData.ammoMs): parts[1] for MaxStack <= 1, any token for stackable ids. MaxStack as the
# engine resolves it (Item.processConfig, VERIFIED bytecode): the MaxStack of the item or its Parent chain, else 1 for an item with a
# Weapon / Armor / Tool section, else 100.
_AZ_JSON = {}
for _n in AZ_NAMES:
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        try:
            _AZ_JSON[os.path.basename(_n)[:-5]] = json.loads(AZ.read(_n).decode("utf-8-sig"))
        except Exception:
            pass


def az_max_stack(i):
    seen, cur, sect = 0, i, False
    while cur in _AZ_JSON and seen < 16:
        d = _AZ_JSON[cur]
        if "MaxStack" in d:
            return int(d["MaxStack"])
        sect = sect or any(k in d for k in ("Weapon", "Armor", "Tool"))
        cur, seen = d.get("Parent"), seen + 1
    return 1 if sect else 100


def az_ammo(i):
    ps = i.split("_")
    if az_max_stack(i) <= 1:
        return len(ps) > 1 and ps[1].lower() in AMMO
    return any(p.lower() in AMMO for p in ps[1:])


assert az_max_stack("Weapon_Shortbow_Bomb") == 1, "Weapon_Shortbow_Bomb stacks now: %s" % az_max_stack("Weapon_Shortbow_Bomb")
assert [i for i in _W_IDS if az_ammo(i)] == AMMO_IDS, "ammo under the MaxStack rule: %s" % [i for i in _W_IDS if az_ammo(i)]
_EXCL0 = EXCLUDE_DEF.split(",")
_STACK_GEAR = dict((i, az_max_stack(i)) for i in _W_IDS if not az_ammo(i) and not i.startswith(tuple(_EXCL0)) and az_max_stack(i) > 1)
assert _STACK_GEAR and max(_STACK_GEAR.values()) <= STACK_CEIL, "stackable vanilla gear above the split ceiling: %s" % _STACK_GEAR
assert all(i.startswith(("Weapon_Spear_", "Weapon_Spellbook_")) for i in _STACK_GEAR), sorted(_STACK_GEAR)
# spec 3.2 default material table - LOCKED 2026-09-30 (Skyy, OPEN-QUESTIONS; 0.1.1): Bronze and Iron both 15 (bronze is hard to get in
# vanilla), Thorium 20, Cobalt 25, Adamantite 35, Mithril / Onyxium 40; our own gear fills the level gaps later
MATERIALS = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 15), ("Thorium", 20), ("Cobalt", 25),
             ("Adamantite", 35), ("Mithril", 40), ("Onyxium", 40)]
# the 0.1 placeholders: GearCfg.migrate011 rewrites a config.properties line that still holds exactly one of these (0.1.1 update)
MATERIALS_010 = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 20), ("Thorium", 30), ("Cobalt", 35),
                 ("Adamantite", 40), ("Mithril", 50), ("Onyxium", 50)]
assert dict(MATERIALS) == {"Crude": 0, "Wood": 0, "Copper": 10, "Bronze": 15, "Iron": 15, "Thorium": 20, "Cobalt": 25,
                           "Adamantite": 35, "Mithril": 40, "Onyxium": 40}, "MATERIALS is not Skyy's 2026-09-30 table"
assert [t for t, _l in MATERIALS_010] == [t for t, _l in MATERIALS], "MATERIALS_010 must list the same materials in the same order"
assert [t for (t, l), (_t0, l0) in zip(MATERIALS, MATERIALS_010) if l != l0] == ["Iron", "Thorium", "Cobalt", "Adamantite", "Mithril",
                                                                                 "Onyxium"], "0.1.1 changes exactly six materials"
# the marker comment of the 0.1.1 update (in the default text and in every updated file): a doc comment with spaces, so the kit never
# takes it for a "#key=value" template line; migrate011 looks for LV_MARK_ID in comment lines only
LV_MARK_ID = "SkyyGear 0.1.1 level defaults"
LV_MARK = "# %s (Skyy 2026-09-30): %s" % (LV_MARK_ID, ", ".join("%s %d" % tl for tl in MATERIALS))
LV_HEAD = "# ---- levels (spec 3.1-3.2): level.material.<first matching id word>=<level>, level.item.<item id>=<level> ----"
# the name on the update's config-changes.log lines and its History version: a fixed literal, like the History text "before the 0.1.1
# level table update" (review of 0.1.1, finding 5) - a later version copied from this script keeps naming the 0.1.1 update correctly
LV_WHO = "SkyyGear 0.1.1"
assert all(32 <= ord(_c) < 127 for _c in LV_MARK + LV_HEAD), "the marker and the levels header must be plain ASCII (ISO-8859-1 = UTF-8)"
# 0.1.1 STAT DEFAULTS (OPEN-QUESTIONS LOCKED 2026-09-30): Skyy "if its not in the game yet, dont leave it in the reforge list" ->
# pool.later off; Mithril / Onyxium are level 40 -> stat.levelFull 40. (key, 0.1 default text, 0.1.1 default text, what it means):
# GearCfg.migrateStat011 rewrites a config.properties line that still holds exactly the 0.1 text (same rules as migrate011)
ST_DEFAULTS = [("pool.later", "true", "false", "coming-later stats never roll"),
               ("stat.levelFull", "50", "40", "full modifier power from item level 40 = Mithril / Onyxium")]
# its own marker (not the level marker): each update runs exactly once on its own. A doc comment with spaces and no "key=value"
# token, so the kit never takes it for a template line; migrateStat011 looks for ST_MARK_ID in comment lines only
ST_MARK_ID = "SkyyGear 0.1.1 stat defaults"
ST_MARK = ("# %s (Skyy 2026-09-30): coming-later stats never roll (pool.later false), full modifier power from item level 40 "
           "(stat.levelFull 40, Mithril / Onyxium)" % ST_MARK_ID)
assert all(32 <= ord(_c) < 127 for _c in ST_MARK + "".join("".join(_t) for _t in ST_DEFAULTS)), "the stat marker must be plain ASCII"
assert ST_MARK_ID not in LV_MARK and LV_MARK_ID not in ST_MARK and "=" not in ST_MARK, "the two markers must not match each other"
assert [(_k, _o) for _k, _o, _n, _w in ST_DEFAULTS] == [("pool.later", "true"), ("stat.levelFull", "50")], "the 0.1 defaults"
# 0.1.2 Charged Attack Damage lines: the marker of the one-time update GearCfg.migrate012 (in the default text and in every updated
# file; a doc comment with spaces and no "key=value" token, so the kit never takes it for a template line) and the update's name
CH_MARK_ID = "SkyyGear 0.1.2 charged attack lines"
CH_MARK = ("# %s (Skyy 2026-09-30): Charged Attack Damage on weapons with a charged attack + armor, bows only the glowing full draw, "
           "spells x 0.15, never clubs" % CH_MARK_ID)
CH_WHO = "SkyyGear 0.1.2"
assert all(32 <= ord(_c) < 127 for _c in CH_MARK) and "=" not in CH_MARK, "the charged marker must be plain ASCII without '='"
assert CH_MARK_ID not in LV_MARK + ST_MARK and LV_MARK_ID not in CH_MARK and ST_MARK_ID not in CH_MARK, "markers must not match"
REFORGE_NAMES_DEF = "Sharp,Heroic,Spicy,Gentle,Odd,Fast,Epic,Withered"
for _n in REFORGE_NAMES_DEF.split(","):
    assert _n.lower() not in [x.lower() for x in R_NAMES], "reforge name is a rarity name: " + _n
PENDING_MAX_MS = 1000       # spec 1.5: a technical constant, not a balance number
SCAN_GAP_MS = 250           # spec 1.5: one coalesced stamp scan at most every 250 ms per player
CHEST_GRACE_MS = 3000       # 0.1.3: the loot window lasts this long after the world chest window was last seen open (technical)
CHEST_LOOT_CAP_MS = 15000   # 0.1.3 review finding 1: and never longer than this after its start (an open / a new decision)
assert CHEST_GRACE_MS < CHEST_LOOT_CAP_MS
KNOWN_RETRY_S = 30          # 0.1.3: the player list read retries this often until it worked once, then every KNOWN_EVERY_S
KNOWN_EVERY_S = 900
VIEW_V = 1                  # spec 6.4

# ---- Assets.zip build checks (spec 11.1 #2)
AZ_ITEMS = set(os.path.basename(n)[:-5] for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _tok, _lv in MATERIALS:
    assert any(("_" + _tok + "_") in ("_" + i + "_") for i in AZ_ITEMS if i.startswith(("Weapon_", "Armor_"))), "no item for " + _tok
for _kit in ("Weapon_Shortbow_Crude", "Weapon_Sword_Crude", "Weapon_Battleaxe_Crude", "Weapon_Daggers_Crude", "Weapon_Staff_Wood",
             "Weapon_Wand_Wood"):
    assert _kit in AZ_ITEMS, _kit
    _tok = next(t for t in _kit.split("_") if t in dict(MATERIALS))
    assert dict(MATERIALS)[_tok] == 0, "class kit weapon %s must resolve to level 0" % _kit

# ================================================================= 0.1.3: levels for the non-metal gear families (see the header)
# Skyy's metal tiers (LOCKED 2026-09-30): Crude / Wood 0, Copper 10, Bronze / Iron 15, Thorium 20, Cobalt 25, Adamantite 35, Mithril /
# Onyxium 40. Hytale's own ItemLevel of those metals: Copper 10, Iron 15-20, Bronze 25-28, Thorium 30, Cobalt 35, Adamantite 40, Mithril /
# Onyxium 50 - the vanilla -> Skyy map used below where nothing better exists. Every row was decided from Assets.zip (recipe metal,
# drop lists = which zone's mobs / chests give it, NPC roles, quality). (entry, level, why). The build prints every family with the
# vanilla levels of its items (= the table for Skyy) and checks it against Assets.zip.
FAMILIES = [
    # cloth armor: one step (5) below the metal bar its recipe needs - Wool Copper, Linen Iron, Cotton Thorium, Silk Cobalt,
    # Cindercloth Adamantite (Hytale gives cloth its bar's level: 10 / 15 / 25 / 35 / 45)
    ("Wool", 5, "cloth armor, Copper bars (Copper 10 - 5); also the unobtainable Armor_Wool set"),
    ("Linen", 10, "cloth armor, Iron bars (Iron 15 - 5)"),
    ("Cotton", 15, "cloth armor, Thorium bars (Thorium 20 - 5)"),
    ("Silk", 20, "cloth armor, Cobalt bars (Cobalt 25 - 5)"),
    ("Cindercloth", 30, "cloth armor (Rare), Adamantite bars (Adamantite 35 - 5)"),
    # leather armor: the cloth ladder (Hytale gives leather exactly the cloth levels 10 / 15 / 25 / 35); two words because "Leather"
    # comes first in these ids and Light / Medium / Heavy / Soft alone would catch other mods' items
    ("Leather_Soft", 5, "leather armor, the Wool step"),
    ("Leather_Light", 10, "leather armor, the Linen step"),
    ("Leather_Medium", 15, "leather armor, the Cotton step"),
    ("Leather_Heavy", 20, "leather armor, the Silk step"),
    ("Leather_Raven", 20, "leather armor (Uncommon): Heavy leather + Cotton bolts = the Heavy step"),
    # zone 1 camps and drops
    ("Stone", 5, "Stone Trork weapons: Zone 1 Trork camps, crafted from rock + wood (just above Crude 0) - Skyy's Lv 25 report"),
    ("Trork", 5, "Trork warrior armor: Zone 1 Trork mobs, the camp of the Stone weapons"),
    ("Fishbone", 5, "spear from the Crude fishing trap (an early craft)"),
    ("Scrap", 10, "Zone 1 Goblin drops (Hytale 15 = Iron's low end; below Iron as junk gear)"),
    ("Steel_Rusty", 10, "rusty steel weapons: Zone 1-3 Undead drops (Iron_Rusty items keep Iron 15 - add an Iron_Rusty row to match)"),
    ("Steel_Flail_Rusty", 10, "the rusty steel flail club, same family"),
    ("Leaf", 10, "Leaf spear: Zone 1 / 3 Kweebec chests"),
    ("Kweebec", 10, "Kweebec armor (Uncommon): Zone 1 / 3 Kweebec chests"),
    ("Cutlass", 10, "plain cutlass, Hytale 15 like Scrap"),
    ("Shortbow_Bomb", 10, "prototype bow (Hytale 10 = Copper)"),
    ("Shortbow_Combat", 10, "prototype bow (Hytale 10 = Copper)"),
    ("Shortbow_Pull", 10, "prototype bow (Hytale 10 = Copper)"),
    ("Shortbow_Ricochet", 10, "prototype bow (Hytale 10 = Copper)"),
    ("Shortbow_Vampire", 10, "prototype bow (Hytale 10 = Copper)"),
    ("Tribal", 15, "Tribal weapons: Iron bar recipes (Iron 15)"),
    ("Bone", 5, "Bone weapons (Rare, Zone 2 Feran drops, Hytale 25): Skyy's own bucket for Bone is 0-5 (review of 0.1.3, finding 7)"),
    # zone 2-3
    ("Steel", 20, "steel armor / sword (Uncommon, Hytale 20-30) between Iron and Cobalt = Thorium 20"),
    ("Incandescent", 20, "Hytale 30 = Thorium's level"),
    ("Zombie", 20, "zombie arm / leg clubs, Hytale 30 = Thorium's level"),
    ("Katana", 20, "Hytale 30 = Thorium's level"),
    ("Nexus", 20, "Hytale 30 = Thorium's level"),
    ("Runic", 20, "Hytale 30 = Thorium's level"),
    ("Kunai", 20, "throwing knives (Hytale's spell / thrown placeholder 40), a mid weapon"),
    ("Grimoire", 20, "the two plain grimoires: the first spellbooks (Hytale gives every spellbook the placeholder 40)"),
    ("Wizard", 20, "wizard staff (Hytale 40 is the placeholder every staff has - Wood staff included)"),
    ("Doomed", 25, "Doomed weapons (Rare): Zone 3 Outlander drops (Cobalt 25 is Zone 3's metal)"),
    ("Void", 25, "Void scythe / longsword: Wraith and Void spawn weapons, Hytale 30"),
    ("Frost", 25, "Frost sword / shortbow: Zone 3 frost skeletons (Cobalt 25); the frost spellbook / staff have their own rows"),
    ("Flame", 25, "Flame longsword (Legendary) / shortbow, Hytale 20-30"),
    # zone 4 and late
    ("Praetorian", 25, "Praetorian longsword: the Zone 4 burnt praetorian's weapon, Hytale's own 25 (never above Hytale's level)"),
    ("Ancient", 30, "Ancient Steel crossbow (Rare): Zone 4 undead"),
    ("Steel_Ancient", 30, "Ancient Steel armor (Rare): Zone 4 burnt skeletons (beats Steel)"),
    ("Crystal", 30, "crystal staffs (Hytale 30-40)"),
    ("Spellbook_Fire", 30, "fire spellbook (late spellbook)"),
    ("Spellbook_Frost", 30, "frost spellbook = the fire spellbook (both Hytale 40; beats Frost - review of 0.1.3, finding 7)"),
    ("Staff_Frost", 30, "frost staff = the crystal staffs (Hytale 40; beats Frost - review of 0.1.3, finding 7)"),
    ("Scarab", 35, "Scarab weapons, Hytale 40-60 = Adamantite's level"),
    ("Spectral", 35, "Hytale 40 = Adamantite's level"),
    ("Silversteel", 35, "Hytale 45, between Adamantite and Mithril"),
    ("Demon", 35, "demon spellbook (late spellbook)"),
    ("Rekindle", 35, "Rekindle Embers spellbook (Rare): the Zone 4 burnt praetorian"),
    ("Crystal_Flame", 40, "Arcane bench staff (Rare): gem + silver / gold bars + 20 essences = top mage weapon (beats Crystal)"),
    ("Crystal_Ice", 40, "Arcane bench staff (Rare), the Crystal_Flame twin"),
    ("Prisma", 45, "Hytale's highest set (armor 75, mace 50): above Mithril / Onyxium 40"),
    # plain staffs / wands (Hytale's placeholder 40, like the Wood staff and wand that are 0 here)
    ("Root", 5, "root wand, a plain wand like Wood"),
    ("Stoneskin", 5, "stoneskin wand, a plain wand like Wood"),
    ("Bamboo", 5, "bamboo bo staff (the wood bo is Wood 0)"),
    ("Cane", 5, "walking-cane staff"),
    ("Onion", 5, "onion staff (a joke staff)"),
]
FAM_DEV = ["Armor_QA_", "Armor_Trooper_", "Weapon_Shortbow_Test_"]    # developer / debug quality, not obtainable: Hytale's level stays
assert len(FAMILIES) == 59 and len(set(t.lower() for t, _l, _w in FAMILIES)) == len(FAMILIES), "59 distinct family rows"
assert not set(t.lower() for t, _l, _w in FAMILIES) & set(t.lower() for t, _l in MATERIALS), "a family row repeats a metal"
for _t, _l, _w in FAMILIES:
    assert re.match(r"^[A-Z][A-Za-z]*(_[A-Z][A-Za-z]*){0,2}$", _t) and 0 <= _l <= 100 and _w and '"' not in _w, (_t, _l)
FAM_WORDS = max(len(t.split("_")) for t, _l, _w in FAMILIES)
assert FAM_WORDS == 3, "the longest entry (Steel_Flail_Rusty) has 3 words"
# the marker of the one-time update GearCfg.migrate013 (in the default text and in every updated file; a doc comment without '=')
FM_MARK_ID = "SkyyGear 0.1.3 level families"
FM_MARK = ("# %s (Skyy 2026-10-01): non-metal weapons and armor (Stone, Bone, cloth, leather, ...) get a level here too; "
           "an entry may be several words of the id in a row (Leather_Soft); remove a row to use Hytale's own level" % FM_MARK_ID)
FM_WHO = "SkyyGear 0.1.3"
assert all(32 <= ord(_c) < 127 for _c in FM_MARK) and "=" not in FM_MARK, "the family marker must be plain ASCII without '='"
assert all(FM_MARK_ID not in _m and _i not in FM_MARK for _m, _i in ((LV_MARK, LV_MARK_ID), (ST_MARK, ST_MARK_ID), (CH_MARK, CH_MARK_ID))), "markers"

# ================================================================= 0.2 (stage 1): OVERLAPPING MATERIAL LEVEL BANDS (spec 2, see the header)
# Skyy (OPEN-QUESTIONS 2026-10-01, spec question 2 answered): "keep the table with a +3 overlap". Every metal band runs from Skyy's LOCKED
# 2026-09-30 start level to the NEXT material's start + 3 (the Wynncraft overlap); Wood / Crude start at 1 instead of 0 (Wynn levels start
# at 1, Skyy's example starts at Lv 1); the top metals end at 49 (question 3: vanilla materials cover 1-49, our own tiers fill 50-100 later).
# Copper ARMOR = the entry Armor_Copper, a default row 1-18 (LOCKED 2026-10-01: "lower copper armors minimum level to 1, since there is no
# lower tier armor"; an entry at the start of the id beats the Copper row). The 59 family rows run from their 0.1.3 level to that + 7
# (level.bandWidth 8 = a 5-level step plus the 3-level overlap), never above 49.
VANILLA_TOP = 49
BAND_W_DEF = 8
GATE_FLOOR_DEF = 1
_MSTART = dict(MATERIALS)
_MSTART.update({"Crude": 1, "Wood": 1})
_MNEXT = {"Crude": "Copper", "Wood": "Copper", "Copper": "Iron", "Bronze": "Thorium", "Iron": "Thorium", "Thorium": "Cobalt",
          "Cobalt": "Adamantite", "Adamantite": "Mithril"}


def _mcap(t):
    return min(_MSTART[_MNEXT[t]] + 3, VANILLA_TOP) if t in _MNEXT else VANILLA_TOP


BANDS = [(t, _MSTART[t], _mcap(t)) for t, _l in MATERIALS]
BANDS.insert([b_[0] for b_ in BANDS].index("Copper") + 1, ("Armor_Copper", 1, 18))
assert BANDS == [("Crude", 1, 13), ("Wood", 1, 13), ("Copper", 10, 18), ("Armor_Copper", 1, 18), ("Bronze", 15, 23), ("Iron", 15, 23),
                 ("Thorium", 20, 28), ("Cobalt", 25, 38), ("Adamantite", 35, 43), ("Mithril", 40, 49), ("Onyxium", 40, 49)], \
    "the bands must be Skyy's table (Wood / Crude 1-13, Copper 10-18, copper armor 1-18, Bronze / Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49)"
assert all(_s >= 1 and _s <= _c <= VANILLA_TOP for _t, _s, _c in BANDS)
FAM_BANDS = [(t, l, min(l + BAND_W_DEF - 1, VANILLA_TOP)) for t, l, _w in FAMILIES]
assert dict((t, (s, c)) for t, s, c in FAM_BANDS)["Prisma"] == (45, 49) and dict((t, (s, c)) for t, s, c in FAM_BANDS)["Wool"] == (5, 12)
assert all(c - s == BAND_W_DEF - 1 or c == VANILLA_TOP for t, s, c in FAM_BANDS), "families: start..start+7, never above 49"
BD_ALL = BANDS + FAM_BANDS          # entry, min, cap in default-file order (the metals with Armor_Copper, then the 59 family rows)
assert len(set(t.lower() for t, _s, _c in BD_ALL)) == len(BD_ALL) == 70
# the 0.1.3 DEFAULT texts the one-time update GearCfg.migrate02 turns into bands (only a line still holding exactly this text): the metals
# (Skyy's 0.1.1 values), the 59 family rows (0.1.3) and Armor_Copper=1 - the value OPEN-QUESTIONS (LOCKED 2026-10-01) told Skyy to type into
# Server Setup until this build ships it as a default
BD_OLD = [(t, str(l)) for t, l in MATERIALS] + [("Armor_Copper", "1")] + [(t, str(l)) for t, l, _w in FAMILIES]
assert sorted(t for t, _o in BD_OLD) == sorted(t for t, _s, _c in BD_ALL)


def band_text(s, c):
    """the file text of a band row (the kit's 2-column table: cells joined by sep=, = ',')"""
    return "%d,%d" % (s, c)


def cap_of(s, w=BAND_W_DEF):
    """what one number N means in 0.2 (GearCfg.capOf): N to N + width - 1, never past 49 while N is a vanilla level (<= 49), never past 100"""
    c = s + max(1, w) - 1
    if s <= VANILLA_TOP and c > VANILLA_TOP:
        c = VANILLA_TOP
    return min(c, 100)


assert cap_of(10) == 17 and cap_of(45) == 49 and cap_of(49) == 49 and cap_of(60) == 67 and cap_of(98) == 100 and cap_of(0) == 7
# the marker of the one-time update GearCfg.migrate02 (in the default text and in every updated file; a doc comment without '=', so the
# kit never takes it for a "#key=value" template line); it heads the block of the new 0.2 level settings
BD_MARK_ID = "SkyyGear 0.2 level bands"
BD_MARK = ("# %s (Skyy 2026-10-01 / 2026-10-02): each level.material row holds <min>,<cap> - crafted gear is made at the crafter's level "
           "inside that band (Wood 1-13, Copper 10-18, copper armor 1-18, Iron 15-23 ...); a row with one number covers N to N + "
           "level.bandWidth - 1. The level settings of 0.2 follow" % BD_MARK_ID)
BD_WHO = "SkyyGear 0.2"
assert all(32 <= ord(_c) < 127 for _c in BD_MARK) and "=" not in BD_MARK, "the bands marker must be plain ASCII without '='"
assert all(BD_MARK_ID not in _m and _i not in BD_MARK for _m, _i in ((LV_MARK, LV_MARK_ID), (ST_MARK, ST_MARK_ID), (CH_MARK, CH_MARK_ID),
                                                                   (FM_MARK, FM_MARK_ID))), "markers must not match each other"
# the new 0.2 scalar rows (Server Setup); a fresh file has them right under the bands marker, migrate02 adds the missing ones there
BD_ROWK = ["part.levels", "level.bandWidth", "level.gateFloor", "craft.levelFrom", "craft.belowBand", "craft.weaponSkill"]
# ================================================================= 0.2.1 (stages 2 + 3): BASE STATS FROM THE ITEM LEVEL (see the header)
# spec 3.1: F(L) = a straight line between these points (weapon damage + armor Health); spec 3.4: R(L) for armor resistance. Both are
# Server Setup rows (base.curve / base.resCurve, PLACEHOLDERS). F(1) = 1 exactly: a Lv 1 kit item keeps its vanilla numbers.
BASE_CURVE_DEF = "1:1.0,4:1.6,10:2.0,40:3.0,100:5.0"
BASE_RES_DEF = "1:1.0,10:1.4,20:1.7,40:2.2,100:3.0"
BASE_MAT_DEF = 0.3          # spec 3.1: % per level a material's band starts at (Copper 10 = +3%); a band starting at Lv 1 gets none
# spec 3.4: the Lv 1 base of every armor slot = the vanilla Copper row (VERIFIED Assets.zip: Armor_Copper_<slot> Health / Physical =
# Projectile Percent resistance); there is no Feet slot (ItemArmorSlot = Head, Chest, Hands, Legs)
BASE_ARMOR_DEF = [("Head", 5, 3.6), ("Chest", 9, 6.48), ("Legs", 7, 5.04), ("Hands", 4, 2.88)]


def py_curve(text, lv):
    """the jar's GearBase.eval in Python: level:multiplier points, straight lines between, flat outside the ends"""
    pts = [(float(a), float(b)) for a, b in (p.split(":") for p in text.split(","))]
    if lv <= pts[0][0]:
        return pts[0][1]
    for (l0, v0), (l1, v1) in zip(pts, pts[1:]):
        if lv <= l1:
            return v0 + (v1 - v0) * (lv - l0) / (l1 - l0)
    return pts[-1][1]


def py_bonus(start, pct=BASE_MAT_DEF):
    return 1.0 if start <= 1 else 1.0 + pct * start / 100.0


def py_round(x):
    """round half up (spec 3.3)"""
    import math
    return int(math.floor(x + 0.5))


# spec 3.1 table + 3.3 worked table, re-derived from the defaults (the build stops when a default no longer reproduces Skyy's numbers)
assert py_curve(BASE_CURVE_DEF, 1) == 1.0 and py_curve(BASE_RES_DEF, 1) == 1.0, "F(1) and R(1) must be exactly 1 (kits keep vanilla)"
assert [round(py_curve(BASE_CURVE_DEF, _l), 2) for _l in (1, 4, 5, 9, 10, 15, 20, 25, 30, 35, 40, 49, 60, 100)] == \
    [1.0, 1.6, 1.67, 1.93, 2.0, 2.17, 2.33, 2.5, 2.67, 2.83, 3.0, 3.3, 3.67, 5.0], "spec 3.1 F(L) table"
WORKED = {1: ("6-8", 25, 5, "6-11", 16, 12, 16, 9, "6.5"), 4: ("10-13", 40, 8, "10-18", 26, 19, 26, 14, "7.3"),
          10: ("12-16", 50, 10, "12-22", 32, 24, 32, 18, "9.1"), 20: ("14-19", 58, 12, "14-26", 37, 28, 37, 21, "11.0"),
          40: ("18-24", 75, 15, "18-33", 48, 36, 48, 27, "14.3")}
for _l, _w in WORKED.items():
    # wand swings 6 / 8 + orb 25, staff swing 5, sword swings 6..11 + thrust 16, shortbow full draw 12 + headshot 16, chestplate 9 Health /
    # 6.48 % resistance (Copper row) - all Lv 1 items of a band starting at Lv 1, so K = 1 and no material bonus (spec 3.3 says so)
    _f, _r = py_curve(BASE_CURVE_DEF, _l), py_curve(BASE_RES_DEF, _l)
    _got = ("%d-%d" % (py_round(6 * _f), py_round(8 * _f)), py_round(25 * _f), py_round(5 * _f), "%d-%d" % (py_round(6 * _f), py_round(11 * _f)),
            py_round(16 * _f), py_round(12 * _f), py_round(16 * _f), py_round(9 * _f), "%.1f" % (py_round(6.48 * _r * 10.0) / 10.0))
    assert _got == _w, "spec 3.3 worked table at Lv %d: %s vs %s" % (_l, _got, _w)
# the marker of the one-time update GearCfg.migrate021 (a comment without '='); it heads the block of the 0.2.1 settings, which a fresh file
# carries right under level.armorNative (the last level row) and migrate021 adds there to an existing file
LS_MARK_ID = "SkyyGear 0.2.1 level stats"
LS_MARK = ("# %s (Skyy 2026-10-02, new weapon level same stats): an item's level sets its base stats - every weapon hit is the vanilla "
           "step x K (the family's Crude / Wood size) x F(level) x the material bonus, and worn armor gets its slot's Lv 1 Health x F(level) "
           "and Physical / Projectile resistance x R(level) per piece. part.base off - vanilla numbers (levels and requirements stay)"
           % LS_MARK_ID)
LS_WHO = "SkyyGear 0.2.1"
assert all(32 <= ord(_c) < 127 for _c in LS_MARK) and "=" not in LS_MARK, "the level stats marker must be plain ASCII without '='"
assert all(LS_MARK_ID not in _m and _i not in LS_MARK for _m, _i in ((LV_MARK, LV_MARK_ID), (ST_MARK, ST_MARK_ID), (CH_MARK, CH_MARK_ID),
                                                                   (FM_MARK, FM_MARK_ID), (BD_MARK, BD_MARK_ID))), "markers must not match"
# the new 0.2.1 scalar rows, in block order (part.base first), then the base.armor table lines under their own comment line
LS_ROWK = ["part.base", "base.mode", "base.curve", "base.matBonus", "base.armorOn", "base.resCurve"]
# (review of 0.2.1 nit: the comment a server owner reads in config.properties names no internal doc section)
LS_TBLC = ("# ---- base.armor.<Head|Chest|Legs|Hands>=<Lv 1 Health>,<Lv 1 resistance %> (Lv 1 armor stats by slot; default = the "
           "vanilla Copper row) ----")
assert "spec" not in LS_TBLC.lower() and "spec" not in LS_MARK.lower(), "config comments must not point into our design docs"
LS_TBLL = ["base.armor.%s=%s,%s" % (_s, ("%g" % _h), ("%g" % _r)) for _s, _h, _r in BASE_ARMOR_DEF]
assert LS_TBLL == ["base.armor.Head=5,3.6", "base.armor.Chest=9,6.48", "base.armor.Legs=7,5.04", "base.armor.Hands=4,2.88"]
assert all(32 <= ord(_c) < 127 for _c in LS_TBLC) and "=" in LS_TBLC and LS_TBLC.startswith("# ---- ")


def az_get(i, k):
    """an item field as the engine resolves it (the item, then its Parent chain)"""
    seen, cur = 0, i
    while cur in _AZ_JSON and seen < 16:
        if k in _AZ_JSON[cur]:
            return _AZ_JSON[cur][k]
        cur, seen = _AZ_JSON[cur].get("Parent"), seen + 1
    return None


def lvl_lookup(table, i):
    """GearLevel.level's material step in Python (the jar runs the same loop): at each id word from the left the longest entry first,
    up to the most words any entry has (max 3); -> (entry in lower case, level) or (None, None)"""
    m = dict((t.lower(), l) for t, l in table)
    mw = min(3, max(len(t.split("_")) for t, _l in table))
    tk = i.split("_")
    for a in range(len(tk)):
        for n in range(mw, 0, -1):
            if a + n <= len(tk) and "_".join(tk[a:a + n]).lower() in m:
                return "_".join(tk[a:a + n]).lower(), m["_".join(tk[a:a + n]).lower()]
    return None, None


_GEAR_AZ = [i for i in sorted(AZ_ITEMS) if (i.startswith("Armor_") or (i.startswith("Weapon_") and not az_ammo(i)
                                                                          and not i.startswith(tuple(EXCLUDE_DEF.split(",")))))]
_MAT2 = [(t, l) for t, l in MATERIALS]
_NEW2 = _MAT2 + [(t, l) for t, l, _w in FAMILIES]
_was = dict((i, lvl_lookup(_MAT2, i)) for i in _GEAR_AZ)
_now = dict((i, lvl_lookup(_NEW2, i)) for i in _GEAR_AZ)
assert lvl_lookup(_MAT2, "Weapon_Sword_Iron") == ("iron", 15) and lvl_lookup(_MAT2, "Weapon_Staff_Bo_Wood") == ("wood", 0)
assert not [i for i in _GEAR_AZ if _was[i][0] is not None and _was[i] != _now[i]], "a metal-resolved vanilla id changed level"
FAM_FALLBACK = [i for i in _GEAR_AZ if _was[i][0] is None]            # the ids that fell back to Hytale's ItemLevel in 0.1.2
_still = [i for i in FAM_FALLBACK if _now[i][0] is None]
assert _still and all(i.startswith(tuple(FAM_DEV)) for i in _still), "a non-developer id still falls back: %s" % _still
assert all(str(az_get(i, "Quality")) in ("Debug", "Developer") for i in _still), "the ids left on Hytale's level are developer items"
_fam_items = dict((t.lower(), [i for i in FAM_FALLBACK if _now[i][0] == t.lower()]) for t, _l, _w in FAMILIES)
assert all(_fam_items[t.lower()] for t, _l, _w in FAMILIES), "a family row matches no vanilla item: %s" % [t for t, _l, _w in FAMILIES if not _fam_items[t.lower()]]
assert _now["Weapon_Daggers_Stone_Trork"] == ("stone", 5), "Skyy's report: Stone Trork Daggers"
assert _now["Weapon_Sword_Steel_Rusty"] == ("steel_rusty", 10) and _now["Weapon_Club_Steel_Flail_Rusty"] == ("steel_flail_rusty", 10)
assert _now["Armor_Steel_Ancient_Chest"] == ("steel_ancient", 30) and _now["Armor_Leather_Soft_Head"] == ("leather_soft", 5)
assert _now["Weapon_Staff_Crystal_Ice"] == ("crystal_ice", 40) and _now["Weapon_Staff_Crystal_Fire_Trork"] == ("crystal", 30)
FAM_REPORT = [(t, l, sorted(set(int(az_get(i, "ItemLevel") or 0) for i in _fam_items[t.lower()])), len(_fam_items[t.lower()]), w)
              for t, l, w in FAMILIES]
print("0.1.3 level families: %d vanilla weapon / armor ids, %d fell back to Hytale's ItemLevel in 0.1.2, %d now have a family row, "
      "%d developer-only ids keep Hytale's level (%s)" % (len(_GEAR_AZ), len(FAM_FALLBACK), len(FAM_FALLBACK) - len(_still), len(_still),
                                                         ", ".join(_still)))
for _t, _l, _vl, _n, _w in FAM_REPORT:
    print("  %-18s %3d  (Hytale %-9s %2d item%s) %s" % (_t, _l, ",".join(str(x) for x in _vl) + ")", _n, "" if _n == 1 else "s", _w))
# the installed mods (read only, when the folder is there): metal-resolved modded ids never change; list the fallback ids that gain a row
_MODS_DIR = os.path.join(B.HYTALE, "UserData", "Mods")
if os.path.isdir(_MODS_DIR):
    _mid = {}
    _mjs = {}        # review of 0.1.3 finding 6: every mod item json (templates too), for the old ItemLevel through the Parent chain
    for _p in sorted(os.listdir(_MODS_DIR)):
        if not _p.endswith((".zip", ".jar")):
            continue
        try:
            with zipfile.ZipFile(os.path.join(_MODS_DIR, _p)) as _z:
                for _n in _z.namelist():
                    _b = os.path.basename(_n)[:-5]
                    if _n.endswith(".json") and "/Item/Items/" in _n and _b.startswith(("Weapon_", "Armor_")) and _b not in AZ_ITEMS:
                        _mid.setdefault(_b, _p)
                    if _n.endswith(".json") and "/Item/Items/" in _n and _b not in _mjs:
                        try:
                            _mjs[_b] = json.loads(_z.read(_n).decode("utf-8-sig"))
                        except Exception:
                            pass
        except Exception:
            pass

    def _mod_level(i):
        """a modded id's own ItemLevel (= its 0.1.2 level when no table row matched): the mod's json, then its Parent chain through
        the mods and Assets.zip; None = none found (the engine's default applies)"""
        seen, cur = 0, i
        while seen < 16 and cur:
            d = _mjs.get(cur) if cur in _mjs else _AZ_JSON.get(cur)
            if not isinstance(d, dict):
                return None
            if "ItemLevel" in d:
                return d["ItemLevel"]
            cur, seen = d.get("Parent"), seen + 1
        return None
    _mch = [i for i in _mid if lvl_lookup(_MAT2, i)[0] is not None and lvl_lookup(_MAT2, i) != lvl_lookup(_NEW2, i)]
    assert not _mch, "a metal-resolved modded id would change level: %s" % _mch[:10]
    _mnew = sorted((i, lvl_lookup(_NEW2, i)) for i in _mid if lvl_lookup(_MAT2, i)[0] is None and lvl_lookup(_NEW2, i)[0] is not None)
    print("0.1.3 installed mods: %d modded Weapon_ / Armor_ ids, 0 metal-resolved ids change, %d fallback ids gain a family row "
          "(Hytale item level -> family level, mod file):" % (len(_mid), len(_mnew)))
    for i, (_e, l) in _mnew:
        _ol = _mod_level(i)
        print("  %-50s %4s -> %3d  (%s, row %s)" % (i, "none" if _ol is None else _ol, l, _mid[i], _e))
else:
    print("0.1.3 note: no Mods folder - the modded-id level check was skipped")


# ---- 0.2: the band of every vanilla gear id + gathering tool (GearLevel.band in Python: the same lookup, the band of the matched row)
def band_lookup(table, i):
    """(entry in lower case, min, cap) of the row GearLevel.band uses for id i (table = (entry, min, cap)); (None, None, None) = no row"""
    e, s = lvl_lookup([(t, s_) for t, s_, _c in table], i)
    if e is None:
        return None, None, None
    return e, s, dict((t.lower(), c) for t, _s, c in table)[e]


_TOOL_AZ = [i for i in sorted(AZ_ITEMS) if i.startswith(tuple(p for p, _k in TOOL_FAMILIES))]
_B02 = dict((i, band_lookup(BD_ALL, i)) for i in _GEAR_AZ + _TOOL_AZ)
for _kit in ("Weapon_Shortbow_Crude", "Weapon_Sword_Crude", "Weapon_Battleaxe_Crude", "Weapon_Daggers_Crude", "Weapon_Staff_Wood",
             "Weapon_Wand_Wood"):
    assert _B02[_kit][1:] == (1, 13), "class kit weapon %s must read Lv 1 (band 1-13): %s" % (_kit, _B02[_kit])
assert all(_B02[i][:3] == ("armor_copper", 1, 18) for i in _GEAR_AZ if i.startswith("Armor_Copper_")), "copper armor 1-18 (LOCKED 2026-10-01)"
assert [i for i in _GEAR_AZ if i.startswith("Armor_Copper_")], "no copper armor in Assets.zip"
assert _B02["Weapon_Sword_Copper"][1:] == (10, 18) and _B02["Tool_Pickaxe_Copper"][1:] == (10, 18) and _B02["Weapon_Sword_Iron"][1:] == (15, 23)
assert _B02["Weapon_Staff_Mithril"][1:] == (40, 49) and _B02["Weapon_Daggers_Stone_Trork"][1:] == (5, 12)
# every id keeps its 0.1.3 start level except Wood / Crude (0 -> 1) and copper armor (10 -> 1); the ids without any row stay without one
_chg02 = sorted(set((i, (_now.get(i) or lvl_lookup(_NEW2, i))[1], _B02[i][1]) for i in _GEAR_AZ + _TOOL_AZ
                    if (_now.get(i) or lvl_lookup(_NEW2, i))[1] != _B02[i][1]))
assert all(e_ in ("crude", "wood", "armor_copper") for e_ in (_B02[i][0] for i, _a, _b in _chg02)), "0.2 changes a start level: %s" % _chg02
assert all(_B02[i][0] is None for i in FAM_FALLBACK if _now[i][0] is None), "an id without a 0.1.3 row gained one"
_bsum = {}
for i, (e_, s_, c_) in _B02.items():
    if e_ is not None:
        _bsum.setdefault((s_, c_), []).append(i)
print("0.2 level bands: %d vanilla gear ids + %d gathering tools; %d start levels change (Wood / Crude 0 -> 1, copper armor 10 -> 1), "
      "%d ids keep Hytale's own level (developer items)" % (len(_GEAR_AZ), len(_TOOL_AZ), len(_chg02),
                                                          sum(1 for i in _B02 if _B02[i][0] is None)))
for (s_, c_) in sorted(_bsum):
    print("  band %2d-%2d: %3d ids (e.g. %s)" % (s_, c_, len(_bsum[(s_, c_)]), ", ".join(sorted(_bsum[(s_, c_)])[:3])))


def az_texture(path):
    """a UI texture path as the client resolves it (relative to Common/UI/Custom/ or Common/, @2x variants count)"""
    for base in ("Common/UI/Custom/", "Common/"):
        p = base + path
        if p in AZ_NAMES or p[:-4] + "@2x.png" in AZ_NAMES:
            return True
    return False


for _r in RARITIES:
    for _q in (_r[4], _r[5]):
        assert ("Server/Item/Qualities/%s.json" % _q) in AZ_NAMES, _q
    assert any(n.endswith("/" + _r[6] + ".particlesystem") for n in AZ_NAMES), "no particle system " + _r[6]

# ================================================================= spec 5.8: vanilla look (values copied from Assets.zip)
# FOR THE SHARED VANILLA STYLE HELPER (RESUME step 5): move this dict there when it exists. Every entry is checked against the
# vanilla text below (Common.ui / Sounds.ui) so a game update that changes them fails the build instead of drifting silently.
# (read-only build checks against the game's own UI documents; nothing here is shipped - every page is built inline. The folder
#  and the document names are kept apart so tools/ci/lint.py's ".ui file" rule never mistakes these reads for a shipped file.)
_VDIR = "Common/" + "UI/Custom/"
_VDOC = dict(common="Common", sounds="Sounds", page="Pages/ItemRepairPage", element="Pages/ItemRepairElement",
             bad="Pages/AssetPackSaveBrowser", ok="Pages/Memories/MemoriesCategory")


def vdoc(k):
    return AZ.read(_VDIR + _VDOC[k] + ".u" + "i").decode("utf-8", "replace")


COMMON_UI = vdoc("common")
SOUNDS_UI = vdoc("sounds")
REPAIR_UI = vdoc("page")
REPAIR_EL = vdoc("element")
VANILLA = {
    "ColorDefault": "#ffffff", "ColorDefaultLabel": "#96a9be", "ColorGoldHighlight": "#E8A93B", "ColorGrayCaption": "#878e9c",
    "ColorDisabled": "#797b7c", "ColorButtonText": "#bfcdd5",
}
for _k, _v in VANILLA.items():
    assert ("@%s = %s;" % (_k, _v)) in COMMON_UI, "Common.ui no longer has @%s = %s" % (_k, _v)
V_TITLE_COLOR = "#b4c8c9"         # @TitleStyle TextColor (FontSize 15, Secondary font, bold, uppercase)
V_SECOND_BTN = "#bdcbd3"          # @SecondaryButtonLabelStyle TextColor
V_PANEL_TITLE = "#afc2c3"         # @PanelTitle label TextColor, line #393426(0.5)
V_SEPARATOR = "#2b3542"           # @ContentSeparator
V_ROW_HOVER = "#000000(0.2)"      # ItemRepairElement.ui row hover
V_ROW_SUB = "#ffffff(0.6)"        # ItemRepairElement.ui #Durability + the 2 px divider
for _needle in ("TextColor: #b4c8c9", "TextColor: #bdcbd3", "TextColor: #afc2c3", "Background: #393426(0.5)", "Color: #2b3542",
                "@TitleHeight = 38;", "\"Common/ContainerHeader.png\", HorizontalBorder: 50, VerticalBorder: 0",
                "\"Common/ContainerPatch.png\", Border: 23", "Anchor: (Width: 236, Height: 11, Top: -12)",
                "Anchor: (Width: 236, Height: 11, Bottom: -6)", "@ButtonBorder = 12;", "@PrimaryButtonHeight = 44;",
                "\"Common/Buttons/Primary.png\", VerticalBorder: @ButtonBorder, HorizontalBorder: 80",
                "\"Common/Buttons/Secondary.png\", Border: @ButtonBorder", "\"Common/Buttons/Destructive.png\", Border: @ButtonBorder",
                "\"Common/Scrollbar.png\", Border: 3", "\"Common/ScrollbarHandle.png\", Border: 3",
                "\"Common/ContainerVerticalSeparator.png\"", "FontSize: 17,", "RenderUppercase: true,"):
    assert _needle in COMMON_UI, "Common.ui changed: " + _needle
for _needle in ('@ButtonsLightActivate = "Sounds/ButtonsLightActivate.ogg";', '@ButtonsLightHover = "Sounds/ButtonsLightHover.ogg";',
                '@ButtonsCancelActivate = "Sounds/ButtonsCancelActivate.ogg";'):
    assert _needle in SOUNDS_UI, "Sounds.ui changed: " + _needle
assert "$C.@DecoratedContainer" in REPAIR_UI and "TopScrolling" in REPAIR_UI and "@DefaultScrollbarStyle" in REPAIR_UI
# design review 3: the refusal / too-low red and the "met" green are the game's own label colours (not the rarity reds / greens)
V_BAD = "#ff6b6b"                 # vanilla error label (AssetPackSaveBrowser, PrefabSavePage, ...)
V_OK = "#39f493"                  # vanilla counter "complete" green (MemoriesCategory)
assert ("TextColor: " + V_BAD) in vdoc("bad"), "vanilla error red changed"
assert ("TextColor: " + V_OK) in vdoc("ok"), "vanilla complete green changed"
assert "Background: #000000(0.2)" in REPAIR_EL and "TextColor: #ffffff(0.6)" in REPAIR_EL and "Anchor: (Width: 32, Height: 32)" in REPAIR_EL
V_TEXTURES = ["Common/ContainerHeader.png", "Common/ContainerPatch.png", "Common/ContainerDecorationTop.png",
              "Common/ContainerDecorationBottom.png", "Common/ContainerVerticalSeparator.png", "Common/Buttons/Primary.png",
              "Common/Buttons/Primary_Hovered.png", "Common/Buttons/Primary_Pressed.png", "Common/Buttons/Disabled.png",
              "Common/Buttons/Secondary.png", "Common/Buttons/Secondary_Hovered.png", "Common/Buttons/Secondary_Pressed.png",
              "Common/Buttons/Destructive.png", "Common/Buttons/Destructive_Hovered.png", "Common/Buttons/Destructive_Pressed.png",
              "Common/Scrollbar.png", "Common/ScrollbarHandle.png", "Common/ScrollbarHandleHovered.png",
              "Common/ScrollbarHandleDragged.png"]
for _t in V_TEXTURES:
    assert az_texture(_t), "vanilla texture missing in Assets.zip: " + _t
for _snd in ("Sounds/ButtonsLightActivate.ogg", "Sounds/ButtonsLightHover.ogg", "Sounds/ButtonsCancelActivate.ogg"):
    assert ("Common/UI/Custom/" + _snd) in AZ_NAMES, _snd

# ================================================================= spec 2.1: the 7 quality assets + lang lines (jar asset pack)
EXTRA = {}
LANG = []
for _i, (_rid, _nm, _hex, _phex, _tt, _slot, _part) in enumerate(RARITIES):
    _q = {
        "QualityValue": _i + 1,
        "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _tt,
        "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _tt,
        "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "TextColor": _hex.lower(),
        "LocalizationKey": "server.general.qualities.%s" % QUAL_IDS[_i],
        "VisibleQualityLabel": True,
        "RenderSpecialSlot": True,
        "ItemEntityConfig": {"ParticleSystemId": _part},
    }
    _vanilla_fields = set(json.loads(AZ.read("Server/Item/Qualities/Common.json").decode("utf-8")).keys())
    assert set(_q.keys()) == _vanilla_fields, "quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _vanilla_fields)
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert az_texture(_q[_k]), "texture missing: " + _q[_k]
    EXTRA["Server/Item/Qualities/%s.json" % QUAL_IDS[_i]] = json.dumps(_q, indent=2)
    LANG.append("general.qualities.%s = %s" % (QUAL_IDS[_i], _nm))
EXTRA["Server/Languages/en-US/server.lang"] = "\n".join(LANG) + "\n"
assert "general.qualities.Common = Common" in AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")

# ================================================================= 0.1.2: Charged Attack Damage - the build-time walk + self-check
# ---- CHARGED WALKER BEGIN (pure Python over the Assets.zip JSON; the 0.1.2 harness exec()s this block from the build script)
class AzWalker:
    """Every weapon item's interaction chains as the engine walks them (InteractionManager.walkChain + the labels of
    WeaponDamageDataCollector), from the raw JSON: the item Parent chain (Interactions / InteractionVars merged per key), inline
    Parent merges (child wins, nested objects deep-merged, TargetedDamage / AngledDamage entries decoded fresh = replaced), Replace
    (item var else DefaultValue; no Next), Charging Next keys + Failed, Chaining, Serial, Parallel (root refs), Selector (HitEntity,
    HitEntityRules, HitBlock, Next, Failed), Repeat, DamageEntity (+ Angled / Targeted calculators and their Next), Projectile ->
    ProjectileConfig ProjectileHit chain, LaunchProjectile ids; every other type = Next (+ any child list) and Failed / Blocked.
    Label per step (VERIFIED engine rule, 0.1.2 glow refinement): an edge ChargingTag s > 0 = charged at s seconds, FULL when s is
    that Charging step's largest Next key, else PARTIAL (the bow's early draws); s = 0 and StringTag Failed / Blocked = NORMAL;
    every other edge keeps the parent's label. Records carry a calculator key: the JSON object that defines the step (the same
    object = the same engine asset = the same DamageCalculator instance), so ambiguity is judged per item like the jar does."""
    NORMAL, PARTIAL = -1.0, -3.0
    SIG_TYPES = ("Ability1", "Ability2", "Ability3")

    def __init__(self, az, names=None, items_overlay=None):
        import os
        self.az = az
        names = names if names is not None else az.namelist()
        self.inter, self.roots, self.pcfg, self.items = {}, {}, {}, {}
        for n in names:
            if not n.endswith(".json"):
                continue
            b = os.path.basename(n)[:-5]
            if n.startswith("Server/Item/Interactions/"):
                self.inter[b] = n
            elif n.startswith("Server/Item/RootInteractions/"):
                self.roots[b] = n
            elif n.startswith("Server/ProjectileConfigs/"):
                self.pcfg[b] = n
            elif n.startswith("Server/Item/Items/"):
                self.items[b] = n
        self._cache = {}
        self._res = {}
        for k, v in (items_overlay or {}).items():       # pack items (More Crossbow Tiers): id -> parsed JSON
            self.items[k] = "overlay:" + k
            self._cache["overlay:" + k] = v

    def js(self, n):
        import json
        if n not in self._cache:
            try:
                self._cache[n] = json.loads(self.az.read(n).decode("utf-8-sig"))
            except Exception:
                self._cache[n] = None
        return self._cache[n]

    @staticmethod
    def merge(base, over):
        if not isinstance(base, dict) or not isinstance(over, dict):
            return over
        out = dict(base)
        for k, v in over.items():
            if k == "Parent":
                continue
            if isinstance(v, dict) and isinstance(base.get(k), dict) and k not in ("TargetedDamage",):
                out[k] = AzWalker.merge(base.get(k), v)
            else:
                out[k] = v
        return out

    def resolve_parent(self, d, table, seen=None):
        seen = seen or set()
        p = d.get("Parent") if isinstance(d, dict) else None
        if not p or p in seen or p not in table:
            return d
        seen.add(p)
        base = self.resolve_parent(self.js(table[p]) or {}, table, seen)
        return self.merge(base, d)

    def item(self, iid):
        n = self.items.get(iid)
        d = self.js(n) if n else None
        if d is None:
            return None
        chain, cur, seen = [], d, set()
        while isinstance(cur, dict):
            chain.append(cur)
            p = cur.get("Parent")
            if not p or p in seen or p not in self.items:
                break
            seen.add(p)
            cur = self.js(self.items[p])
        out = {}
        for c in reversed(chain):
            for k, v in c.items():
                if k in ("Interactions", "InteractionVars") and isinstance(v, dict):
                    m = dict(out.get(k) or {})
                    m.update(v)
                    out[k] = m
                else:
                    out[k] = v
        return out

    @staticmethod
    def refs(v):
        if v is None:
            return []
        return list(v) if isinstance(v, list) else [v]

    def interaction(self, ref):
        """(asset id or None, resolved dict or None, identity key) of a string id or an inline object"""
        if isinstance(ref, str):
            n = self.inter.get(ref)
            d = self.js(n) if n else None
            if d is None:
                return ref, None, ("missing", ref)
            k = ("asset", ref)
            if k not in self._res:
                self._res[k] = self.resolve_parent(d, self.inter)
            return ref, self._res[k], k
        if isinstance(ref, dict):
            k = ("inline", id(ref))
            if k not in self._res:
                self._res[k] = self.resolve_parent(ref, self.inter)
            return None, self._res[k], k
        return None, None, ("none", None)

    def root_ids(self, ref):
        """a root reference (RootInteractions id, or an inline {Interactions: [...]}, or a bare list) -> interaction refs"""
        if isinstance(ref, str):
            n = self.roots.get(ref)
            d = self.js(n) if n else None
            if d is None:
                return []
            return self.refs(self.resolve_parent(d, self.roots).get("Interactions"))
        if isinstance(ref, dict):
            if "Type" in ref or "Parent" in ref:
                return [ref]
            return self.refs(ref.get("Interactions"))
        if isinstance(ref, list):
            return list(ref)
        return []

    def roots_of(self, v):
        out = []
        for r in self.refs(v) if isinstance(v, list) else [v]:
            out += self.root_ids(r)
        return out

    def norm(self, d):
        """the engine walk semantics of one resolved interaction"""
        t = d.get("Type")
        o = {"t": t, "charge": None, "next": [], "failed": [], "replace": None, "dmg": None, "proj": None, "launch": None,
             "explode": t == "Explode"}
        R = self.refs
        if t == "Charging":
            o["charge"] = [(float(k), R(v)) for k, v in (d.get("Next") or {}).items()]
            o["failed"] = R(d.get("Failed"))
            return o
        if t == "Replace":
            o["replace"] = (d.get("Var"), self.roots_of(d.get("DefaultValue")) if d.get("DefaultValue") is not None else [])
            return o
        if t in ("Chaining",):
            o["next"] = R(d.get("Next"))
            return o
        if t == "Serial":
            o["next"] = R(d.get("Interactions"))
            return o
        if t == "Parallel":
            for r in R(d.get("Interactions")):
                o["next"] += self.root_ids(r)
            return o
        if t == "Selector":
            o["next"] = (self.roots_of(d.get("HitEntity")) if d.get("HitEntity") is not None else [])
            for rule in R(d.get("HitEntityRules")):
                if isinstance(rule, dict) and rule.get("Next") is not None:
                    o["next"] += self.roots_of(rule.get("Next"))
            o["next"] += (self.roots_of(d.get("HitBlock")) if d.get("HitBlock") is not None else []) + R(d.get("Next"))
            o["failed"] = R(d.get("Failed"))
            return o
        if t == "Repeat":
            o["next"] = (self.roots_of(d.get("ForkInteractions")) if d.get("ForkInteractions") is not None else []) + R(d.get("Next"))
            o["failed"] = R(d.get("Failed"))
            return o
        if t == "DamageEntity":
            ang = [a for a in (d.get("AngledDamage") or []) if isinstance(a, dict)]
            tgt = dict((k, v) for k, v in (d.get("TargetedDamage") or {}).items() if isinstance(v, dict))
            o["dmg"] = (d.get("DamageCalculator"), [a.get("DamageCalculator") for a in ang],
                        dict((k, v.get("DamageCalculator")) for k, v in tgt.items()))
            o["next"] = R(d.get("Next"))
            for a in ang:
                o["next"] += R(a.get("Next"))
            for v in tgt.values():
                o["next"] += R(v.get("Next"))
            o["failed"] = R(d.get("Failed")) + R(d.get("Blocked"))
            return o
        if t == "Projectile":
            o["proj"] = d.get("Config")
        elif t == "LaunchProjectile":
            o["launch"] = d.get("ProjectileId")
        if t is None and "Interactions" in d:           # an inline root used where an interaction is expected
            o["next"] = R(d.get("Interactions"))
            return o
        for k in ("Interactions", "ForkInteractions"):
            if d.get(k) is not None:
                o["next"] += self.roots_of(d.get(k))
        o["next"] += R(d.get("Next"))
        o["failed"] = R(d.get("Failed")) + R(d.get("Blocked"))
        return o

    def pcfg_hit(self, cfg):
        """ProjectileConfig id / inline -> (config key, ProjectileHit interaction refs)"""
        cd = None
        if isinstance(cfg, str) and cfg in self.pcfg:
            cd = self.resolve_parent(self.js(self.pcfg[cfg]) or {}, self.pcfg)
        elif isinstance(cfg, dict):
            cd = self.resolve_parent(cfg, self.pcfg)
        if not cd:
            return []
        hit = (cd.get("Interactions") or {}).get("ProjectileHit")
        return self.root_ids(hit) if hit is not None else []

    def label(self, parent, tag):
        if tag is None:
            return parent
        if tag[0] == "charge":
            s, mx = tag[1], tag[2]
            if s <= 0:
                return self.NORMAL
            return s if s >= mx - 1e-4 else self.PARTIAL
        if tag[0] == "failed":
            return self.NORMAL
        return parent

    def walk_item(self, iid):
        """records: {kind: dmg | launch | explode | deep, lab, cls, sub, sig, key, pid, path}; None = no such item"""
        it = self.item(iid)
        if it is None:
            return None
        vars_ = it.get("InteractionVars") or {}
        recs = []
        for t, root in (it.get("Interactions") or {}).items():
            sig = t in self.SIG_TYPES
            for r in self.root_ids(root):
                self._walk(r, self.NORMAL, None, vars_, recs, [t], sig, 0, frozenset())
        return recs

    def _walk(self, ref, label, tag, vars_, recs, path, sig, depth, onpath):
        iid, d, key = self.interaction(ref)
        if d is None:
            return
        if depth > 80:
            recs.append({"kind": "deep", "lab": label, "path": list(path), "sig": sig})
            return
        if iid is not None and iid in onpath:
            return
        lab = self.label(label, tag)
        onp = onpath | {iid} if iid else onpath
        p2 = path + [iid or "<%s>" % d.get("Type")]
        o = self.norm(d)

        def W(r, tg=None, lb=None):
            self._walk(r, lab if lb is None else lb, tg, vars_, recs, p2, sig, depth + 1, onp)
        if o["charge"] is not None:
            mx = max([k for k, _v in o["charge"]] or [0.0])
            for k, rs in o["charge"]:
                for r in rs:
                    W(r, ("charge", k, mx))
            for r in o["failed"]:
                W(r, ("failed",))
            return
        if o["replace"] is not None:
            var, dflt = o["replace"]
            if var in vars_:
                v = vars_[var]
                rs = self.root_ids(v)
            else:
                rs = dflt
            for r in rs:
                W(r)
            return
        if o["dmg"] is not None:
            calc, ang, tgt = o["dmg"]
            cl = lambda c: (c or {}).get("Class", "Unknown") if isinstance(c, dict) else "Unknown"
            if isinstance(calc, dict):              # no DamageCalculator = getDamageCalculator() null = nothing recorded (jar)
                recs.append({"kind": "dmg", "lab": lab, "cls": cl(calc), "sub": None, "sig": sig, "key": key + (None,), "path": p2})
            for i, c in enumerate(ang):
                if isinstance(c, dict):
                    recs.append({"kind": "dmg", "lab": lab, "cls": cl(c), "sub": "angled%d" % i, "sig": sig, "key": key + ("a%d" % i,), "path": p2})
            for k, c in tgt.items():
                if isinstance(c, dict):
                    recs.append({"kind": "dmg", "lab": lab, "cls": cl(c), "sub": "targeted:" + k, "sig": sig, "key": key + ("t:" + k,), "path": p2})
        if o["launch"] is not None:
            recs.append({"kind": "launch", "lab": lab, "pid": o["launch"], "sig": sig, "key": ("pid", o["launch"]), "path": p2})
        if o["explode"]:
            recs.append({"kind": "explode", "lab": lab, "sig": sig, "path": p2})
        if o["proj"] is not None:
            for r in self.pcfg_hit(o["proj"]):
                self._walk(r, lab, None, vars_, recs, p2 + ["[hit %s]" % o["proj"]], sig, depth + 1, onp)
        for r in o["next"]:
            W(r)
        for r in o["failed"]:
            W(r, ("failed",))

    # ---- per-item summary, the jar's rules (GearChgIndex.build + hasCharged)
    FULL, PART, NORM, SIGR = 1, 2, 4, 8

    def kind(self, lab):
        return self.NORM if lab == self.NORMAL else (self.PART if lab == self.PARTIAL else self.FULL)

    def summary(self, iid, trusted):
        recs = self.walk_item(iid)
        if recs is None:
            return None
        calcs, launches, deep, explode = {}, {}, False, False
        for r in recs:
            if r["kind"] == "deep":
                deep = True
            elif r["kind"] == "explode":
                explode = True
            elif r["kind"] == "dmg":
                e = calcs.setdefault(r["key"], [0, r["cls"], r["sub"], set()])
                e[0] |= self.kind(r["lab"]) | (self.SIGR if r["sig"] else 0)
                if r["lab"] > 0:
                    e[3].add(round(r["lab"], 3))
            elif r["kind"] == "launch":
                e = launches.setdefault(r["pid"], [0, set()])
                e[0] |= self.kind(r["lab"]) | (self.SIGR if r["sig"] else 0)
                if r["lab"] > 0:
                    e[1].add(round(r["lab"], 3))
        full = [k for k, e in calcs.items() if e[0] == self.FULL and e[1] != "Signature"]
        combo = [k for k, e in calcs.items() if e[0] == self.NORM and e[1] == "Charged"] if trusted else []
        lfull = [p for p, e in launches.items() if e[0] == self.FULL]
        partial = any(e[0] & self.PART for e in calcs.values()) or any(e[0] & self.PART for e in launches.values())
        return {"calcs": calcs, "launches": launches, "full": full, "combo": combo, "lfull": lfull, "partial": partial,
                "has": bool(full or combo or lfull), "deep": deep, "explode": explode, "recs": recs}
# ---- CHARGED WALKER END

# 0.1.2 Skyy's exclusions (OPEN-QUESTIONS LOCKED 2026-09-30): "Leave clubs alone" (every Weapon_Club_, the flail clubs and zombie limbs
# included), the Kunai and the Crystal Flame staff (research 0.5: no charged damage step), the Crystal Ice staff (verifier: its Ice
# hits are neither Physical / Projectile family nor a legacy spell shot, so GearHitSys never applies gear stats to them - the stat
# could never trigger). Never rolls on them, never counts on them.
# Review of 0.1.2 finding 2: the Vampire bow too - its draw is the deprecated Bow_Shoot_Charging (no Bow_Charging particles, only the
# draw animation + sound) and its 1.0 s shot is the legacy Arrow_FullCharge (Appearance Arrow_Crude, no effect), so its arrow NEVER
# glows and Skyy's bow rule ("charge damage only kicks in when the arrow starts to glow") leaves it nothing to count (self-check below).
CHG_EXCL = ["Weapon_Club_", "Weapon_Kunai", "Weapon_Staff_Crystal_Flame", "Weapon_Staff_Crystal_Ice", "Weapon_Shortbow_Vampire"]
# the pack's third-party weapon mod (PACK.md): More Crossbow Tiers 1.1.0 - its crossbows parent Template_Weapon_Crossbow and keep the
# vanilla Combo_Projectile_Damage parent, so their 3rd-bolt combo carries Hytale's Class Charged (signal A trusts these ids)
PACK_TRUST = ["Weapon_Crossbow_Adamantite", "Weapon_Crossbow_Cobalt", "Weapon_Crossbow_Mithril", "Weapon_Crossbow_Thorium"]
_MCT = {}
_MCT_ZIP = os.path.join(B.MODS_DIR, "More_Crossbow_Tiers.zip")
if os.path.isfile(_MCT_ZIP):
    with zipfile.ZipFile(_MCT_ZIP) as _z:
        for _n in _z.namelist():
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
                _MCT[os.path.basename(_n)[:-5]] = json.loads(_z.read(_n).decode("utf-8-sig"))
    assert sorted(_MCT) == sorted(PACK_TRUST), "More Crossbow Tiers items changed: %s" % sorted(_MCT)
    for _i, _d in _MCT.items():
        assert _d.get("Parent") == "Template_Weapon_Crossbow", _i
        _cv = (_d.get("InteractionVars") or {}).get("Combo_Projectile_Damage")
        assert _cv is None or all((isinstance(_x, dict) and _x.get("Parent") == "Weapon_Crossbow_Damage_Combo_Projectile") or
                                  _x == "Weapon_Crossbow_Damage_Combo_Projectile" for _x in _cv.get("Interactions", [])), _i
else:
    print("note: More_Crossbow_Tiers.zip not in the Mods folder - the baked pack list (PACK.md, 1.1.0) is used unchecked")
CW = AzWalker(AZ, AZ_NAMES, _MCT)
VANILLA_WEAPONS = sorted(i for i in CW.items if i.startswith("Weapon_") and not str(CW.items[i]).startswith("overlay:"))
CHG_TRUST = sorted(set(VANILLA_WEAPONS) | set(PACK_TRUST))


def chg_excluded(i):
    return i.startswith(tuple(CHG_EXCL))


def chg_gear(i):
    """the jar's default gear rule for a Weapon_ id (GearData.isGearMs with the default gear.exclude, no gear.include)"""
    return i.startswith("Weapon_") and not az_ammo(i) and not i.startswith(tuple(_EXCL0))


CHG_SUM = dict((i, CW.summary(i, True)) for i in CHG_TRUST)
assert not [i for i, s in CHG_SUM.items() if s is None or s["deep"]], "charged walk: unreadable / too deep chains"
# the roll fallback (GearChg.FALLBACK: only when the runtime walk cannot run) and the ids with partial charge levels (never trusted
# on Hytale's Class tag alone): the same rules as the jar's GearChg.build
CHG_FALLBACK = sorted(i for i, s in CHG_SUM.items() if s["has"] and not chg_excluded(i) and chg_gear(i))
CHG_PARTIAL = sorted(i for i, s in CHG_SUM.items() if s["partial"])

# ---- self-check 1: the bow GLOW step (Skyy: "charge damage only kicks in when the arrow starts to glow")
_BCH = CW.js(CW.inter["Weapon_Shortbow_Primary_Shoot_Charge"])
_BKEYS = sorted(float(k) for k in _BCH["Next"])
assert _BCH["Type"] == "Charging" and _BKEYS == [0.0, 0.1, 0.3, 0.6, 0.9, 1.2], _BKEYS
assert [p.get("SystemId") for p in _BCH["Effects"]["Particles"]] == ["Bow_Charging"], "the draw's particle system changed"
_BPS = json.loads(AZ.read("Server/Particles/Weapon/Bow/Bow_Charging.particlesystem").decode("utf-8-sig"))
assert "tuned to appear at max charge (1.2s)" in _BPS["$Comment"] and "0.45" in _BPS["$Comment"], _BPS["$Comment"]
BOW_GLOW_S = round(min(float(_s["StartDelay"]) for _s in _BPS["Spawners"]) + 0.45, 3)
assert BOW_GLOW_S == max(_BKEYS) == 1.2, "the glow no longer appears at the full draw: %s vs %s" % (BOW_GLOW_S, max(_BKEYS))
assert _BCH["Next"]["1.2"]["Next"]["Var"] == "Primary_Shoot_Strength_4", "the 1.2 s key no longer leads to draw strength 4"
_BDMG = [CW.js(CW.inter["Weapon_Shortbow_Primary_Shoot_Damage_Strength_%d" % _k]) for _k in range(5)]
assert [d["DamageEffects"]["WorldParticles"][0]["SystemId"] for d in _BDMG] == ["Impact_Dagger_Stab"] * 4 + ["Impact_Dagger_Stab_Charged"]
assert [("TargetedDamage" in d) for d in _BDMG] == [False] * 4 + [True], "only the full draw has a headshot"
assert all(d["DamageCalculator"]["Class"] == "Charged" for d in _BDMG), "Hytale tags every draw Charged (why the glow rule is needed)"
for _k in range(5):
    _sj = CW.js(CW.inter["Weapon_Shortbow_Primary_Shoot_Strength_%d" % _k])
    assert _sj["Config"] == "Projectile_Config_Arrow_Shortbow_Strength_%d" % _k, _k
# ---- self-check 1b (review of 0.1.2 finding 2): the Vampire bow's arrow never glows -> it is in CHG_EXCL. A Hytale update that gives
# its draw particles or its full-charge arrow a different look fails the build here (then ask Skyy whether it glows now).
_VB = CW.js(CW.items["Weapon_Shortbow_Vampire"])
assert _VB["Interactions"]["Primary"] == "Bow_Shoot_Charging", "the Vampire bow's draw changed - re-check its glow (review finding 2)"
_VCH = CW.js(CW.inter["Bow_Shoot_Charging"])
assert _VCH["Type"] == "Charging" and "Particles" not in (_VCH.get("Effects") or {}), "the Vampire bow's draw got particles - does it glow now?"
assert sorted(float(k) for k in _VCH["Next"]) == [0.2, 0.6, 1.0] and _VCH["Next"]["1"]["Next"]["ProjectileId"] == "Arrow_FullCharge"
_VAR = [json.loads(AZ.read("Server/Projectiles/%s.json" % _p).decode("utf-8-sig")) for _p in ("Arrow_NoCharge", "Arrow_HalfCharge",
                                                                                                "Arrow_FullCharge")]
assert all(sorted(_a) == sorted(_VAR[0]) and _a["Appearance"] == "Arrow_Crude" and _a.get("HitParticles") == _VAR[0].get("HitParticles")
           for _a in _VAR), "the Vampire bow's full-charge arrow no longer looks like its partial ones - does it glow now?"
assert "Weapon_Shortbow_Vampire" in CHG_EXCL
# ---- self-check 2: every family's charged step as the research found it (VERIFIED 2026-09-30) + Skyy's exclusions
_AX = CW.js(CW.inter["Axe_Attack"])
assert _AX["Type"] == "Charging" and _AX["Next"].get("1.390") == "Axe_Swing_Left_Charged", "Axe_Attack changed"
assert CW.js(CW.inter["Club_Attack"])["Type"] == "Chaining", "clubs got a charged attack - ask Skyy (they said: leave clubs alone)"
assert CW.js(CW.inter["Weapon_Sword_Primary_Thrust_Damage"])["DamageCalculator"]["Class"] == "Charged"


def _fam(prefix, only_gear=True):
    return [i for i in CHG_TRUST if i.startswith(prefix) and (chg_gear(i) or not only_gear)]


# family -> (gear items, items that may roll Charged Attack Damage); a Hytale update that changes one of these fails the build here
CHG_FAMILIES = {"Weapon_Sword_": (23, 23), "Weapon_Battleaxe_": (15, 15), "Weapon_Mace_": (12, 12), "Weapon_Daggers_": (16, 16),
                "Weapon_Axe_": (13, 13), "Weapon_Longsword_": (18, 18), "Weapon_Spear_": (17, 17), "Weapon_Shortbow_": (19, 14),
                "Weapon_Crossbow_": (6, 6), "Weapon_Staff_": (24, 22), "Weapon_Wand_": (5, 3), "Weapon_Spellbook_": (6, 5),
                "Weapon_Club_": (22, 0), "Weapon_Kunai": (1, 0)}
for _p, (_ng, _nr) in CHG_FAMILIES.items():
    _g = _fam(_p)
    _r = [i for i in _g if i in CHG_FALLBACK]
    assert (len(_g), len(_r)) == (_ng, _nr), "charged family %s: %d gear / %d roll, expected %d / %d: %s" % (_p, len(_g), len(_r), _ng, _nr,
                                                                                                          sorted(set(_g) - set(_r)))
# the four prototype bows (one damage step for every draw = ambiguous) + the Vampire bow (excluded: no glow, review finding 2)
assert sorted(set(_fam("Weapon_Shortbow_")) - set(CHG_FALLBACK)) == ["Weapon_Shortbow_Bomb", "Weapon_Shortbow_Combat",
                                                                     "Weapon_Shortbow_Pull", "Weapon_Shortbow_Ricochet",
                                                                     "Weapon_Shortbow_Vampire"]
_VS = CHG_SUM["Weapon_Shortbow_Vampire"]
assert _VS["has"] and _VS["lfull"] == ["Arrow_FullCharge"], "the Vampire bow's walk changed (its excluded full-charge launch)"
assert sorted(set(_fam("Weapon_Staff_")) - set(CHG_FALLBACK)) == ["Weapon_Staff_Crystal_Flame", "Weapon_Staff_Crystal_Ice"]
assert sorted(set(_fam("Weapon_Wand_")) - set(CHG_FALLBACK)) == ["Weapon_Wand_Root", "Weapon_Wand_Stoneskin"]
assert sorted(set(_fam("Weapon_Spellbook_")) - set(CHG_FALLBACK)) == ["Weapon_Spellbook_Rekindle_Embers"]
assert all(CHG_SUM[i]["has"] for i in _fam("Weapon_Club_") if "Flail" in i or "Zombie" in i), "the flail clubs lost their charged spin"
assert not any(CHG_SUM[i]["has"] for i in _fam("Weapon_Club_") if not ("Flail" in i or "Zombie" in i)), "plain clubs got a charged step"
assert not CHG_SUM["Weapon_Kunai"]["has"] and not CHG_SUM["Weapon_Staff_Crystal_Flame"]["has"] and CHG_SUM["Weapon_Staff_Crystal_Flame"]["explode"]
assert [i for i in CHG_FALLBACK if not chg_gear(i) or chg_excluded(i)] == []
# every regular shortbow: exactly one FULL damage step (the 1.2 s glow draw, Class Charged) + its headshot, four PARTIAL draws
for _i in ("Weapon_Shortbow_Iron", "Weapon_Shortbow_Crude", "Weapon_Shortbow_Onyxium"):
    _cs = CHG_SUM[_i]["calcs"]
    _fl = sorted((e[1], e[2] or "") for e in _cs.values() if e[0] == AzWalker.FULL)
    assert _fl == [("Charged", ""), ("Unknown", "targeted:Head")], (_i, _fl)
    assert [e[3] for e in _cs.values() if e[0] == AzWalker.FULL] == [{1.2}, {1.2}], _i
    assert sorted(e[1] for e in _cs.values() if e[0] == AzWalker.PART) == ["Charged"] * 4, _i
print("charged attack walk: %d vanilla + %d pack weapons; %d may roll Charged Attack Damage; bow glow = the %.1f s draw (Bow_Charging)"
      % (len(VANILLA_WEAPONS), len(PACK_TRUST), len(CHG_FALLBACK), BOW_GLOW_S))

# ================================================================= 0.2.1: the FAMILY BASE ITEMS (spec 3.2 "one base item per family")
# K = the family base item's largest primary-attack damage entry / this item's largest entry (GearBase.ratio at run time, from the engine's
# own ItemWeapon.getBasicDamageBreakdown = WeaponDamageDataCollector over InteractionType.Primary, VERIFIED bytecode ItemModule.
# computeWeaponData; cached per id). The base of a family (the id word after Weapon_) = its Crude item, else its Wood item, else its Iron
# item (only the crossbow: vanilla has no other, spec 3.2); a family with none (Spellbook, Kunai) has no base and each item is its own
# base. An item that is its own family's base deals exactly its vanilla damage at its band start: GearBase.kOf divides by F(start) x
# bonus(start), which is 1 for the Crude / Wood bases (band start Lv 1) - the Iron crossbow (band 15) deals exactly vanilla at Lv 15
# (spec 3.2 crossbow row). Families the table lacks (other mods) find their base the same way at run time (Crude / Wood / Iron item).
BASE_GEAR = sorted(i for i in VANILLA_WEAPONS if chg_gear(i))


def base_family(i):
    r = i[len("Weapon_"):]
    return r.split("_", 1)[0]


FAM_BASE = []
for _fm in sorted(set(base_family(i) for i in BASE_GEAR)):
    _b = next(("Weapon_%s_%s" % (_fm, _m) for _m in ("Crude", "Wood", "Iron") if ("Weapon_%s_%s" % (_fm, _m)) in BASE_GEAR), None)
    if _b:
        FAM_BASE.append((_fm, _b))
assert dict(FAM_BASE) == {"Axe": "Weapon_Axe_Crude", "Battleaxe": "Weapon_Battleaxe_Crude", "Club": "Weapon_Club_Crude",
                          "Crossbow": "Weapon_Crossbow_Iron", "Daggers": "Weapon_Daggers_Crude", "Longsword": "Weapon_Longsword_Crude",
                          "Mace": "Weapon_Mace_Crude", "Shortbow": "Weapon_Shortbow_Crude", "Spear": "Weapon_Spear_Crude",
                          "Staff": "Weapon_Staff_Wood", "Sword": "Weapon_Sword_Crude", "Wand": "Weapon_Wand_Wood"}, FAM_BASE
BASE_NOFAM = sorted(set(base_family(i) for i in BASE_GEAR) - set(f for f, _b in FAM_BASE))
assert BASE_NOFAM == ["Kunai", "Spellbook"], BASE_NOFAM
# the five class kits (SkyyClasses 0.1.10) are their family's base: Lv 1, K = 1, F(1) = 1 -> exactly vanilla
for _k in ("Weapon_Wand_Wood", "Weapon_Staff_Wood", "Weapon_Sword_Crude", "Weapon_Shortbow_Crude", "Weapon_Battleaxe_Crude"):
    assert _k in dict((b, f) for f, b in FAM_BASE), _k
print("base stats: %d weapon families with a Crude / Wood / Iron base (%s); own base: %s" % (len(FAM_BASE), ", ".join(
    "%s=%s" % (f, b[len("Weapon_%s_" % f):]) for f, b in FAM_BASE), ", ".join(BASE_NOFAM)))

# ================================================================= 0.2: wand / spellbook / staff RECIPES that MATCH VANILLA WEAPONS (Q&A R1)
# Skyy (OPEN-QUESTIONS, Q&A with Skyy 2026-10-02 R1, LOCKED): "wand / spellbook / staff recipes MATCH VANILLA WEAPONS - same bench and the
# same metals / amounts as that material's other vanilla weapons (Wood, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril)".
# Assets.zip (VERIFIED by the checks below): in those materials only these magic ids exist - Weapon_Wand_Wood and Weapon_Staff_Wood /
# _Copper / _Iron / _Thorium / _Cobalt / _Adamantite / _Mithril. No spellbook is made of a material (Grimoire / Fire / Frost / Demon /
# Rekindle are their own families), no wand but Wood; the Bronze / Onyxium staffs are not in Skyy's list (and vanilla has no Bronze /
# Onyxium weapon recipe to copy); variants (Wood_Rotten, Wood_Kweebec, Bo_Wood) keep vanilla's rule "no recipe for a variant" (Iron_Rusty,
# Adamantite_Saurian ... have none). None of the 8 has a vanilla recipe.
# THE COMPARABLE VANILLA WEAPON = the SHORTBOW of the same material: the other ranged primary weapon of a class kit (Archer: the Crude
# shortbow; Mage: the Wood staff; Priest: the Wood wand) - staffs, wands and spellbooks fire projectiles like bows - and it has a recipe in
# every material Skyy listed (Crude = the Wood / Crude tier: 4 sticks + 6 fibre, all wood). Each new recipe is that bow's Recipe copied
# UNCHANGED - Input, BenchRequirement (bench ids, category = the Weapon Bench's Bow tab, RequiredTierLevel 2 for Thorium / Cobalt and 3 for
# Adamantite / Mithril, the Workbench's Survival tab for the Crude tier), TimeSeconds, KnowledgeRequired - with the magic item as its output
# (the quantity the bow makes: 1). Review of 0.2 finding 5: the ONE thing not copied is the bows' "Armory" entry (DiagramCrafting) - the
# Armory bench (Bench_Armory, Quality Developer) is a developer-only bench with a FIXED number of slots per item category (Bow: 2), so 8
# more Bow-tab recipes there is risk without benefit; every recipe keeps its real Crafting benches (asserted below).
MAGIC_DROP_BENCH = ("Armory",)
# Shipped as STANDALONE recipe assets (Server/Item/Recipes/SkyyGear/<id>.json - Hytale loads "Item/Recipes" for every asset pack, VERIFIED
# AssetRegistryLoader; the format of the vanilla Salvage recipes: Input + PrimaryOutput + Output + BenchRequirement + TimeSeconds), generated
# here from Assets.zip at build time and never committed; no vanilla item or recipe file is overridden. Crafted ones get their level like
# any craft: GearCraftSys at the bench, gear:fn:roll for SkyySacks /craft.
MAGIC_FAMILIES = ["Weapon_Wand_", "Weapon_Spellbook_", "Weapon_Staff_"]
MAGIC_MATS = [("Wood", "Crude"), ("Copper", "Copper"), ("Iron", "Iron"), ("Thorium", "Thorium"), ("Cobalt", "Cobalt"),
              ("Adamantite", "Adamantite"), ("Mithril", "Mithril")]        # Skyy's list -> the model bow's material word
MAGIC_MODEL = "Weapon_Shortbow_"
RECIPE_PREFIX = "SkyyGear_Recipe_"
RECIPE_DIR = "Server/Item/Recipes/SkyyGear/"
RECIPE_KEYS = ("Input", "BenchRequirement", "TimeSeconds", "KnowledgeRequired", "OutputQuantity", "RequiredMemoriesLevel")
_ALL_RECIPE_IDS = set()           # every recipe id Assets.zip defines: item recipes (<item>_Recipe_Generated_0) + standalone files
_RECIPE_OUTS = {}                 # output item id -> vanilla recipe ids that make it
for _i, _d in _AZ_JSON.items():
    if isinstance(_d, dict) and isinstance(_d.get("Recipe"), dict):
        _ALL_RECIPE_IDS.add(_i + "_Recipe_Generated_0")
        _RECIPE_OUTS.setdefault(_i, []).append(_i + "_Recipe_Generated_0")
_SALVAGE_IN = set()
for _n in AZ_NAMES:
    if _n.startswith("Server/Item/Recipes/") and _n.endswith(".json"):
        _rid = os.path.basename(_n)[:-5]
        _ALL_RECIPE_IDS.add(_rid)
        try:
            _rd = json.loads(AZ.read(_n).decode("utf-8-sig"))
        except Exception:
            continue
        for _o in ([_rd.get("PrimaryOutput")] if isinstance(_rd.get("PrimaryOutput"), dict) else []) + list(_rd.get("Output") or []):
            if isinstance(_o, dict) and _o.get("ItemId"):
                _RECIPE_OUTS.setdefault(_o["ItemId"], []).append(_rid)
        for _x in _rd.get("Input") or []:
            if isinstance(_x, dict) and _x.get("ItemId"):
                _SALVAGE_IN.add(_x["ItemId"])
_BENCHES = {}                     # bench id -> {"type": ..., "cats": set of category ids (DiagramCrafting: "<cat>.<item category>")}
for _i, _d in _AZ_JSON.items():
    _b = (_d.get("BlockType") or {}).get("Bench") if isinstance(_d, dict) and isinstance(_d.get("BlockType"), dict) else None
    if isinstance(_b, dict) and _b.get("Id"):
        _cs = set()
        for _c in _b.get("Categories") or []:
            if isinstance(_c, dict) and _c.get("Id"):
                _cs.add(_c["Id"])
                for _ic in _c.get("ItemCategories") or []:
                    if isinstance(_ic, dict) and _ic.get("Id"):
                        _cs.add(_c["Id"] + "." + _ic["Id"])
        _BENCHES.setdefault(_b["Id"], {"type": _b.get("Type"), "cats": set()})["cats"] |= _cs
MAGIC_RECIPES = []                # (recipe id, output id, model id, recipe dict)
for _fam in MAGIC_FAMILIES:
    for _mat, _mm in MAGIC_MATS:
        _out = _fam + _mat
        if _out not in AZ_ITEMS:
            continue
        _model = MAGIC_MODEL + _mm
        _mr = az_get(_model, "Recipe")
        assert isinstance(_mr, dict), "the model bow %s has no recipe any more" % _model
        assert set(_mr) <= set(RECIPE_KEYS), "the model recipe of %s has keys this build does not copy: %s" % (_model, sorted(set(_mr) - set(RECIPE_KEYS)))
        _q = int(_mr.get("OutputQuantity", 1))
        _r = {"Input": json.loads(json.dumps(_mr["Input"])),
              "PrimaryOutput": {"ItemId": _out, "Quantity": _q},
              "Output": [{"ItemId": _out, "Quantity": _q}]}
        for _k in ("BenchRequirement", "TimeSeconds", "KnowledgeRequired", "RequiredMemoriesLevel"):
            if _k in _mr:
                _r[_k] = json.loads(json.dumps(_mr[_k]))
        if "BenchRequirement" in _r:          # review of 0.2 finding 5: the developer-only Armory entry is not copied
            _r["BenchRequirement"] = [_b for _b in _r["BenchRequirement"] if _b.get("Id") not in MAGIC_DROP_BENCH]
        assert any(_b.get("Type") == "Crafting" for _b in _r.get("BenchRequirement") or []), "%s: no Crafting bench left after the Armory drop" % _out
        MAGIC_RECIPES.append((RECIPE_PREFIX + _out, _out, _model, _r))
assert [o for _rid, o, _m, _r in MAGIC_RECIPES] == ["Weapon_Wand_Wood", "Weapon_Staff_Wood", "Weapon_Staff_Copper", "Weapon_Staff_Iron",
                                                     "Weapon_Staff_Thorium", "Weapon_Staff_Cobalt", "Weapon_Staff_Adamantite",
                                                     "Weapon_Staff_Mithril"], \
    "the magic ids per material changed in Assets.zip (a new wand / spellbook / staff material?) - check Skyy's R1 list: %s" % [o for _r, o, _m, _x in MAGIC_RECIPES]
assert not any(i.startswith("Weapon_Spellbook_") and i.split("_")[2] in dict(MAGIC_MATS) for i in AZ_ITEMS), "a material spellbook appeared"
for _rid, _out, _model, _r in MAGIC_RECIPES:
    assert _out not in _RECIPE_OUTS, "%s has a vanilla recipe now (%s) - a second one would be a duplicate" % (_out, _RECIPE_OUTS.get(_out))
    assert _rid not in _ALL_RECIPE_IDS, "recipe id %s is taken by Assets.zip" % _rid
    assert _out not in _SALVAGE_IN, "a vanilla recipe takes %s as input (salvage) - check for a craft / salvage loop first" % _out
    assert chg_gear(_out) and band_lookup(BD_ALL, _out)[0] is not None, "%s must be gear with a level band" % _out
    for _x in _r["Input"]:
        assert ("ItemId" in _x) != ("ResourceTypeId" in _x) and int(_x["Quantity"]) > 0, _x
        assert _x.get("ItemId") is None or _x["ItemId"] in AZ_ITEMS, "unknown input item %s" % _x
        assert _x.get("ResourceTypeId") is None or ("Server/Item/ResourceTypes/%s.json" % _x["ResourceTypeId"]) in AZ_NAMES, "unknown resource type %s" % _x
    for _br in _r.get("BenchRequirement") or []:
        assert _br.get("Id") in _BENCHES and _br.get("Type") == _BENCHES[_br["Id"]]["type"], "unknown bench %s" % _br
        assert all(_c in _BENCHES[_br["Id"]]["cats"] for _c in _br.get("Categories") or []), "a category the bench %s does not have: %s" % (_br["Id"], _br)
assert len(set(r[0] for r in MAGIC_RECIPES)) == len(MAGIC_RECIPES)
assert not [o for _rid, o, _m, r in MAGIC_RECIPES for b in r.get("BenchRequirement") or [] if b.get("Id") in MAGIC_DROP_BENCH], "an Armory entry was copied"
assert [_m for _rid, _o, _m, _r in MAGIC_RECIPES if any(b.get("Id") == "Armory" for b in az_get(_m, "Recipe").get("BenchRequirement") or [])] \
    == ["Weapon_Shortbow_Crude", "Weapon_Shortbow_Crude", "Weapon_Shortbow_Copper", "Weapon_Shortbow_Iron", "Weapon_Shortbow_Thorium",
        "Weapon_Shortbow_Cobalt", "Weapon_Shortbow_Adamantite"], "which vanilla bows carry the Armory entry changed - check the drop"
# the benches a player really crafts them at: the Weapon Bench's Bow tab (tier 2 for Thorium / Cobalt, 3 for Adamantite / Mithril) and the
# Workbench's Survival tab for the Wood ones (the Crude bow's own benches)
_wb = dict((o, [(b["Id"], tuple(b.get("Categories") or []), b.get("RequiredTierLevel", 1)) for b in r.get("BenchRequirement") or [] if b.get("Type") == "Crafting"])
           for _rid, o, _m, r in MAGIC_RECIPES)
assert _wb["Weapon_Staff_Copper"] == [("Weapon_Bench", ("Weapon_Bow",), 1)] and _wb["Weapon_Staff_Thorium"] == [("Weapon_Bench", ("Weapon_Bow",), 2)]
assert _wb["Weapon_Staff_Mithril"] == [("Weapon_Bench", ("Weapon_Bow",), 3)]
assert sorted(_wb["Weapon_Wand_Wood"]) == [("Weapon_Bench", ("Weapon_Bow",), 1), ("Workbench", ("Workbench_Survival",), 1)]
for _rid, _out, _model, _r in MAGIC_RECIPES:
    print("0.2 recipe %-34s <- %-26s %s | %s | %ss" % (_rid, _model, ", ".join("%s x%s" % (_x.get("ItemId") or "[" + _x["ResourceTypeId"] + "]", _x["Quantity"]) for _x in _r["Input"]),
                                                    "; ".join("%s %s%s" % (b["Id"], "/".join(b.get("Categories") or []), " T%d" % b["RequiredTierLevel"] if b.get("RequiredTierLevel") else "")
                                                              for b in _r.get("BenchRequirement") or []), _r.get("TimeSeconds", 0)))
    EXTRA[RECIPE_DIR + _rid + ".json"] = json.dumps(_r, indent=2)
assert not [k for k in EXTRA if k.startswith("Server/Item/Items/")], "no vanilla item file is ever overridden"

# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"
CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("combat", "Combat"), ("migrate", "Migration")]
PH = " Placeholder - Skyy tunes this."
STAT_LEGEND = "dmg Damage, str Strength, mp Magical Power, cc/cd Crit Chance/Damage, tdmg True Damage, def Defense"
assert len(STAT_LEGEND) <= 100, len(STAT_LEGEND)
_rch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:6])
_mch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:5])
CFG_ROWS = [
    # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.gate", "Level requirement check", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear above your level blocks hits and gives no stats. Off = every level passes.", "field:GearCfg.PART_GATE"),
    ("part.stats", "Gear stats in combat", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear modifiers change damage, defence, regen and speed. Off = they are only shown.", "field:GearCfg.PART_STATS"),
    ("part.craft", "Roll crafted gear", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Crafted weapons and armor roll a rarity and modifiers. Off = crafted gear is Normal.", "field:GearCfg.PART_CRAFT"),
    ("part.drops", "Unidentified mob drops", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear dropped by mobs is unidentified with a rarity. Off = mob gear drops Normal.", "field:GearCfg.PART_DROPS"),
    ("part.chests", "Unidentified chest loot", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear in world chests (loot tables + first open) is unidentified. Off = chest gear is Normal.", "field:GearCfg.PART_CHESTS"),
    # 0.2 (spec 9): the master switch of the per-item levels (off = 0.1.3: nothing new is stamped, the table's start level only)
    ("part.levels", "Levels stored on items", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "New gear stores its level (crafts at your skill level). Off = no new stamps, band start levels.", "field:GearCfg.PART_LEVELS"),
    ("identify.command", "/identify command", "general", "bool", "true", "", "", "", "", "live",
     "Players open the Identify page with /identify (switch off when an NPC does it).", "field:GearCfg.IDENTIFY_CMD"),
    ("gear.exclude", "Weapon prefixes that are not gear", "general", "text", EXCLUDE_DEF, "0", "2000", "", "", "live,adv",
     "Comma list of Weapon_ id prefixes that never get rarity or level (shields, bombs, guns ...).",
     "field:GearCfg.EXCLUDE"),
    # design review 1: later stages (Equipment, gathering gear, Skyy_ items) opt in here instead of a code edit. Follow-up review 1:
    # the check refuses prefixes under 6 characters and the bare families (GearCfg.inclBad; the loader drops them from hand edits)
    ("gear.include", "Extra id prefixes that are gear", "general", "text", "", "0", "2000", "", "", "live,adv",
     "Comma list of id prefixes (6+ letters, e.g. Skyy_Ring_) that count as gear too. Bags never are.",
     "field:GearCfg.INCLUDE;check=GearCfg.checkInclude"),
    ("kind.prefix", "Gear kind by id prefix", "general", "table", "", "", "20", "text;type;Kind", "", "live,adv",
     "combat, mining, foraging, farming or equipment: picks the pool + gate skill. Longest prefix wins.",
     "reload@%s:kind.prefix.;check=GearCfg.checkKind" % CFG_FILE),
    ("ui.frames", "Vanilla frames on gear pages", "general", "bool", "true", "", "", "", "", "live,adv",
     "Reforge and Identify use the game's own frame textures and sounds. Off = flat colours.", "field:GearCfg.UI_FRAMES"),
    # 0.1.1: Skyy's lock (OPEN-QUESTIONS 2026-09-30) - default off, so the help carries no Placeholder claim (like level.material)
    ("pool.later", "Roll coming-later stats", "stats", "bool", "false", "", "", "", "", "live",
     "Off (Skyy, 2026-09-30) = stats that do nothing yet never roll. On = they may roll, shown grey.", "field:GearCfg.POOL_LATER"),
    ("rarity", "Modifiers and roll power by rarity", "rarity", "table", "", "0", "1000", "int;none;Mods|Low %|High %", "",
     "live,danger", "Modifier count per rarity and roll power in % of the stat max." + PH,
     "reload@%s:rarity.;check=GearCfg.checkRarity" % CFG_FILE),
    # design review 7: the help is a legend of the short keys (every key with its name sits above its line in config.properties)
    ("stat", "Stat max and weight", "stats", "table", "", "0", "100000", "int;none;Max at 100%|Weight", "", "live,danger",
     STAT_LEGEND, "reload@%s:stats.;check=GearCfg.checkStat" % CFG_FILE),
    ("stat.levelFloor", "Modifier power at item level 0", "stats", "int", "25", "1", "100", "", "%", "live,danger",
     "Level-0 gear rolls at this % of full power (100 = no level scaling)." + PH, "field:GearCfg.LEVEL_FLOOR"),
    # 0.1.1: 40 = the top material level (Mithril / Onyxium); a picked default (OPEN-QUESTIONS), still a placeholder to tune
    ("stat.levelFull", "Item level with full modifier power", "stats", "int", "40", "1", "100", "", "", "live,danger",
     "Gear this level or higher rolls at full power (40 = Mithril)." + PH, "field:GearCfg.LEVEL_FULL"),
    ("odds", "Rarity odds (weights)", "drops", "table", "", "0", "1000000", "dec;none;Craft|Mob|Chest", "", "live,danger",
     "Weights per rarity for crafted gear, mob drops and loot chests." + PH,
     "reload@%s:odds.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("smith.perLevel", "Smithing rarity per level", "drops", "dec", "0.5", "0", "100", "", "%", "live,danger",
     "Chance per Smithing level that a crafted item steps up one rarity." + PH, "field:GearCfg.SMITH_PER"),
    ("smith.cap", "Smithing rarity cap", "drops", "dec", "50", "0", "100", "", "%", "live,danger",
     "The Smithing step-up chance never goes above this." + PH, "field:GearCfg.SMITH_CAP"),
    ("craft.maxRarity", "Best rarity from crafting", "drops", "choice", "fabled", "", "", _rch, "", "live,danger",
     "Crafting (Smithing included) never makes a better rarity than this." + PH, "field:GearCfg.CRAFT_MAX"),
    # 0.2 (spec 4 + 9): the level a craft stamps
    ("craft.levelFrom", "Crafted gear level from", "drops", "choice", "gate", "", "", "gate|Your skill,band|Band start", "", "live",
     "Your skill = the crafter's gate skill level (class skill, Mining ...) kept inside the band.", "field:GearCfg.CRAFT_FROM"),
    ("craft.belowBand", "Crafting below a band", "drops", "choice", "min", "", "", "min|Make at band start,block|Refuse", "", "live",
     "Below a material's band: make it at the band start, or refuse the craft (vanilla benches).", "field:GearCfg.CRAFT_BELOW"),
    ("craft.weaponSkill", "Craft level skill by prefix", "drops", "text", "", "0", "2000", "", "", "live,adv",
     "Optional prefix:Skill list (Weapon_Shortbow_:Archery). Empty = the item's gate skill.",
     "field:GearCfg.CRAFT_SKILL;check=GearCfg.checkCraftSkill"),
    # 0.2 (spec 2 + 9): the table gains a Cap column (Skyy: keep the table with a +3 overlap); one number still works = the width rule
    ("level.material", "Level by material", "levels", "table", "", "0", "100", "int;type;Min|Cap", "", "live",
     "Band by the first id word (Leather_Soft = 2 words). One number = N to N+width-1. Skyy 10-01.",
     "reload@%s:level.material.;check=GearCfg.checkBand" % CFG_FILE),
    ("level.bandWidth", "Band width for one-number rows", "levels", "int", str(BAND_W_DEF), "1", "50", "", "", "live,danger",
     "A row with one number covers N to N+width-1 (8 = 5 levels + 3 overlap), never past 49.", "field:GearCfg.BAND_W"),
    # review of 0.2 finding 6: danger (confirm on change) like level.bandWidth - 100 makes every gear item usable, 0 blocks the Lv 1 kits
    ("level.gateFloor", "Lowest skill level for gear", "levels", "int", str(GATE_FLOOR_DEF), "0", "100", "", "", "live,danger",
     "A skill below this counts as this for gear, so Lv 1 kits work at skill 0 (0 = off).", "field:GearCfg.GATE_FLOOR"),
    ("level.item", "Level by item", "levels", "table", "", "0", "100", "int;held;Level", "", "live",
     "Level needed for one exact item (hold it to add). Wins over the material table.",
     "reload@%s:level.item.;entry=item" % CFG_FILE),
    ("level.vanilla", "Use Hytale item level otherwise", "levels", "bool", "true", "", "", "", "", "live",
     "Gear without a table entry uses the game's own item level (0-100).", "field:GearCfg.LEVEL_VANILLA"),
    ("level.default", "Level when nothing matches", "levels", "int", "0", "0", "100", "", "", "live",
     "Level for gear that matches no table and has no Hytale level.", "field:GearCfg.LEVEL_DEFAULT"),
    ("level.noSkills", "Without SkyySkills", "levels", "choice", "pass", "", "", "pass|Allow all,block|Block", "", "live",
     "When SkyySkills is missing the level cannot be checked: allow all gear or block it.", "field:GearCfg.NO_SKILLS"),
    ("level.armorNative", "Under-level armor loses Hytale stats", "levels", "bool", "true", "", "", "", "", "live",
     "Under-level armor loses its Health + protection (off = mods only)." + PH,
     "field:GearCfg.ARMOR_NATIVE"),
    # 0.2.1 (spec 3 + 9, stages 2 + 3): the item's level sets its base stats. part.base = the part switch of both stages (its own switch:
    # never inside part.stats, spec 3.5 item 2); base.mode / base.curve / base.matBonus = weapon damage; base.armorOn / base.resCurve /
    # base.armor = armor. Every number is live (field rows + a reload table); the tooltips re-render on the config epoch.
    ("part.base", "Level sets base stats", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Weapon damage and armor Health / resistance grow with the item's level. Off = vanilla stats.", "field:GearCfg.PART_BASE"),
    ("base.mode", "Weapon damage by level", "base", "choice", "shape", "", "", "shape|Level x vanilla,off|Vanilla damage", "",
     "live,danger", "Level x vanilla = each vanilla hit x K x F(level) x material bonus. Off = vanilla damage.",
     "field:GearCfg.BASE_MODE"),
    ("base.curve", "Level curve F(L)", "base", "text", BASE_CURVE_DEF, "3", "300", "", "", "live,danger",
     "level:factor points, straight lines between. Damage + armor Health." + PH,
     "field:GearCfg.BASE_CURVE;check=GearCfg.checkCurve"),
    ("base.matBonus", "Better material bonus", "base", "dec", repr(BASE_MAT_DEF), "0", "10", "", "%", "live,danger",
     "% per level the band starts at (Copper 10 = +3%); Lv 1 bands none." + PH, "field:GearCfg.BASE_MAT"),
    ("base.armorOn", "Armor stats by level", "base", "bool", "true", "", "", "", "", "live,danger",
     "Worn armor's Health + resistance come from its level and slot. Off = vanilla armor values.", "field:GearCfg.BASE_ARMOR"),
    ("base.resCurve", "Armor resistance curve R(L)", "base", "text", BASE_RES_DEF, "3", "300", "", "", "live,danger",
     "level:factor points for Physical / Projectile resistance." + PH,
     "field:GearCfg.BASE_RES;check=GearCfg.checkCurve"),
    ("base.armor", "Lv 1 armor stats by slot", "base", "table", "", "0", "1000", "dec;none;Health|Resist %", "", "live,danger",
     "Lv 1 Health + resistance % of Head, Chest, Legs, Hands (Copper row)." + PH,
     "reload@%s:base.armor.;check=GearCfg.checkArmorBase" % CFG_FILE),
    ("cost.reforge", "Reforge cost", "costs", "table", "", "0", "1000000000000", "int;none;Base|Per level", "coins",
     "live,danger", "Coins per reforge by rarity: base + per level x item level." + PH,
     "reload@%s:cost.reforge.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("cost.identify", "Identify cost", "costs", "table", "", "0", "1000000000000", "int;none;Base|Per level", "coins",
     "live,danger", "Coins per identify by rarity: base + per level x item level." + PH,
     "reload@%s:cost.identify.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("xp.reforge", "Smithing XP per reforge", "costs", "table", "", "0", "100000", "int;none;XP", "", "live,danger",
     "Smithing XP a reforge gives, by rarity (SkyySkills caps apply)." + PH,
     "reload@%s:xp.reforge.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("reforge.names", "Reforge names", "costs", "text", REFORGE_NAMES_DEF, "0", "2000", "", "", "live",
     "Comma list of cosmetic reforge prefixes. Never a rarity name.", "field:GearCfg.NAMES;check=GearCfg.checkNames"),
    ("combat.strPer", "Damage per Strength", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Strength point adds this % to physical hits." + PH, "field:GearCfg.STR_PER"),
    ("combat.mpPer", "Spell damage per Magical Power", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Magical Power point adds this % to spell hits." + PH, "field:GearCfg.MP_PER"),
    ("combat.defScale", "Defense curve (100 = SkyBlock)", "combat", "int", "100", "1", "100000", "", "", "live,danger",
     "Damage taken x scale / (scale + Defense)." + PH, "field:GearCfg.DEF_SCALE"),
    ("crit.base", "Base Crit Chance", "combat", "dec", "0", "0", "1000", "", "%", "live,danger",
     "Crit Chance every player has without gear." + PH, "field:GearCfg.CRIT_BASE"),
    ("crit.baseDamage", "Base Crit Damage", "combat", "dec", "0", "0", "10000", "", "%", "live,danger",
     "Crit Damage every player has without gear (a crit doubles first)." + PH, "field:GearCfg.CRIT_BASE_DMG"),
    ("steal.windowS", "Life / Mana Steal window", "combat", "int", "3", "1", "60", "", "s", "live",
     "Life Steal and Mana Steal pay out at most once per this many seconds.", "field:GearCfg.STEAL_S"),
    ("regen.periodMs", "Regen tick", "combat", "int", "2000", "250", "60000", "", "ms", "live",
     "Health Regen and Stamina Regen from gear apply once per this many ms." + PH, "field:GearCfg.REGEN_MS"),
    ("speed.per", "Speed per point", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Speed point adds this % of the default walk speed." + PH, "field:GearCfg.SPEED_PER"),
    # 0.1.2 Charged Attack Damage (OPEN-QUESTIONS LOCKED 2026-09-30). Off = the stat does nothing, so it also leaves the roll pool
    # (Skyy's lock); items that already have it keep the line, shown grey "(off on this server)". 0.15 is Skyy's own number.
    ("charged.on", "Charged Attack Damage in combat", "combat", "bool", "true", "", "", "", "", "live",
     "Charged Attack Damage boosts fully charged hits. Off = it does nothing and never rolls.", "field:GearCfg.CHG_ON"),
    ("charged.spellFactor", "Charged bonus on spells", "combat", "dec", "0.15", "0", "1", "", "x", "live,danger",
     "Spells get this share of Charged Attack Damage: 0.15 = a +100% roll gives spells +15% (Skyy).", "field:GearCfg.CHG_SPELL"),
    ("charged.log", "Log charged hits", "combat", "bool", "false", "", "", "", "", "live,adv",
     "One gear.log line per judged hit (charged or not, and why). For testing; /gear charged shows it.", "field:GearCfg.CHG_LOG"),
    ("migrate.by", "Old SkyyRolls rarity from", "migrate", "choice", "stats", "", "",
     "stats|Roll strength,roll|Roll quality,item|Item colour", "", "new,danger",
     "How an old SkyyRolls item gets its rarity on the move (stats = how strong its rolls are).",
     "field:GearCfg.MIGRATE_BY"),
    ("migrate.map", "Score needed per rarity", "migrate", "table", "", "0", "100", "int;none;Min score %", "", "new,danger",
     "Old SkyyRolls score (0-100) needed for each rarity; lower = Normal." + PH,
     "reload@%s:migrate.map.;check=GearCfg.checkMigKey" % CFG_FILE),
    ("migrate.maxRarity", "Best rarity for old SkyyRolls items", "migrate", "choice", "fabled", "", "", _mch, "", "new,danger",
     "Old SkyyRolls items move over no better than this (never Mythic/Set)." + PH, "field:GearCfg.MIGRATE_MAX"),
    # exploit review 5 (policy): off = the LOCKED "rolled items keep their rolls"; on = each value capped at the best roll its new
    # rarity can make at the item's level (GearRoll.bounds high end)
    ("migrate.clampToLevel", "Cap old rolls at the new roll range", "migrate", "bool", "false", "", "", "", "", "new,danger",
     "Off = old SkyyRolls values stay (locked). On = each is capped at the top roll of its rarity + level.",
     "field:GearCfg.MIGRATE_CLAMP"),
]
_bad = ["%s help %d" % (_r[0], len(_r[10])) for _r in CFG_ROWS if len(_r[10]) > 100] +        ["%s label %d" % (_r[0], len(_r[1])) for _r in CFG_ROWS if len(_r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
# spec 9.2: every row on the LOCKED confirm list carries danger (money, rates, caps, curves, part switches)
_DANGER = {"part.gate", "part.stats", "part.craft", "part.drops", "part.chests", "rarity", "stat", "stat.levelFloor", "stat.levelFull",
           "odds", "smith.perLevel", "smith.cap", "craft.maxRarity", "cost.reforge", "cost.identify", "xp.reforge", "combat.strPer",
           "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "speed.per", "migrate.by", "migrate.map",
           "migrate.maxRarity", "migrate.clampToLevel", "charged.spellFactor",
           # 0.2: a part switch, and the width that sets the caps of every one-number band row (caps are on the LOCKED confirm list);
           # review of 0.2 finding 6: the gate floor (100 = every gear item usable)
           "part.levels", "level.bandWidth", "level.gateFloor",
           # 0.2.1: a part switch, a mode switch, two curves, a rate and a stat table (all change combat numbers)
           "part.base", "base.mode", "base.curve", "base.matBonus", "base.armorOn", "base.resCurve", "base.armor"}
for _r in CFG_ROWS:
    assert (("danger" in _r[9].split(",")) == (_r[0] in _DANGER)), "danger flag mismatch: " + _r[0]
# design review 10: these help lines carry the Placeholder suffix too (0.1.1: pool.later left the list - its default is Skyy's lock
# now, and a Placeholder claim on it would be wrong)
for _r in CFG_ROWS:
    if _r[0] in ("craft.maxRarity", "migrate.maxRarity", "regen.periodMs", "level.armorNative"):
        assert _r[10].endswith(PH), "missing the Placeholder suffix: " + _r[0]
    if _r[0] == "pool.later":
        assert "Placeholder" not in _r[10] and "Skyy, 2026-09-30" in _r[10], "pool.later help: Skyy's lock, no Placeholder claim"
# 0.1.1 stat defaults: the row defaults are the new texts
for _k, _o, _n, _w in ST_DEFAULTS:
    assert [_r[4] for _r in CFG_ROWS if _r[0] == _k] == [_n], "row default of %s must be %s" % (_k, _n)
assert "(spec" not in "".join(_r[10] for _r in CFG_ROWS)


def _dn(x):
    return str(int(x)) if float(x) == int(x) else repr(float(x))


def default_text():
    L = ["# SkyyGear %s - Server Setup -> Gear (SkyWynn Menu, /modconfig). Every number is a PLACEHOLDER Skyy tunes in game." % VERSION,
         "# Changed in game: only the changed line is rewritten, logged in config-changes.log and versioned in config-history/.",
         "# Hand edits apply on Reload in Server Setup or at the next start. Tables: <prefix><entry>=<col1>,<col2>,...", ""]
    rows = dict((r[0], r) for r in CFG_ROWS)
    def scal(k):
        L.append("# %s: %s" % (rows[k][1], rows[k][10]))
        L.append("%s=%s" % (k, rows[k][4]))
    L.append("# ---- general ----")
    for k in ("part.gate", "part.stats", "part.craft", "part.drops", "part.chests", "identify.command", "gear.exclude", "gear.include",
              "ui.frames"):
        scal(k)
    L += ["# ---- kind.prefix.<id prefix>=<combat|mining|foraging|farming|equipment> (Gear kind by id prefix; none by default:",
          "#      Weapon_ / Armor_ = combat, SkyyRolls tools by family). Example: kind.prefix.Skyy_Ring_=equipment ----"]
    L += ["", "# ---- rarity: rarity.<id>=<modifiers>,<low %>,<high %> (spec 2.2) ----"]
    for r in R_IDS:
        L.append("rarity.%s=%d,%d,%d" % ((r,) + RARITY_DEF[r]))
    L += ["", "# ---- stats: stats.<key>=<max at 100 % power>,<weight> (spec 4.2; weight 0 = never rolls); the line above each"
          " names it ----"]
    _where = {"w": "weapon", "s": "spell weapon", "a": "armor", "e": "Equipment"}
    for s in STATS:
        L.append("# %s = %s (%s%s%s)" % (s[0], s[1], ", ".join(_where[c] for c in s[2]), ", %" if s[3] == "%" else "",
                                        "" if s[6] else ", coming later"))
        L.append("stats.%s=%d,%d" % (s[0], s[4], s[5]))
    L.append(ST_MARK)          # 0.1.1: the stat defaults marker right above the pool.later help line (a fresh file never updates)
    for k in ("pool.later", "stat.levelFloor", "stat.levelFull"):
        scal(k)
    L += ["", "# ---- odds: odds.<id>=<craft>,<mob>,<chest> (weights, spec 5.3 / 5.5) ----"]
    for r in R_IDS:
        L.append("odds.%s=%s" % (r, ",".join(_dn(x) for x in ODDS_DEF[r])))
    for k in ("smith.perLevel", "smith.cap", "craft.maxRarity"):
        scal(k)
    L += ["", LV_HEAD, LV_MARK]
    for t, s, c in BANDS:      # 0.2: <min>,<cap> bands (Armor_Copper right after Copper)
        L.append("level.material.%s=%s" % (t, band_text(s, c)))
    L.append(FM_MARK)          # 0.1.3: the family rows right under the metals, under their marker (a fresh file never updates)
    for t, s, c in FAM_BANDS:
        L.append("level.material.%s=%s" % (t, band_text(s, c)))
    L.append(BD_MARK)          # 0.2: the bands marker + the new level settings right under the last band row (a fresh file never updates)
    for k in BD_ROWK:
        scal(k)
    for k in ("level.vanilla", "level.default", "level.noSkills", "level.armorNative"):
        scal(k)
    L.append(LS_MARK)          # 0.2.1: the level stats marker + the new settings right under level.armorNative (a fresh file never updates)
    for k in LS_ROWK:
        scal(k)
    L.append(LS_TBLC)
    L += LS_TBLL
    L += ["", "# ---- costs: cost.<reforge|identify>.<id>=<base coins>,<coins per item level>; xp.reforge.<id>=<Smithing XP> ----"]
    for r in R_IDS:
        L.append("cost.reforge.%s=%d,%d" % ((r,) + COST_R_DEF[r]))
    for r in R_IDS:
        L.append("cost.identify.%s=%d,%d" % ((r,) + COST_I_DEF[r]))
    for r in R_IDS:
        L.append("xp.reforge.%s=%d" % (r, XP_R_DEF[r]))
    scal("reforge.names")
    L += ["", "# ---- combat (PART B applies these; spec 4.3) ----"]
    for k in ("combat.strPer", "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "steal.windowS", "regen.periodMs",
              "speed.per"):
        scal(k)
    L.append(CH_MARK)          # 0.1.2: the charged attack marker right above the charged.on help line (a fresh file never updates)
    for k in ("charged.on", "charged.spellFactor", "charged.log"):
        scal(k)
    L += ["", "# ---- migration of old SkyyRolls items (spec 1.6): migrate.map.<id>=<min score %> ----"]
    scal("migrate.by")
    for r in MIG_IDS:
        L.append("migrate.map.%s=%d" % (r, MIG_DEF[r]))
    scal("migrate.maxRarity")
    scal("migrate.clampToLevel")
    return "\n".join(L) + "\n"


DEFAULT_TEXT = default_text()
_dp = CFG.parse_props(DEFAULT_TEXT)
for _r in CFG_ROWS:
    if _r[3] != "table":
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: " + _r[0]
# 0.1.1: the default file carries Skyy's level table and, right under the levels header, the update marker (a fresh file never updates)
assert ("\n" + LV_HEAD + "\n" + LV_MARK + "\n") in DEFAULT_TEXT and DEFAULT_TEXT.count(LV_MARK_ID) == 1
for _t, _s, _c in BANDS:          # 0.2: the metal rows are bands now (Armor_Copper included)
    assert _dp.get("level.material." + _t) == band_text(_s, _c), "default file level.material.%s is not %d,%d" % (_t, _s, _c)
# 0.1.1 stat defaults: the new values + their marker right above the pool.later help line, once
assert ("\n" + ST_MARK + "\n# Roll coming-later stats: ") in DEFAULT_TEXT and DEFAULT_TEXT.count(ST_MARK_ID) == 1
for _k, _o, _n, _w in ST_DEFAULTS:
    assert _dp.get(_k) == _n and ("\n%s=%s\n" % (_k, _n)) in DEFAULT_TEXT, "default file %s is not %s" % (_k, _n)
assert DEFAULT_TEXT.startswith("# SkyyGear %s - " % VERSION)
# 0.1.2: stats.chg right under stats.cd; the charged marker once, right above the charged.on help line under speed.per
_DL = DEFAULT_TEXT.split("\n")
assert _DL[_DL.index("stats.cd=30,10") + 1:_DL.index("stats.cd=30,10") + 3] == ["# chg = Charged Attack Damage (weapon, armor, %)", "stats.chg=30,5"]
assert _DL[_DL.index("speed.per=1") + 1] == CH_MARK and _DL[_DL.index("speed.per=1") + 2].startswith("# Charged Attack Damage in combat: ")
assert DEFAULT_TEXT.count(CH_MARK_ID) == 1 and _dp.get("stats.chg") == "30,5"
# the lines migrate012 adds to an existing file = exactly the fresh file's lines (help comment + key=value per missing key)
CHG_ADD = _DL[_DL.index("stats.cd=30,10") + 1:_DL.index("stats.cd=30,10") + 3]
CH_ROWK = ["charged.on", "charged.spellFactor", "charged.log"]
CH_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in CH_ROWK]
CH_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in CH_ROWK]
assert all(_c.startswith("# ") for _c in CH_ROWC) and CH_ROWL == ["charged.on=true", "charged.spellFactor=0.15", "charged.log=false"]
assert all(ord(_c) < 127 for _c in DEFAULT_TEXT), "the default file must be plain ASCII (the loader writes UTF-8, the update ISO-8859-1)"
# 0.1.3: the family marker once, right under the last metal line, then the 59 family rows in table order (migrate013 adds the missing
# ones the same way: FM_LINES = exactly the fresh file's lines)
assert DEFAULT_TEXT.count(FM_MARK_ID) == 1 and _DL[_DL.index("level.material.Onyxium=40,49") + 1] == FM_MARK
# 0.2: migrate013 (byte-for-byte the 0.1.3 code) still adds its single-number family lines to a pre-0.1.3 file; migrate02 then turns each
# of them into the band below (the setup order) - so the two updates together give exactly the fresh file's family lines
FM_LINES = ["level.material.%s=%d" % (t, lv) for t, lv, _w in FAMILIES]
FB_LINES = ["level.material.%s=%s" % (t, band_text(s, c)) for t, s, c in FAM_BANDS]
assert _DL[_DL.index(FM_MARK) + 1:_DL.index(FM_MARK) + 1 + len(FB_LINES)] == FB_LINES
assert [l_.split("=")[0] for l_ in FM_LINES] == [l_.split("=")[0] for l_ in FB_LINES]
assert all(dict(BD_OLD)[t] == str(lv) for t, lv, _w in FAMILIES)
for _t, _s, _c in FAM_BANDS:
    assert _dp.get("level.material." + _t) == band_text(_s, _c), _t
# 0.2: the bands marker once, right under the last family row, then the new level settings (help comment + key=default each) and then the
# 0.1.x level rows (migrate02 adds the missing ones the same way: BD_ROWC / BD_ROWL = exactly the fresh file's lines)
assert DEFAULT_TEXT.count(BD_MARK_ID) == 1 and _DL[_DL.index(FM_MARK) + 1 + len(FB_LINES)] == BD_MARK
BD_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in BD_ROWK]
BD_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in BD_ROWK]
assert all(_c.startswith("# ") for _c in BD_ROWC) and BD_ROWL == ["part.levels=true", "level.bandWidth=8", "level.gateFloor=1",
                                                                 "craft.levelFrom=gate", "craft.belowBand=min", "craft.weaponSkill="]
_bi = _DL.index(BD_MARK)
assert _DL[_bi + 1:_bi + 1 + 2 * len(BD_ROWK)] == [x_ for p_ in zip(BD_ROWC, BD_ROWL) for x_ in p_]
assert _DL[_bi + 1 + 2 * len(BD_ROWK)].startswith("# Use Hytale item level otherwise: ")
assert _DL[_DL.index("level.material.Copper=10,18") + 1] == "level.material.Armor_Copper=1,18"
# 0.2.1: the level stats marker once, right under level.armorNative, then the six settings (help comment + key=default each), the table
# comment and the four base.armor lines, then the blank line before the costs (migrate021 adds the missing ones the same way: LS_ROWC /
# LS_ROWL / LS_TBLC / LS_TBLL = exactly the fresh file's lines)
assert DEFAULT_TEXT.count(LS_MARK_ID) == 1 and _DL[_DL.index("level.armorNative=true") + 1] == LS_MARK
LS_ROWC = [_DL[_DL.index("%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k])) - 1] for _k in LS_ROWK]
LS_ROWL = ["%s=%s" % (_k, dict((r[0], r[4]) for r in CFG_ROWS)[_k]) for _k in LS_ROWK]
assert all(_c.startswith("# ") for _c in LS_ROWC) and LS_ROWL == ["part.base=true", "base.mode=shape", "base.curve=" + BASE_CURVE_DEF,
                                                                 "base.matBonus=0.3", "base.armorOn=true", "base.resCurve=" + BASE_RES_DEF]
_li = _DL.index(LS_MARK)
assert _DL[_li + 1:_li + 1 + 2 * len(LS_ROWK)] == [x_ for p_ in zip(LS_ROWC, LS_ROWL) for x_ in p_]
assert _DL[_li + 1 + 2 * len(LS_ROWK):_li + 2 + 2 * len(LS_ROWK) + len(LS_TBLL)] == [LS_TBLC] + LS_TBLL
assert _DL[_li + 2 + 2 * len(LS_ROWK) + len(LS_TBLL)] == "" and _DL[_li + 3 + 2 * len(LS_ROWK) + len(LS_TBLL)].startswith("# ---- costs: ")
for _s, _h, _r in BASE_ARMOR_DEF:
    assert _dp.get("base.armor." + _s) == "%g,%g" % (_h, _r), _s
# every 0.2.1 block line is unique in the fresh file (the harness strips them to compare older shapes)
LS_LINES = [LS_MARK] + [x_ for p_ in zip(LS_ROWC, LS_ROWL) for x_ in p_] + [LS_TBLC] + LS_TBLL
assert all(_DL.count(_x) == 1 for _x in LS_LINES), "a 0.2.1 block line is not unique in the default file"

# ================================================================= classes (methods before callers; one registerSystem per class)
def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


gu   = mk("Gear")            # util: log, bridge, busy, epoch, pkey, text helpers
gdf  = mk("GearDefs")        # tables generated from the Python lists above
gcf  = mk("GearCfg")         # config fields (kit-bound) + tables + loader + checks
glg  = mk("GearLog")         # gear.log (queued, rotated at 5 MB)
gql  = mk("GearQual")        # quality.properties: the Skyy_Gear_* quality indices of the last start (engine review 4)
gdt  = mk("GearData")        # the gear document: id rules, read, migrate, write
glv  = mk("GearLevel")       # level lookup + level factor
grl  = mk("GearRoll")        # SecureRandom rolls: rarity, modifiers, reforge, identify, crafted gear
ggt  = mk("GearGate")        # gate skill + level cache + popup helper (PART B enforcement uses it)
gvw  = mk("GearView")        # tooltip (ItemDisplayMetadata) + plain lines + sigs
gbase = mk("GearBase")       # 0.2.1: base stats from the item level (curves, K, family bases, armor targets)
gst  = mk("GearStats")       # active totals (PART B applies them)
gnt  = mk("GearNotice")      # players/<pkey>.properties noticeShown
gsp  = mk("GearStamp")       # legacy stamp / migration / re-render scan + pending crafts
gspt = mk("GearStampTask")   # coalesced scan task (scheduler -> world thread)
# 0.1.3 world chests (see the header)
gcho = mk("GearChestOpen")       # the first-open decision, the loot window, the players of this server
gopn = mk("GearOpened")          # per world: the containers already decided (Skyy_SkyyGear/chests/<world>.txt)
gcht = mk("GearChestTask")       # the window backup: one decision as a world task
gknt = mk("GearKnownTask")       # reads the players of this server (scheduler, self-rescheduling)
gcos = mk("GearChestOpenSys", EES)   # UseBlockEvent$Pre -> decide before the container window opens
gcbs = mk("GearChestBreakSys", EES)  # BreakBlockEvent -> decide before an unopened world chest drops its items
gfg  = mk("GearForge")       # the reforge core (page + /gear reroll), write safety 1.7
gfn  = mk("GearFn")          # bridge functions (one class, a mode per key)
ginv = mk("GearInvSys", EES)     # InventoryChangeEvent -> dirty
gthr = mk("GearThrowSys", EES)   # DropItemEvent$Drop -> stamp the thrown stack (spec 1.5)
gcrs = mk("GearCraftSys", EES)   # CraftRecipeEvent$Post -> pending + roll task (spec 5.1)
gcrt = mk("GearCraftTask")
gcrp = mk("GearCraftPreSys", EES)   # 0.2: CraftRecipeEvent$Pre -> craft.belowBand block refuses a bench craft below the material band
gtk  = mk("GearTick", ETS)       # 1 s per player: level re-read -> re-render; PART B stat effects plug in here
grft = mk("GearRefreshTask")     # PlayerReadyEvent refresh (waits out profile:busy, 15 tries)
grdy = mk("GearReady")
gui  = mk("GearUi")              # vanilla style snippets (for the shared helper, RESUME step 5)
rpg  = mk("ReforgePage", PAGE)
rfc  = mk("ReforgeCmd", APC)
gad  = mk("GearAdmin")           # /gear sub-command bodies
gcm  = mk("GearCmd", APC)
SUBS = [("give", "GearGiveCmd", "Give gear: /gear give <item> [--rarity <id>] [--unid true]", True),
        ("read", "GearReadCmd", "Show the gear document and raw metadata of the held item", False),
        ("reroll", "GearRerollCmd", "Free reforge of the held item", False),
        ("clear", "GearClearCmd", "Remove SkyyGear data from the held item (it becomes Normal again)", False),
        ("rarity", "GearRarityCmd", "Set the held item's rarity: /gear rarity <id>", True),
        ("unid", "GearUnidCmd", "Make the held item unidentified (keeps its rarity)", False),
        ("identify", "GearIdentifyCmd", "Identify the held item for free", False),
        ("level", "GearLevelCmd", "Set or clear the held item's level: /gear level <n|clear>", True),
        ("gate", "GearGateCmd", "Set the held item's gate skill: /gear gate <skill|class>", True),
        ("migrate", "GearMigrateCmd", "Run the stamp / migration scan now: /gear migrate [player]", True),
        # 0.1.2: the charged-attack probe (read only; arms a 10 min probe of your own hits)
        ("charged", "GearChargedCmd", "Charged attack probe: the held weapon's charged steps + your last hit's result", True),
        # 0.2: re-stamp a player's stamped gear levels into today's bands (spec 2)
        ("relevel", "GearRelevelCmd", "Re-stamp gear levels into today's bands: /gear relevel [player]", True)]
subc = dict((s[0], mk(s[1], APC)) for s in SUBS)
pl   = mk("SkyyGearPlugin", JP)

# ---------------------------------------------------------------- PART B PLUGS IN HERE (1/4): its classes
# PART B (built 2026-09-28): tokens, engine probes and the class list. The Java itself sits in two blocks further down, each right
# before the first PART A class that calls it: "PART B (1/2)" before GearTick (combat, drops, chests, stat effects) and
# "PART B (2/2)" after /reforge (the Identify page + /identify). Engine facts (HytaleServer.jar bytecode, 2026-09-28):
#  - DamageSystems$ArmorDamageReduction (Filter group, no own dependencies) = public static getResistanceModifiers(World, armor
#    container, canApplyPenalties, EffectControllerComponent) + the flat / multiplier loop over inheritedParentId (copied in
#    GearArmor.reduce; ArmorResistanceModifiers' fields are public). The armor container is the InventoryComponent$Armor component.
#  - Store.tick(ArchetypeTickingSystem, dt, systemIndex) consumes that system's CommandBuffer right after its own tick, so the item
#    entities NPCDamageSystems$DropDeathItems adds with AddReason.SPAWN reach RefSystems in the SAME world tick; their TransformComponent
#    position is exactly the NPC position + (0, 1, 0) (ItemComponent.generateItemDrop).
#  - StashPlugin$StashSystem.onEntityAdded (ChunkStore RefSystem) rolls the drop list into ItemContainerBlock.getItemContainer() on ANY
#    add reason while the drop list is set and WorldConfig.isBlockSpawnersResolved(), then clears it when the gameplay config says so.
#  - Armor stat modifiers are applied by StatModifiersManager as ONE StaticModifier(MAX, calc, sum) per calculation type under the key
#    CalculationType.createKey("Armor"); MAX modifiers of one type add up (EntityStatValue.computeModifiers, value clamped to max).
import skyymove as MV
PB = {
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DPRJ": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$ProjectileSource",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "ADRC": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction",
    "ARMR": "com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction$ArmorResistanceModifiers",
    "ARMC": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "UTIL": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "INVC": "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "ITU": "com.hypixel.hytale.server.core.entity.ItemUtils",
    "KBC": "com.hypixel.hytale.server.core.entity.knockback.KnockbackComponent",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "LPC": "com.hypixel.hytale.server.core.entity.entities.ProjectileComponent",
    "SPP": "com.hypixel.hytale.server.core.modules.projectile.config.StandardPhysicsProvider",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "DTHC": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "ILM": "com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode",
    "NPCE": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ROLE": "com.hypixel.hytale.server.npc.role.Role",
    "DCR": "com.hypixel.hytale.server.core.modules.entity.damage.DeferredCorpseRemoval",
    "ITC": "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "ICB": "com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock",
    "BSI": "com.hypixel.hytale.server.core.modules.block.BlockModule$BlockStateInfo",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "MODF": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier",
    "MTG": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "VEC": "org.joml.Vector3d",
    "JPLG": JP,
    "PDEV": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
}
for _k in PB:
    assert _k not in T, "PART B token clashes with PART A: " + _k
    assert re.match(r"^[A-Z]+$", _k), _k
T.update(PB)
for c, m in ((PB["DMG"], "getAmount"), (PB["DMG"], "setAmount"), (PB["DMG"], "getSource"), (PB["DMG"], "getCause"),
             (PB["DMG"], "isCancelled"), (PB["DMG"], "setCancelled"), (PB["DENT"], "getRef"), (PB["DPRJ"], "getProjectile"),
             (PB["DMOD"], "get"), (PB["DMOD"], "getFilterDamageGroup"), (PB["DMOD"], "getInspectDamageGroup"),
             (PB["ADRC"], "getResistanceModifiers"), (PB["ARMR"], "flatModifier"), (PB["ARMR"], "multiplierModifier"),
             (PB["ARMR"], "inheritedParentId"), (PB["ARMC"], "getComponentType"), (PB["ARMC"], "getInventory"),
             (PB["UTIL"], "getComponentType"), (PB["UTIL"], "getActiveItem"), (PB["INVC"], "getItemInHand"),
             (PB["ECC"], "getComponentType"), (PB["ITU"], "canApplyItemStackPenalties"), (PB["KBC"], "getComponentType"),
             (CB, "tryRemoveComponent"), (CB, "getComponent"), (CB, "getExternalData"), (PB["UUIDC"], "getComponentType"),
             (PB["UUIDC"], "getUuid"), (PB["TC"], "getComponentType"), (PB["TC"], "getPosition"), (PB["LPC"], "getComponentType"),
             (PB["LPC"], "getCreatorUuid"), (PB["SPP"], "getComponentType"), (PB["SPP"], "getCreatorUuid"),
             (PB["RSYS"], "onEntityAdded"), (PB["RSYS"], "onEntityRemove"), (PB["ADDR"], "SPAWN"), (EST, "getRefFromUUID"),
             (EST, "getWorld"), (PB["DTHC"], "getComponentType"), (PB["DTHC"], "getItemsLossMode"), (PB["ILM"], "ALL"),
             (PB["NPCE"], "getComponentType"), (PB["NPCE"], "getRole"), (PB["ROLE"], "hasDroppedDeathItems"),
             (PB["ROLE"], "isDropDeathItemsInstantly"), (PB["DCR"], "getComponentType"), (PB["DCR"], "shouldRemove"),
             (PB["ITC"], "getComponentType"), (PB["ITC"], "getItemStack"), (PB["ITC"], "setItemStack"), (PB["CHS"], "getWorld"),
             (PB["ICB"], "getComponentType"), (PB["ICB"], "getDroplist"), (PB["ICB"], "getItemContainer"),
             (PB["BSI"], "getComponentType"), (PB["ESM"], "getComponentType"), (PB["ESM"], "get"), (PB["ESM"], "size"),
             (PB["ESM"], "putModifier"), (PB["ESM"], "removeModifier"), (PB["ESM"], "getModifier"), (PB["ESM"], "addStatValue"),
             (PB["ESV"], "get"), (PB["ESV"], "getMax"), (PB["DST"], "getHealth"), (PB["DST"], "getMana"), (PB["DST"], "getStamina"),
             (SMO, "getTarget"), (PB["MTG"], "MAX"), (CAL, "ADDITIVE"), (PB["VEC"], "x"), (PB["VEC"], "y"), (PB["VEC"], "z"),
             (UNI, "getPlayer"), (WLD, "getName"), (QRY, "and"), (QRY, "any"), (SIC, "setItemStackForSlot"), (IS, "isBroken"),
             ("com.hypixel.hytale.component.system.ISystem", "getDependencies"),
             ("com.hypixel.hytale.component.system.ISystem", "getGroup"),
             ("com.hypixel.hytale.component.system.tick.EntityTickingSystem", "isParallel"),
             ("com.hypixel.hytale.component.system.tick.ArchetypeTickingSystem", "tick"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getChunkStoreRegistry"),
             ("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems", "tick"),
             ("com.hypixel.hytale.builtin.adventure.stash.StashPlugin$StashSystem", "onEntityAdded"),
             ("com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent", "getPlayerRef")):
    B.probe(pool, c, m)
for _c in (PB["SDEP"], PB["ORD"], PB["ROLE"]):
    pool.get(_c)
# review-fix probes (2026-09-29): stack split, armor-container check, the engine Armor key, broken penalties, the lock pass order
for c, m in ((IS, "withQuantity"), (ICE, "getItemContainer"), (ICE, "getInventory"), (CAL, "createKey"), (WLD, "getGameplayConfig"),
             ("com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig", "getItemDurabilityConfig"),
             ("com.hypixel.hytale.server.core.asset.type.gameplay.ItemDurabilityConfig", "getBrokenPenalties"),
             ("com.hypixel.hytale.server.core.asset.type.gameplay.BrokenPenalties", "getArmor"),
             ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate", "tick"),
             ("com.hypixel.hytale.server.core.inventory.InventorySystems$LegacyArmorChangeStatSystem", "tick"),
             ("com.hypixel.hytale.server.core.entity.StatModifiersManager", "recalculateEntityStatModifiers"),
             ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue", "computeModifiers")):
    B.probe(pool, c, m)
# follow-up review probes (2026-09-29): the lock self-heal (item 6) and the MaxStack rules (items 1-2)
for c, m in ((PB["ESM"], "getStatModifiersManager"), ("com.hypixel.hytale.server.core.entity.StatModifiersManager", "scheduleRecalculate"),
             (ITM, "getMaxStack"), (DCS, "getId")):
    B.probe(pool, c, m)
_srm = pool.get("com.hypixel.hytale.server.core.entity.StatModifiersManager").getDeclaredMethod("scheduleRecalculate")
assert J0["Modifier"].isPublic(_srm.getModifiers()) and str(_srm.getSignature()) == "()V", "StatModifiersManager.scheduleRecalculate changed"
MV.probe(B, pool)
# ---------------------------------------------------------------- 0.2.1 base stats: engine tokens + probes (HytaleServer.jar, 2026-10-02)
# ItemArmor.getDamageResistanceValues() holds ResistanceModifier[] per DamageCause (NOT StaticModifier: VERIFIED bytecode
# ArmorDamageReduction.calculateResistanceEntryModifications - FLAT adds to flatModifier, every other type to multiplierModifier;
# Assets.zip armor uses "Percent" = 0.0648 for 6.48 %); ArmorResistanceModifiers has a public no-arg constructor + public fields;
# getResistanceModifiers builds a NEW map (computeIfAbsent) per call, so GearArmor.levelRes may change the copy it asked for.
BS = {
    "RMOD": "com.hypixel.hytale.server.core.modules.entity.damage.ResistanceModifier",
    "RCT": "com.hypixel.hytale.server.core.modules.entity.damage.ResistanceModifier$ResistanceCalculationType",
    # review of 0.2.1 finding 3 (the tooltip's spell line): the legacy projectile asset a wand / staff / spellbook cast launches
    # (LaunchProjectileInteraction ProjectileId, e.g. Skeleton_Mage_Corruption_Orb Damage 25) - VERIFIED bytecode: ProjectileComponent
    # .onProjectileHitEvent deals new Damage(ProjectileSource, DamageCause.PROJECTILE, projectile.getDamage() x brokenDamageModifier)
    "LPRJ": "com.hypixel.hytale.server.core.asset.type.projectile.config.Projectile",
}
for _k in BS:
    assert _k not in T, "0.2.1 token clashes: " + _k
T.update(BS)
for c, m in ((BS["RMOD"], "getCalculationType"), (BS["RMOD"], "getAmount"), (BS["RCT"], "FLAT"), (IAR, "getArmorSlot"),
             (IAR, "getDamageResistanceValues"), (IAR, "getStatModifiers"), (IWP, "getBasicDamageBreakdown"), (DBD, "entries"),
             (DBE, "max"), (DBE, "min"), (DCS, "getInherits"), (DCS, "getAssetMap"), (PB["ADRC"], "getResistanceModifiers"),
             ("com.hypixel.hytale.server.core.asset.type.gameplay.BrokenPenalties", "getWeapon"), (PB["DST"], "getHealth"),
             (BS["LPRJ"], "getAssetMap"), (BS["LPRJ"], "getDamage")):
    B.probe(pool, c, m)
assert str(pool.get(BS["LPRJ"]).getDeclaredMethod("getDamage").getSignature()) == "()I", "Projectile.getDamage() changed"
_armr_ctor = pool.get(PB["ARMR"]).getDeclaredConstructors()
assert any(str(_c.getSignature()) == "()V" and J0["Modifier"].isPublic(_c.getModifiers()) for _c in _armr_ctor), "ArmorResistanceModifiers()"
for _f in ("flatModifier", "multiplierModifier", "inheritedParentId"):
    assert J0["Modifier"].isPublic(pool.get(PB["ARMR"]).getField(_f).getModifiers()), "ArmorResistanceModifiers." + _f + " is not public"
_grm = pool.get(PB["ADRC"]).getDeclaredMethod("getResistanceModifiers")
assert J0["Modifier"].isPublic(_grm.getModifiers()) and J0["Modifier"].isStatic(_grm.getModifiers()), "getResistanceModifiers is public static"
# ---------------------------------------------------------------- 0.1.3 world chests: engine tokens + probes (HytaleServer.jar, 2026-10-01)
CO = {
    "BMOD": "com.hypixel.hytale.server.core.modules.block.BlockModule",
    "CSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.ChunkSection",
    "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "FBU": "com.hypixel.hytale.server.core.util.FillerBlockUtil",
    "PBI": "com.hypixel.hytale.server.core.modules.interaction.components.PlacedByInteractionComponent",
    "UBPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre",
    "BBE": "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "VECI": "org.joml.Vector3i",
    "CBW": "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow",
    "BWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow",
    "WMGR": "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager",
    "PSTO": "com.hypixel.hytale.server.core.universe.playerdata.PlayerStorage",
}
for _k in CO:
    assert _k not in T, "0.1.3 token clashes: " + _k
    assert re.match(r"^[A-Z]+$", _k), _k
T.update(CO)
for c, m in ((CO["BMOD"], "getBlockEntity"), (CO["CSEC"], "getComponentType"), (CO["CSEC"], "getX"), (CO["CSEC"], "getY"),
             (CO["CSEC"], "getZ"), (CO["BSEC"], "getComponentType"), (CO["BSEC"], "getFiller"), (CO["CHU"], "xFromIndex"),
             (CO["CHU"], "yFromIndex"), (CO["CHU"], "zFromIndex"), (CO["CHU"], "worldCoordFromLocalCoord"), (CO["FBU"], "unpackX"),
             (CO["FBU"], "unpackY"), (CO["FBU"], "unpackZ"), (CO["PBI"], "getComponentType"), (CO["PBI"], "getWhoPlacedUuid"),
             (CO["UBPRE"], "isCancelled"), (CO["UBPRE"], "getTargetBlock"), (CO["BBE"], "isCancelled"), (CO["BBE"], "getTargetBlock"),
             (CO["VECI"], "x"), (CO["VECI"], "y"), (CO["VECI"], "z"), (CO["BWIN"], "getX"), (CO["BWIN"], "getY"), (CO["BWIN"], "getZ"),
             (CO["CBW"], "getItemContainer"), (PLA, "getWindowManager"), (CO["WMGR"], "getWindows"), (UNI, "getPlayerStorage"),
             (UNI, "getPlayer"), (CO["PSTO"], "getPlayers"), (PB["BSI"], "getSectionRef"), (PB["BSI"], "getIndex"),
             (PB["ICB"], "getItemContainer"), (PB["CHS"], "getChunkSectionReferenceAtBlock"), (PB["CHS"], "getStore"),
             (WLD, "getChunkStore"), (WLD, "execute"), (WLD, "getWorldConfig"),
             ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "getUuid")):
    B.probe(pool, c, m)
# the engine facts the hook relies on (VERIFIED bytecode 2026-10-01, re-checked here so a game update that moves them stops the build):
# UseBlockInteraction.doInteraction fires UseBlockEvent$Pre (and checks isCancelled) BEFORE it executes the block's root interaction;
# OpenContainerInteraction builds the ContainerBlockWindow from ItemContainerBlock.getItemContainer(); BlockPlaceUtils.tryPlaceBlock
# puts the PlacedByInteractionComponent; BlockHarvestUtils.performBlockBreak fires BreakBlockEvent; the player-storage windows of the
# live set (SkyyVault, SkyyEssentials trade, SkyySacks) are ContainerWindow, which is no BlockWindow.


def _calls(cls, meth):
    from jpype import JClass as _JC
    _ip, _ps, _bo = _JC("javassist.bytecode.InstructionPrinter"), _JC("java.io.PrintStream"), _JC("java.io.ByteArrayOutputStream")
    out_ = []
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) == meth:
            b_ = _bo()
            _ip(_ps(b_)).print_(mm)
            out_.append(str(b_.toString()))
    return "\n".join(out_)


_ubi = _calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.UseBlockInteraction", "doInteraction")
assert _ubi.find("UseBlockEvent$Pre.<init>") >= 0 and _ubi.find("UseBlockEvent$Pre.isCancelled") > _ubi.find("UseBlockEvent$Pre.<init>")
assert _ubi.find("InteractionContext.execute") > _ubi.find("UseBlockEvent$Pre.isCancelled"), "UseBlockEvent$Pre no longer runs before the root interaction"
_oci = _calls("com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenContainerInteraction", "interactWithBlock")
assert "ContainerBlockWindow.<init>" in _oci and "ItemContainerBlock.getItemContainer" in _oci, "OpenContainerInteraction changed"
assert "PlacedByInteractionComponent.<init>" in _calls("com.hypixel.hytale.server.core.modules.interaction.BlockPlaceUtils", "tryPlaceBlock")
assert "BreakBlockEvent.<init>" in _calls("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils", "performBlockBreak")
assert not pool.get("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow").subclassOf(pool.get(CO["BWIN"]))
assert pool.get(CO["CBW"]).subclassOf(pool.get(CO["BWIN"]))
# ---------------------------------------------------------------- review of 0.1.3: replaced / regenerated containers (finding 3) and
# world removal (finding 4) - tokens, probes and the engine facts (VERIFIED bytecode 2026-10-01, re-checked here):
# BlockEntity.setBlockEntity adds a new block entity with AddReason.SPAWN (removing the old one with REMOVE); the container's open /
# close state change (BlockOperations.setBlockInteractionState) calls setBlock with flag 2 = keep the block entity, so it is never a
# SPAWN; the block entities of a loaded OR freshly generated chunk section come back through BlockComponentSectionLoadingSystem with
# AddReason.LOAD, so a regenerated chunk is seen the way Hytale's own TriggerVolumeChunkRegenSystem sees it: the WorldChunk entity
# added with AddReason.SPAWN and ChunkFlag.NEWLY_GENERATED.
CO2 = {
    "WCHK": "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "CFLAG": "com.hypixel.hytale.server.core.universe.world.chunk.ChunkFlag",
    "RWE": "com.hypixel.hytale.server.core.universe.world.events.RemoveWorldEvent",
}
for _k in CO2:
    assert _k not in T, "0.1.3 review token clashes: " + _k
    assert re.match(r"^[A-Z]+$", _k), _k
T.update(CO2)
for c, m in ((CO2["WCHK"], "getComponentType"), (CO2["WCHK"], "is"), (CO2["WCHK"], "getX"), (CO2["WCHK"], "getZ"),
             (CO2["CFLAG"], "NEWLY_GENERATED"), (CO2["RWE"], "getWorld"), (CO2["RWE"], "isCancelled"), (CO["CHU"], "chunkCoordinate"),
             ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "isDeleteOnRemove"),
             ("com.hypixel.hytale.server.core.universe.world.WorldConfig", "isDeleteOnUniverseStart"), (CB, "getComponent"),
             ("com.hypixel.hytale.server.core.plugin.JavaPlugin", "getChunkStoreRegistry")):
    B.probe(pool, c, m)
_tvr = _calls("com.hypixel.hytale.builtin.triggervolumes.prefab.TriggerVolumeChunkRegenSystem", "onEntityAdded")
assert "AddReason.SPAWN" in _tvr and "ChunkFlag.NEWLY_GENERATED" in _tvr and "WorldChunk.is(" in _tvr, "Hytale's chunk regen test changed"
_bcl = _calls("com.hypixel.hytale.server.core.universe.world.chunk.section.BlockComponentSection$BlockComponentSectionLoadingSystem",
              "onComponentRemoved")
assert "AddReason.LOAD" in _bcl and "CommandBuffer.addEntities" in _bcl, "section block entities are no longer re-added with LOAD"
assert "AddReason.SPAWN" in _calls("com.hypixel.hytale.server.core.modules.block.BlockEntity", "setBlockEntity")
_sbi = re.search(r"sipush (\d+)\s*\n[^\n]*BlockOperations\.setBlock\(",
                 _calls("com.hypixel.hytale.server.core.universe.world.chunk.BlockOperations", "setBlockInteractionState"))
assert _sbi and int(_sbi.group(1)) & 2, "a container's open / close state change no longer keeps its block entity (setBlock flag 2)"
gcrg = mk("GearChunkRegen", PB["RSYS"])   # ChunkStore: a regenerated chunk forgets its container records (finding 3b)
gwby = mk("GearWorldBye")                 # RemoveWorldEvent -> GearOpened.evict (finding 4)
# the vanilla armor effects under-level armor does NOT cancel in 0.1 (spec 3.5 part 4): listed here and logged once at start
_KNOWN_LIMIT_KEYS = ("DamageClassEnhancement", "KnockbackResistances", "KnockbackEnhancements", "DamageEnhancement", "Regenerating",
                     "MovementSettings")
ARMOR_LIMITS = []
for _n in sorted(AZ_NAMES):
    if not (_n.startswith("Server/Item/Items/") and _n.endswith(".json") and os.path.basename(_n).startswith("Armor_")):
        continue
    try:
        _a = json.loads(AZ.read(_n).decode("utf-8-sig")).get("Armor")
    except Exception:
        _a = None
    if isinstance(_a, dict):
        _hit = [k for k in _KNOWN_LIMIT_KEYS if _a.get(k)]
        if _hit:
            ARMOR_LIMITS.append("%s (%s)" % (os.path.basename(_n)[:-5], "+".join(_hit)))
print("PART B known limit (spec 3.5 part 4) - under-level armor keeps these vanilla effects: %d piece(s): %s"
      % (len(ARMOR_LIMITS), ", ".join(ARMOR_LIMITS)))
gmv   = mk("GearMove")                   # skyymove protocol v1 copy (tools/skyymove.py): Speed from armor, source gear.armor
ghit  = mk("GearHit")                    # combat helpers: gate judge, weapon-hit test, totals, hit math, per-Damage info
gsho  = mk("GearShot")                   # one launch record (what the shooter held)
gstk  = mk("GearShotTrack", PB["RSYS"])  # RefSystem on projectiles (SkyyClasses ShotTrack copy)
garm  = mk("GearArmor")                  # the copied armor formula + inactive-armor helpers
ghsy  = mk("GearHitSys", PB["DES"])      # Filter, BEFORE ArmorDamageReduction: gate, offence stats, pre-armor capture
garsy = mk("GearArmorSys", PB["DES"])    # Filter, AFTER ArmorDamageReduction: inactive-armor correction, Defense
gtsy  = mk("GearTrueSys", PB["DES"])     # Filter, AFTER GearArmorSys: + True Damage
glsy  = mk("GearLeechSys", PB["DES"])    # Inspect: Life Steal / Mana Steal bookkeeping
gtag  = mk("GearTag")                    # unidentified tagging + death marks + chest marks
gdm   = mk("GearDeathMark", ETS)         # BEFORE NPCDamageSystems$DropDeathItems: marks this tick's dying NPCs
gdrs  = mk("GearDropSys", PB["RSYS"])    # RefSystem ItemComponent: tags death drops at a mark
gcm1  = mk("GearChestMark", PB["RSYS"])  # ChunkStore, BEFORE StashPlugin$StashSystem
gcm2  = mk("GearChestTag", PB["RSYS"])   # ChunkStore, AFTER StashPlugin$StashSystem
gfx   = mk("GearFx")                     # per-player stat effects (armor lock, regen, stamina, speed, steal payouts, armor warn)
gfxi  = mk("GearFxInvSys", EES)          # InventoryChangeEvent of the armor container -> lower-only lock pass + speed at once
glks  = mk("GearLockSys", ETS)           # every tick BEFORE EntityStatsSystems$Recalculate: lower-only lock pass (engine review 1)
gbyb  = mk("GearByeB")                   # PlayerDisconnectEvent -> PART B state cleanup
gidn  = mk("GearIdent")                  # the identify core (write safety 1.7, coins first, refund)
ipg   = mk("IdentifyPage", PAGE)
idc   = mk("IdentifyCmd", APC)
# unordered fallbacks (the registry is keyed by class, so a fallback is its own class; SkyyExploration ChestSpawnLateSys pattern)
ghsyU = mk("GearHitSysU", PKG + ".GearHitSys")
garsU = mk("GearArmorSysU", PKG + ".GearArmorSys")
gtsyU = mk("GearTrueSysU", PKG + ".GearTrueSys")
gdmU  = mk("GearDeathMarkU", PKG + ".GearDeathMark")
gcm1U = mk("GearChestMarkU", PKG + ".GearChestMark")
gcm2U = mk("GearChestTagU", PKG + ".GearChestTag")
glksU = mk("GearLockSysU", PKG + ".GearLockSys")
PARTB_CLASSES = [(gmv, "move"), (ghit, "combat helpers"), (gsho, "shot record"), (gstk, "shot track"), (garm, "armor formula"),
                 (ghsy, "hit"), (garsy, "armor"), (gtsy, "true"), (glsy, "leech"), (gtag, "tag"), (gdm, "death mark"),
                 (gdrs, "drop tag"), (gcm1, "chest mark"), (gcm2, "chest tag"), (gfx, "effects"), (gfxi, "effects on change"),
                 (glks, "lock pass"), (gbyb, "cleanup"), (gidn, "identify core"), (ipg, "identify page"), (idc, "/identify"),
                 (ghsyU, "fallback"), (garsU, "fallback"), (gtsyU, "fallback"), (gdmU, "fallback"), (gcm1U, "fallback"),
                 (gcm2U, "fallback"), (glksU, "fallback")]
# ---------------------------------------------------------------- 0.1.2 Charged Attack Damage: engine tokens, probes, classes
_ICFG = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
CHT = {
    "DCSYS": "com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems",
    "DSEQ": "com.hypixel.hytale.server.core.modules.entity.damage.DamageCalculatorSystems$DamageSequence",
    "DCALC": _ICFG + "server.combat.DamageCalculator",
    "DCLASS": _ICFG + "server.combat.DamageClass",
    "IMS": "com.hypixel.hytale.server.core.meta.IMetaStore",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "ICTX": "com.hypixel.hytale.server.core.entity.InteractionContext",
    "COLL": _ICFG + "data.Collector",
    "CTAG": _ICFG + "data.CollectorTag",
    "CHTAG": _ICFG + "client.ChargingInteraction$ChargingTag",
    "CHGI": _ICFG + "client.ChargingInteraction",
    "STAG": _ICFG + "data.StringTag",
    "DEI": _ICFG + "server.DamageEntityInteraction",
    "ANGD": _ICFG + "server.DamageEntityInteraction$AngledDamage",
    "TGTD": _ICFG + "server.DamageEntityInteraction$TargetedDamage",
    "LPI": _ICFG + "server.LaunchProjectileInteraction",
    "PJI": "com.hypixel.hytale.server.core.modules.projectile.interaction.ProjectileInteraction",
    "PJC": "com.hypixel.hytale.server.core.modules.projectile.config.ProjectileConfig",
    "RTI": _ICFG + "RootInteraction",
    "INTR": _ICFG + "Interaction",
    "ITYPE": "com.hypixel.hytale.protocol.InteractionType",
}
for _k in CHT:
    assert _k not in T, "charged token clashes: " + _k
    assert re.match(r"^[A-Z]+$", _k), _k
T.update(CHT)
# research 3.1's placeholder probe list + everything the walk, the judge and the hand snapshot call (a missing API fails the build)
for c, m in ((CHT["DCSYS"], "DAMAGE_SEQUENCE"), (CHT["DSEQ"], "getDamageCalculator"), (CHT["DCALC"], "getDamageClass"),
             (CHT["DCLASS"], "CHARGED"), (CHT["DCLASS"], "SIGNATURE"), (CHT["DCLASS"], "LIGHT"), (CHT["IMS"], "getIfPresentMetaObject"),
             (CHT["IMGR"], "walkChain"), (CHT["ICTX"], "withoutEntity"), (CHT["ICTX"], "setInteractionVarsGetter"),
             (CHT["ICTX"], "getInteractionVars"), (CHT["COLL"], "collect"), (CHT["COLL"], "into"), (CHT["COLL"], "outof"),
             (CHT["COLL"], "start"), (CHT["COLL"], "finished"), (CHT["CHTAG"], "getSeconds"), (CHT["STAG"], "getTag"),
             (CHT["DEI"], "getDamageCalculator"), (CHT["DEI"], "getAngledDamage"), (CHT["DEI"], "getTargetedDamage"),
             (CHT["TGTD"], "getDamageCalculator"), (CHT["ANGD"], "getDamageCalculator"), (CHT["LPI"], "getProjectileId"),
             (CHT["PJI"], "getConfig"), (CHT["PJC"], "getInteractions"), (CHT["RTI"], "getAssetMap"), (ITM, "getInteractions"),
             (ITM, "getInteractionVars"), (CHT["ITYPE"], "ProjectileHit"), (CHT["ITYPE"], "Ability1"), (CHT["ITYPE"], "Ability2"),
             (CHT["ITYPE"], "Ability3"), (PB["LPC"], "getProjectileAssetName"), (PB["INVC"], "getItemInHand"), (CHT["CHGI"], "walk")):
    B.probe(pool, c, m)
_dsq = pool.get(CHT["DSEQ"])
assert J0["Modifier"].isPublic(_dsq.getModifiers()) and J0["Modifier"].isStatic(_dsq.getModifiers()), "DamageSequence is not public static"
gchv = mk("GearChgVars")                  # the interaction-vars getter the walk needs (= Item.getInteractionVars())
gchs = mk("GearChgState")                 # one item walk: records + the largest Next key per Charging step
gchw = mk("GearChgWalk")                  # the Collector (WeaponDamageDataCollector's label machine + FULL / PARTIAL)
gchi = mk("GearChg")                      # per-item index, roll eligibility, launch codes, the per-hit rule
ghnd = mk("GearHand")                     # the last two hand stacks per player (a single spear / spellbook used up by the cast)
ghns = mk("GearHandSys", ETS)             # every tick: GearHand.seen
gchg = mk("GearCharged")                  # the per-hit judge (DamageSequence meta), /gear charged, charged.log lines
CHG_CLASSES = [gchv, gchs, gchw, gchi, ghnd, ghns, gchg]
CHEST_CLASSES = [gcho, gopn, gcht, gknt, gcos, gcbs, gcrg, gwby]     # 0.1.3 world chests (+ the review's chunk regen / world removal)
# ---------------------------------------------------------------- PART B PLUGS IN HERE (2/4): lines inside setup()
# Java statements (with @TOKENS@) PART B needs in SkyyGearPlugin.setup(), after SkyyGear's own systems and commands, before the
# bridge + kit publish: registerSystem calls (ordered with SystemDependency + unordered fallback + one WARN, spec 5.5), the
# /identify command (registered always; identify.command is checked live when the command runs, so the Server Setup switch works
# without a restart), the movement protocol check, the disconnect cleanup. The bodies live in GearFx.setup (PART B (1/2)).
PARTB_SETUP = ["  @PKG@.GearFx.setup(this);",
               "  getCommandRegistry().registerCommand(new @PKG@.IdentifyCmd());"]
# ---------------------------------------------------------------- PART B PLUGS IN HERE (3/4): GearTick body
# Java statements run once per second per player inside GearTick.tick after the level refresh. In scope: dt, idx, chunk, store,
# cb, ref (Ref), p (Player), pr (PlayerRef), u (UUID), w (World), inv (Inventory), ss (String: this second's active totals, already
# published as gear:stats:<uuid> by PART A). Spec 3.5 / 4.2: armor lock modifiers, regen, stamina, speed (skyymove).
PARTB_TICK = "    @PKG@.GearFx.second(u, pr, cb, ref, inv);"

# ================================================================= GearLog: gear.log (spec 8.2), queued, written on the scheduler
# engine review 6: the class monitor (shared with kick(), which world threads reach through line()) is held only to swap the
# queue out (take); the disk write runs outside it, under WLOCK, which only the writing threads (scheduler, shutdown) ever take.
glg.addInterface(pool.get("java.lang.Runnable"))
F(glg, "public static final java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();")
F(glg, "public static final Object WLOCK = new Object();")
F(glg, "public static volatile boolean SCHED = false;")
F(glg, "public static volatile java.nio.file.Path FILE;")
F(glg, "public static volatile boolean FAILED = false;")
C(glg, "public GearLog() { }")
M(glg, r"""
public static synchronized String take() {
  SCHED = false;
  StringBuilder sb = new StringBuilder();
  Object o = Q.poll();
  while (o != null) { sb.append((String) o).append('\n'); o = Q.poll(); }
  return sb.toString();
}""")
M(glg, r"""
public static void write(java.nio.file.Path f, String text) {
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && java.nio.file.Files.size(f) > 5242880L) {
      java.nio.file.Files.move(f, f.resolveSibling(f.getFileName().toString() + ".1"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    java.nio.file.Files.write(f, text.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { if (!FAILED) { FAILED = true; System.err.println("[SkyyGear] could not write gear.log: " + t); } }
}""")
M(glg, r"""
public static void flush() {
  String text = take();
  java.nio.file.Path f = FILE;
  if (f == null || text.length() == 0) return;
  synchronized (WLOCK) { write(f, text); }
}""")
M(glg, "public void run() { flush(); }")
M(glg, r"""
public static synchronized void kick() {
  if (SCHED) return;
  SCHED = true;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearLog(), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { SCHED = false; }
}""")
M(glg, r"""
public static void line(String s) {
  if (FILE == null || s == null) return;
  String ts = "";
  try { ts = java.time.LocalDateTime.now().withNano(0).toString(); } catch (Throwable t) { ts = String.valueOf(System.currentTimeMillis()); }
  Q.add(ts + " " + s.replace('\n', ' '));
  kick();
}""")

# ================================================================= Gear (util)
F(gu, "public static @LOG@ LOG;")
F(gu, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(gu, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyGear] " + msg); } catch (Throwable t) { }
  try { @PKG@.GearLog.line("WARN " + msg); } catch (Throwable t2) { }
}""")
M(gu, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyGear] " + msg); } catch (Throwable t) { }
}""")
M(gu, r"""
public static boolean once(String key) {
  if (key == null) return false;
  return ONCE.putIfAbsent(key, Boolean.TRUE) == null;
}""")
M(gu, r"""
public static void warnOnce(String key, String msg) {
  if (once(key)) warn(msg + " (logged once)");
}""")
M(gu, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(gu, r"""
public static Object bget(String k) {
  try { return bridge().get(k); } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static java.util.function.Function fn(String k) {
  Object o = bget(k);
  return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
}""")
M(gu, r"""
public static boolean busy(java.util.UUID u) {
  return u != null && bget("profile:busy:" + u) != null;
}""")
M(gu, r"""
public static String epoch(java.util.UUID u) {
  Object e = u == null ? null : bget("profile:epoch:" + u);
  return e == null ? "" : String.valueOf(e);
}""")
# the contract's helper (tools/PROFILES-CONTRACT.md)
M(gu, r"""
public static String pkey(java.util.UUID u) {
  try {
    java.util.function.Function f = fn("profile:fn:key");
    if (f != null) {
      Object r = f.apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u == null ? "" : u.toString();
}""")
M(gu, r"""
public static String fmt(long n) {
  String s = String.valueOf(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
M(gu, r"""
public static String fnum(double f) {
  long r = Math.round(f);
  if (Math.abs(f - (double) r) < 0.05) return String.valueOf(r);
  return String.valueOf(Math.round(f * 10.0) / 10.0);
}""")
# en-US text of a translation key, null when missing (SkyyRolls tr)
M(gu, r"""
public static String tr(String key) {
  if (key == null) return null;
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if (s == null || s.trim().length() == 0 || s.equals(key)) return null;
    return s;
  } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static @ITM@ item(String id) {
  if (id == null) return null;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    return o instanceof @ITM@ ? (@ITM@) o : null;
  } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id;
  if (s.startsWith("Weapon_")) s = s.substring(7);
  else if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Tool_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
M(gu, r"""
public static String itemName(String id) {
  String n = null;
  try { @ITM@ it = item(id); if (it != null) n = tr(it.getTranslationKey()); } catch (Throwable t) { n = null; }
  if (n != null && n.indexOf(123) < 0) return n;
  return pretty(id);
}""")
M(gu, r"""
public static String hex(@PCOL@ c) {
  if (c == null) return null;
  return "#" + Integer.toHexString(256 | (c.red & 255)).substring(1) + Integer.toHexString(256 | (c.green & 255)).substring(1)
    + Integer.toHexString(256 | (c.blue & 255)).substring(1);
}""")
M(gu, r"""
public static int quality(@IS@ s) {
  try { return s == null ? Integer.MIN_VALUE : s.getQualityIndex(); } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
# the item's own quality index (what getQualityIndex answers for a stack without its own); MIN_VALUE when unreadable
M(gu, r"""
public static int ownQuality(@IS@ s) {
  try { @ITM@ it = s == null ? null : s.getItem(); return it == null ? Integer.MIN_VALUE : it.getQualityIndex(); } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
M(gu, r"""
public static boolean admin(java.util.UUID u) {
  try { return u != null && @PERM@.get().hasPermission(u, "skyygear.admin"); } catch (Throwable t) { return false; }
}""")
# one string value out of the page event JSON (SkyyRolls ReforgePage.jsonStr)
M(gu, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(gu, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
# 0.2: one chat line to an online player by UUID (the /craft bridge only knows the crafter's UUID); never throws
M(gu, r"""
public static void tell(java.util.UUID u, String text, String col) {
  if (u == null || text == null) return;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr != null) pr.sendMessage(col == null ? @MSG@.raw(text) : @MSG@.raw(text).color(col));
  } catch (Throwable t) { }
}""")

# ================================================================= GearDefs (generated tables)
F(gdf, "public static final String[] R_ID = %s;" % jarr(R_IDS))
F(gdf, "public static final String[] R_NAME = %s;" % jarr(R_NAMES))
F(gdf, "public static final String[] R_HEX = %s;" % jarr([r[2] for r in RARITIES]))
F(gdf, "public static final String[] R_PAGEHEX = %s;" % jarr([r[3] for r in RARITIES]))
F(gdf, "public static final String[] R_QID = %s;" % jarr(QUAL_IDS))
F(gdf, "public static final int NR = %d;" % NR)
F(gdf, "public static final int NS = %d;" % NS)
F(gdf, "public static final String[] S_KEY = %s;" % jarr(S_KEYS))
F(gdf, "public static final String[] S_LABEL = %s;" % jarr([s[1] for s in STATS]))
F(gdf, "public static final String[] S_SLOT = %s;" % jarr([s[2] for s in STATS]))
F(gdf, "public static final String[] S_UNIT = %s;" % jarr([s[3] for s in STATS]))
F(gdf, "public static final int[] S_MAXDEF = %s;" % jints([s[4] for s in STATS]))
F(gdf, "public static final int[] S_WDEF = %s;" % jints([s[5] for s in STATS]))
F(gdf, "public static final int[] S_LIVE = %s;" % jints([s[6] for s in STATS]))
F(gdf, "public static final String[] S_SUF = %s;" % jarr([s[7] for s in STATS]))
F(gdf, "public static final String[] KINDS = %s;" % jarr([k for k, g in GATE_BY_KIND]))
F(gdf, "public static final String[] KIND_GATE = %s;" % jarr([g for k, g in GATE_BY_KIND]))
F(gdf, "public static final String[] ENFORCED = %s;" % jarr(ENFORCED_KINDS))
F(gdf, "public static final String[] TF_PRE = %s;" % jarr([p for p, k in TOOL_FAMILIES]))
F(gdf, "public static final String[] TF_KIND = %s;" % jarr([k for p, k in TOOL_FAMILIES]))
F(gdf, "public static final String[] CL_NAME = %s;" % jarr([c for c, s in CLASS_SKILLS]))
F(gdf, "public static final String[] CL_SKILL = %s;" % jarr([s for c, s in CLASS_SKILLS]))
F(gdf, "public static final String[] AMMO = %s;" % jarr(AMMO))
F(gdf, "public static final String[] SPELL = %s;" % jarr(SPELL_PREFIXES))
F(gdf, "public static final String[] RQ_FROM = %s;" % jarr([a for a, b in ROLLS_QMAP]))
F(gdf, "public static final String[] RQ_TO = %s;" % jarr([b for a, b in ROLLS_QMAP]))
F(gdf, "public static final String[] MIG_ID = %s;" % jarr(MIG_IDS))
# spec 7.1 gear:gates = the combat + gathering kinds only (equipment / tool / accessory stay internal until their stages exist)
GATES_PUB = ",".join("%s:%s" % (k, g) for k, g in GATE_BY_KIND if k in ("combat", "mining", "foraging", "farming"))
assert GATES_PUB == "combat:class,mining:Mining,foraging:Foraging,farming:Farming", GATES_PUB
F(gdf, "public static final String GATES = %s;" % jstr(GATES_PUB))
F(gdf, "public static final String TIERS = %s;" % jstr(",".join("%s:%s:%s" % (r[0], r[1], r[2]) for r in RARITIES)))
F(gdf, "public static final int VIEW_V = %d;" % VIEW_V)
# 0.2.1: the family base items (spec 3.2; FAM_BASE above, checked against Assets.zip at build time)
F(gdf, "public static final String[] FB_FAM = %s;" % jarr([f for f, b in FAM_BASE]))
F(gdf, "public static final String[] FB_ID = %s;" % jarr([b for f, b in FAM_BASE]))
F(gdf, 'public static final String DOC_KEY = "SkyyGear";')
F(gdf, 'public static final String VIEW_KEY = "SkyyGearView";')
F(gdf, 'public static final String ROLLS_KEY = "SkyyRolls";')
F(gdf, 'public static final String ROLLS_VIEW = "SkyyRollsView";')
F(gdf, "public static final long PENDING_MAX_MS = %dL;" % PENDING_MAX_MS)
F(gdf, "public static final long SCAN_GAP_MS = %dL;" % SCAN_GAP_MS)
# vanilla palette (spec 5.8 / 6.4); FOR THE SHARED STYLE HELPER (RESUME step 5)
F(gdf, 'public static final String C_GRAY = "#878e9c";')      # @ColorGrayCaption: vanilla description, (coming later)
F(gdf, 'public static final String C_LABEL = "#96a9be";')     # @ColorDefaultLabel
F(gdf, 'public static final String C_GOLD = "#E8A93B";')      # @ColorGoldHighlight: costs
F(gdf, 'public static final String C_DIS = "#797b7c";')       # @ColorDisabled
F(gdf, 'public static final String C_OK = "%s";' % V_OK)      # design review 3: vanilla "met" green (MemoriesCategory counter)
F(gdf, 'public static final String C_BAD = "%s";' % V_BAD)    # vanilla error red: too low / refused, everywhere (tooltip, popup, pages)
F(gdf, "public static final String[] NEVER = %s;" % jarr(NEVER_GEAR))
F(gdf, "public static final int INCL_MIN = %d;" % INCL_MIN)
F(gdf, "public static final String[] INCL_BARE = %s;" % jarr(INCL_BARE))
F(gdf, "public static final String[] FAMILIES = %s;" % jarr(GEAR_FAMILIES))
F(gdf, "public static final int STACK_CEIL = %d;" % STACK_CEIL)
F(gdf, "public static final int FREE_KEEP = %d;" % FREE_KEEP)
F(gdf, "public static final String[] KIND_CHOICES = %s;" % jarr(KIND_CHOICES))
F(gdf, "public static final int I_HPR = %d;" % S_KEYS.index("hpr"))
F(gdf, "public static final int I_HPRP = %d;" % S_KEYS.index("hprp"))
F(gdf, "public static final int I_CHG = %d;" % S_KEYS.index("chg"))       # 0.1.2 Charged Attack Damage
M(gdf, r"""
public static int rIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < R_ID.length; i++) if (R_ID[i].equalsIgnoreCase(id.trim())) return i;
  for (int i = 0; i < R_NAME.length; i++) if (R_NAME[i].equalsIgnoreCase(id.trim())) return i;
  return -1;
}""")
M(gdf, r"""
public static int sIndex(String key) {
  if (key == null) return -1;
  for (int i = 0; i < S_KEY.length; i++) if (S_KEY[i].equals(key)) return i;
  return -1;
}""")
M(gdf, r"""
public static String kindGate(String kind) {
  if (kind == null) return "class";
  for (int i = 0; i < KINDS.length; i++) if (KINDS[i].equals(kind)) return KIND_GATE[i];
  return "";
}""")
M(gdf, r"""
public static boolean enforcedKind(String kind) {
  if (kind == null) return true;
  for (int i = 0; i < ENFORCED.length; i++) if (ENFORCED[i].equals(kind)) return true;
  return false;
}""")
M(gdf, r"""
public static String classSkill(String cls) {
  if (cls == null) return null;
  for (int i = 0; i < CL_NAME.length; i++) if (CL_NAME[i].equalsIgnoreCase(cls)) return CL_SKILL[i];
  return null;
}""")
# quality asset index per rarity (resolved once; -1 = the plugin quality asset is not loaded -> fallback 2.1: name colour only).
# qIndex itself sits in the GearQual block (after GearCfg): it compares with the indices of the last start (engine review 4).
F(gdf, "public static volatile int[] QIDX = null;")
F(gdf, "public static volatile long QMISS = 0L;")

# ================================================================= GearCfg fields (kit-bound fields must exist before emit)
CFG_FIELDS = [("PART_GATE", "boolean", "true"), ("PART_STATS", "boolean", "true"), ("PART_CRAFT", "boolean", "true"),
              ("PART_DROPS", "boolean", "true"), ("PART_CHESTS", "boolean", "true"), ("IDENTIFY_CMD", "boolean", "true"),
              ("EXCLUDE", "String", jstr(EXCLUDE_DEF)), ("UI_FRAMES", "boolean", "true"), ("POOL_LATER", "boolean", "false"),
              ("LEVEL_FLOOR", "int", "25"), ("LEVEL_FULL", "int", "40"), ("SMITH_PER", "double", "0.5"),
              ("SMITH_CAP", "double", "50.0"), ("CRAFT_MAX", "String", '"fabled"'), ("LEVEL_VANILLA", "boolean", "true"),
              ("LEVEL_DEFAULT", "int", "0"), ("NO_SKILLS", "String", '"pass"'), ("ARMOR_NATIVE", "boolean", "true"),
              ("NAMES", "String", jstr(REFORGE_NAMES_DEF)), ("STR_PER", "double", "1.0"), ("MP_PER", "double", "1.0"),
              ("DEF_SCALE", "int", "100"), ("CRIT_BASE", "double", "0.0"), ("CRIT_BASE_DMG", "double", "0.0"),
              ("STEAL_S", "int", "3"), ("REGEN_MS", "int", "2000"), ("SPEED_PER", "double", "1.0"),
              ("MIGRATE_BY", "String", '"stats"'), ("MIGRATE_MAX", "String", '"fabled"'), ("INCLUDE", "String", '""'),
              ("MIGRATE_CLAMP", "boolean", "false"),
              # 0.1.2 Charged Attack Damage
              ("CHG_ON", "boolean", "true"), ("CHG_SPELL", "double", "0.15"), ("CHG_LOG", "boolean", "false"),
              # 0.2 per-item levels (stage 1)
              ("PART_LEVELS", "boolean", "true"), ("BAND_W", "int", str(BAND_W_DEF)), ("GATE_FLOOR", "int", str(GATE_FLOOR_DEF)),
              ("CRAFT_FROM", "String", '"gate"'), ("CRAFT_BELOW", "String", '"min"'), ("CRAFT_SKILL", "String", '""'),
              # 0.2.1 base stats from the level (stages 2 + 3)
              ("PART_BASE", "boolean", "true"), ("BASE_MODE", "String", '"shape"'), ("BASE_CURVE", "String", jstr(BASE_CURVE_DEF)),
              ("BASE_MAT", "double", repr(BASE_MAT_DEF)), ("BASE_ARMOR", "boolean", "true"), ("BASE_RES", "String", jstr(BASE_RES_DEF))]
for _n, _t, _v in CFG_FIELDS:
    F(gcf, "public static volatile %s %s = %s;" % (_t, _n, _v))
# tables (set by load(); not kit fields)
F(gcf, "public static volatile int[] R_MODS = %s;" % jints([RARITY_DEF[r][0] for r in R_IDS]))
F(gcf, "public static volatile int[] R_LO = %s;" % jints([RARITY_DEF[r][1] for r in R_IDS]))
F(gcf, "public static volatile int[] R_HI = %s;" % jints([RARITY_DEF[r][2] for r in R_IDS]))
F(gcf, "public static volatile int[] S_MAX = %s;" % jints([s[4] for s in STATS]))
F(gcf, "public static volatile int[] S_W = %s;" % jints([s[5] for s in STATS]))
for _col, _nm in ((0, "O_CRAFT"), (1, "O_MOB"), (2, "O_CHEST")):
    F(gcf, "public static volatile double[] %s = new double[] { %s };" % (_nm, ", ".join(repr(float(ODDS_DEF[r][_col])) for r in R_IDS)))
F(gcf, "public static final double[] OD_CRAFT = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][0])) for r in R_IDS))
F(gcf, "public static final double[] OD_MOB = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][1])) for r in R_IDS))
F(gcf, "public static final double[] OD_CHEST = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][2])) for r in R_IDS))
for _nm, _tbl, _col in (("CR_BASE", COST_R_DEF, 0), ("CR_PER", COST_R_DEF, 1), ("CI_BASE", COST_I_DEF, 0), ("CI_PER", COST_I_DEF, 1)):
    F(gcf, "public static volatile long[] %s = new long[] { %s };" % (_nm, ", ".join("%dL" % _tbl[r][_col] for r in R_IDS)))
    F(gcf, "public static final long[] D%s = new long[] { %s };" % (_nm, ", ".join("%dL" % _tbl[r][_col] for r in R_IDS)))
F(gcf, "public static volatile long[] XPR = new long[] { %s };" % ", ".join("%dL" % XP_R_DEF[r] for r in R_IDS))
F(gcf, "public static final long[] DXPR = new long[] { %s };" % ", ".join("%dL" % XP_R_DEF[r] for r in R_IDS))
F(gcf, "public static volatile int[] MIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))
F(gcf, "public static final int[] DMIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))
F(gcf, "public static final int[] DR_MODS = %s;" % jints([RARITY_DEF[r][0] for r in R_IDS]))
F(gcf, "public static final int[] DR_LO = %s;" % jints([RARITY_DEF[r][1] for r in R_IDS]))
F(gcf, "public static final int[] DR_HI = %s;" % jints([RARITY_DEF[r][2] for r in R_IDS]))
F(gcf, "public static final String[] MAT_T = %s;" % jarr([t for t, l in MATERIALS]))
F(gcf, "public static final int[] MAT_L = %s;" % jints([l for t, l in MATERIALS]))
# 0.1.1 update (GearCfg.migrate011): the 0.1 defaults, the marker comment, the levels header it goes under, the log / History name
F(gcf, "public static final int[] MAT_OLD = %s;" % jints([l for t, l in MATERIALS_010]))
F(gcf, "public static final String LV_MARK = %s;" % jstr(LV_MARK))
F(gcf, "public static final String LV_MARK_ID = %s;" % jstr(LV_MARK_ID))
F(gcf, "public static final String LV_HEAD = %s;" % jstr(LV_HEAD))
F(gcf, "public static final String LV_WHO = %s;" % jstr(LV_WHO))
# 0.1.1 stat defaults update (GearCfg.migrateStat011): keys, 0.1 texts, 0.1.1 texts, what each change means, the marker
F(gcf, "public static final String[] ST_KEY = %s;" % jarr([t[0] for t in ST_DEFAULTS]))
F(gcf, "public static final String[] ST_OLD = %s;" % jarr([t[1] for t in ST_DEFAULTS]))
F(gcf, "public static final String[] ST_NEW = %s;" % jarr([t[2] for t in ST_DEFAULTS]))
F(gcf, "public static final String[] ST_WHY = %s;" % jarr([t[3] for t in ST_DEFAULTS]))
F(gcf, "public static final String ST_MARK = %s;" % jstr(ST_MARK))
F(gcf, "public static final String ST_MARK_ID = %s;" % jstr(ST_MARK_ID))
# 0.1.2 charged attack lines update (GearCfg.migrate012): the marker, its name, the lines it adds (exactly the fresh file's)
F(gcf, "public static final String CH_MARK = %s;" % jstr(CH_MARK))
F(gcf, "public static final String CH_MARK_ID = %s;" % jstr(CH_MARK_ID))
F(gcf, "public static final String CH_WHO = %s;" % jstr(CH_WHO))
F(gcf, "public static final String[] CHG_ADD = %s;" % jarr(CHG_ADD))
F(gcf, "public static final String[] CH_ROWK = %s;" % jarr(CH_ROWK))
F(gcf, "public static final String[] CH_ROWC = %s;" % jarr(CH_ROWC))
F(gcf, "public static final String[] CH_ROWL = %s;" % jarr(CH_ROWL))
# 0.1.3 level families (built-in defaults with no file, the default text, migrate013): entries, levels, the marker, its name
F(gcf, "public static final String[] FAM_T = %s;" % jarr([t for t, l, _w in FAMILIES]))
F(gcf, "public static final int[] FAM_L = %s;" % jints([l for t, l, _w in FAMILIES]))
F(gcf, "public static final String FM_MARK = %s;" % jstr(FM_MARK))
F(gcf, "public static final String FM_MARK_ID = %s;" % jstr(FM_MARK_ID))
F(gcf, "public static final String FM_WHO = %s;" % jstr(FM_WHO))
# 0.2 level bands: the built-in default table (entry, min, cap: the metals with Armor_Copper, then the 59 family rows), the 0.1.3 default
# TEXTS migrate02 turns into bands, its marker / name, the new scalar rows it adds (exactly the fresh file's lines), the vanilla ceiling
F(gcf, "public static final String[] BD_T = %s;" % jarr([t for t, s, c in BD_ALL]))
F(gcf, "public static final int[] BD_MIN = %s;" % jints([s for t, s, c in BD_ALL]))
F(gcf, "public static final int[] BD_CAP = %s;" % jints([c for t, s, c in BD_ALL]))
F(gcf, "public static final int BD_METALS = %d;" % len(BANDS))
F(gcf, "public static final String[] BO_T = %s;" % jarr([t for t, o in BD_OLD]))
F(gcf, "public static final String[] BO_V = %s;" % jarr([o for t, o in BD_OLD]))
F(gcf, "public static final String BD_MARK = %s;" % jstr(BD_MARK))
F(gcf, "public static final String BD_MARK_ID = %s;" % jstr(BD_MARK_ID))
F(gcf, "public static final String BD_WHO = %s;" % jstr(BD_WHO))
F(gcf, "public static final String[] BD_ROWK = %s;" % jarr(BD_ROWK))
F(gcf, "public static final String[] BD_ROWC = %s;" % jarr(BD_ROWC))
F(gcf, "public static final String[] BD_ROWL = %s;" % jarr(BD_ROWL))
F(gcf, "public static final int VTOP = %d;" % VANILLA_TOP)
F(gcf, "public static final int BAND_W_DEF = %d;" % BAND_W_DEF)
# 0.2.1 base stats: the Lv 1 armor table (base.armor.<slot>; set by the loader, built-in = the Copper row), its slot names + defaults, the
# migrate021 marker / name and the lines it adds (exactly the fresh file's), the default curves (a curve the loader cannot read falls
# back to these)
F(gcf, "public static final String[] BA_SLOT = %s;" % jarr([s for s, h, r in BASE_ARMOR_DEF]))
F(gcf, "public static final double[] DBA_H = new double[] { %s };" % ", ".join(repr(float(h)) for s, h, r in BASE_ARMOR_DEF))
F(gcf, "public static final double[] DBA_R = new double[] { %s };" % ", ".join(repr(float(r)) for s, h, r in BASE_ARMOR_DEF))
F(gcf, "public static volatile double[] BA_H = new double[] { %s };" % ", ".join(repr(float(h)) for s, h, r in BASE_ARMOR_DEF))
F(gcf, "public static volatile double[] BA_R = new double[] { %s };" % ", ".join(repr(float(r)) for s, h, r in BASE_ARMOR_DEF))
F(gcf, "public static final String CURVE_DEF = %s;" % jstr(BASE_CURVE_DEF))
F(gcf, "public static final String RES_DEF = %s;" % jstr(BASE_RES_DEF))
F(gcf, "public static final String LS_MARK = %s;" % jstr(LS_MARK))
F(gcf, "public static final String LS_MARK_ID = %s;" % jstr(LS_MARK_ID))
F(gcf, "public static final String LS_WHO = %s;" % jstr(LS_WHO))
F(gcf, "public static final String[] LS_ROWK = %s;" % jarr(LS_ROWK))
F(gcf, "public static final String[] LS_ROWC = %s;" % jarr(LS_ROWC))
F(gcf, "public static final String[] LS_ROWL = %s;" % jarr(LS_ROWL))
F(gcf, "public static final String LS_TBLC = %s;" % jstr(LS_TBLC))
F(gcf, "public static final String[] LS_TBLL = %s;" % jarr(LS_TBLL))
# 0.2 recipes shipped in this jar's asset pack (the ready line names them)
F(gcf, "public static final String[] RCP_ID = %s;" % jarr([r[0] for r in MAGIC_RECIPES]))
F(gcf, "public static final String[] RCP_OUT = %s;" % jarr([r[1] for r in MAGIC_RECIPES]))
# the cap of every level.material entry (lower case -> Integer; set with MAT by the loader) and its spelling in the file (messages)
F(gcf, "public static volatile java.util.HashMap MATCAP = new java.util.HashMap();")
F(gcf, "public static volatile java.util.HashMap MATNAME = new java.util.HashMap();")
# the most words any level.material entry has (1 with only one-word entries = the 0.1.2 loop), set by the loader, max 3
F(gcf, "public static volatile int MAT_WORDS = 1;")
F(gcf, "public static volatile java.util.HashMap MAT = new java.util.HashMap();")
F(gcf, "public static volatile java.util.HashMap ITEMLVL = new java.util.HashMap();")
F(gcf, "public static volatile long EPOCH = 0L;")
F(gcf, "public static volatile java.nio.file.Path FILE;")
F(gcf, "public static volatile java.nio.file.Path DIR;")
F(gcf, "public static volatile String EXCL_SRC = null;")
F(gcf, "public static volatile String[] EXCL = new String[0];")
F(gcf, "public static volatile String NAMES_SRC = null;")
F(gcf, "public static volatile String[] RF = new String[0];")
F(gcf, "public static volatile String INCL_SRC = null;")
F(gcf, "public static volatile String[] INCL = new String[0];")
F(gcf, "public static volatile java.util.HashMap KINDP = new java.util.HashMap();")     # kind.prefix table: id prefix -> kind

kit = CFG.emit(pool, PKG, MOD="SkyyGear", TITLE="Gear", VERSION=VERSION, NODE="skyygear.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE], NOTE="Every number is a placeholder. Tables apply at once; hand edits on Reload.",
               RELOAD="GearCfg.load", KEEP=10, DEFAULTS={CFG_FILE: DEFAULT_TEXT})

# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)
M(gu, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    java.util.function.Function f = fn("settings:fn:get");
    if (f != null) {
      Object r = f.apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(gu, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyGear", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")

# ================================================================= GearCfg: loader, SkyyRolls cost import, checks, costs
M(gcf, "public static String defaultsText() { return " + jlit(DEFAULT_TEXT) + "; }")
# engine review 7: the config kit's atomicWrite shape - temp file, flush + fsync, then ATOMIC_MOVE + REPLACE_EXISTING (plain
# REPLACE_EXISTING where the file system has no atomic move). replace = false keeps "never overwrite a file that appeared in
# between" (a plain move that fails on an existing file; ATOMIC_MOVE would replace it on Windows).
M(gcf, r"""
public static void writeAtomic(java.nio.file.Path dst, String text, boolean replace) throws Exception {
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(text.getBytes("UTF-8"));
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  Throwable last = null;
  int i = 0;
  while (i < 5) {
    try {
      if (replace) {
        try { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
        catch (java.nio.file.AtomicMoveNotSupportedException am) { java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      } else java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[0]);
      return;
    } catch (java.nio.file.FileAlreadyExistsException ae) {
      try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d1) { }
      return;
    } catch (java.nio.file.FileSystemException fe) {
      last = fe;
      i++;
    } catch (Throwable t) {
      last = t;
      i = 5;
    }
    if (i < 5) { try { Thread.sleep(20L); } catch (Throwable ie) { } }
  }
  try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d2) { }
  throw new java.io.IOException("could not write " + dst + ": " + last);
}""")
M(gcf, r"""
public static java.util.Properties read(java.nio.file.Path f) throws Exception {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""")
M(gcf, r"""
public static String clean(String v) {
  if (v == null) return null;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length(); i++) { char c = v.charAt(i); if (c != ',' && c != ' ' && c != '_' && c != '%') sb.append(c); }
  return sb.toString();
}""")
M(gcf, r"""
public static boolean pbool(java.util.Properties p, String k, boolean def) {
  String v = p.getProperty(k);
  if (v == null) return def;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return false;
  @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not true/false - the default is used");
  return def;
}""")
M(gcf, r"""
public static long plong(java.util.Properties p, String k, long def, long lo, long hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  long n = def;
  try { n = (long) Math.floor(Double.parseDouble(clean(v.trim()))); }
  catch (Throwable t) { @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not a number - the default is used"); return def; }
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(gcf, r"""
public static double pdec(java.util.Properties p, String k, double def, double lo, double hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  double n = def;
  try { n = Double.parseDouble(clean(v.trim())); }
  catch (Throwable t) { @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not a number - the default is used"); return def; }
  if (Double.isNaN(n)) return def;
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(gcf, r"""
public static String ptext(java.util.Properties p, String k, String def) {
  String v = p.getProperty(k);
  if (v == null) return def;
  return v.trim();
}""")
# table cells "a,b,c" (the kit's sep=, file form; a hand edit with | is accepted too); null = missing or malformed
M(gcf, r"""
public static double[] cells(String v, int n) {
  if (v == null) return null;
  String s = v.trim().replace('|', ',');
  String[] ps = s.split(",");
  if (ps.length != n) return null;
  double[] out = new double[n];
  for (int i = 0; i < n; i++) {
    try { out[i] = Double.parseDouble(ps[i].trim().replace("_", "")); } catch (Throwable t) { return null; }
    if (Double.isNaN(out[i])) return null;
  }
  return out;
}""")
M(gcf, r"""
public static double clampd(double v, double lo, double hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""")
M(gcf, r"""
public static int rchoice(String v, int maxIdx, int def) {
  int i = @PKG@.GearDefs.rIndex(v);
  if (i < 0 || i > maxIdx) return def;
  return i;
}""")
# design review 1: a kind.prefix value is one of combat, mining, foraging, farming, equipment
M(gcf, r"""
public static boolean kindOk(String v) {
  if (v == null) return false;
  for (int i = 0; i < @PKG@.GearDefs.KIND_CHOICES.length; i++) if (@PKG@.GearDefs.KIND_CHOICES[i].equals(v)) return true;
  return false;
}""")
# 0.1.3: the most words ("_"-separated) any level.material entry has, 1..3 (GearLevel.level tries at most this many at each id word)
M(gcf, r"""
public static int matWords(java.util.HashMap mat) {
  int mw = 1;
  java.util.Iterator it = mat.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int n = 1;
    for (int i = 0; i < k.length(); i++) if (k.charAt(i) == '_') n++;
    if (n > mw) mw = n;
  }
  return mw > 3 ? 3 : mw;
}""")
# 0.2: what a level.material row with ONE number means: N to N + width - 1 (spec 9), never past 49 while N is a vanilla level (spec 2: the
# family bands "never above 49"; question 3: vanilla materials cover 1-49), never past 100
M(gcf, r"""
public static int capOf(int min, int w) {
  int c = min + (w < 1 ? 1 : w) - 1;
  if (min <= VTOP && c > VTOP) c = VTOP;
  if (c > 100) c = 100;
  return c < min ? min : c;
}""")
# 0.2.1 base.curve / base.resCurve: "level:factor,level:factor,..." -> Object[] { double[] levels, double[] factors } (levels whole
# numbers 0-100 strictly rising, factors above 0 and at most 100, 1-50 points); null = not readable. GearBase.eval draws straight lines
# between the points and keeps the end values outside them (spec 3.1).
M(gcf, r"""
public static Object[] curvePts(String s) {
  if (s == null) return null;
  String t = s.trim();
  if (t.length() == 0) return null;
  String[] ps = t.split(",");
  if (ps.length < 1 || ps.length > 50) return null;
  double[] ls = new double[ps.length];
  double[] vs = new double[ps.length];
  for (int i = 0; i < ps.length; i++) {
    String q = ps[i].trim();
    int c = q.indexOf(':');
    if (c <= 0 || c >= q.length() - 1) return null;
    double l = 0.0;
    double v = 0.0;
    try {
      l = Double.parseDouble(q.substring(0, c).trim());
      v = Double.parseDouble(q.substring(c + 1).trim());
    } catch (Throwable x) { return null; }
    if (Double.isNaN(l) || Double.isNaN(v) || Double.isInfinite(l) || Double.isInfinite(v)) return null;
    if (l < 0.0 || l > 100.0 || l != Math.floor(l)) return null;
    if (!(v > 0.0) || v > 100.0) return null;
    if (i > 0 && !(l > ls[i - 1])) return null;
    ls[i] = l;
    vs[i] = v;
  }
  return new Object[] { ls, vs };
}""")
# the kit's check hook of both curve rows (also run by the loader on a hand-edited line)
M(gcf, r"""
public static String checkCurve(String key, String value) {
  if (value == null) return null;
  if (curvePts(value) == null) return "Write level:factor points with rising levels 0-100 and factors above 0, e.g. 1:1.0,4:1.6,10:2.0,40:3.0,100:5.0 (straight lines between the points).";
  return null;
}""")
# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows
M(gcf, r"""
public static synchronized void apply(java.util.Properties p, boolean fromFile) {
  PART_GATE = pbool(p, "part.gate", true);
  PART_STATS = pbool(p, "part.stats", true);
  PART_CRAFT = pbool(p, "part.craft", true);
  PART_DROPS = pbool(p, "part.drops", true);
  PART_CHESTS = pbool(p, "part.chests", true);
  IDENTIFY_CMD = pbool(p, "identify.command", true);
  EXCLUDE = ptext(p, "gear.exclude", @EXCLDEF@);
  UI_FRAMES = pbool(p, "ui.frames", true);
  POOL_LATER = pbool(p, "pool.later", false);
  LEVEL_FLOOR = (int) plong(p, "stat.levelFloor", 25L, 1L, 100L);
  LEVEL_FULL = (int) plong(p, "stat.levelFull", 40L, 1L, 100L);
  SMITH_PER = pdec(p, "smith.perLevel", 0.5, 0.0, 100.0);
  SMITH_CAP = pdec(p, "smith.cap", 50.0, 0.0, 100.0);
  CRAFT_MAX = @PKG@.GearDefs.R_ID[rchoice(ptext(p, "craft.maxRarity", "fabled"), 5, 4)];
  LEVEL_VANILLA = pbool(p, "level.vanilla", true);
  LEVEL_DEFAULT = (int) plong(p, "level.default", 0L, 0L, 100L);
  NO_SKILLS = "block".equalsIgnoreCase(ptext(p, "level.noSkills", "pass")) ? "block" : "pass";
  ARMOR_NATIVE = pbool(p, "level.armorNative", true);
  NAMES = ptext(p, "reforge.names", @NAMESDEF@);
  STR_PER = pdec(p, "combat.strPer", 1.0, 0.0, 100.0);
  MP_PER = pdec(p, "combat.mpPer", 1.0, 0.0, 100.0);
  DEF_SCALE = (int) plong(p, "combat.defScale", 100L, 1L, 100000L);
  CRIT_BASE = pdec(p, "crit.base", 0.0, 0.0, 1000.0);
  CRIT_BASE_DMG = pdec(p, "crit.baseDamage", 0.0, 0.0, 10000.0);
  STEAL_S = (int) plong(p, "steal.windowS", 3L, 1L, 60L);
  REGEN_MS = (int) plong(p, "regen.periodMs", 2000L, 250L, 60000L);
  SPEED_PER = pdec(p, "speed.per", 1.0, 0.0, 100.0);
  CHG_ON = pbool(p, "charged.on", true);
  CHG_SPELL = pdec(p, "charged.spellFactor", 0.15, 0.0, 1.0);
  CHG_LOG = pbool(p, "charged.log", false);
  PART_LEVELS = pbool(p, "part.levels", true);
  int bw = (int) plong(p, "level.bandWidth", (long) BAND_W_DEF, 1L, 50L);
  BAND_W = bw;
  GATE_FLOOR = (int) plong(p, "level.gateFloor", 1L, 0L, 100L);
  CRAFT_FROM = "band".equalsIgnoreCase(ptext(p, "craft.levelFrom", "gate")) ? "band" : "gate";
  CRAFT_BELOW = "block".equalsIgnoreCase(ptext(p, "craft.belowBand", "min")) ? "block" : "min";
  CRAFT_SKILL = ptext(p, "craft.weaponSkill", "");
  // 0.2.1 base stats: a curve the check would refuse (a hand edit) falls back to its default with one WARN; base.armor.<slot> rows are
  // read in any case of the slot word, a missing / unreadable row = its built-in Copper value
  PART_BASE = pbool(p, "part.base", true);
  BASE_MODE = "off".equalsIgnoreCase(ptext(p, "base.mode", "shape")) ? "off" : "shape";
  String bcv = ptext(p, "base.curve", CURVE_DEF);
  if (checkCurve("base.curve", bcv) != null) { @PKG@.Gear.warnOnce("curve:" + bcv, "config.properties: base.curve=" + bcv + " is not a list of level:factor points - the default " + CURVE_DEF + " is used"); bcv = CURVE_DEF; }
  BASE_CURVE = bcv;
  BASE_MAT = pdec(p, "base.matBonus", @BMATDEF@, 0.0, 10.0);
  BASE_ARMOR = pbool(p, "base.armorOn", true);
  String brv = ptext(p, "base.resCurve", RES_DEF);
  if (checkCurve("base.resCurve", brv) != null) { @PKG@.Gear.warnOnce("rcurve:" + brv, "config.properties: base.resCurve=" + brv + " is not a list of level:factor points - the default " + RES_DEF + " is used"); brv = RES_DEF; }
  BASE_RES = brv;
  double[] bah = new double[BA_SLOT.length];
  double[] bar = new double[BA_SLOT.length];
  for (int i = 0; i < BA_SLOT.length; i++) { bah[i] = DBA_H[i]; bar[i] = DBA_R[i]; }
  java.util.Iterator bit = p.stringPropertyNames().iterator();
  while (bit.hasNext()) {
    String bk = (String) bit.next();
    if (!bk.startsWith("base.armor.") || bk.length() <= 11) continue;
    String bs = bk.substring(11);
    int bi = -1;
    for (int i = 0; i < BA_SLOT.length; i++) if (BA_SLOT[i].equalsIgnoreCase(bs)) bi = i;
    double[] bc = cells(p.getProperty(bk), 2);
    if (bi < 0 || bc == null || bc[0] < 0.0 || bc[1] < 0.0 || bc[1] > 100.0) { @PKG@.Gear.warnOnce("barmor:" + bk, "config.properties: " + bk + "=" + p.getProperty(bk) + " is not <Health>,<resistance %> of a Head, Chest, Legs or Hands piece - ignored"); continue; }
    bah[bi] = clampd(bc[0], 0.0, 1000.0);
    bar[bi] = bc[1];
  }
  BA_H = bah;
  BA_R = bar;
  String mb = ptext(p, "migrate.by", "stats").toLowerCase();
  MIGRATE_BY = (mb.equals("roll") || mb.equals("item")) ? mb : "stats";
  MIGRATE_MAX = @PKG@.GearDefs.R_ID[rchoice(ptext(p, "migrate.maxRarity", "fabled"), 4, 4)];
  INCLUDE = ptext(p, "gear.include", "");
  MIGRATE_CLAMP = pbool(p, "migrate.clampToLevel", false);
  int nr = @PKG@.GearDefs.NR;
  int[] rm = new int[nr];
  int[] rl = new int[nr];
  int[] rh = new int[nr];
  double[] oc = new double[nr];
  double[] om = new double[nr];
  double[] ox = new double[nr];
  long[] crb = new long[nr];
  long[] crp = new long[nr];
  long[] cib = new long[nr];
  long[] cip = new long[nr];
  long[] xp = new long[nr];
  for (int i = 0; i < nr; i++) {
    String rid = @PKG@.GearDefs.R_ID[i];
    double[] c = cells(p.getProperty("rarity." + rid), 3);
    if (c == null) {
      if (p.getProperty("rarity." + rid) != null) @PKG@.Gear.warn("config.properties: rarity." + rid + " must be <modifiers>,<low %>,<high %> - the default is used");
      rm[i] = DR_MODS[i]; rl[i] = DR_LO[i]; rh[i] = DR_HI[i];
    } else {
      rm[i] = (int) clampd(c[0], 0.0, 1000.0);
      rl[i] = (int) clampd(c[1], 0.0, 1000.0);
      rh[i] = (int) clampd(c[2], 0.0, 1000.0);
      if (rh[i] < rl[i]) { @PKG@.Gear.warn("config.properties: rarity." + rid + " high % is below low % - high = low"); rh[i] = rl[i]; }
    }
    double[] o = cells(p.getProperty("odds." + rid), 3);
    if (o == null) { oc[i] = OD_CRAFT[i]; om[i] = OD_MOB[i]; ox[i] = OD_CHEST[i]; }
    else { oc[i] = clampd(o[0], 0.0, 1000000.0); om[i] = clampd(o[1], 0.0, 1000000.0); ox[i] = clampd(o[2], 0.0, 1000000.0); }
    double[] cr = cells(p.getProperty("cost.reforge." + rid), 2);
    if (cr == null) { crb[i] = DCR_BASE[i]; crp[i] = DCR_PER[i]; }
    else { crb[i] = (long) clampd(cr[0], 0.0, 1.0E12); crp[i] = (long) clampd(cr[1], 0.0, 1.0E12); }
    double[] ci = cells(p.getProperty("cost.identify." + rid), 2);
    if (ci == null) { cib[i] = DCI_BASE[i]; cip[i] = DCI_PER[i]; }
    else { cib[i] = (long) clampd(ci[0], 0.0, 1.0E12); cip[i] = (long) clampd(ci[1], 0.0, 1.0E12); }
    double[] xr = cells(p.getProperty("xp.reforge." + rid), 1);
    xp[i] = xr == null ? DXPR[i] : (long) clampd(xr[0], 0.0, 100000.0);
  }
  int ns = @PKG@.GearDefs.NS;
  int[] sm = new int[ns];
  int[] sw = new int[ns];
  for (int i = 0; i < ns; i++) {
    String k = @PKG@.GearDefs.S_KEY[i];
    double[] c = cells(p.getProperty("stats." + k), 2);
    int d = @PKG@.GearDefs.S_MAXDEF[i];
    if (c == null) { sm[i] = d; sw[i] = @PKG@.GearDefs.S_WDEF[i]; }
    else {
      sm[i] = (int) clampd(c[0], 0.0, 100000.0);
      sw[i] = (int) clampd(c[1], 0.0, 100000.0);
      // spec 9.2 / review E10: the kit accepts a hand-edited line the check would ask about, so the loader warns instead
      if ((d > 0 && sm[i] > 4 * d) || (sm[i] == 0 && d > 0))
        @PKG@.Gear.warnOnce("stat4x:" + k + ":" + sm[i], "config.properties: stats." + k + " max " + sm[i] + " is far from the default " + d + " - every " + @PKG@.GearDefs.S_LABEL[i] + " roll on new items changes");
    }
  }
  int[] mg = new int[@PKG@.GearDefs.MIG_ID.length];
  for (int i = 0; i < mg.length; i++) {
    double[] c = cells(p.getProperty("migrate.map." + @PKG@.GearDefs.MIG_ID[i]), 1);
    mg[i] = c == null ? DMIG[i] : (int) clampd(c[0], 0.0, 100.0);
  }
  java.util.HashMap mat = new java.util.HashMap();
  java.util.HashMap mcap = new java.util.HashMap();
  java.util.HashMap mnam = new java.util.HashMap();
  java.util.HashMap il = new java.util.HashMap();
  java.util.HashMap kp = new java.util.HashMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  boolean anyMat = false;
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("kind.prefix.") && k.length() > 12) {
      String kv = p.getProperty(k).trim().toLowerCase();
      if (kindOk(kv)) kp.put(k.substring(12), kv);
      else @PKG@.Gear.warn("config.properties: " + k + "=" + kv + " is not combat, mining, foraging, farming or equipment - ignored");
    } else if (k.startsWith("level.material.") && k.length() > 15) {
      anyMat = true;
      // 0.2: <min>,<cap> (the kit's 2-column table) or one number = <min> with the width rule (capOf)
      double[] c = cells(p.getProperty(k), 1);
      double[] c2 = null;
      if (c == null) c2 = cells(p.getProperty(k), 2);
      if (c == null && c2 == null) { @PKG@.Gear.warn("config.properties: " + k + " is not a level or a <min>,<cap> band - ignored"); continue; }
      // review of 0.1.3 finding 8: GearLevel.level tries at most 3 id words in a row, so a longer entry can never match
      int nw = 1;
      for (int q = 15; q < k.length(); q++) if (k.charAt(q) == '_') nw++;
      if (nw > 3) @PKG@.Gear.warnOnce("matwords:" + k.toLowerCase(), "config.properties: " + k + " has " + nw + " words - an entry matches at most 3 words of the item id in a row, so this row never matches (use Level by item for one item)");
      double v0 = 0.0;
      double v1 = 0.0;
      if (c != null) v0 = c[0];
      else { v0 = c2[0]; v1 = c2[1]; }
      int mn = (int) clampd(v0, 0.0, 100.0);
      int cp = mn;
      if (c != null) cp = capOf(mn, bw);
      else cp = (int) clampd(v1, 0.0, 100.0);
      if (cp < mn) { @PKG@.Gear.warnOnce("bandcap:" + k.toLowerCase() + ":" + cp, "config.properties: " + k + " has its cap " + cp + " below its min " + mn + " - the band is exactly level " + mn); cp = mn; }
      String le = k.substring(15).toLowerCase();
      mat.put(le, Integer.valueOf(mn));
      mcap.put(le, Integer.valueOf(cp));
      mnam.put(le, k.substring(15));
    } else if (k.startsWith("level.item.") && k.length() > 11) {
      double[] c = cells(p.getProperty(k), 1);
      if (c == null) { @PKG@.Gear.warn("config.properties: " + k + " is not a level - ignored"); continue; }
      il.put(k.substring(11), Integer.valueOf((int) clampd(c[0], 0.0, 100.0)));
    }
  }
  if (!fromFile && !anyMat) {
    // 0.2: the built-in table = the default file's bands (the metals with Armor_Copper, then the 59 family rows)
    for (int i = 0; i < BD_T.length; i++) {
      String le = BD_T[i].toLowerCase();
      mat.put(le, Integer.valueOf(BD_MIN[i]));
      mcap.put(le, Integer.valueOf(BD_CAP[i]));
      mnam.put(le, BD_T[i]);
    }
  }
  int mw = matWords(mat);
  R_MODS = rm; R_LO = rl; R_HI = rh;
  O_CRAFT = oc; O_MOB = om; O_CHEST = ox;
  CR_BASE = crb; CR_PER = crp; CI_BASE = cib; CI_PER = cip; XPR = xp;
  S_MAX = sm; S_W = sw; MIG = mg; ITEMLVL = il; KINDP = kp;
  // 0.2: the caps + spellings first (a reader that finds an entry in MAT and none here falls back to the width rule)
  MATCAP = mcap;
  MATNAME = mnam;
  if (mw >= MAT_WORDS) { MAT_WORDS = mw; MAT = mat; } else { MAT = mat; MAT_WORDS = mw; }
  EPOCH = EPOCH + 1L;
}""".replace("@EXCLDEF@", jstr(EXCLUDE_DEF)).replace("@NAMESDEF@", jstr(REFORGE_NAMES_DEF)).replace("@BMATDEF@", repr(BASE_MAT_DEF)))
# RELOAD of the kit (tools/CONFIG-CONTRACT.md) and the setup() loader: the first start writes the default file
M(gcf, r"""
public static synchronized void load() {
  java.util.Properties p = new java.util.Properties();
  boolean ok = false;
  try {
    java.nio.file.Path f = FILE;
    if (f != null) {
      if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) writeAtomic(f, defaultsText(), false);
      p = read(f);
      ok = true;
    }
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not read Skyy_SkyyGear/config.properties - the built-in defaults are used: " + t);
    p = new java.util.Properties();
    ok = false;
  }
  apply(p, ok);
}""")
M(gcf, r"""
public static boolean hasLine(String text, String prefix) {
  if (text == null) return false;
  String[] ls = text.split("\n");
  for (int i = 0; i < ls.length; i++) if (ls[i].trim().startsWith(prefix)) return true;
  return false;
}""")
# spec 1.6: one-time import of the SkyyRolls 0.1.5 reforge costs when config.properties has no cost.reforge. lines yet
M(gcf, r"""
public static void importRolls(java.nio.file.Path gearFile, java.nio.file.Path rollsFile) {
  try {
    if (gearFile == null || rollsFile == null || !java.nio.file.Files.exists(rollsFile, new java.nio.file.LinkOption[0])) return;
    String text = null;
    if (java.nio.file.Files.exists(gearFile, new java.nio.file.LinkOption[0])) {
      text = new String(java.nio.file.Files.readAllBytes(gearFile), "UTF-8");
      if (hasLine(text, "cost.reforge.")) return;
    }
    java.util.Properties rp = read(rollsFile);
    java.util.HashMap low = new java.util.HashMap();
    java.util.Iterator it = rp.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); low.put(k.trim().toLowerCase(), rp.getProperty(k)); }
    int nr = @PKG@.GearDefs.NR;
    String[] lines = new String[nr];
    StringBuilder what = new StringBuilder();
    int n = 0;
    for (int i = 0; i < @PKG@.GearDefs.RQ_FROM.length; i++) {
      String from = @PKG@.GearDefs.RQ_FROM[i];
      if (from.equals("Junk")) continue;
      Object v = low.get("cost." + from.toLowerCase());
      if (v == null) continue;
      long c = 0L;
      try { c = (long) Math.floor(Double.parseDouble(clean(String.valueOf(v).trim()))); } catch (Throwable t) { continue; }
      if (c < 0L) c = 0L;
      if (c > 1000000000000L) c = 1000000000000L;
      int r = @PKG@.GearDefs.rIndex(@PKG@.GearDefs.RQ_TO[i]);
      if (r < 0) continue;
      lines[r] = "cost.reforge." + @PKG@.GearDefs.R_ID[r] + "=" + c + ",0";
      what.append(from).append(" -> ").append(@PKG@.GearDefs.R_NAME[r]).append(' ').append(c).append("; ");
      n++;
    }
    if (n == 0) return;
    String out;
    if (text == null) {
      String[] ls = defaultsText().split("\n");
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < ls.length; i++) {
        String l = ls[i];
        for (int r = 0; r < nr; r++) if (lines[r] != null && l.startsWith("cost.reforge." + @PKG@.GearDefs.R_ID[r] + "=")) l = lines[r];
        sb.append(l).append('\n');
      }
      out = sb.toString();
      writeAtomic(gearFile, out, false);
    } else {
      StringBuilder sb = new StringBuilder(text);
      if (!text.endsWith("\n")) sb.append('\n');
      sb.append("# imported once from Skyy_SkyyRolls/reforge.properties (spec 1.6)\n");
      for (int r = 0; r < nr; r++) {
        if (lines[r] != null) sb.append(lines[r]).append('\n');
        else sb.append("cost.reforge.").append(@PKG@.GearDefs.R_ID[r]).append('=').append(DCR_BASE[r]).append(',').append(DCR_PER[r]).append('\n');
      }
      writeAtomic(gearFile, sb.toString(), true);
    }
    @PKG@.Gear.info("imported the SkyyRolls reforge costs once (Mythic and Set keep their placeholders): " + what.toString());
    @PKG@.GearLog.line("IMPORT SkyyRolls reforge costs: " + what.toString());
  } catch (Throwable t) { @PKG@.Gear.warn("SkyyRolls cost import failed - the SkyyGear placeholders are used: " + t); }
}""")
# ---- 0.1.1: the one-time level table update of an existing config.properties (see the header). matIdx = the loader's rule for a
# level.material. key (prefix exact, entry word any case) -> the MATERIALS index, -1 = none
M(gcf, r"""
public static int matIdx(String k) {
  if (k == null || k.length() <= 15 || !k.startsWith("level.material.")) return -1;
  String e = k.substring(15);
  for (int i = 0; i < MAT_T.length; i++) if (MAT_T[i].equalsIgnoreCase(e)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.key / value / end). null = the marker is
# already in a comment line (nothing to do). Else { new text, "Iron 20 -> 15, ..." , String[] kept notes, String[] { entry, old, new }* }.
# A material whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the 0.1 default is updated: every
# one-line entry of it that holds the 0.1 default gets the new value (value text only: key, separator and CR stay). Anything else is
# kept: a custom value (noted unless it already is the 0.1.1 default), a continued entry (noted), a missing line (silent). The marker
# goes under the levels header, else before the first level.material line, else at the end; every other line is copied as it was.
# Review of 0.1.1, finding 4: when the marker would go at the end but the file ends inside a still-open entry (its last line ends in an
# odd number of backslashes, or the final newline follows such a line), the marker goes on its own line just BEFORE that entry instead
# (appended after it, it was swallowed as a continuation line: that value changed and the update re-ran every start). The entry starts
# a logical line, so the line before it never continues; its bytes stay last, exactly as they were (a blank line after it would change
# what java.util.Properties reads when the entry is a lone backslash: its empty key ""). tail = the first line of the entry that ends
# on the text's last line (-1 = none).
M(gcf, r"""
public static Object[] lvUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = MAT_T.length;
  String[] eff = new String[n];
  String[] ent = new String[n];
  boolean[] multi = new boolean[n];
  int head = -1;
  int first = -1;
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(LV_MARK_ID) >= 0) return null;
      if (head < 0 && s.trim().equals(LV_HEAD)) head = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    int m = matIdx(key);
    if (m >= 0) {
      if (first < 0) first = k;
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      ent[m] = key.substring(15);
      multi[m] = e > k;
    }
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (MAT_OLD[i] == MAT_L[i] || eff[i] == null) continue;
    String ov = String.valueOf(MAT_OLD[i]);
    String nv = String.valueOf(MAT_L[i]);
    if (!multi[i] && eff[i].equals(ov)) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(ent[i]).append(' ').append(ov).append(" -> ").append(nv);
      rows.add(ent[i]);
      rows.add(ov);
      rows.add(nv);
    } else if (multi[i] || !eff[i].equals(nv)) {
      kept.add("level.material." + ent[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (custom) - the 0.1.1 default is " + nv);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = matIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(String.valueOf(MAT_OLD[m2]))) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + String.valueOf(MAT_L[m2]) + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int at = -1;
  if (head >= 0 && head + 1 < out.size()) { at = head + 1; cr = raw[head].endsWith("\r") ? "\r" : ""; }
  else if (head < 0 && first >= 0) { at = first; if (first + 1 < raw.length) cr = raw[first].endsWith("\r") ? "\r" : ""; }
  else if (tail >= 0 && (((String) out.get(out.size() - 1)).length() == 0 || @PKG@.CfgFile.cont((String) l.get(l.size() - 1)))) {
    at = tail;
    if (tail + 1 < raw.length) cr = raw[tail].endsWith("\r") ? "\r" : "";
  }
  if (at >= 0) out.add(at, LV_MARK + cr);
  else {
    int last = out.size() - 1;
    if (((String) out.get(last)).length() == 0) out.add(last, LV_MARK + cr);
    else { out.set(last, ((String) out.get(last)) + cr); out.add(LV_MARK); }
  }
  StringBuilder sb = new StringBuilder(text.length() + LV_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of config.properties (the kit's HOME, Skyy_SkyyGear)
M(gcf, r"""
public static void lvKit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.Gear.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# review of 0.1.1, finding 3: CfgHist.snapshot swallows its own errors, so after it the update checks that config-history really holds
# a copy with exactly these bytes (the new copy, or the newest one when snapshot skipped an equal file). The copies themselves are
# checked, not index.log: a copy whose index line failed would make snapshot skip forever and the update never run
M(gcf, r"""
public static boolean lvSaved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
# one config-changes.log line in the kit's format (CfgLog.add without its per-line INFO): time, name, uuid, via, key, old, new, status
M(gcf, r"""
public static String lvLog(String e, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + LV_WHO + "\t-\tupdate\tlevel.material[" + @PKG@.CfgRows.oneLine(e) + "]\t" + o + "\t" + n + "\tok";
}""")
# setup(), after importRolls and BEFORE load() + CfgPub.start: the old file becomes a History version (KEEP 10), the new text is written
# with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line per updated material, one INFO line (+ one per kept custom
# value). Returns the INFO line(s) joined by \n ("" = nothing done: no file, marker already there, or a failure - WARN, file untouched)
M(gcf, r"""
public static synchronized String migrate011() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = lvUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), LV_WHO, "before the 0.1.1 level table update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.1.1 level table: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(lvLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.1 level table: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no level.material line still had its 0.1 default - nothing changed (0.1.1 level table marker added)";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.Gear.info(kept[i]); all.append('\n').append(kept[i]); }
    @PKG@.GearLog.line("CONFIG 0.1.1 level table: " + (chg.length() > 0 ? chg : "nothing changed") + (kept.length > 0 ? "; " + kept.length + " custom kept" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.1.1 level table (the file is used as it is): " + t);
    return "";
  }
}""")
# ---- 0.1.1 STAT DEFAULTS: the one-time update of pool.later + stat.levelFull (see the header), the level update's rules method for
# method. stIdx = a scalar key exactly as java.util.Properties / the loader read it (case-sensitive) -> the ST_KEY index, -1 = none
M(gcf, r"""
public static int stIdx(String k) {
  if (k == null) return -1;
  for (int i = 0; i < ST_KEY.length; i++) if (ST_KEY[i].equals(k)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.key / value / end). null = the stat marker
# is already in a comment line (nothing to do). Else { new text, "pool.later true -> false (...), ...", String[] kept notes,
# String[] { key, old, new }* }. A key whose LAST live line (the one Properties keeps) is a one-line entry holding exactly the 0.1 text
# is updated: every one-line entry of it that holds the 0.1 text gets the new value (value text only: key, separator and CR stay).
# Anything else is kept: a custom value (noted unless it already is the 0.1.1 default), a continued entry (noted), a missing line
# (silent). Marker: on its own line right above the first pool.later / stat.levelFull entry - above that entry's help comment when a
# comment line sits directly on top of it (the fresh default file's place) - else right under the level marker (a comment line, so
# the line after it starts an entry and nothing can continue into the marker: the end-of-file trap of review finding 4 cannot happen);
# neither = IllegalStateException (migrateStat011: WARN, file untouched; unreachable after migrate011, which always leaves its marker).
# Every line is scanned from the start of a logical line, so "a comment right above" is never the tail of a continued entry.
M(gcf, r"""
public static Object[] stUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = ST_KEY.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int first = -1;
  int above = -1;
  int lv = -1;
  int com = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(ST_MARK_ID) >= 0) return null;
      if (lv < 0 && s.indexOf(LV_MARK_ID) >= 0) lv = k;
      if (s.trim().length() > 0) com = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    int m = stIdx(@PKG@.CfgFile.key(s));
    if (m >= 0) {
      if (first < 0) { first = k; above = (com >= 0 && com == k - 1) ? com : k; }
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      multi[m] = e > k;
    }
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    if (eff[i] == null) continue;
    if (!multi[i] && eff[i].equals(ST_OLD[i])) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(ST_KEY[i]).append(' ').append(ST_OLD[i]).append(" -> ").append(ST_NEW[i]).append(" (").append(ST_WHY[i]).append(')');
      rows.add(ST_KEY[i]);
      rows.add(ST_OLD[i]);
      rows.add(ST_NEW[i]);
    } else if (multi[i] || !eff[i].equals(ST_NEW[i])) {
      kept.add(ST_KEY[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (custom) - the 0.1.1 default is " + ST_NEW[i]);
    }
  }
  if (first < 0 && lv < 0) throw new IllegalStateException("no pool.later / stat.levelFull line and no 0.1.1 level table marker to put the stat defaults marker by");
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = stIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(ST_OLD[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + ST_NEW[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  if (first >= 0) {
    String crA = above + 1 < raw.length ? (raw[above].endsWith("\r") ? "\r" : "") : cr;
    out.add(above, ST_MARK + crA);
  } else if (lv + 1 < raw.length) {
    out.add(lv + 1, ST_MARK + (raw[lv].endsWith("\r") ? "\r" : ""));
  } else {
    out.set(lv, ((String) out.get(lv)) + cr);
    out.add(ST_MARK);
  }
  StringBuilder sb = new StringBuilder(text.length() + ST_MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
M(gcf, r"""
public static String stLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + LV_WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after migrate011 and BEFORE load() + CfgPub.start: the file before this update becomes a History version (KEEP 10,
# verified by lvSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line
# per updated key, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no file,
# marker already there, or a failure - WARN, file untouched, the next start tries again)
M(gcf, r"""
public static synchronized String migrateStat011() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = stUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), LV_WHO, "before the 0.1.1 stat defaults update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.1.1 stat defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(stLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.1 stat defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each line)";
    else msg = "config.properties: no pool.later / stat.levelFull line still had its 0.1 default - nothing changed (0.1.1 stat defaults marker added)";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.Gear.info(kept[i]); all.append('\n').append(kept[i]); }
    @PKG@.GearLog.line("CONFIG 0.1.1 stat defaults: " + (chg.length() > 0 ? chg : "nothing changed") + (kept.length > 0 ? "; " + kept.length + " custom kept" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.1.1 stat defaults (the file is used as it is): " + t);
    return "";
  }
}""")
# ---- 0.1.2 CHARGED ATTACK LINES: the one-time update of an existing config.properties (see the header). The file only GAINS lines
# (the ones a fresh 0.1.2 file has and this one lacks), so every value the loader reads stays what it was (the new keys read their
# built-in defaults either way) - no config-changes.log line, only the History version and one INFO line. Lines are read with the
# kit's own parser (CfgFile.isComment / end / key); ISO-8859-1 chars in and out; every other byte is kept.
# where lines go in: right after the anchor entry (its last physical line), or BEFORE it when that entry reaches the file's last line
# still open - its last line ends in an odd number of backslashes, or it swallowed the final newline (the empty tail is its
# continuation): appended lines would become its continuation (the 0.1.1 review finding 4 trap). The entry's bytes stay last.
M(gcf, r"""
public static int chAfter(java.util.ArrayList l, int s, int e) {
  if (e == l.size() - 1) {
    String le = (String) l.get(e);
    if (le.length() == 0 || @PKG@.CfgFile.cont(le)) return s;
  }
  return e + 1;
}""")
# no anchor: the end of the file (before the final newline's empty tail), or before the last entry when it reaches the last line still
# open (tail = its first line; the same rule as chAfter)
M(gcf, r"""
public static int chEnd(java.util.ArrayList l, int tail, String[] raw) {
  if (tail >= 0) {
    String le = (String) l.get(l.size() - 1);
    if (le.length() == 0 || @PKG@.CfgFile.cont(le)) return tail;
  }
  if (raw.length > 0 && raw[raw.length - 1].length() == 0) return raw.length - 1;
  return raw.length;
}""")
# insert lines at index at of out (a copy of the raw lines, CR kept per line); at == out.size() = append after a last line that has no
# newline: that line gains the CR, the last inserted line gets none (the file still ends without a newline)
M(gcf, r"""
public static void chPut(java.util.ArrayList out, int at, java.util.ArrayList lines, String cr) {
  if (lines.size() == 0) return;
  if (at >= out.size()) {
    int last = out.size() - 1;
    if (last >= 0) {
      String lv = (String) out.get(last);
      if (cr.length() > 0 && !lv.endsWith("\r")) out.set(last, lv + cr);
    }
    for (int i = 0; i < lines.size(); i++) out.add(((String) lines.get(i)) + (i < lines.size() - 1 ? cr : ""));
    return;
  }
  for (int i = 0; i < lines.size(); i++) out.add(at + i, ((String) lines.get(i)) + cr);
}""")
# pure text step. null = the charged marker is already in a comment line - any physical line starting with # or ! that holds the marker
# id, so a marker a later hand edit swallowed into a continued value still counts as done (never a second marker). Else { new text,
# "stats.chg, charged.on, ..." (what was added, "" = only the marker), String[] notes (keys already there - kept) }. Which keys are
# already there is asked of java.util.Properties itself (what the loader reads - a key hidden behind a lone backslash line counts
# too), so the update never shadows an existing value; the kit's parser only finds the places. stats.chg (with its "# chg = ..." line) goes
# right under the last stats.cd entry, else under the last stats. entry, else into the block; the block = the marker + every missing
# charged.* row (its help comment + key=default) goes right under the last speed.per entry, else under the last combat. / crit. /
# steal. / regen. / speed. entry, else at the end of the file. Both are inserted from the bottom up (equal places: stats.chg first).
M(gcf, r"""
public static Object[] chUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(CH_MARK_ID) >= 0) return null;
  }
  int n = CH_ROWK.length;
  boolean[] have = new boolean[n];
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  boolean hasChg = pp.getProperty("stats.chg") != null;
  for (int i = 0; i < n; i++) have[i] = pp.getProperty(CH_ROWK[i]) != null;
  int cdS = -1; int cdE = -1; int stS = -1; int stE = -1; int spS = -1; int spE = -1; int cbS = -1; int cbE = -1; int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null) {
      if (key.equals("stats.cd")) { cdS = k; cdE = e; }
      if (key.startsWith("stats.")) { stS = k; stE = e; }
      if (key.equals("speed.per")) { spS = k; spE = e; }
      if (key.startsWith("combat.") || key.startsWith("crit.") || key.startsWith("steal.") || key.startsWith("regen.") || key.startsWith("speed.")) { cbS = k; cbE = e; }
    }
    k = e + 1;
  }
  StringBuilder added = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList chg = new java.util.ArrayList();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(CH_MARK);
  int aS = cdS >= 0 ? cdS : stS;
  int aE = cdS >= 0 ? cdE : stE;
  if (hasChg) notes.add("stats.chg is already in the file - kept");
  else {
    added.append("stats.chg");
    for (int i = 0; i < CHG_ADD.length; i++) { if (aS >= 0) chg.add(CHG_ADD[i]); else blk.add(CHG_ADD[i]); }
  }
  for (int i = 0; i < n; i++) {
    if (have[i]) { notes.add(CH_ROWK[i] + " is already in the file - kept"); continue; }
    if (added.length() > 0) added.append(", ");
    added.append(CH_ROWK[i]);
    blk.add(CH_ROWC[i]);
    blk.add(CH_ROWL[i]);
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  int bS = spS >= 0 ? spS : cbS;
  int bE = spS >= 0 ? spE : cbE;
  int pB = bS >= 0 ? chAfter(l, bS, bE) : chEnd(l, tail, raw);
  String crB = bS >= 0 && bE < raw.length ? (raw[bE].endsWith("\r") ? "\r" : "") : crDef;
  int pC = chg.size() > 0 ? chAfter(l, aS, aE) : -1;
  String crC = aS >= 0 && aE < raw.length ? (raw[aE].endsWith("\r") ? "\r" : "") : crDef;
  if (pC >= 0 && pC > pB) { chPut(out, pC, chg, crC); chPut(out, pB, blk, crB); }
  else { chPut(out, pB, blk, crB); if (pC >= 0) chPut(out, pC, chg, crC); }
  StringBuilder sb = new StringBuilder(text.length() + 1024);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), added.toString(), (String[]) notes.toArray(new String[0]) };
}""")
# setup(), right after migrateStat011 and BEFORE load() + CfgPub.start: the file before this update becomes a History version (KEEP 10,
# verified by lvSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one INFO line (+ one
# per note). Returns the INFO line(s) joined by \n ("" = nothing done: no file, marker already there, or a failure - WARN, file
# untouched, the next start tries again). A fresh file (the loader writes the 0.1.2 default text) carries the marker and never updates.
M(gcf, r"""
public static synchronized String migrate012() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = chUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), CH_WHO, "before the 0.1.2 charged attack lines");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT given the 0.1.2 charged attack lines: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - the new settings run on their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String add = (String) r[1];
    String[] notes = (String[]) r[2];
    String msg = add.length() > 0
      ? "config.properties: added the 0.1.2 Charged Attack Damage lines (" + add + ") with their built-in defaults - nothing changes in effect; the old file is in config-history"
      : "config.properties: the 0.1.2 Charged Attack Damage lines were already there - nothing added (0.1.2 marker added)";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.1.2 charged attack lines: " + (add.length() > 0 ? add : "nothing added"));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.1.2 charged attack lines to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
# ---- 0.1.3 LEVEL FAMILY ROWS: the one-time update of an existing config.properties (see the header). The file only GAINS lines - the
# family rows it does not have yet - under the marker FM_MARK; no line is ever changed or removed. Unlike the 0.1.2 lines these DO change
# levels (those items used Hytale's ItemLevel before), so each added row gets a config-changes.log line (old "(none)") that Server Setup
# -> Changes can undo (the kit's inverse = remove). Lines are read with the kit's own parser; ISO-8859-1 chars in and out.
# pure text step. null = the family marker is already in a comment line (any physical line starting with # or ! that holds the marker
# id). Else { new text, "Wool 5, Linen 10, ..." (what was added, "" = only the marker), String[] notes (entries already there - kept),
# String[] { entry, level }* }. An entry is already there when java.util.Properties (what the loader reads) has any level.material.<x>
# key whose x matches it in any case (the loader lower-cases entries). Place: right after the last level.material entry (chAfter: before
# it when it reaches the file's last line still open), else right under the 0.1.1 level marker / the levels header (a comment line, so
# nothing can continue into the block), else the end of the file (chEnd).
M(gcf, r"""
public static Object[] fmUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(FM_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  java.util.HashSet have = new java.util.HashSet();
  java.util.Iterator it = pp.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String pk = (String) it.next();
    if (pk.startsWith("level.material.") && pk.length() > 15) have.add(pk.substring(15).toLowerCase());
  }
  int mS = -1; int mE = -1; int mark = -1; int head = -1; int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (mark < 0 && s.indexOf(LV_MARK_ID) >= 0) mark = k;
      if (head < 0 && s.trim().equals(LV_HEAD)) head = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null && key.startsWith("level.material.")) { mS = k; mE = e; }
    k = e + 1;
  }
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(FM_MARK);
  StringBuilder added = new StringBuilder();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.ArrayList notes = new java.util.ArrayList();
  for (int i = 0; i < FAM_T.length; i++) {
    if (have.contains(FAM_T[i].toLowerCase())) { notes.add("level.material." + FAM_T[i] + " is already in the file - kept"); continue; }
    blk.add("level.material." + FAM_T[i] + "=" + FAM_L[i]);
    if (added.length() > 0) added.append(", ");
    added.append(FAM_T[i]).append(' ').append(FAM_L[i]);
    rows.add(FAM_T[i]);
    rows.add(String.valueOf(FAM_L[i]));
  }
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  int at = -1;
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  if (mS >= 0) {
    at = chAfter(l, mS, mE);
    cr = mE < raw.length && raw[mE].endsWith("\r") ? "\r" : "";
  } else if (mark >= 0 || head >= 0) {
    int c = mark >= 0 ? mark : head;
    at = c + 1;
    cr = raw[c].endsWith("\r") ? "\r" : "";
  } else {
    at = chEnd(l, tail, raw);
  }
  chPut(out, at, blk, cr);
  StringBuilder sb = new StringBuilder(text.length() + 4096);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), added.toString(), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]) };
}""")
# one config-changes.log line per added row in the kit's table format: old "(none)" = the entry did not exist (Undo = remove)
M(gcf, r"""
public static String fmLog(String e, String n) {
  return @PKG@.CfgLog.now() + "\t" + FM_WHO + "\t-\tupdate\tlevel.material[" + @PKG@.CfgRows.oneLine(e) + "]\t(none)\t" + n + "\tok";
}""")
# setup(), right after migrate012 and BEFORE load() + CfgPub.start: the file before this update becomes a History version (KEEP 10,
# verified by lvSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line
# per added row, one INFO line (+ one per note). Returns the INFO line(s) joined by \n ("" = nothing done: no file, marker already there,
# or a failure - WARN, file untouched, the next start tries again). A fresh file (the loader writes the 0.1.3 default text) carries the
# marker and never updates.
M(gcf, r"""
public static synchronized String migrate013() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = fmUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), FM_WHO, "before the 0.1.3 level family rows");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT given the 0.1.3 level family rows: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - those items keep Hytale's item level; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 1 < rows.length; i += 2) @PKG@.CfgLog.enqueue(fmLog(rows[i], rows[i + 1]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String add = (String) r[1];
    String[] notes = (String[]) r[2];
    String msg = add.length() > 0
      ? "config.properties: added " + (rows.length / 2) + " level family rows (" + add + ") - those weapons and armor use these levels now instead of Hytale's item level; the old file is in config-history, Server Setup -> Changes can undo each row"
      : "config.properties: every 0.1.3 level family row was already there - nothing added (0.1.3 marker added)";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.1.3 level families: " + (rows.length / 2) + " rows added" + (notes.length > 0 ? "; " + notes.length + " already there" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.1.3 level family rows to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
# ---- 0.2 LEVEL BANDS: the one-time update of an existing config.properties (see the header; the 0.1.1 level update's rules for the
# value rewrite, the 0.1.2 / 0.1.3 updates' rules for the added lines). bdIdx = the 0.1.3 default row of a level.material. key (entry in any
# case, the loader's rule) -> the BO_T index, -1 = none
M(gcf, r"""
public static int bdIdx(String k) {
  if (k == null || k.length() <= 15 || !k.startsWith("level.material.")) return -1;
  String e = k.substring(15);
  for (int i = 0; i < BO_T.length; i++) if (BO_T[i].equalsIgnoreCase(e)) return i;
  return -1;
}""")
# the 0.2 default band { min, cap } of BO_T[i] (BD_T lists the same entries), null = none
M(gcf, r"""
public static int[] bdNew(int i) {
  if (i < 0 || i >= BO_T.length) return null;
  for (int j = 0; j < BD_T.length; j++) if (BD_T[j].equalsIgnoreCase(BO_T[i])) return new int[] { BD_MIN[j], BD_CAP[j] };
  return null;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser CfgFile.isComment / end / key / value). null = the
# bands marker is already in a comment line (any physical line starting with # or ! that holds the marker id). Else { new text,
# "Crude 0 -> 1-13, ..., added Armor_Copper 1-18" (what changed), String[] notes (custom values / keys already there - kept),
# String[] { entry, old, new }* (the change-log rows), "part.levels, ..." (the settings added) }.
# (1) BANDS: an entry whose LAST live line (the one java.util.Properties keeps) is a one-line entry holding exactly its 0.1.3 default
# text (BO_V) is updated: every one-line entry of it holding that text gets the 0.2 band "<min>,<cap>" (value text only: key, separator
# and CR stay; one line stays one line). Anything else is kept: a custom value (noted unless it already is the 0.2 band - a custom one
# number now reads N to N + width - 1), a continued entry (noted), a missing line (silent). The change-log row's OLD value is what that old
# one number means in 0.2 (N|N+width-1, the file's own level.bandWidth when it has one), because Server Setup's Undo sends it back
# through the 2-column table, which refuses a single cell; the History copy keeps the exact old bytes.
# (2) ARMOR_COPPER (LOCKED 2026-10-01): no level.material.Armor_Copper line (any case) = add "level.material.Armor_Copper=1,18" right
# after the last level.material.Copper entry (else in the block's place, first); its change-log row has old "(none)" (Undo = remove).
# A line holding exactly 1 (what OPEN-QUESTIONS told Skyy to type until now) is rule (1); any other value is kept.
# (3) THE BLOCK: the marker + the help comment and key=default line of every new 0.2 setting the file does not have (asked of
# java.util.Properties, what the loader reads), right after the last level.material entry (chAfter: before it when it reaches the file's
# last line still open), else right under the 0.1.1 level marker / the levels header, else at the end of the file (chEnd). The settings
# start at their built-in defaults, so they get no change-log line (the 0.1.2 rule). Insertions run from the bottom up.
M(gcf, r"""
public static Object[] bdUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(BD_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int w = BAND_W_DEF;
  try {
    String bv = pp.getProperty("level.bandWidth");
    if (bv != null) { int x = (int) Math.floor(Double.parseDouble(clean(bv.trim()))); if (x >= 1 && x <= 50) w = x; }
  } catch (Throwable x2) { w = BAND_W_DEF; }
  int n = BO_T.length;
  String[] eff = new String[n];
  String[] ent = new String[n];
  boolean[] multi = new boolean[n];
  int mS = -1; int mE = -1; int cS = -1; int cE = -1; int mark = -1; int head = -1; int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (mark < 0 && s.indexOf(LV_MARK_ID) >= 0) mark = k;
      if (head < 0 && s.trim().equals(LV_HEAD)) head = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null && key.startsWith("level.material.") && key.length() > 15) {
      mS = k;
      mE = e;
      if (key.substring(15).equalsIgnoreCase("Copper")) { cS = k; cE = e; }
    }
    int m = bdIdx(key);
    if (m >= 0) {
      eff[m] = @PKG@.CfgFile.value(l, k).trim();
      ent[m] = key.substring(15);
      multi[m] = e > k;
    }
    k = e + 1;
  }
  boolean[] mig = new boolean[n];
  String[] nv = new String[n];
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList kept = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  int armor = -1;
  for (int i = 0; i < n; i++) {
    int[] b = bdNew(i);
    if (b == null) continue;
    nv[i] = b[0] + "," + b[1];
    if (eff[i] == null) {
      if (BO_T[i].equals("Armor_Copper")) armor = i;
      continue;
    }
    if (!multi[i] && eff[i].equals(BO_V[i])) {
      mig[i] = true;
      int om = Integer.parseInt(BO_V[i]);
      if (chg.length() > 0) chg.append(", ");
      chg.append(ent[i]).append(' ').append(BO_V[i]).append(" -> ").append(b[0]).append('-').append(b[1]);
      rows.add(ent[i]);
      rows.add(om + "|" + capOf(om, w));
      rows.add(b[0] + "|" + b[1]);
    } else if (multi[i] || !eff[i].equals(nv[i])) {
      kept.add("level.material." + ent[i] + "=" + @PKG@.CfgRows.oneLine(eff[i]) + " kept (custom) - the 0.2 default band is " + b[0] + "-" + b[1]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    int m2 = bdIdx(@PKG@.CfgFile.key(s2));
    if (m2 >= 0 && mig[m2] && e2 == k && @PKG@.CfgFile.value(l, k).trim().equals(BO_V[m2])) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + nv[m2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(BD_MARK);
  StringBuilder added = new StringBuilder();
  for (int i = 0; i < BD_ROWK.length; i++) {
    if (pp.getProperty(BD_ROWK[i]) != null) { kept.add(BD_ROWK[i] + " is already in the file - kept"); continue; }
    blk.add(BD_ROWC[i]);
    blk.add(BD_ROWL[i]);
    if (added.length() > 0) added.append(", ");
    added.append(BD_ROWK[i]);
  }
  java.util.ArrayList arm = new java.util.ArrayList();
  if (armor >= 0) {
    int[] ab = bdNew(armor);
    arm.add("level.material." + BO_T[armor] + "=" + ab[0] + "," + ab[1]);
    rows.add(BO_T[armor]);
    rows.add("(none)");
    rows.add(ab[0] + "|" + ab[1]);
    if (chg.length() > 0) chg.append(", ");
    chg.append("added ").append(BO_T[armor]).append(' ').append(ab[0]).append('-').append(ab[1]);
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  int pB = -1;
  String crB = crDef;
  if (mS >= 0) {
    pB = chAfter(l, mS, mE);
    crB = mE < raw.length && raw[mE].endsWith("\r") ? "\r" : "";
  } else if (mark >= 0 || head >= 0) {
    int c = mark >= 0 ? mark : head;
    pB = c + 1;
    crB = raw[c].endsWith("\r") ? "\r" : "";
  } else {
    pB = chEnd(l, tail, raw);
  }
  if (arm.size() > 0 && cS >= 0) {
    int pA = chAfter(l, cS, cE);
    String crA = cE < raw.length && raw[cE].endsWith("\r") ? "\r" : "";
    if (pA == pB) { arm.addAll(blk); chPut(out, pB, arm, crB); }
    else if (pA > pB) { chPut(out, pA, arm, crA); chPut(out, pB, blk, crB); }
    else { chPut(out, pB, blk, crB); chPut(out, pA, arm, crA); }
  } else if (arm.size() > 0) {
    arm.addAll(blk);
    chPut(out, pB, arm, crB);
  } else {
    chPut(out, pB, blk, crB);
  }
  StringBuilder sb = new StringBuilder(text.length() + 2048);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) kept.toArray(new String[0]), (String[]) rows.toArray(new String[0]), added.toString() };
}""")
# one config-changes.log line per band row in the kit's table format (key tableKey[entry], the columns joined by |; old "(none)" = the
# row did not exist): Server Setup -> Changes undoes it (tset back / remove)
M(gcf, r"""
public static String bdLog(String e, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + BD_WHO + "\t-\tupdate\tlevel.material[" + @PKG@.CfgRows.oneLine(e) + "]\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after migrate013 and BEFORE load() + CfgPub.start: the file before this update becomes a History version (KEEP 10,
# verified by lvSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log line
# per band row it changed or added, one INFO line (+ one per note). Returns the INFO line(s) joined by \n ("" = nothing done: no file,
# marker already there, or a failure - WARN, file untouched, the next start tries again). A fresh file (the loader writes the 0.2
# default text) carries the marker and never updates.
M(gcf, r"""
public static synchronized String migrate02() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = bdUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), BD_WHO, "before the 0.2 level bands");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.2 level bands: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - one-number rows cover N to N + " + BAND_W_DEF + " - 1; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(bdLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String add = (String) r[4];
    String msg = chg.length() > 0
      ? "config.properties updated to the 0.2 level bands: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo each band)"
      : "config.properties: no level.material row still had its 0.1.3 default - no band changed (0.2 marker added)";
    if (add.length() > 0) msg = msg + "; new settings with their defaults: " + add;
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { @PKG@.Gear.info(kept[i]); all.append('\n').append(kept[i]); }
    @PKG@.GearLog.line("CONFIG 0.2 level bands: " + (rows.length / 3) + " band rows" + (add.length() > 0 ? "; added " + add : "") + (kept.length > 0 ? "; " + kept.length + " kept" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.2 level bands (the file is used as it is): " + t);
    return "";
  }
}""")
# ---- 0.2.1 LEVEL STATS LINES: the one-time update of an existing config.properties (the migrate012 pattern). The file only GAINS lines
# (the 0.2.1 settings a fresh 0.2.1 file has and this one lacks: the six scalar rows with their help comment, the base.armor table comment
# + its four slot lines), so no value the loader already reads changes - no config-changes.log line (the 0.1.2 rule: new settings start
# at their defaults), only the History version and one INFO line. Lines are read with the kit's own parser; ISO-8859-1 chars in and out.
# pure text step. null = the marker is already in a comment line (any physical line starting with # or ! that holds the marker id). Else
# { new text, "part.base, base.mode, ..." (what was added, "" = only the marker), String[] notes (keys already there - kept) }. Which
# keys are there is asked of java.util.Properties itself (a base.armor.<slot> line in any case of the slot word counts), so the update
# never shadows an existing value. The block = the marker + every missing scalar row (help + key=default) + the table comment and the
# missing slot lines (the comment only when a slot line is added); it goes right after the last level.armorNative entry (where a fresh
# file has it), else after the last level.* entry, else at the end of the file (chAfter / chEnd: the end-of-file continuation trap).
M(gcf, r"""
public static Object[] lsUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(LS_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int n = LS_ROWK.length;
  boolean[] have = new boolean[n];
  for (int i = 0; i < n; i++) have[i] = pp.getProperty(LS_ROWK[i]) != null;
  boolean[] slot = new boolean[BA_SLOT.length];
  java.util.Iterator it = pp.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k0 = (String) it.next();
    if (!k0.startsWith("base.armor.")) continue;
    for (int i = 0; i < BA_SLOT.length; i++) if (BA_SLOT[i].equalsIgnoreCase(k0.substring(11))) slot[i] = true;
  }
  int aS = -1; int aE = -1; int vS = -1; int vE = -1; int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null) {
      if (key.equals("level.armorNative")) { aS = k; aE = e; }
      if (key.startsWith("level.")) { vS = k; vE = e; }
    }
    k = e + 1;
  }
  StringBuilder added = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add(LS_MARK);
  for (int i = 0; i < n; i++) {
    if (have[i]) { notes.add(LS_ROWK[i] + " is already in the file - kept"); continue; }
    if (added.length() > 0) added.append(", ");
    added.append(LS_ROWK[i]);
    blk.add(LS_ROWC[i]);
    blk.add(LS_ROWL[i]);
  }
  boolean tc = false;
  for (int i = 0; i < BA_SLOT.length; i++) {
    if (slot[i]) { notes.add("base.armor." + BA_SLOT[i] + " is already in the file - kept"); continue; }
    if (!tc) { blk.add(LS_TBLC); tc = true; }
    blk.add(LS_TBLL[i]);
    if (added.length() > 0) added.append(", ");
    added.append("base.armor." + BA_SLOT[i]);
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  int bS = aS >= 0 ? aS : vS;
  int bE = aS >= 0 ? aE : vE;
  int pB = bS >= 0 ? chAfter(l, bS, bE) : chEnd(l, tail, raw);
  String crB = bS >= 0 && bE < raw.length ? (raw[bE].endsWith("\r") ? "\r" : "") : crDef;
  chPut(out, pB, blk, crB);
  StringBuilder sb = new StringBuilder(text.length() + 2048);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), added.toString(), (String[]) notes.toArray(new String[0]) };
}""")
# setup(), right after migrate02 and BEFORE load() + CfgPub.start: the file before this update becomes a History version (KEEP 10,
# verified by lvSaved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one INFO line (+ one per
# note). Returns the INFO line(s) joined by \n ("" = nothing done: no file, marker already there, or a failure - WARN, file untouched,
# the next start tries again; the loader then runs the missing settings on their built-in defaults anyway). A fresh file (the loader
# writes the 0.2.1 default text) carries the marker and never updates.
M(gcf, r"""
public static synchronized String migrate021() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = lsUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), LS_WHO, "before the 0.2.1 level stats");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT given the 0.2.1 level stats settings: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - the new settings run on their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String add = (String) r[1];
    String[] notes = (String[]) r[2];
    String msg = add.length() > 0
      ? "config.properties: added the 0.2.1 level stats settings (" + add + ") with their built-in defaults - weapon damage and armor Health / resistance now grow with each item's level (Server Setup -> Gear -> Level stats; part.base off = vanilla numbers); the old file is in config-history"
      : "config.properties: the 0.2.1 level stats settings were already there - nothing added (0.2.1 marker added)";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.1 level stats: " + (add.length() > 0 ? add : "nothing added"));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.2.1 level stats settings to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
# 0.2.1 ready line part: the base stats in force (live values)
M(gcf, r"""
public static String baseText() {
  if (!PART_BASE) return "base stats by level OFF (part.base: vanilla weapon damage and armor values; levels and requirements stay)";
  String w = "off".equals(BASE_MODE) ? "weapon damage vanilla (base.mode off)" : "weapon damage = vanilla step x K x F(level) x (1 + " + BASE_MAT + "% x band start), F = " + BASE_CURVE;
  String a = BASE_ARMOR ? "armor Health (F) + resistance (R = " + BASE_RES + ") per piece from its slot's Lv 1 values" : "armor values vanilla (base.armorOn off)";
  return w + "; " + a;
}""")
# a band as text ("10-18", one level = "10"); a missing cap = the width rule
M(gcf, r"""
public static String bandOf(Object mn, Object cp) {
  if (!(mn instanceof Integer)) return "-";
  int a = ((Integer) mn).intValue();
  int b = cp instanceof Integer ? ((Integer) cp).intValue() : capOf(a, BAND_W);
  return a == b ? String.valueOf(a) : a + "-" + b;
}""")
# 0.2 ready line part: the magic weapon recipes this jar's asset pack ships (setup() runs before the asset packs load, so it only names them)
M(gcf, r"""
public static String recipeText() {
  return RCP_ID.length + " wand / staff recipes in the asset pack (each = the same material's shortbow recipe: Weapon Bench Bow tab, Wood also the Workbench Survival tab)";
}""")
# 0.2 ready line part: the level settings in force
M(gcf, r"""
public static String levelText() {
  if (!PART_LEVELS) return "item levels OFF (part.levels: nothing new is stamped, every item reads its band start)";
  return "levels stored on new gear (crafted at the crafter's " + ("gate".equals(CRAFT_FROM) ? "skill level" : "band start") + " inside the material band; below a band: " + ("block".equals(CRAFT_BELOW) ? "refused at benches" : "made at the band start") + "), gate floor " + GATE_FLOOR + ", one-number rows " + BAND_W + " wide";
}""")
# the ready line's stat part: the LIVE values after load() (a kept custom pool.later=true says so loudly)
M(gcf, r"""
public static String statText() {
  String p = POOL_LATER ? "coming-later stats ROLL (pool.later on - the 0.1.1 default is off)" : "coming-later stats never roll";
  return p + "; full modifier power from item level " + LEVEL_FULL;
}""")
# the ready line's level table (0.2: bands): the live band of every metal row incl. Armor_Copper ("-" = no line: the item's own level
# applies), then how many of the 59 family rows the file has and how many still hold their 0.2 default band, then any other entry the file
# adds (lower case)
M(gcf, r"""
public static String matText() {
  java.util.HashMap m = MAT;
  java.util.HashMap cp = MATCAP;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < BD_METALS; i++) {
    String k = BD_T[i].toLowerCase();
    if (i > 0) sb.append(", ");
    sb.append(BD_T[i]).append(' ').append(bandOf(m.get(k), cp.get(k)));
  }
  int fam = 0;
  int famDef = 0;
  for (int i = BD_METALS; i < BD_T.length; i++) {
    String k = BD_T[i].toLowerCase();
    Object v = m.get(k);
    if (v == null) continue;
    fam++;
    Object c = cp.get(k);
    if (v instanceof Integer && ((Integer) v).intValue() == BD_MIN[i] && c instanceof Integer && ((Integer) c).intValue() == BD_CAP[i]) famDef++;
  }
  sb.append("; ").append(fam).append(" of ").append(BD_T.length - BD_METALS).append(" family rows (").append(famDef).append(" at the 0.2 default band)");
  java.util.ArrayList extra = new java.util.ArrayList();
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    boolean known = false;
    for (int j = 0; j < BD_T.length; j++) if (BD_T[j].toLowerCase().equals(k)) known = true;
    if (!known) extra.add(k);
  }
  java.util.Collections.sort(extra);
  for (int i = 0; i < extra.size(); i++) sb.append(", ").append((String) extra.get(i)).append(' ').append(bandOf(m.get(extra.get(i)), cp.get(extra.get(i))));
  return sb.toString();
}""")
M(gcf, r"""
public static String[] excl() {
  String s = EXCLUDE;
  if (s != EXCL_SRC) {
    java.util.ArrayList l = new java.util.ArrayList();
    if (s != null) {
      String[] ps = s.split(",");
      for (int i = 0; i < ps.length; i++) { String t = ps[i].trim(); if (t.length() > 0) l.add(t); }
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    EXCL = a;
    EXCL_SRC = s;
  }
  return EXCL;
}""")
M(gcf, r"""
public static String[] names() {
  String s = NAMES;
  if (s != NAMES_SRC) {
    java.util.ArrayList l = new java.util.ArrayList();
    if (s != null) {
      String[] ps = s.split(",");
      for (int i = 0; i < ps.length; i++) {
        String t = ps[i].trim();
        if (t.length() > 0 && t.length() <= 24 && @PKG@.GearDefs.rIndex(t) < 0) l.add(t);
      }
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    RF = a;
    NAMES_SRC = s;
  }
  return RF;
}""")
# follow-up review 1: a gear.include entry that would pull whole families in ("Skyy_" = menus, food, vaults ...; "Weapon_Arrow_"-style
# short ones) is refused: why (null = fine). The row check refuses it in game; the loader drops it from a hand edit with one WARN.
M(gcf, r"""
public static String inclBad(String t) {
  if (t == null) return null;
  for (int i = 0; i < @PKG@.GearDefs.INCL_BARE.length; i++) if (@PKG@.GearDefs.INCL_BARE[i].equalsIgnoreCase(t)) return t + " is a whole item family - name a narrower prefix such as Skyy_Ring_ or Tool_Pickaxe_.";
  if (t.length() < @PKG@.GearDefs.INCL_MIN) return t + " is too short - a gear.include prefix needs at least " + @PKG@.GearDefs.INCL_MIN + " characters (e.g. Skyy_Ring_).";
  return null;
}""")
M(gcf, r"""
public static String[] incl() {
  String s = INCLUDE;
  if (s != INCL_SRC) {
    java.util.ArrayList l = new java.util.ArrayList();
    if (s != null) {
      String[] ps = s.split(",");
      for (int i = 0; i < ps.length; i++) {
        String t = ps[i].trim();
        if (t.length() == 0) continue;
        String bad = inclBad(t);
        if (bad != null) { @PKG@.Gear.warnOnce("inclbad:" + t, "config.properties: gear.include entry " + bad + " - ignored"); continue; }
        l.add(t);
      }
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    INCL = a;
    INCL_SRC = s;
  }
  return INCL;
}""")
# design review 9: where a player identifies (identify.command live): ": /identify" or nothing ("Identify it first")
M(gcf, "public static String idHow() { return IDENTIFY_CMD ? \": /identify\" : \"\"; }")
M(gcf, "public static String idWhere() { return IDENTIFY_CMD ? \"/identify\" : \"at the identifier\"; }")
M(gcf, "public static int craftMax() { return rchoice(CRAFT_MAX, 5, 4); }")
M(gcf, "public static int migrateMax() { return rchoice(MIGRATE_MAX, 4, 4); }")
M(gcf, r"""
public static long cfgEpoch() {
  Object o = @PKG@.Gear.bget("config:epoch:SkyyGear");
  long k = o instanceof Number ? ((Number) o).longValue() : 0L;
  return EPOCH * 1000003L + k;
}""")
M(gcf, r"""
public static int ri(int r) {
  if (r < 0 || r >= @PKG@.GearDefs.NR) return 0;
  return r;
}""")
M(gcf, r"""
public static long costReforge(int r, int lvl) {
  int i = ri(r);
  long c = CR_BASE[i] + CR_PER[i] * (long) (lvl < 0 ? 0 : lvl);
  return c < 0L ? 0L : c;
}""")
M(gcf, r"""
public static long costIdentify(int r, int lvl) {
  int i = ri(r);
  long c = CI_BASE[i] + CI_PER[i] * (long) (lvl < 0 ? 0 : lvl);
  return c < 0L ? 0L : c;
}""")
M(gcf, "public static long xpReforge(int r) { return XPR[ri(r)]; }")
# ---- check= hooks (tools/CONFIG-CONTRACT.md: key = tableKey[entry], value = columns joined by |, null = removal)
M(gcf, r"""
public static String entryOf(String key) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int z = key.lastIndexOf(']');
  if (a < 0 || z <= a + 1) return null;
  return key.substring(a + 1, z);
}""")
M(gcf, r"""
public static String checkRarityKey(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  int r = @PKG@.GearDefs.rIndex(e);
  if (r < 0 || !@PKG@.GearDefs.R_ID[r].equals(e)) return "Unknown rarity " + e + " - use normal, unique, rare, legendary, fabled, mythic or set (lower case).";
  return null;
}""")
M(gcf, r"""
public static String checkRarity(String key, String value) {
  String bad = checkRarityKey(key, value);
  if (bad != null || value == null) return bad;
  double[] c = cells(value, 3);
  if (c != null && c[2] < c[1]) return "High % must be at least Low % (the roll range gets wider and higher with rarity).";
  return null;
}""")
M(gcf, r"""
public static String checkMigKey(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  for (int i = 0; i < @PKG@.GearDefs.MIG_ID.length; i++) if (@PKG@.GearDefs.MIG_ID[i].equals(e)) return null;
  return "Old SkyyRolls items can only become unique, rare, legendary or fabled (anything lower is normal).";
}""")
M(gcf, r"""
public static String checkKind(String key, String value) {
  if (value == null) return null;
  String v = value.trim().toLowerCase();
  if (!kindOk(v)) return "Use combat, mining, foraging, farming or equipment.";
  return null;
}""")
M(gcf, r"""
public static String checkInclude(String key, String value) {
  if (value == null) return null;
  String[] ps = value.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    String bad = inclBad(t);
    if (bad != null) return bad;
  }
  return null;
}""")
M(gcf, r"""
public static String checkStat(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  int i = @PKG@.GearDefs.sIndex(e);
  if (i < 0) return "Unknown stat " + e + " - use a key from the list above each stats line in config.properties (dmg, str, mp, cc ...).";
  if (value == null) return null;
  double[] c = cells(value, 2);
  if (c == null) return null;
  long mx = (long) c[0];
  int d = @PKG@.GearDefs.S_MAXDEF[i];
  String lab = @PKG@.GearDefs.S_LABEL[i];
  if (d > 0 && mx == 0L) return "?" + lab + " max 0 means every " + lab + " roll on new items is 1. Save anyway?";
  if (d > 0 && mx > 4L * (long) d) return "?" + lab + " max " + mx + " is " + (mx / (long) d) + " x the default " + d + " - every " + lab + " roll on new items changes. Save anyway?";
  return null;
}""")
M(gcf, r"""
public static String checkNames(String key, String value) {
  if (value == null) return null;
  String[] ns = value.split(",");
  for (int i = 0; i < ns.length; i++) {
    String t = ns[i].trim();
    if (t.length() == 0) continue;
    if (@PKG@.GearDefs.rIndex(t) >= 0) return t + " is a rarity name - reforge names may not be rarity names.";
    if (t.length() > 24) return t + " is longer than 24 characters.";
  }
  return null;
}""")
# 0.2: a band row's cap is never below its min (the kit already checked both are whole numbers 0-100); null = a removal / fine
M(gcf, r"""
public static String checkBand(String key, String value) {
  if (value == null) return null;
  double[] c = cells(value, 2);
  if (c == null) return null;
  if (c[1] < c[0]) return "Cap must be at least Min (the band runs from Min to Cap; Min = Cap = exactly one level).";
  return null;
}""")
# 0.2 craft.weaponSkill: a comma list of prefix:Skill pairs (both sides non-empty)
M(gcf, r"""
public static String checkCraftSkill(String key, String value) {
  if (value == null) return null;
  String[] ps = value.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    if (t.length() == 0) continue;
    int c = t.indexOf(':');
    if (c <= 0 || c >= t.length() - 1 || t.substring(0, c).trim().length() == 0 || t.substring(c + 1).trim().length() == 0)
      return t + " - write prefix:Skill pairs, e.g. Weapon_Shortbow_:Archery, Weapon_Wand_:Divinity.";
  }
  return null;
}""")
# 0.2.1 base.armor: the entry is an armor slot (Head, Chest, Legs, Hands - any case), Health >= 0, resistance 0-100 %
M(gcf, r"""
public static String checkArmorBase(String key, String value) {
  String e = entryOf(key);
  if (e != null) {
    boolean ok = false;
    for (int i = 0; i < BA_SLOT.length; i++) if (BA_SLOT[i].equalsIgnoreCase(e)) ok = true;
    if (!ok) return "Unknown armor slot " + e + " - use Head, Chest, Legs or Hands (there is no Feet slot in Hytale).";
  }
  if (value == null) return null;
  double[] c = cells(value, 2);
  if (c != null && (c[0] < 0.0 || c[1] < 0.0 || c[1] > 100.0)) return "Health must be 0 or more and resistance 0-100 % (6.48 = 6.48 % less Physical / Projectile damage).";
  return null;
}""")

# ================================================================= GearQual (engine review 4): per-stack Quality is saved as an INTEGER
# index (ItemStack.CODEC key Quality, load-order indices). The resolved Skyy_Gear_* indices are kept in quality.properties; when
# they move between starts: one WARN. Follow-up review 7: no config-epoch bump - GearView.apply already rewrites every stack whose
# effective quality differs from its stored index (effQ != curQ skips the "unchanged" early return, VERIFIED in apply below), and
# the join scan runs apply on every stack. A stack whose stored index no longer resolves to a quality asset is rewritten the same
# way. Nothing else trusts a raw index: the sig carries the quality's asset id. An unreadable quality.properties is never
# overwritten (one WARN; the admin deletes it and the next start writes a new one).
gql.addInterface(pool.get("java.lang.Runnable"))
F(gql, "public static volatile int[] OLD = null;")                  # indices of the last start (null = no file yet)
F(gql, "public static volatile java.nio.file.Path FILE;")
F(gql, "public static volatile boolean CHECKED = false;")
F(gql, "public static volatile boolean MOVED = false;")
F(gql, "public static volatile boolean UNREAD = false;")            # the file exists but could not be read: never overwrite it
F(gql, "public String text;")
C(gql, "public GearQual(String text) { this.text = text; }")
M(gql, r"""
public static int[] parse(java.util.Properties p) {
  int nr = @PKG@.GearDefs.NR;
  int[] q = new int[nr];
  boolean any = false;
  for (int i = 0; i < nr; i++) {
    q[i] = -1;
    String v = p.getProperty(@PKG@.GearDefs.R_QID[i]);
    if (v == null) continue;
    try { q[i] = Integer.parseInt(v.trim()); any = true; } catch (Throwable t) { q[i] = -1; }
  }
  if (!any) return null;
  return q;
}""")
M(gql, r"""
public static String text(int[] q) {
  StringBuilder sb = new StringBuilder("# SkyyGear: the Skyy_Gear_* quality asset indices of the last start (engine review 4)\n");
  for (int i = 0; q != null && i < q.length && i < @PKG@.GearDefs.NR; i++) sb.append(@PKG@.GearDefs.R_QID[i]).append('=').append(q[i]).append('\n');
  return sb.toString();
}""")
# a known key whose value is not a whole number = the file is damaged (an empty file or one without our keys is not)
M(gql, r"""
public static boolean damaged(java.util.Properties p) {
  for (int i = 0; i < @PKG@.GearDefs.NR; i++) {
    String v = p.getProperty(@PKG@.GearDefs.R_QID[i]);
    if (v == null) continue;
    try { Integer.parseInt(v.trim()); } catch (Throwable t) { return true; }
  }
  return false;
}""")
M(gql, r"""
public static void load(java.nio.file.Path f) {
  FILE = f;
  UNREAD = false;
  String why = null;
  try {
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = @PKG@.GearCfg.read(f);
      OLD = parse(p);
      if (damaged(p)) why = "a value is not a whole number";
    }
  } catch (Throwable t) { why = String.valueOf(t); }
  if (why != null) {
    OLD = null;
    UNREAD = true;
    @PKG@.Gear.warnOnce("qualread", "quality.properties could not be read (" + why + ") - it is left as it is and moved quality indices are not detected this start; delete it and the next start writes a new one");
  }
}""")
# true = a stored index differs from the index resolved now (only known entries count)
M(gql, r"""
public static boolean differs(int[] old, int[] now) {
  if (old == null || now == null) return false;
  for (int i = 0; i < old.length && i < now.length; i++) if (old[i] >= 0 && now[i] >= 0 && old[i] != now[i]) return true;
  return false;
}""")
# a stack index that was a Skyy_Gear_* quality at the last start (a stale frame once the assets are gone or moved)
M(gql, r"""
public static boolean wasOurs(int idx) {
  int[] o = OLD;
  if (o == null || idx < 0) return false;
  for (int i = 0; i < o.length; i++) if (o[i] == idx) return true;
  return false;
}""")
M(gql, r"""
public void run() {
  if (UNREAD) return;
  try { if (FILE != null) @PKG@.GearCfg.writeAtomic(FILE, this.text, true); }
  catch (Throwable t) { @PKG@.Gear.warnOnce("qualwrite", "could not write quality.properties: " + t); }
}""")
# once per start, after the first full resolution: compare, WARN, persist (off the world thread; never over an unreadable file)
M(gql, r"""
public static void check(int[] now) {
  if (CHECKED || now == null) return;
  CHECKED = true;
  int[] old = OLD;
  boolean moved = differs(old, now);
  if (moved) {
    MOVED = true;
    @PKG@.Gear.warnOnce("qualmove", "the Skyy_Gear_* quality indices moved since the last start (" + text(old).replace('\n', ' ') + "-> now " + text(now).replace('\n', ' ') + ") - every gear item gets today's quality when its owner's inventory is scanned (join)");
  }
  boolean same = old != null && !moved;
  if (same) for (int i = 0; i < now.length && i < old.length; i++) if (old[i] != now[i]) same = false;
  if (same || FILE == null || UNREAD) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearQual(text(now)), 100L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { @PKG@.Gear.warnOnce("qualwrite", "could not schedule the quality.properties write: " + t); }
}""")
M(gdf, r"""
public static int qIndex(int r) {
  int[] q = QIDX;
  if (q == null || (QMISS > 0L && System.currentTimeMillis() - QMISS > 60000L)) {
    q = new int[R_QID.length];
    boolean miss = false;
    for (int i = 0; i < R_QID.length; i++) {
      q[i] = -1;
      try {
        int ix = @IQ@.getAssetMap().getIndex(R_QID[i]);
        Object a = ix < 0 ? null : @IQ@.getAssetMap().getAsset(ix);
        if (a instanceof @IQ@ && R_QID[i].equals(((@IQ@) a).getId())) q[i] = ix;
      } catch (Throwable t) { q[i] = -1; }
      if (q[i] < 0) miss = true;
    }
    if (miss) @PKG@.Gear.warnOnce("qual", "the Skyy_Gear_* quality assets were not found - items keep their own quality frame and only the name takes the rarity colour (spec 2.1 fallback)");
    QMISS = miss ? System.currentTimeMillis() : 0L;
    QIDX = q;
    if (!miss) @PKG@.GearQual.check(q);
  }
  if (r < 0 || r >= q.length) return -1;
  return q[r];
}""")
# a stack quality index that resolves to a quality asset (Integer.MIN_VALUE = the item's own quality, always fine)
M(gdf, r"""
public static boolean validQ(int q) {
  if (q == Integer.MIN_VALUE) return true;
  if (q < 0) return false;
  try { return @IQ@.getAssetMap().getAsset(q) instanceof @IQ@; } catch (Throwable t) { return false; }
}""")
# the asset id behind an index for sigs (never the raw index: indices are load-order)
M(gdf, r"""
public static String qName(int q) {
  if (q == Integer.MIN_VALUE) return "own";
  try { Object a = @IQ@.getAssetMap().getAsset(q); if (a instanceof @IQ@) return ((@IQ@) a).getId(); } catch (Throwable t) { }
  return "?";
}""")

# ================================================================= GearData (1/2): id rules + document read + migration (spec 1)
M(gdt, r"""
public static boolean skyyItem(String id) {
  if (id == null) return true;
  String low = id.toLowerCase();
  return low.startsWith("skyy") || low.indexOf("_skyy") >= 0;
}""")
# follow-up review 2: the item's MaxStack as the engine resolved it (Item.processConfig, VERIFIED bytecode: its own / inherited
# MaxStack, else 1 for an item with a Weapon / Armor / Tool section, else 100); -1 = no such item asset (treated as a single item)
M(gdt, r"""
public static int maxStack(String id) {
  try { @ITM@ it = @PKG@.Gear.item(id); return it == null ? -1 : it.getMaxStack(); } catch (Throwable t) { return -1; }
}""")
# exploit review 3: only the token right after the family is an ammo word (Weapon_Arrow_Iron, Weapon_Bomb_Fire); a later token is
# not (Weapon_Shortbow_Bomb is the Archer's shortbow). Follow-up review 2: that narrow rule only for single items (MaxStack <= 1);
# an id that stacks keeps the old any-token test (Weapon_Throwing_Arrow ... stays ammo). Build-checked against Assets.zip: the same
# 14 ammo ids, Weapon_Shortbow_Bomb (MaxStack 1) is gear.
M(gdt, r"""
public static boolean ammoMs(String id, int ms) {
  if (id == null) return false;
  String[] parts = id.split("_");
  if (parts.length < 2) return false;
  int last = ms <= 1 ? 1 : parts.length - 1;
  for (int i = 1; i <= last; i++) {
    String p = parts[i].toLowerCase();
    for (int j = 0; j < @PKG@.GearDefs.AMMO.length; j++) if (p.equals(@PKG@.GearDefs.AMMO[j])) return true;
  }
  return false;
}""")
M(gdt, "public static boolean ammo(String id) { return ammoMs(id, maxStack(id)); }")
M(gdt, r"""
public static boolean family(String id) {
  if (id == null) return false;
  for (int i = 0; i < @PKG@.GearDefs.FAMILIES.length; i++) if (id.startsWith(@PKG@.GearDefs.FAMILIES[i])) return true;
  return false;
}""")
# design review 1: bags (Magic Bags, bag upgrade items, the Accessory Bag) are never gear, not even through gear.include
M(gdt, r"""
public static boolean neverGear(String id) {
  for (int i = 0; i < @PKG@.GearDefs.NEVER.length; i++) if (id.startsWith(@PKG@.GearDefs.NEVER[i])) return true;
  return false;
}""")
M(gdt, r"""
public static boolean included(String id) {
  String[] in = @PKG@.GearCfg.incl();
  for (int i = 0; i < in.length; i++) if (id.startsWith(in[i])) return true;
  return false;
}""")
# spec 1.3: gear = every Weapon_* (not ammo, not an excluded prefix) and every Armor_*; never Skyy_* and never Tool_*.
# design review 1: an id matching a gear.include prefix is gear too (Skyy_ ids and Tool_ families of later stages opt in there;
# include wins over gear.exclude, never over the bag list). Follow-up review 1: include never beats the ammo rule either, and an
# included id that stacks (MaxStack > 1) is gear only in a gear family (Weapon_ / Armor_ / Tool_) and never above the split ceiling
# (a Skyy_ food / menu item must never be stamped, let alone split). ms = the item's MaxStack (maxStack; the harness passes its own).
M(gdt, r"""
public static boolean isGearMs(String id, int ms) {
  if (id == null || id.length() == 0 || neverGear(id)) return false;
  if (included(id)) {
    if (ammoMs(id, ms)) return false;
    if (ms > 1 && (ms > @PKG@.GearDefs.STACK_CEIL || !family(id))) {
      @PKG@.Gear.warnOnce("inclstack:" + id, "gear.include matches " + id + ", which stacks to " + ms + " - only Weapon_ / Armor_ / Tool_ ids stacking to at most " + @PKG@.GearDefs.STACK_CEIL + " can be included; it stays a plain item");
      return false;
    }
    return true;
  }
  if (skyyItem(id)) return false;
  if (id.startsWith("Armor_")) return true;
  if (!id.startsWith("Weapon_")) return false;
  if (ammoMs(id, ms)) return false;
  String[] ex = @PKG@.GearCfg.excl();
  for (int i = 0; i < ex.length; i++) if (id.startsWith(ex[i])) return false;
  return true;
}""")
# the asset lookup only where the answer depends on it (included ids and Weapon_*)
M(gdt, r"""
public static boolean isGear(String id) {
  if (id == null || id.length() == 0 || neverGear(id)) return false;
  if (!included(id)) {
    if (skyyItem(id)) return false;
    if (id.startsWith("Armor_")) return true;
    if (!id.startsWith("Weapon_")) return false;
  }
  return isGearMs(id, maxStack(id));
}""")
M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\"Tool_\") && !skyyItem(id); }")
M(gdt, r"""
public static boolean isSpell(String id) {
  if (id == null) return false;
  for (int i = 0; i < @PKG@.GearDefs.SPELL.length; i++) if (id.startsWith(@PKG@.GearDefs.SPELL[i])) return true;
  return false;
}""")
M(gdt, r"""
public static String toolKind(String id) {
  if (id == null) return "tool";
  for (int i = 0; i < @PKG@.GearDefs.TF_PRE.length; i++) if (id.startsWith(@PKG@.GearDefs.TF_PRE[i])) return @PKG@.GearDefs.TF_KIND[i];
  return "tool";
}""")
# design review 1: the kind.prefix table (longest matching prefix wins), else a tool by family, else combat. Follow-up review 1
# (design finding 11): an included id outside the gear families (Skyy_Talisman_ ...) without a kind.prefix row is Equipment, never a
# combat weapon that the gate could block hits with.
M(gdt, r"""
public static String kindFor(String id) {
  if (id == null) return "combat";
  java.util.HashMap kp = @PKG@.GearCfg.KINDP;
  String best = null;
  int bl = -1;
  java.util.Iterator it = kp.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.length() > bl && id.startsWith(k)) { best = (String) kp.get(k); bl = k.length(); }
  }
  if (best != null) return best;
  if (isTool(id)) return toolKind(id);
  if (!family(id)) return "equipment";
  return "combat";
}""")
# is the engine item an armor piece (an included id without the Armor_ prefix)
M(gdt, r"""
public static boolean armorItem(String id) {
  if (id.startsWith("Armor_")) return true;
  if (id.startsWith("Weapon_")) return false;
  try { @ITM@ it = @PKG@.Gear.item(id); return it != null && it.getArmor() != null; } catch (Throwable t) { return false; }
}""")
# 0 = weapon, 1 = spell weapon, 2 = armor, 3 = tool, 4 = Equipment (design review 1: kind equipment), -1 = not gear
M(gdt, r"""
public static int slotOf(String id) {
  if (isGear(id)) {
    if ("equipment".equals(kindFor(id))) return 4;
    if (armorItem(id)) return 2;
    if (id.startsWith("Tool_")) return 3;
    return isSpell(id) ? 1 : 0;
  }
  if (isTool(id)) return 3;
  return -1;
}""")
M(gdt, r"""
public static @BV@ getv(@BD@ md, String k) {
  try { return md == null ? null : md.get(k); } catch (Throwable t) { return null; }
}""")
M(gdt, r"""
public static int num(@BD@ d, String k, int def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static long lnum(@BD@ d, String k, long def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static String str(@BD@ d, String k, String def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static boolean bool(@BD@ d, String k, boolean def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isBoolean()) return v.asBoolean().getValue(); } catch (Throwable t) { }
  return def;
}""")
# 0 = no document, 1 = SkyyGear v1 document, 2 = only a SkyyRolls document, 3 = SkyyGear data that is not a document (unreadable),
# 4 = a newer SkyyGear schema (read only, never rewritten; spec 1.2)
M(gdt, r"""
public static int state(@BD@ md) {
  if (md == null) return 0;
  @BV@ g = getv(md, @PKG@.GearDefs.DOC_KEY);
  if (g != null && !g.isNull()) {
    if (!g.isDocument()) return 3;
    if (num(g.asDocument(), "v", 1) > 1) return 4;
    return 1;
  }
  @BV@ r = getv(md, @PKG@.GearDefs.ROLLS_KEY);
  if (r != null && r.isDocument()) return 2;
  return 0;
}""")
M(gdt, r"""
public static @BD@ gearDoc(@BD@ md) {
  @BV@ g = getv(md, @PKG@.GearDefs.DOC_KEY);
  return g != null && g.isDocument() ? g.asDocument() : null;
}""")
M(gdt, r"""
public static @BD@ rollsDoc(@BD@ md) {
  @BV@ g = getv(md, @PKG@.GearDefs.ROLLS_KEY);
  return g != null && g.isDocument() ? g.asDocument() : null;
}""")
M(gdt, r"""
public static boolean hasAnyDoc(@BD@ md) {
  if (md == null) return false;
  return md.containsKey(@PKG@.GearDefs.DOC_KEY) || md.containsKey(@PKG@.GearDefs.ROLLS_KEY);
}""")
# gear for every reader: a gear id, or a tool that carries a SkyyGear / SkyyRolls document (migrated SkyyRolls tools, spec 1.6)
M(gdt, r"""
public static boolean gearish(String id, @BD@ md) {
  return isGear(id) || (isTool(id) && hasAnyDoc(md));
}""")
M(gdt, r"""
public static int rarity(@BD@ d) {
  int r = @PKG@.GearDefs.rIndex(str(d, "r", "normal"));
  return r < 0 ? 0 : r;
}""")
M(gdt, "public static boolean identified(@BD@ d) { return bool(d, \"id\", true); }")
M(gdt, "public static String kind(@BD@ d) { return str(d, \"kind\", \"combat\"); }")
# spec 1.2 reading rule 1: a document without gate takes the kind table's gate
M(gdt, r"""
public static String gate(@BD@ d) {
  String g = str(d, "gate", null);
  if (g != null) return g;
  return @PKG@.GearDefs.kindGate(kind(d));
}""")
M(gdt, r"""
public static @BA@ mods(@BD@ d) {
  try { @BV@ v = d == null ? null : d.get("mods"); if (v != null && v.isArray()) return v.asArray(); } catch (Throwable t) { }
  return new @BA@();
}""")
M(gdt, r"""
public static @BD@ mod(String s, int v) {
  @BD@ m = new @BD@();
  m.append("s", new org.bson.BsonString(s));
  m.append("v", new org.bson.BsonInt32(v));
  return m;
}""")
M(gdt, r"""
public static @BD@ base(String kind, int r, boolean ident, String src) {
  @BD@ d = new @BD@();
  d.append("v", new org.bson.BsonInt32(1));
  d.append("kind", new org.bson.BsonString(kind));
  d.append("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[@PKG@.GearCfg.ri(r)]));
  d.append("id", new org.bson.BsonBoolean(ident));
  d.append("mods", new @BA@());
  d.append("src", new org.bson.BsonString(src));
  d.append("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  d.append("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kind)));
  return d;
}""")
# spec 1.5: the legacy stamp (gear a player already owns stays Normal with no modifiers, LOCKED)
M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), 0, true, \"legacy\"); }")
M(gdt, r"""
public static String qualityIdOf(String id) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return "";
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) { String s = ((@IQ@) q).getId(); if (s != null) return s; }
  } catch (Throwable t) { }
  return "";
}""")
# spec 1.6: rarity of an old SkyyRolls document. stats (default): score = average of dmg/30, str/25, crit/15 in % (SkyyRolls' maxima;
# a missing key = 0); roll: the old Roll Quality; item: the item's engine quality. Capped at migrate.maxRarity, never mythic / set.
# exploit review 4: armor never applies Damage % (a weapon-only stat), so an armor piece's score is the average of str/25 and
# crit/15 only (its dmg roll is dropped from the migrated document too; the whole old document stays in "old").
M(gdt, r"""
public static int migrateRarity(String id, @BD@ rolls) {
  String by = @PKG@.GearCfg.MIGRATE_BY;
  int r = 0;
  if ("item".equals(by)) {
    String q = qualityIdOf(id);
    for (int i = 0; i < @PKG@.GearDefs.RQ_FROM.length; i++) if (@PKG@.GearDefs.RQ_FROM[i].equalsIgnoreCase(q)) r = @PKG@.GearDefs.rIndex(@PKG@.GearDefs.RQ_TO[i]);
  } else {
    double score;
    if ("roll".equals(by)) score = (double) num(rolls, "quality", 0);
    else {
      double a = (double) num(rolls, "dmg", 0) / 30.0;
      double b = (double) num(rolls, "str", 0) / 25.0;
      double c = (double) num(rolls, "crit", 0) / 15.0;
      if (slotOf(id) == 2) score = (b + c) / 2.0 * 100.0;
      else score = (a + b + c) / 3.0 * 100.0;
    }
    int[] mg = @PKG@.GearCfg.MIG;
    if (score >= (double) mg[3]) r = 4;
    else if (score >= (double) mg[2]) r = 3;
    else if (score >= (double) mg[1]) r = 2;
    else if (score >= (double) mg[0]) r = 1;
    else r = 0;
  }
  if (r < 0) r = 0;
  int cap = @PKG@.GearCfg.migrateMax();
  if (r > cap) r = cap;
  if (r > 4) r = 4;
  return r;
}""")
# (migrate + effective sit after GearRoll: migrate.clampToLevel needs GearRoll.bounds)

# ================================================================= GearLevel (spec 3.1, 2.2 level factor)
M(glv, r"""
public static int clamp(int v) {
  if (v < 0) return 0;
  if (v > 100) return 100;
  return v;
}""")
M(glv, r"""
public static int level(String id, @BD@ d) {
  if (id == null) return 0;
  try {
    @BV@ v = d == null ? null : d.get("lvl");
    if (v != null && v.isNumber()) return clamp(v.asNumber().intValue());
  } catch (Throwable t) { }
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);
  if (o instanceof Integer) return clamp(((Integer) o).intValue());
  java.util.HashMap mat = @PKG@.GearCfg.MAT;
  int mw = @PKG@.GearCfg.MAT_WORDS;
  String[] tk = id.split("_");
  for (int i = 0; i < tk.length; i++) {
    for (int n = mw; n >= 1; n--) {
      if (i + n > tk.length) continue;
      String key = tk[i].toLowerCase();
      for (int j = 1; j < n; j++) key = key + "_" + tk[i + j].toLowerCase();
      Object m = mat.get(key);
      if (m instanceof Integer) return clamp(((Integer) m).intValue());
    }
  }
  if (@PKG@.GearCfg.LEVEL_VANILLA) {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it != null) {
      int l = 0;
      try { l = it.getItemLevel(); } catch (Throwable t2) { l = 0; }
      if (l > 0) return clamp(l);
    }
  }
  return clamp(@PKG@.GearCfg.LEVEL_DEFAULT);
}""")
# f = floor + (100 - floor) x min(level, full) / full, in % (spec 2.2); floor 100 switches the scaling off
M(glv, r"""
public static double factor(int level) {
  int floor = @PKG@.GearCfg.LEVEL_FLOOR;
  int full = @PKG@.GearCfg.LEVEL_FULL;
  if (full < 1) full = 1;
  if (floor >= 100) return 100.0;
  int l = level < 0 ? 0 : level;
  if (l > full) l = full;
  return (double) floor + (100.0 - (double) floor) * (double) l / (double) full;
}""")
# ---- 0.2 LEVEL BANDS (spec 2). entry = the level.material row (lower case) level() matches for an item id - the same loop: at each id
# word from the left the longest entry first, up to MAT_WORDS words; null = none
M(glv, r"""
public static String entry(String id) {
  if (id == null) return null;
  java.util.HashMap mat = @PKG@.GearCfg.MAT;
  int mw = @PKG@.GearCfg.MAT_WORDS;
  String[] tk = id.split("_");
  for (int i = 0; i < tk.length; i++) {
    for (int n = mw; n >= 1; n--) {
      if (i + n > tk.length) continue;
      String key = tk[i].toLowerCase();
      for (int j = 1; j < n; j++) key = key + "_" + tk[i + j].toLowerCase();
      if (mat.get(key) instanceof Integer) return key;
    }
  }
  return null;
}""")
# { min, cap, kind } of an item id: kind 0 = Level by item (exact, no range - spec 2), 1 = Level by material (the band), 2 = Hytale's own
# item level (exact), 3 = Level when nothing matches (exact). min == level(id, no stamp) always (the same order as level()).
M(glv, r"""
public static int[] band(String id) {
  if (id == null) return new int[] { 0, 0, 3 };
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);
  if (o instanceof Integer) { int v = clamp(((Integer) o).intValue()); return new int[] { v, v, 0 }; }
  String e = entry(id);
  if (e != null) {
    Object m = @PKG@.GearCfg.MAT.get(e);
    if (m instanceof Integer) {
      int mn = clamp(((Integer) m).intValue());
      Object c = @PKG@.GearCfg.MATCAP.get(e);
      int cp = c instanceof Integer ? clamp(((Integer) c).intValue()) : @PKG@.GearCfg.capOf(mn, @PKG@.GearCfg.BAND_W);
      if (cp < mn) cp = mn;
      return new int[] { mn, cp, 1 };
    }
  }
  if (@PKG@.GearCfg.LEVEL_VANILLA) {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it != null) {
      int l = 0;
      try { l = it.getItemLevel(); } catch (Throwable t2) { l = 0; }
      if (l > 0) { int v2 = clamp(l); return new int[] { v2, v2, 2 }; }
    }
  }
  int d = clamp(@PKG@.GearCfg.LEVEL_DEFAULT);
  return new int[] { d, d, 3 };
}""")
# the words a craft line uses for a band: "Copper gear", "Copper armor" (an Armor_ entry), "Leather Soft gear" (the row as the file spells it)
M(glv, r"""
public static String bandWord(String id) {
  String e = entry(id);
  if (e == null) return @PKG@.Gear.itemName(id);
  Object nm = @PKG@.GearCfg.MATNAME.get(e);
  String s = nm instanceof String ? (String) nm : e;
  if (s.length() > 6 && s.toLowerCase().startsWith("armor_")) return s.substring(6).replace('_', ' ') + " armor";
  return s.replace('_', ' ') + " gear";
}""")
# spec 1 "Gate floor": a skill below level.gateFloor counts as that floor for gear (0 = off)
M(glv, r"""
public static int floor(int have) {
  int f = @PKG@.GearCfg.GATE_FLOOR;
  if (f < 0) f = 0;
  return have < f ? f : have;
}""")
# true = the document stores its own level (0.2 stamp, admin /gear level)
M(glv, r"""
public static boolean stamped(@BD@ d) {
  try { @BV@ v = d == null ? null : d.get("lvl"); return v != null && v.isNumber(); } catch (Throwable t) { return false; }
}""")

# ================================================================= GearGate (spec 3.3): gate skill + level cache (+ popup for PART B)
# cache per player: Object[] { String profileEpoch, String classSkill ("" = none), ConcurrentHashMap skill -> Integer level }.
# Every lookup compares profile:epoch + class:skill (two plain map reads) with the cached pair and starts over on a change (E2).
# Levels: >= 0 = the level; -1 = SkyySkills does not know that skill name; -2 = no SkyySkills (skill:fn:level missing).
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")
M(ggt, r"""
public static String classSkillRaw(java.util.UUID u) {
  Object o = u == null ? null : @PKG@.Gear.bget("class:skill:" + u);
  return o instanceof String && ((String) o).length() > 0 ? (String) o : null;
}""")
M(ggt, "public static boolean classesOn() { return @PKG@.Gear.fn(\"class:fn:allowed\") != null; }")
M(ggt, "public static boolean skillsOn() { return @PKG@.Gear.fn(\"skill:fn:level\") != null; }")
M(ggt, r"""
public static int readLevel(java.util.UUID u, String skill) {
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:level");
  if (f == null) return -2;
  try {
    Object r = f.apply(new Object[] { u, skill });
    if (r instanceof Number) { int n = ((Number) r).intValue(); return n < 0 ? 0 : n; }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("skillfn", "skill:fn:level failed: " + t); }
  return -1;
}""")
M(ggt, r"""
public static Object[] entry(java.util.UUID u) {
  String ep = @PKG@.Gear.epoch(u);
  String cs = classSkillRaw(u);
  if (cs == null) cs = "";
  Object[] e = (Object[]) CACHE.get(u);
  if (e == null || !ep.equals(e[0]) || !cs.equals(e[1])) {
    e = new Object[] { ep, cs, new java.util.concurrent.ConcurrentHashMap() };
    CACHE.put(u, e);
  }
  return e;
}""")
M(ggt, r"""
public static int have(java.util.UUID u, String skill) {
  if (u == null || skill == null || skill.length() == 0) return -2;
  Object[] e = entry(u);
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) e[2];
  Object o = m.get(skill);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int n = readLevel(u, skill);
  m.put(skill, Integer.valueOf(n));
  if (n == -1) @PKG@.Gear.warnOnce("skill:" + skill, "SkyySkills does not know the gate skill '" + skill + "' - it counts as level 0");
  return n;
}""")
# the SkyySkills skill a gate asks: "class" -> class:skill:<uuid>; SkyyClasses present but no class -> null (level 0, "pick a class");
# no SkyyClasses -> the pseudo-skill "Combat" (SkyySkills resolves it to the active class row)
M(ggt, r"""
public static String gateSkill(java.util.UUID u, String gate) {
  if (gate == null || gate.length() == 0) return null;
  if (!gate.equals("class")) return gate;
  String cs = classSkillRaw(u);
  if (cs != null) return cs;
  if (classesOn()) return null;
  return "Combat";
}""")
# display name of a gate for tooltips (SkyyGear's own class -> skill copy only when SkyyClasses is absent)
M(ggt, r"""
public static String gateLabel(java.util.UUID u, String gate) {
  if (gate == null || gate.length() == 0) return "";
  if (!gate.equals("class")) return gate;
  String cs = classSkillRaw(u);
  if (cs != null) return cs;
  Object pc = u == null ? null : @PKG@.Gear.bget("profile:class:" + u);
  String m = pc instanceof String ? @PKG@.GearDefs.classSkill((String) pc) : null;
  if (m != null) return m;
  return classesOn() ? "Class skill" : "Combat";
}""")
# GearTick (1 Hz) + the ready refresh: re-read every cached level; true = something the player can see may have changed
M(ggt, r"""
public static boolean refresh(java.util.UUID u) {
  if (u == null) return false;
  Object[] old = (Object[]) CACHE.get(u);
  Object[] e = entry(u);
  boolean changed = old != e;
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) e[2];
  String cs = gateSkill(u, "class");
  if (cs != null && !m.containsKey(cs)) { have(u, cs); changed = true; }
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int n = readLevel(u, k);
    Object o = m.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != n) { m.put(k, Integer.valueOf(n)); changed = true; }
  }
  return changed;
}""")
M(ggt, "public static void forget(java.util.UUID u) { if (u != null) { CACHE.remove(u); POPPED.remove(u); } }")
# Object[] { Boolean ok, String skill (label), Integer need, Integer have, Boolean enforced, Integer state }
# state: 0 evaluated, 1 SkyyClasses present but no class (level 0), 2 no SkyySkills, 3 no gate (kind without a skill),
#        4 no owner (neutral text), 5 part.gate off
# 0.2 (spec 1 "Gate floor"): a skill below level.gateFloor (1) counts as that floor in EVERY gate state - no class picked (state 1), no
# SkyySkills with level.noSkills block (state 2), an unknown skill (0) - so the Lv 1 kit items work for a new player. "have" stays the
# real level (the "(you: N)" texts).
M(ggt, r"""
public static Object[] check(java.util.UUID u, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  boolean enforced = @PKG@.GearDefs.enforcedKind(kind);
  String label = gateLabel(u, gate);
  int fl = @PKG@.GearLevel.floor(0);
  if (gate.length() == 0) return new Object[] { Boolean.TRUE, "", Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(3) };
  if (u == null) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.valueOf(enforced), Integer.valueOf(4) };
  if (!@PKG@.GearCfg.PART_GATE) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(5) };
  if (!skillsOn()) {
    boolean pass = !"block".equals(@PKG@.GearCfg.NO_SKILLS) || need <= fl;
    return new Object[] { Boolean.valueOf(pass), label, Integer.valueOf(need), Integer.valueOf(-2), Boolean.valueOf(enforced), Integer.valueOf(2) };
  }
  String sk = gateSkill(u, gate);
  if (sk == null) return new Object[] { Boolean.valueOf(need <= fl), label, Integer.valueOf(need), Integer.valueOf(0), Boolean.valueOf(enforced), Integer.valueOf(1) };
  int h = have(u, sk);
  if (h == -2) {
    boolean pass2 = !"block".equals(@PKG@.GearCfg.NO_SKILLS) || need <= fl;
    return new Object[] { Boolean.valueOf(pass2), label, Integer.valueOf(need), Integer.valueOf(-2), Boolean.valueOf(enforced), Integer.valueOf(2) };
  }
  if (h < 0) h = 0;
  return new Object[] { Boolean.valueOf(@PKG@.GearLevel.floor(h) >= need), label, Integer.valueOf(need), Integer.valueOf(h), Boolean.valueOf(enforced), Integer.valueOf(0) };
}""")
# PART B: the level / unidentified popup (spec 3.4, the SkyyClasses ClassRules.popup shape); throttled 1500 ms, gated by the
# player switch gear.blockedPopup (only the popup, never the block); the icon is a metadata-free new ItemStack(id, 1)
M(ggt, r"""
public static void popup(@PR@ pr, java.util.UUID u, String id, String title, String body) {
  try {
    if (!@PKG@.Gear.notifyOn(u, "gear.blockedPopup")) return;
    long now = System.currentTimeMillis();
    Long last = (Long) POPPED.get(u);
    if (last != null && now - last.longValue() < 1500L) return;
    POPPED.put(u, Long.valueOf(now));
    @MSG@ t = @MSG@.raw(title).color(@PKG@.GearDefs.C_BAD);
    @MSG@ b = @MSG@.raw(body);
    @IWM@ icon = null;
    try { if (id != null && id.length() > 0) icon = (@IWM@) new @IS@(id, 1).toPacket(); } catch (Throwable t0) { icon = null; }
    if (icon != null) @NTU@.sendNotification(pr.getPacketHandler(), t, b, icon, @NST@.Warning);
    else @NTU@.sendNotification(pr.getPacketHandler(), t, b, @NST@.Warning);
  } catch (Throwable x) { @PKG@.Gear.warnOnce("popup", "popup failed: " + x); }
}""")

# ####################################################################################################################################
# 0.1.2 CHARGED ATTACK DAMAGE (1/2): the per-item index + roll eligibility + the per-hit rules (placed here because GearRoll.pool
# calls GearChg.canRoll). Compile order = call order: GearChgVars, GearChgState, GearChgWalk, GearChg, GearHand. Engine facts
# (HytaleServer.jar bytecode, 2026-09-30): InteractionManager.walkChain(collector, type, ctx, root) = collector.start(),
# into(ctx, null), walkInteractions(ROOT, root ids), outof(), finished(); walkInteraction(child) = collect(tag, ctx, child) (true
# stops the whole walk), into(ctx, child), child.walk(collector, ctx), outof(). ChargingInteraction.walk visits every Next entry
# with ChargingTag.of(key) and Failed with StringTag "Failed"; SimpleInteraction.walk next ("Next") / failed ("Failed");
# DamageEntityInteraction.walk next / failed / blocked + every AngledDamage / TargetedDamage next; ReplaceInteraction.walk takes
# the root id from ctx.getInteractionVars() (the vars getter) or its defaultValue. WeaponDamageDataCollector (the tooltip walk)
# records getDamageCalculator() per DamageEntityInteraction and walks a ProjectileInteraction's ProjectileHit root with a second
# collector - so does GearChgWalk. LaunchProjectileInteraction.firstRun -> ProjectileComponent.assembleDefaultProjectile(time,
# projectileId, ...) -> new ProjectileComponent(projectileId) stores it as projectileAssetName (VERIFIED: the research's
# UNVERIFIED #4 is settled; getProjectileAssetName() == the LaunchProjectile ProjectileId). DamageCalculator equals / hashCode are
# by VALUE, so every table keyed by a calculator is an IdentityHashMap.
# ####################################################################################################################################
gchv.addInterface(pool.get("java.util.function.Function"))
F(gchv, "public java.util.Map vars;")
C(gchv, "public GearChgVars(java.util.Map vars) { this.vars = vars; }")
M(gchv, "public Object apply(Object o) { return this.vars; }")
# one item walk: recs = Object[] { calculator | projectile id, Float label seconds (<= 0 = normal), Float charging serial the label
# came from (-1 = none), Boolean reached from an Ability1-3 root, Integer 0 = damage step / 1 = legacy launch }; max = Integer
# charging serial -> Float largest Next key seen under that Charging step (every collect() edge, so keys that lead to no damage count)
for _f in ("public int serial;", "public java.util.HashMap max;", "public java.util.ArrayList recs;", "public boolean abort;",
           "public int steps;", "public String err;"):
    F(gchs, _f)
C(gchs, r"""
public GearChgState() {
  this.serial = 0;
  this.max = new java.util.HashMap();
  this.recs = new java.util.ArrayList();
  this.abort = false;
  this.steps = 0;
  this.err = null;
}""")
# the Collector: a frame per interaction = float[] { label seconds, charging serial of that label, own charging serial (0 = not a
# Charging step) }. Edge rules (WeaponDamageDataCollector.into, VERIFIED): ChargingTag > 0 -> charged at that many seconds (FULL or
# PARTIAL is decided after the walk against that Charging step's largest key), ChargingTag 0 -> normal, StringTag Failed / Blocked ->
# normal, anything else keeps the parent's label. A walk deeper than 128 frames or longer than 20000 steps stops (collect answers
# true) and the item counts as "walk incomplete" (a looping third-party chain can never hang the server).
gchw.addInterface(pool.get(CHT["COLL"]))
for _f in ("public @PKG@.GearChgState st;", "public java.util.ArrayList stack;", "public Object pending;", "public float seedLab;",
           "public float seedRef;", "public boolean sig;"):
    F(gchw, _f)
C(gchw, r"""
public GearChgWalk(@PKG@.GearChgState st, float lab, float ref, boolean sig) {
  this.st = st;
  this.stack = new java.util.ArrayList();
  this.pending = null;
  this.seedLab = lab;
  this.seedRef = ref;
  this.sig = sig;
}""")
M(gchw, "public void start() { this.stack.clear(); this.pending = null; }")
M(gchw, "public void finished() { }")
M(gchw, r"""
public void outof() {
  int n = this.stack.size();
  if (n > 0) this.stack.remove(n - 1);
}""")
M(gchw, r"""
public boolean collect(@CTAG@ tag, @ICTX@ ctx, @INTR@ in) {
  this.pending = tag;
  int n = this.stack.size();
  if (tag instanceof @CHTAG@ && n > 0) {
    float[] top = (float[]) this.stack.get(n - 1);
    if (top[2] > 0.0f) {
      Integer key = Integer.valueOf((int) top[2]);
      float s = (float) ((@CHTAG@) tag).getSeconds();
      Object m = this.st.max.get(key);
      if (!(m instanceof Float) || s > ((Float) m).floatValue()) this.st.max.put(key, Float.valueOf(s));
    }
  }
  this.st.steps = this.st.steps + 1;
  if (this.st.steps > 20000) this.st.abort = true;
  return this.st.abort;
}""")
M(gchw, r"""
public void add(Object c, float lab, float ref) {
  if (c == null) return;
  this.st.recs.add(new Object[] { c, Float.valueOf(lab), Float.valueOf(ref), Boolean.valueOf(this.sig), Integer.valueOf(0) });
}""")
M(gchw, r"""
public void into(@ICTX@ ctx, @INTR@ in) {
  float lab = this.seedLab;
  float ref = this.seedRef;
  int n = this.stack.size();
  if (n > 0) {
    float[] p = (float[]) this.stack.get(n - 1);
    lab = p[0];
    ref = p[1];
    Object t = this.pending;
    if (t instanceof @CHTAG@) {
      double s = ((@CHTAG@) t).getSeconds();
      if (s > 0.0) { lab = (float) s; ref = p[2]; }
      else { lab = -1.0f; ref = -1.0f; }
    } else if (t instanceof @STAG@) {
      String g = ((@STAG@) t).getTag();
      if ("Failed".equals(g) || "Blocked".equals(g)) { lab = -1.0f; ref = -1.0f; }
    }
  }
  this.pending = null;
  float own = 0.0f;
  if (in instanceof @CHGI@) { this.st.serial = this.st.serial + 1; own = (float) this.st.serial; }
  this.stack.add(new float[] { lab, ref, own });
  if (this.stack.size() > 128) this.st.abort = true;
  if (in == null || this.st.abort) return;
  try {
    if (in instanceof @DEI@) {
      @DEI@ de = (@DEI@) in;
      add(de.getDamageCalculator(), lab, ref);
      @ANGD@[] an = de.getAngledDamage();
      if (an != null) for (int i = 0; i < an.length; i++) if (an[i] != null) add(an[i].getDamageCalculator(), lab, ref);
      java.util.Map td = de.getTargetedDamage();
      if (td != null) {
        java.util.Iterator it = td.values().iterator();
        while (it.hasNext()) {
          Object v = it.next();
          if (v instanceof @TGTD@) add(((@TGTD@) v).getDamageCalculator(), lab, ref);
        }
      }
    } else if (in instanceof @LPI@) {
      String pid = ((@LPI@) in).getProjectileId();
      if (pid != null) this.st.recs.add(new Object[] { pid, Float.valueOf(lab), Float.valueOf(ref), Boolean.valueOf(this.sig), Integer.valueOf(1) });
    } else if (in instanceof @PJI@) {
      @PJC@ cfg = ((@PJI@) in).getConfig();
      java.util.Map im = cfg == null ? null : cfg.getInteractions();
      Object rid = im == null ? null : im.get(@ITYPE@.ProjectileHit);
      Object root = rid == null ? null : @RTI@.getAssetMap().getAsset(rid);
      if (root instanceof @RTI@) {
        @PKG@.GearChgWalk sub = new @PKG@.GearChgWalk(this.st, lab, ref, this.sig);
        @IMGR@.walkChain(sub, @ITYPE@.ProjectileHit, ctx, (@RTI@) root);
      }
    }
  } catch (Throwable x) { if (this.st.err == null) this.st.err = String.valueOf(x); }
}""")

# GearChg: the per-item index (ITEMS: item id -> Object[] entry, built once per id on first use, lock-free reads) and every rule.
# entry = { IdentityHashMap calculator -> int[] { flags, class (0 unknown, 1 light, 2 charged, 3 signature), longest charge ms },
#           HashMap projectile id -> int[] { flags, longest charge ms }, Boolean has (a detectable charged attack), Boolean partial
#           (partial charge levels: never trust the Class tag alone), String summary (/gear charged), Boolean ok (every root walked
#           completely), Long built at, Boolean found (at least one root walked) }. flags: FULL 1, PARTIAL 2, NORMAL 4, SIG 8 (an
# Ability1-3 root). A calculator / launch counts only when its flags are exactly FULL (reached both charged and uncharged = ambiguous
# = never). A calculator the hit carries that the item's index does not know triggers one re-walk (at most every 30 s per item:
# assets reloaded, LoadedAssetsEvent needs no listener).
F(gchi, "public static final String[] EXCL = %s;" % jarr(CHG_EXCL))
F(gchi, "public static final String[] TRUST = %s;" % jarr(CHG_TRUST))
F(gchi, "public static final String[] FALLBACK = %s;" % jarr(CHG_FALLBACK))
F(gchi, "public static final String[] PARTIAL = %s;" % jarr(CHG_PARTIAL))
F(gchi, "public static final double GLOW_S = %s;" % repr(float(BOW_GLOW_S)))
F(gchi, "public static final java.util.concurrent.ConcurrentHashMap ITEMS = new java.util.concurrent.ConcurrentHashMap();")
F(gchi, "public static volatile java.util.HashSet TSET = null;")
F(gchi, "public static volatile java.util.HashSet FSET = null;")
F(gchi, "public static volatile java.util.HashSet PSET = null;")
F(gchi, "public static final int FULL = 1;")
F(gchi, "public static final int PART = 2;")
F(gchi, "public static final int NORM = 4;")
F(gchi, "public static final int SIG = 8;")
F(gchi, "public static final long REWALK_MS = 30000L;")
M(gchi, r"""
public static java.util.HashSet set(String[] a) {
  java.util.HashSet h = new java.util.HashSet();
  for (int i = 0; i < a.length; i++) h.add(a[i]);
  return h;
}""")
M(gchi, r"""
public static boolean trusted(String id) {
  if (id == null) return false;
  java.util.HashSet h = TSET;
  if (h == null) { h = set(TRUST); TSET = h; }
  return h.contains(id);
}""")
M(gchi, r"""
public static boolean fallback(String id) {
  if (id == null) return false;
  java.util.HashSet h = FSET;
  if (h == null) { h = set(FALLBACK); FSET = h; }
  return h.contains(id);
}""")
M(gchi, r"""
public static boolean partialList(String id) {
  if (id == null) return false;
  java.util.HashSet h = PSET;
  if (h == null) { h = set(PARTIAL); PSET = h; }
  return h.contains(id);
}""")
M(gchi, r"""
public static boolean excluded(String id) {
  if (id == null) return false;
  for (int i = 0; i < EXCL.length; i++) if (id.startsWith(EXCL[i])) return true;
  return false;
}""")
M(gchi, r"""
public static int clsCode(Object calc) {
  try {
    if (!(calc instanceof @DCALC@)) return 0;
    Object c = ((@DCALC@) calc).getDamageClass();
    if (c == @DCLASS@.CHARGED) return 2;
    if (c == @DCLASS@.SIGNATURE) return 3;
    if (c == @DCLASS@.LIGHT) return 1;
  } catch (Throwable t) { }
  return 0;
}""")
M(gchi, r"""
public static int kindOf(float lab, float ref, java.util.HashMap max) {
  if (!(lab > 0.0f)) return NORM;
  Object m = max.get(Integer.valueOf((int) ref));
  float mx = m instanceof Float ? ((Float) m).floatValue() : lab;
  return lab + 0.0001f >= mx ? FULL : PART;
}""")
M(gchi, r"""
public static String secs(int ms) {
  int m = ms < 0 ? 0 : ms;
  String f = String.valueOf(m % 1000 + 1000).substring(1);
  while (f.length() > 0 && f.charAt(f.length() - 1) == '0') f = f.substring(0, f.length() - 1);
  return (m / 1000) + (f.length() > 0 ? "." + f : "") + " s";
}""")
M(gchi, r"""
public static Object[] build(String id) {
  java.util.IdentityHashMap calcs = new java.util.IdentityHashMap();
  java.util.HashMap launches = new java.util.HashMap();
  boolean ok = true;
  boolean found = false;
  @PKG@.GearChgState st = new @PKG@.GearChgState();
  java.util.Map inter = null;
  java.util.Map vars = null;
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it != null) { inter = it.getInteractions(); vars = it.getInteractionVars(); }
  } catch (Throwable t0) { inter = null; if (st.err == null) st.err = String.valueOf(t0); }
  if (inter != null) {
    java.util.Iterator ki = inter.keySet().iterator();
    while (ki.hasNext()) {
      Object ty = ki.next();
      Object rid = inter.get(ty);
      if (!(ty instanceof @ITYPE@) || rid == null) continue;
      boolean sig = ty == @ITYPE@.Ability1 || ty == @ITYPE@.Ability2 || ty == @ITYPE@.Ability3;
      try {
        Object root = @RTI@.getAssetMap().getAsset(rid);
        if (!(root instanceof @RTI@)) continue;
        @ICTX@ ctx = @ICTX@.withoutEntity();
        ctx.setInteractionVarsGetter(new @PKG@.GearChgVars(vars == null ? new java.util.HashMap() : vars));
        @IMGR@.walkChain(new @PKG@.GearChgWalk(st, -1.0f, -1.0f, sig), (@ITYPE@) ty, ctx, (@RTI@) root);
        found = true;
      } catch (Throwable t) { ok = false; if (st.err == null) st.err = String.valueOf(t); }
    }
  }
  if (st.abort || st.err != null) ok = false;
  for (int i = 0; i < st.recs.size(); i++) {
    Object[] r = (Object[]) st.recs.get(i);
    float lab = ((Float) r[1]).floatValue();
    int k = kindOf(lab, ((Float) r[2]).floatValue(), st.max);
    if (((Boolean) r[3]).booleanValue()) k = k | SIG;
    int ms = lab > 0.0f ? Math.round(lab * 1000.0f) : 0;
    if (((Integer) r[4]).intValue() == 0) {
      int[] e = (int[]) calcs.get(r[0]);
      if (e == null) { e = new int[] { 0, clsCode(r[0]), 0 }; calcs.put(r[0], e); }
      e[0] = e[0] | k;
      if (ms > e[2]) e[2] = ms;
    } else {
      int[] e2 = (int[]) launches.get(r[0]);
      if (e2 == null) { e2 = new int[] { 0, 0 }; launches.put(r[0], e2); }
      e2[0] = e2[0] | k;
      if (ms > e2[1]) e2[1] = ms;
    }
  }
  boolean tr = trusted(id);
  int full = 0;
  int fullMs = 0;
  int launchMs = 0;
  int combo = 0;
  int part = 0;
  int sigs = 0;
  int amb = 0;
  int lfull = 0;
  boolean partial = false;
  java.util.Iterator ci = calcs.values().iterator();
  while (ci.hasNext()) {
    int[] e = (int[]) ci.next();
    int f = e[0];
    if ((f & PART) != 0) partial = true;
    if ((f & SIG) != 0 || e[1] == 3) { sigs++; continue; }
    if (f == FULL) { full++; if (e[2] > fullMs) fullMs = e[2]; }
    else if ((f & FULL) != 0) amb++;
    else if ((f & PART) != 0) part++;
    else if (e[1] == 2 && tr) combo++;
  }
  StringBuilder lp = new StringBuilder();
  java.util.Iterator li = launches.keySet().iterator();
  while (li.hasNext()) {
    Object pk = li.next();
    int[] e3 = (int[]) launches.get(pk);
    if ((e3[0] & PART) != 0) partial = true;
    if (e3[0] == FULL) {
      lfull++;
      if (lp.length() > 0) lp.append(", ");
      lp.append(String.valueOf(pk));
      if (e3[1] > launchMs) launchMs = e3[1];
    } else if ((e3[0] & PART) != 0) part++;
  }
  boolean has = full + combo + lfull > 0;
  StringBuilder sb = new StringBuilder();
  sb.append(has ? "charged attack: YES" : "charged attack: none detectable");
  sb.append(" - counts: ").append(full).append(" full-charge damage step").append(full == 1 ? "" : "s");
  if (fullMs > 0) sb.append(" (up to ").append(secs(fullMs)).append(")");
  sb.append(", ").append(combo).append(" Hytale Charged-tagged combo hit").append(combo == 1 ? "" : "s");
  sb.append(", ").append(lfull).append(" charged launch").append(lfull == 1 ? "" : "es");
  if (lp.length() > 0) sb.append(" (").append(lp.toString()).append(", ").append(secs(launchMs)).append(")");
  sb.append("; never: ").append(part).append(" partial charge level").append(part == 1 ? "" : "s").append(", ").append(sigs).append(" signature, ").append(amb).append(" ambiguous");
  if (!found) sb.append(" [the walk found no item chain" + (st.err == null ? "" : ": " + st.err) + "]");
  else if (!ok) sb.append(" [walk incomplete" + (st.err == null ? "" : ": " + st.err) + "]");
  return new Object[] { calcs, launches, Boolean.valueOf(has), Boolean.valueOf(partial), sb.toString(), Boolean.valueOf(ok),
    Long.valueOf(System.currentTimeMillis()), Boolean.valueOf(found) };
}""")
M(gchi, r"""
public static synchronized Object[] buildLocked(String id, boolean again) {
  Object[] e = (Object[]) ITEMS.get(id);
  if (e != null && (!again || System.currentTimeMillis() - ((Long) e[6]).longValue() < REWALK_MS)) return e;
  e = build(id);
  if (ITEMS.size() > 4096) ITEMS.clear();
  ITEMS.put(id, e);
  return e;
}""")
M(gchi, r"""
public static Object[] ensure(String id) {
  Object[] e = (Object[]) ITEMS.get(id);
  if (e != null) return e;
  return buildLocked(id, false);
}""")
M(gchi, "public static Object[] rewalk(String id) { return buildLocked(id, true); }")
M(gchi, "public static void clear() { ITEMS.clear(); }")
M(gchi, "public static boolean found(Object[] e) { return e != null && ((Boolean) e[7]).booleanValue(); }")
M(gchi, "public static boolean walked(Object[] e) { return found(e) && ((Boolean) e[5]).booleanValue(); }")
# roll eligibility of a weapon id: never an excluded family; the runtime walk when it ran completely, else the baked vanilla list
M(gchi, r"""
public static boolean hasCharged(String id) {
  if (id == null || excluded(id)) return false;
  Object[] e = ensure(id);
  if (walked(e)) return ((Boolean) e[2]).booleanValue();
  return fallback(id);
}""")
# GearRoll.pool: Charged Attack Damage may roll only while charged.on is on (Skyy's lock: off = it does nothing), always on armor
# (slot 2), on a weapon (slot 0 / 1) only with a detectable charged attack; never on Equipment (slot letters wa)
M(gchi, r"""
public static boolean canRoll(String id, int slot) {
  if (!@PKG@.GearCfg.CHG_ON) return false;
  if (slot == 2) return true;
  if (slot == 0 || slot == 1) return hasCharged(id);
  return false;
}""")
# the legacy projectile pid launched by item id: 1 = only from a FULL step (a charged launch), 0 = also / only uncharged, -1 = this
# item never launches it (or its walk found nothing)
M(gchi, r"""
public static int launchCode(String id, String pid) {
  if (id == null || pid == null) return -1;
  Object[] e = ensure(id);
  if (!found(e)) return -1;
  int[] f = (int[]) ((java.util.HashMap) e[1]).get(pid);
  if (f == null) return -1;
  return f[0] == FULL ? 1 : 0;
}""")
# one damage step's index flags (entry e of an item id), null = the item's walk does not know this calculator object
M(gchi, r"""
public static int[] step(Object[] e, Object calc) {
  if (e == null || calc == null) return null;
  return (int[]) ((java.util.IdentityHashMap) e[0]).get(calc);
}""")
# the rule for a KNOWN step f of item id (cls = the calculator's Class code): 1 = charged; w[0] = the reason
M(gchi, r"""
public static int stepRule(int[] f, int cls, String id, String[] w) {
  int g = f[0];
  if ((g & SIG) != 0) { w[0] = "reached from a signature ability"; return 0; }
  if (g == FULL) { w[0] = "full charge " + secs(f[2]) + (cls == 2 ? " (Hytale Charged tag)" : " (untagged step, from the walk)"); return 1; }
  if ((g & FULL) != 0) { w[0] = "ambiguous: this damage step is reached charged and uncharged"; return 0; }
  if ((g & PART) != 0) { w[0] = "partial charge (" + secs(f[2]) + ") - only the full charge counts"; return 0; }
  if (cls == 2 && trusted(id)) { w[0] = "Hytale Charged tag on a hit without a hold (crossbow 3rd bolt in a row)"; return 1; }
  if (cls == 2) { w[0] = "Charged tag on an untrusted item (not vanilla or pack) - ignored"; return 0; }
  w[0] = "normal attack";
  return 0;
}""")
# review of 0.1.2 finding 3: a Class-tagged (Light / Charged) step that a completely walked vanilla / pack weapon's index still does
# not know after the re-walk -> ONE gear.log WARN per weapon id. UNVERIFIED #2 / #3: if the live engine objects are not the walked
# ones, the stat would roll on axes / longswords / bows but never count - silent without this line (only /gear charged showed it).
M(gchi, r"""
public static void miss(Object[] e, String wid, int cls, boolean proj) {
  if (cls != 1 && cls != 2) return;
  if (wid == null || !walked(e) || !trusted(wid)) return;
  @PKG@.Gear.warnOnce("chgmiss:" + wid, "Charged Attack Damage: a " + (cls == 2 ? "Charged" : "Light") + "-tagged " + (proj ? "projectile" : "melee")
    + " hit judged against " + wid + " is not in that weapon's charged-step index even after a re-walk. If this repeats for the weapon's own attacks,"
    + " the live engine objects do not match the walk (its charged attack would never count although the stat rolls) - check it with /gear charged and tell the SkyyGear builder");
}""")
# THE per-hit rule (research 3.1 with the verifier's fixes, Skyy's glow rule and the review of 0.1.2). calc = the DamageCalculator of
# the hit's DamageSequence (seq = the meta key was there), wid = the weapon the hit's stats come from, proj = a projectile hit judged
# against a launch record (GearShot), alts = null for the projectile's own record (GearShotTrack.find), else the item ids of every live
# record of that shooter (the record came from GearShotTrack.pick, which picks the WEAKER weapon when several are in the air, so wid
# may not be the weapon that fired this arrow), shotCharged / pid = the launch record of a legacy projectile. why[0] = the reason
# (/gear charged, charged.log). 1 = a charged hit.
# Review finding 1: the Class-tag fallback for a step that is not in the walk ("Hytale Charged tag (the step is not in the walk)")
# is for MELEE only. A projectile hit counts only when its step is known: every live shot's weapon whose walk knows the calculator
# must call it charged (a bow's partial draw can never count because a spear / orb record was picked); a step nobody knows = not
# charged. A legacy launch flag without a damage step counts only when the record is unambiguous (one weapon in the air).
M(gchi, r"""
public static int judgeCalc(Object calc, boolean seq, String wid, boolean proj, String[] alts, boolean shotCharged, String pid, String[] why) {
  String w = null;
  int r = 0;
  String[] o = new String[1];
  if (!@PKG@.GearCfg.CHG_ON) w = "charged.on is off";
  else if (wid == null) w = "no weapon";
  else if (excluded(wid)) w = "excluded family (clubs, Kunai, Crystal Flame / Crystal Ice staff, Vampire bow)";
  else if (seq && calc != null) {
    int cls = clsCode(calc);
    if (cls == 3) w = "signature ability (Hytale Class Signature)";
    else {
      Object[] e = ensure(wid);
      int[] f = step(e, calc);
      if (f == null && found(e)) {
        e = rewalk(wid);
        f = step(e, calc);
      }
      if (!proj) {
        if (f != null) { r = stepRule(f, cls, wid, o); w = o[0]; }
        else {
          boolean part = walked(e) ? ((Boolean) e[3]).booleanValue() : partialList(wid);
          if (cls == 2 && trusted(wid) && !part) { r = 1; w = "Hytale Charged tag (the step is not in the walk)"; }
          else if (cls == 2 && !trusted(wid)) w = "Charged tag on an untrusted item (not vanilla or pack) - ignored";
          else if (cls == 2) w = "Charged tag on an item with partial charge levels, step not in the walk - ignored";
          else w = "normal attack (the step is not in the walk)";
          miss(e, wid, cls, false);
        }
      } else {
        int n = 0;
        int yes = 0;
        String good = null;
        String bad = null;
        if (f != null) {
          n = 1;
          if (stepRule(f, cls, wid, o) == 1) { yes = 1; good = o[0]; }
          else bad = o[0];
        }
        int m = alts == null ? 0 : alts.length;
        for (int i = 0; i < m; i++) {
          String x = alts[i];
          if (x == null || x.equals(wid)) continue;
          int[] g = step(ensure(x), calc);
          if (g == null) continue;
          n++;
          if (excluded(x)) { if (bad == null) bad = "fired by " + x + " - excluded family"; }
          else if (stepRule(g, cls, x, o) == 1) { yes++; if (good == null) good = o[0] + " - fired by " + x; }
          else if (bad == null) bad = o[0] + " - fired by " + x;
        }
        if (n == 0) {
          w = "projectile step not in the walk of its shot's weapon" + (m > 1 ? " or of any other live shot's weapon" : "") + " - not charged";
          miss(e, wid, cls, true);
        }
        else if (yes == n) { r = 1; w = good; }
        else w = bad;
      }
    }
  } else if (shotCharged) {
    if (proj && alts != null && alts.length > 1) w = "charged launch" + (pid == null ? "" : " (" + pid + ")") + " but shots of several weapons are in the air and the hit has no damage step - not charged";
    else { r = 1; w = "charged launch" + (pid == null ? "" : " (" + pid + ")"); }
  }
  else if (pid != null) w = "launch not charged (" + pid + ")";
  else w = "no damage step and no charged launch";
  if (why != null && why.length > 0) why[0] = w;
  return r;
}""")
M(gchi, r"""
public static String summary(String id) {
  if (id == null) return "no item";
  if (excluded(id)) return "excluded family (Skyy: clubs, Kunai, Crystal Flame / Crystal Ice staff; the Vampire bow's arrow never glows) - never counts, never rolls";
  Object[] e = ensure(id);
  if (walked(e)) return (String) e[4];
  return (String) e[4] + " - using the built-in list: " + (fallback(id) ? "has a charged attack" : "no charged attack");
}""")
M(gchi, r"""
public static String statusText() {
  if (!@PKG@.GearCfg.CHG_ON) return "Charged Attack Damage OFF (charged.on - it never rolls)";
  return "Charged Attack Damage on (spells x" + @PKG@.Gear.fnum(@PKG@.GearCfg.CHG_SPELL) + "; bows only the glowing " + @PKG@.Gear.fnum(GLOW_S) + " s full draw; never clubs, Kunai, Crystal Flame / Ice staffs, the Vampire bow)";
}""")

# GearHand (verifier fix: a single spellbook / a single thrown spear is used up by the cast before the projectile entity exists, so the
# hand is empty when GearShotTrack records the shot). CUR: UUID -> Object[] { ItemStack cur, Long since, ItemStack prev, Long prevUntil }
# kept by GearHandSys every tick (one identity compare while nothing changes). Review of 0.1.2 finding 5: an empty hand that changes
# to another empty hand (null <-> an empty stack) is no change, so the previous slot keeps the last REAL stack.
F(ghnd, "public static final java.util.concurrent.ConcurrentHashMap CUR = new java.util.concurrent.ConcurrentHashMap();")
M(ghnd, r"""
public static boolean none(Object s) {
  return s == null || ((@IS@) s).isEmpty();
}""")
M(ghnd, r"""
public static void seen(java.util.UUID u, @IS@ s) {
  if (u == null) return;
  Object[] e = (Object[]) CUR.get(u);
  if (e != null && (e[0] == s || (none(e[0]) && none(s)))) return;
  Long now = Long.valueOf(System.currentTimeMillis());
  if (e == null) CUR.put(u, new Object[] { s, now, null, Long.valueOf(0L) });
  else CUR.put(u, new Object[] { s, now, e[0], now });
}""")
M(ghnd, r"""
public static boolean launches(@IS@ s, String pid) {
  if (s == null || s.isEmpty() || pid == null) return false;
  return @PKG@.GearChg.launchCode(s.getItemId(), pid) >= 0;
}""")
M(ghnd, r"""
public static boolean gearLaunch(@IS@ s, String pid) {
  return s != null && !s.isEmpty() && @PKG@.GearData.isGear(s.getItemId()) && launches(s, pid);
}""")
# the stack that launched legacy projectile pid: the live hand when it launches pid; else the newest snapshot (the current one, then
# the previous one if it left the hand <= 1000 ms ago) whose GEAR item launches pid; else the live hand (0.1 behaviour). The live
# hand always wins when it can have launched it, so a snapshot never replaces what is really held.
M(ghnd, r"""
public static @IS@ pick(java.util.UUID u, @IS@ live, String pid, long now) {
  if (u == null || pid == null) return live;
  if (launches(live, pid)) return live;
  Object[] e = (Object[]) CUR.get(u);
  if (e == null) return live;
  @IS@ c = (@IS@) e[0];
  if (c != live && gearLaunch(c, pid)) return c;
  @IS@ p = (@IS@) e[2];
  long pu = ((Long) e[3]).longValue();
  if (p != null && now - pu <= 1000L && gearLaunch(p, pid)) return p;
  return live;
}""")
M(ghnd, "public static void forget(java.util.UUID u) { if (u != null) CUR.remove(u); }")

# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded
F(grl, "public static final java.security.SecureRandom RNG = new java.security.SecureRandom();")
M(grl, r"""
public static int randInt(int a, int b) {
  if (b <= a) return a;
  return a + RNG.nextInt(b - a + 1);
}""")
M(grl, r"""
public static int pickWeighted(double[] w) {
  double total = 0.0;
  for (int i = 0; i < w.length; i++) if (w[i] > 0.0) total = total + w[i];
  if (total <= 0.0) return 0;
  double x = RNG.nextDouble() * total;
  int lastPos = 0;
  for (int i = 0; i < w.length; i++) {
    if (w[i] <= 0.0) continue;
    lastPos = i;
    x = x - w[i];
    if (x < 0.0) return i;
  }
  return lastPos;
}""")
# col 0 = craft, 1 = mob, 2 = chest (table odds)
M(grl, r"""
public static int pickRarity(int col) {
  double[] w = col == 1 ? @PKG@.GearCfg.O_MOB : (col == 2 ? @PKG@.GearCfg.O_CHEST : @PKG@.GearCfg.O_CRAFT);
  return pickWeighted(w);
}""")
# spec 5.3: Smithing rarity = skill:fn:level(uuid, "Smithing") x smith.perLevel %, capped by smith.cap (0 without SkyySkills)
M(grl, r"""
public static double smithChance(java.util.UUID u) {
  if (u == null) return 0.0;
  int lv = @PKG@.GearGate.have(u, "Smithing");
  if (lv <= 0) return 0.0;
  double c = (double) lv * @PKG@.GearCfg.SMITH_PER;
  if (c > @PKG@.GearCfg.SMITH_CAP) c = @PKG@.GearCfg.SMITH_CAP;
  return c < 0.0 ? 0.0 : c;
}""")
# base rarity from the craft odds, never above craft.maxRarity; with the Smithing chance it steps up one tier (never above the cap,
# never to Set; a rolled Set - weight 0 by default - stays Set)
M(grl, r"""
public static int craftRarity(java.util.UUID u, double[] smithOut) {
  int r = pickRarity(0);
  if (r == 6) return r;
  int max = @PKG@.GearCfg.craftMax();
  if (r > max) r = max;
  double c = smithChance(u);
  if (smithOut != null && smithOut.length > 0) smithOut[0] = c;
  if (c > 0.0 && r < max && r < 5 && RNG.nextDouble() * 100.0 < c) r = r + 1;
  return r;
}""")
M(grl, r"""
public static boolean allowed(int i, int slot) {
  String s = @PKG@.GearDefs.S_SLOT[i];
  if (slot == 2) return s.indexOf('a') >= 0;
  if (slot == 0) return s.indexOf('w') >= 0;
  if (slot == 1) return s.indexOf('w') >= 0 || s.indexOf('s') >= 0;
  if (slot == 4) return s.indexOf('e') >= 0;
  return false;
}""")
# 0.1.2: id = the item being rolled - Charged Attack Damage only where GearChg.canRoll says (charged.on, armor, a weapon with a
# detectable charged attack; Skyy's lock: never a stat that does nothing). pool(slot) = no item known = never chg on a weapon.
M(grl, r"""
public static int[] pool(int slot, String id) {
  int[] w = @PKG@.GearCfg.S_W;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.GearDefs.NS; i++) {
    if (!allowed(i, slot) || w[i] <= 0) continue;
    if (@PKG@.GearDefs.S_LIVE[i] == 0 && !@PKG@.GearCfg.POOL_LATER) continue;
    if (i == @PKG@.GearDefs.I_CHG && !@PKG@.GearChg.canRoll(id, slot)) continue;
    l.add(Integer.valueOf(i));
  }
  int[] a = new int[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = ((Integer) l.get(i)).intValue();
  return a;
}""")
M(grl, "public static int[] pool(int slot) { return pool(slot, null); }")
# value bounds of stat i for rarity r at item level lvl: { lo, hi } = max(1, round(max x low/100 x f/100)) .. (high)
M(grl, r"""
public static int[] bounds(int i, int r, int lvl) {
  int rr = @PKG@.GearCfg.ri(r);
  double f = @PKG@.GearLevel.factor(lvl);
  double mx = (double) @PKG@.GearCfg.S_MAX[i];
  long lo = Math.round(mx * (double) @PKG@.GearCfg.R_LO[rr] / 100.0 * f / 100.0);
  long hi = Math.round(mx * (double) @PKG@.GearCfg.R_HI[rr] / 100.0 * f / 100.0);
  if (lo < 1L) lo = 1L;
  if (hi < 1L) hi = 1L;
  if (hi < lo) hi = lo;
  return new int[] { (int) lo, (int) hi };
}""")
# design review 5: Health Regen % only scales Raw Health Regen, so it is a candidate only after Raw Health Regen was picked
M(grl, r"""
public static double wAt(int si, int[] w, boolean[] pick) {
  if (si == @PKG@.GearDefs.I_HPRP && !pick[@PKG@.GearDefs.I_HPR]) return 0.0;
  return (double) w[si];
}""")
# spec 2.3: pick count distinct stats (weighted, no repeats, capped by the pool), roll each value, display order = table order
M(grl, r"""
public static @BA@ rollMods(String id, int slot, int r, int lvl) {
  @BA@ out = new @BA@();
  int[] p = pool(slot, id);
  if (p.length == 0) return out;
  int count = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  if (count > p.length) count = p.length;
  int[] w = @PKG@.GearCfg.S_W;
  boolean[] used = new boolean[p.length];
  boolean[] pick = new boolean[@PKG@.GearDefs.NS];
  for (int k = 0; k < count; k++) {
    double total = 0.0;
    for (int j = 0; j < p.length; j++) if (!used[j]) total = total + wAt(p[j], w, pick);
    if (total <= 0.0) break;
    double x = RNG.nextDouble() * total;
    int sel = -1;
    for (int j = 0; j < p.length; j++) {
      if (used[j]) continue;
      double wj = wAt(p[j], w, pick);
      if (wj <= 0.0) continue;
      sel = j;
      x = x - wj;
      if (x < 0.0) break;
    }
    if (sel < 0) break;
    used[sel] = true;
    pick[p[sel]] = true;
  }
  for (int i = 0; i < @PKG@.GearDefs.NS; i++) {
    if (!pick[i]) continue;
    int[] b = bounds(i, r, lvl);
    out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], randInt(b[0], b[1])));
  }
  return out;
}""")
M(grl, "public static @BA@ rollMods(int slot, int r, int lvl) { return rollMods(null, slot, r, lvl); }")
M(grl, r"""
public static String pickName(String cur) {
  String[] ns = @PKG@.GearCfg.names();
  if (ns.length == 0) return null;
  if (ns.length == 1) return ns[0];
  for (int k = 0; k < 32; k++) {
    String n = ns[RNG.nextInt(ns.length)];
    if (cur == null || !n.equals(cur)) return n;
  }
  return ns[0].equals(cur) ? ns[1] : ns[0];
}""")
# a fresh document: rarity r, identified or not (unidentified = no modifiers stored; they roll at identify time, spec 5.6). 0.2 (spec 4
# "order matters"): lvl >= 0 is stamped into the document BEFORE the modifiers roll, so they roll at the item's own level; lvl < 0 = no
# stamp (part.levels off: the item reads its table level like 0.1.3)
M(grl, r"""
public static @BD@ newDoc(String id, int r, boolean ident, String src, int lvl) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);
  if (lvl >= 0) d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lvl)));
  if (ident) d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  return d;
}""")
# the 0.1.3 entry point (admin /gear give, the unidentified drop / chest tag, the /craft bridge with another source): 0.2 stamps the item's
# band start = the level it reads from the table today (stage 4 rolls found gear inside a zone band later)
M(grl, r"""
public static @BD@ newDoc(String id, int r, boolean ident, String src) {
  return newDoc(id, r, ident, src, @PKG@.GearCfg.PART_LEVELS ? @PKG@.GearLevel.level(id, null) : -1);
}""")
# ---- 0.2 CRAFTED AT YOUR LEVEL (spec 4, LOCKED Skyy 2026-10-01 "all items crafted are crafted at your level").
# craft.weaponSkill: "prefix:Skill" pairs (comma list); the longest prefix that matches the id names the skill its craft reads; null = none
M(grl, r"""
public static String weaponSkill(String id) {
  String s = @PKG@.GearCfg.CRAFT_SKILL;
  if (id == null || s == null || s.trim().length() == 0) return null;
  String best = null;
  int bl = -1;
  String[] ps = s.split(",");
  for (int i = 0; i < ps.length; i++) {
    String t = ps[i].trim();
    int c = t.indexOf(':');
    if (c <= 0 || c >= t.length() - 1) continue;
    String pre = t.substring(0, c).trim();
    String sk = t.substring(c + 1).trim();
    if (pre.length() == 0 || sk.length() == 0) continue;
    if (pre.length() > bl && id.startsWith(pre)) { best = sk; bl = pre.length(); }
  }
  return best;
}""")
# the SkyySkills skill a craft of this item reads: craft.weaponSkill, else the item's GATE skill (LOCKED 2026-09-25: combat gear and
# Equipment = the crafter's class weapon skill - "Combat" without SkyyClasses; mining / foraging / farming tools = that gathering skill);
# null = none (SkyyClasses present but no class picked, a kind without a skill)
M(grl, r"""
public static String craftSkill(String id, java.util.UUID u) {
  String w = weaponSkill(id);
  if (w != null) return w;
  String g = @PKG@.GearDefs.kindGate(@PKG@.GearData.kindFor(id));
  if (g == null || g.length() == 0) return null;
  return @PKG@.GearGate.gateSkill(u, g);
}""")
# the crafter's level in that skill: >= 0, or -1 = none (no skill / no class, no SkyySkills); a skill SkyySkills does not know counts as 0
# (the gate's own rule)
M(grl, r"""
public static int craftHave(String id, java.util.UUID u) {
  if (u == null) return -1;
  String sk = craftSkill(id, u);
  if (sk == null) return -1;
  int h = @PKG@.GearGate.have(u, sk);
  if (h == -2) return -1;
  return h < 0 ? 0 : h;
}""")
# the skill's name for a craft line (the gate's label for the class gate: "Divinity", "Class skill", "Combat")
M(grl, r"""
public static String craftLabel(String id, java.util.UUID u) {
  String w = weaponSkill(id);
  if (w != null) return w;
  return @PKG@.GearGate.gateLabel(u, @PKG@.GearDefs.kindGate(@PKG@.GearData.kindFor(id)));
}""")
# the level a craft stamps: the crafter's skill level (raised to level.gateFloor) moved into the item's band - below it = the band start
# (craft.belowBand min; block refuses at the bench before this), above it = the band's cap (Skyy: a level 80 player crafting a Copper
# pickaxe gets the Copper cap). The band start with craft.levelFrom band, without SkyySkills or without a class picked; -1 = no stamp
# (part.levels off)
M(grl, r"""
public static int craftLevel(String id, java.util.UUID u) {
  if (!@PKG@.GearCfg.PART_LEVELS) return -1;
  int[] b = @PKG@.GearLevel.band(id);
  if (!"gate".equals(@PKG@.GearCfg.CRAFT_FROM)) return b[0];
  int h = craftHave(id, u);
  if (h < 0) return b[0];
  int f = @PKG@.GearLevel.floor(h);
  if (f < b[0]) return b[0];
  if (f > b[1]) return b[1];
  return f;
}""")
# the one chat line a craft below / above the band gets (null = none): only for a material band (an exact Level by item / Hytale level has
# no range) and only when the crafter's skill level is known. Review of 0.2 finding 1: the below-band line says "you need <Skill> N to use
# it", which is only true where the gate is ENFORCED (GearDefs.enforcedKind: combat + equipment) - the gathering tools' gate is "coming
# later" (never enforced), so a tool crafted below its band gets no line at all (its tooltip shows "Lv N - Requires Mining N (coming
# later)"); the cap line stays for tools (true: the stamped level is the cap - Skyy's level-80 copper pickaxe). The kind is the one the new
# document gets (GearRoll.newDoc -> GearData.base(kindFor(id))), so a kind.prefix row that makes a tool enforced brings the line back.
M(grl, r"""
public static String craftNote(String id, java.util.UUID u) {
  if (!@PKG@.GearCfg.PART_LEVELS || !"gate".equals(@PKG@.GearCfg.CRAFT_FROM)) return null;
  int[] b = @PKG@.GearLevel.band(id);
  if (b[2] != 1) return null;
  int h = craftHave(id, u);
  if (h < 0) return null;
  int f = @PKG@.GearLevel.floor(h);
  if (f < b[0]) {
    if (!@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kindFor(id))) return null;
    return "Made at Lv " + b[0] + " (the lowest level of " + @PKG@.GearLevel.bandWord(id) + ") - you need " + craftLabel(id, u) + " " + b[0] + " to use it (you: " + h + ").";
  }
  if (f > b[1]) return @PKG@.GearLevel.bandWord(id) + " caps at Lv " + b[1] + " - a better material goes higher.";
  return null;
}""")
# review of 0.2 finding 3: timed bench crafts fire one CraftRecipeEvent$Post per unit (GearCraftSys: units = 1 when TimeSeconds > 0), so a
# queue of 10 Copper staffs below the band would print 10 identical lines. One line per player + item per crafting burst: the line is sent
# only when that player got no line for that item in the last NOTE_MS (10 s); every craft that had a line refreshes the time, so a long
# queue (3-5 s per unit) prints once. Both craft paths (the bench task, /craft mode 8) ask here; the bench refusal (blockWhy) is not
# throttled (one line per refused click is the answer to that click).
F(grl, "public static final long NOTE_MS = 10000L;")
F(grl, "public static final java.util.HashMap NOTED = new java.util.HashMap();")
M(grl, r"""
public static synchronized boolean noteDue(java.util.UUID u, String id, long now) {
  String k = String.valueOf(u) + "|" + id;
  Long last = (Long) NOTED.get(k);
  NOTED.put(k, Long.valueOf(now));
  if (NOTED.size() > 512) {
    java.util.Iterator it = NOTED.values().iterator();
    while (it.hasNext()) {
      Long v = (Long) it.next();
      if (now - v.longValue() >= NOTE_MS) it.remove();
    }
  }
  return last == null || now - last.longValue() >= NOTE_MS;
}""")
# craft.belowBand block: why a vanilla bench craft is refused (null = allowed) - the crafter is below the item's material band. Review of 0.2
# finding 1: never for a kind whose gate is not enforced (the gathering tools: "coming later") - a tool you could use is never refused
M(grl, r"""
public static String blockWhy(String id, java.util.UUID u) {
  if (!@PKG@.GearCfg.PART_LEVELS || !"block".equals(@PKG@.GearCfg.CRAFT_BELOW) || !"gate".equals(@PKG@.GearCfg.CRAFT_FROM)) return null;
  if (!@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kindFor(id))) return null;
  int[] b = @PKG@.GearLevel.band(id);
  if (b[2] != 1) return null;
  int h = craftHave(id, u);
  if (h < 0 || @PKG@.GearLevel.floor(h) >= b[0]) return null;
  return "You need " + craftLabel(id, u) + " " + b[0] + " to craft " + @PKG@.Gear.itemName(id) + " (you: " + h + ") - " + @PKG@.GearLevel.bandWord(id) + " starts at Lv " + b[0] + ".";
}""")
# which crafted outputs get a document: gear, and (part.levels) the gathering tools of TOOL_FAMILIES (pickaxe, shovel, hatchet, hoe, sickle:
# they store and show a level - spec 1 "Tools"; their gate stays "coming later" and they never get modifiers)
M(grl, r"""
public static boolean craftable(String id) {
  if (id == null) return false;
  if (@PKG@.GearData.isGear(id)) return true;
  return @PKG@.GearCfg.PART_LEVELS && @PKG@.GearData.isTool(id) && !"tool".equals(@PKG@.GearData.toolKind(id));
}""")
# a crafted document at level lvl (craftLevel; -1 = no stamp). Rarity from the craft odds + Smithing; a plain tool (not gear) stays Normal:
# it has no modifiers yet ("coming later" stats never roll, LOCKED 2026-09-30)
M(grl, r"""
public static @BD@ craftDoc(String id, java.util.UUID u, int lvl) {
  int r = (@PKG@.GearData.isTool(id) && !@PKG@.GearData.isGear(id)) ? 0 : craftRarity(u, null);
  return newDoc(id, r, true, "craft", lvl);
}""")
M(grl, "public static @BD@ craftDoc(String id, java.util.UUID u) { return craftDoc(id, u, craftLevel(id, u)); }")
# PART B: the unidentified tag (col 1 = mob -> src drop, col 2 = chest -> src chest)
M(grl, "public static @BD@ unidDoc(String id, int col, String src) { return newDoc(id, pickRarity(col), false, src); }")
# 0.2 (spec 8): a document that is rewritten anyway (reforge, identify) gets its level stamped when it has none - the level it reads now, so
# it keeps the level its modifiers roll at; an existing lvl is never changed (spec 4: reforge / identify never change a level)
M(grl, r"""
public static void stampIfMissing(String id, @BD@ d) {
  if (d == null || !@PKG@.GearCfg.PART_LEVELS || @PKG@.GearLevel.stamped(d)) return;
  d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.level(id, d)));
}""")
# spec 5.4: a reforge re-rolls the whole modifier set for the rarity + level, picks a new cosmetic name, rfN++; rarity, level, set,
# id and src never change; unknown fields are kept (clone, change, put back - reading rule 3)
M(grl, r"""
public static @BD@ reforge(String id, @BD@ doc) {
  @BD@ d = doc.clone();
  stampIfMissing(id, d);
  int r = @PKG@.GearData.rarity(d);
  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  String n = pickName(@PKG@.GearData.str(d, "rf", null));
  if (n != null) d.put("rf", new org.bson.BsonString(n));
  else d.remove("rf");
  d.put("rfN", new org.bson.BsonInt32(@PKG@.GearData.num(d, "rfN", 0) + 1));
  d.put("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  return d;
}""")
# spec 5.7: identify rolls the modifiers for the item's rarity (PART B's page and the admin /gear identify call it)
M(grl, r"""
public static @BD@ identify(String id, @BD@ doc, java.util.UUID by) {
  @BD@ d = doc.clone();
  stampIfMissing(id, d);
  int r = @PKG@.GearData.rarity(d);
  long now = System.currentTimeMillis();
  d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  d.put("id", new org.bson.BsonBoolean(true));
  d.put("idAt", new org.bson.BsonInt64(now));
  if (by != null) d.put("idBy", new org.bson.BsonString(by.toString()));
  d.put("at", new org.bson.BsonInt64(now));
  return d;
}""")
# exploit review 5: migrate.clampToLevel ON = a migrated value never above the best roll of its new rarity at the item's level
M(grl, r"""
public static int clampOld(String key, int v, int r, int lvl) {
  int i = @PKG@.GearDefs.sIndex(key);
  if (i < 0) return v;
  int hi = bounds(i, r, lvl)[1];
  return v > hi ? hi : v;
}""")
# exploit review 2: a split single item keeps apart from its neighbours (identical documents would stack again)
M(grl, r"""
public static @BD@ nonce(@BD@ d) {
  d.put("k", new org.bson.BsonInt32(RNG.nextInt()));
  return d;
}""")

# ================================================================= GearData (1b): migration + the reading rules (spec 1.2, 1.6)
M(gdt, r"""
public static @BD@ migrate(String id, @BD@ rolls) {
  String kind = kindFor(id);
  int r = migrateRarity(id, rolls);
  @BD@ d = base(kind, r, true, "rolls");
  @BA@ ms = new @BA@();
  int vDmg = num(rolls, "dmg", 0);
  int vStr = num(rolls, "str", 0);
  int vCrit = num(rolls, "crit", 0);
  if (slotOf(id) == 2) vDmg = 0;
  if (@PKG@.GearCfg.MIGRATE_CLAMP) {
    int lvl = @PKG@.GearLevel.level(id, d);
    vDmg = @PKG@.GearRoll.clampOld("dmg", vDmg, r, lvl);
    vStr = @PKG@.GearRoll.clampOld("str", vStr, r, lvl);
    vCrit = @PKG@.GearRoll.clampOld("cc", vCrit, r, lvl);
  }
  if (vDmg != 0) ms.add(mod("dmg", vDmg));
  if (vStr != 0) ms.add(mod("str", vStr));
  if (vCrit != 0) ms.add(mod("cc", vCrit));
  d.put("mods", ms);
  String rf = str(rolls, "reforge", null);
  if (rf != null && rf.trim().length() > 0 && !rf.equals("?") && @PKG@.GearDefs.rIndex(rf) < 0) d.append("rf", new org.bson.BsonString(rf.trim()));
  d.append("old", rolls.clone());
  return d;
}""")
# spec 1.2 reading rules 1 + 2 (the in-memory view every reader uses); null = unreadable / newer schema / not gear
M(gdt, r"""
public static @BD@ effective(String id, @BD@ md) {
  int st = state(md);
  if (st == 1) return gearDoc(md);
  if (st == 3 || st == 4) return null;
  if (st == 2) return (isGear(id) || isTool(id)) ? migrate(id, rollsDoc(md)) : null;
  if (isGear(id)) return legacy(id);
  return null;
}""")

# ================================================================= 0.2.1 GearBase: BASE STATS FROM THE ITEM LEVEL (spec 3, stages 2 + 3)
# Pure computations (no ECS, any thread): the curves F(L) / R(L) (GearCfg.BASE_CURVE / BASE_RES, parsed once per text), the material
# bonus, K (family base sizes from the engine's own damage breakdowns, cached per id), the weapon multiplier a hit gets, the tooltip's
# levelled damage range and the per-piece armor targets. GearHit (weapon hits), GearArmor (the lock want + resistance) and GearView
# (tooltip) call these.
F(gbase, "public static volatile String FSRC = null;")
F(gbase, "public static volatile Object[] FP = null;")
F(gbase, "public static volatile String RSRC = null;")
F(gbase, "public static volatile Object[] RP = null;")
F(gbase, "public static final java.util.concurrent.ConcurrentHashMap RAT = new java.util.concurrent.ConcurrentHashMap();")   # id -> Double
F(gbase, "public static final java.util.concurrent.ConcurrentHashMap BASE = new java.util.concurrent.ConcurrentHashMap();")  # id -> base ("" = itself)
# the vanilla-block decision (see the header): the client draws its own Damage Data / Health / resistance lines from the ITEM ASSET under
# our per-stack text, and nothing per stack can hide them - so our lines say they are the levelled numbers and these hints say what the
# vanilla box below is
F(gbase, 'public static final String HINT_W = "(the Damage Data box below is vanilla - before levels)";')
# review of 0.2.1 finding 4: no hint is longer than the longest tooltip line 0.2 already showed in game (57 characters, "Unidentified -
# its modifiers appear when you identify it.") - whether the client wraps a longer line is UNVERIFIED (the 0.2.1 armor hint had 65)
F(gbase, 'public static final String HINT_A = "(Health / Resistance below are vanilla - before levels)";')
assert len("(the Damage Data box below is vanilla - before levels)") <= 57 and len("(Health / Resistance below are vanilla - before levels)") <= 57
M(gbase, r"""
public static void clear() {
  RAT.clear();
  BASE.clear();
  FSRC = null;
  FP = null;
  RSRC = null;
  RP = null;
}""")
# straight lines between the points, the end values outside them (spec 3.1: F(1) = 1 exactly with the default points)
M(gbase, r"""
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
M(gbase, r"""
public static synchronized Object[] reF(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.CURVE_DEF);
  FP = p;
  FSRC = s;
  return p;
}""")
M(gbase, r"""
public static synchronized Object[] reR(String s) {
  Object[] p = @PKG@.GearCfg.curvePts(s);
  if (p == null) p = @PKG@.GearCfg.curvePts(@PKG@.GearCfg.RES_DEF);
  RP = p;
  RSRC = s;
  return p;
}""")
# F(L): weapon damage + armor Health; R(L): armor resistance (base.curve / base.resCurve, live: a new text is parsed on first use)
M(gbase, r"""
public static double curveF(int lv) {
  String s = @PKG@.GearCfg.BASE_CURVE;
  Object[] p = FP;
  if (p == null || s != FSRC) p = reF(s);
  return eval(p, (double) lv);
}""")
M(gbase, r"""
public static double curveR(int lv) {
  String s = @PKG@.GearCfg.BASE_RES;
  Object[] p = RP;
  if (p == null || s != RSRC) p = reR(s);
  return eval(p, (double) lv);
}""")
# spec 3.1 material bonus: 1 + base.matBonus % x the band's start level; a band that starts at Lv 1 (Wood / Crude, copper armor) gets
# none, so a Lv 1 kit item keeps exactly its vanilla numbers (F(1) = 1, K = 1) - the spec's own worked table leaves the bonus out too
M(gbase, r"""
public static double bonus(int start) {
  if (start <= 1) return 1.0;
  double b = @PKG@.GearCfg.BASE_MAT;
  if (!(b > 0.0)) return 1.0;
  return 1.0 + b * (double) start / 100.0;
}""")
M(gbase, "public static boolean on() { return @PKG@.GearCfg.PART_BASE && !\"off\".equals(@PKG@.GearCfg.BASE_MODE); }")
M(gbase, "public static boolean armorOn() { return @PKG@.GearCfg.PART_BASE && @PKG@.GearCfg.BASE_ARMOR; }")
# the weapon family = the id word after Weapon_ (Weapon_Sword_Copper -> Sword, Weapon_Kunai -> Kunai); null = not a Weapon_ id
M(gbase, r"""
public static String family(String id) {
  if (id == null || !id.startsWith("Weapon_") || id.length() <= 7) return null;
  String r = id.substring(7);
  int u = r.indexOf('_');
  return u < 0 ? r : r.substring(0, u);
}""")
# spec 3.2 the family's Lv 1 base item: the build's table (Crude / Wood / Iron item of the family), else the same search over the live item
# map (other mods' families), else the item itself; cached per id
M(gbase, r"""
public static String baseOf(String id) {
  if (id == null) return null;
  Object o = BASE.get(id);
  if (o instanceof String) { String s0 = (String) o; return s0.length() == 0 ? id : s0; }
  String f = family(id);
  String b = null;
  if (f != null) {
    for (int i = 0; i < @PKG@.GearDefs.FB_FAM.length; i++) if (b == null && @PKG@.GearDefs.FB_FAM[i].equals(f)) b = @PKG@.GearDefs.FB_ID[i];
    if (b == null) {
      String[] tr = new String[] { "_Crude", "_Wood", "_Iron" };
      for (int i = 0; i < tr.length; i++) { String c = "Weapon_" + f + tr[i]; if (b == null && @PKG@.Gear.item(c) != null) b = c; }
    }
  }
  if (b == null || @PKG@.Gear.item(b) == null) b = id;
  if (BASE.size() > 4096) BASE.clear();
  BASE.put(id, b.equals(id) ? "" : b);
  return b;
}""")
# the largest entry of the item's basic (primary-attack) damage breakdown - the engine's own WeaponDamageDataCollector result that
# damageText shows; -1 = no item / no weapon / unreadable, 0 = a weapon without any primary damage entry (spellbooks)
M(gbase, r"""
public static float maxEntry(String id) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return -1.0f;
    @IWP@ w = it.getWeapon();
    if (w == null) return -1.0f;
    @DBD@ b = w.getBasicDamageBreakdown();
    if (b == null) return 0.0f;
    java.util.List es = b.entries();
    if (es == null) return 0.0f;
    float hi = 0.0f;
    for (int i = 0; i < es.size(); i++) {
      Object o = es.get(i);
      if (!(o instanceof @DBE@)) continue;
      float z = ((@DBE@) o).max();
      if (z > hi) hi = z;
    }
    return hi;
  } catch (Throwable t) { return -1.0f; }
}""")
# K before the base-level divisor: base item's largest entry / this item's (spec 3.2; vanilla steps scale evenly inside one item, so one
# number per item); 1 for a base item and for a weapon with no primary damage (spellbooks); 1 + one WARN per id when the item or its
# family base has damage data that cannot be read (the task's "unreadable step -> plain multiply, logged once"). Review of 0.2.1 nit: a
# FAILED read (maxEntry -1: no item / no weapon / an exception) is not cached - the next hit reads again (the WARN stays once), so one
# transient failure never fixes K = 1 for the server's lifetime; a definite answer (a ratio, no primary damage) is cached as before
M(gbase, r"""
public static double ratio(String id) {
  if (id == null) return 1.0;
  Object o = RAT.get(id);
  if (o instanceof Double) return ((Double) o).doubleValue();
  double r = 1.0;
  boolean keep = true;
  String b = baseOf(id);
  if (!b.equals(id)) {
    float mi = maxEntry(id);
    float mb = maxEntry(b);
    if (mi > 0.0f && mb > 0.0f) r = (double) mb / (double) mi;
    else if (mi != 0.0f) @PKG@.Gear.warnOnce("basek:" + id, "base damage: the damage data of " + id + " or of its family base " + b + " could not be read - its hits get the plain level multiplier (no scaling to the " + b + " size)");
    if (mi < 0.0f || mb < 0.0f) keep = false;
  }
  if (!keep) return r;
  if (RAT.size() > 4096) RAT.clear();
  RAT.put(id, Double.valueOf(r));
  return r;
}""")
# K = ratio / (F(start) x bonus(start)) of the family base's band start: an item that is its own base deals exactly vanilla at its band
# start (the Crude / Wood bases start at 1, divisor 1; the Iron crossbow starts at 15). Spell projectiles (orbs: the same projectile for
# every wand, staff and spellbook) have K = 1 (spec 3.2).
M(gbase, r"""
public static double kOf(String id, boolean spell) {
  if (spell) return 1.0;
  String b = baseOf(id);
  int lb = @PKG@.GearLevel.band(b)[0];
  double div = curveF(lb) * bonus(lb);
  if (!(div > 0.0)) div = 1.0;
  return ratio(id) / div;
}""")
# spec 3.2: m = K x F(level) x (1 + base.matBonus % x band start) - the multiplier on the engine's own amount of every step
M(gbase, r"""
public static double mult(String id, @BD@ d, boolean spell) {
  int lv = @PKG@.GearLevel.level(id, d);
  int st = @PKG@.GearLevel.band(id)[0];
  return kOf(id, spell) * curveF(lv) * bonus(st);
}""")
# what a weapon hit gets (GearHit.weaponHit): 1 when part.base / base.mode is off or the stack is no gear weapon with a document; a level
# that cannot be read = 1 + one WARN per id (spec 3.5 item 4)
M(gbase, r"""
public static double weaponMult(@IS@ main, boolean spell) {
  if (!on() || main == null || main.isEmpty()) return 1.0;
  String id = main.getItemId();
  int sl = @PKG@.GearData.slotOf(id);
  if ((sl != 0 && sl != 1) || !@PKG@.GearData.isGear(id)) return 1.0;
  @BD@ d = @PKG@.GearData.effective(id, main.getMetadata());
  if (d == null) return 1.0;
  try {
    double m = mult(id, d, spell);
    if (Double.isNaN(m) || Double.isInfinite(m) || m < 0.0) return 1.0;
    return m;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("basemult:" + id, "base damage: the level of " + id + " could not be read - its hits keep the vanilla amount (" + t + ")");
    return 1.0;
  }
}""")
M(gbase, r"""
public static float[] rangeOf(@DBD@ b) {
  if (b == null) return null;
  java.util.List es = b.entries();
  if (es == null || es.isEmpty()) return null;
  float lo = Float.MAX_VALUE;
  float hi = 0f;
  for (int i = 0; i < es.size(); i++) {
    Object o = es.get(i);
    if (!(o instanceof @DBE@)) continue;
    @DBE@ e = (@DBE@) o;
    float a = e.min();
    float z = e.max();
    if (z <= 0f) continue;
    if (a < 0f) a = 0f;
    if (a < lo) lo = a;
    if (z > hi) hi = z;
  }
  if (hi <= 0f) return null;
  if (lo == Float.MAX_VALUE || lo > hi) lo = hi;
  return new float[] { lo, hi };
}""")
# the tooltip's levelled range = the vanilla breakdown range (damageText's) x m; null = no damage data
M(gbase, r"""
public static float[] range(String id, @BD@ d) {
  try {
    @ITM@ item = @PKG@.Gear.item(id);
    if (item == null) return null;
    @IWP@ w = item.getWeapon();
    if (w == null) return null;
    float[] r = rangeOf(w.getBasicDamageBreakdown());
    if (r == null) r = rangeOf(w.getUltimateDamageBreakdown());
    if (r == null) return null;
    double m = mult(id, d, false);
    return new float[] { (float) ((double) r[0] * m), (float) ((double) r[1] * m) };
  } catch (Throwable t) { return null; }
}""")
# review of 0.2.1 finding 2: true when this weapon's levelled hits ARE its vanilla ones (m = 1 up to float noise: the Lv 1 kit items, an
# item that is its own family base at its band start, e.g. the Iron crossbow at Lv 15) - the tooltip then keeps 0.2's plain line
# ("Damage: 6-8", no grey hint: the vanilla box below shows the same numbers); spell = the cast's multiplier (K = 1)
M(gbase, r"""
public static boolean asVanilla(String id, @BD@ d, boolean spell) {
  try { return Math.abs(mult(id, d, spell) - 1.0) < 1.0E-9; } catch (Throwable t) { return false; }
}""")
# review of 0.2.1 finding 3: the vanilla damage of the spell projectiles a weapon casts = every legacy projectile its interactions launch
# (GearChg's walk: LaunchProjectileInteraction ProjectileId - the orb Skeleton_Mage_Corruption_Orb 25 of every wand / staff / spellbook,
# the Frost staff's Ice_Ball 20, the Crystal Red staff's Fireball 60) -> { min, max } of Projectile.getDamage(), what the engine deals on
# the hit (before a broken weapon's penalty); null = no legacy launch / unreadable
M(gbase, r"""
public static float[] spellBase(String id) {
  try {
    Object[] e = @PKG@.GearChg.ensure(id);
    if (!@PKG@.GearChg.found(e)) return null;
    java.util.HashMap l = (java.util.HashMap) e[1];
    if (l == null || l.isEmpty()) return null;
    float lo = Float.MAX_VALUE;
    float hi = 0f;
    java.util.Iterator it = l.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (!(k instanceof String)) continue;
      Object p = @LPRJ@.getAssetMap().getAsset(k);
      if (!(p instanceof @LPRJ@)) continue;
      float z = (float) ((@LPRJ@) p).getDamage();
      if (z <= 0f) continue;
      if (z < lo) lo = z;
      if (z > hi) hi = z;
    }
    if (hi <= 0f) return null;
    return new float[] { lo, hi };
  } catch (Throwable t) { return null; }
}""")
# the tooltip's levelled spell range = spellBase x the spell multiplier (K = 1, so m = F(level) x material bonus - exactly what
# GearHit.weaponHit gives a spell weapon's projectile hit); null = no spell projectile
M(gbase, r"""
public static float[] spellRange(String id, @BD@ d) {
  try {
    float[] r = spellBase(id);
    if (r == null) return null;
    double m = mult(id, d, true);
    return new float[] { (float) ((double) r[0] * m), (float) ((double) r[1] * m) };
  } catch (Throwable t) { return null; }
}""")
# round half up (spec 3.3) and the tooltip texts
M(gbase, "public static long rint(double x) { return (long) Math.floor(x + 0.5); }")
M(gbase, r"""
public static String rangeText(float[] r) {
  long a = rint((double) r[0]);
  long z = rint((double) r[1]);
  return a == z ? String.valueOf(a) : a + "-" + z;
}""")
M(gbase, r"""
public static String pct(double frac) {
  double p = Math.floor(frac * 1000.0 + 0.5) / 10.0;
  return @PKG@.Gear.fnum(p) + "%";
}""")
# ---- armor (spec 3.4): slot index of an armor asset (Head 0, Chest 1, Legs 2, Hands 3; -1 = none / another slot)
M(gbase, r"""
public static int slotIdx(@ITM@ it) {
  try {
    @IAR@ a = it == null ? null : it.getArmor();
    Object sl = a == null ? null : a.getArmorSlot();
    if (!(sl instanceof java.lang.Enum)) return -1;
    String n = ((java.lang.Enum) sl).name();
    for (int i = 0; i < @PKG@.GearCfg.BA_SLOT.length; i++) if (@PKG@.GearCfg.BA_SLOT[i].equalsIgnoreCase(n)) return i;
  } catch (Throwable t) { }
  return -1;
}""")
# the per-stack target of an armor piece: { Health = slot base x F(level) x material bonus, Physical = Projectile resistance (a fraction) =
# slot base % x R(level) } (spec 3.4: resistance gets no material bonus); null = base.armorOn / part.base off or no slot base
M(gbase, r"""
public static float[] armorTarget(String id, @BD@ d) {
  if (!armorOn() || id == null) return null;
  @ITM@ it = @PKG@.Gear.item(id);
  int si = slotIdx(it);
  if (si < 0) return null;
  double[] bh = @PKG@.GearCfg.BA_H;
  double[] br = @PKG@.GearCfg.BA_R;
  if (bh == null || br == null || si >= bh.length || si >= br.length) return null;
  int lv = @PKG@.GearLevel.level(id, d);
  int st = @PKG@.GearLevel.band(id)[0];
  double h = bh[si] * curveF(lv) * bonus(st);
  double r = br[si] / 100.0 * curveR(lv);
  return new float[] { (float) h, (float) r };
}""")
# the asset's own Health (every ADDITIVE Health stat modifier of the piece, as StatModifiersManager adds them; broken handled by callers)
M(gbase, r"""
public static float nativeHealth(@ITM@ it) {
  try {
    @IAR@ a = it == null ? null : it.getArmor();
    Object sm = a == null ? null : a.getStatModifiers();
    if (!(sm instanceof java.util.Map)) return 0.0f;
    int hi = @DST@.getHealth();
    float s = 0.0f;
    java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
    while (e.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) e.next();
      if (!(en.getKey() instanceof Number) || ((Number) en.getKey()).intValue() != hi || !(en.getValue() instanceof Object[])) continue;
      Object[] xs = (Object[]) en.getValue();
      for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @SMO@ && ((@SMO@) xs[j]).getCalculationType() == @CAL@.ADDITIVE) s = s + ((@SMO@) xs[j]).getAmount();
    }
    return s;
  } catch (Throwable t) { return 0.0f; }
}""")
# the asset's own multiplier resistance against one cause id (every non-FLAT ResistanceModifier of that cause, as the engine's
# calculateResistanceEntryModifications adds them to multiplierModifier)
M(gbase, r"""
public static float assetRes(@ITM@ it, String cause) {
  try {
    @IAR@ a = it == null ? null : it.getArmor();
    Object dr = a == null ? null : a.getDamageResistanceValues();
    if (!(dr instanceof java.util.Map)) return 0.0f;
    float s = 0.0f;
    java.util.Iterator e = ((java.util.Map) dr).entrySet().iterator();
    while (e.hasNext()) {
      java.util.Map.Entry en = (java.util.Map.Entry) e.next();
      Object k = en.getKey();
      String cid = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
      if (!cause.equals(cid) || !(en.getValue() instanceof Object[])) continue;
      Object[] xs = (Object[]) en.getValue();
      for (int j = 0; j < xs.length; j++) if (xs[j] instanceof @RMOD@ && ((@RMOD@) xs[j]).getCalculationType() != @RCT@.FLAT) s = s + ((@RMOD@) xs[j]).getAmount();
    }
    return s;
  } catch (Throwable t) { return 0.0f; }
}""")
# review of 0.2.1 finding 2, the same rule for armor: true when this piece's levelled Health + Physical / Projectile resistance ARE its
# asset's own numbers (a Lv 1 copper piece: the slot base = the vanilla Copper row, F(1) = R(1) = 1, no bonus for a band starting at 1) -
# the tooltip then keeps 0.2's armor line and no grey hint (the vanilla lines below show the same numbers)
M(gbase, r"""
public static boolean armorAsVanilla(String id, @BD@ d) {
  try {
    float[] tg = armorTarget(id, d);
    if (tg == null) return false;
    @ITM@ it = @PKG@.Gear.item(id);
    if (Math.abs(tg[0] - nativeHealth(it)) >= 1.0E-4f) return false;
    return Math.abs(tg[1] - assetRes(it, "Physical")) < 1.0E-6f && Math.abs(tg[1] - assetRes(it, "Projectile")) < 1.0E-6f;
  } catch (Throwable t) { return false; }
}""")
# /gear read (admin): how the held item's base stats come out
M(gbase, "public static String f3(double x) { return String.valueOf(Math.round(x * 1000.0) / 1000.0); }")
M(gbase, r"""
public static String describe(String id, @BD@ d) {
  try {
    int lv = @PKG@.GearLevel.level(id, d);
    int st = @PKG@.GearLevel.band(id)[0];
    int sl = @PKG@.GearData.slotOf(id);
    if (sl == 0 || sl == 1) {
      if (!on()) return "base stats: weapon damage vanilla (" + (@PKG@.GearCfg.PART_BASE ? "base.mode off" : "part.base off") + ")";
      String b = baseOf(id);
      float[] r = range(id, d);
      return "base stats: Lv " + lv + " - K " + f3(kOf(id, false)) + " (family base " + b + ", band start " + @PKG@.GearLevel.band(b)[0] + ") x F(" + lv + ") " + f3(curveF(lv)) + " x material " + f3(bonus(st)) + " = x" + f3(mult(id, d, false)) + " per hit" + (r == null ? "" : " (" + rangeText(r) + ")") + "; spell orbs x" + f3(mult(id, d, true));
    }
    if (sl == 2) {
      float[] tg = armorTarget(id, d);
      @ITM@ it = @PKG@.Gear.item(id);
      if (tg == null) return "base stats: armor values vanilla (" + (!armorOn() ? "base.armorOn / part.base off" : "no Head / Chest / Legs / Hands slot") + ")";
      return "base stats: Lv " + lv + " - Health " + @PKG@.Gear.fnum((double) tg[0]) + " (the item's own " + @PKG@.Gear.fnum((double) nativeHealth(it)) + "), resistance " + pct((double) tg[1]) + " physical / " + pct((double) tg[1]) + " projectile (the item's own " + pct((double) assetRes(it, "Physical")) + " / " + pct((double) assetRes(it, "Projectile")) + ")";
    }
    return "base stats: none for this kind of item";
  } catch (Throwable t) { return "base stats: unreadable (" + t + ")"; }
}""")

# ================================================================= GearView (spec 6): tooltip, plain lines, sigs
M(gvw, r"""
public static String slotWord(String id) {
  int s = @PKG@.GearData.slotOf(id);
  if (s == 2) return "ARMOR";
  if (s == 3) return "TOOL";
  if (s == 4) return "EQUIPMENT";
  return "WEAPON";
}""")
M(gvw, r"""
public static String suffix(int i) {
  if (@PKG@.GearDefs.S_LIVE[i] == 0) return " (coming later)";
  if (i == @PKG@.GearDefs.I_CHG && !@PKG@.GearCfg.CHG_ON) return " (off on this server)";
  String s = @PKG@.GearDefs.S_SUF[i];
  if (s.equals("spells")) return " (spell attacks only)";
  if (s.equals("elem")) return " (each element)";
  if (s.equals("steal")) return " (every " + @PKG@.GearCfg.STEAL_S + "s)";
  if (s.equals("regen")) return " (every " + @PKG@.Gear.fnum((double) @PKG@.GearCfg.REGEN_MS / 1000.0) + "s)";
  if (s.equals("hprp")) return " (boosts Raw Health Regen)";
  return "";
}""")
M(gvw, r"""
public static String valText(String key, int v) {
  int i = @PKG@.GearDefs.sIndex(key);
  return (v >= 0 ? "+" : "") + v + (i >= 0 ? @PKG@.GearDefs.S_UNIT[i] : "");
}""")
# one modifier line ("Strength: +12", "Magical Power: +8 (spells)"); unknown stat keys are kept and shown by name (rule 3)
M(gvw, r"""
public static String modLine(String key, int v) {
  int i = @PKG@.GearDefs.sIndex(key);
  if (i < 0) return key + ": " + (v >= 0 ? "+" : "") + v;
  return @PKG@.GearDefs.S_LABEL[i] + ": " + valText(key, v) + suffix(i);
}""")
M(gvw, r"""
public static boolean later(String key) {
  int i = @PKG@.GearDefs.sIndex(key);
  return i >= 0 && @PKG@.GearDefs.S_LIVE[i] == 0;
}""")
# 0.1.2: a modifier line shown grey = coming later, or Charged Attack Damage while charged.on is off (it does nothing then)
M(gvw, r"""
public static boolean dim(String key) {
  if (later(key)) return true;
  return "chg".equals(key) && !@PKG@.GearCfg.CHG_ON;
}""")
# weapon base damage from the engine's own damage data (SkyyRolls 0.1.4 rangeOf / damageText, ItemWeapon basic breakdown)
M(gvw, r"""
public static float[] rangeOf(@DBD@ b) {
  if (b == null) return null;
  java.util.List es = b.entries();
  if (es == null || es.isEmpty()) return null;
  float lo = Float.MAX_VALUE;
  float hi = 0f;
  for (int i = 0; i < es.size(); i++) {
    Object o = es.get(i);
    if (!(o instanceof @DBE@)) continue;
    @DBE@ e = (@DBE@) o;
    float a = e.min();
    float z = e.max();
    if (z <= 0f) continue;
    if (a < 0f) a = 0f;
    if (a < lo) lo = a;
    if (z > hi) hi = z;
  }
  if (hi <= 0f) return null;
  if (lo == Float.MAX_VALUE || lo > hi) lo = hi;
  return new float[] { lo, hi };
}""")
M(gvw, r"""
public static String damageText(String id) {
  try {
    @ITM@ item = @PKG@.Gear.item(id);
    if (item == null) return null;
    @IWP@ w = item.getWeapon();
    if (w == null) return null;
    float[] r = rangeOf(w.getBasicDamageBreakdown());
    if (r == null) r = rangeOf(w.getUltimateDamageBreakdown());
    if (r == null) return null;
    String a = @PKG@.Gear.fnum((double) r[0]);
    String z = @PKG@.Gear.fnum((double) r[1]);
    return a.equals(z) ? a : a + "-" + z;
  } catch (Throwable t) { return null; }
}""")
M(gvw, r"""
public static String statName(int idx) {
  try {
    Object o = @ESTT@.getAssetMap().getAsset(idx);
    if (o instanceof @ESTT@) { String s = ((@ESTT@) o).getId(); if (s != null) return s; }
  } catch (Throwable t) { }
  return "Stat " + idx;
}""")
# armor base lines (native): "Health: 17", "Armor: 9% physical, 9% projectile" (spec 4.2 base lines, 6.1)
M(gvw, r"""
public static void armorLines(String id, java.util.ArrayList out) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return;
    @IAR@ a = it.getArmor();
    if (a == null) return;
    java.util.ArrayList st = new java.util.ArrayList();
    Object sm = a.getStatModifiers();
    if (sm instanceof java.util.Map) {
      java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
      while (e.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(k instanceof Number) || !(v instanceof Object[])) continue;
        Object[] xs = (Object[]) v;
        double add = 0.0;
        double mul = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String nm = statName(((Number) k).intValue());
        if (add != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(add));
        if (mul != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(mul * 100.0) + "%");
      }
    }
    java.util.Collections.sort(st);
    for (int i = 0; i < st.size(); i++) out.add(st.get(i));
    Object dr = a.getDamageResistanceValues();
    if (dr instanceof java.util.Map && !((java.util.Map) dr).isEmpty()) {
      java.util.ArrayList parts = new java.util.ArrayList();
      java.util.Iterator e2 = ((java.util.Map) dr).entrySet().iterator();
      while (e2.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e2.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(v instanceof Object[])) continue;
        String cause = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
        if (cause == null) cause = "?";
        Object[] xs = (Object[]) v;
        double add = 0.0;
        double mul = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String low = cause.toLowerCase();
        if (mul != 0.0) parts.add(@PKG@.Gear.fnum(mul * 100.0) + "% " + low);
        if (add != 0.0) parts.add(@PKG@.Gear.fnum(add) + " " + low);
      }
      java.util.Collections.sort(parts);
      if (!parts.isEmpty()) {
        StringBuilder sb = new StringBuilder("Armor: ");
        for (int i = 0; i < parts.size(); i++) { if (i > 0) sb.append(", "); sb.append((String) parts.get(i)); }
        out.add(sb.toString());
      }
    }
  } catch (Throwable t) { }
}""")
# the gate line for an owner: Object[] { String text, String colour, Boolean inactive, String label }. 0.2 (spec 7): "Lv N - Requires
# <Skill> N" - the item's level = its use requirement; the vanilla "met" green when met (0.1.3's design review 3; grey means "coming later"
# in these tooltips), the vanilla red + "(you: M)" when too low; gathering gear "... (coming later)" in grey
M(gvw, r"""
public static Object[] gateLine(java.util.UUID owner, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  String lv = "Lv " + need;
  if (!@PKG@.GearDefs.enforcedKind(kind)) {
    if (gate.length() == 0) return new Object[] { "", null, Boolean.FALSE, "" };
    return new Object[] { lv + " - Requires " + gate + " " + need + " (coming later)", @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
  }
  Object[] c = @PKG@.GearGate.check(owner, id, d, need);
  String label = (String) c[1];
  boolean ok = ((Boolean) c[0]).booleanValue();
  int have = ((Integer) c[3]).intValue();
  int st = ((Integer) c[5]).intValue();
  String req = label.length() > 0 ? lv + " - Requires " + label + " " + need : lv;
  if (st == 4 || st == 5 || st == 3) return new Object[] { req, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, label };
  if (st == 2) {
    if (ok) return new Object[] { lv, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, "Level" };
    return new Object[] { lv + " - skills unavailable", @PKG@.GearDefs.C_BAD, Boolean.TRUE, "Level" };
  }
  if (st == 1) {
    if (ok) return new Object[] { req, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
    return new Object[] { req + " (pick a class)", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
  }
  if (ok) return new Object[] { req, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
  return new Object[] { req + " (you: " + (have < 0 ? 0 : have) + ")", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
}""")
M(gvw, r"""
public static void add(java.util.ArrayList txt, java.util.ArrayList col, String t, String c) {
  txt.add(t == null ? "" : t);
  col.add(c);
}""")
# 0.2.1 (stage 3): the item's vanilla armor lines that the level does NOT change - every stat modifier but Health ("Mana: 10") and every
# resistance but Physical / Projectile ("Fire resistance: 10%", ResistanceModifier: Percent = a fraction, Flat = a number)
M(gvw, r"""
public static void otherArmorLines(String id, java.util.ArrayList out) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    @IAR@ a = it == null ? null : it.getArmor();
    if (a == null) return;
    java.util.ArrayList st = new java.util.ArrayList();
    int hi = @DST@.getHealth();
    Object sm = a.getStatModifiers();
    if (sm instanceof java.util.Map) {
      java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
      while (e.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(k instanceof Number) || !(v instanceof Object[]) || ((Number) k).intValue() == hi) continue;
        Object[] xs = (Object[]) v;
        double add = 0.0;
        double mul = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String nm = statName(((Number) k).intValue());
        if (add != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(add));
        if (mul != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(mul * 100.0) + "%");
      }
    }
    Object dr = a.getDamageResistanceValues();
    if (dr instanceof java.util.Map) {
      java.util.Iterator e2 = ((java.util.Map) dr).entrySet().iterator();
      while (e2.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e2.next();
        Object k = en.getKey();
        Object v = en.getValue();
        String cause = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
        if (cause == null || "Physical".equals(cause) || "Projectile".equals(cause) || !(v instanceof Object[])) continue;
        Object[] xs = (Object[]) v;
        double fl = 0.0;
        double pc = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @RMOD@)) continue;
          @RMOD@ r = (@RMOD@) xs[i];
          if (r.getCalculationType() == @RCT@.FLAT) fl = fl + (double) r.getAmount();
          else pc = pc + (double) r.getAmount();
        }
        if (pc != 0.0) st.add(cause + " resistance: " + @PKG@.GearBase.pct(pc));
        if (fl != 0.0) st.add(cause + " resistance: " + @PKG@.Gear.fnum(fl));
      }
    }
    java.util.Collections.sort(st);
    for (int i = 0; i < st.size(); i++) out.add(st.get(i));
  } catch (Throwable t) { }
}""")
# 0.2.1: "Health at Lv 6: +16" + "Resistance at Lv 6: 7.9% (physical, projectile)" + the other vanilla lines; false = no levelled armor
# stats for this item (part.base / base.armorOn off, or no Head / Chest / Legs / Hands slot): the caller shows the 0.2 lines. Review of
# 0.2.1 finding 2: also false when the levelled numbers ARE the asset's (GearBase.armorAsVanilla: a Lv 1 copper piece) - 0.2's lines, no hint
M(gvw, r"""
public static boolean levelArmorLines(String id, @BD@ d, java.util.ArrayList out) {
  float[] tg = @PKG@.GearBase.armorTarget(id, d);
  if (tg == null || @PKG@.GearBase.armorAsVanilla(id, d)) return false;
  int lv = @PKG@.GearLevel.level(id, d);
  out.add("Health at Lv " + lv + ": +" + @PKG@.GearBase.rint((double) tg[0]));
  out.add("Resistance at Lv " + lv + ": " + @PKG@.GearBase.pct((double) tg[1]) + " (physical, projectile)");
  otherArmorLines(id, out);
  return true;
}""")
# base value lines + modifier lines of an identified document (the tooltip body, the Reforge page's line columns)
M(gvw, r"""
public static void statLines(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int slot = @PKG@.GearData.slotOf(id);
  @BA@ ms = @PKG@.GearData.mods(d);
  boolean hasDmg = false;
  int dmg = 0;
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    if ("dmg".equals(@PKG@.GearData.str(m.asDocument(), "s", ""))) { hasDmg = true; dmg = @PKG@.GearData.num(m.asDocument(), "v", 0); }
  }
  boolean dmgShown = false;
  if (slot == 0 || slot == 1) {
    // 0.2.1 (stage 2): the LEVELLED range ("Damage at Lv 6: 10-14"); the item tooltip adds the grey hint under it (hints, below).
    // Review of 0.2.1 finding 2: a weapon whose levelled hits equal its vanilla ones (m = 1: the Lv 1 kit items) keeps 0.2's plain
    // "Damage: 6-8" line - no hint (the vanilla box below shows the same numbers)
    float[] lr = null;
    boolean on = @PKG@.GearBase.on();
    if (on && !@PKG@.GearBase.asVanilla(id, d, false)) lr = @PKG@.GearBase.range(id, d);
    if (lr != null) {
      add(txt, col, "Damage at Lv " + @PKG@.GearLevel.level(id, d) + ": " + @PKG@.GearBase.rangeText(lr) + (hasDmg ? " (" + valText("dmg", dmg) + ")" : ""), null);
      dmgShown = hasDmg;
    } else {
      String b = damageText(id);
      if (b != null) {
        add(txt, col, "Damage: " + b + (hasDmg ? " (" + valText("dmg", dmg) + ")" : ""), null);
        dmgShown = hasDmg;
      }
    }
    // review of 0.2.1 finding 3: a spell weapon's cast - the orb a Priest / Mage mostly hits with (the vanilla box shows only the swing):
    // "Spell at Lv 6: 43" (the orb 25 x F(6)), "Spell: 25" when the level changes nothing; part.base / base.mode off = the 0.2 lines
    if (slot == 1 && on) {
      float[] sr = @PKG@.GearBase.spellRange(id, d);
      if (sr != null) add(txt, col, (@PKG@.GearBase.asVanilla(id, d, true) ? "Spell: " : "Spell at Lv " + @PKG@.GearLevel.level(id, d) + ": ") + @PKG@.GearBase.rangeText(sr), null);
    }
  } else if (slot == 2) {
    // 0.2.1 (stage 3): the levelled Health + resistance of this piece, then the item's other vanilla lines
    java.util.ArrayList al = new java.util.ArrayList();
    boolean lv = levelArmorLines(id, d, al);
    if (!lv) armorLines(id, al);
    for (int i = 0; i < al.size(); i++) add(txt, col, (String) al.get(i), null);
  }
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    String k = @PKG@.GearData.str(m.asDocument(), "s", "?");
    if (k.equals("dmg") && dmgShown) continue;
    int v = @PKG@.GearData.num(m.asDocument(), "v", 0);
    add(txt, col, modLine(k, v), (dim(k) || slot == 3) ? @PKG@.GearDefs.C_GRAY : null);
  }
}""")
# 0.2.1 (spec R2, the vanilla-block decision): the grey hint right under our levelled damage / resistance line - ONLY in the item tooltip
# itself (GearView.apply), where the client draws its own vanilla Damage Data / Health / Resistance box from the item asset under our text;
# never in /gear, gear:fn:describe or the Reforge page columns (no vanilla box there)
# review of 0.2.1 finding 3: when the spell line follows the damage line, the hint goes under the spell line (our levelled lines first,
# then the note on the vanilla box)
M(gvw, r"""
public static void hints(java.util.ArrayList txt, java.util.ArrayList col) {
  for (int i = txt.size() - 1; i >= 0; i--) {
    String t = (String) txt.get(i);
    if (t == null) continue;
    if (t.startsWith("Damage at Lv ")) {
      int at = i + 1;
      if (at < txt.size()) {
        Object n = txt.get(at);
        if (n instanceof String && (((String) n).startsWith("Spell at Lv ") || ((String) n).startsWith("Spell: "))) at = at + 1;
      }
      txt.add(at, @PKG@.GearBase.HINT_W);
      col.add(at, @PKG@.GearDefs.C_GRAY);
    }
    else if (t.startsWith("Resistance at Lv ")) { txt.add(i + 1, @PKG@.GearBase.HINT_A); col.add(i + 1, @PKG@.GearDefs.C_GRAY); }
  }
}""")
# every tooltip line below the name (spec 6.1 identified, 6.2 unidentified), for the owner (null = neutral text). 0.2 (spec 7): the
# level line "Lv N - Requires <Skill> N" comes first, right under the name (+ the armor "Gives no stats until ..." line under it)
M(gvw, r"""
public static void lines(String id, @BD@ d, java.util.UUID owner, java.util.ArrayList txt, java.util.ArrayList col) {
  int r = @PKG@.GearData.rarity(d);
  int need = @PKG@.GearLevel.level(id, d);
  int slot = @PKG@.GearData.slotOf(id);
  Object[] g = gateLine(owner, id, d, need);
  String gt = (String) g[0];
  String hex = @PKG@.GearDefs.R_HEX[r];
  if (gt.length() > 0) add(txt, col, gt, (String) g[1]);
  if (!@PKG@.GearData.identified(d)) {
    add(txt, col, "Rarity: " + @PKG@.GearDefs.R_NAME[r], hex);
    add(txt, col, "Unidentified - its modifiers appear when you identify it.", @PKG@.GearDefs.C_GRAY);
    add(txt, col, slot == 2 ? "Gives no stats until identified." : "Cannot be used until identified.", @PKG@.GearDefs.C_BAD);
    add(txt, col, "Identify: " + @PKG@.GearCfg.idWhere() + " - " + @PKG@.Gear.fmt(@PKG@.GearCfg.costIdentify(r, need)) + " coins", @PKG@.GearDefs.C_GOLD);
    return;
  }
  if (slot == 2 && ((Boolean) g[2]).booleanValue()) add(txt, col, "Gives no stats until " + g[3] + " " + need, @PKG@.GearDefs.C_BAD);
  statLines(id, d, txt, col);
  add(txt, col, "", null);
  add(txt, col, @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + slotWord(id), hex);
  String rf = @PKG@.GearData.str(d, "rf", null);
  int rfn = @PKG@.GearData.num(d, "rfN", 0);
  if (rf != null && rf.length() > 0) add(txt, col, "Reforge: " + rf + (rfn > 0 ? " (" + rfn + "x)" : ""), null);
  if (slot == 3 && gt.indexOf("coming later") < 0) add(txt, col, "(coming later: gathering gear)", @PKG@.GearDefs.C_GRAY);
}""")
M(gvw, r"""
public static String nameText(String id, @BD@ d) {
  String base = @PKG@.Gear.itemName(id);
  if (!@PKG@.GearData.identified(d)) return "Unidentified " + base;
  String rf = @PKG@.GearData.str(d, "rf", null);
  return (rf != null && rf.length() > 0 ? rf + " " : "") + base;
}""")
# Name: one raw coloured line; if the en-US name is missing or has {params} the item's translation Message is inserted (SkyyRolls)
M(gvw, r"""
public static @MSG@ nameMsg(String id, @BD@ d, String col) {
  String base = null;
  @ITM@ it = @PKG@.Gear.item(id);
  try { if (it != null) base = @PKG@.Gear.tr(it.getTranslationKey()); } catch (Throwable t) { base = null; }
  if (base != null && base.indexOf(123) < 0) return @MSG@.raw(nameText(id, d).replace(@PKG@.Gear.itemName(id), base)).color(col);
  String pre = "";
  if (!@PKG@.GearData.identified(d)) pre = "Unidentified ";
  else { String rf = @PKG@.GearData.str(d, "rf", null); if (rf != null && rf.length() > 0) pre = rf + " "; }
  @MSG@ m = @MSG@.empty().color(col);
  if (pre.length() > 0) m.insert(@MSG@.raw(pre).color(col));
  try { m.insert(it.getTranslationMessage().color(col)); } catch (Throwable t) { m.insert(@MSG@.raw(@PKG@.Gear.pretty(id)).color(col)); }
  return m;
}""")
M(gvw, r"""
public static boolean hasDesc(String id) {
  try { @ITM@ it = @PKG@.Gear.item(id); return it != null && @PKG@.Gear.tr(it.getDescriptionTranslationKey()) != null; } catch (Throwable t) { return false; }
}""")
M(gvw, r"""
public static @MSG@ descMsg(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  @MSG@ m = @MSG@.empty();
  if (@PKG@.GearData.identified(d) && hasDesc(id)) {
    try {
      m.insert(@PKG@.Gear.item(id).getDescriptionTranslationMessage().color(@PKG@.GearDefs.C_GRAY));
      m.insert(@MSG@.raw("\n\n"));
    } catch (Throwable t) { }
  }
  for (int i = 0; i < txt.size(); i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    String t = (String) txt.get(i);
    if (t.length() == 0) continue;
    String c = (String) col.get(i);
    m.insert(c == null ? @MSG@.raw(t) : @MSG@.raw(t).color(c));
  }
  return m;
}""")
# spec 6.3 sig: item id, stack quality, document JSON, resolved level, every rendered line (base values + the owner lines exactly as
# shown, colour and "(you: N)" included), config epoch - a change the player can see re-renders the item, nothing else does
M(gvw, r"""
public static String sig(String id, int quality, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < txt.size(); i++) sb.append((String) txt.get(i)).append('|').append(String.valueOf(col.get(i))).append('\n');
  return @PKG@.GearDefs.VIEW_V + ":" + id + ":" + @PKG@.GearDefs.qName(quality) + ":" + Integer.toHexString(d.toJson().hashCode()) + ":"
    + Integer.toHexString(sb.toString().hashCode()) + ":" + @PKG@.GearLevel.level(id, d) + ":" + @PKG@.GearCfg.cfgEpoch() + ":" + (hasDesc(id) ? 1 : 0);
}""")
# fingerprint of the stack's CURRENT ItemDisplay through the engine codec (SkyyRolls dispHash); null = none / unreadable
M(gvw, r"""
public static String dispHash(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    Object o = s.getFromMetadataOrNull(@IDM@.KEYED_CODEC);
    if (o == null) return null;
    @BD@ md = s.withMetadata(@IDM@.KEYED_CODEC, o).getMetadata();
    @BV@ v = md == null ? null : md.get(@IDM@.KEY);
    if (v == null || !v.isDocument()) return null;
    return Integer.toHexString(v.asDocument().toJson().hashCode());
  } catch (Throwable t) { return null; }
}""")
M(gvw, r"""
public static boolean ours(@IS@ s, @BD@ view) {
  if (view == null) return false;
  @BV@ h = view.get("disp");
  if (h == null || !h.isString()) return false;
  String now = dispHash(s);
  return now != null && now.equals(h.asString().getValue());
}""")
# review of 0.2 finding 4: is this stack quality index one of today's Skyy_Gear_* rarity qualities (QIDX, resolved by qIndex)
M(gvw, r"""
public static boolean ourQ(int idx) {
  int[] qa = @PKG@.GearDefs.QIDX;
  if (qa == null || idx < 0) return false;
  for (int i = 0; i < qa.length; i++) if (qa[i] >= 0 && qa[i] == idx) return true;
  return false;
}""")
# the text colour of the quality asset at this index ("#rrggbb", the colour vanilla gives an item's name); null = unreadable
M(gvw, r"""
public static String qualHex(int idx) {
  try {
    Object a = @IQ@.getAssetMap().getAsset(idx);
    if (a instanceof @IQ@) return @PKG@.Gear.hex(((@IQ@) a).getTextColor());
  } catch (Throwable t) { }
  return null;
}""")
# the one writer (spec 1.1, 6.4): document + quality + ItemDisplayMetadata + our SkyyGearView marker {v, sig, disp, prev}. Returns
# the SAME object when nothing the player can see would change (callers compare with ==). prev = the display from before SkyyGear.
M(gvw, r"""
public static @IS@ apply(@IS@ s, @BD@ doc, java.util.UUID owner) {
  String id = "?";
  try {
    if (s == null || s.isEmpty() || doc == null) return s;
    id = s.getItemId();
    @BD@ md = s.getMetadata();
    int r = @PKG@.GearData.rarity(doc);
    int q = @PKG@.GearDefs.qIndex(r);
    // ItemStack.getQualityIndex() answers the item's own quality index while the stack has none of its own (VERIFIED bytecode)
    int curQ = @PKG@.Gear.quality(s);
    int ownQ = @PKG@.Gear.ownQuality(s);
    // review of 0.2 finding 4: a PLAIN gathering tool document (0.2 tools: Normal, no modifiers - no tool stat rolls yet, so its rarity
    // is no real rarity) keeps the item's OWN quality frame and name colour (a Mithril pickaxe stays purple, not Normal white); a stack
    // quality SkyyGear wrote (today's or the last start's Skyy_Gear_* index, or one that resolves to nothing) goes back to the item's
    // own. A tool that is gear (gear.include) keeps 0.1.3's rarity quality.
    boolean plainTool = @PKG@.GearData.isTool(id) && !@PKG@.GearData.isGear(id);
    // engine review 4: a stored index that resolves to no quality asset (or, with our assets missing, one that was a Skyy_Gear_*
    // index at the last start) goes back to the item's own quality; a moved index is rewritten to the rarity's index of today
    int wantQ = q;
    if (plainTool) wantQ = (curQ != ownQ && (!@PKG@.GearDefs.validQ(curQ) || @PKG@.GearQual.wasOurs(curQ) || ourQ(curQ))) ? Integer.MIN_VALUE : curQ;
    else if (q < 0) wantQ = (curQ != ownQ && (!@PKG@.GearDefs.validQ(curQ) || @PKG@.GearQual.wasOurs(curQ))) ? Integer.MIN_VALUE : curQ;
    int effQ = wantQ == Integer.MIN_VALUE ? ownQ : wantQ;
    java.util.ArrayList txt = new java.util.ArrayList();
    java.util.ArrayList col = new java.util.ArrayList();
    lines(id, doc, owner, txt, col);
    hints(txt, col);
    String sg = sig(id, effQ, doc, txt, col);
    @BV@ cur = md == null ? null : md.get(@PKG@.GearDefs.DOC_KEY);
    boolean sameDoc = cur != null && cur.isDocument() && cur.asDocument().toJson().equals(doc.toJson());
    @BV@ view = md == null ? null : md.get(@PKG@.GearDefs.VIEW_KEY);
    if (sameDoc && effQ == curQ && view != null && view.isDocument() && md.containsKey(@IDM@.KEY)) {
      @BV@ g = view.asDocument().get("sig");
      if (g != null && g.isString() && g.asString().getValue().equals(sg) && ours(s, view.asDocument())) return s;
    }
    @BV@ keep = null;
    @BV@ curD = md == null ? null : md.get(@IDM@.KEY);
    if (view != null && view.isDocument() && ours(s, view.asDocument())) {
      @BV@ p = view.asDocument().get("prev");
      if (p != null && !p.isNull()) keep = p;
    } else if (curD != null && !curD.isNull()) keep = curD;
    @IS@ out = s;
    if (!sameDoc) out = out.withMetadata(@PKG@.GearDefs.DOC_KEY, (@BV@) doc);
    if (effQ != curQ) out = out.withQuality(wantQ);
    String hex = @PKG@.GearDefs.R_HEX[r];
    if (plainTool) {
      String oh = qualHex(effQ);
      if (oh != null) hex = oh;
    }
    out = out.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(nameMsg(id, doc, hex), descMsg(id, doc, txt, col)));
    @BD@ nv = new @BD@();
    nv.append("v", new org.bson.BsonInt32(@PKG@.GearDefs.VIEW_V));
    nv.append("sig", new org.bson.BsonString(sg));
    String h = dispHash(out);
    if (h != null) nv.append("disp", new org.bson.BsonString(h));
    if (keep != null) nv.append("prev", keep);
    return out.withMetadata(@PKG@.GearDefs.VIEW_KEY, (@BV@) nv);
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("apply:" + id, "could not write the gear tooltip for " + id + ": " + t);
    return s;
  }
}""")
# plain lines (bridge gear:fn:describe, /gear, the page): name line first, neutral owner text when owner is null
M(gvw, r"""
public static String[] plain(String id, @BD@ d, java.util.UUID owner) {
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  txt.add(nameText(id, d));
  col.add(null);
  lines(id, d, owner, txt, col);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < txt.size(); i++) { String t = (String) txt.get(i); if (t.length() > 0) out.add(t); }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
# one line of the modifiers ("Strength +12 - Crit Chance +5%"); "" when none
M(gvw, r"""
public static String modSummary(@BD@ d) {
  @BA@ ms = @PKG@.GearData.mods(d);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    String k = @PKG@.GearData.str(m.asDocument(), "s", "?");
    int v = @PKG@.GearData.num(m.asDocument(), "v", 0);
    int si = @PKG@.GearDefs.sIndex(k);
    if (sb.length() > 0) sb.append(" - ");
    sb.append(si >= 0 ? @PKG@.GearDefs.S_LABEL[si] : k).append(' ').append(valText(k, v));
  }
  return sb.toString();
}""")
# spec 7.1 gear:fn:rollsLine: "Rare - Lv 20 - Strength +12 - Crit Chance +5%"; "" for a Normal with no modifiers
M(gvw, r"""
public static String rollsLine(String id, @BD@ d) {
  int r = @PKG@.GearData.rarity(d);
  int lv = @PKG@.GearLevel.level(id, d);
  if (!@PKG@.GearData.identified(d)) return "Unidentified (" + @PKG@.GearDefs.R_NAME[r] + ", Lv " + lv + ")";
  String ms = modSummary(d);
  if (r == 0 && ms.length() == 0) return "";
  return @PKG@.GearDefs.R_NAME[r] + " - Lv " + lv + (ms.length() > 0 ? " - " + ms : "");
}""")
# spec 7.1 gear:fn:sig: item id + stack quality + rarity + identify state + modifiers (review E4) + 0.2 the item's level (spec 8: the AH
# shows "rolls differ" for a Lv 4 and a Lv 9 wand; it calls the sig live on both sides)
M(gvw, r"""
public static String bridgeSig(String id, int quality, @BD@ d) {
  String s = id + "|" + quality + "|" + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + "|" + @PKG@.GearData.identified(d) + "|" + @PKG@.GearData.mods(d).toString() + "|" + @PKG@.GearLevel.level(id, d);
  return Integer.toHexString(s.hashCode()) + Integer.toHexString(s.length());
}""")

# ================================================================= GearData (2/2): writes (every rewrite goes through GearView.apply)
# drop the SkyyRolls keys of a stack being migrated; when the ItemDisplay on it is still SkyyRolls' tooltip, the display from before
# SkyyRolls comes back first, so GearView.apply stores THAT as prev (spec 1.6: view prev = the old SkyyRollsView.prev)
M(gdt, r"""
public static @IS@ dropRolls(@IS@ s) {
  @BD@ md = s.getMetadata();
  if (md == null) return s;
  @BD@ c = (@BD@) md.clone();
  c.remove(@PKG@.GearDefs.ROLLS_KEY);
  @BV@ rv = (@BV@) c.remove(@PKG@.GearDefs.ROLLS_VIEW);
  if (rv != null && rv.isDocument()) {
    @BV@ h = rv.asDocument().get("disp");
    String now = @PKG@.GearView.dispHash(s);
    if (h != null && h.isString() && now != null && now.equals(h.asString().getValue())) {
      @BV@ p = rv.asDocument().get("prev");
      if (p != null && !p.isNull()) c.put(@IDM@.KEY, p);
      else c.remove(@IDM@.KEY);
    }
  }
  if (c.isEmpty()) return s.withMetadata((@BD@) null);
  return s.withMetadata(c);
}""")
M(gdt, r"""
public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;
  @IS@ x = s;
  @BD@ md = x.getMetadata();
  if (md != null && md.containsKey(@PKG@.GearDefs.ROLLS_KEY)) x = dropRolls(x);
  return @PKG@.GearView.apply(x, doc, owner);
}""")
# /gear clear: SkyyGear data and our tooltip go, the display from before SkyyGear comes back, the item's own quality returns
M(gdt, r"""
public static @IS@ clear(@IS@ s) {
  @BD@ md = s.getMetadata();
  @IS@ out = s;
  if (md != null) {
    @BD@ c = (@BD@) md.clone();
    c.remove(@PKG@.GearDefs.DOC_KEY);
    @BV@ view = (@BV@) c.remove(@PKG@.GearDefs.VIEW_KEY);
    if (view != null && view.isDocument() && @PKG@.GearView.ours(s, view.asDocument())) {
      @BV@ prev = view.asDocument().get("prev");
      if (prev != null && !prev.isNull()) c.put(@IDM@.KEY, prev);
      else c.remove(@IDM@.KEY);
    }
    out = c.isEmpty() ? s.withMetadata((@BD@) null) : s.withMetadata(c);
  }
  return out.withQuality(Integer.MIN_VALUE);
}""")

# ================================================================= GearStats: the player's active totals (PART B applies them)
# T = the main-hand weapon's modifiers + every active armor piece's (weapon-only stats only from the weapon; spec 4.3). Active =
# identified and the gate passes (3.4 / 3.5). World thread (reads the inventory).
M(gst, r"""
public static @IS@ hand(@INV@ inv) {
  try {
    if (inv.usingToolsItem()) {
      @IC@ t = inv.getTools();
      int ts = inv.getActiveToolsSlot();
      return t == null || ts < 0 || ts >= t.getCapacity() ? null : t.getItemStack((short) ts);
    }
    @IC@ h = inv.getHotbar();
    int hs = inv.getActiveHotbarSlot();
    return h == null || hs < 0 || hs >= h.getCapacity() ? null : h.getItemStack((short) hs);
  } catch (Throwable t) { return null; }
}""")
M(gst, r"""
public static boolean active(java.util.UUID u, String id, @BD@ d) {
  if (d == null || !@PKG@.GearData.identified(d)) return false;
  Object[] c = @PKG@.GearGate.check(u, id, d, @PKG@.GearLevel.level(id, d));
  return ((Boolean) c[0]).booleanValue();
}""")
# follow-up review 9: every stat total is summed in long and saturated at +-1,000,000,000 (a hand-made document or a gear:extra text
# can never wrap an int around)
M(gst, r"""
public static int sat(long v) {
  if (v > 1000000000L) return 1000000000;
  if (v < -1000000000L) return -1000000000;
  return (int) v;
}""")
M(gst, r"""
public static void addMods(int[] t, @BD@ d, boolean armor) {
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m.asDocument(), "s", ""));
    if (si < 0) continue;
    if (armor && @PKG@.GearDefs.S_SLOT[si].indexOf('a') < 0) continue;
    t[si] = sat((long) t[si] + (long) @PKG@.GearData.num(m.asDocument(), "v", 0));
  }
}""")
# design review 2: gear:extra:<uuid> = "str:40,cc:10,..." another mod publishes (stat keys of section 4.2, whole numbers, may be
# negative; unknown keys and bad parts are skipped). Parsed once per distinct text. Follow-up review 9: each part and each stat's sum
# stays within +-1,000,000 (long math, no wrap-around however many parts the text has).
F(gst, "public static final java.util.concurrent.ConcurrentHashMap XCACHE = new java.util.concurrent.ConcurrentHashMap();")
M(gst, r"""
public static int[] parseExtra(String s) {
  int[] t = new int[@PKG@.GearDefs.NS];
  if (s == null || s.length() == 0) return t;
  long[] acc = new long[t.length];
  String[] ps = s.split(",");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    int c = p.indexOf(':');
    if (c <= 0) continue;
    int si = @PKG@.GearDefs.sIndex(p.substring(0, c).trim());
    if (si < 0) continue;
    try {
      double v = Double.parseDouble(p.substring(c + 1).trim());
      if (Double.isNaN(v) || Double.isInfinite(v)) continue;
      if (v > 1000000.0) v = 1000000.0;
      if (v < -1000000.0) v = -1000000.0;
      acc[si] = acc[si] + (long) Math.floor(v);
      if (acc[si] > 1000000L) acc[si] = 1000000L;
      if (acc[si] < -1000000L) acc[si] = -1000000L;
    } catch (Throwable x) { }
  }
  for (int i = 0; i < t.length; i++) t[i] = (int) acc[i];
  return t;
}""")
M(gst, r"""
public static int[] extra(java.util.UUID u) {
  Object o = u == null ? null : @PKG@.Gear.bget("gear:extra:" + u);
  if (!(o instanceof String) || ((String) o).length() == 0) return null;
  String s = (String) o;
  int[] t = (int[]) XCACHE.get(s);
  if (t == null) {
    t = parseExtra(s);
    if (XCACHE.size() > 512) XCACHE.clear();
    XCACHE.put(s, t);
  }
  return t;
}""")
# design review 2: THE totals (spec 4.3 T): the weapon's modifiers (weapon-only stats only from it) + every ACTIVE armor piece's
# (+ gear:extra when withExtra). ok[0] = false when the weapon slot holds something that is neither gear nor empty (a tool, a
# block, an unusable gear weapon): offence stats only apply to a gear weapon or bare hands (spec 4.3). weapon == null = armor only.
M(gst, r"""
public static int[] totals(java.util.UUID u, @IS@ weapon, @IC@ armor, boolean[] ok, boolean withExtra) {
  int[] t = new int[@PKG@.GearDefs.NS];
  boolean good = true;
  if (weapon != null && !weapon.isEmpty()) {
    String id = weapon.getItemId();
    int sl = @PKG@.GearData.slotOf(id);
    if (sl == 0 || sl == 1) {
      @BD@ d = @PKG@.GearData.effective(id, weapon.getMetadata());
      if (active(u, id, d)) addMods(t, d, false);
      else good = false;
    } else good = false;
  }
  if (armor != null) {
    for (int i = 0; i < armor.getCapacity(); i++) {
      @IS@ s = armor.getItemStack((short) i);
      if (s == null || s.isEmpty() || @PKG@.GearData.slotOf(s.getItemId()) != 2) continue;
      @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
      if (active(u, s.getItemId(), d)) addMods(t, d, true);
    }
  }
  if (withExtra) {
    int[] x = extra(u);
    if (x != null) for (int i = 0; i < t.length && i < x.length; i++) t[i] = sat((long) t[i] + (long) x[i]);
  }
  if (ok != null && ok.length > 0) ok[0] = good;
  return t;
}""")
M(gst, r"""
public static int[] totalsInv(java.util.UUID u, @INV@ inv, boolean withExtra) {
  if (inv == null) return totals(u, null, null, null, withExtra);
  return totals(u, hand(inv), inv.getArmor(), null, withExtra);
}""")
M(gst, r"""
public static String statsString(int[] t) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length && i < @PKG@.GearDefs.NS; i++) {
    if (t[i] == 0) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.GearDefs.S_KEY[i]).append(':').append(t[i]);
  }
  return sb.toString();
}""")

# ================================================================= GearNotice: players/<pkey>.properties noticeShown (spec 8.2)
gnt.addInterface(pool.get("java.lang.Runnable"))
F(gnt, "public static final java.util.concurrent.ConcurrentHashMap SHOWN = new java.util.concurrent.ConcurrentHashMap();")
F(gnt, "public String key;")
C(gnt, "public GearNotice(String key) { this.key = key; }")
M(gnt, r"""
public static java.nio.file.Path file(String pkey) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pkey == null || pkey.length() == 0) return null;
  return d.resolve("players").resolve(pkey.replace('/', '_').replace('\\', '_').replace(':', '_') + ".properties");
}""")
M(gnt, r"""
public static boolean shown(String pkey) {
  Object o = SHOWN.get(pkey);
  if (o instanceof Boolean) return ((Boolean) o).booleanValue();
  boolean v = false;
  try {
    java.nio.file.Path f = file(pkey);
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) v = "true".equalsIgnoreCase(@PKG@.GearCfg.read(f).getProperty("noticeShown", "false").trim());
  } catch (Throwable t) { v = false; }
  SHOWN.put(pkey, Boolean.valueOf(v));
  return v;
}""")
M(gnt, r"""
public void run() {
  try {
    java.nio.file.Path f = file(this.key);
    if (f != null) @PKG@.GearCfg.writeAtomic(f, "# SkyyGear player flags\nnoticeShown=true\n", true);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("notice", "could not write a players/ notice file: " + t); }
}""")
M(gnt, r"""
public static void mark(String pkey) {
  if (pkey == null) return;
  SHOWN.put(pkey, Boolean.TRUE);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearNotice(pkey), 200L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")

# ================================================================= GearStamp (spec 1.5): legacy stamp, migration, re-render, pending crafts
F(gsp, "public static final int[] SCAN = new int[] { 0, 3, 5, 4, 1, 2 };")   # hotbar, armor, tools, utility, storage, backpack
F(gsp, 'public static final String[] SEC_NAME = new String[] { "Hotbar", "Inventory", "Backpack", "Armor", "Utility", "Tools" };')
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> ConcurrentHashMap(id -> Long)
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap QUEUED = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> long[]{windowStart, writes, pausedUntil}
M(gsp, r"""
public static @IC@ section(@INV@ inv, int s) {
  if (inv == null) return null;
  if (s == 0) return inv.getHotbar();
  if (s == 1) return inv.getStorage();
  if (s == 2) return inv.getBackpack();
  if (s == 3) return inv.getArmor();
  if (s == 4) return inv.getUtility();
  if (s == 5) return inv.getTools();
  return null;
}""")
M(gsp, r"""
public static @IS@ at(@INV@ inv, int s, int slot) {
  @IC@ c = section(inv, s);
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  return c.getItemStack((short) slot);
}""")
M(gsp, r"""
public static void pendingAdd(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m == null) { m = new java.util.concurrent.ConcurrentHashMap(); Object o = PENDING.putIfAbsent(u, m); if (o != null) m = (java.util.concurrent.ConcurrentHashMap) o; }
  m.put(id, Long.valueOf(System.currentTimeMillis()));
}""")
M(gsp, r"""
public static void pendingClear(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m != null) m.remove(id);
}""")
# true = stacks of this item id are held back from the stamp (a craft of it is pending and younger than PENDING_MAX_MS)
M(gsp, r"""
public static boolean held(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m == null) return false;
  Object t = m.get(id);
  if (!(t instanceof Long)) return false;
  if (System.currentTimeMillis() - ((Long) t).longValue() < @PKG@.GearDefs.PENDING_MAX_MS) return true;
  m.remove(id);
  @PKG@.Gear.info("a pending craft of " + id + " expired unrolled - it is stamped Normal");
  return false;
}""")
# ---- exploit review 2: stackable gear (17 spears MaxStack 5/30, 5 spellbooks 5/25) is rolled per ITEM. Follow-up review 3: a stack
# is split only when an action needs its items apart - crafted gear and loot chests (each item rolls its own document: split) and
# Identify / Reforge (one item is taken off the stack: takeOne). The passive stamp scan never splits: every single it would make
# carries the same document anyway (a copy, the same migration, the same legacy Normal), so the stack stays one stack.
# split: single items, each with its own document, into EMPTY slots of give[] in order (the player path passes storage, backpack -
# never the hotbar; a chest passes itself), only while more than floor empty slots are left in give[] (players: GearDefs.FREE_KEEP
# = 5, so loot and craft output always find room; a chest: 0). Never merged into another stack, never dropped: what does not fit
# stays in the original slot as one stack. Follow-up review 2: ids with MaxStack > GearDefs.STACK_CEIL are never split (one WARN per
# id: the admin adds the prefix to gear.exclude). The item id's total over all[] is counted before and after (engine rule); a
# difference is a WARN + gear.log line. Follow-up review 8: the source is written first and restored when the destination write
# fails or throws.
# mode: 0 = stamp (a copy of the stack's document, its SkyyRolls migration, or a legacy Normal document), 1 = craft roll (craftDoc),
# 2 = chest unidentified (unidDoc chest), 3 = mob unidentified (unidDoc mob). Every split single gets a nonce ("k") so identical
# documents never stack again. Returns the number of singles moved; got collects rolled rarity ids (mode 1).
M(gsp, r"""
public static int countId(@IC@[] all, String id) {
  int n = 0;
  for (int k = 0; all != null && k < all.length; k++) {
    @IC@ c = all[k];
    if (c == null) continue;
    boolean dup = false;
    for (int j = 0; j < k; j++) if (all[j] == c) dup = true;
    if (dup) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s != null && !s.isEmpty() && id.equals(s.getItemId())) n = n + s.getQuantity();
    }
  }
  return n;
}""")
M(gsp, r"""
public static @BD@ splitDoc(String id, @BD@ md, int mode, java.util.UUID u) {
  if (mode == 1) return @PKG@.GearRoll.craftDoc(id, u);
  if (mode == 2) return @PKG@.GearRoll.unidDoc(id, 2, "chest");
  if (mode == 3) return @PKG@.GearRoll.unidDoc(id, 1, "drop");
  int st = @PKG@.GearData.state(md);
  if (st == 1) return @PKG@.GearData.gearDoc(md).clone();
  if (st == 2) return @PKG@.GearData.migrate(id, @PKG@.GearData.rollsDoc(md));
  return @PKG@.GearData.legacy(id);
}""")
# empty slots over the distinct containers of give[], the slot (c, slot) not counted
M(gsp, r"""
public static int empties(@IC@[] give, @IC@ c, int slot) {
  int n = 0;
  for (int k = 0; give != null && k < give.length; k++) {
    @IC@ g = give[k];
    if (g == null) continue;
    boolean dup = false;
    for (int j = 0; j < k; j++) if (give[j] == g) dup = true;
    if (dup) continue;
    for (int i = 0; i < g.getCapacity(); i++) {
      if (g == c && i == slot) continue;
      @IS@ e = g.getItemStack((short) i);
      if (e == null || e.isEmpty()) n++;
    }
  }
  return n;
}""")
# the first empty slot of give[] in order (not (c, slot)): Object[] { container, Integer slot } or null
M(gsp, r"""
public static Object[] firstEmpty(@IC@[] give, @IC@ c, int slot) {
  for (int k = 0; give != null && k < give.length; k++) {
    @IC@ g = give[k];
    if (g == null) continue;
    for (int i = 0; i < g.getCapacity(); i++) {
      if (g == c && i == slot) continue;
      @IS@ e = g.getItemStack((short) i);
      if (e == null || e.isEmpty()) return new Object[] { g, Integer.valueOf(i) };
    }
  }
  return null;
}""")
# write one destination slot; false = refused or threw (follow-up review 8: the caller then restores the source)
M(gsp, r"""
public static boolean putDst(@IC@ dst, int ds, @IS@ s) {
  try {
    Object t = dst.setItemStackForSlot((short) ds, s);
    return !(t instanceof @TXN@ && !((@TXN@) t).succeeded());
  } catch (Throwable x) {
    @PKG@.Gear.warnOnce("splitdst", "a stack split could not write its destination slot (the source was restored): " + x);
    return false;
  }
}""")
M(gsp, r"""
public static void countCheck(@IC@[] all, String id, int before, java.util.UUID u, String what) {
  int after = countId(all, id);
  if (after == before) return;
  @PKG@.Gear.warn("SPLIT COUNT MISMATCH " + id + ": " + before + " before, " + after + " after (" + what + ")");
  @PKG@.GearLog.line("SPLIT-COUNT " + u + " " + id + " before " + before + " after " + after + " " + what);
}""")
M(gsp, r"""
public static int split(@IC@ c, int slot, @IC@[] give, @IC@[] all, java.util.UUID u, int mode, int maxMove, int floor, StringBuilder got) {
  if (c == null || slot < 0 || slot >= c.getCapacity()) return 0;
  @IS@ s0 = c.getItemStack((short) slot);
  if (s0 == null || s0.isEmpty() || s0.getQuantity() <= 1 || !@PKG@.GearData.isGear(s0.getItemId())) return 0;
  String id = s0.getItemId();
  int st0 = @PKG@.GearData.state(s0.getMetadata());
  if (st0 == 3 || st0 == 4) return 0;
  int ms = @PKG@.GearData.maxStack(id);
  if (ms > @PKG@.GearDefs.STACK_CEIL) {
    @PKG@.Gear.warnOnce("splitcap:" + id, id + " stacks to " + ms + " - SkyyGear never splits stacks above " + @PKG@.GearDefs.STACK_CEIL + " (the whole stack keeps one document); if it is not gear, add its prefix to gear.exclude in Server Setup");
    return 0;
  }
  int free = empties(give, c, slot);
  int before = countId(all, id);
  int moved = 0;
  while (moved < maxMove && free > floor) {
    @IS@ cur = c.getItemStack((short) slot);
    if (cur == null || cur.isEmpty() || cur.getQuantity() <= 1 || !id.equals(cur.getItemId())) break;
    Object[] fe = firstEmpty(give, c, slot);
    if (fe == null) break;
    @IC@ dst = (@IC@) fe[0];
    int ds = ((Integer) fe[1]).intValue();
    @BD@ d = @PKG@.GearRoll.nonce(splitDoc(id, cur.getMetadata(), mode, u));
    @IS@ one = @PKG@.GearData.put(cur.withQuantity(1), d, u);
    Object t1 = c.setItemStackForSlot((short) slot, cur.withQuantity(cur.getQuantity() - 1));
    if (t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) break;
    if (!putDst(dst, ds, one)) {
      try { c.setItemStackForSlot((short) slot, cur); } catch (Throwable r) { @PKG@.Gear.warn("SPLIT RESTORE FAILED " + id + ": " + r); }
      break;
    }
    moved++;
    free--;
    if (got != null) got.append(' ').append(@PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]);
  }
  int after = countId(all, id);
  if (after != before) countCheck(all, id, before, u, "split moved " + moved);
  else if (moved > 0) @PKG@.GearLog.line("SPLIT " + u + " " + id + " x" + moved + " mode " + mode);
  return moved;
}""")
# follow-up review 3: Identify / Reforge need ONE item: the rest of the stack (quantity - 1, the same metadata) moves as one stack to
# the first empty slot of give[] (storage, backpack - never the hotbar), only when more than FREE_KEEP empty slots are there; the one
# item stays in its own slot for the action (write safety 1.7: same slot). Object[] { container, Integer slot } of the rest, or null
# (nothing changed). Source first, restored when the destination write fails or throws; counted before and after.
M(gsp, r"""
public static Object[] takeOne(@IC@ c, int slot, @IC@[] give, @IC@[] all, java.util.UUID u) {
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  @IS@ cur = c.getItemStack((short) slot);
  if (cur == null || cur.isEmpty() || cur.getQuantity() <= 1) return null;
  if (empties(give, c, slot) <= @PKG@.GearDefs.FREE_KEEP) return null;
  Object[] fe = firstEmpty(give, c, slot);
  if (fe == null) return null;
  @IC@ dst = (@IC@) fe[0];
  int ds = ((Integer) fe[1]).intValue();
  String id = cur.getItemId();
  int before = countId(all, id);
  Object t1 = c.setItemStackForSlot((short) slot, cur.withQuantity(1));
  if (t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) return null;
  boolean ok = putDst(dst, ds, cur.withQuantity(cur.getQuantity() - 1));
  if (!ok) { try { c.setItemStackForSlot((short) slot, cur); } catch (Throwable r) { @PKG@.Gear.warn("SPLIT RESTORE FAILED " + id + ": " + r); } }
  int after = countId(all, id);
  if (after != before) countCheck(all, id, before, u, "take one");
  else if (ok) @PKG@.GearLog.line("SPLIT-ONE " + u + " " + id + " rest x" + (cur.getQuantity() - 1));
  if (!ok) return null;
  return fe;
}""")
# why a stack cannot give up one item for an action (null = it can, or it is one item): what = "a reforge" / "identify"
M(gsp, r"""
public static String stackWhy(@IS@ it, @IC@[] give, String what) {
  if (it == null || it.isEmpty() || it.getQuantity() <= 1) return null;
  int need = @PKG@.GearDefs.FREE_KEEP + 1 - empties(give, null, -1);
  if (need <= 0) return null;
  return "Free " + need + (need == 1 ? " slot" : " slots") + " to split this stack - " + what + " works on one item at a time.";
}""")
M(gsp, r"""
public static @IC@[] giveOf(@INV@ inv) {
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getStorage(), inv.getBackpack() };
}""")
M(gsp, r"""
public static @IC@[] allOf(@INV@ inv) {
  @IC@[] cs = new @IC@[SCAN.length];
  for (int k = 0; k < cs.length; k++) cs[k] = section(inv, SCAN[k]);
  return cs;
}""")
# one stack -> the stack it should be (same object = nothing to do). cnt: [0] stamped Normal, [1] migrated, [2] re-rendered
M(gsp, r"""
public static @IS@ stampStack(@IS@ s, java.util.UUID owner, int[] cnt) {
  if (s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  @BD@ md = s.getMetadata();
  int st = @PKG@.GearData.state(md);
  if (!@PKG@.GearData.gearish(id, md)) return s;
  if (st == 3 || st == 4) {
    @PKG@.Gear.warnOnce("unread:" + id + ":" + (md == null ? 0 : md.toJson().hashCode()), (st == 4 ? "gear data of a newer SkyyGear on " : "Gear data unreadable on ") + id + " - left untouched");
    return s;
  }
  if (st == 0 && !@PKG@.GearData.isGear(id)) return s;
  @BD@ doc;
  if (st == 1) doc = @PKG@.GearData.gearDoc(md);
  else if (st == 2) doc = @PKG@.GearData.migrate(id, @PKG@.GearData.rollsDoc(md));
  else doc = @PKG@.GearData.legacy(id);
  @IS@ out = @PKG@.GearData.put(s, doc, owner);
  if (out != s && cnt != null) {
    if (st == 0) cnt[0] = cnt[0] + 1;
    else if (st == 2) cnt[1] = cnt[1] + 1;
    else cnt[2] = cnt[2] + 1;
  }
  return out;
}""")
M(gsp, r"""
public static void notice(@PR@ pr, int migrated) {
  try {
    java.util.UUID u = pr.getUuid();
    String pk = @PKG@.Gear.pkey(u);
    if (@PKG@.GearNotice.shown(pk)) return;
    @PKG@.GearNotice.mark(pk);
    if (!@PKG@.Gear.notifyOn(u, "gear.notices")) return;
    pr.sendMessage(@MSG@.raw("[Gear] Your old rolled items moved to the new gear system: " + migrated + " item(s) kept their rolls and got a rarity from how strong they are. /gear shows the item in your hand.").color(@PKG@.GearDefs.C_LABEL));
  } catch (Throwable t) { }
}""")
# safety valve (not in the spec): more than 300 stack rewrites for one player within 10 s means something keeps undoing our writes
# (e.g. an engine path that normalises the quality we set) - the stamp pauses 30 s for that player instead of looping, one WARN
M(gsp, r"""
public static boolean paused(java.util.UUID u, int wrote) {
  long now = System.currentTimeMillis();
  long[] r = (long[]) RATE.get(u);
  if (r == null) { r = new long[] { now, 0L, 0L }; RATE.put(u, r); }
  if (r[2] > now) return true;
  if (now - r[0] > 10000L) { r[0] = now; r[1] = 0L; }
  r[1] = r[1] + (long) wrote;
  if (r[1] > 300L) {
    r[2] = now + 30000L;
    r[1] = 0L;
    @PKG@.Gear.warnOnce("rate:" + u, "the gear stamp rewrote more than 300 stacks of one player within 10 s - paused 30 s for that player (an engine path may be undoing the writes)");
    return true;
  }
  return false;
}""")
# ================================================================= 0.1.3 GearChestOpen (1/2): every field + the LOOT WINDOW (see the header)
# LOOT: UUID -> Long = until when (ms) undocumented gear that shows up in that player's inventory (GearStamp.scan) or that the player
# drops (GearThrowSys) counts as chest loot: unidentified with the Chest odds instead of the legacy Normal stamp. Started by every open
# of a world container (GearChestOpen.decide), refreshed by GearTick each second while the container window stays open; GRACE_MS after
# the last sighting covers the coalesced stamp (<= 250 ms) and SkyyExploration's chest-luck give (a world task while the window is open).
# Review of 0.1.3 finding 1: LOOT_AT: UUID -> Long = when the window STARTED (an open = UseBlockEvent$Pre, or a container decided just
# now); a refresh never extends it past start + CAP_MS, however long the chest stays open.
# KNOWN: UUID -> TRUE = the players of this server (Universe player storage + online + PlayerReady); KNOWN_OK once the list was read.
F(gcho, "public static final java.util.concurrent.ConcurrentHashMap LOOT = new java.util.concurrent.ConcurrentHashMap();")
F(gcho, "public static final java.util.concurrent.ConcurrentHashMap LOOT_AT = new java.util.concurrent.ConcurrentHashMap();")
F(gcho, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")
F(gcho, "public static volatile boolean KNOWN_OK = false;")
F(gcho, "public static volatile long KNOWN_AT = 0L;")
F(gcho, "public static final long GRACE_MS = %dL;" % CHEST_GRACE_MS)
F(gcho, "public static final long CAP_MS = %dL;" % CHEST_LOOT_CAP_MS)
F(gcho, "public static final java.util.concurrent.atomic.AtomicLong OPEN_TAGS = new java.util.concurrent.atomic.AtomicLong();")
F(gcho, "public static final java.util.concurrent.atomic.AtomicLong LUCK_TAGS = new java.util.concurrent.atomic.AtomicLong();")
F(gcho, "public static final java.util.concurrent.atomic.AtomicLong WORLD_N = new java.util.concurrent.atomic.AtomicLong();")
F(gcho, "public static final java.util.concurrent.atomic.AtomicLong PLAYER_N = new java.util.concurrent.atomic.AtomicLong();")
# a fresh start: an open (UseBlockEvent$Pre) of a world / loot container, or a container decided just now
M(gcho, r"""
public static void loot(java.util.UUID u) {
  if (u == null) return;
  long now = System.currentTimeMillis();
  LOOT_AT.put(u, Long.valueOf(now));
  LOOT.put(u, Long.valueOf(now + GRACE_MS));
}""")
# the container window is still open (GearTick's sighting, the window task): + GRACE_MS, never past start + CAP_MS; no start = nothing
M(gcho, r"""
public static void lootMore(java.util.UUID u) {
  if (u == null) return;
  Object o = LOOT_AT.get(u);
  if (!(o instanceof Long)) return;
  long cap = ((Long) o).longValue() + CAP_MS;
  long now = System.currentTimeMillis();
  long until = now + GRACE_MS;
  if (until > cap) until = cap;
  if (until <= now) { LOOT_AT.remove(u, o); return; }
  Object cur = LOOT.get(u);
  if (cur instanceof Long && ((Long) cur).longValue() >= until) return;
  LOOT.put(u, Long.valueOf(until));
}""")
M(gcho, r"""
public static boolean looting(java.util.UUID u) {
  if (u == null) return false;
  Object o = LOOT.get(u);
  if (!(o instanceof Long)) return false;
  long now = System.currentTimeMillis();
  if (((Long) o).longValue() >= now) return true;
  LOOT.remove(u, o);
  Object st = LOOT_AT.get(u);
  if (st instanceof Long && ((Long) st).longValue() + CAP_MS <= now) LOOT_AT.remove(u, st);
  return false;
}""")
# chest loot = a gear stack with NO document (SkyyGear's or SkyyRolls'), only while part.chests is on
M(gcho, r"""
public static boolean lootable(@IS@ s) {
  if (s == null || s.isEmpty() || !@PKG@.GearCfg.PART_CHESTS) return false;
  return @PKG@.GearData.isGear(s.getItemId()) && !@PKG@.GearData.hasAnyDoc(s.getMetadata());
}""")
# one stack -> unidentified with the Chest odds (the same document GearTag.unid makes for a chest: GearRoll.unidDoc col 2, src chest)
M(gcho, r"""
public static @IS@ lootStack(@IS@ s, java.util.UUID u, String where) {
  if (!lootable(s)) return s;
  @BD@ d = @PKG@.GearRoll.unidDoc(s.getItemId(), 2, "chest");
  @IS@ ns = @PKG@.GearData.put(s, d, null);
  if (ns == null || ns == s) return s;
  LUCK_TAGS.incrementAndGet();
  @PKG@.GearLog.line("UNID chestloot " + ns.getItemId() + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + " x" + ns.getQuantity() + " " + u + " " + where);
  return ns;
}""")
# an inventory slot during a loot window (GearStamp.scan): a stack of several items is split per item first (each single its own
# unidentified document and rarity roll - GearStamp.split mode 2 into storage / backpack, never the hotbar, the 5-slot floor kept,
# counted before and after), then what stays in the slot is tagged. Returns the number of documents written.
M(gcho, r"""
public static int lootSlot(@IC@ c, int i, @INV@ inv, java.util.UUID u) {
  @IS@ s0 = c.getItemStack((short) i);
  if (!lootable(s0)) return 0;
  int n = 0;
  if (s0.getQuantity() > 1) {
    try { n = @PKG@.GearStamp.split(c, i, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv), u, 2, 64, @PKG@.GearDefs.FREE_KEEP, null); }
    catch (Throwable t) { @PKG@.Gear.warnOnce("lootsplit:" + s0.getItemId(), "chest loot split of " + s0.getItemId() + " failed (the stack is tagged whole): " + t); }
    if (n > 0) {
      LUCK_TAGS.addAndGet((long) n);
      @PKG@.GearLog.line("UNID chestloot " + s0.getItemId() + " x" + n + " singles " + u + " (split in the inventory)");
    }
  }
  @IS@ s = c.getItemStack((short) i);
  @IS@ ns = lootStack(s, u, "(in the inventory while a world chest was open)");
  if (ns == s) return n;
  c.setItemStackForSlot((short) i, ns);
  return n + 1;
}""")
# the scan (world thread): the 6 sections in SkyyRolls' order; never while profile:busy; pending crafts hold back only undocumented
# stacks of their own item id (review E3). Follow-up review 3: the scan never splits a stack (every single would carry the same
# document: a copy, the same migration or the same legacy Normal) - a stack of gear is stamped as one stack; Identify / Reforge take
# one item off it when a player acts on it. cnt[3] (split singles) stays 0, kept for the callers. 0.1.3: while the player's loot
# window is open (GearChestOpen.looting) an undocumented gear stack is chest loot (GearChestOpen.lootSlot, counted in cnt[0]).
M(gsp, r"""
public static int[] scan(@PR@ pr, @INV@ inv) {
  int[] cnt = new int[4];
  if (pr == null || inv == null) return cnt;
  java.util.UUID u = pr.getUuid();
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  if (@PKG@.Gear.busy(u) || paused(u, 0)) return cnt;
  boolean loot = @PKG@.GearChestOpen.looting(u);
  for (int k = 0; k < SCAN.length; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      if (@PKG@.GearData.state(s.getMetadata()) == 0 && held(u, s.getItemId())) continue;
      if (loot && @PKG@.GearChestOpen.lootable(s)) {
        try { cnt[0] = cnt[0] + @PKG@.GearChestOpen.lootSlot(c, i, inv, u); } catch (Throwable t2) { @PKG@.Gear.warnOnce("lootslot", "chest loot tag failed: " + t2); }
        continue;
      }
      @IS@ ns = stampStack(s, u, cnt);
      if (ns == s) continue;
      try { c.setItemStackForSlot((short) i, ns); } catch (Throwable t) { @PKG@.Gear.warnOnce("scanset", "stamp write failed: " + t); }
    }
  }
  paused(u, cnt[0] + cnt[1] + cnt[2] + cnt[3]);
  if (cnt[1] > 0) {
    notice(pr, cnt[1]);
    @PKG@.GearLog.line("MIGRATE " + pr.getUsername() + " " + u + " migrated=" + cnt[1] + " stamped=" + cnt[0]);
  }
  return cnt;
}""")
M(gsp, r"""
public static @INV@ invOf(@PR@ pr) {
  try {
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return null;
    @ST@ st = r.getStore();
    if (st == null) return null;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p == null ? null : p.getInventory();
  } catch (Throwable t) { return null; }
}""")
M(gsp, "public static void forget(java.util.UUID u) { if (u != null) { PENDING.remove(u); QUEUED.remove(u); LAST.remove(u); RATE.remove(u); } }")

# ================================================================= GearStampTask: one coalesced scan (<= every 250 ms per player)
gspt.addInterface(pool.get("java.lang.Runnable"))
F(gspt, "public @PR@ pr;")
F(gspt, "public boolean onWorld;")
F(gspt, "public java.util.UUID hop;")
C(gspt, "public GearStampTask(@PR@ pr, boolean onWorld, java.util.UUID hop) { this.pr = pr; this.onWorld = onWorld; this.hop = hop; }")
M(gspt, r"""
public void run() {
  java.util.UUID u = null;
  try {
    if (this.pr == null || !this.pr.isValid()) { if (this.pr != null) @PKG@.GearStamp.QUEUED.remove(this.pr.getUuid()); return; }
    u = this.pr.getUuid();
    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.GearStamp.QUEUED.remove(u); return; }
      this.onWorld = true;
      this.hop = wu;
      w.execute(this);
      return;
    }
    @PKG@.GearStamp.QUEUED.remove(u);
    java.util.UUID now = this.pr.getWorldUuid();
    if (this.hop != null && (now == null || !now.equals(this.hop))) return;
    @PKG@.GearStamp.scan(this.pr, @PKG@.GearStamp.invOf(this.pr));
  } catch (Throwable t) {
    if (u != null) @PKG@.GearStamp.QUEUED.remove(u);
    @PKG@.Gear.warnOnce("stamptask", "stamp scan failed: " + t);
  }
}""")
M(gsp, r"""
public static void dirty(@PR@ pr, @WLD@ w) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (QUEUED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try {
    Object l = LAST.get(u);
    long wait = (l instanceof Long ? ((Long) l).longValue() : 0L) + @PKG@.GearDefs.SCAN_GAP_MS - System.currentTimeMillis();
    if (wait <= 0L && w != null) w.execute(new @PKG@.GearStampTask(pr, true, pr.getWorldUuid()));
    else @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearStampTask(pr, false, null), wait < 1L ? 1L : wait, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { QUEUED.remove(u); }
}""")

# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)
# what must still be in the slot for a click to go through: same id, quality, gear / rolls document and durability
M(gfg, r"""
public static String fp(@IS@ it) {
  if (it == null || it.isEmpty()) return "";
  @BD@ md = it.getMetadata();
  @BV@ g = @PKG@.GearData.getv(md, @PKG@.GearDefs.DOC_KEY);
  @BV@ r = @PKG@.GearData.getv(md, @PKG@.GearDefs.ROLLS_KEY);
  String dj = g != null && g.isDocument() ? g.asDocument().toJson() : (r != null && r.isDocument() ? "R" + r.asDocument().toJson() : "none");
  return it.getItemId() + "|" + @PKG@.Gear.quality(it) + "|" + Integer.toHexString(dj.hashCode()) + "|" + (long) it.getDurability();
}""")
M(gfg, r"""
public static boolean same(@IS@ it, String id, String f) {
  if (it == null || it.isEmpty() || id == null || f == null) return false;
  return id.equals(it.getItemId()) && f.equals(fp(it));
}""")
M(gfg, r"""
public static java.util.ArrayList rows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });
    }
  }
  return out;
}""")
M(gfg, r"""
public static String where(int s, int slot) {
  if (s < 0 || s >= @PKG@.GearStamp.SEC_NAME.length) return "inventory";
  return @PKG@.GearStamp.SEC_NAME[s] + " " + (slot + 1);
}""")
# SkyyCoins 0.1.5 bridge (SkyyRolls Reforge.purse / take / refund): 1 taken, 0 not enough, -1 coins unavailable
M(gfg, r"""
public static long purse(java.util.UUID u) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:get");
    if (f == null) return -1L;
    Object r = f.apply(u);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:get failed: " + t); }
  return -1L;
}""")
M(gfg, r"""
public static int take(java.util.UUID u, long amt) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:take");
    if (f == null) return -1;
    Object r = f.apply(new Object[] { u, Long.valueOf(amt) });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:take failed: " + t); }
  return -1;
}""")
M(gfg, r"""
public static boolean refund(java.util.UUID u, long amt) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:add");
    if (f == null) return false;
    Object r = f.apply(new Object[] { u, Long.valueOf(amt) });
    return r instanceof Number;
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:add (refund) failed: " + t); }
  return false;
}""")
# why a stack cannot be reforged (null = it can); spec 5.4 "Which items"
M(gfg, r"""
public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick a weapon or armor piece first.";
  String id = it.getItemId();
  if (@PKG@.GearData.isTool(id)) return "Tools get their own modifiers with gathering gear - they cannot be reforged yet.";
  if (!@PKG@.GearData.isGear(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor can be reforged.";
  int st = @PKG@.GearData.state(it.getMetadata());
  if (st == 3) return "The gear data on this item is unreadable - an admin can check it with /gear read.";
  if (st == 4) return "This item comes from a newer SkyyGear - it cannot be changed here.";
  if (d == null) return "The gear data on this item is unreadable.";
  if (!@PKG@.GearData.identified(d)) return "Identify it first" + @PKG@.GearCfg.idHow();
  return null;
}""")
# Object[] { Integer code (1 done, 0 refused, -1 failed + refunded / not refunded), String message, IS newStack, BD before,
#            BD after, Long cost, Object[] { container, Integer slot } of the rest of a stack or null }. Coins TAKEN FIRST, REFUND on
# any failure; the new stack replaces the old one in the same slot. Follow-up review 3: a stack of several items gives up ONE item
# (GearStamp.takeOne: the rest moves to a free storage / backpack slot, 5 always stay free) after the coins are taken; no room =
# refused before any coin moves ("Free N slots to split this stack"). give / all = GearStamp.giveOf / allOf of the inventory.
M(gfg, r"""
public static Object[] reforge(@IC@ c, int slot, String expId, String expFp, java.util.UUID u, String who, boolean free, @IC@[] give, @IC@[] all) {
  @IS@ it = null;
  try { if (c != null && slot >= 0 && slot < c.getCapacity()) it = c.getItemStack((short) slot); } catch (Throwable t0) { it = null; }
  if (!same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a reforge");
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L), null };
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  long cost = free ? 0L : @PKG@.GearCfg.costReforge(r, lvl);
  if (cost > 0L) {
    int t = take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L), null };
    if (t == 0) {
      long have = purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: this reforge costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L), null };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " reforge " + id);
  }
  @BD@ nd = null;
  @IS@ nu = null;
  Object tx = null;
  Object[] rest = null;
  Throwable err = null;
  try {
    if (it.getQuantity() > 1) {
      rest = @PKG@.GearStamp.takeOne(c, slot, give, all, u);
      if (rest == null) throw new IllegalStateException("the stack could not be split");
      it = c.getItemStack((short) slot);
      if (!same(it, expId, expFp) || it.getQuantity() != 1) throw new IllegalStateException("the stack changed while it was split");
    }
    nd = @PKG@.GearRoll.reforge(id, d);
    nu = @PKG@.GearData.put(it, nd, u);
    tx = c.setItemStackForSlot((short) slot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && nu != it && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("REFORGE FAILED for " + who + " (" + u + ") on " + id + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " reforge " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "The reforge failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "The reforge failed and the refund did not go through - an admin can find it in the server log.", null, d, null, Long.valueOf(cost), rest };
  }
  if (!free) {
    long xp = @PKG@.GearCfg.xpReforge(r);
    if (xp > 0L) {
      try {
        java.util.function.Function f = @PKG@.Gear.fn("skill:fn:addxp");
        if (f != null) f.apply(new Object[] { u, "Smithing", Long.valueOf(xp), "gear:reforge", @PKG@.Gear.pkey(u) });
      } catch (Throwable t) { @PKG@.Gear.warnOnce("addxp", "skill:fn:addxp failed: " + t); }
    }
  }
  @PKG@.GearLog.line("REFORGE " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + lvl + " [" + @PKG@.GearView.modSummary(d) + "] -> [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + " rfN " + @PKG@.GearData.num(nd, "rfN", 0) + (free ? " (admin, free)" : ""));
  return new Object[] { Integer.valueOf(1), "Reforged!", nu, d, nd, Long.valueOf(cost), rest };
}""")

# ================================================================= GearFn: bridge functions (spec 7.1). Never throw, never touch ECS.
gfn.addInterface(pool.get("java.util.function.Function"))
F(gfn, "public int mode;")
C(gfn, "public GearFn(int mode) { this.mode = mode; }")
# X = an ItemStack or Object[]{String itemId, BsonDocument metadata} -> Object[]{ String id, BsonDocument md, Integer quality }
M(gfn, r"""
public static Object[] x(Object o) {
  if (o instanceof @IS@) {
    @IS@ s = (@IS@) o;
    if (s.isEmpty()) return null;
    return new Object[] { s.getItemId(), s.getMetadata(), Integer.valueOf(@PKG@.Gear.quality(s)) };
  }
  if (o instanceof Object[]) {
    Object[] a = (Object[]) o;
    if (a.length < 1 || !(a[0] instanceof String)) return null;
    @BD@ md = a.length > 1 && a[1] instanceof @BD@ ? (@BD@) a[1] : null;
    return new Object[] { a[0], md, Integer.valueOf(Integer.MIN_VALUE) };
  }
  return null;
}""")
M(gfn, r"""
public static @BD@ docOf(Object[] xs) {
  if (xs == null) return null;
  String id = (String) xs[0];
  @BD@ md = (@BD@) xs[1];
  if (!@PKG@.GearData.gearish(id, md)) return null;
  return @PKG@.GearData.effective(id, md);
}""")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 6) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2) return null;
      Object[] a = (Object[]) o;
      java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
      Object[] xs = x(a[1]);
      @BD@ d = docOf(xs);
      if (d == null) return null;
      String id = (String) xs[0];
      Object[] c = @PKG@.GearGate.check(u, id, d, @PKG@.GearLevel.level(id, d));
      boolean enf = ((Boolean) c[4]).booleanValue() && @PKG@.GearCfg.PART_GATE;
      return new Object[] { c[0], c[1], c[2], c[3], Boolean.valueOf(enf) };
    }
    if (m == 7) {
      Object v = o instanceof java.util.UUID ? @PKG@.Gear.bget("gear:stats:" + o) : null;
      return v instanceof String ? v : "";
    }
    if (m == 8) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 4) return null;
      Object[] a = (Object[]) o;
      java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
      String id = a[1] instanceof String ? (String) a[1] : null;
      int n = a[2] instanceof Number ? ((Number) a[2]).intValue() : 1;
      String src = a[3] instanceof String ? (String) a[3] : "craft";
      // 0.2: gathering tools too (they store a level, spec 1), not only gear
      if (id == null || !@PKG@.GearRoll.craftable(id) || !@PKG@.GearCfg.PART_CRAFT) return null;
      // never more stacks than were crafted (SkyySacks 0.7.7 refuses an answer above count); above 64 the caller gives the rest plain
      if (n < 1) return null;
      if (n > 64) n = 64;
      boolean craft = "craft".equals(src);
      // 0.2 (spec 4 + 8): every item of this craft is made at the crafter's level (the same crafter + item = the same level); an
      // optional 6th element = a requested level (a later "craft lower" picker), kept inside the band and never above that level
      int lv = craft ? @PKG@.GearRoll.craftLevel(id, u) : -1;
      if (craft && lv >= 0 && a.length > 5 && a[5] instanceof Number) {
        int want = ((Number) a[5]).intValue();
        int[] bb = @PKG@.GearLevel.band(id);
        if (want < bb[0]) want = bb[0];
        if (want > lv) want = lv;
        lv = want;
      }
      Object[] out = new Object[n];
      for (int i = 0; i < n; i++) {
        @BD@ d = craft ? @PKG@.GearRoll.craftDoc(id, u, lv) : @PKG@.GearRoll.newDoc(id, @PKG@.GearData.isGear(id) ? @PKG@.GearRoll.pickRarity(0) : 0, true, src);
        out[i] = @PKG@.GearData.put(new @IS@(id, 1), d, u);
      }
      @PKG@.GearLog.line("ROLL bridge " + src + " " + u + " " + id + " x" + n + (lv >= 0 ? " lv" + lv : "") + (a.length > 4 && a[4] != null ? " recipe " + a[4] : ""));
      if (craft) {
        String note = @PKG@.GearRoll.craftNote(id, u);
        if (note != null && @PKG@.GearRoll.noteDue(u, id, System.currentTimeMillis())) @PKG@.Gear.tell(u, "[Gear] " + note, @PKG@.GearDefs.C_LABEL);
      }
      return out;
    }
    if (m == 9) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2 || !(((Object[]) o)[0] instanceof @IS@)) return o instanceof Object[] && ((Object[]) o).length > 0 ? ((Object[]) o)[0] : null;
      Object[] a = (Object[]) o;
      @IS@ s = (@IS@) a[0];
      String src = a[1] instanceof String ? (String) a[1] : "";
      if (s.isEmpty() || !@PKG@.GearData.isGear(s.getItemId()) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return s;
      int col = "mob".equals(src) ? 1 : ("chest".equals(src) ? 2 : 0);
      if (col == 0) return s;
      if (col == 1 && !@PKG@.GearCfg.PART_DROPS) return s;
      if (col == 2 && !@PKG@.GearCfg.PART_CHESTS) return s;
      return @PKG@.GearData.put(s, @PKG@.GearRoll.unidDoc(s.getItemId(), col, col == 1 ? "drop" : "chest"), null);
    }
    Object[] xs = x(o);
    @BD@ d = docOf(xs);
    if (d == null) {
      if (m == 0 && xs != null && @PKG@.GearData.gearish((String) xs[0], (@BD@) xs[1])) {
        int st = @PKG@.GearData.state((@BD@) xs[1]);
        if (st == 3) return new String[] { @PKG@.Gear.itemName((String) xs[0]), "Gear data unreadable" };
        if (st == 4) return new String[] { @PKG@.Gear.itemName((String) xs[0]), "Gear data from a newer SkyyGear (read only)" };
      }
      return null;
    }
    String id = (String) xs[0];
    if (m == 0) return @PKG@.GearView.plain(id, d, null);
    if (m == 1) return @PKG@.GearView.rollsLine(id, d);
    if (m == 2) return @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)];
    if (m == 3) return Integer.valueOf(@PKG@.GearLevel.level(id, d));
    if (m == 4) return Boolean.valueOf(@PKG@.GearData.identified(d));
    if (m == 5) return @PKG@.GearView.bridgeSig(id, ((Integer) xs[2]).intValue(), d);
    return null;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("fn" + this.mode, "bridge function " + this.mode + " failed: " + t);
    return null;
  }
}""")

# ================================================================= systems (one registerSystem per class)
def event_system(cls, ctor, event_cls, query, body):
    C(cls, "public %s() { super(%s.class); }" % (ctor, event_cls))
    M(cls, "public @QRY@ getQuery() { return %s; }" % query)
    M(cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
%s
  } catch (Throwable t) { @PKG@.Gear.warnOnce("%s", "%s failed: " + t); }
}""" % (body, ctor, ctor))


PLAYER_Q = "(@QRY@) @PLA@.getComponentType()"
# spec 1.5: InventoryChangeEvent (the ECS event SkyySkills' SmeltSys uses) marks the player dirty; one coalesced scan <= 250 ms
event_system(ginv, "GearInvSys", ICE, PLAYER_Q, r"""
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @PKG@.GearStamp.dirty(pr, w);""")
# spec 1.5 GearThrowSys: ItemUtils.throwItem fires the cancellable DropItemEvent$Drop on the dropping entity, then spawns whatever stack
# the event holds (VERIFIED bytecode): a player-thrown undocumented gear stack is stamped here, before the item entity exists.
# 0.1.3: during the player's loot window it is chest loot instead (SkyyExploration's luck roll drops at the feet when the
# inventory is full: SimpleItemContainer.addOrDropItemStack -> ItemUtils.dropItem -> throwItem -> this event)
event_system(gthr, "GearThrowSys", DIE, PLAYER_Q, r"""
    @DIE@ e = (@DIE@) ev;
    if (e.isCancelled()) return;
    @IS@ s = e.getItemStack();
    if (s == null || s.isEmpty() || !@PKG@.GearData.gearish(s.getItemId(), s.getMetadata())) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @IS@ ns = @PKG@.GearChestOpen.looting(pr.getUuid()) && @PKG@.GearChestOpen.lootable(s) ? @PKG@.GearChestOpen.lootStack(s, pr.getUuid(), "(dropped while a world chest was open)") : @PKG@.GearStamp.stampStack(s, pr.getUuid(), null);
    if (ns != s) e.setItemStack(ns);""")
# the roll task: stacks of that id that were not in the snapshot, carry no document and look exactly like a fresh output (metadata
# equal to the recipe output's, full durability; review E1), at most units x output quantity of them
gcrt.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public String id;", "public java.util.IdentityHashMap snap;", "public int cap;", "public @BD@ outMeta;",
           "public String recipe;"):
    F(gcrt, _f)
C(gcrt, r"""
public GearCraftTask(@PR@ pr, String id, java.util.IdentityHashMap snap, int cap, @BD@ outMeta, String recipe) {
  this.pr = pr; this.id = id; this.snap = snap; this.cap = cap; this.outMeta = outMeta; this.recipe = recipe;
}""")
# a stack that looks exactly like a fresh bench output: metadata equal to the recipe output's (normally none) and full durability
M(gcrt, r"""
public static boolean fresh(@IS@ s, @BD@ outMeta) {
  @BD@ md = s.getMetadata();
  boolean e1 = md == null || md.isEmpty();
  boolean e2 = outMeta == null || outMeta.isEmpty();
  if (e1 != e2) return false;
  if (!e1 && !md.equals(outMeta)) return false;
  return s.getDurability() >= s.getMaxDurability();
}""")
# the candidate rule over the containers in SCAN order (static so the bare-JVM harness runs it on plain containers): not in the
# pre-craft identity snapshot, no document, fresh; at most cap rolls. got collects the rolled rarity ids. Returns the roll count.
# exploit review 2: a candidate stack of q items is rolled per item (split into singles, give = storage, backpack - follow-up review
# 3: never the hotbar, 5 slots always stay free) and only when q still fits the craft count (q <= cap - n): a crafted stack that
# merged into an undocumented stack is never rolled as one. What cannot be split for lack of room stays unrolled (CRAFT-MISS line).
M(gcrt, r"""
public static int rollIn(@IC@[] cs, @IC@[] give, java.util.UUID u, String id, java.util.IdentityHashMap snap, int cap, @BD@ outMeta, StringBuilder got) {
  int n = 0;
  for (int k = 0; k < cs.length && n < cap; k++) {
    @IC@ c = cs[k];
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity() && n < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty() || !id.equals(s.getItemId())) continue;
      if (snap.containsKey(s) || @PKG@.GearData.hasAnyDoc(s.getMetadata()) || !fresh(s, outMeta)) continue;
      int q = s.getQuantity();
      if (q > cap - n) continue;
      if (q > 1) {
        n = n + @PKG@.GearStamp.split(c, i, give, cs, u, 1, q - 1, @PKG@.GearDefs.FREE_KEEP, got);
        s = c.getItemStack((short) i);
        if (s == null || s.isEmpty() || s.getQuantity() > 1 || n >= cap) continue;
      }
      @BD@ d = @PKG@.GearRoll.craftDoc(id, u);
      @IS@ ns = @PKG@.GearData.put(s, d, u);
      if (ns == s) continue;
      c.setItemStackForSlot((short) i, ns);
      n++;
      if (got != null) got.append(' ').append(@PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]);
    }
  }
  return n;
}""")
M(gcrt, r"""
public void run() {
  java.util.UUID u = null;
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    u = this.pr.getUuid();
    @INV@ inv = @PKG@.GearStamp.invOf(this.pr);
    if (inv == null || @PKG@.Gear.busy(u)) { @PKG@.GearStamp.pendingClear(u, this.id); return; }
    @IC@[] cs = @PKG@.GearStamp.allOf(inv);
    StringBuilder got = new StringBuilder();
    int n = rollIn(cs, @PKG@.GearStamp.giveOf(inv), u, this.id, this.snap, this.cap, this.outMeta, got);
    @PKG@.GearStamp.pendingClear(u, this.id);
    if (n > 0) {
      // 0.2: the level the items were made at (spec 4) + one chat line when the crafter is below / above the material band (review of 0.2
      // finding 3: once per crafting burst - a timed queue runs one task per unit)
      int lv = @PKG@.GearRoll.craftLevel(this.id, u);
      @PKG@.GearLog.line("CRAFT " + this.pr.getUsername() + " " + u + " " + this.id + " x" + n + ":" + got.toString() + (lv >= 0 ? " lv" + lv : "") + " recipe " + this.recipe + " smith " + @PKG@.Gear.fnum(@PKG@.GearRoll.smithChance(u)) + "%");
      String note = @PKG@.GearRoll.craftNote(this.id, u);
      if (note != null && @PKG@.GearRoll.noteDue(u, this.id, System.currentTimeMillis())) this.pr.sendMessage(@MSG@.raw("[Gear] " + note).color(@PKG@.GearDefs.C_LABEL));
    }
    if (n < this.cap) @PKG@.GearLog.line("CRAFT-MISS " + this.pr.getUsername() + " " + this.id + " rolled " + n + " of " + this.cap + " (output on the ground or changed) - the rest is stamped Normal");
  } catch (Throwable t) {
    if (u != null) @PKG@.GearStamp.pendingClear(u, this.id);
    @PKG@.Gear.warnOnce("crafttask", "crafted gear roll failed: " + t);
  }
}""")
# spec 5.1 GearCraftSys: CraftRecipeEvent$Post (before giveOutput) -> snapshot the identities of every stack of the output id, hold that id
# back from the stamp, and roll the new stacks in a world task that runs after giveOutput returned (same queue, FIFO)
event_system(gcrs, "GearCraftSys", CREP, "@ARC@.empty()", r"""
    @CRE@ e = (@CRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CRAFT) return;
    @CRR@ rc = e.getCraftedRecipe();
    if (rc == null) return;
    @MQ@ po = rc.getPrimaryOutput();
    if (po == null) return;
    String id = po.getItemId();
    if (id == null || !@PKG@.GearRoll.craftable(id)) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pr == null || p == null || p.getInventory() == null) return;
    if (p.getGameMode() == @GM@.Creative) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());
    int cap = units * Math.max(1, po.getQuantity());
    if (cap > 64) cap = 64;
    java.util.IdentityHashMap snap = new java.util.IdentityHashMap();
    @INV@ inv = p.getInventory();
    for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
      @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
      if (c == null) continue;
      for (int i = 0; i < c.getCapacity(); i++) {
        @IS@ s = c.getItemStack((short) i);
        if (s != null && !s.isEmpty() && id.equals(s.getItemId())) snap.put(s, Boolean.TRUE);
      }
    }
    @PKG@.GearStamp.pendingAdd(pr.getUuid(), id);
    w.execute(new @PKG@.GearCraftTask(pr, id, snap, cap, po.getMetadata(), rc.getId()));""")
# 0.2 craft.belowBand block (spec 4 / 9: "block = refuse"): CraftingManager.queueCraft (timed bench crafts) and craftItem (instant) fire the
# cancellable CraftRecipeEvent$Pre on the crafter and return before the job is queued / any input is taken when it was cancelled (VERIFIED
# bytecode 2026-10-02, re-checked below); its Post is fired AFTER the inputs are taken, so only Pre may refuse. Nothing happens unless
# craft.belowBand is block (default min) - the /craft bridge cannot refuse a craft (SkyySacks gives the plain output then), so /craft makes
# the item at the band start in both modes (UNVERIFIED: a SkyySacks refusal path)
for _m in ("queueCraft", "craftItem"):
    _qc = _calls("com.hypixel.hytale.builtin.crafting.component.CraftingManager", _m)
    _qa, _qb = _qc.find("CraftRecipeEvent$Pre.<init>"), _qc.find("CraftRecipeEvent$Pre.isCancelled")
    _qz = max(_qc.find("CraftingManager.removeInputFromInventory"), _qc.find("BlockingQueue.offer"))
    assert 0 <= _qa < _qb < _qz, "CraftingManager.%s no longer refuses a cancelled CraftRecipeEvent$Pre before it takes the inputs" % _m
event_system(gcrp, "GearCraftPreSys", CREPRE, "@ARC@.empty()", r"""
    @CREPRE@ e = (@CREPRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CRAFT || !@PKG@.GearCfg.PART_LEVELS || !"block".equals(@PKG@.GearCfg.CRAFT_BELOW)) return;
    @CRR@ rc = e.getCraftedRecipe();
    if (rc == null) return;
    @MQ@ po = rc.getPrimaryOutput();
    if (po == null) return;
    String id = po.getItemId();
    if (id == null || !@PKG@.GearRoll.craftable(id)) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pr == null || p == null || p.getGameMode() == @GM@.Creative) return;
    String why = @PKG@.GearRoll.blockWhy(id, pr.getUuid());
    if (why == null) return;
    e.setCancelled(true);
    pr.sendMessage(@MSG@.raw("[Gear] " + why).color(@PKG@.GearDefs.C_BAD));
    @PKG@.GearLog.line("CRAFT-BLOCK " + pr.getUsername() + " " + pr.getUuid() + " " + id + " recipe " + rc.getId() + ": " + why);""")

# ####################################################################################################################################
# PART B (1/2): level enforcement (3.4, 3.5), live stats (4.3, 3.5 part 2, 4.2), unidentified mob + chest drops (5.5). Placed here
# because GearTick (next) calls GearFx.second. Compile order = call order: GearMove, GearHit, GearShot, GearShotTrack, GearArmor,
# GearTag, GearFx (helpers), the systems, then GearFx.setup (the registrations PARTB_SETUP calls).
# ####################################################################################################################################
SI = dict((k, S_KEYS.index(k)) for k in S_KEYS)
SHOT_WINDOW_MS = 10000      # SkyyClasses 0.1.6 verbatim: a live projectile launched with a blocked weapon blocks all of its shooter's damage
SHOT_PURGE_MS = 120000      # launch records older than this are purged when the table grows past SHOT_PURGE_AT (safety net)
SHOT_PURGE_AT = 1024
MOVE_SOURCE = "gear.armor"  # spec 4.2 Speed: skyymove protocol v1 source name, layer flat (HANDOFF: armor flat, accessories %)
LOCK_PREFIX = "skyygear_lock_"   # spec 3.5 part 2; SkyySkills uses skyyskill_*, SkyyAccessories skyyacc_* - never the same key
for _other in ("skyyskill_basemana", "skyyskill_overallhp", "skyyskill_overallmana", "skyyacc_health", "skyyacc_stamina", "skyyacc_mana"):
    assert not _other.startswith(LOCK_PREFIX) and not _other.startswith("skyygear_")
MV.add_move_sync(gmv, CtField, CtNewMethod, PKG + ".Gear.warn")

# ================================================================= GearHit: combat helpers (spec 3.4, 4.3)
F(ghit, "public static final java.util.IdentityHashMap INFO = new java.util.IdentityHashMap();")    # Damage -> Object[] (below)
F(ghit, "public static final java.util.concurrent.ConcurrentHashMap FAM = new java.util.concurrent.ConcurrentHashMap();")
for _k in ("dmg", "str", "mp", "cc", "cd", "tdmg", "fEarth", "fThunder", "fWater", "fFire", "fAir", "rThunder", "rWater", "rElem",
           "msteal", "lsteal", "hpr", "hprp", "def", "spd", "stam", "chg"):
    F(ghit, "public static final int I_%s = %d;" % (_k.upper(), SI[_k]))
# the per-Damage info GearHitSys leaves for GearArmorSys / GearTrueSys / GearLeechSys (the same Damage object runs through every
# damage system in one dispatch): Object[] { Float pre-armor amount (null = the victim wears no inactive armor), Integer True Damage,
# Integer Life Steal %, Integer Mana Steal, UUID attacker, Integer flat element damage (design review 8) }. GearLeechSys removes it;
# entries of damage cancelled on the way are dropped when the table passes 512 (they are never read again).
M(ghit, r"""
public static synchronized void put(Object d, Object[] v) {
  if (INFO.size() > 512) INFO.clear();
  INFO.put(d, v);
}""")
M(ghit, "public static synchronized Object[] get(Object d) { return (Object[]) INFO.get(d); }")
M(ghit, "public static synchronized Object[] take(Object d) { return (Object[]) INFO.remove(d); }")
# design review 8 (lock 17): the flat element lines (+ 5 x Raw Elemental) are kept aside from the hit math and added AFTER armor and
# Defense by GearTrueSys, like True Damage - not cut by Defence, not doubled by crits
M(ghit, r"""
public static int elemSum(int[] t) {
  if (t == null) return 0;
  long s = (long) t[I_FEARTH] + (long) t[I_FTHUNDER] + (long) t[I_FWATER] + (long) t[I_FFIRE] + (long) t[I_FAIR] + (long) t[I_RTHUNDER] + (long) t[I_RWATER] + 5L * (long) t[I_RELEM];
  return @PKG@.GearStats.sat(s);
}""")
M(ghit, r"""
public static Object[] info(java.util.UUID u, int[] t) {
  if (t == null) return new Object[] { null, Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(0), u, Integer.valueOf(0) };
  return new Object[] { null, Integer.valueOf(t[I_TDMG]), Integer.valueOf(t[I_LSTEAL]), Integer.valueOf(t[I_MSTEAL]), u, Integer.valueOf(elemSum(t)) };
}""")
# spec 3.4: when SkyyClasses already says the class may not use the item, SkyyGear stays out (SkyyClasses blocks + shows its popup)
M(ghit, r"""
public static boolean classAllows(java.util.UUID u, String id) {
  java.util.function.Function f = @PKG@.Gear.fn("class:fn:allowed");
  if (f == null || u == null) return true;
  try {
    Object r = f.apply(new Object[] { u, id });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue();
  } catch (Throwable t) { }
  return true;
}""")
# spec 3.4: null = this item may deal damage; else { item id, popup title, popup body }. Unidentified gear is always blocked (5.6);
# the level check follows part.gate. Tools and kinds 0.1 does not enforce (gathering) never block.
M(ghit, r"""
public static String[] judge(java.util.UUID u, @IS@ it, boolean util) {
  if (u == null || it == null || it.isEmpty()) return null;
  String id = it.getItemId();
  if (!@PKG@.GearData.isGear(id)) return null;
  // engine review 3: only a weapon is judged as a weapon - armor (or Equipment) held in the hand never blocks a hit
  int sl = @PKG@.GearData.slotOf(id);
  if (sl != 0 && sl != 1) return null;
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  if (d == null || !@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kind(d))) return null;
  if (!classAllows(u, id)) return null;
  String where = util ? " (it is in your utility slot)" : "";
  if (!@PKG@.GearData.identified(d)) return new String[] { id, "Unidentified", "Identify it first" + @PKG@.GearCfg.idHow() + where };
  int need = @PKG@.GearLevel.level(id, d);
  Object[] c = @PKG@.GearGate.check(u, id, d, need);
  if (((Boolean) c[0]).booleanValue()) return null;
  int st = ((Integer) c[5]).intValue();
  String base = @PKG@.Gear.itemName(id);
  String body;
  if (st == 1) body = base + " needs " + c[1] + " " + need + " - pick a class first";
  else if (st == 2) body = base + " needs level " + need + " - skills are unavailable right now";
  else body = base + " needs " + c[1] + " " + need + " - you are " + c[3];
  return new String[] { id, "Level too low", body + where };
}""")
# 1 = Physical family (melee: Physical, Slashing, Bludgeoning), 2 = Projectile family, 0 = anything else (fire / poison damage over
# time, environment). Offence stats only change weapon hits (VERIFIED Assets.zip: weapon BaseDamage keys are Physical / Projectile;
# staff spells use Fire / Ice and count through the spell-projectile record instead).
M(ghit, r"""
public static int family(@DCS@ c) {
  if (c == null) return 0;
  String id = c.getId();
  if (id == null) return 0;
  Object o = FAM.get(id);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int f = 0;
  @DCS@ x = c;
  for (int i = 0; i < 6 && x != null; i++) {
    String xi = x.getId();
    if ("Physical".equals(xi)) { f = 1; break; }
    if ("Projectile".equals(xi)) { f = 2; break; }
    String inh = x.getInherits();
    if (inh == null || inh.length() == 0) break;
    Object n = null;
    try { n = @DCS@.getAssetMap().getAsset(inh); } catch (Throwable t) { n = null; }
    x = n instanceof @DCS@ ? (@DCS@) n : null;
  }
  FAM.put(id, Integer.valueOf(f));
  return f;
}""")
# (the totals live in GearStats.totals since design review 2 - one function for combat, Defense, regen, Speed and gear:stats)
# spec 4.3 step 1, in order: Damage %, Strength (physical) or Magical Power (spell), crit with chance (crit.base + cc) %: x 2 x
# (1 + (crit.baseDamage + cd) %), overcrit (a second roll at chance - 100 %) x 2, at most once. The flat element lines are NOT in
# here any more (design review 8: GearTrueSys adds elemSum after armor). r1 / r2 = the two random numbers in [0, 1) (the harness
# passes fixed ones).
# follow-up review 9: gear:extra may be negative - Damage % counts down to -100 at most, no factor goes below 0, and the result is
# never below 0 (nor above 1e9, so the float stays finite)
# 0.1.2: chg = a charged hit (GearCharged.judge) -> one more SEPARATE factor x (1 + Charged Attack Damage %) - spells x (1 +
# charged.spellFactor x Charged Attack Damage %) (Skyy: "if it adds +100% damage to a charged bow or melee, it would only add +15% to a
# spell") - after Strength / Magical Power, before the crit roll (a charged crit gets both); clamped at 0 like every factor. True
# Damage and the flat element lines are not in here (GearTrueSys adds them after armor), so they are never multiplied.
M(ghit, r"""
public static double hitAmount(double amount, int[] t, boolean spell, boolean chg, double r1, double r2) {
  int dm = t[I_DMG];
  if (dm < -100) dm = -100;
  double a = amount * (1.0 + (double) dm / 100.0);
  double per = spell ? @PKG@.GearCfg.MP_PER : @PKG@.GearCfg.STR_PER;
  int pt = spell ? t[I_MP] : t[I_STR];
  double fp = 1.0 + (double) pt * per / 100.0;
  a = a * (fp > 0.0 ? fp : 0.0);
  if (chg) {
    double cp = (double) t[I_CHG];
    if (spell) cp = cp * @PKG@.GearCfg.CHG_SPELL;
    double fq = 1.0 + cp / 100.0;
    a = a * (fq > 0.0 ? fq : 0.0);
  }
  double ch = (@PKG@.GearCfg.CRIT_BASE + (double) t[I_CC]) / 100.0;
  if (ch > 0.0 && r1 < ch) {
    double fc = 2.0 * (1.0 + (@PKG@.GearCfg.CRIT_BASE_DMG + (double) t[I_CD]) / 100.0);
    a = a * (fc > 0.0 ? fc : 0.0);
    if (ch > 1.0 && r2 < ch - 1.0) a = a * 2.0;
  }
  if (!(a > 0.0)) return 0.0;
  if (a > 1.0E9) return 1.0E9;
  return a;
}""")
# the 0.1.1 signature = no charged hit (kept for every caller that has no DamageSequence to judge)
M(ghit, "public static double hitAmount(double amount, int[] t, boolean spell, double r1, double r2) { return hitAmount(amount, t, spell, false, r1, r2); }")

# ================================================================= GearShot + GearShotTrack (SkyyClasses 0.1.6 ShotRec / ShotTrack copy)
for _f in ("public java.util.UUID shooter;", "public @IS@ main;", "public @IS@ util;", "public String bad;", "public String title;",
           "public String body;", "public long at;",
           # 0.1.2: a legacy projectile launched only from a FULL step (signal C), its asset name, main came from the hand snapshot
           "public boolean charged;", "public String pid;", "public boolean snap;"):
    F(gsho, _f)
C(gsho, r"""
public GearShot(java.util.UUID shooter, @IS@ main, @IS@ util, String[] bad) {
  this.shooter = shooter;
  this.main = main;
  this.util = util;
  this.bad = bad == null ? null : bad[0];
  this.title = bad == null ? null : bad[1];
  this.body = bad == null ? null : bad[2];
  this.at = System.currentTimeMillis();
}""")
# ####################################################################################################################################
# 0.1.2 CHARGED ATTACK DAMAGE (2/2): GearHandSys (the hand snapshot every tick) + GearCharged (the per-hit judge on the hit's
# DamageSequence, the probe of /gear charged, charged.log lines). After GearShot (it reads GearShot.charged / pid), before
# GearShotTrack and GearHitSys (their callers).
# ####################################################################################################################################
F(ghns, "public @QRY@ query;")
C(ghns, "public GearHandSys() { super(); this.query = null; }")
M(ghns, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(ghns, "public boolean isParallel(int a, int b) { return false; }")
M(ghns, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PKG@.GearHand.seen(pr.getUuid(), @INVC@.getItemInHand(cb, r));
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }
}""")
# PROBE: UUID -> Long probe-until (armed by /gear charged: that admin's hits are judged even without the stat); LAST: UUID ->
# Object[] { Long at, String line } = the last judged hit of an armed player
F(gchg, "public static final java.util.concurrent.ConcurrentHashMap PROBE = new java.util.concurrent.ConcurrentHashMap();")
F(gchg, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
M(gchg, r"""
public static boolean watch(java.util.UUID u) {
  if (u == null || PROBE.isEmpty()) return false;
  Object o = PROBE.get(u);
  if (!(o instanceof Long)) return false;
  if (((Long) o).longValue() < System.currentTimeMillis()) { PROBE.remove(u); return false; }
  return true;
}""")
# the hit's DamageSequence (DamageCalculatorSystems.DAMAGE_SEQUENCE, put on the Damage by DamageEntityInteraction before the damage
# event is dispatched - VERIFIED bytecode; the engine's own SequenceModifier reads it the same way; Damage implements IMetaStore and
# getIfPresentMetaObject is an interface default method) -> GearChg.judgeCalc. A legacy projectile hit has no sequence: the launch
# record decides (GearShot.charged). shot = the hit's launch record (null = melee), alts = null when that record is the projectile's
# own (GearShotTrack.find), else the item ids of the shooter's live records (GearShotTrack.liveIds; review of 0.1.2 finding 1).
M(gchg, r"""
public static boolean judge(@DMG@ d, String wid, @PKG@.GearShot shot, String[] alts, String[] why) {
  Object calc = null;
  boolean seq = false;
  try {
    Object so = ((@IMS@) d).getIfPresentMetaObject(@DCSYS@.DAMAGE_SEQUENCE);
    if (so instanceof @DSEQ@) { seq = true; calc = ((@DSEQ@) so).getDamageCalculator(); }
  } catch (Throwable t) { seq = false; calc = null; }
  String[] al = null;
  if (shot != null) al = alts;
  return @PKG@.GearChg.judgeCalc(calc, seq, wid, shot != null, al, shot != null && shot.charged, shot == null ? null : shot.pid, why) == 1;
}""")
# review of 0.1.2 finding 4: the line is built only while someone reads it (an armed probe or charged.log)
M(gchg, r"""
public static void note(java.util.UUID u, @PR@ pr, @IS@ main, boolean chg, String why, boolean spell, int stat, float a0, double a) {
  try {
    boolean wt = watch(u);
    if (!wt && !@PKG@.GearCfg.CHG_LOG) return;
    String wid = main == null || main.isEmpty() ? "-" : main.getItemId();
    double pct = spell ? (double) stat * @PKG@.GearCfg.CHG_SPELL : (double) stat;
    String line = (chg ? "CHARGED" : "not charged") + " - " + why + " - " + wid + (spell ? " (spell)" : "") + " - damage "
      + @PKG@.Gear.fnum((double) a0) + " -> " + @PKG@.Gear.fnum(a)
      + (chg ? " (Charged Attack Damage " + stat + "%" + (spell ? " x " + @PKG@.Gear.fnum(@PKG@.GearCfg.CHG_SPELL) + " = " + @PKG@.Gear.fnum(pct) + "%" : "") + "; every other stat and crits included)" : "");
    if (wt) LAST.put(u, new Object[] { Long.valueOf(System.currentTimeMillis()), line });
    if (@PKG@.GearCfg.CHG_LOG) @PKG@.GearLog.line("CHARGED " + (chg ? "yes " : "no ") + (pr == null ? "?" : pr.getUsername()) + " " + u + " " + line);
  } catch (Throwable t) { }
}""")
M(gchg, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  PROBE.remove(u);
  LAST.remove(u);
  @PKG@.GearHand.forget(u);
}""")
# /gear charged [off] (admin, read only): the switch + your total, the held item's index summary + whether it may roll, the last judged
# hit; arms the 10-minute probe (off ends it)
M(gchg, r"""
public static String[] probe(java.util.UUID u, @IS@ held, int[] t, String rest) {
  java.util.ArrayList out = new java.util.ArrayList();
  String a = rest == null ? "" : rest.trim().toLowerCase();
  if (a.equals("off")) {
    PROBE.remove(u);
    LAST.remove(u);
    out.add("charged-attack probe off");
    return (String[]) out.toArray(new String[0]);
  }
  long now = System.currentTimeMillis();
  boolean was = watch(u);
  PROBE.put(u, Long.valueOf(now + 600000L));
  out.add(@PKG@.GearChg.statusText() + "; your Charged Attack Damage total: " + (t == null ? 0 : t[@PKG@.GearDefs.I_CHG]) + "%");
  if (held == null || held.isEmpty()) out.add("Held: nothing - hold a weapon to see its charged steps");
  else {
    String id = held.getItemId();
    int sl = @PKG@.GearData.slotOf(id);
    if (sl == 2) out.add("Held: " + id + " (armor) - Charged Attack Damage " + (@PKG@.GearChg.canRoll(id, 2) ? "may roll on armor" : "does not roll (charged.on is off)"));
    else if (sl != 0 && sl != 1) out.add("Held: " + id + " - not a gear weapon (gear stats do not apply to its hits)");
    else {
      out.add("Held: " + id + " - " + @PKG@.GearChg.summary(id));
      out.add("  may roll Charged Attack Damage: " + (@PKG@.GearChg.canRoll(id, sl) ? "yes" : "no"));
    }
  }
  Object[] l = (Object[]) LAST.get(u);
  if (l == null) out.add("Last hit: none judged yet - probe " + (was ? "still on" : "on for 10 minutes") + ": hit something, then /gear charged again (/gear charged off ends it)");
  else out.add("Last hit (" + ((now - ((Long) l[0]).longValue()) / 1000L) + " s ago): " + (String) l[1]);
  return (String[]) out.toArray(new String[0]);
}""")
M(gchg, r"""
public static void setup(@JPLG@ pl) {
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearHandSys()); }
  catch (Throwable t) { @PKG@.Gear.warn("GearHandSys could not be registered - a single spear / spellbook throw gets no weapon stats and no charged flag: " + t); }
}""")

F(gstk, "public static final java.util.concurrent.ConcurrentHashMap SHOTS = new java.util.concurrent.ConcurrentHashMap();")
F(gstk, "public @QRY@ query;")
C(gstk, "public GearShotTrack() { super(); this.query = null; }")
M(gstk, r"""
public static void purge() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.GearShot r = (@PKG@.GearShot) it.next();
    if (r == null || now - r.at > %dL) it.remove();
  }
}""" % SHOT_PURGE_MS)
M(gstk, r"""
public static @PKG@.GearShot find(@CB@ buf, @REF@ pj) {
  if (pj == null || !pj.isValid() || SHOTS.isEmpty()) return null;
  @UUIDC@ idc = (@UUIDC@) buf.getComponent(pj, @UUIDC@.getComponentType());
  if (idc == null || idc.getUuid() == null) return null;
  return (@PKG@.GearShot) SHOTS.get(idc.getUuid());
}""")
M(gstk, r"""
public static @PKG@.GearShot liveBad(java.util.UUID u) {
  if (u == null || SHOTS.isEmpty()) return null;
  long now = System.currentTimeMillis();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.GearShot r = (@PKG@.GearShot) it.next();
    if (r != null && r.bad != null && u.equals(r.shooter) && now - r.at < %dL) return r;
  }
  return null;
}""" % SHOT_WINDOW_MS)
# exploit review 1: a projectile hit that reaches GearHitSys as a plain EntitySource (shortbow / crossbow arrows through
# DamageEntityInteraction) takes its weapon from the shooter's NEWEST live launch record in the shot window, never from the item
# in hand at landing (fire bow A, swap to stat-stick bow B mid-flight: B's stats no longer apply)
M(gstk, r"""
public static @PKG@.GearShot newest(java.util.UUID u) {
  if (u == null || SHOTS.isEmpty()) return null;
  long now = System.currentTimeMillis();
  @PKG@.GearShot best = null;
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.GearShot r = (@PKG@.GearShot) it.next();
    if (r == null || !u.equals(r.shooter) || now - r.at >= %dL) continue;
    if (best == null || r.at > best.at) best = r;
  }
  return best;
}""" % SHOT_WINDOW_MS)
# review of 0.2.1 finding 1: the damage step (DamageCalculator) of a hit's DamageSequence - the meta DamageEntityInteraction puts on the
# Damage before the event is dispatched (VERIFIED bytecode, the same read as GearCharged.judge); arrows through a plain EntitySource carry
# it; null = none (a legacy projectile, a hit without a damage step)
M(gstk, r"""
public static Object calcOf(@DMG@ d) {
  if (d == null) return null;
  try {
    Object so = ((@IMS@) d).getIfPresentMetaObject(@DCSYS@.DAMAGE_SEQUENCE);
    if (so instanceof @DSEQ@) return ((@DSEQ@) so).getDamageCalculator();
  } catch (Throwable t) { }
  return null;
}""")
# review of 0.2.1 finding 1: the shooter's live records (the window of pick) that may have fired a plain-EntitySource projectile hit whose
# damage step is calc. Since 0.2.1 the base multiplier depends on the weapon's K and level, so another live weapon's record must not
# decide an arrow (a Lv 40 staff record picked for a bow arrow gave x3.36 instead of x1.12; a newer Lv 13 shortbow record gave an Iron
# crossbow bolt x2.1). Kept: the records whose weapon's GearChg index (every damage step its interactions reach - the arrow's
# ProjectileHit chain included; calculators by identity) knows calc, plus every record whose weapon was NOT walked completely (an
# incomplete walk never rules a record out). No calc, fewer than two records, or no walked weapon knows calc even after GearChg's
# re-walk (at most every 30 s per item: assets reloaded; or the live calculator is not the walked object - UNVERIFIED in game) = every
# live record, the 0.2 rule. The same weapon at several levels / rolls stays ambiguous (they share calculators): pick then takes the
# weaker one and GearHit.weaponHit the smallest multiplier among them.
M(gstk, r"""
public static java.util.ArrayList cands(java.util.UUID u, Object calc) {
  java.util.ArrayList live = new java.util.ArrayList();
  if (u == null || SHOTS.isEmpty()) return live;
  long now = System.currentTimeMillis();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.GearShot r = (@PKG@.GearShot) it.next();
    if (r == null || !u.equals(r.shooter) || now - r.at >= %dL) continue;
    live.add(r);
  }
  if (calc == null || live.size() < 2) return live;
  for (int pass = 0; pass < 2; pass++) {
    java.util.ArrayList own = new java.util.ArrayList();
    boolean known = false;
    for (int i = 0; i < live.size(); i++) {
      @PKG@.GearShot r = (@PKG@.GearShot) live.get(i);
      String id = r.main == null || r.main.isEmpty() ? null : r.main.getItemId();
      Object[] e = null;
      if (id != null) e = pass == 0 ? @PKG@.GearChg.ensure(id) : @PKG@.GearChg.rewalk(id);
      if (e != null && @PKG@.GearChg.step(e, calc) != null) { own.add(r); known = true; }
      else if (!@PKG@.GearChg.walked(e)) own.add(r);
    }
    if (known) return own;
  }
  return live;
}""" % SHOT_WINDOW_MS)
# follow-up review 4: which live record a plain-EntitySource projectile hit belongs to. One record (or several with the same weapon:
# id + document + quality + durability) = the newest. Several with DIFFERENT weapons in the air: GearShot keeps no position, so the
# WEAKER one counts (lower sum of the totals it would give with this armor; a weapon that gives no stats at all is the weakest) -
# swapping to a stat stick mid-flight never pays. A blocked record still blocks: GearHitSys ORs every live bad flag (liveBad).
# Review of 0.2.1 finding 1: the rule runs over cands(u, calc) - the records of the weapon that owns the hit's damage step when the walk
# can tell (GearHitSys passes calcOf(d)); pick(u, arm) = cands(u, null) = every live record, exactly the 0.2 rule.
M(gstk, r"""
public static @PKG@.GearShot pickFor(java.util.UUID u, @IC@ arm, Object calc) {
  java.util.ArrayList live = cands(u, calc);
  @PKG@.GearShot best = null;
  for (int i = 0; i < live.size(); i++) {
    @PKG@.GearShot r = (@PKG@.GearShot) live.get(i);
    if (best == null || r.at > best.at) best = r;
  }
  if (live.size() < 2) return best;
  String f0 = @PKG@.GearForge.fp(best.main);
  boolean same = true;
  for (int i = 0; i < live.size(); i++) if (!f0.equals(@PKG@.GearForge.fp(((@PKG@.GearShot) live.get(i)).main))) same = false;
  if (same) return best;
  @PKG@.GearShot weak = null;
  long ws = 0L;
  for (int i = 0; i < live.size(); i++) {
    @PKG@.GearShot r = (@PKG@.GearShot) live.get(i);
    boolean[] ok = new boolean[1];
    int[] t = @PKG@.GearStats.totals(u, r.main, arm, ok, true);
    long s = 0L;
    for (int k = 0; k < t.length; k++) s = s + (long) t[k];
    if (!ok[0]) s = Long.MIN_VALUE;
    if (weak == null || s < ws || (s == ws && r.at > weak.at)) { weak = r; ws = s; }
  }
  return weak;
}""")
M(gstk, "public static @PKG@.GearShot pick(java.util.UUID u, @IC@ arm) { return pickFor(u, arm, null); }")
# review of 0.1.2 finding 1: the distinct item ids of the shooter's live records (the same window as pick) - GearCharged.judge looks a
# picked projectile hit's damage step up in all of them (pick may have chosen another weapon's record than the one that fired it)
M(gstk, r"""
public static String[] liveIds(java.util.UUID u) {
  if (u == null || SHOTS.isEmpty()) return new String[0];
  long now = System.currentTimeMillis();
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = SHOTS.values().iterator();
  while (it.hasNext()) {
    @PKG@.GearShot r = (@PKG@.GearShot) it.next();
    if (r == null || !u.equals(r.shooter) || now - r.at >= %dL || r.main == null || r.main.isEmpty()) continue;
    String id = r.main.getItemId();
    if (id != null && !out.contains(id)) out.add(id);
  }
  return (String[]) out.toArray(new String[0]);
}""" % SHOT_WINDOW_MS)
# review of 0.2.1 finding 1: the smallest base multiplier (GearBase.weaponMult - never the spell one: a picked hit is an arrow) among the
# records that may have fired a picked hit (cands, the same list pickFor chose from). GearHit.weaponHit clamps the chosen record's
# multiplier to it: when the damage step names its weapon nothing changes (one candidate, or the same weapon twice); when it cannot
# (no step, an unknown step, the same item at two levels) no other live weapon's K / level can raise the hit. -1 = fewer than two
# candidates (no clamp).
M(gstk, r"""
public static double minMult(java.util.UUID u, Object calc) {
  java.util.ArrayList c = cands(u, calc);
  if (c.size() < 2) return -1.0;
  double lo = -1.0;
  for (int i = 0; i < c.size(); i++) {
    double m = @PKG@.GearBase.weaponMult(((@PKG@.GearShot) c.get(i)).main, false);
    if (lo < 0.0 || m < lo) lo = m;
  }
  return lo;
}""")
M(gstk, r"""
public @QRY@ getQuery() {
  if (this.query == null) {
    this.query = @QRY@.and(new @QRY@[] { (@QRY@) @TC@.getComponentType(), @QRY@.or(new @QRY@[] { (@QRY@) @LPC@.getComponentType(), (@QRY@) @SPP@.getComponentType() }) });
  }
  return this.query;
}""")
M(gstk, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN) return;
    java.util.UUID creator = null;
    @SPP@ sp = (@SPP@) buf.getComponent(ref, @SPP@.getComponentType());
    if (sp != null) creator = sp.getCreatorUuid();
    if (creator == null) {
      @LPC@ lp = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());
      if (lp != null) creator = lp.getCreatorUuid();
    }
    if (creator == null) return;
    @UUIDC@ idc = (@UUIDC@) buf.getComponent(ref, @UUIDC@.getComponentType());
    if (idc == null || idc.getUuid() == null) return;
    @REF@ sh = ((@EST@) buf.getExternalData()).getRefFromUUID(creator);
    if (sh == null || !sh.isValid()) return;
    @PR@ pr = (@PR@) buf.getComponent(sh, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @IS@ mh = @INVC@.getItemInHand(buf, sh);
    @UTIL@ ut = (@UTIL@) buf.getComponent(sh, @UTIL@.getComponentType());
    @IS@ ui = ut == null ? null : ut.getActiveItem();
    // 0.1.2 (verifier): a legacy projectile (spear throw, spell orb) names its ProjectileId; a single spear / spellbook is already
    // used up here, so the hand snapshot supplies the stack that launched it (GearHand.pick: the live hand always wins when it can)
    String pid = null;
    @LPC@ lpj = (@LPC@) buf.getComponent(ref, @LPC@.getComponentType());
    if (lpj != null) pid = lpj.getProjectileAssetName();
    boolean snap = false;
    if (pid != null) {
      @IS@ pk = @PKG@.GearHand.pick(u, mh, pid, System.currentTimeMillis());
      if (pk != mh) { mh = pk; snap = true; }
    }
    String[] bad = @PKG@.GearHit.judge(u, mh, false);
    if (bad == null) bad = @PKG@.GearHit.judge(u, ui, true);
    if (SHOTS.size() > %d) purge();
    @PKG@.GearShot rec = new @PKG@.GearShot(u, mh, ui, bad);
    rec.pid = pid;
    rec.snap = snap;
    rec.charged = pid != null && mh != null && !mh.isEmpty() && @PKG@.GearChg.launchCode(mh.getItemId(), pid) == 1;
    SHOTS.put(idc.getUuid(), rec);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("shottrack", "gear shot tracker failed: " + t); }
}""" % SHOT_PURGE_AT)
M(gstk, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (SHOTS.isEmpty()) return;
    @UUIDC@ idc = (@UUIDC@) buf.getComponent(ref, @UUIDC@.getComponentType());
    if (idc != null && idc.getUuid() != null) SHOTS.remove(idc.getUuid());
  } catch (Throwable t) { }
}""")

# ================================================================= GearArmor: the copied engine formula + inactive armor (spec 3.5)
# reduce() = DamageSystems$ArmorDamageReduction.handle after getResistanceModifiers, instruction for instruction (bytecode 2026-09-28):
#   bypass or empty map -> unchanged; r = map[cause]; none -> unchanged; a = max(0, a - flat); a *= max(0, 1 - mult); then the same
#   for every inheritedParentId link until a link is missing. The bare-JVM harness proves reduce(engine map) == the engine's own
#   handle() on 50 random armor sets.
M(garm, r"""
public static float reduce(float amount, @DCS@ cause, java.util.Map m) {
  if (cause == null || cause.doesBypassResistances() || m == null || m.isEmpty()) return amount;
  @ARMR@ r = (@ARMR@) m.get(cause);
  if (r == null) return amount;
  float a = Math.max(0.0f, amount - r.flatModifier);
  a = a * Math.max(0.0f, 1.0f - r.multiplierModifier);
  while (r.inheritedParentId != null) {
    r = (@ARMR@) m.get(r.inheritedParentId);
    if (r == null) break;
    a = Math.max(0.0f, a - r.flatModifier);
    a = a * Math.max(0.0f, 1.0f - r.multiplierModifier);
  }
  return a;
}""")
# cur = the amount after the engine's full-armor pass (plus whatever other mods did in between); full / act = the copied formula on
# the pre-armor amount with every piece / only the active pieces. Nothing in between (the normal case): exactly act. Another mod
# multiplied in between: its factor is kept (cur x act / full).
M(garm, r"""
public static float correct(float cur, float full, float act) {
  if (full > 0.0001f) return cur * act / full;
  return act + (cur > 0.0f ? cur : 0.0f);
}""")
# spec 3.5: an armor piece gives no stats while unidentified (always) or under its gate level (part.gate); gathering kinds and
# unreadable data never count as inactive
M(garm, r"""
public static boolean inactive(java.util.UUID u, @IS@ s) {
  if (s == null || s.isEmpty()) return false;
  String id = s.getItemId();
  if (@PKG@.GearData.slotOf(id) != 2) return false;
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  if (d == null || !@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kind(d))) return false;
  if (!@PKG@.GearData.identified(d)) return true;
  if (!@PKG@.GearCfg.PART_GATE) return false;
  Object[] c = @PKG@.GearGate.check(u, id, d, @PKG@.GearLevel.level(id, d));
  return !((Boolean) c[0]).booleanValue();
}""")
# the gear.armorWarn line for an inactive piece (spec 3.5: "Your Mithril Chestplate gives no stats until Archery 40 (you: 12)"); null = active
M(garm, r"""
public static String why(java.util.UUID u, @IS@ s) {
  if (!inactive(u, s)) return null;
  String id = s.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  String name = @PKG@.GearView.nameText(id, d);
  if (!@PKG@.GearData.identified(d)) return "Your " + name + " gives no stats until you identify it" + @PKG@.GearCfg.idHow();
  int need = @PKG@.GearLevel.level(id, d);
  Object[] c = @PKG@.GearGate.check(u, id, d, need);
  int st = ((Integer) c[5]).intValue();
  if (st == 1) return "Your " + name + " gives no stats until you pick a class (it needs " + c[1] + " " + need + ")";
  if (st == 2) return "Your " + name + " gives no stats - skills are unavailable (it needs level " + need + ")";
  return "Your " + name + " gives no stats until " + c[1] + " " + need + " (you: " + c[3] + ")";
}""")
M(garm, r"""
public static boolean hasInactive(java.util.UUID u, @IC@ armor) {
  if (armor == null) return false;
  for (int i = 0; i < armor.getCapacity(); i++) if (inactive(u, armor.getItemStack((short) i))) return true;
  return false;
}""")
# a temporary container with only the active pieces (non-gear items stay): what the engine formula sees for "only these are worn"
M(garm, r"""
public static @SIC@ activeCopy(java.util.UUID u, @IC@ armor) {
  short cap = armor.getCapacity();
  @SIC@ c = new @SIC@(cap);
  for (int i = 0; i < cap; i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (s == null || s.isEmpty() || inactive(u, s)) continue;
    c.setItemStackForSlot((short) i, s);
  }
  return c;
}""")
# spec 3.5 part 2: per stat index, the ADDITIVE stat modifiers of a piece, the way StatModifiersManager.computeStatModifiers adds
# them (VERIFIED bytecode 2026-09-29): every StaticModifier of the piece's ItemArmor.getStatModifiers() summed per calculation type
# (the engine puts the sum under Modifier target MAX, whatever the asset's own target), amount x (float) BrokenPenalties.getArmor(0.0)
# when the stack isBroken() (engine review 2; Default.json 0.75). statMods = the Int2ObjectMap (a java.util.Map of StaticModifier[]).
M(garm, r"""
public static void addSums(Object statMods, boolean broken, float f, java.util.HashMap out, String id) {
  if (!(statMods instanceof java.util.Map)) return;
  java.util.Iterator e = ((java.util.Map) statMods).entrySet().iterator();
  while (e.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) e.next();
    if (!(en.getKey() instanceof Number) || !(en.getValue() instanceof Object[])) continue;
    Integer k = Integer.valueOf(((Number) en.getKey()).intValue());
    Object[] xs = (Object[]) en.getValue();
    float sum = 0.0f;
    for (int j = 0; j < xs.length; j++) {
      if (!(xs[j] instanceof @SMO@)) continue;
      @SMO@ m = (@SMO@) xs[j];
      if (m.getCalculationType() == @CAL@.ADDITIVE) {
        float a = m.getAmount();
        if (broken) a = a * f;
        sum = sum + a;
      } else if (id != null) @PKG@.Gear.warnOnce("lockcalc:" + id, id + " has a non-additive armor stat modifier - under-level armor keeps it (spec 3.5 part 4)");
    }
    if (sum == 0.0f) continue;
    Object prev = out.get(k);
    out.put(k, Float.valueOf((prev instanceof Float ? ((Float) prev).floatValue() : 0.0f) + sum));
  }
}""")
M(garm, r"""
public static void addPiece(@IS@ s, float f, java.util.HashMap out, boolean warn) {
  if (s == null || s.isEmpty()) return;
  @ITM@ it = @PKG@.Gear.item(s.getItemId());
  @IAR@ a = it == null ? null : it.getArmor();
  Object sm = a == null ? null : a.getStatModifiers();
  boolean br = false;
  try { br = s.isBroken(); } catch (Throwable t) { br = false; }
  addSums(sm, br, f, out, warn ? s.getItemId() : null);
}""")
# 0.2.1 (stage 3) the per-stack Health delta of one worn piece: (the asset's own Health - the per-stack target) x the broken factor, for an
# ACTIVE SkyyGear armor piece of an enforced kind; 0 for everything else (an inactive piece is cancelled whole by the native part below)
M(garm, r"""
public static float healthDelta(java.util.UUID u, @IS@ s, float f) {
  if (s == null || s.isEmpty()) return 0.0f;
  String id = s.getItemId();
  if (@PKG@.GearData.slotOf(id) != 2) return 0.0f;
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  if (d == null || !@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kind(d)) || inactive(u, s)) return 0.0f;
  float[] tg = @PKG@.GearBase.armorTarget(id, d);
  if (tg == null) return 0.0f;
  boolean br = false;
  try { br = s.isBroken(); } catch (Throwable t) { br = false; }
  float dl = @PKG@.GearBase.nativeHealth(@PKG@.Gear.item(id)) - tg[0];
  return br ? dl * f : dl;
}""")
# what the lock modifier skyygear_lock_<stat> holds (Integer stat index -> Float, SIGNED - follow-up review 10; the modifier = -sum):
#  - the inactive pieces' whole native stats (level.armorNative: under-level / unidentified armor gives nothing, spec 3.5 part 2), and
#  - 0.2.1 (spec 3.5 item 5, "through the existing lock plumbing"): for every ACTIVE SkyyGear piece its Health delta (native - per-stack
#    target): positive = part of the native Health is cancelled, NEGATIVE = the modifier ADDS Health (a Lv 10 Copper chestplate: 9 - 18 =
#    -9 -> +9). GearFx.plan keeps the engine-review-1 rule for both signs: max Health only ever goes DOWN in the 1 s tick once the engine's
#    own Armor modifier is synced (never eats current Health); going up applies at once. So the bonus comes on equip at once and leaves
#    within a second of unequip (after the engine dropped the piece's own Health) - one keyed modifier, so it never stacks on re-equip.
M(garm, r"""
public static java.util.HashMap lockSums(java.util.UUID u, @IC@ armor, float f) {
  java.util.HashMap out = new java.util.HashMap();
  if (armor == null) return out;
  boolean nat = @PKG@.GearCfg.ARMOR_NATIVE;
  boolean lv = @PKG@.GearBase.armorOn();
  Integer hk = null;
  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (inactive(u, s)) { if (nat) addPiece(s, f, out, true); continue; }
    if (!lv) continue;
    float dh = healthDelta(u, s, f);
    if (dh == 0.0f) continue;
    if (hk == null) hk = Integer.valueOf(@DST@.getHealth());
    Object prev = out.get(hk);
    out.put(hk, Float.valueOf((prev instanceof Float ? ((Float) prev).floatValue() : 0.0f) + dh));
  }
  return out;
}""")
# every piece = what the engine's own "Armor" modifier holds once it has recalculated this container (engine review 1: the sync check)
M(garm, r"""
public static java.util.HashMap fullSums(@IC@ armor, float f) {
  java.util.HashMap out = new java.util.HashMap();
  if (armor == null) return out;
  for (int i = 0; i < armor.getCapacity(); i++) addPiece(armor.getItemStack((short) i), f, out, false);
  return out;
}""")
# the world's BrokenPenalties armor factor (the engine's own call: getGameplayConfig().getItemDurabilityConfig().getBrokenPenalties()
# .getArmor(0.0)); 1 when it cannot be read (logged once)
M(garm, r"""
public static float brokenFactor(Object ext) {
  try {
    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : (ext instanceof @WLD@ ? (@WLD@) ext : null);
    if (w != null) return (float) w.getGameplayConfig().getItemDurabilityConfig().getBrokenPenalties().getArmor(0.0);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("broken", "could not read the broken-armor penalty - broken armor locks count in full: " + t); }
  return 1.0f;
}""")
# ---- 0.2.1 (stage 3, spec 3.5 item 6): PER-STACK RESISTANCE. The engine scales a broken piece's resistance entry by (1 - BrokenPenalties
# .getWeapon(0)) when penalties apply (VERIFIED bytecode ArmorDamageReduction.calculateResistanceEntryModifications - getWeapon, not
# getArmor); 1 when the world is unknown
M(garm, r"""
public static float resBroken(@WLD@ w) {
  try {
    if (w != null) return (float) (1.0 - w.getGameplayConfig().getItemDurabilityConfig().getBrokenPenalties().getWeapon(0.0));
  } catch (Throwable t) { }
  return 1.0f;
}""")
# the per-stack resistance change of one worn piece against a cause id: per-stack target - the asset's own multiplier, for an ACTIVE
# SkyyGear armor piece of an enforced kind (0 otherwise; inactive pieces lose their resistance through activeCopy instead)
M(garm, r"""
public static float resDelta(java.util.UUID u, @IS@ s, String cause) {
  if (s == null || s.isEmpty()) return 0.0f;
  String id = s.getItemId();
  if (@PKG@.GearData.slotOf(id) != 2) return 0.0f;
  @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
  if (d == null || !@PKG@.GearDefs.enforcedKind(@PKG@.GearData.kind(d)) || inactive(u, s)) return 0.0f;
  float[] tg = @PKG@.GearBase.armorTarget(id, d);
  if (tg == null) return 0.0f;
  return tg[1] - @PKG@.GearBase.assetRes(@PKG@.Gear.item(id), cause);
}""")
# GearHitSys keeps the pre-armor amount for a player victim when this is true (base.armorOn and a worn piece whose per-stack resistance
# differs from its asset)
M(garm, r"""
public static boolean hasResDelta(java.util.UUID u, @IC@ armor) {
  if (armor == null || !@PKG@.GearBase.armorOn()) return false;
  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    if (Math.abs(resDelta(u, s, "Physical")) > 0.000001f || Math.abs(resDelta(u, s, "Projectile")) > 0.000001f) return true;
  }
  return false;
}""")
# add a multiplier delta to the map entry of one cause id; a set without that entry gets a new ArmorResistanceModifiers keyed by the
# cause asset, with the parent link the engine would give it (inheritedParentId = the asset of getInherits())
M(garm, r"""
public static void addRes(java.util.Map m, String cause, float delta) {
  if (m == null || delta == 0.0f) return;
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    if (en.getKey() instanceof @DCS@ && cause.equals(((@DCS@) en.getKey()).getId()) && en.getValue() instanceof @ARMR@) {
      @ARMR@ r0 = (@ARMR@) en.getValue();
      r0.multiplierModifier = r0.multiplierModifier + delta;
      return;
    }
  }
  Object c = null;
  try { c = @DCS@.getAssetMap().getAsset(cause); } catch (Throwable t) { c = null; }
  if (!(c instanceof @DCS@)) return;
  @ARMR@ r = new @ARMR@();
  r.multiplierModifier = delta;
  String inh = ((@DCS@) c).getInherits();
  if (inh != null) {
    Object pc = null;
    try { pc = @DCS@.getAssetMap().getAsset(inh); } catch (Throwable t2) { pc = null; }
    if (pc instanceof @DCS@) r.inheritedParentId = (@DCS@) pc;
  }
  m.put(c, r);
}""")
# the active SkyyGear pieces' per-stack Physical / Projectile resistance on top of the engine's map (m = a map getResistanceModifiers just
# built for this call; a broken piece's delta gets the engine's own broken factor when penalties apply)
M(garm, r"""
public static void levelRes(java.util.UUID u, @IC@ armor, java.util.Map m, boolean pen, @WLD@ w) {
  if (armor == null || m == null || !@PKG@.GearBase.armorOn()) return;
  float dp = 0.0f;
  float dj = 0.0f;
  float bf = -1.0f;
  for (int i = 0; i < armor.getCapacity(); i++) {
    @IS@ s = armor.getItemStack((short) i);
    float a = resDelta(u, s, "Physical");
    float b = resDelta(u, s, "Projectile");
    if (a == 0.0f && b == 0.0f) continue;
    boolean br = false;
    try { br = s.isBroken(); } catch (Throwable t) { br = false; }
    if (pen && br) {
      if (bf < 0.0f) bf = resBroken(w);
      a = a * bf;
      b = b * bf;
    }
    dp = dp + a;
    dj = dj + b;
  }
  addRes(m, "Physical", dp);
  addRes(m, "Projectile", dj);
}""")
# GearArmorSys (AFTER the engine's ArmorDamageReduction): cur = the engine's result with every worn piece at its ASSET values; full = our
# copy of that formula on the pre-armor amount; act = only the active pieces (level.armorNative) with the per-stack resistance on top
# (0.2.1 base.armorOn); the result cur x act / full keeps another mod's factor in between (SkyyMobs' level damage may run after
# GearHitSys kept the pre-armor amount - vanilla armor is multiplier-only, so the ratio is exact either way)
M(garm, r"""
public static float fix(java.util.UUID vu, float pre, float cur, @DCS@ cause, @IC@ full, @WLD@ w, boolean pen, @ECC@ ecc) {
  boolean nat = @PKG@.GearCfg.ARMOR_NATIVE;
  boolean lv = @PKG@.GearBase.armorOn();
  if ((!nat && !lv) || full == null) return cur;
  float f = reduce(pre, cause, @ADRC@.getResistanceModifiers(w, full, pen, ecc));
  @IC@ src = nat ? (@IC@) activeCopy(vu, full) : full;
  java.util.Map am = @ADRC@.getResistanceModifiers(w, src, pen, ecc);
  if (lv) levelRes(vu, full, am, pen, w);
  float a = reduce(pre, cause, am);
  return correct(cur, f, a);
}""")

# ================================================================= GearTag: unidentified tagging (spec 5.5, 5.6) + death / chest marks
# MARKS: world name -> ArrayList of double[]{x, y, z} = where an NPC drops its death items THIS tick (read and written only on that
# world's thread). CHEST: chest block-entity Ref (identity) -> its drop list, between the BEFORE-Stash and the AFTER-Stash system.
F(gtag, "public static final java.util.concurrent.ConcurrentHashMap MARKS = new java.util.concurrent.ConcurrentHashMap();")
F(gtag, "public static final java.util.IdentityHashMap CHEST = new java.util.IdentityHashMap();")
F(gtag, "public static final java.util.concurrent.atomic.AtomicLong MOB_TAGS = new java.util.concurrent.atomic.AtomicLong();")
F(gtag, "public static final java.util.concurrent.atomic.AtomicLong CHEST_TAGS = new java.util.concurrent.atomic.AtomicLong();")
M(gtag, r"""
public static String key(Object ext) {
  try {
    if (ext instanceof @EST@) { @WLD@ w = ((@EST@) ext).getWorld(); return w == null ? "?" : w.getName(); }
    if (ext instanceof @CHS@) { @WLD@ w2 = ((@CHS@) ext).getWorld(); return w2 == null ? "?" : w2.getName(); }
  } catch (Throwable t) { }
  return "?";
}""")
M(gtag, "public static void clear(String k) { if (k != null) MARKS.remove(k); }")
M(gtag, r"""
public static void mark(String k, double x, double y, double z) {
  if (k == null) return;
  java.util.ArrayList l = (java.util.ArrayList) MARKS.get(k);
  if (l == null) { l = new java.util.ArrayList(); MARKS.put(k, l); }
  if (l.size() < 4096) l.add(new double[] { x, y, z });
}""")
M(gtag, r"""
public static boolean any(String k) {
  Object o = k == null ? null : MARKS.get(k);
  return o instanceof java.util.ArrayList && !((java.util.ArrayList) o).isEmpty();
}""")
# within 2 blocks of a mark (the drops spawn exactly at the NPC position + (0, 1, 0), VERIFIED)
M(gtag, r"""
public static boolean near(String k, double x, double y, double z) {
  Object o = k == null ? null : MARKS.get(k);
  if (!(o instanceof java.util.ArrayList)) return false;
  java.util.ArrayList l = (java.util.ArrayList) o;
  for (int i = 0; i < l.size(); i++) {
    double[] p = (double[]) l.get(i);
    double dx = p[0] - x;
    double dy = p[1] - y;
    double dz = p[2] - z;
    if (dx * dx + dy * dy + dz * dz <= 4.0) return true;
  }
  return false;
}""")
# the tag: gear with NO document only (a stack that ever sat in a player inventory or was thrown by a player carries one, spec 1.5 /
# 10), rarity from odds.mob (col 1, src drop) or odds.chest (col 2, src chest), unidentified, no modifiers stored (5.6)
M(gtag, r"""
public static @IS@ unid(@IS@ s, int col) {
  if (s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return s;
  if (col == 1 && !@PKG@.GearCfg.PART_DROPS) return s;
  if (col == 2 && !@PKG@.GearCfg.PART_CHESTS) return s;
  if (col != 1 && col != 2) return s;
  return @PKG@.GearData.put(s, @PKG@.GearRoll.unidDoc(id, col, col == 1 ? "drop" : "chest"), null);
}""")
# exploit review 2: a stack of several undocumented gear items in a fresh loot chest is split into empty slots of the SAME chest
# first (one unidentified document and one rarity roll per item); what does not fit stays one stack with one document (unidentified
# documents carry no modifiers: Identify takes one item off the stack and rolls it, follow-up review 3). Mob drops keep one document
# per dropped stack (splitting an item entity would mean spawning new entities). Follow-up review 8: a failed split is caught here
# (the stack is then tagged whole) so one bad slot never stops the chest.
M(gtag, r"""
public static int tagContainer(@IC@ c, String where) {
  if (c == null) return 0;
  int n = 0;
  @IC@[] self = new @IC@[] { c };
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ s0 = c.getItemStack((short) i);
    if (@PKG@.GearCfg.PART_CHESTS && s0 != null && !s0.isEmpty() && s0.getQuantity() > 1 && @PKG@.GearData.isGear(s0.getItemId()) && !@PKG@.GearData.hasAnyDoc(s0.getMetadata())) {
      try { n = n + @PKG@.GearStamp.split(c, i, self, self, null, 2, 64, 0, null); }
      catch (Throwable t) { @PKG@.Gear.warnOnce("chestsplit:" + s0.getItemId(), "loot chest split of " + s0.getItemId() + " failed (the stack is tagged whole): " + t); }
    }
    @IS@ s = c.getItemStack((short) i);
    @IS@ ns = unid(s, 2);
    if (ns == s || ns == null) continue;
    c.setItemStackForSlot((short) i, ns);
    n++;
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID chest " + ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]) + " " + where);
  }
  if (n > 0) CHEST_TAGS.addAndGet((long) n);
  return n;
}""")
M(gtag, r"""
public static synchronized void chestMark(Object ref, String dl) {
  if (ref == null) return;
  if (CHEST.size() > 1024) CHEST.clear();
  CHEST.put(ref, dl == null ? "" : dl);
}""")
M(gtag, "public static synchronized String chestTake(Object ref) { return ref == null ? null : (String) CHEST.remove(ref); }")

# ================================================================= GearFx: per-player stat effects (spec 3.5 part 2, 4.2), helpers
# REGEN: UUID -> long[]{lastMs, accumulatedMs}; LEECH: UUID -> double[]{heal owed, last payout ms}; MANA: UUID -> double[]{mana owed,
# last Mana Steal ms}; WARNED: UUID -> HashSet of "slot:id:doc" of the armor pieces already announced inactive; MOVE: skyymove state.
# LOCKED: UUID -> Object[] of the armor stacks (identity) when a non-zero lock was last written (GearLockSys only looks at those
# players); BLOCKED: UUID -> int[]{seconds a lock raise waited for the engine}; PRIMED: UUID -> TRUE once GearLockSys looked for lock
# modifiers saved with the player (follow-up review 5: the EntityStatValue codec saves Modifiers, so a lock can come back from disk
# before LOCKED knows it; cleared at every PlayerReady = join / world switch)
for _f in ("REGEN", "LEECH", "MANA", "WARNED", "MOVE", "LOCKED", "BLOCKED", "PRIMED"):
    F(gfx, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
F(gfx, "public static volatile String AKEY = null;")
F(gfx, 'public static final String LOCK = "%s";' % LOCK_PREFIX)
F(gfx, 'public static final String LIMITS = %s;' % jstr(", ".join(ARMOR_LIMITS)[:1500]))
# Life Steal: lsteal % of the landed damage is owed and paid out once per steal.windowS (spec 4.2, the lock-20 shape)
M(gfx, r"""
public static void leech(java.util.UUID u, double heal) {
  if (u == null || !(heal > 0.0)) return;
  double[] v = (double[]) LEECH.get(u);
  if (v == null) { v = new double[] { 0.0, 0.0 }; LEECH.put(u, v); }
  v[0] = v[0] + heal;
}""")
# Mana Steal: when a hit lands and steal.windowS passed since the last payout, v mana is owed (paid by the next GearTick)
M(gfx, r"""
public static void manaSteal(java.util.UUID u, int v) {
  if (u == null || v <= 0) return;
  long now = System.currentTimeMillis();
  double[] m = (double[]) MANA.get(u);
  if (m == null) { m = new double[] { 0.0, 0.0 }; MANA.put(u, m); }
  if ((double) now - m[1] < (double) @PKG@.GearCfg.STEAL_S * 1000.0) return;
  m[1] = (double) now;
  m[0] = m[0] + (double) v;
}""")
# never above max, never on a dead player (Health <= 0)
M(gfx, r"""
public static void add(@ESM@ m, int idx, float amt, boolean health) {
  if (m == null || idx < 0 || !(amt > 0.0f)) return;
  @ESV@ v = m.get(idx);
  if (v == null) return;
  float cur = v.get();
  float max = v.getMax();
  if (health && cur <= 0.0f) return;
  if (cur >= max) return;
  float a = amt;
  if (cur + a > max) a = max - cur;
  m.addStatValue(idx, a);
}""")
# ---- engine review 1: the lock must never eat the CURRENT value. EntityStatValue.putModifier / removeModifier recompute min / max and
# clamp the value at once (VERIFIED bytecode 2026-09-29: computeModifiers ends with value = MathUtil.clamp(value, min, max)), and the
# engine adds a piece's own +sum only at EntityStatsSystems$Recalculate (StatModifiersManager.applyStatModifiers, key
# CalculationType.ADDITIVE.createKey("Armor")). So:
#  - SHRINKING a lock (or removing it) only raises max: always safe, done at once wherever the want drops (GearFxInvSys on an armor
#    change, GearLockSys every tick BEFORE Recalculate, the 1 s tick) - an unequipped piece's lock is gone before the engine drops
#    that piece's +sum;
#  - GROWING a lock lowers max: only in the 1 s tick (raise = true) and only when the engine's own Armor modifier for that stat
#    already equals the container's full sum (the piece's +sum is in), so the lock lands on the final max and the clamp can only
#    remove value above the new max - what vanilla does when a piece with less Health goes on. Not synced yet: wait (next second).
# Follow-up review 10: have / want are SIGNED sums (the lock modifier = -sum): a negative armor sum (a piece with -5 Health) is
# cancelled too. Its cancel (+5) raises max, so it is applied at once like any shrink; taking it away again lowers max, so that
# waits for the tick + the synced engine like any growth. plan() is the same rule for both signs: a smaller want is always safe.
M(gfx, r"""
public static float plan(float have, float want, boolean raise, float engine, float full) {
  if (want <= have) return want;
  if (!raise) return have;
  if (Math.abs(engine - full) > 0.01f) return have;
  return want;
}""")
M(gfx, r"""
public static String armorKey() {
  String k = AKEY;
  if (k == null) { k = @CAL@.ADDITIVE.createKey("Armor"); AKEY = k; }
  return k;
}""")
# the amount of the engine's own ADDITIVE "Armor" MAX modifier on stat i (0 = none)
M(gfx, r"""
public static float engineArmor(@ESM@ m, int i) {
  try {
    @MODF@ x = m.getModifier(i, armorKey());
    if (x instanceof @SMO@) return ((@SMO@) x).getAmount();
  } catch (Throwable t) { }
  return 0.0f;
}""")
# the signed armor sum a lock modifier cancels now (the modifier holds -sum; 0 = none)
M(gfx, r"""
public static float lockNow(@MODF@ cur) {
  if (cur instanceof @SMO@) return -((@SMO@) cur).getAmount();
  return 0.0f;
}""")
# follow-up review 5: does this stat map carry any skyygear_lock_ modifier (e.g. saved with the player)?
M(gfx, r"""
public static boolean hasLock(@ESM@ m) {
  if (m == null) return false;
  int n = m.size();
  for (int i = 0; i < n; i++) {
    try { if (m.get(i) != null && m.getModifier(i, LOCK + @PKG@.GearView.statName(i)) != null) return true; } catch (Throwable t) { }
  }
  return false;
}""")
M(gfx, r"""
public static Object[] snapshot(@IC@ armor) {
  if (armor == null) return new Object[0];
  Object[] o = new Object[armor.getCapacity()];
  for (int i = 0; i < o.length; i++) o[i] = armor.getItemStack((short) i);
  return o;
}""")
M(gfx, r"""
public static boolean sameStacks(Object[] snap, @IC@ armor) {
  if (snap == null || armor == null) return snap == null && armor == null;
  if (snap.length != armor.getCapacity()) return false;
  for (int i = 0; i < snap.length; i++) if (snap[i] != armor.getItemStack((short) i)) return false;
  return true;
}""")
# spec 3.5 part 2: one StaticModifier(MAX, ADDITIVE, -sum) per stat under skyygear_lock_<stat id>, removed at 0; only written when it
# changes; each amount through plan() (signed: follow-up review 10). want = GearArmor.lockSums (Integer stat index -> Float); full =
# GearArmor.fullSums (raise only). Follow-up review 6: a raise that waited 3 ticks in a row for the engine schedules the engine's own
# Recalculate (StatModifiersManager.scheduleRecalculate, public, VERIFIED: it only sets the flag EntityStatsSystems$Recalculate
# reads) and the next tick checks again; again every 10 s while it keeps waiting; the 30 s WARN stays.
M(gfx, r"""
public static void locks(java.util.UUID u, @ESM@ m, java.util.HashMap want, java.util.HashMap full, @IC@ armor, boolean raise) {
  if (m == null) return;
  int n = m.size();
  boolean any = false;
  boolean waited = false;
  for (int i = 0; i < n; i++) {
    @ESV@ v = null;
    try { v = m.get(i); } catch (Throwable t) { v = null; }
    if (v == null) continue;
    String key = LOCK + @PKG@.GearView.statName(i);
    Object w = want == null ? null : want.get(Integer.valueOf(i));
    float amt = w instanceof Float ? ((Float) w).floatValue() : 0.0f;
    @MODF@ cur = m.getModifier(i, key);
    float have = lockNow(cur);
    float fl = 0.0f;
    if (full != null) { Object fo = full.get(Integer.valueOf(i)); fl = fo instanceof Float ? ((Float) fo).floatValue() : 0.0f; }
    float next = plan(have, amt, raise && full != null, engineArmor(m, i), fl);
    if (Math.abs(next - amt) > 0.0001f) waited = true;
    if (Math.abs(next) <= 0.0001f) { if (cur != null) m.removeModifier(i, key); continue; }
    any = true;
    @SMO@ nm = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, -next);
    if (cur != null && cur.equals(nm)) continue;
    m.putModifier(i, key, nm);
  }
  if (u == null) return;
  if (any) LOCKED.put(u, snapshot(armor));
  else LOCKED.remove(u);
  if (!raise) return;
  if (!waited) { BLOCKED.remove(u); return; }
  int[] b = (int[]) BLOCKED.get(u);
  if (b == null) { b = new int[1]; BLOCKED.put(u, b); }
  b[0] = b[0] + 1;
  if (b[0] % 10 == 3) {
    try { m.getStatModifiersManager().scheduleRecalculate(); }
    catch (Throwable t) { @PKG@.Gear.warnOnce("lockrecalc", "could not ask the engine to recalculate armor stats: " + t); }
  }
  if (b[0] == 30) @PKG@.Gear.warnOnce("lockwait:" + u, "an under-level armor lock waited 30 s for the engine's own armor stats (player " + u + ", a Recalculate was requested) - the piece keeps its Health until they match");
}""")
# lower-only pass (GearFxInvSys, GearLockSys): the want of the container as it is now, never a raise
M(gfx, r"""
public static void lowerNow(java.util.UUID u, @ESM@ m, @IC@ armor, float f) {
  if (m == null) return;
  java.util.HashMap want = armor != null ? @PKG@.GearArmor.lockSums(u, armor, f) : new java.util.HashMap();
  locks(u, m, want, null, armor, false);
}""")
# spec 3.5: one chat line each time a piece becomes inactive (gear.armorWarn gates only the line)
M(gfx, r"""
public static void warnLines(@PR@ pr, java.util.UUID u, @IC@ armor) {
  java.util.HashSet now = new java.util.HashSet();
  java.util.ArrayList lines = new java.util.ArrayList();
  java.util.HashSet old = (java.util.HashSet) WARNED.get(u);
  if (armor != null) {
    for (int i = 0; i < armor.getCapacity(); i++) {
      @IS@ s = armor.getItemStack((short) i);
      String why = @PKG@.GearArmor.why(u, s);
      if (why == null) continue;
      @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
      String k = i + ":" + s.getItemId() + ":" + (d == null ? 0 : d.toJson().hashCode());
      now.add(k);
      if (old == null || !old.contains(k)) lines.add(why);
    }
  }
  WARNED.put(u, now);
  if (lines.isEmpty() || pr == null || !@PKG@.Gear.notifyOn(u, "gear.armorWarn")) return;
  for (int i = 0; i < lines.size(); i++) pr.sendMessage(@MSG@.raw("[Gear] " + (String) lines.get(i)).color(@PKG@.GearDefs.C_GOLD));
}""")
# the armor part (on an armor-container change through GearFxInvSys with raise = false, and every second from GearTick with
# raise = true): lock modifiers (engine review 1: raise only from the tick), the warn line, Speed. While SkyyProfiles swaps the
# profile (profile:busy) only the lower-only lock pass runs (lowering never touches the current value).
M(gfx, r"""
public static void armorPass(java.util.UUID u, @PR@ pr, @CB@ cb, @REF@ ref, @IC@ armor, boolean raise) {
  if (u == null || cb == null || ref == null) return;
  boolean busy = @PKG@.Gear.busy(u);
  @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  float f = @PKG@.GearArmor.brokenFactor(cb.getExternalData());
  if (m != null) {
    java.util.HashMap want = armor != null ? @PKG@.GearArmor.lockSums(u, armor, f) : new java.util.HashMap();
    boolean up = raise && !busy;
    locks(u, m, want, up ? @PKG@.GearArmor.fullSums(armor, f) : null, armor, up);
  }
  if (busy) return;
  warnLines(pr, u, armor);
  float sp = 0.0f;
  if (@PKG@.GearCfg.PART_STATS && armor != null) {
    int[] t = @PKG@.GearStats.totals(u, null, armor, null, true);
    sp = (float) ((double) t[@PKG@.GearHit.I_SPD] * @PKG@.GearCfg.SPEED_PER / 100.0);
  }
  @PKG@.GearMove.post(u, "@MOVESRC@", "flat", sp, 0.0f, 0.0f);
  if (pr != null) @PKG@.GearMove.sync(u, pr, cb, ref, MOVE, "SkyyGear");
}""".replace("@MOVESRC@", MOVE_SOURCE))
# GearTick, once per second per player (world thread): the armor part, then regen / stamina every regen.periodMs, Life Steal payout
# every steal.windowS, owed Mana Steal. part.stats off = no regen, no steal, no Speed (the armor lock is level enforcement: part.gate).
M(gfx, r"""
public static void second(java.util.UUID u, @PR@ pr, @CB@ cb, @REF@ ref, @INV@ inv) {
  if (u == null || inv == null) return;
  armorPass(u, pr, cb, ref, inv.getArmor(), true);
  @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
  if (m == null) return;
  if (!@PKG@.GearCfg.PART_STATS) { REGEN.remove(u); LEECH.remove(u); MANA.remove(u); return; }
  boolean dead = cb.getComponent(ref, @DTHC@.getComponentType()) != null;
  long now = System.currentTimeMillis();
  int[] t = @PKG@.GearStats.totalsInv(u, inv, true);
  long[] rg = (long[]) REGEN.get(u);
  if (rg == null) { rg = new long[] { now, 0L }; REGEN.put(u, rg); }
  long el = now - rg[0];
  if (el < 0L) el = 0L;
  if (el > 5000L) el = 5000L;
  rg[0] = now;
  rg[1] = rg[1] + el;
  long per = (long) @PKG@.GearCfg.REGEN_MS;
  if (per < 250L) per = 250L;
  if (rg[1] >= per) {
    long n = rg[1] / per;
    rg[1] = rg[1] - n * per;
    if (!dead) {
      double hp = (double) n * (double) t[@PKG@.GearHit.I_HPR] * (1.0 + (double) t[@PKG@.GearHit.I_HPRP] / 100.0);
      if (hp > 0.0) add(m, @DST@.getHealth(), (float) hp, true);
      double sta = (double) n * (double) t[@PKG@.GearHit.I_STAM];
      if (sta > 0.0) add(m, @DST@.getStamina(), (float) sta, false);
    }
  }
  double[] lv = (double[]) LEECH.get(u);
  if (lv != null && lv[0] > 0.0 && (double) now - lv[1] >= (double) @PKG@.GearCfg.STEAL_S * 1000.0) {
    if (!dead) add(m, @DST@.getHealth(), (float) lv[0], true);
    lv[0] = 0.0;
    lv[1] = (double) now;
  }
  double[] mv = (double[]) MANA.get(u);
  if (mv != null && mv[0] > 0.0) {
    if (!dead) add(m, @DST@.getMana(), (float) mv[0], false);
    mv[0] = 0.0;
  }
}""")
M(gfx, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  REGEN.remove(u); LEECH.remove(u); MANA.remove(u); WARNED.remove(u); MOVE.remove(u); LOCKED.remove(u); BLOCKED.remove(u); PRIMED.remove(u);
  try { @PKG@.GearMove.post(u, "@MOVESRC@", "flat", 0.0f, 0.0f, 0.0f); } catch (Throwable t) { }
}""".replace("@MOVESRC@", MOVE_SOURCE))

# ================================================================= 0.2.1 GearHit.weaponHit: the weapon branch of GearHitSys (spec 3.5 items 2-3)
# A PLAYER's hit with the weapon it used (melee: the hand; projectiles: the launch record's stack - spec 3.5 item 1, no new GearShot field)
# after GearHitSys passed the gate (a blocked weapon never gets here). Only weapon hits (Physical / Projectile family or a spell shot):
#  1. NEW FIRST STEP, its own switch part.base (+ base.mode), never inside part.stats (spec 3.5 item 2): amount x m, m = K x F(level) x
#     material bonus (GearBase.weaponMult: 1 for a non-gear item, a mob's hit never comes here - u is a player's UUID);
#  2. then the 0.2 chain unchanged (moved here from GearHitSys byte for byte): Damage % -> Strength / Magical Power -> Charged Attack Damage
#     -> crit (GearHit.hitAmount) on the levelled amount, part.stats.
# Returns the per-Damage info for GearArmorSys / GearTrueSys / GearLeechSys (null = none). Static with plain arguments so the bare-JVM
# harness can execute it with real engine Damage objects; GearHitSys resolves the attacker, the weapon and the armor container (ECS).
M(ghit, r"""
public static Object[] weaponHit(@DMG@ d, java.util.UUID u, @PR@ pr, @IS@ main, boolean shot, @PKG@.GearShot srec, @PKG@.GearShot rec, @IC@ arm) {
  if (d == null || u == null) return null;
  boolean spell = shot && main != null && !main.isEmpty() && @PKG@.GearData.isSpell(main.getItemId());
  if (!spell && family(d.getCause()) <= 0) return null;
  double m = @PKG@.GearBase.weaponMult(main, spell);
  // review of 0.2.1 finding 1: a record GearShotTrack.pickFor chose (rec == null: an arrow / bolt through a plain EntitySource) never
  // gets more than the smallest multiplier among the records that may have fired it (one candidate = its own weapon: unchanged)
  if (srec != null && rec == null) {
    double lo = @PKG@.GearShotTrack.minMult(u, @PKG@.GearShotTrack.calcOf(d));
    if (lo > 0.0 && lo < m) m = lo;
  }
  if (m != 1.0) d.setAmount((float) ((double) d.getAmount() * m));
  if (!@PKG@.GearCfg.PART_STATS) return null;
  boolean[] ok = new boolean[1];
  int[] t = @PKG@.GearStats.totals(u, main, arm, ok, true);
  if (!ok[0]) return null;
  java.util.concurrent.ThreadLocalRandom rnd = java.util.concurrent.ThreadLocalRandom.current();
  float a0 = d.getAmount();
  // 0.1.2 Charged Attack Damage: judged only for a player with the stat (or an armed /gear charged probe)
  boolean chg = false;
  String[] cw = null;
  if (@PKG@.GearCfg.CHG_ON && (t[I_CHG] != 0 || @PKG@.GearCharged.watch(u))) {
    cw = new String[1];
    // review of 0.1.2 finding 1: a record from GearShotTrack.pick (rec == null) may belong to another weapon than the
    // arrow's - the judge also looks the step up in every live record's weapon (the projectile's own record: exact)
    String[] alts = null;
    if (srec != null && rec == null) alts = @PKG@.GearShotTrack.liveIds(u);
    chg = @PKG@.GearCharged.judge(d, main == null || main.isEmpty() ? null : main.getItemId(), srec, alts, cw);
  }
  double a = hitAmount((double) a0, t, spell, chg, rnd.nextDouble(), rnd.nextDouble());
  if (a != (double) a0) d.setAmount((float) a);
  if (cw != null) @PKG@.GearCharged.note(u, pr, main, chg, cw[0], spell, t[I_CHG], a0, a);
  return info(u, t);
}""")

# ================================================================= damage systems (spec 4.3 order): GearHitSys -> engine armor ->
# GearArmorSys -> GearTrueSys (Filter group, ordered with SystemDependency), GearLeechSys (Inspect group: the landed amount)
def dmg_system(cls, ctor, group, dep_field, dep_order, dep_expr, body):
    F(cls, "public java.util.Set deps;")
    F(cls, "public boolean ordered;")
    if dep_field:
        F(cls, "public static Class %s;" % dep_field)
    C(cls, r"""
public %s(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  Class dc = %s;
  this.ordered = ordered && dc != null;
  if (this.ordered) this.deps.add(new @SDEP@(@ORD@.%s, dc));
}""" % (ctor, dep_expr, dep_order))
    M(cls, "public @QRY@ getQuery() { return @QRY@.any(); }")
    M(cls, "public @SG@ getGroup() { return @DMOD@.get().%s(); }" % group)
    M(cls, "public java.util.Set getDependencies() { return this.deps; }")
    M(cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
%s
  } catch (Throwable t) { @PKG@.Gear.warnOnce("%s", "%s failed: " + t); }
}""" % (body, ctor, ctor))


# GearHitSys (Filter, BEFORE ArmorDamageReduction): spec 3.4 gate (main hand + utility slot, projectiles by their launch record, the
# SkyyClasses shot window), 4.3 offence stats on weapon hits, then the pre-armor amount of a player victim wearing an inactive piece
dmg_system(ghsy, "GearHitSys", "getFilterDamageGroup", "ADR", "BEFORE", "ADR", r"""
    if (d.isCancelled()) return;
    @REF@ vic = chunk.getReferenceTo(idx);
    Object[] info = null;
    @DSRC@ src = d.getSource();
    if (src instanceof @DENT@) {
      java.util.UUID u = null;
      @PR@ pr = null;
      @IS@ main = null;
      @IS@ ut = null;
      @REF@ att = null;
      boolean shot = false;
      String[] bad = null;
      @PKG@.GearShot rec = null;
      @PKG@.GearShot srec = null;
      if (src instanceof @DPRJ@) rec = @PKG@.GearShotTrack.find(buf, ((@DPRJ@) src).getProjectile());
      if (rec != null) {
        srec = rec;
        u = rec.shooter;
        main = rec.main;
        ut = rec.util;
        shot = true;
        if (rec.bad != null) bad = new String[] { rec.bad, rec.title, rec.body };
        pr = @UNI@.get().getPlayer(u);
        try { att = ((@EST@) buf.getExternalData()).getRefFromUUID(u); } catch (Throwable t0) { att = null; }
      } else {
        att = ((@DENT@) src).getRef();
        if (att != null && att.isValid()) pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
        if (pr != null) {
          u = pr.getUuid();
          // exploit review 1: a projectile hit (Projectile family) through a plain EntitySource (shortbow / crossbow arrows via
          // DamageEntityInteraction) takes weapon + spell flag from the shooter's live launch record (follow-up review 4:
          // GearShotTrack.pick - the newest, or the weaker weapon when different ones are in the air); melee keeps the hand.
          // Review of 0.2.1 finding 1: pickFor first keeps the records of the weapon that owns the hit's damage step (calcOf)
          boolean proj = @PKG@.GearHit.family(d.getCause()) == 2;
          @PKG@.GearShot nr = null;
          if (proj) {
            @IC@ pa = null;
            if (att != null && att.isValid()) {
              @ARMC@ pac = (@ARMC@) buf.getComponent(att, @ARMC@.getComponentType());
              pa = pac == null ? null : pac.getInventory();
            }
            nr = @PKG@.GearShotTrack.pickFor(u, pa, @PKG@.GearShotTrack.calcOf(d));
            if (nr == null) @PKG@.Gear.warnOnce("norecord", "a projectile hit (" + d.getCause().getId() + ") by " + pr.getUsername() + " found no launch record in the 10 s window - it got armor stats only; if this repeats, the shot tracker misses this projectile type (tell the SkyyGear builder)");
          }
          if (nr != null) {
            srec = nr;
            main = nr.main;
            ut = nr.util;
            shot = true;
            if (nr.bad != null) bad = new String[] { nr.bad, nr.title, nr.body };
          } else {
            main = @INVC@.getItemInHand(buf, att);
            @UTIL@ uc = (@UTIL@) buf.getComponent(att, @UTIL@.getComponentType());
            ut = uc == null ? null : uc.getActiveItem();
            bad = @PKG@.GearHit.judge(u, main, false);
            if (bad == null) bad = @PKG@.GearHit.judge(u, ut, true);
            // a projectile with no launch record: never the item in hand at landing - armor stats only
            if (proj) { main = null; ut = null; }
          }
          if (bad == null) {
            @PKG@.GearShot lb = @PKG@.GearShotTrack.liveBad(u);
            if (lb != null) bad = new String[] { lb.bad, lb.title, lb.body };
          }
        }
      }
      if (u != null && bad != null) {
        d.setAmount(0.0f);
        d.setCancelled(true);
        if (vic != null) buf.tryRemoveComponent(vic, @KBC@.getComponentType());
        if (pr != null && pr.isValid()) @PKG@.GearGate.popup(pr, u, bad[0], bad[1], bad[2]);
        return;
      }
      // 0.2.1: a PLAYER attacker's weapon branch = GearHit.weaponHit - the level's base multiplier first (part.base), then the 0.2 stats
      // chain (part.stats); u is set only for a player (a mob's hit has no PlayerRef and no launch record: its amount is never scaled here -
      // SkyyMobs scales mob damage in its own system)
      if (u != null) {
        @IC@ arm = null;
        if (att != null && att.isValid()) {
          @ARMC@ ac = (@ARMC@) buf.getComponent(att, @ARMC@.getComponentType());
          arm = ac == null ? null : ac.getInventory();
        }
        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);
      }
    }
    // the pre-armor amount of a player victim, for GearArmorSys: wearing an inactive piece (level.armorNative) or (0.2.1) a piece whose
    // per-stack resistance differs from its asset (base.armorOn); needs the ordered systems (the WARN at setup says when it is off)
    if (this.ordered && vic != null) {
      @PR@ vpr = (@PR@) buf.getComponent(vic, @PR@.getComponentType());
      if (vpr != null) {
        @ARMC@ vac = (@ARMC@) buf.getComponent(vic, @ARMC@.getComponentType());
        @IC@ va = vac == null ? null : vac.getInventory();
        if (va != null && ((@PKG@.GearCfg.ARMOR_NATIVE && @PKG@.GearArmor.hasInactive(vpr.getUuid(), va)) || @PKG@.GearArmor.hasResDelta(vpr.getUuid(), va))) {
          if (info == null) info = @PKG@.GearHit.info(null, null);
          info[0] = Float.valueOf(d.getAmount());
        }
      }
    }
    if (info != null) @PKG@.GearHit.put(d, info);""")
# GearArmorSys (Filter, AFTER ArmorDamageReduction): spec 3.5 part 3 (the engine formula over only the active pieces) and Defense
# (x scale / (scale + def), player victims, damage with an entity source; environment damage untouched, Q17)
dmg_system(garsy, "GearArmorSys", "getFilterDamageGroup", "ADR", "AFTER", "ADR", r"""
    if (d.isCancelled()) return;
    @REF@ vic = chunk.getReferenceTo(idx);
    if (vic == null) return;
    @PR@ vpr = (@PR@) buf.getComponent(vic, @PR@.getComponentType());
    if (vpr == null) return;
    java.util.UUID vu = vpr.getUuid();
    @ARMC@ vac = (@ARMC@) buf.getComponent(vic, @ARMC@.getComponentType());
    @IC@ full = vac == null ? null : vac.getInventory();
    if (full == null) return;
    Object[] info = @PKG@.GearHit.get(d);
    // spec 3.5 part 3 (inactive pieces, level.armorNative) + 0.2.1 item 6 (per-stack resistance, base.armorOn): GearArmor.fix
    if (this.ordered && info != null && info[0] instanceof Float) {
      float pre = ((Float) info[0]).floatValue();
      @WLD@ w = null;
      try { w = ((@EST@) buf.getExternalData()).getWorld(); } catch (Throwable t0) { w = null; }
      boolean pen = @ITU@.canApplyItemStackPenalties(vic, buf);
      @ECC@ ecc = (@ECC@) chunk.getComponent(idx, @ECC@.getComponentType());
      float cur = d.getAmount();
      float nu = @PKG@.GearArmor.fix(vu, pre, cur, d.getCause(), full, w, pen, ecc);
      if (nu != cur) d.setAmount(nu);
    }
    if (@PKG@.GearCfg.PART_STATS && d.getSource() instanceof @DENT@) {
      int[] t = @PKG@.GearStats.totals(vu, null, full, null, true);
      int def = t[@PKG@.GearHit.I_DEF];
      if (def > 0) {
        double sc = (double) @PKG@.GearCfg.DEF_SCALE;
        d.setAmount((float) ((double) d.getAmount() * sc / (sc + (double) def)));
      }
    }""")
# GearTrueSys (Filter, AFTER GearArmorSys): + True Damage, so neither Hytale armor nor Defense reduces it (spec 4.2), + the flat
# element damage (design review 8, lock 17: element damage applies on its own, not cut by Defence; affinities are a later stage)
dmg_system(gtsy, "GearTrueSys", "getFilterDamageGroup", "AFTERSYS", "AFTER", "AFTERSYS", r"""
    if (d.isCancelled() || !@PKG@.GearCfg.PART_STATS) return;
    Object[] info = @PKG@.GearHit.get(d);
    if (info == null || !(info[1] instanceof Integer)) return;
    int td = ((Integer) info[1]).intValue();
    int el = info.length > 5 && info[5] instanceof Integer ? ((Integer) info[5]).intValue() : 0;
    long add = (long) (td > 0 ? td : 0) + (long) (el > 0 ? el : 0);
    if (add > 1000000000L) add = 1000000000L;
    if (add > 0L) d.setAmount(d.getAmount() + (float) add);""")
# GearLeechSys (Inspect: after the damage landed): Life Steal owed, Mana Steal owed; the stat writes happen in GearTick (no stat write
# inside the damage dispatch, the SkyyClasses PriestHealSys rule)
dmg_system(glsy, "GearLeechSys", "getInspectDamageGroup", None, "AFTER", "null", r"""
    Object[] info = @PKG@.GearHit.take(d);
    if (info == null || d.isCancelled() || !@PKG@.GearCfg.PART_STATS) return;
    java.util.UUID u = info[4] instanceof java.util.UUID ? (java.util.UUID) info[4] : null;
    if (u == null) return;
    float dealt = d.getAmount();
    if (!(dealt > 0.0f)) return;
    int ls = ((Integer) info[2]).intValue();
    if (ls > 0) @PKG@.GearFx.leech(u, (double) dealt * (double) ls / 100.0);
    int ms = ((Integer) info[3]).intValue();
    if (ms > 0) @PKG@.GearFx.manaSteal(u, ms);""")
C(ghsyU, "public GearHitSysU() { super(false); }")
C(garsU, "public GearArmorSysU() { super(false); }")
C(gtsyU, "public GearTrueSysU() { super(false); }")

# ================================================================= GearDeathMark (BEFORE DropDeathItems) + GearDropSys (spec 5.5 mobs)
F(gdm, "public java.util.Set deps;")
F(gdm, "public static Class DDI;")
C(gdm, r"""
public GearDeathMark(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  if (ordered && DDI != null) this.deps.add(new @SDEP@(@ORD@.BEFORE, DDI));
}""")
M(gdm, "public @QRY@ getQuery() { return @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @DTHC@.getComponentType() }); }")
M(gdm, "public java.util.Set getDependencies() { return this.deps; }")
M(gdm, "public boolean isParallel(int a, int b) { return false; }")
# once per world tick, before the chunks: last tick's marks go (the window is exactly one tick, spec 5.5 step 3)
M(gdm, r"""
public void tick(float dt, int si, @ST@ store) {
  try { @PKG@.GearTag.clear(@PKG@.GearTag.key(store.getExternalData())); } catch (Throwable t) { }
  super.tick(dt, si, store);
}""")
# the DropDeathItems condition, copied (bytecode 2026-09-28): DeathComponent items-loss mode ALL, a role that has not dropped yet,
# dropping instantly or with a DeferredCorpseRemoval that is due (or none)
M(gdm, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (!@PKG@.GearCfg.PART_DROPS) return;
    @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());
    if (dc == null || dc.getItemsLossMode() != @ILM@.ALL) return;
    @NPCE@ npc = (@NPCE@) chunk.getComponent(idx, @NPCE@.getComponentType());
    if (npc == null) return;
    @ROLE@ role = npc.getRole();
    if (role == null || role.hasDroppedDeathItems()) return;
    if (!role.isDropDeathItemsInstantly()) {
      @DCR@ dcr = (@DCR@) chunk.getComponent(idx, @DCR@.getComponentType());
      if (dcr != null && !dcr.shouldRemove()) return;
    }
    @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return;
    @VEC@ p = tc.getPosition();
    @PKG@.GearTag.mark(@PKG@.GearTag.key(store.getExternalData()), p.x, p.y + 1.0, p.z);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("deathmark", "death drop mark failed: " + t); }
}""")
C(gdmU, "public GearDeathMarkU() { super(false); }")
F(gdrs, "public @QRY@ query;")
C(gdrs, "public GearDropSys() { super(); this.query = null; }")
M(gdrs, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @ITC@.getComponentType(), (@QRY@) @TC@.getComponentType() });
  return this.query;
}""")
M(gdrs, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CB@ buf) {
  try {
    if (reason != @ADDR@.SPAWN || !@PKG@.GearCfg.PART_DROPS) return;
    String k = @PKG@.GearTag.key(st.getExternalData());
    if (!@PKG@.GearTag.any(k)) return;
    @ITC@ ic = (@ITC@) buf.getComponent(ref, @ITC@.getComponentType());
    if (ic == null) return;
    @IS@ s = ic.getItemStack();
    if (s == null || s.isEmpty() || !@PKG@.GearData.isGear(s.getItemId()) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return;
    @TC@ tc = (@TC@) buf.getComponent(ref, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return;
    @VEC@ p = tc.getPosition();
    if (!@PKG@.GearTag.near(k, p.x, p.y, p.z)) return;
    @IS@ ns = @PKG@.GearTag.unid(s, 1);
    if (ns == s || ns == null) return;
    ic.setItemStack(ns);
    @PKG@.GearTag.MOB_TAGS.incrementAndGet();
    @BD@ d = @PKG@.GearData.gearDoc(ns.getMetadata());
    @PKG@.GearLog.line("UNID mob " + ns.getItemId() + " " + (d == null ? "?" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]) + " " + k + " " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z));
  } catch (Throwable t) { @PKG@.Gear.warnOnce("droptag", "death drop tag failed: " + t); }
}""")
M(gdrs, "public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CB@ buf) { }")

# ================================================================= 0.1.3 GearOpened: per world, the containers already decided (see the header)
# W: world name -> ConcurrentHashMap(Long packed x y z -> Character state); a world's file is read once, on its first decision (world
# thread, one small file) or earlier by PlayerReady's prefetch on the scheduler (review of 0.1.3 finding 5). Q: String[] { world, line }
# waiting for the scheduler (GearLog's pattern: the class monitor only swaps the queue, the disk write runs under WLOCK). States: W world
# container, decided + tagged; P player storage, never touched; L a loot container (it had a drop list when added and carries a placer -
# an admin's /stash set chest), not opened yet; T such a loot container, tagged; X (file only) forgotten = no record. The last line of a
# position wins. Review of 0.1.3: PW = world -> (position -> the placer UUID an L / T record was made with; "placer=<uuid>" right after
# the time in its line, finding 2); CH = world -> (chunk -> TRUE) for the chunks that hold a record (a regenerated chunk forgets its
# records, finding 3b); TEMP = the keys of worlds Hytale deletes (memory only, never a file - finding 4).
gopn.addInterface(pool.get("java.lang.Runnable"))
F(gopn, "public static final java.util.concurrent.ConcurrentHashMap W = new java.util.concurrent.ConcurrentHashMap();")
F(gopn, "public static final java.util.concurrent.ConcurrentHashMap PW = new java.util.concurrent.ConcurrentHashMap();")
F(gopn, "public static final java.util.concurrent.ConcurrentHashMap CH = new java.util.concurrent.ConcurrentHashMap();")
F(gopn, "public static final java.util.concurrent.ConcurrentHashMap TEMP = new java.util.concurrent.ConcurrentHashMap();")
F(gopn, "public static final java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();")
F(gopn, "public static final Object WLOCK = new Object();")
F(gopn, "public static volatile boolean SCHED = false;")
F(gopn, "public static volatile java.nio.file.Path DIR;")
F(gopn, "public static volatile boolean FAILED = false;")
F(gopn, "public String pre;")
C(gopn, "public GearOpened() { this.pre = null; }")
C(gopn, "public GearOpened(String k) { this.pre = k; }")
# x 26 bits, z 26 bits, y 12 bits (SkyyExploration's ChestReg key)
M(gopn, r"""
public static long pack(int x, int y, int z) {
  return (((long) x) << 38) | ((((long) z) & 0x3FFFFFFL) << 12) | (((long) y) & 0xFFFL);
}""")
M(gopn, "public static int ux(long k) { return (int) (k >> 38); }")
M(gopn, "public static int uy(long k) { return (int) (k & 0xFFFL); }")
M(gopn, "public static int uz(long k) { return (int) ((k << 26) >> 38); }")
# the chunk of a block (ChunkUtil.chunkCoordinate, the engine's own block -> chunk math)
M(gopn, "public static long ckc(int cx, int cz) { return (((long) cx) << 32) | (((long) cz) & 0xFFFFFFFFL); }")
M(gopn, "public static long ck(int x, int z) { return ckc(@CHU@.chunkCoordinate(x), @CHU@.chunkCoordinate(z)); }")
# a file name for a world name: letters, digits, - _ . kept; anything else (or a changed / empty / dot-first name) gets a hash suffix
M(gopn, r"""
public static String safe(String k) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < k.length() && i < 80; i++) {
    char ch = k.charAt(i);
    boolean ok = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '-' || ch == '_' || ch == '.';
    sb.append(ok ? ch : '_');
  }
  String s = sb.toString();
  if (!s.equals(k) || s.length() == 0 || s.startsWith(".")) s = s + "-" + Integer.toHexString(k.hashCode());
  return s;
}""")
M(gopn, r"""
public static java.nio.file.Path file(String k) {
  java.nio.file.Path d = DIR;
  return d == null || k == null ? null : d.resolve(safe(k) + ".txt");
}""")
M(gopn, r"""
public static void read(String k, java.util.concurrent.ConcurrentHashMap m, java.util.concurrent.ConcurrentHashMap pm, java.util.concurrent.ConcurrentHashMap ch) {
  java.nio.file.Path f = file(k);
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
  try {
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < ls.size(); i++) {
      String l = ((String) ls.get(i)).trim();
      if (l.length() == 0 || l.startsWith("#")) continue;
      String[] p = l.split("\\s+");
      if (p.length < 3) continue;
      try {
        int x = Integer.parseInt(p[0]);
        int y = Integer.parseInt(p[1]);
        int z = Integer.parseInt(p[2]);
        char c = p.length > 3 && p[3].length() == 1 ? p[3].charAt(0) : 'W';
        if (c != 'W' && c != 'P' && c != 'L' && c != 'T' && c != 'X') c = 'W';
        Long key = Long.valueOf(pack(x, y, z));
        if (c == 'X') { m.remove(key); pm.remove(key); continue; }
        m.put(key, new Character(c));
        java.util.UUID pu = null;
        if ((c == 'L' || c == 'T') && p.length > 5 && p[5].startsWith("placer=")) {
          try { pu = java.util.UUID.fromString(p[5].substring(7)); } catch (Throwable t3) { pu = null; }
        }
        if (pu != null) pm.put(key, pu); else pm.remove(key);
        ch.put(Long.valueOf(ck(x, z)), Boolean.TRUE);
      } catch (Throwable t2) { }
    }
  } catch (Throwable t) { @PKG@.Gear.warn("could not read " + f + " - the containers listed there are decided again on their next open (only gear without a document is ever touched): " + t); }
}""")
M(gopn, r"""
public static synchronized java.util.concurrent.ConcurrentHashMap load(String k) {
  Object o = W.get(k);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap pm = new java.util.concurrent.ConcurrentHashMap();
  java.util.concurrent.ConcurrentHashMap ch = new java.util.concurrent.ConcurrentHashMap();
  if (!TEMP.containsKey(k)) read(k, m, pm, ch);
  PW.put(k, pm);
  CH.put(k, ch);
  W.put(k, m);
  return m;
}""")
M(gopn, r"""
public static java.util.concurrent.ConcurrentHashMap map(String k) {
  Object o = W.get(k);
  return o != null ? (java.util.concurrent.ConcurrentHashMap) o : load(k);
}""")
M(gopn, r"""
public static java.util.concurrent.ConcurrentHashMap pmap(String k) {
  map(k);
  Object o = PW.get(k);
  return o == null ? null : (java.util.concurrent.ConcurrentHashMap) o;
}""")
M(gopn, r"""
public static char get(String k, int x, int y, int z) {
  if (k == null) return (char) 0;
  Object o = map(k).get(Long.valueOf(pack(x, y, z)));
  return o instanceof Character ? ((Character) o).charValue() : (char) 0;
}""")
# the placer an L / T record was made with (null = none / not known)
M(gopn, r"""
public static java.util.UUID placer(String k, int x, int y, int z) {
  if (k == null) return null;
  java.util.concurrent.ConcurrentHashMap pm = pmap(k);
  Object o = pm == null ? null : pm.get(Long.valueOf(pack(x, y, z)));
  return o instanceof java.util.UUID ? (java.util.UUID) o : null;
}""")
M(gopn, r"""
public static synchronized Object[] take() {
  SCHED = false;
  java.util.ArrayList l = new java.util.ArrayList();
  Object o = Q.poll();
  while (o != null) { l.add(o); o = Q.poll(); }
  return l.toArray();
}""")
M(gopn, r"""
public static void write(java.nio.file.Path f, String world, String text) {
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String t = text;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) t = "# SkyyGear - the containers of world " + world + " whose first open (or break) was decided: x y z state time [placer=<uuid>] note. W = world container, its gear was made unidentified; P = player storage, never touched; L = loot container not opened yet; T = loot container, tagged; X = forgotten (a new container or a regenerated chunk there). The last line of a position wins. Delete this file while the server is stopped to decide every container again.\n" + text;
    java.nio.file.Files.write(f, t.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable x) { if (!FAILED) { FAILED = true; @PKG@.Gear.warn("could not write " + f + " (decisions stay in memory until the next start): " + x); } }
}""")
M(gopn, r"""
public static void flush() {
  Object[] a = take();
  if (a.length == 0) return;
  java.util.LinkedHashMap g = new java.util.LinkedHashMap();
  for (int i = 0; i < a.length; i++) {
    String[] e = (String[]) a[i];
    StringBuilder sb = (StringBuilder) g.get(e[0]);
    if (sb == null) { sb = new StringBuilder(); g.put(e[0], sb); }
    sb.append(e[1]).append('\n');
  }
  java.util.Iterator it = g.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String wk = (String) en.getKey();
    java.nio.file.Path f = file(wk);
    if (f == null) continue;
    String txt = en.getValue().toString();
    synchronized (WLOCK) { write(f, wk, txt); }
  }
}""")
# the scheduler task: a prefetch (pre = a world key: read its file now, off the world thread) or the queued line write
M(gopn, r"""
public void run() {
  if (this.pre != null) {
    try { load(this.pre); } catch (Throwable t) { }
    return;
  }
  flush();
}""")
M(gopn, r"""
public static synchronized void kick() {
  if (SCHED) return;
  SCHED = true;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearOpened(), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { SCHED = false; }
}""")
# review of 0.1.3 finding 5: PlayerReady reads the world's memory on the scheduler, so the world thread normally finds it loaded
M(gopn, r"""
public static void prefetch(String k) {
  if (k == null || DIR == null || W.containsKey(k)) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearOpened(k), 1L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")
# placer = the L / T record's placer (kept in PW and in the line); state X forgets the position (memory + an X line)
M(gopn, r"""
public static void put(String k, int x, int y, int z, char c, java.util.UUID placer, String note) {
  if (k == null) return;
  Long key = Long.valueOf(pack(x, y, z));
  java.util.concurrent.ConcurrentHashMap m = map(k);
  java.util.concurrent.ConcurrentHashMap pm = pmap(k);
  Object cho = CH.get(k);
  if (c == 'X') m.remove(key); else m.put(key, new Character(c));
  boolean lt = (c == 'L' || c == 'T') && placer != null;
  if (pm != null) { if (lt) pm.put(key, placer); else pm.remove(key); }
  if (c != 'X' && cho instanceof java.util.concurrent.ConcurrentHashMap) ((java.util.concurrent.ConcurrentHashMap) cho).put(Long.valueOf(ck(x, z)), Boolean.TRUE);
  if (TEMP.containsKey(k)) return;
  String ts = "";
  try { ts = java.time.LocalDateTime.now().withNano(0).toString(); } catch (Throwable t) { ts = String.valueOf(System.currentTimeMillis()); }
  String nt = note == null ? "" : note.replace('\n', ' ').replace('\r', ' ');
  Q.add(new String[] { k, x + " " + y + " " + z + " " + String.valueOf(c) + " " + ts + " " + (lt ? "placer=" + placer + " " : "") + nt });
  kick();
}""")
M(gopn, r"""
public static void put(String k, int x, int y, int z, char c, String note) {
  put(k, x, y, z, c, (java.util.UUID) null, note);
}""")
# review of 0.1.3 finding 3b: a regenerated chunk (GearChunkRegen) forgets every record inside it, P included (all its blocks are new).
# Only a world that has records there does any work (CH); a world whose memory is not loaded yet is read first when it has a file.
M(gopn, r"""
public static int regen(String k, int cx, int cz) {
  if (k == null) return 0;
  java.util.concurrent.ConcurrentHashMap m = null;
  Object o = W.get(k);
  if (o != null) m = (java.util.concurrent.ConcurrentHashMap) o;
  else {
    if (TEMP.containsKey(k)) return 0;
    java.nio.file.Path f = file(k);
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0;
    m = load(k);
  }
  Object co = CH.get(k);
  Long cc = Long.valueOf(ckc(cx, cz));
  if (!(co instanceof java.util.concurrent.ConcurrentHashMap) || !((java.util.concurrent.ConcurrentHashMap) co).containsKey(cc)) return 0;
  ((java.util.concurrent.ConcurrentHashMap) co).remove(cc);
  Object[] ks = m.keySet().toArray();
  int n = 0;
  for (int i = 0; i < ks.length; i++) {
    long kk = ((Long) ks[i]).longValue();
    int x = ux(kk);
    int y = uy(kk);
    int z = uz(kk);
    if (@CHU@.chunkCoordinate(x) != cx || @CHU@.chunkCoordinate(z) != cz) continue;
    put(k, x, y, z, 'X', "chunk " + cx + " " + cz + " regenerated");
    n++;
  }
  return n;
}""")
# review of 0.1.3 finding 4: RemoveWorldEvent (GearWorldBye) - write what is queued, then drop the world's maps (a world that comes back
# reads its file again; a deleted one never had a file)
M(gopn, r"""
public static void evict(String k) {
  if (k == null) return;
  try { flush(); } catch (Throwable t) { }
  W.remove(k);
  PW.remove(k);
  CH.remove(k);
  TEMP.remove(k);
}""")

# ================================================================= 0.1.3 GearChestOpen (2/2): who placed it, the decision, the hooks' entry points
# the players of this server: Universe.getPlayerStorage().getPlayers() (the player files), read on the scheduler by GearKnownTask
M(gcho, r"""
public static boolean refreshKnown() {
  try {
    @UNI@ un = @UNI@.get();
    if (un == null) return false;
    @PSTO@ ps = un.getPlayerStorage();
    if (ps == null) return false;
    java.util.Set s = ps.getPlayers();
    if (s == null) return false;
    java.util.Iterator it = s.iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof java.util.UUID) KNOWN.put(o, Boolean.TRUE);
    }
    KNOWN_AT = System.currentTimeMillis();
    if (!KNOWN_OK) @PKG@.Gear.info("world chests: " + s.size() + " players of this server known - containers they placed are player storage and never touched");
    KNOWN_OK = true;
    return true;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("known", "could not read the players of this server (a container with a placer stays undecided until it works): " + t);
    return false;
  }
}""")
# 1 = a player of this server (the list, online now, or seen at PlayerReady), 0 = not, -1 = cannot tell yet (the list was never read).
# Review of 0.1.3 finding 5: only GearKnownTask (scheduler) reads the player list (a folder listing) - never the world thread here.
M(gcho, r"""
public static int known(java.util.UUID u) {
  if (u == null) return 0;
  if (KNOWN.containsKey(u)) return 1;
  try {
    @UNI@ un = @UNI@.get();
    if (un != null && un.getPlayer(u) != null) { KNOWN.put(u, Boolean.TRUE); return 1; }
  } catch (Throwable t) { }
  return KNOWN_OK ? 0 : -1;
}""")
M(gcho, "public static void seen(java.util.UUID u) { if (u != null) KNOWN.put(u, Boolean.TRUE); }")
# the memory key of a world: its name + "~" + its own UUID (WorldConfig.getUuid - saved in the world's config.json, so a world that is
# deleted and made again under the same name, e.g. an instance or a reset, starts with a fresh memory); the name alone when unknown.
# Review of 0.1.3 finding 4: a world Hytale deletes (WorldConfig isDeleteOnRemove / isDeleteOnUniverseStart: instances, temporary
# worlds) is noted in GearOpened.TEMP - its decisions stay in memory only, never a chests/ file.
M(gcho, r"""
public static String wkey(@WLD@ w) {
  if (w == null) return null;
  String n = w.getName();
  if (n == null) return null;
  java.util.UUID id = null;
  boolean tmp = false;
  try {
    if (w.getWorldConfig() != null) {
      id = w.getWorldConfig().getUuid();
      tmp = w.getWorldConfig().isDeleteOnRemove() || w.getWorldConfig().isDeleteOnUniverseStart();
    }
  } catch (Throwable t) { id = null; }
  String k = id == null ? n : n + "~" + id;
  if (tmp) @PKG@.GearOpened.TEMP.put(k, Boolean.TRUE);
  return k;
}""")
# the world name of a memory key
M(gcho, r"""
public static String wname(String k) {
  if (k == null) return null;
  int i = k.lastIndexOf('~');
  return i > 0 ? k.substring(0, i) : k;
}""")
# a SkyyIslands island world (bridge island:owner:fn -> owner key, or its naming skyy-island-<key>[-r<N>]): never touched
M(gcho, r"""
public static boolean island(String wn) {
  if (wn == null) return false;
  if (wn.startsWith("skyy-island-")) return true;
  try {
    java.util.function.Function f = @PKG@.Gear.fn("island:owner:fn");
    return f != null && f.apply(wn) != null;
  } catch (Throwable t) { return false; }
}""")
# THE decision (pure: no engine lookups, so the bare-JVM harness runs it on plain containers). k = the world's memory key (wkey), x y z = the container's
# origin, c = its items, placer = its PlacedByInteractionComponent UUID (null = none), who / name = the opener (who null = a break),
# how = open / break / window. Returns >= 0 = newly decided world container, that many documents written; -2 island; -3 already decided
# world container (nothing written); -4 player storage; -5 a placer that cannot be judged yet (not remembered); -9 part.chests off.
# Every world-container result gives the opener a loot window: an open (how "open") or a container decided just now STARTS it, the
# window task ("window") only extends a started one (review of 0.1.3 finding 1: never past CAP_MS after the start).
# Review of 0.1.3 finding 2: an L / T record keeps its placer; a container there whose placer is ANOTHER player of this server is
# player storage (P), like the W rule below; another placer that is not a player here keeps the loot spot; unreadable list -> -5.
M(gcho, r"""
public static int decide(String k, int x, int y, int z, @IC@ c, java.util.UUID placer, java.util.UUID who, String name, String how) {
  if (k == null || c == null || !@PKG@.GearCfg.PART_CHESTS) return -9;
  if (island(wname(k))) return -2;
  char rec = @PKG@.GearOpened.get(k, x, y, z);
  int kn = placer == null ? 0 : known(placer);
  boolean fresh = "open".equals(how);
  String at = wname(k) + " " + x + " " + y + " " + z;
  java.util.UUID lp = null;
  if (rec == 'L' || rec == 'T') {
    lp = @PKG@.GearOpened.placer(k, x, y, z);
    if (placer != null && lp != null && !placer.equals(lp)) {
      if (kn < 0) {
        @PKG@.Gear.warnOnce("knownwait", "a container with a placer was opened before the players of this server could be read - it is left as it is until a later open");
        return -5;
      }
      if (kn > 0) {
        @PKG@.GearOpened.put(k, x, y, z, 'P', "placed by player " + placer + " where a loot container placed by " + lp + " was");
        PLAYER_N.incrementAndGet();
        @PKG@.GearLog.line("CHEST player storage " + at + " (a player placed a container where a loot container placed by " + lp + " was) placed by " + placer + " - never touched");
        return -4;
      }
    }
  }
  if (rec == 'T') { if (fresh) loot(who); else lootMore(who); return -3; }
  if (rec == 'W') {
    if (kn > 0) {
      @PKG@.GearOpened.put(k, x, y, z, 'P', "placed by player " + placer + " now");
      PLAYER_N.incrementAndGet();
      @PKG@.GearLog.line("CHEST player storage " + at + " (a player placed a container where a world chest was) placed by " + placer + " - never touched");
      return -4;
    }
    if (fresh) loot(who); else lootMore(who);
    return -3;
  }
  if (rec == 'P' && placer != null) return -4;
  if (rec != 'L') {
    if (kn < 0) {
      @PKG@.Gear.warnOnce("knownwait", "a container with a placer was opened before the players of this server could be read - it is left as it is until a later open");
      return -5;
    }
    if (kn > 0) {
      @PKG@.GearOpened.put(k, x, y, z, 'P', "placed by player " + placer);
      PLAYER_N.incrementAndGet();
      @PKG@.GearLog.line("CHEST player storage " + at + " placed by " + placer + " (" + how + " by " + name + ") - never touched");
      return -4;
    }
  }
  int n = @PKG@.GearTag.tagContainer(c, "first " + how + " by " + name + " at " + at);
  @PKG@.GearOpened.put(k, x, y, z, rec == 'L' ? 'T' : 'W', rec == 'L' ? lp : null, "first " + how + " by " + name + ", " + n + " tagged");
  WORLD_N.incrementAndGet();
  OPEN_TAGS.addAndGet((long) n);
  @PKG@.GearLog.line("CHEST first " + how + " " + at + " by " + name + ": " + n + " gear item(s) made unidentified" + (rec == 'L' ? " (loot container)" : "") + (placer == null ? "" : " (placer " + placer + " is not a player here)"));
  loot(who);
  return n;
}""")
# the multi-block origin of a filler block (StashCommand.getItemContainerBlock / SkyyExploration ChestReg.origin math); null = none
M(gcho, r"""
public static int[] origin(@WLD@ w, int x, int y, int z) {
  try {
    @CHS@ cs = w.getChunkStore();
    if (cs == null) return null;
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return null;
    @BSEC@ bs = (@BSEC@) cs.getStore().getComponent(sr, @BSEC@.getComponentType());
    if (bs == null) return null;
    int f = bs.getFiller(x, y, z);
    if (f == 0) return null;
    return new int[] { x - @FBU@.unpackX(f), y - @FBU@.unpackY(f), z - @FBU@.unpackZ(f) };
  } catch (Throwable t) { return null; }
}""")
M(gcho, r"""
public static @ICB@ icbOf(@REF@ be) {
  if (be == null || !be.isValid()) return null;
  try { return (@ICB@) be.getStore().getComponent(be, @ICB@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(gcho, r"""
public static java.util.UUID placedBy(@REF@ be) {
  if (be == null || !be.isValid()) return null;
  try {
    @PBI@ pc = (@PBI@) be.getStore().getComponent(be, @PBI@.getComponentType());
    return pc == null ? null : pc.getWhoPlacedUuid();
  } catch (Throwable t) { return null; }
}""")
# the engine side (world thread): the block entity at x y z (or at its filler's origin) must carry an ItemContainerBlock - else -1 (not
# a container: every other used / broken block ends here after one block-entity lookup)
M(gcho, r"""
public static int process(@WLD@ w, int x, int y, int z, java.util.UUID who, String name, String how) {
  if (w == null || !@PKG@.GearCfg.PART_CHESTS) return -9;
  @REF@ be = @BMOD@.getBlockEntity(w, x, y, z);
  @ICB@ icb = icbOf(be);
  int px = x;
  int py = y;
  int pz = z;
  if (icb == null) {
    int[] o = origin(w, x, y, z);
    if (o == null) return -1;
    px = o[0];
    py = o[1];
    pz = o[2];
    be = @BMOD@.getBlockEntity(w, px, py, pz);
    icb = icbOf(be);
    if (icb == null) return -1;
  }
  return decide(wkey(w), px, py, pz, icb.getItemContainer(), placedBy(be), who, name, how);
}""")
# world position of a block entity (StashPlugin.stash / SkyyExploration ChestReg.posOf: section ref -> ChunkSection, index -> x y z)
M(gcho, r"""
public static int[] posOf(@ST@ acc, @BSI@ info) {
  if (info == null) return null;
  @REF@ sr = info.getSectionRef();
  if (sr == null || !sr.isValid()) return null;
  @CSEC@ cs = (@CSEC@) acc.getComponent(sr, @CSEC@.getComponentType());
  if (cs == null) return null;
  int idx = info.getIndex();
  return new int[] { @CHU@.worldCoordFromLocalCoord(cs.getX(), @CHU@.xFromIndex(idx)), @CHU@.worldCoordFromLocalCoord(cs.getY(), @CHU@.yFromIndex(idx)), @CHU@.worldCoordFromLocalCoord(cs.getZ(), @CHU@.zFromIndex(idx)) };
}""")
# GearChestMark (a container that has a drop list when its block entity is added): one that carries a placer is remembered as a loot
# container (L) so its first open is treated as a world chest although a player placed it (an admin's /stash set chest - SkyyExploration
# counts those too, and gives its chest luck there). A position already decided as world / loot stays as it is.
M(gcho, r"""
public static void lootMark(@ST@ store, @REF@ ref, String dl) {
  try {
    @PBI@ pc = (@PBI@) store.getComponent(ref, @PBI@.getComponentType());
    if (pc == null || pc.getWhoPlacedUuid() == null) return;
    int[] p = posOf(store, (@BSI@) store.getComponent(ref, @BSI@.getComponentType()));
    if (p == null) return;
    Object ext = store.getExternalData();
    @WLD@ w = ext instanceof @CHS@ ? ((@CHS@) ext).getWorld() : null;
    String k = wkey(w);
    if (k == null || island(w.getName())) return;
    char rec = @PKG@.GearOpened.get(k, p[0], p[1], p[2]);
    if (rec == 'L' || rec == 'T' || rec == 'W') return;
    @PKG@.GearOpened.put(k, p[0], p[1], p[2], 'L', pc.getWhoPlacedUuid(), "drop list " + dl);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("lootmark", "could not remember a placed loot container: " + t); }
}""")
# Review of 0.1.3 finding 3a (GearChestMark, AddReason.SPAWN, before chestMark / lootMark): a container block entity made at runtime
# (BlockEntity.setBlockEntity / ensureBlockEntity: a block set by code, a player's placement - its PlacedByInteractionComponent comes
# right after) with no placer at a spot remembered as W / T / L is a NEW container: the record is forgotten (an X line), so its first
# open is decided again (a player's own chest -> P then). The chest's own open / close state change never gets here: setBlock with
# flag 2 keeps the block entity (BlockOperations.setBlockInteractionState passes 198, checked by this build). P records stay.
M(gcho, r"""
public static void spawned(@ST@ store, @REF@ ref) {
  try {
    @PBI@ pc = (@PBI@) store.getComponent(ref, @PBI@.getComponentType());
    if (pc != null && pc.getWhoPlacedUuid() != null) return;
    int[] p = posOf(store, (@BSI@) store.getComponent(ref, @BSI@.getComponentType()));
    if (p == null) return;
    Object ext = store.getExternalData();
    @WLD@ w = ext instanceof @CHS@ ? ((@CHS@) ext).getWorld() : null;
    String k = wkey(w);
    if (k == null) return;
    char rec = @PKG@.GearOpened.get(k, p[0], p[1], p[2]);
    if (rec != 'W' && rec != 'T' && rec != 'L') return;
    @PKG@.GearOpened.put(k, p[0], p[1], p[2], 'X', "a new container without a placer replaced the " + String.valueOf(rec) + " one");
    @PKG@.GearLog.line("CHEST forget " + wname(k) + " " + p[0] + " " + p[1] + " " + p[2] + " (" + String.valueOf(rec) + "): a new container without a placer is there - decided again on its next open");
  } catch (Throwable t) { @PKG@.Gear.warnOnce("chestspawn", "could not check a new container: " + t); }
}""")
# the window backup's world task (GearChestOpen.second queues it)
gcht.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @WLD@ w;", "public int x;", "public int y;", "public int z;", "public java.util.UUID u;", "public String name;"):
    F(gcht, _f)
C(gcht, r"""
public GearChestTask(@WLD@ w, int x, int y, int z, java.util.UUID u, String name) {
  this.w = w; this.x = x; this.y = y; this.z = z; this.u = u; this.name = name;
}""")
M(gcht, r"""
public void run() {
  try { @PKG@.GearChestOpen.process(this.w, this.x, this.y, this.z, this.u, this.name, "window"); }
  catch (Throwable t) { @PKG@.Gear.warnOnce("chesttask", "world chest window check failed: " + t); }
}""")
# GearTick (1 s, world thread): the player's open ContainerBlockWindows - a decided world / loot container extends the loot window
# (lootMore, never past its cap; a T one at once, W through the task so a placer change is seen), an undecided one is decided in a world task (the backup for a
# container opened by any path that skipped UseBlockEvent$Pre). Player storage (P) and islands: nothing. SkyyVault / SkyyEssentials
# trade / SkyySacks windows are ContainerWindow (no BlockWindow) and never get here.
M(gcho, r"""
public static void second(@PLA@ p, @PR@ pr, @WLD@ w) {
  if (!@PKG@.GearCfg.PART_CHESTS || p == null || pr == null || w == null) return;
  java.util.List ws = null;
  try { ws = p.getWindowManager().getWindows(); } catch (Throwable t) { return; }
  if (ws == null || ws.isEmpty()) return;
  String k = wkey(w);
  if (k == null || island(w.getName())) return;
  for (int i = 0; i < ws.size(); i++) {
    Object o = ws.get(i);
    if (!(o instanceof @CBW@)) continue;
    @BWIN@ bw = (@BWIN@) o;
    char rec = @PKG@.GearOpened.get(k, bw.getX(), bw.getY(), bw.getZ());
    if (rec == 'P') continue;
    if (rec == 'T') { lootMore(pr.getUuid()); continue; }
    w.execute(new @PKG@.GearChestTask(w, bw.getX(), bw.getY(), bw.getZ(), pr.getUuid(), pr.getUsername()));
  }
}""")
M(gcho, r"""
public static String statusText() {
  if (!@PKG@.GearCfg.PART_CHESTS) return "world chests off (part.chests)";
  return "world chests: the first open / break of a world container makes its undocumented gear unidentified (player-placed containers and islands never touched; players known: " + (KNOWN_OK ? String.valueOf(KNOWN.size()) : "reading") + ")";
}""")

# ================================================================= 0.1.3 GearKnownTask (the player list)
gknt.addInterface(pool.get("java.lang.Runnable"))
C(gknt, "public GearKnownTask() { }")
M(gknt, r"""
public static void later(long s) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearKnownTask(), s, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
}""")
M(gknt, r"""
public void run() {
  boolean ok = false;
  try { ok = @PKG@.GearChestOpen.refreshKnown(); } catch (Throwable t) { ok = false; }
  later(ok ? %dL : %dL);
}""" % (KNOWN_EVERY_S, KNOWN_RETRY_S))

# ================================================================= 0.1.3 GearChestOpenSys (UseBlockEvent$Pre) + GearChestBreakSys (BreakBlockEvent)
# Both on the player (PLAYER_Q), world thread, inside the engine's own interaction (OpenContainerInteraction itself reads and changes the
# chunk store from there). An event another system already cancelled is left alone.
event_system(gcos, "GearChestOpenSys", CO["UBPRE"], PLAYER_Q, r"""
    @UBPRE@ e = (@UBPRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CHESTS) return;
    @VECI@ tb = e.getTargetBlock();
    if (tb == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @PKG@.GearChestOpen.process(((@EST@) ext).getWorld(), tb.x(), tb.y(), tb.z(), pr.getUuid(), pr.getUsername(), "open");""")
event_system(gcbs, "GearChestBreakSys", CO["BBE"], PLAYER_Q, r"""
    @BBE@ e = (@BBE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CHESTS) return;
    @VECI@ tb = e.getTargetBlock();
    if (tb == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @PKG@.GearChestOpen.process(((@EST@) ext).getWorld(), tb.x(), tb.y(), tb.z(), null, pr == null ? "?" : pr.getUsername(), "break");""")

# ================================================================= GearChestMark / GearChestTag around StashPlugin$StashSystem (5.5 chests)
def chest_system(cls, ctor, order, body):
    F(cls, "public @QRY@ query;")
    F(cls, "public java.util.Set deps;")
    if ctor == "GearChestMark":
        F(cls, "public static Class STASH;")
    C(cls, r"""
public %s(boolean ordered) {
  super();
  this.query = @QRY@.and(new @QRY@[] { (@QRY@) @ICB@.getComponentType(), (@QRY@) @BSI@.getComponentType() });
  this.deps = new java.util.HashSet();
  if (ordered && @PKG@.GearChestMark.STASH != null) this.deps.add(new @SDEP@(@ORD@.%s, @PKG@.GearChestMark.STASH));
}""" % (ctor, order))
    M(cls, "public @QRY@ getQuery() { return this.query; }")
    M(cls, "public java.util.Set getDependencies() { return this.deps; }")
    M(cls, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ store, @CB@ cb) {
  try {
%s
  } catch (Throwable t) { @PKG@.Gear.warnOnce("%s", "%s failed: " + t); }
}""" % (body, ctor, ctor))
    M(cls, "public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ store, @CB@ cb) { }")


# BEFORE the stash roll: a container that has a drop list now (only world generation / prefabs / an admin set one) is remembered
# (0.1.3: one that carries a placer is also remembered per world as a loot container, GearChestOpen.lootMark; review of 0.1.3
# finding 3a: a container made at runtime (AddReason.SPAWN) without a placer first forgets a W / T / L record at its spot)
chest_system(gcm1, "GearChestMark", "BEFORE", r"""
    if (!@PKG@.GearCfg.PART_CHESTS) return;
    @ICB@ icb = (@ICB@) store.getComponent(ref, @ICB@.getComponentType());
    if (icb == null) return;
    if (reason == @ADDR@.SPAWN) @PKG@.GearChestOpen.spawned(store, ref);
    String dl = icb.getDroplist();
    if (dl == null || dl.length() == 0) return;
    @PKG@.GearTag.chestMark(ref, dl);
    @PKG@.GearChestOpen.lootMark(store, ref, dl);""")
# AFTER the stash roll, still inside the engine's own add: every undocumented gear stack in that container becomes unidentified,
# before any player can open the chest (spec 5.5 chests step 2-3)
chest_system(gcm2, "GearChestTag", "AFTER", r"""
    String dl = @PKG@.GearTag.chestTake(ref);
    if (dl == null || !@PKG@.GearCfg.PART_CHESTS) return;
    @ICB@ icb = (@ICB@) store.getComponent(ref, @ICB@.getComponentType());
    if (icb == null) return;
    @PKG@.GearTag.tagContainer(icb.getItemContainer(), "droplist " + dl + " in " + @PKG@.GearTag.key(store.getExternalData()));""")
C(gcm1U, "public GearChestMarkU() { super(false); }")
C(gcm2U, "public GearChestTagU() { super(false); }")

# ================================================================= review of 0.1.3: GearChunkRegen (finding 3b) + GearWorldBye (finding 4)
# GearChunkRegen (ChunkStore RefSystem on WorldChunk): Hytale's own regenerated-chunk test (TriggerVolumeChunkRegenSystem: the chunk
# entity added with AddReason.SPAWN + ChunkFlag.NEWLY_GENERATED) -> every container record in that chunk column is forgotten (a first
# generation has none there: one map lookup). Not behind part.chests: forgetting is always right.
F(gcrg, "public @QRY@ query;")
C(gcrg, "public GearChunkRegen() { super(); this.query = (@QRY@) @WCHK@.getComponentType(); }")
M(gcrg, "public @QRY@ getQuery() { return this.query; }")
M(gcrg, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ store, @CB@ cb) {
  try {
    if (reason != @ADDR@.SPAWN) return;
    @WCHK@ wc = (@WCHK@) cb.getComponent(ref, @WCHK@.getComponentType());
    if (wc == null || !wc.is(@CFLAG@.NEWLY_GENERATED)) return;
    Object ext = store.getExternalData();
    @WLD@ w = ext instanceof @CHS@ ? ((@CHS@) ext).getWorld() : null;
    if (w == null) return;
    int n = @PKG@.GearOpened.regen(@PKG@.GearChestOpen.wkey(w), wc.getX(), wc.getZ());
    if (n > 0) @PKG@.GearLog.line("CHEST forget " + n + " container record(s) in the regenerated chunk " + wc.getX() + " " + wc.getZ() + " of " + w.getName() + " - decided again on their next open");
  } catch (Throwable t) { @PKG@.Gear.warnOnce("chunkregen", "regenerated chunk check failed: " + t); }
}""")
M(gcrg, "public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ store, @CB@ cb) { }")
# GearWorldBye (RemoveWorldEvent, registerGlobal like Hytale's own plugins): write the queued memory lines, drop the world's maps
gwby.addInterface(pool.get("java.util.function.Consumer"))
C(gwby, "public GearWorldBye() { }")
M(gwby, r"""
public void accept(Object ev) {
  try {
    @RWE@ e = (@RWE@) ev;
    if (e.isCancelled() || e.getWorld() == null) return;
    @PKG@.GearOpened.evict(@PKG@.GearChestOpen.wkey(e.getWorld()));
  } catch (Throwable t) { @PKG@.Gear.warnOnce("worldbye", "world removal cleanup failed: " + t); }
}""")

# ================================================================= GearFxInvSys (armor changes apply at once) + GearByeB (cleanup)
# engine review 5: only an event of the ARMOR container runs the armor pass (the weapon side needs nothing here: the gate is judged
# per hit and gear:stats is published by GearTick). Engine review 1: this pass never grows a lock (raise = false).
event_system(gfxi, "GearFxInvSys", ICE, PLAYER_Q, r"""
    @ICE@ ie = (@ICE@) ev;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null) return;
    @IC@ armor = p.getInventory().getArmor();
    if (armor == null || (ie.getItemContainer() != armor && !(ie.getInventory() instanceof @ARMC@))) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.GearFx.armorPass(pr.getUuid(), pr, buf, r, armor, false);""")
# GearLockSys (engine review 1): every tick, ordered BEFORE EntityStatsSystems$Recalculate, for the players that carry a lock: when
# an armor stack changed since the lock was written, the lock shrinks to the container's new want before the engine can drop the
# unequipped piece's +sum (lower-only; the 1 s tick grows locks). Four identity compares per locked player per tick otherwise.
# Follow-up review 5: lock modifiers are saved with the player, so a player not in LOCKED is checked ONCE per join / world switch
# (GearReady clears PRIMED) for a lock that came back from disk; one is found -> the lower-only pass runs and LOCKED knows it.
F(glks, "public java.util.Set deps;")
F(glks, "public static Class RECALC;")
F(glks, "public @QRY@ query;")
C(glks, r"""
public GearLockSys(boolean ordered) {
  super();
  this.deps = new java.util.HashSet();
  if (ordered && RECALC != null) this.deps.add(new @SDEP@(@ORD@.BEFORE, RECALC));
  this.query = null;
}""")
M(glks, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @PLA@.getComponentType(), (@QRY@) @ARMC@.getComponentType(), (@QRY@) @ESM@.getComponentType() });
  return this.query;
}""")
M(glks, "public java.util.Set getDependencies() { return this.deps; }")
M(glks, "public boolean isParallel(int a, int b) { return false; }")
M(glks, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    Object snap = @PKG@.GearFx.LOCKED.get(u);
    if (snap == null) {
      if (@PKG@.GearFx.PRIMED.putIfAbsent(u, Boolean.TRUE) != null) return;
      @ESM@ m0 = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
      if (!@PKG@.GearFx.hasLock(m0)) return;
      @ARMC@ ac0 = (@ARMC@) chunk.getComponent(idx, @ARMC@.getComponentType());
      @PKG@.GearFx.lowerNow(u, m0, ac0 == null ? null : ac0.getInventory(), @PKG@.GearArmor.brokenFactor(store.getExternalData()));
      return;
    }
    @ARMC@ ac = (@ARMC@) chunk.getComponent(idx, @ARMC@.getComponentType());
    @IC@ armor = ac == null ? null : ac.getInventory();
    if (@PKG@.GearFx.sameStacks((Object[]) snap, armor)) return;
    @ESM@ m = (@ESM@) chunk.getComponent(idx, @ESM@.getComponentType());
    @PKG@.GearFx.lowerNow(u, m, armor, @PKG@.GearArmor.brokenFactor(store.getExternalData()));
  } catch (Throwable t) { @PKG@.Gear.warnOnce("locksys", "armor lock pass failed: " + t); }
}""")
C(glksU, "public GearLockSysU() { super(false); }")
gbyb.addInterface(pool.get("java.util.function.Consumer"))
C(gbyb, "public GearByeB() { }")
M(gbyb, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDEV@) ev).getPlayerRef();
    if (pr != null) @PKG@.GearFx.forget(pr.getUuid());
  } catch (Throwable t) { }
}""")

# ================================================================= GearFx.setup: every PART B registration (PARTB_SETUP calls it)
# ordered registrations fall back to an unordered class + one WARN (spec 5.5; SkyyExploration ChestSpawnLateSys pattern)
M(gfx, r"""
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}""")
M(gfx, r"""
public static void setup(@JPLG@ pl) {
  Class adr = cls("@ADRC@");
  @PKG@.GearHitSys.ADR = adr;
  @PKG@.GearArmorSys.ADR = adr;
  @PKG@.GearTrueSys.AFTERSYS = @PKG@.GearArmorSys.class;
  if (adr == null) @PKG@.Gear.warn("DamageSystems$ArmorDamageReduction not found - under-level armor keeps its native resistance (spec 3.5 part 3 off) and the per-stack armor resistance of 0.2.1 (base.armorOn) does not apply; Health by level still does");
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearShotTrack()); } catch (Throwable t0) { @PKG@.Gear.warn("GearShotTrack could not be registered: " + t0); }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearHitSys(true)); }
  catch (Throwable t1) {
    @PKG@.Gear.warn("could not order GearHitSys before ArmorDamageReduction (" + t1 + ") - unordered fallback: under-level armor keeps its native resistance and the per-stack armor resistance of 0.2.1 (base.armorOn) does not apply this start (weapon damage by level and Health by level still do)");
    try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearHitSysU()); } catch (Throwable t1b) { @PKG@.Gear.warn("GearHitSysU could not be registered: " + t1b); }
  }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearArmorSys(true)); }
  catch (Throwable t2) {
    @PKG@.Gear.warn("could not order GearArmorSys after ArmorDamageReduction (" + t2 + ") - unordered fallback: Defense only");
    try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearArmorSysU()); } catch (Throwable t2b) { @PKG@.Gear.warn("GearArmorSysU could not be registered: " + t2b); }
  }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearTrueSys(true)); }
  catch (Throwable t3) {
    @PKG@.Gear.warn("could not order GearTrueSys after GearArmorSys (" + t3 + ") - unordered fallback: armor may reduce True Damage");
    try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearTrueSysU()); } catch (Throwable t3b) { @PKG@.Gear.warn("GearTrueSysU could not be registered: " + t3b); }
  }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearLeechSys(false)); } catch (Throwable t4) { @PKG@.Gear.warn("GearLeechSys could not be registered: " + t4); }
  Class ddi = cls("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems");
  @PKG@.GearDeathMark.DDI = ddi;
  try {
    pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearDeathMark(true));
    if (ddi == null) @PKG@.Gear.warn("NPCDamageSystems$DropDeathItems not found - the death-drop mark runs unordered (mob gear may stay Normal)");
  } catch (Throwable t5) {
    @PKG@.Gear.warn("could not order the death-drop mark before NPCDamageSystems$DropDeathItems (" + t5 + ") - unordered fallback (mob gear may stay Normal)");
    try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearDeathMarkU()); } catch (Throwable t5b) { @PKG@.Gear.warn("GearDeathMarkU could not be registered: " + t5b); }
  }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearDropSys()); } catch (Throwable t6) { @PKG@.Gear.warn("GearDropSys could not be registered: " + t6); }
  Class stash = cls("com.hypixel.hytale.builtin.adventure.stash.StashPlugin$StashSystem");
  @PKG@.GearChestMark.STASH = stash;
  if (stash == null) @PKG@.Gear.warn("StashPlugin$StashSystem not found - nobody fills world loot chests, chest tagging runs unordered");
  try { pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearChestMark(true)); }
  catch (Throwable t7) {
    @PKG@.Gear.warn("could not order the loot chest mark before StashPlugin$StashSystem (" + t7 + ") - Hytale:Stash is not loaded; unordered fallback");
    try { pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearChestMarkU()); } catch (Throwable t7b) { @PKG@.Gear.warn("GearChestMarkU could not be registered: " + t7b); }
  }
  try { pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearChestTag(true)); }
  catch (Throwable t8) {
    @PKG@.Gear.warn("could not order the loot chest tag after StashPlugin$StashSystem (" + t8 + ") - unordered fallback");
    try { pl.getChunkStoreRegistry().registerSystem(new @PKG@.GearChestTagU()); } catch (Throwable t8b) { @PKG@.Gear.warn("GearChestTagU could not be registered: " + t8b); }
  }
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearFxInvSys()); } catch (Throwable t9) { @PKG@.Gear.warn("GearFxInvSys could not be registered: " + t9); }
  Class recalc = cls("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsSystems$Recalculate");
  @PKG@.GearLockSys.RECALC = recalc;
  if (recalc == null) @PKG@.Gear.warn("EntityStatsSystems$Recalculate not found - the armor lock pass runs unordered (GearFxInvSys still lowers locks on armor changes)");
  try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearLockSys(true)); }
  catch (Throwable t10) {
    @PKG@.Gear.warn("could not order the armor lock pass before EntityStatsSystems$Recalculate (" + t10 + ") - unordered fallback");
    try { pl.getEntityStoreRegistry().registerSystem(new @PKG@.GearLockSysU()); } catch (Throwable t10b) { @PKG@.Gear.warn("GearLockSysU could not be registered: " + t10b); }
  }
  @PKG@.GearMove.checkProto("SkyyGear");
  pl.getEventRegistry().registerGlobal(@PDEV@.class, new @PKG@.GearByeB());
  if (LIMITS.length() > 0) @PKG@.Gear.info("known limit (spec 3.5 part 4): under-level armor keeps these rarely used vanilla effects: " + LIMITS);
}""")

# GearTick: 1 s per player (world thread). Re-reads the gate levels (spec 3.3 / 3.6 / 6.3) and marks the player dirty when a level,
# the class skill, the profile or the config changed, so the scan re-renders exactly the items whose visible lines changed.
F(gtk, "public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();")
F(gtk, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")
F(gtk, "public static boolean FAILED_ONCE = false;")
C(gtk, "public GearTick() { super(); }")
M(gtk, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(gtk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    float[] c = (float[]) CLOCK.get(u);
    if (c == null) { c = new float[] { 0.0f }; CLOCK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    c[0] = 0.0f;
    Object ext = store.getExternalData();
    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @INV@ inv = p.getInventory();
    boolean dirty = @PKG@.GearGate.refresh(u);
    long ce = @PKG@.GearCfg.cfgEpoch();
    Object se = SEEN.get(u);
    if (!(se instanceof Long) || ((Long) se).longValue() != ce) { SEEN.put(u, Long.valueOf(ce)); dirty = true; }
    if (dirty) @PKG@.GearStamp.dirty(pr, w);
    // spec 7.1: gear:stats:<uuid> = the active totals (held weapon + worn armor that is identified and meets its gate), read by
    // gear:fn:stats; republished only when it changed. PART B applies these totals in combat; this only publishes them.
    String ss = @PKG@.GearStats.statsString(@PKG@.GearStats.totalsInv(u, inv, false));
    if (!ss.equals(@PKG@.Gear.bget("gear:stats:" + u))) @PKG@.Gear.bridge().put("gear:stats:" + u, ss);
    // ---- PART B PLUGS IN HERE (4/4): stat effects (PARTB_TICK) ----
@PARTBTICK@
    // 0.1.3: open world containers -> loot window / backup decision
    @PKG@.GearChestOpen.second(p, pr, w);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.Gear.warn("gear tick failed (logged once): " + t); }
  }
}""".replace("@PARTBTICK@", PARTB_TICK))

# ================================================================= GearRefreshTask (PlayerReadyEvent, every world switch; idempotent)
grft.addInterface(pool.get("java.lang.Runnable"))
F(grft, "public @PR@ pr;")
F(grft, "public boolean onWorld;")
F(grft, "public int tries;")
F(grft, "public java.util.UUID hopWorld;")
C(grft, "public GearRefreshTask(@PR@ pr) { this.pr = pr; this.onWorld = false; this.tries = 0; this.hopWorld = null; }")
M(grft, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(grft, r"""
public void again(String why) {
  this.tries = this.tries + 1;
  if (this.tries < 15) { later(2000L); return; }
  String who = "?";
  try { who = this.pr.getUsername(); } catch (Throwable t) { who = "?"; }
  @PKG@.Gear.warn("gear refresh gave up for " + who + " after " + this.tries + " tries (" + why + "); the next inventory change or relog tries again");
}""")
# spec 8.4: SkyyRolls still enabled next to SkyyGear -> one WARN and a line for admins at join
M(grft, r"""
public static void rollsWarn(@PR@ pr) {
  try {
    if (@PKG@.Gear.bget("config:def:SkyyRolls") == null) return;
    @PKG@.Gear.warnOnce("rolls", "SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED); both mods register /reforge");
    java.util.UUID u = pr.getUuid();
    if (@PKG@.Gear.admin(u) && @PKG@.Gear.once("rollswarn:" + u)) pr.sendMessage(@MSG@.raw("[Gear] SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED). SkyyGear replaces it.").color(@PKG@.GearDefs.C_GOLD));
  } catch (Throwable t) { }
}""")
M(grft, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) { again("player is in no world"); return; }
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) { again("world " + wu + " is not loaded"); return; }
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }
    java.util.UUID now = this.pr.getWorldUuid();
    if (now == null || !now.equals(this.hopWorld)) { again("player changed world"); return; }
    if (@PKG@.Gear.busy(this.pr.getUuid())) { again("SkyyProfiles profile:busy is still set"); return; }
    @INV@ inv = @PKG@.GearStamp.invOf(this.pr);
    if (inv == null) { again("player inventory not ready"); return; }
    @PKG@.GearGate.refresh(this.pr.getUuid());
    int[] cnt = @PKG@.GearStamp.scan(this.pr, inv);
    if (cnt[0] + cnt[1] + cnt[2] > 0) @PKG@.Gear.info("join refresh " + this.pr.getUsername() + ": stamped " + cnt[0] + ", migrated " + cnt[1] + ", re-rendered " + cnt[2]);
    rollsWarn(this.pr);
  } catch (Throwable t) { @PKG@.Gear.warn("gear refresh failed: " + t); }
}""")
grdy.addInterface(pool.get("java.util.function.Consumer"))
C(grdy, "public GearReady() { }")
M(grdy, r"""
public void accept(Object ev) {
  try {
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    // follow-up review 5: GearLockSys looks once more for lock modifiers saved with the player (join / world switch)
    @PKG@.GearFx.PRIMED.remove(pr.getUuid());
    @PKG@.GearChestOpen.seen(pr.getUuid());
    // review of 0.1.3 finding 5: read this world's container memory on the scheduler now, not on the world thread at the first open
    try {
      java.util.UUID wu = pr.getWorldUuid();
      @WLD@ pw = wu == null ? null : @UNI@.get().getWorld(wu);
      @PKG@.GearOpened.prefetch(@PKG@.GearChestOpen.wkey(pw));
    } catch (Throwable t2) { }
    new @PKG@.GearRefreshTask(pr).later(2000L);
  } catch (Throwable t) { @PKG@.Gear.warn("ready handler failed: " + t); }
}""")
PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"
B.probe(pool, PDE, "getPlayerRef")
gbye = mk("GearBye")
gbye.addInterface(pool.get("java.util.function.Consumer"))
C(gbye, "public GearBye() { }")
M(gbye, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((%s) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.GearGate.forget(u);
    @PKG@.GearStamp.forget(u);
    @PKG@.GearTick.CLOCK.remove(u);
    @PKG@.GearTick.SEEN.remove(u);
    @PKG@.GearCharged.forget(u);
    @PKG@.Gear.bridge().remove("gear:stats:" + u);
  } catch (Throwable t) { }
}""" % PDE)

# ================================================================= GearUi: vanilla styles (spec 5.8) - FOR THE SHARED HELPER (RESUME step 5)
# ui.frames ON (default) = the vanilla textures / sounds / scrolling list; OFF = flat vanilla colours, a paged list, no textures
# (only markup the live Skyy pages already use) - the in-game safety valve if an inline texture path does not resolve.
V_SND_LIGHT = ('Sounds: (Activate: (SoundPath: \\"Sounds/ButtonsLightActivate.ogg\\", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), '
               'MouseHover: (SoundPath: \\"Sounds/ButtonsLightHover.ogg\\", Volume: 6))')
V_SND_CANCEL = ('Sounds: (Activate: (SoundPath: \\"Sounds/ButtonsCancelActivate.ogg\\", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6), '
                'MouseHover: (SoundPath: \\"Sounds/ButtonsLightHover.ogg\\", Volume: 6))')
M(gui, "public static boolean tex() { return @PKG@.GearCfg.UI_FRAMES; }")
M(gui, r"""
public static String lbl(String color) {
  return "LabelStyle: (FontSize: 17, TextColor: " + color + ", RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12)";
}""")
# kind 0 = @DefaultTextButtonStyle, 1 = @SecondaryTextButtonStyle, 2 = @CancelTextButtonStyle, 3 = the Disabled look
M(gui, r"""
public static String btn(int kind) {
  String col = kind == 1 ? "#bdcbd3" : (kind == 3 ? "#797b7c" : "#bfcdd5");
  String ls = lbl(col);
  if (!tex()) {
    String d = kind == 2 ? "#5a2a26" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#2b3542" : "#2c4a66"));
    String h = kind == 2 ? "#6e332e" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#34404f" : "#355a7c"));
    String p = kind == 2 ? "#44201d" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#222a35" : "#223a50"));
    return "Style: TextButtonStyle(Default: (Background: " + d + ", " + ls + "), Hovered: (Background: " + h + ", " + ls + "), Pressed: (Background: " + p + ", " + ls + "));";
  }
  String b1;
  String b2;
  String b3;
  if (kind == 0) {
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/Primary.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b2 = "PatchStyle(TexturePath: \"Common/Buttons/Primary_Hovered.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b3 = "PatchStyle(TexturePath: \"Common/Buttons/Primary_Pressed.png\", VerticalBorder: 12, HorizontalBorder: 80)";
  } else if (kind == 3) {
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/Disabled.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b2 = b1;
    b3 = b1;
  } else {
    String t = kind == 2 ? "Destructive" : "Secondary";
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + ".png\", Border: 12)";
    b2 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + "_Hovered.png\", Border: 12)";
    b3 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + "_Pressed.png\", Border: 12)";
  }
  String snd = kind == 2 ? "@SNDCANCEL@" : "@SNDLIGHT@";
  return "Style: TextButtonStyle(Default: (Background: " + b1 + ", " + ls + "), Hovered: (Background: " + b2 + ", " + ls + "), Pressed: (Background: " + b3 + ", " + ls + "), " + snd + ");";
}""".replace("@SNDCANCEL@", V_SND_CANCEL).replace("@SNDLIGHT@", V_SND_LIGHT))
# the ItemRepairElement.ui row: hover #000000(0.2); the selected row keeps a darker Default background
M(gui, r"""
public static String rowStyle(boolean on) {
  if (on) return "Style: ButtonStyle(Default: (Background: #000000(0.35)), Hovered: (Background: #000000(0.35)), Pressed: (Background: #000000(0.4)));";
  return "Style: ButtonStyle(Default: (Background: #000000(0.05)), Hovered: (Background: #000000(0.2)), Pressed: (Background: #000000(0.3)));";
}""")
M(gui, r"""
public static String scroll() {
  return "ScrollbarStyle: (Spacing: 6, Size: 6, Background: (TexturePath: \"Common/Scrollbar.png\", Border: 3), Handle: (TexturePath: \"Common/ScrollbarHandle.png\", Border: 3), HoveredHandle: (TexturePath: \"Common/ScrollbarHandleHovered.png\", Border: 3), DraggedHandle: (TexturePath: \"Common/ScrollbarHandleDragged.png\", Border: 3));";
}""")
M(gui, r"""
public static String vsep() {
  if (tex()) return "Group { Anchor: (Width: 6); Background: (TexturePath: \"Common/ContainerVerticalSeparator.png\"); }";
  return "Group { Anchor: (Width: 2); Background: #2b3542; }";
}""")
# the @DecoratedContainer frame: ContainerHeader title bar with the @Title label, ContainerPatch body (#SkyyGBody, LayoutMode Top,
# padding 17), top + bottom decorations. The root Group only has Width / Height (HANDOFF section 2).
M(gui, r"""
public static void frame(@UCB@ b, String title, int w, int h) {
  boolean t = tex();
  b.appendInline((String) null, "Group #SkyyGRoot { Anchor: (Width: " + w + ", Height: " + h + "); }");
  String head = t ? "(TexturePath: \"Common/ContainerHeader.png\", HorizontalBorder: 50, VerticalBorder: 0)" : "#1b2533(0.98)";
  b.appendInline("#SkyyGRoot", "Group #SkyyGTitle { Anchor: (Height: 38, Top: 0); Padding: (Top: 7); Background: " + head + "; Label #SkyyGTitleTxt { Padding: (Horizontal: 19); Text: \"\"; Style: (FontSize: 15, VerticalAlignment: Center, HorizontalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: \"Secondary\", RenderBold: true); } }");
  if (t) b.appendInline("#SkyyGTitle", "Group #SkyyGDecoTop { Anchor: (Width: 236, Height: 11, Top: -12); Background: \"Common/ContainerDecorationTop.png\"; }");
  String body = t ? "(TexturePath: \"Common/ContainerPatch.png\", Border: 23)" : "#0e1620(0.97)";
  b.appendInline("#SkyyGRoot", "Group #SkyyGBody { Anchor: (Top: 38); LayoutMode: Top; Padding: (Full: 17); Background: " + body + "; }");
  if (t) b.appendInline("#SkyyGRoot", "Group #SkyyGDecoBot { Anchor: (Width: 236, Height: 11, Bottom: -6); Background: \"Common/ContainerDecorationBottom.png\"; }");
  b.set("#SkyyGTitleTxt.Text", title);
}""")
# info line: "+" done (white), "-" refused / failed (vanilla gold highlight), "=" neutral (vanilla label colour)
M(gui, r"""
public static String infoColor(String res) {
  if (res == null || res.length() == 0) return @PKG@.GearDefs.C_LABEL;
  char c = res.charAt(0);
  if (c == '+') return "#ffffff";
  if (c == '-') return @PKG@.GearDefs.C_GOLD;
  return @PKG@.GearDefs.C_LABEL;
}""")
M(gui, r"""
public static String infoText(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")

# ================================================================= ReforgePage (spec 5.4 + 5.8): the vanilla item-repair page look
for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
           "public String selFp;", "public String info;", "public boolean fresh;", "public String epoch;", "public long lastForge;",
           "public @BD@ before;", "public @BD@ after;"):
    F(rpg, _f)
C(rpg, r"""
public ReforgePage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null;
  this.info = ""; this.fresh = false; this.lastForge = 0L; this.before = null; this.after = null;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
}""")
M(rpg, r"""
public void clearSel() {
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null; this.fresh = false; this.before = null; this.after = null;
}""")
# re-picking the item already on the anvil keeps the Before / After columns (same slot, fingerprint and profile epoch)
M(rpg, r"""
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  String ep = @PKG@.Gear.epoch(this.playerRef.getUuid());
  String f = @PKG@.GearForge.fp(it);
  if (s == this.selSec && slot == this.selSlot && f.equals(this.selFp) && ep.equals(this.epoch)) return true;
  this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = f;
  this.fresh = false; this.before = null; this.after = null;
  this.epoch = ep;
  this.info = "=" + @PKG@.Gear.itemName(it.getItemId()) + " is on the anvil.";
  return true;
}""")
M(rpg, r"""
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
M(rpg, r"""
public static String rarHex(int r) { return @PKG@.GearDefs.R_PAGEHEX[@PKG@.GearCfg.ri(r)]; }""")
# one column of lines (the current roll, or Before / After) into a parent group
M(rpg, r"""
public static void column(@UCB@ b, String parent, String cid, String head, String headCol, String id, @BD@ d, int w) {
  b.appendInline(parent, "Group " + cid + " { Anchor: (Width: " + w + "); LayoutMode: Top; }");
  b.appendInline(cid, "Label " + cid + "H { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + headCol + ", VerticalAlignment: Center); }");
  b.set(cid + "H.Text", head);
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  if (d != null && @PKG@.GearData.identified(d)) @PKG@.GearView.statLines(id, d, txt, col);
  else if (d != null) { txt.add("Unidentified - identify it first" + (@PKG@.GearCfg.IDENTIFY_CMD ? " (/identify)." : ".")); col.add(@PKG@.GearDefs.C_GRAY); }
  if (txt.isEmpty()) { txt.add("No modifiers yet - a reforge rolls them."); col.add(@PKG@.GearDefs.C_GRAY); }
  for (int i = 0; i < txt.size() && i < 12; i++) {
    String c = (String) col.get(i);
    b.appendInline(cid, "Label " + cid + "L" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + (c == null ? "#ffffff" : c) + ", VerticalAlignment: Center); }");
    b.set(cid + "L" + i + ".Text", (String) txt.get(i));
  }
}""")
M(rpg, r"""
public void anvil(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  b.appendInline("#SkyyGMain", "Group #SkyyGAnvil { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGAnvilT.Text", "Anvil");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  if (sel != null) b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(sel.getItemId()) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  if (sel == null) {
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGSelName.Text", "The anvil is empty");
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
    b.set("#SkyyGSelSub.Text", "Pick an item from Your gear - it stays in its own slot.");
    b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGCostH { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGCostH.Text", "Reforge cost by rarity");
    for (int r = 0; r < @PKG@.GearDefs.NR; r++) {
      b.appendInline("#SkyyGAnvil", "Label #SkyyGCost" + r + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
      long per = @PKG@.GearCfg.CR_PER[r];
      b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": " + @PKG@.Gear.fmt(@PKG@.GearCfg.CR_BASE[r]) + " coins" + (per > 0L ? " + " + @PKG@.Gear.fmt(per) + " per item level" : ""));
    }
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow1 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow1.Text", "A reforge re-rolls every modifier for the item's rarity and level.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow2 { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow2.Text", "Tip: hold the item when you type /reforge to put it on the anvil.");
    return;
  }
  String id = sel.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, sel.getMetadata());
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  Object[] g = null;
  if (d != null) g = @PKG@.GearView.gateLine(u, id, d, lvl);
  b.set("#SkyyGSelSub.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + @PKG@.GearView.slotWord(id) + "   -   " + (g == null || ((String) g[0]).length() == 0 ? "Level " + lvl : (String) g[0]));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + (sel.getQuantity() > 1 ? " - stack of " + sel.getQuantity() + ": one item is reforged." : " - it stays there while you reforge it."));
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGCols { Anchor: (Height: 330); LayoutMode: Left; Padding: (Top: 6); }");
  if (this.fresh && this.before != null && this.after != null) {
    column(b, "#SkyyGCols", "#SkyyGColB", "Before", "#878e9c", id, this.before, 275);
    b.appendInline("#SkyyGCols", "Label { Anchor: (Width: 12); Text: \"\"; }");
    column(b, "#SkyyGCols", "#SkyyGColA", "After", "#ffffff", id, this.after, 275);
  } else {
    column(b, "#SkyyGCols", "#SkyyGColC", "Current modifiers", "#ffffff", id, d, 562);
  }
  long cost = @PKG@.GearCfg.costReforge(r, lvl);
  long have = @PKG@.GearForge.purse(u);
  String why = @PKG@.GearForge.refuse(sel, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(sel, @PKG@.GearStamp.giveOf(inv), "a reforge");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGCostTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGCostTxt.Text", cost > 0L ? "Cost: " + @PKG@.Gear.fmt(cost) + " coins (" + @PKG@.GearDefs.R_NAME[r] + ", level " + lvl + ")" : "Cost: free");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGPurse { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  boolean off = why != null || poor;
  // the button says only what happens (the gold cost line right above carries the number: inline button Text goes through safe(),
  // which would turn "1,000" into "1 000")
  String bt = why != null ? (d != null && !@PKG@.GearData.identified(d) ? "Identify it first" : "Cannot reforge") : (poor ? "Not enough coins" : "Reforge");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnForge { Anchor: (Width: 340, Height: 44); Text: \"" + @PKG@.Gear.safe(bt) + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnForge", @EVD@.of("a", "forge"));
}""")
M(rpg, r"""
public void list(@UCB@ b, @UEB@ ev, @INV@ inv) {
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Right: 15, Bottom: 5); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadItem { Anchor: (Width: 300); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadRar { Anchor: (Width: 150); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyGHeadItem.Text", "Your gear (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  int per = t ? 200 : 12;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (t) b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 634); LayoutMode: TopScrolling; " + @PKG@.GearUi.scroll() + " }");
  else b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 590); LayoutMode: Top; }");
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty1 { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty1.Text", "No weapons or armor on you.");
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty2 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty2.Text", "Carry one (hotbar, inventory, backpack or worn) and click Refresh.");
  }
  java.util.UUID u = this.playerRef.getUuid();
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (it.getQuantity() > 1 ? " x" + it.getQuantity() : "") + (on ? "  (on the anvil)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", (d == null ? "?" : @PKG@.GearDefs.R_NAME[r]) + " - Lv " + lvl);
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + i));
  }
  if (!t && pages > 1) {
    b.appendInline("#SkyyGListBox", "Group #SkyyGNav { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
  }
}""")
M(rpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.GearForge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The item on the anvil moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.GearForge.rows(inv);
  @PKG@.GearUi.frame(b, "Reforge", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Pick a weapon or armor piece. A reforge re-rolls its modifiers for coins - the rarity never changes.");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 680); LayoutMode: Left; Padding: (Top: 6); }");
  list(b, ev, inv);
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  anvil(b, ev, u, sel, inv);
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the reforge click: guard -> profile:busy -> selection -> epoch -> GearForge.reforge (same item, refusals, coins first, refund)
M(rpg, r"""
public void forge(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  this.lastForge = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was reforged. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from Your gear first."; return; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  @IC@ c = @PKG@.GearStamp.section(inv, this.selSec);
  String name = @PKG@.Gear.itemName(this.selId);
  Object[] res = @PKG@.GearForge.reforge(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.before = (@BD@) res[3];
    this.after = (@BD@) res[4];
    this.fresh = true;
    long cost = ((Long) res[5]).longValue();
    this.info = "+Reforged! Your " + name + " rolled new modifiers" + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)." : ".");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("That item moved")) clearSel();
  this.info = "-" + msg;
}""")
M(rpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; rebuild(); return; }
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t1) { }
      }
      close();
      return;
    }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("sel:")) {
      int i = -1;
      try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t) { i = -1; }
      if (i < 0 || this.rows == null || i >= this.rows.size()) return;
      int[] r = (int[]) this.rows.get(i);
      if (!pick(inv, r[0], r[1])) this.info = "-That item is not there any more.";
      rebuild();
      return;
    }
    if (a.equals("forge")) { forge(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Gear.warn("reforge page click failed: " + t); }
}""")

# ================================================================= /reforge (player command, same name as SkyyRolls - spec 8.1)
C(rfc, r"""
public ReforgeCmd() {
  super("reforge", "Open the Reforge page: re-roll the modifiers of a weapon or armor piece for coins");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(rfc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Reforge] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.ReforgePage page = new @PKG@.ReforgePage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/reforge failed: " + t);
    pr.sendMessage(@MSG@.raw("[Reforge] could not open the Reforge page - the server log has the details"));
  }
}""")

# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8). The identify core (GearIdent, write safety 1.7), the vanilla-look page (the /reforge
# page's frame, list rows, buttons and sounds from GearUi) and the player command.
# ####################################################################################################################################
# unidentified gear on the player, in the SCAN order (spec 5.7 page left side)
M(gidn, r"""
public static java.util.ArrayList rows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
      if (d == null || @PKG@.GearData.identified(d)) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });
    }
  }
  return out;
}""")
M(gidn, r"""
public static long costOf(@IS@ it) {
  if (it == null || it.isEmpty()) return 0L;
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
  if (d == null) return 0L;
  return @PKG@.GearCfg.costIdentify(@PKG@.GearData.rarity(d), @PKG@.GearLevel.level(it.getItemId(), d));
}""")
# why a stack cannot be identified (null = it can)
M(gidn, r"""
public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick an unidentified weapon or armor piece first.";
  String id = it.getItemId();
  if (!@PKG@.GearData.isGear(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor get identified.";
  int st = @PKG@.GearData.state(it.getMetadata());
  if (st == 3) return "The gear data on this item is unreadable - an admin can check it with /gear read.";
  if (st == 4) return "This item comes from a newer SkyyGear - it cannot be changed here.";
  if (d == null) return "The gear data on this item is unreadable.";
  if (@PKG@.GearData.identified(d)) return "It is already identified.";
  return null;
}""")
# spec 5.7 flow + 1.7 write safety (the GearForge.reforge shape): same id + fingerprint in the same slot, coins TAKEN FIRST, the
# modifiers roll for the item's rarity and level (GearRoll.identify: id true, idAt, idBy), the new stack goes into the SAME slot,
# REFUND on any failure. Object[] { Integer code (1 done, 0 refused, -1 failed), String message, IS new stack, BD before, BD after,
# Long cost, Object[] { container, Integer slot } of the rest of a stack or null }. No Smithing XP (none is designed).
# Follow-up review 3: a stack gives up ONE item (GearStamp.takeOne, after the coins; the rest keeps its unidentified document in a
# free storage / backpack slot, 5 always stay free); no room = refused before any coin moves ("Free N slots to split this stack").
M(gidn, r"""
public static Object[] identify(@IC@ c, int slot, String expId, String expFp, java.util.UUID u, String who, boolean free, @IC@[] give, @IC@[] all) {
  @IS@ it = null;
  try { if (c != null && slot >= 0 && slot < c.getCapacity()) it = c.getItemStack((short) slot); } catch (Throwable t0) { it = null; }
  if (!@PKG@.GearForge.same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L), null };
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "identify");
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L), null };
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  long cost = free ? 0L : @PKG@.GearCfg.costIdentify(r, lvl);
  if (cost > 0L) {
    int t = @PKG@.GearForge.take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L), null };
    if (t == 0) {
      long have = @PKG@.GearForge.purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: identifying it costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L), null };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " identify " + id);
  }
  @BD@ nd = null;
  @IS@ nu = null;
  Object tx = null;
  Object[] rest = null;
  Throwable err = null;
  try {
    if (it.getQuantity() > 1) {
      rest = @PKG@.GearStamp.takeOne(c, slot, give, all, u);
      if (rest == null) throw new IllegalStateException("the stack could not be split");
      it = c.getItemStack((short) slot);
      if (!@PKG@.GearForge.same(it, expId, expFp) || it.getQuantity() != 1) throw new IllegalStateException("the stack changed while it was split");
    }
    nd = @PKG@.GearRoll.identify(id, d, u);
    nu = @PKG@.GearData.put(it, nd, u);
    tx = c.setItemStackForSlot((short) slot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && nu != it && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || @PKG@.GearForge.refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("IDENTIFY FAILED for " + who + " (" + u + ") on " + id + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " identify " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "Identifying failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "Identifying failed and the refund did not go through - an admin can find it in the server log.", null, d, null, Long.valueOf(cost), rest };
  }
  @PKG@.GearLog.line("IDENTIFY " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + lvl + " [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + (free ? " (free)" : ""));
  return new Object[] { Integer.valueOf(1), "Identified!", nu, d, nd, Long.valueOf(cost), rest };
}""")
# spec 5.7 "Identify all" (exploit review 2): one by one, each paid on its own; a REFUSED row (no room to split a stack, not enough
# coins for this one, ...) is skipped and the rest go on; only a failed write (code -1, refunded) stops. bySec[s] = the container of
# inventory section s (GearStamp.section numbering). Follow-up review 3: a stack row gives up one item per identify and the rest of
# the stack (its new slot, identify's res[6]) is queued, so a stack is identified item by item until 5 free slots are left.
# recent collects "Name: modifiers" lines. Object[] { Integer done, Long spent, Integer skipped, String first skip reason,
# String stop reason }.
M(gidn, r"""
public static Object[] allIn(@IC@[] bySec, java.util.ArrayList rs, java.util.UUID u, String who, java.util.ArrayList recent) {
  int done = 0;
  int skipped = 0;
  long spent = 0L;
  String firstSkip = null;
  String stop = null;
  @IC@[] give = new @IC@[] { bySec.length > 1 ? bySec[1] : null, bySec.length > 2 ? bySec[2] : null };
  java.util.ArrayList work = new java.util.ArrayList();
  for (int i = 0; i < rs.size(); i++) {
    int[] rw = (int[]) rs.get(i);
    @IC@ c = rw[0] >= 0 && rw[0] < bySec.length ? bySec[rw[0]] : null;
    if (c != null) work.add(new Object[] { c, Integer.valueOf(rw[1]) });
  }
  for (int i = 0; i < work.size() && i < 4096; i++) {
    Object[] w = (Object[]) work.get(i);
    @IC@ c = (@IC@) w[0];
    int sl = ((Integer) w[1]).intValue();
    if (sl < 0 || sl >= c.getCapacity()) continue;
    @IS@ it = c.getItemStack((short) sl);
    if (it == null || it.isEmpty()) continue;
    String name = @PKG@.Gear.itemName(it.getItemId());
    Object[] res = identify(c, sl, it.getItemId(), @PKG@.GearForge.fp(it), u, who, false, give, bySec);
    int code = ((Integer) res[0]).intValue();
    if (code == 0) { skipped++; if (firstSkip == null) firstSkip = name + ": " + (String) res[1]; continue; }
    if (code != 1) { stop = (String) res[1]; break; }
    done++;
    spent = spent + ((Long) res[5]).longValue();
    if (res.length > 6 && res[6] instanceof Object[]) work.add(res[6]);
    String sum = @PKG@.GearView.modSummary((@BD@) res[4]);
    if (recent != null) recent.add(name + ": " + (sum.length() > 0 ? sum : "no modifiers"));
  }
  return new Object[] { Integer.valueOf(done), Long.valueOf(spent), Integer.valueOf(skipped), firstSkip, stop };
}""")
# the number of items (stack quantities) at the rows' slots
M(gidn, r"""
public static int items(@INV@ inv, java.util.ArrayList rs) {
  int n = 0;
  for (int i = 0; rs != null && i < rs.size(); i++) {
    int[] rw = (int[]) rs.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it != null && !it.isEmpty()) n = n + it.getQuantity();
  }
  return n;
}""")

# ================================================================= IdentifyPage (spec 5.7 + 5.8): the /reforge page's vanilla look
for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
           "public String selFp;", "public String info;", "public String epoch;", "public long lastClick;", "public @BD@ revealed;",
           "public java.util.ArrayList recent;"):
    F(ipg, _f)
C(ipg, r"""
public IdentifyPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.recent = new java.util.ArrayList();
  this.pageNo = 0;
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null;
  this.info = ""; this.lastClick = 0L; this.revealed = null;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
}""")
M(ipg, r"""
public void clearSel() {
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null; this.revealed = null;
}""")
M(ipg, r"""
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  @BD@ d = @PKG@.GearData.effective(it.getItemId(), it.getMetadata());
  if (d == null || @PKG@.GearData.identified(d)) return false;
  this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = @PKG@.GearForge.fp(it);
  this.revealed = null;
  this.info = "=" + @PKG@.GearView.nameText(it.getItemId(), d) + " is selected.";
  return true;
}""")
M(ipg, r"""
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
M(ipg, r"""
public long total(@INV@ inv) {
  long s = 0L;
  for (int i = 0; i < this.rows.size(); i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it != null && !it.isEmpty()) s = s + @PKG@.GearIdent.costOf(it) * (long) it.getQuantity();
  }
  return s;
}""")
M(ipg, r"""
public void detail(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  b.appendInline("#SkyyGMain", "Group #SkyyGDet { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGDet", "Label #SkyyGDetT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGDetT.Text", "Identify");
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGDet", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  if (sel != null) b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(sel.getItemId()) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  if (sel == null) {
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGSelName.Text", "Nothing selected");
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
    b.set("#SkyyGSelSub.Text", "Pick an item from Unidentified gear - it stays in its own slot.");
    b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #2b3542; }");
    if (!this.recent.isEmpty()) {
      b.appendInline("#SkyyGDet", "Label #SkyyGRecH { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
      b.set("#SkyyGRecH.Text", "Revealed");
      for (int i = 0; i < this.recent.size() && i < 14; i++) {
        b.appendInline("#SkyyGDet", "Label #SkyyGRec" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff, VerticalAlignment: Center); }");
        b.set("#SkyyGRec" + i + ".Text", (String) this.recent.get(i));
      }
      return;
    }
    b.appendInline("#SkyyGDet", "Label #SkyyGCostH { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGCostH.Text", "Identify cost by rarity");
    for (int r = 0; r < @PKG@.GearDefs.NR; r++) {
      b.appendInline("#SkyyGDet", "Label #SkyyGCost" + r + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
      long per = @PKG@.GearCfg.CI_PER[r];
      b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": " + @PKG@.Gear.fmt(@PKG@.GearCfg.CI_BASE[r]) + " coins" + (per > 0L ? " + " + @PKG@.Gear.fmt(per) + " per item level" : ""));
    }
    b.appendInline("#SkyyGDet", "Label #SkyyGHow1 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow1.Text", "The rarity is already set - identifying reveals the modifiers.");
    b.appendInline("#SkyyGDet", "Label #SkyyGHow2 { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow2.Text", "Unidentified weapons deal no damage and unidentified armor gives no stats.");
    return;
  }
  String id = sel.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, sel.getMetadata());
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  boolean done = d != null && @PKG@.GearData.identified(d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); }");
  Object[] g = null;
  if (d != null) g = @PKG@.GearView.gateLine(u, id, d, lvl);
  b.set("#SkyyGSelSub.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + @PKG@.GearView.slotWord(id) + "   -   " + (g == null || ((String) g[0]).length() == 0 ? "Level " + lvl : (String) g[0]));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + (sel.getQuantity() > 1 ? " - stack of " + sel.getQuantity() + ": one item is identified." : " - it stays there while you identify it."));
  b.appendInline("#SkyyGDet", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGDet", "Group #SkyyGCols { Anchor: (Height: 330); LayoutMode: Left; Padding: (Top: 6); }");
  if (done) {
    @BD@ show = d;
    if (this.revealed != null) show = this.revealed;
    @PKG@.ReforgePage.column(b, "#SkyyGCols", "#SkyyGColR", "Revealed", "#ffffff", id, show, 562);
  } else {
    b.appendInline("#SkyyGCols", "Group #SkyyGColU { Anchor: (Width: 562); LayoutMode: Top; }");
    b.appendInline("#SkyyGColU", "Label #SkyyGColUH { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGColUH.Text", "Unidentified");
    b.appendInline("#SkyyGColU", "Label #SkyyGColU1 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGColU1.Text", "Its modifiers appear when you identify it.");
    b.appendInline("#SkyyGColU", "Label #SkyyGColU2 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + @PKG@.GearDefs.C_BAD + ", VerticalAlignment: Center); }");
    b.set("#SkyyGColU2.Text", @PKG@.GearData.slotOf(id) == 2 ? "Gives no stats until identified." : "Cannot be used until identified.");
    b.appendInline("#SkyyGColU", "Label #SkyyGColU3 { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGColU3.Text", "The modifiers roll for its rarity and level the moment you pay.");
  }
  long cost = d == null ? 0L : @PKG@.GearCfg.costIdentify(r, lvl);
  long have = @PKG@.GearForge.purse(u);
  String why = @PKG@.GearIdent.refuse(sel, d);
  if (why == null) why = @PKG@.GearStamp.stackWhy(sel, @PKG@.GearStamp.giveOf(inv), "identify");
  b.appendInline("#SkyyGDet", "Label #SkyyGCostTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGCostTxt.Text", done ? "Identified" : (cost > 0L ? "Cost: " + @PKG@.Gear.fmt(cost) + " coins (" + @PKG@.GearDefs.R_NAME[r] + ", level " + lvl + ")" : "Cost: free"));
  b.appendInline("#SkyyGDet", "Label #SkyyGPurse { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  boolean off = done || why != null || poor;
  String bt = done ? "Identified" : (why != null ? "Cannot identify" : (poor ? "Not enough coins" : "Identify"));
  b.appendInline("#SkyyGDet", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnId { Anchor: (Width: 340, Height: 44); Text: \"" + @PKG@.Gear.safe(bt) + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnId", @EVD@.of("a", "id"));
}""")
M(ipg, r"""
public void list(@UCB@ b, @UEB@ ev, @INV@ inv) {
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Right: 15, Bottom: 5); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadItem { Anchor: (Width: 300); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadRar { Anchor: (Width: 150); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyGHeadItem.Text", "Unidentified gear (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  int per = t ? 200 : 11;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (t) b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 590); LayoutMode: TopScrolling; " + @PKG@.GearUi.scroll() + " }");
  else b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 540); LayoutMode: Top; }");
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty1 { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty1.Text", "No unidentified gear on you.");
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty2 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty2.Text", "Weapons and armor from mobs and loot chests arrive unidentified.");
  }
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.ReforgePage.rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (it.getQuantity() > 1 ? " x" + it.getQuantity() : "") + (on ? "  (selected)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", @PKG@.GearDefs.R_NAME[r] + " - Lv " + lvl);
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + i));
  }
  if (!t && pages > 1) {
    b.appendInline("#SkyyGListBox", "Group #SkyyGNav { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
  }
}""")
M(ipg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.GearForge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The selected item moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.GearIdent.rows(inv);
  long all = total(inv);
  long have = @PKG@.GearForge.purse(u);
  @PKG@.GearUi.frame(b, "Identify", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Gear from mobs and loot chests arrives unidentified. Pay coins to reveal its modifiers - the rarity is already set.");
  b.appendInline("#SkyyGBody", "Group #SkyyGTop { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); }");
  int n = @PKG@.GearIdent.items(inv, this.rows);
  boolean allOff = n == 0 || (have >= 0L && have < all && n == 1);
  String at = n == 0 ? "Nothing to identify" : (n == 1 ? "Identify 1 item" : "Identify all " + n + " items");
  b.appendInline("#SkyyGTop", "TextButton #SkyyGBtnAll { Anchor: (Width: 320, Height: 44); Text: \"" + @PKG@.Gear.safe(at) + "\"; " + @PKG@.GearUi.btn(allOff ? 3 : 1) + " }");
  b.appendInline("#SkyyGTop", "Label { Anchor: (Width: 18, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGTop", "Label #SkyyGAllCost { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGAllCost.Text", n == 0 ? "" : "Total: " + @PKG@.Gear.fmt(all) + " coins" + (have >= 0L ? " - your purse: " + @PKG@.Gear.fmt(have) : "") + " - each item is paid on its own");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnAll", @EVD@.of("a", "all"));
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 628); LayoutMode: Left; Padding: (Top: 6); }");
  list(b, ev, inv);
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  detail(b, ev, u, sel, inv);
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the click guard, profile:busy and the profile epoch (spec 1.7) come before any write; the page never holds an item copy
M(ipg, r"""
public boolean guard() {
  long now = System.currentTimeMillis();
  if (now - this.lastClick < 400L) return false;
  this.lastClick = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was identified. Try again in a moment."; return false; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.recent.clear(); this.epoch = ep; this.info = "-Your profile changed - the list was refreshed."; return false; }
  return true;
}""")
M(ipg, r"""
public void one(@INV@ inv) {
  if (!guard()) return;
  if (this.selSec < 0) { this.info = "-Pick an item from Unidentified gear first."; return; }
  java.util.UUID u = this.playerRef.getUuid();
  @IC@ c = @PKG@.GearStamp.section(inv, this.selSec);
  String name = @PKG@.Gear.itemName(this.selId);
  Object[] res = @PKG@.GearIdent.identify(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.revealed = (@BD@) res[4];
    long cost = ((Long) res[5]).longValue();
    String sum = @PKG@.GearView.modSummary(this.revealed);
    this.info = "+Identified your " + name + (sum.length() > 0 ? " - revealed: " + sum : "") + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)" : "");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("That item moved")) clearSel();
  this.info = "-" + msg;
}""")
# spec 5.7 "Identify all": one by one, each paid on its own; refused rows are skipped (exploit review 2), a failed write stops
M(ipg, r"""
public void all(@INV@ inv) {
  if (!guard()) return;
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList rs = @PKG@.GearIdent.rows(inv);
  if (rs.isEmpty()) { this.info = "-No unidentified gear on you."; return; }
  int want = @PKG@.GearIdent.items(inv, rs);
  clearSel();
  this.recent.clear();
  @IC@[] by = new @IC@[6];
  for (int s = 0; s < by.length; s++) by[s] = @PKG@.GearStamp.section(inv, s);
  Object[] r = @PKG@.GearIdent.allIn(by, rs, u, this.playerRef.getUsername(), this.recent);
  int done = ((Integer) r[0]).intValue();
  long spent = ((Long) r[1]).longValue();
  int skipped = ((Integer) r[2]).intValue();
  String first = (String) r[3];
  String stop = (String) r[4];
  String head = "Identified " + done + " of " + want + (done > 0 ? " for " + @PKG@.Gear.fmt(spent) + " coins" : "");
  if (stop != null) this.info = "-" + head + " - stopped: " + stop;
  else if (skipped > 0) this.info = "-" + head + " - skipped " + skipped + " (" + first + ")";
  else this.info = "+Identified " + done + (done == 1 ? " item" : " items") + " for " + @PKG@.Gear.fmt(spent) + " coins.";
}""")
M(ipg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; this.recent.clear(); this.epoch = @PKG@.Gear.epoch(this.playerRef.getUuid()); rebuild(); return; }
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t1) { }
      }
      close();
      return;
    }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("sel:")) {
      int i = -1;
      try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t) { i = -1; }
      if (i < 0 || this.rows == null || i >= this.rows.size()) return;
      int[] r = (int[]) this.rows.get(i);
      this.recent.clear();
      if (!pick(inv, r[0], r[1])) this.info = "-That item is not there any more.";
      rebuild();
      return;
    }
    if (a.equals("id")) { one(inv); rebuild(); return; }
    if (a.equals("all")) { all(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Gear.warn("identify page click failed: " + t); }
}""")

# ================================================================= /identify (player command; identify.command checked live - spec 5.7)
C(idc, r"""
public IdentifyCmd() {
  super("identify", "Open the Identify page: pay coins to reveal the modifiers of unidentified weapons and armor");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(idc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!@PKG@.GearCfg.IDENTIFY_CMD) { pr.sendMessage(@MSG@.raw("[Identify] /identify is switched off on this server - items are identified another way (an NPC).").color(@PKG@.GearDefs.C_GOLD)); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Identify] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.IdentifyPage page = new @PKG@.IdentifyPage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/identify failed: " + t);
    pr.sendMessage(@MSG@.raw("[Identify] could not open the Identify page - the server log has the details"));
  }
}""")

# ================================================================= GearAdmin: /gear bodies (world thread; admin writes are logged)
M(gad, r"""
public static void msg(@PR@ pr, String t) {
  try { pr.sendMessage(@MSG@.raw("[Gear] " + t)); } catch (Throwable x) { }
}""")
M(gad, r"""
public static @IC@ handC(@INV@ inv) {
  if (inv.usingToolsItem()) return inv.getTools();
  return inv.getHotbar();
}""")
M(gad, r"""
public static short handS(@INV@ inv) {
  if (inv.usingToolsItem()) return (short) inv.getActiveToolsSlot();
  return (short) inv.getActiveHotbarSlot();
}""")
M(gad, r"""
public static @IS@ hand(@INV@ inv) {
  @IC@ c = handC(inv);
  short s = handS(inv);
  if (c == null || s < 0 || s >= c.getCapacity()) return null;
  return c.getItemStack(s);
}""")
M(gad, r"""
public static String ok(Object tx) {
  if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return "  (the inventory REFUSED the change)";
  return "";
}""")
# the words after the sub-command word ("gear give iron sword --rarity rare" -> "iron sword --rarity rare")
M(gad, r"""
public static String rest(@CTX@ ctx, String word) {
  String line = "";
  try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
  if (line == null) return "";
  String[] tk = line.trim().split("\\s+");
  StringBuilder sb = new StringBuilder();
  boolean seen = false;
  for (int i = 0; i < tk.length; i++) {
    if (!seen) { if (tk[i].equalsIgnoreCase(word) || tk[i].equalsIgnoreCase("/" + word)) seen = true; continue; }
    if (sb.length() > 0) sb.append(' ');
    sb.append(tk[i]);
  }
  return sb.toString().trim();
}""")
# item name -> gear item id (or null + suggestions; SkyyRolls 0.1.2 resolve)
M(gad, r"""
public static String resolve(String q, StringBuilder sugg) {
  if (q == null) return null;
  String t = q.trim();
  if (t.length() == 0) return null;
  if (@PKG@.Gear.item(t) != null) return t;
  String norm = t.toLowerCase().replace(' ', '_');
  String[] words = t.toLowerCase().replace('_', ' ').trim().split(" ");
  java.util.ArrayList hits = new java.util.ArrayList();
  java.util.ArrayList good = new java.util.ArrayList();
  try {
    java.util.Iterator it = @ITM@.getAssetMap().getAssetMap().keySet().iterator();
    while (it.hasNext()) {
      String id = String.valueOf(it.next());
      if (id.length() == 0 || id.charAt(0) == '*') continue;
      String low = id.toLowerCase();
      if (low.equals(norm)) return id;
      boolean all = true;
      for (int i = 0; i < words.length; i++) { if (words[i].length() > 0 && low.indexOf(words[i]) < 0) { all = false; break; } }
      if (all) { hits.add(id); if (@PKG@.GearData.isGear(id)) good.add(id); }
    }
  } catch (Throwable e) { @PKG@.Gear.warn("item lookup failed: " + e); return null; }
  if (good.size() == 1) return (String) good.get(0);
  if (hits.size() == 1) return (String) hits.get(0);
  java.util.ArrayList show = good.size() > 0 ? good : hits;
  java.util.Collections.sort(show);
  for (int i = 0; i < show.size() && i < 8; i++) { if (sugg.length() > 0) sugg.append(", "); sugg.append((String) show.get(i)); }
  if (show.size() > 8) sugg.append(" ... (" + show.size() + " matches)");
  return null;
}""")
# storage first (engine rule), then hotbar, then backpack; true = it went in
M(gad, r"""
public static boolean give(@INV@ inv, @IS@ s) {
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    try {
      Object tx = cs[i].addItemStack(s);
      if (!(tx instanceof @TXN@) || ((@TXN@) tx).succeeded()) return true;
    } catch (Throwable t) { }
  }
  return false;
}""")
M(gad, r"""
public static void giveCmd(@PR@ pr, @INV@ inv, String rest) {
  String[] tk = rest.length() == 0 ? new String[0] : rest.split("\\s+");
  StringBuilder q = new StringBuilder();
  String rar = null;
  boolean unid = false;
  for (int i = 0; i < tk.length; i++) {
    String w = tk[i];
    if (w.equalsIgnoreCase("--rarity") && i + 1 < tk.length) { rar = tk[i + 1]; i++; continue; }
    if (w.equalsIgnoreCase("--unid")) {
      if (i + 1 < tk.length && !tk[i + 1].startsWith("--")) { String v = tk[i + 1].toLowerCase(); unid = v.equals("true") || v.equals("yes") || v.equals("1") || v.equals("on"); i++; }
      else unid = true;
      continue;
    }
    if (q.length() > 0) q.append(' ');
    q.append(w);
  }
  if (q.length() == 0) { msg(pr, "usage: /gear give <item> [--rarity <id>] [--unid true]"); return; }
  StringBuilder sugg = new StringBuilder();
  String id = resolve(q.toString(), sugg);
  if (id == null) { msg(pr, "no item matches '" + q + "'" + (sugg.length() > 0 ? ". Did you mean: " + sugg : "")); return; }
  if (!@PKG@.GearData.isGear(id)) { msg(pr, id + " is not gear - only Weapon_* (not ammo, shields, bombs ...) and Armor_* items"); return; }
  int r;
  if (rar != null) {
    r = @PKG@.GearDefs.rIndex(rar);
    if (r < 0) { msg(pr, "unknown rarity '" + rar + "' - normal, unique, rare, legendary, fabled, mythic, set"); return; }
  } else r = @PKG@.GearRoll.pickRarity(0);
  java.util.UUID u = pr.getUuid();
  @BD@ d = @PKG@.GearRoll.newDoc(id, r, !unid, "admin");
  @IS@ s = @PKG@.GearData.put(new @IS@(id, 1), d, u);
  boolean in = give(inv, s);
  @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " give " + id + " " + @PKG@.GearDefs.R_ID[r] + (unid ? " unidentified" : " [" + @PKG@.GearView.modSummary(d) + "]") + (in ? "" : " (inventory full)"));
  msg(pr, (in ? "gave " : "NOT given (inventory full): ") + @PKG@.GearView.nameText(id, d) + " - " + @PKG@.GearDefs.R_NAME[r] + (unid ? ", unidentified" : (@PKG@.GearView.modSummary(d).length() > 0 ? " - " + @PKG@.GearView.modSummary(d) : "")));
}""")
# /gear migrate [player] on another player: hop to that player's world thread, scan there, report back
gmt = mk("GearMigrateTask")
gmt.addInterface(pool.get("java.lang.Runnable"))
F(gmt, "public @PR@ admin;")
F(gmt, "public @PR@ target;")
F(gmt, "public boolean onWorld;")
C(gmt, "public GearMigrateTask(@PR@ admin, @PR@ target) { this.admin = admin; this.target = target; this.onWorld = false; }")
M(gmt, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.GearAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.GearAdmin.msg(this.admin, "that player's world is not loaded"); return; }
      this.onWorld = true;
      w.execute(this);
      return;
    }
    if (@PKG@.Gear.busy(this.target.getUuid())) { @PKG@.GearAdmin.msg(this.admin, this.target.getUsername() + "'s profile is loading (profile:busy) - try again in a moment"); return; }
    int[] c = @PKG@.GearStamp.scan(this.target, @PKG@.GearStamp.invOf(this.target));
    @PKG@.GearAdmin.msg(this.admin, "scan of " + this.target.getUsername() + ": stamped Normal " + c[0] + ", migrated from SkyyRolls " + c[1] + ", re-rendered " + c[2]);
    @PKG@.GearLog.line("ADMIN " + this.admin.getUsername() + " migrate " + this.target.getUsername() + " " + c[0] + "/" + c[1] + "/" + c[2]);
  } catch (Throwable t) { @PKG@.GearAdmin.msg(this.admin, "scan failed: " + t); }
}""")
M(gad, r"""
public static void migrateCmd(@PR@ pr, @INV@ inv, String rest) {
  if (rest.length() == 0) {
    if (@PKG@.Gear.busy(pr.getUuid())) { msg(pr, "your profile is loading (profile:busy) - try again in a moment"); return; }
    int[] c = @PKG@.GearStamp.scan(pr, inv);
    msg(pr, "scan: stamped Normal " + c[0] + ", migrated from SkyyRolls " + c[1] + ", re-rendered " + c[2]);
    @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " migrate self " + c[0] + "/" + c[1] + "/" + c[2]);
    return;
  }
  @PR@ target = null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(rest.trim())) { target = (@PR@) o; break; }
    }
  } catch (Throwable t) { target = null; }
  if (target == null) { msg(pr, "no online player called " + rest); return; }
  new @PKG@.GearMigrateTask(pr, target).run();
}""")
# ---- 0.2 /gear relevel (spec 2 "A band is changed in Server Setup": stamped items keep their level; this re-stamps the items a player
# holds). Every STAMPED gear item in the inventory (the 6 sections: hotbar, storage, backpack, armor, utility, tools) moves into TODAY's
# band of its id - below it = the band start, above it = the cap; unstamped items already follow the table live; a level set with /gear
# level stays (lvlA: bands ignored, spec 2). Vault, AH and bag contents are never touched (not in the inventory). World thread.
# Returns { checked, re-stamped, kept (set by /gear level), unstamped }; what = "Copper Sword 10 -> 12, ..."
M(gad, r"""
public static int[] relevelInv(@INV@ inv, java.util.UUID owner, StringBuilder what) {
  int[] cnt = new int[4];
  if (inv == null) return cnt;
  long now = System.currentTimeMillis();
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      String id = s.getItemId();
      @BD@ md = s.getMetadata();
      if (!@PKG@.GearData.gearish(id, md) || @PKG@.GearData.state(md) != 1) continue;
      @BD@ d = @PKG@.GearData.gearDoc(md);
      if (d == null) continue;
      cnt[0]++;
      if (!@PKG@.GearLevel.stamped(d)) { cnt[3]++; continue; }
      if (@PKG@.GearData.bool(d, "lvlA", false)) { cnt[2]++; continue; }
      int old = @PKG@.GearLevel.level(id, d);
      int[] b = @PKG@.GearLevel.band(id);
      int nw = old < b[0] ? b[0] : (old > b[1] ? b[1] : old);
      if (nw == old) continue;
      @BD@ nd = d.clone();
      nd.put("lvl", new org.bson.BsonInt32(nw));
      nd.put("at", new org.bson.BsonInt64(now));
      @IS@ ns = @PKG@.GearData.put(s, nd, owner);
      if (ns == s) continue;
      Object tx = c.setItemStackForSlot((short) i, ns);
      if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) continue;
      cnt[1]++;
      if (what != null && what.length() < 600) {
        if (what.length() > 0) what.append(", ");
        what.append(@PKG@.Gear.itemName(id)).append(' ').append(old).append(" -> ").append(nw);
      }
    }
  }
  return cnt;
}""")
M(gad, r"""
public static String relevelText(String who, int[] c, StringBuilder what) {
  return "relevel of " + who + ": " + c[0] + " gear item(s) checked, " + c[1] + " re-stamped into today's bands" + (what.length() > 0 ? " (" + what.toString() + ")" : "") + ", " + c[2] + " kept (set with /gear level), " + c[3] + " not stamped (they follow the table already)";
}""")
# /gear relevel <player>: hop to that player's world thread, re-stamp there, report back (the GearMigrateTask shape)
grlt = mk("GearRelevelTask")
grlt.addInterface(pool.get("java.lang.Runnable"))
F(grlt, "public @PR@ admin;")
F(grlt, "public @PR@ target;")
F(grlt, "public boolean onWorld;")
C(grlt, "public GearRelevelTask(@PR@ admin, @PR@ target) { this.admin = admin; this.target = target; this.onWorld = false; }")
M(grlt, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.GearAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.GearAdmin.msg(this.admin, "that player's world is not loaded"); return; }
      this.onWorld = true;
      w.execute(this);
      return;
    }
    if (@PKG@.Gear.busy(this.target.getUuid())) { @PKG@.GearAdmin.msg(this.admin, this.target.getUsername() + "'s profile is loading (profile:busy) - try again in a moment"); return; }
    StringBuilder what = new StringBuilder();
    int[] c = @PKG@.GearAdmin.relevelInv(@PKG@.GearStamp.invOf(this.target), this.target.getUuid(), what);
    @PKG@.GearAdmin.msg(this.admin, @PKG@.GearAdmin.relevelText(this.target.getUsername(), c, what));
    @PKG@.GearLog.line("ADMIN " + this.admin.getUsername() + " relevel " + this.target.getUsername() + " " + c[0] + "/" + c[1] + "/" + c[2] + "/" + c[3] + (what.length() > 0 ? " " + what.toString() : ""));
  } catch (Throwable t) { @PKG@.GearAdmin.msg(this.admin, "relevel failed: " + t); }
}""")
M(gad, r"""
public static void relevelCmd(@PR@ pr, @INV@ inv, String rest) {
  if (rest.length() == 0) {
    if (@PKG@.Gear.busy(pr.getUuid())) { msg(pr, "your profile is loading (profile:busy) - try again in a moment"); return; }
    StringBuilder what = new StringBuilder();
    int[] c = relevelInv(inv, pr.getUuid(), what);
    msg(pr, relevelText(pr.getUsername(), c, what));
    @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " relevel self " + c[0] + "/" + c[1] + "/" + c[2] + "/" + c[3] + (what.length() > 0 ? " " + what.toString() : ""));
    return;
  }
  @PR@ target = null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(rest.trim())) { target = (@PR@) o; break; }
    }
  } catch (Throwable t) { target = null; }
  if (target == null) { msg(pr, "no online player called " + rest); return; }
  new @PKG@.GearRelevelTask(pr, target).run();
}""")
M(gad, r"""
public static void read(@PR@ pr, @IS@ h) {
  String id = h.getItemId();
  @BD@ md = h.getMetadata();
  int st = @PKG@.GearData.state(md);
  String[] sn = new String[] { "no document", "SkyyGear v1 document", "SkyyRolls document only (not migrated yet)", "unreadable SkyyGear data", "newer SkyyGear schema" };
  msg(pr, id + ": " + sn[st] + (@PKG@.GearData.gearish(id, md) ? "" : " - not gear"));
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d != null) {
    int lv = @PKG@.GearLevel.level(id, d);
    Object[] g = @PKG@.GearGate.check(pr.getUuid(), id, d, lv);
    msg(pr, (st == 1 ? "doc: " : "view (in memory): ") + d.toJson());
    msg(pr, "level " + lv + ", gate " + @PKG@.GearData.gate(d) + " -> " + g[1] + " (you: " + g[3] + ", ok " + g[0] + ", enforced " + g[4] + ")");
    // 0.2: where the level comes from + the item's band (and what a craft by you would stamp)
    int[] b = @PKG@.GearLevel.band(id);
    String[] kn = new String[] { "Level by item (exact)", "Level by material", "Hytale's item level (exact)", "Level when nothing matches (exact)" };
    String src = @PKG@.GearLevel.stamped(d) ? (@PKG@.GearData.bool(d, "lvlA", false) ? "stored, set with /gear level" : "stored on the item") : "not stored: read from the table now";
    msg(pr, "level " + lv + " (" + src + ") - band " + (b[0] == b[1] ? String.valueOf(b[0]) : b[0] + "-" + b[1]) + " from " + kn[b[2] < 0 || b[2] > 3 ? 3 : b[2]] + (b[2] == 1 ? " row " + @PKG@.GearLevel.entry(id) : "") + "; a craft by you now: Lv " + @PKG@.GearRoll.craftLevel(id, pr.getUuid()));
    // 0.2.1: how the level sets this item's base stats (K / F / material bonus = the per-hit multiplier, or the armor targets)
    msg(pr, @PKG@.GearBase.describe(id, d));
  }
  msg(pr, "raw: " + (md == null ? "null" : md.toJson()));
}""")
M(gad, r"""
public static void run(@ST@ store, @REF@ ref, @PR@ pr, String action, String rest) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null) { msg(pr, "no player inventory"); return; }
    @INV@ inv = p.getInventory();
    java.util.UUID u = pr.getUuid();
    String who = pr.getUsername();
    // 0.1.2: /gear charged is read only (it never writes the inventory) and works with an empty hand
    if (action.equals("charged")) {
      String[] ls = @PKG@.GearCharged.probe(u, hand(inv), @PKG@.GearStats.totalsInv(u, inv, true), rest);
      for (int i = 0; i < ls.length; i++) msg(pr, ls[i]);
      return;
    }
    // spec 1.7: no inventory write while SkyyProfiles is swapping this player's profile (read only reads; migrate / relevel check their
    // target)
    if (!action.equals("read") && !action.equals("migrate") && !action.equals("relevel") && @PKG@.Gear.busy(u)) { msg(pr, "your profile is loading (profile:busy) - try again in a moment"); return; }
    if (action.equals("give")) { giveCmd(pr, inv, rest); return; }
    if (action.equals("migrate")) { migrateCmd(pr, inv, rest); return; }
    if (action.equals("relevel")) { relevelCmd(pr, inv, rest); return; }
    @IS@ h = hand(inv);
    if (h == null || h.isEmpty()) { msg(pr, "hold the item first"); return; }
    String id = h.getItemId();
    @BD@ md = h.getMetadata();
    if (action.equals("read")) { read(pr, h); return; }
    if (!@PKG@.GearData.gearish(id, md)) { msg(pr, @PKG@.Gear.itemName(id) + " is not gear"); return; }
    int st = @PKG@.GearData.state(md);
    if (action.equals("clear")) {
      if (md == null || (!md.containsKey(@PKG@.GearDefs.DOC_KEY) && !md.containsKey(@PKG@.GearDefs.VIEW_KEY))) { msg(pr, id + " has no SkyyGear data"); return; }
      Object tx = handC(inv).setItemStackForSlot(handS(inv), @PKG@.GearData.clear(h));
      @PKG@.GearLog.line("ADMIN " + who + " clear " + id);
      msg(pr, "cleared the SkyyGear data of " + id + " - it is stamped Normal again at the next inventory scan" + ok(tx));
      return;
    }
    if (st == 3 || st == 4) { msg(pr, "the gear data on this item is unreadable or from a newer SkyyGear - /gear read shows it; /gear clear removes it"); return; }
    @BD@ d = @PKG@.GearData.effective(id, md);
    if (d == null) { msg(pr, "no gear data"); return; }
    if (action.equals("reroll")) {
      Object[] res = @PKG@.GearForge.reforge(handC(inv), handS(inv), id, @PKG@.GearForge.fp(h), u, who, true, @PKG@.GearStamp.giveOf(inv), @PKG@.GearStamp.allOf(inv));
      msg(pr, (String) res[1] + (((Integer) res[0]).intValue() == 1 ? " " + @PKG@.GearView.modSummary((@BD@) res[4]) : ""));
      return;
    }
    @BD@ nd = d.clone();
    String note = "";
    if (action.equals("rarity")) {
      int r = @PKG@.GearDefs.rIndex(rest.trim());
      if (r < 0) { msg(pr, "usage: /gear rarity <normal|unique|rare|legendary|fabled|mythic|set>"); return; }
      nd.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[r]));
      note = " (modifiers kept - /gear reroll rolls them for the new rarity)";
    } else if (action.equals("unid")) {
      nd.put("id", new org.bson.BsonBoolean(false));
      nd.put("mods", new @BA@());
    } else if (action.equals("identify")) {
      if (@PKG@.GearData.identified(d)) { msg(pr, "it is already identified"); return; }
      nd = @PKG@.GearRoll.identify(id, d, u);
    } else if (action.equals("level")) {
      String a = rest.trim().toLowerCase();
      // 0.2: an admin level ignores the bands (spec 2) and is marked lvlA, so /gear relevel never moves it; clear = the item reads its
      // table level again (0.1.3 behaviour)
      if (a.equals("clear")) { nd.remove("lvl"); nd.remove("lvlA"); }
      else {
        int lv = -1;
        try { lv = Integer.parseInt(a); } catch (Throwable t) { lv = -1; }
        if (lv < 0 || lv > 100) { msg(pr, "usage: /gear level <0-100 | clear>"); return; }
        nd.put("lvl", new org.bson.BsonInt32(lv));
        nd.put("lvlA", new org.bson.BsonBoolean(true));
      }
    } else if (action.equals("gate")) {
      String g = rest.trim();
      if (g.length() == 0 || g.indexOf(' ') >= 0) { msg(pr, "usage: /gear gate <class | a SkyySkills skill name, e.g. Mining>"); return; }
      if (g.equalsIgnoreCase("class")) g = "class";
      else if (@PKG@.GearGate.readLevel(u, g) == -1) note = " (SkyySkills does not know that skill - it counts as level 0)";
      nd.put("gate", new org.bson.BsonString(g));
    } else { msg(pr, "unknown action " + action); return; }
    nd.put("at", new org.bson.BsonInt64(System.currentTimeMillis()));
    @IS@ ns = @PKG@.GearData.put(h, nd, u);
    Object tx = handC(inv).setItemStackForSlot(handS(inv), ns);
    @PKG@.GearLog.line("ADMIN " + who + " " + action + " " + id + " " + rest + " -> " + @PKG@.GearView.rollsLine(id, nd));
    msg(pr, action + " done: " + @PKG@.GearView.nameText(id, nd) + " - " + @PKG@.GearView.rollsLine(id, nd) + note + ok(tx));
  } catch (Throwable t) {
    @PKG@.Gear.warn("/gear " + action + " failed: " + t);
    msg(pr, "error: " + t);
  }
}""")
M(gad, r"""
public static String totalsText(int[] t) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; t != null && i < t.length && i < @PKG@.GearDefs.NS; i++) {
    if (t[i] == 0) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(@PKG@.GearDefs.S_LABEL[i]).append(' ').append(@PKG@.GearView.valText(@PKG@.GearDefs.S_KEY[i], t[i]));
    if (@PKG@.GearDefs.S_LIVE[i] == 0) sb.append(" (later)");
  }
  return sb.length() > 0 ? sb.toString() : "none";
}""")
# the player's own /gear: held item lines, active totals, Smithing rarity (spec 8.1, 5.3)
M(gad, r"""
public static void me(@ST@ store, @REF@ ref, @PR@ pr) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null) return;
    @INV@ inv = p.getInventory();
    java.util.UUID u = pr.getUuid();
    @PKG@.GearGate.refresh(u);
    @IS@ h = hand(inv);
    if (h != null && !h.isEmpty() && @PKG@.GearData.gearish(h.getItemId(), h.getMetadata())) {
      @BD@ d = @PKG@.GearData.effective(h.getItemId(), h.getMetadata());
      if (d == null) msg(pr, "the gear data on your held item is unreadable");
      else {
        String[] ls = @PKG@.GearView.plain(h.getItemId(), d, u);
        for (int i = 0; i < ls.length; i++) pr.sendMessage(@MSG@.raw((i == 0 ? "[Gear] " : "  ") + ls[i]));
      }
    } else msg(pr, "hold a weapon or armor piece to see its gear lines");
    int[] t = @PKG@.GearStats.totalsInv(u, inv, false);
    msg(pr, "Your active totals (held weapon + worn armor you meet the level for): " + totalsText(t));
    int[] x = @PKG@.GearStats.extra(u);
    if (x != null) msg(pr, "From other mods (gear:extra): " + totalsText(x));
    msg(pr, "Your Smithing rarity: +" + @PKG@.Gear.fnum(@PKG@.GearRoll.smithChance(u)) + " % chance of a better rarity when you craft gear");
  } catch (Throwable t) { @PKG@.Gear.warn("/gear failed: " + t); }
}""")

# ================================================================= /gear (player root) + admin sub-commands (spec 8.1)
# every sub-command: requirePermission("skyygear.admin") AND setPermissionGroups(new String[0]) (lint perm_group_leaks); the root lists
# hytale:Adventurer. Constructors are written out literally so tools/ci/lint.py reads each one.
# /gear give declares --rarity and --unid: AbstractCommand.acceptCall0 runs processOptionalArguments BEFORE execute, and that refuses
# every --name the command did not declare (server.commands.parsing.error.couldNotFindOptionalArgName; VERIFIED bytecode 2026-09-28)
F(subc["give"], "public @OA@ rarityArg;")
F(subc["give"], "public @OA@ unidArg;")
C(subc["give"], r"""
public GearGiveCmd() {
  super("give", "Give gear: /gear give <item> [--rarity <id>] [--unid true]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
  this.rarityArg = withOptionalArg("rarity", "normal, unique, rare, legendary, fabled, mythic or set", @ATY@.STRING);
  this.unidArg = withOptionalArg("unid", "true = the item comes unidentified", @ATY@.BOOLEAN);
}""")
C(subc["read"], r"""
public GearReadCmd() {
  super("read", "Show the gear document and raw metadata of the held item");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["reroll"], r"""
public GearRerollCmd() {
  super("reroll", "Free reforge of the held item");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["clear"], r"""
public GearClearCmd() {
  super("clear", "Remove SkyyGear data from the held item (it becomes Normal again)");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["rarity"], r"""
public GearRarityCmd() {
  super("rarity", "Set the held item's rarity: /gear rarity <id>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["unid"], r"""
public GearUnidCmd() {
  super("unid", "Make the held item unidentified (keeps its rarity)");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["identify"], r"""
public GearIdentifyCmd() {
  super("identify", "Identify the held item for free");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["level"], r"""
public GearLevelCmd() {
  super("level", "Set or clear the held item's level: /gear level <n|clear>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["gate"], r"""
public GearGateCmd() {
  super("gate", "Set the held item's gate skill: /gear gate <skill|class>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["migrate"], r"""
public GearMigrateCmd() {
  super("migrate", "Run the stamp / migration scan now: /gear migrate [player]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["charged"], r"""
public GearChargedCmd() {
  super("charged", "Charged attack probe: the held weapon's charged steps + your last hit's result");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["relevel"], r"""
public GearRelevelCmd() {
  super("relevel", "Re-stamp gear levels into today's bands: /gear relevel [player]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
# give: the parsed --rarity / --unid values are appended last, so they win over the raw-text parse in GearAdmin.giveCmd
M(subc["give"], r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String rest = @PKG@.GearAdmin.rest(ctx, "give");
  try {
    if (ctx.provided(this.rarityArg)) rest = rest + " --rarity " + String.valueOf(ctx.get(this.rarityArg)).trim();
    if (ctx.provided(this.unidArg)) rest = rest + " --unid " + String.valueOf(ctx.get(this.unidArg));
  } catch (Throwable t) { }
  @PKG@.GearAdmin.run(store, ref, pr, "give", rest.trim());
}""")
for _name, _cls, _desc, _args in SUBS:
    if _name == "give":
        continue
    M(subc[_name], r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.GearAdmin.run(store, ref, pr, "%s", %s);
}""" % (_name, ('@PKG@.GearAdmin.rest(ctx, "%s")' % _name) if _args else '""'))
C(gcm, r"""
public GearCmd() {
  super("gear", "Your gear: the held item's lines, your active totals and your Smithing rarity");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.GearGiveCmd());
  addSubCommand(new @PKG@.GearReadCmd());
  addSubCommand(new @PKG@.GearRerollCmd());
  addSubCommand(new @PKG@.GearClearCmd());
  addSubCommand(new @PKG@.GearRarityCmd());
  addSubCommand(new @PKG@.GearUnidCmd());
  addSubCommand(new @PKG@.GearIdentifyCmd());
  addSubCommand(new @PKG@.GearLevelCmd());
  addSubCommand(new @PKG@.GearGateCmd());
  addSubCommand(new @PKG@.GearMigrateCmd());
  addSubCommand(new @PKG@.GearChargedCmd());
  addSubCommand(new @PKG@.GearRelevelCmd());
}""")
M(gcm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.GearAdmin.me(store, ref, pr);
}""")

# ================================================================= plugin (spec Appendix A setup() order)
C(pl, "public SkyyGearPlugin(@JPI@ init) { super(init); }")
_reg = "\n".join('  try { getEntityStoreRegistry().registerSystem(new @PKG@.%s()); } catch (Throwable t%d) { @PKG@.Gear.warn("%s could not be registered: " + t%d); }'
                 % (n, i, n, i) for i, n in enumerate(("GearInvSys", "GearThrowSys", "GearCraftSys", "GearTick", "GearChestOpenSys",
                                                        "GearChestBreakSys", "GearCraftPreSys")))
_fns = "\n".join('  br.put("gear:fn:%s", new @PKG@.GearFn(%d));' % (n, i) for i, n in enumerate(
    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid")))
M(pl, r"""
public void setup() {
  @PKG@.Gear.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyGear");
  @PKG@.GearCfg.DIR = dir;
  @PKG@.GearCfg.FILE = dir.resolve("config.properties");
  @PKG@.GearLog.FILE = dir.resolve("gear.log");
  @PKG@.GearQual.load(dir.resolve("quality.properties"));
  @PKG@.GearCfg.importRolls(@PKG@.GearCfg.FILE, getDataDirectory().resolveSibling("Skyy_SkyyRolls").resolve("reforge.properties"));
  @PKG@.GearCfg.migrate011();
  @PKG@.GearCfg.migrateStat011();
  @PKG@.GearCfg.migrate012();
  @PKG@.GearCfg.migrate013();
  @PKG@.GearCfg.migrate02();
  @PKG@.GearCfg.migrate021();
  @PKG@.GearCfg.load();
  @PKG@.GearOpened.DIR = dir.resolve("chests");
  @PKG@.GearKnownTask.later(5L);
  if (@PKG@.Gear.bget("config:def:SkyyRolls") != null) @PKG@.Gear.warnOnce("rolls", "SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED); both mods register /reforge");
@REG@
  try { getChunkStoreRegistry().registerSystem(new @PKG@.GearChunkRegen()); } catch (Throwable tcr) { @PKG@.Gear.warn("GearChunkRegen could not be registered (a regenerated chunk keeps its container memory): " + tcr); }
  getEventRegistry().registerGlobal(@RWE@.class, new @PKG@.GearWorldBye());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.GearReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.GearBye());
  getCommandRegistry().registerCommand(new @PKG@.ReforgeCmd());
  getCommandRegistry().registerCommand(new @PKG@.GearCmd());
  // ---- PART B PLUGS IN HERE (2/4): PARTB_SETUP ----
@PARTBSETUP@
  @PKG@.GearCharged.setup(this);
  java.util.Map br = @PKG@.Gear.bridge();
@FNS@
  br.put("gear:gates", @PKG@.GearDefs.GATES);
  br.put("gear:tiers", @PKG@.GearDefs.TIERS);
  @PKG@.Gear.regSetting("gear.blockedPopup", "Gear level popups", "combat", true, "Popup when a weapon is too high level or unidentified");
  @PKG@.Gear.regSetting("gear.armorWarn", "Armor level warning", "combat", true, "Chat line when armor gives no stats because of its level");
  @PKG@.Gear.regSetting("gear.notices", "Gear update notices", "combat", true, "One-time line when your old rolled items move to the new gear system");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyGear] @VER@ ready - /reforge, /identify, /gear (admin: /gear give | read | reroll | clear | rarity | unid | identify | level | gate | migrate | charged | relevel, node skyygear.admin); rarity + level + modifiers on every weapon and armor piece; crafted gear rolls; mob + loot chest gear drops unidentified; gear stats live in combat; under-level gear blocked / inactive; SkyyRolls items migrate on first sight; level bands by material (combat gear vs the class weapon skill): " + @PKG@.GearCfg.matText() + "; " + @PKG@.GearCfg.levelText() + "; " + @PKG@.GearCfg.baseText() + "; " + @PKG@.GearCfg.statText() + "; " + @PKG@.GearChg.statusText() + "; " + @PKG@.GearChestOpen.statusText() + "; " + @PKG@.GearCfg.recipeText() + "; Server Setup -> Gear");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@REG@", _reg).replace("@FNS@", _fns).replace("@PDE@", PDE).replace("@VER@", VERSION)
   .replace("@PARTBSETUP@", "\n".join(PARTB_SETUP)))
M(pl, r"""
protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.GearLog.flush(); } catch (Throwable t2) { }
  try { @PKG@.GearOpened.flush(); } catch (Throwable t3) { }
  super.shutdown();
}""")

# ================================================================= write + build checks (spec 11.1 #2) + assemble
ALL = [gu, gdf, gcf, glg, gql, gdt, glv, grl, ggt, gvw, gbase, gst, gnt, gsp, gspt, gfg, gfn, ginv, gthr, gcrs, gcrt, gtk, grft, grdy, gbye, gui,
       rpg, rfc, gad, gmt, gcm] + [subc[s[0]] for s in SUBS] + [pl] + [c for c, _n in PARTB_CLASSES] + CHG_CLASSES + CHEST_CLASSES + [gcrp, grlt]
for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)
_src = open(os.path.abspath(__file__), encoding="utf-8").read()
assert ("new " + "ItemGridSlot") not in _src, "never put an ItemStack into an ItemGridSlot (spec 5.8)"
for _m in re.finditer(r'#(Skyy[A-Za-z0-9_]*)', _src):
    assert "_" not in _m.group(1), "UI id with an underscore: " + _m.group(1)
for _q in QUAL_IDS:
    _j = json.loads(EXTRA["Server/Item/Qualities/%s.json" % _q])
    assert _j["TextColor"] == RARITIES[QUAL_IDS.index(_q)][2].lower()
print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))
jar = os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)
man = B.manifest("SkyyGear", VERSION, "SkyWynn gear: Wynn rarity, level and modifiers on every weapon and armor piece; each item stores its own level = its use requirement (crafted at your skill level inside overlapping material bands) and its base stats (weapon damage, armor Health and resistance grow with the level); crafted gear rolls (Smithing raises the rarity); wand / staff recipes like the vanilla bows; /reforge re-rolls modifiers for coins; old SkyyRolls items keep their rolls; SkyBlock-style tooltips; Server Setup -> Gear. Replaces SkyyRolls. Zero dependencies.", PKG + ".SkyyGearPlugin")
assert man["IncludesAssetPack"] is True
B.assemble(jar, man, OUT, extra_files=EXTRA)
