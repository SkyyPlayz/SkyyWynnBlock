"""Derive SkyyRebirth/build_skyyrebirth_0.2.py from SkyyRebirth/build_skyyrebirth_0.1.py (= the tools/deploy_set.py SET pin, a hand-written
new-mod script). rep(old, new) with asserted anchors; 0.1 stays untouched; its line endings are kept; every change is undone at the end to
prove nothing else changed.
Run:  python tools/rebirth_0_2_patch.py   then   python SkyyRebirth/build_skyyrebirth_0.2.py   (NO --deploy: coordinated deploy)
Test: python SkyyRebirth/test_skyyrebirth_0.2.py --dir tools/dev/scratch/<yours>/rb   (bare JVM, -Xverify:all, every new code path executed;
      loads the real SkyySkills 0.4.36 + SkyyCoins 0.1.7 + SkyyBank 0.1.11 + SkyyProfiles 0.1.13 jars for the crash proofs)

0.2 (2026-10-14) = REBIRTH ROUND R3 (research/cloud/Rebirth-Spec.md section 6 R3 + sections 3.3, 4.3, 5; Skyy's answers docs/answered/economy.md
2026-10-13 REBIRTH + 2026-10-14). THE WHOLE FEATURE STAYS OFF (rebirth.on=false) - only admins can run it (/rebirthadmin) until Server
Setup -> Rebirth switches it on.
  THE JOURNALED TWO-PHASE COMMIT (spec 5.2 / 5.3) with the first participants SkyySkills (rebirth:part:skills, 0.4.36+), SkyyCoins
    (rebirth:part:coins, 0.1.7+) and SkyyBank (rebirth:part:bank, 0.1.11+); Trees / Classes / Gear join in later rounds (R5-R7), so a
    rebirth in 0.2 resets skills (not Exploration), the purse and the bank only - their tree nodes, ability levels and tools stay as
    they are until those rounds.
    Journal = Skyy_SkyyRebirth/journal/<pkey>.journal, one line per step, each appended + fsync'd (a torn last line = never written):
      BEGIN <txid> <pkey> <new n> <uuid> <parts> <live|force>   step 0: the click (busy from here)
      PREPARED <part> <facts>                                    step 1: each part backed up + staged its reset, answered its facts
      DECIDED commit <rewards> | DECIDED abort <why>              step 2: THE decision (points spec 3.5, bank bonus spec 3.3) - once
      COMMITTED <part>                                           step 3: each part applied its staged reset in ONE atomic write
      REBIRTH                                                    step 4: our own file: n, pts.<Arm>, title, cos.<n>, hist.<n>, lastTx
      DONE / ABORTED                                             step 5: the journal moves to journal/done/<pkey>.<txid>.journal
    Every participant stores rb.lastTx in the SAME atomic write as its reset, so a repeated commit answers "done" and changes nothing.
    RECOVERY (a restart, /rebirthadmin recover, and every 30 s while a rebirth is open; the first pass 10 s after start so every mod is
    up): no DECIDED -> abort to every part (staged files deleted; the profile is exactly as before); DECIDED commit -> commit again to
    the parts not COMMITTED (done ones answer "done"), then step 4, DONE. A part whose jar is missing (or that fails) leaves the journal
    open, the profile busy and "waiting for <mod>" in /rebirthadmin status - retried every 30 s and at every start. rebirth:fn:decision
    answers commit / abort / unknown from the open and the done journals (participants use it to clean an older staged file).
  BUSY: rebirth:busy:<uuid> + rebirth:fn:busy are true from BEGIN to DONE / ABORTED (also for journals found at start). SkyyCoins 0.1.7
    refuses spends + /pay, SkyyBank 0.1.11 deposit / withdraw, SkyyProfiles 0.1.13 a profile switch; income still lands (deltas).
  THE BUTTON (only while rebirth.on is true, and only when every requirement is met): "Rebirth" in the left panel of /rebirth - the first
    press arms it (the note: "Resets skills, purse and bank to 0! ..."), a second press 0.8-10 s later starts the rebirth, the page closes and chat says "The
    void is imprinting your soul ..." then the result. Requirement line 1 now also says when a part's jar is missing, a rebirth is still
    finishing or a profile switch is running. The Nexus itself stays the hover (the click is the button beside it - UNVERIFIED whether a
    click on the Nexus disc itself can be bound; asked as a design question).
  BANK BONUS (spec 3.3, Skyy Q7): balance = purse + bank at reset (the parts' prepare facts); bonus = min(bank.bonusPer, bank.bonusBase x
    log10(1 + balance / 100,000)) percentage points, total at most bank.bonusMax (SkyyBank adds it to the profile's rb.bonus). Purse and
    bank go to 0 (Skyy Q8 "0 coins", 2026-10-12 "you lose the money"). New Server Setup rows (Rewards): bank.bonusBase 0.25, bank.bonusPer
    1, bank.bonusMax 3.
  /rebirthadmin (skyyrebirth.admin; works while rebirth is OFF - the admin test path): status | dryrun | rebirth | crashtest <0-7> |
    recover | backups. dryrun asks every part to MEASURE (nothing written) and prints the facts + the decision it would make. rebirth runs
    a real rebirth on YOUR active profile with the class / place / combat checks skipped (type it twice within 10 s). crashtest <p> does
    the same but stops right after point p (0 BEGIN, 1 first PREPARED, 2 all PREPARED, 3 DECIDED, 4 first COMMITTED, 5 all COMMITTED,
    6 REBIRTH, 7 DONE) like a crash there - the profile stays busy; /rebirthadmin recover (or a restart) finishes it: 0-2 = nothing
    changed, 3-7 = the full rebirth. backups lists the per-mod backups of your profile (rebirth-backup/<pkey>/<txid>/, last 3 kept).
  Requirement checks at the click (spec 2.1): switched on, every part loaded, not busy, class at max level (live only), rebirths left,
    not in combat, on your island / the hub. The decision re-checks the class level from SkyySkills' own facts (live) and the max.
  FIX ROUND (2026-10-14, critics): a journal with NO complete line (a kill / disk full between its creation and BEGIN) = nothing started:
    begin() deletes it when BEGIN fails, startup() and recovery delete such a stub (RbTx.dropStub, under begin's monitor) and free the
    profile - a journal with complete but unreadable lines still waits for an admin; begin() claims FRESH BEFORE the file exists (recovery
    never aborts a run that is still being born); a waiting rebirth logs its reason once (again only when it changes), not every 30 s;
    the player's click hands begin + drive to SkyyRebirth-IO (RbRun mode 4) - no journal fsync / file read on the world thread.
  FIX ROUND 2 (2026-10-14, critics): our own players/<pkey>.properties is fsync'd before its rename (like the three parts - a power cut
    can no longer leave a 0-byte file that forgets a finished rebirth); RbJournal.append first cuts a torn tail (bytes after the last
    newline) so a new line is never glued onto a fragment; rebirth:fn:count answers the NEW n from the moment the decision is commit
    (RbStore.PEND, also for journals found at start) so level coins never pay at the old factor in the commit window; begin claims BUSY
    first and then checks profile:busy (SkyyProfiles 0.1.13 claims profile:busy first and then checks rebirth:fn:busy - one side always
    sees the other); a throw inside a run (RbRun 0 / 4) puts the profile on the 30 s retry instead of leaving it busy; the Rebirth button
    ignores a second press under 0.8 s (a double-click is not a confirm) and the armed note warns "Resets skills, purse and bank to 0".
"""
import difflib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyRebirth", "build_skyyrebirth_0.1.py")
dst = os.path.join(ROOT, "SkyyRebirth", "build_skyyrebirth_0.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
s = raw.decode("utf8").replace("\r\n", "\n")
LF = "\n"
S0 = s
assert 'VERSION = "0.1"' in s and "RbJournal" not in s, "not the 0.1 script"
OLDS = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    OLDS.append(old)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.2 (2026-10-14)"):].rstrip() + "\n"

# ================================================================================================ docstring + version
rep('''"""SkyyRebirth 0.1 - build script (javassist via jpype). A NEW small mod: the rebirth (New Game+) module, round R2 of
research/cloud/Rebirth-Spec.md section 6 (Skyy's answers: docs/answered/economy.md 2026-10-13 REBIRTH lines, which win).
Run:   python SkyyRebirth/build_skyyrebirth_0.1.py   -> SkyyRebirth/SkyyRebirth-0.1.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyRebirth/test_skyyrebirth_0.1.py --dir tools/dev/scratch/<yours>/rb   (bare JVM, -Xverify:all, every code path executed)
''', '''"""SkyyRebirth 0.2 - build script (javassist via jpype). GENERATED by tools/rebirth_0_2_patch.py from build_skyyrebirth_0.1.py (the R2 new-mod
script) - edit the patch, never this file. The rebirth (New Game+) module, rounds R2 + R3 of research/cloud/Rebirth-Spec.md section 6
(Skyy's answers: docs/answered/economy.md 2026-10-13 / 2026-10-14 REBIRTH lines, which win).
Run:   python SkyyRebirth/build_skyyrebirth_0.2.py   -> SkyyRebirth/SkyyRebirth-0.2.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyRebirth/test_skyyrebirth_0.2.py --dir tools/dev/scratch/<yours>/rb   (bare JVM, -Xverify:all, every code path executed)

''' + NOTE + '''  CHECKED: SkyyRebirth/test_skyyrebirth_0.2.py.

0.1 (2026-10-14, round R2) - the text below is 0.1's; 0.2 lines above win where they differ:
''')
rep('VERSION = "0.1"', 'VERSION = "0.2"')

# ================================================================================================ fix round 2: RbStore
# our own profile file fsync'd before the rename (a power cut after the journal's DONE could leave a 0-byte file = a forgotten rebirth)
rep('''    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyRebirth @VERSION@ - one profile (research/cloud/Rebirth-Spec.md 4.2)"); } finally { out.close(); }''',
    '''    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());   // 0.2 fix round 2: fsync'd before the rename (like the parts)
    try { p.store(out, "SkyyRebirth @VERSION@ - one profile (research/cloud/Rebirth-Spec.md 4.2)"); out.flush(); out.getFD().sync(); } finally { out.close(); }''')
# PEND = pkey -> Integer new n from DECIDED commit until finish: rebirth:fn:count answers it (SkyySkills' level coins use the new factor
# from the moment its reset may land)
rep('''F(st, "public static final java.util.concurrent.ConcurrentHashMap BUSY = new java.util.concurrent.ConcurrentHashMap();")''',
    '''F(st, "public static final java.util.concurrent.ConcurrentHashMap BUSY = new java.util.concurrent.ConcurrentHashMap();")
F(st, "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();")   # 0.2 fix round 2''')
rep('''    if (this.mode == 0) return Integer.valueOf(@PKG@.RbStore.n(k));''',
    '''    if (this.mode == 0) {   // 0.2 fix round 2: a decided (commit) rebirth counts at once (RbStore.PEND)
      int n0 = @PKG@.RbStore.n(k);
      Object pn = @PKG@.RbStore.PEND.get(k);
      if (pn instanceof Integer && ((Integer) pn).intValue() > n0) n0 = ((Integer) pn).intValue();
      return Integer.valueOf(n0);
    }''')

# ================================================================================================ engine names + probes
rep('''    "PM":   "com.hypixel.hytale.server.core.permissions.PermissionsModule",
''', '''    "PM":   "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
''')
rep('''             (PGM, "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss")):''',
    '''             (PGM, "openCustomPage"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["LIFE"], "CanDismiss"),
             (T["UNI"], "getPlayer"), (T["PR"], "getWorldUuid"), (T["WLD"], "execute"), (T["PAGE"], "rebuild"), (T["ATY"], "GREEDY_STRING"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addUsageVariant")):''')

# ================================================================================================ config: text, fields, rows, loader
rep('''    "# rebirth.on = the whole rebirth feature. false (default): players cannot open /rebirth; admins (skyyrebirth.admin) can view it.",
    "# SkyyRebirth 0.1 never resets anything (no rebirth button yet).",
    "rebirth.on=false",''', '''    "# rebirth.on = the whole rebirth feature. false (default): players cannot open /rebirth; admins (skyyrebirth.admin) can view it",
    "# and test it with /rebirthadmin. true: every player at max class level can rebirth from /rebirth (resets their skills, purse and bank).",
    "rebirth.on=false",''')
rep('''    "dust.perNode=0.25",
    "",
])''', '''    "dust.perNode=0.25",
    "# The bank bonus at a rebirth (percentage points on top of the interest brackets): bank.bonusBase x log10(1 + (purse + bank) / 100000),",
    "# at most bank.bonusPer per rebirth and bank.bonusMax in total.",
    "bank.bonusBase=0.25",
    "bank.bonusPer=1",
    "bank.bonusMax=3",
    "",
])''')
rep('''          "public static volatile int RANKS = 1;", "public static volatile double DUST_FIRST = 2.0;", "public static volatile double DUST_NODE = 0.25;",''',
    '''          "public static volatile int RANKS = 1;", "public static volatile double DUST_FIRST = 2.0;", "public static volatile double DUST_NODE = 0.25;",
          "public static volatile double BANK_BASE = 0.25;", "public static volatile double BANK_PER = 1.0;", "public static volatile double BANK_MAX = 3.0;",''')
rep('''     "Off: only admins can view /rebirth. 0.1 has no rebirth button yet - nothing is ever reset.",''',
    '''     "Off: admins only (/rebirthadmin). On: max-class players can rebirth - Bazaar / AH not checked yet.",''')
rep('''     "Each level of an arm's Dust node adds this to that arm's Dust multiplier.", "field:RbCfg.DUST_NODE@config.properties:dust.perNode"),
]''', '''     "Each level of an arm's Dust node adds this to that arm's Dust multiplier.", "field:RbCfg.DUST_NODE@config.properties:dust.perNode"),
    ("bank.bonusBase", "Bank bonus scale", "rewards", "dec", "0.25", "0", "5", "", "", "live",
     "Bank rate bonus per rebirth = this x log10(1 + (purse + bank) / 100,000) percentage points.", "field:RbCfg.BANK_BASE@config.properties:bank.bonusBase"),
    ("bank.bonusPer", "Bank bonus max per rebirth", "rewards", "dec", "1", "0", "10", "", "%", "live",
     "One rebirth adds at most this to the bank interest rate.", "field:RbCfg.BANK_PER@config.properties:bank.bonusPer"),
    ("bank.bonusMax", "Bank bonus max in total", "rewards", "dec", "3", "0", "20", "", "%", "live",
     "A profile's bank rate bonus from all its rebirths is at most this.", "field:RbCfg.BANK_MAX@config.properties:bank.bonusMax"),
]''')
rep('''NOTE="Rebirth is off by default. 0.1 shows /rebirth only - no rebirth button yet."''',
    '''NOTE="Rebirth is off by default. Admins can test it with /rebirthadmin (dryrun, rebirth, crashtest)."''')
rep('''  DUST_NODE = decOf(p.getProperty("dust.perNode"), 0.25, 0.0, 5.0);
''', '''  DUST_NODE = decOf(p.getProperty("dust.perNode"), 0.25, 0.0, 5.0);
  BANK_BASE = decOf(p.getProperty("bank.bonusBase"), 0.25, 0.0, 5.0);
  BANK_PER = decOf(p.getProperty("bank.bonusPer"), 1.0, 0.0, 10.0);
  BANK_MAX = decOf(p.getProperty("bank.bonusMax"), 3.0, 0.0, 20.0);
''')
rep(''' + " from rebirth 1 (+" + num(DUST_NODE) + " per node level)";''',
    ''' + " from rebirth 1 (+" + num(DUST_NODE) + " per node level), bank bonus " + num(BANK_BASE) + " x log10 (max +" + num(BANK_PER) + " % a rebirth, +" + num(BANK_MAX) + " % in total)";''')

# ================================================================================================ RbMath: the bank bonus (spec 3.3)
rep('''M(mth, r"""
public static String roman(int n) {''', '''# spec 3.3 (Skyy Q7): the bank bonus of ONE rebirth in parts per million (1 % = 10,000): min(bank.bonusPer, bank.bonusBase x log10(1 +
# balance / 100,000)) percentage points; maxPpm = bank.bonusMax (the total SkyyBank keeps)
M(mth, r"""
public static long bonusPpm(long bal) {
  if (bal <= 0L) return 0L;
  double x = @PKG@.RbCfg.BANK_BASE * Math.log10(1.0 + (double) bal / 100000.0);
  double cap = @PKG@.RbCfg.BANK_PER;
  if (x > cap) x = cap;
  if (!(x > 0.0)) return 0L;
  return Math.round(x * 10000.0);
}""")
M(mth, r"""
public static long maxPpm() {
  double m = @PKG@.RbCfg.BANK_MAX;
  return m > 0.0 ? Math.round(m * 10000.0) : 0L;
}""")
M(mth, r"""
public static String pct(long ppm) {
  if (ppm < 0L) ppm = 0L;
  long h = (ppm + 50L) / 100L;
  return (h / 100L) + "." + String.valueOf(100L + h % 100L).substring(1);
}""")
M(mth, r"""
public static String roman(int n) {''')

# ================================================================================================ RbJ + RbJournal (before RbFn: the decision)
rep('''# ================= RbFn: the bridge functions (mode 0 count, 1 cap, 2 node, 3 dustmult, 4 busy, 5 decision). Any thread, never throws =================''',
    r'''# ================= 0.2 RbJ: one parsed journal (RbJournal.parse) =================
rbj = mk("RbJ")
for f in ("public String tx;", "public String k;", "public String uuid;", "public String mode;", "public String decided;", "public String rewards;",
          "public String reason;", "public int newN;", "public String[] parts;", "public java.util.HashMap prepared;", "public java.util.HashSet committed;",
          "public boolean rebirth;", "public boolean done;", "public boolean aborted;", "public boolean bad;"):
    F(rbj, f)
C(rbj, "public RbJ() { this.prepared = new java.util.HashMap(); this.committed = new java.util.HashSet(); this.parts = new String[0]; this.bad = true; }")

# ================= 0.2 RbJournal: Skyy_SkyyRebirth/journal/<pkey>.journal (spec 5.2): append + fsync, read (a torn last line is ignored),
# parse, the participants list, rebirth:fn:decision. Pure files + memory; any thread (the coordinator runs on SkyyRebirth-IO) =================
jrn = mk("RbJournal")
for f in ("public static java.nio.file.Path DIR;",
          'public static final String[] PARTS = new String[] { "skills", "coins", "bank" };',
          'public static final String[] JARS = new String[] { "SkyySkills 0.4.36+", "SkyyCoins 0.1.7+", "SkyyBank 0.1.11+" };',
          "public static final java.util.concurrent.ConcurrentHashMap TXK = new java.util.concurrent.ConcurrentHashMap();"):   # open txid -> pkey
    F(jrn, f)
M(jrn, r"""
public static java.util.function.Function part(String name) {
  Object f = @PKG@.RbCfg.bridge().get("rebirth:part:" + name);
  return f instanceof java.util.function.Function ? (java.util.function.Function) f : null;
}""")
M(jrn, r"""
public static String jar(String name) {
  for (int i = 0; i < PARTS.length; i++) if (PARTS[i].equals(name)) return JARS[i];
  return name;
}""")
# the first part whose jar is not loaded (its jar text), null = every part is there
M(jrn, r"""
public static String missing() {
  for (int i = 0; i < PARTS.length; i++) if (part(PARTS[i]) == null) return JARS[i];
  return null;
}""")
M(jrn, r"""
public static java.nio.file.Path file(String k) {
  return DIR.resolve(k + ".journal");
}""")
M(jrn, r"""
public static boolean open(String k) {
  return DIR != null && java.nio.file.Files.exists(file(k), new java.nio.file.LinkOption[0]);
}""")
M(jrn, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\r', ' ').replace('\n', ' ');
}""")
# fix round 2: bytes after the last newline = a line torn by a crash (never written) - cut off (fsync'd) before the next append, so a
# fragment like "DECIDED commit pts.cl" can never join the next line into something parse() accepts
M(jrn, r"""
public static void cutTorn(java.io.File fl) throws java.io.IOException {
  if (!fl.isFile() || fl.length() <= 0L) return;
  java.io.RandomAccessFile raf = new java.io.RandomAccessFile(fl, "rw");
  try {
    long len = raf.length();
    long p = len - 1L;
    while (p >= 0L) {
      raf.seek(p);
      if (raf.read() == 10) break;
      p--;
    }
    if (p + 1L < len) { raf.setLength(p + 1L); raf.getFD().sync(); }
  } finally { raf.close(); }
}""")
M(jrn, r"""
public static void append(String k, String line) throws java.io.IOException {
  java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
  cutTorn(file(k).toFile());   // fix round 2: never glue a line onto a torn tail
  java.io.FileOutputStream out = new java.io.FileOutputStream(file(k).toFile(), true);
  try {
    out.write((clean(line) + "\n").getBytes("UTF-8"));
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
}""")
# every complete line (a line without its newline was torn by a crash = never written); null = no file / unreadable
M(jrn, r"""
public static String[] lines(java.nio.file.Path f) {
  try {
    if (f == null || !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    String t = new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
    int end = t.lastIndexOf('\n');
    if (end < 0) return new String[0];
    t = t.substring(0, end);
    if (t.length() == 0) return new String[0];
    return t.split("\n");
  } catch (Throwable e) { return null; }
}""")
M(jrn, r"""
public static @PKG@.RbJ parse(String[] ls) {
  @PKG@.RbJ j = new @PKG@.RbJ();
  if (ls == null) return j;
  try {
    for (int i = 0; i < ls.length; i++) {
      String l = ls[i];
      if (l.startsWith("BEGIN ")) {
        String[] a = l.split(" ");
        if (a.length >= 7) { j.tx = a[1]; j.k = a[2]; j.newN = Integer.parseInt(a[3]); j.uuid = a[4]; j.parts = a[5].split(","); j.mode = a[6]; }
      } else if (l.startsWith("PREPARED ")) {
        int sp = l.indexOf(' ', 9);
        String p = sp < 0 ? l.substring(9) : l.substring(9, sp);
        j.prepared.put(p, sp < 0 ? "" : l.substring(sp + 1));
      } else if (l.startsWith("DECIDED commit")) {
        if (j.decided == null) { j.decided = "commit"; j.rewards = l.length() > 15 ? l.substring(15) : ""; }
      } else if (l.startsWith("DECIDED abort")) {
        if (j.decided == null) { j.decided = "abort"; j.reason = l.length() > 14 ? l.substring(14) : ""; }
      } else if (l.startsWith("COMMITTED ")) {
        j.committed.add(l.substring(10).trim());
      } else if (l.equals("REBIRTH")) {
        j.rebirth = true;
      } else if (l.equals("DONE")) {
        j.done = true;
      } else if (l.equals("ABORTED")) {
        j.aborted = true;
      }
    }
    j.bad = j.tx == null || j.k == null || j.parts == null || j.parts.length == 0;
  } catch (Throwable t) { j.bad = true; }
  return j;
}""")
M(jrn, r"""
public static @PKG@.RbJ read(String k) {
  return parse(lines(file(k)));
}""")
M(jrn, r"""
public static String verdict(@PKG@.RbJ j, String tx) {
  if (j == null || j.bad || !tx.equals(j.tx)) return null;
  if ("commit".equals(j.decided)) return "commit";
  if ("abort".equals(j.decided) || j.aborted) return "abort";
  return "unknown";
}""")
# rebirth:fn:decision (spec 5.3): commit / abort / unknown - the open journal first, then every open and every done journal
M(jrn, r"""
public static String decision(String tx) {
  if (tx == null || DIR == null || !tx.matches("tx[0-9]{13}-[0-9a-f]{6}")) return "unknown";
  Object k = TXK.get(tx);
  if (k instanceof String) {
    String v = verdict(read((String) k), tx);
    if (v != null) return v;
  }
  java.io.File[] fs = DIR.toFile().listFiles();
  if (fs != null) for (int i = 0; i < fs.length; i++) {
    if (!fs[i].isFile() || !fs[i].getName().endsWith(".journal")) continue;
    String v = verdict(parse(lines(fs[i].toPath())), tx);
    if (v != null) return v;
  }
  java.io.File[] ds = DIR.resolve("done").toFile().listFiles();
  if (ds != null) for (int i = 0; i < ds.length; i++) {
    if (!ds[i].getName().endsWith("." + tx + ".journal")) continue;
    String v = verdict(parse(lines(ds[i].toPath())), tx);
    if (v != null) return v;
  }
  return "unknown";
}""")

# ================= RbFn: the bridge functions (mode 0 count, 1 cap, 2 node, 3 dustmult, 4 busy, 5 decision). Any thread, never throws =================''')
rep('''    if (this.mode == 5) return "unknown";''', '''    if (this.mode == 5) return o instanceof String ? @PKG@.RbJournal.decision((String) o) : "unknown";   // 0.2: the journals''')

# ================================================================================================ RbCheck: requirement 1 knows the parts + busy
rep('''  if (@PKG@.RbCfg.ON) { t[0] = "OK  Rebirth is switched on"; c[0] = "@GOOD@"; }
  else { t[0] = "NO  Rebirth is switched off"; c[0] = "@BAD@"; all = false; }''', '''  if (!@PKG@.RbCfg.ON) { t[0] = "NO  Rebirth is switched off"; c[0] = "@BAD@"; all = false; }
  else {
    String miss = @PKG@.RbJournal.missing();   // 0.2: every part loaded, nothing running on this profile
    if (miss != null) { t[0] = "NO  Needs " + miss; c[0] = "@BAD@"; all = false; }
    else if (@PKG@.RbStore.BUSY.containsKey(@PKG@.RbCfg.pkey(u))) { t[0] = "NO  A rebirth is finishing"; c[0] = "@BAD@"; all = false; }
    else if (@PKG@.RbCfg.bridge().get("profile:busy:" + u) != null) { t[0] = "NO  A profile switch is running"; c[0] = "@BAD@"; all = false; }
    else { t[0] = "OK  Rebirth is switched on"; c[0] = "@GOOD@"; }
  }''')
rep('''  else sb.append(Boolean.TRUE.equals(req[2]) ? "Every requirement is met - the rebirth button comes in a later update." : "Not ready yet - the NO lines above are what is missing.");''',
    '''  else sb.append(Boolean.TRUE.equals(req[2]) ? "Every requirement is met - press Rebirth on the left, then press it again to confirm." : "Not ready yet - the NO lines above are what is missing.");''')

# ================================================================================================ RbTx: the coordinator (after RbCheck, before the page)
TX = r'''
# ================= 0.2 RbTell: one chat line on the player's world thread =================
tel = mk("RbTell", None, ("java.lang.Runnable",))
F(tel, "public @PR@ pr;")
F(tel, "public String msg;")
F(tel, "public String col;")
C(tel, "public RbTell(@PR@ pr, String msg, String col) { this.pr = pr; this.msg = msg; this.col = col; }")
M(tel, r"""
public void run() {
  try { if (this.pr != null && this.pr.isValid()) this.pr.sendMessage(@MSG@.raw(this.msg).color(this.col)); } catch (Throwable t) { }
}""")

# ================= 0.2 RbTx: the journaled two-phase commit (spec 5.2 / 5.3). begin on the caller (one synchronized method: the checks + BEGIN);
# everything after it on SkyyRebirth-IO (one thread: one rebirth step at a time; inline when IO is not running - tests). HALTS = txid ->
# the crashtest point it stops after; HALTED = pkey -> what stopped (skipped by the 30 s retry until /rebirthadmin recover or a restart);
# WAIT = pkey -> why it waits (a part missing / failing); FRESH = pkey -> txid of a run that still has to prepare (recovery leaves it alone);
# LAST = pkey -> the last result line (status); TEST_TOLD = the harness's chat sink =================
# RbRun is made first (RbTx.kick creates one); its run() comes after RbTx's methods
run_ = mk("RbRun", None, ("java.lang.Runnable",))
F(run_, "public String k;")
F(run_, "public int mode;")
F(run_, "public java.util.UUID u;")   # fix round: mode 4 = a player's rebirth (begin + drive on SkyyRebirth-IO)
C(run_, "public RbRun(String k, int mode) { this.k = k; this.mode = mode; }")
C(run_, "public RbRun(String k, int mode, java.util.UUID u) { this.k = k; this.mode = mode; this.u = u; }")
tx = mk("RbTx")
for f in ("public static final java.util.concurrent.ConcurrentHashMap HALTS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap HALTED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap WAIT = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap FRESH = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap WLOG = new java.util.concurrent.ConcurrentHashMap();",   # fix round: last logged wait
          "public static volatile java.util.ArrayList TEST_TOLD = null;",
          "public static final java.util.concurrent.atomic.AtomicLong DONE = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong ABORTS = new java.util.concurrent.atomic.AtomicLong();"):
    F(tx, f)
M(tx, r"""
public static String newTx() {
  String r = Integer.toHexString(0x1000000 + java.util.concurrent.ThreadLocalRandom.current().nextInt(0x1000000)).substring(1);
  String ms = String.valueOf(System.currentTimeMillis());
  while (ms.length() < 13) ms = "0" + ms;
  return "tx" + ms + "-" + r;
}""")
M(tx, r"""
public static void tell(String uuid, String msg, String col) {
  try {
    java.util.ArrayList tt = TEST_TOLD;
    if (tt != null) { tt.add(msg); return; }
    if (uuid == null || uuid.length() < 36) return;
    @PR@ pr = @UNI@.get().getPlayer(java.util.UUID.fromString(uuid));
    if (pr == null || !pr.isValid()) return;
    @WLD@ w = @UNI@.get().getWorld(pr.getWorldUuid());
    if (w != null) w.execute(new @PKG@.RbTell(pr, msg, col));
  } catch (Throwable t) { }
}""")
M(tx, r"""
public static void note(String k, String m) {
  if (k != null) LAST.put(k, m);
  @PKG@.RbCfg.info(m);
}""")
M(tx, r"""
public static java.util.Properties facts(Object s) {
  java.util.Properties p = new java.util.Properties();
  if (!(s instanceof String)) return p;
  String[] a = ((String) s).split(";");
  for (int i = 0; i < a.length; i++) {
    int e = a[i].indexOf('=');
    if (e > 0) p.setProperty(a[i].substring(0, e).trim(), a[i].substring(e + 1).trim());
  }
  return p;
}""")
M(tx, r"""
public static long lng(java.util.Properties p, String key, long d) {
  String v = p == null ? null : p.getProperty(key);
  if (v == null) return d;
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
# "run/toCap/level/cap" -> 4 longs, null = absent / bad
M(tx, r"""
public static long[] arm(String v) {
  if (v == null) return null;
  String[] a = v.split("/");
  if (a.length < 4) return null;
  long[] r = new long[4];
  try { for (int i = 0; i < 4; i++) r[i] = Long.parseLong(a[i].trim()); } catch (Throwable t) { return null; }
  return r;
}""")
# step 2 (spec 3.3 / 3.5): { "commit", rewards } or { "abort", why } from the PREPARED facts only (what the journal holds = what recovery sees)
M(tx, r"""
public static String[] decide(@PKG@.RbJ j) {
  java.util.Properties sk = facts(j.prepared.get("skills"));
  java.util.Properties co = facts(j.prepared.get("coins"));
  java.util.Properties bk = facts(j.prepared.get("bank"));
  if (j.newN < 1 || j.newN > @PKG@.RbCfg.MAX) return new String[] { "abort", "rebirth " + j.newN + " is past the max (" + @PKG@.RbCfg.MAX + ")" };
  long[] ca = arm(sk.getProperty("arm.class"));
  if ("live".equals(j.mode)) {
    if (ca == null) return new String[] { "abort", "no class skill on this profile" };
    if (ca[2] < ca[3]) return new String[] { "abort", "the class is level " + ca[2] + " of " + ca[3] };
  }
  StringBuilder rw = new StringBuilder();
  for (int i = 0; i < @PKG@.RbMath.ARMS.length; i++) {
    long[] a = arm(sk.getProperty("arm." + @PKG@.RbMath.ARM_SKILL[i]));
    int p = a == null ? 0 : @PKG@.RbMath.points(a[0], a[1], @PKG@.RbMath.ARM_B[i]);
    rw.append("pts.").append(@PKG@.RbMath.ARMS[i]).append('=').append(p).append(';');
  }
  long purse = lng(co, "purse", 0L);
  long bank = lng(bk, "bank", 0L);
  long bal = purse + bank;
  if (bal < 0L) bal = Long.MAX_VALUE;
  rw.append("bonus=").append(@PKG@.RbMath.bonusPpm(bal)).append(";max=").append(@PKG@.RbMath.maxPpm()).append(";bal=").append(bal);
  return new String[] { "commit", rw.toString() };
}""")
M(tx, r"""
public static boolean halt(String k, String t, int point) {
  Object h = HALTS.get(t);
  if (!(h instanceof Integer) || ((Integer) h).intValue() != point) return false;
  HALTS.remove(t);
  FRESH.remove(k);
  HALTED.put(k, t + " stopped after point " + point);
  note(k, "crashtest: rebirth " + t + " of " + k + " stopped after point " + point + " (like a crash) - /rebirthadmin recover or a restart finishes it");
  return true;
}""")
M(tx, r"""
public static void waitOn(String k, String why) {
  WAIT.put(k, why);
  FRESH.remove(k);
  String m = "rebirth of " + k + " is waiting: " + why;
  Object prev = WLOG.put(k, why);   // fix round: the 30 s retry logs a wait once, again only when the reason changes
  if (why.equals(prev)) { LAST.put(k, m); return; }
  note(k, m);
}""")
# fix round: a journal with NO complete line = BEGIN never finished (a kill / disk full between the file's creation and its first line):
# nothing was prepared, so the stub is deleted and the profile freed. Under begin's monitor and only while no run of k is being born
# (FRESH) - begin claims FRESH before it creates the file. true = it was such a stub and is gone.
M(tx, r"""
public static synchronized boolean dropStub(String k) {
  if (FRESH.containsKey(k)) return false;
  java.nio.file.Path f = @PKG@.RbJournal.file(k);
  String[] ls = @PKG@.RbJournal.lines(f);
  if (ls == null || ls.length != 0) return false;
  try { java.nio.file.Files.deleteIfExists(f); } catch (Throwable t) { return false; }
  @PKG@.RbStore.BUSY.remove(k);
  WAIT.remove(k);
  WLOG.remove(k);
  HALTED.remove(k);
  note(k, "journal/" + k + ".journal had no complete line (BEGIN never finished - nothing had started): removed, the profile is free");
  return true;
}""")
# spec 5.1 item 3 / step 0: the checks + BEGIN under ONE monitor (two clicks never start two rebirths of one profile). "+<txid>" / "-why"
M(tx, r"""
public static String begin0(String k, java.util.UUID u, String mode, int halt) {
  if (u != null && @PKG@.RbCfg.bridge().get("profile:busy:" + u) != null) return "-A profile switch is running - try again in a moment.";
  String miss = @PKG@.RbJournal.missing();
  if (miss != null) return "-Rebirth needs " + miss + " - it is not loaded.";
  java.util.Properties p = @PKG@.RbStore.readNow(k);
  if (p == null) return "-The rebirth file of this profile cannot be read - nothing changed (server log).";
  int n = @PKG@.RbStore.num(p, "n");
  if (n >= @PKG@.RbCfg.MAX) return "-Max rebirths reached (" + n + " of " + @PKG@.RbCfg.MAX + ").";
  String t = newTx();
  StringBuilder ps = new StringBuilder();
  for (int i = 0; i < @PKG@.RbJournal.PARTS.length; i++) { if (i > 0) ps.append(','); ps.append(@PKG@.RbJournal.PARTS[i]); }
  FRESH.put(k, t);   // fix round: claimed BEFORE the journal file exists - recovery / dropStub never touch a journal being born
  try { @PKG@.RbJournal.append(k, "BEGIN " + t + " " + k + " " + (n + 1) + " " + (u == null ? "-" : u.toString()) + " " + ps.toString() + " " + mode); }
  catch (Throwable e) {
    FRESH.remove(k);
    try { java.nio.file.Files.deleteIfExists(@PKG@.RbJournal.file(k)); } catch (Throwable e2) { }   // fix round: no BEGIN = nothing started, no stub left
    return "-Could not write the rebirth journal - nothing changed: " + e;
  }
  @PKG@.RbStore.BUSY.put(k, t);
  @PKG@.RbJournal.TXK.put(t, k);
  FRESH.put(k, t);
  if (halt >= 0) HALTS.put(t, Integer.valueOf(halt));
  return "+" + t;
}""")
# fix round 2: claim BUSY first, THEN check profile:busy (in begin0) - SkyyProfiles 0.1.13 sets profile:busy first, then asks
# rebirth:fn:busy, so a switch and a rebirth starting at the same moment always see each other. A refusal (or a throw) releases the claim
# unless a journal file is left (then startup / the recovery tick handles it).
M(tx, r"""
public static synchronized String begin(String k, java.util.UUID u, String mode, int halt) {
  if (!@PKG@.RbStore.validKey(k) || @PKG@.RbJournal.DIR == null || @PKG@.RbStore.DIR == null) return "-This profile cannot rebirth (no data folder).";
  if (@PKG@.RbStore.BUSY.containsKey(k) || @PKG@.RbJournal.open(k)) return "-A rebirth is already running on this profile.";
  @PKG@.RbStore.BUSY.put(k, "starting");
  String r;
  try { r = begin0(k, u, mode, halt); } catch (Throwable t) { FRESH.remove(k); r = "-Could not start the rebirth - nothing changed: " + t; }
  if (!r.startsWith("+") && !@PKG@.RbJournal.open(k)) @PKG@.RbStore.BUSY.remove(k);
  return r;
}""")
M(tx, r"""
public static void finish(String k, @PKG@.RbJ j, boolean ok) {
  java.nio.file.Path f = @PKG@.RbJournal.file(k);
  try {
    java.nio.file.Path dd = @PKG@.RbJournal.DIR.resolve("done");
    java.nio.file.Files.createDirectories(dd, new java.nio.file.attribute.FileAttribute[0]);
    @PKG@.RbStore.moveInto(f, dd.resolve(k + "." + j.tx + ".journal"));
    java.io.File[] old = dd.toFile().listFiles();
    long cut = System.currentTimeMillis() - 30L * 86400000L;
    if (old != null) for (int i = 0; i < old.length; i++) if (old[i].lastModified() < cut) old[i].delete();
  } catch (Throwable t) { waitOn(k, "the finished journal could not be moved to journal/done: " + t); return; }
  @PKG@.RbStore.BUSY.remove(k);
  @PKG@.RbStore.PEND.remove(k);   // fix round 2 (ok: our file holds the new n now)
  @PKG@.RbJournal.TXK.remove(j.tx);
  WAIT.remove(k);
  WLOG.remove(k);
  FRESH.remove(k);
  HALTED.remove(k);
  java.util.Properties rw = facts(j.rewards);
  if (ok) {
    DONE.incrementAndGet();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < @PKG@.RbMath.ARMS.length; i++) {
      long p = lng(rw, "pts." + @PKG@.RbMath.ARMS[i], 0L);
      if (p <= 0L) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(@PKG@.RbMath.ARMS[i]).append(" +").append(p);
    }
    long bp = lng(rw, "bonus", 0L);
    note(k, "rebirth " + j.tx + " of " + k + " DONE - rebirth " + j.newN + ", points " + (sb.length() > 0 ? sb.toString() : "none") + ", bank bonus +" + @PKG@.RbMath.pct(bp) + " %");
    tell(j.uuid, "[Rebirth] The void imprints your soul - rebirth " + j.newN + " done! You are Void-Touched " + @PKG@.RbMath.roman(j.newN) + ". Points: " + (sb.length() > 0 ? sb.toString() : "none") + ". Your skills, purse and bank start again; the bank pays you +" + @PKG@.RbMath.pct(bp) + " % more interest from now on.", "#E8A93B");
    try { if (j.uuid != null && j.uuid.length() >= 36) @PKG@.RbPub.publish(java.util.UUID.fromString(j.uuid)); } catch (Throwable t) { }
  } else {
    ABORTS.incrementAndGet();
    note(k, "rebirth " + j.tx + " of " + k + " cancelled (" + j.reason + ") - nothing changed");
    tell(j.uuid, "[Rebirth] The rebirth was cancelled - nothing changed. (" + j.reason + ")", "#ffcc00");
  }
}""")
# DECIDED abort (if no decision yet), abort to every part that is loaded (a missing one cleans its staged file at its next prepare),
# ABORTED, done. Never after DECIDED commit (forward only).
M(tx, r"""
public static void abortAll(String k, @PKG@.RbJ j, String why) {
  if ("commit".equals(j.decided)) { waitOn(k, "refused to abort a decided rebirth"); return; }
  if (j.decided == null) {
    try { @PKG@.RbJournal.append(k, "DECIDED abort " + why); } catch (Throwable t) { }
    j.decided = "abort";
    j.reason = why;
  }
  for (int i = 0; i < j.parts.length; i++) {
    java.util.function.Function f = @PKG@.RbJournal.part(j.parts[i]);
    if (f == null) continue;
    try { f.apply(new Object[] { "abort", k, j.tx, Integer.valueOf(j.newN), "" }); } catch (Throwable t) { }
  }
  try { @PKG@.RbJournal.append(k, "ABORTED"); } catch (Throwable t) { }
  finish(k, j, false);
}""")
# step 4: our own file (n, points, title, cosmetic, history, lastTx) - idempotent by lastTx; null = written (or already)
M(tx, r"""
public static String applyOwn(String k, @PKG@.RbJ j) {
  java.util.Properties cur = @PKG@.RbStore.readNow(k);
  if (cur == null) return "players/" + k + ".properties of SkyyRebirth cannot be read";
  if (j.tx.equals(cur.getProperty("lastTx"))) return null;
  java.util.Properties rw = facts(j.rewards);
  java.util.Properties p = new java.util.Properties();
  p.putAll(cur);
  p.setProperty("n", String.valueOf(j.newN));
  long tot = 0L;
  for (int i = 0; i < @PKG@.RbMath.ARMS.length; i++) {
    String a = @PKG@.RbMath.ARMS[i];
    long add = lng(rw, "pts." + a, 0L);
    if (add <= 0L) continue;
    tot += add;
    p.setProperty("pts." + a, String.valueOf(@PKG@.RbStore.num(cur, "pts." + a) + add));
  }
  p.setProperty("title", "Void-Touched " + @PKG@.RbMath.roman(j.newN));
  if (j.newN % 3 == 0) p.setProperty("cos." + j.newN, "1");
  p.setProperty("hist." + j.newN, System.currentTimeMillis() + " bal=" + lng(rw, "bal", 0L) + " pts=" + tot + " bonus=" + lng(rw, "bonus", 0L) + " tx=" + j.tx);
  p.setProperty("lastTx", j.tx);
  return @PKG@.RbStore.save(k, p);
}""")
M(tx, r"""
public static void forward(String k, @PKG@.RbJ j) {
  for (int i = 0; i < j.parts.length; i++) {
    String p = j.parts[i];
    if (j.committed.contains(p)) continue;
    java.util.function.Function f = @PKG@.RbJournal.part(p);
    if (f == null) { waitOn(k, "waiting for " + @PKG@.RbJournal.jar(p) + " (not loaded) - retried every 30 s and at every start"); return; }
    Object r;
    try { r = f.apply(new Object[] { "commit", k, j.tx, Integer.valueOf(j.newN), j.rewards }); } catch (Throwable t) { r = "err:" + t; }
    String rs = String.valueOf(r);
    if (!(rs.equals("ok") || rs.equals("done"))) { waitOn(k, p + " could not finish (" + rs + ") - retried every 30 s"); return; }
    try { @PKG@.RbJournal.append(k, "COMMITTED " + p); } catch (Throwable t) { waitOn(k, "could not write the journal: " + t); return; }
    j.committed.add(p);
    if (j.committed.size() == 1 && halt(k, j.tx, 4)) return;
    if (j.committed.size() >= j.parts.length && halt(k, j.tx, 5)) return;
  }
  if (!j.rebirth) {
    String e = applyOwn(k, j);
    if (e != null) { waitOn(k, e); return; }
    try { @PKG@.RbJournal.append(k, "REBIRTH"); } catch (Throwable t) { waitOn(k, "could not write the journal: " + t); return; }
    j.rebirth = true;
    if (halt(k, j.tx, 6)) return;
  }
  try { @PKG@.RbJournal.append(k, "DONE"); } catch (Throwable t) { waitOn(k, "could not write the journal: " + t); return; }
  j.done = true;
  if (halt(k, j.tx, 7)) return;
  finish(k, j, true);
}""")
# step 1: every part backs up + stages; false = stopped (aborted or halted)
M(tx, r"""
public static boolean prepareAll(String k, @PKG@.RbJ j) {
  int got = j.prepared.size();
  for (int i = 0; i < j.parts.length; i++) {
    String p = j.parts[i];
    if (j.prepared.containsKey(p)) continue;
    java.util.function.Function f = @PKG@.RbJournal.part(p);
    if (f == null) { abortAll(k, j, @PKG@.RbJournal.jar(p) + " is not loaded"); return false; }
    Object r;
    try { r = f.apply(new Object[] { "prepare", k, j.tx, Integer.valueOf(j.newN), "" }); } catch (Throwable t) { r = "err:" + t; }
    String rs = String.valueOf(r);
    if (!rs.startsWith("ok:")) { abortAll(k, j, p + " could not get ready (" + rs + ")"); return false; }
    try { @PKG@.RbJournal.append(k, "PREPARED " + p + " " + rs.substring(3)); } catch (Throwable t) { abortAll(k, j, "could not write the journal: " + t); return false; }
    j.prepared.put(p, rs.substring(3));
    got++;
    if (got == 1 && halt(k, j.tx, 1)) return false;
    if (got >= j.parts.length && halt(k, j.tx, 2)) return false;
  }
  return true;
}""")
# drive one profile's journal as far as it can go. fresh = the run begin() started (may prepare); a recovery (fresh false) never prepares:
# no decision yet = abort (spec 5.3)
M(tx, r"""
public static void drive(String k, boolean fresh) {
  if (!fresh && FRESH.containsKey(k)) return;
  java.nio.file.Path f = @PKG@.RbJournal.file(k);
  @PKG@.RbJ j = @PKG@.RbJournal.read(k);
  if (j.bad) {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { @PKG@.RbStore.BUSY.remove(k); FRESH.remove(k); return; }
    if (!fresh && dropStub(k)) return;   // fix round: no complete line = BEGIN never finished = nothing started
    @PKG@.RbStore.BUSY.put(k, "?");
    waitOn(k, "journal/" + k + ".journal cannot be read - an admin must look at it (the profile stays busy)");
    return;
  }
  @PKG@.RbStore.BUSY.put(k, j.tx);
  @PKG@.RbJournal.TXK.put(j.tx, k);
  if (j.done) { finish(k, j, true); return; }
  if (j.aborted) { finish(k, j, false); return; }
  if (j.decided == null) {
    if (!fresh) { abortAll(k, j, "the server stopped before every part was ready"); return; }
    if (j.prepared.isEmpty() && halt(k, j.tx, 0)) return;
    if (!prepareAll(k, j)) return;
    String[] d = decide(j);
    try { @PKG@.RbJournal.append(k, "DECIDED " + d[0] + " " + d[1]); }
    catch (Throwable t) { abortAll(k, j, "could not write the decision: " + t); return; }
    if ("commit".equals(d[0])) { j.decided = "commit"; j.rewards = d[1]; @PKG@.RbStore.PEND.put(k, Integer.valueOf(j.newN)); } else { j.decided = "abort"; j.reason = d[1]; }
    if (halt(k, j.tx, 3)) return;
  }
  if ("abort".equals(j.decided)) { abortAll(k, j, j.reason); return; }
  @PKG@.RbStore.PEND.put(k, Integer.valueOf(j.newN));   // fix round 2: decided commit = the new n counts from now on
  WAIT.remove(k);
  forward(k, j);
}""")
# every open journal (start-up, the 30 s retry, /rebirthadmin recover); all = also the crashtest-stopped ones. Returns how many were driven.
M(tx, r"""
public static int recoverAll(boolean all) {
  if (@PKG@.RbJournal.DIR == null) return 0;
  java.io.File[] fs = @PKG@.RbJournal.DIR.toFile().listFiles();
  if (fs == null) return 0;
  int n = 0;
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!fs[i].isFile() || !nm.endsWith(".journal")) continue;
    String k = nm.substring(0, nm.length() - 8);
    if (!@PKG@.RbStore.validKey(k) || FRESH.containsKey(k)) continue;
    if (HALTED.containsKey(k)) { if (!all) continue; HALTED.remove(k); }
    try { drive(k, false); } catch (Throwable t) { @PKG@.RbCfg.warn("recovery of " + k + " failed: " + t); }
    n++;
  }
  return n;
}""")
# start-up: every open journal makes its profile busy at once (spends / switches wait) - driven 10 s later (every mod is up then)
M(tx, r"""
public static int startup() {
  if (@PKG@.RbJournal.DIR == null) return 0;
  java.io.File[] fs = @PKG@.RbJournal.DIR.toFile().listFiles();
  if (fs == null) return 0;
  int n = 0;
  for (int i = 0; i < fs.length; i++) {
    String nm = fs[i].getName();
    if (!fs[i].isFile() || !nm.endsWith(".journal")) continue;
    String k = nm.substring(0, nm.length() - 8);
    if (!@PKG@.RbStore.validKey(k)) continue;
    if (dropStub(k)) continue;   // fix round: a journal with no complete line (BEGIN never finished) - removed, the profile is free
    @PKG@.RbJ j = @PKG@.RbJournal.parse(@PKG@.RbJournal.lines(fs[i].toPath()));
    @PKG@.RbStore.BUSY.put(k, j.bad ? "?" : j.tx);
    if (!j.bad) @PKG@.RbJournal.TXK.put(j.tx, k);
    if (!j.bad && "commit".equals(j.decided)) @PKG@.RbStore.PEND.put(k, Integer.valueOf(j.newN));   // fix round 2
    n++;
  }
  return n;
}""")
M(tx, r"""
public static void kick(String k) {
  java.util.concurrent.ExecutorService e = @PKG@.RbStore.IO;
  if (e != null) {
    try { e.execute(new @PKG@.RbRun(k, 0)); return; } catch (Throwable t) { }
  }
  drive(k, true);
}""")
# fix round: a player rebirth's begin + drive in one go - on SkyyRebirth-IO (RbRun mode 4; inline when IO is not running). "+txid" / "-why"
M(tx, r"""
public static String startNow(String k, java.util.UUID u) {
  String r = begin(k, u, "live", -1);
  if (r.startsWith("+")) drive(k, true);
  return r;
}""")
# the player's click (rebirth ON, every requirement met on the page's checks) -> "+..." started (or handed to IO) / "-why"
M(tx, r"""
public static String playerStart(java.util.UUID u, String world) {
  if (!@PKG@.RbCfg.ON) return "-Rebirth is switched off on this server.";
  String k = @PKG@.RbCfg.pkey(u);
  int n = @PKG@.RbStore.n(k);
  Object[] req = @PKG@.RbCheck.reqs(u, world, n);
  if (!Boolean.TRUE.equals(req[2])) return "-Not ready yet - the NO lines on /rebirth say what is missing.";
  java.util.concurrent.ExecutorService e = @PKG@.RbStore.IO;   // fix round: begin's file steps (read, journal + fsync) off the world thread
  if (e != null) {
    try { e.execute(new @PKG@.RbRun(k, 4, u)); return "+The void is imprinting your soul ... (rebirth " + (n + 1) + ")"; } catch (Throwable t) { }
  }
  String r = startNow(k, u);
  return r.startsWith("+") ? "+The void is imprinting your soul ... (rebirth " + (n + 1) + ")" : r;
}""")
# /rebirthadmin rebirth | crashtest <p>: YOUR active profile, class / place / combat checks skipped (works while rebirth is OFF)
M(tx, r"""
public static String adminStart(java.util.UUID u, int halt) {
  String k = @PKG@.RbCfg.pkey(u);
  String r = begin(k, u, "force", halt);
  if (!r.startsWith("+")) return r;
  kick(k);
  return "+Rebirth " + r.substring(1) + " started on " + k + " (admin: class / place / combat checks skipped" + (halt >= 0 ? "; stops after point " + halt + " like a crash" : "") + ").";
}""")
# /rebirthadmin dryrun: every part MEASURES (nothing written anywhere), then the decision it would make
M(tx, r"""
public static java.util.ArrayList dryRun(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  String k = @PKG@.RbCfg.pkey(u);
  @PKG@.RbJ j = new @PKG@.RbJ();
  j.bad = false;
  j.tx = newTx();
  j.k = k;
  j.mode = "live";
  j.parts = @PKG@.RbJournal.PARTS;
  java.util.Properties cur = @PKG@.RbStore.readNow(k);
  j.newN = (cur == null ? 0 : @PKG@.RbStore.num(cur, "n")) + 1;
  out.add("+Dry run for " + k + " (nothing is written): rebirth " + j.newN + " of " + @PKG@.RbCfg.MAX + (@PKG@.RbStore.BUSY.containsKey(k) ? " - BUSY: a rebirth is open on this profile" : ""));
  for (int i = 0; i < j.parts.length; i++) {
    String p = j.parts[i];
    java.util.function.Function f = @PKG@.RbJournal.part(p);
    if (f == null) { out.add("-" + p + ": " + @PKG@.RbJournal.jar(p) + " is not loaded"); continue; }
    Object r;
    try { r = f.apply(new Object[] { "measure", k, j.tx, Integer.valueOf(j.newN), "" }); } catch (Throwable t) { r = "err:" + t; }
    String rs = String.valueOf(r);
    if (rs.startsWith("ok:")) { j.prepared.put(p, rs.substring(3)); out.add("=" + p + ": " + rs.substring(3)); }
    else out.add("-" + p + ": " + rs);
  }
  String[] d = decide(j);
  out.add(("commit".equals(d[0]) ? "+Would commit: " : "-Would abort as a player rebirth: ") + d[1]);
  return out;
}""")
M(tx, r"""
public static java.util.ArrayList status(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  String k = @PKG@.RbCfg.pkey(u);
  java.util.Properties cur = @PKG@.RbStore.readNow(k);
  int n = cur == null ? 0 : @PKG@.RbStore.num(cur, "n");
  StringBuilder pts = new StringBuilder();
  for (int i = 0; i < @PKG@.RbMath.ARMS.length; i++) {
    int p = cur == null ? 0 : @PKG@.RbStore.num(cur, "pts." + @PKG@.RbMath.ARMS[i]);
    if (p > 0) { if (pts.length() > 0) pts.append(", "); pts.append(@PKG@.RbMath.ARMS[i]).append(' ').append(p); }
  }
  out.add("=Profile " + k + ": rebirths " + n + " of " + @PKG@.RbCfg.MAX + (cur == null ? " (file unreadable)" : "") + ", points " + (pts.length() > 0 ? pts.toString() : "none") + ", last " + (cur == null ? "-" : cur.getProperty("lastTx", "-")) + "; rebirth is " + (@PKG@.RbCfg.ON ? "ON" : "OFF"));
  Object b = @PKG@.RbStore.BUSY.get(k);
  out.add(b == null ? "=No rebirth is open on this profile." : "-Rebirth " + b + " is OPEN (busy)" + (HALTED.containsKey(k) ? " - " + HALTED.get(k) : "") + (WAIT.containsKey(k) ? " - " + WAIT.get(k) : ""));
  String miss = @PKG@.RbJournal.missing();
  out.add(miss == null ? "=Every part is loaded (" + @PKG@.RbJournal.JARS.length + ")." : "-Not loaded: " + miss);
  Object l = LAST.get(k);
  if (l != null) out.add("=Last: " + l);
  return out;
}""")
# /rebirthadmin backups: the per-mod backup folders of YOUR profile (each mod's rebirth-backup/<pkey>/<txid>/, the last 3 kept)
M(tx, r"""
public static java.util.ArrayList backups(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  String k = @PKG@.RbCfg.pkey(u);
  java.nio.file.Path mods = @PKG@.RbCfg.DIR == null ? null : @PKG@.RbCfg.DIR.getParent();
  String[] ms = new String[] { "Skyy_SkyySkills", "Skyy_SkyyCoins", "Skyy_SkyyBank" };
  for (int i = 0; i < ms.length; i++) {
    java.io.File[] fs = null;
    if (mods != null) fs = mods.resolve(ms[i]).resolve("rebirth-backup").resolve(k).toFile().listFiles();
    StringBuilder sb = new StringBuilder();
    if (fs != null) { java.util.Arrays.sort(fs); for (int x = 0; x < fs.length; x++) { if (sb.length() > 0) sb.append(", "); sb.append(fs[x].getName()); } }
    out.add("=" + ms[i] + "/rebirth-backup/" + k + ": " + (sb.length() > 0 ? sb.toString() : "none"));
  }
  return out;
}""")

# ================= 0.2 RbRun: 0 = drive one fresh rebirth (k), 4 = a player's click (begin + drive, fix round), 1 = recover every open journal (not the crashtest-stopped ones), 2 = every one
# (/rebirthadmin recover), 3 = the 30 s scheduler tick: hand mode 1 to SkyyRebirth-IO when anything is open =================
M(run_, r"""
public void run() {
  try {
    if (this.mode == 0) { @PKG@.RbTx.drive(this.k, true); return; }
    if (this.mode == 4) {   // fix round: the player's click, handed off the world thread - a refusal is told in chat
      String r = @PKG@.RbTx.startNow(this.k, this.u);
      if (r.startsWith("-")) @PKG@.RbTx.tell(String.valueOf(this.u), "[Rebirth] " + r.substring(1), "#ff6b6b");
      return;
    }
    if (this.mode == 3) {
      if (@PKG@.RbStore.BUSY.isEmpty()) return;
      java.util.concurrent.ExecutorService e = @PKG@.RbStore.IO;
      if (e != null) e.execute(new @PKG@.RbRun(null, 1));
      return;
    }
    @PKG@.RbTx.recoverAll(this.mode == 2);
  } catch (Throwable t) {
    @PKG@.RbCfg.warnOnce("run" + this.mode, "a rebirth step failed (logged once): " + t);
    // fix round 2: off FRESH + on the 30 s retry (a throw used to leave the profile busy until a restart)
    if ((this.mode == 0 || this.mode == 4) && this.k != null) @PKG@.RbTx.waitOn(this.k, "internal error: " + t + " - retried every 30 s");
  }
}""")
'''
rep('''# ================= RbUI: the page markup (tools/skyyui.py - vanilla look; inline only; ids SkyyRb..., no underscores) =================''',
    TX + '''
# ================= RbUI: the page markup (tools/skyyui.py - vanilla look; inline only; ids SkyyRb..., no underscores) =================''')

# ================================================================================================ the page: Note dynamic, the Rebirth button
rep('''    "Note": (12, False, 1, ["Hover the Nexus for the full list."]),''',
    '''    "Note": (12, False, 2, ["Hover the Nexus for the full list.", "Resets skills, purse and bank to 0! Press again within 10 s."]),   # fix round 2: the armed warning, 2 lines''')
rep('''                           "NO  Go to your island or hub", "--  Bazaar / AH: later update"]),''',
    '''                           "NO  Go to your island or hub", "--  Bazaar / AH: later update", "NO  Needs SkyySkills 0.4.36+",
                           "NO  Needs SkyyCoins 0.1.7+", "NO  Needs SkyyBank 0.1.11+", "NO  A rebirth is finishing",
                           "NO  A profile switch is running"]),''')
rep('''ap.text(L, P + "Note", "Hover the Nexus for the full list.", "caption", h=ROW_H["Note"])
ap.append((L, SUI.button(P + "Close", "Close", "secondary", w=LW - 24, sound="cancel", anchor={"top": 8})))''',
    '''ap.text(L, P + "Note", J_("this.note", "Hover the Nexus for the full list."), "caption", wrap=True, h=ROW_H["Note"])
# 0.2: the Rebirth button exists ONLY while rebirth.on is true and every requirement is met (this.goOn); else an empty group of its size
GO_W, CL_W = 124, LW - 24 - 124 - 8
ap.append((L, SUI.group(P + "Btns", layout="Left", w=LW - 24, h=SUI.BTN_H, anchor={"top": 8})))
ap.append(("#" + P + "Btns", SUI.choose(J_("this.goOn"), SUI.button(P + "Go", "Rebirth", "destructive", w=GO_W, anchor={"right": 8}),
                                         SUI.group(P + "Go", layout="Left", w=GO_W, h=SUI.BTN_H, anchor={"right": 8}))))
ap.append(("#" + P + "Btns", SUI.button(P + "Close", "Close", "secondary", w=CL_W, sound="cancel")))''')
rep('''          "public String count;", "public String off;", "public String tip;", "public String nexusSt;", "public boolean awake;",
          "public int n;"):''', '''          "public String count;", "public String off;", "public String tip;", "public String nexusSt;", "public boolean awake;",
          "public int n;", "public boolean goOn;", "public String note;", "public long armedAt;", "public String last;"):''')
rep('''  this.tip = @PKG@.RbCheck.tip(this.n, req, gain);
}""".replace("@GOOD@", GOOD).replace("@WARN@", WARN))''', '''  this.tip = @PKG@.RbCheck.tip(this.n, req, gain);
  this.goOn = @PKG@.RbCfg.ON && this.awake;   // 0.2: the button only exists behind the switch, with every requirement met
  this.note = (this.armedAt > 0L && System.currentTimeMillis() - this.armedAt <= 10000L) ? "Resets skills, purse and bank to 0! Press again within 10 s." : "Hover the Nexus for the full list.";   // fix round 2: says what is lost
}""".replace("@GOOD@", GOOD).replace("@WARN@", WARN))''')
rep('''  ev.addEventBinding(@BT@.Activating, "#SkyyRbClose", @EVD@.of("a", "close"));
}""".replace("@PAGE_JAVA@", PAGE_JAVA))
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  if (data == null || this.testMode) return;
  if (data.indexOf("close") >= 0) close();
}""")''', '''  ev.addEventBinding(@BT@.Activating, "#SkyyRbClose", @EVD@.of("a", "close"));
  if (this.goOn) ev.addEventBinding(@BT@.Activating, "#SkyyRbGo", @EVD@.of("a", "rbgo"));   // 0.2: bound only when the button exists
}""".replace("@PAGE_JAVA@", PAGE_JAVA))
# 0.2: the Rebirth button - the first press arms (10 s), the second starts it. "=armed" / "+started" / "-why"
M(page, r"""
public String click(long now, String w) {
  if (!@PKG@.RbCfg.ON) { this.armedAt = 0L; return "-Rebirth is switched off on this server."; }
  if (this.armedAt <= 0L || now - this.armedAt > 10000L) { this.armedAt = now; return "=armed"; }
  if (now - this.armedAt < 800L) return "=armed";   // fix round 2: a double-click (or a duplicated event) is not a confirm
  this.armedAt = 0L;
  return @PKG@.RbTx.playerStart(this.me, w);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  if (data == null) return;
  if (data.indexOf("rbgo") >= 0) {
    String r = click(System.currentTimeMillis(), this.testMode ? this.world : worldOf(st));
    this.last = r;
    if (this.testMode) return;
    if (r.startsWith("+")) { close(); @PKG@.RbTx.tell(String.valueOf(this.me), "[Rebirth] " + r.substring(1), "#E8A93B"); return; }
    if (r.startsWith("-")) @PKG@.RbTx.tell(String.valueOf(this.me), "[Rebirth] " + r.substring(1), "#ff6b6b");
    rebuild();
    return;
  }
  if (this.testMode) return;
  if (data.indexOf("close") >= 0) close();
}""")''')

# the probe print measures markup strings; the 0.2 Rebirth button is a runtime choice (its live look counted)
rep('''_markup_bytes = sum(len(SUI.render(mk_)) for _p, mk_ in ap)''',
    '''_markup_bytes = sum(len(SUI.render(mk_ if isinstance(mk_, str) else mk_.a)) for _p, mk_ in ap)   # 0.2: a choose() counts its live markup''')

# ================================================================================================ /rebirthadmin
rep('''# ================= plugin =================''', '''# ================= 0.2 /rebirthadmin (skyyrebirth.admin; also while rebirth is OFF): status | dryrun | rebirth | crashtest <0-7> | recover |
# backups. rebirth / crashtest change YOUR profile: the same command twice within 10 s. Lines: "+" done, "-" refused, "=" info =================
adm = mk("RbAdmin")
F(adm, "public static final java.util.concurrent.ConcurrentHashMap ASK = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> Object[]{cmd, Long ms}
M(adm, r"""
public static java.util.ArrayList help() {
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("=/rebirthadmin status | dryrun | rebirth | crashtest <0-7> | recover | backups");
  out.add("=rebirth / crashtest reset YOUR active profile's skills (not Exploration), purse and bank - type it twice within 10 s. Points: 0 BEGIN, 1 first PREPARED, 2 all PREPARED, 3 DECIDED, 4 first COMMITTED, 5 all COMMITTED, 6 REBIRTH, 7 DONE.");
  return out;
}""")
M(adm, r"""
public static boolean confirmed(java.util.UUID u, String cmd, long now) {
  Object o = ASK.get(u);
  if (o instanceof Object[]) {
    Object[] a = (Object[]) o;
    if (cmd.equals(a[0]) && now - ((Long) a[1]).longValue() <= 10000L) { ASK.remove(u); return true; }
  }
  ASK.put(u, new Object[] { cmd, Long.valueOf(now) });
  return false;
}""")
M(adm, r"""
public static java.util.ArrayList run(java.util.UUID u, String args, long now) {
  String a = args == null ? "" : args.trim().toLowerCase();
  while (a.indexOf("  ") >= 0) a = a.replace("  ", " ");
  if (a.length() == 0 || a.equals("help")) return help();
  if (a.equals("status")) return @PKG@.RbTx.status(u);
  if (a.equals("dryrun") || a.equals("dry-run") || a.equals("dry")) return @PKG@.RbTx.dryRun(u);
  if (a.equals("backups") || a.equals("backup list")) return @PKG@.RbTx.backups(u);
  java.util.ArrayList out = new java.util.ArrayList();
  if (a.equals("recover")) {
    java.util.concurrent.ExecutorService e = @PKG@.RbStore.IO;
    if (e != null) { e.execute(new @PKG@.RbRun(null, 2)); out.add("+Recovery started for every open rebirth (also crashtest-stopped ones) - /rebirthadmin status in a moment."); }
    else out.add("+Recovered " + @PKG@.RbTx.recoverAll(true) + " open rebirth(s).");
    return out;
  }
  int halt = -1;
  if (a.startsWith("crashtest")) {
    String p = a.substring(9).trim();
    try { halt = Integer.parseInt(p); } catch (Throwable t) { halt = -2; }
    if (halt < 0 || halt > 7) { out.add("-Usage: /rebirthadmin crashtest <0-7>"); out.addAll(help()); return out; }
  } else if (!a.equals("rebirth")) { out.add("-Unknown: " + a); out.addAll(help()); return out; }
  if (!confirmed(u, a, now)) {
    out.add("=This " + (halt >= 0 ? "crash test (stops after point " + halt + ")" : "rebirth") + " resets YOUR active profile's skills (not Exploration), purse and bank (admin: class / place / combat checks skipped). Type the same command again within 10 s to go on.");
    return out;
  }
  out.add(@PKG@.RbTx.adminStart(u, halt));
  return out;
}""")
M(adm, r"""
public static void send(@PR@ pr, java.util.ArrayList lines) {
  for (int i = 0; i < lines.size(); i++) {
    String l = String.valueOf(lines.get(i));
    char c = l.length() > 0 ? l.charAt(0) : ' ';
    String col = c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@");
    pr.sendMessage(@MSG@.raw("[Rebirth] " + (c == '+' || c == '-' || c == '=' ? l.substring(1) : l)).color(col));
  }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@INFO@", INFO))
admv = mk("RbAdminArgsCmd", T["APC"])
F(admv, "public @RA@ argsArg;")
C(admv, r"""
public RbAdminArgsCmd() {
  super("(admin) status | dryrun | rebirth | crashtest <0-7> | recover | backups");
  requirePermission("skyyrebirth.admin");
  this.argsArg = withRequiredArg("args", "status, dryrun, rebirth, crashtest <0-7>, recover or backups", @ATY@.GREEDY_STRING);
}""")
M(admv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.RbAdmin.send(pr, @PKG@.RbAdmin.run(pr.getUuid(), String.valueOf(ctx.get(this.argsArg)), System.currentTimeMillis())); }
  catch (Throwable t) { @PKG@.RbCfg.warn("/rebirthadmin failed: " + t); try { pr.sendMessage(@MSG@.raw("[Rebirth] /rebirthadmin failed - see the server log.").color("#ff6b6b")); } catch (Throwable t2) { } }
}""")
admc = mk("RbAdminCmd", T["APC"])
C(admc, r"""
public RbAdminCmd() {
  super("rebirthadmin", "(admin) Rebirth tests: status | dryrun | rebirth | crashtest <0-7> | recover | backups");
  requirePermission("skyyrebirth.admin");
  addUsageVariant(new @PKG@.RbAdminArgsCmd());
}""")
M(admc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.ArrayList l = @PKG@.RbAdmin.help();
    l.addAll(@PKG@.RbTx.status(pr.getUuid()));
    @PKG@.RbAdmin.send(pr, l);
  } catch (Throwable t) { @PKG@.RbCfg.warn("/rebirthadmin failed: " + t); }
}""")

# ================= plugin =================''')

# ================================================================================================ plugin wiring
rep('''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")''', '''F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.concurrent.ScheduledFuture recov;")   # 0.2: the 30 s recovery tick''')
rep('''  @PKG@.RbStore.DIR = dir.resolve("players");
  @PKG@.RbStore.start();''', '''  @PKG@.RbStore.DIR = dir.resolve("players");
  @PKG@.RbJournal.DIR = dir.resolve("journal");   // 0.2: the two-phase commit journals
  int open = @PKG@.RbTx.startup();
  @PKG@.RbStore.start();''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.RbCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.RbTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  getCommandRegistry().registerCommand(new @PKG@.RbCmd());
  getCommandRegistry().registerCommand(new @PKG@.RbAdminCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.RbTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  this.recov = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.RbRun(null, 3), 10L, 30L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''"OFF: /rebirth for admins only (view; Server Setup - Rebirth switches it on)") + "; NO rebirth button yet (round R3), nothing is ever reset; bridge''',
    '''"OFF: /rebirth for admins only (view + /rebirthadmin tests; Server Setup - Rebirth switches it on)") + "; two-phase commit with " + (@PKG@.RbJournal.missing() == null ? "every part loaded so far" : "parts still loading (" + @PKG@.RbJournal.missing() + ")") + " (skills, coins, bank), " + open + " open rebirth journal(s) at start (recovered 10 s after start, then every 30 s); bridge''')
rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.RbStore.stop(); } catch (Throwable t) { }''', '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { if (this.recov != null) this.recov.cancel(false); } catch (Throwable t) { }
  try { @PKG@.RbStore.stop(); } catch (Throwable t) { }''')
rep('''ALL = [cfg, load, st, mth, fnc, pub, tick, chk, page, cmd, pl]''',
    '''ALL = [cfg, load, st, mth, rbj, jrn, fnc, pub, tick, chk, tel, tx, run_, page, cmd, adm, admv, admc, pl]''')
rep('''View only: no rebirth button yet, nothing is ever reset. Server Setup: Rebirth (admins can view /rebirth while it is off). Zero dependencies; reads SkyySkills 0.4.35+ for levels."''',
    '''0.2: the rebirth itself (OFF by default) - a journaled two-phase commit with SkyySkills 0.4.36+, SkyyCoins 0.1.7+ and SkyyBank 0.1.11+ (skills, purse and bank reset, the bank rate bonus), crash-safe recovery, /rebirthadmin dryrun / crashtest for admins. Server Setup: Rebirth. Zero dependencies."''')

# ================================================================================================ checks
assert s.index("rbj = mk(\"RbJ\")") < s.index("fnc = mk(\"RbFn\"")
assert s.index("public static String missing()") < s.index("public static Object[] reqs(")
assert s.index("tx = mk(\"RbTx\")") > s.index("pub = mk(\"RbPub\")") and s.index("tx = mk(\"RbTx\")") < s.index("page = mk(\"RbPage\"")
_a, _b = S0.split(LF), s.split(LF)
_hunks = [op for op in difflib.SequenceMatcher(None, _a, _b, autojunk=False).get_opcodes() if op[0] != "equal"]
_gone = [(i, _a[i]) for op in _hunks for i in range(op[1], op[2])]
_allowed = set()
for _o in OLDS:
    _allowed.update(_o.split(LF))
_bad = [(i, ln) for i, ln in _gone if ln not in _allowed and not any(_o in ln for _o in OLDS if LF not in _o)]
assert not _bad, "0.1 lines changed outside the planned places: %r" % _bad[:5]
compile(s, dst, "exec")
open(dst, "wb").write(s.replace(LF, NL).encode("utf8"))
print("wrote", dst, len(s), "chars;", len(_hunks), "diff hunks vs 0.1,", len(_gone), "0.1 lines replaced;", len(OLDS), "anchors")
