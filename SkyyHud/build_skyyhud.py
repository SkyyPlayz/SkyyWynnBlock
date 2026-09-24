import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyyhud_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

# ---- verify the APIs we generate against (fail loudly if this server build differs) ----
JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
HUD = "com.hypixel.hytale.server.core.entity.entities.player.hud.CustomUIHud"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
ER  = "com.hypixel.hytale.event.EventRegistry"
def must(cn, member=None, sig=None):
    c = pool.get(cn)
    if member:
        found = False
        for m in list(c.getMethods()) + list(c.getConstructors()):
            if str(m.getName()) in (member, cn.split(".")[-1]) and (sig is None or sig in str(m.getSignature())): found = True; break
        assert found, f"MISSING {cn}.{member}{sig or ''}"
    return c
must(JP); must(JPI); must(UCB, "append"); must(UCB, "set")
must(HUD, "CustomUIHud", "PlayerRef")   # ctor takes PlayerRef
must(HUD, "show"); must(HUD, "update")
must(PRE, "getPlayerRef"); must(PR, "getComponentType")
must(ER, "registerGlobal", "Ljava/lang/Class;Ljava/util/function/Consumer;")
print("API check: all present")

PKG = "com.skyy.hud"
# pre-declare all classes so cross-references compile
hud = pool.makeClass(PKG + ".SkyyHudWidgetHud", pool.get(HUD))
rc  = pool.makeClass(PKG + ".SkyyHudReady")
pl  = pool.makeClass(PKG + ".SkyyHudPlugin", pool.get(JP))
# ---- SkyyHudWidgetHud extends CustomUIHud ----
hud.addField(CtField.make("private String text;", hud))
hud.addConstructor(CtNewConstructor.make(f"""
public SkyyHudWidgetHud({PR} pr, String text) {{
  super(pr, "skyyhud_main");
  this.text = text;
}}""", hud))
hud.addMethod(CtNewMethod.make(f"""
protected void build({UCB} b) {{
  b.append("Hud/SkyyHud.ui");
  b.set("#SkyyHudText.Text", this.text);
}}""", hud))
hud.addMethod(CtNewMethod.make(f"""
public void setText(String t) {{
  if (t == null || t.equals(this.text)) return;
  this.text = t;
  {UCB} b = new {UCB}();
  b.set("#SkyyHudText.Text", t);
  update(false, b);
}}""", hud))

# ---- plugin ctor + attachHud (before consumer references them) ----
pl.addConstructor(CtNewConstructor.make(f"public SkyyHudPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void attachHud({PR} pr) {{
  try {{
    {PKG}.SkyyHudWidgetHud h = new {PKG}.SkyyHudWidgetHud(pr, "SkyyHud 0.1 online");
    h.show();
  }} catch (Throwable t) {{ getLogger().atInfo().log("SkyyHud attach failed: " + t); }}
}}""", pl))

# ---- ReadyConsumer implements Consumer ----
rc.addInterface(pool.get("java.util.function.Consumer"))
rc.addField(CtField.make(f"public {PKG}.SkyyHudPlugin plugin;", rc))
rc.addConstructor(CtNewConstructor.make(f"public SkyyHudReady({PKG}.SkyyHudPlugin p) {{ this.plugin = p; }}", rc))
rc.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PRE} e = ({PRE}) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    plugin.attachHud(pr);
  }} catch (Throwable t) {{ }}
}}""", rc))

# ---- plugin setup (after consumer exists) ----
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.SkyyHudReady(this));
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyyHud] 0.1 setup complete");
}}""", pl))

for c in (hud, rc, pl): c.writeFile(OUT)
print("classes written")

# ---- assemble jar ----
UIFILE = """Group {
  Anchor: (Full: 0);

  Group #SkyyHudFrame {
    Anchor: (Top: 8, Right: 8, Width: 260, Height: 40);
    Background: #0b1524(0.8);
    Padding: (Horizontal: 10, Vertical: 5);
    LayoutMode: Top;

    Group #SkyyHudAccent {
      Anchor: (Height: 2);
      Background: #7fe07f(0.9);
    }

    Label #SkyyHudText {
      Style: (
        FontSize: 12,
        RenderBold: true,
        TextColor: #eaffea,
        Alignment: Center
      );
      Text: "SkyyHud";
    }
  }
}
"""
manifest = {
  "Group": "Skyy",
  "Name": "0.1 SkyyHud",
  "Version": "0.1.0",
  "Description": "SkyyHud: fully customizable server-side HUD widgets. v0.1 skeleton.",
  "Authors": [{"Name": "Skyy"}],
  "ServerVersion": "*",
  "DisabledByDefault": False,
  "IncludesAssetPack": True,
  "Main": "com.skyy.hud.SkyyHudPlugin"
}
jar = "/tmp/SkyyHud.jar"
with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    z.writestr("Common/UI/Custom/Hud/SkyyHud.ui", UIFILE)
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled", jar, os.path.getsize(jar), "bytes")
