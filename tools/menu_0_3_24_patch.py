"""Derive SkyyMenu/build_skyymenu_0.3.24.py from the LIVE SkyyMenu 0.3.23 (python tools/menu_0_3_24_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_23_patch.py -> 0.3.23 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch) -> this patch -> 0.3.24. The harness SkyyMenu/test_skyymenu_0.3.24.py is its own file.

0.3.24 (2026-10-14) = SOUND PASS ROUND 1 (/soundtest) + THE REBIRTH BUTTONS ON THE ADMIN PAGE. Skyy 2026-10-14 ~13:45, to the main session's
list of queued rounds incl. "Sound pass round 1, with /soundtest so you can try the sounds" and "the Shards and Rebirth buttons on the admin
page": "Run the queue". research/Sound-Pass-Plan.md question 1 default: "[yes, in the SkyyMenu admin page]".
  1. /soundtest (admin: skyymenu.modconfig, the Server Setup node; requirePermission on the command and its usage variant) - Skyy
     auditions vanilla sounds by ear, 2D to the admin only (SoundUtil.playSoundEvent2dToPlayer, category UI, the packet every SkyWynn
     sound helper sends):
       /soundtest            the help (+ how many ids the list has)
       /soundtest list       the numbered ids this round's mods use, each with where (Quests task done, Bank interest, ...)
       /soundtest more       the plan's candidate ids for later rounds (research/Sound-Pass-Plan.md: level up, rebirth, casts ...)
       /soundtest <n>        plays number n of the list (1 ..), and says its id + use
       /soundtest next | prev  plays the next / previous one (per admin; starts at 1)
       /soundtest <id>       plays ANY vanilla sound event id (SFX_...; letters, digits, _), e.g. one from Assets.zip
     A missing id / number is answered, never thrown. Every list id is checked against Assets.zip at build time. No file, no setting.
     Pack note (PROJECT-RULES "check existing mods"): no installed mod offers a sound browser; the engine has no /playsound for 2D ids.
  2. THE ADMIN PAGE (OpsPage, 0.3.23): + 4 SkyyRebirth buttons on Players (SkyyRebirth 0.3.1 made crashtest / points / refund
     SUB-COMMANDS - tools/rebirth_0_3_1_patch.py - so each line now parses in the engine; 0.3.23 left them out because 0.3's GREEDY
     variant refused 2- and 3-word lines):
       Rebirth crash test   /rebirthadmin crashtest <Text: point 0-7>   danger (press twice) AND the command asks again: 4 presses in all
                            (fix 2026-10-14: without the page confirm, a page "+Ran" answer read as success and a 2nd press started it)
       Rebirth test points  /rebirthadmin points <Text: arm or all> 100  (test points on YOUR active profile; arm = Class, Mining ...)
       Wipe rebirth arm     /rebirthadmin points <Text: arm or all> reset   danger (press twice)
       Refund rebirth arm   /rebirthadmin refund <Text: arm or all>         danger (press twice)
     + 3 Diagnostics buttons: "Sound list" (/soundtest list), "Next sound" (/soundtest next), "Play sound" (/soundtest <Text: id or
     number>). The rebirth lines have their sub-command depth 1 (OPS_DEPTH_EXCEPT, now checked before OPS_ARG_ROOTS); the menu's own rows
     are checked against THIS script (they are new in this build). The Shards buttons wait for the shards03 round (task text).
  No saved data, no setting, no bridge key. ROUND_PINS = {}. Rollback to 0.3.23: safe (/soundtest and the 7 buttons go).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.23.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.24.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.23"' in s and "0.3.23: THE ADMIN PAGE" in s and "SoundTest" not in s, "not the generated 0.3.23 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.23":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.23" % _set.get("SkyyMenu"))
assert _set is None or tuple(int(x) for x in _set.get("SkyyRebirth", "0").split(".")) >= (0, 3, 1), "the rebirth buttons need SkyyRebirth 0.3.1 (its sub-commands) in the SET"

# ---------------------------------------------------------------------------------------------------------------- the sound list
SOUND_LIST = [   # (id, where it is used) - this round's mods first (the defaults of their Server Setup sound rows), then 0.2's discovery sounds
    ("SFX_Dungeon_Checkpoint_Activate", "Quests: task done"),
    ("SFX_Event_Chapter_1_Complete_Sting", "Quests: quest line done"),
    ("SFX_Coins_Land", "Quests: reward paid"),
    ("SFX_Drag_Items_Paper", "Quests: talk to a quest NPC"),
    ("SFX_Chest_Wooden_Open_Player", "Exploration: Lost Loot / supply drop claimed"),
    ("SFX_Wood_Land", "Exploration: supply drop lands"),
    ("SFX_Coffer_Goblin_Reward", "Exploration reveal: Rare card; Bank: interest paid"),
    ("SFX_Memories_Unlock_Local", "Exploration reveal: Legendary card"),
    ("SFX_Portal_Neutral_Teleport_Local", "Islands: /island or /hub arrival"),
    ("SFX_Deployable_Totem_Heal_Spawn", "Pets: pet into a slot"),
    ("SFX_Deployable_Totem_Heal_Despawn", "Pets: pet out of its slot"),
    ("SFX_Discovery_Z1_Short", "Exploration: discovery spot"),
    ("SFX_Discovery_Z1_Medium", "Exploration: secret spot"),
    ("SFX_Discovery_Z2_Medium", "Exploration: checklist entry"),
]
SOUND_MORE = [   # research/Sound-Pass-Plan.md candidates for the later rounds (S1-S4)
    ("SFX_Workbench_Upgrade_Complete_Default", "plan: skill level up / upgrades"),
    ("SFX_Runebinders_Lattice_Unlock_Local", "plan: tree node / recipe / slot unlock"),
    ("SFX_MemoryRestored", "plan: big reward"),
    ("SFX_Divine_Respawn", "plan: rebirth done / big heal"),
    ("SFX_Portal_Void", "plan: rebirth confirm"),
    ("SFX_Void_Encroaching", "plan: rebirth confirm (dark)"),
    ("SFX_Portal_Neutral_Open", "plan: profile switch / shard portal"),
    ("SFX_Coins_Hit", "plan: bank deposit / withdraw"),
    ("SFX_Coins_Break", "plan: death coin loss"),
    ("SFX_Drop_Items_Paper", "plan: AH listed / quest skipped"),
    ("SFX_Generic_Crafting_Failed", "plan: cooldown / no Mana / refused"),
    ("SFX_Incorrect_Tool", "plan: tool tier refused"),
    ("SFX_Ability_Wind_Strike_Imbue_Local", "plan: ability cast (generic)"),
    ("SFX_Ability_Enrage", "plan: rage ability"),
    ("SFX_Ability_Ground_Slam_Impact", "plan: slam ability"),
    ("SFX_Chest_Legendary_FirstOpen_Player", "plan: identify (rare and up)"),
    ("SFX_Weapon_Bench_Craft", "plan: reforge a weapon"),
    ("SFX_Armour_Bench_Craft", "plan: reforge armour"),
    ("SFX_Drag_Items_Gems", "plan: accessory equip"),
    ("SFX_Crops_Grow_Stage_Complete", "plan: double drop / totem tick"),
    ("SFX_Furnace_Bench_Processing_Complete", "plan: compactor / compressor"),
    ("SFX_Crystal_Hit", "plan: collect from a shard"),
    ("SFX_Tornado", "plan: monk burst"),
]

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.23: THE ADMIN PAGE''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.24: SOUND PASS ROUND 1 + THE REBIRTH ADMIN BUTTONS (notes: tools/menu_0_3_24_patch.py; research/Sound-Pass-Plan.md): /soundtest
       (skyymenu.modconfig) plays any vanilla sound event 2D to the admin - list (the ids this round's mods use, with where), more (the
       plan's candidates), <n>, next, prev, <SFX id>. The Admin page: + Rebirth crash test / test points / wipe arm / refund arm (SkyyRebirth
       0.3.1 sub-commands, depth 1) on Players, + Sound list / Next sound / Play sound on Diagnostics. No saved data. ROUND_PINS = {}.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.24.py.
0.3.23: THE ADMIN PAGE''')
rep('VERSION = "0.3.23"\n', 'VERSION = "0.3.24"\n')
rep('''                  "/modconfig admin - (admin) the Admin page: buttons for the admin commands"]},   # 0.3.23''',
    '''                  "/modconfig admin - (admin) the Admin page: buttons for the admin commands",   # 0.3.23
                  "/soundtest - (admin) hear any vanilla sound by id or number (list)"]},   # 0.3.24''')

# ---------------------------------------------------------------------------------------------------------------- the OPS rows
rep('''    (2, "Recover rebirths", "rebirthadmin recover", "skyyrebirth.admin", "SkyyRebirth", True, "", ""),
''', '''    (2, "Recover rebirths", "rebirthadmin recover", "skyyrebirth.admin", "SkyyRebirth", True, "", ""),
    # 0.3.24: SkyyRebirth 0.3.1's sub-commands (they parse now); crash test = a danger row (page confirm) on top of the command's own
    # type-it-twice confirm - it resets the admin's real active profile, so one stray page press must never start it
    (2, "Rebirth crash test", "rebirthadmin crashtest {t}", "skyyrebirth.admin", "SkyyRebirth", True, "point 0-7", ""),
    (2, "Rebirth test points", "rebirthadmin points {t} 100", "skyyrebirth.admin", "SkyyRebirth", False, "arm or all", ""),
    (2, "Wipe rebirth arm", "rebirthadmin points {t} reset", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
    (2, "Refund rebirth arm", "rebirthadmin refund {t}", "skyyrebirth.admin", "SkyyRebirth", True, "arm or all", ""),
''')
rep('''    (3, "Plugin list", "plugin list", "", "Hytale", False, "", ""),
]''', '''    (3, "Plugin list", "plugin list", "", "Hytale", False, "", ""),
    # 0.3.24: /soundtest (this jar; the Server Setup node)
    (3, "Sound list", "soundtest list", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (3, "Next sound", "soundtest next", "skyymenu.modconfig", "SkyyMenu", False, "", ""),
    (3, "Play sound", "soundtest {t}", "skyymenu.modconfig", "SkyyMenu", False, "sound id or number", ""),
]''')
rep('''    "questadmin place set hub.fishing": 1,
}''', '''    "questadmin place set hub.fishing": 1,
    # 0.3.24: SkyyRebirth 0.3.1 sub-commands under an argument root (checked before OPS_ARG_ROOTS)
    "rebirthadmin crashtest {t}": 1, "rebirthadmin points {t} 100": 1, "rebirthadmin points {t} reset": 1, "rebirthadmin refund {t}": 1,
}''')
rep('''OPS_ARG_ROOTS = ("merchantadmin", "pdadmin", "petadmin", "requipadmin", "fishadmin", "rebirthadmin")''',
    '''OPS_ARG_ROOTS = ("merchantadmin", "pdadmin", "petadmin", "requipadmin", "fishadmin", "rebirthadmin", "soundtest")   # 0.3.24: + soundtest''')
rep('''    d = 0 if line.split(" ")[0] in OPS_ARG_ROOTS else OPS_DEPTH_EXCEPT.get(line, len(lit))''',
    '''    d = OPS_DEPTH_EXCEPT[line] if line in OPS_DEPTH_EXCEPT else (0 if line.split(" ")[0] in OPS_ARG_ROOTS else len(lit))   # 0.3.24: the exception first''')
rep('''    _sp = _script(_mod, _set_live[_mod])''', '''    _sp = os.path.abspath(__file__) if _mod == "SkyyMenu" else _script(_mod, _set_live[_mod])   # 0.3.24: the menu's own rows = this script''')

# ---------------------------------------------------------------------------------------------------------------- the classes
rep('''acmd = mk("AdminCmd", T["APC"])
''', '''acmd = mk("AdminCmd", T["APC"])
snt  = mk("SoundTest")       # 0.3.24: /soundtest - the list + the 2D play (sound pass round 1)
stv  = mk("SoundTestArgCmd", T["APC"])   # 0.3.24: the usage variant /soundtest <what>
stm  = mk("SoundTestCmd", T["APC"])      # 0.3.24: /soundtest
''')
rep('''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, pl)''',
    '''         scl, stp, sta, stc, pet, lay, lsv, spt, mio, midx, gsv, mhk, hko, ops, snt, stv, stm, pl)''')

SOUNDTEST = r'''
# ================= 0.3.24 /soundtest (skyymenu.modconfig): hear any vanilla sound event 2D (research/Sound-Pass-Plan.md question 1) =================
import zipfile as _zf
_SNDZ = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
SOUND_IDS = set(os.path.basename(n)[:-5] for n in _zf.ZipFile(_SNDZ).namelist() if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))
SND_LIST = @LIST@
SND_MORE = @MORE@
_snd_all = SND_LIST + SND_MORE
assert all(i in SOUND_IDS for i, _u in _snd_all), [i for i, _u in _snd_all if i not in SOUND_IDS]
assert len(set(i for i, _u in _snd_all)) == len(_snd_all), "a sound id twice in the /soundtest list"
assert all(re.match(r"^[A-Za-z0-9_]{1,120}$", i) and all(32 <= ord(c) < 127 for c in u) for i, u in _snd_all)
F(snt, "public static final String[] IDS = %s;" % jarr([i for i, _u in _snd_all]))
F(snt, "public static final String[] USES = %s;" % jarr([u for _i, u in _snd_all]))
F(snt, "public static final int IN_USE = %d;" % len(SND_LIST))
F(snt, "public static final java.util.concurrent.ConcurrentHashMap CURSOR = new java.util.concurrent.ConcurrentHashMap();")
F(snt, "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();")
M(snt, r"""
public static int idx(String id) {
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(id);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
M(snt, r"""
public static boolean okId(String s) {
  if (s == null || s.length() == 0 || s.length() > 120) return false;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return false;
  }
  return true;
}""")
M(snt, r"""
public static int num(String s) {
  if (s == null || s.length() == 0 || s.length() > 4) return -1;
  for (int i = 0; i < s.length(); i++) if (s.charAt(i) < '0' || s.charAt(i) > '9') return -1;
  return Integer.parseInt(s);
}""")
# 2D to that player only (UI); the answer line ("+" played, "-" why not)
M(snt, r"""
public static String play(@PR@ pr, String id, String what) {
  if (pr == null) return "-No player.";
  int i = idx(id);
  if (i == Integer.MIN_VALUE || i == 0) return "-The game has no sound event '" + id + "'. Ids look like SFX_Coins_Land - /soundtest list.";
  try {
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return "+Playing " + what + " (only you hear it).";
  } catch (Throwable t) { @MU@.warn("/soundtest could not play " + id + ": " + t); return "-Could not play it - see the server log."; }
}""")
M(snt, r"""
public static String label(int n) {
  return "#" + n + " " + IDS[n - 1] + " - " + USES[n - 1];
}""")
M(snt, r"""
public static java.util.ArrayList help() {
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("=/soundtest list - the " + IN_USE + " sounds SkyWynn plays now, numbered (/soundtest more = " + (IDS.length - IN_USE) + " ideas for later)");
  out.add("=/soundtest <number> | next | prev - play one from the list; /soundtest <id> - play any vanilla sound id (SFX_...)");
  out.add("=Change a mod's sound in Server Setup -> <mod> -> Sounds (each sound: on / off + its id).");
  return out;
}""")
# the whole command (pure but the play): lines to send. cursor per player for next / prev (1-based, wraps over the whole list)
M(snt, r"""
public static java.util.ArrayList run(@PR@ pr, String arg) {
  java.util.ArrayList out = new java.util.ArrayList();
  String a = arg == null ? "" : arg.trim();
  if (a.length() == 0 || a.equalsIgnoreCase("help")) return help();
  if (a.equalsIgnoreCase("list") || a.equalsIgnoreCase("more") || a.equalsIgnoreCase("all")) {
    boolean more = a.equalsIgnoreCase("more");
    int from = more ? IN_USE + 1 : 1;
    int to = a.equalsIgnoreCase("list") ? IN_USE : IDS.length;
    out.add("=" + (more ? "Sound ideas from the sound plan (not played yet):" : (to == IDS.length ? "Every listed sound:" : "Sounds SkyWynn plays now:")));
    for (int n = from; n <= to; n++) out.add(" " + label(n));
    out.add("=Play one: /soundtest <number> (or next / prev).");
    return out;
  }
  java.util.UUID u = null;
  try { u = pr == null ? null : pr.getUuid(); } catch (Throwable t) { u = null; }
  int n = num(a);
  if (a.equalsIgnoreCase("next") || a.equalsIgnoreCase("prev")) {
    Object o = u == null ? null : CURSOR.get(u);
    int c = o instanceof Integer ? ((Integer) o).intValue() : 0;
    if (a.equalsIgnoreCase("next")) c = c >= IDS.length ? 1 : c + 1;
    else c = c <= 1 ? IDS.length : c - 1;
    n = c;
  }
  if (n >= 0) {
    if (n < 1 || n > IDS.length) { out.add("-There is no #" + n + " - the list has 1 to " + IDS.length + " (/soundtest list)."); return out; }
    if (u != null) CURSOR.put(u, Integer.valueOf(n));
    out.add(play(pr, IDS[n - 1], label(n)));
    return out;
  }
  if (!okId(a)) { out.add("-A sound id is letters, digits and _ only (like SFX_Coins_Land), or a list number."); return out; }
  int k = -1;
  for (int j = 0; j < IDS.length; j++) if (IDS[j].equalsIgnoreCase(a)) k = j;
  out.add(play(pr, k >= 0 ? IDS[k] : a, k >= 0 ? label(k + 1) : a));
  return out;
}""")
M(snt, r"""
public static void send(@PR@ pr, java.util.ArrayList lines) {
  for (int i = 0; i < lines.size(); i++) {
    String l = String.valueOf(lines.get(i));
    char c = l.length() > 0 ? l.charAt(0) : ' ';
    String t = c == '+' || c == '-' || c == '=' ? l.substring(1) : l;
    try { pr.sendMessage(@MSG@.raw("[Sound test] " + t).color(c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@"))); } catch (Throwable x) { }
  }
}""".replace("@GOOD@", SUI.COLOR["success"]).replace("@BAD@", SUI.COLOR["error"]).replace("@INFO@", SUI.COLOR["info"]))
F(stv, "public @RA@ whatArg;")
C(stv, r"""
public SoundTestArgCmd() {
  super("(admin) hear a vanilla sound: /soundtest list | more | <number> | next | prev | <sound id>");
  requirePermission(@MD@.ADMIN_NODE);
  this.whatArg = withRequiredArg("what", "list, more, a list number, next, prev or a sound id like SFX_Coins_Land", @ATY@.STRING);
}""")
M(stv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); } catch (Throwable t) { a = null; }
  try { @PKG@.SoundTest.send(pr, @PKG@.SoundTest.run(pr, a)); }
  catch (Throwable t) { @MU@.warn("/soundtest failed: " + t); }
}""")
C(stm, r"""
public SoundTestCmd() {
  super("soundtest", "(admin) hear any vanilla sound by id or by number - /soundtest list");
  requirePermission(@MD@.ADMIN_NODE);
  addUsageVariant(new @PKG@.SoundTestArgCmd());
}""")
M(stm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.SoundTest.send(pr, @PKG@.SoundTest.help()); } catch (Throwable t) { @MU@.warn("/soundtest failed: " + t); }
}""")
'''.replace("@LIST@", repr(SOUND_LIST)).replace("@MORE@", repr(SOUND_MORE))
rep('''
# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================''', SOUNDTEST + '''
# ================= MenuPageFactory (right-click on the menu item -> OpenCustomUI "SkyyMenu") =================''')
rep('''  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());
''', '''  getCommandRegistry().registerCommand(new @PKG@.AdminCmd());
  // 0.3.24: /soundtest - a clash with another mod's /soundtest is logged and the menu still loads
  try { getCommandRegistry().registerCommand(new @PKG@.SoundTestCmd()); }
  catch (Throwable t) { @PKG@.MenuUtil.warn("could not register /soundtest (another mod may own it): " + t); }
''')
rep('''Server Setup: /modconfig (/serversetup) for admins; Stats page''', '''Server Setup: /modconfig (/serversetup) for admins, /soundtest (" + @PKG@.SoundTest.IDS.length + " sounds listed); Stats page''')

# ---------------------------------------------------------------------------------------------------------------- done
assert s.count("SoundTest") >= 10 and s.count('mk("SoundTest")') == 1
_i = s.index
assert _i('snt  = mk("SoundTest")') < _i("public static java.util.ArrayList run(@PR@ pr, String arg)") < _i("public SoundTestArgCmd()") < _i("public SoundTestCmd()")
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.23 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.23 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
