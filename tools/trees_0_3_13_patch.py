"""Derive SkyyTrees/build_skyytrees_0.3.13.py from the LIVE generated SkyyTrees/build_skyytrees_0.3.12.py (the tools/deploy_set.py SET pin).
Run:  python tools/trees_0_3_13_patch.py   then   python SkyyTrees/build_skyytrees_0.3.13.py   (never --deploy: coordinated deploy)
      then python SkyyTrees/test_skyytrees_0.3.13.py --dir <tools/dev/scratch/<task>/...> (bare JVM)
EDITED-SCRIPTS RULE (commit ab75b6c): the lineage is Skyy's EDITED 0.2.3 -> trees_0_2_4_patch.py -> ... -> trees_0_3_12_patch.py -> the
generated 0.3.12 read here; tools/trees_0_2_3_patch.py and older are NEVER re-run. Edit THIS file, never the generated build script.
The SkyyClasses ability table (ABILS, AB_MODS, MODS) is READ from SkyyClasses/build_skyyclasses_0.1.25.py (the SET pin, read-only) when this
patch runs and baked into the generated script as a literal; the build cross-checks it against the newest SkyyClasses script it finds.

0.3.13 = THE ABILITY TREE REDESIGN, R2 (node model + migration) + R3 (the page) of research/Ability-Tree-Redesign-Spec.md, with SkyyClasses
0.1.26 (Skyy 2026-10-15, docs/answered/skills.md "ABILITY TREE REDESIGN" 1-3: "id have the ability's actually be in the skill tree. and thats
how you unlock them. then each ability branches into its modiferss, and each of those thakes an ability point to unlock. then your abilitys
section only shows your unlocked abilitys their level and stats. you click one, and it hides all the others, and just shows the ability you
clicked, and each of the modifiers. AND when you click an ability you have unlocked in the abilities section, it swaps the menu on the right
to something like the vanilla one" + "so you click an ability, click the slot it goes in, then click a modifer and a slot" + "modifiers
unlocked in the tee, but not in the ability."). Spec section 10 questions on their defaults: 4 loadout rows, free spine connectors, the
7-row grid, coin respec + free re-slotting out of combat kept, migration overflow grandfathered, modifier levels still grow from Lv 1.
  R2 THE NODE MODEL (spec 4.1 / 4.2): page 1 of every class tree = ROOT top centre (FREE, owned from class level 1 - TreeTick takes it for
    the player), the stat spine straight down under it (P1, P2, the X1 / X2 pick-one bracket, P3; P4 on page 2) - FREE links now
    (Server Setup row class.ap.spine, default 0) - the ABILITY nodes on the row under ROOT (A1 A2 A3 left; the A4 alt pair A4a / A4b right:
    buying one blocks the other, a respec frees the choice; the Assassin has A4a only) and under each ability its MODIFIER nodes straight
    down (one node per modifier SkyyClasses gives that ability, 4 or 5; saved id "<ability node>.<Modifier>", e.g. A1.Power). An ability
    node costs class.ap.ability (1 AP), keeps its class level gate (class:fn:abilUnlock: 1 / 10 / 20 / 30) and unlocks the ability; a
    modifier node costs class.ap.modifier (1 AP), needs only its ability node and unlocks that modifier for that ability at once (no
    ability-level gate any more - the level only adds power, SkyyClasses 0.1.26). Old class.nodes lines of A1-A4 / M1A-M4B are no longer
    read; the spine lines' AP field neither (class.ap.spine). With every node bought a class tree costs 4 abilities + 18 or 19 modifiers
    + trunk 11 + one path 14 + its element 3 = 50 (+-1) = the AP cap at class level 98 (spec 4.3; printed per class).
  THE ONE-TIME PROFILE UPDATE (spec 7; marker abil.tree2=done in players/<pkey>.properties): when a file without the marker is read, the
    old ids are mapped - an owned A4 becomes A4a or A4b by SkyyClasses' alt pick (class:fn:migInfo), the old M1A-M4B slot nodes go away
    (modifier slots come with the ability now), and every modifier that was USABLE before (its ability level reached the mods.unlock step,
    or it was equipped) becomes an owned modifier node of every owned ability node. ROOT and the spine cost nothing now (their AP come
    back by themselves: AP are computed, never stored). FIRST a History snapshot of the untouched file (history/abiltree2/<pkey>.properties;
    SkyyClasses copies its abilities file the same way) and one change-log line with the Undo in abiltree2-changes.log. Every converted
    ability / modifier node starts GRANDFATHERED (Class.<Class>.gf: it works and costs 0); at the player's next tick with a known class
    level the AP CHECK (Class.<Class>.gfchk) pays for them in order (A1, A2, A3, A4, then the modifiers) while the free AP cover them -
    the rest stay grandfathered ("kept from before") until the next respec of that class, which refunds them as normal nodes. Nothing that
    worked stops working, AP never goes negative through the update (only an old negative balance stays negative), a second read changes
    nothing. Without SkyyClasses' answer the old ids are KEPT in the file (written back as they were) and the update waits for it (tick).
    Equipped modifiers and the p1 / p2 / a1 / a2 rows stay (they live in SkyyClasses' file).
  BRIDGES (spec 8): tree:fn:abil keeps answering the intact node ids (now A4a / A4b and A1.Power ...); NEW tree:fn:modOwned
    (Object[] { UUID, ability id or node id, modifier id }) -> Boolean (null = no gate); the page calls class:fn:abilPanel with "v2" and
    class:fn:abilDo with the actions hold / place / mod / clearMod / back (+ rbpick, attune); class:fn:abilUnlock keeps the level gates.
  REBIRTH R5 (rebirth:part:trees): a rebirth keeps the class picks under the rebirth gate as before - the ability + modifier nodes are paid
    nodes now (they come back as the AP allow, in purchase order) and the commit clears the grandfather marks. The order list learns the
    new ids (the update rewrites A4 -> A4a / A4b, drops M1A-M4B, adds the modifier nodes).
  R3 THE PAGE (spec 6): the class tab's graph = the new page 1 on the 7-row grid; the middle column (Abilities) lists only the abilities you
    OWN (icon, name + level, the key it sits on, uses to the next level); clicking one FOCUSES it (the others hide; Back returns): its
    level and gain, its modifier tiles (owned ones clickable, locked ones say "buy it in the tree"), and Max Up there while rebirth
    upgrades wait; the right panel turns into the LATTICE view: 4 rows (Ability 2 key, Ability 3 key, crouch + Ability 2, crouch +
    Ability 3), each = an ability slot + its modifier slots (2, + the rebirth slots 3 / 4). Click an ability (its card, the focus card or
    a filled slot) - it is held - then an ability slot: it goes there, trading places with what sat there. Click a modifier tile, then one
    of that ability's modifier slots in its own row. A filled modifier slot clicked with nothing held empties it. Out of combat only
    (SkyyClasses re-checks every action). The Imbue element picker sits under Imbue's row. Gone: Swap, Move here, Cancel, Enable, Other
    alt, Modifiers, Next slot, Unequip, Tree node. Casting is unchanged (the 4 rows are p1, p2, a1, a2).
  Saved data: players/<pkey>.properties gains abil.tree2=done, Class.<Class>.gf / .gfchk and the new node ids. trees.properties: 3 NEW rows
  (class.ap.ability 1, class.ap.modifier 1, class.ap.spine 0 - Server Setup -> Trees -> Class trees); an existing file has no line = the
  default (nothing rewritten).
  FIX ROUND (critics): the update runs only after a VERIFIED History copy (a new copy has the source's length; a failed copy = the old
    ids wait, the tick tries again every 10 s); a class level below 1 is "not known yet" for the AP check; the tick's maintenance is
    guarded (a throw is logged once); the free Root alone is "nothing to respec" (no coins); an ability node keeps an admin's OFF switch
    (class.nodes.<Class>.A1 ... A4a / A4b = false, or the 0.3.12 A4 line for both alts; the old M1A-M4B lines are logged as not read);
    the AP number in the texts comes from the Server Setup rows; the A4 alts hang from one drop into a pick-one bracket (A4a column 6,
    the bracket column 7, A4b column 8); a locked modifier tile opens its node's detail + Unlock at once; the focus view shows the stats
    line (Mana + Stamina + cooldown, SkyyClasses' panel [125 + row]) and every ability node shows its rune icon (panel [120 + node]).
  FIX ROUND 2 (critics): a History copy from an EARLIER server run that differs from the file is kept as <k>.properties.<millis> and a
    fresh copy made (a rollback + a second update: the Undo restores the state right before THIS update; this run's copy is refreshed in
    place, an identical one kept - no pile-up); a class respec while the update waits also drops the waiting 0.3.12 ids (no old A4
    comes back); the focus view's texts fit their boxes (level bonus 14 px without the "A use = ..." sentence, tile name 14 px on one
    line, the slots / "Not unlocked - node ..." on the 12 px second line, the Max Up note 12 px; build asserts over every noun and
    modifier); a modifier cell in the graph shows its modifier's name (owned or waiting for its ability; buyable keeps "Unlock N AP") -
    the icons stay placeholders until R4; the class.ap.ability / modifier help says more AP can put owners over budget.
  ROLLBACK FLOOR: once a profile was updated, never go below 0.3.13 (0.3.12 reads A4a / A1.Power as unknown and drops them at its next save)
  - restore the History copies first (the change-log line says how).
"""
import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.12.py")
dst = os.path.join(ROOT, "SkyyTrees", "build_skyytrees_0.3.13.py")
csrc_path = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.25.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
CR, LF = chr(13), chr(10)
s = raw.decode("utf8").replace(CR + LF, LF)
assert 'VERSION = "0.3.12"' in s and "GENERATED by tools/trees_0_3_12_patch.py from the LIVE build_skyytrees_0.3.11.py" in s, \
    "build_skyytrees_0.3.12.py is not the live 0.3.12 of the edited lineage"
assert "abil.tree2" not in s, "0.3.12 already has the 0.3.13 parts"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
CHANGES = []
OLD = s


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old))


def block(start, end, new):
    """replace the text from `start` up to and including `end` (both unique; end after start)"""
    global s
    assert s.count(start) == 1, "block start count %d: %s" % (s.count(start), start[:120])
    i = s.index(start)
    j = s.index(end, i)
    old = s[i:j + len(end)]
    assert s.count(old) == 1, "block not unique: %s" % start[:80]
    s = s[:i] + new + s[j + len(end):]
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.3.13 = THE ABILITY"):HEAD.index("  ROLLBACK FLOOR")].rstrip()

# ---------------------------------------------------------------------------------------------------------------- SkyyClasses' ability table
_ct = ast.parse(open(csrc_path, encoding="utf8").read())
_lits = {}
for _node in _ct.body:
    if isinstance(_node, ast.Assign) and len(_node.targets) == 1 and isinstance(_node.targets[0], ast.Name) and _node.targets[0].id in ("ABILS", "AB_MODS", "MODS"):
        _lits[_node.targets[0].id] = ast.literal_eval(_node.value)
assert set(_lits) == {"ABILS", "AB_MODS", "MODS"}, sorted(_lits)
C_ABILS = {}
for _id, _nm, _cls, _tier, _built, _pas in _lits["ABILS"]:
    C_ABILS.setdefault(_cls, [None] * 5)[_tier] = (_id, _nm, list(_lits["AB_MODS"][_id]))
C_MODNAME = dict((m[0], m[1]) for m in _lits["MODS"])
# fix round 2 (critic: the focus view's level bonus line): SkyyClasses' level-gain nouns, for the layout's text-fit asserts only
C_NOUNS = sorted(set(ast.literal_eval([_n.value for _n in _ct.body if isinstance(_n, ast.Assign) and len(_n.targets) == 1
                                       and isinstance(_n.targets[0], ast.Name) and _n.targets[0].id == "AB_NOUN"][0]).values()))
assert "First Strike damage" in C_NOUNS
assert len(C_ABILS) == 8 and all(v[0] and v[1] and v[2] and v[3] for v in C_ABILS.values())
assert [c for c, v in C_ABILS.items() if v[4] is None] == ["Assassin"], "only the Assassin has one Ability 1 alt"

# ================================================================================================================ header + version
rep('''"""SkyyTrees 0.3.12 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_12_patch.py from the LIVE build_skyytrees_0.3.11.py (the SET pin) - edit the patch, not this file. 0.3.11
was GENERATED''', '''"""SkyyTrees 0.3.13 - build script (javassist via jpype, tools/skyybuild.py). Owner: Skyy (they/them).
GENERATED by tools/trees_0_3_13_patch.py from the LIVE build_skyytrees_0.3.12.py (the SET pin) - edit the patch, not this file. 0.3.12
was GENERATED by tools/trees_0_3_12_patch.py from the LIVE build_skyytrees_0.3.11.py. 0.3.11
was GENERATED''')
rep('''0.3.12 (2026-10-15; notes: tools/trees_0_3_12_patch.py) ''', '''0.3.13 (2026-10-15; notes: tools/trees_0_3_13_patch.py) ''' + NOTE[len("0.3.13 = "):].replace(LF, LF + "    ") + '''
  CHECKED: SkyyTrees/test_skyytrees_0.3.13.py (bare JVM: class compare vs 0.3.12, -Xverify:all, the node model on the real classes, the
    profile update fuzzed on 1000 random old profiles (nothing that worked stops working, AP never negative but grandfathered, a second
    run changes nothing), every page click path (focus, hold, place, mod, clearMod, back, Max Up, the element, the tree cells), the
    layout model of every rendered page (fits 1600 x 941), tree:fn:modOwned, the rebirth gate, the access audit, start twice on a copy).
  ROLLBACK FLOOR: once a profile was updated, never go below 0.3.13 - restore the History copies first (abiltree2-changes.log says how).

=== SkyyTrees 0.3.12 notes (history; still true unless 0.3.13 above says otherwise) ===
0.3.12 (2026-10-15; notes: tools/trees_0_3_12_patch.py) ''', 1)
rep('''Run:   python build_skyytrees_0.3.12.py            -> SkyyTrees/SkyyTrees-0.3.12.jar
       python build_skyytrees_0.3.12.py --deploy   -> also''', '''Run:   python build_skyytrees_0.3.13.py            -> SkyyTrees/SkyyTrees-0.3.13.jar
       python build_skyytrees_0.3.13.py --deploy   -> also''')
rep('VERSION = "0.3.12"', 'VERSION = "0.3.13"')

# ================================================================================================================ the class tree template
block('''CROWS = 7   # 0.3.12: graph rows per page''', '''assert 21 + 1 + 11 + 14 + 3 == 50
''', '''CROWS = 7   # 0.3.12: graph rows per page (spec probe P1: 7 rows of 78 px slots + the pager strip fill the same 600 px well)
# 0.3.13 (R2 of research/Ability-Tree-Redesign-Spec.md, 4.1 + 5.1): PAGE 1 = ROOT top centre (free, owned from class level 1), the stat spine
# straight down under it (P1, P2, the X1 / X2 pick-one bracket closing at P3; free links - class.ap.spine), the ABILITY nodes on the row under
# ROOT (A1 A2 A3 left, the A4 alt pair A4a / A4b right with the PICK-ONE BRACKET between them - fix round (critic C5): ROOT's bar drops into a
# junction at row 1 column 7 whose arms run into A4a (column 6) and A4b (column 8) - buying one blocks the other) and under each ability its
# MODIFIER nodes straight down
# (one per modifier SkyyClasses gives it; a 4-modifier ability leaves its 5th slot hidden). A modifier node needs only its ability (its
# parent + Need); its connector is drawn down from the slot above it (CT_VIS). The template id of modifier slot k is "<ability>m<k>"; per
# class the SAVED id is "<ability>.<Modifier>" (CID, e.g. A1.Power).
ABL = ["A1", "A2", "A3", "A4a", "A4b"]       # the ability node ids (template id = saved id)
ABL_COL = [0, 1, 2, 6, 8]                    # fix round: A4a / A4b at columns 6 / 8, the pick-one bracket in column 7
ABL_TIER = [0, 1, 2, 3, 4]                   # SkyyClasses' ability tier of each ability node (0 = A1, 1 = A2, 2 = A2-alt, 3 / 4 = the A1-alts)
NMOD = 5                                     # modifier slots per ability column (rows 2-6)
def mod_tid(a, k): return "%sm%d" % (a, k + 1)
CT = [  # id, AP, parents, need, lock, lane, laneN, page, row, col, role   (roles: 0 spine, 1 pick-one, 2 ability, 3 modifier, 5-9 page 2)
  ("ROOT", 0, [], None, None, 0, 0, 0, 0, 4, 0),
  ("P1", 0, ["ROOT"], None, None, 0, 0, 0, 1, 4, 0),
  ("P2", 0, ["P1"], None, None, 0, 0, 0, 2, 4, 0),
  ("X1", 0, ["P2"], None, "X2", 0, 0, 0, 3, 3, 1),
  ("X2", 0, ["P2"], None, "X1", 0, 0, 0, 3, 5, 1),
  ("P3", 0, ["X1", "X2"], None, None, 0, 0, 0, 4, 4, 0),
  ("P4", 0, ["P3"], None, None, 0, 0, 1, 0, 8, 0),          # page 2 top right, a leaf (the spine's last stat node)
]
for _a, _c in zip(ABL, ABL_COL):
    CT.append((_a, 1, ["ROOT"], None, {"A4a": "A4b", "A4b": "A4a"}.get(_a), 0, 0, 0, 1, _c, 2))
CT_VIS = {}
for _a, _c in zip(ABL, ABL_COL):
    for _k in range(NMOD):
        CT.append((mod_tid(_a, _k), 1, [_a], _a, None, 0, 0, 0, 2 + _k, _c, 3))
        if _k: CT_VIS[mod_tid(_a, _k)] = mod_tid(_a, _k - 1)
# page 2 (0.3.12): T1 top centre (its parent = ROOT on page 1: the Lv 5-25 gates stay reachable), the trunk T2-T6 straight down under it, the
# switch TS (Priest only; parent ROOT) top right under P4, the three paths off T1 through the fork beside it (PA column 0, PB column 2, PC
# column 6), each path 5 nodes straight down and its element under N5 (row 7)
CT += [("T1", 1, ["ROOT"], None, None, 0, 0, 1, 0, 4, 5)]
CT += [("T%d" % _k, (1, 1, 2, 2, 2, 3)[_k - 1], ["T%d" % (_k - 1)], None, None, 0, 0, 1, _k - 1, 4, 5) for _k in range(2, 7)]
CT += [("TS", 0, ["ROOT"], None, None, 0, 0, 1, 1, 8, 9)]
PATH_AP = [2, 2, 3, 3, 4]
for _ln, (_pre, _el, _col) in enumerate((("PA", "LE", 0), ("PB", "CE", 2), ("PC", "RE", 6))):
    _lane = _ln + 1
    CT += [(_pre + str(_k), PATH_AP[_k - 1], ["T1" if _k == 1 else _pre + str(_k - 1)], None, None, _lane, 0, 1, _k, _col, 6) for _k in range(1, 6)]
    CT += [(_el, 3, [_pre + "5"], None, None, _lane, 5, 1, 6, _col, 7)]
NN = len(CT)
CT_ID = [n[0] for n in CT]
assert NN == 7 + 5 + 25 + 26 - 1 and len(set(CT_ID)) == NN and all(re.fullmatch(r"[A-Z][A-Za-z0-9]*", i) for i in CT_ID), (NN, CT_ID)
assert CT_ID[0] == "ROOT", "TreeClass.intactOf seeds node 0 (the Root)"
assert len(set((n[7], n[8], n[9]) for n in CT)) == NN and all(0 <= n[8] < CROWS and 0 <= n[9] < 9 for n in CT), "one node per cell"
assert len(set(i.lower() for i in CT_ID)) == NN, "node ids are matched ignoring case"
def ct_idx(i): return CT_ID.index(i)
assert all(all(ct_idx(p) < k for p in n[2]) for k, n in enumerate(CT)), "parents come before their children"
assert all(ct_idx(v) < ct_idx(c) for c, v in CT_VIS.items()), "a drawn parent comes before its child"
# the ids 0.3.3 retired (the 0.3.2 stat lanes and capstones; LE / CE / RE stay as the path elements): a saved one refunds itself
RETIRED_IDS = ["L1", "L2", "L3", "L4", "C1", "C2", "C3", "C4", "R1", "R2", "R3", "R4", "LS", "CS", "RS"]
assert not set(RETIRED_IDS) & set(i.upper() for i in CT_ID)
# 0.3.13: the 0.3.12 ability ids the one-time profile update maps (A4 -> A4a / A4b, the modifier SLOT nodes M1A-M4B go away)
OLD_ABIL_IDS = ["A4", "M1A", "M1B", "M2A", "M2B", "M3A", "M3B", "M4A", "M4B"]
assert not set(OLD_ABIL_IDS) & set(i.upper() for i in CT_ID) and not set(OLD_ABIL_IDS) & set(RETIRED_IDS)
# AP: trunk 11 + one path 14 + its element 3 = 28; the abilities + modifiers are counted per class after CN (spec 4.3: about 50)
assert sum(n[1] for n in CT if n[10] == 5) == 11 and sum(PATH_AP) == 14 and all(n[1] == 0 for n in CT if n[10] in (0, 1))
''')

NEWDEFS = '''# ---- the ability / modifier node texts (SkyyClasses' table, baked in by the patch)
MOD_DESC = {"Power": "a stronger main effect each level", "Radius": "a wider area each level", "Duration": "it lasts longer each level",
            "Efficiency": "costs less Mana and Stamina each level", "Split": "splits into smaller copies", "Pierce": "hits one more enemy behind",
            "Chain": "jumps to more targets", "Lingering": "leaves a lingering zone", "Slow": "slows enemies for longer",
            "Knockback": "pushes enemies away", "Follow": "the zone moves with you", "Ward": "a shield for you and your party",
            "Echo": "repeats 1 s later, weaker", "Ricochet": "bounces to another enemy", "Haste": "a burst of speed after the cast",
            "Pull": "pulls enemies in", "Leech": "heals you for part of it", "Floor": "never drops below a set strength",
            "Seeker": "seeks the nearest enemy"}
# placeholder icons until the R4 icon round (spec 5.4): vanilla items the page already shows elsewhere (must_icon checks both Assets.zips)
MOD_ICON = {"Power": "Rock_Gem_Ruby", "Radius": "Rock_Gem_Topaz", "Duration": "Rock_Gem_Sapphire", "Efficiency": "Potion_Mana",
            "Split": "Weapon_Arrow_Iron", "Pierce": "Weapon_Kunai", "Chain": "Rock_Gem_Zephyr", "Lingering": "Plant_Fruit_Poison",
            "Slow": "Ingredient_Feathers_Blue", "Knockback": "Weapon_Shield_Iron", "Follow": "Ingredient_Feathers_Light",
            "Ward": "Weapon_Shield_Orbis_Incandescent", "Echo": "Deco_Scroll", "Ricochet": "Weapon_Arrow_Deadeye", "Haste": "Potion_Stamina",
            "Pull": "Ingredient_Feathers_Dark", "Leech": "Potion_Health", "Floor": "Rock_Gem_Emerald", "Seeker": "Weapon_Arrow_Trueshot"}
ABIL_ICON = ["Deco_Scroll"] * 5               # the ability nodes keep 0.3.12's scroll in the static table; the page shows the rune icon
''' + "C_ABILS = %r   # 0.3.13: SkyyClasses' abilities per class, tier 0-4: (ability id, name, [modifier ids]) or None\n" % C_ABILS + \
"C_MODNAME = %r   # 0.3.13: SkyyClasses' modifier display names\n" % C_MODNAME + \
"C_NOUNS = %r   # fix round 2: SkyyClasses' level-gain nouns (the focus view's text-fit asserts)\n" % C_NOUNS + '''assert set(MOD_DESC) == set(C_MODNAME) == set(MOD_ICON), "every modifier has a text and an icon"
assert sorted(C_ABILS) == sorted(CLASSES) and all(len(v) == 5 for v in C_ABILS.values())
assert all(len(a[2]) <= NMOD and len(set(a[2])) == len(a[2]) for v in C_ABILS.values() for a in v if a)
# the build cross-checks the baked table against the newest SkyyClasses build script it finds (a later SkyyClasses changed its abilities)
def _cls_check():
    import ast as _ast, glob as _glob
    _cands = sorted(_glob.glob(os.path.join(os.path.dirname(HERE), "SkyyClasses", "build_skyyclasses_0.1.*.py")),
                    key=lambda p: [int(x) for x in re.findall(r"(\\d+)", os.path.basename(p))])
    if not _cands: return "no SkyyClasses build script found (not checked)"
    _t = _ast.parse(open(_cands[-1], encoding="utf8").read())
    _l = {}
    for _n in _t.body:
        if isinstance(_n, _ast.Assign) and len(_n.targets) == 1 and isinstance(_n.targets[0], _ast.Name) and _n.targets[0].id in ("ABILS", "AB_MODS", "MODS"):
            _l[_n.targets[0].id] = _ast.literal_eval(_n.value)
    _c = {}
    for _id, _nm, _cl, _ti, _b, _p in _l["ABILS"]:
        _c.setdefault(_cl, [None] * 5)[_ti] = (_id, _nm, list(_l["AB_MODS"][_id]))
    if _c != C_ABILS or dict((m[0], m[1]) for m in _l["MODS"]) != C_MODNAME:
        raise SystemExit("0.3.13: SkyyClasses' abilities / modifiers changed in %s - re-run tools/trees_0_3_13_patch.py with the new table" % os.path.basename(_cands[-1]))
    return "matches " + os.path.basename(_cands[-1])
CLS_CHECK = _cls_check()
def cls_abil(cn, tier): return C_ABILS[cn][tier]
'''
rep('''CN = []   # per class x node:''', NEWDEFS + '''CN = []   # per class x node:''')

rep('''        elif role == 2:   # 0.3.7: ENABLE ability line 1-4 (kind K: SkyyClasses applies it once it lists Class.<Class>.A<n>)
            kind = "K"
            ab = CABIL.get(cn)
            if ab:
                name, now = ab[int(nid[1]) - 1][0], ab[int(nid[1]) - 1][1]
                how = "Enables the ability on your keys (SkyyClasses applies it). Free (0 AP), no parent node - only its class level"
            else:
                name, now = "Ability " + ROMAN[int(nid[1]) - 1], "Ability line " + nid[1] + " - comes with this class's abilities"
        else:             # 0.3.7: modifier slot 1 / 2 of ability line n
            kind = "K"
            ab = CABIL.get(cn)
            ln_ = int(nid[1])
            if ab:
                name = ab[ln_ - 1][2] + " Mod " + ("I" if nid[2] == "A" else "II")
                now = "Opens modifier slot " + ("1" if nid[2] == "A" else "2") + " of " + ab[ln_ - 1][3] + " - equip modifiers in the panel"
                how = "Free (0 AP). Modifiers unlock with the ability's own level and level up by use. A stackable one can sit in both slots"
            else:
                name, now = "Modifier " + ROMAN[ln_ - 1] + "-" + nid[2], "Modifier slot - comes with this class's abilities"
''', '''        elif role == 2:   # 0.3.13: an ABILITY node - buying it (class.ap.ability, 1 AP) unlocks the ability; SkyyClasses applies it (kind K)
            kind = "K"
            ab = cls_abil(cn, ABL_TIER[ABL.index(nid)])
            if ab is None:
                hid, name, now, how = True, "Ability", "", ""
            else:
                abid, name, icon = ab[0], ab[1], ABIL_ICON[ABL.index(nid)]
                now = "Unlocks %s: castable, in your loadout and listed under Abilities" % ab[1]
                tw = cls_abil(cn, 7 - ABL_TIER[ABL.index(nid)]) if nid in ("A4a", "A4b") else None
                how = (("Pick one: buying it blocks %s (a respec frees the choice). " % tw[1]) if tw else "") + \\
                      "Needs its class level; AP: the Cost line. The ability's level then grows by use and adds power"
        elif role == 3:   # 0.3.13: a MODIFIER node - buying it (class.ap.modifier, 1 AP) unlocks that modifier for that ability at once
            kind = "K"
            pa_ = _par[0]
            k_ = int(nid[len(pa_) + 1:]) - 1
            ab = cls_abil(cn, ABL_TIER[ABL.index(pa_)])
            if ab is None or k_ >= len(ab[2]):
                hid, name, now, how = True, "Modifier", "", ""
            else:
                abid, modid = ab[0], ab[2][k_]
                name, icon = C_MODNAME[modid], MOD_ICON[modid]
                now = "%s for %s - %s" % (C_MODNAME[modid], ab[1], MOD_DESC[modid])
                how = "Needs only %s (AP: the Cost line). Usable at once: click %s under Abilities, then a modifier slot. Its level grows by use" % (ab[1], ab[1])
        else:
            raise SystemExit("0.3.13: unknown class node role %d (%s)" % (role, nid))
''')
rep('''        kind, amt, name, icon, mn, now, how, hid = "-", 0, nid, "Deco_Scroll", 0, "", "", False
        node = None''', '''        kind, amt, name, icon, mn, now, how, hid = "-", 0, nid, "Deco_Scroll", 0, "", "", False
        abid, modid = "", ""   # 0.3.13: SkyyClasses' ability id / modifier id of an ability or modifier node
        node = None''')
rep('''        elif role in (2, 3, 4) and not how: how = "Comes with the class abilities: SkyyClasses lists Class.%s.%s when this class has them - until then it waits" % (cn, nid)''',
    '''        elif role in (2, 3) and not how: how = "Comes with the class abilities: SkyyClasses lists Class.%s.%s when this class has them - until then it waits" % (cn, nid)''')
rep('''        CN.append(dict(ci=ci, n=ct_idx(nid), kind=kind, amt=amt, name=name, icon=icon, min=mn, now=now, how=how, hid=hid, rk=rk,
                       m2=CMANA2.get((cn, nid), 0)))''', '''        sid = (_par[0] + "." + modid) if (role == 3 and not hid) else nid   # 0.3.13: the SAVED id (a modifier node: "<ability>.<Modifier>")
        CN.append(dict(ci=ci, n=ct_idx(nid), kind=kind, amt=amt, name=name, icon=icon, min=mn, now=now, how=how, hid=hid, rk=rk,
                       m2=CMANA2.get((cn, nid), 0), sid=sid, abid=abid, modid=modid))''')
# 0.3.13: the icon hook keys use the SAVED id (Mage.A1.Power)
rep('''for c in CN:   # 0.3.12: the icon hook (a hidden switch keeps its unused icon)
    if not c["hid"]: c["icon"] = node_icon("%s.%s" % (CLASSES[c["ci"]], CT_ID[c["n"]]), c["icon"])
_ART_KEYS |= set("%s.%s" % (CLASSES[c["ci"]], CT_ID[c["n"]]) for c in CN if not c["hid"])''', '''for c in CN:   # 0.3.12: the icon hook (a hidden switch keeps its unused icon); 0.3.13: keyed by the saved id (Mage.A1.Power)
    if not c["hid"]: c["icon"] = node_icon("%s.%s" % (CLASSES[c["ci"]], c["sid"]), c["icon"])
_ART_KEYS |= set("%s.%s" % (CLASSES[c["ci"]], c["sid"]) for c in CN if not c["hid"])''')
rep('''assert all(len(c["name"]) <= 24 and "," not in c["name"] and "_" not in c["name"] for c in CN)''',
    '''assert all(len(c["name"]) <= 24 and "," not in c["name"] and "_" not in c["name"] and "~" not in c["name"] for c in CN)
# 0.3.13: per class the saved ids are unique (ignoring case), no saved id contains a separator of the saved line / the bridge csv
for _ci in range(NC):
    _sids = [c["sid"] for c in CN if c["ci"] == _ci and not c["hid"]]
    assert len(set(x.lower() for x in _sids)) == len(_sids) and all(re.fullmatch(r"[A-Z][A-Za-z0-9]*(\\.[A-Z][A-Za-z]*)?", x) for x in _sids), _sids
assert all("~" not in c[f] for c in CN for f in ("now", "how", "icon", "sid", "abid", "modid"))''')
rep('''_now = sorted((CLASSES[c["ci"]], CT_ID[c["n"]]) for c in CN if c["n"] >= 19 and c["kind"] in "HMRVBCF" and c["kind"] != "-")''',
    '''_now = sorted((CLASSES[c["ci"]], CT_ID[c["n"]]) for c in CN if CT[c["n"]][7] == 1 and CT_ID[c["n"]] != "P4" and c["kind"] in "HMRVBCF" and c["kind"] != "-")''')
rep('''assert [c["name"] for c in CN if c["hid"]] == ["Switch"] * 7 and CN[CLASSES.index("Priest") * NN + ct_idx("TS")]["kind"] == "T"
assert all(c["min"] == 0 for c in CN if c["n"] < 19) and all(c["min"] > 0 for c in CN if c["n"] >= 19 and CT_ID[c["n"]] != "P4")''',
    '''assert [c["name"] for c in CN if c["hid"] and CT_ID[c["n"]] == "TS"] == ["Switch"] * 7 and CN[CLASSES.index("Priest") * NN + ct_idx("TS")]["kind"] == "T"
# 0.3.13: the hidden ability / modifier slots = the Assassin's A4b column + every 5th slot of a 4-modifier ability
_HIDM = sorted((CLASSES[c["ci"]], CT_ID[c["n"]]) for c in CN if c["hid"] and CT[c["n"]][10] in (2, 3))
assert _HIDM == sorted([("Assassin", "A4b")] + [(cn, mod_tid(ABL[t], k)) for cn in CLASSES for t in range(5) for k in range(NMOD)
                                                 if (C_ABILS[cn][t] is None or k >= len(C_ABILS[cn][t][2]))]), _HIDM
assert all(c["min"] == 0 for c in CN if CT[c["n"]][7] == 0) and all(c["min"] > 0 for c in CN if CT[c["n"]][7] == 1 and CT_ID[c["n"]] != "P4")''')
rep('''    return sum(c["amt"] for c in CN if c["ci"] == ci and c["kind"] == kind and CT_ID[c["n"]] != ("X2" if pick == "X1" else "X1") and c["n"] < 19)''',
    '''    return sum(c["amt"] for c in CN if c["ci"] == ci and c["kind"] == kind and CT_ID[c["n"]] != ("X2" if pick == "X1" else "X1") and CT[c["n"]][10] in (0, 1))''')

block('''# links (a parent -> child pair on the same page; P3 -> P4, ROOT -> T1 and ROOT -> TS cross the page break without a bar) and their bars''',
      '''assert all(any(PL1[q] == li for q in range(len(PL1))) for li in range(len(CT_LINKS))), "every link is drawn"
''', '''# links (a drawn parent -> child pair on the same page; P3 -> P4, ROOT -> T1 and ROOT -> TS cross the page break without a bar). 0.3.13: a
# modifier slot k >= 2 is drawn from the slot above it (CT_VIS) - its logical parent stays the ability
def _drawn(k, n):
    if n[0] in CT_VIS: return [CT_VIS[n[0]]]
    return [p for p in n[2] if CT[ct_idx(p)][7] == n[7]]
CT_LINKS = [(ct_idx(p), k) for k, n in enumerate(CT) for p in _drawn(k, n)]
assert len(CT_LINKS) == (5 + 6 + 25) + (5 + 3 + 12 + 3) and (ct_idx("P3"), ct_idx("P4")) not in CT_LINKS and (ct_idx("ROOT"), ct_idx("T1")) not in CT_LINKS
# 0.3.13 THE GOLD RULE per link: gate LP = the logical parent (the ability for a modifier column), lit when the gate is lit and ANY of the
# link's targets LD is lit (a modifier column: the slot it reaches and every slot under it - the line you walked down to the deepest owned)
LINK_LP, LINK_LD = [], []
for (_a, _b) in CT_LINKS:
    if CT[_b][10] == 3:
        _ab = ct_idx(CT[_b][2][0])
        _col = [k for k, n in enumerate(CT) if n[10] == 3 and n[2][0] == CT[_b][2][0] and n[8] >= CT[_b][8]]
        LINK_LP.append(_ab); LINK_LD.append(_col)
    else:
        LINK_LP.append(_a); LINK_LD.append([_b])
CT_CELL = dict(((n[7], n[8], n[9]), k) for k, n in enumerate(CT))
# the bent links go through junction cells (a corner with no node); every other link is a straight bar
CT_BENT = {("ROOT", "A1"): [(0, 0)], ("ROOT", "A2"): [(0, 1)], ("ROOT", "A3"): [(0, 2)],          # 0.3.13: ROOT's fork along row 0 to the
           ("ROOT", "A4a"): [(0, 7), (1, 7)], ("ROOT", "A4b"): [(0, 7), (1, 7)],                   # ability columns (A1-A3 left; fix round: the A4
                                                                                                   # pair hangs from ONE drop - the pick-one bracket)
           ("P2", "X1"): [(2, 3)], ("P2", "X2"): [(2, 5)],                                          # the spine's pick-one bracket opens under P2
           ("X1", "P3"): [(4, 3)], ("X2", "P3"): [(4, 5)],                                          # ... and closes at P3
           ("T1", "PA1"): [(0, 0)], ("T1", "PB1"): [(0, 2)], ("T1", "PC1"): [(0, 6)]}   # page 2: T1's fork to the three paths
# 0.3.12 THE DOWNWARD RULE: a link's child sits on a LOWER row than its parent, and its way never climbs (a fork runs along the parent's row
# at most, then straight down)
for (_a, _b) in CT_LINKS:
    _way = [(CT[_a][8], CT[_a][9])] + CT_BENT.get((CT_ID[_a], CT_ID[_b]), []) + [(CT[_b][8], CT[_b][9])]
    assert CT[_b][8] > CT[_a][8], "0.3.12: %s -> %s does not go down" % (CT_ID[_a], CT_ID[_b])
    assert all(_way[_w + 1][0] >= _way[_w][0] for _w in range(len(_way) - 1)), "0.3.12: %s -> %s climbs: %s" % (CT_ID[_a], CT_ID[_b], _way)
# a slot's pieces (role): 0 the single bar of a straight pass-through cell, 1 up arm, 2 left arm, 3 centre, 4 right arm, 5 down arm,
# 6 the stub in the slot's right 4 px gap, 7 the stub in its bottom 4 px gap. PIECES[(page, row, col, role)] = [link indices]
PIECES, JUNCTION, HPASS = {}, set(), set()   # HPASS = the horizontal pass-through cells
def _piece(pg, r, c, role, li):
    PIECES.setdefault((pg, r, c, role), [])
    if li not in PIECES[(pg, r, c, role)]: PIECES[(pg, r, c, role)].append(li)
for (a, b) in CT_LINKS:   # 0.3.3: every bend first (a later link may pass through an earlier link's corner)
    for w in CT_BENT.get((CT_ID[a], CT_ID[b]), []): JUNCTION.add((CT[a][7],) + w)
for li, (a, b) in enumerate(CT_LINKS):
    pg = CT[a][7]
    way = [(CT[a][8], CT[a][9])] + CT_BENT.get((CT_ID[a], CT_ID[b]), []) + [(CT[b][8], CT[b][9])]
    for s in range(len(way) - 1):
        (r1, c1), (r2, c2) = way[s], way[s + 1]
        assert r1 == r2 or c1 == c2, "a diagonal link: %s" % (way,)
        if r1 == r2:
            lo, hi = min(c1, c2), max(c1, c2)
            for c in range(lo, hi): _piece(pg, r1, c, 6, li)
            for c in range(lo + 1, hi):
                assert (pg, r1, c) not in CT_CELL, "a bar through a node cell"
                if (pg, r1, c) in JUNCTION: _piece(pg, r1, c, 2, li); _piece(pg, r1, c, 3, li); _piece(pg, r1, c, 4, li)
                else: _piece(pg, r1, c, 0, li); HPASS.add((pg, r1, c))
        else:
            lo, hi = min(r1, r2), max(r1, r2)
            for r in range(lo, hi): _piece(pg, r, c1, 7, li)
            for r in range(lo + 1, hi):
                assert (pg, r, c1) not in CT_CELL, "a bar through a node cell"
                if (pg, r, c1) in JUNCTION: _piece(pg, r, c1, 1, li); _piece(pg, r, c1, 3, li); _piece(pg, r, c1, 5, li)
                else: _piece(pg, r, c1, 0, li)
    for w in range(1, len(way) - 1):   # the corner's arms: towards the cell before and the cell after
        (r, c) = way[w]
        for (rr, cc) in (way[w - 1], way[w + 1]):
            role = 1 if rr < r else (5 if rr > r else (2 if cc < c else 4))
            _piece(pg, r, c, role, li)
        _piece(pg, r, c, 3, li)
assert all(not (pg, r, c) in CT_CELL for (pg, r, c) in JUNCTION) and len(JUNCTION) == 12
# 0.3.12: nothing overlaps - no pass-through cell carries a horizontal AND a vertical bar (a crossing would need a junction)
_VPASS = set()
for li, (a, b) in enumerate(CT_LINKS):
    _way = [(CT[a][8], CT[a][9])] + CT_BENT.get((CT_ID[a], CT_ID[b]), []) + [(CT[b][8], CT[b][9])]
    for _w in range(len(_way) - 1):
        (r1, c1), (r2, c2) = _way[_w], _way[_w + 1]
        if c1 == c2:
            for r in range(min(r1, r2) + 1, max(r1, r2)):
                if (CT[a][7], r, c1) not in JUNCTION: _VPASS.add((CT[a][7], r, c1))
assert not (_VPASS & HPASS), "0.3.12: a bar crosses another bar outside a junction: %s" % sorted(_VPASS & HPASS)
assert all(len(v) <= 3 for v in PIECES.values()), "a piece carries at most three links (0.3.3: the three paths share T1's corner)"
assert all(role not in (0,) or (pg, r, c) not in JUNCTION for (pg, r, c, role) in PIECES)
# slots: kind 0 empty, 1 node, 2 a horizontal pass-through bar, 3 a vertical one, 4 a junction; arms = 1 up, 2 left, 4 right, 8 down
NSLOT = 9 * CROWS   # 0.3.12: 63 (was 54: 6 rows)
SLOT_KIND, SLOT_NODE, SLOT_ARMS, SLOT_R, SLOT_D = [0] * (2 * NSLOT), [-1] * (2 * NSLOT), [0] * (2 * NSLOT), [False] * (2 * NSLOT), [False] * (2 * NSLOT)
for pg in range(2):
    for r in range(CROWS):
        for c in range(9):
            k = pg * NSLOT + r * 9 + c
            if (pg, r, c) in CT_CELL: SLOT_KIND[k], SLOT_NODE[k] = 1, CT_CELL[(pg, r, c)]
            elif (pg, r, c) in JUNCTION:
                SLOT_KIND[k] = 4
                for bit, role in ((1, 1), (2, 2), (4, 4), (8, 5)):
                    if (pg, r, c, role) in PIECES: SLOT_ARMS[k] |= bit
            elif (pg, r, c, 0) in PIECES: SLOT_KIND[k] = 2 if (pg, r, c) in HPASS else 3
            SLOT_R[k] = (pg, r, c, 6) in PIECES
            SLOT_D[k] = (pg, r, c, 7) in PIECES
assert SLOT_KIND.count(1) == NN and SLOT_KIND.count(4) == 12 and SLOT_KIND.count(2) == 6 and SLOT_KIND.count(3) == 0, (SLOT_KIND.count(2), SLOT_KIND.count(3))
# corners (right + down, left + down, up + right, up + left) and the fork tees (left + right + down) - no arm points up out of a fork except
# the bracket corners under X1 / X2 and (fix round) the A4 pick-one bracket (up + left + right)
assert all(SLOT_ARMS[k] in (0, 4 | 8, 2 | 8, 1 | 4, 1 | 2, 2 | 4 | 8, 1 | 2 | 4) for k in range(2 * NSLOT)) and sum(1 for k in range(2 * NSLOT) if SLOT_ARMS[k]) == 12
assert [SLOT_ARMS[NSLOT + c] for c in range(9)] == [4 | 8, 0, 2 | 4 | 8, 0, 0, 0, 2 | 8, 0, 0] and [SLOT_KIND[NSLOT + c] for c in range(9)] == [4, 2, 4, 2, 1, 2, 4, 0, 1]
assert [SLOT_ARMS[c] for c in range(9)] == [12, 14, 14, 0, 0, 0, 0, 10, 0] and [SLOT_KIND[c] for c in range(9)] == [4, 4, 4, 2, 1, 2, 2, 4, 0]
assert SLOT_ARMS[9 + 7] == 1 | 2 | 4 and [SLOT_KIND[9 + c] for c in (6, 7, 8)] == [1, 4, 1] and SLOT_R[9 + 6] and SLOT_R[9 + 7]   # fix round: the A4 bracket
assert [SLOT_ARMS[r * 9 + c] for (r, c) in ((2, 3), (2, 5), (4, 3), (4, 5))] == [12, 10, 5, 3]
assert not any(SLOT_R[k] or SLOT_D[k] for k in range(2 * NSLOT) if SLOT_KIND[k] == 0), "a stub in an empty slot"
PL1, PL2, PL3 = [-1] * (2 * NSLOT * 8), [-1] * (2 * NSLOT * 8), [-1] * (2 * NSLOT * 8)
for (pg, r, c, role), ls in PIECES.items():
    q = (pg * NSLOT + r * 9 + c) * 8 + role
    PL1[q] = ls[0]
    if len(ls) > 1: PL2[q] = ls[1]
    if len(ls) > 2: PL3[q] = ls[2]
assert sum(1 for x in PL1 if x >= 0) == len(PIECES) and sum(1 for x in PL3 if x >= 0) >= 3
assert all(any(PL1[q] == li for q in range(len(PL1))) for li in range(len(CT_LINKS))), "every link is drawn"
''')
rep('''for _tx in ["Locked", "Owned", "Coming", "Pick one", "Turned off", "Respec", "Lv 100", "Lane 5", "Need 999 AP", "Unlock 9 AP", "Path locked",
            "All players", "Party only"] + ["Needs " + i for i in CT_ID]:''', '''for _tx in ["Locked", "Owned", "Coming", "Pick one", "Turned off", "Respec", "Lv 100", "Lane 5", "Need 999 AP", "Unlock 9 AP", "Path locked",
            "All players", "Party only", "Kept", "Unlock free"] + ["Needs " + i for i in sorted(set(p for n in CT for p in n[2]))]:   # 0.3.13: the parents only''')
rep('''assert all(SUI.text_width(c["name"] + "  (" + CT_ID[c["n"]] + ")", 18, True) <= 344 for c in CN)''',
    '''assert all(SUI.text_width(c["name"] + "  (" + c["sid"] + ")", 18, True) <= 344 for c in CN if not c["hid"])   # 0.3.13: the saved id''')

# ================================================================================================================ trees.properties class block
rep('''CLASS_SCALARS = [("class.enabled", "true"), ("class.ap.first", "1"), ("class.ap.every", "2"), ("class.ap.max", "50"),
                 ("class.respec.perLevel", "100"), ("class.undo", "true"), ("class.debug.extraAp", "0")]''',
    '''CLASS_SCALARS = [("class.enabled", "true"), ("class.ap.first", "1"), ("class.ap.every", "2"), ("class.ap.max", "50"),
                 ("class.respec.perLevel", "100"), ("class.undo", "true"), ("class.debug.extraAp", "0"),
                 ("class.ap.ability", "1"), ("class.ap.modifier", "1"), ("class.ap.spine", "0")]   # 0.3.13 (spec 4.1 + Q2)''')
rep('''              "# Class respec: coins = class skill level x perLevel (SkyyCoins); cooldown = respec.cooldownMinutes; undo = Undo on the page."]''',
    '''              "# Class respec: coins = class skill level x perLevel (SkyyCoins); cooldown = respec.cooldownMinutes; undo = Undo on the page.",
              "# 0.3.13: ability nodes (A1 A2 A3 A4a A4b) cost class.ap.ability, modifier nodes (A1.Power ...) class.ap.modifier, the spine links",
              "# P1-P4 / X1 / X2 class.ap.spine (0 = free); the Root is free. A missing line = these defaults (1 / 1 / 0)."]''')
rep('''                   "# Ids: ROOT P1 P2 X1 X2 P3 P4 (the spine; X1 / X2 = pick one), A1-A4 + M1A-M4B (rune slots), T1-T6 (trunk), PA1-PA5 PB1-PB5",''',
    '''                   "# Ids: ROOT P1 P2 X1 X2 P3 P4 (the spine; X1 / X2 = pick one; their AP = class.ap.spine), T1-T6 (trunk), PA1-PA5 PB1-PB5",''')
rep('''                   "# (L1-L4 C1-C4 R1-R4 LS CS RS) are no longer read."]''',
    '''                   "# (L1-L4 C1-C4 R1-R4 LS CS RS) are no longer read. 0.3.13: the ability + modifier nodes have no line (their AP rows are above);",
                   "# old class.nodes lines of A1-A4 / M1A-M4B are no longer read."]''')
rep('''        if c["hid"]: continue          # 0.3.3: the switch slot of the classes without one has no line
        out.append("class.nodes.%s.%s=true,%d,%d" % (cn, CT_ID[n], c["amt"], 0 if CT[n][10] in (2, 3, 4) else CT[n][1]))   # 0.3.7: A / M free''',
    '''        if c["hid"] or CT[n][10] in (2, 3): continue   # 0.3.3: no line for a hidden switch; 0.3.13: none for ability / modifier nodes
        out.append("class.nodes.%s.%s=true,%d,%d" % (cn, CT_ID[n], c["amt"], CT[n][1]))''')
rep('''NHID = sum(1 for c in CN if c["hid"])
NMIN = sum(1 for c in CN if c["min"] and not c["hid"])
assert NHID == 7 and NMIN == NC * 24 + 1, (NHID, NMIN)   # 0.3.10: + the Spellblade's hidden Switch    # per class trunk 6 + paths 15 + elements 3; TS only on the Priest
assert sum(1 for l in CLASS_LINES if not l.startswith("#")) == 7 + NMIN + NC * NN - NHID and all(ord(ch) < 128 and len(l) <= 160 for l in CLASS_LINES for ch in l)''',
    '''NHID = sum(1 for c in CN if c["hid"])
NMIN = sum(1 for c in CN if c["min"] and not c["hid"])
NABM = sum(1 for c in CN if CT[c["n"]][10] in (2, 3) and not c["hid"])   # 0.3.13: the ability + modifier nodes (no class.nodes line)
assert NHID == 7 + len(_HIDM) and NMIN == NC * 24 + 1, (NHID, NMIN)   # 0.3.10: + the Spellblade's hidden Switch; per class trunk 6 + paths 15 + elements 3; TS only on the Priest
assert sum(1 for l in CLASS_LINES if not l.startswith("#")) == len(CLASS_SCALARS) + NMIN + NC * NN - NHID - NABM and all(ord(ch) < 128 and len(l) <= 160 for l in CLASS_LINES for ch in l)
# 0.3.13 THE AP BUDGET (spec 4.3): 4 abilities + the modifiers of A1-A3 + the larger A4 alt + trunk 11 + one path 14 + its element 3
AP_BUDGET = {}
for _cn in CLASSES:
    _ab = C_ABILS[_cn]
    AP_BUDGET[_cn] = 4 + len(_ab[0][2]) + len(_ab[1][2]) + len(_ab[2][2]) + max(len(_ab[3][2]), len(_ab[4][2]) if _ab[4] else 0) + 11 + 14 + 3
assert all(48 <= v <= 52 for v in AP_BUDGET.values()), AP_BUDGET''')
rep('''assert "class.nodes.Mage.A1=true,0,0\\n" in DEFAULTS and "class.nodes.Priest.M1B=true,0,0\\n" in DEFAULTS   # 0.3.7 second fix round''',
    '''assert "class.nodes.Mage.A1=" not in DEFAULTS and "class.nodes.Priest.M1B=" not in DEFAULTS and "class.nodes.Mage.P1=true,5,0\\n" in DEFAULTS   # 0.3.13
assert "class.ap.ability=1\\n" in DEFAULTS and "class.ap.modifier=1\\n" in DEFAULTS and "class.ap.spine=0\\n" in DEFAULTS''')

# ================================================================================================================ TreeDefs helpers + TreeClass tables
# TreeClass' <clinit> was 62.6 of 64 KB in 0.3.12: the big tables (the per-class texts and the piece lists) are built from joined literals now
rep('''# ---- 0.3 part 2: TreeClass constants (the template of the Python block above, class-major where a value is per class)
F(cls, "public static final int NN = %d;" % NN)''', '''# 0.3.13: TreeClass' big tables come from joined literals (its <clinit> was 62.6 of 64 KB): a String[] split on "~", an int[] on ","
M(defs, r"""
public static String[] strs(String[] parts, int n) {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < parts.length; i++) b.append(parts[i]);
  String[] r = b.toString().split("~", -1);
  if (r.length != n) throw new IllegalStateException("TreeDefs.strs: " + r.length + " values, " + n + " expected");
  return r;
}""")
M(defs, r"""
public static int[] ints(String s, int n) {
  int[] r = new int[n];
  if (n == 0) return r;
  String[] p = s.split(",");
  if (p.length != n) throw new IllegalStateException("TreeDefs.ints: " + p.length + " values, " + n + " expected");
  for (int i = 0; i < n; i++) r[i] = Integer.parseInt(p[i].trim());
  return r;
}""")
def jstrs(xs):
    assert xs and all("~" not in x for x in xs)
    t = "~".join(xs)
    parts = [t[i:i + 16000] for i in range(0, len(t), 16000)] or [""]
    return "@PKG@.TreeDefs.strs(new String[] { %s }, %d)" % (", ".join(json.dumps(p) for p in parts), len(xs))
def jints(xs):
    return "@PKG@.TreeDefs.ints(%s, %d)" % (json.dumps(",".join(str(int(x)) for x in xs)), len(xs))
# ---- 0.3 part 2: TreeClass constants (the template of the Python block above, class-major where a value is per class)
F(cls, "public static final int NN = %d;" % NN)''')
rep('''F(cls, "public static final String[] CNM = %s;" % jstr([c["name"] for c in CN]))
F(cls, "public static final String[] CIC = %s;" % jstr([c["icon"] for c in CN]))
F(cls, "public static final String[] CNOW = %s;" % jstr([c["now"] for c in CN]))
F(cls, "public static final String[] CHOW = %s;" % jstr([c["how"] for c in CN]))''', '''F(cls, "public static final String[] CNM = %s;" % jstrs([c["name"] for c in CN]))
F(cls, "public static final String[] CIC = %s;" % jstrs([c["icon"] for c in CN]))
F(cls, "public static final String[] CNOW = %s;" % jstrs([c["now"] for c in CN]))
F(cls, "public static final String[] CHOW = %s;" % jstrs([c["how"] for c in CN]))
# 0.3.13: the SAVED id of every class node (a modifier node "A1.Power"), its SkyyClasses ability id / modifier id ("" = not an ability /
# modifier node), the ability node ids + their indices, the gold rule of every link (LP gate, LD targets), the modifier names + icons
F(cls, "public static final String[] CID = %s;" % jstrs([c["sid"] for c in CN]))
F(cls, "public static final String[] CABID = %s;" % jstrs([c["abid"] for c in CN]))
F(cls, "public static final String[] CMOD = %s;" % jstrs([c["modid"] for c in CN]))
F(cls, "public static final String[] ABLN = %s;" % jstr(ABL))
F(cls, "public static final int[] ABLI = %s;" % jint([ct_idx(a) for a in ABL]))
F(cls, "public static final int[] LP = %s;" % jint(LINK_LP))
F(cls, "public static final int[] LDS = %s;" % jint([sum(len(x) for x in LINK_LD[:i]) for i in range(len(LINK_LD))]))
F(cls, "public static final int[] LDN = %s;" % jint([len(x) for x in LINK_LD]))
F(cls, "public static final int[] LDV = %s;" % jints([v for x in LINK_LD for v in x]))
F(cls, "public static final String[] MODID = %s;" % jstr(sorted(C_MODNAME)))
F(cls, "public static final String[] MODNM = %s;" % jstr([C_MODNAME[m] for m in sorted(C_MODNAME)]))
F(cls, "public static final String[] MODIC = %s;" % jstr([MOD_ICON[m] for m in sorted(C_MODNAME)]))
F(cls, "public static final String[] OLDAB = %s;" % jstr(OLD_ABIL_IDS))
F(cls, "public static final int[] APB = %s;" % jint([AP_BUDGET[cn] for cn in CLASSES]))   # the AP a full build of each class needs''')
rep('''F(cls, "public static final int[] CRKL = %s;" % jint([(c["rk"] + [(0, 0)] * 3)[r][0] for c in CN for r in range(3)]))   # 0.3.3: rank levels (3 per node)
F(cls, "public static final int[] CRKA = %s;" % jint([(c["rk"] + [(0, 0)] * 3)[r][1] for c in CN for r in range(3)]))   # 0.3.3: + what each rank adds''',
    '''F(cls, "public static final int[] CRKL = %s;" % jints([(c["rk"] + [(0, 0)] * 3)[r][0] for c in CN for r in range(3)]))   # 0.3.3: rank levels (3 per node)
F(cls, "public static final int[] CRKA = %s;" % jints([(c["rk"] + [(0, 0)] * 3)[r][1] for c in CN for r in range(3)]))   # 0.3.3: + what each rank adds''')
rep('''F(cls, "public static final int[] PL1 = %s;" % jint(PL1))
F(cls, "public static final int[] PL2 = %s;" % jint(PL2))
F(cls, "public static final int[] PL3 = %s;" % jint(PL3))          # 0.3.3: the three paths share T1's corner''',
    '''F(cls, "public static final int[] PL1 = %s;" % jints(PL1))
F(cls, "public static final int[] PL2 = %s;" % jints(PL2))
F(cls, "public static final int[] PL3 = %s;" % jints(PL3))          # 0.3.3: the three paths share T1's corner''')
rep('''M(cls, r"""
public static int nodeIdx(String id) {
  if (id == null) return -1;
  String t = id.trim();
  for (int i = 0; i < NN; i++) if (NID[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")''', '''M(cls, r"""
public static int nodeIdx(String id) {
  if (id == null) return -1;
  String t = id.trim();
  for (int i = 0; i < NN; i++) if (NID[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
# 0.3.13: a node by its SAVED id in class ci (a modifier node "A1.Power"; every other node = its template id), ignoring case; -1 = none
M(cls, r"""
public static int nodeIdx(int ci, String id) {
  if (id == null || ci < 0 || ci >= NC) return -1;
  String t = id.trim();
  if (t.length() == 0) return -1;
  for (int i = 0; i < NN; i++) if (CID[ci * NN + i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
M(cls, r"""
public static String sid(int ci, int n) {
  if (n < 0 || n >= NN) return "";
  return (ci < 0 || ci >= NC) ? NID[n] : CID[ci * NN + n];
}""")
M(cls, r"""
public static boolean oldAbilId(String id) {
  if (id == null) return false;
  String t = id.trim();
  for (int i = 0; i < OLDAB.length; i++) if (OLDAB[i].equalsIgnoreCase(t)) return true;
  return false;
}""")
# the placeholder icon of a modifier by its display name ("Power+") - the Lattice cells
M(cls, r"""
public static String modIcon(String name) {
  if (name == null || name.length() == 0) return "Deco_Scroll";
  for (int i = 0; i < MODNM.length; i++) if (MODNM[i].equals(name) || MODID[i].equalsIgnoreCase(name)) return MODIC[i];
  return "Deco_Scroll";
}""")''')

# ================================================================================================================ TreeCfg (the 3 AP rows)
rep('''             "boolean C_UNDO = true", "long C_EXTRA_AP = 0L",
             "boolean[] C_ON = " + jbool([True] * (NC * NN)), "int[] C_AMT = @PKG@.TreeClass.CAMT",
             "int[] C_AP = " + jint([0 if CT[c["n"]][10] in (2, 3, 4) else CT[c["n"]][1] for c in CN]), "int[] C_MIN = @PKG@.TreeClass.CMIN", "boolean HAS33 = true",   # 0.3.3: 7 classes x 44 nodes; fix 2: HAS33''',
    '''             "boolean C_UNDO = true", "long C_EXTRA_AP = 0L",
             "int AP_ABIL = 1", "int AP_MOD = 1", "int AP_SPINE = 0",   # 0.3.13: class.ap.ability / class.ap.modifier / class.ap.spine
             "int AB_OFF = 0", "int M_IGN = 0",   # fix round (critic A3): ability nodes an admin switched off / old M1A-M4B lines saying false (logged when it changes)
             "boolean[] C_ON = " + jbool([True] * (NC * NN)), "int[] C_AMT = @PKG@.TreeClass.CAMT",
             "int[] C_AP = " + jint([CT[c["n"]][1] for c in CN]), "int[] C_MIN = @PKG@.TreeClass.CMIN", "boolean HAS33 = true",   # 0.3.13: 8 classes x 62 nodes (abilities + modifiers 1, the Root + spine 0)''')
rep('''  C_EXTRA_AP = clampL(lng(p, "class.debug.extraAp", 0L), 0L, 1000L);
  int cnn = @PKG@.TreeClass.NC * @PKG@.TreeClass.NN;''', '''  C_EXTRA_AP = clampL(lng(p, "class.debug.extraAp", 0L), 0L, 1000L);
  int apAb = (int) clampL(lng(p, "class.ap.ability", 1L), 0L, 10L);    // 0.3.13 (spec 4.1): an ability node
  int apMd = (int) clampL(lng(p, "class.ap.modifier", 1L), 0L, 10L);   // 0.3.13: a modifier node
  int apSp = (int) clampL(lng(p, "class.ap.spine", 0L), 0L, 10L);      // 0.3.13 (spec Q2: free links): P1-P4, X1, X2
  AP_ABIL = apAb; AP_MOD = apMd; AP_SPINE = apSp;
  int cnn = @PKG@.TreeClass.NC * @PKG@.TreeClass.NN;
  int abOff = 0;      // fix round (critic A3): ability nodes switched off by a class.nodes line (A1 A2 A3 A4a A4b, or the 0.3.12 A4 line = both alts)
  String abOffAt = "";
  int mIgn = 0;       // ... and old M1A-M4B lines that say false (the modifier slots come with the ability now - not read)
  String mIgnAt = "";''')
rep('''    if (@PKG@.TreeClass.NROLE[nn] >= 2 && @PKG@.TreeClass.NROLE[nn] <= 4) {   // 0.3.7 fix round: the A / M nodes are free
      if (cap[j] != 0 && cap[j] != @PKG@.TreeClass.NAP[nn] && cv != null && cv.split(",", -1).length >= 3) { apIgn++; if (apIgnAt.length() == 0) apIgnAt = ck; }   // an admin's own price (not the old default)
      cap[j] = 0;
    }''', '''    int rl = @PKG@.TreeClass.NROLE[nn];   // 0.3.13: the ability + modifier nodes cost the AP rows (a line's amount / AP is not read)
    if (rl == 2) {   // fix round (critic A3): an ability node keeps an admin's OFF switch (its own line, or the 0.3.12 A4 line for A4a / A4b)
      boolean off = !con[j];
      if (!off && @PKG@.TreeClass.NID[nn].startsWith("A4")) {
        String ov = p.getProperty("class.nodes." + @PKG@.TreeClass.CLASSES[ci] + ".A4");
        if (ov != null && ov.split(",", -1)[0].trim().equalsIgnoreCase("false")) off = true;
      }
      con[j] = !off; cam[j] = 0; cap[j] = apAb;
      if (off && !@PKG@.TreeClass.hidden(ci, nn)) { abOff++; if (abOffAt.length() == 0) abOffAt = "class.nodes." + @PKG@.TreeClass.CLASSES[ci] + "." + @PKG@.TreeClass.NID[nn]; }
    }
    else if (rl == 3) { con[j] = true; cam[j] = 0; cap[j] = apMd; }
    else if (rl == 0 || rl == 1) {
      if (nn != 0 && cv != null && cv.split(",", -1).length >= 3 && cap[j] != apSp && cap[j] != 1) { apIgn++; if (apIgnAt.length() == 0) apIgnAt = ck; }   // an admin's own spine price
      cap[j] = nn == 0 ? 0 : apSp;   // the Root is free; the spine costs class.ap.spine
    }''')
rep('''  if (apIgn > 0 && apIgn != AP_IGN) info(apIgn + " class.nodes line(s) set their own AP cost on an A / M ability node (first: " + apIgnAt + ") - those nodes are always free (0.3.7), the AP is ignored.");''',
    '''  if (apIgn > 0 && apIgn != AP_IGN) info(apIgn + " class.nodes line(s) set their own AP cost on a spine node (first: " + apIgnAt + ") - since 0.3.13 the spine costs class.ap.spine (Server Setup -> Trees -> Class trees); the line's AP is not read.");
  for (int cq = 0; cq < @PKG@.TreeClass.NC; cq++) {   // fix round (critic A3): the old modifier SLOT lines are not read any more
    for (int lq = 1; lq <= 4; lq++) {
      for (int aq = 0; aq < 2; aq++) {
        String mk0 = "class.nodes." + @PKG@.TreeClass.CLASSES[cq] + ".M" + lq + (aq == 0 ? "A" : "B");
        String mv = p.getProperty(mk0);
        if (mv != null && mv.split(",", -1)[0].trim().equalsIgnoreCase("false")) { mIgn++; if (mIgnAt.length() == 0) mIgnAt = mk0; }
      }
    }
  }
  if (abOff > 0 && abOff != AB_OFF) info(abOff + " ability node(s) are switched OFF by a class.nodes line (first: " + abOffAt + "; a 0.3.12 A4 line switches both A4a and A4b) - nobody can buy or use those abilities. Only the on / off of such a line is read (the AP is the AP per ability node row).");
  if (mIgn > 0 && mIgn != M_IGN) info(mIgn + " old modifier slot line(s) say false (first: " + mIgnAt + ") - since 0.3.13 an ability's 2 modifier slots come with its ability node, so M1A-M4B lines are not read. Switch the ability node off instead (class.nodes.<Class>.A1 ... A4a / A4b = false).");
  AB_OFF = abOff;
  M_IGN = mIgn;''')

# ================================================================================================================ TreeData + the profile update
rep('''afn = pool.makeClass(PKG + ".TreeAbilFn")   # 0.3.7: tree:fn:abil (SkyyClasses' ability gate)''',
    '''afn = pool.makeClass(PKG + ".TreeAbilFn")   # 0.3.7: tree:fn:abil (SkyyClasses' ability gate)
amig = pool.makeClass(PKG + ".TreeAbMig")   # 0.3.13: the one-time ability tree update of a profile (spec 7)
mfn = pool.makeClass(PKG + ".TreeModFn")    # 0.3.13: tree:fn:modOwned''')
rep('''F(dat, "public java.util.UUID uid;")                                # 0.3.8: the owner (the rebirth gate reads their class level)''',
    '''F(dat, "public java.util.UUID uid;")                                # 0.3.8: the owner (the rebirth gate reads their class level)
F(dat, "public boolean[] cgf = new boolean[%d];" % (NC * NN))      # 0.3.13: GRANDFATHERED nodes (Class.<Class>.gf): work, cost 0 until the next respec
F(dat, "public boolean[] cgfChk = new boolean[%d];" % NC)          # 0.3.13: the AP check of the grandfathered nodes still waits (Class.<Class>.gfchk=1)
F(dat, "public boolean tree2;")                                     # 0.3.13: the profile update ran (abil.tree2=done)
F(dat, "public String[] cold = new String[%d];" % NC)               # 0.3.13: 0.3.12 ability ids still waiting for the update (written back as they were)
F(dat, "public long migNext;")                                      # 0.3.13: the next time the tick asks SkyyClasses for the update's facts''')
rep('''F(sto, "public static Object RBFN;")  # 0.3.8: rebirth:part:trees''', '''F(sto, "public static Object RBFN;")  # 0.3.8: rebirth:part:trees
F(sto, "public static Object MFN;")   # 0.3.13: tree:fn:modOwned
# ================= 0.3.13 TreeAbMig: THE ONE-TIME ABILITY TREE UPDATE of a profile (research/Ability-Tree-Redesign-Spec.md 7, PROJECT-RULES 4) =================
# A players/<pkey>.properties without abil.tree2=done: the old ids are mapped with SkyyClasses' facts (class:fn:migInfo: the alt pick + the
# modifiers usable per ability) - A4 -> A4a / A4b, M1A-M4B dropped, every usable modifier of an owned ability = an owned modifier node -
# AFTER a History copy of the untouched file and with one change-log line (the Undo). Every converted node starts GRANDFATHERED (works,
# costs 0); TreeClass.gfCheck pays for them when the class level is known. Pure on the TreeData (the caller holds the TreeStore monitor
# for an installed one); the bridge call happens before, outside every lock.
F(amig, "public static volatile long APPLIED = 0L;")
F(amig, "public static volatile long WAITS = 0L;")
F(amig, "public static volatile String LAST = \\"\\";")
F(amig, "public static volatile boolean TOLD = false;")
F(amig, "public static volatile long SNAPFAILS = 0L;")   # fix round (critic A1): History copies that failed (the update waited)
F(amig, "public static final long T0 = System.currentTimeMillis();")   # fix round 2: this server run's start (a History copy older = an earlier run's)
F(amig, "public static volatile long ROTATED = 0L;")   # fix round 2: earlier runs' History copies kept under a new name
M(amig, r"""
public static String info(String k) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (!(b instanceof java.util.Map) || k == null) return null;
    Object f = ((java.util.Map) b).get("class:fn:migInfo");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(k);
    return r instanceof String ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
M(amig, r"""
public static String field(String info, String key) {
  if (info == null || key == null || key.length() == 0) return null;
  String[] p = info.split(";");
  for (int i = 0; i < p.length; i++) {
    int e = p[i].indexOf('=');
    if (e <= 0) continue;
    if (p[i].substring(0, e).trim().equalsIgnoreCase(key)) return p[i].substring(e + 1).trim();
  }
  return null;
}""")
M(amig, r"""
public static boolean has(String csv, String id) {
  if (csv == null || id == null || csv.length() == 0) return false;
  String[] p = csv.split(",");
  for (int i = 0; i < p.length; i++) if (p[i].trim().equalsIgnoreCase(id)) return true;
  return false;
}""")
M(amig, r"""
public static boolean needs(@PKG@.TreeData d) {
  if (d == null) return false;
  int nn = @PKG@.TreeClass.NN;
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) {
    if (d.cold[ci] != null && d.cold[ci].length() > 0) return true;
    for (int a = 0; a < @PKG@.TreeClass.ABLI.length; a++) if (d.cown[ci * nn + @PKG@.TreeClass.ABLI[a]]) return true;
  }
  return false;
}""")
M(amig, r"""
public static int a4Of(int ci, boolean altB) {
  int na = @PKG@.TreeClass.nodeIdx(ci, altB ? "A4b" : "A4a");
  if (na < 0 || @PKG@.TreeClass.hidden(ci, na)) na = @PKG@.TreeClass.nodeIdx(ci, "A4a");
  if (na < 0 || @PKG@.TreeClass.hidden(ci, na)) return -1;
  return na;
}""")
M(amig, r"""
public static String apply(@PKG@.TreeData d, String info) {
  if (d == null) return "";
  String alt = field(info, "alt");
  boolean altB = alt != null && alt.equalsIgnoreCase("B");
  int nn = @PKG@.TreeClass.NN;
  StringBuilder all = new StringBuilder();
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) {
    int base = ci * nn;
    String old = d.cold[ci] == null ? "" : d.cold[ci];
    String what = "";
    int na = -1;
    if (has(old, "A4")) {
      na = a4Of(ci, altB);
      int tw = na < 0 ? -1 : @PKG@.TreeClass.NLOCK[na];
      if (na >= 0 && (tw < 0 || !d.cown[base + tw])) { d.cown[base + na] = true; what = "A4 -> " + @PKG@.TreeClass.sid(ci, na); }
      else na = -1;
    }
    String ord = d.corder[ci];
    if (ord != null && ord.length() > 0) {
      String[] p = ord.split(",");
      StringBuilder ob = new StringBuilder();
      for (int i = 0; i < p.length; i++) {
        String t = p[i].trim();
        if (t.length() == 0) continue;
        if (t.equalsIgnoreCase("A4")) { if (na < 0) continue; t = @PKG@.TreeClass.sid(ci, na); }
        else if (@PKG@.TreeClass.oldAbilId(t)) continue;
        if (ob.length() > 0) ob.append(',');
        ob.append(t);
      }
      d.corder[ci] = ob.length() == 0 ? null : ob.toString();
    }
    int nab = 0;
    int nmod = 0;
    String mods = "";
    for (int a = 0; a < @PKG@.TreeClass.ABLI.length; a++) {
      int an = @PKG@.TreeClass.ABLI[a];
      if (!d.cown[base + an] || @PKG@.TreeClass.hidden(ci, an)) continue;
      d.cgf[base + an] = true;
      nab++;
      String us = field(info, @PKG@.TreeClass.CABID[base + an]);
      if (us == null || us.length() == 0) continue;
      for (int m = 0; m < nn; m++) {
        if (@PKG@.TreeClass.NROLE[m] != 3 || @PKG@.TreeClass.NPAR1[m] != an || @PKG@.TreeClass.hidden(ci, m)) continue;
        if (!has(us, @PKG@.TreeClass.CMOD[base + m])) continue;
        if (!d.cown[base + m]) { d.cown[base + m] = true; d.corder[ci] = @PKG@.TreeDefs.orderEdit(d.corder[ci], @PKG@.TreeClass.sid(ci, m), true); }
        d.cgf[base + m] = true;
        nmod++;
        mods = mods + (mods.length() > 0 ? " " : "") + @PKG@.TreeClass.sid(ci, m);
      }
    }
    if (nab + nmod > 0) d.cgfChk[ci] = true;
    d.cold[ci] = null;
    if (what.length() > 0 || nab + nmod > 0 || old.length() > 0) {
      if (all.length() > 0) all.append(" | ");
      all.append(@PKG@.TreeClass.CLASSES[ci]).append(": ");
      if (what.length() > 0) all.append(what).append(", ");
      if (old.length() > 0) all.append("old ids ").append(old.replace(',', ' ')).append(" mapped, ");
      all.append(nab).append(" ability + ").append(nmod).append(" modifier nodes (").append(mods).append(") grandfathered until the AP check");
    }
  }
  d.tree2 = true;
  return all.toString();
}""")
# fix round (critic A1, PROJECT-RULES 4 "verified History snapshot first"): true = the History copy is there and checked (a new copy has the
# source's exact length), or there is no players file to keep; false = the update must WAIT (the old ids stay, the tick tries again in 10 s).
# fix round 2 (critic: a stale History after a rollback + a second update): a copy byte-identical to the file is kept as it is; a DIFFERENT
# copy made by an EARLIER server run (a rollback, play on 0.3.12, then this update again) is kept under <k>.properties.<millis> and a fresh
# copy is written, so the Undo restores the state right before THIS update; a different copy from this run (an earlier try of the same
# waiting update) is refreshed in place - the 10 s retries never pile up copies
M(amig, r"""
public static boolean copyOnce(java.nio.file.Path f, java.nio.file.Path h) throws java.io.IOException {
  java.nio.file.LinkOption[] no = new java.nio.file.LinkOption[0];
  boolean src = java.nio.file.Files.exists(f, no);
  boolean hx = java.nio.file.Files.exists(h, no);
  if (hx && !java.nio.file.Files.isRegularFile(h, no)) return false;
  if (!src) return true;
  byte[] b = java.nio.file.Files.readAllBytes(f);
  if (hx) {
    byte[] o = java.nio.file.Files.readAllBytes(h);
    if (java.util.Arrays.equals(o, b)) return true;
    if (o.length > 0 && java.nio.file.Files.getLastModifiedTime(h, no).toMillis() < T0 - 2000L) {
      java.nio.file.Path kept = h.resolveSibling(h.getFileName().toString() + "." + System.currentTimeMillis());
      java.nio.file.Files.move(h, kept, new java.nio.file.CopyOption[0]);
      ROTATED = ROTATED + 1L;
      @PKG@.TreeCfg.info("ability tree update: an older History copy (from an earlier server run) is kept as history/abiltree2/" + String.valueOf(kept.getFileName()) + " - a fresh copy is made before this update");
    }
  }
  java.nio.file.Files.createDirectories(h.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = h.resolveSibling(h.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, b, new java.nio.file.OpenOption[0]);
  java.nio.file.Files.move(tmp, h, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  return java.nio.file.Files.isRegularFile(h, no) && java.nio.file.Files.size(h) == (long) b.length;
}""")
M(amig, r"""
public static void snapFail(String k, String why) {
  SNAPFAILS = SNAPFAILS + 1L;
  if (SNAPFAILS != 1L && SNAPFAILS % 100L != 0L) return;
  @PKG@.TreeCfg.warn("ability tree update: players/" + k + ".properties could not be kept in history/abiltree2 (" + why + ") - the update WAITS (the old ability ids stay) and tries again every 10 s [" + SNAPFAILS + " failed tries so far]");
}""")
M(amig, r"""
public static boolean snapshot(String k) {
  try {
    java.nio.file.Path dir = @PKG@.TreeStore.DIR;
    if (dir == null || k == null) return false;
    java.nio.file.Path f = dir.resolve(k + ".properties");
    java.nio.file.Path h = dir.getParent().resolve("history").resolve("abiltree2").resolve(k + ".properties");
    boolean r = false;
    synchronized (@PKG@.TreeStore.IO) { r = copyOnce(f, h); }
    if (!r) snapFail(k, "the copy is missing, not a file or incomplete");
    return r;
  } catch (Throwable t) {
    snapFail(k, String.valueOf(t));
    return false;
  }
}""")
M(amig, r"""
public static void appendLine(java.nio.file.Path f, String line) throws java.io.IOException {
  java.nio.file.Files.write(f, (line + "\\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
}""")
M(amig, r"""
public static void logLine(String k, String what, String text) {
  try {
    java.nio.file.Path dir = @PKG@.TreeStore.DIR;
    if (dir == null) return;
    java.nio.file.Path f = dir.getParent().resolve("abiltree2-changes.log");
    String line = java.time.LocalDateTime.now().toString() + "\\t" + k + "\\t" + what + "\\t" + text.replace('\\t', ' ').replace('\\n', ' ');
    synchronized (@PKG@.TreeStore.IO) { appendLine(f, line); }
  } catch (Throwable t) { @PKG@.TreeCfg.warn("ability tree update: could not write abiltree2-changes.log: " + t); }
}""")
M(amig, r"""
public static void done(String k, String sum) {
  APPLIED = APPLIED + 1L;
  if (sum == null || sum.length() == 0) return;
  LAST = k + ": " + sum;
  @PKG@.TreeCfg.info("ability tree update (0.3.13) for " + k + ": " + sum + " [abil.tree2=done; the old file: history/abiltree2/" + k + ".properties; abiltree2-changes.log]");
  logLine(k, "update", sum + "\\tUndo: stop the server, copy history/abiltree2/" + k + ".properties over players/" + k + ".properties (and Skyy_SkyyClasses/history/abiltree2/" + k + ".properties over abilities/), then roll SkyyTrees back below 0.3.13 - else the update runs again");
}""")
M(amig, r"""
public static void waits(String k) {
  WAITS = WAITS + 1L;
  if (TOLD) return;
  TOLD = true;
  @PKG@.TreeCfg.info("ability tree update (0.3.13) waits for SkyyClasses 0.1.26 (class:fn:migInfo) - " + k + " keeps its old ability ids until it answers (logged once)");
}""")''')

# ================================================================================================================ TreeStore: read / write
rep('''    String[] retFound = new String[@PKG@.TreeClass.NC];
    int[] retAp = new int[@PKG@.TreeClass.NC];''', '''    String[] retFound = new String[@PKG@.TreeClass.NC];
    int[] retAp = new int[@PKG@.TreeClass.NC];
    boolean t2 = "done".equals(String.valueOf(p.getProperty("abil.tree2")).trim());   // 0.3.13: the ability tree update ran''')
rep('''      boolean known = cfield.length() == 0 || cfield.equals("respecAt") || cfield.equals("on") || cfield.equals("freeRespec") || cfield.equals("notice") || cfield.equals("retired")
        || cfield.equals("order") || cfield.equals("rb");   // 0.3.8''', '''      boolean known = cfield.length() == 0 || cfield.equals("respecAt") || cfield.equals("on") || cfield.equals("freeRespec") || cfield.equals("notice") || cfield.equals("retired")
        || cfield.equals("order") || cfield.equals("rb")   // 0.3.8
        || cfield.equals("gf") || cfield.equals("gfchk");   // 0.3.13''')
rep('''        for (int j = 0; j < ids.length; j++) {
          int cn = @PKG@.TreeClass.nodeIdx(ids[j]);
          if (cn >= 0) { if (!@PKG@.TreeClass.hidden(ci, cn)) d.cown[ci * @PKG@.TreeClass.NN + cn] = true; continue; }
          int ri = @PKG@.TreeClass.retIdx(ids[j]);''', '''        for (int j = 0; j < ids.length; j++) {
          int cn = @PKG@.TreeClass.nodeIdx(ci, ids[j]);   // 0.3.13: the saved id of this class (A1.Power)
          if (cn >= 0) { if (!@PKG@.TreeClass.hidden(ci, cn)) d.cown[ci * @PKG@.TreeClass.NN + cn] = true; continue; }
          if (!t2 && @PKG@.TreeClass.oldAbilId(ids[j])) { d.cold[ci] = d.cold[ci] == null ? ids[j].trim() : d.cold[ci] + "," + ids[j].trim(); continue; }   // 0.3.13: waits for the update
          int ri = @PKG@.TreeClass.retIdx(ids[j]);''')
rep('''      else if (cfield.equals("on")) {
        String[] ids = cv.split(",");
        for (int j = 0; j < ids.length; j++) { int cn = @PKG@.TreeClass.nodeIdx(ids[j]); if (cn >= 0 && @PKG@.TreeClass.isSwitch(cn)) d.con[ci * @PKG@.TreeClass.NN + cn] = true; }
      }''', '''      else if (cfield.equals("on")) {
        String[] ids = cv.split(",");
        for (int j = 0; j < ids.length; j++) { int cn = @PKG@.TreeClass.nodeIdx(ci, ids[j]); if (cn >= 0 && @PKG@.TreeClass.isSwitch(cn)) d.con[ci * @PKG@.TreeClass.NN + cn] = true; }
      }
      else if (cfield.equals("gf")) {   // 0.3.13: the grandfathered nodes
        String[] ids = cv.split(",");
        for (int j = 0; j < ids.length; j++) { int cn = @PKG@.TreeClass.nodeIdx(ci, ids[j]); if (cn >= 0) d.cgf[ci * @PKG@.TreeClass.NN + cn] = true; }
      }
      else if (cfield.equals("gfchk")) d.cgfChk[ci] = "1".equals(cv.trim());''')
rep('''    String nm = p.getProperty("name");
    if (nm != null && nm.trim().length() > 0) d.name = nm.trim();
    String rtx = p.getProperty("rb.lastTx");   // 0.3.8''', '''    for (int j = 0; j < d.cgf.length; j++) if (!d.cown[j]) d.cgf[j] = false;   // 0.3.13: only an owned node is grandfathered
    // 0.3.13 THE ONE-TIME ABILITY TREE UPDATE (spec 7): History copy first, then the old ids mapped with SkyyClasses' facts; without its
    // answer the old ids stay (written back as they were) and TreeClass.maint tries again from the player's tick
    d.tree2 = t2;
    if (!t2) {
      if (!@PKG@.TreeAbMig.needs(d)) d.tree2 = true;   // nothing to map (the marker goes with the next save)
      else {
        String inf = @PKG@.TreeAbMig.info(k);
        if (inf == null) @PKG@.TreeAbMig.waits(k);
        else if (@PKG@.TreeAbMig.snapshot(k)) {   // fix round (critic A1): only after a verified History copy - else the old ids wait
          @PKG@.TreeAbMig.done(k, @PKG@.TreeAbMig.apply(d, inf));
          d.mig = true;
        }
      }
    }
    String nm = p.getProperty("name");
    if (nm != null && nm.trim().length() > 0) d.name = nm.trim();
    String rtx = p.getProperty("rb.lastTx");   // 0.3.8''')
rep('''  // 0.3 part 2: Class.<Class>=<owned ids>, Class.<Class>.respecAt; the kept Class.* lines of unknown classes
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) {
    StringBuilder cs = new StringBuilder();
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) {
      if (!d.cown[ci * @PKG@.TreeClass.NN + n]) continue;
      if (cs.length() > 0) cs.append(',');
      cs.append(@PKG@.TreeClass.NID[n]);
    }''', '''  // 0.3 part 2: Class.<Class>=<owned ids>, Class.<Class>.respecAt; the kept Class.* lines of unknown classes. 0.3.13: the saved ids; the
  // 0.3.12 ability ids still waiting for the update are written back as they were; .gf / .gfchk; abil.tree2=done
  if (d.tree2) p.setProperty("abil.tree2", "done");
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) {
    StringBuilder cs = new StringBuilder();
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) {
      if (!d.cown[ci * @PKG@.TreeClass.NN + n]) continue;
      if (cs.length() > 0) cs.append(',');
      cs.append(@PKG@.TreeClass.sid(ci, n));
    }
    if (!d.tree2 && d.cold[ci] != null && d.cold[ci].length() > 0) { if (cs.length() > 0) cs.append(','); cs.append(d.cold[ci]); }
    StringBuilder cg = new StringBuilder();
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) {
      if (!d.cgf[ci * @PKG@.TreeClass.NN + n] || !d.cown[ci * @PKG@.TreeClass.NN + n]) continue;
      if (cg.length() > 0) cg.append(',');
      cg.append(@PKG@.TreeClass.sid(ci, n));
    }
    if (cg.length() > 0) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".gf", cg.toString());
    if (d.cgfChk[ci]) p.setProperty("Class." + @PKG@.TreeClass.CLASSES[ci] + ".gfchk", "1");''')
rep('''      if (!d.con[ci * @PKG@.TreeClass.NN + n] || !d.cown[ci * @PKG@.TreeClass.NN + n]) continue;
      if (co.length() > 0) co.append(',');
      co.append(@PKG@.TreeClass.NID[n]);''', '''      if (!d.con[ci * @PKG@.TreeClass.NN + n] || !d.cown[ci * @PKG@.TreeClass.NN + n]) continue;
      if (co.length() > 0) co.append(',');
      co.append(@PKG@.TreeClass.sid(ci, n));''')
rep('''  boolean was = d.cown[ci * @PKG@.TreeClass.NN + n];
  d.cown[ci * @PKG@.TreeClass.NN + n] = v;
  if (was == v) return;
  d.corder[ci] = @PKG@.TreeDefs.orderEdit(d.corder[ci], @PKG@.TreeClass.NID[n], v);   // 0.3.8: the purchase order''',
    '''  boolean was = d.cown[ci * @PKG@.TreeClass.NN + n];
  d.cown[ci * @PKG@.TreeClass.NN + n] = v;
  if (!v) d.cgf[ci * @PKG@.TreeClass.NN + n] = false;   // 0.3.13
  if (was == v) return;
  d.corder[ci] = @PKG@.TreeDefs.orderEdit(d.corder[ci], @PKG@.TreeClass.sid(ci, n), v);   // 0.3.8: the purchase order (0.3.13: the saved id)''')
rep('''  for (int n = 0; n < @PKG@.TreeClass.NN; n++) { d.cown[ci * @PKG@.TreeClass.NN + n] = false; d.con[ci * @PKG@.TreeClass.NN + n] = false; }
  d.crespecAt[ci] = now;''', '''  for (int n = 0; n < @PKG@.TreeClass.NN; n++) { d.cown[ci * @PKG@.TreeClass.NN + n] = false; d.con[ci * @PKG@.TreeClass.NN + n] = false; d.cgf[ci * @PKG@.TreeClass.NN + n] = false; }
  d.cgfChk[ci] = false;   // 0.3.13: a respec refunds the grandfathered nodes as normal nodes
  d.cold[ci] = null;      // fix round 2 (critic): the 0.3.12 ids still waiting for the update go too - a respec never brings an old A4 back
  d.crespecAt[ci] = now;''')
rep('''    String o = d.corder[ci];
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) o = @PKG@.TreeDefs.orderEdit(o, @PKG@.TreeClass.NID[n], true);
    d.corder[ci] = o;
    d.crb[ci] = true;
  }''', '''    String o = d.corder[ci];
    for (int n = 0; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) o = @PKG@.TreeDefs.orderEdit(o, @PKG@.TreeClass.sid(ci, n), true);
    d.corder[ci] = o;
    d.crb[ci] = true;
  }
  for (int j = 0; j < d.cgf.length; j++) d.cgf[j] = false;   // 0.3.13: the ability + modifier nodes come back under the gate like every pick
  for (int ci = 0; ci < @PKG@.TreeClass.NC; ci++) d.cgfChk[ci] = false;''')

# ================================================================================================================ TreeClass rules
rep('''public static String key(int ci, int n) {
  return "Class." + CLASSES[ci] + "." + NID[n];
}""")''', '''public static String key(int ci, int n) {
  return "Class." + CLASSES[ci] + "." + sid(ci, n);   // 0.3.13: the saved id (Class.Mage.A1.Power)
}""")''')
rep('''  if (NROLE[n] >= 2 && NROLE[n] <= 4) return false;   // 0.3.7: ability lines + modifier slots are never passed through''',
    '''  if (NROLE[n] == 2 || NROLE[n] == 3) return false;   // 0.3.7: ability nodes + modifier nodes are never passed through (0.3.13 roles)''')
rep('''public static boolean[] ownOf(@PKG@.TreeData d, int ci) {
  boolean[] o = new boolean[NN];
  if (d == null || ci < 0 || ci >= NC) return o;
  for (int n = 0; n < NN; n++) o[n] = d.cown[ci * NN + n];
  return o;
}""")''', '''public static boolean[] ownOf(@PKG@.TreeData d, int ci) {
  boolean[] o = new boolean[NN];
  if (d == null || ci < 0 || ci >= NC) return o;
  for (int n = 0; n < NN; n++) o[n] = d.cown[ci * NN + n];
  return o;
}""")
# 0.3.13: the grandfathered nodes of class ci (owned, Class.<Class>.gf) - they work and cost 0 until the next respec of that class
M(cls, r"""
public static boolean[] gfOf(@PKG@.TreeData d, int ci) {
  boolean[] g = new boolean[NN];
  if (d == null || ci < 0 || ci >= NC) return g;
  for (int n = 0; n < NN; n++) g[n] = d.cgf[ci * NN + n] && d.cown[ci * NN + n];
  return g;
}""")
M(cls, r"""
public static boolean isGf(@PKG@.TreeData d, int ci, int n) {
  return d != null && ci >= 0 && ci < NC && n >= 0 && n < NN && d.cgf[ci * NN + n] && d.cown[ci * NN + n];
}""")''')
rep('''public static boolean[] coveredBy(boolean[] own, int ci, String order, int apAll) {
  boolean[] r = new boolean[NN];
  if (own == null || ci < 0 || ci >= NC) return r;
  boolean[] done = new boolean[NN];
  int[] seq = new int[NN];
  int ns = 0;
  if (order != null && order.length() > 0) {
    String[] p = order.split(",");
    for (int i = 0; i < p.length; i++) {
      int n = nodeIdx(p[i].trim());''', '''public static boolean[] coveredBy(boolean[] own, int ci, String order, int apAll, boolean[] gf) {
  boolean[] r = new boolean[NN];
  if (own == null || ci < 0 || ci >= NC) return r;
  boolean[] done = new boolean[NN];
  int[] seq = new int[NN];
  int ns = 0;
  if (order != null && order.length() > 0) {
    String[] p = order.split(",");
    for (int i = 0; i < p.length; i++) {
      int n = nodeIdx(ci, p[i].trim());   // 0.3.13: the saved id''')
rep('''    int n = seq[i];
    int c = @PKG@.TreeCfg.C_AP[ci * NN + n];
    if (c <= 0) { r[n] = true; continue; }''', '''    int n = seq[i];
    int c = (gf != null && gf[n]) ? 0 : @PKG@.TreeCfg.C_AP[ci * NN + n];   // 0.3.13: a grandfathered node is free
    if (c <= 0) { r[n] = true; continue; }''')
rep('''  return coveredBy(own, ci, d.corder[ci], ap(lv));
}""")''', '''  return coveredBy(own, ci, d.corder[ci], ap(lv), gfOf(d, ci));
}""")''')
rep('''  for (int n = 0; n < NN; n++) if (own[n] && !cov[n] && @PKG@.TreeCfg.C_AP[ci * NN + n] > 0) n0++;''',
    '''  for (int n = 0; n < NN; n++) if (own[n] && !cov[n] && @PKG@.TreeCfg.C_AP[ci * NN + n] > 0 && !d.cgf[ci * NN + n]) n0++;''')
rep('''public static int spent(boolean[] it, int ci) {
  if (ci < 0 || ci >= NC) return 0;
  int s = 0;
  for (int n = 0; n < NN; n++) if (it[n]) s = s + @PKG@.TreeCfg.C_AP[ci * NN + n];
  return s;
}""")''', '''public static int spent(boolean[] it, int ci, boolean[] gf) {
  if (ci < 0 || ci >= NC) return 0;
  int s = 0;
  for (int n = 0; n < NN; n++) if (it[n] && (gf == null || !gf[n])) s = s + @PKG@.TreeCfg.C_AP[ci * NN + n];   // 0.3.13: grandfathered = 0
  return s;
}""")''')
rep('''  if (why == 3) return NPAR2[n] >= 0 || NPAR1[n] < 0 ? "Locked" : "Needs " + NID[gate(skips(own, ci), NPAR1[n])];
  if (why == 4) return "Needs " + NID[NNEED[n]];''', '''  if (why == 3) return NPAR2[n] >= 0 || NPAR1[n] < 0 ? "Locked" : "Needs " + sid(ci, gate(skips(own, ci), NPAR1[n]));
  if (why == 4) return "Needs " + sid(ci, NNEED[n]);''')
rep('''public static String cardText2(@PKG@.TreeData d, boolean[] own, boolean[] it, int ci, int n, int lvl, int apFree, int stt) {
  if (stt == 2 && isSwitch(n)) return switchOn(d, it, ci, n) ? "All players" : "Party only";''', '''public static String cardText2(@PKG@.TreeData d, boolean[] own, boolean[] it, int ci, int n, int lvl, int apFree, int stt) {
  if (stt == 2 && isSwitch(n)) return switchOn(d, it, ci, n) ? "All players" : "Party only";
  if (stt == 2 && isGf(d, ci, n)) return "Kept";   // 0.3.13: grandfathered by the update (free until a respec)
  if (ci >= 0 && n >= 0 && n < NN && NROLE[n] == 3) {   // fix round 2 (critic): a modifier cell names its modifier (the icons are placeholders until R4)
    String t3 = cardText(own, it, ci, n, lvl, apFree, stt);
    if (stt == 2 || t3.equals("Locked") || t3.startsWith("Needs ")) return name(ci, n);   // owned / waiting for its ability: the name; buyable keeps "Unlock N AP"
    return t3;
  }''')
rep('''    String s = nm + " needs " + name(ci, g1) + " (" + NID[g1] + ")";
    if (g2 >= 0 && g2 != g1) s = s + " or " + name(ci, g2) + " (" + NID[g2] + ")";
    s = s + " first";
    int w = sk[p1] ? p1 : ((p2 >= 0 && sk[p2]) ? p2 : -1);
    if (w >= 0) s = s + " (" + NID[w] + (coming(ci, w) ? " waits for " + comingWho(ci, w) + " and is skipped)" : " is skipped)");
    return s;
  }
  if (why == 4) return nm + " needs its ability " + name(ci, NNEED[n]) + " (" + NID[NNEED[n]] + ") first";''', '''    String s = nm + " needs " + name(ci, g1) + " (" + sid(ci, g1) + ")";
    if (g2 >= 0 && g2 != g1) s = s + " or " + name(ci, g2) + " (" + sid(ci, g2) + ")";
    s = s + " first";
    int w = sk[p1] ? p1 : ((p2 >= 0 && sk[p2]) ? p2 : -1);
    if (w >= 0) s = s + " (" + sid(ci, w) + (coming(ci, w) ? " waits for " + comingWho(ci, w) + " and is skipped)" : " is skipped)");
    return s;
  }
  if (why == 4) return nm + " needs its ability " + name(ci, NNEED[n]) + " (" + sid(ci, NNEED[n]) + ") first";''')
rep('''public static boolean[] pieceGold(int pg, boolean[] it) {
  boolean[] g = new boolean[NSLOT * 8];
  if (pg < 0 || pg > 1) return g;
  int base = pg * NSLOT * 8;
  for (int q = 0; q < g.length; q++) {
    int l1 = PL1[base + q];
    int l2 = PL2[base + q];
    int l3 = PL3[base + q];
    g[q] = (l1 >= 0 && it[LA[l1]] && it[LB[l1]]) || (l2 >= 0 && it[LA[l2]] && it[LB[l2]]) || (l3 >= 0 && it[LA[l3]] && it[LB[l3]]);
  }
  return g;
}""")''', '''public static boolean linkGold(int l, boolean[] it) {
  if (l < 0 || l >= LA.length || it == null || !it[LP[l]]) return false;
  for (int i = 0; i < LDN[l]; i++) if (it[LDV[LDS[l] + i]]) return true;
  return false;
}""")
M(cls, r"""
public static boolean[] pieceGold(int pg, boolean[] it) {
  boolean[] g = new boolean[NSLOT * 8];
  if (pg < 0 || pg > 1 || it == null) return g;
  boolean[] lg = new boolean[LA.length];
  for (int l = 0; l < LA.length; l++) lg[l] = linkGold(l, it);   // 0.3.13: the gate + any target (a modifier column: down to the deepest owned)
  int base = pg * NSLOT * 8;
  for (int q = 0; q < g.length; q++) {
    int l1 = PL1[base + q];
    int l2 = PL2[base + q];
    int l3 = PL3[base + q];
    g[q] = (l1 >= 0 && lg[l1]) || (l2 >= 0 && lg[l2]) || (l3 >= 0 && lg[l3]);
  }
  return g;
}""")
# 0.3.13: the drawn pieces of class ci on page pg - a piece shows while one of its links joins two nodes this class has (a 4-modifier
# ability's 5th slot and the Assassin's A4b column draw no bar)
M(cls, r"""
public static boolean[] pieceShow(int ci, int pg) {
  boolean[] g = new boolean[NSLOT * 8];
  if (pg < 0 || pg > 1) return g;
  boolean[] ls = new boolean[LA.length];
  for (int l = 0; l < LA.length; l++) ls[l] = !hidden(ci, LA[l]) && !hidden(ci, LB[l]);
  int base = pg * NSLOT * 8;
  for (int q = 0; q < g.length; q++) {
    int l1 = PL1[base + q];
    int l2 = PL2[base + q];
    int l3 = PL3[base + q];
    g[q] = (l1 >= 0 && ls[l1]) || (l2 >= 0 && ls[l2]) || (l3 >= 0 && ls[l3]);
  }
  return g;
}""")''')
rep('''  int so = spent(intactOf(ownOf(d, ci), ci), ci);''', '''  int so = spent(intactOf(ownOf(d, ci), ci), ci, gfOf(d, ci));''')
rep('''    if (b.length() > 0) b.append(',');
    b.append(NID[n]);
    int a = @PKG@.TreeCfg.C_AMT[ci * NN + n];''', '''    if (b.length() > 0) b.append(',');
    b.append(sid(ci, n));   // 0.3.13: the saved id (A4a, A1.Power)
    int a = @PKG@.TreeCfg.C_AMT[ci * NN + n];''')
rep('''public static Object[] apanel(java.util.UUID u, String csv) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilPanel");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(new Object[] { u, csv });''', '''public static Object[] apanel(java.util.UUID u, String csv) {
  java.util.function.Function f = @PKG@.TreeCalc.fn("class:fn:abilPanel");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(new Object[] { u, csv, "v2" });   // 0.3.13: the focus + Lattice shape (SkyyClasses 0.1.26)''')
rep('''  if (ap == null) return "Your " + CLASSES[ci] + " abilities show here with SkyyClasses 0.1.22 (it is not loaded or did not answer).";''',
    '''  if (ap == null || ap.length < 129) return "Your " + CLASSES[ci] + " abilities show here with SkyyClasses 0.1.26 (it is not loaded, older or did not answer).";''')
block('''# "Power" -> one panel text field: the slot j (0 / 1) of card i
M(cls, r"""
public static String slotText(Object[] ap, int i, int j, int line) {''', '''M(cls, r"""
public static String nameText(Object[] ap, int i) {
  int b0 = 12 + i * 16;
  String nm = String.valueOf(ap[b0 + 1]);
  if (nm.length() == 0) return "-";
  boolean own = Boolean.TRUE.equals(ap[b0 + 3]);
  return own && Boolean.TRUE.equals(ap[8]) ? nm + "  Lv " + ((Integer) ap[b0 + 6]).intValue() : nm;
}""")''', '''# 0.3.13 THE PAGE TEXTS (SkyyClasses 0.1.26 class:fn:abilPanel "v2": the 0.1.25 fields + [94] the combat line, [95..98] usable per row,
# [99..102] rebirth upgrades per row, [103..106] gain per row, [111] the Imbue row, [112] its element, [113] rebirth slots; fix round:
# [120..124] the rune icon of each ability node A1 A2 A3 A4a A4b, [125..128] the stats line per row - 129 fields)
M(cls, r"""
public static String keyShort(int i) {
  if (i == 0) return "Ability 2 key";
  if (i == 1) return "Ability 3 key";
  if (i == 2) return "Crouch + Ability 2";
  return "Crouch + Ability 3";
}""")
M(cls, r"""
public static String nameText(Object[] ap, int i) {
  int b0 = 12 + i * 16;
  String nm = String.valueOf(ap[b0 + 1]);
  if (nm.length() == 0) return "-";
  return Boolean.TRUE.equals(ap[8]) ? nm + "  Lv " + ((Integer) ap[b0 + 6]).intValue() : nm;
}""")
M(cls, r"""
public static boolean usable(Object[] ap, int i) {
  return ap != null && ap.length >= 129 && i >= 0 && i < 4 && Boolean.TRUE.equals(ap[95 + i]);
}""")
M(cls, r"""
public static String usesText(Object[] ap, int i) {
  int b0 = 12 + i * 16;
  if (!Boolean.TRUE.equals(ap[8])) return "Levels are off here";
  long nx = ((Long) ap[b0 + 8]).longValue();
  if (nx <= 0L) return "Top level";
  return nx + " use" + (nx == 1L ? "" : "s") + " to Lv " + (((Integer) ap[b0 + 6]).intValue() + 1);
}""")
M(cls, r"""
public static String modName(Object[] ap, int i, int j) {
  if (j == 0) return String.valueOf(ap[12 + i * 16 + 10]);
  if (j == 1) return String.valueOf(ap[12 + i * 16 + 12]);
  if (j == 2) return String.valueOf(ap[78 + i * 4]);
  return String.valueOf(ap[80 + i * 4]);
}""")
M(cls, r"""
public static int modLvl(Object[] ap, int i, int j) {
  Object o = j == 0 ? ap[12 + i * 16 + 11] : (j == 1 ? ap[12 + i * 16 + 13] : (j == 2 ? ap[79 + i * 4] : ap[81 + i * 4]));
  return o instanceof Integer ? ((Integer) o).intValue() : 0;
}""")
# the row (0-3) of the ability with id `id` in the panel, -1 = none
M(cls, r"""
public static int rowOf(Object[] ap, String id) {
  if (ap == null || id == null || id.length() == 0) return -1;
  for (int i = 0; i < 4; i++) if (id.equals(String.valueOf(ap[12 + i * 16]))) return i;
  return -1;
}""")''')
rep('''public static int parseKey(String key) {
  if (key == null || !key.startsWith("Class.")) return -1;
  String rest = key.substring(6);
  int dot = rest.indexOf('.');
  if (dot <= 0) return -1;
  int ci = classIdx(rest.substring(0, dot));
  int n = nodeIdx(rest.substring(dot + 1));''', '''public static int parseKey(String key) {
  if (key == null || !key.startsWith("Class.")) return -1;
  String rest = key.substring(6);
  int dot = rest.indexOf('.');
  if (dot <= 0) return -1;
  int ci = classIdx(rest.substring(0, dot));
  int n = nodeIdx(ci, rest.substring(dot + 1));   // 0.3.13: the saved id (Class.Mage.A1.Power)''')

# ---- after TreeClass: the AP check, tree:fn:modOwned, the locked writes, the tick's maintenance
rep('''# ================= TreeFx: per-player effect vector + everything published from it =================''', '''# 0.3.13: the class tree with the rebirth gate at a GIVEN class level (no SkyySkills call - safe under the TreeStore monitor)
M(cls, r"""
public static boolean[] intactAt(@PKG@.TreeData d, int ci, int lvl) {
  if (d == null || ci < 0 || ci >= NC || d.bad) return new boolean[NN];
  boolean[] own = ownOf(d, ci);
  if (d.crb[ci]) own = coveredBy(own, ci, d.corder[ci], ap(lvl < 0 ? 0 : lvl), gfOf(d, ci));
  return intactOf(own, ci);
}""")
# 0.3.13 THE AP CHECK of the update (spec 7.4): the grandfathered nodes are paid in order (the abilities, then the modifiers) while the free
# AP cover them; the rest stay grandfathered until the next respec. Pure (the caller holds the TreeStore monitor); { paid, kept } or null
M(cls, r"""
public static int[] gfCheck(@PKG@.TreeData d, int ci, int lvl) {
  if (d == null || d.bad || ci < 0 || ci >= NC || !d.cgfChk[ci] || lvl < 0) return null;
  if (d.crb[ci]) {   // a rebirth-gated tree: paying them could push a later pick out of the gate - they stay grandfathered (a respec frees them)
    int k0 = 0;
    for (int n = 0; n < NN; n++) if (d.cgf[ci * NN + n] && d.cown[ci * NN + n]) k0++;
    d.cgfChk[ci] = false;
    return new int[] { 0, k0 };
  }
  boolean[] it = intactAt(d, ci, lvl);
  int budget = ap(lvl) - spent(it, ci, gfOf(d, ci));
  int paid = 0;
  int kept = 0;
  for (int pass = 0; pass < 2; pass++) {
    for (int n = 0; n < NN; n++) {
      int j = ci * NN + n;
      if (!d.cgf[j] || !d.cown[j] || NROLE[n] != (pass == 0 ? 2 : 3)) continue;
      int c = @PKG@.TreeCfg.C_AP[j];
      if (it[n] && c <= budget) { d.cgf[j] = false; budget = budget - c; paid++; }
      else kept++;
    }
  }
  d.cgfChk[ci] = false;
  return new int[] { paid, kept };
}""")
# 0.3.13 tree:fn:modOwned (spec 8): { UUID, ability id ("Meteor") or node id ("A1"), modifier id ("Power") } -> Boolean: is that modifier
# node intact for the player's own class? null = no gate (class trees off, no class tree, an unreadable tree file)
M(cls, r"""
public static Boolean modOwned(java.util.UUID u, String ab, String mod) {
  if (u == null || ab == null || mod == null || !@PKG@.TreeCfg.CLASS_ON) return null;
  int ci = classIdx(classOf(u));
  if (ci < 0) return null;
  @PKG@.TreeData d = @PKG@.TreeStore.data(u);
  if (d == null || d.bad) return null;
  String a = ab.trim();
  if (a.length() == 0) return Boolean.FALSE;
  String line = null;
  for (int k = 0; k < ABLN.length; k++) {
    int an = ABLI[k];
    if (ABLN[k].equalsIgnoreCase(a) || (!hidden(ci, an) && CABID[ci * NN + an].equalsIgnoreCase(a))) line = ABLN[k];
  }
  if (line == null) return Boolean.FALSE;
  int n = nodeIdx(ci, line + "." + mod.trim());
  if (n < 0 || NROLE[n] != 3) return Boolean.FALSE;
  return Boolean.valueOf(intact(d, ci)[n]);
}""")
mfn.addInterface(pool.get("java.util.function.Function"))
C(mfn, "public TreeModFn() { }")
M(mfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID)) return null;
    return @PKG@.TreeClass.modOwned((java.util.UUID) a[0], a[1] == null ? null : String.valueOf(a[1]), a[2] == null ? null : String.valueOf(a[2]));
  } catch (Throwable t) { return null; }
}""")
# the locked writes of the update / the AP check / the free Root (the TreeStore monitor, like every tree write)
M(sto, r"""
public static synchronized boolean rootOwn(@PKG@.TreeData d, int ci) {
  if (d == null || d.bad || ci < 0 || ci >= @PKG@.TreeClass.NC || d.cown[ci * @PKG@.TreeClass.NN]) return false;
  setClassOwn(d, ci, 0, true);
  return true;
}""")
M(sto, r"""
public static synchronized int[] gfLocked(@PKG@.TreeData d, int ci, int lvl) {
  return @PKG@.TreeClass.gfCheck(d, ci, lvl);
}""")
M(sto, r"""
public static synchronized String mig2Locked(@PKG@.TreeData d, String info) {
  if (d == null || d.bad || d.tree2) return null;
  return @PKG@.TreeAbMig.apply(d, info);
}""")
# ================= TreeFx: per-player effect vector + everything published from it =================''')

rep('''# ================= TreeMsg: one aggregated "Tree bonus" chat line per feedbackMs =================''', '''# 0.3.13 THE TICK'S CLASS TREE MAINTENANCE (world thread, once a second per player): the profile update when SkyyClasses answers (at most
# every 10 s), the free Root from class level 1, the AP check of the grandfathered nodes once the class level is known (+ one chat line).
# fix round: the AP number in the texts comes from the Server Setup rows (critic C3); the update only after a verified History copy (A1); a
# class level below 1 counts as not known yet (A4); maint() guards maint0() so a throw never costs the rest of the tick (B3)
M(cls, r"""
public static String apEach() {
  int a = @PKG@.TreeCfg.AP_ABIL;
  int m = @PKG@.TreeCfg.AP_MOD;
  if (a == m) return a == 0 ? "free" : a + " AP each";
  return "abilities " + a + " AP, modifiers " + m + " AP";
}""")
F(cls, "public static volatile boolean MAINT_FAILED = false;")   # fix round (critic B3): the tick's class tree maintenance threw (logged once)
M(cls, r"""
public static void maint0(@PR@ pr, java.util.UUID u, @PKG@.TreeData d) {
  if (u == null || d == null || d.bad) return;
  String k = @PKG@.TreeStore.pkey(u);
  if (!d.tree2) {
    long now = System.currentTimeMillis();
    if (now >= d.migNext) {
      d.migNext = now + 10000L;
      String inf = @PKG@.TreeAbMig.info(k);
      if (inf != null && @PKG@.TreeAbMig.snapshot(k)) {
        String sm = @PKG@.TreeStore.mig2Locked(d, inf);
        if (sm != null) { @PKG@.TreeAbMig.done(k, sm); @PKG@.TreeStore.dirty(k); }
      }
    }
  }
  int ci = classIdx(classOf(u));
  if (ci >= 0 && @PKG@.TreeCfg.CLASS_ON && !d.cown[ci * NN]) {
    int lv = level(u, ci);
    if (lv >= 1 && @PKG@.TreeStore.rootOwn(d, ci)) { @PKG@.TreeStore.dirty(k); @PKG@.TreeFx.refresh(u); }
  }
  for (int c = 0; c < NC; c++) {
    if (!d.cgfChk[c]) continue;
    int lv = level(u, c);
    if (lv < 1) continue;   // fix round (critic A4): level 0 = not known yet (the check waits for a real level)
    int[] r = @PKG@.TreeStore.gfLocked(d, c, lv);
    if (r == null) continue;
    @PKG@.TreeStore.dirty(k);
    @PKG@.TreeFx.refresh(u);
    String line = CLASSES[c] + " (" + CSKILL[c] + " " + lv + ", " + ap(lv) + " AP): " + r[0] + " ability / modifier nodes paid with AP, " + r[1] + " kept free until the next respec";
    @PKG@.TreeCfg.info("ability tree update (0.3.13) AP check for " + k + ": " + line);
    @PKG@.TreeAbMig.logLine(k, "apcheck", line + "\\tUndo: the same as the update line above");
    if (pr != null && r[0] + r[1] > 0) {
      try { pr.sendMessage(@MSG@.raw("[Trees] Your " + CLASSES[c] + " tree changed: abilities and modifiers are tree nodes now (" + apEach() + "). " + (r[1] > 0 ? r[1] + " you already had stay free until your next respec." : "Every one you had is paid with your Ability Points.") + " /tree class").color("#9cd8ff")); } catch (Throwable t) { }
    }
  }
}""")
M(cls, r"""
public static void maint(@PR@ pr, java.util.UUID u, @PKG@.TreeData d) {
  try { maint0(pr, u, d); }
  catch (Throwable t) {
    if (!MAINT_FAILED) { MAINT_FAILED = true; @PKG@.TreeCfg.warn("class tree maintenance (the ability tree update / free Root / AP check) failed for " + u + " - logged once, the rest of the tick goes on: " + t); }
  }
}""")
# ================= TreeMsg: one aggregated "Tree bonus" chat line per feedbackMs =================''')

# ================================================================================================================ TreeClassOps
rep('''F(cops, "public static final int[] PROBE_OWN = %s;" % jint([ct_idx(i) for i in ("ROOT", "P1", "P2", "X1", "P3", "P4", "T1", "T2", "PA1")]))''',
    '''F(cops, "public static final int[] PROBE_OWN = %s;" % jint([ct_idx(i) for i in ("ROOT", "P1", "P2", "X1", "P3", "P4", "T1", "T2", "PA1", "A1", mod_tid("A1", 0))]))''')
rep('''  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  return @PKG@.TreeClass.ap(lvl) - @PKG@.TreeClass.spent(it, ci) < 0;''', '''  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  return @PKG@.TreeClass.ap(lvl) - @PKG@.TreeClass.spent(it, ci, @PKG@.TreeClass.gfOf(d, ci)) < 0;''')
rep('''  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int sp = @PKG@.TreeClass.spent(it, ci);''', '''  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int sp = @PKG@.TreeClass.spent(it, ci, @PKG@.TreeClass.gfOf(d, ci));''')
rep('''  if (n < 0 || n >= @PKG@.TreeClass.NN || @PKG@.TreeClass.hidden(ci, n)) return "No such node";
  boolean[] own = @PKG@.TreeClass.ownOf(d, ci);''', '''  if (n < 0 || n >= @PKG@.TreeClass.NN || @PKG@.TreeClass.hidden(ci, n)) return "No such node";
  if (!probe && lvl >= 1 && !d.cown[ci * @PKG@.TreeClass.NN] && @PKG@.TreeStore.rootOwn(d, ci)) @PKG@.TreeStore.dirty(@PKG@.TreeStore.pkey(u));   // 0.3.13: the Root is free from class level 1
  boolean[] own = @PKG@.TreeClass.ownOf(d, ci);''')
rep('''  int apFree = @PKG@.TreeClass.ap(lvl < 0 ? 0 : lvl) - @PKG@.TreeClass.spent(it, ci);
  int why = @PKG@.TreeClass.reason(own, it, ci, n, lvl, apFree);''', '''  int apFree = @PKG@.TreeClass.ap(lvl < 0 ? 0 : lvl) - @PKG@.TreeClass.spent(it, ci, @PKG@.TreeClass.gfOf(d, ci));
  int why = @PKG@.TreeClass.reason(own, it, ci, n, lvl, apFree);''')
rep('''  if (@PKG@.TreeClass.NROLE[n] == 6 && @PKG@.TreeClass.pathOf(it) == 0) pick = " You follow the " + @PKG@.TreeClass.pathName(ci, ln) + " path now - the other two are locked (a respec frees them).";
  return "Unlocked " + @PKG@.TreeClass.name(ci, n) + "! " + cost + " AP spent - " + (apFree - cost) + " left." + pick + suffix(probe);''',
    '''  if (@PKG@.TreeClass.NROLE[n] == 6 && @PKG@.TreeClass.pathOf(it) == 0) pick = " You follow the " + @PKG@.TreeClass.pathName(ci, ln) + " path now - the other two are locked (a respec frees them).";
  if (@PKG@.TreeClass.NROLE[n] == 2) pick = " It is on your keys now - click it under Abilities to set its modifiers and its key.";   // 0.3.13
  if (@PKG@.TreeClass.NROLE[n] == 3) pick = " Put it in a modifier slot: click " + @PKG@.TreeClass.name(ci, @PKG@.TreeClass.NPAR1[n]) + " under Abilities.";
  return "Unlocked " + @PKG@.TreeClass.name(ci, n) + "! " + cost + " AP spent - " + (apFree - cost) + " left." + pick + suffix(probe);''')
rep('''    return @PKG@.TreeClass.name(ci, n) + " cannot be undone - " + @PKG@.TreeClass.name(ci, m) + " (" + @PKG@.TreeClass.NID[m] + ") still needs it" + suffix(probe);''',
    '''    return @PKG@.TreeClass.name(ci, n) + " cannot be undone - " + @PKG@.TreeClass.name(ci, m) + " (" + @PKG@.TreeClass.sid(ci, m) + ") still needs it" + suffix(probe);''')
rep('''public static String stateLine(@PKG@.TreeData d, boolean[] it, int stt, int ci, int n) {
  if (stt == 2 && @PKG@.TreeClass.isSwitch(n)) return @PKG@.TreeClass.switchOn(d, it, ci, n) ? "Owned - switch ON" : "Owned - switch OFF";''',
    '''public static String stateLine(@PKG@.TreeData d, boolean[] it, int stt, int ci, int n) {
  if (stt == 2 && @PKG@.TreeClass.isSwitch(n)) return @PKG@.TreeClass.switchOn(d, it, ci, n) ? "Owned - switch ON" : "Owned - switch OFF";
  if (stt == 2 && @PKG@.TreeClass.isGf(d, ci, n)) return "Owned - kept from before (free until a respec)";   // 0.3.13''')
rep('''  else if (r == 2) what = "Ability line";
  else if (r == 3 || r == 4) what = "Modifier slot";''', '''  else if (r == 2) what = "Ability";      // 0.3.13
  else if (r == 3) what = "Modifier";''')
rep('''  String id = @PKG@.TreeClass.NID[n];
  String more = id.equals("P3") ? " - continues on page 2" : (id.equals("P4") ? " - continues on page 1" : "");''',
    '''  if (r == 2 || r == 3) return what + " - " + (ap == 0 ? "free" : ap + " AP");   // 0.3.13
  String id = @PKG@.TreeClass.NID[n];
  String more = id.equals("P3") ? " - continues on page 2" : (id.equals("P4") ? " - continues on page 1" : "");''')
rep('''public static String costLine(int stt, int ci, int n) {
  if (stt == 3) return "Cost: -";''', '''public static String costLine(@PKG@.TreeData d, int stt, int ci, int n) {
  if (stt == 3) return "Cost: -";
  if (@PKG@.TreeClass.isGf(d, ci, n)) return "Cost: free - kept from before";   // 0.3.13''')

# fix round (critic A2): the Root is owned for free from class level 1 (the tick re-takes it), so it never counts as "something to respec" -
# the respec (and the page's first Respec click) says "Nothing to respec" instead of charging coins for an empty tree
rep('''# the class respec (answer 4): coins = class skill level x class.respec.perLevel through coins:fn:take, taken FIRST, then the in-memory reset;''',
    '''# fix round (0.3.13): has the player bought anything in class ci (an owned node other than the free Root)?
M(cops, r"""
public static boolean anyBought(@PKG@.TreeData d, int ci) {
  if (d == null || ci < 0 || ci >= @PKG@.TreeClass.NC) return false;
  for (int n = 1; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) return true;
  return false;
}""")
# the class respec (answer 4): coins = class skill level x class.respec.perLevel through coins:fn:take, taken FIRST, then the in-memory reset;''')
rep('''  boolean any = false;
  for (int n = 0; n < @PKG@.TreeClass.NN; n++) if (d.cown[ci * @PKG@.TreeClass.NN + n]) any = true;
  if (!any) return "Nothing to respec in your " + cn + " tree" + suffix(probe);''', '''  boolean any = anyBought(d, ci);   // fix round (critic A2): the free Root alone is nothing to respec
  if (!any) return "Nothing to respec in your " + cn + " tree" + suffix(probe);''')
rep('''        long pnow = @PKG@.TreeClassOps.priceOf(cd, cci, clv, this.probe);''',
    '''        if (cci >= 0 && !cd.bad && !@PKG@.TreeClassOps.anyBought(cd, cci)) { this.armT = -1; this.msg = @PKG@.TreeClassOps.respec(u, cd, cci, clv, this.probe); rebuild(); return; }   // fix round: nothing bought = nothing armed, nothing charged
        long pnow = @PKG@.TreeClassOps.priceOf(cd, cci, clv, this.probe);''')

# ================================================================================================================ THE CLASS PAGE (R3)
PAGE_NEW = r'''# ---- 0.3 part 2: the class tab (TreePage.buildClass): the same window, tab rows, info row and detail well as the template trees; the
# 950 x 608 list well holds the rune strip + the 9 x 7 graph. FLOW layout only (LayoutMode Left rows of fixed-size slots; a bar is a
# fixed-size colour Group placed by spacers): no absolutely anchored children in a Group, nothing overlaps, every property proven.
# 0.3.13 (R3 of research/Ability-Tree-Redesign-Spec.md, section 6): the middle well lists only the abilities you OWN; clicking one FOCUSES it
# (its level, gain and modifier tiles; Back returns) and turns the right well into the LATTICE view (4 rows: an ability slot + its modifier
# slots). Click an ability, then a slot; a modifier tile, then one of that ability's modifier slots; a filled modifier slot with nothing held
# empties it. Every action goes through SkyyClasses 0.1.26 (class:fn:abilDo: hold / place / mod / clearMod / back / rbpick / attune).
TRC_SLOT_W, TRC_SLOT_H = 92, 78                  # 0.3.12: a graph slot = the 88 x 74 cell + its 4 px gaps right and below (7 rows)
TRC_CELL_W, TRC_CELL_H, TRC_ICON, TRC_ICON_L = 88, 74, 40, 24   # 0.3.12: 74 high, a 40 px icon centred
TRC_BAR = 6                                      # the connector bar thickness (spec 10)
TRC_BAR_X = (TRC_CELL_W - TRC_BAR) // 2          # 41: a vertical bar's left edge
TRC_BAR_Y = (TRC_CELL_H - TRC_BAR) // 2          # 34: a horizontal bar's top edge
TRC_STRIP_H, TRC_STRIP_GAP = 50, 4               # the pager strip and the gap under it
TRC_PG_W, TRC_RS_GAP = 196, 24
TRC_BAR_COL, TRC_GOLD = "disabled", "gold"       # grey #797b7c, gold #E8A93B (kit colours)
TRC_SB_W, TRC_SB_H, TRC_SB_L, TRC_SB_T, TRC_SB_SIZE = 86, 17, 1, 57, 13   # the cell's one state line (13 px bold) under the 40 px icon
TRC_GRID_W = 2 * SUI.WELL_LIST_PAD + 9 * TRC_SLOT_W                       # 836
TRC_RSL_W = TRC_GRID_W - 2 * SUI.WELL_LIST_PAD - TRC_PG_W - TRC_RS_GAP     # the page caption left of the pager
# the middle well (Abilities, 0.3.7 "Panel on the right"; 0.3.13 owned abilities only + the focus view)
TRC_AP_W, TRC_AP_GAP = 262, 12
TRC_AP_IN_W = TRC_AP_W - 2 * SUI.WELL_PAD                                   # 246
TRC_AP_TITLE_H, TRC_AP_HINT_H = 28, 40
TRC_CARD_H, TRC_CARD_GAP, TRC_CARD_ICON, TRC_CARD_IL = 72, 4, 48, 8       # an owned ability card: one clickable cell (icon + 3 lines)
TRC_CARD_TXT_L = TRC_CARD_IL + TRC_CARD_ICON + 8                           # 64
TRC_CARD_TXT_W = TRC_AP_IN_W - TRC_CARD_TXT_L - 4                          # 178
TRC_FB_W = 110                                                              # the focus view: < Back, Max Up (small buttons)
TRC_TILE_H, TRC_TILE_GAP, TRC_TILE_ICON, TRC_TILE_IL = 56, 2, 32, 8        # a modifier tile: one clickable cell (icon + name + what it does); fix round: gap 2
TRC_TILE_TXT_L = TRC_TILE_IL + TRC_TILE_ICON + 8                           # 48
TRC_TILE_TXT_W = TRC_AP_IN_W - TRC_TILE_TXT_L - 4                          # 194
TRC_FS_L_H, TRC_FS_G_H = 34, 40                 # fix round (critic C7): the stats line (up to 2 lines) + the level bonus
# fix round 2 (critic: text past its box): the stats line 12 px, the level bonus 14 px (2 lines each fit); a tile = the name line (14 px bold,
# one line) + the what-it-does line (12 px, 2 lines); the Max Up note 12 px in 2 lines
TRC_FS_L_SIZE, TRC_FS_G_SIZE = 12, 14
TRC_TILE_N_T, TRC_TILE_N_H, TRC_TILE_N_SIZE = 3, 20, 14
TRC_TILE_S_T, TRC_TILE_S_SIZE = TRC_TILE_N_T + TRC_TILE_N_H, 12
TRC_TILE_S_H = TRC_TILE_H - TRC_TILE_S_T                                    # 33
TRC_FX_SIZE = 12
TRC_FX_H = max(SUI.BTN_SMALL_H, int(2 * SUI.line_height(TRC_FX_SIZE)) + 1)   # the Max Up row: the button or 2 note lines
TRC_W = TRC_GRID_W + TRC_AP_GAP + TRC_AP_W + TR_DET_GAP + TR_DET_W + 2 * SUI.CONTENT_PAD
assert TRC_W <= 1600, TRC_W                                                  # the kit's widest page (the class tab only; the trees stay 1440)
TRC_SEC_H = SUI.outer_size(SUI.section(None, "Modifiers"))[1]
TRC_AP_IN_H = TR_GRID_H - 2 * SUI.WELL_PAD
assert SUI.fit([TRC_AP_TITLE_H, TRC_AP_HINT_H + 6] + [TRC_CARD_H + TRC_CARD_GAP] * 4, TRC_AP_IN_H, "ability list") >= 0
assert SUI.fit([TRC_AP_TITLE_H, SUI.BTN_SMALL_H + 6, TRC_CARD_H + 6, TRC_FS_L_H, TRC_FS_G_H + 2, TRC_SEC_H] + [TRC_TILE_H + TRC_TILE_GAP] * 5
               + [TRC_FX_H], TRC_AP_IN_H, "ability focus") >= 0
# fix round 2: every runtime text of the focus view fits its box (measured with the kit's font metrics; worst cases)
assert 2 * SUI.line_height(TRC_FS_L_SIZE) <= TRC_FS_L_H and 2 * SUI.line_height(TRC_FS_G_SIZE) <= TRC_FS_G_H
for _n in C_NOUNS:
    assert SUI.text_lines("Level bonus: +999.9 %% %s" % _n, TRC_AP_IN_W, TRC_FS_G_SIZE) <= 2, _n
assert SUI.line_height(TRC_TILE_N_SIZE, bold=True) <= TRC_TILE_N_H and 2 * SUI.line_height(TRC_TILE_S_SIZE) <= TRC_TILE_S_H
for _m, _mn in C_MODNAME.items():
    assert SUI.text_width(_mn + " Lv 20 - 4 slots", TRC_TILE_N_SIZE, True) <= TRC_TILE_TXT_W, _mn
    assert SUI.text_lines("Not unlocked - node A4b.%s in the tree (10 AP)" % _m, TRC_TILE_TXT_W, TRC_TILE_S_SIZE) <= 2, _m
    assert SUI.text_width(_mn, TRC_SB_SIZE, True) <= TRC_SB_W, _mn   # fix round 2: a modifier cell in the graph names its modifier
assert SUI.text_lines("Rebirth: 99 upgrades - hold a modifier first", TRC_AP_IN_W - TRC_FB_W - 6, TRC_FX_SIZE) <= 2
assert 2 * SUI.line_height(TRC_FX_SIZE) <= TRC_FX_H
TRC_AP_NO_H = TRC_AP_IN_H - TRC_AP_TITLE_H - 6
# the Lattice (the right well while an ability is focused): 4 rows = the key line + the cells (ability 60 + up to 4 modifier cells 84)
TRC_LY_KEY_H, TRC_LY_CELL, TRC_LY_MOD_W, TRC_LY_GAP, TRC_LY_ROW_GAP = 22, 60, 84, 4, 6
TRC_LY_ICON, TRC_LY_MOD_ICON, TRC_LY_LAB_T, TRC_LY_LAB_H = 48, 28, 44, 16
TRC_LY_STATUS_H, TRC_LY_ELEM_H, TRC_LY_HOW_H = 44, SUI.BTN_SMALL_H, 66
TRC_LY_ELEM_W = TR_DET_IN_W - TRC_FB_W - 8
assert TRC_LY_CELL + 8 + 4 * (TRC_LY_MOD_W + TRC_LY_GAP) <= TR_DET_IN_W, "a Lattice row fits the right well"
assert TRC_LY_LAB_T + TRC_LY_LAB_H <= TRC_LY_CELL and (TRC_LY_CELL - TRC_LY_MOD_ICON) // 2 + TRC_LY_MOD_ICON <= TRC_LY_LAB_T
assert SUI.fit([TRC_SEC_H, TRC_LY_STATUS_H + 4] + [TRC_LY_KEY_H + TRC_LY_CELL + TRC_LY_ROW_GAP] * 4 + [TRC_LY_ELEM_H + 6, TRC_SEC_H, TRC_LY_HOW_H],
               TR_GRID_H - 2 * SUI.WELL_PAD, "Lattice") >= 0
TRC_LVL_W = TRC_W - 2 * SUI.CONTENT_PAD - len(TR_TAB_ROWS[0]) * TR_TAB_W - (len(TR_TAB_ROWS[0]) - 1) * TR_TAB_GAP
TRC_NOTE_W = TRC_W - 2 * SUI.CONTENT_PAD - TR_TOK_W - TR_DUST_W
assert 9 * TRC_SLOT_W == TRC_GRID_W - 2 * SUI.WELL_LIST_PAD and TRC_STRIP_H + TRC_STRIP_GAP + CROWS * TRC_SLOT_H == TR_GRID_H - 2 * SUI.WELL_LIST_PAD
assert (TRC_CELL_H - TRC_ICON) // 2 + TRC_ICON <= TRC_SB_T and TRC_SB_T + TRC_SB_H <= TRC_CELL_H and TRC_SB_L + TRC_SB_W <= TRC_CELL_W
assert 44 + 8 + 92 + 8 + 44 == TRC_PG_W and TRC_BAR_X + TRC_BAR + TRC_BAR_X == TRC_CELL_W and TRC_BAR_Y + TRC_BAR + TRC_BAR_Y == TRC_CELL_H
for _t in ("< Back", "Max Up", "Change"):
    assert SUI.text_width(_t, 14, True, upper=True) + 2 * SUI.BTN_SMALL_PAD <= TRC_FB_W, _t
for _t in ("Knockback+ 5", "Efficiency 5", "Rebirth", "Closed", "Empty"):
    assert SUI.text_width(_t, 12, True) <= TRC_LY_MOD_W - 2, _t   # the Lattice cell label: 12 px bold
for _t in ("Crouch + Ability 3", "29 uses to Lv 25", "Levels are off here"):
    assert SUI.text_width(_t, 15, False) <= TRC_CARD_TXT_W, _t
TRC_NEW_IDS = ["SkyyTrNoClass", "SkyyTrRs", "SkyyTrRsL", "SkyyTrPgG", "SkyyTrPgR", "SkyyTrPgP", "SkyyTrPgL", "SkyyTrPgN", "SkyyTrCR0",
               "SkyyTrCS0", "SkyyTrCA0", "SkyyTrC1", "SkyyTrC1Ic", "SkyyTrC1Sb", "SkyyTrCM0", "SkyyTrCU0", "SkyyTrCJ0", "SkyyTrCD0",
               "SkyyTrCG0", "SkyyTrCB0", "SkyyTrUndo",
               # the middle well: the list (0.3.13 owned abilities only) and the focus view
               "SkyyTrAp", "SkyyTrApT", "SkyyTrApH", "SkyyTrApNo", "SkyyTrAc0", "SkyyTrAc0N", "SkyyTrAc0K", "SkyyTrAc0U",
               "SkyyTrFbR", "SkyyTrFb", "SkyyTrFc", "SkyyTrFcN", "SkyyTrFcK", "SkyyTrFcU", "SkyyTrFsL", "SkyyTrFsG", "SkyyTrFt0",
               "SkyyTrFt0N", "SkyyTrFt0S", "SkyyTrFxR", "SkyyTrFx", "SkyyTrFxT",
               # the Lattice (the right well while an ability is focused)
               "SkyyTrLyS", "SkyyTrLy0", "SkyyTrLy0K", "SkyyTrLy0C", "SkyyTrLy0A", "SkyyTrLyM0", "SkyyTrLyM0T", "SkyyTrLyE", "SkyyTrLyEL",
               "SkyyTrLyEB", "SkyyTrLyH", "SkyyTrTab8"]
assert not set(TRC_NEW_IDS) & set(TR_OLD_IDS) and all(SUI.check_id(_i) for _i in TRC_NEW_IDS) and len(set(TRC_NEW_IDS)) == len(TRC_NEW_IDS)

TRC_BUILD = r"""
public void buildClass(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  int t = @PKG@.TreeDefs.NT;
  int nt = t + 1;
  boolean pb = this.probe;
  int ci = pb ? this.pci : @PKG@.TreeClass.classIdx(@PKG@.TreeClass.classOf(u));
  if (ci >= @PKG@.TreeClass.NC) ci = -1;
  String ucls = (pb || ci >= 0) ? null : @PKG@.TreeClass.classOf(u);   // 0.3 fix H: a class this build has no tree for
  if (ucls != null && ucls.length() > 20) ucls = ucls.substring(0, 20);
  @PKG@.TreeData d = (pb && this.pd != null) ? this.pd : @PKG@.TreeStore.data(u);
  int lvl = pb ? @PKG@.TreeClassOps.PROBE_LVL : @PKG@.TreeClass.level(u, ci);
  if (!pb && ci >= 0 && lvl >= 1 && !d.bad && !d.cown[ci * @PKG@.TreeClass.NN] && @PKG@.TreeStore.rootOwn(d, ci)) @PKG@.TreeStore.dirty(@PKG@.TreeStore.pkey(u));   // 0.3.13: the free Root
  boolean[] own = @PKG@.TreeClass.ownOf(d, ci);
  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  int apAll = ci < 0 ? 0 : @PKG@.TreeClass.ap(lvl < 0 ? 0 : lvl);
  int spent = @PKG@.TreeClass.spent(it, ci, @PKG@.TreeClass.gfOf(d, ci));
  int apFree = apAll - spent;
  int cp = this.cpage;
  if (cp < 0 || cp > 1) cp = 0;
  int sel = this.csel;
  if (sel < 0 || sel >= @PKG@.TreeClass.NN) sel = 0;
  if (@PKG@.TreeClass.NPAGE[sel] != cp || @PKG@.TreeClass.hidden(ci, sel)) sel = @PKG@.TreeClass.firstOf(cp);
  int[] cst = @PKG@.TreeClass.states(own, it, ci, lvl, apFree);
  boolean[] pg = @PKG@.TreeClass.pieceGold(cp, @PKG@.TreeClass.lit(own, it, ci));   // 0.3.1: gold through a skipped node a chain uses
  boolean[] psh = @PKG@.TreeClass.pieceShow(ci, cp);   // 0.3.13: no bar to a slot this class does not have
  int st0 = ci < 0 ? 0 : cst[sel];
  String tn = ci < 0 ? "Class" : @PKG@.TreeClass.CLASSES[ci];
  String col = ci < 0 ? @PKG@.TreeDefs.TCOLOR[0] : @PKG@.TreeClass.CCOLOR[ci];
  boolean canUndo = ci >= 0 && (pb || @PKG@.TreeCfg.C_UNDO) && this.undo != null && this.undo.size() > 0;
  boolean freeR = @PKG@.TreeClassOps.freeOf(d, ci, pb);   // 0.3.3: the free respec of the class paths update
  long price = (ci < 0 || lvl < 0 || pb || freeR) ? 0L : @PKG@.TreeClass.respecPrice(lvl);
  boolean sw = ci >= 0 && st0 == 2 && @PKG@.TreeClass.isSwitch(sel);   // 0.3.3: an owned switch - the buy button is Switch
  // 0.3.13: SkyyClasses 0.1.26's panel ("v2", with THIS page's node list), the focused ability (by id: a placed ability changes its row)
  String acsv = ci < 0 ? null : (pb ? @PKG@.TreeClass.abilCsv(u) : @PKG@.TreeClass.csvOf(d, it, ci));   // fix round: probe = the real tree
  Object[] ap = null;
  if (ci >= 0) ap = @PKG@.TreeClass.apanel(u, acsv);
  boolean apOk = ap != null && ap.length >= 129 && "ok".equals(ap[0]);
  int fr = (apOk && this.amode) ? @PKG@.TreeClass.rowOf(ap, this.afoc) : -1;
  if (fr >= 0 && !@PKG@.TreeClass.usable(ap, fr)) fr = -1;
  boolean am = fr >= 0;
  if (!am) { this.amode = false; this.hk = 0; this.hmod = ""; }
  int hk = this.hk;
  String hmod = this.hmod == null ? "" : this.hmod;
  int fb0 = 12 + (am ? fr : 0) * 16;
  String flid = am ? String.valueOf(ap[116 + fr]) : "";
  String[] amr = null;
  if (am) amr = @PKG@.TreeClass.amods(u, this.afoc, acsv);
  if (amr == null) amr = new String[0];
  String[] ah = amr.length > 0 ? amr[0].split("\\|", -1) : new String[0];
  int rbp = 0;   // the rebirth upgrades to place on the focused ability (SkyyClasses 0.1.23 head field 10)
  try { if (ah.length > 10) rbp = Integer.parseInt(ah[10].trim()); } catch (Throwable x2) { rbp = 0; }
  int[] ord = new int[4];   // the OWNED abilities in tree order (A1, A2, A3, A4) - the middle list
  int nOwn = 0;
  if (apOk) {
    for (int ln = 1; ln <= 4; ln++) for (int i = 0; i < 4; i++) if (@PKG@.TreeClass.usable(ap, i) && ((Integer) ap[12 + i * 16 + 5]).intValue() == ln) { ord[nOwn] = i; nOwn++; }
  }
  String[] aic = new String[5];   // the rune icon of each ability node (the graph shows it once SkyyClasses has loaded the rune)
  if (apOk) {
    for (int a = 0; a < 5; a++) { String ri = String.valueOf(ap[120 + a]); if (ri.length() > 0 && !"null".equals(ri)) aic[a] = ri; }   // fix round (critic C9): every ability node, the unpicked A4 alt too
  }
{{SHELL}}
{{HEAD}}
  for (int i = 0; i < nt; i++) {
{{TAB}}
    ev.addEventBinding(@BT@.Activating, "#SkyyTrTab" + i, @EVD@.of("a", "trtab" + i));
  }
{{INFO}}
  b.set("#SkyyTrLvl.Text", (lvl < 0 && !pb) ? "SkyySkills missing" : (ci < 0 ? (ucls != null ? ucls + " - no tree yet" : "No class yet") : @PKG@.TreeClass.CSKILL[ci] + " " + lvl));
  b.set("#SkyyTrTok.Text", "Ability Points " + apFree + " of " + apAll);
  b.set("#SkyyTrDust.Text", pb ? "Respec free (probe)" : (freeR ? "Respec free (once)" : (price > 0L ? "Respec " + @PKG@.TreeDefs.grp(price) + " coins" : "Respec free")));
  b.set("#SkyyTrNote.Text", @PKG@.TreeClassOps.note(ci, lvl, it, apFree, pb, d.bad, ucls));
{{GRID}}
  if (ci < 0) {
{{NOCLASS}}
    b.set("#SkyyTrNoClass.Text", ucls != null ? "Your class " + ucls + " has no skill tree yet - it comes in a later build." : "Choose a class with /class - or create a profile - and your class tree opens here. Page 1 holds your abilities and their modifiers, page 2 the trunk and three paths (the first path node you unlock picks your path).");
  } else {
{{STRIP}}
    b.set("#SkyyTrRsL.Text", cp == 0 ? "Page 1 - abilities, their modifiers and the stat spine" : "Page 2 - trunk and paths (pick one path)");
    b.set("#SkyyTrPgL.Text", "Page " + (cp + 1) + " of 2");
    ev.addEventBinding(@BT@.Activating, "#SkyyTrPgP", @EVD@.of("a", "trpgp"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrPgN", @EVD@.of("a", "trpgn"));
    int base = cp * @PKG@.TreeClass.NSLOT;
    for (int r = 0; r < 7; r++) {   // 0.3.12: 7 graph rows
{{CROW}}
      for (int c = 0; c < 9; c++) {
        int k = r * 9 + c;
        int q = k * 8;
        int sk = @PKG@.TreeClass.SK[base + k];
        int n = @PKG@.TreeClass.SN[base + k];
        int arms = @PKG@.TreeClass.SARMS[base + k];
        if (sk == 1 && @PKG@.TreeClass.hidden(ci, n)) sk = 0;   // 0.3.3: a slot this class does not have stays empty
        if ((sk == 2 || sk == 3) && !psh[q]) sk = 0;           // 0.3.13: ... and so does the bar to it
        if (sk == 4) {
          if (!psh[q + 1]) arms = arms & 14;
          if (!psh[q + 2]) arms = arms & 13;
          if (!psh[q + 4]) arms = arms & 11;
          if (!psh[q + 5]) arms = arms & 7;
          if (!psh[q + 3]) sk = 0;
        }
        boolean sr = @PKG@.TreeClass.SR[base + k] && psh[q + 6];
        boolean sd = @PKG@.TreeClass.SD[base + k] && psh[q + 7];
{{SLOT}}
        if (sk == 0) continue;
{{ROWA}}
        if (sk == 1) {
{{CELL}}
          b.set("#SkyyTrC" + (n + 1) + "Sb.Text", @PKG@.TreeClass.cardText2(d, own, it, ci, n, lvl, apFree, cst[n]));
          ev.addEventBinding(@BT@.Activating, "#SkyyTrC" + (n + 1), @EVD@.of("a", "trc" + (n + 1)));
        } else if (sk == 2) {
{{HBAR}}
        } else if (sk == 3) {
{{VBAR}}
        } else {
{{JUNC}}
        }
{{GAPR}}
{{ROWB}}
      }
    }
  }
{{APANEL}}
  if (!apOk) {
{{APNO}}
    b.set("#SkyyTrApNo.Text", @PKG@.TreeClass.apanelMsg(ap, ci, ucls));
  } else if (!am) {
{{APHINT}}
    b.set("#SkyyTrApH.Text", (nOwn == 0 ? "No abilities yet - buy A1 in the tree (page 1, " + @PKG@.TreeCfg.AP_ABIL + " AP) to unlock your first." : "Click an ability: its modifiers show here and your loadout on the right.") + (pb ? " Probe: view only." : ""));
    for (int j = 0; j < nOwn; j++) {
      int i = ord[j];
      int b0 = 12 + i * 16;
      String ricon = String.valueOf(ap[b0 + 2]);
      String aicon = ricon.length() > 0 ? ricon : @PKG@.TreeClass.CICON[ci];
{{ACARD}}
      b.set("#SkyyTrAc" + j + "N.Text", @PKG@.TreeClass.nameText(ap, i));
      b.set("#SkyyTrAc" + j + "K.Text", @PKG@.TreeClass.keyShort(i));
      b.set("#SkyyTrAc" + j + "U.Text", @PKG@.TreeClass.usesText(ap, i));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrAc" + j, @EVD@.of("a", "tyca" + i));
    }
  } else {
    String fric = String.valueOf(ap[fb0 + 2]);
    String ficon = fric.length() > 0 ? fric : @PKG@.TreeClass.CICON[ci];
    boolean fheld = hk == 1;
{{FOCUS}}
    b.set("#SkyyTrFcN.Text", @PKG@.TreeClass.nameText(ap, fr));
    b.set("#SkyyTrFcK.Text", @PKG@.TreeClass.keyShort(fr) + (fheld ? " - held" : ""));
    b.set("#SkyyTrFcU.Text", @PKG@.TreeClass.usesText(ap, fr));
    b.set("#SkyyTrFsL.Text", String.valueOf(ap[125 + fr]));   // fix round (critic C7): Mana + Stamina + cooldown of this row's cast
    b.set("#SkyyTrFsG.Text", "Level bonus: " + String.valueOf(ap[103 + fr]));   // fix round 2: at most 2 lines (what a use is: the card's uses line)
    ev.addEventBinding(@BT@.Activating, "#SkyyTrFb", @EVD@.of("a", "tyfb"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrFc", @EVD@.of("a", "tyfc"));
    for (int k2 = 0; k2 < amr.length - 1 && k2 < 5; k2++) {
      String[] f = amr[k2 + 1].split("\\|", -1);
      if (f.length < 12) continue;
      boolean un = "1".equals(f[3]);
      int ts = !un ? 0 : ((hk == 2 && f[0].equals(hmod)) ? 2 : 1);
      int cnt = 0;
      try { cnt = Integer.parseInt(f[7].trim()); } catch (Throwable x6) { cnt = 0; }
      String tic = @PKG@.TreeClass.modIcon(f[0]);
{{FTILE}}
      b.set("#SkyyTrFt" + k2 + "N.Text", f[1] + (un ? " Lv " + f[4] + (cnt > 0 ? " - " + cnt + " slot" + (cnt == 1 ? "" : "s") : "") : ""));   // fix round 2: fits one line (held = the tile's selected look)
      b.set("#SkyyTrFt" + k2 + "S.Text", un ? f[9] : "Not unlocked - node " + flid + "." + f[0] + " in the tree (" + @PKG@.TreeCfg.AP_MOD + " AP)");   // fix round 2: 2 lines at most (click: the node's detail)
      ev.addEventBinding(@BT@.Activating, "#SkyyTrFt" + k2, @EVD@.of("a", "tyft" + k2));
    }
    if (rbp > 0) {
{{FMAX}}
      b.set("#SkyyTrFxT.Text", "Rebirth: " + rbp + " upgrade" + (rbp == 1 ? "" : "s") + " - hold a modifier first");   // fix round 2: 2 lines at most
      ev.addEventBinding(@BT@.Activating, "#SkyyTrFx", @EVD@.of("a", "tymx"));
    }
  }
{{DETP}}
  if (!am) {
{{DET}}
    b.set("#SkyyTrDetName.Text", ci < 0 ? @PKG@.TreeClass.NID[sel] : @PKG@.TreeClass.name(ci, sel) + "  (" + @PKG@.TreeClass.sid(ci, sel) + ")");   // 0.3.13: the saved id
    b.set("#SkyyTrDetState.Text", @PKG@.TreeClassOps.stateLine(d, it, st0, ci, sel));
    b.set("#SkyyTrDetNow.Text", @PKG@.TreeClassOps.nowLine(d, it, st0, ci, sel));
    b.set("#SkyyTrDetNext.Text", (ci < 0 ? "" : @PKG@.TreeClassOps.givesLine(ci, sel) + " - ") + @PKG@.TreeClassOps.typeLine(ci, sel));
    b.set("#SkyyTrDetCost.Text", @PKG@.TreeClassOps.costLine(d, st0, ci, sel));
    b.set("#SkyyTrDetNeed.Text", @PKG@.TreeClassOps.needLine(own, it, ci, sel, lvl, apFree, st0));
    b.set("#SkyyTrDetHow.Text", @PKG@.TreeClassOps.howLine(ci, sel));
{{BUY}}
    b.set("#SkyyTrBuyTx.Text", safe(@PKG@.TreeClassOps.buyText(d, own, it, ci, sel, lvl, apFree, st0)));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrBuy", @EVD@.of("a", "trbuy"));
    ev.addEventBinding(@BT@.Activating, "#SkyyTrUndo", @EVD@.of("a", "trundo"));
  } else {
    boolean fight = Boolean.TRUE.equals(ap[3]);
    String fnm = String.valueOf(ap[fb0 + 1]);
    int imb = ap[111] instanceof Integer ? ((Integer) ap[111]).intValue() : -1;
{{LAT}}
    b.set("#SkyyTrLyS.Text", fight ? "In combat - change your loadout out of combat." : (hk == 1 ? "Holding " + fnm + ": click an ability slot (the two trade places)." : (hk == 2 ? "Holding " + @PKG@.TreeClass.modNm(hmod) + ": click a modifier slot in " + fnm + "'s row (" + @PKG@.TreeClass.keyShort(fr) + ")." : "Click an ability or a modifier, then a slot. A filled modifier slot clicked with nothing held empties it.")) + (pb ? " Probe: view only." : ""));
    for (int r2 = 0; r2 < 4; r2++) {
      int rb0 = 12 + r2 * 16;
      boolean ru = @PKG@.TreeClass.usable(ap, r2);
      String rric = String.valueOf(ap[rb0 + 2]);
      String ric = rric.length() > 0 ? rric : @PKG@.TreeClass.CICON[ci];
      int rsl = ru ? ((Integer) ap[rb0 + 14]).intValue() : 0;
      int ncl = rsl > 2 ? rsl : 2;
      int rs = !ru ? 0 : ((hk == 1 && r2 == fr) ? 2 : 1);
{{LROW}}
      b.set("#SkyyTrLy" + r2 + "K.Text", @PKG@.TreeClass.keyShort(r2) + " - " + (ru ? String.valueOf(ap[rb0 + 1]) : "empty"));
      ev.addEventBinding(@BT@.Activating, "#SkyyTrLy" + r2 + "A", @EVD@.of("a", "tyla" + r2));
      for (int j2 = 0; j2 < ncl && j2 < 4; j2++) {
        int q2 = r2 * 4 + j2;
        String mn = @PKG@.TreeClass.modName(ap, r2, j2);
        boolean mo = j2 < rsl;
        int ms = !mo ? 0 : (mn.length() == 0 ? 1 : 2);
        String mic = @PKG@.TreeClass.modIcon(mn);
{{LMOD}}
        b.set("#SkyyTrLyM" + q2 + "T.Text", !mo ? (j2 >= 2 ? "Rebirth" : "Closed") : (mn.length() == 0 ? "Empty" : mn + " " + @PKG@.TreeClass.modLvl(ap, r2, j2)));
        ev.addEventBinding(@BT@.Activating, "#SkyyTrLyM" + q2, @EVD@.of("a", "tylm" + q2));
      }
      if (r2 == imb) {
{{LELEM}}
        b.set("#SkyyTrLyEL.Text", "Imbue element: " + String.valueOf(ap[112]) + " (an Elemental sword uses its own)");
        ev.addEventBinding(@BT@.Activating, "#SkyyTrLyEB", @EVD@.of("a", "tymat"));
      }
    }
{{LTAIL}}
    b.set("#SkyyTrLyH.Text", "Rows: the Ability 2 / 3 keys and crouch + each. An ability sits in one row; its modifiers go in its own row (2 slots, rebirths add up to 2). Out of combat only. Modifiers are bought in the tree; their level grows by use.");
  }
{{FOOT}}
  b.set("#SkyyTrMsg.Text", this.msg == null ? "" : this.msg);
  ev.addEventBinding(@BT@.Activating, "#SkyyTrBack", @EVD@.of("a", "trback"));
  boolean armed = this.armT == t && System.currentTimeMillis() - this.armAt <= 10000L;
{{RESPEC}}
  ev.addEventBinding(@BT@.Activating, "#SkyyTrRespec", @EVD@.of("a", "trrespec"));
}"""


def class_page_java():
    """TreePage.buildClass(): TRC_BUILD with its {{parts}} from kit calls (every markup recorded for assert_proven). 0.3.7: a 1600 wide
    window, the narrower graph, the middle well, the detail well; 0.3.13: the owned-abilities list, the focus view, the Lattice view."""
    sh = SUI.page_shell("SkyyTrF", TRC_W, TR_H, "Skill Trees", kind="plain", body_id="SkyyTrRoot")
    body, W = sh.body, sh.inner_w
    marks = list(sh.appends.markups())

    def app(parent, markup):
        marks.append(markup)
        return SUI.java_append(parent, markup)

    def chain(conds, parent, markups):
        out = []
        for n_, mk in enumerate(markups):
            head = ("if (%s) " % conds[n_]) if n_ == 0 else (("else if (%s) " % conds[n_]) if n_ < len(conds) else "else ")
            out.append(head + app(parent, mk))
        return "\n".join(out)

    r, k, nn = SUI.J("r", "0"), SUI.J("k", "0"), SUI.J("n + 1", "1")
    # ---- the tab rows: the template tabs (Secondary here: t == NT) + the class tab chain (Primary)
    tab_java = []
    for n_, name in enumerate(TREES):
        _row = TR_TAB_ROW_OF[n_]
        anc = None if TR_TAB_ROWS[_row][0] == n_ else {"left": TR_TAB_GAP}
        mk = SUI.choose(SUI.J("i == t"), SUI.button("SkyyTrTab%d" % n_, name, "primary", w=TR_TAB_W, anchor=anc),
                        SUI.button("SkyyTrTab%d" % n_, name, "secondary", w=TR_TAB_W, anchor=anc))
        tab_java.append(("if (i == %d) " % n_ if n_ == 0 else "else if (i == %d) " % n_) + app(TR_TAB_ROW_IDS[_row], mk))
    tab_java.append("else if (i == %d) {\n%s\n}" % (len(TREES), class_tab_chain(app)))
    info = [app(body, SUI.group("SkyyTrInfo", "Left", h=TR_INFO_H)),
            app("SkyyTrHead", SUI.label("SkyyTrLvl", "", "rowName", w=TRC_LVL_W, h=TR_HEAD_H, align="End", col=SUI.J("col", TCOLOR[0]))),
            app("SkyyTrInfo", SUI.label("SkyyTrTok", "", "bold", w=TR_TOK_W, h=TR_INFO_H, col="gold")),
            app("SkyyTrInfo", SUI.label("SkyyTrDust", "", "bold", w=TR_DUST_W, h=TR_INFO_H, col="value")),
            app("SkyyTrInfo", SUI.label("SkyyTrNote", "", "default", w=TRC_NOTE_W, h=TR_INFO_H))]
    # ---- the list well with the pager strip and the graph, or the no-class message
    well = SUI.list_well("SkyyTrGrid", TRC_GRID_W, rows=6, row_h=TR_CELL_H, gap=TR_ROW_GAP)
    assert well.inner_w == TRC_GRID_W - 2 * SUI.WELL_LIST_PAD and well.inner_h == TRC_STRIP_H + TRC_STRIP_GAP + CROWS * TRC_SLOT_H
    grid = [app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrBody", "Left", h=TR_GRID_H)),
            app("SkyyTrBody", well)]
    noclass = app("SkyyTrGrid", SUI.label("SkyyTrNoClass", "", "message", h=well.inner_h, wrap=True))
    strip = [app("SkyyTrGrid", SUI.group("SkyyTrRs", "Left", h=TRC_STRIP_H, anchor={"bottom": TRC_STRIP_GAP})),
             app("SkyyTrRs", SUI.label("SkyyTrRsL", "", "subtitle", w=TRC_RSL_W, h=TRC_STRIP_H))]
    pg_w, pg_gap = 44, 8
    strip += [app("SkyyTrRs", SUI.group("SkyyTrPgG", "Top", w=TRC_PG_W, h=TRC_STRIP_H, anchor={"left": TRC_RS_GAP})),
              app("SkyyTrPgG", SUI.spacer(h=(TRC_STRIP_H - SUI.BTN_SMALL_H) // 2)),
              app("SkyyTrPgG", SUI.group("SkyyTrPgR", "Left", h=SUI.BTN_SMALL_H)),
              chain(["cp > 0"], "SkyyTrPgR", [SUI.button("SkyyTrPgP", "<", "secondary", size="small", w=pg_w),
                                              SUI.button("SkyyTrPgP", "<", "secondary", size="small", w=pg_w, disabled=True)]),
              app("SkyyTrPgR", SUI.label("SkyyTrPgL", "", "bold", w=TRC_PG_W - 2 * pg_w - 2 * pg_gap, h=SUI.BTN_SMALL_H, align="Center", anchor={"left": pg_gap})),
              chain(["cp < 1"], "SkyyTrPgR", [SUI.button("SkyyTrPgN", ">", "secondary", size="small", w=pg_w, anchor={"left": pg_gap}),
                                              SUI.button("SkyyTrPgN", ">", "secondary", size="small", w=pg_w, anchor={"left": pg_gap}, disabled=True)])]
    # ---- the graph: 7 rows of 9 slots; a slot = a Top column: row A (the cell or the bar piece + the right-gap stub) and the bottom-gap stub
    crow = app("SkyyTrGrid", SUI.group("SkyyTrCR" + r, "Left", h=TRC_SLOT_H))
    slot = app("SkyyTrCR" + r, SUI.group("SkyyTrCS" + k, "Top", w=TRC_SLOT_W, h=TRC_SLOT_H))
    rowa = app("SkyyTrCS" + k, SUI.group("SkyyTrCA" + k, "Left", h=TRC_CELL_H))
    node_col = SUI.color_by([("cst[n] == 1", "success"), ("cst[n] == 2", "info"), ("cst[n] == 4", "error")], "disabled")

    def ccell(state, col):
        c = SUI.icon_cell("SkyyTrC" + nn, SUI.J("cicon(ci, n, aic)", "Weapon_Sword_Iron"), state=state, icon=TRC_ICON,
                          w=TRC_CELL_W, h=TRC_CELL_H, icon_left=TRC_ICON_L)
        sb = SUI.label("SkyyTrC" + nn + "Sb", "", "rowSub", w=TRC_SB_W, h=TRC_SB_H, size=TRC_SB_SIZE, bold=True, align="Center", col=col,
                       anchor={"left": TRC_SB_L, "top": TRC_SB_T})
        return _tr_in(c, sb)
    cells = chain(["n == sel && !am", "cst[n] == 3 && @PKG@.TreeClass.slotComing(n)"], "SkyyTrCA" + k, [ccell("selected", "white"), ccell(TR_DRAFT_CELL, "disabled"), ccell("normal", node_col)])

    def gold(role):
        return SUI.color_by([("pg[q + %d]" % role, TRC_GOLD)], TRC_BAR_COL)

    def bar(w, h, role):
        return SUI.group(None, None, w=w, h=h, bg=gold(role))
    arm = TRC_CELL_H - TRC_BAR_Y - TRC_BAR
    hbar = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Top", w=TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCM" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCM" + k, bar(TRC_CELL_W, TRC_BAR, 0))]
    vbar = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Left", w=TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCM" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCM" + k, bar(TRC_BAR, TRC_CELL_H, 0))]
    junc = [app("SkyyTrCA" + k, SUI.group("SkyyTrCM" + k, "Top", w=TRC_CELL_W, h=TRC_CELL_H)),
            "if ((arms & 1) != 0) {",
            app("SkyyTrCM" + k, SUI.group("SkyyTrCU" + k, "Left", h=TRC_BAR_Y)),
            app("SkyyTrCU" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCU" + k, bar(TRC_BAR, TRC_BAR_Y, 1)),
            "} else " + app("SkyyTrCM" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCM" + k, SUI.group("SkyyTrCJ" + k, "Left", h=TRC_BAR)),
            "if ((arms & 2) != 0) " + app("SkyyTrCJ" + k, bar(TRC_BAR_X, TRC_BAR, 2)),
            "else " + app("SkyyTrCJ" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCJ" + k, bar(TRC_BAR, TRC_BAR, 3)),
            "if ((arms & 4) != 0) " + app("SkyyTrCJ" + k, bar(TRC_CELL_W - TRC_BAR_X - TRC_BAR, TRC_BAR, 4)),
            "if ((arms & 8) != 0) {",
            app("SkyyTrCM" + k, SUI.group("SkyyTrCD" + k, "Left", h=arm)),
            app("SkyyTrCD" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCD" + k, bar(TRC_BAR, arm, 5)),
            "}"]
    gapr = ["if (sr) {",
            app("SkyyTrCA" + k, SUI.group("SkyyTrCG" + k, "Top", w=TRC_SLOT_W - TRC_CELL_W, h=TRC_CELL_H)),
            app("SkyyTrCG" + k, SUI.spacer(h=TRC_BAR_Y)),
            app("SkyyTrCG" + k, bar(TRC_SLOT_W - TRC_CELL_W, TRC_BAR, 6)),
            "}"]
    rowb = ["if (sd) {",
            app("SkyyTrCS" + k, SUI.group("SkyyTrCB" + k, "Left", h=TRC_SLOT_H - TRC_CELL_H)),
            app("SkyyTrCB" + k, SUI.spacer(w=TRC_BAR_X)),
            app("SkyyTrCB" + k, bar(TRC_BAR, TRC_SLOT_H - TRC_CELL_H, 7)),
            "}"]
    # ---- 0.3.13 THE MIDDLE WELL: the title; the owned-abilities list (one clickable card each) OR the focus view
    j_, k2_ = SUI.J("j", "0"), SUI.J("k2", "0")
    apanel = [app("SkyyTrBody", SUI.panel("SkyyTrAp", "well", w=TRC_AP_W, h=TR_GRID_H, anchor={"left": TRC_AP_GAP})),
              app("SkyyTrAp", SUI.label("SkyyTrApT", "Abilities", "subtitle", h=TRC_AP_TITLE_H))]
    apno = app("SkyyTrAp", SUI.label("SkyyTrApNo", "", "message", h=TRC_AP_NO_H, wrap=True, anchor={"top": 6}))
    aphint = app("SkyyTrAp", SUI.label("SkyyTrApH", "", "caption", h=TRC_AP_HINT_H, wrap=True, anchor={"bottom": 6}))

    def card3(cid, item, state, gap):
        c = SUI.icon_cell(cid, item, state=state, w=TRC_AP_IN_W, h=TRC_CARD_H, icon=TRC_CARD_ICON, icon_left=TRC_CARD_IL, anchor={"bottom": gap})
        return _tr_in(c, SUI.label(cid + "N", "", "rowName", w=TRC_CARD_TXT_W, h=24, col="white" if state == "selected" else "rowName", anchor={"left": TRC_CARD_TXT_L, "top": 4}),
                      SUI.label(cid + "K", "", "rowSub", w=TRC_CARD_TXT_W, h=20, col="gold", anchor={"left": TRC_CARD_TXT_L, "top": 28}),
                      SUI.label(cid + "U", "", "rowSub", w=TRC_CARD_TXT_W, h=20, anchor={"left": TRC_CARD_TXT_L, "top": 48}))
    acard = app("SkyyTrAp", card3("SkyyTrAc" + j_, SUI.J("aicon", "Weapon_Staff_Iron"), "normal", TRC_CARD_GAP))

    def tile(state):
        c = SUI.icon_cell("SkyyTrFt" + k2_, SUI.J("tic", "Rock_Gem_Ruby"), state=state, w=TRC_AP_IN_W, h=TRC_TILE_H, icon=TRC_TILE_ICON,
                          icon_left=TRC_TILE_IL, anchor={"bottom": TRC_TILE_GAP})
        ncol = {"selected": "white", "disabled": "disabled"}.get(state, "rowName")
        return _tr_in(c, SUI.label("SkyyTrFt" + k2_ + "N", "", "rowName", w=TRC_TILE_TXT_W, h=TRC_TILE_N_H, size=TRC_TILE_N_SIZE, col=ncol,
                                   anchor={"left": TRC_TILE_TXT_L, "top": TRC_TILE_N_T}),
                      SUI.label("SkyyTrFt" + k2_ + "S", "", "rowSub", w=TRC_TILE_TXT_W, h=TRC_TILE_S_H, size=TRC_TILE_S_SIZE, wrap=True,
                                col="disabled" if state == "disabled" else "rowSub", anchor={"left": TRC_TILE_TXT_L, "top": TRC_TILE_S_T}))
    focus = [app("SkyyTrAp", SUI.group("SkyyTrFbR", "Left", h=SUI.BTN_SMALL_H, anchor={"bottom": 6})),
             app("SkyyTrFbR", SUI.button("SkyyTrFb", "< Back", "secondary", size="small", w=TRC_FB_W, sound="cancel")),
             chain(["fheld"], "SkyyTrAp", [card3("SkyyTrFc", SUI.J("ficon", "Weapon_Staff_Iron"), "selected", 6),
                                           card3("SkyyTrFc", SUI.J("ficon", "Weapon_Staff_Iron"), "normal", 6)]),
             app("SkyyTrAp", SUI.label("SkyyTrFsL", "", "rowSub", h=TRC_FS_L_H, size=TRC_FS_L_SIZE, wrap=True, col="gold")),   # fix round: the stats line
             app("SkyyTrAp", SUI.label("SkyyTrFsG", "", "default", h=TRC_FS_G_H, size=TRC_FS_G_SIZE, wrap=True, col="value", anchor={"bottom": 2})),
             app("SkyyTrAp", SUI.section(None, "Modifiers"))]
    ftile = chain(["ts == 0", "ts == 2"], "SkyyTrAp", [tile("disabled"), tile("selected"), tile("normal")])
    fmax = [app("SkyyTrAp", SUI.group("SkyyTrFxR", "Left", h=TRC_FX_H)),
            app("SkyyTrFxR", SUI.button("SkyyTrFx", "Max Up", "secondary", size="small", w=TRC_FB_W)),
            app("SkyyTrFxR", SUI.label("SkyyTrFxT", "", "rowSub", w=TRC_AP_IN_W - TRC_FB_W - 6, h=TRC_FX_H, size=TRC_FX_SIZE, wrap=True, anchor={"left": 6}))]
    # ---- the detail well: the node detail (the template's ids and layout) OR (0.3.13) the Lattice view
    fg0 = SUI.color_by([("st0 == 1", "success"), ("st0 == 2", "info"), ("st0 == 4", "error")], "disabled")
    frame = SUI.SLOT_FRAME
    name_w = TR_DET_IN_W - frame - 12
    sec_h = SUI.outer_size(SUI.section(None, "Effect"))[1]
    det_parts = [frame + 10, 26 + 4, sec_h, 44 + 6, 44 + 6, sec_h, 26 + 6, 44 + 6, sec_h, 66]
    buy_parts = [26 + 6, SUI.BTN_H]
    slack = SUI.fit(det_parts + buy_parts, TR_GRID_H - 2 * SUI.WELL_PAD, "class detail well")
    detp = app("SkyyTrBody", SUI.panel("SkyyTrDet", "well", w=TR_DET_W, h=TR_GRID_H, anchor={"left": TR_DET_GAP}))
    det = [app("SkyyTrDet", SUI.group("SkyyTrDetTop", "Left", h=frame, anchor={"bottom": 10})),
           app("SkyyTrDetTop", SUI.item_frame("SkyyTrDetFrame", frame, icon_id="SkyyTrDetIcon",
                                              item=SUI.J("cicon(ci, sel, aic)", "Weapon_Sword_Iron"))),
           app("SkyyTrDetTop", SUI.label("SkyyTrDetName", "", "rowName", w=name_w, h=frame, wrap=True, col=fg0, anchor={"left": 12})),
           app("SkyyTrDet", SUI.label("SkyyTrDetState", "", "bold", h=26, col=fg0, anchor={"bottom": 4})),
           app("SkyyTrDet", SUI.section(None, "Effect")),
           app("SkyyTrDet", SUI.label("SkyyTrDetNow", "", "default", h=44, wrap=True, col="value", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNext", "", "default", h=44, wrap=True, anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "Cost")),
           app("SkyyTrDet", SUI.label("SkyyTrDetCost", "", "bold", h=26, col="gold", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.label("SkyyTrDetNeed", "", "default", h=44, wrap=True, col="error", anchor={"bottom": 6})),
           app("SkyyTrDet", SUI.section(None, "How it works")),
           app("SkyyTrDet", SUI.label("SkyyTrDetHow", "", "summary", h=66, wrap=True, max_lines=False))]
    buy_col = SUI.color_by([("st0 == 1", "gold"), ("st0 == 2", "success")], "disabled")
    buy = [app("SkyyTrDet", SUI.label("SkyyTrBuyTx", "", "bold", h=26, col=buy_col, anchor={"top": slack, "bottom": 6})),
           app("SkyyTrDet", SUI.group("SkyyTrBuyRow", "Left", h=SUI.BTN_H)),
           chain(["st0 == 3", "sw", "st0 == 2 || st0 == 4"], "SkyyTrBuyRow", [
               SUI.button("SkyyTrBuy", "Coming soon", "secondary", w=TR_BUY_W, disabled=True),
               SUI.button("SkyyTrBuy", "Switch", "primary", w=TR_BUY_W),
               SUI.button("SkyyTrBuy", "Owned", "secondary", w=TR_BUY_W, disabled=True),
               SUI.choose(SUI.J("st0 == 1"), SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W),
                          SUI.button("SkyyTrBuy", "Unlock", "primary", w=TR_BUY_W, disabled=True))]),
           app("SkyyTrBuyRow", SUI.choose(SUI.J("canUndo"), SUI.button("SkyyTrUndo", "Undo", "secondary", w=TR_BUY_W, anchor={"left": 8}),
                                          SUI.button("SkyyTrUndo", "Undo", "secondary", w=TR_BUY_W, anchor={"left": 8}, disabled=True)))]
    # the Lattice: the title, the status line, 4 rows (the key line + the cells), the Imbue element row under its row, how it works
    r2_, q2_ = SUI.J("r2", "0"), SUI.J("q2", "0")
    lat = [app("SkyyTrDet", SUI.section(None, "Loadout")),
           app("SkyyTrDet", SUI.label("SkyyTrLyS", "", "default", h=TRC_LY_STATUS_H, wrap=True, col="value", anchor={"bottom": 4}))]

    def acellL(state):
        return SUI.icon_cell("SkyyTrLy" + r2_ + "A", None if state == "empty" else SUI.J("ric", "Weapon_Staff_Iron"), state=state,
                             w=TRC_LY_CELL, h=TRC_LY_CELL, icon=TRC_LY_ICON, anchor={"right": 8})

    def mcellL(state, lab_col):
        c = SUI.icon_cell("SkyyTrLyM" + q2_, None if state == "empty" else SUI.J("mic", "Rock_Gem_Ruby"), state=state, w=TRC_LY_MOD_W,
                          h=TRC_LY_CELL, icon=TRC_LY_MOD_ICON, icon_left=(TRC_LY_MOD_W - TRC_LY_MOD_ICON) // 2, anchor={"right": TRC_LY_GAP})
        return _tr_in(c, SUI.label("SkyyTrLyM" + q2_ + "T", "", "rowSub", w=TRC_LY_MOD_W - 2, h=TRC_LY_LAB_H, size=12, bold=True, align="Center",
                                   col=lab_col, anchor={"left": 1, "top": TRC_LY_LAB_T}))
    lrow = [app("SkyyTrDet", SUI.group("SkyyTrLy" + r2_, "Top", h=TRC_LY_KEY_H + TRC_LY_CELL, anchor={"bottom": TRC_LY_ROW_GAP})),
            app("SkyyTrLy" + r2_, SUI.label("SkyyTrLy" + r2_ + "K", "", "bold", h=TRC_LY_KEY_H, col=SUI.color_by([("ru", "rowName")], "disabled"))),
            app("SkyyTrLy" + r2_, SUI.group("SkyyTrLy" + r2_ + "C", "Left", h=TRC_LY_CELL)),
            chain(["rs == 0", "rs == 2"], "SkyyTrLy" + r2_ + "C", [acellL("empty"), acellL("selected"), acellL("normal")])]
    lmod = chain(["ms == 0", "ms == 1"], "SkyyTrLy" + r2_ + "C", [mcellL("empty", "disabled"), mcellL("empty", "value"), mcellL("normal", "rowName")])
    lelem = [app("SkyyTrDet", SUI.group("SkyyTrLyE", "Left", h=TRC_LY_ELEM_H, anchor={"bottom": 6})),
             app("SkyyTrLyE", SUI.label("SkyyTrLyEL", "", "rowSub", w=TRC_LY_ELEM_W, h=TRC_LY_ELEM_H, wrap=True)),
             app("SkyyTrLyE", SUI.button("SkyyTrLyEB", "Change", "secondary", size="small", w=TRC_FB_W, anchor={"left": 8}))]
    ltail = [app("SkyyTrDet", SUI.section(None, "How it works")),
             app("SkyyTrDet", SUI.label("SkyyTrLyH", "", "summary", h=TRC_LY_HOW_H, wrap=True, max_lines=False))]
    foot = [app(body, SUI.result_line("SkyyTrMsg", SUI.J("infoColor(this.msg)", SUI.COLOR["success"]), h=TR_MSG_H, anchor={"top": 8})),
            app(body, SUI.separator("content", anchor={"top": 8, "bottom": 8})),
            app(body, SUI.group("SkyyTrFoot", "Left", h=TR_FOOT_H)),
            app("SkyyTrFoot", SUI.button("SkyyTrBack", "< Skills", "secondary", w=TR_BACK_W, sound="cancel"))]
    respec = []
    for ci_, cn in enumerate(CLASSES):
        on = SUI.button("SkyyTrRespec", "Click again to respec " + cn, "destructive", w=TR_RESPEC_ON_W,
                        anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_ON_W)})
        off = SUI.button("SkyyTrRespec", "Respec " + cn, "secondary", w=TR_RESPEC_OFF_W,
                         anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_OFF_W)})
        respec.append(("if (ci == %d) " % ci_ if ci_ == 0 else "else if (ci == %d) " % ci_) + app("SkyyTrFoot", SUI.choose(SUI.J("armed"), on, off)))
    respec.append("else " + app("SkyyTrFoot", SUI.button("SkyyTrRespec", "Respec", "secondary", w=TR_RESPEC_OFF_W, disabled=True,
                                                          anchor={"left": SUI.right_margin(W - TR_BACK_W, TR_RESPEC_OFF_W)})))
    parts = {
        "SHELL": sh.java("b"),
        "HEAD": app(body, SUI.group("SkyyTrHead", "Left", h=TR_HEAD_H, anchor={"bottom": TR_TAB_GAP})) + "\n" +
                app(body, SUI.group("SkyyTrHead2", "Left", h=TR_HEAD_H, anchor={"bottom": TR_HEAD_GAP})),
        "TAB": "\n".join(tab_java), "INFO": "\n".join(info), "GRID": "\n".join(grid), "NOCLASS": noclass, "STRIP": "\n".join(strip),
        "CROW": crow, "SLOT": slot, "ROWA": rowa, "CELL": cells, "HBAR": "\n".join(hbar), "VBAR": "\n".join(vbar), "JUNC": "\n".join(junc),
        "GAPR": "\n".join(gapr), "ROWB": "\n".join(rowb), "APANEL": "\n".join(apanel), "APNO": apno, "APHINT": aphint, "ACARD": acard,
        "FOCUS": "\n".join(focus), "FTILE": ftile, "FMAX": "\n".join(fmax),
        "DETP": detp, "DET": "\n".join(det), "BUY": "\n".join(buy), "LAT": "\n".join(lat), "LROW": "\n".join(lrow), "LMOD": lmod,
        "LELEM": "\n".join(lelem), "LTAIL": "\n".join(ltail), "FOOT": "\n".join(foot), "RESPEC": "\n".join(respec),
    }
    sh.appends.check(TR_PREFIX)
    SUI.assert_proven(marks, what="TreePage class tab")
    indent = {"SHELL": 2, "HEAD": 2, "TAB": 4, "INFO": 2, "GRID": 2, "NOCLASS": 4, "STRIP": 4, "CROW": 6, "SLOT": 8, "ROWA": 8, "CELL": 10,
              "HBAR": 10, "VBAR": 10, "JUNC": 10, "GAPR": 8, "ROWB": 8, "APANEL": 2, "APNO": 4, "APHINT": 4, "ACARD": 6, "FOCUS": 4,
              "FTILE": 6, "FMAX": 6, "DETP": 2, "DET": 4, "BUY": 4, "LAT": 4, "LROW": 6, "LMOD": 8, "LELEM": 8, "LTAIL": 4, "FOOT": 2, "RESPEC": 2}
    java = TRC_BUILD
    for name, part in parts.items():
        tok = "{{" + name + "}}"
        assert java.count(tok) == 1, "unused / doubled Java part " + name
        java = java.replace(tok, "\n".join((" " * indent[name] + ln) if ln.strip() else ln for ln in part.split("\n")))
    assert not re.findall(r"\{\{[A-Z]+\}\}", java), "unfilled Java placeholder"
    for ident in TRC_NEW_IDS[:-1]:
        base_ = re.sub(r"\d+$", "", ident)
        assert ("#%s {" % ident) in java or ('#%s" + (' % base_) in java or ('#%s" + ' % re.sub(r"\d+(Ic|Sb|N|K|U|S|T|C|A)?$", "", ident)) in java, \
            "the class page does not create #" + ident
    return java, marks
'''
block('''# ---- 0.3 part 2: the class tab (TreePage.buildClass): the same window, tab rows, info row and detail well as the template trees; the''',
      '''    for ident in TRC_NEW_IDS[:-1]:
        assert ("#%s {" % ident) in java or ('#%s" + (' % re.sub(r"\\d+$", "", ident)) in java or ('#%s" + ' % re.sub(r"\\d+(Ic|Sb)?$", "", ident)) in java, \\
            "the class page does not create #" + ident
    return java, marks
''', PAGE_NEW)

rep('''    w_ = {1: "Passive - pick one of two", 2: "Ability line", 3: "Modifier slot", 4: "Modifier slot", 5: "Trunk", 9: "Switch"}.get(r_, "Passive")
    if r_ == 6: w_ = pn_ + " " + nid_[2:] + "/5"
    if r_ == 7: w_ = "Element - " + pn_ + " path"
    return w_ + " - %d AP" % CT[n_][1] + (" - continues on page 2" if nid_ == "P3" else (" - continues on page 1" if nid_ == "P4" else ""))''',
    '''    w_ = {1: "Passive - pick one of two", 2: "Ability", 5: "Trunk", 9: "Switch"}.get(r_, "Passive")
    if r_ == 3: w_ = "Modifier"   # 0.3.13
    if r_ == 6: w_ = pn_ + " " + nid_[2:] + "/5"
    if r_ == 7: w_ = "Element - " + pn_ + " path"
    return w_ + " - %d AP" % CT[n_][1] + (" - continues on page 2" if nid_ == "P3" else (" - continues on page 1" if nid_ == "P4" else ""))''')

# ================================================================================================================ TreePage: fields, helpers, events
rep('''F(page, "public int apend;")''', '''F(page, "public int apend;")
F(page, "public String afoc;")   # 0.3.13: the FOCUSED ability (SkyyClasses ability id; amode = the focus view + the Lattice are on)
F(page, "public int hk;")        # 0.3.13: what is HELD: 0 nothing, 1 the focused ability, 2 the modifier hmod of it
F(page, "public String hmod;")''')
rep('''  this.mslot = 0;
  this.apend = -1;
}""")''', '''  this.mslot = 0;
  this.apend = -1;
  this.afoc = "";
  this.hk = 0;
  this.hmod = "";
}""")''')
rep('''M(page, TR_INFO_COLOR)
M(page, TR_CBUILD_JAVA)   # 0.3 part 2: the class tab (build() calls it)''', '''# 0.3.13: a class node's icon - an ability node shows its rune icon once SkyyClasses has loaded the rune (aic: per ability node, from the panel)
M(page, r"""
public static String cicon(int ci, int n, String[] aic) {
  if (aic != null && n >= 0 && n < @PKG@.TreeClass.NN && @PKG@.TreeClass.NROLE[n] == 2) {
    for (int a = 0; a < @PKG@.TreeClass.ABLI.length && a < aic.length; a++) if (@PKG@.TreeClass.ABLI[a] == n && aic[a] != null && aic[a].length() > 0) return aic[a];
  }
  return @PKG@.TreeClass.icon(ci, n);
}""")
M(page, TR_INFO_COLOR)
M(page, TR_CBUILD_JAVA)   # 0.3 part 2: the class tab (build() calls it)''')
rep('''M(cls, r"""
public static boolean usable(Object[] ap, int i) {''', '''M(cls, r"""
public static String modNm(String id) {
  if (id == null) return "";
  for (int i = 0; i < MODID.length; i++) if (MODID[i].equalsIgnoreCase(id)) return MODNM[i];
  return id;
}""")
M(cls, r"""
public static boolean usable(Object[] ap, int i) {''')
block('''M(page, r"""
public String abilEv(java.util.UUID u, @PKG@.TreeData d, int ci, int lvl, String act, int i, int k) {''', '''  return "";
}""")
M(page, TR_BUILD_JAVA)''', '''# 0.3.13 THE FOCUS + LATTICE CLICKS (spec 6.2 / 6.3). act: focus <row>, back, holdab, tile <modifier index>, slot <row>, mslot <row x 4 +
# slot>, maxup, attune. Held state lives on the page (hk / hmod); every change goes through SkyyClasses (it re-checks combat, ownership,
# the doubling rules). The probe page may look and hold, never change.
M(page, r"""
public String abilEv(java.util.UUID u, @PKG@.TreeData d, int ci, int lvl, String act, int i) {
  if (ci < 0) return "Choose a class first";
  boolean[] it = @PKG@.TreeClass.intact(d, ci);
  String csv = this.probe ? @PKG@.TreeClass.abilCsv(u) : @PKG@.TreeClass.csvOf(d, it, ci);
  Object[] ap = @PKG@.TreeClass.apanel(u, csv);
  if (ap == null || ap.length < 129 || !"ok".equals(ap[0])) { this.amode = false; this.hk = 0; return @PKG@.TreeClass.apanelMsg(ap, ci, null); }
  String off = "Ability: loadout changes are off in the probe (probe - not saved)";
  if (act.equals("back")) {
    this.amode = false; this.hk = 0; this.hmod = "";
    return this.probe ? "" : said(@PKG@.TreeClass.ado(u, "back", "", "", csv));
  }
  if (act.equals("focus")) {
    if (!@PKG@.TreeClass.usable(ap, i)) return "Ability: that ability is not unlocked yet - buy it in the tree";
    String id = String.valueOf(ap[12 + i * 16]);
    this.amode = true; this.afoc = id; this.hk = 1; this.hmod = "";
    return said(@PKG@.TreeClass.ado(u, "hold", id, "", csv));
  }
  int fr = @PKG@.TreeClass.rowOf(ap, this.afoc);
  if (!this.amode || fr < 0 || !@PKG@.TreeClass.usable(ap, fr)) { this.amode = false; this.hk = 0; return "Ability: click an ability under Abilities first"; }
  String fid = this.afoc;
  String fnm = String.valueOf(ap[12 + fr * 16 + 1]);
  if (act.equals("holdab")) {
    if (this.hk == 1) { this.hk = 0; return "Ability: nothing held"; }
    this.hk = 1; this.hmod = "";
    return said(@PKG@.TreeClass.ado(u, "hold", fid, "", csv));
  }
  if (act.equals("tile")) {
    String[] rows = @PKG@.TreeClass.amods(u, fid, csv);
    if (rows == null || i + 1 >= rows.length) return "Ability: that modifier is gone - try again";
    String[] f = rows[i + 1].split("\\\\|", -1);
    if (f.length < 4) return "Ability: that modifier is gone - try again";
    if (!"1".equals(f[3])) {
      String lid = String.valueOf(ap[116 + fr]);
      int n = @PKG@.TreeClass.nodeIdx(ci, lid + "." + f[0]);
      if (n >= 0) { this.csel = n; this.cpage = @PKG@.TreeClass.NPAGE[n]; this.amode = false; this.hk = 0; this.hmod = ""; }   // fix round (critic C8): the node detail + Unlock show at once
      return "Ability: " + f[1] + " is not unlocked - its node " + lid + "." + f[0] + " is selected in the tree: Unlock it on the right (" + @PKG@.TreeCfg.AP_MOD + " AP)";
    }
    if (this.hk == 2 && f[0].equals(this.hmod)) { this.hk = 0; this.hmod = ""; return "Ability: nothing held"; }
    this.hk = 2; this.hmod = f[0];
    return said(@PKG@.TreeClass.ado(u, "hold", fid, f[0], csv));
  }
  if (act.equals("slot")) {
    if (i < 0 || i > 3) return "";
    if (this.hk == 1) {
      if (this.probe) return off;
      String r = said(@PKG@.TreeClass.ado(u, "place", fid, String.valueOf(i), csv));
      if (r.startsWith("Done: ")) this.hk = 0;
      return r;
    }
    if (@PKG@.TreeClass.usable(ap, i)) {
      String id = String.valueOf(ap[12 + i * 16]);
      this.afoc = id; this.hk = 1; this.hmod = "";
      return said(@PKG@.TreeClass.ado(u, "hold", id, "", csv));
    }
    return "Ability: that key is empty - click an ability first, then this slot";
  }
  if (act.equals("mslot")) {
    int r = i / 4;
    int j = i % 4;
    if (r < 0 || r > 3) return "";
    String rid = String.valueOf(ap[12 + r * 16]);
    if (this.hk == 2) {
      if (!rid.equals(fid) || !@PKG@.TreeClass.usable(ap, r)) return "Ability: " + @PKG@.TreeClass.modNm(this.hmod) + " goes in " + fnm + "'s own row (" + @PKG@.TreeClass.keyShort(fr) + ")";
      if (this.probe) return off;
      String rr = said(@PKG@.TreeClass.ado(u, "mod", fid, j + ":" + this.hmod, csv));
      if (rr.startsWith("Done: ")) { this.hk = 0; this.hmod = ""; }
      return rr;
    }
    if (!@PKG@.TreeClass.usable(ap, r)) return "Ability: that key is empty";
    if (@PKG@.TreeClass.modName(ap, r, j).length() == 0) return "Ability: click a modifier tile first (under " + fnm + "), then an empty slot of its row";
    if (this.probe) return off;
    return said(@PKG@.TreeClass.ado(u, "clearMod", rid, String.valueOf(j), csv));
  }
  if (act.equals("maxup")) {
    if (this.hk != 2) return "Ability: hold a modifier first (click its tile), then Max Up";
    if (this.probe) return off;
    return said(@PKG@.TreeClass.ado(u, "rbpick", fid, this.hmod, csv));
  }
  if (act.equals("attune")) {
    if (this.probe) return off;
    return said(@PKG@.TreeClass.ado(u, "attune", "next", "1", csv));
  }
  return "";
}""")
M(page, TR_BUILD_JAVA)''')
rep('''      for (int n = 1; n <= @PKG@.TreeClass.NN; n++) {
        if (data.indexOf("trc" + n + "\\"") >= 0) { this.csel = n - 1; this.cpage = @PKG@.TreeClass.NPAGE[n - 1]; this.msg = ""; this.amode = false; rebuild(); return; }
      }
      // 0.3.7: the ability panel (cards 0-3: icon = details, the two modifier slots, Swap, the action button) and the ability detail
      if (data.indexOf("trtree\\"") >= 0) { this.amode = false; this.msg = ""; rebuild(); return; }
      if (data.indexOf("trmnx\\"") >= 0) { this.mslot = (this.mslot + 1) % 4; this.msg = ""; rebuild(); return; }   // 0.3.10: Next slot (1 - 4)
      if (data.indexOf("trmat\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "attune", this.aslot, this.mslot); rebuild(); return; }   // 0.3.10: the Imbue element
      if (data.indexOf("trmu\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "unequip", this.aslot, 0); rebuild(); return; }
      for (int ai = 0; ai < 4; ai++) {
        if (data.indexOf("trab" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trmsa" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.mslot = 0; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trmsb" + ai + "\\"") >= 0) { this.amode = true; this.aslot = ai; this.mslot = 1; this.msg = ""; rebuild(); return; }
        if (data.indexOf("trsw" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "swap", ai, 0); rebuild(); return; }
        if (data.indexOf("tren" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "act", ai, 0); rebuild(); return; }
      }
      for (int mk = 0; mk < 5; mk++) {
        if (data.indexOf("trme" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "equip", this.aslot, mk); rebuild(); return; }
        if (data.indexOf("trmx" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "rbpick", this.aslot, mk); rebuild(); return; }   // 0.3.8
      }''', '''      for (int n = 1; n <= @PKG@.TreeClass.NN; n++) {
        if (data.indexOf("trc" + n + "\\"") >= 0) { this.csel = n - 1; this.cpage = @PKG@.TreeClass.NPAGE[n - 1]; this.msg = ""; this.amode = false; this.hk = 0; rebuild(); return; }
      }
      // 0.3.13: the middle well (the owned abilities, the focus view) and the Lattice (spec 6.2 / 6.3)
      if (data.indexOf("tyfb\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "back", 0); rebuild(); return; }
      if (data.indexOf("tyfc\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "holdab", 0); rebuild(); return; }
      if (data.indexOf("tymx\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "maxup", 0); rebuild(); return; }
      if (data.indexOf("tymat\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "attune", 0); rebuild(); return; }
      for (int ai = 0; ai < 4; ai++) {
        if (data.indexOf("tyca" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "focus", ai); rebuild(); return; }
        if (data.indexOf("tyla" + ai + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "slot", ai); rebuild(); return; }
      }
      for (int mq = 0; mq < 16; mq++) {
        if (data.indexOf("tylm" + mq + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "mslot", mq); rebuild(); return; }
      }
      for (int mk = 0; mk < 5; mk++) {
        if (data.indexOf("tyft" + mk + "\\"") >= 0) { this.msg = abilEv(u, cd, cci, clv, "tile", mk); rebuild(); return; }
      }''')

# ================================================================================================================ TreeTick, plugin, kit, write
rep('''    @PKG@.TreeData d = @PKG@.TreeStore.data(u);
    if (d.name == null) @PKG@.TreeStore.setName(d, pr.getUsername());''', '''    @PKG@.TreeData d = @PKG@.TreeStore.data(u);
    if (d.name == null) @PKG@.TreeStore.setName(d, pr.getUsername());
    @PKG@.TreeClass.maint(pr, u, d);   // 0.3.13: the profile update (when SkyyClasses answers), the free Root, the AP check''')
rep('''  b.put("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7: SkyyClasses 0.1.22 - the intact class nodes (its ability gate)''',
    '''  b.put("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7: SkyyClasses 0.1.22 - the intact class nodes (its ability gate)
  @PKG@.TreeStore.MFN = new @PKG@.TreeModFn();
  b.put("tree:fn:modOwned", @PKG@.TreeStore.MFN);   // 0.3.13: { UUID, ability, modifier } -> Boolean (the modifier node is intact)''')
rep('''    if (@PKG@.TreeStore.AFN != null) b.remove("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7''',
    '''    if (@PKG@.TreeStore.AFN != null) b.remove("tree:fn:abil", @PKG@.TreeStore.AFN);   // 0.3.7
    if (@PKG@.TreeStore.MFN != null) b.remove("tree:fn:modOwned", @PKG@.TreeStore.MFN);   // 0.3.13''')
rep('''    ("class.debug.extraAp", "Test: extra AP", "classes", "int", "0", "0", "1000", "", "", "live,danger,adv",
     "Testing only: extra Ability Points for every player. Keep 0 on a real server.", "reload"),''', '''    ("class.debug.extraAp", "Test: extra AP", "classes", "int", "0", "0", "1000", "", "", "live,danger,adv",
     "Testing only: extra Ability Points for every player. Keep 0 on a real server.", "reload"),
    # 0.3.13 (research/Ability-Tree-Redesign-Spec.md 4.1 + Q2)
    ("class.ap.ability", "AP per ability node", "classes", "int", "1", "0", "10", "", "", "live,danger",
     "AP one ability node (A1-A4b) costs; it unlocks the ability. More AP: owners can go over budget.", "reload"),   # fix round 2 (critic)
    ("class.ap.modifier", "AP per modifier node", "classes", "int", "1", "0", "10", "", "", "live,danger",
     "AP one modifier node costs; it unlocks that modifier at once. More AP: owners can go over budget.", "reload"),
    ("class.ap.spine", "AP per spine node", "classes", "int", "0", "0", "10", "", "", "live,danger",
     "AP of the stat links P1-P4, X1, X2 (0 = free links, the default). The Root is always free.", "reload"),''')
rep('''      "Entry = node id (ROOT, P1, PA1 ...). On, number, AP cost (A / M nodes are free). Removed = built-in.",''',
    '''      "Entry = node id (P1, T1, A1 ...). On, number, AP (spine + A1-A4b: own rows). M1A-M4B: not read.",''')
rep('''EXTRA_EXACT_ROWS, EXTRA_TABLE_ROWS = 7, 1 + NC   # 0.3 part 2: class.enabled .. class.debug.extraAp; class.minLevel + one class.nodes.<Class> each''',
    '''EXTRA_EXACT_ROWS, EXTRA_TABLE_ROWS = 10, 1 + NC   # 0.3 part 2: class.enabled .. class.debug.extraAp (0.3.13: + class.ap.ability / modifier / spine); class.minLevel + one class.nodes.<Class> each''')
rep('''assert len(_exact) == 24 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 25 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 50''',
    '''assert len(_exact) == 24 + EXTRA_EXACT_ROWS and len(CFG_ROWS) == 25 + len(TREES) + EXTRA_EXACT_ROWS + EXTRA_TABLE_ROWS and len(CFG_ROWS) == 53   # 0.3.13: + 3 AP rows''')
rep('''assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 50''',
    '''assert [r[0] for r in CFG_ROWS].count("class.enabled") == 1 and len(set(r[0] for r in CFG_ROWS)) == 53''')
rep('''    if (@PKG@.TreeClass.retIdx(e) >= 0) return "?" + e + " was a 0.3.2 lane node - the class paths replaced it (0.3.3), this line does nothing. Save it anyway?";
    return "?" + e + " is not a class node (ROOT P1 P2 X1 X2 P3 P4, A1-A4, M1A-M4B, T1-T6, PA1-PA5, PB1-PB5, PC1-PC5, LE CE RE, TS) - this line would do nothing. Save it anyway?";
  }''', '''    if (@PKG@.TreeClass.retIdx(e) >= 0) return "?" + e + " was a 0.3.2 lane node - the class paths replaced it (0.3.3), this line does nothing. Save it anyway?";
    if (e.equalsIgnoreCase("A4")) return "?A4 is the 0.3.12 id of the A4 alt pair - since 0.3.13 only its on / off is read (false switches off both A4a and A4b; the AP is the AP per ability node row). Save it anyway?";   // fix round
    if (@PKG@.TreeClass.oldAbilId(e)) return "?" + e + " was an ability slot node - since 0.3.13 the 2 modifier slots come with the ability node, so this line does nothing. Save it anyway?";
    return "?" + e + " is not a class node (ROOT P1 P2 X1 X2 P3 P4, T1-T6, PA1-PA5, PB1-PB5, PC1-PC5, LE CE RE, TS) - this line would do nothing. Save it anyway?";
  }
  if (@PKG@.TreeClass.NROLE[n] == 2) return "?" + e + " is an ability node - only its on / off is read (false = nobody can buy or use the ability); its AP is the AP per ability node row. Save it anyway?";   // fix round (critic A3)
  if (@PKG@.TreeClass.NROLE[n] == 3) return "?" + e + " is a modifier node - its cost is the AP per modifier node row and it has no line, so this line does nothing. Save it anyway?";   // 0.3.13''')
rep('''  if (ap != 0L && @PKG@.TreeClass.NROLE[n] >= 2 && @PKG@.TreeClass.NROLE[n] <= 4) return "?" + e + " is an ability / modifier slot node - those are always free, so this AP (" + ap + ") is ignored. Save it anyway?";   // 0.3.7''',
    '''  if (@PKG@.TreeClass.NROLE[n] <= 1 && n != 0 && ap != (long) @PKG@.TreeCfg.AP_SPINE) return "?" + e + " is a spine node - since 0.3.13 its cost is the AP per spine node row (" + @PKG@.TreeCfg.AP_SPINE + "), so this AP (" + ap + ") is not read. Save it anyway?";''')
rep('''  int n = @PKG@.TreeClass.nodeIdx(id);
  if (n < 0 || !@PKG@.TreeClass.NID[n].equals(id)) return "?" + id + " is not a class node id (capitals matter; the ids are in trees.properties) - this line would do nothing. Save it anyway?";''',
    '''  int n = @PKG@.TreeClass.nodeIdx(id);
  if (n < 0 || !@PKG@.TreeClass.NID[n].equals(id)) return "?" + id + " is not a class node id (capitals matter; the ids are in trees.properties) - this line would do nothing. Save it anyway?";
  if (@PKG@.TreeClass.NROLE[n] == 3) return "?" + id + " is a modifier node - it needs only its ability node, no class level. Save it anyway?";   // 0.3.13''')
rep('''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, rpt, rpl, dmg, tick, svr, ops, cops, page, kitc, mig, mig32, mig33, vcmd, qcmd, rcmd, scmd, pcmd, cmd, trb, pl)   # 0.3.8: + TreeRb''',
    '''ALL = (defs, cfg, dat, sto, stk, calc, cls, fx, swg, msg, abil, gat, tfn, afn, bfn, ffn, rpt, rpl, dmg, tick, svr, ops, cops, page, kitc, mig, mig32, mig33, vcmd, qcmd, rcmd, scmd, pcmd, cmd, trb, pl,
       amig, mfn)   # 0.3.8: + TreeRb; 0.3.13: + TreeAbMig, TreeModFn''')
rep('''print("0.3.12 downward layout: class graph %d rows x 9 (slot %dx%d, cell %dx%d), %d junctions; tree link rows %s; icon hook %d entries" % (
    CROWS, TRC_SLOT_W, TRC_SLOT_H, TRC_CELL_W, TRC_CELL_H, len(JUNCTION), TR_LINK_GEOM, len(NODE_ICON_ART)))''',
    '''print("0.3.12 downward layout: class graph %d rows x 9 (slot %dx%d, cell %dx%d), %d junctions; tree link rows %s; icon hook %d entries" % (
    CROWS, TRC_SLOT_W, TRC_SLOT_H, TRC_CELL_W, TRC_CELL_H, len(JUNCTION), TR_LINK_GEOM, len(NODE_ICON_ART)))
print("0.3.13 ability tree: %d nodes per class (%d hidden slots in all), AP of a full build %s; SkyyClasses table %s" % (NN, len(_HIDM), AP_BUDGET, CLS_CHECK))''')

# ================================================================================================================ checks on the result
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "no system / command added"
assert "# @@" not in s and "abil.tree2" in s and "tree:fn:modOwned" in s
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.12 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8") if NL != LF else s.encode("utf8"))
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.12 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
