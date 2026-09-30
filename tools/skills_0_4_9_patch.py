"""Derive SkyySkills/build_skyyskills_0.4.9.py from the LIVE generated SkyySkills/build_skyyskills_0.4.8.py (= the tools/deploy_set.py SET
pin since 2026-09-30 11:21; 0.4.8 came from 0.4.7 by tools/skills_0_4_8_patch.py, 0.4.7 from 0.4.6 by skills_0_4_7_patch.py, 0.4.6 from
Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run skills_0_4_5 or older patches). Same style as skills_0_4_8_patch.py: rep(old, new) /
cut(a, b, new) with asserted single anchors, newline-agnostic; 0.4.8 stays untouched and its line endings are kept. Edit THIS file, never
the generated script.
Run:  python tools/skills_0_4_9_patch.py   then   python SkyySkills/build_skyyskills_0.4.9.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.9.py   (bare JVM, -Xverify:all; scratch under tools/dev/scratch/, deleted afterwards)

0.4.9 = EVERY CAST CHECKS WHAT IT SPENDS (Skyy play-tested 0.4.8, 2026-09-30: "the wand spell only costs 5 mana. but you still have to be
above 25 mana to actually cast it."). research/Mana-Cost-And-Regen-Research.md 1.1-1.4 (HytaleServer 0.6.8 bytecode): the Mana CHECK of
a charged cast is the StatsCondition interaction asset the weapon's Charging step names directly (Wand_Primary -> "Wand_Cast_Left_Charged",
Costs.Mana 25). A string is resolved in the global interaction asset map (ChargingInteraction.compile -> Interaction.getInteractionOrUnknown)
- the held item is never asked; an item's InteractionVars are read ONLY by a Replace interaction naming that var. No Replace names
Wand_Cast_Left_Charged / Staff_Cast_Summon_Charged / Spellbook_Cast_Hurl_Charged / Gun_Shoot_Flintlock_Charged, so the item vars 0.4.8 cut
(25 -> 5 ...) are dead data, while the drain vars ARE read by a Replace (that is why a wand cast spent 5 but needed 25).
  1. CAST CHECK = SPEND. The build-time generator (SPELL GEN block, Assets.zip read in memory, nothing committed) now also overrides the
     interaction assets (Server/Item/Interactions/**, same path + id as vanilla, this jar's pack wins like the 0.4.8 items), and keeps the
     32 item overrides of 0.4.8 unchanged:
       Wand_Cast_Left_Charged        Costs.Mana 25 -> 5    (the wands spend 5)
       Spellbook_Cast_Hurl_Charged   Costs.Mana 25 -> 20   (the spellbooks spend 20 - vanilla itself checked 25 and spent 100)
       Gun_Shoot_Flintlock_Charged   Costs.Mana 50 -> 10   (the Rusty blunderbuss spends 10; the plain Weapon_Gun_Blunderbuss spends 0 in
                                     vanilla and still does, so it now needs 10 Mana present to fire - vanilla needed 50)
       Staff_Cast_Summon_Charged     Type Simple -> StatsCondition + Costs.Mana 10 (a staff had NO check at all: it cast for free at 0
                                     Mana; the keys are exactly the wand check's - RunTime / Next / Failed stay, Failed = the vanilla
                                     Staff_Cast_Fail click). Side effect (research 1.4 #4): Crystal_Red and Crystal_Ice (whose Primary
                                     leads into Staff_Primary) spend 0 Mana but now need 10 Mana present to cast. With the plain
                                     Blunderbuss above, 3 items check 10 and spend 0 (the gate simulation lists them; Crystal_Ice's
                                     Secondary bolt is not gated and stays Mana-free).
       Wand_Cast_Cost / Staff_Cast_Cost / Spellbook_Cast_Cost   StatModifiers.Mana -25 -> -5, Gun_Shoot_Cost -75 -> -15 (the default
                                     drains: the Replace DefaultValue and the Parent of every item drain var; no vanilla caster spends
                                     the default today, but "everything / 5" then holds for another mod's item on these steps too)
     The check number is not typed in: it is the one number every item behind that check spends (after the item overrides), so the check
     cannot drift from the spend. Self-checks stop the build: the eight ids exist, have no Parent, carry exactly one top-level Mana
     number (or, for the Simple staff step, only the wand check's keys + Next + Failed); every Mana number in Server/Item/Interactions and
     RootInteractions is one of these or an unreferenced test asset (Tests/StatsCondition); the generated JSON equals vanilla except that
     number (path by path; with the old number put back - and for the staff Costs removed + Type Simple - it IS vanilla); no interaction
     inherits a converted step by Parent; no asset outside Server/Item (NPC roles, entities, drops, ...) names one of the overridden
     interactions or the Charging steps that lead to them (mobs keep their own attacks); no other Skyy mod of the live set or pack mod
     ships one of these files. THE GATE SIMULATION (spell_casts / spell_verify, the engine's rules above) walks every item of Assets.zip
     through its slots -> root -> Charging -> charged step -> Replace vars, on vanilla and on the final assets: every Mana spend sits behind
     a Mana check, each check = what that cast spends = the vanilla spend / 5, a check only ever comes from a charged cast step asset (a
     var named like one is never used), one check per item, and items that spend 0 are listed. 0.4.8's spell_leaks (built on the wrong
     model "an item var named like an interaction replaces it") is replaced by it.
  2. GUARD: ManaCost gets the REAL gate table from that simulation (34 items: the 32 overridden + Crystal_Red + Crystal_Ice): per item the
     check it must pass (GATE) and what a cast spends (SPEND), plus the vanilla numbers. ManaCost.costOf = the real check (0.4.8 returned
     the dead var number); ManaGuard WARNs when a class's base Mana is below its kit weapon's check, and its INFO counts casts from full with
     check and spend ("needs 10 Mana to cast (it spends 0)" for a free item behind a check). PACK CHECK (same tick, same retries): also
     which pack the game's INTERACTION assets take each of the 8 overridden interactions from (Interaction.getAssetMap().getAssetPack) and
     the live Mana check of each of the 4 cast checks as the engine's gate uses it (the RESOLVED StatsConditionBaseInteraction.costs entry
     of the Mana stat index; the decoded rawCosts only tells "no Mana cost" apart) - one INFO when all are this jar's and equal the spend,
     else one WARN. Every Interaction load rebuilds every root (InteractionModule.
     handledLoadedInteractions -> RootInteraction.build), so the compiled Charging steps use the asset map's winner.
  3. Mana regen is NOT changed (the research proves none of our effects broken; vanilla: +1 every 0.2 s, 6 s after the last damage taken,
     not while charging).
Everything else (commands, pages, bridge keys, players files, config rows, ManaMig, the max Mana path) is 0.4.8's - asserted below and by
the harness (class bytes 0.4.8 vs 0.4.9).
REVIEW ROUND (2026-09-30, verdict PASS, low findings only): the plain Blunderbuss named next to Crystal_Red / Crystal_Ice (3 items check 10,
spend 0); ManaGuard.liveCheck reports the RESOLVED costs entry of the Mana stat (what canAfford reads) and -4 when a decoded Mana cost did
not resolve; ready line / manifest say "every paid cast"; the harness also decodes the 8 generated files through the engine's own
Interaction codec (section E). No number and no generated asset changed.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.8.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.9.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.8"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
# the source must be the generated 0.4.8 of the EDITED lineage
assert 'VERSION = "0.4.8"' in s and "derived from the generated 0.4.7 by tools/skills_0_4_8_patch.py" in s, "not the live generated 0.4.8"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
REG0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
BIND0 = [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln]


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:120]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:120])
    s = s.replace(old, new)


def cut(a, b, new):
    """replace s[index(a) : index(b)] (b itself stays) with new"""
    global s
    assert s.count(a) == 1 and s.count(b) == 1 and s.index(a) < s.index(b), (a[:60], b[:60])
    s = s[:s.index(a)] + new + s[s.index(b):]


def block(a, b):
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# blocks that must come out of this patch byte-identical: the pages, the Overall / OverallCfg code, the XP / perk code, the item plan of
# SPELL GEN and ManaMig (the migration must not change - Skyy's live file was already moved by 0.4.8)
KEEP = [block("# ================= /skills page (inline", "# ================= OverallPage (0.4.6)"),
        block("# ================= BridgeCfg (0.4)", "# ================= Overall (0.4.6)"),
        block('# a copy of StatsPage.num (StatsPage is compiled later)', "public static boolean magic(java.util.UUID u) {{"),
        block("# ms since this session's first Perks.ovl", "public static String magicText() {{"),
        block("perk.addMethod(CtNewMethod.make(f\"\"\"\npublic static void mod(", "# drops that depend on the held tool"),
        block("# ================= OverallPage (0.4.6)", "# 0.4.6 (research/Overall-Level-Spec.md 4.9): the \"Overall and Mana\" category"),
        block("def spell_new(v, div):", "def spell_leaks(items, ints, roots):"),
        block("# ---- ManaMig (point 2)", "# ---- ManaGuard (point 3)"),
        block("# 0.4.8 Base Mana by class (tools/skills_0_4_8_patch.py point 2)", "ovc.addMethod(CtNewMethod.make(f\"\"\"\npublic static void read(")]

# ---------------------------------------------------------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.8 - build script (derived from the generated 0.4.7 by tools/skills_0_4_8_patch.py - edit the patch, not this file;
0.4.7 was derived''', '''"""SkyySkills 0.4.9 - build script (derived from the generated 0.4.8 by tools/skills_0_4_9_patch.py - edit the patch, not this file;
0.4.8 was derived from the generated 0.4.7 by tools/skills_0_4_8_patch.py; 0.4.7 was derived''')
HEAD_049 = '''0.4.9: EVERY CAST CHECKS WHAT IT SPENDS (Skyy 2026-09-30 play test of 0.4.8: "the wand spell only costs 5 mana. but you still have to be
  above 25 mana to actually cast it."; full notes in tools/skills_0_4_9_patch.py, research/Mana-Cost-And-Regen-Research.md). The Mana CHECK of
  a charged cast is the StatsCondition interaction the weapon's Charging step names (the engine resolves that name in the global interaction
  assets; an item's InteractionVars are read only by a Replace naming the var), so the item vars 0.4.8 cut were dead data. This jar now
  also carries GENERATED overrides of those interactions (Assets.zip read in memory at every build, never checked into git):
    Wand_Cast_Left_Charged 25 -> 5, Spellbook_Cast_Hurl_Charged 25 -> 20, Gun_Shoot_Flintlock_Charged 50 -> 10, Staff_Cast_Summon_Charged
    no check (Simple: staffs cast for free at 0 Mana) -> a StatsCondition checking 10; the default drains Wand / Staff / Spellbook_Cast_Cost
    -25 -> -5 and Gun_Shoot_Cost -75 -> -15. The check number = the one number the items behind it spend (so it cannot drift). Crystal_Red
    and Crystal_Ice spend 0 but now need 10 Mana present (they sit behind the staff check), and so does the plain Weapon_Gun_Blunderbuss
    (behind the flintlock check; vanilla needed 50). Self-checked (SPELL GEN): only that number
    changes, the eight ids / shapes, no Mana number anywhere else in the interactions, nothing outside Server/Item names them (mobs keep
    their attacks), no clash with another Skyy mod or pack mod, and a GATE SIMULATION of every item on vanilla and on the final assets
    (every spend behind a check, check = spend = vanilla spend / 5). The 32 item overrides of 0.4.8 stay as they were.
  GUARD: ManaCost holds the REAL check and spend per item (34 items, from the simulation); ManaGuard compares base Mana with the real check.
    Pack check: also which pack the game's interaction assets take the 8 overrides from + the live Mana check of each cast check (the
    engine's resolved costs entry, what the gate compares).
  Mana regen unchanged (vanilla +1 every 0.2 s after 6 s without damage, not while charging).
'''
rep('''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
0.4.8: MAGIC THAT WORKS AT LEVEL 1''', '''by tools/skills_0_3_2_patch.py, 0.3 from 0.2 by tools/skills_0_3_patch.py)
''' + HEAD_049 + '''0.4.8: MAGIC THAT WORKS AT LEVEL 1''')
rep('VERSION = "0.4.8"\n', 'VERSION = "0.4.9"\n')

# ---------------------------------------------------------------------------------------------------------------- SPELL GEN: header note
rep('''# difference is those Mana numbers / SPELL_DIVISOR. No game file is checked into git; every self-check fails the build.
''', '''# difference is those Mana numbers / SPELL_DIVISOR. No game file is checked into git; every self-check fails the build.
# 0.4.9 (tools/skills_0_4_9_patch.py point 1): those item vars only set what a cast SPENDS - the cast CHECK is the charged cast step's own
# interaction asset (Wand_Cast_Left_Charged ...; the engine resolves a string in the global interaction assets, an item var is read only by a
# Replace naming it). spell_int_plan overrides those interactions too (check = the one number the items behind it spend; the Simple staff
# step becomes a StatsCondition; the default drains / SPELL_DIVISOR) and spell_verify simulates every cast on vanilla and on the final assets.
''')
rep('''SPELL_SKIP_BLOCKS = ("InteractionVars", "Armor", "Weapon")   # Armor / Weapon StatModifiers Mana are max-Mana bonuses, not costs
''', '''SPELL_SKIP_BLOCKS = ("InteractionVars", "Armor", "Weapon")   # Armor / Weapon StatModifiers Mana are max-Mana bonuses, not costs
# 0.4.9: the keys a Simple charged cast step may have to be turned into a Mana check - exactly the keys of the vanilla wand check
# Wand_Cast_Left_Charged (a StatsCondition with RunTime / Next / Failed), so the converted step runs like the wand's
SPELL_GATE_KEYS = ("Type", "Costs", "$Comment", "RunTime", "Next", "Failed")
# 0.4.9: vanilla test interactions that carry a Mana number and that nothing references - left alone (checked unreferenced every build)
SPELL_INT_TESTS = ("StatsCondition",)
# 0.4.9: keys of an interaction that never name another interaction (not walked by spell_casts)
_SPELL_WALK_SKIP = ("Type", "$Comment", "Var", "Effects", "Parent", "Tags", "Config", "ItemToRemove", "ItemToAdd", "Cooldown", "Costs",
                    "StatModifiers", "DefaultValue", "DefaultOk", "RunTime", "Behaviour")
''')

# ---------------------------------------------------------------------------------------------------------------- SPELL GEN: the walk
SPELL_049 = r'''def _spell_eff(x, ints, src, depth):
    """(fields, source of each field) of interaction x with what it inherits from its Parent interaction chain: a field it sets itself
    wins (the asset codec's field-level inheritance). A Costs / StatModifiers block without Mana over a parent block WITH Mana is refused
    (whether the engine merges the two blocks is not known)."""
    p = x.get("Parent")
    if not (isinstance(p, str) and p in ints):
        return dict(x), dict((k, src) for k in x)
    if depth > 30:
        spell_fail("interaction Parent chain too long (a loop?) at %s" % p)
    pf, ps = _spell_eff(ints[p], ints, ("int", p), depth + 1)
    for f in ("Costs", "StatModifiers"):
        if isinstance(x.get(f), dict) and "Mana" not in x[f] and isinstance(pf.get(f), dict) and "Mana" in pf[f]:
            spell_fail("%s sets %s without Mana over its Parent %s's Mana %s - whether the engine merges the two is not known" % (
                src, f, p, pf[f]["Mana"]))
    pf.update(x)
    for k in x:
        ps[k] = src
    return pf, ps


def spell_casts(item, ints, roots):
    """0.4.9 GATE SIMULATION of one item: what its interactions check and spend in Mana, by the ENGINE's rules (research/Mana-Cost-And-
    Regen-Research.md 1.2, HytaleServer 0.6.8 bytecode - 0.4.8 assumed an item var named like an interaction replaced it, which is false):
      - a string names the global interaction asset (ChargingInteraction.compile -> Interaction.getInteractionOrUnknown): an item
        InteractionVars entry of the same name is never used; an item slot / a var value names a root interaction (its Interactions);
      - an item's InteractionVars are read only by a Replace naming that Var (ReplaceInteraction.doReplace), else its DefaultValue;
      - an inline interaction inherits every field of its Parent interaction it does not set (Type, Costs, Next, ...);
      - a StatsCondition checks its OWN Costs (fails when Mana < cost, drains nothing; Failed runs); a ChangeStat never fails.
    item = the item JSON (Parent already resolved). Returns {"casts": [[check Mana, check source, [(spend, source)], where]], "free":
    [(spend, source, where)] (a Mana drain with no Mana check before it), "fail": [...] (a drain on a check's Failed branch), "gain":
    [...] (a Mana gain)}. Sources: ("int", asset id) / ("var", var name) / ("inline", owner). A spend is the (negative) Mana number."""
    iv = item.get("InteractionVars") or {}
    if not isinstance(iv, dict):
        iv = {}
    out = {"casts": [], "free": [], "fail": [], "gain": []}
    seen = set()

    def ckey(ctx):
        return id(ctx) if isinstance(ctx, list) else ctx

    def root_ref(sid, ctx, depth, stack):
        if sid in roots:
            key = ("root", sid, ckey(ctx))
            if key in seen:
                return
            seen.add(key)
            node(roots[sid].get("Interactions"), ctx, depth + 1, sid, stack)
        elif sid in ints:
            int_ref(sid, ctx, depth, stack)

    def int_ref(sid, ctx, depth, stack):
        if sid in ints:
            if sid in stack:
                return
            key = ("int", sid, ckey(ctx))
            if key in seen:
                return
            seen.add(key)
            inter(ints[sid], ctx, depth + 1, ("int", sid), stack + (sid,))
        elif sid in roots:
            root_ref(sid, ctx, depth, stack)

    def var_value(v, ctx, depth, stack, var):
        if isinstance(v, str):
            root_ref(v, ctx, depth, stack)
        elif isinstance(v, dict):
            for e in (v.get("Interactions") or []):
                if isinstance(e, str):
                    int_ref(e, ctx, depth, stack)
                elif isinstance(e, dict):
                    inter(e, ctx, depth + 1, ("var", var), stack)

    def record(val, src, ctx, where):
        if isinstance(ctx, list):
            ctx[2].append((val, src))
        elif ctx == "fail":
            out["fail"].append((val, src, where))
        else:
            out["free"].append((val, src, where))

    def inter(x, ctx, depth, src, stack):
        if depth > 200:
            spell_fail("interaction nesting deeper than 200 at %s" % (src,))
        f, fs = _spell_eff(x, ints, src, 0)
        t = f.get("Type")
        if t == "Replace" and "Var" in f:
            if f["Var"] in iv:
                var_value(iv[f["Var"]], ctx, depth + 1, stack, f["Var"])
            else:
                var_value(f.get("DefaultValue"), ctx, depth + 1, stack, "(default of %s)" % f["Var"])
            return
        costs, mods = f.get("Costs"), f.get("StatModifiers")
        gate = None
        if t == "StatsCondition" and isinstance(costs, dict) and "Mana" in costs:
            gate = [costs["Mana"], fs.get("Costs"), [], src]
            out["casts"].append(gate)
        elif isinstance(costs, dict) and "Mana" in costs:
            spell_fail("%s has a Mana Costs on a %s interaction (only a StatsCondition checks it)" % (src, t))
        if isinstance(mods, dict) and "Mana" in mods:
            v = mods["Mana"]
            if t != "ChangeStat" or isinstance(v, bool) or not isinstance(v, (int, float)):
                spell_fail("%s has a Mana StatModifiers %r on a %s interaction - not a pattern this build knows" % (src, v, t))
            if v < 0:
                record(v, fs.get("StatModifiers"), ctx, src)
            elif v > 0:
                out["gain"].append((v, fs.get("StatModifiers"), src))
        for k in f:
            if k in _SPELL_WALK_SKIP:
                continue
            if gate is not None and k == "Next":
                node(f[k], gate, depth + 1, src, stack)
            elif gate is not None and k == "Failed":
                node(f[k], "fail", depth + 1, src, stack)
            else:
                node(f[k], ctx, depth + 1, src, stack)

    def node(x, ctx, depth, owner, stack):
        if isinstance(x, str):
            int_ref(x, ctx, depth, stack)
        elif isinstance(x, list):
            for e in x:
                node(e, ctx, depth + 1, owner, stack)
        elif isinstance(x, dict):
            if "Type" in x or "Parent" in x:
                inter(x, ctx, depth + 1, ("inline", owner[1] if isinstance(owner, tuple) else owner), stack)
            else:
                for k in x:
                    if k not in _SPELL_WALK_SKIP:
                        node(x[k], ctx, depth + 1, owner, stack)
    slots = item.get("Interactions")
    if isinstance(slots, dict):
        for k in slots:
            v = slots[k]
            if isinstance(v, str):
                root_ref(v, None, 0, ())
            else:
                var_value(v, None, 0, (), "(slot %s)" % k)
    return out


def _spell_refs(x, sid, key):
    """how often the string sid appears in x as a value (not as a Type)"""
    n = 0
    if isinstance(x, dict):
        for k in x:
            if k != "Type":
                n += _spell_refs(x[k], sid, k)
    elif isinstance(x, list):
        for e in x:
            n += _spell_refs(e, sid, key)
    elif isinstance(x, str) and x == sid and key != "Type":
        n += 1
    return n


def _spell_eff_item(items, iid, depth):
    x = items[iid]
    p = x.get("Parent")
    if isinstance(p, str) and p in items and depth < 30:
        m = dict(_spell_eff_item(items, p, depth + 1))
        m.update(x)
        return m
    return x


def spell_int_plan(items, ints, int_paths, roots, div):
    """0.4.9: the charged cast checks and default drains (Server/Item/Interactions) that must change so a cast CHECKS what it SPENDS.
    items = {item id: JSON} AFTER the item overrides (spell_plan); ints / roots = vanilla {id: JSON}; int_paths = {id: asset path}.
    Returns (plan, fams, heirs, tests): plan = [(id, path, kind, old, new, new JSON)] sorted by id - kind "check" (Costs.Mana set to what
    the items behind it spend), "check+" (a Simple charged step turned into a StatsCondition with the Mana check it never had; old None),
    "drain" (StatModifiers.Mana / div); fams = {check id: (new check, [items that spend it], [items behind it that spend 0])}; heirs =
    [(interaction, the overridden one it inherits by Parent)]; tests = the unreferenced test assets left alone. Anything unknown stops."""
    for sid in SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS:
        if sid not in ints:
            spell_fail("the interaction %s is not in Assets.zip any more - the cast check / drain list needs a look" % sid)
        if "Parent" in ints[sid]:
            spell_fail("the interaction %s has a Parent (%r) - not a pattern this build knows" % (sid, ints[sid]["Parent"]))
    for rid in sorted(roots):
        h = _spell_hits(roots[rid], [], [])
        if h:
            spell_fail("the root interaction %s carries a Mana number %s - not a pattern this build knows" % (rid, h[:3]))
    gates, drains, tests = {}, {}, []
    for sid in sorted(ints):
        d = ints[sid]
        for (hp, f, v) in _spell_hits(d, [], []):
            where = "%s %s" % (sid, "/".join(str(x) for x in hp) or "(top)")
            if sid in SPELL_INT_TESTS:
                if sid not in tests:
                    tests.append(sid)
                continue
            if hp != ():
                spell_fail("%s: a Mana %s inside the interaction (not at its top) - not a pattern this build knows" % (where, f))
            if list(d[f].keys()) != ["Mana"]:
                spell_fail("%s: %s names more than Mana: %s" % (where, f, json.dumps(d[f])))
            if isinstance(v, bool) or not isinstance(v, int):
                spell_fail("%s: Mana %r is not a whole number" % (where, v))
            if f == "Costs" and sid in SPELL_COST_PARENTS and d.get("Type") == "StatsCondition" and v >= 0:
                gates[sid] = v
            elif f == "StatModifiers" and sid in SPELL_DRAIN_PARENTS and d.get("Type") == "ChangeStat" and v <= 0:
                drains[sid] = v
            else:
                spell_fail("%s: a Mana %s %r on a %s interaction that is not a known cast check %s or default drain %s" % (
                    where, f, v, d.get("Type"), list(SPELL_COST_PARENTS), list(SPELL_DRAIN_PARENTS)))
    for sid in SPELL_DRAIN_PARENTS:
        if sid not in drains:
            spell_fail("the default drain %s has no Mana number any more" % sid)
    # a Simple charged step without Costs becomes a StatsCondition (the Mana check it never had) - only with the wand check's keys
    conv = []
    for sid in SPELL_COST_PARENTS:
        if sid in gates:
            continue
        d = ints[sid]
        if d.get("Type") != "Simple" or "Costs" in d or not all(k in SPELL_GATE_KEYS for k in d) or "Next" not in d or "Failed" not in d:
            spell_fail("the charged cast step %s is neither a StatsCondition with a Mana cost nor a plain Simple step with Next + Failed "
                       "(keys %s) - not a pattern this build knows" % (sid, list(d.keys())))
        if list(d.keys())[0] != "Type":
            spell_fail("%s: Type is not its first key" % sid)
        conv.append(sid)
    for sid in tests:
        refs = sum(_spell_refs(x, sid, None) for x in list(items.values()) + list(ints.values()) + list(roots.values()))
        if refs:
            spell_fail("the test interaction %s (Mana %s) is referenced %d time(s) - it is no longer a test asset" % (
                sid, _spell_hits(ints[sid], [], []), refs))
    # interactions that inherit one of these by Parent get the new number too; one that inherits a converted step would become a check
    heirs = []
    for sid in sorted(ints):
        p, seen = ints[sid].get("Parent"), set()
        while isinstance(p, str) and p in ints and p not in seen:
            seen.add(p)
            if p in SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS:
                heirs.append((sid, p))
                if p in conv:
                    spell_fail("the interaction %s inherits %s by Parent - turning %s into a Mana check would change it too" % (sid, p, p))
                break
            p = ints[p].get("Parent")
    # planning world: the default drains / div, every charged step a check - which spends each check guards, item by item
    probe = dict(ints)
    for sid, v in drains.items():
        nd = _scopy.deepcopy(ints[sid])
        nd["StatModifiers"]["Mana"] = spell_new(v, div)
        probe[sid] = nd
    for sid in SPELL_COST_PARENTS:
        nd = _scopy.deepcopy(ints[sid])
        nd["Type"] = "StatsCondition"
        nd["Costs"] = {"Mana": gates.get(sid, 1)}
        probe[sid] = nd
    spend = dict((sid, {}) for sid in SPELL_COST_PARENTS)
    for iid in sorted(items):
        r = spell_casts(_spell_eff_item(items, iid, 0), probe, roots)
        if r["free"] or r["fail"] or r["gain"]:
            spell_fail("%s spends / gains Mana outside a known cast check: free %s, on a Failed branch %s, gains %s" % (
                iid, r["free"][:3], r["fail"][:3], r["gain"][:3]))
        for c in r["casts"]:
            if c[1] is None or c[1][0] != "int" or c[1][1] not in SPELL_COST_PARENTS:
                spell_fail("%s: a Mana check from %s - only the known charged cast steps check Mana" % (iid, c[1]))
            spend[c[1][1]][iid] = -sum(v for v, src in c[2])
    fams = {}
    for sid in SPELL_COST_PARENTS:
        pos = sorted(set(v for v in spend[sid].values() if v > 0))
        if len(pos) != 1:
            spell_fail("the items behind the cast check %s spend %s Mana - one check serves them all, so they must spend one number: %s" % (
                sid, pos or "no", sorted(spend[sid].items())[:8]))
        fams[sid] = (pos[0], sorted(i for i, v in spend[sid].items() if v > 0), sorted(i for i, v in spend[sid].items() if v == 0))
    plan = []
    for sid in sorted(set(SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS)):
        d = ints[sid]
        new = _scopy.deepcopy(d)
        if sid in drains:
            kind, old, nv = "drain", drains[sid], spell_new(drains[sid], div)
            new["StatModifiers"]["Mana"] = nv
            want = [("StatModifiers", "Mana")] if nv != old else []
        elif sid in gates:
            kind, old, nv = "check", gates[sid], fams[sid][0]
            new["Costs"]["Mana"] = nv
            want = [("Costs", "Mana")] if nv != old else []
        else:
            kind, old, nv = "check+", None, fams[sid][0]
            new = dict([("Type", "StatsCondition"), ("Costs", {"Mana": nv})] + [(k, _scopy.deepcopy(d[k])) for k in list(d.keys())[1:]])
            want = None
        if want is not None:
            diff = _spell_diff(d, new, [], [])
            if any(why != "value" for p, why in diff) or sorted(p for p, why in diff) != sorted(want):
                spell_fail("%s: the generated interaction differs from vanilla in more than its Mana number: %s" % (sid, diff[:6]))
            back = _scopy.deepcopy(new)
            back["StatModifiers" if kind == "drain" else "Costs"]["Mana"] = old
        else:
            if list(new.keys()) != ["Type", "Costs"] + list(d.keys())[1:] or new["Type"] != "StatsCondition":
                spell_fail("%s: the converted check does not have the vanilla keys + Costs after Type" % sid)
            back = dict((k, _scopy.deepcopy(new[k])) for k in new if k != "Costs")
            back["Type"] = d["Type"]
        if back != d or json.dumps(back) != json.dumps(d):
            spell_fail("%s: putting the old number back does not give the vanilla interaction" % sid)
        if not (int_paths[sid].startswith("Server/Item/Interactions/") and int_paths[sid].endswith("/%s.json" % sid)):
            spell_fail("%s: unexpected asset path %s" % (sid, int_paths[sid]))
        plan.append((sid, int_paths[sid], kind, old, nv, new))
    return plan, fams, heirs, tests


def spell_verify(items_old, items_new, ints_old, ints_new, roots, div):
    """0.4.9 gate simulation on the FINAL assets (items + interactions as this jar ships them) against vanilla, item by item: every Mana
    spend is behind a Mana check, the check = what the cast spends = the vanilla spend / div (rounded like spell_new), a Mana check only
    comes from a charged cast step asset (an item var named like one is never used - it stays dead data), one check per item, nothing
    that cost Mana in vanilla became free. Returns [(item id, check id, old check (0 = vanilla had none), new check, old spend, new
    spend)] sorted by id (spends as positive numbers)."""
    rows = []
    for iid in sorted(items_new):
        rn = spell_casts(_spell_eff_item(items_new, iid, 0), ints_new, roots)
        ro = spell_casts(_spell_eff_item(items_old, iid, 0), ints_old, roots)
        if rn["free"] or rn["fail"] or rn["gain"]:
            spell_fail("gate simulation: %s spends Mana without a check first (%s), on a Failed branch (%s) or gains Mana (%s)" % (
                iid, rn["free"][:3], rn["fail"][:3], rn["gain"][:3]))
        if not rn["casts"]:
            if ro["casts"] or ro["free"]:
                spell_fail("gate simulation: %s had a Mana cost in vanilla and has none now" % iid)
            continue
        gids = sorted(set(c[1][1] for c in rn["casts"] if c[1] and c[1][0] == "int"))
        if len(gids) != 1 or any(c[1] is None or c[1][0] != "int" or c[1][1] not in SPELL_COST_PARENTS for c in rn["casts"]):
            spell_fail("gate simulation: %s has Mana checks %s - expected exactly one known charged cast step" % (
                iid, [c[1] for c in rn["casts"]]))
        spend_new = sorted(v for c in rn["casts"] for v, src in c[2])
        spend_old = sorted(v for c in ro["casts"] for v, src in c[2]) + sorted(v for v, src, w in ro["free"])
        if sorted(spend_new) != sorted(spell_new(v, div) for v in spend_old):
            spell_fail("gate simulation: %s spends %s now, vanilla %s - expected vanilla / %d" % (iid, spend_new, spend_old, div))
        for c in rn["casts"]:
            sp = -sum(v for v, src in c[2])
            if sp != 0 and c[0] != sp:
                spell_fail("gate simulation: %s checks %s Mana but spends %s" % (iid, c[0], sp))
            if sp == 0 and spend_old:
                spell_fail("gate simulation: %s spent %s in vanilla and spends 0 now" % (iid, spend_old))
        oc = [c[0] for c in ro["casts"] if c[1] == ("int", gids[0])]
        rows.append((iid, gids[0], oc[0] if oc else 0, rn["casts"][0][0], -sum(spend_old), -sum(spend_new)))
    return rows
'''
cut("def spell_leaks(items, ints, roots):", "# <<< SPELL GEN", SPELL_049)

# ---------------------------------------------------------------------------------------------------------------- SPELL GEN: build driver
cut("_leaks = spell_leaks(", "if len(SPELL_PLAN) < 20:", "")
rep('''SPELL_IDS = [x[0] for x in SPELL_TABLE]
# the kit weapons Skyy's numbers were chosen for (Mage 30 = 3 staff casts, Priest 30 = 6 wand casts)
_sk = dict((x[0], x) for x in SPELL_TABLE)
assert _sk["Weapon_Staff_Wood"][2] == 10 and _sk["Weapon_Wand_Wood"][2] == 5, (_sk.get("Weapon_Staff_Wood"), _sk.get("Weapon_Wand_Wood"))
''', '''SPELL_IDS = [x[0] for x in SPELL_TABLE]
# the kit weapons Skyy's numbers were chosen for (Mage 30 = 3 staff casts, Priest 30 = 6 wand casts)
_sk = dict((x[0], x) for x in SPELL_TABLE)
assert _sk["Weapon_Staff_Wood"][2] == 10 and _sk["Weapon_Wand_Wood"][2] == 5, (_sk.get("Weapon_Staff_Wood"), _sk.get("Weapon_Wand_Wood"))
# ---- 0.4.9 (tools/skills_0_4_9_patch.py point 1): the cast CHECKS (charged cast step interactions) + the default drains, then the gate
# simulation of every item on vanilla and on the final assets
_s_items_old = dict((k, v[1]) for k, v in SPELL_ITEMS.items())
_s_items_new = dict(_s_items_old)
for _iid, _p, _e, _nj in SPELL_PLAN:
    _s_items_new[_iid] = _nj
_s_int_paths = dict((k, v[0]) for k, v in _sn.items())
SPELL_INT_PLAN, SPELL_FAMS, SPELL_HEIRS, SPELL_TESTS = spell_int_plan(_s_items_new, SPELL_INTS, _s_int_paths, SPELL_ROOTS, SPELL_DIVISOR)
_s_dups = []


def _s_hook(pairs):
    _ks = [k for k, v in pairs]
    _s_dups.extend(sorted(set(k for k in _ks if _ks.count(k) > 1)))
    return dict(pairs)
with zipfile.ZipFile(ASSETS) as _sz:     # the overridden interaction files have no duplicate key either
    for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
        del _s_dups[:]
        if json.loads(_sz.read(_p).decode("utf-8-sig"), object_pairs_hook=_s_hook) != SPELL_INTS[_sid] or _s_dups:
            spell_fail("%s has a duplicate JSON key %s" % (_p, _s_dups))
    # nothing outside Server/Item (NPC roles, entities, drops, ...) names an overridden interaction or a Charging step leading to one: mobs
    # attack with their own interactions, so these overrides cannot change a mob (research 1.4); World/ and Prefabs/ hold no interactions
    _s_lead = sorted(set(SPELL_COST_PARENTS + SPELL_DRAIN_PARENTS) | set(
        _k for _k, _v in SPELL_INTS.items() if isinstance(_v, dict) and _v.get("Type") == "Charging"
        and any(_x in SPELL_COST_PARENTS for _x in (_v.get("Next") or {}).values() if isinstance(_x, str))))
    _s_needles = [('"%s"' % _x).encode("utf-8") for _x in _s_lead]
    _s_out = []
    _s_nscan = 0
    for _n in _sz.namelist():
        if _n.startswith("Server/") and _n.endswith(".json") and not _n.startswith(("Server/Item/", "Server/World/", "Server/Prefabs/")):
            _s_nscan += 1
            _b = _sz.read(_n)
            for _nd in _s_needles:
                if _nd in _b:
                    _s_out.append("%s names %s" % (_n, _nd.decode()))
    if _s_out:
        spell_fail("assets outside Server/Item name an overridden interaction or its Charging step (a mob or another system would change "
                   "too): %s" % _s_out[:6])
_s_ints_new = dict(SPELL_INTS)
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    _s_ints_new[_sid] = _nj
SPELL_GATES = spell_verify(_s_items_old, _s_items_new, SPELL_INTS, _s_ints_new, SPELL_ROOTS, SPELL_DIVISOR)
SPELL_INT_IDS = [x[0] for x in SPELL_INT_PLAN]
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    _txt = json.dumps(_nj, indent=2, ensure_ascii=True) + "\\n"
    assert _p.startswith("Server/Item/Interactions/") and _p.endswith("/%s.json" % _sid) and _p not in SPELL_FILES
    assert json.loads(_txt) == _nj and all(ord(ch) < 128 for ch in _txt)
    SPELL_FILES[_p] = _txt
_sg = dict((x[0], x) for x in SPELL_GATES)
# the kit weapons: the Priest wand checks 5 and spends 5 (vanilla 25 / 25), the Mage staff checks 10 (vanilla: no check) and spends 10
assert _sg["Weapon_Wand_Wood"][1:] == ("Wand_Cast_Left_Charged", 25, 5, 25, 5), _sg.get("Weapon_Wand_Wood")
assert _sg["Weapon_Staff_Wood"][1:] == ("Staff_Cast_Summon_Charged", 0, 10, 50, 10), _sg.get("Weapon_Staff_Wood")
assert len(SPELL_INT_PLAN) == 8 and sorted(SPELL_FAMS) == sorted(SPELL_COST_PARENTS) and len(SPELL_GATES) >= len(SPELL_PLAN), (
    len(SPELL_INT_PLAN), len(SPELL_GATES))
assert all(x[0] in _sg for x in SPELL_TABLE if x[4] > 0), "an overridden item that spends Mana is missing from the gate table"
SPELL_FREE = sorted(x[0] for x in SPELL_GATES if x[5] == 0)     # items that spend 0 behind a check (need the check's Mana present)
''')
# clash: another Skyy mod of the live set / a pack mod shipping one of the interaction overrides fights over it too
rep('''def _spell_clash(names):
    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
                                                           and os.path.basename(n)[:-5] in _sk))''', '''def _spell_clash(names):
    return sorted(n for n in names if n in SPELL_FILES or (n.startswith("Server/Item/Items/") and n.endswith(".json")
                                                           and os.path.basename(n)[:-5] in _sk)
                  or (n.startswith("Server/Item/Interactions/") and n.endswith(".json") and os.path.basename(n)[:-5] in SPELL_INT_IDS))''')
rep('''for _t in SPELL_TABLE:
    print("  %-34s cast check %3d -> %2d   drain %3d -> %2d" % _t)
''', '''for _t in SPELL_TABLE:
    print("  %-34s cast check %3d -> %2d   drain %3d -> %2d" % _t)
print("  (0.4.9: an item's cast check var above is dead data - the engine checks the charged cast step's own interaction, below)")
print("cast checks /%d (0.4.9): %d interaction overrides generated from Assets.zip (test assets left alone: %s; interactions inheriting "
      "one by Parent: %s)" % (SPELL_DIVISOR, len(SPELL_INT_PLAN), ", ".join(SPELL_TESTS) or "none",
                              ", ".join("%s <- %s" % kv for kv in SPELL_HEIRS) or "none"))
for _sid, _p, _k, _o, _n, _nj in SPELL_INT_PLAN:
    if _k == "drain":
        print("  %-30s default drain %4d -> %3d" % (_sid, _o, _n))
    else:
        _f = SPELL_FAMS[_sid]
        print("  %-30s cast check    %4s -> %3d  (%s; %d item(s) spend %d%s)" % (
            _sid, "none" if _o is None else _o, _n, "Simple -> StatsCondition" if _k == "check+" else "StatsCondition", len(_f[1]), _f[0],
            ("; spend 0 and now need %d Mana present: %s" % (_n, ", ".join(_f[2]))) if _f[2] else ""))
print("gate simulation (the engine's rules, every item, vanilla vs this jar): %d items cast with Mana - each checks what it spends "
      "(vanilla spend / %d); %d spend 0 behind a check (%s); no Mana spend without a check; none of the %d assets outside Server/Item "
      "(NPC roles, entities, drops ...) names an overridden interaction or its Charging step (%s)" % (
          len(SPELL_GATES), SPELL_DIVISOR, len(SPELL_FREE), ", ".join(SPELL_FREE) or "none", _s_nscan, ", ".join(_s_lead)))
_fam_rows = {}
for _g in SPELL_GATES:
    _fam_rows.setdefault(_g[1:], []).append(_g[0])
for _key in sorted(_fam_rows, key=lambda k: (k[0], k[3])):
    print("  %-28s check %4s -> %2d   spend %3d -> %2d : %d item(s) %s" % (
        _key[0], "none" if _key[1] == 0 else _key[1], _key[2], _key[3], _key[4], len(_fam_rows[_key]),
        ", ".join(_fam_rows[_key]) if len(_fam_rows[_key]) <= 3 else ", ".join(_fam_rows[_key][:2]) + ", ..."))
''')
rep('''if _pk_mana:
    print("spell costs: NOTE pack mod items with their own Mana cost (or a Parent overridden here) are NOT divided: %s" % ", ".join(_pk_mana))
''', '''if _pk_mana:
    print("spell costs: NOTE pack mod items with their own Mana cost (or a Parent overridden here) are NOT divided: %s" % ", ".join(_pk_mana))
    print("spell costs: NOTE if such an item casts through one of the overridden cast checks above, it is now checked at that number")
''')

# ---------------------------------------------------------------------------------------------------------------- ManaCost: the real gates
rep('''# the (new) Mana a cast of this item checks for; -1 = not a Mana weapon of this jar
mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  if (id == null) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return COST[i];
  return -1;
}""", mcost))
''', '''# 0.4.9: the REAL gate table from the build's gate simulation (SPELL GEN spell_verify): per item that casts with Mana, the charged cast step
# that checks it (GCHECK), the Mana it must have to cast (GATE) and what a cast spends (SPEND), with the vanilla numbers (GATE_OLD 0 = vanilla
# had no check). OLD / COST above are the item vars 0.4.8 generated (COST = the dead cast check var; DRAIN = what the item spends).
mcost.addField(CtField.make("public static final int GN = %d;" % len(SPELL_GATES), mcost))
mcost.addField(CtField.make("public static final String[] GIDS = %s;" % jarr([_g[0] for _g in SPELL_GATES]), mcost))
mcost.addField(CtField.make("public static final String[] GCHECK = %s;" % jarr([_g[1] for _g in SPELL_GATES]), mcost))
for _nm, _ix in (("GATE_OLD", 2), ("GATE", 3), ("SPEND_OLD", 4), ("SPEND", 5)):
    mcost.addField(CtField.make("public static final int[] %s = new int[] { %s };" % (_nm, ", ".join(str(_g[_ix]) for _g in SPELL_GATES)), mcost))
# the 8 interaction overrides (the pack check reads them in the game's interaction assets): kind "check" / "check+" / "drain", old (-1 = none)
mcost.addField(CtField.make("public static final int INT_N = %d;" % len(SPELL_INT_PLAN), mcost))
mcost.addField(CtField.make("public static final String[] INT_IDS = %s;" % jarr(SPELL_INT_IDS), mcost))
mcost.addField(CtField.make("public static final String[] INT_KIND = %s;" % jarr([_x[2] for _x in SPELL_INT_PLAN]), mcost))
mcost.addField(CtField.make("public static final int[] INT_OLD = new int[] { %s };" % ", ".join(str(-1 if _x[3] is None else _x[3]) for _x in SPELL_INT_PLAN), mcost))
mcost.addField(CtField.make("public static final int[] INT_NEW = new int[] { %s };" % ", ".join(str(_x[4]) for _x in SPELL_INT_PLAN), mcost))
mcost.addMethod(CtNewMethod.make("""
public static int gi(String id) {
  if (id == null) return -1;
  for (int i = 0; i < GIDS.length; i++) if (GIDS[i].equals(id)) return i;
  return -1;
}""", mcost))
# the Mana a cast of this item CHECKS for (0.4.9: the real check of its charged cast step - 0.4.8 returned the dead var); -1 = no Mana cast
mcost.addMethod(CtNewMethod.make("""
public static int costOf(String id) {
  int i = gi(id);
  return i < 0 ? -1 : GATE[i];
}""", mcost))
# what one cast of this item spends (0 for Crystal_Red / Crystal_Ice / the plain Blunderbuss); -1 = no Mana cast
mcost.addMethod(CtNewMethod.make("""
public static int spendOf(String id) {
  int i = gi(id);
  return i < 0 ? -1 : SPEND[i];
}""", mcost))
''')

# ---------------------------------------------------------------------------------------------------------------- ManaGuard: the real gate
rep('''      int cost = {PKG}.ManaCost.costOf(id);
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
      }}''', '''      int cost = {PKG}.ManaCost.costOf(id);
      if (cost <= 0) continue;
      int spend = {PKG}.ManaCost.spendOf(id);
      weapons++;
      if (base + 0.000001 < (double) cost) {{
        if (badW.length() > 0) badW.append(", ");
        if (spend == cost) badW.append(id).append(" costs ").append(cost).append(" Mana per cast");
        else badW.append(id).append(" needs ").append(cost).append(" Mana to cast (it spends ").append(spend).append(")");
        sig.append(id).append(':').append(cost).append(':').append(spend).append(',');
      }} else {{
        if (okW.length() > 0) okW.append(", ");
        if (spend == cost) {{
          long casts = (long) Math.floor(base / (double) cost + 0.000001);
          okW.append(id).append(" ").append(cost).append(" (").append(casts).append(casts == 1L ? " cast)" : " casts)");
        }} else if (spend <= 0) {{
          okW.append(id).append(" ").append(cost).append(" (spends 0: free while Mana is ").append(cost).append("+)");
        }} else {{
          long casts2 = (long) Math.floor((base - (double) cost) / (double) spend + 0.000001) + 1L;
          okW.append(id).append(" ").append(cost).append(" (spends ").append(spend).append(": ").append(casts2).append(casts2 == 1L ? " cast)" : " casts)");
        }}
      }}''')
rep('''", but the kit weapon " + badW.toString() + " Mana per cast (kit from " + (live ? "SkyyClasses" : "the built-in table") + ") - a new " + cls + " cannot cast it.''',
    '''", but the kit weapon " + badW.toString() + " (kit from " + (live ? "SkyyClasses" : "the built-in table") + ") - a new " + cls + " cannot cast it.''')

# ---------------------------------------------------------------------------------------------------------------- ManaGuard: pack check
rep('''mgd.addMethod(CtNewMethod.make(f"""
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
''', '''# ---- 0.4.9 interaction check (tools/skills_0_4_9_patch.py point 2): which pack the game's INTERACTION assets take each of the 8 overridden
# interactions from, and the live Mana check of each cast check as the engine's gate uses it. StatsConditionBaseInteraction.rawCosts = the
# stat id -> cost map of its own Costs as decoded; its afterDecode puts EntityStatsModule.resolveEntityStats(rawCosts) into costs (stat
# index -> cost), and StatsConditionInteraction.canAfford reads ONLY costs (null costs = canAfford false = every cast refused). So the number
# reported is costs' entry for DefaultEntityStatTypes.getMana() (0.4.9 review finding 4; rawCosts only tells "no Mana cost" apart).
# Every Interaction load rebuilds every root (InteractionModule.handledLoadedInteractions ->
# RootInteraction.build), so the compiled Charging steps use the asset map's winner. Same tick and retries as the item pack check.
B.probe(pool, "com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction", "getAssetMap")
assert pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("rawCosts") is not None
assert str(pool.get("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("costs").getType().getName()) == "it.unimi.dsi.fastutil.ints.Int2FloatMap"
B.probe(pool, "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes", "getMana")
mgd.addField(CtField.make("public static volatile boolean ITEMS_DONE = false;", mgd))
mgd.addField(CtField.make("public static volatile boolean INT_DONE = false;", mgd))
mgd.addField(CtField.make('public static volatile String INT_LAST = "";', mgd))
mgd.addField(CtField.make("public static volatile java.lang.reflect.Field RAW = null;", mgd))
mgd.addField(CtField.make("public static volatile java.lang.reflect.Field RES = null;", mgd))
# the live Mana check of an interaction asset: the resolved costs entry of the Mana stat (what the gate compares); -2 = not a
# StatsCondition, -3 = a StatsCondition without a Mana cost, -4 = a Mana cost the engine did not resolve (no costs entry for the Mana
# index: the gate does not check it as decoded), -1 = not readable
mgd.addMethod(CtNewMethod.make("""
public static float liveCheck(Object a) {
  try {
    if (a == null) return -1.0f;
    if (!(a instanceof com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction)) return -2.0f;
    java.lang.reflect.Field f = RAW;
    if (f == null) {
      f = Class.forName("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("rawCosts");
      f.setAccessible(true);
      RAW = f;
    }
    java.lang.reflect.Field g = RES;
    if (g == null) {
      g = Class.forName("com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.StatsConditionBaseInteraction").getDeclaredField("costs");
      g.setAccessible(true);
      RES = g;
    }
    Object m = f.get(a);
    if (!(m instanceof java.util.Map)) return -1.0f;
    Object v = ((java.util.Map) m).get("Mana");
    if (!(v instanceof Number)) return -3.0f;
    Object c = g.get(a);
    if (!(c instanceof it.unimi.dsi.fastutil.ints.Int2FloatMap)) return -4.0f;
    it.unimi.dsi.fastutil.ints.Int2FloatMap cm = (it.unimi.dsi.fastutil.ints.Int2FloatMap) c;
    int mi = com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes.getMana();
    if (!cm.containsKey(mi)) return -4.0f;
    return cm.get(mi);
  } catch (Throwable t) { return -1.0f; }
}""", mgd))
# packs[i] / live[i] for ManaCost.INT_IDS[i] (null / -1 = not there / not readable) -> {level "info" / "warn" / "" (nothing readable - try
# again), message}
mgd.addMethod(CtNewMethod.make(f"""
public static String[] intReport(String[] packs, float[] live) {{
  String[] ids = {PKG}.ManaCost.INT_IDS;
  int mine = 0;
  int other = 0;
  int miss = 0;
  int unread = 0;
  StringBuilder ot = new StringBuilder();
  StringBuilder ms = new StringBuilder();
  StringBuilder bad = new StringBuilder();
  StringBuilder ck = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {{
    String p = (packs != null && i < packs.length) ? packs[i] : null;
    if (p == null) {{
      miss++;
      if (ms.length() > 0) ms.append(", ");
      ms.append(ids[i]);
      continue;
    }}
    if (!p.equals(PACK)) {{
      other++;
      if (ot.length() > 0) ot.append(", ");
      ot.append(ids[i]).append(" (").append(p).append(")");
      continue;
    }}
    mine++;
    if ({PKG}.ManaCost.INT_KIND[i].startsWith("check")) {{
      float v = (live != null && i < live.length) ? live[i] : -1.0f;
      int want = {PKG}.ManaCost.INT_NEW[i];
      if (v == -1.0f) {{ unread++; continue; }}
      if (v == -2.0f || v == -3.0f || v == -4.0f || Math.abs(v - (float) want) > 0.001f) {{
        if (bad.length() > 0) bad.append(", ");
        if (v == -2.0f) bad.append(ids[i]).append(" is not a Mana check (not a StatsCondition; it should check ").append(want).append(")");
        else if (v == -3.0f) bad.append(ids[i]).append(" checks no Mana (it should check ").append(want).append(")");
        else if (v == -4.0f) bad.append(ids[i]).append(" has a Mana cost the engine did not resolve to the Mana stat (its gate does not check it; it should check ").append(want).append(")");
        else bad.append(ids[i]).append(" checks ").append({PKG}.DivCfg.num((double) v)).append(" instead of ").append(want);
        continue;
      }}
      if (ck.length() > 0) ck.append(", ");
      ck.append(ids[i]).append(" ").append(want);
    }}
  }}
  if (mine + other == 0) return new String[] {{ "", "the game's interaction assets could not be read" }};
  String pre = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": ";
  String mt = miss > 0 ? "; " + miss + " not in the game's interaction assets (" + ms.toString() + ")" : "";
  String lv = ck.length() > 0 ? "; live cast checks " + ck.toString() + " (= what each cast spends)" : "";
  String ur = unread > 0 ? "; " + unread + " live cast check(s) not readable" : "";
  if (other == 0 && bad.length() == 0) return new String[] {{ "info", pre + (miss == 0 ? "all " + mine : mine + " of " + ids.length) + " interaction overrides are active (the game's interaction assets take them from " + PACK + ")" + lv + ur + mt }};
  String w = pre;
  if (other > 0) w = w + other + " of " + ids.length + " interaction overrides are NOT active - another asset pack wins for " + ot.toString() + ". Those casts keep that pack's Mana check / spend (of two packs with the same interaction, the one loaded last wins); " + mine + " active";
  else w = w + "all " + mine + " interaction overrides come from " + PACK;
  if (bad.length() > 0) w = w + "; the live cast check differs: " + bad.toString() + " - the Mana a cast needs is not what it spends";
  return new String[] {{ "warn", w + lv + ur + mt + "." }};
}}""", mgd))
mgd.addMethod(CtNewMethod.make(f"""
public static String[] intCheck() {{
  String[] ids = {PKG}.ManaCost.INT_IDS;
  String[] ps = new String[ids.length];
  float[] lv = new float[ids.length];
  for (int i = 0; i < lv.length; i++) lv[i] = -1.0f;
  try {{
    com.hypixel.hytale.assetstore.map.DefaultAssetMap m = com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction.getAssetMap();
    if (m != null) {{
      for (int i = 0; i < ids.length; i++) {{
        try {{ ps[i] = m.getAssetPack(ids[i]); }} catch (Throwable t) {{ ps[i] = null; }}
        try {{ lv[i] = liveCheck(m.getAsset(ids[i])); }} catch (Throwable t) {{ lv[i] = -1.0f; }}
      }}
    }}
  }} catch (Throwable t) {{ }}
  return intReport(ps, lv);
}}""", mgd))
# 0.4.9: both checks (the items as in 0.4.8, the interactions new), each logged once as soon as it is readable; after PACK_MAX tries the
# unreadable one says so
mgd.addMethod(CtNewMethod.make(f"""
public static void packTick() {{
  PACK_TRIES++;
  if (!ITEMS_DONE) {{
    String[] r = packCheck();
    if (r[0].length() > 0) {{
      ITEMS_DONE = true;
      PACK_LAST = r[1];
      if ("warn".equals(r[0])) {PKG}.SkillCfg.warn(r[1]);
      else {PKG}.SkillCfg.info(r[1]);
    }}
  }}
  if (!INT_DONE) {{
    String[] q = intCheck();
    if (q[0].length() > 0) {{
      INT_DONE = true;
      INT_LAST = q[1];
      if ("warn".equals(q[0])) {PKG}.SkillCfg.warn(q[1]);
      else {PKG}.SkillCfg.info(q[1]);
    }}
  }}
  if (ITEMS_DONE && INT_DONE) {{
    PACK_DONE = true;
    return;
  }}
  if (PACK_TRIES >= PACK_MAX) {{
    PACK_DONE = true;
    if (!ITEMS_DONE) {{
      PACK_LAST = "Spell costs /" + {PKG}.ManaCost.DIVISOR + ": the game's item assets could not be read to see which pack each of the " + {PKG}.ManaCost.N + " overridden items comes from - not checked";
      {PKG}.SkillCfg.info(PACK_LAST);
    }}
    if (!INT_DONE) {{
      INT_LAST = "Cast checks /" + {PKG}.ManaCost.DIVISOR + ": the game's interaction assets could not be read to see which pack each of the " + {PKG}.ManaCost.INT_N + " overridden interactions comes from - not checked";
      {PKG}.SkillCfg.info(INT_LAST);
    }}
  }}
}}""", mgd))
''')

# ---------------------------------------------------------------------------------------------------------------- ready line + manifest
rep('''"; spell costs /" + {PKG}.ManaCost.DIVISOR + " (" + {PKG}.ManaCost.N + " items)" + "; bridge skill:fn:addxp''',
    '''"; spell costs /" + {PKG}.ManaCost.DIVISOR + " (" + {PKG}.ManaCost.N + " items + " + {PKG}.ManaCost.INT_N + " interactions: every paid cast checks what it spends, " + {PKG}.ManaCost.GN + " casters)" + "; bridge skill:fn:addxp''')
# (0.4.9 review finding 6: "paid" - the 3 casters that spend 0 still check their family's number, see point 1)
rep('''Spells cost the vanilla Mana / 5 (wand 5, staff 10, spellbook 20: item overrides generated at build time)''',
    '''Spells cost the vanilla Mana / 5 and every paid cast checks exactly what it spends (wand 5, staff 10, spellbook 20: item + cast check overrides generated at build time)''')
rep('''m["IncludesAssetPack"] = True   # 0.4.8: the spell cost item overrides (SPELL_FILES); the pages stay inline (no .ui files)
assert SPELL_FILES and all(_p.startswith("Server/Item/Items/") for _p in SPELL_FILES) and not any(_p.endswith(".ui") for _p in SPELL_FILES)
''', '''m["IncludesAssetPack"] = True   # 0.4.8: the spell cost item overrides (SPELL_FILES; 0.4.9 + the cast check interactions); pages stay inline
assert SPELL_FILES and all(_p.startswith(("Server/Item/Items/", "Server/Item/Interactions/")) for _p in SPELL_FILES) and not any(_p.endswith(".ui") for _p in SPELL_FILES)
assert len(SPELL_FILES) == len(SPELL_PLAN) + len(SPELL_INT_PLAN), (len(SPELL_FILES), len(SPELL_PLAN), len(SPELL_INT_PLAN))
''')

# ---------------------------------------------------------------------------------------------------------------- checks + write
for k in KEEP:
    assert s.count(k) == 1, "a block that must stay byte-identical changed: " + k[:100]
assert s.count("registerSystem(") == REG0 and s.count("registerCommand(") == CMD0, "systems / commands changed"
assert [ln for ln in s.split(LF) if "ev.addEventBinding(" in ln] == BIND0, "event bindings changed"
assert "spell_leaks" not in s and s.count("def spell_casts(") == 1 and s.count("SPELL_GATES = spell_verify(") == 1
assert s.count("ManaMig.run();") == 1 and s.count("ManaGuard.tick(this.n)") == 1 and s.count("B.assemble(jar, m, OUT, SPELL_FILES)") == 1
assert s.index("# >>> SPELL GEN") < s.index("def spell_casts(") < s.index("# <<< SPELL GEN")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars")
