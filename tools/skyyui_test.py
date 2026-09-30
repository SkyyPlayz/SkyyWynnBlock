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
        # kit 1.3: @TitleStyle's LetterSpacing: 0 is the engine default and is not written (= the deployed Ranks / Vault titles)
        vt = C.text("(...@TitleStyle, HorizontalAlignment: Center)")
        check(vt.get("LetterSpacing") == "0", "structure: vanilla @TitleStyle still has LetterSpacing 0 (the dropped default)")
        vt.pop("LetterSpacing", None)
        same("window title (LetterSpacing 0 dropped)", vt, kit_value(UI.title_style()))
        check("LetterSpacing" not in UI.title_style(), "kit 1.3: the title writes no LetterSpacing")
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
    # kit 1.3
    s["label heading no max lines"] = UI.label(P + "Lnm", "", "heading", max_lines=False)
    s["label heading wrap off"] = UI.label(P + "Lwo", "", "heading", wrap=False)
    s["label max lines 0"] = UI.label(P + "Lm0", "", "caption", wrap=True, max_lines=0)
    s["label zero spacing"] = UI.label(P + "Lzs", "", "strong", spacing=0)
    s["label zero spacing float"] = UI.label(P + "Lzf", "", "strong", spacing=0.0)
    s["status line wrap max 0"] = UI.status_line(P + "Stz", h=44, wrap=True, max_lines=0)
    s["item icon runtime"] = UI.item_icon(P + "Iir", UI.J("ids[i]", "Weapon_Sword_Iron"))
    for st in UI.ICON_CELL_STATES:
        for lk in UI.ICON_CELL_LOOKS:
            s["icon cell %s %s" % (st, lk)] = UI.icon_cell(P + "Ic" + st[:2].title() + lk[:2].title(), "Weapon_Sword_Iron", 74, st,
                                                           look=lk)
    s["icon cell qty"] = UI.icon_cell(P + "Icq", "Ingredient_Bar_Iron", 74, qty="64")
    s["icon cell qty label"] = UI.icon_cell(P + "Icl", "Ingredient_Bar_Iron", 87, qty=True, anchor={"right": 6})
    s["icon cell runtime"] = UI.icon_cell(P + "Icr" + UI.J("i", "3"), UI.J("ids[i]", "Weapon_Sword_Iron"), 76)
    s["icon cell wide"] = UI.icon_cell(P + "Icw", "Weapon_Sword_Iron", w=158, h=76, icon=44, icon_left=6)
    s["icon cell silent"] = UI.icon_cell(P + "Ics", "Weapon_Sword_Iron", sound=None)
    s["icon cell no item"] = UI.icon_cell(P + "Icn", None, 64)
    s["item grid kit"] = UI.item_grid(P + "Ig", 9, 6)
    s["item grid bare"] = UI.item_grid(P + "Igb", 4, 1, well=False, tooltips=False, anchor={"left": 8})
    s["item grid runtime"] = UI.item_grid(P + "Igr", UI.J("g[0]", "4"), 2, slot=UI.J("g[1]", "72"), spacing=0,
                                          w=UI.J("g[2]", "288"), h=UI.J("g[3]", "144"))
    s["item grid slot bg"] = UI.item_grid(P + "Igs", 4, 1, slot_bg=True, trial=True, box_id=P + "IgsWell")
    s["item grid drag"] = UI.item_grid(P + "Igd", 32, 18, slot=40, icon=1, spacing=0, drag=True, well=False)
    # kit 1.4 (new names only: the 1.3 samples above are frozen by SNAP13)
    J = UI.J
    s["k14 static row full"] = UI.static_row(P + "Sr", 572, icon="Weapon_Sword_Iron", name="Iron sword", sub="Rare", tag="12 m",
                                             action="Equip")
    s["k14 static row punct"] = UI.static_row(P + "Sp", 572, icon=J("ids[i]", "Weapon_Sword_Iron"), name="Iron sword, +3",
                                              sub=J("sub(i)", "Rare"), bar=J("sel == i"), action="Unequip", action_w=112)
    s["k14 static row runtime id"] = UI.static_row(P + "Sq" + J("i", "2"), 572, name=J("nm", "Steve"), bar=None)
    s["k14 static row normal"] = UI.static_row(P + "Sn", 600, name="Click me", state="normal", bar=False)
    s["k14 static row selected"] = UI.static_row(P + "Ss", 600, name="Picked", sub="", state="selected", bar="warning",
                                                 action="Buy", action_kind="primary", action_on=False)
    s["k14 status bar on"] = UI.status_bar(P + "Stb")
    s["k14 status bar off"] = UI.status_bar(P + "Stb", False)
    s["k14 status bar runtime"] = UI.status_bar(P + "Stb", J("i == sel"), col="warning")
    s["k14 row bar anon"] = UI.row_bar(None)
    s["k14 list well"] = UI.list_well(P + "Lwl", w=580, rows=6)
    s["k14 list well h"] = UI.list_well(P + "Lwh", h=300, anchor={"top": 8})
    s["k14 result line"] = UI.result_line(P + "Rl", J("infoColor(this.info)", "#39f493"))
    s["k14 result line name"] = UI.result_line(P + "Rn", "info", h=30, wrap=False, anchor={"top": 12})
    bp = UI.stat_bar(P + "Sbar", 160, 8, J("stF[0]", "80"), col="progressBlue", anchor={"top": 4})
    s["k14 stat bar full"], s["k14 stat bar empty"] = bp.full, bp.empty
    s["k14 stat bar static"] = UI.stat_bar(P + "Sbs", 300, 12, 120, col="progressGreen").pick()
    spec = UI.column_spec([("Member", 260), ("Health", 175), ("Where", 300)], avail=1300, pad_left=24)
    s["k14 column heads"] = spec.heads(P + "Chd")
    s["k14 column heads punct"] = UI.column_heads(P + "Chp", [("Name", 200), ("Lvl.", 80)], pad_left=12, gap=8)
    s["k14 column row"] = spec.row(P + "Crw", ["Steve", J("hp", "18"), "Hub, near spawn"], kinds=["rowName", "default", "rowSub"])
    s["k14 column row plain"] = UI.column_row(P + "Crp", spec, panel_kind=None, gap=0)
    s["k14 stat well"] = UI.stat_well(P + "Swl", "Purse", J("fmt(purse)", "12345"), "coins you carry", w=527)
    s["k14 stat well punct"] = UI.stat_well(P + "Swp", "Bank", None, "safe when you die, always.", anchor={"left": 12},
                                            ids={"number": "SkyyTSwpNum"})
    s["k14 state word"] = UI.state_word(None, "Selected", "success")
    s["k14 state word punct"] = UI.state_word(P + "Wd", "Coming soon...", "disabled", anchor={"left": 14})
    s["k14 group bg"] = UI.group(P + "Gbg", "Left", w=4, h=84, bg=UI.color_by([("sel", "rowPressed"), ("pend", "rowHover")], "row"))
    s["k14 panel bg"] = UI.panel(P + "Pbg", "row", h=56, bg=J('on ? "#132033(0.8)" : "#101925(0.55)"', "#132033(0.8)"))
    s["k14 item frame item"] = UI.item_frame(P + "Ifi", 64, item=J("ic[k]", "Weapon_Sword_Iron"), icon_anchor={"left": 0, "top": 0})
    s["k14 item frame cover"] = UI.item_frame(P + "Ifc", item="Food_Bread", cover=True, cover_id=P + "IfcOut")
    s["k14 icon cell static"] = UI.icon_cell(P + "Ics14", "Food_Bread", 74, "static", qty="12")
    s["k14 icon cell static plain"] = UI.icon_cell(P + "Icp14", "Food_Bread", 74, "static", look="plain")
    s["k14 button row right"] = UI.button_row(P + "Brr", align="right", used=350, avail=1066)
    s["k14 button row centre"] = UI.button_row(P + "Brc", align="center", used=372, w=900, top=0)
    s["k14 button row runtime"] = UI.button_row(P + "Brj", align="right", left_margin=J("gapR", "722"))
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
    check(UI.STATUS == {"+": "#39f493", "-": "#ff6b6b", "=": "#7caacc"}, "status marks = the vanilla success / error / info blue (1.3)")
    check(UI.STATUS_INFO == {"info": "#7caacc", "gold": "#E8A93B"} and UI.STATUS["="] == UI.COLOR["info"],
          "the gold '=' stays available by name")
    gm = UI.java_status_methods(info="gold")
    check("if (c == '=') return \"#E8A93B\";" in gm[0] and "if (c == '=') return \"#7caacc\";" in UI.java_status_methods()[0],
          "java_status_methods: info blue by default, info='gold' = the old gold")
    check("return \"#ffcc00\";" in UI.java_status_methods(info="warning")[0], "java_status_methods(info=<COLOR name>)")
    raises(lambda: UI.java_status_methods(info="nope"), ValueError, "java_status_methods refuses an unknown colour")
    raises(lambda: UI.java_status_methods(info=UI.J("c", "#ffffff")), ValueError, "java_status_methods refuses a J() colour")
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
    check("FontName" not in lf and "FontSize: 32" in lf and "TextColor: #ffffff" in lf,
          "display label: 32 px in the Default font (Hud/TimeLeft timer, kit 1.3)")
    chk = UI.checks()
    check(("HT", "TimerLabel #TimeLabel {\n      Style: (FontSize: 32, Alignment: Center);",
           "label display (Hud/TimeLeft timer, Default font)") in chk, "display cites the Hud/TimeLeft timer")
    check(not any("@TimeLimitStyle" in n for _d, n, _w in chk), "the unused PortalDeviceSummon @TimeLimitStyle is no longer cited")
    check(any(d == "PS" and "FontSize: 24" in n and 'FontName: "Secondary"' in n for d, n, _w in chk),
          "big Secondary text is proven as a title (PortalDeviceSummon 24 px)")
    check(any(d == "RS" and "FontSize: 38" in n for d, n, _w in chk), "RespawnPage 38 px Secondary title needle")
    check("Hud/TimeLeft" in UI.LABELS["display"][7] and "display" not in UI.LABEL_MORE, "display kind cites Hud/TimeLeft")
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


# ================================================================= kit 1.3 (the SkyyBank pilot review)
ROOT_MK = "Group #SkyyTA { Anchor: (Width: 1100, Height: 900); }"
BODY_MK = "Group #SkyyTBody { LayoutMode: Top; }"


def part_ok(name, part, root=True):
    """check_page of a Part under a stand-in root + body, markup_ok on every append (both variants of a Choice)."""
    ap = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    ap.extend(part)
    try:
        ap.check(P)
        check(True, name + " check_page")
    except ValueError as e:
        FAILS.append("%s: check_page refused it: %s" % (name, e))
    for i, (par, mk) in enumerate(part):
        for j, v in enumerate(UI._variants(mk)):
            markup_ok("%s append %d.%d" % (name, i, j), v)
    return ap


def phase_kit13(samples):
    # ---- finding 4: LetterSpacing 0 is never written; WrapMaxLines only with Wrap: true, never 0
    for name, mk in samples.items():
        plain = UI.render(mk)
        check(re.search(r"LetterSpacing: 0(?![.\d])", plain) is None, name + ": LetterSpacing 0 written")
        check("WrapMaxLines: 0" not in plain, name + ": WrapMaxLines 0 written")
        check(plain.count("WrapMaxLines") == plain.count("Wrap: true, WrapMaxLines"), name + ": WrapMaxLines without Wrap: true")
    check("WrapMaxLines" not in samples["label heading no max lines"] and "Wrap: true" in samples["label heading no max lines"],
          "max_lines=False removes the kind's WrapMaxLines (heading keeps Wrap)")
    check("WrapMaxLines" not in samples["label heading wrap off"] and "Wrap" not in samples["label heading wrap off"],
          "wrap=False drops the kind's WrapMaxLines too")
    check("WrapMaxLines" not in samples["label max lines 0"] and "Wrap: true" in samples["label max lines 0"], "max_lines=0 = none")
    check("LetterSpacing" not in samples["label zero spacing"] and "LetterSpacing" not in samples["label zero spacing float"],
          "spacing=0 / 0.0 writes no LetterSpacing")
    check("LetterSpacing: 0.5" in UI.label(P + "A", "", "strong", spacing=0.5), "spacing=0.5 still written")
    check("WrapMaxLines" not in samples["status line wrap max 0"], "status_line max_lines=0 = none")
    raises(lambda: UI.text_style(16, "text", max_lines=2), ValueError, "text_style WrapMaxLines without wrap", "Wrap: true")
    raises(lambda: UI.label(P + "A", "", "caption", max_lines=2), ValueError, "label max_lines without wrap", "Wrap: true")
    raises(lambda: UI.status_line(P + "A", max_lines=2), ValueError, "status_line max_lines without wrap", "Wrap: true")
    raises(lambda: UI.label(P + "A", "", "heading", max_lines=-1), ValueError, "negative max_lines")
    raises(lambda: UI.label(P + "A", "", "heading", max_lines=True), ValueError, "max_lines=True refused")
    raises(lambda: UI.label(P + "A", "", "heading", max_lines=1.5), ValueError, "max_lines float refused")
    check("Wrap: true, WrapMaxLines: 1" in UI.label(P + "A", "", "heading"), "heading keeps its vanilla Wrap + WrapMaxLines 1")
    check("Wrap: true, WrapMaxLines: 3" in UI.label(P + "A", "", "caption", wrap=True, max_lines=3), "explicit wrap + max_lines")

    # ---- item_icon with a runtime id (inline, as the deployed cells do)
    check(UI.java_expr(samples["item icon runtime"]) == '"ItemIcon #SkyyTIir { Anchor: (Width: 32, Height: 32); ItemId: \\"" + (ids[i]) '
          '+ "\\"; }"', "item_icon J() id is written inline")
    raises(lambda: UI.item_icon(P + "A", UI.J("x", "bad id")), ValueError, "runtime item id sample must be an item id")
    raises(lambda: UI.item_icon(P + "A", "a" + UI.J("x", "B")), ValueError, "runtime item id is one J()")
    raises(lambda: UI.item_icon(P + "A", 'x"y'), ValueError, "static item id with a quote")

    # ---- G4: Appends.text / Shell.text
    ap = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    i1 = ap.text("SkyyTBody", P + "Cap", "your whole purse", "caption", w=200)
    i2 = ap.text("SkyyTBody", P + "Mid", "max 1,000,000 coins (5%).", "caption", w=300)
    i3 = ap.text("SkyyTBody", None, "Page 1 of 3?", "default")
    i4 = ap.text("SkyyTBody", None, "Page 2 of 3?", "default")
    i5 = ap.text("SkyyTBody", None, "plain inline", "default")
    i6 = ap.text("SkyyTBody", P + "Run", UI.J("name", "Skyy"), "strong")
    check(i1 == P + "Cap" and 'Text: "your whole purse"' in ap[2][1], "Appends.text: proven text inline")
    check(i2 == P + "Mid" and 'Text: ""' in ap[3][1] and (P + "Mid", "Text", "max 1,000,000 coins (5%).") in ap.sets,
          "Appends.text: punctuated text = empty label + b.set line")
    check(i3 == "SkyyTBodyTx0" and i4 == "SkyyTBodyTx1" and i5 is None, "Appends.text: auto ids <parent>Tx<n>, anonymous inline")
    check((P + "Run", "Text", UI.J("name", "Skyy")) in ap.sets, "Appends.text: J() text = a b.set line")
    try:
        ap.check(P)
        check(True, "Appends.text page passes check_page")
    except ValueError as e:
        FAILS.append("Appends.text page: %s" % e)
    js = ap.java("b")
    check(js.index("b.set(\"#SkyyTMid.Text\", \"max 1,000,000 coins (5%).\");") > js.rindex("appendInline"),
          "Appends.java: the b.set lines come after every append")
    check('b.set("#SkyyTRun.Text", "" + (name));' in js, "Appends.java: runtime text set")
    raises(lambda: UI.Appends().text(None, None, "x,y"), ValueError, "Appends.text into the root refused")
    raises(lambda: UI.Appends().text("SkyyTBody", P + "Bad_Id", "x,y"), ValueError, "Appends.text id with an underscore", "underscore")
    bad = UI.Appends([(None, ROOT_MK)])
    bad.sets.append((P + "Ghost", "Text", "x"))
    raises(lambda: bad.check(P), ValueError, "check_page: a b.set line whose target no append created", "no append created")
    blk = UI.Appends()
    blk.text("SkyyTBody", P + "Blk", "a, b and c", "caption")
    a2 = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    a2.extend(blk)
    check(a2.sets == [(P + "Blk", "Text", "a, b and c")] and len(a2) == 3, "Appends.extend carries .sets along")
    a3 = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    a3 += list(blk)
    check(a3.sets == [], "a plain list brings no .sets")
    a3 += blk
    check(a3.sets == blk.sets and len(a3) == 4, "Appends += carries .sets along")
    check(UI.Appends(ap).sets == ap.sets, "Appends(copy) keeps .sets")
    sh = UI.page_shell(P, 900, 600, "Shop")
    tid = sh.text(sh.body, None, "Buy 3 for 1,250 coins?", "default")
    check(tid == "SkyyTBodyTx0" and sh.all_sets() == [(tid, "Text", "Buy 3 for 1,250 coins?")] and not sh.sets,
          "Shell.text puts the b.set in the appends; all_sets lists it")
    check('b.set("#SkyyTBodyTx0.Text", "Buy 3 for 1,250 coins?");' in sh.java("b"), "Shell.java emits Appends.text sets")

    # ---- choose(): a markup picked at runtime
    ch = UI.choose(UI.J("pageNo > 0"), UI.button(P + "Pv", "Prev", size="small"), UI.button(P + "Pv", "Prev", size="small",
                                                                                          disabled=True))
    check(isinstance(ch, UI.Choice) and ch.cond == "pageNo > 0", "choose takes J(cond)")
    check(UI.choose("a && b", "Group #SkyyTX { }", "Group #SkyyTX { }").cond == "a && b", "choose takes a plain Java condition")
    jl = UI.java_append(P + "Row", ch)
    check(jl.startswith('b.appendInline("#SkyyTRow", (pageNo > 0) ? ("TextButton #SkyyTPv {') and ') : ("TextButton #SkyyTPv {' in jl,
          "java_append of a Choice = a ternary of both markups")
    raises(lambda: UI.choose("x; y", "Group #SkyyTX { }", "Group #SkyyTX { }"), ValueError, "choose refuses ';' in cond")
    raises(lambda: UI.choose("", "Group #SkyyTX { }", "Group #SkyyTX { }"), ValueError, "choose refuses an empty cond")
    raises(lambda: UI.choose("a" + UI.J("b"), "Group #SkyyTX { }", "Group #SkyyTX { }"), ValueError, "choose: cond is one J()")
    raises(lambda: UI.check_markup(UI.choose("c", "Group #SkyyTX { }", "Group #SkyyTY { }")), ValueError,
           "choose: both variants must create the same ids", "same element ids")
    raises(lambda: UI.check_markup(UI.choose("c", "Group #SkyyTX { }", "Group #SkyyTX { ")), ValueError,
           "choose: a broken variant is refused")
    cp = UI.Appends([(None, ROOT_MK), ("SkyyTA", "Group #SkyyTRow { LayoutMode: Left; }"), ("SkyyTRow", ch),
                     (P + "Pv", "Label #SkyyTPvL { }")])
    try:
        cp.check(P)
        check(True, "check_page knows the ids a Choice creates")
    except ValueError as e:
        FAILS.append("check_page with a Choice: %s" % e)

    # ---- G1 pager
    pg = UI.pager("SkyyTBody", P + "Pg", 1066, text="Page 2 / 5", prev_on=False)
    part_ok("pager static", pg)
    check((pg.row, pg.prev, pg.page, pg.next, pg.h) == (P + "Pg", P + "PgPrev", P + "PgPage", P + "PgNext", 32 + 8), "pager ids + h")
    prev_mk, next_mk = pg[1][1], pg[3][1]
    check(prev_mk.count("Disabled.png") == 4 and "Sounds" not in prev_mk and "Width: 150" in prev_mk and "Left: 241" in prev_mk,
          "pager: Prev in the vanilla Disabled look, centred by a computed left margin ((1066 - 584) / 2)")
    check("Secondary.png" in next_mk and "ButtonsLightActivate" in next_mk and "Height: 32" in next_mk and "FontSize: 14" in next_mk,
          "pager: Next = small Secondary with the light click")
    check('Text: "Page 2 / 5"' in pg[2][1] and not pg.sets and "HorizontalAlignment: Center" in pg[2][1], "pager caption inline")
    check("LayoutMode: Left" in pg[0][1] and "LayoutMode: Center" not in "".join(pg.markups()) and
          "FlexWeight" not in "".join(pg.markups()), "pager uses only LayoutMode Left + margins")
    pj = UI.pager("SkyyTBody", P + "Pj", 900, text=UI.J("pageText()"), prev_on=UI.J("pageNo > 0"), next_on=UI.J("pageNo < pages - 1"))
    part_ok("pager runtime", pj)
    check(isinstance(pj[1][1], UI.Choice) and isinstance(pj[3][1], UI.Choice) and pj.sets == [(P + "PjPage", "Text", UI.J("pageText()"))],
          "pager: J() states = choose(), J() text = a b.set line")
    pt = UI.pager("SkyyTBody", P + "Pt", 900, text="Page 2 of 5, 40 items", align="left", top=0)
    part_ok("pager left", pt)
    check(pt.sets == [(P + "PtPage", "Text", "Page 2 of 5, 40 items")] and "Left:" not in pt[1][1] and pt.h == 32,
          "pager: punctuated caption = b.set, align left, top 0")
    check("Left: 316" in UI.pager("SkyyTBody", P + "Pr", 900, align="right")[1][1], "pager align right")
    po = UI.pager("SkyyTBody", "SkyyTOld", 900, ids={"prev": "SkyyTOldPrevious", "page": "SkyyTOldNo"})
    check(po.prev == "SkyyTOldPrevious" and po.page == "SkyyTOldNo" and po.next == "SkyyTOldNext", "pager ids= keeps old ids")
    raises(lambda: UI.pager("SkyyTBody", P + "Pg", 500), ValueError, "pager wider than w")
    raises(lambda: UI.pager("SkyyTBody", P + "Pg", 900, align="middle"), ValueError, "pager align")
    raises(lambda: UI.pager("SkyyTBody", P + "Pg", 900, prev_on="yes"), ValueError, "pager state must be bool or J()")
    raises(lambda: UI.pager("SkyyTBody", P + "P_g", 900), ValueError, "pager id with an underscore", "underscore")

    # ---- G7 confirm_view
    cv = UI.confirm_view("SkyyTBody", P + "Cf", 1066, question="Delete rank vip?", message="Nothing has changed yet")
    part_ok("confirm view", cv)
    check((cv.box, cv.question, cv.message, cv.note, cv.row, cv.yes, cv.no) ==
          (P + "Cf", P + "CfQ", P + "CfMsg", None, P + "CfBtns", P + "CfYes", P + "CfNo"), "confirm_view ids")
    check(cv.h == 2 * 20 + (46 + 12) + (48 + 16) + (44 + 8) + 8, "confirm_view h (padding 20, question, message, row, top 8)")
    check(cv.sets == [(P + "CfQ", "Text", "Delete rank vip?")] and 'Text: "Nothing has changed yet"' in cv[2][1],
          "confirm_view: a '?' question is b.set, a proven message inline")
    yes = [mk for _p, mk in cv if mk.startswith("TextButton #SkyyTCfYes")][0]
    no = [mk for _p, mk in cv if mk.startswith("TextButton #SkyyTCfNo")][0]
    check("Primary.png" in yes and "SaveActivate" in yes and "Left: 327" in yes and "Right: 6" in yes,
          "confirm_view yes = Primary + save sound, centred ((1026 - 372) / 2 = 327)")
    check("Secondary.png" in no and "ButtonsCancelActivate" in no and "Left: 6" in no, "confirm_view no = Secondary + cancel")
    check("Background: #000000(0.15)" in cv[0][1] and "Padding: (Full: 20)" in cv[0][1] and "#ffcc00" in cv[1][1] and "FontSize: 32" in cv[1][1],
          "confirm_view: the well, padding 20, the #ffcc00 32 px question")
    cd = UI.confirm_view("SkyyTBody", P + "Cd", 900, question=UI.J("q"), message="", note="Costs 5,000 coins", yes_kind="destructive",
                         panel="row")
    part_ok("confirm view destructive", cd)
    check(cd.note == P + "CdNote" and (P + "CdNote", "Text", "Costs 5,000 coins") in cd.sets and (P + "CdQ", "Text", UI.J("q")) in cd.sets
          and "#101925(0.55)" in cd[0][1], "confirm_view: note, J question, row panel")
    cdy = [mk for _p, mk in cd if mk.startswith("TextButton #SkyyTCdYes")][0]
    check("Destructive.png" in cdy and "ButtonsCancelActivate" in cdy and "SaveActivate" not in cdy, "confirm_view destructive yes")
    cn = UI.confirm_view("SkyyTBody", P + "Cn", 900, panel=None, pad=0, top=0)
    check("Background" not in cn[0][1] and "Padding" not in cn[0][1] and cn.h == 58 + 64 + 52, "confirm_view panel=None, pad 0")
    cc = UI.confirm_view("SkyyTBody", P + "Cc", 900, question="Switch to Mage for 500 coins?", compact=True)
    part_ok("confirm view compact", cc)
    check(cc.h == 44 + 16 + 8 and cc.message is None and "LayoutMode: Left" in cc[0][1] and "Width: 504" in cc[1][1]
          and "#ffcc00" in cc[1][1], "confirm_view compact: one row, the question takes what is left")
    raises(lambda: UI.confirm_view("SkyyTBody", P + "Cc", 500, compact=True), ValueError, "confirm_view compact too narrow")
    raises(lambda: UI.confirm_view("SkyyTBody", P + "Cc", 900, panel="glass"), ValueError, "confirm_view panel kind")
    raises(lambda: UI.confirm_view("SkyyTBody", P + "Cc", 900, yes_kind="tertiary"), ValueError, "confirm_view yes kind")
    raises(lambda: UI.confirm_view("SkyyTBody", P + "Cc", None), ValueError, "confirm_view needs an int width")

    # ---- G3 icon_cell
    ic = samples["icon cell normal row"]
    check(ic.startswith("Button #SkyyTIcNoRo { Anchor: (Width: 74, Height: 74); Style: ButtonStyle(Default: (Background: #101925(0.55)), "
                        "Hovered: (Background: #132033(0.8)), Pressed: (Background: #182a40(0.9)), Sounds: (")
          and "ItemIcon #SkyyTIcNoRoIc { Anchor: (Width: 64, Height: 64, Left: 5, Top: 5); ItemId: \"Weapon_Sword_Iron\"; }" in ic,
          "icon_cell normal = the WorldEventListRow palette + light click, a centred 64 px icon")
    check(samples["icon cell selected row"].count("#4274a5") == 3, "icon_cell selected = #4274a5 (@SelectedRowStyle)")
    dis = samples["icon cell disabled row"]
    check("Sounds" not in dis and "#0a0e12(0.75)" in dis and dis.count("#101925(0.55)") == 3, "icon_cell disabled: static, silent, covered")
    check("ItemIcon" not in samples["icon cell empty row"] and "Sounds" not in samples["icon cell empty row"], "icon_cell empty: no icon")
    check("Hovered: (Background: #000000(0.2))" in samples["icon cell normal plain"] and "#7a9cc6(0.25)" in samples["icon cell selected plain"],
          "icon_cell plain look (ItemRepairElement / BasicTextButton)")
    check('Label #SkyyTIcqQty' in samples["icon cell qty"] and 'Text: "64"' in samples["icon cell qty"] and
          "HorizontalAlignment: End" in samples["icon cell qty"], "icon_cell static quantity")
    check('Label #SkyyTIclQty { Anchor: (Width: 79, Height: 20, Right: 4, Bottom: 3); Text: ""' in samples["icon cell qty label"],
          "icon_cell qty=True = an empty quantity label to b.set")
    check("Left: 6, Top: 16" in samples["icon cell wide"] and "Width: 158, Height: 76" in samples["icon cell wide"], "icon_cell wide")
    check("Sounds" not in samples["icon cell silent"], "icon_cell sound=None")
    check("ItemId" not in samples["icon cell no item"] and "ItemIcon #SkyyTIcnIc" in samples["icon cell no item"], "icon_cell item=None")
    rj = UI.java_expr(samples["icon cell runtime"])
    check('"Button #SkyyTIcr" + (i) + " {' in rj and 'ItemId: \\"" + (ids[i]) + "\\"' in rj, "icon_cell runtime id + item")
    raises(lambda: UI.icon_cell(P + "A", "X", state="hot"), ValueError, "icon_cell state")
    raises(lambda: UI.icon_cell(P + "A", "X", look="neon"), ValueError, "icon_cell look")
    raises(lambda: UI.icon_cell(P + "A", "X", qty="lots"), ValueError, "icon_cell qty text")
    raises(lambda: UI.icon_cell(P + "A", "X", size=16), ValueError, "icon_cell too small")
    raises(lambda: UI.icon_cell(P + "A", "X", icon=90), ValueError, "icon_cell icon bigger than the cell")
    raises(lambda: UI.icon_cell(P + "A_b", "X"), ValueError, "icon_cell underscore id", "underscore")
    csel = UI.choose(UI.J("i == sel"), UI.icon_cell(P + "Cs", "X", state="selected"), UI.icon_cell(P + "Cs", "X"))
    check(UI.check_markup(csel) is csel, "icon_cell states as a runtime choice")

    # ---- G2 item_grid + the grid Java
    g = samples["item grid kit"]
    check(g == ("Group #SkyyTIgBox { Anchor: (Width: 690, Height: 462); Background: #000000(0.15); ItemGrid #SkyyTIg { Anchor: (Width: 682, "
                "Height: 454, Left: 4, Top: 4); SlotsPerRow: 9; AreItemsDraggable: false; Style: (SlotSize: 74, SlotIconSize: 64, "
                "SlotSpacing: 2); } }"), "item_grid: the well, 9 x 74 + 8 x 2 = 682 wide, the client inventory style")
    check(samples["item grid bare"] == ("ItemGrid #SkyyTIgb { Anchor: (Width: 302, Height: 74, Left: 8); SlotsPerRow: 4; AreItemsDraggable: "
                                        "false; InfoDisplay: None; Style: (SlotSize: 74, SlotIconSize: 64, SlotSpacing: 2); }"),
          "item_grid bare, tooltips=False = InfoDisplay: None (SkyyAuctions)")
    gr = UI.java_expr(samples["item grid runtime"])
    check('"Group #SkyyTIgrBox { Anchor: (Width: " + ((g[2]) + 8) + ", Height: " + ((g[3]) + 8)' in gr and
          "SlotsPerRow: \" + (g[0]) + \";" in gr and "SlotSize: \" + (g[1]) + \"," in gr, "item_grid with runtime geometry")
    check("AreItemsDraggable: true" in samples["item grid drag"] and "Width: 1280, Height: 720" in samples["item grid drag"],
          "item_grid drag canvas (the SkyyHud editor numbers)")
    check("Group #SkyyTIgsWell" in samples["item grid slot bg"] and "BlockSelectorSlotBackground" in samples["item grid slot bg"],
          "item_grid box_id + slot_bg (trial)")
    raises(lambda: UI.item_grid(P + "G", 4, 1, slot_bg=True), UI.UnverifiedError, "item_grid slot_bg needs trial=True", "UNVERIFIED")
    raises(lambda: UI.item_grid(P + "G", UI.J("c", "4"), 2), ValueError, "item_grid runtime cols need w / h")
    raises(lambda: UI.item_grid(P + "G", 0, 2), ValueError, "item_grid zero columns")
    raises(lambda: UI.item_grid(P + "G", 2, 2, slot=40, icon=64), ValueError, "item_grid icon bigger than its slot")
    raises(lambda: UI.item_grid(P + "G", 2, 2, spacing=-1), ValueError, "item_grid negative spacing")
    raises(lambda: UI.item_grid(P + "G_x", 2, 2), ValueError, "item_grid underscore id", "underscore")
    gm = UI.java_grid_methods()
    check(len(gm) == 4 and gm[0].startswith("public static com.hypixel.hytale.server.core.ui.ItemGridSlot gridSlot(String itemId, int qty)")
          and "gridSlotOf(com.hypixel.hytale.server.core.inventory.ItemStack s)" in gm[1] and "gridSlots(String[] ids" in gm[2]
          and "gridSlotsOf(com.hypixel.hytale.server.core.inventory.ItemStack[] a" in gm[3], "java_grid_methods: 4 methods in call order")
    allj = "\n".join(gm)
    check(UI.item_grid_java_is_safe(allj) and allj.count("new com.hypixel.hytale.server.core.ui.ItemGridSlot(new "
                                                         "com.hypixel.hytale.server.core.inventory.ItemStack(itemId, qty))") == 1,
          "java_grid_methods: the ONLY filled slot is new ItemGridSlot(new ItemStack(itemId, qty))")
    check("s.getItemId(), s.getQuantity()" in gm[1] and "new com.hypixel.hytale.server.core.ui.ItemGridSlot(s" not in allj,
          "gridSlotOf copies id + quantity, never passes the stack")
    check("public static" in UI.java_grid_methods("slot", "a.B", "a.C")[0] and "slotSlot(" in UI.java_grid_methods("slot", "a.B", "a.C")[0],
          "java_grid_methods prefix + class names")
    raises(lambda: UI.java_grid_methods("Grid"), ValueError, "java_grid_methods prefix must be lower-case")
    raises(lambda: UI.java_grid_methods("grid", "a b"), ValueError, "java_grid_methods refuses a bad class name")
    gf = UI.java_grid_fill(P + "Ig", [("Weapon_Sword_Iron", 1), None, (UI.J("ids[k]", "Food_Bread"), UI.J("qs[k]", "3"))], var="pbSlots")
    check(gf.splitlines()[0] == "java.util.ArrayList pbSlots = new java.util.ArrayList();" and
          'pbSlots.add(new com.hypixel.hytale.server.core.ui.ItemGridSlot(new com.hypixel.hytale.server.core.inventory.ItemStack('
          '"Weapon_Sword_Iron", 1)));' in gf and "pbSlots.add(new com.hypixel.hytale.server.core.ui.ItemGridSlot());" in gf and
          '"" + (ids[k]), (qs[k]))));' in gf and gf.endswith('b.set("#SkyyTIg.Slots", (pbSlots));'), "java_grid_fill statements")
    check(UI.item_grid_java_is_safe(gf), "java_grid_fill never passes a raw stack")
    raises(lambda: UI.java_grid_fill(P + "Ig", [("Weapon_Sword_Iron", 0)]), ValueError, "java_grid_fill quantity >= 1")
    raises(lambda: UI.java_grid_fill(P + "Ig", [("bad id", 1)]), ValueError, "java_grid_fill item id")
    raises(lambda: UI.java_grid_fill(P + "Ig", [], var="Bad"), ValueError, "java_grid_fill var name")
    raises(lambda: UI.java_grid_fill(P + "I_g", []), ValueError, "java_grid_fill underscore id", "underscore")
    for src, want in (("slots.add(new com.hypixel.hytale.server.core.ui.ItemGridSlot(st));", False),
                      ("x = new com.hypixel.hytale.server.core.ui.ItemGridSlot( stack.copy());", False),
                      ("x = new com.hypixel.hytale.server.core.ui.ItemGridSlot();", True),
                      ("x = new com.hypixel.hytale.server.core.ui.ItemGridSlot(new com.hypixel.hytale.server.core.inventory.ItemStack(i, 1));", True)):
        check(UI.item_grid_java_is_safe(src) == want, "item_grid_java_is_safe: %s" % src[:60])
    # the rule the kit enforces on a whole probe page's Java (page 18 fills its grid)
    check(UI.item_grid_java_is_safe(UI.probe_page("base3").java("b")), "probe base3 fills its grid only with new ItemStack(id, qty)")


# ================================================================= kit 1.4 (the stage-1b restyle reviews; additive only)
def _func_from(path, name, ns):
    """exec one top-level function of a (read-only) repo script into ns (the held restyles' own helpers, for equivalence tests)."""
    text = open(path, encoding="utf8").read()
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            exec(compile(ast.get_source_segment(text, node), path, "exec"), ns)
            return ns[name]
    return None


def _card_block():
    """The SKYY CARD block of SkyyClasses 0.1.8 / SkyyProfiles 0.1.3 (tools/classes_0_1_8_patch.py CARD_BLOCK, CARD_SHA-checked),
    exec'd with this kit: {card_java, card_state, card_button, card_list, card_list_h, card_text_w, ...} or None."""
    import hashlib
    path = os.path.join(HERE, "classes_0_1_8_patch.py")
    if not os.path.isfile(path):
        return None
    text = open(path, encoding="utf8").read()
    blk = sha = None
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == "CARD_BLOCK":
                blk = ast.literal_eval(node.value)
            elif node.targets[0].id == "CARD_SHA":
                sha = ast.literal_eval(node.value)
    if blk is None or sha is None or hashlib.sha256(blk.encode("utf8")).hexdigest() != sha:
        return None
    ns = {"SUI": UI, "re": re}
    exec(compile(blk, path + " [CARD_BLOCK]", "exec"), ns)
    return ns


def phase_kit14(samples):
    J = UI.J
    UI.fit_warnings("collect", clear=True)
    # ---- Markup, Appends.add / used_height / used_width / outer_size / is_flex / java_add
    row = samples["k14 static row full"]
    check(isinstance(row, UI.Markup) and isinstance(row, str) and row.h == 56 + 3 and row.w == 572, "Markup: a str with .h / .w")
    check(UI.outer_size(UI.label(P + "A", "", "default", h=30, anchor={"top": 12, "bottom": 4})) == (None, 46)
          and UI.outer_size(UI.button(P + "A", "Go", w=200, anchor={"left": 6, "right": 4})) == (210, 44)
          and UI.outer_size(UI.separator("vertical")) == (6, None) and UI.outer_size(UI.group(P + "A", "Left", h=40, anchor={"full": 3}))
          == (None, 46), "outer_size: Width / Height + margins (Full / Horizontal / Vertical count twice)")
    check(UI.outer_size(UI.group(P + "A", "Left", h=J("hh", "40"), anchor={"top": J("t", "8")})) == (None, 48), "outer_size: J() samples")
    check(UI.outer_size(UI.dropdown(P + "Dd", w=300, h=32, search=True, trial=True)) == (300, 32),
          "outer_size reads the element's own Anchor, not one inside its Style (dropdown SearchInputStyle Anchor)")
    raises(lambda: UI.outer_size(UI.choose("c", UI.label(P + "A", "", h=20), UI.label(P + "A", "", h=30))), ValueError,
           "outer_size: a choice whose looks differ in size", "different outer sizes")
    check(UI.is_flex(UI.button(P + "A", "x", flex=1)) and not UI.is_flex(UI.button(P + "A", "x")), "is_flex")
    ap = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    hs = [ap.add("SkyyTBody", UI.label(P + "L1", "", "default", h=30, anchor={"bottom": 4})), ap.add("SkyyTBody", row),
          ap.add("SkyyTBody", UI.scroll_list(P + "Fl")), ap.add("SkyyTBody", samples["k14 stat well"])]
    check(hs == [34, 59, None, 118], "Appends.add returns each outer height (None for a flex list): %s" % hs)
    check(UI.used_height(ap, "SkyyTBody") == 34 + 59 + 118 and ap.used("SkyyTBody") == 211, "used_height sums the outer heights (flex = 0)")
    check((P + "SwlN", "Text", J("fmt(purse)", "12345")) in ap.sets, "Appends.add carries a Markup's .sets along")
    ap.add("SkyyTBody", UI.label(P + "L2", "", "default", h=False))
    raises(lambda: UI.used_height(ap, "SkyyTBody"), ValueError, "used_height refuses a child without a Height or a FlexWeight",
           "cannot be proven")
    rw = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK), ("SkyyTBody", UI.group(P + "Rw", "Left", h=44))])
    for mk in (UI.button(P + "B1", "One", w=172, anchor={"right": 6}), UI.button(P + "B2", "Two", w=172), UI.spacer(12, 44)):
        rw.add(P + "Rw", mk)
    check(UI.used_width(rw, P + "Rw") == 172 + 6 + 172 + 12 and rw.used(P + "Rw", "w") == 362, "used_width of a LayoutMode Left row")
    jl = UI.java_add("SkyyTBody", samples["k14 stat well"])
    check(jl.count("appendInline") == 1 and 'b.set("#SkyyTSwlN.Text", "" + (fmt(purse)));' in jl, "java_add = the append + its b.set lines")
    ch = UI.choose(J("c"), UI.state_word(P + "Sw", "A, b", "success"), UI.state_word(P + "Sw", "A, b", "disabled"))
    check(UI.Appends().add("SkyyTBody", ch) == 44, "Appends.add of a Choice of two Markups")
    raises(lambda: UI.Appends().add("SkyyTBody", UI.choose(J("c"), UI.state_word(P + "Sw", "A, b"), UI.state_word(P + "Sw", "C, d")))
           , ValueError, "Appends.add refuses two looks with different texts", "different b.set lines")
    # ---- margins + button_row(used=)
    check(UI.right_margin(1066, 350) == 716 and UI.centre_margin(900, 372) == 264, "right_margin / centre_margin")
    raises(lambda: UI.right_margin(300, 350), ValueError, "right_margin that does not fit")
    br = samples["k14 button row right"]
    check(br == "Group #SkyyTBrr { Anchor: (Height: 44, Top: 8); LayoutMode: Left; Padding: (Left: 716); }" and br.left == 716,
          "button_row(used=) right-aligns with Padding Left, no LayoutMode Right")
    check("Padding: (Left: 264)" in samples["k14 button row centre"] and "Width: 900" in samples["k14 button row centre"],
          "button_row(used=) centres (avail = w)")
    check(UI.java_expr(samples["k14 button row runtime"]).endswith('LayoutMode: Left; Padding: (Left: " + (gapR) + "); }"'),
          "button_row(left_margin=J()) = a runtime Padding Left (SkyyParty gapR)")
    check(type(UI.button_row(P + "Br")) is str and UI.button_row(P + "Br", align="right") ==
          "Group #SkyyTBr { Anchor: (Height: 44, Top: 8); LayoutMode: Right; }", "button_row without used= is the kit 1.3 row")
    raises(lambda: UI.button_row(P + "Br", align="right", used=100), ValueError, "button_row(used=) needs avail / w")
    raises(lambda: UI.button_row(P + "Br", left_margin=J("x", "wide")), ValueError, "button_row left_margin sample must be a number")
    # ---- status_bar / static_row
    check(samples["k14 status bar on"] == "Group #SkyyTStb { Anchor: (Width: 4, Right: 8); Background: #4274a5; }"
          and samples["k14 status bar off"] == "Group #SkyyTStb { Anchor: (Width: 4, Right: 8); }", "status_bar on / off (space kept)")
    sj = UI.java_expr(samples["k14 status bar runtime"])
    check('+ ((i == sel) ? "Background: #ffcc00; " : "") + "}"' in sj and UI.render(samples["k14 status bar runtime"]) ==
          "Group #SkyyTStb { Anchor: (Width: 4, Right: 8); Background: #ffcc00; }", "status_bar(on=J()) = a runtime Background property")
    check(UI.row_bar is UI.status_bar, "row_bar is status_bar")
    raises(lambda: UI.status_bar(P + "S", "yes"), ValueError, "status_bar on must be bool / J()")
    r = samples["k14 static row full"]
    check(r.startswith("Group #SkyyTSr { Anchor: (Height: 56, Bottom: 3); LayoutMode: Left; Group #SkyyTSrP { Anchor: (Width: 476, "
                       "Height: 56); LayoutMode: Left; Background: #101925(0.55); Padding: (Left: 8, Right: 8); Group #SkyyTSrBar {")
          and "ItemIcon #SkyyTSrIc { Anchor: (Width: 40, Height: 40, Left: 0, Top: 8); ItemId: \"Weapon_Sword_Iron\"; }" in r
          and "Group #SkyyTSrT { Anchor: (Width: 238, Height: 56); LayoutMode: Top; Padding: (Top: 6); " in r
          and 'Label #SkyyTSrTg { Anchor: (Width: 150, Height: 56, Left: 8); Text: "12 m";' in r
          and "TextButton #SkyyTSrAct { Anchor: (Width: 92, Height: 56, Left: 4);" in r and r.text_w == 238 and not r.sets,
          "static_row: panel 572 - 96, padding 2 x 8, bar 12, icon box 52, text 238, tag 150 + 8, action 92 + 4 (SkyyAccessories 0.4.5 geometry)")
    check(r.ids == {"row": P + "Sr", "panel": P + "SrP", "bar": P + "SrBar", "icon_box": P + "SrIb", "icon": P + "SrIc", "text": P + "SrT",
                    "name": P + "SrNm", "sub": P + "SrSb", "tag": P + "SrTg", "action": P + "SrAct"}, "static_row .ids: %s" % r.ids)
    rp = samples["k14 static row punct"]
    check(rp.sets == [(P + "SpNm", "Text", "Iron sword, +3"), (P + "SpSb", "Text", J("sub(i)", "Rare"))] and 'Text: ""' in rp
          and "Width: 112" in rp, "static_row: punctuated / J() texts become b.set lines")
    rn = samples["k14 static row normal"]
    check("Button #SkyyTSnP {" in rn and "ButtonsLightActivate" in rn and "SkyyTSnBar" not in rn and "SkyyTSnAct" not in rn,
          "static_row state normal = a clickable Button panel, bar=False = no bar")
    rs = samples["k14 static row selected"]
    check(rs.count("#4274a5") == 3 and "Background: #ffcc00" in rs and rs.count("Disabled.png") == 4 and "Width: 150" in rs,
          "static_row selected + a colour bar + a disabled small Primary action")
    rj = samples["k14 static row runtime id"]
    check(UI.render(rj).startswith("Group #SkyyTSq2 {") and "Group #SkyyTSq2Bar { Anchor: (Width: 4, Right: 8); }" in UI.render(rj)
          and rj.sets == [(P + "Sq" + J("i", "2") + "Nm", "Text", J("nm", "Steve"))], "static_row: a runtime id, bar=None keeps the space")
    raises(lambda: UI.static_row(P + "Sx", 200, icon="Weapon_Sword_Iron", tag="x", action="Go"), ValueError, "static_row too narrow")
    raises(lambda: UI.static_row(P + "Sx", 572, action="Go", action_on=J("c")), ValueError, "static_row action_on runtime -> choose")
    raises(lambda: UI.static_row(P + "S_x", 572), ValueError, "static_row underscore id", "underscore")
    raises(lambda: UI.static_row(P + "Sx", 572, name="a, b", ids={"name": None}), ValueError, "static_row b.set text needs an id")
    # ---- list_well / result_line / java_color_by_text
    lw = samples["k14 list well"]
    check(lw == UI.panel(P + "Lwl", "well", w=580, h=8 + 6 * 59, pad=4) and lw.inner_w == 572 and lw.inner_h == 354 and lw.h == 362,
          "list_well = panel well, padding 4 (6 rows of 56 + 3)")
    check(UI.list_well_h(2, 84, 4) == UI.list_card_h(2) == 184, "list_well_h / list_card_h")
    raises(lambda: UI.list_well(P + "L"), ValueError, "list_well needs h or rows")
    check(samples["k14 result line"] == UI.status_line(P + "Rl", "infoColor(this.info)", h=44, wrap=True),
          "result_line = the status line look with any colour (J() here)")
    check("TextColor: #7caacc" in samples["k14 result line name"] and "Wrap" not in samples["k14 result line name"],
          "result_line with a colour name, one line")
    raises(lambda: UI.result_line(P + "R"), ValueError, "result_line needs a colour")
    jc = UI.java_color_by_text("infoColor", [("startsWith", "upgraded to ", "+"), ("contains", " could not", "-"),
                                             ("equals", "done", "success"), ("endsWith", "?", "=")], empty="=", default="-")
    check(jc.startswith("public static String infoColor(String t) {") and 'if (t.startsWith("upgraded to ")) return "#39f493";' in jc
          and 'if (t.indexOf(" could not") >= 0) return "#ff6b6b";' in jc and 'if (t.equals("done")) return "#39f493";' in jc
          and 'if (t.endsWith("?")) return "#7caacc";' in jc and jc.endswith('  return "#ff6b6b";\n}'), "java_color_by_text source")
    raises(lambda: UI.java_color_by_text("InfoColor", []), ValueError, "java_color_by_text name")
    raises(lambda: UI.java_color_by_text("c", [("like", "x", "+")]), ValueError, "java_color_by_text test")
    raises(lambda: UI.java_color_by_text("c", [("equals", "x", J("q", "#ffffff"))]), ValueError, "java_color_by_text J colour")
    # ---- stat_bar
    full, empty = samples["k14 stat bar full"], samples["k14 stat bar empty"]
    check(UI.render(empty) == "Group #SkyyTSbar { Anchor: (Width: 160, Height: 8, Top: 4); LayoutMode: Left; Background: #1a2030; }"
          and UI.render(full) == ("Group #SkyyTSbar { Anchor: (Width: 160, Height: 8, Top: 4); LayoutMode: Left; Background: #1a2030; "
                                  "Group { Anchor: (Width: 80, Height: 8); Background: #4a7caa; } }"),
          "stat_bar: the SkyyParty 0.1.6 track + fill; the empty variant has no fill child")
    bp = UI.stat_bar(P + "Sbar", 160, 8, J("stF[0]", "80"), col="progressBlue", anchor={"top": 4})
    cb = bp.choose()
    check(isinstance(cb, UI.Choice) and cb.cond == "(stF[0]) > 0" and UI.check_markup(cb) is cb and bp.h == 12,
          "stat_bar.choose() = choose(fill > 0, full, empty), both looks check")
    check(UI.stat_bar(P + "Sb", 100, 8, 0).pick() == UI.stat_bar(P + "Sb", 100, 8, 0).empty and
          UI.stat_bar(P + "Sb", 100, 8, 5).pick() == UI.stat_bar(P + "Sb", 100, 8, 5).full, "stat_bar.pick() for a static fill")
    raises(lambda: UI.stat_bar(P + "Sb", 100, 8, 5).choose(), ValueError, "stat_bar.choose() of a static fill")
    raises(lambda: UI.stat_bar(P + "Sb", 100, 8, -1), ValueError, "stat_bar negative fill")
    # ---- columns
    spec = UI.column_spec([("Member", 260), ("Health", 175), ("Where", 300)], avail=1300, pad_left=24, gap=10)
    check(spec.total == 755 and spec.slack == 1300 - 24 - 755 and spec.width("Health") == 175 and spec.x(0) == 24 and spec.x(2) == 24 + 260
          + 10 + 175 + 10, "Columns: total, slack, width, x")
    raises(lambda: UI.column_spec([("A", 500), ("B", 500)], avail=900), ValueError, "columns wider than avail")
    raises(lambda: UI.column_spec([("A", 0)]), ValueError, "a zero-width column")
    ch_ = samples["k14 column heads"]
    check(ch_.startswith("Group #SkyyTChd { Anchor: (Height: 30); LayoutMode: Left; Padding: (Left: 24); Label { Anchor: (Width: 260, "
                         'Height: 30); Text: "Member";') and ch_.count("Label {") == 3 and not ch_.sets, "column_heads = SkyyParty's heads")
    chp = samples["k14 column heads punct"]
    check(chp.sets == [(P + "ChpH1", "Text", "Lvl.")] and "Right: 8" in chp and "Label #SkyyTChpH1 {" in chp, "column_heads punctuated + gap")
    check(spec.heads(P + "Hx", outside=4).count("Padding: (Left: 28)") == 1, "Columns.heads(outside=) adds the well padding")
    cr = samples["k14 column row"]
    check("Label #SkyyTCrwC0 { Anchor: (Width: 260, Height: 56);" in cr and "Background: #101925(0.55)" in cr and
          cr.sets == [(P + "CrwC1", "Text", J("hp", "18")), (P + "CrwC2", "Text", "Hub, near spawn")] and cr.h == 59,
          "column_row: one fixed-width cell per column, texts by b.set, row panel")
    check("Background" not in samples["k14 column row plain"] and samples["k14 column row plain"].h == 56, "column_row without a panel")
    raises(lambda: UI.column_row(P + "C", spec, texts=["a"]), ValueError, "column_row texts per column")
    # ---- stat_well = SkyyBank 0.1.4's PURSE box
    bank = UI._inside(UI.panel("SkyyBPurseBox", "well", w=527, h=118), [
        UI.label(None, "Purse", "subtitle", h=25, align="Center", anchor={"bottom": 10}), UI.label("SkyyBPurse", "", "display", h=42, align="Center"),
        UI.label(None, "coins you carry - lost in part when you die", "caption", h=25, align="Center")])
    sw = UI.stat_well("SkyyBPurseBox", "Purse", None, "coins you carry - lost in part when you die", w=527, ids={"number": "SkyyBPurse"})
    check(sw == bank and sw.h == 118 and not sw.sets, "stat_well = the SkyyBank 0.1.4 PURSE well, nested")
    swp = samples["k14 stat well punct"]
    check(swp.sets == [(P + "SwpC", "Text", "safe when you die, always.")] and "Label #SkyyTSwpNum {" in swp and swp.h == 118,
          "stat_well punctuated caption + ids")
    raises(lambda: UI.stat_well(P + "S", number="1,000"), ValueError, "stat_well number must be J() / proven / None")
    # ---- color_by / group(bg=) / panel(bg=) / state_word / item_frame / icon_cell static
    cbj = UI.color_by([("sel", "rowPressed"), (J("pend"), "rowHover")], "row")
    check(UI.java_expr("x" + cbj).endswith('(sel) ? "#182a40(0.9)" : ((pend) ? "#132033(0.8)" : ("#101925(0.55)")))')
          and UI.render(cbj) == "#182a40(0.9)", "color_by: the SKYY CARD look chain from colour names")
    raises(lambda: UI.color_by([("a", J("c", "#ffffff"))], "row"), ValueError, "color_by refuses J() colours")
    raises(lambda: UI.color_by([("a", "nope")], "row"), ValueError, "color_by validates the colour names")
    check(UI.group(P + "G", None, w=4, h=84, bg="selected") == UI.group(P + "G", None, w=4, h=84, extra="Background: #4274a5"),
          "group(bg=) = the hand-written extra=\"Background: ...\"")
    check(UI.panel(P + "Pn", "well", h=40, bg="rowHover") == UI.panel(P + "Pn", "well", h=40).replace("#000000(0.15)", "#132033(0.8)"),
          "panel(bg=) swaps the colour of a colour panel")
    raises(lambda: UI.panel(P + "Pn", "simple", bg="row"), ValueError, "panel(bg=) on a texture panel")
    raises(lambda: UI.group(P + "G", bg="nope"), ValueError, "group(bg=) validates the colour")
    check(samples["k14 state word"] == UI.label(None, "Selected", "success", w=172, h=44, align="Center", bold=True),
          "state_word = the SKYY CARD card_state")
    check(samples["k14 state word punct"].sets == [(P + "Wd", "Text", "Coming soon...")], "state_word punctuated text")
    raises(lambda: UI.state_word(None, "x", "warning"), ValueError, "state_word kind (the 32 px warning is not one)")
    raises(lambda: UI.state_word(None, "Soon, maybe"), ValueError, "state_word punctuated text needs an id")
    fc = samples["k14 item frame cover"]
    check(fc == ('Group #SkyyTIfc { Anchor: (Width: 68, Height: 68); Background: #1a2530; Padding: (Full: 2); ItemIcon { Anchor: (Width: '
                 '64, Height: 64); ItemId: "Food_Bread"; } Group #SkyyTIfcOut { Anchor: (Full: 0); Background: #0a0e12(0.75); } }'),
          "item_frame(item=, cover=True): inline ItemId + the sold-out cover")
    check(UI.item_frame(P + "F", icon_id=P + "FI") == UI.item_frame(P + "F", icon_id=P + "FI", item=None), "item_frame: old call unchanged")
    st = samples["k14 icon cell static"]
    check(st.startswith("Group #SkyyTIcs14 { Anchor: (Width: 74, Height: 74); Background: #101925(0.55); ItemIcon") and "ButtonStyle" not in st
          and "Sounds" not in st and 'Text: "12"' in st, "icon_cell static = a Group, the static row colour, no style / sound")
    check("Background" not in samples["k14 icon cell static plain"].split("ItemIcon")[0], "icon_cell static plain has no back")
    # ---- confirm_view(compact) wrap / yes_on / q_col = SkyyProfiles 0.1.3 pf_row
    prof = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.3.py")
    pf_ns = {"SUI": UI, "re": re, "PF_W": 1100}
    pf_row = _func_from(prof, "pf_row", pf_ns) if os.path.isfile(prof) else None
    check(pf_row is not None, "SkyyProfiles 0.1.3 pf_row could be read (equivalence test)")
    if pf_row is not None:
        for wrap, yes_on, ask in ((False, True, True), (True, True, True), (True, False, False), (False, False, True), (True, False, True)):
            want = pf_row("SkyyTBody", "SkyyTMk", J("safe(q)"), "SkyyTYes", "SkyyTNo", "Create profile", "Back", 200, 180, yes_on=yes_on,
                          ask=ask, wrap=wrap)
            got = UI.confirm_view("SkyyTBody", "SkyyTMk", 1100 - 34, question=J("safe(q)"), yes_text="Create profile", no_text="Back",
                                  yes_w=200, no_w=180, compact=True, top=8, ids={"box": "SkyyTMk", "question": "SkyyTMkQ",
                                                                                 "yes": "SkyyTYes", "no": "SkyyTNo"},
                                  wrap=wrap, yes_on=yes_on, q_col="warning" if ask else "text")
            check(list(got) == list(want) and got.sets == want.sets and got.h == want.h,
                  "confirm_view(compact, wrap=%s, yes_on=%s, q_col=%s) = SkyyProfiles 0.1.3 pf_row" % (wrap, yes_on, ask))
    cvj = UI.confirm_view("SkyyTBody", "SkyyTCj", 900, question="Sure?", compact=True, yes_on=J("picked"))
    check(isinstance(cvj[2][1], UI.Choice) and cvj[2][1].cond == "picked", "confirm_view yes_on=J() = both looks (choose)")
    cvn = UI.confirm_view("SkyyTBody", "SkyyTCn", 900, question="Delete", yes_on=False)
    check([mk for _p, mk in cvn if isinstance(mk, str) and mk.startswith("TextButton #SkyyTCnYes")][0].count("Disabled.png") == 4,
          "confirm_view (not compact) yes_on=False")
    raises(lambda: UI.confirm_view("SkyyTBody", "SkyyTCx", 900, compact=True, yes_on="yes"), ValueError, "confirm_view yes_on type")
    # ---- list_card = the SKYY CARD (SkyyClasses 0.1.8 / SkyyProfiles 0.1.3) byte for byte
    cb_ns = _card_block()
    check(cb_ns is not None, "the SKYY CARD block could be read from tools/classes_0_1_8_patch.py (CARD_SHA ok)")
    if cb_ns is not None:
        cls_lines = [{"id": "Nm", "text": "safe(title)", "kind": "rowName", "h": 24, "col": J("@PKG@.ClassDefs.COLORS[i]", "#8fd67a")},
                     {"id": "Sk", "text": 'safe("Combat skill " + x)', "kind": "fieldLabel", "h": 20, "col": "value"},
                     {"id": "Ds", "text": "safe(d)", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
        tw = cb_ns["card_text_w"](1058, 3)
        pf_lines = [{"id": "Nm", "text": "safe(title)", "kind": "rowName", "h": 24, "col": J("c[3]", "#8fd67a"),
                     "tag": {"id": "Rl", "text": "safe(role)", "col": J("c[3]", "#8fd67a"), "w": tw // 2, "kind": "default"}},
                    {"id": "Sk", "text": "safe(sk)", "kind": "fieldLabel", "h": 20, "col": "value"},
                    {"id": "Ds", "text": "safe(c[2])", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
        new_lines = [{"id": "Tx", "text": 'safe("Empty slot (" + n + " free)")', "kind": "default", "h": 44, "col": "text", "wrap": True}]
        i = J("i")
        cases = [
            ("classes", {"list": "SkyyTList", "card": "SkyyTCard" + i, "icons": "SkyyTIco" + i, "text": "SkyyTTxt" + i, "act": "SkyyTAct" + i},
             1058, [("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"], cls_lines,
             dict(icons="ic", icon_item=J("safe(ic[k])", "Weapon_Sword_Iron"), icon_max=4, on="on")),
            ("profiles list", {"list": "SkyyTList", "card": "SkyyTCard" + J("id", "1"), "text": "SkyyTTx" + J("id", "1"),
                               "act": "SkyyTAc" + J("id", "1")}, 1058, [("selected", "on"), ("pending", "pend"), "normal"],
             [dict(cls_lines[0], col=J('on ? "#39f493" : "#d6e4ee"', "#39f493")), cls_lines[1], dict(cls_lines[2], h=20, wrap=False)],
             dict(icon_item=J("safe(iconOf(cls))", "Weapon_Sword_Iron"), icon_max=1)),
            ("profiles new", {"list": "SkyyTList", "card": "SkyyTNewCard", "text": "SkyyTNewTxt", "act": "SkyyTNewAct"}, 1058, "empty",
             new_lines, dict(icon_item=J("NEW_ICON", "Weapon_Sword_Iron"), icon_max=1, var="newCard")),
            ("profiles create", {"list": "SkyyTList", "card": "SkyyTCls" + i, "icons": "SkyyTIco" + i, "text": "SkyyTCTx" + i,
                                 "act": "SkyyTCAct" + i}, 1058, [("selected", "sel"), ("normal", "on"), "off"], pf_lines,
             dict(icons="ic", icon_item=J("safe(ic[k])", "Weapon_Sword_Iron"), icon_max=3, on="on")),
            ("static off", {"list": "SkyyTList", "card": "SkyyTOff", "text": "SkyyTOffT", "act": "SkyyTOffA"}, 900, "off",
             [cls_lines[1]], dict(icon_item="Weapon_Sword_Iron", on="false"))]
        for name, ids, w, look, lines, kw in cases:
            want = cb_ns["card_java"](ids, w, look, lines, **kw)
            klines = [dict(ln, text=J(ln["text"]), tag=dict(ln["tag"], text=J(ln["tag"]["text"])) if ln.get("tag") else None) for ln in lines]
            for ln in klines:
                if ln["tag"] is None:
                    del ln["tag"]
            card = UI.list_card(ids["list"], ids["card"], w, klines, look=look,
                                ids={"icons": ids.get("icons"), "text": ids["text"], "act": ids["act"]}, **kw)
            got = card.java("b")
            check(got == want, "list_card = the SKYY CARD card_java (%s)%s" % (name, "" if got == want else ": " +
                                                                               next(("%r != %r" % (a, b_) for a, b_ in zip(got.split("\n"), want.split("\n")) if a != b_), "length")))
            chk = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK), ("SkyyTBody", UI.list_well("SkyyTList", h=400))])
            chk.extend(card)
            try:
                chk.check(P)
                check(True, "list_card %s check_page" % name)
            except ValueError as e:
                FAILS.append("list_card %s: %s" % (name, e))
            check(card.h == 88 and card.act == ids["act"], "list_card .h / ids (%s)" % name)
        check(UI.state_word(None, "Coming later", "disabled") == cb_ns["card_state"]("Coming later", "disabled") and
              UI.list_card_button("SkyyTPk", "Choose", "primary") == cb_ns["card_button"]("SkyyTPk", "Choose", "primary") and
              UI.list_well("SkyyTList", h=UI.list_card_h(7)) == cb_ns["card_list"]("SkyyTList", cb_ns["card_list_h"](7)) and
              UI.list_card_text_w(1058, 3) == cb_ns["card_text_w"](1058, 3) and UI.LIST_CARD_LOOKS == cb_ns["CARD_LOOKS"] and
              (UI.LIST_CARD_H, UI.LIST_CARD_GAP, UI.LIST_CARD_BAR, UI.LIST_CARD_FRAME, UI.LIST_CARD_ACT_W) ==
              (cb_ns["CARD_H"], cb_ns["CARD_GAP"], cb_ns["CARD_BAR"], cb_ns["CARD_FRAME"], cb_ns["CARD_ACT_W"]),
              "state_word / list_card_button / list_well / list_card_h / text width / looks = the SKYY CARD helpers")
    lc = UI.list_card("SkyyTList", "SkyyTLc", 900, [{"id": "Nm", "text": "Warrior, level 3", "kind": "rowName", "h": 24, "col": "rowName"}],
                      look="normal", icon_item="Weapon_Sword_Iron", action=UI.state_word(None, "Active", "success"))
    check(lc.sets == [("SkyyTLcNm", "Text", "Warrior, level 3")] and lc[-1] == ("SkyyTLcAct", UI.state_word(None, "Active", "success"))
          and "String cardBg" not in lc.java(), "list_card: a static look, a punctuated text, action= appended")
    raises(lambda: UI.list_card("SkyyTList", "SkyyTLc", 400, []), ValueError, "list_card too narrow")
    raises(lambda: UI.list_card("SkyyTList", "SkyyTLc", 900, [], look="glowing"), ValueError, "list_card look name")
    raises(lambda: UI.list_card("SkyyTList", "SkyyTLc", 900, [], icons="a; b"), ValueError, "list_card icons expression")
    # ---- text width (the client's font tables) + the fit warnings
    fonts = UI.font_table("Default", True) is not None
    if fonts:
        check(abs(UI.text_width("WITHDRAW ALL", 17, True) - 141.9) < 0.2 and abs(UI.line_height(16) - 21.824) < 0.01,
              "text_width: WITHDRAW ALL at 17 px bold = 142 px (the SkyyBank 0.1.4 harness), Nunito line height 1.364")
        check(UI.text_width("Mage", 15, font="Secondary") > UI.text_width("Mage", 15), "the Secondary (Lexend) table is wider")
    else:
        print("note: client font tables not found - text_width uses FONT_FALLBACK")
    nofont = os.path.join(SCRATCH, "no-fonts")
    fb = UI.text_width("Ab1 .", 10, font_dir=nofont)
    check(abs(fb - 10 * (0.665 + 0.512 + 0.600 + 0.260 + 0.428)) < 1e-9, "text_width falls back to the per-class averages: %s" % fb)
    check(UI.text_lines("one two three four five six", 60, 16) >= 3 and UI.text_lines("one", 10, 16) == 1, "text_lines wraps greedily")
    raises(lambda: UI.text_width(J("x"), 16), ValueError, "text_width refuses a J() text")
    raises(lambda: UI.font_table("Comic"), ValueError, "font_table refuses a non-vanilla font")
    UI.fit_warnings(clear=True)
    UI.button(P + "W1", "Reforge everything now", "primary", w=150)
    UI.button(P + "W2", "Reforge everything now", "primary", w=150, fit=False)
    UI.button(P + "W3", "Go", w=172)
    UI.button(P + "W4", "Reforge everything now", flex=1)
    UI.label(P + "W5", "A long line that cannot fit", "default", w=60)
    UI.label(P + "W6", "A long line that cannot fit", "default", w=60, wrap=True)
    UI.label(P + "W7", "Short", "default", w=200)
    wa = UI.Appends()
    wa.text("SkyyTBody", P + "W8", "Costs 1,250,000,000 coins per day.", "caption", w=80)
    wa.text("SkyyTBody", P + "W9", J("x"), "caption", w=10)
    w = UI.fit_warnings()
    check(len(w) == 3 and w[0].startswith("button #SkyyTW1 'Reforge everything now'") and w[1].startswith("label #SkyyTW5")
          and w[2].startswith("label #SkyyTW8"), "fit warnings: only the too-wide static texts (fit=False, flex, wrap, J() skipped): %s" % w)
    UI.button(P + "W1", "Reforge everything now", "primary", w=150)
    check(len(UI.fit_warnings()) == 3, "a fit warning is given once")
    UI.fit_warnings("off", clear=True)
    UI.button(P + "W1", "Reforge everything now", "primary", w=150)
    check(UI.fit_warnings() == [], "fit_warnings('off')")
    UI.fit_warnings("collect")
    raises(lambda: UI.fit_warnings("loud"), ValueError, "fit_warnings mode")
    # ---- Appends.button (b.set on a TextButton Text, UNVERIFIED)
    ab = UI.Appends([(None, ROOT_MK), ("SkyyTA", BODY_MK)])
    check(ab.button("SkyyTBody", P + "Ab1", "Buy", "primary") == P + "Ab1" and not ab.sets and 'Text: "Buy"' in ab[-1][1],
          "Appends.button: proven text inline, no gate")
    raises(lambda: ab.button("SkyyTBody", P + "Ab2", "Buy 3?"), UI.UnverifiedError, "Appends.button b.set text needs trial=True",
           "UNVERIFIED")
    ab.button("SkyyTBody", P + "Ab3", "Buy 1,250 coins?", "primary", trial=True, w=300)
    check(ab.sets == [(P + "Ab3", "Text", "Buy 1,250 coins?")] and 'Text: ""' in ab[-1][1], "Appends.button b.set path")
    # ---- assert_proven: one table, minus PROBED
    for name, mk in samples.items():
        if name.startswith("k14 ") and "runtime" not in name:
            try:
                UI.assert_proven(mk)
                check(True, "assert_proven: kit 1.4 sample %s uses proven properties only" % name)
            except UI.UnprovenError as e:
                FAILS.append("kit 1.4 sample %s is not proven-only: %s" % (name, e))
    base4 = UI.probe_page("base4")
    found = UI.assert_proven(base4.shell.appends, what="probe base4")
    check("FlexWeight" not in found and "WrapMaxLines" not in found and not any(k.startswith("LayoutMode: ") and found[k] for k in found),
          "probe base4 is proven-only (no FlexWeight / WrapMaxLines / LayoutMode Center-Right-Full)")
    raises(lambda: UI.assert_proven(UI.button(P + "A", "x", flex=1)), UI.UnprovenError, "assert_proven refuses FlexWeight", "FlexWeight")
    check("FlexWeight" in UI.assert_proven(UI.button(P + "A", "x", flex=1), allow=("flex-rows",)), "assert_proven allow=")
    UI.PROBED.add("base")
    try:
        check(bool(UI.assert_proven([UI.button_row(P + "Br", align="right"), UI.label(P + "A", "", "heading")])),
              "a PROBED base proves LayoutMode Right + WrapMaxLines")
    finally:
        UI.PROBED.discard("base")
    for mk, what in ((UI.button(P + "A", "x", disable_element=True, trial=True), "Disabled: true"),
                     (UI.quality_frame(P + "Q", "Rare", trial=True), "../ItemQualities"), (UI.tile(P + "T", trial=True), "tile"),
                     (UI.checkbox(P + "C", trial=True), "CheckBox"), (UI.tooltip("Hi", trial=True), "TooltipText"),
                     ('Group #SkyyTA { Alignment: Center; }', "not in the kit's property table")):
        raises(lambda mk=mk: UI.assert_proven(mk), UI.UnprovenError, "assert_proven catches %s" % what, what)
    check(UI.assert_proven(UI.Appends([(None, ROOT_MK), ("SkyyTA", UI.choose("c", UI.label(P + "L", ""), UI.label(P + "L", "", "caption")))]))
          is not None, "assert_proven takes Appends with choices")
    every = {}
    for pg in UI.probe_pages():
        every.update(UI.proven_tokens(pg.shell.appends))
    every.update(UI.proven_tokens(list(samples.values())))
    check(not [k for k, g in every.items() if g == "unknown"], "every element / key the kit emits is in the proven table: %s"
          % sorted(k for k, g in every.items() if g == "unknown"))
    # the PROVEN entries are really on deployed pages: each one appears in a live build script (tools/deploy_set.py SET, the probe mod
    # itself not counted)
    live = _live_scripts()
    check(len(live) >= 15, "live build scripts found: %d" % len(live))
    if live:
        blob = "\n".join(live.values())
        for k, g in sorted(UI.PROVEN_KEYS.items()):
            if g is None:
                check(re.search(r"(?<![A-Za-z])%s\s*:" % k, blob) is not None, "proven key %s appears in a live build script" % k)
        for e, g in sorted(UI.PROVEN_ELEMENTS.items()):
            if g is None:
                check(re.search(r"(?<![A-Za-z])%s\s*[#{]" % e, blob) is not None, "proven element %s appears in a live build script" % e)
        for v, g in sorted(UI.PROVEN_LAYOUTS.items()):
            if g is None:
                check(re.search(r"LayoutMode:\s*%s\b" % v, blob) is not None, "proven LayoutMode %s appears in a live build script" % v)
        for k in ("FlexWeight", "WrapMaxLines", "LetterSpacing"):
            check(re.search(r"(?<![A-Za-z])%s\s*:" % k, blob) is None, "base-gated %s is on no live page (still behind the probe)" % k)
    # ---- probe pages 19-22 + Probe.summary + Probe.with_footer (the public footer hook) + PROBE_OPEN_FIRST
    pages = UI.probe_pages()
    check(UI.PROBE_OPEN_FIRST == ("base1", "base2", "base3", "base4") and all(len(p.summary) <= 95 and p.summary for p in pages),
          "PROBE_OPEN_FIRST; every probe page has a short summary")
    check(pages[0].summary.startswith("Window frame") and UI.probe_page("base4").n == 19 and UI.probe_page(22).name == "layout-right",
          "summaries / page numbers 19-22")

    def footer(cont):
        return [(cont, "Group #SkyyPbNav { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }"),
                ("SkyyPbNav", UI.button("SkyyPbNavBack", "Back", w=240, h=46)), ("SkyyPbNav", UI.button("SkyyPbNavClose", "Close", w=170, h=46))]
    views = {}
    for pg in pages:
        try:
            views[pg.n] = pg.with_footer(footer, 56, foot_w=426, prefix="SkyyPb")
            check(views[pg.n].h <= UI.MAX_PAGE_H, "probe %d with a footer fits 1080" % pg.n)
        except ValueError as e:
            FAILS.append("probe %d with_footer: %s" % (pg.n, e))
        body_used = UI.used_height(pg.shell.appends, pg.shell.body)
        check(body_used <= pg.shell.inner_h, "probe %d body children fit (%d of %d px)" % (pg.n, body_used, pg.shell.inner_h))
    if len(views) == len(pages):
        check(views[1].h == 920 and views[16].h == 346 and views[18].container == "SkyyPb18Main" and views[18].h == 960
              and views[19].container == "SkyyPb19Body" and views[19].h == 647 + 60,
              "with_footer places the footer like SkyyUiProbe 0.1 (base1 860 -> 920, page 16 290 -> 346, base3 in its main column)")
        v18 = views[18]
        check(sum(1 for ln in v18.java("b").splitlines() if "SkyyPbNav" in ln) == 3 and "pbGridSlots" in v18.java("b") and
              v18.java("b").startswith(pages[17].shell.java("b").split("\n")[0][:40]), "with_footer Java: page + footer + java_extra")
        check(pages[0].shell.appends[0][1] == 'Group #SkyyPb1 { Anchor: (Width: 1500, Height: 860); }',
              "with_footer never changes the kit's own page (a copy)")
    UI.fit_warnings("print", clear=True)


def _live_scripts():
    """{mod: text} of the live build scripts (tools/deploy_set.py SET, read-only; SkyyUiProbe excluded)."""
    path = os.path.join(HERE, "deploy_set.py")
    if not os.path.isfile(path):
        return {}
    m = re.search(r"^SET = \[(.*?)^\]", open(path, encoding="utf8").read(), re.S | re.M)
    out = {}
    for mod, ver in re.findall(r'\("(Skyy\w+)", "([\d.]+)"\)', m.group(1) if m else ""):
        p = os.path.join(ROOT, mod, "build_%s_%s.py" % (mod.lower(), ver))
        if mod != "SkyyUiProbe" and os.path.isfile(p):
            out[mod] = open(p, encoding="utf8", errors="replace").read()
    return out


# ================================================================= probe pages (the in-game gate)
PROBE_NAMES13 = ["base1", "base2", "checkbox", "number-field", "tooltip", "progress-element", "memories-bar", "quality-frame",
                 "itemslot", "dropdown", "search-field", "spinner", "tile", "text-mask", "slot-background", "disabled-prop", "value-ref",
                 "base3"]
PROBE_NAMES = PROBE_NAMES13 + ["base4", "button-text", "flex-rows", "layout-right"]      # kit 1.4 appends 19-22


def phase_probes():
    pages = UI.probe_pages()
    keys = [p.key for p in pages]
    check([p.n for p in pages] == list(range(1, len(pages) + 1)), "probe pages are numbered 1..n")
    check([p.name for p in pages] == PROBE_NAMES, "probe pages keep their stable names: %s" % [p.name for p in pages])
    check([p.name for p in pages][:18] == PROBE_NAMES13, "kit 1.4: probe pages 1-18 keep their numbers and names (SkyyUiProbe 0.1)")
    check(tuple(p.name for p in pages if p.key == "base") == UI.PROBE_BASE and [p.n for p in pages if p.key == "base"] == [1, 2, 18],
          "the base pages are base1 / base2 / base3 = 1, 2, 18")
    check(keys[:2] == ["base", "base"], "probe pages 1-2 are the base look")
    check(set(keys) == set(UI.UNVERIFIED), "every UNVERIFIED feature has a probe page (missing: %s, extra: %s)"
          % (sorted(set(UI.UNVERIFIED) - set(keys)), sorted(set(keys) - set(UI.UNVERIFIED))))
    feats = [k for k in keys if k != "base"]
    check(len(set(feats)) == len(feats) == len(UI.UNVERIFIED) - 1, "one probe page per UNVERIFIED feature")
    check(all(p.name == p.key for p in pages if p.key != "base"), "a feature page's name is its UNVERIFIED key")
    check(UI.probe_page("checkbox").n == 3 and UI.probe_page(18).name == "base3" and UI.probe_page("base1").n == 1,
          "probe_page by name or number")
    raises(lambda: UI.probe_page("nope"), KeyError, "probe_page refuses an unknown name")
    for pg in pages:
        check(pg.shell.h <= UI.MAX_PAGE_H and pg.look and pg.look[0].startswith("the page opens"), "probe %d fits 1080 and says what to see"
              % pg.n)
        check(all(len(x) <= 190 for x in pg.look), "probe %d look lines are short" % pg.n)
        try:
            pg.check()
            check(True, "probe %d check_page" % pg.n)
        except ValueError as e:
            FAILS.append("probe %d: %s" % (pg.n, e))
        for i, (par, mk) in enumerate(pg.shell.appends):
            for j, v in enumerate(UI._variants(mk)):        # kit 1.4: probe 19 has runtime choices (both looks are checked)
                markup_ok("probe %d append %d.%d" % (pg.n, i, j), v, root=(par is None), prefix=pg.shell.prefix)
        # the page shows its own numbered "what to see" list: a section head + one b.set line per look line
        P_ = pg.shell.prefix
        sets = pg.shell.all_sets()
        shown = [v for i, pr, v in sets if i.startswith(P_ + "Look") and pr == "Text"]
        want = ["%d. %s" % (k + 1, x[:1].upper() + x[1:]) for k, x in enumerate(pg.look)]
        check(shown == want, "probe %d shows its numbered look list on the page" % pg.n)
        heads = [mk for _p, mk in pg.shell.appends if isinstance(mk, str) and mk.startswith("Label #%sLookH " % P_)]
        check(len(heads) == 1 and ('Text: "Probe %s - what to see"' % pg.name) in heads[0], "probe %d look list head names %s"
              % (pg.n, pg.name))
        js = pg.java("b")
        check(js.count("appendInline") == len(pg.shell.appends) and not lint_java_line(js), "probe %d Java" % pg.n)
        check(UI.item_grid_java_is_safe(js), "probe %d Java never puts a raw stack in a grid slot" % pg.n)
    base_pages = [pg for pg in pages if pg.key == "base"]
    base = "\n".join(UI.render(v) for pg in base_pages for _p, mk in pg.shell.appends for v in UI._variants(mk))
    for feat in ("FlexWeight", "LayoutMode: Right", "LayoutMode: Full", "LetterSpacing: 0.5", "WrapMaxLines", "ShrinkTextToFit",
                 "Disabled: (", "Sounds: (", "ContainerDecorationTop", "Top: -8, Right: -8", "#000000(0.15)", "Tertiary_Active",
                 "ContainerHeaderNoRunes", "Top: -2", "ItemGrid #SkyyPb18Grid", "Button #SkyyPb18C0", "#SkyyPb18CfYes",
                 "#SkyyPb18PgPrev", "#0a0e12(0.75)", "#7a9cc6(0.25)", 'Text: "Page 2 / 5"'):
        check(feat in base, "base probe pages cover %s" % feat)
    p18 = UI.probe_page("base3")
    check(any(v == "Costs 1,250 coins (50% off) - shown exactly as written." for _i, _pr, v in p18.shell.all_sets()),
          "base3 shows a punctuated text through Appends.text")
    check("pbGridSlots" in p18.java("b") and "pbGridSlots" not in p18.java("b", extra=False), "base3 fills its grid in java_extra")
    return pages


# ================================================================= the style guide names only real kit functions
def phase_guide():
    path = os.path.join(ROOT, "research", "Vanilla-UI-Style-Guide.md")
    text = open(path, encoding="utf-8").read()
    # fenced code blocks (worked examples: patch-script code with rep(), open(), ...) are checked for SUI.<name> only
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    check(prose.count("```") == 0 and text.count("```") % 2 == 0, "the guide's code fences are balanced")
    names = set(re.findall(r"SUI\.([A-Za-z_][A-Za-z0-9_]*)", text)) | set(re.findall(r"`([a-z_][a-z0-9_]*)\(", prose))
    names |= set(n for cell in re.findall(r"`([^`|]*)`", prose) for n in re.findall(r"(?<![.\w])([a-z_][a-z0-9_]*)\(", cell))
    names -= {"list", "set", "dict", "tuple", "sorted"}         # Python builtins / the Java set(String, ...) overloads the guide cites
    check(len(names) >= 40, "the guide names the kit functions (%d found)" % len(names))
    for n in sorted(names):
        check(hasattr(UI, n), "the style guide names SUI.%s, which the kit does not have" % n)
    for n in ("pager", "item_grid", "java_grid_methods", "java_grid_fill", "icon_cell", "confirm_view", "choose", "probe_page",
              "for_pysource", "for_fstring"):
        check(n in names, "the guide documents the kit 1.3 function %s" % n)
    for n in ("static_row", "status_bar", "list_well", "result_line", "java_color_by_text", "stat_bar", "column_spec", "column_heads",
              "column_row", "right_margin", "centre_margin", "button_row", "stat_well", "list_card", "list_card_h", "list_card_button",
              "state_word", "color_by", "used_height", "used_width", "outer_size", "text_width", "text_lines", "line_height",
              "assert_proven", "java_add", "fit_warnings"):
        check(n in names, "the guide documents the kit 1.4 function %s" % n)
    for n in ("Markup", "ap.add(", "ap.button(", "with_footer", "PROBE_OPEN_FIRST", "PROBE_SUMMARY", "SNAP13", "base4", "button-text",
              "flex-rows", "layout-right", "## 12. Kit 1.4 blocks", "## 13. Recipe: restyle a LIST page", "## 14. Recipe: restyle a CARD page"):
        check(n in text, "the guide mentions %s (kit 1.4)" % n)
    # the two recipes' code runs as written (the card recipe gets a page shell)
    for sec in ("## 13.", "## 14."):
        m = re.search(r"```python\n(.*?)```", text[text.index(sec):], re.S) if sec in text else None
        if m is None:
            FAILS.append("guide section %s has no python block" % sec)
            continue
        ns = {"SUI": UI}
        if sec == "## 14.":
            ns["sh"] = UI.page_shell("SkyyXF", 1100, 900, "Classes", body_id="SkyyX")
        try:
            exec(compile(m.group(1), "<guide %s>" % sec, "exec"), ns)
            check(any(k.endswith("JAVA") for k in ns), "guide recipe %s runs and emits its Java" % sec)
        except Exception as e:      # noqa
            FAILS.append("guide recipe %s does not run: %s: %s" % (sec, type(e).__name__, e))
    check("@@" in text and "Appends.text" in text and "STATUS_INFO" in text, "the guide documents @@TOKEN@@ patches, Appends.text, STATUS_INFO")
    check("import skyyui as SUI" in text and "import skyyui as UI" not in text, "the guide imports the kit as SUI")
    for k in UI.LABELS:
        check(k in text, "the guide lists the label kind %s" % k)


# ================================================================= the lint rules (tools/ci/lint.py kit warnings, WARN only)
def phase_lint():
    path = os.path.join(HERE, "ci", "lint.py")
    text = open(path, encoding="utf-8").read()
    want = {"_Unres", "_Stub", "_STUB", "_lev", "_kit_lev", "_kit_strs", "_kit_code_lines", "KIT_IMPORT_RE", "KIT_HEX_RE",
            "KIT_PY_COMMENT_RE", "KIT_MAX_WARNS", "KIT_PATH_RE", "KIT_FONT_RE", "kit_color_warnings", "kit_style_warnings",
            "GRID_SLOT_NEW_RE", "grid_slot_warnings"}
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
    # the grid-slot metadata rule (WARN, every newest build script)
    if "grid_slot_warnings" not in ns:
        FAILS.append("lint.py has no grid_slot_warnings rule")
        return
    grid_script = "\n".join([
        'M(page, r"""slots.add(new @IGS@(st));""")',                                                  # a held stack -> WARN
        'M(page, r"""slots.add(new @IGS@(new @IS@(st.getItemId(), st.getQuantity())));""")',          # fresh copy
        'M(page, r"""empty.add(new @IGS@());""")',                                                    # empty slot
        'X = f"""gs = new {IGS}(new {IS}(id, 1));"""',                                                # f-string tokens
        'Y = "g = new com.hypixel.hytale.server.core.ui.ItemGridSlot(stack.copy());"',                # FQN, a held stack -> WARN
        'Z = "g = new ItemGridSlot( new ItemStack(id, 2));"',                                         # plain names, fresh
        'assert ("new " + "ItemGridSlot") not in _src',                                               # a guard, not a slot
    ] + UI.java_grid_methods() + [UI.java_grid_fill("SkyyTGrid", [("Food_Bread", 1), None])])
    w = ns["grid_slot_warnings"]("SkyyX/build_skyyx_0.1.py", grid_script)
    check(len(w) == 2 and w[0].startswith("SkyyX/build_skyyx_0.1.py:1 ") and w[1].startswith("SkyyX/build_skyyx_0.1.py:5 "),
          "lint grid-slot rule flags only slots built from a held stack (the kit's grid Java passes): %s" % w)
    live = []
    for f_ in sorted(os.listdir(ROOT)):
        d_ = os.path.join(ROOT, f_)
        if f_.startswith("Skyy") and os.path.isdir(d_):
            vs = [x for x in os.listdir(d_) if re.match(r"build_skyy[a-z]+_\d+(?:\.\d+)*\.py$", x)]
            if vs:
                newest = max(vs, key=lambda x: tuple(int(p_) for p_ in re.findall(r"\d+", x.rsplit("_", 1)[1])))
                live += ns["grid_slot_warnings"](f_ + "/" + newest, open(os.path.join(d_, newest), encoding="utf8", errors="replace").read())
    check(not live, "no newest build script trips the grid-slot rule: %s" % live[:3])
    old_ah = os.path.join(ROOT, "SkyyAuctions", "build_skyyauctions_0.1.py")
    if os.path.isfile(old_ah):
        check(len(ns["grid_slot_warnings"]("x", open(old_ah, encoding="utf8", errors="replace").read())) == 1,
              "the grid-slot rule catches the SkyyAuctions 0.1 bug (new @IGS@(st))")


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
    # ---- kit 1.3: runtime choices (pager / icon cells), confirm_view, Appends.text, the grid Java, the patch-script templates
    bc.addMethod(CtNewMethod.make('public void set(String k, java.util.List v) { this.sb.append("set ").append(k).append("=L")'
                                  '.append(v.size()).append("\\n"); }', bc))
    pgj = UI.pager(P + "Body", P + "Pj", 900, text=UI.J("pageText", "Page 1 / 5"), prev_on=UI.J("pageNo > 0"),
                   next_on=UI.J("pageNo < pages - 1"))
    uc.addMethod(CtNewMethod.make("public static String pagerJ(int pageNo, int pages, String pageText) { skyyuitest.B b = new "
                                  "skyyuitest.B();\n%s\nreturn b.out(); }" % pgj.java("b"), uc))
    cvj = UI.confirm_view(P + "Body", P + "Cv", 900, question=UI.J("q", "Sure"), message="You get 1,250 coins.", note="Costs 5 coins")
    uc.addMethod(CtNewMethod.make("public static String cview(String q) { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                  % cvj.java("b"), uc))
    cell_ch = UI.choose(UI.J("i == sel"), UI.icon_cell(P + "Cell" + UI.J("i", "0"), UI.J("ids[i]", "Weapon_Sword_Iron"), state="selected",
                                                       qty=True),
                        UI.icon_cell(P + "Cell" + UI.J("i", "0"), UI.J("ids[i]", "Weapon_Sword_Iron"), qty=True))
    cell_stmts = "\n".join(["  " + UI.java_append(P + "Cells", cell_ch),
                            "  " + UI.java_set(P + "Cell" + UI.J("i", "0") + "Qty", "Text", UI.J("String.valueOf(qs[i])", "1"))])
    uc.addMethod(CtNewMethod.make("public static String cells(String[] ids, int[] qs, int sel) { skyyuitest.B b = new skyyuitest.B();\n"
                                  "for (int i = 0; i < ids.length; i++) {\n%s\n}\nreturn b.out(); }" % cell_stmts, uc))
    # the patch-script templates (style guide section 8): kit Java pasted into real Python templates, run, then compiled
    tmpl_mk = [samples["button primary normal"], samples["label text"], samples["item grid kit"]]
    tmpl_java = "\n".join([UI.java_append(P + "Body", mk) for mk in tmpl_mk]
                          + [UI.java_set(P + "Lt", "Text", 'back\\slash "q" {brace} 50% \\n')])
    tmpl_sets = [(P + "Lt", "Text", 'back\\slash "q" {brace} 50% \\n')]
    gens = {
        "non-raw f-string (for_pysource)": 'PKG = "skyyuitest"\nJAVA = f"""// {PKG}\n' + UI.for_pysource(tmpl_java) + '\n"""\n',
        "raw string (for_pysource raw, no f)": 'JAVA = r"""// skyyuitest\n' + UI.for_pysource(tmpl_java, raw=True, fstring=False) + '\n"""\n',
        "raw f-string (for_pysource raw)": 'PKG = "skyyuitest"\nJAVA = rf"""// {PKG}\n' + UI.for_pysource(tmpl_java, raw=True) + '\n"""\n',
        "@@TOKEN@@ replace + f-string": ('X = 1\n@@BODY@@\nY = 2\n').replace(
            "@@BODY@@", 'PKG = "skyyuitest"\nJAVA = f"""// {PKG}\n' + UI.for_pysource(tmpl_java) + '\n"""'),
        "build-time interpolation {LIT}": None,
    }
    tmpl_src = {}
    for k, gen in gens.items():
        if gen is None:
            continue
        ns = {}
        exec(compile(gen, "<generated %s>" % k, "exec"), ns)
        tmpl_src[k] = ns["JAVA"]
    tmpl_src[".format template (for_fstring)"] = ("// {pkg}\n" + UI.for_fstring(tmpl_java)).format(pkg="skyyuitest")
    tmpl_src["% template (for_percent)"] = ("// %s\n" + UI.for_percent(tmpl_java)) % "skyyuitest"
    ns = {"LIT0": UI.java_lit(tmpl_mk[0]), "LIT1": UI.java_lit(tmpl_mk[1]), "LIT2": UI.java_lit(tmpl_mk[2]),
          "SETV": UI.java_lit(tmpl_sets[0][2])}
    exec(compile(r'JAVA = f"""// skyyuitest' + "\n" + r'b.appendInline("#SkyyTBody", {LIT0});' + "\n" + r'b.appendInline("#SkyyTBody", {LIT1});'
                 + "\n" + r'b.appendInline("#SkyyTBody", {LIT2});' + "\n" + r'b.set("#SkyyTLt.Text", {SETV});"""' + "\n",
                 "<generated build-time interpolation>", "exec"), ns)
    tmpl_src["build-time interpolation {LIT}"] = ns["JAVA"]
    tmpl_names = sorted(tmpl_src)
    for i, k in enumerate(tmpl_names):
        check(tmpl_src[k].startswith("// skyyuitest\n"), "template %s still interpolates its own placeholder" % k)
        check(tmpl_src[k].split("\n", 1)[1].rstrip("\n") == tmpl_java, "template %s gives back the kit Java exactly" % k)
        uc.addMethod(CtNewMethod.make("public static String tmpl%d() { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                      % (i, tmpl_src[k]), uc))
    # grid slots: the kit's grid Java against stub ItemStack / ItemGridSlot classes that record what they were given
    isc = pool.makeClass("skyyuitest.IS")
    for f in ("public String id;", "public int qty;", "public String meta;"):
        isc.addField(CtField.make(f, isc))
    isc.addConstructor(CtNewConstructor.make("public IS(String id, int qty) { this.id = id; this.qty = qty; this.meta = null; }", isc))
    isc.addMethod(CtNewMethod.make("public boolean isEmpty() { return this.id == null || this.qty <= 0; }", isc))
    isc.addMethod(CtNewMethod.make("public String getItemId() { return this.id; }", isc))
    isc.addMethod(CtNewMethod.make("public int getQuantity() { return this.qty; }", isc))
    igc = pool.makeClass("skyyuitest.IGS")
    igc.addField(CtField.make("public skyyuitest.IS stack;", igc))
    igc.addConstructor(CtNewConstructor.make("public IGS() { this.stack = null; }", igc))
    igc.addConstructor(CtNewConstructor.make("public IGS(skyyuitest.IS s) { this.stack = s; }", igc))
    gc = pool.makeClass("skyyuitest.Grid")
    grid_src = UI.java_grid_methods("grid", "skyyuitest.IGS", "skyyuitest.IS")
    for src in grid_src:
        gc.addMethod(CtNewMethod.make(src, gc))
    gc.addMethod(CtNewMethod.make(
        "public static String d(skyyuitest.IGS g) { if (g == null) return \"null\"; if (g.stack == null) return \"empty\"; "
        "return g.stack.id + \"x\" + String.valueOf(g.stack.qty) + (g.stack.meta == null ? \"\" : \"+META\"); }", gc))
    gc.addMethod(CtNewMethod.make(
        "public static String run() {\n  skyyuitest.IS held = new skyyuitest.IS(\"Weapon_Sword_Iron\", 3); held.meta = \"rolled\";\n"
        "  skyyuitest.IGS g = gridSlotOf(held);\n"
        "  String r = d(g) + \"|\" + String.valueOf(g.stack != held) + \"|\" + d(gridSlotOf(null)) + \"|\" + d(gridSlot(\" \", 5)) + \"|\" "
        "+ d(gridSlot(\"Food_Bread\", 0)) + \"|\";\n"
        "  java.util.ArrayList l = gridSlots(new String[] { \"Food_Bread\", null, \"Ingredient_Bar_Iron\" }, new int[] { 2 }, 4);\n"
        "  for (int i = 0; i < l.size(); i++) r = r + d((skyyuitest.IGS) l.get(i)) + \",\";\n"
        "  java.util.ArrayList m = gridSlotsOf(new skyyuitest.IS[] { held, null }, 3);\n"
        "  for (int i = 0; i < m.size(); i++) r = r + d((skyyuitest.IGS) m.get(i)) + \";\";\n  return r;\n}", gc))
    fill_java = UI.java_grid_fill(P + "Grid", [("Weapon_Sword_Iron", 1), None, (UI.J("ids[0]", "Food_Bread"), UI.J("qs[0]", "2"))],
                                  var="gs", igs="skyyuitest.IGS", stack="skyyuitest.IS")
    gc.addMethod(CtNewMethod.make("public static String fill(String[] ids, int[] qs) { skyyuitest.B b = new skyyuitest.B();\n%s\n"
                                  "return b.out(); }" % fill_java, gc))
    check(all(UI.item_grid_java_is_safe(s_, "skyyuitest.IGS", "skyyuitest.IS") for s_ in grid_src + [fill_java]),
          "the stub grid Java never passes a raw stack")
    isc.writeFile(out)
    igc.writeFile(out)
    gc.writeFile(out)
    # the real classes (HytaleServer.jar, read-only): the grid Java compiles against the engine's ItemStack / ItemGridSlot /
    # UICommandBuilder signatures (compile only - nothing is loaded or written)
    real_jar = B.SERVER_JAR
    if os.path.isfile(real_jar):
        rp = Jc("javassist.ClassPool")(False)
        rp.appendSystemPath()
        rp.appendClassPath(real_jar)
        rc = rp.makeClass("skyyuitest.RealGrid")
        try:
            for src in UI.java_grid_methods():
                rc.addMethod(CtNewMethod.make(src, rc))
            rc.addMethod(CtNewMethod.make("public static void fill(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, String[] "
                                          "ids) {\n%s\n}" % UI.java_grid_fill(P + "Grid", [("Weapon_Sword_Iron", 1), None,
                                                                                         (UI.J("ids[0]", "Food_Bread"), 3)]), rc))
            check(True, "the grid Java compiles against HytaleServer.jar (ItemStack(String, int), ItemGridSlot, UICommandBuilder.set)")
        except Exception as e:      # noqa - report the compile error as a FAIL
            FAILS.append("the grid Java does not compile against HytaleServer.jar: %s" % e)
        rc.detach()
    else:
        print("note: HytaleServer.jar not found - the grid Java was compiled against stubs only")
    # ---- kit 1.4: the Java the new blocks emit (result colour helper, runtime status bar, stat bar choice, a list card with its
    # runtime look + icon loop, a runtime right footer margin)
    k14_rules = [("startsWith", "upgraded to ", "+"), ("contains", " could not", "-"), ("equals", "done", "success"), ("endsWith", "?", "=")]
    uc.addMethod(CtNewMethod.make(UI.java_color_by_text("infoColor", k14_rules, empty="=", default="-"), uc))
    k14_row = UI.static_row(P + "Sr" + UI.J("i", "2"), 572, icon=UI.J("ids[i]", "Weapon_Sword_Iron"), name=UI.J("nm", "Steve"),
                            sub="Rare, sharp", bar=UI.J("sel"), action="Equip")
    uc.addMethod(CtNewMethod.make("public static String srow(int i, boolean sel, String nm, String[] ids) { skyyuitest.B b = new "
                                  "skyyuitest.B();\n%s\nreturn b.out(); }" % UI.java_add(P + "List", k14_row), uc))
    k14_bar = UI.stat_bar(P + "Sb", 160, 8, UI.J("f", "80"), col="progressBlue")
    uc.addMethod(CtNewMethod.make("public static String sbar(int f) { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                  % UI.java_append(P + "Box", k14_bar.choose()), uc))
    k14_card = UI.list_card(P + "List", P + "Card" + UI.J("i"), 1058, [
        {"id": "Nm", "text": UI.J('"Class " + i'), "kind": "rowName", "h": 24, "col": "rowName",
         "tag": {"id": "Tg", "text": UI.J('"role"'), "col": "rowSub", "w": 200}},
        {"id": "Ds", "text": "Two words, a comma.", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}],
        look=[("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"], icons="ic", icon_item=UI.J("ic[k]", "Weapon_Sword_Iron"),
        icon_max=3, ids={"icons": P + "Ico" + UI.J("i"), "text": P + "Txt" + UI.J("i"), "act": P + "Act" + UI.J("i")},
        action=UI.state_word(None, "Selected", "success"))
    uc.addMethod(CtNewMethod.make("public static String card(String[] ic, int i, boolean sel, boolean pend, boolean on) { skyyuitest.B b "
                                  "= new skyyuitest.B();\n%s\nreturn b.out(); }" % k14_card.java("b"), uc))
    k14_brow = UI.button_row(P + "Br", align="right", left_margin=UI.J("gapR", "722"))
    uc.addMethod(CtNewMethod.make("public static String brow(int gapR) { skyyuitest.B b = new skyyuitest.B();\n%s\nreturn b.out(); }"
                                  % UI.java_append(P + "Body", k14_brow), uc))
    if os.path.isfile(real_jar):
        rp2 = Jc("javassist.ClassPool")(False)
        rp2.appendSystemPath()
        rp2.appendClassPath(real_jar)
        rc2 = rp2.makeClass("skyyuitest.RealCard")
        try:
            rc2.addMethod(CtNewMethod.make("public static void card(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, String[] ic, "
                                           "int i, boolean sel, boolean pend, boolean on) {\n%s\n}" % k14_card.java("b"), rc2))
            rc2.addMethod(CtNewMethod.make("public static void srow(com.hypixel.hytale.server.core.ui.builder.UICommandBuilder b, int i, "
                                           "boolean sel, String nm, String[] ids) {\n%s\n}" % UI.java_add(P + "List", k14_row), rc2))
            check(True, "kit 1.4 list_card / static_row Java compiles against HytaleServer.jar's UICommandBuilder")
        except Exception as e:      # noqa
            FAILS.append("kit 1.4 Java does not compile against HytaleServer.jar: %s" % e)
        rc2.detach()
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
        check(str(getattr(U, "probe%d" % pg.n)()) == expect(pg.shell.appends, pg.shell.all_sets()),
              "probe page %d compiles and builds exactly the Python appends + its b.set lines" % pg.n)
    check(str(U.colorOf("+done")) == "#39f493" and str(U.colorOf("-no")) == "#ff6b6b" and str(U.colorOf("=x")) == "#7caacc"
          and str(U.colorOf("")) == "#96a9be" and str(U.textOf("-no")) == "no" and str(U.textOf("plain")) == "plain",
          "java_status_methods compile and answer ('=' = info blue)")
    for line in (sh.java("b") + "\n" + dl.java("cmd")).splitlines():
        check(not lint_java_line(line), "lint underscore-id rule on the shell Java line: " + line[:60])

    # ---- kit 1.3 results
    def subst(mk, vals):
        return UI._J_RE.sub(lambda m: vals.get(m.group(1), m.group(2)), mk)

    def pick(mk, truth):
        return (mk.a if truth[mk.cond] else mk.b) if isinstance(mk, UI.Choice) else mk

    for pn, pages_n in ((0, 5), (2, 5), (4, 5)):
        truth = {"pageNo > 0": pn > 0, "pageNo < pages - 1": pn < pages_n - 1}
        want = expect([(p_, pick(mk, truth)) for p_, mk in pgj], pgj.sets)
        check(str(U.pagerJ(pn, pages_n, "Page 1 / 5")) == want, "pager with runtime states compiles and picks the right looks (page %d)" % pn)
    check(str(U.cview("Sure")) == expect(cvj, cvj.sets), "confirm_view compiles: appends + its b.set lines (J question, punctuated texts)")
    ids_, qs_, sel_ = ["Weapon_Sword_Iron", "Food_Bread", "Ingredient_Bar_Iron"], [1, 12, 64], 1
    want = "".join("#%sCells|%s\nset #%sCell%dQty.Text=%d\n" % (P, subst(pick(cell_ch, {"i == sel": i == sel_}), {"i": str(i), "ids[i]": ids_[i]}),
                                                               P, i, qs_[i]) for i in range(3))
    check(str(U.cells(jpype.JArray(jpype.JString)(ids_), jpype.JArray(jpype.JInt)(qs_), sel_)) == want,
          "icon cells in a Java loop: runtime ids / items / selected state / quantity")
    for i, k in enumerate(tmpl_names):
        check(str(getattr(U, "tmpl%d" % i)()) == expect([(P + "Body", mk) for mk in tmpl_mk], tmpl_sets),
              "template %s: the pasted kit Java compiles with javassist and builds the Python markup" % k)
    G = jpype.JClass("skyyuitest.Grid", loader=loader)
    check(str(G.run()) == "Weapon_Sword_Ironx3|true|empty|empty|empty|Food_Breadx2,empty,Ingredient_Bar_Ironx1,empty,"
          "Weapon_Sword_Ironx3;empty;empty;", "grid Java: slots are fresh ItemStack(id, qty) copies (no metadata, never the held "
          "stack), blanks / zero quantities are empty slots: %s" % str(G.run()))
    check(str(G.fill(jpype.JArray(jpype.JString)(["Food_Bread"]), jpype.JArray(jpype.JInt)([2]))) == "set #SkyyTGrid.Slots=L3\n",
          "java_grid_fill compiles and sets the slot list")
    # ---- kit 1.4 results
    for t_, want_ in (("", "#7caacc"), ("upgraded to Rare", "#39f493"), ("it could not move", "#ff6b6b"), ("done", "#39f493"),
                      ("Sure?", "#7caacc"), ("something else", "#ff6b6b")):
        check(str(U.infoColor(t_)) == want_, "java_color_by_text compiles and answers %r -> %s (got %s)" % (t_, want_, U.infoColor(t_)))
    for i_, sel_, nm_ in ((0, True, "Steve"), (3, False, "Alex, the 2nd")):
        ids_ = ["Weapon_Sword_Iron", "Food_Bread", "Tool_Pickaxe_Iron", "Ingredient_Bar_Iron"]
        vals = {"i": str(i_), "ids[i]": ids_[i_], "nm": nm_, '(sel) ? "Background: #4274a5; " : ""': "Background: #4274a5; " if sel_ else ""}
        want = "#%sList|%s\n" % (P, subst(k14_row, vals)) + "".join("set #%s.Text=%s\n" % (subst(a_, vals), subst(v_, vals))
                                                                   for a_, _p, v_ in k14_row.sets)
        check(str(U.srow(i_, sel_, nm_, jpype.JArray(jpype.JString)(ids_))) == want,
              "static_row compiles: runtime id / item / name / status bar (sel=%s)" % sel_)
    check(str(U.sbar(0)) == "#%sBox|%s\n" % (P, UI.render(k14_bar.empty)) and
          str(U.sbar(50)) == "#%sBox|%s\n" % (P, subst(k14_bar.full, {"f": "50"})), "stat_bar.choose() compiles: no fill child at 0")
    check(str(U.brow(310)) == "#%sBody|%s\n" % (P, subst(k14_brow, {"gapR": "310"})), "button_row(left_margin=J()) compiles")
    looks = {"selected": ("#182a40(0.9)", "#4274a5"), "pending": ("#132033(0.8)", "#ffcc00"), "normal": ("#101925(0.55)", "#101925(0.55)"),
             "off": ("#1a1e24", "#1a1e24")}
    for ic_, i_, sel_, pend_, on_ in ((["Weapon_Sword_Iron", "Food_Bread"], 2, False, True, True),
                                      (["A_B", "C", "D", "E"], 0, True, False, True), ([], 5, False, False, False)):
        look = "selected" if sel_ else "pending" if pend_ else "normal" if on_ else "off"
        vals = {"i": str(i_), "cardBg": looks[look][0], "cardBar": looks[look][1], '"Class " + i': "Class %d" % i_, '"role"': "role"}
        lines = []
        for idx, (p_, mk) in enumerate(k14_card):
            if idx == k14_card.act_index:
                lines += ["set #%s.Text=%s" % (subst(a_, vals), subst(v_, vals)) for a_, _p, v_ in k14_card.sets]
            if idx == k14_card.loop_index:
                for k_ in range(min(len(ic_), 3)):
                    vk = dict(vals, k=str(k_))
                    vk["ic[k]"] = ic_[k_]
                    lines.append("#%s|%s" % (subst(p_, vk), subst(mk, vk)))
            else:
                lines.append("#%s|%s" % (subst(p_, vals), subst(mk, vals)))
        got = str(U.card(jpype.JArray(jpype.JString)(ic_), i_, sel_, pend_, on_))
        check(got == "\n".join(lines) + "\n", "list_card compiles: the %s look, %d icon cells in the loop, the b.set lines before the action "
                                               "column" % (look, min(len(ic_), 3)))
    print("java phase: %d fields + %d methods compiled with javassist and compared" % (n, 17 + len(probes) + len(tmpl_names)))


# ================================================================= kit 1.4: the kit 1.3 output is FROZEN (the additive-only rule)
# Kit 1.4 (and every later additive kit) may only ADD functions, parameters (with defaults that keep the old output), table
# entries (appended at the END of a table), vanilla needles (registered after the 1.3 ones) and probe pages (after page 18). The
# generator below calls every 1.3 builder over a broad sample of call shapes (fixed literal lists, never a loop over a table that
# may grow) plus the tables and probe pages 1-18; SNAP13 holds (item count, sha256 prefix) per group, computed from the kit 1.3
# file (blob 988889603a0f) before any 1.4 change. A table group compares its first `count` entries in order (new entries go at
# the end); every other group compares all its items. A mismatch names the group; `--snapshot-dump <file>` (a path inside
# tools/dev/scratch/) writes every item's text, to diff against a dump made from the old kit (git show HEAD~n:tools/skyyui.py).
_SNAP_SEP = chr(30)


def _snap_text(v):
    """The exact text of one builder result (J() markers kept, Java for Appends / Part / Shell, every attribute of a Part)."""
    if isinstance(v, UI.Choice):
        return _SNAP_SEP.join(["CHOICE", v.cond, _snap_text(v.a), _snap_text(v.b)])
    if isinstance(v, UI.Shell):
        attrs = ["%s=%r" % (k, getattr(v, k)) for k in ("prefix", "w", "h", "pad", "kind", "root", "bar", "title", "body", "close",
                                                        "inner_w", "body_h", "inner_h")]
        more = ["%s=%r" % (k, getattr(v, k)) for k in ("question", "message", "note", "row", "yes", "no") if hasattr(v, k)]
        return _SNAP_SEP.join(["SHELL", v.java("b")] + attrs + more + ["sets=%r" % (v.all_sets(),)])
    if isinstance(v, UI.Part):
        attrs = ["%s=%r" % (k, v.__dict__[k]) for k in sorted(v.__dict__) if k != "sets"]
        return _SNAP_SEP.join(["PART", v.java("b")] + attrs + ["sets=%r" % (v.sets,)])
    if isinstance(v, UI.Appends):
        return _SNAP_SEP.join(["APPENDS", v.java("b"), "sets=%r" % (v.sets,)])
    if isinstance(v, UI.Probe):
        return _SNAP_SEP.join(["PROBE", str(v.n), v.key, v.name, repr(v.look), v.java("b"), v.java("b", extra=False)])
    if isinstance(v, str):
        return v
    if isinstance(v, (list, tuple)):
        return "[" + _SNAP_SEP.join(_snap_text(x) for x in v) + "]"
    return repr(v)


SNAP_TABLES = ("COLOR", "_COLOR_SRC", "TEX", "SND", "SOUNDS", "LABELS", "LABEL_MORE", "BUTTONS", "BUTTON_SIZES", "STATUS",
               "STATUS_INFO", "RARITY", "RARITY_WYNN", "RARITY_ORDER", "QUALITY", "QUALITY_SLOT", "QUALITY_TIP", "READABLE", "PANELS",
               "UNVERIFIED", "DOCS", "CLIENT_DOCS", "FONTS", "SEPARATORS", "PANEL_KINDS", "FIELD_LOOKS", "CONFIRM_PANELS",
               "ICON_CELL_STATES", "ICON_CELL_LOOKS", "TILE_STATES", "PROBE_BASE")
SNAP_SCALARS = ("GAME_DIR", "ASSETS_ZIP", "CLIENT_UI_DIR", "CUSTOM", "FONT_DEFAULT", "FONT_SECONDARY", "TITLE_H", "TITLE_PAD_TOP",
                "TITLE_LABEL_PAD", "TITLE_SIZE", "DECO_W", "DECO_H", "DECO_TOP", "DECO_BOTTOM", "CONTENT_PAD", "PAGE_PAD", "DIALOG_PAD",
                "FORM_PAD", "BTN_H", "BTN_SMALL_H", "BTN_BIG_H", "BTN_PAD", "BTN_SMALL_PAD", "BTN_MIN_W", "PRIMARY_MIN_W",
                "PRIMARY_SMALL_W", "BTN_BORDER", "FIELD_H", "FIELD_PAD", "INPUT_BORDER", "FILTER_H", "FILTER_PAD", "SEARCH_H",
                "SEARCH_PAD_LEFT", "ROW_H", "ROW_GAP", "ROW_ACTION_W", "ROW_H_READABLE", "OPTION_ROW_H", "OPTION_ROW_GAP",
                "SETTING_ROW_H", "SETTING_ROW_GAP", "PROP_ROW_H", "PROP_ROW_GAP", "PROP_KEY_W", "CHECK_SIZE", "CHECK_LABEL_W",
                "CHECK_ROW_GAP", "TAB_GAP", "TAB_MARGIN", "WELL_PAD", "WELL_LIST_PAD", "SEP_MARGIN", "FORM_LINE_MARGIN", "SCROLL_SIZE",
                "SCROLL_SPACING", "CONFIRM_W", "PROGRESS_W", "PROGRESS_H", "MEMBAR_H", "MEMBAR_PAD", "MEMBAR_W", "DROPDOWN_W",
                "DROPDOWN_H", "SPINNER", "TILE_W", "TILE_H", "TILE_GAP", "TILE_BORDER", "TOOLTIP_MAX_W", "TOOLTIP_PAD",
                "TOOLTIP_BORDER", "CLOSE_SIZE", "SLOT_FRAME", "SLOT_ICON", "CARD_W", "CARD_H", "CARD_MARGIN", "ICON", "MAX_PAGE_H",
                "MAX_PAGE_W", "MIN_PAGE_W", "GRID_SLOT", "GRID_ICON", "GRID_SPACING", "GRID_WELL_PAD", "GRID_SLOT_CLASS",
                "ITEM_STACK_CLASS", "DROPDOWN_SOUNDS", "_HOVER")
SNAP_KINDS = ("default", "bold", "strong", "message", "caption", "captionLight", "note", "muted", "gold", "error", "formError",
              "success", "warning", "info", "disabled", "have", "outOfStock", "stock", "quantity", "rowName", "rowSub", "rowBadge",
              "heading", "propKey", "propValue", "summary", "fieldLabel", "display", "tileName", "section", "subtitle", "panelTitle",
              "formCaption", "optionName", "optionDetail", "cardCaption", "tipName", "tipId", "tipDesc", "tipStat", "setting",
              "settingHead")


def snapshot_items():
    """{group: [(name, text)]} - the kit 1.3 builders over a broad sample of call shapes, the tables, the needles, probe pages 1-18.
    Only the kit 1.3 API is called here (keep it that way: this is the frozen reference)."""
    out = {}
    J = UI.J

    def add(group, name, fn):
        try:
            v = fn() if callable(fn) else fn
            txt = _snap_text(v)
        except Exception as e:      # noqa - an error is part of the frozen behaviour too
            txt = "RAISES " + type(e).__name__ + ": " + str(e)
        out.setdefault(group, []).append((name, txt))

    # ---- tables (insertion order; 1.4 may append entries), scalars, the vanilla needles (1.4 registers new ones after these)
    for t in SNAP_TABLES:
        d = getattr(UI, t)
        if isinstance(d, dict):
            for k in d:
                add("table " + t, repr(k), repr(d[k]))
        else:
            for i, v in enumerate(d):
                add("table " + t, str(i), repr(v))
    for n in SNAP_SCALARS:
        add("scalars", n, repr(getattr(UI, n)))
    for n in ("TEXT_OK", "_ID_OK", "_COLOR_OK", "_J_RE", "_ELEM_OPEN", "_PATH_RE", "_TEXT_PROP_RE", "_NORM_RE", "_ITEM_ID_OK"):
        add("scalars", n, getattr(UI, n).pattern)
    for i, (d, n, w) in enumerate(UI.checks()):
        add("table checks", str(i), "%s|%s|%s" % (d, n, w))
    # ---- small helpers
    for v in (0, 11, 12, 13, 14, 15, 16, 18, 20, 32):
        add("fs", "readable %d" % v, lambda v=v: UI.fs(v))
    for c in ("gold", "text", "#12ab34", "#12AB34(0.5)", "#ffffff00", J("c", "#ffcc00")):
        add("color", repr(c), lambda c=c: UI.color(c))
    for s in ("#ABCDEF(0.50)", "#ffffff(...)", "#FFFFFF(.5)", "#123456", "nope"):
        add("norm_color", s, lambda s=s: UI.norm_color(s))
    add("allowed_colors", "all", lambda: sorted(UI.allowed_colors()))
    for k in ("light", "cancel", "save", "main", "lock", "unlock"):
        add("sounds", k, lambda k=k: UI.sounds(k))
    for a in (("header",), ("header", None, 50, 0), ("headerPlain", None, 35, 0), ("patch", 23), ("input", 16), ("option", 16, None, None, "optionHover"),
              ("Common/Scrollbar.png", 3), ("vsep",)):
        add("patch", repr(a), lambda a=a: UI.patch(*a))
    for f in ("scrollbar_style", "tooltip_style", "checkbox_style", "clear_button_style", "search_icon", "title_style"):
        add(f, "()", getattr(UI, f))
    add("scrollbar_style", "12", lambda: UI.scrollbar_style(12))
    add("dropdown_style", "plain", lambda: UI.dropdown_style())
    add("dropdown_style", "search", lambda: UI.dropdown_style(search=True))
    for a, kw in (((16, "text"), {}), ((14, "white"), {"bold": True, "upper": True, "italic": True}), ((13, "value"), {"halign": "End", "valign": None}),
                  ((12, "caption"), {"wrap": True, "max_lines": 2}), ((15, "title"), {"font": "Secondary", "spacing": 0.5, "shrink": 11}),
                  ((18, J("col", "#ffcc00")), {"halign": "Center", "valign": "Start", "spacing": 0}), ((20, "gold"), {"wrap": True, "max_lines": 0}),
                  ((16, "text"), {"max_lines": 2})):
        add("text_style", repr((a, sorted(kw.items()))), lambda a=a, kw=kw: UI.text_style(*a, **kw))
    # ---- labels: every kind, then the options cycled over the kinds
    opts = ({}, {"text": "Hello World 42"}, {"w": 300}, {"h": False}, {"size": 20}, {"col": "gold"}, {"bold": True}, {"bold": False},
            {"upper": True}, {"align": "End"}, {"align": "Center", "valign": "Start"}, {"valign": False}, {"wrap": True},
            {"wrap": True, "max_lines": 2}, {"max_lines": False}, {"italic": True}, {"anchor": {"top": 4, "left": 2}}, {"padding": 6},
            {"padding": {"horizontal": 10}}, {"flex": 1}, {"font": "Secondary"}, {"spacing": 1.8}, {"extra": "Visible: true"},
            {"col": J("cols[i]", "#8fd67a"), "w": J("lw", "200")}, {"wrap": False}, {"text": "Page 1 of 3 < >", "w": 400, "h": 30})
    for i, k in enumerate(SNAP_KINDS):
        add("label", k, lambda k=k: UI.label("SkyyTL" + k[:1].upper() + k[1:], "", k))
        for j in (i % len(opts), (i + 7) % len(opts), (i + 13) % len(opts)):
            kw = dict(opts[j])
            text = kw.pop("text", "")
            add("label", "%s %d" % (k, j), lambda k=k, kw=kw, text=text: UI.label("SkyyTLo" + str(j), text, k, **kw))
    add("label", "anonymous", lambda: UI.label(None, "Plain", "caption", h=False, flex=1))
    add("label", "runtime id", lambda: UI.label("SkyyTLr" + J("i", "3"), "", "rowSub"))
    add("label", "bad kind", lambda: UI.label("SkyyTX", "", "neon"))
    add("status_line", "default", lambda: UI.status_line("SkyyTSt"))
    add("status_line", "expr", lambda: UI.status_line("SkyyTSt", "infoColor(this.info)"))
    add("status_line", "wrap", lambda: UI.status_line("SkyyTSt", h=44, wrap=True))
    add("status_line", "wrap max", lambda: UI.status_line("SkyyTSt", h=46, size=18, wrap=True, max_lines=2, anchor={"top": 12}))
    add("title_label", "static", lambda: UI.title_label("SkyyTT", "Reforge"))
    add("title_label", "empty", lambda: UI.title_label("SkyyTT"))
    add("section", "plain", lambda: UI.section("SkyyTSec", "Your gear"))
    add("section", "anon w h", lambda: UI.section(None, "Heads", h=30, w=200))
    add("subtitle", "plain", lambda: UI.subtitle("SkyyTSub", "Purse"))
    add("subtitle", "anon h", lambda: UI.subtitle(None, "Bank", h=25))
    add("panel_title", "plain", lambda: UI.panel_title("SkyyTPt", "Before"))
    add("panel_title", "w", lambda: UI.panel_title("SkyyTPt", "", w=275))
    add("property_row", "plain", lambda: UI.property_row("SkyyTPr", "SkyyTPk", "SkyyTPv", "Level"))
    add("property_row", "opts", lambda: UI.property_row("SkyyTPr", "SkyyTPk", "SkyyTPv", "", key_w=200, h=30, gap=0, w=500,
                                                        anchor={"top": 4}))
    # ---- buttons
    for kind in ("primary", "secondary", "tertiary", "destructive"):
        for size in ("normal", "small", "big"):
            add("button_style", "%s %s" % (kind, size), lambda kind=kind, size=size: UI.button_style(kind, size))
            add("button_style", "%s %s disabled" % (kind, size), lambda kind=kind, size=size: UI.button_style(kind, size, disabled=True))
            for snd in ("light", "cancel", "save", "main", "lock", "unlock"):
                add("button_style", "%s %s %s" % (kind, size, snd), lambda kind=kind, size=size, snd=snd: UI.button_style(kind, size, sound=snd))
            add("button", "%s %s" % (kind, size), lambda kind=kind, size=size: UI.button("SkyyTB", "Go", kind, size))
            add("button", "%s %s w" % (kind, size), lambda kind=kind, size=size: UI.button("SkyyTB", "Deposit all", kind, size, w=200))
            add("button", "%s %s disabled" % (kind, size), lambda kind=kind, size=size: UI.button("SkyyTB", "", kind, size, w=180, disabled=True))
    add("button_style", "tertiary selected", lambda: UI.button_style("tertiary", selected=True))
    add("button_style", "tertiary small selected", lambda: UI.button_style("tertiary", "small", selected=True, sound="cancel"))
    for name, fn in (("selected", lambda: UI.button("SkyyTB", "Ranks", "tertiary", "small", w=190, selected=True)),
                     ("save", lambda: UI.button("SkyyTB", "Save", "primary", w=172, sound="save", anchor={"right": 6})),
                     ("cancel", lambda: UI.button("SkyyTB", "Close", "secondary", sound="cancel", anchor={"left": 4})),
                     ("flex", lambda: UI.button("SkyyTB", "Back", flex=1)),
                     ("flex w", lambda: UI.button("SkyyTB", "Back", w=100, flex=2)),
                     ("h", lambda: UI.button("SkyyTB", "Tall", h=56)),
                     ("runtime id", lambda: UI.button("SkyyTB" + J("i", "3"), "Buy", size="small")),
                     ("runtime w", lambda: UI.button("SkyyTB", "Buy", "primary", w=J("bw", "160"))),
                     ("primary 120", lambda: UI.button("SkyyTB", "Save", "primary", w=120)),
                     ("primary 110", lambda: UI.button("SkyyTB", "Save", "primary", w=110)),
                     ("extra", lambda: UI.button("SkyyTB", "X", extra="Visible: true")),
                     ("disable element", lambda: UI.button("SkyyTB", "X", disable_element=True, trial=True)),
                     ("text lt gt", lambda: UI.button("SkyyTB", "< Prev", size="small", w=150))):
        add("button", name, fn)
    add("on_off", "on", lambda: UI.on_off("SkyyTPvp", True))
    add("on_off", "off w h texts", lambda: UI.on_off("SkyyTPvp", False, w=100, h=40, texts=("Yes", "No")))
    add("close_button", "x", lambda: UI.close_button("SkyyTClose"))
    for a in ("center", "left", "right"):
        add("button_row", a, lambda a=a: UI.button_row("SkyyTBr", align=a))
    add("button_row", "opts", lambda: UI.button_row("SkyyTBr", h=48, align="left", top=0, w=600, anchor={"bottom": 4}))
    add("button_row", "anchor top", lambda: UI.button_row("SkyyTBr", top=12, anchor={"top": 4}))
    add("spacer", "w", lambda: UI.spacer(12))
    add("spacer", "h", lambda: UI.spacer(h=40))
    add("spacer", "wh", lambda: UI.spacer(12, 40))
    add("spacer", "J", lambda: UI.spacer(J("gap", "10"), 44))
    for lm in ("Left", "Top", "Right", "Center", "Middle", "Full", "TopScrolling", "CenterMiddle", "MiddleCenter", "LeftCenterWrap", None):
        add("group", str(lm), lambda lm=lm: UI.group("SkyyTG", lm, h=44))
    add("group", "anon", lambda: UI.group(None, "Top", w=300, flex=1, pad=8))
    add("group", "pad dict extra", lambda: UI.group("SkyyTG", "Left", w=500, h=60, pad={"horizontal": 8, "vertical": 4}, extra="Visible: true"))
    add("group", "anchor", lambda: UI.group("SkyyTG", "Left", h=44, anchor={"top": 4, "left": J("m", "12")}))
    # ---- inputs
    for look in ("kit", "vanilla", "filter"):
        add("text_field", look, lambda look=look: UI.text_field("SkyyTFb", "SkyyTF", 300, placeholder="player name", look=look))
        add("text_field", look + " opts", lambda look=look: UI.text_field("SkyyTFb", "SkyyTF", None, 40, "", 16, 18, look=look, flex=1,
                                                                      anchor={"left": 0}, padding={"left": 12}, extra="Visible: true",
                                                                      field_extra="Visible: true"))
    add("text_field", "number", lambda: UI.text_field("SkyyTNb", "SkyyTN", 120, number=True, trial=True))
    add("text_field", "full width", lambda: UI.text_field("SkyyTFb", "SkyyTF"))
    add("search_field", "plain", lambda: UI.search_field("SkyyTSb", "SkyyTS", 300, placeholder="search", trial=True))
    add("search_field", "opts", lambda: UI.search_field("SkyyTSb", "SkyyTS", None, 32, "", 20, "filter", True, {"top": 4}, 1, "Visible: true"))
    add("value_box", "plain", lambda: UI.value_box("SkyyTVb", "SkyyTV", 260))
    add("value_box", "opts", lambda: UI.value_box("SkyyTVb", "SkyyTV", None, 44, "strong", {"right": 8}, 1, {"left": 12}, "Visible: true"))
    add("checkbox", "on", lambda: UI.checkbox("SkyyTC", True, trial=True))
    add("checkbox", "off anchor", lambda: UI.checkbox("SkyyTC", False, trial=True, anchor={"top": 8}, extra="Visible: true"))
    add("checkbox_row", "plain", lambda: UI.checkbox_row("SkyyTCr", "SkyyTCl", "SkyyTCb", True, "Include entities", trial=True))
    add("checkbox_row", "opts", lambda: UI.checkbox_row("SkyyTCr", "SkyyTCl", "SkyyTCb", False, "", 300, 30, 0, True, {"top": 4}))
    add("dropdown", "plain", lambda: UI.dropdown("SkyyTD", trial=True))
    add("dropdown", "search flex", lambda: UI.dropdown("SkyyTD", 400, 40, True, True, {"left": 4}, 1, "Visible: true"))
    # ---- tabs, rows, lists
    add("tab_row", "primary", lambda: UI.tab_row("SkyyTBody", "SkyyTTr", ["SkyyTT0", "SkyyTT1", "SkyyTT2"], ["Ranks", "Players", ""], 1))
    add("tab_row", "tertiary", lambda: UI.tab_row("SkyyTBody", "SkyyTTr", ["SkyyTT0", "SkyyTT1"], ["A", "B"], 0, w=190, mode="tertiary"))
    add("tab_row", "opts", lambda: UI.tab_row("SkyyTBody", "SkyyTTr", ["SkyyTT0", "SkyyTT1"], ["A", "B"], 1, w=200, h=40, gap=0,
                                              row_h=48, top=0, bottom=4))
    for st in ("normal", "selected", "static"):
        add("row_style", st, lambda st=st: UI.row_style(st))
        add("panel_row", st, lambda st=st: UI.panel_row("SkyyTRow", st))
        add("panel_row", st + " opts", lambda st=st: UI.panel_row("SkyyTRow", st, h=42, gap=0, bar=False, w=600))
        add("hover_row", st, lambda st=st: UI.hover_row("SkyyTHr", st, h=44))
        add("option_row", st, lambda st=st: UI.option_row("SkyyTOp", st == "selected"))
        add("list_button", st, lambda st=st: UI.list_button("SkyyTLb", "Mining", st))
    add("panel_row", "runtime", lambda: UI.panel_row("SkyyTRow" + J("r", "4")))
    add("row_text", "both", lambda: UI.row_text("SkyyTTx", "SkyyTNm", "SkyyTSb"))
    add("row_text", "name", lambda: UI.row_text("SkyyTTx", "SkyyTNm"))
    add("row_text", "opts", lambda: UI.row_text("SkyyTTx", "SkyyTNm", "SkyyTSb", row_h=70, name_kind="heading", sub_kind="caption"))
    add("row_badge", "plain", lambda: UI.row_badge("SkyyTBd"))
    add("row_badge", "w", lambda: UI.row_badge("SkyyTBd", w=200))
    for kind in ("secondary", "primary", "destructive"):
        add("row_action", kind, lambda kind=kind: UI.row_action("SkyyTAct", "Edit", kind))
    add("row_action", "opts", lambda: UI.row_action("SkyyTAct", "Equip", w=112, h=56, disabled=True, sound="cancel"))
    add("hover_row", "opts", lambda: UI.hover_row("SkyyTHr", "selected", h=50, pad=8, w=300, sound="light"))
    add("option_style", "plain", lambda: UI.option_style())
    add("option_style", "selected light", lambda: UI.option_style(True, "light"))
    add("option_row", "opts", lambda: UI.option_row("SkyyTOp", False, 60, 0, 400, "light", {"top": 8}))
    add("list_button_style", "normal", lambda: UI.list_button_style())
    add("list_button_style", "selected mask", lambda: UI.list_button_style("selected", mask=True, trial=True))
    add("list_button", "opts", lambda: UI.list_button("SkyyTLb", "Nav", "selected", 40, 200, 0, "light", True, True))
    add("setting_row", "plain", lambda: UI.setting_row("SkyyTSet", "SkyyTSetL"))
    add("setting_row", "opts", lambda: UI.setting_row("SkyyTSet", "SkyyTSetL", 300, 50, 0, {"top": 4}, "Visible: true"))
    add("scroll_list", "h", lambda: UI.scroll_list("SkyyTL", h=500))
    add("scroll_list", "flex spacing", lambda: UI.scroll_list("SkyyTL", extra_spacing=True))
    add("scroll_list", "well", lambda: UI.scroll_list("SkyyTL", well=True))
    add("scroll_list", "opts", lambda: UI.scroll_list("SkyyTL", 400, 2, 600, True, True, 6, {"top": 8}, "Visible: true"))
    for kind in ("content", "fancy", "vertical", "header", "footer", "panel", "form"):
        add("separator", kind, lambda kind=kind: UI.separator(kind))
        add("separator", kind + " opts", lambda kind=kind: UI.separator(kind, "SkyyTSep", 400, 3, {"top": 8, "bottom": 8}, 1, "Visible: true"))
    for kind in ("simple", "full", "secondary", "tooltip", "well", "dark", "row", "hud"):
        add("panel", kind, lambda kind=kind: UI.panel("SkyyTPn", kind, w=400, h=200))
        add("panel", kind + " opts", lambda kind=kind: UI.panel("SkyyTPn", kind, None, 100, {"left": 4, "top": 2}, "Left", 1, {"top": 4},
                                                                "Visible: true"))
    # ---- items, cells, cards, bars
    add("item_icon", "static", lambda: UI.item_icon("SkyyTIc", "Weapon_Sword_Iron", 48))
    add("item_icon", "anon", lambda: UI.item_icon(None, None, 32))
    add("item_icon", "runtime", lambda: UI.item_icon("SkyyTIc", J("ids[i]", "Weapon_Sword_Iron"), anchor={"left": 4, "top": 8}))
    add("item_frame", "plain", lambda: UI.item_frame("SkyyTFr"))
    add("item_frame", "icon", lambda: UI.item_frame("SkyyTFr", icon_id="SkyyTFrI"))
    add("item_frame", "opts", lambda: UI.item_frame("SkyyTFr", 64, "slotBorderHave", "SkyyTFrI", 56, {"left": 8, "top": 10}, "Visible: true"))
    add("item_slot", "plain", lambda: UI.item_slot("SkyyTSb", "SkyyTSl", trial=True))
    add("item_slot", "opts", lambda: UI.item_slot("SkyyTSb", "SkyyTSl", 80, False, True, trial=True))
    for q in ("Default", "Junk", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Technical", "Tool", "Developer", "Debug", "Template"):
        add("quality_frame", q, lambda q=q: UI.quality_frame("SkyyTQf", q, icon_id="SkyyTQfI", trial=True))
        add("tooltip_panel", q, lambda q=q: UI.tooltip_panel("SkyyTTq", quality=q, trial=True))
    add("tooltip_panel", "plain", lambda: UI.tooltip_panel("SkyyTTp"))
    add("tooltip_panel", "opts", lambda: UI.tooltip_panel("SkyyTTp", 300, 120, anchor={"top": 12}))
    add("item_grid_style", "plain", lambda: UI.item_grid_style())
    add("item_grid_style", "bg", lambda: UI.item_grid_style(40, 32, 0, True, True))
    add("item_grid", "kit", lambda: UI.item_grid("SkyyTIg", 9, 6))
    add("item_grid", "bare", lambda: UI.item_grid("SkyyTIg", 4, 1, well=False, tooltips=False, anchor={"left": 8}))
    add("item_grid", "runtime", lambda: UI.item_grid("SkyyTIg", J("g[0]", "4"), 2, slot=J("g[1]", "72"), spacing=0, w=J("g[2]", "288"),
                                                     h=J("g[3]", "144")))
    add("item_grid", "opts", lambda: UI.item_grid("SkyyTIg", 32, 18, 40, 1, 0, True, False, True, "SkyyTIgW", None, None, {"top": 4}, True, True))
    add("java_grid_methods", "default", lambda: UI.java_grid_methods())
    add("java_grid_methods", "custom", lambda: UI.java_grid_methods("slot", "a.B", "a.C"))
    add("java_grid_fill", "mixed", lambda: UI.java_grid_fill("SkyyTIg", [("Weapon_Sword_Iron", 1), None, (J("ids[k]", "Food_Bread"), J("qs[k]", "3"))],
                                                             var="pbSlots", b="cmd"))
    for src in ("slots.add(new com.hypixel.hytale.server.core.ui.ItemGridSlot(st));",
                "x = new com.hypixel.hytale.server.core.ui.ItemGridSlot();"):
        add("item_grid_java_is_safe", src[:40], lambda src=src: UI.item_grid_java_is_safe(src))
    for st in ("normal", "selected", "disabled", "empty"):
        for lk in ("row", "plain"):
            add("icon_cell", "%s %s" % (st, lk), lambda st=st, lk=lk: UI.icon_cell("SkyyTCell", "Weapon_Sword_Iron", 74, st, look=lk))
            add("icon_cell", "%s %s qty" % (st, lk), lambda st=st, lk=lk: UI.icon_cell("SkyyTCell", "Ingredient_Bar_Iron", 87, st, qty="64",
                                                                                 look=lk, sound=None, anchor={"right": 6}))
    add("icon_cell", "qty label", lambda: UI.icon_cell("SkyyTCell", "Ingredient_Bar_Iron", qty=True))
    add("icon_cell", "runtime", lambda: UI.icon_cell("SkyyTCell" + J("i", "3"), J("ids[i]", "Weapon_Sword_Iron"), 76))
    add("icon_cell", "wide", lambda: UI.icon_cell("SkyyTCell", "Weapon_Sword_Iron", w=158, h=76, icon=44, icon_left=6, extra="Visible: true"))
    add("icon_cell", "no item", lambda: UI.icon_cell("SkyyTCell", None, 64))
    add("card", "plain", lambda: UI.card("SkyyTCard"))
    add("card", "sold out", lambda: UI.card("SkyyTCard", sold_out=True))
    add("card", "no margin", lambda: UI.card("SkyyTCard", margin=0, extra="Visible: true"))
    add("card", "opts", lambda: UI.card("SkyyTCard", 200, 160, "SkyyTCardIn2", 4, True, "SkyyTCardO", {"left": 8}, 1, "Visible: true"))
    add("bar", "plain", lambda: UI.bar("SkyyTBar", 400, 18, 120))
    add("bar", "runtime", lambda: UI.bar("SkyyTBar" + J("i", "2"), 400, 18, J("fw", "200"), col="progressGreen", anchor={"top": 4}))
    add("bar", "flex", lambda: UI.bar("SkyyTBar", None, 12, J("fw", "40"), track="well", flex=1, extra="Visible: true"))
    add("progress", "default", lambda: UI.progress("SkyyTPr", value=0.25, trial=True))
    add("progress", "memories", lambda: UI.progress("SkyyTPm", value=0.5, kind="memories", trial=True))
    add("progress", "flex", lambda: UI.progress("SkyyTPr", None, 10, 1, "default", True, {"top": 4}, 1, "Visible: true"))
    add("tooltip", "plain", lambda: UI.tooltip("Sells for 20 coins", trial=True))
    add("spinner", "plain", lambda: UI.spinner("SkyyTSp", trial=True))
    add("spinner", "anon", lambda: UI.spinner(None, 48, True, {"left": 4}))
    for st in ("default", "selected", "complete", "empty"):
        add("tile", st, lambda st=st: UI.tile("SkyyTTl", "Mage", st, trial=True))
    add("tile", "opts", lambda: UI.tile("SkyyTTl", "", "default", 120, 150, 0, None, True, {"left": 4}, "Visible: true"))
    add("gradient_label", "plain", lambda: UI.gradient_label("SkyyTBig", "Mining", trial=True))
    add("gradient_label", "size", lambda: UI.gradient_label("SkyyTBig", "", 28, True))
    # ---- windows, blocks, Java
    for kind in ("decorated", "plain"):
        add("page_shell", kind, lambda kind=kind: UI.page_shell("SkyyT", 1100, 880, "Reforge", kind=kind))
        add("page_shell", kind + " close", lambda kind=kind: UI.page_shell("SkyyT", 1100, 880, "Reforge", kind=kind, close=True))
    add("page_shell", "ids", lambda: UI.page_shell("SkyyBankF", 1100, 860, body_id="SkyyBank", title="Bank"))
    add("page_shell", "custom", lambda: UI.page_shell("SkyyT", 900, 600, "Buy page 3 for 1,250 coins?", "plain", 16, "SkyyTRt", "SkyyTBr",
                                                      "SkyyTTi", "SkyyTBd", True, "SkyyTX", "Left"))
    add("page_shell", "runtime", lambda: UI.page_shell("SkyyT", J("w", "900"), J("h", "600"), J("titleOf(p)", "X")))
    add("page_shell", "too high", lambda: UI.page_shell("SkyyT", 900, 981))
    add("confirm_dialog", "primary", lambda: UI.confirm_dialog("SkyyTD", title="Confirm", yes_text="Buy"))
    add("confirm_dialog", "destructive", lambda: UI.confirm_dialog("SkyyTD", 700, 60, False, "Delete", "Keep", "destructive", None, 200, 160,
                                                                   "Delete rank?", {"body": "SkyyTDb", "root": "SkyyTDr"}))
    add("pager", "static", lambda: UI.pager("SkyyTBody", "SkyyTPg", 1066, text="Page 2 / 5", prev_on=False))
    add("pager", "runtime", lambda: UI.pager("SkyyTBody", "SkyyTPj", 900, text=J("pageText()"), prev_on=J("pageNo > 0"),
                                             next_on=J("pageNo < pages - 1")))
    add("pager", "left", lambda: UI.pager("SkyyTBody", "SkyyTPt", 900, text="Page 2 of 5, 40 items", align="left", top=0))
    add("pager", "opts", lambda: UI.pager("SkyyTBody", "SkyyTOld", 900, None, True, False, 140, 300, 8, "Back", "More", "right", 12, "caption",
                                          {"prev": "SkyyTOldPrevious", "page": "SkyyTOldNo"}))
    add("confirm_view", "plain", lambda: UI.confirm_view("SkyyTBody", "SkyyTCf", 1066, question="Delete rank vip?", message="Nothing has changed yet"))
    add("confirm_view", "destructive row", lambda: UI.confirm_view("SkyyTBody", "SkyyTCd", 900, question=J("q"), message="", note="Costs 5,000 coins",
                                                                   yes_kind="destructive", panel="row"))
    add("confirm_view", "no panel", lambda: UI.confirm_view("SkyyTBody", "SkyyTCn", 900, panel=None, pad=0, top=0))
    add("confirm_view", "compact", lambda: UI.confirm_view("SkyyTBody", "SkyyTCc", 900, question="Switch to Mage for 500 coins?", compact=True))
    add("confirm_view", "compact ids", lambda: UI.confirm_view("SkyyTBody", "SkyyClsConfirm", 1066, question=J("safe(q)"), yes_text="Confirm",
                                                               no_text="Cancel", yes_w=200, no_w=160, compact=True, top=8, panel="row",
                                                               ids={"box": "SkyyClsConfirm", "yes": "SkyyClsYes", "no": "SkyyClsNo"}))
    add("confirm_view", "opts", lambda: UI.confirm_view("SkyyTBody", "SkyyTCo", 1000, "Sell all", "Everything goes", "A note", 60, "Sell", "Keep",
                                                        "primary", "cancel", 200, 200, "well", 16, False, 0,
                                                        {"box": "SkyyTCoB", "question": "SkyyTCoQ", "message": "SkyyTCoM", "note": "SkyyTCoN",
                                                         "row": "SkyyTCoR", "yes": "SkyyTCoY", "no": "SkyyTCoX"}))

    def ap_text():
        ap = UI.Appends([(None, "Group #SkyyTA { Anchor: (Width: 1100, Height: 900); }"), ("SkyyTA", "Group #SkyyTBody { LayoutMode: Top; }")])
        ap.text("SkyyTBody", "SkyyTCap", "your whole purse", "caption", w=200)
        ap.text("SkyyTBody", "SkyyTMid", "max 1,000,000 coins (5%).", "caption", w=300)
        ap.text("SkyyTBody", None, "Page 1 of 3?", "default")
        ap.text("SkyyTBody", None, "Page 2 of 3?", "default")
        ap.text("SkyyTBody", None, "plain inline", "default")
        ap.text("SkyyTBody", "SkyyTRun", J("name", "Skyy"), "strong")
        return ap
    add("Appends.text", "mixed", ap_text)

    def sh_text():
        sh = UI.page_shell("SkyyT", 900, 600, "Shop")
        sh.text(sh.body, None, "Buy 3 for 1,250 coins?", "default")
        return sh
    add("Shell.text", "mixed", sh_text)
    add("choose", "java", lambda: UI.java_append("SkyyTRow", UI.choose(UI.J("pageNo > 0"), UI.button("SkyyTPv", "Prev", size="small"),
                                                                       UI.button("SkyyTPv", "Prev", size="small", disabled=True))))
    add("java_append", "root", lambda: UI.java_append(None, "Group #SkyyTA { Anchor: (Width: 1, Height: 2); }"))
    add("java_append", "hud root", lambda: UI.java_append(None, "Group #SkyyH { Anchor: (Full: 0); }", page_root=False))
    add("java_append", "runtime parent", lambda: UI.java_append("SkyyTRow" + J("r"), "Label { }", "cmd"))
    for name, fn in (("text J", lambda: UI.java_set("SkyyTName", "Text", J("name"))), ("float", lambda: UI.java_set("SkyyTPr", "Value", 0.5)),
                     ("bool", lambda: UI.java_set("SkyyTCk", "Value", True)), ("int", lambda: UI.java_set("SkyyTN", "Value", 3)),
                     ("raw", lambda: UI.java_set("SkyyTPr", "Value", J("f"), raw=True)), ("text", lambda: UI.java_set("SkyyTT", "Text", 'a "q" \\ b')),
                     ("set_raw", lambda: UI.java_set_raw("SkyyTX", "Visible", "on", "cmd"))):
        add("java_set", name, fn)
    for info in (None, "gold", "warning"):
        add("java_status_methods", str(info), lambda info=info: UI.java_status_methods(info=info))
    add("java_status_methods", "names", lambda: UI.java_status_methods("colOf", "txtOf"))
    add("java_ref_style", "plain", lambda: UI.java_ref_style("SkyyTX", "SecondaryTextButtonStyle", trial=True))
    add("java_field", "plain", lambda: UI.java_field("ROW", 'Label { Text: "x"; }'))
    add("java_expr", "mixed", lambda: UI.java_expr("a" + J("i") + "b" + J("j")))
    add("java_lit", "tricky", lambda: UI.java_lit('a "quoted" \\ back\nnew\ttab'))
    add("for_pysource", "raw f", lambda: UI.for_pysource('x {y} \\ "z"', raw=True))
    add("for_pysource", "plain", lambda: UI.for_pysource('x {y} \\ z'))
    add("for_percent", "plain", lambda: UI.for_percent("50% {x}"))
    add("render", "mark", lambda: UI.render("Row" + J("i", "7") + J("j"), mark=True))
    add("assert_page_size", "ok", lambda: UI.assert_page_size(900, 600))
    add("fit", "ok", lambda: UI.fit([10, 20], 50))
    # ---- the vanilla text scale: a sample again at the exact vanilla sizes
    UI.text_scale("vanilla")
    try:
        for k in ("rowName", "rowSub", "caption", "section", "heading", "propKey", "default"):
            add("vanilla scale", "label " + k, lambda k=k: UI.label("SkyyTV", "", k))
        add("vanilla scale", "panel_row", lambda: UI.panel_row("SkyyTRow"))
        add("vanilla scale", "row_text", lambda: UI.row_text("SkyyTTx", "SkyyTNm", "SkyyTSb"))
        add("vanilla scale", "row_action", lambda: UI.row_action("SkyyTAct", "Edit"))
        add("vanilla scale", "property_row", lambda: UI.property_row("SkyyTPr", "SkyyTPk", "SkyyTPv"))
        add("vanilla scale", "text_field filter", lambda: UI.text_field("SkyyTFb", "SkyyTF", look="filter"))
        add("vanilla scale", "dropdown_style", lambda: UI.dropdown_style(True))
        add("vanilla scale", "list_button", lambda: UI.list_button("SkyyTLb", "Nav"))
        add("vanilla scale", "confirm_dialog", lambda: UI.confirm_dialog("SkyyTD", title="Confirm"))
        add("vanilla scale", "tile", lambda: UI.tile("SkyyTTl", "Mage", trial=True))
    finally:
        UI.text_scale("readable")
    # ---- probe pages 1-18 (the deployed SkyyUiProbe 0.1 opens them by number / name) and every build_samples() entry
    pages = UI.probe_pages()
    for pg in pages[:18]:
        add("probe pages 1-18", "%d %s" % (pg.n, pg.name), pg)
    for pg in UI.probe_pages("SkyyZz")[:18]:
        add("probe pages 1-18 prefix", "%d %s" % (pg.n, pg.name), pg)
    for name, mk in build_samples().items():
        if SNAP_SAMPLES13 is None or name in SNAP_SAMPLES13:
            add("build_samples 1.3", name, mk)
    return out


# the build_samples() names of kit 1.3 (their output is frozen; samples added for 1.4 are checked by the builder phases instead)
SNAP_SAMPLES13 = frozenset([
    'bar', 'bar flex', 'bar runtime', 'button destructive big', 'button destructive big default width',
    'button destructive big disabled', 'button destructive normal', 'button destructive normal default width',
    'button destructive normal disabled', 'button destructive small', 'button destructive small default width',
    'button destructive small disabled', 'button flex', 'button lock sound', 'button primary 120', 'button primary big',
    'button primary big default width', 'button primary big disabled', 'button primary normal',
    'button primary normal default width', 'button primary normal disabled', 'button primary small',
    'button primary small default width', 'button primary small disabled', 'button row', 'button runtime id',
    'button runtime width', 'button save sound', 'button secondary big', 'button secondary big default width',
    'button secondary big disabled', 'button secondary normal', 'button secondary normal default width',
    'button secondary normal disabled', 'button secondary small', 'button secondary small default width',
    'button secondary small disabled', 'button tertiary big', 'button tertiary big default width', 'button tertiary big disabled',
    'button tertiary normal', 'button tertiary normal default width', 'button tertiary normal disabled', 'button tertiary selected',
    'button tertiary small', 'button tertiary small default width', 'button tertiary small disabled', 'card', 'card flex',
    'card no margin', 'card sold out', 'checkbox', 'checkbox row', 'close', 'dropdown', 'dropdown search flex', 'gradient label',
    'group anon column', 'group padding dict', 'group row', 'hover row', 'hover row selected', 'hover row sound',
    'icon cell disabled plain', 'icon cell disabled row', 'icon cell empty plain', 'icon cell empty row', 'icon cell no item',
    'icon cell normal plain', 'icon cell normal row', 'icon cell qty', 'icon cell qty label', 'icon cell runtime',
    'icon cell selected plain', 'icon cell selected row', 'icon cell silent', 'icon cell wide', 'item frame', 'item frame have',
    'item grid', 'item grid bare', 'item grid drag', 'item grid kit', 'item grid runtime', 'item grid slot bg', 'item icon',
    'item icon anon', 'item icon runtime', 'item slot', 'label anon', 'label bold', 'label caption', 'label captionLight',
    'label cardCaption', 'label default', 'label disabled', 'label display', 'label error', 'label fieldLabel', 'label formCaption',
    'label formError', 'label gold', 'label have', 'label heading', 'label heading no max lines', 'label heading wrap off',
    'label info', 'label max lines 0', 'label message', 'label muted', 'label note', 'label optionDetail', 'label optionName',
    'label outOfStock', 'label panelTitle', 'label propKey', 'label propValue', 'label quantity', 'label rowBadge', 'label rowName',
    'label rowSub', 'label runtime colour', 'label secondary spaced', 'label section', 'label setting', 'label settingHead',
    'label spaced 1.8', 'label stock', 'label strong', 'label subtitle', 'label success', 'label summary', 'label text',
    'label tileName', 'label tipDesc', 'label tipId', 'label tipName', 'label tipStat', 'label warning', 'label zero spacing',
    'label zero spacing float', 'list button', 'list button selected', 'list button selected mask', 'number field', 'on_off 0',
    'on_off 1', 'option row', 'option row selected', 'option row sound', 'panel dark', 'panel full', 'panel hud',
    'panel padding dict', 'panel row', 'panel row normal', 'panel row runtime', 'panel row selected', 'panel row static',
    'panel secondary', 'panel simple', 'panel title', 'panel tooltip', 'panel well', 'progress', 'progress flex',
    'progress memories', 'property row', 'quality frame', 'quality frame default', 'row action', 'row action destructive',
    'row action primary', 'row badge', 'row text', 'row text name only', 'scroll list', 'scroll list flex', 'scroll list well',
    'search field', 'section', 'separator content', 'separator fancy', 'separator footer', 'separator form', 'separator header',
    'separator id', 'separator margins', 'separator panel', 'separator vertical', 'setting row', 'spacer', 'spinner', 'status line',
    'status line wrap', 'status line wrap max 0', 'subtitle', 'tab primary 0', 'tab primary 1', 'tab primary 2', 'tab primary 3',
    'tab primary 4', 'tab primary 5', 'tab tertiary 0', 'tab tertiary 1', 'tab tertiary 2', 'tab tertiary 3', 'text field',
    'text field filter look', 'text field flex', 'text field full width', 'text field vanilla look', 'tile complete',
    'tile default', 'tile empty', 'tile selected', 'title', 'tooltip', 'tooltip panel', 'tooltip panel quality', 'value box',
    'value box flex', 'value box padding',
])


def snapshot_digests(items):
    """{group: (count, sha256 prefix of the ordered items)}"""
    import hashlib
    out = {}
    for g, lst in items.items():
        h = hashlib.sha256()
        for name, txt in lst:
            h.update(name.encode("utf8") + b"\x00" + txt.encode("utf8") + b"\x00")
        out[g] = (len(lst), h.hexdigest()[:20])
    return out


def snapshot_prefix_digest(lst, n):
    import hashlib
    h = hashlib.sha256()
    for name, txt in lst[:n]:
        h.update(name.encode("utf8") + b"\x00" + txt.encode("utf8") + b"\x00")
    return h.hexdigest()[:20]


# (item count, sha256 prefix) per group, recorded from the kit 1.3 file (blob 988889603a0f, 2026-09-29) by --print-snapshot
SNAP13 = {
    'Appends.text': (1, '0a9adac746090a3b4df4'), 'Shell.text': (1, '70be127d89413485205d'),
    'allowed_colors': (1, '5c6e9536f3c7f3cd9770'), 'assert_page_size': (1, '46e253dd497e7ad66c2f'),
    'bar': (3, '9a74b847191b9c9d893a'), 'build_samples 1.3': (223, '56aae2f64f6ea746d9dc'), 'button': (49, 'd55483f18d55f0b907a1'),
    'button_row': (5, '58a0dd507ddc358a0c4f'), 'button_style': (98, 'f9277425095828eb5cb4'), 'card': (4, '0cdb0c5ee32e94872026'),
    'checkbox': (2, '6253c94daf41ae5ead25'), 'checkbox_row': (2, '767d70e0a66ac12b1395'),
    'checkbox_style': (1, 'dc0d51d7c51c49ec25f1'), 'choose': (1, 'db963919a1a707449ba3'),
    'clear_button_style': (1, '7e93fcf1aecd490c95b7'), 'close_button': (1, 'eb220859e9e1e1b9fa8c'),
    'color': (6, 'a3952ca25c3cc14ada05'), 'confirm_dialog': (2, '8efd403440bf0ea2e145'),
    'confirm_view': (6, '0eed4db5ed08cc83a32e'), 'dropdown': (2, 'c6d0f181d7e6c6c51259'),
    'dropdown_style': (2, '94dfc65060d83d7c6bfc'), 'fit': (1, '4988eb14e5d0ad3304d5'), 'for_percent': (1, 'f95caeff58c567e49f2a'),
    'for_pysource': (2, '8465ff5597589b9b3ca1'), 'fs': (10, 'f9e7bc010f2ba9a5db16'), 'gradient_label': (2, 'eedabfe07c3ae55d8628'),
    'group': (14, 'dc993c9136d9054afad2'), 'hover_row': (4, '89d27d3efd298ef7c98a'), 'icon_cell': (20, '309fba11aef0e10a0eb4'),
    'item_frame': (3, 'cf083441647ef73fef0f'), 'item_grid': (4, 'e97eb65b8adfa4069712'),
    'item_grid_java_is_safe': (2, '72e4881ba9dc37fdc16b'), 'item_grid_style': (2, 'c3eebfc5c97ac0f767dd'),
    'item_icon': (3, '81f425a1a2248fdcb923'), 'item_slot': (2, '81e3429e17825ae69d51'), 'java_append': (3, 'add09461c6e9d9253e55'),
    'java_expr': (1, '77170e0ef4cf680ff29e'), 'java_field': (1, 'eb7fd2ce86c1639ca483'),
    'java_grid_fill': (1, 'f6fc081457c57d904c8d'), 'java_grid_methods': (2, '96898090fc9b44044b34'),
    'java_lit': (1, 'a061966e494fff2f3143'), 'java_ref_style': (1, 'c726c220dcaa632b45b5'), 'java_set': (7, '62a4f4d9e27983bd3ca7'),
    'java_status_methods': (4, 'bf5739c4f3511338e514'), 'label': (171, '9b65963359c3422c08ea'),
    'list_button': (4, 'f6ea03a66b50a830bc9d'), 'list_button_style': (2, '4bd4c149efd21d3c13d6'),
    'norm_color': (5, '5b774e4a91c6dc9a8d8f'), 'on_off': (2, 'db928a3da7b0b1b60498'), 'option_row': (4, '69c8730b31bdd7057b09'),
    'option_style': (2, '46e2c809adf89f7b2ab1'), 'page_shell': (8, 'fdd915555e40795666cf'), 'pager': (4, '208491816c0b5a620bbe'),
    'panel': (16, '61822fe7c113746ac1f8'), 'panel_row': (7, 'c3c8672094ab56e83f27'), 'panel_title': (2, 'b88651201d9fc297d197'),
    'patch': (8, '0f0624524ab083b453f6'), 'probe pages 1-18': (18, '69220672befcf090fb50'),
    'probe pages 1-18 prefix': (18, '7e1ccc1ae8dd7a2d650c'), 'progress': (3, '666c4cd11aba59e718de'),
    'property_row': (2, '4a4de278ccf74fd14ed6'), 'quality_frame': (12, '5f6f4511b3f6375d4375'),
    'render': (1, '1d3e5202aaec8d82f123'), 'row_action': (4, 'ccb913493bb935767297'), 'row_badge': (2, '812b83408bb5350b846e'),
    'row_style': (3, '61cf739df6968309f26c'), 'row_text': (3, '6d6e2eb6bbff3b04ba21'), 'scalars': (99, 'ffc38bb4f180f0d6c7b7'),
    'scroll_list': (4, 'fa5e8b909d303f767785'), 'scrollbar_style': (2, '3788dcd2b517ad242b16'),
    'search_field': (2, '75736315832b16faca12'), 'search_icon': (1, 'fd8570de62c415bde86d'), 'section': (2, 'dad9f55c7c4f3233597b'),
    'separator': (14, 'f46a3e288053699c3f03'), 'setting_row': (2, 'aaf2816ad0da971786d8'), 'sounds': (6, '104022aa2d39a3c628d4'),
    'spacer': (4, '682327923d7a4b12c95f'), 'spinner': (2, '990b403d2637d79aac42'), 'status_line': (4, 'fcf7749a610e4139ef29'),
    'subtitle': (2, '8cae9a303192c02dcfe4'), 'tab_row': (3, 'c73ef930ce4c367a0cdc'), 'table BUTTONS': (4, '551f80e06aa3767fdecd'),
    'table BUTTON_SIZES': (3, '2155c6a21539eacbf9c4'), 'table CLIENT_DOCS': (5, '5cd277fe3fecaa02514e'),
    'table COLOR': (80, 'f6c58e198772132ecff7'), 'table CONFIRM_PANELS': (3, '9d0db9fd424eb890b6ba'),
    'table DOCS': (35, 'c7d7718cbac012e9024f'), 'table FIELD_LOOKS': (3, '6ce4287f55b87622958a'),
    'table FONTS': (2, 'd6b5722e28ede2e53fdd'), 'table ICON_CELL_LOOKS': (2, '70188a6bdbb8d014cc72'),
    'table ICON_CELL_STATES': (4, 'b96e2d493b9874df9270'), 'table LABELS': (42, 'c537c067258fdebb465e'),
    'table LABEL_MORE': (5, 'c283be05e24d7bcf87b2'), 'table PANELS': (4, '0ff35b9fb8e2cbacce83'),
    'table PANEL_KINDS': (8, 'f778d96c57c1b9bd47aa'), 'table PROBE_BASE': (3, 'ba92455962736738ce8e'),
    'table QUALITY': (11, 'ca02af4bbdcf354f91dc'), 'table QUALITY_SLOT': (11, 'fb60fc6bdd8e427c3086'),
    'table QUALITY_TIP': (11, 'dbeceb9e640a4a57cbb2'), 'table RARITY': (7, '65f32f7a715d98054a51'),
    'table RARITY_ORDER': (7, 'b22c76b667eb6f935a96'), 'table RARITY_WYNN': (7, '5760e693a3e98bc23c99'),
    'table READABLE': (4, '8524afb81495d518a2e0'), 'table SEPARATORS': (7, '40fe2b3d900311d85a77'),
    'table SND': (10, '9c54a89171d0e5758153'), 'table SOUNDS': (6, '0e46ec88c5d7e3da9b6f'),
    'table STATUS': (3, '6ca23e992245983e35e7'), 'table STATUS_INFO': (2, '20dc551f2dfd3218d7fe'),
    'table TEX': (87, 'f657e99a58fd029b37fb'), 'table TILE_STATES': (4, 'bae9cc985f96471224f1'),
    'table UNVERIFIED': (16, '29547c0f596bf28c2c7c'), 'table _COLOR_SRC': (80, '36bb8cc66549df56aa2a'),
    'table checks': (276, 'f1edce1309db7ba9001d'), 'text_field': (8, '13021d1abf0800e50524'),
    'text_style': (8, 'b48b7f0988c588546a49'), 'tile': (5, '359e68fc2720b64d071a'), 'title_label': (2, '66331ac83448be81f31a'),
    'title_style': (1, '8d0e5625a5b345c261e2'), 'tooltip': (1, '415fc26c575482235df9'),
    'tooltip_panel': (14, 'ffcbb62a122861aa6c24'), 'tooltip_style': (1, 'e9ac3ddd3c124a1bcc9b'),
    'value_box': (2, '7d74e0df8f5256831597'), 'vanilla scale': (16, 'fc4924b42023b50b07c2'),
}


def phase_snapshot():
    items = snapshot_items()
    if SNAP13 is None:
        FAILS.append("SNAP13 is empty: the kit 1.3 snapshot was never recorded")
        return items
    for g, (n, dig) in sorted(SNAP13.items()):
        lst = items.get(g)
        if lst is None:
            FAILS.append("snapshot: group %r is gone (kit 1.3 had %d items)" % (g, n))
            continue
        if g.startswith("table "):
            check(len(lst) >= n and snapshot_prefix_digest(lst, n) == dig,
                  "snapshot: the first %d entries of %s changed (kit 1.3 entries must stay, new ones go at the end)" % (n, g))
        else:
            check(len(lst) == n and snapshot_prefix_digest(lst, n) == dig,
                  "snapshot: %s output changed (%d items now, %d in kit 1.3) - kit 1.4 is additive only" % (g, len(lst), n))
    extra = sorted(set(items) - set(SNAP13))
    check(not extra, "snapshot: groups the frozen generator does not know: %s" % extra)
    return items


def main():
    if "--print-snapshot" in sys.argv:
        UI.verify(quiet=True)
        d = snapshot_digests(snapshot_items())
        print("SNAP13 = {")
        for g in sorted(d):
            print("    %r: %r," % (g, d[g]))
        print("}")
        print("SNAP_SAMPLES13 = %r" % sorted(build_samples()))
        return
    if "--snapshot-dump" in sys.argv:
        path = os.path.abspath(arg("--snapshot-dump"))
        if not path.lower().startswith((os.path.join(HERE, "dev", "scratch") + os.sep).lower()):
            raise SystemExit("--snapshot-dump writes only inside tools/dev/scratch/")
        UI.verify(quiet=True)
        import json
        json.dump(snapshot_items(), open(path, "w", encoding="utf8"), indent=0)
        print("wrote", path)
        return
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
        phase_snapshot()                      # kit 1.4: every kit 1.3 builder output byte-identical (SNAP13)
        phase_structure()
        samples = phase_builders()
        phase_kit13(samples)
        phase_kit14(samples)
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
