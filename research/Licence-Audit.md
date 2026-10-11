# Licence audit - can SkyWynn fold third-party mods into its own modules? (2026-10-10)

Skyy: "if others mods dont restrict it, fold them into the pack too, then we can build, edit and update ontop of it (give credit in the mods readme)."
"Fold" = copy their files / code, modify them, and redistribute them inside OUR jars (Architecture-Spec.md module list). Running their
unmodified jar next to ours (what PACK.md does today) needs no folding and is a different, much easier question.

How checked: (1) each archive in Skyy's Mods folder opened read-only in memory (python zipfile; nothing extracted or written) - manifest
fields and any LICENSE / NOTICE / README file; (2) the CurseForge page's License field and Permissions text (fetched 2026-10-10), plus the
GitHub LICENSE where a source link exists. The CurseForge page is treated as the licence of record; the jar almost never carries one.
**This is a plain-language reading, not legal advice.** Our own repo has no LICENSE file yet (see section 5).

## 1. Result at a glance

| Fold verdict | Mods |
|---|---|
| YES (MIT / PD / CC BY) | Multitools, VeinMining, Mining Hammers and Excavators, Lucky Mining, Lootr, Spawn Manager (+Assets), AffixPlus (Public Domain), Bio's Kobolds (CC BY 4.0) |
| YES-NC (CC BY-NC) | The Armory (CC BY-NC 3.0) |
| SHARE-ALIKE (GPL-3.0) | Better Mob Expansion (+ Humans), Saplings From Trees, Alec's Tamework (GPL + 7(b) credit), Alec's Animal Husbandry (GPL + 7(b) credit), Angler's Almanac, Better Tools Expansion - Grappler |
| NO - AGPL | BetterMap |
| NO - All Rights Reserved, modpack/pack use stated | NoCube's Orchard, Rare Monsters, Dragon Nestkeeper ("made for use in any modpacks"), Endgame&QoL (run + credit + link; no copying) |
| NO - All Rights Reserved, nothing stated | Dynamic Seasons, More Crossbow Tiers (+ Endgame&QoL Crossbow Tiers add-on), HyFishing, Adathan's Boss Library / Void Asylum / Steamwrought Tomb / Tower of Shiva, Aegos, Ancient Constructs, Forgotten Creatures, Arcane Power, YUNG's HyDungeons, Welkin, PJ-HyperPickaxes, Aetherhaven |

## 2. Table per mod

"Jar" = what the archive in Skyy's Mods folder contains. "Page" = CurseForge. Credit text is what to put in the mod's README (and, where the
author asks, the pack description + a visible server credit / MOTD).

### 2.1 In the pack today / switched off but kept (PACK.md, deploy_set PACK_THIRD_PARTY / PACK_DISABLED)

| Mod (version) | Author | Licence (exact; where found) | Fold? | Credit text needed |
|---|---|---|---|---|
| Dynamic Seasons 6.1.4 (jar; PACK.md says 6.1.2) | BlueOrbit | "All Rights Reserved". Page only; no LICENSE in the jar (manifest has a placeholder email `your.email@example.com`). No permission text. | NO - ask | none required (no grant). Ask BlueOrbit for a written OK before relying on it in a published pack; link the page in PACK.md. |
| BetterMap 1.3.8 | Paralaxe + Theobosse (ninesliced) | "GNU Affero General Public License version 3 (AGPLv3)". Page; source https://github.com/ninesliced/Hytale-BetterMap. No LICENSE in the jar. | NO (AGPL network clause) - keep separate, clean room stays | Link in PACK.md: "BetterMap by Paralaxe and Theobosse (ninesliced), AGPL-3.0, https://www.curseforge.com/hytale/mods/bettermap". |
| Better Mob Expansion 3.5 (+ Humans 1.2) | Frah | "GNU General Public License version 3 (GPLv3)". Page "Legal & Usage": "You are free to use, modify, and redistribute Better Mob Expansion, any derivative work must remain open source under the same license." No LICENSE in the jar. | SHARE-ALIKE | "Better Mob Expansion by Frah - https://www.curseforge.com/hytale/mods/better-mob-expansion" in the pack description AND a visible server credit (MOTD / credits page); keep the in-mod credits. Humans: separate page `better-mob-expansion-humans`, not fetched; assume the same. |
| Multitools 1.2.9 | InkBlindCat (jar); page team "The Multitools Team" | "MIT License". Page Details. No LICENSE in the jar. | YES (keep the MIT notice + copyright line) | "Multitools by InkBlindCat - MIT License - https://www.curseforge.com/hytale/mods/multitools". Copy the MIT text into our NOTICE file. |
| More Crossbow Tiers 1.1.0 | Serj (SergioGMN) | "All Rights Reserved". Page; no permission text. Jar: no LICENSE. | NO - ask | none; courtesy credit "More Crossbow Tiers by SergioGMN". |
| Saplings From Trees 1.0.4 | rex8112 (manifest group "Helios") | "GNU General Public License version 3 (GPLv3)". Page; no extra terms; no LICENSE in the jar. | SHARE-ALIKE | "Saplings From Trees by rex8112 - GPL-3.0 - https://www.curseforge.com/hytale/mods/saplings-from-trees". |
| [NoCube's] Orchard 0.0.2 | NoCube | "All Rights Reserved" with Permissions: "You are allowed to include this mod in modpacks and use this mod in your videos." "A link to the mod page in the description is highly appreciated." NOT allowed: reupload elsewhere, "use any contents of this mod (models, textures, data, etc) in other projects", "sell this mod in any way or include in paid modpacks". Page; no LICENSE in the jar. | NO - keep as separate pack mod (already done) | Link https://www.curseforge.com/hytale/mods/nocubes-orchard-hytale in the pack description. |
| The Armory 1.22.0 (OFF) | LadyPaladra (team Larsonix, S3B4S5C, ScarForges) | "Creative Commons Attribution-NonCommercial 3.0 Unported". Page; FAQ: modpacks "Yes, under the licence ... CC BY-NC"; "Credit The Armory and do not sell it." No LICENSE in the jar. | YES-NC | "The Armory by LadyPaladra (with Larsonix, S3B4S5C, ScarForges), CC BY-NC 3.0, https://www.curseforge.com/hytale/mods/the-armory. Modified by SkyWynn: <what changed>." Name author, title, URL, licence link, and say we changed it. |
| HyFishing 0.6.8 (OFF) | TheRedlotus | "All Rights Reserved". Page; no permission text; no LICENSE in the jar. | NO | none; link in PACK.md while it is installed. |

### 2.2 Proposed / planned (surveys and reviews)

| Mod | Author | Licence (exact; where found) | Fold? | Credit text needed |
|---|---|---|---|---|
| Angler's Almanac 1.2.1 | RM20 (+ CapnSloth) | "GNU General Public License version 3 (GPLv3)". Page and GitHub (https://github.com/rm20killer/Anglers-Almanac, "GPL-3.0 license", GPL text). Jar root LICENSE is Lombok's (MIT) and the jar bundles Apache-2.0 sqlite-jdbc; none of that is the mod's own licence. | SHARE-ALIKE (and SkyyFishing replaces it, so little reason to) | "Angler's Almanac by RM20; original Stardew-style fishing mod by CapnSloth; art ColdLavenderSun - GPL-3.0 - https://www.curseforge.com/hytale/mods/anglers-almanac". |
| Alec's Tamework! 5.2.1 | Alechilles | Page field: "Custom License" (link not readable); page description + GitHub LICENSE.txt: "licensed under the GNU General Public License v3.0 (GPL-3.0)" with Section 7(b) attribution: any distributed version or derivative "must give credit to "Alec's Tamework!" by Alechilles" in a listing/description and/or documentation. Jar: no LICENSE (only third-party sqlite licences). | SHARE-ALIKE + mandatory credit | "Alec's Tamework! by Alechilles (GPL-3.0 with attribution) - https://www.curseforge.com/hytale/mods/alecs-tamework". |
| Alec's Animal Husbandry 4.0.1 | Alechilles | Page: "Custom License". GitHub LICENSE.txt (Alechilles/AlecsAnimalHusbandry): "GNU General Public License v3.0 (GPL-3.0)" + Section 7 attribution: credit "Alec's Animal Husbandry!" by Alechilles. Jar: no LICENSE (README only). | SHARE-ALIKE + mandatory credit | "Alec's Animal Husbandry! by Alechilles (GPL-3.0 with attribution) - https://www.curseforge.com/hytale/mods/alecs-animal-husbandry". Also needs Tamework (hard dependency). |
| Adathan's Boss Library 1.0.8 | Adathan | "All Rights Reserved". Page; no permission text. Jar: no LICENSE. | NO - ask | none until Adathan answers. |
| Void Asylum 1.1.4 | Adathan | "All Rights Reserved". Page; credits Fyrrage (Warden armor) and Bayms (death animation) - their parts have their own owners. | NO - ask | none until answered; if allowed, also credit Fyrrage + Bayms. |
| The Steamwrought Tomb 1.2.2 | Adathan (+ AVeryAngryGardenGnome) | "All Rights Reserved". Page; page header says "BROKEN AS OF UPDATE 3: JAVA OUT OF MEMORY ERROR". | NO - ask | none. |
| Tower of Shiva 1.5.1 | Adathan | "All Rights Reserved". Page. | NO - ask | none. |
| Aegos 1.7.0 | Zbeve | "All Rights Reserved". Page (slug aegos-seeking-bow, team "Aegos - Seeking Bow Team"); jar: no LICENSE. | NO - ask | none. |
| Ancient Constructs 1.2.3 | DanBagh (+ MAJOR76 artist) | "All Rights Reserved". Page; no permission text. Jar: no LICENSE (only Lombok and sqlite libs). | NO - ask | none. |
| Forgotten Creatures 1.3.1 | PedriJoe | "All Rights Reserved". Page; no permission text. Jar: no LICENSE. | NO - ask | none. |
| Arcane Power 3.2.0 | Tayko_Dev | "All Rights Reserved". Page; no permission text. Jar: no LICENSE. | NO - ask (draft in Author-Requests.md) | none. |
| Dragon Nestkeeper 28.08.2026 | BlackAures (BlackAuresArt) | "All Rights Reserved"; page text: "This mod should be compatible with everything by default. It's made for use in any modpacks." Jar: no LICENSE. | NO for folding; pack use is stated OK | link https://www.curseforge.com/hytale/mods/aures-dragon-nestkeeper |
| Rare Monsters 28.08.2026 | BlackAures | "All Rights Reserved"; Permissions: "You are allowed to include this mod in Curseforge modpacks and use this mod in your videos." Link "highly appreciated". NOT allowed: reupload elsewhere, use contents in other projects, sell, paid modpacks. Same "made for use in any modpacks" line. | NO (separate pack mod only) | link https://www.curseforge.com/hytale/mods/aures-rare-monsters |
| YUNG's HyDungeons 0.1.1 | YUNGNICKYOUNG (Refresh Studios) | "All Rights Reserved". Page; no permission text. | NO - ask | none. |
| Bio's Kobolds 1.3.2 | Bio_the_LizardWizard (+ MouseKnight) | "Creative Commons 4.0": the page's licence link reads "Creative Commons Attribution 4.0 International Public License" = CC BY 4.0. Jar: no LICENSE. | YES | "Bio's Kobolds by Bio_the_LizardWizard, CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), https://www.curseforge.com/hytale/mods/bios-kobolds. Modified by SkyWynn: <what changed>." Link the licence, say what we changed. |
| Welkin 1.0.2 | wyvernling (manifest "Wyvern") | "All Rights Reserved". Page. | NO - ask (technique-only is fine: ideas are not copyrightable) | none. |
| PJ-HyperPickaxes 1.3.5 | PedriJoe | "All Rights Reserved". Page; no permission text. Jar: no LICENSE. | NO - ask (one message with Forgotten Creatures) | none. |
| VeinMining 2.4.0 | EineNT (+ Riprod, port) | "MIT License". Page; GitHub https://github.com/aaronpostels/VeinMining shows "MIT license" (copyright holder line not read; the repo owner differs from EineNT - read the LICENSE file before copying). Jar: no LICENSE. | YES (keep notice) | "VeinMining by EineNT (and Riprod) - MIT License - https://www.curseforge.com/hytale/mods/veinmining". |
| Mining Hammers and Excavators (web only) | DanielBelmes (owner) + Toekimi | "MIT License". Page. Needs Daniel's Interactions Library - its licence NOT checked. | YES for the mod; library unchecked | "Mining Hammers and Excavators by DanielBelmes and Toekimi - MIT License - https://www.curseforge.com/hytale/mods/excavatorsandhammers". |
| Lucky Mining 1.0.7 | Buuz135 | "MIT License". Page. Jar: no LICENSE. | YES (keep notice) | "Lucky Mining by Buuz135 - MIT License - https://www.curseforge.com/hytale/mods/lucky-mining". |
| AffixPlus (web only) | traecneh | "Public Domain". Page; no further text; not in Skyy's folder, so no jar check. | YES (no credit legally needed; give it anyway) | "AffixPlus by traecneh (Public Domain) - https://www.curseforge.com/hytale/mods/affixplus". Fetch the licence page / repo once to confirm a CC0-style dedication before copying. |
| Endgame&QoL 5.4.2 | Lewaii (models ReyZ41, BoundlessBuild) | "All Rights Reserved". Jar META-INF/LICENSE: "Copyright (c) 2026 Lewai. All rights reserved ... No part of this work may be copied, modified, distributed, sold, sublicensed, published, mirrored, decompiled ..." Page: "The compiled JAR is free to install and run on any Hytale server"; no copy/modify/redistribute/derivative works without written permission; modpacks include the CurseForge link; servers visibly mention "Endgame & QoL" (description / MOTD / Discord); "Don't remove credits from the mod files." Also bundles LGPL-3 HyUI and MIT hytaleuiparser / jsoup / multiplehud licences (their own, separate). | NO - keep separate; if ever run, follow the credit rule | "Endgame & QoL by Lewaii - https://www.curseforge.com/hytale/mods/endgame-qol" in the pack description AND server MOTD / Discord. |
| Aetherhaven 3.2.1 | Hexvane (+ ArmandVestibule, Mertie) | "All Rights Reserved". Page; jar: no LICENSE. | NO (design reference only) | none. |
| Better Tools Expansion 1.0 (Grappler) | Frah | Page `better-tools-expansion-grappler`: "GNU General Public License version 3 (GPLv3)". Jar: no LICENSE. (Tool-Mods-Survey said "not stated" - now resolved.) | SHARE-ALIKE (one item; we have our own grapple) | "Better Tools Expansion - Grappler by Frah, GPL-3.0". |
| Endgame&QoL expansion - Crossbow Tiers 1.4 | Frah | Page `more-crossbow-tiers-and-prisma-bow`: "All Rights Reserved"; needs More Crossbow Tiers (also ARR). | NO | none. |
| Alec's Tamework! / Animal Husbandry | see 2.2 rows above | | | |
| Others seen in the same surveys | | Lootr (Noobanidus): MIT, page + survey. Spawn Manager + Assets (ReignInBlood): MIT per survey (jar bundles Netty / Jackson / FastDoubleParser notices only; the CurseForge page was not re-fetched). Skip both as pack mods; Lootr is foldable. | YES | "Lootr by Noobanidus - MIT". |

## 3. Where the page and the jar (or our docs) disagree

1. No jar in the folder carries the mod author's own licence file except Endgame&QoL (which matches its page: All Rights Reserved). Every other
   result comes from the CurseForge page only; a jar with no LICENSE file is NOT "free to copy".
2. Dynamic Seasons: PACK.md says "No licence file in the jar" - the page says All Rights Reserved. PACK.md also lists 6.1.2; the folder has 6.1.4.
3. Saplings From Trees: PACK.md gives no licence - the page says GPLv3.
4. Alec's Tamework and Animal Husbandry: the page field says "Custom License"; the description / GitHub LICENSE.txt say GPL-3.0 + a Section 7
   attribution term. Read it as GPL-3.0 with a mandatory credit.
5. Better Tools Expansion (Grappler): Tool-Mods-Survey said "not stated" - the page says GPLv3.
6. Rare Monsters: the survey said only "ARR but made for use in any modpacks" - the page also lists what is NOT allowed (reuse of contents, selling, paid modpacks).
7. Multitools: the jar names InkBlindCat; a web search listing showed the page under "The Multitools Team". The page's licence field is MIT; the team name was not otherwise checked.
8. VeinMining: page byline EineNT, but the linked GitHub repo belongs to account aaronpostels; confirm the copyright line in that repo's LICENSE before copying code.
9. Steamwrought Tomb: page header says BROKEN (out-of-memory error) - do not rely on it.
10. Bio's Kobolds: the page's licence label is only "Creative Commons 4.0"; the licence page shows Attribution 4.0 (BY), so CC BY.

## 4. What the licences mean for our repo

- **MIT / Public Domain / CC BY (YES):** we may copy, change and ship them inside any module, including a private fork or a public CurseForge
  release, under our own licence. Only duty: keep the notice / credit / licence link (CC BY: say what we changed). Put the copyright + MIT text
  in a third-party-notices section of the module README and the credit line in the mod README.
- **CC BY-NC 3.0 (The Armory):** allowed, but anything that contains Armory files becomes non-commercial: never sold, and Skyy should not put it
  behind paid ranks / a store. It is also incompatible with the GPL (a jar cannot mix NC and GPL content). Keep the Armory content in its own asset
  module so SkyyGear's code and the public CurseForge releases (Skyy Menu, Accessories) stay free of the NC restriction.
- **GPL-3.0 (SHARE-ALIKE):** folding GPL files into a jar makes that whole jar a GPL-3.0 work: its source (our module's code + assets, in
  the preferred editable form) must be offered under GPL-3.0 to everyone who gets the jar, and nobody may add stricter terms. Our repo is public,
  so offering source is easy, but the licence of the whole module flips to GPL-3.0 (we could not later relicense or sell it closed). Keeping the
  GPL mod as a separate jar in the pack (PACK.md today) or reacting to its ids at runtime does not trigger this. Alechilles' two mods add a
  mandatory credit; BME adds a mandatory pack-description + server credit.
- **AGPL-3.0 (BetterMap):** same as GPL plus the network clause (users of a server running it can demand the source) - treated as NO. The clean-room
  minimap in SkyyHud stays clean-room.
- **All Rights Reserved:** no copying, editing or redistribution without the author's written OK. Not even a folded copy of one JSON file. Ideas and
  mechanics are free to rebuild in our own words, items and numbers.
- Our repo has no LICENSE file. If any GPL content is ever folded, the module needs one (GPL-3.0); until then pick one (suggest MIT for the Skyy* code)
  so that others know where they stand.

## 5. Recommendation

**Fold now (no ask, permissive), into the planned modules:**
- Multitools (MIT) -> **SkyyGear** (tools ladder; today SkyyGear already rewrites its recipes at runtime - folding lets us just edit the item files) or **SkyyProfessions** if Skyy wants all gathering tools there.
- VeinMining (MIT), Lucky Mining (MIT), Mining Hammers and Excavators (MIT; check Daniel's Interactions Library licence first) -> **SkyyProfessions** (special-tool abilities in Tool-Mods-Survey section 5).
- AffixPlus (Public Domain; confirm the dedication) -> **SkyyGear** (roll / modifier ideas on top of our rarity system).
- Lootr (MIT) -> **SkyyWorld** (per-player chest loot).
- Bio's Kobolds (CC BY 4.0) -> **SkyyWorld** (kobold roles / caravan merchants) or **SkyyEconomy** (roaming merchants). Credit in the README; say what changed.
- The Armory (CC BY-NC 3.0) -> a separate **Armory asset module** (not inside SkyyGear's code jar) so the NC rule stays contained; SkyyGear keeps reading its item ids. Re-test after Hytale 0.7 (texture atlas overflow).

**Fold only with a share-alike decision by Skyy:** Better Mob Expansion, Saplings From Trees, Tamework, Animal Husbandry, Angler's Almanac, Grappler. Cheapest options: keep them as separate pack mods (zero licence cost); or put each in its own GPL-3.0 jar ("SkyyWorld-Mobs" for BME) with a LICENSE and credit. Do NOT fold them into SkyyWorld / SkyyGear / SkyyProfessions / SkyyPets - that would make the whole module GPL. Saplings From Trees is tiny (leaf drops + a few recipes): rebuild it ourselves in SkyyProfessions instead. For pets, borrow Tamework's design, not its files (as Tamework-Review.md decided).

**Keep separate (pack mod) because the licence allows pack use but not folding:** NoCube's Orchard (+ Undead Warriors, same terms), Rare Monsters, Dragon Nestkeeper, Endgame&QoL if ever run, BetterMap (AGPL).

**Needs an author ask before folding or relying on them in a published pack:** Dynamic Seasons (BlueOrbit - in the pack today with no stated grant; highest priority), More Crossbow Tiers (SergioGMN - same), HyFishing (off), Adathan (Library + Void Asylum + Steamwrought + Tower of Shiva, one message), PedriJoe (HyperPickaxes + Forgotten Creatures, one message), Tayko (Arcane Power), DanBagh (Ancient Constructs), YUNGNICKYOUNG (HyDungeons), Zbeve (Aegos), wyvernling (Welkin), Hexvane (Aetherhaven - skip). Drafts: research/Author-Requests.md and Tool-Mods-Survey.md section 7. In each ask say exactly: "may we copy and modify your files inside our free, public server pack, with credit?" - a "may be in modpacks" yes does not cover that.

**PACK.md fixes to make next (not done here):** record the real licence in each row (Dynamic Seasons ARR, Saplings GPLv3, Crossbow Tiers ARR), add the credit lines above, and add a third-party-notices section when the first MIT mod is folded.
