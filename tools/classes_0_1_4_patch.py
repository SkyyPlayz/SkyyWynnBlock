"""Derive SkyyClasses/build_skyyclasses_0.1.4.py from 0.1.3.
0.1.4 (Skyy 2026-09-23: "classes locking you to that weapon type worked! id add a popup warning when you try to use a weapon you cant use."):
 - When DamageLock blocks a hit (wrong class weapon, no class yet, a class that is not out yet, a blocked Kunai in the utility slot, an
   arrow from a blocked bow), the player also gets a POPUP: the vanilla notification toast (NotificationUtil.sendNotification with
   NotificationStyle.Warning - the call vanilla CraftingManager makes for crafting errors) showing the blocked weapon's icon
   (ItemStack.toPacket() -> ItemWithAllMetadata), the title "You can't use this weapon" (or "Choose a class first") and the same text as
   the chat line. At most one popup per 1.5 s per player (POPPED); the chat line keeps its own 3 s throttle.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.3.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
TQ = chr(34) * 3


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')
rep("0.1.3: per-profile storage (tools/PROFILES-CONTRACT.md).",
    "0.1.4: a POPUP (vanilla notification toast with the weapon's icon) whenever a hit is blocked, next to the chat line - notes in" + LF +
    "  tools/classes_0_1_4_patch.py." + LF +
    "0.1.3: per-profile storage (tools/PROFILES-CONTRACT.md).")
rep('    "ES":   "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",' + LF + "}",
    '    "ES":   "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",' + LF +
    '    "NTU":  "com.hypixel.hytale.server.core.util.NotificationUtil",' + LF +
    '    "NST":  "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",' + LF +
    '    "IWM":  "com.hypixel.hytale.protocol.ItemWithAllMetadata",' + LF + "}")
rep('             (T["QRY"], "and"), (T["QRY"], "or"), (T["PR"], "isValid"),',
    '             (T["QRY"], "and"), (T["QRY"], "or"), (T["PR"], "isValid"),' + LF +
    '             (T["NTU"], "sendNotification"), (T["NST"], "Warning"), (T["IS"], "toPacket"), (T["PR"], "getPacketHandler"),')

# the popup lives next to tell() in ClassRules (added after tell, before its only caller in DamageLock)
rep('F(rul, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")',
    'F(rul, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")' + LF +
    'F(rul, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")')
POPUP = LF.join([
    "M(rul, r" + TQ,
    "public static void popup(@PR@ pr, java.util.UUID u, String id, String text) {",
    "  try {",
    "    long now = System.currentTimeMillis();",
    "    Long last = (Long) POPPED.get(u);",
    "    if (last != null && now - last.longValue() < 1500L) return;",
    "    POPPED.put(u, Long.valueOf(now));",
    "    String head = @PKG@.ClassStore.classIndex(u) < 0 ? \"Choose a class first\" : \"You can't use this weapon\";",
    "    @MSG@ title = @MSG@.raw(head).color(\"#ff9d6b\");",
    "    @MSG@ body = @MSG@.raw(text);",
    "    @IWM@ icon = null;",
    "    try { if (id != null && id.length() > 0) icon = (@IWM@) new @IS@(id, 1).toPacket(); } catch (Throwable t0) { icon = null; }",
    "    if (icon != null) @NTU@.sendNotification(pr.getPacketHandler(), title, body, icon, @NST@.Warning);",
    "    else @NTU@.sendNotification(pr.getPacketHandler(), title, body, @NST@.Warning);",
    "  } catch (Throwable t) { @PKG@.ClassCfg.warnLimited(\"popup failed: \" + t); }",
    "}" + TQ + ")",
    "",
    "# ================= bridge functions =================",
])
rep("# ================= bridge functions =================", POPUP)
rep("    if (pr != null && pr.isValid()) @PKG@.ClassRules.tell(pr, u, @PKG@.ClassRules.blockText(u, bad, util));",
    "    if (pr != null && pr.isValid()) {" + LF +
    "      String bt = @PKG@.ClassRules.blockText(u, bad, util);" + LF +
    "      @PKG@.ClassRules.tell(pr, u, bt);" + LF +
    "      @PKG@.ClassRules.popup(pr, u, bad, bt);" + LF +
    "    }")
rep("    @PKG@.ClassRules.WARNED.remove(u);",
    "    @PKG@.ClassRules.WARNED.remove(u);" + LF + "    @PKG@.ClassRules.POPPED.remove(u);")

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
