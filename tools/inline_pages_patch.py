# one-off (2026-09-22): convert SkyySacks 0.1.1 and SkyyCollections 0.1.1 pages to inline documents with
# underscore-free element IDs (see memory: hytale-ui-rules). Edits the 0.1.1 build scripts in place.
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BTN = 'Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 10, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 10, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));'

# ---------------- Sacks ----------------
p = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.1.1.py"); s = open(p, encoding="utf8").read()
start = s.index('page.addMethod(CtNewMethod.make(f"""\npublic void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{')
end = s.index('}}""", page))', start) + len('}}""", page))')
new_build = r'''page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Map m = {PKG}.SackPool.pool(u);
  java.util.ArrayList entries = new java.util.ArrayList(m.entrySet());
  java.util.Collections.sort(entries, new {PKG}.CountCmp());
  int pages = (entries.size() + {ROWS} - 1) / {ROWS};
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * {ROWS};
  String caps = "";
  String[] cats = {PKG}.SackDefs.CATS;
  for (int c = 0; c < cats.length; c++) caps = caps + cats[c] + ": " + {PKG}.SackPool.catTotal(u, cats[c]) + "   ";
  String bs = "{BTN}";
  b.appendInline((String) null, "Group #SkyySacksRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyySacksRoot", "Group #SkyySacks {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 470); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySacks", "Group {{ Anchor: (Height: 2); Background: #e0b060; }}");
  b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 26); Text: \\"SkyySacks\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 16); Text: \\"" + caps + "\\"; Style: (FontSize: 11, TextColor: #c9b89a, HorizontalAlignment: Center); }}");
  if (entries.size() == 0) b.appendInline("#SkyySacks", "Label {{ Anchor: (Height: 30); Text: \\"Nothing pooled yet - carry a sack and pick things up!\\"; Style: (FontSize: 12, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  this.rowItems = new String[{ROWS}];
  for (int i = 0; i < {ROWS}; i++) {{
    int idx = start + i;
    if (idx >= entries.size()) {{ this.rowItems[i] = null; continue; }}
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    this.rowItems[i] = id;
    b.appendInline("#SkyySacks", "Group #SkyySRow" + i + " {{ Anchor: (Height: 26); LayoutMode: Left; Padding: (Vertical: 2); }}");
    b.appendInline("#SkyySRow" + i, "Label {{ Anchor: (Width: 330, Height: 22); Text: \\"" + id.replace("\\"", "") + "   x" + cnt + "\\"; Style: (FontSize: 11, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySRow" + i, "TextButton #SkyySGet" + i + "One {{ Anchor: (Width: 56, Height: 22); Text: \\"Get 1\\"; " + bs + " }}");
    b.appendInline("#SkyySRow" + i, "Label {{ Anchor: (Width: 6, Height: 22); Text: \\"\\"; }}");
    b.appendInline("#SkyySRow" + i, "TextButton #SkyySGet" + i + "Stack {{ Anchor: (Width: 62, Height: 22); Text: \\"Get 64\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyySGet" + i + "One", {EVD}.of("a", "row" + i + ":w1"));
    ev.addEventBinding({BT}.Activating, "#SkyySGet" + i + "Stack", {EVD}.of("a", "row" + i + ":w64"));
  }}
  b.appendInline("#SkyySacks", "Group #SkyySNav {{ Anchor: (Height: 28); LayoutMode: Left; Padding: (Top: 4); }}");
  b.appendInline("#SkyySNav", "TextButton #SkyySPrev {{ Anchor: (Width: 60, Height: 22); Text: \\"< Prev\\"; " + bs + " }}");
  b.appendInline("#SkyySNav", "Label {{ Anchor: (Width: 120, Height: 22); Text: \\"Page " + (this.pageNo + 1) + " / " + pages + "\\"; Style: (FontSize: 10, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySNav", "TextButton #SkyySNext {{ Anchor: (Width: 60, Height: 22); Text: \\"Next >\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySPrev", {EVD}.of("a", "prev"));
  ev.addEventBinding({BT}.Activating, "#SkyySNext", {EVD}.of("a", "next"));
}}""", page))'''.replace("{BTN}", BTN)
s = s[:start] + new_build + s[end:]
# drop the .ui asset and its generator usage
s = s.replace('files = {"Common/UI/Custom/Pages/SkyySacks.ui": SACKS_UI}', 'files = {}  # pages are built inline (no .ui files: see memory hytale-ui-rules)')
s = s.replace('page.build() is public (matches CustomUIPage)', 'page.build() is public (matches CustomUIPage)')
s = s.replace('/sacks page is a static .ui file with TextButtons + paging', '/sacks page is built inline (no .ui files, no underscores in IDs) with TextButtons + paging')
open(p, "w", encoding="utf8").write(s); print("patched sacks")

# ---------------- Collections ----------------
p = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.1.1.py"); s = open(p, encoding="utf8").read()
start = s.index('page.addMethod(CtNewMethod.make(f"""\npublic void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{')
end = s.index('}}""", page))', start) + len('}}""", page))')
new_build = r'''page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.CollStore.counts(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CollCmp());
  int n = entries.size() < {ROWS} ? entries.size() : {ROWS};
  String summary = entries.size() == 0 ? "Nothing collected yet - go break some blocks!" : (entries.size() + " collections tracked" + (entries.size() > {ROWS} ? " (top {ROWS} shown)" : ""));
  b.appendInline((String) null, "Group #SkyyCollRoot {{ Anchor: (Full: 0); }}");
  b.appendInline("#SkyyCollRoot", "Group #SkyyColl {{ Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 460); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyColl", "Group {{ Anchor: (Height: 2); Background: #b48fe0; }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 26); Text: \\"Collections\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #f0e6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 16); Text: \\"" + summary + "\\"; Style: (FontSize: 11, TextColor: #c0b3d6, HorizontalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    int tier = {PKG}.CollStore.tierOf(cnt);
    long next = tier < 5 ? {PKG}.CollStore.TIERS[tier] : 0L;
    String prog = tier >= 5 ? "MAX" : (cnt + " / " + next);
    String name = {PKG}.CollStore.pretty(id).replace("\\"", "");
    b.appendInline("#SkyyColl", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 24); LayoutMode: Left; }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 330, Height: 20); Text: \\"" + name + "  " + {PKG}.CollStore.roman(tier) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 170, Height: 20); Text: \\"" + prog + "\\"; Style: (FontSize: 11, TextColor: #9fd8a2, VerticalAlignment: Center); }}");
  }}
}}""", page))'''
s = s[:start] + new_build + s[end:]
s = s.replace('           OUT, {"Common/UI/Custom/Pages/SkyyCollections.ui": COLL_UI})', '           OUT, {})  # page built inline (no .ui files: see memory hytale-ui-rules)')
s = s.replace('page build() is public (matches CustomUIPage)', 'page build() is public and fully inline (no .ui files, no underscores in IDs)')
open(p, "w", encoding="utf8").write(s); print("patched collections")
