"""soundpass_gen - SOUND PASS ROUND 2 shared pieces (research/Sound-Pass-Plan.md; Skyy 2026-10-14 ~18:30 "do 1. 3. 6. 7. 8. and 9.", item 6 =
"Sound pass rounds 2-4 ... plus a per-player sound switch").

Round 1 (SkyyQuests 0.3.1, SkyyExploration 0.2.9, SkyyBank 0.1.12, SkyyIslands 0.5.9, SkyyPets 0.2.6) pasted one hand-written helper per
mod. Round 2 touches eight mods at once, so the SAME helper is generated here and PASTED AS TEXT into each generated build script by its
patch (tools/<mod>_<ver>_patch.py) - the generated script stays self-contained (it never imports this file), exactly like round 1.

What a mod gets (the round 1 recipe + the round 2 per-player switch):
  * ONE class <Pfx>Snd (no dependency on any other class of the mod, so it compiles first and every caller can use it):
      - vanilla sound event ids played BY ID (no sound file copied or shipped), 2D to ONE player, category UI
        (SoundUtil.playSoundEvent2dToPlayer = one PlaySoundEvent2D packet to that player's connection) - nobody else hears it
      - never throws; the id is looked up in the game's SoundEvent map each time (a missing id = one WARN per id, nothing played)
      - at most one of the same sound per player per 0.5 s (GAP_MS), so a burst (claim all, sell inventory) is one sting
      - NEW: the per-player switch - every play first reads the bridge key settings:sounds:<uuid> (java.lang.Boolean, published by
        SkyyMenu 0.3.25's /settings): Boolean.FALSE = that player hears no SkyWynn sound; absent (an older SkyyMenu, or the player
        never chose) or TRUE = play. Read only - never written here.
      - its own file Skyy_<Mod>/sounds.properties (written with the defaults when missing; an existing file is never rewritten
        by the mod - only the config kit writes a changed line): sounds.enabled, sound.<s>, sound.<s>.id (+ mod extras)
  * Server Setup -> <Mod> -> new category "Sounds": the master switch + per sound an on / off row and its id row (text, max 120,
    check= <Pfx>Snd.check: letters / digits / _ and a sound event the game has; empty = that sound off). All rows live.
  * the build checks every default id against the game's Assets.zip (read only) - an id the game lacks stops the build.

Harness helpers (bare JVM, inside a harness_kit child that set up tools/soundpass_kit.Stage): unit(...) runs every generic path of a
generated <Pfx>Snd (file, rows, kit check hook, id / pick, gate, missing id, the per-player switch muted / on / absent / junk, offline).
"""
import os
import json

GAP_MS = 500


# ================================================================================================================ build-time text
def _java(cls, mod, sounds, extra_fields, extra_methods, extra_load, file_head):
    """(fields, methods) Java source lists for the <Pfx>Snd class; @SPKG@ = the package (filled in by the generated script)"""
    fields = [
        "public static volatile boolean ON = true;",
        "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
        "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
        "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();",
        "public static final java.util.concurrent.atomic.AtomicLong MUTED = new java.util.concurrent.atomic.AtomicLong();",
        "public static final java.util.concurrent.atomic.AtomicLong WARNS = new java.util.concurrent.atomic.AtomicLong();",
        "public static final long GAP_MS = %dL;" % GAP_MS,
        "public static final String MUTE_KEY = \"settings:sounds:\";",
        "public static java.nio.file.Path FILE;",
    ]
    for s in sounds:
        fields.append("public static volatile boolean S_%s = true;" % s["field"])
        fields.append("public static volatile String S_%s_ID = %s;" % (s["field"], json.dumps(s["id"])))
    fields += list(extra_fields)
    text = file_text(mod, sounds, file_head)
    fields.append("public static final String DEFAULT_TEXT = %s;" % json.dumps(text))
    m = []
    m.append("""
public static void warn(String msg) {
  WARNS.incrementAndGet();
  try { com.hypixel.hytale.logger.HytaleLogger.get("%s").at(java.util.logging.Level.WARNING).log("[%s] " + msg); } catch (Throwable t) { }
}""" % (mod, mod))
    m.append("""
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
    m.append("""
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Coins_Land).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}""")
    m.append("""
public static String check(String key, String value) {
  return err(value);
}""")
    m.append("""
public static boolean word(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return d;
}""")
    chain = []
    for i, s in enumerate(sounds):
        chain.append("  if (w == %d) { on = S_%s; v = S_%s_ID; }" % (i, s["field"], s["field"]))
    m.append("""
public static String id(int w) {
  if (!ON) return null;
  boolean on = false;
  String v = null;
%s
  if (!on || v == null) return null;
  v = v.trim();
  return v.length() == 0 ? null : v;
}""" % "\n".join(chain))
    m.append("""
public static java.util.Map bridge() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    return o instanceof java.util.Map ? (java.util.Map) o : null;
  } catch (Throwable t) { return null; }
}""")
    m.append("""
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.Map b = bridge();
    if (b == null) return false;
    Object o = b.get(MUTE_KEY + u.toString());
    return (o instanceof Boolean) && !((Boolean) o).booleanValue();
  } catch (Throwable t) { return false; }
}""")
    m.append("""
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}""")
    m.append("""
public static com.hypixel.hytale.server.core.universe.PlayerRef ref(java.util.UUID u) {
  if (u == null) return null;
  try {
    com.hypixel.hytale.server.core.universe.Universe uni = com.hypixel.hytale.server.core.universe.Universe.get();
    return uni == null ? null : uni.getPlayer(u);
  } catch (Throwable t) { return null; }
}""")
    m.append("""
public static boolean playTo(com.hypixel.hytale.server.core.universe.PlayerRef pr, int w) {
  if (pr == null) return false;
  String id = id(w);
  if (id == null) return false;
  try {
    if (!pr.isValid()) return false;
    java.util.UUID u = pr.getUuid();
    if (muted(u)) { MUTED.incrementAndGet(); return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(u) + "|" + w, System.currentTimeMillis())) return false;
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return true;
  } catch (Throwable t) {
    if (WARNED.putIfAbsent("!play", Boolean.TRUE) == null) warn("could not play a sound (logged once): " + t);
    return false;
  }
}""")
    m.append("""
public static boolean play(java.util.UUID u, int w) {
  if (u == null || id(w) == null) return false;
  return playTo(ref(u), w);
}""")
    m.append("""
public static boolean ok(java.util.UUID u, String res, int w) {
  if (res == null || !res.startsWith("+")) return false;
  return play(u, w);
}""")
    m += list(extra_methods)
    loads = ["    ON = word(p.getProperty(\"sounds.enabled\"), true);"]
    for s in sounds:
        loads.append("    S_%s = word(p.getProperty(\"sound.%s\"), true);" % (s["field"], s["key"]))
        loads.append("    S_%s_ID = p.getProperty(\"sound.%s.id\", %s).trim();" % (s["field"], s["key"], json.dumps(s["id"])))
    loads += ["    " + x for x in extra_load]
    m.append("""
public static String text() {
  int n = 0;
%s
  return "sounds " + (ON ? "on" : "off") + " (" + n + " of %d)";
}""" % ("\n".join("  if (S_%s && S_%s_ID != null && S_%s_ID.trim().length() > 0) n++;" % (s["field"], s["field"], s["field"]) for s in sounds), len(sounds)))
    m.append("""
public static String load(java.nio.file.Path dir) {
  if (dir == null) return text();
  FILE = dir.resolve("sounds.properties");
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("sounds.properties.tmp");
      java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
%s
  } catch (Throwable t) { warn("could not read sounds.properties (the sounds keep their defaults): " + t); }
  return text();
}""" % "\n".join(loads))
    return fields, m


def file_text(mod, sounds, head=()):
    lines = ["# %s sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> %s -> Sounds," % (mod, mod[4:]),
             "# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);",
             "# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings."]
    lines += ["# " + h for h in head]
    lines.append("sounds.enabled=true")
    for s in sounds:
        lines.append("# %s: %s" % (s["label"], s["help"]))
        lines.append("sound.%s=true" % s["key"])
        lines.append("sound.%s.id=%s" % (s["key"], s["id"]))
    t = "\n".join(lines) + "\n"
    assert all(ord(c) < 128 for c in t) and "\\" not in t, "sounds.properties text must be plain ASCII"
    return t


def rows(cls, mod, sounds, cat="sounds"):
    """the Server Setup rows (kit tuples): master + per sound an on / off row and an id row, all bound to Skyy_<Mod>/sounds.properties"""
    f = "Skyy_%s/sounds.properties" % mod
    out = [("sounds.enabled", "Sounds", cat, "bool", "true", "", "", "", "", "live",
            "Off = %s plays no sound at all. Players can also mute every sound in /settings." % mod,
            "field:%s.ON@%s:sounds.enabled" % (cls, f))]
    for s in sounds:
        out.append(("sound.%s" % s["key"], "%s sound" % s["label"], cat, "bool", "true", "", "", "", "", "live",
                    "%s Off = silent." % s["help"], "field:%s.S_%s@%s:sound.%s" % (cls, s["field"], f, s["key"])))
        out.append(("sound.%s.id" % s["key"], "%s sound id" % s["label"], cat, "text", s["id"], "", "120", "", "", "live",
                    "A vanilla sound event id (try it with /soundtest). Empty = no sound.",
                    "field:%s.S_%s_ID@%s:sound.%s.id;check=%s.check" % (cls, s["field"], f, s["key"], cls)))
    for r in out:
        assert len(r[1]) <= 40 and len(r[10]) <= 100, r
    return out


def fragment(ver, mod, cls, pool, pkg_expr, sounds, extra_fields=(), extra_methods=(), extra_load=(), file_head=(), patch="the patch"):
    """the Python text a patch pastes into the generated build script (after `pool`, `PKG` and `OUT` exist, before any caller):
    the build-time Assets.zip check of every default id, then <Pfx>Snd compiled and written at once. sounds = [dict(key, field, label,
    id, help)] in the index order the callers use (play(u, 0) = the first)."""
    for s in sounds:
        assert s["key"].replace("_", "").isalnum() and s["field"].replace("_", "").isalnum() and s["field"].upper() == s["field"], s
        assert all(c.isalnum() or c == "_" for c in s["id"]), s
    fields, methods = _java(cls, mod, sounds, extra_fields, extra_methods, extra_load, file_head)
    for src in fields + methods:
        assert "'''" not in src
    t = []
    t.append("# ================= %s SOUND PASS ROUND 2: %s (pasted by %s from tools/soundpass_gen.py - research/Sound-Pass-Plan.md) =================" % (ver, cls, patch))
    t.append("# Vanilla sound event ids played BY ID, 2D to that player only (category UI); never throws; 0.5 s per player per sound; the per-player")
    t.append("# switch settings:sounds:<uuid> (Boolean FALSE on the bridge = silent; SkyyMenu 0.3.25 /settings); Skyy_%s/sounds.properties." % mod)
    t.append("import zipfile as _sndzf, jpype as _sndjp")
    t.append("_SNDZ = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), \"Assets.zip\")   # read-only")
    t.append("SOUND_IDS = set(os.path.basename(_n)[:-5] for _n in _sndzf.ZipFile(_SNDZ).namelist() if _n.startswith(\"Server/Audio/SoundEvents/\") and _n.endswith(\".json\"))")
    t.append("SND_SOUNDS = %s" % json.dumps([[s["key"], s["field"], s["label"], s["id"]] for s in sounds]))
    t.append("for _s in SND_SOUNDS:")
    t.append("    assert _s[3] in SOUND_IDS, \"%s: sound event %%s is not in Assets.zip\" %% _s[3]" % ver)
    t.append("_SND_PKG = (%s).rstrip(\".\")" % pkg_expr)
    t.append("_SND_FIELDS = [")
    for src in fields:
        t.append("    %s," % json.dumps(src))
    t.append("]")
    t.append("_SND_METHODS = [")
    for src in methods:
        t.append("    r'''%s'''," % src)
    t.append("]")
    t.append("_snd_cls = %s.makeClass(_SND_PKG + \".%s\")" % (pool, cls))
    t.append("for _src in _SND_FIELDS:")
    t.append("    _snd_cls.addField(_sndjp.JClass(\"javassist.CtField\").make(_src.replace(\"@SPKG@\", _SND_PKG), _snd_cls))")
    t.append("for _src in _SND_METHODS:")
    t.append("    _snd_cls.addMethod(_sndjp.JClass(\"javassist.CtNewMethod\").make(_src.replace(\"@SPKG@\", _SND_PKG), _snd_cls))")
    t.append("_snd_cls.writeFile(OUT)")
    t.append("print(\"%s: %d sound(s), every default id is in Assets.zip\")" % (cls, len(sounds)))
    return "\n".join(t) + "\n"


# ================================================================================================================ harness helpers
def bridge(J):
    """the skyy.bridge map of this JVM (created like every Skyy mod does when nobody made it yet)"""
    P = J("java.lang.System").getProperties()
    b = P.get("skyy.bridge")
    if b is None:
        b = J("java.util.concurrent.ConcurrentHashMap")()
        P.put("skyy.bridge", b)
    return b


def unit(K, st, Snd, Rows, Fn, pa, ua, mod, sounds, home, pfx="U"):
    """every generic path of a generated <Pfx>Snd, EXECUTED: sounds = the same dicts the patch used. pa = a Stage player (ua its uuid
    string), st.universe() already called. home = an empty scratch folder for sounds.properties."""
    import soundpass_kit as SK
    J = st.J
    Paths = J("java.nio.file.Paths")
    b = bridge(J)
    who = str(pa.getUsername())
    # ---- the file: a fresh folder gets the default file; the defaults; an old file without lines; typed values; off / off / empty
    os.makedirs(home, exist_ok=True)
    fp = os.path.join(home, "sounds.properties")
    if os.path.exists(fp):
        os.remove(fp)
    txt0 = str(Snd.load(Paths.get(home)))
    txt = open(fp, encoding="latin-1").read()
    K.check(txt == file_text(mod, sounds, ()) or all(("sound.%s.id=%s" % (s["key"], s["id"])) in txt for s in sounds),
            "%s FILE a fresh folder gets sounds.properties with every line" % pfx)
    K.check("sounds.enabled=true" in txt and all(("sound.%s=true" % s["key"]) in txt for s in sounds), "%s FILE master + per sound on" % pfx)
    K.check(bool(Snd.ON) and all(bool(getattr(Snd, "S_" + s["field"])) and str(getattr(Snd, "S_%s_ID" % s["field"])) == s["id"] and s["id"] in st.ids
                                 for s in sounds), "%s FILE the defaults (every id is in Assets.zip): %s" % (pfx, txt0))
    K.check(("of %d)" % len(sounds)) in txt0 and txt0.startswith("sounds on"), "%s text(): %s" % (pfx, txt0))
    open(fp, "w", encoding="latin-1").write("# nothing\n")
    for s in sounds:
        setattr(Snd, "S_%s_ID" % s["field"], "x")
    Snd.load(Paths.get(home))
    K.check(bool(Snd.ON) and all(str(getattr(Snd, "S_%s_ID" % s["field"])) == s["id"] for s in sounds), "%s FILE a file without the lines = the defaults" % pfx)
    K.check(open(fp, encoding="latin-1").read() == "# nothing\n", "%s FILE an existing file is never rewritten by load()" % pfx)
    s0 = sounds[0]
    open(fp, "w", encoding="latin-1").write("sounds.enabled=off\nsound.%s=no\nsound.%s.id=\n" % (s0["key"], s0["key"]))
    Snd.load(Paths.get(home))
    K.check(not bool(Snd.ON) and not bool(getattr(Snd, "S_" + s0["field"])) and str(getattr(Snd, "S_%s_ID" % s0["field"])) == "",
            "%s FILE off / off / empty read" % pfx)
    open(fp, "w", encoding="latin-1").write("sound.%s.id=  SFX_Coins_Hit  \nsounds.enabled=maybe\n" % s0["key"])
    Snd.load(Paths.get(home))
    K.check(bool(Snd.ON) and str(getattr(Snd, "S_%s_ID" % s0["field"])) == "SFX_Coins_Hit", "%s FILE a typed id (trimmed) is read; a junk bool = default" % pfx)
    os.remove(fp)
    Snd.load(Paths.get(home))
    # ---- rows + the kit's own check= hook (what a Server Setup edit runs)
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "sounds.enabled", [("sound.%s" % s["key"], "sound.%s.id" % s["key"], s["id"]) for s in sounds], prefix=pfx + " ")
    K.check(all(rows[k][2] == "sounds" for k in ["sounds.enabled"] + ["sound.%s" % s["key"] for s in sounds] + ["sound.%s.id" % s["key"] for s in sounds]),
            "%s ROW all in the Sounds category" % pfx)
    rk = "sound.%s.id" % s0["key"]
    K.check("no sound event" in (SK.kit_check(Fn, Rows, rk, SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, rk, "a b") is not None
            and SK.kit_check(Fn, Rows, rk, "x" * 121) is not None
            and SK.kit_check(Fn, Rows, rk, "") is None and SK.kit_check(Fn, Rows, rk, "SFX_Coins_Land") is None,
            "%s CHECK the kit's check= hook refuses a missing id / a space / 121 chars, takes empty and a real id" % pfx)
    # ---- id(w): master / per sound / empty
    for i, s in enumerate(sounds):
        K.check(str(Snd.id(i)) == s["id"], "%s id(%d) = %s" % (pfx, i, s["id"]))
    K.check(Snd.id(len(sounds)) is None and Snd.id(-1) is None, "%s id(unknown) = null" % pfx)
    Snd.ON = False
    K.check(all(Snd.id(i) is None for i in range(len(sounds))), "%s master off: every id null" % pfx)
    Snd.ON = True
    setattr(Snd, "S_" + s0["field"], False)
    K.check(Snd.id(0) is None, "%s the sound row off: null" % pfx)
    setattr(Snd, "S_" + s0["field"], True)
    setattr(Snd, "S_%s_ID" % s0["field"], "  ")
    K.check(Snd.id(0) is None, "%s an empty id: null" % pfx)
    setattr(Snd, "S_%s_ID" % s0["field"], s0["id"])
    K.check(int(Snd.idx(s0["id"])) == st.ids[s0["id"]] and int(Snd.idx(SK.BAD_ID)) == -2147483648 and int(Snd.idx(None)) == -2147483648, "%s idx" % pfx)
    # ---- playTo: once, the gate holds a repeat, a different sound is its own gate
    Snd.LAST.clear()
    st.clear()
    K.check(bool(Snd.playTo(pa, 0)) and not bool(Snd.playTo(pa, 0)), "%s playTo once, the 0.5 s gate holds the repeat" % pfx)
    K.eq(st.sounds(), [(who, s0["id"], "UI", "2d")], "%s ... ONE PlaySoundEvent2D to that player, category UI" % pfx)
    if len(sounds) > 1:
        st.clear()
        K.check(bool(Snd.playTo(pa, 1)) and st.sounds() == [(who, sounds[1]["id"], "UI", "2d")], "%s another sound has its own gate" % pfx)
    Snd.LAST.clear()
    k0 = "%s|0" % ua
    Snd.LAST.put(k0, J("java.lang.Long")(int(J("java.lang.System").currentTimeMillis()) - 600))
    st.clear()
    K.check(bool(Snd.playTo(pa, 0)) and len(st.sounds()) == 1, "%s the gate opens after 0.5 s" % pfx)
    # ---- the per-player switch (settings:sounds:<uuid>)
    mk = "settings:sounds:" + ua
    for what, val, plays in (("FALSE (muted in /settings)", J("java.lang.Boolean").FALSE, False), ("TRUE", J("java.lang.Boolean").TRUE, True),
                             ("a String 'false' (not a Boolean - ignored)", "false", True), ("absent", None, True)):
        Snd.LAST.clear()
        st.clear()
        m0 = int(Snd.MUTED.get())
        if val is None:
            b.remove(mk)
        else:
            b.put(mk, val)
        r = bool(Snd.playTo(pa, 0))
        K.check(r == plays and len(st.sounds()) == (1 if plays else 0) and int(Snd.MUTED.get()) == m0 + (0 if plays else 1),
                "%s per-player switch %s -> %s" % (pfx, what, "plays" if plays else "silent, counted in MUTED"))
    b.put(mk, J("java.lang.Boolean").FALSE)
    Snd.LAST.clear()
    st.clear()
    K.check(not bool(Snd.play(J("java.util.UUID").fromString(ua), 0)) and st.sounds() == [], "%s play(uuid) muted: silent" % pfx)
    b.remove(mk)
    # ---- a missing id = one WARN, nothing played; no player / an offline uuid = nothing
    Snd.LAST.clear()
    st.clear()
    w0 = int(Snd.WARNS.get())
    setattr(Snd, "S_%s_ID" % s0["field"], SK.BAD_ID)
    K.check(not bool(Snd.playTo(pa, 0)) and not bool(Snd.playTo(pa, 0)) and st.sounds() == [] and int(Snd.WARNS.get()) == w0 + 1,
            "%s a missing id: nothing played, ONE warning" % pfx)
    setattr(Snd, "S_%s_ID" % s0["field"], s0["id"])
    K.check(not bool(Snd.playTo(None, 0)) and not bool(Snd.play(None, 0)) and not bool(Snd.play(J("java.util.UUID").fromString("00000000-0000-0000-0000-00000000dead"), 0))
            and st.sounds() == [], "%s no player / an offline uuid: nothing" % pfx)
    # ---- play(uuid) through Universe.getPlayer; ok(uuid, "+...")
    Snd.LAST.clear()
    st.clear()
    U = J("java.util.UUID").fromString(ua)
    K.check(bool(Snd.play(U, 0)) and st.sounds() == [(who, s0["id"], "UI", "2d")], "%s play(uuid) finds the online player" % pfx)
    Snd.LAST.clear()
    st.clear()
    K.check(not bool(Snd.ok(U, "-refused", 0)) and not bool(Snd.ok(U, None, 0)) and not bool(Snd.ok(U, "=info", 0)) and st.sounds() == []
            and bool(Snd.ok(U, "+done", 0)) and len(st.sounds()) == 1, "%s ok(): only a '+' result plays" % pfx)
    Snd.LAST.clear()
    st.clear()


def static_only_snd(K, PW, jar, pkg, cls):
    """only <cls>.playTo calls SoundUtil.playSoundEvent2dToPlayer(PlayerRef, int, ...) among the NEW code (old direct calls listed)"""
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    return sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), g


# ================================================================================================================ patch helper
class Patch(object):
    """the round 1 patch pattern (tools/quests_0_3_1_patch.py) as a helper: read the previous GENERATED script (line endings kept), rep()
    asserts each anchor occurs exactly once, finish() undoes every change on a copy and compares with the source (nothing else changed),
    compiles the result and writes it."""

    def __init__(self, src, dst):
        CR, LF = chr(13), chr(10)
        self.src, self.dst = src, dst
        raw = open(src, encoding="utf8", newline="").read()
        self.NL = CR + LF if (CR + LF) in raw else LF
        self.s = raw.replace(CR + LF, LF)
        self.OLD = self.s
        self.changes = []

    def has(self, t):
        return t in self.s

    def rep(self, old, new):
        n = self.s.count(old)
        assert n == 1, "anchor count %d: %s" % (n, old[:200])
        self.s = self.s.replace(old, new, 1)
        self.changes.append((new, old))

    def finish(self):
        u = self.s
        for new, old in reversed(self.changes):
            assert u.count(new) == 1, "a change is not unique any more: %s" % new[:100]
            u = u.replace(new, old, 1)
        assert u == self.OLD, "the generated script differs from its source outside the recorded changes"
        compile(self.s, self.dst, "exec")
        LF = chr(10)
        open(self.dst, "w", encoding="utf8", newline="").write(self.s.replace(LF, self.NL) if self.NL != LF else self.s)
        print("wrote", self.dst, "(%d lines; the source had %d; %d changes)" % (self.s.count(LF), self.OLD.count(LF), len(self.changes)))


def kit_set(K, J, Snd, CP, Fn, mods, mod, sounds, pfx="KIT"):
    """THE KIT end to end on a scratch mods folder: <Pfx>Snd.load + CfgPub.start, then Server Setup edits through the kit's own console
    path (CfgFn.cmdSetConsole = what an in-game edit runs: check= hook, field, file line): an id row to another real id (field + file),
    a missing id refused (field unchanged), the sound row off; CfgPub.shutdown flushes the file. Restores the defaults afterwards."""
    Paths = J("java.nio.file.Paths")
    s0 = sounds[0]
    d = os.path.join(mods, "Skyy_" + mod)
    os.makedirs(d, exist_ok=True)
    Snd.load(Paths.get(d))
    CP.start(Paths.get(mods), J("com.hypixel.hytale.logger.HytaleLogger").get(mod))
    r1 = str(Fn.cmdSetConsole("sound.%s.id" % s0["key"], "SFX_Coins_Hit"))
    K.check(str(getattr(Snd, "S_%s_ID" % s0["field"])) == "SFX_Coins_Hit", "%s a Server Setup edit of the id row sets the field at once (live): %s" % (pfx, r1))
    r2 = str(Fn.cmdSetConsole("sound.%s.id" % s0["key"], "SFX_Skyy_No_Such_Sound"))
    K.check(str(getattr(Snd, "S_%s_ID" % s0["field"])) == "SFX_Coins_Hit" and "no sound event" in r2, "%s a missing id is refused by check=, field unchanged: %s" % (pfx, r2))
    r3 = str(Fn.cmdSetConsole("sound.%s" % s0["key"], "false"))
    K.check(not bool(getattr(Snd, "S_" + s0["field"])) and Snd.id(0) is None, "%s the sound row off (live): %s" % (pfx, r3))
    r4 = str(Fn.cmdSetConsole("sounds.enabled", "false"))
    K.check(not bool(Snd.ON), "%s the master off (live): %s" % (pfx, r4))
    CP.shutdown()
    t = open(os.path.join(d, "sounds.properties"), encoding="latin-1").read()
    K.check(("sound.%s.id=SFX_Coins_Hit" % s0["key"]) in t and ("sound.%s=false" % s0["key"]) in t and "sounds.enabled=false" in t,
            "%s the kit wrote the three changed lines into sounds.properties" % pfx)
    Snd.load(Paths.get(d))
    K.check(not bool(Snd.ON) and str(getattr(Snd, "S_%s_ID" % s0["field"])) == "SFX_Coins_Hit", "%s a restart reads the edited file" % pfx)
    os.remove(os.path.join(d, "sounds.properties"))
    Snd.load(Paths.get(d))
    K.check(bool(Snd.ON) and str(getattr(Snd, "S_%s_ID" % s0["field"])) == s0["id"], "%s defaults back" % pfx)


def live_twice(K, before, after1, after2, pfx="DS", also=()):
    """start twice on the live copy: the first start adds ONLY sounds.properties (+ the kit's own history / change files, + `also` = files
    the previous version writes on its own first start when the live copy never ran it), changes no existing file; the second start
    changes nothing"""
    new = sorted(set(after1) - set(before))
    changed = sorted(k for k in before if after1.get(k) != before[k])
    K.check("sounds.properties" in new and all(n == "sounds.properties" or n in also or n.startswith(("config-history", "config-changes")) for n in new) and not changed,
            "%s the first start adds sounds.properties (and only kit files), no existing file changes: new %s changed %s" % (pfx, new, changed))
    K.check(after1 == after2, "%s the second start changes nothing" % pfx)
