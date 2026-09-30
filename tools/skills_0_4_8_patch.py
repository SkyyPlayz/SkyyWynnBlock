"""Derive SkyySkills/build_skyyskills_0.4.8.py from the LIVE generated SkyySkills/build_skyyskills_0.4.7.py (= the tools/deploy_set.py SET
pin; 0.4.7 came from 0.4.6 by tools/skills_0_4_7_patch.py, 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run skills_0_4_5
or older patches). Same style as skills_0_4_7_patch.py: rep(old, new) / cut(a, b, new) with asserted single anchors, newline-agnostic;
0.4.7 stays untouched and its line endings are kept. Edit THIS file, never the generated script.
Run:  python tools/skills_0_4_8_patch.py   then   python SkyySkills/build_skyyskills_0.4.8.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.8.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.4.8 = MAGIC THAT WORKS AT LEVEL 1 (Skyy 2026-09-30, found in game: vanilla casters cost Mana per charged cast - wands 25, staffs 50,
spellbooks 100, Halloween_Broomstick 50, the blunderbusses 50 - while 0.4.7 gave everyone 10 and Mage / Priest 20, so a new caster could
not cast at all). Skyy's words: "make priest start at like 30 mana. (they need at least enough mana to use the starter weapon.)",
"lets also take your recommendation 1" (every spell's Mana cost / 5) and "so at level 1 when you start, you can get a few shots off
with your magic".
  1. SPELL COSTS / 5. At BUILD time every vanilla Server/Item/Items/**/*.json of Assets.zip (read in memory, read-only) whose
     InteractionVars carry a Mana cost gets an override in this jar's asset pack (same path + id as vanilla, so it replaces the vanilla
     item - the SkyyTrees Pickaxe_Attack / Hatchet_Attack pattern) that differs from vanilla ONLY in the Mana numbers: the StatsCondition
     Costs.Mana (the cast check) and the ChangeStat StatModifiers.Mana (the drain) of that item's var set, each divided by SPELL_DIVISOR
     (5) and rounded half up to a whole number >= 1; 0 stays 0. Nothing from Assets.zip is ever checked into git: the JSON is generated
     into the jar at every build (tools/AGENT-BRIEF.md). Self-checks stop the build: every entry has the one known shape (InteractionVars
     /<var>/Interactions/[one {Parent: <known cast check | drain interaction>, Costs|StatModifiers: {Mana: whole number}}]), a changed item
     has exactly one check and one drain, the generated JSON equals vanilla except those numbers (diffed path by path, and with the old
     numbers put back it IS vanilla), no Mana cost outside InteractionVars, item Parent inheritance (an item that inherits its
     InteractionVars keeps its own file and picks the new cost up from the overridden parent; an item with its own InteractionVars under a
     Mana parent is refused - whether the engine merges the two is not known), every item whose interactions reach a Mana cost defines it
     in its own InteractionVars (no vanilla default cost is left behind), no other Skyy mod of the live set and no pack mod ships one of
     these files or ids. The build prints every item with its old and new cost. Items whose Mana numbers are all 0 (Crystal_Red, the
     Crystal_Ice drain) are NOT overridden. The divisor is a build-time constant (the assets are static): Server Setup shows it READ-ONLY
     (Skills > Overall and Mana > "Spell Mana costs divided by", a custom ro row; export / import / restore skip it).
  2. BASE MANA BY CLASS: the config kit table mana.classBase (Skills > Overall and Mana > "Base Mana by class"; file lines
     mana.classBase.<Class>=<Mana>; default Mage 30, Priest 30) replaces mana.magicBase + mana.magicClasses; a class not in the table
     starts at mana.base (10). ONE-TIME MIGRATION at start (ManaMig.run, before SkillCfg.load and the kit): only a file that still has a
     live mana.magicBase or mana.magicClasses line and no mana.classBase.* line. The UNTOUCHED 0.4.7 default pair (base 20, classes Mage +
     Priest in any order / case) becomes the default table (Mage 30, Priest 30); any other pair is an admin's choice and is KEPT (each
     listed class gets that base, e.g. mana.magicBase=25 + Mage -> Mage 25) with one INFO line. Only those lines change: the first one is
     replaced by a comment + the table lines, the other removed; the 0.4.6 / 0.4.7 default comment about the old keys (3 lines), while
     it is still exactly that text, becomes the 0.4.8 default comment, and any other comment that still names the old keys stays and
     gets a one-line note under the new comment (review 2026-09-30 finding 2); every other byte (comments, order, CRLF / LF, ISO-8859-1 text) stays;
     checked by parsing before and after (same keys and values except the move) and written atomically with the config kit's own
     CfgRows.atomicWrite (tmp + fsync + ATOMIC_MOVE); once the kit has started, the file as it was before the move becomes one entry of the
     kit's own history (ManaMig.keepCopy: config-history/, Server Setup > Skills > History can preview / restore it). A continued line, an
     unreadable file or a failed write changes nothing: the old pair is then read as the table (WARN) and the next start tries again.
     After the move the old lines are gone, so a second start does nothing.
  3. GUARD (ManaGuard, on the 1 s SkillTick from 10 s after start, again after every config load and after SkyyClasses' config epoch
     changes): WARN once per class (again only when its numbers change) whose base Mana is below the Mana cost of a weapon in its class
     kit - the kit from SkyyClasses through the bridge (config:fn:SkyyClasses apply({"get", "kit.<Class>"}), the kit row SkyyClasses
     publishes), else the built-in table (SkyyClasses' own defaults, cross-checked at build time against its SET-pinned script). With
     SkyyClasses' Class kits switched off (kits.enabled=false through the same get op) there is no kit weapon: no WARN, one INFO. One
     INFO summary line with the casts from full Mana. It never changes a number. PACK CHECK (review 2026-09-30 finding 3, same tick,
     once, retried every 10 s up to 6 times while the item assets cannot be read): which asset pack the game's item assets take each
     overridden item from (Item.getAssetMap().getAssetPack - the pack loaded last wins a clash): one INFO when every one is this jar's
     pack (Skyy:<version> SkyySkills), else one WARN naming the items another pack wins.
  4. Max Mana stays on the existing Perks.tick path (world thread, StaticModifier MAX ADDITIVE under skyyskill_basemana, computed from
     scratch every second); the current Mana value is never written: the engine only clamps it to the new max (EntityStatValue.
     computeModifiers), so a switch to a class with more Mana never refills it, and the 0.4.6 session-start hold keeps a relog from
     dipping it.
Everything else (commands, pages, bridge keys, players files, the other rows) is 0.4.7's - asserted below and by the harness (class
bytes 0.4.7 vs 0.4.8).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.7.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.8.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.7"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
# the source must be the generated 0.4.7 of the EDITED lineage
assert 'VERSION = "0.4.7"' in s and "derived from the generated 0.4.6 by tools/skills_0_4_7_patch.py" in s, "not the live generated 0.4.7"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical: the three pages and their look block, the commands, the XP / perk code
KEEP = [block("# ================= /skills page (inline", "# ================= OverallPage (0.4.6)"),
        block("# ================= BridgeCfg (0.4)", "# ================= Overall (0.4.6)"),
        block('# a copy of StatsPage.num (StatsPage is compiled later)', "public static boolean magic(java.util.UUID u) {{"),
        block("# ms since this session's first Perks.ovl", "public static String magicText() {{"),
        block("perk.addMethod(CtNewMethod.make(f\"\"\"\npublic static void mod(", "# drops that depend on the held tool"),
        block("# ================= OverallPage (0.4.6)", "# 0.4.6 (research/Overall-Level-Spec.md 4.9): the \"Overall and Mana\" category")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.7 - build script (derived from the generated 0.4.6 by tools/skills_0_4_7_patch.py - edit the patch, not this file;
0.4.6 was derived''', '''"""SkyySkills 0.4.8 - build script (derived from the generated 0.4.7 by tools/skills_0_4_8_patch.py - edit the patch, not this file;
0.4.7 was derived from the generated 0.4.6 by tools/skills_0_4_7_patch.py; 0.4.6 was derived''')
HEAD_048 = '''0.4.8: MAGIC THAT WORKS AT LEVEL 1 (Skyy 2026-09-30; full notes in tools/skills_0_4_8_patch.py). Found in game: vanilla casters cost Mana
  per charged cast (wands 25, staffs 50, spellbooks 100, Halloween_Broomstick 50, blunderbusses 50) while 0.4.7 gave 10 (Mage / Priest 20).
  Skyy: "make priest start at like 30 mana. (they need at least enough mana to use the starter weapon.)" + "lets also take your
  recommendation 1" (spell costs / 5) + "so at level 1 when you start, you can get a few shots off with your magic".
  SPELL COSTS / 5: this jar is now an asset pack (IncludesAssetPack true) carrying GENERATED overrides of the vanilla items whose
    InteractionVars cost Mana (read from Assets.zip in memory at every build, never checked into git): only the cast check Costs.Mana and
    the drain StatModifiers.Mana change (/ SPELL_DIVISOR 5, rounded half up, at least 1, 0 stays 0): wand 25 -> 5, staff 50 -> 10,
    spellbook 100 -> 20, broomstick / blunderbuss 50 -> 10 (the plain blunderbuss drains 0 in vanilla and still does). Self-checked
    (SPELL GEN block): the one known var shape, JSON = vanilla except those numbers, item Parent rules, no vanilla default cost reachable
    without the item's own override, no clash with another Skyy mod of the live set or a pack mod. Items with only 0 costs are left alone.
    The divisor is fixed in the jar: Server Setup shows it read-only ("Spell Mana costs divided by"). Known limit: an override is a full
    copy of the item, so after a Hytale update that changes one of these items, rebuild SkyySkills (the build re-derives them).
  BASE MANA BY CLASS: config table mana.classBase (Server Setup > Skills > Overall and Mana > "Base Mana by class"; default Mage 30,
    Priest 30) replaces mana.magicBase + mana.magicClasses; other classes (and no class) start at mana.base 10. ManaMig.run (setup, before
    the file is read): the untouched 0.4.7 pair (20 + Mage,Priest) becomes the default table, an admin's pair is kept as the table (INFO);
    only those lines change (plus the untouched 0.4.7 comment about them, which becomes the 0.4.8 one; another comment naming the old
    keys gets a note), byte-safe, atomic (the kit's CfgRows.atomicWrite), once (the old lines are gone afterwards); the file as it
    was goes into the kit's History (restorable in Server Setup). If the move cannot run, the old pair is read as the table (WARN) and
    the next start retries.
  GUARD: ManaGuard WARNs once per class whose base Mana is below its kit weapon's (new) Mana cost (kit from SkyyClasses via config:fn:
    SkyyClasses, else the built-in table; nothing to check while SkyyClasses' Class kits are off) + one INFO summary with the casts from
    full Mana; it never changes a number. Pack check: one INFO when the game's item assets take every override from this jar's pack,
    else one WARN naming the items another pack wins (the pack loaded last wins a clash).
  Max Mana: the same Perks.tick modifier as 0.4.6 (world thread); current Mana is never written (no refill on a switch, the session hold
    keeps a relog from dipping it).
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.7: THE VANILLA LOOK''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_048 + '''0.4.7: THE VANILLA LOOK''')
rep('VERSION = "0.4.7"\n', 'VERSION = "0.4.8"\n')

# ---------------------------------------------------------------------------------------------------------------- default file text
# (a fresh file and the block appended to a pre-0.4.6 file; an existing 0.4.6 / 0.4.7 file is moved by ManaMig)
CLASS_BASE_DEF = [("Mage", 30), ("Priest", 30)]
# the 0.4.6 / 0.4.7 default comment above the old pair (in every file those versions wrote or appended): ManaMig replaces it, when it is
# still exactly this text, with the 0.4.8 comment (MANA_DOC_NEW below = the 4 new default comment lines) - review 2026-09-30 finding 2
OLD_DOC = ["# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase",
           "# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after",
           "# 6 s without taking damage)."]
assert s.count("".join('OVL_L.append("%s")\n' % _l for _l in OLD_DOC)) == 1, "the 0.4.7 default Base Mana comment changed"
assert not any('"' in _l or "\\" in _l for _l in OLD_DOC)
rep('''OVL_L.append("# Base Mana: every player's max Mana starts at mana.base; players whose class is listed in mana.magicClasses start at mana.magicBase")
OVL_L.append("# instead (their base is that number, not mana.base plus it). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after")
OVL_L.append("# 6 s without taking damage).")
OVL_L.append("mana.base.enabled=true")
OVL_L.append("mana.base=10")
OVL_L.append("mana.magicBase=20")
OVL_L.append("mana.magicClasses=Mage,Priest")
''', '''OVL_L.append("# Base Mana: every player's max Mana starts at mana.base. A class listed below (Base Mana by class, one line per class:")
OVL_L.append("# mana.classBase.<Class>=<Mana>) starts at its own number instead - that number IS its base, not mana.base plus it (SkyySkills")
OVL_L.append("# 0.4.8, replaced mana.magicBase / mana.magicClasses). Vanilla max Mana is 0; Mana refills by itself (+1 every 0.2 s after 6 s")
OVL_L.append("# without taking damage). Spells cost the vanilla Mana / %d (wand 5, staff 10, spellbook 20 - fixed in the jar)." % SPELL_DIVISOR)
OVL_L.append("mana.base.enabled=true")
OVL_L.append("mana.base=10")
CLASS_BASE_DEF = @CBD@   # 0.4.8 (Skyy 2026-09-30): enough Mana for the starter weapons (Mage staff 10 a cast, Priest wand 5)
for _cb, _cv in CLASS_BASE_DEF:
    OVL_L.append("mana.classBase.%s=%d" % (_cb, _cv))
'''.replace("@CBD@", repr(CLASS_BASE_DEF)))
# SPELL_DIVISOR is used by the default text above: define it before the defaults are built (the SPELL GEN block below re-asserts it)
rep('''# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
ASSETS = ''', '''# 0.4.8 (Skyy 2026-09-30): every vanilla spell's Mana cost / SPELL_DIVISOR (the SPELL GEN block builds the item overrides)
SPELL_DIVISOR = 5
# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
ASSETS = ''')

# ---------------------------------------------------------------------------------------------------------------- SPELL GEN (build time)
SPELL_GEN = r'''# ================= 0.4.8 SPELL COSTS / SPELL_DIVISOR (Skyy 2026-09-30; tools/skills_0_4_8_patch.py point 1) =================
# Found in game 2026-09-30: vanilla casters cost Mana per charged cast through their InteractionVars - a StatsCondition "Costs": {"Mana": N}
# (the cast check) and a ChangeStat "StatModifiers": {"Mana": -N} (the drain): wands 25, staffs 50 (Crystal_Red 0), spellbooks 100,
# Halloween_Broomstick 50, blunderbusses 50 (the plain one drains 0). This block GENERATES, from Assets.zip read in memory (read-only), an
# override of each such item for this jar's asset pack (same path = same id, it replaces the vanilla item for server and client) whose ONLY
# difference is those Mana numbers / SPELL_DIVISOR. No game file is checked into git; every self-check fails the build.
# >>> SPELL GEN (pure Python: SkyySkills/test_skyyskills_0.4.8.py execs this block on synthetic items to prove the Parent / shape rules)
import copy as _scopy
import math as _smath
SPELL_COST_PARENTS = ("Wand_Cast_Left_Charged", "Spellbook_Cast_Hurl_Charged", "Staff_Cast_Summon_Charged", "Gun_Shoot_Flintlock_Charged")
SPELL_DRAIN_PARENTS = ("Wand_Cast_Cost", "Spellbook_Cast_Cost", "Staff_Cast_Cost", "Gun_Shoot_Cost")
SPELL_SKIP_BLOCKS = ("InteractionVars", "Armor", "Weapon")   # Armor / Weapon StatModifiers Mana are max-Mana bonuses, not costs


def spell_fail(msg):
    raise SystemExit("spell costs: " + msg)


def spell_new(v, div):
    """the new Mana number: |v| / div rounded half up, at least 1; 0 stays 0; the sign is kept (a drain stays negative)"""
    if isinstance(v, bool) or not isinstance(v, int):
        spell_fail("a Mana number %r is not a whole number" % (v,))
    if v == 0:
        return 0
    m = int(_smath.floor(abs(v) / float(div) + 0.5))
    if m < 1:
        m = 1
    return m if v > 0 else -m


def _spell_hits(x, path, out):
    if isinstance(x, dict):
        for f in ("Costs", "StatModifiers"):
            if isinstance(x.get(f), dict) and "Mana" in x[f]:
                out.append((tuple(path), f, x[f]["Mana"]))
        for k in x:
            _spell_hits(x[k], path + [k], out)
    elif isinstance(x, list):
        for i in range(len(x)):
            _spell_hits(x[i], path + [i], out)
    return out


def _spell_at(d, path):
    for p in path:
        d = d[p]
    return d


def _spell_diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a.keys()) != list(b.keys()):
            out.append((tuple(path), "keys"))
            return out
        for k in a:
            _spell_diff(a[k], b[k], path + [k], out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((tuple(path), "len"))
            return out
        for i in range(len(a)):
            _spell_diff(a[i], b[i], path + [i], out)
    elif type(a) != type(b) or a != b:
        out.append((tuple(path), "value"))
    return out


def spell_plan(items, div):
    """items = {item id: (asset path, parsed JSON)} of Server/Item/Items/**. Returns (plan, inherits, unchanged):
    plan = [(id, path, [(entry path, field, old, new)], new JSON)] for every item whose Mana numbers change (sorted by id);
    inherits = {item id: the ancestor whose InteractionVars - and so Mana cost - it takes by Parent}; unchanged = ids whose Mana numbers
    are all 0. Anything this build does not know the meaning of stops the build (spell_fail)."""
    own = {}
    for iid in sorted(items):
        path, d = items[iid]
        if not isinstance(d, dict):
            spell_fail("%s is not a JSON object" % iid)
        outside = _spell_hits(dict((k, v) for k, v in d.items() if k not in SPELL_SKIP_BLOCKS), [], [])
        for (hp, f, v) in outside:
            if f == "Costs" or (isinstance(v, (int, float)) and not isinstance(v, bool) and v < 0):
                spell_fail("%s has a Mana %s outside InteractionVars at %s - not a pattern this build knows" % (iid, f, "/".join(str(x) for x in hp)))
        iv = d.get("InteractionVars")
        if iv is None:
            continue
        if not isinstance(iv, dict):
            spell_fail("%s: InteractionVars is not an object" % iid)
        hits = _spell_hits(iv, ["InteractionVars"], [])
        if not hits:
            continue
        ents = []
        for (hp, f, v) in hits:
            where = "/".join(str(x) for x in hp)
            if len(hp) != 4 or hp[0] != "InteractionVars" or hp[2] != "Interactions" or not isinstance(hp[3], int):
                spell_fail("%s: a Mana %s at %s (expected InteractionVars/<var>/Interactions/<n>)" % (iid, f, where))
            var = iv[hp[1]]
            ent = _spell_at(d, hp)
            if not isinstance(var, dict) or sorted(var.keys()) != ["Interactions"] or len(var["Interactions"]) != 1:
                spell_fail("%s: var %s is not {\"Interactions\": [one entry]}: %s" % (iid, hp[1], json.dumps(var)[:200]))
            if sorted(ent.keys()) != sorted(["Parent", f]):
                spell_fail("%s: var %s entry has keys %s (expected Parent + %s only)" % (iid, hp[1], sorted(ent.keys()), f))
            if list(ent[f].keys()) != ["Mana"]:
                spell_fail("%s: var %s %s names more than Mana: %s" % (iid, hp[1], f, json.dumps(ent[f])))
            parents = SPELL_COST_PARENTS if f == "Costs" else SPELL_DRAIN_PARENTS
            if ent["Parent"] not in parents:
                spell_fail("%s: var %s %s has Parent %r - not a known Mana %s interaction %s" % (
                    iid, hp[1], f, ent["Parent"], "cast check" if f == "Costs" else "drain", list(parents)))
            if isinstance(v, bool) or not isinstance(v, int):
                spell_fail("%s: var %s %s Mana %r is not a whole number" % (iid, hp[1], f, v))
            if (f == "Costs" and v < 0) or (f == "StatModifiers" and v > 0):
                spell_fail("%s: var %s %s Mana %r has the wrong sign (a cast check is >= 0, a drain <= 0)" % (iid, hp[1], f, v))
            ents.append((hp, f, v, spell_new(v, div)))
        own[iid] = ents

    def chain(iid):
        out, seen = [iid], set([iid])
        while True:
            p = items[out[-1]][1].get("Parent")
            if p is None:
                return out
            if not isinstance(p, str):
                spell_fail("%s: Parent %r is not an id" % (out[-1], p))
            if p not in items:
                return out          # a Parent outside Server/Item/Items (none today): nothing to inherit from here
            if p in seen:
                spell_fail("Parent loop at %s" % p)
            seen.add(p)
            out.append(p)
    inherits = {}
    for iid in sorted(items):
        if iid in own:
            continue            # its own Mana entries are overridden in its own file (a Mana parent of it is overridden too)
        ch = chain(iid)
        if not any(a in own for a in ch[1:]):
            continue
        first = [a for a in ch if "InteractionVars" in items[a][1]][0]
        if first not in own:
            spell_fail("%s inherits a Mana cost by Parent (%s), but %s has its own InteractionVars without one - whether the engine merges "
                       "the two is not known, so this build cannot tell which cost %s pays" % (iid, " -> ".join(ch), first, iid))
        inherits[iid] = first   # its own file stays vanilla and names the overridden parent: it gets the new cost from there
    plan, unchanged = [], []
    for iid in sorted(own):
        ents = own[iid]
        path, d = items[iid]
        if all(e[2] == 0 for e in ents):
            unchanged.append(iid)
            continue
        nc = [e for e in ents if e[1] == "Costs"]
        nd = [e for e in ents if e[1] == "StatModifiers"]
        if len(nc) != 1 or len(nd) != 1:
            spell_fail("%s has %d Mana cast check(s) and %d drain(s) - expected exactly one of each" % (iid, len(nc), len(nd)))
        new = _scopy.deepcopy(d)
        for (hp, f, v, nv) in ents:
            _spell_at(new, hp)[f]["Mana"] = nv
        diff = _spell_diff(d, new, [], [])
        want = sorted(tuple(list(hp) + [f, "Mana"]) for (hp, f, v, nv) in ents if v != nv)
        if any(why != "value" for p, why in diff) or sorted(p for p, why in diff) != want:
            spell_fail("%s: the generated item differs from vanilla in more than its Mana numbers: %s" % (iid, diff[:6]))
        back = _scopy.deepcopy(new)
        for (hp, f, v, nv) in ents:
            _spell_at(back, hp)[f]["Mana"] = v
        if back != d or json.dumps(back) != json.dumps(d):
            spell_fail("%s: putting the old numbers back does not give the vanilla item" % iid)
        plan.append((iid, path, list(ents), new))
    return plan, inherits, unchanged


def spell_leaks(items, ints, roots):
    """[(item id, text)] for every item whose interactions reach a Mana cost it does not set in its own InteractionVars: a vanilla
    interaction asset with a Costs / negative StatModifiers Mana (its own or one it inherits by an interaction Parent), an inline one
    outside the item's overrides (also one that inherits it by Parent), or the Parent of an override that does not set that Mana itself.
    Each cost is reported once. items / ints / roots = {id: parsed JSON} (items resolved through Parent, shallow). An item's
    InteractionVars key replaces the interaction / root interaction / Replace var of that name (how the vanilla wands and staffs work)."""
    skip = ("Type", "$Comment", "Var", "Effects", "Parent", "Tags", "Config", "ItemToRemove", "ItemToAdd", "Cooldown", "Costs", "StatModifiers")

    def mana_of(d):
        out = []
        if isinstance(d, dict):
            for f in ("Costs", "StatModifiers"):
                if isinstance(d.get(f), dict) and "Mana" in d[f]:
                    v = d[f]["Mana"]
                    if f == "Costs" or (isinstance(v, (int, float)) and v < 0):
                        out.append((f, v))
        return out

    def sets(d, f):
        return isinstance(d, dict) and isinstance(d.get(f), dict) and "Mana" in d[f]

    def mana_eff(d, depth):
        """the Mana costs an interaction really has: its own + those it inherits through an interaction Parent chain that it does not
        set itself (conservative: a Costs / StatModifiers block without Mana does not hide the parent's Mana)"""
        out = mana_of(d)
        p = d.get("Parent") if isinstance(d, dict) else None
        if isinstance(p, str) and p in ints and depth < 30:
            out += [(f, v) for f, v in mana_eff(ints[p], depth + 1) if not sets(d, f) and f not in [g for g, w in out]]
        return out

    def eff(iid, depth):
        d = items[iid]
        p = d.get("Parent")
        if isinstance(p, str) and p in items and depth < 30:
            m = dict(eff(p, depth + 1))
            m.update(d)
            return m
        return d
    res = []
    for iid in sorted(items):
        d = eff(iid, 0)
        iv = d.get("InteractionVars") or {}
        if not isinstance(iv, dict):
            continue
        seen = set()
        leaks = []

        def parent(x, depth):
            # walk the rest of an interaction Parent (its Next / branches); its Mana was already counted by mana_eff / the override check.
            # Its own seen key: the same interaction referenced directly (by id) is still an asset whose defaults count.
            pid = x.get("Parent")
            if isinstance(pid, str) and pid in ints and ("par", pid) not in seen:
                seen.add(("par", pid))
                node(ints[pid], depth + 1, False, True)

        def asset(sid, depth):
            for kind, amap in (("int", ints), ("root", roots)):
                if sid in amap and (kind, sid) not in seen:
                    seen.add((kind, sid))
                    if kind == "int":
                        for f, v in mana_eff(amap[sid], 0):
                            leaks.append("%s %s Mana %s (a vanilla default the item does not set)" % (sid, f, v))
                    node(amap[sid], depth + 1, False, kind == "int")

        def ref(sid, depth):
            if sid not in iv:
                asset(sid, depth)
                return
            ov = iv[sid]
            ents = [ov] if isinstance(ov, str) else ((ov.get("Interactions") or []) if isinstance(ov, dict) else [])
            for e in ents:
                if isinstance(e, str):
                    asset(e, depth)
                elif isinstance(e, dict):
                    pid = e.get("Parent")
                    if isinstance(pid, str) and pid in ints:
                        for f, v in mana_eff(ints[pid], 0):
                            if not sets(e, f):
                                leaks.append("%s -> Parent %s %s Mana %s (the override does not set it)" % (sid, pid, f, v))
                    node(e, depth + 1, True, True)

        def node(x, depth, mine, top=False):
            # top = this dict's own Mana (and its Parent's) was already counted by the caller; its children are walked as usual
            if depth > 80:
                return
            if isinstance(x, str):
                ref(x, depth)
                return
            if isinstance(x, list):
                for e in x:
                    node(e, depth + 1, mine)
                return
            if not isinstance(x, dict):
                return
            if x.get("Type") == "Replace" and "Var" in x:
                if x["Var"] in iv:
                    ref(x["Var"], depth + 1)
                else:
                    node(x.get("DefaultValue"), depth + 1, mine)
                return
            if not mine and not top:
                for f, v in mana_eff(x, 0):
                    leaks.append("an inline %s Mana %s%s" % (f, v, "" if sets(x, f) else " (inherited from its Parent %s)" % x.get("Parent")))
            parent(x, depth)
            for k in x:
                if k not in skip:
                    node(x[k], depth + 1, mine)
        node(d.get("Interactions"), 0, False)
        for t in leaks:
            res.append((iid, t))
    return res
# <<< SPELL GEN
assert SPELL_DIVISOR == 5 and spell_new(25, 5) == 5 and spell_new(-50, 5) == -10 and spell_new(100, 5) == 20 and spell_new(0, 5) == 0
assert spell_new(3, 5) == 1 and spell_new(-2, 5) == -1 and spell_new(12, 5) == 2 and spell_new(13, 5) == 3 and spell_new(1, 5) == 1
with zipfile.ZipFile(ASSETS) as _sz:
    _snames = _sz.namelist()

    def _sids(prefix):
        out = {}
        for n in _snames:
            if n.startswith(prefix) and n.endswith(".json"):
                out.setdefault(os.path.basename(n)[:-5], []).append(n)
        return out
    _si, _sn, _sr = _sids("Server/Item/Items/"), _sids("Server/Item/Interactions/"), _sids("Server/Item/RootInteractions/")
    for _m, _w in ((_si, "item"), (_sn, "interaction"), (_sr, "root interaction")):
        _dup = sorted(k for k, v in _m.items() if len(v) > 1)
        if _dup:
            spell_fail("Assets.zip has %d %s id(s) more than once: %s" % (len(_dup), _w, _dup[:5]))

    def _sread(n, strict=False):
        t = _sz.read(n).decode("utf-8-sig")
        if not strict:
            return json.loads(t)

        def _hook(pairs):
            ks = [k for k, v in pairs]
            if len(set(ks)) != len(ks):
                spell_fail("%s has a duplicate JSON key %s" % (n, sorted(set(k for k in ks if ks.count(k) > 1))))
            return dict(pairs)
        return json.loads(t, object_pairs_hook=_hook)
    SPELL_ITEMS = dict((k, (v[0], _sread(v[0]))) for k, v in _si.items())
    SPELL_INTS = dict((k, _sread(v[0])) for k, v in _sn.items())
    SPELL_ROOTS = dict((k, _sread(v[0])) for k, v in _sr.items())
    SPELL_PLAN, SPELL_INHERITS, SPELL_UNCHANGED = spell_plan(SPELL_ITEMS, SPELL_DIVISOR)
    for _iid, _p, _e, _nj in SPELL_PLAN:       # the overridden files have no duplicate key (json.loads would have kept only the last)
        if _sread(_p, strict=True) != SPELL_ITEMS[_iid][1]:
            spell_fail("%s parses differently with the duplicate-key check" % _iid)
_leaks = spell_leaks(dict((k, v[1]) for k, v in SPELL_ITEMS.items()), SPELL_INTS, SPELL_ROOTS)
if _leaks:
    spell_fail("%d item(s) reach a Mana cost they do not set in their own InteractionVars (a /%d override of the item would miss it): %s"
               % (len(set(i for i, t in _leaks)), SPELL_DIVISOR, _leaks[:6]))
if len(SPELL_PLAN) < 20:
    spell_fail("only %d Mana-costing items found in Assets.zip (32 on 2026-09-30) - check the scan" % len(SPELL_PLAN))
SPELL_FILES = {}
SPELL_TABLE = []    # (id, old cast check, new, old drain, new drain) - sorted by id
for _iid, _p, _e, _nj in SPELL_PLAN:
    _txt = json.dumps(_nj, indent=2, ensure_ascii=True) + "\n"
    assert _p.startswith("Server/Item/Items/") and _p.endswith("/%s.json" % _iid) and _p not in SPELL_FILES
    assert json.loads(_txt) == _nj and all(ord(ch) < 128 for ch in _txt)
    SPELL_FILES[_p] = _txt
    _c = [x for x in _e if x[1] == "Costs"][0]
    _dr = [x for x in _e if x[1] == "StatModifiers"][0]
    SPELL_TABLE.append((_iid, _c[2], _c[3], -_dr[2], -_dr[3]))
SPELL_IDS = [x[0] for x in SPELL_TABLE]
# the kit weapons Skyy's numbers were chosen for (Mage 30 = 3 staff casts, Priest 30 = 6 wand casts)
_sk = dict((x[0], x) for x in SPELL_TABLE)
assert _sk["Weapon_Staff_Wood"][2] == 10 and _sk["Weapon_Wand_Wood"][2] == 5, (_sk.get("Weapon_Staff_Wood"), _sk.get("Weapon_Wand_Wood"))
# no other Skyy mod of the live set (tools/deploy_set.py SET, its pinned jars) and no pack mod (PACK_THIRD_PARTY, found in the Mods folder by
# its manifest, read only) ships one of these item files or ids - two overrides of one item would fight over it
import re as _sre
_dst = open(os.path.join(os.path.dirname(HERE), "tools", "deploy_set.py"), encoding="utf-8").read()
_s0 = _dst.index("SET = [")
_pins = _sre.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', _dst[_s0:_dst.index("\n]\n", _s0)])
_packs = _sre.findall(r'"([^"]+:[^"]+)"', _sre.search(r"PACK_THIRD_PARTY = \[(.*?)\]", _dst).group(1))
# any SkyySkills pin, not a fixed version: once the SET pin is bumped to this version the build must still run (e.g. after a Hytale update)
assert any(m == "SkyySkills" for m, v in _pins) and len(_pins) >= 20 and _packs, (_pins, _packs)


def _spell_clash(names):
    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
                                                           and os.path.basename(n)[:-5] in _sk))
_checked = []
for _mod, _ver in _pins:
    if _mod == "SkyySkills":
        continue
    _jp = os.path.join(os.path.dirname(HERE), _mod, "%s-%s.jar" % (_mod, _ver))
    if not os.path.isfile(_jp):
        print("spell costs: NOTE %s %s is not built here - its items were not checked" % (_mod, _ver))
        continue
    with zipfile.ZipFile(_jp) as _jz:
        _cl = _spell_clash(_jz.namelist())
    if _cl:
        spell_fail("%s %s (live set) also ships %s" % (_mod, _ver, _cl[:5]))
    _checked.append(_mod)
_pk_found, _other, _pk_mana = [], [], []
for _f in (sorted(os.listdir(B.MODS_DIR)) if os.path.isdir(B.MODS_DIR) else []):
    _p = os.path.join(B.MODS_DIR, _f)
    try:
        if os.path.isdir(_p):
            with open(os.path.join(_p, "manifest.json"), "rb") as _mf:
                _man = json.loads(_mf.read().decode("utf-8-sig"))
            _nm = [os.path.relpath(os.path.join(_r, _x), _p).replace(os.sep, "/") for _r, _ds, _fl in os.walk(_p) for _x in _fl]
        elif _f.lower().endswith((".zip", ".jar")):
            with zipfile.ZipFile(_p) as _mz:
                _man = json.loads(_mz.read("manifest.json").decode("utf-8-sig"))
                _nm = _mz.namelist()
        else:
            continue
    except Exception:
        continue
    if not isinstance(_man, dict):
        continue
    _key = "%s:%s" % (_man.get("Group"), _man.get("Name"))
    _cl = _spell_clash(_nm)
    if _key in _packs:
        _pk_found.append(_key)
        if _cl:
            spell_fail("pack mod %s (%s) also ships %s" % (_key, _f, _cl[:5]))
        # its own items keep their full Mana cost (only vanilla items are divided) - say so if one has a Mana cost or inherits one
        for _n in _nm:
            if not (_n.startswith("Server/Item/Items/") and _n.endswith(".json")):
                continue
            try:
                if os.path.isdir(_p):
                    _raw = open(os.path.join(_p, *_n.split("/")), "rb").read()
                else:
                    with zipfile.ZipFile(_p) as _mz:
                        _raw = _mz.read(_n)
                _pj = json.loads(_raw.decode("utf-8-sig"))
            except Exception:
                continue
            if isinstance(_pj, dict) and (_spell_hits(_pj.get("InteractionVars") or {}, [], [])
                                          or (isinstance(_pj.get("Parent"), str) and _pj["Parent"] in _sk)):
                _pk_mana.append("%s %s" % (_key, os.path.basename(_n)[:-5]))
    elif _cl and not str(_man.get("Name", "")).endswith("SkyySkills"):   # every other mod, Skyy-named or not (not our own deployed jar)
        _other.append("%s (%d)" % (_f, len(_cl)))
print("spell costs /%d: %d item overrides generated from Assets.zip (%d with only 0 costs left alone: %s; Parent: %d item(s) inherit a cost%s); "
      "no clash with %d live-set jars or the pack mods %s" % (
          SPELL_DIVISOR, len(SPELL_PLAN), len(SPELL_UNCHANGED), ", ".join(SPELL_UNCHANGED) or "none", len(SPELL_INHERITS),
          (" " + ", ".join("%s <- %s" % kv for kv in sorted(SPELL_INHERITS.items()))) if SPELL_INHERITS else "", len(_checked),
          ", ".join(sorted(_pk_found)) or "(none installed)"))
for _t in SPELL_TABLE:
    print("  %-34s cast check %3d -> %2d   drain %3d -> %2d" % _t)
if _other:
    print("spell costs: NOTE mods in the Mods folder that are NOT in the live set also replace some of these items (only a problem if "
          "they are ever enabled): %s" % ", ".join(_other))
if _pk_mana:
    print("spell costs: NOTE pack mod items with their own Mana cost (or a Parent overridden here) are NOT divided: %s" % ", ".join(_pk_mana))
'''
rep('# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories\' skyyacc_* or the coming SkyyGear\'s skyygear*\n',
    SPELL_GEN + '# the modifier keys (spec 4.12): our own prefix, distinct, never SkyyAccessories\' skyyacc_* or the coming SkyyGear\'s skyygear*\n')

# ---------------------------------------------------------------------------------------------------------------- OverallCfg
rep('''for _decl in ("boolean MANA_ON = true", "double BASE = 10.0", "double MAGIC_BASE = 20.0", 'String[] MAGIC = new String[] { "Mage", "Priest" }',
              'String MAGIC_TEXT = "Mage,Priest"', "boolean ON = true", "int[] SLOTS = new int[] { 0, 1, 2, 4, 10, 11, 12, 13 }",
              "boolean CLASS = true", "double HP = 0.5", "double MANA = 0.2", "boolean HEAL = true", "boolean CHAT = true"):
    ovc.addField(CtField.make("public static volatile " + _decl + ";", ovc))
''', '''for _decl in ("boolean MANA_ON = true", "double BASE = 10.0", "boolean ON = true", "int[] SLOTS = new int[] { 0, 1, 2, 4, 10, 11, 12, 13 }",
              "boolean CLASS = true", "double HP = 0.5", "double MANA = 0.2", "boolean HEAL = true", "boolean CHAT = true",
              # 0.4.8 Base Mana by class: TBL = the table as ONE snapshot Object[]{String[] classes (SkillDefs.CLASSES spelling and order),
              # double[] base, String text "Mage 30, Priest 30"} (null = not read yet = the default table); LEGACY = it came from the 0.4.7
              # pair because ManaMig could not move it; GUARD_DIRTY = ManaGuard runs on the next tick; WARNED = the last table WARN
              "Object[] TBL = null", "boolean LEGACY = false", "boolean GUARD_DIRTY = true", 'String WARNED = ""'):
    ovc.addField(CtField.make("public static volatile " + _decl + ";", ovc))
ovc.addField(CtField.make('public static final String TABLE_PREFIX = "mana.classBase.";', ovc))
ovc.addField(CtField.make("public static final String[] DEF_CLS = %s;" % jarr([_c for _c, _v in CLASS_BASE_DEF]), ovc))
ovc.addField(CtField.make("public static final double[] DEF_BASE = new double[] { %s };" % ", ".join("%d.0" % _v for _c, _v in CLASS_BASE_DEF), ovc))
''')
# ensureDefaults: a just-appended block is also put into this load's properties (the table has no code default of its own: a missing
# table line means "that class is not listed", so the appended default entries must be read in this same load)
rep('''    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Overall Level + base Mana section (mana.* / overall.* keys, default values)");
''', '''    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the Overall Level + base Mana section (mana.* / overall.* keys, default values)");
    java.util.Properties d = new java.util.Properties();
    d.load(new java.io.StringReader(DEFAULTS));
    java.util.Iterator it = d.stringPropertyNames().iterator();
    while (it.hasNext()) {{
      String k = (String) it.next();
      if (p.getProperty(k) == null) p.setProperty(k, d.getProperty(k));
    }}
''')
OVC_NEW = r'''# 0.4.8 Base Mana by class (tools/skills_0_4_8_patch.py point 2). Table entries are class names in any case, stored and shown with the
# SkillDefs.CLASSES spelling and in that order.
ovc.addMethod(CtNewMethod.make(f"""
public static String canonClass(String t) {{
  if (t == null) return null;
  String x = t.trim();
  for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) if ({PKG}.SkillDefs.CLASSES[k].equalsIgnoreCase(x)) return {PKG}.SkillDefs.CLASSES[k];
  return null;
}}""", ovc))
# {String[] classes, double[] base, String text} in SkillDefs.CLASSES order; entries that are not a class are dropped, the first of a class wins
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] mkTable(String[] c, double[] b) {{
  int n = {PKG}.SkillDefs.CLASSES.length;
  boolean[] has = new boolean[n];
  double[] v = new double[n];
  int cnt = 0;
  for (int i = 0; i < c.length && i < b.length; i++) {{
    String x = canonClass(c[i]);
    if (x == null) continue;
    for (int k = 0; k < n; k++) {{
      if ({PKG}.SkillDefs.CLASSES[k].equals(x) && !has[k]) {{ has[k] = true; v[k] = b[i]; cnt++; }}
    }}
  }}
  String[] oc = new String[cnt];
  double[] ob = new double[cnt];
  StringBuilder sb = new StringBuilder();
  int j = 0;
  for (int k = 0; k < n; k++) {{
    if (!has[k]) continue;
    oc[j] = {PKG}.SkillDefs.CLASSES[k];
    ob[j] = v[k];
    if (j > 0) sb.append(", ");
    sb.append(oc[j]).append(" ").append({PKG}.DivCfg.num(v[k]));
    j++;
  }}
  return new Object[] {{ oc, ob, sb.toString() }};
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static Object[] defTable() {
  return mkTable(DEF_CLS, DEF_BASE);
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static Object[] tbl() {
  Object[] t = TBL;
  if (t == null) {
    t = defTable();
    TBL = t;
  }
  return t;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static boolean anyTableKey(java.util.Properties p) {
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) if (((String) it.next()).startsWith(TABLE_PREFIX)) return true;
  return false;
}""", ovc))
# the mana.classBase.<Class>=<Mana> lines -> {String[], double[], String text, String problems ("" = none)}. Keys are read in sorted order,
# so of two spellings of one class the exact SkillDefs.CLASSES spelling wins (it sorts first: capital letters come before small ones)
# and the other is reported; a line that is not a class or not a number is left out and reported; values are clamped to 0-10000 like
# the row bounds (the kit refuses them when typed).
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] parseTable(java.util.Properties p) {{
  java.util.ArrayList cs = new java.util.ArrayList();
  java.util.ArrayList bs = new java.util.ArrayList();
  StringBuilder bad = new StringBuilder();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {{
    String k = (String) it.next();
    if (!k.startsWith(TABLE_PREFIX)) continue;
    String e = k.substring(TABLE_PREFIX.length()).trim();
    String c = canonClass(e);
    String raw = p.getProperty(k);
    String shown = e.length() > 40 ? e.substring(0, 40) + "..." : e;
    if (c == null) {{ if (bad.length() > 0) bad.append("; "); bad.append(shown + " is not a class (left out)"); continue; }}
    if (cs.contains(c)) {{ if (bad.length() > 0) bad.append("; "); bad.append(c + " is listed twice (" + shown + " left out)"); continue; }}
    double v = Double.NaN;
    try {{ v = Double.parseDouble(raw.trim()); }} catch (Throwable t) {{ v = Double.NaN; }}
    if (Double.isNaN(v) || Double.isInfinite(v)) {{
      if (bad.length() > 0) bad.append("; ");
      String rv = raw == null ? "" : raw.trim();
      bad.append(shown + "=" + (rv.length() > 20 ? rv.substring(0, 20) + "..." : rv) + " is not a number (left out)");
      continue;
    }}
    cs.add(c);
    bs.add(Double.valueOf(clampD(v, 0.0, 0.0, 10000.0)));
  }}
  String[] c2 = new String[cs.size()];
  double[] b2 = new double[cs.size()];
  for (int i = 0; i < c2.length; i++) {{ c2[i] = (String) cs.get(i); b2[i] = ((Double) bs.get(i)).doubleValue(); }}
  Object[] t = mkTable(c2, b2);
  return new Object[] {{ t[0], t[1], t[2], bad.toString() }};
}}""", ovc))
# the 0.4.7 pair read as the table (only while ManaMig could not move it): every class of mana.magicClasses (default Mage,Priest) gets
# mana.magicBase (default 20), exactly what 0.4.7 gave them
ovc.addMethod(CtNewMethod.make(f"""
public static Object[] legacyTable(java.util.Properties p) {{
  double b = clampD({PKG}.SkillCfg.dbl(p, "mana.magicBase", 20.0), 20.0, 0.0, 10000.0);
  String mc = p.getProperty("mana.magicClasses");
  String[] c = parseClasses(mc == null ? "Mage,Priest" : mc);
  double[] v = new double[c.length];
  for (int i = 0; i < v.length; i++) v[i] = b;
  return mkTable(c, v);
}}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static double baseFor(String cls) {
  if (cls != null) {
    String x = cls.trim();
    Object[] t = tbl();
    String[] c = (String[]) t[0];
    double[] b = (double[]) t[1];
    for (int i = 0; i < c.length && i < b.length; i++) if (c[i].equalsIgnoreCase(x)) return b[i];
  }
  return BASE;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static boolean listed(String cls) {
  if (cls == null) return false;
  String x = cls.trim();
  String[] c = (String[]) tbl()[0];
  for (int i = 0; i < c.length; i++) if (c[i].equalsIgnoreCase(x)) return true;
  return false;
}""", ovc))
ovc.addMethod(CtNewMethod.make("""
public static String tableText() {
  return (String) tbl()[2];
}""", ovc))
# check= hook of the mana.classBase table (CONFIG-CONTRACT: key = "mana.classBase[<entry>]", value = the canonical Mana text or null for a
# removal; also run for hand-edited lines, kit 1.1): the entry must be a class name (any case - the loader stores the canonical spelling)
ovc.addMethod(CtNewMethod.make("""
public static String checkClassBase(String key, String value) {
  if (value == null || key == null) return null;
  String e = key;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a >= 0 && b > a) e = key.substring(a + 1, b);
  if (canonClass(e) != null) return null;
  if (e.length() > 40) e = e.substring(0, 40) + "...";
  return "Unknown class " + e + " - use Archer, Warrior, Mage, Berserker, Priest, Assassin or Shaman.";
}""", ovc))
'''
rep('''ovc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  MANA_ON = {PKG}.SkillCfg.bool(p, "mana.base.enabled", true);
  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", 10.0), 10.0, 0.0, 10000.0);
  MAGIC_BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.magicBase", 20.0), 20.0, 0.0, 10000.0);
  String mc = p.getProperty("mana.magicClasses");
  if (mc == null) mc = "Mage,Priest";
  String bad = badClass(mc);
  if (bad != null) {PKG}.SkillCfg.warn("mana.magicClasses: " + bad + " is not a class - left out (classes: Archer, Warrior, Mage, Berserker, Priest, Assassin, Shaman)");
  String[] m = parseClasses(mc);
  MAGIC = m;
  MAGIC_TEXT = join(m, ",");
  ON = ''', OVC_NEW + '''ovc.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  MANA_ON = {PKG}.SkillCfg.bool(p, "mana.base.enabled", true);
  BASE = clampD({PKG}.SkillCfg.dbl(p, "mana.base", 10.0), 10.0, 0.0, 10000.0);
  boolean tk = anyTableKey(p);
  boolean old = p.getProperty("mana.magicBase") != null || p.getProperty("mana.magicClasses") != null;
  Object[] t = null;
  String w = "";
  if (!tk && old) {{
    t = legacyTable(p);
    LEGACY = true;
    w = "xp.properties still has the 0.4.7 lines mana.magicBase / mana.magicClasses (their move to Base Mana by class did not happen - see the start log) - read as Base Mana by class: " + (((String) t[2]).length() > 0 ? (String) t[2] : "no class") + ". Set the table in Server Setup > Skills > Overall and Mana, or restart to retry the move.";
  }} else {{
    t = parseTable(p);
    LEGACY = false;
    if (((String) t[3]).length() > 0) w = "Base Mana by class: " + (String) t[3];
    if (tk && old) w = (w.length() > 0 ? w + "; " : "") + "mana.magicBase / mana.magicClasses in xp.properties are no longer used (0.4.8 reads Base Mana by class, mana.classBase.<Class>=<Mana>) - delete those lines";
  }}
  TBL = new Object[] {{ t[0], t[1], t[2] }};
  if (w.length() > 0 && !w.equals(WARNED)) {PKG}.SkillCfg.warn(w);
  WARNED = w;
  GUARD_DIRTY = true;
  ON = ''')
rep('''  String b = MANA_ON ? "base mana " + {PKG}.DivCfg.num(BASE) + " / " + {PKG}.DivCfg.num(MAGIC_BASE) + " for " + (MAGIC.length > 0 ? MAGIC_TEXT : "nobody") : "base mana off";
''', '''  String tt = tableText();
  String b = MANA_ON ? "base mana " + {PKG}.DivCfg.num(BASE) + ", class Mana table " + (tt.length() > 0 ? tt : "empty") + (LEGACY ? " (from the 0.4.7 lines)" : "") : "base mana off";
''')

# ---------------------------------------------------------------------------------------------------------------- Overall
rep('''public static boolean magic(java.util.UUID u) {{
  String c = classOf(u);
  if (c == null) return false;
  String[] m = {PKG}.OverallCfg.MAGIC;
  for (int i = 0; i < m.length; i++) if (m[i].equalsIgnoreCase(c)) return true;
  return false;
}}''', '''public static boolean magic(java.util.UUID u) {{
  return {PKG}.OverallCfg.listed(classOf(u));
}}''')
rep('''# the TOTAL base this player has (10, 20 for a magic user, 0 when the part is off)
ovl.addMethod(CtNewMethod.make(f"""
public static float baseTarget(java.util.UUID u) {{
  if (!{PKG}.OverallCfg.MANA_ON) return 0.0f;
  return round2(magic(u) ? {PKG}.OverallCfg.MAGIC_BASE : {PKG}.OverallCfg.BASE);
}}""", ovl))''', '''# the TOTAL base this player has (0.4.8: the class's Base Mana by class entry, else mana.base; 0 when the part is off)
ovl.addMethod(CtNewMethod.make(f"""
public static float baseTarget(java.util.UUID u) {{
  if (!{PKG}.OverallCfg.MANA_ON) return 0.0f;
  return round2({PKG}.OverallCfg.baseFor(classOf(u)));
}}""", ovl))''')
rep('''public static String magicText() {{
  return {PKG}.OverallCfg.join({PKG}.OverallCfg.MAGIC, ", ");
}}''', '''public static String magicText() {{
  return {PKG}.OverallCfg.tableText();
}}''')
rep('''  else if (magic(u)) out.add("Base Mana " + num((double) baseTarget(u)) + " - " + classOf(u) + " is a magic user");
  else out.add("Base Mana " + num((double) round2({PKG}.OverallCfg.BASE)) + ({PKG}.OverallCfg.MAGIC.length > 0 ? " (magic users - " + magicText() + " - start at " + num((double) round2({PKG}.OverallCfg.MAGIC_BASE)) + ")" : ""));
''', '''  else if (magic(u)) out.add("Base Mana " + num((double) baseTarget(u)) + " - the " + {PKG}.OverallCfg.canonClass(classOf(u)) + " base (Base Mana by class)");
  else out.add("Base Mana " + num((double) round2({PKG}.OverallCfg.BASE)) + (magicText().length() > 0 ? " (by class: " + magicText() + ")" : ""));
''')

# ---------------------------------------------------------------------------------------------------------------- config rows
rep('''    ("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
     "Max Mana every player starts with (vanilla gives 0).", "reload"),
    ("mana.magicBase", "Base Mana for magic users", "overall", "dec", "20", "0", "10000", "", "", "live",
     "Replaces the base above for the classes below: their base is this, not base + this.", "reload"),
    ("mana.magicClasses", "Magic user classes", "overall", "text", "Mage,Priest", "", "200", "", "", "live",
     "Class names, comma separated (Mage, Priest, Archer, Warrior, Berserker, Assassin, Shaman).", "reload;check=OverallCfg.checkClasses"),
''', '''    ("mana.base", "Base Mana for everyone", "overall", "dec", "10", "0", "10000", "", "", "live",
     "Max Mana every player starts with, unless Base Mana by class lists their class (vanilla gives 0).", "reload"),
    # 0.4.8 (Skyy 2026-09-30): the per-class table replaces mana.magicBase + mana.magicClasses (ManaMig moves an existing file once)
    ("mana.classBase", "Base Mana by class", "overall", "table", "", "0", "10000", "dec;type;Base Mana", "", "live",
     "Max Mana a listed class starts with, instead of the base above (Mage 30 = 3 staff casts).", "reload;check=OverallCfg.checkClassBase"),
    # 0.4.8: the spell cost divisor is fixed in the jar (the item overrides are generated at build time) - shown, never edited
    ("spell.manaDivisor", "Spell Mana costs divided by", "overall", "int", str(SPELL_DIVISOR), "", "", "", "x", "ro",
     "Fixed in the jar at build time: vanilla spell Mana costs / this (wand 5, staff 10, spellbook 20).", "custom:SkillKit"),
''')
rep('''assert len(CFG_ROWS) == 173, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint), got %d" % len(CFG_ROWS))   # 0.4.6
''', '''assert len(CFG_ROWS) == 173, ("0.4.5 had 159 rows + 10 Overall Level / base Mana rows (Overall-Level-Spec 4.9) + divinity.healXpPerHpSelf + "
                              "3 crossbow extras (meter, sound, hint); 0.4.8: - mana.magicBase / mana.magicClasses + the mana.classBase "
                              "table + the read-only spell.manaDivisor, got %d" % len(CFG_ROWS))   # 0.4.6 / 0.4.8
''')
rep('''for _k in ("mana.base.enabled", "mana.base", "mana.magicBase", "mana.magicClasses", "overall.enabled", "overall.skills", "overall.healthPerLevel",
           "overall.manaPerLevel", "overall.healOnLevelUp", "overall.chat"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\\n" + _k + "=") in ("\\n" + OVL_DEFAULTS), _k
''', '''for _k in ("mana.base.enabled", "mana.base", "overall.enabled", "overall.skills", "overall.healthPerLevel",
           "overall.manaPerLevel", "overall.healOnLevelUp", "overall.chat"):
    assert sum(1 for _r in CFG_ROWS if _r[0] == _k) == 1 and _k in _dp and ("\\n" + _k + "=") in ("\\n" + OVL_DEFAULTS), _k
# 0.4.8: the old pair is gone from the rows and the default file; the table's default entries are in the default file AND in the block
# appended to a pre-0.4.6 file; the read-only divisor row has no file line
for _k in ("mana.magicBase", "mana.magicClasses"):
    assert not any(_r[0] == _k for _r in CFG_ROWS) and _k not in _dp and ("\\n" + _k + "=") not in ("\\n" + OVL_DEFAULTS), _k
for _cb, _cv in CLASS_BASE_DEF:
    assert _dp.get("mana.classBase." + _cb) == str(_cv) and ("\\nmana.classBase.%s=%d\\n" % (_cb, _cv)) in ("\\n" + OVL_DEFAULTS), _cb
assert sorted(_k for _k in _dp if _k.startswith("mana.classBase.")) == sorted("mana.classBase." + _c for _c, _v in CLASS_BASE_DEF)
assert sum(1 for _r in CFG_ROWS if _r[0] == "mana.classBase") == 1 and sum(1 for _r in CFG_ROWS if _r[0] == "spell.manaDivisor") == 1
assert "spell.manaDivisor" not in _dp and all(len(_r[10]) <= 100 and len(_r[1]) <= 40 for _r in CFG_ROWS)
''')
rep('''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp.")):''',
    '''for _tk, _pfx in (("block", "block."), ("prefix", "prefix."), ("suffix", "suffix."), ("alchemy.xp", "alchemy.xp."), ("smithing.xp", "smithing.xp."),
                 ("mana.classBase", "mana.classBase.")):''')
rep('''assert all(_c in [_r[0] for _r in CLASS_ROWS] for _c in "Mage,Priest".split(","))
''', '''assert all(_c in [_r[0] for _r in CLASS_ROWS] for _c, _v in CLASS_BASE_DEF)
''')

# ---------------------------------------------------------------------------------------------------------------- ManaCost / ManaMig / ManaGuard
# The builtin kit table = SkyyClasses' own default kits (its CLASSES "kit" texts), cross-checked against the SET-pinned SkyyClasses script.
KIT_FALLBACK = [("Archer", "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64"), ("Warrior", "Weapon_Sword_Crude:1"),
                ("Assassin", "Weapon_Daggers_Crude:1"), ("Shaman", ""), ("Mage", "Weapon_Staff_Wood:1"),
                ("Berserker", "Weapon_Battleaxe_Crude:1"), ("Priest", "Weapon_Wand_Wood:1")]
MANA_JAVA = r'''
# ================= 0.4.8 ManaCost / ManaMig / ManaGuard (tools/skills_0_4_8_patch.py points 1-3) =================
# compiled after the config kit (ManaMig writes with its CfgRows.atomicWrite) and before SkillKit's custom rows / SkillTick / setup (callers)
KIT_FALLBACK = %r
assert [_c for _c, _k in KIT_FALLBACK] == [_c[0] for _c in CLASS_ROWS], "KIT_FALLBACK must follow SkillDefs.CLASSES"
for _c, _k in KIT_FALLBACK:
    for _e in [x for x in _k.split(",") if x]:
        must(_e.split(":")[0])
# cross-check: the SET-pinned SkyyClasses script still ships these default kits (a note, not a stop: SkyyClasses may change them on purpose;
# the guard reads the live kit from SkyyClasses whenever it runs)
_cpin = [v for m, v in _pins if m == "SkyyClasses"]
_cps = os.path.join(os.path.dirname(HERE), "SkyyClasses", "build_skyyclasses_%%s.py" %% (_cpin[0] if _cpin else "?"))
if os.path.isfile(_cps):
    _ctxt = open(_cps, encoding="utf-8").read()
    _cdiff = [c for c, k in KIT_FALLBACK if not _sre.search(r'"name": "%%s",.*?"kit": "%%s"' %% (c, _sre.escape(k)), _ctxt, _sre.S)]
    print("mana guard: built-in kit table %%s SkyyClasses %%s's default kits%%s" %% (
        "matches" if not _cdiff else "DIFFERS from", _cpin[0], (" (" + ", ".join(_cdiff) + ")") if _cdiff else ""))
else:
    print("mana guard: NOTE SkyyClasses script %%s not found - built-in kit table not cross-checked" %% _cps)
mcost = pool.makeClass(PKG + ".ManaCost")
mcost.addField(CtField.make("public static final int DIVISOR = %%d;" %% SPELL_DIVISOR, mcost))
mcost.addField(CtField.make("public static final int N = %%d;" %% len(SPELL_TABLE), mcost))
mcost.addField(CtField.make("public static final String[] IDS = %%s;" %% jarr(SPELL_IDS), mcost))
for _nm, _ix in (("OLD", 1), ("COST", 2), ("OLD_DRAIN", 3), ("DRAIN", 4)):
    mcost.addField(CtField.make("public static final int[] %%s = new int[] { %%s };" %% (_nm, ", ".join(str(_t[_ix]) for _t in SPELL_TABLE)), mcost))
# the (new) Mana a cast of this item checks for; -1 = not a Mana weapon of this jar
mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  if (id == null) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return COST[i];
  return -1;
}""", mcost))

# ---- ManaMig (point 2): the one-time move of mana.magicBase / mana.magicClasses to Base Mana by class. setup() only, BEFORE SkillCfg.load
# and CfgPub.start (the kit owns every write after that). Returns {level "info" / "warn" / "" (nothing to do), message}; logs the message.
mmig = pool.makeClass(PKG + ".ManaMig")
mmig.addField(CtField.make('public static final String OLD_BASE = "mana.magicBase";', mmig))
mmig.addField(CtField.make('public static final String OLD_CLS = "mana.magicClasses";', mmig))
# the file as it was before a move (set only after the move was written); keepCopy puts it into the kit's history once the kit started
mmig.addField(CtField.make("public static volatile byte[] BEFORE = null;", mmig))
mmig.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.8";', mmig))
mmig.addField(CtField.make('public static final String WHAT = "xp.properties before mana.magicBase / mana.magicClasses moved to Base Mana by class";', mmig))
# the 0.4.6 / 0.4.7 default comment above the old pair: while it is still exactly this text (3 whole lines, any line ending) the move
# replaces it with the 0.4.8 default comment (the 4 comment lines of the default file above mana.base.enabled); any other comment that
# names the old keys stays and the move adds STALE_NOTE under its own comment line (review 2026-09-30 finding 2)
MANA_DOC_OLD = %r
_ds = OVL_L.index("mana.base.enabled=true")
MANA_DOC_NEW = OVL_L[_ds - 4:_ds]
assert MANA_DOC_NEW[0].startswith("# Base Mana: every player's max Mana starts at mana.base. A class listed below") and \
    MANA_DOC_NEW[3].startswith("# without taking damage). Spells cost the vanilla Mana / %%d " %% SPELL_DIVISOR) and \
    all(_l.startswith("# ") and '"' not in _l and "\\" not in _l for _l in MANA_DOC_NEW + MANA_DOC_OLD), MANA_DOC_NEW
assert not any(("mana.magicBase" in _l or "mana.magicClasses" in _l) and "replaced" not in _l for _l in MANA_DOC_NEW)
mmig.addField(CtField.make("public static final String[] DOC_OLD = %%s;" %% jarr(MANA_DOC_OLD), mmig))
mmig.addField(CtField.make("public static final String[] DOC_NEW = %%s;" %% jarr(MANA_DOC_NEW), mmig))
mmig.addField(CtField.make('public static final String STALE_NOTE = "# (other comments in this file that name mana.magicBase / mana.magicClasses describe those old keys - 0.4.8 no longer reads them)";', mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean isWs(char c) {
  return c == ' ' || c == '\\t' || c == 12;
}""", mmig))
# lines[i..] are exactly DOC_OLD (each line without its CR)
mmig.addMethod(CtNewMethod.make("""
public static boolean docAt(String[] lines, int i) {
  if (i + DOC_OLD.length > lines.length) return false;
  for (int k = 0; k < DOC_OLD.length; k++) {
    String l = lines[i + k];
    if (l.endsWith("\\r")) l = l.substring(0, l.length() - 1);
    if (!l.equals(DOC_OLD[k])) return false;
  }
  return true;
}""", mmig))
# a live line of this key (Properties syntax: white space, the key, then white space, = or : or the end); body = the line without its CR
mmig.addMethod(CtNewMethod.make("""
public static boolean keyAt(String body, String key) {
  int n = body.length();
  int i = 0;
  while (i < n && isWs(body.charAt(i))) i++;
  if (!body.startsWith(key, i)) return false;
  int j = i + key.length();
  if (j >= n) return true;
  char c = body.charAt(j);
  return c == '=' || c == ':' || isWs(c);
}""", mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean contLine(String body) {
  int k = 0;
  int i = body.length() - 1;
  while (i >= 0 && body.charAt(i) == '\\\\') { k++; i--; }
  return k %% 2 == 1;
}""", mmig))
mmig.addMethod(CtNewMethod.make("""
public static boolean commentOrBlank(String body) {
  int n = body.length();
  int i = 0;
  while (i < n && isWs(body.charAt(i))) i++;
  return i >= n || body.charAt(i) == '#' || body.charAt(i) == '!';
}""", mmig))
# the untouched 0.4.7 pair: mana.magicBase absent or exactly 20, mana.magicClasses absent or exactly the classes Mage and Priest (any order /
# case, nothing else - an unknown name counts as an admin's edit)
mmig.addMethod(CtNewMethod.make(f"""
public static boolean untouched(String mb, String mc) {{
  if (mb != null) {{
    double v = Double.NaN;
    try {{ v = Double.parseDouble(mb.trim()); }} catch (Throwable t) {{ return false; }}
    if (v != 20.0) return false;
  }}
  if (mc != null) {{
    if ({PKG}.OverallCfg.badClass(mc) != null) return false;
    String[] c = {PKG}.OverallCfg.parseClasses(mc);
    if (c.length != 2) return false;
    boolean m = false;
    boolean pr = false;
    for (int i = 0; i < c.length; i++) {{ if (c[i].equals("Mage")) m = true; if (c[i].equals("Priest")) pr = true; }}
    if (!m || !pr) return false;
  }}
  return true;
}}""", mmig))
# after = before without the old keys + exactly the table entries
mmig.addMethod(CtNewMethod.make(f"""
public static boolean sameAfterMove(java.util.Properties before, java.util.Properties after, Object[] t) {{
  String[] c = (String[]) t[0];
  double[] b = (double[]) t[1];
  int gone = (before.getProperty(OLD_BASE) != null ? 1 : 0) + (before.getProperty(OLD_CLS) != null ? 1 : 0);
  if (after.size() != before.size() - gone + c.length) return false;
  if (after.getProperty(OLD_BASE) != null || after.getProperty(OLD_CLS) != null) return false;
  java.util.Iterator it = before.stringPropertyNames().iterator();
  while (it.hasNext()) {{
    String k = (String) it.next();
    if (k.equals(OLD_BASE) || k.equals(OLD_CLS)) continue;
    String y = after.getProperty(k);
    if (y == null || !y.equals(before.getProperty(k))) return false;
  }}
  for (int i = 0; i < c.length; i++) {{
    String y = after.getProperty({PKG}.OverallCfg.TABLE_PREFIX + c[i]);
    if (y == null || !y.equals({PKG}.DivCfg.num(b[i]))) return false;
  }}
  return true;
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String[] res(String level, String msg) {{
  if ("info".equals(level)) {PKG}.SkillCfg.info(msg);
  else if ("warn".equals(level)) {PKG}.SkillCfg.warn(msg);
  return new String[] {{ level, msg }};
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String cut(String v, int n) {{
  String t = v.trim();
  return t.length() > n ? t.substring(0, n) + "..." : t;
}}""", mmig))
mmig.addMethod(CtNewMethod.make(f"""
public static String[] run() {{
  java.nio.file.Path f = {PKG}.SkillCfg.FILE;
  if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return new String[] {{ "", "no xp.properties yet" }};
  byte[] old = null;
  java.util.Properties before = new java.util.Properties();
  try {{
    old = java.nio.file.Files.readAllBytes(f);
    before.load(new java.io.ByteArrayInputStream(old));
  }} catch (Throwable t) {{
    return res("warn", "could not read " + f + " to move mana.magicBase / mana.magicClasses to Base Mana by class: " + t + " - the next start tries again");
  }}
  String mb = before.getProperty(OLD_BASE);
  String mc = before.getProperty(OLD_CLS);
  if (mb == null && mc == null) return new String[] {{ "", "nothing to move" }};
  if ({PKG}.OverallCfg.anyTableKey(before)) return new String[] {{ "", "Base Mana by class is already in the file - the old lines are left alone" }};
  boolean keep0 = untouched(mb, mc);
  Object[] t = null;
  if (keep0) t = {PKG}.OverallCfg.defTable();
  else t = {PKG}.OverallCfg.legacyTable(before);
  String tt = ((String) t[2]).length() > 0 ? (String) t[2] : "no class (every class starts at mana.base)";
  String pair = OLD_BASE + "=" + (mb == null ? "(no line)" : cut(mb, 40)) + " + " + OLD_CLS + "=" + (mc == null ? "(no line)" : cut(mc, 80));
  String badc = mc == null ? null : {PKG}.OverallCfg.badClass(mc);
  String keep = " - until then they are read as Base Mana by class " + ((String) {PKG}.OverallCfg.legacyTable(before)[2]) + " and the next start tries again";
  try {{
    String text = new String(old, "ISO-8859-1");
    String[] lines = text.split("\\n", -1);
    java.util.ArrayList out = new java.util.ArrayList();
    int hits = 0;
    int docs = 0;
    boolean stale = false;
    int headAt = -1;
    String headE = "";
    boolean cont = false;
    boolean contHit = false;
    String[] tc = (String[]) t[0];
    double[] tb = (double[]) t[1];
    for (int i = 0; i < lines.length; i++) {{
      String l = lines[i];
      boolean cr = l.endsWith("\\r");
      String body = cr ? l.substring(0, l.length() - 1) : l;
      if (cont) {{ cont = contLine(body); out.add(l); continue; }}
      if (docAt(lines, i)) {{
        // the untouched 0.4.6 / 0.4.7 comment about the old keys -> the 0.4.8 comment (line ending of its first line)
        String de = cr ? "\\r" : "";
        for (int k = 0; k < DOC_NEW.length; k++) out.add(DOC_NEW[k] + de);
        docs++;
        i += DOC_OLD.length - 1;
        continue;
      }}
      if (commentOrBlank(body)) {{
        if (body.indexOf(OLD_BASE) >= 0 || body.indexOf(OLD_CLS) >= 0) stale = true;
        out.add(l);
        continue;
      }}
      boolean hit = keyAt(body, OLD_BASE) || keyAt(body, OLD_CLS);
      cont = contLine(body);
      if (!hit) {{ out.add(l); continue; }}
      if (cont) contHit = true;
      if (hits == 0) {{
        String e = cr ? "\\r" : "";
        String why = keep0 ? "the old defaults, now Skyy's 0.4.8 default" : "an admin's values, kept";
        String[] ec = {PKG}.OverallCfg.parseClasses(mc == null ? "Mage,Priest" : mc);
        double eb = {PKG}.OverallCfg.clampD({PKG}.SkillCfg.dbl(before, OLD_BASE, 20.0), 20.0, 0.0, 10000.0);
        out.add("# Base Mana by class (SkyySkills 0.4.8) replaced " + OLD_BASE + "=" + {PKG}.DivCfg.num(eb) + " + " + OLD_CLS + "=" + {PKG}.OverallCfg.join(ec, ",") + " (" + why + "):" + e);
        headAt = out.size() - 1;
        headE = e;
        for (int k = 0; k < tc.length; k++) out.add({PKG}.OverallCfg.TABLE_PREFIX + tc[k] + "=" + {PKG}.DivCfg.num(tb[k]) + e);
        if (tc.length == 0) out.add("# (no class listed - every class starts at mana.base)" + e);
      }}
      hits++;
    }}
    if (contHit) return res("warn", "xp.properties: a " + OLD_BASE + " / " + OLD_CLS + " line continues on the next line (a trailing backslash) - not moved to Base Mana by class" + keep);
    if (hits == 0) return res("warn", "xp.properties: the " + OLD_BASE + " / " + OLD_CLS + " lines could not be found to rewrite" + keep);
    // an admin's own comment (or an edited copy of the old one) still names the old keys: say under the new comment line that it is stale
    if (stale && headAt >= 0) out.add(headAt + 1, STALE_NOTE + headE);
    String chg = "only those lines" + (docs > 0 ? " and the 0.4.7 Base Mana comment" : "") + " changed" + (stale ? " (a note under the new comment says other comments naming the old keys are stale)" : "");
    StringBuilder sb = new StringBuilder(text.length() + 256);
    for (int i = 0; i < out.size(); i++) {{
      if (i > 0) sb.append('\\n');
      sb.append((String) out.get(i));
    }}
    byte[] nb = sb.toString().getBytes("ISO-8859-1");
    java.util.Properties after = new java.util.Properties();
    after.load(new java.io.ByteArrayInputStream(nb));
    if (!sameAfterMove(before, after, t)) return res("warn", "xp.properties: moving " + OLD_BASE + " / " + OLD_CLS + " would change more than those lines - nothing written" + keep);
    {PKG}.CfgRows.atomicWrite(f, nb);
    BEFORE = old;
    if (keep0) return res("info", "xp.properties: " + pair + " (the untouched 0.4.7 defaults) became Base Mana by class " + tt + " (the 0.4.8 default); " + chg + ".");
    return res("info", "xp.properties: " + pair + " had been changed by an admin - kept as Base Mana by class " + tt + (badc != null ? " (" + cut(badc, 40) + " is not a class - left out)" : "") + "; the 0.4.8 default " + (String) {PKG}.OverallCfg.defTable()[2] + " was NOT applied (Server Setup > Skills > Overall and Mana > Base Mana by class). " + chg.substring(0, 1).toUpperCase() + chg.substring(1) + ".");
  }} catch (Throwable x) {{
    return res("warn", "could not move " + OLD_BASE + " / " + OLD_CLS + " in " + f + " to Base Mana by class: " + x + keep);
  }}
}}""", mmig))
# setup(), right after CfgPub.start: the pre-move file becomes one entry of the kit's own history (config-history/, the Server Setup
# History view - restorable there like any in-game change; KEEP 10 per file). Under the kit's save monitor like its own snapshots; no
# kit monitor is held. Returns the history file name ("" = nothing to keep or it failed - the move itself stays done either way).
mmig.addMethod(CtNewMethod.make(f"""
public static String keepCopy() {{
  byte[] b = BEFORE;
  BEFORE = null;
  if (b == null) return "";
  try {{
    int fi = -1;
    for (int k = 0; k < {PKG}.CfgRows.FILES.length; k++) if ({PKG}.CfgRows.FILES[k].endsWith("/xp.properties")) fi = k;
    if (fi < 0 || {PKG}.CfgHist.DIR == null) return "";
    String st = {PKG}.CfgHist.stamp();
    synchronized ({PKG}.CfgSaveTask.class) {{
      {PKG}.CfgHist.snapshot(fi, b, st, WHO, WHAT);
    }}
    String[] have = {PKG}.CfgHist.list(fi);
    for (int k = have.length - 1; k >= 0; k--) {{
      byte[] c = java.nio.file.Files.readAllBytes({PKG}.CfgHist.bak(fi, have[k]));
      if (java.util.Arrays.equals(c, b)) {{
        String n = {PKG}.CfgHist.bak(fi, have[k]).getFileName().toString();
        {PKG}.SkillCfg.info("xp.properties: the file as it was before the Base Mana by class move is kept in the config history (" + n + ") - Server Setup > Skills > History can restore it.");
        return n;
      }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not keep a history copy of xp.properties from before the Base Mana by class move: " + t); }}
  return "";
}}""", mmig))

# ---- ManaGuard (point 3): WARN once per class whose base Mana is below the Mana cost of a weapon in its class kit. Scheduler thread
# (SkillTick) - bridge reads, the config kit's read-only "get" op of SkyyClasses and logging only; never a number changed, never the world.
mgd = pool.makeClass(PKG + ".ManaGuard")
mgd.addField(CtField.make("public static final String[] FB_CLS = %%s;" %% jarr([_c for _c, _k in KIT_FALLBACK]), mgd))
mgd.addField(CtField.make("public static final String[] FB_KIT = %%s;" %% jarr([_k for _c, _k in KIT_FALLBACK]), mgd))
mgd.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();", mgd))
mgd.addField(CtField.make('public static volatile String LAST = "";', mgd))
mgd.addField(CtField.make("public static volatile long EPOCH = -2L;", mgd))
mgd.addField(CtField.make("public static volatile boolean STARTED = false;", mgd))
mgd.addField(CtField.make("public static final long START_S = 10L;", mgd))   # every other plugin has published its bridge keys by then
mgd.addMethod(CtNewMethod.make(f"""
public static java.util.function.Function classesFn() {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("config:fn:SkyyClasses");
    if (o instanceof java.util.function.Function) return (java.util.function.Function) o;
  }} catch (Throwable t) {{ }}
  return null;
}}""", mgd))
# a SkyyClasses setting's current value text through the config kit's read-only "get" op (CONFIG-CONTRACT), null = no SkyyClasses /
# no such row / any error. Rows used: kit.<Class> (items text "Weapon_Staff_Wood:1") and kits.enabled (the Class kits part switch)
mgd.addMethod(CtNewMethod.make("""
public static String liveGet(java.util.function.Function f, String key) {
  if (f == null) return null;
  try {
    Object o = f.apply(new Object[] { "get", key });
    if (o instanceof String) return (String) o;
  } catch (Throwable t) { }
  return null;
}""", mgd))
mgd.addMethod(CtNewMethod.make("""
public static String liveKit(java.util.function.Function f, String cls) {
  return liveGet(f, "kit." + cls);
}""", mgd))
mgd.addMethod(CtNewMethod.make("""
public static String fbKit(String cls) {
  for (int i = 0; i < FB_CLS.length; i++) if (FB_CLS[i].equals(cls)) return FB_KIT[i];
  return "";
}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static long classesEpoch() {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("config:epoch:SkyyClasses");
    if (o instanceof Number) return ((Number) o).longValue();
  }} catch (Throwable t) {{ }}
  return -1L;
}}""", mgd))
# ---- pack check (review 2026-09-30 finding 3): which asset pack the game's item assets take each overridden item from. Of two packs
# with the same item the one loaded last wins (DefaultAssetMap keeps a chain of packs per id; getAssetPack = the winner, read under its
# own StampedLock). Once, from START_S on; retried every 10 s up to PACK_MAX times while the item assets cannot be read (a bare JVM, or
# not loaded yet). One INFO (all active) or one WARN (another pack wins for some); it never changes anything.
B.probe(pool, "com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetPack")
_pkm = B.manifest("SkyySkills", VERSION, "", "")
SKILLS_PACK = "%%s:%%s" %% (_pkm["Group"], _pkm["Name"])   # the pack key the engine gives this jar (PluginIdentifier = Group:Name)
mgd.addField(CtField.make('public static final String PACK = "%%s";' %% SKILLS_PACK, mgd))
mgd.addField(CtField.make("public static volatile boolean PACK_DONE = false;", mgd))
mgd.addField(CtField.make("public static volatile int PACK_TRIES = 0;", mgd))
mgd.addField(CtField.make("public static final int PACK_MAX = 6;", mgd))
mgd.addField(CtField.make('public static volatile String PACK_LAST = "";', mgd))
# packs[i] = the pack the item assets name for ManaCost.IDS[i] (null = not there / not readable) -> {level "info" / "warn" / "" (nothing
# readable - try again), message}
mgd.addMethod(CtNewMethod.make(f"""
public static String[] packReport(String[] packs) {{
  String[] ids = {PKG}.ManaCost.IDS;
  int mine = 0;
  int other = 0;
  int miss = 0;
  StringBuilder ot = new StringBuilder();
  StringBuilder ms = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    if (p == null) {{
      miss++;
      if (miss <= 8) {{ if (ms.length() > 0) ms.append(", "); ms.append(ids[i]); }}
      continue;
    }}
    if (p.equals(PACK)) {{ mine++; continue; }}
    other++;
    if (other <= 8) {{ if (ot.length() > 0) ot.append(", "); ot.append(ids[i]).append(" (").append(p).append(")"); }}
  }}
  if (mine + other == 0) return new String[] {{ "", "the game's item assets could not be read" }};
  String pre = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": ";
  String mt = miss > 0 ? "; " + miss + " not in the game's item assets (" + ms.toString() + (miss > 8 ? ", ..." : "") + ")" : "";
  if (other == 0) return new String[] {{ "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " item overrides are active (the game's item assets take them from " + PACK + ")" + mt }};
  return new String[] {{ "warn", pre + other + " of " + ids.length + " item overrides are NOT active - another asset pack wins for " + ot.toString() + (other > 8 ? ", ..." : "") + ". Those items keep that pack's Mana cost (of two packs with the same item, the one loaded last wins); " + mine + " active" + mt + "." }};
}}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static String[] packCheck() {{
  String[] ids = {PKG}.ManaCost.IDS;
  String[] ps = new String[ids.length];
  try {{
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = {ITM}.getAssetMap();
    if (m != null) {{
      for (int i = 0; i < ids.length; i++) {{
        try {{ ps[i] = m.getAssetPack(ids[i]); }} catch (Throwable t) {{ ps[i] = null; }}
      }}
    }}
  }} catch (Throwable t) {{ }}
  return packReport(ps);
}}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static void packTick() {{
  String[] r = packCheck();
  PACK_TRIES++;
  if (r[0].length() > 0) {{
    PACK_DONE = true;
    PACK_LAST = r[1];
    if ("warn".equals(r[0])) {PKG}.SkillCfg.warn(r[1]);
    else {PKG}.SkillCfg.info(r[1]);
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    PACK_LAST = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": the game's item assets could not be read to see which pack each of the " + {PKG}.ManaCost.N + " overridden items comes from - not checked";
    {PKG}.SkillCfg.info(PACK_LAST);
  }}
}}""", mgd))
# the lines it logged this call (WARNs first, then the INFO summary when it changed); tests call it directly
mgd.addMethod(CtNewMethod.make(f"""
public static String[] run() {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.function.Function f = classesFn();
  if ("false".equals(liveGet(f, "kits.enabled"))) {{
    // SkyyClasses gives no class kit at all: no kit weapon to check (checked again when SkyyClasses' config changes)
    WARNED.clear();
    String off = "Base Mana check (kits from SkyyClasses, spell costs /" + {PKG}.ManaCost.DIVISOR + "): class kits are off in SkyyClasses (Server Setup > Classes > Class kits) - no kit weapon to check";
    if (!off.equals(LAST)) {{
      LAST = off;
      {PKG}.SkillCfg.info(off);
      out.add(off);
    }}
    String[] r0 = new String[out.size()];
    for (int i = 0; i < r0.length; i++) r0[i] = (String) out.get(i);
    return r0;
  }}
  StringBuilder ok = new StringBuilder();
  int failed = 0;
  int weapons = 0;
  for (int k = 0; k < {PKG}.SkillDefs.CLASSES.length; k++) {{
    String cls = {PKG}.SkillDefs.CLASSES[k];
    String kit = liveKit(f, cls);
    boolean live = kit != null;
    if (kit == null) kit = fbKit(cls);
    double base = {PKG}.OverallCfg.MANA_ON ? {PKG}.OverallCfg.baseFor(cls) : 0.0;
    String[] ps = kit.split(",");
    StringBuilder badW = new StringBuilder();
    StringBuilder okW = new StringBuilder();
    StringBuilder sig = new StringBuilder();
    for (int i = 0; i < ps.length; i++) {{
      String id = ps[i].trim();
      int c = id.indexOf(':');
      if (c >= 0) id = id.substring(0, c).trim();
      if (id.length() == 0) continue;
      int cost = {PKG}.ManaCost.costOf(id);
      if (cost <= 0) continue;
      weapons++;
      if (base + 0.000001 < (double) cost) {{
        if (badW.length() > 0) badW.append(", ");
        badW.append(id).append(" costs ").append(cost);
        sig.append(id).append(':').append(cost).append(',');
      }} else {{
        long casts = (long) Math.floor(base / (double) cost + 0.000001);
        if (okW.length() > 0) okW.append(", ");
        okW.append(id).append(" ").append(cost).append(" (").append(casts).append(casts == 1L ? " cast)" : " casts)");
      }}
    }}
    if (badW.length() > 0) {{
      failed++;
      String s = {PKG}.DivCfg.num(base) + "|" + sig.toString() + ({PKG}.OverallCfg.MANA_ON ? "on" : "off");
      Object prev = WARNED.put(cls, s);
      if (prev == null || !prev.equals(s)) {{
        String m = "Base Mana check: " + cls + ({PKG}.OverallCfg.MANA_ON ? " starts with " + {PKG}.DivCfg.num(base) + " max Mana" : " starts with 0 max Mana (the Base Mana part is off)") + ", but the kit weapon " + badW.toString() + " Mana per cast (kit from " + (live ? "SkyyClasses" : "the built-in table") + ") - a new " + cls + " cannot cast it. Raise " + cls + " in Server Setup > Skills > Overall and Mana > Base Mana by class. Nothing was changed automatically.";
        {PKG}.SkillCfg.warn(m);
        out.add(m);
      }}
    }} else {{
      WARNED.remove(cls);
      if (okW.length() > 0) {{
        if (ok.length() > 0) ok.append(", ");
        ok.append(cls).append(" ").append({PKG}.DivCfg.num(base)).append(" Mana >= ").append(okW.toString());
      }}
    }}
  }}
  String body = ok.length() > 0 ? ok.toString() : (weapons == 0 ? "no class kit holds a Mana weapon" : "none");
  String info = "Base Mana check (" + (f != null ? "kits from SkyyClasses" : "built-in kit table - SkyyClasses not found") + ", spell costs /" + {PKG}.ManaCost.DIVISOR + "): " + body + (failed > 0 ? "; " + failed + " class(es) below their kit weapon's Mana cost (see the WARN)" : "");
  if (!info.equals(LAST)) {{
    LAST = info;
    {PKG}.SkillCfg.info(info);
    out.add(info);
  }}
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}}""", mgd))
# SkillTick (every second): from START_S on, once at start, then whenever a config load marked it dirty or SkyyClasses' config changed;
# the pack check runs first, at START_S and every 10 s after until it has an answer (at most PACK_MAX tries)
mgd.addMethod(CtNewMethod.make(f"""
public static void tick(long n) {{
  if (n < START_S) return;
  if (!PACK_DONE && (n - START_S) %% 10L == 0L) packTick();
  long e = classesEpoch();
  if (STARTED && !{PKG}.OverallCfg.GUARD_DIRTY && e == EPOCH) return;
  {PKG}.OverallCfg.GUARD_DIRTY = false;
  STARTED = true;
  EPOCH = e;
  run();
}}""", mgd))
''' % (KIT_FALLBACK, OLD_DOC)
rep('''               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: curve size % and max level.")
''', '''               NOTE="Hand edits of xp.properties: /skills reload. Levels tab: curve size % and max level.")
''' + MANA_JAVA)

# ---------------------------------------------------------------------------------------------------------------- SkillKit custom ro row
rep('''public static String customGet(String key) {
  long[] l = curList();''', '''public static String customGet(String key) {
  if ("spell.manaDivisor".equals(key)) return String.valueOf(""" + PKG + """.ManaCost.DIVISOR);
  long[] l = curList();''')

# ---------------------------------------------------------------------------------------------------------------- SkillTick + setup
rep('''  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} try {{ {PKG}.PartyXp.retainOnline(); }} catch (Throwable t) {{ }} }}
}}""", tick))''', '''  if (this.n % 30L == 0L) {{ try {{ {PKG}.Acro.retainOnline(); }} catch (Throwable t) {{ }} try {{ {PKG}.PartyXp.retainOnline(); }} catch (Throwable t) {{ }} }}
  try {{ {PKG}.ManaGuard.tick(this.n); }} catch (Throwable t) {{ }}
}}""", tick))''')
rep('''  {PKG}.SkillCfg.FILE = base.resolve("xp.properties");
  String rules = {PKG}.SkillCfg.load();''', '''  {PKG}.SkillCfg.FILE = base.resolve("xp.properties");
  {PKG}.ManaMig.run();   // 0.4.8: mana.magicBase / mana.magicClasses -> Base Mana by class, once, before the file is read and the kit starts
  String rules = {PKG}.SkillCfg.load();''')
rep('''  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
''', '''  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
  {PKG}.ManaMig.keepCopy();   // 0.4.8: the pre-move xp.properties into the kit's history (only after a move this start)
''')
rep('''"; overall level " + {PKG}.OverallCfg.text() + "; bridge skill:fn:addxp''',
    '''"; overall level " + {PKG}.OverallCfg.text() + "; spell costs /" + {PKG}.ManaCost.DIVISOR + " (" + {PKG}.ManaCost.N + " items)" + "; bridge skill:fn:addxp''')
rep('''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss, ovc, ovl, ofn, opg):''',
    '''          fcf, fdf, frd, fsn, fwt, fel, fdr, fcr, ffn, esy, pcg, pxp, pft, skit, karm, dvc, hxp, hfn, xcf, xst, xbw, xss, ovc, ovl, ofn, opg,
          mcost, mmig, mgd):''')

# ---------------------------------------------------------------------------------------------------------------- manifest + asset pack
rep('''Base Mana for every player (magic users more) and an Overall Level''',
    '''Spells cost the vanilla Mana / 5 (wand 5, staff 10, spellbook 20: item overrides generated at build time) and Mages and Priests can cast their starter weapons from level 1 (Base Mana 10, Mage and Priest 30 - Base Mana by class in Server Setup); an Overall Level''')
rep('''m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: page built inline (see memory hytale-ui-rules)
''', '''m["IncludesAssetPack"] = True   # 0.4.8: the spell cost item overrides (SPELL_FILES); the pages stay inline (no .ui files)
assert SPELL_FILES and all(_p.startswith("Server/Item/Items/") for _p in SPELL_FILES) and not any(_p.endswith(".ui") for _p in SPELL_FILES)
assert "%s:%s" % (m["Group"], m["Name"]) == SKILLS_PACK, (m["Group"], m["Name"], SKILLS_PACK)   # the pack ManaGuard's pack check expects
B.assemble(jar, m, OUT, SPELL_FILES)
''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
assert "MAGIC_BASE" not in s and "OverallCfg.MAGIC" not in s and "mana.magicBase=20" not in s.split("# >>> SPELL GEN")[0].split("OVL_L = []")[1][:3000]
assert s.count("ManaMig.run();") == 1 and s.count("ManaGuard.tick(this.n)") == 1 and s.count("B.assemble(jar, m, OUT, SPELL_FILES)") == 1
assert s.count("ManaMig.keepCopy();") == 1 and s.index("ManaMig.keepCopy();") > s.index("CfgPub.start(getDataDirectory")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
