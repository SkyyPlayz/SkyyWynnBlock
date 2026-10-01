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

## Numbers picked in the beta round (live now)
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
- Bag unlock collections: Mining = Iron (your call), Foraging = Oak Log, Farming = Wheat, Combat = Bone, Smithing = Light Hide; tiers I / III / V / VII. [proposed]
- Bag upgrade materials: Unique 6 Linen Scraps, Rare 6 Shadoweave Scraps, Legendary 6 Cindercloth Scraps (the old Loom bolts were impossible to get). [6 each]
- Coins can unlock bags up to Unique; Rare and Legendary must be gathered (bypass.bagMax). [unique]
- Should Magic Bags be blocked in /trade too (the auction house blocks them)? Otherwise a bag can skip its collection. [allowed]
- Staff bypass for the blocking switches is ON by default (ops + players with skyyparty.bypass / skyyessentials.bypass). [on]
- Overall Level: +0.5 max Health and +0.2 max Mana per level. [placeholders]
- Two crossbows keep only ONE banked big-arrow meter. [one]

## Round 9 + SkyyGear defaults (live 2026-09-29)
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
- PLAN 2026-10-01 (Skyy: "dont build yet, just make a plan"): SkyyWorldGen - Hytale zones as their own islands, biomes as progressively
  harder levels with level ranges -> research/SkyyWorldGen-Plan.md. Questions there (section 8): what unlocks the next island until bosses
  exist [reach the summit, later a class skill level, later the guardian]; solo hub [normal Hytale world stays the hub, islands via /zone
  + menu]; Zone 4 [built but hidden until our own Lv 50+ gear exists].
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
