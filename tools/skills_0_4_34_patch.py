"""Derive SkyySkills/build_skyyskills_0.4.34.py from the LIVE generated SkyySkills/build_skyyskills_0.4.33.py (= the tools/deploy_set.py SET
pin; 0.4.33 came from 0.4.32 by tools/skills_0_4_33_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; 0.4.33 stays untouched, its line endings are kept.
Run:  python tools/skills_0_4_34_patch.py   then   python SkyySkills/build_skyyskills_0.4.34.py   (NO --deploy: coordinated deploy)
Test: python SkyySkills/test_skyyskills_0.4.34.py --dir tools/dev/scratch/<yours>/sk   (bare JVM, -Xverify:all)

0.4.34 (2026-10-13) = CHAT OVERFLOW -> FEED, the sender side (Skyy 2026-10-12, docs/answered/ui.md CHAT OVERFLOW: "watch for things i
probably wont notice, and figure out ways to reduce the chat overflow while still giving players the info they need. the chat has top move
slow enough people can read it for server use. (unless we set up a second notification system that uses our widgets or something.)").
SkyyHud 0.3.20+ already has the notification feed, the Skill XP flash and the per-player Chat / Feed / Off switches; this build moves
SkyySkills' per-gain chat lines there through the shared tools/skyyroute.py MsgRoute (route cached 2 s per player + kind):
  - SKILL XP ("+79 Divinity XP (4601/4650)", the 2026-10-11 log's 75 of 116 lines): route "skillxp". feed = each skill's batch goes to
    xpflash:fn:push (the Skills widget flashes "+79" next to that skill); a skill the HUD cannot draw (FALSE) stays in the chat line, so
    nothing vanishes. off = no line. chat (or no SkyyHud / an old SkyyHud) = the old line, word for word. SkillMsg.take is split into
    takeArr (the same pending / staged merge, LAST stamp) + line (the same text); routed() decides; send() sends what is left.
  - PARTY XP ("[Party] +6 Archery XP (340/500) from Skyy's kill"): the same "skillxp" route (flash per skill, leftovers keep the old
    "[Party] ..." line).
  - DOUBLE DROP ("Double drop! +2 Wood Oak Trunk  (Foraging perk)") and EXTRA POTION: route "drop". feed = ONE card per proc
    (kind drop, the icon of the item with the most extra, "Double drop: Wood Oak Trunk, +1 more" / "Extra potion: Potion Health", count
    = that extra quantity - SkyyHud merges repeats: "x9"). REVIEW FIX: MsgRoute.gate lets a NEW item's card through at most once a
    second per player (SkyyHud sends a card pushed out of its 4-card stack before it was drawn as a chat line); a skipped proc is
    folded away like 0.4.33's 2 s chat throttle. A refused card = the chat line (never both). off = no line.
  - TREE FELLED summary ("Tree felled: 207 logs, 36 leaves (+5140 Foraging XP)"): route "pickup". feed = one card "Tree felled: 207 logs,
    36 leaves" (the XP is on the skill flash already - the 2026-10-11 log showed it twice).
  - Chat KEEPS: SKILL LEVEL UP / OVERALL LEVEL UP + their "next:" lines, perk unlock lines, hints, commands, errors (one line each).
  The existing per-player switches (skills.xpGain, skills.doubleDrop, skills.extraPotion, /skills quiet, feedback=false) still hide a
  message completely, before any route is asked. No config key, no saved data, no migration, no command. Rolling back to 0.4.33 is safe
  (the lines go back to chat).
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.33.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.34.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.33"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.4.33"' in s and "derived from the generated 0.4.32 by tools/skills_0_4_33_patch.py" in s, "not the live generated 0.4.33"
assert s.count('DJ_L.append("acro.doubleJump.trigger=jump")') == 1, "not the edited lineage (Skyy's Double Jump trigger edit missing)"
assert "MANA_INTERVAL = 0.3 " in s, "not 0.4.33 (the Mana 3.3 interval is missing)"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.34 (2026-10-13)"):].rstrip() + "\n"

# ---------------------------------------------------------------- docstring + version
rep('''"""SkyySkills 0.4.33 - build script (derived from the generated 0.4.32 by tools/skills_0_4_33_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.34 - build script (derived from the generated 0.4.33 by tools/skills_0_4_34_patch.py - edit the patch, not this file;
0.4.33 was derived from the generated 0.4.32 by tools/skills_0_4_33_patch.py;
''')
rep('''0.4.33 (2026-10-13) = MANA REGEN 3.3 A SECOND''', NOTE.replace("\n", "\n  ").rstrip() + '''
  CHECKED: SkyySkills/test_skyyskills_0.4.34.py.
0.4.33 (2026-10-13) = MANA REGEN 3.3 A SECOND''')
rep('VERSION = "0.4.33"', 'VERSION = "0.4.34"')
rep('''import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyyAccessories 0.3)
''', '''import skyymove as MV   # shared Skyy movement protocol (MoveSync class source; also used by SkyyAccessories 0.3)
import skyyroute as RT  # 0.4.34: the shared message route (MsgRoute class source; also SkyyClasses 0.1.20, SkyyCollections 0.2.12)
''')

# ---------------------------------------------------------------- MsgRoute (compiled before SkillMsg: its callers come after)
rep('''# ================= SkillMsg: throttled "+12 Mining XP (340/500)" =================
''', '''# ================= 0.4.34 MsgRoute: chat / feed / off per message kind (tools/skyyroute.py; SkyyHud 0.3.20+ bridge API) =================
mrt = pool.makeClass(PKG + ".MsgRoute")
RT.add_msg_route(mrt, CtField, CtNewMethod, PKG + ".SkillStore.bridge()")

# ================= SkillMsg: throttled "+12 Mining XP (340/500)" =================
''')

# ---------------------------------------------------------------- SkillMsg: take -> takeArr + line, routed(), send()
rep('''msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  long[] sg = (long[]) STAGE.remove(u);   // 0.4.31: the staged Acrobatics counter is shown with this line
  if (sg != null && sg[0] >= 0L && sg[0] < (long) {PKG}.SkillDefs.N && sg[1] > 0L) {{
    if (p == null) {{ p = new long[{PKG}.SkillDefs.N]; PEND.put(u, p); }}
    p[(int) sg[0]] += sg[1];
  }}
  if (p == null) return null;
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");
  }}
  PEND.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  return sb.length() == 0 ? null : sb.toString();
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#9fd8ff"));
  }} catch (Throwable t) {{ }}
}}""", msg))''', '''# 0.4.34: take() = takeArr (the pending XP + the staged counter, taken out, LAST stamped - 0.4.33's steps) + line (0.4.33's text)
msg.addMethod(CtNewMethod.make(f"""
public static synchronized long[] takeArr(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  long[] sg = (long[]) STAGE.remove(u);   // 0.4.31: the staged Acrobatics counter is shown with this line
  if (sg != null && sg[0] >= 0L && sg[0] < (long) {PKG}.SkillDefs.N && sg[1] > 0L) {{
    if (p == null) {{ p = new long[{PKG}.SkillDefs.N]; PEND.put(u, p); }}
    p[(int) sg[0]] += sg[1];
  }}
  if (p == null) return null;
  PEND.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  return p;
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static String line(java.util.UUID u, long[] p) {{
  if (p == null) return null;
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.LABELS[i]).append(" XP (").append({PKG}.SkillDefs.progress(i, d[i])).append(")");
  }}
  return sb.length() == 0 ? null : sb.toString();
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  return line(u, takeArr(u));
}}""", msg))
# 0.4.34 route "skillxp": chat = 0.4.33's line; off = nothing; feed = xpflash:fn:push per skill (the Skills widget "+79"), a skill the HUD
# does not draw stays in the chat line (returned). Never throws.
msg.addMethod(CtNewMethod.make(f"""
public static String routed(java.util.UUID u) {{
  String r = {PKG}.MsgRoute.route(u, "skillxp");
  if (!"feed".equals(r) && !"off".equals(r)) return take(u);
  long[] p = takeArr(u);
  if (p == null) return null;
  if ("off".equals(r)) {{ {PKG}.MsgRoute.off(); return null; }}
  long[] rest = null;
  for (int i = 0; i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if ({PKG}.MsgRoute.flash(u, {PKG}.SkillClass.skillName(u, i), p[i])) continue;
    if (rest == null) rest = new long[p.length];
    rest[i] = p[i];
  }}
  return rest == null ? null : line(u, rest);
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = routed(pr.getUuid());
    if (s != null) {{ {PKG}.MsgRoute.said(s); pr.sendMessage({MSG}.raw(s).color("#9fd8ff")); }}
  }} catch (Throwable t) {{ }}
}}""", msg))''')

# ---------------------------------------------------------------- PartyXp: take -> takeRaw + text, routed(), send()
rep('''pxp.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  Object wo = WHO.get(u);
  String who = wo instanceof String ? (String) wo : "";
  PEND.remove(u);
  WHO.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  long[] d = {PKG}.SkillStore.data(u);''', '''pxp.addMethod(CtNewMethod.make(f"""
public static synchronized Object[] takeRaw(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  Object wo = WHO.get(u);
  String who = wo instanceof String ? (String) wo : "";
  PEND.remove(u);
  WHO.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  return new Object[] {{ p, who }};
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static String text(java.util.UUID u, long[] p, String who) {{
  if (p == null || who == null) return null;
  long[] d = {PKG}.SkillStore.data(u);''')
rep('''  if (who.length() > 0) src = n > 1L ? n + " kills by " + who : who + "'s kill";
  else src = n + " party kills";
  return "[Party] " + sb.toString() + " from " + src;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#a8e8c0"));
  }} catch (Throwable t) {{ }}
}}""", pxp))''', '''  if (who.length() > 0) src = n > 1L ? n + " kills by " + who : who + "'s kill";
  else src = n + " party kills";
  return "[Party] " + sb.toString() + " from " + src;
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  Object[] e = takeRaw(u);
  return e == null ? null : text(u, (long[]) e[0], (String) e[1]);
}}""", pxp))
# 0.4.34 route "skillxp" (the party share is skill XP too): feed = one flash per skill; leftovers keep the "[Party] ..." line
pxp.addMethod(CtNewMethod.make(f"""
public static String routed(java.util.UUID u) {{
  String r = {PKG}.MsgRoute.route(u, "skillxp");
  if (!"feed".equals(r) && !"off".equals(r)) return take(u);
  Object[] e = takeRaw(u);
  if (e == null) return null;
  if ("off".equals(r)) {{ {PKG}.MsgRoute.off(); return null; }}
  long[] p = (long[]) e[0];
  long[] rest = null;
  for (int i = 0; i < {PKG}.SkillDefs.N && i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if ({PKG}.MsgRoute.flash(u, {PKG}.SkillClass.skillName(u, i), p[i])) continue;
    if (rest == null) {{ rest = new long[p.length]; rest[p.length - 1] = p[p.length - 1]; }}
    rest[i] = p[i];
  }}
  return rest == null ? null : text(u, rest, (String) e[1]);
}}""", pxp))
pxp.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = routed(pr.getUuid());
    if (s != null) {{ {PKG}.MsgRoute.said(s); pr.sendMessage({MSG}.raw(s).color("#a8e8c0")); }}
  }} catch (Throwable t) {{ }}
}}""", pxp))''')

# ---------------------------------------------------------------- Perks.doubled: route "drop"
rep('''# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
perk.addMethod(CtNewMethod.make(f"""
public static void doubled({PR} pr, java.util.List drops, int row, String world) {{
  String what = give(pr, drops, world);
  if (what != null) collDouble(pr, drops);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;
  long now''', '''# 0.4.34 route "drop" feed. REVIEW FIX (2026-10-13): ONE card per proc (SkyyHud sends a card pushed out of its 4-card stack before it
# was drawn as a CHAT line, and one card per item could push several at once; also no more "cards + the chat line" when only some cards
# were taken): kind drop, the icon + count of the item with the most extra (SkyyHud merges repeats: "x9"), text "Double drop: Wood Oak
# Trunk" (+ ", +N more" for the other items). MsgRoute.gate: a NEW item's card at most once a second per player (the same item always) -
# a skipped proc is folded away like 0.4.33's 2 s chat throttle did (handled, no line). true = handled; false = send the chat line.
perk.addMethod(CtNewMethod.make(f"""
public static boolean ddFeed(java.util.UUID u, String[] ids, long[] qs, String what) {{
  if (u == null || ids == null || qs == null) return false;
  int n = 0;
  int best = -1;
  for (int i = 0; i < ids.length && i < qs.length; i++) {{
    if (ids[i] == null || qs[i] <= 0L) continue;
    n++;
    if (best < 0 || qs[i] > qs[best]) best = i;
  }}
  if (best < 0) return false;
  if (!{PKG}.MsgRoute.gate(u, "drop", ids[best], 1000L, 0L)) return true;
  return {PKG}.MsgRoute.feed(u, "drop", ids[best], what + {PKG}.MsgRoute.pretty(ids[best]) + (n > 1 ? ", +" + (n - 1) + " more" : ""), qs[best]);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static boolean ddFeedList(java.util.UUID u, java.util.List drops, String what) {{
  if (drops == null) return false;
  String[] ids = new String[drops.size()];
  long[] qs = new long[drops.size()];
  for (int i = 0; i < drops.size(); i++) {{
    Object o = drops.get(i);
    if (!(o instanceof {IS})) continue;
    {IS} is = ({IS}) o;
    if (is.isEmpty() || is.getItemId() == null || is.getQuantity() <= 0) continue;
    ids[i] = is.getItemId();
    qs[i] = (long) is.getQuantity();
  }}
  return ddFeed(u, ids, qs, what);
}}""", perk))
# route "drop" of one double drop: true = handled (off, or every card taken); false = send the chat line
perk.addMethod(CtNewMethod.make(f"""
public static boolean ddRoute(java.util.UUID u, java.util.List drops) {{
  String rt = {PKG}.MsgRoute.route(u, "drop");
  if ("off".equals(rt)) {{ {PKG}.MsgRoute.off(); return true; }}
  return "feed".equals(rt) && ddFeedList(u, drops, "Double drop: ");
}}""", perk))
# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
# 0.4.34: route "drop" first - off = nothing, feed = ddFeedList (every proc, no throttle; a refused card = the chat line below)
perk.addMethod(CtNewMethod.make(f"""
public static void doubled({PR} pr, java.util.List drops, int row, String world) {{
  String what = give(pr, drops, world);
  if (what != null) collDouble(pr, drops);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if (!{PKG}.SkillStore.notifyOn(u, "skills.doubleDrop")) return;
  if (ddRoute(u, drops)) return;
  long now''')
rep('''  pr.sendMessage({MSG}.raw("Double drop" + (c[0] > 1L ? " x" + c[0] : "") + "!" + what + "  (" + {PKG}.SkillDefs.LABELS[row] + " perk)").color("#b8f0a0"));''',
    '''  String dl = "Double drop" + (c[0] > 1L ? " x" + c[0] : "") + "!" + what + "  (" + {PKG}.SkillDefs.LABELS[row] + " perk)";
  {PKG}.MsgRoute.said(dl);
  pr.sendMessage({MSG}.raw(dl).color("#b8f0a0"));''')

# ---------------------------------------------------------------- Brew.extraPotion: route "drop"
rep('''# ================= Brew.extraPotion (0.4): the brewer's extra-potion perk (world thread) =================
''', '''# ================= 0.4.34 Brew.potRoute: route "drop" of an extra potion - true = handled (off, or the feed card was taken) =================
brew.addMethod(CtNewMethod.make(f"""
public static boolean potRoute(java.util.UUID u, String id, long n) {{
  String rt = {PKG}.MsgRoute.route(u, "drop");
  if ("off".equals(rt)) {{ {PKG}.MsgRoute.off(); return true; }}
  if (!"feed".equals(rt)) return false;
  if (!{PKG}.MsgRoute.gate(u, "drop", id, 1000L, 0L)) return true;   // review fix: a NEW item's card at most once a second
  return {PKG}.MsgRoute.feed(u, "drop", id, "Extra potion: " + {PKG}.MsgRoute.pretty(id), n);
}}""", brew))
# ================= Brew.extraPotion (0.4): the brewer's extra-potion perk (world thread) =================
''')
rep('''    if (what == null || !{PKG}.SkillStore.notifyOn(u, "skills.extraPotion")) return;
''', '''    if (what == null || !{PKG}.SkillStore.notifyOn(u, "skills.extraPotion")) return;
    if ({PKG}.Brew.potRoute(u, id, (long) (q * hits))) return;                           // 0.4.34: route "drop"
''')
rep('''    pr.sendMessage({MSG}.raw("Extra potion" + (tm[0] > 1L ? " x" + tm[0] : "") + "!" + what + "  (Alchemy perk)").color("#a0f0e0"));''',
    '''    String el = "Extra potion" + (tm[0] > 1L ? " x" + tm[0] : "") + "!" + what + "  (Alchemy perk)";
    {PKG}.MsgRoute.said(el);
    pr.sendMessage({MSG}.raw(el).color("#a0f0e0"));''')

# ---------------------------------------------------------------- Fell.end summary: route "pickup"
rep('''# end a watch: release its claims / layer entries (only where they still point at it), optional chat summary, debug line (spec 2.5 / 2.9)
fel.addMethod(CtNewMethod.make(f"""''', '''# 0.4.34 route "pickup" for the felled-tree summary: true = handled (off, or a feed card "Tree felled: 207 logs, 36 leaves" - the XP is on
# the skill flash already); false = send 0.4.33's chat line
fel.addMethod(CtNewMethod.make(f"""
public static boolean sumFeed(java.util.UUID u, int logs, int leaves) {{
  String rt = {PKG}.MsgRoute.route(u, "pickup");
  if ("off".equals(rt)) {{ {PKG}.MsgRoute.off(); return true; }}
  if (!"feed".equals(rt)) return false;
  String t = "Tree felled: " + logs + (logs == 1 ? " log" : " logs") + (leaves > 0 ? ", " + leaves + (leaves == 1 ? " leaf" : " leaves") : "");
  return {PKG}.MsgRoute.feed(u, "pickup", null, t, 0L);
}}""", fel))
# end a watch: release its claims / layer entries (only where they still point at it), optional chat summary, debug line (spec 2.5 / 2.9)
fel.addMethod(CtNewMethod.make(f"""''')
rep('''      {PR} pr = {UNI}.get().getPlayer(W.u);
      if (pr != null && pr.isValid()) {{
        StringBuilder sb = new StringBuilder("Tree felled: ");''', '''      {PR} pr = {UNI}.get().getPlayer(W.u);
      if (pr != null && pr.isValid() && !sumFeed(W.u, W.cLogs, W.cLeaves)) {{
        StringBuilder sb = new StringBuilder("Tree felled: ");''')
rep('''        if (W.xp > 0L && W.row >= 0 && W.row < {PKG}.SkillDefs.N) sb.append(" (+").append({PKG}.SkillDefs.fmt(W.xp)).append(" ").append({PKG}.SkillDefs.LABELS[W.row]).append(" XP)");
        pr.sendMessage({MSG}.raw(sb.toString()).color("#9fe0a0"));''', '''        if (W.xp > 0L && W.row >= 0 && W.row < {PKG}.SkillDefs.N) sb.append(" (+").append({PKG}.SkillDefs.fmt(W.xp)).append(" ").append({PKG}.SkillDefs.LABELS[W.row]).append(" XP)");
        {PKG}.MsgRoute.said(sb.toString());
        pr.sendMessage({MSG}.raw(sb.toString()).color("#9fe0a0"));''')

# ---------------------------------------------------------------- write the new class
rep('''          rbf, pset, sio, polm):   # 0.4.32: + PlacedSet, SkillIO, PollMig;''', '''          rbf, pset, sio, polm, mrt):   # 0.4.34: + MsgRoute; 0.4.32: + PlacedSet, SkillIO, PollMig;''')

# ---------------------------------------------------------------- checks
assert s.count("MsgRoute.route(u, ") == 5 and s.count("MsgRoute.said(") == 5
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.4.33 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.4.33,", len(_gone), "0.4.33 lines replaced;", len(OLDS), "anchors")
