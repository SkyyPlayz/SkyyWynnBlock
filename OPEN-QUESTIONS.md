# SkyWynn - open questions for Skyy (collected 2026-09-25)

Every choice the builds made for you, in one place. Each line shows the **default that is live now** in brackets. Most of them are one
config value: change it in game (SkyWynn Menu -> Server Setup, once that mod has adopted it) or tell Claude. The detail is in the spec named
under each heading. Older design questions (gear, classes, collections cutoff, World Gen 2, ...) stay in `docs/archive/DESIGN-STATUS.md` "Open questions".

**ONLY OPEN QUESTIONS LIVE HERE (Skyy, 2026-10-05).** When Skyy answers one, the answer goes word for word into
`docs/answered/<topic>.md` (its "New answers" block) and the question is DELETED from this file - one command does both:
`python tools/qa_append.py <topic> <file with the answer lines> --close "<words from the question>"`. Every answer ever given (word for word,
by topic): [docs/answered/README.md](docs/answered/README.md). Format: one `- ` line per question under its topic, today's default in [brackets].

## Still open (newest at the bottom of each topic)

### mobs
- the MOB CURVE spec's questions (research/Mob-Curve-Spec.md; docs/answered/mobs.md "SPEC DONE 2026-10-04"): (1) same-level fights
  = today's Hard [yes]; (2) level gap: 5 levels free, then -2.5% of your damage / +1.5% of its damage per level, floor 40% / cap x1.5 [yes];
  (3) the gap counts only for mobs above you, and "your level" = your class weapon skill [yes / yes]; (4) Mana regen +7% per class level
  above 20 [yes]; (6) XP gap rows to free 3 / +8% / -7.5% [keep the locked rows]; (7) a damage floor above Lv 20 [off]; (8) Lv 50-60 grow
  like Hard [yes]; (9) a fixed level by role for bosses [table empty]; (10) Life Steal cap 5% of max Health per second [yes].
  (Question 5, Reforge raises the item level, is answered: Reforge LEVEL UP, cap +6 - docs/answered/gear.md.)

### skills
- OK the new MINING level list = 10 + 5L + 1.5L^2 XP per level (Mining 10 after ~955 XP, 20 after ~5,450)? [as proposed;
  docs/answered/skills.md "LOCKED 2026-10-04 ... for mining specifically"]
- switch the CLASS TREES on now that the /tree probe page looked right in game (2026-10-04)? [recommended ON]
- which of your live Server Setup test values become the pack defaults - Cooking XP multiplier, early gathering XP boost, the
  XP-per-level list, the Copper level band? [today's pack defaults until you say]
- OPEN 2026-10-02 (SkyySkills 0.4.12 review): everyone has 10 base Mana, so Warriors / Archers also get the in-combat Mana refill. Limit it to classes that use Mana (Mage, Priest)? [everyone - harmless today]
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

### gear
- HIDE the vanilla armor box too, by moving all armor Health / resistance into SkyyGear (rides the mob curve build)? [recommended
  yes; docs/answered/gear.md "TESTED 2026-10-04"]

### economy
- Bazaar CLOTH and GEM prices [x2 per tier step, like metals / woods / crops]
- which late-game items can never be bought or sold (the market wall)? [list empty until you name items]

### bags
- OPEN 2026-10-02 (from the SkyySacks 0.7.11 review): carried bags of one type now add up with NO limit, so e.g. 54 Normal bags hold more than a Legendary. Keep unlimited (each extra bag costs a slot and a recipe), or a Server Setup cap on bags counted per type (e.g. 3)? [unlimited]
- OPEN 2026-10-02 (same review): an idle partial stack only tops up once you use it. Also top up the stack in your selected hotbar slot even when idle? [only when used]
- the ACCESSORY TABLE (its own crafting table for accessories + bags, LOCKED 2026-10-02) - still wanted now that the Pocket
  Dimension keeps the Workbench tab? [spec paused until you say]

### classes
- the missing ability picks - every class's A2 alternative and its two improved A1 options (the Priest's A2 alternative too).
  The class-ability spec PROPOSES them after the reset, then you pick. [proposals pending; research/classes/<Class>.md]
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]

### social
- how a player raises the profile cap above 6 (likely ranks). [parked - no way above 6 yet]
