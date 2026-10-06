# NoCube + Aures mods survey (pack candidates)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: CLOUD-RESUME.md (task text), docs/answered/project.md (lines 35-40: Orchard LOCKED, Cultivation / Undead Warriors / Bakehouse / Culinary / Aures REQUESTS + NOTE), docs/log/2026-10.md (lines 127-130), research/Dragon-Pets-Idea.md, research/cloud/Dragon-Quest-Spec.md.
Web: the CurseForge pages are **blocked** from the cloud (WebFetch denied), so everything below comes from WebSearch snippets. Where a snippet did not give a fact it is marked **UNVERIFIED**. Permissions text could only be quoted where Skyy's own screenshots were written into docs/answered/project.md.

## 0. Decisions already locked (followed here)

| Decision | Source |
|---|---|
| NoCube's Orchard 0.0.2 is IN the pack. Page allows modpacks (link the page), forbids reuse of its contents. | docs/answered/project.md 2026-10-06 |
| Rule for every NoCube mod: modpacks OK with a link, **no modifying / reusing contents**. Our mods only reference item ids. | project.md 2026-10-06 (REQUEST lines) |
| Aures - Rare Monsters permissions: CurseForge modpacks only, link the page, no reupload elsewhere, no content reuse, no paid modpacks. | project.md NOTE 2026-10-06 |
| Angler's Almanac + HyFishing are NOT added; our own fishing takes their ideas. Dynamic Seasons IS added (owner installs from its author, no licence file). | project.md, skills.md 2026-10-06 |
| Advanced Farming dropped. Our own tools get its ideas. | project.md 2026-10-06 |
| Everything must install + get a local check (vanilla overrides, conflicts) before it joins the pack. | project.md REQUEST lines |

## 1. Every NoCube mod found (7 so far)

Author page: NoCube on CurseForge. Version history I could see: Culinary 0.0.2 (12 Jan 2026), Cultivation uploaded 19 Jan 2026. The author looks inactive: a fix mod says the originals "have not been updated for a long time".

| Mod | What it adds | Permissions | Last update / game version | Dependencies | Verdict |
|---|---|---|---|---|---|
| **Orchard** (in pack) | 9 fruit trees, saplings, fruit, Orchard Bench (tiers up to 3), Fruit Press, 17 juices, tree fertilizer | Modpacks OK with a page link; no use of contents (Skyy's screenshot) | 0.0.2; date UNVERIFIED | none known; the Tier 3 bench bug needs the fix mod (section 3) | **Keep** |
| **Cultivation** | Wooden / Copper / Thorium watering cans (Thorium holds 2x the iron can), fertilizers; "new uses for standard materials". 112.89 kB | **UNVERIFIED** (not in snippets; Skyy unsure). Assume the same NoCube rule | uploaded 19 Jan 2026; game version UNVERIFIED | none known | **Maybe** (section 2.1) |
| **Undead Warriors** | Night skeleton variants in Zone 1 main biomes: random armor / weapon / eyes, slightly stronger than vanilla, torches like vanilla skeletons, drops iron ore + linen scraps + bones | **UNVERIFIED** | date UNVERIFIED | none known; must be ticked in World Settings per world | **Maybe** (section 2.2) |
| **Bakehouse** | Workbenches with menus; dough (Corn, Rice, Fine); breads and pastries (Berry Croissant, Brioche, Coconut Bread, Fruitloaf, Rustic Bread). Skyy's screenshots add: Baker's Workbench, Hand Quern, Baker's Oven, Rolling Pin / Bread Peel / Flour Sieve, pies | **UNVERIFIED** (assume NoCube rule) | date UNVERIFIED | needs "Fix NoCube's Mods" (workbench menus did not open, wrong dough output blocked progression) | **Skip for now** (2.3) |
| **Culinary** | New dishes cooked at the vanilla Chef's Stove with buffs; **all food is placeable** decoration. 79.6K+ downloads | **UNVERIFIED** | **0.0.2, 12 Jan 2026** | none known | **Maybe** (2.4) |
| **Tavern** | Hops, brewing, rustic-kitchen / tavern decorations | **UNVERIFIED** | date UNVERIFIED | needs the fix mod (workbench menus). A "NoCube Tavern Fixed" repack also exists, see licence note in section 3 | **Skip** (drinks clash with POTION / FOOD plan) |
| **Simple Bags** | Bags that hold several items to save inventory space | **UNVERIFIED** | date UNVERIFIED | none known | **Skip** (clashes with SkyySacks) |

"Fix NoCube's Mods" is a separate third-party mod (needs **Hytalor**; servers must run with `--ignore-broken-mods`). It fixes Bakehouse (menus, dough), Orchard (menus, Tier 3 bench recipe list) and Tavern (menus). Not by NoCube.

## 2. Fit and clash with our mods

### 2.1 Cultivation
- Fit: our plan has own watering cans in the tool-levels round (Advanced Farming ideas). Cultivation does the same job with the same metal names (Copper, Thorium), so it would **overlap and may clash** with our Tool-Levels metal bands (Copper 10-18, Thorium 20-28): its cans have no levels or collection gates.
- Clash: the Bazaar / collections list by item id, so cans would be sellable and unlockable only if we add them by hand. R3 says NPC shops never sell unlocks.
- Recommend: **maybe, lean skip.** Build our own cans (idea only, no reuse needed). Add only if its page allows modpacks, and then gate the recipes behind our collections with a recipe-override mod (**UNVERIFIED** whether the NoCube rule lets us edit its recipes: "no modifying" says no).

### 2.2 Undead Warriors
- Fit: more Zone 1 variety. Clash: SkyyMobs gives mobs levels by zone band (Z1 1-20). These are unknown NPC ids, so SkyyMobs would need to level them by role or id **(UNVERIFIED: does our leveller handle unknown NPCs?)**. Their drops (iron ore, linen scraps, bones) are vanilla ids, so no collection break. Iron ore from Z1 is above our Iron band (15-23) at low level: a progression leak unless drops are overridden, which we may not do.
- Recommend: **maybe.** Add only after a local check: does SkyyMobs level them, does iron ore from level 1-10 mobs break the metal gates. If yes, skip.

### 2.3 Bakehouse
- Overlaps SkyyCooking (our cooking system, food families, Flour XP). Its dough / bread items would be ids our cooking and Bazaar do not know, and it brings its own benches (Baker's Workbench) next to the Chef's Stove. Two bread paths split the Flour XP line. Needs a third-party fix mod plus Hytalor.
- Recommend: **skip**. Take the idea (Hand Quern, dough tiers, pies) into our Food expansion draft. If Skyy insists: only with the fix mod, and list its breads as a food family by id.

### 2.4 Culinary
- Fits the Chef's Stove, so it adds to vanilla instead of making a new bench. Its dishes carry their own buffs, which clash with the new rule that **food is the primary healing** and our grades (HP / Mana / Stamina by family). Its buffs ignore our Grade system and could outheal ours.
- Placeable food is a nice decoration idea.
- Recommend: **maybe.** Add only if SkyyCooking can read foreign food ids into a family and grade (**UNVERIFIED**: does it key off item id or a tag?). Otherwise skip and make our own dishes.

### 2.5 Orchard (already in)
- Fruit = Mana family by id. Juices should be added to the Bazaar list by id (buy=base*1.10, sell=base*0.90). Juices are crafted at the Fruit Press from fruit, so check the crafted premium stays under the 22.2% spread (arithmetic: 1.10 / 0.90 - 1 = 22.2%; verified).
- Needs the Tier 3 bench fix to unlock the full tree: the fix mod above, or confirm if 0.0.2 has the bug **(UNVERIFIED)**.

### 2.6 Tavern and Simple Bags
- Tavern: brewing makes drinks that overlap the potion design (flat numbers by grade). Skip.
- Simple Bags vs **SkyySacks**: both store items to save space. Two bag systems confuse players and Sacks tie into collections / Bazaar. Skip.

## 3. Aures mods (BlackAuresArt)

Author makes: **Aures - Rare Monsters**, **Aures - Dragon Nestkeeper**, **Aures - Livestock Skins** (cosmetic, 150+ animal variants) and a horse-skins mod. Permissions for Rare Monsters = CurseForge modpacks only (locked line above). Permissions for the other three: **UNVERIFIED**, check each page's Permissions box.

| Mod | What it adds | Last update | Dependencies | Verdict |
|---|---|---|---|---|
| **Rare Monsters** | 8 NPCs: Strange Rabbit, Cursed Bear, Silver Horn, Golden Antelope, Monster Bat, Rusted Machine, Snow Werewolf, Young Snow Werewolf. Rewards: **riding werewolf**, summonable ally wolves, glowing helmets, decorations, armor, loot. 36.6K+ downloads | 27 May 2026 (game version UNVERIFIED) | none known | **Maybe, good** |
| **Dragon Nestkeeper** | Find destroyed / abandoned nests, hatch dragons, **4 growth stages** (each stage a specific food), ride when grown, Nestkeeper Bench, Saurian Trader Statue (saurians buy / sell dragon items), lore-based, "rude-free" taming | version UNVERIFIED | none known | **Skip as a base; maybe as inspiration** |
| **Livestock Skins** | Cosmetic variants of animals | UNVERIFIED | UNVERIFIED | **Maybe**, harmless if it only swaps models |

### 3.1 Rare Monsters vs our mods
- **SkyyMobs levels:** 8 new NPCs need levels in the right zones (Snow Werewolf fits Z3 Whisperfrost 30-45). Same open question as Undead Warriors: does SkyyMobs level foreign NPC ids? **UNVERIFIED.**
- **SkyyGear loot / levels:** its armor, glowing helmets, weapons and loot have no level, rarity (Normal..Mythic, Set) or metal band. They would be an **unleveled gear lane**: a Lv 1 player could wear a "rare" helmet, and our Armor-Types design (light / medium / heavy) knows nothing about them. Fix by gating the fights by zone (they are rare spawns, so gates are soft) or by hiding the gear from the Bazaar. We cannot edit them (no content reuse).
- **Pets:** companions and mounts overlap research/cloud/Pets-Spec.md (one pet system, summon slot, Mythic dragons). A riding werewolf outside the pet system is a second mount line. **Clash risk.**
- **Fun fit:** "rare monsters" match our elite / event idea (Elites-Events-Spec). Department of Arrivals joke: they are "unregistered arrivals".
- Recommend: **maybe**. Add only after the local check of (a) SkyyMobs leveling, (b) the gear lane, (c) the pet clash. Link the page in PACK.md.

### 3.2 Dragon Nestkeeper vs our dragon plan
| Topic | Ours (Dragon-Pets-Idea + Dragon-Quest-Spec) | Nestkeeper |
|---|---|---|
| Source | Zone 5 boss gives a bound egg, one per profile | Nests found in the world, any player |
| Hatch | Quest line, chosen element (5 + 4 secret) | Hatch from a nest egg, no elements (**UNVERIFIED**) |
| Growth | By pet level (pet rules), flight from Lv 10 | 4 stages by food |
| Flight | Dragon only, no /fly | Ride and fly when grown |
| Trade | Dragon Upgrade Stones | Saurian trader buys and sells |
- **Clash:** two dragon systems on one server (ours would be a second mount line, with different growth and no profile binding). Per-profile data (tools/PROFILES-CONTRACT.md) does not apply to Nestkeeper's data.
- **Idea take:** food per growth stage, saurian traders (could be a Zone 5 NPC joke), abandoned nests as loot sites. Put these into the dragon spec as ideas; no reuse of their content.
- Recommend: **skip as a pack mod** (keeps our "one dragon per profile, elements, pet rules"). Revisit if Skyy wants a free-roaming dragon content mod.

## 4. What "CurseForge modpacks only" means for SkyWynn (not legal advice)

**Reading:** the authors allow their mod to be included in a modpack that is published on CurseForge, with a link to the mod page. They do not allow re-hosting the jar anywhere else (GitHub, Discord, our server's download page). CurseForge's own 3rd-party setting lets authors choose whether their files can be distributed outside CurseForge.
Sources: [CurseForge 3rd-party distribution / modpack rules](https://support.curseforge.com/support/solutions/articles/9000197908), [CurseForge modpack requirements](https://support.curseforge.com/support/solutions/articles/9000197279). The same pages say that **override mods** (files bundled inside a pack) must be MIT / GPL-like; mods with "link back" or personal permissions will not be accepted. So the safe form is a pack that lists mods by CurseForge project ID and the launcher downloads each from CurseForge.

Our situation: the repo is PUBLIC and holds our own `Skyy*` mods only. Third-party jars are never committed (PROJECT-RULES section 2). PACK.md + PACK_THIRD_PARTY already say "the owner installs it from its author".

| Option | What it is | Fits "CurseForge modpacks only"? | Cost / risk |
|---|---|---|---|
| A. **Links only (today)** | PACK.md lists each third-party mod + page link; the server owner installs them from CurseForge | Yes. Nothing is re-hosted by us | Owner does manual work; versions drift |
| B. **CurseForge modpack** | A pack on CurseForge listing the third-party mods by project ID plus our Skyy jars as overrides | Yes, the intended route. Our own jars as overrides are ours to license | Needs a CurseForge pack project, review, a manifest that tracks our SET versions; Hytale pack support **UNVERIFIED** |
| C. **Server-side auto-installer** | A script that downloads each mod from CurseForge for the owner | Grey. CurseForge's API terms and the 3rd-party toggle apply; the downloader must use the official API | Needs an API key (never commit); may break per author |
| D. **Bundle the jars in our repo or releases** | Ship third-party jars with our download | **No** for modpacks-only mods (no reupload elsewhere) | Do not do this. Also breaks the "never commit other authors' files" rule |

Rules for all options: link every mod page in PACK.md; no paid pack or paid server perk tied to these mods (their text says no paid modpacks); our mods only reference their item ids; no edits to their files; re-check each page's Permissions box before adding (authors can change it).
**Recommendation:** keep A now, plan B as the real shipping format once the pack settles (Skyy's call, section Questions).
Related: if a mod has **no licence at all** (Dynamic Seasons, HyFishing jars) then you may not redistribute it; option A covers that too. The "NoCube Tavern Fixed" repack and the fix mod are by other authors: check their own permissions before relying on them.

## 5. Summary table (recommendation)

| Mod | Rec | Reason in one line |
|---|---|---|
| Orchard | keep | already in; list juices in Bazaar by id |
| Cultivation | maybe / lean skip | overlaps our own cans; permissions UNVERIFIED |
| Undead Warriors | maybe | needs SkyyMobs leveling + iron ore gate check |
| Bakehouse | skip | clashes with SkyyCooking / Flour XP; needs fix mod |
| Culinary | maybe | vanilla Chef's Stove; buffs must fit our grades |
| Tavern | skip | drinks clash with potion plan |
| Simple Bags | skip | clashes with SkyySacks |
| Rare Monsters | maybe | adds a lot; gear and mounts need gating |
| Dragon Nestkeeper | skip (ideas only) | clashes with our dragon plan |
| Livestock Skins | maybe | cosmetic only, check permissions |

## For the local session (UNVERIFIED)

1. Open each CurseForge page and copy the **Permissions box** word for word (Cultivation, Undead Warriors, Bakehouse, Culinary, Tavern, Simple Bags, Dragon Nestkeeper, Livestock Skins). Add to docs/answered/project.md.
2. Last update + game version + dependencies of every mod (snippets gave few dates).
3. Does Orchard 0.0.2 have the Tier 3 bench bug? Do the workbench menus open?
4. Does SkyyMobs level NPC ids it does not know (Undead Warriors, Rare Monsters)? Do they spawn in the right zones?
5. Do Rare Monsters armor / weapon items clash with SkyyGear (level, rarity, Armor Types)? Do they override any vanilla ids?
6. Does SkyyCooking read food families / grades from item id or tag, so Culinary dishes can be placed?
7. Does Undead Warriors' iron ore drop break the Iron band 15-23?
8. Does Hytale / CurseForge support a pack format with overrides for option B?
9. Which ids Orchard adds (fruits, juices) for the Bazaar and collections lists.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Ship the pack as option A (links) or build a CurseForge modpack (option B)? | A now, B later |
| 2 | Cultivation: build our own watering cans or add NoCube's? | Our own |
| 3 | Add Culinary if SkyyCooking can grade its dishes? | Maybe after the local check |
| 4 | Add Rare Monsters even though its gear is unleveled? | Yes only after the local check, gear gated by zone |
| 5 | Skip Bakehouse, Tavern, Simple Bags and Dragon Nestkeeper? | Skip all four; take the ideas |
| 6 | Add Undead Warriors for Zone 1? | Maybe, after the iron ore check |

## Sources
- [NoCube mods search results (Tavern, Orchard, Culinary, Bakehouse, Cultivation, Simple Bags)](https://www.curseforge.com/hytale/mods/fix-nocubes-mods)
- [Fix NoCube's Mods (CurseForge)](https://www.curseforge.com/hytale/mods/fix-nocubes-mods)
- [NoCube's Culinary (CurseForge)](https://www.curseforge.com/hytale/mods/nocubes-culinary-hytale)
- [NoCube's Bakehouse (CurseForge)](https://www.curseforge.com/hytale/mods/nocubes-bakehouse-hytale)
- [NoCube's Tavern files (CurseForge)](https://www.curseforge.com/hytale/mods/nocubes-tavern-hytale/files/all)
- [Cultivation snippet (vgtimes mirror)](https://vgtimes.com/games/hytale/files/91149-kmetijstvo.html)
- [Undead Warriors snippet (vgtimes mirror)](https://vgtimes.com/games/hytale/files/91155-nezhit-voiny.html)
- [Aures - Dragon Nestkeeper](https://www.curseforge.com/hytale/mods/aures-dragon-nestkeeper)
- [Aures - Rare Monsters gallery](https://www.curseforge.com/hytale/mods/aures-rare-monsters/gallery)
- [CurseForge modpack rules](https://support.curseforge.com/support/solutions/articles/9000197279), [third-party distribution](https://support.curseforge.com/support/solutions/articles/9000197908)
