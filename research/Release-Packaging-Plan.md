# Release packaging plan - 2026-10-14

How to hand SkyWynn to other server owners. Sources read: `tools/deploy_set.py` (SET, RETIRED, PACK_THIRD_PARTY, PACK_DISABLED), `PACK.md`, `research/Licence-Audit.md`,
`PROJECT-RULES.md` section 2, `.gitignore` (jars are ignored: "Releases get the jar attached instead"), `LICENSE` (MIT, 2026 SkyyPlayz), `Desktop\Hytale mods WORK\Your new mods\`
(the old Skyys-Modpack 1.5.0 single-jar release and its ReadME.txt). Nothing was built or published.

## 0. Short version

1. **Ship a "server pack" zip on GitHub Releases, not a bundled modpack.** Our 36 production jars are ours (MIT repo) and can be attached; every third-party mod stays
   "install from CurseForge" (PACK.md rule, and every one that matters is All Rights Reserved or AGPL / GPL).
2. **Do not ship the probes or retired mods.** SET still contains `SkyyAbilityProbe`, `SkyyUiProbe`, `SkyyUiProbeB` (test-only, op commands); they must be excluded.
3. **The one real blocker is not packaging, it is rights:** Dynamic Seasons and More Crossbow Tiers are in the pack with no stated modpack grant (Licence-Audit: "highest
   priority" ask); a public pack that REQUIRES them depends on authors who have not said yes. Plan: list them as optional until each author agrees.
4. **A CurseForge modpack is a second step.** Whether CurseForge accepts a Hytale modpack project that depends on our jars (hosted as separate CurseForge mod projects) is
   UNVERIFIED; cheapest sequence is GitHub release first, CurseForge mod pages for the jars later.
5. **Built jars may contain vanilla-derived data generated at build time** (icons, item JSONs read from `Assets.zip`; PROJECT-RULES: "generate them into the jars at build
   time"). Skyy should confirm this is fine to redistribute before the first public jar (question 2).

## 1. What goes in the release

| Group | Items | Rule |
|---|---|---|
| Our jars (production) | every `("SkyyX", "ver")` in SET except the three probes: about 36 jars | built jars from each mod folder (`SkyyX/SkyyX-<ver>.jar`), pinned by SET |
| Never ship | `SkyyAbilityProbe`, `SkyyUiProbe`, `SkyyUiProbeB` (SET), everything in RETIRED (SkyyRolls and the probes) | dev only |
| Third-party, install from CurseForge | Serj More Crossbow Tiers, NoCube's Orchard, IBC Multitools, BlueOrbit DynamicSeasons, dev.ninesliced BetterMap, narwhals Perfect Parries (PACK_THIRD_PARTY, all ON) | a text file lists name, author, tested version, link; the pack never contains their files |
| Third-party, off | TheArmory, HyFishing, Saplings From Trees, Better Mob Expansion (PACK_DISABLED) | not listed as required; say "optional, off by default" or leave out until 0.7 works |
| Config | world `config.json` fragment (our mod keys on, third-party keys), our `Skyy_*` default configs are written by the mods themselves at first start | ship NO data folders (no player files, no balances); the mods create their defaults |
| Docs | `README-INSTALL.txt`, `CREDITS.txt`, `LICENSES/` folder, `VERSIONS.json` | see section 4 |

## 2. Format options

| Option | What it is | Pros | Cons | Verdict |
|---|---|---|---|---|
| A. Server pack zip (GitHub Release) | `SkyWynn-<ver>-server.zip`: `Mods/` with our jars, a `world-config-snippet.json`, install + credits text, checksums | simple, we control it, no third-party files, works today | the owner installs 6 CurseForge mods by hand | **do this first** |
| B. Single mega-jar (like the old Skyys-Modpack 1.5.0, 33 mods in one file) | one jar | one tick in world setup | folds other authors' files into a redistributed jar - not allowed for the ARR / GPL mods (Licence-Audit); only OK for our own code | NO for the pack; fine later for our own ~10-jar merge (ARCHITECTURE item 6) |
| C. CurseForge modpack project | pack manifest listing CurseForge mod project ids | the usual way players install packs | needs our jars as CurseForge mod projects first; Hytale modpack support / format UNVERIFIED | **later** |
| D. Launcher profile import | N/A | - | UNVERIFIED that a Hytale launcher import exists | skip |

## 3. Third-party handling (PACK.md rule: install from CurseForge only)

| Mod | Licence (Licence-Audit) | In the release as |
|---|---|---|
| Multitools (IBC) | MIT | link + credit "InkBlindCat"; may be folded later |
| NoCube's Orchard | All Rights Reserved, modpacks allowed on its page (no paid packs) | link + credit; free pack only |
| BetterMap | AGPL-3.0 | link + credit; never bundled; our minimap reads only its packets |
| Perfect Parries | All Rights Reserved | link only; our world config tuning is written at deploy (`tune_perfect_parries`) - the release needs a tiny helper script or the tuning is skipped |
| Dynamic Seasons | All Rights Reserved, nothing stated | **ask first**; list as "recommended" not "required" |
| More Crossbow Tiers | All Rights Reserved, nothing stated | **ask first**; our crossbow handling in SkyyClasses / Gear only reacts to the ids |

`PACK.md` fixes pending (from Licence-Audit, not done): real licence in every row, credit lines, a third-party-notices section when anything is folded.
Credits text for the release README: GPL-3.0 mods need name + link; Orchard asks credit; BME is off. A server credit / MOTD line is required for Better Mob Expansion only if it is turned on.

## 4. Manifest and files

`VERSIONS.json` (generated from SET, not hand written):

```
{ "pack": "SkyWynn", "version": "0.9.0", "built": "2026-10-20T12:00:00Z", "game": "0.7.1",
  "mods": [ {"name":"SkyySkills","version":"0.4.35","file":"Mods/SkyySkills-0.4.35.jar","sha256":"..."} , ... ],
  "third_party": [ {"key":"IBC:Multitools","author":"InkBlindCat","tested":"1.2.9","url":"https://www.curseforge.com/hytale/mods/...","licence":"MIT","required":true} ],
  "rollback_floors": "copied from tools/deploy_set.py comments (text)" }
```

| File | Content |
|---|---|
| `README-INSTALL.txt` | 1. install the six CurseForge mods, 2. copy `Mods/*.jar`, 3. merge the config snippet into the world `config.json`, 4. start the world once, 5. open the SkyWynn Menu, Server Setup for every number. Plain English, 20 lines |
| `CREDITS.txt` | one line per third-party mod (author, link, licence) + "built with javassist, Hytale (c) Hypixel Studios" |
| `LICENSES/` | our MIT LICENSE, `javassist` licence (MPL / LGPL / Apache triple - check which applies to shipped classes: our jars contain only our generated classes, not javassist; confirm), notices for credited mods |
| `world-config-snippet.json` | the `Mods` keys exactly as `deploy_set --yes` would write them |
| `SHA256SUMS.txt` | checksums of every jar |

## 5. Config defaults to check before release

| Setting | Default today | Release default |
|---|---|---|
| SkyyRebirth feature | OFF | OFF until R3-R10 are built and tested |
| Test / dev rows (admin probes, `allowTestDurations`, test pages) | off | off; a release lint fails on any `*Probe` key |
| Economy numbers | see `research/Economy-Audit-1014.md` | decide before launch (question 3) |
| Permissions | players get `hytale:Adventurer`, admin commands behind our nodes | run `tools/ci/lint.py` (perm_group_leaks) on the release set |
| Logging / data | no personal data in jars | check that no jar embeds Skyy's UUID or paths (grep before release) |
| Third-party tuning | Perfect Parries per class entries written by deploy | document or script it |

## 6. Tool design: `tools/release_pack.py` (not written)

```
usage: python tools/release_pack.py [--version 0.9.0] [--out tools/dev/scratch/release/] [--check-only]
  1. read tools/deploy_set.py: SET, RETIRED, PACK_THIRD_PARTY, PACK_DISABLED   (import, no side effects)
  2. DEV = {SkyyAbilityProbe, SkyyUiProbe, SkyyUiProbeB, ...*Probe}  -> excluded, listed in the report
  3. for each remaining SET entry: require <Mod>/<Mod>-<ver>.jar exists, is the pinned version, not a "-dev"; sha256
  4. gates (exit 1 on any fail): python tools/ci/lint.py = 0 fails; python tools/smoke_test.py PASS on the SAME jars (game closed);
     no jar contains a path under AppData or a UUID of Skyy (grep the class strings); no third-party file in the output (check names against PACK_THIRD_PARTY keys)
  5. write: <out>/SkyWynn-<ver>-server/Mods/*.jar, world-config-snippet.json, VERSIONS.json, CREDITS.txt (from PACK.md rows),
     LICENSES/, README-INSTALL.txt (template), SHA256SUMS.txt; zip it
  6. print the GitHub release command ("gh release create v<ver> <zip> --notes-file ...") but NEVER run it
```

Safety: reads only the repo; writes only under `tools/dev/scratch/release/` (own folder); never publishes, pushes or uploads. Publishing is Skyy's step (a public release is a
public post - "Explicit permission required").

## UNVERIFIED

| # | Item |
|---|---|
| 1 | The current SET jar count (36 after removing 3 probes by my reading of `deploy_set.py`; the tool counts it). |
| 2 | Whether Hytale / CurseForge accept a modpack for Hytale that lists our jars (format, project ids). |
| 3 | Whether vanilla-derived assets inside our built jars may be redistributed (Hytale's EULA / modding terms were not read here). |
| 4 | Which javassist licence terms apply (our jars hold generated classes only; `tools/javassist.jar` is committed for building). |
| 5 | That none of the six required third-party mods has since changed licence (checked 2026-10-10 in Licence-Audit). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Start with a GitHub "server pack" zip, CurseForge modpack later? | [yes] |
| 2 | OK to redistribute our jars given they may contain assets generated from the game's files at build time (or should I check Hytale's modding terms first)? | [check the terms first, then release] |
| 3 | Dynamic Seasons + More Crossbow Tiers have no stated pack permission: ask the authors now, and list them as optional until they reply? | [yes, ask now, optional until a reply] |
| 4 | Release version number and name (pack `0.9.0` "SkyWynn")? | [0.9.0] |
| 5 | Which tuning scripts ship with the pack (Perfect Parries per class)? | [ship a small apply script, off by default] |
