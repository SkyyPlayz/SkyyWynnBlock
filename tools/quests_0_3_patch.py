"""Derive SkyyQuests/build_skyyquests_0.3.py from the LIVE generated 0.2 script (build_skyyquests_0.2.py = the tools/deploy_set.py SET pin;
0.2 is left untouched; line endings preserved). Every anchor is asserted; edit THIS file, never the generated script.
Run:  python tools/quests_0_3_patch.py   then   python SkyyQuests/build_skyyquests_0.3.py   (never --deploy)
Check: python SkyyQuests/test_skyyquests_0.3.py [--dir <scratch>] [--keep]

0.3 = QUESTS ROUND Q3 (research/SkyyQuests-Tutorial-Spec.md section 10 row Q3, sections 6 + 7; the TownProbe Q0 code proven in game
2026-10-10). Skyy's words: "We will also want quest markers in the game that appear on more than your map" (2026-10-11) and, for the
round: "Run everything you can in parallel. I want everything on your list done by 5 pm" (2026-10-14). Spec answers that apply
(docs/answered/social.md 2026-10-13): Q6 "Shared, per player where possible (Recommended)", Q8 "Marlow, vanilla fisher look
(Recommended)", Q1 "items and coins on other quest types", Q9 "Feed only". Board lock (world.md 2026-10-09): "Job Board 3 daily /
midnight UTC / ~260 coins -> Yes (Recommended)".
  1. QUEST NPCs (spec 7.1, the SkyyMerchants / TownProbe pattern): /questadmin npc add <board|marlow> places the NPC where the admin
     stands (facing the admin's way), npc remove <id>, npc list. Vanilla roles by name (checked against Assets.zip at build time):
     the Quest Board = Temple_Kweebec_Static (Invulnerable, MotionStatic, no shop - TownProbe #1 / #2), Marlow = Tuluk_Fisherman (the
     vanilla fisher look; Template_Placeholder = Invulnerable, no movement, no shop). Nameplate / DisplayName / PersistentDisplayName,
     Interactable, the vanilla *UseNPC root and OUR hint key server.skyyquests.talkHint "Press [{key}] to talk" (TownProbe #3; the one
     lang line this jar ships - the jar now carries an asset pack). Registry Skyy_SkyyQuests/npcs.tsv (id, world, x, y, z, yaw, uuid +
     ghost lines; written on SkyyQuests-IO, atomic; an unreadable file is never written over). A keeper hop every 2 s - only for worlds
     that hold a registered NPC AND an online player - re-applies the name / Use / hint after a chunk load, re-spawns a registered NPC
     missing 15 s after its chunk loaded (the old UUID becomes a ghost), removes ghosts that load. A RefSystem on NPCs removes ghosts and
     orphans (our role + our NPC name, not registered) the moment they load: never two Marlows.
  2. MARKERS (spec 6): (a) a floating "!" over every quest NPC (TownProbe #4 mode 2 - Skyy saw it: a tiny rubble prop with a Nameplate,
     NonSerialized like SkyyFishing's bobber, so it is never saved and the keeper puts it back after a reload) - shared, everyone sees it;
     (b) PER PLAYER: the vanilla emote particles Question (?) = you have something to hand in here (an active talk task names this NPC)
     and Alerted (!) = this NPC has a quest for you (a line it gives that you have not started, or an undone daily job on the board),
     sent every 2 s only to players within 24 blocks (ParticleUtil with a player list - TownProbe #4 mode 3); Server Setup "Quest NPC
     markers" both / floating ! only / per-player signs only / off; (c) MAP + COMPASS markers: a WorldMapManager marker provider per
     world (TownProbe #9: the engine asks it per player = per player by construction) that answers from a per-player list rebuilt on
     the tick thread ONLY when that player's quest epoch, world, the NPC registry or the widget target changed (the TownProbe log: "the
     real mod must send markers once / on change"); markers: each quest NPC that has a ! / ? for YOU, and the place your widget's task 1
     points at; addIgnoreViewDistance (visible from far, like the vanilla death / respawn markers) + withCompassImage (the vanilla
     compass - UNVERIFIED U3 until Skyy looks); marker ids start with "SkyyQuest" so SkyyHud 0.3.23's minimap draws them as gold
     quest diamonds; quest:fn:markers answers the same list {id, "!" / "?" / "place", x, y, z, label}.
  3. THE HUB QUEST BOARD (spec 7.2): F on the Quest Board opens the board page (no dialogue): Daily Jobs = 3 per PROFILE (one Easy,
     one Medium, one Hard) picked from the pool in Skyy_SkyyQuests/board.properties (copied once; a normal line file with mode=daily +
     task.<n>.tier=1-3; it lives OUTSIDE quests/ so a 0.2 rollback never loads it) by java.util.Random(FNV-1a64(pkey | day)) - the
     TownProbe #12 seed, PASS across a restart and a world change; day = floor((now - board.anchorSeconds) / 86400 s), default midnight
     UTC (Skyy's lock); a job whose objective is hidden / coming soon is replaced by the next one of its tier. Jobs count only after the
     player first used the board (the line starts there) and count anywhere; rewards through the same claim ledger (coins 40 / 80 / 140
     = 260 a day + a small item each - Skyy Q1 "items and coins"; kill jobs: coins + an unidentified weapon + armor piece instead of the
     item - Skyy Q1 "if its a combat quest, unidentified weapons and armor"); progress, done and issued keys carry the day (board.<job>@<day>), so
     a new day = new jobs, a job pays once per day, a restart keeps today's progress; keys older than yesterday are pruned at load and at
     the day change. Track / Claim / Close on the page; "/quests board" opens it within 8 blocks of the board (anywhere with Server
     Setup "Board from anywhere"). The tutorial's "talk to the quest board" part now has its caller (quest:caller:board).
  4. MARLOW + HIS LINE (spec 7.3): quests/fishing_intro.properties (copied once; mode=chain, giver=marlow, every task requires
     fishing:fn:starter = SkyyFishing 0.1.4): F on Marlow -> his dialogue page (Skyy_SkyyQuests/dialogue/marlow.properties, copied
     once): 3 offer pages, "Take the pole" / "Not now". Accepting starts the line, tracks it in the widget and completes "Take Marlow's
     fishing pole" (talk) = ONE claim pole:starter -> SkyyFishing's fishing:fn:starter makes the Wooden Fishing Rod with the Wooden Reel
     fitted, stamped with the claim's grant id; given storage-first with a count before / after (the gear-bag path) - ONCE per profile:
     issued.fishing_intro.take_pole is never removed, the claim ledger pays at most once, and a give whose grant id is already on a
     rod in the inventory (fishing:fn:grantOf) is not given again (a /questadmin repay after a crash). Then "Catch a fish"
     (fishing:catch, sent by SkyyFishing 0.1.4) and "Show Marlow your catch" (talk) -> coins + items. Without SkyyFishing 0.1.4 the line
     is hidden and Marlow says the fish are not biting. The pole is a plain SkyyFishing rod (NOT a SkyyGear lifelong tool - that needs
     SkyyGear's gear:fn:grant / lifelong flag, a SkyyGear round; noted for Skyy).
  5. DIALOGUE PAGES (spec 7.4): the TownProbe page made permanent (kit page, inline, portrait = an ItemIcon of the dialogue's icon item,
     wrapped text, Next / accept / decline / Close; opens on the NEXT tick via World.execute, never inside the Use handler; F presses
     within 250 ms of each other count once).
FIX ROUND (critics 2026-10-14): B1 the floating "!" is removed before a re-spawn / an unloaded area drops its link (never two); B2
  quest:caller:board exists only while the Daily jobs board is on, a board line is loaded and a Quest Board is placed (re-checked on
  place / remove, Server Setup, /questadmin reload); C2 kill jobs pay coins + gear:weapon + gear:armor (Skyy Q1, newest - the "board =
  never gear" line was a cloud draft); C3 Server Setup rows "Daily jobs per day" (1-3) and "Daily job coins (percent)" (0-300; no coin cap
  row: 3 jobs x 300 % = 780 < the spec's 1000). Not changed: the pole stays a plain SkyyFishing rod (lifelong = a SkyyGear round, asked);
  no Fishing XP (Skyy Q1 "items and coins", the 0.2 rule "no XP on shipped lines"); no hook / line / sinker (SkyyFishing has no plain T1
  part - its parts are perks; a crafted rod starts the same way).
FIX ROUND 2 (critics 2026-10-14): the board's reward column 300 -> 380 px (the kill jobs' "+1 unidentified armor" was cut off; build
  check: every shipped job's name + reward text at 300 % fits one line); the floating "!" stands only over an NPC that offers something
  (Marlow without SkyyFishing 0.1.4 = none; it is shared, so it stays after one player finished the line - "Your signs only" is the
  per-player choice); a floating "!" of an NPC removed / moved by an admin in ANOTHER world waits in a queue for that world's keeper
  (never left floating). Rejected: Skip on "Catch a fish" stays (Skyy: "any tutorial quest can be bypassed"; the skipped task still
  pays when done later); gear on every kill job stays until Skyy answers (asked); grantOf keeps the ItemStack (gear:fn:box does too).
Unchanged: the 0.2 tutorial / area lines, rewards, the widget contract (quest:fn:hud), the claim ledger, lag rules.
SAVED DATA: new files npcs.tsv, board.properties, dialogue/marlow.properties, quests/fishing_intro.properties (copied once); profile files
  gain board.<job>@<day> keys (0.2 keeps unknown keys as they are). No one-time migration of existing files (PROJECT-RULES 4 not needed:
  only new files and new keys). ROLLBACK to 0.2: safe - 0.2 ignores board.properties / npcs.tsv / the dialogue folder; it loads
  quests/fishing_intro.properties as a normal line (the pole:starter reward is reported as bad and dropped, nothing can start the line
  without the NPC) and the NPC entities stay in the world as plain vanilla NPCs - run /questadmin npc remove board and marlow BEFORE a
  rollback (else remove them by hand). An unpaid "pole|" claim in a profile file is dropped by 0.2 as LOST? (have the player run /quests
  claim first).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "SkyyQuests")
CR, LF = chr(13), chr(10)
raw = open(os.path.join(D, "build_skyyquests_0.2.py"), encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.2"\n' in s and "QNpc" not in s, "the source must be the generated 0.2 script"
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:200])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3 = QUESTS ROUND Q3"):].rstrip() + "\n"

# ================================================================= docstring + version
rep('''"""SkyyQuests 0.2 - build script (javassist via jpype). Derived from the LIVE SkyyQuests 0.1 build script (a full script, no patch
chain - 0.1 was a new mod). Run:   python SkyyQuests/build_skyyquests_0.2.py   -> SkyyQuests/SkyyQuests-0.2.jar   (never --deploy)
Check: python SkyyQuests/test_skyyquests_0.2.py --dir <empty folder inside tools/dev/scratch/>
''', '''"""SkyyQuests 0.3 - build script (javassist via jpype). GENERATED by tools/quests_0_3_patch.py from build_skyyquests_0.2.py (the 0.2
script was a full script derived from 0.1) - edit the patch, never this file.
Run:   python SkyyQuests/build_skyyquests_0.3.py   -> SkyyQuests/SkyyQuests-0.3.jar   (never --deploy)
Check: python SkyyQuests/test_skyyquests_0.3.py [--dir <folder inside tools/dev/scratch/>] [--keep]

''' + NOTE + '''
--- 0.2 notes (still true unless 0.3 above says otherwise) ---
''')
rep('VERSION = "0.2"\n', 'VERSION = "0.3"\n')

# ================================================================= Python data: Marlow's line, the board pool, the NPCs, the dialogue
rep('''_ALL_IDS = [t[0] for t in TUT] + [t[0] for l_ in AREA_LINES for t in l_[4]]
assert len(_ALL_IDS) == len(set(_ALL_IDS))
''', '''_ALL_IDS = [t[0] for t in TUT] + [t[0] for l_ in AREA_LINES for t in l_[4]]
assert len(_ALL_IDS) == len(set(_ALL_IDS))

# ================= 0.3 (Quests Q3): Marlow's FISHING line, the hub BOARD's daily jobs, the quest NPCs, Marlow's dialogue =================
POLE_NAME = "Wooden Fishing Rod"        # SkyyFishing 0.1.1+ shows SkyyFishing_Rod_Bamboo (T0) as the Wooden Fishing Rod
POLE_REQ = "fishing:fn:starter"         # SkyyFishing 0.1.4 (the pole maker); without it the whole line is hidden
# (id, name, where, hint, reward, any, parts, requires, flags) - the 0.2 TUT tuple shape
FISH_LINE = ("fishing_intro", "Marlow's Lesson", 55, "marlow", [
    ("take_pole", "Take Marlow's fishing pole", "npc:marlow", "Talk to Marlow at the pier", "pole:starter,coins:25", False,
     [("talk", "marlow", 1, {})], POLE_REQ, {}),
    ("catch_fish", "Catch a fish", "", "Right click deep water with the rod - click fast when it bites", "coins:25,item:Food_Bread:2", False,
     [("event", "fishing:catch", 1, {"caller": "fishing"})], POLE_REQ, {}),
    ("show_marlow", "Show Marlow your catch", "npc:marlow", "Marlow waits at the pier", "coins:50,item:Food_Fish_Grilled:3", False,
     [("talk", "marlow", 1, {})], POLE_REQ, {}),
])
# the daily job pool (Zone1 spec 3.1 shapes with today's counted objectives; 40 / 80 / 140 coins = Skyy's ~260 a day). FIX (critic C2):
# Skyy Q1 2026-10-13 (social.md, newest; the 0.2 tutorial follows it) "if its a combat quest, unidentified weapons and armor for your class
# at your level. items and coins on other quest types." -> the kill jobs pay coins + an unidentified weapon + armor piece, the rest coins + an
# item. (The old "board = never gear" line was a cloud draft, research/cloud/SkyyQuests-Zone1-Spec.md, never Skyy's words.)
BOARD_POOL = [  # (id, name, hint, reward, any, parts, requires, tier)
    ("hunt10", "Defeat 10 mobs", "Any mob counts", "coins:40,gear:weapon,gear:armor", False, [("kill", "any", 10, {})], "", 1),
    ("logs32", "Chop 32 logs", "Fell whole trees", "coins:40,item:Plant_Sapling_Oak:2", True,
     [("felled", "Wood_*_Trunk*", 32, {}), ("break", "Wood_*_Trunk", 32, {})], "", 1),
    ("wheat24", "Harvest 24 wheat", "Ripe wheat only", "coins:40,item:Plant_Seeds_Wheat:4", False, [("gather", "Plant_Crop_Wheat_Item", 24, {})], "", 1),
    ("stone64", "Mine 64 stone", "Any stone counts", "coins:40,item:Food_Bread:2", False, [("break", "Rock_Stone*", 64, {})], "", 1),
    ("copper20", "Mine 20 copper ore", "Copper shows orange in the rock", "coins:80,item:Ingredient_Bar_Copper:2", False, [("break", "Ore_Copper*", 20, {})], "", 2),
    ("hunt20", "Defeat 20 mobs", "Any mob counts", "coins:80,gear:weapon,gear:armor", False, [("kill", "any", 20, {})], "", 2),
    ("fish5", "Catch 5 fish", "Any fish counts", "coins:80,item:Food_Fish_Grilled:2", False, [("event", "fishing:catch", 5, {"caller": "fishing"})], "config:def:SkyyFishing", 2),
    ("iron15", "Mine 15 iron ore", "Iron sits deeper than copper", "coins:140,item:Ingredient_Bar_Iron:2", False, [("break", "Ore_Iron*", 15, {})], "", 3),
    ("hunt40", "Defeat 40 mobs", "Any mob counts", "coins:140,gear:weapon,gear:armor", False, [("kill", "any", 40, {})], "", 3),
    ("fish15", "Catch 15 fish", "Any fish counts", "coins:140,item:Food_Fish_Grilled:4", False, [("event", "fishing:catch", 15, {"caller": "fishing"})], "config:def:SkyyFishing", 3),
]
assert sorted(set(j[7] for j in BOARD_POOL)) == [1, 2, 3] and len(set(j[0] for j in BOARD_POOL)) == len(BOARD_POOL)
for _j in BOARD_POOL:
    if _j[5][0][0] == "kill":     # Skyy Q1: combat = unidentified weapon + armor (+ the board's coins), no item
        assert "gear:weapon" in _j[3] and "gear:armor" in _j[3] and "item:" not in _j[3], "Skyy Q1: a combat job pays gear (%s)" % _j[0]
    else:
        assert "coins:" in _j[3] and "item:" in _j[3] and "gear:" not in _j[3], "Skyy Q1: items + coins on other job types (%s)" % _j[0]
    assert int(_j[3].split(",")[0].split(":")[1]) == {1: 40, 2: 80, 3: 140}[_j[7]], _j[0]
_ALL3 = _ALL_IDS + [t[0] for t in FISH_LINE[4]] + [j[0] for j in BOARD_POOL]
assert len(_ALL3) == len(set(_ALL3)), "task ids must be unique across the shipped lines"
# the quest NPCs: (id, nameplate, vanilla role, kind, dialogue portrait item, floating-marker height above the feet)
NPCS = [("board", "Quest Board", "Temple_Kweebec_Static", "board", "Furniture_Village_Sign", 2.3),
        ("marlow", "Marlow", "Tuluk_Fisherman", "talk", "Food_Fish_Raw", 2.7)]
NPC_PROP_MODEL = "Rubble_Stone_Mossy"   # TownProbe #4 mode 2: the floating "!" = a tiny rubble prop with a Nameplate (Skyy saw it)
MARK_BANG, MARK_ASK = "Alerted", "Question"                      # vanilla emote particles (TownProbe #4 mode 3, short LifeSpan)
IMG_NPC, IMG_PLACE = "Temple_GatewayCTA.png", "Coordinate.png"   # vanilla map marker images (Common/UI/WorldMap/MapMarkers/)
TALK_KEY = "skyyquests.talkHint"                                 # OUR lang key (server.lang merged per key; TownProbe #3)
MARLOW_DLG = "\\n".join([
    "# Marlow's dialogue (SkyyQuests 0.3; copied ONCE - your edits stay). offer.N = the pages before Take the pole; turnin.<task> = what",
    "# he says when that talk task completes; task.<task> = while that task is your next one; done = after the whole line; closed = when",
    "# the line is hidden (no SkyyFishing 0.1.4). icon = the portrait item. /questadmin reload re-reads this folder.",
    "name=Marlow",
    "icon=Food_Fish_Raw",
    "line=fishing_intro",
    "offer.1=Ahoy there! New to the hub? The water round here is full of fish, and nobody new should go without a rod.",
    "offer.2=Take this old pole of mine. It has a Wooden Reel on it already. Hooks, lines and sinkers you can craft at a Fishing Bench later on.",
    "offer.3=Catch me one fish and come back to show me. Deal?",
    "accept=Take the pole",
    "decline=Not now",
    "turnin.take_pole=There you go. Right click deep water to cast, wait for the bite, then click fast to reel it in.",
    "task.catch_fish=Deep water, a steady hand, and click fast when it bites. Come back with a fish!",
    "turnin.show_marlow=Now that is a fish! Keep at it. The Fishing Bench buys and fillets whatever you catch.",
    "done=Good to see you again. The fish are biting today.",
    "closed=The fish are not biting today. Come back another time.",
]) + "\\n"

''')
# 0.3 build checks after the reward items / names are read from Assets.zip
rep('''assert all(32 <= ord(_c) < 127 for _n in ITEM_NAMES for _c in _n), ITEM_NAMES
''', '''assert all(32 <= ord(_c) < 127 for _n in ITEM_NAMES for _c in _n), ITEM_NAMES
# build checks against Assets.zip (read-only): reward items, roles + their templates (Invulnerable, no shop), icons, particles, markers
with _zf.ZipFile(_AZ) as _z:
    _AZN = set(_z.namelist())
    _ROLE_JSON = dict((_n.rsplit("/", 1)[1][:-5], _n) for _n in _AZN if _n.startswith("Server/NPC/Roles/") and _n.endswith(".json"))
    for _nid, _nm, _role, _kind, _icon, _h in NPCS:
        assert _role in _ROLE_JSON, "vanilla role %s missing (%s)" % (_role, _nid)
        _rj = json.loads(_z.read(_ROLE_JSON[_role]).decode("utf-8-sig"))
        _tp = _rj.get("Reference")
        assert _tp in _ROLE_JSON, "role %s template %s missing" % (_role, _tp)
        _tj = _z.read(_ROLE_JSON[_tp]).decode("utf-8-sig")
        assert '"Invulnerable": true' in _tj, "role %s (template %s) is not Invulnerable" % (_role, _tp)
        assert "InteractionInstruction" not in _tj + json.dumps(_rj), "role %s would open a vanilla shop" % _role
        assert _icon in _ITEM_IDS, "portrait item %s missing" % _icon
    assert "Server/Models/Projectiles/Items/Rubble/%s.json" % NPC_PROP_MODEL in _AZN or any(_n.endswith("/%s.json" % NPC_PROP_MODEL) and _n.startswith("Server/Models/") for _n in _AZN), NPC_PROP_MODEL
    for _ps in (MARK_BANG, MARK_ASK):
        _pp = [_n for _n in _AZN if _n.endswith("/%s.particlesystem" % _ps)]
        assert _pp, "particle system %s missing" % _ps
        _pj = json.loads(_z.read(_pp[0]).decode("utf-8-sig"))
        assert isinstance(_pj.get("LifeSpan"), (int, float)) and _pj["LifeSpan"] <= 5, "particle %s has no short LifeSpan" % _ps
    for _mk in (IMG_NPC, IMG_PLACE):
        assert "Common/UI/WorldMap/MapMarkers/" + _mk in _AZN, "map marker image %s missing" % _mk
    _L3 = _z.read("Server/Languages/en-US/server.lang").decode("utf-8", "replace")
assert TALK_KEY not in _L3, "vanilla server.lang already has %s" % TALK_KEY
assert not [_k for _k in _L3.splitlines() if _k.startswith("interactionHints.") and "talk" in _k.split("=")[0].lower()], "vanilla now has a talk hint - use it"
for _t in FISH_LINE[4] + [(j[0], j[1], "", j[2], j[3], j[4], j[5], j[6], {}) for j in BOARD_POOL]:
    for _r in _t[4].split(","):
        if _r.startswith("item:"):
            assert _r.split(":")[1] in _ITEM_IDS, "reward item %s of %s is not in Assets.zip" % (_r, _t[0])
for _b in ("Ore_Iron", "Ore_Copper", "Rock_Stone"):
    assert [_i for _i in _ITEM_IDS if _i.startswith(_b)], _b
ASSETS = {"Server/Languages/en-US/server.lang": "%s = Press [{key}] to talk\\n" % TALK_KEY}
''')
# Assets.zip sits next to the INSTALLED server jar (B.SERVER_JAR is a cached copy in tools/dev/scratch/serverjar since 2026-10-13 - the
# 0.2 path would point into that folder); Python's zipfile reads it read-only, no JVM holds it
# FIX (critic C3): a daily job's coins x Server Setup "Daily job coins (percent)" (rewardOf feeds the claims, the page and the widget)
rep('''M(defs, r"""
public static String rewardOf(@PKG@.QLine l, @PKG@.QTask t) {
  String r = t.reward == null ? "" : t.reward;
  if (!"tutorial".equals(l.id)) return r;''', '''M(defs, r"""
public static String boardScale(String r) {
  int pc = @PKG@.QCfg.BOARD_SCALE;
  if (pc == 100 || r == null) return r;
  String[] a = r.split(",");
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    String x = a[i].trim();
    if (x.startsWith("coins:")) {
      long n = @PKG@.QLog.num(x.substring(6), 0L) * (long) pc / 100L;
      if (n <= 0L) continue;
      x = "coins:" + n;
    }
    if (x.length() == 0) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(x);
  }
  return sb.toString();
}""")
M(defs, r"""
public static String rewardOf(@PKG@.QLine l, @PKG@.QTask t) {
  String r = t.reward == null ? "" : t.reward;
  if (l.daily) return boardScale(r);                              // 0.3 FIX C3: the board's coin percent
  if (!"tutorial".equals(l.id)) return r;''')
rep('''_AZ = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")      # read-only''',
    '''_AZ = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")      # read-only (0.3: the installed game folder)''')
# the shipped reward items of the new lines get the game's English names too
rep('''_REW_ITEMS = sorted(set(_r.split(":")[1] for _t in TUT + TUT01 + [t for l_ in AREA_LINES for t in l_[4]] for _r in _t[4].split(",") if _r.startswith("item:")))''',
    '''_REW_ITEMS = sorted(set(_r.split(":")[1] for _t in TUT + TUT01 + [t for l_ in AREA_LINES for t in l_[4]] + list(FISH_LINE[4]) + [(j[0], j[1], "", j[2], j[3]) for j in BOARD_POOL] for _r in _t[4].split(",") if _r.startswith("item:")))''')

# the new line texts (after line_text exists): Marlow's chain line + the board pool (mode=daily, tier per task)
rep('''AREAS_TEXT = "\\n".join([''', '''

def line_text3(lid, name, mode, giver, order, tasks, head, tiers=None):
    """0.3: a line with giver= (the NPC that offers it) and, on a daily line, task.<n>.tier"""
    t_ = line_text(lid, name, mode, False, "", tasks, head, order=order)
    t_ = t_.replace("\\nauto=false\\n", "\\nauto=false\\ngiver=%s\\n" % giver, 1)
    if tiers:
        for n_, tr in enumerate(tiers, 1):
            a_ = "task.%d.id=%s\\n" % (n_, tasks[n_ - 1][0])
            assert t_.count(a_) == 1
            t_ = t_.replace(a_, a_ + "task.%d.tier=%d\\n" % (n_, tr), 1)
    return t_


_HEAD03 = _HEAD02 + [
    "0.3: giver=<npc id> = the quest NPC that offers this line (it is started by talking to that NPC); mode=daily (board.properties)",
    "= 3 jobs a day per profile, one per task.<n>.tier (1 Easy, 2 Medium, 3 Hard), picked from this pool; reward pole:starter =",
    "SkyyFishing's starter rod (once)."]
FISH_TEXT = line_text3(FISH_LINE[0], FISH_LINE[1], "chain", FISH_LINE[3], FISH_LINE[2], FISH_LINE[4], _HEAD03)
BOARD_TEXT = line_text3("board", "Daily Jobs", "daily", "board", 90,
                        [(j[0], j[1], "", j[2], j[3], j[4], j[5], j[6], {}) for j in BOARD_POOL],
                        ["SkyyQuests DAILY JOBS (the hub Quest Board; SkyyQuests 0.3) - copied ONCE, your edits stay. Each day every profile gets",
                         "3 jobs: one task of tier 1, one of tier 2, one of tier 3, picked from this pool by a seed of the profile + the day (the",
                         "same after a restart). Rewards here (coins + items; kill jobs coins + gear:weapon,gear:armor = unidentified class gear at your",
                         "level, Skyy Q1). Server Setup > Quests > NPCs and board: jobs per day, coin percent, Daily reset. The",
                         "objective grammar is the quest-line grammar (quests/tutorial.properties)."],
                        tiers=[j[7] for j in BOARD_POOL])
AREAS_TEXT = "\\n".join([''')

# ================================================================= config: new keys + rows
rep('''    "coop.partyKills=true",
''', '''    "coop.partyKills=true",
    "markers.npc=both",
    "markers.map=true",
    "board.enabled=true",
    "board.anchorSeconds=0",
    "board.remote=false",
    "board.jobsPerDay=3",
    "board.coinScalePercent=100",
''')
rep('''           "public static volatile boolean FOLLOW = true;", "public static volatile boolean PARTY_KILLS = true;",   # 0.2
''', '''           "public static volatile boolean FOLLOW = true;", "public static volatile boolean PARTY_KILLS = true;",   # 0.2
           "public static volatile String MARK_NPC = \\"both\\";", "public static volatile boolean MARK_MAP = true;",          # 0.3
           "public static volatile boolean BOARD_ON = true;", "public static volatile int BOARD_ANCHOR = 0;",
           "public static volatile boolean BOARD_REMOTE = false;",
           "public static volatile int BOARD_JOBS = 3;", "public static volatile int BOARD_SCALE = 100;",                  # 0.3 FIX (critic C3)
''')
rep('''    PARTY_KILLS = @PKG@.QLog.bool(p.getProperty("coop.partyKills"), true);      // 0.2: party=true kill parts credit the party
''', '''    PARTY_KILLS = @PKG@.QLog.bool(p.getProperty("coop.partyKills"), true);      // 0.2: party=true kill parts credit the party
    String mn = p.getProperty("markers.npc", "both").trim().toLowerCase(java.util.Locale.ROOT);         // 0.3
    MARK_NPC = (mn.equals("off") || mn.equals("prop") || mn.equals("particle") || mn.equals("both")) ? mn : "both";
    MARK_MAP = @PKG@.QLog.bool(p.getProperty("markers.map"), true);
    BOARD_ON = @PKG@.QLog.bool(p.getProperty("board.enabled"), true);
    BOARD_ANCHOR = clampI(@PKG@.QLog.num(p.getProperty("board.anchorSeconds"), 0L), 0, 86399);
    BOARD_REMOTE = @PKG@.QLog.bool(p.getProperty("board.remote"), false);
    BOARD_JOBS = clampI(@PKG@.QLog.num(p.getProperty("board.jobsPerDay"), 3L), 1, 3);              // FIX C3: 1 Easy / 2 + Medium / 3 + Hard
    BOARD_SCALE = clampI(@PKG@.QLog.num(p.getProperty("board.coinScalePercent"), 100L), 0, 300);   // FIX C3: board coins x percent
''')
# 0.3 helpers on QCfg: the marker style switches
rep('''# "<coins>,<Skill:N or empty>" -> { coins, xp } or null (a bad line is ignored, the quest file's reward stays)''',
    '''M(cfg, "public static boolean propsOn() { String m = MARK_NPC; return ENABLED && (\\"both\\".equals(m) || \\"prop\\".equals(m)); }")          # 0.3
M(cfg, "public static boolean particlesOn() { String m = MARK_NPC; return ENABLED && (\\"both\\".equals(m) || \\"particle\\".equals(m)); }")
# "<coins>,<Skill:N or empty>" -> { coins, xp } or null (a bad line is ignored, the quest file's reward stays)''')
rep('''Q_CFG_CATS = [("parts", "Parts"), ("tutorial", "Tutorial"), ("widget", "Widget"), ("timing", "Timing")]''',
    '''Q_CFG_CATS = [("parts", "Parts"), ("tutorial", "Tutorial"), ("widget", "Widget"), ("timing", "Timing"), ("npcs", "NPCs and board")]''')
rep('''    ("quests.event.rate", "Quest events per second", "timing", "int", "20", "1", "100", "step=1", "", "live",
     "Most quest events one player may send per second; extra ones are dropped (logged once).",
     "field:QCfg.EVENT_RATE@config.properties:event.rate"),
]''', '''    ("quests.event.rate", "Quest events per second", "timing", "int", "20", "1", "100", "step=1", "", "live",
     "Most quest events one player may send per second; extra ones are dropped (logged once).",
     "field:QCfg.EVENT_RATE@config.properties:event.rate"),
    # 0.3 (Quests Q3): markers, the board
    ("quests.markers.npc", "Quest NPC markers", "npcs", "choice", "both", "", "",
     "both|! and your signs,prop|Floating ! only,particle|Your signs only,off|Off", "", "live",
     "Floating ! = all see it, over NPCs with a quest on. Own signs: ? = hand in, ! = new quest, only you.",
     "field:QCfg.MARK_NPC@config.properties:markers.npc;after=QHooks.cfgChanged"),
    ("quests.markers.map", "Map and compass markers", "npcs", "bool", "true", "", "", "", "", "live",
     "Quest NPCs with something for you and your next task's place show on the map and compass.",
     "field:QCfg.MARK_MAP@config.properties:markers.map;after=QHooks.cfgChanged"),
    ("quests.board.enabled", "Daily jobs board", "npcs", "bool", "true", "", "", "", "", "live",
     "The Quest Board's 3 daily jobs per profile. Off = the board is closed (progress is kept).",
     "field:QCfg.BOARD_ON@config.properties:board.enabled;after=QHooks.cfgChanged"),
    ("quests.board.anchorSeconds", "Daily reset (after UTC midnight)", "npcs", "int", "0", "0", "86399", "step=60", "s", "live",
     "New daily jobs start this many seconds after midnight UTC. 0 = midnight UTC.",
     "field:QCfg.BOARD_ANCHOR@config.properties:board.anchorSeconds;after=QHooks.cfgChanged"),
    ("quests.board.remote", "Board from anywhere", "npcs", "bool", "false", "", "", "", "", "live",
     "On = /quests board opens the daily jobs anywhere. Off = only within 8 blocks of the Quest Board.",
     "field:QCfg.BOARD_REMOTE@config.properties:board.remote"),
    # FIX (critic C3, PROJECT-RULES "everything a server owner might change is editable in game"; Zone1 spec 9 board.jobsPerDay /
    # board.coinScalePercent). No daily coin cap row: at most 3 jobs a day x 300 % = 780 coins, under the spec's 1000 cap.
    ("quests.board.jobsPerDay", "Daily jobs per day", "npcs", "int", "3", "1", "3", "step=1", "", "live",
     "1 = an Easy job only, 2 = Easy + Medium, 3 = Easy + Medium + Hard.",
     "field:QCfg.BOARD_JOBS@config.properties:board.jobsPerDay;after=QHooks.cfgChanged"),
    ("quests.board.coinScalePercent", "Daily job coins (percent)", "npcs", "int", "100", "0", "300", "step=10", "%", "live",
     "Each daily job's coins times this percent (100 = 40 / 80 / 140). Items and gear stay the same.",
     "field:QCfg.BOARD_SCALE@config.properties:board.coinScalePercent;after=QHooks.cfgChanged"),
]''')
rep('''FILES=["Skyy_SkyyQuests/config.properties"], NOTE="Also: /questadmin reload | check | list | set | repay | place. Areas: areas.properties.",''',
    '''FILES=["Skyy_SkyyQuests/config.properties"], NOTE="Also: /questadmin reload | check | list | set | repay | place | npc. Daily jobs: board.properties.",''')

# ================================================================= definitions: QLine / QTask fields, the loader, rewards
rep('''           "public int order = 100;", "public String area = \\"\\";", "public String shortAfter = \\"\\";"):     # 0.2''',
    '''           "public int order = 100;", "public String area = \\"\\";", "public String shortAfter = \\"\\";",     # 0.2
           "public boolean daily;", "public String giver = \\"\\";"):                                             # 0.3''')
rep('''           "public boolean optional;", "public boolean island;", "public boolean tut;"):       # 0.2''',
    '''           "public boolean optional;", "public boolean island;", "public boolean tut;",       # 0.2
           "public int tier;"):                                                                    # 0.3: a daily job's tier 1-3''')
rep('''F(defs, "public static final String[] LINE_FILES = %s;" % jarr([l_[0] + ".properties" for l_ in AREA_LINES]))
F(defs, "public static final String[] LINE_TEXTS = new String[] { %s };" % ", ".join(jbig(t_) for _i, t_ in AREA_TEXTS))''',
    '''F(defs, "public static final String[] LINE_FILES = %s;" % jarr([l_[0] + ".properties" for l_ in AREA_LINES] + [FISH_LINE[0] + ".properties"]))   # 0.3: + Marlow's line
F(defs, "public static final String[] LINE_TEXTS = new String[] { %s };" % ", ".join([jbig(t_) for _i, t_ in AREA_TEXTS] + [jbig(FISH_TEXT)]))
F(defs, "public static final String BOARD_TEXT = %s;" % jbig(BOARD_TEXT))                   # 0.3: board.properties (copied once)
F(defs, "public static java.nio.file.Path BOARD_FILE;")
F(defs, "public static volatile @PKG@.QLine BOARD;")                                         # 0.3: the daily line (giver board) or null
F(defs, "public static volatile java.util.Map NPCPLACES = new java.util.HashMap();")         # 0.3: "<npc id>" -> QPlace (QNpc keeps it)
F(defs, "public static volatile long TEST_NOW = 0L;")                                        # harness: the clock of the board day
F(defs, "public static volatile long DAYMAX = Long.MIN_VALUE;")                              # the board day never goes back in one run
F(defs, "public static final String POLE_NAME = %s;" % jstr(POLE_NAME))''')
rep('''  if (!mode.equals("open") && !mode.equals("chain")) err.add(file + ": mode=" + mode + " (open or chain) - open used");
  l.chain = mode.equals("chain");''', '''  if (!mode.equals("open") && !mode.equals("chain") && !mode.equals("daily")) err.add(file + ": mode=" + mode + " (open, chain or daily) - open used");
  l.chain = mode.equals("chain");
  l.daily = mode.equals("daily");                                                   // 0.3: the board's daily jobs
  l.giver = p.getProperty("giver", "").trim();                                      // 0.3: the quest NPC that offers this line''')
rep('''    t.tut = @PKG@.QLog.bool(p.getProperty(pre + "tut"), false);
''', '''    t.tut = @PKG@.QLog.bool(p.getProperty(pre + "tut"), false);
    t.tier = (int) @PKG@.QLog.num(p.getProperty(pre + "tier"), 0L);                  // 0.3
    if (l.daily && (t.tier < 1 || t.tier > 3)) { err.add(where + " (" + t.id + "): tier must be 1, 2 or 3 on a daily line (1 used)"); t.tier = 1; }
''')
rep('''    if (p[0].equals("gear") && p.length == 2) {                       // 0.2: gear:weapon / gear:armor (an unidentified bag, SkyyGear)''',
    '''    if (p[0].equals("pole") && p.length == 2 && p[1].equals("starter")) continue;    // 0.3: SkyyFishing's starter rod (fishing:fn:starter)
    if (p[0].equals("gear") && p.length == 2) {                       // 0.2: gear:weapon / gear:armor (an unidentified bag, SkyyGear)''')
rep('''    return "'" + x + "' is not coins:N, xp:<Skill>:N, item:<id>:N (1-1000), gear:weapon, gear:armor or flag:<name>";''',
    '''    return "'" + x + "' is not coins:N, xp:<Skill>:N, item:<id>:N (1-1000), gear:weapon, gear:armor, pole:starter or flag:<name>";''')
rep('''    else if (p[0].equals("gear") && p.length == 2) x = p[1].equals("armor") ? "+1 unidentified armor" : "+1 unidentified weapon";     // 0.2''',
    '''    else if (p[0].equals("gear") && p.length == 2) x = p[1].equals("armor") ? "+1 unidentified armor" : "+1 unidentified weapon";     // 0.2
    else if (p[0].equals("pole") && p.length == 2) x = "+1 " + POLE_NAME;                                                              // 0.3''')
# the board day + the FNV seed (TownProbe #12) + npc:<id> places
rep('''M(defs, r"""
public static @PKG@.QPlace place(String id) {
  if (id == null || id.length() == 0) return null;
  Object o = PLACES.get(id);''', '''# 0.3: the board day = floor((now - anchor) / 86400 s) (TownProbe #12 PASS); never goes back within one run (an anchor change)
M(defs, r"""
public static long day() {
  long now = TEST_NOW != 0L ? TEST_NOW : System.currentTimeMillis();
  long d = Math.floorDiv(now / 1000L - (long) @PKG@.QCfg.BOARD_ANCHOR, 86400L);
  long m = DAYMAX;
  if (d < m) return m;
  DAYMAX = d;
  return d;
}""")
M(defs, r"""
public static long leftSeconds() {
  long now = TEST_NOW != 0L ? TEST_NOW : System.currentTimeMillis();
  return 86400L - Math.floorMod(now / 1000L - (long) @PKG@.QCfg.BOARD_ANCHOR, 86400L);
}""")
# FNV-1a 64 over the UTF-16 chars (TownProbe #12: the same answer in every JVM, after a restart and a world change)
M(defs, r"""
public static long fnv(String s) {
  long h = 0xcbf29ce484222325L;
  if (s == null) return h;
  for (int i = 0; i < s.length(); i++) { h = h ^ (long) s.charAt(i); h = h * 0x100000001b3L; }
  return h;
}""")
M(defs, r"""
public static @PKG@.QPlace place(String id) {
  if (id == null || id.length() == 0) return null;
  if (id.startsWith("npc:")) { Object n = NPCPLACES.get(id.substring(4)); return n instanceof @PKG@.QPlace ? (@PKG@.QPlace) n : null; }   // 0.3
  Object o = PLACES.get(id);''')
# the loader: board.properties (outside quests/) is copied once and joins the lines
rep('''  } catch (Throwable t) { err.add("quests folder: " + t); }
  // 0.2: lines by order (stable: equal orders keep the file-name order) - the widget's flow tutorial -> area lines''',
    '''  } catch (Throwable t) { err.add("quests folder: " + t); }
  @PKG@.QLine bl = null;                                    // 0.3: the board's daily jobs (board.properties, copied once)
  try {
    if (BOARD_FILE != null) {
      if (!java.nio.file.Files.exists(BOARD_FILE, new java.nio.file.LinkOption[0])) {
        @PKG@.QLog.writeAtomic(BOARD_FILE, BOARD_TEXT);
        @PKG@.QLog.info("wrote the shipped daily jobs to board.properties (copied once - edits stay)");
      }
      @PKG@.QLine l = parse(@PKG@.QLog.readProps(BOARD_FILE), "board.properties", err);
      if (l != null) {
        boolean dup = false;
        for (int i = 0; i < out.size(); i++) if (((@PKG@.QLine) out.get(i)).id.equals(l.id)) dup = true;
        if (dup) err.add("board.properties: line " + l.id + " is already defined by a quests/ file - skipped");
        else if (!l.daily) err.add("board.properties: mode must be daily - the board is skipped");
        else { out.add(l); bl = l; }
      }
    }
  } catch (Throwable t) { err.add("board.properties: " + t); }
  BOARD = bl;
  // 0.2: lines by order (stable: equal orders keep the file-name order) - the widget's flow tutorial -> area lines''')

# ================================================================= QState: the daily pick cache
rep('''           "public String track = \\"\\";", "public int seq;", "public long ver;", "public long saved;", "public boolean frozen;",''',
    '''           "public long jobDay = Long.MIN_VALUE;", "public int[] jobs;", "public Object jobLine;",          # 0.3: today's daily picks (memory)
           "public int jobN;",                                                                              # FIX C3: picked for this jobs-per-day
           "public String track = \\"\\";", "public int seq;", "public long ver;", "public long saved;", "public boolean frozen;",''')

# ================================================================= QEng part A: daily keys, picks, the board switch, NPC marks, pruning
rep('''  if ("tutorial".equals(l.id) && !@PKG@.QCfg.TUT_ON) return false;''',
    '''  if ("tutorial".equals(l.id) && !@PKG@.QCfg.TUT_ON) return false;
  if (l.daily && !@PKG@.QCfg.BOARD_ON) return false;                       // 0.3: the board switch''')
rep('''public static String tk(@PKG@.QLine l, @PKG@.QTask t) {
  return l.id + "." + t.id;
}""")''', '''public static String tk(@PKG@.QLine l, @PKG@.QTask t) {
  if (l.daily) return l.id + "." + t.id + "@" + @PKG@.QDefs.day();      // 0.3: a daily job's keys carry the day (once per day)
  return l.id + "." + t.id;
}""")
# 0.3: today's jobs of a daily line for one profile: per tier 1..3 ONE task, java.util.Random(FNV(pkey | day)) (TownProbe #12); a pick that
# is hidden / coming soon moves on to the next task of that tier (file order, wrapping); no task of a tier = no job of that tier
M(eng, r"""
public static int[] pickDaily(@PKG@.QLine l, String pk, long day) {
  java.util.Random r = new java.util.Random(@PKG@.QDefs.fnv(pk + "|" + day));
  int[] tmp = new int[3];
  int c = 0;
  int tiers = @PKG@.QCfg.BOARD_JOBS;                                  // FIX C3: Server Setup "Daily jobs per day" (1-3)
  for (int tier = 1; tier <= tiers; tier++) {
    int n = 0;
    for (int i = 0; i < l.tasks.length; i++) if (l.tasks[i].tier == tier) n++;
    if (n == 0) continue;
    int k = r.nextInt(n);
    int[] idx = new int[n];
    int j = 0;
    for (int i = 0; i < l.tasks.length; i++) if (l.tasks[i].tier == tier) { idx[j] = i; j++; }
    for (int m = 0; m < n; m++) {
      int i = idx[(k + m) % n];
      if (hidden(l.tasks[i]) || soon(l.tasks[i])) continue;
      tmp[c] = i;
      c++;
      break;
    }
  }
  int[] out = new int[c];
  for (int i = 0; i < c; i++) out[i] = tmp[i];
  return out;
}""")
M(eng, r"""
public static int[] picksL(@PKG@.QState s, @PKG@.QLine l) {
  long d = @PKG@.QDefs.day();
  int jn = @PKG@.QCfg.BOARD_JOBS;
  if (s.jobLine == l && s.jobDay == d && s.jobN == jn && s.jobs != null) return s.jobs;
  int[] p = pickDaily(l, s.pk, d);
  s.jobLine = l;
  s.jobDay = d;
  s.jobN = jn;
  s.jobs = p;
  return p;
}""")''')
rep('''public static boolean taskActive(@PKG@.QState s, @PKG@.QLine l, int i) {
  if (!l.chain) return true;''', '''public static boolean taskActive(@PKG@.QState s, @PKG@.QLine l, int i) {
  if (l.daily) {                                                           // 0.3: only today's 3 picks
    int[] p = picksL(s, l);
    for (int k = 0; k < p.length; k++) if (p[k] == i) return true;
    return false;
  }
  if (!l.chain) return true;''')
rep('''    if (hidden(t) || t.optional) continue;                       // 0.2: optional tasks are not counted in "x / y"''',
    '''    if (hidden(t) || t.optional) continue;                       // 0.2: optional tasks are not counted in "x / y"
    if (l.daily && !taskActive(s, l, i)) continue;               // 0.3: a daily line counts today's jobs only''')
# NPC marks + pruning + the talk helpers, right before the state wrappers (they only use part A)
rep('''# the IO job class first (QEng.wake builds one); its run() comes after QPay''', '''# 0.3: the marker of quest NPC `npc` for this profile: 2 = "?" (an active, live talk part names it - something to hand in), 1 = "!" (a line
# it gives that you have not started and that has a visible task, or the daily line it gives has an undone job today), 0 = none
M(eng, r"""
public static int npcMarkL(@PKG@.QState s, String npc) {
  if (s.frozen || !@PKG@.QCfg.ENABLED || npc == null) return 0;
  boolean bang = false;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!lineOn(l)) continue;
    boolean act = l.auto || s.started.containsKey(l.id);
    if (!act) {
      if (!npc.equals(l.giver)) continue;
      for (int i = 0; i < l.tasks.length; i++) if (!hidden(l.tasks[i])) { bang = true; break; }
      continue;
    }
    for (int i = 0; i < l.tasks.length; i++) {
      @PKG@.QTask t = l.tasks[i];
      String k = tk(l, t);
      if (s.done.containsKey(k) || hidden(t) || soon(t) || !taskActive(s, l, i)) continue;
      for (int pi = 0; pi < t.parts.length; pi++) {
        @PKG@.QPart q = t.parts[pi];
        if (q.type == @TTALK@ && !s.pdone.contains(k + "." + pi) && !partSoon(q) && @PKG@.QDefs.matches(q.match, npc)) return 2;
      }
      if (l.daily && npc.equals(l.giver) && !s.skip.containsKey(k)) bang = true;
    }
  }
  return bang ? 1 : 0;
}""")
# 0.3: "<line>.<task>@<day>..." keys of daily lines older than yesterday leave every map (tk never makes those days again; yesterday's
# stay so an anchor change by less than a day can never pay a job twice)
M(eng, r"""
public static boolean oldDay(String k, java.util.HashSet pre, long day) {
  int at = k.indexOf('@');
  if (at <= 0) return false;
  int dot = k.indexOf('.');
  if (dot <= 0 || !pre.contains(k.substring(0, dot + 1))) return false;
  int e = k.indexOf('.', at);
  long d = @PKG@.QLog.num(e < 0 ? k.substring(at + 1) : k.substring(at + 1, e), Long.MAX_VALUE);
  return d < day - 1L;
}""")
M(eng, r"""
public static int pruneIt(java.util.Iterator it, java.util.HashSet pre, long day) {
  int n = 0;
  while (it.hasNext()) { if (oldDay(String.valueOf(it.next()), pre, day)) { it.remove(); n++; } }
  return n;
}""")
M(eng, r"""
public static int pruneDailyL(@PKG@.QState s, long day) {
  if (s.frozen) return 0;
  java.util.HashSet pre = new java.util.HashSet();
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int i = 0; i < ls.length; i++) if (ls[i].daily) pre.add(ls[i].id + ".");
  if (pre.isEmpty()) return 0;
  int n = pruneIt(s.done.keySet().iterator(), pre, day) + pruneIt(s.prog.keySet().iterator(), pre, day) + pruneIt(s.pdone.iterator(), pre, day)
      + pruneIt(s.skip.keySet().iterator(), pre, day) + pruneIt(s.base.keySet().iterator(), pre, day) + pruneIt(s.issued.iterator(), pre, day)
      + pruneIt(s.recent.keySet().iterator(), pre, day);
  if (n > 0) s.ver = s.ver + 1L;
  return n;
}""")
# 0.3: the first live, undone task of line l with a talk part naming npc (the one a talk completes), or null
M(eng, r"""
public static @PKG@.QTask talkTaskL(@PKG@.QState s, @PKG@.QLine l, String npc) {
  if (s.frozen || l == null) return null;
  for (int i = 0; i < l.tasks.length; i++) {
    @PKG@.QTask t = l.tasks[i];
    String k = tk(l, t);
    if (s.done.containsKey(k) || hidden(t) || !taskActive(s, l, i)) continue;
    for (int pi = 0; pi < t.parts.length; pi++) if (t.parts[pi].type == @TTALK@ && !s.pdone.contains(k + "." + pi) && @PKG@.QDefs.matches(t.parts[pi].match, npc)) return t;
  }
  return null;
}""")
# 0.3: the next task of line l (first live, undone, not hidden), or null = the line is finished
M(eng, r"""
public static @PKG@.QTask nextTaskL(@PKG@.QState s, @PKG@.QLine l) {
  if (s.frozen || l == null) return null;
  for (int i = 0; i < l.tasks.length; i++) {
    @PKG@.QTask t = l.tasks[i];
    if (s.done.containsKey(tk(l, t)) || hidden(t) || t.optional || !taskActive(s, l, i)) continue;
    return t;
  }
  return null;
}""")

# the IO job class first (QEng.wake builds one); its run() comes after QPay''')
rep('''    "public synchronized boolean follow(@PKG@.QP p, @PKG@.QLine l, long now) { return @PKG@.QEng.followL(this, p, l, now); }",                                 # 0.2
):''', '''    "public synchronized boolean follow(@PKG@.QP p, @PKG@.QLine l, long now) { return @PKG@.QEng.followL(this, p, l, now); }",                                 # 0.2
    "public synchronized int npcMark(String npc) { return @PKG@.QEng.npcMarkL(this, npc); }",                                                                 # 0.3
    "public synchronized int pruneDaily(long day) { return @PKG@.QEng.pruneDailyL(this, day); }",
    "public synchronized boolean isStarted(String line) { return this.started.containsKey(line); }",
    "public synchronized int[] dailyPicks(@PKG@.QLine l) { int[] p = @PKG@.QEng.picksL(this, l); int[] c = new int[p.length]; for (int i = 0; i < p.length; i++) c[i] = p[i]; return c; }",
    "public synchronized String talkTask(@PKG@.QLine l, String npc) { @PKG@.QTask t = @PKG@.QEng.talkTaskL(this, l, npc); return t == null ? null : t.id; }",
    "public synchronized String nextTask(@PKG@.QLine l) { @PKG@.QTask t = @PKG@.QEng.nextTaskL(this, l); return t == null ? null : t.id; }",
):''')
rep('''    r[2 * i] = dn ? "done" : (@PKG@.QEng.hidden(t) ? "hidden" : (@PKG@.QEng.soon(t) ? "soon" : (this.skip.containsKey(k) ? "skipped" : (@PKG@.QEng.taskActive(this, l, i) ? "open" : "locked"))));      // 0.2: + skipped''',
    '''    r[2 * i] = dn ? "done" : ((l.daily && !@PKG@.QEng.taskActive(this, l, i)) ? "nottoday" : (@PKG@.QEng.hidden(t) ? "hidden" : (@PKG@.QEng.soon(t) ? "soon" : (this.skip.containsKey(k) ? "skipped" : (@PKG@.QEng.taskActive(this, l, i) ? "open" : "locked")))));      // 0.2: + skipped; 0.3: + nottoday (a daily line: not one of today's jobs)''')
# the log page lists only today's jobs of a daily line
rep('''      vis[n] = i; n++;                                  // FIX2 (spec 5.5): hidden tasks are listed grey, not left out''',
    '''      if ("nottoday".equals(rows[2 * i])) continue;    // 0.3: a daily line lists today's jobs only
      vis[n] = i; n++;                                  // FIX2 (spec 5.5): hidden tasks are listed grey, not left out''')
# a profile that loads drops its old daily keys
rep('''  p.settleUntil = System.currentTimeMillis() + @SETTLE@;   // FIX2: the first lazy check after the settle window (QLife.step)''',
    '''  p.settleUntil = System.currentTimeMillis() + @SETTLE@;   // FIX2: the first lazy check after the settle window (QLife.step)
  if (s.pruneDaily(@PKG@.QDefs.day()) > 0) @PKG@.QEng.wake();   // 0.3: board keys older than yesterday leave the file''')

# ================================================================= QPay / QGive: the starter pole (SkyyFishing fishing:fn:starter), once
rep('''  if (c.startsWith("gear|")) return @PKG@.QLog.fn("gear:fn:box") != null;       // 0.2: no SkyyGear = the gear claim waits''',
    '''  if (c.startsWith("gear|")) return @PKG@.QLog.fn("gear:fn:box") != null;       // 0.2: no SkyyGear = the gear claim waits
  if (c.startsWith("pole|")) return @PKG@.QLog.fn("fishing:fn:starter") != null;  // 0.3: no SkyyFishing 0.1.4 = the pole claim waits''')
rep('''           "public Object stack;"):          # 0.2: the prepared gear bag (one ItemStack WITH its metadata - never into an ItemGridSlot)''',
    '''           "public Object stack;",           # 0.2: the prepared gear bag (one ItemStack WITH its metadata - never into an ItemGridSlot)
           "public String grant;"):          # 0.3: the pole's grant id - a rod carrying it already = not given again''')
rep('''# 0.2: ONE prepared stack (quantity 1, the gear bag): storage first, each try measured by counting that container before and after''',
    '''# 0.3: a stack in these containers carries this grant id (SkyyFishing's fishing:fn:grantOf reads its rod metadata) - the pole's dupe guard
M(give, r"""
public static boolean hasGrant(@IC@[] cs, String g) {
  java.util.function.Function f = @PKG@.QLog.fn("fishing:fn:grantOf");
  if (f == null || g == null || g.length() == 0) return false;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short i = 0; i < cap; i++) {
      @IS@ it = cs[c].getItemStack(i);
      if (it == null || it.isEmpty()) continue;
      Object r;
      try { r = f.apply(it); } catch (Throwable t) { r = null; }
      if (g.equals(r)) return true;
    }
  }
  return false;
}""")
# 0.2: ONE prepared stack (quantity 1, the gear bag): storage first, each try measured by counting that container before and after''')
rep('''        if (inv != null && this.stack instanceof @IS@) added = giveStack(new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() }, (@IS@) this.stack);''',
    '''        if (inv != null && this.grant != null && hasGrant(new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() }, this.grant)) {
          added = this.qty;                                      // 0.3: that pole is already here (a repay after a crash) - never a second one
          @PKG@.QLog.info("reward " + this.c + ": the player already holds the item with grant " + this.grant + " - not given again");
        }
        else if (inv != null && this.stack instanceof @IS@) added = giveStack(new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() }, (@IS@) this.stack);''')
rep('''    @PKG@.QGive g = new @PKG@.QGive(p.u, s, c, bag.getItemId(), 1);
    g.stack = bag;
    s.markPaying(c, System.currentTimeMillis());
    try { w.execute(g); return 2; }
    catch (Throwable t) { s.setPaying(false); return 0; }
  }
  return -1;''', '''    @PKG@.QGive g = new @PKG@.QGive(p.u, s, c, bag.getItemId(), 1);
    g.stack = bag;
    s.markPaying(c, System.currentTimeMillis());
    try { w.execute(g); return 2; }
    catch (Throwable t) { s.setPaying(false); return 0; }
  }
  if (a[0].equals("pole")) {                                    // 0.3: SkyyFishing's starter rod, stamped with this claim's grant id
    if (!a[1].equals("starter")) return -1;
    java.util.function.Function f = @PKG@.QLog.fn("fishing:fn:starter");
    if (f == null) return 0;
    @PR@ pr = p.pr;
    java.util.UUID wu = pr == null ? null : pr.getWorldUuid();
    @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
    if (w == null) return 0;
    Object st;
    try { st = f.apply(new Object[] { p.u, a[2] }); } catch (Throwable t) { st = null; }
    if (!(st instanceof @IS@) || ((@IS@) st).isEmpty()) return 0;
    @PKG@.QGive g = new @PKG@.QGive(p.u, s, c, ((@IS@) st).getItemId(), 1);
    g.stack = st;
    g.grant = a[2];
    s.markPaying(c, System.currentTimeMillis());
    try { w.execute(g); return 2; }
    catch (Throwable t) { s.setPaying(false); return 0; }
  }
  return -1;''')

# ================================================================= engine names + probes (API drift stops the build)
rep('''PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
AC_ = "com.hypixel.hytale.server.core.command.system.AbstractCommand"''', '''T.update({   # 0.3 (Quests Q3): NPCs, markers, the map provider (the TownProbe 0.2 / SkyyMerchants / SkyyFishing names)
    "UEPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "UUC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "RR": "com.hypixel.hytale.component.RemoveReason",
    "ADR": "com.hypixel.hytale.component.AddReason",
    "HR": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "NPCP": "com.hypixel.hytale.server.npc.NPCPlugin",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "R3C": "com.hypixel.hytale.math.vector.Rotation3fc",
    "V3DC": "org.joml.Vector3dc",
    "PAIR": "it.unimi.dsi.fastutil.Pair",
    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "MMB": "com.hypixel.hytale.server.core.universe.world.worldmap.markers.MapMarkerBuilder",
    "MKC": "com.hypixel.hytale.server.core.universe.world.worldmap.markers.MarkersCollector",
    "MMK": "com.hypixel.hytale.protocol.packets.worldmap.MapMarker",
    "MPV": "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager$MarkerProvider",
    "DNC": "com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent",
    "PDN": "com.hypixel.hytale.server.core.modules.entity.component.PersistentDisplayName",
    "ITB": "com.hypixel.hytale.server.core.modules.entity.component.Interactable",
    "ITS": "com.hypixel.hytale.server.core.modules.interaction.Interactions",
    "ITY": "com.hypixel.hytale.protocol.InteractionType",
    "INT": "com.hypixel.hytale.server.core.modules.entity.component.Intangible",
    "PROP": "com.hypixel.hytale.server.core.modules.entity.component.PropComponent",
    "MC": "com.hypixel.hytale.server.core.modules.entity.component.ModelComponent",
    "MDA": "com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset",
    "MDL": "com.hypixel.hytale.server.core.asset.type.model.config.Model",
    "NID": "com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId",
    "NSER": "com.hypixel.hytale.component.NonSerialized",
    "HOL": "com.hypixel.hytale.component.Holder",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
})
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
AC_ = "com.hypixel.hytale.server.core.command.system.AbstractCommand"''')
rep('''TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")
''', '''for c, m in ((T["UEPRE"], "getTargetEntity"), (T["UEPRE"], "setCancelled"), (T["UEPRE"], "isCancelled"), (T["RSYS"], "onEntityAdded"),
             (T["RSYS"], "onEntityRemove"), (T["CB"], "tryRemoveEntity"), (T["UUC"], "getUuid"), (T["UUC"], "getComponentType"),
             (T["NPL"], "getText"), (T["NPL"], "getComponentType"), (T["HR"], "getRotation"), (T["HR"], "getComponentType"), (T["NPCP"], "get"),
             (T["NPCP"], "spawnNPC"), (T["R3F"], "setYaw"), (T["R3F"], "yaw"), (T["TC"], "getRotation"), (T["MMB"], "withCustomName"),
             (T["MMB"], "withCompassImage"), (T["MMB"], "build"), (T["MKC"], "addIgnoreViewDistance"), (T["MPV"], "update"),
             (T["WLD"], "getWorldMapManager"), ("com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager", "addMarkerProvider"),
             (T["WLD"], "getEntityStore"), (T["WLD"], "getChunkStore"), ("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore", "getChunkReference"), (T["EST"], "getStore"), (T["EST"], "getRefFromUUID"),
             (T["EST"], "takeNextNetworkId"), (T["EST"], "REGISTRY"), ("com.hypixel.hytale.component.ComponentRegistry", "getNonSerializedComponentType"),
             (T["NSER"], "get"), (T["ST"], "getRegistry"), (T["ST"], "addEntity"), (T["ST"], "removeEntity"), (T["ST"], "putComponent"),
             (T["ST"], "ensureComponent"), (T["HOL"], "addComponent"), (T["DNC"], "getComponentType"), (T["PDN"], "getComponentType"),
             (T["ITB"], "getComponentType"), (T["ITS"], "getComponentType"), (T["ITS"], "getInteractionId"), (T["ITS"], "setInteractionId"),
             (T["ITS"], "setInteractionHint"), (T["ITY"], "Use"), (T["INT"], "INSTANCE"), (T["INT"], "getComponentType"), (T["PROP"], "get"),
             (T["PROP"], "getComponentType"), (T["MC"], "getComponentType"), (T["MDA"], "getAssetMap"), (T["MDL"], "createStaticScaledModel"),
             (T["NID"], "getComponentType"), (T["CHU"], "indexChunkFromBlock"), (T["PTU"], "spawnParticleEffect"), (T["UNI"], "getWorld"),
             (T["PLA"], "getPlayerRef"), (T["REF"], "getStore"), (T["REF"], "isValid"), (T["ITM"], "getAssetMap"), (T["NPC"], "getComponentType")):
    B.probe(pool, c, m)
_sig3 = lambda cls, name: [str(x.getSignature()) for x in pool.get(cls).getDeclaredMethods() if str(x.getName()) == name]
assert "(Lcom/hypixel/hytale/component/Store;Ljava/lang/String;Ljava/lang/String;Lorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3fc;)Lit/unimi/dsi/fastutil/Pair;" in _sig3(T["NPCP"], "spawnNPC"), "NPCPlugin.spawnNPC changed"
assert "(Ljava/lang/String;Lorg/joml/Vector3dc;Ljava/util/List;Lcom/hypixel/hytale/component/ComponentAccessor;)V" in _sig3(T["PTU"], "spawnParticleEffect"), "ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor) changed"
assert "(Lcom/hypixel/hytale/server/core/universe/world/World;Lcom/hypixel/hytale/server/core/entity/entities/Player;Lcom/hypixel/hytale/server/core/universe/world/worldmap/markers/MarkersCollector;)V" in _sig3(T["MPV"], "update"), "MarkerProvider.update changed"
assert "(Lcom/hypixel/hytale/protocol/packets/worldmap/MapMarker;)V" in _sig3(T["MKC"], "addIgnoreViewDistance"), "MarkersCollector.addIgnoreViewDistance changed"
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")
''')

# ================================================================= the new classes (before QIO.run: QIO / QTick / QEvents / QFn call them)
NEW = r'''
# =====================================================================================================================
# 0.3 (Quests Q3) QUEST NPCs: QNpcApi (the engine seam - the harness puts a stand-in in QNpc.API), QNpcRec (one registry line), QNpc
# (registry npcs.tsv, dialogue files, the keeper, ghosts / orphans, the per-player signs), QNpcReal (the game's side, world thread)
# =====================================================================================================================
napi = pool.makeInterface(PKG + ".QNpcApi")
for _sg in ("public abstract Object spawn(Object world, String role, double x, double y, double z, float yaw);",
            "public abstract Object find(Object world, String uuid);",
            "public abstract String uuidOf(Object world, Object ref);",
            "public abstract boolean loaded(Object world, double x, double z);",
            "public abstract void remove(Object world, Object ref);",
            "public abstract void prepare(Object world, Object ref, String name, String hint);",
            "public abstract Object prop(Object world, double x, double y, double z, String text);",
            "public abstract boolean valid(Object ref);",
            "public abstract double[] pos(Object world, Object ref);",
            "public abstract void particle(Object world, String id, double x, double y, double z, java.util.List viewers);",
            "public abstract java.util.List near(Object world, double x, double y, double z, double r);",
            "public abstract String worldName(Object world);",
            "public abstract Object world(String name);",
            "public abstract void exec(Object world, Runnable r);",
            "public abstract void provide(Object world, Object provider);"):
    napi.addMethod(CtNewMethod.make(jv(_sg), napi))
ALL.append(napi)
nrec = K("QNpcRec")
for _f in ("public String id;", "public String world;", "public double x;", "public double y;", "public double z;", "public float yaw;",
           "public volatile String uuid = \"\";", "public volatile long missing;", "public volatile Object prepared;", "public volatile Object prop;"):
    F(nrec, _f)
C(nrec, "public QNpcRec(String id, String world, double x, double y, double z, float yaw, String uuid) { this.id = id; this.world = world; this.x = x; this.y = y; this.z = z; this.yaw = yaw; this.uuid = uuid == null ? \"\" : uuid; }")
npc = K("QNpc")
F(npc, "public static volatile @PKG@.QNpcApi API;")
F(npc, "public static volatile @PKG@.QNpcRec[] RECS = new @PKG@.QNpcRec[0];")
for _f in ("KNOWN", "GHOSTS", "LASTUSE", "DLG", "PROPQ"):     # FIX2: PROPQ = floating ! refs -> world, removed by that world's keeper
    F(npc, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
for _f in ("public static java.nio.file.Path FILE;", "public static java.nio.file.Path DLG_DIR;", "public static volatile boolean FROZEN;",
           "public static volatile long VER = 1L;", "public static volatile long SAVED_VER = 1L;", "public static volatile long SPAWNS;",
           "public static volatile long RESPAWNS;", "public static volatile long REMOVED;", "public static volatile long PROPS;",
           "public static volatile long PARTICLES;", "public static volatile long TALKS;"):
    F(npc, _f)
F(npc, "public static final String[] IDS = %s;" % jarr([n_[0] for n_ in NPCS]))
F(npc, "public static final String[] NAMES = %s;" % jarr([n_[1] for n_ in NPCS]))
F(npc, "public static final String[] ROLES = %s;" % jarr([n_[2] for n_ in NPCS]))
F(npc, "public static final String[] KINDS = %s;" % jarr([n_[3] for n_ in NPCS]))
F(npc, "public static final String[] ICONS = %s;" % jarr([n_[4] for n_ in NPCS]))
F(npc, "public static final double[] MARKH = new double[] { %s };" % ", ".join(repr(n_[5]) for n_ in NPCS))
F(npc, "public static final String HINT = %s;" % jstr("server." + TALK_KEY))
F(npc, "public static final String USE_ROOT = \"*UseNPC\";")
F(npc, "public static final String PROP_MODEL = %s;" % jstr(NPC_PROP_MODEL))
F(npc, "public static final String BANG = %s;" % jstr(MARK_BANG))
F(npc, "public static final String ASK = %s;" % jstr(MARK_ASK))
F(npc, "public static final String MARLOW_DLG = %s;" % jbig(MARLOW_DLG))
M(npc, r"""
public static int def(String id) {
  if (id == null) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return i;
  return -1;
}""")
M(npc, r"""
public static @PKG@.QNpcRec recOf(String id) {
  @PKG@.QNpcRec[] a = RECS;
  for (int i = 0; i < a.length; i++) if (a[i].id.equals(id)) return a[i];
  return null;
}""")
# FIX2 (critic 2.1): a floating "!" that cannot be removed now (its NPC was removed / moved by an admin standing in ANOTHER world) waits
# here (prop ref -> world) until the keeper runs in that world; one that is gone already (its area unloaded - NonSerialized) is forgotten
M(npc, r"""
public static void propLater(Object prop, String world) {
  if (prop != null && world != null) PROPQ.put(prop, world);
}""")
# FIX2 (critic 3.2): the shared floating "!" stands only over an NPC that offers something on this server: the Quest Board while the
# Daily jobs board is on and loaded, Marlow while his line is loaded and not hidden (SkyyFishing 0.1.4 present). It is SHARED, so a
# player who finished the line still sees it - the per-player signs (and Server Setup "Your signs only") are the per-player option.
M(npc, r"""
public static boolean offers(String id) {
  if (id == null || !@PKG@.QCfg.ENABLED) return false;
  @PKG@.QLine[] ls = @PKG@.QDefs.LINES;
  for (int li = 0; li < ls.length; li++) {
    @PKG@.QLine l = ls[li];
    if (!id.equals(l.giver) || !@PKG@.QEng.lineOn(l)) continue;
    for (int i = 0; i < l.tasks.length; i++) if (!@PKG@.QEng.hidden(l.tasks[i])) return true;
  }
  return false;
}""")
# FIX (critic B2): quest:caller:board exists only while the board can count a talk (Daily jobs board on, a board line loaded, a Quest Board
# placed) - else the tutorial's "talk to the quest board" part shows coming soon instead of a task nobody can finish; true = it changed
M(npc, r"""
public static boolean boardCaller() {
  boolean on = @PKG@.QCfg.BOARD_ON && @PKG@.QDefs.BOARD != null && recOf("board") != null;
  java.util.Map b = @PKG@.QLog.bridge();
  boolean was = b.containsKey("quest:caller:board");
  if (on == was) return false;
  if (on) b.put("quest:caller:board", Boolean.TRUE); else b.remove("quest:caller:board");
  return true;
}""")
# KNOWN (uuid -> rec) + the npc:<id> places (the widget arrow / reach to an NPC) follow RECS
M(npc, r"""
public static void publish() {
  @PKG@.QNpcRec[] a = RECS;
  java.util.HashMap pl = new java.util.HashMap();
  java.util.HashSet keep = new java.util.HashSet();
  for (int i = 0; i < a.length; i++) {
    int di = def(a[i].id);
    if (a[i].uuid.length() > 0) { KNOWN.put(a[i].uuid, a[i]); keep.add(a[i].uuid); }
    pl.put(a[i].id, new @PKG@.QPlace("npc:" + a[i].id, a[i].world, a[i].x, a[i].y, a[i].z, di < 0 ? a[i].id : NAMES[di]));
  }
  java.util.Iterator it = KNOWN.keySet().iterator();
  while (it.hasNext()) if (!keep.contains(it.next())) it.remove();
  @PKG@.QDefs.NPCPLACES = pl;
  VER = VER + 1L;
  if (boardCaller()) @PKG@.QLife.rebuildAll();                         // FIX B2: the board placed / removed = the tutorial part live / soon
}""")
M(npc, r"""
public static synchronized void putRec(@PKG@.QNpcRec r) {
  @PKG@.QNpcRec[] a = RECS;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) if (!a[i].id.equals(r.id)) l.add(a[i]);
  l.add(r);
  @PKG@.QNpcRec[] b = new @PKG@.QNpcRec[l.size()];
  for (int i = 0; i < b.length; i++) b[i] = (@PKG@.QNpcRec) l.get(i);
  RECS = b;
  publish();
}""")
M(npc, r"""
public static synchronized void dropRec(String id) {
  @PKG@.QNpcRec[] a = RECS;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) if (!a[i].id.equals(id)) l.add(a[i]);
  @PKG@.QNpcRec[] b = new @PKG@.QNpcRec[l.size()];
  for (int i = 0; i < b.length; i++) b[i] = (@PKG@.QNpcRec) l.get(i);
  RECS = b;
  publish();
}""")
M(npc, r"""
public static synchronized void reuuid(@PKG@.QNpcRec r, String u) {
  KNOWN.remove(r.uuid);
  r.uuid = u;
  publish();
}""")
M(npc, r"""
public static void ghost(String uuid, String world, long now) {
  if (uuid == null || uuid.length() == 0) return;
  KNOWN.remove(uuid);
  GHOSTS.put(uuid, now + "|" + (world == null ? "" : world));
}""")
M(npc, r"""
public static String text() {
  StringBuilder b = new StringBuilder("# SkyyQuests quest NPCs (written by the server; /questadmin npc add | remove | list). npc = id world x y z yaw uuid; ghost = an old NPC uuid removed when it loads\n");
  @PKG@.QNpcRec[] a = RECS;
  for (int i = 0; i < a.length; i++) {
    @PKG@.QNpcRec r = a[i];
    b.append("npc\t").append(r.id).append('\t').append(r.world).append('\t').append(r.x).append('\t').append(r.y).append('\t').append(r.z).append('\t').append(r.yaw).append('\t').append(r.uuid).append('\n');
  }
  java.util.Iterator it = new java.util.TreeMap(GHOSTS).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String v = String.valueOf(e.getValue());
    int bar = v.indexOf('|');
    b.append("ghost\t").append(e.getKey()).append('\t').append(bar < 0 ? v : v.substring(0, bar)).append('\t').append(bar < 0 ? "" : v.substring(bar + 1)).append('\n');
  }
  return b.toString();
}""")
# setup / reload: an unreadable npcs.tsv freezes the registry (never written over, no orphan removal) until it reads
M(npc, r"""
public static void load(java.util.List err) {
  if (FILE == null) return;
  java.util.ArrayList recs = new java.util.ArrayList();
  try {
    if (!java.nio.file.Files.isRegularFile(FILE, new java.nio.file.LinkOption[0])) { FROZEN = false; RECS = new @PKG@.QNpcRec[0]; publish(); return; }
    java.util.List ls = java.nio.file.Files.readAllLines(FILE, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < ls.size(); i++) {
      String ln = (String) ls.get(i);
      if (ln.trim().length() == 0 || ln.startsWith("#")) continue;
      String[] a = ln.split("\t", -1);
      if (a[0].equals("npc") && a.length >= 8) {
        if (def(a[1]) < 0) { err.add("npcs.tsv line " + (i + 1) + ": unknown NPC id " + a[1] + " (skipped)"); continue; }
        recs.add(new @PKG@.QNpcRec(a[1], a[2], Double.parseDouble(a[3]), Double.parseDouble(a[4]), Double.parseDouble(a[5]), Float.parseFloat(a[6]), a[7].trim()));
        continue;
      }
      if (a[0].equals("ghost") && a.length >= 4) { GHOSTS.put(a[1].trim(), a[2].trim() + "|" + a[3].trim()); continue; }
      err.add("npcs.tsv line " + (i + 1) + " is not an npc / ghost line (ignored)");
    }
  } catch (Throwable t) {
    FROZEN = true;
    @PKG@.QLog.warn("npcs.tsv cannot be read (" + t + ") - the quest NPC registry is FROZEN: nothing is written over the file and no NPC is removed or re-spawned until it is fixed and /questadmin reload");
    return;
  }
  FROZEN = false;
  java.util.HashSet seen = new java.util.HashSet();
  java.util.ArrayList keep = new java.util.ArrayList();
  for (int i = recs.size() - 1; i >= 0; i--) { @PKG@.QNpcRec r = (@PKG@.QNpcRec) recs.get(i); if (seen.add(r.id)) keep.add(0, r); }
  @PKG@.QNpcRec[] b = new @PKG@.QNpcRec[keep.size()];
  for (int i = 0; i < b.length; i++) b[i] = (@PKG@.QNpcRec) keep.get(i);
  RECS = b;
  publish();
}""")
# the SkyyQuests-IO thread (QIO mode 8) and the shutdown: one atomic write of the registry
M(npc, r"""
public static boolean save() {
  if (FROZEN || FILE == null) return false;
  long v = VER;
  try {
    @PKG@.QLog.writeAtomic(FILE, text());
    if (v > SAVED_VER) SAVED_VER = v;
    return true;
  } catch (Throwable t) { @PKG@.QStore.ioWarn("could not save npcs.tsv (kept in memory, retried at the next change): " + t); return false; }
}""")
M(npc, r"""
public static void dirty() {
  VER = VER + 1L;
  @PKG@.QStore.ioRun(new @PKG@.QIO(8, null, null, null));
}""")
# dialogue/<npc>.properties (copied once for the shipped ones; read on setup / reload - never a world thread)
M(npc, r"""
public static void loadDialogues(java.util.List err) {
  if (DLG_DIR == null) return;
  for (int i = 0; i < IDS.length; i++) {
    if (!"talk".equals(KINDS[i])) continue;
    try {
      java.nio.file.Path f = DLG_DIR.resolve(IDS[i] + ".properties");
      if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && "marlow".equals(IDS[i])) {
        @PKG@.QLog.writeAtomic(f, MARLOW_DLG);
        @PKG@.QLog.info("wrote the shipped dialogue/" + IDS[i] + ".properties (copied once - edits stay)");
      }
      java.util.Properties p = @PKG@.QLog.readProps(f);
      if (p == null) { DLG.remove(IDS[i]); continue; }
      DLG.put(IDS[i], p);
    } catch (Throwable t) { err.add("dialogue/" + IDS[i] + ".properties: " + t); }
  }
}""")
M(npc, r"""
public static String dlg(String npc, String key, String def) {
  Object o = DLG.get(npc);
  String v = o instanceof java.util.Properties ? ((java.util.Properties) o).getProperty(key) : null;
  if (v == null || v.trim().length() == 0) return def == null ? "" : def;
  return @PKG@.QLog.clean(v);
}""")
# the portrait item: the dialogue's icon when it is a plain id the game knows (an empty asset map = the harness: trusted), else the default
M(npc, r"""
public static boolean itemOk(String id) {
  if (id == null || id.length() == 0 || id.length() > 80) return false;
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  try {
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = @ITM@.getAssetMap();
    if (m == null || m.getAssetCount() <= 0) return true;
    return m.getAsset(id) != null;
  } catch (Throwable t) { return true; }
}""")
M(npc, r"""
public static String icon(String npc) {
  int di = def(npc);
  String d = di < 0 ? "Food_Fish_Raw" : ICONS[di];
  String v = dlg(npc, "icon", d);
  return itemOk(v) ? v : d;
}""")
M(npc, r"""
public static boolean firstPress(java.util.UUID u, long now) {
  Object o = LASTUSE.put(u, Long.valueOf(now));
  return !(o instanceof Long) || now - ((Long) o).longValue() >= 250L;
}""")
# /questadmin npc add <id> (the admin's world thread): spawn + name + Use + hint, register (KNOWN before anything else can see it as an
# orphan), the old one (same id) removed now when it stands in this world and is loaded, else a ghost; the registry is written on IO
M(npc, r"""
public static String add(@PR@ pr, Object w, double x, double y, double z, float yaw, String id) {
  int di = def(id);
  if (di < 0) return "-Unknown quest NPC '" + id + "' - use one of: board, marlow.";
  if (FROZEN) return "-npcs.tsv could not be read - fix it (server log) and /questadmin reload first.";
  @PKG@.QNpcApi a = API;
  if (a == null || w == null) return "-The NPC tools are not ready.";
  String wn = a.worldName(w);
  Object ref = a.spawn(w, ROLES[di], x, y, z, yaw);
  if (ref == null) { @PKG@.QLog.warn("npc add " + id + ": role " + ROLES[di] + " did not spawn in " + wn); return "-" + NAMES[di] + " did not spawn (vanilla role " + ROLES[di] + ") - see the server log."; }
  String u = a.uuidOf(w, ref);
  if (u == null) { a.remove(w, ref); return "-" + NAMES[di] + " spawned without an id - removed again (server log)."; }
  a.prepare(w, ref, NAMES[di], HINT);
  long now = System.currentTimeMillis();
  @PKG@.QNpcRec old = recOf(id);
  @PKG@.QNpcRec r = new @PKG@.QNpcRec(id, wn, x, y, z, yaw, u);
  r.prepared = ref;
  putRec(r);
  String was = "";
  if (old != null && old.uuid.length() > 0 && !old.uuid.equals(u)) {
    Object or = old.world.equals(wn) ? a.find(w, old.uuid) : null;
    if (or != null) { a.remove(w, or); REMOVED = REMOVED + 1L; was = " - the old one was removed"; }
    else { ghost(old.uuid, old.world, now); was = " - the old one (" + old.world + ") goes the moment its area loads"; }
    Object op = old.prop;                                               // FIX2 (critic 2.1): another world = queued for its keeper
    old.prop = null;
    if (op != null) { if (old.world.equals(wn)) { if (a.valid(op)) a.remove(w, op); } else propLater(op, old.world); }
  }
  SPAWNS = SPAWNS + 1L;
  dirty();
  @PKG@.QLog.info("quest NPC " + id + " (" + NAMES[di] + ", role " + ROLES[di] + ", " + u + ") placed in " + wn + " at " + Math.round(x) + " " + Math.round(y) + " " + Math.round(z) + " by " + (pr == null ? "?" : pr.getUsername()));
  return "+" + NAMES[di] + " placed here (" + wn + " " + Math.round(x) + " " + Math.round(y) + " " + Math.round(z) + ")" + was + ". Players press F on it to talk.";
}""")
M(npc, r"""
public static String remove(@PR@ pr, Object w, String id) {
  int di = def(id);
  if (di < 0) return "-Unknown quest NPC '" + id + "' - use one of: board, marlow.";
  if (FROZEN) return "-npcs.tsv could not be read - fix it (server log) and /questadmin reload first.";
  @PKG@.QNpcRec r = recOf(id);
  if (r == null) return "=" + NAMES[di] + " is not placed.";
  @PKG@.QNpcApi a = API;
  String wn = a == null || w == null ? "" : a.worldName(w);
  Object e = a != null && r.world.equals(wn) && r.uuid.length() > 0 ? a.find(w, r.uuid) : null;
  long now = System.currentTimeMillis();
  String how;
  if (e != null) { a.remove(w, e); REMOVED = REMOVED + 1L; how = "removed"; }
  else { ghost(r.uuid, r.world, now); how = "removed from the list - the NPC itself goes the moment its area in " + r.world + " loads"; }
  dropRec(id);                                                          // FIX2: off the list first (a keeper pass sees it gone)
  Object op = r.prop;                                                   // FIX2 (critic 2.1): another world = queued for its keeper
  r.prop = null;
  if (op != null) { if (a != null && r.world.equals(wn)) { if (a.valid(op)) a.remove(w, op); } else propLater(op, r.world); }
  dirty();
  @PKG@.QLog.info("quest NPC " + id + " " + how + " by " + (pr == null ? "?" : pr.getUsername()));
  return "+" + NAMES[di] + " " + how + ".";
}""")
M(npc, r"""
public static String listText() {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < IDS.length; i++) {
    @PKG@.QNpcRec r = recOf(IDS[i]);
    b.append(i == 0 ? "" : "\n").append(IDS[i]).append(" (").append(NAMES[i]).append(", ").append(ROLES[i]).append("): ");
    if (r == null) b.append("not placed - stand on the spot and /questadmin npc add ").append(IDS[i]);
    else b.append(r.world).append(" ").append(Math.round(r.x)).append(" ").append(Math.round(r.y)).append(" ").append(Math.round(r.z)).append(r.missing > 0L ? " (missing - re-spawns 15 s after its area loads)" : "");
  }
  b.append("\nghosts waiting: ").append(GHOSTS.size()).append(FROZEN ? "   (npcs.tsv unreadable - FROZEN)" : "");
  return b.toString();
}""")
# FIX (critic B1): the floating "!" is its own entity - removed before the record forgets it (a re-spawn / an unloaded area), never a second one
M(npc, r"""
public static void dropProp(@PKG@.QNpcApi a, Object w, @PKG@.QNpcRec r) {
  Object o = r.prop;
  r.prop = null;
  if (o == null || a == null) return;
  try { if (a.valid(o)) a.remove(w, o); } catch (Throwable t) { @PKG@.QLog.warnOnce("dropprop:" + r.id, "could not remove the old floating ! of " + r.id + " (logged once): " + t); }
}""")
M(npc, r"""
public static void respawn(@PKG@.QNpcApi a, Object w, @PKG@.QNpcRec r, int di, long now) {
  Object ref = a.spawn(w, ROLES[di], r.x, r.y, r.z, r.yaw);
  if (ref == null) { r.missing = now; @PKG@.QLog.warnOnce("respawn:" + r.id, "quest NPC " + r.id + " is missing and did not re-spawn (role " + ROLES[di] + ") - retried every 15 s (logged once)"); return; }
  String u = a.uuidOf(w, ref);
  if (u == null) { a.remove(w, ref); r.missing = now; return; }
  a.prepare(w, ref, NAMES[di], HINT);
  String old = r.uuid;
  ghost(old, r.world, now);
  reuuid(r, u);
  r.prepared = ref;
  r.missing = 0L;
  dropProp(a, w, r);
  RESPAWNS = RESPAWNS + 1L;
  dirty();
  @PKG@.QLog.info("quest NPC " + r.id + " was missing 15 s after its area loaded - re-spawned at its spot (" + u + "; the old " + old + " is a ghost now)");
}""")
# the per-player signs (particles) over one NPC: ? to the players within 24 blocks with something to hand in here, ! to those with a quest
M(npc, r"""
public static void signs(@PKG@.QNpcApi a, Object w, @PKG@.QNpcRec r, int di, double[] p) {
  java.util.List near = a.near(w, p[0], p[1], p[2], 24.0);
  if (near == null || near.isEmpty()) return;
  java.util.ArrayList ask = new java.util.ArrayList();
  java.util.ArrayList bang = new java.util.ArrayList();
  for (int i = 0; i < near.size(); i++) {
    Object[] e = (Object[]) near.get(i);
    @PKG@.QP qp = @PKG@.QEng.player((java.util.UUID) e[0]);
    @PKG@.QState s = @PKG@.QEng.stateOf(qp);
    if (s == null || !s.pk.equals(qp.pk)) continue;
    int m = s.npcMark(r.id);
    if (m == 2) ask.add(e[1]);
    else if (m == 1) bang.add(e[1]);
  }
  if (!ask.isEmpty()) { a.particle(w, ASK, p[0], p[1] + MARKH[di] + 0.5, p[2], ask); PARTICLES = PARTICLES + 1L; }
  if (!bang.isEmpty()) { a.particle(w, BANG, p[0], p[1] + MARKH[di] + 0.5, p[2], bang); PARTICLES = PARTICLES + 1L; }
}""")
# THE KEEPER (the world thread, QNpcTask, every 2 s while a player stands in a world with a quest NPC): name / Use / hint after a load, the
# floating "!" prop (NonSerialized - put back after a reload), the per-player signs, a missing NPC re-spawned 15 s after its chunk loaded,
# ghosts removed when they load (forgotten after 7 days)
M(npc, r"""
public static void keep(Object w, long now) {
  @PKG@.QNpcApi a = API;
  if (a == null || w == null || FROZEN) return;
  String wn = a.worldName(w);
  if (wn == null) return;
  if (!PROPQ.isEmpty()) {                                               // FIX2 (critic 2.1): floating ! left by a remove / move elsewhere
    java.util.Iterator pq = PROPQ.entrySet().iterator();
    while (pq.hasNext()) {
      java.util.Map.Entry pe = (java.util.Map.Entry) pq.next();
      if (!wn.equals(pe.getValue())) continue;
      Object po = pe.getKey();
      pq.remove();
      try { if (a.valid(po)) { a.remove(w, po); REMOVED = REMOVED + 1L; } } catch (Throwable x) { @PKG@.QLog.warnOnce("propq", "could not remove a left-over floating ! (logged once): " + x); }
    }
  }
  boolean props = @PKG@.QCfg.propsOn();
  boolean parts = @PKG@.QCfg.particlesOn();
  @PKG@.QNpcRec[] rs = RECS;
  for (int i = 0; i < rs.length; i++) {
    @PKG@.QNpcRec r = rs[i];
    if (!r.world.equals(wn)) continue;
    int di = def(r.id);
    if (di < 0) continue;
    try {
      Object ref = r.uuid.length() == 0 ? null : a.find(w, r.uuid);
      if (ref != null) {
        r.missing = 0L;
        if (r.prepared != ref) { a.prepare(w, ref, NAMES[di], HINT); r.prepared = ref; }
        double[] p = null;
        if (props && offers(r.id)) {                                      // FIX2 (critic 3.2): only over an NPC that offers something
          if (r.prop == null || !a.valid(r.prop)) {
            p = a.pos(w, ref);
            if (p != null) {
              r.prop = a.prop(w, p[0], p[1] + MARKH[di], p[2], "!");
              PROPS = PROPS + 1L;
              if (recOf(r.id) != r) dropProp(a, w, r);                    // FIX2: removed / moved meanwhile - never a stray !
            }
          }
        } else if (r.prop != null) dropProp(a, w, r);
        if (parts) { if (p == null) p = a.pos(w, ref); if (p != null) signs(a, w, r, di, p); }
      } else if (a.loaded(w, r.x, r.z)) {
        r.prepared = null;
        if (r.missing == 0L) r.missing = now;
        else if (now - r.missing >= 15000L) respawn(a, w, r, di, now);
      } else { r.missing = 0L; r.prepared = null; dropProp(a, w, r); }
    } catch (Throwable t) { @PKG@.QLog.warnOnce("keep:" + r.id, "the quest NPC keeper failed for " + r.id + " (logged once): " + t); }
  }
  if (GHOSTS.isEmpty()) return;
  boolean ch = false;
  java.util.Iterator it = GHOSTS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String v = String.valueOf(e.getValue());
    int bar = v.indexOf('|');
    long t = @PKG@.QLog.num(bar < 0 ? v : v.substring(0, bar), now);
    String gw = bar < 0 ? "" : v.substring(bar + 1);
    if (now - t > 604800000L) { it.remove(); ch = true; continue; }
    if (!gw.equals(wn)) continue;
    try {
      Object g = a.find(w, String.valueOf(e.getKey()));
      if (g != null) { a.remove(w, g); it.remove(); REMOVED = REMOVED + 1L; ch = true; @PKG@.QLog.info("an old quest NPC (" + e.getKey() + ") loaded in " + wn + " - removed (no duplicates)"); }
    } catch (Throwable x) { @PKG@.QLog.warnOnce("ghost", "ghost removal failed (logged once): " + x); }
  }
  if (ch) dirty();
}""")
# the RefSystem add hook (world thread): 1 = remove it (a ghost, or our role + our NPC name with no registry line = an orphan), 0 = keep
M(npc, r"""
public static int onAdded(String wn, String uuid, String role, String plate) {
  if (uuid == null || FROZEN) return 0;
  if (KNOWN.containsKey(uuid)) return 0;
  if (GHOSTS.remove(uuid) != null) { REMOVED = REMOVED + 1L; dirty(); @PKG@.QLog.info("an old quest NPC (" + uuid + ") loaded in " + wn + " - removed (no duplicates)"); return 1; }
  if (role == null || plate == null) return 0;
  for (int i = 0; i < IDS.length; i++) {
    if (ROLES[i].equals(role) && NAMES[i].equals(plate)) {
      REMOVED = REMOVED + 1L;
      @PKG@.QLog.info("a quest NPC " + plate + " with no registry line (" + uuid + ", " + role + ") loaded in " + wn + " - removed (orphan)");
      return 1;
    }
  }
  return 0;
}""")
nreal = K("QNpcReal")
nreal.addInterface(napi)
C(nreal, "public QNpcReal() { }")
M(nreal, r"""
public Object spawn(Object world, String role, double x, double y, double z, float yaw) {
  @WLD@ w = (@WLD@) world;
  @ST@ st = w.getEntityStore().getStore();
  @R3F@ rot = new @R3F@();
  rot.setYaw(yaw);
  @PAIR@ p = @NPCP@.get().spawnNPC(st, role, (String) null, (@V3DC@) new @V3D@(x, y, z), (@R3C@) rot);
  if (p == null) return null;
  Object r = p.first();
  if (!(r instanceof @REF@) || !((@REF@) r).isValid()) return null;
  return r;
}""")
M(nreal, r"""
public Object find(Object world, String uuid) {
  try {
    @REF@ r = ((@WLD@) world).getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    return r != null && r.isValid() ? r : null;
  } catch (Throwable t) { return null; }
}""")
M(nreal, r"""
public String uuidOf(Object world, Object ref) {
  @REF@ r = (@REF@) ref;
  @UUC@ u = (@UUC@) r.getStore().getComponent(r, @UUC@.getComponentType());
  return u == null || u.getUuid() == null ? null : u.getUuid().toString();
}""")
M(nreal, r"""
public boolean loaded(Object world, double x, double z) {
  @REF@ c = ((@WLD@) world).getChunkStore().getChunkReference(@CHU@.indexChunkFromBlock((int) Math.floor(x), (int) Math.floor(z)));   // 0.7 (SkyyMerchants 0.1.2 recipe)
  return c != null && c.isValid();
}""")
M(nreal, r"""
public void remove(Object world, Object ref) {
  @REF@ r = (@REF@) ref;
  if (r != null && r.isValid()) r.getStore().removeEntity(r, @RR@.REMOVE);
}""")
M(nreal, r"""
public void prepare(Object world, Object ref, String name, String hint) {
  @REF@ r = (@REF@) ref;
  @ST@ st = r.getStore();
  @MSG@ m = @MSG@.raw(name);
  st.putComponent(r, @DNC@.getComponentType(), new @DNC@(m));
  st.putComponent(r, @PDN@.getComponentType(), new @PDN@(m));
  st.putComponent(r, @NPL@.getComponentType(), new @NPL@(name));
  st.ensureComponent(r, @ITB@.getComponentType());
  @ITS@ its = (@ITS@) st.getComponent(r, @ITS@.getComponentType());
  if (its == null) { its = new @ITS@(); st.putComponent(r, @ITS@.getComponentType(), its); }
  if (its.getInteractionId(@ITY@.Use) == null) its.setInteractionId(@ITY@.Use, @PKG@.QNpc.USE_ROOT);
  its.setInteractionHint(hint);
}""")
M(nreal, r"""
public Object prop(Object world, double x, double y, double z, String text) {
  @WLD@ w = (@WLD@) world;
  @ST@ st = w.getEntityStore().getStore();
  @HOL@ h = st.getRegistry().newHolder();
  h.addComponent(@NID@.getComponentType(), new @NID@(w.getEntityStore().takeNextNetworkId()));
  h.addComponent(@EST@.REGISTRY.getNonSerializedComponentType(), @NSER@.get());
  h.addComponent(@TC@.getComponentType(), new @TC@(new @V3D@(x, y, z), new @R3F@()));
  Object ma = @MDA@.getAssetMap().getAsset(@PKG@.QNpc.PROP_MODEL);
  if (ma instanceof @MDA@) h.addComponent(@MC@.getComponentType(), new @MC@(@MDL@.createStaticScaledModel((@MDA@) ma, 0.2f)));
  h.addComponent(@HR@.getComponentType(), new @HR@(new @R3F@()));
  h.addComponent(@NPL@.getComponentType(), new @NPL@(text));
  h.addComponent(@INT@.getComponentType(), @INT@.INSTANCE);
  h.addComponent(@PROP@.getComponentType(), @PROP@.get());
  return st.addEntity(h, @ADR@.SPAWN);
}""")
M(nreal, "public boolean valid(Object ref) { return ref instanceof @REF@ && ((@REF@) ref).isValid(); }")
M(nreal, r"""
public double[] pos(Object world, Object ref) {
  @REF@ r = (@REF@) ref;
  @TC@ tc = (@TC@) r.getStore().getComponent(r, @TC@.getComponentType());
  if (tc == null) return null;
  @V3D@ v = tc.getPosition();
  return new double[] { v.x, v.y, v.z };
}""")
M(nreal, r"""
public void particle(Object world, String id, double x, double y, double z, java.util.List viewers) {
  @ST@ st = ((@WLD@) world).getEntityStore().getStore();
  @PTU@.spawnParticleEffect(id, (@V3DC@) new @V3D@(x, y, z), viewers, (@CAC@) st);
}""")
M(nreal, r"""
public java.util.List near(Object world, double x, double y, double z, double r) {
  java.util.ArrayList out = new java.util.ArrayList();
  double r2 = r * r;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    if (pr == null || !pr.isValid()) continue;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null || @UNI@.get().getWorld(wu) != world) continue;
    @REF@ ref = pr.getReference();
    if (ref == null || !ref.isValid()) continue;
    @TC@ tc = (@TC@) ref.getStore().getComponent(ref, @TC@.getComponentType());
    if (tc == null) continue;
    @V3D@ v = tc.getPosition();
    double dx = v.x - x; double dy = v.y - y; double dz = v.z - z;
    if (dx * dx + dy * dy + dz * dz <= r2) out.add(new Object[] { pr.getUuid(), ref });
  }
  return out;
}""")
M(nreal, "public String worldName(Object world) { return world instanceof @WLD@ ? ((@WLD@) world).getName() : null; }")
M(nreal, "public Object world(String name) { return name == null ? null : @UNI@.get().getWorld(name); }")
M(nreal, "public void exec(Object world, Runnable r) { ((@WLD@) world).execute(r); }")
M(nreal, "public void provide(Object world, Object provider) { ((@WLD@) world).getWorldMapManager().addMarkerProvider(\"skyyquests\", (@MPV@) provider); }")
ntask = K("QNpcTask")
ntask.addInterface(pool.get("java.lang.Runnable"))
F(ntask, "public Object world;")
C(ntask, "public QNpcTask(Object world) { this.world = world; }")
M(ntask, r"""
public void run() {
  try { @PKG@.QNpc.keep(this.world, System.currentTimeMillis()); } catch (Throwable t) { @PKG@.QLog.warnOnce("npctask", "the quest NPC keeper failed (logged once): " + t); }
}""")

# =====================================================================================================================
# 0.3 MAP + COMPASS MARKERS: QMarks (per-player rows rebuilt on the TICK thread only when the profile's state, the world, the NPC registry,
# the widget target or the switches changed; the MapMarker objects are reused while the rows stay the same) + QMapProv (the engine asks it
# per player on the WorldMap thread: a memory read). quest:fn:markers answers the same rows.
# =====================================================================================================================
marks = K("QMarks")
for _f in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> { sig, world, MapMarker[], rows, rowKey }
           "public static final java.util.concurrent.ConcurrentHashMap PROVIDED = new java.util.concurrent.ConcurrentHashMap();",
           "public static volatile Object PROV;", "public static volatile long BUILDS;", "public static volatile long ROWS;"):
    F(marks, _f)
F(marks, "public static final String IMG_NPC = %s;" % jstr(IMG_NPC))
F(marks, "public static final String IMG_PLACE = %s;" % jstr(IMG_PLACE))
M(marks, r"""
public static Object marker(String id, String img, double x, double y, double z, String label) {
  return new @MMB@(id, img, new @TRF@((@V3DC@) new @V3D@(x, y, z))).withCustomName(label).withCompassImage(img).build();
}""")
M(marks, r"""
public static void refresh(@PKG@.QP p, @PKG@.QState s) {
  String w = p.world;
  String dp = p.dirPlace;
  String sig = w + "|" + s.ver + "|" + s.pk + "|" + @PKG@.QNpc.VER + "|" + dp + "|" + @PKG@.QCfg.MARK_MAP + "|" + @PKG@.QCfg.ENABLED + "|" + @PKG@.QCfg.BOARD_ON + "|" + System.identityHashCode(@PKG@.QDefs.PLACES) + "|" + @PKG@.QDefs.day();
  Object[] c = (Object[]) CACHE.get(p.u);
  if (c != null && sig.equals(c[0])) return;
  java.util.ArrayList rows = new java.util.ArrayList();
  StringBuilder key = new StringBuilder();
  if (@PKG@.QCfg.ENABLED && w != null) {
    @PKG@.QNpcRec[] rs = @PKG@.QNpc.RECS;
    for (int i = 0; i < rs.length; i++) {
      if (!rs[i].world.equals(w)) continue;
      int di = @PKG@.QNpc.def(rs[i].id);
      if (di < 0) continue;
      int m = s.npcMark(rs[i].id);
      if (m == 0) continue;
      rows.add(new Object[] { "npc:" + rs[i].id, m == 2 ? "?" : "!", Double.valueOf(rs[i].x), Double.valueOf(rs[i].y), Double.valueOf(rs[i].z), @PKG@.QNpc.NAMES[di] + (m == 2 ? "  ?" : "  !") });
    }
    @PKG@.QPlace q = @PKG@.QDefs.place(dp);
    if (q != null && @PKG@.QEng.worldMatch(q.world, w)) {
      boolean dup = false;
      for (int i = 0; i < rows.size(); i++) if (q.id.equals(((Object[]) rows.get(i))[0])) dup = true;
      if (!dup) rows.add(new Object[] { q.id, "place", Double.valueOf(q.x), Double.valueOf(q.y), Double.valueOf(q.z), q.label });
    }
  }
  for (int i = 0; i < rows.size(); i++) {
    Object[] r = (Object[]) rows.get(i);
    key.append(r[0]).append('|').append(r[1]).append('|').append(r[2]).append('|').append(r[3]).append('|').append(r[4]).append('|').append(r[5]).append(';');
  }
  String rk = key.toString() + @PKG@.QCfg.MARK_MAP;
  if (c != null && rk.equals(c[4]) && w != null && w.equals(c[1])) { CACHE.put(p.u, new Object[] { sig, c[1], c[2], c[3], c[4] }); return; }
  Object[] mm = new Object[@PKG@.QCfg.MARK_MAP ? rows.size() : 0];
  for (int i = 0; i < mm.length; i++) {
    Object[] r = (Object[]) rows.get(i);
    String id = (String) r[0];
    boolean npc = id.startsWith("npc:");
    mm[i] = marker(npc ? "SkyyQuestNpc" + id.substring(4) : "SkyyQuestPlace", npc ? IMG_NPC : IMG_PLACE, ((Double) r[2]).doubleValue(), ((Double) r[3]).doubleValue(), ((Double) r[4]).doubleValue(), (String) r[5]);
  }
  CACHE.put(p.u, new Object[] { sig, w, mm, rows.toArray(), rk });
  BUILDS = BUILDS + 1L;
  ROWS = ROWS + (long) rows.size();
}""")
M(marks, r"""
public static int collect(java.util.UUID u, String world, @MKC@ col) {
  if (u == null || world == null || col == null || !@PKG@.QCfg.MARK_MAP) return 0;
  Object o = CACHE.get(u);
  if (!(o instanceof Object[])) return 0;
  Object[] c = (Object[]) o;
  if (!world.equals(c[1])) return 0;
  Object[] m = (Object[]) c[2];
  for (int i = 0; i < m.length; i++) col.addIgnoreViewDistance((@MMK@) m[i]);
  return m.length;
}""")
M(marks, r"""
public static Object[] bridge(java.util.UUID u, String world) {
  Object o = u == null ? null : CACHE.get(u);
  if (!(o instanceof Object[]) || world == null) return new Object[0];
  Object[] c = (Object[]) o;
  if (!world.equals(c[1])) return new Object[0];
  Object[] r = (Object[]) c[3];
  Object[] out = new Object[r.length];
  for (int i = 0; i < r.length; i++) out[i] = r[i];
  return out;
}""")
mprov = K("QMapProv")
mprov.addInterface(pool.get(T["MPV"]))
C(mprov, "public QMapProv() { }")
M(mprov, r"""
public void update(@WLD@ world, @PLA@ player, @MKC@ col) {
  try {
    if (world == null || player == null || !@PKG@.QCfg.MARK_MAP) return;
    @PR@ pr = player.getPlayerRef();
    if (pr != null) @PKG@.QMarks.collect(pr.getUuid(), world.getName(), col);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("mapprov", "the quest map markers failed (logged once): " + t); }
}""")
# one provider per world object, added at the first PlayerReady there (the world thread); the same key again replaces it (idempotent)
M(marks, r"""
public static boolean provide(Object w) {
  @PKG@.QNpcApi a = @PKG@.QNpc.API;
  if (a == null || w == null) return false;
  String k = a.worldName(w) + "#" + System.identityHashCode(w);
  if (PROVIDED.putIfAbsent(k, Boolean.TRUE) != null) return false;
  if (PROV == null) PROV = new @PKG@.QMapProv();
  a.provide(w, PROV);
  return true;
}""")

# =====================================================================================================================
# 0.3 PAGES: the dialogue page (TownProbe #1 / #8 / #16 made permanent) and the Quest Board page (3 daily jobs) - kit, inline, no underscores
# =====================================================================================================================
DPW, DPH = 900, 430
DSH = SUI.page_shell("SkyyQdF", DPW, DPH, SUI.J("this.name", "Marlow"), body_id="SkyyQdBody")
DIW = DSH.inner_w
D_TOP_H, D_SUB_H, D_ST_H, D_PORT, D_BTN_W, D_GAP = 160, 30, 30, 104, 200, 12
SUI.fit([D_TOP_H, 10, D_SUB_H, D_ST_H, SUI.BTN_H + 8], DSH.inner_h, "dialogue page")
DLG_TOP = "\n".join([
    DSH.java("b"),
    ja("SkyyQdBody", SUI.group("SkyyQdTop", "Left", h=D_TOP_H)),
    ja("SkyyQdTop", SUI.item_frame("SkyyQdPic", size=D_PORT, item=SUI.J("this.icon", "Food_Fish_Raw"))),
    ja("SkyyQdTop", SUI.spacer(w=16)),
    ja("SkyyQdTop", SUI.label("SkyyQdText", "", "default", w=DIW - D_PORT - 16, h=D_TOP_H, wrap=True, max_lines=6)),
    ja("SkyyQdBody", SUI.spacer(h=10)),
    ja("SkyyQdBody", SUI.label("SkyyQdSub", "", "caption", w=DIW, h=D_SUB_H, align="Center")),
    ja("SkyyQdBody", SUI.status_line("SkyyQdStatus", h=D_ST_H)),
    ja("SkyyQdBody", SUI.button_row("SkyyQdFoot", align="center", top=8, used=2 * D_BTN_W + D_GAP, avail=DIW)),
])
D_TWO_A = "\n".join([ja("SkyyQdFoot", SUI.button("SkyyQdNext", "Next", "primary", w=D_BTN_W)),
                     ja("SkyyQdFoot", SUI.button("SkyyQdClose", "Close", "secondary", w=D_BTN_W, sound="cancel", anchor={"left": D_GAP}))])
D_TWO_B = "\n".join([ja("SkyyQdFoot", SUI.button("SkyyQdYes", "Accept", "primary", w=D_BTN_W)),
                     ja("SkyyQdFoot", SUI.button("SkyyQdNo", "Not now", "secondary", w=D_BTN_W, sound="cancel", anchor={"left": D_GAP}))])
D_ONE = "\n".join([ja("SkyyQdFoot", SUI.spacer(w=(D_BTN_W + D_GAP) // 2)),
                   ja("SkyyQdFoot", SUI.button("SkyyQdClose", "Close", "secondary", w=D_BTN_W, sound="cancel"))])
dpage = K("QDlgPage", T["CUP"])
for _f in ("public String npc;", "public String name;", "public String icon;", "public String[] pages;", "public int at;", "public int mode;",
           "public String reward = \"\";", "public String info = \"\";", "public boolean answered;", "public boolean closing;",
           "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();"):
    F(dpage, _f)
C(dpage, r"""
public QDlgPage(@PR@ pr, String npc, String name, String icon, String[] pages, int mode, String reward) {
  super(pr, @LIFE@.CanDismiss);
  this.npc = npc; this.name = name; this.icon = icon; this.pages = pages == null || pages.length == 0 ? new String[] { "..." } : pages;
  this.at = 0; this.mode = mode; this.reward = reward == null ? "" : reward;
}""")
for _l in SUI.java_status_methods():
    M(dpage, _l)
M(dpage, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {\n  BUILDS.incrementAndGet();\n"
         + "  if (this.at < 0) this.at = 0;\n  if (this.at >= this.pages.length) this.at = this.pages.length - 1;\n"
         + "  boolean last = this.at >= this.pages.length - 1;\n"
         + "\n".join("  " + x for x in DLG_TOP.split("\n")) + "\n"
         + "  if (!last) {\n" + "\n".join("    " + x for x in D_TWO_A.split("\n")) + "\n  } else if (this.mode == 1) {\n"
         + "\n".join("    " + x for x in D_TWO_B.split("\n")) + "\n  } else {\n" + "\n".join("    " + x for x in D_ONE.split("\n")) + "\n  }\n"
         + r"""  b.set("#SkyyQdText.Text", this.pages[this.at]);
  String sub = this.reward.length() > 0 ? "Reward: " + this.reward : (this.pages.length > 1 ? "page " + (this.at + 1) + " of " + this.pages.length : "");
  b.set("#SkyyQdSub.Text", sub);
  b.set("#SkyyQdStatus.Text", textOf(this.info));
  if (!last) {
    ev.addEventBinding(@CEB@.Activating, "#SkyyQdNext", @EVD@.of("a", "next"));
    ev.addEventBinding(@CEB@.Activating, "#SkyyQdClose", @EVD@.of("a", "close"));
  } else if (this.mode == 1) {
    ev.addEventBinding(@CEB@.Activating, "#SkyyQdYes", @EVD@.of("a", "yes"));
    ev.addEventBinding(@CEB@.Activating, "#SkyyQdNo", @EVD@.of("a", "close"));
  } else ev.addEventBinding(@CEB@.Activating, "#SkyyQdClose", @EVD@.of("a", "close"));
}""")
BPW, BPH = 960, 520
BSH = SUI.page_shell("SkyyQbF", BPW, BPH, "Quest Board", body_id="SkyyQbBody")
BIW = BSH.inner_w
B_HEAD_H, B_SUB_H, B_ROW_H, B_ST_H = 34, 28, 52, 30
SUI.fit([B_HEAD_H, 4, B_SUB_H, 10, 3 * B_ROW_H, 10, B_ST_H, SUI.BTN_H + 8], BSH.inner_h, "board page")
B_TIER_W, B_PROG_W, B_REW_W, B_GAP = 110, 130, 380, 8      # FIX2 (critic 3.1): 300 cut "+1 unidentified armor" off on the kill jobs
B_NAME_W = BIW - B_TIER_W - B_PROG_W - B_REW_W - 3 * B_GAP


def _board_rew(j, pct):
    """the board's reward text as QDefs.rewardText(boardScale(..)) shows it (coins x percent, the game's item names)"""
    out = []
    for _p in j[3].split(","):
        _q = _p.split(":")
        if _q[0] == "coins":
            out.append("+%d coins" % (int(_q[1]) * pct // 100))
        elif _q[0] == "item":
            out.append("+%s %s" % (_q[2], _NAMES.get(_q[1], _q[1])))
        elif _q[0] == "gear":
            out.append("+1 unidentified armor" if _q[1] == "armor" else "+1 unidentified weapon")
    return "  ".join(out)


# FIX2 (critic 3.1): every shipped job's name + its worst-case reward text (300 %) fits ONE line of its column (rowSub wraps to 1 line)
for _j in BOARD_POOL:
    for _pc in (100, 300):
        assert SUI.text_width(_board_rew(_j, _pc), 12) <= B_REW_W - 8, "board reward text too wide: %s (%s %%)" % (_board_rew(_j, _pc), _pc)
    assert SUI.text_width(_j[1], 14, bold=True) <= B_NAME_W - 8, "board job name too wide: %s" % _j[1]
assert SUI.text_width("Medium", 12) <= B_TIER_W - 8 and SUI.text_width("skipped", 12) <= B_PROG_W - 8
B_TRACK, B_CLAIM, B_CLOSE = 190, 200, 150
BOARD_TOP = "\n".join([
    BSH.java("b"),
    ja("SkyyQbBody", SUI.label("SkyyQbHead", "", "heading", w=BIW, h=B_HEAD_H, align="Center")),
    ja("SkyyQbBody", SUI.spacer(h=4)),
    ja("SkyyQbBody", SUI.label("SkyyQbSub", "", "caption", w=BIW, h=B_SUB_H, align="Center")),
    ja("SkyyQbBody", SUI.spacer(h=10)),
    ja("SkyyQbBody", SUI.group("SkyyQbList", "Top", w=BIW, h=3 * B_ROW_H)),
])
BOARD_ROW = "\n".join([
    ja("SkyyQbList", SUI.group("SkyyQbR" + _i, "Left", h=B_ROW_H)),
    ja("SkyyQbR" + _i, SUI.label("SkyyQbT" + _i, "", "rowSub", w=B_TIER_W, h=B_ROW_H, col=_ROW_COL)),
    ja("SkyyQbR" + _i, SUI.label("SkyyQbN" + _i, "", "rowName", w=B_NAME_W, h=B_ROW_H, col=_ROW_COL, anchor={"left": B_GAP})),
    ja("SkyyQbR" + _i, SUI.label("SkyyQbP" + _i, "", "rowSub", w=B_PROG_W, h=B_ROW_H, align="End", col=_ROW_COL, anchor={"left": B_GAP})),
    ja("SkyyQbR" + _i, SUI.label("SkyyQbW" + _i, "", "rowSub", w=B_REW_W, h=B_ROW_H, align="End", col=_ROW_COL, anchor={"left": B_GAP})),
])
BOARD_BOTTOM = "\n".join([
    ja("SkyyQbBody", SUI.spacer(h=10)),
    ja("SkyyQbBody", SUI.status_line("SkyyQbStatus", h=B_ST_H)),
    ja("SkyyQbBody", SUI.button_row("SkyyQbFoot", align="center", top=8, used=B_TRACK + B_CLAIM + B_CLOSE + 2 * D_GAP, avail=BIW)),
    ja("SkyyQbFoot", SUI.button("SkyyQbTrack", "Track jobs", "secondary", w=B_TRACK)),
    ja("SkyyQbFoot", SUI.button("SkyyQbClaim", "Claim rewards", "secondary", w=B_CLAIM, anchor={"left": D_GAP})),
    ja("SkyyQbFoot", SUI.button("SkyyQbClose", "Close", "secondary", w=B_CLOSE, sound="cancel", anchor={"left": D_GAP})),
])
bpage = K("QBoardPage", T["CUP"])
for _f in ("public String info = \"\";", "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final String[] TIERS = new String[] { \"\", \"Easy\", \"Medium\", \"Hard\" };"):
    F(bpage, _f)
C(bpage, "public QBoardPage(@PR@ pr) { super(pr, @LIFE@.CanDismiss); }")
for _l in SUI.java_status_methods():
    M(bpage, _l)
M(bpage, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {\n  BUILDS.incrementAndGet();\n"
         + r"""  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.QP pp = @PKG@.QEng.player(u);
  @PKG@.QState s = @PKG@.QEng.stateOf(pp);
  @PKG@.QLine l = @PKG@.QDefs.BOARD;
  int[] picks = new int[0];
  String[] rows = null;
  if (s != null && l != null) { picks = s.dailyPicks(l); rows = s.rowsOf(l); }
""" + "\n".join("  " + x for x in BOARD_TOP.split("\n")) + r"""
  int dn = 0;
  for (int i = 0; i < 3; i++) {
    int k = i < picks.length ? picks[i] : -1;
    String sw = k >= 0 && rows != null ? rows[2 * k] : "";
    int st = "done".equals(sw) ? 2 : (k < 0 ? 1 : 0);
""" + "\n".join("    " + x for x in BOARD_ROW.split("\n")) + r"""
    if (k < 0) {
      b.set("#SkyyQbT" + i + ".Text", "");
      b.set("#SkyyQbN" + i + ".Text", "-");
      b.set("#SkyyQbP" + i + ".Text", "");
      b.set("#SkyyQbW" + i + ".Text", "");
      continue;
    }
    @PKG@.QTask t = l.tasks[k];
    if (st == 2) dn++;
    b.set("#SkyyQbT" + i + ".Text", t.tier >= 1 && t.tier <= 3 ? TIERS[t.tier] : "");
    b.set("#SkyyQbN" + i + ".Text", t.name);
    b.set("#SkyyQbP" + i + ".Text", st == 2 ? "Done" : ("skipped".equals(sw) ? "skipped" : rows[2 * k + 1]));
    b.set("#SkyyQbW" + i + ".Text", @PKG@.QDefs.rewardText(@PKG@.QDefs.rewardOf(l, t)));
  }
""" + "\n".join("  " + x for x in BOARD_BOTTOM.split("\n")) + r"""
  long left = @PKG@.QDefs.leftSeconds();
  b.set("#SkyyQbHead.Text", l == null ? "The board is empty" : (dn >= picks.length && picks.length > 0 ? "Daily Jobs - all done today!" : "Daily Jobs"));
  String sub;
  if (s == null) sub = "Your quests are still loading - try again in a moment.";
  else if (l == null || !@PKG@.QCfg.BOARD_ON) sub = "The quest board is closed on this server.";
  else sub = "New jobs in " + (left / 3600L) + " h " + ((left / 60L) % 60L) + " m   -   they count anywhere, each pays once" + (s.claimCount() > 0 ? "   -   " + s.claimCount() + " reward(s) waiting" : "");
  b.set("#SkyyQbSub.Text", sub);
  b.set("#SkyyQbStatus.Text", textOf(this.info));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQbTrack", @EVD@.of("a", "track"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQbClaim", @EVD@.of("a", "claim"));
  ev.addEventBinding(@CEB@.Activating, "#SkyyQbClose", @EVD@.of("a", "close"));
}""")
M(bpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.QWelcomePage.jsonStr(data, "a");
  java.util.UUID u = this.playerRef.getUuid();
  try {
    if (a.equals("close")) { close(); return; }
    @PKG@.QLine l = @PKG@.QDefs.BOARD;
    if (a.equals("track")) this.info = l == null ? "-The board is empty." : @PKG@.QEng.action(u, "track", l.id);
    else if (a.equals("claim")) this.info = @PKG@.QEng.action(u, "claim", null);
  } catch (Throwable t) { @PKG@.QLog.warn("board click " + a + " failed: " + t); this.info = "-Something went wrong (server log)."; }
  rebuild();
}""")

# =====================================================================================================================
# 0.3 TALKING: QTalk (what a quest NPC answers - pure state logic, the harness runs it), QTalkTask (opens the page on the NEXT tick)
# =====================================================================================================================
talk = K("QTalk")
M(talk, r"""
public static @PKG@.QTask task(@PKG@.QLine l, String id) {
  if (l == null || id == null) return null;
  for (int i = 0; i < l.tasks.length; i++) if (l.tasks[i].id.equals(id)) return l.tasks[i];
  return null;
}""")
M(talk, r"""
public static boolean allHidden(@PKG@.QLine l) {
  for (int i = 0; i < l.tasks.length; i++) if (!@PKG@.QEng.hidden(l.tasks[i])) return false;
  return true;
}""")
M(talk, r"""
public static String[] offer(String npc) {
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 1; i <= 9; i++) { String v = @PKG@.QNpc.dlg(npc, "offer." + i, ""); if (v.length() > 0) l.add(v); }
  if (l.isEmpty()) l.add("I have a job for you.");
  String[] r = new String[l.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i);
  return r;
}""")
# the daily line starts at the first use of the board (jobs count from then on)
M(talk, r"""
public static boolean startBoard(@PKG@.QP p, @PKG@.QState s, long now) {
  @PKG@.QLine bl = @PKG@.QDefs.BOARD;
  if (bl == null || !@PKG@.QCfg.BOARD_ON || p == null || s == null) return false;
  if (!s.startLine(bl.id, now)) return false;
  @PKG@.QEng.rebuild(p.u, s);
  @PKG@.QEng.bump(p.u);
  @PKG@.QEng.wake();
  return true;
}""")
# a talk NPC: closed (no line / every task hidden) -> offer (line not started) -> count the talk (a hand-in completes) -> the next task's
# text -> done
M(talk, r"""
public static @PKG@.QDlgPage dialogue(@PR@ pr, @PKG@.QP p, @PKG@.QState s, String npc, int di) {
  String nm = @PKG@.QNpc.dlg(npc, "name", @PKG@.QNpc.NAMES[di]);
  String ic = @PKG@.QNpc.icon(npc);
  @PKG@.QLine l = @PKG@.QDefs.line(@PKG@.QNpc.dlg(npc, "line", ""));
  if (l == null || !@PKG@.QEng.lineOn(l) || allHidden(l)) return new @PKG@.QDlgPage(pr, npc, nm, ic, new String[] { @PKG@.QNpc.dlg(npc, "closed", "Not today.") }, 0, "");
  if (!l.auto && !s.isStarted(l.id)) return new @PKG@.QDlgPage(pr, npc, nm, ic, offer(npc), 1, "");
  String tid = s.talkTask(l, npc);
  if (tid != null) {
    @PKG@.QEng.count(p.u, @TTALK@, npc, 1L, p.world, false);
    @PKG@.QTask t = task(l, tid);
    if (t != null && s.isDone(@PKG@.QEng.tk(l, t))) return new @PKG@.QDlgPage(pr, npc, nm, ic, new String[] { @PKG@.QNpc.dlg(npc, "turnin." + tid, "Thank you!") }, 0, @PKG@.QDefs.rewardText(@PKG@.QDefs.rewardOf(l, t)));
  }
  String nx = s.nextTask(l);
  if (nx == null) return new @PKG@.QDlgPage(pr, npc, nm, ic, new String[] { @PKG@.QNpc.dlg(npc, "done", "Good to see you.") }, 0, "");
  @PKG@.QTask t2 = task(l, nx);
  return new @PKG@.QDlgPage(pr, npc, nm, ic, new String[] { @PKG@.QNpc.dlg(npc, "task." + nx, t2 == null ? "" : t2.hint) }, 0, "");
}""")
# the page a player gets from F on quest NPC `npc` (world thread)
M(talk, r"""
public static @CUP@ pageFor(@PR@ pr, String npc) {
  int di = @PKG@.QNpc.def(npc);
  if (pr == null || di < 0) return null;
  java.util.UUID u = pr.getUuid();
  @PKG@.QP p = @PKG@.QEng.player(u);
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  @PKG@.QNpc.TALKS = @PKG@.QNpc.TALKS + 1L;
  if (s == null || !s.pk.equals(@PKG@.QLog.pkey(u)) || @PKG@.QLog.bridge().containsKey("profile:busy:" + u.toString()))
    return new @PKG@.QDlgPage(pr, npc, @PKG@.QNpc.NAMES[di], @PKG@.QNpc.icon(npc), new String[] { "One moment - your quests are still loading." }, 0, "");
  if ("board".equals(@PKG@.QNpc.KINDS[di])) {
    if (!@PKG@.QCfg.BOARD_ON || @PKG@.QDefs.BOARD == null) return new @PKG@.QDlgPage(pr, npc, @PKG@.QNpc.NAMES[di], @PKG@.QNpc.icon(npc), new String[] { "The quest board is closed today." }, 0, "");
    startBoard(p, s, System.currentTimeMillis());
    @PKG@.QEng.count(u, @TTALK@, npc, 1L, p.world, false);
    return new @PKG@.QBoardPage(pr);
  }
  return dialogue(pr, p, s, npc, di);
}""")
# "Accept" on an offer page: the line starts and is tracked; a talk task naming this NPC completes now (Marlow's pole) -> { text, reward }
M(talk, r"""
public static String[] accept(@PR@ pr, String npc) {
  java.util.UUID u = pr.getUuid();
  @PKG@.QP p = @PKG@.QEng.player(u);
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  @PKG@.QLine l = @PKG@.QDefs.line(@PKG@.QNpc.dlg(npc, "line", ""));
  if (s == null || l == null || !s.pk.equals(@PKG@.QLog.pkey(u)) || !@PKG@.QEng.lineOn(l) || allHidden(l)) return null;
  long now = System.currentTimeMillis();
  boolean fresh = s.startLine(l.id, now);
  s.setTrack(l.id);
  @PKG@.QEng.rebuild(u, s);
  @PKG@.QEng.bump(u);
  if (fresh) @PKG@.QLog.info(pr.getUsername() + " (" + s.pk + ") accepted " + l.id + " from " + npc);
  String tid = s.talkTask(l, npc);
  if (tid != null) {
    @PKG@.QEng.count(u, @TTALK@, npc, 1L, p.world, false);
    @PKG@.QTask t = task(l, tid);
    if (t != null && s.isDone(@PKG@.QEng.tk(l, t))) return new String[] { @PKG@.QNpc.dlg(npc, "turnin." + tid, "Here you go."), @PKG@.QDefs.rewardText(@PKG@.QDefs.rewardOf(l, t)) };
  }
  @PKG@.QEng.wake();
  String nx = s.nextTask(l);
  @PKG@.QTask t2 = task(l, nx);
  return new String[] { nx == null ? @PKG@.QNpc.dlg(npc, "done", "Good to see you.") : @PKG@.QNpc.dlg(npc, "task." + nx, t2 == null ? "" : t2.hint), "" };
}""")
# /quests board: within 8 blocks of the Quest Board (or anywhere with "Board from anywhere"); answers "" when the page opened
M(talk, r"""
public static String boardCmd(@PR@ pr, @ST@ store, @REF@ ref, @WLD@ world) {
  if (!@PKG@.QCfg.BOARD_ON || @PKG@.QDefs.BOARD == null) return "-The quest board is closed on this server.";
  @PKG@.QNpcRec r = @PKG@.QNpc.recOf("board");
  boolean ok = @PKG@.QCfg.BOARD_REMOTE;
  if (!ok && r != null && world != null && r.world.equals(world.getName())) {
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc != null) { @V3D@ v = tc.getPosition(); double dx = v.x - r.x; double dy = v.y - r.y; double dz = v.z - r.z; ok = dx * dx + dy * dy + dz * dz <= 64.0; }
  }
  if (!ok) return "-The Quest Board stands in the hub" + (r == null ? " (not placed yet)" : "") + " - press F on it there.";
  java.util.UUID u = pr.getUuid();
  @PKG@.QP p = @PKG@.QEng.player(u);
  @PKG@.QState s = @PKG@.QEng.stateOf(p);
  if (s == null) return "-Your quests are still loading - try again in a moment.";
  startBoard(p, s, System.currentTimeMillis());
  @PLA@ pl = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
  if (pl == null) return "-Could not open the board.";
  pl.getPageManager().openCustomPage(ref, store, new @PKG@.QBoardPage(pr));
  return "";
}""")
M(dpage, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = @PKG@.QWelcomePage.jsonStr(data, "a");
  try {
    if (a.equals("close")) { this.closing = true; close(); return; }
    if (a.equals("next")) { this.at = this.at + 1; this.info = ""; }
    else if (a.equals("yes") && this.mode == 1 && !this.answered) {
      this.answered = true;
      String[] r = @PKG@.QTalk.accept(this.playerRef, this.npc);
      if (r == null) this.info = "-That did not work - try again in a moment.";
      else { this.pages = new String[] { r[0] }; this.at = 0; this.mode = 0; this.reward = r[1]; this.info = r[1].length() > 0 ? "+Quest started - your reward is on its way." : "+Quest started - see your quest widget."; }
    }
  } catch (Throwable t) { @PKG@.QLog.warn("dialogue click " + a + " failed: " + t); this.info = "-Something went wrong (server log)."; }
  rebuild();
}""")
ttask = K("QTalkTask")
ttask.addInterface(pool.get("java.lang.Runnable"))
F(ttask, "public @PR@ pr;")
F(ttask, "public String npc;")
C(ttask, "public QTalkTask(@PR@ pr, String npc) { this.pr = pr; this.npc = npc; }")
M(ttask, r"""
public void run() {
  try {
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    @PLA@ pl = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pl == null || pl.getPageManager().getCustomPage() != null) return;
    @CUP@ pg = @PKG@.QTalk.pageFor(this.pr, this.npc);
    if (pg != null) pl.getPageManager().openCustomPage(r, st, pg);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("talktask", "a quest NPC page did not open (logged once): " + t); }
}""")

# =====================================================================================================================
# 0.3 QWorld: the tick's world work (SkyyQuests-Tick): the board day change, the map-marker rows, the keeper hops (every 2 s, only worlds
# with a quest NPC or ghost AND an online player there)
# =====================================================================================================================
qw = K("QWorld")
F(qw, "public static volatile long DAY = Long.MIN_VALUE;")
F(qw, "public static volatile long HOPS;")
M(qw, r"""
public static void roll(long d) {
  java.util.Iterator it = @PKG@.QEng.PLAYERS.values().iterator();
  while (it.hasNext()) { @PKG@.QState s = @PKG@.QEng.stateOf((@PKG@.QP) it.next()); if (s != null) s.pruneDaily(d); }
  @PKG@.QLife.rebuildAll();
  @PKG@.QEng.wake();
  @PKG@.QLog.info("a new board day (" + d + ") - new daily jobs for everyone");
}""")
M(qw, r"""
public static void tick(long now) {
  long d = @PKG@.QDefs.day();
  if (d != DAY) { long old = DAY; DAY = d; if (old != Long.MIN_VALUE) roll(d); }
  java.util.HashSet ws = new java.util.HashSet();
  java.util.Iterator it = @PKG@.QEng.PLAYERS.values().iterator();
  while (it.hasNext()) {
    @PKG@.QP p = (@PKG@.QP) it.next();
    if (p.world != null) ws.add(p.world);
    @PKG@.QState s = @PKG@.QEng.stateOf(p);
    if (s != null) { try { @PKG@.QMarks.refresh(p, s); } catch (Throwable t) { @PKG@.QLog.warnOnce("marks", "quest map markers failed (logged once): " + t); } }
  }
  if (@PKG@.QTick.N % 2L != 0L) return;
  @PKG@.QNpcApi a = @PKG@.QNpc.API;
  if (a == null || ws.isEmpty()) return;
  java.util.HashSet go = new java.util.HashSet();
  @PKG@.QNpcRec[] rs = @PKG@.QNpc.RECS;
  for (int i = 0; i < rs.length; i++) if (ws.contains(rs[i].world)) go.add(rs[i].world);
  java.util.Iterator gi = @PKG@.QNpc.GHOSTS.values().iterator();
  while (gi.hasNext()) { String v = String.valueOf(gi.next()); int bar = v.indexOf('|'); if (bar >= 0 && ws.contains(v.substring(bar + 1))) go.add(v.substring(bar + 1)); }
  java.util.Iterator qi = @PKG@.QNpc.PROPQ.values().iterator();           // FIX2 (critic 2.1): a left-over floating ! waits for its world
  while (qi.hasNext()) { String qv = String.valueOf(qi.next()); if (ws.contains(qv)) go.add(qv); }
  java.util.Iterator wi = go.iterator();
  while (wi.hasNext()) {
    String wn = (String) wi.next();
    try {
      Object w = a.world(wn);
      if (w != null) { a.exec(w, new @PKG@.QNpcTask(w)); HOPS = HOPS + 1L; }
    } catch (Throwable t) { @PKG@.QLog.warnOnce("npchop", "a world refused the quest NPC task (logged once): " + t); }
  }
}""")

# ---- QIO.run: every job of the private writer thread'''
rep('''# ---- QIO.run: every job of the private writer thread''', NEW)

# ---- QIO: the registry write (mode 8) + the dialogue files on reload
rep('''    if (this.mode == 7) { @PKG@.QPay.itemDone((@PKG@.QState) this.o, this.a, (int) this.n, (int) this.m, this.b); return; }''',
    '''    if (this.mode == 7) { @PKG@.QPay.itemDone((@PKG@.QState) this.o, this.a, (int) this.n, (int) this.m, this.b); return; }
    if (this.mode == 8) { if (@PKG@.QNpc.VER != @PKG@.QNpc.SAVED_VER) @PKG@.QNpc.save(); return; }     // 0.3: npcs.tsv''')
rep('''      int n = @PKG@.QDefs.load();
      @PKG@.QLife.rebuildAll();
      @PR@ pr = (@PR@) this.o;''', '''      int n = @PKG@.QDefs.load();
      java.util.ArrayList de = new java.util.ArrayList();                       // 0.3: the dialogue files + the NPC registry again
      @PKG@.QNpc.loadDialogues(de);
      if (@PKG@.QNpc.FROZEN) @PKG@.QNpc.load(de);
      @PKG@.QNpc.boardCaller();                                                 // FIX B2: the board line may be gone / back
      if (!de.isEmpty()) { java.util.ArrayList all = new java.util.ArrayList(@PKG@.QDefs.PROBLEMS); all.addAll(de); @PKG@.QDefs.PROBLEMS = all; }
      @PKG@.QLife.rebuildAll();
      @PR@ pr = (@PR@) this.o;''')
# ---- the tick: QWorld after the per-player pass
rep('''  if (pay) @PKG@.QEng.wake();''', '''  if (pay) @PKG@.QEng.wake();
  try { @PKG@.QWorld.tick(now); } catch (Throwable t) { @PKG@.QLog.warnOnce("qworld", "the quest world tick failed (logged once): " + t); }    // 0.3''')
# ---- PlayerReady: the map provider of that world; a quit forgets the marker rows
rep('''    @PKG@.QLife.join(pr, w == null ? null : w.getName());''', '''    @PKG@.QLife.join(pr, w == null ? null : w.getName());
    if (w != null) @PKG@.QMarks.provide(w);                                         // 0.3: the quest map markers of this world''')
rep('''      if (q != null) @PKG@.QLife.quit(q.getUuid());''', '''      if (q != null) { @PKG@.QLife.quit(q.getUuid()); @PKG@.QMarks.CACHE.remove(q.getUuid()); }''')
# ---- quest:fn:markers = the marker rows (NPC ! / ? + the widget target)
rep('''    if ("markers".equals(this.mode)) {
      String dpl = null;
      if (p != null) dpl = p.dirPlace;
      @PKG@.QPlace q = @PKG@.QDefs.place(dpl);
      if (q == null || !@PKG@.QEng.worldMatch(q.world, k)) return new Object[0];
      return new Object[] { new Object[] { q.id, "place", Double.valueOf(q.x), Double.valueOf(q.y), Double.valueOf(q.z), q.label } };
    }''', '''    if ("markers".equals(this.mode)) return @PKG@.QMarks.bridge(u, k);          // 0.3: { id, "!" / "?" / "place", x, y, z, label } rows''')

# ---- ECS: F on a quest NPC (UseEntityEvent$Pre) + the ghost / orphan hook (RefSystem on NPCs)
rep('''kil = K("QKillSys", T["ODS"])''', '''# 0.3: F on OUR quest NPC (fired on the player): cancel the vanilla use for our NPC (and ghost) UUIDs only, open the page NEXT tick
event_system("QUseSys", "@UEPRE@", r"""
    if (@PKG@.QNpc.KNOWN.isEmpty() && @PKG@.QNpc.GHOSTS.isEmpty()) return;
    if (!(ev instanceof @UEPRE@)) return;
    @UEPRE@ e = (@UEPRE@) ev;
    if (e.isCancelled()) return;
    @REF@ t = e.getTargetEntity();
    if (t == null || !t.isValid()) return;
    @UUC@ uc = (@UUC@) st.getComponent(t, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return;
    String us = uc.getUuid().toString();
    Object rec = @PKG@.QNpc.KNOWN.get(us);
    if (rec == null && !@PKG@.QNpc.GHOSTS.containsKey(us)) return;
    e.setCancelled(true);
    if (!(rec instanceof @PKG@.QNpcRec)) return;
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null || !@PKG@.QNpc.firstPress(pr.getUuid(), System.currentTimeMillis())) return;
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (w != null) w.execute(new @PKG@.QTalkTask(pr, ((@PKG@.QNpcRec) rec).id));""")
addsys = K("QNpcAddSys", T["RSYS"])
F(addsys, "public @QRY@ query;")
C(addsys, "public QNpcAddSys() { super(); }")
M(addsys, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = (@QRY@) @NPC@.getComponentType();
  return this.query;
}""")
M(addsys, r"""
public void onEntityAdded(@REF@ ref, @ADR@ why, @ST@ st, @CB@ cb) {
  try {
    if (@PKG@.QNpc.RECS.length == 0 && @PKG@.QNpc.GHOSTS.isEmpty()) return;
    @UUC@ uc = (@UUC@) st.getComponent(ref, @UUC@.getComponentType());
    if (uc == null || uc.getUuid() == null) return;
    @NPC@ n = (@NPC@) st.getComponent(ref, @NPC@.getComponentType());
    @NPL@ pl = (@NPL@) st.getComponent(ref, @NPL@.getComponentType());
    @WLD@ w = @PKG@.QSys.worldOf(st);
    if (@PKG@.QNpc.onAdded(w == null ? null : w.getName(), uc.getUuid().toString(), n == null ? null : n.getRoleName(), pl == null ? null : pl.getText()) == 1) cb.tryRemoveEntity(ref, @RR@.REMOVE);
  } catch (Throwable t) { @PKG@.QLog.warnOnce("npcadd", "the quest NPC add hook failed (logged once): " + t); }
}""")
M(addsys, "public void onEntityRemove(@REF@ ref, @RR@ why, @ST@ st, @CB@ cb) { }")
kil = K("QKillSys", T["ODS"])''')

# ---- commands: /quests board (players), /questadmin npc list | add <id> | remove <id> (admins)
rep('''cmd("QuestsCmd", ['super("quests", "Your quests: the quest log page (track, claim, skip, hide or show the tutorial)");', 'addAliases(new String[] { "quest" });', ADV,''',
    '''cmd("QuestsBoardCmd", ['super("board", "Open the Quest Board (stand next to it in the hub)");', ADV],
    '    String r = @PKG@.QTalk.boardCmd(pr, store, ref, world); if (r.length() > 0) @PKG@.QCmdUtil.say(pr, r);')      # 0.3
cmd("QuestsCmd", ['super("quests", "Your quests: the quest log page (track, claim, skip, hide or show the tutorial)");', 'addAliases(new String[] { "quest" });', ADV,''')
rep('''                  "addSubCommand(new @PKG@.QuestsSkipCmd());"],''', '''                  "addSubCommand(new @PKG@.QuestsSkipCmd());", "addSubCommand(new @PKG@.QuestsBoardCmd());"],''')
rep('''cmd("QuestAdminCmd", [''', '''cmd("QaNpcIdCmd", ['super("(admin) /questadmin npc add <id> | npc remove <id> - place (where you stand, facing your way) or remove a quest NPC");',
                   'this.aArg = withRequiredArg("action", "add or remove", @ATY@.STRING);',
                   'this.iArg = withRequiredArg("id", "board or marlow", @ATY@.STRING);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);'],
    r\'\'\'    String a = @PKG@.QCmdUtil.str(ctx.get(this.aArg)).toLowerCase(java.util.Locale.ROOT);
    String id = @PKG@.QCmdUtil.str(ctx.get(this.iArg)).toLowerCase(java.util.Locale.ROOT);
    if (a.equals("add")) {
      @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
      if (tc == null) { @PKG@.QCmdUtil.say(pr, "-Your position could not be read."); return; }
      @V3D@ v = tc.getPosition();
      float yaw = tc.getRotation() == null ? 0.0f : tc.getRotation().yaw();
      @HR@ hr = (@HR@) store.getComponent(ref, @HR@.getComponentType());
      if (hr != null && hr.getRotation() != null) yaw = hr.getRotation().yaw();
      @PKG@.QCmdUtil.say(pr, @PKG@.QNpc.add(pr, world, v.x, v.y, v.z, yaw, id));
    } else if (a.equals("remove")) @PKG@.QCmdUtil.say(pr, @PKG@.QNpc.remove(pr, world, id));
    else @PKG@.QCmdUtil.say(pr, "-Usage: /questadmin npc add <board|marlow>  or  /questadmin npc remove <board|marlow>");\'\'\', ("aArg", "iArg"))
cmd("QaNpcCmd", ['super("npc", "(admin) /questadmin npc list | add <id> | remove <id> - the quest NPCs (board = the Quest Board, marlow = the fisher)");',
                 'this.aArg = withRequiredArg("action", "list (or: add <id> / remove <id>)", @ATY@.STRING);', 'requirePermission("@NODE@");', 'setPermissionGroups(new String[0]);',
                 "addUsageVariant(new @PKG@.QaNpcIdCmd());"],
    r\'\'\'    String a = @PKG@.QCmdUtil.str(ctx.get(this.aArg)).toLowerCase(java.util.Locale.ROOT);
    if (!a.equals("list")) { @PKG@.QCmdUtil.say(pr, "-Usage: /questadmin npc list  or  /questadmin npc add <board|marlow>  or  /questadmin npc remove <board|marlow>"); return; }
    String[] ls = @PKG@.QNpc.listText().split("\\\\n");
    for (int i = 0; i < ls.length; i++) @PKG@.QLog.chat(pr, ls[i], i == 0 ? "@COLINF@" : null);\'\'\', ("aArg",))
cmd("QuestAdminCmd", [''')
rep('''                      "addSubCommand(new @PKG@.QaSetCmd());", "addSubCommand(new @PKG@.QaRepayCmd());", "addSubCommand(new @PKG@.QaPlaceCmd());"],
    '    @PKG@.QCmdUtil.say(pr, "=/questadmin reload | check | list <player> | set <player> <line> <task> <done|undo> | repay <player> | place list | place set <id>");')''',
    '''                      "addSubCommand(new @PKG@.QaSetCmd());", "addSubCommand(new @PKG@.QaRepayCmd());", "addSubCommand(new @PKG@.QaPlaceCmd());",
                      "addSubCommand(new @PKG@.QaNpcCmd());"],
    '    @PKG@.QCmdUtil.say(pr, "=/questadmin reload | check | list <player> | set <player> <line> <task> <done|undo> | repay <player> | place list | place set <id> | npc list | npc add <id> | npc remove <id>");')''')
rep('''cmd("QuestAdminCmd", ['super("questadmin", "(admin) SkyyQuests: reload | check | list | set | repay | place");''',
    '''cmd("QuestAdminCmd", ['super("questadmin", "(admin) SkyyQuests: reload | check | list | set | repay | place | npc");''')

# ---- the plugin: files, the NPC registry + dialogue, the systems, the board caller, the ready line, the shutdown save
rep('''  @PKG@.QDefs.AREAS_FILE = base.resolve("areas.properties");          // 0.2''',
    '''  @PKG@.QDefs.AREAS_FILE = base.resolve("areas.properties");          // 0.2
  @PKG@.QDefs.BOARD_FILE = base.resolve("board.properties");          // 0.3: the daily jobs (copied once)
  @PKG@.QNpc.FILE = base.resolve("npcs.tsv");                         // 0.3: the quest NPC registry
  @PKG@.QNpc.DLG_DIR = base.resolve("dialogue");
  @PKG@.QNpc.API = new @PKG@.QNpcReal();''')
rep('''  int n = @PKG@.QDefs.load();
  getCommandRegistry().registerCommand(new @PKG@.QuestsCmd());''', '''  int n = @PKG@.QDefs.load();
  java.util.ArrayList nerr = new java.util.ArrayList();                // 0.3
  @PKG@.QNpc.load(nerr);
  @PKG@.QNpc.loadDialogues(nerr);
  for (int i = 0; i < nerr.size() && i < 10; i++) @PKG@.QLog.warn("quest NPCs: " + nerr.get(i));
  getCommandRegistry().registerCommand(new @PKG@.QuestsCmd());''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.QKillSys());
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.QKillSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.QUseSys());        // 0.3: F on a quest NPC
  getEntityStoreRegistry().registerSystem(new @PKG@.QNpcAddSys());     // 0.3: ghosts / orphans removed when they load
''')
rep('''  b.put("quest:fn:markers", new @PKG@.QFn("markers"));''', '''  b.put("quest:fn:markers", new @PKG@.QFn("markers"));
  @PKG@.QNpc.boardCaller();                                            // 0.3 FIX B2: quest:caller:board only while a Quest Board can answer''')
rep('''" place(s), " + @PKG@.QDefs.AREAS.length + " area(s), "''', '''" place(s), " + @PKG@.QDefs.AREAS.length + " area(s), " + @PKG@.QNpc.RECS.length + " quest NPC(s), " + (@PKG@.QDefs.BOARD == null ? 0 : @PKG@.QDefs.BOARD.tasks.length) + " daily job(s), "''')
rep('''  try { @PKG@.QStore.stopIO(); } catch (Throwable x) { @PKG@.QLog.warn("shutdown save failed: " + x); }''',
    '''  try { @PKG@.QStore.stopIO(); } catch (Throwable x) { @PKG@.QLog.warn("shutdown save failed: " + x); }
  try { if (@PKG@.QNpc.VER != @PKG@.QNpc.SAVED_VER) @PKG@.QNpc.save(); } catch (Throwable x) { @PKG@.QLog.warn("shutdown npcs.tsv save failed: " + x); }   // 0.3''')
rep('''man = B.manifest("SkyyQuests", VERSION, "SkyWynn quests: data-driven quest lines (non-linear tutorial flowing into area lines), per-profile progress, rewards paid once (combat = unidentified class gear), skip any task, the quest widget data for SkyyHud (quest:fn:hud), /quests log page. Zero dependencies.", PKG + ".SkyyQuestsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)''', '''man = B.manifest("SkyyQuests", VERSION, "SkyWynn quests: data-driven quest lines (non-linear tutorial flowing into area lines), per-profile progress, rewards paid once (combat = unidentified class gear), skip any task, quest NPCs (Quest Board with 3 daily jobs, Marlow the fisher) with dialogue, ! / ? markers over them, map + compass markers, the quest widget data for SkyyHud (quest:fn:hud), /quests log page. Zero dependencies.", PKG + ".SkyyQuestsPlugin")
man["IncludesAssetPack"] = True     # 0.3: one lang line (server.skyyquests.talkHint "Press [{key}] to talk") - nothing else
B.assemble(jar, man, OUT, ASSETS)''')

# FIX B2: a Server Setup change (Daily jobs board) re-checks the board caller before the rebuild
rep('''public static void cfgChanged(String key) {
  @PKG@.QLife.rebuildAll();
}""")
M(hooks, r"""
public static void reload() {
  @PKG@.QCfg.load();
  @PKG@.QLife.rebuildAll();
}""")''', '''public static void cfgChanged(String key) {
  @PKG@.QNpc.boardCaller();                     // 0.3 FIX B2
  @PKG@.QLife.rebuildAll();
}""")
M(hooks, r"""
public static void reload() {
  @PKG@.QCfg.load();
  @PKG@.QNpc.boardCaller();                     // 0.3 FIX B2
  @PKG@.QLife.rebuildAll();
}""")''')

# ================================================================= self-checks + write
assert "KEEP=10" in s and "KEEP=20" not in s
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.2 outside the recorded changes"
dst = os.path.join(D, "build_skyyquests_0.3.py")
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines, %d changes)" % (s.count(LF), len(CHANGES)))
