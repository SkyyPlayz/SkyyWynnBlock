"""Bare-JVM check for SkyyCooking 0.1.4 (food Grade strength S = 1 + 0.32 x Grade, duration D = 2^(Grade/5) unchanged, the new tooltip
wording, the campfire pick on the strength part, Cooking XP default 0.5 + the one-time xpMultiplier update), kept next to the build so the
build report's claims can be re-run.

    python SkyyCooking/test_skyycooking_0.1.4.py [--jar <0.1.4 jar>] [--old <0.1.3 jar>] [--live <Skyy_SkyyCooking folder>] [--dir <scratch>] [--keep]

Build first (python SkyyCooking/build_skyycooking_0.1.4.py). The parent copies the live Skyy_SkyyCooking folder (READ ONLY; default: the
"HUD mod" world's mods/Skyy_SkyyCooking: cooking.properties, config-history/, config-changes.log) into the scratch folder and starts a
child: a fresh JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar + the 0.1.4 jar + tools/javassist.jar,
java.io.tmpdir / TEMP / TMP in the scratch folder).
Checks:
  A  every 0.1.4 class loads and verifies (-Xverify:all)
  B  the factor tables CookCfg.SF / DF / MUL (S = 1 + 0.32 x g exactly, D = 2^(g/5) to 4 decimals, MUL = S); the Cooking XP default: row
     xpMultiplier (dec 0-100 x, default 0.5, the new help), CookCfg.DEF_XP_MULT / XP_MULT, the generated default text (xpMultiplier=0.5 with
     the 0.1.4 marker above its help line; the 0.1.3 campfire marker still there); the loader: missing line / junk -> 0.5, 1.0 and 0.7 kept
  C  the generated assets in the jar against Assets.zip: every Grade 1-12 effect = the vanilla JSON with its strength fields x S(g) and its
     Duration x D(g) (spelled out per number), every other key untouched, durations byte-equal to 0.1.3's; the 108 family checks re-derived
     from the jar's numbers (EffectCondition on every stronger member, clear every weaker one, apply this one); the 180 dish items equal to
     0.1.3's; every tooltip rebuilt from the jar's own effect numbers ("Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses. Heal
     and buffs x1.64 stronger, buffs last x1.32 longer." ...); the Meat Pie and Vegetable Skewer numbers for Grades 1-12 printed
  D  the campfire pick through the COMPILED path: Cook.campGrade = floor(buffFactor x Grade) for several factors; Cook.campfire and the bridge
     Function cook:fn:campfire with a fake Campfire recipe (fake skill:fn:level / tree:fn:level / skill:fn:addxp) at Cooking 0-100 with and
     without Master Chef -> Skyy_Cook_<dish>_G<floor(0.75 x Grade)>; the XP it sends = round(1,600 x 0.25) x xpMultiplier (200 at 0.5)
  E  the texts through the compiled code: Cook.sd / sdShort for every Grade, Cook.campText, Cook.cookingLines (the /cooking reply: Skyy's
     Cooking 15 + Master Chef case, Cooking 5, 100, graded cooking off, no SkyySkills), the Skills Stats lines (CookStatsFn), and the
     "Your food now comes out Grade N" line of the byte-identical CookXpTask from the tables
  F  the one-time update CookXpMig.migrate on scratch COPIES of the live cooking.properties: (a) the live file (exact bytes: one value line
     1.0 -> 0.5 + the marker above its help line, History copy = the old bytes + index line, one config-changes.log line in the kit format,
     the INFO line, the loader reads 0.5, java.util.Properties sees one changed key), (b) second start: nothing, (c) a hand-set 0.7 kept +
     noted, (c2) a 0.5 set in Server Setup first kept ("already 0.5"), (c3) the kit's canonical 1 -> 0.5, (c4) 1.00 / 2 / 0 / a continued
     entry kept, (d) CRLF kept, (e) no file -> nothing; the fresh 0.1.4 file is marked + 0.5 and never updates, (f) no xpMultiplier line ->
     marker above the first entry only, (g) a 0.1.2-era file gets both updates in setup()'s order (two History copies, two Undo-able lines),
     (h) History blocked -> WARN, file untouched, then updated once it can be kept; a folder in place of the file -> nothing, (i) the whole
     start with the config kit: config:fn get 0.5, the log op lists the update (status ok = Undo offered), versions lists the History copy,
     restore preview shows the value going back, a set back to 1.0 (the Undo path) writes 1, keeps the marker, reaches the running field
     and survives the next start
  G  the pure text step CookXpMig.update on 3000 random files checked against java.util.Properties
  H  start twice on a scratch COPY of the live data folder, the way setup() starts (CookMig.migrate, CookXpMig.migrate, CookCfg.load,
     CfgPub.start / flush / shutdown): the first start updates once (History + change log + 1 each), the second changes nothing (files and
     modified times)
  I  class compare 0.1.3 vs 0.1.4 (normalised per-member disassembly + constant values) and asset compare; setup() order (bytecode)
Not testable without the game (UNVERIFIED): eating the dishes (the effect assets are checked as data), the chat lines on a client, SkyySkills
adding the XP, the Server Setup page drawing Changes / History, a real Undo click (the harness sends the same set op with via console).
Nothing is deployed and nothing under AppData is written. Default scratch folder tools/dev/scratch/cook014/harness (deleted unless --keep).
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, zipfile, json, random, time, math, copy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, OLD = "0.1.4", "0.1.3"
PKG = "com.skyy.cooking."
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE_DEFAULT = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyCooking")
DEPLOYED = os.path.join(APPDATA, "Hytale", "UserData", "Mods", "SkyyCooking.jar")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cook014", "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLDJAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyCooking-%s.jar" % OLD)))
LIVE = os.path.abspath(arg("--live", LIVE_DEFAULT))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


XP_MARK = ("# SkyyCooking 0.1.4 Cooking XP (Skyy 2026-10-02): cooking levelled too fast - every Cooking XP award is halved - "
           "xpMultiplier default 0.5, was 1")
XP_HELP = "# multiplies every Cooking XP award (SkyySkills' own global multiplier applies on top)"
CAMP_MARK = ("# SkyyCooking 0.1.3 campfire XP (Skyy 2026-10-01): campfire accessory dishes pay a quarter of the Cooking Bench XP - "
             "campfire.xpFactor default 0.25, was 0.5")
ROW_HELP = "Multiplies every Cooking XP award. Default 0.5 = half. SkyySkills' XP multiplier applies on top."
INFO_LIVE = ("cooking.properties updated to the 0.1.4 Cooking XP default: xpMultiplier 1.0 -> 0.5 (Skyy 2026-10-02: cooking levelled too "
             "fast - every Cooking XP award is halved; the old file is in config-history; Server Setup -> Changes can undo it)")
INFO_CAMP = ("cooking.properties updated to the 0.1.3 campfire XP share: campfire.xpFactor 0.5 -> 0.25 (Skyy 2026-10-01: campfire cooking "
             "pays half the XP it did; the old file is in config-history; Server Setup -> Changes can undo it)")
CAMP = {"Food_Wildmeat_Cooked": 1600, "Food_Fish_Grilled": 2000, "Food_Vegetable_Cooked": 1200}
DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
INSTANT = ["Food_Instant_Heal_T1", "Food_Instant_Heal_T2", "Food_Instant_Heal_T3", "Food_Instant_Heal_Bread"]
FAMILIES = ["HealthRegen", "Meat", "FruitVeggie"]
BASES = INSTANT + ["%s_Buff_T%d" % (f, t) for f in FAMILIES for t in (1, 2, 3)]
W = '<color is="#ffffff">%s</color>'


def S(g):
    return 1.0 + 0.32 * g          # Skyy's strength rule (the build uses the exact quotient (100 + 32 g) / 100)


def D(g):
    return 2.0 ** (g / 5.0)        # the duration rule, unchanged (= 0.1.3's single multiplier M)


def jround(v):
    """java.lang.Math.round(double) (floor(x + 0.5))"""
    return int(math.floor(v + 0.5))


def x2(v):
    c = jround(v * 100.0)
    return "%d.%02d" % (c // 100, c % 100)


def expected_update(text, new_value="0.5", old_value="1.0"):
    """the live shape: the 0.1.4 marker on its own line right above the xpMultiplier help comment, the old value line -> 0.5, endings kept"""
    nl = "\r\n" if "\r\n" in text else "\n"
    out = text
    if new_value is not None:
        a_ = nl + "xpMultiplier=" + old_value + nl
        assert out.count(a_) == 1, old_value
        out = out.replace(a_, nl + "xpMultiplier=" + new_value + nl)
    assert out.count(nl + XP_HELP + nl) == 1
    return out.replace(nl + XP_HELP + nl, nl + XP_MARK + nl + XP_HELP + nl)


# ============================================================================================================== C (pure Python)
def section_c():
    import skyybuild as B
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    anames = AZ.namelist()

    def vjson(prefix, iid):
        n = [x for x in anames if x.startswith(prefix) and x.endswith("/" + iid + ".json")]
        return json.loads(AZ.read(n[0]).decode("utf-8-sig"))
    vlang = {}
    for l in AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
        if "=" in l and not l.lstrip().startswith("#"):
            k, v = l.split("=", 1)
            vlang[k.strip()] = v.strip()
    z4, z3 = zipfile.ZipFile(JAR), zipfile.ZipFile(OLDJAR)

    def jj(z, p):
        return json.loads(z.read(p).decode("utf-8"))
    VB = dict((b, vjson("Server/Entity/Effects/", b)) for b in BASES)

    def r4(v):
        return float("%.4f" % v)

    def expect(b, g):
        d = copy.deepcopy(VB[b])
        s_, d_ = (100 + 32 * g) / 100.0, D(g)
        for k, v in d.get("StatModifiers", {}).items():
            d["StatModifiers"][k] = r4(v * s_)
        for stat, lst in d.get("RawStatModifiers", {}).items():
            for m in lst:
                m["Amount"] = r4(1.0 + (m["Amount"] - 1.0) * s_) if m.get("CalculationType") == "Multiplicative" else r4(m["Amount"] * s_)
        for typ, lst in d.get("DamageResistance", {}).items():
            for m in lst:
                m["Amount"] = r4(m["Amount"] * s_)
        if VB[b].get("Duration", 0) > 0.5:
            d["Duration"] = float("%.2f" % (VB[b]["Duration"] * d_))
        return d

    def strength_numbers(d):
        """(label, value) of every strength field: StatModifiers values, the BONUS part (Amount - 1) of multiplicative max-stat modifiers,
        damage resistance"""
        out = []
        for k, v in sorted(d.get("StatModifiers", {}).items()):
            out.append(("StatModifiers." + k, float(v)))
        for stat, lst in sorted(d.get("RawStatModifiers", {}).items()):
            for i, m in enumerate(lst):
                out.append(("RawStatModifiers.%s[%d] bonus" % (stat, i), float(m["Amount"]) - 1.0))
        for typ, lst in sorted(d.get("DamageResistance", {}).items()):
            for i, m in enumerate(lst):
                out.append(("DamageResistance.%s[%d]" % (typ, i), float(m["Amount"])))
        return out
    n_num = n_dur = n_same_dur = 0
    for b in BASES:
        v0 = VB[b]
        for g in range(1, 13):
            p = "Server/Entity/Effects/SkyyCook/Skyy_Cook_%s_G%d.json" % (b, g)
            e = jj(z4, p)
            check(e == expect(b, g), "C: %s Grade %d = vanilla with strength x S(%d) and Duration x D(%d), every other key untouched" % (b, g, g, g))
            sb, se = strength_numbers(v0), strength_numbers(e)
            check([x[0] for x in sb] == [x[0] for x in se], "C: %s G%d has the vanilla strength fields" % (b, g))
            for (lb, vb), (le, ve) in zip(sb, se):
                ok = abs(ve - vb * S(g)) <= 0.00005 + 1e-12
                check(ok, "C: %s G%d %s = %s x %.2f = %.5f (jar %s)" % (b, g, lb, vb, S(g), vb * S(g), ve))
                n_num += 1
            if v0.get("Duration", 0) > 0.5:
                check(abs(e["Duration"] - v0["Duration"] * D(g)) <= 0.005 + 1e-9, "C: %s G%d Duration = %s x %.4f (jar %s)" % (b, g, v0["Duration"], D(g), e["Duration"]))
            else:
                check(e["Duration"] == v0["Duration"], "C: %s G%d instant Duration kept (%s)" % (b, g, e["Duration"]))
            n_dur += 1
            e3 = jj(z3, p)
            check(e3.get("Duration") == e.get("Duration"), "C: %s G%d Duration byte-equal to 0.1.3 (%s / %s)" % (b, g, e3.get("Duration"), e.get("Duration")))
            n_same_dur += 1 if e3.get("Duration") == e.get("Duration") else 0
    print("C. %d effects: %d strength numbers = vanilla x (1 + 0.32 x Grade), %d durations = vanilla x 2^(Grade/5) (all %d equal to 0.1.3's)"
          % (len(BASES) * 12, n_num, n_dur, n_same_dur))

    # ---- family checks re-derived from the jar's numbers (vanilla Grade 0 members included)
    def strength(fam, d):
        if fam == "HealthRegen":
            return d["StatModifiers"]["Health"]
        if fam == "Meat":
            return d["RawStatModifiers"]["Health"][0]["Amount"]
        return d["RawStatModifiers"]["Stamina"][0]["Amount"]
    n_chk = 0
    reorders = 0
    for fam in FAMILIES:
        mem = []
        for t in (1, 2, 3):
            for g in range(0, 13):
                bid = "%s_Buff_T%d" % (fam, t)
                d = VB[bid] if g == 0 else jj(z4, "Server/Entity/Effects/SkyyCook/Skyy_Cook_%s_G%d.json" % (bid, g))
                mem.append(((round(strength(fam, d), 6), round(d["Duration"], 4), t, g), bid if g == 0 else "Skyy_Cook_%s_G%d" % (bid, g), t, g))
        mem.sort()
        ids = [m[1] for m in mem]
        for i, (key, eid, t, g) in enumerate(mem):
            if g == 0:
                continue
            cid = "Skyy_Cook_%s_Check_T%d_G%d" % (fam, t, g)
            node = jj(z4, "Server/Item/Interactions/SkyyCook/%s.json" % cid)
            above, below = ids[i + 1:], ids[:i]
            serial = node["Next"] if node.get("Type") == "EffectCondition" else node
            got_above = node.get("EntityEffectIds", []) if node.get("Type") == "EffectCondition" else []
            inter = serial.get("Interactions", [])
            clears = [x.get("EntityEffectId") for x in inter[:-1] if x.get("Type") == "ClearEntityEffect"]
            ok = (set(got_above) == set(above) and len(got_above) == len(above) and set(clears) == set(below) and len(clears) == len(inter) - 1
                  and inter[-1] == {"Type": "ApplyEffect", "EffectId": eid} and serial.get("Type") == "Serial"
                  and (not above or (node.get("Match") == "None" and node.get("Failed") == {"Type": "Simple", "RunTime": 0})))
            check(ok, "C: family check %s: blocked by every stronger member (%d), clears every weaker one (%d), applies %s" % (cid, len(above), len(below), eid))
            n_chk += 1
            old = jj(z3, "Server/Item/Interactions/SkyyCook/%s.json" % cid)
            if old != node:
                reorders += 1
    print("C. %d family checks re-derived from the jar's numbers (a weaker buff never replaces a stronger one); %d differ from 0.1.3 (re-ranked)"
          % (n_chk, reorders))

    # ---- dish items + tooltips
    lang = {}
    for l in z4.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n"):
        if "=" in l:
            k, v = l.split("=", 1)
            lang[k] = v
    ROMAN = {1: "I", 2: "II", 3: "III"}

    def pct_s(v):
        return ("%.1f" % v).rstrip("0").rstrip(".")

    def num_s(v):
        return ("%.3f" % v).rstrip("0").rstrip(".")

    def mmss(sec):
        s_ = int(round(sec))
        return "%d:%02d" % (s_ // 60, s_ % 60)
    n_items = n_tips = 0
    rows = {}
    for dish in DISHES:
        name = vlang.get("items.%s.name" % dish) or dish
        for g in range(1, 13):
            gid = "Skyy_Cook_%s_G%d" % (dish, g)
            p = "Server/Item/Items/SkyyCook/%s.json" % gid
            check(z4.read(p) == z3.read(p), "C: dish item %s is byte-identical to 0.1.3 (ids, eat chain, Quality)" % gid)
            n_items += 1
            it = jj(z4, p)
            chain = it["InteractionVars"]["Effect"]["Interactions"]
            check(isinstance(chain[0], dict) and chain[0].get("Type") == "ApplyEffect" and str(chain[0].get("EffectId", "")).endswith("_G%d" % g)
                  and all(isinstance(c, str) and c.endswith("_G%d" % g) for c in chain[1:]), "C: %s eats Grade %d effects only" % (gid, g))
            heal_e = jj(z4, "Server/Entity/Effects/SkyyCook/%s.json" % chain[0]["EffectId"])
            heal = heal_e["StatModifiers"]["Health"]
            bullets, dur = [], 0.0
            row = {"heal": heal}
            for c in chain[1:]:
                m = re.match(r"^Skyy_Cook_(HealthRegen|Meat|FruitVeggie)_Check_T([123])_G(\d+)$", c)
                fam, k = m.group(1), int(m.group(2))
                e = jj(z4, "Server/Entity/Effects/SkyyCook/Skyy_Cook_%s_Buff_T%d_G%d.json" % (fam, k, g))
                dur = max(dur, e["Duration"])
                if fam == "HealthRegen":
                    row["regen"] = e["StatModifiers"]["Health"]
                    bullets.append("\u2022 " + W % ("Health Regen " + ROMAN[k]) + " (%s%% health every %s s)" % (pct_s(e["StatModifiers"]["Health"]), pct_s(e["DamageCalculatorCooldown"])))
                elif fam == "Meat":
                    res = e.get("DamageResistance", {}).get("Physical", [{}])[0].get("Amount")
                    row["maxHealth"] = (e["RawStatModifiers"]["Health"][0]["Amount"] - 1.0) * 100.0
                    if res:
                        row["res"] = res * 100.0
                    bullets.append("\u2022 " + W % ("Health Boost " + ROMAN[k]) + " (+%s%% max health%s)" % (
                        pct_s((e["RawStatModifiers"]["Health"][0]["Amount"] - 1.0) * 100.0),
                        (", %s%% less physical and projectile damage" % pct_s(res * 100.0)) if res else ""))
                else:
                    st = e.get("StatModifiers", {}).get("Stamina")
                    row["maxStamina"] = (e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1.0) * 100.0
                    if st:
                        row["stamina"] = st
                    bullets.append("\u2022 " + W % ("Stamina Boost " + ROMAN[k]) + " (+%s%% max stamina%s)" % (
                        pct_s((e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1.0) * 100.0),
                        (", +%s stamina every %s s" % (num_s(st), pct_s(e["DamageCalculatorCooldown"]))) if st else ""))
            row["dur"] = dur
            rows[(dish, g)] = row
            if g <= 10:
                head = "Grade %d food - Cooking %d, or sooner with Cooking tree bonuses." % (g, g * 10)
            else:
                head = "Grade %d food - only a Cooking skill tree bonus reaches it." % g
            head += " Heal and buffs " + W % ("x%.2f" % S(g)) + " stronger, buffs last " + W % ("x%.2f" % D(g)) + " longer."
            body = "Instantly restores " + W % (pct_s(heal) + "%") + " health"
            if bullets:
                body += " and grants:\\n\\n" + "\\n".join(bullets) + "\\n\\nDuration: " + W % mmss(dur)
            else:
                body += "."
            want = head + "\\n\\n" + body
            for pre in ("items.", "server.items."):
                check(lang.get("%s%s.name" % (pre, gid)) == "%s (Grade %d)" % (name, g), "C: %s%s.name" % (pre, gid))
                got = lang.get("%s%s.description" % (pre, gid))
                check(got == want, "C: %s%s.description rebuilt from the jar's own numbers:\n   got  %r\n   want %r" % (pre, gid, got, want))
                n_tips += 1
    check(not any("cooked at Cooking" in v for v in lang.values()), "C: no tooltip says 'cooked at Cooking N or higher' any more")
    print("C. %d dish items byte-identical to 0.1.3; %d tooltip lines rebuilt from the jar's numbers (new head wording); e.g. Meat Pie G2:" % (n_items, n_tips))
    print("   " + lang["server.items.Skyy_Cook_Food_Pie_Meat_G2.description"].split("\\n\\n")[0].replace(W % "x1.64", "x1.64").replace(W % "x1.32", "x1.32"))

    # ---- the numbers table (Grades 1-12) for a pie and a skewer, base values from Assets.zip, factors S / D
    def table(dish, cols):
        base = {}
        v = vjson("Server/Item/Items/", dish)
        for e in v["InteractionVars"]["Effect"]["Interactions"]:
            if isinstance(e, dict):
                base["heal"] = VB[e["EffectId"]]["StatModifiers"]["Health"]
            else:
                m = re.match(r"^(HealthRegen|Meat|FruitVeggie)_TierCheck_T([123])$", e)
                d = VB["%s_Buff_T%s" % (m.group(1), m.group(2))]
                base["dur"] = max(base.get("dur", 0), d["Duration"])
                if m.group(1) == "HealthRegen":
                    base["regen"] = d["StatModifiers"]["Health"]
                elif m.group(1) == "Meat":
                    base["maxHealth"] = (d["RawStatModifiers"]["Health"][0]["Amount"] - 1.0) * 100.0
                    r_ = d.get("DamageResistance", {}).get("Physical", [{}])[0].get("Amount")
                    if r_:
                        base["res"] = r_ * 100.0
                else:
                    base["maxStamina"] = (d["RawStatModifiers"]["Stamina"][0]["Amount"] - 1.0) * 100.0
                    if d.get("StatModifiers", {}).get("Stamina"):
                        base["stamina"] = d["StatModifiers"]["Stamina"]
        hdr = "   %-6s %-11s" % ("Grade", "S / D") + "".join("%-15s" % c[1] for c in cols)
        print("   " + "%s (%s) - base (vanilla) = Grade 0; every strength number = base x S, duration = base x D" % (vlang.get("items.%s.name" % dish), dish))
        print(hdr)
        print("   %-6s %-11s" % ("0", "1.00/1.00") + "".join("%-15s" % c[2](base[c[0]]) for c in cols))
        for g in range(1, 13):
            r_ = rows[(dish, g)]
            cells = []
            for key, _lab, fmt in cols:
                want = base[key] * (D(g) if key == "dur" else S(g))
                ok = abs(r_[key] - want) <= (0.006 if key == "dur" else 0.0051 if key in ("maxHealth", "maxStamina", "res") else 0.00006)
                check(ok, "C: table %s G%d %s = base %s x %s = %s (jar %s)" % (dish, g, key, base[key], "D" if key == "dur" else "S", want, r_[key]))
                cells.append(fmt(r_[key]))
            print("   %-6d %-11s" % (g, "%.2f/%.2f" % (S(g), D(g))) + "".join("%-15s" % c for c in cells))
    print("C. numbers table (from the jar):")
    table("Food_Pie_Meat", [("heal", "heal %", lambda v: "%.2f" % v), ("regen", "regen %/2s", lambda v: "%.3f" % v),
                            ("maxHealth", "max health +%", lambda v: "%.2f" % v), ("res", "resist %", lambda v: "%.2f" % v),
                            ("dur", "duration", lambda v: "%.2f s %s" % (v, mmss(v)))])
    table("Food_Kebab_Vegetable", [("heal", "heal %", lambda v: "%.2f" % v), ("regen", "regen %/2s", lambda v: "%.3f" % v),
                                   ("maxStamina", "max stam +%", lambda v: "%.2f" % v), ("stamina", "stam/0.1s", lambda v: "%.4f" % v),
                                   ("dur", "duration", lambda v: "%.2f s %s" % (v, mmss(v)))])


# ============================================================================================================== child
def run():
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, JAR, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()

    # ---------------- A. load + verify
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(JAR).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    J = lambda n: JClass(PKG + n)
    Cfg, Cook, Mig, XMig, Rows, CfgPub = J("CookCfg"), J("Cook"), J("CookMig"), J("CookXpMig"), J("CfgRows"), J("CfgPub")
    Paths, Props, Integer = JClass("java.nio.file.Paths"), JClass("java.util.Properties"), JClass("java.lang.Integer")
    UUID, HashMap, CHM, System = JClass("java.util.UUID"), JClass("java.util.HashMap"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.lang.System")
    BAIS = JClass("java.io.ByteArrayInputStream")
    Bool = JClass("java.lang.Boolean")
    OA = JArray(JObject)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)

    def jfield(cls, name):
        c = cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    # ---------------- B. factor tables + the XP default
    sf, df, mu = [float(x) for x in Cfg.SF], [float(x) for x in Cfg.DF], [float(x) for x in Cfg.MUL]
    check(len(sf) == len(df) == len(mu) == 13, "B: 13 factor entries (Grade 0-12)")
    check(all(abs(sf[g] - S(g)) < 1e-12 for g in range(13)) and sf == mu, "B: CookCfg.SF = MUL = 1 + 0.32 x Grade: %s" % sf)
    check(all(abs(df[g] - round(D(g), 4)) < 1e-12 for g in range(13)), "B: CookCfg.DF = 2^(Grade/5) (4 decimals): %s" % df)
    check([round(sf[g], 2) for g in (1, 2, 5, 10, 11, 12)] == [1.32, 1.64, 2.6, 4.2, 4.52, 4.84], "B: Skyy's numbers x1.32 / x1.64 / x2.6 / x4.2 / x4.52 / x4.84")
    keys = [str(k) for k in Rows.KEYS]
    xi = keys.index("xpMultiplier") if "xpMultiplier" in keys else -1
    check(xi >= 0, "B: row xpMultiplier exists")
    if xi >= 0:
        check(str(Rows.LABELS[xi]) == "Cooking XP multiplier" and str(Rows.TYPES[xi]) == "dec" and str(Rows.DEFS[xi]) == "0.5"
              and str(Rows.MINS[xi]) == "0" and str(Rows.MAXS[xi]) == "100" and str(Rows.CATS[xi]) == "xp" and str(Rows.UNITS[xi]) == "x"
              and set(str(Rows.FLAGS[xi]).split(",")) == {"live", "danger"}, "B: row = Cooking XP multiplier, dec 0-100 x, default 0.5, live + danger, Cooking XP tab")
        check(str(Rows.HELPS[xi]) == ROW_HELP and len(ROW_HELP) <= 100, "B: row help: %s" % str(Rows.HELPS[xi]))
    for k_, d_ in (("campfire.xpFactor", "0.25"), ("campfire.buffFactor", "0.75"), ("maxGrade", "12"), ("enabled", "true")):
        check(str(Rows.DEFS[keys.index(k_)]) == d_, "B: row %s default stays %s" % (k_, d_))
    check(str(Rows.VERSION) == VERSION and int(Rows.KEEP) == 20 and str(Rows.KIT) == "1.1", "B: kit version 1.1, KEEP 20, VERSION 0.1.4")
    check(abs(float(Cfg.DEF_XP_MULT) - 0.5) < 1e-12 and abs(float(Cfg.XP_MULT) - 0.5) < 1e-12, "B: CookCfg.DEF_XP_MULT / XP_MULT = 0.5")
    dflt = str(Cfg.DEFAULTS)
    check(dflt.startswith("# SkyyCooking 0.1.4 - cooking.properties") and dflt.count("\nxpMultiplier=0.5\n") == 1
          and dflt.count("\n" + XP_MARK + "\n" + XP_HELP + "\nxpMultiplier=0.5\n") == 1 and "xpMultiplier=1" not in dflt
          and dflt.count("\n" + CAMP_MARK + "\n") == 1 and "\ncampfire.xpFactor=0.25\n" in dflt,
          "B: default file: xpMultiplier=0.5 with the 0.1.4 marker above its help line; the 0.1.3 campfire marker + 0.25 still there")
    check("Heal and buffs x(1 + 0.32 x Grade), buffs last" in dflt and "x2 at Grade 5 / x4" not in dflt, "B: default file comment names S and D")
    blk = str(Cfg.CAMP_BLOCK)
    check(blk.startswith("\n# Campfire ACCESSORY") and blk.endswith("\n" + CAMP_MARK + "\n# campfire.xpFactor = share of the Cooking XP the same dish pays at a Cooking Bench (its xp.<dish> line). 0..1\ncampfire.xpFactor=0.25\n")
          and "bench Grade 5 (x2.60) -> Grade 3 (x1.96), Grade 10 (x4.20) -> Grade 7 (x3.24)" in blk,
          "B: the 0.1 append block: strength wording, marker + 0.25")
    bdir = os.path.join(SCRATCH, "work", "b-loader")
    os.makedirs(bdir)
    bf = os.path.join(bdir, "cooking.properties")
    Cfg.FILE = Paths.get(bf)
    base_txt = dflt.replace("xpMultiplier=0.5\n", "")
    for line, want, name in (("", 0.5, "missing line"), ("xpMultiplier=abc\n", 0.5, "junk"), ("xpMultiplier=1.0\n", 1.0, "1.0 (a kept value)"),
                             ("xpMultiplier=0.7\n", 0.7, "0.7"), ("xpMultiplier=-2\n", 0.0, "-2 -> 0")):
        open(bf, "w", encoding="latin-1", newline="").write(base_txt + line)
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - want) < 1e-12, "B: loader %s -> XP_MULT %s (got %s)" % (name, want, float(Cfg.XP_MULT)))
    print("B. factor tables S / D / MUL, default 0.5: row, fields, default text, append block, loader checked")

    # ---------------- C. assets (pure Python, from the jar)
    section_c()

    # ---------------- D. the campfire pick through the compiled path
    for f_ in (0.75, 0.5, 0.25, 0.9, 0.33, 0.1, 1.0, 0.0, 1.5, -1.0):
        got = [int(Cook.campGrade(g, f_)) for g in range(13)]
        want = [g if f_ >= 1.0 else (0 if f_ <= 0.0 else int(math.floor(f_ * g + 1e-9))) for g in range(13)]
        check(got == want, "D: compiled Cook.campGrade(g, %s) = floor(%s x g): %s (want %s)" % (f_, f_, got, want))
    print("D. compiled Cook.campGrade = floor(buffFactor x bench Grade): 0.75 -> %s" % [int(Cook.campGrade(g, 0.75)) for g in range(13)])
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FakeStore = fake.toClass(AS.class_)
    am_field = jfield(AS.class_, "assetMap")
    dam_field = jfield(DAM.class_, "assetMap")

    def fake_store(asset_cls, mapping):
        """asset_cls.ASSET_STORE = a never-constructed store whose DefaultAssetMap reads this java.util.HashMap"""
        st = us.allocateInstance(FakeStore)
        dm = DAM()
        hm = HashMap()
        for k_, v_ in mapping.items():
            hm.put(k_, v_)
        dam_field.set(dm, hm)
        am_field.set(st, dm)
        jfield(asset_cls.class_, "ASSET_STORE").set(None, st)

    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    BTP = JClass("com.hypixel.hytale.protocol.BenchType")
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    id_field = jfield(CRR.class_, "id")

    def recipe(rid, out, bench):
        r_ = CRR(JArray(MQ)([MQ("Food_Wildmeat_Raw", None, None, 1, None)]), MQ(out, None, None, 1, None), JArray(MQ)([MQ(out, None, None, 1, None)]),
                 1, JArray(BRQ)([BRQ(BTP.Crafting, bench, None, 0, None)]), 1.0, False, 0)
        id_field.set(r_, rid)
        return r_

    RID = dict((d, d + "_Recipe_Generated_0") for d in CAMP)
    recs = dict((RID[d], recipe(RID[d], d, "Campfire")) for d in CAMP)
    recs["Skyy_Cook_Recipe_Wildmeat"] = recipe("Skyy_Cook_Recipe_Wildmeat", "Food_Wildmeat_Cooked", "Cookingbench")
    fake_store(CRR, recs)
    items = {}
    for d in DISHES:
        for g in range(1, 13):
            items["Skyy_Cook_%s_G%d" % (d, g)] = us.allocateInstance(ITM.class_)
    fake_store(ITM, items)
    check(CRR.getAssetMap().getAsset(RID["Food_Wildmeat_Cooked"]) is not None and bool(Cook.isCampfire(CRR.getAssetMap().getAsset(RID["Food_Wildmeat_Cooked"]))),
          "D: fake Campfire recipe is in the asset map")
    calls = []

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    level = [50]
    mchef = [0]
    bridge.put("skill:fn:level", Fn(lambda a: Integer(level[0])))
    bridge.put("tree:fn:level", Fn(lambda a: Integer(mchef[0] if str(a[1]) == "Cooking.CMaster" else 0)))

    def addxp(a):
        calls.append((str(a[0]), str(a[1]), int(a[2].longValue()), str(a[3])))
        return Bool.TRUE
    bridge.put("skill:fn:addxp", Fn(addxp))
    cdir = os.path.join(SCRATCH, "work", "d-camp")
    os.makedirs(cdir)
    Cfg.FILE = Paths.get(os.path.join(cdir, "cooking.properties"))
    Cfg.load()                                   # a fresh 0.1.4 file: xpMultiplier 0.5, campfire 0.75 / 0.25
    check(abs(float(Cfg.XP_MULT) - 0.5) < 1e-12 and abs(float(Cfg.CAMP_BUFF) - 0.75) < 1e-12 and abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12,
          "D: fresh 0.1.4 file: xpMultiplier 0.5, campfire buff 0.75, campfire XP 0.25")
    U = UUID.fromString("00000000-0000-0000-0000-00000000c014")

    def camp(dish, n, rid=None):
        del calls[:]
        r_ = Cook.campfire(U, rid or RID[dish], n, None, Bool.FALSE)
        Cook.RATE.clear()
        Cook.CAMP_TOLD.clear()
        return r_, sum(c[2] for c in calls)
    seen = []
    for lv in (0, 5, 9, 10, 15, 19, 20, 30, 40, 50, 60, 70, 80, 90, 99, 100, 130):
        for mc in (0, 1):
            level[0], mchef[0] = lv, mc
            G = max(0, min(min(lv // 10, 10) + mc, 12))
            c = int(math.floor(0.75 * G + 1e-9))
            r_, sent = camp("Food_Wildmeat_Cooked", 1)
            want_id = "Skyy_Cook_Food_Wildmeat_Cooked_G%d" % c if c > 0 else "Food_Wildmeat_Cooked"
            check(r_ is not None and str(r_[0]) == want_id and int(r_[1]) == G and int(r_[2]) == c and sent == 200,
                  "D: Cooking %d%s -> bench Grade %d -> campfire Grade %d (%s), 200 XP (got %s, %s)" % (
                      lv, " + Master Chef" if mc else "", G, c, want_id, None if r_ is None else [str(x) for x in r_], sent))
            if (G, c) not in seen:
                seen.append((G, c))
    print("D. Cook.campfire end to end: bench Grade -> campfire Grade %s; one Cooked Wildmeat sends 200 XP (1,600 x 0.25 x xpMultiplier 0.5)"
          % ", ".join("G%d->G%d" % x for x in sorted(seen)))
    level[0], mchef[0] = 100, 0
    fnc = J("CookCampFn")()
    del calls[:]
    gid = fnc.apply(OA([U, RID["Food_Fish_Grilled"], Integer(2), None, Bool.FALSE]))
    Cook.RATE.clear()
    check(str(gid) == "Skyy_Cook_Food_Fish_Grilled_G7" and sum(c[2] for c in calls) == 500,
          "D: the bridge Function cook:fn:campfire (SkyySacks' call) at Cooking 100: Grilled Fish Grade 7, 2 x 2,000 x 0.25 x 0.5 = 500 XP (%s, %d)"
          % (gid, sum(c[2] for c in calls)))
    Cfg.XP_MULT = 1.0
    r_, sent = camp("Food_Wildmeat_Cooked", 1)
    check(sent == 400, "D: xpMultiplier 1 (the 0.1.3 default) on the same code sends 400 for one wildmeat - 0.1.4's 0.5 halves it (200)")
    Cfg.XP_MULT = 0.5
    r_, sent = camp("Food_Wildmeat_Cooked", 1, rid="Skyy_Cook_Recipe_Wildmeat")
    check(r_ is None and sent == 0, "D: a Cooking Bench recipe is still refused by the campfire path")
    Cfg.CAMP_BUFF = 0.5
    level[0] = 100
    r_, sent = camp("Food_Wildmeat_Cooked", 0)
    check(int(r_[2]) == 5 and sent == 0, "D: buffFactor 0.5 at bench Grade 10 -> campfire Grade 5 (preview, no XP)")
    Cfg.CAMP_BUFF = 0.75

    # ---------------- E. texts through the compiled code
    for g in range(13):
        check(str(Cook.sd(g)) == "heal and buffs x%s stronger, buffs last x%s longer" % (x2(sf[g]), x2(df[g])), "E: Cook.sd(%d) = %s" % (g, str(Cook.sd(g))))
        check(str(Cook.sdShort(g)) == "x%s stronger and x%s longer" % (x2(sf[g]), x2(df[g])), "E: Cook.sdShort(%d) = %s" % (g, str(Cook.sdShort(g))))
    print("E. Cook.sd: " + " | ".join("G%d %s" % (g, str(Cook.sdShort(g))) for g in (1, 2, 5, 10, 12)))
    pre = "Campfire accessory = quick emergency cooking: your campfire dishes come out "
    post = " and pay 25% of the Cooking XP. A Cooking Bench gives the full Grade and XP."
    for g, c, mid in ((5, 3, "Grade 3 (75% of your Grade 5 strength bonus - heal and buffs x1.96 stronger, buffs last x1.52 longer)"),
                      (10, 7, "Grade 7 (75% of your Grade 10 strength bonus - heal and buffs x3.24 stronger, buffs last x2.64 longer)"),
                      (1, 0, "plain (75% of your Grade 1 bonus rounds down to Grade 0)"), (0, 0, "plain")):
        check(str(Cook.campText(g, c)) == pre + mid + post, "E: Cook.campText(%d, %d) = %r" % (g, c, str(Cook.campText(g, c))))
    names3 = str(Cfg.campNames())

    def lines(lv, mc):
        level[0], mchef[0] = lv, mc
        return [str(x) for x in Cook.cookingLines(U)]
    earn = ("[Cooking] Earn XP at a Cooking Bench (ingredients can come from your bags) - pies and Caesar salad pay the most. A placed Campfire "
            "gives plain food and no XP; its dishes are on the Cooking Bench too (full Grade and XP).")
    want15 = ["[Cooking] Cooking 15 - your food comes out Grade 2: heal and buffs x1.64 stronger, buffs last x1.32 longer.",
              "[Cooking] Next: Grade 3 (x1.96 stronger and x1.52 longer) at Cooking 20.",
              "[Cooking] Campfire accessory (quick cooking in /craft, an emergency cook): " + names3 + " come out Grade 1 (x1.32 stronger and x1.15 longer) and pay 25% of the Cooking XP.",
              "[Cooking] Skill tree - +1 Grade: T1 0% T2 0% T3 0% - +2 Grades 0% - extra dish 0% - ingredient back 0% - double ingredients 0% - Master Chef +1 Grade",
              earn]
    got15 = lines(15, 1)
    check(got15 == want15, "E: /cooking at Cooking 15 + Master Chef (Skyy's case):\n   got  %s\n   want %s" % (got15, want15))
    print("E. /cooking at Cooking 15 + Master Chef:\n     " + "\n     ".join(got15[:3]))
    want5 = ["[Cooking] Cooking 5 - your food comes out Grade 0: heal and buffs x1.00 stronger, buffs last x1.00 longer.",
             "[Cooking] Next: Grade 1 (x1.32 stronger and x1.15 longer) at Cooking 10.",
             "[Cooking] Campfire accessory (quick cooking in /craft, an emergency cook): " + names3 + " come out plain and pay 25% of the Cooking XP.",
             earn]
    check(lines(5, 0) == want5, "E: /cooking at Cooking 5: %s" % lines(5, 0))
    want100 = ["[Cooking] Cooking 100 - your food comes out Grade 10: heal and buffs x4.20 stronger, buffs last x4.00 longer.",
               "[Cooking] Grades 11 and 12 come only from the Cooking skill tree (SkyyTrees).",
               "[Cooking] Campfire accessory (quick cooking in /craft, an emergency cook): " + names3 + " come out Grade 7 (x3.24 stronger and x2.64 longer) and pay 25% of the Cooking XP.",
               earn]
    check(lines(100, 0) == want100, "E: /cooking at Cooking 100: %s" % lines(100, 0))
    g11 = lines(100, 1)
    check(g11[0] == "[Cooking] Cooking 100 - your food comes out Grade 11: heal and buffs x4.52 stronger, buffs last x4.59 longer.",
          "E: /cooking at Cooking 100 + Master Chef -> Grade 11: %s" % g11[0])
    Cfg.ENABLED = False
    check(lines(15, 1) == ["[Cooking] graded cooking is turned off on this server (enabled=false)."], "E: /cooking with graded cooking off: one line")
    Cfg.ENABLED = True
    lvf = bridge.remove("skill:fn:level")
    check([str(x) for x in Cook.cookingLines(U)] == ["[Cooking] SkyySkills is not installed - food comes out plain (Grade 0) and cooking gives no XP."],
          "E: /cooking without SkyySkills: one line")
    bridge.put("skill:fn:level", lvf)
    st = J("CookStatsFn")()
    level[0], mchef[0] = 15, 1
    sl = [str(x) for x in st.apply(OA([U, Integer(15), Bool.FALSE]))]
    want_st = ["Food you cook - Grade 2 - heal and buffs x1.64 stronger - buffs last x1.32 longer",
               "Next Grade - Grade 3 at Cooking 20 - x1.96 stronger and x1.52 longer",
               "Campfire accessory - Grade 1 food x1.32 stronger and x1.15 longer - 25% of the XP",
               "Skill tree - 0% chance of +1 Grade on pies - 0% of +2 - 0% extra dish - 0% ingredient back"]
    check(sl == want_st, "E: Skills Stats lines at Cooking 15 + Master Chef:\n   got  %s\n   want %s" % (sl, want_st))
    nx = [str(x) for x in st.apply(OA([U, Integer(19), Bool.TRUE]))]
    check(nx == ["Grade 3 food - heal and buffs x1.96 stronger and lasting x1.52 longer"], "E: Skills Stats 'Level 20 adds' line: %s" % nx)
    print("E. Skills Stats lines:\n     " + "\n     ".join(sl[:3]))
    told = "Your food now comes out Grade %d - heal and buffs x%s stronger, buffs last x%s longer. /cooking for details." % (2, x2(sf[2]), x2(df[2]))
    check(told == "Your food now comes out Grade 2 - heal and buffs x1.64 stronger, buffs last x1.32 longer. /cooking for details.",
          "E: CookXpTask's new-Grade line (byte-identical class, new tables) reads: " + told)
    level[0], mchef[0] = 50, 0
    print("E. texts: sd / sdShort / campText / cookingLines / Stats lines checked; new-Grade line: " + told)

    # ---------------- F. the one-time update on scratch copies
    XD = os.path.join(SCRATCH, "work", "f-mig")

    def case(name, data):
        """<XD>/<name>/mods/Skyy_SkyyCooking/cooking.properties with these bytes (None = no file); CookCfg.FILE points there"""
        d_ = os.path.join(XD, name, "mods", "Skyy_SkyyCooking")
        os.makedirs(d_)
        f_ = os.path.join(d_, "cooking.properties")
        if data is not None:
            open(f_, "wb").write(data)
        Cfg.FILE = Paths.get(f_)
        return d_, f_

    def rb(p):
        return open(p, "rb").read()

    def baks(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []

    def lines_of(p):
        return [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()] if os.path.isfile(p) else []

    def idx(d_):
        return lines_of(os.path.join(d_, "config-history", "index.log"))

    def clog(d_):
        return lines_of(os.path.join(d_, "config-changes.log"))

    live_path = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking", "cooking.properties")
    live = rb(live_path) if os.path.isfile(live_path) else None
    check(live is not None, "F: a scratch copy of the live cooking.properties exists (%s)" % LIVE)
    if live is not None:
        lt = live.decode("latin-1")
        check("\nxpMultiplier=1.0\n" in lt and XP_MARK not in lt and CAMP_MARK in lt,
              "F: the live file still holds xpMultiplier=1.0 (no 0.1.4 marker; the 0.1.3 campfire update already ran)")
        # (a) the live file
        d, f = case("a-live", live)
        exp = expected_update(lt)
        check(str(Mig.migrate()) == "" and rb(f) == live, "F(a): the 0.1.3 campfire update does nothing on the live file (marker already there)")
        res = str(XMig.migrate())
        got = rb(f)
        check(got == exp.encode("latin-1"), "F(a): live file -> exactly one value line 1.0 -> 0.5 + the marker above its help line, every other byte kept")
        check(res.split("\n") == [INFO_LIVE], "F(a): one INFO line: %r" % res)
        print("F. INFO line the live file produces: [SkyyCooking] " + res)
        b = baks(d)
        check(len(b) == 1 and b[0].startswith("Skyy_SkyyCooking~cooking.properties.") and rb(os.path.join(d, "config-history", b[0])) == live,
              "F(a): History keeps the old file (one .bak = the old bytes): %s" % b)
        ix = idx(d)
        check(len(ix) == 1 and ix[0].split("\t")[1] == "Skyy_SkyyCooking/cooking.properties"
              and ix[0].split("\t")[3:] == ["SkyyCooking 0.1.4", "before the 0.1.4 Cooking XP update"], "F(a): index.log names the update: %s" % ix)
        cl = clog(d)
        check(len(cl) == 1 and cl[0].split("\t")[1:] == ["SkyyCooking 0.1.4", "-", "update", "xpMultiplier", "1.0", "0.5", "ok"]
              and re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", cl[0].split("\t")[0]) is not None,
              "F(a): one config-changes.log line in the kit's format (an Undo-able ok line): %s" % cl)
        print("F. change-log line: " + (cl[0] if cl else "(none)"))
        check(not os.path.exists(f + ".tmp"), "F(a): no temp file left")
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 0.5) < 1e-12 and abs(float(Cfg.CAMP_XP) - 0.25) < 1e-12, "F(a): the loader reads 0.5 (campfire share 0.25 unchanged)")
        pl_old, pl_new = Props(), Props()
        pl_old.load(BAIS(live))
        pl_new.load(BAIS(got))
        diffk = sorted(str(k) for k in set(list(pl_old.stringPropertyNames()) + list(pl_new.stringPropertyNames()))
                       if pl_old.getProperty(k) != pl_new.getProperty(k))
        check(diffk == ["xpMultiplier"] and str(pl_new.getProperty("xpMultiplier")) == "0.5", "F(a): java.util.Properties sees exactly one changed key: %s" % diffk)
        # (b) a second start
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and rb(f) == got and len(baks(d)) == 1 and len(idx(d)) == 1 and len(clog(d)) == 1,
              "F(b): a second start changes nothing (file, History, change log)")
        # (c) a hand-set value
        hand = lt.replace("\nxpMultiplier=1.0\n", "\nxpMultiplier=0.7\n")
        d, f = case("c-hand", hand.encode("latin-1"))
        res = str(XMig.migrate())
        check(rb(f) == expected_update(hand, None).encode("latin-1"), "F(c): hand-set 0.7 kept, only the marker added")
        check(res.split("\n") == ["cooking.properties: xpMultiplier was changed by hand - kept, nothing changed (0.1.4 Cooking XP marker added)",
                                  "xpMultiplier=0.7 kept (custom) - the 0.1.4 default is 0.5"], "F(c): INFO + kept note: %r" % res)
        check(len(baks(d)) == 1 and clog(d) == [], "F(c): History copy made, no change-log line (no value changed)")
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 0.7) < 1e-12, "F(c): the loader keeps 0.7")
        check(str(XMig.migrate()) == "" and len(baks(d)) == 1, "F(c): second start: nothing")
        # (c2) 0.5 set in Server Setup before 0.1.4 ships (the kit writes the canonical 0.5)
        s05 = lt.replace("\nxpMultiplier=1.0\n", "\nxpMultiplier=0.5\n")
        d, f = case("c2-skyy05", s05.encode("latin-1"))
        res = str(XMig.migrate())
        check(rb(f) == expected_update(s05, None).encode("latin-1") and res == "cooking.properties: xpMultiplier is already 0.5 - kept, nothing changed (0.1.4 Cooking XP marker added)"
              and clog(d) == [], "F(c2): a 0.5 Skyy set in Server Setup first is kept (marker only, no change-log line): %r" % res)
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 0.5) < 1e-12 and str(XMig.migrate()) == "", "F(c2): loader 0.5, second start nothing")
        # (c3) the kit's canonical write of the old default (Server Setup's Default button) = 1
        k1 = lt.replace("\nxpMultiplier=1.0\n", "\nxpMultiplier=1\n")
        d, f = case("c3-kit1", k1.encode("latin-1"))
        res = str(XMig.migrate())
        check(rb(f) == expected_update(k1, "0.5", "1").encode("latin-1") and res.startswith("cooking.properties updated to the 0.1.4 Cooking XP default: xpMultiplier 1 -> 0.5 ")
              and len(clog(d)) == 1 and clog(d)[0].split("\t")[4:] == ["xpMultiplier", "1", "0.5", "ok"], "F(c3): the kit's 1 -> 0.5 (old 1 in the Undo line): %r" % res)
        # (c4) other values and a continued entry are kept
        for v in ("1.00", "2", "0", " 1.0\\\n  ", "01"):
            hv = lt.replace("\nxpMultiplier=1.0\n", "\nxpMultiplier=%s\n" % v)
            r_ = XMig.update(hv)
            check(r_ is not None and str(r_[1]) == "" and r_[2] is not None and str(r_[0]) == expected_update(hv, None), "F(c4): value %r is kept (marker only, noted)" % v)
        # (d) CRLF
        crlf = lt.replace("\n", "\r\n")
        d, f = case("d-crlf", crlf.encode("latin-1"))
        res = str(XMig.migrate())
        check(rb(f) == expected_update(crlf).encode("latin-1") and res == INFO_LIVE, "F(d): CRLF file -> same update, every CRLF kept")
        check(b"\n" not in rb(f).replace(b"\r\n", b""), "F(d): no bare LF introduced")
        # (e) no file
        d, f = case("e-nofile", None)
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and not os.path.exists(f) and not os.path.exists(os.path.join(d, "config-history")),
              "F(e): no file -> nothing written")
        Cfg.load()
        fresh = rb(f).decode("latin-1")
        check(XP_MARK in fresh and CAMP_MARK in fresh and "\nxpMultiplier=0.5\n" in fresh and abs(float(Cfg.XP_MULT) - 0.5) < 1e-12,
              "F(e): the loader's fresh 0.1.4 file carries both markers, xpMultiplier 0.5")
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and rb(f).decode("latin-1") == fresh and not os.path.exists(os.path.join(d, "config-history")),
              "F(e): the fresh file never updates")
        # (f) no xpMultiplier line
        nox = lt.replace(XP_HELP + "\nxpMultiplier=1.0\n", "")
        d, f = case("f-noline", nox.encode("latin-1"))
        res = str(XMig.migrate())
        nl_ = nox.split("\n")
        first = [i for i, l in enumerate(nl_) if l.strip() and not l.lstrip().startswith("#")][0]
        at = first - 1 if first > 0 and nl_[first - 1].strip() and nl_[first - 1].lstrip().startswith("#") else first
        want_f = "\n".join(nl_[:at] + [XP_MARK] + nl_[at:])
        check(rb(f).decode("latin-1") == want_f and res == "cooking.properties: no xpMultiplier line (the default 0.5 applies) - nothing changed (0.1.4 Cooking XP marker added)"
              and clog(d) == [], "F(f): no xpMultiplier line -> the marker above the first entry (%s), nothing else: %r" % (nl_[at][:40], res))
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 0.5) < 1e-12 and str(XMig.migrate()) == "", "F(f): the fallback 0.5 applies; second start nothing")
        # (g) a 0.1.2-era file: both updates in setup()'s order
        v012 = lt.replace(CAMP_MARK + "\n", "").replace("\ncampfire.xpFactor=0.25\n", "\ncampfire.xpFactor=0.5\n")
        d, f = case("g-v012", v012.encode("latin-1"))
        r1 = str(Mig.migrate())
        mid = rb(f)
        r2 = str(XMig.migrate())
        check(r1 == INFO_CAMP and r2 == INFO_LIVE and rb(f) == exp.encode("latin-1"), "F(g): a 0.1.2 file gets the 0.1.3 campfire update then the 0.1.4 XP update -> the same text as (a)")
        b = baks(d)
        check(len(b) == 2 and rb(os.path.join(d, "config-history", b[0])) == v012.encode("latin-1") and rb(os.path.join(d, "config-history", b[1])) == mid,
              "F(g): two History copies (the 0.1.2 file, then the file between the two updates): %s" % b)
        check([l.split("\t")[4] for l in idx(d)] == ["before the 0.1.3 campfire XP update", "before the 0.1.4 Cooking XP update"], "F(g): index.log: %s" % idx(d))
        check([l.split("\t")[4:] for l in clog(d)] == [["campfire.xpFactor", "0.5", "0.25", "ok"], ["xpMultiplier", "1.0", "0.5", "ok"]],
              "F(g): two Undo-able change-log lines: %s" % clog(d))
        # (h) History blocked, then free; a folder in place of the file
        d, f = case("h-blocked", live)
        open(os.path.join(d, "config-history"), "w").write("not a folder")
        check(str(XMig.migrate()) == "" and rb(f) == live and clog(d) == [], "F(h): History cannot be kept -> WARN, file untouched, no log line")
        os.remove(os.path.join(d, "config-history"))
        check(str(XMig.migrate()) == INFO_LIVE and rb(f) == exp.encode("latin-1") and len(baks(d)) == 1 and len(clog(d)) == 1,
              "F(h): the next start updates once History can keep the old file")
        d, f = case("h-folder", None)
        os.makedirs(f)
        check(str(XMig.migrate()) == "" and os.path.isdir(f) and not os.path.exists(os.path.join(d, "config-history")),
              "F(h): a folder in place of the file -> nothing written")
        # (i) the whole start with the config kit
        d, f = case("i-kit", live)
        mods = os.path.dirname(d)
        Mig.migrate()
        XMig.migrate()
        Cfg.load()
        CfgPub.start(Paths.get(mods), None)
        fn = bridge.get("config:fn:SkyyCooking")
        check(fn is not None and str(fn.apply(OA(["get", "xpMultiplier"]))) == "0.5" and abs(float(Cfg.XP_MULT) - 0.5) < 1e-12,
              "F(i): config:fn:SkyyCooking get xpMultiplier = 0.5 after the start")
        st_ = fn.apply(OA(["status"]))
        check(st_ is not None and str(st_[0]) == "ok", "F(i): kit status ok (no hand edit seen: the update ran before the kit's first read): %s"
              % (None if st_ is None else [str(x) for x in st_]))
        lg = [str(x) for x in fn.apply(OA(["log", Integer(20)]))]
        check(len(lg) == 1 and lg[0].split("\t")[1:] == ["SkyyCooking 0.1.4", "-", "update", "xpMultiplier", "1.0", "0.5", "ok"],
              "F(i): the kit's log op (Server Setup -> Changes) lists the update line with status ok (Undo offered): %s" % lg)
        vs = [str(x) for x in fn.apply(OA(["versions"]))]
        check(len(vs) == 1 and vs[0].split("\t")[3:] == ["SkyyCooking 0.1.4", "before the 0.1.4 Cooking XP update"],
              "F(i): the kit's versions op (Server Setup -> History) lists the copy: %s" % vs)
        pv = fn.apply(OA(["restore", vs[0].split("\t")[0], None, "console", "preview"])) if vs else None
        pvt = "" if pv is None else " | ".join(str(x) for x in pv)
        check(pv is not None and str(pv[0]) == "ok" and re.search(r"Cooking XP multiplier: 0\.5 x -> 1(\.0)? x", pvt) is not None,
              "F(i): restore preview of that copy = the value going back: %s" % pvt.split("\n")[:2])
        r1 = fn.apply(OA(["set", "xpMultiplier", "1.0", None, "console", "yes", "console"]))
        CfgPub.flush()
        t2 = rb(f).decode("latin-1")
        check(r1 is not None and str(r1[0]) == "ok" and "\nxpMultiplier=1\n" in t2 and XP_MARK in t2 and abs(float(Cfg.XP_MULT) - 1.0) < 1e-12,
              "F(i): set back to 1.0 (the Undo path): ok, the kit writes 1, marker kept, the running multiplier is 1 (%s)" % (None if r1 is None else str(r1[2])))
        check(t2 == exp.replace("\nxpMultiplier=0.5\n", "\nxpMultiplier=1\n"), "F(i): only the value line changed back")
        lg2 = [str(x) for x in fn.apply(OA(["log", Integer(20)]))]
        check(len(lg2) == 2 and lg2[0].split("\t")[4:] == ["xpMultiplier", "0.5", "1", "ok"], "F(i): the set back is logged: %s" % lg2[:1])
        try:
            CfgPub.shutdown()
        except Exception:
            pass
        check(str(Mig.migrate()) == "" and str(XMig.migrate()) == "" and rb(f).decode("latin-1") == t2, "F(i): next start: no second update (1 set back is kept)")
        Cfg.load()
        check(abs(float(Cfg.XP_MULT) - 1.0) < 1e-12, "F(i): next start reads 1")
    print("F. one-time update on scratch copies checked")

    # ---------------- G. random files vs java.util.Properties
    rnd = random.Random(20261002)
    KEYS = ["xpMultiplier"] * 6 + ["maxXpPerMinute"] * 2 + ["enabled", "xpMultiplierX", "XpMultiplier", "xpMulti\\plier", " xpMultiplier",
                                                            "campfire.xpFactor"]
    SEPS = ["=", ":", " ", " = ", "\t=", "  :  ", "=  "]
    VALS = ["1.0"] * 4 + ["1"] * 3 + ["1.00", " 1.0", "1.0 ", "0.5", "0.7", "", "1\\.0", "abc", "1.0\\\\", "2", "01"]
    COMS = ["# x", "!bang", "   # indented", "#xpMultiplier=1.0", XP_HELP, "", "   ", "#", "\t! t", CAMP_MARK]
    stats = {"mig": 0, "kept": 0, "none": 0}
    for it_ in range(3000):
        lines_ = []
        for _n in range(rnd.randint(0, 9)):
            r0 = rnd.random()
            if r0 < 0.35:
                lines_.append(rnd.choice(COMS))
            else:
                k_ = rnd.choice(KEYS)
                v_ = rnd.choice(VALS)
                ln = rnd.choice(["", "  ", "\t"]) + k_ + rnd.choice(SEPS) + v_
                if rnd.random() < 0.12:
                    ln = ln + "\\"                                    # a continued entry
                    lines_.append(ln)
                    ln = rnd.choice(["  5", "  ", "1.0", "  # not a comment"])
                lines_.append(ln)
        if rnd.random() < 0.02:
            lines_.insert(rnd.randint(0, len(lines_)), "# SkyyCooking 0.1.4 Cooking XP marker")
        eol = rnd.choice(["\n", "\r\n", "mix"])
        text = ""
        for i_, ln in enumerate(lines_):
            e_ = ("\n" if rnd.random() < 0.5 else "\r\n") if eol == "mix" else eol
            text += ln + (e_ if (i_ < len(lines_) - 1 or rnd.random() < 0.7) else "")
        r_ = XMig.update(text)
        po = Props()
        po.load(BAIS(text.encode("latin-1")))
        if r_ is None:
            stats["none"] += 1
            check("# SkyyCooking 0.1.4 Cooking XP" in text, "G%d: only a marked file is left alone" % it_)
            continue
        new = str(r_[0])
        pn = Props()
        pn.load(BAIS(new.encode("latin-1")))
        ko = sorted(str(k) for k in po.stringPropertyNames())
        kn = sorted(str(k) for k in pn.stringPropertyNames())
        others_same = ko == kn and all(str(po.getProperty(k)) == str(pn.getProperty(k)) for k in ko if k != "xpMultiplier")
        ov, nv = po.getProperty("xpMultiplier"), pn.getProperty("xpMultiplier")
        ov = None if ov is None else str(ov)
        nv = None if nv is None else str(nv)
        if str(r_[1]):
            stats["mig"] += 1
            ok = others_same and ov is not None and ov.strip() in ("1.0", "1") and nv == "0.5"
        else:
            stats["kept" if r_[2] is not None else "none"] += 1
            ok = others_same and ov == nv and (ov is None or r_[2] is not None or ov.strip() == "0.5")
        check(ok, "G%d: Properties: only xpMultiplier may change, 1.0 / 1 -> 0.5 (%r -> %r, chg %r)\n%r" % (it_, ov, nv, str(r_[1]), text))
        # byte for byte: drop the one marker line, then only xpMultiplier value lines may differ (CR kept)
        nl_ = new.split("\n")
        mi = [i for i, l in enumerate(nl_) if l.rstrip("\r") == XP_MARK]
        check(len(mi) == 1, "G%d: exactly one marker line" % it_)
        if len(mi) == 1:
            rest = nl_[:mi[0]] + nl_[mi[0] + 1:]
            ol_ = text.split("\n")
            same_n = len(rest) == len(ol_)
            dif = [(a, b_) for a, b_ in zip(ol_, rest) if a != b_] if same_n else [("len", "len")]
            ok2 = same_n and all(a.endswith("\r") == b_.endswith("\r") and b_.rstrip("\r").endswith("0.5")
                                 and re.match(r"^[ \t]*xpMulti\\?plier", a) is not None for a, b_ in dif)
            check(ok2, "G%d: only xpMultiplier value lines differ, CR kept: %r" % (it_, dif[:3]))
        check(XMig.update(new) is None, "G%d: runs once (the new text is never updated again)" % it_)
        if len(FAILS) > 20:
            break
    check(stats["mig"] > 300 and stats["kept"] > 100 and stats["none"] > 100, "G: the random set covers update / kept / untouched: %s" % stats)
    print("G. 3000 random files vs java.util.Properties: %s" % stats)

    # ---------------- H. start twice on a scratch COPY of the live data folder
    src_live = os.path.join(SCRATCH, "live", "Skyy_SkyyCooking")
    sd = os.path.join(SCRATCH, "twice", "mods")
    sh = os.path.join(sd, "Skyy_SkyyCooking")
    if os.path.isdir(src_live):
        shutil.copytree(src_live, sh)
        H_MG = []

        def start():        # setup()'s order: CookMig.migrate, CookXpMig.migrate, CookCfg.load, CfgPub.start
            Cfg.FILE = Paths.get(os.path.join(sh, "cooking.properties"))
            H_MG.append((str(Mig.migrate()), str(XMig.migrate())))
            Cfg.load()
            CfgPub.start(Paths.get(sd), None)
            CfgPub.flush()
            time.sleep(0.6)
            CfgPub.shutdown()

        def snap():
            out = {}
            for dp, _dn, fns in os.walk(sd):
                for f_ in fns:
                    p_ = os.path.join(dp, f_)
                    out[os.path.relpath(p_, sd)] = (open(p_, "rb").read(), os.path.getmtime(p_))
            return out
        s0 = snap()
        start()
        s1 = snap()
        cp = os.path.join("Skyy_SkyyCooking", "cooking.properties")
        hl = os.path.join("Skyy_SkyyCooking", "config-changes.log")
        ix_ = os.path.join("Skyy_SkyyCooking", "config-history", "index.log")
        check(H_MG[0] == ("", INFO_LIVE), "H: first start: the campfire update has nothing to do, the XP update runs once: %s" % (H_MG[0],))
        check(s1[cp][0] == expected_update(s0[cp][0].decode("latin-1")).encode("latin-1") and abs(float(Cfg.XP_MULT) - 0.5) < 1e-12,
              "H: first start: cooking.properties = the live file + marker + xpMultiplier=0.5; running multiplier 0.5")
        new_baks = sorted(set(k for k in s1 if k.endswith(".bak")) - set(k for k in s0 if k.endswith(".bak")))
        check(len(new_baks) == 1 and s1[new_baks[0]][0] == s0[cp][0] and all(s1[k] == s0[k] for k in s0 if k.endswith(".bak")),
              "H: first start: one new History copy = the live bytes, the old copies untouched: %s" % new_baks)
        oldlog = s0.get(hl, (b"", 0))[0].decode("utf-8")
        newlog = s1[hl][0].decode("utf-8")
        added = newlog[len(oldlog):].strip().split("\n") if newlog.startswith(oldlog) else ["(rewritten)"]
        check(len(added) == 1 and added[0].split("\t")[1:] == ["SkyyCooking 0.1.4", "-", "update", "xpMultiplier", "1.0", "0.5", "ok"],
              "H: first start: the change log keeps its old lines and gains one: %s" % added)
        check(s1[ix_][0].decode("utf-8").startswith(s0[ix_][0].decode("utf-8")) and s1[ix_][0].decode("utf-8").count("\n") == s0[ix_][0].decode("utf-8").count("\n") + 1,
              "H: first start: index.log gains one line")
        time.sleep(1.1)
        start()
        s2 = snap()
        check(H_MG[1] == ("", ""), "H: second start: neither update runs: %s" % (H_MG[1],))
        check(sorted(s1) == sorted(s2) and all(s1[k] == s2[k] for k in s1), "H: the second start changes nothing (files + modified times): %s"
              % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k)))
        print("H. start twice on a copy of the live data folder: first start updates once (+1 History copy, +1 change-log line), second: no churn")
    else:
        check(False, "H: no scratch copy of the live data folder (%s)" % LIVE)

    # ---------------- I. class compare 0.1.3 vs 0.1.4
    CP = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def members(jar, cname):
        cp = CP(False)
        cp.appendClassPath(jar)
        cp.appendClassPath(B.SERVER_JAR)
        cp.appendSystemPath()
        cc = cp.get(cname)
        cf = cc.getClassFile()
        out = {}
        for mi in cf.getMethods():
            key = str(mi.getName()) + str(mi.getDescriptor())
            code = mi.getCodeAttribute()
            lines = []
            if code is not None:
                it = code.iterator()
                while it.hasNext():
                    pos = it.next()
                    lines.append(re.sub(r"#\d+ = ", "", str(IP.instructionString(it, pos, cf.getConstPool()))))
            out["m " + key] = "\n".join(lines)
        for fi in cf.getFields():
            cv = int(fi.getConstantValue())
            val = str(cf.getConstPool().getLdcValue(cv)) if cv else ""
            out["f " + str(fi.getName())] = str(fi.getDescriptor()) + " " + str(fi.getAccessFlags()) + " " + val
            out["v " + str(fi.getName())] = val
        return out

    z3, z4 = zipfile.ZipFile(OLDJAR), zipfile.ZipFile(JAR)
    c3 = dict((n, z3.read(n)) for n in z3.namelist() if n.endswith(".class"))
    c4 = dict((n, z4.read(n)) for n in z4.namelist() if n.endswith(".class"))
    check(sorted(set(c4) - set(c3)) == ["com/skyy/cooking/CookXpMig.class"] and sorted(set(c3) - set(c4)) == [],
          "I: the class list gains only CookXpMig: %s / %s" % (sorted(set(c4) - set(c3)), sorted(set(c3) - set(c4))))
    same = sorted(n for n in c4 if c3.get(n) == c4[n])
    diff = sorted(n for n in c4 if n in c3 and c3[n] != c4[n])
    EXPECT = {"CookCfg": {"f DEF_XP_MULT", "f DEFAULTS", "f CAMP_BLOCK", "m <clinit>()V", "m load()Ljava/lang/String;"},
              "Cook": {"m sd(I)Ljava/lang/String;", "m sdShort(I)Ljava/lang/String;", "m campText(II)Ljava/lang/String;",
                       "m campHint(Ljava/util/UUID;II)V", "m cookingLines(Ljava/util/UUID;)Ljava/util/List;"},
              "CookStatsFn": {"m apply(Ljava/lang/Object;)Ljava/lang/Object;"},
              "CookingCmd": None,
              "CookMig": {"f WHO", "m logLine(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;", "m migrate()Ljava/lang/String;"},
              "SkyyCookingPlugin": {"m setup()V"}}
    report = []
    for n in diff:
        cname = n[:-6].replace("/", ".")
        short = cname.rsplit(".", 1)[1]
        m3, m4 = members(OLDJAR, cname), members(JAR, cname)
        changed = sorted(kk for kk in set(m3) | set(m4) if m3.get(kk) != m4.get(kk) and not kk.startswith("v "))
        report.append("%s: %s" % (short, ", ".join(c.split("(")[0] for c in changed) or "(constant pool only)"))
        if short.startswith("Cfg"):
            continue                        # the config kit classes: VERSION + the row table (xpMultiplier default / help)
        allowed = EXPECT.get(short, set())
        if short == "CookingCmd":
            ok = len(changed) == 1 and changed[0].startswith("m execute(")
        else:
            ok = allowed is not None and set(changed) <= allowed
        check(ok, "I: class %s differs only in the expected members: %s" % (short, changed))
    check(all(("com/skyy/cooking/%s.class" % c) in diff for c in EXPECT), "I: every patched class really changed")
    must_same = ["CookXpTask", "CookSys", "CookGradeFn", "CookOutFn", "CookCampFn", "CookCampInfoFn", "CookHooks", "CookGiveCmd", "CookReloadCmd",
                 "CookCampCmd", "CookAdminCmd"]
    check(all(("com/skyy/cooking/%s.class" % c) in same for c in must_same), "I: grading / XP / bridge / admin command classes are byte-identical: %s"
          % [c for c in must_same if ("com/skyy/cooking/%s.class" % c) not in same])
    # CookMig differs only by its WHO text (inlined): the 0.1.3 update logic is unchanged
    m3, m4 = members(OLDJAR, PKG + "CookMig"), members(JAR, PKG + "CookMig")
    bad = []
    for k in sorted(set(m3) | set(m4)):
        a_, b_ = m3.get(k), m4.get(k)
        if k.startswith("v ") or a_ == b_:
            continue
        if k == "f WHO":
            ok_ = a_ is not None and a_.endswith(" SkyyCooking 0.1.3") and b_ == a_[:-len("0.1.3")] + "0.1.4"
        else:
            la, lb = (a_ or "").split("\n"), (b_ or "").split("\n")
            ok_ = len(la) == len(lb) and all(x == y or x.replace('"SkyyCooking 0.1.3"', '"SkyyCooking 0.1.4"') == y for x, y in zip(la, lb))
        if not ok_:
            bad.append(k)
    check(not bad and sorted(m3) == sorted(m4), "I: CookMig (the 0.1.3 campfire update) differs only in its WHO text 'SkyyCooking 0.1.3' -> "
          "'SkyyCooking 0.1.4' (the field + the two inlined uses): %s" % bad)
    # Cook.campGrade (the campfire pick) is byte-identical: only the MUL table it reads changed
    m3, m4 = members(OLDJAR, PKG + "Cook"), members(JAR, PKG + "Cook")
    check(m3["m campGrade(ID)I"] == m4["m campGrade(ID)I"] and m3["m campfire(Ljava/util/UUID;Ljava/lang/String;ILjava/lang/String;Ljava/lang/Boolean;)[Ljava/lang/Object;"]
          == m4["m campfire(Ljava/util/UUID;Ljava/lang/String;ILjava/lang/String;Ljava/lang/Boolean;)[Ljava/lang/Object;"],
          "I: Cook.campGrade and Cook.campfire are unchanged (the pick reads CookCfg.MUL, now the strength table)")
    c3_, c4_ = members(OLDJAR, PKG + "CookCfg"), members(JAR, PKG + "CookCfg")
    check(c4_["f DEF_XP_MULT"].endswith(" 0.5") and "f DEF_XP_MULT" not in c3_, "I: new constant CookCfg.DEF_XP_MULT = 0.5")
    l3, l4 = c3_["m load()Ljava/lang/String;"], c4_["m load()Ljava/lang/String;"]
    l3 = l3.replace(c3_["v DEFAULTS"], "<DEFAULTS>").replace(c3_["v CAMP_BLOCK"], "<CAMP_BLOCK>").split("\n")
    l4 = l4.replace(c4_["v DEFAULTS"], "<DEFAULTS>").replace(c4_["v CAMP_BLOCK"], "<CAMP_BLOCK>").split("\n")
    ld = [(a, b_) for a, b_ in zip(l3, l4) if a != b_]
    BR = re.compile(r"^(if\w*|goto)\s+(\d+)$")
    consts = [(a.strip(), b_.strip()) for a, b_ in ld if not BR.match(a.strip())]
    shifts = [(BR.match(a.strip()), BR.match(b_.strip())) for a, b_ in ld if BR.match(a.strip())]
    # dconst_1 (1 byte) -> ldc2_w 0.5 (3 bytes): every branch target behind it moves by exactly 2, nothing else changes
    ok_shift = all(y is not None and x.group(1) == y.group(1) and int(y.group(2)) - int(x.group(2)) == 2 for x, y in shifts)
    check(len(l3) == len(l4) and consts == [("dconst_1", "ldc2_w double 0.5")] and ok_shift,
          "I: CookCfg.load differs only in the inlined constants (DEFAULTS, CAMP_BLOCK, the xpMultiplier fallback 1.0 -> 0.5; %d branch targets "
          "behind it +2): %s" % (len(shifts), consts))
    print("   CookCfg.load: only inlined constants differ (DEFAULTS, CAMP_BLOCK, %s; %d branch targets behind it moved +2 bytes)"
          % ("; ".join("%s -> %s" % c for c in consts), len(shifts)))
    d3 = set(c3_["v DEFAULTS"].split("\n"))
    d4 = set(c4_["v DEFAULTS"].split("\n"))
    print("   default text: + %s" % sorted(d4 - d3))
    print("                 - %s" % sorted(d3 - d4))
    check(sorted(d4 - d3) == sorted([XP_MARK, "xpMultiplier=0.5", "# SkyyCooking 0.1.4 - cooking.properties (written on first run; comments must stay on their own lines)",
                                     "# Grade = floor(Cooking level / 10) (max 10) + Cooking skill tree (SkyyTrees). Heal and buffs x(1 + 0.32 x Grade), buffs last",
                                     "# x2^(Grade/5) - both baked into the generated assets. maxGrade can only LOWER the cap: the jar has Grades 1-12; a higher value is read as 12.",
                                     "# campfire.buffFactor = share of the Cooking-skill part of the Grade STRENGTH bonus: the dish comes out at the highest Grade whose",
                                     "# strength is <= 1 + buffFactor x (the Cooking Bench strength - 1). 0.75: bench Grade 5 (x2.60) -> Grade 3 (x1.96), Grade 10 (x4.20) -> Grade 7 (x3.24). 0..1"])
          and len(d3 - d4) == 6 and "xpMultiplier=1.0" in d3 - d4, "I: the default text differs only in the version line, the S / D comments, the campfire comment, the marker and 0.5")
    print("I. classes byte-identical: %d (%s)" % (len(same), ", ".join(x.rsplit("/", 1)[1][:-6] for x in same)))
    print("   classes that differ: %d + new CookXpMig" % len(diff))
    for r in report:
        print("     " + r)
    a3 = dict((n, z3.read(n)) for n in z3.namelist() if not n.endswith(".class"))
    a4 = dict((n, z4.read(n)) for n in z4.namelist() if not n.endswith(".class"))
    check(sorted(a3) == sorted(a4), "I: same asset list (%d)" % len(a4))
    adiff = sorted(n for n in a4 if a3.get(n) != a4[n])
    eff = [n for n in adiff if n.startswith("Server/Entity/Effects/")]
    inter = [n for n in adiff if n.startswith("Server/Item/Interactions/")]
    rest = [n for n in adiff if n not in eff and n not in inter]
    check(len(eff) == 156 and rest == ["Server/Languages/en-US/server.lang", "manifest.json"],
          "I: assets that differ: all 156 effects, %d family checks, server.lang, manifest.json (dish items + recipes identical): rest %s" % (len(inter), rest))
    print("   assets that differ: %d effects (strength), %d family checks (re-ranked), server.lang (tooltips), manifest.json; identical: %d"
          % (len(eff), len(inter), len(a4) - len(adiff)))
    mf3, mf4 = json.loads(a3["manifest.json"]), json.loads(a4["manifest.json"])
    check(mf4["Version"] == VERSION and mf4["Name"] == "0.1.4 SkyyCooking" and "+32% stronger per Grade" in mf4["Description"] and "25% of the XP" in mf4["Description"]
          and dict(mf3, Version=0, Name=0, Description=0) == dict(mf4, Version=0, Name=0, Description=0),
          "I: manifest: Name / Version 0.1.4, description +32% per Grade")
    sm = members(JAR, PKG + "SkyyCookingPlugin")["m setup()V"]
    pos = [sm.find(x) for x in ("com.skyy.cooking.CookMig.migrate(", "com.skyy.cooking.CookXpMig.migrate(", "com.skyy.cooking.CookCfg.load(",
                                "com.skyy.cooking.CfgPub.start(")]
    check(all(p >= 0 for p in pos) and pos[0] < pos[1] < pos[2] < pos[3] and sm.count("CookXpMig.migrate(") == 1,
          "I: setup() calls CookMig.migrate -> CookXpMig.migrate -> CookCfg.load -> CfgPub.start (bytecode)")
    if os.path.isfile(DEPLOYED):
        print("   the 0.1.3 jar compared %s the deployed Mods/SkyyCooking.jar" % ("IS" if open(DEPLOYED, "rb").read() == open(OLDJAR, "rb").read() else "is NOT"))


# ============================================================================================================== parent
def main():
    if "--child" in sys.argv:
        try:
            run()
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("child crashed: %s" % e)
        print("%d ok, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS[:40]:
            print("  FAILED:", f[:400])
        sys.exit(1 if FAILS else 0)
    for p in (JAR, OLDJAR):
        if not os.path.isfile(p):
            raise SystemExit("missing " + p + " (build it first)")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    os.makedirs(os.path.join(SCRATCH, "live"))
    if os.path.isdir(LIVE):
        shutil.copytree(LIVE, os.path.join(SCRATCH, "live", "Skyy_SkyyCooking"))      # READ ONLY copy of the live data folder
        print("copied the live Skyy_SkyyCooking folder (read only): %s" % LIVE)
    else:
        print("note: live Skyy_SkyyCooking folder not found: %s" % LIVE)
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    env.pop("JAVA_TOOL_OPTIONS", None)
    args = [sys.executable, os.path.abspath(__file__), "--child", "--dir", SCRATCH, "--jar", JAR, "--old", OLDJAR, "--live", LIVE]
    rc = subprocess.call(args, env=env, cwd=ROOT)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyCooking %s bare-JVM check: %s%s" % (VERSION, "PASS" if rc == 0 else "FAIL", "" if KEEP else " (scratch folder removed)"))
    sys.exit(rc)


if __name__ == "__main__":
    main()
