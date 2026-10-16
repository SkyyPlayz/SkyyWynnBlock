"""Harness for SkyyCollections 0.2.18 (TIER TAGS round T1: the tagged description of every id tools/tier_tags.py gives SkyyCollections;
tools/collections_0_2_18_patch.py). Build first:
    python tools/collections_0_2_18_patch.py && python SkyyCollections/build_skyycollections_0.2.18.py

    python SkyyCollections/test_skyycollections_0.2.18.py [--jar <SkyyCollections-0.2.18.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.17 -> 0.2.18: SkyyCollectionsPlugin.setup (version + ready line) + the config kit's version texts (CfgFn.opExport,
                CfgRows.header) only; non-class entries: manifest.json +
                Server/Languages/en-US/server.lang
  TT   tags     the jar's server.lang read back: every tier_tags id of SkyyCollections has items.<id>.description AND the server. twin
                (same value), the value = "T<n> <Noun> - <vanilla text>" / "T<n> <Noun>" (the vanilla text read again from Assets.zip
                here, independently of the build), the 34 tiered Enchanted lines = "tag - <0.2.17 text>", every other 0.2.17 line
                byte-identical, no key twice, no line break inside a value; the probes P1 / P1b / control / P2 exactly as listed; no item
                JSON over a vanilla id (Server/Item/Items/ holds only our Skyy_Ench_ items); tools/ci/langdup.py over the SET jars with
                this jar in place of 0.2.17 = 0 FAIL; the ready line names the 80 VISIBLE tags (108 written minus the 28 seeds DynamicSeasons
                shadows: tier_tags.shadowed); hides / leathers untagged; vanilla's "[TMP]" placeholder dropped after the tag
  D    live     0.2.17's live phase (= 0.2.16's start twice on a scratch COPY of the live Skyy_SkyyCollections): nothing new written
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("tc0217", os.path.join(HERE, "test_skyycollections_0.2.17.py"))
T17 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T17)

VERSION = "0.2.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.17.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "tiertags1", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = T17.LIVE_DIR
EXPECT = {"SkyyCollectionsPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}   # + the config kit's VERSION texts
ADDED = []
LANG = "Server/Languages/en-US/server.lang"
P1 = {"Ingredient_Bar_Copper": "T2 Copper - ", "Wood_Oak_Trunk": "T2 Copper - ", "Ore_Copper": "T2 Copper - ", "Plant_Crop_Carrot_Item": "T3 Iron - "}
P1B = ("Wood_Azure_Trunk", "Wood_Crystal_Trunk", "Wood_Ice_Trunk", "Wood_Poisoned_Trunk", "Wood_Spiral_Trunk", "Wood_Stormbark_Trunk",
       "Wood_Windwillow_Trunk")
CTRL = "Plant_Crop_Wheat_Item"
P2 = "Plant_Crop_Lettuce_Item"      # moved off the seeds (DynamicSeasons overrides every Plant_Seeds_* Description key)
P2_CMP = "Plant_Crop_Corn_Item"


def untmp(t):
    return t[len("[TMP]"):].lstrip() if t.startswith("[TMP]") else t

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            return self.check(sorted(got) == sorted(["manifest.json", LANG]), "C: non-class entries changed = manifest.json + %s: %s" % (LANG, sorted(got)))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def lang_rows(text):
    rows = []
    for line in text.split("\n"):
        if line.strip() and not line.startswith("#"):
            k, v = line.split("=", 1)
            rows.append((k.strip(), v.strip()))
    return rows


def run_tags(out, jar, scratch, _home):
    import tier_tags as TT
    import skyyench as EN
    import serverjar
    import langdup as LD
    K = HK.Child(out)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    new_t, old_t = zn.read(LANG).decode("utf-8"), zo.read(LANG).decode("utf-8")
    K.check("\r" not in new_t and new_t.endswith("\n"), "TT: LF lines, final newline")
    rows, orows = lang_rows(new_t), lang_rows(old_t)
    keys = [k for k, _v in rows]
    K.check(len(keys) == len(set(keys)), "TT: no key twice in server.lang (%d lines, %d keys)" % (len(keys), len(set(keys))))
    d, od = dict(rows), dict(orows)
    ids = TT.ids_for("SkyyCollections")
    K.eq(len(ids), 108, "TT: tier_tags gives SkyyCollections 108 ids")
    K.check(not any(("items.Ingredient_%s_%s.description" % (a, b)) in d for a in ("Hide", "Leather") for b in ("Soft", "Light", "Medium", "Heavy", "Scaled", "Storm", "Dark", "Prismic")),
            "TT: no hide / leather description key (left untagged)")
    # the vanilla text, read again here (the cached Assets.zip copy, read-only)
    with zipfile.ZipFile(serverjar.assets_zip()) as z:
        vl = {}
        for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                vl[k.strip()] = v.strip()
    bad, ench_ok = [], 0
    for i in ids:
        a, b = d.get("items.%s.description" % i), d.get("server.items.%s.description" % i)
        tag = TT.tag_for(i)
        if a is None or a != b:
            bad.append("%s: twins %r / %r" % (i, a, b))
            continue
        if i.startswith(EN.PREFIX):
            want = tag + " - " + od["items.%s.description" % i]
            ench_ok += a == want
        elif i == P2:
            want = tag + "\\n" + untmp(vl["items.%s.description" % i])
        else:
            vt = untmp(vl.get("items.%s.description" % i, ""))
            want = tag + " - " + vt if vt else tag
        if a != want:
            bad.append("%s: %r != %r" % (i, a[:80], want[:80]))
    K.check(not bad, "TT: every tagged id has the right text in both keys (%d bad: %s)" % (len(bad), bad[:4]))
    K.eq(ench_ok, 17, "TT: the 17 tiered Enchanted lines = tag - <0.2.17 text>")
    # every other 0.2.17 line is unchanged; the only new keys are the vanilla material twins
    changed = sorted(k for k in od if d.get(k) != od[k])
    want_changed = sorted(p + "items.%s.description" % i for i in ids if i.startswith(EN.PREFIX) for p in ("", "server."))
    K.eq(changed, want_changed, "TT: the changed 0.2.17 lines = the 34 tiered Enchanted description twins only")
    added = sorted(set(d) - set(od))
    K.eq(added, sorted(p + "items.%s.description" % i for i in ids if not i.startswith(EN.PREFIX) for p in ("", "server.")),
         "TT: the added lines = the 91 vanilla material description twins")
    K.check(all(d[k] == od[k] for k in ("items.Skyy_Ench_Cobblestone.description", "items.Skyy_Ench_Rubble.description")),
            "TT: Enchanted Cobblestone / Rubble untouched (no tier)")
    # probes
    for i, pre in P1.items():
        K.check(d["items.%s.description" % i].startswith(pre) and len(d["items.%s.description" % i]) > len(pre) + 5 and vl.get("items.%s.description" % i),
                "TT P1: %s = %r... and vanilla HAS its own description key" % (i, pre))
    K.check(d["items.%s.description" % CTRL] == "T2 Copper" and not vl.get("items.%s.description" % CTRL), "TT control: Wheat = just 'T2 Copper' (vanilla has none)")
    K.check(d["items.%s.description" % P2].startswith("T2 Copper\\nInstantly restores ") and vl["items.%s.description" % P2].startswith("[TMP] "),
            "TT P2: Lettuce = T2 Copper\\nInstantly restores ... (vanilla's [TMP] dropped)")
    K.check(d["items.%s.description" % P2_CMP].startswith("T3 Iron - Instantly restores "), "TT P2 compare: Corn = T3 Iron - Instantly restores ...")
    K.check(not any("[TMP]" in d["items.%s.description" % i] for i in ids), "TT: no tagged value keeps vanilla's [TMP] placeholder")
    K.check(sum(1 for i in ids if vl.get("items.%s.description" % i, "").startswith("[TMP]")) == 12, "TT: [TMP] was on the 12 crop items")
    K.eq(d["items.Plant_Seeds_Wheat.description"], "T2 Copper - Grows Wheat", "TT: Wheat Seed Bag key still written (shows with DynamicSeasons off)")
    K.check(all(TT.shadowed(i) for i in TT.ids_in("seed")) and len(TT.visible_ids_for("SkyyCollections")) == 80,
            "TT: tier_tags marks the 28 seeds shadowed; 80 visible")
    with zipfile.ZipFile(serverjar.assets_zip()) as z:
        import json
        ip = dict((os.path.basename(n)[:-5], n) for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        blank = sorted(i for i in ids if i in ip and (json.loads(z.read(ip[i]).decode("utf-8-sig")).get("TranslationProperties") or {}).get("Description", None) == "")
    K.eq(blank, sorted(P1B), "TT P1b: the 7 logs whose vanilla Description key is blank")
    K.check(all(d["items.%s.description" % i] == TT.tag_for(i) for i in P1B), "TT P1b: their keys are written (bare tag)")
    # jar entries: no vanilla item JSON, no pack id
    items = [n for n in zn.namelist() if n.startswith("Server/Item/Items/")]
    K.check(items and all(os.path.basename(n).startswith(EN.PREFIX) for n in items), "TT: Server/Item/Items/ holds only our Skyy_Ench_ items (%d)" % len(items))
    # langdup over the SET with this jar
    jars = [(m, v, (jar if m == "SkyyCollections" else p)) for m, v, p in LD.set_jars()]
    have = [j for j in jars if os.path.isfile(j[2])]
    fails, warns, st = LD.check(have)
    K.check(not fails, "TT: langdup over %d SET jars with 0.2.18 = 0 FAIL (%s)" % (len(have), fails[:3]))
    K.notes.append("TT: langdup %d jars, %d keys, %d WARN (%s)" % (st["jars"], st["keys"], len(warns), "; ".join(w[:90] for w in warns[:3])))
    # the ready line
    plug = zn.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(b"0.2.18 ready" in plug and b"; tier tags on 80 item descriptions" in plug, "TT: the ready line = 0.2.18 + the tier tag count")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("tags", run_tags), ("live", T17.run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
