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

### skills
- which of your live Server Setup test values become the pack defaults - Cooking XP multiplier, early gathering XP boost, the
  XP-per-level list, the Copper level band? [today's pack defaults until you say]
- OPEN 2026-10-02 (SkyySkills 0.4.12 review): everyone has 10 base Mana, so Warriors / Archers also get the in-combat Mana refill. Limit it to classes that use Mana (Mage, Priest)? [everyone - harmless today]
- NOTE 2026-10-02 (same review): with the flatter class curve, class level-up coins arrive much faster (xp.properties coinsPerLevel). Your live profiles gained nothing (little class XP yet); check the coin rate before a public launch.

### gear

### economy
- Bazaar CLOTH and GEM prices [x2 per tier step, like metals / woods / crops - built into SkyyBazaar 0.1.4: cloth scraps 4 / 16 / 40 / 96 / 256 / 640, Diamond + Voidstone 120]
- which late-game items can never be bought or sold (the market wall)? [list empty until you name items]

### bags
- OPEN 2026-10-02 (from the SkyySacks 0.7.11 review): carried bags of one type now add up with NO limit, so e.g. 54 Normal bags hold more than a Legendary. Keep unlimited (each extra bag costs a slot and a recipe), or a Server Setup cap on bags counted per type (e.g. 3)? [unlimited]
- OPEN 2026-10-02 (same review): an idle partial stack only tops up once you use it. Also top up the stack in your selected hotbar slot even when idle? [only when used]
- the ACCESSORY TABLE (its own crafting table for accessories + bags, LOCKED 2026-10-02) - still wanted now that the Pocket
  Dimension keeps the Workbench tab? [spec paused until you say]

### classes
- the STAFF / WAND TRAVERSAL spec's 12 questions (research/Magic-Traversal-Spec.md section 7): blink with no free spot [spend Mana], keep falling speed [yes], hop = server push [yes], direct hit = full shot only [yes], burst knockback [off], heal orb = party only + Divinity XP [yes], trail hurts players where PvP is on [yes], pierce count [3], staff quick bonus [+15%], cooldowns [none], glass / fences / leaves block the blink [yes], hide quick.life + read-only rows [yes]
- the missing ability picks - every class's A2 alternative and its two improved A1 options (the Priest's A2 alternative too).
  The class-ability spec PROPOSES them after the reset, then you pick. [proposals pending; research/classes/<Class>.md]
- each class file's "Open" list (e.g. Soul Cage essences + colours for Thorium and up). [see research/classes/]

### social
- how a player raises the profile cap above 6 (likely ranks). [parked - no way above 6 yet]
