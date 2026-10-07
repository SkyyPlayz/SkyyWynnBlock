"""Derive SkyyGear/build_skyygear_0.2.6.py from the LIVE 0.2.5 (build_skyygear_0.2.5.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_5_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_6_patch.py      then      python SkyyGear/build_skyygear_0.2.6.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.6.py (section AG executes every new path; it also re-runs the 0.2.5 harness on the new jar).

0.2.6 = WEAPON SPEED TIERS (Skyy REQUEST 2026-10-05 + LOCKED 2026-10-06, docs/answered/gear.md: "Fully random per item" - any weapon can roll
any tier, same DPS; "Those speed tiers only roll on weapons. Not tools"; design research/cloud/Weapon-Speed-Tiers.md, mechanism
research/Swing-Speed-Spec.md, the 2026-10-06 engine verification). Every melee weapon of the 9 vanilla melee families rolls ONE of four
tiers - Slow, Medium, Fast, Super Fast - and keeps it for good. A tier changes how fast the weapon swings AND how hard each swing hits, so
damage per second stays the same at the same level and modifiers (Wynncraft rule). Tools never get one (pickaxes, hatchets, shovels, hoes,
sickles, every Tool_ id: tool speed comes from tool levels later).
  (1) THE SWING (generated at build time from Assets.zip read in memory - nothing vanilla is committed; the build STOPS when Hytale changes a
      shape this relies on). Tiers are FACTORS on each family's own vanilla cadence (the verifier: weapon swings outlast their cooldown, so
      there is no single "seconds" interval): f = 1.4 Slow, 1 Medium (= vanilla, nothing generated), 0.7 Fast, 0.5 Super Fast; a faster tier
      never swings quicker than SPEED_FLOOR 0.15 s per click (RequireNewClick roots: ~6.7 clicks a second) - only the daggers hit it (their
      0.207 s swing: Fast and Super Fast both become x0.7246). For every family x tier the TAP path of the vanilla Primary root is copied with
      every RunTime x f (the charged keys of every Charging step keep pointing at the vanilla charged attacks: holds are NOT re-timed), each
      swing animation is played from a copied animation set whose Speed is / f (Effects.ItemPlayerAnimationsId, the vanilla NPC / Hylamity
      pattern; the hold animations of Charging steps are left alone), and the root's cooldown is set to (vanilla cooldown or the engine's
      0.35 s default) x f by a TriggerCooldown step. The vanilla Primary root of each family is REPLACED (same path + id, every other field
      kept) by a decision tree on three hidden status effects (SkyyGear_Speed_Slow / _Fast / _SuperFast; Medium = none): no effect = the
      vanilla interaction unchanged (Swing-Speed-Spec 2.3 / SkyyTrees 0.2.3 pattern; no other installed mod replaces these 9 roots -
      checked 2026-10-06). The build re-times every family and every vanilla item with its own InteractionVars and asserts the main swing
      path of each tier is exactly f x vanilla per combo step.
      Families: Sword, Daggers, Longsword, Spear, Battleaxe, Axe, Club, Club flail, Mace. Items that replace a swing-timing variable of
      the main path or use another animation set never get a tier (no line, no change): Crude / Scrap sword, Crude daggers, Crude battleaxe,
      Crude mace, the Doomed battleaxe, the zombie-limb flails, the NPC Praetorian longsword and Scrap mace (the build prints the list).
      NOT IN THIS ROUND (reported): bows / crossbows (draw keys + reload need their own pass), wands / staffs / spellbooks (SkyyArmory owns
      their roots - a SkyyArmory change), the Void scythe and the Incandescent double spear (one item each, other animation sets), shields
      and the Tribal claws (not gear: gear.exclude).
  (2) PER ITEM: the tier is stored in the gear document ("spd": 0 Slow, 1 Medium, 2 Fast, 3 Super Fast), rolled with the swing.odds weights
      (default 25 / 25 / 25 / 25) the FIRST time an identified weapon of a tier family gets a document write while weapon speed tiers are on:
      a new item (craft, drop, chest, admin give) at once, an unidentified one at identify, an item made before 0.2.6 on its first stamp scan
      (first touch). Never changed afterwards: reforge, level up, /gear level / gate / rarity keep it (every rewrite clones the document).
      Rolled through GearSpeed.ensure in GearRoll.newDoc / GearRoll.identify and, as the safety net, GearData.put (one gear.log SPEED line).
  (3) PER PLAYER: GearHandSys (every tick) puts the held weapon's tier effect on the player (3 s, re-put under 1.5 s left on the 1 s check -
      the SkyyTrees margin; the others taken away; nothing for Medium, a tool, a non-tier item, an unidentified one or with swing.tiers off),
      so the replaced root picks the tier. The record of the applied effect is checked against the player every tick (an effect lost to
      death / a world change / another mod is noted and put back at once); states of players gone for 2 minutes are dropped.
  (4) DAMAGE: GearHit.weaponHit multiplies a MELEE hit by the hit weight w of the stored tier - only a damage step the tier's own tap path
      reaches (GearSpeed.normals: the engine's walkChain over the tier root with the item's own vars, labels like the charged index: charged
      holds, signature abilities, the guard and every other root stay x1). w is DERIVED (the draft's rule): the tier's real cycle as written
      into the assets (every combo step behind its leaf cooldown) / the vanilla cycle = 1.4 / 0.7 / 0.5 for 8 families, 1.4 / 0.724638 /
      0.724638 for the daggers - so damage per second is equal to the 6th decimal. The hit uses the weight of the tier the swing really RAN:
      the tier effect on the player (no effect = a vanilla swing = x1, whatever the item stores) and, inside the swap window after a change
      (the previous tier's longest tap step + 150 ms), the smaller of it and the previous one - a weapon swap can never lend a slow weapon's
      hit to a fast swing. Every item swinging with a replaced root counts (a tier-less Crude sword hit while a tier effect still lags is
      weighed too). Per hit x w as well (draft section 4: every per-hit number x w): True Damage and the flat element lines (added after
      armor; STOCHASTIC rounding, so the mean is exact), the victim's knockback (a x w modifier on the KnockbackComponent the hit put) and
      the attacker's stats on hit (SignatureEnergy: the signature meter fills per second, not per click). Not weighted: the Life / Mana Steal
      windows (already per second); durability loss (default OFF, another mod's switch - for when it is turned on).
  (5) TOOLTIP: "Attack Speed: Fast" right above the damage line, which shows the PER-HIT swing damage of that tier ("Damage at Lv 6: 7-9 per
      hit", x w, the Damage % roll as before) and, when the weapon has a charged attack, "Charged at Lv 6: 18-26" (holds are not weighted).
      Only while swing.tiers is on and the family root is SkyyGear's. gear:fn:sig gains "|spd<tier>" (the AH's "rolls differ").
  (6) MANA PER CAST: no staff / wand has a tier in this round (above), so no cast cost changes. GearSpeed.manaCost(base, w) (Mana in
      tenths, the draft's section 5 rule) and the new bridge gear:fn:speed (Object[] { String tier, Double w, Boolean active, Integer tier
      index, String family } or null, for a stack or {id, the stack metadata}) are there for SkyyArmory's tier pass.
  (7) Server Setup -> Gear -> Combat: swing.tiers (switch, live, default ON: off = every weapon vanilla, no effect, no line, no new rolls)
      and swing.odds (text "Slow,Medium,Fast,Super Fast" weights, live). Both are new keys: a missing line means its default (the 0.1.2 rule,
      no one-time config update; a fresh file carries them under their heading). /gear read prints the held weapon's tier line.
  The tier factors and the floor are BUILD constants (the generated assets are made from them), not Server Setup rows.
  Rolling back to 0.2.5 is safe: the vanilla roots come back with the jar, 0.2.5 keeps the unknown "spd" key in every rewrite (clone) and
  ignores it; a tier effect left on a player runs out within 3 s.
UNVERIFIED (needs the game): the client honouring the replaced roots + hidden effects for weapons (SkyyTrees' pickaxe pattern, itself not
yet confirmed in game); the copied animation sets playing faster / slower (Effects.ItemPlayerAnimationsId on a player - vanilla only uses
it for NPC attacks); an empty HUD slot for the hidden effects; a late or cancelled swing for about one ping right after a weapon swap; the
feel of Slow tiers with ClickQueuingTimeout 0.2 s (a click more than 0.2 s early is dropped) and of Fast tiers at ~6 clicks a second.
FIX ROUND 2026-10-06 (critics: DPS / balance, data, engine / feel): signature energy + knockback x w, stochastic flat rounding, the swing's
own tier for the hit weight with a per-family swap window, effect 3 s / 1.5 s, the effect record verified every tick, famOf never caches a
miss + drops its cache on a config epoch / Item reload, GearSpeed.reset() from the Item reload listener, idle player states swept.
Fix round checked (scratch tools/dev/scratch/gear026fix, deleted afterwards): build 539,389 bytes, access audit 0 refused; lint 0 fails;
test_skyygear_0.2.6.py 1431 ok, 0 FAIL, 42 expected deviations (new AG8: one check per fix); mutants (Math.round flat lines / no stats-on-hit
extra / no lost-effect check / the stored tier back in the weight / the old 1 s refresh margin) each FAIL; crosscheck --baseline READY.
CHECKED 2026-10-06 (first build; scratch tools/dev/scratch/gear026, deleted afterwards): build "assembled ...SkyyGear-0.2.6.jar" 537,279 bytes, 106 classes
(99 + 7 kit), 74 rows, 258 speed assets (9 replaced Primary roots), 118 vanilla tier weapons, access audit 20,529 references 0 refused;
python tools/ci/lint.py 0 fails; test_skyygear_0.2.6.py 1423 ok, 0 FAIL, 43 expected deviations (each listed with its reason; every 0.1 ...
0.2.5 section carried + section AG); three mutants (no hit weight / roll on every item / reforge drops the tier) each FAIL the harness;
tools/ci/crosscheck.py --jar SkyyGear-0.2.6.jar --baseline READY (28 jars, 1212 classes -Xverify:all, 82,734 refs 0 refused, command tree
identical).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.5.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.6.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.5"' in s and s.startswith('"""SkyyGear 0.2.5 - build script'), "build_skyygear_0.2.5.py is not the live 0.2.5"
SYS0 = s.count("registerSystem(")
CMD0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.5 - build script (javassist via jpype). GENERATED by tools/gear_0_2_5_patch.py from the LIVE 0.2.4 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.5.py -> SkyyGear/SkyyGear-0.2.5.jar (never --deploy).

0.2.5 = ''', '''"""SkyyGear 0.2.6 - build script (javassist via jpype). GENERATED by tools/gear_0_2_6_patch.py from the LIVE 0.2.5 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.6.py -> SkyyGear/SkyyGear-0.2.6.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.6 = "):].strip() + '''

0.2.5 (the base, everything below is still true unless 0.2.6 above says otherwise):
0.2.5 = ''')
rep('VERSION = "0.2.5"', 'VERSION = "0.2.6"')

# ================================================================================================================ the speed generator
SPEEDGEN = r'''# ================================================================= 0.2.6: WEAPON SPEED TIERS - the build-time generator (see the header)
# ---- SPEED GENERATOR BEGIN (pure Python over the Assets.zip JSON; the 0.2.6 harness exec()s this block from the build script)
SPEED_TIERS = ["Slow", "Medium", "Fast", "Super Fast"]
SPEED_TAG = ["S", "M", "F", "X"]
# hit weight w = the swing time factor f of the tier (Medium = vanilla). PLACEHOLDERS, but BUILD constants: the assets are made from them
SPEED_FACTOR = [1.4, 1.0, 0.7, 0.5]
SPEED_FLOOR = 0.15          # s per click at most this fast (RequireNewClick roots: ~6.7 clicks a second; the verifier's floor)
SPEED_DEFAULT_CD = 0.35     # InteractionTypeUtils.getDefaultCooldown(Primary) - a root without Cooldown (VERIFIED, Swing-Speed-Spec 1)
SPEED_ODDS_DEF = "25,25,25,25"
SPEED_EFF_IDS = ["SkyyGear_Speed_Slow", "", "SkyyGear_Speed_Fast", "SkyyGear_Speed_SuperFast"]
# hidden marker: no icon, no ApplicationEffects, no stats. 3 s, re-put when under 1.5 s is left on the 1 s re-check (the SkyyTrees 0.2.3 margin;
# fix round: 2 s / under 1 s left had no margin - the effect could lapse for a tick every other cycle)
SPEED_EFFECT = {"Duration": 3, "OverlapBehavior": "Overwrite"}
# (family, the vanilla Primary root every item of it uses, its player animation set) - the 9 vanilla melee gear families (the Tribal
# claws are not gear: gear.exclude Weapon_Claws_)
SPEED_FAMS = [("Sword", "Root_Weapon_Sword_Primary", "Sword"), ("Daggers", "Root_Weapon_Daggers_Primary", "Daggers"),
              ("Longsword", "Longsword_Attack", "Longsword"), ("Spear", "Spear_Attack", "Spear"),
              ("Battleaxe", "Root_Weapon_Battleaxe_Primary", "Battleaxe"), ("Axe", "Axe_Attack", "Axe"), ("Club", "Club_Attack", "Club"),
              ("Flail", "Club_Flail_Attack", "Club_Flail"), ("Mace", "Root_Weapon_Mace_Primary", "Mace")]
SPEED_DIR_I = "Server/Item/Interactions/SkyyGear/Speed/"
SPEED_DIR_R = "Server/Item/RootInteractions/SkyyGear/Speed/"
SPEED_DIR_A = "Server/Item/Animations/SkyyGear/"
SPEED_DIR_E = "Server/Entity/Effects/SkyyGear/"


def speed_tree_id(fam):
    return "SkyyGear_Spd_%s" % fam


def speed_walk_id(fam, t):
    return "SkyyGear_SpdWalk%s_%s" % (SPEED_TAG[t], fam)


def speed_anim_id(aset, t):
    return "SkyyGear_Spd%s_%s" % (SPEED_TAG[t], aset)


class SpeedGen:
    """the TAP path of one root re-timed by f (every RunTime x f, combos included, charged hold keys untouched). Reference keys follow
    AzWalker.norm (the engine walk) + MovementCondition's directions + ApplyForce's next keys; any other key holding an interaction stops
    the build (a Hytale update needs a look)."""
    SLOTS_SAFE = ("Type", "Parent", "$Comment", "ChainId", "Var", "RunTime", "Effects", "Selector", "Cooldown", "Rules", "Tags",
                  "DamageCalculator", "DamageEffects", "StatModifiers", "Costs", "EntityStatsOnHit", "Direction", "VelocityConfig",
                  "Knockback", "Config", "Settings", "Forces", "Behaviour", "ValueType", "Match", "EntityEffectIds", "Entity", "EffectId",
                  "OnItemChangeBehavior", "RequiredGameMode", "ChainingAllowance", "DefaultOk", "DisplayProgress", "AllowIndefiniteHold",
                  "HorizontalSpeedMultiplier", "MouseSensitivityAdjustmentTarget", "MouseSensitivityAdjustmentDuration", "Camera",
                  "ChangeVelocityType", "VerticalClamp", "RaycastHeightOffset", "RaycastDistance", "GroundCheckDelay", "Force",
                  "FailOn", "Tool", "UseLatestTarget", "ProjectileId", "Crouching")

    def __init__(self, cw, anim_sets):
        self.cw = cw
        self.A = anim_sets
        self.tcache = {}

    def inter(self, i):
        n = self.cw.inter.get(i)
        return self.cw.js(n) if n else None

    def root(self, i):
        n = self.cw.roots.get(i)
        return self.cw.js(n) if n else None

    def resolved(self, d):
        return self.cw.resolve_parent(d, self.cw.inter) if isinstance(d, dict) else d

    @staticmethod
    def slots(d):
        t = d.get("Type")
        if t == "Charging": return [("Next", "charge"), ("Failed", "i")]
        if t == "Replace": return [("DefaultValue", "r")]
        if t == "Serial": return [("Interactions", "i")]
        if t == "Chaining": return [("Next", "i")]
        if t == "Parallel": return [("Interactions", "r"), ("Next", "i")]
        if t == "Selector": return [("HitEntity", "r"), ("HitBlock", "r"), ("HitEntityRules", "rules"), ("Next", "i"), ("Failed", "i")]
        if t == "Repeat": return [("ForkInteractions", "r"), ("Next", "i"), ("Failed", "i")]
        if t == "MovementCondition":
            return [(k, "i") for k in ("Forward", "Back", "Left", "Right", "ForwardLeft", "ForwardRight", "BackLeft", "BackRight", "Failed")]
        if t == "DamageEntity": return [("Next", "i"), ("Failed", "i"), ("Blocked", "i"), ("AngledDamage", "ang"), ("TargetedDamage", "tgt")]
        if t == "ApplyForce": return [("Next", "i"), ("CollisionNext", "i"), ("GroundNext", "i"), ("Failed", "i")]
        if t is None and "Interactions" in d: return [("Interactions", "i")]
        return [("Interactions", "r"), ("ForkInteractions", "r"), ("Next", "i"), ("Failed", "i"), ("Blocked", "i")]

    def root_refs(self, r):
        if r is None: return []
        if isinstance(r, str):
            d = self.root(r)
            if d is None: raise SystemExit("speed self-check: root interaction %s is missing" % r)
            x = d.get("Interactions")
        elif isinstance(r, dict):
            if "Type" in r or "Parent" in r: return [r]
            x = r.get("Interactions")
        elif isinstance(r, list): x = r
        else: return []
        return x if isinstance(x, list) else ([] if x is None else [x])

    # ---- has a RunTime / a combo anywhere below (only then is a step copied; damage steps keep their vanilla ids and objects)
    def timed(self, ref, root=False, depth=0):
        if depth > 80: raise SystemExit("speed self-check: interaction nesting too deep near %r" % (ref,))
        if ref is None: return False
        if isinstance(ref, list): return any(self.timed(r, root, depth + 1) for r in ref)
        if isinstance(ref, str):
            key = ("R" if root else "I", ref)
            if key not in self.tcache:
                self.tcache[key] = False
                if root: v = self.timed(self.root_refs(ref), False, depth + 1)
                else:
                    d = self.inter(ref)
                    if d is None: raise SystemExit("speed self-check: interaction %s is missing" % ref)
                    v = self.timed_node(d, depth + 1)
                self.tcache[key] = v
            return self.tcache[key]
        if isinstance(ref, dict):
            if root and "Type" not in ref and "Parent" not in ref: return self.timed(ref.get("Interactions"), False, depth + 1)
            return self.timed_node(ref, depth + 1)
        return False

    def timed_node(self, d, depth):
        r = self.resolved(d)
        if "RunTime" in r or r.get("Type") == "Chaining": return True
        for k, kind in self.slots(r):
            v = r.get(k)
            if v is None: continue
            if kind == "i" and self.timed(v, False, depth): return True
            if kind == "r" and self.timed(v, True, depth): return True
            if kind == "charge" and any(self.timed(vv, False, depth) for kk, vv in v.items() if float(kk) == 0): return True
            if kind == "rules" and any(self.timed(x.get("Next"), True, depth) for x in v if isinstance(x, dict)): return True
            if kind == "ang" and any(self.timed(x.get("Next"), False, depth) for x in v if isinstance(x, dict)): return True
            if kind == "tgt" and any(self.timed(x.get("Next"), False, depth) for x in v.values() if isinstance(x, dict)): return True
        return False

    # ---- the copy
    def retime(self, fam, t, f, aset, top_refs):
        self.f, self.prefix, self.aset, self.t = f, "SkyyGear_Spd%s_%s_" % (SPEED_TAG[t], fam), aset, t
        self.out_i, self.out_r, self.memo, self.anims = {}, {}, {}, set()
        top = self.ref(top_refs, False, 0)
        return top, self.out_i, self.out_r, sorted(self.anims)

    def ref(self, v, root, depth):
        if v is None: return None
        if isinstance(v, list): return [self.ref(x, root, depth + 1) for x in v]
        if isinstance(v, str):
            if not self.timed(v, root): return v
            key = ("R" if root else "I", v)
            if key in self.memo: return self.memo[key]
            n = self.prefix + v
            self.memo[key] = n
            if root:
                c = dict(self.root(v))
                c["Interactions"] = self.ref(self.root_refs(v), False, depth + 1)
                self.out_r[n] = c
            else:
                self.out_i[n] = self.node(self.inter(v), depth + 1)
            return n
        if isinstance(v, dict):
            if root and "Type" not in v and "Parent" not in v:
                c = dict(v)
                c["Interactions"] = self.ref(v.get("Interactions"), False, depth + 1)
                return c
            if not self.timed(v): return v
            return self.node(v, depth + 1)
        return v

    def node(self, d, depth):
        if depth > 80: raise SystemExit("speed self-check: re-time too deep")
        r = self.resolved(d)
        typ = r.get("Type")
        sl = self.slots(r)
        for k, v in r.items():
            if k in self.SLOTS_SAFE or k in [x[0] for x in sl]: continue
            if (isinstance(v, str) and v in self.cw.inter) or (isinstance(v, dict) and ("Type" in v or "Interactions" in v)) or \
                    (isinstance(v, list) and any(isinstance(x, dict) and ("Type" in x or "Interactions" in x) for x in v)):
                raise SystemExit("speed self-check: key %s of a %s step holds an interaction the re-timer does not follow: %r" % (k, typ, v))
        if r.get("WaitForAnimationToFinish"):
            raise SystemExit("speed self-check: a WaitForAnimationToFinish step in a weapon swing - its length follows the animation")
        c = dict(d)
        if "RunTime" in r: c["RunTime"] = round(float(r["RunTime"]) * self.f, 4)
        if typ == "Chaining" and self.f > 1.0 and "ChainingAllowance" in r:
            c["ChainingAllowance"] = round(float(r["ChainingAllowance"]) * self.f, 4)
        eff = r.get("Effects")
        if isinstance(eff, dict) and eff.get("ItemAnimationId") and typ != "Charging":
            e = dict(eff)
            src = e.get("ItemPlayerAnimationsId") or self.aset
            e["ItemPlayerAnimationsId"] = speed_anim_id(src, self.t)
            self.anims.add((src, e["ItemAnimationId"]))
            c["Effects"] = e
        for k, kind in sl:
            v = r.get(k)
            if v is None: continue
            if kind == "i": nv = self.ref(v, False, depth + 1)
            elif kind == "r": nv = self.ref(v, True, depth + 1)
            elif kind == "charge":
                nv = dict((kk, self.ref(vv, False, depth + 1) if float(kk) == 0 else vv) for kk, vv in v.items())
            elif kind == "rules":
                nv = []
                for x in v:
                    if isinstance(x, dict) and x.get("Next") is not None:
                        x = dict(x)
                        x["Next"] = self.ref(x["Next"], True, depth + 1)
                    nv.append(x)
            elif kind == "ang":
                nv = []
                for x in v:
                    if isinstance(x, dict) and x.get("Next") is not None:
                        x = dict(x)
                        x["Next"] = self.ref(x["Next"], False, depth + 1)
                    nv.append(x)
            else:
                nv = {}
                for kk, x in v.items():
                    if isinstance(x, dict) and x.get("Next") is not None:
                        x = dict(x)
                        x["Next"] = self.ref(x["Next"], False, depth + 1)
                    nv[kk] = x
            if nv != v or k in d:
                c[k] = nv
        return c


class SpeedDur:
    """per combo step seconds of a TAP on the engine's main path: Parallel = only its first branch keeps the chain busy (the others and a
    Selector's hit chains are FORKED - InteractionContext.fork, VERIFIED for SkyyTrees 0.2.3); Charging = its 0 key (a tap); Replace = the
    item's own var, else its default. mainvars = the Replace variables met on that path."""
    def __init__(self, ints, roots, vars_=None):
        self.I, self.R, self.vars, self.mainvars = ints, roots, vars_ or {}, set()

    def resolved(self, d):
        p = d.get("Parent") if isinstance(d, dict) else None
        if not p or p not in self.I: return d
        return AzWalker.merge(self.resolved(self.I[p]), d)

    def root_list(self, r):
        if r is None: return []
        if isinstance(r, str):
            d = self.R.get(r)
            if d is None: raise SystemExit("speed self-check: root %s is missing" % r)
            x = d.get("Interactions")
        elif isinstance(r, dict):
            if "Type" in r or "Parent" in r: return [r]
            x = r.get("Interactions")
        elif isinstance(r, list): x = r
        else: return []
        return x if isinstance(x, list) else ([] if x is None else [x])

    @staticmethod
    def seq(a, b):
        if len(a) == 1: return [a[0] + x for x in b]
        if len(b) == 1: return a[:-1] + [a[-1] + b[0]]
        raise SystemExit("speed self-check: two combos in one tap")

    @staticmethod
    def mx(ls):
        ls = [l for l in ls if l]
        if not ls: return [0.0]
        n = max(len(l) for l in ls)
        if any(len(l) not in (1, n) for l in ls): raise SystemExit("speed self-check: combo branches of different lengths")
        return [max((l[i] if len(l) > 1 else l[0]) for l in ls) for i in range(n)]

    def lst(self, refs, depth):
        out = [0.0]
        for r in refs:
            out = self.seq(out, self.steps(r, depth + 1))
        return out

    def steps(self, ref, depth=0):
        if depth > 80: raise SystemExit("speed self-check: timing walk too deep")
        if ref is None: return [0.0]
        if isinstance(ref, list): return self.lst(ref, depth)
        if isinstance(ref, str):
            if ref not in self.I: raise SystemExit("speed self-check: interaction %s is missing" % ref)
            ref = self.I[ref]
        d = self.resolved(ref)
        t = d.get("Type")
        rt = float(d.get("RunTime", 0) or 0)
        if t == "Chaining":
            out = []
            for x in d.get("Next") or []:
                s1 = self.steps(x, depth + 1)
                if len(s1) != 1: raise SystemExit("speed self-check: a combo step that is itself a combo")
                out.append(s1[0])
            return self.seq([rt], out) if out else [rt]
        if t == "Charging":
            tap = [v for k, v in (d.get("Next") or {}).items() if float(k) == 0]
            return self.seq([rt], self.steps(tap[0] if tap else None, depth + 1))
        if t == "Replace":
            var = d.get("Var")
            self.mainvars.add(var)
            src = self.vars[var] if var in self.vars else d.get("DefaultValue")
            return self.seq([rt], self.lst(self.root_list(src), depth))
        if t == "Serial": return self.seq([rt], self.lst(d.get("Interactions") or [], depth))
        if t == "Parallel":
            br = d.get("Interactions") or []
            first = self.lst(self.root_list(br[0]), depth) if br else [0.0]
            return self.seq(self.seq([rt], first), self.steps(d.get("Next"), depth + 1))
        if t == "Selector": return self.seq([rt], self.steps(d.get("Next"), depth + 1))
        if t == "MovementCondition":
            return self.seq([rt], self.mx([self.steps(d.get(k), depth + 1) for k in ("Forward", "Back", "Left", "Right", "ForwardLeft",
                                                                                  "ForwardRight", "BackLeft", "BackRight", "Failed") if d.get(k) is not None]))
        if t is None and "Interactions" in d: return self.seq([rt], self.lst(d.get("Interactions"), depth))
        return self.seq([rt], self.mx([self.steps(d.get(k), depth + 1) for k in ("Next", "Failed") if d.get(k) is not None]))


def speed_build(cw, names, items, read_anim):
    """-> (files {path: json text}, fams [dict per family], skipped {item: reason}, eligible [item ids])"""
    anim_sets = {}
    for n in names:
        if n.startswith("Server/Item/Animations/") and n.endswith(".json"):
            b = os.path.basename(n)[:-5]
            if b in anim_sets: raise SystemExit("speed self-check: animation set %s exists twice" % b)
            anim_sets[b] = n
    G = SpeedGen(cw, anim_sets)
    I0 = dict((i, cw.js(p)) for i, p in cw.inter.items())
    R0 = dict((i, cw.js(p)) for i, p in cw.roots.items())
    files, fams, skipped, elig = {}, [], {}, []
    for _t in (0, 2, 3):
        files[SPEED_DIR_E + SPEED_EFF_IDS[_t] + ".json"] = json.dumps(SPEED_EFFECT, indent=2)
    users = {}
    for iid in items:
        it = cw.item(iid)
        if not it or it.get("Quality") == "Template": continue
        pr = (it.get("Interactions") or {}).get("Primary")
        if isinstance(pr, str): users.setdefault(pr, []).append(iid)
    for fam, rid, aset in SPEED_FAMS:
        rpaths = [n for n in names if n.startswith("Server/Item/RootInteractions/") and os.path.basename(n) == rid + ".json"]
        if len(rpaths) != 1: raise SystemExit("speed self-check: vanilla root %s exists %d times" % (rid, len(rpaths)))
        R = R0[rid]
        ri = R.get("Interactions")
        if not (isinstance(ri, list) and len(ri) == 1 and isinstance(ri[0], str)):
            raise SystemExit("speed self-check: vanilla root %s no longer has exactly one interaction id: %s" % (rid, json.dumps(R)))
        if aset not in anim_sets: raise SystemExit("speed self-check: animation set %s is missing" % aset)
        if (R.get("Cooldown") or {}).get("Id"): raise SystemExit("speed self-check: root %s has a named cooldown now" % rid)
        cd = float((R.get("Cooldown") or {}).get("Cooldown", SPEED_DEFAULT_CD))
        dv = SpeedDur(I0, R0)
        van = dv.steps(ri)
        mainvars = sorted(dv.mainvars)
        cad = [max(x, cd) for x in van]
        fe = [1.0] * 4
        for t in (0, 2, 3):
            f = SPEED_FACTOR[t]
            if f < 1.0: f = max(f, SPEED_FLOOR / min(cad))
            fe[t] = round(f, 4)
        tops, leaves, anim_used = {}, {}, {}
        for t in (0, 2, 3):
            top, oi, orr, an = G.retime(fam, t, fe[t], aset, ri)
            if not (isinstance(top, list) and len(top) == 1 and isinstance(top[0], str) and top[0].startswith("SkyyGear_Spd")):
                raise SystemExit("speed self-check: %s %s: the re-timed top is not one copied interaction: %r" % (fam, SPEED_TIERS[t], top))
            for k, v in oi.items():
                if k in cw.inter: raise SystemExit("speed self-check: %s collides with a vanilla interaction" % k)
                files[SPEED_DIR_I + k + ".json"] = json.dumps(v, indent=2)
            for k, v in orr.items():
                if k in cw.roots: raise SystemExit("speed self-check: %s collides with a vanilla root" % k)
                files[SPEED_DIR_R + k + ".json"] = json.dumps(v, indent=2)
            files[SPEED_DIR_R + speed_walk_id(fam, t) + ".json"] = json.dumps({"Interactions": top}, indent=2)
            I2 = dict(I0)
            I2.update(oi)
            R2 = dict(R0)
            R2.update(orr)
            got = SpeedDur(I2, R2).steps(top)
            if len(got) != len(van) or any(abs(a - fe[t] * b) > 1e-3 for a, b in zip(got, van)):
                raise SystemExit("speed self-check: %s %s: the re-timed tap is %s, not %s x %s" % (fam, SPEED_TIERS[t], got, fe[t], van))
            tops[t] = (top[0], I2, R2)
            leaves[t] = {"Type": "TriggerCooldown", "Cooldown": {"Cooldown": round(cd * fe[t], 4)}, "Next": top[0]}
            for src, aid in an:
                anim_used.setdefault(src, set()).add(aid)
        # THE HIT WEIGHT w = the tier's real cycle / the vanilla cycle (draft rule "w is derived, never typed"): every combo step of the
        # re-timed tap as written into the assets (RunTimes rounded to 0.1 ms) behind the leaf cooldown, so damage per second is equal to
        # the 6th decimal (the nominal f only re-times the chain)
        cyc_m = sum(cad)
        wv = [1.0] * 4
        for t in (0, 2, 3):
            st_t = SpeedDur(tops[t][1], tops[t][2]).steps([tops[t][0]])
            lcd = leaves[t]["Cooldown"]["Cooldown"]
            wv[t] = round(sum(max(x, lcd) for x in st_t) / cyc_m, 6)
            if abs(wv[t] - fe[t]) > 1e-3: raise SystemExit("speed self-check: %s %s: the cycle ratio %s is far from f %s" % (fam, SPEED_TIERS[t], wv[t], fe[t]))
        # the copied animation sets: Speed / f on every swing animation the copy plays (an inherited one is copied in whole)
        for src, aids in sorted(anim_used.items()):
            if src not in anim_sets: raise SystemExit("speed self-check: %s plays from the unknown animation set %s" % (fam, src))
            base = read_anim(anim_sets[src])
            chain, cur, seen = [], base, set()
            while isinstance(cur, dict):
                chain.append(cur)
                p = cur.get("Parent")
                if not p or p in seen or p not in anim_sets: break
                seen.add(p)
                cur = read_anim(anim_sets[p])
            for t in (0, 2, 3):
                c = json.loads(json.dumps(base))
                c.setdefault("Animations", {})
                for aid in sorted(aids):
                    e = next((x.get("Animations", {}).get(aid) for x in chain if aid in (x.get("Animations") or {})), None)
                    if not isinstance(e, dict): raise SystemExit("speed self-check: animation %s is not in set %s" % (aid, src))
                    e = dict(e)
                    e["Speed"] = round(float(e.get("Speed", 1.0)) / fe[t], 4)
                    c["Animations"][aid] = e
                files[SPEED_DIR_A + speed_anim_id(src, t) + ".json"] = json.dumps(c, indent=2)
        # the decision tree (an interaction asset) + the replaced vanilla root: no tier effect = the vanilla interaction, unchanged
        tree = ri[0]
        for t in (3, 2, 0):
            tree = {"Type": "EffectCondition", "Match": "All", "EntityEffectIds": [SPEED_EFF_IDS[t]], "Next": leaves[t], "Failed": tree}
        tree = {"Type": "EffectCondition", "Match": "None", "EntityEffectIds": [SPEED_EFF_IDS[x] for x in (0, 2, 3)], "Next": ri[0],
                "Failed": tree}
        files[SPEED_DIR_I + speed_tree_id(fam) + ".json"] = json.dumps(tree, indent=2)
        over = dict(R)
        over["Interactions"] = [speed_tree_id(fam)]
        files[rpaths[0]] = json.dumps(over, indent=2)
        # every vanilla item of the family: the runtime rule (the family's animation set, no main-path variable of its own) must give the
        # exact re-timed tap with ITS vars; items the rule refuses never get a tier
        mine = []
        for iid in sorted(users.get(rid, [])):
            it = cw.item(iid)
            vv = it.get("InteractionVars") or {}
            bad = sorted(k for k in vv if k in mainvars)
            pa = it.get("PlayerAnimationsId")
            if pa != aset:
                skipped[iid] = "%s: plays the %s animation set" % (fam, pa if isinstance(pa, str) else "item's own inline")
                continue
            if bad:
                skipped[iid] = "%s: replaces the swing step(s) %s" % (fam, ", ".join(bad))
                continue
            v0 = SpeedDur(I0, R0, vv).steps(ri)
            for t in (0, 2, 3):
                top0, I2, R2 = tops[t]
                v1 = SpeedDur(I2, R2, vv).steps([top0])
                if len(v1) != len(v0) or any(abs(a - fe[t] * b) > 1e-3 for a, b in zip(v1, v0)):
                    raise SystemExit("speed self-check: %s passes the runtime rule but its %s tap is %s, not %s x %s" % (iid, SPEED_TIERS[t], v1, fe[t], v0))
            mine.append(iid)
        elig += mine
        # smax = the longest single tap step of each tier (seconds): a swing started on the previous tier lands its hit within it (the
        # runtime swap window, GearSpeed.winMs)
        smax = [round(max(van) * fe[t], 4) for t in range(4)]
        fams.append({"fam": fam, "root": rid, "anim": aset, "tree": speed_tree_id(fam), "cd": cd, "steps": van, "cad": cad, "f": fe, "w": wv, "smax": smax,
                     "vars": mainvars, "walk": [speed_walk_id(fam, t) if t != 1 else "" for t in range(4)], "items": mine,
                     "path": rpaths[0], "anims": sorted(anim_used)})
    for k in files:
        b = os.path.basename(k)[:-5]
        if k.startswith(SPEED_DIR_A) and b in anim_sets: raise SystemExit("speed self-check: %s collides with a vanilla animation set" % b)
    return files, fams, skipped, sorted(elig)
# ---- SPEED GENERATOR END


SPEED_FILES, SPEED_FAMLIST, SPEED_SKIPPED, SPEED_ITEMS = speed_build(CW, sorted(AZ_NAMES), VANILLA_WEAPONS,
                                                                      lambda p: json.loads(AZ.read(p).decode("utf-8-sig")))
assert not [k for k in SPEED_FILES if k in EXTRA], "a speed asset path collides with another SkyyGear asset"
assert not [i for i in SPEED_ITEMS if not i.startswith("Weapon_")], "Skyy LOCKED 2026-10-06: tools never get a speed tier"
EXTRA.update(SPEED_FILES)
for _sf in SPEED_FAMLIST:
    print("0.2.6 speed %-9s %-30s cd %.2f tap %s -> x%s (hit weights %s); %d items" % (_sf["fam"], _sf["root"], _sf["cd"],
          [round(_x, 3) for _x in _sf["steps"]], "/".join(str(_x) for _x in _sf["f"]), "/".join(str(_x) for _x in _sf["w"]), len(_sf["items"])))
print("0.2.6 speed: %d tier weapons, %d assets; no tier: %s" % (len(SPEED_ITEMS), len(SPEED_FILES),
                                                               "; ".join("%s (%s)" % (k, v) for k, v in sorted(SPEED_SKIPPED.items()))))

'''
rep('''# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"''', SPEEDGEN + '''# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"''')

# ================================================================================================================ Server Setup rows
rep('''    ("regen.periodMs", "Regen tick", "combat", "int",''', '''    # 0.2.6 WEAPON SPEED TIERS (Skyy LOCKED 2026-10-06: fully random per item, weapons only - never tools). New keys: a missing line
    # means its default (the 0.1.2 rule, no one-time config update)
    ("swing.tiers", "Weapon speed tiers", "combat", "bool", "true", "", "", "", "", "live,danger",
     "Weapons swing Slow / Medium / Fast / Super Fast (same damage per second). Off = all vanilla.", "field:GearCfg.SWING_ON"),
    ("swing.odds", "Weapon speed tier odds", "combat", "text", SPEED_ODDS_DEF, "7", "100", "", "", "live,danger",
     "Weights Slow,Medium,Fast,Super Fast of a weapon's tier." + PH, "field:GearCfg.SWING_ODDS;check=GearCfg.checkSwingOdds"),
    ("regen.periodMs", "Regen tick", "combat", "int",''')
rep('''           "base.spellCurve", "base.hpCurve", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp"}''',
    '''           "base.spellCurve", "base.hpCurve", "steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp",
           # 0.2.6: the weapon speed switch + the tier odds (both change combat numbers / item data)
           "swing.tiers", "swing.odds"}''')
# the fresh default file: the speed rows under their own heading at the end (no one-time update adds them)
rep('''CF_ROWK = ["crit.fx", "crit.fx.sparks", "crit.fx.style", "crit.fx.text", "crit.fx.textOver", "view.hideDamageBox"]''',
    '''CF_ROWK = ["crit.fx", "crit.fx.sparks", "crit.fx.style", "crit.fx.text", "crit.fx.textOver", "view.hideDamageBox"]
# 0.2.6: the weapon speed rows of a fresh file (an existing file gets them the first time they are changed in Server Setup)
SW_HEAD = "# ---- weapon speed tiers (SkyyGear 0.2.6) ----"
SW_ROWK = ["swing.tiers", "swing.odds"]
assert all(32 <= ord(_c) < 127 for _c in SW_HEAD) and "=" not in SW_HEAD''')
rep(r'''    scal("migrate.clampToLevel")
    return "\n".join(L) + "\n"''', r'''    scal("migrate.clampToLevel")
    L += ["", SW_HEAD]         # 0.2.6: the weapon speed rows at the end of a fresh file (no one-time update adds them to an old one)
    for k in SW_ROWK:
        scal(k)
    return "\n".join(L) + "\n"''')

# ================================================================================================================ GearCfg fields + loader
rep('''              ("LVLUP_ON", "boolean", "true"), ("LVLUP_CAP", "int", str(LVLUP_CAP_DEF)), ("HIDE_ABOX", "boolean", "true")]''',
    '''              ("LVLUP_ON", "boolean", "true"), ("LVLUP_CAP", "int", str(LVLUP_CAP_DEF)), ("HIDE_ABOX", "boolean", "true"),
              # 0.2.6 weapon speed tiers
              ("SWING_ON", "boolean", "true"), ("SWING_ODDS", "String", jstr(SPEED_ODDS_DEF))]
F(gcf, "public static volatile double[] SWING_W = new double[] { %s };" % ", ".join(repr(float(_x)) for _x in SPEED_ODDS_DEF.split(",")))''')
rep('''# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''',
    '''# 0.2.6 swing.odds: four weights Slow,Medium,Fast,Super Fast (0-1000000 each, at least one above 0); null = not that shape
M(gcf, r"""
public static double[] swingOdds(String v) {
  if (v == null) return null;
  String[] p = v.trim().split(",");
  if (p.length != 4) return null;
  double[] w = new double[4];
  double tot = 0.0;
  for (int i = 0; i < 4; i++) {
    double x = 0.0;
    try { x = Double.parseDouble(p[i].trim()); } catch (Throwable t) { return null; }
    if (Double.isNaN(x) || Double.isInfinite(x) || x < 0.0 || x > 1000000.0) return null;
    w[i] = x;
    tot = tot + x;
  }
  if (!(tot > 0.0)) return null;
  return w;
}""")
M(gcf, r"""
public static String checkSwingOdds(String key, String value) {
  if (value == null) return null;
  if (swingOdds(value) == null) return "Write four weights Slow,Medium,Fast,Super Fast (0 or more, at least one above 0), e.g. 25,25,25,25.";
  return null;
}""")
# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''')
rep('''  LVLUP_CAP = (int) plong(p, "reforge.levelCap", @LVLCAPDEF@L, 0L, 50L);''', '''  LVLUP_CAP = (int) plong(p, "reforge.levelCap", @LVLCAPDEF@L, 0L, 50L);
  // 0.2.6 weapon speed tiers: a hand-edited odds line the check would refuse falls back to the default with one WARN
  SWING_ON = pbool(p, "swing.tiers", true);
  String swo = ptext(p, "swing.odds", "@SWODDSDEF@");
  if (swingOdds(swo) == null) { @PKG@.Gear.warnOnce("swodds:" + swo, "config.properties: swing.odds=" + swo + " is not four weights Slow,Medium,Fast,Super Fast - the default @SWODDSDEF@ is used"); swo = "@SWODDSDEF@"; }
  SWING_ODDS = swo.trim();
  SWING_W = swingOdds(swo);''')
rep('''   .replace("@STEALDEF@", repr(float(STEAL_MAX_DEF))).replace("@LVLCAPDEF@", str(LVLUP_CAP_DEF))''',
    '''   .replace("@STEALDEF@", repr(float(STEAL_MAX_DEF))).replace("@LVLCAPDEF@", str(LVLUP_CAP_DEF)).replace("@SWODDSDEF@", SPEED_ODDS_DEF)''')

# ================================================================================================================ the class + engine tokens
rep('''gchg = mk("GearCharged")                  # the per-hit judge (DamageSequence meta), /gear charged, charged.log lines''',
    '''gchg = mk("GearCharged")                  # the per-hit judge (DamageSequence meta), /gear charged, charged.log lines
gspd = mk("GearSpeed")                    # 0.2.6: weapon speed tiers - roll, hit weight, tier effect, tooltip lines, gear:fn:speed''')
rep('''+ CHG_CLASSES + CHEST_CLASSES + [gcrp, grlt] + CRIT_CLASSES''', '''+ CHG_CLASSES + CHEST_CLASSES + [gcrp, grlt] + CRIT_CLASSES + [gspd]''')
rep('''T.update(CHT)
''', '''T.update(CHT)
# 0.2.6 weapon speed tiers: the hidden tier effects (the SkyyTrees 0.2.3 calls, VERIFIED there) + the per-step damage range + root ids
SPT = {"EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
       "OVB": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.OverlapBehavior",
       "AEE": "com.hypixel.hytale.server.core.entity.effect.ActiveEntityEffect",
       "I2O": "it.unimi.dsi.fastutil.ints.Int2ObjectMap",
       # fix round: a tier hit's EntityStatsOnHit (SignatureEnergy) x w - the engine's per-hit stat gain (DamageSequence meta, applied by
       # DamageCalculatorSystems$SequenceModifier AFTER the Filter group, VERIFIED bytecode) and the victim's KnockbackComponent x w
       "ESOH": _ICFG + "server.DamageEntityInteraction$EntityStatOnHit",
       "PESOH": "com.hypixel.hytale.protocol.EntityStatOnHit"}
T.update(SPT)
for c, m in ((PB["ECC"], "getActiveEffects"), (PB["ECC"], "addEffect"), (PB["ECC"], "removeEffect"), (PB["ECC"], "getComponentType"),
             (SPT["EFX"], "getAssetMap"), (SPT["AEE"], "getRemainingDuration"), (SPT["OVB"], "OVERWRITE"), (SPT["I2O"], "get"),
             (CHT["DCALC"], "computeDamageRange"), (CHT["RTI"], "getInteractionIds"), (ITM, "getPlayerAnimationsId"),
             (ITM, "getInteractions"), (ITM, "getInteractionVars"), (CHT["ITYPE"], "Primary"),
             (CHT["DSEQ"], "getEntityStatOnHit"), (CHT["DSEQ"], "getSequentialHits"), (SPT["ESOH"], "toPacket"),
             (SPT["PESOH"], "entityStatIndex"), (SPT["PESOH"], "amount"), (SPT["PESOH"], "multipliersPerEntitiesHit"),
             (SPT["PESOH"], "multiplierPerExtraEntityHit"), (PB["KBC"], "addModifier"), (PB["ESM"], "addStatValue")):
    B.probe(pool, c, m)
''')

# ================================================================================================================ GearSpeed (1/2): the core
# (before GearRoll: newDoc / identify roll the tier; GearData.put is the safety net)
SPEED_CORE = r'''# ####################################################################################################################################
# 0.2.6 WEAPON SPEED TIERS (1/2): the per-item tier (document key "spd": 0 Slow, 1 Medium, 2 Fast, 3 Super Fast), its roll and the
# family rule. A family = one of the 9 vanilla melee Primary roots SkyyGear replaces (SPEED_FAMS); an item is in it when its Primary root
# is that root, it plays the family's animation set and it replaces none of the family's main-path swing variables (the build proved the
# re-timed tap exact for every vanilla item that passes this rule). Tools never: not gear weapons (slot 3), and no Tool_ id ever.
# ####################################################################################################################################
F(gspd, "public static final String[] TIER = %s;" % jarr(SPEED_TIERS))
F(gspd, "public static final String[] EFF = %s;" % jarr(SPEED_EFF_IDS))
F(gspd, "public static final String[] F_NAME = %s;" % jarr([_f["fam"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_ROOT = %s;" % jarr([_f["root"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_TREE = %s;" % jarr([_f["tree"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_ANIM = %s;" % jarr([_f["anim"] for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_VARS = %s;" % jarr([",".join(_f["vars"]) for _f in SPEED_FAMLIST]))
F(gspd, "public static final String[] F_WALK = %s;" % jarr([_w for _f in SPEED_FAMLIST for _w in _f["walk"]]))
F(gspd, "public static final double[] F_W = new double[] { %s };" % ", ".join(repr(float(_x)) for _f in SPEED_FAMLIST for _x in _f["w"]))
F(gspd, "public static final double[] F_SMAX = new double[] { %s };" % ", ".join(repr(float(_x)) for _f in SPEED_FAMLIST for _x in _f["smax"]))
F(gspd, "public static final double FLOOR = %r;" % float(SPEED_FLOOR))
F(gspd, "public static final java.security.SecureRandom RNG = new java.security.SecureRandom();")
F(gspd, "public static final java.util.concurrent.ConcurrentHashMap FAM = new java.util.concurrent.ConcurrentHashMap();")   # id -> Integer famCalc
F(gspd, "public static volatile long FAM_EP = -1L;")   # GearCfg.EPOCH the FAM cache was filled under (gear.exclude / include are live)
F(gspd, "public static final java.util.concurrent.atomic.AtomicLong ROLLS = new java.util.concurrent.atomic.AtomicLong();")
# the bare-JVM harness holds the system off while it re-runs the 0.1 ... 0.2.5 sections (their documents must stay as they were); never
# set in game
F(gspd, "public static volatile boolean FORCE_OFF = false;")
M(gspd, "public static boolean on() { return @PKG@.GearCfg.SWING_ON && !FORCE_OFF; }")
M(gspd, "public static String tierName(int t) { return t >= 0 && t < TIER.length ? TIER[t] : \"?\"; }")
M(gspd, r"""
public static int tierOf(@BD@ d) {
  if (d == null) return -1;
  int v = @PKG@.GearData.num(d, "spd", -1);
  return v >= 0 && v <= 3 ? v : -1;
}""")
# swing.odds weights (Slow, Medium, Fast, Super Fast); all 0 = Medium
M(gspd, r"""
public static int pickW(double[] w, double r) {
  double tot = 0.0;
  for (int i = 0; i < 4 && w != null && i < w.length; i++) if (w[i] > 0.0) tot = tot + w[i];
  if (!(tot > 0.0)) return 1;
  double x = r * tot;
  int last = 1;
  for (int i = 0; i < 4 && i < w.length; i++) {
    if (w[i] <= 0.0) continue;
    last = i;
    x = x - w[i];
    if (x < 0.0) return i;
  }
  return last;
}""")
M(gspd, "public static int pick() { return pickW(@PKG@.GearCfg.SWING_W, RNG.nextDouble()); }")
# famCalc: f (0-8) = a tier weapon of family f; -2 - f = an item that swings with family f's replaced root but gets no tier (not gear, another
# animation set, its own main-path swing variables: the Crude sword ...); -1 = neither (a tool never: no Tool_ id, no tool); -100 = the item
# is not loaded (yet) - never cached (fix round: a transient miss no longer sticks until a restart)
M(gspd, r"""
public static int famCalc(String id) {
  if (id == null || id.startsWith("Tool_") || @PKG@.GearData.isTool(id)) return -1;
  @ITM@ it = @PKG@.Gear.item(id);
  if (it == null) return -100;
  java.util.Map in = it.getInteractions();
  Object r = null;
  if (in != null) r = in.get(@ITYPE@.Primary);
  if (!(r instanceof String)) return -1;
  int f = -1;
  for (int i = 0; i < F_ROOT.length; i++) if (F_ROOT[i].equals(r)) { f = i; break; }
  if (f < 0) return -1;
  if (!@PKG@.GearData.isGear(id) || @PKG@.GearData.slotOf(id) != 0) return -2 - f;
  if (!F_ANIM[f].equals(it.getPlayerAnimationsId())) return -2 - f;
  java.util.Map v = it.getInteractionVars();
  if (v != null && F_VARS[f].length() > 0) {
    String[] vs = F_VARS[f].split(",");
    for (int k = 0; k < vs.length; k++) if (v.containsKey(vs[k])) return -2 - f;
  }
  return f;
}""")
# cached per id; the cache is dropped when the config epoch moves (a live gear.exclude edit) and by reset() (an Item asset reload)
M(gspd, r"""
public static int famRaw(String id) {
  if (id == null) return -1;
  long ep = @PKG@.GearCfg.EPOCH;
  if (ep != FAM_EP) { FAM.clear(); FAM_EP = ep; }
  Object o = FAM.get(id);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int f = -100;
  try { f = famCalc(id); } catch (Throwable t) { f = -100; }
  if (f == -100) return -1;
  if (FAM.size() > 4096) FAM.clear();
  FAM.put(id, Integer.valueOf(f));
  return f;
}""")
M(gspd, r"""
public static int famOf(String id) {
  int f = famRaw(id);
  return f >= 0 ? f : -1;
}""")
# the family whose replaced Primary root this item swings with, tier weapon or not (the hit weight: a tier-less sword swings through the same
# tree, so a tier effect still on the player re-times it)
M(gspd, r"""
public static int rootFam(String id) {
  int f = famRaw(id);
  if (f >= 0) return f;
  if (f <= -2 && f >= -1 - F_ROOT.length) return -2 - f;
  return -1;
}""")
# THE roll (spec "rolled once, stored, never changes"): an identified document of a tier weapon without "spd" gets one, while the system is
# on. Every other document comes back as it was (the same object). A clone - the caller's document is never changed in place.
M(gspd, r"""
public static @BD@ ensure(String id, @BD@ doc) {
  if (doc == null || id == null || !on()) return doc;
  try {
    if (tierOf(doc) >= 0 || !@PKG@.GearData.identified(doc) || famOf(id) < 0) return doc;
    @BD@ c = doc.clone();
    int t = pick();
    c.put("spd", new org.bson.BsonInt32(t));
    ROLLS.incrementAndGet();
    @PKG@.GearLog.line("SPEED " + id + " " + TIER[t]);
    return c;
  } catch (Throwable x) {
    @PKG@.Gear.warnOnce("spdroll", "weapon speed: the tier roll failed (" + x + ") - the item keeps no tier for now");
    return doc;
  }
}""")
# the hit weight of tier t in family f = its real cycle / the vanilla cycle (Medium 1; the build's numbers, the dagger floor included)
M(gspd, r"""
public static double weight(int f, int t) {
  if (f < 0 || f >= F_NAME.length || t < 0 || t > 3) return 1.0;
  return F_W[f * 4 + t];
}""")
# Mana per cast of a tier caster (draft section 5: cost x w in tenths). No staff / wand has a tier in 0.2.6 - for SkyyArmory's tier pass.
M(gspd, r"""
public static double manaCost(double base, double w) {
  if (!(base > 0.0)) return 0.0;
  if (!(w > 0.0) || Double.isInfinite(w)) return base;
  return Math.floor(base * w * 10.0 + 0.5) / 10.0;
}""")

'''
rep('''# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded''',
    SPEED_CORE + '''# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded''')
# the roll: a new identified document (craft, admin give, a 0.1.3 newDoc caller) and identify
rep('''  if (ident) d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  return d;
}""")''', '''  if (ident) d.put("mods", rollMods(id, @PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  // 0.2.6: an identified weapon of a speed family rolls its tier now (an unidentified one at identify)
  if (ident) return @PKG@.GearSpeed.ensure(id, d);
  return d;
}""")''')
rep('''  if (by != null) d.put("idBy", new org.bson.BsonString(by.toString()));
  d.put("at", new org.bson.BsonInt64(now));
  return d;''', '''  if (by != null) d.put("idBy", new org.bson.BsonString(by.toString()));
  d.put("at", new org.bson.BsonInt64(now));
  // 0.2.6: an unidentified weapon rolls its speed tier at identify
  return @PKG@.GearSpeed.ensure(id, d);''')
rep('''public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;''', '''public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;
  // 0.2.6: the safety net of the speed roll - every document write of an identified tier weapon without a tier (an item from before 0.2.6
  // on its first stamp scan = "first touch", a SkyyRolls migration, a legacy stamp) rolls it once; a document with one is never touched
  doc = @PKG@.GearSpeed.ensure(s.getItemId(), doc);''')

# ================================================================================================================ GearSpeed (2/2)
# (before GearView.statLines: the tooltip lines; GearHandSys, GearHit, GearFn, GearAdmin and GearCharged come later in the script)
SPEED_LATE = r'''# ####################################################################################################################################
# 0.2.6 WEAPON SPEED TIERS (2/2): which family roots are SkyyGear's, the tier's tap calculators (the hit rule), the hit weight, the per-
# player tier effect (world thread, GearHandSys), the tooltip lines, gear:fn:speed and the /gear read line.
# ####################################################################################################################################
F(gspd, "public static final java.util.concurrent.ConcurrentHashMap NORM = new java.util.concurrent.ConcurrentHashMap();")  # id#t -> Object[] { IdentityHashMap, Long }
# UUID -> Object[] { ItemStack seen, int[] { family, wanted effect tier (-1 none) }, long[] { re-check at, refresh at, applied tier (-1 none,
# -2 not looked at yet), previous tier, applied-change at, last tick } }
F(gspd, "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();")
F(gspd, "public static volatile long SWEEP_AT = 0L;")
F(gspd, "public static volatile boolean IDX_INFO = false;")
# the hit weight of the damage event GearHit.weaponHit just weighed (per world thread): GearHitSys hands it to perHit (stats on hit, knockback)
F(gspd, "public static final ThreadLocal LAST = new ThreadLocal();")
F(gspd, "public static volatile int[] IDX = null;")
F(gspd, "public static volatile long IDX_NEXT = 0L;")
F(gspd, "public static volatile boolean IDX_TOLD = false;")
F(gspd, "public static volatile int[] ACT = null;")
F(gspd, "public static volatile long ACT_AT = 0L;")
F(gspd, "public static final java.util.concurrent.atomic.AtomicBoolean FAILED_ONCE = new java.util.concurrent.atomic.AtomicBoolean(false);")
# counters (/gear read, the harness): 0 effects added, 1 effects removed, 2 weighted hits, 3 hits kept x1 (not a tap step), 4 walks, 5 re-walks,
# 6 knockbacks weighted, 7 stats-on-hit weighted, 8 tier effects found lost (death, world change, another mod)
F(gspd, "public static final java.util.concurrent.atomic.AtomicLongArray N = new java.util.concurrent.atomic.AtomicLongArray(9);")
# the first interaction id of a root asset ("missing" / "empty" / "unknown")
M(gspd, r"""
public static String rootFirst(String rid) {
  try {
    Object o = @RTI@.getAssetMap().getAsset(rid);
    if (!(o instanceof @RTI@)) return "missing";
    String[] xs = ((@RTI@) o).getInteractionIds();
    if (xs == null || xs.length == 0) return "empty";
    return xs[0];
  } catch (Throwable t) { return "unknown"; }
}""")
# family f works only while its vanilla Primary root is SkyyGear's tree (another mod replacing it = no tier for that family: no line, x1);
# re-checked every 30 s (an asset reload)
M(gspd, r"""
public static boolean active(int f) {
  if (f < 0 || f >= F_ROOT.length) return false;
  int[] a = ACT;
  long now = System.currentTimeMillis();
  if (a == null || now >= ACT_AT) {
    a = new int[F_ROOT.length];
    for (int i = 0; i < a.length; i++) a[i] = F_TREE[i].equals(rootFirst(F_ROOT[i])) ? 1 : 0;
    ACT = a;
    ACT_AT = now + 30000L;
  }
  return a[f] == 1;
}""")
M(gspd, r"""
public static void reset() {
  ACT = null;
  NORM.clear();
  FAM.clear();
  IDX = null;
  IDX_NEXT = 0L;
  IDX_TOLD = false;
}""")
# fix round: an Item asset reload (the GearBoxL listener, LoadedAssetsEvent(Item)) drops these caches - GearBoxL is compiled before this
# class, so the call goes in front of its accept() here
gboxl.getDeclaredMethod("accept").insertBefore(J("{ try { @PKG@.GearSpeed.reset(); } catch (Throwable t3) { } }"))
# the one INFO line once the tier effects resolve (the first held weapon after the assets loaded): how many family roots are SkyyGear's
M(gspd, r"""
public static String rootsText() {
  int n = 0;
  StringBuilder no = new StringBuilder();
  for (int i = 0; i < F_ROOT.length; i++) {
    if (active(i)) n++;
    else { if (no.length() > 0) no.append(", "); no.append(F_ROOT[i]).append(" = ").append(rootFirst(F_ROOT[i])); }
  }
  return "weapon speed tiers ready: " + n + "/" + F_ROOT.length + " melee families on SkyyGear's swing roots" + (no.length() > 0 ? " - NOT SkyyGear's (no tier works there): " + no.toString() : "");
}""")
M(gspd, r"""
public static boolean shows(String id, @BD@ d) {
  if (!on() || id == null || d == null || !@PKG@.GearData.identified(d) || tierOf(d) < 0) return false;
  // the tier effects failed to load (asset pack missing): every weapon swings vanilla - no line claims otherwise
  if (IDX == null && IDX_TOLD) return false;
  int f = famOf(id);
  return f >= 0 && active(f);
}""")
# THE HIT RULE: the damage calculators the tier's own TAP path reaches = the engine's walkChain over the tier walk root with the item's vars
# (the GearChg collector: a ChargingTag > 0 edge = a held charge, a Failed / Blocked edge = normal), so only those hits are weighted -
# never a charged hold, a signature ability, the guard or any other root. The damage steps are the vanilla assets (never copied), so the
# set is the same for every tier (the Medium tooltip reads the Fast walk). Any item swinging with a replaced root walks (rootFam): a tier-less
# sword's taps are known too.
M(gspd, r"""
public static java.util.IdentityHashMap walk(String id, int t) {
  java.util.IdentityHashMap m = new java.util.IdentityHashMap();
  int f = rootFam(id);
  if (f < 0 || t < 0 || t > 3 || t == 1) return m;
  String rid = F_WALK[f * 4 + t];
  try {
    Object root = @RTI@.getAssetMap().getAsset(rid);
    if (!(root instanceof @RTI@)) return m;
    @ITM@ it = @PKG@.Gear.item(id);
    java.util.Map vars = null;
    if (it != null) vars = it.getInteractionVars();
    @PKG@.GearChgState st = new @PKG@.GearChgState();
    @ICTX@ ctx = @ICTX@.withoutEntity();
    ctx.setInteractionVarsGetter(new @PKG@.GearChgVars(vars == null ? new java.util.HashMap() : vars));
    @IMGR@.walkChain(new @PKG@.GearChgWalk(st, -1.0f, -1.0f, false), @ITYPE@.Primary, ctx, (@RTI@) root);
    for (int i = 0; i < st.recs.size(); i++) {
      Object[] r = (Object[]) st.recs.get(i);
      if (((Integer) r[4]).intValue() != 0) continue;
      if (((Float) r[1]).floatValue() > 0.0f) continue;
      m.put(r[0], Boolean.TRUE);
    }
    N.incrementAndGet(4);
  } catch (Throwable x) { @PKG@.Gear.warnOnce("spdwalk:" + id, "weapon speed: the tier walk of " + id + " failed (" + x + ") - its hits stay x1"); }
  return m;
}""")
M(gspd, r"""
public static java.util.IdentityHashMap normals(String id, int t, boolean again) {
  String k = id + "#" + t;
  Object[] e = (Object[]) NORM.get(k);
  long now = System.currentTimeMillis();
  if (e != null && (!again || now - ((Long) e[1]).longValue() < 30000L)) return (java.util.IdentityHashMap) e[0];
  java.util.IdentityHashMap m = walk(id, t);
  if (NORM.size() > 4096) NORM.clear();
  NORM.put(k, new Object[] { m, Long.valueOf(now) });
  if (again && e != null) N.incrementAndGet(5);
  return m;
}""")
M(gspd, r"""
public static boolean tapHit(String id, int t, Object calc) {
  if (calc == null || id == null) return false;
  if (normals(id, t, false).containsKey(calc)) return true;
  return normals(id, t, true).containsKey(calc);
}""")
M(gspd, r"""
public static Object calcOf(@DMG@ d) {
  try {
    Object so = ((@IMS@) d).getIfPresentMetaObject(@DCSYS@.DAMAGE_SEQUENCE);
    if (so instanceof @DSEQ@) return ((@DSEQ@) so).getDamageCalculator();
  } catch (Throwable t) { }
  return null;
}""")
# the swap window of tier t in family f (ms): its longest single tap step + 150 ms (a tick and the click that raced the effect change) - a
# swing started on the previous tier lands its hit inside it. Fix round: was a flat 1 s, which cost a fresh Slow weapon its x1.4 for a second
M(gspd, r"""
public static long winMs(int f, int t) {
  if (f < 0 || f >= F_NAME.length) return 1000L;
  int k = t < 0 || t > 3 ? 1 : t;
  return (long) (F_SMAX[f * 4 + k] * 1000.0) + 150L;
}""")
# THE HIT WEIGHT = the weight of the tier the swing really RAN: the tier effect on the player (GearHandSys keeps the record true every tick,
# a lost effect included) and, inside the swap window after a change, the smaller of it and the one before it (a swing that started on the
# old tier, or a click that raced the change - never a slow tier's weight on a fast swing). The stored tier is not consulted (fix round): no
# effect = a vanilla swing = x1, whatever the item says. A hotbar swap to another item id cancels the swing in flight (Interaction
# onItemChangeBehavior defaults to Cancel, VERIFIED bytecode: Interaction.<init> + tickInternal); two items of the same id do not, which the
# window covers.
M(gspd, r"""
public static double appliedW(java.util.UUID u, int f) {
  Object[] s = null;
  if (u != null) s = (Object[]) ST.get(u);
  if (s == null) return 1.0;
  long[] L = (long[]) s[2];
  int ap = (int) L[2];
  double w = weight(f, ap < 0 ? 1 : ap);
  int pv = (int) L[3];
  if (pv != ap && System.currentTimeMillis() - L[4] < winMs(f, pv)) {
    double w2 = weight(f, pv < 0 ? 1 : pv);
    if (w2 < w) w = w2;
  }
  return w;
}""")
# GearHit.weaponHit (a MELEE hit of a player): a TAP step of an item that swings with a replaced root -> appliedW; everything else x1
# (charged holds, signatures, guards, other roots, switched off). The weight is kept for perHit (GearHitSys, same event, same thread).
M(gspd, r"""
public static double hitWeight(@DMG@ d, java.util.UUID u, @IS@ main) {
  try {
    if (!on() || d == null || main == null || main.isEmpty() || u == null) return 1.0;
    String id = main.getItemId();
    int f = rootFam(id);
    if (f < 0 || !active(f)) return 1.0;
    if (!tapHit(id, 2, calcOf(d))) { N.incrementAndGet(3); return 1.0; }
    double w = appliedW(u, f);
    if (w != 1.0) {
      N.incrementAndGet(2);
      LAST.set(new Object[] { d, Double.valueOf(w) });
    }
    return w;
  } catch (Throwable x) {
    @PKG@.Gear.warnOnce("spdhit", "weapon speed: the hit weight failed (" + x + ") - hits stay x1");
    return 1.0;
  }
}""")
# the extra a stat-on-hit line owes a hit of weight w: the engine adds amount x its multiplier for the h-th entity this swing hit
# (EntityStatOnHit.processEntityStatsOnHit, VERIFIED bytecode: h <= the array -> array[h - 1], else multiplierPerExtraEntityHit); the extra
# makes it amount x multiplier x w
M(gspd, r"""
public static float statExtra(float amount, float[] mults, float extra, int h, double w) {
  if (h <= 0 || w == 1.0) return 0.0f;
  float mu = (mults != null && h <= mults.length) ? mults[h - 1] : extra;
  return (float) ((w - 1.0) * (double) mu * (double) amount);
}""")
# GearHitSys (Filter group), right after weaponHit, for the same damage event: a weighted tap also weighs (draft section 4, "every per-hit
# number x w") (a) the victim's knockback - the KnockbackComponent DamageEntityInteraction put before the event gets a x w modifier (applied
# by KnockbackSystems with the others) and (b) the attacker's stats on hit (SignatureEnergy: the signature meter fills per second, not per
# click) - the engine's own gain comes later (DamageCalculatorSystems$SequenceModifier runs AFTER the Filter group and counts this hit as
# getSequentialHits() + 1, VERIFIED bytecode)
M(gspd, r"""
public static void perHit(@DMG@ d, @CB@ buf, @REF@ att, @REF@ vic) {
  Object[] l = (Object[]) LAST.get();
  if (l == null) return;
  LAST.set(null);
  if (d == null || l[0] != d || buf == null) return;
  double w = ((Double) l[1]).doubleValue();
  if (w == 1.0 || !(w > 0.0) || d.isCancelled()) return;
  try {
    if (vic != null && vic.isValid()) {
      @KBC@ kc = (@KBC@) buf.getComponent(vic, @KBC@.getComponentType());
      if (kc != null) { kc.addModifier(w); N.incrementAndGet(6); }
    }
  } catch (Throwable x) { @PKG@.Gear.warnOnce("spdkb", "weapon speed: the knockback weight failed (" + x + ") - knockback stays vanilla"); }
  try {
    if (att == null || !att.isValid()) return;
    Object so = ((@IMS@) d).getIfPresentMetaObject(@DCSYS@.DAMAGE_SEQUENCE);
    if (!(so instanceof @DSEQ@)) return;
    @ESOH@[] es = ((@DSEQ@) so).getEntityStatOnHit();
    if (es == null || es.length == 0) return;
    @ESM@ m = (@ESM@) buf.getComponent(att, @ESM@.getComponentType());
    if (m == null) return;
    int h = ((@DSEQ@) so).getSequentialHits() + 1;
    for (int i = 0; i < es.length; i++) {
      if (es[i] == null) continue;
      @PESOH@ p = (@PESOH@) es[i].toPacket();
      if (p == null || p.entityStatIndex < 0) continue;
      float x = statExtra(p.amount, p.multipliersPerEntitiesHit, p.multiplierPerExtraEntityHit, h, w);
      if (x != 0.0f) { m.addStatValue(p.entityStatIndex, x); N.incrementAndGet(7); }
    }
  } catch (Throwable x) { @PKG@.Gear.warnOnce("spdstat", "weapon speed: the stats-on-hit weight failed (" + x + ") - the signature meter fills per click"); }
}""")
# True Damage + the flat element lines (GearHit.info [1] / [5], added after armor by GearTrueSys) x the same weight, STOCHASTICALLY rounded
# (floor, +1 with the chance of the fraction: the mean is exactly v x w, so DPS stays equal - fix round: Math.round made True Damage 1 on
# Super Fast a flat +100%)
M(gspd, r"""
public static int sround(double x, double r) {
  if (!(x > 0.0)) return (int) Math.round(x);
  double b = Math.floor(x);
  return (int) b + (r < x - b ? 1 : 0);
}""")
M(gspd, r"""
public static void scaleInfo(Object[] inf, double w) {
  if (inf == null || inf.length < 6 || w == 1.0) return;
  for (int k = 1; k < 6; k = k + 4) {
    if (inf[k] instanceof Integer) inf[k] = Integer.valueOf(sround((double) ((Integer) inf[k]).intValue() * w, java.util.concurrent.ThreadLocalRandom.current().nextDouble()));
  }
}""")
# ---- the per-player tier effect (world thread: GearHandSys every tick)
M(gspd, r"""
public static synchronized boolean ready() {
  if (IDX != null) return true;
  long now = System.currentTimeMillis();
  if (now < IDX_NEXT) return false;
  IDX_NEXT = now + 10000L;
  int[] r = new int[] { -1, -1, -1, -1 };
  for (int t = 0; t < 4; t++) {
    if (t == 1) continue;
    int x = Integer.MIN_VALUE;
    try { x = @EFX@.getAssetMap().getIndex(EFF[t]); } catch (Throwable e) { x = Integer.MIN_VALUE; }
    if (x == Integer.MIN_VALUE || x < 0) {
      if (!IDX_TOLD) { IDX_TOLD = true; @PKG@.Gear.warn("weapon speed: the tier effect " + EFF[t] + " is not loaded (asset pack missing?) - weapons swing at vanilla speed (retried every 10 s)"); }
      return false;
    }
    r[t] = x;
  }
  IDX = r;
  if (!IDX_INFO) { IDX_INFO = true; @PKG@.Gear.info(rootsText()); }
  return true;
}""")
M(gspd, r"""
public static int wantOf(@IS@ h, int[] out) {
  out[0] = -1;
  out[1] = -1;
  if (!on() || h == null || h.isEmpty()) return -1;
  String id = h.getItemId();
  int f = famOf(id);
  if (f < 0 || !active(f)) return -1;
  @BD@ d = @PKG@.GearData.effective(id, h.getMetadata());
  if (d == null || !@PKG@.GearData.identified(d)) return -1;
  int t = tierOf(d);
  out[0] = f;
  out[1] = t;
  return t;
}""")
M(gspd, r"""
public static Object[] state(java.util.UUID u) {
  Object[] s = (Object[]) ST.get(u);
  if (s == null) {
    s = new Object[] { null, new int[] { -1, -1 }, new long[] { 0L, 0L, -2L, -1L, 0L, System.currentTimeMillis() } };
    ST.put(u, s);
  }
  return s;
}""")
# every other tier effect off; the wanted one (3 s) on when missing or under 1.5 s left (want -1 = none). Fix round: 3 s / 1.5 s like
# SkyyTrees 0.2.3 - with 2 s re-put under 1 s on a 1 s re-check the effect could run out for a tick (a vanilla swing) every other cycle
M(gspd, r"""
public static void put(@CB@ cb, @REF@ ref, @ECC@ ecc, int want) {
  int[] idx = IDX;
  @I2O@ map = ecc.getActiveEffects();
  if (idx == null || map == null) return;
  for (int t = 0; t < 4; t++) {
    if (t == 1 || t == want) continue;
    if (map.get(idx[t]) != null) { ecc.removeEffect(ref, idx[t], cb); N.incrementAndGet(1); }
  }
  if (want < 0 || want == 1) return;
  Object o = map.get(idx[want]);
  if (o instanceof @AEE@ && ((@AEE@) o).getRemainingDuration() >= 1.5f) return;
  @EFX@ fx = (@EFX@) @EFX@.getAssetMap().getAsset(idx[want]);
  if (fx == null) return;
  ecc.addEffect(ref, idx[want], fx, 3.0f, @OVB@.OVERWRITE, cb);
  N.incrementAndGet(0);
}""")
# drop the state of players not ticked for 2 minutes (a disconnect that raced one more GearHandSys tick re-created it) - at most once a minute
M(gspd, r"""
public static int sweep(long now) {
  if (now < SWEEP_AT) return 0;
  SWEEP_AT = now + 60000L;
  int n = 0;
  java.util.Iterator it = ST.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] s = (Object[]) e.getValue();
    long[] L = null;
    if (s != null) L = (long[]) s[2];
    if (L == null || now - L[5] > 120000L) { it.remove(); n++; }
  }
  return n;
}""")
# one player, one tick: the held stack decides (re-read on a new stack and every second - a config change, a level-up of the document). The
# record of the applied effect is kept TRUE every tick (fix round): an effect the player lost (death, a world change, another mod's clear)
# is noted at once (the hit weight follows it) and put back; the first tick of a player looks at the component (a stray effect from before
# is removed). The effect is touched only on a change, a loss or the 1 s refresh. Medium / no tier / a tool / switched off = no effect.
M(gspd, r"""
public static void tick(@CB@ cb, @REF@ ref, java.util.UUID u, @IS@ h) {
  if (cb == null || ref == null || u == null) return;
  try {
    long now = System.currentTimeMillis();
    sweep(now);
    Object[] s = state(u);
    int[] W = (int[]) s[1];
    long[] L = (long[]) s[2];
    L[5] = now;
    if (s[0] != h || now >= L[0]) {
      s[0] = h;
      L[0] = now + 1000L;
      int[] o = new int[2];
      int t = wantOf(h, o);
      W[0] = o[0];
      W[1] = t == 1 ? -1 : t;
    }
    int eff = W[1];
    int ap = (int) L[2];
    if (eff == ap && eff < 0) return;
    if (!ready()) return;
    int[] idx = IDX;
    if (idx == null) return;
    @ECC@ ecc = (@ECC@) cb.getComponent(ref, @ECC@.getComponentType());
    if (ecc == null) return;
    if (ap >= 0) {
      @I2O@ map = ecc.getActiveEffects();
      if (map == null || map.get(idx[ap]) == null) {
        L[3] = (long) ap;
        L[4] = now;
        L[2] = -1L;
        ap = -1;
        L[1] = 0L;
        N.incrementAndGet(8);
      }
    }
    if (eff == ap && (eff < 0 || now < L[1])) return;
    put(cb, ref, ecc, eff);
    if (eff != ap) {
      L[3] = ap < -1 ? -1L : (long) ap;
      L[4] = now;
      L[2] = (long) eff;
    }
    L[1] = now + 1000L;
  } catch (Throwable x) {
    if (FAILED_ONCE.compareAndSet(false, true)) @PKG@.Gear.warn("weapon speed: the tier effect could not be set (logged once): " + x);
  }
}""")
M(gspd, "public static void forget(java.util.UUID u) { if (u != null) ST.remove(u); }")
# ---- the tooltip: { "Attack Speed: Fast", "Damage at Lv 6: 7-9 per hit" (the tap's own steps x the level multiplier x w), "Charged at
# Lv 6: 18-26" (full-charge steps, x the level multiplier only) or null }; null = no tier line for this item
M(gspd, r"""
public static float[] calcRange(java.util.Iterator it) {
  float lo = Float.MAX_VALUE;
  float hi = 0f;
  float[] a = new float[2];
  while (it.hasNext()) {
    Object c = it.next();
    if (!(c instanceof @DCALC@)) continue;
    a[0] = 0f;
    a[1] = 0f;
    try { ((@DCALC@) c).computeDamageRange(1.0, a); } catch (Throwable t) { continue; }
    if (a[1] <= 0f) continue;
    float x = a[0] < 0f ? 0f : a[0];
    if (x < lo) lo = x;
    if (a[1] > hi) hi = a[1];
  }
  if (hi <= 0f) return null;
  if (lo == Float.MAX_VALUE || lo > hi) lo = hi;
  return new float[] { lo, hi };
}""")
M(gspd, r"""
public static float[] tapRange(String id, int t) {
  return calcRange(normals(id, t == 1 ? 2 : t, false).keySet().iterator());
}""")
M(gspd, r"""
public static float[] chargedRange(String id) {
  try {
    Object[] e = @PKG@.GearChg.ensure(id);
    if (!@PKG@.GearChg.found(e)) return null;
    java.util.IdentityHashMap m = (java.util.IdentityHashMap) e[0];
    java.util.ArrayList l = new java.util.ArrayList();
    java.util.Iterator it = m.keySet().iterator();
    while (it.hasNext()) {
      Object c = it.next();
      int[] fl = (int[]) m.get(c);
      if (fl != null && fl[0] == @PKG@.GearChg.FULL && fl[1] != 3) l.add(c);
    }
    return calcRange(l.iterator());
  } catch (Throwable x) { return null; }
}""")
M(gspd, r"""
public static String[] tipLines(String id, @BD@ d) {
  if (!shows(id, d)) return null;
  int t = tierOf(d);
  int f = famOf(id);
  double w = weight(f, t);
  String[] out = new String[] { "Attack Speed: " + TIER[t], null, null };
  try {
    boolean on = @PKG@.GearBase.on();
    double m = on ? @PKG@.GearBase.mult(id, d, false) : 1.0;
    String lab = on && !@PKG@.GearBase.asVanilla(id, d, false) ? " at Lv " + @PKG@.GearLevel.level(id, d) + ": " : ": ";
    float[] r = tapRange(id, t);
    if (r != null) out[1] = "Damage" + lab + @PKG@.GearBase.rangeText(new float[] { (float) ((double) r[0] * m * w), (float) ((double) r[1] * m * w) }) + " per hit";
    float[] c = chargedRange(id);
    if (r != null && c != null) out[2] = "Charged" + lab + @PKG@.GearBase.rangeText(new float[] { (float) ((double) c[0] * m), (float) ((double) c[1] * m) });
  } catch (Throwable x) { }
  return out;
}""")
# gear:fn:speed (mode 11): Object[] { String tier, Double hit weight, Boolean active (shown + applied now), Integer tier index, String
# family } or null (no tier family / no tier yet). SkyyArmory's tier pass: Mana per cast = GearSpeed.manaCost(base, weight)
M(gspd, r"""
public static Object[] info(String id, @BD@ d) {
  int f = famOf(id);
  int t = tierOf(d);
  if (f < 0 || t < 0) return null;
  return new Object[] { TIER[t], Double.valueOf(weight(f, t)), Boolean.valueOf(shows(id, d)), Integer.valueOf(t), F_NAME[f] };
}""")
M(gspd, r"""
public static String describe(String id, @BD@ d, java.util.UUID u) {
  String s = "weapon speed: ";
  if (id == null) return s + "no item";
  if (id.startsWith("Tool_") || @PKG@.GearData.isTool(id)) return s + "tools never get a tier (Skyy 2026-10-06)";
  int f = famOf(id);
  if (f < 0) return s + "no tier for this item (not one of the " + F_NAME.length + " melee families, or it changes its own swing steps / animation set)";
  int t = tierOf(d);
  String st;
  if (t >= 0) st = TIER[t] + " - swing time and hit x" + @PKG@.Gear.fnum(weight(f, t));
  else st = @PKG@.GearData.identified(d) ? "no tier yet (rolls on its next document write while swing.tiers is on)" : "rolls at identify";
  String ap = "none";
  Object[] so = null;
  if (u != null) so = (Object[]) ST.get(u);
  if (so != null) { int a = (int) ((long[]) so[2])[2]; if (a >= 0) ap = TIER[a]; }
  return s + F_NAME[f] + " family (" + (active(f) ? "SkyyGear's swing root loaded" : "root " + F_ROOT[f] + " is NOT SkyyGear's (" + rootFirst(F_ROOT[f]) + ") - no tier works") + "), " + st + "; swing.tiers " + (on() ? "on" : "OFF") + "; your tier effect now: " + ap + "; counters " + N.toString();
}""")
M(gspd, r"""
public static String readyText() {
  return "weapon speed tiers " + (on() ? "on" : "OFF (swing.tiers)") + " (" + F_ROOT.length + " melee families, odds " + @PKG@.GearCfg.SWING_ODDS + "; the swing roots + tier effects are checked when a player first holds a weapon - one INFO line, /gear read)";
}""")

'''
rep('''# base value lines + modifier lines of an identified document (the tooltip body, the Reforge page's line columns)''',
    SPEED_LATE + '''# base value lines + modifier lines of an identified document (the tooltip body, the Reforge page's line columns)''')
# the tooltip: "Attack Speed: <tier>" + the per-hit swing line (+ the charged range) replace the plain damage line of a tier weapon
rep('''    Object[] sh = @PKG@.GearBase.shots(id, d);
    if (sh == null || sh[1] == null) {''', '''    Object[] sh = @PKG@.GearBase.shots(id, d);
    // 0.2.6 WEAPON SPEED TIERS: "Attack Speed: Fast" + the PER-HIT swing damage of that tier (x its hit weight) + the charged range
    String[] spd = null;
    if (sh == null && slot == 0) spd = @PKG@.GearSpeed.tipLines(id, d);
    if (spd != null) {
      add(txt, col, spd[0], null);
      if (spd[1] != null) {
        add(txt, col, spd[1] + (hasDmg ? " (" + valText("dmg", dmg) + ")" : ""), null);
        dmgShown = hasDmg;
        if (spd[2] != null) add(txt, col, spd[2], null);
      }
    }
    if ((sh == null || sh[1] == null) && (spd == null || spd[1] == null)) {''')
rep('''  String s = id + "|" + quality + "|" + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + "|" + @PKG@.GearData.identified(d) + "|" + @PKG@.GearData.mods(d).toString() + "|" + @PKG@.GearLevel.level(id, d);
  return Integer.toHexString(s.hashCode()) + Integer.toHexString(s.length());''', '''  String s = id + "|" + quality + "|" + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + "|" + @PKG@.GearData.identified(d) + "|" + @PKG@.GearData.mods(d).toString() + "|" + @PKG@.GearLevel.level(id, d);
  // 0.2.6: two items that differ only in their speed tier "differ" (the AH caveat); an item without a tier keeps its 0.2.5 sig
  int sp = @PKG@.GearSpeed.tierOf(d);
  if (sp >= 0) s = s + "|spd" + sp;
  return Integer.toHexString(s.hashCode()) + Integer.toHexString(s.length());''')
# the per-player tier effect, every tick, from the hand snapshot's own stack
rep('''    @PKG@.GearHand.seen(pr.getUuid(), @INVC@.getItemInHand(cb, r));
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''', '''    @IS@ held = @INVC@.getItemInHand(cb, r);
    @PKG@.GearHand.seen(pr.getUuid(), held);
    // 0.2.6: the held weapon's speed tier effect (SkyyGear's Primary roots pick the re-timed swing from it)
    @PKG@.GearSpeed.tick(cb, r, pr.getUuid(), held);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("handsys", "hand snapshot failed: " + t); }''')
rep('''  @PKG@.GearHand.forget(u);''', '''  @PKG@.GearHand.forget(u);
  @PKG@.GearSpeed.forget(u);''')
# the hit weight (melee only) + True Damage / flat element lines x the same weight
rep('''  if (m != 1.0) d.setAmount((float) ((double) d.getAmount() * m));
  if (!@PKG@.GearCfg.PART_STATS) return null;''', '''  // 0.2.6 WEAPON SPEED TIERS: a melee tap of a tier weapon hits x its hit weight (Slow x1.4 ... Super Fast x0.5) - the same damage per second
  double sw = shot ? 1.0 : @PKG@.GearSpeed.hitWeight(d, u, main);
  if (sw != 1.0) m = m * sw;
  if (m != 1.0) d.setAmount((float) ((double) d.getAmount() * m));
  if (!@PKG@.GearCfg.PART_STATS) return null;''')
rep('''  if (cw != null) @PKG@.GearCharged.note(u, pr, main, chg, cw[0], spell, t[I_CHG], a0, a);
  return info(u, t);''', '''  if (cw != null) @PKG@.GearCharged.note(u, pr, main, chg, cw[0], spell, t[I_CHG], a0, a);
  Object[] inf = info(u, t);
  if (sw != 1.0) @PKG@.GearSpeed.scaleInfo(inf, sw);
  return inf;''')
# gear:fn:speed
rep('''    if (m == 10) return curve(o);''', '''    if (m == 10) return curve(o);
    if (m == 11) {
      Object[] xs = x(o);
      @BD@ d = docOf(xs);
      if (d == null) return null;
      return @PKG@.GearSpeed.info((String) xs[0], d);
    }''')
rep('''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve")))''',
    '''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve", "speed")))''')
# /gear read: the held weapon's tier line
rep('''    msg(pr, @PKG@.GearBase.describe(id, d));
  }''', '''    msg(pr, @PKG@.GearBase.describe(id, d));
    // 0.2.6: the weapon speed tier (family, tier, factor, the effect on you now, counters)
    msg(pr, @PKG@.GearSpeed.describe(id, d, pr.getUuid()));
  }''')
# the ready line
rep('''+ @PKG@.GearBox.readyText() + "; " + @PKG@.GearABox.readyText() + "; Reforge level up "''',
    '''+ @PKG@.GearBox.readyText() + "; " + @PKG@.GearABox.readyText() + "; " + @PKG@.GearSpeed.readyText() + "; Reforge level up "''')
rep('''Life Steal at most " + @PKG@.GearCfg.STEAL_MAX + "% of max Health per second; gear:fn:curve; wand''',
    '''Life Steal at most " + @PKG@.GearCfg.STEAL_MAX + "% of max Health per second; gear:fn:curve, gear:fn:speed; wand''')
rep('''Reforge also levels an item up for coins; Life Steal is capped; crits show''',
    '''Reforge also levels an item up for coins; Life Steal is capped; melee weapons roll a speed tier (Slow / Medium / Fast / Super Fast: faster swings hit softer, same damage per second - never tools); crits show''')
# the jar: every speed asset in it, nothing else from the game
rep('''    assert not [n for n in _names if n.startswith("Server/Item/Items/")], "SkyyGear 0.2.2 overrides no item file (the box is hidden at run time)"''',
    '''    assert not [n for n in _names if n.startswith("Server/Item/Items/")], "SkyyGear 0.2.2 overrides no item file (the box is hidden at run time)"
    # 0.2.6: every generated speed asset is in the jar byte for byte; the only vanilla paths it shadows are the 9 family Primary roots
    for _k, _v in SPEED_FILES.items():
        assert _jz.read(_k).decode("utf-8") == _v, "speed asset missing from the jar: " + _k
    _shad = sorted(_n for _n in _names if _n in AZ_NAMES and _n not in ("manifest.json", "Server/Languages/en-US/server.lang"))
    assert _shad == sorted(_f["path"] for _f in SPEED_FAMLIST), "SkyyGear 0.2.6 replaces exactly the 9 melee Primary roots: %s" % _shad''')

# fix round: a weighted tap also weighs the victim's knockback and the attacker's stats on hit (SignatureEnergy) - GearHitSys, same event
rep('''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);''',
    '''        info = @PKG@.GearHit.weaponHit(d, u, pr, main, shot, srec, rec, arm);
        // 0.2.6 weapon speed tiers: the hit's knockback + stats on hit x the same hit weight (nothing when it was x1)
        @PKG@.GearSpeed.perHit(d, buf, att, vic);''')
# ================================================================================================================ write
assert s.count("registerSystem(") == SYS0 and s.count("registerCommand(") == CMD0, "0.2.6 adds no system / command"
out = s.replace(LF, NL)
with open(DST, "w", encoding="utf8", newline="") as f:
    f.write(out)
print("wrote %s (%d lines)" % (os.path.relpath(DST, ROOT), out.count(NL) + 1))


