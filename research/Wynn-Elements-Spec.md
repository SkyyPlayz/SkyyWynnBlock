# Wynn elements - spec draft (Earth / Thunder / Water / Fire / Air, Imbue all 5)

Local draft, 2026-10-17. Nothing built. This is the short decision layer on top of the full cloud draft `research/cloud/Element-System-Spec.md` (2026-10-09:
engine ids, statuses, mob table, Server Setup rows, build plan, probes E1-E7). Read that for the numbers; this file only adds what changed since.

## 0. Decisions this follows

| Source | Line | Fixes |
|---|---|---|
| `docs/answered/classes.md` | 212 (2026-10-17) | "yes all 5. we are in 0.7.2 now. so we can build in the wynn craft elements": Imbue picks any of the 5 (like the Priest Bubble), each with its status; build the Wynn-style system on 0.7.2 (spec first: elemental damage / defence per element on gear, abilities, mobs) |
| `docs/answered/classes.md` | 213 (2026-10-17) | exact names Earth, Thunder, Water, Fire, Air everywhere (Lightning -> Thunder, Wind -> Air); Gravity sword = Earth |
| `docs/answered/classes.md` | 52, 54, 172, 209 | class-tree nodes make an ability elemental, pick one of 5; Poison stays a status; Priest Elemental Bubble already built (SkyyClasses 0.1.35) |
| `SkyyGear-Plan.md` lock 17 (read only) | 60-67 | flat element on the WEAPON only; element damage applied on its own, then cut or raised by the target's affinity / defence; single-element % = equipment only, single-element defence = armor only, all-element % and Elemental Defence = class trees only; raw elemental spell damage = skill trees + accessories |
| `SkyyGear-Plan.md` 303 | - | Powders (Wynn's five) stay locked; slots / tiers / drops open |
| `docs/answered/gear.md` | 119 | Armory Elemental swords shelved until tied to our elements |
| `PROJECT-RULES.md` section 4 | - | four power sources; tier tags; everything editable in Server Setup; no dev gates (default ON) |

Already live (do not rebuild): SkyyGear weapon lines Earth / Thunder / Water / Fire / Air Damage, Raw Thunder, Raw Water, Raw Elemental (summed into one number, `GearHit.elemSum`); armor Defence lines exist but never roll; SkyyClasses Spellblade Imbue is Fire-only today; Priest Elemental Bubble picks one of 5.
Note: the gear numbers cited in the cloud draft come from SkyyGear 0.2.11; the pin is now 0.3.18 and SkyyClasses 0.1.36, so line numbers there are stale - re-verify at build.

## 1. What this spec settles

1. **One element table**, five rows, Wynn names: Fire (Burn), Water (Chill / Freeze), Earth (Stagger), Thunder (Shock), Air (Gust). Poison = status only. Colours, numbers: cloud draft sections 2, 5, 9, 10.
2. **Imbue all 5**: attunement picked out of combat (default Fire), Imbue adds +30% of the hit as the chosen element for 12 s + that element's status. "Imbue cycles through all 5" is a swap order the player sets (like swappable key order), not random. Mana at 0 stops the element part (Spellblade rule).
3. **Per-element split on the hit** (SkyyGear `elemSplit` int[5]) so resistances work per element; with an empty mob table damage equals today.
4. **Mob affinity**: family Weak +25% / Resist -25%, boss own element -50%, never immune. Table `elem.mobs` in SkyyMobs.
5. **Statuses come from abilities only**; gear lines never apply them.
6. **No reactions at launch.**

## 2. Four power sources (tool / weapon + gear + accessories + pets)

Skyy's rule: every class and skill stat balances as weapon + gear + accessories + pets stacking. Wynn puts elements on weapon and armor only, so the other two need explicit slots here.

| Source | Element role | Reads / stays within |
|---|---|---|
| Weapon | flat element lines (live), Elemental sword guaranteed line (Gravity = Earth, Flame = Fire, Ice = Water), Powder slots later | lock 17: weapon-only flat element |
| Gear (armor) | single-element Defence lines (Earth / Thunder / Water / Fire / Air Defence), armor only. Needed because mobs and bosses will deal element damage | lock 17; lines exist, switch on when mobs deal element damage |
| Accessories | **raw elemental spell damage** and an **Elemental Power** selectable buff in Accessory Power (a "Magical" / "Elementalist" buff: +X% element status strength and +Imbue damage). Specific accessories can be single-element (e.g. +10 Earth to a build), per lock 17 line 67 | SkyyAccessories Accessory Power rows; all values Server Setup |
| Pets | element-themed pets add a small matching element line (+N Fire damage / +N% status duration) at pet level; the dragon pet's element = its type; summon slot 50% | SkyyPets buff table; Aures dragon Plain / Tundra mapping is Q3 |
| Class tree | all-element %, Elemental Damage %, Elemental Defence, deepen statuses (+20% element strength node on the Spellblade page 143) | lock 17 (class trees only) |

Balance rule proposed: gear + weapon give a base of about the Imbue size (small flat extras today, 1-8 at Lv 40+), accessories + pets together may add up to about the same again, the class tree sets the multiplier. No one source above ~40% of the total element damage of a build. Actual numbers wait for the Class Balance Workbench pass (balance chart must be refreshed when numbers change).

## 3. How it fits the build

| Step | Mods | Round |
|---|---|---|
| 0 | probes E1-E7 of the cloud draft on 0.7.2 (E1 is the blocker: status ticks must not pick up weapon stats) | no agents |
| 1 | SkyyGear + SkyyMobs: split, `elem.*` rows, `elem.mobs`, bridge `mob:fn:elem` | full round (damage maths, 2 mods) |
| 2 | SkyyClasses + SkyyGear: Imbue all 5, attunement, six statuses, `classes:fn:imbue` | full round with the Spellblade build |
| 3 | SkyyAccessories + SkyyPets: element lines / Elemental Power / element pets | full round (saved data: accessory power) |
| 4 | Elemental swords unshelved as boss specials (needs Skyy OK, gear.md 119) | lean |
| Later | Defence lines live, mobs dealing element damage, coloured numbers, reactions (Wildfire, Shatter), powders | full |

Cross-mod only through `skyy.bridge` (plain java.lang types). Stats page shows one coloured row per element. Tier tags unaffected (elements are stats, not items); any new element accessory or pet goes into `tools/tier_tags.py`.

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Imbue attunement: choose out of combat (like the Bubble), or cycle with the ability key in combat? | [out of combat; default Fire; swap order you set] |
| 2 | Accessories: add an Elemental Power buff plus single-element accessories (lock 17 allows raw elemental spell damage there)? | [yes, small, Server Setup] |
| 3 | Pets: element-themed pets give a matching element line; the dragon pet's element follows its type (Plain = Earth, Tundra = Water) until more dragons exist? | [yes; Plain Earth, Tundra Water] |
| 4 | Turn on armor element Defence lines now, or only once mobs deal element damage? | [only once mobs deal it; no dead stats on tooltips] |
| 5 | Mob table (cloud draft section 6): Resist -25 / Weak +25, boss -50, never immune; bosses of the Fire and Frost dragon type keep it. OK? | [yes] |
| 6 | Reactions (Wildfire, Shatter) stay out of launch? | [yes, later tree nodes] |
| 7 | Show "Weak: Fire" on mob name plates? | [no; learn by playing, Bestiary later] |
| 8 | Poison Elemental sword: Imbue applies Poison status, no element? | [yes] |
| 9 | Unshelve the 4 Armory Elemental swords as Spellblade boss specials once step 2 ships? | [yes, after step 2] |
| 10 | Powders (Wynn-style gem slots): spec them after the element system ships? | [yes, next spec] |
