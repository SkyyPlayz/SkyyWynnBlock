# Skill-tree node icons - one icon per node (DRAFT v1: the Mining tree, 44 icons, 64 x 64)

Skyy (2026-10-23, screenshot of Character > Trees > Mining at 150 %): "most of these use a pickaxe icon. we should make custom icons for
most of these". Every Mining node now has its OWN picture that shows what the node does (coins from ore = a coin on an ore chunk,
Motherlode's rare x3 jackpot = three gems bursting from a gold star, speed = a pick with motion lines, Smelter's Touch = a bar on a flame ...).
Status: **DRAFT, waiting for Skyy's OK on `sheet.png`**. Not wired in, not seen in game.

Original pixels drawn from code (`tools/art/make_tree_node_icons.py`, pure Python, reuses `tools/art/make_menu_icons.py`'s painter -
the same family look as the approved menu / warp icons). No vanilla file, other mod or reference picture was read, copied, traced or recoloured.

## 1. Files

| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/Skyy_NodeIcon_Mining_<B><R><a/b/c/Free>.png` | 44 icons, 64 x 64 RGBA, hard alpha, 1 px dark outline, no pure black / white |
| `sheet.png` (= `sheet-mining.png`) | review sheet: every icon 2x + 1x with its node name, key, kind, max and effect text; each node on its dark disc at 100 % (32 px disc, 18 px icon) and 150 %; the real-size strips at the bottom (tree-colour / gold / locked rings) |
| `manifest.json` | per tree: node key -> icon item id -> file (bytes, sha256), saved key, branch, row, kind, name, effect, category + accent, what the icon shows; `node_counts` of all 19 trees |

File stem = the node's place, not its name (a renamed node keeps its icon): `B3R3b` = branch 3, row 3, upgrade b (Deep Bounty);
`B1R2Free` = branch 1, row 2's free perk (Vein Burst); `B1R6` = branch 1's capstone.

## 2. Colour code (research/Vanilla-UI-Style-Guide.md section 15)

The icon's ACCENT marks (plus signs, sparkles, motion lines, rays, arrows, waves) take the colour of what the node boosts:
yield / loot / coins green `#7ee08a` - skill XP gold `#e8c25a` - speed Air white-teal `#86d8d0` - health / safety red `#ff7a7a` -
damage Fire orange `#ff9a3c` - tool / durability soft white `#d6e4ee` - pets Beastmastery tan `#d8a070` - ability / sense the Mining
tree blue `#8fc8ff`. Each node's category is in `manifest.json`.

## 3. Wiring them into SkyyTrees (for the main session's next Trees patch - this folder edits no build script)

1. **Ship 44 icon-only items** exactly like SkyyMenu ships its `Skyy_Menu_Icon_*` (SkyyMenu 0.3.11 ICON_ITEMS, `build_skyymenu_0.3.45.py` ~line 14705):
   - `Server/Item/Items/Utility/<id>.json` = `{"TranslationProperties": {"Name": "server.items.<id>.name"}, "Icon": "Icons/ItemsGenerated/<id>.png",
     "Variant": true, "MaxStack": 1}` + the held-look keys `Model`, `Texture`, `Scale`, `PlayerAnimationsId`, `ItemSoundSetId` copied from
     one vanilla look item (never held - any small item, e.g. the ore it is about). No `Categories` (hidden from the creative library),
     no `Recipe`, no `Interactions`.
   - `Common/Icons/ItemsGenerated/<id>.png` = the file here, byte for byte (assert the sha256 from `manifest.json`).
   - lang: `items.<id>.name=<node name>` + `server.items.<id>.name=<node name>` (unique ids, so `tools/ci/langdup.py` stays clean).
   - asserts: `<id>` not in Assets.zip ITEM_IDS, `Common/<Icon>` not a vanilla path.
2. `OWN_ICON_IDS = set(<the 44 icon_id values of manifest.json trees.Mining.nodes>)`.
3. `NODE_ICON_ART["Mining.b3.r3b"] = "Skyy_NodeIcon_Mining_B3R3b"` ... one per node (key = manifest `key`; free perks
   `"Mining.b1.r2.free"`).
   **The hook needs a small change first** - today (0.5.0) `node_icon()` is applied only to the 0.3 rows (`"Mining.MSpeed"`, line ~2482)
   and the class nodes (line ~3421), and `_ART_KEYS` (line ~3423) only knows those keys. The radial page's upgrade icons are
   `V3_UP[k]["icon"]` (line ~4078: the 0.3 alias node's icon, else the tree icon = the pickaxe Skyy saw), and several upgrades share one
   0.3 alias (Quick Swing + Steady Pick = `Mining.MSpeed`), so the key must be the v3 node, not the alias. Add after the V3_UP / V3_RW
   loop (~line 4100), before the `must_icon` checks:
   ```python
   for _u in V3_UP:                                   # "Skill.Mining.b3.r3b" -> "Mining.b3.r3b"
       _u["icon"] = node_icon(_u["key"].split(".", 1)[1], _u["icon"])
   for _r in V3_RW:
       if _r["fic"] and V3T[_r["tv"]]["kind"] == "skill":
           _r["fic"] = node_icon("%s.b%d.r%d.free" % (V3T[_r["tv"]]["name"], V3_BR[_r["b"]]["n"], _r["num"]), _r["fic"])
   ```
   and extend `_ART_KEYS` with those keys (moving the `assert set(NODE_ICON_ART) <= _ART_KEYS` below this). The `must_icon()` loops
   (~4104-4107) must skip ids in `OWN_ICON_IDS` (must() checks Assets.zip only).
4. Free perks: the radial map draws a free perk as a diamond with NO icon (`node_icon` lambda ~line 13600 returns None for a negative
   TM_CODE); their icon shows in the right panel (`RFIC`). To show the 4 free-perk icons on the map too, return `V3_RW[-c - 1]["fic"]`
   for them - a layout call for the main session (the diamond is 0.7 x the node size).
5. Other trees: add `DRAW["<Tree>"]` rows in the generator, run `--tree <Tree>`; the manifest keeps every tree.

## 4. Regenerate / check

`python tools/art/make_tree_node_icons.py [--tree Mining]` (deterministic) - `--check` (two builds byte-identical, writes nothing) -
`--counts` (nodes per tree). The node list is read from `tools/trees_v3_data.py`; the build stops if a node has no picture or a picture
names a node that is gone.

## 5. Node counts (for sizing the next icon rounds)

Skill trees: Mining 44 (done), Foraging 42, Combat 42, Beastmastery 40, Farming 40, Cooking 40, Alchemy 40, Fishing 17, Exploration 18,
Acrobatics 19, Smithing 19. Class trees: Warrior 37, Berserker 38, Spellblade 38, Monk 38, Assassin 41, Archer 41, Mage 44, Priest 46.
(Counts include each row's free perk / ability. Class rows' free abilities already have approved art in `art/ability-icons`.)

## 6. Open questions for Skyy (each with today's default)

- OK the 44 Mining icons as drawn? [default: yes - wire them in the next Trees round]
- Show icons on the free-perk diamonds of the map too? [default: yes, 0.7 x size like the diamond]
- Echo Step (two teal after-image boots) and Steady Pick (pick over a rhythm line) are the weakest reads at 18 px - redraw if Skyy wants.
