"""skyyelem - THE one element table of the Wynn element system (research/Wynn-Elements-Build-Spec.md section 2.1; built in the elem1 round
2026-10-22: SkyyMobs 0.1.17, SkyyGear 0.3.39, SkyyClasses 0.1.46, SkyyPets 0.4.10, SkyyAccessories 0.5.32, SkyyMenu 0.3.45).

Every build script that shows or names an element imports this file (plain Python, no kit, no JVM) so the names, the order on the bridge
and the colours are the same everywhere (Style Guide section 15: "elements: Fire orange, Water blue, Earth green, Thunder yellow, Air
white-teal, Poison lime"). Where new element things go: research/Wynn-Elements-Build-Spec.md (design), this file (shared constants).
"""

# the five elements in Wynn order - the ONLY spelling on the bridge and in text (Skyy 2026-10-17: "Lightning -> Thunder, Wind -> Air")
NAMES = ["Earth", "Thunder", "Water", "Fire", "Air"]
# old spellings still read (SkyyClasses' saved attunements "Lightning" / "Wind")
ALIASES = {"lightning": "Thunder", "wind": "Air"}
# SkyyGear stat keys per element (element damage % of the hit, element Defence flat)
DMG_KEYS = ["fEarth", "fThunder", "fWater", "fFire", "fAir"]
DEF_KEYS = ["dEarth", "dThunder", "dWater", "dFire", "dAir"]
# the engine's DamageCause asset ids (Assets.zip Server/Entity/Damage/, VERIFIED 2026-10-22) - DoT ticks only
CAUSE = {"Earth": "Earth", "Thunder": "Lightning", "Water": "Water", "Fire": "Fire", "Air": "Wind", "Poison": "Poison"}
# the wheel: Earth > Thunder > Water > Fire > Air > Earth ("beats" = the target is Weak to it)
WHEEL_DEF = "Earth>Thunder>Water>Fire>Air"
# colours (popups, rows, charts, plates, tooltips): Style Guide 15
COLORS = {"Earth": "#5dbb4a", "Thunder": "#ffd84d", "Water": "#4fa8ff", "Fire": "#ff6a3d", "Air": "#c8f5ee", "Poison": "#b8f04a"}
WEAK_COLOR, RESIST_COLOR, NEUTRAL_COLOR = "#39f493", "#ff6b6b", "#7f93a6"
# the planned reactions (D7: "Later, as tree nodes") - the chart lists them, nothing applies them yet
REACTIONS = [("Wildfire", "Air hit on a Burning enemy", "Burn spreads to enemies nearby"),
             ("Shatter", "Thunder hit on a Frozen enemy", "+50 % of the hit as Water"),
             ("Steam", "Fire hit on a Chilled enemy", "a blinding cloud"),
             ("Quake", "Earth hit on a Shocked enemy", "a stagger wave")]


def norm(s):
    """an element word -> its Wynn name, "" for none, None for an unknown word"""
    if s is None:
        return None
    t = s.strip()
    if t.lower() in ("", "none", "-"):
        return ""
    for n in NAMES:
        if n.lower() == t.lower():
            return n
    return ALIASES.get(t.lower())


def wheel(text):
    """the wheel text -> the 5 names in order, or None when it is not the 5 names once each"""
    p = [norm(x) for x in (text or "").split(">")]
    if len(p) != 5 or any(not x for x in p) or len(set(p)) != 5:
        return None
    return p


def beats(e, wh=None):
    """the element that beats e (e's target is Weak to it): the one before e on the wheel"""
    w = wh or wheel(WHEEL_DEF)
    return w[(w.index(e) + 4) % 5]


def check():
    assert len(NAMES) == 5 and len(set(NAMES)) == 5 and wheel(WHEEL_DEF) == NAMES
    assert [beats(e) for e in NAMES] == ["Air", "Earth", "Thunder", "Water", "Fire"], "Fire mob weak to Water, Water weak to Thunder ..."
    assert norm("Lightning") == "Thunder" and norm("wind") == "Air" and norm("none") == "" and norm("Ice") is None
    assert all(len(v) == 7 and v.startswith("#") for v in COLORS.values()) and set(COLORS) == set(NAMES) | {"Poison"}
    assert all(ord(c) < 128 for r in REACTIONS for x in r for c in x)


check()
