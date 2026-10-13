# Icons 2026-10-13 - Rarity Sigils, Hub Shard + Shard Portals, Nexus of the Void (DRAFT v1, cloud)

**Status: drafts for Skyy's review. Not wired in, no build script touched.** Made by the cloud session under Skyy's visuals go-ahead
(docs/answered/ui.md line 93).

## Decisions this follows
| Source | Line | What it fixes here |
|---|---|---|
| docs/answered/gear.md | 176 | 2026-10-12 RARITY SIGILS, Skyy word for word: "and to upgrade the rarity of an item. gems? stones? or runes? (we will make it work on any and all gear that has a rarity. and skip tiers. so if you have a common pickaxe, and a legendary upgrade rune, you can just upgrade it to legendary in the /smithing menu" -> popup "Sigils (Recommended)": one sigil per rarity ("Legendary Sigil"), any gear with a rarity, skip tiers, upward only. Names kept apart: Gems = sockets, Stones = pet Upgrade Stones, Runes = Hytale 0.7's runes. |
| docs/answered/gear.md | 123 | the live rarity ladder: Normal, Unique, Rare, Legendary, Fabled, Mythic (+ Set) |
| tools/skyyui.py | 237 | the locked rarity colours: Normal `#FFFFFF`, Unique `#FFFF55`, Rare `#FF55FF`, Legendary `#55FFFF`, Fabled `#FF5555`, Mythic `#CC66CC` (page-readable Mythic; Wynn `#AA00AA` kept in `RARITY_WYNN`) |
| docs/answered/gear.md | 78 | approved accessory icons: "rarity = growing gem + metal" -> sigil frame metals Normal..Legendary = the same iron / gold / rose gold / platinum |
| docs/answered/skills.md | 108, 110-113 | SHARD ISLANDS / SHARDS 2 / SHARDS 3: a shard placed on your island is a PORTAL to a mini island; right-click opens the shard menu (like a vanilla portal); 6 shards Mining, Foraging, Farming, Ranching, Orchard, Combat |
| docs/answered/social.md | 55 + research/Tutorial-Plan.md | the island-3 mini boss drops the **Hub Shard** that activates the portal to the hub |
| docs/answered/skills.md | 117-118 + research/Rebirth-Ideas.md | REBIRTH TREE / CONTROL: the tree radiates from the black hole in the centre, the **Nexus of the Void**; "by touching it, the void imprints your soul"; hover = requirements, click + confirm = rebirth |
| .claude/skills/skywynn-art/SKILL.md + art/menu-icons/README.md | - | 64 x 64 item icons, hard alpha, 1 px violet-black outline, light from the top left, ramp-snapped colours, no pure black / white |

## Files (all in research/cloud/icons-1013/)
| File | Size | What |
|---|---|---|
| `make_icons.py` | - | the generator: Pillow only, deterministic (two runs = same bytes, checked) |
| `sheet-sigils.png` | 1180 x 1080 | 6 sigils: 4x on checker, 1x on menu navy, 1x on light, 32 px; slot row; a smithing mock |
| `sheet-shards.png` | 1560 x 1000 | Hub Shard + 6 Shard Portals, same views + a hotbar row |
| `sheet-nexus.png` | 1500 x 900 | the Nexus 128 + 64, on dark / light, and a mock of the centre of /rebirth |
| `icons/<id>.png` | 64 x 64 (Nexus also 128 x 128) | one PNG per icon, ready to copy to `Common/Icons/ItemsGenerated/` |
| `manifest.json` | - | size, bytes and sha256 of every PNG |

## 1. Rarity Sigils (proposed owner: SkyyGear, /smithing)
One family: a **hex plate** with a recessed field and a glowing **up arrow** (= upgrade) in the rarity colour. The frame grows with rank,
so the rank reads even without colour:

| Proposed id | Frame | Extras |
|---|---|---|
| `Skyy_Sigil_Normal` | iron | arrow only - **optional** (upward only, so nothing can be upgraded TO Normal) |
| `Skyy_Sigil_Unique` | gold | arrow |
| `Skyy_Sigil_Rare` | rose gold | + inner trim line, 6 rivets, a bar under the arrow |
| `Skyy_Sigil_Legendary` | platinum | + a cyan gem at the top corner, a sparkle |
| `Skyy_Sigil_Fabled` | blackened steel | + gold side blades with red inlay, a red top gem |
| `Skyy_Sigil_Mythic` | obsidian violet | + a gold 3-point crown, side blades, top + bottom gems, 3 sparkles |

Not drawn: a Set sigil (Set gear is its own kind, not a rung on the ladder).

## 2. Hub Shard + Shard Portals
One family = **the same hex crystal shard**: faceted rim (light left face, dark right face), a portal **swirl** in its window, a cream
symbol inside the swirl. The crystal colour says which shard.

| Proposed id | Shows | Colour |
|---|---|---|
| `Skyy_Hub_Shard` (carried item, quest key) | the shard LOOSE, held in a gold key clasp with a ring; a gold 8-point compass star with a sky gem inside (the SkyWynn menu emblem's star = "the hub") | void violet `#9466ee` |
| `Skyy_Shard_Portal_Mining` | the shard planted in a small floating island (grass, soil, stepped rock), two side crystals; a pickaxe | blue `#4aa6e8` |
| `Skyy_Shard_Portal_Foraging` | same; a pine tree | green `#46b856` |
| `Skyy_Shard_Portal_Farming` | same; an ear of wheat (each grain outlined) | gold `#e2b532` |
| `Skyy_Shard_Portal_Ranching` | same; a cow's head | orange `#e0864a` |
| `Skyy_Shard_Portal_Orchard` | same; an apple with stem + leaf | blossom pink `#ec6aa6` |
| `Skyy_Shard_Portal_Combat` | same; two crossed swords with gold guards | red `#d83c48` |

The floating-island base says "a shard is a mini island"; the Hub Shard has no island (it is a key you carry, not a place).

## 3. Nexus of the Void (proposed: the centre button of /rebirth; 64 px for a menu tile)
| Proposed id | Size | Shows |
|---|---|---|
| `Skyy_Nexus_Of_The_Void` | 128 x 128 | the hole (deepest void violet, never pure black) inside a bright photon ring; a 4-arm spiral accretion swirl, ember-hot near the hole, violet further out; **8 radiating branches** with nodes (inner lit = spent, outer dim = still to buy) = the rebirth tree growing out of it; a **cyan soul** with two eye dots being pulled into the hole = "the void imprints your soul" |
| `Skyy_Nexus_Of_The_Void_64` | 64 x 64 | the same, 8 straight branches, no sub-branches |

## Questions for Skyy
| # | Question | Default |
|---|---|---|
| 1 | Sigils: drop the Normal sigil (nothing upgrades TO Normal)? | [yes - ship 5: Unique .. Mythic; keep the Normal art unused] |
| 2 | Sigil look: hex plate + up arrow, frame grows with rank. OK, or a different object (seal / scroll / glyph stone)? | [hex plate] |
| 3 | Shard colours: Mining blue, Foraging green, Farming gold, Ranching orange, Orchard pink, Combat red, Hub violet. OK? | [yes] |
| 4 | Ranching symbol: cow head, or a sheep / an egg / a horseshoe? | [cow head] |
| 5 | Portal icon = the shard planted in a mini floating island. Keep the island, or the shard alone (smaller, like the Hub Shard)? | [keep the island] |
| 6 | Nexus: the cyan soul being pulled in - keep it (lore), or a clean black hole only? | [keep it] |
| 7 | Nexus tree look: should the real /rebirth tree use these same violet lines + ember "spent" nodes? | [yes, as the starting style] |

## For the local session
- **UNVERIFIED ids:** check every proposed id (`Skyy_Sigil_*`, `Skyy_Hub_Shard`, `Skyy_Shard_Portal_*`, `Skyy_Nexus_Of_The_Void*`) against
  Assets.zip and the pack mods (PACK.md) before use; rename to the owning mod's prefix if that is the convention (e.g. `SkyyGear_Sigil_*`).
- **UNVERIFIED render:** look at the 64 px icons in a real slot (game filtering at 32 px); the sheets show a LANCZOS 32 px as a guess.
- Hytale 0.7 "runes" exist (gear.md 176) - compare the sigil plate with the vanilla rune icons in Assets.zip so they do not look alike.
- Shard Portals are placed blocks: this round drew only the ICON. The placed model (crystal + swirl, right-click menu) is a later model round.
- The Nexus 128 is meant as a UI image (/rebirth page), not an item icon - check the page kit can show a 128 image button (tools/skyyui.py).
- Regenerate: `python3 research/cloud/icons-1013/make_icons.py` (writes everything above; no other file touched).
- Nothing vanilla was copied, traced or recoloured; no pack-mod files used.
