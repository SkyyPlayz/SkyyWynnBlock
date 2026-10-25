# art/r064-icons - round cap064 icons (DRAFT v1, not yet seen by Skyy)

What is here: the pictures of round cap064 (SkyyTrees 0.6.4 + SkyyClasses 0.1.50, 2026-10-24; docs/answered/classes.md 2026-10-24
PER-PATH CAPSTONES + 2ND ASSASSIN ALT), our own pixels drawn from code by `tools/art/make_r064_icons.py` (the approved class-node painter,
deterministic - two runs = same bytes; `--check` builds twice and writes nothing).

| File | What |
|---|---|
| `Common/Icons/ItemsGenerated/Skyy_NodeIcon_<Class>_B1R6a/b.png` | the 8 new per-path capstones (Oath of Legions, Shatterpoint, Raincaller, Storm of Fists, Supernova, Saint's Covenant, Shroud of Night, Death Sentence) |
| `Common/Icons/ItemsGenerated/Skyy_NodeIcon_Assassin_B1R2c / R3c / R5c.png` | the 3 Shadow Mark path passives (Lingering Mark, Quiet Mark, Killing Intent) |
| `Common/Icons/Abilities/Assassin/ShadowMark.png` | the Shadow Mark ability icon (the approved Assassin ability frame + a new symbol): SkyyClasses' rune, SkyyTrees' row-5 ability node |
| `manifest.json` | every file (sha256 + bytes), the node key / icon id / what it shows - the builds check it |
| `sheet.png` | the review sheet (2x, 1x, on the node disc) |

Why a folder of its own: the shared manifests (`art/tree-node-icons/manifest-classes.json`, `art/ability-icons/manifest.json`) are counted
by the pinned builds - adding entries there would break their byte-identical rebuilds. When Skyy approves these, a later art round may fold
them into those folders together with a Trees / Classes round.

Where new things go: a later round's icons get their own `art/r<round>-icons/` folder like this one (or the shared folders when a build
round updates their counts). Index: `INDEX.md` -> art/.
