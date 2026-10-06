# Mining Helmet Lamp (a real light, from the Lantern code)

Cloud draft, 2026-10-06. Paper design; nothing built. Inputs read: `docs/answered/gear.md` line 72 (the lock), `docs/answered/bags.md` (lines 25-31, the Lantern locks and the squares report), `docs/log/2026-10.md` (lines 62-63, 86-87, 108: 0.5.4 / 0.5.5 Lantern builds and Skyy's tests), `docs/tests/2026-10.md` (Lantern test lists, lines 320-356), `research/NightVision-Glare-Research.md` (the client light maths, read from the shader), `research/cloud/gathering-armor-art/README.md` (section 2 lamp rule, spec check 3, Q9), `research/cloud/Gathering-Armor-Mining-Farming.md` (the 8 Miner sets), `research/cloud/Accessory-Acquisition.md`. Every number is a placeholder and a Server Setup row (times in seconds). Arithmetic checked in python3.

## 0. Decisions followed (LOCKED, not re-decided)

| Lock | Source | Used here |
|---|---|---|
| A Mining helmet that shows a lamp must REALLY emit light, through our SkyyAccessories Lantern light code (hidden helper lights, glare cap, smooth edges 0.5.5), not through the other lantern-helmet mod; if the real light cannot be done, show NO lamp (no fake glow) | `docs/answered/gear.md:72` | The whole spec; fallback in section 8 |
| Lantern = you glow like a torch (everyone sees it); higher rarities REACH FARTHER, brightness capped at torch level near you; the extra range comes from hidden helper lights, so no particle glare ("Range up, brightness capped") | `docs/answered/bags.md:27` | Section 2 and 3 |
| Lantern reach lives in rows; Legendary reach was cut to a ring of lights at 0.5.5 after the "square dark patches" report; "try to smooth the edges" | `docs/answered/bags.md:30-31`, log 2026-10-05 | The helmet uses the same solver, never its own |
| Skyy's test: Unique / Rare / Legendary light "about 12 / 24 / 48 blocks", "legendary lantern looks really good now" | log 2026-10-04 / 2026-10-05 | The reach scale (section 3) |
| Metal bands Copper 10-18 ... Onyxium 40-49; the Mining sets are Copper Miner ... Onyxium Miner | `research/cloud/Gathering-Armor-Mining-Farming.md` section 1 | Section 3 |
| R3: coins never skip a collection unlock; NPC shops never sell unlocks or accessories | economy rules | Section 4 (no shop lamp, no coin bypass) |
| Everything a server owner might change is editable in Server Setup; times in seconds | `PROJECT-RULES.md` section 4 | Section 7 |

## 1. How the Lantern light works today (what we reuse)

Read from the logs and the shader research; the code itself is not in the cloud (UNVERIFIED, section 8).

- **Torch glow:** a wearer-visible AND other-player-visible light on the player, at a normal torch's level (vanilla torch `#ba9` = levels 11 / 10 / 9). The client reads a ColorLight as a level per colour channel and turns it into light with `0.8 x C x (1 - 0.1 x d / C)^1.5`, `C = level / 15`; the light is cut off at `0.635 x level` blocks.
- **Reach light:** one or more **hidden helper lights** above (and, since 0.5.5, in a ring around) the wearer, shown only to the wearer unless the row "Others see the reach light" is on (default off). White, never coloured (the far edge turned red in 0.5.3 tests, because the client fades each channel on its own).
- **Glare cap:** world light is capped at "fully lit", but **lit particles are not** (the shader multiplies by `4 x light`, no clamp), so any light that is bright at the player's feet makes mining bits glow white. The helper lights are therefore placed high enough that the light at the player is no brighter than about a torch.
- **0.5.5 edges:** lights capped at level 96, up to 7 lights (a ring), Legendary = 6 lights (level 95 at 52 up plus 5 in a ring 27.5 out); the edge drop went from 35% to 16% of full. Advanced rows: "Hidden light: highest" 64, "Hidden lights: most" 7, "Hidden lights: brightest" 96.
- **Lifecycle:** the lights go out at once on unequip, death, logout, world change and line off, and come back on respawn / rejoin (Skyy's test list 8).

**Check of the maths (python3):** with the glare rule "light at the wearer <= 1.3 x" a single light of level `L` must sit at height `h` with `4 x I(h) = 1.3`, and then reaches the ground at `sqrt((0.635 L)^2 - h^2)`:

| Light level L | Height h (min, glare-safe) | Ground reach, single light |
|---|---|---|
| 40 | 19.1 | 16.8 |
| 60 | 31.3 | 21.7 |
| 79 | 43.1 | 25.6 |
| 96 (cap) | 53.8 | 28.6 |

So the shipped Legendary light at **level 95 / 52 up** matches this rule (the model is sound), and one light never reaches past about 29 blocks; the 48-block Legendary reach needs the ring. That is why the helmet must call the **same solver** (reach in, lights out) and not place its own lights.

## 2. One light per player (helmet vs Lantern accessory)

- The player has **one lamp slot** in the light manager. Sources: the **Lantern** line (Accessory Bag), the **Mining helmet lamp**. Each source offers a reach `R_src` (blocks); the manager takes the **largest**: **the stronger wins**, ties go to the helmet (it is the one the player sees on their head). Lights are never added together (the client already combines lights with `max`, so two lights would only cost server work).
- Torch glow is part of the winner's light, never doubled; a held vanilla torch is ignored by the client (it also takes the max).
- Source off (helmet taken off, Lantern line off, helmet lamp toggled off) = recompute at once; if the other source is still on it takes over without a gap (the old lights are replaced in the same tick, not removed first).
- Rows are separate: turning the Lantern line off in Server Setup does **not** switch off helmet lamps, and "Mining lamp" off does not touch Lanterns.
- Implementation shape (for the local session): a small shared helper in SkyyAccessories (`LampLight.setSource(playerId, sourceId, reach)`; the solver and sender stay one code path) and the Mining armor reads "worn helmet id" and calls it through the shared `skyy.bridge` map with plain `java.lang` types (cross-mod rule). The armor mod must not carry any light code of its own.

## 3. Reach per mining tier (proposed rows)

Skyy's own proposal (README section 2): Copper lamp = the Common Lantern reach up to Mithril / Onyxium = Legendary. The Lantern's tested figures are Unique 12 / Rare 24 / Legendary 48 blocks; the in-between steps below are placeholders.

| Set (band) | Lamp look | Reach (blocks) | Equals Lantern | Light shape (python3, single light where possible) |
|---|---|---|---|---|
| T0 Miner's Leather (1-13) | none (no lamp drawn) | 0 | - | - |
| Copper Miner (10-18) | small copper lamp | torch glow only (about 7 blocks) | Normal | level 11 on the player, no hidden light |
| Iron Miner (15-23) | iron cap lamp | 12 | Unique | 1 light, level 24, 9.8 up |
| Thorium Miner (20-28) | bright lamp | 18 | between | 1 light, level 45, 21.8 up |
| Cobalt Miner (25-38) | lens visor | 24 | Rare | 1 light, level 71, 37.9 up |
| Adamantite Miner (35-43) | strong lamp | 34 | between | 1 light at the 96 cap + a small ring (solver) |
| Mithril Miner (40-49) | glowing lens | 48 | Legendary | the Legendary ring (6 lights) |
| Onyxium Miner (40-49) | violet-glow lamp | 48 | Legendary | same lights as Mithril (the colour stays WHITE; violet is art only) |

- Reach is "the ground lit about this far around you", the unit the Lantern rows already use. Torch glow reach 7 is `0.635 x 11`.
- Levels 24 / 45 / 71 above come from the glare-safe rule in section 1 (reach 12 / 18 / 24, python3: L 24 / 45 / 71, h 9.8 / 21.8 / 37.9). Real Lantern Unique / Rare may use other levels; the solver's own output wins over this table.
- The lamp sits in the **helmet only** (Head piece). Chest / legs / boots do nothing for light. Wearing a half set gives the lamp for the helmet's own tier (no set bonus needed).
- Mithril and Onyxium share a band, so they share a reach by default (Q3). The next metal tiers (Cindersteel ...) are not designed here: the cap 96 and 29-block single-light limit mean they can only add lights, never brightness, so the ladder tops out at Legendary unless Skyy wants a "Mythic" reach (Q4).

## 4. Cost and toggle

- **No running cost** (no Mana, Stamina, coins or fuel): the lantern line is also free once worn; a lamp that ticks a cost every second would be a chore in a mining loop. Default row `lamp.fuel` = 0 (Q5 asks about a "lamp oil" option).
- **Cost = the helmet.** The lamp is part of the Mining helmet recipe (a lamp part in the T-piece recipe, e.g. 1 Crude Torch x2 per tier as a placeholder). It is **not** sold by NPC shops and does not unlock earlier through coins (R3); the helmet stays behind its metal collection (Copper VI ... Mithril V) as in the Mining armor spec.
- **Bypass check:** Legendary-reach light on a Mithril Miner helmet is a Mining reward, not a Tree Sap one; Lanterns stay gated behind the Tree Sap collection. A player who wants the light without mining can still only get it by crafting the Lantern. This does not break R3 (no coin path), but see Q2.
- **Toggle:** `/lamp` switches the helmet lamp on or off for you, default on; the state is saved per profile; a SkyyMenu button next to Accessories can show the same switch (UI pass for the local session). Off = the helmet's lamp art is dark too (same item, a second "lit" texture layer; UNVERIFIED if swapping an emissive layer per player is possible, then the art stays lit and only the light goes).
- Day / bright light: the lamp stays on but the light is invisible in full sun; a row `lamp.autoOffDay` (default off) turns it off in daylight above ground to save server load (section 6).

## 5. Edge cases

| Case | Behaviour |
|---|---|
| **Underwater** | Same light (the client light has no water rule). Water fog may hide the far edge; no change in reach. The lamp does not go out in water (a vanilla torch would, a modern helmet lamp would not). UNVERIFIED how the client fogs it |
| **Caves / tunnels** | Point lights have no occlusion (research section 1.3), so the hidden light above you also lights rock and tunnels next to yours "through" walls. Accepted: the only effect is a lit patch in a neighbouring cave; no sight, no map reveal. The ring lights at "27.5 out" can sit inside solid rock; fine, nothing is placed in the world (client-side light only, no light blocks). |
| **Surface and ceiling height** | A light 52 up from a miner at Y 30 is above the ground: fine for the light. Max height row ("Hidden light: highest" 64) clamps it against the world top. A ceiling does not block it (no occlusion) |
| **Other players** | See only your torch glow (default). The row "Others see the reach light" is the existing one; the helmet obeys it. A miner with a helmet next to a Lantern wearer: both see only torch glows; each wearer gets their own largest light |
| **Group mining** | Several wearers just overlap, the client takes the max per pixel, so no extra brightness |
| **Death / respawn / logout / world change / profile switch** | All lights out at once; back on respawn / rejoin; profile switch re-reads the helmet (Skyy's test 8) |
| **Swapping helmets** | Hot-swap: the new reach replaces the old in the same tick |
| **Dropping the helmet / durability break / unequip in a chest** | The lamp goes out the tick the head slot changes; no leftover light |
| **Low client view distance** | The ring is dropped when the view distance is shorter than the ring (known from 0.5.5), so the reach shrinks; the torch glow stays. Documented in the Server Setup help line |
| **Sprint / flying / teleport** | The lights follow the player; refresh is throttled (section 6), the lights must not stay behind after a teleport (rebuild on position jump > 8 blocks) |
| **Particle glare** | The glare rule from section 1 holds for every row (the solver caps level and height); mining dust must still look normal (Skyy's test 2) |
| **Vanilla "lantern helmet" mod** | Not read, not required. If its item id is worn it does nothing for us (and does not clash: we send only ours) |

## 6. Server load caps (rows)

The 0.5.5 review flagged a per-tick refresh of 6 lights per Legendary wearer (a LOW). Python3: 20 wearers x 6 lights x 20 ticks = **2,400 light updates a second** if refreshed every tick; throttled to 2 times a second = **240** (10x less; 40 wearers: 4,800 vs 480).

| Row (Server Setup > Mining > Helmet lamp) | Default | Why |
|---|---|---|
| `lamp.enabled` | on | master switch (off = all helmet lamps dark, helmets show no light) |
| `lamp.reach.<tier>` (7 rows) | 0 / 7 / 12 / 18 / 24 / 34 / 48 / 48 (T0..Onyxium; Copper = torch glow) | section 3 |
| `lamp.torchGlow` (level) | 11 | the Normal Lantern torch level |
| `lamp.refresh` (seconds) | 0.5 | per-player update interval while moving; idle players refresh once on stop |
| `lamp.moveThreshold` (blocks) | 1.0 | no update while you move less than this |
| `lamp.maxLightsPerPlayer` | 7 | the existing "Hidden lights: most" |
| `lamp.maxPlayersFullReach` | 24 | beyond this the oldest wearers fall back to torch glow + one light (and the log says so once per minute) |
| `lamp.maxLightsTotal` | 150 | hard cap server-wide, like a circuit breaker |
| `lamp.autoOffDay` | off | skip the light above ground in full day |
| `lamp.othersSee` | off | follow the Lantern row |
| `lamp.underwater` | on | allow the lamp underwater |

Shared Lantern rows keep working (level cap 96, highest 64, brightest 96, most 7); the helmet reads them and never exceeds them.

## 7. Server Setup placement

SkyWynn Menu -> Server Setup -> **Mining -> Helmet lamp** (the rows above, times in seconds), and a pointer line under **Accessories -> Lantern**: "Mining helmet lamps use these light limits too; the stronger of helmet and Lantern is used". Config kit `tools/skyycfg.py` (`tools/CONFIG-CONTRACT.md`). Any later change to the Lantern's defaults is a one-time migration per the project rule (only lines still at the old default).

## 8. Build sketch (for the main session to size)

- **Lean round** if the shared helper already exists in SkyyAccessories (one mod + one reader in the armor mod); **full round** if the helper is new, because it touches two mods and light cleanup on death / logout (items or world state are not at risk, but the Lantern is live and tested - do not regress it).
- Stage 1: refactor the Lantern code into "source -> reach -> lights" with `Lantern` as the first source, with no behaviour change (Skyy's 0.5.5 test list must still pass). Stage 2: add the helmet source + rows + `/lamp`. Stage 3: art (the lamp lens in the helmet texture, the lit layer).
- If stage 2 cannot be done in a given Hytale version, **the helmet shows no lamp** (the lock): the art gets a plain cap with a dark lens, never a fake glow.

## For the local session (UNVERIFIED)

1. The real SkyyAccessories 0.5.5 / 0.5.6 Lantern code: the exact levels and heights it uses per rarity (this spec's reach rows come from Skyy's "about 12 / 24 / 48 blocks" and the glare maths, not from the code), where the solver lives, whether it can take a source id and a numeric reach.
2. The Mining armor item ids and how to read the worn helmet cheaply (an equipment-change event rather than polling).
3. Whether a head slot item can show a lit/dark texture per player, or an emissive layer (and how the lamp lens looks with the 0.5.x torch glow).
4. Underwater light fogging and the client's light in water (no vanilla water-light rule was seen).
5. Lights above the world height limit (the helper must clamp to "highest" 64 and the world roof).
6. Whether another mod's lantern helmet (Skyy mentioned one) also sends a light, and how both look when worn.
7. Whether the lights of two wearers close together cost two sends each (the lights are per viewer): the cap `lamp.maxLightsTotal` may need a lower value.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Reach per helmet: Copper torch glow, then 12 / 18 / 24 / 34 / 48 blocks, Mithril and Onyxium = Legendary (as above)? | [yes, as rows] |
| 2 | Is a Legendary-reach helmet fine, or should the helmet stop one rarity below the Lantern (Mithril 24-34) so the Tree Sap Lantern stays the best light? | [Legendary reach, helmet = a Mining reward] |
| 3 | Mithril and Onyxium (same band): the same reach, or Onyxium slightly longer (e.g. 56) when the lights allow? | [same, 48] |
| 4 | Do the later metal tiers (Cindersteel ...) add reach, or does the lamp stop at Legendary (48)? | [stop at 48] |
| 5 | Should the lamp use fuel (lamp oil / Tree Sap) for a Mining chore, or stay free? | [free] |
| 6 | Toggle: `/lamp` plus a menu button, default on? | [yes] |
| 7 | Show the helmet lamp to other players as the torch glow only (as the Lantern)? | [yes] |
