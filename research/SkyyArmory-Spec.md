# SkyyArmory 0.1 "metal wands": build spec

> **Skyy's locks win over this draft:** OPEN-QUESTIONS.md, "Q&A with Skyy 2026-10-02", the two LOCKED SkyyArmory lines (Priest weapon
> path = custom metal wands + art; mod name SkyyArmory; tap = fast shot, hold = charged shot, Wood 5/1, Copper 10/2, Iron 15/3 = 3.5x,
> "the next 3 will be bigger jumps") and the art lock (OPEN-QUESTIONS.md:233, LOCKED 2026-10-02: "actually do B" -> EVERY metal wand
> uses style B, wood handle + metal head and bands, tier-coloured leaf crystals, gold bands on Mithril).

*Written 2026-10-02 (spec agent, Opus). Sources, all read-only: SkyySkills 0.4.12 (**S** = `SkyySkills/build_skyyskills_0.4.12.py` +
its jar), SkyyGear 0.2 jar and the 0.2.1 script that was being built then (**G** = `SkyyGear/build_skyygear_0.2.1.py`, built
2026-10-02 since; its line numbers may move, the function names will not), SkyyClasses 0.1.10 (**C**), SkyySacks 0.7.12 (**K**),
SkyyAccessories 0.5.2 (**A**), `tools/deploy_set.py`, Assets.zip and HytaleServer.jar (copied/decoded in `tools/dev/scratch/armoryspec/`,
deleted after; bytecode read with javassist's InstructionPrinter). Nothing is built. `tools/skyyart.py` was being written by another
agent then; section 1.3 now describes its real kit 1.0 (editor pass).*

*Edited 2026-10-03 (editor pass, Opus): the critic's 14 corrections were each re-verified (HytaleServer.jar bytecode, Assets.zip, the
build scripts; scratch `tools/dev/scratch/armoryedit/`, deleted after) and applied; section 14 "Review notes" lists every correction,
its proof and the editor's own findings. Biggest changes: art style B is locked; the quick orb's "smaller" and the reach claim were wrong
(the engine ignores ModelAsset scale and TimeToLive for these orbs) -> a small spawn hook makes the quick orb smaller and its size /
speed live rows; Mithril / Onyxium go back to 85 / 17 with +5 Priest Mana per Divinity level recommended; the Mana stopgap is not
harmless (Mages get it too); taps heal about 5x more per Mana from Iron up.*

**Legend.** LOCKED = Skyy decided it. VERIFIED = seen in bytecode (class#method), in Assets.zip (path) or in a build script (file:line).
PROPOSED = this spec's default, Skyy can change it. UNVERIFIED = needs the game client to prove.

**Corrections to the task brief (VERIFIED):**
- The Priest's base Mana is **30**, not 20 (`CLASS_BASE_DEF = [('Mage', 30), ('Priest', 30)]`, S:1659, since SkyySkills 0.4.8).
- `Weapon_Wand_Wood_Rotten` does **not** use its own projectile: its item names `Wand_Cast_Left_Launch: "Wand_Cast_Launch"` like the Wood
  wand. `Server/Projectiles/Player/Wand/Wand_Wood_Rotten_Corruption_Orb.json` is launched by no item or interaction; its only use is as
  the `Parent` of `Server/Projectiles/NPCs/Undead/Skeleton_Archmage/Skeleton_Archmage_Corruption_Orb.json` (VERIFIED Assets.zip).
- Every player caster launches the **same** orb: `Wand_Cast_Launch`, `Staff_Cast_Launch` and `Spellbook_Cast_Launch` all name
  `Skeleton_Mage_Corruption_Orb` (Damage 25, `Parent: Staff_Wood_Rotten_Corruption_Orb` = MuzzleVelocity 30, TerminalVelocity 50,
  Gravity 0, TimeToLive 3.1 - a field the engine never reads, 2.3). The Skeleton Mage mobs use it too, so **nobody may override it**;
  SkyyArmory makes new projectile ids.

---

## 0. Plain words (for Skyy)

- **SkyyArmory adds 7 metal wands:** Copper, Iron, Thorium, Cobalt, Adamantite, Mithril and Onyxium. Each one is the Wooden Earth Wand
  recoloured in its metal, in your style **B** (wood handle + metal head and bands, tier-coloured leaf crystals, gold bands on Mithril -
  LOCKED). Style A (all metal) still builds with one switch if you ever change your mind.
- **Tap = quick shot:** a blue orb, smaller (60% of the charged orb, set in Server Setup), 3 times as fast, 1/5 of the Mana and 1/5 of
  the damage. **Hold** (0.35 s, the same as today) = the charged shot, the normal green orb. Too little Mana = the "no Mana" click, like a
  charged cast today.
- **The Wooden Earth Wand gets the tap too:** 1 Mana, 1/5 damage. Its charged shot stays 5 Mana. Its free melee swing goes away
  (question 2).
- **Two things set a wand's damage.** (1) The wand's **level**, from SkyyGear, like every weapon: about x1 at Lv 1, x2 at Lv 10,
  x3.4 at Lv 40. (2) The **metal**: it sets the Mana per shot and a matching damage multiplier with your rule (cost x2 -> damage
  x2.25, cost x3 -> x3.5, so damage = 1.25 x cost multiple - 0.25). A better metal gives a little more damage per Mana: +12% for
  Copper up to +23.5% for Mithril / Onyxium.
- **The cost steps** ("the next 3 will be bigger jumps"): Wood 5 -> Copper 10 -> Iron 15 (+5, +5: your numbers), then Thorium 25 (+10),
  Cobalt 40 (+15), Adamantite 60 (+20), Mithril / Onyxium 85 (+25, the proposal already in OPEN-QUESTIONS; the other choice is 75 = +15,
  question 1).
- **The final table** (PROPOSED; Wood, Copper and Iron are your numbers):

| Wand | Levels | Hold (charged) | Tap (quick) | Damage x | Damage before levels (charged / quick) | Damage per Mana (before levels) | At its first level* (charged / quick) |
|---|---|---|---|---|---|---|---|
| Wooden Earth Wand | 1-13 | 5 Mana | 1 Mana | 1 | 25 / 5 | 5.0 | Lv 1: 25 / 5 |
| Copper Wand | 10-18 | 10 | 2 | 2.25 | 56 / 11 | 5.6 | Lv 10: 115 / 23 |
| Iron Wand | 15-23 | 15 | 3 | 3.5 | 88 / 18 | 5.9 | Lv 15: 199 / 41 |
| Thorium Wand | 20-28 | 25 | 5 | 6 | 150 / 30 | 6.0 | Lv 20: 371 / 74 |
| Cobalt Wand | 25-38 | 40 | 8 | 9.75 | 244 / 49 | 6.1 | Lv 25: 656 / 132 |
| Adamantite Wand | 35-43 | 60 | 12 | 14.75 | 369 / 74 | 6.15 | Lv 35: 1155 / 232 |
| Mithril Wand | 40-49 | **85** | **17** | 21 | 525 / 105 | 6.18 | Lv 40: 1764 / 353 |
| Onyxium Wand | 40-49 | **85** | **17** | 21 | 525 / 105 | 6.18 | Lv 40: 1764 / 353 |

  \* with SkyyGear 0.2.1's level damage (built, not in the live set yet), before Magical Power, crits and mob armor. Mithril / Onyxium at
  the other choice 75 / 15: x18.5, 463 / 93, Lv 40: 1556 / 312.
- **Heads-up 1 - Mana (your call, question 1).** Today a Priest has about **30 Mana at every Divinity level** (base 30 + 0.2 per Overall
  Level; Alchemy and a Mana accessory add a little). That pays for Copper (10), but Iron is already half of it, Thorium is one cast from a
  full pool, and Cobalt, Adamantite and Mithril cannot be cast at all. **Fix: Priests gain +5 max Mana per Divinity level** (35 at Lv 1,
  80 at 10, 130 at 20, 231 at 40): every charged shot then costs at most 37% of the Mana a Priest has when that wand first becomes
  usable, with Mithril / Onyxium at 85. (The other choice: +4 per level and Mithril / Onyxium 75 - at most 39%.) The clean way is a small
  SkyySkills update: a "Max Mana per class level" row, Priest only. **Careful with the shortcut:** SkyWynn Menu > Server Setup > Skills >
  Perks (turn Advanced on) > "Combat: max mana per level" works today with no build, but it gives EVERY class that much per class-skill
  level. Mages spend Mana too (staff 10, spellbook 20), so a Sorcery 40 Mage would hold about 231 Mana (23 staff casts instead of 3).
  Use the shortcut only if you are OK with that until the Priest-only row ships.
- **Heads-up 2.** Mana refills at a flat 5 a second (2.5 in combat). A Mithril charged shot (85) takes 17 s to refill (34 s in
  combat). Big metals = big hits, then the quick shot fills the gaps. Mana Regen boosts help. Vanilla also pauses the refill while you
  hold or tap a wand (every tap is a short charge); SkyySkills 0.4.13 (built, in its fix round) keeps Mana refilling - it should go live
  with or before SkyyArmory.
- **Heads-up 3 (question 4).** Mage staffs keep 10 Mana and the same 25-damage orb at every metal, so a Mithril wand hits about 21x
  harder per cast (2.5x per Mana) than a Mithril staff.
- **Heads-up 4 - healing (question 5).** A quick hit heals like any Priest hit (25% of its damage), but the heal is capped at 10 per hit.
  From the Iron wand up a quick hit already reaches that cap, so a tap heals as much as a charged shot for 1/5 of the Mana - about 5x
  more healing per Mana. Recommended: quick hits count 1/5 toward the cap (a small SkyyClasses update).
- **Crafting:** each wand uses that metal's **shortbow recipe**, like the staffs (Weapon Bench > Bow tab). It is made at your Divinity
  level inside the metal's level range (SkyyGear). Vanilla has no Onyxium weapon recipe at all, so the Onyxium wand has none for now,
  like the Onyxium staff (question 3).
- **What you can change in game** (Server Setup > Armory, live): a damage % per wand (100% = the table), the quick shot's size, speed and
  damage share, and the Mana check warnings. The Mana costs and the art are fixed in the jar: the game client gets the Mana costs with
  the wand's files and predicts them, so they cannot change while the server runs. They are shown read-only.

---

## 1. Items

### 1.1 The seven items (PROPOSED ids; LOCKED metals)

| Item id | Name (en-US) | Quality | ItemLevel | SkyyGear band (by the material word) |
|---|---|---|---|---|
| `Weapon_Wand_Copper` | Copper Wand | Common | 10 | Copper 10-18 |
| `Weapon_Wand_Iron` | Iron Wand | Uncommon | 20 | Iron 15-23 |
| `Weapon_Wand_Thorium` | Thorium Wand | Rare | 30 | Thorium 20-28 |
| `Weapon_Wand_Cobalt` | Cobalt Wand | Rare | 35 | Cobalt 25-38 |
| `Weapon_Wand_Adamantite` | Adamantite Wand | Rare | 40 | Adamantite 35-43 |
| `Weapon_Wand_Mithril` | Mithril Wand | Epic | 50 | Mithril 40-49 |
| `Weapon_Wand_Onyxium` | Onyxium Wand | Epic | 50 | Onyxium 40-49 |

- **Quality and ItemLevel** = that metal's vanilla **Sword** (VERIFIED Assets.zip: Weapon_Sword_Copper Common/10, _Iron Uncommon/20,
  _Thorium Rare/30, _Cobalt Rare/35, _Adamantite Rare/40, _Mithril Epic/50, _Onyxium Epic/50). SkyyGear replaces the frame per stack
  with its rarity (`Skyy_Gear_*` qualities) and ignores ItemLevel for these ids because the material band wins (G `GearLevel.level`:
  the id words from the left, longest entry first; BANDS assert G:1053-1058). Names follow vanilla ("Copper Staff", Assets
  `Server/Languages/en-US/server.lang`).
- **The id rule is load-bearing (VERIFIED):**
  - `Weapon_` + `Wand` + metal word: SkyyGear's band lookup reads the metal word (BANDS, G:1053), its spell list is the prefix
    `Weapon_Wand_` (`SPELL_PREFIXES`, G:831 -> `GearData.isSpell`, G:5109), SkyyClasses' Priest weapons are the prefix `Weapon_Wand_`
    (C:254).
  - **Never put "skyy" anywhere in an item id:** `GearData.skyyItem` (G:5026) treats any id whose lowercase starts with "skyy" or holds
    "_skyy" as a Skyy item, and such an item is never gear (no level, no rarity, no gate).
  - No family row of SkyyGear catches "Wand" or "Weapon" first (FAMILIES, G:949: only Root / Stoneskin / Bamboo / Cane / Onion for plain
    wands and staffs), so `Weapon_Wand_Copper` resolves to Copper.
  - Build check: none of the 7 ids exists in Assets.zip today. If a Hytale update adds one (vanilla might make metal wands), our pack
    would override it - the build stops with that message so Skyy can decide.
- **MaxStack: not set** -> 1. VERIFIED `Item#processConfig`: an unset MaxStack (-1) becomes 1 when the item has a Tool / Weapon / Armor /
  BuilderTool / BlockSelector section, else 100. The wands carry `"Weapon": {}` like the vanilla wand. With MaxStack 1, SkyyGear's ammo
  test (`GearData.ammoMs`) looks only at the family word "Wand", which is no ammo word, so `GearData.isGearMs` makes them gear.
- **Durability: unchanged** = like the Wooden Earth Wand (no MaxDurability field; the kit wand never breaks). SkyyEssentials' durability
  switch covers them like every weapon.
- **Categories** `["Items.Weapons"]`, **Tags** `{"Type": ["Weapon"], "Family": ["Wand"]}`, `PlayerAnimationsId: "Wand"`,
  `Utility: {"Compatible": true}`, `IconProperties`, `DroppedItemAnimation`, `ItemSoundSetId: "ISS_Weapons_Wand"` and the item particle
  `{"SystemId": "Wood_Wand", "TargetNodeName": "Handle"}` are copied from `Weapon_Wand_Wood` at build time (every vanilla wand uses the
  Wood_Wand particle, also the non-wood Stoneskin wand). No `InteractionVars` (our chains use no Replace steps, section 2).
- **Interactions:** `"Primary"` and `"Secondary"` = `SkyyArmory_Wand_Primary_<Metal>` (vanilla maps both to `Wand_Primary`).
- **Description** (shown grey by SkyyGear's tooltip, G `GearView.descMsg` G:7177, and by the plain vanilla tooltip):
  `items.Weapon_Wand_Copper.description = Tap: quick shot, 2 Mana. Hold: charged shot, 10 Mana.` The item needs no Description field:
  VERIFIED `Item#getDescriptionTranslationKey` falls back to `"server.items.<id>.description"` (constant pool of Item.class). The
  same fallback gives the **vanilla** Wood / Rotten / Tribal wands a description from our lang file ("1 Mana / 5 Mana") **without
  overriding their item files** (SkyySkills owns those, section 8).
- **Recipe:** embedded in the item (`"Recipe"`, the vanilla way; the engine names it `<id>_Recipe_Generated_0`, which SkyySacks expects:
  `RECIPE_SUFFIX`, K:286). Section 5.

### 1.2 Model, texture, icon (art)

| Part | Value |
|---|---|
| Model | `Items/Weapons/Wand/Wood.blockymodel` (vanilla, reused; the Rotten wand does the same with another texture) |
| Texture | `Items/Weapons/Wand/SkyyArmory_<Metal>_Texture.png` - generated, 64 x 32 RGBA (vanilla `Wood_Texture.png` is 64 x 32) |
| Icon | `Icons/ItemsGenerated/SkyyArmory_Wand_<Metal>.png` - generated, 64 x 64 RGBA (vanilla `Weapon_Wand_Wood.png` is 64 x 64) |

The `SkyyArmory_` prefix on the PNG paths keeps them clear of any future vanilla file. Nothing vanilla is committed: the PNGs exist only
inside the jar (the SkyySkills generated-override pattern; PROJECT-RULES section 2). Proof that custom Common PNGs reach the client:
SkyyVault 0.1.5 ships `Common/Icons/ItemsGenerated/Skyy_Vault_*.png` (seen in game), SkyySacks 0.7.12 and SkyyHud 0.3.11 ship PNGs too.
A custom texture on a vanilla model has no precedent in our mods yet (UNVERIFIED, risk R1; vanilla precedent: the Rotten wand).

### 1.3 The art kit `tools/skyyart.py` (kit 1.0, VERIFIED by reading it) and the style switch

The kit exists (KIT_VERSION "1.0", pure Python: zlib + struct, no Pillow; deterministic bytes). SkyyArmory's build uses exactly these
calls (`import skyyart as SA`):

1. `SA.verify()` - proves the PNG codec, the icon renderer (against the vanilla Wood wand, Rotten wand and Iron staff icons) and every
   vanilla file / model node the wand recipe reads (Assets.zip, read-only). The build calls it first, like `skyyui.verify()`.
2. `z = SA.assets()` (Assets.zip opened read-only), then `tex, icon = SA.wand_art(z, metal, WAND_STYLE)` -> (texture PNG, icon PNG):
   the texture has the size and UV layout of `Items/Weapons/Wand/Wood_Texture.png` (64 x 32, alpha kept; `SA.wand_texture`), the icon is
   rendered 64 x 64 from that texture with the Wood wand's `IconProperties` (`SA.render_icon`). Metals = `SA.METALS` (our 7), styles =
   `SA.WAND_STYLES` ("A" full metal, "B" wood handle + metal head).
3. The quick orb's blue texture is built from existing kit parts (no new kit function): `SA.recolor(SkeletonMage.png,
   SA.palette_from([Iceball_Texture.png]))` - a gradient map of `Common/Items/Projectiles/Fireball_Textures/SkeletonMage.png` (32 x 32,
   mean colour of its 400 opaque pixels (191, 247, 124), green) onto the colours of the vanilla `Common/Items/Projectiles/Iceball_Texture.png`
   (mean (126, 217, 243), ice blue); alpha kept.
4. Not in the kit: a blockymodel scaler (only needed by the fallback size path `QUICK_SIZE_MODE = "model"`, 2.3). The SkyyArmory build does
   that JSON edit itself, or the builder adds it to the kit together with a kit test.

**One build switch:** `WAND_STYLE = "B"` at the top of `build_skyyarmory_0.1.py` - **set from Skyy's lock** (OPEN-QUESTIONS.md:233,
2026-10-02 "actually do B": every metal wand, Copper through Onyxium). `"A"` (all metal) must still build (test T11) so a later change of
mind is one letter.

---

## 2. Interactions

### 2.1 The vanilla wand chain (VERIFIED, Assets.zip + bytecode)

`Weapon_Wand_Wood` -> Primary / Secondary root `Wand_Primary` (`RootInteractions/Weapons/Wand/Wand_Primary.json`, `{"Interactions":
["Wand_Primary"]}`) -> interaction `Wand_Primary` (`Interactions/Weapons/Wand/Wand_Primary.json`):

```
Charging  (ItemAnimationId CastLeftCharging, AllowIndefiniteHold true, HorizontalSpeedMultiplier 0.75)
  Next "0"    -> Chaining (ChainingAllowance 1.25) [Sword_Swing_Left_Fast, Sword_Swing_Right_Fast]   = TODAY'S TAP: a melee swing
  Next "0.35" -> Wand_Cast_Left_Charged                                                              = THE HOLD
Wand_Cast_Left_Charged = StatsCondition Costs {Mana: 25 -> 5 by SkyySkills}, RunTime 0.167
  Next   Parallel [ Replace var Wand_Cast_Left_Cost   (default Wand_Cast_Cost   = ChangeStat Mana -25 -> -5 by SkyySkills),
                    Replace var Wand_Cast_Left_Launch (default Wand_Cast_Launch = LaunchProjectile Skeleton_Mage_Corruption_Orb,
                                                       RunTime 0.25, ItemAnimationId CastLeftCharged),
                    Replace var Wand_Cast_Left_Effect (default Wand_Cast_Effect = Simple, sound SFX_Staff_Ice_Shoot, RunTime 0.5) ]
  Failed Replace var Wand_Cast_Left_Fail (default Wand_Cast_Fail = Simple, ItemAnimationId Interact, sound SFX_Bow_No_Ammo, RunTime 0.2)
```

Engine facts behind it:
- **Tap vs hold is decided by the client's charge value.** `ChargingInteraction#tick0` reads `InteractionSyncData.chargeValue` from the
  client state (-1 = still held, -2 = cancelled), calls `validateChargeValue` (only **logs a WARNING** when the value is above wall time
  x dilation + 0.25 s) and `jumpToChargeValue`, which jumps to the **largest Next key <= the charge value** (`sortedKeys` loop). Keys
  {0, 0.35}: released before 0.35 s = key 0, at or after 0.35 s = key 0.35. `ChargingInteraction#configurePacket` sends the Next map to
  the client. The class lives in `config/client/`: the client runs it.
- **The Mana check is the StatsCondition the Charging step names, and it does not spend.** `StatsConditionInteraction#canAfford`: for
  every cost, the stat value (Absolute) below the cost -> false (unless `lenient` overdraw) -> `firstRun` sets the state Failed -> the
  `Failed` branch runs. Nothing is subtracted. `StatsConditionInteraction#configurePacket` copies the costs to the client.
- **The spend is the ChangeStat.** `ChangeStatInteraction#firstRun` -> `EntityStatMap.processStatChanges(Predictable.SELF, ...)` (the client
  predicts it). A ChangeStat never fails.
- **An item's InteractionVars are read only by a Replace naming the var** (S:1880-1890 notes, research/Mana-Cost-And-Regen-Research.md 1.2);
  a plain string in Next / Failed / Parallel names the global interaction asset. So a check named directly is the check that runs.
- **Today's tap cadence:** `Sword_Swing_Left_Fast` RunTime 0.18 + Parallel(max(Selector 0.05 + pad 0.107, Effect 0.166)) = **0.346 s**
  per swing (Assets `Interactions/Weapons/Sword/Attacks/Deprecated/Swing_Left_Fast/*`). The hold path: 0.35 s charge + 0.167 + 0.5 =
  about 1.0 s per charged cast.
- The wand animation set has an unused uncharged cast animation `CastLeft` (Assets `Server/Item/Animations/Wand.json`: CastLeft /
  CastLeftCharging / CastLeftCharged). VERIFIED lengths: `CastLeft` = `Common/Characters/Animations/Items/Main_Handed/Wand/Attacks/
  Cast_Left/Cast_Left.blockyanim`, duration 50 (R-Arm keys at 0 / 30 / 40 / 50 - a long wind-up before the thrust); `CastLeftCharged` =
  `.../Cast_Left_Charged/Cast_Left_Charged.blockyanim`, duration 20 (R-Arm keys 0 / 10 / 20), the one vanilla plays on its 0.25 s launch.
  Vanilla also has an unused wand sound `SFX_Wand_Ice_Shoot`
  (`Server/Audio/SoundEvents/SFX/Weapons/Wand/SFX_Wand_Ice_Shoot.json`, Parent SFX_Attn_Loud, MaxInstance 5).

### 2.2 The metal wand chain (PROPOSED asset ids; all new, all `SkyyArmory_`)

Per metal M (Copper ... Onyxium), costs C (charged) and Q = C / 5 (quick), from section 4:

```
Root        SkyyArmory_Wand_Primary_<M>          {"Interactions": ["SkyyArmory_Wand_Primary_<M>"]}      (item Primary + Secondary)
Interaction SkyyArmory_Wand_Primary_<M>          Charging, the vanilla Wand_Primary values (CastLeftCharging, AllowIndefiniteHold,
                                                 HorizontalSpeedMultiplier 0.75), Next {"0": "SkyyArmory_Wand_Quick_<M>",
                                                                                       "0.35": "SkyyArmory_Wand_Cast_<M>"}
--- HOLD (charged)
SkyyArmory_Wand_Cast_<M>          StatsCondition Costs {Mana: C}, RunTime 0.167,
                                  Next Parallel [{"Interactions": ["SkyyArmory_Wand_Cast_Cost_<M>"]},
                                                 {"Interactions": ["SkyyArmory_Wand_Cast_Launch_<M>"]},
                                                 {"Interactions": ["SkyyArmory_Wand_Cast_Effect"]}],
                                  Failed "SkyyArmory_Wand_Fail"
SkyyArmory_Wand_Cast_Cost_<M>     ChangeStat StatModifiers {Mana: -C}
SkyyArmory_Wand_Cast_Launch_<M>   LaunchProjectile ProjectileId "SkyyArmory_Orb_<M>", RunTime 0.25, ItemAnimationId CastLeftCharged
SkyyArmory_Wand_Cast_Effect       Simple, WorldSoundEventId SFX_Staff_Ice_Shoot, RunTime 0.5        (shared; = vanilla Wand_Cast_Effect)
--- TAP (quick)
SkyyArmory_Wand_Quick_<M>         StatsCondition Costs {Mana: Q}, RunTime 0.1,
                                  Next Parallel [SkyyArmory_Wand_Quick_Cost_<M>, SkyyArmory_Wand_Quick_Launch_<M>,
                                                 SkyyArmory_Wand_Quick_Effect]   (same shape as the hold),
                                  Failed "SkyyArmory_Wand_Fail"
SkyyArmory_Wand_Quick_Cost_<M>    ChangeStat StatModifiers {Mana: -Q}
SkyyArmory_Wand_Quick_Launch_<M>  LaunchProjectile ProjectileId "SkyyArmory_QuickOrb_<M>", RunTime 0.25, ItemAnimationId QUICK_ANIM
                                  (build constant, default "CastLeftCharged" = the 20-frame cast vanilla already plays on a 0.25 s
                                  launch; "CastLeft" = the unused 50-frame cast, whose thrust comes after the 0.35 s quick chain - try
                                  it in game only, test step 10)
SkyyArmory_Wand_Quick_Effect      Simple, WorldSoundEventId SFX_Wand_Ice_Shoot, RunTime 0.25        (shared)
--- shared
SkyyArmory_Wand_Fail              Simple, ItemAnimationId Interact, WorldSoundEventId SFX_Bow_No_Ammo, RunTime 0.2  (= vanilla Wand_Cast_Fail)
```

- **No SkyyArmory chain references any interaction that SkyySkills overrides** (its 8: `Wand_Cast_Left_Charged`, `Wand_Cast_Cost`,
  `Staff_Cast_Summon_Charged`, `Staff_Cast_Cost`, `Spellbook_Cast_Hurl_Charged`, `Spellbook_Cast_Cost`, `Gun_Shoot_Flintlock_Charged`,
  `Gun_Shoot_Cost`; S:1891-1892, SkyySkills 0.4.12 jar). Even the vanilla ids SkyySkills leaves alone (`Wand_Cast_Launch / _Effect /
  _Fail`) are copied under our own ids, so a later SkyySkills that overrides them cannot change a metal wand. The one exception is the
  Wood wand's hold (2.4), which keeps SkyySkills' check on purpose.
- **No Replace steps, no InteractionVars:** the check that runs is the check the Charging step names (2.1). One Charging root per metal
  gives 7 roots + 56 interaction files (7 x 7 per metal, 3 shared, 3 for the Wood tap, the `Wand_Primary` override) - trivial for a
  generator, and each file can be decoded and checked on its own (section 9).
- **Cadence:** quick chain = 0.1 + max(0.25, 0.25) = **0.35 s >= the vanilla tap 0.346 s** (the build computes the vanilla number from
  Assets.zip and asserts it; test T7). A click during a running chain waits for it (the chain is the rate limit, as for today's swing),
  so quick shots are never faster than today's taps (about 2.8 a second at most). No root cooldown (the vanilla wand root has none).
- **Charged chain** = the vanilla one: 0.167 + max(0, 0.25, 0.5) = 0.667 s after the 0.35 s hold.
- **Too little Mana:** the StatsCondition fails, nothing is spent, `SkyyArmory_Wand_Fail` plays the vanilla no-ammo click (0.2 s). Same
  for tap and hold (question 2 asks whether the Wood wand should swing instead).
- **The client predicts Mana** (ChangeStat Predictable.SELF) exactly as for today's wand; nothing server-only.

### 2.3 Projectiles (PROPOSED; generated **fully resolved, without "Parent"**)

**Why no Parent (VERIFIED in a scratch decode):** a Projectile with `Parent` decoded on its own reads only its own fields - vanilla
`Skeleton_Mage_Corruption_Orb` came back as Damage 25 but MuzzleVelocity 0 and TimeToLive 0 (the asset store applies the parent at
load). Fully resolved files decode and check standalone (section 9) and keep working if a pack changes the vanilla parent. The build
resolves `Skeleton_Mage_Corruption_Orb <- Staff_Wood_Rotten_Corruption_Orb` from Assets.zip, prints it and asserts the vanilla values.

| Id | Count | Appearance | Damage | MuzzleVelocity | TerminalVelocity | Gravity | Hit / death particles |
|---|---|---|---|---|---|---|---|
| `SkyyArmory_Orb_<M>` (charged) | 7 | `Skeleton_Mage_Corruption_Orb` (vanilla model asset, green; drawn at scale 1.0, see below) | round(25 x mult) | 30 | 50 | 0 | GreenOrbImpact (vanilla) |
| `SkyyArmory_QuickOrb_<M>` (quick, Wood included) | 8 | `SkyyArmory_QuickOrb` (new model asset, blue; made smaller by `quick.size`, below) | round(5 x mult) | **90** (3 x 30) | 150 | 0 | `SkyyArmory_Orb_Impact_Blue` |

Every other field (PitchAdjustShot, SticksVertically, DeathEffectsOnHit, DeadTimeMiss, ImpactSlowdown, DepthShot, VerticalCenterShot,
HorizontalCenterShot, hit / miss sounds `SFX_Skeleton_Mage_Spellbook_Impact`, and TimeToLive 3.1) = the resolved vanilla orb.

- **3x speed is real speed (VERIFIED):** `ProjectileComponent#shoot` sets the velocity to the aim direction normalised to
  `getMuzzleVelocity()`. `SimplePhysicsProvider#initialize` turns TerminalVelocity into a drag coefficient,
  `PhysicsMath#computeDragCoefficient = mass x gravity / (area x vt^2)`, which is **0 with Gravity 0** - so the orb keeps its muzzle
  speed. TerminalVelocity must stay > 0 (vt = 0 would be 0 / 0). Vanilla already flies a legacy projectile at 100
  (`Gun_Blunderbuss_Bullet`, MuzzleVelocity 100), so 90 is inside what the client draws. `SimplePhysicsProvider#tick` sweeps the
  whole move each tick (`EntityCollisionProvider.computeNearest` and `BlockCollisionProvider.cast` along the movement vector), so
  90 blocks/s does not tunnel through mobs or walls.
- **Speed and damage are server-only (VERIFIED):** `AssetRegistryLoader.<clinit>` builds the legacy `Projectile` store (path
  "Projectiles", `Projectile.CODEC`, a `DefaultAssetMap`; bytecode offsets 2526-2599) and the `ModelAsset` store ("Models", 2226-2311)
  **without** `setPacketGenerator` - only the new `ProjectileConfig` has one (`ProjectileConfigPacketGenerator`, offset 4066).
  `LaunchProjectileInteraction` is a server interaction (`config/server/`), and its `firstRun` calls `ProjectileComponent#shoot` (offset
  283, the velocity) before `CommandBuffer.addEntity` (offset 293). The client only sees the orb entity (its Model packet + its moves).
  So a spawn hook can change speed and size live (below); the Mana costs stay build-time (section 7).
- **Reach - no lifetime limit (VERIFIED):** `Projectile#getTimeToLive` has **no caller** in HytaleServer.jar (methods, constructors and
  static blocks scanned; only `equals`, `hashCode`, `toString` and the codec lambdas touch the field). A legacy projectile ends only by
  `ProjectileComponent#onProjectileHitEvent` (deadTimer = DeadTime), `#onProjectileMissEvent` (deadTimer = DeadTimeMiss) -> the ticking
  system's `consumeDeadTimer` -> `onProjectileDeath` + `removeEntity` (`LegacyProjectileSystems$TickingSystem#tick`), or the 60 s
  `DespawnComponent.despawnInMilliseconds(time, 60000)` that `ProjectileComponent#assembleDefaultProjectile` attaches (offsets 59-62).
  So **both** orbs fly until they hit something or 60 s pass - exactly like every vanilla wand / staff orb today (charged 30 blocks/s, up
  to 1,800 blocks; quick 90 blocks/s, up to 5,400). No reach cap in 0.1 (a cap is a possible later option: ArmorySpawnSys could swap the
  DespawnComponent for a shorter one - UNVERIFIED, R17).
- **Damage is an int and read at spawn (VERIFIED):** `Projectile.damage` is an `int`; `ProjectileComponent#initialize` fetches the
  Projectile asset by `projectileAssetName` once; `#onProjectileHitEvent` builds `new Damage(new Damage$ProjectileSource(shooter,
  projectile), DamageCause.PROJECTILE, getDamage() x brokenDamageModifier)` and calls `DamageSystems.executeDamage`.
- **The Wood wand's charged shot keeps the vanilla `Skeleton_Mage_Corruption_Orb`** (via SkyySkills' chain, 2.4). Only its tap uses
  `SkyyArmory_QuickOrb_Wood` (Damage 5).

**The blue quick-orb look** (`QUICK_LOOK` build constant):
- `"recolor"` (PROPOSED default - Skyy asked for the same shot, blue and smaller): model asset `SkyyArmory_QuickOrb` = a build-time copy
  of `Server/Models/Projectiles/NPCs/Undead/Skeleton_Mage/Skeleton_Mage_Corruption_Orb.json` (Model `Items/Projectiles/
  Projectile.blockymodel` + `Projectile_default.png`, which is 100% transparent - 0 of 1,024 pixels opaque - so the only visible body is
  the DefaultAttachment `Items/Projectiles/Fireball.blockymodel`), the same HitBox (+-0.1, so it is not harder to hit), MinScale /
  MaxScale left at the vanilla 0.7 (ignored, below), particle colours `#3f8cff`, and generated look assets: trail
  `SkyyArmory_Orb_Trail_Blue` (copy of `Entity/Trails/SkeletonMage.json`, start colour blue), particle systems
  `SkyyArmory_Orb_Glow_Blue` / `SkyyArmory_Orb_Impact_Blue` (+ their spawners) = copies of GreenOrbTrail / GreenOrbImpact /
  Spectre_Void_Head with the green colour values turned blue, and the attachment texture
  `Items/Projectiles/Fireball_Textures/SkyyArmory_QuickOrb_Blue.png` (section 1.3 item 3). Why copies and not just a `Color` tint:
  `ModelParticle` and `WorldParticle` do have Color + Scale fields (VERIFIED), but the GreenOrb spawners hard-code greens
  (`#5bff57`, `#d7ff28`, ...), and whether the client multiplies or replaces them is unknown; a recoloured copy is exact.
- `"ice"` (fallback, all vanilla, no recolouring): DefaultAttachment `Items/Projectiles/Iceball.blockymodel` + `Iceball_Texture.png`,
  particle `IceBall`, trail `Orb_Trail_White`, impact `Impact_Ice`. One constant if the recolour looks wrong in game (R2).

**The smaller quick orb - why the model asset's scale does nothing (VERIFIED):** a legacy projectile gets its model in
`LegacyProjectileSystems$OnAddHolderSystem#onEntityAdd` from `Model.createUnitScaleModel(modelAsset)` = `createScaledModel(asset, 1.0f,
null)`, and its BoundingBox from that unit model. `ModelAsset.getMinScale / getMaxScale` are called only by `ProjectileConfig#toPacket`
(the NEW projectile route), NPC spawning / validation, `SpawningContext` and the `/model` command; `generateRandomScale` only by
`ProjectileConfig#createSpawnModel`, NPC role setup, `/model` and `Model.createRandomScaleModel` (spawning, entity effects, the asset
editor, minecarts) - never by `LaunchProjectileInteraction` or the legacy projectile systems. `Model#toPacket` sends `scale` = the
Model's own 1.0. So the vanilla orb already draws at 1.0 (not 0.7), and a 0.4 copy would draw at 1.0 too: blue but not smaller.

**How SkyyArmory makes it smaller** (`QUICK_SIZE_MODE` build constant; size = the live row `quick.size`, default **60%** of the charged
orb, PROPOSED):
- `"scale"` (PROPOSED default; UNVERIFIED in game): **ArmorySpawnSys** (new, small Java) puts `new EntityScaleComponent(quick.size / 100)`
  on every spawned quick orb. VERIFIED engine path: `EntityTrackerSystems$EntityModel#tick` reads the entity's `EntityScaleComponent`
  (`getScale`, `consumeNetworkOutdated`) and `queueUpdatesFor` sends `new ModelUpdate(Model.toPacket(), entityScale)` to every viewer,
  also when the orb first becomes visible; the constructor marks the component network-outdated. Nothing on the hit side reads
  `EntityScaleComponent` (callers: trackers, block-entity migration, player self, snapshots, prefab editor, NPC spawn page, builder
  tools), so the hitbox stays +-0.1. Being a live row, Skyy can change the size without a build (new shots only).
- `"model"` (fallback; UNVERIFIED in game, no Java): the build writes a smaller copy of `Common/Items/Projectiles/Fireball.blockymodel`
  (`SkyyArmory_QuickOrb.blockymodel`: every shape's offset and stretch and every node position x the size; a JSON edit, the art kit has
  no scaler) as the quick model asset's DefaultAttachment, plus explicitly smaller `Scale` values on its model particles. Size fixed at
  build time (the row's default); the row shows read-only. Hitbox unchanged (the model asset's HitBox).
- Whether the client also shrinks the model's particles / trails with the entity scale is unknown: path `"scale"` keeps the vanilla
  particle sizes; test step 10 looks at it.

**ArmorySpawnSys** (PROPOSED Java, one system): a `HolderSystem` on `ProjectileComponent` - the `LegacyProjectileSystems$OnAddHolderSystem`
pattern (a HolderSystem whose `onEntityAdd(Holder, AddReason, Store)` runs on the holder before the entity exists) - acting only when
`AddReason.SPAWN`, `part.spawn` is on and the holder's `ProjectileComponent.getProjectileAssetName()` is one of our 8 quick ids:
1. size: put `EntityScaleComponent(quick.size / 100)` (mode `"scale"`, size < 100);
2. speed: when `quick.speed` != 3 (the built-in 3x), `getSimplePhysicsProvider().getVelocity()` x (quick.speed / 3). VERIFIED that this
   is safe in either order with the vanilla holder system: `shoot` set the velocity before `addEntity`, `getVelocity()` returns the live
   vector, and `ProjectileComponent#initializePhysics` -> `SimplePhysicsProvider#initialize` sets gravity / drag / bounce but never the
   velocity. At the default 3 it does nothing, so the asset's 90 holds even if the hook fails. UNVERIFIED in game.
Charged orbs, the vanilla orb and every other projectile are never touched.

### 2.4 The Wooden Earth Wand gets the tap (PROPOSED: yes)

Skyy's ladder starts at "stalk wand 5 / quick 1", so the Wood wand gets the quick shot.

- **Who touches the Wood wand today (VERIFIED):** SkyySkills 0.4.12 overrides the **item files** `Weapon_Wand_Wood`, `_Wood_Rotten`,
  `_Tribal` (costs / 5) and the interactions `Wand_Cast_Left_Charged` (check 5) + `Wand_Cast_Cost` (drain 5) - its jar holds exactly
  those 3 wand items and 8 interactions. SkyyGear 0.2 ships only a standalone **recipe** (`Server/Item/Recipes/SkyyGear/
  SkyyGear_Recipe_Weapon_Wand_Wood.json`) and qualities. SkyyClasses 0.1.10 only hands out `Weapon_Wand_Wood:1` (its jar has no assets).
- **The safe way: override the vanilla INTERACTION `Wand_Primary` only.** SkyyArmory ships
  `Server/Item/Interactions/Weapons/Wand/Wand_Primary.json` = the vanilla file read from Assets.zip at build time with **one** change:
  `Next["0"]` = `"SkyyArmory_Wand_Quick_Wood"` instead of the swing Chaining. `Next["0.35"]` stays `"Wand_Cast_Left_Charged"`, so the
  hold keeps SkyySkills' 5 / 5. The build asserts the vanilla shape first (Charging; keys exactly {"0", "0.35"}; "0" = Chaining
  [Sword_Swing_Left_Fast, Sword_Swing_Right_Fast]; "0.35" = Wand_Cast_Left_Charged) and that the generated file differs in that key only
  (the SkyySkills `_spell_diff` pattern, S:1939). `SkyyArmory_Wand_Quick_Wood` = the 2.2 quick chain with Q = 1, projectile
  `SkyyArmory_QuickOrb_Wood` (Damage 5).
- **No asset conflict (VERIFIED, scan of the 24 pinned SET jars + all 278 archives and 3 folders in `UserData\Mods`, read-only):** no jar
  or mod ships an asset named `Wand_Primary`, a `Weapon_Wand_<metal>` item or any `SkyyArmory*` file; the only other wand assets are
  SkyySkills' three item overrides. SkyySkills' item overrides keep `"Primary": "Wand_Primary"`, so our interaction override reaches
  them. SkyySkills' build clash check (`_spell_clash`, S:2507) refuses a live-set jar only for its 32 item ids, its 8 interaction ids
  and its generated files - `Wand_Primary` is none of them, so the next SkyySkills still builds with SkyyArmory pinned. Overriding a
  vanilla interaction from a mod pack is proven in game (SkyySkills 0.4.9: Skyy saw the wand cost 5). VERIFIED by SkyySkills' notes
  (S:12152-12153): every Interaction load rebuilds every root (`InteractionModule.handledLoadedInteractions -> RootInteraction.build`),
  so the compiled Charging step uses the winning asset.
- **Who else uses `Wand_Primary` (VERIFIED, Assets.zip grep):** exactly 3 items - `Weapon_Wand_Wood`, `Weapon_Wand_Wood_Rotten`,
  `Weapon_Wand_Tribal`. No NPC. All three get the 1-Mana tap (they share the 5-Mana hold already).
- **Build switch** `WOOD_QUICK = True` (False = ship no `Wand_Primary` file; the Wood wand stays vanilla).
- **Cost of the change:** the Wood wand loses its free melee swing (Physical 6) and with it the vanilla "Damage Data" box in its tooltip
  (R5). Question 2.
- **Description:** our lang file adds `items.Weapon_Wand_Wood.description`, `..._Wood_Rotten.description`, `..._Tribal.description`
  ("Tap: quick shot, 1 Mana. Hold: charged shot, 5 Mana.") through the default key (1.1). Vanilla has no description for them today
  (Assets lang grep).

### 2.5 How SkyySkills treats SkyyArmory's costs (no double / 5)

- SkyySkills' cost generator (SPELL GEN, S:1880-2490) reads **only vanilla entries of Assets.zip** at SkyySkills' own build time and
  writes overrides of vanilla ids. SkyyArmory's ids are not in Assets.zip, so they are never divided. **SkyyArmory's numbers are final
  in-game numbers** (Skyy's numbers), never divided again.
- SkyySkills' runtime only checks its own 40 overrides (pack check) and the class **kit** weapons (`ManaGuard`, S:12050: kit from
  SkyyClasses = `Weapon_Wand_Wood`, cost from its baked `ManaCost` table = 5). Nothing reads SkyyArmory's items.
- **Anchor check:** SkyyArmory's build reads the pinned SkyySkills jar's `Wand_Cast_Left_Charged` (Costs Mana) and `Wand_Cast_Cost`
  (Mana) and asserts 5 / -5 = the Wood rung of the ladder. If a future SkyySkills changes the divisor, the SkyyArmory build stops so the
  ladder is re-anchored on purpose.
- "Mana keeps regenerating while charging" (OPEN-QUESTIONS, LOCKED 2026-10-02) is **already built** in SkyySkills 0.4.13
  (`SkyySkills/SkyySkills-0.4.13.jar`, 2026-10-02; header "MANA WHILE CHARGING", `build_skyyskills_0.4.13.py:23`; still in its fix round
  before the first deploy, not in SET). It matters for the tap: vanilla stops Mana regen while a Charging step runs or right after one
  (`ChargingCondition#eval0`: any running Charging interaction, or `DamageDataComponent.getLastChargeTime()` within the delay;
  `Mana.json` condition `Charging` Inverse), and every tap is a short Charging step - without 0.4.13 a Priest who keeps tapping stops
  refilling. **Prerequisite:** pin SkyySkills 0.4.13 with or before SkyyArmory (section 11).

---

## 3. Damage

### 3.1 Where the metal multiplier lives

**In the projectile asset (PROPOSED).** `SkyyArmory_Orb_<M>.Damage = round(25 x mult)`, `SkyyArmory_QuickOrb_<M>.Damage = round(5 x
mult)` (round half up). 25 = the vanilla orb (`Skeleton_Mage_Corruption_Orb` Damage 25, asserted at build). The engine puts that
number into the hit (2.3). Why the asset and not a runtime multiplier:
- correct with no Java at all (the jar's code can be off, crash or be missing - the wands still hit for the table numbers);
- one place for both shots: the quick orb is its own asset with exactly 1/5;
- no second damage system competing with SkyyGear's.

**Plus a runtime tune (PROPOSED, Server Setup):** the `tune` table, one entry per wand, 100% by default (section 7). `ArmoryTuneSys`, a
`DamageEventSystem` in the **Filter**
group ordered **before** `DamageSystems$ArmorDamageReduction` (the slot SkyyGear's GearHitSys and SkyyMobs' LevelDamage already use),
multiplies a hit only when its source is a `Damage$ProjectileSource` whose projectile's `ProjectileComponent.getProjectileAssetName()`
is one of our 15 ids (no launch tracking needed: the projectile knows its own asset). 100% = untouched. For the 7 metal wands it
scales charged and quick alike, so 1/5 holds. **The Wood entry is quick-only:** the Wood wand's hold launches the shared vanilla
`Skeleton_Mage_Corruption_Orb` (also fired by Mage staffs, spellbooks and the Skeleton Mage mobs, and not one of our 15 ids), so only
`SkyyArmory_QuickOrb_Wood` follows the Wood row and any value other than 100% changes the Wood wand's quick / charged ratio; the row is
labelled that way (section 7). It also applies the live `quick.damage` row to the 8 quick ids: x (quick.damage / 20), so the default 20
(= 1/5) leaves them untouched. Multiplications commute, so its order against GearHitSys does not matter for mob targets; for a player
target SkyyGear's armor correction keeps another mod's factor (`GearArmor.correct`: "cur x act / full", G notes).

### 3.2 On top of SkyyGear 0.2.1's level damage (no double scaling)

VERIFIED in G (0.2.1, built 2026-10-02, not in SET yet):
- `GearShotTrack#onEntityAdded` (G:8853) records every spawned projectile (query Transform AND (ProjectileComponent OR
  StandardPhysicsProvider), AddReason.SPAWN, creator = a player) with the stack in hand (or the hand snapshot `GearHand.pick` when the
  live hand does not launch that projectile id), keyed by the projectile's UUID, plus `pid = getProjectileAssetName()`.
- On the hit, GearHitSys finds that record by the projectile (`GearShotTrack.find`, the `Damage$ProjectileSource`) -> the wand stack ->
  `GearHit.weaponHit` (G:9536): `spell = shot && GearData.isSpell(wand id)` -> `GearBase.weaponMult(main, spell)` (G:6648) = `kOf(id,
  spell) x F(level) x bonus(band start)`; **`kOf` returns 1.0 for a spell shot** (G:6630). Then the 0.2 chain: Damage % -> **Magical
  Power** (spells) -> Charged Attack Damage (spells x 0.15, only when charged) -> crit (`hitAmount`, G:8597).
- So a SkyyArmory hit = asset damage (metal) x tune x F(level) x SkyyGear's own material bonus x the stats. **The metal multiplier
  exists once (the asset); SkyyGear never derives K from the wand** (K = 1 for spells). SkyyGear's small material bonus (1 + 0.3% x band
  start: Copper +3% ... Mithril +12%) is SkyyGear's universal per-band bonus on every weapon, not a second metal multiplier - accepted.
- F(L) = straight lines through `1:1.0, 4:1.6, 10:2.0, 40:3.0, 100:5.0` (G `base.curve`). Band start x bonus: Copper 2.06, Iron 2.26,
  Thorium 2.47, Cobalt 2.69, Adamantite 3.13, Mithril / Onyxium 3.36 (the last column of the section-0 table).
- **Charged Attack Damage sees the right shot.** `GearShot.charged = GearChg.launchCode(itemId, pid) == 1` (G:5914): a projectile id
  counts as charged only when the item's walk launches it **only** from a Charging step's **largest** key (`GearChgWalk`: ChargingTag 0
  -> "normal", key > 0 -> charged, FULL when it is the largest key). The orb is launched only under 0.35 (FULL), the quick orb only
  under 0 (normal) - which is why the two shots must be **different projectile ids**. The walk runs on the live assets, so it sees our
  `Wand_Primary` override too; SkyyGear's admin `/gear charged` shows it in game.
- Other systems on the same hit (all proportional, so quick stays 1/5): SkyySkills' class weapon damage perk (+0.2% per class level),
  Magical Power, crits. SkyyMobs scales only mob attacks.
- **Not proportional (R8):** SkyyGear adds True Damage and the flat element lines **after** armor, per hit, never multiplied
  (`GearTrueSys`). Five quick shots get five times the flat bonus of one charged shot for the same Mana. Small at low item levels
  (modifier power grows to full at item level 40). Follow-up in section 8 (a "hit weight" for quick orbs).
- **Windowed, so not exploitable:** Mana Steal and Life Steal pay at most once per `steal.windowS` (3 s), whatever the hit count
  (`GearFx.manaSteal`, G:9292).

### 3.3 Quick shot = 1/5

`round(5 x mult)` vs `round(25 x mult)`: 5/25, 11/56, 18/88, 30/150, 49/244, 74/369, 105/525 (93/463 at the 75 option) - within one
point of 1/5 (rounded from the exact value, not from the rounded charged number). Every multiplier after the asset applies to both.
Healing is the exception (section 6: the per-hit heal cap).

### 3.4 Tooltip

VERIFIED: the vanilla tooltip's "Damage Data" box comes from `WeaponDamageDataCollector`, which reads only `DamageEntityInteraction`
and `ProjectileInteraction` (ProjectileConfig + ProjectileHit root) - **not** the legacy `LaunchProjectileInteraction` the wands use.
So wands show no Damage Data box (like vanilla spellbooks), and the Wood wand loses the box it shows today (that box is its melee
swing, "6-8"). SkyyGear's "Damage at Lv N" line reads the same breakdown (`GearBase.range`) and does not appear. **But SkyyGear 0.2.1
already has a spell line** (VERIFIED G `GearBase.spellRange` ~G:6783, used by the tooltip ~G:7205: "Spell at Lv N: lo-hi" = the lowest
and highest `Projectile.getDamage()` among the projectiles the item's GearChg walk launches x the level multiplier), so a metal wand
should show e.g. "Spell at Lv 10: 23-115" (quick - charged) with no bridge (UNVERIFIED in game; the `tune` % is not in it). The item
description carries the Mana costs (1.1).

---

## 4. Mana

### 4.1 A Priest's max Mana today (VERIFIED)

| Source | Amount | Proof |
|---|---|---|
| Base Mana by class | Priest **30** (the class base replaces the general 10) | S:1658-1659 `mana.base=10`, `mana.classBase.Priest=30` |
| Overall Level | +0.2 per Overall Level = floor(average of 9 skills: Mining, Foraging, Farming, Acrobatics, Alchemy, Smithing, Cooking, Exploration, the class skill) | S:1649, S:1667 |
| Alchemy perk | +0.2 per Alchemy level | S:1363 |
| Class skill perk | `perk.combat.manaPerLevel` **0** by default; live Server Setup row "Combat: max mana per level" (advanced, decimal 0-10), per **class skill** level of **every class** (Mage Sorcery too - `PerkCfg.MANA`, applied in `Perks.tick`) | S:11337, S:11352, S:3203 |
| Mana accessory | +6 / 12 / 18 / 24% of the flat max Mana (floor +1 / 2 / 3 / 4), best one only | A:434-435, A:3450 |
| Vanilla armor | Silk +60, Cindercloth +64, Onyxium +80, Prisma +100 (full sets) - **not counted**: Silk / Cindercloth recipes name the bench "TODO" (not craftable), Onyxium / Prisma have no recipe of their own (they inherit the Iron armor recipe through Parent - UNVERIFIED whether that crafts), none is in any drop list | Assets `Server/Item/Items/Armor/*` |
| Planned SkyyTrees 0.3 class tree | Priest Smiter lane / X1 node +Mana (about +48 by class skill 52) - **not counted** (not built) | research/Skill-Trees-2-Spec.md section 6-7 |
| Regen | +1 every 0.2 s = 5/s, only 6 s after the last damage taken and not while charging (vanilla `Mana.json`); SkyySkills 0.4.12 adds 50% of that in combat = 2.5/s | Assets `Server/Entity/Stats/Mana.json`, OPEN-QUESTIONS R2 |

### 4.2 The check at each band start (charged cost / max Mana)

"Fighter" = a Priest who levels Divinity only (Overall = Divinity / 9). "Typical" = Overall = Divinity / 2, Alchemy = Divinity / 4 and a
Unique Mana accessory (+12%) from Divinity 10.

| Wand (band start) | Charged | Today, fighter | Today, typical | **+5 per Divinity level** (recommended), fighter | +5, typical | +4 per Divinity level, fighter | +4, typical |
|---|---|---|---|---|---|---|---|
| Wood (Div 1) | 5 | 30 -> 17% | 30 -> 17% | 35 -> 14% | 35 -> 14% | 34 -> 15% | 34 -> 15% |
| Copper (Div 10) | 10 | 30 -> 33% | 35 -> 28% | 80 -> 12.5% | 91 -> 11% | 70 -> 14% | 80 -> 13% |
| Iron (Div 15) | 15 | 30 -> **50%** | 36 -> **42%** | 105 -> 14% | 120 -> 12.5% | 90 -> 17% | 103 -> 15% |
| Thorium (Div 20) | 25 | 30 -> **82%** (1 cast) | 37 -> **68%** (1 cast) | 130 -> 19% | 149 -> 17% | 110 -> 23% | 127 -> 20% |
| Cobalt (Div 25) | 40 | 30 -> **cannot cast** | 38 -> **cannot cast** | 155 -> 26% | 178 -> 22.5% | 130 -> 31% | 150 -> 27% |
| Adamantite (Div 35) | 60 | **cannot cast** | **cannot cast** | 206 -> 29% | 235 -> 25.5% | 171 -> 35% | 196 -> 31% |
| Mithril / Onyxium (Div 40), **85** (proposed) | 85 | **cannot cast** | **cannot cast** | 231 -> **36.8%** | 264 -> 32% | 191 -> **45%** | 220 -> 39% |
| Mithril / Onyxium (Div 40), 75 (the other choice) | 75 | **cannot cast** | **cannot cast** | 231 -> 32.5% | 264 -> 28% | 191 -> 39% | 220 -> 34% |

(Pools recomputed 2026-10-03: base 30 + N x Divinity + 0.2 x Overall (+ 0.2 x Alchemy and x1.12 for the typical case); the +5 fighter
pools 35 / 80 / 105 / 130 / 155 / 206 / 231 are the critic's numbers too.)

**Flags (above ~40%):** today Iron (Skyy's own number) is already 42-50% of the pool, Thorium is one cast from a full pool (68-82%), and
Cobalt, Adamantite and Mithril / Onyxium cannot be cast at all. With +4 Mana per Divinity level only Mithril / Onyxium at 85 stays above
40% (45% for the fighter at exactly Divinity 40; 85 needs +4.54 per level to reach 40%). With +5 every charged shot is at or under 37%.

**The cost steps** (Skyy: "the next 3 will be bigger jumps"): +5 (Wood -> Copper), +5 (-> Iron) = Skyy's numbers, then +10 (Thorium),
+15 (Cobalt), +20 (Adamantite), and Mithril / Onyxium **+25 at 85** (keeps the jumps growing; 85 / 17 is the proposal already recorded in
OPEN-QUESTIONS.md:206-210 - the main session's proposal, not a number Skyy gave) or only +15 at 75.

**Fix (PROPOSED, question 1) - two options for Skyy:**
1. **Recommended: Priests +5 max Mana per Divinity level, Mithril / Onyxium 85 / 17.** Every charged shot <= 37% of the pool at its band
   start (fighter), the jumps keep growing.
2. **Other choice: Priests +4 per Divinity level, Mithril / Onyxium 75 / 15** (the first draft): <= 39%, but the top step (+15) is smaller
   than Adamantite's (+20).
3. Thorium 25, Cobalt 40, Adamantite 60 stay in both (the "bigger jumps": +10, +15, +20 after Skyy's +5 steps).

**How the Priest gets that Mana (VERIFIED: there is no Priest-only per-level row today):**
- **Proper (PROPOSED, needs a build):** the next SkyySkills after 0.4.13 adds a per-class row "Max Mana per class level" (a table like
  "Base Mana by class": Priest 5 (or 4), others 0). This is a proposal of this spec - it is **not queued** anywhere yet (no line in
  OPEN-QUESTIONS / HANDOFF / RESUME).
- **Stopgap (live today, NOT harmless):** Server Setup > Skills > Perks (Advanced on) > "Combat: max mana per level" (decimal, 0-10)
  adds per class-skill level for **every** class (`Perks.tick`, `PerkCfg.MANA`). Mages spend Mana: staff 10, spellbook 20 (SkyySkills
  asserts the kit costs, S:2489-2490; its own row help says "Mage 30 = 3 staff casts", S:11388). At 5, a Sorcery 40 Mage holds about 231
  Mana = 23 staff casts instead of 3 (about 191 = 19 casts at 4) - an unasked Mage buff while the Mage ladder is still open (question 4).
  Use it only if Skyy accepts that until the Priest-only row ships.
- **Not recommended:** the live, Priest-only but flat `mana.classBase` Priest value - a flat pool big enough for Mithril (about 230) would
  give a Divinity 1 Priest 46 Wood casts.

With option 1: casts from a full pool at the band start (fighter) = Wood 7, Copper 8, Iron 7, Thorium 5, Cobalt 3, Adamantite 3,
Mithril 2. Refill time per charged shot (out of / in combat): Wood 1 / 2 s, Copper 2 / 4, Iron 3 / 6, Thorium 5 / 10, Cobalt 8 / 16,
Adamantite 12 / 24, Mithril 17 / 34 s (15 / 30 s at 75); quick shots 1/5 of that. Sustained damage is set by regen x damage per Mana,
so a higher metal mostly adds burst (R6).

### 4.3 Final defaults (all 8)

| Wand | Charged Mana | Quick Mana | mult = 1.25 x (C / 5) - 0.25 | Charged dmg | Quick dmg |
|---|---|---|---|---|---|
| Wood (vanilla item; hold by SkyySkills) | 5 | 1 | 1.00 | 25 (vanilla orb) | 5 |
| Copper | 10 | 2 | 2.25 | 56 | 11 |
| Iron | 15 | 3 | 3.50 | 88 | 18 |
| Thorium | 25 | 5 | 6.00 | 150 | 30 |
| Cobalt | 40 | 8 | 9.75 | 244 | 49 |
| Adamantite | 60 | 12 | 14.75 | 369 | 74 |
| Mithril | 85 | 17 | 21.00 | 525 | 105 |
| Onyxium | 85 | 17 | 21.00 | 525 | 105 |

(Question 1's other choice: Mithril / Onyxium 75 / 15, mult 18.50, 463 / 93.)

The rule reproduces both of Skyy's points exactly (Copper "slightly more than 2x" = 2.25, Iron 3.5) and gives damage per Mana = 5 x
(1.25 - 0.25 / multiple): +0% Wood, +12% Copper, +17% Iron, +20% Thorium, +22% Cobalt, +23% Adamantite, +23.5% Mithril / Onyxium. The
build holds the numbers in ONE Python table (`WANDS = [(metal, charged)]`; Skyy's answer to question 1 is one number there), derives
quick, mult and damage from it, and asserts Skyy's locked rungs (5/1, 10/2, 15/3, mult 2.25 and 3.5), `charged % 5 == 0` and that the
steps never shrink before Mithril (+5, +5, +10, +15, +20).

---

## 5. Recipes and levels

### 5.1 Which vanilla weapon each wand mirrors: **that metal's shortbow** (PROPOSED)

Skyy's R1 lock: magic weapon recipes "MATCH VANILLA WEAPONS - same bench and the same metals / amounts as that material's other vanilla
weapons". Why the shortbow:
1. SkyyGear 0.2 already made the **Wood wand = the Crude shortbow recipe** and every staff = its metal's shortbow (G header (6); the 0.2
   jar's recipe files) - one ladder for every caster.
2. Priests find every wand in **one tab** (Weapon Bench > Bow, next to the staffs and bows - the ranged weapons).
3. The shortbow exists for **every metal Copper -> Mithril** (VERIFIED: Axe, Club and Longsword have no Mithril recipe).
4. Its bench tiers match the bands (tier 2 Thorium / Cobalt, tier 3 Adamantite / Mithril).

(Alternative: the Sword - a one-hander, Sword tab, 4 / 6 / 8 / 10 / 11 / 6 bars. Not chosen because of 1 and 2.)

| Wand | = recipe of | Bench / tab / tier | Time | Inputs (VERIFIED Assets.zip) |
|---|---|---|---|---|
| Copper | Weapon_Shortbow_Copper | Weapon_Bench / Weapon_Bow / - | 3 s | Copper Bar x4, Wood Trunk (resource) x4, Fibre x6 |
| Iron | Weapon_Shortbow_Iron | Weapon_Bench / Weapon_Bow / - | 3.5 s | Iron Bar x6, Light Leather x2, Linen Scrap x3 |
| Thorium | Weapon_Shortbow_Thorium | Weapon_Bench / Weapon_Bow / 2 | 4 s | Thorium Bar x8, Medium Leather x2, Linen Scrap x3 |
| Cobalt | Weapon_Shortbow_Cobalt | Weapon_Bench / Weapon_Bow / 2 | 4 s | Cobalt Bar x10, Heavy Leather x2, Shadoweave Scrap x3 |
| Adamantite | Weapon_Shortbow_Adamantite | Weapon_Bench / Weapon_Bow / 3 | 4.5 s | Adamantite Bar x11, Heavy Leather x3, Cindercloth Scrap x3 |
| Mithril | Weapon_Shortbow_Mithril | Weapon_Bench / Weapon_Bow / 3 | 5 s | Mithril Bar x6, Storm Leather x2, Voidheart x1 |
| Onyxium | **none** (question 3; SkyyGear 0.2 gave the Onyxium staff none either) | - | - | VERIFIED (re-checked 2026-10-03: only `Ingredient_Bar_Onyxium`'s own Furnace recipe from `Ore_Onyxium`, the ore, `BlockTypeList/Ores.json` and a block migration name Onyxium bar / ore): vanilla has **no recipe that uses Onyxium bars**; no Onyxium weapon has a recipe (the Onyxium mace's "recipe" is a bench-less placeholder of wood, rock and fibre); no drop list holds Onyxium. Possible fallback (Skyy's call): the Mithril shortbow recipe with the bars swapped to `Ingredient_Bar_Onyxium` (smeltable, so craftable) |

- Copied at build time from the shortbow's `Recipe` exactly like SkyyGear did for the staffs: the developer-only **Armory** bench entry
  (`Bench_Armory`, DiagramCrafting) is dropped (SkyyGear 0.2 review finding 5), output = the wand x1, `KnowledgeRequired: false`.
  The values above are what the build reads today; the build reads them again every time, so a Hytale update flows through.
- Embedded as the item's `Recipe` (1.1). The vanilla `Weapon_Wand_Wood` recipe stays SkyyGear's (`SkyyGear_Recipe_Weapon_Wand_Wood`).

### 5.2 Levels

- **No SkyyArmory code.** SkyyGear stamps the level when the wand is crafted: the crafter's **class skill** (Divinity for a Priest),
  raised to the gate floor and moved into the band; below the band = the band start + the chat note, above = the cap (G header 0.2 (4):
  vanilla bench `GearCraftSys` on CraftRecipeEvent; SkyySacks /craft through `gear:fn:roll` mode 8). Bands from the metal word (1.1).
- The use requirement = the same level vs Divinity (SkyyGear gate; an under-level wand's hits deal 0 and show SkyyGear's notice). The
  Mana is still spent on a blocked cast - the same as every caster today.
- Rarity, reforge, identify, `/gear read`, Auction House signatures: SkyyGear, automatic (the ids are gear: Weapon_ prefix, MaxStack 1,
  no "skyy" in the id).

---

## 6. Classes and heals

- **Priest only, automatic:** SkyyClasses' Priest weapons are the prefixes `Weapon_Wand_`, `Weapon_Spellbook_` and the Healing Totem
  (C:254). Another class's hits with a metal wand are blocked (DamageLock + the popup). Projectiles are judged by the item at launch:
  SkyyClasses `ShotTrack` (C:637, query Transform AND (ProjectileComponent OR StandardPhysicsProvider), AddReason.SPAWN, creator UUID).
- **Do quick shots heal? Yes - but NOT at 1/5 once the cap is reached.** `PriestHealSys` (C:662, Inspect group = after armor, only damage
  that landed) takes the post-scaling `d.getAmount()` of a Priest-weapon hit on a monster (projectiles through `ShotTrack.find`) and heals
  party members within `priestHeal.radius` (16) by `sharePercent` (25%) of it, the Priest itself by `selfPercent` (100%) of that; caps
  `maxPerHit` 10 and `maxPerSecond` 10 per player, shared by all Priests (VERIFIED C:310-315 `DEF_HEAL_SHARE_PCT 25`, `DEF_HEAL_MAX_HIT
  10.0`, `DEF_HEAL_MAX_SEC 10.0`). A hit reaches the 10-per-hit cap at 40 damage. A quick hit already does 41 at Iron Lv 15 (41 x 25% =
  10.25 -> 10), so **from the Iron wand up a tap heals as much as a charged hit for 1/5 of the Mana - about 5x more healing per Mana**
  (sustained in combat at 2.5 Mana/s with Iron: taps about 8 HP/s, charged shots about 1.7 HP/s; the 10/s cap still limits both). At
  Copper Lv 10 a tap heals 5.75 (23 x 25%) for 2 Mana vs 10 for 10 Mana charged (about 2.9x per Mana); at Wood they are equal.
- **Divinity XP from heals** = HP healed (SkyySkills rows: 1 per HP on others, 1.25 on yourself, cap 900 a minute) -> it follows the heal
  (so taps also pay heal XP faster per Mana, up to the 900 / minute cap). Kill XP: a kill with a class weapon (`combat.classWeaponOnly`,
  class:weapons:Priest = the prefixes) - quick-shot kills count.
- **Question 5 (PROPOSED fix, not in SkyyArmory 0.1):** a small SkyyClasses update makes a quick hit count 1/5 toward the per-hit cap
  (its projectile id is in SkyyArmory's bridge list `armory:quick`, section 8): a capped tap heals 2, so healing per Mana equals the
  charged shot's. Other choices: keep it (the heal numbers are placeholders), or raise the caps (then big charged hits heal a lot more:
  an Iron Lv 15 charged hit would heal about 50).
- Kit: unchanged (`Weapon_Wand_Wood:1`).

---

## 7. Server Setup (SkyWynn Menu > Server Setup > Armory)

Config kit `tools/skyycfg.py` (kit 1.1), page title "Armory", admin node `skyyarmory.admin`, file `mods/Skyy_SkyyArmory/config.properties`.

**Runtime (live):**

| Key | Label (<= 40) | Type | Default | Help (<= 100) |
|---|---|---|---|---|
| `part.tune` | Wand damage tune | bool, part | on | Off = every wand hits for its built-in numbers (tune and quick damage ignored). |
| `tune` | Damage by wand (%) | table: entry = Wood (quick only), Copper, ... Onyxium; column % (10-500) | 100 each | Both shots of that wand x this %. Wood: quick shot only (its hold is the shared vanilla orb). |
| `quick.damage` | Quick shot damage (% of charged) | int 5-100 | 20 | 20 = 1/5 of the charged shot (built in). Scales quick-shot hits only. |
| `part.spawn` | Quick shot size / speed | bool, part | on | Off = quick shots keep the built-in speed and full size. |
| `quick.size` | Quick shot size (%) | int 20-100 | 60 | Size of the blue orb, % of the charged orb. New shots only. 100 = same size. |
| `quick.speed` | Quick shot speed (x charged) | dec 1-5 | 3 | 3 = Skyy's 3x (built into the orb). New shots only. |
| `check.on` | Wand Mana check in the log | bool | on | One INFO table at start (and when SkyySkills' Mana rows change); WARN per wand over the share. |
| `check.share` | Mana check share (%) | int 10-100 | 40 | Warn when a charged shot needs more than this share of a Priest's Mana at the wand's first level. |

`quick.size` is read-only when the build uses `QUICK_SIZE_MODE = "model"` (the size is then baked into the model copy, 2.3).
`quick.damage` is an editor addition (the brief: every number editable where the engine allows); `quick.size` / `quick.speed` follow
the critic's items 2 and 4. All three are UNVERIFIED in game until test step 8 / 10.

**Build-time (read-only rows, flag `ro`, value from `customGet` - the SkyySkills `spell.manaDivisor` pattern, S:11390):** one row per wand
("Copper Wand (fixed in the jar)": "10 / 2 Mana - x2.25 - 56 / 11 damage - Lv 10-18"), "Quick shot (fixed)" (built-in speed 90 blocks/s =
3x, cadence 0.35 s, look blue / ice, size mode scale / model, animation), "Wand art style" (B, LOCKED), "Wood wand quick shot" (on / off).

**Runtime vs build-time (VERIFIED):**
- **Build-time: the Mana costs, the tap / hold keys and the art.** The cast check (StatsCondition Costs) and the spend (ChangeStat) are
  interaction assets whose values go to the client (`StatsConditionInteraction#configurePacket` copies `costs`;
  `ChargingInteraction#configurePacket` copies the Next map) and the client predicts the cast (`Predictable.SELF`). Changing them on the
  server only would make client and server disagree. Textures, icons, blockymodels, particles and trails are client files.
- **Runtime: damage, speed and size.** The legacy Projectile asset (Damage, MuzzleVelocity, Gravity) and the ModelAsset are never sent to
  the client (their stores have no packet generator, 2.3); the client only sees the orb entity. So damage is tuned live by ArmoryTuneSys
  (`tune`, `quick.damage`) and the quick orb's speed and size by ArmorySpawnSys (`quick.speed`, `quick.size`). The built-in values stay
  in the assets, so with both Java parts off (or broken) the wands still hit, fly and look as the table says (full size).
- **Later option (UNVERIFIED, not in 0.1):** the engine has a public runtime asset API (`AssetStore#loadAssets` / `loadBuffersWithKeys` /
  `loadAssetsFromPaths`, the asset-editor path) and every Interaction load rebuilds every root (S:12152-12153), so a probe could make
  costs "editable, applied at the next restart" by loading regenerated SkyyArmory interactions at plugin start. Needs a probe build first.

---

## 8. Bridges and cross-mod contracts

**SkyyArmory publishes** (`System.getProperties().get("skyy.bridge")`, java.lang types only):
- `armory:wands` -> String `id:charged:quick:mult:chargedDmg:quickDmg,...` (all 8, Wood included).
- `armory:fn:info` -> `Function(Object[] {"wand", itemId})` -> `Object[] { Integer charged, Integer quick, Double mult, Integer chargedDmg,
  Integer quickDmg, Double tunePct }` or null.
- `armory:quick` -> String, the 8 quick projectile ids (for SkyyGear's flat-line follow-up and SkyyClasses' heal-cap follow-up).
- `armory:check` -> String, the last Mana check line.
- `config:def / fn / epoch:SkyyArmory` (config kit).

**SkyyArmory reads:** `config:fn:SkyySkills` ops `keys mana.classBase` and `get perk.combat.manaPerLevel` / `overall.manaPerLevel` /
`perk.alchemy.manaPerLevel` (+ the future per-class row), `config:epoch:SkyySkills`; `config:fn:SkyyGear` `keys level.material` for the
live band starts (built-in bands as fallback). Read-only ops only (CONFIG-CONTRACT: `get` returns "" for table rows - use `keys`).

**Contracts other mods own that SkyyArmory relies on (keep stable):**

| Mod | Contract | Proof |
|---|---|---|
| SkyyGear | `Weapon_` + material word -> band; no "skyy" in gear ids; `Weapon_Wand_` = spell (K = 1, Magical Power, Mana Steal, charged x0.15); GearShotTrack records any player projectile + its asset name; charged = launched only from the largest Charging key; craft level = crafter's class skill in the band | G:1053, G:5026, G:831/5109/6630, G:8853, G:5914, G header 0.2 (4) |
| SkyyClasses | `Weapon_Wand_` = Priest; ShotTrack; PriestHealSys on landed damage | C:254, C:637, C:662 |
| SkyySkills | SPELL GEN touches only Assets.zip ids; its clash check refuses its 32 item + 8 interaction ids in any live-set jar - **SkyyArmory must never ship `Weapon_Wand_Wood / _Wood_Rotten / _Tribal` or those 8 interactions**; Wood rung = its `Wand_Cast_Left_Charged` 5 | S:2507, S:1891-1892 |
| SkyySacks | /craft lists every CraftingRecipe with a Weapon_Bench requirement under Smithing (primary output `Weapon_*`) for players whose Weapon Bench accessory tier >= `RequiredTierLevel`; recipe id `<item>_Recipe_Generated_0` | K:5079, K:5119, K:286 |

**SkyyArmory owns `Wand_Primary`:** its build refuses any SET jar or pack mod that ships an asset named `Wand_Primary` (and any of its
other ids). Proposed for the next SkyySkills: add `Wand_Primary` to its clash list as "owned by SkyyArmory".

**Prerequisites (pin these first, or in the same deploy):** `tools/deploy_set.py` SET still pins SkyyGear 0.2 and SkyySkills 0.4.12.
- **SkyyGear 0.2.1** (`SkyyGear/SkyyGear-0.2.1.jar`, built 2026-10-02): the level damage behind the "first level" numbers, the shot
  tracker / charged walk on our ids and the "Spell at Lv N" tooltip line (3.2, 3.4). Without it the wands hit for the asset numbers.
- **SkyySkills 0.4.13** (`SkyySkills/SkyySkills-0.4.13.jar`, built 2026-10-02, in its fix round): Mana keeps refilling while charging /
  tapping (2.5).
- **Pin order:** SkyyGear 0.2.1 -> SkyySkills 0.4.13 -> SkyyArmory 0.1 (each reviewed and cross-checked; one deploy may carry all three).

**Follow-ups for other mods (not in SkyyArmory 0.1):**
1. **SkyySkills (the next one after 0.4.13; PROPOSED here, not queued anywhere yet):** a per-class row "Max Mana per class level" (a
   table like "Base Mana by class": Priest 5 - or 4, question 1 - others 0) so the stopgap `perk.combat.manaPerLevel` (which Mages get
   too) is not needed; optionally list `Wand_Primary` as SkyyArmory's in its clash check.
2. **SkyyClasses (if Skyy picks it, question 5):** `PriestHealSys` counts a quick-shot hit (projectile id in `armory:quick`) 1/5 toward
   `maxPerHit`, so a tap heals at most 2 and healing per Mana matches the charged shot (6).
3. **SkyyGear (0.2.x, optional):** (a) mostly done: 0.2.1's "Spell at Lv N: lo-hi" line already covers the wands (3.4); a per-shot line
   from `armory:fn:info` ("Charged at Lv 12: 120 (10 Mana) / Quick: 24 (2 Mana)") would only add the Mana and the tune %; (b) a hit
   weight 0.2 on the flat True / element lines for the projectile ids in `armory:quick` (R8); (c) the 0.2.3 loot round's mystery items can
   include the `Wand` family from SkyyArmory.
4. **SkyyMenu (next):** MODS_VERSIONS + help text (tap = quick shot, hold = charged shot, Server Setup > Armory).
5. **Main session:** the prerequisites above, then pin `("SkyyArmory", "0.1")` in `tools/deploy_set.py` SET; a rollback note (once
   players own metal wands, removing SkyyArmory removes those items - what the engine does with unknown saved item ids is UNVERIFIED).

---

## 9. Tests (the harness must EXECUTE them; `SkyyArmory/test_skyyarmory_0.1.py`, bare JVM, `-XX:-UsePerfData`, TEMP in scratch)

**How to decode through the engine codecs - PROVEN in this spec's scratch run (2026-10-02):** a bare decode fails twice - the
interaction `Type` codecs are registered by `InteractionModule#setup` (`Interaction.CODEC.register("Charging", ChargingInteraction.class,
ChargingInteraction.CODEC)` ...), and referenced keys are validated against asset stores (`AssetStore.validate` -> NullPointerException
"Supplier.get() is null"). What worked: (1) `Options.parse(new String[0])` (else `HytaleAssetStore.<clinit>` throws), (2) for every
referenced type build and `AssetRegistry.register` a `HytaleAssetStore` (the `EntityStatsModule#setup` recipe: `builder(cls, map)
.setPath(..).setCodec(cls.CODEC).setKeyFunction(getId)` + `setReplaceOnRemove` for `IndexedLookupTableAssetMap` stores) - `register` then
throws an NPE from the missing event bus **after** the store is in the registry (catch it), (3) register the 8 interaction type codecs.
After that, these decoded with **no validation failure and no unknown key**: vanilla `Wand_Primary` (next = {0.0 -> inline chaining, 0.35
-> Wand_Cast_Left_Charged}), `Wand_Cast_Left_Charged`, `Wand_Cast_Effect`, `Wand_Cast_Fail`, root `Wand_Primary`, both orb projectiles,
the orb ModelAsset, the GreenOrbTrail ParticleSystem, the SkeletonMage Trail; a test StatsCondition read back `rawCosts {Mana=10.0}` and a
ChangeStat `entityStatAssets {Mana=-10.0}, valueType Absolute, changeStatBehaviour Add, entityTarget USER`. The critic's bare-JVM run
(2026-10-02) also decoded this spec's `Charging` JSON (string keys "0" and "0.35") and `LaunchProjectile` JSON with no unknown key
(StatsCondition `Costs` needs an EntityStatType store). **Items (`Item.CODEC`):** plain `decodeJson` stops at `Tags` ("putTags ...
Function.apply(Object) is null", `AssetExtraInfo$Data.putTags`); decode through `AssetBuilderCodec#decodeJsonAsset(RawJsonReader,
AssetExtraInfo)` instead (VERIFIED the method exists; the critic reproduced that it gets past Tags). The next blockers are in
`Item#processConfig`, which reads asset stores (VERIFIED bytecode): `UnarmedInteractions.getAssetMap()`, `ItemQuality.getAssetMap()` - it
casts the store's map to `IndexedLookupTableAssetMap`, so that store must be built with one (a `DefaultAssetMap` gives a
ClassCastException) - `ItemReticleConfig`, `SoundEvent`, `ItemSoundSet`; the critic also hit ItemPlayerAnimations, ParticleSystem and
RootInteraction. `AssetStore#loadAssetsFromDirectory` needs `HytaleServer.get()` (not needed for decoding). Reference existence is
checked separately (T2) because the decode did not fail on key names it could not look up.

| # | Test | Pass condition |
|---|---|---|
| T1 | Engine-codec decode of every generated asset | 7 items (`Item.CODEC`), the 56 interactions incl. the `Wand_Primary` override (`Interaction.CODEC`), 7 roots (`RootInteraction.CODEC`), 15 projectiles (`Projectile.CODEC`), the quick-orb model (`ModelAsset.CODEC`), trail (`Trail.CODEC`), particle systems / spawners, the 6 embedded recipes (`CraftingRecipe.CODEC`, the SkyyGear AB8 pattern): no exception, no validation failure, no unknown key |
| T2 | Reference closure | every interaction id, projectile id, model, particle SystemId, TrailId, texture, icon, sound, item / resource id, bench id + category exists in the jar or Assets.zip; no reference to SkyySkills' 8 overridden interactions except `Wand_Primary` 0.35 -> `Wand_Cast_Left_Charged` |
| T3 | Mana gate simulation (Python, SkyySkills `spell_casts` rules, S:2076) | per wand: tap = check Q then spend Q, hold = check C then spend C, Failed spends 0, check == spend; numbers == section 4.3; quick == charged / 5; Wood: tap 1 / 1, hold = the pinned SkyySkills jar's 5 / 5 |
| T4 | Engine read-back (decoded objects) | each StatsCondition `rawCosts` Mana == C or Q; each ChangeStat `entityStatAssets` Mana == -C or -Q; each LaunchProjectile `getProjectileId()` == the table |
| T5 | Tap / hold selection | each Charging's `next` keys == {0.0, 0.35}; the `jumpToChargeValue` rule (largest key <= value) on 0, 0.1, 0.34, 0.35, 2.0 -> quick, quick, quick, charged, charged |
| T6 | Projectiles + spawn hook | `getDamage()` == round(25 x mult) / round(5 x mult); quick `getMuzzleVelocity()` == 3 x charged (90 vs 30); Gravity 0; TerminalVelocity > 0; every other field (TimeToLive included) == the resolved vanilla orb; the quick model asset's HitBox == the charged orb's (+-0.1); `QUICK_SIZE_MODE = "model"`: the scaled Fireball copy's boxes are exactly size x the vanilla ones. **ArmorySpawnSys on real engine objects** (a holder from `ProjectileComponent.assembleDefaultProjectile` + `shoot`, with the Projectile store registered as in the decode recipe): a quick id gets `EntityScaleComponent.getScale()` == quick.size / 100 and a velocity length == 90 x (quick.speed / 3); quick.speed 3 = the velocity vector untouched; a charged id, the vanilla orb and `part.spawn` off = no component, velocity untouched; a non-SPAWN reason = untouched. If the bare JVM cannot build that holder (the component registry needs the entity modules), test the system's decision function on plain values instead and leave the engine part to T-live - say which in the harness output. (No reach test: the engine never reads TimeToLive, 2.3.) |
| T7 | Cadence | quick chain >= the vanilla tap chain computed from Assets.zip (0.346 s); charged chain == vanilla (0.667 s) |
| T8 | SkyyGear cross-mod (SkyyGear 0.2.1 jar in the same JVM, its real static code) | `GearLevel.band(id)` == the band table; `GearData.isGear / isSpell` true, `skyyItem` false, `slotOf` == 1; `GearBase.kOf(id, true)` == 1; `GearBase.mult` at the band start == F x bonus; **the jar's real charged walk, no Python replica:** reuse `SkyyGear/test_skyygear_0.2.1.py` section Z3 (the engine model built from JSON - real Interaction / RootInteraction objects - walked by the jar's `GearChg`, about lines 2265-2548; its `launchCode` checks about line 2647) with our generated files added: `GearChg.launchCode(wand, quickPid) == 0` and `GearChg.launchCode(wand, orbPid) == 1` for the 7 wands, and for the overridden Wood wand (`SkyyArmory_QuickOrb_Wood` 0, `Skeleton_Mage_Corruption_Orb` 1); `GearBase.spellRange` gives the quick - charged range (3.4) |
| T9 | Recipes | each embedded recipe == the mirrored shortbow recipe minus Armory (inputs, bench + category + tier, time, knowledge), output the wand x1; Onyxium has none; no recipe id clash with Assets.zip or any SET jar |
| T10 | Clash scan | no SET jar / pack mod / installed mod ships any SkyyArmory id; our jar ships none of SkyySkills' 40 files / 32 item ids / 8 interaction ids (run SkyySkills' `_spell_clash` rule on our jar) |
| T11 | Style switch | `SA.verify()` passes; `SA.wand_art(z, metal, style)` with A and B: both give valid PNGs (64 x 32 textures, 64 x 64 icons, RGBA, decoded by `SA.png_decode`), A != B, two runs = same bytes, the jar holds style B only (the lock); the blue quick texture (`SA.recolor` of SkeletonMage.png onto `SA.palette_from([Iceball_Texture.png])`) is 32 x 32, keeps the source alpha exactly, and its mean colour is blue (B > R) |
| T12 | Java | config rows publish (kit harness); `ro` rows show the table; `ArmoryTuneSys` on real engine `Damage` objects: multiplies only our projectile ids, 100% = untouched, the Wood row moves only `SkyyArmory_QuickOrb_Wood` (never `Skeleton_Mage_Corruption_Orb`), `quick.damage` 20 = untouched and 40 = quick hits x2, part off = untouched; ArmorySpawnSys as in T6; the Mana check computed from a fake `config:fn:SkyySkills`; access audit of every engine reference (protected members only from a subclass on `this`, the SkyyUiProbe 0.3.1 lesson) with the code paths executed |
| T13 | Mana rule | the section-4.2 table recomputed from the pinned SkyySkills jar's default config text; assert every charged shot <= 40% at its band start (fighter case) under the per-level number of Skyy's question-1 answer (+5 with 85, or +4 with 75), and print the table |
| T14 | Build + lint + cross-check | the build ends `assembled ...SkyyArmory-0.1.jar`; `python tools/ci/lint.py` 0 fails; all SET jars + SkyyArmory in one JVM with `-Xverify:all` |
| T-live | Plugin self-check on the real server (log) | at start: every SkyyArmory item / interaction / projectile resolves in the live asset maps from our pack (`DefaultAssetMap.getAssetPack`, the SkyySkills pack-check pattern), and the loaded values read back (StatsCondition `costs` Mana via reflection, ChangeStat, Projectile damage / speed, Charging keys) equal the table; one INFO or one WARN. The first quick orb after a start logs one INFO line with its `EntityScaleComponent` scale and its speed (proves the spawn hook ran) |

**In game (TEST-CHECKLIST draft):** 1) Priest, Copper wand (craft it at the Weapon Bench > Bow tab or `/gear give`): tap = smaller fast
blue orb, Mana -2; hold = green orb, Mana -10; below 2 Mana the tap clicks "no Mana". 2) Wooden Earth Wand: tap 1 Mana (Rotten / Tribal
too), hold 5. 3) Craft at Divinity 4 -> "Made at Lv 10 ..." note; at Divinity 12 -> Lv 12 (`/gear read`); the tooltip shows "Spell at
Lv 12: lo-hi". 4) Damage numbers: charged about 5x quick. 5) Admin `/gear charged` while holding the wand: the 0.35 s cast is FULL, the
quick shot normal. 6) In a party, quick hits heal and pay Divinity XP (from Iron up a tap heals the full 10 unless question 5's fix is
in). 7) A Warrior with a metal wand: blocked popup. 8) Server Setup > Armory: Copper 50% halves its damage at once; back to 100. Quick
shot damage 40 doubles quick hits only; back to 20. 9) Log line "[SkyyArmory] 0.1 ready - 7 wands, Wood quick shot on, pack check OK,
Mana check ..." and the first quick orb's scale / speed line. 10) Looks: style B textures, icons; the blue orb is smaller than the green
one (Quick shot size 100 -> 60 changes the next taps: proves the scale path; if 60 looks the same as 100, switch the build to
`QUICK_SIZE_MODE = "model"`), 3x faster (Quick shot speed 3 -> 1.5 halves it); the tap's arm animation fits the 0.35 s shot
(`QUICK_ANIM` CastLeftCharged; CastLeft is the other option).

---

## 10. Risks

| # | Risk | Status / mitigation |
|---|---|---|
| R1 | The client draws the recoloured texture on the vanilla wand model | UNVERIFIED in our mods; vanilla does exactly this (Rotten wand); custom Common PNG icons are proven (SkyyVault). Test step 10 |
| R2 | The client draws the new quick projectile (model asset + generated particles / trail / texture) | UNVERIFIED. Fallback `QUICK_LOOK = "ice"` (all vanilla assets), one constant |
| R2b | The client honours `EntityScaleComponent` on a projectile (the smaller quick orb) | UNVERIFIED; the server side is VERIFIED (2.3). Test step 10 (size 100 vs 60); fallback `QUICK_SIZE_MODE = "model"` (build-time smaller Fireball copy, no Java). Hitbox unchanged either way |
| R2c | ArmorySpawnSys (HolderSystem on projectiles) changes speed / size at spawn | UNVERIFIED in game; at the defaults it only adds the scale component (speed 3 = no change); `part.spawn` off = the built-in orb at once |
| R3 | Tap vs hold | The client decides (`chargeValue`); the server only warns on impossible values (2.1). Same mechanism and keys as today's wand - nothing new on the server |
| R4 | Wood wand loses its free melee tap; at 0 Mana a Priest has no free attack | Question 2 (a swing fallback on the quick check's Failed branch is possible) |
| R5 | No Damage Data box on wands; the Wood wand's current box (its melee swing) disappears | VERIFIED cause (3.4). Description lines + SkyyGear 0.2.1's "Spell at Lv N" line |
| R6 | Flat regen (5/s, 2.5/s in combat): high metals refill slowly; sustained damage barely rises with the metal | By design of the cost ladder; Mana Regen % boosts, regen while charging (SkyySkills 0.4.13, a prerequisite), a later regen-scales-with-max-Mana idea (Skyy's call) |
| R7 | Balance vs Mage staffs (flat 10 Mana, 25 orb at every metal); the Mana stopgap row also buffs Mages | Question 4; question 1 (Priest-only row) |
| R8 | Flat per-hit gear lines favour quick shots | SkyyGear follow-up 3b |
| R8b | Healing favours quick shots (10-per-hit cap: from Iron up a tap heals like a charged hit, about 5x per Mana) | Question 5; SkyyClasses follow-up 2 |
| R9 | A Hytale update adds vanilla `Weapon_Wand_<metal>` | Build check stops (1.1) |
| R10 | Hytale 0.7: vanilla Mana base 100 (research/PreRelease-Compat-Audit-1002.md), rune abilities cost Mana, SkyySkills' generator stops | SkyyArmory's build asserts the vanilla `Wand_Primary` shape and the SkyySkills anchor (2.5); costs get re-tuned with SkyySkills' 0.7 Mana decision |
| R11 | SkyyGear 0.2.1 and SkyySkills 0.4.13 are not live yet | Prerequisites, pinned first (section 8). Without SkyyGear 0.2.1 the wands hit for the asset numbers; without SkyySkills 0.4.13 tapping pauses Mana regen |
| R12 | Three vanilla wands share `Wand_Primary` | Intended (2.4); all three are 5-Mana wood-tier wands |
| R13 | Removing SkyyArmory later | Metal wands in inventories become unknown items (engine behaviour UNVERIFIED); deploy note (section 8) |
| R14 | Runtime cost editing | Not possible without the asset reload probe (7) |
| R15 | Onyxium has no vanilla recipe | Question 3 (none for now, or the Mithril shortbow recipe with Onyxium bars) |
| R16 | The tap animation does not fit the 0.35 s shot | `QUICK_ANIM` default CastLeftCharged (the 20-frame cast vanilla plays on a 0.25 s launch); test step 10 |
| R17 | Projectiles have no lifetime limit (TimeToLive is never read): quick orbs fly until a hit or 60 s, up to about 170 live orbs if a Wood-wand Priest taps into the sky for a minute (vanilla charged orbs: about 60) | Same rule as every vanilla orb today; most shots hit terrain at once. Later option: a reach cap in ArmorySpawnSys (swap the DespawnComponent) - UNVERIFIED (2.3) |

---

## 11. Stages

PROJECT-RULES section 8 (Skyy 2026-10-02 late): a new mod = a BIG job -> a full multi-agent workflow (spec critics, build, review, fix,
cross-check, deploy).

0. **Now:** the art style is settled (B, LOCKED - no art question left); Skyy answers section 12 (questions 1 and 5 change numbers or
   other mods). The Mana stopgap ("Combat: max mana per level" in Server Setup, no build) only if Skyy accepts that Mages get it too.
1. **Build SkyyArmory 0.1** (Opus): `SkyyArmory/build_skyyarmory_0.1.py` (new mod, no patch script, package `com.skyy.armory`, manifest
   `Group Skyy`, `Name "0.1 SkyyArmory"`, `IncludesAssetPack true`, main `com.skyy.armory.SkyyArmoryPlugin`): generated assets (sections
   1-5) + small Java: `ArmoryDefs` (the tables), `ArmoryCfg` (kit rows), `ArmoryTuneSys` (3.1), `ArmorySpawnSys` (2.3: quick-orb size /
   speed), `ArmoryCheck` (pack check, live read-back, Mana check), bridge keys. No commands, no pages, no saved data beyond the config file
   (no migrations). Build switches: `WAND_STYLE = "B"` (LOCKED; "A" must still build), `QUICK_LOOK` ("recolor" | "ice"),
   `QUICK_SIZE_MODE` ("scale" | "model"), `QUICK_ANIM` ("CastLeftCharged" | "CastLeft"), `WOOD_QUICK` (True | False); the `WANDS` table
   holds Skyy's question-1 answer (85 or 75).
2. **Harness** `SkyyArmory/test_skyyarmory_0.1.py` (section 9; T8 reuses SkyyGear 0.2.1's Z3 harness).
3. **Review** (Sonnet) + fixes.
4. **Cross-check** with the whole SET plus the prerequisites (one JVM, `-Xverify:all`, lint 0, SkyyGear 0.2.1 functions on our ids,
   SkyySkills' clash rule).
5. **Main session - pin order:** SkyyGear 0.2.1 -> SkyySkills 0.4.13 -> SkyyArmory 0.1 in `tools/deploy_set.py` SET (today it pins
   SkyyGear 0.2 and SkyySkills 0.4.12); deploy with the game closed; TEST-CHECKLIST section, HANDOFF / OPEN-QUESTIONS lines. If Skyy took
   the stopgap, note the Mage side effect in the TEST-CHECKLIST.
6. **Later:** the SkyySkills per-class Mana row (proposed, not queued yet); the SkyyClasses quick-shot heal cap (question 5); SkyyGear
   quick-orb hit weight; Mage staff ladder (question 4); Onyxium recipe (question 3); a quick-orb reach cap (R17); the runtime cost-reload
   probe if Skyy wants costs editable in game; the next SkyyArmory content (Crude armor, Lv 50+ gear).

---

## 12. Questions for Skyy (each with the recommended default)

1. **Priest Mana for the bigger wands.** Today a Priest has about 30 Mana at every level: Iron is half of it, Thorium is one cast from a
   full pool, and Cobalt and up cannot be cast. The cost steps are +5, +5 (your numbers), +10, +15, +20 and then Mithril / Onyxium. Pick:
   (a) Priests **+5 max Mana per Divinity level** and **Mithril / Onyxium 85 / 17** (the jumps keep growing: +25; every charged shot at
   most 37% of the Priest's Mana when the wand unlocks), or (b) **+4 per level and Mithril / Onyxium 75 / 15** (+15; at most 39%).
   Either way the clean version is a Priest-only "Max Mana per class level" row in the next SkyySkills. The shortcut you can switch on
   today (Server Setup > Skills > Perks, Advanced on, "Combat: max mana per level") gives every class that much per class-skill level,
   so Mages get it too (about 231 Mana = 23 staff casts at Sorcery 40 instead of 3). **[(a) +5 per Divinity level, Mithril / Onyxium
   85 / 17, through the Priest-only row; the shortcut only if you are OK with the Mage boost until then]**
2. **Wooden Earth Wand tap.** Its free melee swing becomes the 1-Mana quick shot (also on the Rotten and Tribal wands). With too little
   Mana: the "no Mana" click like a charged cast, or fall back to the old free swing? **[the no-Mana click, like vanilla casts]**
3. **Recipes.** Each metal wand = that metal's shortbow recipe (same bench tab and bars as the staffs). Vanilla has no Onyxium weapon
   recipe at all (the Onyxium staff has none either). Onyxium wand: none for now (admin / later loot only - nobody can craft it), or the
   Mithril shortbow recipe with Onyxium bars (they can be smelted from Onyxium ore)? **[none for now, like the Onyxium staff]**
4. **Mage balance.** Mage staffs stay 10 Mana and the same 25-damage orb at every metal, so a Mithril wand hits about 21x harder per cast
   (2.5x per Mana) than a Mithril staff. Leave staffs as they are for now and decide a staff ladder in its own spec later? **[yes, later]**
5. **Healing from quick shots.** A Priest hit heals 25% of its damage but at most 10 per hit, so from the Iron wand up a tap heals as
   much as a charged shot for 1/5 the Mana (about 5x more healing per Mana). Make a quick hit count 1/5 toward that cap (a tap heals at
   most 2; a small SkyyClasses update), keep it as is, or raise the caps? **[count 1/5 - healing per Mana then matches the charged shot]**

(The art style is LOCKED: style B for every metal wand, OPEN-QUESTIONS.md:233.)

---

## 13. Should SkyyArmory be merged into SkyyGear?

**Recommended: keep it separate** (as named). SkyyArmory is mostly generated content (items, art, interactions, projectiles) with very
little Java; SkyyGear is a 12,000-line systems mod with a rollback floor and a busy queue (0.2.1 damage + armor, 0.2.2 tools, 0.2.3
loot). Separate means the wands ship without waiting behind that queue, a broken wand asset never forces a SkyyGear rollback, and every
SkyyGear system already applies to the wands through stable contracts (the material word, the `Weapon_Wand_` spell prefix, the shot
tracker) - nothing is lost. SkyyArmory also becomes the home for our own items later (Crude armor, Lv 50+ gear): SkyyGear owns the stats
and rules, SkyyArmory owns the items. The costs: one more mod in the SET and in SkyyMenu's list, two places to look for "gear" work,
the Wood wand recipe stays in SkyyGear while the metal recipes live in SkyyArmory, and those contracts must not change without both
mods being checked (SkyyArmory's harness T8 runs SkyyGear's own code on the wand ids to catch it).

---

## 14. Review notes (editor pass, 2026-10-03)

Every critic item was re-verified before it was applied (HytaleServer.jar bytecode read with javassist - methods, constructors and static
blocks; Assets.zip read-only; the build scripts and jars named below; scratch `tools/dev/scratch/armoryedit/`, deleted afterwards).

| # | Critic item | Verdict | Proof (re-checked) | Changed |
|---|---|---|---|---|
| 1 | Art style is already locked | APPLIED | OPEN-QUESTIONS.md:230 (the mix, REPLACED) and :233 (LOCKED "actually do B", every metal) | header, 0, 1.3, 7, 11, 12 |
| 2 | The 0.4 ModelAsset scale cannot make the quick orb smaller | APPLIED (both new paths UNVERIFIED in game) | `LegacyProjectileSystems$OnAddHolderSystem#onEntityAdd` -> `Model.createUnitScaleModel` -> `createScaledModel(asset, 1.0f, null)`; `ModelAsset.getMinScale / getMaxScale / generateRandomScale` callers = ProjectileConfig, NPC code, SpawningContext, /model, `Model.createRandomScaleModel` - none on the legacy projectile path; the "Models" store has no packet generator; `EntityTrackerSystems$EntityModel#tick` -> `queueUpdatesFor` -> `new ModelUpdate(Model.toPacket(), entityScale)`; `Projectile_default.png` 0 of 1,024 pixels opaque | 2.3 (size paths, ArmorySpawnSys), 7, T6, T-live, step 10, R2b / R2c |
| 3 | TimeToLive is never read | APPLIED | `Projectile#getTimeToLive`: no caller; the field is read only by equals / hashCode / toString / codec lambdas; deadTimer only from `onProjectileHitEvent` / `onProjectileMissEvent`; `assembleDefaultProjectile` attaches `despawnInMilliseconds(time, 60000)` (offsets 59-62) | 2.3, 7, T6, R17 |
| 4 | Speed and damage are server-only, so more rows can be live | APPLIED (UNVERIFIED in game) | `AssetRegistryLoader.<clinit>`: "Projectiles" store (offsets 2526-2599) and "Models" store built without `setPacketGenerator`; `ProjectileConfigPacketGenerator` (offset 4066) serves the new ProjectileConfig only; `LaunchProjectileInteraction#firstRun`: `shoot` (283) before `addEntity` (293); `SimplePhysicsProvider#getVelocity` returns the live vector and `#initialize` never sets velocity | 2.3, 7 (`quick.speed`, `quick.size`, runtime vs build-time) |
| 5 | The Wood tune row cannot scale the hold | APPLIED | the Wood hold launches the shared vanilla `Skeleton_Mage_Corruption_Orb` (2.4), not one of the 15 ids `ArmoryTuneSys` matches | 3.1, 7, T12 |
| 6 | The stopgap is not harmless | APPLIED | S:2489-2490 (staff 10, spellbook 20 asserted); S:11388 row help "Mage 30 = 3 staff casts"; S:11352 the row is per class-skill level for every class (`PerkCfg.MANA`, S:3203); Sorcery 40 at +4 = 190.8 Mana | 0, 4.1, 4.2, 11, 12 |
| 7 | 75 / 15 breaks "bigger jumps"; offer +5 per Divinity level | APPLIED, wording corrected | pools recomputed (+5 fighter 35 / 80.2 / 105.2 / 130.4 / 155.4 / 205.6 / 230.8; shares 14 / 12.5 / 14 / 19 / 26 / 29 / 36.8%; 85 needs +4.54 for 40%). Correction: 85 / 17 is the main session's proposal recorded at OPEN-QUESTIONS.md:206-210, not a number Skyy gave. The recommended default is now (a) +5 with 85 / 17 | 0, 3.3, 4.2, 4.3, 12 |
| 8 | The Rotten orb is not an orphan | APPLIED | `Server/Projectiles/NPCs/Undead/Skeleton_Archmage/Skeleton_Archmage_Corruption_Orb.json` has `"Parent": "Wand_Wood_Rotten_Corruption_Orb"` | corrections list |
| 9 | Pins and queued features are stale | APPLIED | `SkyySkills/SkyySkills-0.4.13.jar` exists (file time 2026-10-02 22:58), "MANA WHILE CHARGING" at `build_skyyskills_0.4.13.py:23`, its header says it is still in a fix round; `SkyyGear/SkyyGear-0.2.1.jar` exists; `tools/deploy_set.py:20` pins SkyyGear 0.2 and SkyySkills 0.4.12 | 2.5, 8 (prerequisites, pin order), 11, R11 |
| 10 | The skyyart contract does not match the kit | APPLIED | `tools/skyyart.py` KIT_VERSION "1.0": `assets`, `verify`, `wand_texture(z, metal, style)`, `wand_art(z, metal, style)` -> (texture, icon), `recolor` = gradient map, `palette_from`; no `wand_icon`, no hue recolour, no blockymodel scaler; mean colours (191, 247, 124) and (126, 217, 243) | 1.3, T11 |
| 11 | Tests that would not run or not catch problems | APPLIED | `AssetBuilderCodec#decodeJsonAsset(RawJsonReader, AssetExtraInfo)` exists; `ItemQuality.getAssetMap` casts to `IndexedLookupTableAssetMap`; `Item#processConfig` reads `UnarmedInteractions`, `ItemQuality`, `ItemReticleConfig`, `SoundEvent`, `ItemSoundSet` stores; `SkyyGear/test_skyygear_0.2.1.py` Z3 (~2265-2548) walks real engine objects with the jar's `GearChg`, `launchCode` checks ~2647 | 9 intro, T6, T8, T12 |
| 12 | The tap animation is too long | APPLIED | `Cast_Left.blockyanim` duration 50 (R-Arm keys 0 / 30 / 40 / 50), `Cast_Left_Charged.blockyanim` duration 20 (0 / 10 / 20) | 2.1, 2.2 (`QUICK_ANIM`), step 10, R16 |
| 13 | Healing is not 1/5 | APPLIED | `build_skyyclasses_0.1.10.py:310-315` (25%, 10 per hit, 10 per second); Iron Lv 15 quick 41 x 25% = 10.25 -> capped 10 | 0, 6, 8, 12 (question 5), R8b |
| 14 | Onyxium recipe fallback | APPLIED | Assets.zip scan: only `Ingredient_Bar_Onyxium`'s own Furnace recipe (from `Ore_Onyxium`), the ore, `BlockTypeList/Ores.json` and a block migration mention Onyxium bars / ore; SkyyGear 0.2 gave the Onyxium staff no recipe either | 0, 5.1, 12 (question 3), R15 |
| M1 | Show the cost steps and both Mana options | APPLIED | - | 0, 4.2, 12 |
| M2 | Name the deploy order in the pin step | APPLIED | - | 8, 11 |

**Rejected:** none. Small slips in the critique that change nothing: the 0.4.13 jar's file time is 22:58 (critique: 23:11); the
"staff 10 / spellbook 20" line is now OPEN-QUESTIONS.md:415 (critique: 408); the texture means differ by 1 (rounding).

**Editor's own findings (VERIFIED, applied):**
- E1: the draft said Thorium "cannot be cast" today; 25 < 30, so it is one cast from a full pool (its own 4.2 row showed 82% / 68%).
- E2: the per-class Mana row was called "already queued"; no line in OPEN-QUESTIONS / HANDOFF / RESUME queues it - now "proposed".
- E3: SkyyGear 0.2.1 already prints "Spell at Lv N: lo-hi" for spell weapons (`GearBase.spellRange` ~G:6783, tooltip ~G:7205), so the
  wands get a damage line without a bridge (3.4, follow-up 3a).
- E4: added the live `quick.damage` row (ArmoryTuneSys, default 20 = untouched), because the brief asks for every number to be editable
  where the engine allows.
- E5: the quick orb's TimeToLive stays the vanilla 3.1 (ignored by the engine) instead of 1.05, so the jar carries no misleading number.
