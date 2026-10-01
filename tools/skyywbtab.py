"""THE WORKBENCH TAB "Accessories & Bags" - one source for SkyyAccessories (0.5.2+, the OWNER) and SkyySacks (0.7.10+, a FALLBACK copy).

Skyy 2026-10-01 (vanilla Workbench, accessory recipes mixed into its Crafting tab): "make a new tab for accessories, and sacks. list them in
the order you would craft them. low levels first. with legendries and omnis at the bottom."

ENGINE FACTS (HytaleServer.jar bytecode, 2026-10-01; probe() below stops a build when any of them changes):
  - The Workbench's tabs are the ordered array CraftingBench.categories (protected, BenchCategory[]) of the Bench_WorkBench BlockType.
    CraftingWindow's constructor rebuilds windowData "categories" from bench.getCategories() EVERY time a Workbench window opens (id,
    name, icon, craftableRecipes = CraftingPlugin.getAvailableRecipesForCategory(benchId, catId) iterated into a JsonArray), so a category
    appended at runtime shows in the next window. Categories reach the client only through that windowData.
  - An asset cannot inherit from itself ("Failed to load asset ... because it is its own parent!") and a full Bench_WorkBench.json
    override collides with any other mod that overrides it (Extended Backpacks, WorkbenchTierKeeper: one winner, the loser's tab and its
    recipes vanish). So the tab is APPENDED AT RUNTIME to every Workbench CraftingBench (copy-on-write: a new array is written, the old
    one is never changed, so a window being built keeps a consistent array) - whatever Workbench asset won, this tab is added to it.
  - A recipe lands in a tab through its BenchRequirement Categories (CraftingPlugin.onRecipeLoad -> BenchRecipeRegistry.addRecipe ->
    categoryMap.computeIfAbsent(cat, new ObjectOpenHashSet).add(recipeId)); the set is only ever used through java.util.Set (no cast to
    the fastutil class anywhere), registries are created once (computeIfAbsent) and never replaced. The ORDER inside a tab is that set's
    iteration order (a hash set = "mixed in"). Replacing our category's set with a java.util.TreeSet(WbRank) makes the server send the
    crafting-progression order; recipe reloads go through Set.remove / add and keep it sorted. Whether the client keeps the order the
    server sends is UNVERIFIED (client is native code; it knows each output's level and quality and could sort by itself).
  - Validation (CraftingManager.isValidBenchForRecipe) ignores categories; /craft (SkyySacks) never reads them.

WHO DOES WHAT (identical result whichever plugin starts first, and each mod works alone):
  - The tab id / name key / name text / rank tables are THIS module, imported by both build scripts.
  - SkyyAccessories (OWNER = true) always ends with ITS definition: it adds the tab when missing and replaces a fallback entry with the same
    id IN PLACE (same index); it always installs its own TreeSet(WbRank) (replacing any other set, also SkyySacks' sorted one).
  - SkyySacks (OWNER = false) only adds the tab when no entry with the id exists, and only sorts when the set is not sorted yet. So with
    both mods the result is always SkyyAccessories' entry + order; with SkyySacks alone the bags still get the tab (never invisible).
  - Each mod's start() applies it (every asset pack is loaded then); a LoadedAssetsEvent listener (BlockType: the event's new objects +
    the whole map; CraftingRecipe: re-check the sorted set) re-applies it after an asset reload, which builds new BlockType objects.
  - The icon: Assets.zip Icons/ItemsGenerated/Utility_Bag_Seed.png (the Accessory Bag's and every Magic Bag's icon, 64x64 like the
    vanilla tab icons) copied at build time into each jar under Icons/CraftingCategories/<Mod>/ (the folder the vanilla category
    validator wants; dozens of installed mods ship their tab icons there).
"""
import os, json, zipfile, struct

WB_VERSION = "1"                                      # bump when the runtime protocol below changes (both mods print it)
TAB_ID = "Workbench_SkyyAccessories"                  # the category id (a recipe's BenchRequirement Categories entry)
NAME_KEY = "server.benchCategories.workbench.skyyaccessories"   # the vanilla pattern server.benchCategories.workbench.<x>
TAB_TEXT = "Accessories & Bags"                       # in-game: the items are "... Accessory", "Accessory Bag" and "... Bag"
LANG_LINES = ["benchCategories.workbench.skyyaccessories=" + TAB_TEXT,   # vanilla server.lang style (file prefix server.)
              NAME_KEY + "=" + TAB_TEXT]                                 # + the prefixed twin (the SkyySacks / SkyyVault pattern)
BENCH_ID = "Workbench"
OWNER_MOD = "SkyyAccessories"
ICON_SRC = "Common/Icons/ItemsGenerated/Utility_Bag_Seed.png"
RECIPE_SUFFIX = "_Recipe_Generated_"


def icon_path(mod):
    return "Icons/CraftingCategories/%s/AccessoriesBags.png" % mod


# ---- THE ORDER (crafting progression across both mods). rank(): Accessory Bag 0; then tier by tier - Normal 1, Unique 2, Rare 3,
# Legendary 4 (accessory words Common / Uncommon / Rare / Epic, bag words Small / Medium / Rare / Large, bench accessory I / II / III /
# IV and up); inside a tier: stat accessories (LINES order), bench accessories (BENCHES order, then the numeral), bags (SACKS order) - EXCEPT
# the Normal bags, which come right after the Accessory Bag ("the Accessory Bag and the first bags first"); an id this table does not
# know (a future line / bench / bag) sorts by its pattern into its tier with sub-order 99, an id with no known pattern after the Legendary
# tier; the Omni Accessory next to last and the Mythic Omni Bag LAST. Ties: String.compareTo (a TreeSet needs a total order).
LINES = ("Vitality", "Endurance", "Intelligence", "Regeneration", "Speed")
BENCHES = ("Workbench", "Armor_Bench", "Weapon_Bench", "Farmingbench", "Furnace", "Tannery", "Arcanebench", "Furniture_Bench",
           "Loombench", "Salvagebench", "Campfire")
BENCH_TIERS = {"Workbench": 3, "Armor_Bench": 3, "Weapon_Bench": 3, "Farmingbench": 7, "Furnace": 2, "Tannery": 2, "Arcanebench": 1,
               "Furniture_Bench": 1, "Loombench": 1, "Salvagebench": 1, "Campfire": 1}
SACKS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
TIER_WORDS = (("Common", 1), ("Small", 1), ("Uncommon", 2), ("Medium", 2), ("Rare", 3), ("Epic", 4), ("Large", 4))
ACC_BAG, ACC_OMNI, SACK_OMNI = "Skyy_Accessory_Bag", "Skyy_Accessory_Omni", "Skyy_Sack_Omni"
R_BAG, R_UNKNOWN, R_ACC_OMNI, R_SACK_OMNI = 0, 8000000, 9000000, 9100000


def _expected():
    acc_words, sack_words = ("Common", "Uncommon", "Rare", "Epic"), ("Small", "Medium", "Rare", "Large")
    out = [ACC_BAG] + ["Skyy_Sack_%s_Small" % s for s in SACKS]
    for t in range(1, 5):
        out += ["Skyy_Talisman_%s_%s" % (l, acc_words[t - 1]) for l in LINES]
        for b in BENCHES:
            for n in range(1, BENCH_TIERS[b] + 1):
                if min(n, 4) == t:
                    out.append("Skyy_Accessory_%s_T%d" % (b, n))
        if t > 1:
            out += ["Skyy_Sack_%s_%s" % (s, sack_words[t - 1]) for s in SACKS]
    return out + [ACC_OMNI, SACK_OMNI]


EXPECTED = _expected()          # the item ids, in the order the tab lists them (recipe id = item id + "_Recipe_Generated_0")
assert len(EXPECTED) == 68 and len(set(EXPECTED)) == 68 and EXPECTED[0] == ACC_BAG and EXPECTED[-1] == SACK_OMNI


def base_py(rid):
    i = rid.find(RECIPE_SUFFIX)
    return rid if i < 0 else rid[:i]


def _tier_py(w):
    for k, v in TIER_WORDS:
        if k == w:
            return v
    return 0


def _num_py(s):
    if not (1 <= len(s) <= 4) or any(c not in "0123456789" for c in s):
        return -1
    return int(s)


def _key_py(tier, kind, sub, n):
    k = 0 if (kind == 3 and tier == 1) else kind
    return tier * 1000000 + k * 100000 + (99 if sub < 0 else sub) * 100 + min(n, 99)


def rank_py(rid):
    """the Python mirror of WbRank.rank (the test harnesses compare both on every id they see)"""
    if rid is None:
        return 9900000
    b = base_py(rid)
    if b == ACC_BAG:
        return R_BAG
    if b == ACC_OMNI:
        return R_ACC_OMNI
    if b == SACK_OMNI:
        return R_SACK_OMNI
    if b.startswith("Skyy_Talisman_"):
        r = b[14:]
        u = r.rfind("_")
        if u > 0:
            t = _tier_py(r[u + 1:])
            if t > 0:
                return _key_py(t, 1, LINES.index(r[:u]) if r[:u] in LINES else -1, 0)
    if b.startswith("Skyy_Accessory_"):
        r = b[15:]
        u = r.rfind("_T")
        if u > 0:
            n = _num_py(r[u + 2:])
            if n > 0:
                return _key_py(min(n, 4), 2, BENCHES.index(r[:u]) if r[:u] in BENCHES else -1, n)
    if b.startswith("Skyy_Sack_"):
        r = b[10:]
        u = r.rfind("_")
        if u > 0:
            t = _tier_py(r[u + 1:])
            if t > 0:
                return _key_py(t, 3, SACKS.index(r[:u]) if r[:u] in SACKS else -1, 0)
    return R_UNKNOWN


def sort_py(ids):
    return sorted(ids, key=lambda i: (rank_py(i), i))


assert sort_py(list(reversed(EXPECTED))) == EXPECTED, "the rank mirror must give exactly the expected order"
assert sort_py([i + "_Recipe_Generated_0" for i in reversed(EXPECTED)]) == [i + "_Recipe_Generated_0" for i in EXPECTED]


def _jarr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"


# ---- engine names
CB = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench"
CBC = CB + "$BenchCategory"
BIC = CB + "$BenchItemCategory"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
BT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
BRR = "com.hypixel.hytale.builtin.crafting.BenchRecipeRegistry"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
LAE = "com.hypixel.hytale.assetstore.event.LoadedAssetsEvent"
CWN = "com.hypixel.hytale.builtin.crafting.window.CraftingWindow"
LOGT = "com.hypixel.hytale.logger.HytaleLogger"


def probe(pool):
    """build-time proof of every engine fact the runtime part relies on (stops the build when one changed)"""
    from jpype import JClass
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def code(cname, mname, desc=None):
        cc = pool.get(cname)
        cf = cc.getClassFile()
        for mi in cf.getMethods():
            if str(mi.getName()) == mname and (desc is None or str(mi.getDescriptor()) == desc):
                ca = mi.getCodeAttribute()
                it = ca.iterator()
                out = []
                while it.hasNext():
                    p = it.next()
                    out.append(str(IP.instructionString(it, p, mi.getConstPool())))
                return "\n".join(out)
        raise SystemExit("Workbench tab probe: %s.%s%s not found" % (cname, mname, desc or ""))

    def field(cname, fname, desc, static):
        cc = pool.get(cname)
        for f in cc.getDeclaredFields():
            if str(f.getName()) == fname:
                st = bool(f.getModifiers() & 0x0008)
                if str(f.getSignature()) != desc or st != static:
                    raise SystemExit("Workbench tab probe: %s.%s is %s static=%s, expected %s static=%s"
                                     % (cname, fname, f.getSignature(), st, desc, static))
                return
        raise SystemExit("Workbench tab probe: field %s.%s is gone" % (cname, fname))

    field(CB, "categories", "[L%s;" % CBC.replace(".", "/"), False)
    field(CRP, "registries", "Ljava/util/Map;", True)
    field(BRR, "categoryMap", "Ljava/util/Map;", False)
    ctor = [k for k in pool.get(CBC).getDeclaredConstructors()
            if str(k.getSignature()) == "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;[L%s;)V" % BIC.replace(".", "/")]
    if not ctor or not (ctor[0].getModifiers() & 0x0001):
        raise SystemExit("Workbench tab probe: the public BenchCategory(String id, String name, String icon, BenchItemCategory[]) is gone")
    for cname, m, d in ((CB, "getCategories", "()[L%s;" % CBC.replace(".", "/")), (CBC, "getId", "()Ljava/lang/String;"),
                        (CBC, "getName", "()Ljava/lang/String;"), (CBC, "getIcon", "()Ljava/lang/String;"),
                        (BEN, "getId", "()Ljava/lang/String;"), (BT, "getBench", "()L%s;" % BEN.replace(".", "/")),
                        (CRP, "getAvailableRecipesForCategory", "(Ljava/lang/String;Ljava/lang/String;)Ljava/util/Set;"),
                        (BRR, "getRecipesForCategory", "(Ljava/lang/String;)Ljava/util/Set;"),
                        (LAE, "getLoadedAssets", "()Ljava/util/Map;"), (LAE, "getAssetClass", "()Ljava/lang/Class;")):
        code(cname, m, d)
    am = [m for m in pool.get(BT).getDeclaredMethods() if str(m.getName()) == "getAssetMap"]
    if len(am) != 1:
        raise SystemExit("Workbench tab probe: BlockType.getAssetMap() changed")
    amc = am[0].getReturnType()
    if "getAssetMap" not in set(str(m.getName()) for m in amc.getMethods()):
        raise SystemExit("Workbench tab probe: %s has no getAssetMap()" % amc.getName())
    reg = [m for m in pool.get("com.hypixel.hytale.event.EventRegistry").getMethods() if str(m.getName()) == "register"
           and str(m.getSignature()) == "(Ljava/lang/Class;Ljava/lang/Object;Ljava/util/function/Consumer;)Lcom/hypixel/hytale/event/EventRegistration;"]
    if not reg:
        raise SystemExit("Workbench tab probe: EventRegistry.register(Class, key, Consumer) is gone")
    # the window builds the tab list from getCategories() and each tab's recipe list by iterating the registry set (order kept)
    cw = [k for k in pool.get(CWN).getDeclaredConstructors()]
    if len(cw) != 1:
        raise SystemExit("Workbench tab probe: CraftingWindow constructors changed")
    ca = cw[0].getMethodInfo().getCodeAttribute()
    it, cp, w = ca.iterator(), cw[0].getMethodInfo().getConstPool(), []
    while it.hasNext():
        p = it.next()
        w.append(str(IP.instructionString(it, p, cp)))
    w = "\n".join(w)
    for need in ("CraftingBench.getCategories(", "CraftingPlugin.getAvailableRecipesForCategory(", "java.util.Set.iterator(",
                 "com.google.gson.JsonArray.add((Ljava/lang/String;)V)", '"craftableRecipes"', '"categories"', "BenchCategory.getIcon(",
                 "BenchCategory.getName(", "BenchCategory.getItemCategories("):
        if need not in w:
            raise SystemExit("Workbench tab probe: CraftingWindow no longer does " + need)
    if "ifnonnull" not in w:
        raise SystemExit("Workbench tab probe: CraftingWindow no longer skips a null itemCategories")
    # the registry sets are only used through java.util.Set (a TreeSet is a valid replacement) and never re-created
    for cname, mname in ((BRR, "addRecipe"), (BRR, "removeRecipe"), (BRR, "getRecipesForCategory"), (BRR, "recompute"),
                         (CRP, "getAvailableRecipesForCategory"), (CRP, "onRecipeLoad"), (CRP, "onRecipeRemove"),
                         (CRP, "computeBenchRecipeRegistries")):
        t = code(cname, mname)
        if any(l.startswith("checkcast") and "ObjectOpenHashSet" in l for l in t.splitlines()):
            raise SystemExit("Workbench tab probe: %s.%s casts a category set to the fastutil class" % (cname, mname))
        if "putstatic" in t and "registries" in t:
            raise SystemExit("Workbench tab probe: %s.%s replaces the registries map" % (cname, mname))
    if "java.util.Map.computeIfAbsent(" not in code(BRR, "addRecipe") or "java.util.Set.add(" not in code(BRR, "addRecipe"):
        raise SystemExit("Workbench tab probe: BenchRecipeRegistry.addRecipe no longer reuses the category set (computeIfAbsent + Set.add)")
    if "java.util.Map.computeIfAbsent(" not in code(CRP, "onRecipeLoad") or "removeRecipe(" not in code(CRP, "onRecipeLoad"):
        raise SystemExit("Workbench tab probe: CraftingPlugin.onRecipeLoad no longer reuses the registries (computeIfAbsent)")
    for cname in (BRR, CRP):
        cf = pool.get(cname).getClassFile()
        for mi in cf.getMethods():
            if str(mi.getName()) == "<init>" or mi.getCodeAttribute() is None:
                continue
            ca = mi.getCodeAttribute()
            it = ca.iterator()
            while it.hasNext():
                p = it.next()
                s = str(IP.instructionString(it, p, mi.getConstPool()))
                if s.startswith("putfield") and "categoryMap" in s:
                    raise SystemExit("Workbench tab probe: %s.%s replaces categoryMap" % (cname, mi.getName()))
    return "engine probes ok (CraftingBench.categories, BenchCategory 4-arg constructor, CraftingPlugin.registries, " \
           "BenchRecipeRegistry.categoryMap via java.util.Set only, CraftingWindow order, BlockType map, LoadedAssetsEvent)"


def icon_png(assets_zip):
    """the tab icon bytes (Assets.zip Utility_Bag_Seed.png, checked to be a 64x64 PNG like the vanilla tab icons)"""
    with zipfile.ZipFile(assets_zip) as z:
        data = z.read(ICON_SRC)
        ref = z.read("Common/Icons/CraftingCategories/Workbench/Processing.png")
    def size(b):
        if b[:8] != b"\x89PNG\r\n\x1a\n" or b[12:16] != b"IHDR":
            raise SystemExit("Workbench tab icon: not a PNG")
        return struct.unpack(">II", b[16:24])
    if size(data) != size(ref):
        raise SystemExit("Workbench tab icon: %s is %s, the vanilla tab icons are %s" % (ICON_SRC, size(data), size(ref)))
    return data


def emit(pool, CtField, CtNewMethod, CtNewConstructor, pkg, owner, mod):
    """the runtime part: <pkg>.WbRank (the order), <pkg>.WbTab (tab + order, owner / fallback rules), <pkg>.WbAssetL (asset reloads).
    Returns the CtClass list (write them with the mod's other classes). Plugin hooks (see wire()): setup() sets WbTab.LOG and registers
    WbAssetL for LoadedAssetsEvent of BlockType and CraftingRecipe; start() calls WbTab.start()."""
    tok = {"@PKG@": pkg, "@CB@": CB, "@CBC@": CBC, "@BIC@": BIC, "@BEN@": BEN, "@BT@": BT, "@CRP@": CRP, "@BRR@": BRR, "@LAE@": LAE,
           "@LOGT@": LOGT, "@MOD@": mod}

    def T(src):
        for k, v in tok.items():
            src = src.replace(k, v)
        assert "@" not in src, src[:200]
        return src

    rank = pool.makeClass(pkg + ".WbRank")
    rank.addInterface(pool.get("java.util.Comparator"))
    tab = pool.makeClass(pkg + ".WbTab")
    lis = pool.makeClass(pkg + ".WbAssetL")
    lis.addInterface(pool.get("java.util.function.Consumer"))

    def F(c, s):
        c.addField(CtField.make(T(s), c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(T(s), c))

    # ---------------- WbRank: the order (Python mirror rank_py)
    F(rank, "public static final String SUFFIX = \"%s\";" % RECIPE_SUFFIX)
    F(rank, "public static final String[] LINES = %s;" % _jarr(LINES))
    F(rank, "public static final String[] BENCHES = %s;" % _jarr(BENCHES))
    F(rank, "public static final String[] SACKS = %s;" % _jarr(SACKS))
    rank.addConstructor(CtNewConstructor.make("public WbRank() { }", rank))
    M(rank, """
public static String base(String id) {
  int i = id.indexOf(SUFFIX);
  return i < 0 ? id : id.substring(0, i);
}""")
    M(rank, """
public static int idx(String[] a, String v) {
  for (int i = 0; i < a.length; i++) if (a[i].equals(v)) return i;
  return -1;
}""")
    M(rank, """
public static int tierWord(String w) {
  if (w.equals("Common") || w.equals("Small")) return 1;
  if (w.equals("Uncommon") || w.equals("Medium")) return 2;
  if (w.equals("Rare")) return 3;
  if (w.equals("Epic") || w.equals("Large")) return 4;
  return 0;
}""")
    M(rank, """
public static int num(String s) {
  if (s.length() < 1 || s.length() > 4) return -1;
  int v = 0;
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c < '0' || c > '9') return -1;
    v = v * 10 + (c - '0');
  }
  return v;
}""")
    M(rank, """
public static long key(int tier, int kind, int sub, int n) {
  int k = kind;
  if (kind == 3 && tier == 1) k = 0;
  int s = sub < 0 ? 99 : sub;
  int m = n > 99 ? 99 : n;
  return tier * 1000000L + k * 100000L + s * 100L + m;
}""")
    M(rank, """
public static long rank(String id) {
  if (id == null) return 9900000L;
  String b = base(id);
  if (b.equals("%s")) return %dL;
  if (b.equals("%s")) return %dL;
  if (b.equals("%s")) return %dL;
  if (b.startsWith("Skyy_Talisman_")) {
    String r = b.substring(14);
    int u = r.lastIndexOf('_');
    if (u > 0) {
      int t = tierWord(r.substring(u + 1));
      if (t > 0) return key(t, 1, idx(LINES, r.substring(0, u)), 0);
    }
  }
  if (b.startsWith("Skyy_Accessory_")) {
    String r2 = b.substring(15);
    int u2 = r2.lastIndexOf("_T");
    if (u2 > 0) {
      int n = num(r2.substring(u2 + 2));
      if (n > 0) return key(n >= 4 ? 4 : n, 2, idx(BENCHES, r2.substring(0, u2)), n);
    }
  }
  if (b.startsWith("Skyy_Sack_")) {
    String r3 = b.substring(10);
    int u3 = r3.lastIndexOf('_');
    if (u3 > 0) {
      int t3 = tierWord(r3.substring(u3 + 1));
      if (t3 > 0) return key(t3, 3, idx(SACKS, r3.substring(0, u3)), 0);
    }
  }
  return %dL;
}""" % (ACC_BAG, R_BAG, ACC_OMNI, R_ACC_OMNI, SACK_OMNI, R_SACK_OMNI, R_UNKNOWN))
    M(rank, """
public int compare(Object a, Object b) {
  String x = (String) a;
  String y = (String) b;
  long rx = rank(x);
  long ry = rank(y);
  if (rx < ry) return -1;
  if (rx > ry) return 1;
  return x.compareTo(y);
}""")

    # ---------------- WbTab
    F(tab, "public static final String ID = \"%s\";" % TAB_ID)
    F(tab, "public static final String NAME = \"%s\";" % NAME_KEY)
    F(tab, "public static final String TEXT = \"%s\";" % TAB_TEXT)
    F(tab, "public static final String ICON = \"%s\";" % icon_path(mod))
    F(tab, "public static final String BENCH = \"%s\";" % BENCH_ID)
    F(tab, "public static final String PROTO = \"%s\";" % WB_VERSION)
    F(tab, "public static final boolean OWNER = %s;" % ("true" if owner else "false"))
    F(tab, "public static @LOGT@ LOG;")
    F(tab, "public static java.lang.reflect.Field CATS;")
    F(tab, "public static java.lang.reflect.Field REGS;")
    F(tab, "public static java.lang.reflect.Field CMAP;")
    F(tab, "public static volatile boolean CATS_BAD = false;")
    F(tab, "public static volatile boolean MAP_BAD = false;")
    F(tab, "public static volatile boolean WARN_SCAN = false;")
    F(tab, "public static volatile boolean WARN_SORT = false;")
    F(tab, "public static volatile String LAST = \"not started\";")
    M(tab, """
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    M(tab, """
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    # CraftingBench.categories (null + one WARNING when the engine changed)
    M(tab, """
public static java.lang.reflect.Field catsField() {
  if (CATS != null) return CATS;
  if (CATS_BAD) return null;
  try {
    java.lang.reflect.Field f = @CB@.class.getDeclaredField("categories");
    f.setAccessible(true);
    CATS = f;
    return f;
  } catch (Throwable t) {
    CATS_BAD = true;
    warn("Workbench tab: the game changed (CraftingBench.categories: " + t + ") - the Accessories & Bags recipes are not shown at the Workbench; pocket crafting and /craft still make them");
    return null;
  }
}""")
    # CraftingPlugin.registries + BenchRecipeRegistry.categoryMap (false + one WARNING: the tab then keeps the engine's order)
    M(tab, """
public static boolean mapFields() {
  if (REGS != null && CMAP != null) return true;
  if (MAP_BAD) return false;
  try {
    java.lang.reflect.Field a = @CRP@.class.getDeclaredField("registries");
    a.setAccessible(true);
    java.lang.reflect.Field b = @BRR@.class.getDeclaredField("categoryMap");
    b.setAccessible(true);
    REGS = a;
    CMAP = b;
    return true;
  } catch (Throwable t) {
    MAP_BAD = true;
    warn("Workbench tab: the game changed (recipe registry: " + t + ") - the tab lists its recipes in the engine's own order");
    return false;
  }
}""")
    M(tab, """
public static @CBC@ mine() {
  return new @CBC@(ID, NAME, ICON, (@BIC@[]) null);
}""")
    # 0 = nothing to do, 1 = added (appended), 2 = the owner replaced a fallback entry in place, -1 = failed. Copy-on-write.
    M(tab, """
public static int applyTo(@CB@ b) {
  java.lang.reflect.Field f = catsField();
  if (f == null || b == null) return -1;
  try {
    @CBC@[] cur = b.getCategories();
    int n = cur == null ? 0 : cur.length;
    for (int i = 0; i < n; i++) {
      if (cur[i] == null || !ID.equals(cur[i].getId())) continue;
      if (!OWNER) return 0;
      if (ICON.equals(cur[i].getIcon()) && NAME.equals(cur[i].getName())) return 0;
      @CBC@[] cp = new @CBC@[n];
      for (int j = 0; j < n; j++) cp[j] = cur[j];
      cp[i] = mine();
      f.set(b, cp);
      return 2;
    }
    @CBC@[] out = new @CBC@[n + 1];
    for (int k = 0; k < n; k++) out[k] = cur[k];
    out[n] = mine();
    f.set(b, out);
    return 1;
  } catch (Throwable t) { return -1; }
}""")
    M(tab, """
public static int locked(@CB@ b) {
  int r = -1;
  synchronized (b) { r = applyTo(b); }
  return r;
}""")
    # every Workbench CraftingBench among these BlockTypes (state variants may share one bench object: counted once);
    # returns how many benches carry the tab, -1 when none could be changed
    M(tab, """
public static int scan(java.util.Collection c) {
  if (c == null) return 0;
  if (catsField() == null) return -1;
  java.util.IdentityHashMap seen = new java.util.IdentityHashMap();
  int ok = 0;
  int bad = 0;
  java.util.Iterator it = c.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @BT@)) continue;
    @BEN@ be = ((@BT@) o).getBench();
    if (!(be instanceof @CB@) || !BENCH.equals(be.getId())) continue;
    if (seen.put(be, be) != null) continue;
    if (locked((@CB@) be) < 0) bad++; else ok++;
  }
  if (bad > 0 && !WARN_SCAN) {
    WARN_SCAN = true;
    warn("Workbench tab: could not add the tab to " + bad + " Workbench definition(s) - their Accessories & Bags recipes are not shown there; pocket crafting and /craft still make them");
  }
  return (bad > 0 && ok == 0) ? -1 : ok;
}""")
    M(tab, """
public static int scanAll() {
  try {
    return scan(@BT@.getAssetMap().getAssetMap().values());
  } catch (Throwable t) {
    if (!WARN_SCAN) { WARN_SCAN = true; warn("Workbench tab: could not read the block types (" + t + ")"); }
    return -1;
  }
}""")
    # the order: OWNER always ends with its own TreeSet(WbRank); the fallback only sorts an unsorted set
    M(tab, """
public static String sort() {
  if (!mapFields()) return "the engine's order (registry unavailable)";
  try {
    java.util.Map regs = (java.util.Map) REGS.get(null);
    Object reg = regs == null ? null : regs.get(BENCH);
    if (reg == null) return "no Workbench recipes loaded yet";
    java.util.Map cm = (java.util.Map) CMAP.get(reg);
    Object cur = cm.get(ID);
    if (cur instanceof java.util.TreeSet && ((java.util.TreeSet) cur).comparator() instanceof @PKG@.WbRank)
      return "crafting progression, " + ((java.util.Set) cur).size() + " recipes";
    if (!OWNER && cur instanceof java.util.SortedSet)
      return "kept the order SkyyAccessories set, " + ((java.util.Set) cur).size() + " recipes";
    java.util.TreeSet ts = new java.util.TreeSet(new @PKG@.WbRank());
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    cm.put(ID, ts);
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    return "crafting progression, " + ts.size() + " recipes";
  } catch (Throwable t) {
    if (!WARN_SORT) { WARN_SORT = true; warn("Workbench tab: could not order the recipes (" + t + ") - they stay in the engine's own order"); }
    return "the engine's order";
  }
}""")
    M(tab, """
public static String start() {
  int n = scanAll();
  String s = sort();
  String who = OWNER ? "" : " (SkyySacks' copy - SkyyAccessories' tab wins when both run)";
  String line;
  if (n > 0) line = "Workbench tab '" + TEXT + "'" + who + " on " + n + " Workbench definition(s); order: " + s + " (tab protocol " + PROTO + ")";
  else if (n == 0) line = "Workbench tab '" + TEXT + "': no Workbench block type found yet (the asset reload listener adds it later)";
  else line = "Workbench tab '" + TEXT + "' could not be added - see the warning above";
  LAST = line;
  if (n >= 0) info(line); else warn(line);
  return line;
}""")
    M(tab, """
public static void onLoaded(Object e) {
  try {
    @LAE@ ev = (@LAE@) e;
    if (ev.getAssetClass() == @BT@.class) {
      java.util.Map m = ev.getLoadedAssets();
      if (m != null) scan(m.values());
      scanAll();
    } else sort();
  } catch (Throwable t) { }
}""")
    lis.addConstructor(CtNewConstructor.make("public WbAssetL() { }", lis))
    M(lis, """
public void accept(Object e) {
  try { @PKG@.WbTab.onLoaded(e); } catch (Throwable t) { }
}""")
    return [rank, tab, lis]


# the plugin lines (setup() end + start()), with the mod's package
def setup_java(pkg):
    return ("  // Workbench tab 'Accessories & Bags' (tools/skyywbtab.py): re-applied after an asset reload (new BlockType objects / recipe sets)\n"
            "  %s.WbTab.LOG = getLogger();\n"
            "  try {\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.WbAssetL());\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.WbAssetL());\n"
            "  } catch (Throwable twb) { %s.WbTab.warn(\"Workbench tab: no asset reload listener (\" + twb + \") - a live asset reload drops the tab until a restart\"); }\n"
            % (pkg, LAE, BT, pkg, LAE, CRR, pkg, pkg))


def start_java(pkg):
    return ("protected void start() {\n"
            "  // every asset pack (mods included) is loaded now: add the Workbench tab 'Accessories & Bags' + its order\n"
            "  try { %s.WbTab.start(); } catch (Throwable t) { %s.WbTab.warn(\"Workbench tab failed: \" + t); }\n"
            "}" % (pkg, pkg))


def recipe_checks(files, own_ids, bag_req_id=None):
    """build checks on the mod's item JSONs: every recipe with a Workbench requirement names exactly [TAB_ID] (none left in a vanilla
    tab), the pocket recipe keeps Fieldcraft/Tools first and adds the Workbench tab, own_ids = exactly the recipes in the tab, all in
    EXPECTED; returns {item id: requirements}"""
    got = {}
    for p, t in files.items():
        if not (p.startswith("Server/Item/Items/") and p.endswith(".json")):
            continue
        node = json.loads(t)
        r = node.get("Recipe")
        if not r:
            continue
        iid = p.rsplit("/", 1)[1][:-5]
        reqs = r.get("BenchRequirement") or []
        got[iid] = reqs
        wb = [q for q in reqs if q.get("Id") == BENCH_ID]
        if len(wb) != 1 or wb[0].get("Categories") != [TAB_ID] or wb[0].get("Type") != "Crafting" or "RequiredTierLevel" in wb[0]:
            raise SystemExit("Workbench tab: %s must have exactly one Workbench requirement {Crafting, Workbench, [%s]}: %r" % (iid, TAB_ID, reqs))
        if "Workbench_Crafting" in json.dumps(r) or any(c.startswith("Workbench_") and c != TAB_ID for q in reqs for c in q.get("Categories") or []):
            raise SystemExit("Workbench tab: %s still names a vanilla Workbench tab: %r" % (iid, reqs))
        if iid == bag_req_id:
            if reqs != [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}, wb[0]]:
                raise SystemExit("Workbench tab: %s must stay pocket-craftable (Fieldcraft / Tools first) and add the tab: %r" % (iid, reqs))
        elif len(reqs) != 1:
            raise SystemExit("Workbench tab: %s has %d requirements, expected only the Workbench one" % (iid, len(reqs)))
    if sorted(got) != sorted(own_ids):
        raise SystemExit("Workbench tab: recipes %s vs the expected %s" % (sorted(set(got) ^ set(own_ids)), "list"))
    bad = [i for i in got if i not in EXPECTED]
    if bad:
        raise SystemExit("Workbench tab: recipes the order table does not list: %s (add them to tools/skyywbtab.py)" % bad)
    return got


LINE_NAMES = {"Vitality": "Health", "Endurance": "Stamina", "Intelligence": "Mana", "Regeneration": "Regeneration", "Speed": "Speed"}
BENCH_NAMES = {"Workbench": "Workbench", "Armor_Bench": "Armor Bench", "Weapon_Bench": "Weapon Bench", "Farmingbench": "Farming Bench",
               "Furnace": "Furnace", "Tannery": "Tannery", "Arcanebench": "Arcane Bench", "Furniture_Bench": "Furniture Bench",
               "Loombench": "Loom", "Salvagebench": "Salvage Bench", "Campfire": "Campfire"}
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]


def default_names():
    """display names of the 68 tab recipes by the two mods' naming rules (the builds print their real lang names where they have them)"""
    out = {ACC_BAG: "Accessory Bag", ACC_OMNI: "Omni Accessory", SACK_OMNI: "Mythic Omni Bag"}
    rar = ("Normal", "Unique", "Rare", "Legendary")
    for l in LINES:
        for t, w in enumerate(("Common", "Uncommon", "Rare", "Epic")):
            out["Skyy_Talisman_%s_%s" % (l, w)] = "%s %s Accessory" % (rar[t], LINE_NAMES[l])
    for b in BENCHES:
        for n in range(1, BENCH_TIERS[b] + 1):
            out["Skyy_Accessory_%s_T%d" % (b, n)] = "%s Accessory%s" % (BENCH_NAMES[b], (" " + ROMAN[n]) if BENCH_TIERS[b] > 1 else "")
    for s_ in SACKS:
        for t, w in enumerate(("Small", "Medium", "Rare", "Large")):
            out["Skyy_Sack_%s_%s" % (s_, w)] = "%s %s Bag" % (rar[t], s_)
    assert sorted(out) == sorted(EXPECTED)
    return out


def order_print(names, mine_prefixes):
    """print the full in-tab order (both mods) with the names this mod knows, and assert it (Omni Accessory next to last, Mythic Omni Bag
    last); names = {item id: display name}"""
    order = sort_py([i + RECIPE_SUFFIX + "0" for i in EXPECTED])
    assert [base_py(i) for i in order] == EXPECTED and EXPECTED[-1] == SACK_OMNI and EXPECTED[-2] == ACC_OMNI
    print("Workbench tab '%s' order (%d recipes, both mods; * = this mod):" % (TAB_TEXT, len(order)))
    row = []
    for n, i in enumerate(EXPECTED, 1):
        mine = i.startswith(tuple(mine_prefixes))
        row.append("%2d %s%s" % (n, "*" if mine else " ", names.get(i, i)))
    for k in range(0, len(row), 4):
        print("   " + " | ".join(row[k:k + 4]))


# ============================================================================================================ test harness part
# Both harnesses (SkyyAccessories 0.5.2+, SkyySacks 0.7.10+) call harness_checks() inside their bare JVM (-Xverify:all; HytaleServer.jar,
# tools/javassist.jar and BOTH jars on the classpath - the two mods use different packages, so they never collide).
EDGE_IDS = ["Skyy_Talisman_Crit_Epic", "Skyy_Talisman_Vitality_Legendary", "Skyy_Talisman_Vitality_Artifact", "Skyy_Accessory_Furnace_T9",
            "Skyy_Accessory_Alchemybench_T2", "Skyy_Accessory_Workbench_T", "Skyy_Accessory_Workbench_Tx", "Skyy_Accessory_Farmingbench_T123",
            "Skyy_Accessory_Farmingbench_T+1", "Skyy_Accessory_Farmingbench_T12345", "Skyy_Sack_Fishing_Small", "Skyy_Sack_Mining_Huge",
            "Skyy_Sack_Omni_Recipe_Generated_3", "Skyy_Accessory_Bag_Recipe_Generated_1", "Bench_Furnace_Recipe_Generated_0", "", "Skyy_",
            "Skyy_Talisman_", "Skyy_Talisman__Rare", "Skyy_Sack__Large", "Skyy_Accessory_Omni_Extra", "Tool_Pickaxe_Crude_Recipe_Generated_0"]
# the 11 vanilla recipes of the Workbench Crafting tab (Assets.zip, Workbench / Workbench_Crafting; review 2026-10-01 replaced the invented
# Bench_Loom with the real Bench_Builders - there is no vanilla Loom recipe at the Workbench)
VANILLA_WB = ["Bench_Alchemy_Recipe_Generated_0", "Bench_Arcane_Recipe_Generated_0", "Bench_Armour_Recipe_Generated_0",
              "Bench_Builders_Recipe_Generated_0", "Bench_Cooking_Recipe_Generated_0", "Bench_Farming_Recipe_Generated_0",
              "Bench_Furnace_Recipe_Generated_0", "Bench_Furniture_Recipe_Generated_0", "Bench_Salvage_Recipe_Generated_0",
              "Bench_Tannery_Recipe_Generated_0", "Bench_Weapon_Recipe_Generated_0"]
assert len(VANILLA_WB) == 11 and len(set(VANILLA_WB)) == 11
PKGS = {"SkyyAccessories": "com.skyy.accessories", "SkyySacks": "com.skyy.sacks"}


def _loadable(Cls, loader, name):
    try:
        Cls.forName(name, True, loader)
        return True
    except Exception:
        return False


def harness_checks(check, server_jar, mods=("SkyyAccessories", "SkyySacks")):
    """the runtime part on real engine objects: tab added / idempotent / owner wins in both start orders / each mod alone, copy-on-write,
    shared and overridden Workbench definitions, other benches untouched, the asset reload path, the TreeSet order = EXPECTED, recipe
    reloads keep it, vanilla tabs untouched, a REAL CraftingWindow's windowData (what the client receives), WbRank = rank_py on every
    id. Returns printable lines."""
    from jpype import JClass, JArray, JString
    out = []
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jf(c, name):
        k = c
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    CBj, CBCj, BTj, BENj = JClass(CB), JClass(CBC), JClass(BT), JClass(BEN)
    ITEM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
    ITj, BBj = JClass(ITEM), JClass("com.hypixel.hytale.builtin.crafting.component.BenchBlock")
    BTY = JClass("com.hypixel.hytale.protocol.BenchType")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(server_jar)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    BTPK = BT.rsplit(".", 1)[0]

    def made(name, build):
        try:
            return JClass(Cls.forName(name, True, loader))
        except Exception:
            return build()

    def mk_bt():
        ct = jp.makeClass(BTPK + ".SkyyWbTestBT", jp.get(BT))
        ct.addField(CtF.make("public %s it;" % ITEM, ct))
        ct.addConstructor(CtC.make("public SkyyWbTestBT() { super(); }", ct))
        ct.addMethod(CtM.make("public %s getItem() { return this.it; }" % ITEM, ct))
        return JClass(ct.toClass(BTj.class_))
    TBT = made(BTPK + ".SkyyWbTestBT", mk_bt)
    BTAM = "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap"

    def mk_map():
        ct = jp.makeClass("com.hypixel.hytale.assetstore.map.SkyyWbTestMap", jp.get(BTAM))
        ct.addField(CtF.make("public java.util.Map m;", ct))
        ct.addConstructor(CtC.make("public SkyyWbTestMap() { super((java.util.function.IntFunction) null, (java.util.function.Function) null); }", ct))
        ct.addMethod(CtM.make("public java.util.Map getAssetMap() { return this.m; }", ct))
        return JClass(ct.toClass(JClass(BTAM).class_))
    TMAP = made("com.hypixel.hytale.assetstore.map.SkyyWbTestMap", mk_map)

    def mk_store():
        ct = jp.makeClass("com.hypixel.hytale.assetstore.SkyyWbTestStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
        ct.addConstructor(CtC.make("public SkyyWbTestStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", ct))
        return JClass(ct.toClass(JClass("com.hypixel.hytale.assetstore.AssetStore").class_))
    TST = made("com.hypixel.hytale.assetstore.SkyyWbTestStore", mk_store)
    bt_map = us.allocateInstance(TMAP.class_)
    HashMap, ArrayList = JClass("java.util.HashMap"), JClass("java.util.ArrayList")
    jf(TMAP.class_, "m").set(bt_map, HashMap())
    store = us.allocateInstance(TST.class_)
    jf(JClass("com.hypixel.hytale.assetstore.AssetStore").class_, "assetMap").set(store, bt_map)
    jf(BTj.class_, "ASSET_STORE").set(None, store)

    VAN = [("Workbench_Survival", "Icons/CraftingCategories/Workbench/WeaponsCrude.png", "server.benchCategories.workbench.survival"),
           ("Workbench_Tools", "Icons/CraftingCategories/Workbench/Tools.png", "server.benchCategories.workbench.tools"),
           ("Workbench_Crafting", "Icons/CraftingCategories/Workbench/Processing.png", "server.benchCategories.workbench.crafting"),
           ("Workbench_Tinkering", "Icons/CraftingCategories/Workbench/Deco_Target.png", "server.benchCategories.workbench.tinkering")]
    CATS_F = jf(CBj.class_, "categories")

    def bench(bid, cats):
        b = CBj()
        jf(BENj.class_, "id").set(b, bid)
        jf(BENj.class_, "type").set(b, BTY.Crafting)
        arr = JArray(CBCj)(len(cats))
        for i, (cid, icon, name) in enumerate(cats):
            arr[i] = CBCj(cid, name, icon, None)
        CATS_F.set(b, arr)
        return b

    def btype(tid, b):
        t = us.allocateInstance(TBT.class_)
        jf(BTj.class_, "id").set(t, tid)
        jf(BTj.class_, "bench").set(t, b)
        it = us.allocateInstance(ITj.class_)
        jf(ITj.class_, "id").set(it, "Bench_WorkBench")
        jf(TBT.class_, "it").set(t, it)
        return t

    def cats_of(b):
        return [(str(c.getId()), str(c.getIcon()), str(c.getName())) for c in b.getCategories()]

    # the recipe registry (CraftingPlugin.registries is the engine's static map; one Workbench registry per scenario)
    REGS = jf(JClass(CRP).class_, "registries").get(None)
    CMAP_F = jf(JClass(BRR).class_, "categoryMap")
    CRRj = JClass(CRR)
    BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    tab_ids = [i + RECIPE_SUFFIX + "0" for i in EXPECTED]
    shuffled = [tab_ids[(k * 37) % len(tab_ids)] for k in range(len(tab_ids))]
    assert sorted(shuffled) == sorted(tab_ids)

    def recipe(rid):
        r = us.allocateInstance(CRRj.class_)
        jf(CRRj.class_, "id").set(r, rid)
        return r

    def req(cat):
        q = BRQ()
        q.type = BTY.Crafting
        q.id = BENCH_ID
        q.categories = JArray(JString)([cat])
        return q

    def fresh_registry():
        REGS.clear()
        reg = JClass(BRR)(JString(BENCH_ID))
        REGS.put(BENCH_ID, reg)
        for rid in shuffled:
            reg.addRecipe(req(TAB_ID), recipe(rid))
        for rid in VANILLA_WB:
            reg.addRecipe(req("Workbench_Crafting"), recipe(rid))
        return reg

    def world():
        """the Workbench (two BlockType state variants share ONE bench object), another mod's full Workbench override (5 tabs, its own
        bench object), a Furnace (not touched); all in the BlockType asset map start() reads"""
        wb = bench(BENCH_ID, VAN)
        ov = bench(BENCH_ID, VAN + [("Workbench_Extended_Backpacks", "Icons/CraftingCategories/Workbench/Upgrade_Backpack.png", "server.x")])
        fu = bench("Furnace", [("Furnace_Main", "Icons/CraftingCategories/Furnace/Main.png", "server.y")])
        bts = [btype("Bench_WorkBench", wb), btype("*Bench_WorkBench_State_Definitions_Tier2", wb), btype("Other_Mod_WorkBench", ov),
               btype("Bench_Furnace", fu)]
        m = jf(TMAP.class_, "m").get(bt_map)
        m.clear()
        for t in bts:
            m.put(t.getId(), t)
        return wb, ov, fu, bts

    have = [m for m in mods if _loadable(Cls, loader, PKGS[m] + ".WbTab")]
    check(len(have) == len(mods), "W jars on the classpath: %s" % ", ".join(have))
    TAB = dict((m, JClass(Cls.forName(PKGS[m] + ".WbTab", True, loader))) for m in have)
    RANK = dict((m, JClass(Cls.forName(PKGS[m] + ".WbRank", True, loader))) for m in have)
    LIS = dict((m, JClass(Cls.forName(PKGS[m] + ".WbAssetL", True, loader))) for m in have)
    allids = EXPECTED + tab_ids + EDGE_IDS + VANILLA_WB
    for m in have:
        t = TAB[m]
        check(str(t.ID) == TAB_ID and str(t.NAME) == NAME_KEY and str(t.TEXT) == TAB_TEXT and str(t.ICON) == icon_path(m)
              and bool(t.OWNER) == (m == OWNER_MOD) and str(t.PROTO) == WB_VERSION and str(t.BENCH) == BENCH_ID,
              "W %s WbTab constants (id, name key, text, icon, owner %s, protocol)" % (m, m == OWNER_MOD))
        bad = [i for i in allids if int(RANK[m].rank(i)) != rank_py(i)]
        check(not bad, "W %s WbRank.rank == rank_py on %d ids %s" % (m, len(allids), bad[:4]))
        cmpo = RANK[m]()
        ids = EXPECTED + EDGE_IDS
        jl = ArrayList()
        for i in reversed(ids):
            jl.add(JString(i))
        JClass("java.util.Collections").sort(jl, cmpo)
        check([str(x) for x in jl] == sort_py(ids), "W %s WbRank sorts like the Python mirror (incl. %d edge ids)" % (m, len(EDGE_IDS)))
        check(int(cmpo.compare(JString("Skyy_Sack_Omni_Recipe_Generated_0"), JString("Skyy_Sack_Omni_Recipe_Generated_0"))) == 0
              and int(cmpo.compare(JString("a"), JString("b"))) < 0, "W %s WbRank is a total order (equal ids 0, ties by name)" % m)
    want_order = tab_ids

    def ts_state(reg):
        s_ = CMAP_F.get(reg).get(TAB_ID)
        comp = s_.comparator() if s_ is not None and str(s_.getClass().getName()) == "java.util.TreeSet" else None
        return s_, (str(comp.getClass().getName()) if comp is not None else None)

    expect_mod = OWNER_MOD if OWNER_MOD in have else have[0]
    scen = [[m] for m in have]
    if len(have) == 2:
        scen += [list(have), list(reversed(have))]
    finals = []
    for order in scen:
        nm = "+".join(order)
        reg = fresh_registry()
        wb, ov, fu, bts = world()
        van_before = sorted(str(x) for x in CMAP_F.get(reg).get("Workbench_Crafting"))
        fu_arr = fu.getCategories()
        for m in order:
            line = str(TAB[m].start())
            check("on 2 Workbench definition(s)" in line, "W start %s: %s says: %s" % (nm, m, line))
        own = order[0] if len(order) == 1 else expect_mod
        w = cats_of(wb)
        check(w[:4] == VAN and len(w) == 5 and w[4] == (TAB_ID, icon_path(own), NAME_KEY),
              "W start %s: the Workbench has the 4 vanilla tabs + '%s' (%s's entry) at the end" % (nm, TAB_TEXT, own))
        o = cats_of(ov)
        check(len(o) == 6 and o[4][0] == "Workbench_Extended_Backpacks" and o[5] == (TAB_ID, icon_path(own), NAME_KEY),
              "W start %s: another mod's Workbench override keeps its 5 tabs, ours is appended" % nm)
        check(fu.getCategories() is fu_arr or fu.getCategories().equals(fu_arr), "W start %s: the Furnace is untouched" % nm)
        s_, comp = ts_state(reg)
        check(comp == PKGS[own] + ".WbRank" and [str(x) for x in s_] == want_order,
              "W start %s: the tab's recipe set is %s's TreeSet in the expected order (%d recipes)" % (nm, own, len(want_order)))
        check(sorted(str(x) for x in CMAP_F.get(reg).get("Workbench_Crafting")) == van_before == sorted(VANILLA_WB),
              "W start %s: the vanilla Crafting tab keeps exactly its %d recipes (no foreign recipe moved)" % (nm, len(VANILLA_WB)))
        arr1 = wb.getCategories()
        for m in order:
            TAB[m].start()
        check(wb.getCategories().equals(arr1) and len(cats_of(wb)) == 5 and CMAP_F.get(reg).get(TAB_ID).equals(s_)
              and ts_state(reg)[1] == comp, "W start %s: a second start changes nothing (5 tabs, same sorted set)" % nm)
        finals.append((order, w[4], comp))
    if len(have) == 2:
        check(len(set((f[1], f[2]) for f in finals[2:])) == 1, "W both start orders give the identical tab entry and order owner: %s" % finals[2:])
    # copy-on-write: the array a window is building from never changes
    reg = fresh_registry()
    wb, ov, fu, bts = world()
    before = wb.getCategories()
    TAB[expect_mod].start()
    check(len(before) == 4 and len(wb.getCategories()) == 5, "W copy-on-write: the old 4-tab array stays as it was, a new array is written")
    # recipe reload (CraftingPlugin.onRecipeLoad: removeRecipe on every registry, then addRecipe) keeps the order
    for rid in [tab_ids[0], tab_ids[30], tab_ids[-1], tab_ids[-2]]:
        reg.removeRecipe(rid)
        reg.addRecipe(req(TAB_ID), recipe(rid))
    s_, comp = ts_state(reg)
    check([str(x) for x in s_] == want_order and comp == PKGS[expect_mod] + ".WbRank", "W a recipe reload (remove + add) keeps the order")
    reg.addRecipe(req(TAB_ID), recipe("Skyy_Talisman_Crit_Epic_Recipe_Generated_0"))
    lst = [str(x) for x in ts_state(reg)[0]]
    check(lst.index("Skyy_Talisman_Crit_Epic_Recipe_Generated_0") == lst.index("Skyy_Talisman_Speed_Epic_Recipe_Generated_0") + 1,
          "W a future accessory line sorts into its tier (after the known Legendary lines)")
    reg.removeRecipe("Skyy_Talisman_Crit_Epic_Recipe_Generated_0")
    # an asset reload: NEW BlockType objects (4 vanilla tabs again) arrive through LoadedAssetsEvent -> every mod's WbAssetL
    LAEj = JClass(LAE)
    nwb = bench(BENCH_ID, VAN)
    nbt = btype("Bench_WorkBench", nwb)
    loaded = HashMap()
    loaded.put("Bench_WorkBench", nbt)
    jf(TMAP.class_, "m").get(bt_map).put("Bench_WorkBench", nbt)
    ev = LAEj(BTj.class_, None, loaded, False, None)
    for m in reversed(have):
        LIS[m]().accept(ev)
    check(len(cats_of(nwb)) == 5 and cats_of(nwb)[-1] == (TAB_ID, icon_path(expect_mod), NAME_KEY),
          "W asset reload: the new Workbench object gets the tab from the listener (%s's entry)" % expect_mod)
    # a CraftingRecipe reload event re-checks the sorted set; a set that is no longer ours is sorted again
    CMAP_F.get(reg).put(TAB_ID, JClass("java.util.HashSet")(CMAP_F.get(reg).get(TAB_ID)))
    for m in have:
        LIS[m]().accept(LAEj(CRRj.class_, None, HashMap(), False, None))
    s_, comp = ts_state(reg)
    check([str(x) for x in s_] == want_order and comp == PKGS[expect_mod] + ".WbRank", "W recipe reload event: the set is sorted again (owner's order)")
    # a REAL CraftingWindow (the server's window code): windowData = what the client receives
    try:
        bb = us.allocateInstance(BBj.class_)
        jf(BBj.class_, "grantedAugmentTags").set(bb, JClass("java.util.HashSet")())
        jf(BBj.class_, "tierLevel").setInt(bb, 1)
        # SimpleCraftingWindow = the Workbench's window (CraftingWindow is abstract; its constructor builds the tab list)
        win = JClass("com.hypixel.hytale.builtin.crafting.window.SimpleCraftingWindow")(0, 64, 0, 0, nbt, bb)
        data = win.getData()
        cats = data.get("categories").getAsJsonArray()
        rows = []
        for i in range(int(cats.size())):
            c = cats.get(i).getAsJsonObject()
            rec = c.get("craftableRecipes")
            ra = rec.getAsJsonArray() if rec is not None else None
            rows.append((str(c.get("id").getAsString()), str(c.get("name").getAsString()), str(c.get("icon").getAsString()),
                         [str(ra.get(k).getAsString()) for k in range(int(ra.size()))] if ra is not None else None))
        check([r[0] for r in rows] == [v[0] for v in VAN] + [TAB_ID], "W CraftingWindow: 5 tabs, ours last: %s" % [r[0] for r in rows])
        check(rows[4][1] == NAME_KEY and rows[4][2] == icon_path(expect_mod), "W CraftingWindow: our tab's name key and icon")
        check(rows[4][3] == want_order, "W CraftingWindow: craftableRecipes of our tab = the %d recipes in crafting order (Omni Bag last)" % len(want_order))
        check(sorted(rows[2][3] or []) == sorted(VANILLA_WB), "W CraftingWindow: the vanilla Crafting tab lists only its vanilla recipes")
        out.append("W. a real CraftingWindow sends tabs %s; '%s' craftableRecipes: %s ... %s" % (
            ", ".join(r[0] for r in rows), TAB_TEXT, ", ".join(base_py(x) for x in rows[4][3][:4]), ", ".join(base_py(x) for x in rows[4][3][-3:])))
    except Exception as e:
        check(False, "W CraftingWindow could not be built in the bare JVM: %s" % e)
    REGS.clear()
    jf(TMAP.class_, "m").get(bt_map).clear()
    jf(BTj.class_, "ASSET_STORE").set(None, None)
    out.append("W. scenarios: %s; final entry icon %s, order %s" % ("; ".join("+".join(f[0]) for f in finals), finals[-1][1][1], finals[-1][2]))
    return out
