"""Test harness for tools/skyyui.py (the shared vanilla UI kit).

    python tools/skyyui_test.py [--assets <Assets.zip>] [--dir <scratch folder>] [--no-java] [--keep]

Phase 1  verify() against Assets.zip (READ-ONLY): every vanilla value / texture / sound / item quality frame the kit copies; a
         missing Assets.zip and a drifted document must fail loudly; the Java emitters refuse to run before verify() passed.
Phase 2  structure: the kit's style values (buttons in every kind / size / sound, scrollbar, tooltip, checkbox, dropdown, title,
         list rows, nav buttons, option cards) are parsed and compared KEY BY KEY with the vanilla definitions they copy, expanded
         from Common.ui / Sounds.ui / the vanilla pages (spreads ...@X, references @X / $Sounds.@X, constructors) - not just needle
         presence.
Phase 3  every builder: ids (no underscores, the page prefix, no duplicates), inline text rule (also a trailing newline), sizes
         (page fits 1080, fit(), Primary width, positive sizes, padding), the markup parses (skyyui.check_markup: balanced brackets /
         quotes, every { opens an element, root anchor Width / Height only), every texture / sound path in any output is one verify()
         proves, every colour is a kit / rarity colour, Java literal escaping round trips, J() runtime values, typed b.set values,
         trial gating of the UNVERIFIED elements, the probe pages (one per UNVERIFIED feature, each fits and checks), the rarity
         palette = Skyy's lock (and the SkyyGear 0.1 / SkyySacks 0.7.7 tables), every kit function the style guide names exists.
         Reused repo validation: SkyyRanks 0.1.1 _check_ui (read from the build script and run with this test's prefix) and
         tools/ci/lint.py's underscore-id rule (ID_RE / UI_HINT read from lint.py) on the Java lines, plus lint.py's kit warning rules.
Phase 4  (a JVM with javassist; skipped with --no-java or when jpype is missing) compiles the kit's Java output with javassist -
         String fields from java_field / emit_fields, methods built from java_expr with runtime values, page_shell().java()
         statements (static and runtime sizes) and every probe page against a stub builder with the set(String, String / int / float
         / boolean) overloads, typed java_set lines, java_status_methods - loads the classes and compares every string with Python.
         Java runs with -XX:-UsePerfData and TEMP / TMP / java.io.tmpdir in the scratch folder.
Default scratch folder: tools/dev/scratch/skyyui-test (git-ignored), deleted at the end unless --keep. Prints "N ok, 0 fail";
exit code 1 on any failure.
"""
import os, sys, re, ast, shutil, zipfile, posixpath

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import skyyui as UI


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(HERE, "dev", "scratch", "skyyui-test")))
ASSETS = arg("--assets")
KEEP = "--keep" in sys.argv
NOJAVA = "--no-java" in sys.argv
P = "SkyyT"                       # the test page prefix
OKS = [0]
FAILS = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)


def raises(fn, exc, what, contains=None):
    try:
        fn()
    except exc as e:
        check(contains is None or contains in str(e), "%s (message was: %s)" % (what, str(e)[:160]))
        return
    except BaseException as e:      # noqa - a wrong exception type is a failure, not a crash
        FAILS.append("%s: raised %s (%s) instead of %s" % (what, type(e).__name__, str(e)[:120], exc.__name__))
        return
    FAILS.append(what + ": did not raise")


# ================================================================= reused repo validation
RANKS_NS = {"re": re, "PREFIX": P}      # the globals of the reused _check_ui: PREFIX is set per page before each call


def ranks_check_ui():
    """SkyyRanks 0.1.1's _check_ui, read from its build script, with the page prefix (RANKS_NS["PREFIX"]) instead of SkyyRk."""
    path = os.path.join(ROOT, "SkyyRanks", "build_skyyranks_0.1.1.py")
    if not os.path.isfile(path):
        return None
    text = open(path, encoding="utf-8").read()
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and node.name == "_check_ui":
            src = ast.get_source_segment(text, node).replace('eid.startswith("SkyyRk")', "eid.startswith(PREFIX)")
            exec(compile(src, path, "exec"), RANKS_NS)
            return RANKS_NS["_check_ui"]
    return None


def lint_id_rule():
    """tools/ci/lint.py's underscore-id rule: (ID_RE, UI_HINT) compiled from the regex text in lint.py."""
    text = open(os.path.join(HERE, "ci", "lint.py"), encoding="utf-8").read()
    got = {}
    for name in ("ID_RE", "UI_HINT"):
        m = re.search(r'^%s = re\.compile\((r"(?:[^"\\]|\\.)*")\)' % name, text, re.M)
        if not m:
            return None
        got[name] = re.compile(ast.literal_eval(m.group(1)))
    return got["ID_RE"], got["UI_HINT"]


RANKS_CHECK = ranks_check_ui()
LINT_RULE = lint_id_rule()
check(RANKS_CHECK is not None, "SkyyRanks 0.1.1 _check_ui could not be read (reused validation)")
check(LINT_RULE is not None, "lint.py ID_RE / UI_HINT could not be read (reused validation)")

ALLOWED = UI.allowed_colors()
KNOWN_PATHS = set(UI.TEX.values()) | set(UI.SND.values())
COLOR_LIT = re.compile(r"(?<![0-9A-Za-z_&])#([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)(\(\s*(?:\d+(?:\.\d+)?|\.\d+)\s*\))?(?![0-9A-Za-z_])")
PATH_LIT = re.compile(r'"((?:\.\./)*(?:Common|Sounds|Pages|Hud|ItemQualities)/[^"]*)"')


def lint_java_line(line):
    """lint.py's FAIL rule on one Java line: a UI element id with an underscore on a page-building line."""
    id_re, hint = LINT_RULE
    if not hint.search(line):
        return []
    return [m.group(1) for m in id_re.finditer(line) if "_" in m.group(1) and not m.group(1).isupper()]


def markup_ok(name, mk, root=False, prefix=P):
    """Every generic property of one generated markup string."""
    try:
        UI.check_markup(mk, prefix=prefix, root=root)
        check(True, name)
    except ValueError as e:
        FAILS.append("%s: check_markup refused it: %s" % (name, e))
        return
    plain = UI.render(mk)
    ids = re.findall(r"#([A-Za-z0-9_]+)\s*\{", plain)
    check(all("_" not in i for i in ids), name + ": underscore in an element id")
    check(all(i.startswith(prefix) for i in ids), name + ": element id without the page prefix")
    bare = re.sub(r'"(?:[^"\\]|\\.)*"', '""', plain)
    check("@" not in bare and "$" not in bare, name + ": document variable inline")
    for m in PATH_LIT.finditer(plain):
        check(m.group(1) in KNOWN_PATHS, "%s: path %s is not verified by the kit" % (name, m.group(1)))
    for m in COLOR_LIT.finditer(plain):
        lit = "#" + m.group(1) + (m.group(2) or "")
        check(UI.norm_color(lit) in ALLOWED, "%s: colour %s is not a kit / rarity colour" % (name, lit))
    if RANKS_CHECK is not None and not UI.has_j(mk):
        try:
            RANKS_NS["PREFIX"] = prefix
            RANKS_CHECK(mk, name)
            check(True, name + " (SkyyRanks _check_ui)")
        except AssertionError as e:
            FAILS.append("%s: SkyyRanks _check_ui refused it: %s" % (name, e))
    if not UI.has_j(mk):
        check(UI.java_unlit(UI.java_lit(mk)) == mk, name + ": java_lit round trip")
    line = UI.java_append(prefix + "Body", mk)
    if LINT_RULE is not None:
        check(not lint_java_line(line), "%s: lint.py underscore-id rule fires on its Java line" % name)


# ================================================================= phase 1: verify()
def phase_verify():
    # the Java emitters are locked until verify() passes
    check(not UI._STATE["verified"], "the kit starts unverified")
    raises(lambda: UI.java_append(None, "Group #SkyyTA { Anchor: (Width: 1, Height: 2); }"), UI.NotVerifiedError,
           "java_append before verify()", "verify")
    raises(lambda: UI.java_set("SkyyTA", "Text", "x"), UI.NotVerifiedError, "java_set before verify()")
    raises(lambda: UI.java_expr("Group #SkyyTA { }"), UI.NotVerifiedError, "java_expr before verify()")
    raises(lambda: UI.java_field("A", "x"), UI.NotVerifiedError, "java_field before verify()")
    raises(lambda: UI.page_shell(P, 900, 600, "T").java("b"), UI.NotVerifiedError, "Shell.java before verify()")
    missing = os.path.join(SCRATCH, "no-such-Assets.zip")
    raises(lambda: UI.verify(missing, quiet=True), UI.VanillaCheckError, "verify() with a missing Assets.zip", "not found")
    fake = os.path.join(SCRATCH, "fake-assets.zip")
    with zipfile.ZipFile(fake, "w") as z:
        z.writestr(UI.CUSTOM + "Common.ui", "@ColorDefault = #ffffff;\n")
    raises(lambda: UI.verify(fake, quiet=True), UI.VanillaCheckError, "verify() with drifted documents", "vanilla look check failed")
    try:
        UI.verify(fake, quiet=True)
    except UI.VanillaCheckError as e:
        check("Sounds.ui is missing" in str(e) and "texture Common/ContainerHeader.png" in str(e)
              and "Common/UI/ItemQualities/Slots/SlotRare.png" in str(e), "verify() lists missing documents and textures")
    check(not UI._STATE["verified"], "a failed verify() leaves the Java emitters locked")
    counts = UI.verify(ASSETS)           # the real one, last: it unlocks the emitters for the rest of the test
    check(UI._STATE["verified"], "a passing verify() unlocks the Java emitters")
    check(isinstance(counts, dict) and counts["values"] >= 250 and counts["files"] >= 90,
          "verify() counts look too small: %s" % (counts,))
    n_custom = sum(1 for d, _n, _w in UI.checks() if d in UI.DOCS)
    check(counts["values"] == n_custom + len(UI.QUALITY), "verify() values = every custom-kit check + every quality file")
    check(counts["files"] == len(UI.texture_files()) + len(UI.sound_files()), "verify() files = every texture + sound")
    for k in UI.COLOR:
        check(k in UI._COLOR_SRC and UI._COLOR_SRC[k] in [(d, n) for d, n, _w in UI.checks()], "colour %s has a vanilla check" % k)
    check(UI._zip_path("../ItemQualities/Slots/SlotRare.png") == "Common/UI/ItemQualities/Slots/SlotRare.png",
          "a ../ItemQualities path resolves outside the custom root")
    check(set(UI.QUALITY) == set(UI.QUALITY_SLOT) == set(UI.QUALITY_TIP), "every quality has a slot and a tooltip frame")
    return counts


# ================================================================= phase 2: structural diff against the expanded vanilla definitions
class UiDoc(object):
    """A tiny reader for the vanilla .ui value grammar: definitions `@Name = value;`, spreads `...@X`, references `@X` /
    `$Alias.@X`, constructors `Type(...)`, tuples `(Key: value, ...)`. Enough to expand the style definitions the kit copies."""
    TOK = re.compile(r'\s+|//[^\n]*|/\*.*?\*/|("(?:[^"\\]|\\.)*")|(\.\.\.)'
                     r'|(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)(?![0-9A-Za-z])|(#[A-Za-z][A-Za-z0-9]*)'
                     r'|(-?\d+(?:\.\d+)?)|(\$[A-Za-z]+\.@[A-Za-z0-9]+)|(\$[A-Za-z]+)|(@[A-Za-z0-9]+)|([A-Za-z_][A-Za-z0-9_]*)'
                     r'|([(){}:;,=+*/%.\[\]-])', re.S)
    KINDS = ("str", "spread", "col", "eid", "num", "xref", "alias", "ref", "id", "p")

    def __init__(self, name, text, folder, docs):
        self.name, self.folder, self.docs = name, folder, docs
        self.toks = self.tokens(text)
        self.defs, self.aliases, self.cache = {}, {}, {}
        depth, i, toks = 0, 0, self.toks
        while i < len(toks):
            k, v = toks[i]
            if depth == 0 and k in ("ref", "alias") and i + 1 < len(toks) and toks[i + 1] == ("p", "="):
                j, d = i + 2, 0
                while j < len(toks) and not (d == 0 and toks[j] == ("p", ";")):
                    if toks[j][0] == "p" and toks[j][1] in "({[":
                        d += 1
                    elif toks[j][0] == "p" and toks[j][1] in ")}]":
                        d -= 1
                    j += 1
                if k == "ref":
                    self.defs[v[1:]] = toks[i + 2:j]
                elif j == i + 3 and toks[i + 2][0] == "str":
                    self.aliases[v] = posixpath.basename(toks[i + 2][1][1:-1])[:-3]
                i = j + 1
                continue
            if k == "p" and v in "({[":
                depth += 1
            elif k == "p" and v in ")}]":
                depth -= 1
            i += 1

    @classmethod
    def tokens(cls, text):
        out, pos = [], 0
        while pos < len(text):
            m = cls.TOK.match(text, pos)
            if not m:
                raise ValueError("UiDoc cannot read %r" % text[pos:pos + 30])
            pos = m.end()
            for k, g in zip(cls.KINDS, m.groups()):
                if g is not None:
                    out.append((k, g))
                    break
        return out

    def parse(self, toks, i=0):
        k, v = toks[i]
        if k == "p" and v == "(":
            return self.parse_tuple(toks, i)
        if k == "id" and i + 1 < len(toks) and toks[i + 1] == ("p", "("):
            return self.parse_tuple(toks, i + 1)
        if k in ("str", "col", "num", "xref", "ref", "id"):
            return (k, v), i + 1
        raise ValueError("UiDoc: unexpected %r" % (v,))

    def parse_tuple(self, toks, i):
        assert toks[i] == ("p", "(")
        i += 1
        items = []
        while toks[i] != ("p", ")"):
            if toks[i][0] == "spread":
                node, i = self.parse(toks, i + 1)
                items.append(("spread", node))
            else:
                key = toks[i][1]
                assert toks[i + 1] == ("p", ":"), (key, toks[i + 1])
                node, i = self.parse(toks, i + 2)
                items.append(("kv", key, node))
            if toks[i] == ("p", ","):
                i += 1
        return ("tuple", items), i + 1

    def get(self, name):
        if name not in self.cache:
            node, _i = self.parse(self.defs[name])
            self.cache[name] = self.ev(node)
        return self.cache[name]

    def text(self, value_text):
        """Evaluate a value written in this document's context (e.g. '(...@X, Sounds: (...$Sounds.@ButtonsLight))')."""
        node, _i = self.parse(self.tokens(value_text))
        return self.ev(node)

    def ev(self, node):
        k = node[0]
        if k == "tuple":
            d = {}
            for it in node[1]:
                if it[0] == "spread":
                    v = self.ev(it[1])
                    if isinstance(v, str):
                        v = {"Color": v} if v.startswith("#") else {"TexturePath": v}
                    d.update(v if isinstance(v, dict) else {})
                else:
                    d[it[1]] = self.ev(it[2])
            d = dict((a, b) for a, b in d.items() if b != {})          # an empty style (InputFieldStyle()) = the engine default
            if list(d) == ["Color"]:
                return d["Color"]
            if list(d) == ["TexturePath"]:
                return d["TexturePath"]
            return d
        if k == "ref":
            return self.get(node[1][1:])
        if k == "xref":
            alias, name = node[1].split(".", 1)
            return self.docs[self.aliases[alias]].get(name[1:])
        if k == "str":
            s = node[1][1:-1]
            return posixpath.normpath(posixpath.join(self.folder, s)) if s.endswith((".png", ".ogg")) else s
        if k == "col":
            return UI.norm_color(node[1])
        if k == "num":
            return format(float(node[1]), "g")
        return node[1]


def ui_diff(v, k, path=""):
    out = []
    if isinstance(v, dict) and isinstance(k, dict):
        for key in sorted(set(v) | set(k)):
            if key not in k:
                out.append("%s.%s missing in the kit (vanilla %s)" % (path, key, v[key]))
            elif key not in v:
                out.append("%s.%s only in the kit (%s)" % (path, key, k[key]))
            else:
                out += ui_diff(v[key], k[key], path + "." + key)
    elif v != k:
        out.append("%s: vanilla %r != kit %r" % (path, v, k))
    return out


def load_docs():
    path = ASSETS or UI.ASSETS_ZIP
    docs = {}
    with zipfile.ZipFile(path) as z:
        for key in ("C", "S", "W", "WN", "O"):
            rel = UI.DOCS[key]
            text = z.read(UI.CUSTOM + rel + ".ui").decode("utf-8", "replace").replace("\r\n", "\n")
            name = posixpath.basename(rel) if key in ("C", "S") else key
            docs[name] = UiDoc(name, text, posixpath.dirname(rel), docs)
    return docs


def kit_value(s):
    """Parse a kit style value ('Style: X(...);' / '(...)') with the same reader (paths relative to the custom root)."""
    s = s.strip()
    if s.startswith("Style: "):
        s = s[len("Style: "):]
    return UiDoc("kit", "", "", {}).text(s.rstrip(";"))


def phase_structure():
    try:
        docs = load_docs()
    except (KeyError, OSError, ValueError, AssertionError) as e:
        FAILS.append("structure phase could not read the vanilla documents: %s" % e)
        return
    C, W, WN, O = docs["Common"], docs["W"], docs["WN"], docs["O"]
    UI.text_scale("vanilla")
    try:
        def same(what, vanilla, kit):
            d = ui_diff(vanilla, kit)
            check(not d, "structure %s differs from vanilla: %s" % (what, "; ".join(d[:6])))

        light = "$Sounds.@ButtonsLight"
        for kind, size, style, snd in (("primary", "normal", "@DefaultTextButtonStyle", light),
                                       ("secondary", "normal", "@SecondaryTextButtonStyle", light),
                                       ("tertiary", "normal", "@TertiaryTextButtonStyle", light),
                                       ("destructive", "normal", "@CancelTextButtonStyle", "$Sounds.@ButtonsCancel"),
                                       ("secondary", "small", "@SmallSecondaryTextButtonStyle", light),
                                       ("tertiary", "small", "@SmallTertiaryTextButtonStyle", light)):
            # what the vanilla @TextButton / @CancelTextButton element does: the style, Sounds merged over its sound set
            same("button %s %s" % (kind, size), C.text("(...%s, Sounds: (...%s))" % (style, snd)), kit_value(UI.button_style(kind, size)))
        for kind, style, snd, over in (("secondary", "@SecondaryTextButtonStyle", "$Sounds.@ButtonsCancel", "cancel"),
                                       ("primary", "@DefaultTextButtonStyle", "$Sounds.@SaveSettings", "save"),
                                       ("secondary", "@SecondaryTextButtonStyle", "$Sounds.@Lock", "lock"),
                                       ("secondary", "@SecondaryTextButtonStyle", "$Sounds.@Unlock", "unlock")):
            same("button %s sound=%s" % (kind, over), C.text("(...%s, Sounds: (...%s, ...%s))" % (style, light, snd)),
                 kit_value(UI.button_style(kind, sound=over)))
        # the kit's recombinations where vanilla has no usable style (documented in the kit): small Primary / Destructive keep their
        # normal textures with the small label
        for kind, style in (("primary", "@DefaultTextButtonStyle"), ("destructive", "@CancelTextButtonStyle")):
            want = C.text("(...%s, Sounds: (...%s))" % (style, "$Sounds.@ButtonsCancel" if kind == "destructive" else light))
            for stt in ("Default", "Hovered", "Pressed"):
                want[stt]["LabelStyle"] = C.get("SmallButtonLabelStyle")
            want["Disabled"]["LabelStyle"] = C.get("SmallButtonDisabledLabelStyle")
            same("button %s small (normal textures + small label)" % kind, want, kit_value(UI.button_style(kind, "small")))
        same("scrollbar", C.get("DefaultScrollbarStyle"), kit_value(UI.scrollbar_style()))
        same("scrollbar extra spacing", C.get("DefaultExtraSpacingScrollbarStyle"), kit_value(UI.scrollbar_style(12)))
        same("text tooltip", C.get("DefaultTextTooltipStyle"), kit_value(UI.tooltip_style()))
        same("checkbox", C.get("DefaultCheckBoxStyle"), kit_value(UI.checkbox_style()))
        same("dropdown with search", C.get("DefaultDropdownBoxStyle"), kit_value(UI.dropdown_style(search=True)))
        nos = dict(C.get("DefaultDropdownBoxStyle"))
        nos.pop("SearchInputStyle")
        same("dropdown", nos, kit_value(UI.dropdown_style()))
        same("clear button", C.get("ClearButtonStyle"), kit_value(UI.clear_button_style()))
        same("window title", C.text("(...@TitleStyle, HorizontalAlignment: Center)"), kit_value(UI.title_style()))
        same("list row normal", W.get("NormalRowStyle"), kit_value(UI.row_style("normal")))
        same("list row selected", W.get("SelectedRowStyle"), kit_value(UI.row_style("selected")))
        same("list row static", W.get("StaticRowStyle"), kit_value(UI.row_style("static")))
        same("nav button", WN.get("LabelStyle"), kit_value(UI.list_button_style("normal")))
        same("nav button selected + mask", WN.get("SelectedLabelStyle"), kit_value(UI.list_button_style("selected", mask=True, trial=True)))
        same("option card", O.get("DefaultRespawnButtonStyle"), kit_value(UI.option_style(False)))
        same("option card selected (Default)", O.get("SelectedRespawnButtonStyle")["Default"], kit_value(UI.option_style(True))["Default"])
        check("Sounds" not in kit_value(UI.option_style(False)), "structure: the option card is silent like vanilla")
        # negative controls: the diff must notice a wrong style / a wrong value
        check(ui_diff(C.text("(...@DefaultTextButtonStyle, Sounds: (...%s))" % light), kit_value(UI.button_style("secondary"))),
              "structure: the diff notices Secondary where Primary is expected")
        check(ui_diff(C.get("DefaultScrollbarStyle"), kit_value(UI.scrollbar_style(12))), "structure: the diff notices a changed number")
    finally:
        UI.text_scale("readable")


# ================================================================= phase 3: builders
def build_samples():
    """name -> markup of (nearly) every builder call shape."""
    s = {}
    for k in UI.LABELS:
        s["label " + k] = UI.label(P + "L" + k[0].upper() + k[1:], "", k)
    s["label text"] = UI.label(P + "Lt", "Page 1 of 3 <b>", "default", w=300)
    s["label anon"] = UI.label(None, "", "caption", h=False, flex=1)
    s["label runtime colour"] = UI.label(P + "Lc", "", "rowName", col=UI.J("col", "#ffcc00"))
    s["label secondary spaced"] = UI.label(P + "Ls", "Letter spacing", "strong", font="Secondary", spacing=0.5)
    s["label spaced 1.8"] = UI.label(P + "Lq", "", "display", spacing=1.8, valign=False)
    s["title"] = UI.title_label(P + "Tt", "Reforge")
    s["status line"] = UI.status_line(P + "Status")
    s["status line wrap"] = UI.status_line(P + "Stw", h=44, wrap=True, max_lines=2, anchor={"top": 12})
    s["section"] = UI.section(P + "Sec", "Your gear")
    s["subtitle"] = UI.subtitle(P + "Sub")
    s["panel title"] = UI.panel_title(P + "Pt", "Before", w=275)
    s["property row"] = UI.property_row(P + "Prop", P + "PropK", P + "PropV", "Level")
    for kind in UI.BUTTONS:
        for size in UI.BUTTON_SIZES:
            s["button %s %s" % (kind, size)] = UI.button(P + "B" + kind[:3] + size[:2], "Go", kind, size, w=180)
            s["button %s %s default width" % (kind, size)] = UI.button(P + "W" + kind[:3] + size[:2], "Go", kind, size)
            s["button %s %s disabled" % (kind, size)] = UI.button(P + "D" + kind[:3] + size[:2], "", kind, size, w=180, disabled=True)
    s["button tertiary selected"] = UI.button(P + "Sel", "Ranks", "tertiary", "small", w=190, selected=True)
    s["button save sound"] = UI.button(P + "Save", "Save", "primary", w=172, sound="save", anchor={"right": 6})
    s["button lock sound"] = UI.button(P + "Lock", "Lock", "secondary", sound="lock")
    s["button flex"] = UI.button(P + "Flex", "Back", "secondary", flex=1)
    s["button runtime id"] = UI.button(P + "Buy" + UI.J("i", "3"), "Buy", "secondary", "small")
    s["button runtime width"] = UI.button(P + "Bw", "Buy", "primary", w=UI.J("bw", "160"))
    s["button primary 120"] = UI.button(P + "B120", "Save", "primary", w=120)
    for i, mk in enumerate(UI.on_off(P + "Pvp", True)):
        s["on_off %d" % i] = mk
    s["close"] = UI.close_button(P + "Close")
    s["button row"] = UI.button_row(P + "Btns")
    s["spacer"] = UI.spacer(12, 40)
    s["group row"] = UI.group(P + "Grp", "Left", h=44, anchor={"top": 4})
    s["group anon column"] = UI.group(None, "Top", w=300, flex=1, pad=8)
    s["group padding dict"] = UI.group(P + "Grd", "Left", w=500, h=60, pad={"horizontal": 8, "vertical": 4}, extra="Visible: true")
    s["text field"] = UI.text_field(P + "Fb", P + "F", 300, placeholder="player name", max_length=40)
    s["text field vanilla look"] = UI.text_field(P + "Fvb", P + "Fv", 300, placeholder="player name", look="vanilla")
    s["text field filter look"] = UI.text_field(P + "Ffb", P + "Ff", 260, placeholder="filter", look="filter")
    s["text field flex"] = UI.text_field(P + "Fxb", P + "Fx", flex=1, anchor={"left": 0})
    s["text field full width"] = UI.text_field(P + "Fwb", P + "Fw")
    s["value box"] = UI.value_box(P + "Vb", P + "V", 260)
    s["value box flex"] = UI.value_box(P + "Vfb", P + "Vf", flex=1, anchor={"right": 8})
    for i, (par, mk) in enumerate(UI.tab_row(P + "Body", P + "Tabs", [P + "Tab%d" % j for j in range(3)], ["Ranks", "Players", ""], 1)):
        s["tab primary %d" % i] = mk
    for i, (par, mk) in enumerate(UI.tab_row(P + "Body", P + "Tabz", [P + "Tabz%d" % j for j in range(2)], ["A", "B"], 0, w=190,
                                             mode="tertiary")):
        s["tab tertiary %d" % i] = mk
    for st in ("normal", "selected", "static"):
        s["panel row " + st] = UI.panel_row(P + "Row" + st[:2], st)
    s["panel row runtime"] = UI.panel_row(P + "Row" + UI.J("r", "4"), "normal")
    s["row text"] = UI.row_text(P + "Txt", P + "Name", P + "Desc")
    s["row text name only"] = UI.row_text(P + "Txo", P + "Nmo")
    s["row badge"] = UI.row_badge(P + "Badge")
    s["row action"] = UI.row_action(P + "Act", "Edit")
    s["row action destructive"] = UI.row_action(P + "Del", "Delete", "destructive")
    s["row action primary"] = UI.row_action(P + "Rap", "Set", "primary")
    s["hover row"] = UI.hover_row(P + "Hr", h=44)
    s["hover row selected"] = UI.hover_row(P + "Hs", "selected", h=44)
    s["option row"] = UI.option_row(P + "Opt")
    s["option row selected"] = UI.option_row(P + "Ops", True)
    s["option row sound"] = UI.option_row(P + "Opn", sound="light")
    s["list button"] = UI.list_button(P + "Lb", "Mining")
    s["list button selected"] = UI.list_button(P + "Ls", "Mining", "selected", sound="light")
    s["list button selected mask"] = UI.list_button(P + "Lm", "Mining", "selected", mask=True, trial=True)
    s["hover row sound"] = UI.hover_row(P + "Hc", h=44, sound="light")
    s["setting row"] = UI.setting_row(P + "Set", P + "SetL")
    s["scroll list"] = UI.scroll_list(P + "List", h=500)
    s["scroll list flex"] = UI.scroll_list(P + "Lf", extra_spacing=True)
    s["scroll list well"] = UI.scroll_list(P + "Lw", well=True)
    for kind in UI.SEPARATORS:
        s["separator " + kind] = UI.separator(kind)
    s["separator id"] = UI.separator("content", P + "Sep", w=400)
    s["separator margins"] = UI.separator("content", anchor={"top": 8, "bottom": 8}, flex=1)
    for kind in UI.PANEL_KINDS:
        s["panel " + kind] = UI.panel(P + "Pn" + kind[:3], kind, w=400, h=200)
    s["panel padding dict"] = UI.panel(P + "Pd", "simple", pad={"left": 4, "top": 2}, extra="Visible: true")
    s["item icon"] = UI.item_icon(P + "Ic", "Weapon_Sword_Iron", 48)
    s["item icon anon"] = UI.item_icon(None, None, 32)
    s["item frame"] = UI.item_frame(P + "Fr", icon_id=P + "FrI")
    s["item frame have"] = UI.item_frame(P + "Fh", border="slotBorderHave", anchor={"left": 8})
    s["item slot"] = UI.item_slot(P + "Sb", P + "Sl", trial=True)
    s["quality frame"] = UI.quality_frame(P + "Qf", "Epic", icon_id=P + "QfI", trial=True)
    s["quality frame default"] = UI.quality_frame(P + "Qd", trial=True)
    s["item grid"] = "ItemGrid #%sGrid { Anchor: (Width: 300, Height: 80); SlotsPerRow: 4; AreItemsDraggable: false; Style: %s; }" % (
        P, UI.item_grid_style(74, 64, 2, slot_bg=True, trial=True))
    s["card"] = UI.card(P + "Card")
    s["card sold out"] = UI.card(P + "Cso", sold_out=True)
    s["card no margin"] = UI.card(P + "Cnm", margin=0)
    s["card flex"] = UI.card(P + "Cfx", flex=1)
    s["bar flex"] = UI.bar(P + "Bfx", None, 12, UI.J("fw", "40"), flex=1)
    s["progress flex"] = UI.progress(P + "Pfx", flex=1, trial=True)
    s["value box padding"] = UI.value_box(P + "Vpb", P + "Vp", 200, padding={"left": 12, "right": 4})
    s["bar"] = UI.bar(P + "Bar", 400, 18, 120)
    s["bar runtime"] = UI.bar(P + "Bar" + UI.J("i", "2"), 400, 18, UI.J("fw", "200"), col="progressGreen", anchor={"top": 4})
    s["progress"] = UI.progress(P + "Pr", value=0.25, trial=True)
    s["progress memories"] = UI.progress(P + "Pm", value=0.5, kind="memories", trial=True)
    s["tooltip"] = UI.button(P + "Tip", "Hover", "secondary", extra=UI.tooltip("Sells for 20 coins", trial=True))
    s["tooltip panel"] = UI.tooltip_panel(P + "Tp")
    s["tooltip panel quality"] = UI.tooltip_panel(P + "Tq", quality="Legendary", trial=True)
    s["checkbox"] = UI.checkbox(P + "Chk", True, trial=True)
    s["checkbox row"] = UI.checkbox_row(P + "Chr", P + "ChrL", P + "ChrC", text="Include entities", trial=True)
    s["dropdown"] = UI.dropdown(P + "Dd", trial=True)
    s["dropdown search flex"] = UI.dropdown(P + "Ds", search=True, flex=1, trial=True)
    s["search field"] = UI.search_field(P + "Sfb", P + "Sf", 300, placeholder="search", trial=True)
    s["spinner"] = UI.spinner(P + "Spin", trial=True)
    for st in UI.TILE_STATES:
        s["tile " + st] = UI.tile(P + "Tl" + st[:3], "Mage", st, trial=True)
    s["gradient label"] = UI.gradient_label(P + "Big", "Mining", trial=True)
    s["number field"] = UI.text_field(P + "Nb", P + "N", 120, number=True, trial=True)
    return s


def phase_builders():
    samples = build_samples()
    for name, mk in samples.items():
        markup_ok(name, mk)

    # page shells and dialogs (the first append is the root)
    for kind in ("decorated", "plain"):
        sh = UI.page_shell(P, 1100, 880, "Reforge", kind=kind, close=True)
        try:
            sh.appends.check(P)
            check(True, "page shell %s check_page" % kind)
        except ValueError as e:
            FAILS.append("page shell %s: %s" % (kind, e))
        for i, (par, mk) in enumerate(sh.appends):
            markup_ok("page shell %s append %d" % (kind, i), mk, root=(par is None))
        check(sh.pad == 17 and sh.inner_w == 1100 - 34 and sh.body_h == 880 - 38 and sh.inner_h == 880 - 38 - 34,
              "page shell sizes (container default padding 17)")
        check(("ContainerDecorationTop" in sh.appends.java()) == (kind == "decorated"), "page shell %s ornaments" % kind)
        check(sh.appends[-1][1].startswith("Button #SkyyTClose"), "close X appended last")
    sh = UI.page_shell("SkyyBankF", 1100, 860, body_id="SkyyBank", title="Bank")
    check(sh.body == "SkyyBank" and sh.root == "SkyyBankF" and sh.appends[2][1].startswith("Group #SkyyBank {"),
          "page shell: the old root id becomes the body")
    check(not sh.sets and 'Text: "Bank"' in sh.appends[1][1], "static title goes inline")
    check("Padding: (Full: 16)" in UI.page_shell(P, 900, 600, "T", pad=UI.PAGE_PAD).appends[2][1], "editor-page padding 16 on request")
    sh2 = UI.page_shell(P, 900, 600, "Buy page 3 for 1,250 coins?")
    check(sh2.sets == [(P + "Title", "Text", "Buy page 3 for 1,250 coins?")] and 'Text: ""' in sh2.appends[1][1],
          "a title with unproven characters is b.set, not inline")
    j2 = sh2.java("b")
    check('b.set("#SkyyTTitle.Text", "Buy page 3 for 1,250 coins?");' in j2, "shell.java emits the title b.set")
    sh3 = UI.page_shell(P, 900, 600, UI.J("titleOf(p)", "X"))
    check('b.set("#SkyyTTitle.Text", "" + (titleOf(p)));' in sh3.java(), "runtime title through java_expr")
    shn = UI.page_shell(P, 900, 600, "Hi\n")
    check(shn.sets == [(P + "Title", "Text", "Hi\n")] and 'Text: ""' in shn.appends[1][1], "a title with a newline is b.set, not inline")
    shj = UI.page_shell(P, UI.J("w", "900"), UI.J("h", "600"), "Sized")
    check(shj.w == 900 and shj.inner_w == 900 - 34 and shj.inner_h == 600 - 38 - 34, "runtime page size: sizes from the samples")
    check('"Group #SkyyT { Anchor: (Width: " + (w) + ", Height: " + (h) + "); }"' in shj.java(), "runtime page size in the root append")
    raises(lambda: UI.page_shell(P, UI.J("w"), 600), ValueError, "runtime page size with the default 0 sample")
    raises(lambda: UI.page_shell(P, UI.J("w", "wide"), 600), ValueError, "runtime page size with a non-digit sample")
    raises(lambda: UI.page_shell(P, 900, 981), ValueError, "page taller than MAX_PAGE_H", "1080")
    raises(lambda: UI.page_shell(P, 250, 600), ValueError, "page narrower than MIN_PAGE_W")
    raises(lambda: UI.page_shell(P, 900, 600, body_id=P), ValueError, "page shell with two equal ids", "differ")
    raises(lambda: UI.page_shell(P, 900, 600, pad=400), ValueError, "page padding that leaves no body", "padding")
    raises(lambda: UI.page_shell(P, 900, 600, pad=-5), ValueError, "negative page padding", "padding")
    raises(lambda: sh.fit([400, 400]), ValueError, "Shell.fit over budget")
    check(sh.fit([100, 200]) == sh.inner_h - 300, "Shell.fit returns what is left")
    for yk in ("primary", "destructive"):
        dl = UI.confirm_dialog(P + "D", yes_kind=yk, yes_text="Buy", title="Confirm")
        try:
            dl.appends.check(P)
            check(True, "confirm dialog %s check_page" % yk)
        except ValueError as e:
            FAILS.append("confirm dialog %s: %s" % (yk, e))
        for i, (par, mk) in enumerate(dl.appends):
            markup_ok("confirm %s append %d" % (yk, i), mk, root=(par is None))
        yes = [mk for par, mk in dl.appends if mk.startswith("TextButton #SkyyTDYes")][0]
        check(("SaveActivate" in yes) == (yk == "primary") and ("ButtonsCancelActivate" in yes) == (yk == "destructive"),
              "confirm dialog yes sound (%s)" % yk)
        check(dl.w == 620 and dl.pad == 20 and dl.h == 38 + 40 + 58 + 64 + (UI.fs(12) + 10 + 8) + 52, "confirm dialog geometry %s" % yk)
        note = [mk for par, mk in dl.appends if mk.startswith("Label #SkyyTDNote")][0]
        check("Bottom: 8, Horizontal: 4" in note and "FontSize: %d" % UI.fs(12) in note and "HorizontalAlignment" not in note,
              "confirm note = PrefabEditorExitConfirm (12 px readable-scaled, left, bottom 8 / horizontal 4)")
    nd = UI.confirm_dialog(P + "E", note=False, title="Sell")
    check(nd.note is None and not any("#SkyyTENote" in mk for _p, mk in nd.appends), "confirm dialog without a note")
    raises(lambda: UI.confirm_dialog(P + "F"), ValueError, "confirm dialog without a title", "title")

    # underscores are refused everywhere an id goes in (Java selectors too)
    bad = P + "Bad_Id"
    for name, fn in (("label", lambda: UI.label(bad)), ("title", lambda: UI.title_label(bad)), ("button", lambda: UI.button(bad, "X")),
                     ("close", lambda: UI.close_button(bad)), ("row", lambda: UI.panel_row(bad)),
                     ("row text", lambda: UI.row_text(P + "X", bad)), ("hover row", lambda: UI.hover_row(bad)),
                     ("option row", lambda: UI.option_row(bad)), ("list button", lambda: UI.list_button(bad)),
                     ("setting row", lambda: UI.setting_row(bad, P + "Y")), ("scroll", lambda: UI.scroll_list(bad)),
                     ("field box", lambda: UI.text_field(bad, P + "F", 100)), ("field", lambda: UI.text_field(P + "Fb", bad, 100)),
                     ("value box", lambda: UI.value_box(bad, P + "V", 100)), ("separator", lambda: UI.separator("content", bad)),
                     ("panel", lambda: UI.panel(bad)), ("icon", lambda: UI.item_icon(bad)), ("frame", lambda: UI.item_frame(bad)),
                     ("slot", lambda: UI.item_slot(P + "S", bad, trial=True)), ("card", lambda: UI.card(bad)),
                     ("card overlay", lambda: UI.card(P + "C", sold_out=True, out_id=bad)),
                     ("bar", lambda: UI.bar(bad, 10, 10, 5)), ("tab", lambda: UI.tab_row(None, P + "R", [bad], ["A"], 0)),
                     ("tab row", lambda: UI.tab_row(None, bad, [P + "A"], ["A"], 0)), ("shell", lambda: UI.page_shell(bad, 900, 600)),
                     ("shell body", lambda: UI.page_shell(P, 900, 600, body_id=bad)), ("dialog", lambda: UI.confirm_dialog(bad, title="T")),
                     ("on_off", lambda: UI.on_off(bad, True)), ("button row", lambda: UI.button_row(bad)), ("group", lambda: UI.group(bad)),
                     ("property row", lambda: UI.property_row(P + "Pr", bad, P + "V")),
                     ("checkbox row", lambda: UI.checkbox_row(P + "Cr", P + "L", bad, trial=True)),
                     ("dropdown", lambda: UI.dropdown(bad, trial=True)), ("search", lambda: UI.search_field(P + "S", bad, trial=True)),
                     ("spinner", lambda: UI.spinner(bad, trial=True)), ("tile", lambda: UI.tile(bad, trial=True)),
                     ("quality frame", lambda: UI.quality_frame(bad, trial=True)),
                     ("runtime id sample", lambda: UI.button(P + "B" + UI.J("i", "a_b"), "X")),
                     ("java_set selector", lambda: UI.java_set("Skyy_Bad", "Text", "x")),
                     ("java_append parent", lambda: UI.java_append("Skyy_Bad", "Label { }")),
                     ("java_ref_style", lambda: UI.java_ref_style("Skyy_Bad", "SecondaryTextButtonStyle", trial=True))):
        raises(fn, ValueError, "underscore id refused by " + name, "underscore")
    check(UI.check_id(P + "Row" + UI.J("row_i", "7")) is not None, "a Java variable with an underscore inside J() is fine")
    raises(lambda: UI.java_set("SkyyX", "Some_Prop", "x"), ValueError, "java_set refuses a property with an underscore", "property")
    raises(lambda: UI.java_set("SkyyX", "Text.Sub", "x"), ValueError, "java_set refuses a dotted property")
    raises(lambda: UI.check_id("9Skyy"), ValueError, "id starting with a digit")
    raises(lambda: UI.check_id("Skyy-X"), ValueError, "id with a dash")
    raises(lambda: UI.check_id("SkyyX", prefix="SkyyY"), ValueError, "id without the page prefix", "prefix")
    raises(lambda: UI.check_id("SkyyX\n"), ValueError, "id with a trailing newline")

    # inline text rule (also a trailing newline: the validators use fullmatch)
    raises(lambda: UI.label(P + "A", "Hello, world"), ValueError, "comma in inline text", "b.set")
    raises(lambda: UI.label(P + "A", "Hi\n"), ValueError, "trailing newline in inline text", "b.set")
    raises(lambda: UI.button(P + "A", "Go\n"), ValueError, "trailing newline in button text")
    raises(lambda: UI.button(P + "A", "50%"), ValueError, "percent in button text")
    raises(lambda: UI.label(P + "A", UI.J("name")), ValueError, "runtime text inline", "b.set")
    raises(lambda: UI.text_field(P + "A", P + "B", 100, placeholder="e.g. vip"), ValueError, "dot in a placeholder")
    raises(lambda: UI.tooltip("Costs 5.", trial=True), ValueError, "dot in a tooltip")
    raises(lambda: UI.check_markup('Label #SkyyTA { Text: "a\n"; }'), ValueError, "check_markup: newline inside Text")
    check(UI.check_text("< Prev") == "< Prev" and UI.check_text("Next >") == "Next >", "proven text characters pass")

    # duplicate element ids
    raises(lambda: UI.check_page(UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 900, Height: 600); }"),
                                             ("SkyyTA", "Group #SkyyTB { }"), ("SkyyTA", "Label #SkyyTB { }")])), ValueError,
           "check_page: the same id created twice", "duplicate")
    raises(lambda: UI.check_page(UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 900, Height: 600); }"),
                                             ("SkyyTA", "Group #SkyyTA { }")])), ValueError, "check_page: a child reusing the root id")
    raises(lambda: UI.check_markup("Group #SkyyTA { Label #SkyyTB { } Label #SkyyTB { } }"), ValueError,
           "check_markup: a duplicate id inside one markup", "duplicate")
    dyn = UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 900, Height: 600); }"),
                      ("SkyyTA", UI.panel_row(P + "Row" + UI.J("i", "1"))), ("SkyyTA", UI.panel_row(P + "Row" + UI.J("j", "1")))])
    try:
        UI.check_page(dyn)
        check(True, "runtime ids are never duplicates")
    except ValueError as e:
        FAILS.append("runtime ids were counted as duplicates: %s" % e)
    raises(lambda: UI.check_page(UI.Appends([("SkyyTK", "Group #SkyyTK { }")]), known_parents=["SkyyTK"]), ValueError,
           "check_page: re-creating a known parent")

    # colours
    check(UI.color("gold") == "#E8A93B" and UI.color("#12ab34(0.5)") == "#12ab34(0.5)", "colour names and literals")
    raises(lambda: UI.color("#12345"), ValueError, "short hex refused")
    raises(lambda: UI.color("red"), ValueError, "unknown colour name refused")
    raises(lambda: UI.color("#ffffff\n"), ValueError, "colour with a trailing newline refused")
    raises(lambda: UI.label(P + "A", "", "default", col="#zzzzzz"), ValueError, "bad label colour refused")
    check(UI.STATUS == {"+": "#39f493", "-": "#ff6b6b", "=": "#E8A93B"}, "status marks = the vanilla success / error / gold")
    check(UI.norm_color("#ABCDEF(0.50)") == "#abcdef(0.5)" and UI.norm_color("#ffffff(...)") == "#ffffff(...)"
          and UI.norm_color("#123456(1.2.3)") == "#123456(1.2.3)" and UI.norm_color("#FFFFFF(.5)") == "#ffffff(0.5)",
          "norm_color (malformed alphas come back lower-cased instead of raising)")
    check(UI.COLOR["well"] == "#000000(0.15)" and UI.COLOR["value"] == "#b7cedd" and UI.COLOR["propKey"] == "#7a8a9a"
          and UI.COLOR["summary"] == "#8fa6ba" and UI.COLOR["formLine"] == "#5e512c", "the new vanilla colours")

    # buttons
    raises(lambda: UI.button(P + "A", "Go", "primary", w=110), ValueError, "Primary narrower than 120", "120")
    raises(lambda: UI.button(P + "A", "Go", "primary", w=UI.J("bw", "100")), ValueError, "runtime Primary width checked by its sample")
    check("Primary.png" in UI.button(P + "A", "Go", "primary", w=120), "Primary at the vanilla 120 is allowed")
    sp = UI.button(P + "A", "Go", "primary", "small")
    check("Width: 150" in sp and "Height: 32" in sp and "Primary.png" in sp, "a small Primary defaults to 150 wide")
    check("Width: 150" in UI.row_action(P + "A", "Set", "primary") and "Width: 92" in UI.row_action(P + "A", "Edit"),
          "row_action widths: small Primary 150, others 92")
    raises(lambda: UI.button(P + "A", "Go", w=-5), ValueError, "negative button width", "> 0")
    raises(lambda: UI.button(P + "A", "Go", w=0), ValueError, "zero button width", "> 0")
    raises(lambda: UI.label(P + "A", "", h=0), ValueError, "zero label height")
    raises(lambda: UI.bar(P + "A", 10, 10, -1), ValueError, "negative bar fill")
    raises(lambda: UI.button(P + "A", "Go", "secondary", selected=True), ValueError, "selected on a non-tertiary button")
    raises(lambda: UI.button(P + "A", "Go", "fancy"), ValueError, "unknown button kind")
    raises(lambda: UI.button(P + "A", "Go", size="huge"), ValueError, "unknown button size")
    raises(lambda: UI.button(P + "A", "Go", sound="boom"), ValueError, "unknown sound set")
    st = UI.button_style("secondary")
    check(all(x in st for x in ("Default: (", "Hovered: (", "Pressed: (", "Disabled: (", "Sounds: (")), "button style has all states")
    check("Secondary_Hovered.png" in st and "Secondary_Pressed.png" in st and "Disabled.png" in st, "secondary textures")
    check("TextColor: #bdcbd3" in st and "TextColor: #797b7c" in st and "ButtonsLightActivate" in st, "secondary label + light sound")
    ds = UI.button_style("primary", disabled=True)
    check(ds.count("Disabled.png") == 4 and "Sounds" not in ds and "#bfcdd5" not in ds, "disabled look: every state, no sound")
    check("ButtonsCancelActivate" in UI.button_style("destructive"), "destructive default sound = ButtonsCancel")
    check("SaveActivate" in UI.button_style("primary", sound="save"), "save sound override")
    check("LockActivate" in UI.sounds("lock") and "ButtonsLightHover" in UI.sounds("lock") and "ButtonsLightHover" in UI.sounds("unlock"),
          "lock / unlock keep the light hover (the vanilla merge)")
    sm = UI.button(P + "A", "Go", "secondary", "small")
    check("Height: 32" in sm and "Padding: (Horizontal: 16)" in sm and "FontSize: 14" in sm and "Width: 92" in sm, "small button sizes")
    check("Height: 48" in UI.button(P + "A", "Go", "primary", "big"), "big button height")
    sel = UI.button_style("tertiary", selected=True)
    check(sel.count("Tertiary_Active.png") == 2 and "Tertiary_Pressed.png" in sel, "selected tertiary look")
    check("VerticalBorder: 12, HorizontalBorder: 80" in UI.button_style("primary"), "primary patch borders")
    check("Sounds" not in UI.hover_row(P + "A") and "Sounds" not in UI.list_button(P + "A") and "Sounds" not in UI.option_row(P + "A"),
          "vanilla list rows / nav buttons / option cards are silent")
    check("ButtonsLightActivate" in UI.hover_row(P + "A", sound="light") and "ButtonsLightActivate" in UI.option_row(P + "A", sound="light"),
          "sound= options")
    check("Disabled: (Background: (TexturePath: \"Common/OptionBackgroundPatch.png\", Border: 16))" in UI.option_row(P + "A"),
          "option card Disabled state")
    fb = UI.button(P + "A", "Back", flex=1)
    check("FlexWeight: 1" in fb and "Width" not in fb, "a flex button takes its width from the row")
    oo = UI.on_off(P + "X", False)
    check("Tertiary_Active" not in oo[0] and "Tertiary_Active" in oo[1], "on_off selects the current state")

    # tabs: the vanilla server tab row by default (EntitySpawnPage)
    tr = UI.tab_row(P + "Body", P + "Tr", [P + "T0", P + "T1", P + "T2"], ["A", "B", "C"], 1)
    check(len(tr) == 1 + 3 + 2 and "Top: 10, Bottom: 10" in tr[0][1] and tr[2][1] == "Group { Anchor: (Width: 5); }",
          "tab row: margins 10, 5 px spacers")
    tabs = [mk for _p, mk in tr if mk.startswith("TextButton")]
    check("Secondary.png" in tabs[0] and "Primary.png" in tabs[1] and "Secondary.png" in tabs[2]
          and all("FlexWeight: 1" in t and "Width" not in t.split("Padding")[0] for t in tabs), "tab row: flex Secondary, the active Primary")
    tt = UI.tab_row(P + "Body", P + "Tt", [P + "U0", P + "U1"], ["A", "B"], 0, w=190, mode="tertiary")
    check("Tertiary_Active" in tt[1][1] and "Width: 190" in tt[1][1] and "Height: 32" in tt[1][1], "tab row tertiary mode")
    raises(lambda: UI.tab_row(None, P + "R", [P + "A"], ["A"], 0, w=100), ValueError, "a fixed-width Primary tab under 120")
    raises(lambda: UI.tab_row(None, P + "R", [P + "A", P + "B"], ["A"], 0), ValueError, "tab ids / names differ")

    # the new vanilla building blocks
    check("Background: #000000(0.15); Padding: (Full: 4);" in UI.scroll_list(P + "A", well=True), "scroll_list well: #000000(0.15), 4")
    check("Background: #000000(0.15); Padding: (Full: 8);" in UI.panel(P + "A", "well"), "panel well: #000000(0.15), 8")
    check("Background: #000000(0.3)" in UI.panel(P + "A", "dark"), "panel dark stays the respawn block")
    check("Padding: (Horizontal: 20, Vertical: 10)" in UI.panel(P + "A", "hud"), "panel hud (Hud/TimeLeft)")
    check("Top: -2" in UI.separator("vertical") and "Vertical: 16" in UI.separator("form") and "#5e512c" in UI.separator("form"),
          "vertical separator Top -2, form divider")
    pr = UI.property_row(P + "A", P + "K", P + "V")
    check("Width: 150, Right: 8" in pr and "FlexWeight: 1" in pr and "#7a8a9a" in pr and "#b7cedd" in pr and "WrapMaxLines: 1" in pr
          and "Height: 26, Bottom: 2" in pr, "property row (WorldEventPropertyRow, readable 26)")
    lbs = UI.list_button(P + "A", "X", "selected")
    check(lbs.count("Background: #000000(0.2)") == 2 and "LabelMask" not in lbs, "selected nav button has the dark back")
    raises(lambda: UI.list_button(P + "A", "X", "selected", mask=True), UI.UnverifiedError, "nav mask needs trial=True")
    cd = UI.card(P + "Cd")
    check(cd.startswith("Group #SkyyTCdBox { Anchor: (Width: 230, Height: 185); Padding: (Horizontal: 5, Vertical: 5);")
          and "Button #SkyyTCd { Anchor: (Full: 0);" in cd, "card: the 5 px margin box around the button (BarterTradeRow)")
    check("#0a0e12(0.75)" in UI.card(P + "Cd", sold_out=True) and "Label #SkyyTCdOutL" in UI.card(P + "Cd", sold_out=True),
          "card sold-out cover")
    check(UI.card(P + "Cd", margin=0).startswith("Button #SkyyTCd { Anchor: (Width: 230, Height: 185);"), "card margin 0")
    lf = UI.label(P + "A", "", "display")
    check('FontName: "Secondary"' in lf and "FontSize: 32" in lf, "display label: Secondary 32")
    check("LetterSpacing: 0.5" in samples["label secondary spaced"] and "LetterSpacing: 1.8" in samples["label spaced 1.8"]
          and "VerticalAlignment" not in samples["label spaced 1.8"], "LetterSpacing floats, valign=False")
    tf = UI.text_field(P + "A", P + "B", flex=1)
    check("FlexWeight: 1" in tf and "Width" not in tf, "a flex text field")
    tv = UI.text_field(P + "A", P + "B", look="vanilla")
    check(re.search(r"(?<![A-Za-z])Style:", tv) is None and "PlaceholderStyle: (TextColor: #6e7da1);" in tv,
          "vanilla text field look = @TextField (engine default style, placeholder colour only)")
    fl = UI.text_field(P + "A", P + "B", look="filter")
    check("Height: 28" in fl and "Horizontal: 6" in fl and "TextColor: #b7cedd" in fl, "filter text field look")
    raises(lambda: UI.text_field(P + "A", P + "B", look="neon"), ValueError, "unknown text field look")
    check("ShowSearchInput: true" in samples["dropdown search flex"] and "FlexWeight: 1" in samples["dropdown search flex"],
          "dropdown search + flex")
    check("Padding: (Left: 28)" in samples["search field"] and "SearchIcon.png" in samples["search field"]
          and "ClearInputIcon.png" in samples["search field"], "search field look")
    check('"../ItemQualities/Slots/SlotEpic.png"' in samples["quality frame"] and "Padding: (Full: 24, Top: 21)" in
          samples["tooltip panel quality"], "quality frames outside the custom root")
    raises(lambda: UI.quality_frame(P + "A", "Shiny", trial=True), ValueError, "unknown quality")
    raises(lambda: UI.tile(P + "A", state="glowing", trial=True), ValueError, "unknown tile state")
    raises(lambda: UI.progress(P + "A", kind="round", trial=True), ValueError, "unknown progress kind")
    check("ProgressBar #SkyyTPmTex" in samples["progress memories"] and "MemoriesBarBg.png" in samples["progress memories"],
          "memories bar with its texture overlay")

    # trial gating of the UNVERIFIED elements
    gated = (("item_slot", lambda t: UI.item_slot(P + "S", P + "T", trial=t)), ("progress", lambda t: UI.progress(P + "P", trial=t)),
             ("memories bar", lambda t: UI.progress(P + "P", kind="memories", trial=t)),
             ("tooltip", lambda t: UI.tooltip("Hi", trial=t)), ("checkbox", lambda t: UI.checkbox(P + "C", trial=t)),
             ("checkbox row", lambda t: UI.checkbox_row(P + "R", P + "L", P + "C", trial=t)),
             ("gradient", lambda t: UI.gradient_label(P + "G", trial=t)),
             ("number field", lambda t: UI.text_field(P + "Nb", P + "N", 100, number=True, trial=t)),
             ("slot background", lambda t: UI.item_grid_style(slot_bg=True, trial=t)),
             ("disabled element", lambda t: UI.button(P + "X", "X", disable_element=True, trial=t)),
             ("value ref", lambda t: UI.java_ref_style(P + "X", "SecondaryTextButtonStyle", trial=t)),
             ("dropdown", lambda t: UI.dropdown(P + "D", trial=t)), ("search", lambda t: UI.search_field(P + "S", P + "F", trial=t)),
             ("spinner", lambda t: UI.spinner(P + "S", trial=t)), ("tile", lambda t: UI.tile(P + "T", trial=t)),
             ("quality frame", lambda t: UI.quality_frame(P + "Q", trial=t)),
             ("quality tooltip", lambda t: UI.tooltip_panel(P + "Q", quality="Rare", trial=t)))
    for name, fn in gated:
        raises(lambda: fn(False), UI.UnverifiedError, "%s needs trial=True" % name, "UNVERIFIED")
        try:
            check(bool(fn(True)), "%s works with trial=True" % name)
        except Exception as e:
            FAILS.append("%s with trial=True raised %s" % (name, e))
    UI.PROBED.add("itemslot")
    try:
        check(bool(UI.item_slot(P + "S", P + "T")), "a PROBED feature needs no trial")
    except UI.UnverifiedError:
        FAILS.append("a PROBED feature still needs trial=True")
    finally:
        UI.PROBED.discard("itemslot")
    check('Value.ref("Common.ui", "SecondaryTextButtonStyle")' in UI.java_ref_style(P + "X", "SecondaryTextButtonStyle", trial=True)
          and "Common/UI" not in UI.java_ref_style(P + "X", "SecondaryTextButtonStyle", trial=True),
          "Value.ref line keeps lint's 'Common/UI' rule quiet")

    # text scale
    check(UI.text_scale() == "readable" and "FontSize: 18" in UI.label(P + "A", "", "rowName"), "readable scale: row name 18")
    UI.text_scale("vanilla")
    try:
        check("FontSize: 14" in UI.label(P + "A", "", "rowName") and "Height: 42" in UI.panel_row(P + "R"), "vanilla scale: 14 / 42")
        check("FontSize: 16" in UI.label(P + "A", "", "default"), "labels of 16 never scale")
        check("Height: 20, Bottom: 2" in UI.property_row(P + "A", P + "K", P + "V"), "vanilla scale: property row 20")
    finally:
        UI.text_scale("readable")
    raises(lambda: UI.text_scale("huge"), ValueError, "unknown text scale")
    check("FontSize: 15" in UI.title_label(P + "T") and 'FontName: "Secondary"' in UI.title_label(P + "T"), "title never scales")
    raises(lambda: UI.row_text(P + "A", P + "B", P + "C", row_h=30), ValueError, "row text taller than its row")

    # check_markup negatives (the parse check must catch each)
    negatives = (("unbalanced", "Group #SkyyTA { "), ("underscore", "Group #SkyyT_A { }"),
                 ("Anchow", "Group #SkyyTA { Anchow: (Width: 1); }"), ("double semicolon", "Group #SkyyTA { Anchor: (Width: 1);; }"),
                 ("variable", "Group #SkyyTA { Style: @DefaultLabelStyle; }"), ("import", "$C.@TextButton #SkyyTA { }"),
                 ("unknown texture", 'Group #SkyyTA { Background: "Common/Nope.png"; }'),
                 ("unknown quality texture", 'Group #SkyyTA { Background: "../ItemQualities/Slots/SlotShiny.png"; }'),
                 ("brace after a property", "Group #SkyyTA { Style: { } }"), ("unproven text", 'Label #SkyyTA { Text: "a,b"; }'),
                 ("runtime text", 'Label #SkyyTA { Text: "' + UI.J("x") + '"; }'), ("close before open", "Group #SkyyTA { Anchor: )Width: 1(; }"),
                 ("unterminated quote", 'Label #SkyyTA { Text: "abc; }'), ("placeholder", "Group #SkyyTRow%R { }"),
                 ("wrong prefix", "Group #SkyyXA { }"), ("empty", "   "))
    for name, mk in negatives:
        raises(lambda: UI.check_markup(mk, prefix=P), ValueError, "check_markup catches: " + name)
    raises(lambda: UI.check_markup("Group #SkyyTA { Anchor: (Width: 1, Height: 2, Top: 3); }", root=True), ValueError,
           "root anchor with more than Width / Height", "Width / Height only")
    check(UI.check_markup("Group #SkyyTA { Anchor: (Width: 1, Height: 2); }", root=True) is not None, "a Width / Height root passes")
    raises(lambda: UI.check_page(UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 1, Height: 2); }"),
                                             ("SkyyTNope", "Group #SkyyTB { }")])), ValueError, "append into a missing parent")
    raises(lambda: UI.fit([10, 20], 25), ValueError, "fit over budget")

    # Java emission
    tricky = 'a "quoted" \\ back\nnew\ttab - Café – ✓'
    check(UI.java_unlit(UI.java_lit(tricky)) == tricky, "java_lit round trip (quotes, backslash, newline, tab, unicode)")
    raises(lambda: UI.java_lit(UI.J("x")), ValueError, "java_lit refuses a runtime value", "java_expr")
    raises(lambda: UI.java_lit("bell\x07"), ValueError, "java_lit refuses control characters")
    check(UI.java_expr("a" + UI.J("i") + "b") == '"a" + (i) + "b"', "java_expr middle value")
    check(UI.java_expr(UI.J("i") + UI.J("j")) == '"" + (i) + (j)', "java_expr leading values start with an empty string")
    check(UI.java_expr("") == '""' and UI.java_expr("x") == '"x"', "java_expr without values")
    check(UI.java_append(None, "Group #SkyyTA { Anchor: (Width: 1, Height: 2); }") ==
          'b.appendInline((String) null, "Group #SkyyTA { Anchor: (Width: 1, Height: 2); }");', "java_append root")
    check(UI.java_append("SkyyTA", "Label { }", "cmd") == 'cmd.appendInline("#SkyyTA", "Label { }");', "java_append parent")
    check(UI.java_append("#SkyyTA", "Label { }") == 'b.appendInline("#SkyyTA", "Label { }");', "java_append parent with #")
    check(UI.java_append("SkyyTRow" + UI.J("r"), "Label { }") == 'b.appendInline("#SkyyTRow" + (r), "Label { }");', "java_append runtime parent")
    raises(lambda: UI.java_append(None, "Group #SkyyH { Anchor: (Full: 0); }"), ValueError, "java_append checks a page root",
           "Width / Height only")
    check(UI.java_append(None, "Group #SkyyH { Anchor: (Full: 0); }", page_root=False).startswith("b.appendInline((String) null"),
          "java_append page_root=False for a HUD root")
    raises(lambda: UI.java_append("SkyyTA", "Label { Anchow: 1; }"), ValueError, "java_append checks raw extra= text", "Anchow")
    raises(lambda: UI.java_append("SkyyTA", UI.label(P + "A", extra="Anchow: 1")), ValueError, "a typo in extra= stops at java_append")
    check(UI.java_set(P + "Name", "Text", UI.J("name")) == 'b.set("#SkyyTName.Text", "" + (name));', "java_set runtime String value")
    check(UI.java_set(P + "Pr", "Value", 0.5) == 'b.set("#SkyyTPr.Value", 0.5f);', "java_set float literal")
    check(UI.java_set(P + "Ck", "Value", True) == 'b.set("#SkyyTCk.Value", true);', "java_set boolean literal")
    check(UI.java_set(P + "N", "Value", 3) == 'b.set("#SkyyTN.Value", 3);', "java_set int literal")
    check(UI.java_set(P + "Pr", "Value", UI.J("f"), raw=True) == 'b.set("#SkyyTPr.Value", (f));', "java_set raw J() = a typed expression")
    check(UI.java_set_raw(P + "X", "Visible", "on") == 'b.set("#SkyyTX.Visible", (on));', "java_set_raw")
    raises(lambda: UI.java_set(P + "X", "Value", "a" + UI.J("f"), raw=True), ValueError, "java_set raw needs exactly one J()")
    raises(lambda: UI.java_set(P + "X", "Value", None), ValueError, "java_set refuses None")
    check(UI.java_field("ROW", 'Label { Text: "x"; }') == 'public static final String ROW = "Label { Text: \\"x\\"; }";', "java_field")
    raises(lambda: UI.java_field("bad name", "x"), ValueError, "java_field refuses a bad name")
    raises(lambda: UI.java_field("ROW\n", "x"), ValueError, "java_field refuses a trailing newline")
    mk = samples["button secondary normal"]
    check(UI.for_fstring(mk).format() == mk, "for_fstring survives str.format")
    check(("x = %s; " + UI.for_percent("50% of {")) % 1 == "x = 1; 50% of {", "for_percent survives % formatting")
    for raw in (False, True):
        line = UI.java_append(P + "Body", mk) + "  // {braces}"
        src = "X = %sf'''%s'''\n" % ("r" if raw else "", UI.for_pysource(line, raw=raw, quote="'''"))
        ns = {}
        exec(compile(src, "<for_pysource>", "exec"), ns)
        check(ns["X"] == line, "for_pysource round trip through a %s f-string" % ("raw" if raw else "non-raw"))
    raises(lambda: UI.for_pysource('a """ b'), ValueError, "for_pysource refuses the template quote")
    raises(lambda: UI.for_pysource('ends with "'), ValueError, "for_pysource refuses a trailing quote")
    check(UI.render("Row" + UI.J("i", "7")) == "Row7", "render uses the J() sample")
    raises(lambda: UI.J("", "0"), ValueError, "empty J() refused")
    raises(lambda: UI.J("x", 'a"b'), ValueError, "J() sample with a quote refused")

    class _Cls(object):
        def __init__(self):
            self.fields = []

        def addField(self, f):
            self.fields.append(f)

    class _CtField(object):
        @staticmethod
        def make(src, cls):
            return src

    c = _Cls()
    check(UI.emit_fields(c, {"A": "Group { }", "B": 'x "y"'}, _CtField) == 2 and c.fields[1] == 'public static final String B = "x \\"y\\"";',
          "emit_fields hands CtField.make the field source")
    check(UI.java_expr(UI.status_line(P + "St", "colorOf(info)")).count("(colorOf(info))") == 1, "status_line colour is a runtime value")
    sw = samples["status line wrap"]
    check("Anchor: (Height: 44, Top: 12);" in sw and "Wrap: true, WrapMaxLines: 2" in sw and "RenderBold: true" in sw,
          "status_line wrap / max_lines / anchor (kit 1.2)")
    check("Wrap" not in samples["status line"] and UI.render(samples["status line"]) ==
          'Label #SkyyTStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 16, TextColor: #39f493, RenderBold: true, '
          'HorizontalAlignment: Center, VerticalAlignment: Center); }', "status_line default output unchanged by kit 1.2")
    # group(): a plain layout container, no look (kit 1.2)
    check(samples["group row"] == "Group #SkyyTGrp { Anchor: (Height: 44, Top: 4); LayoutMode: Left; }", "group row (plain, no look)")
    check(samples["group anon column"] == "Group { Anchor: (Width: 300); FlexWeight: 1; LayoutMode: Top; Padding: (Full: 8); }",
          "anonymous group column")
    check("Padding: (Horizontal: 8, Vertical: 4); Visible: true; }" in samples["group padding dict"], "group padding dict + extra")
    check(all("Background" not in samples[k] for k in ("group row", "group anon column", "group padding dict")), "group has no look")
    check(UI.group(P + "G", None) == "Group #SkyyTG { }", "group without a layout")
    raises(lambda: UI.group(P + "G", "Diagonal"), ValueError, "group refuses an unknown LayoutMode", "LayoutMode")
    raises(lambda: UI.group(P + "G", "Left", w=0), ValueError, "group refuses a zero width", "> 0")
    raises(lambda: UI.group(P + "G", "Left", pad=-1), ValueError, "group refuses a negative padding")
    raises(lambda: UI.check_markup(UI.group(P + "G", "Left", h=40), root=True), ValueError, "a group is never a page root",
           "Width / Height only")
    gp = UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 900, Height: 600); }"), ("SkyyTA", UI.group(P + "Row", "Left", h=44)),
                     (P + "Row", UI.button(P + "Ok", "Ok", "primary", anchor={"right": 6})), (P + "Row", UI.button(P + "No", "No"))])
    try:
        UI.check_page(gp, P)
        check(True, "a group row holding kit buttons passes check_page")
    except ValueError as e:
        FAILS.append("group row page: %s" % e)
    check(("E", "        Group {\n          LayoutMode: Left;\n\n          Group #SelectedPackBox {", "plain layout row (group)")
          in UI.checks(), "group() has its vanilla proof (PrefabSavePage plain row)")
    meths = UI.java_status_methods()
    check(len(meths) == 2 and "#39f493" in meths[0] and "substring(1)" in meths[1], "status methods source")
    check(re.match(r"^skyyui \d+\.\d+ [0-9a-f]{12}$", UI.kit_id()) is not None, "kit_id format")

    # rarity palette = Skyy's lock (2026-09-25) and the live tables
    want = {"Normal": "#FFFFFF", "Unique": "#FFFF55", "Rare": "#FF55FF", "Legendary": "#55FFFF", "Fabled": "#FF5555",
            "Mythic": "#CC66CC", "Set": "#55FF55"}
    check(UI.RARITY == want, "RARITY = the locked Wynn ladder (Mythic readable #CC66CC)")
    check(UI.RARITY_WYNN["Mythic"] == "#AA00AA" and all(UI.RARITY_WYNN[k] == v for k, v in want.items() if k != "Mythic"),
          "RARITY_WYNN keeps Wynn's #AA00AA Mythic")
    check(UI.RARITY_ORDER == list(want), "rarity order")
    gear = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.1.py")
    if os.path.isfile(gear):
        gt = open(gear, encoding="utf-8").read()
        rows = dict((m.group(1), m.group(3)) for m in re.finditer(r'\("\w+", "(\w+)", "(#\w+)", "(#\w+)"', gt))
        check(all(rows.get(k, "").upper() == v.upper() for k, v in want.items()), "RARITY = SkyyGear 0.1 RARITIES page hex")
    sacks = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.7.py")
    if os.path.isfile(sacks):
        stx = open(sacks, encoding="utf-8").read()
        rows = dict((m.group(1), (m.group(2), m.group(3))) for m in re.finditer(r'\("Skyy_Bag_\w+",\s*"(\w+)",\s*"(#\w+)",\s*"(#\w+)"', stx))
        check(len(rows) == 5 and all(rows[k][1].upper() == want[k].upper() for k in rows), "RARITY = SkyySacks 0.7.7 bag page hex")
        check(rows.get("Mythic", ("", ""))[0].upper() == UI.RARITY_WYNN["Mythic"], "RARITY_WYNN = SkyySacks 0.7.7 bag tooltip Mythic")
    for d in (UI.RARITY, UI.RARITY_WYNN, UI.QUALITY):
        check(all(UI.norm_color(v) in ALLOWED for v in d.values()), "rarity / quality colours are allowed colours")
    return samples


# ================================================================= probe pages (the in-game gate)
def phase_probes():
    pages = UI.probe_pages()
    keys = [p.key for p in pages]
    check([p.n for p in pages] == list(range(1, len(pages) + 1)), "probe pages are numbered 1..n")
    check(keys[:2] == ["base", "base"], "probe pages 1-2 are the base look")
    check(set(keys) == set(UI.UNVERIFIED), "every UNVERIFIED feature has a probe page (missing: %s, extra: %s)"
          % (sorted(set(UI.UNVERIFIED) - set(keys)), sorted(set(keys) - set(UI.UNVERIFIED))))
    check(len(set(keys[2:])) == len(keys[2:]), "one probe page per UNVERIFIED feature")
    for pg in pages:
        check(pg.shell.h <= UI.MAX_PAGE_H and pg.look and pg.look[0].startswith("the page opens"), "probe %d fits 1080 and says what to see"
              % pg.n)
        try:
            pg.check()
            check(True, "probe %d check_page" % pg.n)
        except ValueError as e:
            FAILS.append("probe %d: %s" % (pg.n, e))
        for i, (par, mk) in enumerate(pg.shell.appends):
            markup_ok("probe %d append %d" % (pg.n, i), mk, root=(par is None), prefix=pg.shell.prefix)
        js = pg.java("b")
        check(js.count("appendInline") == len(pg.shell.appends) and not lint_java_line(js), "probe %d Java" % pg.n)
    base = "\n".join(UI.render(mk) for pg in pages[:2] for _p, mk in pg.shell.appends)
    for feat in ("FlexWeight", "LayoutMode: Right", "LayoutMode: Full", "LetterSpacing: 0.5", "WrapMaxLines", "ShrinkTextToFit",
                 "Disabled: (", "Sounds: (", "ContainerDecorationTop", "Top: -8, Right: -8", "#000000(0.15)", "Tertiary_Active",
                 "ContainerHeaderNoRunes", "Top: -2"):
        check(feat in base, "base probe pages cover %s" % feat)
    return pages


# ================================================================= the style guide names only real kit functions
def phase_guide():
    path = os.path.join(ROOT, "research", "Vanilla-UI-Style-Guide.md")
    text = open(path, encoding="utf-8").read()
    names = set(re.findall(r"SUI\.([A-Za-z_][A-Za-z0-9_]*)", text)) | set(re.findall(r"`([a-z_][a-z0-9_]*)\(", text))
    names |= set(n for cell in re.findall(r"`([^`|]*)`", text) for n in re.findall(r"(?<![.\w])([a-z_][a-z0-9_]*)\(", cell))
    names -= {"list", "set", "dict", "tuple", "sorted"}         # Python builtins / the Java set(String, ...) overloads the guide cites
    check(len(names) >= 40, "the guide names the kit functions (%d found)" % len(names))
    for n in sorted(names):
        check(hasattr(UI, n), "the style guide names SUI.%s, which the kit does not have" % n)
    check("import skyyui as SUI" in text and "import skyyui as UI" not in text, "the guide imports the kit as SUI")
    for k in UI.LABELS:
        check(k in text, "the guide lists the label kind %s" % k)


# ================================================================= the lint rules (tools/ci/lint.py kit warnings, WARN only)
def phase_lint():
    path = os.path.join(HERE, "ci", "lint.py")
    text = open(path, encoding="utf-8").read()
    want = {"_Unres", "_Stub", "_STUB", "_lev", "_kit_lev", "_kit_strs", "_kit_code_lines", "KIT_IMPORT_RE", "KIT_HEX_RE",
            "KIT_PY_COMMENT_RE", "KIT_MAX_WARNS", "KIT_PATH_RE", "KIT_FONT_RE", "kit_color_warnings", "kit_style_warnings"}
    nodes = []
    for node in ast.parse(text).body:
        names = {node.name} if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else \
            {t.id for t in node.targets if isinstance(t, ast.Name)} if isinstance(node, ast.Assign) else set()
        if names & want:
            nodes.append(node)
    ns = {"re": re, "ast": ast, "__name__": "lintpart"}
    try:
        exec(compile(ast.Module(body=nodes, type_ignores=[]), path, "exec"), ns)
    except Exception as e:
        FAILS.append("lint.py kit rules could not be loaded: %s" % e)
        return
    check("kit_color_warnings" in ns and "kit_style_warnings" in ns, "lint.py has the kit colour + style rules")
    if "kit_color_warnings" not in ns or "kit_style_warnings" not in ns:
        return
    script = "\n".join([
        "import skyyui as SUI",
        "UI_DATA_COLORS = ['#8fd67a', '#e0b060']       # class colours",
        'A = "Label { Style: (TextColor: #96a9be); }"',                 # kit colour
        'B = "Group { Background: #0b1524(0.96); }"',                  # the old dark-blue panel -> WARN
        'C = "Label { Style: (TextColor: #FFFF55); }"',                # rarity (Unique)
        'D = "Label { Style: (TextColor: #8fd67a); }"',                # a declared data colour
        'E = "Label { Style: (TextColor: #ff00ff); }"  # ui-data',    # marked line
        'F = "Group { Background: #ffffff(0.3); }"',                  # alpha on a kit colour
        'G = "Group { Background: #000000(0.35); }"',                 # alpha on a non-kit colour -> WARN
        "# old style #123456 in a comment",                            # comment
        'H = "Group #SkyyAbc { }"',                                   # an element id, not a colour
        'I = "Group #Facade { Label #Decade { } }"',                  # hex-looking element ids
        'J = "b.set(\\"#Facade.Text\\", x)"',                         # a hex-looking selector
        'K = "#ffffff(...) and #123456(1.2.3) and #abcdef(.)"',       # malformed alphas: skipped, never a crash
    ])
    try:
        w = ns["kit_color_warnings"]("SkyyX/build_skyyx_0.1.py", script, UI)
        check(len(w) == 2 and ":4 colour #0b1524(0.96)" in w[0] and ":9 colour #000000(0.35)" in w[1],
              "lint kit colour rule flags only the non-kit colours: %s" % w)
    except Exception as e:
        FAILS.append("lint kit colour rule crashed: %s: %s" % (type(e).__name__, e))
    env_script = "\n".join([
        "import skyyui as SUI",
        'CLS = {"Warrior": "#aa3333", "Mage": ("#3366cc", "x")}',
        'EXTRA = ["#123abc"]',
        "UI_DATA_COLORS = list(CLS.values()) + EXTRA + ['#8fd67a', unknown_call(), UNKNOWN_NAME]",
        'A = "Label { Style: (TextColor: #aa3333); } Label { Style: (TextColor: #3366cc); }"',
        'B = "Label { Style: (TextColor: #123abc); } Label { Style: (TextColor: #8fd67a); }"',
        'C = "Label { Style: (TextColor: #0b1524); }"',
    ])
    w = ns["kit_color_warnings"]("SkyyX/build_skyyx_0.1.py", env_script, UI)
    check(len(w) == 1 and ":7 colour #0b1524" in w[0],
          "UI_DATA_COLORS built from earlier module constants (unreadable elements skipped): %s" % w)
    style_script = "\n".join([
        "import skyyui as SUI",
        'A = "Group { Background: (TexturePath: \\"Common/Nope.png\\", Border: 3); }"',      # not a kit texture -> WARN
        'B = "Label { Style: (FontName: \\"Comic\\"); }"',                                     # not a vanilla font -> WARN
        'C = "Group { Background: \\"Common/ContainerPatch.png\\"; }"',                        # kit texture
        'D = "Label { Style: (FontName: \\"Secondary\\"); }"',                                 # vanilla font
        'E = "Sounds: (Activate: (SoundPath: \\"Sounds/Boom.ogg\\"))"',                         # not a kit sound -> WARN
        'F = "Group { Background: \\"Pages/Mine/Art.png\\"; }"  # ui-data',                    # marked line
        'G = "Group { Background: \\"../ItemQualities/Slots/SlotRare.png\\"; }"',              # kit quality frame
        'ICON = "Icons/ItemsGenerated/Skyy_Coin.png"',                                         # an asset path, not UI markup
    ])
    w = ns["kit_style_warnings"]("SkyyX/build_skyyx_0.1.py", style_script, UI)
    check(len(w) == 3 and ":2 path Common/Nope.png" in w[0] and ':3 FontName "Comic"' in w[1] and ":6 path Sounds/Boom.ogg" in w[2],
          "lint kit style rule flags only non-kit paths / fonts: %s" % w)
    check(ns["KIT_IMPORT_RE"].search(script) is not None and ns["KIT_IMPORT_RE"].search("import skyyuiX\nx = 1") is None,
          "lint kit import detection")


# ================================================================= phase 4: javassist compile
def phase_java(samples, probes):
    try:
        import jpype
        import skyybuild as B
    except ImportError as e:
        print("java phase skipped: %s" % e)
        return
    if not os.path.isfile(B.JAVASSIST):
        print("java phase skipped: no tools/javassist.jar")
        return
    os.environ["TEMP"] = os.environ["TMP"] = SCRATCH
    out = os.path.join(SCRATCH, "classes")
    os.makedirs(out, exist_ok=True)
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", "-Djava.io.tmpdir=" + SCRATCH, "--add-opens=java.base/java.lang=ALL-UNNAMED",
                   "--enable-native-access=ALL-UNNAMED", classpath=[B.JAVASSIST], convertStrings=True)
    Jc = jpype.JClass
    pool = Jc("javassist.ClassPool")(False)
    pool.appendSystemPath()
    CtField, CtNewMethod, CtNewConstructor = Jc("javassist.CtField"), Jc("javassist.CtNewMethod"), Jc("javassist.CtNewConstructor")
    bc = pool.makeClass("skyyuitest.B")
    bc.addField(CtField.make("public java.lang.StringBuilder sb;", bc))
    bc.addConstructor(CtNewConstructor.make("public B() { this.sb = new java.lang.StringBuilder(); }", bc))
    bc.addMethod(CtNewMethod.make('public void appendInline(String p, String m) { this.sb.append(p == null ? "<null>" : p).append("|")'
                                  '.append(m).append("\\n"); }', bc))
    # the real UICommandBuilder has set(String, String / int / float / double / boolean / Value / ...): the stub marks the overload
    for jt, mark in (("String", ""), ("int", "i"), ("float", "f"), ("boolean", "b")):
        bc.addMethod(CtNewMethod.make('public void set(String k, %s v) { this.sb.append("set ").append(k).append("=%s").append(v)'
                                      '.append("\\n"); }' % (jt, mark), bc))
    bc.addMethod(CtNewMethod.make("public String out() { return this.sb.toString(); }", bc))
    uc = pool.makeClass("skyyuitest.UiT")
    consts = {}
    for i, (name, mk) in enumerate(sorted(samples.items())):
        if not UI.has_j(mk):
            consts["M%d" % i] = mk
    consts["UNI"] = 'Café – ✓ "q" \\ back\nline'
    n = UI.emit_fields(uc, consts, CtField)
    for src in UI.java_status_methods():
        uc.addMethod(CtNewMethod.make(src, uc))
    row = UI.panel_row(P + "Row" + UI.J("i", "3"), "selected")
    br = UI.bar(P + "Bar" + UI.J("i", "3"), 400, 18, UI.J("fw", "120"), col=UI.J("col", "#ffcc00"))
    uc.addMethod(CtNewMethod.make("public static String row(int i) { return %s; }" % UI.java_expr(row), uc))
    uc.addMethod(CtNewMethod.make("public static String bar(int i, int fw, String col) { return %s; }" % UI.java_expr(br), uc))
    sh = UI.page_shell(P, 1000, 700, "Trade with Skyy, now", close=True)
    dl = UI.confirm_dialog(P + "D", yes_kind="destructive", title="Delete")
    shj = UI.page_shell(P, UI.J("w", "900"), UI.J("h", "600"), "Sized")
    uc.addMethod(CtNewMethod.make("public static String shell() { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                  % sh.java("b"), uc))
    uc.addMethod(CtNewMethod.make("public static String dialog(String q) { skyyuitest.B cmd = new skyyuitest.B();\n%s\nreturn cmd.out(); }"
                                  % dl.java("cmd", sets=[(dl.question, "Text", UI.J("q"))]), uc))
    uc.addMethod(CtNewMethod.make("public static String shellj(int w, int h) { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                  % shj.java("b"), uc))
    typed = [UI.java_set(P + "Pr", "Value", 0.75), UI.java_set(P + "Ck", "Value", True), UI.java_set(P + "N", "Value", 3),
             UI.java_set(P + "Pf", "Value", UI.J("f"), raw=True), UI.java_set_raw(P + "V", "Visible", "on"),
             UI.java_set(P + "T", "Text", UI.J("n")), UI.java_set_raw(P + "Q", "Value", "n")]
    uc.addMethod(CtNewMethod.make("public static String typed(float f, boolean on, int n) { skyyuitest.B b = new skyyuitest.B();\n%s\n"
                                  "return b.out(); }" % "\n".join(typed), uc))
    for pg in probes:
        uc.addMethod(CtNewMethod.make("public static String probe%d() { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                      % (pg.n, pg.java("b", extra=False)), uc))
    bc.writeFile(out)
    uc.writeFile(out)
    url = Jc("java.io.File")(out).toURI().toURL()
    loader = Jc("java.net.URLClassLoader")(jpype.JArray(Jc("java.net.URL"))([url]))
    U = jpype.JClass("skyyuitest.UiT", loader=loader)
    for k, v in consts.items():
        check(str(getattr(U, k)) == v, "javassist field %s equals the Python markup" % k)
    check(str(U.row(3)) == UI.render(row), "java_expr method (row) equals the Python markup")
    check(str(U.bar(3, 120, "#ffcc00")) == UI.render(br), "java_expr method (bar) equals the Python markup")

    def fmt(v):
        if isinstance(v, bool):
            return "b" + ("true" if v else "false")
        if isinstance(v, int):
            return "i%d" % v
        if isinstance(v, float):
            return "f" + repr(v)
        return UI.render(v)

    def expect(appends, sets):
        lines = ["%s|%s" % ("<null>" if p is None else "#" + UI.render(p), UI.render(mk)) for p, mk in appends]
        lines += ["set #%s.%s=%s" % (i, pr, fmt(v)) for i, pr, v in sets]
        return "\n".join(lines) + "\n"

    check(str(U.shell()) == expect(sh.appends, sh.sets), "page_shell().java() compiles and builds exactly the Python appends")
    check(str(U.dialog("Delete rank vip?")) == expect(dl.appends, [(dl.question, "Text", "Delete rank vip?")]),
          "confirm_dialog().java(sets=...) compiles and builds exactly the Python appends")
    check(str(U.shellj(900, 600)) == expect(shj.appends, shj.sets), "a runtime-size page_shell compiles and builds the Python appends")
    check(str(U.typed(0.25, True, 7)) == "set #SkyyTPr.Value=f0.75\nset #SkyyTCk.Value=btrue\nset #SkyyTN.Value=i3\n"
          "set #SkyyTPf.Value=f0.25\nset #SkyyTV.Visible=btrue\nset #SkyyTT.Text=7\nset #SkyyTQ.Value=i7\n",
          "typed java_set lines pick the float / boolean / int overloads: %s" % str(U.typed(0.25, True, 7)).replace("\n", " | "))
    for pg in probes:
        check(str(getattr(U, "probe%d" % pg.n)()) == expect(pg.shell.appends, pg.shell.sets),
              "probe page %d compiles and builds exactly the Python appends" % pg.n)
    check(str(U.colorOf("+done")) == "#39f493" and str(U.colorOf("-no")) == "#ff6b6b" and str(U.colorOf("=x")) == "#E8A93B"
          and str(U.colorOf("")) == "#96a9be" and str(U.textOf("-no")) == "no" and str(U.textOf("plain")) == "plain",
          "java_status_methods compile and answer")
    for line in (sh.java("b") + "\n" + dl.java("cmd")).splitlines():
        check(not lint_java_line(line), "lint underscore-id rule on the shell Java line: " + line[:60])
    print("java phase: %d fields + %d methods compiled with javassist and compared" % (n, 8 + len(probes)))


def main():
    base = os.path.join(HERE, "dev", "scratch") + os.sep
    if not (SCRATCH + os.sep).lower().startswith(base.lower()) or SCRATCH.rstrip(os.sep).lower() == base.rstrip(os.sep).lower():
        raise SystemExit("--dir must be a folder inside tools/dev/scratch/ (it is emptied and deleted): " + SCRATCH)
    if os.path.exists(SCRATCH):
        shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    try:
        try:
            phase_verify()
        except UI.VanillaCheckError as e:
            FAILS.append("verify() failed: %s" % e)
            UI._STATE["verified"] = True      # already a FAIL; unlock the emitters so the rest of the test still reports
        phase_structure()
        samples = phase_builders()
        probes = phase_probes()
        phase_guide()
        phase_lint()
        if NOJAVA:
            print("java phase skipped (--no-java)")
        else:
            phase_java(samples, probes)
    finally:
        if not KEEP:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    for f in FAILS:
        print("  FAIL:", f)
    print("%d ok, %d fail" % (OKS[0], len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
