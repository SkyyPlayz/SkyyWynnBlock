"""Derive SkyyGear/build_skyygear_0.2.13.py from the LIVE 0.2.12 (build_skyygear_0.2.12.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_12_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_13_patch.py      then      python SkyyGear/build_skyygear_0.2.13.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.13.py

0.2.13 = SPEED TIERS FOR THE CRUDE / SCRAP WEAPONS + THE MACE LOAD WARNINGS (Skyy 2026-10-09 "the copper axe shows attack speed. my crude one
doesnt"; the 2026-10-09 LOG SCAN line of docs/log/2026-10.md).
  1. THE CAUSE (found, not a missing roll path): every path that makes or identifies a weapon already rolls a tier - GearRoll.newDoc,
     GearRoll.identify (the 0.2.11 bag identify / re-identify, /gear box, Identify / Reforge pages) and, as the safety net, GearData.put,
     which EVERY gear document write goes through (craft, drop, chest loot, class kit items on their first stamp scan, items from before
     0.2.6, SkyyRolls migrations). The Crude Battleaxe had no tier because 0.2.6's BUILD left it out of the speed families on purpose:
     it overrides the battleaxe's swing steps (InteractionVars Swing_Down / Swing_Down_Left / Swing_Down_Right) and the re-timed tier copies
     looked those variables up, so a Crude battleaxe would have swung at vanilla speed whatever its tier - GearSpeed.famCalc said "no tier
     family" and GearSpeed.ensure never rolled one. Same for the Crude sword, Crude daggers, Crude mace and the Scrap sword (the class kit
     weapons). Their overrides change ONLY sounds (Scrap sword: its smaller swing trails): each is the vanilla default step as Parent +
     Effects sound / trail keys.
     FIX: the re-timed tier copies (Slow / Fast / Super Fast; Medium = the vanilla root, untouched) look the family's main-path swing
     variables up under a renamed key (SkyyGear_Spd_<Var>), which no item defines, so every item gets the re-timed default steps at a tier.
     For the 118 items that already had a tier nothing changes (they define none of those variables - the 0.2.6 rule - so they always
     got the defaults). The 5 Crude / Scrap weapons join their families; the build proves for each that its overrides are cosmetic only
     (Parent = the variable's default step, only Effects sound / trail / particle / camera keys) and that its tier tap is exactly f x its own
     vanilla tap. At Slow / Fast / Super Fast they play the family's default swing SOUND (Copper's) instead of their own T1 sound (Scrap:
     the default trail); at Medium they are exactly vanilla. Items with another animation set (Doomed battleaxe, zombie-limb flails, the NPC
     Praetorian longsword / Scrap mace) stay without a tier. Runtime: GearSpeed.famCalc accepts an item that defines a main-path variable
     only when the build listed it with exactly those variables (F_OKID "id=var,var"); any other item keeps the 0.2.6 rule.
     LAZY HEAL (already there, now reached): a Crude weapon identified before 0.2.13 has no "spd"; the stamp scan (join, every inventory
     change, /identify, /reforge) rewrites each identified tier weapon's document through GearData.put -> GearSpeed.ensure, which adds
     ONLY "spd" to a clone (never on an unidentified item, never touching another roll; one gear.log SPEED line). No new code path, no
     migration marker - the roll is the same once-per-item roll as 0.2.6.
  2. THE 18 LOAD WARNINGS 'Missing interaction **SkyyGear_Spd{F,S,X}_Mace_Weapon_Mace_Primary_Swing_{Left,Right,Up_Left}_Charged_StaminaCondition
     _Next_Next(_0 / _0.2)': the mace's charged-swing Stamina check holds an INLINE Charging step whose two children (the tap Replace and the
     charge ChangeStat) were inline too. The engine builds a batch's client packet before it loads that batch's inline children (the
     SkyySkills 0.4.23 finding), so the inline Charging's children were "missing" for a moment (harmless - the real steps replaced the
     placeholders - but 18 WARN lines). FIX (the 0.4.23 way): every inline child of a Charging step in a generated speed file is now its own
     NAMED file (<file>_Hold0 = the tap, <file>_Hold0p2 = the charge; only an INLINE Charging's children - a file whose own top step is a
     Charging with inline children never warned and is left as it was), all in the same batch as the rest of the speed files, so every name
     resolves before the packet is built. Re-inlined (and with the variable names put back) every speed file equals 0.2.12's byte for byte
     in JSON - maces swing exactly as before (the harness proves it).
No saved data, no migration, no config row, no command, no new class. Rolling back to 0.2.12 is safe: Crude weapons keep the stored "spd"
(0.2.12 ignores it for them: no family = no line, vanilla swing).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.12.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.13.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.12"' in s and s.startswith('"""SkyyGear 0.2.12 - build script'), "build_skyygear_0.2.12.py is not the live 0.2.12"
assert "SPEED_VAR_PREFIX" not in s and "F_OKID" not in s, "0.2.12 already has the 0.2.13 parts"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")
MK0 = s.count(" = mk(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.12 - build script (javassist via jpype). GENERATED by tools/gear_0_2_12_patch.py from the LIVE 0.2.11 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.12.py -> SkyyGear/SkyyGear-0.2.12.jar (never --deploy).

0.2.12 = ''', '''"""SkyyGear 0.2.13 - build script (javassist via jpype). GENERATED by tools/gear_0_2_13_patch.py from the LIVE 0.2.12 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.13.py -> SkyyGear/SkyyGear-0.2.13.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.13 = "):].strip() + '''

0.2.12 (the base, everything below is still true unless 0.2.13 above says otherwise):
0.2.12 = ''')
rep('VERSION = "0.2.12"', 'VERSION = "0.2.13"')

# ================================================================================================================ 1. the generator
# the renamed variable prefix + the cosmetic keys an item override may change and still get a tier
rep('''SPEED_DIR_I = "Server/Item/Interactions/SkyyGear/Speed/"
''', '''SPEED_DIR_I = "Server/Item/Interactions/SkyyGear/Speed/"
# 0.2.13: the tier copies look a family's main-path swing variables up under this prefix (no item defines it -> always the re-timed default)
SPEED_VAR_PREFIX = "SkyyGear_Spd_"
# 0.2.13: an item override of a main-path swing variable that changes only these Effects keys (Parent = the variable's default step) still
# gets a tier (the Crude / Scrap weapons: their own swing sounds / trails; the tier copies play the default ones)
SPEED_COSMETIC = ("WorldSoundEventId", "LocalSoundEventId", "Trails", "Particles", "CameraEffect")
''')
rep('''        self.tcache = {}
''', '''        self.tcache = {}
        self.rename = {}          # 0.2.13: main-path variable -> its renamed key in the tier copies (set per family by speed_build)
''')
rep('''        c = dict(d)
        if "RunTime" in r: c["RunTime"] = round(float(r["RunTime"]) * self.f, 4)
''', '''        c = dict(d)
        if "RunTime" in r: c["RunTime"] = round(float(r["RunTime"]) * self.f, 4)
        # 0.2.13: a main-path swing variable is looked up under its renamed key (an item's own swing step never replaces a re-timed one)
        if typ == "Replace" and r.get("Var") in self.rename: c["Var"] = self.rename[r["Var"]]
''')
# the helpers: the Charging children naming (2.) and the cosmetic check (1.)
rep('''def speed_build(cw, names, items, read_anim):
''', '''def _speed_sni(owner, x, new, typ_of, top=False):
    if isinstance(x, list): return [_speed_sni(owner, v, new, typ_of) for v in x]
    if not isinstance(x, dict): return x
    y = dict((k, _speed_sni(owner, v, new, typ_of)) for k, v in x.items())
    # only an INLINE Charging (not the file's own top step): its children are the second inline level the packet misses
    if not top and typ_of(y) == "Charging" and isinstance(y.get("Next"), dict):
        nx = {}
        for k, v in y["Next"].items():
            if isinstance(v, dict) and ("Type" in v or "Parent" in v):
                nm = "%s_Hold%s" % (owner, str(k).replace(".", "p"))
                if nm in new: raise SystemExit("speed self-check: two Charging steps in %s name the same child %s" % (owner, nm))
                new[nm] = v
                v = nm
            nx[k] = v
        y["Next"] = nx
    return y


def speed_name_inline(out_i, typ_of, taken):
    """0.2.13: every inline child of an INLINE Charging step in a copied interaction becomes its own NAMED file <file>_Hold<key> (the engine
    builds a batch's packet before it loads the batch's inline children: 'Missing interaction **<file>_Next_Next_0'; a file whose TOP step
    is a Charging with inline children never warned - left as it was). Returns the new names."""
    work, done, made = sorted(out_i), set(), []
    while work:
        k = work.pop()
        if k in done: continue
        done.add(k)
        new = {}
        out_i[k] = _speed_sni(k, out_i[k], new, typ_of, True)
        for nk in sorted(new):
            if nk in out_i or nk in taken: raise SystemExit("speed self-check: the named Charging child %s collides" % nk)
            out_i[nk] = new[nk]
            made.append(nk)
            work.append(nk)
    return made


def speed_var_defaults(ints, vars_):
    """0.2.13: main-path variable -> the step ids its vanilla Replace steps default to"""
    out = {}

    def walk(x):
        if isinstance(x, dict):
            if x.get("Type") == "Replace" and x.get("Var") in vars_:
                dv = x.get("DefaultValue")
                ids = dv.get("Interactions") if isinstance(dv, dict) else None
                out.setdefault(x["Var"], set()).update(i for i in (ids or []) if isinstance(i, str))
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    for v in ints.values(): walk(v)
    return out


def speed_cosmetic(vv, bad, vdef):
    """0.2.13: True when every override of a main-path variable is the variable's default step as Parent + only cosmetic Effects keys"""
    for var in bad:
        o = vv.get(var)
        ints = o.get("Interactions") if isinstance(o, dict) else None
        if set(o) - {"Interactions"} or not isinstance(ints, list) or len(ints) != 1 or not isinstance(ints[0], dict): return False
        x = ints[0]
        if set(x) - {"Parent", "$Comment", "Effects"} or x.get("Parent") not in vdef.get(var, ()): return False
        e = x.get("Effects", {})
        if not isinstance(e, dict) or set(e) - set(SPEED_COSMETIC): return False
    return True


def speed_build(cw, names, items, read_anim):
''')
rep('''        mainvars = sorted(dv.mainvars)
''', '''        mainvars = sorted(dv.mainvars)
        G.rename = dict((v, SPEED_VAR_PREFIX + v) for v in mainvars)        # 0.2.13
        vdef = speed_var_defaults(I0, set(mainvars))
''')
rep('''            top, oi, orr, an = G.retime(fam, t, fe[t], aset, ri)
''', '''            top, oi, orr, an = G.retime(fam, t, fe[t], aset, ri)
            speed_name_inline(oi, lambda y: G.resolved(y).get("Type"), set(cw.inter) | set(orr))      # 0.2.13 (2.)
''')
rep('''            if bad:
                skipped[iid] = "%s: replaces the swing step(s) %s" % (fam, ", ".join(bad))
                continue
''', '''            if bad and not speed_cosmetic(vv, bad, vdef):
                skipped[iid] = "%s: replaces the swing step(s) %s" % (fam, ", ".join(bad))
                continue
            if bad:
                cosm.append("%s=%s" % (iid, ",".join(bad)))          # 0.2.13: sound / trail-only overrides get a tier
''')
rep('''        mine = []
        for iid in sorted(users.get(rid, [])):''', '''        mine, cosm = [], []
        for iid in sorted(users.get(rid, [])):''')
rep('''                     "vars": mainvars, "walk": [speed_walk_id(fam, t) if t != 1 else "" for t in range(4)], "items": mine,''',
    '''                     "vars": mainvars, "walk": [speed_walk_id(fam, t) if t != 1 else "" for t in range(4)], "items": mine, "cosm": cosm,''')
# build-time checks after the generator: the renamed keys, the named Charging children, no one-entry Parallel, the 5 Crude / Scrap weapons
rep('''EXTRA.update(SPEED_FILES)
for _sf in SPEED_FAMLIST:''', '''EXTRA.update(SPEED_FILES)
# 0.2.13 checks
_SPD_OK = [_c for _sf in SPEED_FAMLIST for _c in _sf["cosm"]]
assert sorted(_c.split("=")[0] for _c in _SPD_OK) == ["Weapon_Battleaxe_Crude", "Weapon_Daggers_Crude", "Weapon_Mace_Crude", "Weapon_Sword_Crude",
                                                     "Weapon_Sword_Scrap"], "0.2.13: the cosmetic-override weapons changed: %s" % _SPD_OK
assert all(_c.split("=")[0] in SPEED_ITEMS and _c.split("=")[0] not in SPEED_SKIPPED for _c in _SPD_OK)
assert not [_i for _i in AZ_ITEMS if SPEED_VAR_PREFIX in json.dumps(az_get(_i, "InteractionVars") or {})], "an item defines a SkyyGear_Spd_ variable"


def _spd_walk(x, fn, top=True):
    if isinstance(x, dict):
        fn(x, top)
        for _v in x.values(): _spd_walk(_v, fn, False)
    elif isinstance(x, list):
        for _v in x: _spd_walk(_v, fn, False)


_SPD_BAD = []
_SPD_HOLD = []
for _k, _v in SPEED_FILES.items():
    if not _k.startswith(SPEED_DIR_I):
        continue
    _j = json.loads(_v)
    _spd_walk(_j, lambda x, top: _SPD_BAD.append((_k, "one-entry Parallel")) if x.get("Type") == "Parallel" and len(x.get("Interactions") or []) < 2 else None)
    _spd_walk(_j, lambda x, top: _SPD_BAD.append((_k, "inline child of an inline Charging")) if not top and x.get("Type") == "Charging" and any(
        isinstance(_c, dict) for _c in (x.get("Next") or {}).values()) else None)
    _spd_walk(_j, lambda x, top: _SPD_BAD.append((_k, "old variable name %s" % x.get("Var"))) if x.get("Type") == "Replace" and any(
        x.get("Var") in _sf["vars"] for _sf in SPEED_FAMLIST) else None)
    if os.path.basename(_k)[:-5].rsplit("_", 1)[-1].startswith("Hold"):
        _SPD_HOLD.append(os.path.basename(_k)[:-5])
assert not _SPD_BAD, "0.2.13 speed files: %s" % _SPD_BAD[:5]
assert len(_SPD_HOLD) == 18 and len([_h for _h in _SPD_HOLD if "_Mace_" in _h]) == 18, "0.2.13: the 18 named mace Charging children: %s" % _SPD_HOLD
print("0.2.13 speed: %d named Charging children (%d mace); cosmetic-override weapons with a tier: %s" % (len(_SPD_HOLD), len([_h for _h in _SPD_HOLD if "_Mace_" in _h]),
                                                                                                    "; ".join(_SPD_OK)))
for _sf in SPEED_FAMLIST:''')

# ================================================================================================================ 1. the runtime rule
rep('''F(gspd, "public static final String[] F_VARS = %s;" % jarr([",".join(_f["vars"]) for _f in SPEED_FAMLIST]))
''', '''F(gspd, "public static final String[] F_VARS = %s;" % jarr([",".join(_f["vars"]) for _f in SPEED_FAMLIST]))
# 0.2.13: the build-proven items that define main-path swing variables with cosmetic-only overrides ("id=var,var")
F(gspd, "public static final String[] F_OKID = %s;" % jarr([_c for _f in SPEED_FAMLIST for _c in _f["cosm"]]))
''')
rep('''# famCalc: f (0-8) = a tier weapon of family f;''', '''# 0.2.13: may item id define main-path variable var and still get a tier (the build listed it with exactly that variable)?
M(gspd, r"""
public static boolean okVar(String id, String var) {
  if (id == null || var == null) return false;
  String p = id + "=";
  for (int i = 0; i < F_OKID.length; i++) {
    if (!F_OKID[i].startsWith(p)) continue;
    String[] vs = F_OKID[i].substring(p.length()).split(",");
    for (int k = 0; k < vs.length; k++) if (vs[k].equals(var)) return true;
    return false;
  }
  return false;
}""")
# famCalc: f (0-8) = a tier weapon of family f;''')
rep('''    for (int k = 0; k < vs.length; k++) if (v.containsKey(vs[k])) return -2 - f;
''', '''    for (int k = 0; k < vs.length; k++) if (v.containsKey(vs[k]) && !okVar(id, vs[k])) return -2 - f;
''')

# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 and s.count("registerCommand(") == CMD0 and s.count(" = mk(") == MK0, "0.2.13 adds no system / command / class"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))
