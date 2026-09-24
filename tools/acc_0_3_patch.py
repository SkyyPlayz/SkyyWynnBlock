"""Derive SkyyAccessories/build_skyyaccessories_0.3.py from 0.2 (same style as acc_0_2_patch.py: rep(old, new) with asserted anchors;
0.2 stays untouched, the line endings of 0.2 are preserved).
0.3: the Speed talisman moves to the SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py - the same MoveSync code SkyySkills 0.2 uses for
     Acrobatics), so talismans and Acrobatics never fight over MovementManager settings:
 - AccEffects no longer writes baseSpeed = default * (1 + talisman) itself. Once per second per player it posts its source
   "accessories.talismans" (layer "pct": speed = the best Speed talisman's bonus, e.g. 0.08; all zeros = entry removed) into the bridge
   map "move:<uuid>", then calls MoveSync.sync, which sets baseSpeed / jumpForce from the defaults and the SUM of every mod's sources:
   default x clamp((1 + sum flat) x (1 + sum pct), 0.3, 5) (Skyy's layer rule: skills/armor flat on the default, accessories % on top).
   Both mods compute the identical target, so whichever applies first wins and the other sees "already right" (no flicker).
 - The 0.2 back-off (5 re-applies in a row -> pause) is kept inside MoveSync, but it only counts writers OUTSIDE the protocol: a changed
   target (any source changed) resets it, and a second protocol applier never looks like an external reset. Unequipping restores the
   default only for a field that still holds the exact value the protocol wrote (0.2 rule), and never while another source remains.
 - AccStore.SPEED now holds the MoveSync applier state {lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed, targetJump, warned}.
 - Review fixes (2026-09-23, all inside tools/skyymove.py, so a rebuild picks them up): the 5-strike pause is logged once PER PLAYER
   (was one static flag: only the first paused player on the server was ever logged), with the number of players paused now; on
   its first sync MoveSync names every enabled plugin from skyymove.KNOWN_WRITERS (non-Skyy mods that write MovementSettings
   baseSpeed/jumpForce directly, incl. EndgameAndQoL's AccessoryPassiveSystem that 0.2's speed code was patterned after, and the
   pre-protocol SkyyAccessories 0.2 itself). Those mods are outside the protocol and win for the player they reset: do not enable
   them in a SkyWynn world.
 - Nothing is written while the player is mounted. Everything else (bag, talismans, bench accessories, stat modifiers, bridge keys
   acc:has / acc:tal / acc:fn:has) is unchanged from 0.2.
 - Deploy together with SkyySkills 0.2 (SkyySkills 0.1 has no movement effects, so 0.3 also works alone or with 0.1).
Run:  python tools/acc_0_3_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.3.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.2.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2"
s = raw.decode("utf8").replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------------------------------------------------------- header / version
rep('"""SkyyAccessories 0.2 - build script (derived from 0.1 by tools/acc_0_2_patch.py - edit the patch, not this file)\n',
'''"""SkyyAccessories 0.3 - build script (derived from 0.2 by tools/acc_0_3_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.3.py            -> SkyyAccessories/SkyyAccessories-0.3.jar
       python build_skyyaccessories_0.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.3: Speed talismans use the SHARED SKYY MOVEMENT PROTOCOL v1 (tools/skyymove.py has the full spec; SkyySkills 0.2 Acrobatics runs the
     identical MoveSync code): bridge "move:<uuid>" -> ConcurrentHashMap source -> Map{layer "flat"|"pct", speed, jump, fallDamage}.
     This mod posts ONLY its own source "accessories.talismans" (layer pct, speed = best Speed talisman, removed at 0) and then applies
     the total of ALL sources: baseSpeed = default x clamp((1 + sum flat speed) x (1 + sum pct speed), 0.3, 5); jump height =
     (h0 + sum flat blocks) x (1 + sum pct), jumpForce = sqrt(2 g h), h0 = default jumpForce^2 / 2g, g = 32. Idempotent: two appliers
     agree, so talismans and Acrobatics never fight. The 5-strike back-off only triggers against writers outside the protocol (a new
     target resets it; logged once per player); defaults are restored only for a field that still holds the value the protocol wrote;
     nothing is written while mounted. fallDamage is applied only by the owner of bridge "stat:owner:fallDamage" (SkyySkills) -
     talismans post no fall stat. Non-Skyy mods that write MovementSettings directly are NOT coordinated (they win for the player
     they reset): keep them out of SkyWynn worlds; the known ones are named in the log on the first sync (skyymove.KNOWN_WRITERS).
0.2 notes:
SkyyAccessories 0.2 - build script (derived from 0.1 by tools/acc_0_2_patch.py - edit the patch, not this file)
''')
rep('VERSION = "0.2"', 'VERSION = "0.3"')
rep('import skyybuild as B\n', 'import skyybuild as B\nimport skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyySkills 0.2)\n')

# ---------------------------------------------------------------- probes + new class
rep('''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)
''', '''             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)
MV.probe(B, pool)   # 0.3: MovementStates.mounting, MovementSettings.jumpForce, PhysicsConstants.GRAVITY_ACCELERATION, ...
''')
rep('eff  = pool.makeClass(PKG + ".AccEffects", pool.get(ETS))\n',
    'eff  = pool.makeClass(PKG + ".AccEffects", pool.get(ETS))\nmvs_ = pool.makeClass(PKG + ".MoveSync")   # 0.3: shared movement protocol\n')
rep('''# SPEED uuid -> float[]{appliedMultiplier, consecutiveReapplies, baseSpeedWeWrote (-1 = none)}''',
    '''# SPEED uuid -> 0.3: MoveSync applier state float[]{lastWrittenSpeed, lastWrittenJump, strikes, targetSpeed, targetJump, warned} (0.2: own speed state)''')

# ---------------------------------------------------------------- MoveSync class (after AccStore.warn exists, before AccEffects uses it)
rep('# ================= AccEffects: talisman stats (EntityTickingSystem on Player entities, runs on each world\'s thread) =================\n',
'''# ================= MoveSync: the shared Skyy movement protocol (tools/skyymove.py; identical code in SkyySkills 0.2) =================
MV.add_move_sync(mvs_, CtField, CtNewMethod, PKG + ".AccStore.warn")

# ================= AccEffects: talisman stats (EntityTickingSystem on Player entities, runs on each world's thread) =================
''')

# ---------------------------------------------------------------- speed: 0.2 own writer -> protocol source + shared applier
a = s.index("# Speed (review fix): ONLY MovementSettings.baseSpeed is scaled.")
b = s.index('eff.addMethod(CtNewMethod.make(f"""\npublic void tick(')
assert 0 < a < b and s.count("# Speed (review fix): ONLY MovementSettings.baseSpeed is scaled.") == 1
old_speed = s[a:b]
assert "public static void speed(java.util.UUID u, {PR} pr, {MMG} mm, float want) {{" in old_speed and old_speed.count("eff.addMethod(") == 2
s = s[:a] + '''# Speed (0.3): the talisman bonus is POSTED as source "accessories.talismans" (layer pct) into the shared movement protocol and
# MoveSync.sync applies the total of every source (Acrobatics from SkyySkills 0.2 = layer flat): baseSpeed = default x
# clamp((1 + sum flat) x (1 + sum pct), 0.3, 5), jumpForce from the summed jump height. Still baseSpeed only for speed (the direction
# multipliers are factors ON baseSpeed - vanilla Default.json BaseSpeed 5.5, ForwardRun 1.0, Walk 0.3, Sprint 1.273 - scaling them too
# compounded to f*f in the first 0.2 build). The 0.2 back-off lives on in MoveSync (5 writes in a row against the same target = an
# outside writer -> pause until the target changes); an unequip restores defaults only for a field still holding the value written.
eff.addMethod(CtNewMethod.make(f"""
public static void speed(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref, float bonus) {{
  {PKG}.MoveSync.post(u, "accessories.talismans", "pct", bonus, 0.0f, 0.0f);
  {PKG}.MoveSync.sync(u, pr, cb, ref, {PKG}.AccStore.SPEED, "SkyyAccessories");
}}""", eff))
''' + s[b:]
rep('''    {MMG} mm = ({MMG}) cb.getComponent(ref, {MMG}.getComponentType());
    if (mm != null) speed(u, pr, mm, 1.0f + {PKG}.AccDefs.SPD[best[{FAM['Speed']}]]);
''', '''    speed(u, pr, cb, ref, {PKG}.AccDefs.SPD[best[{FAM['Speed']}]]);
''')

# ---------------------------------------------------------------- plugin + class list + manifest
rep('''  getEntityStoreRegistry().registerSystem(new {PKG}.AccEffects());
''', '''  getEntityStoreRegistry().registerSystem(new {PKG}.AccEffects());
  {PKG}.MoveSync.checkProto("SkyyAccessories");
''')
rep('for c in (dfs, st_, fn, page, fac, cmd, tick, eff, pl):', 'for c in (dfs, st_, fn, page, fac, cmd, tick, eff, pl, mvs_):')
rep('stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) work while they sit in the bag. Zero dependencies."',
    'stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) work while they sit in the bag; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol. Zero dependencies."')

assert "speed(u, pr, mm," not in s and "st[2] = target;" not in s
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
