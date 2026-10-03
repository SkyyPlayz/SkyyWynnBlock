# SkyyGear 0.2.3 "loot round": build spec (mystery items, drop boost, Smithing-tree hooks)

> **Skyy's decisions win over this draft:** OPEN-QUESTIONS.md "Q&A with Skyy 2026-10-02": the drop-boost line ("boost the drop rates of
> unidentified weapons and armor", l.174-177), the Smithing tree identify line (l.178-182), the Wynncraft-style unidentified items line
> (l.183-190), the Smithing tree + XP line (l.122-127), the SkyyArmory / Priest wand lines (l.199-213, 2026-10-02 late), the
> Skill-Trees-2 answers (l.247-254: Smithing XP x10, "Smithing readers + gear:extras ride the SkyyGear 0.2.3 loot build", nodes whose
> reader is not live are not buyable) and the SkyyMobs rewards lock R5 (l.61-62: "slightly better gear rarity from higher levels").

*Written 2026-10-02. Research and planning only: nothing is built, deployed or committed. Owner: Skyy (they/them). Build base: the
FINISHED `build_skyygear_0.2.2.py` (tool levels, `research/Tool-Levels-Spec.md`), itself on top of 0.2.1 (damage + armor by level).
SkyyGear has no patch scripts: `build_skyygear_0.2.3.py` = a direct copy of the finished 0.2.2 script with only the changes below.
Hooks are named by class and function; line numbers point into the stable live script G (0.2) because 0.2.1 / 0.2.2 move lines.
Critic pass applied 2026-10-02 (editor): every correction was re-checked first; see "Review notes" at the end.*

**Legend.** LOCKED = Skyy decided it (source named). VERIFIED = seen in HytaleServer.jar bytecode (class#method, read with a scratch
javassist printer), a build script (file:line), Assets.zip or a jar. UNVERIFIED = needs the game. PLACEHOLDER = a number Skyy has not
picked; every placeholder is a Server Setup row (section 7). PROPOSED = a default that waits for Skyy's answer (section 12).

| Ref | File |
|---|---|
| G | `SkyyGear/build_skyygear_0.2.py` (live) - same functions in 0.2.1 / 0.2.2 |
| M | `SkyyMobs/build_skyymobs_0.1.1.py` |
| S | `SkyySkills/build_skyyskills_0.4.12.py` |
| K | `SkyySacks/build_skyysacks_0.7.12.py` |
| A | `SkyyAuctions/build_skyyauctions_0.1.2.py` |
| C | `SkyyClasses/build_skyyclasses_0.1.10.py` |
| T | `SkyyTrees/build_skyytrees_0.2.5.py` |
| T2 | `research/Skill-Trees-2-Spec.md` (SkyyTrees 0.3, written today) |
| SA | `tools/skyyart.py` (the shared art kit, v1.0, commit 5f2e965) |
| AR | `research/SkyyArmory-Spec.md` (SkyyArmory 0.1, written today 23:11) |
| ML / GL / W | `research/Mob-Levels-Plan.md` / `research/Gear-Levels-Wynn-Spec.md` / `research/SkyyWorldGen-Plan.md` |
| HS | `HytaleServer.jar` (game `latest`, copied into scratch, read only) |
| AZ | `Assets.zip` (game `latest`, entries copied into scratch, read only) |

---

## 0. Plain words (for Skyy)

- **New drops look like Wynncraft's.** A mob or chest gives you an **"Unidentified Sword"**, "Unidentified Bow", "Unidentified
  Chestplate" ... It shows its **exact level** and its **rarity** (name colour + frame). You can see it is a sword, but not which
  sword (material, model, stats) until you identify it.
- **How hidden it really is (question 5):** the exact level plus the material level ranges narrow it down. For a given type and level
  there are usually about 3 possible items, sometimes only 1 (a Lv 30 mace is always the Cobalt Mace), so a sharp player guesses the
  real item about 4 times in 10. Wynncraft shows a level RANGE instead; you choose.
- **18 mystery items:** one per weapon type (sword, longsword, daggers, kunai, mace, axe, battleaxe, club, spear, bow, crossbow,
  staff, wand, spellbook) and one per armor slot (helmet, chestplate, gauntlets, leggings). **They do not stack:** when a mob drops 3
  spears at once you get 3 separate "Unidentified Spear" items, each with its own rarity.
- **Their look:** a dark grey "shadow" of that weapon or armor piece with a **?** on the icon. It is made from the game's own art when
  the mod is built, so nothing from the game goes into our public repo. On the ground every mystery item has the same plain white
  glow (the game draws the glow per item type, not per rarity); the rarity shows in the frame and the name colour.
- **They cannot be used:** you cannot wear them or fight with them. Magic Bags never pick them up. You CAN keep them in your vault,
  trade them and sell them on the Auction House (it shows "Unidentified Sword", level and rarity).
- **Identify** (`/identify`, same page and costs as today) turns the mystery item into the real item **in the same slot**, so a full
  inventory is fine. The page tells you what it was: "It was a Mithril Sword!"
- **More drops (your 2026-10-02 pick):** every kill of a levelled mob has an **extra 4% (1 in 25)** chance to drop one mystery item at
  **that mob's level**, and higher-level mobs give slightly better rarities (your SkyyMobs rewards lock). About **1 in 3 freshly
  filled world loot chests** gets one extra mystery item at **the zone's level**. The game fills about 45 loot chests an hour around an
  exploring player (about 200 in a fast burst), most of them in chests you walk past, so roughly 15 (up to 65) extra pieces an hour
  are created in chests. Both chances are Server Setup numbers.
- **Only fresh chests get the extra piece:** loot chests that the game fills from now on (land you have not explored yet). Chests that
  already exist keep what they have (question 4). Chests the game filled before this update still hold old-style "Unidentified Iron
  Sword" items; they identify as before.
- **Anti-farm:** only kills by a player count (not pets, lava, falling, other mobs), Creative kills do not count, and one player can get
  at most 20 extra drops an hour (a safety net; normal play gets about 5 an hour).
- **Gear the game already drops** (mob weapons, chest armor) becomes mystery items too. **Items you already own stay exactly as they
  are** and identify like before.
- **Smithing tree (SkyyTrees 0.3):** SkyyGear reads the tree's craft-rarity, reforge-roll, identify-roll, identify-rarity-step,
  Masterwork and cheaper-cost nodes plus the class trees' Strength the day the tree ships (all 0 until then), and it tells SkyyTrees
  which nodes it reads, so those can be bought. Crafting weapons and armor and identifying now pay **Smithing XP** at your x10 numbers
  (craft 500-16,000, identify 250-8,000 by rarity). Tools pay Smithing XP when you reforge them (0.2.2), not when crafted.
- **One full round** (items that could be lost or duplicated, coins, several mods). Six questions in section 12.

---

## 1. Mystery items

### 1.1 The list (one per weapon type and armor slot)

The type of a gear item: a `Weapon_` id = its second word (`Weapon_Sword_Iron` -> `Weapon_Sword`, VERIFIED: every one of the 197 vanilla
+ pack weapon ids has a family word there, scan of AZ + `More_Crossbow_Tiers.zip`); an `Armor_` id = its armor slot
(`Item.getArmor().getArmorSlot()`, AZ field `Armor.ArmorSlot`: Head / Chest / Hands / Legs, 111 ids). Shields, bombs, guns, darts,
deployables and ammo are not gear (G:746 `EXCLUDE_DEF`, ammo rule G:748-797), so they have no mystery item.

| Type key | Item id | Name (en-US) | Look from (vanilla, referenced) | Candidates | Levels with a candidate | Class (lean, 3.3) |
|---|---|---|---|---|---|---|
| Weapon_Sword | Skyy_Unid_Weapon_Sword | Unidentified Sword | Weapon_Sword_Iron | 23 | 1-49 | Warrior |
| Weapon_Longsword | Skyy_Unid_Weapon_Longsword | Unidentified Longsword | Weapon_Longsword_Iron | 17 | 1-49 | Warrior |
| Weapon_Spear | Skyy_Unid_Weapon_Spear | Unidentified Spear | Weapon_Spear_Iron | 17 | 1-49 | Warrior |
| Weapon_Shortbow | Skyy_Unid_Weapon_Shortbow | Unidentified Bow | Weapon_Shortbow_Iron | 18 | 1-49 | Archer |
| Weapon_Crossbow | Skyy_Unid_Weapon_Crossbow | Unidentified Crossbow | Weapon_Crossbow_Iron | 6 (2 vanilla + 4 More Crossbow Tiers) | 15-49 | Archer |
| Weapon_Staff | Skyy_Unid_Weapon_Staff | Unidentified Staff | Weapon_Staff_Iron | 24 | 1-49 | Mage |
| Weapon_Axe | Skyy_Unid_Weapon_Axe | Unidentified Axe | Weapon_Axe_Iron | 13 | 1-49 | Berserker |
| Weapon_Battleaxe | Skyy_Unid_Weapon_Battleaxe | Unidentified Battleaxe | Weapon_Battleaxe_Iron | 15 | 1-49 | Berserker |
| Weapon_Mace | Skyy_Unid_Weapon_Mace | Unidentified Mace | Weapon_Mace_Iron | 11 | 1-49 | Berserker |
| Weapon_Club | Skyy_Unid_Weapon_Club | Unidentified Club | Weapon_Club_Iron | 22 | 1-49 | Berserker |
| Weapon_Wand | Skyy_Unid_Weapon_Wand | Unidentified Wand | Weapon_Wand_Wood (the only wand model) | 5 (+ SkyyArmory metal wands later) | 1-22 (gap 14) | Priest |
| Weapon_Spellbook | Skyy_Unid_Weapon_Spellbook | Unidentified Spellbook | Weapon_Spellbook_Grimoire_Brown (a plain book, no flame) | 6 | 20-42 (gap 28-29) | Priest |
| Weapon_Daggers | Skyy_Unid_Weapon_Daggers | Unidentified Daggers | Weapon_Daggers_Iron | 16 | 1-49 | Assassin (not playable yet) |
| Weapon_Kunai | Skyy_Unid_Weapon_Kunai | Unidentified Kunai | Weapon_Kunai | 1 | 20-27 | Assassin (not playable yet) |
| Armor_Head | Skyy_Unid_Armor_Head | Unidentified Helmet | Armor_Iron_Head | 27 | 1-49 | everyone |
| Armor_Chest | Skyy_Unid_Armor_Chest | Unidentified Chestplate | Armor_Iron_Chest | 27 | 1-49 | everyone |
| Armor_Hands | Skyy_Unid_Armor_Hands | Unidentified Gauntlets | Armor_Iron_Hands | 26 | 1-49 | everyone |
| Armor_Legs | Skyy_Unid_Armor_Legs | Unidentified Leggings | Armor_Iron_Legs | 25 | 1-49 | everyone |

- **Candidates** = the vanilla + pack gear ids of that type that the extra drops may pick (section 3.3): every gear id of AZ and the SET
  pack jars, minus quality Developer / Debug / Template / Technical / Tool, the `FAM_DEV` prefixes (G:937) and `*_NPC` ids. Dropped:
  Armor_QA_* (3), Armor_Trooper_* (3), Weapon_Longsword_Praetorian_NPC, Weapon_Mace_Scrap_NPC, Weapon_Shortbow_Test_Zoom (VERIFIED, scan:
  308 ids = 304 AZ + 4 More Crossbow Tiers, 9 dropped, 299 candidates in 18 types).
  Levels = the item's band (`GearLevel.band`; build twin `band_lookup` G:1113): the table above is that scan.
- **How much the type + exact level give away (VERIFIED, the same scan, 2026-10-02):** over the 771 (type, level) pairs that have a
  candidate, the median is 3 candidate items; 14.5% of the pairs have exactly one (Lv 30 Mace = Cobalt only, Lv 30 Spear = Cobalt
  only; Lv 30 Sword = Cobalt, Doomed or Frost), 37.7% have two or fewer, and a random guess among the candidates is right 41% of
  the time on average (mean of 1 / candidates; the picker gives every candidate the same chance). Rarity adds nothing (any item can
  roll any rarity). This follows from two choices: the exact level (Skyy's default) and the material bands (LOCKED +3 overlap).
  Question 5 offers a Wynncraft-style level range. Converted vanilla drops can also be guessed from their source (a Trork Guard's
  spear is always the Stone Trork spear, AZ `Drop_Trork_Guard.json`); the extra drops pick at random and have no such tell.
- **Armor words:** vanilla names armor by material (Iron Helm / Cuirass / Gauntlets / Greaves, Linen Gloves, Silk Pants - AZ
  `server.lang`). The mystery names use neutral slot words; "Chestplate" is Skyy's own word.
- **Kunai** has one vanilla item, so identifying it only reveals the rolls. It keeps its own type anyway (a thrown knife is not a pair of
  daggers); `loot.weights` can set its weight to 0.
- **Mod gear without a type here** (another mod's `Weapon_Scythe_*`, ...) keeps today's 0.2-style unidentified document on the real
  item (1.7). Ids are stable forever: never rename a `Skyy_Unid_` id (owned items would turn into unknown items).

### 1.2 How the look is generated at build time (never committed)

- **Proof that a server mod can ship its own client art (VERIFIED, jar / zip listings):** the SET plugin jar `SkyyVault.jar` ships
  `Server/Item/Items/Utility/Skyy_Vault_*.json` with `Common/Icons/ItemsGenerated/Skyy_Vault_*.png` (seen in game, AR 1.2): custom items
  with their own icons work from a plugin jar. A recoloured TEXTURE on a model is proven only for a pack zip:
  `More_Crossbow_Tiers.zip` carries `Common/Items/Weapons/Crossbow/*.blockymodel` + `*_Texture.png` + icons. From a plugin jar it is
  UNVERIFIED until seen (SkyyArmory's wand textures prove it first if SkyyArmory ships earlier). SkyyGear's manifest already has
  `IncludesAssetPack: true` (jar `manifest.json`).
- **Vanilla re-texture pattern (VERIFIED, AZ):** `Weapon_Sword_Steel_Rusty` = `Sword/Steel.blockymodel` + `Steel_Rusty_Texture.png`;
  `Weapon_Shortbow_Ricochet` = `Bow/Iron.blockymodel` + `Ricochet_Texture.png`; `Weapon_Wand_Wood_Rotten` = the Wood wand model + another
  texture. So a vanilla model + a recoloured texture of the same size (same UV layout) works.
- **Tool: `tools/skyyart.py` (SA, v1.0, exists).** Pure Python (zlib + struct, its own `png_decode` / `png_encode`), no Pillow, no JVM,
  deterministic (fixed zlib level 9, no time chunks: the same input gives the same bytes, so the "byte-identical re-run" check holds;
  Java ImageIO output is not guaranteed identical across JDKs, so it is not used). OPEN-QUESTIONS l.199-206 names this kit for every
  build-time recolour.
- **Kit additions (the skyyui rule: what the kit lacks is added to the kit, proven in its self-check `SA.verify()`, and a kit harness
  if the main session adds one):**
  - `SA.GREY_RAMP` = a 2-stop gradient (dark `#2b2f3a` -> light `#b4bcc8`, PLACEHOLDER colours; the kit's gradient format = a tuple of
    (r, g, b) steps, `SA.sample`);
  - `SA.glyph_q(icon)` = a centred **?** from a built-in 5x8 pixel bitmap scaled x3, opaque white with a 1 px `#1b1e26` outline,
    written premultiplied (alpha 255), no font (deterministic);
  - `SA.shadow_art(z, item_json)` -> (texture PNG, icon PNG) for one representative, the two steps below.
- **Per type (18):**
  1. Read the representative's resolved `Texture` and `Icon` PNG bytes from AZ (Parent chain: `SA.item_parts`, or the SkyyAccessories
     `visual_of` / `icon_of` pattern, `SkyyAccessories/build_skyyaccessories_0.5.2.py:3716-3746`). All 18 exist (VERIFIED: icons 64x64,
     textures 32x32 up to 128x64 and 32x128; the Grimoire_Brown spellbook = `Spellbook/Grimoire.blockymodel` + a 64x64 texture).
  2. **Texture** -> `Common/Items/SkyyGear/Unid/<TypeKey>.png` = `SA.recolor(tex, SA.GREY_RAMP, regions=None, rank=0)`: every texel
     (alpha >= 1) is gradient-mapped by its own luminance, alpha kept, so shape and shading stay and the material colour goes ("show the
     type, never the material").
  3. **Icon** -> `Common/Icons/ItemsGenerated/Skyy_Unid_<TypeKey>.png` = `SA.recolor_icon(icon, SA.GREY_RAMP, None, rank=0)` then
     `SA.glyph_q`. Vanilla icons are PREMULTIPLIED with the alpha steps 0 / 49 / 127 / 206 / 255 (SA module notes); `recolor_icon`
     un-premultiplies, maps and premultiplies again, so edge pixels get no bright halo. Not `SA.render_icon`: it is proven only for the
     wand / staff `[45, 90, 0]` view (SA module notes).
  4. The bytes go into the jar through `B.assemble(extra_files=...)` (zipfile `writestr` takes bytes). The build also writes a contact
     sheet `tools/dev/scratch/<build>/unid_sheet.png` (all 18 icons + textures) for the reviewer and Skyy; nothing lands in the repo.
- **Build checks:** each PNG decodes (`SA.png_decode`), has the source size, no pixel keeps a hue (max - min channel <= 24, icons
  un-premultiplied first), the icon carries the ? pixels, **every icon pixel keeps r, g, b <= alpha** (premultiplied edge check), no
  generated path exists in AZ or any SET jar, and the build is byte-identical on a re-run.

### 1.3 The item asset (`Server/Item/Items/SkyyGear/Skyy_Unid_<TypeKey>.json`, 18 files)

```json
{ "TranslationProperties": { "Name": "server.items.Skyy_Unid_Weapon_Sword.name",
                             "Description": "server.items.Skyy_Unid_Weapon_Sword.description" },
  "Quality": "Skyy_Gear_Normal", "MaxStack": 1, "Variant": true,
  "Icon": "Icons/ItemsGenerated/Skyy_Unid_Weapon_Sword.png", "IconProperties": <copied from Weapon_Sword_Iron>,
  "Model": "Items/Weapons/Sword/Iron.blockymodel", "Texture": "Items/SkyyGear/Unid/Weapon_Sword.png",
  "PlayerAnimationsId": "Sword", "DroppedItemAnimation": <resolved from the representative>, "ItemSoundSetId": <copied>,
  "Tags": { "Type": ["Unidentified"], "Family": ["Sword"] } }
```

- **PlayerAnimationsId = the representative's RESOLVED value (VERIFIED, AZ Parent chains), never the family word:** Sword `Sword`,
  Longsword `Longsword`, Spear `Spear`, Shortbow `Bow`, Crossbow `Crossbow`, Staff `Staff`, Axe `Axe`, Battleaxe `Battleaxe`, Mace
  `Mace`, Club `Club`, Wand `Wand`, Spellbook `Spellbook`, Daggers `Daggers`, Kunai `Throwing_Knife`. Armor uses `Item`, never vanilla
  armor's `Block` (see below).
- **Absent keys are omitted, never written empty (VERIFIED, AZ):** `DroppedItemAnimation` is copied only when the representative
  resolves one (`Weapon_Crossbow_Iron`, `Weapon_Kunai` and the 4 iron armor pieces have none); `ItemSoundSetId` likewise
  (`Weapon_Kunai` has none). AE1 checks both.
- **No** `Weapon`, `Armor`, `Tool`, `Utility`, `Interactions`, `Recipe` or `Categories`. `Variant: true` + no `Categories` keeps it out
  of the creative item library (the SkyyAccessories 0.5.1 filter, `build_skyyaccessories_0.5.2.py:3740-3762`). `Quality` = the
  SkyyGear quality shipped in the same jar; every stack carries its rarity quality (1.4).
- **Not wearable (VERIFIED, HS):** the armor container's slot filter is `ArmorSlotAddFilter#test` = `item.getArmor() != null &&
  getArmorSlot() == slot`, installed by `ItemContainerUtil#trySetArmorFilters` for `InventoryComponent$Armor`. No `Armor` block = refused.
- **Not in the off-hand (VERIFIED, HS):** `InventoryComponent$Utility` filter lambda = `ItemStack.getItem().getUtility().isUsable()`.
- **Not a weapon (VERIFIED, HS + AZ):** `Item#processConfig` builds an item's interactions as its own map + `putIfAbsent` of the
  unarmed set named like its `PlayerAnimationsId` + `putIfAbsent` of the unarmed set `"Empty"` (bytecode offsets 109-240). AZ has only
  three unarmed sets: `Item` (`Primary` = `Block_Primary` -> UseBlock, else `Block_Attack`), `Block` (+ `Secondary` = `Block_Secondary`
  = block placement mode) and `Empty` (`Primary` = UseBlock, else `Unarmed_Attack` = the fist swing; `Use`, `Pick`, `Wielding`
  Double_Jump). So a weapon-type mystery item (`Sword`, `Bow`, `Throwing_Knife` ...) gets the `Empty` set only (left click = a punch),
  the same as an empty hand; with "Item" it attacks like a held ingot. Either way it is no weapon, and it is not gear
  (`GearData.isGear` returns false for every `Skyy` id, G:4621 + `skyyItem` G:4549), so no gear stat, gate or popup applies.
- **Armor uses `Item`:** vanilla armor's `Block` would add the block-placement `Secondary`, because a mystery item has no `EquipItem`
  interaction of its own. UNVERIFIED: how the grip and the punch look together; if odd, the build constant `MYSTERY_ANIM` switches every
  weapon to `Item`.
- **Language:** `items.Skyy_Unid_<TypeKey>.name=Unidentified Sword` and `.description=Identify it to find out which sword it is.` in
  the jar's `Server/Languages/en-US/server.lang`.
- **Build check change:** G:1813 asserts "no `Server/Item/Items/` entry at all". 0.2.3 narrows it: every such entry is a `Skyy_Unid_`
  file whose id exists in no AZ / SET jar file. The harness decodes each item JSON through the engine's `Item` codec (AE1, the AB8
  recipe-decode pattern).

### 1.4 Hidden data: the mystery document + the sealed real item id

- **Why sealed (VERIFIED, HS):** `ItemStack#toPacket` copies `metadata.toJson()` into `ItemWithAllMetadata.metadata` for every stack the
  client sees (bytecode offsets 71-90). The 0.1 spec already refused to store rolls before identify for this reason (SkyyGear Stage 1
  spec 5.6). A plain real id would let a modded client see which items are worth identifying and dump the rest on the AH.
- **The document** (metadata key `"SkyyGear"`, schema v1, unknown fields kept by every reader as today):

| Field | Meaning |
|---|---|
| `mys` | the type key (`Weapon_Sword`); must match the item id `Skyy_Unid_<mys>` |
| `r`, `lvl`, `id:false`, `kind:"combat"`, `gate:"class"`, `mods:[]` | rarity, the exact level shown, unidentified, the usual gate (the owner's class weapon skill) |
| `q` | units inside: 1. Only the rest of a spear / spellbook stack that found no free slot when it was split keeps its units here (fallback, see 1.7; never more than the real item's MaxStack) |
| `src` | `drop` / `chest` (converted vanilla gear) plus `ex:true` for the extra rolls; `admin` for `/gear mystery` |
| `ls` | where the level came from: `mob`, `zone`, `ring`, `world`, `droplist` (drop-list zone), `band` (band start) - for `/gear read` and the log |
| `x` | the sealed real id: base64url(12-byte IV + AES/GCM/NoPadding(P)) with P = 64 bytes: [1 length byte][UTF-8 real id][zero bytes]. An id over 63 bytes pads to the next multiple of 64 (logged once; no vanilla or SET id is longer than 31). AAD = `"SkyyUnid1|" + mys + "|" + lvl + "|" + r + "|" + q` |
| `at` | creation time |

- **Why the padding (VERIFIED, the 1.1 scan):** AES-GCM keeps the plaintext length, so an unpadded blob is 12 + len(realId) + 16 bytes
  and base64url without padding keeps that length visible. For 62.7% of the 2,765 (type, level, candidate) triples of the candidate table
  the id length alone singles out the real item among the candidates of that type and level (length-set sizes 1: 1,735; 2: 860;
  3: 126; 4: 44). With P fixed at 64 bytes every blob has the same length. AE3 asserts it.
- **Key:** 16 random bytes (`SecureRandom`) in `Skyy_SkyyGear/unid.key` (one base64 line), created once at setup with the kit's atomic
  write (tmp + fsync + ATOMIC_MOVE). It is never in the kit's `FILES` (never exported, never in History). An unreadable key file is
  never overwritten: ERROR line, and new mystery items are made without `x` (decided at identify, below).
- **Open at identify:** decrypt `x` and read the length byte; the result must exist in the item map, be gear, and have the same type.
  Any failure (key lost, item removed by an update, tampered, no `x`) = **re-pick** a candidate of the same type whose band holds `lvl`
  AND whose MaxStack >= `q` (3.3 picker), logged `UNID reopen`. The player always gets the type, level and rarity they saw. No candidate
  with MaxStack >= `q` (only possible for a fallback `q` item whose key was lost) = the identify is refused before any coin moves,
  logged; an admin settles it (`/gear mystery reveal`, `/gear give`). (VERIFIED, AZ MaxStack: `Weapon_Spellbook_Fire` 1 - no MaxStack,
  default 1 for an item with a Weapon section, G:774-783 `az_max_stack` -, `Rekindle_Embers` 5, Demon / Frost / Grimoire 25, spears 5
  or 30.)
- javassist-safe: `javax.crypto.Cipher`, `GCMParameterSpec`, `SecretKeySpec`, `java.util.Base64` - no lambdas, explicit arrays.

### 1.5 Tooltip (vanilla look; `ItemDisplayMetadata` + the stack quality, as gear tooltips today)

`ItemDisplayMetadata` holds only a name and a description (VERIFIED, HS fields `name`, `description`), so the mystery look must come
from the item asset (1.3) and the text from metadata. Lines mirror `GearView.lines`' unidentified branch (G:6222-6240):

```
Unidentified Sword                                   <- rarity hex (the quality's own "Rare" label shows too: VisibleQualityLabel)
Lv 12 - Requires Archery 12 (you: 9)                 <- gate line, green / red exactly as gear (owner = the holder)
Rarity: Rare                                         <- rarity hex
Unidentified - which sword it is and its modifiers appear when you identify it.     <- #878e9c
Cannot be used until identified.                     <- armor: "Cannot be worn until identified."  (vanilla red)
Holds 3 - they identify together.                    <- only on a fallback item with q > 1
Identify: /identify - 490 coins                      <- gold #E8A93B; cost = cost.identify(r, lvl) x q x (1 - Haggler)
```

- **Frame and name colour by rarity:** the stack quality = `Skyy_Gear_<Rarity>` (`ItemStack.withQuality`, the 0.1 mechanism, per-stack
  field saved by `ItemStack.CODEC`). VERIFIED, HS: the stack packet carries only that quality index (`ItemWithAllMetadata.quality`,
  `ItemStack#toPacket` offsets 55-60), and protocol `ItemQuality` holds the tooltip / slot textures, text colour and label - so frame,
  name colour and label follow the rarity.
- **The drop glow does NOT follow the rarity (VERIFIED, HS):** `Item#processConfig` (offsets 410-464) copies the ASSET quality's
  `ItemEntityConfig` (particle system, colour) into the item; the client receives it once per item id (protocol `ItemBase.itemEntity`),
  and protocol `ItemQuality` has no entity config. So every mystery item glows like its asset quality `Skyy_Gear_Normal`
  (`Drop_Common`, G:611 + G:1236) whatever its rarity, exactly as rolled real gear does today. (One item id per rarity would fix the
  glow but breaks "one mystery item per type", 108 ids: not done.)
- The holder's lines re-render through the existing passive scan (`GearStamp.scan`, owner lines 6.3 of the Stage 1 spec) with a
  mystery branch that is idempotent: a second scan of an unchanged mystery item writes nothing (otherwise the 300-rewrites-per-10-s
  valve `GearStamp.paused`, G:6926, pauses that player). The view signature never includes `x`.

### 1.6 What they can and cannot do

| Action | Result | Proof |
|---|---|---|
| Wear / off-hand | refused | 1.3 filters |
| Fight with it | the unarmed `Empty` / `Item` sets (a punch), no gear stats | 1.3 (`Item#processConfig`) |
| Stack | never (MaxStack 1; equal metadata is required anyway: `ItemStack#isStackableWith`) | HS |
| Magic Bags / auto-pickup / Deposit all | never pooled | K:832-853 `SackDefs.homeOf`: any `Skyy_` id -> null unless a cooked dish |
| Accessory Bag | never (accepts accessory ids only) | `AccDefs.isAccessory`: `Skyy_Talisman_*` / `Skyy_Accessory_*` only (`build_skyyaccessories_0.5.2.py:824-828`) |
| Vault | allowed | SkyyVault treats only `Skyy_Vault_` ids specially (`build_skyyvault_0.1.5.py:1163`) |
| `/trade` | allowed | SkyyEssentials blocks only `Skyy_Sack_*,Skyy_Accessory_Bag` (`build_skyyessentials_0.1.7.py:2197`) |
| Auction House | allowed; name, level, rarity through the gear bridges (8) | A:1747-1781 |
| Reforge page | not listed (not gear) | G `GearForge.rows` lists gear |
| `/gear relevel` | skipped (not gear: `gearish` false for `Skyy_` ids) | G:4737-4739, `GearAdmin.relevelInv` G:10738-10776 |
| Drop / pick up / death drop | like any item; keeps its document; on the ground the plain `Drop_Common` glow (1.5) | - |
| Creative library | hidden (`Variant`) | 1.3 |
| `gear.include` | can never make it gear: `Skyy_Unid_` joins `NEVER_GEAR` (G:727) | - |

### 1.7 Which items become mystery items (and at what level)

Every NEW unidentified document today is made by `GearRoll.unidDoc(id, col, src)` (G:5906) on the paths below (+ the admin `/gear unid`
and `/gear give --unid`). With `part.mystery` on, each makes a mystery item instead when the item's type exists (1.1); otherwise it keeps
the 0.2-style document on the real item:

| Path (today) | Becomes | Level |
|---|---|---|
| Mob death drops: `GearDropSys.onEntityAdded` -> `GearTag.unid(s, 1)` (G:8744, G:8188) | mystery, `ItemComponent.setItemStack`; a stack = one drop entity per unit (stacks, below) | the dying mob's level from the death mark (3.4), moved into the real item's band |
| Fresh loot chests: `GearChestTag` -> `GearTag.tagContainer` (G:9374-9380, G:8203) | mystery in the same slot; a stack splits into free slots of the same chest | the chest's zone level (4.2), into the band |
| First open / break of other world containers: `GearChestOpen.decide` (G:9097) | mystery in the same slot (+ the split) | zone level at the container from the 4.2 chain (computed in `process`, G:9183, and passed into `decide` through a new overload; the old signature delegates with "none"); none = band start |
| SkyyExploration chest luck (loot window): `GearChestOpen.lootStack` / `lootSlot` (G:7003) | mystery (one stack: the `q` fallback for a stack) | zone level at the opened container (its position is remembered with the loot window); none = band start |
| `gear:fn:unid` (mode 9, no callers today: VERIFIED, grep of every build script) | mystery (the returned stack has another item id) | the 4.2 chain at an optional world + position argument (GL 8, carried); without one = band start |

- **Level rule (LOCKED for the extra drops; question 2 for vanilla drops):** level = the mob / zone level moved into the real item's band
  (below the band = its start, above = its cap), then `GearLevel.clamp`. `loot.levelFrom = band` restores the 0.2 rule (band start)
  for converted vanilla gear only; the extra drops always use the mob / zone level.
- **Carried from GL 9 (stage 4 rows):** `loot.aboveYou` (default 0 = off; a pacing lever): when set, mob-sourced items (extra roll and
  converted drops: the killer) and first-open / loot-window conversions (the opener) never get a level above that player's gate skill
  + N; the band start still wins. Fill-time chests have no player and ignore it. `loot.level.world` joins the zone chain (4.2).
  **Retired:** `loot.mobSpread` (GL 9): Skyy's "matching the mob's level" means the exact mob level.
- **Stacks (lock "they do not stack"):** a spear (MaxStack 5 / 30) or spellbook (5 / 25) stack becomes one mystery item PER UNIT, each
  with its own rarity roll and seal - the same idea as 0.2's fresh-chest split ("a fresh loot chest splits its stacks into single
  rolled items", OPEN-QUESTIONS l.423-424; `GearTag.tagContainer` G:8203-8224 + `GearStamp.split`).
  - Chests and world containers: the units go into free slots of the same container; the units that find no free slot stay ONE
    mystery item holding `q` (fallback, nothing is lost).
  - Mob drops: the dropped entity keeps the first unit and `GearDropSys` spawns one more drop entity per further unit with
    `ItemComponent.generateItemDrops(store, list, pos, rotation)` + `CommandBuffer.addEntities(holders, AddReason.SPAWN)` (the call
    DropDeathItems makes, VERIFIED signature); the new entities reach `onEntityAdded` again and are ignored (not gear). A failed spawn
    = the `q` fallback.
  - The SkyyExploration loot window hands over one stack: the `q` fallback.
  - Vanilla stacks this touches (VERIFIED, AZ drop lists): `Weapon_Spear_Stone_Trork` 2-4 (Drop_Trork_Guard, Drop_Trork_Sentry),
    `Weapon_Spear_Bone` 2-4 (Drop_Feran_Longtooth), `Weapon_Spear_Leaf` 2-4 / 2-5 (Zone1 + Zone3 Kweebec chests),
    `Weapon_Spellbook_Rekindle_Embers` 5 (Drop_Skeleton_Burnt_Praetorian).
  - A stack bigger than the real item's MaxStack (vanilla does this once: `Weapon_Sword_Doomed` 1-4 at weight 0.1 in
    `Drop_Bramblekin.json`, MaxStack 1) is NOT converted: it keeps the 0.2-style document, nothing is lost. With `part.mystery` off,
    chests keep 0.2's per-item split.
- **Rarity:** `odds` Mob column for mob drops, Chest column for chests (G `GearRoll.pickRarity`, the `odds.<id>` table). Mob-sourced
  rarity (converted mob drops and the extra mob roll) also gets the **level shift** of the R5 lock: every weight above Normal x
  (1 + `odds.levelShift` x (L - 1)), L = the mob's level, default 0.02 (ML 5 "Gear rarity", ML stage 2 row `odds.levelShift`; Lv 30
  = Unique-and-up weights x1.58). This is SkyyGear's part of the lock and needs only `mob:fn:level` (SkyyMobs 0.1+), so it does not
  wait for SkyyMobs stage 2. Chest rarity is not shifted.

---

## 2. Identify

### 2.1 The swap (one world-thread call, same slot, no loss, no dupe)

`GearIdent.identify(c, slot, expId, expFp, u, who, free, give, all)` (G:10126) gets a mystery branch; everything else of 0.2's write
safety stays (Stage 1 spec 1.7):

1. **Same item:** `GearForge.same(it, expId, expFp)` (G:7139; fingerprint = id + quality + metadata JSON, G:7130). `x` has a random IV,
   so every mystery item has its own fingerprint. Refuse while `profile:busy`, and on the page's 400 ms click guard.
2. **Cost** = `GearIdent.costOf(it, u)` = `costIdentify(r, lvl)` (G:4299) x `q` x (1 - Haggler, section 6). **Coins taken first**
   (`coins:fn:take`), log `TAKE`.
3. **Real id** = open `x` (1.4), else re-pick (same type, band holds `lvl`, MaxStack >= `q`; none = refused before step 2).
4. **Rarity** = `r`, or one step up by the Appraiser node (2.3).
5. **Document** = a fresh identified document for the real id at `lvl` (stamped explicitly, like `newDoc(realId, r2, true, src, lvl)`
   G:5758, but rolled through the identify path so the tree bonuses of section 6 apply), `idAt`, `idBy`, `from:"mys"`.
6. **Write:** `c.setItemStackForSlot(slot, GearData.put(new ItemStack(realId, q), doc, u))` (`put` G:6471 writes the document, quality
   and tooltip). The new stack replaces the mystery item **in its own slot**: no free slot is needed, a full inventory changes nothing.
   Mystery items can only sit in the hotbar, storage or backpack (1.3 filters), and those take any item (VERIFIED, HS: only
   `InventoryComponent$Armor` / `$Utility` install slot filters - the only callers of `ItemContainerUtil#trySetArmorFilters` /
   `trySetSlotFilters`).
7. **Failure** (exception or `Transaction.succeeded() == false`): refund (`coins:fn:add`), log `REFUND`; the slot still holds the mystery
   item (the write did not happen).
8. **Success:** log `IDENTIFY <who> <uuid> Skyy_Unid_Weapon_Sword -> Weapon_Sword_Mithril rare lv44 x1 [mods] cost N (step: legendary)`;
   Smithing XP (2.4); the page shows the reveal (2.5).

**Why there is no dupe:** the mystery item and the real item never exist at the same time - one `setItemStackForSlot` on the world thread
replaces one with the other. A second click, a second page or "Identify all" after the first swap sees a new fingerprint and is refused.
A disconnect cannot interleave (the page handler and the disconnect both run on the world thread). A crash between the coin save and the
player save can lose one payment or one identify, never create an item (section 10, risk 2).

### 2.2 Every identify path

- **Identify page:** `GearIdent.rows(inv)` (G:10082) lists 0.2-style unidentified gear AND mystery items (icon = `ItemIcon { ItemId }` of
  the mystery id: metadata free, the HANDOFF section 2 rule). `costOf` / `refuse` (G:10100-10124) get the mystery branch; `costOf`
  gains the UUID (`costOf(it, u)`, Haggler) and already includes `q`, because `IdentifyPage.total` (G:10270) multiplies it by the stack
  quantity, which is 1 for a mystery item.
- **Identify all** (`GearIdent.allIn`, G:10181): includes mystery items, each paid on its own, unchanged stop / skip rules.
- **Admin** `/gear identify` (free): the same core with `free = true` (no coins, no XP, no tree step - "admin and free actions pay
  nothing", T2 3).
- **Later NPC:** calls the same core.

### 2.3 Rarity step-up from the Smithing tree (Skyy's lock)

Aligned with T2 section 3 node **S7 Appraiser (`Smithing.SAppraise`)**: "On identify: 1% chance the item steps up one rarity (10%);
never above Fabled, never Mythic or Set". SkyyGear reads `tree:fn:bonus` (Object[]{UUID, "Smithing.SAppraise"} -> Double fraction,
T:3201-3213; fractions VERIFIED by `TreeFx.value` T:2400-2414 and SkyyCooking's reader `build_skyycooking_0.1.3.py:1618-1640`). Chance =
that value x 100 %, capped by `tree.idStepMax` (10). On a hit: `r + 1`, never above `tree.idStepTo` (Fabled), a Set item never steps, and
nothing steps into Mythic or Set. It applies to old 0.2-style unidentified items too (the same `GearRoll.identify`). Reads 0 until
SkyyTrees 0.3.

### 2.4 Smithing XP (Skyy's lock item 4, numbers from Skyy's x10 answer)

- **Today (VERIFIED):** reforge pays (`skill:fn:addxp` source `gear:reforge`, `xp.reforge` 5-160, G:7260-7267); identifying and
  crafting gear pay nothing (Stage 1 spec 5.7 "No Smithing XP for identifying"; SkyySkills `RecipeXp.classify` pays only Alchemybench
  and Furnace recipes, S:4656-4686, so Weapon / Armor bench crafts get no Smithing XP).
- **New, through the existing bridge** `skill:fn:addxp` = apply(Object[]{UUID, "Smithing", Number xp, String source, String pkey}) ->
  Boolean (S:9935-9950, published S:13061; Smithing is grantable by default `bridge.addxp.skills`, S:582; caps 500,000 per call /
  3,000,000 a minute, S:1393-1394 - far above one grant: the largest is a Mythic identify of a `q` 5 item, 40,000):
  - identify: `xp.identify[final rarity]` x `q`, source `gear:identify`, after a successful paid identify;
  - craft: `xp.craft[rarity]` per crafted **gear** item (`GearData.isGear(id)`: weapons and armor), source `gear:craft`, in
    `GearCraftTask.rollIn` (vanilla benches, G:7455) and `gear:fn:roll` mode 8 (SkyySacks /craft, G `GearFn.apply`).
    - **Tools never pay craft XP** (they are not gear: Tool-Levels-Spec "Tools stay not gear", `isGear` G:4621-4629 never takes `Tool_`;
      they pay `xp.reforge` when reforged, 0.2.2). This closes the loop T2 3 found: `Tool_Sickle_Copper` = 2 trunks + 1 copper bar,
      salvage returns 1 copper ore + fibre (`research/Smithing-Smelting-Spec.md` l.125), which at the x10 rows would pay about 1,000
      XP a lap for 2 logs.
    - **`xp.craft.exclude`** (T2 16 asked for the row): ids matching it (exact id, `Prefix*` or `*Suffix`) pay no craft XP.
      PROPOSED default `*_Crude,*_Wood` (question 6): the Crude Sword is a 0-second pocket craft of 2 rubble + 2 fibre + 2 sticks
      (AZ recipe, Fieldcraft / Workbench) and every Crude / Wood weapon is sticks, fibre, rubble, rock or logs, so at 990 XP a craft
      530 Crude Swords would buy Smithing 20.
  - **Defaults = Skyy's answer** (OPEN-QUESTIONS l.247-252, answer 6, "x10 faster than the spec's rows"): `xp.identify` 250 / 500 /
    1000 / 2000 / 4000 / 8000 (Set 2000), `xp.craft` 500 / 1000 / 2000 / 4000 / 8000 / 16000 (Set 4000). Averages at the default odds
    (G:631): identify at mob odds 605 XP, at chest odds 697 XP; craft at craft odds 990 XP, so Smithing 20 (522,425 XP, T2 3) is about
    530 crafts - Skyy's own number.
  - Admin / free actions pay nothing. A refused grant (FALSE) is logged once per source.
  - `skill:fn:craftxp` is NOT used: it classifies by recipe bench and returns 0 for gear benches (S:9987-10006).
- The Smithing Wisdom node (`xp.smithing`) boosts these grants only once SkyySkills lists Smithing in `bridge.bonus.addxpSkills` - T2
  section 12 gives that to the next SkyySkills.

### 2.5 Page changes (vanilla kit, no new page)

Rows: mystery icon + "Unidentified Sword" in the rarity colour + "Lv 12" + cost. After identify the detail panel and the summary line say
"It was a Mithril Sword!" (+ "Appraiser raised it to Legendary!" on a step) and the revealed modifiers, as 0.2 already does for revealed
lines. Ids without underscores, no periodic updates, BIG readable page (HANDOFF section 2) - unchanged layout.

---

## 3. Drops: the extra 4% per kill

### 3.1 Which kills roll (LOCKED "each kill of a leveled hostile mob"; anti-farm rules proposed)

All must hold:
1. **A levelled mob:** `mob:fn:level` (Object[]{world name, NPC UUID} -> Integer, -1 = none; M:2335-2351) returns >= 1. That is
   SkyyMobs' own allow list: hostile mobs + neutral fighters, never animals, pets, summons, traders or (until stage 3) bosses. The entry
   is still there when the corpse drops: SkyyMobs forgets a mob when its entity is removed (`onEntityRemoved` M:2292 -> `forget`
   M:2169-2176), when it stops qualifying, or in the prune once its entity is gone (M:2185-2265, entries younger than 60 s kept); the
   removal runs in `DeathSystems$CorpseRemoval`, which comes AFTER DropDeathItems (VERIFIED order, 3.4). Without SkyyMobs no mob has a
   level, so no extra roll. `loot.mob.neutral` (default on) can leave neutral fighters out (attitude NEUTRAL by
   `WorldSupport.getDefaultPlayerAttitude()`, the SkyyMobs `attitudeOf` recipe M:2119).
2. **A player made the kill:** `DeathComponent.getDeathInfo().getSource()` is a `Damage$EntitySource` whose `getRef()` is **valid
   (`Ref.isValid()`) and in the same store** (`ref.getStore() == store`: the killer may have logged out or changed world while a corpse
   timer ran) and has a `PlayerRef` (VERIFIED, HS: `ProjectileSource extends EntitySource`, so arrows and spells count with their
   shooter). This is SkyySkills' kill-XP rule (`KillSys.onComponentAdded`, S:9678-9705). Lava, falls, drowning, other mobs and other
   mods' pets do not count.
3. **Not Creative** (`Player.getGameMode()`), unless `loot.mob.creative`.
4. **Under the hourly cap:** at most `loot.mob.capPerHour` (20) extra drops per physical player in any rolling 60 minutes (memory only,
   resets on restart; a safety net, not a pacing tool: at 4% a player needs 500 kills an hour to reach it). Staff with `skyygear.admin`
   skip the cap (staff bypass).
5. **Once per death:** a small map of NPC UUIDs already rolled (pruned after 60 s), on top of the role flag (3.4).

**Not needed as rules (VERIFIED):** vanilla has no player spawner or spawn egg in survival - `Egg_Spawner_*` items appear in no drop
list, recipe or prefab (AZ scan; their `SpawnNPC` interaction is admin / creative only). Marker, beacon and world spawns are normal
grinding (Wynncraft-style camps). Farming low mobs gives low-level items (the level follows the mob). Another mod's spawner is what the
hourly cap is for.

### 3.2 The roll

`RNG.nextDouble() * 100 < loot.mob.chance` (4 = 1 in 25, LOCKED) with SkyyGear's `SecureRandom` (`GearRoll.RNG`). Rolls that miss write
nothing; a hit writes `LOOT xmob <killer> <uuid> <mob role> Lv<n> -> Skyy_Unid_<type>=<realId> <rarity> lv<n> <world> x y z` to gear.log
(server only; the real id may be logged). `part.lootMob` is its own switch: today's `part.drops` (the tag on vanilla drops) does not
turn the extra roll on or off.

### 3.3 Item choice (mob drops and chest extras share it)

1. `L` = the mob level (chests: the zone level, 4.2). `L'` = min(`L`, `loot.levelTop` 49 = the top of the vanilla bands until our own
   Lv 50+ gear exists, and - mob drops with `loot.aboveYou` > 0 - the killer's gate skill + `loot.aboveYou`).
2. **Eligible types** = types with at least one candidate whose band holds `L'` (1.1 table: e.g. no Kunai below 20, no Spellbook at
   28-29, no Wand above 22, no Crossbow below 15).
3. **Group, then type:** armor with chance `loot.armorShare` (50 %), else weapons; then the type inside the group by `loot.weights`
   (default 1 each) over its eligible types. A group with no eligible type falls back to the other. This gives exactly half weapons,
   half armor at every level. (VERIFIED, the 1.1 scan: one weight per type - weapons 1, armor slots 3.5 - gave weapons 44% at Lv 1-13,
   28-29 and 43-49, 41.7% at Lv 14, 46.2% at Lv 15-19 and 30-42, 48.1% at Lv 23-27 and 50% only at Lv 20-22, because some weapon types
   have no candidate at some levels.)
4. **Class lean (question 1, PROPOSED, mob drops only):** when the group is weapons and the killer has a playable class, with chance
   `loot.classLean` (50%) the type is picked again by weight among the eligible weapon types of that class: `class:<uuid>` -> class
   name (C:1639), `class:weapons:<Class>` -> id prefixes (C:4412: Archer `Weapon_Shortbow_,Weapon_Crossbow_`, Warrior sword / longsword /
   spear, Mage staff, Berserker axe / battleaxe / mace / club, Priest wand / spellbook, Assassin daggers / kunai). "Playable" = the
   class is listed in `class:list`, which holds ENABLED classes only (`ClassDefs.listText` C:1380-1388, published C:4411): Assassin and
   Shaman are `enabled: False` in SkyyClasses 0.1.10 (C:256), so an admin-set Assassin profile (allowed by `/profileadmin setclass`,
   C:1599; its weapons stay blocked) gets no daggers / kunai lean. No class, no SkyyClasses, or no eligible class type (a Priest
   above Lv 42) = no lean. Armor is never leaned.
5. **Item** = a random candidate of that type whose band holds `L'` (equal chance each; `loot.exclude` removes ids). Candidates = the
   build-time table (1.1) + ids other mods offer on `gear:loot:add:<Mod>` (8) + `loot.include`; each must exist in the live item map,
   be gear (`isGear` / `gear.include`), have a band and map to one of the 18 types (else ignored, one WARN per id).
6. **Level** = `L'` (inside that item's band by construction).
7. **Rarity** = `pickRarity` Mob column x the level shift of 1.7 (`odds.levelShift`, L = the mob level); chests: the Chest column.
   `q` = 1. With `part.mystery` off the extra drop is a 0.2-style unidentified real item (same level and rarity).

The picker is pure (a harness runs it for every type at every level).

### 3.4 Where it spawns, and the order (proof)

**Vanilla's death drop (VERIFIED, HS):**
- `NPCDamageSystems$DropDeathItems`: `QUERY` = NPCEntity + TransformComponent + HeadRotation + not Player + DeathComponent;
  `DEPENDENCIES` = AFTER `DeathSystems$TickCorpseRemoval`, BEFORE `DeathSystems$CorpseRemoval` (`<clinit>` offsets 59-86).
- `DropDeathItems#tick`: DeathComponent `ItemsLossMode.ALL`; a role and `!role.hasDroppedDeathItems()`; then it goes on when
  `role.isDropDeathItemsInstantly()` OR the entity has **no** `DeferredCorpseRemoval` OR `DeferredCorpseRemoval.shouldRemove()`
  (offsets 98-132); `role.setDeathItemsDropped()`; list = the NPC's storage (`isPickupDropOnDeath`) +
  `ItemModule.getRandomItemDrops(dropListId)` (only while `ItemModule.isEnabled()`); if not empty: position + (0, 1, 0), HeadRotation,
  `ItemComponent.generateItemDrops(store, list, pos, rot)`, `CommandBuffer.addEntities(holders, AddReason.SPAWN)`.
- `DeathSystems$TickCorpseRemoval#tick`: returns while `DeathComponent.getInteractionChain()` is `NotFinished` (no countdown), else
  `DeferredCorpseRemoval.tick(dt)`; `shouldRemove` = `timeRemaining <= 0`.
- `DeathSystems$CorpseRemoval#tick`: returns while the chain is `NotFinished`; no `DeferredCorpseRemoval` = `removeEntity` at once;
  else removes once `shouldRemove()` (+ the death particles).
- So: a mob without a corpse timer drops and is removed in the same tick; a mob with one drops on the tick its timer reaches 0; while
  the death interaction chain still runs, a timer mob neither counts down nor drops, and a mob without a timer drops at once while its
  removal waits.
- `ItemComponent#generateItemDrop` builds ItemComponent + Transform + Velocity + PhysicsValues + UUIDComponent + Intangible +
  DespawnComponent; there is no model component, so the client draws whatever stack the ItemComponent holds when it is first sent.

**The extra drop** is spawned inside `GearDeathMark.tick` (G:8715-8734), which already copies the condition above (G:8720-8732,
including the "no corpse timer" case) BEFORE DropDeathItems (its constructor adds `SystemDependency(BEFORE, DropDeathItems)`,
G:8699-8706, registered G:9516-9524) and marks the spot for `GearDropSys`. After the mark: `GearLoot.mobRoll(...)` (3.1-3.3) builds the
mystery stack and calls `ItemComponent.generateItemDrops(store, list, pos + (0,1,0), headRotation)` + `cb.addEntities(holders,
AddReason.SPAWN)` - exactly vanilla's call (also when the mob's own drop list rolled nothing). The roll only runs for deaths
DropDeathItems itself handles: its query parts that GearDeathMark's broader query (NPCEntity + DeathComponent) lacks - TransformComponent,
HeadRotation, not a Player - are checked in `mobRoll`, so the role flag always gets set right after it. The new entity reaches
`GearDropSys.onEntityAdded`, which ignores it (not gear). Because the role flag is set by DropDeathItems in the same tick, the next tick
fails the condition for both systems: one roll per death (plus the UUID map).

**Ordering hardening (not a proven bug):** GearDeathMark only says BEFORE DropDeathItems. VERIFIED, HS: `SystemDependency(order,
class)` uses `OrderPriority.NORMAL` = 0, so BEFORE and AFTER edges both get priority 0 (`SystemDependency.resolveGraphEdge`); the graph
keeps its edges sorted by priority and puts a new edge after the equal ones (`DependencyGraph.addEdge`); dependency edges are added
first and the root edges of systems without incoming edges after them, both in system order (`resolveEdges`); and `sort` always places
the first ready edge from the start of that array. GearDeathMark is such a root, registered after every vanilla system, so it lands
after `TickCorpseRemoval` unless a system registered after SkyyGear has to run before TickCorpseRemoval: today's order is very likely
already right. The live gear.log agrees (3 "UNID mob" tags: 2026-09-30 18:29, 2026-10-02 21:56 and 22:23 - read-only look at the test
world's log). 0.2.3 still adds `SystemDependency(AFTER, DeathSystems$TickCorpseRemoval)` to GearDeathMark as hardening; it cannot
cycle (DropDeathItems is itself AFTER TickCorpseRemoval and BEFORE CorpseRemoval). AE4 runs the REAL `DependencyGraph` over the four
systems.

**The unordered fallback:** if registering GearDeathMark with its dependencies throws, G:9516-9523 registers `GearDeathMarkU` with no
order. If the scheduler then runs it after DropDeathItems, the role flag is already set and neither today's tag nor the extra roll ever
fires. 0.2.3: one WARN "extra mob drops may not fire (unordered fallback)" and `/gear lootstats` shows "death order: fallback".

### 3.5 Vanilla gear drops -> mystery items

`GearTag.mark(k, x, y, z)` (G:8159) gains the mob level (`double[]{x, y, z, level}`); `GearDropSys.onEntityAdded` (G:8744) takes the
level of the nearest mark within 2 blocks (`near`, G:8172) and converts the undocumented gear stack: `ic.setItemStack(mystery)` (the same
call that writes today's tag - live since 0.1), plus one spawned drop entity per further unit of a stack (1.7). The swap happens in
`onEntityAdded` before the first network send (3.4).

### 3.6 Expected numbers (economy check, PLACEHOLDER rates)

Kill rate: the project's own 120 kills an hour (`research/cloud/Class-Skill-Curve-Proposal.md:83`), plus 60 (casual) and 250 (fast).

| Kills / hour | Extra mob drops / hour (4%) | Legendary or better / hour | Mythic |
|---|---|---|---|
| 60 | 2.4 | 0.17 | 1 per 83 h |
| 120 | 4.8 | 0.34 | 1 per 42 h |
| 250 | 10 | 0.70 | 1 per 20 h |

(Mob odds column 50 / 30 / 13 / 5 / 1.5 / 0.5, G:631, at Lv 1. With the level shift at Lv 30 Legendary-or-better rises from 7.0% to
8.6% of the drops and Mythic from 0.50% to 0.61%.)

**Chest extras (VERIFIED from AZ + the live log; the 33% is Skyy's lock):**
- The vanilla prefab drop lists hold 0.25 gear stacks per fill on average (all 49 lists, AZ weights under the engine's container rules:
  `MultipleItemDropContainer#populateDrops` rolls each child with chance Weight / 100, default weight 100; `ChoiceItemDropContainer`
  makes RollsMin..RollsMax weighted picks).
- The live gear.log has 81 fill-time tag lines (one line per tagged gear item) over 7 clock hours with chest activity = 11.6 an hour,
  so about **46 loot-chest fills an hour** in an average exploring hour; the 2026-10-02 22:00 hour had 50 lines (in 18 distinct
  seconds), about **200 fills**. Fills happen as chunks generate around the player, so most of these chests are never opened.
- At 33%: about **15 extra pieces created an hour** (about 65 in a fast burst). Chest odds (45 / 30 / 15 / 7 / 2.4 / 0.6) make 1.5 of the
  15 Legendary or better and one Mythic about every 11 hours of exploring.
- Vanilla mob gear is rare today (3 tagged mob drops in about three days of Skyy's play, live log). `/gear lootstats` counts chest
  fills, fills with gear, extras made, extras skipped for want of a free slot and CHEST-map clears (4.1), so the first playtest measures
  the real rate.

**Identify cost as a coin sink:** expected cost per item = 140 + 12.05 x level coins at mob odds and 164 + 13.87 x level at chest odds
(`cost.identify` defaults COST_I_DEF, G:636): mob items Lv 10 = 260, Lv 20 = 381, Lv 30 = 502, Lv 45 = 682; chest items Lv 10 = 303,
Lv 20 = 441. At 4.8 mob items an hour that is 1,250-1,830 coins an hour to identify everything (Haggler -20% at max); every 10 chest
pieces a player actually loots add about 3,000-4,400 coins an hour at Lv 10-20. Players will sell many unidentified (AH flood, risk 1).
Check against coin income before a public launch (the existing OPEN-QUESTIONS note on class level-up coins).

---

## 4. Chests: about 1 in 3 gets an extra piece

### 4.1 Which chests

- **Only loot chests the game fills from a drop list, at the moment it fills them** (LOCKED "world chests"; the task's "StashPlugin-
  filled, once per chest, never player chests"). VERIFIED, HS: `StashPlugin$StashSystem#onEntityAdded` -> `StashPlugin.stash(info, icb,
  StashGameplayConfig.isClearContainerDropList())` reads `ItemContainerBlock.getDroplist()`, rolls `ItemModule.getRandomItemDrops`, puts
  the stacks into shuffled slots (`addItemStackToSlot`). SkyyGear's `GearChestMark` (BEFORE, G:9363) / `GearChestTag` (AFTER, G:9374)
  already sit around it; the live gear.log proves the AFTER side runs at fill time ("UNID chest Weapon_Daggers_Crude rare droplist
  Zone1_Encounters_Tier3 in default").
- **Once per real fill (exact condition, VERIFIED, HS `StashPlugin#stash`):** vanilla clears the drop list only when `clear` is on AND at
  least one stack was placed (offsets 325-340); a roll that gives nothing returns before that (offset 360) and keeps the list, so the
  chest fills again at its next load. Vanilla prefab lists never roll empty (their first containers have no Empty entry). So
  `GearChestTag` rolls the extra only when `GearChestMark` saw a drop list AND, after the stash, the container's drop list is null. A
  chunk reload then adds nothing. A server that switches `isClearContainerDropList` off refills chests on every load: the extra then
  rolls when the container holds more items than `GearChestMark` counted before the stash (each real refill).
- **The BEFORE -> AFTER map:** `GearTag.chestMark` clears the whole `CHEST` map once it holds more than 1024 entries (G:8227); a clear
  in a big chunk burst would drop pending tags, and now extras, silently. 0.2.3 counts every clear (`/gear lootstats`) and logs the first.
- **Never player chests:** players cannot give a container a drop list (Stage 1 spec 5.5, VERIFIED there); an admin's `/stash set` chest
  is a loot chest on purpose.
- **Never on SkyyIslands island worlds** (`GearChestOpen.island`, G:9080) unless `loot.chest.islands`.
- **All 49 vanilla prefab drop lists contain gear** (AZ scan: `Zone<1-4>_Encounters / Goblin / Kweebec / Trork / Undead / Feran /
  Outlander_Tier<n>` + `Portals_Oasis`), so "drop-list container" = loot chest.
- **Chests that already exist** (filled before 0.2.3, unopened or not) get no extra piece (question 4). Their untagged vanilla gear
  becomes mystery items at the first open (1.7); gear that 0.2 already tagged at fill time stays 0.2-style (section 5).

### 4.2 The zone level at the chest (one contract: SkyyMobs' own band lookup)

One rule for mobs and loot, and SkyyGear keeps no copy of the zone tables (the GL 5 direction). Order:
1. **`mob:fn:levelAt`** (the next free SkyyMobs version, contract 4.5) at the chest's block (`GearChestOpen.posOf`, G:9204). `L` = an even
   roll in `[lo, hi]`, once per chest. On SkyyWorldGen islands SkyyMobs answers the ring band itself once its lookup gains
   `wg:fn:ring` as step 3b (W 5.2); until then the environment rows apply (the SkyyWorldGen 0.1 test island: rim 1-3, middle 5-9,
   core 16-20, its build header).
2. **`wg:fn:ring`** (SkyyWorldGen stage 2: Object[]{world, x, z} -> `"Z1|R3|5-7|name"`, pure maths, any thread, W 5.1) read directly,
   only when SkyyMobs or its `levelAt` is missing (SkyyWorldGen 0.1 publishes no bridge keys yet, its build header).
3. **`loot.level.world`** (carried from GL 9): a Min | Cap row for a named world (hand-built zone islands, dungeons). Default EMPTY:
   W 5.4's draft rows `skywynn_zN` 1-10 / 15-25 / 30-40 / 45-60 predate the LOCKED bands and must not ship.
4. **The drop list's zone** when none of the above answers: `Zone<N>` at the start of the drop list id -> `loot.zone.Zone<N>` (Zone1 1-20,
   Zone2 20-30, Zone3 30-45, Zone4 45-60 = the LOCKED zone bands 2026-10-01). Every vanilla list but `Portals_Oasis` has one (AZ).
5. **None** = no extra piece, and the chest's vanilla gear gets band-start levels (0.2). One INFO line per world.

`mob:fn:levelAt` replaces the planned `mob:fn:band` (ML 8) for loot: that key reads SkyyMobs' per-chunk cache and returns null for a
chunk where no mob has spawned yet - exactly the chest case (W 5.4). (Main session: note it in ML 8 / W 5.4 at the next docs pass.)

Calling it at fill time: `GearChestTag` runs on the world thread inside the chunk's block-entity add. SkyyMobs' lookup = the worldgen
zone / biome (`ChunkGenerator.getZoneBiomeResultAt(seed, x, z)`, pure from the seed, M:1943-1976; the engine's own
`NPCMemory$GatherMemoriesSystem.findLocationZoneName` recipe, M:791) + the block environment (`ChunkStore.getChunkComponent` ->
`getChunkReference`, which only reads the loaded-chunk map and never loads, VERIFIED HS). While the chunk is still being added the
environment may read as unknown, so a chest in a deep lava cave can get the surface biome's band instead of the zone-top band
(UNVERIFIED, minor).

### 4.3 The extra piece

In `GearChestTag` after the fill and the conversion (1.7), when the 4.1 condition holds: `RNG < loot.chest.chance` (33 %) -> the 3.3
picker at `L` (no class lean and no `loot.aboveYou`: no player is involved) -> the mystery stack goes into a random EMPTY slot of the same
container with `setItemStackForSlot` (the call `tagContainer` already makes there, G:8203-8224). No empty slot = no extra (counted,
logged). Log `LOOT xchest <world> x y z Lv<L> <list> -> Skyy_Unid_<type>=<realId> <rarity>`.

### 4.4 Vanilla chest gear -> mystery items

At fill time (same `L`, each item moved into its own band), at the first open of other world containers (1.7), and through the
SkyyExploration loot window (1.7). Stacks: split into free slots, the rest as one `q` item (1.7).

### 4.5 SkyyMobs dependency: `mob:fn:levelAt` (exact contract)

Version: the task named SkyyMobs 0.1.2, but 0.1.2 is already the running "level health floor 50 HP" build (RESUME.md, wf_1f9a2b82-87b).
So `levelAt` ships in the next free SkyyMobs version (0.1.3), or rides along 0.1.2 if that round is still open when this one starts.
Below, "SkyyMobs levelAt" means that version.

| | |
|---|---|
| Key | `mob:fn:levelAt` = `java.util.function.Function`, put in setup, removed in shutdown (like `mob:fn:level`, M:3038 / 3049) |
| Argument | `Object[]{ String worldName, Number x, Number y, Number z }` (block coordinates; doubles are floored) |
| Result | `Object[]{ Integer lo, Integer hi, String step, String key }`: the levels a mob spawning on that block can get = `MobLevel.lookupAt(world, x, y, z, Integer.MIN_VALUE)` (M:1980) band + its Bonus, each like `levelFor` (M:1680: a min <= 0 counts as 1, + bonus, capped at `levels.max`), `lo <= hi`; step / key = the lookup's step and row key (for logs and `/gear read`) |
| null | no level there (band 0,0: island worlds, `bands.default` 0, a world row 0,0), part switch off, unknown world, bad arguments, any error |
| Threads | any thread. On that world's own thread (`World.isInThread()`, `TickingThread#isInThread` VERIFIED) the block environment is read (lava caves, env Bonus); from any other thread only the 2D worldgen lookup runs (step gets `-2d`) |
| Guarantees | never throws, never loads a chunk, never writes; uses the existing per-column worldgen cache (`MobLevel.WG`) |
| Later | when SkyyWorldGen stage 2 publishes `wg:fn:ring`, SkyyMobs' lookup reads it as step 3b (W 5.2) and `levelAt` follows with no SkyyGear change |
| Size | one small class (`MobLevelAtFn`) + one `lookupAt` flag to skip `blockEnv` off-thread; a lean round on top of 0.1.2 |
| Without it | 4.2 steps 2-5. Mob drops do not need it (`mob:fn:level` exists since 0.1) |

---

## 5. Old items (no mass conversion)

- 0.2-style unidentified items ("Unidentified Iron Sword": the real id + `id:false`) **keep their item and document**: same tooltip, same
  in-place identify (`GearRoll.identify`, G:5931), now with the identify tree bonuses and Smithing XP.
- **Nothing turns them into mystery items.** They are still touched where 0.2 touches documented gear: `/gear relevel` re-stamps `lvl`
  of every stamped documented item, unidentified ones included (`GearAdmin.relevelInv` G:10738-10776; mystery items are skipped there
  because `gearish` is false for `Skyy_` ids, G:4737-4739), the scan migrates SkyyRolls documents, and the passive scan refreshes
  tooltips. The drop / chest conversions only touch gear with NO document (`GearTag.unid`, `lootable`: `!hasAnyDoc`, G:8191, G:6997).
- **Unopened chests that 0.2 already tagged at fill time keep 0.2-style items** and show real names. The fill-time tag is recorded
  nowhere (`GearChestTag` G:9374-9380 writes no `GearOpened` record; only first-open decisions and admin loot containers are), so 0.2.3
  cannot find those chests later. Skyy's test world has 81 such fill-time tags (gear.log): test step 9 says what to expect.
- Identified gear, crafted gear, SkyyRolls items: unchanged (beyond the 0.2 passes above).
- `part.mystery` off later: no new mystery items; existing ones still show and identify.
- **Rollback floor (main session, `tools/deploy_set.py` note):** SkyyGear below 0.2.3 has no `Skyy_Unid_` item assets, so mystery items in
  inventories, vaults, AH listings and chests become unknown items. Once any exists (`/gear lootstats` counts them), never roll SkyyGear
  below 0.2.3 (or have everyone identify first). Removing SkyyGear has the same effect.

---

## 6. Smithing tree hooks, tree Strength and the reader list (aligned with T2 sections 3, 7, 12 and 16)

T2 decided the interface: the Smithing nodes are SkyyTrees "read" kinds and other mods read them through **`tree:fn:bonus`**
(Object[]{UUID, "Smithing.<Id>"} -> Double fraction = level x per; 0 when off, absent or SkyyTrees is missing - T:3201-3213: unknown ids
answer 0.0, so these reads are safe on the live SkyyTrees 0.2.5 too). The task text said "skill:bonus:<uuid> style"; T2 chose
`tree:fn:bonus` for these nodes (like Cooking, T2 12 "Reading channel"), so SkyyGear reads exactly that. The main-session call
(OPEN-QUESTIONS l.252-253, HANDOFF 2026-10-02 PLAN DONE line, T2 M1) puts these readers AND `gear:extras` in 0.2.3 (if SkyyTrees 0.3's
round comes first, the same readers move into that round's SkyyGear unchanged).

| Node (T2 slot, id) | Per level / max | SkyyGear reads it in | Effect | Safety cap row |
|---|---|---|---|---|
| S1 Fine Craft `Smithing.SRarity` + S10 Fine Craft II `Smithing.SRarity2` | 0.4% / +10% and 0.5% / +10% | `GearRoll.smithChance` (G:5640) used by `craftRarity` (G:5651) | chance = min(Smithing lv x `smith.perLevel`, `smith.cap`) + (SRarity + SRarity2) x 100, the tree part ABOVE `smith.cap` (T2); never above `craft.maxRarity` | `tree.craftMax` 20 |
| S5 Keen Eye `Smithing.SIdent` | 4% / 40% | `GearRoll.identify` (G:5931; the mystery branch too) -> `rollMods` | per modifier: with that chance roll twice, keep the higher; never above the rarity's top value; same stats picked | `tree.twiceMax` 50 |
| S4 Steady Hand `Smithing.SReforge` | 4% / 40% | `GearRoll.reforge` (G:5917; the UUID is passed in from `GearForge.reforge`, G:7215) | the same, on reforge | `tree.twiceMax` 50 |
| S7 Appraiser `Smithing.SAppraise` | 1% / 10% | identify (2.3) | one rarity step, never above Fabled / into Mythic or Set | `tree.idStepMax` 10, `tree.idStepTo` Fabled |
| S12 Masterwork `Smithing.SMaster` | 1% / 5% | identify + reforge | with that chance every modifier rolls its best value (checked before Keen Eye / Steady Hand) | `tree.bestMax` 5 |
| S11 Haggler `Smithing.SHaggle` | 2% / 20% | identify + reforge cost at every call site below (`GearCfg.cost*` stay pure) | cost x (1 - value), rounded half up | `tree.haggleMax` 20 |

- `rollMods(String id, int slot, int r, int lvl)` (G:5708) gets an overload with (twiceChance, best); the old signature = (0, false), so
  every other caller is byte-identical in behaviour. At the T2 defaults Keen Eye and Steady Hand top out at 40%, so `tree.twiceMax` 50
  never binds; it stays as the cap for an admin who raises a node.
- **Haggler call sites (VERIFIED, G; every one must apply the same discount or a page shows a different price than it charges):** the
  tooltip `GearView.lines` unidentified branch G:6234 (has `owner`; + the new mystery branch), the reforge charge `GearForge.reforge`
  G:7226, the reforge page `ReforgePage` G:9892, `GearIdent.costOf` G:10100-10105 (no UUID today -> `costOf(it, u)`), which feeds the
  identify row list and `IdentifyPage.total` G:10270 (x stack quantity), the identify charge `GearIdent.identify` G:10137 and the
  identify page detail G:10343. `costReforge` / `costIdentify` (G:4293, G:4299) stay pure. AE9 checks that the shown cost equals the
  charged cost on every page.
- `part.tree` off, `tree:fn:bonus` absent or answering 0 -> the exact 0.2.2 outcomes for the same random stream (9, AE9).
- **Tree Strength: `gear:extras:<uuid>` (IN this round).** T2 7 / 13: SkyyTrees posts `"str:N"` (source `trees`) into a map
  `gear:extras:<uuid>` = `java.util.concurrent.ConcurrentHashMap` (String source -> String stat text). SkyyGear reads it next to today's
  single-writer string `gear:extra:<uuid>` (owned by SkyyAccessories): `GearStats.extra(u)` (G:6569-6581) joins the `gear:extra` text and
  every String value of the map (in key order, through a `TreeMap` copy; a non-Map or non-String value is ignored) with "," and parses
  the result with the existing `parseExtra` (saturation kept), cached by the joined text (`XCACHE`, 512). The `/gear` line (G:10964)
  becomes "From other mods (gear:extra + trees): Strength +25". `GearStats.totals(..., withExtra)` picks it up unchanged. SkyyGear never
  writes the map.
- **The reader list: `gear:tree:readers` (NEW).** The main-session call says nodes whose reader mod is not live are not buyable and show
  "coming with <mod>" (OPEN-QUESTIONS l.253-254), so SkyyTrees needs to know what SkyyGear reads. SkyyGear publishes `gear:tree:readers`
  = one java.lang.String: the seven ids `Smithing.SRarity`, `Smithing.SRarity2`, `Smithing.SIdent`, `Smithing.SReforge`,
  `Smithing.SAppraise`, `Smithing.SMaster`, `Smithing.SHaggle` plus the token `gear:extras` (the class-tree Strength input), joined with
  "," and no spaces. It is put in setup, removed in shutdown and re-published on every config reload; with `part.tree` off the seven
  Smithing ids are left out (those nodes then show as not live).
  SkyyTrees 0.3 reads it when its page opens (SkyyTrees 0.2.5 ignores it). SkyySkills / SkyySacks can follow the same pattern
  (`skill:tree:readers`, `sack:tree:readers`). Main session: the SkyyTrees 0.3 build must adopt this key name (or this spec follows
  whatever name that build already chose).
- Not here: Smithing Wisdom (`xp.smithing`) and the smelting nodes are SkyySkills / SkyySacks work (T2 12).

---

## 7. Server Setup rows (tools/skyycfg.py kit 1.1; row format G:1824)

New category `loot` "Loot" and `smith` "Smithing tree" (9 categories in 0.2.1 + 0.2.2's `tools` + these 2 = 12 of 16). `xp.*` rows sit
in `costs` next to `xp.reforge`; `odds.levelShift` in `drops` next to `odds`; part switches in `general`. 30 rows (labels <= 40 and helps
<= 100 characters, checked).

| Row | Label (<= 40) | Cat | Type / default / range | Flags | Help (<= 100) |
|---|---|---|---|---|---|
| `part.mystery` | Mystery items for new unidentified gear | general | bool / true | live,part,danger | New unidentified gear shows as "Unidentified Sword" (type, level, rarity). Off = the real item. |
| `part.lootMob` | Extra gear drops from mobs | general | bool / true | live,part,danger | Kills of levelled mobs may drop one extra unidentified piece (Loot page). |
| `part.lootChest` | Extra gear in loot chests | general | bool / true | live,part,danger | Freshly filled world loot chests may get one extra unidentified piece. |
| `part.tree` | Smithing tree bonuses | general | bool / true | live,part,danger | Craft, identify and reforge use the Smithing tree (SkyyTrees 0.3). Off = no tree bonus. |
| `loot.mob.chance` | Extra drop chance per kill | loot | dec / 4 / 0-100 % | live,danger | Chance per kill of a levelled mob (Skyy: 4% = 1 in 25). |
| `loot.mob.capPerHour` | Most extra drops per player an hour | loot | int / 20 / 0-1000 | live,danger | Safety net against farms; 0 = no cap. Staff skip it. |
| `loot.mob.neutral` | Neutral fighters roll too | loot | bool / true | live | Boars, Scaraks and other levelled mobs that only fight back also roll the extra drop. |
| `loot.mob.creative` | Creative kills roll too | loot | bool / false | live,adv | Kills by a player in Creative also roll the extra drop. |
| `loot.chest.chance` | Loot chests with an extra piece | loot | dec / 33 / 0-100 % | live,danger | Chance a freshly filled world loot chest gets one extra piece (Skyy: about 1 in 3). |
| `loot.chest.islands` | Extra pieces on island worlds | loot | bool / false | live,adv | Loot chests filled on SkyyIslands island worlds also roll. |
| `loot.armorShare` | Armor share of extra drops | loot | dec / 50 / 0-100 % | live,danger | Share of extra drops that are armor, at every level. The rest are weapons. |
| `loot.weights` | Extra drop type weights | loot | table dec;none;Weight / 18 entries, all 1 / 0-1000 | live,danger | Weight of each type inside its group (weapons or armor slots). 0 = never. |
| `loot.classLean` | Class weapons in extra mob drops | loot | dec / 50 / 0-100 % (PROPOSED, question 1) | live,danger | Share of extra weapon drops that are a type your class uses (question 1). |
| `loot.levelFrom` | Level of found vanilla gear | loot | choice mob (PROPOSED, question 2) / (mob "Mob or zone level", band "Band start") | live | Gear mobs and chests already drop: the mob or zone level in its band, or the band start (0.2). |
| `loot.levelTop` | Highest level of found gear | loot | int / 49 / 1-100 | live,danger | Found gear never goes above this (49 = the top vanilla band until our own Lv 50+ gear). |
| `loot.aboveYou` | Found gear above your skill (0 = off) | loot | int / 0 / 0-100 | live,danger | Mob drops and first-open finds stay at most N above your gate skill (band start wins). 0 = off. |
| `loot.zone` | Chest level by drop list zone | loot | table int;none;Min\|Cap / Zone1 1\|20, Zone2 20\|30, Zone3 30\|45, Zone4 45\|60 / 1-100 | live | Used when no mod can tell the level at a chest (LOCKED zone bands). |
| `loot.level.world` | Found gear level by world | loot | table int;none;Min\|Cap / empty / 1-100 | live | A level band for a named world (hand-built islands, dungeons). Used after SkyyMobs / World Gen. |
| `loot.exclude` | Items extra drops never pick | loot | text / "" / 0-2000 | live,adv | Comma list of item ids or Prefix* (checked against the item list). |
| `loot.include` | Extra items extra drops may pick | loot | text / "" / 0-2000 | live,adv | Comma list of other mods' gear ids; the type comes from the id or armor slot. |
| `odds.levelShift` | Better rarity per mob level | drops | dec / 0.02 / 0-1 | live,danger | Mob-dropped gear: rarity weights above Normal x (1 + this x (mob level - 1)). |
| `xp.identify` | Smithing XP per identify | costs | table int;none;XP / 250 500 1000 2000 4000 8000, Set 2000 / 0-100000 | live,danger | Smithing XP per identified item, by rarity (Skyy: x10). SkyySkills caps apply. |
| `xp.craft` | Smithing XP per crafted gear | costs | table int;none;XP / 500 1000 2000 4000 8000 16000, Set 4000 / 0-100000 | live,danger | Smithing XP per crafted weapon or armor piece, by rarity. Tools pay on reforge. |
| `xp.craft.exclude` | Gear that pays no craft XP | costs | text / "*_Crude,*_Wood" (PROPOSED, question 6) / 0-2000 | live,adv | Comma list of item ids, Prefix* or *Suffix: crafting these pays no Smithing XP. |
| `tree.craftMax` | Most tree craft rarity bonus | smith | dec / 20 / 0-100 % | live,danger | Fine Craft I + II never add more than this to the craft step chance. |
| `tree.twiceMax` | Most roll-twice chance | smith | dec / 50 / 0-100 % | live,danger | Keen Eye / Steady Hand: the per-modifier roll-twice chance never goes above this. |
| `tree.bestMax` | Most Masterwork chance | smith | dec / 5 / 0-100 % | live,danger | Masterwork (every modifier at its best) never goes above this. |
| `tree.idStepMax` | Most identify step-up chance | smith | dec / 10 / 0-100 % | live,danger | Appraiser's chance to raise the rarity on identify never goes above this. |
| `tree.idStepTo` | Best rarity from a step-up | smith | choice fabled / unique..mythic | live,danger | An identify step-up never goes above this (Skill-Trees-2: Fabled). Never Set. |
| `tree.haggleMax` | Most Haggler discount | smith | dec / 20 / 0-90 % | live,danger | Haggler never cuts identify / reforge costs by more than this. |

- PROPOSED rows ship with the bracketed default only if Skyy has not answered by build time (project rule: an open question keeps its
  current default, OPEN-QUESTIONS header); the main session asks first.
- Existing rows used unchanged: `odds` (Mob / Chest columns), `cost.identify`, `cost.reforge`, `xp.reforge`, `smith.perLevel`,
  `smith.cap`, `craft.maxRarity`, `level.material`, `identify.command`, `part.drops`, `part.chests`.
- Not carried: `loot.mobSpread` (GL 9; retired, 1.7).
- **Check hooks:** `GearCfg.checkWeights` (entry = one of the 18 type keys, weight >= 0, at least one > 0 in each group),
  `GearCfg.checkZone` (`Zone<N>`, Min <= Cap), `GearCfg.checkWorld` (a world name without spaces, Min <= Cap), `GearCfg.checkIds` (ids
  exist / Prefix* matches; never a `Skyy_Unid_` id), `GearCfg.checkPatterns` (`xp.craft.exclude`: id, Prefix* or *Suffix, at least 3
  characters besides the star).
- **One-time update `GearCfg.migrate023`** (the migrate013 / 02 / 021 / 022 pattern): History snapshot first ("before the 0.2.3 loot
  rows"), add-only (the new rows' lines under a `SkyyGear 0.2.3 loot rows` marker; `xp.identify.*` / `xp.craft.*` / `xp.craft.exclude`
  after the last `xp.` line, `odds.levelShift` after the last `odds.` line), defaults (no change-log line), the kit's atomic write
  keeping bytes and CR, runs once; a fresh file carries it.
- Danger set additions: every row marked danger above. `unid.key` is never a kit file.

---

## 8. Bridges

| Key | Direction | Change |
|---|---|---|
| `gear:fn:describe` / `rollsLine` / `rarity` / `level` / `identified` / `sig` (G:11101) | SkyyGear publishes; SkyyAuctions reads | Accept mystery stacks (ItemStack or Object[]{id, metadata}). describe = ["Unidentified Sword", "Lv 12 - Requires <class skill> 12" (owner-neutral form), "Rarity: Rare", "Unidentified - identify it to find out which sword it is.", "Holds 3" if q > 1]; rollsLine = "Unidentified (Rare, Lv 12)" (today's format, G:6435); rarity = `r`; level = `lvl`; identified = false; sig = hash(type, lvl, r, q) - **never `x`**, so two mystery items that look the same never show "rolls differ" and the AH never leaks a difference. No string ever contains the real id or material |
| `gear:fn:unid` (mode 9) | published | May now return a stack with another item id (a mystery item); takes an optional world + x, y, z for the 4.2 chain (GL 8). No caller today |
| `gear:fn:mystery` NEW (mode 10) | published | ItemStack or Object[]{id, metadata} -> String[]{typeKey, "weapon"\|"armor", name, level, rarity id}, null = not a mystery item |
| `gear:mystery:ids` NEW | published | "Skyy_Unid_Weapon_Sword,...,Skyy_Unid_Armor_Legs" (18 ids) for other mods |
| `gear:tree:readers` NEW | published (setup, reload; removed in shutdown) | the node ids SkyyGear reads + `gear:extras` (section 6); SkyyTrees 0.3 shows only these nodes as buyable |
| `gear:extras:<uuid>` NEW | SkyyTrees 0.3 writes; SkyyGear reads | ConcurrentHashMap source -> "str:N,..."; merged with `gear:extra:<uuid>` in `GearStats.extra` (section 6) |
| `gear:loot:add:<Mod>` NEW | other mods publish; SkyyGear reads | comma list of a mod's own gear ids the extra drops may pick (SkyyArmory's metal wands: `gear:loot:add:SkyyArmory`) |
| `mob:fn:level` | SkyyGear reads (SkyyMobs 0.1+) | M:2335-2351 (also the level shift, 1.7) |
| `mob:fn:levelAt` NEW | SkyyGear reads (SkyyMobs 0.1.3, 4.5) | 4.5 |
| `wg:fn:ring` | SkyyGear reads when SkyyMobs is missing (SkyyWorldGen stage 2) | W 5.1 |
| `class:<uuid>`, `class:weapons:<Class>`, `class:list` | SkyyGear reads (SkyyClasses) | C:1639, C:4412, C:4411 (class lean, playable classes only) |
| `tree:fn:bonus` | SkyyGear reads (SkyyTrees 0.3) | section 6 node ids |
| `skill:fn:addxp` | SkyyGear calls (SkyySkills) | + sources `gear:identify`, `gear:craft` (existing `gear:reforge`) |
| `coins:fn:take` / `add`, `profile:busy:<uuid>`, `skill:fn:level` | existing | unchanged (`skill:fn:level` also feeds `loot.aboveYou`) |

**Dependencies:**
- **SkyyMobs 0.1.3** (`mob:fn:levelAt`, 4.5; 0.1.2 is the running health-floor build). Optional for SkyyGear (fallbacks 4.2). Can be
  built before or with 0.2.3.
- **SkyyAuctions 0.1.3** (small, recommended in the same round): `AhItem.category` (A:1656-1670) returns WEAPONS / ARMOR for
  `Skyy_Unid_Weapon_*` / `Skyy_Unid_Armor_*` (today they have no Weapon / Armor block, so they list under Tools & Misc). Names, levels,
  rarity filter, search ("unidentified", "sword") already work through the gear bridges (A:1747-1781, A:1870-1876).
- **SkyyTrees 0.3** publishes the Smithing nodes (T2) and writes `gear:extras:<uuid>`; it must read `gear:tree:readers` to decide which
  nodes are buyable (main-session call). Nothing else is needed from SkyyGear's side.
- **SkyySkills:** none required (Smithing is grantable today). T2's next SkyySkills adds Smithing to `addxpSkills` so Wisdom boosts
  these grants.
- **SkyyArmory** (AR exists, 0.1 not built): its wands are `Weapon_Wand_Copper` ... `Weapon_Wand_Onyxium` with no "skyy" in the id (AR
  1.1), so `isGear` takes them and their type is `Weapon_Wand`; bands from the metal words (Copper 10-18 ... Mithril / Onyxium 40-49).
  They become candidates either at build time (if a SkyyArmory jar is in the SET when 0.2.3 is built, its item JSONs join the 1.1 scan
  like More Crossbow Tiers) or at runtime through `gear:loot:add:SkyyArmory`, which AR does not publish yet (main session: one line in
  its setup). Either closes the Priest wand gap (1.1) for Lv 10-49.
- **SkyyWorldGen:** `wg:fn:ring` is stage 2 (0.1 publishes no keys). W 5.4's draft `loot.level.world.skywynn_zN` rows use the
  pre-lock bands (1-10 / 15-25 / 30-40 / 45-60 vs the LOCKED 1-20 / 20-30 / 30-45 / 45-60); SkyyGear ships the row empty (main session:
  fix W 5.4).
- Main session: SkyyMenu `MODS_VERSIONS` bump, `tools/deploy_set.py` pin + the rollback floor (5), HANDOFF / TEST-CHECKLIST.

---

## 9. Tests

**Bare-JVM harness `SkyyGear/test_skyygear_0.2.3.py`:** every earlier section carried forward + new section **AE**. (0.2.1 uses AC; the
0.2.2 harness should be AD, but `research/Tool-Levels-Spec.md` section 9 also names its section AC - main session: rename it AD. AE is
free either way.) The 2026-10-02 lesson: the harness must RUN the code paths. Engine stand-ins follow SkyySkills 0.4.13 section E
(javassist subclasses of Store / CommandBuffer / ArchetypeChunk made with `Unsafe.allocateInstance`, answering only what the code asks);
other SET jars load read-only on the classpath like 0.2.1's SkyyMobs jar.

| # | What it executes |
|---|---|
| AE1 assets | The 18 item JSONs decode through the engine's Item codec (no unknown key; if the bare JVM's empty asset maps make the codec refuse a reference, a key check against vanilla item JSON keys + `Variant` instead, said so in the report); MaxStack 1; no Weapon / Armor / Tool / Utility / Interactions / Recipe; Variant; quality; every referenced vanilla model exists; `PlayerAnimationsId` = the representative's resolved value (`Bow` for the Shortbow, `Throwing_Knife` for the Kunai, `Item` for armor); `DroppedItemAnimation` / `ItemSoundSetId` present exactly when the representative resolves one (none for Crossbow_Iron, Kunai and armor; no sound set for the Kunai); each PNG decodes (`SA.png_decode`), has the source size, hue-free (spread <= 24), the icon has the ? pixels, every icon pixel has r, g, b <= alpha; a second build gives the same bytes; no path collision with AZ / SET jars; lang lines. With the decoded items: the REAL `ArmorSlotAddFilter.test` and the Utility filter refuse every mystery item; the REAL `SackDefs.homeOf` / `catOf` from the pinned SkyySacks jar return null for all 18 ids. |
| AE2 picker | Type map: every candidate in exactly one type (= an independent Python rule); the coverage table of 1.1 reproduced; for every type x level 1-60: only ids whose band holds min(L, 49), never a dropped id; 20,000 picks per level: armor share 50% +- 1% at EVERY level, types spread evenly inside each group (loose chi-square); class lean share within 1%, and no lean for a class missing from `class:list` (an admin-set Assassin); `loot.aboveYou` caps `L'` at skill + N; the level-shift weights at L = 1 / 30 / 60 equal the formula; a type with no candidate at L is never picked; `gear:loot:add:*` and `loot.include` / `exclude` obeyed (an id of an unknown type ignored with one WARN). |
| AE3 seal | Round trip for all 308 ids x levels, every blob the same length (plus a 63-byte and a 70-byte stand-in id: the long one pads to 128 and logs once); a tampered blob, a wrong key, a changed `lvl` / `r` / `q` (AAD), an item without `x` -> open fails -> re-pick of the same type and level, logged; re-pick only among MaxStack >= `q` (a `q` 5 spellbook at Lv 30-37 never becomes `Weapon_Spellbook_Fire`, MaxStack 1), none = refused before any coin moves; key created once, read back after a "restart", an unreadable key file never overwritten (items then carry no `x`). |
| AE4 real death path | Stand-in chunk with a REAL DeathComponent (REAL `Damage` with `EntitySource` of a player ref / `ProjectileSource` / an NPC source / an environment cause), a Role stand-in, a REAL `DeferredCorpseRemoval`. Per tick, in dependency order: `TickCorpseRemoval`, `GearDeathMark.tick`, the REAL `NPCDamageSystems$DropDeathItems.tick`, `CorpseRemoval`. With chance 100: the CommandBuffer records exactly one extra holder from the REAL `ItemComponent.generateItemDrops`, holding a mystery stack at position + (0,1,0), once per death over 40 ticks, for: an instant drop, a corpse timer (drops on the 0-crossing tick), no `DeferredCorpseRemoval` (drops at once, removed the same tick), a `NotFinished` interaction chain with a timer (no countdown, no drop, no roll until it finishes) and without one (drops at once, removal waits). No roll for: level -1, NPC / environment / pet killer, a killer ref that is no longer valid or sits in another store, Creative (switch off), cap reached (staff not capped), `part.lootMob` off, chance 0, neutral with `loot.mob.neutral` off. **Order:** the REAL `DependencyGraph` built over TickCorpseRemoval, DropDeathItems, CorpseRemoval and GearDeathMark in both registration orders places GearDeathMark after TickCorpseRemoval and before DropDeathItems (if the graph cannot be built in the bare JVM: a bytecode check of both dependencies, said so in the report); a forced wrong order (GearDeathMark before TickCorpseRemoval, without the AFTER edge) shows the missed roll the hardening prevents; the unordered fallback logs its WARN and `/gear lootstats` shows it. **Rate:** 1,000,000 rolls of the pure roll at chance 4 -> 4.00% +- 0.08 (4 sigma). The vanilla holders DropDeathItems produced then run through the REAL `GearDropSys.onEntityAdded` -> mystery items at the mark's mob level clamped into each band, rarity with the level shift; a 3-spear stack -> 3 drop entities, 3 mystery items, each its own rarity and seal; a modded type-less id keeps the 0.2-style document; an oversized stack is not converted. |
| AE5 real stash fill | `GearChestMark.onEntityAdded` -> the REAL `StashPlugin.stash(info, icb, true)` (stand-in BlockStateInfo / section; the `ItemModule.get()` singleton stood in so `getRandomItemDrops` returns `Zone1_Encounters_Tier3`'s items parsed from AZ, and a `Zone1_Kweebec_Tier3` roll whose Leaf spear stack (2-5 in that list) is 3) -> `GearChestTag.onEntityAdded`: every vanilla gear stack is now mystery items at the zone level (a stand-in `mob:fn:levelAt`; without it a stand-in `wg:fn:ring`, then a `loot.level.world` row, then the `Zone1` row; none = band start); the spear stack split into free slots, one mystery item each, and in a nearly full chest the rest as one `q` item; with chance 100 one extra in an empty slot; a full chest gets none (counted); an island world none; the drop list is cleared, so a second add (LOAD) changes nothing; a stand-in list that rolls empty keeps the drop list and makes no extra; `clear` off -> one extra per refill that added items; a `CHEST` map clear is counted; the carried-forward `decide` cases run unchanged on the old signature; item counts before / after. |
| AE6 identify swap | A REAL Inventory with EVERY slot full and the mystery item in the hotbar / storage / backpack in turn: `GearIdent.identify` -> that slot holds the real item (sealed id, shown level, rarity or one step, `q` units), every other slot byte-identical, item count unchanged, coins taken once (coins stand-in), Smithing XP granted once (a recording `skill:fn:addxp`, `xp.identify` x `q`); the `q` fallback path for a spear (q 3) and a spellbook (q 5): one real stack of `q`, cost x `q`; refusals (not enough coins, profile busy, moved item) take nothing; a container stand-in that refuses the write -> refund + the mystery item stays; Identify all over old + mystery items; `/gear identify` = no coins, no XP, no step. Scan idempotency: a second `GearStamp.scan` over an inventory full of mystery items writes 0 stacks and `GearStamp.paused` never trips. |
| AE7 no dupe | identify twice with the same fingerprint -> the second refused, coins once, one real item; two page clicks 100 ms apart -> one identify; "relog": the inventory saved through the REAL `ItemStack.CODEC` / BSON before and after the swap holds exactly one of {mystery, real}, never both, never none; an AH-style snapshot (CODEC + JSON round trip) restores the same sealed blob; drop + pick up keeps the document. |
| AE8 AH display | All gear bridges on a mystery stack AND its CODEC copy: type, level, rarity present; no returned string contains any of the 308 real ids or their en-US names, except that the type word itself may equal a name (the only Kunai's en-US name is "Kunai": the check skips a name equal to the mystery item's own type word); equal sig for two mystery items with the same visible data and different sealed ids; the REAL SkyyAuctions 0.1.2 `AhItem.gearName` / `gearSummary` / `tierName` / `searchExtra` / `category` from its pinned jar: "Unidentified Sword", "Unidentified (Rare, Lv 12)", "Rare", "rare unidentified", MISC (0.1.3: WEAPONS / ARMOR). |
| AE9 tree read + XP | A stand-in `tree:fn:bonus`: smithChance = level part + tree part (above `smith.cap`, capped by `tree.craftMax`), never above `craft.maxRarity`; Keen Eye / Steady Hand: 20,000 rolls, mean higher than single rolls, never above the top value, same stats picked; Masterwork = every value at its top; Appraiser rate, never above Fabled, never into Mythic / Set, Set never steps; Haggler: the shown cost equals the charged cost at every call site of section 6 (tooltip, reforge page, identify rows, `IdentifyPage.total`, identify detail, both charges); craft XP: a crafted weapon / armor piece pays the table, a crafted tool pays 0, ids matching `xp.craft.exclude` (`*_Crude`, `Prefix*`, an exact id) pay 0; no function / `part.tree` off -> identical outcomes to 0.2.2 for the same seeded RNG stream. |
| AE10 config | New rows: label / help lengths, units, the danger list, defaults, check hooks; `migrate023` on a scratch COPY of the live `config.properties` (read-only original): History, marker, add-only, CRLF, twice = once, a fresh file equals; the kit export never contains `unid.key`. |
| AE11 wiring | Bytecode: GearDeathMark deps = BEFORE DropDeathItems + AFTER TickCorpseRemoval; `mobRoll` only from GearDeathMark.tick; the chest extra only from GearChestTag; the swap only from GearIdent.identify; `isGear` / `gearish` false for all 18 ids even with `gear.include=Skyy_Unid_`; `gear:tree:readers` published in setup with the 7 Smithing ids + `gear:extras`, removed in shutdown, re-published on reload, without the Smithing ids while `part.tree` is off; new admin sub-commands carry `requirePermission("skyygear.admin")` + `setPermissionGroups(new String[0])` (lint perm_group_leaks); class byte-compare 0.2.2 -> 0.2.3 lists every difference + the new non-class entries (18 JSON, 36 PNG, lang). |
| AE12 extras | A stand-in bridge: `gear:extra` "str:5" alone = 5; `gear:extras` {trees: "str:25"} alone = 25; both = 30; a non-Map, a non-String value or a bad part is ignored; saturation still holds; the cache stays at most 512; `/gear` prints the merged line; `GearStats.totals(..., true)` includes it. |

**Cross-check (full round):** all SET jars in one JVM with `-Xverify:all`, the engine-access audit (protected members only from a
subclass on `this` - the UiProbe 0.3.1 lesson), the Adventurer permission audit, `python tools/ci/lint.py` 0 fails.

**New admin commands for testing:** `/gear mystery <type> [level] [rarity] [player]` (a sealed random candidate),
`/gear mystery reveal` (the held item's real id), `/gear lootstats` (rolls, hits, cap hits, chest fills, fills with gear, chest extras,
no-room skips, CHEST-map clears, conversions, splits, step-ups, mystery items made, death order normal / fallback). `/gear give <item>
--unid true` now gives a mystery item. `/gear clear` refuses on a mystery item.

**In game (numbered, for TEST-CHECKLIST):**
1. `/gear mystery Sword 12 rare`: an "Unidentified Sword" with a grey sword icon and a ?, Rare frame. Tooltip: "Lv 12 - Requires <your
   class skill> 12", "Rarity: Rare", the unidentified line, "Identify: /identify - 490 coins".
2. Hold it (a dark grey sword), swing (a punch, no sword attack), drop it (the plain white glow every mystery item has - the frame and
   name colour show the rarity, not the glow), pick it up.
3. `/gear mystery Chestplate 5`: try to wear it and to put it in the off-hand -> refused.
4. `/identify`: listed with its icon, level and cost. Identify -> "It was a ... Sword!", the modifiers, coins taken, a Smithing XP line
   (a Rare pays 1,000 XP).
5. Fill every inventory slot, keep one mystery item, identify -> works, nothing drops.
6. Double-click Identify fast -> one identify, coins taken once.
7. Kill about 50 levelled mobs -> about 2 extra drops; each drop's level = that mob's plate level; `/gear lootstats` agrees.
8. Let a mob burn or fall to death, or let a pet kill it -> no extra drop.
9. Walk into land you have never explored, open loot chests -> about 1 in 3 has an extra "Unidentified ..." piece; its level fits the area
   (`/mobs info`). Vanilla gear in those chests and from mob drops is a mystery item too. **Expected:** chests the game filled BEFORE
   this update (your world's gear.log has 81 such fill-time tags) still hold old-style "Unidentified Iron Sword" items - they identify
   as before and cannot be converted later.
10. An old "Unidentified Iron Sword" you already had -> unchanged, identifies as before.
11. Vault it, `/trade` it to a friend, list it on the AH -> "Unidentified Sword", "Unidentified (Rare, Lv 12)"; buy it back.
12. Carry Magic Bags -> they never take it.
13. Server Setup -> Gear -> Loot: chance 100% -> every levelled kill drops one; set it back.
14. Kill Trork Guards until one drops spears (15% of kills): 2-4 separate "Unidentified Spear" items, each with its own rarity.
15. Craft a Copper Sword -> a Smithing XP line (500 or more); craft a Crude Sword -> no Smithing XP (if question 6 = yes); craft a
    pickaxe -> no craft XP (reforging it pays).
16. After SkyyTrees 0.3: the Smithing nodes can be bought (not "coming with SkyyGear"); Appraiser / Keen Eye / Fine Craft levels change
    identify and craft results (T2 first checks 4-5, 14); a class Strength node shows in `/gear` under "From other mods" (T2 check 9).

---

## 10. Risks

1. **Economy.** About 5 extra mob items an hour at 120 kills (3.6) plus about 15 extra chest pieces created per exploring hour (up to
   65 in a fast burst; a player opens only part of them). Identify costs 1,250-1,830 coins an hour for the mob items at Lv 10-20, plus
   about 3,000-4,400 per 10 chest pieces looted; many will go to the AH unidentified (price flood). Every rate is a row; the hourly cap
   (20) stops machine farms. Watch `/gear lootstats`, AH prices and coin income in the first playtest; `loot.chest.chance` is the lever.
2. **Dupes.** Every swap is one in-place `setItemStackForSlot` on the world thread after a fingerprint check (2.1); coins go first and
   are refunded on failure; the chest extra is added once per real fill (4.1); the mob extra once per death (role flag + UUID map);
   split units are placed before the original slot is rewritten and counted before / after. A crash between SkyyCoins' save and the
   player save can lose one payment or one identify, never create an item (the existing identify / reforge window, unchanged).
3. **Client display of a custom item (UNVERIFIED until Skyy sees it):** the icon path, the recoloured texture on the vanilla model (a
   texture from a PLUGIN jar is unproven - only pack zips and plugin-jar icons are, 1.2), the held pose (`MYSTERY_ANIM`), the tooltip on
   a custom id. In-game steps 1-3 check it first; the art contact sheet goes to Skyy before the build.
4. **Rollback / uninstall** turns mystery items into unknown items (5). Floor note in `deploy_set.py`.
5. **Key loss** (data folder deleted): items still identify, the real item is re-picked (same type, level, rarity; MaxStack >= `q`).
6. **The GearDeathMark hardening** (3.4) most likely changes nothing (the order is very likely right today); if the order was ever
   wrong, more vanilla mob drops get tagged than before. Wanted either way.
7. **Zone lookup at fill time** may miss the lava-cave rule (4.2); without SkyyMobs the ring / world / drop-list rows apply; without
   any, no extra.
8. **Priest gap:** no vanilla wand above Lv 22 and no spellbook above Lv 42 (or at 28-29): Priests get fewer class drops until
   SkyyArmory's metal wands are candidates (8).
9. **AH lowest BIN** groups all levels and rarities of one mystery type (one item id), as it already does for rarities of real gear.
10. **Modded clients** see only what the tooltip shows (type, level, rarity) and an opaque, fixed-length sealed blob. **Guessing** still
    works from type + exact level: right about 4 times in 10 (1.1, question 5).
11. **Smithing pace:** cheap recipes would buy the tree (530 Crude Swords = Smithing 20) unless `xp.craft.exclude` keeps them out
    (question 6).
12. **Old fill-time tags:** chests filled under 0.2 keep 0.2-style items forever (5); harmless, but Skyy may see both styles for a while.
13. **Parallel versions:** 0.2.1 / 0.2.2 move code; every hook here is named by class / function; the builder starts from the FINISHED
    0.2.2 script and re-checks each G line it touches.
14. **Performance:** one map lookup + one bridge call per levelled death; one `levelAt` per chest fill; a few extra entities for a split
    spear stack; nothing periodic is added.

---

## 11. Stages (one full round, built in parts like 0.1's PART A / PART B)

| Part | Content | Size |
|---|---|---|
| 0 - art + proofs | `tools/skyyart.py` additions (`GREY_RAMP`, `glyph_q`, `shadow_art`, proven in `SA.verify()`), the 18 icons / textures + contact sheet for Skyy; Item codec decode of the 18 JSONs; no game needed | S |
| A - mystery items | Assets, `GearMystery` (types, candidates, seal / open with the 64-byte padding, key, make, tooltip), the conversion paths with the per-unit split + `q` fallback (1.7), identify swap + page + Identify all + `/gear identify`, bridges (8), admin commands, `NEVER_GEAR`, the idempotent passive-scan refresh | L |
| B - extra drops | `GearLoot` (mob roll in GearDeathMark + the AFTER TickCorpseRemoval hardening + fallback WARN, kill rules with the killer-ref guard, cap, group-then-type picker, class lean for playable classes, level shift, `loot.aboveYou`; chest extra in GearChestTag with the exact fill condition; zone chain levelAt -> ring -> world row -> drop-list zone), mark levels for GearDropSys, `/gear lootstats` counters | M |
| C - Smithing + extras | tree readers (section 6), Haggler at every call site, Smithing XP on identify + gear crafts (`xp.craft.exclude`), `gear:extras` merge, `gear:tree:readers` | S |
| Config | the 30 rows, check hooks, `migrate023` | S |
| Others | SkyyMobs 0.1.3 `mob:fn:levelAt` (lean, can go first); SkyyAuctions 0.1.3 category (lean, same deploy); SkyyMenu `MODS_VERSIONS`; outside this round: SkyyTrees 0.3 reads `gear:tree:readers` and writes `gear:extras`, SkyyArmory publishes `gear:loot:add:SkyyArmory` | S each |

Round size: **full round** (PROJECT-RULES 4: items that could be lost or duplicated, coins, saved data, several mods). Order: SkyyMobs
0.1.3 (optional) -> SkyyGear 0.2.3 (parts 0-C + config) -> review -> fix -> cross-check with SkyyAuctions 0.1.3 (and SkyyMobs 0.1.3) ->
pin -> commit -> deploy.

---

## 12. Questions for Skyy (each has a recommended default)

1. **Class lean:** should the extra weapon drops lean toward your class? **[Yes: half of the extra weapon drops are a type your class
   uses (Archer: bows / crossbows ...); the rest any type, so the AH and your friends still get theirs. Armor is always any slot.
   Classes that are not playable yet (Assassin, Shaman) get no lean.]**
2. **Levels of gear the game already drops:** should those mystery items also get the mob's / zone's level (like the extra drops),
   instead of the lowest level of their material? **[Yes, the mob / zone level - one rule for every drop.]**
3. **Look:** a dark grey "shadow" of the weapon or armor type with a **?** on the icon (contact sheet before the build)? **[Yes.]**
4. **Chests:** the extra piece only in loot chests the game fills from now on (new land), or also in old unopened chests when you first
   open them? **[New chests only: exactly once per chest and no guessing which old chests were loot chests; their untagged vanilla gear
   still becomes mystery items.]**
5. **Exact level or a range?** With the exact level shown, a player can often tell which item it is (about 3 possible items per type and
   level, sometimes 1: a Lv 30 mace is always Cobalt; a guess is right about 4 times in 10). Wynncraft shows a level range instead
   ("Lv 26-30"), and the real level appears on identify. **[Keep the exact level, as written: you see whether you can use it and what
   it is worth. If you pick the range, the exact level is sealed like the item and the tooltip, the AH and the sort use 5-level steps -
   a small change, no new question.]**
6. **Smithing XP for Crude and Wood gear:** these are made from sticks, fibre, rubble, rock and logs (the Crude Sword is a 0-second
   pocket craft), so at your x10 numbers 530 Crude Swords would buy Smithing 20. **[No craft XP for Crude and Wood gear (Server Setup
   row "Gear that pays no craft XP" = *_Crude,*_Wood); metal, cloth and leather gear pays the full table; tools pay when reforged.]**

---

## Appendix A. Hook map by class / function (builder checklist)

| Where | Change |
|---|---|
| build: `MYSTERY` table, candidate table, art (SA), item JSON (resolved PlayerAnimationsId, absent keys omitted), lang, checks (1.1-1.3) | new |
| `tools/skyyart.py` | `GREY_RAMP`, `glyph_q`, `shadow_art` + `SA.verify()` coverage (main session names the file in the build task) |
| `GearDefs` | type keys / ids / names / kinds, candidate arrays, class prefix fallback |
| `GearMystery` (new) | `is`, `typeOf(itemId)`, `typeFor(realId)`, `pick(type, L, q)`, `make(realId, r, lvl, q, src, ex)`, `seal` / `open` (64-byte padding), `loadKey`, `lines`, `describe`, `sig`, `convert(stack, col, L)` + the per-unit split |
| `GearLoot` (new) | `mobRoll`, `chestExtra`, `zoneLevel(world, x, y, z, dropList)` (levelAt -> ring -> world row -> drop-list zone), `classTypes(u)` (playable classes), hourly cap, rolled-UUID map, counters |
| `GearDeathMark` ctor + `tick` (G:8699-8734) | AFTER `DeathSystems$TickCorpseRemoval` (hardening); mark with level; `GearLoot.mobRoll` (killer ref valid + same store) |
| plugin setup (G:9516-9523) | the unordered `GearDeathMarkU` fallback: WARN + lootstats flag |
| `GearTag.mark` / `near` / `unid` / `tagContainer` / `chestMark` (G:8159-8227) | level in marks; mystery conversion with the split and `q` fallback; count `CHEST` clears |
| `GearDropSys.onEntityAdded` (G:8744) | mystery conversion at the mark's level; one spawned drop entity per further unit |
| `GearChestMark` / `GearChestTag` bodies (G:9363-9380) | item count before the stash; zone level, conversion, `GearLoot.chestExtra` only when the drop list was cleared (or a refill added items with `clear` off), island check |
| `GearChestOpen.process` / `decide` / `lootStack` / `lootSlot` (G:9183, 9097, 7003) | zone level computed in `process`, passed into a new `decide` overload (old signature delegates with "none"); loot window remembers the container position |
| `GearIdent.rows` / `costOf` / `refuse` / `identify` / `allIn` (G:10082-10230) | mystery branch (2.1-2.2), `costOf(it, u)` with `q` + Haggler, XP, Appraiser, re-pick MaxStack >= `q` |
| `IdentifyPage` (`total` G:10270, detail G:10343) | rows, reveal text (2.5), Haggler-consistent costs |
| `GearView.lines` (G:6222-6240) | mystery branch; Haggler on the identify line (G:6234) |
| `ReforgePage` (G:9892), `GearForge.reforge` (G:7215, 7226) | Haggler; pass the UUID into `GearRoll.reforge` |
| `GearRoll.smithChance` / `craftRarity` / `rollMods` / `identify` / `reforge` / `pickRarity` (G:5640-5945) | tree readers (6); level-shift overload for mob-sourced rarity |
| `GearCraftTask.rollIn` (G:7455), `GearFn` mode 8 | Smithing XP on gear crafts only, `xp.craft.exclude` |
| `GearFn` (G:7273) | modes 0-5 + 9 mystery branch (mode 9 optional position); mode 10 `gear:fn:mystery`; `gear:mystery:ids`; read `gear:loot:add:*` |
| `GearStats.extra` (G:6569-6581), `GearAdmin.me` (G:10964) | `gear:extras:<uuid>` merge + the "From other mods" line |
| `GearStamp.scan` | idempotent mystery tooltip refresh; a mystery item without a document gets one (lowest band start, Normal, src admin) |
| `GearAdmin` / `GearCmd` | `/gear mystery`, `mystery reveal`, `lootstats`; `give --unid`; `clear` refuses; `level` / `rarity` on a mystery item re-seal `x` (its AAD holds them); `read` shows type, level source, rarity, `q` and the real id; `relevel` unchanged (skips mystery items) |
| `GearData.NEVER` (G:727) | + `Skyy_Unid_` |
| `GearCfg` | rows, loaders, `checkWeights` / `checkZone` / `checkWorld` / `checkIds` / `checkPatterns`, `migrate023`, re-publish `gear:tree:readers` on reload |
| `SkyyGearPlugin.setup` / shutdown (G:11103-11136) | `GearMystery.loadKey` after `GearCfg.load`; new bridges incl. `gear:tree:readers` (removed in shutdown); ready line adds the loot status |

## Appendix B. Proofs index (read-only, 2026-10-02)

- HS (javassist instruction print in scratch): `ItemStack#toPacket`, `ItemStack#isStackableWith`, `ItemDisplayMetadata` fields,
  `ArmorSlotAddFilter#test`, `ItemContainerUtil#trySetArmorFilters` / `trySetSlotFilters` (callers), `InventoryComponent$Utility`
  filter lambda, `Item#processConfig` (unarmed interaction merge; quality -> `itemEntityConfig`, offsets 410-464), protocol `ItemBase`
  (`itemEntity`), `ItemQuality` (no entity config), `ItemWithAllMetadata` (`quality`, `metadata`), `ItemEntityConfig`,
  `NPCDamageSystems$DropDeathItems#tick` + `<clinit>`, `DeferredCorpseRemoval#shouldRemove`, `DeathSystems$TickCorpseRemoval#tick`,
  `DeathSystems$CorpseRemoval#tick`, `DependencyGraph#sort` / `addEdge` / `resolveEdges` / `hasEdgeOfLaterPriority`, `Edge#compareTo`,
  `SystemDependency` constructors + `resolveGraphEdge`, `OrderPriority` values (NORMAL = 0), `ItemComponent#generateItemDrop(s)`,
  `ItemComponent#setItemStack`, `StashPlugin$StashSystem#onEntityAdded`, `StashPlugin#stash` (clear condition, offsets 325-360),
  `MultipleItemDropContainer` / `ChoiceItemDropContainer#populateDrops` + defaults (weight 100, count 1), `DeathComponent#getDeathInfo`,
  `Damage$EntitySource#getRef`, `Damage$ProjectileSource`, `ChunkStore#getChunkComponent` / `getChunkReference`,
  `TickingThread#isInThread`.
- AZ: gear ids, families, armor slots, qualities, visuals, PNG sizes and resolved `PlayerAnimationsId` / `DroppedItemAnimation` /
  `ItemSoundSetId` / `MaxStack` of the 18 representatives and all spears / spellbooks; `Server/Item/Unarmed/Interactions/Item.json`; the
  49 prefab drop lists (all contain gear; 0.25 gear stacks per fill) and their names; NPC and prefab drop lists with gear stacks above 1;
  `Egg_Spawner_*` in no drop list / recipe / prefab; en-US names (only `Weapon_Kunai` = "Kunai" equals a mystery type word); the Crude
  recipes; the candidate scan (308 / 9 / 299 / 18, the 771 pairs, the 2,765 triples, the weapon shares).
- Jars / files: `More_Crossbow_Tiers.zip` (ships Common art), `SkyyVault.jar` (item JSON + icons from a plugin jar), SkyyGear 0.2.1 jar
  (manifest `IncludesAssetPack`, quality assets), `tools/skyyart.py` (codec, `recolor`, `recolor_icon`, premultiplied icons).
- Live test world, read only (copied into scratch): `Saves/HUD mod/mods/Skyy_SkyyGear/gear.log` (3 "UNID mob" lines; 81 "UNID chest ...
  droplist ZoneN_..." fill-time lines over 7 clock hours, 50 of them in the 2026-10-02 22:00 hour in 18 distinct seconds).
- Build scripts: as cited (G, M, S, K, A, C, T, `build_skyyaccessories_0.5.2.py`, `build_skyyvault_0.1.5.py`,
  `build_skyyessentials_0.1.7.py`, `build_skyycooking_0.1.3.py`, `SkyyWorldGen/build_skyyworldgen_0.1.py` header); specs: Stage 1
  (`research/SkyyGear-Stage1-Spec.md` 5.5-5.7), GL 5 / 8 / 9, ML 5 / 8, W 5.1-5.4, AR 1.1, `research/Tool-Levels-Spec.md` 9-11,
  `research/Smithing-Smelting-Spec.md` l.118-130, T2 3, 7, 12, 13, 16; OPEN-QUESTIONS l.61-62, 122-127, 174-190, 199-213, 247-254, 423-424;
  HANDOFF 2026-10-02 PLAN DONE line.

---

## Review notes (critic pass 2026-10-02, editor)

Every correction was re-checked against the jar, Assets.zip, the scripts or the docs before it was applied.

| # | Correction | Result |
|---|---|---|
| 1 | Smithing XP defaults x10 | Applied (2.4, 7): OPEN-QUESTIONS l.251 confirmed; averages 605 / 990 recomputed. |
| 2 | `gear:extras` belongs in 0.2.3 | Applied (6, 8, 9 AE12, 11, App. A): l.252-253 + HANDOFF PLAN DONE line confirmed. |
| 3 | No reader-live signal | Applied: `gear:tree:readers` (6, 8, AE11); `TreeBonusFn` returns 0.0 for unknown ids (T:3201-3213) confirmed. |
| 4 | Craft XP pays crafted tools | Applied: gear-only rule (tools never pay; they are not `isGear`) + the `xp.craft.exclude` row T2 asked for, defaulted per question 6. |
| 5 | Locked mob-level rarity shift ignored | Applied: `odds.levelShift` 0.02 for mob-sourced rarity (1.7, 3.3, 7); ML 5 row confirmed. |
| 6 | Stage-4 rows neither carried nor retired | Applied: `loot.aboveYou` + `loot.level.world` + the `gear:fn:unid` position carried, `loot.mobSpread` retired (1.7, 4.2, 7). |
| 7 | `q` contradicts "they do not stack" | Applied without a new question: one mystery item per unit (chest split, extra drop entities), `q` only as the no-room fallback; the lock already decides it. |
| 8 | Art tool basis wrong | Applied: `tools/skyyart.py` (pure Python, deterministic) replaces ImageIO; plugin-jar texture marked UNVERIFIED (1.2). |
| 9 | Premultiplied icon alpha | Applied: `SA.recolor_icon` + the r, g, b <= alpha check (1.2, AE1). |
| 10 | Sealed id leaks its length | Applied: 64-byte padded plaintext (1.4, AE3). Recount: 62.7% of 2,765 triples (critic 62% of 2,723; set sizes 2-4 identical). |
| 11 | "Cannot see which sword" overstated | Applied + question 5: 771 pairs, median 3, 14.5% single, 37.7% <= 2, guess 41% reproduced exactly. |
| 12 | Drop glow by rarity false | Applied (1.5, 1.6, step 2, risk 3): protocol `ItemQuality` has no entity config. The "one id per rarity" alternative rejected: it breaks "one mystery item per type" (108 ids). |
| 13 | "Bug found" unproven | Applied: relabelled hardening, with the bytecode reason (all NORMAL priority 0, insertion-ordered edges, roots in registration order); fallback WARN added; AE4 runs the REAL graph. |
| 14 | Death condition incomplete | Applied (3.4, AE4): no-DCR and `NotFinished` cases from `TickCorpseRemoval` / `CorpseRemoval` bytecode; killer ref valid + same store (3.1). |
| 15 | Section 5 bullet 2 false | Applied: `relevelInv` does re-stamp old unidentified documents; the true rule is "nothing converts them". |
| 16 | `PlayerAnimationsId` must be the resolved value | Applied (1.3, AE1): Bow / Throwing_Knife / armor Item; absent keys omitted. |
| 17 | Re-pick must respect MaxStack | Applied (1.4, 2.1, AE3); "MaxStack - 1.7" reworded. |
| 18 | Half / half only at Lv 20-22 | Applied: group-then-type pick with `loot.armorShare` (3.3, 7, AE2); shares reproduced exactly. |
| 19 | Chest estimate about 4x low | Applied (0, 3.6, 10): 0.248 gear stacks per fill and the log counts confirmed; lootstats counters added. |
| 20 | "Once per chest" needs the exact condition | Applied (4.1, AE5): `stash` clears only with `clear` on AND a stack placed (offsets 325-360); `CHEST` clears counted. |
| 21 | Section 6 slot labels stale | Applied: S5 Keen Eye 4% / 40%, S4 Steady Hand, S7 Appraiser, S11 Haggler. |
| 22 | Haggler call sites incomplete | Applied (6, 2.2, App. A, AE9): all sites incl. `ReforgePage`, `GearView.lines`, `costOf(it, u)`, `IdentifyPage.total`. |
| 23 | Zone level ignores W 5.4 | Applied (4.2, 4.5, 8): one contract (`levelAt`, SkyyMobs adds `wg:fn:ring` as step 3b), direct ring read only as fallback; W 5.4's pre-lock rows flagged for the main session. |
| 24 | SkyyArmory dependency under-specified | Applied with one correction: `research/SkyyArmory-Spec.md` DOES exist now (written 23:11) - its 1.1 ids `Weapon_Wand_<Metal>` pass `isGear`; it does not publish `gear:loot:add:SkyyArmory` yet. Assassin `enabled: False` confirmed; the lean now uses `class:list`. |
| 25 | Harness letters collide | Applied as a main-session note (9): Tool-Levels-Spec section 9 says AC like 0.2.1. |
| 26 | Unlocked defaults ship ON | Applied: `loot.classLean`, `loot.levelFrom` (and the new `xp.craft.exclude`) labelled PROPOSED with the ship rule (7). |
| 27 | AE4 tolerance + Kunai name | Kunai special case applied. Tolerance partly rejected: +-0.1 on 100,000 deaths is only 1.6 sigma (a random seed fails about 1 run in 9); used 1,000,000 rolls at +-0.08 (4 sigma). |
| 28 | Missing tests | Applied: scan idempotency (AE6), items without `x` (AE3), `q` path (AE6), edge check (AE1), no-DCR / NotFinished (AE4), shown = charged cost (AE9), `xp.craft.exclude` (AE9), reader key (AE11), the `decide` overload keeps old harness calls (AE5). |
| 29 | Old fill-time tagged chests | Applied (0, 4.1, 5, step 9, risk 12): `GearChestTag` records nothing, confirmed. |

**Added by the editor while checking (not in the critic report):** question 6 and the `*_Crude,*_Wood` proposal (the Crude Sword is a
0-second pocket craft, so the x10 craft rows would make it the cheapest route to Smithing 20); the identify-cost line for chest-odds
items; the "3 tagged mob drops" count (the log gained a line at 22:23); the note that converted vanilla drops can be guessed from
their source mob or chest list (1.1); the check that no vanilla prefab list can roll empty (all 49: the first containers are Choice
lists with RollsMin >= 1 and no Empty entry).

**For the main session (other files, not edited here):** rename the 0.2.2 harness section to AD in `research/Tool-Levels-Spec.md`;
fix W 5.4's draft `loot.level.world.skywynn_zN` rows (pre-lock bands); note in ML 8 / W 5.4 that `mob:fn:levelAt` replaces
`mob:fn:band` for loot; add `gear:loot:add:SkyyArmory` to the SkyyArmory build; make the SkyyTrees 0.3 build read `gear:tree:readers`
and write `gear:extras:<uuid>`; add the 0.2.3 rollback floor to `tools/deploy_set.py` at deploy.
