# Totem page redesign (SkyyShards) - proposal 2026-10-25

Skyy 2026-10-25 (screenshot: Harvest Spirit Totem Pole II page - a list of grey text lines and 8 same-size buttons): "the show range button
should show an aura to indicate what range it has.  this whole us for the totem feels clunky, ugly and slow. how can you make it look better,
and show what information you need in a good way. like i have no idea how the modifiers work, or how i could give it seeds to replant."
Recorded word for word in docs/answered/world.md (2026-10-25 TOTEM PAGE). Build after the shbags fix (Shards 0.4.12), as Shards 0.4.13.
Follows research/Menu-Pattern.md, tools/skyyui.py, PROJECT-RULES 4 (rarity + tooltip sections), the approved pet tooltip layout.

## Problems today
- Plain grey lines; the important ones (what it makes, what is missing) look the same as the rest.
- 8 identical buttons, half of them for things you cannot do yet (no modifiers, bench too low).
- Nothing explains modifiers, boosters or the seed store; replanting seeds lives on another page (Map tab -> Give seeds).
- "Show range" only sparkles; you cannot see the edge of the range.

## Proposed layout (one window, three columns, like the Map tab)
| Left: the totem | Middle: what it does | Right: improve it |
|---|---|---|
| Big totem icon in its tier / rarity colour, name + tier tag "T2 Totem", pad number | **Output card**: items / min (green, big), crops in range "72 of 112" with a small bar, the pad's island | **Tier up card**: next tier's gain (+X items / min, +range), cost lines green / red with "(you have N)" incl. the Pocket Dimension, ONE Tier up button (greyed with the reason) |
| Range ring picture: the 5-block radius drawn over the pad grid | **Seeds card**: seed store "0 Wheat Seeds", what replanting does in one line, GIVE SEEDS / TAKE SEEDS right here | **Modifiers card**: 2 slots as icons; empty slot = "+" that opens a short list of what each modifier does + where to craft it (Totem Bench); a filled slot shows its effect in green |
| SHOW RANGE (toggle) + PICK UP (two-click) | **Booster card**: slot icon, "1 Life / Water / Void Essence = +X % for Y min", ADD BOOSTER | Bench note in red only when it blocks you ("Totem Bench I stops at II - upgrade it") |

- Every card has a 1-line "what is this" in the Style Guide section 15 colours; numbers green, missing things red, names in their rarity colour.
- Buttons only for actions you can take now; the rest show the reason instead of a dead button.

## Show range = a real aura
- Toggle (not 10 s): a ring of particles exactly on the range edge (circle of radius R around the totem, at crop height), plus faint
  sparkles on every crop cell it covers; cells outside stay dark. Stays on while the page is open and 30 s after (Server Setup row).
- Vanilla particles first (Assets.zip ring / aura systems); per-player only (other players do not see it).

## Questions for Skyy (defaults)
1. Range aura: until you turn it off, or 30 s after closing the page? [30 s after closing, toggle on the page]
2. Put GIVE / TAKE SEEDS on the totem page too (also keep them on the Map tab)? [yes, both]
3. Mockup picture first, or build straight away? [mockup first - the cloud draws it, Skyy picks]
