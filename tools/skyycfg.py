"""skyycfg - the admin config-registry kit every Skyy mod copies into its own jar (research/Server-Setup-Spec.md 1.3-1.4, 6).

Contract for other mods and for SkyyMenu 0.3: tools/CONFIG-CONTRACT.md. Test harness: python tools/skyycfg_test.py (bare JVM, spec 8.2).

KIT 1.1 (2026-09-25, the round-4 builders' gaps; bridge contract "1", file, log, history and export formats unchanged, so the 18 jars
built with 1.0 keep working next to jars built with 1.1; each adopter picks 1.1 up at its own next version):
  1. CfgFile.handApply: a hand-edited TABLE line is checked like an in-game change (entry key, column count / types / bounds, the row's
     check= hook with tableKey[entry] and the canonical columns, or null for a removed line). A refused line is logged `invalid`, memory
     keeps the old value (held until that entry changes again in game or by hand, or the next start), its reload routine is not run for
     it, and the file keeps the hand-typed line (a hand edit is never lost). The check= hooks run outside every kit lock: after the
     locked part of a save (CfgSaveTask.saveLocked -> CfgFn.handChecks), and between merge and apply on the reload op's own thread.
     Concurrency: merge and the kit's own line checks are one monitor hold (CfgFile.mergeApply); a line waiting for its check= hook is
     held like a refused one until the hook accepts it, and only the entry's newest change may apply (CfgFile.HCHK), so a slow hook
     answering about an older line never puts a value in memory that did not pass; the reload op reads + merges under the save
     monitor (CfgSaveTask.readMerge), so it never merges a file a save is writing (that stale merge could drop the in-game change
     being written from memory and let a later save write the older lines back); op keys leaves out a key-family entry removed while
     it lists (test Q6 + its stress phase).
  2. A 1-column table no longer splits a value on '|' (the whole value is the one column, written to the file as is, never through
     sep=), and a table without int/dec columns takes its text length from the row max (1-2000, build-checked; 200 when no max) and
     takes no min (build-checked: it would have no effect).
  3. A custom: row or custom table whose customSet hands back file lines queues the mod's RELOAD after the write, like a reload: row
     (not for a restart row or a "restart" answer). Before any reload routine runs, the mod's other files with unsaved in-game changes
     are written; a file that still cannot be written (a failed write) or that another thread saves while the routine runs is read
     stale by the routine, so those in-game field: values are set again after the routines (CfgSaveTask.quiet + CfgFile.reassert)
     and no false clamp is logged.
  4. CfgFile.wants() also answers true for a pending reload request with no changed line, so a lone CfgFile.addReloads(...) runs.
  5. Action rows may take a typed value: binding option value=int|dec|text|bool|range|color. The row publishes Object[12] (element 11 =
     the value type; every other row keeps Object[11]), op action takes the value after via, validated against the row's min / max /
     unit (a missing value = the row default, published at element 4, or `bad` when there is none), check= gets (key, value), the
     method is static Object[] m(UUID who, String name, String value), and the log line carries the value in its old column.

Why a code generator: every mod has its own classloader and there is no javac, so shared code cannot be a library jar. A build script
imports this module and gets the same seven classes, in its own package, compiled by javassist. The build script only adds DATA: its rows
and how each row binds to the mod's own fields, files and reload routine.

    import skyycfg as CFG
    CATS = [("parts", "Parts"), ("bank", "Bank")]
    ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
      ("bank.interestPercent", "Interest per payout", "bank", "int", "2", "0", "100", "step=1", "%", "live,danger",
       "Percent of the bank balance paid each payout.", "field:BankCfg.PERCENT@Skyy_SkyyBank/config.properties:interestPercent"),
    ]
    kit = CFG.emit(pool, PKG, MOD="SkyyEconomy", TITLE="Economy", VERSION=VERSION, NODE="skyyeconomy.admin", CATS=CATS, ROWS=ROWS,
                   FILES=["Skyy_SkyyBank/config.properties"], RELOAD="EcoCfg.reloadAll", DEFAULTS={"Skyy_SkyyBank/config.properties": text})
    ... compile the rest of the mod (it may call PKG.CfgPub / PKG.CfgFn directly) ...
    kit.write(OUT)                   # runs the deferred build checks, then writeFile for the kit classes
    # plugin setup(), AFTER the mod's own config load:  PKG.CfgPub.start(getDataDirectory().getParent(), getLogger());
    # plugin shutdown():                                 PKG.CfgPub.shutdown();
    # admin commands:                                    String msg = PKG.CfgFn.cmdSet(key, typedValue, uuid, username);
    # ... the command's explicit console branch only:   String msg = PKG.CfgFn.cmdSetConsole(key, typedValue);

The config class and its bound fields must exist in the pool BEFORE emit() (the field types are read at build time). Hook methods
(reload routines, custom:, action:, after=, check=) are called by reflection, so they may be compiled before or after emit();
kit.write() checks them all.

Binding grammar (row element 11):
    field:<Class>.<FIELD>[*<scale>][@<file>[:<fileKey>]]     public static volatile int/long/double/boolean/String field
    reload[:<Class>.<method>][@<file>[:<fileKey>]]           file line only; the routine (default RELOAD) runs after the write
    custom:<Class>[@<file>[:<k1>,<k2>]]                     Class.customGet(String) / customSet(String,String) [/ customRead / customKeys]
    action:<Class>.<method>                                  static Object[] method(java.util.UUID who, String name) -> R
                                                             (with value=: method(java.util.UUID who, String name, String value))
    none | ""                                                link rows
  options, appended with ';':  after=<Class>.<m>   check=<Class>.<m>   confirm=on|off|up|down|always|never   sep=<c>
                               entry=key|item|itemprefix   value=int|dec|text|bool|range|color (action rows, kit 1.1)
    check= works on scalar, table (key tableKey[entry], value null = remove; also run on hand-edited lines) and action rows (key, value
    null, or the canonical typed value for a value= action).
    confirm= needs the danger flag and refines when that row asks: on/off bool rows, up/down int/dec rows, always/never any row
    (tables and actions: always/never only).
  <Class> is a simple name in PKG or a full name. <file> is a path under the world's mods/ folder, or the unique end of one FILES entry.
  Default file = FILES[0] (a custom: row must name its file when there are several FILES); default fileKey = the row key; a table's
  default fileKey (its prefix) = the row key + ".". One row per file key; table prefixes in one file never overlap each other or a
  scalar key.
  Table rows bind reload@<file>:<prefix> (a key family: every line <prefix><entry>=<col1><sep><col2>...) or custom:.
  A restart row (or table) never runs its reload routine on a change: the file waits for the next start.
"""
import os, re, zipfile
from decimal import Decimal, InvalidOperation

CONTRACT = "1"
KIT_VERSION = "1.1"
TYPES = ("bool", "int", "dec", "text", "choice", "items", "range", "table", "link", "action", "color")
ACTION_VALUE_TYPES = ("int", "dec", "text", "bool", "range", "color")   # value=<type> on an action row (kit 1.1); no opts-based types
TABLE_TEXT_MAX = 2000   # a table without int/dec columns takes its text length from the row max, up to this (kit 1.1)
SCALAR = ("bool", "int", "dec", "text", "choice", "items", "range", "color")
FLAGS = ("live", "restart", "new", "danger", "part", "adv", "ro")
UNITS = ("%", "coins", "h", "min", "s", "ms", "blocks", "x", "")
MS_UNIT_SCALE = {"ms": 1, "s": 1000, "min": 60000, "h": 3600000}
KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]{0,79}$")
CAT_RE = re.compile(r"^[a-z][a-zA-Z0-9]{0,15}$")
MOD_RE = re.compile(r"^Skyy[A-Z][A-Za-z]{1,30}$")
NODE_RE = re.compile(r"^[a-z][a-z0-9_-]*(\.[a-z0-9_*-]+)+$")
# a millisecond field: FOO_MS / MS, fooMs, *MILLIS / *Millis. A bare trailing "MS" after a letter (MAX_ITEMS, DEFAULT_TEAMS) is a plural, not ms
MS_FIELD_RE = re.compile(r"(?:(?:^|_)MS|(?<=[a-z0-9])Ms|MILLIS|Millis)$")
ITEM_RE = re.compile(r"^[A-Za-z0-9_.-]{1,120}$")
CHOICE_LABEL_MAX = 20   # spec 2.5: one 100 px button per value (<= 4 values) or the 220 px cycling label; category tabs use 20 in 126 px
INT_MIN, INT_MAX = -(2 ** 31), 2 ** 31 - 1
LONG_MIN, LONG_MAX = -(2 ** 63), 2 ** 63 - 1
CONF = {"": 0, "on": 1, "off": 2, "up": 3, "down": 4, "always": 5, "never": 6}
ENTRY = {"key": 0, "item": 1, "itemprefix": 2}
FTYPE = {"int": 1, "long": 2, "double": 3, "boolean": 4, "java.lang.String": 5}
FIELD_OK = {"bool": (1, 2, 4, 5), "int": (1, 2, 5), "dec": (3, 5), "text": (5,), "choice": (5,), "items": (5,), "range": (5,), "color": (5,)}
HEADER_LINE = "# ---- changed in game (SkyWynn Menu) ----"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOGC = "com.hypixel.hytale.logger.HytaleLogger"
PERM_DEFAULT = "com.hypixel.hytale.server.core.permissions.PermissionsModule.get().hasPermission(who, NODE)"
ITEM_DEFAULT = "com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id) != null"
CLASS_NAMES = ("CfgRows", "CfgLog", "CfgHist", "CfgSaveTask", "CfgFile", "CfgFn", "CfgPub")


class CfgError(SystemExit):
    """A build check failed (SystemExit so a build script stops with the message, like skyybuild.probe)."""


def _fail(msg):
    raise CfgError("skyycfg: " + msg)


# ================================================================================================================ python-side checks
def _dec(s):
    try:
        d = Decimal(s)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return d if d.is_finite() else None


def _plain(d):
    if d == 0:
        return "0"
    t = format(d.normalize(), "f")
    return t


def _num(text, unit=""):
    """Python mirror of CfgRows.num: '2k', '1.5m', '1,000', '90s', '3%' -> Decimal or None."""
    t = str(text).strip().lower()
    if not t or len(t) > 60:
        return None
    t = "".join(c for c in t if c not in ", _")
    u = unit.lower()
    if u and t.endswith(u) and len(t) > len(u):
        t = t[:-len(u)]
    if t.endswith("%") and len(t) > 1:
        t = t[:-1]
    mul = {"k": 1000, "m": 10 ** 6, "b": 10 ** 9, "t": 10 ** 12}.get(t[-1:], 1) if t else 1
    if mul != 1:
        t = t[:-1]
    if not t or any(not (c.isdigit() or c == "." or (i == 0 and c in "+-")) for i, c in enumerate(t)):
        return None
    d = _dec(t)
    return None if d is None else d * mul


def _choices(opts):
    vals, labs = [], []
    for part in opts.split(","):
        v, _, l = part.partition("|")
        vals.append(v.strip())
        labs.append((l or v).strip())
    return vals, labs


def _cols(opts):
    p = opts.split(";")
    return p[2].split("|") if len(p) >= 3 else ["Value"]


def py_validate(row, text, items=None):
    """Mirror of CfgRows.validate for build checks. Returns (canonical, None) or (None, why)."""
    t, lo, hi, opts, unit = row["type"], row["min"], row["max"], row["opts"], row["unit"]
    s = text
    if t == "bool":
        v = s.strip().lower()
        if v in ("true", "on", "yes", "1"):
            return "true", None
        if v in ("false", "off", "no", "0"):
            return "false", None
        return None, "not ON/OFF"
    if t in ("int", "dec"):
        d = _num(s, unit)
        if d is None:
            return None, "not a number"
        if t == "int" and d != d.to_integral_value():
            return None, "not a whole number"
        if (lo and d < Decimal(lo)) or (hi and d > Decimal(hi)):
            return None, "out of range %s..%s" % (lo, hi)
        return (str(int(d)) if t == "int" else _plain(d)), None
    if t == "text":
        v = s.strip()
        if "\n" in v or "\r" in v:
            return None, "more than one line"
        if (lo and len(v) < int(lo)) or len(v) > (int(hi) if hi else 2000):
            return None, "length out of range"
        return v, None
    if t == "color":
        v = s.strip().lower()
        return (v, None) if re.match(r"^#[0-9a-f]{6}$", v) else (None, "not #rrggbb")
    if t == "choice":
        vals, labs = _choices(opts)
        for v, l in zip(vals, labs):
            if s.strip().lower() in (v.lower(), l.lower()):
                return v, None
        return None, "not one of %s" % vals
    if t == "range":
        x = s.strip().lower().replace(" ", "").replace("%", "")
        if unit:
            x = x.replace(unit.lower(), "")
        if not x or x.startswith("-"):
            return None, "not a range"
        a, _, b = x.partition("-")
        b = b or a
        da, db = _num(a), _num(b)
        if da is None or db is None or da > db:
            return None, "not a range"
        for d in (da, db):
            if (lo and d < Decimal(lo)) or (hi and d > Decimal(hi)):
                return None, "out of range"
        return (_plain(da) if da == db else _plain(da) + "-" + _plain(db)), None
    if t == "items":
        toks = [x for x in opts.split(",") if x]
        out, seen = [], set()
        for e in [x.strip() for x in s.split(",") if x.strip()]:
            iid, q = e, 1
            if "qty" in toks:
                if ":" in e:
                    iid, _, qs = e.rpartition(":")
                    if not qs.strip().isdigit():
                        return None, "bad amount in " + e
                    q = int(qs)
                if not 1 <= q <= 9999:
                    return None, "amount out of 1..9999 in " + e
            elif ":" in e:
                return None, "amounts not allowed: " + e
            iid = iid.strip()
            if iid.endswith("*"):
                if "prefix" not in toks or len(iid) == 1:
                    return None, "* not allowed: " + iid
            elif not ITEM_RE.match(iid) or (items is not None and iid not in items):
                return None, "unknown item " + iid
            if iid in seen:
                return None, "listed twice: " + iid
            seen.add(iid)
            out.append("%s:%d" % (iid, q) if "qty" in toks else iid)
        if (lo and len(out) < int(lo)) or (hi and len(out) > int(hi)):
            return None, "entry count out of range"
        return ",".join(out), None
    return None, "type %s has no value" % t


def parse_props(text):
    """Minimal java.util.Properties reader (last key wins) for the build checks and table defaults."""
    out = {}
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        s = lines[i].lstrip(" \t\f")
        if not s or s[0] in "#!":
            i += 1
            continue
        logical = s
        while _cont(logical) and i + 1 < len(lines):
            logical = logical[:-1] + lines[i + 1].lstrip(" \t\f")
            i += 1
        if _cont(logical):
            logical = logical[:-1]
        k, j = [], 0
        while j < len(logical):
            c = logical[j]
            if c == "\\" and j + 1 < len(logical):
                k.append(logical[j:j + 2]); j += 2; continue
            if c in "=: \t\f":
                break
            k.append(c); j += 1
        while j < len(logical) and logical[j] in " \t\f":
            j += 1
        if j < len(logical) and logical[j] in "=:":
            j += 1
            while j < len(logical) and logical[j] in " \t\f":
                j += 1
        out[_unesc("".join(k))] = _unesc(logical[j:])
        i += 1
    return out


def _cont(s):
    n = len(s) - len(s.rstrip("\\"))
    return n % 2 == 1


def _unesc(s):
    if "\\" not in s:
        return s
    o, i = [], 0
    while i < len(s):
        c = s[i]
        if c != "\\" or i + 1 >= len(s):
            if c != "\\":
                o.append(c)
            i += 1
            continue
        n = s[i + 1]
        if n == "u" and i + 5 < len(s) + 0 and re.match(r"^[0-9a-fA-F]{4}$", s[i + 2:i + 6] or ""):
            o.append(chr(int(s[i + 2:i + 6], 16))); i += 6; continue
        o.append({"t": "\t", "n": "\n", "r": "\r", "f": "\f"}.get(n, n)); i += 2
    return "".join(o)


def _jstr(s):
    if any((ord(c) < 32 and c != "\t") or ord(c) > 126 for c in s):
        _fail("text must be plain ASCII without control characters (javassist literal): %r" % s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\t", "\\t") + '"'


def _jarr(xs):
    return "new String[] { " + ", ".join(_jstr(x) for x in xs) + " }" if xs else "new String[0]"


def _jints(xs):
    return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }" if xs else "new int[0]"


def _jlongs(xs):
    return "new long[] { " + ", ".join("%dL" % int(x) for x in xs) + " }" if xs else "new long[0]"


def _items_from_assets():
    try:
        import skyybuild as B
        z = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
        return set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    except Exception:
        return None


# ================================================================================================================ Java: CfgRows
ROWS_JAVA = [
r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""",
r"""
public static void say(boolean warn, String msg) {
  String m = "[" + MOD + "] " + msg;
  try {
    if (LOG != null) {
      if (warn) LOG.at(java.util.logging.Level.WARNING).log(m); else LOG.at(java.util.logging.Level.INFO).log(m);
    } else if (warn) System.err.println(m); else System.out.println(m);
  } catch (Throwable t) { }
  if (warn) WARNS = WARNS + 1L;
}""",
r"""public static void warn(String m) { say(true, m); }""",
r"""public static void info(String m) { say(false, m); }""",
r"""
public static int index(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}""",
r"""public static boolean flag(int i, String f) { return ("," + FLAGS[i] + ",").indexOf("," + f + ",") >= 0; }""",
r"""public static boolean opt(int i, String t) { return ("," + OPTS[i] + ",").indexOf("," + t + ",") >= 0; }""",
r"""
public static String clip(String s, int n) {
  if (s == null) return "";
  if (s.length() <= n) return s;
  if (n <= 3) return s.substring(0, n);
  return s.substring(0, n - 3) + "...";
}""",
r"""
public static String oneLine(String s) {
  if (s == null) return "";
  return s.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ');
}""",
r"""public static boolean isTable(int i) { return TYPES[i].equals("table"); }""",
# a table with one named column (no '|' after the last ';' of its opts): its value is never split on '|' (kit 1.1)
r"""public static boolean oneCol(int i) { return OPTS[i].indexOf('|', OPTS[i].lastIndexOf(';') + 1) < 0; }""",
r"""public static boolean noValue(int i) { return TYPES[i].equals("table") || TYPES[i].equals("link") || TYPES[i].equals("action"); }""",
r"""
public static String[] ok(String v) { return new String[] { v, null }; }""",
r"""
public static String[] no(String e) { return new String[] { null, e }; }""",
r"""
public static java.math.BigDecimal num(int i, String s) {
  if (s == null) return null;
  String t = s.trim().toLowerCase();
  if (t.length() == 0 || t.length() > 60) return null;
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < t.length(); k++) { char c = t.charAt(k); if (c != ',' && c != '_' && c != ' ') sb.append(c); }
  t = sb.toString();
  String u = "";
  if (i >= 0) u = UNITS[i].toLowerCase();
  if (u.length() > 0 && t.endsWith(u) && t.length() > u.length()) t = t.substring(0, t.length() - u.length());
  if (t.endsWith("%") && t.length() > 1) t = t.substring(0, t.length() - 1);
  long mul = 1L;
  if (t.length() > 0) {
    char last = t.charAt(t.length() - 1);
    if (last == 'k') mul = 1000L; else if (last == 'm') mul = 1000000L; else if (last == 'b') mul = 1000000000L; else if (last == 't') mul = 1000000000000L;
  }
  if (mul != 1L) t = t.substring(0, t.length() - 1);
  if (t.length() == 0) return null;
  for (int k = 0; k < t.length(); k++) {
    char c = t.charAt(k);
    if (!(c >= '0' && c <= '9') && c != '.' && !(k == 0 && (c == '-' || c == '+'))) return null;
  }
  try { return new java.math.BigDecimal(t).multiply(java.math.BigDecimal.valueOf(mul)); } catch (Throwable e) { return null; }
}""",
r"""
public static java.math.BigDecimal bnd(String s) {
  if (s == null || s.length() == 0) return null;
  try { return new java.math.BigDecimal(s); } catch (Throwable t) { return null; }
}""",
r"""
public static String canonDec(java.math.BigDecimal d) {
  if (d.signum() == 0) return "0";
  return d.stripTrailingZeros().toPlainString();
}""",
r"""public static boolean isInt(java.math.BigDecimal d) { return d.signum() == 0 || d.stripTrailingZeros().scale() <= 0; }""",
r"""
public static boolean inb(int i, java.math.BigDecimal v) {
  java.math.BigDecimal lo = bnd(MINS[i]);
  java.math.BigDecimal hi = bnd(MAXS[i]);
  if (lo != null && v.compareTo(lo) < 0) return false;
  if (hi != null && v.compareTo(hi) > 0) return false;
  return true;
}""",
r"""
public static String boundsText(int i) {
  String lo = MINS[i];
  String hi = MAXS[i];
  String u = UNITS[i];
  String us = "";
  if (u.equals("%")) us = "%"; else if (u.length() > 0) us = " " + u;
  if (lo.length() > 0 && hi.length() > 0) return " from " + lo + " to " + hi + us;
  if (lo.length() > 0) return " of at least " + lo + us;
  if (hi.length() > 0) return " of at most " + hi + us;
  return "";
}""",
r"""public static String rangeText(int i, String what) { return "Must be " + what + boundsText(i) + "."; }""",
r"""
public static boolean idChars(String id) {
  if (id == null || id.length() == 0 || id.length() > 120) return false;
  for (int k = 0; k < id.length(); k++) {
    char c = id.charAt(k);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-' || c == '.')) return false;
  }
  return true;
}""",
r"""
public static boolean itemOk(String id) {
  if (!idChars(id)) return false;
  try { return @ITEMCHECK@; } catch (Throwable t) { return false; }
}""",
r"""
public static String[] chVals(int i) {
  String[] p = OPTS[i].split(",");
  String[] r = new String[p.length];
  for (int k = 0; k < p.length; k++) { int b = p[k].indexOf('|'); if (b < 0) r[k] = p[k].trim(); else r[k] = p[k].substring(0, b).trim(); }
  return r;
}""",
r"""
public static String[] chLabels(int i) {
  String[] p = OPTS[i].split(",");
  String[] r = new String[p.length];
  for (int k = 0; k < p.length; k++) { int b = p[k].indexOf('|'); if (b < 0) r[k] = p[k].trim(); else r[k] = p[k].substring(b + 1).trim(); }
  return r;
}""",
# t = the row type, or a value= action's value type (kit 1.1: same rules, the row's min / max / unit)
r"""
public static String[] validateAs(int i, String t, String s) {
  if (s == null) return no("No value given.");
  if (s.length() > 20000) return no("That value is too long.");
  if (t.equals("bool")) {
    String v = s.trim().toLowerCase();
    if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return ok("true");
    if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return ok("false");
    return no("Must be ON or OFF (true or false).");
  }
  if (t.equals("int")) {
    java.math.BigDecimal n = num(i, s);
    if (n == null || !isInt(n)) return no(rangeText(i, "a whole number"));
    if (n.compareTo(java.math.BigDecimal.valueOf(Long.MAX_VALUE)) > 0 || n.compareTo(java.math.BigDecimal.valueOf(Long.MIN_VALUE)) < 0) return no(rangeText(i, "a whole number"));
    if (!inb(i, n)) return no(rangeText(i, "a whole number"));
    return ok(n.toBigInteger().toString());
  }
  if (t.equals("dec")) {
    java.math.BigDecimal n = num(i, s);
    if (n == null || !inb(i, n)) return no(rangeText(i, "a number"));
    return ok(canonDec(n));
  }
  if (t.equals("text")) {
    String v = s.trim();
    if (v.indexOf('\n') >= 0 || v.indexOf('\r') >= 0) return no("Must be one line.");
    int lo = 0;
    int hi = 2000;
    if (MINS[i].length() > 0) lo = Integer.parseInt(MINS[i]);
    if (MAXS[i].length() > 0) hi = Integer.parseInt(MAXS[i]);
    if (v.length() < lo || v.length() > hi) return no("Must be " + lo + " to " + hi + " characters long.");
    return ok(v);
  }
  if (t.equals("color")) {
    String v = s.trim().toLowerCase();
    boolean good = v.length() == 7 && v.charAt(0) == '#';
    for (int k = 1; good && k < 7; k++) { char c = v.charAt(k); if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) good = false; }
    if (!good) return no("Must be a colour like #ffcc00.");
    return ok(v);
  }
  if (t.equals("choice")) {
    String[] vs = chVals(i);
    String[] ls = chLabels(i);
    String v = s.trim();
    for (int k = 0; k < vs.length; k++) if (vs[k].equalsIgnoreCase(v) || ls[k].equalsIgnoreCase(v)) return ok(vs[k]);
    StringBuilder sb = new StringBuilder("Must be one of: ");
    for (int k = 0; k < ls.length; k++) { if (k > 0) sb.append(", "); sb.append(ls[k]); }
    return no(sb.append(".").toString());
  }
  if (t.equals("range")) {
    String x = s.trim().toLowerCase().replace(" ", "").replace("%", "");
    String u = UNITS[i].toLowerCase();
    if (u.length() > 0) x = x.replace(u, "");
    String msg = "Must be a range like 5-10, or one number" + boundsText(i) + ".";
    if (x.length() == 0 || x.startsWith("-")) return no(msg);
    int d = x.indexOf('-');
    String a = x;
    String b = x;
    if (d >= 0) { a = x.substring(0, d); b = x.substring(d + 1); }
    java.math.BigDecimal lo = num(-1, a);
    java.math.BigDecimal hi = num(-1, b);
    if (lo == null || hi == null) return no(msg);
    if (lo.compareTo(hi) > 0) return no("The first number must not be above the second.");
    if (!inb(i, lo) || !inb(i, hi)) return no(msg);
    if (lo.compareTo(hi) == 0) return ok(canonDec(lo));
    return ok(canonDec(lo) + "-" + canonDec(hi));
  }
  if (t.equals("items")) {
    String[] parts = s.split(",");
    java.util.ArrayList out = new java.util.ArrayList();
    java.util.HashSet seen = new java.util.HashSet();
    boolean qty = opt(i, "qty");
    boolean pre = opt(i, "prefix");
    for (int k = 0; k < parts.length; k++) {
      String e = parts[k].trim();
      if (e.length() == 0) continue;
      String id = e;
      long q = 1L;
      if (qty) {
        int c = e.lastIndexOf(':');
        if (c >= 0) {
          id = e.substring(0, c).trim();
          try { q = Long.parseLong(e.substring(c + 1).trim()); } catch (Throwable x) { return no("The amount for " + id + " must be a whole number from 1 to 9999."); }
        }
        if (q < 1L || q > 9999L) return no("The amount for " + id + " must be a whole number from 1 to 9999.");
      } else if (e.indexOf(':') >= 0) return no("No amounts in this list: " + e + ".");
      if (id.endsWith("*")) {
        if (!pre) return no("No * in this list: " + id + ".");
        String base = id.substring(0, id.length() - 1);
        if (base.length() == 0) return no("A lone * would match every item.");
        if (!idChars(base)) return no("Not an item id: " + id + ".");
      } else if (!itemOk(id)) return no("Unknown item: " + id + ".");
      if (!seen.add(id)) return no(id + " is listed twice.");
      if (qty) out.add(id + ":" + q); else out.add(id);
    }
    int lo = 0;
    int hi = 100000;
    if (MINS[i].length() > 0) lo = Integer.parseInt(MINS[i]);
    if (MAXS[i].length() > 0) hi = Integer.parseInt(MAXS[i]);
    if (out.size() < lo || out.size() > hi) return no("Must list " + lo + " to " + hi + " items.");
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < out.size(); k++) { if (k > 0) sb.append(','); sb.append((String) out.get(k)); }
    return ok(sb.toString());
  }
  return no("This row has no single value.");
}""",
r"""public static String[] validate(int i, String s) { return validateAs(i, TYPES[i], s); }""",
r"""
public static boolean same(int i, String a, String b) {
  if (a == null || b == null) return a == b;
  if (a.equals(b)) return true;
  String[] x = validate(i, a);
  String[] y = validate(i, b);
  if (x[0] == null || y[0] == null) return false;
  if (TYPES[i].equals("dec")) { try { return new java.math.BigDecimal(x[0]).compareTo(new java.math.BigDecimal(y[0])) == 0; } catch (Throwable t) { return false; } }
  return x[0].equals(y[0]);
}""",
r"""
public static String dispAs(int i, String t, String v) {
  if (v == null) return "(unknown)";
  if (t.equals("bool")) { if (v.equals("true")) return "ON"; if (v.equals("false")) return "OFF"; return v; }
  if (v.length() == 0) return "(empty)";
  String u = UNITS[i];
  if (u.length() == 0) return v;
  if (u.equals("%")) { if (t.equals("range")) return v.replace("-", "%-") + "%"; return v + "%"; }
  return v + " " + u;
}""",
r"""public static String disp(int i, String v) { return dispAs(i, TYPES[i], v); }""",
r"""
public static String fileText(int i, String canon) {
  if (TYPES[i].equals("bool") && opt(i, "01")) { if (canon.equals("true")) return "1"; return "0"; }
  return canon;
}""",
r"""
public static String fromFile(int i, String raw) {
  if (raw == null) { String[] d = validate(i, DEFS[i]); if (d[0] != null) return d[0]; return DEFS[i]; }
  if (TYPES[i].equals("bool") && opt(i, "01")) { if (raw.trim().equals("0")) return "false"; return "true"; }
  String[] v = validate(i, raw);
  if (v[0] != null) return v[0];
  return raw.trim();
}""",
r"""public static Class cls(String n) throws Exception { return Class.forName(n, true, @PKG@.CfgRows.class.getClassLoader()); }""",
r"""
public static java.lang.reflect.Field fld(int i) throws Exception {
  java.lang.reflect.Field f = FLD[i];
  if (f == null) { f = cls(BCLS[i]).getField(BNAME[i]); FLD[i] = f; }
  return f;
}""",
r"""
public static java.lang.reflect.Method mth(String spec, Class[] sig) throws Exception {
  String key = spec + "/" + sig.length;
  Object m = MCACHE.get(key);
  if (m != null) return (java.lang.reflect.Method) m;
  int d = spec.lastIndexOf('.');
  java.lang.reflect.Method r = cls(spec.substring(0, d)).getMethod(spec.substring(d + 1), sig);
  MCACHE.put(key, r);
  return r;
}""",
r"""
public static boolean hasMth(String spec, Class[] sig) {
  try { return mth(spec, sig) != null; } catch (Throwable t) { return false; }
}""",
r"""
public static Object call(String spec, Class[] sig, Object[] args) throws Throwable {
  try { return mth(spec, sig).invoke(null, args); }
  catch (java.lang.reflect.InvocationTargetException e) { Throwable c = e.getCause(); if (c != null) throw c; throw e; }
}""",
r"""
public static String fieldGet(int i) throws Exception {
  java.lang.reflect.Field f = fld(i);
  int ft = BFT[i];
  long sc = BSC[i];
  if (ft == 5) { Object o = f.get(null); if (o == null) return ""; return o.toString(); }
  if (ft == 4) { if (f.getBoolean(null)) return "true"; return "false"; }
  long v = 0L;
  if (ft == 3) {
    double d = f.getDouble(null);
    java.math.BigDecimal b = null;
    try { b = java.math.BigDecimal.valueOf(d); } catch (Throwable x) { return String.valueOf(d); }
    if (sc != 1L) b = b.divide(java.math.BigDecimal.valueOf(sc), 9, java.math.RoundingMode.HALF_UP);
    return canonDec(b);
  }
  if (ft == 1) v = (long) f.getInt(null); else v = f.getLong(null);
  if (TYPES[i].equals("bool")) { if (v != 0L) return "true"; return "false"; }
  if (sc == 1L) return String.valueOf(v);
  if (v % sc == 0L) return String.valueOf(v / sc);
  return canonDec(java.math.BigDecimal.valueOf(v).divide(java.math.BigDecimal.valueOf(sc), 9, java.math.RoundingMode.HALF_UP));
}""",
r"""
public static void fieldSet(int i, String canon) throws Exception {
  java.lang.reflect.Field f = fld(i);
  int ft = BFT[i];
  if (ft == 5) { f.set(null, canon); return; }
  if (TYPES[i].equals("bool")) {
    boolean b = canon.equals("true");
    if (ft == 4) f.setBoolean(null, b); else if (ft == 1) { if (b) f.setInt(null, 1); else f.setInt(null, 0); } else { if (b) f.setLong(null, 1L); else f.setLong(null, 0L); }
    return;
  }
  java.math.BigDecimal v = new java.math.BigDecimal(canon).multiply(java.math.BigDecimal.valueOf(BSC[i]));
  if (ft == 3) { f.setDouble(null, v.doubleValue()); return; }
  long l = v.setScale(0, java.math.RoundingMode.HALF_UP).longValue();
  if (ft == 1) f.setInt(null, (int) l); else f.setLong(null, l);
}""",
# file value -> field for field rows when the mod has no reload routine: clamp like a mod's own load() (spec 1.4.2)
r"""
public static String fileApply(int i, String raw) {
  try {
    String v = raw;
    if (v == null) v = DEFS[i];
    if (TYPES[i].equals("bool") && opt(i, "01")) { if (v.trim().equals("0")) v = "false"; else v = "true"; }
    String[] r = validate(i, v);
    if (r[0] != null) { fieldSet(i, r[0]); return "ok"; }
    if (TYPES[i].equals("int") || TYPES[i].equals("dec")) {
      java.math.BigDecimal n = num(i, v);
      if (n != null) {
        java.math.BigDecimal lo = bnd(MINS[i]);
        java.math.BigDecimal hi = bnd(MAXS[i]);
        if (lo != null && n.compareTo(lo) < 0) n = lo;
        if (hi != null && n.compareTo(hi) > 0) n = hi;
        String c = null;
        if (TYPES[i].equals("int")) c = n.setScale(0, java.math.RoundingMode.HALF_UP).toBigInteger().toString(); else c = canonDec(n);
        fieldSet(i, c);
        return "clamped";
      }
    }
    return "invalid";
  } catch (Throwable t) { return "invalid"; }
}""",
r"""
public static Object[] header() {
  Object[] rows = new Object[KEYS.length];
  for (int i = 0; i < KEYS.length; i++) {
    if (VTYPES[i].length() == 0) rows[i] = new Object[] { KEYS[i], LABELS[i], CATS[i], TYPES[i], DEFS[i], MINS[i], MAXS[i], OPTS[i], UNITS[i], FLAGS[i], HELPS[i] };
    else rows[i] = new Object[] { KEYS[i], LABELS[i], CATS[i], TYPES[i], DEFS[i], MINS[i], MAXS[i], OPTS[i], UNITS[i], FLAGS[i], HELPS[i], VTYPES[i] };
  }
  String[] ci = new String[CAT_IDS.length];
  String[] cl = new String[CAT_LABELS.length];
  System.arraycopy(CAT_IDS, 0, ci, 0, ci.length);
  System.arraycopy(CAT_LABELS, 0, cl, 0, cl.length);
  return new Object[] { CONTRACT, MOD, TITLE, VERSION, NODE, ci, cl, rows, FILES_CSV, NOTE };
}""",
# tmp file + fsync + atomic rename, 5 x 20 ms retries on FileSystemException (the ProfCfg.atomicWrite copy, spec 1.4.4 step 6)
r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""",
# who == null is the server console ONLY with the explicit via "console" (CfgFn.cmdSetConsole); a UUID that resolved to null with any
# other via ("command" included) is denied, so a mod's lookup bug can never turn a player into the console
r"""
public static boolean allowed(java.util.UUID who, String via) {
  if (who == null) return "console".equals(via);
  try { return @PERMCHECK@; } catch (Throwable t) { return false; }
}""",
]

# ================================================================================================================ Java: CfgLog
LOG_FIELDS = [
    "public static java.nio.file.Path FILE;",
    "public static final java.util.ArrayList Q = new java.util.ArrayList();",
    "public static final long ROTATE = 1048576L;",
    "public static final java.time.format.DateTimeFormatter FMT = java.time.format.DateTimeFormatter.ofPattern(\"yyyy-MM-dd'T'HH:mm:ss\");",
]
LOG_JAVA = [
r"""public static void init() { FILE = @PKG@.CfgRows.HOME.resolve("config-changes.log"); }""",
r"""public static String now() { return FMT.format(java.time.LocalDateTime.now()); }""",
r"""public static synchronized void enqueue(String line) { Q.add(line); }""",
r"""public static synchronized java.util.ArrayList snap() { return new java.util.ArrayList(Q); }""",
r"""public static synchronized void drop(int n) { for (int k = 0; k < n && Q.size() > 0; k++) Q.remove(0); }""",
r"""
public static String nameOf(java.util.UUID who, String name) {
  if (name != null && name.length() > 0) return name;
  if (who == null) return "console";
  return who.toString();
}""",
# one line per change, tab separated (spec 1.4.6); the file is appended by the save task, never on the caller's thread
r"""
public static void add(java.util.UUID who, String name, String via, String key, String old, String nw, String status) {
  String n = nameOf(who, name);
  String u = "-";
  if (who != null) u = who.toString();
  String o = old;
  if (o == null) o = "";
  String w = nw;
  if (w == null) w = "";
  String line = now() + "\t" + @PKG@.CfgRows.oneLine(n) + "\t" + u + "\t" + @PKG@.CfgRows.oneLine(via) + "\t" + @PKG@.CfgRows.oneLine(key)
    + "\t" + @PKG@.CfgRows.oneLine(o) + "\t" + @PKG@.CfgRows.oneLine(w) + "\t" + @PKG@.CfgRows.oneLine(status);
  enqueue(line);
  String tail = "";
  if (!"ok".equals(status)) tail = " [" + status + "]";
  @PKG@.CfgRows.info("config " + key + " " + @PKG@.CfgRows.oneLine(o) + " -> " + @PKG@.CfgRows.oneLine(w) + " by " + n + " (" + via + ")" + tail);
}""",
r"""
public static void addFile(java.util.ArrayList entries) {
  for (int k = 0; k < entries.size(); k++) {
    String[] e = (String[]) entries.get(k);
    add(null, "file", "file", e[0], e[1], e[2], e[3]);
  }
}""",
r"""
public static java.nio.file.Path old(int n) { return FILE.resolveSibling(FILE.getFileName().toString() + "." + n); }""",
r"""
public static void rotate() throws java.io.IOException {
  java.nio.file.Files.deleteIfExists(old(3));
  for (int n = 2; n >= 1; n--) {
    if (java.nio.file.Files.exists(old(n), new java.nio.file.LinkOption[0]))
      java.nio.file.Files.move(old(n), old(n + 1), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
  java.nio.file.Files.move(FILE, old(1), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
}""",
# save thread only (the save task, CfgPub.flush/shutdown): rotate at 1 MB, keep 3 old files
r"""
public static void flush() {
  if (FILE == null) return;
  java.util.ArrayList l = snap();
  if (l.size() == 0) return;
  try {
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < l.size(); k++) sb.append((String) l.get(k)).append('\n');
    byte[] data = sb.toString().getBytes("UTF-8");
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]) && java.nio.file.Files.size(FILE) >= ROTATE) rotate();
    java.nio.file.Files.write(FILE, data, new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    drop(l.size());
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not write " + FILE + " (kept in memory, retried with the next save): " + t); }
}""",
r"""
public static void addLines(java.util.ArrayList all, java.nio.file.Path p) {
  try {
    if (!java.nio.file.Files.exists(p, new java.nio.file.LinkOption[0])) return;
    String t = new String(java.nio.file.Files.readAllBytes(p), "UTF-8");
    String[] ls = t.split("\n");
    for (int k = 0; k < ls.length; k++) if (ls[k].trim().length() > 0) all.add(ls[k]);
  } catch (Throwable x) { }
}""",
r"""
public static String[] read(int max) {
  java.util.ArrayList all = new java.util.ArrayList();
  if (FILE != null) {
    java.util.ArrayList main = new java.util.ArrayList();
    addLines(main, FILE);
    if (main.size() < max) addLines(all, old(1));
    all.addAll(main);
  }
  all.addAll(snap());
  int n = all.size();
  if (n > max) n = max;
  String[] r = new String[n];
  for (int k = 0; k < n; k++) r[k] = (String) all.get(all.size() - 1 - k);
  return r;
}""",
]

# ================================================================================================================ Java: CfgHist
HIST_FIELDS = [
    "public static java.nio.file.Path DIR;",
    "public static java.nio.file.Path INDEX;",
    "public static final java.time.format.DateTimeFormatter STAMP = java.time.format.DateTimeFormatter.ofPattern(\"yyyyMMdd-HHmmss-SSS\");",
    "public static final String SOH = String.valueOf((char) 1);",
]
HIST_JAVA = [
r"""public static void init() { DIR = @PKG@.CfgRows.HOME.resolve("config-history"); INDEX = DIR.resolve("index.log"); }""",
r"""public static String stamp() { return STAMP.format(java.time.LocalDateTime.now()); }""",
r"""
public static boolean validStamp(String s) {
  if (s == null || s.length() != 19) return false;
  for (int k = 0; k < 19; k++) {
    char c = s.charAt(k);
    if (k == 8 || k == 15) { if (c != '-') return false; }
    else if (c < '0' || c > '9') return false;
  }
  return true;
}""",
r"""
public static String next(String s) {
  try { return STAMP.format(java.time.LocalDateTime.parse(s, STAMP).plusNanos(1000000L)); } catch (Throwable t) { return stamp(); }
}""",
r"""
public static String human(String s) {
  return s.substring(0, 4) + "-" + s.substring(4, 6) + "-" + s.substring(6, 8) + " " + s.substring(9, 11) + ":" + s.substring(11, 13) + ":" + s.substring(13, 15);
}""",
r"""public static java.nio.file.Path bak(int f, String st) { return DIR.resolve(@PKG@.CfgRows.FILE_IDS[f] + "." + st + ".bak"); }""",
# sorted oldest first
r"""
public static String[] list(int f) {
  java.util.ArrayList r = new java.util.ArrayList();
  String pre = @PKG@.CfgRows.FILE_IDS[f] + ".";
  try {
    if (DIR != null && java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) {
      java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(DIR);
      try {
        java.util.Iterator it = ds.iterator();
        while (it.hasNext()) {
          String n = ((java.nio.file.Path) it.next()).getFileName().toString();
          if (n.startsWith(pre) && n.endsWith(".bak")) {
            String st = n.substring(pre.length(), n.length() - 4);
            if (validStamp(st)) r.add(st);
          }
        }
      } finally { ds.close(); }
    }
  } catch (Throwable t) { }
  java.util.Collections.sort(r);
  return (String[]) r.toArray(new String[0]);
}""",
r"""
public static int fileIdx(String id) {
  if (id == null) return -1;
  int h = id.lastIndexOf('#');
  if (h <= 0) return -1;
  String fid = id.substring(0, h);
  if (!validStamp(id.substring(h + 1))) return -1;
  for (int f = 0; f < @PKG@.CfgRows.FILE_IDS.length; f++) if (@PKG@.CfgRows.FILE_IDS[f].equals(fid)) return f;
  return -1;
}""",
r"""
public static byte[] read(String id) {
  int f = fileIdx(id);
  if (f < 0) return null;
  try {
    java.nio.file.Path p = bak(f, id.substring(id.lastIndexOf('#') + 1));
    if (!java.nio.file.Files.isRegularFile(p, new java.nio.file.LinkOption[0])) return null;
    return java.nio.file.Files.readAllBytes(p);
  } catch (Throwable t) { return null; }
}""",
r"""
public static void compact() {
  try {
    if (!java.nio.file.Files.exists(INDEX, new java.nio.file.LinkOption[0])) return;
    String[] ls = new String(java.nio.file.Files.readAllBytes(INDEX), "UTF-8").split("\n");
    if (ls.length < @PKG@.CfgRows.FILES.length * @PKG@.CfgRows.KEEP * 3 + 60) return;
    StringBuilder sb = new StringBuilder();
    for (int k = 0; k < ls.length; k++) {
      int t = ls[k].indexOf('\t');
      if (t <= 0) continue;
      String id = ls[k].substring(0, t);
      int f = fileIdx(id);
      if (f >= 0 && java.nio.file.Files.exists(bak(f, id.substring(id.lastIndexOf('#') + 1)), new java.nio.file.LinkOption[0])) sb.append(ls[k]).append('\n');
    }
    @PKG@.CfgRows.atomicWrite(INDEX, sb.toString().getBytes("UTF-8"));
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not tidy " + INDEX + ": " + t); }
}""",
# save thread only: the file as it is on disk BEFORE the write (spec 1.4.5); skipped when it equals the newest copy
r"""
public static void snapshot(int f, byte[] cur, String st, String who, String sum) {
  if (cur == null || DIR == null) return;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    String[] have = list(f);
    if (have.length > 0) {
      byte[] last = java.nio.file.Files.readAllBytes(bak(f, have[have.length - 1]));
      if (java.util.Arrays.equals(last, cur)) return;
    }
    String s = st;
    if (!validStamp(s)) s = stamp();
    int guard = 0;
    while (java.nio.file.Files.exists(bak(f, s), new java.nio.file.LinkOption[0]) && guard < 1000) { s = next(s); guard++; }
    @PKG@.CfgRows.atomicWrite(bak(f, s), cur);
    String line = @PKG@.CfgRows.FILE_IDS[f] + "#" + s + "\t" + @PKG@.CfgRows.FILES[f] + "\t" + human(s) + "\t" + @PKG@.CfgRows.oneLine(who) + "\t" + @PKG@.CfgRows.oneLine(sum) + "\n";
    java.nio.file.Files.write(INDEX, line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    have = list(f);
    for (int k = 0; k < have.length - @PKG@.CfgRows.KEEP; k++) java.nio.file.Files.deleteIfExists(bak(f, have[k]));
    compact();
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not save a history copy of " + @PKG@.CfgRows.FILES[f] + ": " + t); }
}""",
# newest first, max KEEP per file, only versions whose copy still exists
r"""
public static String[] versions() {
  java.util.ArrayList keys = new java.util.ArrayList();
  java.util.HashSet live = new java.util.HashSet();
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) {
    String[] have = list(f);
    int from = have.length - @PKG@.CfgRows.KEEP;
    if (from < 0) from = 0;
    for (int k = from; k < have.length; k++) live.add(@PKG@.CfgRows.FILE_IDS[f] + "#" + have[k]);
  }
  java.util.HashSet seen = new java.util.HashSet();
  try {
    if (INDEX != null && java.nio.file.Files.exists(INDEX, new java.nio.file.LinkOption[0])) {
      String[] ls = new String(java.nio.file.Files.readAllBytes(INDEX), "UTF-8").split("\n");
      for (int k = 0; k < ls.length; k++) {
        int t = ls[k].indexOf('\t');
        if (t <= 0) continue;
        String id = ls[k].substring(0, t);
        if (!live.contains(id) || !seen.add(id)) continue;
        keys.add(id.substring(id.lastIndexOf('#') + 1) + SOH + id + SOH + ls[k]);
      }
    }
  } catch (Throwable t) { }
  java.util.Collections.sort(keys);
  String[] r = new String[keys.size()];
  for (int k = 0; k < r.length; k++) { String s = (String) keys.get(keys.size() - 1 - k); r[k] = s.substring(s.indexOf(SOH, s.indexOf(SOH) + 1) + 1); }
  return r;
}""",
]

# ================================================================================================================ Java: CfgSaveTask (fields + ctor first)
TASK_FIELDS = ["public int idx;", "public long delay;", "public boolean sleepFirst;"]
TASK_CTOR = r"""public CfgSaveTask(int i, long ms) { this.idx = i; this.delay = ms; this.sleepFirst = false; }"""

# ================================================================================================================ Java: CfgFile (THE kit monitor)
FILE_JAVA_HELPERS = [
r"""
public static java.util.ArrayList split(String text) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (text == null || text.length() == 0) return l;
  int s = 0;
  for (int k = 0; k < text.length(); k++) {
    if (text.charAt(k) == '\n') {
      String ln = text.substring(s, k);
      if (ln.endsWith("\r")) ln = ln.substring(0, ln.length() - 1);
      l.add(ln);
      s = k + 1;
    }
  }
  if (s < text.length()) { String ln = text.substring(s); if (ln.endsWith("\r")) ln = ln.substring(0, ln.length() - 1); l.add(ln); }
  return l;
}""",
r"""
public static String join(java.util.ArrayList l, String nl, boolean end) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < l.size(); k++) { if (k > 0) sb.append(nl); sb.append((String) l.get(k)); }
  if (end && l.size() > 0) sb.append(nl);
  return sb.toString();
}""",
r"""
public static int lead(String s) {
  int k = 0;
  while (k < s.length() && (s.charAt(k) == ' ' || s.charAt(k) == '\t' || s.charAt(k) == '\f')) k++;
  return k;
}""",
r"""
public static boolean isComment(String s) {
  int k = lead(s);
  return k >= s.length() || s.charAt(k) == '#' || s.charAt(k) == '!';
}""",
r"""
public static boolean cont(String s) {
  int n = 0;
  int k = s.length() - 1;
  while (k >= 0 && s.charAt(k) == '\\') { n++; k--; }
  return (n % 2) == 1;
}""",
r"""
public static int keyEnd(String s) {
  int k = lead(s);
  while (k < s.length()) {
    char c = s.charAt(k);
    if (c == '\\') { k += 2; continue; }
    if (c == '=' || c == ':' || c == ' ' || c == '\t' || c == '\f') break;
    k++;
  }
  if (k > s.length()) k = s.length();
  return k;
}""",
r"""
public static int valStart(String s) {
  int k = keyEnd(s);
  while (k < s.length() && (s.charAt(k) == ' ' || s.charAt(k) == '\t' || s.charAt(k) == '\f')) k++;
  if (k < s.length() && (s.charAt(k) == '=' || s.charAt(k) == ':')) {
    k++;
    while (k < s.length() && (s.charAt(k) == ' ' || s.charAt(k) == '\t' || s.charAt(k) == '\f')) k++;
  }
  return k;
}""",
r"""
public static String unesc(String s) {
  if (s.indexOf('\\') < 0) return s;
  StringBuilder sb = new StringBuilder();
  int k = 0;
  while (k < s.length()) {
    char c = s.charAt(k);
    if (c != '\\') { sb.append(c); k++; continue; }
    if (k + 1 >= s.length()) { k++; continue; }
    char n = s.charAt(k + 1);
    if (n == 'u' && k + 6 <= s.length()) {
      try { sb.append((char) Integer.parseInt(s.substring(k + 2, k + 6), 16)); k += 6; continue; } catch (Throwable t) { }
    }
    if (n == 't') sb.append('\t'); else if (n == 'n') sb.append('\n'); else if (n == 'r') sb.append('\r'); else if (n == 'f') sb.append('\f'); else sb.append(n);
    k += 2;
  }
  return sb.toString();
}""",
# java.util.Properties escaping, non-ASCII as \uXXXX (spec 1.4.4 step 4): an ISO-8859-1 and a UTF-8 reader see the same value
r"""
public static String esc(String s, boolean isKey) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < s.length(); k++) {
    char c = s.charAt(k);
    if (c == '\\') sb.append("\\\\");
    else if (c == '\t') sb.append("\\t");
    else if (c == '\n') sb.append("\\n");
    else if (c == '\r') sb.append("\\r");
    else if (c == '\f') sb.append("\\f");
    else if (c == ' ' && (isKey || k == 0)) sb.append("\\ ");
    else if (isKey && (c == '=' || c == ':' || c == '#' || c == '!')) { sb.append('\\'); sb.append(c); }
    else if (c < 0x20 || c > 0x7e) {
      String h = Integer.toHexString(c);
      sb.append("\\u");
      for (int p = h.length(); p < 4; p++) sb.append('0');
      sb.append(h);
    } else sb.append(c);
  }
  return sb.toString();
}""",
r"""
public static String key(String s) {
  if (isComment(s)) return null;
  return unesc(s.substring(lead(s), keyEnd(s)));
}""",
r"""
public static int end(java.util.ArrayList l, int start) {
  int e = start;
  while (e < l.size() - 1 && cont((String) l.get(e))) e++;
  return e;
}""",
r"""
public static String value(java.util.ArrayList l, int start) {
  int e = end(l, start);
  StringBuilder sb = new StringBuilder();
  for (int k = start; k <= e; k++) {
    String s = (String) l.get(k);
    String part = null;
    if (k == start) part = s.substring(valStart(s)); else part = s.substring(lead(s));
    if (cont(s) && part.length() > 0) part = part.substring(0, part.length() - 1);
    sb.append(part);
  }
  return unesc(sb.toString());
}""",
r"""
public static java.util.HashMap parseVals(java.util.ArrayList l) {
  java.util.HashMap m = new java.util.HashMap();
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (isComment(s)) { k++; continue; }
    int e = end(l, k);
    String kk = key(s);
    if (kk != null) m.put(kk, value(l, k));
    k = e + 1;
  }
  return m;
}""",
# '#key=value' or '# key=value' with a one-token value = a template line (a doc comment has spaces in its text)
r"""
public static boolean isTemplate(String s, String key) {
  int k = lead(s);
  if (k >= s.length() || s.charAt(k) != '#') return false;
  k++;
  while (k < s.length() && s.charAt(k) == ' ') k++;
  String rest = s.substring(k);
  String ek = esc(key, true);
  if (!rest.startsWith(ek)) return false;
  int p = ek.length();
  while (p < rest.length() && rest.charAt(p) == ' ') p++;
  if (p >= rest.length() || (rest.charAt(p) != '=' && rest.charAt(p) != ':')) return false;
  String v = rest.substring(p + 1).trim();
  for (int q = 0; q < v.length(); q++) if (Character.isWhitespace(v.charAt(q))) return false;
  return true;
}""",
# spec 1.4.4 steps 1-3: replace the value on every live line of the key (the last one wins when the mod reads the file), else
# uncomment a template line, else append under one header; val == null removes the key's lines
r"""
public static void applyEdit(java.util.ArrayList l, String fk, String val) {
  boolean found = false;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (isComment(s)) { k++; continue; }
    int e = end(l, k);
    String kk = key(s);
    if (kk != null && kk.equals(fk)) {
      if (val == null) { for (int r = e; r >= k; r--) l.remove(r); found = true; continue; }
      String pre = s.substring(0, valStart(s));
      l.set(k, pre + esc(val, false));
      for (int r = e; r > k; r--) l.remove(r);
      found = true;
      k++;
      continue;
    }
    k = e + 1;
  }
  if (found || val == null) return;
  for (int t = 0; t < l.size(); t++) {
    if (isTemplate((String) l.get(t), fk)) { l.set(t, esc(fk, true) + "=" + esc(val, false)); return; }
  }
  boolean hdr = false;
  for (int t = 0; t < l.size(); t++) if (HEADER.equals(((String) l.get(t)).trim())) hdr = true;
  if (!hdr) {
    if (l.size() > 0 && ((String) l.get(l.size() - 1)).trim().length() > 0) l.add("");
    l.add(HEADER);
  }
  l.add(esc(fk, true) + "=" + esc(val, false));
}""",
]

FILE_JAVA_STATE = [
r"""
public static void init() {
  for (int f = 0; f < NF; f++) {
    PATH[f] = @PKG@.CfgRows.MODS.resolve(@PKG@.CfgRows.FILES[f]);
    LINES[f] = new java.util.ArrayList();
    BASE[f] = new java.util.HashMap();
    VALS[f] = new java.util.HashMap();
    PEND[f] = new java.util.LinkedHashMap();
    RLD[f] = new java.util.HashSet();
    PWHAT[f] = new java.util.HashSet();
    HOLD[f] = new java.util.HashMap();
    HCHK[f] = new java.util.HashMap();
    WROTE[f] = new java.util.HashMap();
    NL[f] = "\n";
    ENDNL[f] = true;
  }
}""",
# I/O, no lock. Missing file = null bytes (not unreadable); a folder or a read error = unreadable
r"""
public static Object[] readDisk(int f) throws Exception {
  java.nio.file.Path p = PATH[f];
  if (java.nio.file.Files.isDirectory(p, new java.nio.file.LinkOption[0])) throw new java.io.IOException(@PKG@.CfgRows.FILES[f] + " is a folder");
  if (!java.nio.file.Files.exists(p, new java.nio.file.LinkOption[0])) return new Object[] { null, Long.valueOf(0L), Long.valueOf(-1L) };
  byte[] b = java.nio.file.Files.readAllBytes(p);
  long mt = java.nio.file.Files.getLastModifiedTime(p, new java.nio.file.LinkOption[0]).toMillis();
  return new Object[] { b, Long.valueOf(mt), Long.valueOf((long) b.length) };
}""",
r"""
public static synchronized void seed(int f) {
  String[] d = @PKG@.CfgRows.defLines(f);
  for (int k = 0; k < d.length; k++) LINES[f].add(d[k]);
}""",
# kit 1.1: table entries whose hand edit was refused keep their old value in memory (HOLD: file key -> old file text, null = the entry
# did not exist); laid over VALS after every re-parse, dropped by an in-game edit of that key or by a later accepted hand edit.
# A hand-edited line whose check= hook has not answered yet is held too (memory never shows a value that did not pass), and HCHK maps
# its file key to that pending check (the String[] handApply queued): only the check still in HCHK may accept or keep refusing the
# line; a newer change of the entry (an in-game edit, a newer hand edit) replaces or drops it
r"""
public static synchronized void holdOver(int f) {
  java.util.ArrayList drop = new java.util.ArrayList();
  java.util.Iterator it = HOLD[f].keySet().iterator();
  while (it.hasNext()) {
    String fk = (String) it.next();
    if (PEND[f].containsKey(fk)) { drop.add(fk); continue; }
    String v = (String) HOLD[f].get(fk);
    if (v == null) VALS[f].remove(fk); else VALS[f].put(fk, v);
  }
  for (int k = 0; k < drop.size(); k++) HOLD[f].remove(drop.get(k));
}""",
r"""
public static synchronized void holdSet(int f, String fk, String oldRaw) {
  HOLD[f].put(fk, oldRaw);
  if (oldRaw == null) VALS[f].remove(fk); else VALS[f].put(fk, oldRaw);
}""",
r"""
public static synchronized boolean holdClear(int f, String fk, String nowRaw) {
  if (!HOLD[f].containsKey(fk)) return false;
  HOLD[f].remove(fk);
  if (nowRaw == null) VALS[f].remove(fk); else VALS[f].put(fk, nowRaw);
  return true;
}""",
# the disk text replaces the in-memory copy; in-game edits not yet saved are applied again on top (spec 1.4.4 step 5)
r"""
public static synchronized java.util.ArrayList merge(int f, byte[] disk, long mt, long sz) throws Exception {
  String text = "";
  if (disk != null) text = new String(disk, "ISO-8859-1");
  java.util.ArrayList lines = split(text);
  java.util.HashMap nv = parseVals(lines);
  java.util.ArrayList diffs = new java.util.ArrayList();
  if (LOADED[f]) {
    java.util.HashMap old = BASE[f];
    java.util.Iterator it = nv.keySet().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      Object o = old.get(k);
      Object n = nv.get(k);
      if (o == null || !o.equals(n)) diffs.add(new String[] { k, (String) o, (String) n });
    }
    it = old.keySet().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (!nv.containsKey(k)) diffs.add(new String[] { k, (String) old.get(k), null });
    }
  }
  if (disk != null) { if (text.indexOf("\r\n") >= 0) NL[f] = "\r\n"; else NL[f] = "\n"; ENDNL[f] = text.length() == 0 || text.endsWith("\n"); }
  MISSING[f] = disk == null;
  LINES[f] = lines;
  if (MISSING[f] && PEND[f].size() > 0) seed(f);
  java.util.Iterator pit = PEND[f].keySet().iterator();
  while (pit.hasNext()) { String k = (String) pit.next(); applyEdit(LINES[f], k, (String) PEND[f].get(k)); }
  VALS[f] = parseVals(LINES[f]);
  holdOver(f);
  BASE[f] = nv;
  MT[f] = mt;
  SZ[f] = sz;
  BROKEN[f] = false;
  WARNED[f] = false;
  WHY[f] = null;
  LOADED[f] = true;
  return diffs;
}""",
r"""
public static synchronized boolean markBroken(int f, Throwable t) {
  BROKEN[f] = true;
  WHY[f] = String.valueOf(t);
  if (WARNED[f]) return false;
  WARNED[f] = true;
  return true;
}""",
r"""public static synchronized boolean isBroken(int f) { return BROKEN[f]; }""",
r"""public static synchronized boolean isFailed(int f) { return FAILED[f]; }""",
# kit 1.1: in-game changes of this file still only in memory, and the file can be written (not unreadable, no failed write pending)
r"""public static synchronized boolean dirtyOk(int f) { return DIRTY[f] && !BROKEN[f] && !FAILED[f]; }""",
r"""public static synchronized boolean changedOnDisk(int f, long mt, long sz) { return BROKEN[f] || !LOADED[f] || FORCE[f] || mt != MT[f] || sz != SZ[f]; }""",
# kit 1.1: a pending reload request with no changed line (CfgFile.addReloads alone) also wants a save pass, so its routine runs
r"""public static synchronized boolean wants(int f) { return DIRTY[f] || FORCE[f] || RLD[f].size() > 0 || (BROKEN[f] && PEND[f].size() > 0); }""",
r"""
public static synchronized String value(int f, String fk) {
  if (f < 0) return null;
  Object o = VALS[f].get(fk);
  if (o == null) return null;
  return (String) o;
}""",
r"""
public static synchronized String[] entries(int f, String prefix) {
  java.util.ArrayList r = new java.util.ArrayList();
  java.util.Iterator it = VALS[f].keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k.startsWith(prefix) && k.length() > prefix.length()) r.add(k); }
  java.util.Collections.sort(r);
  return (String[]) r.toArray(new String[0]);
}""",
r"""
public static synchronized boolean edit(int f, String fk, String val, String stamp, String who, String via, String what) {
  if (BROKEN[f]) return false;
  if (MISSING[f] && LINES[f].size() == 0) seed(f);
  applyEdit(LINES[f], fk, val);
  PEND[f].remove(fk);
  PEND[f].put(fk, val);
  HOLD[f].remove(fk);
  HCHK[f].remove(fk);
  if (val == null) VALS[f].remove(fk); else VALS[f].put(fk, val);
  DIRTY[f] = true;
  if (PSTAMP[f] == null) PSTAMP[f] = stamp;
  PWHO[f] = who;
  PVIA[f] = via;
  PWHAT[f].add(what);
  return true;
}""",
# kit 1.1: the file lines a customSet hands back ({ key1, value1, key2, value2 }, value null removes the line), all under one monitor
# hold, plus the reload routine rel (the mod's RELOAD; "" = none) when at least one line was taken
r"""
public static synchronized int editLines(int f, String[] fl, String stamp, String who, String via, String what, String rel) {
  int n = 0;
  for (int q = 0; q + 1 < fl.length; q += 2) {
    if (fl[q] == null) continue;
    if (edit(f, fl[q], fl[q + 1], stamp, who, via, what)) n++;
  }
  if (n > 0 && rel != null && rel.length() > 0) RLD[f].add(rel);
  return n;
}""",
r"""
public static synchronized void bump() {
  try {
    java.util.Map b = @PKG@.CfgRows.bridge();
    String k = "config:epoch:" + @PKG@.CfgRows.MOD;
    Object o = b.get(k);
    long v = 0L;
    if (o instanceof Long) v = ((Long) o).longValue();
    b.put(k, Long.valueOf(v + 1L));
  } catch (Throwable t) { }
}""",
# one scalar row: field (unless restart) + file line + pending restart value + reload mark + epoch, all under the kit monitor.
# A restart row never queues its reload routine: the value waits in the file for the next start (spec 1.4.1 flags, "restart")
r"""
public static synchronized boolean setRow(int i, String canon, String ftext, String stamp, String who, String via, boolean setField) throws Exception {
  int f = @PKG@.CfgRows.BF[i];
  if (f >= 0 && BROKEN[f]) return false;
  if (setField) @PKG@.CfgRows.fieldSet(i, canon);
  if (f >= 0) edit(f, @PKG@.CfgRows.BFK[i], ftext, stamp, who, via, @PKG@.CfgRows.KEYS[i]);
  if (@PKG@.CfgRows.flag(i, "restart")) PENDV[i] = canon;
  else if (@PKG@.CfgRows.BK[i] == 2 && f >= 0) RLD[f].add(@PKG@.CfgRows.BNAME[i]);
  bump();
  return true;
}""",
r"""
public static synchronized boolean setEntry(int i, String fk, String ftext, String stamp, String who, String via, String what) {
  int f = @PKG@.CfgRows.BF[i];
  if (f < 0 || BROKEN[f]) return false;
  edit(f, fk, ftext, stamp, who, via, what);
  if (@PKG@.CfgRows.BK[i] == 2 && !@PKG@.CfgRows.flag(i, "restart")) RLD[f].add(@PKG@.CfgRows.BNAME[i]);
  bump();
  return true;
}""",
r"""public static synchronized String pendv(int i) { return PENDV[i]; }""",
r"""public static synchronized void setPendv(int i, String v) { PENDV[i] = v; }""",
r"""public static synchronized String runv(int i) { return RUNV[i]; }""",
r"""public static synchronized void setRunv(int i, String v) { RUNV[i] = v; }""",
r"""public static synchronized void addReloads(int f, java.util.HashSet s) { RLD[f].addAll(s); }""",
r"""public static synchronized void force(int f) { FORCE[f] = true; }""",
r"""
public static void schedule(int f, long ms) {
  @PKG@.CfgSaveTask t = new @PKG@.CfgSaveTask(f, ms);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(t, ms, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable e) {
    t.sleepFirst = true;
    Thread th = new Thread(t, "SkyyCfg-" + @PKG@.CfgRows.MOD);
    th.setDaemon(true);
    th.start();
  }
}""",
r"""
public static synchronized void saveSoon(int f) {
  if (f < 0) return;
  if (SCHED[f]) return;
  SCHED[f] = true;
  schedule(f, 500L);
}""",
r"""
public static synchronized void saveNowSoon(int f) {
  if (SCHED[f]) return;
  SCHED[f] = true;
  schedule(f, 0L);
}""",
r"""
public static synchronized void retry(int f) {
  SCHED[f] = true;
  schedule(f, 30000L);
}""",
r"""public static synchronized void unsched(int f) { SCHED[f] = false; }""",
r"""
public static synchronized void logSoon() {
  if (LOGSCHED) return;
  LOGSCHED = true;
  schedule(-1, 500L);
}""",
r"""public static synchronized void logDone() { LOGSCHED = false; }""",
r"""
public static String summary(int f) {
  String w = PWHO[f];
  if (w == null) w = "?";
  String v = PVIA[f];
  if (v != null && (v.equals("import") || v.equals("restore") || v.equals("undo"))) return "before " + v + " by " + w;
  if (PWHAT[f].size() == 1) return "before " + w + " changed " + (String) PWHAT[f].iterator().next();
  return "before " + w + " changed " + PWHAT[f].size() + " settings";
}""",
r"""
public static synchronized Object[] takeBatch(int f) throws Exception {
  FORCE[f] = false;
  if (BROKEN[f]) return null;
  if (!DIRTY[f]) {
    if (RLD[f].size() == 0) return null;
    Object[] z = new Object[] { null, null, null, null, null, RLD[f], null };
    RLD[f] = new java.util.HashSet();
    return z;
  }
  byte[] out = join(LINES[f], NL[f], ENDNL[f] || MISSING[f]).getBytes("ISO-8859-1");
  String st = PSTAMP[f];
  if (st == null) st = @PKG@.CfgHist.stamp();
  SGEN = SGEN + 1L;
  java.util.Iterator wi = PEND[f].keySet().iterator();
  while (wi.hasNext()) { String wk = (String) wi.next(); WROTE[f].put(wk, new Object[] { PEND[f].get(wk), Long.valueOf(SGEN) }); }
  Object[] r = new Object[] { out, st, summary(f), PWHO[f], PEND[f], RLD[f], PVIA[f], PWHAT[f] };
  PEND[f] = new java.util.LinkedHashMap();
  RLD[f] = new java.util.HashSet();
  DIRTY[f] = false;
  PSTAMP[f] = null;
  PWHAT[f] = new java.util.HashSet();
  return r;
}""",
r"""
public static synchronized void saveOk(int f, byte[] out, long mt) throws Exception {
  BASE[f] = parseVals(split(new String(out, "ISO-8859-1")));
  MT[f] = mt;
  SZ[f] = (long) out.length;
  FAILED[f] = false;
  MISSING[f] = false;
}""",
r"""
public static synchronized boolean saveFail(int f, Object[] b) {
  java.util.LinkedHashMap np = new java.util.LinkedHashMap((java.util.LinkedHashMap) b[4]);
  java.util.Iterator it = PEND[f].keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); np.remove(k); np.put(k, PEND[f].get(k)); }
  PEND[f] = np;
  RLD[f].addAll((java.util.HashSet) b[5]);
  DIRTY[f] = true;
  if (PSTAMP[f] == null) { PSTAMP[f] = (String) b[1]; PWHO[f] = (String) b[3]; PVIA[f] = (String) b[6]; }
  PWHAT[f].addAll((java.util.HashSet) b[7]);
  boolean first = !FAILED[f];
  FAILED[f] = true;
  return first;
}""",
# which rows a file key belongs to: scalar rows first, then the table (key family) with the LONGEST matching prefix (emit() already
# refuses overlapping prefixes in one file; most-specific-wins is the defence in depth)
r"""
public static int rowFor(int f, String fk) {
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.BF[i] != f || @PKG@.CfgRows.isTable(i)) continue;
    int k = @PKG@.CfgRows.BK[i];
    if ((k == 1 || k == 2) && @PKG@.CfgRows.BFK[i].equals(fk)) return i;
    if (k == 3 && ("," + @PKG@.CfgRows.BCK[i] + ",").indexOf("," + fk + ",") >= 0) return i;
  }
  int best = -1;
  int bestLen = -1;
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.BF[i] != f || !@PKG@.CfgRows.isTable(i) || @PKG@.CfgRows.BK[i] != 2) continue;
    String p = @PKG@.CfgRows.BFK[i];
    if (fk.startsWith(p) && fk.length() > p.length() && p.length() > bestLen) { best = i; bestLen = p.length(); }
  }
  return best;
}""",
r"""
public static String colsFromFile(int i, String raw) {
  if (raw == null) return null;
  String sep = @PKG@.CfgRows.BSEP[i];
  if (@PKG@.CfgRows.oneCol(i) || sep.length() == 0) return raw.trim();
  StringBuilder sb = new StringBuilder();
  int s = 0;
  while (true) {
    int p = raw.indexOf(sep, s);
    if (p < 0) { sb.append(raw.substring(s).trim()); break; }
    sb.append(raw.substring(s, p).trim()).append('|');
    s = p + sep.length();
  }
  return sb.toString();
}""",
r"""
public static String colsToFile(int i, String cols) {
  if (cols == null) return null;
  if (@PKG@.CfgRows.oneCol(i)) return cols;
  return cols.replace("|", @PKG@.CfgRows.BSEP[i]);
}""",
# hand edits found at a save or a reload (spec 1.4.4 step 5, 1.4.2): returns { log entries, reload routines, changed row count,
# table lines whose check= hook must still run }. Kit 1.1: a hand-edited table line gets the kit's own checks here (entry key, column
# count / types / bounds; pure kit code, allowed under the monitor); a refused one is logged invalid and memory keeps the old value
# (holdSet). A '|' typed into a 2-3 column line is refused too (the kit never writes one there: columns are split by sep=, so the
# mod's loader would misread it). A line of a row with a check= hook is only queued: the hook is mod code, so CfgFn.handChecks runs it
# after this monitor (and the save lock) is released, then keeps refusing or accepts the line (holdIf / unholdIf) and logs it. Until
# then the line is held like a refused one (memory keeps the last value that passed) and HCHK[f] names its pending check; any newer
# diff of the same entry drops that pending check first, so a late answer about an older line never touches memory
r"""
public static synchronized Object[] handApply(int f, java.util.ArrayList diffs) {
  java.util.ArrayList logs = new java.util.ArrayList();
  java.util.HashSet rel = new java.util.HashSet();
  java.util.ArrayList checks = new java.util.ArrayList();
  int n = 0;
  for (int d = 0; d < diffs.size(); d++) {
    String[] df = (String[]) diffs.get(d);
    String fk = df[0];
    int i = rowFor(f, fk);
    if (i < 0) continue;
    n++;
    int k = @PKG@.CfgRows.BK[i];
    boolean mine = PEND[f].containsKey(fk);
    String st = "ok";
    if (mine) st = "overridden";
    if (@PKG@.CfgRows.isTable(i)) {
      HCHK[f].remove(fk);
      String e = fk.substring(@PKG@.CfgRows.BFK[i].length());
      String tk = @PKG@.CfgRows.KEYS[i] + "[" + e + "]";
      String oldRaw = df[1];
      if (HOLD[f].containsKey(fk)) oldRaw = (String) HOLD[f].get(fk);
      String o = colsFromFile(i, oldRaw);
      String w = colsFromFile(i, df[2]);
      if (o == null) o = "(none)";
      if (w == null) w = "(none)";
      if (mine) { logs.add(new String[] { tk, o, w, st }); continue; }
      String canon = null;
      String why = null;
      if (df[2] != null) {
        why = @PKG@.CfgFn.entryErr(i, e);
        if (why == null && !@PKG@.CfgRows.oneCol(i) && df[2].indexOf('|') >= 0) why = "a | inside a column";
        if (why == null) { String[] tv = @PKG@.CfgFn.tvalue(i, w); canon = tv[0]; why = tv[1]; }
      }
      if (why != null) { holdSet(f, fk, oldRaw); logs.add(new String[] { tk, o, w, "invalid" }); continue; }
      if (@PKG@.CfgRows.BCHECK[i].length() > 0) {
        String[] c = new String[] { fk, oldRaw, df[2], canon, tk, o, w, String.valueOf(i) };
        holdSet(f, fk, oldRaw);
        HCHK[f].put(fk, c);
        checks.add(c);
        continue;
      }
      holdClear(f, fk, df[2]);
      logs.add(new String[] { tk, o, w, "ok" });
      if (!@PKG@.CfgRows.flag(i, "restart")) rel.add(@PKG@.CfgRows.BNAME[i]);
      continue;
    }
    if (k == 3) {
      String o = df[1];
      String w = df[2];
      if (o == null) o = "(none)";
      if (w == null) w = "(none)";
      logs.add(new String[] { @PKG@.CfgRows.KEYS[i], fk + "=" + o, fk + "=" + w, "file" });
      if (!mine && @PKG@.CfgRows.RELOAD.length() > 0) rel.add(@PKG@.CfgRows.RELOAD);
      continue;
    }
    String o = @PKG@.CfgRows.fromFile(i, df[1]);
    String w = @PKG@.CfgRows.fromFile(i, df[2]);
    String clamp = null;
    if (!mine) {
      WROTE[f].remove(fk);
      if (@PKG@.CfgRows.flag(i, "restart")) {
        PENDV[i] = w;
      } else if (k == 1) {
        if (@PKG@.CfgRows.RELOAD.length() > 0) rel.add(@PKG@.CfgRows.RELOAD);
        else {
          String fa = @PKG@.CfgRows.fileApply(i, df[2]);
          if (fa.equals("invalid")) st = "invalid";
          if (fa.equals("clamped")) { try { clamp = @PKG@.CfgRows.fieldGet(i); } catch (Throwable t) { clamp = "?"; } }
        }
      } else if (k == 2) {
        rel.add(@PKG@.CfgRows.BNAME[i]);
      }
    }
    logs.add(new String[] { @PKG@.CfgRows.KEYS[i], o, w, st });
    if (clamp != null) logs.add(new String[] { @PKG@.CfgRows.KEYS[i], w, clamp, "clamped" });
  }
  if (n > 0) bump();
  return new Object[] { logs, rel, Integer.valueOf(n), checks };
}""",
# kit 1.1, after a table line's check= hook ran outside the monitor (c = the String[] handApply queued): only while c is still the
# entry's pending check (no in-game edit, no newer hand edit of it since, no in-game edit waiting) - refused: the hold handApply set
# stays (memory keeps the last value that passed); accepted: the hold is dropped and memory shows the hand-typed line. True = applied
r"""
public static synchronized boolean holdIf(int f, String[] c) {
  String fk = c[0];
  Object me = c;
  if (HCHK[f].get(fk) != me) return false;
  HCHK[f].remove(fk);
  if (PEND[f].containsKey(fk)) return false;
  if (!HOLD[f].containsKey(fk)) { holdSet(f, fk, c[1]); bump(); }
  return true;
}""",
r"""
public static synchronized boolean unholdIf(int f, String[] c) {
  String fk = c[0];
  Object me = c;
  if (HCHK[f].get(fk) != me) return false;
  HCHK[f].remove(fk);
  if (PEND[f].containsKey(fk)) return false;
  if (holdClear(f, fk, c[2])) bump();
  return true;
}""",
# kit 1.1: merge + the kit's checks of the hand-edited lines in ONE monitor hold, so no reader ever sees a hand-typed table line in
# memory before the kit's own checks (and the hold of a line that still waits for its check= hook) are applied
r"""
public static synchronized Object[] mergeApply(int f, byte[] disk, long mt, long sz) throws Exception {
  return handApply(f, merge(f, disk, mt, sz));
}""",
# kit 1.1, after the mod's reload routines ran (CfgSaveTask.runReloads): a routine re-reads the mod's files, so a field: row whose
# in-game value was not on disk while it read was just set back to the old file text: a value still only in memory (its file could not
# be written: a failed write waiting for its 30 s retry, an unreadable file, or an edit that landed meanwhile), or one whose save batch
# was taken after g0 (CfgSaveTask.quiet, just before the routines: that write may have landed after the routine read the file). Set
# those fields again from that in-game value (validated in game already; WROTE = the last value each save batch took per file key,
# dropped when a hand edit of the key is merged), so memory, the field and the file agree; returns how many were set
r"""
public static synchronized long sgen() { return SGEN; }""",
r"""
public static synchronized int reassert(long g0) {
  int n = 0;
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.BK[i] != 1) continue;
    int f = @PKG@.CfgRows.BF[i];
    if (f < 0 || @PKG@.CfgRows.flag(i, "restart")) continue;
    String fk = @PKG@.CfgRows.BFK[i];
    Object v = null;
    if (PEND[f].containsKey(fk)) v = PEND[f].get(fk);
    else {
      Object[] w = (Object[]) WROTE[f].get(fk);
      if (w != null && ((Long) w[1]).longValue() > g0) v = w[0];
    }
    if (v == null) continue;
    if (@PKG@.CfgRows.fileApply(i, (String) v).equals("ok")) n++;
  }
  return n;
}""",
]

# ================================================================================================================ Java: CfgSaveTask (methods)
TASK_JAVA = [
# the locked part of a save (file I/O under the CfgSaveTask monitor): returns { reload routines, hand-edited table lines whose check=
# hook still has to run (kit 1.1) or null }
r"""
public static synchronized Object[] saveLocked(int f) {
  @PKG@.CfgFile.unsched(f);
  java.util.HashSet rel = new java.util.HashSet();
  java.util.ArrayList checks = null;
  if (!@PKG@.CfgFile.wants(f)) return new Object[] { rel, checks };
  Object[] d = null;
  try { d = @PKG@.CfgFile.readDisk(f); }
  catch (Throwable t) {
    if (@PKG@.CfgFile.markBroken(f, t)) @PKG@.CfgRows.warn(@PKG@.CfgRows.FILES[f] + " cannot be read - in-game changes to it wait until it can be read again (fix or delete it, then Reload): " + t);
    @PKG@.CfgFile.retry(f);
    return new Object[] { rel, checks };
  }
  byte[] cur = (byte[]) d[0];
  long mt = ((Long) d[1]).longValue();
  long sz = ((Long) d[2]).longValue();
  try {
    if (@PKG@.CfgFile.changedOnDisk(f, mt, sz)) {
      Object[] h = @PKG@.CfgFile.mergeApply(f, cur, mt, sz);
      @PKG@.CfgLog.addFile((java.util.ArrayList) h[0]);
      rel.addAll((java.util.HashSet) h[1]);
      checks = (java.util.ArrayList) h[3];
    }
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not re-read " + @PKG@.CfgRows.FILES[f] + ": " + t); @PKG@.CfgFile.retry(f); return new Object[] { rel, checks }; }
  Object[] b = null;
  try { b = @PKG@.CfgFile.takeBatch(f); } catch (Throwable t) { @PKG@.CfgRows.warn("save of " + @PKG@.CfgRows.FILES[f] + " failed: " + t); }
  if (b == null) { @PKG@.CfgLog.flush(); return new Object[] { rel, checks }; }
  if (b[0] == null) { rel.addAll((java.util.HashSet) b[5]); @PKG@.CfgLog.flush(); return new Object[] { rel, checks }; }
  @PKG@.CfgHist.snapshot(f, cur, (String) b[1], (String) b[3], (String) b[2]);
  byte[] out = (byte[]) b[0];
  try { @PKG@.CfgRows.atomicWrite(@PKG@.CfgFile.PATH[f], out); }
  catch (Throwable t) {
    if (@PKG@.CfgFile.saveFail(f, b)) @PKG@.CfgRows.warn("could not save " + @PKG@.CfgRows.FILES[f] + " (the change is kept in memory; retried every 30 s and at shutdown): " + t);
    @PKG@.CfgFile.retry(f);
    @PKG@.CfgLog.flush();
    return new Object[] { rel, checks };
  }
  long nmt = 0L;
  try { nmt = java.nio.file.Files.getLastModifiedTime(@PKG@.CfgFile.PATH[f], new java.nio.file.LinkOption[0]).toMillis(); } catch (Throwable t) { }
  try { @PKG@.CfgFile.saveOk(f, out, nmt); } catch (Throwable t) { }
  @PKG@.CfgLog.flush();
  rel.addAll((java.util.HashSet) b[5]);
  return new Object[] { rel, checks };
}""",
# kit 1.1: the reload op's read + merge, under the same monitor as a save (no mod code runs here). Without it a reload could read the
# file while a save is writing it and merge that older text: memory would drop the in-game change being written (and show a refused
# hand-typed line again, its hold already dropped by that change), and a later save could write the older lines back
r"""
public static synchronized Object[] readMerge(int f) throws Exception {
  Object[] d = @PKG@.CfgFile.readDisk(f);
  return @PKG@.CfgFile.mergeApply(f, (byte[]) d[0], ((Long) d[1]).longValue(), ((Long) d[2]).longValue());
}""",
# one save pass: the locked part, then (no kit lock held) the check= hooks of hand-edited table lines; the caller runs the reloads
r"""
public static java.util.HashSet saveFile(int f) {
  Object[] r = saveLocked(f);
  java.util.HashSet rel = (java.util.HashSet) r[0];
  if (r[1] != null) @PKG@.CfgFn.handChecks(f, (java.util.ArrayList) r[1], rel);
  return rel;
}""",
# a field row whose file value is not what the mod's loader put in the field was clamped (or refused) by that loader (spec 1.4.2)
r"""
public static void clampCheck() {
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.BK[i] != 1 || @PKG@.CfgRows.BF[i] < 0 || @PKG@.CfgRows.flag(i, "restart")) continue;
    try {
      String raw = @PKG@.CfgFile.value(@PKG@.CfgRows.BF[i], @PKG@.CfgRows.BFK[i]);
      if (raw == null) continue;
      String fv = @PKG@.CfgRows.fromFile(i, raw);
      String run = @PKG@.CfgRows.fieldGet(i);
      if (!@PKG@.CfgRows.same(i, fv, run) && !@PKG@.CfgFile.clampSeen(i, raw)) @PKG@.CfgLog.add(null, "file", "file", @PKG@.CfgRows.KEYS[i], raw.trim(), run, "clamped");
    } catch (Throwable t) { }
  }
}""",
# the mod's reload routines, after the write, outside every kit lock; a global RELOAD run is followed by the clamp check.
# Kit 1.1: a reload routine re-reads the mod's files, so every other file whose in-game changes are still only in memory is written
# first (a field: row's new value would otherwise be read back as the old file text and stay reverted); their routines join this run.
# A file that still cannot be written (a failed write: saveFail keeps its changes and reload marks for the 30 s retry, which runs its
# own routines after the write) is read stale by the routines, and so may be a file another thread saves while they run: quiet() waits
# for a save that is writing right now and notes the batch count, and CfgFile.reassert then sets the field: values those routines may
# have read stale again (before the clamp check, which would otherwise log them clamped)
r"""
public static synchronized long quiet() { return @PKG@.CfgFile.sgen(); }""",
r"""
public static void runReloads(java.util.HashSet rel) {
  if (rel == null || rel.size() == 0) return;
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) {
    if (!@PKG@.CfgFile.dirtyOk(f)) continue;
    try { rel.addAll(saveFile(f)); } catch (Throwable t) { @PKG@.CfgRows.warn("save of " + @PKG@.CfgRows.FILES[f] + " before a reload failed: " + t); }
  }
  long g0 = quiet();
  java.util.Iterator it = rel.iterator();
  boolean global = false;
  boolean ran = false;
  while (it.hasNext()) {
    String spec = (String) it.next();
    if (spec == null || spec.length() == 0) continue;
    if (spec.equals(@PKG@.CfgRows.RELOAD)) global = true;
    ran = true;
    try { @PKG@.CfgRows.call(spec, @PKG@.CfgRows.SIG0, new Object[0]); }
    catch (Throwable t) { @PKG@.CfgRows.warn("reload routine " + spec + " failed: " + t); }
  }
  if (ran) { try { @PKG@.CfgFile.reassert(g0); } catch (Throwable t) { @PKG@.CfgRows.warn("could not set pending values again after a reload: " + t); } }
  if (global) clampCheck();
}""",
r"""
public void run() {
  try {
    if (this.sleepFirst && this.delay > 0L) { try { Thread.sleep(this.delay); } catch (InterruptedException e) { } }
    if (this.idx < 0) { @PKG@.CfgFile.logDone(); @PKG@.CfgLog.flush(); return; }
    runReloads(saveFile(this.idx));
  } catch (Throwable t) { @PKG@.CfgRows.warn("config save task failed: " + t); }
}""",
]

# ================================================================================================================ Java: CfgFn, early part
# Compiled right after the CfgFile helpers and BEFORE the CfgFile state methods (kit 1.1): CfgFile.handApply runs the kit's own table
# checks (entryErr / tvalue) on hand-edited lines. Only CfgRows is referenced here. checkHook calls mod code and is never called while
# a kit monitor is held.
FN_EARLY = [
r"""
public static String checkHook(int i, String key, String value) {
  if (@PKG@.CfgRows.BCHECK[i].length() == 0) return null;
  try {
    Object o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCHECK[i], @PKG@.CfgRows.SIG_SS, new Object[] { key, value });
    if (o instanceof String && ((String) o).length() > 0) return (String) o;
    return null;
  } catch (Throwable t) { @PKG@.CfgRows.warn("check " + @PKG@.CfgRows.BCHECK[i] + " failed: " + t); return "This value could not be checked - see the server log."; }
}""",
r"""
public static String[] cols(int i) {
  String[] p = @PKG@.CfgRows.OPTS[i].split(";");
  if (p.length < 3) return new String[] { "Value" };
  return p[2].split("\\|");
}""",
r"""
public static String colType(int i, int c) {
  String[] p = @PKG@.CfgRows.OPTS[i].split(";");
  String[] ts = p[0].split("\\|");
  if (ts.length == 0) return "text";
  if (c < ts.length) return ts[c].trim();
  return ts[ts.length - 1].trim();
}""",
r"""
public static String entryErr(int i, String e) {
  if (e == null) return "No entry given.";
  String s = e.trim();
  if (s.length() == 0 || s.length() > 120) return "An entry must be 1 to 120 characters.";
  for (int k = 0; k < s.length(); k++) {
    char c = s.charAt(k);
    if (c <= ' ' || c == '=' || c == ':' || c == '#' || c == '!' || c == '[' || c == ']' || c == '\\' || c == '|' || c > 0x7e) return "Not a valid entry: " + s + ".";
  }
  int m = @PKG@.CfgRows.BENT[i];
  if (s.indexOf('*') >= 0) {
    if (m != 2) return "No * in " + @PKG@.CfgRows.LABELS[i] + ".";
    if (s.indexOf('*') != s.length() - 1) return "A * may only end an entry.";
    if (s.length() == 1) return "A lone * would match every item.";
    return null;
  }
  if ((m == 1 || m == 2) && !@PKG@.CfgRows.itemOk(s)) return "Unknown item: " + s + ".";
  return null;
}""",
# kit 1.1: a text column's length limit. A table with an int/dec column uses min/max for those numbers, so its text stays at 200; a
# table without one takes the row max as its text length (emit() allows 1-2000), 200 when it has no max
r"""
public static int textMax(int i) {
  String[] ts = @PKG@.CfgRows.OPTS[i].split(";")[0].split("\\|");
  for (int k = 0; k < ts.length; k++) { String t = ts[k].trim(); if (t.equals("int") || t.equals("dec")) return 200; }
  if (@PKG@.CfgRows.MAXS[i].length() == 0) return 200;
  try {
    int n = new java.math.BigDecimal(@PKG@.CfgRows.MAXS[i]).intValue();
    if (n < 1) return 200;
    if (n > 2000) return 2000;
    return n;
  } catch (Throwable t) { return 200; }
}""",
# kit 1.1: a 1-column table's value is the one column as typed ('|' included), never split
r"""
public static String[] tvalue(int i, String v) {
  String[] cn = cols(i);
  String x = v;
  if (x == null) x = "";
  String[] parts = null;
  if (cn.length == 1) parts = new String[] { x };
  else parts = x.split("\\|", -1);
  if (parts.length != cn.length) {
    StringBuilder sb = new StringBuilder();
    for (int c = 0; c < cn.length; c++) { if (c > 0) sb.append(" | "); sb.append(cn[c]); }
    return @PKG@.CfgRows.no("Needs " + cn.length + " value(s): " + sb.toString() + ".");
  }
  StringBuilder out = new StringBuilder();
  String sep = @PKG@.CfgRows.BSEP[i];
  int tmax = textMax(i);
  for (int c = 0; c < cn.length; c++) {
    String p = parts[c].trim();
    String ty = colType(i, c);
    if (ty.equals("int")) {
      java.math.BigDecimal n = @PKG@.CfgRows.num(i, p);
      if (n == null || !@PKG@.CfgRows.isInt(n) || !@PKG@.CfgRows.inb(i, n)) return @PKG@.CfgRows.no(cn[c] + ": " + @PKG@.CfgRows.rangeText(i, "a whole number"));
      p = n.toBigInteger().toString();
    } else if (ty.equals("dec")) {
      java.math.BigDecimal n = @PKG@.CfgRows.num(i, p);
      if (n == null || !@PKG@.CfgRows.inb(i, n)) return @PKG@.CfgRows.no(cn[c] + ": " + @PKG@.CfgRows.rangeText(i, "a number"));
      p = @PKG@.CfgRows.canonDec(n);
    } else if (ty.equals("bool")) {
      String b = p.toLowerCase();
      if (b.equals("true") || b.equals("on") || b.equals("yes") || b.equals("1")) p = "true";
      else if (b.equals("false") || b.equals("off") || b.equals("no") || b.equals("0")) p = "false";
      else return @PKG@.CfgRows.no(cn[c] + " must be ON or OFF.");
    } else {
      if (p.length() > tmax) return @PKG@.CfgRows.no(cn[c] + " is too long (" + tmax + " characters at most).");
      if (cn.length > 1 && sep.length() > 0 && p.indexOf(sep) >= 0) return @PKG@.CfgRows.no(cn[c] + " cannot contain '" + sep + "'.");
      for (int q = 0; q < p.length(); q++) if (p.charAt(q) < ' ') return @PKG@.CfgRows.no(cn[c] + " must be one line.");
    }
    if (c > 0) out.append('|');
    out.append(p);
  }
  return @PKG@.CfgRows.ok(out.toString());
}""",
# a table value in a message: columns shown as "a / b"; a 1-column value exactly as it is
r"""
public static String shown(int i, String v) {
  if (v == null) return "";
  if (@PKG@.CfgRows.oneCol(i)) return v;
  return v.replace("|", " / ");
}""",
]

# Compiled after the CfgFile state methods and before CfgSaveTask (kit 1.1). Runs OUTSIDE every kit lock: the save task calls it after
# saveLocked returns, the reload op on its own thread between handApply and queuing the reloads.
FN_MID = [
# the check= hooks of hand-edited table lines that passed the kit's own checks (handApply queued and held them): refused -> stays held
# + invalid, else accepted (the hold dropped) + ok + the row's reload routine (not for a restart table); a "?question" answer counts as
# accepted (nobody to ask). The log line is the hook's verdict on that line; memory changes only while the line is still the entry's
# newest change (CfgFile.holdIf / unholdIf with the queued String[] itself)
r"""
public static void handChecks(int f, java.util.ArrayList checks, java.util.HashSet rel) {
  if (checks == null || checks.size() == 0) return;
  java.util.ArrayList logs = new java.util.ArrayList();
  for (int k = 0; k < checks.size(); k++) {
    String[] c = (String[]) checks.get(k);
    int i = Integer.parseInt(c[7]);
    String chk = checkHook(i, c[4], c[3]);
    if (chk != null && !chk.startsWith("?")) {
      @PKG@.CfgFile.holdIf(f, c);
      logs.add(new String[] { c[4], c[5], c[6], "invalid" });
    } else {
      @PKG@.CfgFile.unholdIf(f, c);
      logs.add(new String[] { c[4], c[5], c[6], "ok" });
      if (!@PKG@.CfgRows.flag(i, "restart")) rel.add(@PKG@.CfgRows.BNAME[i]);
    }
  }
  @PKG@.CfgLog.addFile(logs);
  @PKG@.CfgFile.logSoon();
}""",
]

# ================================================================================================================ Java: CfgFn (the op dispatcher)
FN_JAVA = [
r"""public static Object[] R(String s, String v, String m) { return new Object[] { s, v, m }; }""",
r"""
public static String S(Object[] a, int k) {
  if (a.length <= k) return null;
  Object o = a[k];
  if (o instanceof String) return (String) o;
  return null;
}""",
r"""
public static java.util.UUID U(Object[] a, int k) {
  if (a.length <= k) return null;
  Object o = a[k];
  if (o instanceof java.util.UUID) return (java.util.UUID) o;
  return null;
}""",
r"""
public static boolean bad(Object[] a, int k, boolean uuid) {
  if (a.length <= k || a[k] == null) return false;
  if (uuid) return !(a[k] instanceof java.util.UUID);
  return !(a[k] instanceof String);
}""",
r"""
public static String brokenMsg(int f) {
  if (f < 0) return "The config file cannot be read - fix or delete it, then Reload.";
  return @PKG@.CfgRows.FILES[f] + " cannot be read - fix or delete it, then Reload.";
}""",
r"""
public static String current(int i) {
  try {
    if (@PKG@.CfgRows.noValue(i)) return "";
    int k = @PKG@.CfgRows.BK[i];
    if (k == 1) { String p = @PKG@.CfgFile.pendv(i); if (p != null) return p; return @PKG@.CfgRows.fieldGet(i); }
    if (k == 2) return @PKG@.CfgRows.fromFile(i, @PKG@.CfgFile.value(@PKG@.CfgRows.BF[i], @PKG@.CfgRows.BFK[i]));
    if (k == 3) {
      Object o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customGet", @PKG@.CfgRows.SIG_S, new Object[] { @PKG@.CfgRows.KEYS[i] });
      if (o instanceof String) return (String) o;
      return @PKG@.CfgRows.DEFS[i];
    }
    return @PKG@.CfgRows.DEFS[i];
  } catch (Throwable e) { @PKG@.CfgRows.warn("could not read " + @PKG@.CfgRows.KEYS[i] + ": " + e); return null; }
}""",
r"""
public static void afterHook(int i) {
  if (@PKG@.CfgRows.BAFTER[i].length() == 0) return;
  try { @PKG@.CfgRows.call(@PKG@.CfgRows.BAFTER[i], @PKG@.CfgRows.SIG_S, new Object[] { @PKG@.CfgRows.KEYS[i] }); }
  catch (Throwable t) { @PKG@.CfgRows.warn("after-set hook " + @PKG@.CfgRows.BAFTER[i] + " failed: " + t); }
}""",
r"""
public static String withHelp(String q, int i) {
  String h = @PKG@.CfgRows.HELPS[i];
  if (h.length() > 0) q = q + " " + h;
  return @PKG@.CfgRows.clip(q, 200);
}""",
# spec 1.4.2 / 3: danger rows confirm; part rows only when switched OFF; confirm= refines WHEN a danger row asks (emit() refuses it on
# a row without danger, on/off on non-bool rows, up/down on non-int/dec rows); a check hook's "?question" always asks
r"""
public static String needConfirm(int i, String old, String nv, String chk) {
  if (chk != null && chk.startsWith("?")) return @PKG@.CfgRows.clip(chk.substring(1), 200);
  if (!@PKG@.CfgRows.flag(i, "danger")) return null;
  int p = @PKG@.CfgRows.BCONF[i];
  boolean isBool = @PKG@.CfgRows.TYPES[i].equals("bool");
  if (p == 6) return null;
  if (p == 0 && @PKG@.CfgRows.flag(i, "part") && isBool && nv.equals("true")) return null;
  if (p == 1 && isBool && !nv.equals("true")) return null;
  if (p == 2 && isBool && !nv.equals("false")) return null;
  if (p == 3 || p == 4) {
    java.math.BigDecimal a = @PKG@.CfgRows.num(i, old);
    java.math.BigDecimal b = @PKG@.CfgRows.num(i, nv);
    if (a != null && b != null) {
      if (p == 3 && b.compareTo(a) <= 0) return null;
      if (p == 4 && b.compareTo(a) >= 0) return null;
    }
  }
  String l = @PKG@.CfgRows.LABELS[i];
  if (isBool && nv.equals("false")) return withHelp("Turn " + l + " OFF for everyone on this server?", i);
  if (isBool) return withHelp("Turn " + l + " ON for everyone on this server?", i);
  return withHelp("Change " + l + " from " + @PKG@.CfgRows.disp(i, old) + " to " + @PKG@.CfgRows.disp(i, nv) + "?", i);
}""",
r"""
public static String okMsg(int i, String v, String st) {
  String l = @PKG@.CfgRows.LABELS[i] + ": " + @PKG@.CfgRows.disp(i, v);
  if ("restart".equals(st)) return l + " - saved, applies after a server restart.";
  if (@PKG@.CfgRows.flag(i, "new")) return l + " - saved (applies to new ones).";
  return l + " - saved (applies now).";
}""",
# the one apply path for scalar rows (menu, command, import, restore, undo); validation and confirm happened before
r"""
public static Object[] applyRow(int i, String nv, String old, java.util.UUID who, String name, String via, String stamp) {
  int k = @PKG@.CfgRows.BK[i];
  int f = @PKG@.CfgRows.BF[i];
  String nm = @PKG@.CfgLog.nameOf(who, name);
  if (f >= 0 && @PKG@.CfgFile.isBroken(f)) return R("error", null, brokenMsg(f));
  boolean rs = @PKG@.CfgRows.flag(i, "restart");
  String st = "ok";
  if (rs) st = "restart";
  if (k == 1 || k == 2) {
    boolean done = false;
    try { done = @PKG@.CfgFile.setRow(i, nv, @PKG@.CfgRows.fileText(i, nv), stamp, nm, via, k == 1 && !rs); }
    catch (Throwable t) { @PKG@.CfgRows.warn("could not apply " + @PKG@.CfgRows.KEYS[i] + ": " + t); return R("error", null, "Could not apply " + @PKG@.CfgRows.LABELS[i] + " - see the server log."); }
    if (!done) return R("error", null, brokenMsg(f));
    @PKG@.CfgLog.add(who, nm, via, @PKG@.CfgRows.KEYS[i], old, nv, st);
    @PKG@.CfgFile.saveSoon(f);
    if (k == 1) afterHook(i);
    return R(st, nv, okMsg(i, nv, st));
  }
  if (k == 3) {
    Object o = null;
    try { o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customSet", @PKG@.CfgRows.SIG_SS, new Object[] { @PKG@.CfgRows.KEYS[i], nv }); }
    catch (Throwable t) { @PKG@.CfgRows.warn("customSet " + @PKG@.CfgRows.KEYS[i] + " failed: " + t); return R("error", null, "Could not apply " + @PKG@.CfgRows.LABELS[i] + " - see the server log."); }
    if (!(o instanceof Object[])) return R("error", null, "Could not apply " + @PKG@.CfgRows.LABELS[i] + " - see the server log.");
    Object[] r = (Object[]) o;
    String rst = S(r, 0);
    if (rst == null) rst = "error";
    String rm = S(r, 2);
    if (!rst.equals("ok") && !rst.equals("restart")) { if (rm == null) rm = "Not changed."; return R(rst, S(r, 1), rm); }
    String val = S(r, 1);
    if (val == null) val = nv;
    if (r.length > 3 && r[3] instanceof String[] && f >= 0) {
      String rl = "";
      if (!rs && !rst.equals("restart")) rl = @PKG@.CfgRows.RELOAD;
      @PKG@.CfgFile.editLines(f, (String[]) r[3], stamp, nm, via, @PKG@.CfgRows.KEYS[i], rl);
      @PKG@.CfgFile.saveSoon(f);
    } else @PKG@.CfgFile.logSoon();
    @PKG@.CfgFile.bump();
    @PKG@.CfgLog.add(who, nm, via, @PKG@.CfgRows.KEYS[i], old, val, rst);
    if (rm == null) rm = okMsg(i, val, rst);
    return R(rst, val, rm);
  }
  return R("bad", null, @PKG@.CfgRows.LABELS[i] + " has no single value.");
}""",
r"""
public static Object[] set(String key, String value, java.util.UUID who, String name, String confirm, String via) {
  int i = @PKG@.CfgRows.index(key);
  if (i < 0) return R("unknown", null, "Unknown setting: " + key + ".");
  if (@PKG@.CfgRows.noValue(i)) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " has no single value.");
  if (@PKG@.CfgRows.flag(i, "ro")) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " is read-only.");
  if (!@PKG@.CfgRows.allowed(who, via)) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  int f = @PKG@.CfgRows.BF[i];
  if (f >= 0 && @PKG@.CfgFile.isBroken(f)) return R("error", null, brokenMsg(f));
  String in = value;
  if (in == null) in = @PKG@.CfgRows.DEFS[i];
  String[] v = @PKG@.CfgRows.validate(i, in);
  if (v[0] == null) return R("bad", null, v[1]);
  String nv = v[0];
  String old = current(i);
  if (old == null) return R("error", null, "Could not read " + @PKG@.CfgRows.LABELS[i] + " - see the server log.");
  if (@PKG@.CfgRows.same(i, old, nv)) return R("ok", nv, @PKG@.CfgRows.LABELS[i] + " is already " + @PKG@.CfgRows.disp(i, nv) + ".");
  String chk = checkHook(i, key, nv);
  if (chk != null && !chk.startsWith("?")) return R("bad", null, chk);
  if (!"yes".equals(confirm)) { String q = needConfirm(i, old, nv, chk); if (q != null) return R("confirm", null, q); }
  return applyRow(i, nv, old, who, name, via, @PKG@.CfgHist.stamp());
}""",
r"""
public static Object opSet(Object[] a) {
  if (a.length < 7 || S(a, 1) == null || bad(a, 2, false) || bad(a, 3, true) || bad(a, 4, false) || bad(a, 5, false) || bad(a, 6, false)) return null;
  String via = S(a, 6);
  if (via == null || via.length() == 0) via = "menu";
  return set(S(a, 1), S(a, 2), U(a, 3), S(a, 4), S(a, 5), via);
}""",
r"""
public static Object opGet(Object[] a) {
  String k = S(a, 1);
  int i = @PKG@.CfgRows.index(k);
  if (i < 0) return null;
  return current(i);
}""",
# ---- tables (spec 1.3 keys/tset/add/remove, 1.4.6 log form); cols / colType / entryErr / textMax / tvalue / shown are in FN_EARLY
r"""
public static String entryValue(int i, String e) {
  try {
    if (@PKG@.CfgRows.BK[i] == 3) {
      Object o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customGet", @PKG@.CfgRows.SIG_S, new Object[] { @PKG@.CfgRows.KEYS[i] + "[" + e + "]" });
      if (o instanceof String) return (String) o;
      return null;
    }
    return @PKG@.CfgFile.colsFromFile(i, @PKG@.CfgFile.value(@PKG@.CfgRows.BF[i], @PKG@.CfgRows.BFK[i] + e));
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not read " + @PKG@.CfgRows.KEYS[i] + "[" + e + "]: " + t); return null; }
}""",
r"""
public static String[] entryKeys(int i) {
  try {
    if (@PKG@.CfgRows.BK[i] == 3) {
      Object o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customKeys", @PKG@.CfgRows.SIG_S, new Object[] { @PKG@.CfgRows.KEYS[i] });
      if (o instanceof String[]) return (String[]) o;
      return new String[0];
    }
    String p = @PKG@.CfgRows.BFK[i];
    String[] full = @PKG@.CfgFile.entries(@PKG@.CfgRows.BF[i], p);
    String[] r = new String[full.length];
    for (int k = 0; k < full.length; k++) r[k] = full[k].substring(p.length());
    return r;
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not list " + @PKG@.CfgRows.KEYS[i] + ": " + t); return new String[0]; }
}""",
r"""
public static Object opKeys(Object[] a) {
  String tk = S(a, 1);
  int i = @PKG@.CfgRows.index(tk);
  if (i < 0 || !@PKG@.CfgRows.isTable(i) || bad(a, 2, false)) return null;
  String flt = S(a, 2);
  if (flt == null) flt = "";
  flt = flt.trim().toLowerCase();
  String[] ek = entryKeys(i);
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  for (int k = 0; k < ek.length && ks.size() < 500; k++) {
    String v = entryValue(i, ek[k]);
    if (v == null && @PKG@.CfgRows.BK[i] != 3) continue;   // kit 1.1: a key-family entry removed between the listing and this read
    if (v == null) v = "";
    if (flt.length() > 0 && ek[k].toLowerCase().indexOf(flt) < 0 && v.toLowerCase().indexOf(flt) < 0) continue;
    ks.add(ek[k]);
    vs.add(v);
  }
  String[] keys = (String[]) ks.toArray(new String[0]);
  String[] labels = (String[]) ks.toArray(new String[0]);
  String[] vals = (String[]) vs.toArray(new String[0]);
  return new Object[] { keys, labels, vals };
}""",
# apply one validated table change (no checks here): nv == null removes the entry
r"""
public static Object[] tableApply(int i, String e, String cur, String nv, java.util.UUID who, String name, String via, String stamp) {
  String nm = @PKG@.CfgLog.nameOf(who, name);
  String tk = @PKG@.CfgRows.KEYS[i] + "[" + e + "]";
  String st = "ok";
  if (@PKG@.CfgRows.flag(i, "restart")) st = "restart";
  if (@PKG@.CfgRows.BK[i] == 3) {
    Object o = null;
    try { o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customSet", @PKG@.CfgRows.SIG_SS, new Object[] { tk, nv }); }
    catch (Throwable t) { @PKG@.CfgRows.warn("customSet " + tk + " failed: " + t); return R("error", null, "Could not change " + @PKG@.CfgRows.LABELS[i] + " - see the server log."); }
    if (!(o instanceof Object[])) return R("error", null, "Could not change " + @PKG@.CfgRows.LABELS[i] + " - see the server log.");
    Object[] r = (Object[]) o;
    String rst = S(r, 0);
    if (!"ok".equals(rst) && !"restart".equals(rst)) { String m = S(r, 2); if (m == null) m = "Not changed."; if (rst == null) rst = "error"; return R(rst, null, m); }
    if ("restart".equals(rst)) st = "restart";
    int f = @PKG@.CfgRows.BF[i];
    if (r.length > 3 && r[3] instanceof String[] && f >= 0) {
      String rl = "";
      if (!st.equals("restart")) rl = @PKG@.CfgRows.RELOAD;
      @PKG@.CfgFile.editLines(f, (String[]) r[3], stamp, nm, via, tk, rl);
      @PKG@.CfgFile.saveSoon(f);
    } else @PKG@.CfgFile.logSoon();
    @PKG@.CfgFile.bump();
  } else {
    if (!@PKG@.CfgFile.setEntry(i, @PKG@.CfgRows.BFK[i] + e, @PKG@.CfgFile.colsToFile(i, nv), stamp, nm, via, tk)) return R("error", null, brokenMsg(@PKG@.CfgRows.BF[i]));
    @PKG@.CfgFile.saveSoon(@PKG@.CfgRows.BF[i]);
  }
  String o2 = cur;
  if (o2 == null) o2 = "(none)";
  String n2 = nv;
  if (n2 == null) n2 = "(none)";
  @PKG@.CfgLog.add(who, nm, via, tk, o2, n2, st);
  String l = @PKG@.CfgRows.LABELS[i];
  String tail = ".";
  if (st.equals("restart")) tail = " - saved, applies after a server restart.";
  if (nv == null) return R(st, "", l + ": " + e + " removed" + tail);
  if (cur == null) return R(st, nv, l + ": " + e + " added (" + shown(i, nv) + ")" + tail);
  return R(st, nv, l + ": " + e + " set to " + shown(i, nv) + tail);
}""",
# mode 0 = tset, 1 = add, 2 = remove
r"""
public static Object[] tableChange(int i, String entry, String value, int mode, java.util.UUID who, String name, String confirm, String via) {
  if (!@PKG@.CfgRows.isTable(i)) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " is not a table.");
  if (@PKG@.CfgRows.flag(i, "ro")) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " is read-only.");
  if (!@PKG@.CfgRows.allowed(who, via)) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  int f = @PKG@.CfgRows.BF[i];
  if (f >= 0 && @PKG@.CfgFile.isBroken(f)) return R("error", null, brokenMsg(f));
  String ee = entryErr(i, entry);
  if (ee != null) return R("bad", null, ee);
  String e = entry.trim();
  String cur = entryValue(i, e);
  String l = @PKG@.CfgRows.LABELS[i];
  if (mode == 1 && cur != null) return R("bad", null, e + " is already in " + l + " - use Set to change it.");
  if (mode != 1 && cur == null) return R("bad", null, e + " is not in " + l + ".");
  String nv = null;
  if (mode != 2) {
    String[] tv = tvalue(i, value);
    if (tv[0] == null) return R("bad", null, tv[1]);
    nv = tv[0];
    if (mode == 0 && nv.equals(cur)) return R("ok", nv, l + ": " + e + " is already " + shown(i, nv) + ".");
  }
  String tk = @PKG@.CfgRows.KEYS[i] + "[" + e + "]";
  String chk = checkHook(i, tk, nv);
  if (chk != null && !chk.startsWith("?")) return R("bad", null, chk);
  if (!"yes".equals(confirm)) {
    String q = null;
    if (chk != null) q = @PKG@.CfgRows.clip(chk.substring(1), 200);
    else if (@PKG@.CfgRows.flag(i, "danger") && @PKG@.CfgRows.BCONF[i] != 6) {
      if (mode == 2) q = "Remove " + e + " from " + l + "?";
      else if (mode == 1) q = "Add " + e + " to " + l + " (" + shown(i, nv) + ")?";
      else q = "Change " + e + " in " + l + " from " + shown(i, cur) + " to " + shown(i, nv) + "?";
      q = withHelp(q, i);
    }
    if (q != null) return R("confirm", null, q);
  }
  return tableApply(i, e, cur, nv, who, name, via, @PKG@.CfgHist.stamp());
}""",
r"""
public static Object opTable(Object[] a, int mode) {
  int base = 4;
  if (mode == 2) base = 3;
  if (a.length < base + 3 || S(a, 1) == null || bad(a, 2, false)) return null;
  if (mode != 2 && bad(a, 3, false)) return null;
  if (bad(a, base, true) || bad(a, base + 1, false) || bad(a, base + 2, false) || bad(a, base + 3, false)) return null;
  int i = @PKG@.CfgRows.index(S(a, 1));
  if (i < 0) return R("unknown", null, "Unknown table: " + S(a, 1) + ".");
  String via = S(a, base + 3);
  if (via == null || via.length() == 0) via = "menu";
  String v = null;
  if (mode != 2) v = S(a, 3);
  return tableChange(i, S(a, 2), v, mode, U(a, base), S(a, base + 1), S(a, base + 2), via);
}""",
# ---- actions: check= runs first (key, value null) and may refuse or ask "?question"; a danger action asks unless confirm=never.
# Kit 1.1: a value= action takes its typed value after via (a[6]); none given (a SkyyMenu 0.3 call) = the row default, else bad. The
# value is validated like a scalar row of the value type (the row's min / max / unit), passed to check= and to the method, shown in the
# confirm question and logged in the old column (new stays "(action)", status "done"). A plain action ignores a[6].
r"""
public static Object opAction(Object[] a) {
  if (a.length < 5 || S(a, 1) == null || bad(a, 2, true) || bad(a, 3, false) || bad(a, 4, false) || bad(a, 5, false) || bad(a, 6, false)) return null;
  int i = @PKG@.CfgRows.index(S(a, 1));
  if (i < 0) return R("unknown", null, "Unknown action: " + S(a, 1) + ".");
  if (!@PKG@.CfgRows.TYPES[i].equals("action")) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " is not an action.");
  java.util.UUID who = U(a, 2);
  String via = S(a, 5);
  if (via == null || via.length() == 0) via = "menu";
  if (!@PKG@.CfgRows.allowed(who, via)) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  if (@PKG@.CfgRows.flag(i, "ro")) return R("bad", null, @PKG@.CfgRows.LABELS[i] + " is read-only.");
  String vt = @PKG@.CfgRows.VTYPES[i];
  String val = null;
  if (vt.length() > 0) {
    String in = S(a, 6);
    if (in == null) {
      if (@PKG@.CfgRows.DEFS[i].length() == 0) return R("bad", null, "Type a value for " + @PKG@.CfgRows.LABELS[i] + " first.");
      in = @PKG@.CfgRows.DEFS[i];
    }
    String[] v = @PKG@.CfgRows.validateAs(i, vt, in);
    if (v[0] == null) return R("bad", null, v[1]);
    val = v[0];
  }
  String chk = checkHook(i, @PKG@.CfgRows.KEYS[i], val);
  if (chk != null && !chk.startsWith("?")) return R("bad", null, chk);
  if (!"yes".equals(S(a, 4))) {
    if (chk != null) return R("confirm", null, @PKG@.CfgRows.clip(chk.substring(1), 200));
    if (@PKG@.CfgRows.flag(i, "danger") && @PKG@.CfgRows.BCONF[i] != 6) {
      String q = @PKG@.CfgRows.OPTS[i];
      if (val != null) q = q + " (" + @PKG@.CfgRows.dispAs(i, vt, val) + ")";
      return R("confirm", null, withHelp(q + "?", i));
    }
  }
  String nm = @PKG@.CfgLog.nameOf(who, S(a, 3));
  Object o = null;
  try {
    String spec = @PKG@.CfgRows.BCLS[i] + "." + @PKG@.CfgRows.BNAME[i];
    if (vt.length() > 0) o = @PKG@.CfgRows.call(spec, @PKG@.CfgRows.SIG_USS, new Object[] { who, nm, val });
    else o = @PKG@.CfgRows.call(spec, @PKG@.CfgRows.SIG_US, new Object[] { who, nm });
  }
  catch (Throwable t) { @PKG@.CfgRows.warn("action " + @PKG@.CfgRows.KEYS[i] + " failed: " + t); return R("error", null, @PKG@.CfgRows.OPTS[i] + " failed - see the server log."); }
  if (!(o instanceof Object[])) return R("error", null, @PKG@.CfgRows.OPTS[i] + " failed - see the server log.");
  Object[] r = (Object[]) o;
  String st = S(r, 0);
  if (st == null) st = "error";
  String m = S(r, 2);
  if (m == null) m = "";
  if (st.equals("ok") || st.equals("restart")) {
    String ov = "";
    if (val != null) ov = val;
    @PKG@.CfgFile.bump();
    @PKG@.CfgLog.add(who, nm, via, @PKG@.CfgRows.KEYS[i], ov, "(action)", "done");
    @PKG@.CfgFile.logSoon();
  }
  return R(st, S(r, 1), m);
}""",
# ---- reload (hand edits): read on the caller thread, merge in memory, the save task writes and runs the reload routines. Kit 1.1:
# the read + merge wait for a save that is writing (CfgSaveTask.readMerge); the check= hooks run after it, with no kit lock held
r"""
public static Object opReload(Object[] a) {
  if (a.length < 3 || bad(a, 1, true) || bad(a, 2, false) || bad(a, 3, false)) return null;
  String via = S(a, 3);
  if (via == null || via.length() == 0) via = "menu";
  if (!@PKG@.CfgRows.allowed(U(a, 1), via)) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  int changed = 0;
  String err = null;
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) {
    try {
      Object[] h = @PKG@.CfgSaveTask.readMerge(f);
      @PKG@.CfgLog.addFile((java.util.ArrayList) h[0]);
      java.util.HashSet rs = (java.util.HashSet) h[1];
      handChecks(f, (java.util.ArrayList) h[3], rs);
      @PKG@.CfgFile.addReloads(f, rs);
      changed += ((Integer) h[2]).intValue();
      @PKG@.CfgFile.force(f);
      @PKG@.CfgFile.saveNowSoon(f);
    } catch (Throwable t) {
      if (@PKG@.CfgFile.markBroken(f, t)) @PKG@.CfgRows.warn(@PKG@.CfgRows.FILES[f] + " cannot be read - in-game changes to it are refused until it can be read again: " + t);
      if (err == null) err = brokenMsg(f);
    }
  }
  if (err != null) return R("error", null, err);
  if (changed == 0) return R("ok", "0", "Read the files again: nothing was changed by hand.");
  String w = " values";
  if (changed == 1) w = " value";
  return R("ok", String.valueOf(changed), "Read the files again: " + changed + w + " changed by hand (see Changes).");
}""",
# ---- export / import (spec 1.4.7)
r"""
public static String[] defEntries(int i) {
  int f = @PKG@.CfgRows.BF[i];
  String[] d = @PKG@.CfgRows.defLines(f);
  if (d.length == 0) return null;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int k = 0; k < d.length; k++) l.add(d[k]);
  java.util.HashMap m = @PKG@.CfgFile.parseVals(l);
  java.util.ArrayList r = new java.util.ArrayList();
  String p = @PKG@.CfgRows.BFK[i];
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k.startsWith(p) && k.length() > p.length()) r.add(k.substring(p.length()) + "=" + @PKG@.CfgFile.colsFromFile(i, (String) m.get(k))); }
  java.util.Collections.sort(r);
  return (String[]) r.toArray(new String[0]);
}""",
r"""
public static String encode(String text) throws Exception {
  byte[] raw = text.getBytes("UTF-8");
  java.util.zip.Deflater d = new java.util.zip.Deflater(9);
  d.setInput(raw);
  d.finish();
  java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
  byte[] buf = new byte[4096];
  while (!d.finished()) { int n = d.deflate(buf); bos.write(buf, 0, n); }
  d.end();
  java.util.zip.CRC32 c = new java.util.zip.CRC32();
  c.update(raw, 0, raw.length);
  String hx = Long.toHexString(c.getValue());
  while (hx.length() < 8) hx = "0" + hx;
  return "SKYY1." + @PKG@.CfgRows.MOD + "." + java.util.Base64.getUrlEncoder().withoutPadding().encodeToString(bos.toByteArray()) + "." + hx;
}""",
r"""
public static Object opExport(Object[] a) {
  if (bad(a, 1, false)) return null;
  String scope = S(a, 1);
  if (scope == null || scope.length() == 0) scope = "changed";
  if (!scope.equals("changed") && !scope.equals("all")) return null;
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) if (@PKG@.CfgFile.isBroken(f)) return null;
  boolean all = scope.equals("all");
  StringBuilder sb = new StringBuilder();
  sb.append("_mod=").append(@PKG@.CfgRows.MOD).append('\n');
  sb.append("_ver=").append(@PKG@.CfgRows.VERSION).append('\n');
  sb.append("_date=").append(@PKG@.CfgLog.now()).append('\n');
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.flag(i, "ro") || @PKG@.CfgRows.TYPES[i].equals("link") || @PKG@.CfgRows.TYPES[i].equals("action")) continue;
    if (@PKG@.CfgRows.isTable(i)) {
      String[] ek = entryKeys(i);
      java.util.ArrayList cur = new java.util.ArrayList();
      for (int k = 0; k < ek.length; k++) { String v = entryValue(i, ek[k]); if (v != null) cur.add(ek[k] + "=" + v); }
      java.util.Collections.sort(cur);
      if (!all && @PKG@.CfgRows.BK[i] == 2) {
        String[] de = defEntries(i);
        if (de != null && de.length == cur.size()) {
          boolean eq = true;
          for (int k = 0; k < de.length; k++) if (!de[k].equals((String) cur.get(k))) eq = false;
          if (eq) continue;
        }
      }
      sb.append("_table=").append(@PKG@.CfgRows.KEYS[i]).append('\n');
      for (int k = 0; k < cur.size(); k++) {
        String s = (String) cur.get(k);
        int q = s.indexOf('=');
        sb.append(@PKG@.CfgRows.KEYS[i]).append('[').append(s.substring(0, q)).append("]=").append(@PKG@.CfgRows.oneLine(s.substring(q + 1))).append('\n');
      }
      continue;
    }
    String cur = current(i);
    if (cur == null) return null;
    if (!all && @PKG@.CfgRows.same(i, cur, @PKG@.CfgRows.DEFS[i])) continue;
    sb.append(@PKG@.CfgRows.KEYS[i]).append('=').append(@PKG@.CfgRows.oneLine(cur)).append('\n');
  }
  try { return encode(sb.toString()); } catch (Throwable t) { @PKG@.CfgRows.warn("export failed: " + t); return null; }
}""",
r"""
public static boolean alias(String m) {
  for (int k = 0; k < @PKG@.CfgRows.ALIASES.length; k++) if (@PKG@.CfgRows.ALIASES[k].equals(m)) return true;
  return false;
}""",
# { text, null } or { null, why }
r"""
public static String[] decode(String code) {
  if (code == null) return @PKG@.CfgRows.no("No code given.");
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < code.length(); k++) { char c = code.charAt(k); if (!Character.isWhitespace(c)) sb.append(c); }
  String c = sb.toString();
  if (c.length() > 3000000) return @PKG@.CfgRows.no("That code is too long.");
  if (!c.startsWith("SKYY1.")) return @PKG@.CfgRows.no("That is not a SkyWynn setup code (it must start with SKYY1.).");
  String[] p = c.split("\\.");
  if (p.length != 4) return @PKG@.CfgRows.no("The code is damaged (it needs 4 parts).");
  if (!p[1].equals(@PKG@.CfgRows.MOD) && !alias(p[1])) return @PKG@.CfgRows.no("This code is for " + p[1] + ", not " + @PKG@.CfgRows.MOD + ".");
  byte[] raw = null;
  try {
    byte[] z = java.util.Base64.getUrlDecoder().decode(p[2]);
    java.util.zip.Inflater inf = new java.util.zip.Inflater();
    inf.setInput(z);
    java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
    byte[] buf = new byte[4096];
    int guard = 0;
    while (!inf.finished() && guard < 100000) {
      int n = inf.inflate(buf);
      if (n == 0 && (inf.needsInput() || inf.needsDictionary())) break;
      bos.write(buf, 0, n);
      if (bos.size() > 4194304) { inf.end(); return @PKG@.CfgRows.no("That code is too big."); }
      guard++;
    }
    boolean fin = inf.finished();
    inf.end();
    if (!fin) return @PKG@.CfgRows.no("The code is damaged (cut off?).");
    raw = bos.toByteArray();
  } catch (Throwable t) { return @PKG@.CfgRows.no("The code is damaged."); }
  java.util.zip.CRC32 cr = new java.util.zip.CRC32();
  cr.update(raw, 0, raw.length);
  String hx = Long.toHexString(cr.getValue());
  while (hx.length() < 8) hx = "0" + hx;
  if (!hx.equalsIgnoreCase(p[3])) return @PKG@.CfgRows.no("The code is damaged (checksum does not match).");
  String text = null;
  try { text = new String(raw, "UTF-8"); } catch (Throwable t) { return @PKG@.CfgRows.no("The code is damaged."); }
  if (text.indexOf("_mod=" + p[1] + "\n") < 0 && !text.startsWith("_mod=" + p[1])) return @PKG@.CfgRows.no("The code is damaged (mod name).");
  return @PKG@.CfgRows.ok(text);
}""",
# a change plan: parallel lists; kind 0 scalar, 1 table add, 2 table set, 3 table remove
r"""
public static String planLine(int kind, int i, String e, String old, String nv) {
  String l = @PKG@.CfgRows.LABELS[i];
  if (kind == 0) return l + ": " + @PKG@.CfgRows.disp(i, old) + " -> " + @PKG@.CfgRows.disp(i, nv);
  if (kind == 1) return l + ": " + e + " added (" + shown(i, nv) + ")";
  if (kind == 3) return l + ": " + e + " removed";
  return l + ": " + e + " " + shown(i, old) + " -> " + shown(i, nv);
}""",
# shared by import and restore: values = scalar key -> value, tables = table key -> LinkedHashMap entry -> value (null = not in the plan)
r"""
public static Object[] plan(java.util.LinkedHashMap values, java.util.HashMap tables, java.util.ArrayList errors) {
  java.util.ArrayList kinds = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.ArrayList ents = new java.util.ArrayList();
  java.util.ArrayList olds = new java.util.ArrayList();
  java.util.ArrayList news = new java.util.ArrayList();
  java.util.ArrayList lines = new java.util.ArrayList();
  java.util.Iterator it = values.keySet().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    int i = @PKG@.CfgRows.index(key);
    String[] v = @PKG@.CfgRows.validate(i, (String) values.get(key));
    if (v[0] == null) { errors.add(@PKG@.CfgRows.LABELS[i] + ": " + v[1]); continue; }
    String chk = checkHook(i, key, v[0]);
    if (chk != null && !chk.startsWith("?")) { errors.add(@PKG@.CfgRows.LABELS[i] + ": " + chk); continue; }
    String old = current(i);
    if (old == null) { errors.add(@PKG@.CfgRows.LABELS[i] + ": could not be read"); continue; }
    if (@PKG@.CfgRows.same(i, old, v[0])) continue;
    kinds.add(Integer.valueOf(0)); rows.add(Integer.valueOf(i)); ents.add(""); olds.add(old); news.add(v[0]);
    lines.add(planLine(0, i, "", old, v[0]));
  }
  it = tables.keySet().iterator();
  while (it.hasNext()) {
    String tk = (String) it.next();
    int i = @PKG@.CfgRows.index(tk);
    java.util.LinkedHashMap want = (java.util.LinkedHashMap) tables.get(tk);
    java.util.Iterator et = want.keySet().iterator();
    while (et.hasNext()) {
      String e = (String) et.next();
      String ee = entryErr(i, e);
      if (ee != null) { errors.add(@PKG@.CfgRows.LABELS[i] + ": " + ee); continue; }
      String[] tv = tvalue(i, (String) want.get(e));
      if (tv[0] == null) { errors.add(@PKG@.CfgRows.LABELS[i] + " " + e + ": " + tv[1]); continue; }
      String chk = checkHook(i, tk + "[" + e + "]", tv[0]);
      if (chk != null && !chk.startsWith("?")) { errors.add(@PKG@.CfgRows.LABELS[i] + " " + e + ": " + chk); continue; }
      String cur = entryValue(i, e.trim());
      if (cur != null && cur.equals(tv[0])) continue;
      int kind = 2;
      if (cur == null) kind = 1;
      kinds.add(Integer.valueOf(kind)); rows.add(Integer.valueOf(i)); ents.add(e.trim()); olds.add(cur); news.add(tv[0]);
      lines.add(planLine(kind, i, e.trim(), cur, tv[0]));
    }
    String[] have = entryKeys(i);
    for (int k = 0; k < have.length; k++) {
      if (want.containsKey(have[k])) continue;
      String chk = checkHook(i, tk + "[" + have[k] + "]", null);
      if (chk != null && !chk.startsWith("?")) { errors.add(@PKG@.CfgRows.LABELS[i] + " " + have[k] + ": " + chk); continue; }
      kinds.add(Integer.valueOf(3)); rows.add(Integer.valueOf(i)); ents.add(have[k]); olds.add(entryValue(i, have[k])); news.add(null);
      lines.add(planLine(3, i, have[k], null, null));
    }
  }
  return new Object[] { kinds, rows, ents, olds, news, lines };
}""",
r"""
public static String joinLines(java.util.ArrayList l, int max) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < l.size() && k < max; k++) { if (k > 0) sb.append('\n'); sb.append((String) l.get(k)); }
  if (l.size() > max) sb.append("\nand ").append(l.size() - max).append(" more");
  return sb.toString();
}""",
# every change validated before, so only a broken file or a custom row can still fail here
r"""
public static String runPlan(Object[] pl, java.util.UUID who, String name, String via) {
  java.util.ArrayList kinds = (java.util.ArrayList) pl[0];
  String stamp = @PKG@.CfgHist.stamp();
  int failed = 0;
  String first = null;
  for (int k = 0; k < kinds.size(); k++) {
    int kind = ((Integer) kinds.get(k)).intValue();
    int i = ((Integer) ((java.util.ArrayList) pl[1]).get(k)).intValue();
    String e = (String) ((java.util.ArrayList) pl[2]).get(k);
    String old = (String) ((java.util.ArrayList) pl[3]).get(k);
    String nv = (String) ((java.util.ArrayList) pl[4]).get(k);
    Object[] r = null;
    if (kind == 0) r = applyRow(i, nv, old, who, name, via, stamp);
    else r = tableApply(i, e, old, nv, who, name, via, stamp);
    String st = (String) r[0];
    if (!st.equals("ok") && !st.equals("restart")) { failed++; if (first == null) first = @PKG@.CfgRows.LABELS[i] + ": " + r[2]; }
  }
  if (failed == 0) return null;
  return failed + " change(s) failed, first: " + first;
}""",
r"""
public static Object opImport(Object[] a) {
  if (a.length < 5 || S(a, 1) == null || bad(a, 2, true) || bad(a, 3, false) || S(a, 4) == null) return null;
  String mode = S(a, 4);
  if (!mode.equals("preview") && !mode.equals("apply")) return null;
  java.util.UUID who = U(a, 2);
  if (mode.equals("apply") && !@PKG@.CfgRows.allowed(who, "import")) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) if (@PKG@.CfgFile.isBroken(f)) return R("error", null, brokenMsg(f));
  String[] d = decode(S(a, 1));
  if (d[0] == null) return R("bad", null, d[1]);
  String[] ls = d[0].split("\n");
  java.util.LinkedHashMap values = new java.util.LinkedHashMap();
  java.util.HashMap tables = new java.util.LinkedHashMap();
  java.util.ArrayList skipped = new java.util.ArrayList();
  for (int k = 0; k < ls.length; k++) {
    String s = ls[k];
    int q = s.indexOf('=');
    if (q <= 0) continue;
    String key = s.substring(0, q);
    String val = s.substring(q + 1);
    if (key.equals("_table")) {
      int i = @PKG@.CfgRows.index(val);
      if (i < 0 || !@PKG@.CfgRows.isTable(i) || @PKG@.CfgRows.flag(i, "ro")) { skipped.add(val); continue; }
      if (!tables.containsKey(val)) tables.put(val, new java.util.LinkedHashMap());
      continue;
    }
    if (key.startsWith("_")) continue;
    int b = key.indexOf('[');
    if (b > 0 && key.endsWith("]")) {
      String tk = key.substring(0, b);
      Object t = tables.get(tk);
      if (t == null) { if (!skipped.contains(tk)) skipped.add(tk); continue; }
      ((java.util.LinkedHashMap) t).put(key.substring(b + 1, key.length() - 1), val);
      continue;
    }
    int i = @PKG@.CfgRows.index(key);
    if (i < 0 || @PKG@.CfgRows.noValue(i) || @PKG@.CfgRows.flag(i, "ro")) { skipped.add(key); continue; }
    values.put(key, val);
  }
  java.util.ArrayList errors = new java.util.ArrayList();
  Object[] pl = plan(values, tables, errors);
  if (errors.size() > 0) return R("bad", null, "Nothing was imported - " + errors.size() + " value(s) are not allowed here:\n" + joinLines(errors, 8));
  java.util.ArrayList lines = (java.util.ArrayList) pl[5];
  String skip = "";
  if (skipped.size() > 0) {
    StringBuilder sb = new StringBuilder("\nSkipped (not known or read-only here): ");
    for (int k = 0; k < skipped.size(); k++) { if (k > 0) sb.append(", "); sb.append((String) skipped.get(k)); }
    skip = sb.toString();
  }
  int n = lines.size();
  if (n == 0) return R("ok", "0", "Nothing to change - this server already has these values." + skip);
  if (mode.equals("preview")) return R("ok", String.valueOf(n), n + " change(s):\n" + joinLines(lines, 40) + skip);
  String fail = runPlan(pl, who, S(a, 3), "import");
  if (fail != null) return R("error", String.valueOf(n), "Imported with problems - " + fail + "\n" + joinLines(lines, 40) + skip);
  return R("ok", String.valueOf(n), "Imported " + n + " change(s):\n" + joinLines(lines, 40) + skip);
}""",
# ---- history (spec 1.4.5): restore touches only the one file the version belongs to
r"""
public static Object opRestore(Object[] a) {
  if (a.length < 5 || S(a, 1) == null || bad(a, 2, true) || bad(a, 3, false) || S(a, 4) == null) return null;
  String mode = S(a, 4);
  if (!mode.equals("preview") && !mode.equals("apply")) return null;
  String id = S(a, 1);
  java.util.UUID who = U(a, 2);
  int f = @PKG@.CfgHist.fileIdx(id);
  if (f < 0) return R("bad", null, "That version does not exist.");
  if (mode.equals("apply") && !@PKG@.CfgRows.allowed(who, "restore")) return R("denied", null, "Changing " + @PKG@.CfgRows.MOD + " needs " + @PKG@.CfgRows.NODE + ".");
  if (@PKG@.CfgFile.isBroken(f)) return R("error", null, brokenMsg(f));
  byte[] b = @PKG@.CfgHist.read(id);
  if (b == null) return R("bad", null, "That version no longer exists.");
  java.util.HashMap vals = null;
  try { vals = @PKG@.CfgFile.parseVals(@PKG@.CfgFile.split(new String(b, "ISO-8859-1"))); } catch (Throwable t) { return R("error", null, "That version cannot be read."); }
  java.util.LinkedHashMap values = new java.util.LinkedHashMap();
  java.util.HashMap tables = new java.util.LinkedHashMap();
  java.util.ArrayList skipped = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (@PKG@.CfgRows.BF[i] != f || @PKG@.CfgRows.flag(i, "ro")) continue;
    int k = @PKG@.CfgRows.BK[i];
    if (@PKG@.CfgRows.isTable(i)) {
      if (k != 2) { skipped.add(@PKG@.CfgRows.LABELS[i]); continue; }
      java.util.LinkedHashMap want = new java.util.LinkedHashMap();
      String p = @PKG@.CfgRows.BFK[i];
      java.util.Iterator it = vals.keySet().iterator();
      while (it.hasNext()) { String fk = (String) it.next(); if (fk.startsWith(p) && fk.length() > p.length()) want.put(fk.substring(p.length()), @PKG@.CfgFile.colsFromFile(i, (String) vals.get(fk))); }
      tables.put(@PKG@.CfgRows.KEYS[i], want);
      continue;
    }
    if (k == 1 || k == 2) { values.put(@PKG@.CfgRows.KEYS[i], @PKG@.CfgRows.fromFile(i, (String) vals.get(@PKG@.CfgRows.BFK[i]))); continue; }
    if (k == 3) {
      String v = null;
      try { Object o = @PKG@.CfgRows.call(@PKG@.CfgRows.BCLS[i] + ".customRead", @PKG@.CfgRows.SIG_SM, new Object[] { @PKG@.CfgRows.KEYS[i], vals }); if (o instanceof String) v = (String) o; } catch (Throwable t) { v = null; }
      if (v == null) skipped.add(@PKG@.CfgRows.LABELS[i]); else values.put(@PKG@.CfgRows.KEYS[i], v);
    }
  }
  java.util.ArrayList errors = new java.util.ArrayList();
  Object[] pl = plan(values, tables, errors);
  java.util.ArrayList lines = (java.util.ArrayList) pl[5];
  String note = "";
  if (errors.size() > 0) note = "\nKept as they are (not valid in this version): " + joinLines(errors, 5);
  if (skipped.size() > 0) {
    StringBuilder sb = new StringBuilder("\nNot restored (the mod cannot read them back): ");
    for (int k = 0; k < skipped.size(); k++) { if (k > 0) sb.append(", "); sb.append((String) skipped.get(k)); }
    note = note + sb.toString();
  }
  int n = lines.size();
  if (n == 0) return R("ok", "0", @PKG@.CfgRows.FILES[f] + " already matches that version." + note);
  if (mode.equals("preview")) return R("ok", String.valueOf(n), n + " change(s) in " + @PKG@.CfgRows.FILES[f] + ":\n" + joinLines(lines, 40) + note);
  String fail = runPlan(pl, who, S(a, 3), "restore");
  if (fail != null) return R("error", String.valueOf(n), "Restored with problems - " + fail);
  return R("ok", String.valueOf(n), "Restored " + @PKG@.CfgRows.FILES[f] + " (" + n + " change(s)):\n" + joinLines(lines, 40) + note);
}""",
r"""
public static Object opLog(Object[] a) {
  if (a.length < 2 || !(a[1] instanceof Number)) return null;
  int n = ((Number) a[1]).intValue();
  if (n < 1) n = 1;
  if (n > 200) n = 200;
  return @PKG@.CfgLog.read(n);
}""",
# a restart table's entries as one text (sorted entry=columns lines): recorded at start, compared by restartPending
r"""
public static String tableSig(int i) {
  String[] ek = entryKeys(i);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int k = 0; k < ek.length; k++) l.add(ek[k] + "=" + entryValue(i, ek[k]));
  java.util.Collections.sort(l);
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < l.size(); k++) sb.append((String) l.get(k)).append('\n');
  return sb.toString();
}""",
r"""
public static int restartPending() {
  int n = 0;
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    if (!@PKG@.CfgRows.flag(i, "restart")) continue;
    try {
      int k = @PKG@.CfgRows.BK[i];
      if (@PKG@.CfgRows.isTable(i)) { String r = @PKG@.CfgFile.runv(i); if (r != null && !r.equals(tableSig(i))) n++; }
      else if (k == 1) { String p = @PKG@.CfgFile.pendv(i); if (p != null && !@PKG@.CfgRows.same(i, p, @PKG@.CfgRows.fieldGet(i))) n++; }
      else if (k == 2) { String r = @PKG@.CfgFile.runv(i); if (r != null && !@PKG@.CfgRows.same(i, current(i), r)) n++; }
    } catch (Throwable t) { }
  }
  return n;
}""",
r"""
public static Object opStatus(Object[] a) {
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) if (@PKG@.CfgFile.isBroken(f)) return new String[] { "unreadable", brokenMsg(f) };
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) if (@PKG@.CfgFile.isFailed(f)) return new String[] { "unsaved", "Changes to " + @PKG@.CfgRows.FILES[f] + " are not saved yet - retrying every 30 s." };
  int r = restartPending();
  if (r > 0) return new String[] { "restart", r + " change(s) wait for a server restart." };
  return new String[] { "ok", "All changes are saved." };
}""",
r"""
public static boolean isWrite(String op) {
  return op.equals("set") || op.equals("tset") || op.equals("add") || op.equals("remove") || op.equals("action") || op.equals("reload") || op.equals("import") || op.equals("restore");
}""",
r"""
public static Object call(Object o) {
  if (!(o instanceof Object[])) return null;
  Object[] a = (Object[]) o;
  if (a.length < 1 || !(a[0] instanceof String)) return null;
  String op = (String) a[0];
  if (op.equals("get")) return opGet(a);
  if (op.equals("set")) return opSet(a);
  if (op.equals("keys")) return opKeys(a);
  if (op.equals("tset")) return opTable(a, 0);
  if (op.equals("add")) return opTable(a, 1);
  if (op.equals("remove")) return opTable(a, 2);
  if (op.equals("action")) return opAction(a);
  if (op.equals("reload")) return opReload(a);
  if (op.equals("export")) return opExport(a);
  if (op.equals("import")) return opImport(a);
  if (op.equals("versions")) return @PKG@.CfgHist.versions();
  if (op.equals("restore")) return opRestore(a);
  if (op.equals("log")) return opLog(a);
  if (op.equals("status")) return opStatus(a);
  return null;
}""",
# guarantee 1: never throws
r"""
public Object apply(Object o) {
  try { return call(o); }
  catch (Throwable t) {
    @PKG@.CfgRows.warn("config op failed (internal error): " + t);
    try {
      if (o instanceof Object[] && ((Object[]) o).length > 0 && ((Object[]) o)[0] instanceof String && isWrite((String) ((Object[]) o)[0]))
        return R("error", null, "internal error - see the server log");
    } catch (Throwable t2) { }
    return null;
  }
}""",
# ---- helpers for the mod's own code (same classloader): admin commands share the menu path (spec 1.4.3). A player sender MUST have
# a UUID (null is refused, never treated as the console); only the mod's explicit console branch calls cmdSetConsole
r"""
public static String cmdSet(String key, String value, java.util.UUID who, String name) {
  try {
    if (who == null) {
      @PKG@.CfgRows.warn("cmdSet(" + key + ") was called without a player UUID - refused (the server console uses cmdSetConsole)");
      return "Could not tell who sent this command - nothing was changed.";
    }
    Object[] r = set(key, value, who, name, "yes", "command");
    return (String) r[2];
  } catch (Throwable t) { @PKG@.CfgRows.warn("config command failed: " + t); return "internal error - see the server log"; }
}""",
r"""
public static String cmdSetConsole(String key, String value) {
  try {
    Object[] r = set(key, value, null, "console", "yes", "console");
    return (String) r[2];
  } catch (Throwable t) { @PKG@.CfgRows.warn("config command failed: " + t); return "internal error - see the server log"; }
}""",
r"""
public static String cmdGet(String key) {
  try { int i = @PKG@.CfgRows.index(key); if (i < 0) return null; return current(i); } catch (Throwable t) { return null; }
}""",
# start: remember the running value of restart rows, log field rows the mod's loader clamped (once)
r"""
public static void boot() {
  for (int i = 0; i < @PKG@.CfgRows.KEYS.length; i++) {
    try {
      if (@PKG@.CfgRows.flag(i, "restart")) {
        if (@PKG@.CfgRows.isTable(i)) @PKG@.CfgFile.setRunv(i, tableSig(i));
        else if (!@PKG@.CfgRows.noValue(i)) @PKG@.CfgFile.setRunv(i, current(i));
      }
    } catch (Throwable t) { }
  }
  @PKG@.CfgSaveTask.clampCheck();
  @PKG@.CfgFile.logSoon();
}""",
]

# ================================================================================================================ Java: CfgPub
PUB_JAVA = [
r"""
public static void publish() {
  try {
    java.util.Map b = @PKG@.CfgRows.bridge();
    b.put("config:def:" + @PKG@.CfgRows.MOD, @PKG@.CfgRows.header());
    b.put("config:fn:" + @PKG@.CfgRows.MOD, new @PKG@.CfgFn());
    if (!(b.get("config:epoch:" + @PKG@.CfgRows.MOD) instanceof Long)) b.put("config:epoch:" + @PKG@.CfgRows.MOD, Long.valueOf(0L));
  } catch (Throwable t) { @PKG@.CfgRows.warn("could not publish config:def/config:fn: " + t); }
}""",
# plugin setup(), AFTER the mod's own config load; modsDir = the world's mods/ folder (getDataDirectory().getParent())
r"""
public static void start(java.nio.file.Path modsDir, @LOG@ log) {
  try {
    @PKG@.CfgRows.LOG = log;
    @PKG@.CfgRows.MODS = modsDir;
    @PKG@.CfgRows.HOME = modsDir.resolve("Skyy_" + @PKG@.CfgRows.MOD);
    @PKG@.CfgLog.init();
    @PKG@.CfgHist.init();
    @PKG@.CfgFile.init();
    for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) {
      try {
        Object[] d = @PKG@.CfgFile.readDisk(f);
        @PKG@.CfgFile.merge(f, (byte[]) d[0], ((Long) d[1]).longValue(), ((Long) d[2]).longValue());
      } catch (Throwable t) {
        if (@PKG@.CfgFile.markBroken(f, t)) @PKG@.CfgRows.warn(@PKG@.CfgRows.FILES[f] + " cannot be read - in-game changes to it are refused until it can be read again (fix or delete it, then Reload): " + t);
      }
    }
    @PKG@.CfgFn.boot();
    STARTED = true;
  } catch (Throwable t) { @PKG@.CfgRows.warn("config kit could not start: " + t); }
  publish();
}""",
# every pending save and log line, now, on the calling thread (plugin shutdown; also usable before a backup)
r"""
public static void flush() {
  for (int f = 0; f < @PKG@.CfgRows.FILES.length; f++) {
    try { @PKG@.CfgSaveTask.runReloads(@PKG@.CfgSaveTask.saveFile(f)); } catch (Throwable t) { @PKG@.CfgRows.warn("flush of " + @PKG@.CfgRows.FILES[f] + " failed: " + t); }
  }
  try { @PKG@.CfgLog.flush(); } catch (Throwable t) { }
}""",
r"""public static void shutdown() { flush(); }""",
]


# ================================================================================================================ emit
def _row_dict(t):
    if not isinstance(t, (tuple, list)) or len(t) != 12:
        _fail("a row must be a 12-tuple (key, label, cat, type, default, min, max, opts, unit, flags, help, bind): %r" % (t,))
    keys = ("key", "label", "cat", "type", "default", "min", "max", "opts", "unit", "flags", "help", "bind")
    r = dict(zip(keys, [("" if v is None else str(v)) for v in t]))
    return r


def _resolve_file(files, mod, spec, key):
    if spec == "":
        if not files:
            _fail("%s: no FILES given, so a binding must name its file" % key)
        return 0
    if spec in files:
        return files.index(spec)
    hits = [i for i, f in enumerate(files) if f.endswith("/" + spec)]
    if len(hits) == 1:
        return hits[0]
    _fail("%s: file %r is not one of FILES %s (or matches more than one)" % (key, spec, files))


def _qual(pkg, cls):
    return cls if "." in cls else pkg + "." + cls


def _parse_bind(r, pkg, mod, files, reload_default):
    b = r["bind"].strip()
    key, typ = r["key"], r["type"]
    parts = b.split(";")
    main, optlist = parts[0].strip(), parts[1:]
    o = {"after": "", "check": "", "confirm": "", "sep": ",", "entry": "key", "value": ""}
    for p in optlist:
        k, eq, v = p.partition("=")
        k = k.strip()
        if not eq or k not in o:
            _fail("%s: unknown binding option %r (after= check= confirm= sep= entry= value=)" % (key, p))
        o[k] = v if k == "sep" else v.strip()
    d = {"kind": 0, "cls": "", "name": "", "scale": 1, "file": -1, "fkey": "", "ckeys": "", "ftype": 0}
    if main in ("", "none"):
        return d, o
    if main.startswith("reload@"):
        main = "reload:" + main[len("reload"):]
    kind, _, rest = main.partition(":")
    target, at, fpart = rest.partition("@")
    fname, colon, fkey = fpart.partition(":")
    if kind == "field":
        m = re.match(r"^([A-Za-z_$][\w$.]*)\.([A-Za-z_$][\w$]*)(?:\*(\d+))?$", target)
        if not m:
            _fail("%s: field binding must be field:<Class>.<FIELD>[*scale]@<file>:<fileKey>, got %r" % (key, b))
        d.update(kind=1, cls=_qual(pkg, m.group(1)), name=m.group(2), scale=int(m.group(3) or 1))
    elif kind == "reload":
        if target:
            m = re.match(r"^([A-Za-z_$][\w$.]*)\.([A-Za-z_$][\w$]*)$", target)
            if not m:
                _fail("%s: reload binding must be reload[:<Class>.<method>]@<file>:<fileKey>, got %r" % (key, b))
            spec = _qual(pkg, m.group(1)) + "." + m.group(2)
        else:
            spec = reload_default
            if not spec:
                _fail("%s: reload binding without a routine and no RELOAD given" % key)
        d.update(kind=2, name=spec)
    elif kind == "custom":
        if not re.match(r"^[A-Za-z_$][\w$.]*$", target):
            _fail("%s: custom binding must be custom:<Class>[@<file>[:<k1>,<k2>]], got %r" % (key, b))
        d.update(kind=3, cls=_qual(pkg, target))
    elif kind == "action":
        m = re.match(r"^([A-Za-z_$][\w$.]*)\.([A-Za-z_$][\w$]*)$", target)
        if not m:
            _fail("%s: action binding must be action:<Class>.<method>, got %r" % (key, b))
        d.update(kind=4, cls=_qual(pkg, m.group(1)), name=m.group(2))
        return d, o
    else:
        _fail("%s: unknown binding kind %r in %r" % (key, kind, b))
    if typ == "table":
        dflt_key = key + "."
    else:
        dflt_key = key
    # a custom: row's file only gates its ops and receives the lines customSet returns, so with several FILES a silent FILES[0] would
    # tie it to the wrong file: it must say which one
    if d["kind"] == 3 and not at and len(files) > 1:
        _fail("%s: this mod has %d FILES, so a custom: binding must name its file (custom:<Class>@<file>)" % (key, len(files)))
    if d["kind"] in (1, 2) or (d["kind"] == 3 and (at or files)):
        d["file"] = _resolve_file(files, mod, fname if at else "", key)
    if d["kind"] == 3:
        d["ckeys"] = fkey if colon else ""
        d["fkey"] = ""
    else:
        d["fkey"] = fkey if colon else dflt_key
    return d, o


def _check_member(pool, cls, name, sig, mode, what):
    """A public static method cls.name whose JVM signature equals sig (mode 'exact') or starts with it (mode 'prefix': any return)."""
    J = __import__("jpype").JClass
    Mod = J("javassist.Modifier")
    try:
        cc = pool.get(cls)
    except Exception:
        _fail("%s: class %s does not exist" % (what, cls))
    for m in cc.getDeclaredMethods():
        if str(m.getName()) != name:
            continue
        s = str(m.getSignature())
        if (mode == "exact" and s == sig) or (mode == "prefix" and s.startswith(sig)):
            mods = m.getModifiers()
            if not Mod.isPublic(mods) or not Mod.isStatic(mods):
                _fail("%s: %s.%s must be public static" % (what, cls, name))
            return
    _fail("%s: needs a public static method %s.%s with JVM signature %s%s" % (what, cls, name, sig, "..." if mode == "prefix" else ""))


class Kit(object):
    """What emit() returns. kit.write(OUT) runs the deferred checks (hook methods may be compiled after emit) and writes the classes."""
    def __init__(self, pool, classes, deferred, info):
        self.pool, self.classes, self.deferred, self.info = pool, classes, deferred, info

    def check(self):
        for (cls, name, sig, mode, what) in self.deferred:
            _check_member(self.pool, cls, name, sig, mode, what)

    def write(self, out_dir):
        self.check()
        for c in self.classes:
            c.writeFile(out_dir)


def emit(pool, PKG, MOD, TITLE, VERSION, NODE, CATS, ROWS, FILES=None, NOTE="", RELOAD=None, KEEP=20, ALIASES=(),
         DEFAULTS=None, ITEMS=None, PERM_FN=None, ITEM_FN=None):
    """Checks the schema (spec 2.12 per-mod checks) and compiles CfgRows, CfgLog, CfgHist, CfgSaveTask, CfgFile, CfgFn, CfgPub into
    PKG. Returns a Kit; call kit.write(OUT) after the rest of the mod is compiled. PERM_FN / ITEM_FN are for the bare-JVM test
    harness only: "<Class>.<method>" static boolean (java.util.UUID, String) / (String) used instead of PermissionsModule / Item."""
    import jpype
    JClass = jpype.JClass
    CtField, CtNewMethod, CtNewConstructor, Mod = (JClass("javassist.CtField"), JClass("javassist.CtNewMethod"),
                                                   JClass("javassist.CtNewConstructor"), JClass("javassist.Modifier"))
    # ---------------------------------------------------------------- header checks
    if not MOD_RE.match(MOD or ""):
        _fail("MOD %r must match Skyy[A-Z][A-Za-z]{1,30}" % MOD)
    if not TITLE or len(TITLE) > 24:
        _fail("TITLE must be 1-24 characters")
    if not VERSION or not re.match(r"^[0-9][0-9A-Za-z.\-]{0,20}$", VERSION):
        _fail("VERSION %r looks wrong" % VERSION)
    if not NODE_RE.match(NODE or ""):
        _fail("NODE %r is not a permission node like skyyeconomy.admin" % NODE)
    if len(NOTE) > 100:
        _fail("NOTE is longer than 100 characters")
    if not isinstance(KEEP, int) or not 1 <= KEEP <= 200:
        _fail("KEEP must be 1-200")
    for a in ALIASES:
        if not MOD_RE.match(a):
            _fail("alias %r must match Skyy[A-Z][A-Za-z]{1,30}" % a)
    cats = [(str(c[0]), str(c[1])) for c in CATS]
    if not 1 <= len(cats) <= 16:
        _fail("CATS needs 1-16 categories")
    for cid, cl in cats:
        if not CAT_RE.match(cid):
            _fail("category id %r must match [a-z][a-zA-Z0-9]{0,15}" % cid)
        if not cl or len(cl) > 20:
            _fail("category label %r must be 1-20 characters" % cl)
    if len(set(c for c, _ in cats)) != len(cats):
        _fail("duplicate category id")
    cat_ids = [c for c, _ in cats]
    files = list(FILES or [])
    for f in files:
        if not re.match(r"^[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)*$", f) or ".." in f.split("/"):
            _fail("file %r must be a plain relative path under mods/ (like Skyy_SkyyBank/config.properties)" % f)
    if len(set(files)) != len(files):
        _fail("duplicate FILES entry")
    defaults = dict(DEFAULTS or {})
    for k in list(defaults):
        if k not in files:
            hits = [f for f in files if f.endswith("/" + k)]
            if len(hits) != 1:
                _fail("DEFAULTS key %r is not one of FILES" % k)
            defaults[hits[0]] = defaults.pop(k)
    dprops = {f: parse_props(t) for f, t in defaults.items()}
    reload_default = ""
    if RELOAD:
        m = re.match(r"^([A-Za-z_$][\w$.]*)\.([A-Za-z_$][\w$]*)$", RELOAD)
        if not m:
            _fail("RELOAD must be <Class>.<method>")
        reload_default = _qual(PKG, m.group(1)) + "." + m.group(2)
    items = ITEMS if ITEMS is not None else _items_from_assets()
    # ---------------------------------------------------------------- rows
    rows = [_row_dict(t) for t in ROWS]
    if not rows:
        _fail("no rows")
    seen = set()
    binds = []
    deferred = []
    for r in rows:
        k, t = r["key"], r["type"]
        if not KEY_RE.match(k):
            _fail("key %r must match [A-Za-z][A-Za-z0-9._-]{0,79}" % k)
        if k in seen:
            _fail("duplicate key %r" % k)
        seen.add(k)
        if t not in TYPES:
            _fail("%s: unknown type %r" % (k, t))
        if not r["label"] or len(r["label"]) > 40:
            _fail("%s: label must be 1-40 characters" % k)
        if len(r["help"]) > 100:
            _fail("%s: help is longer than 100 characters (%d)" % (k, len(r["help"])))
        if r["cat"] not in cat_ids:
            _fail("%s: category %r is not in CATS" % (k, r["cat"]))
        fl = [x for x in r["flags"].split(",") if x]
        for x in fl:
            if x not in FLAGS:
                _fail("%s: unknown flag %r" % (k, x))
        if len(set(fl)) != len(fl):
            _fail("%s: duplicate flag" % k)
        if "part" in fl and t != "bool":
            _fail("%s: a part switch must be a bool row" % k)
        if "part" in fl and "danger" not in fl:
            _fail("%s: a part switch needs the danger flag too (live,part,danger, spec 3): switching a part OFF must ask first" % k)
        if "live" in fl and "restart" in fl:
            _fail("%s: live and restart together" % k)
        if r["unit"] not in UNITS:
            _fail("%s: unit %r is not one of %s (extend UNITS in tools/skyycfg.py if a new one is needed)" % (k, r["unit"], UNITS))
        # kit 1.1: a value= action's min / max / default follow its value type (a text value: min / max are its length)
        valt = ""
        for p in r["bind"].split(";")[1:]:
            pk, peq, pv = p.partition("=")
            if pk.strip() == "value" and peq:
                valt = pv.strip()
        et = valt if (t == "action" and valt in ACTION_VALUE_TYPES) else t
        for bound in ("min", "max"):
            v = r[bound]
            if v == "":
                continue
            d = _dec(v)
            if d is None:
                _fail("%s: %s %r is not a number" % (k, bound, v))
            if et in ("text", "items") and (d != d.to_integral_value() or d < 0):
                _fail("%s: %s of a %s row is a count (whole number >= 0)" % (k, bound, et))
            if et == "int" and d != d.to_integral_value():
                _fail("%s: %s of an int row must be whole" % (k, bound))
            r[bound] = _plain(d) if et not in ("text", "items") else str(int(d))
        if r["min"] and r["max"] and Decimal(r["min"]) > Decimal(r["max"]):
            _fail("%s: min is above max" % k)
        # opts per type
        o = r["opts"]
        if t == "bool" and o not in ("", "01"):
            _fail("%s: bool opts may only be '01'" % k)
        if t in ("int", "dec") and o and not re.match(r"^step=\d+(\.\d+)?$", o):
            _fail("%s: int/dec opts may only be step=N" % k)
        if t == "items" and any(x not in ("qty", "prefix") for x in o.split(",") if x):
            _fail("%s: items opts are qty and/or prefix" % k)
        if t == "choice":
            vals, labs = _choices(o)
            if not o or any(not v or not re.match(r"^[A-Za-z0-9_.\-]+$", v) for v in vals) or len(set(vals)) != len(vals):
                _fail("%s: choice opts must be value|Label,value|Label with unique plain values" % k)
            for v, lab in zip(vals, labs):
                if not lab or len(lab) > CHOICE_LABEL_MAX:
                    _fail("%s: choice %r has the label %r; a choice label must be 1-%d characters (SkyyMenu draws it in a 100 px button or "
                          "the 220 px cycling label, spec 2.5)" % (k, v, lab, CHOICE_LABEL_MAX))
        if t == "table":
            p = o.split(";")
            if len(p) != 3 or p[1] not in ("none", "type", "held", "both"):
                _fail("%s: table opts must be <valueType>;<none|type|held|both>;<Col1|Col2|Col3>" % k)
            cn = p[2].split("|")
            vt = p[0].split("|")
            if not 1 <= len(cn) <= 3 or any(not c for c in cn):
                _fail("%s: a table has 1-3 named columns" % k)
            if len(vt) not in (1, len(cn)) or any(x not in ("int", "dec", "text", "bool") for x in vt):
                _fail("%s: table value types are int, dec, text or bool (one, or one per column)" % k)
            if r["default"]:
                _fail("%s: a table's default must be empty (its entries come from the file)" % k)
            # kit 1.1: without an int/dec column the row max is the text length of the table's text columns (CfgFn.textMax) and min
            # means nothing (no minimum text length for table cells), so a min there is refused instead of silently ignored
            if not any(x.strip() in ("int", "dec") for x in vt):
                if r["min"]:
                    _fail("%s: min %s has no effect on a table without number columns (only max counts there: the text length); "
                          "leave min empty" % (k, r["min"]))
                if r["max"]:
                    dm = Decimal(r["max"])
                    if dm != dm.to_integral_value() or not 1 <= dm <= TABLE_TEXT_MAX:
                        _fail("%s: a table without number columns uses max as its text length: a whole number from 1 to %d, not %s" % (
                            k, TABLE_TEXT_MAX, r["max"]))
        if t in ("link", "action"):
            if not o:
                _fail("%s: a %s row needs opts (%s)" % (k, t, "the command" if t == "link" else "the button text"))
            # a value= action may publish a default (the value used when a caller sends none, SkyyMenu's field text); checked below
            if r["default"] and not (t == "action" and valt):
                _fail("%s: a %s row's default must be empty" % (k, t))
        # binding
        d, bo = _parse_bind(r, PKG, MOD, files, reload_default)
        if bo["confirm"] not in CONF:
            _fail("%s: confirm= must be one of on, off, up, down, always, never" % k)
        if bo["entry"] not in ENTRY:
            _fail("%s: entry= must be key, item or itemprefix" % k)
        if len(bo["sep"]) != 1 or bo["sep"] in "|\r\n":
            _fail("%s: sep= must be one character other than |" % k)
        if (bo["confirm"] or bo["check"]) and t in ("link",):
            _fail("%s: link rows take no confirm=/check=" % k)
        # kit 1.1: value=<type> gives an action a typed value (validated like a scalar row of that type with this row's min/max/unit)
        if bo["value"]:
            if t != "action":
                _fail("%s: value= is for action rows (an action that takes a typed value), not for type %s" % (k, t))
            if bo["value"] not in ACTION_VALUE_TYPES:
                _fail("%s: value= must be one of %s (types that need opts are not possible: opts is the button text)" % (
                    k, ", ".join(ACTION_VALUE_TYPES)))
            if r["default"]:
                canon, why = py_validate(dict(r, type=bo["value"], opts=""), r["default"], items)
                if canon is None:
                    _fail("%s: default %r does not pass its own row (value=%s: %s)" % (k, r["default"], bo["value"], why))
        # confirm= refines WHEN a danger row asks (the published danger flag stays the page's CONFIRM tag); every row kind that takes it
        # honours it at runtime: scalars in needConfirm, tables in tableChange, actions in opAction
        if bo["confirm"]:
            c = bo["confirm"]
            if "danger" not in fl:
                _fail("%s: confirm=%s refines when a danger row asks, but this row has no danger flag" % (k, c))
            if t in ("table", "action") and c not in ("always", "never"):
                _fail("%s: %s rows take confirm=always or confirm=never only (they have no old/new value)" % (k, t))
            if c in ("on", "off") and t != "bool":
                _fail("%s: confirm=%s is for bool rows" % (k, c))
            if c in ("up", "down") and t not in ("int", "dec"):
                _fail("%s: confirm=%s is for int and dec rows" % (k, c))
        kind = d["kind"]
        if t in SCALAR and kind not in (1, 2, 3):
            _fail("%s: a %s row needs a field:, reload: or custom: binding" % (k, t))
        if t == "table" and kind not in (2, 3):
            _fail("%s: a table row binds reload@<file>:<prefix> (a key family) or custom:" % k)
        if t == "link" and kind != 0:
            _fail("%s: a link row has no binding" % k)
        if t == "action" and kind != 4:
            _fail("%s: an action row binds action:<Class>.<method>" % k)
        if (kind in (1, 2)) and d["file"] < 0:
            _fail("%s: needs a file" % k)
        if kind in (1, 2) and ((t != "table" and not d["fkey"]) or any(c in d["fkey"] for c in " \t=:#!\\")):
            _fail("%s: file key %r is not usable" % (k, d["fkey"]))
        if d["scale"] != 1 and kind != 1:
            _fail("%s: only field: bindings take a scale" % k)
        # field type + unit rule (spec 1.4.1, 2.12)
        if kind == 1:
            try:
                cc = pool.get(d["cls"])
            except Exception:
                _fail("%s: class %s does not exist (compile the config class before emit)" % (k, d["cls"]))
            try:
                fld = cc.getDeclaredField(d["name"])
            except Exception:
                _fail("%s: %s has no field %s" % (k, d["cls"], d["name"]))
            mods = fld.getModifiers()
            if not (Mod.isPublic(mods) and Mod.isStatic(mods) and Mod.isVolatile(mods)) or Mod.isFinal(mods):
                _fail("%s: %s.%s must be public static volatile and not final" % (k, d["cls"], d["name"]))
            ft = FTYPE.get(str(fld.getType().getName()), 0)
            if ft == 0:
                _fail("%s: %s.%s has type %s; field: supports int, long, double, boolean, String" % (k, d["cls"], d["name"], fld.getType().getName()))
            if ft not in FIELD_OK.get(t, ()):
                _fail("%s: a %s row cannot bind a %s field" % (k, t, fld.getType().getName()))
            d["ftype"] = ft
            numeric = ft in (1, 2, 3)
            is_ms = numeric and MS_FIELD_RE.search(d["name"]) is not None
            u = r["unit"]
            if is_ms:
                if u not in MS_UNIT_SCALE:
                    _fail("%s: %s stores milliseconds; its row must use unit ms, s, min or h (unit rule 1.4.1)" % (k, d["name"]))
                if d["scale"] != MS_UNIT_SCALE[u]:
                    _fail("%s: %s stores milliseconds and the row unit is %r, so the binding needs %s (unit rule 1.4.1)" % (
                        k, d["name"], u, "no scale" if u == "ms" else "*%d" % MS_UNIT_SCALE[u]))
            else:
                if u == "ms" and numeric:
                    _fail("%s: a row with unit ms must bind a millisecond field (*_MS, *Ms, *MILLIS, *Millis) (unit rule 1.4.1)" % k)
                if d["scale"] != 1:
                    _fail("%s: a scale is only allowed on a millisecond field (*_MS, *Ms, *MILLIS, *Millis) (unit rule 1.4.1)" % k)
            if ft in (1, 2) and t == "int":
                lim_lo, lim_hi = (INT_MIN, INT_MAX) if ft == 1 else (LONG_MIN, LONG_MAX)
                if ft == 1 and (not r["max"] or not r["min"]):
                    _fail("%s: an int field needs a min and a max in its row" % k)
                if d["scale"] != 1 and not r["max"]:
                    _fail("%s: a scaled field needs a max in its row" % k)
                if r["max"] and Decimal(r["max"]) * d["scale"] > lim_hi:
                    _fail("%s: max %s x scale %d does not fit the %s field" % (k, r["max"], d["scale"], fld.getType().getName()))
                if r["min"] and Decimal(r["min"]) * d["scale"] < lim_lo:
                    _fail("%s: min %s x scale %d does not fit the %s field" % (k, r["min"], d["scale"], fld.getType().getName()))
        if kind == 2:
            deferred.append((d["name"].rsplit(".", 1)[0], d["name"].rsplit(".", 1)[1], "()", "prefix", k + " reload routine"))
        if kind == 3:
            deferred.append((d["cls"], "customGet", "(Ljava/lang/String;)Ljava/lang/String;", "exact", k + " custom:"))
            deferred.append((d["cls"], "customSet", "(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/Object;", "exact", k + " custom:"))
            if t == "table":
                deferred.append((d["cls"], "customKeys", "(Ljava/lang/String;)[Ljava/lang/String;", "exact", k + " custom table"))
        if kind == 4:
            asig = "(Ljava/util/UUID;Ljava/lang/String;Ljava/lang/String;)" if bo["value"] else "(Ljava/util/UUID;Ljava/lang/String;)"
            deferred.append((d["cls"], d["name"], asig + "[Ljava/lang/Object;", "exact",
                             k + (" value action (value=%s)" % bo["value"] if bo["value"] else " action")))
        for hook, sig, mode in (("after", "(Ljava/lang/String;)", "prefix"),
                                ("check", "(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "exact")):
            if bo[hook]:
                m = re.match(r"^([A-Za-z_$][\w$.]*)\.([A-Za-z_$][\w$]*)$", bo[hook])
                if not m:
                    _fail("%s: %s= must be <Class>.<method>" % (k, hook))
                bo[hook] = _qual(PKG, m.group(1)) + "." + m.group(2)
                if hook == "after" and kind != 1:
                    _fail("%s: after= is for field: rows (reload rows get their reload routine)" % k)
                deferred.append((_qual(PKG, m.group(1)), m.group(2), sig, mode, k + " " + hook + "="))
        # default validates (build check 2.12)
        if t in SCALAR:
            canon, why = py_validate(r, r["default"], items)
            if canon is None:
                _fail("%s: default %r does not pass its own row (%s)" % (k, r["default"], why))
        # 01 check: a bool row whose file key is written 1/0 in the mod's default file needs the 01 token (1.4.1 value format rule)
        if t == "bool" and kind in (1, 2) and d["file"] >= 0 and files[d["file"]] in dprops:
            fv = dprops[files[d["file"]]].get(d["fkey"])
            if fv is not None and fv.strip() in ("1", "0") and r["opts"] != "01":
                _fail("%s: the default file writes %s=%s, so this bool row needs opts '01' (1.4.1 value format rule)" % (k, d["fkey"], fv.strip()))
        binds.append((d, bo))
    # key families: an empty prefix owns the whole file
    for idx, r in enumerate(rows):
        d, bo = binds[idx]
        if r["type"] == "table" and d["kind"] == 2 and d["fkey"] == "":
            others = [rows[j]["key"] for j, (dd, _) in enumerate(binds) if j != idx and dd["file"] == d["file"] and dd["kind"] in (1, 2, 3)]
            if others:
                _fail("%s: a table with an empty prefix owns its whole file, but %s also bind it" % (r["key"], others))
    # one owner per file key: no two rows bind the same key, no two key-family prefixes in a file overlap (combat. / combat.role), and
    # no scalar or custom file key falls inside a table's family (it would be listed, exported and restored as a table entry too)
    for fi in range(len(files)):
        exact, fams = [], []
        for idx, r in enumerate(rows):
            d, _ = binds[idx]
            if d["file"] != fi:
                continue
            if r["type"] == "table" and d["kind"] == 2:
                fams.append((d["fkey"], r["key"]))
            elif d["kind"] in (1, 2):
                exact.append((d["fkey"], r["key"]))
            elif d["kind"] == 3 and d["ckeys"]:
                exact.extend((ck, r["key"]) for ck in d["ckeys"].split(",") if ck)
        owner = {}
        for fk, rk in exact:
            if fk in owner and owner[fk] != rk:
                _fail("%s and %s both bind %s:%s (one row per file key)" % (owner[fk], rk, files[fi], fk))
            owner[fk] = rk
        for a in range(len(fams)):
            for b in range(a + 1, len(fams)):
                pa, pb = fams[a][0], fams[b][0]
                if pa.startswith(pb) or pb.startswith(pa):
                    _fail("tables %s (prefix %r) and %s (prefix %r) overlap in %s: one family would swallow the other's lines" % (
                        fams[a][1], pa, fams[b][1], pb, files[fi]))
        for fk, rk in exact:
            for p, tk in fams:
                if fk.startswith(p) and len(fk) > len(p):
                    _fail("%s binds %s:%s, which is inside the key family of table %s (prefix %r)" % (rk, files[fi], fk, tk, p))
    # deferred global reload routine (any return type)
    if reload_default:
        deferred.append((reload_default.rsplit(".", 1)[0], reload_default.rsplit(".", 1)[1], "()", "prefix", "RELOAD"))
    dfr = list(dict.fromkeys(deferred))
    # ---------------------------------------------------------------- generate + compile
    n = len(rows)
    nf = len(files)
    def _spec(s):
        c, _, m = s.rpartition(".")
        if not c or not m:
            _fail("%r must be <Class>.<method>" % s)
        return _qual(PKG, c) + "." + m

    T = {"PKG": PKG, "HSV": HSV, "LOG": LOGC,
         "PERMCHECK": ("%s(who, NODE)" % _spec(PERM_FN)) if PERM_FN else PERM_DEFAULT,
         "ITEMCHECK": ("%s(id)" % _spec(ITEM_FN)) if ITEM_FN else ITEM_DEFAULT}

    def jv(src):
        out = src
        for kk, vv in T.items():
            out = out.replace("@" + kk + "@", vv)
        left = re.findall(r"@[A-Z]+@", out)
        if left:
            _fail("internal: unreplaced tokens %s" % left)
        return out

    cls = {}
    for name in CLASS_NAMES:
        try:
            pool.get(PKG + "." + name)
            _fail("%s.%s already exists in the pool (emit once per package)" % (PKG, name))
        except CfgError:
            raise
        except Exception:
            pass
        cls[name] = pool.makeClass(PKG + "." + name)
    cls["CfgFn"].addInterface(pool.get("java.util.function.Function"))
    cls["CfgSaveTask"].addInterface(pool.get("java.lang.Runnable"))

    def F(c, src):
        cls[c].addField(CtField.make(jv(src), cls[c]))

    def M(c, src):
        try:
            cls[c].addMethod(CtNewMethod.make(jv(src), cls[c]))
        except Exception as e:
            _fail("internal compile error in %s: %s\n%s" % (c, e, jv(src)[:600]))

    def C(c, src):
        cls[c].addConstructor(CtNewConstructor.make(jv(src), cls[c]))

    dlines = []
    for f in files:
        t = defaults.get(f)
        dlines.append(t.replace("\r\n", "\n").rstrip("\n").split("\n") if t else [])
    col = lambda name: [r[name] for r in rows]
    # CfgRows fields
    F("CfgRows", "public static final String CONTRACT = %s;" % _jstr(CONTRACT))
    F("CfgRows", "public static final String KIT = %s;" % _jstr(KIT_VERSION))
    F("CfgRows", "public static final String MOD = %s;" % _jstr(MOD))
    F("CfgRows", "public static final String TITLE = %s;" % _jstr(TITLE))
    F("CfgRows", "public static final String VERSION = %s;" % _jstr(VERSION))
    F("CfgRows", "public static final String NODE = %s;" % _jstr(NODE))
    F("CfgRows", "public static final String FILES_CSV = %s;" % _jstr(",".join(files)))
    F("CfgRows", "public static final String NOTE = %s;" % _jstr(NOTE))
    F("CfgRows", "public static final String RELOAD = %s;" % _jstr(reload_default))
    F("CfgRows", "public static final int KEEP = %d;" % KEEP)
    F("CfgRows", "public static final String[] CAT_IDS = %s;" % _jarr(cat_ids))
    F("CfgRows", "public static final String[] CAT_LABELS = %s;" % _jarr([c for _, c in cats]))
    for arr, name in (("KEYS", "key"), ("LABELS", "label"), ("CATS", "cat"), ("TYPES", "type"), ("DEFS", "default"), ("MINS", "min"),
                      ("MAXS", "max"), ("OPTS", "opts"), ("UNITS", "unit"), ("FLAGS", "flags"), ("HELPS", "help")):
        F("CfgRows", "public static final String[] %s = %s;" % (arr, _jarr(col(name))))
    F("CfgRows", "public static final int[] BK = %s;" % _jints([d["kind"] for d, _ in binds]))
    F("CfgRows", "public static final int[] BF = %s;" % _jints([d["file"] for d, _ in binds]))
    F("CfgRows", "public static final int[] BFT = %s;" % _jints([d["ftype"] for d, _ in binds]))
    F("CfgRows", "public static final int[] BCONF = %s;" % _jints([CONF[o["confirm"]] for _, o in binds]))
    F("CfgRows", "public static final int[] BENT = %s;" % _jints([ENTRY[o["entry"]] for _, o in binds]))
    F("CfgRows", "public static final long[] BSC = %s;" % _jlongs([d["scale"] for d, _ in binds]))
    F("CfgRows", "public static final String[] BCLS = %s;" % _jarr([d["cls"] for d, _ in binds]))
    F("CfgRows", "public static final String[] BNAME = %s;" % _jarr([d["name"] for d, _ in binds]))
    F("CfgRows", "public static final String[] BFK = %s;" % _jarr([d["fkey"] for d, _ in binds]))
    F("CfgRows", "public static final String[] BCK = %s;" % _jarr([d["ckeys"] for d, _ in binds]))
    F("CfgRows", "public static final String[] BAFTER = %s;" % _jarr([o["after"] for _, o in binds]))
    F("CfgRows", "public static final String[] BCHECK = %s;" % _jarr([o["check"] for _, o in binds]))
    F("CfgRows", "public static final String[] BSEP = %s;" % _jarr([o["sep"] for _, o in binds]))
    F("CfgRows", "public static final String[] VTYPES = %s;" % _jarr([o["value"] for _, o in binds]))
    F("CfgRows", "public static final String[] FILES = %s;" % _jarr(files))
    F("CfgRows", "public static final String[] FILE_IDS = %s;" % _jarr([f.replace("/", "~") for f in files]))
    F("CfgRows", "public static final String[] ALIASES = %s;" % _jarr(list(ALIASES)))
    # javassist cannot compile a String[][] initializer: one array per file + an accessor
    for fi, dl in enumerate(dlines):
        F("CfgRows", "public static final String[] DL%d = %s;" % (fi, _jarr(dl)))
    M("CfgRows", "public static String[] defLines(int f) { " + " ".join("if (f == %d) return DL%d;" % (fi, fi) for fi in range(len(dlines)))
      + " return new String[0]; }")
    F("CfgRows", "public static %s LOG;" % LOGC)
    F("CfgRows", "public static java.nio.file.Path MODS;")
    F("CfgRows", "public static java.nio.file.Path HOME;")
    F("CfgRows", "public static volatile long WARNS;")
    F("CfgRows", "public static final java.lang.reflect.Field[] FLD = new java.lang.reflect.Field[%d];" % n)
    F("CfgRows", "public static final java.util.Map MCACHE = new java.util.concurrent.ConcurrentHashMap();")
    F("CfgRows", "public static final Class[] SIG0 = new Class[0];")
    F("CfgRows", "public static final Class[] SIG_S = new Class[] { String.class };")
    F("CfgRows", "public static final Class[] SIG_SS = new Class[] { String.class, String.class };")
    F("CfgRows", "public static final Class[] SIG_US = new Class[] { java.util.UUID.class, String.class };")
    F("CfgRows", "public static final Class[] SIG_USS = new Class[] { java.util.UUID.class, String.class, String.class };")
    F("CfgRows", "public static final Class[] SIG_SM = new Class[] { String.class, java.util.Map.class };")
    for src in ROWS_JAVA:
        M("CfgRows", src)
    for src in LOG_FIELDS:
        F("CfgLog", src)
    for src in LOG_JAVA:
        M("CfgLog", src)
    for src in HIST_FIELDS:
        F("CfgHist", src)
    for src in HIST_JAVA:
        M("CfgHist", src)
    for src in TASK_FIELDS:
        F("CfgSaveTask", src)
    C("CfgSaveTask", TASK_CTOR)
    # CfgFile fields
    F("CfgFile", "public static final int NF = %d;" % nf)
    F("CfgFile", "public static final String HEADER = %s;" % _jstr(HEADER_LINE))
    for decl in ("java.nio.file.Path[] PATH = new java.nio.file.Path[NF]", "java.util.ArrayList[] LINES = new java.util.ArrayList[NF]",
                 "String[] NL = new String[NF]", "boolean[] ENDNL = new boolean[NF]", "long[] MT = new long[NF]", "long[] SZ = new long[NF]",
                 "java.util.HashMap[] BASE = new java.util.HashMap[NF]", "java.util.HashMap[] VALS = new java.util.HashMap[NF]",
                 "java.util.LinkedHashMap[] PEND = new java.util.LinkedHashMap[NF]", "java.util.HashSet[] RLD = new java.util.HashSet[NF]",
                 "boolean[] DIRTY = new boolean[NF]", "boolean[] BROKEN = new boolean[NF]", "boolean[] FAILED = new boolean[NF]",
                 "boolean[] SCHED = new boolean[NF]", "boolean[] WARNED = new boolean[NF]", "boolean[] MISSING = new boolean[NF]",
                 "boolean[] LOADED = new boolean[NF]", "boolean[] FORCE = new boolean[NF]", "String[] WHY = new String[NF]",
                 "String[] PSTAMP = new String[NF]", "String[] PWHO = new String[NF]",
                 "String[] PVIA = new String[NF]", "java.util.HashSet[] PWHAT = new java.util.HashSet[NF]",
                 "java.util.HashMap[] HOLD = new java.util.HashMap[NF]", "java.util.HashMap[] HCHK = new java.util.HashMap[NF]",
                 "java.util.HashMap[] WROTE = new java.util.HashMap[NF]",
                 "String[] PENDV = new String[%d]" % n, "String[] RUNV = new String[%d]" % n,
                 "java.util.HashSet CLAMPED = new java.util.HashSet()"):
        F("CfgFile", "public static final %s;" % decl)
    F("CfgFile", "public static boolean LOGSCHED;")
    F("CfgFile", "public static long SGEN;")   # kit 1.1: save batches taken so far (CfgFile.takeBatch / reassert)
    for src in FILE_JAVA_HELPERS:
        M("CfgFile", src)
    for src in FN_EARLY:          # kit 1.1: CfgFile.handApply uses CfgFn.entryErr / tvalue
        M("CfgFn", src)
    for src in FILE_JAVA_STATE:
        M("CfgFile", src)
    M("CfgFile", r"""public static synchronized boolean clampSeen(int i, String raw) { return !CLAMPED.add(i + "=" + raw); }""")
    for src in FN_MID:            # kit 1.1: CfgSaveTask.saveFile calls CfgFn.handChecks
        M("CfgFn", src)
    for src in TASK_JAVA:
        M("CfgSaveTask", src)
    C("CfgFn", "public CfgFn() { }")
    for src in FN_JAVA:
        M("CfgFn", src)
    F("CfgPub", "public static volatile boolean STARTED;")
    for src in PUB_JAVA:
        M("CfgPub", src)
    classes = [cls[c] for c in CLASS_NAMES]
    info = {"rows": n, "files": files, "classes": [PKG + "." + c for c in CLASS_NAMES], "kit": KIT_VERSION}
    return Kit(pool, classes, dfr, info)
