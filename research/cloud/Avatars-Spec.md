# Avatars spec (draft, 2026-10-10)

Cloud draft. Nothing is built. Everything that needs the game files is marked **UNVERIFIED** and listed under "For the local session".

## Decisions this follows

- `docs/answered/social.md` line 52 (LOCKED 2026-10-10, newest on this topic). Skyy asked: "is there a way to make the player menu show
  player heads? (there is a Minecraft mod that shows the player heads before their name in chat too, i love that one.)" Answer
  recorded: real skin heads are not possible today (the client draws skins; mod UI shows item icons only; no player-preview element in
  the vanilla .ui files - re-check on Hytale 0.7). Popup answer "Chosen avatar (Recommended)": every player picks an AVATAR icon (pet
  faces, mob heads, class crests, unlocked by playing) shown in the Players list, Party, Guild and - if chat formatting allows - as a
  badge before the name in chat. "spec + engine check (chat icons / glyphs) before building; art = avatar icon set."
- `docs/answered/pets.md` lines 12-17 (second slot, summon slot): pets are per profile and unlock through play. Avatars only READ pets.
- `tools/PROFILES-CONTRACT.md` rule 6: Party / Essentials / HUD / Menu data is per PLAYER unless noted (basis for the default below).
- `HANDOFF.md` section 2: vanilla look, inline pages only, no underscores in element ids, item icons in `ItemGridSlot` carry no metadata.
- `.claude/skills/skywynn-art/SKILL.md` (art rules) and `PROJECT-RULES.md` section 4 (Server Setup rows through `tools/skyycfg.py`).

## 1. What an avatar is

One small picture a player chooses to stand for them. It is a cosmetic only: no stats, no power, nothing to lose or duplicate.
Unlocking is automatic when the player does the thing (no coins, no shop). The avatar is stored as an icon id string, never as an item
in the inventory, so it cannot be dropped, traded or duped.

## 2. The icon set and how each group unlocks

Ties to systems that exist or are planned. A group whose source system is not built yet is marked LATER and ships hidden until then.

| Group | Icons | Unlocks when | Source system | State |
|---|---|---|---|---|
| Default | 1 | always (everyone starts with it; used until a pick) | none | now |
| Pet faces | 30 | you own that pet (a record in your pet ledger, any profile) | SkyyPets (30 launch kinds, `research/Pets-Roster.md`, art `art/pets/`) | now |
| Mob heads | 12 | first kill of that mob type (Zone 1-2 list below) | SkyyMobs kill events, later the bestiary | kill hook now, bestiary LATER |
| Class crests | 8 | you have created a profile of that class (Archer, Warrior, Mage, Berserker, Priest, Assassin, Monk, Spellblade) | SkyyProfiles `profile:class:<uuid>` | now |
| Collection badges | 10 | reach tier V of that collection (one per main skill collection) | SkyyCollections | now |
| Total | 61 | | | |

Notes:
- Pet faces: the 15 art pets in `art/pets/` already have 64 px icon items (`Skyy_Menu_Icon_Pet_<Pet>` is how the menu tile shows the
  pet-slot pet today, `SkyyMenu/build_skyymenu_0.3.15.py` header). Reuse those for the first 15 faces; the other 15 kinds need new art.
- Mob heads: suggested 12 = the common Zone 1-2 hostiles and a few boss-type heads for later (Fox, Wolf, Hyena, Bear, Trork, Skeleton,
  Scarak, Kweebec and so on, names from `research/Pets-Roster.md` and SkyyMobs). The exact list is a question for Skyy (Q3).
- Slayers: the repo has no slayer system (it only appears in accessory research). So no slayer avatars now; if slayers are ever built,
  add a group then. The bestiary is a future system (`research/Collections-Spec.md` line 354), so until then mob heads unlock on first
  kill, counted in a tiny per-player set.
- Unlocks are checked from the other mods through the `skyy.bridge` map with plain java.lang types (PROJECT-RULES section 4). SkyyAvatars
  reads, other mods never call it. If a source mod is not installed its group simply shows nothing unlocked.

## 3. Where it shows

| Place | How | Notes |
|---|---|---|
| Players list (SkyyMenu `players` view, 28 slots per page, `PLAYER_SLOTS` in `SkyyMenu/build_skyymenu_0.3.15.py` line 496) | the tile's icon is the player's avatar icon item | Menu already uses icon-only items per tile, so this fits. Icon items carry no metadata (HANDOFF section 2). |
| Party page / HUD party widget | small 24 px icon before each member name | HUD widget is inline markup; an icon in a widget is **UNVERIFIED** (vanilla-looking image element in an inline HUD). Fallback: text tag. |
| Guild member list | same as Party | |
| Chat badge | see below | engine answer **UNVERIFIED** |
| Your Profile page / Settings | big preview of the chosen avatar and the Picker button | |

### Chat badge: can a Hytale Message carry an icon?

What the repo proves today (read-only, from our build scripts):
- Chat lines are built as `Message.raw(text).color(colour)`. SkyyRanks puts `Message.raw(prefix + " ").color(colour)` in front of the
  existing formatted message (`SkyyRanks/build_skyyranks_0.1.1.py` lines 133-137), inside a `PlayerChatEvent` formatter registered with
  `registerAsyncGlobal` and wrapped with `ev.setFormatter(new RankFormatter(prev == null ? DEFAULT_FORMATTER : prev))` (same file, line
  2938). SkyyExploration does the same with its title at order 30000 (SkyyRanks at 31000). So a text badge before the name already works
  the same way as the rank tag. Source of the pattern: `research/Exploration-Build-Spec.md` lines 17, 46.
- Every outgoing chat line is one packet, `ServerMessage(ChatType.Chat, message.getFormattedMessage())`, and `FormattedMessage` has fields
  for text, colour, children and a `markupEnabled` flag (`tools/essentials_0_1_9_patch.py` lines 14-15, 95-96, 109-111). Nothing in
  those lines shows an image, item or sprite field. The same file reads only rawText, messageId, params and children.
- Verdict: a TEXT badge (a coloured tag or a Unicode symbol) is buildable now with the same formatter pattern. A real PICTURE badge in
  chat is **UNVERIFIED**: the protocol class `FormattedMessage` must be dumped to see if it has any image/item/sprite field, and the
  client font must be checked for which Unicode symbols it draws (or whether a mod can ship a font/glyph atlas). Assume NO until
  the local session reports.

Text badge fallback (works without any engine change): a short coloured tag in the avatar's colour, for example `[Fox]` or a 1-2 letter
code, chosen from the avatar's short name. Players who want chat badges off use a Settings switch (`avatar.chat`, see section 6).

Priority: the avatar formatter slots between Exploration (30000) and Ranks (31000) at 30500 so order reads `[Rank] [Avatar] [Title] Name`.
Whether Skyy wants that order is Q5.

## 4. The picker page

- Opened from SkyWynn Menu "Your Profile" tile (new button "Avatar") and by `/avatar` (player command, `setPermissionGroups(new String[] {"hytale:Adventurer"})` on
  the command and every variant; HANDOFF section 3).
- Layout (vanilla look through `tools/skyyui.py` `page_shell`, `button`, `panel_row`; style guide `research/Vanilla-UI-Style-Guide.md`):
  - Left: group tabs (Default is not a tab; Pets, Mobs, Classes, Collections) and the count "12 / 30 unlocked".
  - Centre: an `ItemGridSlot` grid of icon items (no metadata). Unlocked icons are bright; locked icons are shown dim with the unlock rule in the
    tooltip ("Own a Fox pet"). Items are plain `new ItemStack(id, 1)`.
  - Right: big preview, the avatar name, how it unlocked, buttons "Use this avatar" and "Clear (use default)".
- All element ids letters and digits only, inline `Text` only `[A-Za-z0-9 <>/-]` (anything else through `b.set`). Click handlers only;
  never page updates from Mouse Entered or Exited (HANDOFF section 2).
- Owner of a pick sees it at once on every place in section 3 (next tick of the display cache).

## 5. Per account or per profile

Default: **per account (per player)**. Reasons: the avatar is how others recognise YOU in a list or chat, and profiles are different
characters on the same person (`tools/PROFILES-CONTRACT.md` rule 6, Party / Menu data is per player). Unlocks are also account-wide so a
Monk profile earns the Monk crest for the whole account. Option B (Q2): the chosen avatar per profile, unlocks still per account, so a Monk
profile could wear the Monk crest while the Archer profile wears a Fox. Cost of option B: one more key through `pkey()` (profile key) and
a republish on `profile:epoch:<uuid>` change.

## 6. Which mod owns it

Recommended: a NEW small mod **SkyyAvatars** (own data folder `Skyy_SkyyAvatars`, zero hard dependencies, reads other mods only through
the `skyy.bridge` map). Reason: the chat formatter, picker, unlock cache and save file are one self-contained job, and the rules say each
Skyy mod stays standalone. Alternative (Q1): put it inside SkyyMenu (it already owns the Players view and Your Profile page) - fewer jars
but a heavier SkyyMenu and the chat formatter then lives in the menu mod.

Bridge keys (all plain java.lang types):

| Key | Value | Written by |
|---|---|---|
| `avatar:<uuid>` | String icon id of the chosen avatar ("Pet_Fox", "Class_Monk", ...). Absent = default | SkyyAvatars |
| `avatar:fn:icon` | Function apply(UUID) -> String icon id (what other mods draw) | SkyyAvatars |
| `avatar:fn:tag` | Function apply(UUID) -> String short text tag for text fallbacks | SkyyAvatars |

Save file: `Skyy_SkyyAvatars/players/<uuid>.properties`: `chosen=Pet_Fox` and `unlocked=Pet_Fox,Class_Monk,...` (comma list). Existing
unlock rules are re-checked on join so a lost file just re-derives pet, class and collection unlocks (mob heads need the kill set kept).

## 7. Server Setup rows (through `tools/skyycfg.py`, `tools/CONFIG-CONTRACT.md`)

| Key | Default | Meaning |
|---|---|---|
| `avatar.enabled` | on | whole feature on/off |
| `avatar.chat` | on | show the badge in chat (if the engine allows; text fallback otherwise) |
| `avatar.chat.priority` | 30500 | chat formatter order (30000 Exploration, 31000 Ranks) |
| `avatar.list` | on | show avatars in Players / Party / Guild |
| `avatar.unlock.pets` | on | pets give pet faces |
| `avatar.unlock.mobs` | on | first kills give mob heads |
| `avatar.unlock.all` | off | owner testing switch: every avatar unlocked for everyone |

Player Settings (the `settings:*` twin, `research/Settings-Spec.md`): "Show avatars in chat" (default on) and "Show avatars in lists" (default on).

## 8. Art list (for the art agent)

Rules from the skywynn-art skill (`.claude/skills/skywynn-art/SKILL.md`): 64 x 64 RGBA item icons, hard alpha, 1 px violet-black outline `#120e1c`, light from the top left,
a 6-7 step ramp per material, no pure black or white; "cute Hytale" for animals. The emblem family to match is `art/menu-icons/`
(see `art/menu-icons/README.md`: 64 px, hard alpha, per-category tint) and the approved menu emblem `art/menu-emblem/`. Original drawings only; never copy
vanilla textures or a pack mod's art. Tool pattern: pure-Python generator next to the sheet, deterministic (`tools/art/` like
`make_menu_emblem.py`), one sheet per group.

| Group | Count | Look | Tint | Reuse |
|---|---|---|---|---|
| Default | 1 | blank adventurer silhouette in a round medallion | steel | new |
| Pet faces | 30 | the pet's face, chunky voxel, big glinting eyes, round medallion frame | teal | 15 already exist as 64 px pet icons (`art/pets/`); crop to the face and add the frame. 15 new |
| Mob heads | 12 | the mob's head, a bit fiercer than pets, square frame | red / rust | new, 12 |
| Class crests | 8 | shield-shaped crest with the class emblem | one colour per class (Monk Saffron #f08a30) | the class emblems are approved (skywynn-art skill section 3); 8 crests, reuse the emblem art |
| Collection badges | 10 | round badge with the collection resource in the centre | gold | new, 10 |
| Total | 61 | | | 15 reusable, 46 new |

Frame per group (one shape per group) so a player can tell the group at a glance in the Players list. The 61 icons ship as
`Skyy_Avatar_<Id>` icon-only items hidden from the creative library (same pattern as `Skyy_Menu_Icon_AccessoryBag` in
`SkyyMenu/build_skyymenu_0.3.15.py`). Art lives in `art/avatars/` with a README and a validation script. Record the locked sheets in
`research/cloud/ART-INDEX.md` style. A 16 px or 24 px version is drawn by scaling down in the generator and checked by eye; if too fuzzy, the
art agent draws a simplified small version (Q6).

## 9. Build phases

| Phase | Work | Needs |
|---|---|---|
| 0 | Engine check (local): can `FormattedMessage` / chat show an image or which Unicode symbols draw; does an inline HUD widget draw a small image | game files |
| 1 | Art: 61 icons + validate script (Default, Class crests, 15 pet faces first) | art agent |
| 2 | SkyyAvatars 0.1: data, unlock rules for pets, classes, collections; bridge keys; `/avatar` picker page; Server Setup rows | phase 1 |
| 3 | SkyyMenu Players grid + SkyyParty + SkyyGuilds read `avatar:fn:icon`; text-tag chat badge | phase 2 |
| 4 | Picture chat badge if phase 0 says yes; else keep the text tag | phase 0 |
| 5 | Mob heads (kill hook) and later the bestiary link | SkyyMobs |

Round size: Full round for phase 2-3 (new mod and several mods, PROJECT-RULES section 4). Phases 1 and 5 are lean / art-only.

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| Q1 | A new small mod SkyyAvatars, or inside SkyyMenu? | [new mod SkyyAvatars] |
| Q2 | One avatar per account or per profile? | [per account; unlocks account-wide] |
| Q3 | Which 12 mob heads? | [Fox, Wolf, Hyena, Bear, Boar, Spider, Skeleton, Trork, Scarak, Slime, Zombie, Kweebec, picked from SkyyMobs once the list is checked] |
| Q4 | Collection badge unlock level | [tier V of that collection] |
| Q5 | Chat order | [Rank, Avatar, Title, Name] |
| Q6 | If chat cannot show pictures, is a coloured text tag like [Fox] OK? | [yes, with a Settings switch to hide it] |
| Q7 | Can players pick any unlocked avatar from any group, or only one group each? | [any unlocked avatar] |

## For the local session

- UNVERIFIED: does `com.hypixel.hytale.protocol.FormattedMessage` (and the client chat) support an image / item / sprite / emoji field? Dump the class and list its fields. Test which Unicode symbols the client chat font draws.
- UNVERIFIED: does an inline HUD widget (the party widget) draw a small image element (`Group` with `Background: (TexturePath: ...)`) from a mod icon item?
- UNVERIFIED: can the Players grid tile show a mod icon item whose `Icon` is a PNG shipped in the jar (the menu pet tiles prove yes for item icons; confirm for 61 more items and the picker's grid size).
- UNVERIFIED: the real list of Zone 1-2 hostile mobs in SkyyMobs for Q3 (cloud has only `research/Pets-Roster.md` names).
- Chat formatter order 30500 between Exploration 30000 and Ranks 31000 - check on the live set that `setFormatter` wrapping three layers keeps the name intact.
- Hytale 0.7 re-check: player head or preview element in the vanilla .ui files (`docs/answered/social.md` line 52 says re-check).
- Docs: add `art/avatars/` and the SkyyAvatars mod to `INDEX.md`; add a line to `docs/log/` when the spec is accepted.
