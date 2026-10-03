# Night Vision glare - research (2026-10-03)

Skyy (2026-10-03, in game): *"night vision accessory makes break particles reallly bright its kinda blinding."* SkyyAccessories 0.5.3
(the SET pin) gives the wearer a light by queueing `DynamicLightUpdate(ColorLight(radius 255 (sent as -1), 1, 1, 1))` on the player's own
entity through the player's own EntityViewer (wearer-only, nothing saved). Block-break bits next to the pickaxe show almost white.

Everything below was read from the live game files, read-only: `HytaleServer.jar` 0.6.8 (Implementation-Revision-Id d2feeb39...),
`Assets.zip`, and `Client/HytaleClient.exe` (build of 2026-09-21, sha1 a419b5c4...; a NativeAOT .NET exe - its GLSL shaders are embedded
as text, the C# code was read as x86-64 machine code with a small scratch decoder; addresses below are virtual addresses in that exe).
Installed mods were opened read-only for ideas only. Nothing was built, deployed or run in the game.

## 0. Answer in one paragraph

**"Radius" is not a radius.** The client turns a ColorLight into a light level per colour channel `E = max(channel, radius)` (0-255,
unsigned), then uses `E / 15` as the light strength (vanilla lights are 0-15; 15 = the brightest vanilla light). Our `(255, 1, 1, 1)`
therefore means **level 255 on every channel = 17 times the brightest vanilla light**, reaching about 160 blocks. Walls cannot show it:
the world shader caps light at "fully lit", so caves just look fullbright. **Lit particles are not capped:** Hytale's particle shader
multiplies their colour by `max(4 x dynamic light, block light)` with no limit (a "x4, for some reason" fudge in the shader), so every
block-break / hit / run / landing bit near you is drawn about **53 times too bright -> pure white** (still 10x+ at 100 blocks). The fix that works
tonight without a build: **Server Setup -> Accessories -> Night Vision -> Light radius = 12** (or 15; the colour rows can stay at 1).
A point light at your feet can never be both "lights the whole cave" and "no glare": anything above level ~15 makes nearby bits glow
again. UpdatePostFxSettings is bloom only (no brightness/exposure field), so it cannot replace the light. Recommended 0.5.4: one clear
**Brightness** row (light level, default 12 or Skyy's pick from tonight), send `ColorLight(0, L, L, L)`, optional "dimmer while mining".

---

## 1. Why the particles blow out (proof chain)

### 1.1 The light value the server sends (HytaleServer.jar)

- `protocol.ColorLight` is 4 bytes on the wire in the order **radius, red, green, blue** (`ColorLight.serialize` offsets 0-3; the
  constructor `ColorLight(byte radius, byte red, byte green, byte blue)` stores them in that order).
- Asset colours are 4-bit light levels: `ColorParseUtil.hexStringToColorLightDirect` parses `"#RGB"` one hex digit per channel (0-15) and
  `"#RRGGBB"` as `value / 17` (0-15); `colorLightToHexString` multiplies by 17. The JSON codec (`ProtocolCodecs.COLOR_LIGHT`) has `Color`
  (HytaleType "ColorShort") and `Radius` (byte).
- The server's own block light (`FloodLightCalculation.floodChunkSection`) reads only red/green/blue, never radius; `ChunkLightData` packs
  4 bits per channel (`getLightValue = (raw >> 4*i) & 15`). Radius is a client-only value.
- Vanilla examples: torch `#ba9`, Radius 0 -> levels (11, 10, 9). White build light `#eee`. The only vanilla light above 15 is
  `Rock_Crystal_Iridescent_Large` (`#cde`, Radius 18). The builder tool's entity-light panel calls the radius "Bright Radius", slider
  1-15 (`Client/Data/Game/Interface/.../EntityToolSelectedEntity.ui`).

### 1.2 What the client does with it (HytaleClient.exe machine code)

- `0x140760580` - ColorLight -> 3-byte RGB slot: `R = max(Red, Radius)`, `G = max(Green, Radius)`, `B = max(Blue, Radius)` (movzx =
  unsigned 0-255; `cmp / cmovl` = max). **The radius is a floor for every channel.**
- `0x1409f1974..0x1409f197f` - the entity component-update handler passes `DynamicLightUpdate.dynamicLight` to that function, into the
  entity's dynamic-light slot (entity+0x49c). Model lights (+0x49f) and held/worn item lights (+0x4a2) go through the same function.
- `0x14054bc20..0x14054bfce` - the entity's light = per-channel **max** of the three slots (dynamic, model, items - a held torch never
  adds to our light, the bigger one wins), then **each channel / 15.0** (constant at 0x142be0c44) -> the light colour in the light list.
- `0x14055dbd1..0x14055dc75` - every frame: the light position = the entity's own position vector (entity+0x440, no offset added - for a
  player that is the feet); the light's cut-off distance = `0.635 x max(channel level)` blocks (constants 15.0 and 0.635 at 0x142be11f0 /
  0x142be1200).
- `0x1402344ab..0x14023462e` - the client's own machinima actor light converts a 0-1 colour to levels with `x255, /255, x15` and sends
  Radius 0: the client itself treats ColorLight channels as **0-15 levels**.

### 1.3 The shaders (embedded in the exe)

- `LightCluster_inc.glsl`: per channel `light = 0.8 x C x (1 - 0.1 x d / C)^1.5` with `C = level / 15`, `d` = distance in blocks;
  it reaches 0 at `d = 10 x C` (the CPU cut-off 0.635 x level is just inside that). Several lights combine with `max`, not a sum.
  Point lights have **no occlusion** test (they shine through blocks).
- World surfaces: `LightClusteredFS.glsl` writes `light x DynamicLightMultiplier (3.0)` into the light buffer with GL MAX blending
  ("3.0f gives the best results ( = closest to what we had with forward rendering)"); `DeferredFS.glsl` draws `albedo x light`. The
  forward chunk path says it out loud: `light = clamp(max(dynamicLight, light), 0, 1)` - **world light is capped at 1 (fully lit)**,
  and the deferred path behaves the same (early-out at 1/3 before the x3; Skyy's walls look normal while the bits glow).
- Particles: `ParticleVS.glsl computeFXClusteredLighting` returns `max(4.0 * dynamicLightColor, staticLightColorInfluence)` with the
  comment *"For some reason the clustered lights here are a lot darker than they are for blocky models, so it has to be multiplied by 4
  to make sense"*; the vertex colour is multiplied by it **with no clamp** (`ParticleFS` then also multiplies by the sunlight colour; the
  transparency buffer keeps HDR colour up to 64). `PostEffectFS.glsl` has no tone mapping: `clamp(color + brightness, 0, 1)` -> anything
  above 1 per channel is drawn white. Trails use the same path.
- Which particles are lit (Assets.zip, `LightInfluence`; the ParticleSpawner codec doc: *"0.0: Lighting does not affect it
  (fullbright). Any other value applies the full lighting."*): `Block_Break_Stone_Parts`, `Block_Hit_Stone_Parts` (Erosion, opaque bits)
  and `Block_Break_Stone_Dust` = 1; `Block_Break_Stone_Sparks` = 0 (unaffected). Over all block spawners: Break 41 of 47, Land 45 of 49,
  Run 10 of 11, Sprint 18 of 20, Hit 5 of 11 are lit - so footstep, sprint and landing dust at your feet glow too.

### 1.4 The numbers

`E` = light level of a channel = `max(colour, radius)`. Distances from the light (your feet). "full" = walls fully lit up to; "half" =
walls at least half lit up to; "P" = how many times brighter than its own colour a lit particle is drawn (above ~1.3 it reads as
glowing; a grey stone bit at P 2 is white). Eye-level mining bits are ~2.9 blocks from your feet, floor mining ~1.5, dust ~0.3.

| Level E | Reach (cut-off) | full | half | P dust 0.3 | P floor 1.5 | P eye 2.9 |
|---|---|---|---|---|---|---|
| 8 | 5.1 | 0.8 | 2.5 | 1.6 | 1.0 | 0.5 |
| 10 | 6.3 | 1.8 | 3.6 | 2.0 | 1.5 | 0.9 |
| 11 (vanilla torch, red) | 7.0 | 2.3 | 4.2 | 2.2 | 1.7 | 1.1 |
| 12 | 7.6 | 2.8 | 4.7 | 2.4 | 1.9 | 1.3 |
| 13 | 8.3 | 3.3 | 5.3 | 2.6 | 2.1 | 1.5 |
| 15 (brightest vanilla) | 9.5 | 4.4 | 6.5 | 3.1 | 2.5 | 1.9 |
| 18 | 11.4 | 6.1 | 8.3 | 3.7 | 3.1 | 2.5 |
| 20 | 12.7 | 7.2 | 9.5 | 4.1 | 3.6 | 3.0 |
| 30 | 19.1 | 13.0 | 15.6 | 6.3 | 5.7 | 5.1 |
| 127 (Mermaids fullbright) | 80.6 | 73 | 78 | 27 | 26 | 26 |
| **255 (0.5.3 now)** | **162** | **156** | **161** | **54** | **54** | **53** |

Why only the particles hurt: walls get `min(1, 3 x light)` (capped), bits get `4 x light` (not capped). At level 255 the walls are just
"fully lit" everywhere (looks like fullbright), the bits are ~53 times too bright. A vanilla held torch already makes nearby bits about
1.1-1.7x - that is the glare level players are used to.

### 1.5 The shipped mods we copied the value from

NotEnoughPotions 2.3.0 and SimpleEnchantments 1.2.0 send `(-1, 1, 1, 1)` = level 255 too (same glare). Mermaids 3.4.2 "Fullbright" uses
a DynamicLight **component** + PersistentDynamicLight `(1, 127, 127, 127)` (level 127: everyone sees it, it is saved with the player,
~26x glare) plus a per-player bloom boost. Community packs that look right stay low: BrighterTorches 1.0.3 uses Radius 12 / 15 on the
torch colour, Spark Lantern Pets uses Radius 14 / 20 on floating pets. (PJ-HyperGlowingArmors' Radius 5 / 10 does nothing - its colour
#bbb = 11 is already above the floor; Brightness-Tweaks 0.4.7 maps its slider to radius 1-16 and colour 1-255.)

---

## 2. Values to try now (Server Setup -> Accessories -> Night Vision, all live, no build)

The radius row floors all three colours, so change **only "Light radius"**; red/green/blue at 1 are then ignored. (Same result: radius 0
and red = green = blue = the level.) Ranked:

1. **Light radius 12** - glare like holding a torch (eye-level bits ~1.3x, floor bits ~1.9x). Walls fully lit ~3 blocks around you,
   half lit ~5, dark beyond ~7.6. Best first try.
2. **Light radius 15** - the brightest vanilla light level. Bits ~1.9x (eye) / ~2.5x (floor): light-grey to white for pale blocks, but
   ~28 times less than now. Fully lit ~4.4 blocks, half ~6.5, ends ~9.5.
3. **Light radius 10** - if 12 still glares: eye-level bits normal (0.9x). Small bubble (full ~1.8, half ~3.6, ends ~6.3).
4. **Light radius 18** - only if 15 feels too dark and some glow is acceptable: bits ~2.5-3x; full ~6, half ~8, ends ~11.

Optional look: radius 0 + red 8 / green 13 / blue 9 = a green "night vision" tint (green channel level 13).
Do not use: radius 255 (now), anything 30 or above (bits 5x+), and the 0.5.3 help text's "15,255,255,255" (= level 255 again).
Radius 0 with colours 1 = level 1 = practically off (a 0.6-block glow).

---

## 3. Alternatives without a light at your feet

| Idea | Per player? | Lights caves / night? | Verdict |
|---|---|---|---|
| **UpdatePostFxSettings** (`globalIntensity, power, sunshaftScale, sunIntensity, sunshaftIntensity`) | yes (`PacketHandler.write`) | **no** | Bloom only. Proof: `ClientEffectWorldSettings.createPostFxSettingsPacket` = (BloomIntensity 0.3, BloomPower 8, SunshaftScaleFactor 4, SunIntensity 0.25, SunshaftIntensity 0.3) by default; client `BloomSelectFS` = `pow(colour, uPower)` of fullbright/emissive pixels + `sun/moon x uSunMoonIntensity`, `BloomCompositeFS` = `bloom x uBloomIntensity` + `sunshaft x uSunshaftIntensity`. There is no exposure / brightness / ambient field. Raising it only adds glow halos around already-bright things (worse glare, no cave light). Resets on every world join (`World.onFinishPlayerJoining` re-sends the world's ClientEffects). |
| **Mermaids Fullbright** | partly | yes | It is a level-127 light component (everyone sees it, saved) + the bloom boost above (globalIntensity >= 1.7, power >= 1.2, sunIntensity >= 2.2, sunshaftIntensity >= 1.4, sunshaftScale >= 1). Same glare. Nothing to take. |
| **Light on a helper entity above you** | yes (our EntityViewer trick works on any entity the wearer sees) | yes (point lights shine through blocks) | The only way to keep a big lit area without glare: e.g. level 20 about 6 blocks above your head lights your surroundings fully while nearby bits sit at ~1.6x. Costs an extra (invisible, unsaved) entity per wearer moved every tick (other clients receive it too), the light trails behind when moving fast, clean-up on logout / world switch / crash. A later build ("lantern wisp"), not 0.5.4. |
| **Dimmer while mining** (adaptive level) | yes | yes | Cheap and server-only: on each `DamageBlockEvent` by the wearer use a lower level (e.g. 10) for ~2 s, then go back (e.g. 15). One 4-byte update each way. Limits: the first hit's bits appear before the server dims (one flash per mining start), the bubble visibly shrinks/grows, footstep dust is unchanged. Good optional 0.5.4 add-on. |
| Per-player particle assets with LightInfluence 0 | yes (asset packets) | - | Hacky: ~100 spawners, asset reloads, and Erosion bits with LightInfluence 0 get the bloom flag (a glow halo). No. |
| Per-player weather with bright night sunlight (`UpdateWeather`) | yes | outdoors only | Sky light only (caves stay dark), replaces the weather visuals, the weather system overwrites it. No. |
| World fullbright lighting (`FullBrightLightCalculation`, /lightingcalculation) | no (whole world) | yes | Everyone in the world. No. |
| Builder-tools "Fullbright" | client-local creative setting | - | The server cannot switch it. No. |

---

## 4. Recommendation for SkyyAccessories 0.5.4 (lean round: one mod, no saved data)

1. **Fix the light model.** AccNv sends `ColorLight(radius 0, L, L, L)` where L = the level (keep `key()` packing; radius byte 0).
2. **Server Setup rows (category Night Vision):**
   - `line.NightVision` on/off (unchanged).
   - NEW `nightVision.level` "Brightness" int 1-30, **default 12** (or the value Skyy picks tonight). Help: "Light level. 15 = the
     brightest vanilla light (lights ~4 blocks fully, fades out by ~9). Higher reaches further but makes nearby mining bits glow white;
     12 = about a torch."
   - `nightVision.refreshSeconds` (unchanged, Advanced).
   - Drop the four raw rows (radius / red / green / blue) - their help texts are wrong ("255 = a wide, even glow", "try 15,255,255,255").
     New key names mean **no migration**: a 0.5.3 file's old keys are simply ignored (one INFO line "old Night Vision light keys are
     ignored since 0.5.4"), a missing new key = its default. The default-file comments describe the level instead of the radius.
3. **Optional (Skyy decides): dimmer while mining.** NEW `nightVision.miningLevel` "Brightness while mining" 0-30 (default 10, 0 = no
   dimming) and `nightVision.miningSeconds` "Dim after a hit for" 0-10 s (default 2). A new class (one registerSystem) on
   `DamageBlockEvent` marks the wearer; `AccNv.step` picks the level (the existing once-a-second decision + a poke on change). With this,
   the main level can be 15 while mining stays at 10.
4. Build gate: keep `_nv_engine_proof`; add a harness check that the packed light is `(0, L, L, L)` and L is clamped to 1-30.
5. Risks: the conversion lives in the client (this exe build) - a client update could change it, the server build cannot check it;
   the lit area is smaller than tonight's fullbright (unavoidable with a light at the feet); dust at your feet stays the brightest bit
   (~2-3x at 12-15, faint because dust is see-through); with the dimming option, one bright flash per mining start.

## 5. UNVERIFIED - only an in-game test can confirm

1. How levels 12 / 15 / 10 actually look (bubble size, bit brightness) - the numbers above come from the shader math.
2. That the light sits at the feet (the client code uses the entity's position vector unchanged; for players that is the feet).
3. That walls never turn white at any level (world light is capped at 1 - matches tonight's screenshot).
4. Holding a torch with Night Vision on changes nothing visible at level 12+ (the client takes the per-channel max, not a sum).
5. The feel of "dimmer while mining", if built.
