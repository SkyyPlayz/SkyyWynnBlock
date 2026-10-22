# Rebirth (idea) - Skyy 2026-10-12

Skyy's words are in `docs/answered/skills.md` (2026-10-12 REBIRTH / NEW GAME+ and REBIRTH TREE). Not designed yet.

## What it is

- **When:** you can rebirth once your **CLASS** reaches max level - even if Mining etc. are not maxed.
- **Resets:** skill and class levels, coins + bank. **Keeps:** the island, shard upgrades, gear (usable again as you re-level),
  collection knowledge. Each rebirth **raises the max** (more collection ranks, higher skill / class caps).
- **Rewards:** a stacking stat boost, cosmetics / title, new content, and rebirth upgrade points for the tree below.

## The rebirth tree

- **ONE rebirth menu with ONE upgrade tree** that **radiates out from a black hole in the centre - the Nexus of the Void** (lore: by
  touching it, the void imprints your soul, altering you in strange ways). Reference look: a radiating star-shaped tree of glowing
  lines and nodes (Skyy's screenshot, kept locally as `research/refs/rebirth-radiating-tree.webp`; Shell Diver's upgrade tree).
- **The Nexus is the rebirth button:** `/rebirth` opens the tree; **hover** the black hole to see the requirements (met / not met) and
  what this rebirth will give; **click** it, then **confirm**, to rebirth.
- **Points are separate per skill:** class rebirth points, Mining rebirth points, Farming points, and so on; each branch of the tree
  spends its own skill's points.
- **XP keeps counting past max level:** extra Mining / Farming XP earned while you finish your class turns into more points at rebirth.
- **Costs** start cheap and scale quickly (like the dust upgrades of the current skill tree).
- **No unlock points:** a row opens when you have about **8 total levels in the row before it**.

## Locked same day

- **All together:** one rebirth at the Nexus resets every skill + the class (no single-skill rebirths). If one big tree can't be drawn,
  fall back to one tree per skill around the Nexus.
- **Lifelong tools:** you spawn with a COMMON pickaxe + axe; tools are never crafted, only upgraded in /smithing (tier with enchanted
  materials, rarity with special tool-upgrade items). Rarity = stat multiplier + better reroll pool (reroll after each rarity upgrade);
  level = your skill level. On rebirth the tool keeps rarity + stats, goes back to Crude at level 0, and gains a **rebirth modifier**
  upgraded in that skill's branch. The **multitool unlocks after the first rebirth** (merge pickaxe + axe, no stat loss, no downside).
  Open: hoes / shovels / sickles / rods; the Multitools pack mod before rebirth 1.

- **Bank at rebirth:** the bank keeps all your money (coins + bank reset); in exchange you get a permanently better interest rate,
  scaled by the balance at reset.

## Research to do (spec)

- Shell Diver's upgrade tree, and how other clicker / incremental games do rebirth (prestige layers, point formulas, cost curves,
  what resets) - Skyy: "lots of other clickers do rebirths really well".
- Check existing Hytale rebirth / prestige mods first (PROJECT-RULES 2).
- UI: can the Hytale UI draw a big zoomable radiating tree (lines + nodes, pan / zoom)? Probe before designing the page.
- 2026-10-22 REFERENCE LOOK #2 (Skyy, screenshot of the Hylterium server tutorial step 8 "Jobs and talents", kept locally as `research/refs/rebirth-tree-hylterium.webp`, git-ignored): "this picture they have in the center here is kinda what i pictured for the rebirth tree. imma play this server a little more and see if there are any good visuals we should learn from." -> what the picture shows: ONE radial web, a glowing centre node (class emblem) with three coloured branches (orange / blue / green) fanning outward, many small round rank nodes joined by thin lines, the next ring of nodes further out; a left column lists the trees (with progress), a right panel shows the hovered node + points; dark navy panel, gold trim. Matches our Nexus-of-the-Void plan above (centre = the black hole, branches = skills). Use it when the Nexus page gets its visual pass (Menu-Pattern rules still apply). Skyy is playing Hylterium for more visuals to learn from (look only - never copy their art).
