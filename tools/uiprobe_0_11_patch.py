"""Derive SkyyUiProbe/build_skyyuiprobe_0.11.py + test_skyyuiprobe_0.11.py from the 0.10 SET pin (0.10 untouched; bytes / CRLF kept).
Run:  python tools/uiprobe_0_11_patch.py   then   python SkyyUiProbe/build_skyyuiprobe_0.11.py   (never --deploy)
Check: python SkyyUiProbe/test_skyyuiprobe_0.11.py

0.11 = ONE fix (Skyy 2026-11-14 test of /uiprobe inv: "it crashed when i tried" - client disconnect "CustomUI Set command couldn't set
value. Selector: #SkyyPrIh.Slots -> Property QualityOverride does not exist on HytaleClient.Data.Items.ClientItemStack").
Cause: the grid copy was stack.withMetadata(null), which KEEPS ItemStack.qualityIndexOverride; SkyyAccessories re-stamps charms with
withQuality(...), and a stack with a quality override serializes a QualityOverride field the 0.7.6 client's CustomUI ItemStack does not
have. Fix: the grid copy is new ItemStack(id, quantity, durability, maxDurability, (BsonDocument) null) - the 5-arg constructor runs the
3-arg one and sets only the two durabilities (bytecode-checked 2026-11-14), so no metadata AND no quality override reach the client.
RULE for the real screen (HANDOFF section 2 candidate): a grid slot copy carries id + count + durability only; rarity is shown by our frame.
Everything else is byte-for-byte 0.10.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(os.path.dirname(HERE), "SkyyUiProbe")
NL = "\r\n"  # both 0.10 scripts are CRLF

OLD_COPY = "g.setItemStack(s.withMetadata((@BSON@) null));"
NEW_COPY = ("g.setItemStack(new @IS@(s.getItemId(), s.getQuantity(), s.getDurability(), s.getMaxDurability(), (@BSON@) null));"
            "  /* 0.11: no metadata AND no quality override (client has no QualityOverride) */")

COMMON = [
    ("build_skyyuiprobe_0.10.py", "build_skyyuiprobe_0.11.py"),
    ("test_skyyuiprobe_0.10.py", "test_skyyuiprobe_0.11.py"),
    ('VERSION = "0.10"', 'VERSION = "0.11"'),
]
BUILD = COMMON + [("SkyyUiProbe-0.10.jar", "SkyyUiProbe-0.11.jar"), (OLD_COPY, NEW_COPY)]

KEEP_META = ('    K.check(inv(PI, "storage").getItemStack(JShort(5)).getMetadata() is not None, '
             '"I4: the REAL sword keeps its metadata (only the copy is stripped)")' + NL)
QUALITY_CHECK = NL.join([
    '    # 0.11 (Skyy crash 11-14 "Property QualityOverride does not exist on ClientItemStack"): a quality-stamped stack (SkyyAccessories withQuality)',
    '    _qf = JClass(PH + "server.core.inventory.ItemStack").class_.getDeclaredField("qualityIndexOverride"); _qf.setAccessible(True)',
    '    _qs = inv(PI, "storage").getItemStack(JShort(5)).withQuality(3)',
    '    _qd = E.jf(IGSc.class_, "itemStack").get(INVPG.slot(_qs))',
    '    _q0 = _qf.get(E.jf(IGSc.class_, "itemStack").get(INVPG.slot(inv(PI, "storage").getItemStack(JShort(0)))))',
    '    K.check(int(_qf.get(_qs)) != int(_q0) and int(_qf.get(_qd)) == int(_q0) and _qd.getMetadata() is None '
    'and int(_qd.getQuantity()) == int(_qs.getQuantity()),',
    '            "I4 0.11: a quality-stamped stack\'s grid copy has NO quality override (= a plain item), no metadata, same count")',
]) + NL

TEST = COMMON + [
    (r'K.eq(len(re.findall(r"\.withMetadata\(", _src)), 2, "J: TWO withMetadata in the build: the fresh probe stack + the grid copy")',
     r'K.eq(len(re.findall(r"\.withMetadata\(", _src)), 1, "J: ONE withMetadata in the build: the fresh probe stack (0.11: the grid copy is a new stack)")'),
    ('K.check("g.setItemStack(s.withMetadata((@BSON@) null));" in _src, "J: ... the grid copy STRIPS the metadata (I4)")',
     'K.check("g.setItemStack(new @IS@(s.getItemId(), s.getQuantity(), s.getDurability(), s.getMaxDurability(), (@BSON@) null));" in _src, '
     '"J: 0.11 the grid copy = a NEW ItemStack(id, qty, dur, max, null): no metadata, no quality override")'),
    (KEEP_META, KEEP_META + QUALITY_CHECK),
    ("SkyyUiProbe 0.10 - UI queue probe", "SkyyUiProbe 0.11 - UI queue probe"),
    ("(ONLY their title line 0.9 -> 0.10)", "(ONLY their title line 0.9 -> 0.11)"),
]


def patch(src, dst, reps):
    b = open(os.path.join(MOD, src), "rb").read()
    for old, new in reps:
        o, n = old.encode(), new.encode()
        if o not in b:
            sys.exit("STOP: %r not found in %s" % (old[:80], src))
        b = b.replace(o, n)
    open(os.path.join(MOD, dst), "wb").write(b)
    print("wrote", dst)


patch("build_skyyuiprobe_0.10.py", "build_skyyuiprobe_0.11.py", BUILD)
patch("test_skyyuiprobe_0.10.py", "test_skyyuiprobe_0.11.py", TEST)
