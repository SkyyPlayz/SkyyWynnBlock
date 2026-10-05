"""Derive SkyyEssentials/build_skyyessentials_0.1.8.py from the LIVE 0.1.7 (build_skyyessentials_0.1.7.py = the tools/deploy_set.py SET pin).
Run:  python tools/essentials_0_1_8_patch.py   then   python SkyyEssentials/build_skyyessentials_0.1.8.py   (never --deploy: coordinated deploy)
Check: python SkyyEssentials/test_skyyessentials_0.1.8.py   (bare JVM, -Xverify:all; nothing is deployed)
SkyyEssentials uses patch scripts since 0.1.4: edit THIS file, never the generated build script.

0.1.8 = Skyy 2026-10-03 (docs/answered/social.md REQUEST 2026-10-03 evening, Party page screenshot: "here in the party and a tpa button
and a tpa accept to make it quick and easy"). SkyyParty 0.1.7 gets a TPA button on each other member's row and an Accept TPA button; it
reaches /tpa and /tpaccept through three bridge functions published here (java.util.function.Function, plain java.lang / java.util
types only, the settings:fn:get calling style: apply(Object[])):
  ess:fn:tpa         apply(Object[] { UUID requester, UUID target, Boolean here (optional, default false) }) -> String
                     the line the requester gets (also sent to chat, exactly as /tpa <player> or /tpahere <player> would)
  ess:fn:tpaccept    apply(Object[] { UUID accepter, UUID from (or null = the newest) }) -> String
                     the line the accepter gets (also sent to chat, exactly as /tpaccept [player] would)
  ess:fn:tpaPending  apply(UUID player) (or Object[] { UUID }) -> Object[] { String fromUuid, String fromName, Boolean here } of the
                     NEWEST live request TO that player (the one /tpaccept alone would take), or null (none, part.tpa off, offline,
                     no /tpaccept permission). Read only - nothing is removed.
SAME RULES AS THE COMMANDS (no rule is written twice):
  - The command bodies were moved into EssStore.requestR / acceptR (String: they return the line they send the player); EssStore.request /
    accept (what TpaCmd, TpaHereCmd, TpAcceptCmd, TpAcceptNamedCmd call - those classes are untouched) are now one call each to them. So
    part.tpa, self, offline, the target's tpa.requests switch + staff bypass, already pending, the cooldown, expiry, the request book,
    the accept / teleport tasks (ReadDestTask -> MoveTask on the world threads: cross-world, instance return points) are the commands'.
  - Permissions: the command system checks a command's node before it runs; the bridge asks the REGISTERED command objects the same
    question (AbstractCommand.hasPermission(sender) - the engine's own check, its node + Adventurer virtual group; a usage variant
    uses its parent's): TpaCmd for tpa, TpaHereCmd for here, TpAcceptCmd for tpaccept. EssStore.cmdFor finds them through
    CommandManager.getCommandRegistration() at the first call (only OUR classes count) and keeps them in TPA_CMD / TPH_CMD / TAC_CMD
    (setup() still registers them as `new X()` - the form tools/ci/crosscheck.py audits). Denied (or no command / no permissions module) = "[TPA] You
    don't have permission to use /tpa." (fail closed). A target that is not online = "[TPA] That player is not online." (the command's
    argument parser refuses it before the command runs; the bridge gets a UUID, not a typed name).
  - There are no combat or world rules on /tpa in SkyyEssentials (it is cross-world on purpose); none were invented here.
  - Threads: requestR / acceptR touch no component (the request book is synchronized on EssStore.class; the teleport itself always hops
    to the right world threads through ReadDestTask / MoveTask), so the functions may be called from any thread - SkyyParty calls them
    from its page's click handler (the clicking player's world thread, the same thread a typed /tpa runs on).
  setup(): the functions are published right after the commands are registered (own try: a failure costs only the Party page buttons);
  shutdown(): removed again (only when the map still holds OUR objects). The ready line names them.
Version 0.1.8. Nothing else changes: commands (same classes, nodes, texts), the other bridge keys, rows, files, /trade, /msg, /r, /fly,
warps, the durability switch, the no-trade list.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.7.py")
dst = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.8.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


# ================================================================================================ docstring + version
DOC = '''SkyyEssentials 0.1.8 - build script (javassist via jpype). GENERATED by tools/essentials_0_1_8_patch.py from the LIVE 0.1.7
(build_skyyessentials_0.1.7.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyessentials_0.1.8.py            -> SkyyEssentials/SkyyEssentials-0.1.8.jar   (never --deploy: tools/deploy_set.py)
Check: python test_skyyessentials_0.1.8.py            (bare JVM, -Xverify:all: the 0.1.7 checks + the tpa bridge against the command paths)

0.1.8 (2026-10-05, Skyy 2026-10-03 "here in the party and a tpa button and a tpa accept to make it quick and easy"; docs/answered/social.md):
  THE TPA BRIDGE for SkyyParty 0.1.7's TPA / Accept TPA buttons (plain java types, apply(Object[]) like settings:fn:get):
    ess:fn:tpa         Object[] { UUID requester, UUID target, Boolean here? }  -> String (the requester's line; chat gets it too)
    ess:fn:tpaccept    Object[] { UUID accepter, UUID from or null }           -> String (the accepter's line; chat gets it too)
    ess:fn:tpaPending  UUID (or Object[] { UUID })  -> Object[] { String fromUuid, String fromName, Boolean here } or null (read only)
  Same code path as the commands: /tpa /tpahere /tpaccept bodies moved into EssStore.requestR / acceptR (they return the line they say);
  request / accept (the commands' calls) are one call each to them. Permissions = the registered command objects' own
  AbstractCommand.hasPermission (TpaCmd / TpaHereCmd / TpAcceptCmd found through the CommandManager, fail closed). Published in setup() after the commands, removed in
  shutdown(). No combat / world rules exist on /tpa (cross-world on purpose). Everything else is 0.1.7's.

'''
first = s.index('"""') + 3
s = s[:first] + DOC + s[first:]
rep('\nVERSION = "0.1.7"\n', '\nVERSION = "0.1.8"\n')

# ================================================================================================ requestR / acceptR (the command bodies)
OLD_REQ = '''es.addMethod(CtNewMethod.make(f"""
public static void request({PR} pr, Object t, boolean here) {{
  String cmd = here ? "/tpahere" : "/tpa";
  if (!PART_TPA) {{ say(pr, "[TPA] Teleport requests are turned off on this server.", ERR); return; }}
  if (!(t instanceof {PR})) {{ say(pr, "[TPA] Usage: " + cmd + " <player>", ERR); return; }}
  {PR} target = ({PR}) t;
  if (target.getUuid().equals(pr.getUuid())) {{ say(pr, "[TPA] You can't send a teleport request to yourself.", ERR); return; }}
  if (online(target.getUuid()) == null) {{ say(pr, "[TPA] " + target.getUsername() + " is not online.", ERR); return; }}
  String me = pr.getUsername();
  String them = target.getUsername();
  // 0.1.5: the target's tpa.requests switch refuses the request (nothing stored, no cooldown used); staff pass while the bypass is on
  int g = gate(target.getUuid(), "tpa.requests", pr.getUuid());
  if (g == 1) {{ say(pr, "[TPA] " + them + " is not taking teleport requests.", ERR); return; }}
  String err = tryAdd(pr.getUuid(), target.getUuid(), here, me, them);
  if (err != null) {{ say(pr, "[TPA] " + err, ERR); return; }}
  String ex = secs(EXPIRE_MS);
  String who = me + (g == 2 ? " (staff)" : "");
  if (here) {{
    say(pr, "[TPA] Asked " + them + " to teleport to you. They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + who + " wants you to teleport to them. /tpaccept " + me + " to go, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }} else {{
    say(pr, "[TPA] Request sent to " + them + ". They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + who + " wants to teleport to you. /tpaccept " + me + " to allow, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }}
  if (g == 2) say(pr, "[TPA] (sent anyway - staff bypass: " + them + " has teleport requests off)", INFO);
}}""", es))
'''
NEW_REQ = '''# 0.1.8: the /tpa + /tpahere body returns the line it sends the requester (sayR = say + return the text), so SkyyParty's TPA button
# (bridge ess:fn:tpa -> EssStore.fnTpa) runs EXACTLY this code; request() - what TpaCmd / TpaHereCmd call - is one call to it
es.addMethod(CtNewMethod.make(f"""
public static String sayR({PR} p, String text, String color) {{
  say(p, text, color);
  return text;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static String requestR({PR} pr, Object t, boolean here) {{
  String cmd = here ? "/tpahere" : "/tpa";
  if (!PART_TPA) return sayR(pr, "[TPA] Teleport requests are turned off on this server.", ERR);
  if (!(t instanceof {PR})) return sayR(pr, "[TPA] Usage: " + cmd + " <player>", ERR);
  {PR} target = ({PR}) t;
  if (target.getUuid().equals(pr.getUuid())) return sayR(pr, "[TPA] You can't send a teleport request to yourself.", ERR);
  if (online(target.getUuid()) == null) return sayR(pr, "[TPA] " + target.getUsername() + " is not online.", ERR);
  String me = pr.getUsername();
  String them = target.getUsername();
  // 0.1.5: the target's tpa.requests switch refuses the request (nothing stored, no cooldown used); staff pass while the bypass is on
  int g = gate(target.getUuid(), "tpa.requests", pr.getUuid());
  if (g == 1) return sayR(pr, "[TPA] " + them + " is not taking teleport requests.", ERR);
  String err = tryAdd(pr.getUuid(), target.getUuid(), here, me, them);
  if (err != null) return sayR(pr, "[TPA] " + err, ERR);
  String ex = secs(EXPIRE_MS);
  String who = me + (g == 2 ? " (staff)" : "");
  String res;
  if (here) {{
    res = sayR(pr, "[TPA] Asked " + them + " to teleport to you. They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + who + " wants you to teleport to them. /tpaccept " + me + " to go, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }} else {{
    res = sayR(pr, "[TPA] Request sent to " + them + ". They have " + ex + " to accept. /tpacancel to cancel.", INFO);
    say(target, "[TPA] " + who + " wants to teleport to you. /tpaccept " + me + " to allow, /tpdeny " + me + " to refuse (" + ex + ").", INFO);
  }}
  if (g == 2) say(pr, "[TPA] (sent anyway - staff bypass: " + them + " has teleport requests off)", INFO);
  return res;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void request({PR} pr, Object t, boolean here) {{
  requestR(pr, t, here);
}}""", es))
'''
rep(OLD_REQ, NEW_REQ)

OLD_ACC = '''es.addMethod(CtNewMethod.make(f"""
public static void accept({PR} pr, java.util.UUID from) {{
  if (!PART_TPA) {{ say(pr, "[TPA] Teleport requests are turned off on this server.", ERR); return; }}
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null) {{
    say(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
    return;
  }}
  {PR} req = online(r.from);
  if (req == null) {{ say(pr, "[TPA] " + r.fromName + " is no longer online.", ERR); return; }}
  java.util.UUID moverU = r.here ? r.to : r.from;
  java.util.UUID destU = r.here ? r.from : r.to;
  String moverName = r.here ? pr.getUsername() : req.getUsername();
  String destName = r.here ? req.getUsername() : pr.getUsername();
  if (r.here) {{
    say(pr, "[TPA] Accepted. Teleporting you to " + destName + "...", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted and is teleporting to you.", OK);
  }} else {{
    say(pr, "[TPA] Accepted. " + moverName + " is teleporting to you.", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted your request. Teleporting...", OK);
  }}
  int left = pendingFor(pr.getUuid());
  if (left > 0) say(pr, "[TPA] You still have " + left + " pending request(s). /tpaccept <player> or /tpdeny <player>.", INFO);
  new {PKG}.ReadDestTask(moverU, destU, moverName, destName).hop();
}}""", es))
'''
NEW_ACC = '''# 0.1.8: the /tpaccept body returns the accepter's line (SkyyParty's Accept TPA button: bridge ess:fn:tpaccept -> EssStore.fnAccept);
# accept() - what TpAcceptCmd / TpAcceptNamedCmd call - is one call to it
es.addMethod(CtNewMethod.make(f"""
public static String acceptR({PR} pr, java.util.UUID from) {{
  if (!PART_TPA) return sayR(pr, "[TPA] Teleport requests are turned off on this server.", ERR);
  {PKG}.TpReq r = take(pr.getUuid(), from);
  if (r == null)
    return sayR(pr, from == null ? "[TPA] You have no pending teleport requests." : "[TPA] No pending teleport request from that player.", ERR);
  {PR} req = online(r.from);
  if (req == null) return sayR(pr, "[TPA] " + r.fromName + " is no longer online.", ERR);
  java.util.UUID moverU = r.here ? r.to : r.from;
  java.util.UUID destU = r.here ? r.from : r.to;
  String moverName = r.here ? pr.getUsername() : req.getUsername();
  String destName = r.here ? req.getUsername() : pr.getUsername();
  String res;
  if (r.here) {{
    res = sayR(pr, "[TPA] Accepted. Teleporting you to " + destName + "...", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted and is teleporting to you.", OK);
  }} else {{
    res = sayR(pr, "[TPA] Accepted. " + moverName + " is teleporting to you.", OK);
    say(req, "[TPA] " + pr.getUsername() + " accepted your request. Teleporting...", OK);
  }}
  int left = pendingFor(pr.getUuid());
  if (left > 0) say(pr, "[TPA] You still have " + left + " pending request(s). /tpaccept <player> or /tpdeny <player>.", INFO);
  new {PKG}.ReadDestTask(moverU, destU, moverName, destName).hop();
  return res;
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void accept({PR} pr, java.util.UUID from) {{
  acceptR(pr, from);
}}""", es))
'''
rep(OLD_ACC, NEW_ACC)

# ================================================================================================ the bridge functions (after deny, before pm)
BRIDGE = '''# ================= 0.1.8: the tpa bridge (SkyyParty 0.1.7's TPA / Accept TPA buttons) =================
# The registered command objects (found through the CommandManager at the first call, cmdFor): the bridge asks THEM the permission
# question the command system asks before a command runs
es.addField(CtField.make(f"public static volatile {AC} TPA_CMD;", es))
es.addField(CtField.make(f"public static volatile {AC} TPH_CMD;", es))
es.addField(CtField.make(f"public static volatile {AC} TAC_CMD;", es))
# AbstractCommand.hasPermission(CommandSender) = the engine's own check (its node via the Adventurer virtual group; a usage variant falls
# back to its parent's node). No command / no permissions module / an error = false (fail closed).
es.addMethod(CtNewMethod.make(f"""
public static boolean cmdOk({AC} c, {PR} pr) {{
  if (c == null || pr == null) return false;
  try {{ return c.hasPermission(pr); }} catch (Throwable t) {{ return false; }}
}}""", es))
# the registered command object (k 1 = /tpa, 2 = /tpahere, 3 = /tpaccept): the field when set, else the object the CommandManager holds
# under that name - only when it is OURS (another mod's /tpa is not this command) - remembered in the field. null = fail closed.
es.addMethod(CtNewMethod.make(f"""
public static {AC} cmdFor(int k) {{
  {AC} c = k == 1 ? TPA_CMD : (k == 2 ? TPH_CMD : TAC_CMD);
  if (c != null) return c;
  try {{
    Object o = {CMG}.get().getCommandRegistration().get(k == 1 ? "tpa" : (k == 2 ? "tpahere" : "tpaccept"));
    if (k == 1 && o instanceof {PKG}.TpaCmd) {{ c = ({AC}) o; TPA_CMD = c; }}
    else if (k == 2 && o instanceof {PKG}.TpaHereCmd) {{ c = ({AC}) o; TPH_CMD = c; }}
    else if (k == 3 && o instanceof {PKG}.TpAcceptCmd) {{ c = ({AC}) o; TAC_CMD = c; }}
  }} catch (Throwable t) {{ c = null; }}
  return c;
}}""", es))
# the newest live request TO `to` - the one take(to, null) (= /tpaccept alone) would take; nothing is removed
es.addMethod(CtNewMethod.make(f"""
public static synchronized {PKG}.TpReq peek(java.util.UUID to) {{
  long now = System.currentTimeMillis();
  {PKG}.TpReq best = null;
  java.util.Iterator it = REQ.values().iterator();
  while (it.hasNext()) {{
    {PKG}.TpReq r = ({PKG}.TpReq) it.next();
    if (r == null || !r.to.equals(to) || r.expires <= now) continue;
    if (best == null || r.created > best.created) best = r;
  }}
  return best;
}}""", es))
# ess:fn:tpa: Object[] { UUID requester, UUID target, Boolean here? } -> the requester's line. Order = the command system's: permission,
# then the target (the argument parser), then the /tpa body (requestR)
es.addMethod(CtNewMethod.make(f"""
public static String fnTpa(Object o) {{
  try {{
    if (!(o instanceof Object[])) return "[TPA] Something went wrong with that request.";
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof java.util.UUID)) return "[TPA] Something went wrong with that request.";
    boolean here = a.length > 2 && Boolean.TRUE.equals(a[2]);
    {PR} pr = online((java.util.UUID) a[0]);
    if (pr == null) return "[TPA] You are not online.";
    if (!cmdOk(cmdFor(here ? 2 : 1), pr)) return sayR(pr, "[TPA] You don't have permission to use " + (here ? "/tpahere" : "/tpa") + ".", ERR);
    {PR} t = online((java.util.UUID) a[1]);
    if (t == null) return sayR(pr, "[TPA] That player is not online.", ERR);
    return requestR(pr, t, here);
  }} catch (Throwable e) {{
    warn("ess:fn:tpa failed: " + e);
    return "[TPA] Something went wrong with that request.";
  }}
}}""", es))
# ess:fn:tpaccept: Object[] { UUID accepter, UUID from or null } -> the accepter's line (the /tpaccept [player] body: acceptR)
es.addMethod(CtNewMethod.make(f"""
public static String fnAccept(Object o) {{
  try {{
    if (!(o instanceof Object[])) return "[TPA] Something went wrong with that request.";
    Object[] a = (Object[]) o;
    if (a.length < 1 || !(a[0] instanceof java.util.UUID)) return "[TPA] Something went wrong with that request.";
    java.util.UUID from = (a.length > 1 && a[1] instanceof java.util.UUID) ? (java.util.UUID) a[1] : null;
    {PR} pr = online((java.util.UUID) a[0]);
    if (pr == null) return "[TPA] You are not online.";
    if (!cmdOk(cmdFor(3), pr)) return sayR(pr, "[TPA] You don't have permission to use /tpaccept.", ERR);
    return acceptR(pr, from);
  }} catch (Throwable e) {{
    warn("ess:fn:tpaccept failed: " + e);
    return "[TPA] Something went wrong with that request.";
  }}
}}""", es))
# ess:fn:tpaPending: UUID (or Object[] { UUID }) -> Object[] { String fromUuid, String fromName, Boolean here } or null. Read only; null
# while part.tpa is off, for an offline player or one /tpaccept would refuse (so the page shows no button it cannot answer)
es.addMethod(CtNewMethod.make(f"""
public static Object fnPending(Object o) {{
  try {{
    Object u = o;
    if (o instanceof Object[]) u = ((Object[]) o).length > 0 ? ((Object[]) o)[0] : null;
    if (!(u instanceof java.util.UUID) || !PART_TPA) return null;
    {PR} pr = online((java.util.UUID) u);
    if (pr == null || !cmdOk(cmdFor(3), pr)) return null;
    {PKG}.TpReq r = peek((java.util.UUID) u);
    if (r == null) return null;
    return new Object[] {{ r.from.toString(), r.fromName, Boolean.valueOf(r.here) }};
  }} catch (Throwable e) {{
    warn("ess:fn:tpaPending failed: " + e);
    return null;
  }}
}}""", es))
efn = pool.makeClass(PKG + ".EssFn")
efn.addInterface(pool.get("java.util.function.Function"))
efn.addField(CtField.make("public final int kind;", efn))
efn.addConstructor(CtNewConstructor.make("public EssFn(int kind) { this.kind = kind; }", efn))
efn.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  if (this.kind == 1) return {ES}.fnTpa(o);
  if (this.kind == 2) return {ES}.fnAccept(o);
  if (this.kind == 3) return {ES}.fnPending(o);
  return null;
}}""", efn))
es.addField(CtField.make('public static final String[] FN_KEYS = new String[] { "ess:fn:tpa", "ess:fn:tpaccept", "ess:fn:tpaPending" };', es))
es.addMethod(CtNewMethod.make(f"""
public static void publishFns() {{
  java.util.Map br = bridge();
  for (int i = 0; i < FN_KEYS.length; i++) br.put(FN_KEYS[i], new {PKG}.EssFn(i + 1));
}}""", es))
es.addMethod(CtNewMethod.make(f"""
public static void unpublishFns() {{
  try {{
    java.util.Map br = bridge();
    for (int i = 0; i < FN_KEYS.length; i++) {{
      Object v = br.get(FN_KEYS[i]);
      if (v instanceof {PKG}.EssFn) br.remove(FN_KEYS[i], v);
    }}
  }} catch (Throwable t) {{ }}
}}""", es))

'''
PM_ANCHOR = '''es.addMethod(CtNewMethod.make(f"""
public static void pm({PR} pr, {PR} target, String text) {{'''
rep(PM_ANCHOR, BRIDGE + PM_ANCHOR)

# ================================================================================================ setup / shutdown / class list
rep('''  getCommandRegistry().registerCommand(new @PKG@.FlyCmd());
''', '''  getCommandRegistry().registerCommand(new @PKG@.FlyCmd());
  // 0.1.8: the tpa bridge for SkyyParty's TPA / Accept TPA buttons (own try: a problem costs only those buttons)
  String fNote = "bridge ess:fn:tpa ess:fn:tpaccept ess:fn:tpaPending";
  try { @ES@.publishFns(); } catch (Throwable tf) { fNote = "tpa bridge off (error)"; @ES@.warn("could not publish the tpa bridge (SkyyParty's TPA buttons): " + tf); }
''')
rep('''/reply /fly; switches tpa.requests msg.private (staff bypass " + (@ES@.STAFF_BYPASS ? "on" : "off") + "); " + rNote''',
    '''/reply /fly; switches tpa.requests msg.private (staff bypass " + (@ES@.STAFF_BYPASS ? "on" : "off") + "); " + fNote + "; " + rNote''')
rep('''  @ES@.releaseR();
  // 0.1.6: the original durability costs go back''', '''  @ES@.releaseR();
  // 0.1.8: the tpa bridge goes (only our own objects)
  @ES@.unpublishFns();
  // 0.1.6: the original durability costs go back''')
rep('''MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS''', '''MINE = [rq, es, hop, mv, rd, fly, tick, efn] + OLD_CMDS''')

# ================================================================================================ checks on the generated text
code = s
assert code.count("registerCommand(") == REG0 and code.count("registerSystem(") == SYS0
assert "public static void request(" in code and "public static void accept(" in code
_rq = code[code.index("public static void request({PR} pr, Object t, boolean here) {{"):]
_rq = _rq[:_rq.index('}}""", es))')]
assert _rq.count(";") == 1 and "requestR(pr, t, here);" in _rq
_ac = code[code.index("public static void accept({PR} pr, java.util.UUID from) {{"):]
_ac = _ac[:_ac.index('}}""", es))')]
assert _ac.count(";") == 1 and "acceptR(pr, from);" in _ac
# every early exit of the bodies returns the line it said (no bare return; left)
for sig in ("public static String requestR(", "public static String acceptR("):
    b_ = code[code.index(sig):]
    b_ = b_[:b_.index('}}""", es))')]
    assert "return;" not in b_ and b_.count("say(pr,") == (1 if "requestR" in sig else 1), sig
# the bridge goes through the bodies; the permission comes first, from the registered command objects
_ft = code[code.index("public static String fnTpa(Object o) {{"):]
_ft = _ft[:_ft.index('}}""", es))')]
assert _ft.index("cmdOk(cmdFor(here ? 2 : 1), pr)") < _ft.index("online((java.util.UUID) a[1])") < _ft.index("return requestR(pr, t, here);")
_fa = code[code.index("public static String fnAccept(Object o) {{"):]
_fa = _fa[:_fa.index('}}""", es))')]
assert _fa.index("cmdOk(cmdFor(3), pr)") < _fa.index("return acceptR(pr, from);")
for _bad in ("tryAdd(", "take(", "REQ.", "LAST_SENT", "COOLDOWN_MS", "gate("):
    assert _bad not in _ft and _bad not in _fa, "the bridge must not repeat a /tpa rule: " + _bad
assert code.index("public static String requestR(") < code.index("public static String fnTpa(") < code.index('efn = pool.makeClass(PKG + ".EssFn")') \
    < code.index("public static void publishFns() {{")
_su = code[code.index("getCommandRegistry().registerCommand(new @PKG@.TpaCmd());"):]
assert _su.index("registerCommand(new @PKG@.TpAcceptCmd());") < _su.index("@ES@.publishFns();")
assert "B.deploy(" not in code and "enable_in_world(" not in code
for _t in ("[TPA] You don't have permission to use ", "[TPA] That player is not online.", "[TPA] You are not online."):
    assert all(32 <= ord(_c) < 127 for _c in _t) and _t in code

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == CR + LF else "LF"))
