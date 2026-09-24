"""Derive SkyySacks/build_skyysacks_0.6.5.py from 0.6.3 (0.6.4 changes + crafted items into storage first).
0.6.4 CRAFT LOSS FIX (Skyy: "used the furnace tab to craft all my copper into bars, it all vanished"): the craft page gave outputs only
when removeMaterials() reported succeeded(), but still deducted the consumed bag items. Now: count every input before and after the
removal and pay for exactly what was removed (done = min(removed_i / perCraft_i)); hand back any excess removed ItemId input;
outputs for `done` crafts always; every craft appended to Skyy_SkyySacks/crafts.log (uuid, recipe, requested, done, flag, per-input
before/after). Bags tab relabelled "< Back to bags".
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.3.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.6.5.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    s = s.replace(old, new, count)


rep('VERSION = "0.6.3"', 'VERSION = "0.6.5"')
s = s.replace('"""SkyySacks 0.6.3', '"""SkyySacks 0.6.5' + LF + '0.6.5: crafted items go to STORAGE first (storage-hotbar-backpack order); 0.6.4 put them in the hidden backpack section first. 0.6.4: craft page pays by counted removal (fixes vanished furnace crafts), crafts.log, "< Back to bags".' + LF, 1)
BS = chr(92)
Q = BS + BS + '"'   # how \" appears inside the Python source of the build script (f-string: \\")
rep('TextButton #SkyyCBags {{ Anchor: (Width: 92, Height: 32); Text: ' + Q + 'Bags' + Q,
    'TextButton #SkyyCBags {{ Anchor: (Width: 150, Height: 32); Text: ' + Q + '< Back to bags' + Q)
rep('    int cap = tabRow == 0 ? 7 : 8;', '    int cap = tabRow == 0 ? 6 : 8;')

old_start = s.index('    java.util.List inputs = {CRM}.getInputMaterials(r, qty);')
old_end = s.index('    rebuild();' + LF + '  }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft page event failed: " + t); }}', old_start)
new = LF.join([
    '    java.util.List inputs = {CRM}.getInputMaterials(r, qty);',
    '    int n = inputs == null ? 0 : inputs.size();',
    '    if (n == 0) {{ this.info = "this recipe has no inputs"; rebuild(); return; }}',
    '    if (!mats.canRemoveMaterials(inputs)) {{ this.info = "not enough materials"; rebuild(); return; }}',
    '    int[] before = new int[n]; int[] per = new int[n];',
    '    for (int i = 0; i < n; i++) {{',
    '      {MQ} mq = ({MQ}) inputs.get(i);',
    '      before[i] = mats.countRemovableMaterial(mq);',
    '      per[i] = mq.getQuantity() / qty; if (per[i] <= 0) per[i] = 1;',
    '    }}',
    '    Object tx = mats.removeMaterials(inputs);',
    '    boolean flag = tx != null && ((com.hypixel.hytale.server.core.inventory.transaction.Transaction) tx).succeeded();',
    '    int[] after = new int[n]; int done = qty;',
    '    for (int i = 0; i < n; i++) {{',
    '      after[i] = mats.countRemovableMaterial(({MQ}) inputs.get(i));',
    '      int removed = before[i] - after[i]; if (removed < 0) removed = 0;',
    '      int c2 = removed / per[i]; if (c2 < done) done = c2;',
    '    }}',
    '    if (done < 0) done = 0;',
    '    StringBuilder audit = new StringBuilder();',
    '    for (int i = 0; i < n; i++) {{',
    '      {MQ} mq = ({MQ}) inputs.get(i);',
    '      int removed = before[i] - after[i]; if (removed < 0) removed = 0;',
    '      int extra = removed - done * per[i];',
    '      String mid = mq.getItemId() != null ? mq.getItemId() : ("res:" + mq.getResourceTypeId());',
    '      audit.append(" ").append(mid).append("=").append(before[i]).append("->").append(after[i]);',
    '      if (extra > 0) {{',
    '        if (mq.getItemId() != null) {{ {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(mq.getItemId(), extra)); audit.append("(returned ").append(extra).append(")"); }}',
    '        else {{ audit.append("(LOST ").append(extra).append(" resource items)"); {PKG}.SackPool.warn("craft: " + extra + " x " + mid + " removed beyond " + done + " crafts for " + u + " - resource type, cannot return"); }}',
    '      }}',
    '    }}',
    '    {PKG}.BagMirror m = {PKG}.BagMirror.of(u);',
    '    int consumed = m.sync(u);',
    '    if (consumed > 0) {PKG}.SackPool.save(u);',
    '    {MQ}[] outs = r.getOutputs();',
    '    {MQ} outq = r.getPrimaryOutput();',
    '    if ((outs == null || outs.length == 0) && outq != null) outs = new {MQ}[] {{ outq }};',
    '    int given = 0;',
    '    if (done > 0 && outs != null) {{',
    '      for (int k = 0; k < outs.length; k++) {{',
    '        if (outs[k] == null || outs[k].getItemId() == null) continue;',
    '        long total = (long) outs[k].getQuantity() * (long) done; if (total > 100000L) total = 100000L;',
    '        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(outs[k].getItemId(), (int) total));',
    '        given += (int) total;',
    '      }}',
    '    }}',
    '    {PKG}.CraftLog.write(u, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());',
    '    if (done > 0 && given == 0) {PKG}.SackPool.warn("craft: " + done + " crafts of " + r.getId() + " paid but the recipe has no item output (" + u + ")");',
    '    String nm = pretty(outq == null ? "?" : outq.getItemId());',
    '    if (done == qty) this.info = "crafted " + qty + " x " + nm + (consumed > 0 ? " (" + consumed + " from bags)" : "");',
    '    else if (done > 0) this.info = "crafted " + done + " of " + qty + " x " + nm + " - extra materials were returned";',
    '    else this.info = "could not remove the materials - nothing was used";',
    '',
])
s = s[:old_start] + new + s[old_end:]

rep('cpg  = pool.makeClass(PKG + ".CraftPage", pool.get(PAGE))',
    'clog = pool.makeClass(PKG + ".CraftLog")' + LF + 'cpg  = pool.makeClass(PKG + ".CraftPage", pool.get(PAGE))')
anchor = '# CraftPage fields + constructor first (SacksPage references it)'
rep(anchor, LF.join([
    '# ================= CraftLog (append-only audit of every craft-page craft) =================',
    'clog.addField(CtField.make("public static java.nio.file.Path FILE;", clog))',
    'clog.addMethod(CtNewMethod.make("""',
    'public static synchronized void write(java.util.UUID u, String recipe, int requested, int done, boolean flag, int given, String audit) {',
    '  try {',
    '    if (FILE == null) return;',
    '    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);',
    '    String line = new java.util.Date().toString() + " " + u + " " + recipe + " requested=" + requested + " done=" + done + " flag=" + flag + " given=" + given + audit + System.lineSeparator();',
    '    java.nio.file.Files.write(FILE, line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });',
    '  } catch (Throwable t) { }',
    '}""", clog))',
    '',
    anchor]))
rep('  {PKG}.SackPool.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pools");',
    '  {PKG}.SackPool.DIR = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("pools");' + LF +
    '  {PKG}.CraftLog.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("crafts.log");')
m = re.search(r'for c in \(([^)]*)\):', s)
assert m and 'cpg' in m.group(1), "class write list not found"
s = s[:m.start(1)] + m.group(1).replace('cpg', 'clog, cpg', 1) + s[m.end(1):]

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
