# Potion Flask + Food Pouch - spec

*Spec 2026-10-16 (paper only, nothing built). Owner: Skyy (they/them). Lives in research/ (INDEX.md "research"). Skyy's answers go to
`docs/answered/skills.md` (where the idea is); open questions (section 7) go to `OPEN-QUESTIONS.md` until answered.*

Skyy 2026-10-16 (docs/answered/skills.md, POTION FLASK + FOOD POUCH): "wynncraft has a cool potion thing i want to add. a healing potion
that holds all the healing options you have (they do in automatically like our pockets.) and when you right click it it drinks a potion.
(sorted from worst to best. and drinks the first first.) id like to do that for healing potions and food." + "(takes the normal eat/drink
time to consume.)". Popups: "Two items (Recommended)"; "Healing only (Recommended)"; "Yes, lifelong (Recommended)"; filling: "auto like the
void, with a toggle."

Read with: `research/Menu-Pattern.md` (section 3 = the page rules), `tools/skyyonce.py` (lifelong one-per-profile items),
`tools/PROFILES-CONTRACT.md`, `tools/CONFIG-CONTRACT.md`, `research/Cooking-Skill-Spec.md`, SkyyCooking 0.1.10 header (eat speed, families),
SkyySacks 0.8.13 header (Void sweep, auto-pickup, journal), `research/Grapple-Bolt-Spec.md` 2.1 (the marker-effect click trick).

---

## 0. Survey - does a mod already do this?

| Mod | What it is | Verdict |
|---|---|---|
| Aetherhaven 4.0.0 (Hexvane, in Skyy's Mods folder, not in PACK.md) | `Aetherhaven_Alchemy_Flask`: a MaxStack 1 potion whose Secondary is a 1.5 s `Charging` that ends in a custom Java interaction type `AetherhavenAlchemyFlaskConsume` (registered through the interaction codec). One brew at a time, no store, no auto-fill, `FailOnDamage: true`. | LEARN: the shape (vanilla charge + "consume" step swapped out). We avoid the custom codec (new to our javassist toolchain) and keep hits from cancelling. |
| The Armory 1.23 (PACK, switched off) | Potion belts: armor-slot containers, 8 potions, `ItemTag Type=Potion`, opened with `OpenItemStackContainer`. No drinking from the belt. | Storage only - no. |
| NotEnoughPotions 2.3.0 | More potions (one healing splash). No container. | No (its potions stay out, see 2.2). |
| OffhandAutofill 0.1.0, PapiSpieltAutoHeal 0.0.7 | Refill an offhand stack; commands that heal. | No. |
| CurseForge (web search 2026-10-16) | HyFlask (reusable flask, charges back on sleep, you learn effects), Green's Potions, PotPvP, Alchemy: Weaponized. No auto-filling store, no food bag. ([HyFlask](https://www.curseforge.com/hytale/mods/hyflask), [Green's Potions](https://www.curseforge.com/hytale/mods/greens-potions), [PotPvP](https://www.curseforge.com/hytale/mods/potpvp), [Alchemy: Weaponized](https://www.curseforge.com/hytale/mods/alchemy-weaponized)) | Different idea (a refilling charge, not "holds what you own"). |

**Verdict: build ours.** No duplicates: Requip (SkyyWardrobe) also stores potions / food, but as loadout storage - it never drinks or
eats. The Flask / Pouch are the only "use from a store" items. Requip must leave our two items alone (4.3).

---

## 1. The items

| | Potion Flask | Food Pouch |
|---|---|---|
| Base id (empty) | `Skyy_Flask_Empty` | `Skyy_Food_Pouch_Empty` |
| Loaded ids (one per thing it can hold, 3.1) | `Skyy_Flask_V_<PotionId>` (5) | `Skyy_Food_Pouch_V_<FoodId>` (~350: 26 dishes x Grades 0-12 + raw snacks) |
| Id prefix (every rule matches the prefix) | `Skyy_Flask_` | `Skyy_Food_Pouch_` (NOT `Skyy_Cook_Food_` - that prefix goes to the Farming bag) |
| Look | vanilla `Items/Consumables/Potions/Potion_Large.blockymodel`, a red texture generated at build from the vanilla potion texture | vanilla `Items/Consumables/Food/Food_Bag.blockymodel` + its texture |
| Icon | ONE icon for all flask ids, ONE for all pouch ids (generated at build; no new textures per variant, so no atlas growth - The Armory was switched off for atlas overflow) | same |
| Name / description | one shared name key per item ("Potion Flask" / "Food Pouch"); the live line comes from `ItemDisplay` metadata (2.5) | same |
| Stack, quality | MaxStack 1, `DropOnDeath: false`, untiered -> no tier tag | same |

**Lifelong (like the tools / Pocket / Menu item, `tools/skyyonce.py`):** one of each per profile, given to every profile once (existing
profiles too, run-once marker), never dropped, never on the ground, never left in a chest / Vault / trade, never sold (market:veto), never
in a starter kit twice (`once:item:<id>`), extra copies removed with a History line first. Recall: `/flask` and `/pouch` give it back when
the inventory holds none, and otherwise open the page on that tab (2 commands, nothing replaced - new system).
- skyyonce today guards ONE id; this needs a **prefix mode** (`item_prefix="Skyy_Flask_"`: every id with that prefix counts as the same item;
  a kept copy of any variant is fine, the 2.5 sync fixes its id). Kit change, additive; the three jars already built keep working unchanged.
- **Given storage-first** (engine rule; the hotbar is already full of lifelong tools). The player drags it to the hotbar once. A full
  inventory = the skyyonce rescue / recall line.
- The store lives in the profile's file (2.1), never on the item, so every copy is the same - skyyonce's "opener" rule holds.

**Hotbar behaviour**
- Right click = use the next item (section 3).
- Crouch + right click = open the page (vanilla consume roots already branch on `Crouching`; ours sends crouch to `OpenCustomUI`, the
  SkyyMenu-item pattern).
- Empty right click = a short popup line: "Your Potion Flask is empty - healing potions go in by themselves (Auto-fill ON). Crouch + right
  click to open it." (Food: same with food.)

---

## 2. Contents

### 2.1 The store (per profile, PROFILES-CONTRACT rules)
- File `Skyy_SkyyCooking/supplies/<pkey>.properties`: `flask.<itemId>=<count>`, `pouch.<itemId>=<count>`, `flask.auto=true`,
  `pouch.auto=true`, `skip.<itemId>=true` (per-item "do not auto-fill"). Keyed by `pkey(u)`; cache keyed by the pkey String.
- Plain stacks only: an item carrying metadata is never taken (same as the Void), so nothing personal is lost.
- Cap per store (Server Setup, 4.4). Full = auto-fill leaves the rest in the inventory, one popup line per minute at most.
- Every change (fill, take out, use, reserve, return) = one journal line in `Skyy_SkyyCooking/supplies/journal.log` with its undo;
  History snapshot of the file before the first write of a session. Crash safety = copy SkyySacks' journal + credit-delay pattern (the
  item leaves the inventory first, the store is credited after the engine has saved the inventory) - name the Sacks classes in the build.
- `profile:busy:<uuid>` set = no moves (retry every 2 s, like skyyonce).

### 2.2 What counts
- **Flask - healing potions only** (Skyy: "Healing only"): vanilla `Potion_Health_Lesser`, `Potion_Health_Small`, `Potion_Health`,
  `Potion_Health_Greater`, `Potion_Health_Large` = every item in Assets.zip whose Secondary is `Root_Secondary_Consume_Potion_Health`
  (found at build time, asserted 5). Not: `Potion_Regen_Health*` (decorative in 0.7), splash potions, mana / stamina / signature.
  Our mods add no healing potion today; a future one joins by its id in the same list.
- **Pouch - every food SkyyCooking knows**: the 15 vanilla dishes it overrides, its 11 own dishes, every graded copy
  `Skyy_Cook_Food_*_G1..G12`, and the raw snacks it overrides (raw meats, raw fish, egg, cheese) - but raw snacks only when Server Setup
  `supplies.pouchRaw` is on [default OFF: raw produce stays a Farming-bag ingredient, Q4].
- **Pack-mod potions / foods are left out**: a loaded id copies the item's own numbers (3.1), and PACK rules forbid copying their numbers.
  They stay normal items.

### 2.3 Auto-fill (like the Void, with a toggle)
- When: the owner's `InventoryChangeEvent` on a player (only if a fillable id is in the main storage section and that store's Auto-fill is
  ON) + PlayerReady 1.5 s later -> ONE deduplicated world-thread task per player (the skyyonce task pattern). Count before / after.
- Where from: **main storage + backpack only. The hotbar is never touched** (a potion you put in the hotbar on purpose stays; Requip
  loadouts keep working). The same reach as the Void's 2 s sweep.
- So every pickup, craft, chest take, quest reward, Bazaar buy that lands in storage goes in.
- **Order with the Void:** today no clash - the Void never takes potions, and cooked food only when `bags.cookedFood` is ON (default OFF).
  Rule: **the Flask / Pouch go first when their Auto-fill is ON** (eating beats storing). SkyySacks asks `supply:fn:claims` before its
  sweep / auto-pickup / Deposit all routes an id (small Sacks change, 4.3). Auto-pickup then lands it in the inventory and our task takes it.
  Raw snacks: the Void first (they are ingredients) unless `supplies.pouchRaw` is ON.
- **Toggles:** per store Auto-fill ON / OFF (Skyy's toggle, on the page, saved per profile, default ON); per item "Auto-fill this" (the
  page row) for someone who wants to keep e.g. Grade 12 stew out. Manual "Put all in" on the page works with Auto-fill OFF.

### 2.4 The page (Menu Pattern section 3)
- **Storage hub > Supplies** (new HUB_TABS row `("storage", "supplies", 15, "SkyyCooking", "Supplies", "flask")`), 1600 x 980, row 1 +
  row 2, sub-tab row: **[Potion Flask] [Food Pouch]** + on the right the store's Auto-fill switch.
- Content: `scroll_list` in a `list_well`, `list_card` rows (icon, name in rarity colour, "Grade 5" / heal line, count), **sorted worst ->
  best** (3.2) - the same order right-click uses; the first usable row carries a "Next" badge. Untiered items (no tier tags apply: food and
  potions are untagged in `tools/tier_tags.py`).
- Detail panel (456 wide): icon, name, the item's own effect text, count, buttons **Take 1** (Primary), **Take all**, "Auto-fill this:
  ON / OFF". Footer: status line left, **Put all in** right.
- Take out = store -> inventory, storage first, count before / after, journal; no room = refused with a status line.
- Empty state: "No healing potions yet - drink-ready potions you pick up go in here." Mod missing = tab hidden.
- Opening the page / any change re-syncs the held item (2.5).

### 2.5 What the held item shows
- Its id is ALWAYS the loaded id of the next item (`Skyy_Flask_V_Potion_Health_Small`), or the Empty id. That is what makes right click
  run exactly that item's effect (3.1).
- Name / description via `ItemDisplay` metadata (VERIFIED in use: SkyyRolls writes reforge names this way): name "Potion Flask (12)",
  description "Next: Small Health Potion - then 4 more kinds. Right click: drink. Crouch + right click: open." Food: "Food Pouch (38)",
  "Next: Bread (Grade 5)".
- **Sync** (write `new ItemStack(id, 1)` + the display metadata into the slot where the copy sits, any section): after a use, a fill, a take
  out, a toggle, PlayerReady, a profile switch (new profile's store). Only when id or text changed. **Never while a consume chain of that
  player is running** (read `InteractionManager.getChains()` - VERIFIED in SkyyArmory 0.1.17 `sigHit`); deferred to the chain's end.

---

## 3. Using it

### 3.1 How the effect stays exactly the item's own (build time, SkyyCooking)
The vanilla consume chain reads the HELD item's `InteractionVars` (`Effect`, `ConsumeCooldown`, `ConsumeSFX`, `ConsumedSFX`,
`Consume_Charge`, Cooking's `Skyy_Cook_Apply_*`) and removes 1 of the held item with `ModifyInventory AdjustHeldItemQuantity -1`.
So each loaded id = **a copy of the real item's Interactions + InteractionVars + animation fields**, with only two changes:
1. The charge copy has the `ModifyInventory -1` step replaced by `ApplyEffect Skyy_Supply_Used` (an invisible 0.2 s marker effect, the
   Grapple Bolt / SkyyFishing click trick) followed by the same `Next` (SFX, cooldown, Effect).
   - Food: our copies `Skyy_Supply_Charge_Food_T<n>_Inner` of SkyyCooking's `Skyy_Cook_Consume_Charge_Food_T<n>_Inner_Fast` - so the
     **25 % faster eating** (1.875 s) and **FailOnDamage false** (hits never cancel) come along. The loaded id's `Consume_Charge` var points
     at them.
   - Potions: our copy `Skyy_Supply_Charge_Potion_Fast` of vanilla `Consume_Charge_Potion_Fast` (1.5 s, FailOnDamage false) and a copy of
     `Condition_Consume_Potion_Health` that keeps the **same CooldownCondition id `Potion_Consume_Health`** - the flask shares the vanilla
     15 s potion cooldown, it is never faster than loose potions.
2. The root: crouch -> `OpenCustomUI` (the page), else the vanilla / copied consume path. Recipe, model, quality, DropOnDeath come from
   the Flask / Pouch, not the item.
Because the loaded id is generated **in the same loop that writes each dish** (`set_food`), a Grade / family / buff change in Cooking
changes the pouch copy in the same build - one writer, never out of step. Effects, Grades, families, "a weaker buff never replaces a
stronger one", Alchemy's duration bonus (applied to the effect id) all work as for the item itself. Build self-check: every loaded id's
vars equal its source item's vars except `Consume_Charge` / the charge id; every referenced id exists.

### 3.2 Order: worst first
- Flask: by total healing (instant + regen over its duration, computed at build from the effect assets), then ItemLevel, then name. The
  build prints the order and asserts Lesser comes first.
- Pouch: Grade low -> high, then total restore value (SkyyCooking's own `numbers()`), then name; raw snacks (Grade 0, raw) first.
- Items whose "Auto-fill this" is OFF still get used (that switch is about filling) [Q1 asks about a family choice].
- Vanilla rule kept: a potion whose regen is refused because a stronger one runs is still used (that is what the loose potion does).

### 3.3 One use, no dupes (runtime)
1. **Start:** `InteractionChainStartEvent` (cancellable; VERIFIED in pre.4 - re-verify on the 0.7 jar with tools/dev/reflect.py) for a
   Secondary chain whose held item has our prefix: read the loaded id -> **reserve** 1 of that item (store -1, journal "reserve"). Not in
   the store (taken out, profile switched) = **cancel the event** (no animation) + sync. Empty id = no reserve, the empty line.
2. **Finish:** our tick (only players holding a Flask / Pouch - cheap) sees `Skyy_Supply_Used`, removes it, **commits** the reservation
   (journal "use"), then syncs the held item to the next one.
3. **Cancel:** the chain is gone from `getChains()` with no marker (let go, slot change, death, crouch, page) -> the reservation is
   **returned** (journal "return"). Cancel = nothing used.
4. Crash with a reservation open: on start-up an open "reserve" without "use" / "return" is returned (journal undo).
- The held id never changes during a chain (2.5), so the effect that ran and the item that is taken are always the same item. This blocks
  the "start with Grade 12, auto-fill a Grade 0 mid-eat, pay with the Grade 0" trick.
- Holding the button: roots keep `RequireNewClick: true` (vanilla), each drink / bite is its own click and its own reserve.
- The SkyySacks take / put / commit bridge is the model for reserve / return / commit.

---

## 4. Owner, bridge, settings

### 4.1 Owner: SkyyCooking (recommended)
- It already generates every food's vars and the fast charge copies (3.1) - the loaded ids MUST come from the same build or they drift.
- It already reads Assets.zip items at build, so the 5 potion copies are cheap there too.
- It is small and chat-only today (no page) - a new page there does not crowd a big mod. SkyySacks (13k lines) would have to read
  Cooking's generated JSON across builds (drift); a new mod = one more jar for two items.
- Rejected: SkyySkills (Alchemy) for the Flask - splits one engine (store, reserve, page) across two mods.

### 4.2 Bridge keys (plain java.lang types)
| Key | Shape | Who uses it |
|---|---|---|
| `supply:fn:claims` | Function `Object[] {UUID, String itemId}` -> Boolean (true = Flask / Pouch takes it now) | SkyySacks sweep / auto-pickup / Deposit all |
| `supply:fn:counts` | Function UUID -> HashMap itemId -> Long (flask + pouch, null = busy) | later: HUD, Stats |
| `once:item:Skyy_Flask_*` / `Skyy_Food_Pouch_*` | skyyonce rule 6 (prefix) | SkyyIslands starter kit |
| `market:veto` entry | skyyonce rule 5 | Bazaar, Auction House |
| `hub:tab:storage:supplies` | the hub contract | SkyyMenu hub rows |

### 4.3 Other mods touched (small)
- `tools/skyyonce.py` prefix mode (kit; test file).
- `tools/skyyui.py` HUB_TABS row (kit).
- SkyySacks: ask `supply:fn:claims` before routing an id; never sweep our prefixes.
- SkyyWardrobe (Requip): add both prefixes to `swap.keepIds` (loadouts never pool or move them) and refuse them in the ITEMS space.
- SkyyProfiles: nothing (the item travels with the inventory; the store follows the pkey).

### 4.4 Server Setup rows (`tools/skyycfg.py`, category SkyyCooking > Supplies)
| Key | Type | Default | Note |
|---|---|---|---|
| `supplies.on` | bool | true | OFF = items stay but do nothing except open the page; nothing new fills |
| `supplies.lifelong` | bool | true | the skyyonce switch |
| `supplies.flaskCap` | int 1-10000 | 64 | potions held [Q3] |
| `supplies.pouchCap` | int 1-10000 | 256 | foods held [Q3] |
| `supplies.pouchRaw` | bool | false | raw snacks go in the pouch [Q4] |
| `supplies.fullNoticeSeconds` | int seconds | 60 | how often "full" is said |
No eat / drink time row: the times are the vanilla / Cooking ones (Cooking's eat-speed row covers food).

### 4.5 Tier tags
None: the two items are untiered, potions and food are untagged in `tools/tier_tags.py`. If a tiered ladder is added later (Q3), it gets
its own ladder tag ("T2 Flask") via `ladder_tag`.

---

## 5. Engine feasibility - the risky parts

| # | Risk | Why | Probe / fallback |
|---|---|---|---|
| R1 | A loaded id with copied vars + the marker in place of `ModifyInventory` runs the food's effect and keeps the held item. | Assets-only, vanilla types; each piece is used today (vars per item - Cooking; ApplyEffect marker - Grapple / Fishing), the combination is new. | **P1** (probe jar, offline smoke + Skyy test): `Skyy_Probe_Pouch_V_Food_Bread` eats like Bread (same heal, same 1.875 s, a hit does not stop it), stays in the hand, marker seen. |
| R2 | `InteractionChainStartEvent` on 0.7: fires for Secondary, names the held item, cancel works. | VERIFIED pre.4 only. | **P2**: reflect + log on the 0.7 jar. Fallback: reserve at the marker instead (no cancel; then a pouch with an id not in the store gives one free use - so sync on every store change and refuse the debit with a History line). |
| R3 | Rewriting the held slot's id between clicks does not break the next click / client prediction. | Normal slot write, but in the active slot. | **P3**: two different foods, click fast 10 times; count store vs effects. |
| R4 | ~350 extra item assets load fast and add nothing to the texture atlas. | Shared model / icon / texture. | Smoke test log time + asset-validation; P1 jar ships them all. |
| R5 | The Charging copy keeps the eat animation for a non-food item model. | Animation comes from the copied `PlayerAnimationsId`. | P1 look check. |
Rejected: a custom interaction type (Aetherhaven's way) - `BuilderCodec` from javassist is UNVERIFIED in our toolchain; applying effects
from Java - would not be "exactly that item's effect" (Grade chains, EffectConditions, SFX, cooldowns would all be re-written by hand).

---

## 6. Build rounds

| Round | What | Size |
|---|---|---|
| **FP0 probe** | SkyyFlaskProbe jar: P1-P3 (one loaded bread + one loaded potion, chain-start log, slot rewrite) + smoke test; Skyy tries P1 / P3 in game. | lean (one builder, Opus) |
| **FP1** | SkyyCooking next version: items, loaded ids, store + journal, auto-fill, reserve / commit / return, page, `/flask` `/pouch`, Server Setup rows, bridge; skyyonce prefix mode; HUB_TABS row; SkyySacks `supply:fn:claims`; SkyyWardrobe keepIds. | **full round** (saved data, items that could be duped, several mods) - waits for sacks0814, wardrobe 0.2.5 and the kit K step of the Menu Pattern if it is running |
| FP2 (later, only if Skyy wants) | upgrades (cap / tiers), HUD count widget, pack-mod foods with their authors' OK. | lean |

In-game test (FP1): pick up a Lesser + Small potion -> both in the Flask, Lesser drunk first, 1.5 s, a hit does not stop it, 15 s cooldown
shared with loose potions; let go mid-drink -> count unchanged; Grade 3 and Grade 0 bread -> Grade 0 eaten first in 1.875 s; Auto-fill OFF
-> new food stays in the inventory; hotbar food never pulled in; drop / chest / AH refused; `/pouch` with no pouch gives it back; switch
profile -> the other profile's store.

---

## 7. Questions for Skyy (defaults in [brackets])

1. **Food order:** worst first across ALL foods (a Mana dish may come before a Health dish), or worst first inside the bar you pick on the
   page (Health / Mana / Stamina)? [Worst first across all foods; each food row also gets a "Use this: ON / OFF" switch.]
2. **Page:** a new Storage tab "Supplies" with Flask / Food Pouch sub-tabs, crouch + right click on the item opens it? [Yes.]
3. **Size / upgrades:** fixed size (Flask 64, Pouch 256, changeable in Server Setup), or upgrade them like the tools (bigger with each
   tier)? [Fixed for now; upgrades later if you want.]
4. **Raw food:** raw meat / fish / eggs / cheese stay in the Farming bag (ingredients), the Pouch takes only cooked dishes? [Yes - a
   Server Setup switch can put raw snacks in the Pouch.]
