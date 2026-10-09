# Dynamic Seasons crash report - draft for research/Author-Requests.md item 10

Cloud draft, 2026-10-09. The task asks for item 10 in `research/Author-Requests.md`, but cloud sessions can only push `research/cloud/`
straight to main, so the draft lives here. The local session pastes the block below into `research/Author-Requests.md` after item 9,
in the same style. Skyy sends it. Facts come from the CLOUD-RESUME task text and `docs/log/2026-10.md` (2026-10-09 07:07 line). The
time, server build and pack size are left for Skyy to fill in from the crash log (marked `<...>`). Nothing has been checked against the jar.

## For the local session

1. Paste the block into `research/Author-Requests.md` as item 10, after item 9 (Welkin).
2. Fill in the three `<...>` fields from the crash log: the exact server build, the mod count and the time.
3. Attach the full stack trace when sending. Trim it to our side only, and keep nothing personal in paths (username, PC name).
4. UNVERIFIED (needs the jar): the guess about how the component gets added. Dynamic Seasons ships no licence file (`PACK.md`), so
   we only read stack traces, never decompile the mod to check.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Send it as a CurseForge comment or on their Discord? | [Discord if they have one, else CurseForge comment] |
| 2 | Offer to test a fix build on our test world? | [yes] |

## Block to paste

---

## 10. BlueOrbit - Dynamic Seasons (bug report, 6.1.3)
Where: Discord or CurseForge comment

> Hi BlueOrbit! I'm Skyy from SkyWynn, a free Hytale server pack. We love Dynamic Seasons, and it's in our pack. We hit a crash I
> wanted to pass on in case it helps:
>
> **What happened:** on 2026-10-09 (<time>) the world crashed while a player was fighting near a field of crops. Chunks around them were
> unloading and loading back in as they moved.
>
> **Error** (server <0.6.x build>, DynamicSeasons 6.1.3, a modded server with <N> mods):
> ```
> java.lang.IllegalArgumentException: Entity already contains component type ...
>   typeClass=class DynamicSeasons.component.CropQualityComponent
>   at ...Store.addEntities
>   at ...CommandBuffer.consume
>   at ...Store.removeComponentIfExists
>   at ...ChunkTracker.lambda$tick$1   (World tick)
> ```
> (full log attached)
>
> **Our guess:** when a chunk reloads, a crop entity comes back with its CropQualityComponent already on it, and the component is then
> added a second time. Using a put / "add if missing" (or checking for it first) when the crop is re-added might fix it. You know your
> code much better than we do, of course!
>
> Happy to test a fix build on our test world. Thanks for the mod!

---
