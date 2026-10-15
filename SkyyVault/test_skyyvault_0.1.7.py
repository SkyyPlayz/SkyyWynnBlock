"""Harness for SkyyVault 0.1.7 (HUBS H3d: the Storage > Vault tab + storage:fn:find:vault; tools/vault_0_1_7_patch.py). Build first:
python tools/vault_0_1_7_patch.py && python SkyyVault/build_skyyvault_0.1.7.py

    python SkyyVault/test_skyyvault_0.1.7.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.6 -> 0.1.7 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyVault as its own player, AA engine-access audit), plus here:
  PAGE  the tab opens the vault the way /vault pages does: page mode (Skyy's live config) = the page WITH its vault window (a VSession),
        chest mode = the page with the page buttons (no session)
  FIND  storage:fn:find:vault (VFindFn): put by register, removed by unregister (only OUR object); 64 Wood_Oak_Log + 10 Rock_Stone on
        page 1 -> "oak log" / "OAK_LOG" / "wood_oak" = [["vault", 64]], "rock" = 10, a page past the owned ones never counts, "x" / ""
        / a non-array / no UUID / an unreadable vault = an empty answer, never null, never throws
  CLICK Prev / Next (non-hub clicks) still work on the hub page; the page id is the one the patch pins (VAULT_PAGE_CHECKED)
Exit code 1 on any failure.
"""
import os, sys, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.7"
PKG = "com.skyy.vault."


def prep(E, J, home):
    from jpype import JClass
    J("VCfg").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyVault")
    P = lambda *a: E.Paths.get(os.path.join(home, *a))
    J("VCfg").DIR = P()
    J("VCfg").VDIR = P("vaults")
    J("VCfg").FILE = P("config.properties")
    J("VCfg").LOGF = P("vault.log")
    J("VCfg").NAMESF = P("names.properties")
    J("VStore").STOPPING = False
    J("VStore").SAVER = None


def live_prep(E, J, home):
    # the live copy: chest mode (the page with the page buttons, no vault window / session to close and save afterwards)
    J("VCfg").PAGE_MODE = False
    J("VCfg").OPEN_MODE = "chest"
    J("VStore").loadNames()


def replace_prep(J, on):
    # review fix check (CLICK "replaced"): in page mode the vault's own open re-shows the SAME page (open2's swap) - chest mode replaces it
    J("VCfg").PAGE_MODE = not on
    J("VCfg").OPEN_MODE = "chest" if on else "page"


def live_player(home):
    d = os.path.join(home, "vaults")
    fs = sorted(f for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []
    if not fs:
        return None
    j = json.load(open(os.path.join(d, fs[0]), encoding="utf8"))
    return j["uuid"], j.get("name") or "SkyyLive"


def after_open(K, E, J, P, pg):
    s = J("VSessions").current(P.pr.getUuid())
    K.check(s is not None and pg.sess is not None and int(s.mode) == 1, "PAGE: page mode = the vault page WITH its window (a live VSession, mode 1)")


def chk_next(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "VaultPage", "CLICK: Next (not a hub click) keeps the vault page")
    K.check(int(after.sel) == 2 or "locked" in str(after.info) or len(E.sent(P)) > f0, "CLICK: Next acts on the vault (page %s, %s)" % (after.sel, after.info))


def extra_hub(K, W, J):
    import jpype
    from jpype import JClass
    E = W.E
    Fn = JClass("java.util.function.Function")
    f = E.br.get("storage:fn:find:vault")
    K.check(f is not None and Fn.class_.isInstance(f) and str(f.getClass().getName()) == PKG + "VFindFn", "FIND: storage:fn:find:vault is put by register")
    u = W.O.pr.getUuid()
    d = J("VStore").load(u)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    pg1 = d.page(1)
    pg1[0] = IS("Wood_Oak_Log", 64)
    pg1[3] = IS("Rock_Stone", 10)
    far = d.page(int(d.unlocked) + 1)
    far[0] = IS("Wood_Oak_Log", 5)
    Obj = JClass("java.lang.Object")
    q = lambda *a: f.apply(jpype.JArray(Obj)(list(a)))
    ans = lambda r: [(str(x[0]), int(x[1])) for x in r]
    for text, want in (("oak log", [("vault", 64)]), ("OAK_LOG", [("vault", 64)]), ("wood_oak", [("vault", 64)]), ("rock", [("vault", 10)]),
                       ("x", []), ("", []), ("diamond", [])):
        r = q(u, text)
        K.check(r is not None and ans(r) == want, "FIND: %r -> %s (%s)" % (text, want, None if r is None else ans(r)))
    K.check(len(f.apply("junk")) == 0 and len(q(None, "oak")) == 0 and len(f.apply(None)) == 0, "FIND: junk / no UUID / null -> empty, never null")
    K.check(isinstance(int(len(q(u, "oak"))), int) and JClass("java.lang.Long").class_.isInstance(q(u, "oak")[0][1]), "FIND: the count is a java.lang.Long")
    J("VaultHubOpen").unregister()
    K.check(E.br.get("storage:fn:find:vault") is None, "FIND: unregister removes storage:fn:find:vault")
    other = JClass("java.util.HashMap")()
    E.br.put("storage:fn:find:vault", other)
    J("VaultHubOpen").unregister()
    K.check(E.br.get("storage:fn:find:vault") is not None, "FIND: unregister leaves a key another jar put")
    E.br.remove("storage:fn:find:vault")
    src = open(os.path.join(HERE, "build_skyyvault_%s.py" % VERSION), encoding="utf8").read()
    m = re.search(r'VAULT_PAGE_CHECKED = "([0-9a-f]{12})"', src)
    import zipfile
    data = zipfile.ZipFile(S.jar).read("com/skyy/vault/SkyyVaultPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "PAGE: the built page id = VAULT_PAGE_CHECKED %s (the ready line)" % (m and m.group(1)))
    # chest mode: the tab opens the page with the page buttons (no session)
    J("VCfg").PAGE_MODE = False
    J("VCfg").OPEN_MODE = "chest"
    X = W.mkp(E.UUID.randomUUID(), "SkyyChest")
    E.br.put("hub:last:" + str(X.pr.getUuid()), JClass("java.util.concurrent.ConcurrentHashMap")())
    J("VaultHubOpen").register()
    r = str(J("HubBar").open(X.pr, X.pr.getUuid(), "storage", "vault"))
    E.pump(X)
    pg = X.pm.getCustomPage()
    K.check(r == "bridge" and pg is not None and str(pg.getClass().getSimpleName()) == "VaultPage" and pg.sess is None,
            "PAGE: chest mode = the vault page with the page buttons, no session (%s)" % r)
    J("VaultHubOpen").unregister()
    J("VCfg").PAGE_MODE = True
    J("VCfg").OPEN_MODE = "page"


S = H.Spec(name="SkyyVault", version=VERSION, pkg=PKG, hub="storage", tab="vault", mod="SkyyVault", open_cls="VaultHubOpen", vis_cls=None,
           page_cls="VaultPage", prefix="SkyyVF", idp="SkyyV", plugin_cls="SkyyVaultPlugin", register_call="VaultHubOpen.register",
           drop_call="VaultHubOpen.unregister", register=lambda J: J("VaultHubOpen").register(), prep=prep, live_prep=live_prep, replace_prep=replace_prep,
           live_player=live_player, after_open=after_open, clicks=[('{"a":"next"}', chk_next)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyVault-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyVault-0.1.6.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "vault"))), script=__file__,
           added=["HubBar", "VaultHubOpen", "VFindFn"],
           expect={"VaultPage": ["+m hubAck", "+m hubClick", "~m build", "~m handleDataEvent"], "SkyyVaultPlugin": ["~m setup", "~m shutdown"],
                   "VData": ["+m countMatching"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
                   "VStore": ["~m toDoc"]})     # toDoc: the "version" stamp every vault file carries (0.1.6 wrote "0.1.6")

if __name__ == "__main__":
    H.run(S)
