#!/usr/bin/env python3
"""SkyWynn CLASS tree node icons - one 64 x 64 icon per node of the 8 class trees (DRAFT v1), same family as the approved Mining set.

Skyy (2026-10-23, the Mining node icons): "i love it!" -> the same style for the class trees. Every node shows what it DOES (its hook /
effect text): the ability or body part it changes + one accent glyph for WHAT changes (class_kit.CLASS_CATS colour code).
  - Free-row ABILITY nodes reuse the approved ability icons (art/ability-icons/Common/Icons/Abilities/<Class>/<Ability>.png) - not redrawn,
    no new file; the manifest names the reused file.
  - MODIFIER-type nodes (hook 'mod', Skyy 2026-10-23 docs/answered/classes.md: to be cut / renamed in a later round) get the MOD MARK
    (a small pink rune diamond, top-left) - added HERE by the runner, so every 'mod' node carries it and no other node does.
ORIGINAL pixels only (the painter of tools/art/make_tree_node_icons.py, imported read-only; drawings in tools/art/node_icons/class_<Class>.py).
The node list is READ from tools/trees_v3_data.py (kind 'class'); the build stops if a node has no picture or a picture names a node that is gone.

Writes:
  art/tree-node-icons/Common/Icons/ItemsGenerated/Skyy_NodeIcon_<Class>_<B><R>[a|b|c|Free].png   64 x 64 RGBA, hard alpha
  art/tree-node-icons/sheet-class-<class>.png     review sheet per class
  art/tree-node-icons/manifest-classes.json       every class node -> icon (own file or reused ability icon), category, mod flag, what it shows

Re-laid-out trees (Skyy 2026-10-23: the class trees are being redesigned): a node whose key the ROWS do not name takes the drawing made
for the same EFFECT (manifest-classes.json effect_sig = hook + name; e.g. 'mod:Challenge/Duration|Duration'), printed as "<- drawing of";
nodes with no matching drawing stop the build (add a ROWS line), drawings whose node is gone are listed as unused.

Run:   python tools/art/make_class_node_icons.py [--class Warrior]   (no --class = all 8; deterministic)
       python tools/art/make_class_node_icons.py --check [--class C]  (build twice, compare bytes, write nothing)
"""
import importlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_tree_node_icons as T
import emblem_png as P
from node_icons import class_kit as K

ROOT = T.ROOT
OUT = T.OUT
V3D = T.V3D
CLASSES = ["Warrior", "Berserker", "Spellblade", "Monk", "Assassin", "Archer", "Mage", "Priest"]
ABIL_DIR = os.path.join(ROOT, "art", "ability-icons")


def class_nodes(name):
    """[(key, branch, row, kind free|up|cap, id, name, max, text, hook)] in page order"""
    t = V3D.tree(name)
    assert t["kind"] == "class", name
    out = []
    for bn, b in enumerate(t["branches"]):
        for r in b["rows"]:
            if r.get("free"):
                f = r["free"]
                out.append(("%s.b%d.r%d.free" % (name, bn + 1, r["r"]), b["name"], r["r"], "free", "r%d.free" % r["r"], f["name"], 0,
                            f.get("text", ""), f.get("hook")))
            for u in r["ups"]:
                out.append(("%s.b%d.%s" % (name, bn + 1, u["id"]), b["name"], r["r"], "cap" if r.get("cap") else "up", u["id"], u["name"], u["max"],
                            u["text"], u.get("hook")))
    return out


def is_mod(n):
    return bool(n[8]) and n[8][0] == "mod"


def rows_of(cls):
    return importlib.import_module("node_icons.class_" + cls).ROWS


def effect_sig(n):
    """what a node DOES, independent of its place: '<hook>|<name>' - e.g. 'mod:Challenge/Duration|Duration', 'fx:drMelee|Iron Skin',
    'abil:RallyingGuard|Rallying Guard'. Saved in manifest-classes.json so a drawing follows its node when the tree layout changes."""
    h = n[8]
    if not h:
        hp = "none"
    elif h[0] == "mod":
        hp = "mod:%s/%s" % (h[1], h[2])
    elif h[0] == "abil":
        hp = "abil:%s" % h[2]
    elif h[0] == "fx":
        hp = "fx:" + (h[1] if isinstance(h[1], str) else ",".join(str(c[0]) for c in h[1]))
    else:
        hp = str(h[0])
    return "%s|%s" % (hp, n[5])


def old_sigs(cls):
    """{effect sig: old node key} from the last written manifest-classes.json (the layout the drawings were made for)"""
    mpath = os.path.join(OUT, "manifest-classes.json")
    old_sigs.by_key = {}
    if not os.path.isfile(mpath):
        return {}, {}
    ents = json.load(open(mpath, encoding="utf8")).get("classes", {}).get(cls, {}).get("nodes", [])
    full, hook = {}, {}
    old_sigs.by_key = dict((e["key"], e.get("effect_sig")) for e in ents)
    for e in ents:
        if e.get("effect_sig"):
            full.setdefault(e["effect_sig"], []).append(e["key"])
            hook.setdefault(e["effect_sig"].split("|")[0], []).append(e["key"])
    return full, hook


def build(cls, relayout_report=None):
    nodes = class_nodes(cls)
    rows = rows_of(cls)
    have = [r[0] for r in rows]
    assert len(set(have)) == len(have), "a key twice in class_%s.ROWS" % cls
    byk = dict((r[0], r) for r in rows)
    # a node the ROWS do not name (the tree was re-laid out) takes the drawing made for the SAME effect (manifest effect_sig):
    # exact hook + name first, else the hook alone when only one old node had it. Its file stem follows the NEW key.
    full, hook = old_sigs(cls)
    used, missing = set(), []
    # 1) a node whose key AND effect are unchanged keeps its own drawing (the drawing belongs to the effect, not the place)
    moved = []
    for n in nodes:
        was = old_sigs.by_key.get(n[0])
        if n[0] in byk and (was is None or was == effect_sig(n)):
            used.add(n[0])
        else:
            moved.append(n)
    orig = dict(byk)
    for n in moved:
        byk.pop(n[0], None)
    for n in moved:
        sig = effect_sig(n)
        cand = [k for k in full.get(sig, []) if k in orig and k not in used] or                [k for k in hook.get(sig.split("|")[0], []) if k in orig and k not in used and len(hook[sig.split("|")[0]]) == 1]
        if cand:
            o = orig[cand[0]]; used.add(cand[0])
            byk[n[0]] = (n[0], K.stem_of(n[0])) + tuple(o[2:])
            if relayout_report is not None:
                relayout_report.append("%s <- drawing of %s (%s)" % (n[0], cand[0], sig))
        else:
            missing.append("%s (%s)" % (n[0], sig))
    if missing:
        raise SystemExit("class_%s: %d node(s) have no drawing (add a ROWS line): %s" % (cls, len(missing), "; ".join(missing)))
    unused = [k for k in have if k not in used and k not in [n[0] for n in nodes]]
    if unused and relayout_report is not None:
        relayout_report.append("unused drawings (node gone): " + ", ".join(unused))
    stems = [byk[n[0]][1] for n in nodes]
    assert len(set(stems)) == len(stems), "a file stem twice in " + cls
    out = []
    for n in nodes:
        r = byk[n[0]]
        assert r[2] in K.CLASS_CAT_HEX, r
        assert r[1] == K.stem_of(n[0]), (r[1], n[0])
        if isinstance(r[3], K.Reuse):
            assert n[3] == "free", "only a row's free ability reuses art: " + n[0]
            src = os.path.join(ABIL_DIR, r[3].rel)
            data = open(src, "rb").read()
            out.append((n, r, P.read_png(data), data))
        else:
            if n[3] == "free":
                h = n[8]
                assert not (h and h[0] == "abil"), "an ability node must reuse its approved icon: " + n[0]
            ic = r[3]()
            if is_mod(n):
                K.mod_mark(ic)
            img = ic.render()
            out.append((n, r, img, T.png_bytes(img)))
    return out


# ====================================================================== sheet
def build_sheet(cls, built):
    COLS, CW, CH = 4, 316, 236
    cc = T.hx(K.PALN["cls_" + cls][4])
    branches = []
    for b in built:
        if not branches or branches[-1][0] != b[0][1]:
            branches.append((b[0][1], []))
        branches[-1][1].append(b)
    W = 24 + COLS * CW + 8
    hb = sum(44 + ((len(items) + COLS - 1) // COLS) * CH + 14 for _, items in branches)
    strip_h = 60 + len(branches) * 44 + 30 + len(branches) * 60 + 40
    H = 176 + hb + strip_h + 40
    cv = T.Canvas(W, H, T.BG)
    nmod = sum(1 for b in built if is_mod(b[0])); nre = sum(1 for b in built if isinstance(b[1][3], K.Reuse))
    cv.text(24, 20, "SKYWYNN %s CLASS TREE - NODE ICONS - DRAFT V1" % cls.upper(), cc, 4)
    cv.text(24, 60, "%d NODES: %d NEW + %d REUSED ABILITY ICONS. %d MODIFIER-TYPE (PINK CORNER MARK)." % (len(built), len(built) - nre, nre, nmod),
            T.DIM, 2)
    cv.text(24, 84, "EACH CELL: 2X, 1X, ON THE DISC AT 100 % + 150 %. ACCENT = WHAT THE NODE CHANGES:", T.DIM, 2)
    y = 108; x = 24
    for cid, lab, hexc, _why in K.CLASS_CATS:
        lab2 = lab.split(" (")[0]
        if x + 30 + len(lab2) * 6 > W - 20:
            x = 24; y += 22
        cv.rect(x, y, x + 14, y + 14, T.hx(hexc)); x = cv.text(x + 20, y + 4, lab2, T.INK, 1) + 22
    y += 22
    cv.rect(24, y, 38, y + 14, T.hx(K.MOD_HEX)); x = cv.text(44, y + 4, "MOD MARK = MODIFIER-TYPE NODE (HOOK MOD, TO BE CUT / RENAMED)", T.INK, 1) + 22
    cv.rect(x, y, x + 14, y + 14, cc); cv.text(x + 20, y + 4, "REUSED = THE APPROVED ABILITY ICON (NOT REDRAWN)", T.INK, 1)
    y = 166
    for bname, items in branches:
        rows = (len(items) + COLS - 1) // COLS
        h = 44 + rows * CH
        cv.rect(16, y, W - 8, y + h, T.PANEL)
        cv.rect(16, y, W - 8, y + 3, cc)
        cv.text(28, y + 14, "BRANCH %s" % bname.upper(), cc, 2)
        for k, (n, r, img, data) in enumerate(items):
            cx = 28 + (k % COLS) * CW; cy = y + 44 + (k // COLS) * CH
            cv.checker(cx, cy, 136, 136, (52, 56, 74), (44, 48, 64))
            cv.blit(img, cx + 4, cy + 4, 2)
            cv.rect(cx + 144, cy, cx + 216, cy + 72, (16, 20, 30))
            cv.blit(img, cx + 148, cy + 4, 1)
            cv.rect(cx + 144, cy + 78, cx + 264, cy + 136, (16, 20, 30))
            T.node_disc(cv, cx + 150, cy + 91, 32, img, ring=cc)
            T.node_disc(cv, cx + 196, cy + 83, 48, img, ring=cc)
            cv.rect(cx + 272, cy, cx + 286, cy + 14, T.hx(K.CLASS_CAT_HEX[r[2]]))
            cv.text(cx + 272, cy + 20, "R%d" % n[2], T.DIM, 1)
            if is_mod(n):
                cv.rect(cx + 272, cy + 32, cx + 286, cy + 46, T.hx(K.MOD_HEX)); cv.text(cx + 270, cy + 50, "MOD", T.hx(K.MOD_HEX), 1)
            reuse = isinstance(r[3], K.Reuse)
            tag = "ABILITY - REUSED" if reuse else {"free": "FREE PASSIVE", "cap": "CAPSTONE"}.get(n[3], "UPGRADE")
            cv.text(cx, cy + 144, T.clean(n[5]).upper()[:25], T.INK, 2)
            cv.text(cx, cy + 164, "%s  %s  %s" % (n[0].split(".", 1)[1].upper(), tag, ("MAX %d" % n[6]) if n[6] else ""), cc if reuse else T.DIM, 1)
            txt = n[7] or ("REUSED: " + r[3].cls + "/" + r[3].ability + ".png" if reuse else "")
            for li, ln in enumerate(T.wrap(T.clean(txt), 48)[:5]):
                cv.text(cx, cy + 178 + li * 10, ln.upper(), (200, 206, 220), 1)
        y += h + 14
    cv.rect(16, y, W - 8, y + strip_h, (11, 14, 22))
    cv.text(28, y + 14, "AT REAL SIZE ON THE NODE DISC (CLASS COLOUR RING = LEARNT) - 100 %", T.INK, 2)
    yy = y + 40
    for bname, items in branches:
        for k, b in enumerate(items):
            T.node_disc(cv, 28 + k * 38, yy, 32, b[2], ring=cc)
        yy += 44
    cv.text(28, yy + 6, "150 %", T.INK, 2)
    yy += 30
    for bname, items in branches:
        for k, b in enumerate(items):
            T.node_disc(cv, 28 + k * 54, yy, 48, b[2], ring=T.GOLDR if k % 3 == 1 else (T.LOCKR if k % 3 == 2 else cc))
        yy += 60
    return cv.png()


# ====================================================================== write
def write(classes):
    os.makedirs(os.path.join(OUT, T.ICON_DIR_REL), exist_ok=True)
    mpath = os.path.join(OUT, "manifest-classes.json")
    man = json.load(open(mpath, encoding="utf8")) if os.path.isfile(mpath) else {}
    man.update({
        "what": "SkyWynn CLASS tree node icons (one 64 x 64 item icon per Skill Trees 3 class node) - DRAFT v1, not wired in yet",
        "generator": "tools/art/make_class_node_icons.py (drawings: tools/art/node_icons/class_<Class>.py, parts: node_icons/class_kit.py)",
        "deterministic": True, "original_pixels": True,
        "same_rules_as": "manifest.json (the Mining set): 64 x 64, hard alpha, 1 px outline, light top left, no pure black / white",
        "categories": dict((c[0], {"label": c[1], "accent": c[2], "why": c[3]}) for c in K.CLASS_CATS),
        "mod_mark": {"accent": K.MOD_HEX, "what": "small pink rune diamond in the top-left corner = a modifier-type node (hook 'mod'); "
                     "Skyy 2026-10-23 (docs/answered/classes.md): those are cut / renamed in a later round"},
        "reused": "free-row ability nodes keep their approved ability icon (art/ability-icons/<file>) - no Skyy_NodeIcon file is made for them",
        "item_json": {"path": "Server/Item/Items/Utility/<icon_id>.json", "icon": "Icons/ItemsGenerated/<icon_id>.png",
                      "png_in_jar": "Common/Icons/ItemsGenerated/<icon_id>.png", "see": "README.md section 3 (same wiring as Mining)"},
    })
    trees = man.get("classes", {})
    for cls in classes:
        rep = []
        built = build(cls, rep)
        for line in rep:
            print("  %s: %s" % (cls, line))
        files, nodes = [], []
        for n, r, img, data in built:
            reuse = isinstance(r[3], K.Reuse)
            ent = {"key": n[0], "saved_key": ("Class." + n[0]) if n[3] != "free" else "", "tree": cls, "branch": n[1], "row": n[2], "kind": n[3],
                   "id": n[4], "name": n[5], "max": n[6], "effect": n[7], "hook": (n[8][0] if n[8] else None), "effect_sig": effect_sig(n), "modifier": is_mod(n),
                   "category": r[2], "accent": K.CLASS_CAT_HEX[r[2]], "shows": r[4]}
            if is_mod(n):
                ent["hook_mod"] = "%s/%s" % (n[8][1], n[8][2])
            if reuse:
                ent.update({"icon_id": None, "reused_ability_icon": "art/ability-icons/" + r[3].rel, "file": None,
                            "bytes": len(data), "sha256": T.sha(data)})
            else:
                rel = T.icon_rel(cls, r[1])
                with open(os.path.join(OUT, rel), "wb") as fh:
                    fh.write(data)
                files.append({"path": rel, "bytes": len(data), "sha256": T.sha(data)})
                ent.update({"icon_id": T.icon_id(cls, r[1]), "file": rel})
            nodes.append(ent)
        sname = "sheet-class-%s.png" % cls.lower()
        with open(os.path.join(OUT, sname), "wb") as fh:
            fh.write(build_sheet(cls, built))
        trees[cls] = {"count": len(nodes), "new_icons": len(files), "reused_ability_icons": len(nodes) - len(files),
                      "modifier_nodes": sum(1 for e in nodes if e["modifier"]), "sheet": sname, "nodes": nodes, "files": files}
        print("%-10s %d nodes: %d new icons, %d reused ability icons, %d modifier-marked -> %s"
              % (cls, len(nodes), len(files), len(nodes) - len(files), trees[cls]["modifier_nodes"], sname))
    man["classes"] = dict((c, trees[c]) for c in CLASSES if c in trees)
    man["totals"] = {"nodes": sum(v["count"] for v in man["classes"].values()), "new_icons": sum(v["new_icons"] for v in man["classes"].values()),
                     "reused_ability_icons": sum(v["reused_ability_icons"] for v in man["classes"].values()),
                     "modifier_nodes": sum(v["modifier_nodes"] for v in man["classes"].values())}
    with open(mpath, "w", newline="\n") as fh:
        json.dump(man, fh, indent=1)
        fh.write("\n")


def main():
    a = sys.argv[1:]
    classes = [a[a.index("--class") + 1]] if "--class" in a else CLASSES
    for c in classes:
        assert c in CLASSES, c
    if "--check" in a:
        for c in classes:
            one = [b[3] for b in build(c)]; two = [b[3] for b in build(c)]
            assert one == two, "not deterministic: " + c
            print("OK: %s %d icons, two builds byte-identical" % (c, len(one)))
        return
    write(classes)


if __name__ == "__main__":
    main()
