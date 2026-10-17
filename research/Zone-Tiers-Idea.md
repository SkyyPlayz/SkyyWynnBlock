# Zone tiers idea - 2 or 3 metal tiers per zone (IDEA, not built)

Where answers go: Skyy's words -> `docs/answered/gear.md`; when this becomes a spec, rename it to a Zone-Tiers Spec file and add it to `INDEX.md`.

## Skyy 2026-10-17 (word for word)
"5 zones at start. and with zone 1 going through iron, that's 20 levels. if we do 2 tiers per zone, players will be hitting max lvl and
needing to rebirth to get all the way through zone 3. it will take a lot of rebirths to get through zone 5. (dont change now.) when we add
more tiers should we adjust the levels of each tier, so you get to the end of zone 4 by lvl 50. then have to rebirth and work back up to get
to zone 5.     (i had an idea. we could even do 3 tiers per zone.  copper, then iron, then you smelt the 2 together to make bronze.   zone 2
has thorium. so we could do silver then an alloy, or add a different metal to zone 2, and an alloy. so each zone could have 2 metals you
find, then you smelt together for a third alloy tier.    (if we need more metals we can look into Brandon Sandersons mistborn for a really
good list of real metals and alloys.)"

Earlier the same day: UT + Mythic are per ZONE at the zone's highest tier; "eventually i want to do 2 tiers per zone ... including more
ore, for the farming/ tool tiers. then we could make the farming and gathering match".

## Claude's take (draft, for when we build it)
- Yes, re-band levels: the first run reaches the end of Zone 4 at Lv 50 (today's max class level; rebirth raises it +10 each, Rebirth-Spec
  Q12). Zone 5 (dinosaur caves, dragon) is the first post-rebirth zone.
- 3 tiers per zone (metal A, metal B, their alloy) = 12 tiers over Lv 1-50, about 4 levels each; Zone 5 adds 3 more after rebirth.
  Draft bands: Zone 1 Lv 1-12, Zone 2 13-25, Zone 3 26-38, Zone 4 39-50, Zone 5 50+ (rebirth).
- The alloy tier = smelt metal A + B (a real smithing step) = the zone's top GATHERING tier. Metals and alloys are for MINING SETS and TOOL
  upgrades only (the forever gear you level up), not combat gear. Skyy 2026-10-17 correction: "not quite ... like the current ore sets in
  the game. the metals you mine and their alloys will be used for mining sets, and upgrading tools. not combat gear. all combat gear is still
  drops only. and all Ut and mythic are combat gear. not your forever gear you level up."
- Combat gear (normal drops, UT, Mythic) stays DROPS ONLY; UT + Mythic sit at each zone's highest combat level band, not on a metal.
- Real-metal pool (Mistborn uses real metals + alloys, so names are free to use): copper + tin -> bronze; iron + carbon -> steel;
  tin + lead -> pewter; copper + zinc -> brass; gold + silver -> electrum; aluminium + copper -> duralumin; nickel + chromium (+ silicon) ->
  nicrosil; cadmium + bismuth -> bendalloy. Today's ladder (Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium, ...) maps in.
- Touches: SkyyGear tiers + `tools/tier_tags.py`, SkyyWorldGen ores per zone, Mob-Levels-Plan bands, tool / farming tiers, collections,
  Bazaar, rebirth. A full ultracode spec round when Skyy says go.

## Alloys (Skyy 2026-10-17)
"none of the alloys you mentioned really fit, i think well have to make our own.  should we use silver and gold in them? or save those for
other things and make our own new ores?" -> popup "Keep Silver/Gold for charms (Recommended)": Silver + Gold stay precious (Void Charms,
jewelry, coin-type items). Each zone = the vanilla metals already in it + ONE new ore of ours themed to the zone, smelted into our OWN alloy
(own names, not the real-world list above).

## Metal list (Skyy 2026-10-17, their table) - Zone 1 alloy = Bronze ("copper and iron make bronze")
| Zone | Base | Our ore | Alloy |
|---|---|---|---|
| 1 | Copper | Iron | Bronze |
| 2 | Thorium | Lead | Dusk |
| 3 | Cobalt | Chromium | Azurvane |
| 4 | Adamantite | Slag | Cinder |
| 5 | Mithril | Titanium | Lumen |

"Onyx and Nightveil are parked until there's a Zone 6. Silver and Gold stay for charms." "Quirk will send you art drafts for each family."
(Iron is vanilla; "our ore" column = the zone's second ore.) Metals + alloys = mining sets + tool upgrades only.

## Furnace Charm + collections (Skyy 2026-10-17, docs/answered/gear.md)
- Furnace Charm (Void Charm) T1-T5 = the alloy unlock ladder: each tier-up costs that zone's two metals and unlocks smelting its alloy
  (T1 Copper + Iron -> Bronze, T2 Thorium + Lead -> Dusk, T3 Cobalt + Chromium -> Azurvane, T4 Adamantite + Slag -> Cinder, T5 Mithril +
  Titanium -> Lumen). Smelt time -10/-20/-30/-40/-50%, fuel +15/+30/+45/+60/+75%; max tier -> Eternal Flame (no fuel) at Charcoal tier 7.
- Collections for the BASE metals only; alloys get no collection.
