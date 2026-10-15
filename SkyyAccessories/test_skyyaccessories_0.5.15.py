"""Harness for SkyyAccessories 0.5.15 (THE WORKBENCH TAB ORDER, CLIENT SIDE: every recipe of the tab gets ItemLevel 1 .. 51 in the wanted
order; tools/accessories_0_5_15_patch.py).
Build first: python tools/accessories_0_5_15_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.15.py

    python SkyyAccessories/test_skyyaccessories_0.5.15.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.5.14 -> 0.5.15: the kit's version texts only; non-class entries: manifest.json + exactly the 51 tab items' JSONs
  ORD the client-sort key, on the JARS:
        - 0.5.14 -> 0.5.15 item JSONs: the ONLY difference is a new "ItemLevel" on the 51 recipes of the Workbench tab (ids, recipes,
          qualities, names, every other key byte-identical); no other item has an ItemLevel; lang / qualities / icons unchanged
        - the wanted order = the order the SERVER already sends (WbRank.ORDER of the 0.5.15 jar, loaded in the JVM, + the Omni Accessory)
          = Workbench Accessory I first, rarity tiers ascending, inside a tier the 0.5.13 cost ascending (WbRank.TIER)
        - every client-key candidate sorts the tab exactly into that order: ItemLevel; (rarity, ItemLevel); (ItemLevel, rarity); with a
          STABLE sort and with an UNSTABLE one (a .NET-style introsort, the kind that scrambled the ties) fed from the server order, the
          reverse order and 20 shuffles; ItemLevel values unique (no ties); the Lantern recipes (hidden until learned) keep their place
        - control: the 0.5.14 jar's keys DO tie (all ItemLevel 0) - the reason the client could ignore the server order
  AA  engine-access audit
NOT driven here: the native client (UNVERIFIED that its key is ItemLevel - Skyy's in-game look decides). No saved-data change -> no live phase.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, random, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.15"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.14.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0515", "harness")))
PKG = "com.skyy.accessories."
TAB_ID = "Workbench_SkyyAccessories"
OMNI = "Skyy_Accessory_Omni"
FIRST = "Skyy_Accessory_Workbench_T1"
QUAL = ["Skyy_Acc_Normal", "Skyy_Acc_Unique", "Skyy_Acc_Rare", "Skyy_Acc_Legendary"]
EXPECT = {          # the version text "0.5.15" only (the same three members every version bump changes, cf. 0.5.14's harness)
    "SkyyAccessoriesPlugin": ["~m setup"],
    "CfgRows": ["~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = []


def items_of(jar):
    z = zipfile.ZipFile(jar)
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            out[n] = z.read(n).decode("utf8")
    return out


def tab_ids(items):
    got = []
    for p, t in items.items():
        n = json.loads(t)
        r = n.get("Recipe") or {}
        if any(TAB_ID in (q.get("Categories") or []) for q in r.get("BenchRequirement") or []):
            got.append(os.path.basename(p)[:-5])
    return sorted(got)


def tab_paths():
    return sorted("Server/Item/Items/Utility/%s.json" % i for i in tab_ids(items_of(JAR)))


# C: the kit's compare allows only manifest.json among non-class entries - 0.5.15 also changes exactly the 51 tab item JSONs (checked
# byte for byte in ORD), so that one comparison gets those paths added to its expected list
_ChildBase = HK.Child


class _Child(_ChildBase):
    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(list(want) + tab_paths())
        return _ChildBase.eq(self, got, want, what)


HK.Child = _Child


def introsort(a, cmp):
    """the .NET Array.Sort / List.Sort algorithm (introsort: median-of-three quicksort, insertion sort at <= 16, heapsort at depth 0) -
    NOT stable: equal keys come out in an order that depends on the input, never on the server's intent"""
    a = list(a)

    def sw(i, j):
        a[i], a[j] = a[j], a[i]

    def sig(lo, i, j):
        if i != j and cmp(a[lo + i], a[lo + j]) > 0:
            sw(lo + i, lo + j)

    def ins(lo, n):
        for i in range(n - 1):
            t = a[lo + i + 1]
            j = i
            while j >= 0 and cmp(t, a[lo + j]) < 0:
                a[lo + j + 1] = a[lo + j]
                j -= 1
            a[lo + j + 1] = t

    def heap(lo, n):
        def down(i, m):
            d = a[lo + i - 1]
            while i <= m // 2:
                c = 2 * i
                if c < m and cmp(a[lo + c - 1], a[lo + c]) < 0:
                    c += 1
                if not cmp(d, a[lo + c - 1]) < 0:
                    break
                a[lo + i - 1] = a[lo + c - 1]
                i = c
            a[lo + i - 1] = d
        for i in range(n // 2, 0, -1):
            down(i, n)
        for i in range(n, 1, -1):
            sw(lo, lo + i - 1)
            down(1, i - 1)

    def part(lo, n):
        hi = n - 1
        mid = hi >> 1
        sig(lo, 0, mid)
        sig(lo, 0, hi)
        sig(lo, mid, hi)
        piv = a[lo + mid]
        sw(lo + mid, lo + hi - 1)
        l, r = 0, hi - 1
        while l < r:
            l += 1
            while cmp(a[lo + l], piv) < 0:
                l += 1
            r -= 1
            while cmp(piv, a[lo + r]) < 0:
                r -= 1
            if l >= r:
                break
            sw(lo + l, lo + r)
        if l != hi - 1:
            sw(lo + l, lo + hi - 1)
        return l

    def intro(lo, n, depth):
        while n > 1:
            if n <= 16:
                if n == 2:
                    sig(lo, 0, 1)
                    return
                if n == 3:
                    sig(lo, 0, 1)
                    sig(lo, 0, 2)
                    sig(lo, 1, 2)
                    return
                ins(lo, n)
                return
            if depth == 0:
                heap(lo, n)
                return
            depth -= 1
            p = part(lo, n)
            intro(lo + p + 1, n - p - 1, depth)
            n = p
    if len(a) > 1:
        intro(0, len(a), 2 * (int(math.log2(len(a))) + 1))
    return a


def run_order(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    L = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
    WR = JClass(PKG + "WbRank", loader=L)
    server = [str(x) for x in WR.ORDER] + [OMNI]
    tiers = [int(x) for x in WR.TIER]
    new, old = items_of(jar), items_of(OLD_JAR)
    tab = tab_ids(new)
    K.eq(tab, tab_ids(old), "ORD the same 51 recipes sit in the tab")
    K.check(len(tab) == 51 and sorted(server) == tab, "ORD the server order lists every tab recipe once (%d)" % len(server))
    # ---- 0.5.14 -> 0.5.15: only ItemLevel on the tab items
    K.eq(sorted(new), sorted(old), "ORD the same item files")
    changed = sorted(p for p in new if new[p] != old[p])
    K.eq(changed, sorted("Server/Item/Items/Utility/%s.json" % i for i in tab), "ORD exactly the 51 tab item JSONs changed")
    bad = []
    for p in changed:
        a, b = json.loads(old[p]), json.loads(new[p])
        lv = b.pop("ItemLevel", None)
        if "ItemLevel" in a or not isinstance(lv, int) or a != b or json.dumps(b, indent=2) != old[p]:
            bad.append(os.path.basename(p))
    K.eq(bad, [], "ORD each changed JSON = the 0.5.14 bytes + one ItemLevel key (recipes, costs, qualities, names untouched)")
    K.eq([os.path.basename(p) for p in new if p not in changed and "ItemLevel" in json.loads(new[p])], [], "ORD no other item has an ItemLevel")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    other = sorted(n for n in set(zn.namelist()) | set(zo.namelist()) if not n.endswith(".class") and not n.startswith("Server/Item/Items/")
                   and n != "manifest.json" and (n not in zo.namelist() or n not in zn.namelist() or zn.read(n) != zo.read(n)))
    K.eq(other, [], "ORD lang, qualities, icons, models: byte-identical")
    # ---- the wanted order
    node = dict((i, json.loads(new["Server/Item/Items/Utility/%s.json" % i])) for i in tab)
    lvl = dict((i, node[i]["ItemLevel"]) for i in tab)
    rar = dict((i, QUAL.index(node[i]["Quality"])) for i in tab)
    K.check(server[0] == FIRST and server[-1] == OMNI, "ORD wanted: Workbench Accessory I first, the Omni Accessory last")
    K.check(all(tiers[k] <= tiers[k + 1] for k in range(len(tiers) - 1)) and tiers[1:] == [rar[i] + 1 for i in server[1:-1]],
            "ORD wanted: rarity tiers ascending (WbRank.TIER = the item rarity)")
    K.eq([lvl[i] for i in server], list(range(1, 52)), "ORD ItemLevel = 1 .. 51 along the wanted order (unique: no ties)")
    cands = [("ItemLevel", lambda i: lvl[i]), ("rarity, ItemLevel", lambda i: (rar[i], lvl[i])), ("ItemLevel, rarity", lambda i: (lvl[i], rar[i]))]
    rnd = random.Random(515)
    starts = [("server order", list(server)), ("reversed", server[::-1])]
    for k in range(20):
        s = list(server)
        rnd.shuffle(s)
        starts.append(("shuffle %d" % k, s))
    for cname, key in cands:
        K.eq(sorted(tab, key=key), server, "ORD stable sort by (%s) = the wanted order" % cname)
        cmp = lambda a, b, key=key: (key(a) > key(b)) - (key(a) < key(b))
        bad = [sname for sname, s in starts if introsort(s, cmp) != server]
        K.eq(bad, [], "ORD unstable (introsort) sort by (%s) = the wanted order from %d starting orders" % (cname, len(starts)))
        vis = [i for i in server if "Lantern" not in i]
        K.eq(introsort(vis[::-1], cmp), vis, "ORD ... also with the 4 Lantern recipes hidden (fresh profile)")
    # ---- control: 0.5.14 tied on every numeric key -> an unstable client sort may scramble the server order
    onode = dict((i, json.loads(old["Server/Item/Items/Utility/%s.json" % i])) for i in tab)
    K.check(len(set(int(onode[i].get("ItemLevel", 0)) for i in tab)) == 1, "ORD control: 0.5.14's 51 recipes all have the same ItemLevel (the ties)")
    oc = lambda a, b: (rar[a] > rar[b]) - (rar[a] < rar[b])
    K.check(introsort(server, oc) != server, "ORD control: an unstable sort by rarity alone does NOT keep 0.5.14's server order")
    names = dict(l.split("=", 1) for l in zn.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines() if "=" in l)
    print("ORD client order (ItemLevel): " + ", ".join("%d %s" % (lvl[i], names.get("server.items.%s.name" % i, i)) for i in server[:6]) + " ... 51 " +
          names.get("server.items.%s.name" % OMNI, OMNI))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("order", run_order)], script=__file__)
