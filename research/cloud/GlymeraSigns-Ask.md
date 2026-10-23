# GlymeraSigns - the ask to GlymeraCraft (Skyy sends it)

Cloud draft, 2026-10-23. Nothing sent; nobody but Skyy contacts GlymeraCraft. Style copied from the joszza ask (`research/StructureV2-Pack-Check.md` section 9).
Read: `docs/answered/social.md` (2026-10-23 GLYMERASIGNS line), `research/Farming-Mods-Survey.md` section 4 (same author), `research/GlymeraWorker-Totem-Learn.md`
(same author, "Glymera" mods say All Rights Reserved), `PACK.md`.

## Decisions followed (`docs/answered/social.md`)

| Date | Skyy's words (short) | Used for |
|---|---|---|
| 2026-10-23 | "these two could be useful to add" (GlymeraSigns + GlymeraTrade, CurseForge screenshot) | GlymeraSigns is a PACK candidate; GlymeraTrade is LEFT OUT (duplicate of our /trade), so no ask for it |
| `docs/answered/social.md` 2026-10-23 verdict | writable signs (11 woods x 3 sizes + 23 vanilla sign styles, 56 items, no client mod, server `*`), no duplicate in our mods or the pack, licence ARR with no modpack text -> "ask GlymeraCraft first (Discord https://discord.gg/s5NRFWfxgy or a CurseForge comment; Skyy sends, Claude drafts), then pack as a separate mod (credit + link, never re-uploaded); signs are untiered furniture" | the message below |
| `PROJECT-RULES.md` section 2 | pack mods: permissions in `PACK.md`; never bundle or re-upload; credit + link | what we promise in the message |

## 1. The message (Discord DM or a comment on the GlymeraSigns CurseForge page)

> Hi GlymeraCraft! We are building SkyWynn, a free Hytale server pack (Hypixel SkyBlock x Wynncraft). **GlymeraSigns** is exactly the sign writing
> we were missing, and nothing in our pack does it. May we include it in the SkyWynn modpack / server pack? We would credit you and link your
> CurseForge page in our pack list, players and server owners would download it from your page (we would never re-upload your file or edit
> anything in it), and it stays free. If you would rather we did not, no problem at all - thank you either way!

(About 70 words. Short on purpose; no list of your other mods, so nothing else is asked.)

## 2. Variants

| Where | Text |
|---|---|
| CurseForge comment (public, shorter) | "Hi! We would love to list GlymeraSigns in the SkyWynn Hytale server modpack, with credit and a link to this page (players install it from here, never re-uploaded or changed). Is that OK with you? Thanks!" |
| If they say yes but want wording | Ask for: the credit line they prefer, and whether a server-side config change (turning individual wood sizes off) is fine. We only react to their sign items by id, if at all. |
| If they say no / no answer | Leave it out of the pack; players may still install it themselves. Record the answer in `docs/answered/social.md` and `PACK.md`. |

## 3. What happens after a yes

1. Record their reply word for word in `docs/answered/social.md` (`python tools/qa_append.py social ...`), then a `PACK.md` row (licence ARR, permission "asked, <date>", link, credit).
2. Duplicate check once more (PROJECT-RULES 2): signs are untiered furniture; no tier tag, no Bazaar row needed, sort by name.
3. Add it to the pack only after a smoke test on a scratch copy (`python tools/smoke_test.py`); unsure items (vanilla sign overrides) go in the check note.
4. Pack list credit text: "GlymeraSigns by GlymeraCraft - installed from CurseForge, not bundled."

## Questions for Skyy (each with a default)

| # | Question | Default |
|---|---|---|
| 1 | Send it as a CurseForge comment or Discord DM? | [Discord DM first (private, and they may be more likely to see it); the comment as a backup] |
| 2 | Use the long message (section 1) or the short comment (section 2)? | [section 1 in Discord, the short one on CurseForge] |
| 3 | While waiting, keep GlymeraSigns out of the pack and the server? | [yes - ARR, no modpack text] |
| 4 | Also ask about GlymeraFarmer / GlymeraWorker for ideas or code? | [no - reference only, as recorded; we build our own farming and shard totems] |

## For the local session (UNVERIFIED)

| # | Check |
|---|---|
| 1 | Re-read the GlymeraSigns CurseForge page right before sending: current version, whether a modpack sentence has appeared, exact page URL for the pack credit (this draft has no URL - the screenshot named only GlymeraSigns 3.0.0 / GlymeraCraft) |
| 2 | Whether GlymeraSigns overrides any vanilla sign ids (the 23 "writable vanilla sign styles") that a pack mod or ours also uses; ask in the same thread if yes |
| 3 | Whether the Discord invite https://discord.gg/s5NRFWfxgy is still valid |
